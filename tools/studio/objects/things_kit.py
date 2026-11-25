# Shared by tower.py and desk_things.py (not an object of its own): the extra geometry and materials the
# PC and the small things on the desk need, on top of desk_kit's (powder coat, dark plastic, rubber, zinc),
# which they reuse so the desk reads as one set. Every part is built at its true size around a local
# origin and hung from an empty, so a thing can be placed and turned as one.
import math
import bpy, bmesh
from mathutils import Matrix, Vector
from objects.desk_kit import (rrect, ellipse, prism, loft, cylinder, transform, mesh_object, curve_tube, N, out, M, V,
                              mix_rgb, mix_f, maprange, xyz, comb, tex, new_material, shared, principled)

# The reference's RGB: a cold cyan and a violet (linear).
CYAN = (0.0, 0.50, 1.0)
VIOLET = (0.40, 0.045, 1.0)


# ---------------------------------------------------------------- placement

def empty(name, loc=(0, 0, 0), rz=0.0, parent=None):
    """An empty to hang a thing's parts from: at loc, turned rz degrees about z."""
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    e.empty_display_size = 0.05
    e.location = loc
    e.rotation_euler = (0, 0, math.radians(rz))
    if parent is not None:
        e.parent = parent
    return e


def part(name, bm, mats, parent, bevel=0.0, segs=3, sharp=30, bevel_mat=None, smooth=True, limit=None, mx=None,
         at=None):
    """mesh_object, hung from parent: its bmesh in the parent's frame, or moved there by mx (baked into the
    mesh), or kept in its own frame and placed by `at` (an object transform: object-space shading, such as
    an LED ring's colour sweep, then follows the part)."""
    if mx is not None:
        transform(bm, mx)
    ob = mesh_object(name, bm, mats, bevel=bevel, segs=segs, sharp=sharp, bevel_mat=bevel_mat, smooth=smooth, limit=limit)
    ob.parent = parent
    if at is not None:
        ob.matrix_basis = at
    return ob


def instance(name, ob, parent, mx):
    """Another object sharing ob's mesh (and a copy of its modifiers), at local matrix mx."""
    o = bpy.data.objects.new(name, ob.data)
    bpy.context.scene.collection.objects.link(o)
    for md in ob.modifiers:
        n = o.modifiers.new(md.name, md.type)
        for k in ("width", "segments", "limit_method", "angle_limit", "harden_normals", "use_clamp_overlap", "material"):
            if hasattr(md, k):
                setattr(n, k, getattr(md, k))
    o.parent = parent
    o.matrix_basis = mx
    return o


def tube(name, pts, r, mat, parent, res=12):
    """A cable or hose through points in the parent's frame; its length is kept for the sleeve's weave."""
    ob = curve_tube(name, pts, r, mat, res=res)
    if parent is not None:
        ob.parent = parent
    ob["len"] = sum((Vector(b) - Vector(a)).length for a, b in zip(pts, pts[1:]))
    return ob


def T(x=0.0, y=0.0, z=0.0):
    return Matrix.Translation(Vector((x, y, z)))


def R(deg, axis):
    return Matrix.Rotation(math.radians(deg), 4, axis)


# ---------------------------------------------------------------- geometry

def ring_prism(outer, inner, z0, z1, axis="z", bm=None):
    """A flat ring between two outlines of equal point count (outer and inner, same winding), from d0 to d1:
    a fan's flange, a trim ring."""
    bm = bm or bmesh.new()
    from objects.desk_kit import _place
    n = len(outer)
    o0 = [bm.verts.new(_place(p, z0, axis)) for p in outer]
    o1 = [bm.verts.new(_place(p, z1, axis)) for p in outer]
    i0 = [bm.verts.new(_place(p, z0, axis)) for p in inner]
    i1 = [bm.verts.new(_place(p, z1, axis)) for p in inner]
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((o0[k], o0[j], o1[j], o1[k]))        # outer wall
        bm.faces.new((i0[j], i0[k], i1[k], i1[j]))        # inner wall
        bm.faces.new((o1[k], o1[j], i1[j], i1[k]))        # top
        bm.faces.new((o0[j], o0[k], i0[k], i0[j]))        # bottom
    return bm


