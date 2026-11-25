# One case-bound hardcover, lying flat, in its own metres: height (head to tail) along x, the spine on
# +y and the fore-edge on -y, the bottom board on z = 0. A cloth-covered case (two boards and a rounded
# spine, a joint groove beside it, boards overhanging the text block by the squares), the text block
# (rounded and backed: convex spine, concave fore-edge) and a headband at each end of the spine.
import math
import bmesh
from mathutils import Vector
from objects.books_kit import finish, bevel, edge_weights

BOARD = 0.0028      # board with its cloth
SPINE_T = 0.0013    # the spine's stiffener and cloth
SQUARE = 0.0032     # boards overhang the text block by this at head, tail and fore-edge
GROOVE_W = 0.0022   # half width of the joint groove
GROOVE_D = 0.0011
GAP = 0.0007        # the hollow between the text block's spine and the case's


def dims(W, T):
    e = 0.085 * T + 0.0015          # how far the spine rounds out past the joint
    ys = W / 2 - e                   # where the boards meet the spine
    return e, ys


def case_path(W, T, n_arc=28):
    """The case's centreline (y, z) from the top board's fore-edge round the spine to the bottom
    board's fore-edge, with outer and inner offsets and the length along it."""
    e, ys = dims(W, T)
    yf = -W / 2
    zt, zb = T - BOARD / 2, BOARD / 2
    gc = ys - 0.0034                 # the groove's middle, on the board beside the spine
    g0, g1 = gc - GROOVE_W * 1.6, gc + GROOVE_W * 1.6
    n_b = max(2, round((g0 - yf) / 0.006))
    board = [yf + (g0 - yf) * i / n_b for i in range(n_b)]
    board += [g0 + (g1 - g0) * i / 16 for i in range(17)]
    board += [g1 + (ys - g1) * i / 3 for i in range(1, 4)]
    board = sorted(set(round(v, 7) for v in board))
    ay, az = e, T / 2 - BOARD / 2
    pts = []   # (y, z, nx, nz, t_out, t_in, kind)

    def groove(y):
        d = abs(y - gc) / (GROOVE_W * 1.6)
        return GROOVE_D * (math.cos(d * math.pi / 2) ** 2) if d < 1 else 0.0

    for y in board[:-1]:
        pts.append((y, zt, 0.0, 1.0, BOARD / 2 - groove(y), BOARD / 2, "top"))
    for i in range(n_arc + 1):
        th = math.pi / 2 - math.pi * i / n_arc
        y, z = ys + ay * math.cos(th), T / 2 + az * math.sin(th)
        # the ellipse's outward normal (its gradient)
        gx, gz = math.cos(th) / ay, math.sin(th) / az
        g = math.hypot(gx, gz)
        nx, nz = gx / g, gz / g
        k = 1 - abs(math.sin(th))
        w = min(1.0, k / 0.25)
        w = w * w * (3 - 2 * w)
        t_in = BOARD / 2 + (SPINE_T - BOARD) * w
        pts.append((y, z, nx, nz, BOARD / 2, t_in, "spine"))
    for y in reversed(board[:-1]):
        pts.append((y, zb, 0.0, -1.0, BOARD / 2 - groove(y), BOARD / 2, "bot"))
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    spine_idx = [i for i, p in enumerate(pts) if p[6] == "spine"]
    spine = (s[spine_idx[0]], s[spine_idx[-1]])
    return pts, s, spine


def case(name, H, W, T, mats, rnd):
    pts, s, spine = case_path(W, T)
    nx_st = max(8, int(H / 0.012))
    xs = [-H / 2 + H * j / nx_st for j in range(nx_st + 1)]
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    O, I = [], []
    for (y, z, ny, nz, to, ti, kind) in pts:
        O.append([bm.verts.new((x, y + ny * to, z + nz * to)) for x in xs])
        I.append([bm.verts.new((x, y - ny * ti, z - nz * ti)) for x in xs])
    n, m = len(pts), len(xs)

    def quad(vs, uvs):
        f = bm.faces.new(vs)
        for loop, q in zip(f.loops, uvs):
            loop[uvl].uv = q
        return f

    for i in range(n - 1):
        for j in range(m - 1):
            quad((O[i][j], O[i + 1][j], O[i + 1][j + 1], O[i][j + 1]),
                 ((xs[j], s[i]), (xs[j], s[i + 1]), (xs[j + 1], s[i + 1]), (xs[j + 1], s[i])))
            quad((I[i][j], I[i][j + 1], I[i + 1][j + 1], I[i + 1][j]),
                 ((xs[j], -s[i]), (xs[j + 1], -s[i]), (xs[j + 1], -s[i + 1]), (xs[j], -s[i + 1])))
    for j, sgn in ((0, -1), (m - 1, 1)):
        for i in range(n - 1):
            quad((O[i][j], I[i][j], I[i + 1][j], O[i + 1][j]),
                 ((xs[j] + sgn * 0.001, s[i]), (xs[j], s[i]), (xs[j], s[i + 1]), (xs[j] + sgn * 0.001, s[i + 1])))
    for i in (0, n - 1):
        for j in range(m - 1):
            quad((O[i][j], I[i][j], I[i][j + 1], O[i][j + 1]),
                 ((xs[j], s[i] + 0.001), (xs[j], s[i]), (xs[j + 1], s[i]), (xs[j + 1], s[i] + 0.001)))
    # a little life: the boards bow a fraction of a millimetre, the case is not a perfect extrusion
    for v in bm.verts:
        x, y, z = v.co
        u = x / (H / 2)
        v.co.z += 0.00035 * (1 - u * u) * (1 if z > T / 2 else -1) * max(0.0, (-y + W / 2 - 0.02) / W)
    ob = finish(name, bm, mats, sharp=35)
    # the four fore-edge corners rounded in plan, each worn its own amount, then every edge eased
    yf = -W / 2
    wts = {}
    for sx in (-1, 1):
        for sz in (-1, 1):
            wts[(sx, sz)] = rnd.uniform(0.45, 1.0)

    def corner(a, b):
        if abs(a.x - b.x) > 1e-6 or abs(abs(a.x) - H / 2) > 1e-6:
            return 0.0
        if max(a.y, b.y) > yf + 0.0005:
            return 0.0
        return wts[(1 if a.x > 0 else -1, 1 if (a.z + b.z) / 2 > T / 2 else -1)]

    edge_weights(ob, corner)
    b1 = bevel(ob, 0.0042, 6, weight=True, harden=False)
    b1.profile = 0.5
    bevel(ob, 0.00075, 3, 40)
    return ob, spine


