# Three monitors as laid out by monitors_layout(): the landscape pair on one dual arm (a weighted base, a
# pole and two articulated arms to their VESA mounts), the portrait one pivoted on its own height-adjustable
# stand. Each is a thin-bezel panel with a slim domed back; the screens show the owner's projects as a lit
# display under an anti-glare cover. Desk-local metres; no brands or logos.
import os
import math
import bmesh
from mathutils import Matrix, Vector
from common import DESK_H, DESK_D, monitors_layout
from objects.desk_kit import (rrect, prism, loft, cylinder, transform, mesh_object, curve_tube, N, out, M, V,
                              mix_rgb, xyz, comb, tex, new_material, shared, principled, powder, powder_edge,
                              plastic, rubber, black_steel, TRAY_Y, TRAY_DROP, TRAY_LIP)

ROOT = "/Users/mbonete/code/new-portfolio/public/"
SHOTS = {  # left landscape, right landscape, portrait
    0: ROOT + "screens/prompt-beach-desktop.webp",
    1: os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "renders", "ide.png"),  # ide.py
    2: ROOT + "screens/switchboard-panel.webp",
}
# The portrait screen: the Switchboard panel (580 x 1500, owner's pick 2026-11-25) at full height, centred on
# its own dark ground (#1e1e1e), so the monitor reads as one dark app.
PORTRAIT_ASPECT = 580 / 1500
# The landscape shots' aspect: Prompt Beach is a 16:10 screenshot (cropped to the 16:9 panel); the middle
# one is the editor view ide.py draws at 16:9 (owner, 2026-11-25: an IDE there instead of Studiolo).
SHOT_ASPECT = {0: 16 / 10, 1: 16 / 9}
PORTRAIT_FILL = 1.0
PORTRAIT_BG = (0.0130, 0.0130, 0.0130, 1)
# A full-white pixel's emission: the screenshots come out at about their own values under the scene's
# exposure, whites just short of clipping. The light they throw on the desk (diffuse bounces only) is
# SPILL times that, so the glow on the desk top and keyboard reads; reflections stay true to the screen.
GLOW = 1.38
SPILL = 4.0

# The panel, in its own landscape frame: x across, z up, -y towards the viewer; origin at the layout's
# centre. A 16:9 active area as wide as the outer width allows with 9.5 mm side and top borders, the rest
# of the height going to the chin.
SIDE = 0.0095
RIM = 0.0016          # the plastic lip around the glass
FRONT = -0.0085       # glass front
BACK = 0.0045         # back of the thin slab
DOME = 0.028          # how far the back housing bulges behind the slab
VESA_Y = BACK + DOME  # where the VESA plate sits


def frame_of(m):
    """Monitor-local -> desk-local: rotate about z by its turn, pivot the portrait one 90 degrees
    clockwise (its chin to the left), move to its centre."""
    rot = Matrix.Rotation(math.radians(m["turn"]), 4, "Z")
    if m["kind"] == "portrait":
        rot = rot @ Matrix.Rotation(math.radians(90), 4, "Y")
    return Matrix.Translation(Vector(m["centre"])) @ rot


def panel_dims(m):
    """Landscape-frame outer width and height."""
    return (m["w"], m["h"]) if m["kind"] == "landscape" else (m["h"], m["w"])


# ---------------------------------------------------------------- screen material

