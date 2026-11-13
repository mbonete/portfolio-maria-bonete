# The Gold Screen, pass 2: a four-panel byobu in a dark lacquer room. A lamp from the front-left
# throws her real profile silhouette (from a photo) across panels 1-2; she reaches toward a murasaki
# stream on panel 1, a sumi plum branch hangs on panel 4.
# Usage: blender -b --factory-startup -P screen2.py -- out.png W H view samples [fold_deg]
import bpy, math, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, RW, RH, VIEW, SAMPLES = argv[0], int(argv[1]), int(argv[2]), argv[3], int(argv[4])
FOLD = math.radians(float(argv[5]) if len(argv) > 5 else 26)
HERE = os.path.dirname(os.path.abspath(__file__))

scn = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.preferences.addon_enable(module="cycles")
scn.render.engine = "CYCLES"
prefs = bpy.context.preferences.addons["cycles"].preferences
try:
    prefs.compute_device_type = "METAL"; prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    scn.cycles.device = "GPU"
except Exception:
    scn.cycles.device = "CPU"
scn.cycles.samples = SAMPLES
scn.cycles.use_denoising = os.environ.get("DENOISE", "1") == "1"
# Pixel filter: Cycles defaults to a 1.5 px Blackman-Harris, which softens fine line work.
scn.cycles.filter_width = float(os.environ.get("FILTER", "1.5"))
if os.environ.get("BORDER"):   # x0,x1,y0,y1 as fractions, y from the bottom: render one region only
    x0, x1, y0, y1 = (float(v) for v in os.environ["BORDER"].split(","))
    scn.render.use_border = True; scn.render.use_crop_to_border = True
    scn.render.border_min_x, scn.render.border_max_x, scn.render.border_min_y, scn.render.border_max_y = x0, x1, y0, y1
scn.cycles.max_bounces = 6
scn.render.resolution_x, scn.render.resolution_y = RW, RH
scn.view_settings.view_transform = os.environ.get("VT", "Khronos PBR Neutral")
scn.view_settings.look = os.environ.get("LOOK", "None")
scn.view_settings.exposure = float(os.environ.get("EXPO", "0"))
scn.render.filepath = OUT

# ---------- world: near-black room ----------
world = bpy.data.worlds.new("room"); scn.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.0025, 0.002, 0.0022, 1)

def mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]

lac, n, l, p = mat("lacquer")
p.inputs["Base Color"].default_value = (0.010, 0.006, 0.006, 1)
p.inputs["Roughness"].default_value = 0.3
p.inputs["Coat Weight"].default_value = 1.0
p.inputs["Coat Roughness"].default_value = 0.05

flo, n, l, p = mat("floor")
p.inputs["Base Color"].default_value = (0.006, 0.004, 0.004, 1)
p.inputs["Roughness"].default_value = 0.18
p.inputs["Coat Weight"].default_value = 0.7
p.inputs["Coat Roughness"].default_value = 0.1
# faint large-scale unevenness so the reflection is not a mirror
fn = n.new("ShaderNodeTexNoise"); fn.inputs["Scale"].default_value = 3.0
fr = n.new("ShaderNodeMapRange"); fr.inputs["To Min"].default_value = float(os.environ.get("FRMIN", "0.05")); fr.inputs["To Max"].default_value = float(os.environ.get("FRMAX", "0.13"))
l.new(fn.outputs["Fac"], fr.inputs["Value"])
# the polish fades with distance from the screen: the reflection dissolves into the dark floor
geo = n.new("ShaderNodeNewGeometry"); sxyz = n.new("ShaderNodeSeparateXYZ"); l.new(geo.outputs["Position"], sxyz.inputs["Vector"])
fade = n.new("ShaderNodeMapRange"); fade.inputs["From Min"].default_value = -0.3; fade.inputs["From Max"].default_value = float(os.environ.get("FADEY", "-5.0"))
fade.interpolation_type = "SMOOTHSTEP"
l.new(sxyz.outputs["Y"], fade.inputs["Value"])
rmix = n.new("ShaderNodeMix"); rmix.data_type = "FLOAT"; rmix.inputs["B"].default_value = float(os.environ.get("FARR", "0.42"))
l.new(fade.outputs["Result"], rmix.inputs["Factor"]); l.new(fr.outputs["Result"], rmix.inputs["A"])
l.new(rmix.outputs["Result"], p.inputs["Roughness"])
cmix = n.new("ShaderNodeMath"); cmix.operation = "SUBTRACT"; cmix.inputs[0].default_value = 0.7
cmul = n.new("ShaderNodeMath"); cmul.operation = "MULTIPLY"; cmul.inputs[1].default_value = 0.7
l.new(fade.outputs["Result"], cmul.inputs[0]); l.new(cmul.outputs["Value"], cmix.inputs[1]); l.new(cmix.outputs["Value"], p.inputs["Coat Weight"])

