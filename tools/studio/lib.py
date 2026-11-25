# Building blocks shared by the stand-ins and the finished objects: simple meshes, materials, image
# textures from tools/studio/assets (see fetch.py), and a way to collect what a builder made.
import bpy, bmesh, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")


def material(name, color, rough=0.6, emit=None, strength=0.0, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    return m


CLAY = material("clay", (0.50, 0.50, 0.50))
DARK = material("clay dark", (0.16, 0.16, 0.16))
SCREEN = material("monitor glow", (0.02, 0.02, 0.02), 0.3, (0.62, 0.22, 1.0), 4.0)
RGB = material("rgb", (0.02, 0.02, 0.02), 0.3, (0.15, 0.85, 1.0), 6.0)


def image(path, colour=True):
    """An image from disk, loaded once. Non-colour data (roughness, normal, height) is read raw."""
    path = path if os.path.isabs(path) else os.path.join(ASSETS, path)
    img = bpy.data.images.load(path, check_existing=True)
    if not colour:
        img.colorspace_settings.name = "Non-Color"
    return img


def made(fn):
    """Run a builder and return the objects it created."""
    before = set(bpy.data.objects)
    fn()
    return [o for o in bpy.data.objects if o not in before]


def box(size, loc, rot=(0, 0, 0), m=CLAY):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.active_object
    ob.scale = size
    ob.data.materials.append(m)
    return ob


def cyl(r, h, loc, rot=(0, 0, 0), m=CLAY, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=verts)
    ob = bpy.context.active_object
    ob.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return ob


def blob(scale, loc, m=CLAY):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=loc, segments=48, ring_count=24)
    ob = bpy.context.active_object
    ob.scale = scale
    ob.data.materials.append(m)
    bpy.ops.object.shade_smooth()
    return ob


def lathe(profile, loc=(0, 0, 0), m=CLAY, seg=64, name="lathe", caps=True):
    """A surface of revolution about z from (radius, height) pairs."""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        rings.append([bm.verts.new((r * math.cos(2 * math.pi * k / seg), r * math.sin(2 * math.pi * k / seg), z)) for k in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for k in range(seg):
            bm.faces.new((a[k], a[(k + 1) % seg], b[(k + 1) % seg], b[k]))
    if caps:
        bm.faces.new(rings[-1][::-1])
        bm.faces.new(rings[0])
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.data.materials.append(m)
    for f in ob.data.polygons:
        f.use_smooth = True
    return ob
