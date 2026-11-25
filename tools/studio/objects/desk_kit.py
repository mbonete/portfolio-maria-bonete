# Shared by desk_frame.py and monitors.py (not an object of its own): meshes built at their true size
# (no object scale, so bevels stay even), a small node-tree shorthand, and the materials the desk's parts
# share: black powder-coated steel, dark plastic, rubber and bright zinc.
import bpy, bmesh, math, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")


# The cable tray under the top's back edge (desk_frame builds it, monitors.py drops its leads into it):
# x span, y span (front wall, back lip), its floor's height below the top's underside, the back lip's
# height below the underside. The monitor leads come over the back edge, over the lip and into it.
TRAY_X = (-0.62, 0.78)
TRAY_Y = (0.235, 0.368)
TRAY_DROP = 0.105
TRAY_LIP = 0.050

# ---------------------------------------------------------------- geometry

def rrect(w, h, r, seg=6, cx=0.0, cy=0.0):
    """A rounded rectangle's outline, counter-clockwise, as 2D points."""
    r = min(r, w / 2, h / 2)
    if r < 1e-6:
        return [(cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2), (cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2)]
    pts = []
    for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox, oy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            p = (ox + r * math.cos(a), oy + r * math.sin(a))
            if not pts or (abs(p[0] - pts[-1][0]) + abs(p[1] - pts[-1][1])) > 1e-7:
                pts.append(p)
    if (abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1])) < 1e-7:
        pts.pop()
    return pts


def ellipse(w, h, seg=48, cx=0.0, cy=0.0):
    return [(cx + w / 2 * math.cos(2 * math.pi * k / seg), cy + h / 2 * math.sin(2 * math.pi * k / seg)) for k in range(seg)]


def _place(p, d, axis):
    """A 2D outline point p and a depth d along axis -> 3D. axis 'z': (x, y) at z = d; 'x': (y, z) at
    x = d; 'y': (x, z) at y = d."""
    a, b = p
    return {"z": (a, b, d), "x": (d, a, b), "y": (a, d, b)}[axis]


def prism(pts, d0, d1, axis="z", bm=None):
    """An outline extruded from d0 to d1 along an axis, capped both ends."""
    bm = bm or bmesh.new()
    lo = [bm.verts.new(_place(p, d0, axis)) for p in pts]
    hi = [bm.verts.new(_place(p, d1, axis)) for p in pts]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bm.faces.new(hi)
    bm.faces.new(lo[::-1])
    return bm


def loft(sections, axis="z", caps=(True, True), bm=None):
    """Outlines of equal point count at successive depths [(pts, d), ...], bridged into one surface."""
    bm = bm or bmesh.new()
    rings = [[bm.verts.new(_place(p, d, axis)) for p in pts] for pts, d in sections]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if caps[0]:
        bm.faces.new(rings[0][::-1])
    if caps[1]:
        bm.faces.new(rings[-1])
    return bm


def cylinder(r, z0, z1, seg=40, bm=None, cx=0.0, cy=0.0, axis="z"):
    return prism(ellipse(2 * r, 2 * r, seg, cx, cy), z0, z1, axis, bm)


def transform(bm, m):
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return bm


def mesh_object(name, bm, mats, bevel=0.0, segs=3, sharp=30, bevel_mat=None, smooth=True, limit=None):
    """A mesh object from a bmesh, smooth-shaded with hard edges kept sharp, and a bevel modifier that
    rounds every edge sharper than `sharp` degrees (or `limit`) by `bevel` metres."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if smooth:
        me.shade_smooth()
        me.set_sharp_from_angle(angle=math.radians(sharp))
    if bevel:
        md = ob.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = segs
        md.limit_method = "ANGLE"
        md.angle_limit = math.radians(limit if limit is not None else sharp)
        md.harden_normals = True
        md.use_clamp_overlap = True
        if bevel_mat is not None:
            md.material = bevel_mat
    return ob


def curve_tube(name, pts, radius, mat, res=12, smooth_pts=True):
    """A cable: a bezier through 3D points with a round bevel."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 4
    cu.resolution_u = res
    cu.use_fill_caps = True
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for bp, p in zip(sp.bezier_points, pts):
        bp.co = p
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(mat)
    return ob


# ---------------------------------------------------------------- node shorthand

