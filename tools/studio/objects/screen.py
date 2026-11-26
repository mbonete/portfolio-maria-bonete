# The folding screen of the old hero (tools/gold-screen/scene.py, painted by paint.py), as one object of
# the studio: four 1.0 x 1.6 m panels in black lacquer frames, each painting in an indigo brocade mounting
# edged with gold piping, brass corner fittings with domed nails, lacquer feet. The paintings are on washi
# (owner's call, 2026-11-26: on gold leaf, folded at 75 degrees, the leaf mirrored the studio's strip light
# as straight yellow bands); SCREEN_PAPER=0 brings back the burnished gold leaf. Each frame is four rails
# with rounded arrises, standing 6 mm proud of the recessed painting and its mounting.
# A murasaki stream runs from the top of panel 1 across the fold into panel 2; a sumi plum in bloom rises
# on panel 3 and reaches over panel 4. Same paintings (tools/gold-screen/p3), same shaders, same sizes.
#
# The pose is the stand-in's zigzag (standins.screen): panels 1 and 2 fold together, 2 and 3 apart, 3 and 4
# together, centred on x with the front folds at y = -0.25. Unlike the stand-in, whose 3.5 cm slabs pass
# through each other at the folds, every fold here turns on a hinge at the edge of the faces that close
# together (the fronts for a valley fold, the backs for a mountain fold), as a real screen's paper hinges
# do. Hinged, four panels at 74 degrees would stand 10 cm wider than the stand-in, so the fold is solved
# for the stand-in's width instead (75.5 degrees); the placement in common.py stays right.
#
# Her profile: a lamp in front of the screen throws the owner's silhouette (tools/gold-screen/figure2.png)
# onto the gold of panel 2, as in the hero. She stands 0.65 m in front of panel 2, her side to a spot on
# a stand 2.5 m up and 2.6 m beyond her; nothing of her is rendered but the shadow. The lamp is a
# projector of that geometry (a gobo): its beam is shuttered to panel 2's gold, as a framing spot is to a
# painting, and cut where her silhouette, placed in her standing plane at life size, crosses the ray, so
# her shadow and the lamp's glow stop at the gold's edge. A real blocker would also block the scene's key
# and fill and throw her onto the floor; the gobo blocks nothing else. Light linking keeps the lamp off
# everything but the screen (its receivers are the screen's collection). Gold is mostly mirror, so a
# shadow on it would barely darken the studio it reflects: as in the hero, the same matte, projected
# from the lamp, darkens panel 2's leaf where she stands.
import bpy, math, os
import numpy as np
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = os.path.normpath(os.path.join(HERE, "..", "..", "gold-screen"))
TEX = os.path.join(GOLD, "p3")              # paint.py's output (gold-screen/build.sh); gitignored there
FIGURE = os.path.join(GOLD, "figure2.png")  # the owner's silhouette (gold-screen/make-mask.sh); gitignored

# ---------- sizes (metres), as in the hero ----------
PW, PH, T, FR, LEG = 1.0, 1.6, 0.035, 0.04, 0.05   # panel, height, frame thickness and border, feet
BR = 0.032                                         # brocade mounting band around each painting
STANDIN_WIDTH = 4 * PW * math.cos(math.radians(74))   # the stand-in's outer ends, 1.103 m apart
FRONT_Y = -0.25                                    # the stand-in's front folds

# ---------- her shadow ----------
# Off in the studio (owner's call, 2026-11-25: no human silhouette on the screen). SCREEN_HER=1 brings it back.
HER_SHADOW = os.environ.get("SCREEN_HER", "0") == "1"
SHADOW_PANEL = 1          # panel 2, as in the hero (0-based)
# The camera sees every panel about 74 degrees off square. Lit from straight in front, as in the hero, her
# profile would reach the camera squeezed to 30% of its width; lit from near the camera, it would spread
# wider than the gold. Between the two, from 68 degrees, it reads at 75% and her head still fits.
LAMP_TURN = 68            # degrees from the panel's normal, toward the camera side
MAG = 1.25                # her shadow over her size, at the head: she stands a fifth of the way from the panel to the lamp
LAMP_TO_PANEL = 3.2       # horizontal distance from the lamp to her shadow on the gold
HER_CROWN = 1.66          # the top of her head above the floor (a 1.68 m woman)
CROWN_ON_GOLD = 1.45      # where the shadow of her crown falls; sets the lamp's height (2.5 m, on a stand)
NOSE_CLEAR = 0.06         # her raised chin, the front of her profile, clears the gold's left edge by this much
LIFE_PX = 2070            # figure2.png pixels per metre at life size (crown to chin 455 px, about 22 cm)
LAMP_RADIUS = 0.012       # the bulb, for the penumbra
LAMP_W = 9000             # watts at real size (a driver keeps the light on the gold the same at the scene's 1.32x)
LAMP_RGB = (1.0, 0.86, 0.70)   # warm white: the hero's orange lamp (1.0, 0.70, 0.30) turns the leaf copper here
SPOT_DEG, SPOT_BLEND = 40, 0.9  # a soft pool centred on her head, the glow the hero has around it
SHK = 0.95                # how much of the leaf's mirror the matte darkens (hero: 0.95)

