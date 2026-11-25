# The small things for desk_things.py: an audio interface, a fat round cat figure and a pot of pencils and
# paintbrushes. Local frames: origin on the desk under each thing, front towards -y.
import math, random
import bpy, bmesh
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
from objects.desk_kit import rrect, ellipse, prism, loft, cylinder, transform, N, out, M, V, mix_rgb, mix_f, maprange, \
    xyz, comb, tex, new_material, shared, principled, plastic, rubber, black_steel
from objects.things_kit import (part, T, R, lathe, bx, led, satin, paint, metal, anodized, text_mesh, mesh_bm, merge,
                                rounded_poly, tube)


# ---------------------------------------------------------------- audio interface

IW, ID = 0.160, 0.100
ZF, ZB = 0.030, 0.046          # the top's height at the front and at the back
SLOPE = math.degrees(math.atan((ZB - ZF) / ID))
TOP = Matrix.Translation((0, 0, (ZF + ZB) / 2)) @ Matrix.Rotation(math.radians(SLOPE), 4, "X")


def _knob_grip(name):
    """Rubberised knob sides with fine vertical knurls (round the object's z)."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    a = M(t, "ARCTAN2", y, x)
    h = M(t, "ABSOLUTE", M(t, "SINE", M(t, "MULTIPLY", a, 30.0)))
    bump = N(t, "ShaderNodeBump", Strength=0.5, Distance=0.0003, Height=h)
    principled(t, **{"Base Color": (0.012, 0.012, 0.013, 1), "Roughness": 0.55, "Normal": out(bump), "Sheen Weight": 0.25})
    return m


def _circular(name):
    """Circular-brushed aluminium (the scan of a spun finish) for the knob caps."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co = out(tc, "Object")
    x, y, _ = xyz(t, co)
    u = M(t, "ADD", M(t, "DIVIDE", x, 0.024), 0.5)
    v = M(t, "ADD", M(t, "DIVIDE", y, 0.024), 0.5)
    rg = tex(t, "ambientcg/Metal051A/Metal051A_2K-JPG_Roughness.jpg", comb(t, u, v), False, extension="EXTEND")
    nm = tex(t, "ambientcg/Metal051A/Metal051A_2K-JPG_NormalGL.jpg", comb(t, u, v), False, extension="EXTEND")
    nmap = N(t, "ShaderNodeNormalMap", Color=out(nm), Strength=0.6)
    principled(t, **{"Base Color": (0.62, 0.62, 0.64, 1), "Metallic": 1.0, "Roughness": maprange(t, out(rg), 0.0, 1.0, 0.18, 0.40),
                     "Normal": out(nmap)})
    return m


def knob(p, mx, r, h, name):
    """A knob on a surface (local z out of it): a skirt, a knurled grip, a spun-aluminium cap with a white
    pointer line."""
    grip = shared("knob grip", _knob_grip)
    part(name + " skirt", lathe([(r + 0.0012, 0.0), (r + 0.0012, 0.0016), (r + 0.0006, 0.0024), (0.0, 0.0024)], 64),
         [plastic("knob skirt", (0.010, 0.010, 0.011), 0.4)], p, sharp=50, at=mx)
    part(name, lathe([(r, 0.0020), (r, h - 0.0016), (r - 0.0006, h - 0.0004), (r - 0.0016, h), (0.0, h)], 64), [grip], p,
         sharp=50, at=mx)
    part(name + " cap", cylinder(r - 0.0019, h - 0.0001, h + 0.0005, 64), [shared("spun aluminium", _circular)], p,
         bevel=0.0003, segs=2, at=mx)
    part(name + " pointer", bx((-0.0004, r * 0.35, h + 0.0004), (0.0004, r - 0.0024, h + 0.0007)),
         [paint("pointer white", (0.80, 0.80, 0.80), 0.4)], p, smooth=False, at=mx)


def label(p, text, size, x, v, mat, frame=TOP):
    bm = mesh_bm(text_mesh(text, size))
    transform(bm, frame @ T(x, v, 0.00005))
    return part("label", bm, [mat], p, smooth=False)


