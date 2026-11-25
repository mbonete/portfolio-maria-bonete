# The standing desk: a 2.2 x 0.75 m solid oak butcher-block top, 30 mm thick with softly rounded edges,
# on a black powder-coated electric frame (two two-stage telescoping legs, wide stage at the bottom as in
# the reference; T feet on levelling glides; side brackets and a telescoping crossbeam under the top; a
# control box and a small keypad at the front right). Desk-local metres, the top's upper face at DESK_H.
import math
from mathutils import Matrix, Vector
from common import DESK_H, DESK_W, DESK_D
from objects.desk_kit import (rrect, prism, loft, cylinder, transform, mesh_object, N, out, M, V, mix_rgb,
                              mix_f, maprange, xyz, comb, tex, new_material, shared, principled, powder,
                              powder_edge, plastic, rubber, zinc, black_steel, TRAY_X, TRAY_Y, TRAY_DROP, TRAY_LIP)

TOP_T = 0.030                  # top thickness
LEG_X = 0.92                   # leg centres, as the stand-in
LEG_Y = 0.02                   # a little behind the middle of the depth
FOOT_L, FOOT_W = 0.68, 0.080   # T foot
GLIDE = 0.013                  # the feet stand this high on their glides
FOOT_H = 0.036
LOW = (0.078, 0.058)           # outer (lower) stage of the column
UPP = (0.066, 0.046)           # inner (upper) stage
SPLIT = 0.385                  # where the inner stage leaves the outer
BRK_H = 0.030                  # side bracket height under the top
UNDER = DESK_H - TOP_T         # underside of the top

STAVE = 0.042                  # butcher-block stave width
TILE = 1.83                    # real size of the oak texture (Poly Haven oak_veneer_01)
OAK = "polyhaven/oak_veneer_01/oak_veneer_01_"


# ---------------------------------------------------------------- the oak top

