# A pair of 27 cm wooden maracas crossed on the floor, as in the reference: gourd-shaped heads
# lacquered red at the tip and green at the neck, a band of bare wood between with painted stars and
# sprigs, on turned beech handles with a flared end. Built lying at rest: each touches the floor at
# its head and the end of its handle, the front one with its handle across the other's.
# Maraca-local metres: the axis along +x from the head's tip (x = 0) to the handle's end.
import math
from mathutils import Vector, Matrix
from objects.books_kit import lathe, empty, parent
from objects import maracas_shaders as sh

LENGTH = 0.270
HEAD_C, HEAD_R = 0.052, 0.0455          # the head's widest point and radius
NECK = 0.124                             # where the head closes round the handle
KNOB_X, KNOB_R = 0.2565, 0.0158


def _head_r(x):
    if x <= HEAD_C:
        t = (HEAD_C - x) / HEAD_C
        return HEAD_R * math.sqrt(max(0.0, 1 - t ** 2.15))
    t = (x - HEAD_C) / (NECK - HEAD_C)
    # the gourd tapers to its neck in a long S
    r_neck = 0.0150
    return r_neck + (HEAD_R - r_neck) * (0.5 + 0.5 * math.cos(math.pi * t)) ** 0.80


def head_profile():
    prof = [(0.0, 0.0)]
    n = 60
    for i in range(1, n + 1):
        x = HEAD_C * (1 - math.cos(math.pi / 2 * i / n))
        prof.append((_head_r(x), x))
    for i in range(1, 49):
        x = HEAD_C + (NECK - 0.004 - HEAD_C) * i / 48
        prof.append((_head_r(x), x))
    # the lip folds into the neck round the handle
    r_end = prof[-1][0]
    prof += [(r_end - 0.0008, NECK - 0.0025), (0.0136, NECK - 0.0012), (0.0131, NECK)]
    return prof


def handle_profile():
    pts = [(0.0115, NECK - 0.010), (0.0124, NECK - 0.002), (0.0128, NECK + 0.002), (0.0136, NECK + 0.0045),
           (0.0140, NECK + 0.0068), (0.0136, NECK + 0.0092), (0.0127, NECK + 0.0120)]
    x0 = NECK + 0.0120
    for i in range(1, 21):
        x = x0 + (KNOB_X - 0.020 - x0) * i / 20
        t = (x - x0) / (KNOB_X - 0.020 - x0)
        pts.append((0.0127 - 0.0017 * math.sin(math.pi * t * 0.8), x))
    # the flared end and its rounded knob
    for i in range(1, 17):
        t = i / 16
        x = KNOB_X - 0.020 + 0.020 * t
        pts.append((0.0112 + (KNOB_R - 0.0112) * t ** 2.2, x))
    for i in range(1, 9):
        a = math.pi / 2 * i / 8
        pts.append((KNOB_R - 0.0026 * (1 - math.cos(a)), KNOB_X + 0.0026 * math.sin(a)))
    r1 = pts[-1][0]
    for i in range(1, 9):
        a = math.pi / 2 * i / 8
        pts.append((r1 * math.cos(a) ** 0.9, KNOB_X + 0.0026 + (LENGTH - KNOB_X - 0.0026) * math.sin(a)))
    pts[-1] = (0.0, LENGTH)
    return [(0.0, NECK - 0.010)] + pts


def maraca(name, mats, roll):
    """One maraca with its axis along +x (lathe z mapped to x)."""
    to_x = Matrix.Rotation(math.radians(90), 4, "Y") @ Matrix.Rotation(math.radians(roll), 4, "Z")
    head = lathe(f"{name} head", head_profile(), 192, [mats["head"]])
    hand = lathe(f"{name} handle", handle_profile(), 96, [mats["handle"]])
    for o in (head, hand):
        o.data.transform(to_x)
    return [head, hand]


def _axis_z(x, alpha, z0):
    return z0 + x * math.tan(alpha)


def build():
    mats = sh.make()
    # A, behind: head on the floor, handle end on the floor. B, in front: head on the floor, its handle
    # across A's.
    a_head, a_turn, a_roll = Vector((-0.020, 0.046)), -10.0, 25.0
    b_head, b_turn, b_roll = Vector((-0.042, -0.046)), 21.0, 200.0
    # A's tilt: the head and the knob both touch the floor
    alpha_a = math.atan2(KNOB_R - HEAD_R, KNOB_X - HEAD_C)
    z0_a = HEAD_R - HEAD_C * math.tan(alpha_a)
    # where B's axis crosses A's, in the plan
    da = Vector((math.cos(math.radians(a_turn)), math.sin(math.radians(a_turn))))
    db = Vector((math.cos(math.radians(b_turn)), math.sin(math.radians(b_turn))))
    pa = a_head - da * HEAD_C            # A's tip in the plan
    pb = b_head - db * HEAD_C
    det = da.x * (-db.y) - da.y * (-db.x)
    rhs = pb - pa
    t = (rhs.x * (-db.y) - rhs.y * (-db.x)) / det
    u = (da.x * rhs.y - da.y * rhs.x) / det
    r_a = 0.0118 if t > NECK + 0.012 else 0.013
    r_b = 0.0115
    z_cross = _axis_z(t, alpha_a, z0_a) + r_a + r_b
    alpha_b = math.atan2(z_cross - HEAD_R, u - HEAD_C)
    z0_b = HEAD_R - HEAD_C * math.tan(alpha_b)
    obs = []
    for name, tip, turn, alpha, z0, roll in (("maraca A", pa, a_turn, alpha_a, z0_a, a_roll),
                                             ("maraca B", pb, b_turn, alpha_b, z0_b, b_roll)):
        root = empty(name, (tip.x, tip.y, z0), (0.0, -alpha, math.radians(turn)))
        parts = maraca(name, mats, roll)
        parent(parts, root)
        obs += [root] + parts
    return obs