# ---------- the leaf, as the hero's open still (render-fold.sh) unless noted ----------
GESSO = 0.14              # the gesso showing through the leaf
# In the hero the open screen showed each leaf once. Folded to 75 degrees, the camera sees most of the leaf
# in the facing panel's mirror, gold in gold two or three times over, which compounds into copper. The
# leaf seen in a reflection is taken this far toward grey, so the folds keep the hero's burnished gold.
GOLD_IN_GOLD = 0.5
STREAM_COAT = 0.25        # the murasaki's coat (hero 0.6, seen square on; at 74 degrees it would wash to lavender)
PAPER = os.environ.get("SCREEN_PAPER", "1") == "1"
KINDEI_METAL = 0.35       # the mist bands in gold paint on the paper: this much of it shines as metal, the rest
                          # is the matte glue it is ground in (the hero's paper test had 0.7)
REC = 0.006               # how far the painting sits back from the frame's face
# The painting's straight-edged mist bands are left off the paper, relief and all (owner's call,
# 2026-11-26); SCREEN_MIST=1 paints them back in gold (kindei)
MIST = os.environ.get("SCREEN_MIST", "0") == "1"


# =============================================================================================
# materials: ported from tools/gold-screen/scene.py
# =============================================================================================
def _mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]


def _lacquer():
    m, n, l, p = _mat("screen lacquer")
    p.inputs["Base Color"].default_value = (0.010, 0.006, 0.006, 1)
    p.inputs["Roughness"].default_value = 0.3
    p.inputs["Coat Weight"].default_value = 1.0
    p.inputs["Coat Roughness"].default_value = 0.05
    # urushi carries its pigment in the lacquer itself: one glossy surface, the coat; no second reflection
    # from a layer beneath (which would turn the frame grey in a bright studio)
    p.inputs["Specular IOR Level"].default_value = 0.0
    return m


