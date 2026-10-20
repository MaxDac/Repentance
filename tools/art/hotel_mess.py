"""The Aurelian, room 507: the room Eleanor had the night she vanished. Luxurious, lived in, and turned upside down.

Overlays: the closet thrown open (with the wall safe), the safe door open, the brass box inside it, and the
lockpicked desk drawer with the slip of paper. For the First Interlude: the tidy closet opened, its safe standing half
open, and the brass box put inside."""
import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import W, H, TOP, tall, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save, city
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


def _sheer(img, pts, seed):
    """A translucent lace sheer: the night shows through it, soft vertical folds and a scalloped, dotted hem."""
    layer = Image.new("RGB", img.size, hx("e8dcc6"))
    mask = Image.new("L", img.size, 0)
    m = ImageDraw.Draw(mask)
    m.polygon(pts, fill=96)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
    for x in range(bx0 + 2, bx1, 4):
        m.line([(x, by0), (x + 1, by1)], fill=60)
    img.paste(layer, (0, 0), mask)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for x in range(bx0, bx1 + 1):
        if (x - bx0) % 3 != 2:
            d.point((x, by1 - 1 + (x % 2)), fill=hx("efe6d4"))
        if (x - bx0) % 4 == 1:
            d.point((x, by1 - 4), fill=hx("d8ccb4"))
    for _ in range(6):
        d.point((rnd.randint(bx0 + 1, bx1 - 1), rnd.randint(by1 - 12, by1 - 6)), fill=hx("e0d4bc"))