def interface(p):
    body = anodized("interface body", (0.040, 0.041, 0.046), 0.32, scale=0.10, brushed=True)
    capm = plastic("interface cap", (0.011, 0.011, 0.012), 0.45, grain=0.08, scale=0.05, bump=0.03)
    prof = rounded_poly([(-ID / 2, 0.003), (ID / 2, 0.003), (ID / 2, ZB), (-ID / 2, ZF)], [0.003, 0.003, 0.004, 0.004], 6)
    part("interface body", prism(prof, -0.0745, 0.0745, "x"), [body], p, bevel=0.0005, segs=2)
    e = 0.0008
    prof2 = rounded_poly([(-ID / 2 - e, 0.0022), (ID / 2 + e, 0.0022), (ID / 2 + e, ZB + e), (-ID / 2 - e, ZF + e)],
                         [0.0035, 0.0035, 0.0048, 0.0048], 6)
    for x0, x1 in ((-IW / 2, -0.0745), (0.0745, IW / 2)):
        part("interface end cap", prism(prof2, x0, x1, "x"), [capm], p, bevel=0.0014, segs=3)
    for sx in (-1, 1):
        for sy in (-1, 1):
            part("interface foot", cylinder(0.0055, 0.0, 0.0030, 32, cx=sx * 0.062, cy=sy * 0.036), [rubber()], p,
                 bevel=0.0006, segs=2)
    ink = paint("panel ink", (0.55, 0.55, 0.57), 0.45)
    # two gain knobs with halos (a lit arc of LEDs round each)
    off = paint("halo off", (0.02, 0.022, 0.024), 0.25)
    for k, (x, lvl) in enumerate(((-0.052, 0.62), (-0.018, 0.45))):
        mx = TOP @ T(x, 0.010, 0.0)
        knob(p, mx, 0.0112, 0.0150, f"gain knob {k + 1}")
        a0 = math.radians(-135 - 90)
        a1 = a0 + math.radians(270 * lvl)
        a2 = math.radians(135 - 90)
        sec = rrect(0.0012, 0.0006, 0.0002, 2, 0.0146, 0.0001)
        # the arc runs clockwise from lower left (seen from above), lit up to the gain's setting
        arc = mx @ Matrix.Diagonal((-1, 1, 1, 1))
        part("halo lit", lathe(sec + [sec[0]], 48, a0=a0, a1=a1), [led("halo", (0.15, 0.95, 0.75), (0.15, 0.95, 0.75), 1.4,
                                                                        "flat", light=3.0)], p, sharp=80, at=arc)
        part("halo dim", lathe(sec + [sec[0]], 48, a0=a1, a1=a2), [off], p, sharp=80, at=arc)
        label(p, str(k + 1), 0.0035, x - 0.0175, 0.022, ink)
        # 48V and INST buttons under each knob
        for j, (dx, txt) in enumerate(((-0.0068, "48V"), (0.0068, "INST"))):
            bm = loft([(rrect(0.0070, 0.0062, 0.0014, 4), 0.0), (rrect(0.0070, 0.0062, 0.0014, 4), 0.0012),
                       (rrect(0.0062, 0.0054, 0.0011, 4), 0.0019)], "z")
            part("button", transform(bm, TOP @ T(x + dx, -0.0175, 0.0)), [plastic("button plastic", (0.020, 0.020, 0.022), 0.35)],
                 p, bevel=0.0003, segs=1)
            lit = k == 0 and j == 0
            part("button led", transform(cylinder(0.0006, 0.0018, 0.0020, 12, cx=x + dx, cy=-0.0175 + 0.0018), TOP),
                 [led("led red", (1.0, 0.05, 0.02), (1.0, 0.05, 0.02), 1.2, "flat", light=1.0) if lit else off], p)
            label(p, txt, 0.0019, x + dx, -0.0258, ink)
    # level meters, two columns of eight
    seg_cols = [(0.08, 0.85, 0.18)] * 6 + [(1.0, 0.55, 0.0), (1.0, 0.06, 0.02)]
    for c, lvl in enumerate((5, 4)):
        x = 0.012 + c * 0.0072
        for s in range(8):
            v = -0.026 + s * 0.0052
            col = seg_cols[s]
            mat = led(f"meter {s}", col, col, 1.1, "flat", light=1.0) if s < lvl else \
                paint(f"meter off {s}", tuple(0.03 + 0.05 * c_ for c_ in col), 0.2)
            part("meter", transform(prism(rrect(0.0050, 0.0030, 0.0006, 3, x, v), -0.0001, 0.0002), TOP), [mat], p)
    label(p, "L", 0.0022, 0.012, 0.0195, ink)
    label(p, "R", 0.0022, 0.0192, 0.0195, ink)
    # three small knobs and their labels
    for x, v, txt in ((0.043, 0.012, "MIX"), (0.063, 0.012, "MON"), (0.053, -0.017, "PHONES")):
        knob(p, TOP @ T(x, v, 0.0), 0.0068, 0.0110, txt.lower())
        label(p, txt, 0.0019, x, v - 0.0110, ink)
    part("power light", transform(cylinder(0.0008, 0.0, 0.0003, 16, cx=0.070, cy=0.033), TOP),
         [led("power white", (0.85, 0.9, 1.0), (0.85, 0.9, 1.0), 1.2, "flat", light=1.0)], p)
    # two combo XLR/jack inputs in the front
    for k, x in enumerate((-0.052, -0.018)):
        combo(p, T(x, -ID / 2, 0.0165) @ R(90, "X"))


