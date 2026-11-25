# The capybara plush's stuffed shape as a signed distance field (metres; the plush faces -y, sits on
# z = 0), and its mesh. The fur, the scarf and the face all ask this field where the surface is, so the
# shape lives in one place. Built from smooth-blended ellipsoids, rounded boxes and round cones; panel
# seams are shallow grooves; the bottom is squashed flat where the weight sits.
import numpy as np

H = 0.002  # voxel size of the mesh (2 mm)


SCARF_AX = -0.020   # the neck's axis (x = 0, this y), which the scarf's wrap goes round


def scarf_z(theta):
    """Height of the middle of the scarf's wrap: lower in front, under the chin; higher at the back,
    where the head meets the shoulders."""
    return 0.491 - 0.043 * np.cos(theta) + 0.004 * np.cos(2 * theta) + 0.005 * np.sin(2.3 * theta + 0.7)


def _len(v):
    return np.sqrt(np.einsum("...i,...i->...", v, v))


def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25


def smax(a, b, k):
    return -smin(-a, -b, k)


def ellipsoid(p, c, r):
    q = (p - np.asarray(c)) / np.asarray(r)
    k0 = _len(q)
    k1 = _len(q / np.asarray(r))
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def round_box(p, c, b, r, R=None):
    """b: half extents (outer), r: corner radius, R: the box's rotation (local -> world)."""
    q = p - np.asarray(c)
    if R is not None:
        q = q @ R  # world -> local
    q = np.abs(q) - (np.asarray(b) - r)
    return _len(np.maximum(q, 0.0)) + np.minimum(q.max(axis=-1), 0.0) - r


