# Roasted coffee beans: a dozen shapes (each an ellipsoid with a domed back, a flatter face and the
# S-shaped crease down its middle, a little bent, one end fuller), shared by every bean placed. The
# crease is a vertex attribute the shader uses for the pale silverskin left in it.
import math, random
import bpy, bmesh
from mathutils import Vector, Euler

VARIANTS = 12


def bean_mesh(rnd, name):
    a = rnd.uniform(0.0051, 0.0062)          # half length
    b = rnd.uniform(0.0037, 0.0044)          # half width
    c = rnd.uniform(0.0025, 0.0031)          # half thickness (back to face)
    face = rnd.uniform(0.28, 0.42)           # how flat the face is
    amp = rnd.uniform(0.06, 0.20) * b        # the crease's S
    ph = rnd.uniform(-0.6, 0.6)
    depth = rnd.uniform(0.50, 0.70) * c
    width = rnd.uniform(0.09, 0.14) * b
    bend = rnd.uniform(-0.10, 0.10)
    fat = rnd.uniform(-0.10, 0.10)
    off = rnd.uniform(-0.08, 0.08) * b
    nu, nv = 40, 48                          # round the bean, along it (poles at the tips)
    bm = bmesh.new()
    cr = bm.verts.layers.float.new("crease")

    def vert(x, y, z, k):
        v = bm.verts.new((x, y, z))
        v[cr] = k
        return v

    rows = []
    for j in range(nv + 1):
        th = -math.pi / 2 + math.pi * j / nv
        u = math.sin(th)
        if j in (0, nv):
            rows.append([vert(a * u, 0.0, bend * a * u * u, 0.0)])
            continue
        row = []
        for i in range(nu):
            ph_ = 2 * math.pi * i / nu
            x = a * u
            y = b * math.cos(th) * math.cos(ph_) * (1 + fat * u)
            z = c * math.cos(th) * math.sin(ph_)
            if z < 0:
                z *= face
            yc = off + amp * math.sin(math.pi * 0.9 * u + ph)
            g = math.exp(-((y - yc) / width) ** 2) * max(0.0, 1 - abs(u) ** 3.0)
            k = 0.0
            if math.sin(ph_) < 0:
                z += depth * g * min(1.0, -math.sin(ph_) * 3)
                k = g * min(1.0, -math.sin(ph_) * 3)
                # the halves of the face swell a little either side of the crease
                z -= 0.10 * c * math.exp(-((y - yc) / (width * 3.2)) ** 2) * (1 - g) * max(0.0, 1 - abs(u) ** 2) * (-math.sin(ph_))
            z += bend * a * u * u
            row.append(vert(x, y, z, k))
        rows.append(row)
    for j in range(nv):
        A, B = rows[j], rows[j + 1]
        for i in range(nu):
            i2 = (i + 1) % nu
            if len(A) == 1:
                bm.faces.new((A[0], B[i2], B[i]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[i2], B[0]))
            else:
                bm.faces.new((A[i], A[i2], B[i2], B[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.shade_smooth()
    # the thickness: the face sits at z = -c*face, the back at +c
    return me, (a, b, c * face, c)


def variants(seed=5):
    rnd = random.Random(seed)
    return [bean_mesh(rnd, f"bean {k}") for k in range(VARIANTS)]


def place(meshes, mat, items, name="bean"):
    """items: (location, rotation quaternion, variant). Linked duplicates of the shared meshes."""
    obs = []
    for k, (loc, q, var) in enumerate(items):
        me, _ = meshes[var % len(meshes)]
        if mat.name not in [m.name for m in me.materials if m]:
            me.materials.append(mat)
        ob = bpy.data.objects.new(f"{name} {k}", me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = q
        obs.append(ob)
    return obs


def lying(rnd, meshes, x, y, z_floor, var=None, face_down=None):
    """A bean resting on a flat surface: face down (crease hidden) or on its back (crease up)."""
    var = rnd.randrange(len(meshes)) if var is None else var
    _, (a, b, cf, cb) = meshes[var]
    if face_down is None:
        face_down = rnd.random() < 0.55
    yaw = rnd.uniform(0, 2 * math.pi)
    if face_down:
        q = Euler((0, 0, yaw)).to_quaternion()
        z = z_floor + cf * 0.92
    else:
        q = Euler((0, 0, yaw)).to_quaternion() @ Euler((math.pi, 0, 0)).to_quaternion()
        z = z_floor + cb * 0.97
    tilt = Euler((rnd.gauss(0, 0.05), rnd.gauss(0, 0.05), 0)).to_quaternion()
    return (Vector((x, y, z)), tilt @ q, var)
