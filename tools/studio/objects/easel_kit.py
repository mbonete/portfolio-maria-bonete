# Shared by easel.py and palette.py (not an object of its own): wooden parts built along their grain
# with UVs that wrap round their edges, cuts and booleans that leave real end faces, small turned and
# stamped hardware, and the materials: oiled beech, pine, primed and raw canvas, brass, zinc, phenolic.
# Every part is built at true size in its own frame (local z along the grain) and placed with a matrix,
# so bevels stay even and the shaders can work in object space.
import os
import bpy, bmesh, math, random
from mathutils import Matrix, Vector
from objects.desk_kit import (prism, N, out, M as Mf, V, mix_rgb, mix_f, maprange, xyz, comb, tex, new_material,
                              principled)

# Poly Haven's oak_veneer_04 (CC0): a pale, fine, straight-grained scan that, graded, reads as beech
WOOD = "polyhaven/oak_veneer_04/oak_veneer_04_"
WOOD_TILE = 1.0          # metres the veneer scan covers (Poly Haven lists it as 1 x 1 m)


# ---------------------------------------------------------------- frames and planes

def frame(origin, ez, ex):
    """A rigid 4x4 matrix: local z along ez, local x along ex (made perpendicular), origin at origin."""
    ez = Vector(ez).normalized()
    ex = Vector(ex)
    ex = (ex - ez * ex.dot(ez)).normalized()
    ey = ez.cross(ex)
    m = Matrix.Identity(4)
    for i in range(3):
        m[i][0], m[i][1], m[i][2], m[i][3] = ex[i], ey[i], ez[i], origin[i]
    return m


def plane_into(mtx, co, no):
    """A plane (point, normal) given in the parent space, expressed in the space mtx maps from."""
    inv = mtx.inverted()
    return inv @ Vector(co), (inv.to_3x3() @ Vector(no)).normalized()


def cut(bm, planes):
    """Cut a closed mesh by planes (point, normal in the mesh's own space): what lies on the normal's side
    goes, and the opening is capped, so a leg stands on a real flat foot."""
    for co, no in planes:
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no, clear_outer=True, dist=1e-7)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge) and e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    return bm


def revolve(profile, seg=48, bm=None, mtx=None):
    """A closed surface of revolution about local z from (radius, z) pairs, top to bottom or bottom to
    top; a zero radius at either end closes it with a pole."""
    bm = bm or bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-7:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                          for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1:
            for k in range(seg):
                bm.faces.new((a[0], b[k], b[(k + 1) % seg]))
        elif len(b) == 1:
            for k in range(seg):
                bm.faces.new((a[k], b[0], a[(k + 1) % seg]))
        else:
            for k in range(seg):
                bm.faces.new((a[k], b[k], b[(k + 1) % seg], a[(k + 1) % seg]))
    if len(rings[0]) > 1:
        bm.faces.new(rings[0])
    if len(rings[-1]) > 1:
        bm.faces.new(rings[-1][::-1])
    if mtx is not None:
        bmesh.ops.transform(bm, matrix=mtx, verts=bm.verts)
    return bm


def box_bm(x0, x1, y0, y1, z0, z1, bm=None):
    return prism([(x1, y1), (x0, y1), (x0, y0), (x1, y0)], z0, z1, "z", bm)


def grain_uvs(bm, name, tile=WOOD_TILE):
    """UVs for wood whose grain runs along local z: u along the grain, v round the section (x + y is
    continuous over every edge, so the figure wraps the corners as it does on solid wood). Each part
    starts somewhere different in the scan."""
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    rnd = random.Random(name)
    oz, os_ = rnd.uniform(0, tile), rnd.uniform(0, tile)
    for f in bm.faces:
        for lp in f.loops:
            c = lp.vert.co
            lp[uvl].uv = ((c.z + oz) / tile, (c.x + c.y + os_) / tile)


def orient(bm, centre):
    """Turn every face of an open surface to face away from a point (recalculating normals cannot tell
    the outside of a surface that does not enclose anything)."""
    c = Vector(centre)
    flip = [f for f in bm.faces if f.normal.dot(f.calc_center_median() - c) < 0]
    if flip:
        bmesh.ops.reverse_faces(bm, faces=flip)
    return bm


