# A DSLR with a standard zoom, no brand or text: a moulded body with a deep rubber-covered grip, the
# pentaprism hump with a hot shoe, a knurled mode dial, the shutter button with its front dial, top and
# rear screens, the eyecup, strap eyelets; the lens with a ribbed zoom and focus ring, a chrome bayonet,
# and a front element over three inner elements and the iris, each glass coated.
# Camera-local metres: the lens points along -y, the grip is on the photographer's right (-x), z up
# from the base.
import math
from mathutils import Matrix, Vector
from objects.books_kit import (catmull, rrect, rounded_extrude, lathe, tube, box, finish, empty, parent, loft,
                               resample, offset, ccw)
from objects import books_camera_shaders as cs
import bmesh

XM, ZM = 0.006, 0.0505      # the lens axis
YF, YB = -0.027, 0.030      # front (mount) face and back face of the body
ZS = 0.0765                 # shoulder height
ZG = 0.0875                 # the grip's top plate
TOPZ = 0.1140               # prism top


def _grip_scale(z):
    """How far the grip bulges at height z, relative to its full depth: fuller in the palm, easing
    off at the base and under the top plate."""
    t = min(max(z / 0.088, 0.0), 1.0)
    return 0.80 + 0.22 * math.sin(math.pi * min(1.0, t * 1.08)) ** 0.8


PLAN = [
    (0.0712, -0.016), (0.0712, 0.020), (0.0688, 0.0278), (0.061, 0.0302), (0.0, 0.0302),
    (-0.061, 0.0302), (-0.0690, 0.0276), (-0.0722, 0.016), (-0.0728, -0.010), (-0.0708, -0.0312),
    (-0.0650, -0.0438), (-0.0558, -0.0498), (-0.0448, -0.0497), (-0.0365, -0.0446), (-0.0308, -0.0368),
    (-0.0266, -0.0294), (-0.0205, -0.0272), (0.040, -0.0270), (0.0618, -0.0270), (0.0694, -0.0240),
]


def body(mats):
    outline = catmull(PLAN, 220)

    def shape(z, pts):
        g = _grip_scale(z)
        out = []
        # the grip's flank swells a little in the middle of its height
        bulge = 0.0024 * math.sin(math.pi * min(max(z / ZS, 0.0), 1.0)) ** 0.7
        for p in pts:
            if p.x < -0.020 and p.y < YF:
                w = min(1.0, (-0.020 - p.x) / 0.008)
                p = Vector((p.x, YF + (p.y - YF) * (1 - w + w * g), p.z))
            if p.x < -0.052:
                w = min(1.0, (-0.052 - p.x) / 0.014)
                p = Vector((p.x - bulge * w, p.y, p.z))
            out.append(p)
        return out

    ob = rounded_extrude("camera body", outline, 0.0, ZS, 0.0045, 0.0035, mats, nb=6, nt=6, ring_fn=shape, mid=10)
    return ob


def grip_plate(mats):
    """The raised top over the grip: its front slopes down toward the shutter button."""
    outline = [p for p in catmull(PLAN, 220) if p.x < -0.018]
    # close it along x = -0.018, behind the prism's flank
    poly = outline + [Vector((-0.018, outline[-1].y)), Vector((-0.018, outline[0].y))]
    poly = resample(ccw(poly), 160)
    poly = offset(poly, 0.0006)

    def shape(z, ring):
        g = _grip_scale(z)
        out = []
        for p in ring:
            y = p.y
            if p.x < -0.020 and y < YF:
                w = min(1.0, (-0.020 - p.x) / 0.008)
                y = YF + (y - YF) * (1 - w + w * g)
            zz = p.z
            if p.z > ZS + 0.002:
                zz -= 0.20 * max(0.0, -(y + 0.006)) * (p.z - ZS) / (ZG - ZS)
            out.append(Vector((p.x, y, zz)))
        return out

    return rounded_extrude("camera grip top", poly, ZS - 0.006, ZG, 0.0, 0.0042, mats, nb=1, nt=7, ring_fn=shape, mid=3)


