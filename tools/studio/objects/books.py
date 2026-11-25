# The stack of ten large hardcover art books with a DSLR on top, at real size on the floor at z = 0.
# Sizes follow the stand-in (standins.books); its offsets are doubled and its turns a quarter wider, so
# the stack is less tidy. Book cloth in muted colours and one printed paper-over-board cover; half the
# books show their spine, half their pages. Spines carry abstract marks only: gilt rules, dots, a blank
# label, a printed disc, a foil band.
import math, random
from objects import books_book as bk
from objects import books_shaders as sh
from objects.books_kit import empty, parent

# (thickness, height along x, width along y, offset x, offset y, turn in degrees) from the stand-in, and
# per book: cover, which way the spine faces, its marks.
STACK = [
    (0.0459, 0.286, 0.220, -0.0083, -0.0087, -1.4),
    (0.0629, 0.328, 0.238, -0.0067, +0.0007, -3.1),
    (0.0443, 0.286, 0.211, +0.0103, +0.0066, +4.3),
    (0.0600, 0.292, 0.215, +0.0030, +0.0046, +5.0),
    (0.0620, 0.285, 0.230, +0.0041, +0.0001, -4.5),
    (0.0518, 0.285, 0.247, +0.0088, +0.0010, -2.8),
    (0.0627, 0.314, 0.244, +0.0084, +0.0002, -1.2),
    (0.0550, 0.306, 0.208, -0.0047, +0.0063, -6.4),
    (0.0412, 0.318, 0.214, +0.0008, -0.0006, -2.2),
    (0.0649, 0.292, 0.221, -0.0071, +0.0027, -3.1),
]

COVERS = [
    dict(cover="navy", spine_front=False, marks="rules", paper="cream"),
    dict(cover="green", spine_front=True, marks="rules", paper="white"),
    dict(cover="slate", spine_front=False, marks="none", paper="cream"),
    dict(cover="red", spine_front=True, marks="rules", paper="cream"),
    dict(cover="ochre_print", spine_front=True, marks="disc", paper="white"),
    dict(cover="olive", spine_front=False, marks="none", paper="cream"),
    dict(cover="brick", spine_front=True, marks="label", paper="cream"),
    dict(cover="cream", spine_front=False, marks="band", paper="white"),
    dict(cover="teal", spine_front=True, marks="dots", paper="cream"),
    dict(cover="navy2", spine_front=False, marks="rules", paper="cream"),
]

TOP = sum(b[0] for b in STACK)


def book(k, spec, cov, rnd, z):
    t, H, W, ox, oy, turn = spec
    root = empty(f"book {k}", (ox * 2.0, oy * 2.0, z), (0, 0, math.radians(turn * 1.25) + (math.pi if cov["spine_front"] else 0)))
    pts, s, spine = bk.case_path(W, t)
    cloth = sh.cover(f"book {k} cover", cov["cover"], cov["marks"], H, spine, rnd.random())
    case, _ = bk.case(f"book {k} case", H, W, t, [cloth], rnd)
    block, geo = bk.text_block(f"book {k} pages", H, W, t, [sh.paper(cov["paper"])], rnd)
    hb = bk.headbands(f"book {k} headband", H, W, t, geo, [sh.headband(cov["cover"])])
    parts = [case, block] + hb
    parent(parts, root)
    for p in parts:
        p["book"] = k
    return [root] + parts


def build():
    rnd = random.Random(23)
    obs = []
    z = 0.0
    for k, (spec, cov) in enumerate(zip(STACK, COVERS)):
        obs += book(k, spec, cov, rnd, z)
        z += spec[0]
    from objects import books_camera
    obs += books_camera.build(z)
    return obs
