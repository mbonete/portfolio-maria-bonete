# The PC's insides, for tower.py: RGB fans, the front radiator of a 360 mm AIO and its pump head, an ATX
# motherboard with its heatsinks, slots and RAM, and a triple-slot graphics card. Tower-local metres (see
# tower.py): x to the solid right side, y to the back, z up from the desk top. The board stands on the
# right-hand tray facing the glass side (-x); "board coordinates" u run from its rear edge forwards, v from
# its top edge down, h out of its face towards the glass.
import math
import bmesh
from mathutils import Matrix, Vector
from objects.desk_kit import (rrect, ellipse, prism, loft, cylinder, transform, N, out, M, V, mix_rgb, mix_f,
                              maprange, xyz, comb, tex, new_material, shared, principled, powder, powder_edge,
                              plastic, rubber, black_steel)
from objects.things_kit import (CYAN, VIOLET, part, instance, T, R, ring_prism, square_ring, lathe, bx, led, merge,
                                anodized, satin, paint, metal, perf, glass, glass_edge)

FAN_D, FAN_T = 0.120, 0.025

# the motherboard: its face's x, its rear edge's y, its top edge's z
XB, YR, ZT = 0.0850, 0.205, 0.462
# the pump head's centre (board coordinates u, v)
CPU_U, CPU_V = 0.094, 0.085
# the graphics card: front and back ends, inner (slot) and outer edges, the PCB's underside
GPU_Y0, GPU_Y1 = -0.0895, 0.2155
GPU_XI, GPU_XO = 0.074, -0.050
GPU_ZP = 0.3195
# the radiator, behind the front fans
RAD_Y0, RAD_Y1 = -0.1760, -0.1490


def B(u0, u1, v0, v1, h0, h1, r=0.0, bm=None):
    """A box in board coordinates, its corners in the board's plane rounded by r."""
    return bx((XB - h1, YR - u1, ZT - v1), (XB - h0, YR - u0, ZT - v0), r, "x", bm=bm)


def bp(u, v, h=0.0):
    """A board-coordinate point in tower coordinates."""
    return Vector((XB - h, YR - u, ZT - v))


# ---------------------------------------------------------------- materials

def fan_plastic():
    return satin("fan plastic", (0.016, 0.016, 0.018), 0.40, bump_scale=3000.0, bump=0.02)


def blade_plastic():
    return satin("fan blade", (0.008, 0.008, 0.009), 0.28, bump=0.01)


def pad_rubber():
    return satin("fan pad", (0.040, 0.040, 0.044), 0.75, sheen=0.2)


def heatsink():
    return anodized("heatsink", (0.16, 0.165, 0.18), 0.36, scale=0.10, brushed=True)


def machined():
    return metal("machined aluminium", (0.60, 0.61, 0.63), 0.20)


def hole():
    return paint("hole", (0.0012, 0.0012, 0.0013), 0.9)


def _pcb(name):
    """Black solder mask over copper: faint traces show as a slightly lighter, glossier grid of runs."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    br = N(t, "ShaderNodeTexBrick", co, Scale=55.0, Bias=0.0, _offset=0.37, _squash=1.6,
           **{"Mortar Size": 0.004, "Brick Width": 0.9, "Row Height": 0.18})
    lines = M(t, "SUBTRACT", 1.0, out(br, "Fac"))
    vias = out(N(t, "ShaderNodeTexVoronoi", co, Scale=900.0, Randomness=1.0), "Distance")
    via = maprange(t, vias, 0.05, 0.08, 1.0, 0.0)
    via = M(t, "MULTIPLY", via, maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=40.0), "Factor"), 0.55, 0.6, 0.0, 1.0))
    col = mix_rgb(t, M(t, "MULTIPLY", lines, 0.5), (0.016, 0.016, 0.018, 1), (0.035, 0.035, 0.038, 1))
    col = mix_rgb(t, via, col, (0.25, 0.22, 0.16, 1))
    r = mix_f(t, lines, 0.42, 0.30)
    bump = N(t, "ShaderNodeBump", Strength=0.2, Distance=0.0001, Height=lines)
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.5,
                     "Metallic": M(t, "MULTIPLY", via, 0.8)})
    return m


def pcb():
    return shared("pcb", _pcb)


def _radcore(name):
    """A radiator's face: flat coolant tubes every 8.5 mm across, folded fins between them."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    tubef = M(t, "FRACT", M(t, "DIVIDE", x, 0.0085))
    tubes = M(t, "LESS_THAN", M(t, "ABSOLUTE", M(t, "SUBTRACT", tubef, 0.5)), 0.12)
    fins = M(t, "SINE", M(t, "MULTIPLY", z, 2 * math.pi / 0.0015))
    finm = M(t, "MULTIPLY", maprange(t, fins, -1.0, 1.0, 0.0, 1.0), M(t, "SUBTRACT", 1.0, tubes))
    col = mix_rgb(t, finm, (0.004, 0.004, 0.0045, 1), (0.030, 0.030, 0.033, 1))
    col = mix_rgb(t, tubes, col, (0.020, 0.020, 0.022, 1))
    h = M(t, "ADD", M(t, "MULTIPLY", finm, 0.6), M(t, "MULTIPLY", tubes, 1.0))
    bump = N(t, "ShaderNodeBump", Strength=0.8, Distance=0.0006, Height=h)
    principled(t, **{"Base Color": col, "Roughness": 0.45, "Metallic": 0.6, "Normal": out(bump)})
    return m


