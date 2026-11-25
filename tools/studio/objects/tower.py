# The PC: a 235 x 455 x 480 mm mid-tower at the desk's right end, its front towards the camera. A black
# steel chassis on four feet, tempered glass on the front and the left side (the one facing the monitors
# and, at an angle, the camera), a perforated filter on top with the power button and ports, the solid
# steel right side. Inside (tower_parts.py): three RGB intake fans in front of a 360 mm radiator, an
# exhaust fan at the back, the AIO's pump on the CPU, RAM with light bars, a graphics card and the PSU
# shroud, with sleeved cables between them. RGB in the reference's cyan and violet, as real emitters that
# light the inside and spill a little through the glass onto the desk. No brand or logo.
# Desk-local metres; built round its own origin (the footprint's centre on the desk top) and hung from an
# empty at the stand-in's place.
import math
import bmesh
from mathutils import Matrix, Vector
from common import DESK_H, TOWER_X
from objects.desk_kit import rrect, ellipse, prism, loft, cylinder, transform, powder, powder_edge, plastic, rubber, black_steel
from objects.things_kit import (empty, part, tube, T, R, bx, ring_prism, lathe, led, glass, glass_edge, satin, paint,
                                metal, perf, sleeve, anodized, CYAN, VIOLET)
from objects import tower_parts as tp

W, D, H = 0.235, 0.455, 0.480
FOOT = 0.020            # the feet lift the chassis this far
SLAB = 0.006            # top and bottom panels
Y_FRONT = -0.2045       # the chassis' front face, behind the glass front panel
Y_BACK = D / 2
TURN = 0.0              # turn about z, degrees


def glass_panel(p, name, centre, rot, hw, hh, frit, thick=0.004):
    """A tempered glass panel: its local xy is the panel's plane (so the frit is printed by object
    coordinates), local z its outward normal."""
    mat = glass(name, hw, hh, frit)
    bm = bx((-hw, -hh, -thick / 2), (hw, hh, thick / 2), 0.004, "z")
    ob = part(name, bm, [mat, glass_edge()], p, bevel=0.0009, segs=2, bevel_mat=1)
    for f in ob.data.polygons:
        if abs(f.normal.z) < 0.5:
            f.material_index = 1
    ob.matrix_basis = Matrix.Translation(Vector(centre)) @ rot.to_4x4()
    return ob


