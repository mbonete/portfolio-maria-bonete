# The folding screen: a four-panel byobu, built new (owner's brief, 2026-11-26: a Japanese byobu keeping the
# old hero's gold painting; the screen ported from that hero threw straight yellow reflections off its gold
# piping and brass fittings, and neither is here).
#
# Built as a byobu is. Each panel is a light core faced with paper and edged in a slim black-lacquer frame
# with rounded arrises, satin rather than mirror, so the frame catches a soft line of light, never a flat
# band. The panels are joined by paper hinges: nothing metal shows, there are no corner fittings, and the
# panels stand straight on the floor. The painting runs on across the folds; a band of dark indigo brocade
# runs along the top and the bottom of every panel and down the screen's two outer ends.
#
# The painting is the old hero's (tools/gold-screen/paint.py, p3/, and its face material, node for node):
# burnished gold leaf laid in squares, gold dust and cut leaf; the murasaki stream from the top of panel 1
# across the fold into panel 2 with its gold current lines; the sumi plum in bloom on panels 3 and 4. Its
# straight-edged mist bands are left off, relief and all (owner, 2026-11-26). The backs are a plain
# dark-green paper. (A cinnabar ground was tried and turned down,
# 2026-11-26.)
#
# Pose: the stand-in's zigzag (standins.screen): panels 1 and 2 fold together, 2 and 3 apart, 3 and 4
# together, centred on x with the front folds at y = -0.25. Every fold turns on a hinge at the edge of the
# faces that close together (the fronts for a valley fold, the backs for a mountain fold), and the fold
# angle is solved so the screen spans the stand-in's width; the placement in common.py stays right.
import bpy, math, os
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.normpath(os.path.join(HERE, "..", "..", "gold-screen", "p3"))   # paint.py's output; gitignored

# ---------- sizes (metres) ----------
PW, PH = 1.0, 1.6          # a panel
T = 0.030                  # its thickness
FR = 0.022                 # the lacquer frame's face
REC = 0.004                # how far the paper sits back from the frame's face
BR = 0.034                 # the brocade band
STANDIN_WIDTH = 4 * PW * math.cos(math.radians(74))   # the stand-in's outer ends, 1.103 m apart
FRONT_Y = -0.25            # the stand-in's front folds

# ---------- the gold, as the old hero's open still unless noted ----------
GESSO = 0.14              # the gesso showing through the leaf
# Folded to 75 degrees, the camera sees most of the leaf in the facing panel's mirror, gold in gold two or
# three times over, which compounds into copper. The leaf seen in a reflection is taken this far toward
# grey, so the folds keep a burnished gold.
GOLD_IN_GOLD = 0.5
STREAM_COAT = 0.25        # the murasaki's coat (hero 0.6, seen square on; at 74 degrees it would wash to lavender)
SUMI_GREEN = (0.020, 0.032, 0.022)  # the backs


# =============================================================================================
# materials
# =============================================================================================
def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n, l = m.node_tree.nodes, m.node_tree.links
    return m, n, l, n["Principled BSDF"]


def _lacquer():
    """Black urushi, polished to a satin: one glossy surface (the pigment is in the lacquer, nothing
    reflects from beneath), its highlight broad and soft."""
    m, n, l, p = _mat("screen lacquer")
    p.inputs["Base Color"].default_value = (0.011, 0.008, 0.008, 1)
    p.inputs["Roughness"].default_value = 0.4
    p.inputs["Specular IOR Level"].default_value = 0.0
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.16
    # the faint unevenness of hand-rubbed lacquer
    tc = n.new("ShaderNodeTexCoord")
    nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 30; nz.inputs["Detail"].default_value = 3
    l.new(tc.outputs["Object"], nz.inputs["Vector"])
    b = n.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.03
    l.new(nz.outputs["Fac"], b.inputs["Height"]); l.new(b.outputs["Normal"], p.inputs["Coat Normal"])
    return m


