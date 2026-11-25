# The conga: a 76 cm stave drum with a 29.6 cm rawhide head, 14 staves glued into a barrel and finished in
# amber lacquer, a brass crown rim with six ears, six L-hooks down to brass side plates where nuts under
# the brackets pull the rim down, a blank brass badge and a rubber ring round the foot. Built at real size
# on the floor at z = 0; the camera looks along +y, so the badge faces -y.
import math, random
import bpy, bmesh
from mathutils import Vector, Matrix
from objects import conga_shaders as shaders

H = 0.76                       # overall height, the top of the head
HEAD_Z = 0.7598                # the playing surface
SHELL_TOP = 0.741              # the bearing edge
WALL = 0.009                   # stave thickness
STAVES = 14
STAVE_SEG = 12                 # facets across one stave
STAVE_PHASE = 0.17             # turns the stave seams off the badge's centre line
LUG_DEG = (-60, -120, 0, 180, 60, 120)   # six lugs; -90 faces the camera, where the badge is
LUG_Z = 0.580                  # the middle of the side plates
BADGE_Z = 0.574
ROD_R = 0.0032                 # the hooks are 6.4 mm rods
EAR_Z = 0.6875                 # where a hook enters its rim ear

# Radius at height (r, z), the stand-in's profile: narrow foot, belly widest at 0.38 m, a slight waist
# under the rim.
PROFILE = [(0.118, 0.0), (0.128, 0.06), (0.155, 0.23), (0.168, 0.38), (0.160, 0.53), (0.146, 0.67),
           (0.148, 0.72), (0.1485, SHELL_TOP)]


def _pchip(xs, ys):
    """Monotone cubic interpolation (no overshoot between the profile's points)."""
    n = len(xs)
    h = [xs[i + 1] - xs[i] for i in range(n - 1)]
    d = [(ys[i + 1] - ys[i]) / h[i] for i in range(n - 1)]
    m = [0.0] * n
    m[0], m[-1] = d[0], d[-1]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])

    def f(x):
        x = min(max(x, xs[0]), xs[-1])
        i = max(0, min(n - 2, next((k for k in range(n - 1) if x <= xs[k + 1]), n - 2)))
        t = (x - xs[i]) / h[i]
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h[i] * m[i]
                + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h[i] * m[i + 1])
    return f


_R = _pchip([z for r, z in PROFILE], [r for r, z in PROFILE])


def R(z):
    return _R(z)


def dR(z, e=1e-4):
    return (_R(z + e) - _R(z - e)) / (2 * e)


def surf(phi, z, off=0.0):
    """A point on the shell's outer surface at angle phi and height z, pushed off it along the normal."""
    k = dR(z)
    s = 1 / math.sqrt(1 + k * k)
    r = R(z) + off * s
    return Vector((r * math.cos(phi), r * math.sin(phi), z - off * k * s))


def frame(phi, z):
    """Unit vectors at a point of the shell: t round the drum (left to right seen from outside), m up the
    surface, n outward."""
    k = dR(z)
    n = Vector((math.cos(phi), math.sin(phi), -k)).normalized()
    m = Vector((k * math.cos(phi), k * math.sin(phi), 1)).normalized()
    t = m.cross(n).normalized()
    return t, m, n


def _link(name, me, mats):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    for mt in mats:
        me.materials.append(mt)
    return ob


def _smooth(me):
    for p in me.polygons:
        p.use_smooth = True


def _bevel(ob, width, seg=2, angle=40, harden=False):
    b = ob.modifiers.new("bevel", "BEVEL")
    b.width = width
    b.segments = seg
    b.limit_method = "ANGLE"
    b.angle_limit = math.radians(angle)
    b.harden_normals = harden
    b.miter_outer = "MITER_ARC"
    return b


def _solidify(ob, thick, offset=1.0):
    s = ob.modifiers.new("solidify", "SOLIDIFY")
    s.thickness = thick
    s.offset = offset
    s.use_even_offset = True
    s.use_quality_normals = True
    return s