brs, n, l, p = mat("brass")
p.inputs["Base Color"].default_value = (0.80, 0.62, 0.34, 1)
p.inputs["Metallic"].default_value = 1.0
p.inputs["Roughness"].default_value = 0.3
# nanako: the punched ring ground of Japanese metalwork, as a fine dimpled bump
gpos = n.new("ShaderNodeNewGeometry")
vor = n.new("ShaderNodeTexVoronoi"); vor.feature = "F1"; vor.inputs["Scale"].default_value = 900
l.new(gpos.outputs["Position"], vor.inputs["Vector"])
vb = n.new("ShaderNodeBump"); vb.inputs["Strength"].default_value = 0.35; vb.inputs["Distance"].default_value = 0.0003
l.new(vor.outputs["Distance"], vb.inputs["Height"]); l.new(vb.outputs["Normal"], p.inputs["Normal"])

# ---------- screen face ----------
TEX = os.environ.get("TEX", os.path.join(HERE, "p3"))
face, n, l, p = mat("face")
uv = n.new("ShaderNodeTexCoord")
def img(name, color=False):
    t = n.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(os.path.join(TEX, name))
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
seamk = n.new("ShaderNodeMath"); seamk.operation = "MULTIPLY"; seamk.inputs[1].default_value = float(os.environ.get("SEAMK", "0.45"))
l.new(leaf.outputs["Green"], seamk.inputs[0])
goldc = mixc(seamk.outputs["Value"], c1, (0.66, 0.46, 0.19, 1))
rough = n.new("ShaderNodeMapRange"); rough.inputs["To Min"].default_value = float(os.environ.get("RMIN", "0.12")); rough.inputs["To Max"].default_value = float(os.environ.get("RMAX", "0.34"))
l.new(patina.outputs["Fac"], rough.inputs["Value"])
burn = n.new("ShaderNodeMath"); burn.operation = "MULTIPLY_ADD"; burn.inputs[1].default_value = 0.03
l.new(leaf.outputs["Blue"], burn.inputs[0]); l.new(rough.outputs["Result"], burn.inputs[2])
crinkle = n.new("ShaderNodeTexNoise"); crinkle.inputs["Scale"].default_value = 260; crinkle.inputs["Detail"].default_value = 4
l.new(uv.outputs["UV"], crinkle.inputs["Vector"])
b1 = n.new("ShaderNodeBump"); b1.inputs["Strength"].default_value = 0.035; l.new(crinkle.outputs["Fac"], b1.inputs["Height"])
# relief: raised gesso clouds, gofun blossoms, the gold lines stand a hair proud
b2 = n.new("ShaderNodeBump"); b2.inputs["Strength"].default_value = float(os.environ.get("RELIEF", "0.6"))
b2.inputs["Distance"].default_value = float(os.environ.get("RELD", "0.0012"))
l.new(det.outputs["Green"], b2.inputs["Height"]); l.new(b1.outputs["Normal"], b2.inputs["Normal"])
NRM = b2.outputs["Normal"]
GESSO = float(os.environ.get("GESSO", "0.22"))
ground = mixs(GESSO, bsdf(goldc, 1.0, burn.outputs["Value"], NRM), diffuse(goldc, NRM))
# mist bands: a paler, finer gold, part dust and so part matte
cloud = mixs(float(os.environ.get("CLOUDM", "0.42")), bsdf((0.98, 0.80, 0.46, 1), 1.0, 0.32, NRM), diffuse((0.93, 0.77, 0.47, 1), NRM))
sh = mixs(sep.outputs["Blue"], ground, cloud)
# dust and cut leaf: bright fresh leaf, burnished
sh = mixs(det.outputs["Blue"], sh, mixs(0.3, bsdf((1.0, 0.82, 0.48, 1), 1.0, 0.2, NRM), diffuse((0.98, 0.82, 0.5, 1), NRM)))
# stream: murasaki with settled pigment, under a light coat
vcol = mixc(det.outputs["Red"], (0.062, 0.024, 0.19, 1), (0.105, 0.048, 0.28, 1))
sh = mixs(sep.outputs["Red"], sh, bsdf(vcol, 0.0, 0.42, NRM, **{"Coat Weight": 0.6, "Coat Roughness": 0.15}))
sh = mixs(sep.outputs["Green"], sh, mixs(0.45, bsdf((0.98, 0.84, 0.52, 1), 1.0, 0.25, NRM), diffuse((0.95, 0.80, 0.50, 1), NRM)))
# paint: matte
paint = bsdf(artT.outputs["Color"], 0.0, 0.85, NRM, **{"Specular IOR Level": 0.12})
sh = mixs(artT.outputs["Alpha"], sh, paint)
l.new(sh, n["Material Output"].inputs["Surface"])

