# The books' materials: woven book cloth or a printed paper-over-board cover per book (with its spine
# marks, edge and corner wear), the page edges, and the striped headbands. The case carries a UV map in
# metres: u along the book's height, v along the case's section (negative inside), so the spine is a
# band of v; object coordinates are the book's own.
from objects.conga_nodes import (tree, node, math, add, mul, mad, remap, mix, mixf, vec, xyz, combine, noise, bump,
                                 objpos, principled)

# cover colours (linear): cloth, its worn edges, and the headband's two threads
PALETTE = {
    "navy":   dict(col=(0.024, 0.036, 0.080), worn=(0.115, 0.120, 0.140), hb=((0.45, 0.06, 0.04), (0.80, 0.74, 0.60))),
    "navy2":  dict(col=(0.030, 0.042, 0.088), worn=(0.120, 0.125, 0.150), hb=((0.80, 0.74, 0.60), (0.05, 0.06, 0.12))),
    "green":  dict(col=(0.020, 0.052, 0.034), worn=(0.100, 0.120, 0.100), hb=((0.70, 0.55, 0.18), (0.08, 0.20, 0.10))),
    "slate":  dict(col=(0.052, 0.082, 0.140), worn=(0.150, 0.160, 0.180), hb=((0.80, 0.74, 0.60), (0.06, 0.08, 0.16))),
    "red":    dict(col=(0.180, 0.020, 0.016), worn=(0.240, 0.120, 0.100), hb=((0.80, 0.74, 0.60), (0.25, 0.02, 0.02))),
    "brick":  dict(col=(0.270, 0.048, 0.026), worn=(0.300, 0.160, 0.120), hb=((0.70, 0.55, 0.18), (0.30, 0.04, 0.02))),
    "olive":  dict(col=(0.064, 0.074, 0.030), worn=(0.150, 0.150, 0.110), hb=((0.45, 0.06, 0.04), (0.70, 0.62, 0.40))),
    "teal":   dict(col=(0.020, 0.072, 0.080), worn=(0.110, 0.140, 0.140), hb=((0.80, 0.74, 0.60), (0.03, 0.10, 0.11))),
    "cream":  dict(col=(0.600, 0.520, 0.360), worn=(0.380, 0.320, 0.230), hb=((0.05, 0.06, 0.12), (0.80, 0.74, 0.60))),
    "ochre_print": dict(col=(0.470, 0.250, 0.040), worn=(0.640, 0.580, 0.470), hb=((0.30, 0.04, 0.02), (0.80, 0.70, 0.40)),
                        printed=True),
}
GILT = (0.80, 0.56, 0.24)
INK = (0.030, 0.020, 0.016)


def _uv(nt):
    return xyz(nt, node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0])


def _band(nt, x, a, b, soft=0.00012):
    """1 between a and b (a < b), soft edges."""
    return mul(nt, remap(nt, x, a - soft, a + soft), remap(nt, x, b - soft, b + soft, 1.0, 0.0))


def _weave(nt, u, v, pitch):
    """Plain weave: a height field of over/under threads, and a per-thread tone."""
    su, sv = mul(nt, u, 1 / pitch), mul(nt, v, 1 / pitch)
    fu, fv = math(nt, "FRACT", su), math(nt, "FRACT", sv)
    iu, iv = math(nt, "FLOOR", su), math(nt, "FLOOR", sv)
    par = mul(nt, math(nt, "FRACT", mul(nt, add(nt, iu, iv), 0.5)), 2.0)          # 0 or 1
    across_warp = math(nt, "SQRT", math(nt, "SINE", mul(nt, fv, 3.14159)), clamp=True)
    across_weft = math(nt, "SQRT", math(nt, "SINE", mul(nt, fu, 3.14159)), clamp=True)
    along_warp = mad(nt, math(nt, "SINE", mul(nt, fu, 3.14159)), 0.35, 0.65)
    along_weft = mad(nt, math(nt, "SINE", mul(nt, fv, 3.14159)), 0.35, 0.65)
    h = mixf(nt, par, mul(nt, across_weft, along_weft), mul(nt, across_warp, along_warp))
    # slubs: threads thicken and thin along their length
    slub_w = noise(nt, combine(nt, mul(nt, u, 1.0), mul(nt, iv, 7.31), 0.0), 900.0, 1.0).outputs[0]
    slub_f = noise(nt, combine(nt, mul(nt, iu, 5.17), mul(nt, v, 1.0), 3.0), 900.0, 1.0).outputs[0]
    slub = mixf(nt, par, slub_f, slub_w)
    h = mul(nt, h, mad(nt, slub, 0.6, 0.7))
    # each thread is dyed a touch differently
    tw = node(nt, "ShaderNodeTexWhiteNoise", {"W": iv}, noise_dimensions="1D").outputs[0]
    tf = node(nt, "ShaderNodeTexWhiteNoise", {"W": add(nt, iu, 911.0)}, noise_dimensions="1D").outputs[0]
    tone = mixf(nt, par, tf, tw)
    return h, tone


