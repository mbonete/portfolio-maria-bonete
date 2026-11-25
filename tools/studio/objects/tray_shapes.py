# The coffee tray's solid parts, in the tray's own metres (floor at z = 0, long side along x): the
# walnut frame with its rounded-over top and a routed handle slot in each end, the floor panel, the
# porcelain cup and saucer, the coffee's surface and the espresso spoon.
import math
import bpy, bmesh
from mathutils import Vector
from objects.books_kit import rrect, rounded_extrude, lathe, finish, bevel, subsurf, catmull

L, W, H = 0.580, 0.400, 0.050     # the stand-in's size
T = 0.013                         # wall thickness
R_OUT = 0.020                     # plan radius of the outer corners
FLOOR_TOP = 0.012
SLOT = dict(len=0.104, h=0.021, z=0.0285)


def frame(mats):
    """The four walls as one ring (mitred at the rounded corners), lofted from a section: a small
    chamfer under the outside, the top rounded over on both sides."""
    seg = 14
    outer = rrect(L, W, R_OUT, seg)
    inner = rrect(L - 2 * T, W - 2 * T, R_OUT - T, seg)
    rt, ch = 0.0042, 0.0012
    prof = [(1 - ch / T, 0.0), (1.0, ch)]
    for k in range(1, 6):
        prof.append((1.0, ch + (H - rt - ch) * k / 6))
    for i in range(9):
        a = math.pi / 2 * i / 8
        prof.append((1 - rt / T + rt / T * math.cos(a), H - rt + rt * math.sin(a)))
    for i in range(9):
        a = math.pi / 2 + math.pi / 2 * i / 8
        prof.append((rt / T + rt / T * math.cos(a), H - rt + rt * math.sin(a)))
    for k in range(1, 6):
        prof.append((0.0, H - rt - (H - rt) * k / 6))
    prof.append((0.5, 0.0))
    bm = bmesh.new()
    rings = []
    for d, z in prof:
        rings.append([bm.verts.new((pi.x * (1 - d) + po.x * d, pi.y * (1 - d) + po.y * d, z)) for pi, po in zip(inner, outer)])
    n = len(outer)
    for a, b in zip(rings, rings[1:] + rings[:1]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    ob = finish("tray frame", bm, mats, sharp=35)
    # the handle slots: a stadium cut through each end wall, then every cut edge rounded over
    cut = bmesh.new()
    sl, sh, sz = SLOT["len"], SLOT["h"], SLOT["z"]
    outline = []
    for i in range(17):
        a = -math.pi / 2 + math.pi * i / 16
        outline.append((sl / 2 - sh / 2 + sh / 2 * math.cos(a), sz + sh / 2 * math.sin(a)))
    for i in range(17):
        a = math.pi / 2 + math.pi * i / 16
        outline.append((-sl / 2 + sh / 2 + sh / 2 * math.cos(a), sz + sh / 2 * math.sin(a)))
    for sx in (-1, 1):
        x0, x1 = sx * (L / 2 - T - 0.01), sx * (L / 2 + 0.01)
        lo = [cut.verts.new((x0, y, z)) for y, z in outline]
        hi = [cut.verts.new((x1, y, z)) for y, z in outline]
        m = len(outline)
        for i in range(m):
            j = (i + 1) % m
            cut.faces.new((lo[i], lo[j], hi[j], hi[i]))
        cut.faces.new(lo[::-1])
        cut.faces.new(hi)
    bmesh.ops.recalc_face_normals(cut, faces=cut.faces[:])
    cme = bpy.data.meshes.new("tray slot cutter")
    cut.to_mesh(cme)
    cut.free()
    cutter = bpy.data.objects.new("tray slot cutter", cme)
    bpy.context.scene.collection.objects.link(cutter)
    bo = ob.modifiers.new("slots", "BOOLEAN")
    bo.operation = "DIFFERENCE"
    bo.solver = "EXACT"
    bo.object = cutter
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter)
    bpy.data.meshes.remove(cme)
    me.shade_smooth()
    me.set_sharp_from_angle(angle=math.radians(35))
    b = bevel(ob, 0.0030, 5, 50)
    b.harden_normals = False
    return ob