def _put(t, sock, v):
    if isinstance(v, bpy.types.NodeSocket):
        t.links.new(v, sock)
    elif isinstance(v, bpy.types.Node):
        t.links.new(out(v), sock)
    else:
        sock.default_value = v


def _sock(coll, key):
    if isinstance(key, int):
        return [s for s in coll if s.enabled][key]
    for s in coll:
        if s.identifier == key and s.enabled:
            return s
    for s in coll:
        if s.name == key and s.enabled:
            return s
    raise KeyError(key)


def N(t, kind, *args, **kw):
    """A node of type `kind` in tree t. Keywords starting with '_' set node properties (first); the rest,
    and positional arguments, feed inputs (by identifier, name or index among enabled sockets) with a
    value or a socket/node to link from."""
    n = t.nodes.new(kind)
    for k, v in kw.items():
        if k.startswith("_"):
            setattr(n, k[1:], v)
    for i, v in enumerate(args):
        if v is not None:
            _put(t, _sock(n.inputs, i), v)
    for k, v in kw.items():
        if not k.startswith("_"):
            _put(t, _sock(n.inputs, k), v)
    return n


def out(n, key=0):
    return _sock(n.outputs, key)


def M(t, op, a, b=None, c=None, clamp=False):
    """Math node output."""
    n = N(t, "ShaderNodeMath", _operation=op, _use_clamp=clamp)
    _put(t, n.inputs[0], a)
    if b is not None:
        _put(t, n.inputs[1], b)
    if c is not None:
        _put(t, n.inputs[2], c)
    return n.outputs[0]


def V(t, op, a, b=None, scale=None):
    n = N(t, "ShaderNodeVectorMath", _operation=op)
    _put(t, n.inputs[0], a)
    if b is not None:
        _put(t, n.inputs[1], b)
    if scale is not None:
        _put(t, n.inputs[3], scale)
    return out(n, "Value") if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else out(n, "Vector")


def mix_rgb(t, fac, a, b, blend="MIX"):
    n = N(t, "ShaderNodeMix", _data_type="RGBA", _blend_type=blend, Factor_Float=fac, A_Color=a, B_Color=b)
    return out(n, "Result_Color")


def mix_f(t, fac, a, b):
    n = N(t, "ShaderNodeMix", _data_type="FLOAT", Factor_Float=fac, A_Float=a, B_Float=b)
    return out(n, "Result_Float")


def maprange(t, v, a, b, c, d, clamp=True, interp="LINEAR"):
    return out(N(t, "ShaderNodeMapRange", v, a, b, c, d, _clamp=clamp, _interpolation_type=interp), "Result")


def xyz(t, vec):
    n = N(t, "ShaderNodeSeparateXYZ", vec)
    return n.outputs[0], n.outputs[1], n.outputs[2]


def comb(t, x, y, z=0.0):
    return out(N(t, "ShaderNodeCombineXYZ", x, y, z))


def image(path, colour=True):
    path = path if os.path.isabs(path) else os.path.join(ASSETS, path)
    img = bpy.data.images.load(path, check_existing=True)
    if not colour:
        img.colorspace_settings.name = "Non-Color"
    return img


def tex(t, path, vec, colour=True, box=0.0, extension="REPEAT", interp="Linear"):
    """An image texture lookup; box > 0 projects it from the three axes with that blend."""
    n = N(t, "ShaderNodeTexImage", _image=image(path, colour), _extension=extension, _interpolation=interp)
    if box:
        n.projection = "BOX"
        n.projection_blend = box
    _put(t, n.inputs["Vector"], vec)
    return n


