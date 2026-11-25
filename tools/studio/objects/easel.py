# The easel: a beech A-frame studio easel, 1.75 m to the top of its mast, oiled, every edge softly
# rounded. Two splayed front legs bolted either side of a central mast at their apex, a lower crossbar,
# a back leg on a brass hinge with a slotted stay and a wing nut, a canvas ledge (top board with a lip,
# a shallow drawer with a brass knob between end cheeks, a deeper tray below) on a collar that rides a
# brass rack set into the mast and locks with a knurled knob, and a sliding top clamp with a black star
# knob. On it, a blank 87.4 x 88 cm canvas primed with gesso, gallery-wrapped on 3.5 cm stretchers.
#
# The legs, mast, ledge, clamp and canvas share one plane tilted back TILT radians (the "frame": u
# across, w into the picture, v up its face); the frame's front face (w = 0) meets the floor at y = Y0.
# canvas_front is the painted face alone, its UVs 0..1 over it (u left to right, v bottom to top), so a
# painting can be swapped in as an image: EASEL_PAINTING=/path/to/image.png, or gesso(name, painting).
import math, os
import bmesh
from mathutils import Matrix, Vector
from objects.desk_kit import rrect, prism, loft
from objects.easel_kit import (frame, revolve, box_bm, to_object, wood_part, link_copy, dome_screw,
                               countersunk, wing_nut, oiled_wood, gesso, raw_canvas, metal, phenolic, orient)

TILT = 0.10                     # the whole front assembly leans back 5.7 degrees
Y0 = -0.075                     # where the front plane (w = 0) meets the floor
FRAME = Matrix.Translation((0, Y0, 0)) @ Matrix.Rotation(-TILT, 4, "X")

H = 1.755                       # top of the mast, along the frame (1.746 m above the floor)
LEG_W, LEG_D = 0.044, 0.028     # front legs: face width, depth
FOOT_U, APEX_U, APEX_V = 0.300, 0.046, 1.47   # front leg centres at the floor and at their top
MAST_W, MAST_D = 0.046, 0.032
BACK_W, BACK_D = 0.040, 0.026   # back leg
BACK_FOOT_Y = 0.700             # the back leg's front face meets the floor here (y)
HINGE_V = 1.405                 # where the back leg meets the mast's back face
CROSS_V = (0.205, 0.250)        # lower crossbar
COLLAR_V = (0.483, 0.525)
LEDGE_V = 0.655                 # top of the ledge's top board: the canvas stands on it
CW, CH, CD = 0.874, 0.880, 0.035
CANVAS_W = -0.0360              # the canvas's front face (w)
CLAMP_V = LEDGE_V + 0.0005 + CH  # underside of the top clamp's bar, on the canvas's top edge
FABRIC = 0.0006


def F(u, w, v):
    return FRAME @ Vector((u, w, v))


def FD(du, dw, dv):
    return FRAME.to_3x3() @ Vector((du, dw, dv))


def in_frame(origin, ez, ex):
    """A part's matrix (to easel space) from an origin and axes given in the frame."""
    return FRAME @ frame(origin, ez, ex)


POST = (Vector((0, 0, 1)), Vector((1, 0, 0)))      # grain up the frame: part x = u, y = w, z = v
BOARD = (Vector((1, 0, 0)), Vector((0, 1, 0)))     # grain across: part x = w, y = v, z = u


def post(name, mat, u0, u1, w0, w1, v0, v1, holes=(), bevel=0.0028, **kw):
    return wood_part(name, box_bm(u0, u1, w0, w1, v0, v1), in_frame((0, 0, 0), *POST), mat, bevel=bevel,
                     holes=holes, **kw)


def board(name, mat, u0, u1, w0, w1, v0, v1, holes=(), bevel=0.0028, **kw):
    return wood_part(name, box_bm(w0, w1, v0, v1, u0, u1), in_frame((0, 0, 0), *BOARD), mat, bevel=bevel,
                     holes=holes, **kw)


def leg_axes(s):
    foot = Vector((s * FOOT_U, 0.0, 0.0))
    top = Vector((s * APEX_U, 0.0, APEX_V))
    d = (top - foot).normalized()
    ex = Vector((d.z, 0.0, -d.x))
    return foot, d, ex