def combo(p, mx):
    """A combo input: a black ring with a push latch, the XLR insert's three pin holes round a 6.35 mm jack."""
    dark = paint("socket dark", (0.004, 0.004, 0.0045), 0.7)
    face = plastic("socket plastic", (0.014, 0.014, 0.015), 0.35, grain=0.04, bump=0.02)
    part("combo ring", lathe([(0.0119, -0.0004), (0.0119, 0.0006), (0.0114, 0.0013), (0.0101, 0.0013), (0.0097, 0.0003),
                              (0.0097, -0.0020)], 64), [face], p, sharp=50, at=mx)
    part("combo insert", cylinder(0.0098, -0.0050, -0.0018, 48), [face], p, bevel=0.0004, segs=2, at=mx)
    for a in (150, 30, 270):
        r = 0.0064
        part("pin hole", cylinder(0.0011, -0.0018, -0.0017, 16, cx=r * math.cos(math.radians(a)), cy=r * math.sin(math.radians(a))),
             [dark], p, at=mx)
    part("jack ring", lathe([(0.0044, -0.0017), (0.0044, -0.0012), (0.0040, -0.0010), (0.0034, -0.0010), (0.0032, -0.0020)], 32),
         [metal("nickel", (0.62, 0.62, 0.64), 0.22)], p, sharp=50, at=mx)
    part("jack hole", cylinder(0.0032, -0.0040, -0.0016, 24), [dark], p, at=mx)
    part("latch", prism(rrect(0.0048, 0.0024, 0.0008, 3, 0.0, 0.0108), 0.0010, 0.0016), [metal("latch metal", (0.5, 0.5, 0.52), 0.3)],
         p, bevel=0.0002, segs=1, at=mx)


# ---------------------------------------------------------------- the cat

def _vinyl(name):
    """Soft vinyl, two flat colours (a warm cream, caramel where the 'zone' attribute says) under a soft
    satin coat, a little translucent."""
    m, t = new_material(name)
    zone = out(N(t, "ShaderNodeAttribute", _attribute_type="GEOMETRY", _attribute_name="zone"), "Fac")
    zone = maprange(t, zone, 0.35, 0.65, 0.0, 1.0, interp="SMOOTHSTEP")
    col = mix_rgb(t, zone, (0.80, 0.68, 0.50, 1), (0.50, 0.21, 0.075, 1))
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=400.0, Detail=2.0), "Factor")
    bump = N(t, "ShaderNodeBump", Strength=0.04, Distance=0.0002, Height=nz)
    principled(t, **{"Base Color": col, "Roughness": 0.42, "Normal": out(bump), "Coat Weight": 0.55, "Coat Roughness": 0.18,
                     "Subsurface Weight": 0.12, "Subsurface Radius": (1.0, 0.55, 0.35), "Subsurface Scale": 0.003,
                     "Specular IOR Level": 0.5})
    return m


def _spline(pts, n):
    """Catmull-Rom through points, n samples."""
    P = [Vector(q) for q in pts]
    P = [P[0] * 2 - P[1]] + P + [P[-1] * 2 - P[-2]]
    out_ = []
    segs = len(P) - 3
    for k in range(n):
        u = k / (n - 1) * segs
        i = min(int(u), segs - 1)
        t = u - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out_.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out_


TAIL = [(-0.012, 0.045, 0.012), (0.018, 0.046, 0.0095), (0.042, 0.026, 0.0085), (0.049, -0.004, 0.0085),
        (0.042, -0.030, 0.0090), (0.027, -0.044, 0.0098)]
EARS = [(-1, (-0.0235, -0.006, 0.093)), (1, (0.0235, -0.006, 0.093))]


EAR_PROFILE = [(0.0, 0.0120), (0.006, 0.0098), (0.012, 0.0062), (0.016, 0.0030), (0.0175, 0.0)]


def _ear_r(z):
    for (z0, r0), (z1, r1) in zip(EAR_PROFILE, EAR_PROFILE[1:]):
        if z <= z1:
            return r0 + (r1 - r0) * max(0.0, (z - z0)) / (z1 - z0)
    return 0.0


def _ear_frame(sx, base):
    return T(*base) @ R(sx * -17, "Y") @ R(-8, "X")