# ---------- the shell: staves round a barrel, each with its own piece of the oak texture ----------
def shell(mat):
    rnd = random.Random(11)
    n_around = STAVES * STAVE_SEG
    dphi = 2 * math.pi / n_around
    zs = [0.0]
    while zs[-1] < SHELL_TOP - 1e-6:
        z = zs[-1]
        step = 0.0025 if z < 0.03 or z > SHELL_TOP - 0.04 else 0.005
        zs.append(min(SHELL_TOP, z + step))
    TEX = shaders.WOOD_SIZE
    st = [dict(ou=rnd.uniform(0, TEX), ov=rnd.uniform(0, TEX), flip=rnd.choice((-1, 1)), ang=math.radians(rnd.uniform(-1, 1)),
               rand=rnd.random(), rand2=rnd.random()) for _ in range(STAVES)]
    SU, SV = 1.25, 0.5   # the veneer's figure, finer across the grain and drawn out along it, as in rived staves

    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    seam = bm.loops.layers.float.new("seam")
    srand = bm.faces.layers.float.new("stave")
    srand2 = bm.faces.layers.float.new("stave2")

    def ring(rad_fn, z):
        return [bm.verts.new(((rad_fn(z)) * math.cos(STAVE_PHASE + k * dphi),
                              (rad_fn(z)) * math.sin(STAVE_PHASE + k * dphi), z)) for k in range(n_around)]

    outer = [ring(R, z) for z in zs]
    inner = [ring(lambda z: R(z) - WALL, z) for z in zs]

    def corner_data(k, z, stave):
        # local position across the stave (metres from its centre line) and distance to its nearest seam
        local = (k - stave * STAVE_SEG - STAVE_SEG / 2) * dphi
        r = R(z)
        u_m = local * r
        d = (STAVE_SEG / 2 - abs(k - stave * STAVE_SEG - STAVE_SEG / 2)) * dphi * r
        s = st[stave]
        ca, sa = math.cos(s["ang"]), math.sin(s["ang"])      # a little grain run-out, different per stave
        gu, gv = u_m * ca - z * sa, u_m * sa + z * ca
        return ((s["flip"] * gu * SU + s["ou"]) / TEX, (gv * SV + s["ov"]) / TEX), d

    for j in range(len(zs) - 1):
        for k in range(n_around):
            k2 = (k + 1) % n_around
            f = bm.faces.new((outer[j][k], outer[j][k2], outer[j + 1][k2], outer[j + 1][k]))
            stave = k // STAVE_SEG
            f[srand] = st[stave]["rand"]
            f[srand2] = st[stave]["rand2"]
            for loop, (kk, zz) in zip(f.loops, ((k, zs[j]), (k + 1, zs[j]), (k + 1, zs[j + 1]), (k, zs[j + 1]))):
                uv, d = corner_data(kk, zz, stave)
                loop[uvl].uv = uv
                loop[seam] = d
            f.smooth = True
            g = bm.faces.new((inner[j][k], inner[j + 1][k], inner[j + 1][k2], inner[j][k2]))
            g.smooth = True
    for k in range(n_around):
        k2 = (k + 1) % n_around
        bm.faces.new((outer[-1][k], inner[-1][k], inner[-1][k2], outer[-1][k2]))   # top of the staves
        bm.faces.new((outer[0][k], outer[0][k2], inner[0][k2], inner[0][k]))       # foot
    me = bpy.data.meshes.new("conga shell")
    bm.to_mesh(me)
    bm.free()
    return _link("conga shell", me, [mat])