def prism(mats):
    """The pentaprism hump: wide at the shoulders, narrowing to a flat top, its front leaning back."""
    z0, z1, rt = ZS - 0.004, TOPZ, 0.0045

    def section(t):
        w = 0.074 + (0.045 - 0.074) * t
        yf = -0.0250 + (-0.0045 - -0.0250) * t ** 0.9
        yb = 0.0302 - 0.0012 * t
        r = 0.011 - 0.004 * t
        return w, yf, yb, r

    rings = []
    zs = [z0 + (z1 - rt - z0) * i / 8 for i in range(9)]
    for z in zs:
        t = (z - z0) / (z1 - z0)
        w, yf, yb, r = section(t)
        rings.append([Vector((p.x, p.y, z)) for p in rrect(w, yb - yf, r, 10, XM, (yf + yb) / 2)])
    for i in range(1, 8):
        a = math.pi / 2 * i / 7
        z = z1 - rt + rt * math.sin(a)
        ins = rt * (1 - math.cos(a))
        t = (z - z0) / (z1 - z0)
        w, yf, yb, r = section(t)
        rings.append([Vector((p.x, p.y, z)) for p in rrect(w - 2 * ins, yb - yf - 2 * ins, max(r - ins, 0.0012), 10, XM,
                                                            (yf + yb) / 2)])
    return loft("camera prism", rings, mats)


def mount_boss(mats):
    """The raised housing round the bayonet, part of the body's front."""
    prof = [(0.0300, -0.0010), (0.0300, 0.0024), (0.0306, 0.0031), (0.0330, 0.0034), (0.0352, 0.0032),
            (0.0364, 0.0024), (0.0370, 0.0012), (0.0373, -0.0010)]
    ob = lathe("camera mount boss", prof, 192, mats, bev=0.0002)
    ob.data.transform(Matrix.Translation((XM, YF, ZM)) @ Matrix.Rotation(math.radians(90), 4, "X"))
    return ob


def mode_dial(mats):
    knurl = lambda ph, z, r: r + (0.00028 * (math.cos(ph * 54) ** 2 - 0.5) if 0.0022 < z < 0.0098 else 0.0)
    prof = [(0.0, 0.0), (0.0150, 0.0), (0.0150, 0.0018), (0.0158, 0.0022)]
    prof += [(0.0160, 0.0022 + 0.0076 * i / 14) for i in range(15)]
    prof += [(0.0157, 0.0102), (0.0151, 0.0108), (0.0142, 0.0110), (0.0052, 0.0110), (0.0048, 0.0114),
             (0.0046, 0.0122), (0.0040, 0.0126), (0.0, 0.0127)]
    ob = lathe("camera mode dial", prof, 54 * 6, mats, rfun=knurl, bev=0.0003, angle=55)
    ob.data.transform(Matrix.Translation((0.048, 0.006, ZS - 0.0003)))
    return ob


def shutter(mats_btn, mats_chrome):
    """The shutter button on the grip's sloping top, in its chrome collar, tilted forward."""
    M = Matrix.Translation((-0.0525, -0.0335, ZG - 0.0075)) @ Matrix.Rotation(math.radians(-24), 4, "X")
    collar = lathe("camera shutter collar", [(0.0052, -0.002), (0.0068, -0.002), (0.0070, 0.0012), (0.0066, 0.0019),
                                            (0.0058, 0.0020), (0.0053, 0.0014)], 64, mats_chrome, bev=0.00015)
    btn = lathe("camera shutter button", [(0.0, 0.0034), (0.0025, 0.0033), (0.0042, 0.0029), (0.0049, 0.0022),
                                          (0.0051, 0.0010), (0.0051, -0.001)], 64, mats_btn, bev=0.00015)
    for o in (collar, btn):
        o.data.transform(M)
    return [collar, btn]


def front_dial(mats):
    knurl = lambda ph, z, r: r + (0.0003 * (math.cos(ph * 40) ** 2 - 0.5) if -0.0026 < z < 0.0026 else 0.0)
    prof = [(0.0, -0.0034), (0.0066, -0.0034), (0.0074, -0.0028)]
    prof += [(0.0077, -0.0026 + 0.0052 * i / 8) for i in range(9)]
    prof += [(0.0074, 0.0028), (0.0066, 0.0034), (0.0, 0.0034)]
    ob = lathe("camera front dial", prof, 240, mats, rfun=knurl, bev=0.0002, angle=55)
    ob.data.transform(Matrix.Translation((-0.0440, -0.0215, ZG - 0.0040)) @ Matrix.Rotation(math.radians(90), 4, "Y"))
    return ob


def hot_shoe(mats):
    obs = []
    z = TOPZ
    obs.append(box("camera shoe plate", (0.0215, 0.0190, 0.0010), (XM, 0.0120, z + 0.0002), mats, 0.0003, 2))
    for s in (-1, 1):
        obs.append(box("camera shoe rail", (0.0020, 0.0190, 0.0032), (XM + s * 0.0105, 0.0120, z + 0.0016), mats, 0.0003, 2))
        obs.append(box("camera shoe lip", (0.0034, 0.0190, 0.0008), (XM + s * 0.0090, 0.0120, z + 0.0029), mats, 0.0002, 2))
    return obs