def to_object(name, bm, mats, mtx=None, bevel=0.0, segs=3, sharp=30.0, smooth=True, harden=True, profile=0.5,
              recalc=True):
    """A mesh object from a bmesh in its own frame, placed by mtx; smooth-shaded with hard edges kept,
    and a bevel modifier that rounds every edge sharper than `sharp` degrees by `bevel` metres."""
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mtx is not None:
        ob.matrix_world = mtx
    if smooth:
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(sharp))
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = segs
        md.profile = profile
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(sharp)
        md.harden_normals = harden
        md.use_clamp_overlap = True
        md.miter_outer = "MITER_ARC"
    return ob


def wood_part(name, bm, mtx, mat, bevel=0.0028, segs=4, planes=(), holes=(), sharp=30.0):
    """A wooden part: bm in its own frame (grain along z), cut by planes given in the parent space,
    with holes (bmeshes in the part's frame) taken out, its grain UVs, and softly rounded edges."""
    if planes:
        cut(bm, [plane_into(mtx, co, no) for co, no in planes])
    grain_uvs(bm, name)
    ob = to_object(name, bm, [mat], mtx)
    for k, h in enumerate(holes):
        subtract(ob, h)
    if holes:
        # the boolean's new faces need grain UVs too
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        grain_uvs(bm, name)
        bm.to_mesh(ob.data)
        bm.free()
        ob.data.shade_smooth()
        ob.data.set_sharp_from_angle(angle=math.radians(sharp))
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = segs
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(sharp)
        md.harden_normals = True
        md.use_clamp_overlap = True
        md.miter_outer = "MITER_ARC"
    return ob


def subtract(ob, cutter_bm, solver="EXACT"):
    """Apply a boolean difference with a cutter given as a bmesh in ob's own frame."""
    me = bpy.data.meshes.new(ob.name + " cutter")
    cutter_bm.to_mesh(me)
    cutter_bm.free()
    cutter = bpy.data.objects.new(ob.name + " cutter", me)
    bpy.context.scene.collection.objects.link(cutter)
    cutter.matrix_world = ob.matrix_world
    md = ob.modifiers.new("cut", "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.solver = solver
    md.object = cutter
    # keep only this boolean while applying (other modifiers come later)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.remove(md)
    old = ob.data
    ob.data = new
    new.name = old.name
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cutter, do_unlink=True)
    bpy.data.meshes.remove(me)
    return ob


def link_copy(ob, mtx, name=None):
    """Another object sharing ob's mesh and modifiers, placed by mtx."""
    c = ob.copy()
    if name:
        c.name = name
    for col in ob.users_collection:
        col.objects.link(c)
    c.matrix_world = mtx
    return c


# ---------------------------------------------------------------- small hardware

def dome_screw(name, mat, r=0.0045, h=0.0018, slot=True):
    """A slotted round-head screw, its underside at z = 0 facing -z, the dome up +z."""
    prof = [(0.0, h)]
    for k in range(1, 9):
        a = math.pi / 2 * k / 8
        prof.append((r * math.sin(a), h * math.cos(a) ** 0.8))
    prof.append((r * 0.97, 0.0))
    prof.append((0.0, 0.0))
    bm = revolve(prof, 32)
    ob = to_object(name, bm, [mat], smooth=True, sharp=60)
    if slot:
        subtract(ob, box_bm(-r * 1.2, r * 1.2, -r * 0.11, r * 0.11, h * 0.35, h * 2, None))
    return ob


def countersunk(name, mat, r=0.0038):
    """A flat countersunk screw head flush with a plate, slotted."""
    bm = revolve([(0.0, 0.0004), (r * 0.9, 0.0004), (r, 0.0001), (r, 0.0), (0.0, 0.0)], 32)
    ob = to_object(name, bm, [mat], smooth=True, sharp=50)
    subtract(ob, box_bm(-r * 1.2, r * 1.2, -r * 0.1, r * 0.1, 0.0001, 0.002, None))
    return ob


