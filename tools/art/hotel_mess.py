"""The Aurelian, room 507: the room Eleanor had the night she vanished. Luxurious, lived in, and turned upside down.

Overlays: the closet thrown open (with the wall safe), the safe door open, the brass box inside it, and the
lockpicked desk drawer with the slip of paper."""
import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import W, H, TOP, tall, hx, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save, city
from . import hotel
from .hotel import R, WOOD, WOOD_D, GOLD, GOLD_D, GREEN, GREEN_L, BURGUNDY, BURGUNDY_L

STEEL, STEEL_D, STEEL_L = hx("4a4c52"), hx("2a2c30"), hx("70747c")
DESK_X0, DESK_X1, DESK_Z0, DESK_Z1 = 154, 232, 2, 26
CL_X0, CL_X1, CL_Z0, CL_Z1 = 72, 124, 2, 26
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1, SAFE_Z = 84, 112, 8, 34, 4

PAPER, PAPER_D, PAPER_L, INK = hx("f2e8d2"), hx("b8a684"), hx("fffaf0"), hx("283050")
LILAC = (hx("c084c4"), hx("82508c"), hx("e8bcec"), hx("5a2c64"), hx("341836"))  # body, fold, lit, sash, outline
NAVY = (hx("3a3c5c"), hx("23243a"), hx("6a6c94"), hx("a08040"), hx("0e0e18"))
IVORY = (hx("e2d4b8"), hx("b0a080"), hx("fbf3e2"), hx("8a6a7a"), hx("4a3a2a"))
LINEN, LINEN_D, LINEN_L, LINEN_O = hx("eee4d0"), hx("bcac90"), hx("fffaf0"), hx("6a5a46")


# --- small hand-placed sprites (screen space, painting coordinates) ---------------------------------------------

def _outlined(spr, col):
    """Wraps a sprite's silhouette in a one-pixel outline so it reads against any floor."""
    a = spr.getchannel("A").point(lambda v: 255 if v else 0)
    ring = ImageChops.subtract(a.filter(ImageFilter.MaxFilter(3)), a)
    out = Image.new("RGBA", spr.size, col + (255,))
    out.putalpha(ring)
    out.alpha_composite(spr)
    return out


def _stamp(img, spr, x, y):
    img.paste(spr, (int(round(x)), int(round(y))), spr)


