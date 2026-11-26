# The painting on the easel: a work in progress, painted in code. The owner's design (a warm geometric
# abstract she had ChatGPT make; she asked for a version of it, 2026-11-25): hills, a pale disc and a
# sun, a small block, two lilac orbits with dots. Here it is mid-way: the sun,
# the hills on the left worked up with brush texture; the big front hill only blocked in, its strokes
# running out on bare primed canvas; the block and the lower orbit still pencil.
# Writes renders/painting.png (colour, sRGB; bare canvas in the gesso's own colour) and
# renders/painting_paint.png (R = paint cover, G = paint height), which easel.py picks up.
# PAINT_STAGE=1..3 paints further on, for the hero's easel (a click moves the painting a stage on) and
# writes painting-s<N>.png and painting-s<N>_paint.png: 1 the ground and the front hill finished,
# 2 the block painted, 3 the lower orbit painted along its whole arc (the painting finished).
# Usage: [PAINT_STAGE=N] blender -b --factory-startup --python-exit-code 1 -P painting.py
import math, os
import numpy as np
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = int(os.environ.get("PAINT_STAGE", "0"))
SUFFIX = f"-s{STAGE}" if STAGE else ""
W, H = 2048, 2062          # 87.4 x 88 cm
rng = np.random.default_rng(11)
f32 = np.float32


def srgb(*c):
    return np.array(c, f32) / 255.0


GESSO = srgb(231, 230, 227)    # the primed canvas (easel_kit.gesso's colour, as sRGB)
GRAPHITE = srgb(72, 72, 80)

Y, X = np.mgrid[0:H, 0:W].astype(f32)


