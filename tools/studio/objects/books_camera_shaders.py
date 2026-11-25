# The DSLR's materials: satin black paint over moulded polycarbonate with worn edges, the pebbled
# rubber covering on the grip, front and thumb rest (a raised layer with a crisp edge), knurled black
# dials, chrome, the coated glass of the screens and the lens elements, matte black inside the lens.
# Body parts use camera-local object coordinates, lens parts the lens's own (axis +z).
from objects.conga_nodes import (tree, node, math, add, mul, mad, remap, mix, mixf, vec, xyz, combine, noise, bump,
                                 objpos, principled)
from lib import image

XM, ZM = 0.006, 0.0505
PLASTIC_DISP = "ambientcg/Plastic012A/Plastic012A_2K-JPG_Displacement.jpg"


def _band(nt, x, a, b, soft):
    return mul(nt, remap(nt, x, a - soft, a + soft), remap(nt, x, b - soft, b + soft, 1.0, 0.0))


def _grain(nt, p, scale=0.05):
    """The fine moulded grain of camera plastics (the monitors' plastic map, at camera scale)."""
    v = vec(nt, "SCALE", p, scale=1 / scale)
    t = node(nt, "ShaderNodeTexImage", {"Vector": v}, image=image(PLASTIC_DISP, False), projection="BOX",
             projection_blend=0.3)
    return t.outputs[0]


def _edges(nt, dist=0.0008):
    ao = node(nt, "ShaderNodeAmbientOcclusion", {"Distance": dist}, only_local=True, inside=True, samples=8).outputs["AO"]
    return remap(nt, ao, 0.72, 0.97, 1.0, 0.0)