def dress(w, h, colours, bow=True, folds=None):
    """A dress hanging straight: shoulder straps, a fitted bodice, a sash at the waist and a skirt flaring out in
    folds to a scalloped hem. Returned as an outlined RGBA sprite, top at the top."""
    body, fold, lit, sash, line = colours
    spr = Image.new("RGBA", (w + 6, h + 3), (0, 0, 0, 0))
    px = spr.load()
    cx = (w + 6) / 2
    bw = max(4, w // 3 + 1)
    strap = max(2, h // 9)
    waist = strap + max(4, h // 4)
    nfold = folds or max(2, w // 5)

    def put(x, y, c):
        if 0 <= x < spr.width and 0 <= y + 1 < spr.height:
            px[x, y + 1] = c + (255,)

    for y in range(h):
        if y < strap:
            put(int(cx - bw / 2), y, body)
            put(int(cx + bw / 2) - 1, y, body)
            continue
        if y < waist:
            hw = bw / 2 - 0.6 * (y - strap) / (waist - strap)
            t = None
        elif y < waist + 2:
            hw = bw / 2 - 0.6
            t = None
        else:
            t = (y - waist - 2) / max(1, h - 1 - waist - 2)
            hw = bw / 2 - 0.6 + (w / 2 - bw / 2 + 0.6) * t ** 0.8
        x0, x1 = int(round(cx - hw)), int(round(cx + hw))
        for x in range(x0, x1):
            u = (x + 0.5 - x0) / max(1, x1 - x0)
            c = lit if u < 0.25 else fold if u > 0.74 else body
            if y == strap and abs(x + 0.5 - cx) < bw / 2 - 1.2:
                continue  # sweetheart neckline
            if waist <= y < waist + 2:
                c = sash
            elif t is not None:
                for f in range(1, nfold):
                    if t > 0.12 + 0.3 * (f % 2) and x == int(x0 + (x1 - x0) * f / nfold):
                        c = fold if f % 2 else lit
                if y == h - 2:
                    c = lit
                if y == h - 1 and (x - x0) % 3 == 2:
                    continue  # scalloped hem
            put(x, y, c)
    if bow:
        xr = int(round(cx + bw / 2 - 0.6))
        for (dx, dy) in ((0, -1), (1, -1), (0, 0), (0, 1), (1, 2), (-1, 2)):
            put(xr + dx, waist + dy, sash)
    return _outlined(spr, line)


def _crumple(spr, amp=1.5, period=7.0, phase=0.0):
    """Shifts the columns of a sprite up and down so cloth lying on the floor looks rumpled rather than pressed."""
    pad = int(math.ceil(amp)) + 1
    out = Image.new("RGBA", (spr.width, spr.height + 2 * pad), (0, 0, 0, 0))
    for x in range(spr.width):
        dy = int(round(amp * math.sin(x / period * 2 * math.pi + phase)))
        out.paste(spr.crop((x, 0, x + 1, spr.height)), (x, pad + dy))
    return out


def sheet(img, x, y, w, h, skew=0, lines=2, col=PAPER, seed=0, crease=False, envelope=False, seal=None):
    """A sheet of paper or an envelope: a crisp light shape with a drop shadow, a darker bottom/right edge and,
    for letters, a few lines of ink."""
    d = ImageDraw.Draw(img)
    pts = [(x, y), (x + w, y + skew), (x + w, y + h + skew), (x, y + h)]
    shadow(img, "polygon", [(px + 1, py + 1) for px, py in pts], 0.6, 0.6)
    d.polygon(pts, fill=col)
    d.line([(x, y + h), (x + w, y + h + skew), (x + w, y + skew)], fill=mul(col, 0.74))
    d.line([(x, y + h - 1), (x, y), (x + w - 1, y + skew)], fill=PAPER_L)
    rnd = random.Random(seed)
    if envelope:
        m = (x + w / 2, y + h / 2 + skew / 2 + 1)
        d.line([(x + 1, y + 1), m, (x + w - 1, y + skew + 1)], fill=mul(col, 0.7))
        if seal:
            d.rectangle([m[0] - 1, m[1] - 1, m[0], m[1]], fill=seal)
        return
    if crease:
        cy = y + h // 2
        d.line([(x + 1, cy), (x + w - 1, cy + skew)], fill=mul(col, 0.86))
    for i in range(lines):
        yy = y + 2 + 2 * i
        if yy >= y + h - 1:
            break
        x2 = x + w - 2 - rnd.randint(0, max(1, w // 3))
        k = skew / max(1, w)
        d.line([(x + 2, yy + k * 2), (x2, yy + k * (x2 - x))], fill=INK)


def pillow(w, h, gash=False, seed=0):
    """A plump pillow seen from above: stuffed corners poking out, edges sagging between them, lit and rounded on
    top and, if gutted, a slash with feathers spilling out."""
    spr = Image.new("RGBA", (w + 2, h + 2), (0, 0, 0, 0))
    px = spr.load()
    tones = (hx("b4a486"), hx("d4c8ae"), LINEN, LINEN_L)
    for y in range(h):
        for x in range(w):
            u, v = (x + 0.5) / w * 2 - 1, (y + 0.5) / h * 2 - 1
            if abs(v) > 1 - 0.28 * (1 - u * u) or abs(u) > 1 - 0.12 * (1 - v * v):
                continue
            b = 0.55 + 0.45 * (1 - (u * u + v * v) / 2) - 0.35 * v
            px[x + 1, y + 1] = tones[max(0, min(3, int(b * 4) - 1))] + (255,)
    d = ImageDraw.Draw(spr)
    if gash:
        rnd = random.Random(seed)
        a, b = (w * 0.32, h * 0.3), (w * 0.7, h * 0.72)
        d.line([a, b], fill=hx("3a3026") + (255,), width=2)
        for _ in range(8):
            t = rnd.random()
            fx, fy = a[0] + (b[0] - a[0]) * t + rnd.randint(-2, 2), a[1] + (b[1] - a[1]) * t + rnd.randint(-2, 1)
            d.point((fx, fy), fill=(255, 255, 255, 255))
    return _outlined(spr, LINEN_O)


def feathers(img, box, n, seed):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    for _ in range(n):
        x, y = rnd.randint(x0, x1), rnd.randint(y0, y1)
        d.point((x, y), fill=hx("fffcf4"))
        d.point((x + rnd.choice((-1, 1)), y + rnd.choice((0, 1))), fill=hx("cfc6b6"))


def window_night(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 156, 28, 230, 100
    city(img, (x0, y0, x1, y1), seed=507, lit=0.3)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], outline=WOOD_D, width=4)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=WOOD_D, width=3)
    d.line([(x0, 60), (x1, 60)], fill=WOOD_D, width=2)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 7], fill=hx("8c6748"))
    # one drape torn down from its rail, the other still hanging
    d.polygon([(x1 + 16, y0 - 8), (x1 - 6, y0 - 4), (x1 - 2, y0 + 44), (x1 - 8, y1 + 30), (x1 + 16, y1 + 32)], fill=BURGUNDY)
    for x in (x1 + 6, x1 + 12):
        d.line([(x, y0 - 4), (x, y1 + 28)], fill=mul(BURGUNDY, 0.72))
    d.rectangle([x0 - 20, y0 - 12, x1 + 20, y0 - 6], fill=GOLD_D)
    d.line([(x0 - 20, y0 - 12), (x1 + 20, y0 - 12)], fill=GOLD)
    d.line([(x0 - 20, y0 - 6), (x0 - 10, y0 + 8)], fill=GOLD_D, width=2)


def crooked_painting(img):
    d = ImageDraw.Draw(img)
    # the landscape above the bed, knocked askew
    d.rectangle([294, 28, 354, 64], fill=hotel.CREAM)
    d.polygon([(298, 30), (354, 36), (350, 68), (294, 62)], fill=GOLD_D)
    d.polygon([(300, 33), (351, 38), (348, 65), (297, 60)], fill=GOLD)
    d.polygon([(302, 35), (349, 40), (346, 62), (299, 58)], fill=hx("a69374"))
    d.polygon([(300, 56), (314, 44), (330, 49), (347, 42), (346, 61)], fill=hx("617367"))


def closet(img, opened=False, safe_open=False, box=False):
    X0, X1, Z0, Z1 = CL_X0, CL_X1, CL_Z0, CL_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 2, a[1] - 3, b[0] + 10, a[1] + 3], 0.4, 3)
    R.box(img, X0, X1, 3, 104, Z0, Z1, mul(WOOD, 0.95), top=WOOD, side=hx("4c2f1a"))
    R.box(img, X0 - 2, X1 + 2, 104, 112, Z0, Z1 + 2, WOOD, top=hx("8a5e3c"), side=hx("4c2f1a"))
    R.box(img, X0 + 1, X1 - 1, 0, 3, Z0, Z1 - 1, WOOD_D)
    xm = (X0 + X1) / 2
    if not opened:
        for (c, e) in ((X0 + 3, xm - 1), (xm + 1, X1 - 3)):
            R.quad(img, [(c, 6, Z1), (e, 6, Z1), (e, 100, Z1), (c, 100, Z1)], hx("75492b"), hx("3e2615"))
            R.quad(img, [(c + 4, 12, Z1), (e - 4, 12, Z1), (e - 4, 94, Z1), (c + 4, 94, Z1)], None, hx("8e6040"))
        for x in (xm - 3, xm + 3):
            R.line(img, (x, 52, Z1), (x, 60, Z1), GOLD, 2)
        R.line(img, (xm, 6, Z1), (xm, 100, Z1), WOOD_D)
        # an evening dress left hanging off the door handles, hanger hooked over the right one
        hx_, hy = R.P(xm + 3, 56, Z1)
        d = ImageDraw.Draw(img)
        d.line([(hx_ - 1, hy - 3), (hx_ + 1, hy - 4), (hx_ + 2, hy - 2), (hx_, hy + 1)], fill=STEEL_L)
        d.line([(hx_ - 8, hy + 5), (hx_, hy + 1), (hx_ + 8, hy + 5)], fill=GOLD_D, width=1)
        spr = dress(15, 40, LILAC)
        _stamp(img, spr, hx_ - spr.width / 2 + 0.5, hy + 3)
        return
    # cavity, hanging rail and what's left on the hangers
    R.quad(img, [(X0 + 3, 4, Z1), (X1 - 3, 4, Z1), (X1 - 3, 100, Z1), (X0 + 3, 100, Z1)], hx("1e140c"))
    R.quad(img, [(X0 + 3, 4, Z0 + 2), (X1 - 3, 4, Z0 + 2), (X1 - 3, 100, Z0 + 2), (X0 + 3, 100, Z0 + 2)], hx("2a1a10"))
    R.line(img, (X0 + 4, 88, Z0 + 12), (X1 - 4, 88, Z0 + 12), GOLD_D, 2)
    d = ImageDraw.Draw(img)
    for (x, col, h) in ((X0 + 10, LILAC, 40), (X1 - 12, IVORY, 36), (X0 + 24, NAVY, 42)):
        rx, ry = R.P(x, 88, Z0 + 12)
        d.line([(rx, ry - 2), (rx + 1, ry - 2), (rx, ry + 2)], fill=STEEL_L)
        d.line([(rx - 6, ry + 5), (rx, ry + 2), (rx + 6, ry + 5)], fill=STEEL_L)
        spr = dress(12, h, col, bow=False)
        _stamp(img, spr, rx - spr.width / 2 + 0.5, ry + 3)
    # clothes yanked off their hangers, heaped at the bottom
    hx_, hy = R.P(X0 + 4, 4, Z1 - 4)
    heap = _crumple(dress(9, 26, (hx("8a6a8a"), hx("5a3e5a"), hx("b096b0"), hx("3e2a3e"), hx("1a101a")), bow=False)
                    .rotate(90, expand=True), 1.2, 9)
    _stamp(img, heap, hx_ - 1, hy - heap.height + 2)
    slip = _crumple(dress(7, 16, IVORY, bow=False).rotate(-90, expand=True), 1, 6, 1.0)
    _stamp(img, slip, hx_ + 16, hy - slip.height + 3)
    # wall safe set into the back
    R.quad(img, [(SAFE_X0 - 2, SAFE_Y0 - 2, SAFE_Z), (SAFE_X1 + 2, SAFE_Y0 - 2, SAFE_Z), (SAFE_X1 + 2, SAFE_Y1 + 2, SAFE_Z),
                 (SAFE_X0 - 2, SAFE_Y1 + 2, SAFE_Z)], STEEL_D)
    if not safe_open:
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z + 0.5), (SAFE_X1, SAFE_Y0, SAFE_Z + 0.5), (SAFE_X1, SAFE_Y1, SAFE_Z + 0.5),
                     (SAFE_X0, SAFE_Y1, SAFE_Z + 0.5)], STEEL, STEEL_L)
        cx, cy = R.P((SAFE_X0 + SAFE_X1) / 2, (SAFE_Y0 + SAFE_Y1) / 2, SAFE_Z + 1)
        d = ImageDraw.Draw(img)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=STEEL_D, outline=GOLD)
        d.line([(cx, cy - 4), (cx, cy - 1)], fill=GOLD)
        hx_, hy = R.P(SAFE_X1 - 4, (SAFE_Y0 + SAFE_Y1) / 2, SAFE_Z + 1)
        d.line([(hx_, hy - 3), (hx_, hy + 3)], fill=STEEL_L, width=2)
    else:
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z - 0.5), (SAFE_X1, SAFE_Y0, SAFE_Z - 0.5), (SAFE_X1, SAFE_Y1, SAFE_Z - 0.5),
                     (SAFE_X0, SAFE_Y1, SAFE_Z - 0.5)], hx("121214"))
        # heavy door swung open on its left hinge
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z), (SAFE_X0, SAFE_Y0, SAFE_Z + 22), (SAFE_X0, SAFE_Y1, SAFE_Z + 22),
                     (SAFE_X0, SAFE_Y1, SAFE_Z)], STEEL, STEEL_L)
        if box:
            R.box(img, SAFE_X0 + 6, SAFE_X1 - 6, SAFE_Y0, SAFE_Y0 + 8, SAFE_Z - 0.4, SAFE_Z + 0.2, hx("b08a3a"), top=hx("d8b050"))
            px, py = R.P((SAFE_X0 + SAFE_X1) / 2, SAFE_Y0 + 4, SAFE_Z + 0.3)
            ImageDraw.Draw(img).point((px, py), fill=hx("6a5020"))
    # both doors flung wide
    for x in (X0, X1):
        R.quad(img, [(x, 6, Z1), (x, 6, Z1 + 24), (x, 100, Z1 + 24), (x, 100, Z1)], hx("75492b"), hx("3e2615"))
        R.quad(img, [(x, 12, Z1 + 4), (x, 12, Z1 + 20), (x, 94, Z1 + 20), (x, 94, Z1 + 4)], None, hx("8e6040"))