def wing_nut(name, mat, hub_r=0.0055, hub_h=0.0065, span=0.034, wing_h=0.013, t=0.0022):
    """A wing nut seated at z = 0, its axis along +z: a round hub and two thin upswept wings."""
    bm = revolve([(0.0, hub_h), (hub_r * 0.8, hub_h), (hub_r, hub_h * 0.8), (hub_r * 1.08, 0.0012),
                  (hub_r * 1.2, 0.0), (0.0, 0.0)], 32)
    # a wing's outline in (radius, height): rising from the hub, its top edge a rounded ear
    for s in (-1, 1):
        pts = [(hub_r * 0.6, 0.0008), (span / 2 * 0.62, 0.0018)]
        for k in range(0, 13):
            a = math.pi * (-0.15 + 1.05 * k / 12)
            cx, cy, rr = span / 2 - 0.0055, wing_h - 0.0055, 0.0055
            pts.append((cx + rr * math.cos(-a + math.pi / 2), cy + rr * math.sin(-a + math.pi / 2)))
        pts.append((hub_r * 0.6, hub_h * 0.9))
        pts = [(s * x, z) for x, z in pts]
        if s < 0:
            pts = pts[::-1]
        bm2 = bmesh.new()
        prism(pts, -t / 2, t / 2, "y", bm2)
        me = bpy.data.meshes.new("tmp")
        bm2.to_mesh(me)
        bm2.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    return to_object(name, bm, [mat], bevel=0.0006, segs=2, sharp=40)


# ---------------------------------------------------------------- materials

def _grain_tex(t, uv, name):
    return tex(t, WOOD + name, uv, colour=(name.startswith("diff")))


