# Paints the unfolded four-panel screen, pass 3. Geometry is written in "design units" (4000 x 1600
# for the four panels) and rasterised at S times that. Outputs, all at full resolution:
#   art.png     RGBA  opaque paint: sumi plum with tarashikomi, Korin blossoms, drifting petals
#   stream.png  RGB   R = stream band, G = gold current lines, B = raised gold cloud bands
#   detail.png  RGB   R = pigment mottling inside the stream, G = relief height, B = gold dust + cut leaf
#   leaf.png    RGB   R = per-leaf tone, G = leaf overlaps, B = burnish direction
# Run with Blender's bundled python (numpy): python3 -I paint3.py OUTDIR
import math, os, struct, sys, zlib
import numpy as np

OUT = sys.argv[1]
S = float(os.environ.get("S", "1.5"))
W, H = int(4000 * S), int(1600 * S)
rng = np.random.default_rng(23)


def write_png(path, arr):
    arr = np.clip(arr * 255 + 0.5, 0, 255).astype(np.uint8)
    h, w = arr.shape[:2]
    ch = 1 if arr.ndim == 2 else arr.shape[2]
    ctype = {1: 0, 3: 2, 4: 6}[ch]
    raw = b"".join(b"\x00" + arr[y].tobytes() for y in range(h))
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


# ---------- primitives (pixel space) ----------

def bez(p0, p1, p2, p3, n):
    t = np.linspace(0, 1, n)[:, None]
    u = 1 - t
    return u**3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t**3 * p3


def path(segs, step=1.0):
    """Cubic segments in design units -> dense polyline in pixels."""
    pts = []
    for s in segs:
        s = [np.array(p, float) * S for p in s]
        L = sum(np.linalg.norm(s[i + 1] - s[i]) for i in range(3))
        pts.append(bez(*s, max(8, int(L / step))))
    return np.vstack(pts)