# ---------------------------------------------------------------- fans

def _blades(n=9, r0=0.0195, r1=0.0572):
    """Nine swept, pitched, cambered blades as thin closed shells."""
    bm = bmesh.new()
    NR, NC = 10, 16
    sweep = 0.40

    def P(s, t, b):
        r = r0 + (r1 - r0) * s
        le = 2 * math.pi * b / n + sweep * s ** 1.4
        span = 0.58 + 0.12 * s
        th = le - span * t
        depth = 0.0150 - 0.0040 * s
        z = depth / 2 - depth * t + 0.0018 * math.sin(math.pi * t)
        return Vector((r * math.cos(th), r * math.sin(th), z))

    for b in range(n):
        top, bot = [], []
        for i in range(NR + 1):
            s = i / NR
            rt, rb = [], []
            for j in range(NC + 1):
                t = j / NC
                p = P(s, t, b)
                ds = P(min(s + 1e-3, 1), t, b) - P(max(s - 1e-3, 0), t, b)
                dt = P(s, min(t + 1e-3, 1), b) - P(s, max(t - 1e-3, 0), b)
                nn = ds.cross(dt).normalized()
                th = (0.0013 - 0.0005 * s) * max(0.3, math.sin(math.pi * t) ** 0.5) / 2
                rt.append(bm.verts.new(p + nn * th))
                rb.append(bm.verts.new(p - nn * th))
            top.append(rt)
            bot.append(rb)
        for i in range(NR):
            for j in range(NC):
                bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]))
                bm.faces.new((bot[i][j], bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j]))
        for i in range(NR):
            for j in (0, NC):
                bm.faces.new((top[i][j], top[i + 1][j], bot[i + 1][j], bot[i][j]))
        for j in range(NC):
            for i in (0, NR):
                bm.faces.new((top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j]))
    return bm


def _ring(r0, r1, z0, z1, seg=96):
    """A small rounded ring (a diffuser), its section a rounded rectangle from r0..r1, z0..z1."""
    cr = min(r1 - r0, z1 - z0) * 0.45
    sec = rrect(r1 - r0, z1 - z0, cr, 3, (r0 + r1) / 2, (z0 + z1) / 2)
    return lathe(sec + [sec[0]], seg)


