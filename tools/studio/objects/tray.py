# The coffee tray on the floor: a 58 x 40 cm walnut serving tray with routed handle slots, a white
# porcelain cup of coffee on its saucer with an espresso spoon, and a burlap sack lying on its side,
# its rolled mouth spilling roasted beans onto the tray, with loose beans scattered. Real size, floor at
# z = 0, long side along x (the stand-in's footprint).
import math, random
from mathutils import Vector, Matrix, Euler, noise as mnoise
from objects import tray_shapes as ts
from objects import tray_shaders as sh
from objects import tray_beans as tb
from objects import tray_sack as sk
from objects.books_kit import empty, parent

CUP = (-0.128, 0.022)                   # the saucer's centre on the tray
CUP_TURN = -28.0                        # the handle points right, a little toward the camera
SACK = (0.122, 0.036, 47.0)             # the sack's middle and turn (its mouth faces left and forward)
LEVEL = 0.0480                          # the coffee's surface in the cup


def cup_set(mats):
    obs = []
    root = empty("cup set", (CUP[0], CUP[1], ts.FLOOR_TOP), (0, 0, 0))
    sau = ts.saucer([mats["porcelain"]])
    cup_root = empty("cup", (0, 0, 0.0052), (0, 0, math.radians(CUP_TURN)))
    cup_root.parent = root
    c = ts.cup([mats["cup"]])
    h = ts.handle([mats["porcelain"]])
    cof = ts.coffee([mats["crema"]], LEVEL)
    parent([c, h, cof], cup_root)
    sp = ts.spoon([mats["steel"]])
    # the spoon rests on the saucer at the cup's front left, its handle over the rim
    sp.location = (-0.0079, -0.0601, 0.0135)
    sp.rotation_euler = (0.0, math.radians(2.9), math.radians(125.2))
    sau.parent = root
    sp.parent = root
    return [root, sau, cup_root, c, h, cof, sp]


def _poisson(rnd, region, spacing, tries=30, limit=4000):
    """Points in a region (a predicate over x, y within a box) at least spacing apart."""
    (x0, x1, y0, y1), ok = region
    cell = spacing / math.sqrt(2)
    grid = {}
    pts = []
    for _ in range(limit * tries):
        if len(pts) >= limit:
            break
        x, y = rnd.uniform(x0, x1), rnd.uniform(y0, y1)
        if not ok(x, y):
            continue
        gx, gy = int(x / cell), int(y / cell)
        clash = False
        for i in range(gx - 2, gx + 3):
            for j in range(gy - 2, gy + 3):
                q = grid.get((i, j))
                if q and (q[0] - x) ** 2 + (q[1] - y) ** 2 < spacing * spacing:
                    clash = True
                    break
            if clash:
                break
        if not clash:
            grid[(gx, gy)] = (x, y)
            pts.append((x, y))
    return pts


XM = sk.X0 - sk.LEN                     # the mouth's lip in sack-local x


def heap_h(x, y):
    """The beans' surface in sack-local space (height above the tray floor), or None outside it."""
    ry1, rz1, sink1 = sk.section(1.0)
    lip = 0.050
    if x >= XM:
        s = (sk.X0 - x) / sk.LEN
        ry, rz, sink = sk.section(s)
        top = 2 * rz * (1 - sink) - 0.010
        lev = min(top, lip + (x - XM) * 0.55)
        yy = y / max(ry - 0.006, 1e-4)
        if abs(yy) >= 1:
            return None
        # the cloth's sides curve in: beans lower toward the flanks
        return lev * (1 - 0.55 * yy ** 4) if x < XM + 0.07 else None
    d = XM - x
    # the fan's reach varies round its edge, and its surface is lumpy
    wav = mnoise.noise(Vector((y * 18.0, 0.7, 2.3)))
    run = 0.115 * (1 + 0.22 * wav)
    wfan = ry1 * 0.92 + 0.55 * d
    yy = y / wfan
    if abs(yy) >= 1 or d >= run:
        return None
    t = d / run
    h = lip * (1 - t) ** 1.7 * (1 - yy * yy) ** 0.6
    h *= 1 + 0.12 * mnoise.noise(Vector((x * 40.0, y * 40.0, 5.1)))
    return h


def heap_normal(x, y, e=0.002):
    hx0, hx1 = heap_h(x - e, y), heap_h(x + e, y)
    hy0, hy1 = heap_h(x, y - e), heap_h(x, y + e)
    h = heap_h(x, y)
    hx0 = h if hx0 is None else hx0
    hx1 = h if hx1 is None else hx1
    hy0 = h if hy0 is None else hy0
    hy1 = h if hy1 is None else hy1
    return Vector((-(hx1 - hx0) / (2 * e), -(hy1 - hy0) / (2 * e), 1.0)).normalized()