def strap_eyelets(mats_metal, mats_body):
    obs = []
    for s in (-1, 1):
        xs = s * 0.0712 if s > 0 else -0.0722
        boss = rounded_extrude("camera eyelet boss", rrect(0.0085, 0.0110, 0.0030, 6), 0.0, 0.0045, 0.0, 0.0012,
                               mats_body, nb=1, nt=3)
        boss.data.transform(Matrix.Translation((xs, -0.004, 0.0665)) @ Matrix.Rotation(math.radians(90 * s), 4, "Y"))
        obs.append(boss)
        pts = []
        for i in range(25):
            a = math.pi * i / 24
            pts.append((xs + s * (0.0030 + 0.0042 * math.sin(a)), -0.004 + 0.0040 * math.cos(a), 0.0690))
        obs.append(tube("camera eyelet", pts, 0.0010, mats_metal, seg=12))
    return obs


def back_parts(m_glass, m_rubber, m_body):
    obs = []
    lcd = box("camera rear screen", (0.0700, 0.0030, 0.0500), (0.0100, YB + 0.0010, 0.0405), [m_body], 0.0008, 3)
    obs.append(lcd)
    glass = box("camera rear glass", (0.0660, 0.0008, 0.0460), (0.0100, YB + 0.0026, 0.0405), [m_glass], 0.0003, 2)
    obs.append(glass)
    # the eyecup: a rubber frame round the viewfinder window
    cup = rounded_extrude("camera eyecup", rrect(0.038, 0.030, 0.008, 8), 0.0, 0.0150, 0.0, 0.0030, [m_rubber], nb=1, nt=6)
    cup.data.transform(Matrix.Translation((XM, YB - 0.002, 0.0935)) @ Matrix.Rotation(math.radians(-90), 4, "X"))
    obs.append(cup)
    win = box("camera viewfinder", (0.0210, 0.0010, 0.0150), (XM, YB + 0.0132, 0.0935), [m_glass], 0.0003, 2)
    obs.append(win)
    # the multi-controller ring and its centre button
    ring = lathe("camera dial ring", [(0.0085, 0.0), (0.0125, 0.0), (0.0128, 0.0014), (0.0124, 0.0026), (0.0090, 0.0026),
                                      (0.0085, 0.0018)], 160, [m_body], bev=0.0002, angle=50,
                 rfun=lambda ph, z, r: r + (0.00018 * (math.cos(ph * 36) ** 2 - 0.5) if r > 0.012 else 0.0))
    ring.data.transform(Matrix.Translation((-0.044, YB, 0.036)) @ Matrix.Rotation(math.radians(-90), 4, "X"))
    obs.append(ring)
    btn = lathe("camera set button", [(0.0, 0.0024), (0.0050, 0.0022), (0.0062, 0.0012), (0.0064, 0.0)], 64, [m_body], bev=0.00015)
    btn.data.transform(Matrix.Translation((-0.044, YB, 0.036)) @ Matrix.Rotation(math.radians(-90), 4, "X"))
    obs.append(btn)
    for k in range(4):
        b = rounded_extrude("camera back button", rrect(0.0075, 0.0050, 0.0022, 6), 0.0, 0.0018, 0.0, 0.0008, [m_body],
                            nb=1, nt=3)
        b.data.transform(Matrix.Translation((0.0590, YB, 0.056 - 0.0105 * k)) @ Matrix.Rotation(math.radians(-90), 4, "X"))
        obs.append(b)
    return obs


def top_parts(m_glass, m_body):
    obs = []
    lcd = box("camera top screen", (0.0215, 0.0175, 0.0014), (-0.0470, 0.0130, ZG - 0.0001), [m_glass], 0.0004, 2)
    obs.append(lcd)
    for k in range(3):
        b = lathe("camera top button", [(0.0, 0.0012), (0.0022, 0.0011), (0.0028, 0.0006), (0.0029, -0.001)], 32, [m_body], bev=0.00012)
        b.data.transform(Matrix.Translation((-0.0605 + 0.0072 * k, -0.0050, ZG - 0.0016 - 0.0006 * (k == 0))))
        obs.append(b)
    return obs