def _screen(name, idx, portrait, aw, ah):
    """The lit image under an anti-glare cover. UVs put the active area at [0,1]^2 (landscape frame); the
    black border under the glass falls outside and does not glow."""
    m, t = new_material(name)
    m.cycles.emission_sampling = "FRONT"
    uv = out(N(t, "ShaderNodeTexCoord"), "UV")
    u, v, _ = xyz(t, uv)
    inside = M(t, "MULTIPLY", M(t, "MULTIPLY", M(t, "GREATER_THAN", u, 0.0), M(t, "LESS_THAN", u, 1.0)),
               M(t, "MULTIPLY", M(t, "GREATER_THAN", v, 0.0), M(t, "LESS_THAN", v, 1.0)))
    if not portrait:
        # a screenshot on the 16:9 panel: full width, a 16:10 one cropped in height (kept from the top,
        # where the apps keep their title bars)
        f = SHOT_ASPECT[idx] / (aw / ah)
        top = {0: 1.0, 1: 0.5}[idx]
        v0 = (1 - f) * top
        img = tex(t, SHOTS[idx], comb(t, u, M(t, "ADD", v0, M(t, "MULTIPLY", v, f))), True, extension="EXTEND")
        col = out(img)
    else:
        # display frame of the pivoted panel: right = landscape up, up = landscape left
        ud, vd = v, M(t, "SUBTRACT", 1.0, u)
        W, H = ah, aw                                   # the portrait active area
        hf = PORTRAIT_FILL
        wf = PORTRAIT_ASPECT * hf * H / W               # the window's width, in display units
        wu = M(t, "DIVIDE", M(t, "SUBTRACT", ud, 0.5 - wf / 2), wf)
        wv = M(t, "DIVIDE", M(t, "SUBTRACT", vd, (1 - hf) / 2), hf)
        img = tex(t, SHOTS[idx], comb(t, wu, wv), True, extension="CLIP")
        # rounded window corners and the dark ground around the window
        qx = M(t, "SUBTRACT", M(t, "ABSOLUTE", M(t, "SUBTRACT", wu, 0.5)), 0.5 - 0.0143 * 2)
        qy = M(t, "SUBTRACT", M(t, "ABSOLUTE", M(t, "SUBTRACT", wv, 0.5)), 0.5 - 0.0143)
        qd = V(t, "LENGTH", comb(t, M(t, "MAXIMUM", M(t, "MULTIPLY", qx, 0.5), 0.0), M(t, "MAXIMUM", qy, 0.0)))
        corner = M(t, "LESS_THAN", qd, 0.0143)
        a = M(t, "MULTIPLY", out(img, "Alpha"), corner)
        bg = PORTRAIT_BG
        col = mix_rgb(t, a, bg, out(img))
    glow = mix_rgb(t, inside, (0, 0, 0, 1), col)
    lp = N(t, "ShaderNodeLightPath")
    strength = M(t, "MULTIPLY", GLOW, M(t, "ADD", 1.0, M(t, "MULTIPLY", out(lp, "Is Diffuse Ray"), SPILL - 1.0)))
    principled(t, **{"Base Color": (0.004, 0.004, 0.005, 1), "Roughness": 0.20, "Specular IOR Level": 0.5,
                     "IOR": 1.5, "Emission Color": glow, "Emission Strength": strength})
    return m


# ---------------------------------------------------------------- one monitor

def monitor(m, idx):
    W, H = panel_dims(m)
    aw = W - 2 * SIDE
    ah = aw * 9 / 16
    az1 = H / 2 - SIDE                  # active area top
    az0 = az1 - ah                      # active area bottom; below it the chin
    X = frame_of(m)
    body = plastic("monitor plastic", (0.017, 0.017, 0.019), 0.42, grain=0.10, scale=0.07, bump=0.03)
    rim = shared("monitor rim", lambda n: _rim(n))
    # thin slab: outer rounded rectangle
    bm = prism(rrect(W, H, 0.0055, 6), FRONT + 0.0004, BACK, "y")
    mesh_object("monitor slab", transform(bm, X), [rim], bevel=0.0012, segs=3)
    # the glass, from the plastic lip to the lip, down to just under the active area
    g = SIDE - RIM
    gx0, gx1, gz0, gz1 = -W / 2 + RIM, W / 2 - RIM, az0 - g, H / 2 - RIM
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in ((gx0, FRONT, gz0), (gx1, FRONT, gz0), (gx1, FRONT, gz1), (gx0, FRONT, gz1))]
    f = bm.faces.new(vs[::-1])  # normal towards -y
    uvl = bm.loops.layers.uv.new("UVMap")
    for lp in f.loops:
        x, _, z = lp.vert.co
        lp[uvl].uv = ((x + aw / 2) / aw, (z - az0) / ah)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    transform(bm, X)
    scr = _screen(f"screen {idx}", idx, m["kind"] == "portrait", aw, ah)
    mesh_object("screen", bm, [scr], smooth=False)
    # domed back housing: a quarter-ellipse profile from the slab's back to a flat back face
    secs = []
    for k in range(7):
        th = math.radians(90 * k / 6)
        ins = (1 - math.cos(th))
        w_, h_ = 0.60 * W - ins * 0.16 * W, 0.80 * H - ins * 0.26 * H
        secs.append((rrect(w_, h_, 0.045 + ins * 0.01, 8, 0.0, -0.03 * H), BACK - 0.0008 + math.sin(th) * DOME))
    bm = loft(secs, "y")
    mesh_object("monitor back", transform(bm, X), [body], sharp=80)
    # VESA plate (on the arm/stand side) with four screws
    bm = prism(rrect(0.118, 0.118, 0.008, 4), VESA_Y, VESA_Y + 0.004, "y")
    mesh_object("vesa plate", transform(bm, X), [powder(), powder_edge()], bevel=0.0012, segs=2, bevel_mat=1)
    for sx in (-1, 1):
        for sz in (-1, 1):
            bm = cylinder(0.0042, VESA_Y + 0.004, VESA_Y + 0.0068, 20, cx=sx * 0.05, cy=sz * 0.05, axis="y")
            mesh_object("vesa screw", transform(bm, X), [black_steel()], bevel=0.0008, segs=2)


