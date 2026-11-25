# The plush's pile as hair curves, grown in numpy on the stuffed shape: long caramel minky over the
# body and head, short chocolate velboa on the muzzle, paws, soles and inner ears. Each strand leaves
# the fabric steeply and lies over in the nap's direction; neighbours gather into tufts; slow noise
# waves the pile so it reads as brushed fabric rather than a comb.
import itertools
import bpy
import numpy as np
from objects import capybara_shape as shape


# ---------- small numpy tools ----------
def unit(v):
    return v / np.maximum(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12)


def waves(P, seed, scale, n=6):
    """Smooth noise in about [-1, 1]: a sum of random plane waves with wavelengths near `scale`."""
    rng = np.random.default_rng(seed)
    out = np.zeros(len(P))
    for i in range(n):
        k = unit(rng.normal(size=3)) * (2 * np.pi / (scale * rng.uniform(0.6, 1.6)))
        out += np.sin(P @ k + rng.uniform(0, 2 * np.pi))
    return out / np.sqrt(n / 2)


def _hash3(c, seed):
    h = (c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (seed * 2654435761)
    h = h & 0xFFFFFFFF
    out = []
    for k in range(3):
        h = (h * 1103515245 + 12345 + k * 977) & 0x7FFFFFFF
        out.append((h % 100003) / 100003.0)
    return np.stack(out, 1)


def worley(P, cell, seed=0):
    """Each point's nearest jittered lattice point: a compact id per cell (the tufts)."""
    g = np.floor(P / cell).astype(np.int64)
    best = np.full(len(P), np.inf)
    key = np.zeros((len(P), 3), np.int64)
    for off in itertools.product((-1, 0, 1), repeat=3):
        c = g + np.array(off)
        ctr = (c + 0.15 + 0.7 * _hash3(c, seed)) * cell
        d = ((P - ctr) ** 2).sum(1)
        better = d < best
        best = np.where(better, d, best)
        key[better] = c[better]
    _, ids = np.unique(key, axis=0, return_inverse=True)
    return ids.ravel()


def sample_surface(verts, quads, n, rng):
    """n points spread over the mesh by area."""
    tris = np.concatenate([quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]])
    a, b, c = verts[tris[:, 0]], verts[tris[:, 1]], verts[tris[:, 2]]
    area = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
    cdf = np.cumsum(area)
    idx = np.searchsorted(cdf, rng.random(n) * cdf[-1])
    idx = np.minimum(idx, len(tris) - 1)
    u, v = rng.random(n), rng.random(n)
    flip = u + v > 1
    u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
    P = a[idx] + u[:, None] * (b - a)[idx] + v[:, None] * (c - a)[idx]
    return P, cdf[-1]


def rotate_about(v, axis, ang):
    """Rodrigues: rotate vectors v about unit axes by angles (broadcast)."""
    c, s = np.cos(ang)[..., None], np.sin(ang)[..., None]
    return v * c + np.cross(axis, v) * s + axis * (axis * v).sum(-1, keepdims=True) * (1 - c)


# ---------- growing strands ----------
def grow(P, N, T, L, K, lift_root, lift_tip, rng, wave_amp=0.0, wave_freq=1.0, wave_phase=None):
    """Strands from roots P with normals N, nap tangents T and lengths L, as (n, K, 3) points. The
    strand's angle above the fabric eases from lift_root to lift_tip (radians, per strand); it sways
    sideways in the fabric's plane by wave_amp (radians) along its length."""
    n = len(P)
    s = np.linspace(0, 1, K)
    sm = (s[:-1] + s[1:]) / 2                      # segment midpoints
    lift = lift_root[:, None] + (lift_tip - lift_root)[:, None] * sm[None] ** 0.8
    ph = wave_phase if wave_phase is not None else rng.uniform(0, 2 * np.pi, n)
    sway = wave_amp[:, None] * np.sin(2 * np.pi * wave_freq[:, None] * sm[None] + ph[:, None])
    Tk = rotate_about(np.repeat(T[:, None], K - 1, 1), N[:, None], sway)
    d = np.cos(lift)[..., None] * Tk + np.sin(lift)[..., None] * N[:, None]
    seg = (L / (K - 1))[:, None, None] * d
    pts = np.concatenate([P[:, None], P[:, None] + np.cumsum(seg, 1)], 1)
    return pts


def clump(pts, ids, strength, power=1.4):
    """Pull each strand towards the mean strand of its tuft, more towards the tip."""
    n, K, _ = pts.shape
    cnt = np.bincount(ids).astype(float)
    mean = np.zeros((cnt.size, K, 3))
    for k in range(K):
        for j in range(3):
            mean[:, k, j] = np.bincount(ids, weights=pts[:, k, j], minlength=cnt.size) / np.maximum(cnt, 1)
    s = np.linspace(0, 1, K)[None, :, None] ** power
    return pts + (mean[ids] - pts) * (strength[:, None, None] * s)


def collide(pts, clearance, iters=2):
    """Push strand points (not roots) out of the stuffed shape and above the floor."""
    n, K, _ = pts.shape
    body = pts[:, 1:].reshape(-1, 3)
    clr = np.broadcast_to(clearance[:, 1:], (n, K - 1)).reshape(-1)
    for _ in range(iters):
        d = shape.sdf(body, seams=False)
        bad = d < clr
        if bad.any():
            g = shape.gradient(body[bad], seams=False)
            body[bad] += g * (clr[bad] - d[bad])[:, None]
    body[:, 2] = np.maximum(body[:, 2], 0.0006)
    pts[:, 1:] = body.reshape(n, K - 1, 3)
    return pts


def tangents(P, N):
    f, _ = shape.flow(P)
    t = f - (f * N).sum(1, keepdims=True) * N
    bad = np.linalg.norm(t, axis=1) < 1e-6
    if bad.any():
        t[bad] = np.cross(N[bad], [1.0, 0.0, 0.0])
    return unit(t)


# ---------- Blender ----------
def curves_object(name, pts, r_root, r_tip, mat, curve_attrs=None):
    n, K, _ = pts.shape
    cv = bpy.data.hair_curves.new(name)
    cv.add_curves([K] * n)
    cv.position_data.foreach_set("vector", pts.astype(np.float32).ravel())
    rad = cv.attributes.new("radius", "FLOAT", "POINT")
    s = np.linspace(0, 1, K)[None]
    r = (r_root[:, None] * (1 - s) + r_tip[:, None] * s).astype(np.float32)
    rad.data.foreach_set("value", r.ravel())
    for k, v in (curve_attrs or {}).items():
        a = cv.attributes.new(k, "FLOAT", "CURVE")
        a.data.foreach_set("value", np.asarray(v, np.float32))
    cv.materials.append(mat)
    ob = bpy.data.objects.new(name, cv)
    bpy.context.scene.collection.objects.link(ob)
    return ob
