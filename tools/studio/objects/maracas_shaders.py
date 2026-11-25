# The maracas' materials. The head: red lacquer over the tip, green over the neck, and between them a
# band of bare, varnished wood painted by hand with gold stars and dark sprigs, each edge ruled with a
# dark and a gold line that wander a little. The handle: turned beech under a clear varnish. Object
# coordinates: the axis along x from the tip.
import math as m
from objects.conga_nodes import (tree, node, math, add, mul, mad, remap, mix, mixf, vec, xyz, combine, noise, ramp,
                                 bump, objpos, principled)

RED = (0.42, 0.012, 0.010)
GREEN = (0.008, 0.085, 0.034)
WOOD = (0.40, 0.235, 0.105)
GOLD = (0.80, 0.56, 0.20)
INK = (0.030, 0.014, 0.008)
X_RED, X_GREEN = 0.047, 0.083          # where the red ends and the green begins


def _seg(nt, p, a, b, w):
    """1 within w of the segment a-b (2D points as (u, v, 0) sockets/tuples)."""
    pa = vec(nt, "SUBTRACT", p, a)
    ba = vec(nt, "SUBTRACT", b, a)
    h = math(nt, "DIVIDE", vec(nt, "DOT_PRODUCT", pa, ba), vec(nt, "DOT_PRODUCT", ba, ba))
    h = math(nt, "MINIMUM", math(nt, "MAXIMUM", h, 0.0), 1.0)
    d = vec(nt, "LENGTH", vec(nt, "SUBTRACT", pa, vec(nt, "SCALE", ba, scale=h)))
    return remap(nt, d, w * 0.7, w, 1.0, 0.0)


def _star(nt, q, r_out, r_in, turn=0.0):
    u, v, _ = xyz(nt, q)
    rho = vec(nt, "LENGTH", q)
    phi = add(nt, math(nt, "ARCTAN2", u, v), turn)
    k = math(nt, "FRACT", mul(nt, add(nt, phi, 3.14159), 5 / (2 * 3.14159)))
    tri = mul(nt, math(nt, "ABSOLUTE", add(nt, k, -0.5)), 2.0)
    R = add(nt, r_in, mul(nt, math(nt, "POWER", tri, 1.6), math(nt, "SUBTRACT", r_out, r_in)))
    return remap(nt, add(nt, rho, mul(nt, R, -1.0)), 0.00025, -0.00015)


def head():
    mt, nt, o = tree("maraca head")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    rnd = node(nt, "ShaderNodeObjectInfo").outputs["Random"]
    r = vec(nt, "LENGTH", combine(nt, y, z, 0.0))
    th = add(nt, math(nt, "ARCTAN2", z, y), mul(nt, rnd, 6.2832))
    # hand-ruled borders wander by a millimetre
    wob = mul(nt, add(nt, noise(nt, combine(nt, math(nt, "SINE", th), math(nt, "COSINE", th), 0.0), 1.6, 2.0).outputs[0], -0.5), 0.003)
    xr = add(nt, X_RED, wob)
    xg = add(nt, X_GREEN, mul(nt, wob, -0.8))
    red = remap(nt, add(nt, x, mul(nt, xr, -1.0)), 0.00015, -0.00015)
    green = remap(nt, add(nt, x, mul(nt, xg, -1.0)), -0.00015, 0.00015)
    band = mul(nt, add(nt, 1.0, mul(nt, red, -1.0)), add(nt, 1.0, mul(nt, green, -1.0)))
    # border lines: a dark rule on the paint's edge and a gold one just inside the band
    def rule(edge, off, w):
        return remap(nt, math(nt, "ABSOLUTE", add(nt, add(nt, x, mul(nt, edge, -1.0)), -off)), w * 0.6, w, 1.0, 0.0)
    ink = math(nt, "MAXIMUM", rule(xr, 0.0002, 0.00065), rule(xg, -0.0002, 0.00065))
    gold = math(nt, "MAXIMUM", rule(xr, 0.0022, 0.00050), rule(xg, -0.0022, 0.00050))
    # motifs: five sectors round the band; a gold star in each, a dark sprig between
    n = 5
    sec = math(nt, "FRACT", mul(nt, th, n / (2 * m.pi)))
    # painted by hand: each motif sits a little off its place, turned and sized its own way
    idx = math(nt, "FLOOR", mul(nt, th, n / (2 * m.pi)))
    jit = node(nt, "ShaderNodeTexWhiteNoise", {"W": add(nt, idx, mul(nt, rnd, 50.0))}, noise_dimensions="1D").outputs["Color"]
    ju, jv, jr = xyz(nt, jit)
    arc = add(nt, mul(nt, mul(nt, add(nt, sec, -0.5), 2 * m.pi / n), r), mul(nt, add(nt, ju, -0.5), 0.004))
    vc = add(nt, add(nt, x, -(X_RED + X_GREEN) / 2), mul(nt, add(nt, jv, -0.5), 0.004))
    q = combine(nt, arc, vc, 0.0)
    size = mad(nt, jr, 0.0012, 0.0056)
    star = _star(nt, q, size, mul(nt, size, 0.42), mul(nt, jr, 1.3))
    centre = remap(nt, vec(nt, "LENGTH", q), 0.0011, 0.0008)
    sec2 = math(nt, "FRACT", add(nt, mul(nt, th, n / (2 * m.pi)), 0.5))
    arc2 = mul(nt, mul(nt, add(nt, sec2, -0.5), 2 * m.pi / n), r)
    q2 = combine(nt, arc2, vc, 0.0)
    sprig = 0.0
    for a, b in (((0.0, -0.011, 0), (0.0, 0.011, 0)), ((0.0, -0.002, 0), (0.0055, 0.006, 0)),
                 ((0.0, -0.002, 0), (-0.0055, 0.006, 0)), ((0.0, 0.004, 0), (0.0042, 0.0105, 0)),
                 ((0.0, 0.004, 0), (-0.0042, 0.0105, 0)), ((0.0, -0.007, 0), (0.0048, -0.0025, 0)),
                 ((0.0, -0.007, 0), (-0.0048, -0.0025, 0))):
        sprig = math(nt, "MAXIMUM", sprig, _seg(nt, q2, a, b, 0.00055))
    dots = remap(nt, vec(nt, "LENGTH", vec(nt, "SUBTRACT", q2, (0.0, 0.0135, 0.0))), 0.0011, 0.0008)
    gold = math(nt, "MAXIMUM", gold, mul(nt, math(nt, "MAXIMUM", star, dots), band))
    ink = math(nt, "MAXIMUM", ink, mul(nt, math(nt, "MAXIMUM", sprig, centre), band))
    # a few small gold stars scattered on the red, as in the reference
    q3 = combine(nt, arc2, add(nt, x, -0.030), 0.0)
    small = mul(nt, _star(nt, q3, 0.0040, 0.0017), red)
    gold = math(nt, "MAXIMUM", gold, small)

    # the wood under the band: fine grain along the axis
    grain = noise(nt, vec(nt, "MULTIPLY", p, (0.08, 1.0, 1.0)), 350.0, 3.0, 0.6).outputs[0]
    wood = mix(nt, mul(nt, remap(nt, grain, 0.40, 0.65), 0.5), WOOD, (0.25, 0.13, 0.05))
    paint = mix(nt, red, mix(nt, green, wood, GREEN), RED)
    tone = noise(nt, p, 40.0, 3.0, 0.5).outputs[0]
    paint = node(nt, "ShaderNodeHueSaturation", {"Color": paint, "Value": mad(nt, tone, 0.12, 0.94)}).outputs[0]
    col = mix(nt, ink, paint, INK)
    col = mix(nt, gold, col, GOLD)
    metal = mul(nt, gold, 0.85)
    rough = mixf(nt, band, 0.22, 0.38)
    rough = mixf(nt, gold, rough, 0.30)
    peel = noise(nt, p, 900.0, 2.0, 0.5).outputs[0]
    cn = bump(nt, peel, 0.04, 0.00002)
    n = bump(nt, grain, mul(nt, band, 0.12), 0.00005)
    n = bump(nt, math(nt, "MAXIMUM", gold, ink), 0.4, 0.00004, n)
    bs = principled(nt, Base_Color=col, Metallic=metal, Roughness=rough, Normal=n, Specular_IOR_Level=0.5,
                    Coat_Weight=1.0, Coat_Roughness=add(nt, 0.035, mul(nt, band, 0.08)), Coat_IOR=1.52, Coat_Normal=cn,
                    Coat_Tint=(1.0, 0.95, 0.88))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return mt


