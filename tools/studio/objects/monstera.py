# The monstera: a Monstera deliciosa about 1.5 m tall in a matte black cylinder pot (0.45 m tall, 0.26 m
# across), its soil covered with bark chips and pebbles. Fourteen leaves on long petioles rise from a
# cluster of three short upright stems: the higher leaves more upright, the lower ones reaching further
# out and drooping, two young ones smaller and barely split; two brown aerial roots, dry sheaths at old
# nodes. Built at real size around the origin, the pot on the floor at z = 0; the camera looks along +y.
import math, time
import bpy
import numpy as np
from mathutils import Vector, Matrix, noise as mnoise
from objects import monstera_leaf as ml
from objects import monstera_shaders as sh
from objects import monstera_pot as pot
from objects.capybara_yarn import tubes

SEED = 5


def _log(*a):
    print("monstera:", *a, flush=True)


def mesh(name, verts, faces, uv=None, attrs=None, mat_index=None, smooth=True):
    """A mesh object from numpy arrays; faces is a list of (k, n) index arrays (triangles, quads...)."""
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co", np.asarray(verts, np.float32).ravel())
    sizes = np.concatenate([np.full(len(f), f.shape[1]) for f in faces])
    flat = np.concatenate([f.ravel() for f in faces]).astype(np.int32)
    me.loops.add(len(flat))
    me.loops.foreach_set("vertex_index", flat)
    me.polygons.add(len(sizes))
    me.polygons.foreach_set("loop_start", (np.cumsum(sizes) - sizes).astype(np.int32))
    me.polygons.foreach_set("loop_total", sizes.astype(np.int32))
    me.update(calc_edges=True)
    if uv is not None:
        layer = me.uv_layers.new(name="UVMap")
        layer.data.foreach_set("uv", np.asarray(uv, np.float32)[flat].ravel() if len(uv) == len(verts)
                               else np.asarray(uv, np.float32).ravel())
    for k, vals in (attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", "POINT")
        a.data.foreach_set("value", np.asarray(vals, np.float32))
    if mat_index is not None:
        me.polygons.foreach_set("material_index", np.asarray(mat_index, np.int32))
    me.polygons.foreach_set("use_smooth", np.full(len(sizes), smooth))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def frame(origin, along, normal_hint):
    """A rotation whose columns are (across, along, normal), along exactly `along`."""
    t = Vector(along).normalized()
    n = Vector(normal_hint)
    n = (n - t * n.dot(t)).normalized()
    b = t.cross(n)
    return Matrix.Translation(origin) @ Matrix((b, t, n)).transposed().to_4x4()


# ---------- one leaf ----------
def leaf_object(name, leaf, sp, rng, M, mats, props, yel=None, dmg=None):
    """Build a blade from the flat leaf, bend it by sp, place it by M (leaf-local to plant), and the
    raised midrib under it."""
    d = ml.blade(leaf, sp, rng)
    P = np.asarray(d["P"])
    R = np.array(M.to_3x3())
    o = np.array(M.translation)
    Pw = P @ R.T + o
    data = dict(d["data"])
    n = len(P)
    uv2 = d["uv"]
    data["yel"] = yel(uv2) if yel else np.zeros(n)
    data["dmg"] = dmg(uv2, data["ed"]) if dmg else np.zeros(n)
    mi = np.concatenate([np.zeros(len(d["tris"]), int), np.ones(len(d["quads"]), int)])
    ob = mesh(name, Pw, [d["tris"], d["quads"]], uv=uv2, attrs=data, mat_index=mi)
    ob.data.materials.append(mats["leaf"])
    ob.data.materials.append(mats["edge"])
    for k, v in props.items():
        ob[k] = v
    # the midrib underneath: a tube along the centre line, sunk so only its top breaks the upper face
    C, Rf, us = d["rib"]
    L = leaf.L
    r = 0.0045 * (L / 0.36) * (1 - 0.85 * (us / us[-1]) ** 0.75) + 0.0003
    Nn = Rf[:, :, 2]
    path = C - Nn * (r * 0.82)[:, None]
    rib = capped_tube(name + " midrib", path @ R.T + o, r, [mats["rib"]], sides=10)
    return ob, rib


def materials():
    return dict(leaf=sh.leaf(), edge=sh.leaf_edge(), rib=sh.midrib(), petiole=sh.petiole(), stem=sh.stem(),
                root=sh.root(), pot=sh.pot(), soil=sh.soil(), chip=sh.bark_chip(), peb=sh.pebbles(),
                sheath=sh.cataphyll())


def bezier(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = (np.asarray(p, float) for p in (p0, p1, p2, p3))
    return ((1 - t) ** 3) * p0 + 3 * ((1 - t) ** 2) * t * p1 + 3 * (1 - t) * t * t * p2 + t ** 3 * p3


def capped_tube(name, path, radii, mats, attrs=None, sides=12, cap=(True, True)):
    """A tube along a polyline with its ends closed by fans; per-vertex attributes are given per ring."""
    v, q, uv = tubes(path[None], radii[None], sides=sides)
    K = len(path)
    faces = [q]
    uvs = [uv]
    extra = []
    for end, on in ((0, cap[0]), (K - 1, cap[1])):
        if not on:
            continue
        c = len(v) + len(extra)
        extra.append(path[end])
        ring = end * sides + np.arange(sides)
        tri = np.stack([ring, np.roll(ring, -1), np.full(sides, c)], 1)
        if end == 0:
            tri = tri[:, ::-1]
        faces.append(tri)
        uvs.append(np.zeros((sides * 3, 2)))
    V = np.vstack([v] + ([np.array(extra)] if extra else []))
    at = {}
    for k, per_ring in (attrs or {}).items():
        vals = np.repeat(np.asarray(per_ring, float), sides)
        ends = [per_ring[0] if cap[0] else None, per_ring[-1] if cap[1] else None]
        at[k] = np.concatenate([vals, [e for e in ends if e is not None]])
    ob = mesh(name, V, faces, uv=np.vstack(uvs), attrs=at)
    for m in mats:
        ob.data.materials.append(m)
    return ob


# ---------- the plant's layout ----------
# Three short stems out of the soil, leaning a little apart (base x, y; top x, y, z; radius).
STEMS = [((0.024, 0.020), (0.070, 0.050, 0.66), 0.019),
         ((-0.032, 0.006), (-0.095, -0.012, 0.61), 0.017),
         ((0.004, -0.034), (0.030, -0.090, 0.56), 0.015)]

# Most blades turn their upper faces towards the light, high on the left in front (the key light), so
# from the camera most are seen in three-quarter view, a few edge on.
LIGHT = (-0.45, -0.55, 0.70)

# The leaves: which stem and how far up it (0 soil .. 1 its top), where the blade's base sits, the
# midrib's heading (degrees, 0 = +x, 90 = away from the camera) and pitch, which way the upper face
# turns (a hint vector, added to LIGHT), length, maturity (1 fully split), how it bends ('up' upright,
# 'mid', 'low' drooping, 'young'), and specials. Leaves reaching right stay low enough to pass over the
# desk's left end under the monitors.
LEAVES = [
    # the youngest, upright in the middle, and two upright leaves above
    dict(stem=2, node=0.99, base=(0.02, -0.03, 1.25), az=95, pitch=64, face=(0.0, -1.0, 0.2), L=0.23, mat=0.15, tier="young"),
    dict(stem=1, node=0.96, base=(-0.10, 0.06, 1.22), az=150, pitch=44, face=(0.0, 0.0, 0.3), L=0.39, mat=1.0, tier="up"),
    dict(stem=0, node=0.97, base=(0.10, 0.06, 1.19), az=58, pitch=40, face=(0.3, 0.0, 0.2), L=0.37, mat=1.0, tier="up"),
    # the middle ring
    dict(stem=1, node=0.86, base=(-0.26, -0.02, 1.04), az=176, pitch=20, face=(0.0, 0.0, 0.4), L=0.40, mat=1.0, tier="mid"),
    dict(stem=0, node=0.84, base=(0.21, 0.03, 1.00), az=12, pitch=12, face=(0.2, 0.0, 0.5), L=0.36, mat=1.0, tier="low"),
    dict(stem=2, node=0.88, base=(0.03, -0.19, 1.05), az=272, pitch=34, face=(0.2, -0.6, 0.0), L=0.37, mat=1.0, tier="mid"),
    dict(stem=0, node=0.80, base=(-0.04, 0.21, 1.10), az=98, pitch=32, face=(0.0, 0.6, 0.6), L=0.38, mat=1.0, tier="mid"),
    dict(stem=2, node=0.93, base=(0.10, -0.08, 1.13), az=305, pitch=42, face=(0.1, -0.4, 0.0), L=0.27, mat=0.5, tier="young"),
    # the lower ring, reaching out and drooping, the lowest down to the pot's rim
    dict(stem=1, node=0.55, base=(-0.33, -0.08, 0.82), az=198, pitch=6, face=(0.0, 0.0, 0.5), L=0.40, mat=1.0, tier="low", yellow=True),
    dict(stem=0, node=0.58, base=(0.22, -0.20, 0.85), az=-38, pitch=6, face=(0.3, 0.0, 0.5), L=0.37, mat=1.0, tier="low", tear=True),
    dict(stem=2, node=0.62, base=(-0.11, -0.28, 0.76), az=252, pitch=4, face=(0.0, -0.3, 0.4), L=0.37, mat=1.0, tier="low"),
    dict(stem=1, node=0.70, base=(-0.23, 0.18, 0.88), az=140, pitch=10, face=(0.0, 0.3, 0.5), L=0.38, mat=1.0, tier="low"),
    dict(stem=0, node=0.70, base=(0.13, 0.20, 0.97), az=75, pitch=16, face=(0.0, 0.5, 0.5), L=0.36, mat=0.95, tier="mid"),
    dict(stem=1, node=0.30, base=(-0.30, -0.25, 0.64), az=222, pitch=-4, face=(0.0, -0.4, 0.5), L=0.35, mat=0.95, tier="low"),
]

TIERS = {"up": dict(arch=(0.10, 0.30), droop=(0.30, 0.60), segdroop=(0.5, 1.1)),
         "mid": dict(arch=(0.08, 0.25), droop=(0.55, 0.85), segdroop=(0.8, 1.5)),
         "low": dict(arch=(0.05, 0.20), droop=(0.85, 1.25), segdroop=(1.0, 1.9)),
         "young": dict(arch=(0.10, 0.25), droop=(0.25, 0.50), segdroop=(0.3, 0.6))}


def stem_path(k, n=40):
    (bx, by), top, r = STEMS[k]
    b = np.array([bx, by, pot.SOIL_Z - 0.04])
    t = np.array(top)
    lean = t - b
    p1 = b + np.array([0, 0, 0.35 * lean[2]])
    p2 = t - lean * 0.35
    return bezier(b, p1, p2, t, n)


def shape_params(tier, rng):
    T = TIERS[tier]
    u = lambda ab: rng.uniform(*ab)
    return dict(arch=u(T["arch"]), droop=u(T["droop"]), dp=rng.uniform(1.6, 2.4), sweep=rng.uniform(-0.25, 0.25),
                twist=rng.uniform(-0.3, 0.3), fold={1: rng.uniform(0.08, 0.3), -1: rng.uniform(0.08, 0.3)},
                curl={1: rng.uniform(0.45, 1.0), -1: rng.uniform(0.45, 1.0)}, segdroop=u(T["segdroop"]),
                wave=rng.uniform(0.005, 0.011))


def leaf_frame(spec):
    az, pt = math.radians(spec["az"]), math.radians(spec["pitch"])
    along = Vector((math.cos(pt) * math.cos(az), math.cos(pt) * math.sin(az), math.sin(pt)))
    face = Vector(LIGHT).normalized() + Vector(spec["face"])
    return frame(Vector(spec["base"]), along, face)


def yellow_spot(leaf, rng):
    """An old leaf yellowing from the tip of one strap near its own tip."""
    s = rng.choice((1, -1))
    h = leaf.halves[s]
    q = leaf.veins[s][-2]
    vr = leaf.rim_v(h, q)
    cu, cv = h.u_of(q, vr), s * vr
    R = 0.32 * leaf.L

    def f(uv):
        d = np.hypot(uv[:, 0] - cu, uv[:, 1] - cv)
        return np.clip(1 - d / R, 0, 1) ** 1.3
    return f


def tear_damage(leaf):
    if leaf.tear is None:
        return None
    s, qt, vr = leaf.tear
    h = leaf.halves[s]
    c = [c for c in leaf.cuts[s] if c["torn"]][0]

    def f(uv, ed):
        u, v = uv[:, 0], uv[:, 1]
        m = (v * s) > 0
        out = np.zeros(len(u))
        q = h.q_of(u[m], np.abs(v[m]))
        near = np.abs(q - qt) * h.metric(q, np.abs(v[m]))[0] < 0.012
        far = np.abs(v[m]) > c["v_end"] - 0.004
        out[m] = (near & far) * np.exp(-ed[m] / 0.0025)
        return out
    return f


def petiole(name, S, d0, E, d1, L, rnd, mats, bow=0.0, r_base=0.012):
    """A petiole from the stem node S (leaving along d0) to the blade at E (arriving along d1): round,
    tapering, flared into a sheath where it clasps the stem, nearly straight but for a short swollen
    knee under the blade, where it turns the blade."""
    dist = (E - S).length
    D = (E - S).normalized()
    up = Vector((0, 0, 1))
    lift = (up - D * up.dot(D)) * bow * dist        # a long petiole bows upwards under its blade's weight
    path = bezier(S, S + d0 * 0.42 * dist + lift, E - d1 * 0.10 * dist + lift * 0.8, E, 90)
    t = np.linspace(0, 1, len(path))
    rb = 0.0066 * (L / 0.36) ** 0.6
    r = rb * (1 - 0.38 * t)
    # the sheathing base: as wide as the stem where it clasps it, narrowing over its first 15 cm
    sh_len = min(0.15 / dist, 0.3)
    r = np.maximum(r, rb + (r_base - rb) * np.clip(1 - t / sh_len, 0, 1) ** 1.6)
    r *= 1 + 0.16 * np.sin(np.pi * np.clip((t - 0.945) / 0.05, 0, 1))
    return capped_tube(name, path, r, [mats["petiole"]], attrs=dict(pt=t, rnd=np.full(len(t), rnd)))


def stems(mats, rng):
    obs = []
    for k, (_, _, r) in enumerate(STEMS):
        path = stem_path(k)
        t = np.linspace(0, 1, len(path))
        # nodes every 3 to 5 cm, each a slightly swollen ring of an old leaf scar
        z = path[:, 2]
        nodes = np.arange(pot.SOIL_Z + 0.01, z[-1], rng.uniform(0.03, 0.045))
        dn = np.min(np.abs(z[:, None] - nodes[None, :]), 1)
        scar = np.exp(-(dn / 0.004) ** 2)
        rad = r * (1 + 0.07 * scar) * (1 - 0.18 * t)
        # the top tapers away inside the sheathing bases of the youngest petioles
        rad *= 1 - 0.45 * np.clip((t - 0.88) / 0.12, 0, 1) ** 2
        ob = capped_tube(f"monstera stem {k}", path, rad, [mats["stem"]], attrs=dict(node=scar), sides=16)
        obs.append(ob)
    return obs


def stem_point(k, f):
    path = stem_path(k, 200)
    z0, z1 = pot.SOIL_Z, path[-1, 2]
    z = z0 + f * (z1 - z0)
    i = int(np.argmin(np.abs(path[:, 2] - z)))
    tang = path[min(i + 1, len(path) - 1)] - path[max(i - 1, 0)]
    return Vector(path[i]), Vector(tang).normalized()


def leaves(mats, rng):
    obs = []
    for i, spec in enumerate(LEAVES):
        lr = np.random.default_rng(1000 + 17 * i + SEED)
        leaf = ml.Leaf(spec["L"], lr, maturity=spec["mat"], width=lr.uniform(0.9, 1.03), tear=spec.get("tear", False))
        sp = shape_params(spec["tier"], lr)
        M = leaf_frame(spec)
        age = {"young": 0.15, "up": 0.6, "mid": 0.85, "low": 1.0}[spec["tier"]] * lr.uniform(0.85, 1.0)
        props = dict(age=age, tint=lr.uniform(0, 1), yel=1.0 if spec.get("yellow") else 0.0)
        ob, rib = leaf_object(f"monstera leaf {i}", leaf, sp, lr, M, mats, props,
                              yel=yellow_spot(leaf, lr) if spec.get("yellow") else None, dmg=tear_damage(leaf))
        obs += [ob, rib]
        # the petiole: from its node on the stem to under the blade's base, coming up into it from below
        R = M.to_3x3()
        T0, N0 = R.col[1], R.col[2]
        E = Vector(spec["base"]) - N0 * 0.004
        S, st = stem_point(spec["stem"], spec["node"])
        out = Vector((E.x - S.x, E.y - S.y, 0))
        out = out.normalized() if out.length > 1e-6 else Vector((1, 0, 0))
        S = S + out * STEMS[spec["stem"]][2] * 0.15 - st * 0.01
        D = (E - S).normalized()
        # it leaves the stem steeper than the straight line (the lower, longer ones arch outwards) and
        # reaches the blade already turning towards the midrib
        steep = {"young": 0.3, "up": 0.4, "mid": 0.7, "low": 1.1}[spec["tier"]]
        d0 = (D + st * steep * lr.uniform(0.8, 1.2)).normalized()
        d1 = (D * 0.6 + T0 * 0.4 - N0 * 0.15).normalized()
        bow = {"young": 0.01, "up": 0.02, "mid": 0.06, "low": 0.12}[spec["tier"]] * lr.uniform(0.7, 1.3)
        pet = petiole(f"monstera petiole {i}", S, d0, E, d1, spec["L"], lr.random(), mats, bow,
                      r_base=STEMS[spec["stem"]][2] * lr.uniform(0.6, 0.8))
        obs.append(pet)
        # where the leaf would swing from in a breeze (layers.py): its node on the stem, and the blade's base
        for o in (ob, rib, pet):
            o["sway_node"], o["sway_blade"], o["sway_tier"], o["sway_len"] = tuple(S), tuple(E), spec["tier"], spec["L"]
    return obs


def pot_parts(mats, rng):
    obs = []
    V, Q, uv = pot.lathe_mesh(pot.pot_profile())
    ob = mesh("monstera pot", V, [Q], uv=uv)
    ob.data.materials.append(mats["pot"])
    obs.append(ob)
    V, Q = pot.soil_mesh(rng)
    ob = mesh("monstera soil", V, [Q])
    ob.data.materials.append(mats["soil"])
    obs.append(ob)
    # mulch: bark chips and pebbles, each kind one mesh
    chipsV, chipsF, chipsR, chipsS = [], [], [], []
    pebV, pebF, pebR = [], [], []
    for kind, x, y, z, turn, (tx, ty), ln, w, t in pot.scatter(rng):
        Rm = np.array((Matrix.Rotation(turn, 3, "Z") @ Matrix.Rotation(tx, 3, "X") @ Matrix.Rotation(ty, 3, "Y")))
        if kind == "chip":
            V, F, (s0, s1) = pot.chip_mesh(rng, ln, w, t)
            V = V @ Rm.T + np.array([x, y, z - 0.25 * t])
            o = sum(len(v) for v in chipsV)
            chipsF += [np.array(f) + o for f in F]
            chipsV.append(V)
            chipsR.append(np.full(len(V), rng.random()))
            # the broken sides show the paler inner bark; flag their vertices
            sd = np.zeros(len(V))
            sd[s0:s1] = 1.0
            chipsS.append(sd)
        else:
            V, F = pot.pebble_mesh(rng, ln / 2)
            V = V @ Rm.T + np.array([x, y, z + 0.4 * ln / 2])
            o = sum(len(v) for v in pebV)
            pebF += [np.array(f) + o for f in F]
            pebV.append(V)
            pebR.append(np.full(len(V), rng.random()))
    V = np.vstack(chipsV)
    groups = {}
    for f in chipsF:
        groups.setdefault(len(f), []).append(f)
    ob = mesh("monstera bark chips", V, [np.array(g) for g in groups.values()],
              attrs=dict(rnd=np.concatenate(chipsR), side=np.concatenate(chipsS)), smooth=False)
    ob.data.materials.append(mats["chip"])
    obs.append(ob)
    V = np.vstack(pebV)
    ob = mesh("monstera pebbles", V, [np.array(pebF)], attrs=dict(rnd=np.concatenate(pebR)))
    ob.data.materials.append(mats["peb"])
    obs.append(ob)
    return obs


# Two aerial roots: one from the left stem arching out over the rim and hanging down the pot's side, its
# growing tip pale; one from the right stem curving down into the mulch. Control points of a Bezier.
ROOTS = [dict(stem=1, node=0.45, ctrl=((-0.105, -0.045, 0.505), (-0.15, -0.065, 0.45), (-0.143, -0.07, 0.34)),
              r=0.0042, tip=True),
         dict(stem=0, node=0.6, ctrl=((0.075, 0.045, 0.54), (0.095, 0.06, 0.46), (0.098, 0.062, 0.415)),
              r=0.0048, tip=False)]


def roots(mats, rng):
    obs = []
    for i, rt in enumerate(ROOTS):
        S, st = stem_point(rt["stem"], rt["node"])
        c1, c2, E = (Vector(c) for c in rt["ctrl"])
        path = bezier(S, c1, c2, E, 80)
        # a root is never smooth: small kinks and a slow wander
        ph = rng.uniform(0, 50, 3)
        t = np.linspace(0, 1, len(path))
        wob = np.stack([[mnoise.noise((x * 5 + ph[0], ph[1], ph[2])) for x in t],
                        [mnoise.noise((ph[0], x * 5 + ph[1], ph[2])) for x in t],
                        [mnoise.noise((ph[2], ph[1], x * 5 + ph[0])) for x in t]], 1)
        path = path + wob * 0.006 * np.sin(np.pi * t)[:, None]
        r = rt["r"] * (1 - 0.25 * t)
        if rt["tip"]:
            r = r * np.clip((1 - t) / 0.04, 0.35, 1) ** 0.5
        obs.append(capped_tube(f"monstera aerial root {i}", path, r, [mats["root"]], attrs=dict(pt=t), sides=10))
    return obs


def sheaths(mats, rng):
    """Dry sheaths (cataphylls) wrapped round each stem at a few old nodes: a curled papery sheet with a
    torn top edge, open on one side."""
    obs = []
    for k, ((bx, by), top, r) in enumerate(STEMS):
        for j in range(1):
            f = rng.uniform(0.1, 0.35)
            C, st = stem_point(k, f)
            H = rng.uniform(0.02, 0.04)
            a0 = rng.uniform(0, 2 * math.pi)
            span = rng.uniform(2.4, 3.6)
            na, nh = 48, 16
            A = a0 + np.linspace(-span / 2, span / 2, na)
            hh = np.linspace(0, 1, nh)
            ph = rng.uniform(0, 50)
            # a torn top edge, shorter at the free sides, which peel away from the stem
            rag = np.array([0.7 + 0.3 * mnoise.noise((a * 6 + ph, ph, 0.0)) + 0.1 * mnoise.noise((a * 25, ph, 1.0))
                            for a in A]) * (1 - 0.35 * np.abs(np.linspace(-1, 1, na)) ** 2)
            side = np.abs(np.linspace(-1, 1, na))
            V = []
            for h in hh:
                for a, rg, sd in zip(A, rag, side):
                    hz = h * H * rg
                    rad = r * (1.06 + 0.18 * h ** 2 * (0.3 + sd)) + 0.0005 * mnoise.noise((a * 5, h * 4, ph))
                    V.append((C.x + rad * math.cos(a), C.y + rad * math.sin(a), C.z - 0.01 + hz))
            V = np.array(V)
            i = np.arange(nh - 1)[:, None]
            c = np.arange(na - 1)[None, :]
            Q = np.stack([i * na + c, i * na + c + 1, (i + 1) * na + c + 1, (i + 1) * na + c], -1).reshape(-1, 4)
            uv = np.stack(np.meshgrid(np.linspace(0, span * r, na), hh * H), -1).reshape(-1, 2)
            ob = mesh(f"monstera sheath {k}.{j}", V, [Q], uv=uv,
                      attrs=dict(pt=np.repeat(hh, na), rnd=np.full(len(V), rng.random())))
            ob.data.materials.append(mats["sheath"])
            obs.append(ob)
    return obs


def build():
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    mats = materials()
    pot_parts(mats, rng)
    _log("pot", round(time.time() - t0, 1), "s")
    stems(mats, rng)
    sheaths(mats, rng)
    roots(mats, rng)
    leaves(mats, rng)
    _log("plant", round(time.time() - t0, 1), "s")