def _brass():
    m, n, l, p = _mat("screen brass")
    p.inputs["Base Color"].default_value = (0.80, 0.62, 0.34, 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.3
    # nanako: the punched ring ground of Japanese metalwork, as a fine dimpled bump (object space, so it
    # keeps its size when the scene enlarges the screen)
    tc = n.new("ShaderNodeTexCoord")
    vor = n.new("ShaderNodeTexVoronoi"); vor.feature = "F1"; vor.inputs["Scale"].default_value = 900
    l.new(tc.outputs["Object"], vor.inputs["Vector"])
    vb = n.new("ShaderNodeBump"); vb.inputs["Strength"].default_value = 0.35; vb.inputs["Distance"].default_value = 0.0003
    l.new(vor.outputs["Distance"], vb.inputs["Height"]); l.new(vb.outputs["Normal"], p.inputs["Normal"])
    return m


def _brocade():
    # mounting band: deep indigo silk with a faint woven sheen
    m, n, l, p = _mat("screen brocade")
    p.inputs["Base Color"].default_value = (0.014, 0.017, 0.045, 1)
    p.inputs["Roughness"].default_value = 0.62
    # the hero saw it square on; the studio sees it at 74 degrees, where a strong sheen turns it pale grey
    p.inputs["Sheen Weight"].default_value = 0.06
    p.inputs["Sheen Tint"].default_value = (0.40, 0.45, 1.0, 1)
    p.inputs["Specular IOR Level"].default_value = 0.2
    weave = n.new("ShaderNodeTexWave"); weave.wave_type = "BANDS"; weave.inputs["Scale"].default_value = 420
    weave.inputs["Distortion"].default_value = 1.5
    wb = n.new("ShaderNodeBump"); wb.inputs["Strength"].default_value = 0.08
    l.new(weave.outputs["Fac"], wb.inputs["Height"]); l.new(wb.outputs["Normal"], p.inputs["Normal"])
    return m


def _piping():
    m, n, l, p = _mat("screen piping")
    p.inputs["Base Color"].default_value = (0.90, 0.70, 0.36, 1)
    p.inputs["Metallic"].default_value = 1.0
    p.inputs["Roughness"].default_value = 0.3
    return m


def _washi():
    """The backs, which the hero never showed: a warm unbleached kozo paper, its cloudy formation and a
    net of fibres (the hero's PAPER=1 ground, in object space)."""
    m, n, l, p = _mat("screen washi")
    tc = n.new("ShaderNodeTexCoord")
    form = n.new("ShaderNodeTexNoise"); form.inputs["Scale"].default_value = 44; form.inputs["Detail"].default_value = 8
    form.inputs["Roughness"].default_value = 0.62; l.new(tc.outputs["Object"], form.inputs["Vector"])
    warp = n.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 25; l.new(tc.outputs["Object"], warp.inputs["Vector"])
    wadd = n.new("ShaderNodeVectorMath"); wadd.operation = "MULTIPLY_ADD"; wadd.inputs[1].default_value = (0.019, 0.019, 0.019)
    l.new(warp.outputs["Color"], wadd.inputs[0]); l.new(tc.outputs["Object"], wadd.inputs[2])
    fib = n.new("ShaderNodeTexVoronoi"); fib.feature = "DISTANCE_TO_EDGE"; fib.inputs["Scale"].default_value = 34
    l.new(wadd.outputs["Vector"], fib.inputs["Vector"])
    fline = n.new("ShaderNodeMapRange"); fline.inputs["From Min"].default_value = 0.0; fline.inputs["From Max"].default_value = 0.035
    fline.inputs["To Min"].default_value = 1.0; fline.inputs["To Max"].default_value = 0.0; fline.interpolation_type = "SMOOTHSTEP"
    l.new(fib.outputs["Distance"], fline.inputs["Value"])
    c1 = n.new("ShaderNodeMix"); c1.data_type = "RGBA"
    l.new(form.outputs["Fac"], c1.inputs[0]); c1.inputs[6].default_value = (0.60, 0.52, 0.38, 1); c1.inputs[7].default_value = (0.52, 0.44, 0.31, 1)
    fk = n.new("ShaderNodeMath"); fk.operation = "MULTIPLY"; fk.inputs[1].default_value = 0.5
    l.new(fline.outputs["Result"], fk.inputs[0])
    c2 = n.new("ShaderNodeMix"); c2.data_type = "RGBA"
    l.new(fk.outputs["Value"], c2.inputs[0]); l.new(c1.outputs[2], c2.inputs[6]); c2.inputs[7].default_value = (0.70, 0.63, 0.50, 1)
    l.new(c2.outputs[2], p.inputs["Base Color"])
    ph = n.new("ShaderNodeMath"); ph.operation = "MULTIPLY_ADD"; ph.inputs[1].default_value = 0.6
    l.new(fline.outputs["Result"], ph.inputs[0]); l.new(form.outputs["Fac"], ph.inputs[2])
    pb = n.new("ShaderNodeBump"); pb.inputs["Strength"].default_value = 0.12; pb.inputs["Distance"].default_value = 0.0004
    l.new(ph.outputs["Value"], pb.inputs["Height"]); l.new(pb.outputs["Normal"], p.inputs["Normal"])
    p.inputs["Roughness"].default_value = 0.88
    p.inputs["Specular IOR Level"].default_value = 0.3
    p.inputs["Sheen Weight"].default_value = 0.25
    return m


def _face():
    """The painted gold: per-leaf tone, overlaps, patina and burnish; raised gesso mist bands, gold dust
    and cut leaf; the murasaki stream under a light coat with its gold current lines; the matte paint of
    the plum. Node for node the hero's face material (scene.py, PAPER off)."""
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
    l.new(det.outputs["Green"], b2.inputs["Height"]); l.new(b1.outputs["Normal"], b2.inputs["Normal"])
    NRM = b2.outputs["Normal"]
    if PAPER:
        # The same painting on washi (the hero's PAPER=1): unbleached kozo with its cloudy formation and a
        # net of fibres, stained a little where the leaf had its patina; dust and cut leaf still metal, as
        # gold flakes scattered on paper are; the stream without its coat.
        iso = n.new("ShaderNodeMapping"); iso.inputs["Scale"].default_value = (2.5, 1.0, 1.0)   # UV: 4 panels wide, 1 tall
        l.new(uv.outputs["UV"], iso.inputs["Vector"])
        form = n.new("ShaderNodeTexNoise"); form.inputs["Scale"].default_value = 70; form.inputs["Detail"].default_value = 8
        form.inputs["Roughness"].default_value = 0.62; l.new(iso.outputs["Vector"], form.inputs["Vector"])
        warp = n.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 40; l.new(iso.outputs["Vector"], warp.inputs["Vector"])
        wadd = n.new("ShaderNodeVectorMath"); wadd.operation = "MULTIPLY_ADD"; wadd.inputs[1].default_value = (0.012, 0.012, 0.012)
        l.new(warp.outputs["Color"], wadd.inputs[0]); l.new(iso.outputs["Vector"], wadd.inputs[2])
        fib = n.new("ShaderNodeTexVoronoi"); fib.feature = "DISTANCE_TO_EDGE"; fib.inputs["Scale"].default_value = 55
        l.new(wadd.outputs["Vector"], fib.inputs["Vector"])
        fline = n.new("ShaderNodeMapRange"); fline.inputs["From Min"].default_value = 0.0; fline.inputs["From Max"].default_value = 0.035
        fline.inputs["To Min"].default_value = 1.0; fline.inputs["To Max"].default_value = 0.0; fline.interpolation_type = "SMOOTHSTEP"
        l.new(fib.outputs["Distance"], fline.inputs["Value"])
        pc = mixc(form.outputs["Fac"], (0.88, 0.82, 0.68, 1), (0.80, 0.73, 0.58, 1))
        pc = mixc(pat.outputs["Result"], pc, (0.76, 0.67, 0.50, 1))
        fk = n.new("ShaderNodeMath"); fk.operation = "MULTIPLY"; fk.inputs[1].default_value = 0.5
        l.new(fline.outputs["Result"], fk.inputs[0])
        pc = mixc(fk.outputs["Value"], pc, (0.93, 0.89, 0.79, 1))
        ph = n.new("ShaderNodeMath"); ph.operation = "MULTIPLY_ADD"; ph.inputs[1].default_value = 0.6
        l.new(fline.outputs["Result"], ph.inputs[0]); l.new(form.outputs["Fac"], ph.inputs[2])
        pb = n.new("ShaderNodeBump"); pb.inputs["Strength"].default_value = 0.12; pb.inputs["Distance"].default_value = 0.0004
        l.new(ph.outputs["Value"], pb.inputs["Height"])
        pr = n.new("ShaderNodeBump"); pr.inputs["Strength"].default_value = 0.6; pr.inputs["Distance"].default_value = 0.0012
        relief = det.outputs["Green"]
        if not MIST:     # the bands' raised gesso goes with them; the blossoms and gold lines keep theirs
            keep = n.new("ShaderNodeMath"); keep.operation = "SUBTRACT"; keep.inputs[0].default_value = 1.0
            l.new(sep.outputs["Blue"], keep.inputs[1])
            rl = n.new("ShaderNodeMath"); rl.operation = "MULTIPLY"
            l.new(det.outputs["Green"], rl.inputs[0]); l.new(keep.outputs[0], rl.inputs[1])
            relief = rl.outputs[0]
        l.new(relief, pr.inputs["Height"]); l.new(pb.outputs["Normal"], pr.inputs["Normal"])
        PN = pr.outputs["Normal"]
        sh = bsdf(pc, 0.0, 0.88, PN, **{"Specular IOR Level": 0.3, "Sheen Weight": 0.25})
        if MIST:
            sh = mixs(sep.outputs["Blue"], sh, mixs(KINDEI_METAL, metal((0.96, 0.76, 0.42, 1), 0.55, PN),
                                                     diffuse((0.86, 0.68, 0.38, 1), PN)))
        sh = mixs(det.outputs["Blue"], sh, mixs(0.3, metal((1.0, 0.82, 0.48, 1), 0.25, PN), diffuse((0.98, 0.82, 0.5, 1), PN)))
        vcol = mixc(det.outputs["Red"], (0.062, 0.024, 0.19, 1), (0.105, 0.048, 0.28, 1))
        sh = mixs(sep.outputs["Red"], sh, bsdf(vcol, 0.0, 0.7, PN))
        sh = mixs(sep.outputs["Green"], sh, mixs(0.5, metal((0.98, 0.84, 0.52, 1), 0.4, PN), diffuse((0.95, 0.80, 0.50, 1), PN)))
        sh = mixs(artT.outputs["Alpha"], sh, bsdf(artT.outputs["Color"], 0.0, 0.85, PN, **{"Specular IOR Level": 0.12}))
        l.new(sh, n["Material Output"].inputs["Surface"])
        return face
    ground = mixs(GESSO, metal(goldc, burn.outputs["Value"], NRM), diffuse(goldc, NRM))
    # mist bands: a paler, finer gold, part dust and so part matte
    cloud = mixs(0.42, metal((0.98, 0.80, 0.46, 1), 0.32, NRM), diffuse((0.93, 0.77, 0.47, 1), NRM))
    sh = mixs(sep.outputs["Blue"], ground, cloud)
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
def _box(name, size, loc, rz, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rz))
    ob = bpy.context.active_object; ob.name = name; ob.scale = size; ob.data.materials.append(m)
    if bevel:
        # rounded arrises: the lacquer and brass catch a thin line of light along every edge
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 3; bv.harden_normals = True
        bpy.ops.object.shade_smooth()
    return ob