def handle():
    """Turned beech: the growth rings cut by the turning show as long stripes along the handle, with
    the fine dark flecks of beech's rays, under a clear varnish."""
    mt, nt, o = tree("maraca handle")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    rnd = node(nt, "ShaderNodeObjectInfo").outputs["Random"]
    # the log's pith runs just off the blank, a little skew to the handle
    py = add(nt, add(nt, y, -0.034), mul(nt, x, 0.04))
    pz = add(nt, add(nt, z, mad(nt, rnd, 0.02, -0.01)), mul(nt, x, -0.02))
    warp = noise(nt, vec(nt, "MULTIPLY", p, (8.0, 60.0, 60.0)), 1.0, 3.0, 0.5).outputs[0]
    d = add(nt, vec(nt, "LENGTH", combine(nt, py, pz, 0.0)), mul(nt, warp, 0.0012))
    ring = math(nt, "FRACT", mul(nt, d, 1 / 0.0021))
    late = remap(nt, ring, 0.70, 0.92, 0.0, 1.0, smooth=True)
    late = mul(nt, late, remap(nt, ring, 0.96, 1.0, 1.0, 0.0))
    pp = vec(nt, "ADD", p, combine(nt, mul(nt, rnd, 3.0), 0.0, 0.0))
    fleck = noise(nt, vec(nt, "MULTIPLY", pp, (0.35, 1.0, 1.0)), 2200.0, 2.0, 0.5).outputs[0]
    tone = noise(nt, pp, 30.0, 2.0, 0.5).outputs[0]
    col = mix(nt, mul(nt, late, 0.55), (0.50, 0.32, 0.155), (0.33, 0.185, 0.075))
    col = mix(nt, mul(nt, remap(nt, fleck, 0.62, 0.74), 0.40), col, (0.25, 0.13, 0.055))
    col = node(nt, "ShaderNodeHueSaturation", {"Color": col, "Value": mad(nt, tone, 0.14, 0.93)}).outputs[0]
    # handled: a little darker and glossier along the grip
    grip = mul(nt, remap(nt, x, 0.150, 0.170, 0.0, 1.0), remap(nt, x, 0.230, 0.250, 1.0, 0.0))
    col = mix(nt, mul(nt, grip, 0.18), col, (0.18, 0.09, 0.035), "MULTIPLY")
    n = bump(nt, late, 0.05, 0.00004)
    bs = principled(nt, Base_Color=col, Roughness=0.40, Normal=n, Specular_IOR_Level=0.45, Coat_Weight=0.8,
                    Coat_Roughness=mixf(nt, grip, 0.12, 0.08), Coat_IOR=1.5, Coat_Tint=(1.0, 0.94, 0.84))
    nt.links.new(bs.outputs[0], o.inputs["Surface"])
    return mt


def make():
    return dict(head=head(), handle=handle())