class Fan:
    """A 120 mm RGB fan, its axis along local z, the intake (blade) side at +z: a moulded frame with open
    corners, a diffuser ring round the bore and one round the hub. The first one builds the meshes; the rest
    share them."""

    def __init__(self, parent, mx, ring_mat, d=FAN_D):
        h = FAN_T / 2
        fl = 0.0038
        rb = d / 2 - 0.0004
        mats = [fan_plastic()]
        sq = square_ring(d, 0.0055, 24)
        bore = ellipse(2 * rb, 2 * rb, 96)
        bm = ring_prism(sq, bore, h - fl, h)
        ring_prism(sq, bore, -h, -h + fl, bm=bm)
        ring_prism(ellipse(2 * (rb + 0.0018), 2 * (rb + 0.0018), 96), bore, -h + fl - 0.0003, h - fl + 0.0003, bm=bm)
        k = d / 2 - 0.0075
        for sx in (-1, 1):
            for sy in (-1, 1):
                cylinder(0.0052, -h + fl - 0.0003, h - fl + 0.0003, 20, bm, sx * k, sy * k)
        self.parts = [part("fan frame", bm, mats, parent, bevel=0.0007, segs=2, at=mx.copy())]
        # rubber pads on the intake corners, each round its screw hole
        bm = bmesh.new()
        for sx in (-1, 1):
            for sy in (-1, 1):
                prism(rrect(0.0135, 0.0135, 0.0035, 4, sx * k, sy * k), h - 0.0002, h + 0.0011, "z", bm)
        self.parts.append(part("fan pads", bm, [pad_rubber()], parent, bevel=0.0004, segs=2, at=mx.copy()))
        bm = bmesh.new()
        for sx in (-1, 1):
            for sy in (-1, 1):
                cylinder(0.0021, h + 0.0009, h + 0.0012, 16, bm, sx * k, sy * k)
        self.parts.append(part("fan holes", bm, [hole()], parent, smooth=False, at=mx.copy()))
        # the light rings: round the bore on the intake face, and round the hub
        self.parts.append(part("fan ring", _ring(rb - 0.0004, rb + 0.0030, h - 0.0010, h + 0.0009), [ring_mat],
                               parent, at=mx.copy()))
        self.parts.append(part("fan hub ring", _ring(0.0168, 0.0203, h - 0.0034, h - 0.0020, 64), [ring_mat],
                               parent, at=mx.copy()))
        # hub: body, a domed cap inside the ring, and the motor's struts behind
        bm = lathe([(0.0, -h + 0.003), (0.0204, -h + 0.003), (0.0206, h - 0.0042), (0.0196, h - 0.0034),
                    (0.0168, h - 0.0034), (0.0, h - 0.0034)], 64)
        self.parts.append(part("fan hub", bm, [blade_plastic()], parent, at=mx.copy()))
        bm = lathe([(0.0, h - 0.0016), (0.0100, h - 0.0018), (0.0150, h - 0.0024), (0.0166, h - 0.0034)], 64)
        self.parts.append(part("fan cap", bm, [satin("fan cap", (0.006, 0.006, 0.007), 0.18, coat=0.5)], parent,
                               at=mx.copy()))
        bm = cylinder(0.0215, -h, -h + 0.0032, 48)
        for a in range(4):
            sb = bx((0.019, -0.0017, -h), (rb + 0.001, 0.0017, -h + 0.0030))
            merge(bm, transform(sb, R(45 + 90 * a, "Z")))
        self.parts.append(part("fan motor", bm, [fan_plastic()], parent, bevel=0.0005, segs=2, at=mx.copy()))
        self.parts.append(part("fan blades", _blades(r1=rb - 0.0021), [blade_plastic()], parent, sharp=50,
                               at=mx.copy()))

    def again(self, parent, mx):
        for ob in self.parts:
            instance(ob.name, ob, parent, mx)


# ---------------------------------------------------------------- radiator and pump

def radiator(p):
    """A 360 mm radiator behind the front fans: a black core of tubes and fins between two end tanks, the
    hoses' fittings on the top tank's back."""
    core = shared("radiator core", _radcore)
    part("radiator core", bx((-0.0595, RAD_Y0 + 0.001, 0.040), (0.0595, RAD_Y1 - 0.001, 0.400)), [core], p,
         bevel=0.0005, segs=1)
    tank = plastic("tank plastic", (0.010, 0.010, 0.011), 0.35, grain=0.05, bump=0.02)
    for z0, z1 in ((0.0255, 0.040), (0.400, 0.4295)):
        part("radiator tank", bx((-0.0610, RAD_Y0, z0), (0.0610, RAD_Y1, z1), 0.004, "y"), [tank], p,
             bevel=0.0018, segs=3)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 0.0595, sx * 0.0612))
        part("radiator side", bx((x0, RAD_Y0 + 0.002, 0.040), (x1, RAD_Y1 - 0.002, 0.400)), [powder(), powder_edge()], p,
             bevel=0.0005, segs=2, bevel_mat=1)
    for x in (0.012, 0.036):
        bm = cylinder(0.0074, RAD_Y1 - 0.0005, RAD_Y1 + 0.004, 32, cx=x, cy=0.415, axis="y")
        part("fitting nut", bm, [black_steel()], p, bevel=0.0008, segs=2)
        bm = cylinder(0.0062, RAD_Y1 + 0.004, RAD_Y1 + 0.016, 32, cx=x, cy=0.415, axis="y")
        part("fitting", bm, [black_steel()], p, bevel=0.0010, segs=2)