# ---------- a surface of revolution from (r, z) pairs ----------
def lathe(name, prof, seg, mats, closed=False, smooth=True):
    bm = bmesh.new()
    rings = []
    for r, z in prof:
        if r < 1e-7:
            rings.append([bm.verts.new((0, 0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z))
                          for k in range(seg)])
    pairs = list(zip(rings, rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for a, b in pairs:
        for k in range(seg):
            k2 = (k + 1) % seg
            if len(a) == 1:
                f = bm.faces.new((a[0], b[k2], b[k]))
            elif len(b) == 1:
                f = bm.faces.new((a[k], a[k2], b[0]))
            else:
                f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
            f.smooth = smooth
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    return _link(name, me, mats)


def arc(c, rad, a0, a1, n):
    return [(c[0] + rad * math.cos(a0 + (a1 - a0) * i / n), c[1] + rad * math.sin(a0 + (a1 - a0) * i / n))
            for i in range(n + 1)]


# ---------- the head: rawhide over the bearing edge, tucked round the flesh hoop under the rim ----------
def head(mat):
    prof = [(0.0, HEAD_Z + 0.0002)]
    for i in range(1, 25):
        r = 0.1445 * i / 24
        prof.append((r, HEAD_Z + 0.0002 * (1 - (r / 0.1445) ** 2)))
    prof += arc((0.1445, HEAD_Z - 0.0040), 0.0040, math.pi / 2, 0.0, 10)[1:]
    prof += [(0.1484, 0.750), (0.1487, 0.745), (0.1490, 0.740), (0.1497, 0.7355), (0.1512, 0.7315), (0.1535, 0.7285),
             (0.1565, 0.7265)]
    ob = lathe("conga head", prof, 256, [mat])
    _solidify(ob, 0.0015, -1.0)
    return ob


def flesh_hoop(mat):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1545, minor_radius=0.0028, major_segments=128,
                                     minor_segments=12, location=(0, 0, 0.7250))
    ob = bpy.context.active_object
    ob.name = "conga flesh hoop"
    ob.data.materials.append(mat)
    _smooth(ob.data)
    return ob


# ---------- the crown rim: a curled lip over the head, a band, and an ear hanging under each lug ----------
RIM_BAND_R = 0.1638            # the band's mid-surface
RIM_T = 0.0022                 # sheet thickness
EAR_DEPTH, EAR_TIP, EAR_TOP = 0.0305, 0.0058, 0.0195   # ear: depth below the band, half-widths at tip/top


BAND_TOP_Z, BAND_BOT_Z = 0.7325, 0.7100


def band_r(z):
    """The band's mid-surface radius: it carries on from the curl and turns gently in as it goes down
    (2.5 mm by the band's foot), so it shows the light above as well as the floor; the ears keep leaning
    in at the same slope."""
    d = BAND_TOP_Z - z
    db = BAND_TOP_Z - BAND_BOT_Z
    k = 0.0025 / (db * db)
    if d <= db:
        return RIM_BAND_R - k * d * d
    return RIM_BAND_R - k * db * db - 2 * k * db * (d - db)


def rim_bottom(phi):
    """Height of the rim's lower edge at angle phi: the band, dropping into a rounded V under each lug
    (flat-bottomed tip, sides and shoulder fillets from one smootherstep)."""
    d = min(abs((phi - math.radians(a) + math.pi) % (2 * math.pi) - math.pi) for a in LUG_DEG) * RIM_BAND_R
    if d <= EAR_TIP:
        f = 1.0
    elif d >= EAR_TOP:
        f = 0.0
    else:
        t = (d - EAR_TIP) / (EAR_TOP - EAR_TIP)
        f = 1 - t * t * t * (t * (6 * t - 15) + 10)
    return BAND_BOT_Z - EAR_DEPTH * f


def rim(mat):
    curl = arc((0.1580, BAND_TOP_Z), 0.0058, math.radians(200), 0.0, 14)   # inner lip, over the top, to the band
    band_top = curl[-1]
    seg = 1440
    rows_band = 10
    bm = bmesh.new()
    grid = []
    for k in range(seg):
        phi = 2 * math.pi * k / seg
        c, s = math.cos(phi), math.sin(phi)
        zb = rim_bottom(phi)
        col = [(r, z) for r, z in curl]
        for i in range(1, rows_band + 1):
            t = i / rows_band
            z = band_top[1] + (zb - band_top[1]) * t
            col.append((band_r(z), z))
        grid.append([bm.verts.new((r * c, r * s, z)) for r, z in col])
    rows = len(grid[0])
    for k in range(seg):
        a, b = grid[k], grid[(k + 1) % seg]
        for i in range(rows - 1):
            f = bm.faces.new((a[i], a[i + 1], b[i + 1], b[i]))
            f.smooth = True
    bm.normal_update()
    # outward normals on the band
    test = [f for f in bm.faces if f.calc_center_median().z < 0.72][0]
    if test.normal.dot(Vector((test.calc_center_median().x, test.calc_center_median().y, 0))) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new("conga rim")
    bm.to_mesh(me)
    bm.free()
    ob = _link("conga rim", me, [mat])
    _solidify(ob, RIM_T, 0.0)
    _bevel(ob, 0.0007, 3, 50)
    return ob


# ---------- a tube along a polyline (the hooks) ----------
def tube(name, pts, rad, mats, seg=20):
    bm = bmesh.new()
    pts = [Vector(p) for p in pts]
    tans = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tans.append((b - a).normalized())
    up = Vector((0, 0, 1)) if abs(tans[0].z) < 0.9 else Vector((1, 0, 0))
    nrm = tans[0].cross(up).normalized()
    rings, frames = [], []
    for i, p in enumerate(pts):
        if i > 0:
            # parallel transport
            axis = tans[i - 1].cross(tans[i])
            if axis.length > 1e-9:
                ang = tans[i - 1].angle(tans[i])
                nrm = Matrix.Rotation(ang, 3, axis.normalized()) @ nrm
        bin_ = tans[i].cross(nrm).normalized()
        frames.append((nrm.copy(), bin_))
        rings.append([bm.verts.new(p + rad * (math.cos(2 * math.pi * k / seg) * nrm + math.sin(2 * math.pi * k / seg) * bin_))
                      for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((a[k], a[k2], b[k2], b[k]))
            f.smooth = True
    # caps: a small chamfer ring, then a flat end
    for end, sign in ((0, -1), (len(pts) - 1, 1)):
        p, t = pts[end], tans[end] * sign
        n2, b2 = frames[end]
        ring = rings[end]
        ch = [bm.verts.new(p + t * rad * 0.18 + rad * 0.78 * (math.cos(2 * math.pi * k / seg) * n2 +
                                                                math.sin(2 * math.pi * k / seg) * b2))
              for k in range(seg)]
        cv = bm.verts.new(p + t * rad * 0.18)
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((ring[k], ring[k2], ch[k2], ch[k]))
            f.smooth = True
            bm.faces.new((ch[k], ch[k2], cv))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return _link(name, me, mats)


# ---------- a plate conformed to the shell (side plates, the badge) ----------
def conformed_plate(name, phi0, z0, half_w, b0, b1, thick, mats, rows=40, cols=16, lift=0.0002, uv=True):
    """A plate lying on the shell, centred at angle phi0 and height z0. half_w(b) gives its half width at
    b metres up the surface from the centre; it spans b0..b1. Solidified outward by thick."""
    t0, m0, n0 = frame(phi0, z0)
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap") if uv else None
    grid = []
    for i in range(rows + 1):
        b = b0 + (b1 - b0) * i / rows
        w = max(half_w(b), 1e-5)
        row = []
        for j in range(cols + 1):
            a = -w + 2 * w * j / cols
            z = z0 + b * m0.z
            phi = phi0 + a / R(z)
            row.append((bm.verts.new(surf(phi, z, lift)), a, b))
        grid.append(row)
    for i in range(rows):
        for j in range(cols):
            vs = (grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j])
            f = bm.faces.new([v[0] for v in vs])
            f.smooth = True
            if uv:
                for loop, v in zip(f.loops, vs):
                    loop[uvl].uv = (v[1], v[2])
    bm.normal_update()
    bm.faces.ensure_lookup_table()
    c = bm.faces[0]
    if c.normal.dot(n0) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = _link(name, me, mats)
    _solidify(ob, thick, 1.0)
    return ob


LUG_K = 1.15       # the lug hardware's scale: side plates 5.2 x 9 cm


def shield(b):
    """Half width of a side plate: square shoulders with rounded corners, tapering to a rounded point."""
    K = LUG_K
    W, top, rc, waist, tip = 0.0225 * K, 0.036 * K, 0.005 * K, -0.010 * K, -0.042 * K
    if b > top - rc:
        y = b - (top - rc)
        return W - rc + math.sqrt(max(rc * rc - y * y, 0.0))
    if b >= waist:
        return W
    t = (waist - b) / (waist - tip)
    w = W * (1 - t) + 0.0035 * K * t
    if t > 0.85:   # round the point
        u = (t - 0.85) / 0.15
        w *= math.sqrt(max(1 - u * u, 0.0)) * 0.6 + 0.4 * (1 - u)
    return w


def rounded_rect(W, Hh, rc):
    def f(b):
        if abs(b) > Hh - rc:
            y = abs(b) - (Hh - rc)
            return W - rc + math.sqrt(max(rc * rc - y * y, 0.0))
        return W
    return f


# ---------- small hardware in a lug's frame ----------
def _xf(phi, z, off):
    t, m, n = frame(phi, z)
    o = surf(phi, z, off)
    M = Matrix((t, m, n)).transposed().to_4x4()
    M.translation = o
    return M


def block(name, M, lo, hi, mats, bev=0.0015, seg=3):
    """An axis-aligned box in a lug's frame (t, m, n), from corner lo to corner hi."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    s = [hi[i] - lo[i] for i in range(3)]
    for v in bm.verts:
        v.co = M @ Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = _link(name, me, mats)
    _smooth(me)
    _bevel(ob, bev, seg, 30, harden=True)
    return ob


def prism(name, M, centre, axis_len, radius, sides, mats, bev=0.0006, seg=2, rot=0.0):
    """A prism (hex nut, washer) along the frame's m axis."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=sides, radius1=radius, radius2=radius, depth=axis_len)
    R0 = Matrix.Rotation(rot, 4, "Z")
    to_m = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))   # z -> m
    for v in bm.verts:
        v.co = M @ (Matrix.Translation(Vector(centre)) @ to_m @ R0 @ v.co)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = _link(name, me, mats)
    _smooth(me)
    _bevel(ob, bev, seg, 30, harden=True)
    return ob