def floor_panel(mats):
    """The floor, let into a groove round the inside of the walls."""
    out = rrect(L - 2 * T + 0.008, W - 2 * T + 0.008, R_OUT - T + 0.004, 10)
    ob = rounded_extrude("tray floor", out, 0.0035, FLOOR_TOP, 0.0, 0.0006, mats, nb=1, nt=2)
    return ob


# ---------------------------------------------------------------- porcelain

CUP_IN = [(0.0, 0.0115), (0.0120, 0.0118), (0.0200, 0.0135), (0.0270, 0.0180), (0.0325, 0.0255), (0.0362, 0.0340),
          (0.0385, 0.0430), (0.0396, 0.0510), (0.0399, 0.0575)]


def cup_inner_r(z):
    for (r0, z0), (r1, z1) in zip(CUP_IN, CUP_IN[1:]):
        if z0 <= z <= z1:
            return r0 + (r1 - r0) * (z - z0) / (z1 - z0)
    return CUP_IN[-1][0]


def cup(mats):
    """A cappuccino-size cup, 8.6 cm across: a foot ring, a tulip bowl, a rounded rim."""
    prof = [(0.0, 0.0022), (0.0150, 0.0020), (0.0188, 0.0008), (0.0196, 0.0), (0.0222, 0.0), (0.0232, 0.0012),
            (0.0236, 0.0050), (0.0250, 0.0080), (0.0285, 0.0120), (0.0335, 0.0180), (0.0378, 0.0260), (0.0408, 0.0350),
            (0.0424, 0.0440), (0.0431, 0.0520), (0.0432, 0.0570), (0.0430, 0.0588), (0.0424, 0.0598), (0.0416, 0.0601),
            (0.0407, 0.0598), (0.0401, 0.0588)]
    prof += CUP_IN[::-1][1:]
    return lathe("cup", prof, 128, mats, bev=0.0002, angle=40)


def handle(mats, rim_r=0.0430):
    """An ear-shaped handle with a flattened oval section, swelling where it meets the bowl."""
    pts = catmull([(0.0385, 0.0, 0.0500), (0.0470, 0.0, 0.0525), (0.0565, 0.0, 0.0500), (0.0610, 0.0, 0.0420),
                   (0.0595, 0.0, 0.0320), (0.0535, 0.0, 0.0240), (0.0440, 0.0, 0.0175), (0.0330, 0.0, 0.0150)],
                  48, closed=False)
    bm = bmesh.new()
    n = len(pts)
    B = Vector((0, 1, 0))
    rings = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        t = (b - a).normalized()
        nrm = B.cross(t).normalized()
        s = i / (n - 1)
        swell = 1.0 + 0.55 * max(0.0, 1 - s / 0.12) ** 2 + 0.45 * max(0.0, 1 - (1 - s) / 0.14) ** 2
        ra, rb = 0.0027 * swell, 0.0037 * (1 + (swell - 1) * 0.6)
        seg = 20
        rings.append([bm.verts.new(p + nrm * ra * math.cos(2 * math.pi * k / seg) + B * rb * math.sin(2 * math.pi * k / seg))
                      for k in range(seg)])
    for ra_, rb_ in zip(rings, rings[1:]):
        for k in range(20):
            k2 = (k + 1) % 20
            bm.faces.new((ra_[k], ra_[k2], rb_[k2], rb_[k]))
    for ring, sgn in ((rings[0], -1), (rings[-1], 1)):
        c = bm.verts.new(sum((v.co for v in ring), Vector()) / len(ring))
        for k in range(20):
            k2 = (k + 1) % 20
            bm.faces.new((ring[k], ring[k2], c))
    ob = finish("cup handle", bm, mats)
    subsurf(ob, 1)
    return ob