def front_leg(s, mat):
    foot, d, ex = leg_axes(s)
    length = (Vector((s * APEX_U, 0, APEX_V)) - foot).length
    bm = box_bm(-LEG_W / 2, LEG_W / 2, 0.0, LEG_D, -0.10, length + 0.10)
    planes = [((0, 0, 0), (0, 0, -1)), (F(0, 0, APEX_V), FD(0, 0, 1))]
    return wood_part(f"easel leg {'right' if s > 0 else 'left'}", bm, in_frame(foot, d, ex), mat, planes=planes)


def leg_outer_plane(s):
    """The outer face of a front leg, as a plane in easel space (for cutting the crossbar flush)."""
    foot, d, ex = leg_axes(s)
    n = ex * s
    return F(*(foot + n * (LEG_W / 2))), FD(*n)


def mast(mat):
    groove = box_bm(-0.0075, 0.0075, -0.01, 0.0065, CROSS_V[1] + 0.012, 1.20)
    return post("easel mast", mat, -MAST_W / 2, MAST_W / 2, 0.0, MAST_D, CROSS_V[0], H, holes=[groove])


def rack(mat):
    """The brass rack in the mast's groove: plain saw teeth, a ramp up and a square drop for the
    collar's pawl to catch."""
    z0, z1, p = CROSS_V[1] + 0.014, 1.19, 0.014
    crest, root, back = 0.0024, 0.0044, 0.0064
    k = int((z1 - z0) / p)
    pts = [(back, z0), (back, z0 + k * p), (root, z0 + k * p)]
    for i in range(k - 1, -1, -1):
        zk = z0 + i * p
        pts += [(crest, zk + 0.97 * p), (crest, zk + 0.90 * p), (root, zk + 0.04 * p)]
    pts.append((root, z0))
    # prism along x: points are (y, z)
    bm = prism(pts, -0.0065, 0.0065, "x")
    return to_object("easel rack", bm, [mat], FRAME, bevel=0.0002, segs=2, sharp=40)


def crossbar(mat):
    planes = [leg_outer_plane(1), leg_outer_plane(-1)]
    return board("easel crossbar", mat, -0.42, 0.42, -0.022, 0.0, CROSS_V[0], CROSS_V[1], planes=planes)


def sleeve_hole():
    return box_bm(-MAST_W / 2 - 0.0006, MAST_W / 2 + 0.0006, -0.0006, MAST_D + 0.0006, -1.0, 3.0)


def ledge(mat):
    obs = []
    v0 = COLLAR_V[1]
    obs.append(post("easel collar", mat, -0.062, 0.062, -0.024, 0.046, COLLAR_V[0], v0, holes=[sleeve_hole()],
                    bevel=0.0024))
    obs.append(board("easel ledge tray", mat, -0.400, 0.400, -0.100, 0.0, v0, v0 + 0.018))
    obs.append(board("easel ledge tray lip", mat, -0.400, 0.400, -0.100, -0.087, v0 + 0.018, v0 + 0.032, bevel=0.0022))
    top0 = LEDGE_V - 0.018
    for s in (-1, 1):
        obs.append(post(f"easel ledge cheek {s}", mat, *sorted((s * 0.370, s * 0.392)), -0.062, 0.0, v0 + 0.018, top0,
                        bevel=0.0022))
    obs.append(board("easel drawer", mat, -0.366, 0.366, -0.0445, -0.010, v0 + 0.0195, top0 - 0.0015, bevel=0.001))
    obs.append(board("easel ledge back", mat, -0.370, 0.370, -0.010, 0.0, v0 + 0.018, top0, bevel=0.0015))
    obs.append(board("easel drawer front", mat, -0.3675, 0.3675, -0.0585, -0.0445, v0 + 0.0205, top0 - 0.0018,
                     bevel=0.0018))
    obs.append(board("easel ledge top", mat, -0.410, 0.410, -0.064, 0.0, top0, LEDGE_V))
    obs.append(board("easel ledge lip", mat, -0.410, 0.410, -0.064, -0.053, LEDGE_V, LEDGE_V + 0.009, bevel=0.002))
    return obs