def _drape(img, box, inside, seed, tie=None, fringe=True):
    """A heavy silk drape in vertical folds: each column shaded by the fold it sits on, a damask sprig every so
    often, a dark edge and gold fringe along the hem (or a ragged edge if torn). inside(x, y) gives its shape."""
    d = ImageDraw.Draw(img)
    tones = (mul(BURGUNDY, 0.5), mul(BURGUNDY, 0.72), BURGUNDY, BURGUNDY_L, mix_(BURGUNDY_L, hx("c87080"), 0.4))
    rnd = random.Random(seed)
    bx0, by0, bx1, by1 = box
    for x in range(bx0, bx1 + 1):
        ys = [y for y in range(by0, by1 + 1) if inside(x, y)]
        if not ys:
            continue
        u = (x - bx0) / max(1, bx1 - bx0)
        s = math.sin(u * math.pi * 2 * 2.5 + 0.6)
        for y in ys:
            k = int(round((s + 1) * 1.6 + (0.6 if u < 0.15 else 0) - (0.8 if y - ys[0] < 2 else 0)))
            c = tones[max(0, min(4, k))]
            if not inside(x - 1, y) or not inside(x + 1, y):
                c = mul(BURGUNDY, 0.42)
            elif (y - by0) % 9 == 4 and (x + (y // 9) * 3) % 7 == 0 and k >= 2:
                c = mix_(c, GOLD_D, 0.45)
            d.point((x, y), fill=c)
        hem = ys[-1]
        if fringe:
            d.point((x, hem + 1), fill=GOLD)
            if x % 2 == 0:
                d.line([(x, hem + 2), (x, hem + 3 + rnd.randint(0, 1))], fill=GOLD_D)
        else:
            d.point((x, hem), fill=mul(BURGUNDY, 0.42))
            if rnd.random() < 0.3:
                d.point((x, hem + 1), fill=mix_(BURGUNDY_L, hx("e8c8b0"), 0.3))
    if tie:
        ty = tie
        xs = [x for x in range(bx0, bx1 + 1) if inside(x, ty)]
        l, r = xs[0], xs[-1]
        d.line([(l - 1, ty - 1), ((l + r) / 2, ty + 1), (r + 1, ty - 1)], fill=GOLD, width=2)
        d.line([(l - 1, ty + 1), ((l + r) / 2, ty + 3), (r + 1, ty + 1)], fill=GOLD_D)
        tx = l - 1
        d.ellipse([tx - 2, ty, tx + 1, ty + 3], fill=GOLD)
        d.polygon([(tx - 2, ty + 3), (tx + 1, ty + 3), (tx + 2, ty + 11), (tx - 3, ty + 11)], fill=GOLD_D)
        for k in (-3, -1, 1):
            d.line([(tx + k * 0.4, ty + 4), (tx + k, ty + 11)], fill=GOLD)


def mix_(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def window_night(img, tidy=False):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 156, 28, 230, 100
    # the rain is animated in-game (Rain node in eleanor_room.tscn)
    city(img, (x0, y0, x1, y1), seed=507, lit=0.3, rain=False)
    # lace sheers behind the drapes: the right one hanging true, the left one half torn from its hooks
    _sheer(img, [(x1 - 22, y0), (x1, y0), (x1, y1), (x1 - 18, y1)], 71)
    if tidy:
        _sheer(img, [(x0, y0), (x0 + 22, y0), (x0 + 18, y1), (x0, y1)], 72)
    else:
        _sheer(img, [(x0, y0), (x0 + 8, y0), (x0 + 20, y1 - 18), (x0 + 12, y1 - 6), (x0, y1 - 10)], 72)
    # frame: outer casing with a lit inner bead, the sash bars, a brass sash lock on the meeting rail
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], outline=WOOD_D, width=4)
    d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], outline=mul(WOOD_D, 0.7))
    d.line([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4)], fill=hx("8a5e3c"))
    d.line([(x0 - 4, y0 - 4), (x0 - 4, y1 + 4)], fill=hx("6b4428"))
    d.line([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1)], fill=hx("4a3020"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=WOOD_D, width=3)
    d.line([((x0 + x1) // 2 - 1, y0), ((x0 + x1) // 2 - 1, y1)], fill=hx("6b4428"))
    d.line([(x0, 60), (x1, 60)], fill=WOOD_D, width=2)
    d.line([(x0, 59), (x1, 59)], fill=hx("6b4428"))
    for gx in ((x0 + x1) // 2 - 4, (x0 + x1) // 2 + 2):
        d.rectangle([gx, 58, gx + 2, 61], fill=GOLD_D)
        d.point((gx + 1, 58), fill=GOLD)
    # sill with a moulded nose and two carved brackets underneath
    d.rectangle([x0 - 10, y1 + 4, x1 + 10, y1 + 7], fill=hx("8c6748"))
    d.line([(x0 - 10, y1 + 4), (x1 + 10, y1 + 4)], fill=hx("b08a64"))
    d.line([(x0 - 10, y1 + 7), (x1 + 10, y1 + 7)], fill=WOOD_D)
    d.line([(x0 - 8, y1 + 8), (x1 + 8, y1 + 8)], fill=mul(WOOD_D, 0.8))
    for bx in (x0 + 2, x1 - 6):
        d.polygon([(bx, y1 + 8), (bx + 5, y1 + 8), (bx + 4, y1 + 12), (bx + 2, y1 + 14), (bx + 1, y1 + 12)],
                  fill=hx("6b4428"))
        d.point((bx + 2, y1 + 10), fill=WOOD_D)
        d.line([(bx, y1 + 8), (bx + 1, y1 + 12)], fill=hx("8c6748"))
    # brass pole on brackets, ball finials; the left bracket has given way and the pole sags off it
    ry = y0 - 10
    d.rectangle([x1 + 15, ry - 3, x1 + 17, ry + 6], fill=GOLD_D)
    d.rectangle([x0 - 22, ry - 3, x0 - 20, ry + 6], fill=GOLD_D)
    d.point((x0 - 21, ry - 2), fill=GOLD)
    d.point((x1 + 16, ry - 2), fill=GOLD)
    d.line([(x0 + 18, ry), (x1 + 19, ry)], fill=GOLD, width=2)
    d.line([(x0 + 18, ry + 2), (x1 + 19, ry + 2)], fill=GOLD_D)
    d.line([(x0 + 18, ry - 1), (x1 + 19, ry - 1)], fill=hx("f0d890"))
    if tidy:
        d.line([(x0 - 19, ry), (x0 + 19, ry)], fill=GOLD, width=2)
        d.line([(x0 - 19, ry + 2), (x0 + 19, ry + 2)], fill=GOLD_D)
        d.line([(x0 - 19, ry - 1), (x0 + 19, ry - 1)], fill=hx("f0d890"))
        ends = ((x1 + 21, ry + 1), (x0 - 21, ry + 1))
    else:
        d.line([(x0 + 19, ry), (x0 - 8, ry + 14)], fill=GOLD, width=2)
        d.line([(x0 + 19, ry + 2), (x0 - 8, ry + 16)], fill=GOLD_D)
        ends = ((x1 + 21, ry + 1), (x0 - 10, ry + 16))
    for (fx, fy) in ends:
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=GOLD_D)
        d.ellipse([fx - 3, fy - 3, fx + 2, fy + 2], fill=GOLD)
        d.point((fx - 1, fy - 2), fill=hx("fff0c0"))
        d.line([(fx - 4 if fx > x1 else fx + 4, fy - 1), (fx - 4 if fx > x1 else fx + 4, fy + 1)], fill=GOLD_D)
    # rings on the pole, a couple slid down the sagging end
    for rx in range(x1 - 4, x1 + 14, 4):
        d.ellipse([rx - 1, ry - 2, rx + 2, ry + 3], outline=GOLD_D)
    if tidy:
        for rx in range(x0 - 16, x0 + 4, 4):
            d.ellipse([rx - 1, ry - 2, rx + 2, ry + 3], outline=GOLD_D)
        # both drapes hanging, gathered under their rings and tied back with tasselled cords
        def left(x, y):
            if y < ry + 3 or y > y1 + 30 or x < x0 - 16:
                return False
            if y < y0 + 40:
                return x <= x0 + 6
            if y < y0 + 50:
                return x <= x0 + 6 - (y - y0 - 40) * 0.7
            k = (y - y0 - 50) / (y1 + 30 - y0 - 50)
            return x <= x0 - 1 + 9 * k ** 0.8
        _drape(img, (x0 - 16, ry + 3, x0 + 9, y1 + 30), left, 81, tie=y0 + 47)
        for x in range(x0 - 15, x0 + 6, 3):
            d.line([(x, ry + 3), (x, ry + 6)], fill=mul(BURGUNDY, 0.5))
            d.point((x + 1, ry + 4), fill=BURGUNDY_L)
    else:
        for t in (0.3, 0.55, 0.8):
            rx, rry = x0 + 19 + (-27) * t, ry + 14 * t + 1
            d.ellipse([rx - 1, rry - 2, rx + 2, rry + 3], outline=GOLD_D)
    # the left drape torn half off: still hooked on the sagging pole, ripped diagonally and hanging in a rag
    def pole(x):
        return ry + 1 + 14 * min(1.0, max(0.0, (x0 + 19 - x) / 27))
    rag = random.Random(82)
    tear = {x: rag.randint(-2, 2) for x in range(x0 - 20, x0 + 20)}
    def torn(x, y):
        if not x0 - 9 <= x <= x0 + 12:
            return False
        bottom = y0 + 62 - (x - (x0 - 9)) * 1.9 + tear[x]
        return pole(x) + 2 <= y <= bottom
    if not tidy:
        _drape(img, (x0 - 9, ry, x0 + 12, y0 + 66), torn, 81, fringe=False)
    # the right drape still hanging, gathered under its rings and tied back with a tasselled cord
    def right(x, y):
        if y < ry + 3 or y > y1 + 30 or x > x1 + 16:
            return False
        if y < y0 + 40:
            return x >= x1 - 6
        if y < y0 + 50:
            return x >= x1 - 6 + (y - y0 - 40) * 0.7
        k = (y - y0 - 50) / (y1 + 30 - y0 - 50)
        return x >= x1 + 1 - 9 * k ** 0.8
    _drape(img, (x1 - 9, ry + 3, x1 + 16, y1 + 30), right, 83, tie=y0 + 47)
    for x in range(x1 - 5, x1 + 16, 3):
        d.line([(x, ry + 3), (x, ry + 6)], fill=mul(BURGUNDY, 0.5))
        d.point((x + 1, ry + 4), fill=BURGUNDY_L)


def sconces(img):
    """Gilt wall sconces either side of the window: a shield backplate with a drop finial, a scrolled arm, a cup
    hung with crystal drops and a pleated silk shade trimmed in gold, throwing light up and down the wall."""
    d = ImageDraw.Draw(img)
    shade, shade_l, shade_d = hx("efe2c4"), hx("fff6e0"), hx("c8b48e")
    for cx in (136, 254):
        light(img, "polygon", [(cx - 6, 44), (cx + 6, 44), (cx + 14, 26), (cx - 14, 26)], hx("fff0cc"), 0.22, 3)
        light(img, "polygon", [(cx - 8, 56), (cx + 8, 56), (cx + 16, 82), (cx - 16, 82)], hx("fff0cc"), 0.12, 4)
        # backplate: a slim shield with a beaded edge, a rosette boss and a drop finial underneath
        d.polygon([(cx - 3, 50), (cx + 3, 50), (cx + 4, 56), (cx + 3, 68), (cx, 72), (cx - 3, 68), (cx - 4, 56)],
                  fill=GOLD_D)
        d.polygon([(cx - 2, 51), (cx + 2, 51), (cx + 3, 56), (cx + 2, 67), (cx, 70), (cx - 2, 67), (cx - 3, 56)],
                  fill=GOLD)
        d.line([(cx - 2, 52), (cx - 2, 66)], fill=hx("f4dc98"))
        d.line([(cx + 2, 53), (cx + 2, 66)], fill=GOLD_D)
        d.ellipse([cx - 2, 61, cx + 2, 65], fill=GOLD_D)
        d.point((cx, 63), fill=hx("f8e4a8"))
        d.line([(cx, 72), (cx, 75)], fill=GOLD_D)
        d.ellipse([cx - 1, 75, cx + 1, 77], fill=GOLD)
        # S-scrolled arm out from the boss up to the candle cup
        d.line([(cx, 63), (cx - 3, 62), (cx - 4, 59), (cx - 2, 57), (cx, 57)], fill=GOLD_D)
        d.line([(cx + 1, 64), (cx + 4, 62), (cx + 4, 59)], fill=GOLD)
        d.point((cx - 4, 60), fill=GOLD)
        # cup and crystal drops
        d.ellipse([cx - 5, 54, cx + 5, 57], fill=GOLD_D)
        d.line([(cx - 4, 54), (cx + 4, 54)], fill=GOLD)
        for k in (-4, -2, 0, 2, 4):
            ln = 2 if k % 4 == 0 else 3
            d.line([(cx + k, 57), (cx + k, 57 + ln)], fill=hx("b8c8d0"))
            d.point((cx + k, 58 + ln), fill=hx("f4fcff"))
        # pleated silk shade: a flared drum, pleats fanning down, gold bands and a fringe
        d.polygon([(cx - 4, 42), (cx + 4, 42), (cx + 7, 53), (cx - 7, 53)], fill=shade)
        for k in range(-3, 4):
            top_x, bot_x = cx + k * 1.1, cx + k * 2
            d.line([(top_x, 43), (bot_x, 52)], fill=shade_d if k % 2 else shade_l)
        d.line([(cx - 4, 42), (cx + 4, 42)], fill=GOLD)
        d.line([(cx - 7, 53), (cx + 7, 53)], fill=GOLD)
        d.line([(cx + 4, 42), (cx + 7, 53)], fill=shade_d)
        d.line([(cx - 4, 42), (cx - 7, 53)], fill=shade_l)
        for x in range(cx - 7, cx + 8, 2):
            d.point((x, 54), fill=GOLD_D)
        d.ellipse([cx - 1, 39, cx + 1, 41], fill=GOLD)
        light(img, "ellipse", [cx - 20, 30, cx + 20, 76], hx("fff4db"), 0.16, 6)


def _landscape(w, h):
    """The canvas: an alpine lake at evening. A sky warming to the horizon with lit cloud banks, pale far peaks
    with snow catching the sun, blue-green mid ranges, a lake holding the sky, dark wooded shores with cypresses
    and a sunlit meadow in front, all with a little brushwork."""
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    hz = h * 13 // 24
    vgrad(im, (0, 0, w - 1, hz), hx("4e6c9e"), hx("f2d6a4"))
    for (cx_, cy_, cw) in ((9, 3, 9), (30, 2, 12), (20, 6, 7), (40, 7, 6)):
        d.line([(cx_ - cw // 2, cy_), (cx_ + cw // 2, cy_)], fill=hx("e8d4c0"))
        d.line([(cx_ - cw // 2 + 2, cy_ - 1), (cx_ + cw // 2 - 2, cy_ - 1)], fill=hx("fff0dc"))
        d.line([(cx_ - cw // 2 + 1, cy_ + 1), (cx_ + cw // 2 - 1, cy_ + 1)], fill=hx("b8a8b8"))
    d.ellipse([w - 13, hz - 6, w - 7, hz], fill=hx("fff2c8"))
    # far range: hazy lilac peaks, sunlit snow on their left faces
    far = [(0, hz), (0, hz - 4), (6, hz - 8), (11, hz - 5), (17, hz - 10), (24, hz - 6), (29, hz - 9), (36, hz - 4),
           (w - 1, hz - 3), (w - 1, hz)]
    d.polygon(far, fill=hx("9a9cb8"))
    for (px_, py_) in ((6, hz - 8), (17, hz - 10), (29, hz - 9)):
        d.polygon([(px_, py_), (px_ - 2, py_ + 2), (px_ + 1, py_ + 2)], fill=hx("f4eef0"))
        d.line([(px_, py_), (px_ + 2, py_ + 3)], fill=hx("b8b8cc"))
    # middle range: blue-green, shaded on the right of each ridge
    mid = [(0, hz + 2), (0, hz - 2), (8, hz - 5), (14, hz - 1), (22, hz - 6), (30, hz - 1), (38, hz - 5), (w - 1, hz - 1),
           (w - 1, hz + 2)]
    d.polygon(mid, fill=hx("4e6e72"))
    for (px_, py_) in ((8, hz - 5), (22, hz - 6), (38, hz - 5)):
        d.polygon([(px_, py_), (px_ + 4, py_ + 5), (px_ + 1, py_ + 5)], fill=hx("344c54"))
        d.line([(px_, py_), (px_ - 3, py_ + 4)], fill=hx("7a9a90"))
    # the lake, mirroring the sky, with a sun glitter and a ripple line
    vgrad(im, (0, hz + 1, w - 1, hz + 4), hx("d8cca8"), hx("7a96a8"))
    d.line([(w - 14, hz + 2), (w - 6, hz + 2)], fill=hx("fff4d0"))
    d.line([(w - 12, hz + 3), (w - 8, hz + 3)], fill=hx("f0dcb0"))
    d.line([(4, hz + 3), (12, hz + 3)], fill=hx("a8b8c0"))
    # wooded near shore: rolling dark hills and cypresses
    near = [(0, h), (0, hz + 3), (7, hz + 1), (15, hz + 4), (w - 18, hz + 5), (w - 8, hz + 2), (w - 1, hz + 3), (w - 1, h)]
    d.polygon(near, fill=hx("3a5a30"))
    for (tx_, th) in ((5, 6), (8, 4), (w - 9, 7), (w - 6, 5), (w - 12, 4)):
        d.polygon([(tx_, hz + 3 - th), (tx_ - 1, hz + 3), (tx_ + 1, hz + 3)], fill=hx("1e3420"))
        d.point((tx_ - 1, hz + 2), fill=hx("4a6a3a"))
    # sunlit meadow in front with a path and flecks of flowers
    d.polygon([(0, h), (0, h - 5), (12, h - 7), (30, h - 6), (w - 1, h - 8), (w - 1, h)], fill=hx("8a9a4a"))
    d.line([(18, h - 6), (22, h - 1)], fill=hx("c8b080"))
    d.line([(19, h - 6), (24, h - 1)], fill=hx("b09868"))
    rnd = random.Random(507)
    for _ in range(14):
        fx, fy = rnd.randrange(w), rnd.randrange(h - 6, h)
        d.point((fx, fy), fill=rnd.choice([hx("e8d070"), hx("f0e8d0"), hx("c86a50"), hx("5a7a34")]))
    noise(im, (0, 0, w - 1, h - 1), 5, 508)
    # old varnish: a faint warm glaze
    return Image.blend(im, Image.new("RGB", im.size, hx("c8a060")), 0.1)


def _gilt_frame(cw, ch):
    """A carved gilt frame round a cw x ch canvas: dark back edge, a bevelled gilt moulding with a bead run, acanthus
    corner ornaments and a shell cresting, then a dark sight edge, a linen liner and a gilt fillet."""
    m = 3  # room for the ornaments standing proud of the moulding
    b = 7
    fw, fh = cw + 2 * b, ch + 2 * b
    im = Image.new("RGBA", (fw + 2 * m, fh + 2 * m), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    gl, g, gd, gdd = hx("f6e0a0"), GOLD, GOLD_D, hx("4a3410")
    x0, y0, x1, y1 = m, m, m + fw - 1, m + fh - 1
    d.rectangle([x0, y0, x1, y1], fill=gdd)
    # the moulding: each side shaded for the light from the upper left, mitred at the corners
    for k, (top, left, right, bot) in enumerate(((gl, gl, g, gd), (g, mix(g, gl, 0.5), gd, mix(gd, gdd, 0.4)),
                                                 (gd, g, mix(gd, gdd, 0.3), g))):
        i = k + 1
        d.line([(x0 + i, y0 + i), (x1 - i, y0 + i)], fill=top)
        d.line([(x0 + i, y1 - i), (x1 - i, y1 - i)], fill=bot)
        d.line([(x0 + i, y0 + i), (x0 + i, y1 - i)], fill=left)
        d.line([(x1 - i, y0 + i + 1), (x1 - i, y1 - i)], fill=right)
    # bead run along the middle of the moulding
    for xx in range(x0 + 4, x1 - 3, 2):
        d.point((xx, y0 + 2), fill=hx("fff4c8"))
        d.point((xx, y1 - 2), fill=gdd)
    for yy in range(y0 + 4, y1 - 3, 2):
        d.point((x0 + 2, yy), fill=hx("fff4c8"))
        d.point((x1 - 2, yy), fill=gdd)
    # sight edge, linen liner (shaded under the top rail) and the gilt fillet round the canvas
    d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], fill=gdd)
    d.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], fill=hx("d8cbb0"))
    d.line([(x0 + 5, y0 + 5), (x1 - 5, y0 + 5)], fill=hx("a8987a"))
    d.line([(x0 + 5, y0 + 5), (x0 + 5, y1 - 5)], fill=hx("b8a888"))
    d.rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], outline=g)
    d.line([(x0 + 6, y1 - 6), (x1 - 6, y1 - 6)], fill=gl)
    # acanthus corner ornaments: a rosette on the mitre with leaves curling out along both rails
    for (cx_, cy_, sx, sy) in ((x0 + 1, y0 + 1, 1, 1), (x1 - 1, y0 + 1, -1, 1), (x0 + 1, y1 - 1, 1, -1),
                               (x1 - 1, y1 - 1, -1, -1)):
        d.ellipse([cx_ - 3, cy_ - 3, cx_ + 3, cy_ + 3], fill=gd)
        d.ellipse([cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2], fill=g)
        d.point((cx_ - 1, cy_ - 1), fill=gl)
        d.point((cx_, cy_), fill=hx("fff4c8"))
        d.point((cx_ + 1, cy_ + 1), fill=gdd)
        d.line([(cx_ + 3 * sx, cy_), (cx_ + 6 * sx, cy_ - sy)], fill=g)
        d.line([(cx_, cy_ + 3 * sy), (cx_ - sx, cy_ + 6 * sy)], fill=g)
        d.point((cx_ + 5 * sx, cy_), fill=gd)
        d.point((cx_, cy_ + 5 * sy), fill=gd)
    # shell cresting in the middle of the top rail
    mx = (x0 + x1) // 2
    d.pieslice([mx - 5, y0 - 3, mx + 5, y0 + 5], 180, 360, fill=g, outline=gd)
    for k in (-3, -1, 1, 3):
        d.line([(mx, y0 + 1), (mx + k, y0 - 2)], fill=gd if k > 0 else gl)
    d.point((mx, y0 + 1), fill=hx("fff4c8"))
    # the same pendant shell, smaller, under the bottom rail
    d.pieslice([mx - 3, y1 - 3, mx + 3, y1 + 3], 0, 180, fill=gd, outline=gdd)
    d.point((mx - 1, y1), fill=g)
    return im, (m + b, m + b)


def crooked_painting(img, tilt=-6):
    """The landscape above the bed, knocked askew so a paler patch of wallpaper shows where it used to hang (or,
    with tilt=0, hanging straight over its own shadow)."""
    d = ImageDraw.Draw(img)
    if tilt:
        d.rectangle([294, 28, 354, 64], fill=hotel.CREAM)
    cw, ch = 42, 20
    frame, (ox, oy) = _gilt_frame(cw, ch)
    frame.paste(_landscape(cw, ch), (ox, oy))
    # drawn at 4x and turned, then brought back down so the tilt stays crisp without stair-stepping
    k = 4
    big = frame.resize((frame.width * k, frame.height * k), Image.NEAREST).rotate(tilt, Image.BICUBIC, expand=True)
    tilted = big.resize((big.width // k, big.height // k), Image.BOX)
    a = tilted.getchannel("A").point(lambda v: 255 if v > 110 else 0)
    px_, py_ = 324 - tilted.width // 2, 49 - tilted.height // 2
    shade = Image.new("L", img.size, 0)
    shade.paste(a, (px_ + 2, py_ + 3))
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, hx("6a5a48")))
    img.paste(Image.composite(dark, img, shade.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: v * 0.6)))
    img.paste(tilted.convert("RGB"), (px_, py_), a)


def bedside_lamp(img):
    """The lamp on the nightstand: a celadon porcelain urn in gilt-bronze mounts on a round foot, a knuckled stem, a
    pleated silk shade with gold bands and a fringe, a pine-cone finial, and the lit bulb warming the wall."""
    d = ImageDraw.Draw(img)
    x, y = (int(v) for v in R.P(399, 28, 13))
    gl, g, gd, gdd = hx("f6e0a0"), GOLD, GOLD_D, hx("4a3410")
    # round stepped foot
    d.ellipse([x - 5, y - 2, x + 5, y + 1], fill=gdd)
    d.ellipse([x - 5, y - 3, x + 5, y], fill=gd)
    d.ellipse([x - 4, y - 4, x + 4, y - 1], fill=g)
    d.arc([x - 4, y - 4, x + 4, y - 1], 160, 250, fill=gl)
    # baluster urn: lit porcelain on the left, a gilt ring at its waist and a mount at the shoulder
    por, por_l, por_d = hx("7aa894"), hx("c4e0d0"), hx("3e6a5a")
    for yy in range(y - 12, y - 3):
        t = (yy - (y - 12)) / 8
        hw = 1.5 + 2.6 * math.sin(math.pi * min(1.0, t * 1.15))
        for xx in range(int(round(x - hw)), int(round(x + hw)) + 1):
            u = (xx - x) / max(hw, 1)
            col = por_l if u < -0.45 else por if u < 0.35 else por_d
            d.point((xx, yy), fill=col)
    d.line([(x - 3, y - 7), (x + 3, y - 7)], fill=g)
    d.point((x - 3, y - 7), fill=gl)
    d.line([(x - 2, y - 11), (x + 2, y - 11)], fill=gd)
    d.line([(x - 2, y - 4), (x + 2, y - 4)], fill=gd)
    d.point((x - 1, y - 9), fill=hx("eef8f0"))
    # stem with a knuckle, rising into the shade
    d.rectangle([x, y - 17, x + 1, y - 12], fill=gd)
    d.line([(x, y - 17), (x, y - 12)], fill=gl)
    d.ellipse([x - 1, y - 15, x + 2, y - 13], fill=g)
    # the bulb's glow under the shade, then the shade itself
    ty, by = y - 27, y - 18
    d.ellipse([x - 3, by - 1, x + 3, by + 2], fill=hx("fff2c8"))
    d.point((x - 1, by + 1), fill=hx("ffffff"))
    silk, silk_l, silk_d = hx("dc9e5c"), hx("f8d098"), hx("9a6234")
    for yy in range(ty, by + 1):
        t = (yy - ty) / (by - ty)
        hw = 4 + 4 * t
        for xx in range(int(x - hw), int(x + hw) + 1):
            u = (xx - x) / hw
            col = silk_l if int((u + 1) * 5) % 2 else silk
            if u > 0.55:
                col = mix(col, silk_d, 0.55)
            elif u < -0.85:
                col = mix(col, silk_d, 0.3)
            d.point((xx, yy), fill=col)
    d.line([(x - 4, ty), (x + 4, ty)], fill=gd)
    d.line([(x - 4, ty + 1), (x + 4, ty + 1)], fill=g)
    d.line([(x - 8, by - 1), (x + 8, by - 1)], fill=g)
    d.line([(x - 8, by), (x + 8, by)], fill=gd)
    d.line([(x - 8, by - 1), (x - 4, by - 1)], fill=gl)
    for xx in range(x - 8, x + 9, 2):
        d.point((xx, by + 1), fill=hx("b89040"))
    # pine-cone finial on the harp
    d.point((x, ty - 1), fill=gd)
    d.ellipse([x - 1, ty - 4, x + 1, ty - 1], fill=g)
    d.point((x, ty - 4), fill=gl)
    d.point((x + 1, ty - 2), fill=gdd)
    light(img, "ellipse", [x - 26, ty - 16, x + 26, by + 18], hx("fff0c8"), 0.18, 8)
    light(img, "ellipse", [x - 10, ty - 3, x + 10, by + 4], hx("ffe0a0"), 0.12, 3)
    return x, (ty + by) // 2


from .common import PHONE, PHONE_M, PHONE_L, NICKEL, NICKEL_D, CORD, CORD_L, CARD, braided_cord as _cord, candlestick_phone
PHONE_AT = (461, 30, 13)  # the candlestick's foot at the right end of the vanity, by the wall
RINGER = (469, 477, 44, 57)  # the bell box on the wall over the vanity's right end: x0, x1, bottom, top


def ringer(img, tidy=True):
    """The subscriber set the candlestick needs: a walnut bell box screwed to the wall, two nickel gongs on its face,
    the line running down the wall behind the vanity. In the searched room the desk cord is still plugged in and runs
    over the vanity's front corner to where the telephone was dragged down."""
    d = ImageDraw.Draw(img)
    X0, X1, B, T = RINGER
    R.box(img, X0, X1, B, T, 0, 3, hx("5a3820"), top=hx("7a5232"), side=hx("2e1c10"))
    R.quad(img, [(X0 + 1, B + 1, 3.05), (X1 - 1, B + 1, 3.05), (X1 - 1, B + 6, 3.05), (X0 + 1, B + 6, 3.05)],
           None, hx("2e1c10"))
    for gx in (X0 + 2.5, X1 - 2.5):
        cx, cy = R.P(gx, T - 3.5, 3.1)
        d.ellipse([cx - 2, cy - 2, cx + 1, cy + 1], fill=NICKEL_D)
        d.point((cx - 1, cy - 1), fill=NICKEL)
        d.point((cx, cy), fill=hx("ffffff"))
    cx, cy = R.P((X0 + X1) / 2, T - 3.5, 3.1)
    d.line([(cx, cy - 1), (cx, cy + 2)], fill=NICKEL_D)
    d.point((cx, cy - 1), fill=NICKEL)
    a = R.P(X0 + 4, B, 1)
    b = R.P(X0 + 4, 30, 1)
    _cord(d, [a, b], 3)
    x, y = (int(v) for v in R.P(*PHONE_AT))
    if tidy:
        # the desk cord lies along the top from the wall to the foot
        _cord(d, [b, R.P(X0 + 1, 30, 6), (x + 6, y - 1)])
    else:
        _cord(d, [b, R.P(X0 - 2, 30, 10), R.P(468, 30, 21)])


def telephone(img):
    """The hotel extension on the vanity: a black Western Electric candlestick with no dial (lifting the receiver
    rings the switchboard downstairs). A flared, stepped foot with the room's number card, a column ringed in nickel,
    the mouthpiece trumpet turned to the room with its nickel rim and dark throat, and the receiver hanging by its bell
    on the nickel switchhook, its braided cord looping down to the foot."""
    x, y = (int(v) for v in R.P(*PHONE_AT))
    candlestick_phone(img, x, y)


def telephone_down(img):
    """The searched room: the telephone dragged off the vanity by its cord and dropped by the stool, lying on its
    side, the mouthpiece rim knocked askew, the receiver jerked off the hook and lying face down at the end of its
    cord; the desk cord still hangs over the vanity's corner from the bell box on the wall."""
    d = ImageDraw.Draw(img)
    x, y = (int(v) for v in R.P(463, 0, 40))
    top = R.P(468, 30, 21)
    shadow(img, "ellipse", [x - 11, y - 2, x + 8, y + 4], 0.45, 2)
    # the desk cord hanging off the corner, down to the foot
    _cord(d, [top, (top[0] + 1, top[1] + 8), (top[0], y - 14), (x + 6, y - 5)])
    # foot, on its edge
    d.ellipse([x + 3, y - 7, x + 7, y + 1], fill=PHONE)
    d.line([(x + 4, y - 6), (x + 4, y - 1)], fill=PHONE_L)
    d.point((x + 5, y - 3), fill=CARD)
    # column along the floor with its nickel collars
    d.rectangle([x - 7, y - 3, x + 3, y - 2], fill=PHONE)
    d.line([(x - 7, y - 3), (x + 2, y - 3)], fill=PHONE_L)
    d.point((x + 2, y - 3), fill=NICKEL)
    d.point((x - 6, y - 3), fill=NICKEL)
    # the switchhook sticking up, empty
    d.line([(x - 3, y - 4), (x - 3, y - 6)], fill=NICKEL)
    d.point((x - 2, y - 6), fill=NICKEL_D)
    # the trumpet at the far end, rim turned up
    d.polygon([(x - 8, y - 4), (x - 8, y - 1), (x - 10, y), (x - 10, y - 5)], fill=PHONE)
    d.ellipse([x - 12, y - 6, x - 9, y + 1], fill=NICKEL_D)
    d.line([(x - 11, y - 5), (x - 11, y - 1)], fill=hx("060608"))
    d.point((x - 12, y - 4), fill=NICKEL)
    # the receiver flung forward, face down, its braided cord trailing back to the foot
    rx, ry = x - 6, y + 7
    _cord(d, [(x + 4, y), (x + 2, y + 4), (x - 1, y + 4), (rx + 4, ry - 1)])
    d.rectangle([rx - 2, ry - 1, rx + 4, ry], fill=PHONE)
    d.line([(rx - 2, ry - 1), (rx + 3, ry - 1)], fill=PHONE_L)
    d.ellipse([rx - 6, ry - 2, rx - 2, ry + 1], fill=PHONE)
    d.point((rx - 5, ry - 2), fill=PHONE_L)
    d.point((rx - 4, ry), fill=NICKEL_D)


DOOR_WOOD, DOOR_PANEL, DOOR_LINE, DOOR_HI = hx("75492b"), hx("7e5232"), hx("3e2615"), hx("9a6c48")


def _panel(img, x0, x1, y0, y1, z, arch=0, seed=0):
    """A raised, bevelled door panel on a front (constant z) face: shaded bevel, a lighter field with a faint
    grain and, if arch, a rounded top."""
    d = ImageDraw.Draw(img)

    def outline(inset):
        pts = [(x0 + inset, y0 + inset), (x1 - inset, y0 + inset), (x1 - inset, y1 - inset - arch)]
        if arch:
            for k in range(1, 8):
                t = k / 8
                pts.append((x1 - inset - (x1 - x0 - 2 * inset) * t, y1 - inset - arch + arch * math.sin(t * math.pi)))
        pts.append((x0 + inset, y1 - inset - arch))
        return [R.P(x, y, z) for x, y in pts]
    d.polygon(outline(0), fill=DOOR_LINE)
    d.polygon(outline(1), fill=mul(DOOR_WOOD, 0.82))
    d.polygon(outline(2.2), fill=DOOR_PANEL)
    o = outline(1)
    d.line(o[:2], fill=DOOR_HI)
    d.line([o[1], o[2]], fill=DOOR_HI)
    rnd = random.Random(seed)
    for _ in range(3):
        gx = rnd.uniform(x0 + 4, x1 - 4)
        a, b = R.P(gx, y0 + 4, z), R.P(gx + rnd.uniform(-1, 1), y1 - 4 - arch, z)
        d.line([a, (a[0] + rnd.choice((-1, 1)), (a[1] + b[1]) / 2), b], fill=mul(DOOR_PANEL, 0.88))


def _closet_carcass(img):
    """The carving shared by both states: a broken-pediment crest with a gilt cartouche and urn finials, dentils
    under the cornice, fluted corner pilasters, a panelled side and bun feet."""
    X0, X1, Z0, Z1 = CL_X0, CL_X1, CL_Z0, CL_Z1
    xm = (X0 + X1) / 2
    d = ImageDraw.Draw(img)
    z = Z1 + 2
    # cornice mouldings and a dentil course
    R.line(img, (X0 - 2, 111, z), (X1 + 2, 111, z), hx("a07450"))
    R.line(img, (X0 - 2, 106, z), (X1 + 2, 106, z), WOOD_D)
    for x in range(X0, X1 + 1, 3):
        R.line(img, (x, 104.5, Z1 + 1), (x, 106, Z1 + 1), WOOD_D)
    # crest: two scrolled halves of a pediment rising to a cartouche
    crest = [(X0 - 1, 112), (X0 - 1, 115), (xm - 12, 117), (xm - 6, 121), (xm - 4, 119), (xm + 4, 119),
             (xm + 6, 121), (xm + 12, 117), (X1 + 1, 115), (X1 + 1, 112)]
    d.polygon([R.P(x, y, z) for x, y in crest], fill=WOOD, outline=DOOR_LINE)
    R.line(img, (X0, 114, z), (xm - 12, 116, z), hx("a07450"))
    R.line(img, (X1, 114, z), (xm + 12, 116, z), mul(WOOD, 0.8))
    for s in (-1, 1):
        sx, sy = R.P(xm + s * 6, 120, z)
        d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], outline=GOLD_D)
    cx, cy = R.P(xm, 117, z)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 3], fill=GOLD_D)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 2], fill=GOLD)
    d.ellipse([cx - 1.5, cy - 2, cx + 1.5, cy + 1], fill=hx("8a5e3c"))
    d.point((cx - 2, cy - 3), fill=hx("f4dc98"))
    for x in (X0 + 1, X1 - 1):
        ux, uy = R.P(x, 112, z)
        d.rectangle([ux - 2, uy - 2, ux + 2, uy], fill=GOLD_D)
        d.ellipse([ux - 2, uy - 6, ux + 2, uy - 2], fill=GOLD)
        d.point((ux, uy - 7), fill=GOLD)
        d.point((ux - 1, uy - 5), fill=hx("f4dc98"))
    # fluted pilasters at the front corners, with gilt capitals and bases
    for (a, b) in ((X0, X0 + 3), (X1 - 3, X1)):
        R.quad(img, [(a, 3, Z1), (b, 3, Z1), (b, 104, Z1), (a, 104, Z1)], mul(WOOD, 0.9))
        R.line(img, (a + 1, 10, Z1), (a + 1, 96, Z1), WOOD_D)
        R.line(img, (a + 2, 10, Z1), (a + 2, 96, Z1), hx("8a5e3c"))
        R.quad(img, [(a - 0.5, 97, Z1), (b + 0.5, 97, Z1), (b + 0.5, 101, Z1), (a - 0.5, 101, Z1)], GOLD_D)
        R.line(img, (a, 100, Z1), (b, 100, Z1), GOLD)
        R.quad(img, [(a - 0.5, 3, Z1), (b + 0.5, 3, Z1), (b + 0.5, 6, Z1), (a - 0.5, 6, Z1)], GOLD_D)
    # a sunk panel down the side and bun feet
    R.quad(img, [(X1, 12, Z0 + 4), (X1, 12, Z1 - 4), (X1, 94, Z1 - 4), (X1, 94, Z0 + 4)], None, hx("2e1c10"))
    R.line(img, (X1, 13, Z0 + 5), (X1, 93, Z0 + 5), hx("5a3a22"))
    for x in (X0 + 2, X1 - 2):
        fx, fy = R.P(x, 0, Z1 - 1)
        d.ellipse([fx - 3, fy - 3, fx + 3, fy + 1], fill=WOOD_D)
        d.line([(fx - 2, fy - 2), (fx + 1, fy - 2)], fill=hx("6b4428"))