def body():
    m, nt, o = tree("camera body")
    tc = node(nt, "ShaderNodeTexCoord")
    p, n = tc.outputs["Object"], tc.outputs["Normal"]
    x, y, z = xyz(nt, p)
    nx, ny, nz = xyz(nt, n)
    soft = 0.00015
    zb = _band(nt, z, 0.0068, 0.0712, soft)
    side = remap(nt, math(nt, "ABSOLUTE", nz), 0.50, 0.60, 1.0, 0.0)
    not_lug = remap(nt, math(nt, "ABSOLUTE", x), 0.0726, 0.0730, 1.0, 0.0)
    grip = mul(nt, mul(nt, remap(nt, x, -0.0240, -0.0244, 0.0, 1.0), zb), mul(nt, side, not_lug))
    rl = vec(nt, "LENGTH", combine(nt, add(nt, x, -XM), add(nt, z, -ZM), 0.0))
    front = mul(nt, mul(nt, remap(nt, ny, -0.50, -0.60), zb), mul(nt, remap(nt, rl, 0.0333, 0.0337),
                                                                   remap(nt, x, 0.0648, 0.0652, 1.0, 0.0)))
    thumb = mul(nt, mul(nt, remap(nt, ny, 0.50, 0.60), remap(nt, x, -0.0398, -0.0402)), _band(nt, z, 0.048, 0.0712, soft))
    leather = math(nt, "MAXIMUM", math(nt, "MAXIMUM", grip, front), thumb)

    # pebbled rubber: rounded cells with a little height variation, and a finer tooth
    vor = node(nt, "ShaderNodeTexVoronoi", {"Vector": p, "Scale": 1400.0, "Randomness": 0.9}, feature="F1")
    cell = remap(nt, vor.outputs["Distance"], 0.05, 0.55, 1.0, 0.0, smooth=True)
    vor2 = node(nt, "ShaderNodeTexVoronoi", {"Vector": p, "Scale": 1400.0, "Randomness": 0.9}, feature="DISTANCE_TO_EDGE")
    crev = remap(nt, vor2.outputs["Distance"], 0.0, 0.12, 0.0, 1.0)
    tooth = noise(nt, p, 6000.0, 2.0, 0.5).outputs[0]
    lh = mul(nt, mad(nt, cell, 0.5, mul(nt, crev, 0.5)), mad(nt, tooth, 0.3, 0.85))

    # the card door's seam on the grip's flank
    door = mul(nt, mul(nt, remap(nt, nx, -0.55, -0.65), remap(nt, x, -0.0690, -0.0695)),
               math(nt, "MAXIMUM", mul(nt, _band(nt, z, 0.016, 0.060, 0.0001), math(nt, "MAXIMUM",
                    _band(nt, y, -0.0232, -0.0228, 0.00007), _band(nt, y, 0.0168, 0.0172, 0.00007))),
                    mul(nt, _band(nt, y, -0.0230, 0.0170, 0.0001), math(nt, "MAXIMUM",
                        _band(nt, z, 0.0158, 0.0162, 0.00007), _band(nt, z, 0.0598, 0.0602, 0.00007)))))

    # the parting line between the top cover and the body shell, round the sides and back
    part = mul(nt, _band(nt, z, 0.0717, 0.0723, 0.00008), side)
    door = math(nt, "MAXIMUM", door, part)
    g = _grain(nt, p)
    smudge = noise(nt, p, 60.0, 3.0, 0.6).outputs[0]
    edge = mul(nt, _edges(nt), remap(nt, noise(nt, p, 900.0, 3.0, 0.6).outputs[0], 0.4, 0.65, 0.2, 1.0))
    paint = mix(nt, mul(nt, edge, 0.6), (0.0105, 0.0105, 0.0115), (0.040, 0.039, 0.038))
    rub = mix(nt, mul(nt, cell, 0.3), (0.0065, 0.0065, 0.007), (0.012, 0.012, 0.013))
    col = mix(nt, leather, paint, rub)
    col = mix(nt, mul(nt, door, 0.9), col, (0.003, 0.003, 0.003))
    r_paint = add(nt, add(nt, 0.34, mul(nt, remap(nt, smudge, 0.35, 0.7), 0.08)), mul(nt, edge, -0.12))
    r_rub = add(nt, 0.52, mul(nt, crev, 0.12))
    r = mixf(nt, leather, r_paint, r_rub)
    nrm = bump(nt, g, 0.08, 0.0002)
    nrm = bump(nt, mul(nt, leather, lh), 0.45, 0.00010, nrm)
    nrm = bump(nt, leather, 1.0, 0.00025, nrm)
    nrm = bump(nt, mul(nt, door, -1.0), 1.0, 0.0001, nrm)
    bs = principled(nt, Base_Color=col, Roughness=r, Normal=nrm, Specular_IOR_Level=0.5,
                    Sheen_Weight=mul(nt, leather, 0.15), Sheen_Roughness=0.4)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def satin(name, col, rough, grain=0.05, metal=0.0, spec=0.5, edge=True):
    m, nt, o = tree(name)
    p = objpos(nt)
    g = _grain(nt, p, grain)
    r = add(nt, rough, mul(nt, remap(nt, noise(nt, p, 80.0, 3.0, 0.6).outputs[0], 0.35, 0.7), 0.06))
    c = col
    if edge:
        e = mul(nt, _edges(nt, 0.0006), 0.5)
        c = mix(nt, e, col, tuple(min(1.0, v * 2.4 + 0.02) for v in col))
        r = mixf(nt, e, r, rough * 0.7)
    bs = principled(nt, Base_Color=c, Roughness=r, Metallic=metal, Normal=bump(nt, g, 0.06, 0.0002),
                    Specular_IOR_Level=spec)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def chrome(name, col=(0.86, 0.86, 0.87), rough=0.12):
    m, nt, o = tree(name)
    p = objpos(nt)
    tc = node(nt, "ShaderNodeTexCoord").outputs["Object"]
    x, y, z = xyz(nt, tc)
    # turned: fine circular lines round the lens axis
    rr = vec(nt, "LENGTH", combine(nt, x, z, 0.0))
    lines = noise(nt, combine(nt, mul(nt, rr, 1.0), 0.0, 0.0), 6000.0, 2.0, 0.5).outputs[0]
    r = add(nt, rough, mul(nt, remap(nt, lines, 0.3, 0.7), 0.06))
    bs = principled(nt, Base_Color=col, Metallic=1.0, Roughness=r, Normal=bump(nt, lines, 0.05, 0.00002))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def glass(name, film, film_ior=1.38, tint=(1.0, 1.0, 1.0), ior=1.62, spec=0.5):
    """Lens glass: its coating is a thin film (a single MgF2 layer: 100 nm reflects magenta, 200 nm
    green), and the anti-reflection effect is a lower specular level."""
    m, nt, o = tree(name)
    bs = principled(nt, Base_Color=tint, Roughness=0.0, Transmission_Weight=1.0, IOR=ior, Specular_IOR_Level=spec,
                    Thin_Film_Thickness=film, Thin_Film_IOR=film_ior)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def screen():
    m, nt, o = tree("camera screen glass")
    p = objpos(nt)
    smudge = noise(nt, p, 90.0, 4.0, 0.6).outputs[0]
    bs = principled(nt, Base_Color=(0.004, 0.005, 0.006), Roughness=add(nt, 0.03, mul(nt, remap(nt, smudge, 0.5, 0.8), 0.10)),
                    Specular_IOR_Level=0.5, Coat_Weight=1.0, Coat_Roughness=0.02, Thin_Film_Thickness=140.0,
                    Thin_Film_IOR=1.38)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def lens_plastic():
    """Satin black barrel with a white index dot and a short index line between the rings."""
    m, nt, o = tree("lens barrel")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    ang = math(nt, "ARCTAN2", x, y)                 # 0 at the top of the lens (+y up)
    rr = vec(nt, "LENGTH", combine(nt, x, y, 0.0))
    arc = mul(nt, ang, rr)                          # metres round from the top
    dot = remap(nt, vec(nt, "LENGTH", combine(nt, arc, add(nt, z, -0.0142), 0.0)), 0.0010, 0.0012, 1.0, 0.0)
    line = mul(nt, _band(nt, arc, -0.00028, 0.00028, 0.00006), _band(nt, z, 0.0512, 0.0590, 0.0001))
    ticks = 0.0
    for k, a in enumerate((-0.020, -0.011, -0.003, 0.004, 0.012)):
        ticks = math(nt, "MAXIMUM", ticks, mul(nt, _band(nt, arc, a - 0.0002, a + 0.0002, 0.00005),
                                                     _band(nt, z, 0.0122, 0.0158 - 0.0012 * (k % 2), 0.0001)))
    mark = math(nt, "MAXIMUM", math(nt, "MAXIMUM", dot, line), mul(nt, ticks, 0.0))
    g = _grain(nt, p, 0.04)
    e = mul(nt, _edges(nt, 0.0006), 0.5)
    col = mix(nt, e, (0.010, 0.010, 0.011), (0.04, 0.04, 0.04))
    col = mix(nt, mark, col, (0.80, 0.80, 0.78))
    r = add(nt, 0.34, mul(nt, remap(nt, noise(nt, p, 70.0, 3.0, 0.6).outputs[0], 0.35, 0.7), 0.08))
    bs = principled(nt, Base_Color=col, Roughness=mixf(nt, mark, r, 0.45), Normal=bump(nt, g, 0.06, 0.0002),
                    Specular_IOR_Level=0.5)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def rubber(name="camera rubber", col=(0.0075, 0.0075, 0.008)):
    m, nt, o = tree(name)
    p = objpos(nt)
    fine = noise(nt, p, 3000.0, 2.0, 0.5).outputs[0]
    dust = remap(nt, noise(nt, p, 140.0, 4.0, 0.6).outputs[0], 0.55, 0.75, 0.0, 1.0)
    c = mix(nt, mul(nt, dust, 0.5), col, (0.05, 0.048, 0.045))
    bs = principled(nt, Base_Color=c, Roughness=add(nt, 0.58, mul(nt, dust, 0.15)), Normal=bump(nt, fine, 0.12, 0.00004),
                    Specular_IOR_Level=0.45, Sheen_Weight=0.2, Sheen_Roughness=0.5)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def flat(name, col, rough, metal=0.0, spec=0.5):
    m, nt, o = tree(name)
    bs = principled(nt, Base_Color=col, Roughness=rough, Metallic=metal, Specular_IOR_Level=spec)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def lamp():
    m, nt, o = tree("camera lamp")
    bs = principled(nt, Base_Color=(0.35, 0.10, 0.03), Roughness=0.08, Transmission_Weight=0.6, IOR=1.5)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def make():
    return dict(
        body=body(),
        dial=satin("camera dial", (0.009, 0.009, 0.010), 0.30),
        button=satin("camera button", (0.010, 0.010, 0.011), 0.28),
        chrome=chrome("camera chrome"),
        shoe=satin("camera shoe", (0.16, 0.16, 0.17), 0.30, metal=1.0, edge=False),
        screen=screen(),
        rubber=rubber(),
        lamp=lamp(),
        lens=lens_plastic(),
        glass_front=glass("lens glass front", 100.0, spec=0.25),
        glass_inner=glass("lens glass inner", 200.0, spec=0.04),
        inner=flat("lens inside", (0.004, 0.004, 0.004), 0.75),
        iris=flat("lens iris", (0.015, 0.015, 0.016), 0.42, metal=0.6),
        paint=flat("lens paint", (0.8, 0.8, 0.78), 0.45),
    )