def clamp(mat):
    obs = []
    hole_post = sleeve_hole()
    obs.append(post("easel clamp", mat, -0.038, 0.038, -0.022, 0.046, CLAMP_V + 0.0255, CLAMP_V + 0.112,
                    holes=[hole_post], bevel=0.0024))
    # the bar that bears on the canvas's top edge, its lip hooked down over the front
    hb = box_bm(-0.0006, MAST_D + 0.0006, -1.0, 3.0, -MAST_W / 2 - 0.0006, MAST_W / 2 + 0.0006)
    obs.append(board("easel clamp bar", mat, -0.085, 0.085, -0.052, 0.046, CLAMP_V, CLAMP_V + 0.0255, holes=[hb]))
    obs.append(board("easel clamp lip", mat, -0.085, 0.085, -0.052, CANVAS_W - 0.0028, CLAMP_V - 0.019, CLAMP_V,
                     bevel=0.0022))
    return obs


def back_leg_geometry():
    """The back leg's frame (easel space) and the corner where its back face meets the mast's back face."""
    pf = Vector((0.0, BACK_FOOT_Y, 0.0))
    hc = F(0, MAST_D, HINGE_V)
    d = (hc - pf).normalized()
    m = frame(pf, d, (1, 0, 0))
    ey = m.to_3x3() @ Vector((0, 1, 0))
    n = FD(0, 1, 0)
    c = F(0, MAST_D, 0)
    p0 = pf + ey * BACK_D
    t = n.dot(c - p0) / n.dot(d)
    return m, d, ey, p0 + d * t, (hc - pf).length


def back_leg(mat):
    m, d, ey, pb, length = back_leg_geometry()
    bm = box_bm(-BACK_W / 2, BACK_W / 2, 0.0, BACK_D, -0.10, length + 0.12)
    planes = [((0, 0, 0), (0, 0, -1)), (F(0, MAST_D, 0), FD(0, -1, 0))]
    return wood_part("easel back leg", bm, m, mat, planes=planes)


def hinge(brass):
    """A brass butt hinge across the joint: one leaf on the mast's back, one on the leg's, the knuckles
    in the corner between them."""
    m, d, ey, pb, _ = back_leg_geometry()
    n_mast = FD(0, 1, 0)
    up = FD(0, 0, 1)
    r = 0.0036
    bis = (n_mast + ey).normalized()
    centre = pb + bis * (r * 1.05)
    obs = []
    # knuckles: five, alternating leaves, with hairline gaps
    L, k = 0.036, 5
    seg = L / k
    for i in range(k):
        x0 = -L / 2 + i * seg + 0.0002
        x1 = -L / 2 + (i + 1) * seg - 0.0002
        bm = revolve([(0.0, x1), (r * 0.92, x1), (r, x1 - 0.0003), (r, x0 + 0.0003), (r * 0.92, x0), (0.0, x0)], 24)
        obs.append(to_object(f"easel hinge knuckle {i}", bm, [brass], frame(centre, (1, 0, 0), (0, 0, 1)), sharp=50))
    # leaves
    o_a = centre - n_mast * n_mast.dot(centre - F(0, MAST_D, 0))
    la = to_object("easel hinge leaf mast", box_bm(-L / 2, L / 2, 0.0, 0.0014, 0.0, 0.034), [brass],
                   frame(o_a, up, (1, 0, 0)), bevel=0.0006, segs=2)
    o_b = centre - ey * ey.dot(centre - pb)
    lb = to_object("easel hinge leaf leg", box_bm(-L / 2, L / 2, -0.0014, 0.0, 0.0, 0.034), [brass],
                   frame(o_b, -d, (1, 0, 0)), bevel=0.0006, segs=2)
    obs += [la, lb]
    screw = countersunk("easel hinge screw", brass, 0.0032)
    first = True
    for leaf, nrm, along in ((o_a, n_mast, up), (o_b, ey, -d)):
        for sx in (-1, 1):
            p = leaf + Vector((sx * 0.010, 0, 0)) + along * 0.023 + nrm * 0.0014
            mtx = frame(p, nrm, (1, 0, 0)) @ Matrix.Rotation(0.6 * sx, 4, "Z")
            if first:
                screw.matrix_world = mtx
                first = False
            else:
                obs.append(link_copy(screw, mtx))
    obs.append(screw)
    return obs