def oiled_wood(name, colour=(0.50, 0.255, 0.105), contrast=2.2, rough=(0.36, 0.54), end_dark=0.55, sheen=0.25,
               raw=False):
    """Beech, wiped with oil: the veneer scan's own figure with its contrast raised (oil darkens the
    dense lines more than the soft wood between, so the grain stands out) and its mean brought to
    `colour`; a satin sheen; end grain soaks up more oil and reads darker, with its growth rings; each
    part a little different in tone. Object space: every part's local z runs along its grain."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    uv, co, nrm = out(tc, "UV"), out(tc, "Object"), out(tc, "Normal")
    rnd = out(N(t, "ShaderNodeObjectInfo"), "Random")
    x, y, z = xyz(t, co)
    nx, ny, nz = xyz(t, nrm)
    diff = _grain_tex(t, uv, "diff_2k.jpg")
    rgh = _grain_tex(t, uv, "rough_2k.jpg")
    nor = _grain_tex(t, uv, "nor_gl_2k.jpg")
    tint = colour
    # the scan divided by its mean colour, raised to a power (the figure's contrast), times the target
    norm = mix_rgb(t, 1.0, out(diff), (1 / 0.76, 1 / 0.51, 1 / 0.35, 1), "MULTIPLY")
    g = N(t, "ShaderNodeGamma", Color=norm, Gamma=contrast)
    col = mix_rgb(t, 1.0, out(g), (*colour, 1), "MULTIPLY")
    # medullary rays: beech's small dark flecks, short dashes along the grain
    fl = out(N(t, "ShaderNodeTexVoronoi", V(t, "MULTIPLY", co, (1.0, 1.0, 0.16)), Scale=260.0, Randomness=1.0,
               _feature="F1"), "Distance")
    fleck = maprange(t, fl, 0.10, 0.03, 0.0, 1.0)
    fleck = Mf(t, "MULTIPLY", fleck, maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=40.0, Detail=2.0), "Factor"),
                                              0.45, 0.65, 0.0, 0.5))
    col = mix_rgb(t, fleck, col, (tint[0] * 0.55, tint[1] * 0.36, tint[2] * 0.22, 1), "MIX")
    # each part its own board: a touch lighter or darker, warmer or cooler
    hsv = N(t, "ShaderNodeHueSaturation", Hue=Mf(t, "ADD", 0.495, Mf(t, "MULTIPLY", rnd, 0.012)),
            Saturation=Mf(t, "ADD", 0.94, Mf(t, "MULTIPLY", rnd, 0.12)),
            Value=Mf(t, "MULTIPLY", 1.0, Mf(t, "ADD", 0.90, Mf(t, "MULTIPLY", Mf(t, "FRACT", Mf(t, "MULTIPLY", rnd, 7.31)), 0.20))),
            Color=col)
    col = out(hsv)
    # end grain: growth rings round a pith off to one side of the part, pores, and more oil taken up
    endm = maprange(t, Mf(t, "ABSOLUTE", nz), 0.55, 0.85, 0.0, 1.0)
    px = Mf(t, "ADD", -0.08, Mf(t, "MULTIPLY", rnd, 0.16))
    py = Mf(t, "SUBTRACT", -0.05, Mf(t, "MULTIPLY", Mf(t, "FRACT", Mf(t, "MULTIPLY", rnd, 13.7)), 0.10))
    d = V(t, "LENGTH", comb(t, Mf(t, "SUBTRACT", x, px), Mf(t, "SUBTRACT", y, py)))
    wob = out(N(t, "ShaderNodeTexNoise", co, Scale=60.0, Detail=2.0), "Factor")
    d = Mf(t, "ADD", d, Mf(t, "MULTIPLY", wob, 0.0012))
    ring = Mf(t, "FRACT", Mf(t, "DIVIDE", d, 0.0028))
    ring = maprange(t, ring, 0.0, 0.25, 1.0, 0.0, interp="SMOOTHSTEP")
    pores = maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=3000.0, Detail=1.0), "Factor"), 0.55, 0.7, 0.0, 1.0)
    endc = mix_rgb(t, Mf(t, "MULTIPLY", ring, 0.55), col, (0.0, 0.0, 0.0, 1), "MIX")
    endc = mix_rgb(t, end_dark, endc, (tint[0] * 0.30, tint[1] * 0.18, tint[2] * 0.09, 1), "MIX")
    endc = mix_rgb(t, Mf(t, "MULTIPLY", pores, 0.25), endc, (0.02, 0.01, 0.005, 1), "MIX")
    col = mix_rgb(t, endm, col, endc)
    # satin oil: roughness follows the scan's open pores; end grain is dull
    r = maprange(t, out(rgh), 0.2, 0.9, rough[0], rough[1])
    smear = out(N(t, "ShaderNodeTexNoise", co, Scale=9.0, Detail=4.0, Roughness=0.6), "Factor")
    r = Mf(t, "ADD", r, maprange(t, smear, 0.35, 0.7, -0.04, 0.05))
    r = mix_f(t, endm, r, 0.72)
    nmap = N(t, "ShaderNodeNormalMap", Strength=0.45, Color=out(nor))
    lum = out(N(t, "ShaderNodeRGBToBW", Color=out(diff)))
    bump = N(t, "ShaderNodeBump", Strength=0.12, Distance=0.0002, Height=lum, Normal=out(nmap))
    eb = N(t, "ShaderNodeBump", Strength=0.4, Distance=0.00015, Height=Mf(t, "ADD", Mf(t, "MULTIPLY", ring, 0.5), pores))
    nrmo = out(N(t, "ShaderNodeMix", _data_type="VECTOR", Factor_Float=endm, A_Vector=out(bump), B_Vector=out(eb)),
               "Result_Vector")
    kw = {"Base Color": col, "Roughness": r, "Normal": nrmo, "Specular IOR Level": 0.5}
    if not raw:
        kw.update({"Sheen Weight": sheen, "Sheen Roughness": 0.35, "Sheen Tint": (1.0, 0.85, 0.65, 1)})
    principled(t, **kw)
    return m


def weave(t, a, b, threads=1000.0):
    """A plain weave's height (0..1) at surface coordinates a, b (metres): warp threads along b, weft
    along a, each passing over one and under the next, with slubs (thicker stretches) along them."""
    A, B = Mf(t, "MULTIPLY", a, threads), Mf(t, "MULTIPLY", b, threads)
    i, j = Mf(t, "FLOOR", A), Mf(t, "FLOOR", B)
    fu, fv = Mf(t, "FRACT", A), Mf(t, "FRACT", B)
    si = Mf(t, "SUBTRACT", 1.0, Mf(t, "MULTIPLY", Mf(t, "FLOORED_MODULO", i, 2.0), 2.0))
    sj = Mf(t, "SUBTRACT", 1.0, Mf(t, "MULTIPLY", Mf(t, "FLOORED_MODULO", j, 2.0), 2.0))
    pi = math.pi
    over_w = Mf(t, "ADD", 0.5, Mf(t, "MULTIPLY", Mf(t, "MULTIPLY", si, Mf(t, "SINE", Mf(t, "MULTIPLY", B, pi))), 0.5))
    over_f = Mf(t, "SUBTRACT", 0.5, Mf(t, "MULTIPLY", Mf(t, "MULTIPLY", sj, Mf(t, "SINE", Mf(t, "MULTIPLY", A, pi))), 0.5))
    # slubs: each thread a little thicker or thinner along its length
    slub_w = out(N(t, "ShaderNodeTexNoise", comb(t, Mf(t, "MULTIPLY", i, 0.731), Mf(t, "MULTIPLY", B, 0.06), 0.0),
                   Scale=1.0, Detail=2.0), "Factor")
    slub_f = out(N(t, "ShaderNodeTexNoise", comb(t, Mf(t, "MULTIPLY", A, 0.06), Mf(t, "MULTIPLY", j, 0.731), 5.0),
                   Scale=1.0, Detail=2.0), "Factor")
    prof_w = Mf(t, "POWER", Mf(t, "SINE", Mf(t, "MULTIPLY", fu, pi)), 0.6)
    prof_f = Mf(t, "POWER", Mf(t, "SINE", Mf(t, "MULTIPLY", fv, pi)), 0.6)
    hw = Mf(t, "MULTIPLY", Mf(t, "MULTIPLY", prof_w, Mf(t, "ADD", 0.35, Mf(t, "MULTIPLY", over_w, 0.65))),
            maprange(t, slub_w, 0.3, 0.7, 0.75, 1.15))
    hf = Mf(t, "MULTIPLY", Mf(t, "MULTIPLY", prof_f, Mf(t, "ADD", 0.35, Mf(t, "MULTIPLY", over_f, 0.65))),
            maprange(t, slub_f, 0.3, 0.7, 0.75, 1.15))
    return Mf(t, "MAXIMUM", hw, hf)


def _face_coords(t, co, nrm):
    """Two surface coordinates for a box-like canvas in its own frame (x across, y depth, z up): the
    front and back use (x, z), the sides (y, z), the top and bottom edges (x, y)."""
    x, y, z = xyz(t, co)
    nx, ny, nz = xyz(t, nrm)
    sx = Mf(t, "GREATER_THAN", Mf(t, "ABSOLUTE", nx), 0.6)
    sz = Mf(t, "GREATER_THAN", Mf(t, "ABSOLUTE", nz), 0.6)
    return mix_f(t, sx, x, y), mix_f(t, sz, z, y)


def corner_pull(t, co, face):
    """Height of the soft diagonal ridges a stretched canvas keeps at its corners, where the cloth was
    pulled hardest: parallel to the diagonal, fading a few centimetres in. face: (x0, x1, z0, z1)."""
    x, y, z = xyz(t, co)
    x0, x1, z0, z1 = face
    total = None
    k = 2 * math.pi / 0.016
    for cx, ix in ((x0, 1.0), (x1, -1.0)):
        for cz, iz in ((z0, 1.0), (z1, -1.0)):
            dx = Mf(t, "MULTIPLY", Mf(t, "SUBTRACT", x, cx), ix)
            dz = Mf(t, "MULTIPLY", Mf(t, "SUBTRACT", z, cz), iz)
            sd = Mf(t, "MULTIPLY", Mf(t, "ADD", dx, dz), 0.7071)
            pd = Mf(t, "MULTIPLY", Mf(t, "SUBTRACT", dx, dz), 0.7071)
            wave = Mf(t, "SINE", Mf(t, "MULTIPLY", pd, k))
            fade = Mf(t, "EXPONENT", Mf(t, "MULTIPLY", sd, -1 / 0.05))
            wedge = Mf(t, "EXPONENT", Mf(t, "MULTIPLY", -1.0, Mf(t, "POWER", Mf(t, "DIVIDE", pd, Mf(t, "ADD", Mf(t, "MULTIPLY", sd, 0.45), 0.004)), 2.0)))
            term = Mf(t, "MULTIPLY", Mf(t, "MULTIPLY", wave, fade), wedge)
            total = term if total is None else Mf(t, "ADD", total, term)
    return total


def gesso(name, painting=None, colour=(0.80, 0.79, 0.765), face=None):
    """Cotton duck primed with acrylic gesso: slightly warm white, matte, the weave just showing through
    the coats (the crowns of the threads stand a little proud and catch the light, the hollows are
    filled), faint brush ridges from priming, and a gentle unevenness in the coat. painting: an image
    path; it then colours the face through the UVs (0..1 over the front) and the weave stays."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co, nrm = out(tc, "Object"), out(tc, "Normal")
    a, b = _face_coords(t, co, nrm)
    h = weave(t, a, b)
    # gesso fills the hollows: the height flattens toward the top of the threads
    hg = Mf(t, "POWER", h, 0.55)
    strokes = out(N(t, "ShaderNodeTexNoise", V(t, "MULTIPLY", co, (0.25, 1.0, 6.0)), Scale=55.0, Detail=3.0,
                    Roughness=0.55), "Factor")
    coat = out(N(t, "ShaderNodeTexNoise", co, Scale=4.0, Detail=3.0, Roughness=0.55), "Factor")
    tooth = out(N(t, "ShaderNodeTexNoise", co, Scale=4000.0, Detail=1.0), "Factor")
    if painting:
        img = N(t, "ShaderNodeTexImage", _image=bpy.data.images.load(painting, check_existing=True),
                _extension="EXTEND", _interpolation="Cubic")
        t.links.new(out(tc, "UV"), img.inputs["Vector"])
        base = out(img)
    else:
        base = (*colour, 1)
    # the crowns of the threads, thinly covered, show a trace of the cotton's cream
    col = mix_rgb(t, Mf(t, "MULTIPLY", maprange(t, h, 0.75, 1.0, 0.0, 1.0), 0.07), base, (0.70, 0.62, 0.50, 1))
    # the interstices, though filled, sit a hair lower and catch a little less light
    col = mix_rgb(t, Mf(t, "MULTIPLY", maprange(t, h, 0.35, 0.0, 0.0, 1.0), 0.06), col, (0.0, 0.0, 0.0, 1))
    col = mix_rgb(t, Mf(t, "MULTIPLY", maprange(t, coat, 0.3, 0.7, 0.0, 1.0), 0.05), col, (0.74, 0.725, 0.69, 1))
    r = Mf(t, "ADD", 0.70, maprange(t, h, 0.2, 1.0, 0.06, -0.06))
    r = Mf(t, "ADD", r, maprange(t, coat, 0.3, 0.7, -0.03, 0.03))
    bump = N(t, "ShaderNodeBump", Strength=0.55, Distance=0.00012, Height=hg)
    bump = N(t, "ShaderNodeBump", Strength=0.25, Distance=0.0002, Height=strokes, Normal=out(bump))
    bump = N(t, "ShaderNodeBump", Strength=0.08, Distance=0.00003, Height=tooth, Normal=out(bump))
    # the face is not quite a plane: a faint unevenness of tension, and the pull at the corners
    bump = N(t, "ShaderNodeBump", Strength=0.2, Distance=0.0006, Height=coat, Normal=out(bump))
    if face:
        nx, ny, nz = xyz(t, nrm)
        front = maprange(t, Mf(t, "ABSOLUTE", ny), 0.6, 0.9, 0.0, 1.0)
        bump = N(t, "ShaderNodeBump", Strength=0.5, Distance=0.00035,
                 Height=Mf(t, "MULTIPLY", corner_pull(t, co, face), front), Normal=out(bump))
    # where oil paint lies (painting.py's <name>_paint.png: R = cover, G = paint height), it is glossier
    # than the matte primer and its strokes stand a little proud of the weave
    paint_map = painting[:-4] + "_paint.png" if painting else None
    if paint_map and os.path.exists(paint_map):
        pm = N(t, "ShaderNodeTexImage", _image=bpy.data.images.load(paint_map, check_existing=True),
               _extension="EXTEND", _interpolation="Cubic")
        pm.image.colorspace_settings.name = "Non-Color"
        t.links.new(out(tc, "UV"), pm.inputs["Vector"])
        cov, ph, _ = xyz(t, out(pm))
        r = Mf(t, "ADD", Mf(t, "MULTIPLY", r, Mf(t, "SUBTRACT", 1.0, cov)), Mf(t, "MULTIPLY", cov, 0.40))
        bump = N(t, "ShaderNodeBump", Strength=0.35, Distance=0.0005, Height=Mf(t, "MULTIPLY", ph, cov), Normal=out(bump))
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.45,
                     "Sheen Weight": 0.15, "Sheen Roughness": 0.5})
    return m


