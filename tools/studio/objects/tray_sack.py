# The burlap coffee sack lying on the tray, its mouth rolled back and turned toward the cup, and the
# beans: a heap inside the mouth pouring out onto the tray in a fan, and loose ones scattered.
# Sack-local metres: its axis along x, the closed (seamed) end at +x, the mouth at -x, the tray floor at
# z = 0; build() places it on the tray.
import math
import bpy, bmesh
from mathutils import Vector, noise as mnoise
from objects.books_kit import finish, subsurf

LEN = 0.270            # seam to the lip of the mouth
RY, RZ = 0.099, 0.064  # half width and half height of the full part: settled, wider than tall
X0 = LEN / 2           # the seamed end
NS, NT = 72, 96        # rows along, columns round


def smooth(a, b, x):
    t = min(max((x - a) / (b - a), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def section(s):
    """Half width, half height and how much the top has sunk, at s (0 seam .. 1 mouth)."""
    ey = math.sqrt(max(0.0, 1 - (1 - min(s / 0.24, 1.0)) ** 2))
    ry = RY * (0.04 + 0.96 * ey) * (1 - 0.10 * smooth(0.62, 0.92, s)) + 0.014 * smooth(0.90, 1.0, s)
    rz = RZ * (0.78 + 0.22 * ey)
    sink = 0.42 * smooth(0.50, 1.0, s)
    return ry, rz, sink


def heap_top(s):
    """The beans' level inside the sack at s, from the floor."""
    ry, rz, sink = section(s)
    return 2 * rz * (1 - sink) - 0.010


def point(s, th, seed=0.0):
    """A point of the sack's surface (before the cuff): th = 0 on top, pi underneath."""
    ry, rz, sink = section(s)
    c, sn = math.cos(th), math.sin(th)
    if c >= 0:            # upper half: rounder, sunk toward the mouth
        z = rz + rz * (1 - sink) * c
        y = ry * sn
    else:                 # lower half: squarer, resting flat
        k = abs(c) ** 0.55
        z = rz - rz * k
        y = ry * math.copysign(abs(sn) ** 0.7, sn)
    x = X0 - LEN * s
    p = Vector((x, y, z))
    # lumps of beans pressing through, slack folds, and pleats gathering toward the mouth
    q = Vector((x * 9, y * 9, z * 9 + seed))
    big = mnoise.noise(q) * 0.0065
    lumps = mnoise.noise(Vector((x * 85, y * 85, z * 85 + seed))) * 0.0016 * (1 - smooth(0.80, 0.98, s))
    pleat = math.sin(th * 7 + 3 * mnoise.noise(Vector((x * 6, 0.3, seed)))) * 0.0055 * smooth(0.70, 1.0, s) * max(0.0, c + 0.3)
    wr = mnoise.noise(Vector((s * 18, th * 2.2, seed + 4))) * 0.004 * (1 - smooth(0.0, 0.25, s))
    # creases: narrow ridges where the jute folded in the warehouse and kept the fold
    ridge = (1 - abs(mnoise.noise(Vector((x * 15 + 3.1, y * 15, z * 15 + seed))))) ** 6
    ridge2 = (1 - abs(mnoise.noise(Vector((x * 26 - 7.3, y * 26, z * 26 + seed * 2))))) ** 6
    crease = (ridge - 0.10) * 0.0055 + (ridge2 - 0.10) * 0.0030
    off = big + lumps + pleat + wr + crease * (0.35 + 0.65 * smooth(0.0, 0.3, s))
    rad = Vector((0, y, z - rz)).normalized() if (abs(y) + abs(z - rz)) > 1e-6 else Vector((0, 0, 1))
    p = p + rad * off
    p.z = max(p.z, 0.0012 + 0.0008 * mnoise.noise(Vector((x * 40, y * 40, seed))))
    return p


def cuff_point(u, th, base, normal, along):
    """The mouth's rolled-back cuff: the cloth turns outward over a soft fold and lies back along the
    outside for a few centimetres. u = 0 at the lip .. 1 at the raw edge."""
    rho = 0.009
    turn = 0.35
    if u < turn:
        a = math.pi * u / turn
        return base + along * (rho * math.sin(a)) + normal * (rho * (1 - math.cos(a)))
    t = (u - turn) / (1 - turn)
    return base - along * (0.055 * t) + normal * (2 * rho + 0.004 * t * t)


def sack(mats, seed=3.0):
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    rows, uvs = [], []
    ss = [i / NS for i in range(NS + 1)]
    for s in ss:
        rows.append([point(max(s, 0.002), 2 * math.pi * k / NT, seed) for k in range(NT)])
    # the cuff: continue each column past the lip, turning back outward
    lip = rows[-1]
    prev = rows[-2]
    NC = 16
    cuff_rows = []
    for j in range(1, NC + 1):
        u = j / NC
        row = []
        for k in range(NT):
            base = lip[k]
            along = (base - prev[k]).normalized()
            ry, rz, sink = section(1.0)
            centre = Vector((base.x, 0.0, rz))
            nrm = Vector((0.0, base.y - centre.y, base.z - centre.z))
            nrm = nrm.normalized() if nrm.length > 1e-6 else Vector((0, 0, 1))
            # the cuff rolls less underneath, where the sack rests on the tray
            th = 2 * math.pi * k / NT
            uu = u * (0.55 + 0.45 * max(0.0, math.cos(th)) ** 0.5)
            p = cuff_point(uu, th, base, nrm, along)
            p.z = max(p.z, 0.0014)
            ragged = mnoise.noise(Vector((k * 0.35, j * 0.2, seed + 9))) * 0.004 * u
            p += nrm * ragged
            row.append(p)
        cuff_rows.append(row)
    allrows = rows + cuff_rows
    V = [[bm.verts.new(p) for p in row] for row in allrows]
    # UVs in metres: v along the cloth, u round it
    vlen = [0.0]
    for a, b in zip(allrows, allrows[1:]):
        vlen.append(vlen[-1] + sum((pb - pa).length for pa, pb in zip(a, b)) / NT)
    for j in range(len(V) - 1):
        circ = sum((allrows[j][(k + 1) % NT] - allrows[j][k]).length for k in range(NT))
        for k in range(NT):
            k2 = (k + 1) % NT
            f = bm.faces.new((V[j][k], V[j][k2], V[j + 1][k2], V[j + 1][k]))
            u0, u1 = circ * k / NT, circ * (k + 1) / NT
            for loop, q in zip(f.loops, ((u0, vlen[j]), (u1, vlen[j]), (u1, vlen[j + 1]), (u0, vlen[j + 1]))):
                loop[uvl].uv = q
            f.smooth = True
    # close the seam end
    c = bm.verts.new(sum((v.co for v in V[0]), Vector()) / NT)
    for k in range(NT):
        bm.faces.new((V[0][(k + 1) % NT], V[0][k], c)).smooth = True
    ob = finish("coffee sack", bm, mats)
    so = ob.modifiers.new("solidify", "SOLIDIFY")
    so.thickness = 0.0018
    so.offset = 1.0
    so.use_even_offset = True
    subsurf(ob, 1)
    return ob, allrows


def inside(x, y, z, margin=0.006):
    """Whether a point in sack-local space lies inside the cloth (for placing beans)."""
    s = (X0 - x) / LEN
    if s < 0.0 or s > 1.0:
        return False
    ry, rz, sink = section(s)
    zz = (z - rz) / max(rz * (1 - sink) - margin, 1e-4) if z > rz else (z - rz) / max(rz - margin, 1e-4)
    return (y / max(ry - margin, 1e-4)) ** 2 + zz * zz < 1.0


# ---------------------------------------------------------------- loose jute: fuzz and the frayed edge

def _curves(name, pts, r_root, r_tip, mat):
    import numpy as np
    n, K, _ = pts.shape
    cv = bpy.data.hair_curves.new(name)
    cv.add_curves([K] * n)
    cv.position_data.foreach_set("vector", pts.astype(np.float32).ravel())
    rad = cv.attributes.new("radius", "FLOAT", "POINT")
    s = np.linspace(0, 1, K)[None]
    r = (np.asarray(r_root)[:, None] * (1 - s) + np.asarray(r_tip)[:, None] * s).astype(np.float32)
    rad.data.foreach_set("value", r.ravel())
    cv.materials.append(mat)
    ob = bpy.data.objects.new(name, cv)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def fibres(rows, mat, n_fuzz=6000, seed=7, skin=0.0018):
    """Stray fibres standing off the cloth, and unravelled threads hanging from the cuff's raw edge."""
    import numpy as np
    rng = np.random.default_rng(seed)
    P = np.array([[tuple(p) for p in row] for row in rows])            # (rows, NT, 3)
    R, C, _ = P.shape
    a = P[:-1, :]
    b = np.roll(P[:-1, :], -1, axis=1)
    c = np.roll(P[1:, :], -1, axis=1)
    d = P[1:, :]
    area = 0.5 * np.linalg.norm(np.cross(b - a, d - a), axis=2) + 0.5 * np.linalg.norm(np.cross(c - b, d - b), axis=2)
    cdf = np.cumsum(area.ravel())
    idx = np.searchsorted(cdf, rng.random(n_fuzz) * cdf[-1])
    j, k = np.divmod(np.minimum(idx, cdf.size - 1), C)
    fu, fv = rng.random(n_fuzz)[:, None], rng.random(n_fuzz)[:, None]
    A, B, Cc, D = a[j, k], b[j, k], c[j, k], d[j, k]
    root = (A * (1 - fu) + B * fu) * (1 - fv) + (D * (1 - fu) + Cc * fu) * fv
    tu = (B - A) + (Cc - D)
    tv = (D - A) + (Cc - B)
    nrm = np.cross(tu, tv)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    # the mesh's normals point out of the sack; make sure
    out = root - np.array([[0.0, 0.0, 1.0]]) * RZ
    out[:, 0] = 0.0
    flip = np.sum(nrm * out, axis=1) < 0
    nrm[flip] *= -1
    root = root + nrm * skin
    tang = tu / (np.linalg.norm(tu, axis=1, keepdims=True) + 1e-12)
    bit = np.cross(nrm, tang)
    ang = rng.uniform(0, 2 * np.pi, n_fuzz)[:, None]
    lift = rng.uniform(0.15, 0.95, n_fuzz)[:, None]
    dirn = (tang * np.cos(ang) + bit * np.sin(ang)) * np.cos(lift) + nrm * np.sin(lift)
    L = rng.uniform(0.0018, 0.0070, n_fuzz)[:, None]
    K = 5
    s = np.linspace(0, 1, K)[None, :, None]
    curl = rng.normal(0, 0.0007, (n_fuzz, 1, 3))
    pts = root[:, None, :] + dirn[:, None, :] * L[:, None, :] * s + curl * s ** 2 + np.array([0, 0, -1.0]) * (L[:, None, :] * 0.25) * s ** 2
    fuzz = _curves("sack fuzz", pts, np.full(n_fuzz, 0.000055), np.full(n_fuzz, 0.00002), mat)
    # the raw edge: threads come loose from the last row and hang
    edge, prev = P[-1], P[-3]
    m = C * 4
    t = rng.random(m)
    kk = (np.arange(m) // 4) % C
    k2 = (kk + 1) % C
    e = edge[kk] * (1 - t[:, None]) + edge[k2] * t[:, None]
    pdir = (edge[kk] - prev[kk])
    pdir /= np.linalg.norm(pdir, axis=1, keepdims=True) + 1e-12
    L = rng.uniform(0.003, 0.014, m)[:, None]
    K = 7
    s = np.linspace(0, 1, K)[None, :, None]
    wig = rng.normal(0, 0.0012, (m, 1, 3))
    pts = e[:, None, :] + pdir[:, None, :] * L[:, None, :] * s + np.array([0, 0, -1.0]) * (L[:, None, :] * 0.5) * s ** 2 + wig * s ** 1.5
    pts[:, :, 2] = np.maximum(pts[:, :, 2], 0.0004)
    fray = _curves("sack fray", pts, np.full(m, 0.00028), np.full(m, 0.00012), mat)
    return [fuzz, fray]