SAUCER = [(0.0, 0.0016), (0.0380, 0.0013), (0.0398, 0.0004), (0.0410, 0.0), (0.0455, 0.0), (0.0468, 0.0010),
          (0.0478, 0.0032), (0.0560, 0.0058), (0.0640, 0.0092), (0.0700, 0.0124), (0.0732, 0.0142), (0.0748, 0.0152),
          (0.0752, 0.0160), (0.0746, 0.0167), (0.0734, 0.0168), (0.0700, 0.0159), (0.0640, 0.0132), (0.0560, 0.0104),
          (0.0450, 0.0080), (0.0330, 0.0068), (0.0300, 0.0066), (0.0292, 0.0060), (0.0284, 0.0054), (0.0, 0.0052)]


def saucer_top(r):
    top = SAUCER[13:]
    for (r0, z0), (r1, z1) in zip(top, top[1:]):
        if r1 <= r <= r0:
            return z1 + (z0 - z1) * (r - r1) / (r0 - r1 + 1e-12)
    return 0.0052


def saucer(mats):
    return lathe("saucer", SAUCER, 160, mats, bev=0.0002, angle=40)


def coffee(mats, level=0.0480):
    """The coffee's surface under its crema, curving up a little where it meets the cup."""
    rw = cup_inner_r(level)
    prof = [(0.0, level)]
    for i in range(1, 21):
        r = (rw - 0.0016) * i / 20
        prof.append((r, level))
    for i in range(1, 7):
        a = math.pi / 2 * i / 6
        prof.append((rw - 0.0016 + 0.0016 * math.sin(a) + 0.0003, level + 0.0010 * (1 - math.cos(a))))
    return lathe("coffee", prof, 128, mats)


# ---------------------------------------------------------------- the spoon

def spoon(mats, length=0.112):
    """A polished espresso spoon: an oval bowl, a narrow neck, a handle widening to a rounded end and
    curving up. Built as a thin surface, thickened and smoothed."""
    nu, nv = 96, 16

    def half_w(x):
        if x <= 0.031:
            t = (x - 0.0155) / 0.0155
            return 0.0106 * math.sqrt(max(0.0, 1 - (t * (1.0 if t < 0 else 0.98)) ** 2))
        if x <= 0.036:
            t = (x - 0.031) / 0.005
            return 0.0030 + (0.0019 - 0.0030) * t
        t = (x - 0.036) / (length - 0.036)
        w = 0.0019 + (0.0044 - 0.0019) * t ** 1.3
        if x > length - 0.006:
            u = (x - (length - 0.006)) / 0.006
            w *= math.sqrt(max(0.0, 1 - u * u)) * 0.85 + 0.15 * (1 - u)
        return w

    def height(x, y):
        z = 0.0
        if x < 0.031:
            t = (x - 0.0158) / 0.0150
            q = 1 - t * t - (y / 0.0104) ** 2
            z -= 0.0034 * max(0.0, q) ** 0.75
        s = min(max((x - 0.030) / 0.070, 0.0), 1.0)
        z += 0.0095 * s * s * (3 - 2 * s)
        return z

    bm = bmesh.new()
    G = []
    for i in range(nu + 1):
        x = 0.0006 + (length - 0.0012) * (0.5 - 0.5 * math.cos(math.pi * i / nu))
        w = max(half_w(x), 0.0002)
        row = []
        for j in range(nv + 1):
            v = -1 + 2 * j / nv
            y = v * w
            row.append(bm.verts.new((x, y, height(x, y) + 0.0003 * (1 - v * v) * (x > 0.034))))
        G.append(row)
    for i in range(nu):
        for j in range(nv):
            bm.faces.new((G[i][j], G[i][j + 1], G[i + 1][j + 1], G[i + 1][j]))
    ob = finish("spoon", bm, mats)
    s = ob.modifiers.new("solidify", "SOLIDIFY")
    s.thickness = 0.0012
    s.offset = -1.0
    s.use_even_offset = True
    s.use_rim = True
    subsurf(ob, 2)
    return ob