def chassis(p):
    pc, pe = powder(), powder_edge()
    z0, z1 = FOOT, H
    # bottom and top panels
    part("bottom panel", bx((-W / 2, Y_FRONT, z0), (W / 2, Y_BACK, z0 + SLAB), 0.004), [pc, pe], p, bevel=0.0018,
         segs=3, bevel_mat=1)
    # the top in a matte textured coat (a satin one mirrors the room at this angle)
    top = satin("case top coat", (0.014, 0.014, 0.015), 0.66, bump_scale=1800.0, bump=0.08)
    part("top panel", bx((-W / 2, Y_FRONT, z1 - SLAB), (W / 2, Y_BACK, z1), 0.004), [top, pe], p, bevel=0.0022, segs=3,
         bevel_mat=1)
    # top dust filter: a plastic frame round a fine perforated sheet
    fr = plastic("filter frame", (0.010, 0.010, 0.011), 0.60, grain=0.05, bump=0.02)
    outer = rrect(0.196, 0.352, 0.008, 6, 0.0, 0.020)
    inner = rrect(0.184, 0.340, 0.004, 6, 0.0, 0.020)
    part("filter frame", ring_prism(outer, inner, z1 - 0.0004, z1 + 0.0012), [fr], p, bevel=0.0005, segs=2)
    part("filter mesh", prism(inner, z1 - 0.0003, z1 + 0.0006), [perf("filter mesh", 0.0021, 0.00072, "xy",
                                                                       (0.006, 0.006, 0.0065), 0.62)], p)
    # front I/O on the top, ahead of the filter
    yio = -0.186
    bm = cylinder(0.0062, z1, z1 + 0.0016, 48, cx=-0.070, cy=yio)
    part("power button", bm, [anodized("button alu", (0.05, 0.05, 0.055), 0.25, scale=0.02)], p, bevel=0.0005, segs=2)
    part("power ring", tp._ring(0.0064, 0.0074, z1 - 0.0002, z1 + 0.0010, 48), [led("power led", CYAN, CYAN, 1.5, "flat", light=1.5)], p)
    dark = tp.hole()
    for x, w, d in ((-0.040, 0.0130, 0.0050), (-0.022, 0.0130, 0.0050), (-0.004, 0.0090, 0.0033)):
        part("port", prism(rrect(w + 0.0016, d + 0.0016, 0.0012 if w < 0.01 else 0.0006, 4, x, yio), z1 - 0.0002,
                           z1 + 0.0003), [satin("port rim", (0.02, 0.02, 0.022), 0.3)], p)
        part("port hole", prism(rrect(w, d, 0.0011 if w < 0.01 else 0.0004, 4, x, yio), z1 + 0.0002, z1 + 0.00035),
             [dark], p)
    bm = cylinder(0.0020, z1 + 0.0002, z1 + 0.00035, 24, cx=0.012, cy=yio)
    part("audio jack", bm, [dark], p)
    bm = cylinder(0.0032, z1, z1 + 0.0009, 24, cx=0.026, cy=yio)
    part("reset button", bm, [plastic()], p, bevel=0.0003, segs=1)
    # rear panel (inside it, the exhaust fan's perforated grille and the slot covers)
    part("rear panel", bx((-W / 2 + 0.0008, Y_BACK - 0.006, z0 + SLAB), (W / 2 - 0.0008, Y_BACK, z1 - SLAB)), [pc, pe],
         p, bevel=0.0008, segs=2, bevel_mat=1)
    part("rear grille", bx((-0.066, Y_BACK - 0.0062, 0.338), (0.046, Y_BACK - 0.0058, 0.452), 0.004, "y"),
         [perf("rear grille", 0.0045, 0.0019, "xz", (0.02, 0.02, 0.022), 0.45)], p)
    for k in range(4):
        zc = 0.244 - k * 0.0203
        part("slot cover", bx((-0.052, Y_BACK - 0.0068, zc - 0.0085), (0.072, Y_BACK - 0.0060, zc + 0.0085), 0.001, "y"),
             [perf("slot vents", 0.0030, 0.0009, "xz", (0.02, 0.02, 0.022), 0.4)], p, bevel=0.0003, segs=1)
    # the solid right side, with two thumbscrews at its back edge
    part("right panel", bx((W / 2 - 0.0016, Y_FRONT + 0.0005, z0 + SLAB), (W / 2, Y_BACK, z1 - SLAB)), [pc, pe], p,
         bevel=0.0007, segs=2, bevel_mat=1)
    for zc in (0.11, 0.39):
        bm = cylinder(0.0065, W / 2, W / 2 + 0.006, 24, cx=Y_BACK - 0.008, cy=zc, axis="x")
        part("thumbscrew", bm, [black_steel()], p, bevel=0.0012, segs=2)
    # the motherboard tray (the right side's inner wall) and its rubber cable grommets
    xt = 0.093
    part("tray", bx((xt, Y_FRONT + 0.001, z0 + SLAB), (xt + 0.0015, Y_BACK - 0.006, z1 - SLAB)), [pc, pe], p,
         bevel=0.0004, segs=1, bevel_mat=1)
    for zc in (0.215, 0.327, 0.420):
        grommet(p, xt, -0.0600, zc, 0.016, 0.070)
    # pillars behind the glass's frit, front and back, and the fans' rails
    for y0, y1 in ((Y_FRONT, Y_FRONT + 0.012), (Y_BACK - 0.018, Y_BACK - 0.006)):
        part("pillar", bx((-W / 2 + 0.0045, y0, z0 + SLAB), (-W / 2 + 0.0145, y1, z1 - SLAB)), [pc, pe], p,
             bevel=0.0005, segs=1, bevel_mat=1)
    for sx in (-1, 1):
        part("fan rail", bx((sx * 0.0525 - 0.008, Y_FRONT, z0 + SLAB), (sx * 0.0525 + 0.008, Y_FRONT + 0.0015, z1 - SLAB)),
             [pc, pe], p, bevel=0.0004, segs=1, bevel_mat=1)
    # a light strip under the top, along the glass side, in a diffuser channel
    part("top channel", bx((-W / 2 + 0.0060, Y_FRONT + 0.014, z1 - SLAB - 0.0060), (-W / 2 + 0.0160, Y_BACK - 0.020, z1 - SLAB)),
         [plastic("channel plastic", (0.010, 0.010, 0.011), 0.4)], p, bevel=0.0005, segs=1)
    part("top light", bx((-W / 2 + 0.0075, Y_FRONT + 0.016, z1 - SLAB - 0.0068), (-W / 2 + 0.0145, Y_BACK - 0.022, z1 - SLAB - 0.0050), 0.0012, "y"),
         [led("top light", CYAN, VIOLET, 1.1, "y", Y_FRONT, Y_BACK)], p, bevel=0.0005, segs=2)
    # underglow: a diffuser strip under the bottom panel along its front and glass-side edges, lighting the
    # desk under and round the case
    ch = plastic("channel plastic", (0.010, 0.010, 0.011), 0.4)
    ug = led("tower underglow", VIOLET, CYAN, 1.0, "x", -W / 2, W / 2, light=170.0)
    for lo, hi in (((-W / 2 + 0.012, Y_FRONT + 0.004, z0 - 0.0030), (W / 2 - 0.012, Y_FRONT + 0.012, z0)),
                   ((-W / 2 + 0.004, Y_FRONT + 0.016, z0 - 0.0030), (-W / 2 + 0.012, Y_BACK - 0.016, z0))):
        part("underglow channel", bx(lo, hi, 0.001), [ch], p, bevel=0.0004, segs=1)
        a, b = Vector(lo) + Vector((0.0012, 0.0012, -0.0006)), Vector(hi) - Vector((0.0012, 0.0012, 0.0024))
        part("underglow", bx(tuple(a), tuple(b), 0.0008), [ug], p, bevel=0.0003, segs=1)
    # feet
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.082, sy * 0.170
            part("foot", loft([(rrect(0.030, 0.062, 0.010, 6, x, y), 0.0022), (rrect(0.030, 0.062, 0.010, 6, x, y), 0.012),
                                (rrect(0.024, 0.056, 0.008, 6, x, y), z0 + 0.0002)], "z"),
                 [plastic("foot plastic", (0.012, 0.012, 0.013), 0.42)], p, bevel=0.0015, segs=3)
            part("foot pad", prism(rrect(0.028, 0.060, 0.009, 6, x, y), 0.0, 0.0024), [rubber()], p, bevel=0.0008, segs=2)