def dome(name, M, centre, radius, height, mats, slot=None):
    """A domed screw or rivet head lying on the surface (local n is up)."""
    prof = [(radius, 0.0)]
    for i in range(1, 9):
        a = math.pi / 2 * i / 8
        prof.append((radius * math.cos(a), height * math.sin(a)))
    prof[-1] = (0.0, height)
    prof = [(radius * 0.92, -0.0006)] + prof
    bm = bmesh.new()
    seg = 24
    rings = []
    for r, h in prof:
        if r < 1e-7:
            rings.append([bm.verts.new((0, 0, h))])
        else:
            rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), h))
                          for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            k2 = (k + 1) % seg
            f = bm.faces.new((a[k], a[k2], b[0]) if len(b) == 1 else (a[k], a[k2], b[k2], b[k]))
            f.smooth = True
    bm.faces.new(rings[0][::-1])
    if slot:
        # a screwdriver slot: push the dome's middle strip down
        for v in bm.verts:
            if abs(v.co.y) < radius * 0.14 and v.co.z > height * 0.35:
                v.co.z = height * 0.35
    for v in bm.verts:
        v.co = M @ Vector((centre[0] + v.co.x, centre[1] + v.co.y, centre[2] + v.co.z))
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    return _link(name, me, mats)


# ---------- one lug: side plate, bracket, hook, washer and nut ----------
D_AX = 0.0130      # the hook's axis, off the shell's surface


