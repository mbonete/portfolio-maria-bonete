# One Monstera deliciosa leaf blade, built flat in leaf space and then bent into shape.
#
# Leaf space, in metres: u runs along the midrib from the petiole's insertion at the sinus (u = 0) to the
# tip (u = L), v across it (v > 0 is the right half seen from above, tip pointing away). The lateral veins
# are a family of curves u = U(q) + b(q) v + c v^2 on each half, labelled by q in [0, 1]: q = 0 leaves the
# base backwards into the basal lobe, q = 1 runs out near the tip. Splits, holes and the vein pattern are
# all laid out in (q, v), so they follow the veins the way the real leaf's do: the splits and the holes
# (fenestrations) sit between primary lateral veins, each strap-like segment carries one primary vein.
#
# The outline is an implicit function f(u, v) (positive inside, roughly metres to the edge); its zero
# contour is traced, resampled and triangulated together with a jittered grid of interior points
# (constrained Delaunay), so the cuts are real geometry with clean edges.
import numpy as np
from mathutils import Vector, geometry, kdtree, noise as mnoise


def _smin(a, b, k):
    """Smooth minimum: intersecting two regions (f > 0 inside) with corners rounded over about k."""
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def _pchip(xs, ys):
    """Monotone cubic interpolation through (xs, ys), C1, vectorised; flat past the ends."""
    xs, ys = np.asarray(xs, float), np.asarray(ys, float)
    h = np.diff(xs)
    d = np.diff(ys) / h
    m = np.zeros_like(ys)
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, len(xs) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        x = np.asarray(x, float)
        i = np.clip(np.searchsorted(xs, x) - 1, 0, len(xs) - 2)
        t = np.clip((x - xs[i]) / h[i], 0, 1)
        t2, t3 = t * t, t * t * t
        y = ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
             + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
        # straight on past the ends
        y = np.where(x < xs[0], ys[0] + (x - xs[0]) * m[0], y)
        return np.where(x > xs[-1], ys[-1] + (x - xs[-1]) * m[-1], y)
    return f