def _brocade():
    """Dark indigo silk woven with a small lozenge in a slightly lighter blue-green, a soft sheen, no gold."""
    m, n, l, p = _mat("screen brocade")
    tc = n.new("ShaderNodeTexCoord")
    sep = n.new("ShaderNodeSeparateXYZ"); l.new(tc.outputs["Object"], sep.inputs[0])

    def lin(a, b, k):
        s_ = n.new("ShaderNodeMath"); s_.operation = "MULTIPLY_ADD"; s_.inputs[1].default_value = k
        l.new(a, s_.inputs[0]); l.new(b, s_.inputs[2]); return s_.outputs[0]

    def tri(x):   # a triangle wave, lozenges 13 mm across on the band's plane (object x, y in metres)
        k_ = n.new("ShaderNodeMath"); k_.operation = "MULTIPLY"; k_.inputs[1].default_value = 1 / 0.0065
        l.new(x, k_.inputs[0])
        w = n.new("ShaderNodeMath"); w.operation = "PINGPONG"; w.inputs[1].default_value = 0.5
        l.new(k_.outputs[0], w.inputs[0]); return w.outputs[0]

    u = lin(sep.outputs["X"], sep.outputs["Y"], 1.0)
    v = n.new("ShaderNodeMath"); v.operation = "SUBTRACT"; l.new(sep.outputs["X"], v.inputs[0]); l.new(sep.outputs["Y"], v.inputs[1])
    lz = n.new("ShaderNodeMath"); lz.operation = "MINIMUM"; l.new(tri(u), lz.inputs[0]); l.new(tri(v.outputs[0]), lz.inputs[1])
    edge = n.new("ShaderNodeMapRange"); edge.inputs["From Min"].default_value = 0.10; edge.inputs["From Max"].default_value = 0.16
    l.new(lz.outputs[0], edge.inputs["Value"])
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = (0.012, 0.016, 0.040, 1); mix.inputs[7].default_value = (0.020, 0.040, 0.050, 1)
    l.new(edge.outputs["Result"], mix.inputs[0]); l.new(mix.outputs[2], p.inputs["Base Color"])
    weave = n.new("ShaderNodeTexWave"); weave.wave_type = "BANDS"; weave.inputs["Scale"].default_value = 900
    weave.inputs["Distortion"].default_value = 1.2; l.new(tc.outputs["Object"], weave.inputs["Vector"])
    wb = n.new("ShaderNodeBump"); wb.inputs["Strength"].default_value = 0.10
    l.new(weave.outputs["Fac"], wb.inputs["Height"]); l.new(wb.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.55
    p.inputs["Sheen Weight"].default_value = 0.6
    p.inputs["Sheen Tint"].default_value = (0.5, 0.65, 1.0, 1)
    p.inputs["Specular IOR Level"].default_value = 0.3
    return m


def _paper_fibres(n, l, vec, scale=55, strength=0.10):
    """A net of kozo fibres under the surface, as a bump: Voronoi cell edges on warped coordinates."""
    warp = n.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 40; l.new(vec, warp.inputs["Vector"])
    wadd = n.new("ShaderNodeVectorMath"); wadd.operation = "MULTIPLY_ADD"; wadd.inputs[1].default_value = (0.012,) * 3
    l.new(warp.outputs["Color"], wadd.inputs[0]); l.new(vec, wadd.inputs[2])
    fib = n.new("ShaderNodeTexVoronoi"); fib.feature = "DISTANCE_TO_EDGE"; fib.inputs["Scale"].default_value = scale
    l.new(wadd.outputs["Vector"], fib.inputs["Vector"])
    fl = n.new("ShaderNodeMapRange"); fl.inputs["From Max"].default_value = 0.035
    fl.inputs["To Min"].default_value = 1.0; fl.inputs["To Max"].default_value = 0.0; fl.interpolation_type = "SMOOTHSTEP"
    l.new(fib.outputs["Distance"], fl.inputs["Value"])
    b = n.new("ShaderNodeBump"); b.inputs["Strength"].default_value = strength; b.inputs["Distance"].default_value = 0.0004
    l.new(fl.outputs["Result"], b.inputs["Height"])
    return b


def _back():
    """The backs: a plain dark-green paper with its fibres."""
    m, n, l, p = _mat("screen back paper")
    tc = n.new("ShaderNodeTexCoord")
    form = n.new("ShaderNodeTexNoise"); form.inputs["Scale"].default_value = 20; form.inputs["Detail"].default_value = 6
    l.new(tc.outputs["Object"], form.inputs["Vector"])
    mix = n.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs[6].default_value = (*SUMI_GREEN, 1); mix.inputs[7].default_value = (0.030, 0.044, 0.030, 1)
    l.new(form.outputs["Fac"], mix.inputs[0]); l.new(mix.outputs[2], p.inputs["Base Color"])
    l.new(_paper_fibres(n, l, tc.outputs["Object"], 34, 0.1).outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.85
    p.inputs["Sheen Weight"].default_value = 0.08
    return m


def _painting():
    """The painted gold: per-leaf tone, overlaps, patina and burnish; gold dust and cut leaf; the murasaki stream under a light coat with its gold current lines; the matte paint of
    the plum. Node for node the old hero's face material (tools/gold-screen/scene.py, PAPER off)."""
    face, n, l, p = _mat("screen gold leaf")
    n.remove(p)
    uv = n.new("ShaderNodeTexCoord")

    def img(name, color=False):
        t = n.new("ShaderNodeTexImage")
        t.image = bpy.data.images.load(os.path.join(TEX, name), check_existing=True)
        if not color:
            t.image.colorspace_settings.name = "Non-Color"
        t.interpolation = "Cubic"; l.new(uv.outputs["UV"], t.inputs["Vector"])
        return t

    def split(t):
        s_ = n.new("ShaderNodeSeparateColor"); l.new(t.outputs["Color"], s_.inputs["Color"]); return s_

    def mixc(fac, a, b):
        m_ = n.new("ShaderNodeMix"); m_.data_type = "RGBA"
        for sock, v in ((m_.inputs[0], fac), (m_.inputs[6], a), (m_.inputs[7], b)):
            if isinstance(v, tuple): sock.default_value = v
            else: l.new(v, sock)
        return m_.outputs[2]

    def mixs(fac, a, b):
        m_ = n.new("ShaderNodeMixShader")
        if isinstance(fac, float): m_.inputs["Fac"].default_value = fac
        else: l.new(fac, m_.inputs["Fac"])
        l.new(a, m_.inputs[1]); l.new(b, m_.inputs[2]); return m_.outputs["Shader"]

    def bsdf(col, metal, rough, normal=None, **kw):
        b_ = n.new("ShaderNodeBsdfPrincipled")
        if isinstance(col, tuple): b_.inputs["Base Color"].default_value = col
        else: l.new(col, b_.inputs["Base Color"])
        b_.inputs["Metallic"].default_value = metal
        if isinstance(rough, float): b_.inputs["Roughness"].default_value = rough
        else: l.new(rough, b_.inputs["Roughness"])
        for k_, v_ in kw.items(): b_.inputs[k_].default_value = v_
        if normal is not None: l.new(normal, b_.inputs["Normal"])
        return b_.outputs["BSDF"]

    def metal(col, rough, normal=None):
        # a pure metal: the Principled BSDF's own F82 conductor (white edge tint), as one closure; the
        # leaf's many layers would otherwise exceed Cycles' 64 closures per shader
        b_ = n.new("ShaderNodeBsdfMetallic"); b_.fresnel_type = "F82"
        b_.inputs["Edge Tint"].default_value = (1, 1, 1, 1)
        if isinstance(col, tuple): b_.inputs["Base Color"].default_value = col
        else: l.new(col, b_.inputs["Base Color"])
        if isinstance(rough, float): b_.inputs["Roughness"].default_value = rough
        else: l.new(rough, b_.inputs["Roughness"])
        if normal is not None: l.new(normal, b_.inputs["Normal"])
        return b_.outputs["BSDF"]

    def diffuse(col, normal=None):
        d_ = n.new("ShaderNodeBsdfDiffuse")
        if isinstance(col, tuple): d_.inputs["Color"].default_value = col
        else: l.new(col, d_.inputs["Color"])
        if normal is not None: l.new(normal, d_.inputs["Normal"])
        return d_.outputs["BSDF"]

    leaf = split(img("leaf.png")); det = split(img("detail.png")); sep = split(img("stream.png"))
    artT = img("art.png", True)
    # each leaf its own gold, within a narrow range; the overlap of one leaf on the next reads as a
    # slightly deeper strip; old-gold patina in broad blotches
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.87, 0.62, 0.265, 1); ramp.color_ramp.elements[1].color = (0.93, 0.685, 0.30, 1)
    l.new(leaf.outputs["Red"], ramp.inputs["Fac"])
    patina = n.new("ShaderNodeTexNoise"); l.new(uv.outputs["UV"], patina.inputs["Vector"])
    patina.inputs["Scale"].default_value = 3.5; patina.inputs["Detail"].default_value = 6; patina.inputs["Roughness"].default_value = 0.6
    pat = n.new("ShaderNodeMapRange"); pat.inputs["From Min"].default_value = 0.5; pat.inputs["From Max"].default_value = 0.78
    l.new(patina.outputs["Fac"], pat.inputs["Value"])
    c1 = mixc(pat.outputs["Result"], ramp.outputs["Color"], (0.64, 0.48, 0.23, 1))
    seamk = n.new("ShaderNodeMath"); seamk.operation = "MULTIPLY"; seamk.inputs[1].default_value = 0.45
    l.new(leaf.outputs["Green"], seamk.inputs[0])
    goldc = mixc(seamk.outputs["Value"], c1, (0.66, 0.46, 0.19, 1))
    if GOLD_IN_GOLD:     # the leaf as a reflection sees it (glossy depth 1 and up), part way to its own grey
        lp = n.new("ShaderNodeLightPath")
        gt = n.new("ShaderNodeMath"); gt.operation = "GREATER_THAN"; gt.inputs[1].default_value = 0.5
        l.new(lp.outputs["Glossy Depth"], gt.inputs[0])
        k_ = n.new("ShaderNodeMath"); k_.operation = "MULTIPLY"; k_.inputs[1].default_value = GOLD_IN_GOLD
        l.new(gt.outputs[0], k_.inputs[0])
        bw = n.new("ShaderNodeRGBToBW"); l.new(goldc, bw.inputs[0])
        grey = n.new("ShaderNodeCombineColor")
        for j in range(3):
            l.new(bw.outputs[0], grey.inputs[j])
        goldc = mixc(k_.outputs[0], goldc, grey.outputs[0])
    rough = n.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value = 0.12; rough.inputs["To Max"].default_value = 0.34
    l.new(patina.outputs["Fac"], rough.inputs["Value"])
    burn = n.new("ShaderNodeMath"); burn.operation = "MULTIPLY_ADD"; burn.inputs[1].default_value = 0.03
    l.new(leaf.outputs["Blue"], burn.inputs[0]); l.new(rough.outputs["Result"], burn.inputs[2])
    crinkle = n.new("ShaderNodeTexNoise"); crinkle.inputs["Scale"].default_value = 260; crinkle.inputs["Detail"].default_value = 4
    l.new(uv.outputs["UV"], crinkle.inputs["Vector"])
    b1 = n.new("ShaderNodeBump"); b1.inputs["Strength"].default_value = 0.035; l.new(crinkle.outputs["Fac"], b1.inputs["Height"])
    # relief: raised gesso clouds, gofun blossoms, the gold lines stand a hair proud
    b2 = n.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = 0.6
    b2.inputs["Distance"].default_value = 0.0012
    # (the mist bands' raised gesso goes with the bands: their mask, stream.png's blue, takes it out)
    nob = n.new("ShaderNodeMath"); nob.operation = "SUBTRACT"; nob.inputs[0].default_value = 1.0
    l.new(sep.outputs["Blue"], nob.inputs[1])
    rel = n.new("ShaderNodeMath"); rel.operation = "MULTIPLY"
    l.new(det.outputs["Green"], rel.inputs[0]); l.new(nob.outputs[0], rel.inputs[1])
    l.new(rel.outputs[0], b2.inputs["Height"]); l.new(b1.outputs["Normal"], b2.inputs["Normal"])
    NRM = b2.outputs["Normal"]
    ground = mixs(GESSO, metal(goldc, burn.outputs["Value"], NRM), diffuse(goldc, NRM))
    # the painting's mist bands are left off: their pale gold blocks read as stray reflections (owner, 2026-11-26)
    sh = ground
    # dust and cut leaf: bright fresh leaf, burnished
    sh = mixs(det.outputs["Blue"], sh, mixs(0.3, metal((1.0, 0.82, 0.48, 1), 0.2, NRM), diffuse((0.98, 0.82, 0.5, 1), NRM)))
    # stream: murasaki with settled pigment, under a light coat
    vcol = mixc(det.outputs["Red"], (0.062, 0.024, 0.19, 1), (0.105, 0.048, 0.28, 1))
    # (the hero's coat was 0.6, seen square on; at the studio's 74 degrees it mirrors the facing gold and
    # washes the violet out to lavender)
    sh = mixs(sep.outputs["Red"], sh, bsdf(vcol, 0.0, 0.42, NRM, **{"Coat Weight": STREAM_COAT, "Coat Roughness": 0.15,
                                                                    "Specular IOR Level": 0.3}))
    sh = mixs(sep.outputs["Green"], sh, mixs(0.45, metal((0.98, 0.84, 0.52, 1), 0.25, NRM), diffuse((0.95, 0.80, 0.50, 1), NRM)))
    # paint: matte
    paint = bsdf(artT.outputs["Color"], 0.0, 0.85, NRM, **{"Specular IOR Level": 0.12})
    sh = mixs(artT.outputs["Alpha"], sh, paint)
    l.new(sh, n["Material Output"].inputs["Surface"])
    return face


# =============================================================================================
# geometry
# =============================================================================================
def _box(name, size, loc, rz, m, bevel=0.0, segs=4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rz))
    ob = bpy.context.active_object; ob.name = name; ob.scale = size; ob.data.materials.append(m)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = segs; bv.harden_normals = True
        bpy.ops.object.shade_smooth()
    return ob