def wall_safe(img, opened=False, box=False, ajar=False, scratched=True):
    """The wall safe sunk into the back of the closet: a bolted steel door with hinges, a maker's plate, a ticked
    combination dial scratched raw by whoever tried it, and a spoked handle. Open, it shows a shelved steel box and
    the inside of the door with its locking bolts."""
    X0, X1, Y0, Y1, Z = SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1, SAFE_Z
    SEAM, SCRATCH, CAVITY = hx("18191c"), hx("9a9ea6"), hx("121214")
    d = ImageDraw.Draw(img)
    # the housing set into the wall: dark steel collar, lit along the top and left where the closet light catches it
    R.quad(img, [(X0 - 2, Y0 - 2, Z), (X1 + 2, Y0 - 2, Z), (X1 + 2, Y1 + 2, Z), (X0 - 2, Y1 + 2, Z)], STEEL_D)
    R.line(img, (X0 - 2, Y1 + 2, Z), (X1 + 2, Y1 + 2, Z), mul(STEEL, 0.85))
    R.line(img, (X0 - 2, Y0 - 2, Z), (X0 - 2, Y1 + 2, Z), mul(STEEL, 0.85))
    R.line(img, (X0 - 2, Y0 - 2, Z), (X1 + 2, Y0 - 2, Z), SEAM)
    R.line(img, (X1 + 2, Y0 - 2, Z), (X1 + 2, Y1 + 2, Z), SEAM)
    bolt_ys = (Y0 + 6, (Y0 + Y1) / 2, Y1 - 6)
    if ajar:
        # the door left standing half open on its left hinge, waiting for the box
        R.quad(img, [(X0, Y0, Z - 0.5), (X1, Y0, Z - 0.5), (X1, Y1, Z - 0.5), (X0, Y1, Z - 0.5)], CAVITY)
        if box:
            R.box(img, X0 + 8, X1 - 4, Y0, Y0 + 8, Z - 0.4, Z + 0.2, hx("b08a3a"), top=hx("d8b050"))
            px, py = R.P((X0 + X1) / 2 + 2, Y0 + 4, Z + 0.3)
            d.point((px, py), fill=hx("6a5020"))
        ex, ez = X0 + 6, Z + 16
        R.quad(img, [(X0, Y0, Z), (ex, Y0, ez), (ex, Y1, ez), (X0, Y1, Z)], STEEL, STEEL_L)
        # the dial on the door's face, turned half away
        cx, cy = R.P(X0 + 3, (Y0 + Y1) / 2, Z + 8.5)
        d.ellipse([cx - 2, cy - 4, cx + 2, cy + 4], fill=STEEL_D, outline=GOLD)
        return
    if not opened:
        x0, y0 = (round(v) for v in R.P(X0, Y1, Z + 0.5))
        x1, y1 = (round(v) for v in R.P(X1, Y0, Z + 0.5))
        d.rectangle([x0, y0, x1, y1], fill=STEEL)
        # the door seam: lit on the top and left, shadowed underneath and on the right
        d.line([(x0, y0), (x1, y0)], fill=STEEL_L)
        d.line([(x0, y0), (x0, y1)], fill=STEEL_L)
        d.line([(x0, y1), (x1, y1)], fill=SEAM)
        d.line([(x1, y0), (x1, y1)], fill=SEAM)
        # a recessed panel in the door, its bevel the other way round
        d.line([(x0 + 3, y0 + 3), (x1 - 3, y0 + 3)], fill=STEEL_D)
        d.line([(x0 + 3, y0 + 3), (x0 + 3, y1 - 3)], fill=STEEL_D)
        d.line([(x0 + 3, y1 - 3), (x1 - 3, y1 - 3)], fill=mul(STEEL_L, 0.9))
        d.line([(x1 - 3, y0 + 3), (x1 - 3, y1 - 3)], fill=mul(STEEL_L, 0.9))
        # rivets at the corners
        for rx, ry in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
            d.point((rx, ry), fill=STEEL_L)
            d.point((rx + 1, ry + 1), fill=SEAM)
        # two hinge knuckles on the left edge
        for hy in (y0 + 5, y1 - 7):
            d.rectangle([x0 - 2, hy, x0 - 1, hy + 3], fill=STEEL_L)
            d.point((x0 - 1, hy + 3), fill=SEAM)
            d.point((x0 - 2, hy), fill=mul(STEEL_L, 1.2))
        # the maker's brass plate in the top right corner of the panel
        cx, cy = x0 + 11, (y0 + y1) // 2 + 1
        d.rectangle([x1 - 11, y0 + 5, x1 - 5, y0 + 6], fill=GOLD_D)
        d.line([(x1 - 11, y0 + 5), (x1 - 5, y0 + 5)], fill=GOLD)
        d.line([(x1 - 9, y0 + 6), (x1 - 7, y0 + 6)], fill=hx("4a3418"))
        # scratches around the dial, gouged by somebody without the combination (not yet the night she locked it)
        rnd = random.Random(507)
        for _ in range(9 if scratched else 0):
            a = rnd.uniform(0, 2 * math.pi)
            r0 = rnd.uniform(6, 7.5)
            r1 = r0 + rnd.uniform(1.5, 3)
            da = rnd.uniform(-0.25, 0.25)
            d.line([(cx + r0 * math.cos(a), cy + r0 * math.sin(a)),
                    (cx + r1 * math.cos(a + da), cy + r1 * math.sin(a + da))], fill=SCRATCH)
        # the combination dial: gold rim lit at the top left, ticks round the face, an index notch, a knob
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=hx("1c1c20"), outline=GOLD_D)
        d.arc([cx - 5, cy - 5, cx + 5, cy + 5], 160, 290, fill=GOLD)
        for k in range(12):
            a = k * math.pi / 6
            d.point((round(cx + 3.6 * math.cos(a)), round(cy + 3.6 * math.sin(a))),
                    fill=STEEL_L if k % 3 else hx("e8e4d8"))
        d.polygon([(cx - 1, cy - 7), (cx + 1, cy - 7), (cx, cy - 6)], fill=GOLD)
        d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=STEEL_L)
        d.point((cx - 1, cy - 1), fill=hx("e8e4d8"))
        d.point((cx + 1, cy + 1), fill=STEEL_D)
        # the spoked handle: a hub with three arms, each ending in a little knob
        hx_, hy = x1 - 8, cy + 2
        for a in (-90, 30, 150):
            ex, ey = hx_ + 4 * math.cos(math.radians(a)), hy + 4 * math.sin(math.radians(a))
            d.line([(hx_ + 1, hy + 1), (ex + 1, ey + 1)], fill=SEAM)
            d.line([(hx_, hy), (ex, ey)], fill=GOLD_D)
            d.point((round(ex), round(ey)), fill=GOLD)
        d.ellipse([hx_ - 2, hy - 2, hx_ + 2, hy + 2], fill=GOLD_D, outline=GOLD)
        d.point((hx_, hy), fill=hx("4a3418"))
        return
    # the open box: dark back wall, its left side and floor catching some light, a steel shelf across the middle
    B = Z - 10
    R.quad(img, [(X0, Y0, Z - 0.5), (X1, Y0, Z - 0.5), (X1, Y1, Z - 0.5), (X0, Y1, Z - 0.5)], CAVITY)
    R.quad(img, [(X0, Y0, B), (X1, Y0, B), (X1, Y1, B), (X0, Y1, B)], hx("1a1b1f"))
    R.quad(img, [(X0, Y0, Z - 0.5), (X0, Y0, B), (X0, Y1, B), (X0, Y1, Z - 0.5)], hx("2a2b31"))
    R.quad(img, [(X0, Y0, Z - 0.5), (X1, Y0, Z - 0.5), (X1, Y0, B), (X0, Y0, B)], hx("34363d"))
    ym = Y0 + 15
    R.quad(img, [(X0, ym, Z - 0.5), (X1, ym, Z - 0.5), (X1, ym, B), (X0, ym, B)], hx("3c3e46"))
    R.line(img, (X0, ym, Z - 0.5), (X1, ym, Z - 0.5), STEEL_L)
    R.line(img, (X0, ym - 1, Z - 0.5), (X1, ym - 1, Z - 0.5), SEAM)
    # an envelope left flat on the shelf
    R.quad(img, [(X1 - 12, ym, B + 2), (X1 - 3, ym, B + 2), (X1 - 3, ym, B + 8), (X1 - 12, ym, B + 8)], PAPER_D)
    # bolt sockets in the jamb on the far side of the opening
    for by in bolt_ys:
        R.line(img, (X1 + 1, by, Z), (X1 + 1, by + 1, Z), CAVITY)
    if box:
        R.box(img, X0 + 6, X1 - 6, Y0, Y0 + 8, Z - 0.4, Z + 0.2, hx("b08a3a"), top=hx("d8b050"))
        px, py = R.P((X0 + X1) / 2, Y0 + 4, Z + 0.3)
        d.point((px, py), fill=hx("6a5020"))
    # the heavy door swung open on its left hinge, seen nearly edge on: its inner face lit along the top, the locking
    # bolts standing out of the free edge
    DZ = Z + 22
    R.quad(img, [(X0, Y0, Z), (X0, Y0, DZ), (X0, Y1, DZ), (X0, Y1, Z)], STEEL, STEEL_L)
    R.line(img, (X0, Y0, DZ), (X0, Y1, DZ), SEAM)
    for by in bolt_ys:
        a, b = R.P(X0, by, DZ), R.P(X0, by, DZ + 3)
        d.line([(a[0], a[1] + 1), (b[0], b[1] + 1)], fill=SEAM)
        d.line([a, b], fill=hx("b4b8c0"))
    for hy in (Y0 + 4, Y1 - 6):
        R.line(img, (X0, hy, Z + 0.5), (X0, hy + 3, Z + 0.5), hx("b4b8c0"), 2)


