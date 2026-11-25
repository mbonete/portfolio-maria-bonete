# Mesh helpers for the books, the coffee tray and the maracas (not an object of its own): surfaces of
# revolution with UVs, lofts of outlines, rounded extrusions, tubes along paths, bevels, and per-face
# material assignment. Everything is built at true size in the object's own metres, with no object
# scale, so bevels stay even.
import math
import bpy, bmesh
from mathutils import Vector, Matrix


def link(name, me, mats=()):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for m in mats:
        me.materials.append(m)
    return ob


def finish(name, bm, mats=(), smooth=True, sharp=None, recalc=True):
    """A mesh object from a bmesh: normals made consistent, smooth shaded; with sharp (degrees) the
    edges sharper than that stay hard."""
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = link(name, me, mats)
    if smooth:
        me.shade_smooth()
        if sharp is not None:
            me.set_sharp_from_angle(angle=math.radians(sharp))
    return ob


def bevel(ob, width, seg=3, angle=30, harden=True, weight=False, clamp=True, profile=0.5):
    b = ob.modifiers.new("bevel", "BEVEL")
    b.width = width
    b.segments = seg
    b.profile = profile
    if weight:
        b.limit_method = "WEIGHT"
    else:
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(angle)
    b.harden_normals = harden
    b.use_clamp_overlap = clamp
    b.miter_outer = "MITER_ARC"
    return b


def subsurf(ob, levels=2, render=None):
    s = ob.modifiers.new("subsurf", "SUBSURF")
    s.levels = levels
    s.render_levels = render if render is not None else levels
    return s


def edge_weights(ob, pred, name="bevel_weight_edge"):
    """Bevel weight on every edge for which pred(v0, v1) returns a weight > 0 (for a WEIGHT-limited
    bevel)."""
    me = ob.data
    at = me.attributes.get(name) or me.attributes.new(name, "FLOAT", "EDGE")
    vs = me.vertices
    for e in me.edges:
        w = pred(vs[e.vertices[0]].co, vs[e.vertices[1]].co)
        at.data[e.index].value = w or 0.0


def assign(ob, fn):
    """Material index per face from fn(centre, normal)."""
    for p in ob.data.polygons:
        p.material_index = fn(p.center, p.normal)


# ---------------------------------------------------------------- 2D outlines

def catmull(pts, n, closed=True, alpha=0.5):
    """n points sampled along a centripetal Catmull-Rom spline through pts (2D or 3D tuples)."""
    P = [Vector(p) for p in pts]
    m = len(P)
    segs = m if closed else m - 1

    def get(i):
        if closed:
            return P[i % m]
        if i < 0:
            return P[0] * 2 - P[1]
        if i >= m:
            return P[-1] * 2 - P[-2]
        return P[i]

    def seg_pts(i, k):
        p0, p1, p2, p3 = get(i - 1), get(i), get(i + 1), get(i + 2)
        def tj(ti, a, b):
            return ti + max((b - a).length, 1e-9) ** alpha
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        out = []
        for s in range(k):
            t = t1 + (t2 - t1) * s / k
            a1 = p0 * ((t1 - t) / (t1 - t0)) + p1 * ((t - t0) / (t1 - t0))
            a2 = p1 * ((t2 - t) / (t2 - t1)) + p2 * ((t - t1) / (t2 - t1))
            a3 = p2 * ((t3 - t) / (t3 - t2)) + p3 * ((t - t2) / (t3 - t2))
            b1 = a1 * ((t2 - t) / (t2 - t0)) + a2 * ((t - t0) / (t2 - t0))
            b2 = a2 * ((t3 - t) / (t3 - t1)) + a3 * ((t - t1) / (t3 - t1))
            out.append(b1 * ((t2 - t) / (t2 - t1)) + b2 * ((t - t1) / (t2 - t1)))
        return out

    dense = []
    for i in range(segs):
        dense += seg_pts(i, 24)
    if not closed:
        dense.append(P[-1])
    return resample(dense, n, closed)


def resample(pts, n, closed=True):
    """n points evenly spaced along a polyline."""
    P = [Vector(p) for p in pts]
    if closed:
        P = P + [P[0]]
    L = [0.0]
    for a, b in zip(P, P[1:]):
        L.append(L[-1] + (b - a).length)
    total = L[-1]
    out = []
    k = 0
    count = n if closed else n - 1
    for i in range(n):
        s = total * i / count
        while k < len(L) - 2 and L[k + 1] < s:
            k += 1
        t = (s - L[k]) / max(L[k + 1] - L[k], 1e-12)
        out.append(P[k].lerp(P[k + 1], min(max(t, 0.0), 1.0)))
    return out