def grommet(p, x, y, z, w, h):
    """A rubber grommet in the tray: a rounded rim and a split membrane."""
    g = satin("grommet rubber", (0.010, 0.010, 0.011), 0.65, sheen=0.25)
    outer = rrect(w + 0.006, h + 0.006, (w + 0.006) / 2 - 0.0005, 8, y, z)
    inner = rrect(w, h, w / 2 - 0.0005, 8, y, z)
    part("grommet", ring_prism(outer, inner, x - 0.0022, x + 0.0004, "x"), [g], p, bevel=0.0007, segs=2)
    part("grommet membrane", prism(inner, x - 0.0004, x + 0.0002, "x"), [g], p)
    part("grommet slit", prism(rrect(0.0012, h - 0.006, 0.0005, 2, y, z), x - 0.0007, x - 0.0003, "x"), [tp.hole()], p)


def front_panel(p):
    """The front: a plastic surround with perforated intakes down both sides, and a glass sheet over it."""
    fr = plastic("front plastic", (0.013, 0.013, 0.014), 0.38, grain=0.06, bump=0.02)
    zc, hz = (FOOT + H) / 2, H - FOOT
    yf = -D / 2 + 0.004          # glass's inner face
    outer = rrect(W, hz, 0.006, 6, 0.0, zc)
    inner = rrect(W - 0.030, hz - 0.030, 0.004, 6, 0.0, zc)
    part("front surround", ring_prism(outer, inner, yf, Y_FRONT, "y"), [fr], p, bevel=0.0014, segs=3)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * W / 2, sx * (W / 2 + 0.0004)))
        part("intake", bx((x0, yf + 0.0025, FOOT + 0.012), (x1, Y_FRONT - 0.0025, H - 0.012), 0.0015, "x"),
             [perf("intake mesh", 0.0026, 0.0009, "yz", (0.016, 0.016, 0.018), 0.45)], p)
    rot = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))
    glass_panel(p, "front glass", (0.0, -D / 2 + 0.002, zc), rot, W / 2 - 0.0012, hz / 2 - 0.0012, 0.0145)


