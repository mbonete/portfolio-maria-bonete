# The tray's materials: oiled walnut (the walls mitred at the corners, the grain turning with each
# board; the floor glued up from three boards), glazed porcelain with a coffee line inside the cup, the
# crema, polished steel, roasted beans and jute burlap. Object coordinates are each part's own metres.
from objects.conga_nodes import (tree, node, math, add, mul, mad, remap, mix, mixf, vec, xyz, combine, noise, ramp,
                                 bump, attr, objpos, principled)
from lib import image

WALNUT = "polyhaven/black_walnut_veneer_02/black_walnut_veneer_02_"
FIGURED = "polyhaven/walnut_veneer_02/walnut_veneer_02_"
HESSIAN = "polyhaven/hessian_230/hessian_230_"
VENEER_SIZE = 1.0          # metres the veneer scans cover (Poly Haven: 1 x 1 m)
HESSIAN_SIZE = 0.2687


def _tex(nt, path, vec_, colour=True):
    return node(nt, "ShaderNodeTexImage", {"Vector": vec_}, image=image(path, colour), interpolation="Cubic").outputs[0]


def _oiled(nt, diff, darker=0.0):
    """Raw veneer read through oil: deep chocolate in the dark figure, warm amber in the light."""
    lum = node(nt, "ShaderNodeRGBToBW", {"Color": diff}).outputs[0]
    t = remap(nt, lum, 0.23, 0.47)
    col = ramp(nt, t, [(0.0, (0.050, 0.0240, 0.0105)), (0.40, (0.130, 0.066, 0.026)), (0.75, (0.225, 0.118, 0.050)),
                       (1.0, (0.310, 0.178, 0.082))])
    if darker:
        col = mix(nt, darker, col, (0.0, 0.0, 0.0), "MULTIPLY")
    return col