def desk(img, drawer_open=False, paper=False):
    X0, X1, Z0, Z1 = DESK_X0, DESK_X1, DESK_Z0, DESK_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0], a[1] - 4, b[0] + 6, a[1] + 3], 0.35, 3)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z0 + 2), (x, 24, Z0 + 2), WOOD_D, 2)
    R.box(img, X0, X1, 20, 26, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.box(img, X0 - 1, X1 + 1, 26, 28, Z0, Z1 + 1, hx("7d5232"), top=hx("8e6040"), side=WOOD_D)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z1 - 2), (x, 20, Z1 - 2), WOOD_D, 2)
    # left drawer: locked, brass keyhole; right drawer: yanked out and dumped
    c = X0 + 6
    R.quad(img, [(c, 21, Z1), (c + 24, 21, Z1), (c + 24, 25, Z1), (c, 25, Z1)], None, WOOD_D)
    R.line(img, (c + 11, 23, Z1), (c + 13, 23, Z1), GOLD)
    c2 = X1 - 30
    R.quad(img, [(c2, 21, Z1), (c2 + 24, 21, Z1), (c2 + 24, 25, Z1), (c2, 25, Z1)], hx("120a06"))
    R.box(img, c2 + 6, c2 + 30, 0, 4, Z1 + 14, Z1 + 26, WOOD, top=hx("2a1a10"), side=WOOD_D)
    # stationery scattered, inkwell tipped over and bleeding across a letter to the edge
    d = ImageDraw.Draw(img)
    sheet(img, 157, 120, 10, 5, envelope=True, seal=hx("a02828"))
    sheet(img, 170, 119, 13, 6, lines=2, seed=3, crease=True)
    sheet(img, 179, 122, 12, 5, skew=1, lines=2, seed=4)
    d.line([(185, 127), (194, 125)], fill=hx("101014"), width=1)
    d.point((195, 125), fill=GOLD)
    d.polygon([(193, 123), (199, 122), (204, 124), (202, 127), (197, 128), (194, 126)], fill=hx("141a2e"))
    d.line([(198, 128), (198, 131)], fill=hx("141a2e"))
    d.point((198, 132), fill=hx("141a2e"))
    R.box(img, 202, 210, 28, 30.5, 10, 14, hx("2e4646"), top=hx("5a7a7a"))
    ix, iy = R.P(201, 29.5, 12)
    d.rectangle([ix - 1, iy - 1, ix, iy], fill=GOLD_D)
    d.point((ix + 4, iy - 1), fill=hx("a8c8c8"))
    if drawer_open:
        R.box(img, c, c + 24, 20, 25, Z1, Z1 + 12, hx("6a4428"), top=hx("1e120a"), side=WOOD_D)
        R.line(img, (c + 11, 23, Z1 + 12), (c + 13, 23, Z1 + 12), GOLD)
        if paper:
            R.quad(img, [(c + 6, 25.1, Z1 + 3), (c + 18, 25.1, Z1 + 2), (c + 19, 25.1, Z1 + 9), (c + 7, 25.1, Z1 + 10)],
                   hx("f4ecdc"))
            R.line(img, (c + 8, 25.2, Z1 + 5), (c + 16, 25.2, Z1 + 5), hx("3a3a6a"))
            R.line(img, (c + 8, 25.2, Z1 + 7), (c + 15, 25.2, Z1 + 7), hx("3a3a6a"))


