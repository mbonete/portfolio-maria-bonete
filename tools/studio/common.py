# The studio scene, shared by the blockout and the finished render: render settings, where each
# object stands, the camera and the lights. Metres; x to the right, y away from the camera, z up,
# the floor at z = 0. Every object is built around its own origin (on the floor, or on the desk top
# for the things on the desk) and parked at its place here, in a collection of its own, so a later
# pass can render any one of them as a layer.
import bpy, math, os
from mathutils import Vector, Matrix
from bpy_extras.object_utils import world_to_camera_view

DESK_H = 0.73

# name: (x, y, turn in degrees about z; 0 faces the camera[, scale]). Everything but the plush is built
# at real size and shown 1.2 times larger (owner's call, 2026-11-24): bigger objects, packed close.
SCALE = 1.32
# Left to right: the screen, the monstera, the desk (tower at its right end), the conga, the easel with
# its palette (owner's arrangement, 2026-11-24: balanced, the tallest shapes at both ends). Everything but
# the plush is shown 1.32 times its real size and packed close: neighbours nearly touch or overlap in
# depth.
PLACE = {
    "screen": (-2.55, 1.02, 14),
    "monstera": (-1.72, 0.55, 0),
    "tray": (-1.06, -0.56, 10),
    "desk": (0.0, 0.72, 0),
    "capybara": (-0.30, -0.14, 8, 1.0),
    "books": (0.32, -0.04, -6),
    "maracas": (1.08, -0.34, 0),
    "conga": (1.60, 0.00, 0),
    "easel": (2.24, 0.44, -12),
    "palette": (2.14, -0.30, 22),
}


# The desk's own layout, shared by its stand-in and the finished parts (desk-local metres, before SCALE).
DESK_W, DESK_D = 2.20, 0.75
MON_K = 1.1                      # monitors 10% larger than 27" (owner, 2026-11-24)
MON_W, MON_H = 0.615 * MON_K, 0.37 * MON_K   # a 16:9 panel's outer size, landscape
MON_X = -0.29                    # the middle of the landscape pair
TOWER_X = 0.97


def monitors_layout():
    """Left to right: two landscape monitors on one arm, turned in 7 degrees, then one in portrait turned
    in 24 degrees, its right edge clear of the tower. Each: centre (x, y, z), turn about z in degrees,
    outer width and height, and where its stand meets the desk."""
    z = DESK_H
    out = []
    for s in (-1, 1):
        out.append(dict(kind="landscape", centre=(MON_X + s * 0.318 * MON_K, 0.22, z + 0.195 + MON_H / 2),
                        turn=-s * 7, w=MON_W, h=MON_H, foot=(MON_X, 0.23)))
    px = MON_X + 0.798 * MON_K
    out.append(dict(kind="portrait", centre=(px, 0.13, z + 0.2025 + MON_W / 2), turn=-24, w=MON_H, h=MON_W,
                    foot=(px - 0.02, 0.23)))
    return out


def reset():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)


def cycles(samples, width):
    scn = bpy.context.scene
    bpy.ops.preferences.addon_enable(module="cycles")
    scn.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        scn.cycles.device = "GPU"
    except Exception:
        scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = True
    scn.cycles.max_bounces = 8
    scn.render.resolution_x = width
    scn.render.resolution_percentage = 100
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    scn.render.image_settings.color_depth = "16"
    scn.view_settings.view_transform = "Khronos PBR Neutral"
    scn.view_settings.exposure = float(os.environ.get("EXPO", "-0.5"))


def group(name):
    """A collection for one object, and an empty at its place that everything in it hangs from."""
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    root = bpy.data.objects.new(name, None)
    col.objects.link(root)
    x, y, rz, *k = PLACE.get(name, (0, 0, 0))
    root.location = (x, y, 0)
    root.rotation_euler = (0, 0, math.radians(rz))
    root.scale = (k[0] if k else SCALE,) * 3
    return col, root


def adopt(col, root, obs):
    """Move freshly made objects into the collection and hang them from the root, keeping their local
    placement (they were built around the origin)."""
    for ob in obs:
        for c in list(ob.users_collection):
            c.objects.unlink(ob)
        col.objects.link(ob)
        if ob is not root and ob.parent is None:
            ob.parent = root


def floor(ground=(0.130, 0.212, 0.735)):
    """A shadow catcher: transparent in the render, it keeps the shadows the objects cast. Its colour is
    the page's azurite (linear), so the light it bounces back up onto the objects is blue."""
    bpy.ops.mesh.primitive_plane_add(size=60)
    fl = bpy.context.active_object
    fl.name = "floor"
    fl.is_shadow_catcher = True
    m = bpy.data.materials.new("floor")
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*ground, 1)
    p.inputs["Roughness"].default_value = 0.95
    fl.data.materials.append(m)
    return fl


def area(name, loc, target, size, color, power, shape="RECTANGLE", size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = shape
    ld.size = size
    ld.size_y = size_y or size
    ld.color = color
    ld.energy = power
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)
    ob.visible_camera = False
    return ob