def cover(name, kind, marks, H, spine, seed):
    """A book's case: cloth (or printed paper) with spine marks and wear."""
    P = PALETTE[kind]
    printed = P.get("printed", False)
    m, nt, o = tree(name)
    u, v, _ = _uv(nt)
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    s0, s1 = spine
    sm = (s0 + s1) / 2
    on_spine = _band(nt, v, s0 + 0.0015, s1 - 0.0015, 0.0012)

    # ---- base: cloth weave or a printed, laminated sheet
    big = noise(nt, vec(nt, "ADD", p, (seed * 10, seed * 3, 0)), 18.0, 3.0, 0.55).outputs[0]
    mid = noise(nt, p, 140.0, 3.0, 0.6).outputs[0]
    col = P["col"]
    if not printed:
        h, tone = _weave(nt, u, v, 0.00055)
        base = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": add(nt, 0.92, mul(nt, tone, 0.16)),
                                                     "Saturation": add(nt, 0.95, mul(nt, tone, 0.1))}).outputs[0]
        base = mix(nt, mul(nt, h, 0.25), mul_col(nt, base, 0.80), base)
        # slubs: threads thicker or paler for a few centimetres, streaking the cloth along warp and weft
        warp = noise(nt, combine(nt, mul(nt, u, 0.04), v, 1.7), 1800.0, 2.0, 0.6).outputs[0]
        weft = noise(nt, combine(nt, u, mul(nt, v, 0.04), 4.1), 1800.0, 2.0, 0.6).outputs[0]
        streak = add(nt, mul(nt, remap(nt, warp, 0.35, 0.65, -1.0, 1.0), 0.6), mul(nt, remap(nt, weft, 0.35, 0.65, -1.0, 1.0), 0.4))
        base = node(nt, "ShaderNodeHueSaturation", {"Color": base, "Value": add(nt, 1.0, mul(nt, streak, 0.09))}).outputs[0]
        h = add(nt, h, mul(nt, streak, 0.35))
    else:
        h = noise(nt, p, 2500.0, 2.0, 0.6).outputs[0]
        base = col
    base = node(nt, "ShaderNodeHueSaturation", {"Color": base, "Value": add(nt, 0.93, mul(nt, big, 0.14)),
                                                 "Hue": add(nt, 0.49, mul(nt, mid, 0.02))}).outputs[0]
    # the spine has faded a little in daylight, as on a shelf
    fade = mul(nt, on_spine, 0.6)
    base = mix(nt, mul(nt, fade, 0.22), base, add_col(nt, base, (0.05, 0.05, 0.05)), "SCREEN")
    base = node(nt, "ShaderNodeHueSaturation", {"Color": base, "Saturation": sub1(nt, mul(nt, fade, 0.18))}).outputs[0]

    # ---- spine marks (abstract only)
    du = math(nt, "ABSOLUTE", u)              # distance from the middle of the book's height
    head = H / 2
    gilt = 0.0
    ink = 0.0
    if marks in ("rules", "label", "dots"):
        r = 0.0
        for a in (0.0150, 0.0185):
            r = math(nt, "MAXIMUM", r, _band(nt, du, head - a - 0.0004, head - a + 0.0004))
        gilt = mul(nt, r, on_spine)
    if marks == "label":
        # a darker panel with a gilt border, blank
        lu0, lu1 = head - 0.095, head - 0.050
        half = (s1 - s0) * 0.30
        panel = mul(nt, _band(nt, u, lu0, lu1), _band(nt, v, sm - half, sm + half))
        inner = mul(nt, _band(nt, u, lu0 + 0.0016, lu1 - 0.0016), _band(nt, v, sm - half + 0.0016, sm + half - 0.0016))
        inner2 = mul(nt, _band(nt, u, lu0 + 0.0024, lu1 - 0.0024), _band(nt, v, sm - half + 0.0024, sm + half - 0.0024))
        border = mul(nt, inner, add(nt, 1.0, mul(nt, inner2, -1.0)))
        base = mix(nt, panel, base, (0.045, 0.012, 0.008))
        gilt = math(nt, "MAXIMUM", gilt, border)
    if marks == "dots":
        d = 0.0
        for k in range(3):
            cu = head - 0.060 - 0.009 * k
            dd = vec(nt, "LENGTH", combine(nt, add(nt, u, -cu), add(nt, v, -sm), 0.0))
            d = math(nt, "MAXIMUM", d, remap(nt, dd, 0.0016, 0.0019, 1.0, 0.0))
        gilt = math(nt, "MAXIMUM", gilt, d)
    if marks == "disc":
        # printed: a dark disc and a thin rule through it, on the spine and the front board
        dd = vec(nt, "LENGTH", combine(nt, add(nt, u, -(head - 0.070)), add(nt, v, -sm), 0.0))
        disc = remap(nt, dd, 0.0105, 0.0110, 1.0, 0.0)
        rule = mul(nt, _band(nt, v, sm - 0.00035, sm + 0.00035), _band(nt, u, -head + 0.03, head - 0.03))
        ink = math(nt, "MAXIMUM", disc, mul(nt, rule, on_spine))
        ring = mul(nt, remap(nt, dd, 0.0128, 0.0131, 0.0, 1.0), remap(nt, dd, 0.0136, 0.0139, 1.0, 0.0))
        ink = math(nt, "MAXIMUM", ink, ring)
    if marks == "band":
        # a block of navy foil across the spine
        bandm = mul(nt, _band(nt, u, head - 0.075, head - 0.050), on_spine)
        base = mix(nt, bandm, base, (0.030, 0.040, 0.085))
        gilt = math(nt, "MAXIMUM", mul(nt, _band(nt, du, head - 0.0805, head - 0.0795), on_spine),
                    mul(nt, _band(nt, du, head - 0.0455, head - 0.0445), on_spine))
    if ink != 0.0:
        base = mix(nt, mul(nt, ink, 0.92), base, INK)

    # ---- wear: the cloth rubbed pale along convex edges, most at the head and tail (corners, spine ends)
    ao = node(nt, "ShaderNodeAmbientOcclusion", {"Distance": 0.0009}, only_local=True, inside=True, samples=8).outputs["AO"]
    edge = remap(nt, ao, 0.70, 0.97, 1.0, 0.0)
    brk = noise(nt, p, 260.0, 4.0, 0.65).outputs[0]
    brk2 = noise(nt, p, 60.0, 3.0, 0.6).outputs[0]
    dxh = add(nt, H / 2, mul(nt, math(nt, "ABSOLUTE", x), -1.0))
    wear = mul(nt, edge, remap(nt, brk, 0.42, 0.62, 0.15, 1.0))
    ends = remap(nt, dxh, 0.0, 0.006, 1.0, 0.0)
    wear = math(nt, "MAXIMUM", wear, mul(nt, mul(nt, ends, edge), remap(nt, brk2, 0.35, 0.6, 0.3, 1.2)))
    wear = math(nt, "MINIMUM", wear, 1.0)
    gilt_keep = remap(nt, noise(nt, p, 420.0, 3.0, 0.6).outputs[0], 0.30, 0.38)
    gilt = mul(nt, gilt, gilt_keep) if gilt != 0.0 else 0.0
    col_out = mix(nt, mul(nt, wear, 0.85), base, P["worn"])
    if gilt != 0.0:
        col_out = mix(nt, gilt, col_out, GILT)

    # ---- surface
    rough = 0.80 if not printed else 0.42
    r = add(nt, rough, mul(nt, remap(nt, mid, 0.3, 0.7), 0.06))
    r = mixf(nt, mul(nt, wear, 0.6), r, 0.55 if not printed else 0.75)
    if gilt != 0.0:
        r = mixf(nt, gilt, r, add(nt, 0.26, mul(nt, brk, 0.12)))
    if not printed:
        nrm = bump(nt, h, 0.5, 0.00014)
    else:
        nrm = bump(nt, h, 0.05, 0.00004)
    if gilt != 0.0:
        nrm = bump(nt, mul(nt, gilt, -1.0), 0.6, 0.00015, nrm)
    nrm = bump(nt, mul(nt, wear, mul(nt, brk, -1.0)), 0.3, 0.0002, nrm)
    kw = dict(Base_Color=col_out, Roughness=r, Normal=nrm, Specular_IOR_Level=0.35 if not printed else 0.5)
    if gilt != 0.0:
        kw["Metallic"] = gilt
    if not printed:
        kw.update(Sheen_Weight=0.45, Sheen_Roughness=0.45, Sheen_Tint=(0.9, 0.88, 0.84))
    bs = principled(nt, **kw)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m


