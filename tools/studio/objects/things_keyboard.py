# The keyboard, its felt mat and the mouse (desk_things.py places them). A full-size 104-key mechanical
# keyboard with floating keys: a brushed dark aluminium top plate on a black shell, sculpted dark PBT keycaps
# (row heights and tilts, cylindrical dishes) with light grey QWERTY legends that follow the dish, a switch
# under each key whose violet LED leaks out under the caps, a diffuser band round the shell's foot for the
# underglow, a volume roller above the numpad. The mat: 4 mm wool felt with soft cut edges. The mouse: a
# smooth symmetric shell with its button split, a ribbed wheel and side buttons. No brand.
# Local frames: origin on the surface each thing stands on, front towards -y.
import math
import bmesh
from mathutils import Matrix, Vector
from objects.desk_kit import rrect, ellipse, prism, loft, cylinder, transform, N, out, M, V, mix_rgb, mix_f, maprange, \
    xyz, comb, tex, new_material, shared, principled, plastic, rubber, black_steel
from objects.things_kit import (part, T, R, lathe, bx, led, satin, paint, metal, anodized, text_mesh, mesh_bm, merge,
                                ring_prism, rounded_slab, VIOLET, CYAN)

U = 0.01905
KW, KD = 0.4400, 0.1370               # case footprint
TILT = math.degrees(math.atan(0.007 / KD))
Z_PLATE = 0.0190                       # plate top at the case's middle
DECK = Matrix.Translation((0, 0, Z_PLATE)) @ Matrix.Rotation(math.radians(TILT), 4, "X")
CAP_Z = 0.0052                         # keycap skirts above the plate

# row profiles: keycap height, top tilt (degrees, + towards the typist)
ROWS = {0: (0.0104, 7.0), 1: (0.0104, 7.0), 2: (0.0090, 3.5), 3: (0.0085, 0.0), 4: (0.0090, -4.0), 5: (0.0090, -4.0)}

MODS = {"Esc", "Tab", "Caps Lock", "Shift", "Ctrl", "Fn", "Alt", "Menu", "Backspace", "Enter", "PrtSc", "ScrLk", "Pause",
        "Ins", "Home", "PgUp", "Del", "End", "PgDn", "Num", "up", "down", "left", "right"}


def layout():
    """Every key: (row, x in units from the left edge, width, height in units, legend or (shift, main))."""
    keys = []

    def run(row, x, items):
        for it in items:
            if isinstance(it, (int, float)):
                x += it
                continue
            lab, w = it if isinstance(it, tuple) and len(it) == 2 and isinstance(it[1], (int, float)) else (it, 1.0)
            keys.append((row, x, w, 1.0, lab))
            x += w
        return x

    run(0, 0, ["Esc", 1.0, "F1", "F2", "F3", "F4", 0.5, "F5", "F6", "F7", "F8", 0.5, "F9", "F10", "F11", "F12", 0.25,
               "PrtSc", "ScrLk", "Pause"])
    nums = [("~", "`"), ("!", "1"), ("@", "2"), ("#", "3"), ("$", "4"), ("%", "5"), ("^", "6"), ("&", "7"), ("*", "8"),
            ("(", "9"), (")", "0"), ("_", "-"), ("+", "=")]
    run(1, 0, [(n, 1.0) for n in nums] + [("Backspace", 2.0), 0.25, "Ins", "Home", "PgUp", 0.25, "Num", "/", "*", "-"])
    run(2, 0, [("Tab", 1.5)] + list("QWERTYUIOP") + [(("{", "["), 1.0), (("}", "]"), 1.0), (("|", "\\"), 1.5), 0.25,
                                                      "Del", "End", "PgDn", 0.25, "7", "8", "9"])
    run(3, 0, [("Caps Lock", 1.75)] + list("ASDFGHJKL") + [((":", ";"), 1.0), (('"', "'"), 1.0), ("Enter", 2.25), 3.5,
                                                         "4", "5", "6"])
    run(4, 0, [("Shift", 2.25)] + list("ZXCVBNM") + [(("<", ","), 1.0), ((">", "."), 1.0), (("?", "/"), 1.0),
                                                      ("Shift", 2.75), 1.25, "up", 1.25, "1", "2", "3"])
    run(5, 0, [("Ctrl", 1.25), ("Fn", 1.25), ("Alt", 1.25), (" ", 6.25), ("Alt", 1.25), ("Fn", 1.25), ("Menu", 1.25),
               ("Ctrl", 1.25), 0.25, "left", "down", "right", 0.25, ("0", 2.0), "."])
    keys.append((2, 21.5, 1.0, 2.0, "+"))           # tall numpad keys
    keys.append((4, 21.5, 1.0, 2.0, "Enter"))
    return keys