def round_cone(p, a, b, r1, r2):
    """A capsule from a (radius r1) to b (radius r2)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ba = b - a
    l2 = ba @ ba
    rr = r1 - r2
    a2 = l2 - rr * rr
    il2 = 1.0 / l2
    pa = p - a
    y = pa @ ba
    z = y - l2
    xv = pa * l2 - y[:, None] * ba
    x2 = np.einsum("ij,ij->i", xv, xv)
    y2 = y * y * l2
    z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d_mid = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d_b = np.sqrt(x2 + z2) * il2 - r2
    d_a = np.sqrt(x2 + y2) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d_b, np.where(np.sign(y) * a2 * y2 < k, d_a, d_mid))


def groove(d, s, depth, width):
    """Push the surface in by depth along a seam line, s being the distance to the seam."""
    return d + depth * np.exp(-(s / width) ** 2)


# ---------- the parts (all symmetric about x = 0 except the head's small turn) ----------
# The head is a rounded block dominated by the muzzle: a capybara's snout is long, deep and blunt, and
# on the plush its front is one big oval panel of dark velboa. The head is turned a few degrees and
# tilted, as a stuffed head settles.
HEAD_PIVOT = np.array([0.0, -0.02, 0.47])
HEAD_TURN, HEAD_ROLL, HEAD_NOD = np.radians(5.0), np.radians(-3.0), np.radians(4.0)
HEAD_R = rot_z(HEAD_TURN) @ rot_y(HEAD_ROLL) @ rot_x(-HEAD_NOD)   # head-local -> world
HEAD_S = 1.07                            # the head's own scale about the pivot
HEAD_OFF = np.array([0.0, -0.004, -0.019])
HEAD_C = np.array([0.0, -0.066, 0.596])
HEAD_RAD = (0.170, 0.208, 0.144)       # a loaf lying along y: long, flat-topped, blunt in front
MUZZLE_C = np.array([0.0, -0.204, 0.572])
MUZZLE_R = rot_x(np.radians(-5))      # nose bridge sloping down to the front
MUZZLE_B = (0.089, 0.098, 0.094)      # half extents of the snout block
EYE = np.array([0.098, -0.186, 0.664])  # the left bead (+x is the plush's left); mirrored
EYE_R = 0.0105                          # bead radius
EAR = np.array([0.148, 0.030, 0.692])
EAR_R = rot_z(np.radians(-22)) @ rot_y(np.radians(-30))
ARM_A = np.array([0.180, -0.080, 0.408])   # shoulder
ARM_B = np.array([0.120, -0.230, 0.360])   # paw
ARM_R = (0.058, 0.041)
ARM_B2 = np.array([0.117, -0.224, 0.371])  # the right paw (mirrored): a little higher, set back
FOOT_A = np.array([0.150, -0.165, 0.072])
FOOT_B = np.array([0.160, -0.250, 0.056])
FOOT_R = (0.066, 0.057)
FOOT_B2 = np.array([0.172, -0.244, 0.057])  # the right foot (mirrored): splayed out a bit more
SINK = 0.022  # how far the stuffed shape would sink below the floor if it were not squashed


def _mirror(p):
    q = p.copy()
    q[:, 0] = np.abs(q[:, 0])
    return q


def head_local(p):
    """World points into the head's own frame (before its turn, tilt and scale). Distances measured
    there are multiplied by HEAD_S to be world distances."""
    return ((p - HEAD_PIVOT - HEAD_OFF) @ HEAD_R) / HEAD_S + HEAD_PIVOT


def head_world(p):
    return ((np.asarray(p) - HEAD_PIVOT) * HEAD_S) @ HEAD_R.T + HEAD_PIVOT + HEAD_OFF


def _torso(p):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    # the weight spreads the bottom: wider and flatter near the floor
    bul = 1.0 + 0.05 * np.exp(-np.maximum(z, 0.0) / 0.07)
    q = p.copy()
    q[:, 0] = x / bul
    q[:, 1] = (y - 0.02) / bul + 0.02
    d = ellipsoid(q, (0, 0.020, 0.205), (0.256, 0.232, 0.226))
    # broad round shoulders under the head: an egg more than a pear
    d = smin(d, ellipsoid(q, (0, 0.010, 0.352), (0.198, 0.196, 0.170)), 0.15)
    # the belly pushes forward a little
    d = smin(d, ellipsoid(q, (0, -0.070, 0.205), (0.196, 0.168, 0.163)), 0.10)
    return d


def _head(p):
    q = head_local(p)
    d = ellipsoid(q, HEAD_C, HEAD_RAD)
    box = round_box(q, HEAD_C + (0, 0.0, -0.005), np.array(HEAD_RAD) * (0.96, 0.95, 0.97), 0.11)
    d = 0.50 * d + 0.50 * box
    m = _mirror(q)
    # full cheeks low on the sides of the snout
    d = smin(d, ellipsoid(m, (0.085, -0.115, 0.540), (0.090, 0.105, 0.080)), 0.05)
    # the muzzle: a broad blunt block, a little narrower and lower at the front
    s = (q - MUZZLE_C) @ MUZZLE_R
    f = np.clip(-s[:, 1] / MUZZLE_B[1], -1, 1)
    s2 = s.copy()
    s2[:, 0] *= 1.0 + 0.08 * f
    mz = round_box(s2, (0, 0, 0), MUZZLE_B, 0.080)
    d = smin(d, mz, 0.09)
    return d * HEAD_S


def _ears(p):
    m = _mirror(head_local(p))
    q = (m - EAR) @ EAR_R
    e = ellipsoid(q, (0, 0, 0), (0.033, 0.014, 0.031))
    cup = ellipsoid(q, (0, -0.013, 0.005), (0.025, 0.009, 0.023))   # the inner ear is cupped
    return smax(e, -cup, 0.004) * HEAD_S


def _sides(p, f):
    """f(mirrored points, paw end, foot end) evaluated with each side's own limb ends."""
    m = _mirror(p)
    left = p[:, 0] >= 0
    out = np.empty(len(p))
    if left.any():
        out[left] = f(m[left], ARM_B, FOOT_B)
    if (~left).any():
        out[~left] = f(m[~left], ARM_B2, FOOT_B2)
    return out


def _limbs(p):
    m = _mirror(p)
    arm = _sides(p, lambda q, ab, fb: round_cone(q, ARM_A, ab, *ARM_R))
    # the folded leg under the body and the foot poking forward
    thigh = ellipsoid(m, (0.150, -0.080, 0.118), (0.112, 0.140, 0.100))
    foot = _sides(p, lambda q, ab, fb: smax(round_cone(q, FOOT_A, fb, *FOOT_R),
                                            _axial(q, FOOT_A, fb) - 0.040, 0.018))   # a flat oval sole
    return arm, thigh, foot


def _axial(p, a, b):
    """Distance along the axis a -> b past b (positive beyond b)."""
    d = (b - a) / np.linalg.norm(b - a)
    return (p - b) @ d