def side_glass(p):
    hw = (Y_BACK - (Y_FRONT + 0.0005)) / 2
    yc = (Y_BACK + Y_FRONT + 0.0005) / 2
    hh = (H - SLAB - (FOOT + SLAB)) / 2 - 0.0004
    zc = (H + FOOT) / 2
    rot = Matrix(((0, 0, -1), (-1, 0, 0), (0, 1, 0)))
    glass_panel(p, "side glass", (-W / 2 + 0.002, yc, zc), rot, hw, hh, 0.016)


def psu_shroud(p):
    pc, pe = powder(), powder_edge()
    x0, x1 = -W / 2 + 0.0065, 0.093
    y0, y1 = -0.147, Y_BACK - 0.006
    zt = 0.155
    part("psu shroud", bx((x0, y0, FOOT + SLAB), (x1, y1, zt)), [pc, pe], p, bevel=0.0012, segs=2, bevel_mat=1)
    # vents over the PSU and on the shroud's glass-facing side
    part("shroud vent", bx((x0 + 0.012, 0.110, zt - 0.0002), (x1 - 0.012, y1 - 0.012, zt + 0.0003), 0.003),
         [perf("shroud vent", 0.0040, 0.0015, "xy", (0.02, 0.02, 0.022), 0.45)], p)
    part("shroud side vent", bx((x0 - 0.0003, y0 + 0.012, 0.040), (x0 + 0.0002, y0 + 0.095, 0.140), 0.004, "x"),
         [perf("shroud side vent", 0.0040, 0.0015, "yz", (0.02, 0.02, 0.022), 0.45)], p)
    # light strip along its top outer edge, in a diffuser channel
    part("shroud channel", bx((x0 - 0.0012, y0 + 0.004, zt - 0.0050), (x0 + 0.0040, y1 - 0.004, zt + 0.0010), 0.0008, "y"),
         [plastic("channel plastic", (0.010, 0.010, 0.011), 0.4)], p, bevel=0.0004, segs=1)
    part("shroud light", bx((x0 - 0.0016, y0 + 0.006, zt - 0.0040), (x0 + 0.0010, y1 - 0.006, zt - 0.0002), 0.0010, "y"),
         [led("shroud light", VIOLET, CYAN, 1.1, "y", y0, y1)], p, bevel=0.0004, segs=2)
    # cable cut-out for the card's power, with a rubber grommet
    g = satin("grommet rubber", (0.010, 0.010, 0.011), 0.65, sheen=0.25)
    outer = rrect(0.030, 0.062, 0.010, 8, -0.078, 0.014)
    inner = rrect(0.024, 0.056, 0.008, 8, -0.078, 0.014)
    part("shroud grommet", ring_prism(outer, inner, zt - 0.0004, zt + 0.0018), [g], p, bevel=0.0006, segs=2)
    part("shroud hole", prism(inner, zt - 0.0030, zt - 0.0010), [tp.hole()], p)