def square_ring(w, r_corner, seg_per_side, cx=0.0, cy=0.0):
    """A rounded square sampled at the same angles as ellipse(..., seg) (seg = 4 * seg_per_side), so it can be
    bridged to a circle: each point is where a ray from the centre meets the rounded square."""
    seg = 4 * seg_per_side
    h = w / 2
    pts = []
    for k in range(seg):
        a = 2 * math.pi * k / seg
        c, s = math.cos(a), math.sin(a)
        # ray march against the rounded square's signed distance
        lo, hi = 0.0, h * 1.5
        for _ in range(40):
            m = (lo + hi) / 2
            x, y = abs(m * c), abs(m * s)
            qx, qy = x - (h - r_corner), y - (h - r_corner)
            d = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r_corner
            if d < 0:
                lo = m
            else:
                hi = m
        pts.append((cx + lo * c, cy + lo * s))
    return pts


def lathe(profile, seg=48, bm=None, close_axis=True, a0=0.0, a1=None):
    """A surface of revolution about z through (r, z) points, in order. Points with r == 0 close to a pole."""
    bm = bm or bmesh.new()
    full = a1 is None
    a1 = 2 * math.pi if full else a1
    n = seg if full else seg + 1
    rings = []
    for r, z in profile:
        if r < 1e-7 and close_axis:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(a0 + (a1 - a0) * k / seg), r * math.sin(a0 + (a1 - a0) * k / seg), z))
                          for k in range(n)])
    for a, b in zip(rings, rings[1:]):
        rng = range(n) if full else range(n - 1)
        for k in rng:
            j = (k + 1) % n
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                bm.faces.new((a[0], b[j], b[k]))
            elif len(b) == 1:
                bm.faces.new((a[k], a[j], b[0]))
            else:
                bm.faces.new((a[k], a[j], b[j], b[k]))
    return bm


def rounded_poly(pts, radii, seg=6):
    """A polygon (2D, CCW) with each corner rounded by its radius (a number or one per corner)."""
    n = len(pts)
    radii = radii if isinstance(radii, (list, tuple)) else [radii] * n
    res = []
    for i in range(n):
        a, b, c = Vector(pts[i - 1]), Vector(pts[i]), Vector(pts[(i + 1) % n])
        r = radii[i]
        if r <= 0:
            res.append((b.x, b.y))
            continue
        d1, d2 = (a - b).normalized(), (c - b).normalized()
        half = math.acos(max(-1.0, min(1.0, d1.dot(d2)))) / 2
        t = r / math.tan(half)
        p1, p2 = b + d1 * t, b + d2 * t
        centre = b + (d1 + d2).normalized() * (r / math.sin(half))
        a1 = math.atan2(p1.y - centre.y, p1.x - centre.x)
        a2 = math.atan2(p2.y - centre.y, p2.x - centre.x)
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(seg + 1):
            ang = a1 + da * k / seg
            res.append((centre.x + r * math.cos(ang), centre.y + r * math.sin(ang)))
    return res


def bx(lo, hi, r=0.0, axis="z", seg=4, bm=None):
    """An axis-aligned box from corner lo to corner hi, its edges along `axis` rounded by r (the others left
    for a bevel modifier)."""
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    if axis == "z":
        return prism(rrect(x1 - x0, y1 - y0, r, seg, (x0 + x1) / 2, (y0 + y1) / 2), z0, z1, "z", bm)
    if axis == "x":
        return prism(rrect(y1 - y0, z1 - z0, r, seg, (y0 + y1) / 2, (z0 + z1) / 2), x0, x1, "x", bm)
    return prism(rrect(x1 - x0, z1 - z0, r, seg, (x0 + x1) / 2, (z0 + z1) / 2), y0, y1, "y", bm)


def rbox(w, d, h, r, cx=0.0, cy=0.0, z0=0.0, seg=6, bm=None):
    """A box with rounded vertical edges (its other edges left for a bevel modifier)."""
    return prism(rrect(w, d, r, seg, cx, cy), z0, z0 + h, "z", bm)


def rounded_slab(pts, z0, z1, r, steps=4, bm=None, axis="z"):
    """An outline extruded from z0 to z1 with both rims rounded by radius r (quarter circles), as a loft of
    offset outlines. pts must be convex-ish and CCW; offsetting is done by moving each point along its
    corner bisector."""
    def offset(p, dist):
        n = len(p)
        res = []
        for i in range(n):
            a, b, c = Vector(p[i - 1]), Vector(p[i]), Vector(p[(i + 1) % n])
            e1 = (b - a).normalized()
            e2 = (c - b).normalized()
            n1 = Vector((e1.y, -e1.x))
            n2 = Vector((e2.y, -e2.x))
            nb = (n1 + n2)
            if nb.length < 1e-9:
                nb = n1
            nb.normalize()
            k = 1.0 / max(0.3, nb.dot(n1))
            q = b - nb * dist * k
            res.append((q.x, q.y))
        return res
    secs = []
    for k in range(steps + 1):
        a = math.pi / 2 * k / steps
        secs.append((offset(pts, r * (1 - math.sin(a))), z0 + r * (1 - math.cos(a))))
    for k in range(steps + 1):
        a = math.pi / 2 * k / steps
        secs.append((offset(pts, r * (1 - math.cos(a))), z1 - r + r * math.sin(a)))
    return loft(secs, axis, bm=bm)