def regions(p):
    """Signed distances to the edges of the panels cut from the dark short-pile fabric (negative
    inside), for the shader, the fur and the seam grooves. Each is confined to its own part."""
    m = _mirror(p)
    q = head_local(p)
    # the muzzle panel: a cap over the front of the snout, bounded by a tilted plane cut
    s = (q - MUZZLE_C) @ MUZZLE_R
    muz = ellipsoid(s, (0, -0.106, -0.004), (0.086, 0.064, 0.086)) * HEAD_S
    arm, thigh, foot = _limbs(p)
    # paw ends: the arm past a plane a little behind the paw's centre
    paw = -_sides(p, lambda q, ab, fb: _axial(q, ARM_A, ab) + 0.004)
    paw = np.where(arm < 0.02, paw, 1.0)
    # the soles: the front of each foot
    sole = -_sides(p, lambda q, ab, fb: _axial(q, FOOT_A, fb) + 0.004)
    sole = np.where(foot < 0.02, sole, 1.0)
    # inner ears
    e = (_mirror(q) - EAR) @ EAR_R
    ear_in = ellipsoid(e, (0, -0.017, 0.005), (0.026, 0.011, 0.024)) * HEAD_S
    return {"muzzle": muz, "paw": paw, "sole": sole, "ear_in": ear_in}


# The embroidered nose and mouth, in the muzzle's own frame seen from the front (x across, z up, metres
# from the snout block's centre): two nostril slits slanting in, a line down, and a soft w for the
# mouth. Each a polyline; the right half is mirrored.
NOSTRILS = [
    [(0.026, 0.040), (0.021, 0.033), (0.011, 0.027)],
    [(-0.026, 0.040), (-0.021, 0.033), (-0.011, 0.027)],
]
NOSTRIL_W = 0.0042
STITCH_PATHS = NOSTRILS + [
    [(0.0, 0.021), (0.0, -0.006), (0.0, -0.034)],
    [(0.0, -0.034), (0.008, -0.044), (0.020, -0.048), (0.032, -0.043), (0.038, -0.036)],
    [(0.0, -0.034), (-0.008, -0.044), (-0.020, -0.048), (-0.032, -0.043), (-0.038, -0.036)],
]