def normals(p):
    d = np.gradient(p, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    return np.stack([-d[:, 1], d[:, 0]], 1)


def patch(x, y, R, shape=None):
    h, w = shape if shape is not None else (H, W)
    x0, x1 = max(int(x - R), 0), min(int(x + R) + 2, w)
    y0, y1 = max(int(y - R), 0), min(int(y + R) + 2, h)
    return x0, x1, y0, y1


class Local:
    """A small mask around (cx, cy); draw into it with pixel coordinates, then .over() it."""
    def __init__(self, cx, cy, R):
        self.x0, x1, self.y0, y1 = patch(cx, cy, R)
        self.m = np.zeros((y1 - self.y0, x1 - self.x0), np.float32)
        self.sl = (slice(self.y0, y1), slice(self.x0, x1))
    def stamp(self, x, y, r, a=1.0): stamp(self.m, x - self.x0, y - self.y0, r, a)
    def ellipse(self, x, y, rx, ry, rot, a=1.0): ellipse(self.m, x - self.x0, y - self.y0, rx, ry, rot, a)
    def over(self, col):
        over(art[self.sl], col, self.m)
    def raise_(self, k):
        np.maximum(relief[self.sl], self.m * k, out=relief[self.sl])


def stamp(canvas, x, y, r, a=1.0):
    """Antialiased disk, max-composited (wet ink does not stack darker)."""
    x0, x1, y0, y1 = patch(x, y, r + 2, canvas.shape)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    v = np.clip(r + 0.5 - np.hypot(xx - x, yy - y), 0, 1) * a
    np.maximum(canvas[y0:y1, x0:x1], v, out=canvas[y0:y1, x0:x1])


def ellipse(canvas, x, y, rx, ry, rot, a=1.0):
    R = max(rx, ry)
    x0, x1, y0, y1 = patch(x, y, R + 2, canvas.shape)
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    c, s = math.cos(rot), math.sin(rot)
    u = ((xx - x) * c + (yy - y) * s) / rx
    v = (-(xx - x) * s + (yy - y) * c) / ry
    d = (np.hypot(u, v) - 1) * min(rx, ry)
    np.maximum(canvas[y0:y1, x0:x1], np.clip(0.5 - d, 0, 1) * a, out=canvas[y0:y1, x0:x1])


def polyline(canvas, pts, widths, a=1.0):
    for (x, y), w in zip(pts, widths):
        if w > 0.25:
            stamp(canvas, x, y, w, a)


def brush(canvas, pts, width, bristles=22, ink=1.0, dry=0.0):
    """Bristle brush along pts; width(t) in design units. Each bristle carries its own load that
    runs out along the stroke and then skips in streaks (flying white)."""
    n = len(pts)
    nm = normals(pts)
    t = np.linspace(0, 1, n)
    W_ = np.array([width(v) for v in t]) * S
    offs = np.sort(rng.uniform(-1, 1, bristles))
    loads = ink * rng.uniform(0.85, 1.25, bristles)
    rates = dry * rng.uniform(0.4, 1.6, bristles) * (0.6 + 0.8 * np.abs(offs))
    rad = max(0.7, W_.max() / bristles * 0.95)
    for b in range(bristles):
        noise = np.convolve(rng.random(n + 60), np.ones(31) / 31, mode="same")[30:30 + n]
        noise = (noise - noise.min()) / (np.ptp(noise) + 1e-9)
        for i in range(0, n, 1):
            left = loads[b] - rates[b] * t[i]
            if left <= 0.05 or noise[i] > left * 1.15 or W_[i] < 0.5:
                continue
            o = offs[b] * W_[i] / 2
            r = max(0.6, min(rad, W_[i] / 2) * (0.7 + 0.3 * left))
            stamp(canvas, pts[i, 0] + nm[i, 0] * o, pts[i, 1] + nm[i, 1] * o, r, min(1, 0.55 + left))
    for i in range(0, n, 2):
        core = W_[i] * 0.42 * max(0, 1 - dry * t[i] * 1.4)
        if core > 0.7:
            stamp(canvas, pts[i, 0], pts[i, 1], core, 0.95)


def taper(w0, a=0.06, b=0.4, lo=0.05, knots=()):
    def f(t):
        s = min(1, t / a) ** 0.5 if a else 1
        e = min(1, (1 - t) / b) ** 0.9 if b else 1
        k = 1 + sum(h * math.exp(-((t - c) / 0.014) ** 2) for c, h in knots)
        return w0 * max(lo, s * e) * k
    return f


def value_noise(cells, seed, shape=None):
    h, w = shape or (H, W)
    r = np.random.default_rng(seed).random((cells[1] + 2, cells[0] + 2))
    ys = np.linspace(0, cells[1], h); xs = np.linspace(0, cells[0], w)
    y0 = ys.astype(int); x0 = xs.astype(int); fy = (ys - y0)[:, None]; fx = (xs - x0)[None, :]
    fy = fy * fy * (3 - 2 * fy); fx = fx * fx * (3 - 2 * fx)
    a = r[y0][:, x0]; b = r[y0][:, x0 + 1]; c = r[y0 + 1][:, x0]; d = r[y0 + 1][:, x0 + 1]
    return ((a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy).astype(np.float32)


def box(a, k):
    k = max(1, int(k))
    c = np.cumsum(np.cumsum(np.pad(a, ((k + 1, k), (k + 1, k))), 0), 1)
    return (c[2 * k + 1:, 2 * k + 1:] - c[:-2 * k - 1, 2 * k + 1:] - c[2 * k + 1:, :-2 * k - 1] + c[:-2 * k - 1, :-2 * k - 1]) / (2 * k + 1) ** 2


def blur(a, k):
    return box(box(box(a, k), k), k)


def over(dst, col, a):
    """Composite colour col with coverage a over an RGBA layer, in place."""
    a3 = a[..., None]
    dst[..., :3] = dst[..., :3] * (1 - a3) + np.asarray(col) * a3
    dst[..., 3] = a + dst[..., 3] * (1 - a)


fine = value_noise((1600, 640), 5)
mid = 0.6 * value_noise((220, 88), 6) + 0.4 * value_noise((560, 224), 7)

# =============================================================================================
# Plum: an old trunk rises from the foot of panel 3, twists, and throws one limb over to panel
# 4 and one back toward the fold with panel 2. Old wood in tarashikomi: a grey-green wash with
# pooled ink at the edges of every puddle; young shoots straight up in one dry stroke each.
# =============================================================================================
wood = np.zeros((H, W), np.float32)      # broad wet strokes, to be pooled
twig = np.zeros((H, W), np.float32)      # crisp dark strokes

trunk = path([((2640, 1720), (2610, 1520), (2480, 1430), (2500, 1270)),
              ((2500, 1270), (2520, 1120), (2660, 1080), (2650, 930)),
              ((2650, 930), (2640, 820), (2560, 790), (2575, 690))])
brush(wood, trunk, taper(150, 0.0, 0.25, 0.42, knots=((0.12, 0.22), (0.3, -0.18), (0.42, 0.26), (0.58, -0.14), (0.7, 0.2), (0.86, -0.1))), bristles=40, dry=0.25)
limbA = path([((2590, 720), (2700, 600), (2860, 520), (3010, 540)),
              ((3010, 540), (3140, 556), (3220, 470), (3340, 450)),
              ((3340, 450), (3470, 430), (3560, 520), (3640, 640))])
brush(wood, limbA, taper(80, 0.0, 0.5, 0.1, knots=((0.08, 0.25), (0.3, 0.22), (0.42, -0.15), (0.55, 0.2), (0.75, -0.12))), bristles=30, dry=0.4)
limbB = path([((2580, 740), (2500, 640), (2420, 600), (2360, 470)),
              ((2360, 470), (2310, 370), (2230, 330), (2150, 250))])
brush(wood, limbB, taper(66, 0.0, 0.55, 0.08, knots=((0.25, -0.15), (0.45, 0.24), (0.7, -0.1))), bristles=26, dry=0.4)
stub = path([((2530, 1260), (2440, 1210), (2390, 1130), (2330, 1110))])
brush(wood, stub, taper(48, 0.0, 0.7, 0.2), bristles=20, dry=0.6)

twigs = [
    [((3010, 545), (3000, 420), (3020, 300), (3005, 150))],         # zuwai: straight young shoots
    [((3340, 452), (3350, 330), (3335, 230), (3350, 90))],
    [((2810, 560), (2800, 470), (2815, 380), (2800, 300))],
    [((2360, 470), (2370, 360), (2355, 250), (2372, 120))],
    [((3560, 520), (3600, 420), (3590, 330), (3630, 230))],
    [((3640, 640), (3680, 760), (3660, 880), (3700, 990))],          # hanging tip
    [((3200, 500), (3230, 610), (3215, 720), (3250, 830))],
    [((2230, 330), (2160, 300), (2100, 320), (2040, 290))],
    [((2440, 600), (2380, 650), (2300, 640), (2240, 690))],
]
for k, segs in enumerate(twigs):
    w = 13 if k < 5 else 10
    brush(twig, path(segs), taper(w, 0.0, 0.97, 0.02), bristles=12, dry=0.45)
for segs in [[((3005, 300), (2960, 260), (2930, 270), (2900, 240))], [((3350, 230), (3400, 200), (3420, 210), (3460, 180))],
             [((2815, 420), (2860, 380), (2870, 350), (2905, 330))], [((3660, 880), (3610, 900), (3590, 940), (3560, 950))]]:
    brush(twig, path(segs), taper(8, 0.0, 0.8, 0.08), bristles=8, dry=0.5)

# tarashikomi: pigment pools to the edges of each puddle; the puddles are irregular cells
wetm = np.clip(np.maximum(wood, np.clip((blur(wood, 3 * S) - 0.3) * 4, 0, 1)), 0, 1)
pud = 0.55 * value_noise((70, 28), 31) + 0.3 * value_noise((180, 72), 32) + 0.15 * fine
lv = np.clip((pud - 0.30) / 0.42, 0, 1)
rims = np.exp(-((lv - 0.38) / 0.035) ** 2) + 0.7 * np.exp(-((lv - 0.68) / 0.03) ** 2)
inner = np.clip(blur(wetm, 6 * S), 0, 1)                 # 1 deep inside the stroke, falls at its edge
edge_dark = np.clip((1 - inner) * 2.6 - 0.5, 0, 1)        # ink gathers at the stroke's border
ragged = np.clip((wetm - 0.5 + 0.45 * (fine - 0.5)) * 4 + 0.5, 0, 1)
SUMI = np.array([0.035, 0.03, 0.028]); MOSS = np.array([0.20, 0.21, 0.13]); WASH = np.array([0.33, 0.31, 0.21])
tone = np.clip(0.15 + 0.85 * lv, 0, 1)                    # 0 = dark pool, 1 = pale wash
darkness = np.clip(np.maximum(edge_dark, rims * 0.9) + (1 - tone) * 0.55, 0, 1)
woodcol = WASH * (1 - darkness[..., None]) + SUMI * darkness[..., None]
woodcol = woodcol * 0.75 + MOSS * 0.25 * (1 - darkness[..., None])
art = np.zeros((H, W, 4), np.float32)
art[..., :3] = woodcol
art[..., 3] = ragged
# young twigs are one crisp dark stroke
tw = np.clip((box(twig, 1) - 0.4 + 0.3 * (fine - 0.5)) * 3 + 0.5, 0, 1)
over(art, SUMI, tw)
# moss dots (tenten): dark dabs with a greener halo, along the top of the old wood
for (x, y) in [(2520, 1240), (2640, 1000), (2580, 760), (2760, 590), (2990, 525), (3150, 520), (3330, 440),
               (2420, 590), (2330, 420), (2480, 1380), (2660, 900), (3480, 455)]:
    for k in range(int(rng.integers(2, 4))):
        L = Local(x * S, (y - 40) * S, 40 * S)
        L.ellipse((x + rng.normal(0, 14)) * S, (y - 40 + rng.normal(0, 9)) * S, rng.uniform(6, 10) * S, rng.uniform(4, 7) * S, rng.uniform(0, 3))
        L.over(np.array([0.06, 0.07, 0.04]))
del wood, twig, wetm, pud, lv, rims, inner, edge_dark, ragged, darkness, woodcol, tw

# ---------- blossoms: Korin's round plum. Gofun white is raised; red is flat cinnabar ----------
relief = np.zeros((H, W), np.float32)
CORAL = np.array([0.74, 0.25, 0.22]); CORAL_D = np.array([0.52, 0.13, 0.12])
WHITE = np.array([0.95, 0.93, 0.86]); WHITE_D = np.array([0.80, 0.77, 0.68])
POLLEN = np.array([0.88, 0.68, 0.26]); STAMEN = np.array([0.32, 0.12, 0.07]); CALYX = np.array([0.36, 0.40, 0.17])


def blossom(x, y, r, white, rot, tilt=1.0):
    """Five round petals, each shaded toward its base; a fine darker rim; nine stamens with pollen.
    tilt < 1 squashes the flower to show it turned away."""
    x, y, r = x * S, y * S, r * S
    base, deep = (WHITE, WHITE_D) if white else (CORAL, CORAL_D)
    R = int(r * 1.8)
    x0, x1, y0, y1 = patch(x, y, R)
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    c, s = math.cos(rot), math.sin(rot)
    u = (xx - x) * c + (yy - y) * s; v = (-(xx - x) * s + (yy - y) * c) / tilt
    loc = art[y0:y1, x0:x1]
    cover = np.zeros_like(u)
    for k in range(5):
        a = k * 2 * math.pi / 5 + 0.04 * k
        px, py = math.cos(a) * r * 0.58, math.sin(a) * r * 0.58
        d = np.hypot(u - px, v - py)
        pr = r * (0.54 + 0.03 * math.sin(k * 2.1))
        m = np.clip(pr + 0.6 - d, 0, 1)
        shade = np.clip(1 - np.hypot(u, v) / (r * 1.05), 0, 1) ** 1.4      # deeper toward the heart
        col = base[None, None, :] * (1 - 0.45 * shade[..., None]) + deep[None, None, :] * 0.45 * shade[..., None]
        rim = np.clip(1 - np.abs(d - pr + 1.0 * S) / (0.9 * S), 0, 1) * m
        col = col * (1 - 0.35 * rim[..., None])
        a3 = m[..., None]
        loc[..., :3] = loc[..., :3] * (1 - a3) + col * a3
        loc[..., 3] = np.maximum(loc[..., 3], m)
        cover = np.maximum(cover, m)
    if white:
        rl = relief[y0:y1, x0:x1]
        np.maximum(rl, cover * 0.7, out=rl)
    # calyx shows between petals of the red, stamens over all
    for k in range(10):
        a = rot + 0.25 + k * 2 * math.pi / 10 + rng.normal(0, 0.06)
        L = r * (0.5 + 0.16 * rng.random())
        st = Local(x, y, R)
        pts = np.array([(x + math.cos(a) * L * t, y + math.sin(a) * L * t * tilt) for t in np.linspace(0.16, 1, int(L))])
        for px_, py_ in pts:
            st.stamp(px_, py_, 0.55 * S)
        st.over(STAMEN)
        d = Local(x, y, R)
        d.ellipse(pts[-1, 0], pts[-1, 1], max(1.6, r * 0.075), max(1.3, r * 0.06), a)
        d.over(POLLEN)
    c_ = Local(x, y, R); c_.ellipse(x, y, r * 0.15, r * 0.15 * tilt, rot); c_.over(CALYX)


def bud(x, y, r, white, ang):
    x, y, r = x * S, y * S, r * S
    m = Local(x, y, r * 3)
    m.ellipse(x + math.cos(ang) * r * 0.25, y + math.sin(ang) * r * 0.25, r * 1.05, r * 0.85, ang)
    m.over(WHITE if white else CORAL)
    if white:
        m.raise_(0.6)
    s = Local(x, y, r * 3)
    for side in (-1, 1):
        s.ellipse(x - math.cos(ang) * r * 0.7 + math.cos(ang + side * 1.25) * r * 0.42,
                y - math.sin(ang) * r * 0.7 + math.sin(ang + side * 1.25) * r * 0.42, r * 0.42, r * 0.28, ang + side * 0.9)
    s.over(np.array([0.12, 0.10, 0.05]))


flowers = [  # x, y, r, white, tilt
    (3032, 232, 28, False, 1.0), (2978, 380, 23, True, 0.8), (3322, 160, 27, True, 1.0), (3372, 300, 21, False, 0.75),
    (2830, 360, 24, True, 1.0), (2915, 318, 19, False, 0.85), (2395, 200, 26, False, 1.0), (2338, 330, 20, True, 0.7),
    (3615, 300, 24, False, 1.0), (3672, 935, 23, True, 1.0), (3690, 800, 18, False, 0.7), (3228, 780, 22, True, 1.0),
    (3245, 660, 17, False, 0.8), (2075, 318, 22, True, 1.0), (2270, 668, 21, False, 1.0), (2880, 260, 17, True, 0.75),
    (3440, 196, 19, False, 1.0), (3580, 935, 17, True, 0.8), (2960, 480, 16, False, 0.8), (3112, 460, 15, True, 1.0),
    (2700, 540, 15, False, 0.7), (2440, 560, 16, True, 0.9),
]
for x, y, r, wht, tilt in flowers:
    blossom(x, y, r, wht, rng.uniform(0, 6.28), tilt)
for (x, y, r, wht, ang) in [(2995, 360, 9, False, -1.6), (3352, 300, 8, True, -1.6), (2808, 400, 8, False, -1.6),
                            (2368, 330, 8, False, -1.6), (3600, 420, 8, True, -1.4), (3672, 790, 7, False, 1.7),
                            (3232, 640, 7, True, 1.6), (2120, 312, 8, False, 3.0), (2300, 646, 7, True, 3.1),
                            (3010, 210, 7, True, -1.6), (3345, 160, 7, False, -1.6), (3585, 330, 7, False, -1.5),
                            (2810, 350, 7, True, -1.6), (2362, 190, 7, True, -1.6)]:
    bud(x, y, r, wht, ang)

# =============================================================================================
# Stream: a murasaki band from the top of panel 1, swelling across the fold into panel 2.
# Current lines in thick-thin gold, each throwing Korin's curls at staggered intervals; two big
# eddies at the bend. Pigment settles unevenly in the band (mottle).
# =============================================================================================
band = np.zeros((H, W), np.float32)
lines = np.zeros((H, W), np.float32)
centre = path([((380, -80), (300, 260), (620, 420), (520, 760)),
               ((520, 760), (430, 1060), (900, 1180), (1350, 1290)),
               ((1350, 1290), (1700, 1380), (1850, 1420), (2080, 1700))], step=2.0)
tt = np.linspace(0, 1, len(centre))
bw = (120 + 170 * np.sin(tt * math.pi) ** 1.3) * S
nm = normals(centre)
wob = 0.5 * np.sin(np.arange(len(centre)) * 0.031) + 0.5 * np.sin(np.arange(len(centre)) * 0.0137 + 1)
for i in range(0, len(centre), 2):
    stamp(band, centre[i, 0] + nm[i, 0] * 3 * S * wob[i], centre[i, 1] + nm[i, 1] * 3 * S * wob[i], bw[i] / 2 + 4 * S * math.sin(i * 0.05))
band = np.clip((blur(band, 1.2 * S) - 0.5 + 0.12 * (fine - 0.5)) * 6 + 0.5, 0, 1)


def curl(cx, cy, ang, r, turns, n, sgn):
    j = np.arange(n) / n
    a = ang + sgn * j * turns * 2 * math.pi
    rr = r * (1 - j / 1.25)
    return np.stack([cx + rr * np.cos(a), cy + rr * np.sin(a)], 1)


def gold_line(pts, w0, t_in=0.1, t_out=0.2):
    m = len(pts)
    t = np.linspace(0, 1, m)
    swell = 0.75 + 0.25 * np.sin(t * math.pi * 2.2 + rng.uniform(0, 6))     # calligraphic thick-thin
    w = w0 * np.minimum(1, t / t_in) ** 0.6 * np.minimum(1, (1 - t) / t_out + 0.25) * swell
    polyline(lines, pts, np.maximum(w, 0.35 * S))


NL = 10
for k in range(NL):
    f = (k - (NL - 1) / 2) / ((NL - 1) / 2) * 0.84
    tr = centre + nm * (f * bw[:, None] / 2)
    n_ = len(tr)
    period = int((430 + 57 * (k % 3)) * S / 2)
    phase = int(((k * 151) % 430) * S / 2)
    i0 = int(n_ * 0.02)
    for start in range(i0 + phase, int(n_ * 0.98), period):
        seg = tr[max(i0, start - period + int(22 * S)): start]
        if len(seg) < 20:
            continue
        d = seg[-1] - seg[-6]
        sgn = 1 if (k + start // period) % 2 else -1
        ang = math.atan2(d[1], d[0]) - sgn * math.pi / 2
        r = (13 + 3.5 * (k % 3) + 5 * rng.random()) * S
        cx, cy = seg[-1, 0] - r * math.cos(ang), seg[-1, 1] - r * math.sin(ang)
        cpts = curl(cx, cy, ang, r, 1.15 + 0.35 * rng.random(), int(26 * r / S), sgn)
        gold_line(np.vstack([seg, cpts]), 1.35 * S)
# two eddies where the stream turns: a spiral of nested lines, Korin's signature
# eddies: two interleaved arms of an Archimedean spiral; the current lines are cleared around them
for q, sgn, R0 in [(0.31, 1, 50), (0.47, -1, 40)]:
    i = int(len(centre) * q)
    cx, cy = centre[i] + nm[i] * (0.22 * bw[i] * sgn)
    yy, xx = np.mgrid[0:H, 0:W]
    lines *= np.clip((np.hypot(xx - cx, yy - cy) - R0 * S * 1.22) / (2 * S), 0, 1)
    del yy, xx
    for arm in range(2):
        th = np.linspace(0, 2.6 * 2 * math.pi, int(220 * S))
        rr = R0 * S * (1 - th / th[-1] * 0.92) * (1 + 0.035 * np.sin(th * 1.7 + arm))
        a = arm * math.pi + sgn * th
        pts = np.stack([cx + rr * np.cos(a), cy + rr * np.sin(a)], 1)
        gold_line(pts, 1.5 * S, 0.06, 0.25)
lines *= np.clip(blur(band, 2 * S) * 1.6 - 0.45, 0, 1)

# pigment settles: lighter pools and darker tide marks, only inside the band
pool = 0.6 * value_noise((60, 24), 41) + 0.4 * value_noise((150, 60), 42)
mottle = np.clip((pool - 0.35) * 2.2, 0, 1) * 0.7 + 0.3 * np.exp(-((pool - 0.52) / 0.02) ** 2)
mottle *= band

# fallen petals drifting on the water (single petals, turned)
for idx, off, r, wht in [(0.16, -0.3, 17, True), (0.25, 0.3, 14, False), (0.36, -0.15, 18, True), (0.44, 0.4, 13, False),
                         (0.55, -0.35, 16, True), (0.63, 0.2, 14, False), (0.72, -0.2, 17, True), (0.86, 0.15, 14, False)]:
    q = int(len(centre) * idx)
    x, y = centre[q] + nm[q] * off * bw[q] / 2
    m = Local(x, y, r * 2 * S)
    m.ellipse(x, y, r * 0.62 * S, r * 0.46 * S, rng.uniform(0, 6.28))
    m.over(WHITE if wht else CORAL)
    if wht:
        m.raise_(0.5)

# =============================================================================================
# Gold cloud bands (suyari-gasumi): long stadium forms in tiers with clean, slightly wandering
# edges, built up in gesso so they stand proud of the ground; gold dust settles thickest along
# their lower edges and thins out, with cut squares and strips of leaf (kirihaku, noge).
# =============================================================================================
cloud = np.zeros((H, W), np.float32)


def stadium(x0, x1, y, h):
    x0, x1, y, h = x0 * S, x1 * S, y * S, h * S
    r = h / 2
    X0, X1, Y0, Y1 = patch((x0 + x1) / 2, y, (x1 - x0) / 2 + r + 2)
    Y0, Y1 = max(int(y - r - 3), 0), min(int(y + r + 3), H)
    if X0 >= X1 or Y0 >= Y1:
        return
    yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
    cxp = np.clip(xx, x0 + r, x1 - r)
    d = np.hypot(xx - cxp, yy - y) - r
    np.maximum(cloud[Y0:Y1, X0:X1], np.clip(0.5 - d, 0, 1), out=cloud[Y0:Y1, X0:X1])


tiers = [  # each cloud is a few tiers of stadiums overlapping like stacked mist
    [(-80, 700, 112, 70), (220, 980, 168, 60), (560, 1180, 216, 44)],
    [(1080, 1880, 120, 58), (1340, 1980, 170, 46)],
    [(2050, 2700, 1330, 52), (2300, 3260, 1390, 72), (2660, 3700, 1460, 62)],
    [(3080, 4080, 1300, 54), (3440, 4080, 1352, 40)],
    [(-80, 560, 1450, 60), (180, 900, 1505, 50)],
]
for t in tiers:
    for x0, x1, y, h in t:
        stadium(x0, x1, y, h)
edge_n = 0.7 * value_noise((140, 56), 21) + 0.3 * value_noise((420, 168), 22)
cloud = np.clip((blur(cloud, 1.5 * S) - 0.5 + 0.10 * (edge_n - 0.5)) * 7 + 0.5, 0, 1)
cloud *= 1 - band                                  # the stream runs over the mist
height = np.maximum(relief, blur(cloud, 2.2 * S) * 0.9)
height = np.maximum(height, blur(lines, 0.8 * S) * 0.35)

# dust: density falls off below and around each band, settling heaviest on the lower edge
halo = np.clip(blur(cloud, 22 * S) * 2.2, 0, 1) * (1 - cloud)
low = np.roll(blur(cloud, 14 * S), int(26 * S), axis=0)
dens = np.clip(halo * 0.6 + low * 0.9, 0, 1) * (1 - band)
dust = np.zeros((H, W), np.float32)
ys, xs = np.nonzero(dens > 0.03)
pick = rng.random(len(ys)) < 0.006 * dens[ys, xs] ** 1.5
for y, x in zip(ys[pick], xs[pick]):
    stamp(dust, x, y, rng.uniform(0.6, 2.2) * S * 0.7, rng.uniform(0.55, 1))
# kirihaku: cut squares of leaf, and noge: thin strips, scattered along the dust
cand = np.nonzero(dens > 0.25)
sel = rng.choice(len(cand[0]), size=min(180, len(cand[0])), replace=False)
for j, idx in enumerate(sel):
    y, x = cand[0][idx], cand[1][idx]
    if j % 5 == 0:
        ellipse(dust, x, y, rng.uniform(7, 14) * S, rng.uniform(0.9, 1.4) * S, rng.uniform(-0.5, 0.5) + (0 if j % 2 else math.pi / 2))
    else:
        s_ = rng.uniform(3, 8) * S
        a = rng.uniform(0, math.pi / 2)
        X0, X1, Y0, Y1 = patch(x, y, s_ * 1.5)
        yy, xx = np.mgrid[Y0:Y1, X0:X1].astype(np.float32)
        u = (xx - x) * math.cos(a) + (yy - y) * math.sin(a); v = -(xx - x) * math.sin(a) + (yy - y) * math.cos(a)
        m = np.clip(s_ / 2 + 0.5 - np.maximum(np.abs(u), np.abs(v)), 0, 1)
        np.maximum(dust[Y0:Y1, X0:X1], m, out=dust[Y0:Y1, X0:X1])
dust *= 1 - band

# =============================================================================================
# Leaf: 10.9 cm squares laid in rows from the top, each row and leaf a little out of true, with
# the overlap of every leaf on its neighbour showing as a doubled strip. Each leaf has its own
# tone and burnish direction.
# =============================================================================================
LW, LH = 108.8 * S, 108.8 * S
leaf_t = np.zeros((H, W), np.float32)
leaf_s = np.zeros((H, W), np.float32)
leaf_b = np.zeros((H, W), np.float32)
X = np.arange(W, dtype=np.float32)
y = 0.0
while y < H:
    h = LH - rng.uniform(3, 6) * S
    y0, y1 = int(y), min(int(y + LH), H)
    starts = [rng.uniform(-LW, 0)]
    while starts[-1] < W:
        starts.append(starts[-1] + LW - rng.uniform(3, 7) * S)
    starts = np.array(starts)
    tones = np.clip(rng.normal(0.5, 0.13, len(starts)), 0, 1)
    burn = rng.uniform(0, 1, len(starts))
    idx = np.clip(np.searchsorted(starts, X, side="right") - 1, 0, len(starts) - 1)
    rows = np.arange(y0, y1, dtype=np.float32)[:, None]
    tilt = rng.normal(0, 0.0025)                  # leaves are not laid perfectly level
    gx = (X - starts[idx]) / LW
    leaf_t[y0:y1] = tones[idx][None, :] + 0.06 * (gx[None, :] - 0.5) * (burn[idx][None, :] - 0.5)
    leaf_b[y0:y1] = burn[idx][None, :]
    # the overlap strip on the leading edge of each leaf and along the top of each row
    ov_x = np.clip(1 - (X - starts[idx]) / (4.5 * S), 0, 1)
    ov_y = np.clip(1 - (rows - y - tilt * X[None, :]) / (4 * S), 0, 1)
    leaf_s[y0:y1] = np.maximum(ov_x[None, :] ** 0.7, ov_y ** 0.7)
    y += h
leaf_t = np.clip(leaf_t + 0.05 * (mid - 0.5), 0, 1)

os.makedirs(OUT, exist_ok=True)
write_png(os.path.join(OUT, "art.png"), art)
write_png(os.path.join(OUT, "stream.png"), np.stack([band, lines, cloud], 2))
write_png(os.path.join(OUT, "detail.png"), np.stack([mottle, np.clip(height, 0, 1), np.clip(dust, 0, 1)], 2))
write_png(os.path.join(OUT, "leaf.png"), np.stack([leaf_t, np.clip(leaf_s, 0, 1), leaf_b], 2))
print("ok", W, H)

if os.environ.get("PREVIEW"):
    g = np.array([0.80, 0.58, 0.25]) * (1 - leaf_t[..., None]) + np.array([0.95, 0.72, 0.33]) * leaf_t[..., None]
    g = g * (1 - 0.18 * leaf_s[..., None])
    g = g * (1 - cloud[..., None]) + np.array([0.98, 0.82, 0.48]) * cloud[..., None]
    g = g * (1 - dust[..., None]) + np.array([1.0, 0.86, 0.52]) * dust[..., None]
    v = np.array([0.20, 0.08, 0.42]) * (1 - mottle[..., None]) + np.array([0.30, 0.15, 0.55]) * mottle[..., None]
    g = g * (1 - band[..., None]) + v * band[..., None]
    g = g * (1 - lines[..., None]) + np.array([0.98, 0.84, 0.52]) * lines[..., None]
    a = art[..., 3:4]
    g = g * (1 - a) + art[..., :3] * a
    write_png(os.path.join(OUT, "preview.png"), g)