def _plane(name, w, h, loc, a, m, back=False):
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.name = name; ob.scale = (w, h, 1)
    ob.rotation_euler = (math.radians(-90 if back else 90), 0, a)
    ob.location = loc
    ob.data.materials.append(m)
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


def _panel(i, start, d, f, a, mats, hinge_left, hinge_right):
    lac, brs, brc, pip, face, washi = mats
    c = start + d * (PW / 2); c.z = LEG + PH / 2
    # the frame: top and bottom rails the panel's width, the stiles between them, all with rounded arrises
    # (a fine seam where they butt); behind the painting, a core REC thinner on each face
    obs = []
    for sz in (-1, 1):
        obs.append(_box(f"screen frame {i + 1}", (PW, T, FR), c + Vector((0, 0, sz * (PH / 2 - FR / 2))), a, lac, 0.004))
    for sx in (-1, 1):
        obs.append(_box(f"screen frame {i + 1}", (FR, T, PH - 2 * FR + 0.001), c + d * (sx * (PW / 2 - FR / 2)), a, lac, 0.004))
    obs.append(_box(f"screen core {i + 1}", (PW - 2 * FR + 0.004, T - 2 * REC, PH - 2 * FR + 0.004), c, a, lac))
    face_y = T / 2 - REC
    obs.append(_plane(f"screen brocade {i + 1}", PW - 2 * FR, PH - 2 * FR, c + f * (face_y + 0.001), a, brc))
    obs.append(_plane(f"screen piping {i + 1}", PW - 2 * FR - 2 * BR + 0.009, PH - 2 * FR - 2 * BR + 0.009,
                      c + f * (face_y + 0.0013), a, pip))
    w, h = PW - 2 * FR - 2 * BR, PH - 2 * FR - 2 * BR
    gold = _plane(f"screen gold {i + 1}", w, h, c + f * (face_y + 0.0016), a, face)
    uvl = gold.data.uv_layers.active.data
    for loop in gold.data.loops:
        u, v = uvl[loop.index].uv
        uvl[loop.index].uv = ((i + (FR + BR) / PW + u * (w / PW)) / 4, (FR + BR) / PH + v * (h / PH))
    obs.append(gold)
    back = _plane(f"screen back {i + 1}", PW - 2 * FR, PH - 2 * FR, c - f * (face_y + 0.001), a, washi, back=True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # object space in metres, for the paper
    obs.append(back)
    # corner fittings (kanagu): an L of brass on each corner of the frame, three domed nails. On the outer
    # edges of the screen they wrap 2 mm past the frame, as in the hero; on a hinged edge they stop at it.
    FL, FW, FT = 0.088, 0.027, 0.004
    for sx in (-1, 1):
        wrap = 0.0 if (hinge_left if sx < 0 else hinge_right) else 0.002
        for sz in (-1, 1):
            def at(u, v, out):
                return c + d * (sx * u) + Vector((0, 0, sz * v)) + f * (T / 2 + out)
            obs.append(_box(f"screen fitting {i + 1}", (FL, FT, FW), at(PW / 2 - FL / 2 + wrap, PH / 2 - FW / 2 + 0.002, FT / 2), a, brs, 0.0014))
            obs.append(_box(f"screen fitting {i + 1}", (FW, FT, FL), at(PW / 2 - FW / 2 + wrap, PH / 2 - FL / 2 + 0.002, FT / 2), a, brs, 0.0014))
            for (u, v) in ((PW / 2 - 0.012 - 0.002 + wrap, PH / 2 - 0.012), (PW / 2 - FL + 0.014, PH / 2 - FW / 2 + 0.002),
                           (PW / 2 - FW / 2 + wrap, PH / 2 - FL + 0.014)):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0036, segments=16, ring_count=8, location=at(u, v, FT))
                nail = bpy.context.active_object; nail.name = f"screen nail {i + 1}"
                nail.data.materials.append(brs); bpy.ops.object.shade_smooth()
                obs.append(nail)
        # feet: 9 cm in from the ends (the hero's 7 cm would make neighbours' feet touch at these folds)
        ft = c + d * (sx * (PW / 2 - 0.09)); ft.z = LEG / 2
        obs.append(_box(f"screen foot {i + 1}", (0.07, T + 0.02, LEG), ft, a, lac, 0.004))
    for ob in obs:
        ob["panel"] = i
    return obs, gold


