# The studio: every object at its place under the final camera and lights. A finished object
# (objects/<name>.py) is used where there is one, the grey stand-in otherwise.
# Usage: blender -b --factory-startup -P scene.py -- out.png WIDTH SAMPLES
import importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import reset, cycles, place, finish  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, WIDTH, SAMPLES = argv[0], int(argv[1]), int(argv[2])
reset()
cycles(SAMPLES, WIDTH)
import standins  # noqa: E402


def builder(name):
    if os.path.exists(os.path.join(HERE, "objects", name + ".py")):
        return importlib.import_module("objects." + name).build
    return getattr(standins, name)


for name in standins.ORDER:
    if name == "desk":
        place("desk", lambda: [builder(p)() for p in standins.DESK_PARTS])
    else:
        place(name, builder(name))
finish(OUT)