def bed(img):
    """hotel.bed's frame with the linen torn apart: coverlet heaped at the foot, the ticking bared and slit open,
    the top sheet dragged over the side and the pillows gutted."""
    X0, X1, Z0, Z1 = 264, 380, 4, 62
    d = ImageDraw.Draw(img)
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 4, a[1] - 6, b[0] + 6, a[1] + 4], 0.45, 4)
    R.box(img, X1 - 4, X1, 0, 56, Z0, Z1, WOOD_D, top=GOLD_D, side=BURGUNDY)
    R.quad(img, [(X1 - 4, 22, Z0 + 3), (X1 - 4, 22, Z1 - 3), (X1 - 4, 52, Z1 - 3), (X1 - 4, 52, Z0 + 3)], BURGUNDY_L, mul(BURGUNDY, 0.6))
    for y in (30, 38, 46):
        for z in range(Z0 + 8, Z1 - 4, 9):
            px, py = R.P(X1 - 4, y, z + (4 if y == 38 else 0))
            img.putpixel((int(px), int(py)), mul(BURGUNDY, 0.55))
    R.box(img, X0, X1 - 4, 6, 16, Z0, Z1, WOOD, top=hx("8a5e3c"), side=WOOD_D)
    R.box(img, X0 + 1, X1 - 5, 16, 26, Z0 + 1, Z1 - 1, hx("e4d6bc"), top=hx("f4ecdc"), side=hx("c4b49a"))
    # the mattress's piped edge
    R.line(img, (X0 + 1, 25, Z1 - 1), (X1 - 5, 25, Z1 - 1), hx("b8a686"))
    R.line(img, (X0 + 1, 17, Z1 - 1), (X1 - 5, 17, Z1 - 1), hx("b8a686"))
    # bottom sheet dragged back: striped ticking bared in the middle and slit open, stuffing bursting out
    T0, T1 = X0 + 28, X0 + 84
    R.quad(img, [(T0, 26.05, Z0 + 1), (T1, 26.05, Z0 + 1), (T1 - 4, 26.05, Z1 - 1), (T0, 26.05, Z1 - 1)], hx("ddd6c4"))
    for x in range(T0 + 2, T1 - 3, 4):
        R.line(img, (x, 26.1, Z0 + 2), (x - 2, 26.1, Z1 - 2), hx("7c88a0"))
    R.line(img, (T0, 25.2, Z1 - 1), (T1 - 4, 25.2, Z1 - 1), hx("7c88a0"))
    s0, s1 = R.P(T0 + 8, 26.2, Z0 + 12), R.P(T1 - 10, 26.2, Z1 - 14)
    d.line([s0, s1], fill=hx("2a2018"), width=2)
    rnd = random.Random(62)
    for _ in range(14):
        t = rnd.random()
        x, y = s0[0] + (s1[0] - s0[0]) * t, s0[1] + (s1[1] - s0[1]) * t
        d.point((x + rnd.randint(-1, 1), y - rnd.randint(1, 2)), fill=hx("fffcf2"))
        d.point((x + rnd.randint(-1, 1), y + rnd.randint(-1, 0)), fill=hx("e8e2d4"))
    for t in (0.2, 0.45, 0.7):
        x, y = s0[0] + (s1[0] - s0[0]) * t, s0[1] + (s1[1] - s0[1]) * t
        d.rectangle([x - 1, y - 2, x + 1, y - 1], fill=hx("fbf6ea"))
        d.point((x, y), fill=hx("d8d0c0"))
    # the pulled-back edge of the bottom sheet, rolled up
    R.line(img, (T1, 26.3, Z0 + 1), (T1 - 4, 26.3, Z1 - 1), LINEN_L, 2)
    R.line(img, (T1 + 1, 26.2, Z0 + 1), (T1 - 3, 26.2, Z1 - 1), LINEN_D)
    for (p, q) in (((T1 + 8, 26.1, Z0 + 10), (T1 + 30, 26.1, Z1 - 12)), ((T1 + 20, 26.1, Z0 + 4), (T1 + 40, 26.1, Z0 + 24))):
        R.line(img, p, q, hx("cbbca4"))
    # pillows at the head: one where it was, one knocked askew and gutted
    p1x, p1y = R.P(X1 - 26, 26, Z0 + 4)
    _stamp(img, pillow(22, 9), p1x, p1y - 3)
    p2x, p2y = R.P(X1 - 42, 26, Z0 + 28)
    _stamp(img, pillow(22, 10, gash=True, seed=9), p2x, p2y - 3)
    feathers(img, (int(p2x) - 6, int(p2y) - 6, int(p2x) + 30, int(p2y) + 12), 10, 7)
    # the green coverlet thrown in a heap at the foot, one corner slumped over the side, gold trim and fringe
    hx0, hy0 = R.P(X0, 26, Z1)
    heap = Image.new("RGBA", (42, 34), (0, 0, 0, 0))
    h = ImageDraw.Draw(heap)
    G, GD, GL = GREEN + (255,), mul(GREEN, 0.62) + (255,), GREEN_L + (255,)
    h.polygon([(1, 15), (3, 8), (9, 4), (16, 6), (22, 2), (30, 3), (36, 8), (40, 15), (40, 17), (1, 17)], fill=G)
    drape = [(0, 15), (31, 15), (34, 27), (28, 25), (22, 30), (15, 26), (8, 29), (0, 27)]
    h.polygon(drape, fill=mul(GREEN, 0.84) + (255,))
    for (p, q) in (((5, 9), (10, 5)), ((17, 7), (23, 3)), ((29, 5), (35, 9)), ((12, 12), (19, 10))):
        h.line([p, q], fill=GL)
    for (p, q) in (((10, 9), (16, 12)), ((24, 6), (28, 12)), ((32, 12), (38, 14)), ((4, 13), (9, 11))):
        h.line([p, q], fill=GD)
    for (p, q, c) in (((7, 17), (6, 27), GD), ((19, 17), (21, 28), GD), ((13, 17), (12, 25), GL), ((27, 17), (29, 24), GL)):
        h.line([p, q], fill=c)
    h.line(drape[2:], fill=GOLD + (255,))
    for (x, y) in drape[3:]:
        h.point((x, y + 1), fill=GOLD_D + (255,))
    for x in range(1, 33, 2):
        h.point((x, 30 if x < 24 else 29), fill=GOLD_D + (255,))
    _stamp(img, _outlined(heap, hx("142218")), hx0 - 1, hy0 - 16)
    # the top sheet dragged off the side, hanging over the rail in soft folds
    L, Rr = X0 + 54, X0 + 88
    R.quad(img, [(L - 4, 26.4, Z1 - 16), (Rr - 2, 26.4, Z1 - 20), (Rr, 26.4, Z1), (L, 26.4, Z1)], LINEN)
    R.line(img, (L + 6, 26.5, Z1 - 12), (Rr - 8, 26.5, Z1 - 4), LINEN_D)
    R.line(img, (L, 26.5, Z1 - 8), (L + 10, 26.5, Z1 - 15), LINEN_L)
    tl, tr = R.P(L, 26, Z1 + 1), R.P(Rr, 26, Z1 + 1)
    bot = R.P(L, 3, Z1 + 3)[1]
    tones = (LINEN_D, hx("d4c6aa"), LINEN, LINEN_L)
    x0, x1 = int(tl[0]), int(tr[0])
    for x in range(x0 - 1, x1 + 2):
        u = (x - x0) / (x1 - x0)
        ph = u * math.pi * 2 * 4.3 + 0.8 * math.sin(u * 7)
        s = math.sin(ph)
        hem = bot - 2 + 2.2 * math.cos(ph) + 2 * u
        for y in range(int(tl[1]), int(hem) + 1):
            k = (y - tl[1]) / max(1, hem - tl[1])
            lvl = s * min(1.0, 0.3 + k)
            d.point((x, y), fill=tones[max(0, min(3, int((lvl + 1) * 2)))])
        d.point((x, int(hem) + 1), fill=LINEN_O)
    d.line([tl, tr], fill=LINEN_L)
    d.line([(x0 - 2, tl[1]), (x0 - 2, bot - 1)], fill=LINEN_O)
    d.line([(x1 + 2, tr[1]), (x1 + 2, bot + 1)], fill=LINEN_O)
    # footboard and posts in front
    R.box(img, X0 - 4, X0, 0, 32, Z0, Z1 + 1, WOOD, top=hx("8a5e3c"), side=hx("5a3822"))
    R.quad(img, [(X0 - 4, 10, Z0 + 5), (X0 - 4, 10, Z1 - 4), (X0 - 4, 27, Z1 - 4), (X0 - 4, 27, Z0 + 5)], None, WOOD_D)
    for (x, top) in ((X0 - 2, 36), (X1 - 2, 60)):
        R.line(img, (x, 0, Z1 + 1), (x, top, Z1 + 1), WOOD_D, 3)
        px, py = R.P(x, top + 1, Z1 + 1)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD)
    light(img, "polygon", [R.P(X0, 27, Z0), R.P(X1 - 30, 27, Z0), R.P(X1 - 30, 27, Z1), R.P(X0, 27, Z1)], hx("fff4df"), 0.08, 6)