fig, n, l, p = mat("figure")
FIGSET = os.environ.get("FIGSET", "2")
ft = n.new("ShaderNodeTexImage"); ft.image = bpy.data.images.load(os.path.join(HERE, "figure2.png" if FIGSET == "2" else "figure.png"))
p.inputs["Base Color"].default_value = (0, 0, 0, 1)
# SIL: how much of her is there, 1 to 0. The fold sequence fades her out as the screen shuts,
# since with the panels turned away there is no one left standing in the lamp.
SIL = float(os.environ.get("SIL", "1"))
silk = n.new("ShaderNodeMath"); silk.operation = "MULTIPLY"; silk.inputs[1].default_value = SIL
l.new(ft.outputs["Alpha"], silk.inputs[0]); l.new(silk.outputs["Value"], p.inputs["Alpha"])

# ---------- screen geometry ----------
PW, PH, T, FR, LEG = 1.0, 1.6, 0.035, 0.04, 0.05
BR = 0.032   # brocade mounting band around each painting

# mounting band: deep indigo silk with a faint woven sheen; a gold piping line edges the painting
brc, n, l, p = mat("brocade")
p.inputs["Base Color"].default_value = (0.014, 0.017, 0.045, 1)
p.inputs["Roughness"].default_value = 0.62
p.inputs["Sheen Weight"].default_value = 0.5
p.inputs["Sheen Tint"].default_value = (0.55, 0.6, 1.0, 1)
weave = n.new("ShaderNodeTexWave"); weave.wave_type = "BANDS"; weave.inputs["Scale"].default_value = 420
weave.inputs["Distortion"].default_value = 1.5
wb = n.new("ShaderNodeBump"); wb.inputs["Strength"].default_value = 0.08
l.new(weave.outputs["Fac"], wb.inputs["Height"]); l.new(wb.outputs["Normal"], p.inputs["Normal"])
pip, n, l, p = mat("piping")
p.inputs["Base Color"].default_value = (0.90, 0.70, 0.36, 1)
p.inputs["Metallic"].default_value = 1.0
p.inputs["Roughness"].default_value = 0.3
angles = [FOLD if i % 2 == 0 else -FOLD for i in range(4)]
# OPEN: the fold the camera and the lamp are set for. A render at a tighter FOLD is the same screen
# folding in front of the same camera and lamp, its middle held still, so the renders make one sequence.
OPEN = math.radians(float(os.environ.get("OPEN", math.degrees(FOLD))))
DY = 0.5 * PW * (math.sin(FOLD) - math.sin(OPEN))
open_centres = [Vector(((i - 1.5) * PW * math.cos(OPEN), 0.5 * PW * math.sin(OPEN), LEG + PH / 2)) for i in range(4)]