def _rim(name):
    m, t = new_material(name)
    principled(t, **{"Base Color": (0.014, 0.014, 0.016, 1), "Roughness": 0.36, "Specular IOR Level": 0.5})
    return m


# ---------------------------------------------------------------- stands

def stadium(p, q, r, z0, z1, name, mats, bevel=0.002):
    """A flat arm link: a slot shape from p to q (xy), r its half width, from z0 to z1."""
    p, q = Vector((p[0], p[1])), Vector((q[0], q[1]))
    d = (q - p)
    a = math.atan2(d.y, d.x)
    L = d.length
    pts = rrect(L + 2 * r, 2 * r, r * 0.999, 10)
    c, s = math.cos(a), math.sin(a)
    mid = (p + q) / 2
    pts = [(mid.x + x * c - y * s, mid.y + x * s + y * c) for x, y in pts]
    return mesh_object(name, prism(pts, z0, z1), mats, bevel=bevel, segs=3)


def back_dir(m):
    a = math.radians(m["turn"])
    return Vector((-math.sin(a), math.cos(a), 0))


def dual_arm(lay):
    """Weighted base at the pair's shared foot, a 35 mm pole at its back and two arms reaching to the
    VESA plates behind the monitors."""
    fx, fy = lay[0]["foot"]
    pc = powder()
    pe = powder_edge()
    base_c = (fx, fy + 0.01)
    bm = loft([(rrect(0.245, 0.18, 0.035, 10, *base_c), DESK_H), (rrect(0.245, 0.18, 0.035, 10, *base_c), DESK_H + 0.009),
               (rrect(0.233, 0.168, 0.029, 10, *base_c), DESK_H + 0.013)], "z")
    mesh_object("arm base", bm, [pc, pe], bevel=0.0015, segs=3, sharp=25, bevel_mat=1)
    # felt pad under it, so it does not sit on the wood with a hard line
    bm = prism(rrect(0.235, 0.17, 0.03, 10, *base_c), DESK_H - 0.0001, DESK_H + 0.0008)
    mesh_object("arm base felt", bm, [rubber()], smooth=False)
    P = Vector((fx, fy + 0.066))
    ztop = DESK_H + 0.47
    bm = cylinder(0.0175, DESK_H + 0.012, ztop, 48, cx=P.x, cy=P.y)
    mesh_object("arm pole", bm, [pc, pe], bevel=0.0015, segs=2, bevel_mat=1)
    bm = cylinder(0.0185, ztop - 0.002, ztop + 0.008, 48, cx=P.x, cy=P.y)
    mesh_object("pole cap", bm, [plastic("cap plastic", (0.014, 0.014, 0.015), 0.38)], bevel=0.003, segs=3)
    bm = cylinder(0.026, DESK_H + 0.012, DESK_H + 0.03, 48, cx=P.x, cy=P.y)
    mesh_object("pole foot collar", bm, [pc, pe], bevel=0.0025, segs=3, bevel_mat=1)
    zc = lay[0]["centre"][2]
    # the clamp collar the two arms hang from
    bm = cylinder(0.027, zc - 0.050, zc - 0.006, 48, cx=P.x, cy=P.y)
    mesh_object("arm collar", bm, [pc, pe], bevel=0.003, segs=3, bevel_mat=1)
    bm = cylinder(0.0065, P.y + 0.024, P.y + 0.040, 20, cx=P.x, cy=zc - 0.028, axis="y")  # its clamp knob
    mesh_object("collar knob", bm, [plastic("cap plastic", (0.014, 0.014, 0.015), 0.38)], bevel=0.002, segs=2)
    for m in lay[:2]:
        C = Vector(m["centre"])
        b = back_dir(m)
        Hd = C + b * (VESA_Y + 0.004 + 0.040)                     # swivel behind the VESA plate
        E = Vector(((P.x + Hd.x) / 2, max(P.y, Hd.y) + 0.07, 0))   # elbow, folded back
        z1a, z1b = zc - 0.045, zc - 0.017                          # lower link (from the collar)
        z2a, z2b = zc - 0.014, zc + 0.014                          # upper link (to the head)
        stadium(P, E, 0.0175, z1a, z1b, "arm link", [pc, pe])
        stadium(E, Hd, 0.016, z2a, z2b, "arm link", [pc, pe])
        bm = cylinder(0.0185, z1a - 0.004, z2b + 0.004, 40, cx=E.x, cy=E.y)
        mesh_object("arm elbow", bm, [pc, pe], bevel=0.003, segs=3, bevel_mat=1)
        bm = cylinder(0.017, z2a - 0.012, z2b + 0.006, 40, cx=Hd.x, cy=Hd.y)
        mesh_object("arm swivel", bm, [pc, pe], bevel=0.003, segs=3, bevel_mat=1)
        tilt_head(m)
    return P


