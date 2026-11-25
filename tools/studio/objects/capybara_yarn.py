# Round threads as meshes: the embroidery floss, the scarf's yarn and its fringe. A thread is a
# polyline swept by a ring with parallel-transported frames; its UVs run along (u, in metres) and
# around (v, 0..1) so a shader can draw the twist of the plies.
import bpy
import numpy as np


def _unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def frames(paths):
    """Tangent, normal and binormal along each polyline (n, K, 3), the normal carried by parallel
    transport so the rings do not twist."""
    n, K, _ = paths.shape
    T = np.empty_like(paths)
    T[:, 1:-1] = paths[:, 2:] - paths[:, :-2]
    T[:, 0] = paths[:, 1] - paths[:, 0]
    T[:, -1] = paths[:, -1] - paths[:, -2]
    T = _unit(T)
    ref = np.where(np.abs(T[:, 0, 2:3]) < 0.9, np.array([0.0, 0.0, 1.0]), np.array([1.0, 0.0, 0.0]))
    N = np.empty_like(paths)
    N[:, 0] = _unit(np.cross(T[:, 0], ref))
    for k in range(1, K):
        v = N[:, k - 1] - (N[:, k - 1] * T[:, k]).sum(1, keepdims=True) * T[:, k]
        N[:, k] = _unit(v)
    B = np.cross(T, N)
    return T, N, B


def tubes(paths, radii, sides=8, phase=None):
    """Mesh rings around each polyline. paths (n, K, 3), radii (n, K). Returns verts (n*K*S, 3),
    quads, and per-loop UVs. The ends are left open (they are buried in fabric or tapered shut)."""
    n, K, _ = paths.shape
    T, N, B = frames(paths)
    a = 2 * np.pi * np.arange(sides) / sides
    if phase is None:
        phase = np.zeros(n)
    ang = a[None, None, :] + phase[:, None, None]
    ring = (np.cos(ang)[..., None] * N[:, :, None] + np.sin(ang)[..., None] * B[:, :, None])
    verts = paths[:, :, None] + radii[:, :, None, None] * ring
    verts = verts.reshape(-1, 3)
    base = (np.arange(n) * K * sides)[:, None, None]
    k = np.arange(K - 1)[None, :, None]
    s = np.arange(sides)[None, None, :]
    s1 = (s + 1) % sides
    v00 = base + k * sides + s
    v01 = base + k * sides + s1
    v11 = base + (k + 1) * sides + s1
    v10 = base + (k + 1) * sides + s
    quads = np.stack([v00, v01, v11, v10], -1).reshape(-1, 4)
    # UVs: u = arc length along the thread, v = around (the seam column repeats the first)
    seg = np.linalg.norm(np.diff(paths, axis=1), axis=2)
    u = np.concatenate([np.zeros((n, 1)), np.cumsum(seg, 1)], 1)       # (n, K)
    uq = np.stack([u[:, :-1, None].repeat(sides, 2), u[:, :-1, None].repeat(sides, 2),
                   u[:, 1:, None].repeat(sides, 2), u[:, 1:, None].repeat(sides, 2)], -1)
    vs = (np.arange(sides) / sides)[None, None, :]
    vs1 = ((np.arange(sides) + 1) / sides)[None, None, :]
    vq = np.stack([np.broadcast_to(vs, (n, K - 1, sides)), np.broadcast_to(vs1, (n, K - 1, sides)),
                   np.broadcast_to(vs1, (n, K - 1, sides)), np.broadcast_to(vs, (n, K - 1, sides))], -1)
    uv = np.stack([uq, vq], -1).reshape(-1, 2)
    return verts, quads, uv


def mesh_object(name, verts, faces, uv=None, attrs=None, smooth=True):
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(verts))
    me.vertices.foreach_set("co", np.asarray(verts, np.float32).ravel())
    nf, nc = faces.shape
    me.loops.add(faces.size)
    me.loops.foreach_set("vertex_index", faces.astype(np.int32).ravel())
    me.polygons.add(nf)
    me.polygons.foreach_set("loop_start", (np.arange(nf) * nc).astype(np.int32))
    me.polygons.foreach_set("loop_total", np.full(nf, nc, np.int32))
    me.update(calc_edges=True)
    if uv is not None:
        layer = me.uv_layers.new(name="UVMap")
        layer.data.foreach_set("uv", np.asarray(uv, np.float32).ravel())
    for k, (domain, vals) in (attrs or {}).items():
        a = me.attributes.new(k, "FLOAT", domain)
        a.data.foreach_set("value", np.asarray(vals, np.float32))
    me.polygons.foreach_set("use_smooth", np.full(nf, smooth))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob
