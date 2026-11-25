# The monstera's materials: the leaf blades (a single surface shaded as either face by which side the ray
# meets, glossy over a diffuse green with diffuse translucency added, so backlit leaves glow; its edge
# band; the raised midrib underneath), petioles and stems, dry sheaths, aerial roots, the matte black
# pot, the soil, bark chips and pebbles. Colours are linear.
#
# The blade shader reads what monstera_leaf.blade() stores on each vertex: vp (the vein phase, an
# integer on each primary lateral vein), vm (metres across the veins per unit of phase), lv and lu (the
# distance from the midrib in metres and the position along it, 0 to 1), ed (metres to the nearest edge),
# seg (a random number per strap), and per leaf the object properties "age" (0 young, 1 old), "tint" and
# "yel" spots; UVs are the flat leaf's own (u, v) in metres, so the vein lines stay sharp at any distance.
import bpy
from objects.conga_nodes import (tree, node, wire, math, add, mul, mad, mix, mixf, vec, xyz, combine, noise, ramp, bump,
                                 attr, objpos, principled)


def remap(nt, v, a0, a1, b0=0.0, b1=1.0, smooth=False, clamp=True):
    """Map Range whose bounds may be sockets as well as numbers."""
    n = nt.nodes.new("ShaderNodeMapRange")
    n.interpolation_type = "SMOOTHSTEP" if smooth else "LINEAR"
    n.clamp = clamp
    for k, x in (("Value", v), ("From Min", a0), ("From Max", a1), ("To Min", b0), ("To Max", b1)):
        wire(nt, n.inputs[k], x)
    return n.outputs[0]


def obj_attr(nt, name):
    return node(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name=name).outputs["Fac"]


def line(nt, dist, width, soft):
    """1 on a line of half-width `width` (metres), falling to 0 over `soft` beyond it."""
    return remap(nt, dist, width, add(nt, width, soft), 1.0, 0.0, smooth=True)


def vein_dist(nt, phase, scale, every=1.0):
    """Metres to the nearest line of the vein family at integer multiples of `every` in phase."""
    p = mul(nt, phase, 1.0 / every)
    fr = math(nt, "ABSOLUTE", math(nt, "SUBTRACT", p, math(nt, "ROUND", p)))
    return mul(nt, mul(nt, fr, every), scale)


def leaf():
    m, nt, o = tree("monstera leaf")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    uu, vv, _ = xyz(nt, uvn)
    vp, vm, lv, lu, ed, seg = (attr(nt, k) for k in ("vp", "vm", "lv", "lu", "ed", "seg"))
    age, tint, yel_amt = obj_attr(nt, "age"), obj_attr(nt, "tint"), obj_attr(nt, "yel")
    back = node(nt, "ShaderNodeNewGeometry").outputs["Backfacing"]
    p3 = combine(nt, uu, vv, mul(nt, tint, 7.0))      # the flat leaf's space, a different slice per leaf

    # ---- veins ----
    # primary laterals: about 1.4 mm wide near the midrib, thinning outwards
    taper = remap(nt, lv, 0.0, 0.16, 1.0, 0.45)
    d1 = vein_dist(nt, vp, vm)
    w1 = mul(nt, taper, 0.00055)
    v1 = line(nt, d1, w1, 0.00045)
    v1h = line(nt, d1, mul(nt, w1, 1.6), 0.0012)      # the broader shoulder the vein sits in
    # interprimary veins, halfway between, fainter
    d2 = vein_dist(nt, add(nt, vp, 0.5), vm)
    v2 = mul(nt, line(nt, d2, mul(nt, taper, 0.00025), 0.0003), 0.55)
    # the many fine parallel veins between
    d3 = vein_dist(nt, vp, vm, 1.0 / 11.0)
    v3 = line(nt, d3, 0.00010, 0.00016)
    # the midrib: a broad pale band near the base, narrowing to the tip
    wm = remap(nt, lu, 0.0, 1.0, 0.0034, 0.0005)
    mid = line(nt, lv, wm, 0.0007)
    midsh = line(nt, lv, mul(nt, wm, 2.4), 0.003)
    # the edge: a thin paler rim and the collective vein just inside it
    rim = line(nt, ed, 0.0002, 0.0004)
    coll = line(nt, math(nt, "ABSOLUTE", add(nt, ed, -0.0021)), 0.00018, 0.00025)

    # ---- colour ----
    # mature leaves a deep, slightly blue green; the youngest a fresher, yellower, lighter green
    base_top = mix(nt, remap(nt, age, 0.0, 1.0, 1.0, 0.0), (0.008, 0.030, 0.006), (0.028, 0.080, 0.012))
    # broad mottling and per-strap variation, as the light green of new growth or slight unevenness
    n_big = noise(nt, p3, 9.0, 3.0, 0.55).outputs[0]
    n_mid = noise(nt, p3, 60.0, 3.0, 0.6).outputs[0]
    mott = add(nt, mul(nt, add(nt, n_big, -0.5), 0.55), mul(nt, add(nt, n_mid, -0.5), 0.25))
    hsv = node(nt, "ShaderNodeHueSaturation", {"Color": base_top, "Hue": add(nt, 0.5, mul(nt, add(nt, seg, -0.5), 0.012)),
                                                "Saturation": 1.0, "Value": add(nt, 1.0, add(nt, mott, mul(nt, add(nt, seg, -0.5), 0.12)))})
    top = hsv.outputs[0]
    # a touch lighter along the midrib, deeper towards the margins
    top = mix(nt, mul(nt, remap(nt, lv, 0.0, 0.06, 1.0, 0.0, smooth=True), 0.25), top, (0.03, 0.075, 0.014))
    top = mix(nt, mul(nt, remap(nt, ed, 0.03, 0.0), 0.2), top, (0.008, 0.03, 0.007))
    # the veins paler and yellower than the blade
    vein_c = (0.06, 0.11, 0.024)
    top = mix(nt, mul(nt, v1, 0.6), top, vein_c)
    top = mix(nt, mul(nt, v2, 0.25), top, vein_c)
    top = mix(nt, mul(nt, v3, 0.05), top, vein_c)
    top = mix(nt, mul(nt, midsh, 0.25), top, (0.04, 0.08, 0.016))
    top = mix(nt, mul(nt, mid, 0.9), top, (0.14, 0.20, 0.04))
    top = mix(nt, mul(nt, rim, 0.35), top, (0.09, 0.13, 0.028))
    top = mix(nt, mul(nt, coll, 0.25), top, vein_c)

    # underside: paler and greyer, the veins raised and lighter still
    bot = mix(nt, remap(nt, age, 0.0, 1.0, 1.0, 0.0), (0.050, 0.095, 0.030), (0.075, 0.14, 0.035))
    bot = node(nt, "ShaderNodeHueSaturation", {"Color": bot, "Value": add(nt, 1.0, mul(nt, mott, 0.6))}).outputs[0]
    bot = mix(nt, mul(nt, v1, 0.8), bot, (0.11, 0.18, 0.05))
    bot = mix(nt, mul(nt, v2, 0.5), bot, (0.10, 0.17, 0.05))
    bot = mix(nt, mul(nt, v3, 0.25), bot, (0.10, 0.17, 0.05))
    bot = mix(nt, mul(nt, mid, 0.9), bot, (0.16, 0.22, 0.06))

    # yellowing (an old leaf's tip or a strap going) and the brown of a dried tear, from attributes
    yel = attr(nt, "yel")
    dmg = attr(nt, "dmg")
    edge_n = noise(nt, p3, 140.0, 4.0, 0.6).outputs[0]
    ys = add(nt, mul(nt, yel, yel_amt), mul(nt, add(nt, n_mid, -0.5), 0.25))
    ym = remap(nt, add(nt, ys, mul(nt, add(nt, edge_n, -0.5), 0.22)), 0.18, 0.42, smooth=True)
    yc = ramp(nt, remap(nt, ys, 0.1, 1.0),
              [(0.0, (0.055, 0.09, 0.016)), (0.35, (0.14, 0.15, 0.025)), (0.7, (0.30, 0.24, 0.04)),
               (0.9, (0.24, 0.15, 0.04)), (1.0, (0.12, 0.065, 0.02))])
    top = mix(nt, ym, top, yc)
    bot = mix(nt, ym, bot, yc)
    dm = remap(nt, add(nt, dmg, mul(nt, add(nt, edge_n, -0.5), 0.5)), 0.35, 0.7, smooth=True)
    # an old leaf's margin browns in places, in a hairline
    edge_patch = remap(nt, noise(nt, p3, 11.0, 3.0, 0.6).outputs[0], 0.55, 0.68)
    burn = mul(nt, mul(nt, line(nt, ed, 0.0003, 0.0006), edge_patch), remap(nt, age, 0.8, 1.0))
    dm = math(nt, "MAXIMUM", dm, burn)
    # where it has yellowed furthest the margin has dried to a crisp brown rim
    crisp = mul(nt, remap(nt, ys, 0.55, 0.8), line(nt, ed, add(nt, 0.0008, mul(nt, edge_n, 0.002)), 0.0008))
    dm = math(nt, "MAXIMUM", dm, crisp)
    # a few tiny dead spots, more on old leaves
    vor = node(nt, "ShaderNodeTexVoronoi", {"Vector": p3, "Scale": 55.0, "Randomness": 1.0})
    pick = xyz(nt, vor.outputs["Color"])[0]
    spots = mul(nt, line(nt, mul(nt, vor.outputs["Distance"], 1.0 / 55.0), 0.00035, 0.0003),
                remap(nt, pick, add(nt, 0.985, mul(nt, age, -0.03)), 1.0, 0.0, 1.0))
    dm = math(nt, "MAXIMUM", dm, mul(nt, spots, 0.9))
    dry = (0.10, 0.055, 0.016)
    top = mix(nt, dm, top, dry)
    bot = mix(nt, dm, bot, dry)
    col = mix(nt, back, top, bot)

    # ---- surface ----
    # a waxy cuticle: glossy on top, uneven in patches (dust, wiping, age); the underside matte
    rpatch = noise(nt, p3, 14.0, 3.0, 0.6).outputs[0]
    r_top = add(nt, 0.2, mul(nt, remap(nt, rpatch, 0.35, 0.7), 0.12))
    r_top = add(nt, r_top, mul(nt, age, 0.06))
    r_top = add(nt, r_top, mul(nt, ym, 0.25))
    gloss = noise(nt, p3, 4.5, 4.0, 0.6).outputs[0]
    r_top = add(nt, r_top, mul(nt, remap(nt, gloss, 0.35, 0.75, -0.06, 0.14), 1.0))
    rough = mixf(nt, back, r_top, 0.58)

    # relief: veins impressed on top and raised underneath, a slight pucker between primaries, a fine
    # cellular texture of the epidermis
    relief = add(nt, mul(nt, v1h, -0.5), mul(nt, v1, -0.2))
    relief = add(nt, relief, mul(nt, v2, -0.2))
    relief = add(nt, relief, mul(nt, v3, -0.04))
    relief = add(nt, relief, mul(nt, mid, 0.5))
    relief = add(nt, relief, mul(nt, midsh, -0.5))
    relief = add(nt, relief, mul(nt, coll, -0.2))
    # the blade bulges a little between primary veins, so reflections ripple along them
    fr = math(nt, "FRACT", vp)
    pucker = mul(nt, add(nt, 0.5, mul(nt, math(nt, "COSINE", mul(nt, fr, 6.2832)), -0.5)), remap(nt, lv, 0.004, 0.03))
    cells = node(nt, "ShaderNodeTexVoronoi", {"Vector": p3, "Scale": 2600.0}, feature="DISTANCE_TO_EDGE").outputs["Distance"]
    rel_top = relief
    rel_bot = mul(nt, relief, -1.4)
    rel = mixf(nt, back, rel_top, rel_bot)
    nrm = bump(nt, rel, 1.0, 0.00025)
    nrm = bump(nt, mixf(nt, back, pucker, mul(nt, pucker, -0.5)), 1.0, mul(nt, vm, 0.05), nrm)
    nrm = bump(nt, remap(nt, cells, 0.0, 0.08), 0.06, 0.00003, nrm)
    nrm = bump(nt, n_mid, 0.25, 0.0005, nrm)

    bsdf = principled(nt, Base_Color=col, Roughness=rough, Normal=nrm, Specular_IOR_Level=0.38)
    # light through the blade: a yellower green than either face, the veins and the midrib paler, a
    # yellowing patch glowing gold and the dry tear dark
    tc = mix(nt, remap(nt, age, 0.0, 1.0, 1.0, 0.0), (0.018, 0.048, 0.006), (0.05, 0.11, 0.014))
    tc = node(nt, "ShaderNodeHueSaturation", {"Color": tc, "Value": add(nt, 1.0, mul(nt, mott, 0.8))}).outputs[0]
    tc = mix(nt, mul(nt, add(nt, v1, mul(nt, v2, 0.5)), 0.5), tc, (0.10, 0.17, 0.03))
    tc = mix(nt, mid, tc, (0.07, 0.10, 0.025))
    tc = mix(nt, ym, tc, mul(nt, yc, 0.8))
    tc = mix(nt, dm, tc, (0.02, 0.01, 0.003))
    tr = node(nt, "ShaderNodeBsdfTranslucent", {"Color": tc, "Normal": nrm})
    both = node(nt, "ShaderNodeAddShader", {0: bsdf.outputs[0], 1: tr.outputs[0]})
    # seen from a diffuse bounce (the floor, the pot) the blade is matte: no caustics from its gloss,
    # which the shadow-catcher floor would show as dark specks
    matte = node(nt, "ShaderNodeAddShader", {0: node(nt, "ShaderNodeBsdfDiffuse", {"Color": col, "Normal": nrm}).outputs[0],
                                              1: tr.outputs[0]})
    lp = node(nt, "ShaderNodeLightPath")
    out = node(nt, "ShaderNodeMixShader", {0: lp.outputs["Is Diffuse Ray"], 1: both.outputs[0], 2: matte.outputs[0]})
    nt.links.new(out.outputs[0], o.inputs["Surface"])
    return m


def leaf_edge():
    """The blade's cut edge, about half a millimetre: paler, matte, translucent."""
    m, nt, o = tree("monstera leaf edge")
    dmg = attr(nt, "dmg")
    col = mix(nt, remap(nt, dmg, 0.3, 0.7), (0.045, 0.085, 0.017), (0.10, 0.06, 0.018))
    bsdf = principled(nt, Base_Color=col, Roughness=0.6, Specular_IOR_Level=0.3)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def midrib():
    """The midrib raised under the blade: pale green, faintly ridged along its length."""
    m, nt, o = tree("monstera midrib")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    a, b, _ = xyz(nt, uvn)
    p = combine(nt, mul(nt, a, 8.0), mul(nt, b, 900.0), 0.0)
    st = noise(nt, p, 1.0, 3.0, 0.6).outputs[0]
    col = mix(nt, mul(nt, st, 0.3), (0.075, 0.14, 0.035), (0.11, 0.17, 0.045))
    nrm = bump(nt, st, 0.2, 0.0003)
    bsdf = principled(nt, Base_Color=col, Roughness=0.42, Normal=nrm, Subsurface_Weight=0.25, Thin_Wall=True,
                      Coat_Weight=0.2, Coat_Roughness=0.25)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def pot():
    """Matte black planter: a fine-grained matte finish, the sheen a little uneven, faint dust on the
    lip and a little soil rubbed onto the inside of the rim."""
    m, nt, o = tree("monstera pot")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    nz = xyz(nt, node(nt, "ShaderNodeNewGeometry").outputs["Normal"])[2]
    grain = noise(nt, p, 2400.0, 2.0, 0.5).outputs[0]
    blot = noise(nt, p, 9.0, 3.0, 0.6).outputs[0]
    smear = noise(nt, vec(nt, "MULTIPLY", p, (1.0, 1.0, 0.25)), 22.0, 3.0, 0.6).outputs[0]
    col = mix(nt, mul(nt, remap(nt, blot, 0.3, 0.7), 0.5), (0.011, 0.011, 0.012), (0.017, 0.017, 0.018))
    # dust settles on the lip's upward face
    up = remap(nt, nz, 0.6, 0.95)
    lip = remap(nt, z, 0.438, 0.446)
    dust = mul(nt, mul(nt, up, lip), remap(nt, noise(nt, p, 180.0, 3.0, 0.6).outputs[0], 0.35, 0.75, 0.15, 0.45))
    col = mix(nt, dust, col, (0.09, 0.085, 0.08))
    # soil rubbed on the inside of the rim
    rr = vec(nt, "LENGTH", combine(nt, x, y, 0.0))
    inside = mul(nt, remap(nt, rr, 0.1245, 0.1225), remap(nt, z, 0.44, 0.425))
    col = mix(nt, mul(nt, inside, 0.7), col, (0.03, 0.02, 0.012))
    rough = add(nt, 0.52, mul(nt, remap(nt, smear, 0.3, 0.7), 0.16))
    rough = add(nt, rough, mul(nt, dust, 0.3))
    nrm = bump(nt, grain, 0.12, 0.00004)
    nrm = bump(nt, blot, 0.03, 0.002, nrm)
    bsdf = principled(nt, Base_Color=col, Roughness=rough, Normal=nrm, Specular_IOR_Level=0.45)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def soil():
    m, nt, o = tree("monstera soil")
    p = objpos(nt)
    n1 = noise(nt, p, 300.0, 4.0, 0.7).outputs[0]
    n2 = noise(nt, p, 40.0, 3.0, 0.6).outputs[0]
    col = mix(nt, remap(nt, n2, 0.3, 0.7), (0.014, 0.009, 0.006), (0.035, 0.022, 0.013))
    perl = node(nt, "ShaderNodeTexVoronoi", {"Vector": p, "Scale": 900.0}).outputs["Distance"]
    col = mix(nt, mul(nt, remap(nt, perl, 0.06, 0.0), 0.8), col, (0.35, 0.33, 0.30))   # perlite specks
    nrm = bump(nt, n1, 0.6, 0.0015)
    bsdf = principled(nt, Base_Color=col, Roughness=0.92, Normal=nrm)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def bark_chip():
    """Pine bark: the outer face in dark reddish-brown plates split by fissures and flaking in layers, the
    broken sides the paler, fibrous inner bark; every chip its own shade (vertex attribute 'rnd')."""
    m, nt, o = tree("monstera bark chips")
    p = objpos(nt)
    rnd = attr(nt, "rnd")
    side = attr(nt, "side")
    q = add(nt, p, mul(nt, rnd, 13.0))
    fib = noise(nt, vec(nt, "MULTIPLY", q, (1.0, 6.0, 1.0)), 420.0, 5.0, 0.7).outputs[0]
    plates = node(nt, "ShaderNodeTexVoronoi", {"Vector": q, "Scale": 220.0}, feature="DISTANCE_TO_EDGE").outputs["Distance"]
    n = noise(nt, q, 120.0, 5.0, 0.65).outputs[0]
    outer = ramp(nt, add(nt, mul(nt, n, 0.7), mul(nt, rnd, 0.45)),
                 [(0.0, (0.018, 0.008, 0.004)), (0.45, (0.045, 0.019, 0.009)), (0.75, (0.085, 0.036, 0.016)), (1.0, (0.13, 0.06, 0.028))])
    fissure = remap(nt, plates, 0.06, 0.0)
    outer = mix(nt, mul(nt, fissure, 0.8), outer, (0.012, 0.006, 0.003))
    inner = mix(nt, fib, (0.075, 0.034, 0.014), (0.15, 0.075, 0.032))
    col = mix(nt, side, outer, inner)
    rough = add(nt, 0.75, mul(nt, n, 0.2))
    nrm = bump(nt, add(nt, mul(nt, fissure, -1.0), mul(nt, fib, 0.5)), 0.9, 0.0012)
    nrm = bump(nt, n, 0.6, 0.0008, nrm)
    bsdf = principled(nt, Base_Color=col, Roughness=rough, Normal=nrm)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def pebbles():
    m, nt, o = tree("monstera pebbles")
    p = objpos(nt)
    rnd = attr(nt, "rnd")
    q = add(nt, p, mul(nt, rnd, 11.0))
    base = ramp(nt, rnd, [(0.0, (0.14, 0.135, 0.13)), (0.3, (0.27, 0.25, 0.23)), (0.55, (0.40, 0.37, 0.33)),
                          (0.8, (0.22, 0.18, 0.15)), (1.0, (0.50, 0.48, 0.45))], interp="CONSTANT")
    sp = noise(nt, q, 900.0, 3.0, 0.6).outputs[0]
    mott = noise(nt, q, 160.0, 3.0, 0.6).outputs[0]
    col = node(nt, "ShaderNodeHueSaturation", {"Color": base, "Value": add(nt, 0.75, mul(nt, mott, 0.5))}).outputs[0]
    col = mix(nt, mul(nt, remap(nt, sp, 0.62, 0.72), 0.6), col, (0.05, 0.05, 0.05))
    nrm = bump(nt, sp, 0.25, 0.0002)
    bsdf = principled(nt, Base_Color=col, Roughness=add(nt, 0.42, mul(nt, mott, 0.25)), Normal=nrm)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def petiole():
    """Petioles: smooth glossy green, finely striate along their length, paler and yellower at the
    sheathing base and at the knee under the blade (UV u = metres along, v = around; 'pt' = 0 at the
    base, 1 at the blade)."""
    m, nt, o = tree("monstera petiole")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    a, b, _ = xyz(nt, uvn)
    pt = attr(nt, "pt")
    rnd = attr(nt, "rnd")
    stri = noise(nt, combine(nt, mul(nt, a, 6.0), mul(nt, b, 70.0), mul(nt, rnd, 9.0)), 1.0, 3.0, 0.6).outputs[0]
    blot = noise(nt, combine(nt, mul(nt, a, 25.0), mul(nt, b, 3.0), mul(nt, rnd, 9.0)), 1.0, 3.0, 0.6).outputs[0]
    col = mix(nt, mul(nt, remap(nt, stri, 0.35, 0.7), 0.35), (0.055, 0.12, 0.020), (0.08, 0.15, 0.028))
    col = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": add(nt, 0.85, mul(nt, blot, 0.3))}).outputs[0]
    knee = remap(nt, pt, 0.955, 0.985, smooth=True)
    col = mix(nt, mul(nt, knee, 0.8), col, (0.11, 0.17, 0.035))
    sheath = remap(nt, pt, 0.18, 0.0, smooth=True)
    col = mix(nt, mul(nt, sheath, 0.55), col, (0.12, 0.15, 0.045))
    nrm = bump(nt, stri, 0.25, 0.00015)
    bsdf = principled(nt, Base_Color=col, Roughness=add(nt, 0.32, mul(nt, blot, 0.12)), Normal=nrm,
                      Coat_Weight=0.25, Coat_Roughness=0.2, Specular_IOR_Level=0.45)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def stem():
    """The short trunks: green going corky brown towards the soil, ringed with old leaf scars at the
    nodes ('node' attribute, 1 on a scar)."""
    m, nt, o = tree("monstera stem")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    a, b, _ = xyz(nt, uvn)
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    scar = attr(nt, "node")
    n = noise(nt, p, 120.0, 4.0, 0.65).outputs[0]
    crk = noise(nt, combine(nt, mul(nt, a, 30.0), mul(nt, b, 250.0), 0.0), 1.0, 4.0, 0.6).outputs[0]
    green = mix(nt, n, (0.035, 0.06, 0.016), (0.06, 0.09, 0.025))
    cork = mix(nt, n, (0.06, 0.035, 0.018), (0.12, 0.08, 0.045))
    corky = remap(nt, add(nt, z, mul(nt, add(nt, n, -0.5), 0.08)), 0.47, 0.56, 1.0, 0.0, smooth=True)
    col = mix(nt, corky, green, cork)
    col = mix(nt, mul(nt, scar, 0.8), col, (0.10, 0.085, 0.05))
    nrm = bump(nt, add(nt, mul(nt, crk, corky), mul(nt, scar, 1.5)), 0.4, 0.0006)
    bsdf = principled(nt, Base_Color=col, Roughness=add(nt, 0.45, mul(nt, corky, 0.35)), Normal=nrm)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def root():
    """Aerial roots: brown and corky, finely cracked lengthwise, the growing tip pale ('pt' 1 at the tip)."""
    m, nt, o = tree("monstera aerial root")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    a, b, _ = xyz(nt, uvn)
    pt = attr(nt, "pt")
    crk = noise(nt, combine(nt, mul(nt, a, 40.0), mul(nt, b, 60.0), 0.0), 1.0, 5.0, 0.65).outputs[0]
    n = noise(nt, combine(nt, mul(nt, a, 8.0), mul(nt, b, 4.0), 3.0), 1.0, 3.0, 0.6).outputs[0]
    col = mix(nt, n, (0.05, 0.027, 0.014), (0.11, 0.065, 0.035))
    col = mix(nt, mul(nt, remap(nt, crk, 0.55, 0.7), 0.6), col, (0.16, 0.12, 0.08))
    tip = remap(nt, pt, 0.93, 0.99, smooth=True)
    col = mix(nt, tip, col, (0.30, 0.24, 0.14))
    nrm = bump(nt, crk, 0.5, 0.0004)
    bsdf = principled(nt, Base_Color=col, Roughness=0.72, Normal=nrm)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def cataphyll():
    """The dry papery sheaths round the stem at old nodes: tan to brown, veined lengthwise, translucent
    where thin ('pt' 0 at the base, 1 at the ragged top)."""
    m, nt, o = tree("monstera sheath")
    uvn = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    a, b, _ = xyz(nt, uvn)
    pt = attr(nt, "pt")
    rnd = attr(nt, "rnd")
    fib = noise(nt, combine(nt, mul(nt, a, 300.0), mul(nt, b, 12.0), mul(nt, rnd, 9.0)), 1.0, 4.0, 0.6).outputs[0]
    blot = noise(nt, combine(nt, mul(nt, a, 30.0), mul(nt, b, 25.0), mul(nt, rnd, 9.0)), 1.0, 3.0, 0.6).outputs[0]
    col = ramp(nt, add(nt, mul(nt, blot, 0.7), mul(nt, pt, 0.4)),
               [(0.0, (0.05, 0.03, 0.013)), (0.45, (0.10, 0.06, 0.028)), (0.8, (0.17, 0.11, 0.055)), (1.1, (0.24, 0.17, 0.09))])
    col = mix(nt, mul(nt, remap(nt, fib, 0.55, 0.7), 0.4), col, (0.10, 0.06, 0.03))
    nrm = bump(nt, fib, 0.4, 0.0003)
    bsdf = principled(nt, Base_Color=col, Roughness=0.62, Normal=nrm, Subsurface_Weight=0.35, Thin_Wall=True)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m