def tilt_head(m):
    """From the swivel to the VESA plate: a short block with a horizontal tilt knuckle (in the monitor's
    frame the swivel stands 44 mm behind the plate)."""
    X = frame_of(m)
    pc, pe = powder(), powder_edge()
    bm = prism(rrect(0.036, 0.040, 0.006, 4), VESA_Y + 0.004, VESA_Y + 0.030, "y")
    mesh_object("tilt block", transform(bm, X), [pc, pe], bevel=0.002, segs=3, bevel_mat=1)
    bm = cylinder(0.011, -0.028, 0.028, 32, cx=VESA_Y + 0.026, cy=0.0, axis="x")
    mesh_object("tilt knuckle", transform(bm, X), [pc, pe], bevel=0.002, segs=3, bevel_mat=1)


def portrait_stand(m):
    """A height-adjustable stand: an oval base, a flat column on the monitor's axis behind it, a carriage
    with the pivot disc at the VESA plate."""
    C = Vector(m["centre"])
    b = back_dir(m)
    tv = Vector((b.y, -b.x, 0))                 # the monitor's own right, along the desk
    k = 0.083                                    # the column's depth behind the panel's centre plane
    U = C + b * k
    U.z = 0
    pc, pe = powder(), powder_edge()
    a = math.atan2(tv.y, tv.x)
    R = Matrix.Rotation(a, 4, "Z")
    bc = U - b * 0.032
    bm = loft([(rrect(0.235, 0.165, 0.06, 10), DESK_H), (rrect(0.235, 0.165, 0.06, 10), DESK_H + 0.008),
               (rrect(0.223, 0.153, 0.054, 10), DESK_H + 0.012)], "z")
    transform(bm, Matrix.Translation((bc.x, bc.y, 0)) @ R)
    mesh_object("stand base", bm, [pc, pe], bevel=0.0015, segs=3, sharp=25, bevel_mat=1)
    bm = prism(rrect(0.225, 0.155, 0.055, 10), DESK_H - 0.0001, DESK_H + 0.0008)
    transform(bm, Matrix.Translation((bc.x, bc.y, 0)) @ R)
    mesh_object("stand felt", bm, [rubber()], smooth=False)
    ztop = C.z + 0.09
    bm = prism(rrect(0.056, 0.028, 0.009, 6), DESK_H + 0.010, ztop)
    transform(bm, Matrix.Translation((U.x, U.y, 0)) @ R)
    mesh_object("stand column", bm, [pc, pe], bevel=0.002, segs=3, bevel_mat=1)
    # carriage riding on the column's front, holding the hinge and the pivot disc
    bm = prism(rrect(0.066, 0.016, 0.005, 4), C.z - 0.045, C.z + 0.045)
    transform(bm, Matrix.Translation(tuple(C + b * (k - 0.020))) @ Matrix.Translation((0, 0, -C.z)) @ R)
    mesh_object("stand carriage", bm, [pc, pe], bevel=0.002, segs=3, bevel_mat=1)
    rot = Matrix.Rotation(math.radians(m["turn"]), 4, "Z")
    Xn = Matrix.Translation(C) @ rot
    bm = prism(rrect(0.040, 0.036, 0.006, 4), VESA_Y + 0.010, k - 0.028, "y")
    mesh_object("stand hinge", transform(bm, Xn), [pc, pe], bevel=0.002, segs=3, bevel_mat=1)
    bm = cylinder(0.042, VESA_Y + 0.004, VESA_Y + 0.011, 64, axis="y")
    mesh_object("pivot disc", transform(bm, Xn), [pc, pe], bevel=0.0015, segs=2, bevel_mat=1)
    return U