def lug(phi, M_brass, M_plate, M_rod, M_rim):
    obs = []
    z0 = LUG_Z
    K = LUG_K
    obs.append(conformed_plate("conga side plate", phi, z0, shield, -0.042 * K, 0.036 * K, 0.0028, [M_plate], rows=56, cols=16))
    _bevel(obs[-1], 0.0009, 3, 35, harden=True)
    M = _xf(phi, z0, 0.0)
    P = 0.0028                                   # plate thickness: the bracket stands on it
    obs.append(block("conga lug guide", M, (-0.0090 * K, 0.0165 * K, P - 0.0005), (0.0090 * K, 0.0280 * K, D_AX + 0.0062),
                     [M_brass], 0.0036, 5))
    obs.append(block("conga lug spine", M, (-0.0062 * K, -0.0150 * K, P - 0.0005), (0.0062 * K, 0.0270 * K, P + 0.0034),
                     [M_brass], 0.0016, 3))
    obs.append(block("conga lug shelf", M, (-0.0100 * K, -0.0165 * K, P - 0.0005), (0.0100 * K, -0.0040 * K, D_AX + 0.0068),
                     [M_brass], 0.0040, 5))
    yb = -0.0165 * K
    obs.append(prism("conga washer", M, (0.0, yb - 0.00075, D_AX), 0.0015, 0.0078, 32, [M_brass], 0.0004, 2))
    obs.append(prism("conga nut", M, (0.0, yb - 0.0015 - 0.0050, D_AX), 0.0100, 0.0060 / math.cos(math.pi / 6), 6, [M_brass],
                     0.0008, 2, rot=math.radians(30)))
    for a, b in ((-0.0165, 0.0305), (0.0165, 0.0305), (-0.0172, -0.0082), (0.0172, -0.0082)):
        a, b = a * K, b * K
        z = z0 + b * frame(phi, z0)[1].z
        Ms = _xf(phi + a / R(z), z, P)
        obs.append(dome("conga screw", Ms, (0, 0, 0), 0.0032, 0.0015, [M_brass], slot=True))

    # the hook: into the rim ear, a bend, down an S onto the bracket's axis, through it, out under the nut
    t, m, n = frame(phi, z0)
    axis_o = surf(phi, z0, 0.0) + n * D_AX
    radial = Vector((math.cos(phi), math.sin(phi), 0))
    r_top = band_r(EAR_Z) + RIM_T / 2 + ROD_R + 0.0003
    pts = []
    # horizontal leg from inside the ear out to the bend
    br = 0.0042
    r_in = band_r(EAR_Z) - 0.0035
    for i in range(5):
        r = r_in + (r_top - br - r_in) * i / 4
        pts.append(radial * r + Vector((0, 0, EAR_Z)))
    for i in range(1, 9):
        a = math.pi / 2 * i / 8
        r = r_top - br + br * math.sin(a)
        z = EAR_Z - br + br * math.cos(a)
        pts.append(radial * r + Vector((0, 0, z)))
    # S down to the bracket's axis line, joining it above the guide
    p0 = radial * r_top + Vector((0, 0, EAR_Z - br))
    s_join = 0.0330 * K
    p1 = axis_o + m * s_join
    t0 = Vector((0, 0, -1)) * 0.045
    t1 = -m * 0.045
    for i in range(1, 21):
        s = i / 20
        h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
        pts.append(p0 * h00 + t0 * h10 + p1 * h01 + t1 * h11)
    s_end = yb - 0.0015 - 0.0100 - 0.0055       # 5.5 mm of thread below the nut
    for i in range(1, 13):
        s = s_join + (s_end - s_join) * i / 12
        pts.append(axis_o + m * s)
    obs.append(tube("conga hook", pts, ROD_R, [M_rod]))
    # the hole in the ear the hook passes through: a rolled lip round the rod
    face = band_r(EAR_Z) + RIM_T / 2
    bpy.ops.mesh.primitive_torus_add(major_radius=ROD_R + 0.0009, minor_radius=0.00075, major_segments=32, minor_segments=8,
                                     location=radial * (face - 0.0002) + Vector((0, 0, EAR_Z)),
                                     rotation=(0.0, math.pi / 2, phi))
    lip = bpy.context.active_object
    lip.name = "conga ear hole"
    lip.data.materials.append(M_rim)
    _smooth(lip.data)
    obs.append(lip)
    return obs


