# The studio in grey: every object as a stand-in of its real size, at its place, under the final camera
# and lights, to judge the composition before anything is modelled.
# Usage: blender -b --factory-startup -P blockout.py -- out.png WIDTH SAMPLES
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import reset, cycles, place, finish  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, WIDTH, SAMPLES = argv[0], int(argv[1]), int(argv[2])
reset()
cycles(SAMPLES, WIDTH)
import standins  # noqa: E402  (after reset: its materials must survive)

for name in standins.ORDER:
    place(name, getattr(standins, name))
finish(OUT)