def rrect(w, h, r, seg=8, cx=0.0, cy=0.0):
    """A rounded rectangle's outline, counter-clockwise."""
    r = min(r, w / 2 - 1e-6, h / 2 - 1e-6)
    pts = []
    for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox, oy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            pts.append(Vector((ox + r * math.cos(a), oy + r * math.sin(a))))
    return pts


def superellipse(a, b, n=4.0, seg=64, cx=0.0, cy=0.0):
    pts = []
    for k in range(seg):
        t = 2 * math.pi * k / seg
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2 / n), c)
        y = b * math.copysign(abs(s) ** (2 / n), s)
        pts.append(Vector((cx + x, cy + y)))
    return pts


def ccw(pts):
    area = 0.0
    for a, b in zip(pts, pts[1:] + pts[:1]):
        area += a.x * b.y - b.x * a.y
    return pts if area > 0 else pts[::-1]


def offset(pts, d):
    """A closed counter-clockwise outline moved inward by d (outward if negative), along its smoothed
    vertex normals."""
    n = len(pts)
    out = []
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        t1 = (b - a).normalized()
        t2 = (c - b).normalized()
        n1 = Vector((-t1.y, t1.x))
        n2 = Vector((-t2.y, t2.x))
        nm = (n1 + n2)
        if nm.length < 1e-9:
            nm = n1
        nm.normalize()
        k = 1.0 / max(nm.dot(n1), 0.35)
        out.append(b + nm * d * k)
    return out


# ---------------------------------------------------------------- solids

def lathe(name, prof, seg, mats=(), rfun=None, closed=False, uv=True, smooth=True, phase=0.0, bev=0.0, angle=35):
    """A surface of revolution about z from (r, z) pairs (r = 0 closes a pole). rfun(phi, z, r) can
    modulate the radius (ribs, knurls). UVs: u round the axis (0..1), v the length along the profile
    in metres. bev > 0 keeps the profile's corners sharper than angle hard and rounds them by bev."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    rings = []
    vs = [0.0]
    for (r0, z0), (r1, z1) in zip(prof, prof[1:]):
        vs.append(vs[-1] + math.hypot(r1 - r0, z1 - z0))
    for (r, z) in prof:
        if r < 1e-7:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            ring = []
            for k in range(seg):
                ph = phase + 2 * math.pi * k / seg
                rr = rfun(ph, z, r) if rfun else r
                ring.append(bm.verts.new((rr * math.cos(ph), rr * math.sin(ph), z)))
            rings.append(ring)
    pairs = list(zip(range(len(rings)), range(1, len(rings))))
    if closed:
        pairs.append((len(rings) - 1, 0))
    for ia, ib in pairs:
        a, b = rings[ia], rings[ib]
        va, vb = vs[ia], vs[ib] if ib else vs[-1] + (Vector(prof[0]) - Vector(prof[-1])).length
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(a) == 1:
                f = bm.faces.new((a[0], b[k2], b[k]))
                uvs = ((k + 0.5) / seg, va), ((k + 1) / seg, vb), (k / seg, vb)
            elif len(b) == 1:
                f = bm.faces.new((a[k], a[k2], b[0]))
                uvs = (k / seg, va), ((k + 1) / seg, va), ((k + 0.5) / seg, vb)
            else:
                f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
                uvs = (k / seg, va), ((k + 1) / seg, va), ((k + 1) / seg, vb), (k / seg, vb)
            f.smooth = smooth
            if uv:
                for loop, q in zip(f.loops, uvs):
                    loop[uvl].uv = q
    ob = finish(name, bm, mats, smooth=smooth, sharp=angle if bev else None)
    if bev:
        bevel(ob, bev, 2, angle)
    return ob


def loft(name, rings, mats=(), caps=(True, True), smooth=True, uv=False, sharp=None):
    """3D rings of equal point count, bridged in order; optional flat caps."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    R = [[bm.verts.new(p) for p in ring] for ring in rings]
    n = len(R[0])
    for j, (a, b) in enumerate(zip(R, R[1:])):
        for i in range(n):
            i2 = (i + 1) % n
            f = bm.faces.new((a[i], a[i2], b[i2], b[i]))
            if uv:
                for loop, q in zip(f.loops, ((i / n, j), ((i + 1) / n, j), ((i + 1) / n, j + 1), (i / n, j + 1))):
                    loop[uvl].uv = q
    if caps[0]:
        bm.faces.new(R[0][::-1])
    if caps[1]:
        bm.faces.new(R[-1])
    return finish(name, bm, mats, smooth=smooth, sharp=sharp)


