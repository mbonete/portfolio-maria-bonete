# The grey stand-ins: every object at its real size, as simple shapes. The blockout renders only these;
# the finished scene uses them for whatever is not modelled yet (objects/<name>.py replaces <name>).
import bpy, math, os, random
from mathutils import Vector
from common import DESK_H, DESK_W, DESK_D, MON_X, TOWER_X, monitors_layout
from lib import material, box, cyl, blob, lathe, CLAY, DARK, SCREEN, RGB


# ---------- easel: an A-frame studio easel, the canvas tilted back on its ledge ----------
def easel():
    H = 1.75
    for s in (-1, 1):
        box((0.034, 0.024, 1.62), (s * 0.20, 0.02, 0.80), (-0.10, -s * 0.13, 0))  # splayed front legs
    box((0.04, 0.03, H), (0, 0.06, H / 2), (-0.10, 0, 0))  # mast
    box((0.032, 0.024, 1.55), (0, 0.42, 0.74), (0.40, 0, 0))  # back leg
    box((0.80, 0.11, 0.06), (0, -0.07, 0.62))  # ledge with its drawer
    box((0.874, 0.028, 0.88), (0, 0.0, 1.07), (-0.10, 0, 0), material("canvas", (0.82, 0.80, 0.76)))
    box((0.10, 0.05, 0.05), (0, 0.10, 1.53))  # top clamp


# ---------- desk: one straight standing desk, 2.2 x 0.75 m, and what stands on it ----------
def desk_frame():
    z = DESK_H
    box((DESK_W, DESK_D, 0.03), (0, 0, z - 0.015))
    for x in (-0.92, 0.92):
        box((0.07, 0.05, z - 0.06), (x, 0.08, (z - 0.06) / 2 + 0.03), m=DARK)
        box((0.08, 0.70, 0.03), (x, 0.08, 0.015), m=DARK)  # T foot


def monitors():
    z = DESK_H
    for m in monitors_layout():
        x, y, zc = m["centre"]
        rot = (0, 0, math.radians(m["turn"]))
        box((m["w"], 0.022, m["h"]), (x, y, zc), rot, DARK)
        n = Vector((math.sin(rot[2]), -math.cos(rot[2]), 0))  # towards the viewer
        c = Vector((x, y, zc)) + n * 0.013
        box((m["w"] - 0.02, 0.004, m["h"] - 0.025), tuple(c), rot, SCREEN)
    for fx, fy in {tuple(m["foot"]) for m in monitors_layout()}:
        cyl(0.018, 0.60, (fx, fy + 0.02, z + 0.30), m=DARK)
        box((0.22, 0.16, 0.012), (fx, fy, z + 0.006), m=DARK)


def tower():
    z, tx = DESK_H, TOWER_X
    box((0.24, 0.46, 0.48), (tx, 0.10, z + 0.24), m=DARK)
    box((0.004, 0.40, 0.42), (tx - 0.122, 0.10, z + 0.25), m=RGB)
    box((0.22, 0.004, 0.42), (tx, 0.10 - 0.232, z + 0.25), m=RGB)


def desk_things():
    """Speakers, keyboard on its mat, mouse, audio interface, the fat cat figure, a pot of brushes."""
    z, MX = DESK_H, MON_X
    p = monitors_layout()[2]
    px, py = p["centre"][0], p["centre"][1]
    box((0.12, 0.15, 0.20), (MX - 0.68, 0.0, z + 0.10), m=DARK)
    box((0.12, 0.15, 0.20), (px - 0.03, py - 0.12, z + 0.10), (0, 0, math.radians(p["turn"])), DARK)
    box((0.80, 0.30, 0.004), (MX - 0.02, -0.13, z + 0.002), m=DARK)
    box((0.44, 0.14, 0.03), (MX - 0.08, -0.13, z + 0.017), m=DARK)
    blob((0.035, 0.06, 0.02), (MX + 0.26, -0.13, z + 0.02), DARK)
    box((0.16, 0.10, 0.045), (MX + 0.07, 0.10, z + 0.022), m=DARK)
    blob((0.06, 0.05, 0.055), (MX + 0.30, 0.06, z + 0.055))  # the cat, about 11 cm
    cyl(0.04, 0.10, (-0.90, -0.24, z + 0.05), m=DARK)