def stay(mat, brass, zinc):
    """A flat stay from a pivot bolt through the mast to the back leg, slotted at that end, held by a
    wing nut: it sets how far the back leg stands out."""
    zs = 0.42
    m, d, ey, pb, _ = back_leg_geometry()
    pf = Vector((0.0, BACK_FOOT_Y, 0.0))
    c = pf + ey * (BACK_D / 2)
    t = (zs - c.z) / d.z
    y_leg = (c + d * t).y
    vm = (zs + MAST_D / 2 * math.sin(TILT)) / math.cos(TILT)
    y_mast = F(0, MAST_D / 2, vm).y
    x0, x1 = 0.0235, 0.0355
    sm = frame((0, 0, zs), (0, 1, 0), (1, 0, 0))     # part z along +y, x along x, y = -z
    bm = box_bm(x0, x1, -0.015, 0.015, y_mast - 0.022, y_leg + 0.040)
    slot = prism(rrect(0.0068, 0.050, 0.0034, 8, 0.0, y_leg - 0.004), x0 - 0.01, x1 + 0.01, "x")
    obs = [wood_part("easel stay", bm, sm, mat, holes=[slot], bevel=0.0022)]
    # pivot bolt at the mast: a dome head on the stay, a nut on the far side of the mast
    head = dome_screw("easel stay bolt", zinc, r=0.0062, h=0.0034, slot=False)
    head.matrix_world = frame((x1, y_mast, zs), (1, 0, 0), (0, 1, 0))
    obs.append(head)
    nut = to_object("easel stay nut", prism([(0.0055 * math.cos(a), 0.0055 * math.sin(a)) for a in
                                             [math.pi / 3 * k + math.pi / 6 for k in range(6)]], 0.0, 0.0045, "z"),
                    [zinc], frame((-MAST_W / 2, y_mast, zs), (-1, 0, 0), (0, 1, 0)), bevel=0.0005, segs=2)
    obs.append(nut)
    # at the leg: a washer and a brass wing nut on the bolt through the slot
    washer = to_object("easel stay washer", revolve([(0.0, 0.0012), (0.0095, 0.0012), (0.0095, 0.0), (0.0, 0.0)], 32),
                       [zinc], frame((x1, y_leg, zs), (1, 0, 0), (0, 0, 1)), bevel=0.0003, segs=1)
    wn = wing_nut("easel stay wing nut", brass)
    wn.matrix_world = frame((x1 + 0.0012, y_leg, zs), (1, 0, 0), (0, 0.25, 1))
    # a spacer between the stay and the leg's side
    spacer = to_object("easel stay spacer", revolve([(0.0, x0), (0.0075, x0), (0.0075, BACK_W / 2), (0.0, BACK_W / 2)], 24),
                       [zinc], Matrix.Translation((0, y_leg, zs)) @ Matrix.Rotation(math.pi / 2, 4, "Y"), sharp=50)
    return obs + [washer, wn, spacer]


def apex_bolt(zinc, brass):
    """The carriage bolt through both front legs and the mast where they meet: a domed head on the left,
    a washer and wing nut on the right."""
    obs = []
    v, w = 1.425, LEG_D / 2
    for s in (-1, 1):
        foot, d, ex = leg_axes(s)
        t = v / d.z
        cpt = foot + d * t + Vector((0, w, 0))
        n = ex * s
        p = F(*(cpt + n * (LEG_W / 2)))
        nn = FD(*n)
        if s < 0:
            h = dome_screw("easel apex bolt", zinc, r=0.0085, h=0.0042, slot=False)
            h.matrix_world = frame(p, nn, FD(0, 0, 1))
            obs.append(h)
        else:
            wsh = to_object("easel apex washer", revolve([(0.0, 0.0014), (0.012, 0.0014), (0.012, 0.0), (0.0, 0.0)], 32),
                            [zinc], frame(p, nn, FD(0, 0, 1)), bevel=0.0003, segs=1)
            wn = wing_nut("easel apex wing nut", brass, hub_r=0.0065, hub_h=0.008, span=0.042, wing_h=0.016)
            wn.matrix_world = frame(p + nn * 0.0014, nn, FD(0, 0, 1))
            obs += [wsh, wn]
    return obs