# =============================================================================================
# her shadow
# =============================================================================================
def _matte_image(px_per_m, crown_on_gold, gold_bottom, mag, blur_px):
    """figure2.png's alpha, its faded lower edge replaced by the body carried straight down (she is
    standing; the photo stops at her chest) until its shadow passes the gold's lower edge, softened by
    the lamp's penumbra. Returns the image and landmarks in its pixels (top-down rows)."""
    src = bpy.data.images.load(FIGURE, check_existing=True)
    W, H = src.size
    a = np.empty(W * H * 4, np.float32); src.pixels.foreach_get(a)
    a = a.reshape(H, W, 4)[::-1, :, 3].copy()                    # top-down rows
    rows = np.nonzero(a.max(1) > 0.5)[0]
    crown = int(rows.min())
    crown_u = float(np.nonzero(a[crown + 8] > 0.5)[0].mean())
    face = a[crown + 150:crown + 480] > 0.5                       # nose, lips and the raised chin
    chin_u = int(np.nonzero(face.any(0))[0].min())
    chin_v = crown + 150 + int(np.nonzero(face[:, chin_u])[0].mean())
    cut = int(np.nonzero(a.max(1) > 0.97)[0].max()) - 4          # the last solid row, above the photo's fade
    need = (crown_on_gold - gold_bottom + 0.08) / mag * px_per_m   # rows below the crown to clear the gold
    ext = max(40, int(need - (cut - crown)))
    body = np.repeat(a[cut:cut + 1], ext, 0)
    # the hair thins out toward its ends: pull the back (right) edge in a little as the body goes down
    xs = np.nonzero(a[cut] > 0.5)[0]; x0, x1 = xs.min(), xs.max()
    k = np.linspace(0, 1, ext)[:, None]
    right = x1 - (x1 - x0) * 0.18 * k
    body = body * np.clip(right - np.arange(W)[None, :] + 0.5, 0, 1)
    a = np.vstack([a[:cut], body])
    r = int(round(blur_px))
    if r >= 1:
        for axis in (0, 1):
            for _ in range(3):
                pad = [(r + 1, r) if ax == axis else (0, 0) for ax in (0, 1)]
                c = np.cumsum(np.pad(a, pad, mode="edge"), axis)
                a = (c[2 * r + 1:] - c[:-2 * r - 1]) if axis == 0 else (c[:, 2 * r + 1:] - c[:, :-2 * r - 1])
                a = a / (2 * r + 1)
    H2 = a.shape[0]
    img = bpy.data.images.new("screen her matte", W, H2, alpha=False)
    img.colorspace_settings.name = "Non-Color"
    rgba = np.repeat(a[::-1, :, None], 4, 2); rgba[..., 3] = 1
    img.pixels.foreach_set(rgba.astype(np.float32).ravel())
    img.pack()
    return img, (W, H2), dict(crown=(crown_u, crown), chin=(chin_u, chin_v))