def box(name, size, loc, rz, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rz))
    ob = bpy.context.active_object; ob.name = name; ob.scale = size; ob.data.materials.append(m)
    if bevel:
        # rounded arrises: the lacquer and brass catch a thin line of light along every edge
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bv = ob.modifiers.new("bevel", "BEVEL"); bv.width = bevel; bv.segments = 3; bv.harden_normals = True
        bpy.ops.object.shade_smooth()
    return ob

def front(a):
    return Vector((math.sin(a), -math.cos(a), 0))

pts = [Vector((0, 0, 0))]
for a in angles:
    pts.append(pts[-1] + Vector((PW * math.cos(a), PW * math.sin(a), 0)))
cx = (pts[0].x + pts[-1].x) / 2
centres = []
for i, a in enumerate(angles):
    made = set(bpy.data.objects)
    c = (pts[i] + pts[i + 1]) / 2; c.x -= cx; c.y -= DY; c.z = LEG + PH / 2
    centres.append(c)
    box(f"frame{i}", (PW, T, PH), c, a, lac, 0.005)
    bpy.ops.mesh.primitive_plane_add(size=1)
    bo = bpy.context.active_object; bo.scale = (PW - 2 * FR, PH - 2 * FR, 1)
    bo.rotation_euler = (math.radians(90), 0, a)
    bo.location = c + front(a) * (T / 2 + 0.001)
    bo.data.materials.append(brc)
    bpy.ops.mesh.primitive_plane_add(size=1)
    po = bpy.context.active_object; po.scale = (PW - 2 * FR - 2 * BR + 0.009, PH - 2 * FR - 2 * BR + 0.009, 1)
    po.rotation_euler = (math.radians(90), 0, a)
    po.location = c + front(a) * (T / 2 + 0.0013)
    po.data.materials.append(pip)
    w, h = PW - 2 * FR - 2 * BR, PH - 2 * FR - 2 * BR
    bpy.ops.mesh.primitive_plane_add(size=1)
    ob = bpy.context.active_object; ob.scale = (w, h, 1)
    ob.rotation_euler = (math.radians(90), 0, a)
    ob.location = c + front(a) * (T / 2 + 0.0016)
    uvl = ob.data.uv_layers.active.data
    for loop in ob.data.loops:
        u, v = uvl[loop.index].uv
        uvl[loop.index].uv = ((i + (FR + BR) / PW + u * (w / PW)) / 4, (FR + BR) / PH + v * (h / PH))
    ob.data.materials.append(face)
    d = Vector((math.cos(a), math.sin(a), 0))
    # corner fittings (kanagu): an L of brass on each corner of the frame, three domed nails
    FL, FW, FT = 0.088, 0.027, 0.004
    for sx in (-1, 1):
        for sz in (-1, 1):
            def at(u, v, out):
                return c + d * (sx * u) + Vector((0, 0, sz * v)) + front(a) * (T / 2 + out)
            box(f"fitH{i}{sx}{sz}", (FL, FT, FW), at(PW / 2 - FL / 2 + 0.002, PH / 2 - FW / 2 + 0.002, FT / 2), a, brs, 0.0014)
            box(f"fitV{i}{sx}{sz}", (FW, FT, FL), at(PW / 2 - FW / 2 + 0.002, PH / 2 - FL / 2 + 0.002, FT / 2), a, brs, 0.0014)
            for (u, v) in ((PW / 2 - 0.012, PH / 2 - 0.012), (PW / 2 - FL + 0.014, PH / 2 - FW / 2 + 0.002), (PW / 2 - FW / 2 + 0.002, PH / 2 - FL + 0.014)):
                bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0036, segments=16, ring_count=8, location=at(u, v, FT))
                nail = bpy.context.active_object; nail.data.materials.append(brs); bpy.ops.object.shade_smooth()
        f = c + d * (sx * (PW / 2 - 0.07)); f.z = LEG / 2
        box(f"foot{i}{sx}", (0.07, T + 0.02, LEG), f, a, lac, 0.004)
    for ob in set(bpy.data.objects) - made:
        ob["panel"] = i