def front_parts(m_chrome, m_body, m_lamp):
    obs = []
    rot = Matrix.Rotation(math.radians(90), 4, "X")   # lathe z -> -y
    mount = lathe("camera mount ring", [(0.0272, 0.0), (0.0302, 0.0), (0.0306, 0.0010), (0.0302, 0.0020), (0.0272, 0.0020)],
                  160, [m_chrome], bev=0.0002)
    mount.data.transform(Matrix.Translation((XM, YF - 0.0030, ZM)) @ rot)
    obs.append(mount)
    rel = lathe("camera lens release", [(0.0, 0.0030), (0.0036, 0.0029), (0.0044, 0.0020), (0.0046, 0.0)], 48, [m_body], bev=0.00015)
    rel.data.transform(Matrix.Translation((XM + 0.0410, YF, ZM + 0.0070)) @ rot)
    obs.append(rel)
    dof = lathe("camera preview button", [(0.0, 0.0016), (0.0024, 0.0015), (0.0030, 0.0008), (0.0031, 0.0)], 32, [m_body], bev=0.00012)
    dof.data.transform(Matrix.Translation((XM - 0.0395, YF, ZM - 0.0190)) @ rot)
    obs.append(dof)
    lamp = lathe("camera lamp", [(0.0, 0.0010), (0.0030, 0.0009), (0.0036, 0.0)], 32, [m_lamp])
    lamp.data.transform(Matrix.Translation((-0.0325, YF - 0.0006, 0.0705)) @ rot)
    obs.append(lamp)
    return obs


# ---------------------------------------------------------------- the lens (axis +z, mount at z = 0)

def ribs(n, h, z0, z1, fillet=0.0012):
    def f(ph, z, r):
        if z <= z0 or z >= z1:
            return r
        w = min(1.0, (z - z0) / fillet, (z1 - z) / fillet)
        c = math.cos(ph * n)
        prof = max(-1.0, min(1.0, c * 2.2))      # flat-topped ribs with rounded flanks
        return r + h * 0.5 * (prof + 1) * w
    return f