def screws(brass):
    """Round-head brass screws: the crossbar into the mast and into each leg."""
    base = dome_screw("easel screw", brass, r=0.0042, h=0.0019)
    vc = sum(CROSS_V) / 2
    pts = [(0.0, vc)]
    for s in (-1, 1):
        foot, d, ex = leg_axes(s)
        uc = foot.x + d.x * (vc / d.z)
        pts += [(uc, vc + 0.011), (uc, vc - 0.011)]
    obs = [base]
    for k, (u, v) in enumerate(pts):
        mtx = frame(F(u, -0.022, v), FD(0, -1, 0), FD(1, 0, 0)) @ Matrix.Rotation(0.4 + k * 1.1, 4, "Z")
        if k == 0:
            base.matrix_world = mtx
        else:
            obs.append(link_copy(base, mtx))
    return obs


def knobs(brass, knurled, black, zinc):
    obs = []
    out_ = FD(0, -1, 0)
    # the drawer's brass mushroom knob
    prof = [(0.0, 0.0165), (0.0042, 0.0162), (0.0068, 0.0150), (0.0080, 0.0126), (0.0078, 0.0102), (0.0060, 0.0086),
            (0.0037, 0.0072), (0.0033, 0.0040), (0.0044, 0.0021), (0.0060, 0.0008), (0.0062, 0.0), (0.0, 0.0)]
    obs.append(to_object("easel drawer knob", revolve(prof, 48), [brass],
                         frame(F(0, -0.0585, (COLLAR_V[1] + 0.0205 + LEDGE_V - 0.0198) / 2), out_, FD(1, 0, 0)), sharp=60))
    # the collar: a brass plate, the knurled knob that locks it to the mast, and the pawl in the rack
    vc = sum(COLLAR_V) / 2
    plate = to_object("easel collar plate", prism(rrect(0.052, 0.030, 0.003, 4), 0.0, 0.0012, "z"), [brass],
                      frame(F(0, -0.024, vc), out_, FD(1, 0, 0)), bevel=0.0004, segs=2)
    obs.append(plate)
    cs = countersunk("easel plate screw", brass, 0.0028)
    cs.matrix_world = frame(F(-0.019, -0.0252, vc), out_, FD(1, 0, 0)) @ Matrix.Rotation(0.3, 4, "Z")
    obs += [cs, link_copy(cs, frame(F(0.019, -0.0252, vc), out_, FD(1, 0, 0)) @ Matrix.Rotation(1.4, 4, "Z"))]
    kprof = [(0.0, 0.0115), (0.0080, 0.0115), (0.0096, 0.0105), (0.0100, 0.0090), (0.0100, 0.0058), (0.0094, 0.0050),
             (0.0048, 0.0046), (0.0042, 0.0012), (0.0058, 0.0), (0.0, 0.0)]
    obs.append(to_object("easel collar knob", revolve(kprof, 64), [knurled],
                         frame(F(0, -0.0252, vc), out_, FD(1, 0, 0)), sharp=50))
    pawl = [(-0.0025, COLLAR_V[0] + 0.006), (0.0016, COLLAR_V[0] + 0.006), (0.0016, COLLAR_V[0] - 0.012),
            (0.0006, COLLAR_V[0] - 0.016), (-0.0025, COLLAR_V[0] - 0.014)]
    obs.append(to_object("easel pawl", prism(pawl, -0.0055, 0.0055, "x"), [brass], FRAME, bevel=0.0004, segs=2))
    # the top clamp's black star knob on a steel washer
    vk = CLAMP_V + 0.0255 + (0.112 - 0.0255) / 2
    p = F(0, -0.022, vk)
    obs.append(to_object("easel clamp washer", revolve([(0.0, 0.0012), (0.0095, 0.0012), (0.0095, 0.0), (0.0, 0.0)], 32),
                         [zinc], frame(p, out_, FD(1, 0, 0)), bevel=0.0003, segs=1))
    obs.append(star_knob(black, frame(p + out_ * 0.0012, out_, FD(1, 0, 0))))
    return obs