def _oak(name):
    """Butcher block: 42 mm oak staves running the length, each cut from a different part of the veneer
    scan with its own tone, hairline glue joints between them, end grain on the two ends, and a satin
    lacquer. Everything in object space, so it needs no UVs and scales with the desk."""
    m, t = new_material(name)
    tc = N(t, "ShaderNodeTexCoord")
    co, nrm = out(tc, "Object"), out(tc, "Normal")
    x, y, z = xyz(t, co)
    nx, ny, nz = xyz(t, nrm)
    s = M(t, "DIVIDE", M(t, "ADD", y, DESK_D / 2), STAVE)          # stave coordinate across the depth
    i = M(t, "FLOOR", s)
    r1 = out(N(t, "ShaderNodeTexWhiteNoise", _noise_dimensions="1D", W=i), "Color")
    r2 = out(N(t, "ShaderNodeTexWhiteNoise", _noise_dimensions="1D", W=M(t, "ADD", i, 37.0)), "Color")
    a1, b1, c1 = xyz(t, r1)
    a2, b2, c2 = xyz(t, r2)
    # The veneer's grain runs along its v axis: v follows the length (x); u runs across the stave and
    # down its edge (y + z is continuous over the rounded edge, so the grain wraps it like solid wood).
    across = M(t, "ADD", M(t, "ADD", y, z), M(t, "MULTIPLY", a1, TILE))
    along = M(t, "ADD", x, M(t, "MULTIPLY", b1, TILE))
    vec = comb(t, M(t, "DIVIDE", across, TILE), M(t, "DIVIDE", along, TILE))
    col = tex(t, OAK + "diff_4k.jpg", vec, True)
    rgh = tex(t, OAK + "rough_4k.jpg", vec, False)
    # the scan's figure is bolder than a butcher block's: soften it toward its mean colour
    soft = mix_rgb(t, 0.32, out(col), (0.356, 0.208, 0.095, 1))
    # per-stave tone: a little lighter or darker, a little warmer or cooler
    hsv = N(t, "ShaderNodeHueSaturation", Hue=M(t, "ADD", 0.5, M(t, "MULTIPLY", M(t, "SUBTRACT", a2, 0.5), 0.03)),
            Saturation=M(t, "ADD", 1.02, M(t, "MULTIPLY", M(t, "SUBTRACT", b2, 0.5), 0.22)),
            Value=M(t, "ADD", 1.0, M(t, "MULTIPLY", M(t, "SUBTRACT", c2, 0.5), 0.26)), Color=soft)
    grade = N(t, "ShaderNodeHueSaturation", Hue=0.505, Saturation=1.12, Value=1.03, Color=out(hsv))
    wood = out(grade)
    # glue joints between staves, on the top, underside and ends (not on the long edges)
    f = M(t, "SUBTRACT", s, i)
    d = M(t, "MULTIPLY", M(t, "MINIMUM", f, M(t, "SUBTRACT", 1.0, f)), STAVE)
    line = maprange(t, d, 0.0, 0.0006, 1.0, 0.0, interp="SMOOTHSTEP")
    line = M(t, "MULTIPLY", line, M(t, "SUBTRACT", 1.0, M(t, "ABSOLUTE", ny)))
    wood = mix_rgb(t, M(t, "MULTIPLY", line, 0.45), wood, (0.10, 0.055, 0.025, 1), "MULTIPLY")
    # end grain on the two ends: each stave's growth rings, arcs around a pith somewhere below or above
    # it, each ring opening with a band of oak's large earlywood pores
    cy = M(t, "ADD", M(t, "MULTIPLY", M(t, "ADD", i, M(t, "ADD", 0.2, M(t, "MULTIPLY", a2, 0.6))), STAVE), -DESK_D / 2)
    sgn = M(t, "SUBTRACT", M(t, "MULTIPLY", M(t, "GREATER_THAN", b2, 0.5), 2.0), 1.0)
    cz = M(t, "SUBTRACT", DESK_H - TOP_T / 2, M(t, "MULTIPLY", sgn, M(t, "ADD", 0.025, M(t, "MULTIPLY", c1, 0.13))))
    dist = V(t, "LENGTH", comb(t, M(t, "SUBTRACT", y, cy), M(t, "SUBTRACT", z, cz)))
    wob = out(N(t, "ShaderNodeTexNoise", co, Scale=18.0, Detail=2.0), "Factor")
    dist = M(t, "ADD", dist, M(t, "MULTIPLY", wob, 0.0007))
    ring = M(t, "FRACT", M(t, "DIVIDE", dist, M(t, "ADD", 0.0016, M(t, "MULTIPLY", b1, 0.0018))))
    ring = maprange(t, ring, 0.0, 0.22, 1.0, 0.0, interp="SMOOTHSTEP")
    pores = out(N(t, "ShaderNodeTexNoise", co, Scale=2600.0, Detail=1.0), "Factor")
    porous = M(t, "MULTIPLY", ring, maprange(t, pores, 0.35, 0.6, 0.35, 1.0))
    endc = mix_rgb(t, porous, (0.20, 0.112, 0.050, 1), (0.105, 0.056, 0.024, 1))
    endc = mix_rgb(t, maprange(t, pores, 0.62, 0.75, 0.0, 0.3), endc, (0.07, 0.036, 0.015, 1))
    endc = mix_rgb(t, M(t, "MULTIPLY", line, 0.6), endc, (0.05, 0.025, 0.01, 1))
    endm = maprange(t, M(t, "ABSOLUTE", nx), 0.6, 0.85, 0.0, 1.0)
    colour = mix_rgb(t, endm, wood, endc)
    # satin lacquer: roughness follows the open pores; end grain drinks the finish and stays duller
    r = maprange(t, out(rgh), 0.25, 0.85, 0.28, 0.48)
    smear = out(N(t, "ShaderNodeTexNoise", co, Scale=3.0, Detail=5.0, Roughness=0.65), "Factor")
    r = M(t, "ADD", r, maprange(t, smear, 0.35, 0.7, -0.05, 0.06))
    r = mix_f(t, endm, r, 0.62)
    lum = out(N(t, "ShaderNodeRGBToBW", Color=out(col)))
    bump = N(t, "ShaderNodeBump", Strength=0.18, Distance=0.00025, Height=lum)
    rb = N(t, "ShaderNodeBump", Strength=0.35, Distance=0.0002, Height=M(t, "SUBTRACT", 1.0, porous), Normal=out(bump))
    nor = out(N(t, "ShaderNodeMix", _data_type="VECTOR", Factor_Float=endm, A_Vector=out(bump), B_Vector=out(rb)), "Result_Vector")
    principled(t, **{"Base Color": colour, "Roughness": r, "Normal": nor, "Specular IOR Level": 0.5})
    return m