def _catmull(pts, n=24):
    """A centripetal Catmull-Rom spline through pts (open), n samples per span."""
    P = np.asarray(pts, float)
    P = np.vstack([2 * P[0] - P[1], P, 2 * P[-1] - P[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t0 = 0.0
        t1 = t0 + np.linalg.norm(p1 - p0) ** 0.5 + 1e-9
        t2 = t1 + np.linalg.norm(p2 - p1) ** 0.5 + 1e-9
        t3 = t2 + np.linalg.norm(p3 - p2) ** 0.5 + 1e-9
        t = np.linspace(t1, t2, n, endpoint=False)[:, None]
        a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
        a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
        a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
        b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
        b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
        out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    out.append(P[-2][None])
    return np.vstack(out)


# The right half's outline from the tip round the basal lobe to the sinus, in units of L: broadly ovate,
# nearly as wide as long and widest below the middle, a short blunt tip, a deep heart-shaped base whose
# rounded lobes reach about 0.14 L behind the sinus.
OUTLINE = [(1.0, 0.0), (0.965, 0.058), (0.90, 0.158), (0.79, 0.268), (0.64, 0.358), (0.46, 0.418),
           (0.27, 0.448), (0.09, 0.444), (-0.04, 0.405), (-0.115, 0.33), (-0.145, 0.235), (-0.13, 0.14),
           (-0.085, 0.065), (-0.035, 0.02), (0.0, 0.0)]
CENTRE = 0.42      # the outline is star-shaped about (CENTRE * L, 0)


class Half:
    """The vein family and the cuts of one half of the blade."""

    def __init__(self, L, rng, side):
        self.L, self.side = L, side
        # where each vein leaves the midrib, and at what angle: the first ones fan out of the base into
        # the lobe, the later ones leave at about 60 degrees and turn towards the tip
        qa = np.array([0.0, 0.07, 0.16, 0.32, 0.55, 0.78, 1.0])
        ang = np.array([138, 110, 92, 78, 68, 58, 45]) + rng.uniform(-3, 3, 7)
        ang = np.minimum.accumulate(ang)                      # never increasing along the leaf
        # a smooth (C1) run of slopes, carried on in straight lines past both ends, so u stays monotone
        # in q everywhere off the midrib and the spacing of the veins changes without kinks
        b = _pchip(qa, 1 / np.tan(np.radians(ang)))
        # tabulated finely (with its derivative) for speed
        self._qt = np.linspace(-0.3, 1.3, 6401)
        self._bt = b(self._qt)
        self._dbt = np.gradient(self._bt, self._qt)
        self.c = rng.uniform(0.5, 0.75) / L                  # the veins' forward curl
        self.ue = rng.uniform(1.25, 1.45)                     # how the vein origins crowd at the base

    def U(self, q):
        return self.L * 0.93 * np.clip(q, 0, 1.3) ** self.ue

    def dU(self, q):
        qc = np.clip(q, 0, 1.3)
        return np.where((q > 0) & (q < 1.3), self.L * 0.93 * self.ue * qc ** (self.ue - 1), 0.0)

    def b(self, q):
        return np.interp(q, self._qt, self._bt)

    def u_of(self, q, v):
        return self.U(q) + self.b(q) * v + self.c * v * v

    def q_of(self, u, v, it=27):
        """Invert u = u_of(q, v) for q (monotone in q for v > 0), within [-0.3, 1.3]."""
        lo = np.full(np.shape(u), -0.3)
        hi = np.full(np.shape(u), 1.3)
        for _ in range(it):
            mid = 0.5 * (lo + hi)
            big = self.u_of(mid, v) > u
            hi = np.where(big, mid, hi)
            lo = np.where(big, lo, mid)
        q = 0.5 * (lo + hi)
        return q

    def metric(self, q, v):
        """Metres across the veins per unit q, and the slope du/dv of the vein through (q, v)."""
        du = self.dU(q) + np.interp(q, self._qt, self._dbt) * v
        slope = self.b(q) + 2 * self.c * v
        return du / np.sqrt(1 + slope * slope), slope


class Leaf:
    """The flat blade: outline, splits and holes, as an implicit function, plus the vein layout."""

    def __init__(self, L, rng, maturity=1.0, width=1.0, tear=False, n_veins=None):
        self.L, self.rng, self.mat = L, rng, maturity
        self.width = width
        # each half has its own outline jitter, veins and cuts
        self.halves = {}
        self.outline = {}
        for side in (1, -1):
            pts = np.array(OUTLINE) * L
            jit = rng.normal(0, 0.008, (len(pts), 2)) * L
            jit[0] = 0
            jit[-1] = 0
            pts = pts + jit
            pts[:, 1] *= width * rng.uniform(0.96, 1.04)
            # the basal lobe a little rounder or fuller on one side
            lobe = (pts[:, 0] < 0.05 * L)
            pts[lobe, 0] *= rng.uniform(0.9, 1.1)
            dense = _catmull(pts, 40)
            c = np.array([CENTRE * L, 0.0])
            d = dense - c
            th = np.arctan2(d[:, 1], d[:, 0])
            r = np.hypot(d[:, 0], d[:, 1])
            o = np.argsort(th)
            th, r = th[o], r[o]
            # a slight irregularity of the margin (real margins are never a clean curve)
            ph = rng.uniform(0, 100)
            r = r * (1 + 0.006 * np.array([mnoise.noise((t * 2.2, ph, 0.0)) for t in th]))
            self.outline[side] = (th, r)
            self.halves[side] = Half(L, rng, side)
        self.make_cuts(n_veins, tear)

    # ---------- the outline ----------
    def f_outline(self, u, v):
        side = np.where(v >= 0, 1, -1)
        av = np.abs(v)
        c = CENTRE * self.L
        du = u - c
        th = np.arctan2(av, du)
        d = np.hypot(du, av)
        out = np.empty_like(u)
        for s in (1, -1):
            m = side == s
            T, R = self.outline[s]
            r = np.interp(th[m], T, R)
            dr = np.gradient(R, T)
            g = np.interp(th[m], T, dr) / np.maximum(r, 1e-6)
            out[m] = (r - d[m]) / np.sqrt(1 + g * g)
        return out

    def rim_v(self, half, q):
        """How far out the vein q runs before it meets the outline (marching along it)."""
        vs = np.linspace(0, 0.75 * self.L, 900)
        u = half.u_of(np.full_like(vs, q), vs)
        f = self.f_outline(u, vs * half.side)
        out = np.nonzero(f < 0)[0]
        out = out[out > 3]
        return vs[out[0]] if len(out) else vs[-1]

    # ---------- splits, holes and veins ----------
    def make_cuts(self, n_veins, tear):
        rng, L, m = self.rng, self.L, self.mat
        self.cuts = {1: [], -1: []}
        self.holes = {1: [], -1: []}
        self.veins = {}
        self.bulges = {}
        for s in (1, -1):
            h = self.halves[s]
            n = n_veins or int(round(rng.uniform(5.6, 7.8)))
            # primary veins: roughly even along the leaf, with the irregular spacing of a real leaf
            q = (np.arange(n) + 0.5 + rng.uniform(-0.2, 0.2, n)) / n
            q = np.sort(np.clip(q, 0.02, 0.97))
            self.veins[s] = q
            dq = np.diff(q)
            # the lines between veins, where splits and holes go
            mids = q[:-1] + dq * rng.uniform(0.42, 0.58, n - 1)
            for i, qs in enumerate(mids):
                vr = self.rim_v(h, qs)
                # the mature leaf splits nearly everywhere but at the very tip; a young one barely at all
                p_split = m * (0.86 if 0.04 < qs < 0.84 else 0.4)
                if rng.random() < p_split:
                    depth = rng.uniform(0.5, 0.84) * (0.4 + 0.6 * m)
                    if qs > 0.75:
                        depth *= 0.65
                    v_end = max(vr * (1 - depth), 0.06 * L)
                    self.cuts[s].append(dict(q=qs, v_end=v_end, v_rim=vr, hw=(rng.uniform(0.010, 0.034) if rng.random() < 0.8 else rng.uniform(0.04, 0.06)) * L * (0.5 + 0.5 * m),
                                             r=rng.uniform(0.004, 0.008) * L, p=rng.uniform(1.3, 2.4), torn=False))
                    # a hole between the midrib and the split's inner end
                    room = v_end - 0.07 * L
                    if room > 0.045 * L and rng.random() < 0.8 * m + 0.1:
                        ln = min(room * rng.uniform(0.55, 0.85), 0.13 * L) / 2
                        vc = 0.042 * L + ln + rng.uniform(0, max(room - 2 * ln - 0.02 * L, 0))
                        self.holes[s].append(dict(q=qs + rng.uniform(-0.12, 0.12) * dq[i], v=vc, l=ln,
                                                  w=ln * rng.uniform(0.3, 0.48)))
                elif rng.random() < 0.55 * m + 0.3:
                    # unsplit: perhaps a hole along this line
                    ln = rng.uniform(0.018, 0.04) * L * (0.6 + 0.4 * m)
                    vc = vr * rng.uniform(0.3, 0.55)
                    if vc + ln < vr - 0.04 * L and vc - ln > 0.04 * L:
                        self.holes[s].append(dict(q=qs, v=vc, l=ln, w=ln * rng.uniform(0.3, 0.45)))
            # each strap between two splits ends in its own rounded margin
            edges = sorted(c["q"] for c in self.cuts[s])
            self.bulges[s] = [(a, b, rng.uniform(0.004, 0.012) * L * m) for a, b in zip(edges, edges[1:])]
        if tear:
            s = rng.choice((1, -1))
            h = self.halves[s]
            qv = self.veins[s]
            i = rng.integers(len(qv) // 3, len(qv) - 2)
            qt = qv[i] + rng.uniform(0.2, 0.35) * (qv[i + 1] - qv[i])
            vr = self.rim_v(h, qt)
            rag = [(rng.uniform(0.2, 0.4), rng.uniform(300, 700), rng.uniform(0, 6.3)) for _ in range(3)]
            self.cuts[s].append(dict(q=qt, v_end=vr * rng.uniform(0.55, 0.7), v_rim=vr, hw=0.006 * L, r=0.0015 * L,
                                     p=2.5, torn=True, rag=rag))
            self.tear = (s, qt, vr)
        else:
            self.tear = None

    def phase(self, side, q):
        """The vein phase: integer on a primary vein, varying smoothly between and carried on at the end
        spacings past the first and last vein."""
        qv = self.veins[side]
        n = len(qv)
        p = np.interp(q, qv, np.arange(n, dtype=float))
        p = np.where(q < qv[0], (q - qv[0]) / (qv[1] - qv[0]), p)
        p = np.where(q > qv[-1], n - 1 + (q - qv[-1]) / (qv[-1] - qv[-2]), p)
        return p

    def bulge(self, side, q):
        out = np.zeros_like(q)
        for a, b, amp in self.bulges[side]:
            t = np.clip((q - a) / (b - a), 0, 1)
            out += amp * np.sin(np.pi * t) ** 0.8
        return out

    def field(self, u, v, k_round=None):
        """f(u, v): roughly the distance to the edge in metres, positive on the blade."""
        L = self.L
        f = self.f_outline(u, v)
        k_round = k_round or 0.006 * L
        # cuts only take away and the straps' bulges add at most 0.012 L, so well outside the outline
        # nothing changes
        near = f > -0.015 * L
        for s in (1, -1):
            h = self.halves[s]
            m = ((v * s) >= 0) & near
            if not np.any(m):
                continue
            uu, vv = u[m], np.abs(v[m])
            q = h.q_of(uu, vv)
            met, slope = h.metric(q, vv)
            along = np.sqrt(1 + slope * slope)
            g = f[m] + self.bulge(s, q)
            for c in self.cuts[s]:
                # metres across the veins from the cut's line: the metric taken halfway between
                dq = np.abs(q - c["q"]) * h.metric(0.5 * (q + c["q"]), vv)[0]
                t = np.clip((vv - c["v_end"]) / max(c["v_rim"] - c["v_end"], 1e-6), 0, 1)
                hw = c["r"] + (c["hw"] - c["r"]) * t ** c["p"]
                if c["torn"]:
                    # a tear's edges are ragged and it narrows to nothing
                    rag = sum(a * np.sin(vv * w + ph) for a, w, ph in c["rag"])
                    hw = c["r"] * (0.4 + 2.5 * t) * (1 + rag)
                fs = np.where(vv >= c["v_end"], dq - hw,
                              np.sqrt(dq * dq + ((c["v_end"] - vv) * along) ** 2) - c["r"])
                g = _smin(g, fs, k_round if not c["torn"] else 0.001 * L)
            for c in self.holes[s]:
                dq = (q - c["q"]) * h.metric(0.5 * (q + c["q"]), vv)[0]
                dl = (vv - c["v"]) * along
                # oblong, a little egg-shaped: wider towards the margin
                w = c["w"] * (1 + 0.18 * np.clip(dl / c["l"], -1, 1))
                rr = np.sqrt((dl / c["l"]) ** 2 + (dq / w) ** 2)
                fh = (rr - 1) * np.minimum(c["l"], w)
                g = np.minimum(g, fh)
            f[m] = g
        return f

    # ---------- tracing and meshing ----------
    def bounds(self):
        L = self.L
        return -0.2 * L, 1.05 * L, -0.55 * L * self.width - 0.02, 0.55 * L * self.width + 0.02

    def contours(self, h=0.0007):
        u0, u1, v0, v1 = self.bounds()
        us = np.arange(u0, u1, h)
        vs = np.arange(v0, v1, h)
        U, V = np.meshgrid(us, vs)
        F = self.field(U.ravel(), V.ravel()).reshape(U.shape)
        return _march(F, us[0], vs[0], h)


def _march(F, x0, y0, h):
    """Closed contours of F = 0 (F > 0 inside) by marching squares, as lists of (x, y) arrays."""
    F = np.pad(F, 1, constant_values=-1.0)
    x0, y0 = x0 - h, y0 - h
    ny, nx = F.shape
    ins = F > 0
    NH = ny * (nx - 1)
    pts = {}

    def hp(i, j):
        a, b = F[i, j], F[i, j + 1]
        return (x0 + (j + a / (a - b)) * h, y0 + i * h)

    def vp(i, j):
        a, b = F[i, j], F[i + 1, j]
        return (x0 + j * h, y0 + (i + a / (a - b)) * h)

    # crossing ids for each cell's four edges: bottom, right, top, left
    c00, c01, c11, c10 = ins[:-1, :-1], ins[:-1, 1:], ins[1:, 1:], ins[1:, :-1]
    case = c00 * 1 + c01 * 2 + c11 * 4 + c10 * 8
    I, J = np.nonzero((case != 0) & (case != 15))
    nbr = {}

    def link(a, b):
        nbr.setdefault(a, []).append(b)
        nbr.setdefault(b, []).append(a)

    # edge ids: horizontal (i, j) -> i*(nx-1)+j ; vertical (i, j) -> NH + i*nx + j
    for i, j in zip(I.tolist(), J.tolist()):
        cs = case[i, j]
        e = []
        bot, top = i * (nx - 1) + j, (i + 1) * (nx - 1) + j
        lef, rig = NH + i * nx + j, NH + i * nx + j + 1
        if c00[i, j] != c01[i, j]:
            e.append(bot)
        if c01[i, j] != c11[i, j]:
            e.append(rig)
        if c11[i, j] != c10[i, j]:
            e.append(top)
        if c10[i, j] != c00[i, j]:
            e.append(lef)
        if len(e) == 2:
            link(e[0], e[1])
        else:  # saddle: decide by the centre
            centre = (F[i, j] + F[i, j + 1] + F[i + 1, j + 1] + F[i + 1, j]) > 0
            if (cs == 5) == centre:
                link(bot, lef)
                link(rig, top)
            else:
                link(bot, rig)
                link(top, lef)

    def coord(k):
        if k < NH:
            return hp(k // (nx - 1), k % (nx - 1))
        k -= NH
        return vp(k // nx, k % nx)

    seen = set()
    loops = []
    for start in nbr:
        if start in seen:
            continue
        loop = [start]
        seen.add(start)
        prev, cur = None, start
        while True:
            a, b = nbr[cur]
            nxt = a if a != prev else b
            if nxt == start or nxt in seen:
                break
            loop.append(nxt)
            seen.add(nxt)
            prev, cur = cur, nxt
        if len(loop) > 8:
            loops.append(np.array([coord(k) for k in loop]))
    return loops


def resample(loop, ds, smooth=2):
    """A closed polyline resampled to an even spacing ds and lightly smoothed."""
    P = np.vstack([loop, loop[:1]])
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(s[-1] / ds), 6)
    t = np.linspace(0, s[-1], n, endpoint=False)
    Q = np.stack([np.interp(t, s, P[:, 0]), np.interp(t, s, P[:, 1])], 1)
    for _ in range(smooth):
        Q = 0.5 * Q + 0.25 * (np.roll(Q, 1, 0) + np.roll(Q, -1, 0))
    return Q


def _area(P):
    x, y = P[:, 0], P[:, 1]
    return 0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)


def triangulate(leaf, ds=0.0016, spacing=0.0042, seed=0):
    """Boundary loops resampled at ds, a jittered interior grid at `spacing`, constrained Delaunay.
    Returns 2D verts (n, 2), triangles (m, 3), the boundary loops as index arrays."""
    rng = np.random.default_rng(seed)
    loops = [resample(lp, ds) for lp in leaf.contours()]
    loops = [lp for lp in loops if abs(_area(lp)) > 2e-5]
    bpts = np.vstack(loops)
    # interior points: a jittered triangular lattice
    u0, u1, v0, v1 = leaf.bounds()
    rows = np.arange(v0, v1, spacing * 0.866)
    P = []
    for k, y in enumerate(rows):
        xs = np.arange(u0 + (k % 2) * spacing / 2, u1, spacing)
        P.append(np.stack([xs, np.full_like(xs, y)], 1))
    P = np.vstack(P) + rng.uniform(-0.22, 0.22, (sum(len(p) for p in P), 2)) * spacing
    f = leaf.field(P[:, 0].copy(), P[:, 1].copy())
    P = P[f > 0.3 * spacing]
    kd = kdtree.KDTree(len(bpts))
    for i, p in enumerate(bpts):
        kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    keep = np.array([kd.find((p[0], p[1], 0.0))[2] > 0.62 * spacing for p in P], bool)
    P = P[keep]
    verts = np.vstack([bpts, P])
    edges = []
    idx = []
    o = 0
    for lp in loops:
        n = len(lp)
        ids = np.arange(o, o + n)
        idx.append(ids)
        edges += [(int(a), int(b)) for a, b in zip(ids, np.roll(ids, -1))]
        o += n
    res = geometry.delaunay_2d_cdt([Vector(p) for p in verts], edges, [], 0, 1e-7, True)
    vout, _, faces, orig_v = res[0], res[1], res[2], res[3]
    V = np.array([(p.x, p.y) for p in vout])
    T = np.array([f for f in faces if len(f) == 3])
    cen = V[T].mean(1)
    fc = leaf.field(cen[:, 0].copy(), cen[:, 1].copy())
    T = T[fc > 0]
    # map the boundary loops to output indices
    inv = np.full(len(verts), -1)
    for k, ov in enumerate(orig_v):
        for j in ov:
            inv[j] = k
    loops_out = [inv[ids] for ids in idx]
    # drop vertices no triangle uses
    used = np.zeros(len(V), bool)
    used[T.ravel()] = True
    remap = np.cumsum(used) - 1
    V = V[used]
    T = remap[T]
    loops_out = [remap[lp] for lp in loops_out if np.all(used[lp])]
    return V, T, loops_out


# ---------- bending the flat blade into shape ----------
def _rot(axis, a):
    c, s = np.cos(a), np.sin(a)
    o, z = np.ones_like(a), np.zeros_like(a)
    if axis == "x":
        m = [[o, z, z], [z, c, -s], [z, s, c]]
    elif axis == "y":
        m = [[c, z, s], [z, o, z], [-s, z, c]]
    else:
        m = [[c, -s, z], [s, c, z], [z, z, o]]
    return np.moveaxis(np.array(m), [0, 1], [-2, -1])


def midrib_frames(L, sp, us):
    """The midrib's path and frames at arc lengths us, in leaf-local axes (x across to the right, y along
    the midrib's start, z the upper face's normal): it rises by `arch`, droops by `droop` towards the
    tip, sweeps sideways and rolls about itself. Behind the insertion (u < 0) it runs on straight."""
    t = np.clip(us / L, 0, 1)
    beta = sp["arch"] * t - (sp["arch"] + sp["droop"]) * t ** sp["dp"]
    sigma = sp["sweep"] * t * t
    tau = sp["twist"] * t
    R = _rot("z", sigma) @ _rot("x", beta) @ _rot("y", tau)
    T = R[:, :, 1]
    C = np.zeros((len(us), 3))
    C[1:] = np.cumsum(0.5 * (T[1:] + T[:-1]) * np.diff(us)[:, None], 0)
    C -= np.array([np.interp(0.0, us, C[:, k]) for k in range(3)])
    return C, R


def segments(leaf, side):
    """The straps of one half: for each, the q range and how far out it is free of its neighbours."""
    cs = sorted((c for c in leaf.cuts[side] if not c["torn"]), key=lambda c: c["q"])
    if not cs:
        return []
    out = [(-1.0, cs[0]["q"], cs[0]["v_end"])]
    for a, b in zip(cs, cs[1:]):
        out.append((a["q"], b["q"], max(a["v_end"], b["v_end"])))
    out.append((cs[-1]["q"], 2.0, cs[-1]["v_end"]))
    return out


def shape(leaf, V2, sp, rng):
    """Leaf-local 3D positions for flat (u, v) points, and the midrib's centre line."""
    L = leaf.L
    u, v = V2[:, 0], V2[:, 1]
    us = np.linspace(-0.3 * L, 1.02 * L, 700)
    C, R = midrib_frames(L, sp, us)
    Ci = np.stack([np.interp(u, us, C[:, k]) for k in range(3)], 1)
    Bi = np.stack([np.interp(u, us, R[:, k, 0]) for k in range(3)], 1)
    Ni = np.stack([np.interp(u, us, R[:, k, 2]) for k in range(3)], 1)
    t = np.clip(u / L, 0, 1)
    av = np.abs(v)
    z = np.zeros_like(u)
    seg_id = np.zeros_like(u)
    for s in (1, -1):
        m = (v * s) > 0
        if not np.any(m):
            continue
        h = leaf.halves[s]
        fold, curl = sp["fold"][s], sp["curl"][s]
        # the halves rise a little from the midrib, more near the base, and their outer parts fall away
        zz = fold * av[m] * (1 - 0.6 * t[m]) - curl * av[m] ** 2 / L
        q = h.q_of(u[m], av[m])
        # each free strap droops and turns on its own
        for k, (qa, qb, r) in enumerate(segments(leaf, s)):
            inn = (q >= qa) & (q < qb)
            if not np.any(inn):
                continue
            d, tw = rng.uniform(0.15, 1.1) * sp["segdroop"], rng.uniform(-1.6, 1.6)
            free = np.maximum(av[m][inn] - r, 0)
            qm = 0.5 * (max(qa, 0) + min(qb, 1.05))
            off = (q[inn] - qm) * h.metric(q[inn], av[m][inn])[0]
            zz[inn] += -d * free * free / L + tw * off * free / L
            seg_id[np.nonzero(m)[0][inn]] = rng.random()
        z[m] = zz
    # a gentle, irregular waviness, stronger towards the margin
    ph = rng.uniform(0, 100, 3)
    wv = np.array([mnoise.noise((a / 0.07 + ph[0], b / 0.07 + ph[1], ph[2])) for a, b in zip(u, v)])
    z += sp["wave"] * (np.minimum(av / (0.42 * L), 1.2) ** 2) * wv
    P = Ci + Bi * v[:, None] + Ni * z[:, None]
    return P, seg_id


def blade(leaf, sp, rng, ds=0.0016, spacing=0.0042, thick=0.00045):
    """The finished blade in leaf-local metres: a single sheet (for thin-walled shading, both faces) with
    a band round every edge for its thickness, the per-vertex data the leaf shader reads, and the
    midrib's centre line for the raised rib underneath."""
    L = leaf.L
    V2, T, loops = triangulate(leaf, ds, spacing, seed=int(rng.integers(1 << 30)))
    P, seg_id = shape(leaf, V2, sp, rng)
    # face winding so the normals point to the upper face (+z when flat)
    a, b, c = V2[T[:, 0]], V2[T[:, 1]], V2[T[:, 2]]
    cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    # (u, v) -> (x = v, y = u) mirrors the winding: a clockwise (u, v) triangle faces +z
    T = np.where((cr > 0)[:, None], T[:, ::-1], T)
    # vertex normals
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]])
    vn = np.zeros_like(P)
    for k in range(3):
        np.add.at(vn, T[:, k], fn)
    vn /= np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)

    # per-vertex data: vein phase and its scale, distance to the midrib and to the nearest edge
    u, v = V2[:, 0], V2[:, 1]
    vp = np.zeros_like(u)
    vm = np.zeros_like(u)
    for s in (1, -1):
        m = (v * s) >= 0
        h = leaf.halves[s]
        q = h.q_of(u[m], np.abs(v[m]))
        p = leaf.phase(s, q)
        dpdq = (leaf.phase(s, q + 1e-4) - leaf.phase(s, q - 1e-4)) / 2e-4
        vp[m] = p
        vm[m] = h.metric(q, np.abs(v[m]))[0] / np.maximum(dpdq, 1e-6)
    bpts = np.vstack([V2[lp] for lp in loops])
    kd = kdtree.KDTree(len(bpts))
    for i, p in enumerate(bpts):
        kd.insert((p[0], p[1], 0.0), i)
    kd.balance()
    ed = np.array([kd.find((p[0], p[1], 0.0))[2] for p in V2])
    data = dict(vp=vp, vm=vm, lv=np.abs(v), lu=u / L, ed=ed, seg=seg_id)

    # the band round the edges, its quads facing away from the blade
    nb = sum(len(lp) for lp in loops)
    top = np.concatenate(loops)
    bot_P = P[top] - vn[top] * thick
    band_v0 = len(P)
    quads = []
    o = 0
    for lp in loops:
        n = len(lp)
        tops = band_v0 + o + np.arange(n)          # copies of the edge vertices (a hard edge)
        bots = band_v0 + nb + o + np.arange(n)
        q4 = np.stack([tops, np.roll(tops, -1), np.roll(bots, -1), bots], 1)
        # the quad (top_i, top_i+1, bot_i+1, bot_i) faces to the left of the edge seen from above (x = v,
        # y = u); probe the blade there and flip the strip if that is the blade's side
        k = np.linspace(0, n - 1, 9).astype(int)
        e = V2[lp[(k + 1) % n]] - V2[lp[k]]
        mid = 0.5 * (V2[lp[(k + 1) % n]] + V2[lp[k]])
        probe = mid + 0.0008 * np.stack([e[:, 1], -e[:, 0]], 1) / np.maximum(np.linalg.norm(e, axis=1, keepdims=True), 1e-9)
        if np.mean(leaf.field(probe[:, 0].copy(), probe[:, 1].copy()) > 0) > 0.5:
            q4 = q4[:, ::-1]
        quads.append(q4)
        o += n
    quads = np.vstack(quads)
    Pall = np.vstack([P, P[top], bot_P])
    for k in data:
        data[k] = np.concatenate([data[k], data[k][top], data[k][top]])
    uv = np.vstack([V2, V2[top], V2[top]])
    # midrib centre line
    us = np.linspace(0, 0.93 * L, 80)
    C, R = midrib_frames(L, sp, us)
    return dict(P=Pall, tris=T, quads=quads, n_sheet=len(P), uv=uv, data=data, loops=loops, top=top,
                rib=(C, R, us), normals=vn)