def closet(img, opened=False, safe_open=False, box=False, tidy=False, ajar=False):
    X0, X1, Z0, Z1 = CL_X0, CL_X1, CL_Z0, CL_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 2, a[1] - 3, b[0] + 10, a[1] + 3], 0.4, 3)
    R.box(img, X0, X1, 3, 104, Z0, Z1, mul(WOOD, 0.95), top=WOOD, side=hx("4c2f1a"))
    R.box(img, X0 - 2, X1 + 2, 104, 112, Z0, Z1 + 2, WOOD, top=hx("8a5e3c"), side=hx("4c2f1a"))
    R.box(img, X0 + 1, X1 - 1, 0, 3, Z0, Z1 - 1, WOOD_D)
    _closet_carcass(img)
    xm = (X0 + X1) / 2
    if not opened:
        d = ImageDraw.Draw(img)
        for i, (c, e) in enumerate(((X0 + 3, xm - 1), (xm + 1, X1 - 3))):
            R.quad(img, [(c, 6, Z1), (e, 6, Z1), (e, 100, Z1), (c, 100, Z1)], DOOR_WOOD, DOOR_LINE)
            R.line(img, (c + 1, 99, Z1), (e - 1, 99, Z1), DOOR_HI)
            _panel(img, c + 4, e - 4, 12, 44, Z1, seed=11 + i)
            _panel(img, c + 4, e - 4, 54, 94, Z1, arch=6, seed=13 + i)
            # a little inlaid gilt lozenge on the rail between the panels, brass butt hinges on the outer stile
            lx, ly = R.P((c + e) / 2, 49, Z1)
            d.polygon([(lx, ly - 2), (lx + 2, ly), (lx, ly + 2), (lx - 2, ly)], fill=GOLD_D)
            d.point((lx, ly), fill=GOLD)
            hxx = c + 0.5 if i == 0 else e - 0.5
            for hy in (20, 86):
                h0, h1 = R.P(hxx, hy, Z1), R.P(hxx, hy + 6, Z1)
                d.line([h0, h1], fill=GOLD_D, width=2)
                d.point((h0[0], h1[1] + 1), fill=GOLD)
        R.line(img, (xm, 6, Z1), (xm, 100, Z1), WOOD_D)
        # keyhole escutcheon on the left door, a drop pull on the right
        kx, ky = R.P(xm - 3, 54, Z1)
        d.ellipse([kx - 2, ky - 3, kx + 2, ky + 4], fill=GOLD_D)
        d.ellipse([kx - 1.5, ky - 2.5, kx + 1.5, ky + 3.5], fill=GOLD)
        d.point((kx, ky), fill=hx("140c08"))
        d.point((kx, ky + 1), fill=hx("140c08"))
        px_, py_ = R.P(xm + 3, 56, Z1)
        d.ellipse([px_ - 1, py_ - 3, px_ + 1, py_ - 1], fill=GOLD_D)
        d.line([(px_, py_ - 1), (px_, py_ + 3)], fill=GOLD)
        d.ellipse([px_ - 1, py_ + 3, px_ + 1, py_ + 5], fill=GOLD)
        if tidy:
            return
        # a sleeve of her silk caught in the doors when they were slammed
        sx, sy = R.P(xm, 38, Z1)
        body, fold, lit, _, line = LILAC
        d.polygon([(sx - 1, sy - 6), (sx + 1, sy - 6), (sx + 4, sy + 2), (sx + 2, sy + 5), (sx - 1, sy + 3)],
                  fill=line)
        d.polygon([(sx, sy - 5), (sx + 1, sy - 5), (sx + 3, sy + 2), (sx + 2, sy + 4), (sx, sy + 2)], fill=body)
        d.line([(sx + 1, sy - 3), (sx + 2, sy + 3)], fill=fold)
        d.point((sx, sy - 4), fill=lit)
        return
    # cavity, hanging rail and what's left on the hangers
    R.quad(img, [(X0 + 3, 4, Z1), (X1 - 3, 4, Z1), (X1 - 3, 100, Z1), (X0 + 3, 100, Z1)], hx("1e140c"))
    R.quad(img, [(X0 + 3, 4, Z0 + 2), (X1 - 3, 4, Z0 + 2), (X1 - 3, 100, Z0 + 2), (X0 + 3, 100, Z0 + 2)], hx("2a1a10"))
    R.line(img, (X0 + 4, 88, Z0 + 12), (X1 - 4, 88, Z0 + 12), GOLD_D, 2)
    d = ImageDraw.Draw(img)
    # the night she left her dresses still hang in a row; after the old man's men, three are left on the rail
    hanging = (((X0 + 9, LILAC, 40), (X0 + 18, NAVY, 42), (X0 + 27, IVORY, 38), (X1 - 18, LILAC, 36),
                (X1 - 10, NAVY, 40)) if tidy else ((X0 + 10, LILAC, 40), (X1 - 12, IVORY, 36), (X0 + 24, NAVY, 42)))
    for (x, col, h) in hanging:
        rx, ry = R.P(x, 88, Z0 + 12)
        d.line([(rx, ry - 2), (rx + 1, ry - 2), (rx, ry + 2)], fill=STEEL_L)
        d.line([(rx - 6, ry + 5), (rx, ry + 2), (rx + 6, ry + 5)], fill=STEEL_L)
        spr = dress(12, h, col, bow=False)
        _stamp(img, spr, rx - spr.width / 2 + 0.5, ry + 3)
    if not tidy:
        # clothes yanked off their hangers, heaped at the bottom
        hx_, hy = R.P(X0 + 4, 4, Z1 - 4)
        heap = _crumple(dress(9, 26, (hx("8a6a8a"), hx("5a3e5a"), hx("b096b0"), hx("3e2a3e"), hx("1a101a")), bow=False)
                        .rotate(90, expand=True), 1.2, 9)
        _stamp(img, heap, hx_ - 1, hy - heap.height + 2)
        slip = _crumple(dress(7, 16, IVORY, bow=False).rotate(-90, expand=True), 1, 6, 1.0)
        _stamp(img, slip, hx_ + 16, hy - slip.height + 3)
    wall_safe(img, safe_open, box, ajar, scratched=not tidy)
    # both doors flung wide, their inner faces panelled like the fronts
    for x in (X0, X1):
        R.quad(img, [(x, 6, Z1), (x, 6, Z1 + 24), (x, 100, Z1 + 24), (x, 100, Z1)], DOOR_WOOD, DOOR_LINE)
        for (y0, y1) in ((12, 44), (54, 94)):
            R.quad(img, [(x, y0, Z1 + 4), (x, y0, Z1 + 20), (x, y1, Z1 + 20), (x, y1, Z1 + 4)], DOOR_PANEL, DOOR_LINE)
            R.line(img, (x, y1 - 1, Z1 + 5), (x, y1 - 1, Z1 + 19), DOOR_HI)
            R.line(img, (x, y0 + 1, Z1 + 19), (x, y1 - 1, Z1 + 19), mul(DOOR_PANEL, 0.8))
        for hy in (20, 86):
            R.line(img, (x, hy, Z1 + 0.5), (x, hy + 6, Z1 + 0.5), GOLD_D, 2)
        R.line(img, (x, 52, Z1 + 21), (x, 57, Z1 + 21), GOLD, 2)