def text_mesh(body, size, name="legend", align="CENTER", valign="CENTER", spacing=1.0, bold=False):
    """Blender's built-in font as a flat mesh in the xy plane (no third-party font), centred on the origin."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = valign
    cu.space_character = spacing
    cu.resolution_u = 3
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return me


def merge(dst, src):
    """Copy src's geometry into dst (and free src)."""
    vmap = {v: dst.verts.new(v.co) for v in src.verts}
    for f in src.faces:
        dst.faces.new([vmap[v] for v in f.verts])
    src.free()
    return dst


def mesh_bm(me):
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    return bm


# ---------------------------------------------------------------- materials

def _led(name, ca, cb, strength, mode, lo, hi, light, waves):
    """An RGB diffuser: milky plastic lit from inside. The colour runs from ca to cb by mode: 'angle' about
    the object's z (waves times round), or along an object axis 'x'/'y'/'z' from lo to hi. To the camera
    it shows `strength`, hotter where it faces the eye, so it keeps its colour at the edges instead of
    clipping to white; the light it throws on what is near (diffuse rays) is `light`, the brightness a
    real strip of LEDs would have in a dark case."""
    m, t = new_material(name)
    m.cycles.emission_sampling = "FRONT"
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    if mode == "angle":
        a = M(t, "ARCTAN2", y, x)
        f = M(t, "ADD", M(t, "DIVIDE", a, 2 * math.pi), 0.5)
        f = M(t, "PINGPONG", M(t, "MULTIPLY", f, 2.0 * waves), 1.0)
    elif mode == "flat":
        f = 0.0
    else:
        f = maprange(t, {"x": x, "y": y, "z": z}[mode], lo, hi, 0.0, 1.0)
    f = out(N(t, "ShaderNodeMapRange", f, 0.0, 1.0, 0.0, 1.0, _interpolation_type="SMOOTHSTEP"), "Result")
    col = mix_rgb(t, f, (*ca, 1), (*cb, 1))
    lp = N(t, "ShaderNodeLightPath")
    face = out(N(t, "ShaderNodeLayerWeight", Blend=0.5), "Facing")
    core = M(t, "POWER", M(t, "SUBTRACT", 1.0, face), 2.0)
    cam = M(t, "MULTIPLY", strength, M(t, "ADD", 0.45, M(t, "MULTIPLY", core, 1.3)))
    s = mix_f(t, out(lp, "Is Diffuse Ray"), cam, light)
    # the diffuser's own colour, lit or not: a dim tint of its light, so outside light does not wash it white
    tint = mix_rgb(t, 0.85, (0.03, 0.03, 0.03, 1), mix_rgb(t, 0.5, (0.06, 0.06, 0.06, 1), col))
    principled(t, **{"Base Color": tint, "Roughness": 0.35, "Emission Color": col, "Emission Strength": s,
                     "Specular IOR Level": 0.4})
    return m


def led(name, ca=CYAN, cb=VIOLET, strength=1.1, mode="angle", lo=0.0, hi=1.0, light=120.0, waves=1.0):
    return shared(name, lambda n: _led(n, ca, cb, strength, mode, lo, hi, light, waves))


def _thin_ior(t, ior=1.52):
    """Thin glass never bends the ray, so its inner face must reflect like its outer one: the Fresnel node
    would otherwise see glass-to-air there and go into total internal reflection past 41 degrees."""
    back = out(N(t, "ShaderNodeNewGeometry"), "Backfacing")
    return mix_f(t, back, ior, 1.0 / ior)