bpy.ops.mesh.primitive_plane_add(size=40)
floor = bpy.context.active_object
floor.data.materials.append(flo)
# CUTOUT: the screen alone on a transparent ground, for pages that set it on a flat colour. The floor
# keeps only the shadow it receives, and a pale world stands in for the lit room the leaf mirrors.
CUTOUT = os.environ.get("CUTOUT") == "1"
if CUTOUT:
    scn.render.film_transparent = True
    floor.is_shadow_catcher = True
    # matte, so the catcher keeps a soft contact shadow and no mirror image
    mf, _, _, mp_ = mat("matte floor"); mp_.inputs["Roughness"].default_value = 1.0
    mp_.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1)
    floor.data.materials[0] = mf
    wc = tuple(float(v) for v in os.environ.get("WORLDC", "0.30,0.28,0.26").split(","))
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (*wc, 1)

# ---------- her silhouette: a caster parallel to panel 2, near the fold with panel 1 ----------
P1 = centres[1]; A1 = angles[1]; D1 = Vector((math.cos(A1), math.sin(A1), 0))
FIG_H = float(os.environ.get("FIGH", "1.45" if FIGSET == "2" else "1.32"))
FIG_OFF = float(os.environ.get("FIGX", "0.05"))     # along panel 2, + = right
FIG_Z = float(os.environ.get("FIGZ", "0.80" if FIGSET == "2" else "0.88"))
DIST = float(os.environ.get("DIST", "0.03"))
bpy.ops.mesh.primitive_plane_add(size=1)
figob = bpy.context.active_object
figob.scale = (FIG_H * ft.image.size[0] / ft.image.size[1], FIG_H, 1)
figob.rotation_euler = (math.radians(90), 0, A1)
figob.location = P1 + D1 * FIG_OFF + front(A1) * DIST
figob.location.z = FIG_Z
figob.data.materials.append(fig)

# Gold is mostly mirror: inside a real cast shadow it still reflects the candles behind the camera,
# so the silhouette washes out. Project the same matte from the caster onto the screen face and
# darken the whole surface there; with the caster close to the panel this sits on the cast shadow.
SHK = float(os.environ.get("SHK", "0.95")) * SIL
if SHK > 0:
    fn_, fl_ = face.node_tree.nodes, face.node_tree.links
    out_ = fn_["Material Output"]
    last = out_.inputs["Surface"].links[0].from_socket
    tc = fn_.new("ShaderNodeTexCoord"); tc.object = figob
    mp = fn_.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    fl_.new(tc.outputs["Object"], mp.inputs["Vector"])
    proj = fn_.new("ShaderNodeTexImage"); proj.image = ft.image; proj.extension = "CLIP"; proj.interpolation = "Cubic"
    fl_.new(mp.outputs["Vector"], proj.inputs["Vector"])
    k = fn_.new("ShaderNodeMath"); k.operation = "MULTIPLY"; k.inputs[1].default_value = SHK
    fl_.new(proj.outputs["Alpha"], k.inputs[0])
    shade = fn_.new("ShaderNodeBsdfPrincipled")
    shade.inputs["Base Color"].default_value = (0.03, 0.018, 0.008, 1)
    shade.inputs["Metallic"].default_value = 0.6
    shade.inputs["Roughness"].default_value = 0.45
    sm = fn_.new("ShaderNodeMixShader")
    fl_.new(k.outputs["Value"], sm.inputs["Fac"]); fl_.new(last, sm.inputs[1]); fl_.new(shade.outputs["BSDF"], sm.inputs[2])
    fl_.new(sm.outputs["Shader"], out_.inputs["Surface"])
figob.visible_camera = False; figob.visible_glossy = False; figob.visible_diffuse = False

# ---------- lights ----------
def aim(ob, target):
    ob.rotation_euler = (Vector(target) - ob.location).to_track_quat("-Z", "Y").to_euler()