def mess(img):
    """Everything the searchers threw on the floor."""
    d = ImageDraw.Draw(img)
    # the desk chair, on its back
    R.box(img, 186, 210, 0, 3, 34, 48, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))
    R.box(img, 210, 214, 0, 14, 34, 48, mul(WOOD, 0.85), top=WOOD, side=WOOD_D)
    for z in (36, 46):
        R.line(img, (186, 6, z), (172, 8, z), WOOD_D, 2)
    # papers and letters, a bundle of them still tied in ribbon, and the emptied handbag
    dx, dy = R.P(96, 0, 110)
    spr = _crumple(dress(20, 50, LILAC, folds=3).rotate(90, expand=True), 1, 26, 0.6)
    _stamp(img, spr, dx - 8, dy - 9)
    for (x, y, w, h, sk, seed) in ((121, 170, 12, 6, 0, 1), (136, 178, 11, 5, 1, 2), (233, 172, 12, 6, -1, 3),
                                   (251, 186, 12, 6, 0, 4), (102, 187, 11, 6, 1, 5), (305, 192, 12, 6, 0, 6)):
        sheet(img, x, y, w, h, skew=sk, lines=2, seed=seed, crease=seed % 2 == 0)
    for (x, y, sk) in ((160, 196, 0), (163, 193, 1), (158, 190, -1)):
        sheet(img, x, y, 10, 5, skew=sk, col=hx("e6dcc4"), envelope=True)
    d.line([(158, 194), (171, 193)], fill=hx("b02838"))
    d.line([(165, 190), (165, 199)], fill=hx("b02838"))
    d.point([(164, 193), (166, 193)], fill=hx("e05060"))
    sheet(img, 176, 199, 10, 5, skew=1, col=hx("e6dcc4"), envelope=True, seal=hx("a02828"))
    bx, by = R.P(222, 0, 100)
    bag = Image.new("RGBA", (20, 14), (0, 0, 0, 0))
    b = ImageDraw.Draw(bag)
    b.polygon([(3, 5), (14, 5), (16, 12), (1, 12)], fill=hx("6a2c50"))
    b.line([(2, 11), (15, 11)], fill=hx("421a32"))
    b.line([(3, 6), (14, 6)], fill=hx("8e4a72"))
    b.ellipse([12, 4, 18, 10], fill=hx("1a0c14"))
    b.line([(3, 5), (14, 5)], fill=GOLD)
    b.point([(8, 4), (9, 4)], fill=GOLD)
    for i, (x, y) in enumerate(((3, 4), (4, 2), (6, 1), (8, 0), (10, 0), (12, 1), (13, 3))):
        b.point((x, y), fill=GOLD if i % 2 == 0 else GOLD_D)
    _stamp(img, _outlined(bag, hx("140a10")), bx, by - 4)
    d.ellipse([bx + 21, by + 3, bx + 25, by + 6], fill=GOLD, outline=GOLD_D)
    d.rectangle([bx + 19, by + 8, bx + 22, by + 9], fill=hx("b02030"))
    d.point((bx + 23, by + 8), fill=GOLD)
    d.point([(bx + 27, by + 6), (bx + 26, by + 9)], fill=hx("c0c4c8"))
    # a fox-fur stole, head, banded pelts and a white-tipped brush, dragged across the rug
    sx, sy = R.P(330, 0, 120)
    stole = Image.new("RGBA", (60, 16), (0, 0, 0, 0))
    sp = stole.load()
    rnd = random.Random(507)
    for x in range(9, 58):
        t = (x - 9) / 48
        cy = 8 + 2.2 * math.sin(t * math.pi * 1.3)
        half = 2.8 if t < 0.72 else 3.4 - 2.6 * ((t - 0.72) / 0.28) ** 1.5
        for y in range(16):
            off = y + 0.5 - cy
            if abs(off) <= half + (0.9 if rnd.random() < 0.5 else 0):
                c = hx("e4b47a") if off < -half / 3 else hx("7a4426") if off > half / 2 else hx("b8743e")
                if t > 0.9:
                    c = hx("f6efe2")
                elif t < 0.72 and (x - 9) % 8 in (0, 1) and abs(off) < half - 0.5:
                    c = mul(c, 0.72)
                sp[x, y] = c + (255,)
    s = ImageDraw.Draw(stole)
    s.polygon([(1, 9), (6, 6), (11, 5), (11, 12), (6, 11)], fill=hx("b8743e") + (255,))
    s.line([(2, 10), (6, 11)], fill=hx("f6efe2") + (255,))
    s.polygon([(7, 6), (8, 3), (10, 5)], fill=hx("5a3018") + (255,))
    s.point([(1, 9)], fill=(16, 10, 8, 255))
    s.point([(5, 8)], fill=(16, 10, 8, 255))
    _stamp(img, _outlined(stole, hx("2a1a10")), sx - 8, sy - 9)
    # a silk stocking: dark welt and lace at the top, a seam down the back, the foot turned over at the end
    a = R.P(380, 0, 96)
    st = Image.new("RGBA", (38, 14), (0, 0, 0, 0))
    sp = st.load()
    for x in range(1, 31):
        t = x / 30
        cy = 4 + 1.2 * math.sin(t * math.pi * 1.6) + 5 * t
        half = 2.4 - 1.2 * t
        for y in range(14):
            off = y + 0.5 - cy
            if abs(off) <= half:
                c = hx("eccaa6") if off < -half / 3 else hx("a8805e") if off > half / 3 else hx("d4ae88")
                if x < 5:
                    c = hx("f8e8d4") if x == 1 else hx("7a5040")
                sp[x, y] = c + (255,)
    fy = int(4 + 1.2 * math.sin(math.pi * 1.6) + 5)
    ImageDraw.Draw(st).polygon([(29, fy - 1), (33, fy), (36, fy + 2), (35, fy + 4), (31, fy + 3), (29, fy + 2)],
                               fill=hx("d4ae88") + (255,))
    ImageDraw.Draw(st).point([(30, fy + 2), (34, fy + 3)], fill=hx("a8805e") + (255,))
    _stamp(img, _outlined(st, hx("3a2418")), a[0] - 2, a[1] - 5)
    # her hatbox, knocked over, lid rolled off and tissue paper spilling
    hx_, hy = R.P(134, 0, 36)
    d.rectangle([hx_ - 1, hy - 9, hx_ + 13, hy + 1], fill=hx("e8d8c0"), outline=hx("3a2a20"))
    for x in range(int(hx_) + 1, int(hx_) + 13, 3):
        d.line([(x, hy - 8), (x, hy)], fill=hx("c07a8a"))
    d.ellipse([hx_ + 10, hy - 10, hx_ + 17, hy + 2], fill=hx("2a1a1a"), outline=hx("3a2a20"))
    d.ellipse([hx_ + 12, hy - 7, hx_ + 18, hy - 1], fill=hx("fbf6ea"))
    d.ellipse([hx_ - 10, hy - 2, hx_ + 4, hy + 4], fill=hx("c07a8a"), outline=hx("3a2a20"))
    d.ellipse([hx_ - 7, hy - 1, hx_ + 1, hy + 2], fill=hx("e8d8c0"))
    d.line([(hx_ - 3, hy - 2), (hx_ - 3, hy + 4)], fill=hx("8a2a3a"))
    # a pillow thrown down and gutted, its feathers everywhere
    px_, py_ = R.P(256, 0, 76)
    _stamp(img, pillow(24, 11, gash=True, seed=5), px_ - 3, py_ - 10)
    feathers(img, (236, 166, 304, 202), 22, 76)
    # the nightstand lamp knocked over, shade rolled away
    R.quad(img, [(412, 0.2, 40), (424, 0.2, 38), (426, 0.2, 48), (414, 0.2, 50)], hx("efe2c4"), GOLD_D)
    R.line(img, (402, 1, 34), (414, 1, 42), GOLD_D, 2)
    # vanity: both drawers pulled out, a perfume bottle spilt
    R.box(img, 420, 438, 14, 20, 22, 32, mul(WOOD, 0.92), top=hx("2a1a10"), side=WOOD_D)
    R.box(img, 450, 468, 0, 6, 34, 44, mul(WOOD, 0.92), top=hx("2a1a10"), side=WOOD_D)
    R.quad(img, [(440, 0.2, 52), (452, 0.2, 54), (448, 0.2, 60)], hx("c9a0b8"))


