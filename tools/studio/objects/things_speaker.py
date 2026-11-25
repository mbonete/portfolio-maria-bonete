# A compact studio monitor (desk_things.py places two): a 125 x 155 x 200 mm black cabinet with rounded
# edges, a moulded front baffle carrying a 3.5" woofer (woven cone, rubber surround, trim ring), a 1" silk
# dome in a waveguide flared into the baffle, a flared slot port along the bottom and a small power light;
# an amplifier plate on the back, rubber feet. No brand. Local frame: origin under the cabinet's centre,
# front towards -y.
import math
import bmesh
from mathutils import Matrix, Vector
from objects.desk_kit import rrect, ellipse, prism, loft, cylinder, transform, N, out, M, V, mix_rgb, mix_f, maprange, \
    xyz, comb, tex, new_material, shared, principled, plastic, rubber, black_steel
from objects.things_kit import part, T, R, lathe, bx, led, satin, paint, metal, anodized

W, D, H = 0.125, 0.155, 0.200
FOOT = 0.003
YF = -D / 2 - 0.0025          # the baffle's front face
WOOF_Z, TWEET_Z, PORT_Z = 0.083, 0.161, 0.0215
BW, BH, BR = 0.108, 0.194, 0.007   # baffle outline: the cabinet's front is open behind it


def _woven(name):
    """A woven glass-fibre cone, black: a basket weave whose crossing threads catch the light in turn."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, _ = xyz(t, co)
    p = 0.0024
    a = M(t, "SINE", M(t, "MULTIPLY", x, 2 * math.pi / p))
    b = M(t, "SINE", M(t, "MULTIPLY", y, 2 * math.pi / p))
    cell = M(t, "MULTIPLY", M(t, "SINE", M(t, "MULTIPLY", x, math.pi / p)), M(t, "SINE", M(t, "MULTIPLY", y, math.pi / p)))
    over = M(t, "GREATER_THAN", cell, 0.0)
    h = mix_f(t, over, M(t, "ABSOLUTE", a), M(t, "ABSOLUTE", b))
    bump = N(t, "ShaderNodeBump", Strength=0.30, Distance=0.0003, Height=h)
    col = mix_rgb(t, over, (0.016, 0.016, 0.018, 1), (0.030, 0.030, 0.033, 1))
    r = mix_f(t, over, 0.46, 0.34)
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Coat Weight": 0.12, "Coat Roughness": 0.3,
                     "Specular IOR Level": 0.5})
    return m


def _silk(name):
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=4000.0, Detail=1.0), "Factor")
    bump = N(t, "ShaderNodeBump", Strength=0.15, Distance=0.0001, Height=nz)
    principled(t, **{"Base Color": (0.035, 0.035, 0.037, 1), "Roughness": 0.55, "Sheen Weight": 0.8, "Sheen Roughness": 0.3,
                     "Normal": out(bump), "Coat Weight": 0.2, "Coat Roughness": 0.3})
    return m


def baffle(p, mats):
    """The front panel with its three openings: the woofer's round hole, the waveguide's mouth and the slot
    port, its outer rim rounded over and the port's mouth flared."""
    bm = bmesh.new()
    cz = (FOOT + H) / 2
    rr = 0.0022
    steps = 4

    def ring(pts, y):
        return [bm.verts.new((x, y, z)) for x, z in pts]

    def bridge(a, b):
        n = len(a)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))

    # outer rim, rounded from the face back to the full outline, then straight back into the cabinet
    rims = []
    for k in range(steps + 1):
        ang = math.pi / 2 * k / steps
        ins = rr * (1 - math.sin(ang))
        rims.append(ring(rrect(BW - 2 * ins, BH - 2 * ins, BR - ins, 8, 0.0, cz), YF + rr * (1 - math.cos(ang))))
    rims.append(ring(rrect(BW, BH, BR, 8, 0.0, cz), -D / 2 + 0.004))
    for a, b in zip(rims, rims[1:]):
        bridge(a, b)
    # openings in the face
    woof = ring(ellipse(2 * 0.0458, 2 * 0.0458, 96, 0.0, WOOF_Z), YF)
    tw = ring(ellipse(2 * 0.0275, 2 * 0.0275, 72, 0.0, TWEET_Z), YF)
    pw, ph, fl = 0.068, 0.0105, 0.0024
    port = [ring(rrect(pw + 2 * fl * (1 - math.sin(math.pi / 2 * k / 4)), ph + 2 * fl * (1 - math.sin(math.pi / 2 * k / 4)),
                       ph / 2 - 0.0002 + fl * (1 - math.sin(math.pi / 2 * k / 4)), 8, 0.0, PORT_Z),
                 YF + fl * (1 - math.cos(math.pi / 2 * k / 4))) for k in range(5)]
    edges = []
    for lp in (rims[0], woof, tw, port[0]):
        for i in range(len(lp)):
            pair = (lp[i], lp[(i + 1) % len(lp)])
            edges.append(bm.edges.get(pair) or bm.edges.new(pair))
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges, normal=(0, -1, 0))
    # woofer hole wall and the port's flare and tube
    deep = ring(ellipse(2 * 0.0458, 2 * 0.0458, 96, 0.0, WOOF_Z), YF + 0.007)
    bridge(woof, deep)
    for a, b in zip(port, port[1:]):
        bridge(a, b)
    tube = ring(rrect(pw, ph, ph / 2 - 0.0002, 8, 0.0, PORT_Z), YF + 0.030)
    bridge(port[-1], tube)
    bm.faces.new(tube)
    ob = part("speaker baffle", bm, mats, p, sharp=35)
    # the WeightedNormal keeps the flat face flat next to the rounded rims
    wn = ob.modifiers.new("wn", "WEIGHTED_NORMAL")
    wn.keep_sharp = True
    for f in ob.data.polygons:
        if f.center.y > YF + 0.026 and abs(f.normal.y) > 0.9:
            f.material_index = 1
    return ob