WARM = (1.0, 0.90, 0.78)
# lamp: from the front, a little left and above, along panel 2's normal; casts the silhouette
# set for the open screen, so it stays put while the screen folds
A1o = -OPEN; P1o = open_centres[1]; D1o = Vector((math.cos(A1o), math.sin(A1o), 0))
fig_open = P1o + D1o * FIG_OFF + front(A1o) * DIST; fig_open.z = FIG_Z
lamp_dir = (front(A1o) * 1.0 + D1o * -0.18 + Vector((0, 0, 0.14))).normalized()
bpy.ops.object.light_add(type="SPOT", location=fig_open + lamp_dir * 5.5)
key = bpy.context.active_object
key.data.energy = float(os.environ.get("KEY", "500")); key.data.color = tuple(float(v) for v in os.environ.get("LAMPC", "1.0,0.84,0.64").split(","))
key.data.spot_size = math.radians(float(os.environ.get("SPOT", "30"))); key.data.spot_blend = float(os.environ.get("BLEND", "0.55"))
key.data.shadow_soft_size = float(os.environ.get("SOFT", "0.025"))
aim(key, P1o + D1o * 0.1 + Vector((0, 0, float(os.environ.get("AIMZ", "-0.05")))))
# candle wall behind the camera: what the burnished leaf mirrors
WALLE = float(os.environ.get("WALL", "160"))
for k, (x, z, s, e) in enumerate([(-4.2, 1.0, 0.9, 1.0), (-2.6, 1.6, 0.7, 0.7), (-1.2, 0.8, 1.2, 1.25),
                                  (0.4, 1.4, 0.6, 0.6), (1.8, 0.9, 1.0, 0.9), (3.2, 1.7, 0.7, 0.55)]):
    bpy.ops.object.light_add(type="AREA", location=(x, -7.0, z))
    cw = bpy.context.active_object; cw.data.shape = "RECTANGLE"; cw.data.size = s; cw.data.size_y = 2.2
    cw.data.energy = WALLE * e * s / 0.9; cw.data.color = tuple(float(v) for v in os.environ.get("WALLC", "1.0,0.88,0.74").split(","))
    aim(cw, (0, 0, 0.9)); cw.visible_camera = False
# violet rim from behind-right: catches lacquer edges and the stream's coat
bpy.ops.object.light_add(type="AREA", location=(3.6, 2.2, 2.6))
rim = bpy.context.active_object; rim.data.size = 2.0; rim.data.energy = 220; rim.data.color = (0.62, 0.5, 1.0)
aim(rim, (0, 0, 0.8)); rim.visible_camera = False; rim.visible_glossy = False

# ---------- camera: square-on to panel 2 so her profile is not skewed ----------
bpy.ops.object.camera_add()
cam = bpy.context.active_object; scn.camera = cam
screen_mid = (open_centres[1] + open_centres[2]) / 2
look = (front(A1o) * 0.85 + front(OPEN) * 0.15).normalized()
if VIEW == "desktop":
    cam.data.lens = float(os.environ.get("LENS", "38"))
    cam.location = screen_mid + look * float(os.environ.get("CAMD", "4.4")) + Vector((0, 0, -0.1))
    cam.data.shift_x = float(os.environ.get("SHX", "-0.2")); cam.data.shift_y = float(os.environ.get("SHY", "0.04"))
elif VIEW == "mobile":
    cam.data.lens = float(os.environ.get("LENS", "30"))
    cam.location = screen_mid + look * float(os.environ.get("CAMD", "3.6")) + Vector((0, 0, -0.25))
    cam.data.shift_x = float(os.environ.get("SHX", "-0.1")); cam.data.shift_y = float(os.environ.get("SHY", "0.12"))
elif VIEW == "object":
    # the whole screen, centred, still square-on to panel 2: an object photographed for a catalogue
    mid = sum(open_centres, Vector()) / 4
    screen_mid = Vector((mid.x, mid.y, 0))
    cam.data.lens = float(os.environ.get("LENS", "50"))
    cam.location = screen_mid + look * float(os.environ.get("CAMD", "6.2")) + Vector((0, 0, float(os.environ.get("CAMZ", "1.05"))))
    cam.data.shift_y = float(os.environ.get("SHY", "0.0"))