def row_y(r):
    """Deck-frame y of a row's centre (rows run back to front)."""
    y0 = 3.2 * U - 0.5 * U
    return y0 if r == 0 else y0 - 0.4 * U - r * U


def key_centre(row, x, w, hgt):
    left = -22.5 * U / 2
    cx = left + (x + w / 2) * U
    cy = row_y(row) if hgt == 1 else (row_y(row) + row_y(row + 1)) / 2
    return cx, cy


class Cap:
    """One keycap shape: its outline lofted up to a dished, tilted top; top_point() maps a point of the top's
    plane onto that surface (for legends)."""

    def __init__(self, wu, hu, row):
        self.h, self.tilt = ROWS[row]
        self.bw, self.bd = wu * U - 0.0011, hu * U - 0.0011
        self.tw, self.td = self.bw - 0.0060, self.bd - 0.0060
        self.ty = 0.0006
        self.depth = 0.0 if wu > 3 else (0.00055 if wu <= 1.25 else 0.00035)
        self.rot = Matrix.Rotation(math.radians(self.tilt), 3, "X")

    def top_point(self, x, y, lift=0.0):
        u = max(-1.0, min(1.0, 2 * x / self.tw))
        z = self.h - self.depth * (1 - u * u) + lift
        p = Vector((x, y - self.ty, z - self.h))
        p = self.rot @ p
        return Vector((p.x, p.y + self.ty, p.z + self.h))

    def mesh(self):
        bm = bmesh.new()
        seg = 4
        secs = [rrect(self.bw, self.bd, 0.0010, seg), rrect(self.bw - 0.0006, self.bd - 0.0006, 0.0012, seg)]
        zs = [0.0, 0.35 * self.h]
        rings = []
        for pts, z in zip(secs, zs):
            rings.append([bm.verts.new((x, y, z)) for x, y in pts])
        # just under the top: a ring a little wider, then the top's rim, then rings in towards the middle
        topo = rrect(self.tw, self.td, 0.0019, seg, 0.0, self.ty)
        under = rrect(self.tw + 0.0009, self.td + 0.0009, 0.0023, seg, 0.0, self.ty)
        rings.append([bm.verts.new(self.top_point(x, y, -0.0006)) for x, y in under])
        for k, s in enumerate((1.0, 0.85, 0.6, 0.35, 0.12)):
            rings.append([bm.verts.new(self.top_point(x * s, (y - self.ty) * s + self.ty)) for x, y in topo])
        n = len(rings[0])
        for a, b in zip(rings, rings[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((a[i], a[j], b[j], b[i]))
        c = bm.verts.new(self.top_point(0.0, self.ty))
        last = rings[-1]
        for i in range(n):
            bm.faces.new((last[i], last[(i + 1) % n], c))
        bm.faces.new(rings[0][::-1])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm


def arrow(direction, size):
    """An arrow legend as a mesh (the built-in font has no arrows): a short stem and a head."""
    bm = bmesh.new()
    s = size
    pts = [(-0.10 * s, -0.45 * s), (0.10 * s, -0.45 * s), (0.10 * s, 0.05 * s), (0.30 * s, 0.05 * s), (0.0, 0.45 * s),
           (-0.30 * s, 0.05 * s), (-0.10 * s, 0.05 * s)]
    vs = [bm.verts.new((x, y, 0.0)) for x, y in pts]
    bm.faces.new(vs)
    ang = {"up": 0, "left": 90, "down": 180, "right": 270}[direction]
    transform(bm, Matrix.Rotation(math.radians(ang), 4, "Z"))
    return bm


def legend_bm(lab, w):
    """The legend(s) for a key, flat, centred on the key top."""
    bm = bmesh.new()

    def add(text, size, dx, dy, align="CENTER"):
        b = mesh_bm(text_mesh(text, size, align=align))
        transform(b, T(dx, dy, 0))
        merge(bm, b)

    if isinstance(lab, tuple):
        add(lab[0], 0.0034, 0.0, 0.0027)
        add(lab[1], 0.0034, 0.0, -0.0025)
    elif lab in ("up", "down", "left", "right"):
        merge(bm, arrow(lab, 0.0052))
    elif lab == " ":
        pass
    elif len(lab) == 1:
        add(lab, 0.0052 if lab.isalpha() else 0.0044, 0.0, 0.0006)
    elif lab.startswith("F") and lab[1:].isdigit():
        add(lab, 0.0032, 0.0, 0.0006)
    else:
        add(lab, 0.0026 if len(lab) > 4 else 0.0030, 0.0, 0.0006)
    return bm


def _pbt(name, colour):
    """Dye-sublimated-look PBT: a dry, fine-grained matte with a little sheen."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=9000.0, Detail=2.0), "Factor")
    var = out(N(t, "ShaderNodeTexNoise", co, Scale=60.0, Detail=2.0), "Factor")
    bump = N(t, "ShaderNodeBump", Strength=0.12, Distance=0.00008, Height=nz)
    r = M(t, "ADD", 0.68, maprange(t, var, 0.3, 0.7, -0.05, 0.05))
    principled(t, **{"Base Color": (*colour, 1), "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.32})
    return m


def keyboard(p):
    alu = anodized("keyboard plate", (0.040, 0.040, 0.045), 0.32, scale=0.12, brushed=True)
    edge = metal("keyboard chamfer", (0.55, 0.55, 0.57), 0.22)
    shell = plastic("keyboard shell", (0.012, 0.012, 0.013), 0.42, grain=0.08, scale=0.05, bump=0.03)
    # the shell, its top sloping with the plate
    bm = prism(rrect(KW, KD, 0.0075, 8), 0.0026, 0.010)
    for v in bm.verts:
        if v.co.z > 0.005:
            v.co.z = Z_PLATE - 0.0015 + v.co.y * math.tan(math.radians(TILT))
    part("keyboard shell", bm, [shell], p, bevel=0.0022, segs=4)
    bm = prism(rrect(KW - 0.0030, KD - 0.0030, 0.0062, 8), -0.0015, 0.0)
    transform(bm, DECK)
    part("keyboard plate", bm, [alu, edge], p, bevel=0.0006, segs=2, bevel_mat=1)
    # underglow: a diffuser band round the shell's foot
    o = rrect(KW + 0.0004, KD + 0.0004, 0.0077, 8)
    i = rrect(KW - 0.0030, KD - 0.0030, 0.0062, 8)
    part("underglow", ring_prism(o, i, 0.0019, 0.0030), [led("underglow", VIOLET, VIOLET, 0.6, "flat", light=55.0)], p,
         bevel=0.0004, segs=2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            part("keyboard foot", cylinder(0.0065, 0.0, 0.0024, 32, cx=sx * 0.195, cy=sy * 0.055), [rubber()], p,
                 bevel=0.0006, segs=2)
    # keycaps, switches with their LEDs, legends
    alpha = shared("pbt alpha", lambda n: _pbt(n, (0.011, 0.011, 0.012)))
    modc = shared("pbt mod", lambda n: _pbt(n, (0.0055, 0.0055, 0.0062)))
    ink = paint("legend ink", (0.48, 0.48, 0.50), 0.55)
    caps = {}
    bms = {"a": bmesh.new(), "m": bmesh.new()}
    sw, leds, legs = bmesh.new(), bmesh.new(), bmesh.new()
    for row, x, w, hgt, lab in layout():
        key = (w, hgt, row)
        if key not in caps:
            caps[key] = Cap(w, hgt, row)
        cap = caps[key]
        cx, cy = key_centre(row, x, w, hgt)
        mx = DECK @ T(cx, cy, CAP_Z)
        cb = cap.mesh()
        transform(cb, mx)
        kind = "m" if (lab if isinstance(lab, str) else "") in MODS else "a"
        merge(bms[kind], cb)
        # the switch under it (and one each side for long keys' stabilisers)
        offs = [0.0] if w < 2 else [-(w * U / 2 - 0.012), 0.0, (w * U / 2 - 0.012)]
        if hgt > 1:
            offs = [0.0]
        for ox in offs:
            s = bx((cx + ox - 0.0070, cy - 0.0070, 0.0), (cx + ox + 0.0070, cy + 0.0070, 0.0026), 0.0010)
            merge(sw, transform(s, DECK))
            if ox == 0.0:
                l = bx((cx - 0.0066, cy - 0.0066, 0.0026), (cx + 0.0066, cy + 0.0066, 0.0046), 0.0012)
                merge(leds, transform(l, DECK))
        lb = legend_bm(lab, w)
        for v in lb.verts:
            v.co = mx @ cap.top_point(v.co.x, v.co.y, 0.00004)
        merge(legs, lb)
    part("keycaps", bms["a"], [alpha], p, sharp=55)
    part("keycaps mod", bms["m"], [modc], p, sharp=55)
    part("switches", sw, [satin("switch housing", (0.020, 0.020, 0.023), 0.30)], p, bevel=0.0003, segs=1)
    part("switch tops", leds, [led("key glow", VIOLET, VIOLET, 0.55, "flat", light=40.0)], p, bevel=0.0003, segs=1)
    part("legends", legs, [ink], p, smooth=False)
    # above the numpad: three indicator lights and a volume roller
    for k in range(3):
        x = -22.5 * U / 2 + (18.75 + k * 0.6) * U
        part("indicator", transform(bx((x - 0.0016, row_y(0) - 0.0008, 0.0), (x + 0.0016, row_y(0) + 0.0008, 0.0003), 0.0006),
                                    DECK),
             [led("indicator on", (0.9, 0.85, 1.0), (0.9, 0.85, 1.0), 1.0, "flat", light=1.0) if k == 0 else
              paint("indicator off", (0.05, 0.05, 0.055), 0.2)], p)
    xr = -22.5 * U / 2 + 21.6 * U
    part("roller well", transform(prism(rrect(0.0230, 0.0120, 0.0040, 6, xr, row_y(0)), -0.0003, 0.0006), DECK),
         [paint("well", (0.004, 0.004, 0.005), 0.6)], p)
    knurl = shared("knurled alu", _knurl)
    part("volume roller", cylinder(0.0062, -0.0095, 0.0095, 48, axis="x"), [knurl], p, bevel=0.0006, segs=2,
         at=DECK @ T(xr, row_y(0), 0.0040))


def _knurl(name):
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    a = M(t, "ARCTAN2", z, y)
    h = M(t, "ABSOLUTE", M(t, "SINE", M(t, "MULTIPLY", a, 40.0)))
    bump = N(t, "ShaderNodeBump", Strength=0.6, Distance=0.0003, Height=h)
    principled(t, **{"Base Color": (0.45, 0.45, 0.47, 1), "Metallic": 1.0, "Roughness": 0.3, "Normal": out(bump)})
    return m


# ---------------------------------------------------------------- mat

def _felt(name):
    """Wool felt, charcoal: the scan's fibrous grain at its real scale, matte, with a soft sheen."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    v = V(t, "SCALE", co, scale=1 / 0.06)
    col = tex(t, "ambientcg/Fabric034/Fabric034_2K-JPG_Color.jpg", v, True, box=0.2)
    disp = tex(t, "ambientcg/Fabric034/Fabric034_2K-JPG_Displacement.jpg", v, False, box=0.2)
    lum = out(N(t, "ShaderNodeRGBToBW", Color=out(col)))
    base = mix_rgb(t, maprange(t, lum, 0.3, 0.8, 0.0, 1.0), (0.008, 0.008, 0.009, 1), (0.030, 0.030, 0.033, 1))
    blot = out(N(t, "ShaderNodeTexNoise", co, Scale=5.0, Detail=3.0), "Factor")
    base = mix_rgb(t, maprange(t, blot, 0.35, 0.65, 0.0, 0.25), base, (0.05, 0.05, 0.055, 1))
    fuzz = out(N(t, "ShaderNodeTexNoise", co, Scale=3000.0, Detail=3.0, Roughness=0.7), "Factor")
    h = M(t, "ADD", out(disp), M(t, "MULTIPLY", fuzz, 0.6))
    bump = N(t, "ShaderNodeBump", Strength=0.9, Distance=0.0005, Height=h)
    principled(t, **{"Base Color": base, "Roughness": 0.95, "Normal": out(bump), "Sheen Weight": 0.35, "Sheen Roughness": 0.6,
                     "Sheen Tint": (0.55, 0.55, 0.6, 1), "Specular IOR Level": 0.25})
    return m


def mat(p, w=0.80, d=0.30):
    felt = shared("felt", _felt)
    part("desk mat", rounded_slab(rrect(w, d, 0.012, 8), 0.0, 0.0040, 0.0013, steps=3), [felt], p, sharp=50)


# ---------------------------------------------------------------- mouse

MOUSE_L, MOUSE_W, MOUSE_H = 0.124, 0.063, 0.038


def _mouse_profile(t):
    """Plan half-width and height of the shell at t (0 at the back, 1 at the front)."""
    hw = 0.0300 + 0.0016 * math.sin(math.pi * min(1.0, t * 1.15)) - 0.0010 * math.sin(2 * math.pi * t)
    h = 0.010 + 0.028 * math.sin(math.pi * (0.06 + 0.82 * t)) ** 0.75
    f = 1.0
    if t < 0.10:
        f = math.sqrt(max(0.0, 1 - ((0.10 - t) / 0.10) ** 2))
    elif t > 0.92:
        f = math.sqrt(max(0.0, 1 - ((t - 0.92) / 0.08) ** 2))
    return hw * f, h * (0.45 + 0.55 * f)


def _mouse_y(t):
    return MOUSE_L / 2 - t * MOUSE_L


def mouse(p):
    """A symmetric mouse, 124 x 63 x 38 mm: a lofted soft-touch shell (its hump behind the middle, a blunt
    rounded nose), the button split and the buttons' seam cut in, a ribbed wheel in its slot, two side
    buttons and PTFE feet."""
    shell = shared("mouse shell", _mouse_shell)
    n, m = 40, 32
    bm = bmesh.new()
    rings = []
    for k in range(n + 1):
        t = k / n
        hw, h = _mouse_profile(t)
        y = _mouse_y(t)
        pts = []
        for j in range(m + 1):
            a = math.pi * j / m
            c, s_ = math.cos(a), math.sin(a)
            x = hw * math.copysign(abs(c) ** 0.55, c)
            z = 0.0012 + h * (abs(s_) ** 0.8)
            pts.append((x, z))
        rings.append([bm.verts.new((x, y, z)) for x, z in pts])
    for a_, b_ in zip(rings, rings[1:]):
        for j in range(m):
            bm.faces.new((a_[j], a_[j + 1], b_[j + 1], b_[j]))
    bot = [r[0] for r in rings] + [r[-1] for r in reversed(rings)]
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bot = [v for v in bot if v.is_valid]
    seen = []
    for v in bot:
        if v not in seen:
            seen.append(v)
    bm.faces.new(seen)
    ob = part("mouse shell", bm, [shell], p, sharp=80)
    md = ob.modifiers.new("smooth", "SUBSURF")
    md.levels = md.render_levels = 1
    # wheel, 3 mm proud of the shell
    tw = 0.74
    hw, h = _mouse_profile(tw)
    yw = _mouse_y(tw)
    wheel = shared("wheel rubber", _wheel)
    part("wheel", cylinder(0.0100, -0.0034, 0.0034, 48, axis="x"), [wheel], p, bevel=0.0010, segs=3,
         at=T(0.0, yw, h + 0.0012 + 0.0030 - 0.0100))
    # side buttons on the left flank
    for yb in (-0.004, 0.017):
        tb = (MOUSE_L / 2 - yb) / MOUSE_L
        hwb, _ = _mouse_profile(tb)
        bm = loft([(rrect(0.018, 0.0072, 0.0035, 6, yb, 0.0215), -hwb + 0.0030),
                   (rrect(0.018, 0.0072, 0.0035, 6, yb, 0.0215), -hwb + 0.0004),
                   (rrect(0.016, 0.0056, 0.0027, 6, yb, 0.0215), -hwb - 0.0008)], "x")
        part("side button", bm, [shell], p, bevel=0.0006, segs=2)
    for sy in (-1, 1):
        part("mouse foot", prism(rrect(0.036, 0.006, 0.003, 6, 0.0, sy * 0.042), 0.0, 0.0008),
             [satin("ptfe", (0.6, 0.6, 0.6), 0.3)], p)
    return ob


def _mouse_shell(name):
    """Soft-touch black. The button split (along the middle, ahead of the hump), the buttons' rear seam and
    the wheel's slot, in object space."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    ys = _mouse_y(0.53)
    front = M(t, "LESS_THAN", y, ys)
    split = M(t, "MULTIPLY", maprange(t, M(t, "ABSOLUTE", x), 0.00025, 0.0006, 1.0, 0.0), front)
    seam = maprange(t, M(t, "ABSOLUTE", M(t, "SUBTRACT", y, ys)), 0.0002, 0.0005, 1.0, 0.0)
    seam = M(t, "MULTIPLY", seam, M(t, "LESS_THAN", M(t, "ABSOLUTE", x), 0.0215))
    seam = M(t, "MULTIPLY", seam, M(t, "GREATER_THAN", z, 0.020))
    g = M(t, "MAXIMUM", split, seam)
    # wheel slot: a dark rounded opening
    yw = _mouse_y(0.74)
    qx = M(t, "SUBTRACT", M(t, "ABSOLUTE", x), 0.0045 - 0.0035)
    qy = M(t, "SUBTRACT", M(t, "ABSOLUTE", M(t, "SUBTRACT", y, yw)), 0.0125 - 0.0035)
    d = M(t, "SUBTRACT", V(t, "LENGTH", comb(t, M(t, "MAXIMUM", qx, 0.0), M(t, "MAXIMUM", qy, 0.0))), 0.0035)
    slot = M(t, "MULTIPLY", maprange(t, d, -0.0002, 0.0002, 1.0, 0.0), M(t, "GREATER_THAN", z, 0.025))
    g = M(t, "MAXIMUM", g, slot)
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=5000.0, Detail=1.0), "Factor")
    h = M(t, "SUBTRACT", M(t, "MULTIPLY", nz, 0.05), g)
    bump = N(t, "ShaderNodeBump", Strength=0.5, Distance=0.0004, Height=h)
    col = mix_rgb(t, g, (0.010, 0.010, 0.011, 1), (0.0008, 0.0008, 0.0008, 1))
    principled(t, **{"Base Color": col, "Roughness": mix_f(t, g, 0.55, 0.9), "Normal": out(bump), "Sheen Weight": 0.08,
                     "Specular IOR Level": 0.42})
    return m


def _wheel(name):
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    a = M(t, "ARCTAN2", z, y)
    h = M(t, "ABSOLUTE", M(t, "SINE", M(t, "MULTIPLY", a, 24.0)))
    bump = N(t, "ShaderNodeBump", Strength=0.7, Distance=0.0004, Height=h)
    principled(t, **{"Base Color": (0.02, 0.02, 0.022, 1), "Roughness": 0.65, "Normal": out(bump), "Sheen Weight": 0.3})
    return m