def _glass(name, hw, hh, frit, tint, corner):
    """Tempered glass, 4 mm, as thin glass: it tints what is behind it a little (and lets light and shadow
    rays through, so the LEDs inside light the desk), reflects with Fresnel, and carries faint smudges. A
    black frit is printed round its border on the inside (hw, hh: the panel's half size in the object's xy;
    frit: the border's width)."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, _ = xyz(t, co)
    # rounded-rectangle distance to the frit's inner edge
    qx = M(t, "SUBTRACT", M(t, "ABSOLUTE", x), hw - frit - corner)
    qy = M(t, "SUBTRACT", M(t, "ABSOLUTE", y), hh - frit - corner)
    d = M(t, "SUBTRACT", V(t, "LENGTH", comb(t, M(t, "MAXIMUM", qx, 0.0), M(t, "MAXIMUM", qy, 0.0))), corner)
    clear = maprange(t, d, 0.0, 0.0004, 1.0, 0.0)
    # smudges: the scan's prints, only here and there
    fp = tex(t, "ambientcg/Fingerprints002/Fingerprints002_2K-JPG_Roughness.jpg", V(t, "SCALE", co, scale=1 / 0.22),
             False, box=0.2)
    patch = maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=6.0, Detail=2.0), "Factor"), 0.52, 0.66, 0.0, 1.0)
    smudge = M(t, "MULTIPLY", out(fp), patch)
    rough = M(t, "ADD", 0.012, M(t, "MULTIPLY", smudge, 0.16))
    fr = N(t, "ShaderNodeFresnel", IOR=_thin_ior(t))
    gloss = N(t, "ShaderNodeBsdfGlossy", Color=(1, 1, 1, 1), Roughness=rough, _distribution="GGX")
    see = N(t, "ShaderNodeBsdfTransparent", Color=(*tint, 1))
    paint = N(t, "ShaderNodeBsdfDiffuse", Color=(0.006, 0.006, 0.007, 1))
    body = N(t, "ShaderNodeMixShader", clear, paint, see)
    mix = N(t, "ShaderNodeMixShader", fr, body, gloss)
    o = N(t, "ShaderNodeOutputMaterial")
    t.links.new(mix.outputs[0], o.inputs["Surface"])
    return m


def glass(name, hw, hh, frit=0.012, tint=(0.88, 0.89, 0.90), corner=0.004):
    return shared(name, lambda n: _glass(n, hw, hh, frit, tint, corner))


def _glass_edge(name):
    m, t = new_material(name)
    fr = N(t, "ShaderNodeFresnel", IOR=_thin_ior(t))
    gloss = N(t, "ShaderNodeBsdfGlossy", Color=(1, 1, 1, 1), Roughness=0.05)
    see = N(t, "ShaderNodeBsdfTransparent", Color=(0.32, 0.42, 0.38, 1))
    mix = N(t, "ShaderNodeMixShader", fr, see, gloss)
    o = N(t, "ShaderNodeOutputMaterial")
    t.links.new(mix.outputs[0], o.inputs["Surface"])
    return m


def glass_edge():
    return shared("glass edge", _glass_edge)


def _anodized(name, colour, rough, scale, brushed, metal):
    """Anodized aluminium: a dyed oxide over metal, bead-blasted (fine noise) or brushed (the scan's
    streaks, stretched along x)."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    if brushed:
        v = V(t, "MULTIPLY", co, (1 / scale, 1 / (scale * 0.08), 1 / (scale * 0.08)))
        rg = tex(t, "ambientcg/Metal009/Metal009_2K-JPG_Roughness.jpg", v, False, box=0.25)
        r = maprange(t, out(rg), 0.2, 0.8, rough - 0.08, rough + 0.10)
        h = out(rg)
    else:
        nz = out(N(t, "ShaderNodeTexNoise", co, Scale=1800.0, Detail=1.0), "Factor")
        r = maprange(t, nz, 0.3, 0.7, rough - 0.04, rough + 0.04)
        h = nz
    var = out(N(t, "ShaderNodeTexNoise", co, Scale=9.0, Detail=3.0), "Factor")
    r = M(t, "ADD", r, maprange(t, var, 0.3, 0.7, -0.03, 0.03))
    bump = N(t, "ShaderNodeBump", Strength=0.05, Distance=0.0002, Height=h)
    principled(t, **{"Base Color": (*colour, 1), "Metallic": metal, "Roughness": r, "Normal": out(bump),
                     "Specular IOR Level": 0.5})
    return m


def anodized(name, colour=(0.035, 0.035, 0.038), rough=0.38, scale=0.12, brushed=False, metal=0.85):
    return shared(name, lambda n: _anodized(n, colour, rough, scale, brushed, metal))