def star_knob(mat, mtx):
    """A five-lobed moulded knob, 32 mm across, on a round hub."""
    n = 120

    def star(R, z):
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n
            r = R * (0.78 + 0.22 * (0.5 + 0.5 * math.cos(5 * a)) ** 0.7)
            pts.append((r * math.cos(a), r * math.sin(a)))
        return pts, z

    secs = [star(0.0076, 0.0), star(0.0078, 0.0030), star(0.0140, 0.0042), star(0.0158, 0.0052), star(0.0160, 0.0068),
            star(0.0160, 0.0118), star(0.0155, 0.0134), star(0.0142, 0.0146), star(0.0118, 0.0155), star(0.0080, 0.0160)]
    bm = loft(secs, "z")
    return to_object("easel clamp knob", bm, [mat], mtx, sharp=70)


# ---------------------------------------------------------------- the canvas

def _sweep(path, profile):
    """A surface swept round a closed outline (u, v points with outward normals) by a profile of
    (inset, w) points; returns a bmesh in frame coordinates."""
    bm = bmesh.new()
    rings = []
    for (pu, pv), (nu, nv) in path:
        rings.append([bm.verts.new((pu - nu * d, w, pv - nv * d)) for d, w in profile])
    n = len(rings)
    for i in range(n):
        a, b = rings[i], rings[(i + 1) % n]
        for k in range(len(profile) - 1):
            bm.faces.new((a[k], b[k], b[k + 1], a[k + 1]))
    return bm


def _outline(w, h, rc, cv, seg=8):
    """Points round a rounded rectangle (centre (0, cv)) with their outward normals, counter-clockwise."""
    out = []
    for sx, sy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox, oy = sx * (w / 2 - rc), cv + sy * (h / 2 - rc)
        for k in range(seg + 1):
            a = math.radians(a0 + 90 * k / seg)
            out.append(((ox + rc * math.cos(a), oy + rc * math.sin(a)), (math.cos(a), math.sin(a))))
    return out