def lens(mats):
    obs = []
    plastic, rubber, chrome, glass_a, glass_b, inner, iris, paint = (
        mats["lens"], mats["rubber"], mats["chrome"], mats["glass_front"], mats["glass_inner"], mats["inner"],
        mats["iris"], mats["paint"])
    # the hard barrel, from the bayonet to the front lip and in to the front element
    shell = [(0.0300, 0.0016), (0.0316, 0.0024), (0.0322, 0.0040), (0.0332, 0.0100), (0.0352, 0.0106),
             (0.0364, 0.0118), (0.0366, 0.0168), (0.0378, 0.0178), (0.0384, 0.0186), (0.0384, 0.0484),
             (0.0390, 0.0490), (0.0392, 0.0500), (0.0393, 0.0600), (0.0390, 0.0610), (0.0386, 0.0620),
             (0.0386, 0.0822), (0.0398, 0.0832), (0.0406, 0.0846), (0.0410, 0.0870), (0.0413, 0.0956),
             (0.0417, 0.0962), (0.0417, 0.0972), (0.0413, 0.0978), (0.0414, 0.0994), (0.0412, 0.1005),
             (0.0405, 0.1013), (0.0394, 0.1015), (0.0385, 0.1010), (0.0382, 0.0996), (0.0382, 0.0962),
             (0.0372, 0.0955), (0.0358, 0.0953), (0.0354, 0.0946), (0.0354, 0.0910), (0.0348, 0.0902),
             (0.0347, 0.0870)]
    obs.append(lathe("lens barrel", shell, 192, [plastic], bev=0.0003))
    bay = lathe("lens bayonet", [(0.0250, -0.0040), (0.0296, -0.0040), (0.0298, -0.0010), (0.0302, 0.0000), (0.0302, 0.0016),
                                 (0.0296, 0.0024), (0.0250, 0.0024)], 160, [chrome], closed=True, bev=0.0002)
    obs.append(bay)
    # zoom ring (wide, coarse ribs) and focus ring (narrow, finer ribs), in rubber
    zr = [(0.0384, 0.0188), (0.0394, 0.0190), (0.0399, 0.0196)] + \
         [(0.0400, 0.0200 + (0.0466 - 0.0200) * i / 24) for i in range(25)] + [(0.0399, 0.0470), (0.0394, 0.0476), (0.0384, 0.0478)]
    obs.append(lathe("lens zoom ring", zr, 80 * 8, [rubber], rfun=ribs(80, 0.00075, 0.0202, 0.0464), bev=0.0002, angle=65))
    fr = [(0.0386, 0.0624), (0.0396, 0.0626), (0.0401, 0.0632)] + \
         [(0.0402, 0.0636 + (0.0812 - 0.0636) * i / 18) for i in range(19)] + [(0.0401, 0.0816), (0.0396, 0.0821), (0.0386, 0.0823)]
    obs.append(lathe("lens focus ring", fr, 120 * 6, [rubber], rfun=ribs(120, 0.00045, 0.0638, 0.0810), bev=0.0002, angle=65))
    # front element: a convex meniscus sitting in its retaining ring
    Rc, ap, apex = 0.072, 0.0347, 0.0962
    sag = Rc - math.sqrt(Rc * Rc - ap * ap)
    front = [(0.0, apex)]
    for i in range(1, 25):
        r = ap * i / 24
        front.append((r, apex - (Rc - math.sqrt(Rc * Rc - r * r))))
    Rb = 0.11
    back = []
    zb_edge = apex - sag - 0.0030
    for i in range(24, -1, -1):
        r = ap * i / 24
        back.append((r, zb_edge + (Rb - math.sqrt(Rb * Rb - r * r)) * -1 + (Rb - math.sqrt(Rb * Rb - ap * ap))))
    obs.append(lathe("lens front element", front + back, 160, [glass_a]))
    # inside: black walls with baffle steps, two more elements, the iris
    wall = [(0.0347, 0.0870), (0.0347, 0.0832), (0.0336, 0.0826), (0.0328, 0.0790), (0.0312, 0.0784), (0.0305, 0.0700),
            (0.0290, 0.0694), (0.0280, 0.0600), (0.0262, 0.0594), (0.0254, 0.0420), (0.0240, 0.0280)]
    obs.append(lathe("lens inner wall", wall, 128, [inner]))
    for name, ap2, z, r1, r2, th, mat in (("lens element 2", 0.0288, 0.0745, -0.060, 0.09, 0.0040, glass_b),
                                         ("lens element 3", 0.0250, 0.0630, 0.050, -0.07, 0.0050, glass_b)):
        prof = []
        for i in range(17):
            r = ap2 * i / 16
            prof.append((r, z + th / 2 - (abs(r1) - math.sqrt(r1 * r1 - r * r)) * (1 if r1 > 0 else -1)))
        for i in range(16, -1, -1):
            r = ap2 * i / 16
            prof.append((r, z - th / 2 + (abs(r2) - math.sqrt(r2 * r2 - r * r)) * (1 if r2 > 0 else -1)))
        prof = [prof[0]] + prof[1:-1] + [prof[-1]]
        obs.append(lathe(name, prof, 128, [mat]))
    # the iris: nine blades closing to a small polygon, seen through the glass
    bm = bmesh.new()
    n, r_in, r_out, z = 9, 0.0085, 0.0258, 0.0520
    outer = [bm.verts.new((r_out * math.cos(2 * math.pi * k / 72), r_out * math.sin(2 * math.pi * k / 72), z)) for k in range(72)]
    inner_pts = []
    for k in range(72):
        a = 2 * math.pi * k / 72
        seg = 2 * math.pi / n
        local = (a % seg) - seg / 2
        rr = r_in * math.cos(seg / 2) / math.cos(local) * (1 + 0.04 * math.sin(local * 3))
        inner_pts.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), z + 0.0004 * ((a % seg) / seg))))
    for k in range(72):
        k2 = (k + 1) % 72
        bm.faces.new((outer[k], outer[k2], inner_pts[k2], inner_pts[k]))
    obs.append(finish("lens iris", bm, [iris], smooth=False))
    # a black disc closing the barrel behind the iris
    obs.append(lathe("lens back", [(0.0, 0.0280), (0.0245, 0.0280)], 64, [inner]))
    # white index marks (abstract ticks only)
    return obs


def build(top_z=0.0, loc=(-0.024, 0.016), turn=32.0):
    mats = cs.make()
    root = empty("camera", (loc[0], loc[1], top_z), (0, 0, math.radians(turn)))
    parts = [body([mats["body"]]), grip_plate([mats["body"]]), prism([mats["body"]]), mount_boss([mats["body"]]),
             mode_dial([mats["dial"]])]
    parts += shutter([mats["button"]], [mats["chrome"]])
    parts.append(front_dial([mats["dial"]]))
    parts += hot_shoe([mats["shoe"]])
    parts += strap_eyelets([mats["chrome"]], [mats["body"]])
    parts += back_parts(mats["screen"], mats["rubber"], mats["body"])
    parts += top_parts(mats["screen"], mats["body"])
    parts += front_parts(mats["chrome"], mats["body"], mats["lamp"])
    parent(parts, root)
    lens_root = empty("camera lens", (XM, YF, ZM), (math.radians(90), 0, 0))
    lens_root.parent = root
    lp = lens(mats)
    parent(lp, lens_root)
    return [root, lens_root] + parts + lp