def heap_beans(rnd, meshes):
    """Two layers of beans over the heap, each lying on the slope at a jumbled angle."""
    items = []
    box = (XM - 0.12, XM + 0.075, -0.16, 0.16)

    def ok(x, y):
        h = heap_h(x, y)
        if h is None or h < 0.002:
            return False
        if x > XM - 0.004 and not sk.inside(x, y, h, margin=0.007):
            return False
        if x < XM:
            # thin out toward the fan's edge: the last beans lie apart
            d = XM - x
            ry1 = sk.section(1.0)[0]
            e = max(d / 0.115, abs(y) / (ry1 * 0.92 + 0.55 * d))
            if e > 0.62 and rnd.random() > (1.0 - (e - 0.62) / 0.38) ** 1.5:
                return False
        return True

    for layer, (spacing, drop) in enumerate(((0.0074, 0.0), (0.0080, 0.0048))):
        for x, y in _poisson(rnd, (box, ok), spacing):
            h = heap_h(x, y) - drop
            if h < 0.0:
                continue
            var = rnd.randrange(len(meshes))
            _, (a, b, cf, cb) = meshes[var]
            nrm = heap_normal(x, y)
            face_up = rnd.random() < 0.5
            yaw = rnd.uniform(0, 2 * math.pi)
            q = Euler((0, 0, yaw)).to_quaternion()
            if face_up:
                q = q @ Euler((math.pi, 0, 0)).to_quaternion()
            jumble = Euler((rnd.gauss(0, 0.32), rnd.gauss(0, 0.32), 0)).to_quaternion()
            align = Vector((0, 0, 1)).rotation_difference(nrm)
            q = align @ jumble @ q
            lift = (cb if face_up else cf) * 0.85
            p = Vector((x, y, h)) + nrm * lift
            p.z = max(p.z, (cb if face_up else cf) * 0.9)
            items.append((p, q, var))
    return items


def to_tray(items):
    """Sack-local placements to the tray's frame (on its floor), leaving the saucer and the walls
    clear."""
    sx, sy, turn = SACK
    R = Euler((0, 0, math.radians(turn))).to_quaternion()
    out = []
    lim_x, lim_y = ts.L / 2 - ts.T - 0.006, ts.W / 2 - ts.T - 0.006
    for p, q, v in items:
        w = Vector((sx, sy, ts.FLOOR_TOP)) + R @ p
        if (w.x - CUP[0]) ** 2 + (w.y - CUP[1]) ** 2 < 0.081 ** 2 or abs(w.x) > lim_x or abs(w.y) > lim_y:
            continue
        out.append((w, R @ q, v))
    return out


def loose_beans(rnd, meshes):
    """Beans scattered over the tray's left and front, a few in twos and threes, none under the cup."""
    items = []
    sx, sy, turn = SACK
    R = Matrix.Rotation(math.radians(-turn), 3, "Z")
    inner_x, inner_y = ts.L / 2 - ts.T - 0.008, ts.W / 2 - ts.T - 0.008

    def ok(x, y):
        if abs(x) > inner_x or abs(y) > inner_y:
            return False
        if (x - CUP[0]) ** 2 + (y - CUP[1]) ** 2 < 0.083 ** 2:
            return False
        lx, ly, _ = R @ Vector((x - sx, y - sy, 0))
        if lx > XM - 0.02 and abs(ly) < sk.RY + 0.03:
            return False                                    # under the sack
        if heap_h(lx, ly) is not None:
            return False
        return True

    pts = _poisson(rnd, ((-0.27, 0.27, -0.18, 0.18), ok), 0.026, limit=60)
    keep = []
    for x, y in pts:
        # thin them out: more near the spill and the tray's front left, few at the back
        lx, ly, _ = R @ Vector((x - sx, y - sy, 0))
        near = math.exp(-max(0.0, (XM - lx) - 0.10) / 0.06) if abs(ly) < 0.16 else 0.0
        front = 0.55 if (x < -0.02 and y < 0.0) else 0.18
        if rnd.random() < max(near, front):
            keep.append((x, y))
    for x, y in keep:
        items.append(tb.lying(rnd, meshes, x, y, ts.FLOOR_TOP))
        if rnd.random() < 0.22:          # a neighbour touching it
            a = rnd.uniform(0, 2 * math.pi)
            items.append(tb.lying(rnd, meshes, x + 0.0105 * math.cos(a), y + 0.0105 * math.sin(a), ts.FLOOR_TOP))
    return items


def build():
    rnd = random.Random(19)
    mats = dict(walnut=sh.walnut_frame(ts.L, ts.W), floor=sh.walnut_floor(), porcelain=sh.porcelain(),
                cup=sh.porcelain("porcelain cup", stain=LEVEL), crema=sh.crema(ts.cup_inner_r(LEVEL)), steel=sh.steel(),
                bean=sh.bean(), burlap=sh.burlap())
    obs = [ts.frame([mats["walnut"]]), ts.floor_panel([mats["floor"]])]
    obs += cup_set(mats)
    sack_ob, rows = sk.sack([mats["burlap"]])
    sx, sy, turn = SACK
    sack_ob.location = (sx, sy, ts.FLOOR_TOP)
    sack_ob.rotation_euler = (0, 0, math.radians(turn))
    obs.append(sack_ob)
    for f in sk.fibres(rows, sh.jute_fibre()):
        f.parent = sack_ob
        obs.append(f)
    meshes = tb.variants()
    items = to_tray(heap_beans(rnd, meshes)) + loose_beans(rnd, meshes)
    obs += tb.place(meshes, mats["bean"], items)
    return obs