def cables(lay, P, U):
    """Power and video leads: the pair's down the back of the pole, the portrait one's down the back of
    its column; over the back of the bases, off the desk's back edge and into the cable tray."""
    mat = shared("cable", lambda n: _cable(n))
    edge = DESK_D / 2
    for m in lay:
        X = frame_of(m)
        C = Vector(m["centre"])
        b = back_dir(m)
        W, H = panel_dims(m)
        for j, dx in enumerate((-0.03, 0.03)):
            r = 0.0029 if j == 0 else 0.0034
            if m["kind"] == "landscape":
                side = 1 if C.x > P.x else -1
                s0 = X @ Vector((-side * 0.06 + dx * 0.5, BACK + DOME * 0.5, -0.16 * H))
                px = P.x + side * 0.008 + dx * 0.12
                py = P.y + 0.0175 + r
                pts = [s0, s0 + b * 0.03 + Vector((0, 0, -0.03)), Vector((px, py + 0.01, C.z - 0.17)),
                       Vector((px, py, DESK_H + 0.20)), Vector((px, py, DESK_H + 0.06)),
                       Vector((px, py + 0.012, DESK_H + 0.020)), Vector((px + side * 0.004, P.y + 0.05, DESK_H + r)),
                       Vector((px + side * 0.012, edge - 0.012, DESK_H + r))] + into_tray(px + side * 0.014, r)
            else:
                # out of the housing's lower half, round the column's side and down its back, clipped
                # close, then off the back of the base
                tv = Vector((b.y, -b.x, 0))
                s0 = X @ Vector((-0.12 * W, BACK + DOME * 0.5, dx))
                bk = U + b * (0.014 + r + 0.001) + tv * (dx * 0.25)
                sd = U + tv * (0.036 + dx * 0.2) + b * 0.004
                pts = [s0, s0 + b * 0.03 + Vector((0, 0, -0.02)), Vector((sd.x, sd.y, C.z - 0.13)),
                       Vector((bk.x, bk.y, C.z - 0.21)), Vector((bk.x, bk.y, DESK_H + 0.07)),
                       Vector((bk.x, bk.y, DESK_H + 0.03)) + b * 0.006,
                       Vector((0, 0, DESK_H + 0.012 + r)) + Vector((bk.x, bk.y, 0)) + b * 0.03,
                       Vector((0, 0, DESK_H + r)) + Vector((bk.x, bk.y, 0)) + b * 0.075,
                       Vector((bk.x + dx * 0.5 + 0.01, edge - 0.012, DESK_H + r))] + into_tray(bk.x + dx * 0.5 + 0.012, r)
            curve_tube("cable", pts, r, mat)


def into_tray(x, r):
    """Over the back edge, down the back, back in over the tray's lip and onto its floor."""
    edge, under = DESK_D / 2, DESK_H - 0.03
    return [Vector((x, edge + 0.004 + r, DESK_H - 0.008)), Vector((x, edge + 0.008 + r, under - 0.030)),
            Vector((x, TRAY_Y[1] - 0.004, under - TRAY_LIP + 0.012)), Vector((x, TRAY_Y[1] - 0.04, under - TRAY_DROP + 0.004 + r)),
            Vector((x + 0.06, TRAY_Y[0] + 0.03, under - TRAY_DROP + 0.0015 + r))]


def _cable(name):
    m, t = new_material(name)
    principled(t, **{"Base Color": (0.010, 0.010, 0.011, 1), "Roughness": 0.55, "Sheen Weight": 0.1})
    return m


def build():
    lay = monitors_layout()
    for idx, m in enumerate(lay):
        monitor(m, idx)
    P = dual_arm(lay)
    U = portrait_stand(lay[2])
    cables(lay, P, U)