DESK_PARTS = ["desk_frame", "monitors", "tower", "desk_things"]


def desk():
    for part in DESK_PARTS:
        globals()[part]()


# ---------- monstera: a tall potted monstera in a black cylinder pot, beside the easel ----------
def monstera():
    rnd = random.Random(7)
    POT_H, POT_R = 0.45, 0.13
    cyl(POT_R, POT_H, (0, 0, POT_H / 2), m=DARK, verts=48)
    green = material("leaf", (0.10, 0.22, 0.10), 0.5)
    # leaves on long stalks, rising from the pot in a loose spiral, lower ones reaching further out
    for k in range(13):
        t = k / 12
        h = POT_H + 0.18 + 0.82 * t + rnd.uniform(-0.04, 0.04)
        a = k * 2.4 + rnd.uniform(-0.3, 0.3)
        reach = 0.30 - 0.14 * t + rnd.uniform(-0.03, 0.03)
        tip = Vector((reach * math.cos(a), reach * math.sin(a), h))
        base = Vector((0.02 * math.cos(a), 0.02 * math.sin(a), POT_H))
        mid = (base + tip) / 2
        stalk = tip - base
        cyl(0.007, stalk.length, mid, stalk.to_track_quat("Z", "Y").to_euler(), green, 8)
        size = 0.30 + 0.10 * (1 - t) + rnd.uniform(-0.03, 0.03)
        leaf = blob((size * 0.55, size * 0.5, 0.012), tip + Vector((0.6 * size * 0.55 * math.cos(a), 0.6 * size * 0.55 * math.sin(a), -0.03)), green)
        leaf.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(0.25, 0.6) * (1 if math.cos(a) > 0 else -1), a)


# ---------- palette: a wooden painter's palette on the floor, dabs of paint and a brush across it ----------
def palette():
    blob((0.20, 0.15, 0.004), (0, 0, 0.004), material("palette wood", (0.55, 0.38, 0.22), 0.5))
    for k, (dx, dy, col) in enumerate([(-0.12, 0.05, (0.75, 0.55, 0.10)), (-0.06, 0.10, (0.70, 0.10, 0.08)),
                                       (0.02, 0.11, (0.10, 0.20, 0.55)), (0.10, 0.08, (0.95, 0.92, 0.85)),
                                       (0.14, 0.01, (0.10, 0.35, 0.15)), (-0.13, -0.04, (0.40, 0.15, 0.45))]):
        blob((0.018, 0.016, 0.008), (dx, dy, 0.010), material(f"paint {k}", col, 0.3))
    cyl(0.004, 0.26, (0.0, -0.03, 0.013), (0, math.radians(90), math.radians(18)), DARK, 12)


# ---------- capybara: a big seated plush with a scarf ----------
def capybara():
    S = 1.12
    def k(v):
        return tuple(S * x for x in v)
    blob(k((0.25, 0.22, 0.25)), k((0, 0, 0.25)))
    blob(k((0.17, 0.17, 0.15)), k((0, -0.04, 0.53)))
    blob(k((0.10, 0.09, 0.07)), k((0, -0.16, 0.50)))
    for s in (-1, 1):
        blob(k((0.035, 0.02, 0.03)), k((s * 0.12, 0.02, 0.66)))  # ears
        blob(k((0.06, 0.08, 0.05)), k((s * 0.12, -0.16, 0.05)))  # feet
        blob(k((0.05, 0.05, 0.10)), k((s * 0.14, -0.15, 0.27)))  # arms
    bpy.ops.mesh.primitive_torus_add(major_radius=0.15 * S, minor_radius=0.035 * S, location=k((0, -0.02, 0.42)))
    scarf = bpy.context.active_object
    scarf.data.materials.append(DARK)
    box(k((0.07, 0.025, 0.20)), k((0.06, -0.17, 0.32)), (0.1, 0, 0.1), DARK)