def top():
    bm = prism(rrect(DESK_W, DESK_D, 0.010, 8), UNDER, DESK_H)
    ob = mesh_object("desk top", bm, [shared("oak butcher block", _oak)], bevel=0.0055, segs=6)
    return ob


# ---------------------------------------------------------------- frame

def foot(sx):
    """A T foot: a steel bar 80 mm wide, deepest under the column and tapering to the ends, with plastic
    end caps and a levelling glide under each end."""
    x0 = sx * LEG_X
    L, H, he, flat = FOOT_L - 0.016, FOOT_H, 0.021, 0.20
    z0 = GLIDE
    # the top: flat under the column, then easing down into a straight taper towards each end
    def zt(y):
        u = max(0.0, abs(y) - flat / 2) / (L / 2 - flat / 2)
        e = u * u * (2 - u) if u < 1 else 1.0          # starts tangent to the flat, ends on the taper
        return z0 + H - (H - he) * e
    ys = [L / 2 * k / 16 for k in range(17)]
    ys = sorted(set([-y for y in ys] + ys))
    top_pts = [(y, zt(y)) for y in reversed(ys)]
    prof = [(-L / 2, z0), (L / 2, z0)] + top_pts
    prof = [(y + LEG_Y, z) for y, z in prof]
    bm = prism(prof, x0 - FOOT_W / 2, x0 + FOOT_W / 2, "x")
    mesh_object("foot", bm, [powder(), powder_edge()], bevel=0.0045, segs=4, sharp=20, bevel_mat=1)
    for e in (-1, 1):
        # end cap, the bar's profile continued 8 mm in plastic, its outer face slightly domed
        y0 = LEG_Y + e * L / 2
        cap = [(-FOOT_W / 2 + 0.001, z0 + 0.0005), (FOOT_W / 2 - 0.001, z0 + 0.0005), (FOOT_W / 2 - 0.001, z0 + he - 0.0005),
               (-FOOT_W / 2 + 0.001, z0 + he - 0.0005)]
        cap = [(x + x0, z) for x, z in cap]
        bm = prism(cap, y0, y0 + e * 0.008, "y")
        mesh_object("foot cap", bm, [plastic("cap plastic", (0.014, 0.014, 0.015), 0.38)], bevel=0.0035, segs=4)
        # levelling glide: a threaded stem and a round pad
        gy = LEG_Y + e * (L / 2 - 0.045)
        bm = cylinder(0.0055, 0.006, z0 + 0.001, 24, cx=x0, cy=gy)
        mesh_object("glide stem", bm, [zinc()], bevel=0.0006, segs=2)
        bm = cylinder(0.0085, 0.0062, 0.0095, 6, cx=x0, cy=gy)
        mesh_object("glide nut", bm, [zinc()], bevel=0.0007, segs=2)
        bm = loft([(rrect(0.044, 0.044, 0.022, 10, x0, gy), 0.0), (rrect(0.044, 0.044, 0.022, 10, x0, gy), 0.0045),
                   (rrect(0.036, 0.036, 0.018, 10, x0, gy), 0.0068)])
        mesh_object("glide pad", bm, [rubber()], bevel=0.0012, segs=3)
    # two socket-head bolts holding the column's base plate
    for e in (-1, 1):
        by = LEG_Y + e * 0.052
        bm = cylinder(0.0062, z0 + H - 0.0005, z0 + H + 0.0042, 28, cx=x0, cy=by)
        bolt = mesh_object("foot bolt", bm, [black_steel()], bevel=0.0009, segs=2)
        bm = prism([(x0 + 0.0032 * math.cos(a), by + 0.0032 * math.sin(a)) for a in [k * math.pi / 3 for k in range(6)]],
                   z0 + H + 0.0020, z0 + H + 0.00425)
        mesh_object("bolt socket", bm, [rubber()], smooth=False)