def cat(p):
    """An original figure: a fat round cat, 11 cm, sitting. Body and head one soft mass, chubby cheeks, two
    small rounded ears, front paws tucked, the tail wrapped round its side to the front; bead eyes, a small
    nose and a 'w' mouth. Built from simple volumes fused by a voxel remesh and relaxed into one surface."""
    bm = bmesh.new()

    def blob(c, r, seg=48):
        b = bmesh.new()
        bmesh.ops.create_uvsphere(b, u_segments=seg, v_segments=seg // 2, radius=1.0)
        for v in b.verts:
            v.co = Vector((v.co.x * r[0] + c[0], v.co.y * r[1] + c[1], v.co.z * r[2] + c[2]))
        return b

    body = blob((0.0, 0.004, 0.038), (0.049, 0.045, 0.040))
    for v in body.verts:
        v.co.z = max(v.co.z, 0.0035)
    merge(bm, body)
    merge(bm, blob((0.0, -0.006, 0.073), (0.043, 0.038, 0.033)))
    for sx in (-1, 1):
        merge(bm, blob((sx * 0.020, -0.027, 0.0645), (0.0145, 0.0115, 0.0115), 32))  # cheeks
        merge(bm, blob((sx * 0.0165, -0.037, 0.0095), (0.0105, 0.0120, 0.0078), 32))  # front paws
        merge(bm, blob((sx * 0.033, 0.002, 0.0145), (0.0175, 0.026, 0.0135), 32))    # haunches
    merge(bm, blob((0.0, -0.040, 0.064), (0.012, 0.007, 0.0085), 32))               # muzzle
    for sx, base in EARS:
        e = lathe([(0.0, -0.002), (0.0120, -0.002), (0.0098, 0.006), (0.0062, 0.0120), (0.0030, 0.0160), (0.0010, 0.0172), (0.0, 0.0175)], 32)
        for v in e.verts:
            v.co.y *= 0.62
        merge(bm, transform(e, _ear_frame(sx, base)))
    # tail: a tube along the spline, thinning to its tip
    path = _spline(TAIL, 40)
    tb = bmesh.new()
    rings = []
    for k, c in enumerate(path):
        d = (path[min(k + 1, len(path) - 1)] - path[max(k - 1, 0)]).normalized()
        side = d.cross(Vector((0, 0, 1))).normalized()
        up = side.cross(d).normalized()
        r = 0.0078 - 0.0018 * k / (len(path) - 1)
        rings.append([tb.verts.new(c + (side * math.cos(a) + up * math.sin(a)) * r)
                      for a in [2 * math.pi * j / 16 for j in range(16)]])
    for a, b in zip(rings, rings[1:]):
        for j in range(16):
            tb.faces.new((a[j], a[(j + 1) % 16], b[(j + 1) % 16], b[j]))
    tb.faces.new(rings[0][::-1])
    tb.faces.new(rings[-1])
    merge(bm, tb)
    merge(bm, blob(tuple(path[-1]), (0.0060, 0.0060, 0.0060), 24))
    raw = part("cat raw", bm, [], p, smooth=False)
    rm = raw.modifiers.new("remesh", "REMESH")
    rm.mode = "VOXEL"
    rm.voxel_size = 0.0007
    sm = raw.modifiers.new("relax", "LAPLACIANSMOOTH")
    sm.lambda_factor = 0.7
    sm.iterations = 40
    sm.use_volume_preserve = True
    cs = raw.modifiers.new("even", "SMOOTH")
    cs.factor = 0.5
    cs.iterations = 6
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(raw.evaluated_get(dg))
    bpy.data.objects.remove(raw)
    me.name = "cat"
    # colour zones: the ears' insides and the tail's tip, as smooth values (a soft step over a millimetre,
    # so the boundary between the two colours is clean where the attribute is interpolated)
    zone = me.attributes.new("zone", "FLOAT", "POINT")
    inv = [(sx, _ear_frame(sx, base).inverted()) for sx, base in EARS]
    n = len(path)
    tail_tip = path[int(n * 0.62):]
    def soft(d, w=0.0007):
        return max(0.0, min(1.0, 0.5 - d / (2 * w)))
    vals = []
    for v in me.vertices:
        z = 0.0
        for sx, mi in inv:
            q = mi @ v.co
            if q.y < 0.0004 and q.z > 0.0:
                # only on the ear itself: no further from its axis than its own surface
                radial = math.hypot(q.x, q.y / 0.62)
                on_ear = radial - _ear_r(q.z) - 0.0010
                hw = 0.0070 * (1 - (q.z - 0.0030) / 0.0125)
                d = max(abs(q.x) - hw, 0.0030 - q.z, q.z - 0.0150, q.y + 0.0003 - 0.0007, on_ear)
                z = max(z, soft(d))
        dmin = 9.0
        for k in range(len(tail_tip) - 1):
            a_, b_ = tail_tip[k], tail_tip[k + 1]
            ab = b_ - a_
            t_ = max(0.0, min(1.0, (v.co - a_).dot(ab) / ab.length_squared))
            dmin = min(dmin, (v.co - (a_ + ab * t_)).length)
        z = max(z, soft(dmin - 0.0072))
        vals.append(z)
    zone.data.foreach_set("value", vals)
    for f in me.polygons:
        f.use_smooth = True
    ob = bpy.data.objects.new("cat", me)
    bpy.context.scene.collection.objects.link(ob)
    me.materials.append(shared("cat vinyl", _vinyl))
    ob.parent = p
    face(p, ob)
    return ob


def face(p, ob):
    """Eyes, nose and mouth, placed on the finished surface by casting rays at it from the front."""
    me = ob.data
    bvh = BVHTree.FromPolygons([v.co.copy() for v in me.vertices], [list(f.vertices) for f in me.polygons])

    def hit(x, z):
        loc, nrm, _, _ = bvh.ray_cast(Vector((x, -0.2, z)), Vector((0, 1, 0)))
        return loc, nrm

    eye = satin("eye gloss", (0.006, 0.005, 0.005), 0.08, coat=1.0, bump=0.0)
    for sx in (-1, 1):
        loc, nrm = hit(sx * 0.0150, 0.0765)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=1.0)
        for v in bm.verts:
            v.co = Vector((v.co.x * 0.0042, v.co.y * 0.0020, v.co.z * 0.0054))
        rot = Vector((0, -1, 0)).rotation_difference(-nrm).to_matrix().to_4x4()
        part("eye", bm, [eye], p, at=T(*(loc + nrm * 0.0004)) @ rot)
        # a painted catchlight
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, segments=16, radius=0.0011)
        transform(bm, R(90, "X"))
        part("catchlight", bm, [paint("catchlight", (0.85, 0.85, 0.85), 0.3)], p, smooth=False,
             at=T(*(loc + nrm * 0.0004)) @ rot @ T(sx * -0.0012 + 0.0003, -0.00205, 0.0017))
    loc, nrm = hit(0.0, 0.0675)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 0.0030 * (1 - 0.35 * max(0.0, -v.co.z)), v.co.y * 0.0016, v.co.z * 0.0021))
    rot = Vector((0, -1, 0)).rotation_difference(-nrm).to_matrix().to_4x4()
    part("nose", bm, [satin("nose pink", (0.62, 0.22, 0.20), 0.30, coat=0.6, bump=0.0)], p, at=T(*(loc + nrm * 0.0005)) @ rot)
    # the mouth: a short line down from the nose, then a 'w'
    mouth = paint("mouth line", (0.10, 0.045, 0.030), 0.45)
    pts2 = [(-0.0060, 0.0623), (-0.0040, 0.0610), (-0.0018, 0.0612), (0.0, 0.0628), (0.0018, 0.0612), (0.0040, 0.0610),
            (0.0060, 0.0623)]
    stroke = [hit(x, z)[0] + Vector((0, 0.00015, 0)) for x, z in pts2]
    tube("mouth", stroke, 0.00042, mouth, p, res=6)
    tube("mouth", [hit(0.0, 0.0655)[0] + Vector((0, 0.00015, 0)), hit(0.0, 0.0628)[0] + Vector((0, 0.00015, 0))], 0.00042,
         mouth, p, res=4)