def cables(p, fittings, plugs):
    """Sleeved power leads (one sleeve per wire) and the AIO's braided hoses."""
    sl = sleeve("psu sleeve", (0.016, 0.016, 0.018))
    comb = plastic("cable comb", (0.012, 0.012, 0.013), 0.35)
    r = 0.00165
    XB, YR, ZT = tp.XB, tp.YR, tp.ZT
    # 24-pin: out of the socket at the board's front edge, round into the tray's middle grommet
    for i in range(12):
        z = ZT - 0.110 - i * 0.0042
        for j, hx in enumerate((0.0040, 0.0090)):
            x = XB - hx
            pts = [Vector((x, YR - 0.244, z)), Vector((x, YR - 0.250, z)), Vector((x - 0.002 + j * 0.003, -0.054, z)),
                   Vector((0.084 + j * 0.003, -0.0600 - 0.0042 * (j - 0.5), z)), Vector((0.098, -0.0600 - 0.0042 * (j - 0.5), z))]
            tube("atx wire", pts, r, sl, p, res=8)
    part("atx comb", bx((XB - 0.0122, YR - 0.2535, ZT - 0.1625), (XB - 0.0018, YR - 0.2505, ZT - 0.1075), 0.0006, "y"),
         [comb], p, bevel=0.0004, segs=1)
    # EPS: up from its socket and back through the tray over the board's top edge
    for i in range(4):
        y = YR - 0.0365 - i * 0.0042
        for j, v in enumerate((0.0055, 0.0098)):
            z = ZT - v
            pts = [Vector((XB - 0.012, y, z)), Vector((XB - 0.016, y, z + 0.002)), Vector((XB - 0.017 + j * 0.004, y, 0.4665)),
                   Vector((XB - 0.004, y, 0.4700 - j * 0.0035)), Vector((0.098, y, 0.4700 - j * 0.0035))]
            tube("eps wire", pts, r, sl, p, res=8)
    # the card's two 8-pin leads: out of the plugs, down to the shroud's grommet
    xo, zp = tp.GPU_XO, tp.GPU_ZP
    for yc in plugs:
        for i in range(4):
            y = yc - 0.0063 + i * 0.0042
            for j, z in enumerate((zp - 0.0170, zp - 0.0118)):
                xe = -0.0700 - j * 0.0040
                pts = [Vector((xo - 0.016, y, z)), Vector((xo - 0.020, y, z)),
                       Vector((xe + 0.010, y, z - 0.012 + j * 0.003)), Vector((xe, y + (yc - 0.016) * 0.10, 0.215)),
                       Vector((xe + 0.001, 0.014 + (y - 0.0155) * 0.9, 0.170)), Vector((xe + 0.002, 0.014 + (y - 0.0155) * 0.9, 0.140))]
                tube("pcie wire", pts, r, sl, p, res=8)
    part("pcie comb", bx((-0.0880, -0.0080, 0.232), (-0.0640, 0.0390, 0.235), 0.0006), [comb], p, bevel=0.0004, segs=1)
    # hoses: from the pump's swivels, out past the RAM and forwards to the radiator's fittings
    hose = sleeve("hose sleeve", (0.010, 0.010, 0.011))
    rh = 0.0058
    ends = [Vector((0.036, tp.RAD_Y1 + 0.016, 0.415)), Vector((0.012, tp.RAD_Y1 + 0.016, 0.415))]
    for k, (a, b) in enumerate(zip(fittings, ends)):
        xm = 0.024 - k * 0.012
        pts = [a, a + Vector((-0.010, -0.002, 0.0)), Vector((xm, a.y - 0.020, a.z + 0.004)),
               Vector((xm, 0.010, a.z + 0.012 + k * 0.006)), Vector((b.x, -0.080, b.z - 0.002)), b + Vector((0, 0.012, 0)), b]
        tube("hose", pts, rh, hose, p, res=24)
        # crimped collars where the hose meets each fitting
        for end, nxt in ((pts[0], pts[1]), (pts[-1], pts[-2])):
            d = (nxt - end).normalized()
            rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
            part("hose collar", lathe([(rh + 0.0010, 0.0), (rh + 0.0012, 0.0015), (rh + 0.0009, 0.0045), (rh + 0.0012, 0.0075),
                                       (rh + 0.0010, 0.0090)], 32), [black_steel()], p, sharp=50, at=T(*end) @ rot)


def build():
    p = empty("tower", (TOWER_X, 0.10, DESK_H), TURN)
    chassis(p)
    front_panel(p)
    side_glass(p)
    psu_shroud(p)
    ring = led("rgb ring", light=320.0)
    fan = None
    for k, zc in enumerate((0.100, 0.222, 0.344)):
        mx = T(0.0, Y_FRONT + 0.0027 + tp.FAN_T / 2, zc) @ R(90, "X") @ R(37 * k + 10, "Z")
        if fan is None:
            fan = tp.Fan(p, mx, ring)
        else:
            fan.again(p, mx)
        for sx in (-1, 1):
            for sz in (-1, 1):
                bm = cylinder(0.0034, Y_FRONT - 0.0012, Y_FRONT, 20, cx=sx * 0.0525, cy=zc + sz * 0.0525, axis="y")
                part("fan screw", bm, [black_steel()], p, bevel=0.0005, segs=2)
    # exhaust fan at the back, its blade side facing in
    fan.again(p, T(-0.010, Y_BACK - 0.006 - tp.FAN_T / 2, 0.395) @ R(90, "X") @ R(200, "Z"))
    tp.radiator(p)
    tp.motherboard(p)
    fittings = tp.pump(p)
    plugs = tp.gpu(p)
    cables(p, fittings, plugs)
    return p
