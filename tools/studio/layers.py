# The hero's interactive layers, rendered from the same scene, camera and lights as scene.py, so they
# stack back into the studio pixel for pixel. Everything that moves on the page (MOVING) is "indirect
# only" in the room and in every region pass: unseen by the camera, it still casts its shadows and
# shows in reflections, and its own cut-out goes on top.
#   base.png                  the room without the moving things
#   capybara/conga/maracas.png  each alone, everything else held out (what stands in front cuts it),
#                             except the other moving things, which are left out: their layers stack
#   monstera-NN.png           the monstera alone, frame by frame of a breeze (00 is at rest)
#   mask-<name>.png           the silhouettes of the things that only light up or change (alpha only,
#                             few samples), for the page's hit test
#   <region>-base.png and its variants, each rendered inside a border round one thing, same seed, so
#   their noise matches:
#     keys-lit-<k>            the keyboard's LEDs k times as bright (added on top as light)
#     tower-p<n>              the computer's LEDs in palette n (shown in place where they differ)
#     easel-s<n>              the painting at stage n (painting.py PAINT_STAGE=n)
#     flash-lit               the camera's flash firing (added on top as light)
#   full.png                  (FULL=1) the studio in one piece, to check the stack against.
#   layout.json               the borders, in pixels, and the breeze's frame rate.
# Usage: [PASSES=base,cutouts,monstera,masks,keys,tower,easel,flash] blender -b --factory-startup
#        -P layers.py -- OUTDIR WIDTH SAMPLES
import json, math, os, sys
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import reset, cycles, floor, lights, camera  # noqa: E402
import scene  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, WIDTH, SAMPLES = argv[0], int(argv[1]), int(argv[2])
PASSES = set(os.environ.get("PASSES", "base,cutouts,monstera,masks,keys,tower,easel,flash").split(","))
MOVING = ["capybara", "conga", "maracas", "monstera"]
KEYS_K = [float(k) for k in os.environ.get("KEYS_K", "20").split()]
# the computer's LEDs run from CYAN to VIOLET (things_kit); each palette swaps those two for its own
CYAN, VIOLET = (0.0, 0.50, 1.0), (0.40, 0.045, 1.0)
PALETTES = [((1.0, 0.30, 0.02), (1.0, 0.03, 0.30)),     # sunset: orange to pink
            ((0.10, 1.0, 0.25), (0.0, 0.85, 0.55)),     # green to teal
            ((1.0, 0.78, 0.50), (1.0, 0.62, 0.36))]     # warm white
TOWER_LEDS = ("rgb ring", "ram light", "gpu light", "top light", "tower underglow", "shroud light", "power led")
STAGES = [1, 2, 3]
FPS, FRAMES = 15, 20
os.makedirs(OUTDIR, exist_ok=True)

reset()
cycles(SAMPLES, WIDTH)
scene.build_all()
fl = floor()
lights()
bpy.context.view_layer.update()
cam = camera(WIDTH)
scn = bpy.context.scene
LC = {lc.name: lc for lc in bpy.context.view_layer.layer_collection.children}
W, H = scn.render.resolution_x, scn.render.resolution_y
layout = {"width": W, "height": H, "fps": FPS, "frames": FRAMES, "borders": {}}


def flags(holdout=(), indirect=()):
    for n, lc in LC.items():
        lc.holdout = n in holdout
        lc.indirect_only = n in indirect


def room():
    """The state every region pass shares with base.png."""
    flags(indirect=MOVING)
    fl.visible_camera = True


