# The palette: a 40 x 30 cm oval wooden palette with a thumb hole and a finger notch (kidney cut), 6 mm
# plywood darkened by years of linseed oil and scraped-off paint, lying on the floor. Fresh oil colours
# squeezed round the far edge (titanium white, cadmium yellow, cadmium red, dioxazine violet,
# ultramarine, sap green and a muted mixed grey-rose), knife-mixed tints in the middle, and a long
# filbert brush lying across, its bristles loaded with blue.
#
# Local metres: the palette's centre at the origin, its long axis along x, the thumb hole to the front
# left (-x, -y), its underside on the floor and its top at z = T. The dabs are metaballs turned into
# meshes; the mixing area is a height field.
import math, random
import bpy, bmesh
from mathutils import Matrix, Vector, noise
from objects.desk_kit import N, out, M as Mf, V, mix_rgb, mix_f, maprange, xyz, comb, tex, new_material, principled, loft
from objects.easel_kit import WOOD, to_object, revolve, frame

A, B = 0.200, 0.150             # half length, half width of the oval
T = 0.006                        # thickness
NOTCH_A, NOTCH_D, NOTCH_W = math.radians(212), 0.042, 0.28   # the finger notch: where, how deep, how wide
SEED = 11


def radius(a):
    r = 1.0 / math.sqrt((math.cos(a) / A) ** 2 + (math.sin(a) / B) ** 2)
    d = (a - NOTCH_A + math.pi) % (2 * math.pi) - math.pi
    return r - NOTCH_D * math.exp(-(d / NOTCH_W) ** 2)


def outline(n=240, inset=0.0):
    return [((radius(2 * math.pi * k / n) - inset) * math.cos(2 * math.pi * k / n),
             (radius(2 * math.pi * k / n) - inset) * math.sin(2 * math.pi * k / n)) for k in range(n)]


def thumb_hole():
    r = radius(NOTCH_A) - 0.036
    c = Vector((r * math.cos(NOTCH_A), r * math.sin(NOTCH_A)))
    a = NOTCH_A + math.radians(20)
    pts = []
    for k in range(64):
        t = 2 * math.pi * k / 64
        x, y = 0.0185 * math.cos(t), 0.0155 * math.sin(t)
        pts.append((c.x + x * math.cos(a) - y * math.sin(a), c.y + x * math.sin(a) + y * math.cos(a)))
    return pts, c


# ---------------------------------------------------------------- the board

def board(mat):
    """The plywood blank: a filled 2D curve with its edge rounded over (2 mm radius) top and bottom."""
    cu = bpy.data.curves.new("palette", "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = T / 2 - 0.002
    cu.bevel_depth = 0.002
    cu.bevel_resolution = 4
    for pts in (outline(inset=0.002), thumb_hole()[0][::-1]):
        sp = cu.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for p, (x, y) in zip(sp.points, pts):
            p.co = (x, y, 0.0, 1.0)
        sp.use_cyclic_u = True
    tmp = bpy.data.objects.new("palette tmp", cu)
    bpy.context.scene.collection.objects.link(tmp)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.curves.remove(cu)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, T / 2))
    uvl = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        for lp in f.loops:
            c = lp.vert.co
            lp[uvl].uv = (c.x + 0.37, c.y + 0.61 + 0.35 * c.z)
    ob = to_object("palette board", bm, [mat], smooth=True, sharp=60)
    return ob


# ---------------------------------------------------------------- paint

PAINTS = {   # name: linear colour (masstone), roughness, how far light gets into it
    "titanium white": ((0.80, 0.79, 0.75), 0.16, 0.25),
    "cadmium yellow": ((0.88, 0.50, 0.012), 0.17, 0.12),
    "cadmium red": ((0.58, 0.028, 0.014), 0.17, 0.08),
    "dioxazine violet": ((0.060, 0.012, 0.085), 0.14, 0.03),
    "ultramarine": ((0.024, 0.022, 0.23), 0.14, 0.04),
    "sap green": ((0.040, 0.085, 0.012), 0.15, 0.03),
    "grey rose": ((0.36, 0.26, 0.24), 0.20, 0.12),
}
VIS = 0.66        # a metaball chain's visible radius, as a share of its elements' radius