def pump(p):
    """The AIO's pump head on the CPU: a round housing on its retention ring, a halo of light round the rim
    and three more rings under a smoked cover (an infinity mirror), two swivel fittings on its front."""
    c = bp(CPU_U, CPU_V)
    mx = T(*c) @ R(-90, "Y")                      # local z out of the board, towards the glass
    bm = cylinder(0.0360, 0.0003, 0.0040, 64)
    part("pump bracket", bm, [black_steel()], p, bevel=0.0008, segs=2, at=mx)
    for a in range(4):
        q = Matrix.Rotation(math.radians(45 + 90 * a), 4, "Z")
        bm = transform(cylinder(0.0042, 0.004, 0.0085, 6), q @ T(0.0332, 0.0, 0.0))
        part("pump thumb nut", bm, [black_steel()], p, bevel=0.0006, segs=2, at=mx)
    body = anodized("pump body", (0.022, 0.022, 0.025), 0.30, scale=0.05, brushed=False)
    bm = lathe([(0.0, 0.0040), (0.0315, 0.0040), (0.0330, 0.0052), (0.0336, 0.0080), (0.0336, 0.0350),
                (0.0332, 0.0372), (0.0322, 0.0386), (0.0300, 0.0390), (0.0, 0.0390)], 96)
    part("pump body", bm, [body], p, sharp=40, at=mx)
    part("pump halo", _ring(0.0300, 0.0325, 0.0383, 0.0398), [led("rgb ring")], p, at=mx)
    for k, (r, z, s) in enumerate(((0.0262, 0.0386, 3.0), (0.0222, 0.0380, 1.4), (0.0185, 0.0374, 0.6))):
        part("pump mirror ring", _ring(r - 0.0010, r + 0.0006, z - 0.0005, z),
             [led(f"pump ring {k}", strength=s * 0.6, light=s * 30.0)], p, at=mx)
    part("pump cover", cylinder(0.0299, 0.0392, 0.0412, 96),
         [glass("smoked cover", 0.03, 0.03, frit=0.0, tint=(0.34, 0.34, 0.36), corner=0.0)], p, bevel=0.0007,
         segs=2, at=mx)
    part("pump floor", cylinder(0.0290, 0.0360, 0.0368, 64), [satin("mirror floor", (0.002, 0.002, 0.002), 0.08)],
         p, at=mx)
    # fittings: out of the housing's front (-y), then swivelling towards the glass
    ends = []
    for dz in (0.012, -0.012):
        base = mx @ Vector((dz, -0.0325, 0.0200))
        stub = cylinder(0.0060, 0.0, 0.0085, 32, axis="y")
        transform(stub, T(base.x, base.y, base.z) @ R(180, "Z"))
        part("pump fitting", stub, [black_steel()], p, bevel=0.0008, segs=2)
        elbow = Vector((base.x, base.y - 0.0105, base.z))
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.0068)
        transform(bm, T(*elbow))
        part("pump swivel", bm, [black_steel()], p)
        bm = cylinder(0.0060, 0.0, 0.0140, 32, axis="x")
        transform(bm, T(elbow.x, elbow.y, elbow.z) @ R(180, "Z"))
        part("pump fitting", bm, [black_steel()], p, bevel=0.0008, segs=2)
        ends.append(Vector((elbow.x - 0.0140, elbow.y, elbow.z)))
    return ends


# ---------------------------------------------------------------- motherboard

def finned(u0, u1, v0, v1, h, fins, along_u, mats, p, name):
    """A heatsink: a solid base and a row of fins, their machined tops catching the light."""
    base = 0.35 * h
    bm = B(u0, u1, v0, v1, 0.0, base, 0.0015)
    n = fins
    if along_u:
        w = (u1 - u0) / n
        for i in range(n):
            B(u0 + i * w + 0.0006, u0 + (i + 1) * w - 0.0006, v0, v1, base - 0.0005, h, 0.0004, bm)
    else:
        w = (v1 - v0) / n
        for i in range(n):
            B(u0, u1, v0 + i * w + 0.0006, v0 + (i + 1) * w - 0.0006, base - 0.0005, h, 0.0004, bm)
    return part(name, bm, mats, p, bevel=0.0005, segs=2, bevel_mat=1)