WOOD_L = hx("9a6c46")


def _turned_leg(img, x, z, top, w=3.0):
    """A tapering leg, lit down its left edge, with a turned collar under the apron and a brass cap at the foot."""
    d = ImageDraw.Draw(img)
    s = R.s(z)
    xt, yt = R.P(x, top, z)
    yb = R.P(x, 0, z)[1]
    y0, y1 = int(round(yt)), int(round(yb))
    for y in range(y0, y1 + 1):
        hw = w * s / 2 * (1 - 0.4 * (y - y0) / max(1, y1 - y0))
        xa, xb = int(round(xt - hw)), int(round(xt + hw)) - 1
        d.line([(xa, y), (max(xa, xb), y)], fill=WOOD)
        d.point((xa, y), fill=WOOD_L)
        if xb > xa:
            d.point((xb, y), fill=WOOD_D)
    cy = y0 + max(1, int(round(1.5 * s)))
    hw = int(round(w * s / 2))
    d.line([(int(round(xt)) - hw, cy), (int(round(xt)) + hw - 1, cy)], fill=WOOD_L)
    d.line([(int(round(xt)) - hw, cy + 1), (int(round(xt)) + hw - 1, cy + 1)], fill=WOOD_D)
    d.point((int(round(xt - w * s / 3)), y1), fill=GOLD)
    d.point((int(round(xt - w * s / 3)) + 1, y1), fill=GOLD_D)