# ---------------------------------------------------------------- pot of pencils and brushes

POT_R, POT_H, WALL = 0.0400, 0.100, 0.0045


def _glaze(name):
    """Speckled stoneware under a satin charcoal glaze that breaks brown on the rim; the unglazed foot
    shows the clay."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co = out(tc, "Object")
    x, y, z = xyz(t, co)
    vor = N(t, "ShaderNodeTexVoronoi", co, Scale=260.0, Randomness=1.0)
    spk = maprange(t, out(vor, "Distance"), 0.06, 0.11, 1.0, 0.0)
    pick = out(N(t, "ShaderNodeTexWhiteNoise", out(vor, "Position"), _noise_dimensions="3D"), "Value")
    spk = M(t, "MULTIPLY", spk, M(t, "GREATER_THAN", pick, 0.55))
    glaze = mix_rgb(t, maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=35.0, Detail=4.0), "Factor"), 0.3, 0.7, 0.0, 1.0),
                    (0.022, 0.021, 0.020, 1), (0.040, 0.037, 0.033, 1))
    glaze = mix_rgb(t, spk, glaze, (0.30, 0.25, 0.19, 1))
    rim = maprange(t, z, POT_H - 0.0030, POT_H - 0.0004, 0.0, 1.0)
    glaze = mix_rgb(t, M(t, "MULTIPLY", rim, 0.55), glaze, (0.16, 0.11, 0.075, 1))
    foot = maprange(t, z, 0.0030, 0.0042, 1.0, 0.0)
    clay = mix_rgb(t, spk, (0.36, 0.30, 0.24, 1), (0.16, 0.11, 0.07, 1))
    col = mix_rgb(t, foot, glaze, clay)
    r = mix_f(t, foot, M(t, "ADD", 0.58, M(t, "MULTIPLY", spk, 0.15)), 0.85)
    ripple = out(N(t, "ShaderNodeTexNoise", co, Scale=60.0, Detail=3.0), "Factor")
    bump = N(t, "ShaderNodeBump", Strength=0.08, Distance=0.0005, Height=M(t, "ADD", ripple, M(t, "MULTIPLY", foot, 0.0)))
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Coat Weight": mix_f(t, foot, 0.12, 0.0),
                     "Coat Roughness": 0.35, "Specular IOR Level": 0.5})
    return m


def pot(p):
    prof = [(0.0, 0.0006), (POT_R - 0.0040, 0.0006), (POT_R - 0.0022, 0.0), (POT_R - 0.0012, 0.0010), (POT_R - 0.0016, 0.0040),
            (POT_R - 0.0010, 0.0060)]
    for k in range(1, 9):
        z = 0.006 + (POT_H - 0.009) * k / 8
        prof.append((POT_R - 0.0010 + 0.0010 * (k / 8) ** 2, z))
    prof += [(POT_R + 0.0001, POT_H - 0.0018), (POT_R - 0.0006, POT_H - 0.0003), (POT_R - WALL / 2, POT_H),
             (POT_R - WALL + 0.0006, POT_H - 0.0003), (POT_R - WALL, POT_H - 0.0018), (POT_R - WALL - 0.0004, 0.030),
             (POT_R - WALL - 0.0012, 0.0135), (POT_R - WALL - 0.0040, 0.0100), (0.0, 0.0098)]
    part("pot", lathe(prof, 96), [shared("glaze", _glaze)], p, sharp=60)
    contents(p)


# what stands in the pot: kind, length, colour
ITEMS = [("pencil", 0.178, (0.72, 0.42, 0.015)), ("brush round", 0.214, (0.42, 0.030, 0.020)),
         ("pencil", 0.163, (0.010, 0.010, 0.011)), ("brush flat", 0.198, None), ("brush filbert", 0.206, (0.012, 0.012, 0.013)),
         ("pencil", 0.151, (0.018, 0.075, 0.040)), ("brush small", 0.186, (0.06, 0.11, 0.25))]


def contents(p):
    """The items stand as a loose bundle: the longest brush near the middle, the rest round it, each leaning
    out until it rests on the rim on its own side (so the tops fan out). Jittered and re-tried until no
    two pass through each other."""
    rnd = random.Random(23)
    r_in = POT_R - WALL
    floor_z = 0.0100
    order = sorted(range(len(ITEMS)), key=lambda i: -ITEMS[i][1])
    best = None
    for attempt in range(5000):
        axes = [None] * len(ITEMS)
        a0 = rnd.uniform(0, 2 * math.pi)
        for slot, i in enumerate(order):
            kind, L, col = ITEMS[i]
            ra = 0.0038 if kind.startswith("pencil") else 0.0040
            if slot == 0:
                th = rnd.uniform(0, 2 * math.pi)
                b = Vector((0.003 * math.cos(th), 0.003 * math.sin(th), floor_z + 0.002))
                d = Vector((math.cos(th) * 0.07, math.sin(th) * 0.07, 1.0)).normalized()
            else:
                th = a0 + 2 * math.pi * (slot - 1) / (len(ITEMS) - 1) + rnd.uniform(-0.18, 0.18)
                rho = rnd.uniform(0.0105, 0.0150)
                b = Vector((rho * math.cos(th), rho * math.sin(th), floor_z + 0.002))
                tw = th + rnd.uniform(-0.22, 0.22)
                rim = Vector(((r_in - ra) * math.cos(tw), (r_in - ra) * math.sin(tw), POT_H))
                d = (rim - b).normalized()
            axes[i] = (b, d, L, ra)
        clear = True
        for i in range(len(axes)):
            for j in range(i + 1, len(axes)):
                if _seg_dist(axes[i], axes[j]) < axes[i][3] + axes[j][3] + 0.0005:
                    clear = False
                    break
            if not clear:
                break
        if clear:
            best = axes
            break
    if best is None:
        raise RuntimeError("pot: no arrangement")
    for (kind, L, col), (b, d, _, _) in zip(ITEMS, best):
        rot = Vector((0, 0, 1)).rotation_difference(d).to_matrix().to_4x4()
        spin = R(rnd.uniform(0, 360), "Z")
        at = T(*b) @ rot @ spin
        if kind == "pencil":
            pencil(p, at, L, col)
        else:
            brush(p, at, L, col, kind.split()[1])


def _seg_dist(a, b):
    """Closest distance between two items' axes, from the floor to their tops."""
    pa, da, la, _ = a
    pb, db, lb, _ = b
    best = 1.0
    for k in range(41):
        q = pa + da * (la * k / 40)
        # closest point on b's segment
        t = max(0.0, min(lb, (q - pb).dot(db)))
        best = min(best, (q - (pb + db * t)).length)
    return best