def new_material(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    t = m.node_tree
    for n in list(t.nodes):
        t.nodes.remove(n)
    return m, t


def shared(name, maker):
    """One material per name for the whole desk group."""
    return bpy.data.materials.get(name) or maker(name)


def principled(t, mat_out=True, **kw):
    p = N(t, "ShaderNodeBsdfPrincipled", **kw)
    if mat_out:
        o = N(t, "ShaderNodeOutputMaterial")
        t.links.new(p.outputs[0], o.inputs["Surface"])
    return p


# ---------------------------------------------------------------- shared materials

def _powder(name, edge=False):
    """Black powder-coated steel: a fine orange-peel texture, satin sheen and faint handling marks. The
    edge variant (the bevel strips) is a touch lighter and glossier where the coat has worn thin."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    v = V(t, "SCALE", co, scale=1 / 0.18)
    disp = tex(t, "ambientcg/Metal027/Metal027_2K-JPG_Displacement.jpg", v, False, box=0.3)
    rgh = tex(t, "ambientcg/Metal027/Metal027_2K-JPG_Roughness.jpg", v, False, box=0.3)
    # orange peel at the scale of a real coat (a few mm), on top of the map's own grain
    peel = out(N(t, "ShaderNodeTexNoise", co, Scale=700.0, Detail=2.0, Roughness=0.5), "Factor")
    wave = out(N(t, "ShaderNodeTexNoise", co, Scale=160.0, Detail=1.0), "Factor")
    h = M(t, "ADD", M(t, "ADD", M(t, "MULTIPLY", out(disp), 0.5), M(t, "MULTIPLY", peel, 0.35)), M(t, "MULTIPLY", wave, 0.5))
    bump = N(t, "ShaderNodeBump", Strength=0.22, Distance=0.0005, Height=h)
    # scratches: the map's darkest lines, as a slightly lighter, glossier trace
    scr = maprange(t, out(disp), 0.18, 0.34, 1.0, 0.0)
    smudge = out(N(t, "ShaderNodeTexNoise", co, Scale=7.0, Detail=4.0, Roughness=0.6), "Factor")
    r = maprange(t, out(rgh), 0.55, 0.75, 0.40, 0.56)
    r = M(t, "ADD", r, maprange(t, smudge, 0.35, 0.65, -0.06, 0.05))
    r = mix_f(t, M(t, "MULTIPLY", scr, 0.6), r, 0.30)
    base = mix_rgb(t, M(t, "MULTIPLY", scr, 0.5), (0.020, 0.020, 0.022, 1), (0.055, 0.055, 0.058, 1))
    if edge:
        wear = maprange(t, out(N(t, "ShaderNodeTexNoise", co, Scale=60.0, Detail=6.0, Roughness=0.7), "Factor"), 0.45, 0.62, 0.0, 1.0)
        base = mix_rgb(t, M(t, "MULTIPLY", wear, 0.7), base, (0.075, 0.074, 0.072, 1))
        r = mix_f(t, wear, M(t, "MULTIPLY", r, 0.85), 0.26)
    principled(t, **{"Base Color": base, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.5})
    return m


def powder():
    return shared("powder coat", lambda n: _powder(n))


def powder_edge():
    return shared("powder coat edge", lambda n: _powder(n, edge=True))


def _plastic(name, colour, rough, grain=0.12, scale=0.08, bump=0.04):
    """Moulded plastic with a fine leather-like grain (as on monitor housings)."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    v = V(t, "SCALE", co, scale=1 / scale)
    disp = tex(t, "ambientcg/Plastic012A/Plastic012A_2K-JPG_Displacement.jpg", v, False, box=0.3)
    bm = N(t, "ShaderNodeBump", Strength=bump, Distance=0.0003, Height=out(disp))
    var = out(N(t, "ShaderNodeTexNoise", co, Scale=12.0, Detail=3.0), "Factor")
    r = M(t, "ADD", rough, maprange(t, out(disp), 0.0, 1.0, -grain / 2, grain / 2))
    r = M(t, "ADD", r, maprange(t, var, 0.3, 0.7, -0.04, 0.04))
    principled(t, **{"Base Color": (*colour, 1), "Roughness": r, "Normal": out(bm), "Specular IOR Level": 0.5})
    return m


def plastic(name="dark plastic", colour=(0.016, 0.016, 0.018), rough=0.45, **kw):
    return shared(name, lambda n: _plastic(n, colour, rough, **kw))


def _simple(name, colour, rough, metal=0.0, spec=0.5, sheen=0.0):
    m, t = new_material(name)
    principled(t, **{"Base Color": (*colour, 1), "Roughness": rough, "Metallic": metal,
                     "Specular IOR Level": spec, "Sheen Weight": sheen})
    return m


def rubber():
    return shared("rubber", lambda n: _simple(n, (0.012, 0.012, 0.012), 0.72, sheen=0.15))


def zinc():
    return shared("zinc", lambda n: _simple(n, (0.62, 0.63, 0.66), 0.32, metal=1.0))


def black_steel():
    return shared("black screw", lambda n: _simple(n, (0.03, 0.03, 0.032), 0.35, metal=0.8))
