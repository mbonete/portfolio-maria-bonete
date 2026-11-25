# The conga's materials: amber-lacquered oak staves, rawhide, polished brass (rim, hooks, brackets), a
# brushed brass badge, the rubber foot and the steel flesh hoop. Object coordinates are the drum's own
# metres (the scene scales the whole drum by its parent, not the mesh).
import bpy
from lib import image
from objects.conga_nodes import (tree, node, math, add, mul, mad, remap, mix, mixf, vec, xyz, combine, noise, ramp, bump,
                                 attr, objpos, principled)

WOOD = "polyhaven/oak_veneer_01/oak_veneer_01_"
WOOD_SIZE = 1.83        # metres the texture covers (Poly Haven's dimensions for oak_veneer_01)


def scratches(nt, p, rot, scale, width, density):
    """Fine hairline scratches: iso-lines of a noise drawn out along one direction, only in patches."""
    q = node(nt, "ShaderNodeMapping", {"Vector": p, "Rotation": rot}).outputs[0]
    q = vec(nt, "MULTIPLY", q, (1.0, 1.0, 0.04))
    n = noise(nt, q, scale, 2.0, 0.5).outputs[0]
    line = remap(nt, math(nt, "ABSOLUTE", add(nt, n, -0.5)), 0.0, width, 1.0, 0.0)
    mask = remap(nt, noise(nt, p, 9.0, 2.0, 0.5).outputs[0], 1.0 - density, 1.0 - density + 0.12)
    return mul(nt, line, mask)