def mul_col(nt, c, f):
    return node(nt, "ShaderNodeMix", {"Factor_Float": 1.0, "A_Color": c, "B_Color": (f, f, f)}, data_type="RGBA",
                blend_type="MULTIPLY").outputs[2]


def add_col(nt, c, d):
    return node(nt, "ShaderNodeMix", {"Factor_Float": 1.0, "A_Color": c, "B_Color": d}, data_type="RGBA",
                blend_type="ADD").outputs[2]


def sub1(nt, a):
    return add(nt, 1.0, mul(nt, a, -1.0))


_PAPER = {}


def paper(kind):
    """The text block's edges: leaves seen edge-on, grouped in signatures, toned at the surface."""
    if kind in _PAPER:
        return _PAPER[kind]
    m, nt, o = tree(f"book pages {kind}")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    rnd = node(nt, "ShaderNodeObjectInfo").outputs["Random"]
    warp = noise(nt, p, 30.0, 2.0, 0.5).outputs[0]
    zw = add(nt, add(nt, z, mul(nt, warp, 0.0004)), mul(nt, rnd, 0.37))
    zline = combine(nt, 0.0, 0.0, zw)
    fine = noise(nt, zline, 2600.0, 2.0, 0.6).outputs[0]
    fine2 = noise(nt, combine(nt, mul(nt, x, 0.02), 0.0, zw), 900.0, 2.0, 0.5).outputs[0]
    sig_s = noise(nt, combine(nt, 0.0, 0.0, zw), 30.0, 1.0).outputs[0]
    sig = math(nt, "FRACT", add(nt, mul(nt, zw, 1 / 0.0029), mul(nt, sig_s, 2.0)))
    sigline = remap(nt, math(nt, "ABSOLUTE", add(nt, sig, -0.5)), 0.44, 0.5)
    if kind == "cream":
        c0, c1, tone = (0.66, 0.565, 0.40), (0.50, 0.415, 0.28), (0.55, 0.45, 0.30)
        rough = 0.72
    else:
        c0, c1, tone = (0.70, 0.67, 0.60), (0.52, 0.50, 0.45), (0.64, 0.59, 0.49)
        rough = 0.48
    col = mix(nt, mul(nt, remap(nt, fine, 0.3, 0.7), 0.55), c0, c1)
    col = mix(nt, mul(nt, remap(nt, fine2, 0.35, 0.65), 0.35), col, c1)
    col = mix(nt, mul(nt, sigline, 0.5), col, mul_col(nt, c1, 0.75))
    blot = noise(nt, p, 22.0, 3.0, 0.6).outputs[0]
    col = mix(nt, mul(nt, remap(nt, blot, 0.45, 0.7), 0.45), col, tone)
    h = add(nt, mul(nt, fine, 0.6), mul(nt, sigline, -0.6))
    nrm = bump(nt, h, 0.25, 0.00006)
    r = add(nt, rough, mul(nt, remap(nt, fine, 0.3, 0.7), 0.08))
    bs = principled(nt, Base_Color=col, Roughness=r, Normal=nrm, Specular_IOR_Level=0.4,
                    Sheen_Weight=0.15, Sheen_Roughness=0.5)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    _PAPER[kind] = m
    return m


def headband(kind):
    a, b = PALETTE[kind]["hb"]
    m, nt, o = tree(f"headband {kind}")
    u, v, _ = _uv(nt)
    s = math(nt, "FRACT", mul(nt, v, 1 / 0.0012))
    stripe = remap(nt, s, 0.45, 0.55)
    col = mix(nt, stripe, a, b)
    thread = math(nt, "SINE", mul(nt, add(nt, u, mul(nt, v, 40.0)), 6.28318 * 9))
    nrm = bump(nt, thread, 0.4, 0.0001)
    bs = principled(nt, Base_Color=col, Roughness=0.55, Normal=nrm, Sheen_Weight=0.5, Sheen_Roughness=0.35,
                    Specular_IOR_Level=0.4)
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return m
