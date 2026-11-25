# The chunky cable-knit scarf: wrapped once round the neck, both ends hanging down the chest with a
# fringe. The cloth is placed by draping it on the stuffed shape (it rests on the fur, which it
# squashes); the knit is built yarn by yarn on that cloth: each visible leg of a knit stitch, each purl
# bump and each cable crossing is a short piece of plied yarn, laid on a dark backing so no gap shows
# through.
import numpy as np
from objects import capybara_shape as shape
from objects import capybara_yarn as yarn

Y_AX = -0.020                 # the neck's axis (x = 0, this y), which the wrap goes round
COLS = "KPCCCCPPPCCCCPK"      # knit edge, purl, a 2/2 cable, three purl, a cable, purl, knit edge
W = 0.0975                    # width of the scarf laid flat
CW = W / len(COLS)            # 6.5 mm a stitch
RH = 0.0050                   # 5 mm a row
RY = 0.00175                  # yarn radius
CABLE_EVERY = 8               # rows between crossings
CLR = 0.0045                  # how far the cloth stays off the fabric (the fur it squashes)
LAYER = 2.1 * RY              # thickness of the knit layer


def _unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def _smooth1(a, k, axis=0, wrap=False):
    """Moving average with a Hann window of half-width k samples."""
    if k < 1:
        return a
    w = np.hanning(2 * k + 3)[1:-1]
    w /= w.sum()
    a = np.moveaxis(a, axis, 0)
    if wrap:
        pad = np.concatenate([a[-k:], a, a[:k]], 0)
    else:
        pad = np.concatenate([np.repeat(a[:1], k, 0), a, np.repeat(a[-1:], k, 0)], 0)
    out = np.zeros_like(a)
    for i, wi in enumerate(w):
        out += wi * pad[i:i + len(a)]
    return np.moveaxis(out, 0, axis)


def _waves1(x, seed, period, n=3):
    rng = np.random.default_rng(seed)
    out = np.zeros_like(x)
    for _ in range(n):
        out += np.sin(2 * np.pi * x / (period * rng.uniform(0.6, 1.5)) + rng.uniform(0, 2 * np.pi))
    return out / np.sqrt(n / 2)


# ---------- where the stuffed surface is ----------
def radial_surface(theta, z, r0=0.05, r1=0.42, step=0.002):
    """Distance from the neck axis to the surface along horizontal rays (arrays of equal shape)."""
    th, zz = np.broadcast_arrays(theta, z)
    shp = th.shape
    th, zz = th.ravel(), zz.ravel()
    d = np.stack([np.sin(th), -np.cos(th)], 1)
    rs = np.arange(r0, r1, step)
    lo = np.full(len(th), r1)
    for i, r in enumerate(rs):
        P = np.stack([d[:, 0] * r, Y_AX + d[:, 1] * r, zz], 1)
        out = shape.sdf(P, seams=False) > 0
        hit = out & (lo == r1)
        lo[hit] = r
        if (lo < r1).all():
            break
    a, b = np.maximum(lo - step, r0), lo
    for _ in range(14):
        m = (a + b) / 2
        P = np.stack([d[:, 0] * m, Y_AX + d[:, 1] * m, zz], 1)
        out = shape.sdf(P, seams=False) > 0
        b = np.where(out, m, b)
        a = np.where(out, a, m)
    return ((a + b) / 2).reshape(shp)


def front_surface(x, z, y0=-0.45, y1=0.10, step=0.002):
    """The body's y where rays along +y from the front first meet it."""
    xx, zz = np.broadcast_arrays(x, z)
    shp = xx.shape
    xx, zz = xx.ravel(), zz.ravel()
    ys = np.arange(y0, y1, step)
    hit = np.full(len(xx), y1)
    for y in ys:
        P = np.stack([xx, np.full(len(xx), y), zz], 1)
        inside = shape.sdf(P, seams=False) < 0
        new = inside & (hit == y1)
        hit[new] = y
        if (hit < y1).all():
            break
    a, b = hit - step, hit
    for _ in range(14):
        m = (a + b) / 2
        P = np.stack([xx, m, zz], 1)
        inside = shape.sdf(P, seams=False) < 0
        b = np.where(inside, m, b)
        a = np.where(inside, a, m)
    return ((a + b) / 2).reshape(shp)