def motherboard(p):
    hs = [heatsink(), machined()]
    part("pcb", B(0.0, 0.244, 0.0, 0.305, -0.0016, 0.0, 0.002), [pcb()], p, bevel=0.0004, segs=2)
    # rear I/O cover, a plastic shell with a brushed inset
    shell = plastic("io cover plastic", (0.013, 0.013, 0.014), 0.38, grain=0.05, bump=0.02)
    bm = loft([(rrect(0.030, 0.166, 0.004, 4, 0.0, 0.0), 0.0), (rrect(0.030, 0.166, 0.004, 4, 0.0, 0.0), 0.022),
               (rrect(0.024, 0.160, 0.003, 4, 0.0015, 0.0), 0.031)], "z")
    transform(bm, T(*bp(0.015, 0.087)) @ R(-90, "Y") @ R(90, "Z"))
    part("io cover", bm, [shell], p, bevel=0.0012, segs=3)
    part("io inset", B(0.006, 0.020, 0.020, 0.150, 0.0305, 0.0322, 0.0015), [anodized("dark brushed", (0.05, 0.05, 0.055), 0.30, scale=0.08, brushed=True)],
         p, bevel=0.0004, segs=2)
    # VRM heatsinks round the socket's top and rear, joined by a heatpipe
    finned(0.058, 0.140, 0.006, 0.034, 0.028, 9, True, hs, p, "vrm heatsink")
    finned(0.033, 0.058, 0.040, 0.142, 0.028, 10, False, hs, p, "vrm heatsink")
    bm = cylinder(0.0028, YR - 0.112, YR - 0.045, 24, cx=XB - 0.0305, cy=ZT - 0.024, axis="y")
    part("heatpipe", bm, [metal("copper nickel", (0.55, 0.53, 0.52), 0.22)], p)
    # CPU socket frame under the pump
    part("socket frame", B(CPU_U - 0.038, CPU_U + 0.038, CPU_V - 0.042, CPU_V + 0.042, 0.0, 0.0035, 0.003),
         [metal("socket steel", (0.42, 0.42, 0.44), 0.35)], p, bevel=0.0006, segs=2)
    # EPS power connector on the top edge
    part("eps socket", B(0.034, 0.056, 0.002, 0.013, 0.0, 0.012, 0.0008), [plastic()], p, bevel=0.0005, segs=2)
    # DIMM slots and four RAM sticks
    slot = satin("slot plastic", (0.012, 0.012, 0.013), 0.48)
    latch = satin("latch plastic", (0.020, 0.020, 0.022), 0.40)
    us = (0.152, 0.162, 0.176, 0.186)
    for u in us:
        part("dimm slot", B(u - 0.0031, u + 0.0031, 0.020, 0.164, 0.0, 0.0075, 0.0008), [slot], p, bevel=0.0005, segs=2)
        part("dimm latch", B(u - 0.0036, u + 0.0036, 0.164, 0.171, 0.0, 0.0105, 0.0010), [latch], p, bevel=0.0006, segs=2)
    ram = ram_stick(p, T(*bp(us[0], 0.092)))
    for u in us[1:]:
        for ob in ram:
            instance(ob.name, ob, p, T(*bp(u, 0.092)))
    # PCIe slots: the armoured x16 for the card and a second below
    armour = metal("slot armour", (0.62, 0.62, 0.64), 0.28)
    for v in (0.142, 0.223):
        part("pcie slot", B(0.010, 0.100, v - 0.0040, v + 0.0040, 0.0, 0.0110, 0.0008), [slot], p, bevel=0.0005, segs=2)
        part("pcie armour", B(0.0095, 0.1005, v - 0.0046, v + 0.0046, 0.0105, 0.0116, 0.0008), [armour], p,
             bevel=0.0003, segs=1)
        part("pcie latch", B(0.100, 0.110, v - 0.0040, v + 0.0040, 0.0, 0.0125, 0.0010), [latch], p, bevel=0.0005, segs=2)
    # M.2 heatsink between the socket and the card, and the chipset's big plate
    finned(0.032, 0.118, 0.123, 0.137, 0.008, 1, True, hs, p, "m2 heatsink")
    bm = B(0.120, 0.236, 0.236, 0.296, 0.0, 0.0085, 0.006)
    part("chipset heatsink", bm, hs, p, bevel=0.0012, segs=3, bevel_mat=1)
    part("chipset stripe", B(0.128, 0.228, 0.251, 0.2535, 0.0084, 0.0090, 0.0006), [machined()], p, bevel=0.0002, segs=1)
    part("chipset stripe", B(0.128, 0.200, 0.2565, 0.2590, 0.0084, 0.0090, 0.0006), [machined()], p, bevel=0.0002, segs=1)
    # 24-pin power socket at the front edge, SATA ports below it
    part("atx socket", B(0.229, 0.244, 0.108, 0.162, 0.0, 0.0130, 0.0010), [plastic()], p, bevel=0.0006, segs=2)
    for k in range(3):
        part("sata port", B(0.232, 0.244, 0.200 + k * 0.012, 0.209 + k * 0.012, 0.0, 0.0105, 0.0008), [plastic()], p,
             bevel=0.0005, segs=2)
    # audio corner: a cover and a row of gold capacitors
    part("audio cover", B(0.003, 0.050, 0.232, 0.300, 0.0, 0.0045, 0.004), [shell], p, bevel=0.0010, segs=2)
    gold = metal("cap gold", (0.80, 0.58, 0.25), 0.30)
    for k in range(5):
        u, v = 0.060 + (k % 3) * 0.010, 0.270 + (k // 3) * 0.011
        bm = cylinder(0.0032, XB - 0.0095, XB, 24, cx=YR - u, cy=ZT - v, axis="x")
        part("audio cap", bm, [gold], p, bevel=0.0006, segs=2)
    # front-panel and fan headers along the bottom edge
    hdr = plastic()
    for u0, u1 in ((0.090, 0.112), (0.122, 0.140), (0.160, 0.185), (0.200, 0.214)):
        part("header", B(u0, u1, 0.291, 0.300, 0.0, 0.0085, 0.0005), [hdr], p, bevel=0.0004, segs=1)
    # small parts scattered on the bare board: chips and capacitors
    import random
    rnd = random.Random(11)
    chip = satin("chip", (0.010, 0.010, 0.011), 0.30)
    spots = [(0.065, 0.150, 0.150, 0.170), (0.110, 0.230, 0.180, 0.228), (0.010, 0.050, 0.180, 0.225),
             (0.200, 0.238, 0.020, 0.100), (0.060, 0.115, 0.236, 0.262)]
    bm = bmesh.new()
    for u0, u1, v0, v1 in spots:
        for _ in range(9):
            w, d = rnd.choice(((0.004, 0.004), (0.006, 0.003), (0.002, 0.001), (0.003, 0.0015)))
            u, v = rnd.uniform(u0, u1 - w), rnd.uniform(v0, v1 - d)
            B(u, u + w, v, v + d, 0.0, rnd.choice((0.0008, 0.0012, 0.0015)), 0.0002, bm)
    part("chips", bm, [chip], p, bevel=0.0002, segs=1)
    # mounting screws
    for u, v in ((0.005, 0.240), (0.140, 0.008), (0.239, 0.008), (0.239, 0.175), (0.140, 0.225), (0.239, 0.296),
                 (0.054, 0.296)):
        bm = cylinder(0.0034, XB - 0.0022, XB, 24, cx=YR - u, cy=ZT - v, axis="x")
        part("board screw", bm, [black_steel()], p, bevel=0.0006, segs=2)


def ram_stick(p, mx):
    """A DIMM with a black heat spreader and a light bar along its top edge. Built along local z (its
    length), local -x out of the board."""
    sp = [anodized("ram spreader", (0.06, 0.06, 0.066), 0.32, scale=0.06, brushed=True), machined()]
    obs = []
    bm = bx((-0.0385, -0.0034, -0.0665), (-0.004, 0.0034, 0.0665), 0.0012, "x")
    obs.append(part("ram spreader", bm, sp, p, bevel=0.0006, segs=2, bevel_mat=1, at=mx))
    bm = bx((-0.0405, -0.0030, -0.0655), (-0.0380, 0.0030, 0.0655), 0.0010, "x")
    obs.append(part("ram cap", bm, [satin("ram cap", (0.015, 0.015, 0.017), 0.35)], p, bevel=0.0004, segs=2,
                    at=mx))
    bm = bx((-0.0450, -0.0026, -0.0640), (-0.0400, 0.0026, 0.0640), 0.0020, "x")
    obs.append(part("ram light", bm, [led("ram light", VIOLET, CYAN, 1.1, "z", -0.064, 0.064)], p, bevel=0.0010,
                    segs=3, at=mx))
    return obs


# ---------------------------------------------------------------- graphics card

def gpu(p):
    """A triple-slot card hanging from the top x16 slot: PCB, a brushed backplate with a vented end, an
    angular shroud whose outer edge carries a light bar and shows its fins at the front, two 8-pin plugs."""
    y0, y1, xi, xo, zp = GPU_Y0, GPU_Y1, GPU_XI, GPU_XO, GPU_ZP
    part("gpu pcb", bx((xo + 0.004, y0 + 0.004, zp), (xi, y1 - 0.001, zp + 0.0016)), [pcb()], p, bevel=0.0003, segs=1)
    bpm = [anodized("backplate", (0.10, 0.10, 0.11), 0.30, scale=0.10, brushed=True), machined()]
    part("gpu backplate", bx((xo + 0.0005, y0 + 0.0005, zp + 0.0032), (xi - 0.004, y1 - 0.003, zp + 0.0057), 0.004),
         bpm, p, bevel=0.0009, segs=2, bevel_mat=1)
    part("gpu backplate vent", bx((xo + 0.008, y0 + 0.010, zp + 0.0056), (xi - 0.016, y0 + 0.070, zp + 0.0059), 0.006),
         [perf("backplate vent", 0.0040, 0.0014, "xy", (0.04, 0.04, 0.044), 0.35)], p, bevel=0.0003, segs=1)
    # shroud: the body, then its outer edge's angular panels
    shroud = plastic("gpu shroud", (0.035, 0.035, 0.039), 0.34, grain=0.06, bump=0.02)
    zb = zp - 0.0525
    part("gpu shroud", bx((xo, y0, zb), (xi - 0.002, y1 - 0.004, zp - 0.0008), 0.010), [shroud], p, bevel=0.0018, segs=3)
    dark = satin("gpu panel", (0.008, 0.008, 0.009), 0.25, coat=0.3)
    # outer edge (x = xo, faces the glass): a raised panel cut away at the front for the fins
    pnl = [(y0 + 0.075, zb + 0.004), (y1 - 0.030, zb + 0.004), (y1 - 0.018, zb + 0.020), (y1 - 0.018, zp - 0.010),
           (y0 + 0.090, zp - 0.010)]
    bm = prism(pnl, xo - 0.0030, xo + 0.0005, "x")
    part("gpu edge panel", bm, [dark], p, bevel=0.0010, segs=2, sharp=20)
    # light bar along the panel's top
    part("gpu light", bx((xo - 0.0042, y0 + 0.092, zp - 0.0135), (xo - 0.0026, y1 - 0.032, zp - 0.0105), 0.0006),
         [led("gpu light", VIOLET, CYAN, 1.1, "y", y0 + 0.09, y1 - 0.03)], p, bevel=0.0005, segs=2)
    # fins at the front, behind a cut-out of the edge
    bm = bmesh.new()
    for k in range(22):
        y = y0 + 0.008 + k * 0.0029
        bx((xo + 0.0015, y, zb + 0.006), (xo + 0.040, y + 0.0007, zp - 0.006), bm=bm)
    part("gpu fins", bm, [heatsink()], p)
    part("gpu fin shadow", bx((xo + 0.040, y0 + 0.006, zb + 0.004), (xo + 0.042, y0 + 0.074, zp - 0.004)), [hole()], p)
    # bracket at the back
    part("gpu bracket", bx((xo - 0.002, y1 - 0.0005, zb - 0.004), (xi + 0.010, y1 + 0.0010, zp + 0.010)),
         [powder(), powder_edge()], p, bevel=0.0004, segs=1, bevel_mat=1)
    # power plugs in the edge, near the middle
    plugs = []
    for yc in (0.004, 0.027):
        part("pcie plug", bx((xo - 0.016, yc - 0.0105, zp - 0.0195), (xo + 0.006, yc + 0.0105, zp - 0.0090), 0.0012, "x"),
             [plastic()], p, bevel=0.0006, segs=2)
        plugs.append(yc)
    return plugs