def _matte_group(img, size, lamp_inv, caster, goldrect):
    """A shader node group: given a ray from the lamp (a direction, or a point, in the lamp's own space),
    Gold is 1 where the ray lands on panel 2's gold, Shadow 1 where it crosses her silhouette on the way."""
    (cw, ch), (c0, ex, ey, cn) = size, caster
    g0, gx, gz, gn, gw, gh = goldrect
    # everything in the lamp's frame
    R = lamp_inv.to_3x3()
    c0, g0 = lamp_inv @ c0, lamp_inv @ g0
    ex, ey, cn, gx, gz, gn = (R @ v for v in (ex, ey, cn, gx, gz, gn))
    grp = bpy.data.node_groups.new("screen her matte", "ShaderNodeTree")
    grp.interface.new_socket("Ray", in_out="INPUT", socket_type="NodeSocketVector")
    grp.interface.new_socket("Shadow", in_out="OUTPUT", socket_type="NodeSocketFloat")
    grp.interface.new_socket("Gold", in_out="OUTPUT", socket_type="NodeSocketFloat")
    n, l = grp.nodes, grp.links
    gi = n.new("NodeGroupInput"); go = n.new("NodeGroupOutput")
    ray = gi.outputs[0]

    def dot(vec):
        d = n.new("ShaderNodeVectorMath"); d.operation = "DOT_PRODUCT"; d.inputs[1].default_value = tuple(vec)
        l.new(ray, d.inputs[0]); return d.outputs["Value"]

    def math_(op, a, b=None, c=None):
        m = n.new("ShaderNodeMath"); m.operation = op
        for k, v in enumerate((a, b, c)):
            if v is None: continue
            if isinstance(v, (int, float)): m.inputs[k].default_value = v
            else: l.new(v, m.inputs[k])
        return m.outputs[0]

    # the ray reaches her plane at t (in units of the ray), the gold's plane at tg
    t = math_("DIVIDE", c0.dot(cn), dot(cn))
    tg = math_("DIVIDE", g0.dot(gn), dot(gn))
    u = math_("MULTIPLY_ADD", math_("SUBTRACT", math_("MULTIPLY", t, dot(ex)), c0.dot(ex)), 1 / cw, 0.5)
    v = math_("MULTIPLY_ADD", math_("SUBTRACT", math_("MULTIPLY", t, dot(ey)), c0.dot(ey)), 1 / ch, 0.5)
    uvw = n.new("ShaderNodeCombineXYZ"); l.new(u, uvw.inputs[0]); l.new(v, uvw.inputs[1])
    tex = n.new("ShaderNodeTexImage"); tex.image = img; tex.extension = "CLIP"; tex.interpolation = "Cubic"
    l.new(uvw.outputs[0], tex.inputs["Vector"])
    gu = math_("ABSOLUTE", math_("SUBTRACT", math_("MULTIPLY", tg, dot(gx)), g0.dot(gx)))
    gv = math_("ABSOLUTE", math_("SUBTRACT", math_("MULTIPLY", tg, dot(gz)), g0.dot(gz)))
    inside = math_("MULTIPLY", math_("LESS_THAN", gu, gw / 2), math_("LESS_THAN", gv, gh / 2))
    gold = math_("MULTIPLY", inside, math_("GREATER_THAN", tg, 0.0))
    ahead = math_("MULTIPLY", math_("GREATER_THAN", t, 0.0), math_("LESS_THAN", t, tg))
    out = math_("MULTIPLY", math_("MULTIPLY", tex.outputs["Color"], gold), ahead)
    l.new(out, go.inputs[0]); l.new(gold, go.inputs[1])
    return grp