def canvas(gesso_front, gesso_wrap, raw, pine, steel):
    obs = []
    v0 = LEDGE_V + 0.0005
    cv = v0 + CH / 2
    wf, wb = CANVAS_W, CANVAS_W + CD
    r, r2, rc = 0.0030, 0.0022, 0.0040
    # the face: a flat rounded rectangle, the start of the roundover all round it
    fw, fh = CW - 2 * r, CH - 2 * r
    pts = rrect(fw, fh, rc - r, 4, 0.0, cv)
    bm = bmesh.new()
    vs = [bm.verts.new((x, wf, y)) for x, y in pts]
    face = bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=[face], quad_method="BEAUTY", ngon_method="BEAUTY")
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            c = lp.vert.co
            lp[uvl].uv = ((c.x + fw / 2) / fw, (c.z - (cv - fh / 2)) / fh)
    bm.normal_update()
    orient(bm, (0.0, 1.0, cv))
    front = to_object("canvas_front", bm, [gesso_front], FRAME, smooth=False, recalc=False)
    obs.append(front)
    # the wrap: round the front edge, down the sides, round the back edge onto the stretchers' backs
    prof = []
    for k in range(7):
        a = math.pi / 2 * k / 6
        prof.append((r - r * math.sin(a), wf + r - r * math.cos(a)))
    for k in range(1, 5):
        prof.append((0.0, wf + r + (wb - r2 - wf - r) * k / 4))
    for k in range(1, 6):
        a = math.pi / 2 * k / 5
        prof.append((r2 - r2 * math.cos(a), wb - r2 + r2 * math.sin(a)))
    wrap = _sweep(_outline(CW, CH, rc, cv, 6), prof)
    wrap.normal_update()
    orient(wrap, (0.0, wf + CD / 2, cv))
    obs.append(to_object("canvas wrap", wrap, [gesso_wrap], FRAME, smooth=True, sharp=80, recalc=False))
    # the turned-over margin on the back, mitred at the corners, a folded flap over each corner
    M_ = 0.028
    bm = bmesh.new()
    corners = [(-CW / 2 + r2, v0 + r2), (CW / 2 - r2, v0 + r2), (CW / 2 - r2, v0 + CH - r2), (-CW / 2 + r2, v0 + CH - r2)]
    inner = [(-CW / 2 + M_, v0 + M_), (CW / 2 - M_, v0 + M_), (CW / 2 - M_, v0 + CH - M_), (-CW / 2 + M_, v0 + CH - M_)]
    wm = wb + 0.0001
    for i in range(4):
        a, b, c, d = corners[i], corners[(i + 1) % 4], inner[(i + 1) % 4], inner[i]
        bm.faces.new([bm.verts.new((p[0], wm, p[1])) for p in (a, b, c, d)])
    for i, (cx, cy) in enumerate(corners):
        sx = 1 if cx > 0 else -1
        sy = 1 if cy > cv else -1
        # the flap: a triangle folded in over the mitre, a little proud of the margin
        p1 = (cx, cy)
        p2 = (cx - sx * 0.040, cy)
        p3 = (cx - sx * 0.016, cy - sy * 0.030)
        bm.faces.new([bm.verts.new((p[0], wm + 0.0007, p[1])) for p in (p1, p2, p3)])
    bm.normal_update()
    orient(bm, (0.0, -1.0, cv))
    obs.append(to_object("canvas margin", bm, [gesso_wrap], FRAME, smooth=False, recalc=False))
    # the unprimed back of the cloth, seen between the stretchers
    bm = bmesh.new()
    a = 0.012
    q = [(-CW / 2 + a, v0 + a), (CW / 2 - a, v0 + a), (CW / 2 - a, v0 + CH - a), (-CW / 2 + a, v0 + CH - a)]
    bm.faces.new([bm.verts.new((x, wf + 0.0007, y)) for x, y in q])
    bm.normal_update()
    orient(bm, (0.0, -1.0, cv))
    obs.append(to_object("canvas back", bm, [raw], FRAME, smooth=False, recalc=False))
    obs += stretchers(pine, v0, cv, wf + FABRIC, wb - FABRIC)
    obs.append(staples(steel, v0, wb))
    return obs


def stretchers(pine, v0, cv, wf, wb):
    """Four mitred stretcher bars, 42 mm wide with a raised lip at the outer edge so the cloth only bears
    on it, a cross brace each way set back from the cloth, and a pair of keys in each corner."""
    obs = []
    BW = 0.042
    u1, v1 = CW / 2 - FABRIC, CH / 2 - FABRIC
    sides = [  # origin on the outer edge's middle, along, inward
        ((0.0, cv - v1), (1, 0), (0, 1), u1),
        ((u1, cv), (0, 1), (-1, 0), v1),
        ((0.0, cv + v1), (-1, 0), (0, -1), u1),
        ((-u1, cv), (0, -1), (1, 0), v1),
    ]
    # cross-section in (inset, depth from the back): x = inset, y = -w
    sec = [(0.0, -wf), (0.0, -wb), (BW, -wb), (BW, -(wf + 0.0045)), (0.011, -wf)]
    for i, ((ou, ov), (au, av), (iu, iv), half) in enumerate(sides):
        mtx = in_frame(Vector((ou, 0.0, ov)), Vector((au, 0, av)), Vector((iu, 0, iv)))
        bm = prism(sec, -half - 0.01, half + 0.01, "z")
        planes = []
        for e in (-1, 1):
            cu, cvv = ou + au * half * e, ov + av * half * e
            # the mitre: the diagonal from this outer corner inwards; drop what lies beyond it
            nu, nv = au * e + iu, av * e + iv
            ln = math.hypot(nu, nv)
            planes.append((F(cu, 0, cvv), FD(nu / ln, 0, nv / ln)))
        obs.append(wood_part(f"stretcher {i}", bm, mtx, pine, planes=planes, bevel=0.0012, segs=2))
    # cross braces, flush with the back, 8 mm clear of the cloth
    bd0, bd1 = wf + 0.008, wb
    obs.append(post("stretcher brace v", pine, -0.020, 0.020, bd0, bd1, cv - v1 + BW, cv + v1 - BW,
                    bevel=0.0012, segs=2))
    for s in (-1, 1):
        a, b = sorted((s * 0.020, s * (u1 - BW)))
        obs.append(board(f"stretcher brace h {s}", pine, a, b, bd0, bd1, cv - 0.020, cv + 0.020, bevel=0.0012, segs=2))
    # keys: small hardwood wedges tapped into the corner slots, lying against the bars' inner edges
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (1, 1), (-1, 1))):
        iu, iv = sx * (u1 - BW), cv + sy * (v1 - BW)
        for k, (a0, a1, b0, b1) in enumerate(((0.010, 0.040, 0.0, 0.008), (0.0, 0.008, 0.010, 0.040))):
            ua, ub = sorted((iu - sx * a0, iu - sx * a1))
            va, vb = sorted((iv - sy * b0, iv - sy * b1))
            obs.append(post(f"stretcher key {i}{k}", pine, ua, ub, wb - 0.010, wb + 0.0015, va, vb, bevel=0.0008, segs=1))
    return obs


