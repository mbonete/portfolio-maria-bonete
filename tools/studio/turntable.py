# One object alone, under the scene's lights on the azurite shadow-catcher floor, from the scene camera's
# side and two three-quarter sides, plus a close view: for judging an object at full detail.
# Usage: blender -b --factory-startup -P turntable.py -- NAME OUT_PREFIX WIDTH SAMPLES
# Writes OUT_PREFIX-front.png, -left.png, -right.png, -close.png (transparent; see turntable.sh).
import importlib, math, os, sys
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import reset, cycles, floor, lights, aim  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
NAME, OUT, WIDTH, SAMPLES = argv[0], argv[1], int(argv[2]), int(argv[3])
reset()
cycles(SAMPLES, WIDTH)
import standins  # noqa: E402
from lib import made  # noqa: E402


def builder(name):
    if os.path.exists(os.path.join(HERE, "objects", name + ".py")):
        return importlib.import_module("objects." + name).build
    return getattr(standins, name)


names = standins.DESK_PARTS if NAME == "desk" else [p.strip() for p in NAME.split(",")]
obs = []
for n in names:
    obs += made(builder(n))
floor()
lights()
bpy.context.view_layer.update()

pts = []
dg = bpy.context.evaluated_depsgraph_get()
for ob in obs:
    if ob.type != "MESH":
        continue
    ev = ob.evaluated_get(dg)
    me = ev.to_mesh()
    pts += [ob.matrix_world @ v.co for v in me.vertices]
    ev.to_mesh_clear()
lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
mid, size = (lo + hi) / 2, (hi - lo).length

scn = bpy.context.scene
cd = bpy.data.cameras.new("cam")
cd.lens = 70
cam = bpy.data.objects.new("cam", cd)
scn.collection.objects.link(cam)
scn.camera = cam
scn.render.resolution_y = int(WIDTH * 0.75)
# the scene camera looks from -y, 13 degrees down; the turntable keeps that height and swings round
for view, turn, dist in (("front", 0, 3.0), ("left", -40, 3.0), ("right", 40, 3.0), ("close", -15, 1.5)):
    a = math.radians(turn)
    d = size * dist
    cam.location = mid + Vector((math.sin(a) * d * math.cos(0.23), -math.cos(a) * d * math.cos(0.23), d * math.sin(0.23)))
    aim(cam, mid if view != "close" else mid + Vector((0, 0, (hi.z - lo.z) * 0.18)))
    scn.render.filepath = f"{OUT}-{view}.png"
    bpy.ops.render.render(write_still=True)
    print("SAVED", scn.render.filepath)
