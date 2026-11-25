# The capybara plush: a giant seated plush toy, 0.76 m tall, in caramel minky with chocolate velboa
# panels, bead eyes, an embroidered nose and a chunky knitted scarf.
import os, time
import bpy
import numpy as np
from objects import capybara_shape as shape
from objects import capybara_fur as fur
from objects import capybara_yarn as yarn
from objects import capybara_scarf as scarf

SEED = 11
# For quick tests: CAPY_FUR scales every strand count, CAPY_NOFUR=1 leaves the pile off.
DENSITY = float(os.environ.get("CAPY_FUR", "1.0"))


def _log(*a):
    print("capybara:", *a, flush=True)


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# ---------- colours (linear) ----------
CARAMEL_ROOT = (0.170, 0.055, 0.012)
CARAMEL = (0.420, 0.124, 0.026)
CARAMEL_TIP = (0.620, 0.278, 0.088)
COCOA = (0.120, 0.045, 0.021)


def _nodes(m):
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return nt, out


def skin_material():
    """The fabric under the pile: the backing of the minky (dark, like the pile's roots) and the
    velboa panels, chosen by the 'dark' attribute."""
    m = bpy.data.materials.new("capybara fabric")
    nt, out = _nodes(m)
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "dark"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*CARAMEL_ROOT, 1)
    mix.inputs["B"].default_value = (*COCOA, 1)
    nt.links.new(attr.outputs["Fac"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.85
    bs.inputs["Sheen Weight"].default_value = 0.6
    bs.inputs["Sheen Roughness"].default_value = 0.35
    bs.inputs["Sheen Tint"].default_value = (0.55, 0.40, 0.30, 1)
    # the velboa's pile seen end-on: a fine grain
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 900.0
    noise.inputs["Detail"].default_value = 4.0
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.0003
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    nt.links.new(bs.outputs[0], out.inputs["Surface"])
    return m


def hair_material(name, root, mid, tip, rough=0.32, radial=0.55, coat=0.0):
    """Polyester pile: a hair BSDF coloured from root to tip, each strand a little lighter or
    darker ('tone')."""
    m = bpy.data.materials.new(name)
    nt, out = _nodes(m)
    h = nt.nodes.new("ShaderNodeBsdfHairPrincipled")
    h.model = "CHIANG"
    h.parametrization = "COLOR"
    info = nt.nodes.new("ShaderNodeHairInfo")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*root, 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (*tip, 1)
    e = cr.elements.new(0.45)
    e.color = (*mid, 1)
    nt.links.new(info.outputs["Intercept"], ramp.inputs["Fac"])
    tone = nt.nodes.new("ShaderNodeAttribute")
    tone.attribute_name = "tone"
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], mul.inputs["A"])
    nt.links.new(tone.outputs["Color"], mul.inputs["B"])
    nt.links.new(mul.outputs["Result"], h.inputs["Color"])
    h.inputs["Roughness"].default_value = rough
    h.inputs["Radial Roughness"].default_value = radial
    h.inputs["Coat"].default_value = coat
    h.inputs["IOR"].default_value = 1.55
    h.inputs["Random Roughness"].default_value = 0.25
    nt.links.new(h.outputs[0], out.inputs["Surface"])
    return m


# ---------- the pile ----------
def _region_min(P):
    r = shape.regions(P)
    return np.minimum.reduce([r["muzzle"], r["paw"], r["sole"], r["ear_in"]]), r