def column(sx):
    x0 = sx * LEG_X
    zb = GLIDE + FOOT_H
    # outer (lower) stage, on a base plate welded to the foot
    bm = prism(rrect(LOW[0] + 0.012, LOW[1] + 0.030, 0.006, 6, x0, LEG_Y), zb - 0.002, zb + 0.004)
    mesh_object("column plate", bm, [powder(), powder_edge()], bevel=0.0018, segs=3, bevel_mat=1)
    bm = prism(rrect(*LOW, 0.0055, 8, x0, LEG_Y), zb + 0.004, SPLIT)
    mesh_object("column outer", bm, [powder(), powder_edge()], bevel=0.0016, segs=3, bevel_mat=1)
    # the plastic bushing the inner stage slides through
    bm = loft([(rrect(LOW[0] + 0.001, LOW[1] + 0.001, 0.006, 8, x0, LEG_Y), SPLIT - 0.002),
               (rrect(LOW[0] + 0.001, LOW[1] + 0.001, 0.006, 8, x0, LEG_Y), SPLIT + 0.006),
               (rrect(UPP[0] + 0.006, UPP[1] + 0.006, 0.006, 8, x0, LEG_Y), SPLIT + 0.009)])
    mesh_object("column bushing", bm, [plastic("bushing plastic", (0.012, 0.012, 0.013), 0.5)], bevel=0.0012, segs=3)
    # inner (upper) stage up to the top housing
    bm = prism(rrect(*UPP, 0.005, 8, x0, LEG_Y), SPLIT - 0.05, UNDER - BRK_H - 0.012)
    mesh_object("column inner", bm, [powder(), powder_edge()], bevel=0.0015, segs=3, bevel_mat=1)
    # top housing (the motor's end), bolted to the side bracket
    bm = prism(rrect(LOW[0] + 0.008, LOW[1] + 0.022, 0.007, 6, x0, LEG_Y), UNDER - BRK_H - 0.014, UNDER - BRK_H)
    mesh_object("column head", bm, [powder(), powder_edge()], bevel=0.0025, segs=3, bevel_mat=1)


def bracket(sx):
    """Side bracket: a 50 mm steel channel along the depth under the top, its ends cut at 45 degrees."""
    x0 = sx * LEG_X
    L, c = 0.64, BRK_H
    prof = [(-L / 2 + c, UNDER - BRK_H), (L / 2 - c, UNDER - BRK_H), (L / 2, UNDER - 0.0005), (-L / 2, UNDER - 0.0005)]
    prof = [(y + LEG_Y - 0.01, z) for y, z in prof]
    bm = prism(prof, x0 - 0.025, x0 + 0.025, "x")
    mesh_object("side bracket", bm, [powder(), powder_edge()], bevel=0.002, segs=3, bevel_mat=1)


def crossbeam():
    """Telescoping crossbeam between the side brackets: two outer tubes and the inner one between."""
    y0, zc = LEG_Y - 0.01, UNDER - 0.019
    xin = LEG_X - 0.025
    for sx in (-1, 1):
        a, b = sx * xin, sx * 0.16
        bm = prism(rrect(0.050, 0.034, 0.003, 4, y0, zc), min(a, b), max(a, b), "x")
        mesh_object("crossbeam outer", bm, [powder(), powder_edge()], bevel=0.0015, segs=3, bevel_mat=1)
    bm = prism(rrect(0.044, 0.028, 0.003, 4, y0, zc), -0.30, 0.30, "x")
    mesh_object("crossbeam inner", bm, [powder(), powder_edge()], bevel=0.0012, segs=3, bevel_mat=1)


def cable_tray():
    """A folded sheet-steel tray hung under the back edge, a tall front wall and a low back lip, closed at
    the ends, on two angle brackets screwed to the top."""
    tk = 0.0015
    y0, y1 = TRAY_Y
    zb, zf, zl = UNDER - TRAY_DROP, UNDER - 0.012, UNDER - TRAY_LIP
    prof = [(y0, zf), (y0, zb), (y1, zb), (y1, zl), (y1 - tk, zl), (y1 - tk, zb + tk), (y0 + tk, zb + tk), (y0 + tk, zf)]
    bm = prism(prof, TRAY_X[0], TRAY_X[1], "x")
    mesh_object("cable tray", bm, [powder(), powder_edge()], bevel=0.0006, segs=2, bevel_mat=1)
    for e, xe in ((1, TRAY_X[0]), (-1, TRAY_X[1])):
        end = [(y0, zf), (y0, zb), (y1, zb), (y1, zl)]
        bm = prism(end, xe, xe + e * tk, "x")
        mesh_object("tray end", bm, [powder(), powder_edge()], bevel=0.0005, segs=2, bevel_mat=1)
        # angle bracket from the end plate's top up to the underside
        xb = xe + e * 0.004
        bm = prism([(y0 + 0.01, zf - 0.03), (y0 + 0.05, zf - 0.03), (y0 + 0.05, UNDER - 0.0005), (y0 + 0.01, UNDER - 0.0005)],
                   xb, xb + e * 0.003, "x")
        mesh_object("tray bracket", bm, [powder(), powder_edge()], bevel=0.0008, segs=2, bevel_mat=1)