def objects_only(light):
    """Light linking: the light reaches every object's collection, not the floor."""
    rec = bpy.data.collections.new(light.name + " receivers")
    for c in bpy.context.scene.collection.children:
        rec.children.link(c)
    light.light_linking.receiver_collection = rec


def aim(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def lights():
    """Warm daylight from high on the left (the window in the reference), a soft neutral fill from the
    right, and a dim warm-white rim from behind that separates the tops of things from the ground (it was
    lilac, which tinted the desk top pink)."""
    key = float(os.environ.get("KEY", "1300"))
    area("key", (-4.2, -3.6, 5.0), (-0.2, 0.2, 0.5), 4.5, (1.0, 0.80, 0.60), key)
    area("fill", (4.6, -5.4, 3.2), (0.2, 0.0, 0.6), 6.0, (0.92, 0.94, 1.0), key * 0.40)
    rim = area("rim", (0.6, 5.0, 4.2), (0.0, 0.3, 0.8), 3.0, (1.0, 0.95, 0.90), key * 0.30)
    # The rim lights the objects only: on the floor it would throw every object's shadow forward, a dark
    # band under the whole scene.
    objects_only(rim)
    # A tall strip softbox that only reflections see (STRIP = its power; 0 turns it off): the long vertical
    # highlight product photographs show on lacquer and glass, without changing the light on anything.
    strip = float(os.environ.get("STRIP", "600"))
    if strip:
        st = area("strip", (float(os.environ.get("STRIP_X", "-2.6")), -4.2, 1.6), (0.0, 0.3, 0.7), 0.35,
                  (1.0, 0.92, 0.82), strip, size_y=3.2)
        st.visible_diffuse = False
        st.visible_transmission = False
        st.visible_volume_scatter = False
    world = bpy.data.worlds.new("room")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.20, 0.20, 0.21, 1)
    bg.inputs["Strength"].default_value = float(os.environ.get("AMBIENT", "0.45"))
    reflections(world, bg)


def reflections(world, flat):
    """A studio environment that only glossy rays see: lacquer, brass and glass get real highlights to
    reflect, while diffuse light and the shadows stay as the lights above make them. HDRI names a CC0
    Poly Haven map in assets/ (fetch.py polyhaven-hdri; "none" turns it off); HDRI_S its strength, HDRI_ROT its turn."""
    name = os.environ.get("HDRI", "studio_small_08")
    if name == "none":
        return
    nt = world.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Rotation"].default_value = (0, 0, math.radians(float(os.environ.get("HDRI_ROT", "0"))))
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.join(os.path.dirname(__file__), "assets", "polyhaven", name, f"{name}_2k.hdr"))
    bg2 = nt.nodes.new("ShaderNodeBackground")
    bg2.inputs["Strength"].default_value = float(os.environ.get("HDRI_S", "1.5"))
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg2.inputs["Color"])
    nt.links.new(lp.outputs["Is Glossy Ray"], mix.inputs["Fac"])
    nt.links.new(flat.outputs["Background"], mix.inputs[1])
    nt.links.new(bg2.outputs["Background"], mix.inputs[2])
    out = nt.nodes["World Output"]
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])


def camera(width, margin_x=0.03, top=0.05, bottom=0.10):
    """A long lens from a little above desk height, looking slightly down so the desk top shows. The
    lens is fitted so the objects fill the width less a margin, and the frame's height is cut to them
    (more room below, for the shadows)."""
    scn = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = "HORIZONTAL"
    cd.lens = 60
    cam = bpy.data.objects.new("cam", cd)
    scn.collection.objects.link(cam)
    scn.camera = cam
    dist = float(os.environ.get("CAMD", "10.5"))
    cam.location = (0.05, -dist, float(os.environ.get("CAMZ", "3.1")))
    aim(cam, (0.05, 0.2, 0.62))
    bpy.context.view_layer.update()

    pts = []
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in scn.objects:
        if ob.type != "MESH" or ob.name == "floor" or not ob.visible_camera:
            continue
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ob.matrix_world
        pts += [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()

    def extent():
        scn.render.resolution_x, scn.render.resolution_y = width, width  # square while fitting
        bpy.context.view_layer.update()
        ps = [world_to_camera_view(scn, cam, p) for p in pts]
        return min(p.x for p in ps), max(p.x for p in ps), min(p.y for p in ps), max(p.y for p in ps)

    x0, x1, _, _ = extent()
    cd.lens *= (1 - 2 * margin_x) / (x1 - x0)
    x0, x1, y0, y1 = extent()
    px0, px1, py0, py1 = x0 * width, x1 * width, y0 * width, y1 * width
    h = int(round((py1 - py0) / (1 - top - bottom) / 2) * 2)
    scn.render.resolution_y = h
    cd.shift_x = ((px0 + px1) / 2 - width / 2) / width
    cd.shift_y = ((py0 - bottom * h + h / 2) - width / 2) / width
    return cam


def place(name, fn):
    """Build one object with fn and park it at its place, in its own collection."""
    from lib import made
    col, root = group(name)
    adopt(col, root, made(fn))
    return col, root


def finish(out):
    floor()
    lights()
    bpy.context.view_layer.update()
    camera(bpy.context.scene.render.resolution_x)
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("SAVED", out, bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y)