def _paint_coat(name, colour, rough=0.28):
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=300.0, Detail=2.0), "Factor")
    bump = N(t, "ShaderNodeBump", Strength=0.04, Distance=0.0002, Height=nz)
    principled(t, **{"Base Color": (*colour, 1), "Roughness": rough, "Normal": out(bump), "Coat Weight": 0.6,
                     "Coat Roughness": 0.12})
    return m


def _wood(name, tint, lacquer):
    """Fine-grained wood (the desk's oak scan, at pencil scale and tinted), plain or lacquered."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    vec = comb(t, M(t, "MULTIPLY", M(t, "ADD", x, y), 4.0), M(t, "MULTIPLY", z, 0.8))
    col = tex(t, "polyhaven/oak_veneer_01/oak_veneer_01_diff_4k.jpg", vec, True)
    c = N(t, "ShaderNodeHueSaturation", Saturation=0.8, Value=1.0, Color=out(col))
    c = mix_rgb(t, 0.55, out(c), (*tint, 1), "MULTIPLY")
    principled(t, **{"Base Color": c, "Roughness": 0.30 if lacquer else 0.62, "Coat Weight": 0.6 if lacquer else 0.0,
                     "Coat Roughness": 0.1, "Specular IOR Level": 0.5})
    return m


def pencil(p, at, L, colour):
    """A hexagonal pencil, 7.2 mm across the flats, painted; sharpened at the top, where the cone cuts the
    hexagon into scallops of bare cedar and ends in graphite."""
    paintm = shared(f"pencil paint {colour}", lambda n: _paint_coat(n, colour))
    cedar = shared("cedar", lambda n: _wood(n, (1.0, 0.72, 0.50), False))
    graphite = metal("graphite", (0.06, 0.06, 0.065), 0.38)
    rf = 0.0036
    hexr = lambda a: rf / math.cos(((a + math.pi / 6) % (math.pi / 3)) - math.pi / 6)
    n = 48
    zc0, zc1 = L - 0.0235, L - 0.0028        # the cone, from where it meets the corners down to the lead
    cone = lambda z: 0.0011 + (rf / math.cos(math.pi / 6) - 0.0011) * (zc1 - z) / (zc1 - zc0)
    zs = [0.0, zc0 - 0.008] + [zc0 - 0.008 + (zc1 - zc0 + 0.008) * k / 22 for k in range(1, 23)]
    bm = bmesh.new()
    rings = []
    for z in zs:
        ring = []
        for j in range(n):
            a = 2 * math.pi * j / n
            r = min(hexr(a), cone(z)) if z > zc0 - 0.008 else hexr(a)
            ring.append(bm.verts.new((r * math.cos(a), r * math.sin(a), z)))
        rings.append(ring)
    for zi, (ra, rb) in enumerate(zip(rings, rings[1:])):
        for j in range(n):
            k = (j + 1) % n
            f = bm.faces.new((ra[j], ra[k], rb[k], rb[j]))
            a = 2 * math.pi * (j + 0.5) / n
            zm = (zs[zi] + zs[zi + 1]) / 2
            f.material_index = 1 if cone(zm) < hexr(a) - 0.00002 else 0
    bm.faces.new(rings[0][::-1])
    top = bm.faces.new(rings[-1])
    top.material_index = 1
    part("pencil", bm, [paintm, cedar], p, sharp=40, at=at)
    part("lead", lathe([(0.00112, zc1 - 0.0004), (0.0004, L - 0.0004), (0.0, L)], 24), [graphite], p, sharp=60, at=at)


def brush(p, at, L, colour, kind):
    """A paintbrush: a lacquered handle swelling towards the ferrule, a crimped nickel ferrule and its hair:
    round to a point, flat, or filbert. Some carry dried paint."""
    hand = shared(f"handle {colour}", lambda n: _paint_coat(n, colour, 0.2)) if colour else \
        shared("handle birch", lambda n: _wood(n, (1.0, 0.86, 0.66), True))
    ferr = metal("ferrule", (0.70, 0.70, 0.72), 0.18)
    lf = 0.026 if kind != "small" else 0.020
    lh = L - lf - (0.018 if kind != "small" else 0.012)
    rmax = 0.0044 if kind != "small" else 0.0034
    prof = [(0.0, 0.0), (0.0014, 0.0002), (0.0021, 0.0012)]
    for k in range(1, 13):
        t = k / 12
        r = 0.0022 + (rmax - 0.0022) * math.sin(min(1.0, t / 0.78) * math.pi / 2) ** 1.5 - (0.0006 if t > 0.92 else 0.0)
        prof.append((r, 0.0012 + (lh - 0.0012) * t))
    prof.append((0.0, lh))
    part("brush handle", lathe(prof, 32), [hand], p, sharp=50, at=at)
    rf = rmax - 0.0006
    flat = kind in ("flat", "filbert")
    secs = []
    for k in range(9):
        t = k / 8
        z = lh - 0.0015 + (lf + 0.0015) * t
        crimp = 1.0 - (0.06 if abs(t - 0.22) < 0.04 or abs(t - 0.32) < 0.04 else 0.0)
        if flat:
            w = rf * 2 * (1 + 0.55 * t ** 1.5)
            d = rf * 2 * (1 - 0.62 * t ** 1.2)
            secs.append((ellipse(w * crimp, d * crimp, 32), z))
        else:
            r = rf * (1 - 0.10 * t) * crimp
            secs.append((ellipse(2 * r, 2 * r, 32), z))
    part("ferrule", loft(secs, "z"), [ferr], p, sharp=40, at=at)
    hair_col = {"round": (0.80, 0.74, 0.62), "flat": (0.62, 0.48, 0.30), "filbert": (0.20, 0.09, 0.035),
                "small": (0.26, 0.12, 0.05)}[kind]
    hair = shared(f"bristles {kind}", lambda n: _bristles(n, hair_col, kind == "flat"))
    z0 = lh + lf - 0.001
    lb = L - z0
    w0, d0 = secs[-1][0][0][0] * 2, abs(secs[-1][0][8][1]) * 2
    bsecs = []
    for k in range(11):
        t = k / 10
        z = z0 + lb * t
        if kind in ("round", "small"):
            r = (w0 / 2) * (1 + 0.18 * math.sin(math.pi * min(1, t / 0.6))) * (1 - t ** 1.6) + 0.00015
            bsecs.append((ellipse(2 * r, 2 * r, 32), z))
        elif kind == "flat":
            bsecs.append((rrect(w0 * (1 + 0.06 * t), max(0.0004, d0 * (1 - 0.55 * t)), max(0.0002, d0 * 0.4 * (1 - 0.5 * t)), 4), z))
        else:
            sh = math.sqrt(max(0.0, 1 - max(0.0, (t - 0.55) / 0.45) ** 2))
            bsecs.append((ellipse(max(0.0004, w0 * (1 + 0.05 * t) * sh), max(0.0003, d0 * (1 - 0.5 * t) * max(0.3, sh)), 32), z))
    if kind == "flat":
        bsecs = [(ellipse(w0, d0, 32), z0)] + [(_resample(pts, 32), z) for pts, z in bsecs[1:]]
    part("bristles", loft(bsecs, "z"), [hair], p, sharp=60, at=at)


def _resample(pts, n):
    """An outline resampled to n points by angle round its centre (to loft against ellipses)."""
    res = []
    for k in range(n):
        a = 2 * math.pi * k / n
        best, bd = pts[0], 9.0
        for q in pts:
            d = abs(((math.atan2(q[1], q[0]) - a + math.pi) % (2 * math.pi)) - math.pi)
            if d < bd:
                best, bd = q, d
        res.append(best)
    return res


def _bristles(name, colour, painted):
    """Hair: fine streaks along the brush, a sheen, and (on the flat) dried blue paint near the tip."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    st = out(N(t, "ShaderNodeTexNoise", comb(t, M(t, "MULTIPLY", x, 2500.0), M(t, "MULTIPLY", y, 2500.0), M(t, "MULTIPLY", z, 30.0)),
               Scale=1.0, Detail=2.0), "Factor")
    col = mix_rgb(t, maprange(t, st, 0.3, 0.7, 0.0, 1.0), (*[c * 0.6 for c in colour], 1), (*colour, 1))
    if painted:
        tipm = maprange(t, z, 0.188, 0.192, 0.0, 1.0)
        col = mix_rgb(t, tipm, col, (0.02, 0.06, 0.38, 1))
    bump = N(t, "ShaderNodeBump", Strength=0.3, Distance=0.0002, Height=st)
    principled(t, **{"Base Color": col, "Roughness": 0.45, "Normal": out(bump), "Sheen Weight": 0.6, "Sheen Roughness": 0.3,
                     "Anisotropic": 0.5})
    return m