def render(name):
    scn.render.filepath = os.path.join(OUTDIR, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("SAVED", scn.render.filepath, flush=True)


def tree(root):
    out = [root]
    for c in root.children:
        out += tree(c)
    return out


def empty(name):
    return next(o for o in scn.objects if o.name == name and o.type == "EMPTY")


def collection(name):
    return list(bpy.data.collections[name].all_objects)


def border(obs, mx, my, name):
    """Border round what obs show to the camera, grown by mx, my times their own size; kept in layout."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in obs:
        if ob.type == "MESH":
            ev = ob.evaluated_get(dg)
            me = ev.to_mesh()
            pts += [world_to_camera_view(scn, cam, ob.matrix_world @ v.co) for v in me.vertices]
            ev.to_mesh_clear()
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    dx, dy = mx * (x1 - x0), my * (y1 - y0)
    b = (max(0, x0 - dx), min(1, x1 + dx), max(0, y0 - dy), min(1, y1 + dy))
    scn.render.use_border, scn.render.use_crop_to_border = True, False
    scn.render.border_min_x, scn.render.border_max_x, scn.render.border_min_y, scn.render.border_max_y = b
    layout["borders"][name] = [round(b[0] * W), round((1 - b[3]) * H), round(b[1] * W), round((1 - b[2]) * H)]
    return b


def no_border():
    scn.render.use_border = False


if os.environ.get("FULL") == "1":
    flags()
    render("full")

if "base" in PASSES:
    room()
    render("base")

if "cutouts" in PASSES:
    fl.visible_camera = False
    for name in ("capybara", "conga", "maracas"):
        flags(holdout=[n for n in LC if n not in MOVING], indirect=[n for n in MOVING if n != name])
        render(name)
    fl.visible_camera = True

# ---------- the monstera in a breeze ----------
# A gust from the left, then the plant settles: every leaf swings about its node on the stem (the long
# low ones slower and further, the young ones quicker), and each blade flutters about its own base.
# Leaves carry their pivots from monstera.py (sway_node, sway_blade, in the plant's own space); a
# leaf's blade, midrib and petiole share them.
if "monstera" in PASSES:
    import random
    rnd = random.Random(7)
    parts = [o for o in collection("monstera") if "sway_node" in o]
    leaves = {}
    for o in parts:
        leaves.setdefault(tuple(o["sway_node"]), []).append(o)
    rest = {o.name: o.matrix_basis.copy() for o in parts}
    motion = {}
    for k, obs in leaves.items():
        tier = obs[0]["sway_tier"]
        motion[k] = ({"young": 6.0, "up": 4.5, "mid": 6.5, "low": 8.0}[tier] * rnd.uniform(0.8, 1.2),
                     {"young": 2.1, "up": 1.7, "mid": 1.4, "low": 1.15}[tier] * rnd.uniform(0.9, 1.1),
                     rnd.uniform(0.0, 0.5), rnd.uniform(6.0, 10.0), rnd.uniform(2.3, 3.0), rnd.uniform(0, 1.5))
    T_END = (FRAMES - 1) / FPS

    def pose(t):
        # pushed over in the first tenth of a second, swinging down, faded to rest by the last frame
        win = 1.0 if t < 0.7 * T_END else max(0.0, 1 - (t - 0.7 * T_END) / (0.3 * T_END))
        win = win * win * (3 - 2 * win)
        rise = min(1.0, t / 0.12)
        for k, obs in leaves.items():
            amp, freq, ph, bamp, bfreq, bph = motion[k]
            th = math.radians(amp) * rise * win * math.exp(-t / 0.65) * math.sin(2 * math.pi * freq * t + ph)
            be = math.radians(bamp) * rise * win * math.exp(-t / 0.45) * math.sin(2 * math.pi * bfreq * t + bph)
            S, E = Vector(obs[0]["sway_node"]), Vector(obs[0]["sway_blade"])
            node = Matrix.Translation(S) @ Matrix.Rotation(th, 4, "Y") @ Matrix.Translation(-S)
            blade = Matrix.Translation(E) @ Matrix.Rotation(be, 4, "Y") @ Matrix.Translation(-E)
            for o in obs:
                o.matrix_basis = node @ (Matrix() if "petiole" in o.name else blade) @ rest[o.name]

    fl.visible_camera = False
    flags(holdout=[n for n in LC if n not in MOVING], indirect=[n for n in MOVING if n != "monstera"])
    border(collection("monstera"), 0.15, 0.08, "monstera")
    for f in range(FRAMES):
        pose(f / FPS)
        bpy.context.view_layer.update()
        render(f"monstera-{f:02d}")
    for o in parts:
        o.matrix_basis = rest[o.name]
    no_border()
    fl.visible_camera = True

# ---------- silhouettes for the hit test ----------
if "masks" in PASSES:
    targets = {"keys": tree(empty("keyboard")), "camera": tree(empty("camera")), "tower": tree(empty("tower")),
               "easel": collection("easel")}
    flags()
    fl.visible_camera = False
    samples, denoise = scn.cycles.samples, scn.cycles.use_denoising
    scn.cycles.samples, scn.cycles.use_denoising = 16, False
    for name, obs in targets.items():
        keep = set(obs)
        for ob in scn.objects:
            ob.is_holdout = ob not in keep
        render(f"mask-{name}")
    for ob in scn.objects:
        ob.is_holdout = False
    scn.cycles.samples, scn.cycles.use_denoising = samples, denoise
    fl.visible_camera = True


def led_gain(names):
    """A multiplier on the Emission Strength of the named LED materials; returns its inputs."""
    gains = []
    for m in bpy.data.materials:
        if m.name in names and m.node_tree:
            t = m.node_tree
            p = next(n for n in t.nodes if n.type == "BSDF_PRINCIPLED")
            s = p.inputs["Emission Strength"]
            mul = t.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = 1.0
            t.links.new(s.links[0].from_socket, mul.inputs[0])
            t.links.new(mul.outputs[0], s)
            gains.append(mul.inputs[1])
    return gains


# ---------- the keyboard's LEDs flaring ----------
if "keys" in PASSES:
    room()
    border(tree(empty("keyboard")), 0.6, 3.0, "keys")
    render("keys-base")
    gains = led_gain({"key glow", "underglow"})
    for k in KEYS_K:
        for g in gains:
            g.default_value = k
        render(f"keys-lit-{k:g}")
    for g in gains:
        g.default_value = 1.0
    no_border()

# ---------- the computer's LEDs in other colours ----------
if "tower" in PASSES:
    room()
    border(tree(empty("tower")), 0.7, 0.35, "tower")
    render("tower-base")
    sockets = []    # every colour input set to CYAN or VIOLET in the computer's LED materials
    for m in bpy.data.materials:
        if m.node_tree and (m.name in TOWER_LEDS or m.name.startswith("pump ring")):
            for n in m.node_tree.nodes:
                for i in n.inputs:
                    if i.type == "RGBA" and not i.is_linked:
                        c = tuple(i.default_value[:3])
                        for which, ref in ((0, CYAN), (1, VIOLET)):
                            if all(abs(a - b) < 1e-3 for a, b in zip(c, ref)):
                                sockets.append((i, which))
    print("tower LED colour inputs:", len(sockets), flush=True)
    for n, pal in enumerate(PALETTES, 1):
        for i, which in sockets:
            i.default_value = (*pal[which], 1.0)
        render(f"tower-p{n}")
    for i, which in sockets:
        i.default_value = (*(CYAN, VIOLET)[which], 1.0)
    no_border()

# ---------- the painting, stage by stage ----------
if "easel" in PASSES:
    room()
    imgs = [im for im in bpy.data.images if os.path.basename(im.filepath).startswith("painting")]
    canvas = [o for o in collection("easel") if o.type == "MESH" and any(
        s.material and s.material.node_tree and any(n.type == "TEX_IMAGE" and n.image in imgs
                                                    for n in s.material.node_tree.nodes) for s in o.material_slots)]
    border(canvas or collection("easel"), 0.03, 0.03, "easel")
    render("easel-base")
    orig = {im.name: im.filepath for im in imgs}
    for st in STAGES:
        for im in imgs:
            f = orig[im.name]
            im.filepath = f.replace("painting_paint.png", f"painting-s{st}_paint.png").replace(
                "painting.png", f"painting-s{st}.png")
            im.reload()
        render(f"easel-s{st}")
    for im in imgs:
        im.filepath = orig[im.name]
        im.reload()
    no_border()

# ---------- the camera's flash ----------
# A pop-up flash at the front of the prism's top, as on most DSLRs: a small, very bright panel facing
# where the lens points, and its light on what is in front.
if "flash" in PASSES:
    room()
    root = empty("camera")
    cm = root.matrix_world
    prism = next(o for o in tree(root) if o.name.startswith("camera prism"))
    inv = cm.inverted()
    loc = [inv @ (prism.matrix_world @ v.co) for v in prism.data.vertices]
    ztop = max(p.z for p in loc)
    yfront = min(p.y for p in loc if p.z > ztop - 0.012)
    head = cm @ Vector((0.006, yfront - 0.002, ztop - 0.006))
    ahead = (cm.to_3x3() @ Vector((0, -1, 0))).normalized()
    turn = ahead.to_track_quat("-Z", "Y").to_euler()
    ld = bpy.data.lights.new("flash", "AREA")
    ld.shape, ld.size, ld.size_y = "RECTANGLE", 0.03 * 1.32, 0.012 * 1.32
    ld.energy = float(os.environ.get("FLASH_W", "120"))
    ld.color = (1.0, 0.97, 0.92)
    lo = bpy.data.objects.new("flash", ld)
    scn.collection.objects.link(lo)
    lo.location, lo.rotation_euler = head + ahead * 0.004, turn
    # its light reaches everything but the camera itself, which it sits on
    rec = bpy.data.collections.new("flash receivers")
    body = set(tree(root))
    for c in scn.collection.children:
        if c.name != "books":
            rec.children.link(c)
    for o in collection("books"):
        if o not in body:
            rec.objects.link(o)
    rec.objects.link(fl)
    lo.light_linking.receiver_collection = rec
    # the flash window itself, seen lit by the camera
    bpy.ops.mesh.primitive_plane_add(size=1, location=head + ahead * 0.002)
    win = bpy.context.active_object
    win.name = "flash window"
    win.scale = (0.028 * 1.32, 0.011 * 1.32, 1)
    win.rotation_euler = turn
    wm = bpy.data.materials.new("flash window")
    wm.use_nodes = True
    em = wm.node_tree.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = float(os.environ.get("FLASH_WINDOW", "25"))
    wm.node_tree.links.new(em.outputs[0], wm.node_tree.nodes["Material Output"].inputs["Surface"])
    win.data.materials.append(wm)
    win.visible_shadow = False
    win.hide_render = lo.hide_render = True
    p = world_to_camera_view(scn, cam, head)
    layout["flash_head"] = [round(p.x * W), round((1 - p.y) * H)]   # where the page draws the flash's burst
    border(collection("books"), 1.6, 0.35, "flash")
    render("flash-base")
    win.hide_render = lo.hide_render = False
    render("flash-lit")
    no_border()

json.dump(layout, open(os.path.join(OUTDIR, "layout.json"), "w"), indent=1)
print("DONE", W, H, json.dumps(layout["borders"]), flush=True)