cam.location.z = max(cam.location.z, 0.55)
# Tall renders keep the original frame and extend it downward, so the floor's reflection can run on
# below the hero. BASEH is the height the framing was designed at.
BASEH = int(os.environ.get("BASEH", RH))
if BASEH != RH:
    if RW >= BASEH:      # landscape: width set the field of view and the shift units
        cam.data.sensor_fit = "HORIZONTAL"
        cam.data.shift_y += 0.5 * (BASEH - RH) / max(RW, RH)
        cam.data.shift_x *= RW / max(RW, RH)
    else:                # portrait: height did; pin the same pixel scale to the width instead
        cam.data.sensor_fit = "HORIZONTAL"; cam.data.sensor_width = 36 * RW / BASEH
        # shift is measured in the fitted dimension: the height before, the width now
        cam.data.shift_y = (cam.data.shift_y * BASEH + BASEH / 2 - RH / 2) / RW
        cam.data.shift_x = cam.data.shift_x * BASEH / RW
aim(cam, Vector((screen_mid.x, screen_mid.y, LEG + PH / 2 if VIEW == "object" else cam.location.z)))

# FRONT=1,3: a matte of those panels only (the rest held out, the floor unseen), so a page can set
# type between the panels that fold toward the viewer and the ones that fold away.
if os.environ.get("FRONT"):
    keep = {int(v) for v in os.environ["FRONT"].split(",")}
    for ob in scn.objects:
        if ob.type != "MESH" or ob is floor:
            continue
        ob.is_holdout = ob.get("panel") not in keep
    floor.visible_camera = False

ANIM = int(os.environ.get("ANIM", "0"))
if not ANIM:
    bpy.ops.render.render(write_still=True)
    print("SAVED", OUT)
else:
    # Looping wind in her hair: warp only the hair region of the caster's alpha, frame by frame.
    import numpy as np
    img = ft.image
    W_, H_ = img.size
    src = np.empty(W_ * H_ * 4, np.float32); img.pixels.foreach_get(src)
    src = src.reshape(H_, W_, 4)[::-1].copy()          # top-down rows
    alpha = src[..., 3]
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    def sstep(a, b, v):
        t = np.clip((v - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
    # behind the head and down the back; strands move more toward the tips
    if FIGSET == "2":
        # hair behind the head and down the back, plus the strands falling forward over the shoulder
        back = sstep(540, 720, xx) * sstep(100, 380, yy) * (np.clip((yy - 100) / 1300, 0, 1) ** 1.1)
        front_ = 0.5 * sstep(360, 240, xx) * sstep(640, 820, yy) * np.clip((yy - 640) / 700, 0, 1)
        w = np.maximum(back, front_)
        AMP = 0.68
    else:
        w = sstep(880, 1140, xx) * sstep(160, 520, yy) * (np.clip((yy - 160) / 1250, 0, 1) ** 1.25)
        AMP = 1.0
    base_key = key.data.energy
    frames = range(int(os.environ.get("FROM", "0")), ANIM)
    for f in frames:
        t = f / ANIM
        sway = (np.sin(2 * np.pi * t + yy / 170) * 0.65 + 0.35 * np.sin(4 * np.pi * t + yy / 85 + 1.3))
        lift = 0.5 + 0.5 * np.sin(2 * np.pi * t - 0.6)
        dx = w * AMP * (16 * sway + 22 * lift)
        dy = w * AMP * 4 * np.cos(2 * np.pi * t + yy / 140)
        sx = np.clip(xx - dx, 0, W_ - 1.001); sy = np.clip(yy - dy, 0, H_ - 1.001)
        x0 = sx.astype(int); y0 = sy.astype(int); fx = sx - x0; fy = sy - y0
        a = (alpha[y0, x0] * (1 - fx) + alpha[y0, x0 + 1] * fx) * (1 - fy) + \
            (alpha[y0 + 1, x0] * (1 - fx) + alpha[y0 + 1, x0 + 1] * fx) * fy
        out = src.copy(); out[..., 3] = a
        img.pixels.foreach_set(out[::-1].ravel()); img.update()
        key.data.energy = base_key * (1 + 0.03 * np.sin(2 * np.pi * 3 * t) + 0.018 * np.sin(2 * np.pi * 7 * t + 1))
        scn.render.filepath = OUT.replace("####", f"{f:04d}")
        bpy.ops.render.render(write_still=True)
        print("FRAME", f, flush=True)

