# The things on the desk, where the stand-ins put them: two compact studio monitors (the left one beside
# the monitors, the right one under the portrait monitor and turned with it), a mechanical keyboard with a
# violet underglow on a dark felt mat, a mouse, a small audio interface, a fat round cat figure and a pot of
# pencils and brushes, and the leads of the wired ones, run back over the desk's edge into its cable tray
# like the monitors'. Desk-local metres, the desk top at DESK_H; each thing hangs from an empty at its place.
import bpy
from mathutils import Vector
from common import DESK_H, MON_X, monitors_layout
from objects.desk_kit import cylinder, plastic, shared
from objects.monitors import into_tray
from objects.things_kit import empty, part, tube, sleeve, T, R, bx
from objects import things_speaker, things_keyboard, things_small


def _lead(name):
    from objects.monitors import _cable
    return shared("cable", _cable)


def at(e, x, y, z):
    """A point in an empty's frame, in desk coordinates."""
    bpy.context.view_layer.update()
    return e.matrix_world @ Vector((x, y, z))


def cables(spk_l, spk_r, kb, iface):
    z = DESK_H
    lead = _lead("cable")
    braid = sleeve("keyboard braid", (0.020, 0.020, 0.022), 0.0016)
    boot = plastic("plug boot", (0.012, 0.012, 0.013), 0.4)
    # keyboard: out of its back, off the mat and back past the arm's base
    r = 0.0019
    a = at(kb, -0.090, 0.0685, 0.0105)
    part("usb boot", cylinder(0.0042, 0.0, 0.016, 24, axis="y"), [boot], kb, bevel=0.0012, segs=2, at=T(-0.090, 0.0680, 0.0105))
    a = at(kb, -0.090, 0.0840, 0.0105)
    pts = [a, at(kb, -0.090, 0.092, 0.006), Vector((a.x - 0.004, 0.012, z + 0.004 + r)), Vector((a.x - 0.012, 0.030, z + r)),
           Vector((-0.505, 0.140, z + r)), Vector((-0.520, 0.300, z + r)), Vector((-0.522, 0.355, z + r))] + into_tray(-0.522, r)
    tube("keyboard cable", pts, r, braid, None, res=10)
    # audio interface: USB out of its right end, round the arm's base
    r = 0.0017
    part("usb boot", cylinder(0.0035, 0.0, 0.013, 24, axis="x"), [boot], iface, bevel=0.0010, segs=2, at=T(0.080, 0.030, 0.016))
    a = at(iface, 0.093, 0.030, 0.016)
    pts = [a, at(iface, 0.103, 0.032, 0.008), at(iface, 0.110, 0.045, r), Vector((-0.118, 0.200, z + r)),
           Vector((-0.120, 0.320, z + r)), Vector((-0.121, 0.355, z + r))] + into_tray(-0.121, r)
    tube("interface cable", pts, r, lead, None, res=10)
    # speakers: a plug in the back of each, the lead down to the desk and back
    r = 0.0026
    for e, route in ((spk_l, [Vector((-0.80, 0.24, z + r)), Vector((-0.62, 0.33, z + r)), Vector((-0.592, 0.355, z + r))]),
                     (spk_r, [Vector((0.800, 0.110, z + r)), Vector((0.802, 0.260, z + r)), Vector((0.740, 0.345, z + r)),
                              Vector((0.712, 0.355, z + r))])):
        sx = -0.022 if e is spk_l else 0.024
        part("speaker plug", cylinder(0.0050, 0.0, 0.020, 24, axis="y"), [boot], e, bevel=0.0012, segs=2,
             at=T(sx, things_speaker.D / 2 + 0.0040, 0.060))
        a = at(e, sx, things_speaker.D / 2 + 0.024, 0.060)
        if e is spk_l:
            pts = [a, at(e, sx, 0.110, 0.045), at(e, sx - 0.004, 0.122, r + 0.002), at(e, sx - 0.010, 0.140, r)] + route
            pts += into_tray(-0.592, r)
        else:
            pts = [a, at(e, sx + 0.012, 0.108, 0.048), at(e, 0.072, 0.104, 0.012), at(e, 0.096, 0.080, r)] + route
            pts += into_tray(0.712, r)
        tube("speaker cable", pts, r, lead, None, res=10)


def build():
    z, MX = DESK_H, MON_X
    p = monitors_layout()[2]
    px, py, pturn = p["centre"][0], p["centre"][1], p["turn"]
    spk_l = empty("speaker left", (MX - 0.68, 0.0, z), 10.0)
    things_speaker.speaker(spk_l)
    spk_r = empty("speaker right", (px - 0.03, py - 0.12, z), pturn)
    things_speaker.speaker(spk_r)
    things_keyboard.mat(empty("desk mat", (MX - 0.02, -0.13, z)))
    kb = empty("keyboard", (MX - 0.08, -0.135, z + 0.004), -1.2)
    things_keyboard.keyboard(kb)
    things_keyboard.mouse(empty("mouse", (MX + 0.26, -0.125, z + 0.004), 172.0))
    iface = empty("audio interface", (MX + 0.07, 0.088, z), 0.0)
    things_small.interface(iface)
    things_small.cat(empty("cat", (MX + 0.30, 0.078, z), -12.0))
    things_small.pot(empty("pot", (-0.90, -0.24, z), 0.0))
    cables(spk_l, spk_r, kb, iface)