def long_pile(verts, quads, rng, eyes, keepout=None):
    _, area = fur.sample_surface(verts, quads, 1, rng)
    n = int(area * 1e4 * 95 * DENSITY)       # strands per cm2
    P, _ = fur.sample_surface(verts, quads, n, rng)
    dmin, reg = _region_min(P)
    ok = dmin > 0.0008
    for e in eyes:
        ok &= np.linalg.norm(P - e, axis=1) > shape.EYE_R + 0.0012
    if keepout is not None:
        ok &= keepout.keep(P)
    P = P[ok]
    dmin = dmin[ok]
    reg = {k: v[ok] for k, v in reg.items()}
    N = shape.gradient(P)
    T = fur.tangents(P, N)
    _, w = shape.flow(P)
    n = len(P)
    # length by part: torso, head, arm, thigh, foot, ear
    L = w @ np.array([0.020, 0.0150, 0.016, 0.018, 0.013, 0.007])
    # shorter where the fur meets the velboa panels, as trimmed plush is around a muzzle
    L *= 0.45 + 0.55 * _smooth(dmin, 0.0, 0.03)
    de = np.min([np.linalg.norm(P - e, axis=1) for e in eyes], axis=0)
    L *= 0.35 + 0.65 * _smooth(de, shape.EYE_R + 0.002, shape.EYE_R + 0.03)
    L *= np.clip(1 + 0.09 * fur.waves(P, 3, 0.05) + 0.10 * rng.normal(size=n), 0.6, 1.5)
    # swirl the nap a little, coherently, as brushing leaves it
    T = fur.rotate_about(T, N, 0.22 * fur.waves(P, 5, 0.06))
    # a few stray fibres stand out longer, as on any real plush
    fly = rng.random(n) < 0.012
    L = np.where(fly, L * rng.uniform(1.3, 1.8, n), L)
    lift_root = np.radians(66 + 5 * fur.waves(P, 7, 0.04) + 6 * rng.normal(size=n))
    lift_tip = np.radians(26 + 5 * fur.waves(P, 8, 0.03) + 9 * rng.normal(size=n) + 25 * fly)
    # locks (about a centimetre) gather tufts (a few millimetres): both sway together
    locks = fur.worley(P, 0.014, seed=11)
    ids = fur.worley(P, 0.005, seed=1)
    lock_h = fur._hash3(np.stack([locks, locks * 3, locks * 7], 1), 4)
    tuft_h = fur._hash3(np.stack([ids, ids * 3, ids * 5], 1), 9)
    phase = lock_h[:, 0] * 2 * np.pi
    pts = fur.grow(P, N, T, L, 6, lift_root, lift_tip, rng, wave_amp=np.where(fly, 0.6, 0.42),
                   wave_freq=np.full(n, 0.8), wave_phase=phase + rng.normal(0, 0.35, n))
    pts = fur.clump(pts, locks, np.where(fly, 0.0, 0.28 + 0.25 * lock_h[:, 1]))
    pts = fur.clump(pts, ids, np.where(fly, 0.0, 0.50 + 0.38 * tuft_h[:, 0]))
    s = np.linspace(0, 1, 6)[None, :, None] ** 2
    pts += rng.normal(0, 1, pts.shape) * (0.05 * L)[:, None, None] * s
    clear = 0.0006 + 0.12 * L[:, None] * np.linspace(0, 1, 6)[None]
    pts = fur.collide(pts, clear)
    if keepout is not None:
        pts = keepout.push(pts)
        pts = fur.collide(pts, clear, iters=1)
    tone = np.clip(1 + 0.09 * rng.normal(size=n) + 0.07 * fur.waves(P, 13, 0.09)
                   + 0.12 * (lock_h[:, 2] - 0.5), 0.7, 1.3)
    r0 = np.full(n, 0.00011)
    return pts, r0, r0 * 0.35, tone


def short_pile(verts, quads, rng):
    _, area = fur.sample_surface(verts, quads, 1, rng)
    n = int(area * 1e4 * 320 * DENSITY)
    P, _ = fur.sample_surface(verts, quads, n, rng)
    dmin, _ = _region_min(P)
    P = P[dmin < -0.0004]
    P = P[shape.stitch_distance(P) > 0.0014]
    P = P[shape.stitch_distance(P, shape.NOSTRILS) > shape.NOSTRIL_W * 0.5 + 0.0006]
    n = len(P)
    N = shape.gradient(P)
    T = fur.tangents(P, N)
    T = fur.rotate_about(T, N, 0.6 * fur.waves(P, 21, 0.02))
    L = 0.0030 * np.clip(1 + 0.15 * rng.normal(size=n), 0.6, 1.4)
    lift_root = np.radians(np.full(n, 76.0))
    lift_tip = np.radians(50 + 12 * rng.normal(size=n))
    pts = fur.grow(P, N, T, L, 4, lift_root, lift_tip, rng, wave_amp=np.full(n, 0.2),
                   wave_freq=np.full(n, 0.5))
    ids = fur.worley(P, 0.0016, seed=4)
    pts = fur.clump(pts, ids, np.full(n, 0.15))
    tone = np.clip(1 + 0.12 * rng.normal(size=n), 0.7, 1.3)
    r0 = np.full(n, 0.00005)
    return pts, r0, r0 * 0.5, tone


# ---------- the scarf ----------
WOOL = (0.100, 0.037, 0.014)
WOOL_LIGHT = (0.190, 0.085, 0.036)