def speaker(p):
    cab = plastic("speaker vinyl", (0.011, 0.011, 0.012), 0.52, grain=0.14, scale=0.05, bump=0.05)
    face = plastic("speaker baffle", (0.009, 0.009, 0.010), 0.30, grain=0.04, scale=0.06, bump=0.015)
    dark = paint("port dark", (0.002, 0.002, 0.002), 0.9)
    # cabinet
    bm = prism(rrect(W, D, 0.011, 8), FOOT, H)
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if all(abs(v.co.y + D / 2) < 1e-6 for v in f.verts)], context="FACES")
    part("speaker cabinet", bm, [cab], p, bevel=0.0035, segs=4)
    baffle(p, [face, dark])
    # woofer, its axis along local z out of the baffle
    at = T(0.0, YF, WOOF_Z) @ R(90, "X")
    trim = anodized("speaker trim", (0.07, 0.07, 0.075), 0.28, scale=0.03)
    part("woofer trim", lathe([(0.0473, -0.0030), (0.0473, -0.0004), (0.0469, 0.0006), (0.0461, 0.0011), (0.0452, 0.0011),
                               (0.0445, 0.0005), (0.0442, -0.0012)], 96), [trim], p, sharp=50, at=at)
    sur = [(0.0412 + 0.0031 * math.cos(math.pi * k / 10), -0.0016 + 0.0029 * math.sin(math.pi * k / 10)) for k in range(11)]
    part("woofer surround", lathe(sur, 96), [satin("surround rubber", (0.012, 0.012, 0.013), 0.62, sheen=0.3, bump=0.01)],
         p, sharp=80, at=at)
    cone = [(0.0381 - 0.0216 * k / 10, -0.0018 - 0.0110 * (k / 10) ** 0.75) for k in range(11)]
    part("woofer cone", lathe(cone, 96), [shared("woven cone", _woven)], p, sharp=80, at=at)
    capp = [(0.0166 * math.cos(math.pi / 2 * k / 8), -0.0128 + 0.0066 * math.sin(math.pi / 2 * k / 8)) for k in range(9)]
    capp[-1] = (0.0, capp[-1][1])
    part("dust cap", lathe(capp, 64), [satin("dust cap", (0.012, 0.012, 0.013), 0.22, coat=0.6, bump=0.005)], p, sharp=80,
         at=at)
    part("woofer back", cylinder(0.046, -0.022, -0.020, 48), [dark], p, at=at)
    # tweeter: the waveguide flares from the baffle's face down to a silk dome
    at = T(0.0, YF, TWEET_Z) @ R(90, "X")
    horn = [(0.0275, 0.0), (0.0271, -0.0001), (0.0262, -0.0006), (0.0240, -0.0020), (0.0215, -0.0038), (0.0190, -0.0058),
            (0.0166, -0.0080), (0.0149, -0.0098), (0.0141, -0.0110)]
    part("waveguide", lathe(horn, 72), [plastic("waveguide plastic", (0.010, 0.010, 0.011), 0.20, grain=0.02, scale=0.06,
                                                 bump=0.01)], p, sharp=60, at=at)
    part("tweeter ring", lathe([(0.0141, -0.0110), (0.0141, -0.0104), (0.0137, -0.0101), (0.0131, -0.0103), (0.0128, -0.0112)],
                               64), [trim], p, sharp=60, at=at)
    dome = [(0.0127 * math.cos(math.pi / 2 * k / 8), -0.0114 + 0.0060 * math.sin(math.pi / 2 * k / 8)) for k in range(9)]
    dome[-1] = (0.0, dome[-1][1])
    part("tweeter dome", lathe(dome, 64), [shared("silk dome", _silk)], p, sharp=80, at=at)
    # power light, top right
    part("power light", cylinder(0.0013, YF - 0.0004, YF + 0.001, 20, cx=0.040, cy=0.192, axis="y"),
         [led("speaker light", (0.55, 0.75, 1.0), (0.55, 0.75, 1.0), 1.2, "flat", light=2.0)], p)
    # back: amplifier plate with its heatsink fins, sockets and a level knob
    amp = anodized("amp plate", (0.025, 0.025, 0.028), 0.38, scale=0.05)
    part("amp plate", bx((-0.046, D / 2 - 0.0005, 0.030), (0.046, D / 2 + 0.0025, 0.170), 0.004, "y"), [amp], p, bevel=0.0008,
         segs=2)
    bm = bmesh.new()
    for k in range(7):
        x = -0.036 + k * 0.012
        bx((x - 0.0015, D / 2 + 0.0025, 0.112), (x + 0.0015, D / 2 + 0.0095, 0.165), bm=bm)
    part("amp fins", bm, [amp], p, bevel=0.0005, segs=2)
    for x, z, r in ((-0.022, 0.060, 0.0062), (0.0, 0.060, 0.0062), (0.024, 0.060, 0.0040)):
        part("socket", cylinder(r, D / 2 + 0.0024, D / 2 + 0.0040, 32, cx=x, cy=z, axis="y"), [black_steel()], p, bevel=0.0005,
             segs=2)
        part("socket hole", cylinder(r * 0.55, D / 2 + 0.0040, D / 2 + 0.0042, 24, cx=x, cy=z, axis="y"), [dark], p)
    part("level knob", cylinder(0.0075, D / 2 + 0.0024, D / 2 + 0.0120, 32, cx=0.0, cy=0.090, axis="y"), [plastic()], p,
         bevel=0.0012, segs=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            part("speaker foot", cylinder(0.0085, 0.0, FOOT + 0.0004, 32, cx=sx * 0.045, cy=sy * 0.055), [rubber()], p,
                 bevel=0.0008, segs=2)
