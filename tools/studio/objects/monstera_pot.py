# The monstera's pot and what covers its soil: a matte black cylinder planter 0.45 m tall and 0.26 m
# across (a 7 mm wall, a softly rounded lip, a small chamfer at the foot), the soil 25 mm under the
# lip, and over it pine bark chips and small pebbles, dropped one by one onto what is already there.
import math
import numpy as np
from mathutils import noise as mnoise

POT_H, POT_R, WALL = 0.45, 0.13, 0.007
SOIL_Z = POT_H - 0.025
IN_R = POT_R - WALL


def pot_profile():
    """(r, z) from the centre of the base round the foot, up the outside, over the lip and down the
    inside to just under the soil."""
    prof = [(0.0, 0.004), (0.112, 0.004), (0.118, 0.0015), (0.121, 0.0)]
    # the foot's chamfer, then the wall
    prof += [(0.1255, 0.0), (0.1285, 0.0015), (0.1297, 0.0045), (POT_R, 0.009)]
    prof += [(POT_R, z) for z in np.linspace(0.02, POT_H - 0.012, 40)]
    # the lip, rounded on both sides
    c = (POT_R - WALL / 2, POT_H - WALL / 2)
    for a in np.linspace(0, math.pi, 14):
        prof.append((c[0] + WALL / 2 * math.cos(a), c[1] + WALL / 2 * math.sin(a) * 0.9))
    prof += [(IN_R, POT_H - 0.012), (IN_R, SOIL_Z - 0.02)]
    return prof


def lathe_mesh(prof, seg=160):
    """Rings of the profile round z; quads, UVs (around, along the profile in metres)."""
    P = np.array(prof)
    a = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = np.stack([P[:, 0:1] * np.cos(a), P[:, 0:1] * np.sin(a), np.repeat(P[:, 1:2], seg, 1)], -1).reshape(-1, 3)
    n = len(P)
    i = np.arange(n - 1)[:, None]
    k = np.arange(seg)[None, :]
    k1 = (k + 1) % seg
    Q = np.stack([i * seg + k, i * seg + k1, (i + 1) * seg + k1, (i + 1) * seg + k], -1).reshape(-1, 4)
    s = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    # per-loop UVs, the seam column using u = 1
    uq = np.stack([k + 0 * i, k1 + 0 * i, k1 + 0 * i, k + 0 * i], -1).astype(float) / seg
    uq[..., 1][np.broadcast_to(k1 == 0, uq[..., 1].shape)] = 1.0
    uq[..., 2][np.broadcast_to(k1 == 0, uq[..., 2].shape)] = 1.0
    vq = np.stack([s[i] + 0 * k, s[i] + 0 * k, s[i + 1] + 0 * k, s[i + 1] + 0 * k], -1)
    uv = np.stack([uq, vq], -1).reshape(-1, 2)
    return V, Q, uv


def soil_mesh(rng, n_r=34, n_a=140):
    """A lumpy disc of soil filling the pot at SOIL_Z, a little lower in the middle where it settles."""
    rs = np.linspace(0, IN_R + 0.002, n_r)
    a = np.linspace(0, 2 * np.pi, n_a, endpoint=False)
    R, A = np.meshgrid(rs, a, indexing="ij")
    X, Y = R * np.cos(A), R * np.sin(A)
    ph = rng.uniform(0, 50, 2)
    Z = np.array([[mnoise.noise((x * 40 + ph[0], y * 40 + ph[1], 0.5)) * 0.004 +
                   mnoise.noise((x * 160 + ph[1], y * 160, 3.1)) * 0.0012 for x, y in zip(rx, ry)]
                  for rx, ry in zip(X, Y)])
    Z += SOIL_Z - 0.006 * (1 - (R / IN_R) ** 2)
    V = np.stack([X, Y, Z], -1).reshape(-1, 3)
    i = np.arange(n_r - 1)[:, None]
    k = np.arange(n_a)[None, :]
    k1 = (k + 1) % n_a
    Q = np.stack([i * n_a + k, (i + 1) * n_a + k, (i + 1) * n_a + k1, i * n_a + k1], -1).reshape(-1, 4)
    return V, Q


