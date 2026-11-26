# The studio: every object at its place under the final camera and lights. A finished object
# (objects/<name>.py) is used where there is one, the grey stand-in otherwise.
# Usage: blender -b --factory-startup -P scene.py -- out.png WIDTH SAMPLES
# (layers.py imports build_all() to render the hero's interactive layers from the same scene.)
import importlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import reset, cycles, place, finish  # noqa: E402


def builder(name):
    import standins
    if os.path.exists(os.path.join(HERE, "objects", name + ".py")):
        return importlib.import_module("objects." + name).build
    return getattr(standins, name)


def build_all():
    import standins
    for name in standins.ORDER:
        if name == "desk":
            place("desk", lambda: [builder(p)() for p in standins.DESK_PARTS])
        else:
            place(name, builder(name))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    OUT, WIDTH, SAMPLES = argv[0], int(argv[1]), int(argv[2])
    reset()
    cycles(SAMPLES, WIDTH)
    build_all()
    finish(OUT)