def wool_material():
    """Chocolate wool, heathered: two plies twisting round each other (drawn from the tube's UVs:
    u along in metres, v around), lighter flecks, a soft sheen."""
    m = bpy.data.materials.new("capybara wool")
    nt, out = _nodes(m)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tone = nt.nodes.new("ShaderNodeAttribute")
    tone.attribute_name = "tone"
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 1400.0
    noise.inputs["Detail"].default_value = 3.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (*WOOL, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*WOOL_LIGHT, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    mul = nt.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    nt.links.new(ramp.outputs["Color"], mul.inputs["A"])
    nt.links.new(tone.outputs["Color"], mul.inputs["B"])
    nt.links.new(mul.outputs["Result"], p.inputs["Base Color"])
    p.inputs["Roughness"].default_value = 0.82
    p.inputs["Sheen Weight"].default_value = 0.45
    p.inputs["Sheen Roughness"].default_value = 0.5
    p.inputs["Sheen Tint"].default_value = (0.85, 0.55, 0.38, 1)
    # the ply twist
    uvn = nt.nodes.new("ShaderNodeUVMap")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uvn.outputs["UV"], sep.inputs[0])
    a = nt.nodes.new("ShaderNodeMath")
    a.operation = "MULTIPLY"
    a.inputs[1].default_value = 1.0 / 0.0075
    nt.links.new(sep.outputs["X"], a.inputs[0])
    b = nt.nodes.new("ShaderNodeMath")
    b.operation = "MULTIPLY_ADD"
    b.inputs[1].default_value = 2.0
    nt.links.new(sep.outputs["Y"], b.inputs[0])
    nt.links.new(a.outputs[0], b.inputs[2])
    c = nt.nodes.new("ShaderNodeMath")
    c.operation = "MULTIPLY"
    c.inputs[1].default_value = np.pi
    nt.links.new(b.outputs[0], c.inputs[0])
    sn = nt.nodes.new("ShaderNodeMath")
    sn.operation = "SINE"
    nt.links.new(c.outputs[0], sn.inputs[0])
    ab = nt.nodes.new("ShaderNodeMath")
    ab.operation = "ABSOLUTE"
    nt.links.new(sn.outputs[0], ab.inputs[0])
    pw = nt.nodes.new("ShaderNodeMath")
    pw.operation = "POWER"
    pw.inputs[1].default_value = 0.6
    nt.links.new(ab.outputs[0], pw.inputs[0])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.9
    bump.inputs["Distance"].default_value = 0.0007
    nt.links.new(pw.outputs[0], bump.inputs["Height"])
    nb = nt.nodes.new("ShaderNodeBump")
    nb.inputs["Strength"].default_value = 0.25
    nb.inputs["Distance"].default_value = 0.0002
    nt.links.new(noise.outputs["Fac"], nb.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], nb.inputs["Normal"])
    nt.links.new(nb.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    return m


def build_scarf(rng):
    t = time.time()
    sc = scarf.make(rng)
    _log("scarf cloth", round(time.time() - t, 1), "s")
    wool = wool_material()
    obs = []
    g = sc["grains"]
    K = g.shape[1]
    u = np.linspace(0, 1, K)
    radii = np.tile(scarf.RY * (0.78 + 0.22 * np.sin(np.pi * u)), (len(g), 1))
    v, f, uv = yarn.tubes(g, radii, sides=8, phase=rng.uniform(0, 6.3, len(g)))
    faces_per = (K - 1) * 8
    ob = yarn.mesh_object("capybara scarf knit", v, f, uv, {"tone": ("FACE", np.repeat(sc["tones"], faces_per))})
    ob.data.materials.append(wool)
    obs.append(ob)
    # the fringe, grouped by point count
    fp, fr = sc["fringe"]
    for k in sorted({len(p) for p in fp}):
        P = np.array([p for p in fp if len(p) == k])
        R = np.array([r for p, r in zip(fp, fr) if len(p) == k])
        v, f, uv = yarn.tubes(P, R, sides=10, phase=rng.uniform(0, 6.3, len(P)))
        tn = np.clip(1 + 0.08 * rng.normal(size=len(P)), 0.8, 1.2)
        ob = yarn.mesh_object("capybara scarf fringe", v, f, uv, {"tone": ("FACE", np.repeat(tn, (k - 1) * 10))})
        ob.data.materials.append(wool)
        obs.append(ob)
    back = bpy.data.materials.new("capybara wool backing")
    nt, out = _nodes(back)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.060, 0.023, 0.009, 1)
    p.inputs["Roughness"].default_value = 0.9
    p.inputs["Sheen Weight"].default_value = 0.2
    p.inputs["Sheen Tint"].default_value = (0.8, 0.5, 0.35, 1)
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 400.0
    bmp = nt.nodes.new("ShaderNodeBump")
    bmp.inputs["Strength"].default_value = 0.5
    nt.links.new(nz.outputs["Fac"], bmp.inputs["Height"])
    nt.links.new(bmp.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    for verts, quads in sc["backs"]:
        ob = yarn.mesh_object("capybara scarf backing", verts, quads)
        ob.data.materials.append(back)
        obs.append(ob)
    # the woolly halo
    fz = scarf.fuzz(g, radii, rng, per=int(16 * DENSITY) + 1)
    m = hair_material("capybara wool fuzz", (0.07, 0.027, 0.011), (0.12, 0.050, 0.022), (0.20, 0.100, 0.050),
                      rough=0.45, radial=0.7)
    n = len(fz)
    ob = fur.curves_object("capybara scarf fuzz", fz, np.full(n, 0.00004), np.full(n, 0.00002), m,
                           {"tone": np.clip(1 + 0.15 * rng.normal(size=n), 0.6, 1.4)})
    obs.append(ob)
    _log("scarf", len(g), "grains,", n, "fuzz fibres", round(time.time() - t, 1), "s")
    return obs, sc["keepout"]


# ---------- the face ----------
def surface_hit(origins, dirs, tmax=0.25, steps=100):
    """Where rays from outside first meet the stuffed shape (bisection after a coarse march)."""
    n = len(origins)
    ts = np.linspace(0, tmax, steps)
    prev = np.zeros(n)
    hit_lo, hit_hi = np.zeros(n), np.full(n, tmax)
    found = np.zeros(n, bool)
    for t in ts[1:]:
        d = shape.sdf(origins + dirs * t)
        new = (d < 0) & ~found
        hit_lo[new], hit_hi[new] = prev[new], t
        found |= new
        prev[:] = t
    for _ in range(24):
        mid = (hit_lo + hit_hi) / 2
        d = shape.sdf(origins + dirs * mid[:, None])
        hit_hi = np.where(d < 0, mid, hit_hi)
        hit_lo = np.where(d < 0, hit_lo, mid)
    return origins + dirs * ((hit_lo + hit_hi) / 2)[:, None]


def eye_beads():
    """Centres and outward normals of the two safety-eye beads, set two-fifths into their dents."""
    e = shape.head_world(np.array([shape.EYE, shape.EYE * (-1, 1, 1)]))
    g = shape.gradient(e)
    hit = surface_hit(e + g * 0.05, -g, 0.1)
    n = shape.gradient(hit)
    return hit + n * shape.EYE_R * 0.38, n


def eyes(centres):
    m = bpy.data.materials.new("capybara eye")
    nt, out = _nodes(m)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.006, 0.004, 0.003, 1)
    p.inputs["Roughness"].default_value = 0.06
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.03
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    obs = []
    for c in centres:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=shape.EYE_R, location=tuple(c), segments=48, ring_count=24)
        ob = bpy.context.active_object
        ob.name = "capybara eye"
        ob.data.materials.append(m)
        bpy.ops.object.shade_smooth()
        obs.append(ob)
    return obs