# ---------- a cloth surface parametrised by fabric coordinates ----------
class Cloth:
    """A grid of points (nu along the scarf, nv across) on the cloth's face, with normals pointing
    away from the body. Fabric coordinates: Y along (arc length of the middle line), X across (0..W,
    stretched to the actual width row by row)."""

    def __init__(self, P, periodic=False, flip=False, lo=0.0, hi=1.0):
        self.P = P
        self.lo, self.hi = lo, hi
        self.periodic = periodic
        nu, nv, _ = P.shape
        if periodic:
            dU = np.roll(P, -1, 0) - np.roll(P, 1, 0)
        else:
            dU = np.gradient(P, axis=0)
        dV = np.gradient(P, axis=1)
        N = _unit(np.cross(dU, dV))
        self.N = -N if flip else N
        mid = P[:, nv // 2]
        seg = np.linalg.norm(np.diff(np.concatenate([mid, mid[:1]]) if periodic else mid, axis=0), axis=1)
        self.Yu = np.concatenate([[0], np.cumsum(seg)])            # (nu [+1])
        self.length = self.Yu[-1]
        sv = np.linalg.norm(np.diff(P, axis=1), axis=2)
        cv = np.concatenate([np.zeros((nu, 1)), np.cumsum(sv, 1)], 1)
        self.Xv = cv / cv[:, -1:]                                   # 0..1 across, per row

    def at(self, X, Y, Z):
        """Fabric coordinates (X 0..W across, Y along, Z off the face) to world points."""
        nu, nv, _ = self.P.shape
        if self.periodic:
            Y = np.mod(Y, self.length)
        Y = np.clip(Y, 0, self.length - 1e-9)
        fu = np.interp(Y, self.Yu, np.arange(len(self.Yu)))
        i0 = np.floor(fu).astype(int)
        tu = fu - i0
        i0 = i0 % nu if self.periodic else np.minimum(i0, nu - 2)
        i1 = (i0 + 1) % nu if self.periodic else i0 + 1
        if not self.periodic:
            tu = np.clip(fu - i0, 0, 1)
        xr = self.lo + (self.hi - self.lo) * np.clip(X / W, 0, 1)
        # across: the row's own stretch
        xv = (1 - tu)[:, None] * self.Xv[i0] + tu[:, None] * self.Xv[i1]      # (n, nv)
        fv = self._fv(xr, xv)
        j0 = np.minimum(np.floor(fv).astype(int), nv - 2)
        tv = fv - j0

        def bil(A):
            return ((1 - tu) * (1 - tv))[:, None] * A[i0, j0] + ((1 - tu) * tv)[:, None] * A[i0, j0 + 1] + \
                (tu * (1 - tv))[:, None] * A[i1, j0] + (tu * tv)[:, None] * A[i1, j0 + 1]
        n = _unit(bil(self.N))
        return bil(self.P) + n * np.asarray(Z)[:, None]

    @staticmethod
    def _fv(xr, xv):
        # vectorised interp of xr into each row's monotonic xv
        idx = (xv < xr[:, None]).sum(1) - 1
        idx = np.clip(idx, 0, xv.shape[1] - 2)
        a = xv[np.arange(len(xr)), idx]
        b = xv[np.arange(len(xr)), idx + 1]
        return idx + np.clip((xr - a) / np.maximum(b - a, 1e-12), 0, 1)


# ---------- the wrap round the neck ----------
# A roll of knit: in each half-plane through the neck's axis its section is an ellipse, pushed out from
# the axis until it rests on the body. The knit covers the outer side of the ellipse and wraps a little
# past its top and bottom; a closed backing fills the rest.
NT, NV = 720, 72
A_RAD = 0.022        # half the roll's thickness
B_RAD = 0.034        # half its height
PHI_KNIT = np.pi / 2 + 0.70


def wrap_centre_z(theta):
    return shape.scarf_z(theta)


def _ellipse_pts(th, zc, rc, a, b, phi):
    """Points of the roll's section: phi = 0 straight out, +pi/2 at the top."""
    rho = rc[:, None] + a[:, None] * np.cos(phi)[None]
    z = zc[:, None] + b[:, None] * np.sin(phi)[None]
    return np.stack([rho * np.sin(th)[:, None], Y_AX - rho * np.cos(th)[:, None], z], 2)


def build_wrap():
    th = np.linspace(0, 2 * np.pi, NT, endpoint=False)
    zc = wrap_centre_z(th)
    # lumpy: the knit bunches where it was pulled round, flatter in between
    a = A_RAD * (1 + 0.14 * _waves1(th, 7, 1.3) + 0.10 * _waves1(th, 17, 0.55))
    b = B_RAD * (1 + 0.10 * _waves1(th, 8, 1.7) + 0.06 * _waves1(th, 18, 0.6))
    tilt = 0.28 * _waves1(th, 10, 2.2)            # the section leans in and out along the wrap
    # rest the inner-lower part of each section on the body...
    phi_rest = np.linspace(0.97 * np.pi, 1.45 * np.pi, 11)
    rc = np.full(NT, 0.12)
    for step in (0.008, 0.002, 0.0005):
        for _ in range(60):
            P = _ellipse_pts(th, zc, rc, a, b, phi_rest).reshape(-1, 3)
            d = shape.sdf(P, seams=False).reshape(NT, -1).min(1)
            bad = d < CLR
            if not bad.any():
                break
            rc[bad] += step
        rc -= step
    rc += 0.0005
    rc = np.maximum(_smooth1(rc, 8, wrap=True), rc)
    rc = _smooth1(rc, 4, wrap=True)
    # ...then the whole section, squashed where it presses on the chin or the cheeks
    phi = np.linspace(-np.pi, np.pi, NV, endpoint=False)
    ph = phi[None] + tilt[:, None] * np.cos(phi)[None]
    P = _ellipse_pts(th, zc, rc, a, b, phi)
    rho = rc[:, None] + a[:, None] * np.cos(ph)
    z = zc[:, None] + b[:, None] * np.sin(ph) + tilt[:, None] * a[:, None] * np.cos(phi)[None] * 0.6
    P = np.stack([rho * np.sin(th)[:, None], Y_AX - rho * np.cos(th)[:, None], z], 2)
    out = np.stack([np.sin(th), -np.cos(th), np.zeros(NT)], 1)
    fold = 0.0022 * np.sin(3.0 * phi[None] + 1.4 * _waves1(th, 9, 1.6)[:, None]) * np.clip(np.cos(phi), 0, 1)[None] ** 2
    P = P + out[:, None] * fold[..., None]
    for it in range(3):
        flat = P.reshape(-1, 3)
        d = shape.sdf(flat, seams=False)
        bad = d < CLR
        if bad.any():
            g = shape.gradient(flat[bad], seams=False)
            flat[bad] += g * (CLR - d[bad])[:, None]
        P = flat.reshape(NT, NV, 3)
        P = 0.5 * P + 0.25 * (np.roll(P, 1, 1) + np.roll(P, -1, 1))   # relax along the section
    # the inner side is drawn in against the neck all the way round, so no gap shows over the top
    rho = np.hypot(P[..., 0], P[..., 1] - Y_AX)
    ang = np.arctan2(P[..., 0], -(P[..., 1] - Y_AX))
    inner = np.cos(phi) < 0.35
    rs = radial_surface(ang[:, inner], P[:, inner, 2])
    w = np.clip((0.35 - np.cos(phi[inner])) / 0.6, 0, 1)
    w = w * w * (3 - 2 * w)
    target = rs + CLR
    rin = rho[:, inner]
    rho[:, inner] = rin - w[None] * np.maximum(rin - target, 0)
    P[..., 0] = rho * np.sin(ang)
    P[..., 1] = Y_AX - rho * np.cos(ang)
    P = 0.5 * P + 0.25 * (np.roll(P, 1, 1) + np.roll(P, -1, 1))
    flat = P.reshape(-1, 3)
    d = shape.sdf(flat, seams=False)
    bad = d < CLR
    if bad.any():
        g = shape.gradient(flat[bad], seams=False)
        flat[bad] += g * (CLR - d[bad])[:, None]
    P = flat.reshape(NT, NV, 3)
    # the knit covers the outer side and wraps over the top and bottom; the backing is the whole ring,
    # drawn in a little towards the section's middle
    sel = np.abs(phi) <= PHI_KNIT + 0.25
    cl = Cloth(np.ascontiguousarray(P[:, sel]), periodic=True)
    ps = phi[sel]
    cl.lo = float(cl.Xv[:, np.argmin(np.abs(ps + PHI_KNIT))].mean())
    cl.hi = float(cl.Xv[:, np.argmin(np.abs(ps - PHI_KNIT))].mean())
    ctr = P.mean(1, keepdims=True)
    ring = P + _unit(ctr - P) * (0.9 * RY)
    return cl, dict(th=th, zc=zc, rc=rc, a=a, b=b, ring=ring)


# ---------- the hanging ends ----------
def drape_end(x_c, z_top, z_bot, start_y, over=None, width=W, nx=29, dz=0.0015, top_gather=0.6,
              clr=CLR):
    """A hanging end: for each column across, the cloth falls straight down unless the body (or the
    cloth `over`, already placed behind it) pushes it forward. start_y(x) gives the y where each
    column leaves the wrap. Returns a Cloth grid (rows from the top down)."""
    xs = x_c + width * (np.linspace(0, 1, nx) - 0.5)
    zs = np.arange(z_top, z_bot - 1e-9, -dz)
    Xg, Zg = np.meshgrid(xs, zs)                     # (nz, nx)
    yb = front_surface(Xg, Zg) - clr
    if over is not None:
        yb = np.minimum(yb, over(Xg, Zg))
    y = np.empty_like(yb)
    y[0] = np.minimum(start_y(xs), yb[0])
    for i in range(1, len(zs)):
        y[i] = np.minimum(y[i - 1] + 0.0007, yb[i])  # a floppy knit: it settles back onto the body
    y = _smooth1(_smooth1(y, 2, 1), 3, 0)
    y = np.minimum(y, yb)
    # gathered where it comes out of the knot, spreading to its full width lower down
    g = top_gather + (1 - top_gather) * np.clip((z_top - zs) / 0.05, 0, 1)
    Xg = x_c + (Xg - x_c) * g[:, None]
    P = np.stack([Xg, y, Zg], 2)
    return Cloth(P, flip=False)


# ---------- stitches ----------
def _cable_pos(Y):
    """0..1: where a cable's first pair sits (left .. right) along the scarf, crossing every
    CABLE_EVERY rows."""
    r = Y / RH / CABLE_EVERY
    k = np.floor(r)
    f = r - k
    # the crossing takes about a third of the interval
    s = np.clip((f - 0.35) / 0.32, 0, 1)
    s = s * s * (3 - 2 * s)
    parity = np.mod(k, 2)
    return np.where(parity == 0, s, 1 - s)


def stitches(length, rng):
    """Grain polylines in fabric coordinates (X, Y, Z) for a strip `length` long: (n, 9, 3) and a
    tone per grain. Z is off the cloth face (positive outwards)."""
    rows = int(length / RH)
    t = np.linspace(0, 1, 9)
    grains, tones = [], []
    cable_cols = [i for i, c in enumerate(COLS) if c == "C"]
    cables = [cable_cols[i:i + 4] for i in range(0, len(cable_cols), 4)]
    zb = np.sin(np.pi * t) ** 0.8
    for r in range(rows):
        Y0 = (r + 0.5) * RH
        for ci, c in enumerate(COLS):
            Xc = (ci + 0.5) * CW
            if c == "P":
                sgn = 1 if r % 2 == 0 else -1
                X = Xc + CW * (t - 0.5) * 1.05
                Yv = Y0 + sgn * 0.20 * RH * np.sin(np.pi * t)
                Z = RY * (-0.95 + 0.55 * zb)
                grains.append(np.stack([X, Yv, Z], 1))
                continue
            dz, slant = 0.25 * RY, 0.0
            if c == "C":
                cab = [cab for cab in cables if ci in cab][0]
                j = cab.index(ci)
                pair, k = (0, j) if j < 2 else (1, j - 2)
                pos = float(_cable_pos(np.array([Y0]))[0])
                p = pos if pair == 0 else 1 - pos
                Xl = (cab[0] + 0.5) * CW
                Xc = Xl + (2 * p + k) * CW
                # slope of the pair's travel
                pos2 = _cable_pos(np.array([Y0 + 0.5 * RH]))
                pos1 = _cable_pos(np.array([Y0 - 0.5 * RH]))
                dp = float(pos2[0] - pos1[0]) * (1 if pair == 0 else -1)
                slant = 2 * CW * dp / RH
                front = (dp > 0)              # the pair travelling right goes over
                if abs(dp) > 1e-3:
                    dz = (0.85 if front else -0.75) * RY
                else:
                    dz = 0.45 * RY
            for side in (-1, 1):
                x0, y0 = side * 0.10 * CW, -0.58 * RH
                x1, y1 = side * 0.47 * CW, 0.62 * RH
                lx = x0 + (x1 - x0) * t + side * 0.06 * CW * np.sin(np.pi * t)
                ly = y0 + (y1 - y0) * t
                lx = lx + slant * ly
                Z = RY * (-0.45 + 1.0 * zb) + dz * zb
                g = np.stack([Xc + lx, Y0 + ly, Z], 1)
                grains.append(g)
    grains = np.array(grains)
    grains[..., :2] += rng.normal(0, 0.00012, grains[..., :2].shape)
    tones = np.clip(1 + 0.10 * rng.normal(size=len(grains)), 0.75, 1.25)
    return grains, tones


# ---------- yarn: grains, backing, fringe, fuzz ----------
def zbuffer(P, x0, z0, h, nx, nz, splat=1):
    """The front-most y of a cloud of points on an (x, z) raster (inf where none)."""
    buf = np.full((nz, nx), np.inf)
    ix = np.round((P[:, 0] - x0) / h).astype(int)
    iz = np.round((P[:, 2] - z0) / h).astype(int)
    for dx in range(-splat, splat + 1):
        for dz in range(-splat, splat + 1):
            jx, jz = ix + dx, iz + dz
            ok = (jx >= 0) & (jx < nx) & (jz >= 0) & (jz < nz)
            np.minimum.at(buf, (jz[ok], jx[ok]), P[ok, 1])
    return buf


class Raster:
    def __init__(self, P, x0=-0.20, x1=0.20, z0=0.15, z1=0.56, h=0.0015):
        self.x0, self.z0, self.h = x0, z0, h
        self.nx, self.nz = int((x1 - x0) / h) + 1, int((z1 - z0) / h) + 1
        self.buf = zbuffer(P, x0, z0, h, self.nx, self.nz, splat=2)

    def __call__(self, x, z):
        ix = np.clip(np.round((x - self.x0) / self.h).astype(int), 0, self.nx - 1)
        iz = np.clip(np.round((z - self.z0) / self.h).astype(int), 0, self.nz - 1)
        return self.buf[iz, ix]


def grid_quads(nu, nv, periodic_u=False):
    i = np.arange(nu if periodic_u else nu - 1)[:, None]
    j = np.arange(nv - 1)[None, :]
    i1 = (i + 1) % nu
    q = np.stack([i * nv + j, i * nv + j + 1, i1 * nv + j + 1, i1 * nv + j], -1)
    return q.reshape(-1, 4)


def _ring_quads(nu, nv):
    """Quads of a torus-like grid closed both ways."""
    i = np.arange(nu)[:, None]
    j = np.arange(nv)[None, :]
    i1, j1 = (i + 1) % nu, (j + 1) % nv
    return np.stack([i * nv + j, i * nv + j1, i1 * nv + j1, i1 * nv + j], -1).reshape(-1, 4)


def slab(cloth, z_front, z_back, edge_seg=6):
    """The knit's body behind the grains: a closed ring of front face, rounded edge, back face and
    rounded edge for each row (for the hanging ends)."""
    P, N = cloth.P, cloth.N
    nu, nv, _ = P.shape
    side = _unit(np.gradient(P, axis=1))
    mid = (z_front + z_back) / 2
    rad = (z_front - z_back) / 2
    ring = []
    for j in range(nv):
        ring.append(P[:, j] + N[:, j] * z_front)
    a = np.linspace(0, np.pi, edge_seg + 2)[1:-1]
    for ang in a:   # right edge, front to back
        ring.append(P[:, -1] + N[:, -1] * (mid + rad * np.cos(ang)) + side[:, -1] * rad * np.sin(ang))
    for j in range(nv - 1, -1, -1):
        ring.append(P[:, j] + N[:, j] * z_back)
    for ang in a:   # left edge, back to front
        ring.append(P[:, 0] + N[:, 0] * (mid - rad * np.cos(ang)) - side[:, 0] * rad * np.sin(ang))
    R = np.stack(ring, 1)                        # (nu, m, 3)
    m = R.shape[1]
    q = grid_quads(nu, m + 1)
    Rc = np.concatenate([R, R[:, :1]], 1)
    return Rc.reshape(-1, 3), q


def fringe(cloth, rng, over, n_tassels=8, per=8, length=0.066):
    """Tassels knotted through the cast-off edge (fabric Y = 0 is the cloth's last row), each a few
    pieces of the yarn folded in half; they hang and rest on what is behind them."""
    paths, radii = [], []
    for k in range(n_tassels):
        X = W * (k + 0.5) / n_tassels + rng.normal(0, 0.0008)
        top = cloth.at(np.array([X]), np.array([cloth.length - 0.0015]), np.array([0.0]))[0]
        nrm = _unit(cloth.at(np.array([X]), np.array([cloth.length - 0.0015]), np.array([0.01]))[0] - top)
        # the knot: a loop of yarn round the edge
        a = np.linspace(-0.2, np.pi + 0.2, 10)
        down = np.array([0.0, 0.0, -1.0])
        loop = top[None] + nrm[None] * (RY * 1.6 * np.cos(a))[:, None] + down * (0.002 + 0.003 * np.sin(a))[:, None]
        loop = loop + np.array([1.0, 0, 0]) * 0.0022 * np.cos(a)[:, None]
        paths.append(loop)
        radii.append(np.full(10, RY * 1.05))
        L = length * (1 + 0.06 * rng.normal())
        tw = rng.uniform(0, 2 * np.pi)
        sway = rng.normal(0, 0.0025)                # the whole tassel hangs a little askew
        for sidx in range(per):
            ang = tw + 2 * np.pi * sidx / per
            ns = 14
            u = np.linspace(0, 1, ns)
            Ls = L * (1 + 0.09 * rng.normal())
            spread = 0.0015 + 0.0030 * u ** 1.3 * (1 + 0.4 * abs(rng.normal()))
            bend = rng.normal(0, 0.0011) * np.sin(np.pi * u * rng.uniform(0.6, 1.2))
            x = top[0] + spread * np.cos(ang + 1.3 * u) + sway * u ** 1.5 + bend
            z = top[2] - 0.004 - Ls * u
            y0 = top[1] + spread * np.sin(ang + 1.2 * u) * 0.6
            yb = over(x, z) - RY * 1.1
            y = np.minimum(y0, yb)
            y = np.minimum.accumulate(np.minimum(y, y0[0] + 0.0))  # it does not swing back under the cloth
            P = np.stack([x, y, z], 1) + rng.normal(0, 0.00025, (ns, 3)) * u[:, None]
            paths.append(P)
            r = np.full(ns, RY * 0.92)
            r[-1] = RY * 0.55
            radii.append(r)
    return paths, radii


def fuzz(paths, radii, rng, per=18):
    """Loose wool fibres standing off the yarn: a soft halo at its edges."""
    n, K, _ = paths.shape
    T, Nf, Bf = yarn.frames(paths)
    m = n * per
    gi = rng.integers(0, n, m)
    tk = rng.uniform(0.12, 0.88, m) * (K - 1)
    k0 = np.floor(tk).astype(int)
    f = tk - k0
    P = paths[gi, k0] * (1 - f)[:, None] + paths[gi, k0 + 1] * f[:, None]
    r = radii[gi, k0]
    ang = rng.uniform(0, 2 * np.pi, m)
    out = np.cos(ang)[:, None] * Nf[gi, k0] + np.sin(ang)[:, None] * Bf[gi, k0]
    root = P + out * r[:, None] * 0.85
    L = rng.uniform(0.0008, 0.0032, m) * (1 + rng.exponential(0.4, m))
    tan = T[gi, k0] * rng.choice([-1, 1], m)[:, None]
    d0 = _unit(out * 0.8 + tan * rng.uniform(0.2, 1.2, m)[:, None])
    curl = _unit(rng.normal(size=(m, 3)))
    pts = [root]
    d = d0
    for s in range(3):
        d = _unit(d + curl * 0.45)
        pts.append(pts[-1] + d * (L / 3)[:, None])
    return np.stack(pts, 1)


# ---------- the whole scarf ----------
END_A = (0.023, 0.492, 0.262)    # x of its middle, top z, bottom z (the one in front)
END_B = (-0.024, 0.444, 0.292)   # the one underneath, coming out from below the wrap
CLR_END = CLR + 2.2 * RY         # cloth middle to body for a hanging end
FRONT = 1.8 * RY                 # how far the knit stands in front of the cloth's middle
BACK = 2.2 * RY                  # and behind it


class Keepout:
    """What the scarf does to the fur: no roots under the cloth, and strands that reach into it are
    pressed out of it."""

    def __init__(self, info, ends, fringe=None):
        self.info, self.ends, self.fringe = info, ends, fringe

    def _wrap(self, P):
        """Each point's place in the roll's section: angle round the neck, distance from the axis,
        and the section's centre and radii there."""
        th = np.mod(np.arctan2(P[:, 0], -(P[:, 1] - Y_AX)), 2 * np.pi)
        rho = np.hypot(P[:, 0], P[:, 1] - Y_AX)
        info = self.info
        fi = th / (2 * np.pi) * NT
        i0 = np.floor(fi).astype(int) % NT
        i1 = (i0 + 1) % NT
        t = fi - np.floor(fi)

        def lerp(A):
            return (1 - t) * A[i0] + t * A[i1]
        return th, rho, lerp(info["zc"]), lerp(info["rc"]), lerp(info["a"]), lerp(info["b"])

    def _end(self, cloth, P):
        Pg = cloth.P
        zs = Pg[:, 0, 2]                      # rows from the top down
        z = P[:, 2]
        inside_z = (z <= zs[0]) & (z >= zs[-1])
        fi = np.interp(-z, -zs, np.arange(len(zs)))
        i0 = np.clip(np.floor(fi).astype(int), 0, len(zs) - 2)
        t = fi - i0
        row_x = (1 - t)[:, None] * Pg[i0, :, 0] + t[:, None] * Pg[i0 + 1, :, 0]
        row_y = (1 - t)[:, None] * Pg[i0, :, 1] + t[:, None] * Pg[i0 + 1, :, 1]
        x = P[:, 0]
        xl, xr = row_x[:, 0], row_x[:, -1]
        inside_x = (x >= xl) & (x <= xr)
        fx = Cloth._fv(np.clip((x - xl) / np.maximum(xr - xl, 1e-9), 0, 1),
                       (row_x - xl[:, None]) / np.maximum(xr - xl, 1e-9)[:, None])
        j0 = np.clip(np.floor(fx).astype(int), 0, row_x.shape[1] - 2)
        u = fx - j0
        ym = (1 - u) * row_y[np.arange(len(P)), j0] + u * row_y[np.arange(len(P)), j0 + 1]
        return inside_z, inside_x, x - xl, xr - x, ym

    def keep(self, P):
        th, rho, zc, rc, a, b = self._wrap(P)
        e = ((rho - rc) / (a + 0.010)) ** 2 + ((P[:, 2] - zc) / (b + 0.002)) ** 2
        ok = e > 1.0
        for c in self.ends:
            iz, ix, dl, dr, ym = self._end(c, P)
            under = iz & (dl > 0.012) & (dr > 0.012) & (P[:, 1] > ym - FRONT)
            ok &= ~under
        return ok

    def push(self, pts):
        n, K, _ = pts.shape
        P = pts[:, 1:].reshape(-1, 3).copy()
        th, rho, zc, rc, a, b = self._wrap(P)
        A, B = a + FRONT + 0.0012, b + FRONT + 0.0012
        dr, dz = rho - rc, P[:, 2] - zc
        e = np.sqrt((dr / A) ** 2 + (dz / B) ** 2)
        hit = e < 1.0
        if hit.any():
            # out to the section's surface, along the ray from its centre
            k = 1.0 / np.maximum(e[hit], 1e-6)
            rho_n = rc[hit] + dr[hit] * k
            P[hit, 2] = zc[hit] + dz[hit] * k
            d = np.stack([np.sin(th[hit]), -np.cos(th[hit])], 1)
            P[hit, 0] = d[:, 0] * rho_n
            P[hit, 1] = Y_AX + d[:, 1] * rho_n
        for c in self.ends:
            iz, ix, dl, dr, ym = self._end(c, P)
            inside = iz & ix & (P[:, 1] > ym - FRONT) & (P[:, 1] < ym + BACK + 0.0008)
            # near an edge the pile bulges out from under the cloth; further in it is pressed flat
            edge = inside & (np.minimum(dl, dr) < 0.010)
            left = dl < dr
            P[edge & left, 0] = (P[:, 0] - dl - 0.0015)[edge & left]
            P[edge & ~left, 0] = (P[:, 0] + dr + 0.0015)[edge & ~left]
            flat = inside & ~edge
            P[flat, 1] = ym[flat] + BACK + 0.0008 + 0.0015 * np.abs(np.sin(P[flat, 0] * 2900 + P[flat, 2] * 1700))
        if self.fringe is not None:
            # the tassels lie on the pile and flatten it
            yf = self.fringe(P[:, 0], P[:, 2])
            under = np.isfinite(yf) & (P[:, 1] > yf - RY) & (P[:, 1] < yf + RY + 0.006)
            P[under, 1] = yf[under] + RY + 0.0008 + 0.003 * np.abs(np.sin(P[under, 0] * 2300 + P[under, 2] * 3100))
        pts[:, 1:] = P.reshape(n, K - 1, 3)
        return pts


def make(rng):
    """Everything the scarf is made of, as arrays: yarn tubes (paths, radii, tones), backing meshes,
    fuzz fibres, and the Keepout for the fur."""
    wrap, info = build_wrap()
    period = RH * CABLE_EVERY * 2
    rows_len = period * max(1, round(wrap.length / period))
    g, tone = stitches(rows_len, rng)
    g[..., 1] *= wrap.length / rows_len
    shp = g.shape
    flat = g.reshape(-1, 3)
    paths = [wrap.at(flat[:, 0], flat[:, 1], flat[:, 2]).reshape(shp)]
    tones = [tone]
    backs = []
    ring = info["ring"]
    nb = ring.shape[1]
    backs.append((ring.reshape(-1, 3), _ring_quads(NT, nb)))

    front_half = wrap.P[wrap.P[..., 1] < Y_AX - 0.05]
    wrap_r = Raster(front_half)

    # end B, under the wrap and coming out below it
    xB, ztB, zbB = END_B
    clothB = drape_end(xB, ztB, zbB, lambda xs: np.full(len(xs), np.inf), clr=CLR_END)
    rB = Raster(clothB.P.reshape(-1, 3))

    def over_A(x, z):
        return np.minimum(wrap_r(x, z) - FRONT - BACK - 0.0006, rB(x, z) - FRONT - BACK - 0.0004)
    xA, ztA, zbA = END_A
    clothA = drape_end(xA, ztA, zbA, lambda xs: over_A(xs, np.full(len(xs), ztA)), over=over_A, clr=CLR_END,
                       top_gather=0.72)
    ends = [clothB, clothA]
    fr_paths, fr_radii = [], []
    for cloth in (clothB, clothA):
        g, tone = stitches(cloth.length, rng)
        g[..., 1] = cloth.length - g[..., 1]
        shp = g.shape
        flat = g.reshape(-1, 3)
        paths.append(cloth.at(flat[:, 0], flat[:, 1], flat[:, 2]).reshape(shp))
        tones.append(tone)
        backs.append(slab(cloth, -0.9 * RY, -BACK))

        def over_f(x, z, cloth=cloth):
            yb = front_surface(x, z) - 0.0105    # resting on the pile it squashes
            if cloth is clothA:
                yb = np.minimum(yb, rB(x, z) - FRONT - 0.0005)
            return yb
        fp, frr = fringe(cloth, rng, over_f)
        fr_paths += fp
        fr_radii += frr
    grains = np.concatenate(paths)
    gtones = np.concatenate(tones)
    fringe_r = Raster(np.concatenate(fr_paths), h=0.0012)
    return dict(grains=grains, tones=gtones, backs=backs, fringe=(fr_paths, fr_radii),
                keepout=Keepout(info, ends, fringe_r), wrap=wrap, ends=ends)
