# The hero's interactive layers, rendered from the same scene, camera and lights as scene.py, so they
# stack back into the studio pixel for pixel:
#   base.png         the studio without the conga and the maracas. They are "indirect only" here: unseen
#                    by the camera, they still cast their shadows on the floor and show in reflections.
#   conga.png        the conga alone, everything else held out (so what stands in front of it cuts it),
#   maracas.png      except the other moving object, which is left out instead: its own layer goes on top.
#   keys-mask.png    the keyboard's silhouette, for the page's hit test (alpha only, few samples).
#   keys-base.png    the keyboard's corner of the studio as it is, and with its LEDs k times as bright
#   keys-lit-<k>.png for each k in KEYS_K; the page adds the difference on top when the keyboard is typed on.
#   full.png         (FULL=1) the studio in one piece, to check the stack against.
# Usage: blender -b --factory-startup -P layers.py -- OUTDIR WIDTH SAMPLES
import json, os, sys
import bpy
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import reset, cycles, floor, lights, camera  # noqa: E402
import scene  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUTDIR, WIDTH, SAMPLES = argv[0], int(argv[1]), int(argv[2])
MOVING = ["conga", "maracas"]
KEYS_K = [float(k) for k in os.environ.get("KEYS_K", "5 10 20").split()]
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


def flags(holdout=(), indirect=()):
    for n, lc in LC.items():
        lc.holdout = n in holdout
        lc.indirect_only = n in indirect


def render(name):
    scn.render.filepath = os.path.join(OUTDIR, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("SAVED", scn.render.filepath, flush=True)


def tree(root):
    out = [root]
    for c in root.children:
        out += tree(c)
    return out


if os.environ.get("FULL") == "1":
    flags()
    render("full")

flags(indirect=MOVING)
render("base")

fl.visible_camera = False
for name in MOVING:
    flags(holdout=[n for n in LC if n not in MOVING], indirect=[n for n in MOVING if n != name])
    render(name)

# the keyboard's silhouette: every other object held out one by one (the keyboard shares the desk's collection)
flags()
kb = next(o for o in scn.objects if o.name == "keyboard" and o.type == "EMPTY")
keys = set(tree(kb))
for ob in scn.objects:
    ob.is_holdout = ob not in keys
samples, denoise = scn.cycles.samples, scn.cycles.use_denoising
scn.cycles.samples, scn.cycles.use_denoising = 16, False
render("keys-mask")
for ob in scn.objects:
    ob.is_holdout = False
scn.cycles.samples, scn.cycles.use_denoising = samples, denoise
fl.visible_camera = True

# the keyboard's corner, as it is and brighter; same seed, so their noise matches and the difference is clean
dg = bpy.context.evaluated_depsgraph_get()
pts = []
for ob in keys:
    if ob.type == "MESH":
        me = ob.evaluated_get(dg).to_mesh()
        pts += [world_to_camera_view(scn, cam, ob.matrix_world @ v.co) for v in me.vertices]
        ob.evaluated_get(dg).to_mesh_clear()
x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
mx, my = 0.6 * (x1 - x0), 3.0 * (y1 - y0)
border = (max(0, x0 - mx), min(1, x1 + mx), max(0, y0 - my), min(1, y1 + my))
scn.render.use_border, scn.render.use_crop_to_border = True, False
scn.render.border_min_x, scn.render.border_max_x, scn.render.border_min_y, scn.render.border_max_y = border
render("keys-base")
gains = []
for name in ("key glow", "underglow"):
    t = bpy.data.materials[name].node_tree
    p = next(n for n in t.nodes if n.type == "BSDF_PRINCIPLED")
    s = p.inputs["Emission Strength"]
    mul = t.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    t.links.new(s.links[0].from_socket, mul.inputs[0])
    t.links.new(mul.outputs[0], s)
    gains.append(mul.inputs[1])
for k in KEYS_K:
    for g in gains:
        g.default_value = k
    render(f"keys-lit-{k:g}")

W, H = scn.render.resolution_x, scn.render.resolution_y
json.dump({"width": W, "height": H, "keys_border_px": [round(border[0] * W), round((1 - border[3]) * H),
                                                      round(border[1] * W), round((1 - border[2]) * H)]},
          open(os.path.join(OUTDIR, "layout.json"), "w"), indent=1)
print("DONE", W, H, border, flush=True)