def _satin(name, colour, rough, coat, sheen, bump_scale, bump):
    """A plain moulded or painted surface with a fine micro-texture, optional clear coat."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=bump_scale, Detail=2.0), "Factor")
    var = out(N(t, "ShaderNodeTexNoise", co, Scale=14.0, Detail=3.0), "Factor")
    r = M(t, "ADD", rough, maprange(t, var, 0.3, 0.7, -0.04, 0.04))
    bm = N(t, "ShaderNodeBump", Strength=bump, Distance=0.0002, Height=nz)
    principled(t, **{"Base Color": (*colour, 1), "Roughness": r, "Normal": out(bm), "Specular IOR Level": 0.5,
                     "Coat Weight": coat, "Coat Roughness": 0.08, "Sheen Weight": sheen})
    return m


def satin(name, colour, rough=0.45, coat=0.0, sheen=0.0, bump_scale=2500.0, bump=0.03):
    return shared(name, lambda n: _satin(n, colour, rough, coat, sheen, bump_scale, bump))


def _print(name, colour, rough):
    m, t = new_material(name)
    principled(t, **{"Base Color": (*colour, 1), "Roughness": rough, "Specular IOR Level": 0.45})
    return m


def paint(name, colour, rough=0.5):
    """Pad-printed ink, a legend or a mark."""
    return shared(name, lambda n: _print(n, colour, rough))


def _metal(name, colour, rough):
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    nz = out(N(t, "ShaderNodeTexNoise", co, Scale=600.0, Detail=3.0), "Factor")
    r = maprange(t, nz, 0.3, 0.7, rough * 0.8, rough * 1.25)
    principled(t, **{"Base Color": (*colour, 1), "Metallic": 1.0, "Roughness": r})
    return m


def metal(name, colour=(0.62, 0.62, 0.64), rough=0.25):
    return shared(name, lambda n: _metal(n, colour, rough))


def _sleeve(name, colour, pitch):
    """Braided nylon sleeving on a curve: a fine diagonal over-under weave. The curve's UV runs 0..1 along it
    and round it; the object's "len" property (set by tube()) turns that into metres."""
    m, t = new_material(name)
    uv = out(N(t, "ShaderNodeTexCoord"), "UV")
    u, v, _ = xyz(t, uv)
    ln = out(N(t, "ShaderNodeAttribute", _attribute_type="OBJECT", _attribute_name="len"), "Fac")
    along = M(t, "DIVIDE", M(t, "MULTIPLY", u, ln), pitch)
    around = M(t, "MULTIPLY", v, 8.0)
    a = M(t, "SINE", M(t, "MULTIPLY", M(t, "ADD", along, around), 2 * math.pi))
    b = M(t, "SINE", M(t, "MULTIPLY", M(t, "SUBTRACT", along, around), 2 * math.pi))
    h = M(t, "MAXIMUM", a, b)
    bump = N(t, "ShaderNodeBump", Strength=0.4, Distance=0.0002, Height=h)
    col = mix_rgb(t, maprange(t, h, -1.0, 1.0, 0.0, 1.0), (*[c * 0.55 for c in colour], 1), (*colour, 1))
    principled(t, **{"Base Color": col, "Roughness": 0.48, "Normal": out(bump), "Sheen Weight": 0.12,
                     "Sheen Roughness": 0.45, "Specular IOR Level": 0.4})
    return m


def sleeve(name="sleeve", colour=(0.012, 0.012, 0.013), pitch=0.0022):
    return shared(name, lambda n: _sleeve(n, colour, pitch))


def _perf(name, pitch, hole, plane, colour, rough):
    """Perforated sheet: a hex grid of round holes (dark, matte) in a painted surface, in the object's
    `plane` ("xy", "xz" or "yz"); pitch and hole radius in metres."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    a, b = {"xy": (x, y), "xz": (x, z), "yz": (y, z)}[plane]
    sy = pitch * math.sqrt(3)
    def dist(oa, ob):
        aa = M(t, "ADD", M(t, "DIVIDE", a, pitch), oa)
        bb = M(t, "ADD", M(t, "DIVIDE", b, sy), ob)
        da = M(t, "MULTIPLY", M(t, "SUBTRACT", aa, M(t, "ROUND", aa)), pitch)
        db = M(t, "MULTIPLY", M(t, "SUBTRACT", bb, M(t, "ROUND", bb)), sy)
        return V(t, "LENGTH", comb(t, da, db))
    d = M(t, "MINIMUM", dist(0.0, 0.0), dist(0.5, 0.5))
    holef = maprange(t, d, hole - 0.00012, hole + 0.00012, 1.0, 0.0)
    col = mix_rgb(t, holef, (*colour, 1), (0.0015, 0.0015, 0.0017, 1))
    r = mix_f(t, holef, rough, 0.95)
    bump = N(t, "ShaderNodeBump", Strength=0.6, Distance=0.0004, Height=M(t, "SUBTRACT", 1.0, holef))
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.5})
    return m


def perf(name, pitch=0.003, hole=0.0011, plane="xy", colour=(0.02, 0.02, 0.022), rough=0.45):
    return shared(name, lambda n: _perf(n, pitch, hole, plane, colour, rough))