def wood():
    m, nt, o = tree("conga lacquered oak")
    uv = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
    tex = lambda f, col: node(nt, "ShaderNodeTexImage", {"Vector": uv}, image=image(WOOD + f, col), interpolation="Cubic")
    diff, rgh, nor = tex("diff_4k.jpg", True), tex("rough_4k.jpg", False), tex("nor_gl_4k.jpg", False)
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    st, st2 = attr(nt, "stave"), attr(nt, "stave2")
    seam_d = attr(nt, "seam")

    # the oak's own light and dark, read through an amber stain: the pores take more of it
    lum = node(nt, "ShaderNodeRGBToBW", {"Color": diff.outputs[0]}).outputs[0]
    t = remap(nt, lum, 0.12, 0.37)
    col = ramp(nt, t, [(0.0, (0.20, 0.072, 0.010)), (0.45, (0.42, 0.185, 0.034)), (1.0, (0.62, 0.315, 0.070))])
    # each stave is its own board: a little lighter or darker, redder or yellower
    hsv = node(nt, "ShaderNodeHueSaturation", {"Hue": mad(nt, st, 0.036, 0.482), "Saturation": mad(nt, st2, 0.16, 0.93),
                                               "Value": mad(nt, st2, 0.42, 0.78), "Color": col})
    col = hsv.outputs[0]
    # the finish is shaded: deeper toward the foot and just under the rim
    foot = remap(nt, z, 0.0, 0.34, 1.0, 0.0, smooth=True)
    col = mix(nt, mul(nt, foot, 0.65), col, (0.26, 0.11, 0.022), "MULTIPLY")
    under = remap(nt, z, 0.660, 0.730, 0.0, 1.0, smooth=True)
    col = mix(nt, mul(nt, under, 0.35), col, (0.25, 0.08, 0.02), "MULTIPLY")
    # glue lines between staves, under the lacquer
    line = remap(nt, seam_d, 0.00010, 0.00045, 1.0, 0.0)
    col = mix(nt, mul(nt, line, 0.75), col, (0.05, 0.012, 0.003))

    # lacquer: a clear coat with a faint amber tint, slightly uneven sheen, a groove at each seam and a
    # trace of orange peel and waviness, as a sprayed and rubbed-out finish
    smudge = noise(nt, p, 7.0, 4.0, 0.6).outputs[0]
    smudge2 = noise(nt, p, 55.0, 3.0, 0.5).outputs[0]
    coat_r = add(nt, 0.012, mul(nt, remap(nt, smudge, 0.45, 0.70), 0.03))
    coat_r = add(nt, coat_r, mul(nt, remap(nt, smudge2, 0.58, 0.78), 0.025))
    scr = math(nt, "MAXIMUM", scratches(nt, p, (0.4, 1.1, 0.3), 160.0, 0.0035, 0.45),
               scratches(nt, p, (1.2, 0.2, 2.1), 220.0, 0.0030, 0.40))
    coat_r = add(nt, coat_r, mul(nt, scr, 0.10))
    peel = noise(nt, p, 650.0, 2.0, 0.5).outputs[0]
    wave = noise(nt, p, 16.0, 2.0, 0.5).outputs[0]
    groove = mul(nt, line, -1.0)
    cn = bump(nt, peel, 0.06, 0.00002)
    cn = bump(nt, wave, 0.05, 0.0004, cn)
    cn = bump(nt, groove, 1.0, 0.00012, cn)
    cn = bump(nt, scr, -0.25, 0.00001, cn)

    bn = node(nt, "ShaderNodeNormalMap", {"Strength": 0.35, "Color": nor.outputs[0]}).outputs[0]
    bn = bump(nt, groove, 1.0, 0.00020, bn)
    base_r = remap(nt, rgh.outputs[0], 0.1, 0.9, 0.30, 0.60)
    bsdf = principled(nt, Base_Color=col, Roughness=base_r, Normal=bn, Specular_IOR_Level=0.35,
                      Coat_Weight=1.0, Coat_Roughness=coat_r, Coat_IOR=1.52, Coat_Tint=(1.0, 0.62, 0.30), Coat_Normal=cn)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def hide():
    m, nt, o = tree("conga rawhide")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    rho = vec(nt, "LENGTH", combine(nt, x, y, 0.0))
    warp = noise(nt, p, 6.0, 3.0, 0.6).outputs["Color"]
    pw = vec(nt, "ADD", p, vec(nt, "SCALE", add(nt, warp, -0.5), scale=0.04))
    # the hide's thickness varies in clouds: thin places let light through and read amber, thick ones
    # are chalky cream
    cloud = noise(nt, pw, 5.0, 8.0, 0.66).outputs[0]
    cloud2 = noise(nt, pw, 16.0, 6.0, 0.6).outputs[0]
    thick = mad(nt, cloud, 0.65, mul(nt, cloud2, 0.35))
    # fibres run mostly one way across the head
    fib = noise(nt, vec(nt, "MULTIPLY", pw, (1.0, 7.0, 1.0)), 90.0, 12.0, 0.75, distortion=0.6).outputs[0]
    fib2 = noise(nt, vec(nt, "MULTIPLY", pw, (6.0, 1.0, 1.0)), 60.0, 10.0, 0.7, distortion=0.8).outputs[0]
    fine = noise(nt, p, 1600.0, 3.0, 0.6).outputs[0]
    # veins: soft branching lines where two noises cross their middles
    def veins(scale, width, seed_off):
        vn = noise(nt, vec(nt, "ADD", pw, (seed_off, 0.0, 0.0)), scale, 4.0, 0.5, distortion=0.4).outputs[0]
        return remap(nt, math(nt, "ABSOLUTE", add(nt, vn, -0.5)), 0.0, width, 1.0, 0.0, smooth=True)
    vein = math(nt, "MAXIMUM", veins(7.0, 0.022, 0.0), mul(nt, veins(19.0, 0.018, 3.7), 0.6))
    vein = mul(nt, vein, remap(nt, noise(nt, p, 2.5, 2.0, 0.5).outputs[0], 0.42, 0.62))
    # a few small dark marks in the hide
    spots = remap(nt, noise(nt, pw, 40.0, 3.0, 0.5).outputs[0], 0.68, 0.76)

    cream = (0.66, 0.53, 0.34)
    amber = (0.47, 0.33, 0.165)
    col = mix(nt, remap(nt, thick, 0.40, 0.60, smooth=True), amber, cream)
    col = mix(nt, mul(nt, remap(nt, fib, 0.45, 0.62), 0.35), col, (0.74, 0.63, 0.45))
    col = mix(nt, mul(nt, remap(nt, fib2, 0.48, 0.62), 0.25), col, (0.55, 0.41, 0.24))
    col = mix(nt, mul(nt, vein, 0.30), col, (0.50, 0.34, 0.17))
    col = mix(nt, mul(nt, spots, 0.45), col, (0.38, 0.26, 0.13))
    # the edge: darker where it rolls over the bearing edge and down to the rim, oily from hands
    edge = remap(nt, rho, 0.120, 0.1465, 0.0, 1.0, smooth=True)
    collar = remap(nt, z, 0.7545, 0.7395, 0.35, 1.0, smooth=True)
    edge = math(nt, "MAXIMUM", mul(nt, edge, 0.60), mul(nt, collar, remap(nt, rho, 0.146, 0.1484)))
    grime = remap(nt, noise(nt, p, 26.0, 4.0, 0.6).outputs[0], 0.35, 0.65, 0.7, 1.0)
    col = mix(nt, mul(nt, edge, grime), col, (0.22, 0.135, 0.06))
    low = remap(nt, z, 0.7425, 0.7385, 0.0, 1.0, smooth=True)
    col = mix(nt, mul(nt, low, 0.7), col, (0.10, 0.06, 0.03))
    # a soft ring of hand wear on the playing area, greyer
    played = mul(nt, remap(nt, rho, 0.06, 0.10, 0.0, 1.0, smooth=True), remap(nt, rho, 0.125, 0.142, 1.0, 0.0, smooth=True))
    col = mix(nt, mul(nt, played, mul(nt, remap(nt, cloud2, 0.25, 0.75), 0.28)), col, (0.50, 0.41, 0.30))

    rough = add(nt, 0.42, mul(nt, remap(nt, thick, 0.3, 0.7), 0.18))
    rough = mixf(nt, mul(nt, edge, 0.8), rough, 0.34)
    hn = bump(nt, fine, 0.05, 0.00003)
    hn = bump(nt, fib, 0.14, 0.00007, hn)
    hn = bump(nt, fib2, 0.08, 0.00005, hn)
    hn = bump(nt, thick, 0.20, 0.00050, hn)
    hn = bump(nt, vein, 0.10, 0.00006, hn)
    # the hide gathers into small vertical folds where it is pulled down round the flesh hoop
    fold_zone = mul(nt, remap(nt, z, 0.7525, 0.7470, 0.0, 1.0, smooth=True), remap(nt, rho, 0.1470, 0.1482))
    folds = noise(nt, vec(nt, "MULTIPLY", p, (1.0, 1.0, 0.10)), 110.0, 2.0, 0.5).outputs[0]
    hn = bump(nt, mul(nt, folds, fold_zone), 0.5, 0.0004, hn)
    col = mix(nt, mul(nt, fold_zone, mul(nt, remap(nt, folds, 0.40, 0.62), 0.25)), col, (0.12, 0.075, 0.035))
    bsdf = principled(nt, Base_Color=col, Roughness=add(nt, rough, 0.06), Normal=hn, Specular_IOR_Level=0.32,
                      Sheen_Weight=0.08, Sheen_Roughness=0.4, Sheen_Tint=(1.0, 0.92, 0.80))
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def brass(name, rough=0.2, metal=1.0, wear="ao", polish=None, brushed=False, lacquer=(1.0, 0.80, 0.52), base=None,
          border=None, threads=False):
    """Lacquered brass. wear: "ao" polishes convex edges of solid parts (found by an inside AO probe),
    "top" polishes the crown rim's curl where hands rub, None leaves it even. polish: "ring" for the
    rim's circumferential polishing lines; brushed: straight lines for the badge."""
    m, nt, o = tree(name)
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    base = base or (0.84, 0.56, 0.19)
    tarn = noise(nt, p, 45.0, 5.0, 0.6).outputs[0]
    tf = remap(nt, tarn, 0.50, 0.75, 0.0, 0.30)
    ao = node(nt, "ShaderNodeAmbientOcclusion", {"Distance": 0.004}, only_local=True, samples=8).outputs["AO"]
    crevice = remap(nt, ao, 0.55, 0.95, 1.0, 0.0)
    tf = math(nt, "MAXIMUM", tf, mul(nt, crevice, 0.85))
    col = mix(nt, tf, base, (0.36, 0.24, 0.10))
    r = add(nt, rough, mul(nt, tf, 0.18))
    fine = noise(nt, p, 900.0, 4.0, 0.6).outputs[0]
    r = add(nt, r, mul(nt, remap(nt, fine, 0.4, 0.7), 0.02))
    nrm = None
    if polish == "ring":
        # lathe-polished: fine lines running round the rim
        lines = noise(nt, vec(nt, "MULTIPLY", p, (8.0, 8.0, 900.0)), 6.0, 3.0, 0.6).outputs[0]
        r = add(nt, r, mul(nt, remap(nt, lines, 0.35, 0.65, -0.04, 0.05), 1.0))
        nrm = bump(nt, lines, 0.04, 0.00001)
    if brushed:
        streak = noise(nt, vec(nt, "MULTIPLY", p, (1.0, 1.0, 60.0)), 900.0, 2.0, 0.5).outputs[0]
        r = add(nt, r, mul(nt, remap(nt, streak, 0.3, 0.7), 0.08))
        nrm = bump(nt, streak, 0.05, 0.00002)
    if border:
        # a plain engraved line round the badge, 2.8 mm in from its edge; the engraving holds dark tarnish
        uvp = node(nt, "ShaderNodeUVMap", uv_map="UVMap").outputs[0]
        u, v, _ = xyz(nt, uvp)
        du = add(nt, border[0], mul(nt, math(nt, "ABSOLUTE", u), -1.0))
        dv = add(nt, border[1], mul(nt, math(nt, "ABSOLUTE", v), -1.0))
        dd = math(nt, "ABSOLUTE", add(nt, math(nt, "MINIMUM", du, dv), -0.0028))
        groove = remap(nt, dd, 0.00015, 0.00035, 1.0, 0.0)
        col = mix(nt, mul(nt, groove, 0.8), col, (0.10, 0.07, 0.03))
        r = mixf(nt, groove, r, 0.5)
        nrm = bump(nt, mul(nt, groove, -1.0), 1.0, 0.00008, nrm)
    if threads:
        # the hooks' tails under the nuts are threaded, 1.25 mm pitch
        th = math(nt, "SINE", mul(nt, z, 2 * 3.14159265 / 0.00125))
        zone = remap(nt, z, 0.5625, 0.5605, 0.0, 1.0)
        nrm = bump(nt, mul(nt, th, zone), 0.6, 0.00012, nrm)
        col = mix(nt, mul(nt, zone, 0.35), col, (0.30, 0.21, 0.09))
    rub = None
    if wear == "ao":
        edge = node(nt, "ShaderNodeAmbientOcclusion", {"Distance": 0.003}, only_local=True, inside=True, samples=8).outputs["AO"]
        rub = mul(nt, remap(nt, edge, 0.75, 0.98, 1.0, 0.0), 0.6)
    elif wear == "top":
        rub = mul(nt, remap(nt, z, 0.7355, 0.7385, 0.0, 1.0, smooth=True),
                  remap(nt, noise(nt, p, 20.0, 3.0, 0.5).outputs[0], 0.35, 0.65, 0.3, 0.8))
    if rub is not None:
        col = mix(nt, rub, col, (0.92, 0.72, 0.38))
        r = mixf(nt, rub, r, 0.10)
    kw = dict(Base_Color=col, Metallic=metal, Roughness=r, Specular_Tint=(1.0, 0.93, 0.80))
    if lacquer:
        # instrument brass is lacquered: a thin gold-tinted coat that warms everything the metal reflects
        kw.update(Coat_Weight=1.0, Coat_Roughness=add(nt, mul(nt, r, 0.08), 0.025), Coat_IOR=1.5, Coat_Tint=lacquer)
    if nrm is not None:
        kw["Normal"] = nrm
    bsdf = principled(nt, **kw)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def rubber():
    m, nt, o = tree("conga rubber")
    p = objpos(nt)
    x, y, z = xyz(nt, p)
    dust = remap(nt, noise(nt, p, 60.0, 4.0, 0.6).outputs[0], 0.45, 0.75, 0.0, 0.5)
    low = remap(nt, z, 0.006, 0.0, 0.0, 1.0)
    col = mix(nt, mul(nt, dust, add(nt, 0.4, low)), (0.020, 0.018, 0.017), (0.10, 0.09, 0.085))
    fine = noise(nt, p, 2000.0, 2.0, 0.5).outputs[0]
    bsdf = principled(nt, Base_Color=col, Roughness=add(nt, 0.55, mul(nt, dust, 0.3)), Specular_IOR_Level=0.4,
                      Sheen_Weight=0.2, Sheen_Roughness=0.5, Normal=bump(nt, fine, 0.08, 0.00003))
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def steel():
    m, nt, o = tree("conga steel")
    bsdf = principled(nt, Base_Color=(0.30, 0.29, 0.27), Metallic=1.0, Roughness=0.4)
    nt.links.new(bsdf.outputs[0], o.inputs["Surface"])
    return m


def make():
    # Satin rather than mirror brass: in this studio a mirror finish shows little but the blue floor and
    # the grey room, and reads as steel; at 0.3 roughness the key light warms the whole surface.
    return dict(wood=wood(), hide=hide(), rim=brass("conga brass rim", 0.30, wear="top", polish="ring"),
                brass=brass("conga brass", 0.24), rod=brass("conga brass rod", 0.30, wear=None, threads=True),
                plate=brass("conga brass plate", 0.30, wear=None),
                badge=brass("conga badge", 0.36, wear=None, brushed=True, base=(0.62, 0.43, 0.16), border=(0.0195, 0.0265)),
                rubber=rubber(), steel=steel())