def rounded_extrude(name, outline, z0, z1, rb, rt, mats=(), nb=5, nt=5, sharp=None, ring_fn=None, mid=2):
    """A plan outline (counter-clockwise 2D points) extruded from z0 to z1, its bottom and top edges
    rounded with radii rb and rt (quarter circles, by insetting the outline). ring_fn(z, pts) may
    reshape each ring (taper, lean)."""
    outline = ccw([Vector(p) for p in outline])
    rings = []

    def put(z, inset):
        pts = offset(outline, inset) if inset else outline
        pts = [Vector((p.x, p.y, z)) for p in pts]
        if ring_fn:
            pts = ring_fn(z, pts)
        rings.append(pts)

    if rb > 0:
        for i in range(nb + 1):
            a = math.pi / 2 * (1 - i / nb)
            put(z0 + rb * (1 - math.sin(a)), rb * (1 - math.cos(a)))
    else:
        put(z0, 0.0)
    za, zb = z0 + rb, z1 - rt
    for i in range(1, mid):
        put(za + (zb - za) * i / mid, 0.0)
    if rt > 0:
        for i in range(nt + 1):
            a = math.pi / 2 * i / nt
            put(zb + rt * math.sin(a), rt * (1 - math.cos(a)))
    else:
        put(z1, 0.0)
    return loft(name, rings, mats, sharp=sharp)


def tube(name, pts, rad, mats=(), seg=16, caps=True, rad_fn=None, uv=True, closed=False):
    """A round tube along a 3D polyline (parallel-transport frames). rad_fn(i, t) can vary the radius
    (t = 0..1 along). UVs: u round, v along (metres)."""
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    P = [Vector(p) for p in pts]
    n = len(P)
    T = []
    for i in range(n):
        if closed:
            a, b = P[i - 1], P[(i + 1) % n]
        else:
            a, b = P[max(i - 1, 0)], P[min(i + 1, n - 1)]
        T.append((b - a).normalized())
    up = Vector((0, 0, 1)) if abs(T[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = T[0].cross(up).normalized()
    rings = []
    L = [0.0]
    for i in range(1, n):
        L.append(L[-1] + (P[i] - P[i - 1]).length)
    for i in range(n):
        if i > 0:
            axis = T[i - 1].cross(T[i])
            if axis.length > 1e-9:
                nrm = Matrix.Rotation(T[i - 1].angle(T[i]), 3, axis.normalized()) @ nrm
        bi = T[i].cross(nrm).normalized()
        r = rad_fn(i, L[i] / max(L[-1], 1e-9)) if rad_fn else rad
        rings.append([bm.verts.new(P[i] + r * (math.cos(2 * math.pi * k / seg) * nrm + math.sin(2 * math.pi * k / seg) * bi))
                      for k in range(seg)])
    pairs = list(zip(range(n), range(1, n)))
    if closed:
        pairs.append((n - 1, 0))
    for ia, ib in pairs:
        a, b = rings[ia], rings[ib]
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
            f.smooth = True
            if uv:
                vb = L[ib] if ib else L[-1] + (P[0] - P[-1]).length
                for loop, q in zip(f.loops, ((k / seg, L[ia]), ((k + 1) / seg, L[ia]), ((k + 1) / seg, vb), (k / seg, vb))):
                    loop[uvl].uv = q
    if caps and not closed:
        for ring, end, sgn in ((rings[0], 0, -1), (rings[-1], n - 1, 1)):
            c = bm.verts.new(P[end] + T[end] * sgn * (rad_fn(end, end / max(n - 1, 1)) if rad_fn else rad) * 0.35)
            for k in range(seg):
                k2 = (k + 1) % seg
                f = bm.faces.new((ring[k], ring[k2], c) if sgn > 0 else (ring[k2], ring[k], c))
                f.smooth = True
    return finish(name, bm, mats)


def box(name, size, loc=(0, 0, 0), mats=(), bev=0.0, seg=3, M=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0] + loc[0], v.co.y * size[1] + loc[1], v.co.z * size[2] + loc[2]))
    if M is not None:
        bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    ob = finish(name, bm, mats, sharp=30)
    if bev:
        bevel(ob, bev, seg)
    return ob


def place(ob, M):
    """Apply a matrix to an object's mesh (keeps the object at identity)."""
    ob.data.transform(M)
    return ob


def parent(children, par):
    for c in children:
        c.parent = par
    return children


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0)):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.location = loc
    e.rotation_euler = rot
    return e