def _her(panel, gold_ob, face):
    """The lamp, the matte and the darkening of panel 2's leaf. panel = (start, d, f, a) of that panel."""
    start, d, f, a = panel
    c = start + d * (PW / 2)
    w, h = PW - 2 * FR - 2 * BR, PH - 2 * FR - 2 * BR
    g0 = Vector((c.x, c.y, LEG + PH / 2)) + f * (T / 2 + 0.0016)
    goldrect = (g0, d.copy(), Vector((0, 0, 1)), f.copy(), w, h)
    # the lamp's horizontal direction from the panel: its normal turned toward the camera (which looks
    # along +y from -y)
    turn = math.radians(LAMP_TURN)
    ul = min((Matrix.Rotation(s_ * turn, 3, "Z") @ f for s_ in (1, -1)), key=lambda v: v.y)
    px = LIFE_PX
    lamp_h = (MAG * HER_CROWN - CROWN_ON_GOLD) / (MAG - 1)      # the shadow of her crown lands at CROWN_ON_GOLD
    dist_her = LAMP_TO_PANEL / MAG                               # lamp to her plane, horizontally
    blur = LAMP_RADIUS * (MAG - 1) / MAG * px                    # half the penumbra, in silhouette pixels
    img, (W, H2), mark_px = _matte_image(px, CROWN_ON_GOLD, LEG + FR + BR, MAG, blur)
    cw, ch = W / px, H2 / px
    ex = Vector((-ul.y, ul.x, 0))
    if ex.dot(d) < 0:
        ex = -ex                                        # the photo's right runs along the panel, away from the fold
    ey = Vector((0, 0, 1))

    def on_plane(c0, u_px, v_px):
        return c0 + ex * ((u_px - W / 2) / px) + ey * ((H2 / 2 - v_px) / px)

    def shadow_of(pt, lamp):
        """Where the ray from the lamp through pt meets the gold's plane, along the panel from the gold's
        left edge."""
        r = pt - lamp
        q = lamp + r * ((g0 - lamp).dot(f) / r.dot(f)) - g0
        return q.dot(d) + w / 2

    # place her: the shadow of her crown at CROWN_ON_GOLD, the shadow of her raised chin (the front of her
    # profile) NOSE_CLEAR in from the gold's left edge
    anchor_s = w * 0.45
    for _ in range(12):
        A = g0 + d * (anchor_s - w / 2); A.z = CROWN_ON_GOLD
        lamp = A + ul * LAMP_TO_PANEL; lamp.z = lamp_h
        crown = lamp + (A - lamp) * (dist_her / LAMP_TO_PANEL)    # her crown, on the ray to its shadow
        c0 = crown - (on_plane(Vector(), *mark_px["crown"]))      # her plane, square to the lamp's direction
        anchor_s += NOSE_CLEAR - shadow_of(on_plane(c0, *mark_px["chin"]), lamp)
    if os.environ.get("SCREEN_DEBUG"):
        print(f"screen: she stands at ({crown.x:.2f}, {crown.y:.2f}), crown {crown.z:.2f} m, {LAMP_TO_PANEL - dist_her:.2f} m "
              f"from the panel; the lamp at ({lamp.x:.2f}, {lamp.y:.2f}, {lamp.z:.2f}), {dist_her:.2f} m in front of her")
    cn = ul.copy()
    # the lamp: a small spot on a stand, aimed at her head
    ld = bpy.data.lights.new("screen her lamp", "SPOT")
    ld.color = LAMP_RGB
    ld.spot_size = math.radians(SPOT_DEG); ld.spot_blend = SPOT_BLEND
    ld.shadow_soft_size = 0.0
    lob = bpy.data.objects.new("screen her lamp", ld)
    bpy.context.scene.collection.objects.link(lob)
    lob.location = lamp
    aim_at = g0 + d * (anchor_s - w / 2 + 0.05); aim_at.z = CROWN_ON_GOLD - 0.15
    lob.rotation_euler = (aim_at - lamp).to_track_quat("-Z", "Y").to_euler()
    lob.visible_camera = False
    # light power falls with the square of the distance, and the scene shows the screen 1.32x: keep the
    # light on the gold the same at any scale
    fc = ld.driver_add("energy"); drv = fc.driver; drv.type = "SCRIPTED"
    var = drv.variables.new(); var.name = "s"; var.type = "TRANSFORMS"
    var.targets[0].id = lob; var.targets[0].transform_type = "SCALE_X"; var.targets[0].transform_space = "WORLD_SPACE"
    drv.expression = f"{LAMP_W} * s * s"
    bpy.context.view_layer.update()
    grp = _matte_group(img, (cw, ch), lob.matrix_world.inverted(), (c0, ex, ey, cn), goldrect)
    # the lamp is shuttered to panel 2's painting, as a framing spot is to a picture (the frame and the
    # brocade keep the studio's light), and its light is cut where she stands
    ld.use_nodes = True
    nt = ld.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    gn = nt.nodes.new("ShaderNodeGroup"); gn.node_tree = grp
    nt.links.new(tc.outputs["Normal"], gn.inputs[0])
    lit = nt.nodes.new("ShaderNodeMath"); lit.operation = "SUBTRACT"
    nt.links.new(gn.outputs["Gold"], lit.inputs[0]); nt.links.new(gn.outputs["Shadow"], lit.inputs[1])
    nt.links.new(lit.outputs[0], nt.nodes["Emission"].inputs["Strength"])
    # and on panel 2's leaf, the same matte darkens the mirror (hero: SHK)
    m2 = face.copy(); m2.name = "screen gold leaf, her shadow"
    gold_ob.data.materials[0] = m2
    n, l = m2.node_tree.nodes, m2.node_tree.links
    out = n["Material Output"]
    last = out.inputs["Surface"].links[0].from_socket
    tc2 = n.new("ShaderNodeTexCoord"); tc2.object = lob
    g2 = n.new("ShaderNodeGroup"); g2.node_tree = grp
    l.new(tc2.outputs["Object"], g2.inputs[0])
    k = n.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = SHK
    l.new(g2.outputs["Shadow"], k.inputs[0])
    shade = n.new("ShaderNodeBsdfPrincipled")
    shade.inputs["Base Color"].default_value = (0.03, 0.018, 0.008, 1)
    # the hero's shade was 0.6 metallic: seen square on, dark; at 74 degrees a metal's Fresnel turns white
    # and the shadow would mirror the facing gold. A dull dark ground instead, as the hero shows it.
    shade.inputs["Metallic"].default_value = 0.0
    shade.inputs["Roughness"].default_value = 0.5
    shade.inputs["Specular IOR Level"].default_value = 0.3
    sm = n.new("ShaderNodeMixShader")
    l.new(k.outputs["Value"], sm.inputs["Fac"]); l.new(last, sm.inputs[1]); l.new(shade.outputs["BSDF"], sm.inputs[2])
    l.new(sm.outputs["Shader"], out.inputs["Surface"])
    # where she stands, for anyone opening the file: her silhouette as an image empty (never rendered)
    mark = bpy.data.objects.new("screen her (not rendered)", None)
    bpy.context.scene.collection.objects.link(mark)
    mark.empty_display_type = "IMAGE"; mark.data = img
    mark.empty_display_size = ch
    mark.matrix_world = Matrix.Translation(c0) @ Matrix((ex, ey, cn)).transposed().to_4x4()
    return lob, mark


def build():
    if not os.path.exists(os.path.join(TEX, "leaf.png")):
        raise FileNotFoundError(f"{TEX}: run tools/gold-screen/build.sh first (paint.py paints the panels)")
    mats = (_lacquer(), _brass(), _brocade(), _piping(), _face(), _washi())
    _, panels = layout()
    obs, golds = [], []
    for i, (start, d, f, a) in enumerate(panels):
        o, g = _panel(i, start, d, f, a, mats, hinge_left=i > 0, hinge_right=i < 3)
        obs += o; golds.append(g)
    if not HER_SHADOW:
        return
    lamp, mark = _her(panels[SHADOW_PANEL], golds[SHADOW_PANEL], mats[4])
    # Light linking: her lamp lights the screen only. scene.py moves every object it builds into the
    # screen's own collection (common.adopt), which empties any other collection they were in; so the
    # receivers are that collection when it exists (scene.py), and the objects themselves otherwise
    # (turntable.py).
    rec = bpy.data.collections.new("screen her lamp receivers")
    for ob in obs:
        rec.objects.link(ob)
    host = bpy.data.collections.get("screen")
    if host is not None:
        rec.children.link(host)
    lamp.light_linking.receiver_collection = rec