def staples(steel, v0, wb):
    """Staples through the turned-over cloth into the stretchers' backs, every 55 mm or so."""
    bm = bmesh.new()
    w0 = wb + 0.0001
    cv = v0 + CH / 2
    def staple(u, v, horiz):
        L, Wd = 0.0105, 0.0011
        du, dv = (L / 2, Wd / 2) if horiz else (Wd / 2, L / 2)
        box_bm(u - du, u + du, w0, w0 + 0.0006, v - dv, v + dv, bm)
    inset = 0.016
    nu = int(CW / 0.055)
    for k in range(nu + 1):
        u = -CW / 2 + 0.045 + (CW - 0.09) * k / nu
        staple(u, v0 + inset, True)
        staple(u, v0 + CH - inset, True)
    nv = int(CH / 0.055)
    for k in range(nv + 1):
        v = v0 + 0.045 + (CH - 0.09) * k / nv
        staple(-CW / 2 + inset, v, False)
        staple(CW / 2 - inset, v, False)
    return to_object("canvas staples", bm, [steel], FRAME, bevel=0.0002, segs=1)


# ---------------------------------------------------------------- build

def build():
    beech = oiled_wood("easel beech")
    pine = oiled_wood("stretcher pine", colour=(0.66, 0.47, 0.28), contrast=1.4, rough=(0.55, 0.72), raw=True)
    brass = metal("easel brass", (0.80, 0.58, 0.26), 0.26)
    zinc = metal("easel zinc", (0.60, 0.60, 0.62), 0.30, tarnish=(0.30, 0.29, 0.27))
    knurled = metal("easel brass knurled", (0.80, 0.58, 0.26), 0.30, knurl=90)
    black = phenolic("easel knob")
    # the work in progress painting.py paints (owner, 2026-11-25); EASEL_PAINTING swaps another in, "none" leaves it blank
    painting = os.environ.get("EASEL_PAINTING") or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders", "painting.png")
    if painting == "none" or not os.path.exists(painting):
        painting = None
    face = (-CW / 2, CW / 2, LEDGE_V + 0.0005, LEDGE_V + 0.0005 + CH)
    front = gesso("canvas front", painting=painting, face=face)
    wrap = gesso("canvas gesso", face=face)
    raw = raw_canvas("canvas raw")

    for s in (-1, 1):
        front_leg(s, beech)
    mast(beech)
    rack(brass)
    crossbar(beech)
    ledge(beech)
    clamp(beech)
    back_leg(beech)
    hinge(brass)
    stay(beech, brass, zinc)
    apex_bolt(zinc, brass)
    screws(brass)
    knobs(brass, knurled, black, zinc)
    canvas(front, wrap, raw, pine, zinc)