def text_block(name, H, W, T, mats, rnd, nu=14, nw=56):
    """The pages as a grid mapped onto the block's section: u from fore-edge to spine, w through the
    thickness; extruded from tail to head."""
    e, ys = dims(W, T)
    pts, s, spine = case_path(W, T)
    apex_case_in = ys + e - (SPINE_T - BOARD / 2)
    ysh = ys - 0.0025
    a_y = apex_case_in - GAP - ysh
    yfe = -W / 2 + SQUARE
    c = 0.75 * a_y                    # the fore-edge is as concave as the spine is round
    z0, z1 = BOARD + 0.0001, T - BOARD - 0.0001
    hx = H / 2 - SQUARE
    # signatures stand a hair proud of or behind their neighbours at the fore-edge
    sig = []
    zz = z0
    while zz < z1:
        sig.append((zz, rnd.gauss(0, 0.00012)))
        zz += rnd.uniform(0.0022, 0.0034)

    def jitter(z):
        for k in range(len(sig) - 1, -1, -1):
            if z >= sig[k][0]:
                return sig[k][1]
        return 0.0

    def P(u, w, x):
        z = z0 + (z1 - z0) * w
        q = 2 * w - 1
        fy = yfe + c * (1 - q * q) + jitter(z) * (1 - u) ** 6
        sy = ysh + a_y * math.sqrt(max(0.0, 1 - q * q))
        return Vector((x, fy + (sy - fy) * u, z))

    # u spaced finely near both faces so the curved faces stay smooth
    us = [0.5 - 0.5 * math.cos(math.pi * i / nu) for i in range(nu + 1)]
    ws = [0.5 - 0.5 * math.cos(math.pi * i / nw) for i in range(nw + 1)]
    nx_st = max(6, int(H / 0.03))
    xs = [-hx + 2 * hx * j / nx_st for j in range(nx_st + 1)]
    bm = bmesh.new()
    V = {}

    def v(i, k, j):
        key = (i, k, j)
        if key not in V:
            V[key] = bm.verts.new(P(us[i], ws[k], xs[j]))
        return V[key]

    U, Wn, X = len(us) - 1, len(ws) - 1, len(xs) - 1
    for j in range(X):                       # fore-edge (u=0) and spine (u=1) faces
        for k in range(Wn):
            bm.faces.new((v(0, k, j), v(0, k + 1, j), v(0, k + 1, j + 1), v(0, k, j + 1)))
            bm.faces.new((v(U, k, j), v(U, k, j + 1), v(U, k + 1, j + 1), v(U, k + 1, j)))
        for i in range(U):                   # bottom (w=0) and top (w=1)
            bm.faces.new((v(i, 0, j), v(i, 0, j + 1), v(i + 1, 0, j + 1), v(i + 1, 0, j)))
            bm.faces.new((v(i, Wn, j), v(i + 1, Wn, j), v(i + 1, Wn, j + 1), v(i, Wn, j + 1)))
    for j in (0, X):                         # the head and tail: grids
        for i in range(U):
            for k in range(Wn):
                bm.faces.new((v(i, k, j), v(i + 1, k, j), v(i + 1, k + 1, j), v(i, k + 1, j)))
    ob = finish(name, bm, mats, sharp=40)
    bevel(ob, 0.0005, 2, 50)
    return ob, (ysh, a_y, z0, z1, hx)


def headbands(name, H, W, T, geo, mats):
    from objects.books_kit import tube
    ysh, a_y, z0, z1, hx = geo
    obs = []
    r = 0.00105
    for sx in (-1, 1):
        pts = []
        for i in range(25):
            q = -0.92 + 1.84 * i / 24
            z = (z0 + z1) / 2 + q * (z1 - z0) / 2
            y = ysh + a_y * math.sqrt(max(0.0, 1 - q * q)) - r * 0.9
            pts.append((sx * (hx + r * 0.35), y, z))
        obs.append(tube(name, pts, r, mats, seg=12))
    return obs