def raw_canvas(name):
    """The unprimed back of the cotton duck: oatmeal, fibrous, the weave plain to see."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co, nrm = out(tc, "Object"), out(tc, "Normal")
    a, b = _face_coords(t, co, nrm)
    h = weave(t, a, b)
    fuzz = out(N(t, "ShaderNodeTexNoise", co, Scale=900.0, Detail=4.0, Roughness=0.7), "Factor")
    col = mix_rgb(t, maprange(t, h, 0.1, 1.0, 0.0, 1.0), (0.36, 0.30, 0.22, 1), (0.56, 0.48, 0.37, 1))
    col = mix_rgb(t, Mf(t, "MULTIPLY", fuzz, 0.2), col, (0.62, 0.55, 0.44, 1))
    # size from the priming has soaked through here and there: faint, slightly darker blotches
    blot = maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=7.0, Detail=3.0), "Factor"), 0.5, 0.7, 0.0, 0.25)
    col = mix_rgb(t, blot, col, (0.40, 0.33, 0.24, 1))
    bump = N(t, "ShaderNodeBump", Strength=0.8, Distance=0.0002, Height=h)
    principled(t, **{"Base Color": col, "Roughness": 0.88, "Normal": out(bump), "Specular IOR Level": 0.3,
                     "Sheen Weight": 0.5, "Sheen Roughness": 0.5})
    return m


def metal(name, colour, rough=0.28, tarnish=(0.36, 0.25, 0.11), knurl=None, brushed=False):
    """Brass or plated steel: an even satin with fine variation, tarnish gathering in the crevices,
    worn bright on the edges a hand touches."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co = out(tc, "Object")
    fine = out(N(t, "ShaderNodeTexNoise", co, Scale=900.0, Detail=3.0), "Factor")
    blot = out(N(t, "ShaderNodeTexNoise", co, Scale=120.0, Detail=4.0, Roughness=0.6), "Factor")
    ao = out(N(t, "ShaderNodeAmbientOcclusion", Distance=0.003, _only_local=True, _samples=8), "AO")
    crev = maprange(t, ao, 0.55, 0.95, 1.0, 0.0)
    tf = Mf(t, "MAXIMUM", maprange(t, blot, 0.52, 0.75, 0.0, 0.35), Mf(t, "MULTIPLY", crev, 0.8))
    col = mix_rgb(t, tf, (*colour, 1), (*tarnish, 1))
    r = Mf(t, "ADD", rough, Mf(t, "ADD", Mf(t, "MULTIPLY", tf, 0.18), maprange(t, fine, 0.3, 0.7, -0.03, 0.03)))
    edge = out(N(t, "ShaderNodeAmbientOcclusion", Distance=0.0015, _only_local=True, _inside=True, _samples=8), "AO")
    rub = Mf(t, "MULTIPLY", maprange(t, edge, 0.75, 0.98, 1.0, 0.0), 0.5)
    col = mix_rgb(t, rub, col, (min(1, colour[0] * 1.08), min(1, colour[1] * 1.08), min(1, colour[2] * 1.08), 1))
    r = mix_f(t, rub, r, rough * 0.55)
    kw = {"Base Color": col, "Metallic": 1.0, "Roughness": r}
    nrm = None
    if knurl:
        # straight knurling round the edge of a turned knob (local z is its axis)
        x, y, z = xyz(t, co)
        at = N(t, "ShaderNodeMath", _operation="ARCTAN2")
        t.links.new(y, at.inputs[0])
        t.links.new(x, at.inputs[1])
        lines = Mf(t, "SINE", Mf(t, "MULTIPLY", out(at), knurl))
        nrm = out(N(t, "ShaderNodeBump", Strength=0.6, Distance=0.0002, Height=lines))
    if brushed:
        streak = out(N(t, "ShaderNodeTexNoise", V(t, "MULTIPLY", co, (1.0, 60.0, 1.0)), Scale=700.0, Detail=2.0), "Factor")
        r = Mf(t, "ADD", r, maprange(t, streak, 0.3, 0.7, -0.03, 0.05))
        nrm = out(N(t, "ShaderNodeBump", Strength=0.04, Distance=0.00002, Height=streak))
        kw["Roughness"] = r
    if nrm is not None:
        kw["Normal"] = nrm
    principled(t, **kw)
    return m


def phenolic(name, colour=(0.018, 0.017, 0.016), rough=0.32):
    """Black moulded phenolic, as on a clamp knob: a soft gloss with faint mould marks."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    var = out(N(t, "ShaderNodeTexNoise", co, Scale=300.0, Detail=3.0), "Factor")
    r = Mf(t, "ADD", rough, maprange(t, var, 0.3, 0.7, -0.05, 0.06))
    bump = N(t, "ShaderNodeBump", Strength=0.05, Distance=0.00005, Height=var)
    principled(t, **{"Base Color": (*colour, 1), "Roughness": r, "Specular IOR Level": 0.5, "Normal": out(bump)})
    return m