def walnut_frame(L, W):
    m, nt, o = tree("tray walnut frame")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    ax, ay = math(nt, "ABSOLUTE", x), math(nt, "ABSOLUTE", y)
    dx, dy = add(nt, L / 2, mul(nt, ax, -1.0)), add(nt, W / 2, mul(nt, ay, -1.0))
    is_end = math(nt, "LESS_THAN", dx, dy)                         # 1 on the end boards (grain along y)
    sx = math(nt, "SIGN", x)
    sy = math(nt, "SIGN", y)
    # each board its own part of the scan
    ou = mixf(nt, is_end, mad(nt, sy, 0.21, 0.37), mad(nt, sx, 0.17, 0.61))
    ov = mixf(nt, is_end, mad(nt, sy, 0.13, 0.28), mad(nt, sx, 0.23, 0.71))
    u_side, v_side = x, add(nt, z, ay)
    u_end, v_end = y, add(nt, z, ax)
    u = add(nt, mixf(nt, is_end, u_side, u_end), mul(nt, ou, VENEER_SIZE))
    v = add(nt, mixf(nt, is_end, v_side, v_end), mul(nt, ov, VENEER_SIZE))
    uv = combine(nt, mul(nt, u, 1 / VENEER_SIZE), mul(nt, v, 1.6 / VENEER_SIZE), 0.0)   # quarter-sawn: a little finer
    diff, rgh, nor = _tex(nt, WALNUT + "diff_4k.jpg", uv), _tex(nt, WALNUT + "rough_2k.jpg", uv, False), \
        _tex(nt, WALNUT + "nor_gl_2k.jpg", uv, False)
    col = _oiled(nt, diff)
    tone = node(nt, "ShaderNodeTexWhiteNoise", {"Vector": combine(nt, sx, sy, is_end)}, noise_dimensions="3D").outputs[0]
    col = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": mad(nt, tone, 0.18, 0.91),
                                               "Hue": mad(nt, tone, 0.012, 0.494)}).outputs[0]
    # the mitre: a hairline where the boards meet at each corner
    mitre = remap(nt, math(nt, "ABSOLUTE", add(nt, dx, mul(nt, dy, -1.0))), 0.00008, 0.00025, 1.0, 0.0)
    near = remap(nt, math(nt, "MINIMUM", dx, dy), 0.030, 0.034, 1.0, 0.0)
    mitre = mul(nt, mitre, near)
    col = mix(nt, mul(nt, mitre, 0.7), col, (0.012, 0.006, 0.003))
    # handling: the slots and the rim a shade darker and smoother where hands go
    slot = mul(nt, remap(nt, ay, 0.050, 0.060, 1.0, 0.0), remap(nt, dx, 0.016, 0.012, 0.0, 1.0))
    col = mix(nt, mul(nt, slot, 0.25), col, (0.02, 0.009, 0.004), "MULTIPLY")
    r = remap(nt, rgh, 0.2, 0.9, 0.40, 0.60)
    r = mixf(nt, mul(nt, slot, 0.6), r, 0.30)
    n = node(nt, "ShaderNodeNormalMap", {"Strength": 0.45, "Color": nor}).outputs[0]
    n = bump(nt, mul(nt, mitre, -1.0), 0.5, 0.00008, n)
    bs = principled(nt, Base_Color=col, Roughness=r, Normal=n, Specular_IOR_Level=0.36,
                    Coat_Weight=0.12, Coat_Roughness=0.26, Coat_IOR=1.48, Coat_Tint=(1.0, 0.93, 0.82))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def walnut_floor():
    m, nt, o = tree("tray walnut floor")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    bw = 0.1240                                                   # three boards across
    bi = math(nt, "FLOOR", mul(nt, add(nt, y, 1.5 * bw), 1 / bw))
    wn = node(nt, "ShaderNodeTexWhiteNoise", {"W": bi}, noise_dimensions="1D").outputs[0]
    wn2 = node(nt, "ShaderNodeTexWhiteNoise", {"W": add(nt, bi, 17.0)}, noise_dimensions="1D").outputs[0]
    u = add(nt, x, mul(nt, wn, VENEER_SIZE))
    v = add(nt, add(nt, y, z), mul(nt, wn2, VENEER_SIZE))
    uv = combine(nt, mul(nt, u, 1 / VENEER_SIZE), mul(nt, v, 1 / VENEER_SIZE), 0.0)
    diff, rgh, nor = _tex(nt, FIGURED + "diff_4k.jpg", uv), _tex(nt, FIGURED + "rough_2k.jpg", uv, False), \
        _tex(nt, FIGURED + "nor_gl_2k.jpg", uv, False)
    col = _oiled(nt, diff)
    col = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": mad(nt, wn2, 0.20, 0.88),
                                               "Hue": mad(nt, wn, 0.014, 0.493)}).outputs[0]
    f = math(nt, "FRACT", mul(nt, add(nt, y, 1.5 * bw), 1 / bw))
    d = mul(nt, math(nt, "MINIMUM", f, add(nt, 1.0, mul(nt, f, -1.0))), bw)
    joint = remap(nt, d, 0.00006, 0.00022, 1.0, 0.0)
    col = mix(nt, mul(nt, joint, 0.6), col, (0.012, 0.006, 0.003))
    r = remap(nt, rgh, 0.2, 0.9, 0.40, 0.60)
    n = node(nt, "ShaderNodeNormalMap", {"Strength": 0.45, "Color": nor}).outputs[0]
    n = bump(nt, mul(nt, joint, -1.0), 0.4, 0.00008, n)
    bs = principled(nt, Base_Color=col, Roughness=r, Normal=n, Specular_IOR_Level=0.36,
                    Coat_Weight=0.12, Coat_Roughness=0.26, Coat_IOR=1.48, Coat_Tint=(1.0, 0.93, 0.82))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def porcelain(name="porcelain", stain=None):
    """Glazed hard-paste porcelain; stain=(level, inner radius fn) draws the coffee line in the cup."""
    m, nt, o = tree(name)
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    ripple = noise(nt, p, 900.0, 2.0, 0.5).outputs[0]
    col = (0.80, 0.795, 0.775)
    rr = 0.04
    if stain:
        level = stain
        rho = vec(nt, "LENGTH", combine(nt, x, y, 0.0))
        band = mul(nt, remap(nt, z, level - 0.0004, level + 0.0002), remap(nt, z, level + 0.0010, level + 0.0024, 1.0, 0.0))
        band = mul(nt, band, remap(nt, rho, 0.0402, 0.0398, 0.0, 1.0))
        film = mul(nt, band, remap(nt, noise(nt, p, 300.0, 3.0, 0.6).outputs[0], 0.3, 0.7, 0.4, 1.0))
        col = mix(nt, film, col, (0.30, 0.15, 0.06))
    bs = principled(nt, Base_Color=col, Roughness=add(nt, rr, mul(nt, remap(nt, ripple, 0.3, 0.7), 0.03)),
                    Subsurface_Weight=0.25, Subsurface_Radius=(1.0, 0.85, 0.7), Subsurface_Scale=0.0012,
                    Specular_IOR_Level=0.55, Normal=bump(nt, ripple, 0.04, 0.00004))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def crema(r_wall):
    """Espresso crema: tan foam, lighter in the middle, tiger-flecked, thinning to dark coffee at the
    cup wall, with fine bubbles there."""
    m, nt, o = tree("crema")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    rho = vec(nt, "LENGTH", combine(nt, x, y, 0.0))
    t = mul(nt, rho, 1 / r_wall)
    warp = noise(nt, p, 60.0, 3.0, 0.6).outputs["Color"]
    pw = vec(nt, "ADD", p, vec(nt, "SCALE", add(nt, warp, -0.5), scale=0.006))
    fleck = noise(nt, vec(nt, "MULTIPLY", pw, (1.0, 1.0, 1.0)), 260.0, 4.0, 0.6).outputs[0]
    swirl = noise(nt, pw, 90.0, 3.0, 0.55).outputs[0]
    base = ramp(nt, t, [(0.0, (0.52, 0.225, 0.045)), (0.55, (0.42, 0.160, 0.026)), (1.0, (0.32, 0.110, 0.017))])
    col = mix(nt, mul(nt, remap(nt, fleck, 0.50, 0.64), 0.55), base, (0.17, 0.060, 0.013))
    col = mix(nt, mul(nt, remap(nt, swirl, 0.40, 0.65), 0.30), col, (0.60, 0.31, 0.085))
    # where the crema thins against the cup the dark coffee shows: a ring a few millimetres wide
    rim = remap(nt, add(nt, t, mul(nt, add(nt, swirl, -0.5), 0.06)), 0.80, 0.97, 0.0, 1.0, smooth=True)
    col = mix(nt, mul(nt, rim, 0.85), col, (0.075, 0.024, 0.006))
    vor = node(nt, "ShaderNodeTexVoronoi", {"Vector": p, "Scale": 2200.0, "Randomness": 1.0}, feature="F1")
    bub = mul(nt, remap(nt, vor.outputs["Distance"], 0.18, 0.08), remap(nt, t, 0.70, 0.92))
    col = mix(nt, mul(nt, bub, 0.6), col, (0.62, 0.40, 0.18))
    n = bump(nt, bub, 0.3, 0.00015)
    n = bump(nt, fleck, 0.05, 0.0001, n)
    # foam: a soft satin sheen, not a glaze
    bs = principled(nt, Base_Color=col, Roughness=add(nt, 0.42, mul(nt, remap(nt, swirl, 0.3, 0.7), 0.12)), Normal=n,
                    Specular_IOR_Level=0.28, Sheen_Weight=0.08, Sheen_Roughness=0.4, Sheen_Tint=(1.0, 0.75, 0.5),
                    Subsurface_Weight=0.15, Subsurface_Radius=(1.0, 0.6, 0.35), Subsurface_Scale=0.001)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def steel():
    m, nt, o = tree("spoon steel")
    p = objpos(nt)
    sm = noise(nt, p, 140.0, 4.0, 0.6).outputs[0]
    fine = noise(nt, vec(nt, "MULTIPLY", p, (1.0, 8.0, 8.0)), 3000.0, 2.0, 0.5).outputs[0]
    r = add(nt, 0.06, add(nt, mul(nt, remap(nt, sm, 0.45, 0.75), 0.12), mul(nt, fine, 0.03)))
    bs = principled(nt, Base_Color=(0.78, 0.77, 0.75), Metallic=1.0, Roughness=r, Normal=bump(nt, fine, 0.03, 0.00002))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def bean():
    m, nt, o = tree("roasted bean")
    p = objpos(nt)
    rnd = node(nt, "ShaderNodeObjectInfo").outputs["Random"]
    crease = attr(nt, "crease")
    roast = ramp(nt, rnd, [(0.0, (0.022, 0.0095, 0.0055)), (0.5, (0.048, 0.021, 0.0105)), (1.0, (0.085, 0.040, 0.018))])
    mott = noise(nt, vec(nt, "ADD", p, (0.0, 0.0, 0.0)), 700.0, 3.0, 0.6).outputs[0]
    col = mix(nt, mul(nt, remap(nt, mott, 0.35, 0.7), 0.35), roast, (0.10, 0.050, 0.022))
    groove = remap(nt, crease, 0.25, 0.75)
    col = mix(nt, mul(nt, groove, 0.65), col, (0.010, 0.0045, 0.0025))
    skin = mul(nt, remap(nt, crease, 0.88, 0.98), remap(nt, noise(nt, p, 1500.0, 2.0, 0.5).outputs[0], 0.35, 0.6, 0.3, 1.0))
    col = mix(nt, skin, col, (0.34, 0.22, 0.11))
    oily = remap(nt, rnd, 0.0, 1.0, 0.26, 0.48)
    wr = noise(nt, p, 2600.0, 3.0, 0.6).outputs[0]
    bs = principled(nt, Base_Color=col, Roughness=mixf(nt, skin, add(nt, oily, mul(nt, wr, 0.08)), 0.7),
                    Normal=bump(nt, wr, 0.12, 0.00005), Specular_IOR_Level=0.5, Coat_Weight=mul(nt, sub(nt, 1.0, rnd), 0.3),
                    Coat_Roughness=0.18)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def sub(nt, a, b):
    return math(nt, "SUBTRACT", a, b)