def paint_material(name, colour, rough, sss, ribs=None):
    """Fresh oil colour: glossy with the oil, the light going a little way into the lighter pigments,
    a faintly uneven skin with the odd air pit. ribs: the direction (radians) a bead was squeezed in;
    the nozzle's mouth leaves faint grooves along it."""
    m, t = new_material("paint " + name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    fine = out(N(t, "ShaderNodeTexNoise", co, Scale=900.0, Detail=3.0, Roughness=0.6), "Factor")
    blot = out(N(t, "ShaderNodeTexNoise", co, Scale=160.0, Detail=3.0), "Factor")
    pits = out(N(t, "ShaderNodeTexVoronoi", co, Scale=420.0, Randomness=1.0), "Distance")
    pit = maprange(t, pits, 0.06, 0.02, 0.0, 1.0)
    pit = Mf(t, "MULTIPLY", pit, maprange(t, blot, 0.55, 0.7, 0.0, 1.0))
    col = mix_rgb(t, Mf(t, "MULTIPLY", maprange(t, blot, 0.3, 0.7, 0.0, 1.0), 0.10), (*colour, 1),
                  (colour[0] * 0.85, colour[1] * 0.85, colour[2] * 0.85, 1))
    r = Mf(t, "ADD", rough, maprange(t, blot, 0.3, 0.75, -0.04, 0.10))
    bump = N(t, "ShaderNodeBump", Strength=0.25, Distance=0.00012, Height=fine)
    bump = N(t, "ShaderNodeBump", Strength=0.6, Distance=0.0002, Height=Mf(t, "MULTIPLY", pit, -1.0), Normal=out(bump))
    if ribs is not None:
        x, y, z = xyz(t, co)
        across = Mf(t, "ADD", Mf(t, "MULTIPLY", x, -math.sin(ribs)), Mf(t, "MULTIPLY", y, math.cos(ribs)))
        wob = out(N(t, "ShaderNodeTexNoise", co, Scale=90.0, Detail=2.0), "Factor")
        rib = Mf(t, "SINE", Mf(t, "MULTIPLY", Mf(t, "ADD", across, Mf(t, "MULTIPLY", wob, 0.0015)), 2 * math.pi / 0.0013))
        bump = N(t, "ShaderNodeBump", Strength=0.35, Distance=0.00008, Height=rib, Normal=out(bump))
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.55,
                     "Subsurface Weight": sss, "Subsurface Radius": (colour[0] + 0.05, colour[1] + 0.05, colour[2] + 0.05),
                     "Subsurface Scale": 0.0015, "Coat Weight": 0.15, "Coat Roughness": 0.06, "Coat IOR": 1.48})
    return m


def smear_material(name, dried=False):
    """Paint laid down by knife or brush, its colours in per-vertex attributes: c1 the body, c2 and c3
    streaked through it along the stroke (flow = the stroke's direction and a seed). Dried paint is
    duller and a little lighter, its skin finely crazed."""
    m, t = new_material(name)
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    attr = lambda n: out(N(t, "ShaderNodeAttribute", _attribute_name=n, _attribute_type="GEOMETRY"), "Vector")
    c1, c2, c3, flow = attr("c1"), attr("c2"), attr("c3"), attr("flow")
    fx, fy, seed = xyz(t, flow)
    along = Mf(t, "ADD", Mf(t, "MULTIPLY", x, fx), Mf(t, "MULTIPLY", y, fy))
    across = Mf(t, "SUBTRACT", Mf(t, "MULTIPLY", y, fx), Mf(t, "MULTIPLY", x, fy))
    sv = comb(t, Mf(t, "MULTIPLY", along, 22.0), Mf(t, "MULTIPLY", across, 240.0), seed)
    s2 = out(N(t, "ShaderNodeTexNoise", sv, Scale=1.0, Detail=4.0, Roughness=0.55, Distortion=0.6), "Factor")
    s3 = out(N(t, "ShaderNodeTexNoise", V(t, "ADD", sv, (5.3, 1.1, 0.0)), Scale=1.3, Detail=3.0, Roughness=0.5), "Factor")
    col = mix_rgb(t, maprange(t, s2, 0.56, 0.70, 0.0, 0.85), c1, c2)
    col = mix_rgb(t, maprange(t, s3, 0.64, 0.72, 0.0, 0.75), col, c3)
    fine = out(N(t, "ShaderNodeTexNoise", co, Scale=800.0, Detail=3.0), "Factor")
    # where it thins out at its edges the wood shows through, raggedly
    rag = out(N(t, "ShaderNodeTexNoise", co, Scale=1400.0, Detail=2.0), "Factor")
    alpha = maprange(t, Mf(t, "ADD", Mf(t, "SUBTRACT", z, T), Mf(t, "MULTIPLY", Mf(t, "SUBTRACT", rag, 0.5), 0.00012)),
                     0.00002, 0.00016, 0.0, 1.0)
    if dried:
        crack = out(N(t, "ShaderNodeTexVoronoi", co, Scale=900.0, Randomness=1.0, _feature="DISTANCE_TO_EDGE"), "Distance")
        cr = maprange(t, crack, 0.0, 0.04, 1.0, 0.0)
        col = mix_rgb(t, Mf(t, "MULTIPLY", cr, 0.35), col, (0.02, 0.015, 0.01, 1))
        bump = N(t, "ShaderNodeBump", Strength=0.3, Distance=0.00008, Height=Mf(t, "ADD", fine, Mf(t, "MULTIPLY", cr, -0.8)))
        principled(t, **{"Base Color": col, "Roughness": Mf(t, "ADD", 0.52, Mf(t, "MULTIPLY", fine, 0.18)),
                         "Normal": out(bump), "Specular IOR Level": 0.5, "Alpha": alpha})
    else:
        bump = N(t, "ShaderNodeBump", Strength=0.2, Distance=0.0001, Height=fine)
        bump = N(t, "ShaderNodeBump", Strength=0.15, Distance=0.0002, Height=s2, Normal=out(bump))
        principled(t, **{"Base Color": col, "Roughness": Mf(t, "ADD", 0.17, Mf(t, "MULTIPLY", s3, 0.08)),
                         "Normal": out(bump), "Specular IOR Level": 0.55, "Subsurface Weight": 0.10, "Alpha": alpha,
                         "Subsurface Radius": (0.6, 0.6, 0.6), "Subsurface Scale": 0.001, "Coat Weight": 0.1,
                         "Coat Roughness": 0.08})
    return m