def _plane(name, w, h, loc, a, m, back=False, apply=False):
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.name = name; ob.scale = (w, h, 1)
    ob.rotation_euler = (math.radians(-90 if back else 90), 0, a)
    ob.location = loc
    ob.data.materials.append(m)
    if apply:   # object space in metres, for the patterns that use it
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return ob


def _front(a):
    return Vector((math.sin(a), -math.cos(a), 0))


def _dir(a):
    return Vector((math.cos(a), math.sin(a), 0))


def _width(fold):
    return 4 * PW * math.cos(fold) + 3 * T * math.sin(fold)


def _solve_fold():
    """The fold at which the hinged screen spans the stand-in's width."""
    lo, hi = math.radians(70), math.radians(85)
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if _width(mid) > STANDIN_WIDTH else (lo, mid)
    return (lo + hi) / 2


def layout():
    """Each panel's centre line: (start, direction, front normal, turn about z). Panels 1-2 and 3-4 fold
    together (a valley: the fronts close, so the hinge is on the front edges), 2-3 apart (a mountain: on
    the back edges)."""
    fold = _solve_fold()
    angles = [fold if i % 2 == 0 else -fold for i in range(4)]
    q = [Vector((0, 0, 0))]
    for i in range(3):
        s = 1 if i % 2 == 0 else -1
        hinge = q[i] + _dir(angles[i]) * PW + _front(angles[i]) * (s * T / 2)
        q.append(hinge - _front(angles[i + 1]) * (s * T / 2))
    end = q[3] + _dir(angles[3]) * PW
    shift = Vector((-(q[0].x + end.x) / 2, FRONT_Y - q[0].y, 0))
    return fold, [(q[i] + shift, _dir(a), _front(a), a) for i, a in enumerate(angles)]