def chip_mesh(rng, length, width, thick):
    """One pine bark chip: an irregular, broken slab, thicker in places, its top uneven with the plates
    of the bark. Returns verts, faces, the side faces' vertex range, z up around its own centre."""
    n = int(rng.integers(14, 20))
    ang = np.sort(rng.uniform(0, 2 * np.pi, n)) + rng.uniform(0, 2 * np.pi)
    # a broken outline: a few big bites and a jagged small scale
    rad = 1 + rng.uniform(-0.12, 0.08, n)
    for _ in range(int(rng.integers(1, 3))):
        k = int(rng.integers(n))
        rad[[k, (k + 1) % n]] *= rng.uniform(0.6, 0.8)
    xy = np.stack([np.cos(ang) * rad * length / 2, np.sin(ang) * rad * width / 2], 1)
    ph = rng.uniform(0, 50)
    tk = thick * (1 + 0.35 * np.array([mnoise.noise((x / length * 2.5 + ph, y / length * 2.5, 0.3)) for x, y in xy]))
    # rings: bottom, side (outermost), top edge, an inner ring on the top; centres top and bottom
    V = [np.column_stack([xy * 0.9, np.zeros(n)]),
         np.column_stack([xy, tk * 0.45]),
         np.column_stack([xy * 0.96, tk]),
         np.column_stack([xy * 0.55, tk * 1.02])]
    V = np.vstack(V + [np.array([[0, 0, 0.0], [0, 0, thick * 1.03]])])
    V[:, 2] += 0.2 * thick * np.array([mnoise.noise((x / length * 6 + ph, y / length * 6, 1.7)) for x, y, _ in V])
    # a slight curl, as bark keeps the curve of the trunk
    V[:, 2] += rng.uniform(-0.6, 0.6) * (V[:, 0] / length) ** 2 * length * 0.25
    F = []
    for L0 in range(3):
        for k in range(n):
            a, b = L0 * n + k, L0 * n + (k + 1) % n
            F.append([a, b, b + n, a + n])
    cb, ct = 4 * n, 4 * n + 1
    for k in range(n):
        F.append([(k + 1) % n, k, cb])                        # bottom fan
        F.append([3 * n + k, 3 * n + (k + 1) % n, ct])        # top centre fan
    return V, F, (0, 3 * n)


def pebble_mesh(rng, r, sub=2):
    """A small rounded stone: an icosphere squashed into an uneven ellipsoid."""
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V = np.array([v.co[:] for v in bm.verts])
    F = [[v.index for v in f.verts] for f in bm.faces]
    bm.free()
    sx, sy, sz = r * rng.uniform(0.9, 1.3), r * rng.uniform(0.7, 1.0), r * rng.uniform(0.45, 0.75)
    ph = rng.uniform(0, 50, 3)
    k = np.array([1 + 0.16 * mnoise.noise((x * 1.3 + ph[0], y * 1.3 + ph[1], z * 1.3 + ph[2])) for x, y, z in V])
    V = V * k[:, None] * np.array([sx, sy, sz])
    return V, F


def scatter(rng, n_chips=135, n_peb=40):
    """Where the chips and pebbles lie: (kind, x, y, z, turn, tilt_x, tilt_y, size...). Each falls onto a
    height field of what lies there already, so they pile and overlap as a mulch does."""
    G = 64
    hmap = np.full((G, G), SOIL_Z)
    xs = np.linspace(-IN_R, IN_R, G)

    def cell(x, y):
        return int(np.clip((x + IN_R) / (2 * IN_R) * (G - 1), 0, G - 1)), int(np.clip((y + IN_R) / (2 * IN_R) * (G - 1), 0, G - 1))

    items = []
    order = ["chip"] * n_chips + ["peb"] * n_peb
    rng.shuffle(order)
    for kind in order:
        for _ in range(20):
            rr = IN_R * math.sqrt(rng.uniform(0, 1)) * 0.97
            a = rng.uniform(0, 2 * math.pi)
            x, y = rr * math.cos(a), rr * math.sin(a)
            if kind == "chip":
                ln = rng.uniform(0.016, 0.042)
                w = ln * rng.uniform(0.45, 0.8)
                t = rng.uniform(0.004, 0.009)
                ext = ln / 2
            else:
                ln = rng.uniform(0.008, 0.016)
                w = t = ln
                ext = ln
            if rr + 0.6 * ext < IN_R:
                break
        i, j = cell(x, y)
        k = max(1, int(ext / (2 * IN_R) * G))
        under = hmap[max(i - k, 0):i + k + 1, max(j - k, 0):j + k + 1]
        z = float(np.percentile(under, 70))
        tilt = (rng.normal(0, 0.26), rng.normal(0, 0.26))
        items.append((kind, x, y, z, rng.uniform(0, 2 * math.pi), tilt, ln, w, t))
        top = z + (t if kind == "chip" else t * 1.2)
        kk = max(1, int(0.7 * ext / (2 * IN_R) * G))
        sub = hmap[max(i - kk, 0):i + kk + 1, max(j - kk, 0):j + kk + 1]
        np.maximum(sub, top - 0.25 * (t if kind == "chip" else ln), out=sub)
    return items