def blob_mesh(name, elements, res=0.00055, smooth=2, jitter=0.00015, seed=0):
    """A metaball surface from (centre, radius, (sx, sy, sz), negative) elements, as a bmesh."""
    # metaballs will not polygonise finer than 5 mm, so they are built ten times too large and scaled down
    K = 10.0
    mb = bpy.data.metaballs.new(name)
    mb.resolution = res * K
    mb.render_resolution = res * K
    mb.threshold = 0.6
    for co, r, size, neg in elements:
        e = mb.elements.new(type="ELLIPSOID")
        e.co = Vector(co) * K
        e.radius = r * K
        e.size_x, e.size_y, e.size_z = size
        e.stiffness = 2.0
        e.use_negative = neg
    ob = bpy.data.objects.new(name, mb)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.metaballs.remove(mb)
    bm = bmesh.new()
    bm.from_mesh(me)
    bpy.data.meshes.remove(me)
    bmesh.ops.scale(bm, vec=(1 / K, 1 / K, 1 / K), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=res * 0.05)
    for _ in range(smooth):
        bmesh.ops.smooth_vert(bm, verts=bm.verts, factor=0.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.normal_update()
    off = Vector((seed * 3.1, seed * 1.7, seed * 2.3))
    for v in bm.verts:
        v.co += v.normal * noise.noise(v.co * 380.0 + off) * jitter
    return bm


def _el(p, r_vis, sz=0.78, neg=False):
    return ((p.x, p.y, p.z), r_vis / VIS, (1.0, 1.0, sz), neg)


def coil(c, r0, turns, a0, rnd):
    """Paint squeezed in a small spiral: the bead lies in a ring and climbs onto itself toward the
    middle, where the tube was lifted away in a soft peak."""
    els = []
    n = int(22 * turns)
    for k in range(n + 1):
        t = k / n
        a = a0 + 2 * math.pi * turns * t
        rho = r0 * (1.25 - 1.05 * t)
        rr = r0 * (1.0 - 0.32 * t) * rnd.uniform(0.95, 1.05)
        z = T + 0.50 * rr + r0 * 1.05 * t
        els.append(_el(Vector((c.x + rho * math.cos(a), c.y + rho * math.sin(a), z)), rr))
        if t < 0.7:
            els.append(_el(Vector((c.x + rho * math.cos(a), c.y + rho * math.sin(a), T + 0.10 * rr)), rr * 1.1, 0.30))
    top = els[-1][0][2]
    lean = Vector((math.cos(a0 + 0.6), math.sin(a0 + 0.6), 0)) * r0 * 0.6
    for h, s in ((0.30, 0.58), (0.52, 0.40), (0.66, 0.24)):
        els.append(_el(Vector((c.x, c.y, top)) + lean * h + Vector((0, 0, r0 * h)), r0 * s, 0.9))
    return els


def worm(p0, ang, length, r0, bend, rnd):
    """Paint squeezed in a line: a fat bead along a gentle curve, slumped under its own weight, ending
    where the tube was lifted in a little peak folded back over the bead."""
    els, pts = [], [Vector(p0)]
    n = max(4, int(length / (r0 * 0.5)))
    for k in range(1, n + 1):
        a = ang + bend * (k / n - 0.5)
        pts.append(pts[-1] + Vector((math.cos(a), math.sin(a), 0)) * (length / n))
    for k, p in enumerate(pts):
        t = k / n
        rr = r0 * (0.80 + 0.24 * math.sin(math.pi * min(1.0, 0.25 + t))) * rnd.uniform(0.88, 1.12)
        side = Vector((-math.sin(ang), math.cos(ang), 0)) * r0 * rnd.uniform(-0.12, 0.12)
        els.append(_el(p + side + Vector((0, 0, T + 0.40 * rr)), rr, 0.68))
        # where it touches the palette the bead has spread a little under its weight
        els.append(_el(p + side + Vector((0, 0, T + 0.10 * rr)), rr * 1.12, 0.30))
    back = (pts[-3] - pts[-1]).normalized()
    for h, f, s in ((0.45, 0.25, 0.70), (0.72, 0.50, 0.50), (0.90, 0.72, 0.32), (0.98, 0.88, 0.18)):
        els.append(_el(pts[-1] + back * (r0 * f) + Vector((0, 0, T + r0 * h)), r0 * s, 0.85))
    return els, pts


def dent(p, r0, depth=0.55):
    """A scoop where a brush took paint."""
    return _el(p + Vector((0, 0, r0 * (1.6 - depth))), r0 * 1.05, 0.8, neg=True)


def drag_field(p, ang, length, width, thick, seed):
    """A trail where a loaded brush dragged colour out of the dab: a band tapering away from it, thinning
    to nothing, grooved along its length by the hairs."""
    ca, sa = math.cos(ang), math.sin(ang)

    def f(x, y):
        dx, dy = x - p.x, y - p.y
        al = dx * ca + dy * sa
        ac = -dx * sa + dy * ca
        if al < -0.002 or al > length:
            return None
        t = max(0.0, al) / length
        half = width / 2 * (1.0 - 0.55 * t) * (1.0 + 0.15 * noise.noise(Vector((al * 80, seed, 0))))
        e = abs(ac) / half
        if e > 1.0:
            return None
        # the hairs leave it in streaks that break up toward the end, where the brush ran dry
        hair = noise.noise(Vector((ac * 1500, al * 18, seed)))
        broken = min(1.0, max(0.0, (hair + 0.45 - 0.9 * t) / 0.25))
        h = thick * (1.0 - t) ** 0.6 * (1.0 - e ** 3) * broken * (0.75 + 0.25 * hair)
        if al < 0:
            h *= 1.0 + al / 0.002
        return (h, None) if h > 0.00003 else None
    return f


def lumps_field(c, r0, rnd, seed):
    """Old colour dried where the dab always goes: a crust of hard lumps and flattened smears."""
    bumps = []
    for k in range(7):
        a = rnd.uniform(0, 2 * math.pi)
        d = r0 * rnd.uniform(0.0, 1.6)
        bumps.append((c.x + d * math.cos(a), c.y + d * math.sin(a), r0 * rnd.uniform(0.6, 1.2),
                      rnd.uniform(0.0003, 0.0010)))

    def f(x, y):
        g = 0.0
        for bx, by, br, bh in bumps:
            q = ((x - bx) ** 2 + (y - by) ** 2) / (br * br)
            if q < 9:
                g += bh * math.exp(-q ** 1.3)
        g *= 1.0 + 0.35 * noise.noise(Vector((x * 300, y * 300, seed)))
        if g < 0.00004:
            return None
        return g, None
    return f


def heightfield(name, fn, bounds, step, mat, tuck=0.0003):
    """A height field over a rectangle: fn(x, y) -> (height above the palette, {attribute: vector}) or
    None. Its open edge tucks just under the palette's top so it has no visible lip."""
    x0, x1, y0, y1 = bounds
    nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
    samples = {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            r = fn(x0 + i * step, y0 + j * step)
            if r is not None:
                samples[i, j] = r
    bm = bmesh.new()
    keys = sorted({k for _, at in samples.values() for k in at})
    layers = {k: bm.verts.layers.float_vector.new(k) for k in keys}
    grid = {}
    for (i, j), (h, attrs) in samples.items():
        v = bm.verts.new((x0 + i * step, y0 + j * step, T + h))
        for k, val in attrs.items():
            v[layers[k]] = val
        grid[i, j] = v
    for j in range(ny):
        for i in range(nx):
            q = [grid.get((i, j)), grid.get((i + 1, j)), grid.get((i + 1, j + 1)), grid.get((i, j + 1))]
            if all(q):
                bm.faces.new(q)
    for v in [v for v in bm.verts if not v.link_faces]:
        bm.verts.remove(v)
    for v in bm.verts:
        if v.is_boundary:
            v.co.z = T - tuck
    return to_object(name, bm, [mat], smooth=True, sharp=180, recalc=False)


def knife_field(passes, plateau, ridge=0.35, seed=0.0):
    """The height of paint worked with a knife: passes of (centre, angle, half length, half width,
    amount) add up, the knife flattens the top (the blade's tilt and chatter in it), and paint pushed
    aside stands in a ridge round the flat."""
    def f(x, y):
        near = False
        for (cx, cy), ang, la, wa, amt in passes:
            if abs(x - cx) < la * 1.6 + 0.004 and abs(y - cy) < la * 1.6 + 0.004:
                near = True
                break
        if not near:
            return None
        wob = Vector((noise.noise(Vector((x * 70, y * 70, seed))), noise.noise(Vector((x * 70 + 9.1, y * 70, seed))), 0)) * 0.0035
        best, g = 0.0, 0.0
        for (cx, cy), ang, la, wa, amt in passes:
            dx, dy = x + wob.x - cx, y + wob.y - cy
            al = dx * math.cos(ang) + dy * math.sin(ang)
            ac = -dx * math.sin(ang) + dy * math.cos(ang)
            q = (al / la) ** 2 + (ac / wa) ** 2
            g += amt * math.exp(-q ** 1.6)
        u = g / plateau
        if u < 0.04:
            return None
        h = plateau * math.tanh(u)
        h += plateau * ridge * math.exp(-((u - 1.15) / 0.22) ** 2) * (0.7 + 0.6 * noise.noise(Vector((x * 400, y * 400, seed))))
        h += plateau * 0.06 * noise.noise(Vector((x * 900, y * 900, seed + 3)))
        return max(h, 0.00002), u
    return f


def dabs():
    """The colours round the far edge, each squeezed its own way, most on an old crust of itself."""
    rnd = random.Random(SEED)
    spots = [  # name, angle round the palette (deg), kind, bead radius, extras
        ("titanium white", 150, "coil", 0.0052, dict(turns=1.45, dent=True, tail=(-28, 0.040))),
        ("cadmium yellow", 125, "worm", 0.0050, dict(length=0.032)),
        ("cadmium red", 101, "coil", 0.0042, dict(turns=1.2)),
        ("dioxazine violet", 79, "worm", 0.0044, dict(length=0.024)),
        ("ultramarine", 56, "worm", 0.0050, dict(length=0.030, dent=True, tail=(22, 0.034))),
        ("sap green", 31, "coil", 0.0040, dict(turns=1.1)),
    ]
    obs = []
    crust_mat = smear_material("paint dried", dried=True)
    fresh_mat = smear_material("paint dragged")
    for i, (name, deg, kind, r0, ex) in enumerate(spots):
        a = math.radians(deg)
        rr = radius(a) - 0.030
        c = Vector((rr * math.cos(a), rr * math.sin(a), 0))
        along = None
        if kind == "coil":
            els = coil(c, r0, ex["turns"], rnd.uniform(0, 6.28), rnd)
            pts = [c]
        else:
            along = a - math.pi / 2 + rnd.uniform(-0.3, 0.3)
            L = ex["length"]
            p0 = c - Vector((math.cos(along), math.sin(along), 0)) * (L / 2)
            els, pts = worm(p0, along, L, r0, rnd.uniform(-0.7, 0.7), rnd)
        if ex.get("dent"):
            p = pts[len(pts) // 2] if len(pts) > 1 else c + Vector((r0 * 0.6, 0, 0))
            els.append(dent(Vector((p.x, p.y, T)), r0))
        bm = blob_mesh("paint-" + name.replace(" ", "-"), els, seed=i)
        col, rough, sss = PAINTS[name]
        obs.append(to_object("paint " + name, bm, [paint_material(name, col, rough, sss, along)], smooth=True, sharp=180,
                             recalc=False))
        R = r0 * 4.0
        # the old crust under it: the same colour gone dull and dirty, in hard lumps
        dull = tuple(0.55 * ci + 0.45 * g for ci, g in zip(col, (0.12, 0.10, 0.08)))
        at = {"c1": dull, "c2": tuple(ci * 0.75 for ci in dull), "c3": (0.30, 0.27, 0.23), "flow": (1.0, 0.0, i * 1.7)}
        obs.append(heightfield(f"paint crust {i}", _with(lumps_field(c, r0, rnd, i * 2.3), at),
                               (c.x - R, c.x + R, c.y - R, c.y + R), 0.0006, crust_mat))
        if ex.get("tail"):
            ta, tl = ex["tail"]
            ang = a + math.pi + math.radians(ta)
            at = {"c1": col, "c2": tuple(ci * 0.8 for ci in col), "c3": col,
                  "flow": (math.cos(ang), math.sin(ang), i * 2.9)}
            p0 = c + Vector((math.cos(ang), math.sin(ang), 0)) * r0 * 0.6
            box = (min(p0.x, p0.x + math.cos(ang) * tl) - 0.012, max(p0.x, p0.x + math.cos(ang) * tl) + 0.012,
                   min(p0.y, p0.y + math.sin(ang) * tl) - 0.012, max(p0.y, p0.y + math.sin(ang) * tl) + 0.012)
            obs.append(heightfield(f"paint drag {i}", _with(drag_field(p0, ang, tl, r0 * 2.4, 0.0005, i * 1.3), at),
                                   box, 0.0005, fresh_mat))
    return obs


def _with(f, attrs):
    """A field function that returns these attributes with its height."""
    def g(x, y):
        r = f(x, y)
        return None if r is None else (r[0], attrs)
    return g


SMEARS = [  # passes, plateau, ridge, colours (body, streak, streak)
    ([((-0.046, 0.016), math.radians(18), 0.030, 0.012, 0.0024), ((-0.028, 0.006), math.radians(-12), 0.024, 0.010, 0.0018)],
     0.0010, 0.35, ((0.11, 0.16, 0.40), (0.62, 0.62, 0.60), (0.03, 0.03, 0.24))),
    ([((0.012, -0.040), math.radians(160), 0.028, 0.012, 0.0022), ((0.028, -0.028), math.radians(138), 0.020, 0.009, 0.0016)],
     0.0009, 0.40, ((0.52, 0.24, 0.12), (0.72, 0.62, 0.50), (0.45, 0.04, 0.02))),
    ([((-0.010, 0.050), math.radians(4), 0.022, 0.009, 0.0018)],
     0.0008, 0.30, ((0.15, 0.19, 0.10), (0.28, 0.20, 0.26), (0.62, 0.62, 0.58))),
    ([((0.050, 0.012), math.radians(74), 0.026, 0.008, 0.0008)],
     0.0004, 0.25, ((0.13, 0.075, 0.18), (0.45, 0.42, 0.42), (0.05, 0.012, 0.08))),
    # the grey rose: a heap knife-mixed at the edge from white, red and green
    ([((0.158, 0.012), math.radians(80), 0.014, 0.010, 0.0070), ((0.150, -0.004), math.radians(40), 0.010, 0.008, 0.0050)],
     0.0042, 0.30, ((0.36, 0.26, 0.24), (0.50, 0.42, 0.40), (0.22, 0.18, 0.16))),
]


def smears(mat):
    """Tints mixed with a knife in the middle, and the grey-rose heap at the edge: one height field, each
    point taking its colours and stroke direction from the smear that is thickest there."""
    fields = [(knife_field(p, pl, rg, seed=k * 2.7), p, cols) for k, (p, pl, rg, cols) in enumerate(SMEARS)]

    def fn(x, y):
        best = None
        for k, (f, passes, cols) in enumerate(fields):
            r = f(x, y)
            if r is not None and (best is None or r[0] > best[0]):
                ang = passes[0][1]
                best = (r[0], {"c1": cols[0], "c2": cols[1], "c3": cols[2],
                               "flow": (math.cos(ang), math.sin(ang), k * 3.1)})
        return best
    return heightfield("paint smears", fn, (-0.115, 0.185, -0.090, 0.075), 0.0006, mat)


def palette_wood():
    """Plywood with a fine-grained face veneer, years of linseed oil gone amber in it, its face clouded with old paint:
    films and crusts of dried colour with crisp edges, thickest in the middle where the mixing is done
    and thinning toward the rim the hand holds; the edge shows the plies."""
    m, t = new_material("palette wood")
    tc = N(t, "ShaderNodeTexCoord")
    uv, co, nrm = out(tc, "UV"), out(tc, "Object"), out(tc, "Normal")
    x, y, z = xyz(t, co)
    nx, ny, nz = xyz(t, nrm)
    diff = tex(t, WOOD + "diff_2k.jpg", uv)
    rgh = tex(t, WOOD + "rough_2k.jpg", uv, False)
    norm = mix_rgb(t, 1.0, out(diff), (1 / 0.76, 1 / 0.51, 1 / 0.35, 1), "MULTIPLY")
    g = N(t, "ShaderNodeGamma", Color=norm, Gamma=1.8)
    wood = mix_rgb(t, 1.0, out(g), (0.25, 0.125, 0.050, 1), "MULTIPLY")
    rad = V(t, "LENGTH", comb(t, Mf(t, "DIVIDE", x, A), Mf(t, "DIVIDE", y, B)))
    # oil and handling: darker toward the middle, a soft blotchiness
    blotch = out(N(t, "ShaderNodeTexNoise", co, Scale=14.0, Detail=3.0), "Factor")
    wood = mix_rgb(t, Mf(t, "ADD", maprange(t, rad, 0.9, 0.2, 0.0, 0.35), maprange(t, blotch, 0.4, 0.7, 0.0, 0.2)),
                   wood, (0.10, 0.05, 0.02, 1))
    # old paint: a grey-brown haze of scraped-off films, thickest toward the middle and streaked the way
    # the knife went; on it, crisp patches and specks of dried colour, mostly muted
    w1 = out(N(t, "ShaderNodeTexNoise", co, Scale=7.0, Detail=5.0, Roughness=0.6), "Factor")
    w2 = out(N(t, "ShaderNodeTexNoise", V(t, "ADD", co, (3.1, 1.7, 0)), Scale=24.0, Detail=6.0, Roughness=0.62), "Factor")
    w3 = out(N(t, "ShaderNodeTexNoise", V(t, "ADD", co, (8.4, 4.2, 0)), Scale=70.0, Detail=4.0, Roughness=0.6), "Factor")
    rot = N(t, "ShaderNodeMapping", co, Rotation=(0, 0, 0.45)).outputs[0]
    knife = out(N(t, "ShaderNodeTexNoise", V(t, "MULTIPLY", rot, (1.0, 14.0, 1.0)), Scale=18.0, Detail=3.0), "Factor")
    centre = maprange(t, rad, 1.0, 0.40, 0.0, 1.0)
    haze = Mf(t, "MULTIPLY", maprange(t, Mf(t, "ADD", w1, Mf(t, "MULTIPLY", knife, 0.08)), 0.48, 0.70, 0.0, 0.6), centre)
    hazec = mix_rgb(t, maprange(t, w2, 0.3, 0.7, 0.0, 1.0), (0.20, 0.17, 0.14, 1), (0.30, 0.27, 0.23, 1))
    film = maprange(t, Mf(t, "ADD", w2, Mf(t, "MULTIPLY", centre, 0.08)), 0.645, 0.655, 0.0, 1.0)
    specks = maprange(t, w3, 0.735, 0.745, 0.0, 1.0)
    hue = out(N(t, "ShaderNodeTexNoise", V(t, "ADD", co, (7.7, 2.2, 0)), Scale=6.0, Detail=2.0), "Factor")
    hue2 = out(N(t, "ShaderNodeTexNoise", V(t, "ADD", co, (1.3, 9.2, 0)), Scale=11.0, Detail=2.0), "Factor")

    def oldcolours(fac):
        ramp = N(t, "ShaderNodeValToRGB", Fac=fac)
        ramp.color_ramp.interpolation = "CONSTANT"
        els = ramp.color_ramp.elements
        stops = [(0.0, (0.34, 0.31, 0.27)), (0.38, (0.24, 0.10, 0.06)), (0.44, (0.12, 0.15, 0.24)), (0.49, (0.34, 0.25, 0.10)),
                 (0.54, (0.46, 0.43, 0.38)), (0.59, (0.14, 0.16, 0.08)), (0.64, (0.25, 0.18, 0.21)), (0.70, (0.12, 0.07, 0.04))]
        els[0].position, els[0].color = stops[0][0], (*stops[0][1], 1)
        els[1].position, els[1].color = 1.0, (0.40, 0.37, 0.33, 1)
        for pos, c in stops[1:]:
            els.new(pos).color = (*c, 1)
        return out(ramp)

    c1, c2 = oldcolours(hue), oldcolours(hue2)
    grain = out(N(t, "ShaderNodeTexNoise", co, Scale=300.0, Detail=3.0), "Factor")
    c1 = mix_rgb(t, Mf(t, "MULTIPLY", maprange(t, grain, 0.4, 0.7, 0.0, 1.0), 0.20), c1, (0.08, 0.06, 0.05, 1))
    top = mix_rgb(t, haze, wood, hazec)
    top = mix_rgb(t, Mf(t, "MULTIPLY", film, 0.95), top, c1)
    top = mix_rgb(t, specks, top, c2)
    film2 = haze
    # the edge: the plies, alternate ones a little darker where they run across the grain
    ply = Mf(t, "SINE", Mf(t, "MULTIPLY", z, 2 * math.pi * 5 / T))
    edgecol = mix_rgb(t, maprange(t, ply, -0.4, 0.4, 0.0, 1.0), (0.26, 0.15, 0.07, 1), (0.40, 0.25, 0.12, 1))
    edgem = maprange(t, Mf(t, "ABSOLUTE", nz), 0.5, 0.2, 0.0, 1.0)
    col = mix_rgb(t, edgem, top, edgecol)
    paint = Mf(t, "MAXIMUM", Mf(t, "MAXIMUM", film, Mf(t, "MULTIPLY", film2, 0.7)), specks)
    r = maprange(t, out(rgh), 0.2, 0.9, 0.46, 0.62)
    r = mix_f(t, paint, r, Mf(t, "ADD", 0.36, Mf(t, "MULTIPLY", grain, 0.2)))
    relief = Mf(t, "ADD", Mf(t, "ADD", film, film2), Mf(t, "MULTIPLY", grain, paint))
    bump = N(t, "ShaderNodeBump", Strength=0.5, Distance=0.00010, Height=relief)
    bump = N(t, "ShaderNodeBump", Strength=0.15, Distance=0.0001, Height=out(N(t, "ShaderNodeRGBToBW", Color=out(diff))),
             Normal=out(bump))
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.4})
    return m


# ---------------------------------------------------------------- the brush

def brush():
    """A long-handled filbert, 30 cm: a lacquered beech handle swelling behind the ferrule and tapering
    to the end, a seamless nickel ferrule crimped twice and pressed flat, hog bristles loaded with
    ultramarine and white. Built along +z from the bristle tip, then laid on the palette."""
    obs = []
    TIP, BR, FE, HA = 0.0, 0.020, 0.038, 0.215     # bristle length, ferrule length, handle length
    z_f0 = BR                    # ferrule starts
    z_h0 = BR + FE - 0.010       # handle goes 10 mm into the ferrule
    hprof = []
    for k in range(25):
        s = k / 24
        L = HA
        if s < 0.25:
            r = 0.0040 + (0.0049 - 0.0040) * math.sin(s / 0.25 * math.pi / 2)
        else:
            u = (s - 0.25) / 0.75
            r = 0.0049 - (0.0049 - 0.0021) * (u ** 1.3)
        hprof.append((r, z_h0 + s * L))
    hprof = [(0.0, z_h0)] + hprof + [(0.0016, z_h0 + HA + 0.0012), (0.0, z_h0 + HA + 0.0016)]
    handle = to_object("brush handle", revolve(hprof, 40), [brush_handle_material()], smooth=True, sharp=80)
    obs.append(handle)
    # ferrule: round at the handle, pressed to a flat oval at the bristles, two crimp rings
    secs = []
    nseg = 48
    for k in range(13):
        s = k / 12
        z = z_f0 + s * FE
        flat = max(0.0, 1.0 - s / 0.65)
        flat = flat * flat * (3 - 2 * flat)
        ax = 0.0043 + 0.0016 * flat
        ay = 0.0043 - 0.0021 * flat
        crimp = 1.0
        for zc in (0.78, 0.86):
            crimp -= 0.035 * math.exp(-((s - zc) / 0.02) ** 2)
        secs.append(([(ax * crimp * math.cos(2 * math.pi * i / nseg), ay * crimp * math.sin(2 * math.pi * i / nseg))
                      for i in range(nseg)], z))
    obs.append(to_object("brush ferrule", loft(secs, "z"), [ferrule_material()], smooth=True, sharp=80))
    # bristles: a flat bundle that swells a little out of the ferrule and closes to an oval tip
    secs = []
    for k in range(15):
        s = k / 14                    # 0 at the ferrule, 1 at the tip
        z = z_f0 + 0.002 - s * (BR + 0.002)
        w = 0.0057 * (1.0 + 0.06 * math.sin(s * math.pi)) * math.sqrt(max(0.0, 1 - (max(0.0, s - 0.45) / 0.56) ** 2.2))
        h = 0.0021 * (1.0 + 0.10 * math.sin(s * math.pi * 0.8)) * (1.0 - 0.55 * s ** 2)
        w, h = max(w, 0.0004), max(h, 0.0003)
        secs.append(([(w * math.cos(2 * math.pi * i / nseg), h * math.sin(2 * math.pi * i / nseg)) for i in range(nseg)], z))
    bm = loft(secs, "z")
    # a lump of the colour it last took up, worked into one face near the tip
    for v in bm.verts:
        s = (z_f0 - v.co.z) / BR
        if v.co.y > 0 and 0.35 < s < 1.0:
            v.co.y += 0.0009 * math.sin((s - 0.35) / 0.65 * math.pi) * (1 - abs(v.co.x) / 0.006)
    obs.append(to_object("brush bristles", bm, [bristle_material(BR, z_f0)], smooth=True, sharp=80))
    return obs


def brush_handle_material():
    m, t = new_material("brush handle")
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    # beech under a deep red lacquer, the end dipped and left natural
    uvv = comb(t, Mf(t, "MULTIPLY", z, 1.0), Mf(t, "ADD", Mf(t, "MULTIPLY", x, 3.0), 0.31), 0.0)
    diff = tex(t, WOOD + "diff_2k.jpg", uvv)
    lum = out(N(t, "ShaderNodeRGBToBW", Color=out(diff)))
    lac = mix_rgb(t, maprange(t, lum, 0.45, 0.75, 0.0, 1.0), (0.16, 0.012, 0.008, 1), (0.30, 0.03, 0.015, 1))
    bare = mix_rgb(t, maprange(t, lum, 0.45, 0.75, 0.0, 1.0), (0.42, 0.24, 0.11, 1), (0.58, 0.36, 0.18, 1))
    dip = maprange(t, z, 0.238, 0.2392, 0.0, 1.0)
    col = mix_rgb(t, dip, lac, bare)
    # a smear of blue where a hand put it down
    sm = out(N(t, "ShaderNodeTexNoise", co, Scale=120.0, Detail=3.0), "Factor")
    smear = Mf(t, "MULTIPLY", maprange(t, sm, 0.62, 0.68, 0.0, 1.0), maprange(t, z, 0.07, 0.085, 0.0, 1.0))
    smear = Mf(t, "MULTIPLY", smear, maprange(t, z, 0.11, 0.095, 0.0, 1.0))
    col = mix_rgb(t, smear, col, (0.10, 0.12, 0.40, 1))
    r = mix_f(t, dip, 0.12, 0.5)
    principled(t, **{"Base Color": col, "Roughness": r, "Specular IOR Level": 0.5, "Coat Weight": Mf(t, "SUBTRACT", 1.0, dip),
                     "Coat Roughness": 0.05, "Coat IOR": 1.5})
    return m


def ferrule_material():
    m, t = new_material("brush ferrule")
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    streak = out(N(t, "ShaderNodeTexNoise", V(t, "MULTIPLY", co, (40.0, 40.0, 1.0)), Scale=400.0, Detail=2.0), "Factor")
    # paint has crept onto the ferrule's lower end
    sm = out(N(t, "ShaderNodeTexNoise", co, Scale=300.0, Detail=3.0), "Factor")
    paint = Mf(t, "MULTIPLY", maprange(t, z, 0.030, 0.022, 0.0, 1.0), maprange(t, sm, 0.45, 0.55, 0.0, 1.0))
    col = mix_rgb(t, paint, (0.70, 0.70, 0.70, 1), (0.20, 0.25, 0.55, 1))
    principled(t, **{"Base Color": col, "Metallic": Mf(t, "SUBTRACT", 1.0, paint),
                     "Roughness": Mf(t, "ADD", 0.16, Mf(t, "MULTIPLY", streak, 0.10)), "Normal":
                     out(N(t, "ShaderNodeBump", Strength=0.05, Distance=0.00002, Height=streak))})
    return m


def bristle_material(BR, z_f0):
    """Hog bristle, creamy and stiff, every hair its own line; loaded with blue from the tip back."""
    m, t = new_material("brush bristles")
    co = out(N(t, "ShaderNodeTexCoord"), "Object")
    x, y, z = xyz(t, co)
    hair = out(N(t, "ShaderNodeTexNoise", V(t, "MULTIPLY", co, (1.0, 1.0, 0.015)), Scale=2500.0, Detail=2.0), "Factor")
    s = maprange(t, z, z_f0, z_f0 - BR, 0.0, 1.0)
    load = maprange(t, Mf(t, "ADD", s, Mf(t, "MULTIPLY", hair, 0.25)), 0.38, 0.62, 0.0, 1.0)
    hairc = mix_rgb(t, maprange(t, hair, 0.35, 0.7, 0.0, 1.0), (0.42, 0.34, 0.22, 1), (0.72, 0.62, 0.44, 1))
    mixw = out(N(t, "ShaderNodeTexNoise", co, Scale=500.0, Detail=3.0), "Factor")
    blue = mix_rgb(t, maprange(t, mixw, 0.35, 0.7, 0.0, 1.0), (0.05, 0.07, 0.38, 1), (0.42, 0.48, 0.72, 1))
    col = mix_rgb(t, load, hairc, blue)
    r = mix_f(t, load, 0.55, 0.16)
    bump = N(t, "ShaderNodeBump", Strength=mix_f(t, load, 0.6, 0.15), Distance=0.0001, Height=hair)
    principled(t, **{"Base Color": col, "Roughness": r, "Normal": out(bump), "Specular IOR Level": 0.5,
                     "Coat Weight": Mf(t, "MULTIPLY", load, 0.4), "Coat Roughness": 0.08,
                     "Anisotropic": Mf(t, "MULTIPLY", Mf(t, "SUBTRACT", 1.0, load), 0.5)})
    return m


# ---------------------------------------------------------------- build

def build():
    board(palette_wood())
    dabs()
    smears(smear_material("paint mixed"))
    # the brush lies across from the front right to the back left, its bristles resting in the mixing:
    # local z (tip to handle end) along -d, local y up so the flat of the bristles lies flat; it rests on
    # the swell of the handle and tips forward until the bristles touch
    parts = brush()
    ang = math.radians(152)
    tip = Vector((-0.020, 0.010, 0.0))
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    base = frame(tip + Vector((0, 0, T + 0.0049)), -d, (d.y, -d.x, 0.0))
    zb, drop = 0.102, 0.0028
    tilt = Matrix.Translation((0, 0, zb)) @ Matrix.Rotation(-math.atan2(drop, zb), 4, "X") @ Matrix.Translation((0, 0, -zb))
    for o in parts:
        o.matrix_world = base @ tilt