def _smoothstep(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def muzzle_local(p):
    return (head_local(p) - MUZZLE_C) @ MUZZLE_R


def stitch_distance(p, paths=None):
    """Distance in the front view of the snout to the nearest embroidered line (inf off the front)."""
    paths = STITCH_PATHS if paths is None else paths
    s = muzzle_local(p)
    out = np.full(len(p), np.inf)
    near = (s[:, 1] < -0.04) & (np.abs(s[:, 0]) < 0.06) & (np.abs(s[:, 2]) < 0.07)
    if not near.any():
        return out
    xz = s[near][:, [0, 2]]
    best = np.full(len(xz), np.inf)
    for path in paths:
        pts = np.array(path)
        for a, b in zip(pts[:-1], pts[1:]):
            ab = b - a
            t = np.clip(((xz - a) @ ab) / (ab @ ab), 0, 1)
            best = np.minimum(best, _len(xz - (a + t[:, None] * ab)))
    out[near] = best * HEAD_S
    return out


def sdf(p, seams=True):
    p = np.asarray(p, dtype=np.float64)
    d = _torso(p)
    d = smin(d, _head(p), 0.085)
    arm, thigh, foot = _limbs(p)
    d = smin(d, thigh, 0.07)
    d = smin(d, foot, 0.035)
    d = smin(d, arm, 0.024)
    d = smin(d, _ears(p), 0.010)
    if seams:
        r = regions(p)
        # sewn edges: the dark panels meet the fur fabric in a crease
        d = groove(d, np.abs(r["muzzle"]), 0.0028, 0.0035)
        d = groove(d, np.abs(r["paw"]), 0.0022, 0.003)
        d = groove(d, np.abs(r["sole"]), 0.0022, 0.003)
        # the centre seam over the head and down the back
        q = head_local(p)
        back = (q[:, 2] > 0.52) & (q[:, 1] > -0.10)
        d = np.where(back, groove(d, np.abs(q[:, 0]), 0.0016, 0.0028), d)
        d = np.where((p[:, 1] > 0.05) & (p[:, 2] <= 0.52), groove(d, np.abs(p[:, 0]), 0.0014, 0.0028), d)
        # the stuffing domes the muzzle panel; the embroidery pulls the velboa in along its lines
        d = d - 0.0045 * _smoothstep(r["muzzle"], 0.0, -0.035)
        d = groove(d, stitch_distance(p), 0.0013, 0.0019)
        d = groove(d, stitch_distance(p, NOSTRILS), 0.0010, NOSTRIL_W * 0.6)
        # bead eyes sit in small dents
        e1 = _len(_mirror(q) - EYE) * HEAD_S
        d = d + 0.0045 * np.exp(-(e1 / 0.013) ** 2)
    # the scarf, tied snug, pulls the stuffing in a little round the neck
    th = np.arctan2(p[:, 0], -(p[:, 1] - SCARF_AX))
    zc = scarf_z(th)
    d = d + 0.0075 * np.exp(-((p[:, 2] - zc) / 0.030) ** 2)
    # squash: cut flat at the floor with a soft rounded edge
    d = smax(d, -p[:, 2], 0.03)
    return d


def gradient(p, eps=0.0008, seams=True):
    p = np.asarray(p, dtype=np.float64)
    g = np.zeros_like(p)
    for i in range(3):
        o = np.zeros(3)
        o[i] = eps
        g[:, i] = sdf(p + o, seams) - sdf(p - o, seams)
    n = _len(g)
    return g / np.maximum(n, 1e-12)[:, None]


BOUNDS = (np.array([-0.31, -0.33, -0.004]), np.array([0.31, 0.28, 0.785]))


def mesh(h=H):
    """The zero level set as a quad mesh: (verts (n, 3), quads (m, 4)), faces wound outward."""
    import openvdb as vdb
    lo, hi = BOUNDS
    n = np.ceil((hi - lo) / h).astype(int) + 1
    xs = lo[0] + np.arange(n[0]) * h
    ys = lo[1] + np.arange(n[1]) * h
    zs = lo[2] + np.arange(n[2]) * h
    grid = np.empty((n[0], n[1], n[2]), np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    XY = np.stack([X.ravel(), Y.ravel()], 1)
    # coarse pass to skip empty slabs quickly
    for k, z in enumerate(zs):
        P = np.concatenate([XY, np.full((XY.shape[0], 1), z)], 1)
        grid[:, :, k] = sdf(P).reshape(n[0], n[1])
    g = vdb.FloatGrid(background=float(h * 3))
    g.copyFromArray(grid, tolerance=0.0)
    pts, quads = g.convertToQuads(0.0)
    verts = lo + pts.astype(np.float64) * h
    quads = quads.astype(np.int64)
    # orient outward: compare a face normal with the field's gradient
    v = verts[quads]
    fn = np.cross(v[:, 2] - v[:, 0], v[:, 3] - v[:, 1])
    fc = v.mean(1)
    sample = np.linspace(0, len(quads) - 1, 400).astype(int)
    gr = gradient(fc[sample])
    if np.einsum("ij,ij->i", fn[sample], gr).mean() < 0:
        quads = quads[:, ::-1]
    return verts, quads


def _unit(v):
    return v / np.maximum(_len(v), 1e-12)[:, None]


def flow(p):
    """The direction the pile lies in (world vectors, not yet projected onto the surface). Plush fabric
    is cut with its nap running down the body, back from the nose over the head, down the arms to the
    paws and forward along the feet."""
    p = np.asarray(p, dtype=np.float64)
    m = _mirror(p)
    sx = np.where(p[:, 0] < 0, -1.0, 1.0)
    arm, thigh, foot = _limbs(p)
    parts = np.stack([_torso(p), _head(p), arm, thigh, foot, _ears(p)], 1)
    w = np.exp(-(parts - parts.min(1, keepdims=True)) / 0.010)
    w /= w.sum(1, keepdims=True)
    n = len(p)
    dirs = np.zeros((6, n, 3))
    # body: down, a little out from the middle of the front
    dirs[0] = _unit(np.stack([0.25 * np.tanh(p[:, 0] / 0.1), np.zeros(n), -np.ones(n)], 1))
    # head: back and out from a point in front of the nose (head-local), then into world
    q = head_local(p)
    r = q - np.array([0.0, -0.34, 0.585])
    r[:, 2] *= 0.6
    hd = _unit(r) + np.array([0, 0, -0.35])
    dirs[1] = _unit(hd @ HEAD_R.T)
    # arms: towards the paw; legs and feet: forward and down
    ad = (ARM_B - ARM_A) / np.linalg.norm(ARM_B - ARM_A)
    # the arms' pile runs down them more than along them, so it is not seen end-on from the front
    dirs[2] = _unit(np.stack([ad[0] * sx, np.full(n, ad[1]), np.full(n, ad[2] - 1.1)], 1))
    dirs[3] = _unit(np.tile([0.0, -0.75, -0.65], (n, 1)))
    fd = (FOOT_B - FOOT_A) / np.linalg.norm(FOOT_B - FOOT_A)
    dirs[4] = np.stack([fd[0] * sx, np.full(n, fd[1]), np.full(n, fd[2])], 1)
    dirs[5] = np.tile([0.0, 0.0, 1.0], (n, 1))
    f = (w.T[:, :, None] * dirs).sum(0)
    return f, w