def paint(closet_open=False, safe_open=False, box=False, drawer_open=False, paper=False):
    img = Image.new("RGB", (W, H))
    hotel.shell(img)
    crooked_painting(img)
    hotel.floor(img)
    hotel.door(img)
    window_night(img)
    hotel.sconces(img)
    closet(img, closet_open, safe_open, box)
    desk(img, drawer_open, paper)
    bed(img)
    hotel.nightstand(img)
    hotel.vanity(img)
    mess(img)
    hotel.chandelier(img)
    img = tall(img, hotel.ceiling)
    # night: the only light comes from the sconces and the city outside
    dark = Image.new("RGB", img.size, (70, 70, 120))
    img = ImageChops.multiply(img, Image.blend(dark, Image.new("RGB", img.size, (255, 240, 210)), 0.55))
    light(img, "ellipse", [96, 40, 296, 140], hx("ffe0a0"), 0.18, 18)
    light(img, "polygon", [(166, 134), (222, 134), (300, H + TOP - 1), (150, H + TOP - 1)], hx("6a80c0"), 0.1, 12)
    vignette(img, 0.4, tint=(30, 24, 40), blur=34)
    return img


def _bbox(a, b):
    return ImageChops.difference(a, b).getbbox()


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "eleanor_room.png")
    states = {
        "closet": pixelize(paint(closet_open=True), pal),
        "safe": pixelize(paint(closet_open=True, safe_open=True), pal),
        "box": pixelize(paint(closet_open=True, safe_open=True, box=True), pal),
        "drawer": pixelize(paint(drawer_open=True), pal),
        "paper": pixelize(paint(drawer_open=True, paper=True), pal),
    }
    # each overlay is cut where it differs from the layer it sits on; positions go into eleanor_room.tscn
    for name, under, over in (("closet_open", px, "closet"), ("safe_open", states["closet"], "safe"),
                              ("brass_box", states["safe"], "box"), ("drawer_open", px, "drawer"),
                              ("paper", states["drawer"], "paper")):
        box = _bbox(under, states[over])
        save(states[over].crop(box), "rooms", f"eleanor_room_{name}.png")
        print(f"  eleanor_room_{name}.png at {box[:2]}")
    return px