def _drawer_front(img, c, z, face=None):
    """A recessed drawer panel with a brass escutcheon at its centre and a knob either side."""
    R.quad(img, [(c, 21, z), (c + 24, 21, z), (c + 24, 25, z), (c, 25, z)], face or mul(WOOD, 0.8), WOOD_D)
    R.line(img, (c + 1, 21.7, z), (c + 23, 21.7, z), mul(WOOD_L, 0.9))
    d = ImageDraw.Draw(img)
    ex, ey = R.P(c + 12, 23, z)
    d.rectangle([ex - 1, ey - 1, ex + 1, ey + 1], fill=GOLD_D)
    d.point((ex, ey - 1), fill=GOLD)
    d.point((ex, ey), fill=hx("120a06"))
    for k in (c + 5, c + 19):
        kx, ky = R.P(k, 23, z)
        d.point((kx, ky), fill=GOLD)
        d.point((kx + 1, ky), fill=GOLD_D)


def desk(img, drawer_open=False, paper=False, tidy=False):
    X0, X1, Z0, Z1 = DESK_X0, DESK_X1, DESK_Z0, DESK_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0], a[1] - 4, b[0] + 6, a[1] + 3], 0.35, 3)
    for x in (X0 + 2, X1 - 2):
        _turned_leg(img, x, Z0 + 2, 20, 2.4)
    R.box(img, X0, X1, 20, 26, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    # the apron: a bead along its lower edge and a carved brass rosette between the drawers, over a shallow arch
    R.line(img, (X0, 20.4, Z1), (X1, 20.4, Z1), WOOD_L)
    d = ImageDraw.Draw(img)
    m = (X0 + X1) / 2
    arc = [R.P(m - 9 + 18 * t / 8, 20 - 1.6 * math.sin(math.pi * t / 8), Z1) for t in range(9)]
    d.polygon(arc, fill=mul(WOOD, 0.9))
    d.line(arc, fill=WOOD_D)
    rx, ry = R.P(m, 23, Z1)
    d.point([(rx - 1, ry), (rx + 1, ry), (rx, ry - 1), (rx, ry + 1)], fill=GOLD_D)
    d.point((rx, ry), fill=GOLD)
    # the top: a moulded edge catching the light over a shadowed underside, an inlaid border and a tooled leather inset
    R.box(img, X0 - 1, X1 + 1, 26, 28, Z0, Z1 + 1, hx("7d5232"), top=hx("8e6040"), side=WOOD_D)
    R.line(img, (X0 - 1, 27.7, Z1 + 1), (X1 + 1, 27.7, Z1 + 1), hx("a87850"))
    R.line(img, (X0 - 1, 26.2, Z1 + 1), (X1 + 1, 26.2, Z1 + 1), WOOD_D)
    R.quad(img, [(X0 + 2, 28.02, Z0 + 2), (X1 - 2, 28.02, Z0 + 2), (X1 - 2, 28.02, Z1 - 1), (X0 + 2, 28.02, Z1 - 1)],
           None, hx("a87850"))
    R.quad(img, [(X0 + 6, 28.04, Z0 + 5), (X1 - 6, 28.04, Z0 + 5), (X1 - 6, 28.04, Z1 - 4), (X0 + 6, 28.04, Z1 - 4)],
           mul(GREEN, 0.62), GOLD_D)
    R.line(img, (X0 + 8, 28.06, Z1 - 5), (X1 - 8, 28.06, Z1 - 5), mul(GREEN, 0.85))
    # a low gallery of spindles along the back edge
    for x in range(X0 + 2, X1 - 1, 4):
        R.line(img, (x, 28, Z0 + 0.6), (x, 30.5, Z0 + 0.6), mul(WOOD_D, 1.2))
    R.line(img, (X0 + 1, 30.8, Z0 + 0.6), (X1 - 1, 30.8, Z0 + 0.6), WOOD_L)
    for x in (X0 + 1, X1 - 1):
        px, py = R.P(x, 31.5, Z0 + 0.6)
        d.point((px, py), fill=GOLD)
    for x in (X0 + 2, X1 - 2):
        _turned_leg(img, x, Z1 - 2, 20)
    # left drawer: locked; right drawer: yanked out and dumped
    c = X0 + 6
    _drawer_front(img, c, Z1)
    c2 = X1 - 30
    if tidy:
        # both drawers shut; on top a squared stack of stationery, a sealed envelope, the pen laid by an upright inkwell
        _drawer_front(img, c2, Z1)
        d = ImageDraw.Draw(img)
        sheet(img, 166, 120, 14, 6, lines=0, seed=3)
        sheet(img, 167, 119, 14, 6, lines=3, seed=4)
        sheet(img, 184, 121, 10, 5, envelope=True, seal=hx("a02828"))
        d.line([(197, 126), (205, 124)], fill=hx("101014"))
        d.point((205, 124), fill=GOLD)
        R.box(img, 202, 210, 28, 32, 10, 14, hx("2e4646"), top=hx("5a7a7a"))
        ix, iy = R.P(206, 32, 12)
        d.rectangle([ix - 1, iy - 1, ix + 1, iy], fill=GOLD_D)
        d.point((ix - 2, iy + 1), fill=hx("a8c8c8"))
        return
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
        _drawer_front(img, c, Z1 + 12, hx("6a4428"))
        if paper:
            R.quad(img, [(c + 6, 25.1, Z1 + 3), (c + 18, 25.1, Z1 + 2), (c + 19, 25.1, Z1 + 9), (c + 7, 25.1, Z1 + 10)],
                   hx("f4ecdc"))
            R.line(img, (c + 8, 25.2, Z1 + 5), (c + 16, 25.2, Z1 + 5), hx("3a3a6a"))
            R.line(img, (c + 8, 25.2, Z1 + 7), (c + 15, 25.2, Z1 + 7), hx("3a3a6a"))


def _upholstery(img, corner, du, dv, nu=3, nv=3):
    """Button-tufted burgundy upholstery on a flat panel spanned from corner by the world vectors du and dv: a diamond
    of buttons, each with the stuffing swelling lit above it, inside a border of brass nailheads."""
    d = ImageDraw.Draw(img)

    def at(u, v):
        return R.P(*(corner[i] + du[i] * u + dv[i] * v for i in range(3)))

    d.polygon([at(0, 0), at(1, 0), at(1, 1), at(0, 1)], fill=BURGUNDY, outline=mul(BURGUNDY, 0.55))
    for j in range(nv):
        for i in range(nu if j % 2 == 0 else nu - 1):
            x, y = at((i + (1 if j % 2 == 0 else 1.5)) / (nu + 1), (j + 1) / (nv + 1))
            x, y = int(round(x)), int(round(y))
            d.point((x, y), fill=mul(BURGUNDY, 0.45))
            d.point((x - 1, y - 1), fill=BURGUNDY_L)
            d.point((x + 1, y + 1), fill=mul(BURGUNDY, 0.8))
    lu, lv = math.dist((0, 0, 0), du), math.dist((0, 0, 0), dv)
    eu, ev = 0.6 / lu, 0.6 / lv
    for n in range(int(lu / 2.2) + 1):
        u = eu + (1 - 2 * eu) * n / max(1, int(lu / 2.2))
        for v in (ev, 1 - ev):
            d.point(at(u, v), fill=GOLD_D)
    for n in range(1, int(lv / 2.2)):
        v = ev + (1 - 2 * ev) * n / int(lv / 2.2)
        for u in (eu, 1 - eu):
            d.point(at(u, v), fill=GOLD_D)


def _finial(d, p):
    x, y = int(round(p[0])), int(round(p[1]))
    d.rectangle([x - 1, y - 1, x, y], fill=GOLD_D)
    d.point((x - 1, y - 1), fill=GOLD)


def chair_upright(img):
    """The desk chair pulled up square, its back to us: turned front legs joined by stretchers, a piped cushion on a
    nailed seat rail, and rear legs rising into stiles that frame a tufted back under an arched, carved crest rail."""
    d = ImageDraw.Draw(img)
    a, b = R.P(182, 0, 46), R.P(204, 0, 46)
    shadow(img, "rect", [a[0] - 1, a[1] - 3, b[0] + 3, a[1] + 2], 0.35, 2)
    for x in (183.5, 202.5):
        _turned_leg(img, x, 32, 10.5, 2.4)
        R.line(img, (x, 4, 32), (x, 4, 44), WOOD_D)
    R.line(img, (183.5, 5, 32), (202.5, 5, 32), WOOD_D)
    R.line(img, (183.5, 4, 44), (202.5, 4, 44), mul(WOOD, 0.85), 2)
    R.box(img, 181, 205, 10.5, 13.5, 30, 44, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.box(img, 181.5, 204.5, 13.5, 16, 30.5, 44, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))
    R.line(img, (204.5, 16, 30.5), (204.5, 16, 44), mul(BURGUNDY_L, 1.15))
    for z in range(32, 44, 3):
        d.point(R.P(205, 12, z), fill=GOLD_D)
    for x0 in (181, 202.6):
        R.box(img, x0, x0 + 2.4, 0, 37, 44, 46, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
        R.line(img, (x0 + 0.2, 1, 46), (x0 + 0.2, 36, 46), WOOD_L)
        px, py = R.P(x0 + 0.6, 0, 46)
        d.point((px, py), fill=GOLD)
    R.box(img, 183.4, 202.6, 16, 18, 44.5, 45.5, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.line(img, (183.4, 16.3, 45.5), (202.6, 16.3, 45.5), WOOD_L)
    _upholstery(img, (183.4, 18, 45.6), (19.2, 0, 0), (0, 15.2, 0))
    arch = [R.P(181 + 24 * t / 10, 36.5 + 2.2 * math.sin(math.pi * t / 10), 46.1) for t in range(11)]
    d.polygon([R.P(181, 33, 46.1)] + arch + [R.P(205, 33, 46.1)], fill=mul(WOOD, 0.95), outline=WOOD_D)
    d.line(arch[1:-1], fill=WOOD_L)
    R.line(img, (183.4, 33.4, 46.15), (202.6, 33.4, 46.15), mul(WOOD, 0.7))
    # a carved shell at the crown of the crest rail
    sx, sy = (int(round(v)) for v in R.P(193, 36.6, 46.2))
    d.point([(sx - 2, sy + 1), (sx - 1, sy), (sx + 1, sy), (sx + 2, sy + 1)], fill=GOLD_D)
    d.point([(sx, sy - 1), (sx, sy)], fill=GOLD)
    for x in (182.2, 203.8):
        _finial(d, R.P(x, 38, 46))


def chair_toppled(img):
    """The desk chair knocked over on its back: the tufted back flat on the carpet with its crest rail and finials,
    the seat on end showing its webbed underside, and the legs sticking out stiff, front pair over rear."""
    d = ImageDraw.Draw(img)
    a, b = R.P(176, 0, 49), R.P(213, 0, 49)
    shadow(img, "rect", [a[0] - 1, a[1] - 5, b[0] + 3, a[1] + 2], 0.4, 3)
    # the far pair of legs, behind the seat
    R.line(img, (201.5, 1.2, 35.5), (212, 1.2, 35.5), mul(WOOD, 0.8), 2)
    R.line(img, (201.5, 13.5, 35.5), (211.5, 13, 35.5), mul(WOOD, 0.8), 2)
    R.line(img, (207, 1.5, 35.5), (207, 13, 35.5), WOOD_D)
    # the back lying flat: a wooden frame, stiles down its long sides, the tufted panel facing up
    R.box(img, 178, 197, 0, 3, 34, 49, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    for z0 in (34, 47):
        R.box(img, 178, 201.5, 0, 3.4, z0, z0 + 2, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
        R.line(img, (178, 3.4, z0 + 2), (201.5, 3.4, z0 + 2), WOOD_L)
    _upholstery(img, (180, 3.05, 36), (15.5, 0, 0), (0, 0, 11))
    R.box(img, 176, 180, 0, 4.2, 34, 49, mul(WOOD, 0.95), top=WOOD_L, side=WOOD_D)
    R.line(img, (176, 4.2, 49), (180, 4.2, 49), WOOD_L)
    sx, sy = (int(round(v)) for v in R.P(177.8, 4.2, 41.5))
    d.point([(sx, sy - 1), (sx, sy + 1)], fill=GOLD_D)
    d.point((sx, sy), fill=GOLD)
    for z in (35, 48):
        _finial(d, R.P(175.5, 2, z))
    # the seat on end: cushion against the back, the rail behind it, webbing and burlap where the bottom shows
    R.box(img, 197, 199.6, 0.5, 14.5, 34.5, 48.5, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))
    R.box(img, 199.5, 201.5, 0, 15, 34, 49, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.quad(img, [(201.55, 1.5, 35.5), (201.55, 1.5, 47.5), (201.55, 13.5, 47.5), (201.55, 13.5, 35.5)], hx("4a3a28"))
    for (p, q) in (((1.5, 38.5), (13.5, 38.5)), ((1.5, 44.5), (13.5, 44.5)), ((5, 35.5), (5, 47.5)),
                   ((10, 35.5), (10, 47.5))):
        R.line(img, (201.6, p[0], p[1]), (201.6, q[0], q[1]), hx("8a7656"))
    for z in range(36, 48, 3):
        d.point(R.P(200.5, 15, z), fill=GOLD_D)
    # the near pair of legs, the brass caps on their feet
    R.line(img, (201.5, 1.2, 47.5), (212, 1.2, 47.5), WOOD, 2)
    R.line(img, (201.5, 2, 47.5), (212, 2, 47.5), WOOD_L)
    R.line(img, (201.5, 13.5, 47.5), (211.5, 13, 47.5), WOOD, 2)
    R.line(img, (201.5, 14.2, 47.5), (211.5, 13.7, 47.5), WOOD_L)
    R.line(img, (207, 2.5, 47.5), (207, 12.5, 47.5), WOOD_D)
    for (y, z) in ((1.2, 35.5), (13, 35.5), (1.2, 47.5), (13, 47.5)):
        d.point(R.P(212, y, z), fill=GOLD)


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
    chair_toppled(img)
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


def _mirror(img):
    """The oval gilt pier glass over the vanity: a carved shell crest between C-scrolls with a ribbon bow, a beaded
    frame with leaf scrolls at the sides and a pendant below, swags of gilt garland, and a glass that holds a dim
    reflection of the lamplit room."""
    d = ImageDraw.Draw(img)
    cx, cy, rx, ry = 444, 69, 18, 25
    hi, lo = hx("f4dc98"), mul(GOLD_D, 0.7)
    shadow(img, "ellipse", [cx - rx + 1, cy - ry + 2, cx + rx + 3, cy + ry + 4], 0.3, 2)
    # carved laurel trailing round the lower half of the frame, leaf by leaf
    for k in range(15):
        a = math.radians(15 + k * 10.7)
        x, y = cx + (rx + 1.5) * math.cos(a), cy + (ry + 1.5) * math.sin(a)
        d.point((round(x), round(y)), fill=GOLD_D)
        d.point((round(x + (1 if x > cx else -1) * (k % 2)), round(y + 1)), fill=GOLD if k % 3 else hi)
    # leaf scrolls standing off either side
    for s in (-1, 1):
        x = cx + s * (rx + 1)
        d.arc([x - 3, cy - 7, x + 3, cy - 1], 90 if s < 0 else 270, 270 if s < 0 else 90, fill=GOLD_D)
        d.point((x + s * 2, cy - 3), fill=GOLD)
        d.polygon([(x, cy), (x + s * 4, cy + 3), (x + s * 2, cy + 6), (x, cy + 4)], fill=GOLD)
        d.point((x + s * 2, cy + 3), fill=lo)
    # frame: dark outer edge, gilt band, bead-and-reel ring, a sight edge
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=lo)
    d.ellipse([cx - rx + 1, cy - ry + 1, cx + rx - 1, cy + ry - 1], fill=GOLD_D)
    d.ellipse([cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2], fill=GOLD)
    d.arc([cx - rx + 2, cy - ry + 2, cx + rx - 2, cy + ry - 2], 150, 290, fill=hi)
    for k in range(40):
        a = k / 40 * 2 * math.pi
        x, y = cx + (rx - 3.5) * math.cos(a), cy + (ry - 3.5) * math.sin(a)
        d.point((round(x), round(y)), fill=hi if k % 2 else GOLD_D)
    d.ellipse([cx - rx + 5, cy - ry + 5, cx + rx - 5, cy + ry - 5], fill=GOLD_D)
    # the glass: dark at the edges, a cool sheen, the window and a lamp's glow reflected, a bevel catching light
    g0 = (cx - rx + 6, cy - ry + 6, cx + rx - 6, cy + ry - 6)
    glass = Image.new("RGB", img.size)
    vgrad(glass, g0, hx("a8b4b8"), hx("6e7680"))
    gd = ImageDraw.Draw(glass)
    gd.rectangle([g0[0], cy + 6, g0[2], g0[3]], fill=hx("7a6e66"))
    gd.line([(g0[0], cy + 6), (g0[2], cy + 6)], fill=hx("958272"))
    gd.rectangle([cx - 9, cy - 9, cx - 1, cy + 3], fill=hx("6a5040"))
    gd.rectangle([cx - 8, cy - 8, cx - 2, cy + 2], fill=hx("4e5666"))
    gd.line([(cx - 5, cy - 8), (cx - 5, cy + 2)], fill=hx("6a5040"))
    gd.line([(cx - 8, cy - 3), (cx - 2, cy - 3)], fill=hx("6a5040"))
    for (x, y) in ((cx - 7, cy - 6), (cx - 3, cy - 5), (cx - 7, cy + 1), (cx - 3, cy)):
        gd.point((x, y), fill=hx("c8b88a"))
    gd.line([(cx + 5, cy - 2), (cx + 5, cy + 5)], fill=hx("8a6a40"))
    gd.polygon([(cx + 3, cy - 2), (cx + 7, cy - 2), (cx + 8, cy + 1), (cx + 2, cy + 1)], fill=hx("d8c8a0"))
    light(glass, "ellipse", [cx, cy - 8, cx + 12, cy + 6], hx("ffe0a0"), 0.35, 3)
    gd.line([(cx - 12, cy - 6), (cx - 3, cy + 16)], fill=hx("d0dcdc"))
    gd.line([(cx - 10, cy - 12), (cx - 6, cy - 2)], fill=hx("eef4f4"))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse(g0, fill=255)
    img.paste(glass, (0, 0), m)
    d.arc(g0, 200, 290, fill=hx("e8f0f0"))
    d.arc(g0, 20, 110, fill=hx("4a5664"))
    # crest: C-scrolls flanking a fanned shell, a ribbon bow on top
    top = cy - ry
    for s in (-1, 1):
        d.arc([cx + s * 9 - 4, top - 6, cx + s * 9 + 4, top + 2], 180 if s < 0 else 270, 90 if s < 0 else 180,
              fill=GOLD)
        d.point((cx + s * 13, top - 1), fill=hi)
        d.point((cx + s * 5, top - 2), fill=GOLD_D)
    d.pieslice([cx - 7, top - 9, cx + 7, top + 5], 180, 360, fill=GOLD)
    for k in range(5):
        a = math.pi + (k + 0.5) / 5 * math.pi
        d.line([(cx, top + 1), (cx + 7 * math.cos(a), top - 2 + 7 * math.sin(a))], fill=GOLD_D)
    d.arc([cx - 7, top - 9, cx + 7, top + 5], 200, 260, fill=hi)
    d.ellipse([cx - 1, top - 1, cx + 1, top + 1], fill=hi)
    by = top - 11
    d.polygon([(cx, by + 1), (cx - 4, by - 2), (cx - 4, by + 3)], fill=GOLD)
    d.polygon([(cx, by + 1), (cx + 4, by - 2), (cx + 4, by + 3)], fill=GOLD_D)
    d.line([(cx - 1, by + 2), (cx - 3, by + 6)], fill=GOLD)
    d.line([(cx + 1, by + 2), (cx + 3, by + 6)], fill=GOLD_D)
    d.point((cx, by + 1), fill=hi)
    # pendant drop under the frame
    bot = cy + ry
    d.polygon([(cx - 4, bot - 1), (cx + 4, bot - 1), (cx + 2, bot + 3), (cx, bot + 7), (cx - 2, bot + 3)], fill=GOLD)
    d.line([(cx + 4, bot - 1), (cx, bot + 7)], fill=GOLD_D)
    d.point((cx - 1, bot + 1), fill=hi)
    d.ellipse([cx - 1, bot + 7, cx + 1, bot + 9], fill=GOLD_D)


def vanity(img):
    """hotel.vanity with a far more ornate mirror; the card box shifted left to leave the right end for the telephone."""
    X0, X1, Z0, Z1 = 418, 470, 2, 22
    _mirror(img)
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0], a[1] - 3, b[0] + 4, a[1] + 3], 0.35, 3)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z1 - 2), (x, 22, Z1 - 2), WOOD_D, 2)
    R.box(img, X0, X1, 20, 30, Z0, Z1, mul(WOOD, 0.92), top=hx("8e6040"), side=WOOD_D)
    for c in (X0 + 3, X1 - 21):
        R.quad(img, [(c, 22, Z1), (c + 18, 22, Z1), (c + 18, 28, Z1), (c, 28, Z1)], None, WOOD_D)
        R.line(img, (c + 7, 25, Z1), (c + 11, 25, Z1), GOLD)
    for (x, h, col) in ((X0 + 8, 6, hx("c9a0b8")), (X0 + 14, 9, hx("e2c27a")), (X0 + 20, 5, hx("9fc0c8"))):
        R.box(img, x, x + 3, 30, 30 + h, 8, 11, col, top=mul(col, 1.15))
    R.box(img, X0 + 25, X0 + 34, 30, 31.5, 9, 16, hx("e6d8c0"), top=hx("f2e8d6"))
    S0, S1, Sz0, Sz1 = 432, 452, 30, 42
    for x in (S0 + 2, S1 - 2):
        for z in (Sz0 + 2, Sz1 - 2):
            R.line(img, (x, 0, z), (x, 13, z), WOOD_D, 2)
    R.box(img, S0, S1, 13, 17, Sz0, Sz1, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))