def _resample(poly, step):
    poly = np.asarray(poly, float)
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(np.ceil(s[-1] / step)), 2)
    t = np.linspace(0, s[-1], n + 1)
    return np.stack([np.interp(t, s, poly[:, i]) for i in range(poly.shape[1])], 1), t


def embroidery():
    """The nose and mouth in stem stitch: short stitches of dark floss, each starting halfway along
    the last, sunk into the velboa along the grooves the shape has for them."""
    R = shape.HEAD_R @ shape.MUZZLE_R
    fwd = R @ np.array([0.0, 1.0, 0.0])
    paths, radii = [], []
    rng = np.random.default_rng(5)
    for pi, poly in enumerate(shape.STITCH_PATHS):
        satin = pi < len(shape.NOSTRILS)
        xz, s = _resample(poly, 0.0004)
        local = np.stack([xz[:, 0], np.full(len(xz), -0.17), xz[:, 1]], 1)
        org = shape.head_world(shape.MUZZLE_C + local @ shape.MUZZLE_R.T)
        surf = surface_hit(org, np.tile(fwd, (len(org), 1)), 0.2)
        nrm = shape.gradient(surf)
        L = s[-1]
        if satin:
            # satin stitch: floss laid side by side across the slit, wider in its middle
            tan = np.gradient(surf, axis=0)
            tan /= np.linalg.norm(tan, axis=1, keepdims=True)
            side = np.cross(nrm, tan)
            for k in range(0, len(s), 1):
                u = s[k] / L
                w = shape.NOSTRIL_W * (0.35 + 0.65 * np.sin(np.pi * np.clip(u, 0.02, 0.98)) ** 0.6)
                c = np.linspace(-1, 1, 9)
                P = surf[k] + side[k] * (w / 2) * c[:, None] + nrm[k] * (0.0005 + 0.0007 * (1 - c ** 2))[:, None]
                P = P + tan[k] * rng.normal(0, 0.00008) + rng.normal(0, 0.00003, P.shape)
                paths.append(P)
                radii.append(np.full(9, 0.00042))
            continue
        stitch, step = 0.0042, 0.0021
        starts = np.arange(0, max(L - stitch * 0.6, 1e-4), step)
        for s0 in starts:
            s1 = min(s0 + stitch, L)
            t = np.linspace(s0, s1, 9)
            P = np.stack([np.interp(t, s, surf[:, i]) for i in range(3)], 1)
            Nn = np.stack([np.interp(t, s, nrm[:, i]) for i in range(3)], 1)
            Nn /= np.linalg.norm(Nn, axis=1, keepdims=True)
            tan = P[-1] - P[0]
            tan /= max(np.linalg.norm(tan), 1e-9)
            side = np.cross(Nn, tan)
            u = np.linspace(0, 1, 9)
            lift = 0.00025 + 0.00045 * np.sin(np.pi * u)
            lean = 0.00022 * (1 - 2 * u)              # stem stitch: each stitch leans across the line
            P = P + Nn * lift[:, None] + side * lean[:, None] + rng.normal(0, 0.00004, P.shape)
            paths.append(P)
            radii.append(0.00062 * (0.75 + 0.25 * np.sin(np.pi * u)))
    v, f, uv = yarn.tubes(np.array(paths), np.array(radii), sides=8)
    ob = yarn.mesh_object("capybara embroidery", v, f, uv)
    m = bpy.data.materials.new("capybara floss")
    nt, out = _nodes(m)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.inputs["Base Color"].default_value = (0.018, 0.007, 0.004, 1)
    p.inputs["Roughness"].default_value = 0.45
    p.inputs["Sheen Weight"].default_value = 0.6
    p.inputs["Sheen Tint"].default_value = (0.6, 0.45, 0.35, 1)
    # the floss's six strands twist along the stitch
    uvn = nt.nodes.new("ShaderNodeUVMap")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uvn.outputs["UV"], sep.inputs[0])
    mth = nt.nodes.new("ShaderNodeMath")
    mth.operation = "MULTIPLY_ADD"
    mth.inputs[1].default_value = 1200.0
    nt.links.new(sep.outputs["X"], mth.inputs[0])
    nt.links.new(sep.outputs["Y"], mth.inputs[2])
    mth2 = nt.nodes.new("ShaderNodeMath")
    mth2.operation = "MULTIPLY"
    mth2.inputs[1].default_value = 3.0
    nt.links.new(mth.outputs[0], mth2.inputs[0])
    sine = nt.nodes.new("ShaderNodeMath")
    sine.operation = "SINE"
    nt.links.new(mth2.outputs[0], sine.inputs[0])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(sine.outputs[0], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], p.inputs["Normal"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    ob.data.materials.append(m)
    return ob


def build():
    rng = np.random.default_rng(SEED)
    t = time.time()
    v, q = shape.mesh()
    _log("shape", len(v), "verts", round(time.time() - t, 1), "s")
    dmin, _ = _region_min(v)
    body = yarn.mesh_object("capybara body", v, q, attrs={"dark": ("POINT", _smooth(-dmin, -0.0006, 0.0006))})
    body.data.materials.append(skin_material())

    t = time.time()
    centres, _ = eye_beads()
    for ob in eyes(centres):
        ob.parent = body
    embroidery().parent = body
    sobs, keepout = build_scarf(rng)
    for ob in sobs:
        ob.parent = body
    if os.environ.get("CAPY_NOFUR"):
        return
    t = time.time()
    pts, r0, r1, tone = long_pile(v, q, rng, centres, keepout)
    m = hair_material("capybara minky", CARAMEL_ROOT, CARAMEL, CARAMEL_TIP)
    pile = fur.curves_object("capybara pile", pts, r0, r1, m, {"tone": tone})
    pile.parent = body
    _log("long pile", len(pts), "strands", round(time.time() - t, 1), "s")

    t = time.time()
    pts, r0, r1, tone = short_pile(v, q, rng)
    m = hair_material("capybara velboa", (0.050, 0.018, 0.009), COCOA, (0.21, 0.100, 0.056), rough=0.28)
    vel = fur.curves_object("capybara velboa", pts, r0, r1, m, {"tone": tone})
    vel.parent = body
    _log("short pile", len(pts), "strands", round(time.time() - t, 1), "s")