# ---------- coffee tray: cup and saucer, a burlap bag of beans spilling ----------
def tray():
    L, Wd = 0.58, 0.40
    box((L, Wd, 0.014), (0, 0, 0.007))
    for s in (-1, 1):
        box((L, 0.014, 0.05), (0, s * (Wd / 2 - 0.007), 0.025))
        box((0.014, Wd, 0.05), (s * (L / 2 - 0.007), 0, 0.025))
    cyl(0.08, 0.008, (-0.10, -0.03, 0.018))
    cyl(0.046, 0.06, (-0.10, -0.03, 0.052))
    blob((0.16, 0.11, 0.09), (0.20, 0.05, 0.08), DARK)


# ---------- books: a stack of ten, the camera on top ----------
def books():
    rnd = random.Random(4)
    z = 0
    for k in range(10):
        t = rnd.uniform(0.04, 0.065)
        w, d = rnd.uniform(0.28, 0.34), rnd.uniform(0.20, 0.25)
        box((w, d, t), (rnd.uniform(-0.012, 0.012), rnd.uniform(-0.01, 0.01), z + t / 2), (0, 0, math.radians(rnd.uniform(-7, 7))))
        z += t
    box((0.15, 0.08, 0.11), (0, 0.01, z + 0.055), m=DARK)
    cyl(0.042, 0.12, (-0.03, -0.09, z + 0.055), (math.radians(90), 0, math.radians(-20)), DARK)


# ---------- conga: 76 cm, a 29.6 cm head, its top about level with the desk top ----------
def conga():
    lathe([(0.118, 0.0), (0.128, 0.06), (0.155, 0.23), (0.168, 0.38), (0.160, 0.53), (0.146, 0.67), (0.148, 0.72), (0.148, 0.76)])


# ---------- maracas: a pair of 27 cm, crossed on the floor ----------
def maracas():
    for s, rz in ((-1, 25), (1, 5)):
        a = math.radians(rz)
        d = Vector((math.cos(a), math.sin(a), 0))
        c = Vector((s * 0.03, s * 0.05, 0.047))
        bulb = blob((0.06, 0.047, 0.047), c, material("maraca", (0.5, 0.12, 0.1)))  # 12 cm long, 9.4 cm across
        bulb.rotation_euler = (0, 0, a)
        cyl(0.011, 0.15, c + d * 0.13 + Vector((0, 0, -0.025)), (0, math.radians(90), a), CLAY)  # 27 cm in all


# ---------- the folding screen: four 1 x 1.6 m panels in a zigzag, as in the hero today ----------
def screen():
    PW, PH, T, LEG = 1.0, 1.6, 0.035, 0.05
    fold = math.radians(float(os.environ.get("FOLD", "74")))
    angles = [fold if i % 2 == 0 else -fold for i in range(4)]
    pts = [Vector((0, 0, 0))]
    for a in angles:
        pts.append(pts[-1] + Vector((PW * math.cos(a), PW * math.sin(a), 0)))
    cx = (pts[0].x + pts[-1].x) / 2
    gold = material("gold", (0.75, 0.55, 0.25), 0.35)
    for i, a in enumerate(angles):
        c = (pts[i] + pts[i + 1]) / 2
        c.x -= cx
        c.y -= 0.25
        c.z = LEG + PH / 2
        box((PW, T, PH), c, (0, 0, a), DARK)
        n = Vector((math.sin(a), -math.cos(a), 0))
        box((PW - 0.08, 0.004, PH - 0.08), c + n * (T / 2 + 0.002), (0, 0, a), gold)



ORDER = ["screen", "monstera", "tray", "desk", "capybara", "books", "maracas", "conga", "easel", "palette"]