def badge(mat):
    ob = conformed_plate("conga badge", math.radians(-90), BADGE_Z, rounded_rect(0.0195, 0.0265, 0.004),
                         -0.0265, 0.0265, 0.0011, [mat], rows=40, cols=24)
    _bevel(ob, 0.00045, 2, 35, harden=True)
    obs = [ob]
    for a, b in ((-0.0145, 0.0215), (0.0145, 0.0215), (-0.0145, -0.0215), (0.0145, -0.0215)):
        z = BADGE_Z + b
        phi = math.radians(-90) + a / R(z)
        obs.append(dome("conga rivet", _xf(phi, z, 0.0011), (0, 0, 0), 0.0015, 0.0008, [mat]))
    return obs


# ---------- the foot: a rubber ring over the bottom edge ----------
def foot(mat):
    h, lip = 0.0165, 0.0030
    prof = []
    # outside, from the top edge (tucked against the shell) down, round the corner, under, and up inside
    prof += [(R(h + 0.0012) + 0.0002, h + 0.0012)]
    prof += arc((R(h) + lip - 0.0012, h - 0.0010), 0.0012, math.radians(100), 0.0, 4)
    prof += [(R(0.008) + lip, 0.008)]
    prof += arc((R(0.0) + lip - 0.0032, 0.0035), 0.0032, 0.0, -math.pi / 2, 6)
    prof += [(R(0.0) - WALL - 0.0025, 0.0003), (R(0.0) - WALL - 0.0030, 0.0040), (R(0.012) - WALL - 0.0005, 0.0120)]
    return lathe("conga foot", prof, 192, [mat], closed=True)


def build():
    mats = shaders.make()
    obs = [shell(mats["wood"]), head(mats["hide"]), flesh_hoop(mats["steel"]), rim(mats["rim"]), foot(mats["rubber"])]
    for a in LUG_DEG:
        obs += lug(math.radians(a), mats["brass"], mats["plate"], mats["rod"], mats["rim"])
    obs += badge(mats["badge"])
    return obs