def burlap():
    m, nt, o = tree("burlap")
    uvp = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    uv = vec(nt, "SCALE", uvp, scale=1 / HESSIAN_SIZE)
    diff = _tex(nt, HESSIAN + "diff_4k.jpg", uv)
    rgh = _tex(nt, HESSIAN + "rough_2k.jpg", uv, False)
    nor = _tex(nt, HESSIAN + "nor_gl_2k.jpg", uv, False)
    disp = _tex(nt, HESSIAN + "disp_2k.jpg", uv, False)
    mask = _tex(nt, HESSIAN + "mask_2k.jpg", uv, False)
    p = objpos(nt)
    lum = node(nt, "ShaderNodeRGBToBW", {"Color": diff}).outputs[0]
    t = remap(nt, lum, 0.05, 0.45)
    col = ramp(nt, t, [(0.0, (0.030, 0.018, 0.009)), (0.35, (0.150, 0.092, 0.042)), (0.75, (0.330, 0.215, 0.105)),
                       (1.0, (0.460, 0.320, 0.165))])
    blot = noise(nt, p, 14.0, 3.0, 0.6).outputs[0]
    col = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": mad(nt, blot, 0.30, 0.86),
                                               "Hue": mad(nt, blot, 0.03, 0.485)}).outputs[0]
    gaps = remap(nt, mask, 0.6, 0.2)
    col = mix(nt, mul(nt, gaps, 0.85), col, (0.012, 0.007, 0.004))
    n = node(nt, "ShaderNodeNormalMap", {"Strength": 1.0, "Color": nor}).outputs[0]
    n = bump(nt, disp, 0.35, 0.0008, n)
    bs = principled(nt, Base_Color=col, Roughness=remap(nt, rgh, 0.0, 1.0, 0.70, 0.95), Normal=n,
                    Specular_IOR_Level=0.30, Sheen_Weight=0.6, Sheen_Roughness=0.45, Sheen_Tint=(1.0, 0.85, 0.62))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def jute_fibre():
    m, nt, o = tree("jute fibre")
    rnd = node(nt, "ShaderNodeHairInfo").outputs["Random"]
    col = ramp(nt, rnd, [(0.0, (0.16, 0.10, 0.045)), (0.6, (0.32, 0.21, 0.10)), (1.0, (0.46, 0.33, 0.17))])
    bs = principled(nt, Base_Color=col, Roughness=0.55, Specular_IOR_Level=0.35, Sheen_Weight=0.3, Sheen_Roughness=0.4)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m