def control_box():
    bm = prism(rrect(0.22, 0.085, 0.008, 6, 0.36, LEG_Y + 0.11), UNDER - 0.034, UNDER - 0.001)
    mesh_object("control box", bm, [plastic()], bevel=0.003, segs=3)


def keypad():
    """The height keypad under the front edge on the right: a wedge-shaped housing whose sloped face, turned
    up towards the user, holds up/down rockers and four round memory buttons. No markings."""
    xc, W = 0.66, 0.128
    yb, zt = -DESK_D / 2 + 0.038, UNDER - 0.0005
    prof = [(yb, zt), (yb, zt - 0.021), (-DESK_D / 2 - 0.012, zt - 0.021), (-DESK_D / 2 - 0.001, zt)]
    bm = prism(prof, xc - W / 2, xc + W / 2, "x")
    mesh_object("keypad", bm, [plastic("keypad plastic", (0.012, 0.012, 0.013), 0.32, grain=0.06, bump=0.02)],
                bevel=0.0028, segs=4)
    # the sloped face: from (y=-D/2-0.012, z=zt-0.021) up to (y=-D/2-0.001, z=zt)
    p0 = Vector((0, -DESK_D / 2 - 0.012, zt - 0.021))
    p1 = Vector((0, -DESK_D / 2 - 0.001, zt))
    up = (p1 - p0).normalized()
    n = Vector((0, -up.z, up.y))                      # the face's outward normal (forward and up)
    mid = (p0 + p1) / 2
    rot = Matrix.Rotation(math.atan2(-n.y, n.z), 4, "X")   # maps +z onto n
    key = plastic("key rubber", (0.022, 0.022, 0.024), 0.55, grain=0.02, bump=0.01)
    # a dark display window at the left
    bm = prism(rrect(0.030, 0.012, 0.002, 4), 0.0, 0.0004)
    transform(bm, Matrix.Translation(Vector((xc - 0.040, mid.y, mid.z))) @ rot)
    disp = shared("keypad display", _display)
    mesh_object("keypad display", bm, [disp], smooth=False)
    # up / down: two rounded keys with a raised chevron each
    for k, (dx, flip) in enumerate(((-0.004, 1), (0.014, -1))):
        bm = loft([(rrect(0.013, 0.0095, 0.0035, 6), 0.0), (rrect(0.013, 0.0095, 0.0035, 6), 0.0010),
                   (rrect(0.011, 0.0075, 0.0025, 6), 0.0016)])
        transform(bm, Matrix.Translation(Vector((xc + dx, mid.y, mid.z))) @ rot)
        mesh_object("key", bm, [key], bevel=0.0003, segs=2)
        tri = [(-0.0028, -0.0012 * flip), (0.0028, -0.0012 * flip), (0.0, 0.0018 * flip)]
        if flip < 0:
            tri = tri[::-1]
        bm = prism(tri, 0.0016, 0.00172)
        transform(bm, Matrix.Translation(Vector((xc + dx, mid.y, mid.z))) @ rot)
        mesh_object("key mark", bm, [shared("key print", lambda n: _print(n))], smooth=False)
    # four memory buttons
    for k in range(4):
        bm = loft([(rrect(0.0068, 0.0068, 0.0034, 6), 0.0), (rrect(0.0068, 0.0068, 0.0034, 6), 0.0009),
                   (rrect(0.0056, 0.0056, 0.0028, 6), 0.0014)])
        transform(bm, Matrix.Translation(Vector((xc + 0.027 + k * 0.0095, mid.y, mid.z))) @ rot)
        mesh_object("memory key", bm, [key], bevel=0.0002, segs=2)


def _print(name):
    m, t = new_material(name)
    principled(t, **{"Base Color": (0.30, 0.30, 0.31, 1), "Roughness": 0.5})
    return m


def _display(name):
    m, t = new_material(name)
    principled(t, **{"Base Color": (0.004, 0.005, 0.006, 1), "Roughness": 0.08, "Specular IOR Level": 0.6})
    return m


def build():
    top()
    for sx in (-1, 1):
        foot(sx)
        column(sx)
        bracket(sx)
    crossbeam()
    cable_tray()
    control_box()
    keypad()