def sample(img, x, y):
    """Bilinear lookup of a 2D array at float pixel positions (clamped)."""
    h, w = img.shape
    x = np.clip(x, 0, w - 1.001); y = np.clip(y, 0, h - 1.001)
    x0 = x.astype(np.int32); y0 = y.astype(np.int32)
    fx = x - x0; fy = y - y0
    a = img[y0, x0]; b = img[y0, x0 + 1]; c = img[y0 + 1, x0]; d = img[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def noise(cell, octaves=3, seed=0):
    """Smooth value noise in [-1, 1], features about `cell` px."""
    r = np.random.default_rng(seed)
    out = np.zeros((H, W), f32); amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(cell / (2 ** o), 2)
        g = r.uniform(-1, 1, (int(H / c) + 3, int(W / c) + 3)).astype(f32)
        out += amp * sample(g, X / c, Y / c); tot += amp; amp *= 0.5
    return out / tot


def lic(src, angle, steps=18, step=1.6):
    """Line-integral convolution: src smeared along the stroke direction field (radians)."""
    acc = src.copy(); n = 1
    for sgn in (1.0, -1.0):
        px, py = X.copy(), Y.copy()
        for _ in range(steps):
            a = sample(angle, px, py)
            px += sgn * step * np.cos(a); py += sgn * step * np.sin(a)
            acc += sample(src, px, py); n += 1
    return acc / n


def smooth(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ---------- brush texture ----------
# strokes swirl gently as in the design, mostly sideways, bending with a slow field
angle = (0.35 + 0.55 * np.sin(2 * math.pi * (X / W * 0.7 + Y / H * 0.45)) + 0.6 * noise(260, 2, 1)).astype(f32)
bristle = lic(rng.uniform(-1, 1, (H, W)).astype(f32), angle, 16, 1.5)            # fine bristle streaks
bristle /= np.abs(bristle).max() + 1e-6
patches = lic(noise(13, 1, 2), angle, 30, 3.2)                                     # stroke-sized patches
patches /= np.abs(patches).max() + 1e-6
TEX = (0.25 * bristle + 0.75 * patches).astype(f32)                                # in about [-1, 1]
hue = noise(120, 2, 3)                                                             # slow colour drift

# hand-drawn edges: shapes are evaluated on gently warped coordinates
WX = X + 2.4 * noise(140, 2, 4) * 1.0
WY = Y + 2.4 * noise(140, 2, 5) * 1.0


def P(u, v):
    return u * W, v * W   # one unit for both axes so circles stay round


def circle(cx, cy, r, x=None, y=None):
    x = WX if x is None else x; y = WY if y is None else y
    (cx, cy), r = P(cx, cy), r * W
    return np.hypot(x - cx, y - cy) - r


def box(x0, y0, x1, y1, x=None, y=None):
    x = WX if x is None else x; y = WY if y is None else y
    (x0, y0), (x1, y1) = P(x0, y0), P(x1, y1)
    qx = np.abs(x - (x0 + x1) / 2) - (x1 - x0) / 2
    qy = np.abs(y - (y0 + y1) / 2) - (y1 - y0) / 2
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0)


def fill(sdf):
    return np.clip(0.5 - sdf / 1.4, 0, 1).astype(f32)


def line(sdf, width):
    return np.clip(0.5 * width - np.abs(sdf) + 0.5, 0, 1).astype(f32)


def fit_circle(p1, p2, p3):
    (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    ux = ((x1**2 + y1**2) * (y2 - y3) + (x2**2 + y2**2) * (y3 - y1) + (x3**2 + y3**2) * (y1 - y2)) / d
    uy = ((x1**2 + y1**2) * (x3 - x2) + (x2**2 + y2**2) * (x1 - x3) + (x3**2 + y3**2) * (x2 - x1)) / d
    return ux, uy, math.hypot(x1 - ux, y1 - uy)


# ---------- the design ----------
# The owner's design also had a tall round-topped tower between the two hills; at the hero's size that read
# as a phallus, so it is left out (owner's choice, 2026-11-25, over turning it into a broad gateway).
U, V = X / W, Y / W
o1 = fit_circle((0.0, 0.30), (0.40, 0.112), (0.69, 0.215))
o2 = fit_circle((0.51, 0.935), (0.742, 0.584), (1.0, 0.49))
SHAPES = {   # name: sdf(x, y), on whatever coordinates (warped for paint, lightly jittered for pencil)
    "pale": lambda x, y: circle(0.63, 0.30, 0.322, x, y),
    "sun": lambda x, y: circle(0.985, 0.10, 0.30, x, y),
    "midhill": lambda x, y: circle(0.08, 1.05, 0.595, x, y),
    "front": lambda x, y: circle(1.00, 1.60, 1.015, x, y),
    "block": lambda x, y: box(0.79, 0.405, 0.898, 0.62, x, y),
    "terra": lambda x, y: circle(-0.03, 1.27, 0.60, x, y),
}
sdf = {k: f(WX, WY) for k, f in SHAPES.items()}
orbit1 = circle(o1[0], o1[1], o1[2])
orbit2 = circle(o2[0], o2[1], o2[2])
block = sdf["block"]

# ---------- pencil underdrawing (laid first; paint covers it where the paint is full) ----------
press = smooth(-0.6, 0.4, noise(60, 2, 6))                      # pressure comes and goes along a line
px_, py_ = X + 0.8 * noise(40, 1, 7), Y + 0.8 * noise(40, 1, 8)
pencil = np.zeros((H, W), f32)
for f in SHAPES.values():
    pencil = np.maximum(pencil, line(f(px_, py_), 3.6) * (0.45 + 0.55 * press))
# the lower orbit's first half is only drawn so far
lower = (U > 0.505) & (U < 0.745) & (V > 0.57)
pencil = np.maximum(pencil, line(circle(o2[0], o2[1], o2[2], px_, py_), 3.4) * lower * (0.5 + 0.5 * press))
# light hatching where the block will be painted
hatch = (np.sin((X + Y * 0.9) / 9.0) > 0.86).astype(f32) * fill(block - 6) * smooth(-0.2, 0.5, noise(50, 1, 9))
pencil = np.maximum(pencil, 0.45 * hatch)
# a couple of construction ticks
pencil = np.maximum(pencil, 0.35 * line(box(0.79, 0.6, 0.98, 0.6, px_, py_), 1.6) * (U > 0.77))

img = np.empty((H, W, 3), f32); img[:] = GESSO
img = img * (1 - 0.85 * pencil[..., None]) + GRAPHITE * (0.85 * pencil[..., None])
cover = np.zeros((H, W), f32)
height = np.zeros((H, W), f32)


def paint(mask, colour, opacity=1.0, wip=None, jitter=0.05, dry=0.0):
    """Lay a coat of `colour` where `mask` is, textured by the brush. wip: where the coat has reached so
    far (0..1, ragged along the strokes). dry: how much of the canvas the dry brush skips."""
    global img, cover, height
    a = mask * opacity
    if wip is not None:
        a = a * wip
    if dry:
        a = a * smooth(-0.15 - dry, 0.2 - dry, 1.4 * patches + 0.3 * bristle)   # skips run along the strokes
    c = colour[None, None, :] * (1 + jitter * TEX[..., None] + 0.035 * hue[..., None])
    img = img * (1 - a[..., None]) + c * a[..., None]
    cover = np.maximum(cover, a)
    height = np.maximum(height, a * (0.55 + 0.45 * TEX))


def reached(edge_field, soft=0.05):
    """Ragged stroke ends: 1 where the painter has worked, fading out along the strokes."""
    return smooth(soft, -soft, edge_field + 0.06 * TEX + 0.03 * noise(30, 2, 11))


# the ground: worked over the top and left; the right-middle and lower right still bare canvas
ground = reached((U - 0.72) * 1.2 + (V - 0.50) * 1.0) if STAGE < 1 else None
paint(np.ones((H, W), f32), srgb(245, 222, 186), 1.0, ground, 0.045)
paint(fill(sdf["pale"]), srgb(249, 232, 203), 1.0, reached(U - 0.80) if STAGE < 1 else None, 0.04)
paint(fill(sdf["sun"]), srgb(233, 177, 92), 1.0, None, 0.06)
paint(fill(sdf["midhill"]), srgb(167, 160, 99), 0.95, None, 0.06)                # the olive hill
paint(fill(sdf["terra"]), srgb(204, 111, 62), 0.96, None, 0.06)
# the front hill only blocked in, thin and dry, its strokes stopping part-way across
if STAGE < 1:
    paint(fill(sdf["front"]), srgb(241, 205, 153), 0.88, reached(U - 0.70, 0.08), 0.05, dry=0.10)
else:   # stage 1 on: worked across in a second, fuller coat
    paint(fill(sdf["front"]), srgb(241, 205, 153), 0.97, None, 0.05)
# a first thin wash on the block's top half; from stage 2, the block painted
if STAGE < 2:
    paint(fill(block), srgb(236, 192, 104), 0.55, reached(V - 0.50, 0.03), 0.05, dry=0.25)
else:
    paint(fill(block), srgb(236, 192, 104), 0.97, None, 0.06)
# the orbits in lilac: the upper one finished, the lower one from its dot to the edge
lilac = srgb(122, 124, 199)
taper1 = np.clip(1.0 - np.maximum(U - 0.55, 0) / 0.2, 0.25, 1)
paint(line(orbit1, 6.0 * taper1) * (V < o1[1]) * (U < 0.70), lilac, 1.0, None, 0.02)
paint(fill(circle(0.545, 0.1345, 0.0095)), lilac, 1.0, None, 0.02)
paint(line(orbit2, 5.0) * (V < o2[1]) * (U > (0.742 if STAGE < 3 else 0.505)), lilac, 1.0, None, 0.02)
paint(fill(circle(0.742, 0.584, 0.0072)), lilac, 1.0, None, 0.02)


def save(name, arr):
    im = bpy.data.images.new(name, W, H, alpha=True, float_buffer=False)
    im.colorspace_settings.name = "Non-Color" if name.endswith("_paint") else "sRGB"
    rgba = np.ones((H, W, 4), f32); rgba[..., :3] = np.clip(arr, 0, 1)
    im.pixels.foreach_set(rgba[::-1].ravel())      # Blender stores rows bottom-up
    path = os.path.join(HERE, "renders", name + ".png")
    im.filepath_raw = path; im.file_format = "PNG"; im.save()
    print("SAVED", path)


os.makedirs(os.path.join(HERE, "renders"), exist_ok=True)
save("painting" + SUFFIX, img)
save("painting" + SUFFIX + "_paint", np.stack([cover, np.clip(height, 0, 1), np.zeros_like(cover)], -1))