RED = (hx("a81c2c"), hx("6a1018"), hx("dc4a5a"), hx("2a0a10"), hx("1e0608"))


def tidy_floor(img, bench=True):
    """Room 507 before the searchers came: the desk chair pulled up square, and her red evening dress laid across the
    upholstered bench at the foot of the closet, a loose thread hanging from the hem. The bench stands out in the room,
    so it is painted on its own (bench=False leaves only its shadow) and cut out as a y-sorted sprite."""
    d = ImageDraw.Draw(img)
    chair_upright(img)
    # the bench, and the dress laid out across it
    B0, B1, Bz0, Bz1 = 90, 140, 104, 122
    a, b = R.P(B0, 0, Bz1), R.P(B1, 0, Bz1)
    shadow(img, "rect", [a[0] - 1, a[1] - 3, b[0] + 4, a[1] + 3], 0.4, 3)
    if not bench:
        return
    for x in (B0 + 2, B1 - 2):
        for z in (Bz0 + 2, Bz1 - 2):
            R.line(img, (x, 0, z), (x, 9, z), WOOD_D, 2)
    R.box(img, B0, B1, 9, 13, Bz0, Bz1, hx("d8c8a0"), top=hx("ece0c4"), side=hx("a89870"))
    R.line(img, (B0, 9, Bz1), (B1, 9, Bz1), GOLD_D)
    # lying flat along the seat, seen from above at a slant, the hem falling over the far end
    spr = dress(22, 46, RED, folds=3).rotate(90, expand=True)
    spr = _crumple(spr.resize((spr.width, max(1, spr.height * 4 // 5)), Image.NEAREST), 0.6, 14, 0.4)
    sx, sy = R.P(B0 + 3, 13, (Bz0 + Bz1) / 2)
    _stamp(img, spr, sx, sy - spr.height / 2)
    ex, ey = sx + spr.width - 3, sy - spr.height / 2 + 1
    d.polygon([(ex, ey), (ex + 3, ey + 1), (ex + 4, ey + spr.height + 3), (ex + 1, ey + spr.height + 2)],
              fill=RED[1], outline=RED[4])
    # a loose silk thread from the torn hem
    d.line([(ex + 3, ey + spr.height + 3), (ex + 4, ey + spr.height + 6), (ex + 3, ey + spr.height + 9)], fill=RED[2])

def paint(closet_open=False, safe_open=False, box=False, drawer_open=False, paper=False, tidy=False, bench=True,
          phone=True, ajar=False):
    img = Image.new("RGB", (W, H))
    hotel.shell(img)
    crooked_painting(img, 0 if tidy else -6)
    hotel.floor(img)
    hotel.door(img)
    window_night(img, tidy)
    sconces(img)
    closet(img, closet_open, safe_open, box, tidy, ajar)
    desk(img, drawer_open, paper, tidy)
    if tidy:
        hotel.bed(img)
    else:
        bed(img)
    hotel.nightstand(img, lamp=False)
    lamp = bedside_lamp(img)
    vanity(img)
    ringer(img, tidy)
    if tidy and phone:
        telephone(img)
    if tidy:
        tidy_floor(img, bench)
    else:
        mess(img)
        telephone_down(img)
    hotel.chandelier(img)
    img = tall(img, hotel.ceiling)
    # night: the only light comes from the sconces, the bedside lamp and the city outside
    dark = Image.new("RGB", img.size, (70, 70, 120))
    img = ImageChops.multiply(img, Image.blend(dark, Image.new("RGB", img.size, (255, 240, 210)), 0.55))
    lx, ly = lamp[0], lamp[1] + TOP
    light(img, "ellipse", [lx - 30, ly - 26, lx + 30, ly + 30], hx("ffd8a0"), 0.12, 10)
    light(img, "ellipse", [lx - 7, ly - 5, lx + 7, ly + 5], hx("fff0c8"), 0.2, 3)
    light(img, "ellipse", [96, 40, 296, 140], hx("ffe0a0"), 0.18, 18)
    light(img, "polygon", [(166, 134), (222, 134), (300, H + TOP - 1), (150, H + TOP - 1)], hx("6a80c0"), 0.1, 12)
    vignette(img, 0.4, tint=(30, 24, 40), blur=34)
    return img


def _bbox(a, b):
    return ImageChops.difference(a, b).getbbox()


def _pinned(img, box, n):
    q = img.crop(box).quantize(n, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()
    return [tuple(pal[i * 3:i * 3 + 3]) for i in range(n)]


def build():
    base = paint()
    # the painting's sky, lake and meadow and the lamp's silk are small next to the cream walls, so their colours are
    # pinned or quantising turns the landscape tan and the shade into wallpaper
    lx, ly = (int(v) for v in R.P(399, 28, 13))
    pal = (palette_of(base, 128) + _pinned(base, (296, 52, 352, 96), 16)
           + _pinned(base, (lx - 9, ly + TOP - 32, lx + 10, ly + TOP + 2), 10))
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
    # the First Interlude: the same room the night she left, before the old man's men turned it over
    tidy = paint(tidy=True)
    tpal = (palette_of(tidy, 128) + _pinned(tidy, (296, 52, 352, 96), 16)
            + _pinned(tidy, (lx - 9, ly + TOP - 32, lx + 10, ly + TOP + 2), 10) + _pinned(tidy, (90, 205, 160, 240), 8))
    with_bench = pixelize(paint(tidy=True, phone=False), tpal)
    room = pixelize(paint(tidy=True, bench=False, phone=False), tpal)
    save(room, "rooms", "eleanor_room_interlude.png")
    # the bench with the dress is a y-sorted sprite Eleanor walks around (and behind), cut out pixel by pixel
    box = _bbox(room, with_bench)
    mask = ImageChops.difference(room, with_bench).convert("L").point(lambda v: 255 if v else 0)
    bench = with_bench.convert("RGBA")
    bench.putalpha(mask)
    save(bench.crop(box), "rooms", "eleanor_room_interlude_bench.png")
    print(f"  eleanor_room_interlude_bench.png at {box[:2]}, size {(box[2] - box[0], box[3] - box[1])}")
    # the telephone on the vanity is its own sprite too, so it can go when she lifts it for the call
    with_phone = pixelize(paint(tidy=True, bench=False), tpal)
    box = _bbox(room, with_phone)
    mask = ImageChops.difference(room, with_phone).convert("L").point(lambda v: 255 if v else 0)
    phone = with_phone.convert("RGBA")
    phone.putalpha(mask)
    save(phone.crop(box), "rooms", "eleanor_room_interlude_telephone.png")
    print(f"  eleanor_room_interlude_telephone.png at {box[:2]}, size {(box[2] - box[0], box[3] - box[1])}")
    # Puzzle 17: her closet opened on the safe she left standing half open, the box put in it, the door shut on it
    tstates = {
        "closet_open": pixelize(paint(tidy=True, bench=False, phone=False, closet_open=True), tpal),
        "safe_ajar": pixelize(paint(tidy=True, bench=False, phone=False, closet_open=True, ajar=True), tpal),
        "safe_box": pixelize(paint(tidy=True, bench=False, phone=False, closet_open=True, ajar=True, box=True), tpal),
    }
    for name, under in (("closet_open", room), ("safe_ajar", tstates["closet_open"]), ("safe_box", tstates["safe_ajar"])):
        box = _bbox(under, tstates[name])
        save(tstates[name].crop(box), "rooms", f"eleanor_room_interlude_{name}.png")
        print(f"  eleanor_room_interlude_{name}.png at {box[:2]}")
    return px