def _panel(i, start, d, f, a, mats):
    lac, brc, face, back = mats
    c = start + d * (PW / 2); c.z = PH / 2
    # the frame: top and bottom rails the panel's width, the stiles between them; rounded all round
    for sz in (-1, 1):
        _box(f"screen frame {i + 1}", (PW, T, FR), c + Vector((0, 0, sz * (PH / 2 - FR / 2))), a, lac, 0.0075)
    for sx in (-1, 1):
        _box(f"screen frame {i + 1}", (FR, T, PH - 2 * FR + 0.002), c + d * (sx * (PW / 2 - FR / 2)), a, lac, 0.0075)
    # the core behind the paper, a little thinner than the frame on each face
    _box(f"screen core {i + 1}", (PW - 2 * FR + 0.004, T - 2 * REC, PH - 2 * FR + 0.004), c, a, lac)
    fy = T / 2 - REC
    # the painting, its UV over the whole screen: u across the four panels, v up the height
    w, h = PW - 2 * FR, PH - 2 * FR
    paint = _plane(f"screen painting {i + 1}", w, h, c + f * (fy + 0.0004), a, face)
    uvl = paint.data.uv_layers.active.data
    for loop in paint.data.loops:
        u, v = uvl[loop.index].uv
        uvl[loop.index].uv = ((i + (FR + u * w) / PW) / 4, (FR + v * h) / PH)
    # the brocade: along the top and the bottom, and down the screen's outer ends
    for sz in (-1, 1):
        _plane(f"screen brocade {i + 1}", w, BR, c + f * (fy + 0.0008) + Vector((0, 0, sz * (h / 2 - BR / 2))), a, brc,
               apply=True)
    for sx, outer in ((-1, i == 0), (1, i == 3)):
        if outer:
            _plane(f"screen brocade {i + 1}", BR, h - 2 * BR, c + f * (fy + 0.0008) + d * (sx * (w / 2 - BR / 2)), a, brc,
                   apply=True)
    _plane(f"screen back {i + 1}", w, h, c - f * (fy + 0.0004), a, back, back=True, apply=True)


def build():
    if not os.path.exists(os.path.join(TEX, "art.png")):
        raise FileNotFoundError(f"{TEX}: run tools/gold-screen/build.sh first (paint.py paints the panels)")
    mats = (_lacquer(), _brocade(), _painting(), _back())
    _, panels = layout()
    for i, (start, d, f, a) in enumerate(panels):
        _panel(i, start, d, f, a, mats)
