"""The Aurelian: a gleaming art-deco hotel lobby."""
from PIL import Image, ImageDraw
import math
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, cut, frieze, sunburst)

FLOOR = 138
GOLD, GOLD_D, CREAM = hx("d8b050"), hx("8a6a28"), hx("e8dcc0")


def walls(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("d8c8a4"), hx("b8a684"))
    noise(img, (0, 0, W - 1, FLOOR), 3, 21)
    # ceiling coffer band + chevron frieze
    vgrad(img, (0, 0, W - 1, 10), hx("3a2a1a"), hx("5a4228"))
    frieze(d, 10, 17, hx("2a1e14"), GOLD, step=8)
    d.line([(0, 18), (W, 18)], fill=GOLD_D)
    # fluted wall panels
    for x in range(0, W, 24):
        d.line([(x, 20), (x, FLOOR - 26)], fill=hx("c4b290"))
        d.line([(x + 1, 20), (x + 1, FLOOR - 26)], fill=hx("ece0c4"))
    # black marble dado with gold strip
    vgrad(img, (0, FLOOR - 24, W - 1, FLOOR), hx("2a2428"), hx("161216"))
    d.line([(0, FLOOR - 25), (W, FLOOR - 25)], fill=GOLD)
    noise(img, (0, FLOOR - 24, W - 1, FLOOR), 5, 22)
    for x in range(0, W, 40):
        d.line([(x + 5, FLOOR - 20), (x + 20, FLOOR - 4)], fill=hx("3a3238"))
        d.line([(x + 12, FLOOR - 22), (x + 16, FLOOR - 15), (x + 14, FLOOR - 9), (x + 22, FLOOR - 2)], fill=hx("4a4048"))
        d.point((x + 30, FLOOR - 12), fill=hx("5a5058"))


def floor(img):
    d = ImageDraw.Draw(img)
    vx, vy = 240, -200
    rows, y, step = [], float(FLOOR), 6.0
    while y < H:
        rows.append(y)
        y += step
        step *= 1.12
    rows.append(H)

    def xat(xb, yy):
        return vx + (xb - vx) * (yy - vy) / (H - vy)

    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        for i in range(-30, 31):
            xa, xb2 = vx + i * 20, vx + (i + 1) * 20
            col = hx("d8ccb0") if (i + r) % 2 == 0 else hx("2a2a30")
            d.polygon([(xat(xa, ya), ya), (xat(xb2, ya), ya), (xat(xb2, yb), yb), (xat(xa, yb), yb)], fill=col)
    noise(img, (0, FLOOR, W - 1, H - 1), 6, 23)
    # gold inlay border and polish reflections
    d.line([(0, FLOOR + 2), (W, FLOOR + 2)], fill=GOLD_D)
    light(img, "ellipse", [180, FLOOR, 300, H], hx("fff4d0"), 0.25, 14)
    light(img, "ellipse", [300, FLOOR, 380, 180], hx("fff0c0"), 0.2, 10)


def plaque_and_cubbies(img):
    d = ImageDraw.Draw(img)
    d.rectangle([28, 20, 128, 36], fill=hx("1e1a14"))
    d.rectangle([30, 22, 126, 34], outline=GOLD)
    text(img, (78, 28), "THE AURELIAN", GOLD, size=8)
    d.rectangle([22, 40, 134, 92], fill=hx("4a2e1a"))
    for r in range(4):
        for c in range(8):
            x, y = 26 + c * 13, 43 + r * 12
            d.rectangle([x, y, x + 10, y + 9], fill=hx("2a180c"))
            if (r * 3 + c) % 4 == 1:
                d.rectangle([x + 2, y + 4, x + 8, y + 9], fill=hx("e0d8c0"))
            if (r + c) % 5 == 2:
                d.line([(x + 5, y + 1), (x + 5, y + 6)], fill=GOLD)
                d.point((x + 5, y + 7), fill=GOLD)


def desk(img, d=None):
    d = d or ImageDraw.Draw(img)
    vgrad(img, (14, 104, 142, 150), hx("3a2414"), hx("1e120a"))
    d.rectangle([10, 98, 146, 104], fill=hx("1e1a20"))
    d.line([(10, 98), (146, 98)], fill=hx("6a6070"))
    d.line([(10, 104), (146, 104)], fill=GOLD)
    sunburst(d, 78, 150, 34, 14, hx("6a4424"), hx("4a2c16"))
    for x in (20, 136):
        d.rectangle([x - 3, 106, x + 3, 150], fill=hx("2a1a10"))
        d.line([(x, 106), (x, 150)], fill=GOLD_D)
    d.line([(14, 150), (142, 150)], fill=GOLD)
    # bell, ledger, lamp
    d.chord([116, 92, 126, 102], 180, 360, fill=GOLD)
    d.point((121, 91), fill=GOLD)
    d.polygon([(40, 96), (64, 96), (66, 98), (38, 98)], fill=hx("e0d8c0"))
    d.line([(52, 96), (52, 98)], fill=hx("6a1a1a"))
    d.rectangle([92, 82, 94, 97], fill=GOLD_D)
    d.polygon([(86, 82), (100, 82), (96, 74), (90, 74)], fill=hx("f0e0b0"))


def elevator(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 196, 60, 274, 137
    cx = (x0 + x1) // 2
    # stepped black-marble surround with gold edging, ziggurat-style
    for k, (dx, dy) in enumerate(((12, 12), (8, 18), (4, 23))):
        d.rectangle([x0 - dx, y0 - dy, x1 + dx, y1], fill=hx("221c20"))
        d.line([(x0 - dx, y0 - dy), (x1 + dx, y0 - dy)], fill=GOLD if k == 2 else GOLD_D)
        d.line([(x0 - dx, y0 - dy), (x0 - dx, y1)], fill=GOLD_D)
        d.line([(x1 + dx, y0 - dy), (x1 + dx, y1)], fill=hx("4a3a20"))
    noise(img, (x0 - 12, y0 - 23, x1 + 12, y1), 4, 51)
    for vx, vy, dx2, dy2 in ((x0 - 10, 80, 6, 18), (x1 + 4, 70, 5, 24), (x0 - 9, 112, 5, 14), (x1 + 3, 108, 6, 20)):
        d.line([(vx, vy), (vx + dx2 // 2, vy + dy2 // 2), (vx + dx2, vy + dy2)], fill=hx("3e3438"))
    # fan transom: gold rays inside a dark arch, a floor dial at its heart
    d.pieslice([cx - 38, y0 - 40, cx + 38, y0 + 36], 180, 360, fill=hx("1a1410"))
    sunburst(d, cx, y0 - 2, 34, 18, GOLD, hx("9a7428"))
    d.arc([cx - 34, y0 - 36, cx + 34, y0 + 32], 180, 360, fill=hx("f0d890"))
    d.arc([cx - 37, y0 - 39, cx + 37, y0 + 35], 180, 360, fill=GOLD_D)
    d.arc([cx - 24, y0 - 26, cx + 24, y0 + 22], 180, 360, fill=hx("6a4c1c"))
    d.pieslice([cx - 15, y0 - 17, cx + 15, y0 + 13], 180, 360, fill=hx("141010"), outline=GOLD)
    d.pieslice([cx - 12, y0 - 14, cx + 12, y0 + 10], 180, 360, fill=hx("2a2218"))
    for i in range(9):
        a = math.pi + (i + 0.5) * math.pi / 9
        d.point((round(cx + 10 * math.cos(a)), round(y0 - 2 + 10 * math.sin(a))),
                fill=hx("ffe890") if i == 5 else hx("a88a4a"))
    a = math.pi + 5.5 * math.pi / 9
    d.line([(cx, y0 - 2), (round(cx + 9 * math.cos(a)), round(y0 - 2 + 9 * math.sin(a)))], fill=hx("e04040"))
    d.ellipse([cx - 2, y0 - 4, cx + 2, y0], fill=GOLD)
    d.ellipse([cx - 2, y0 - 41, cx + 2, y0 - 37], fill=hx("fff0b0"))
    light(img, "ellipse", [cx - 8, y0 - 47, cx + 8, y0 - 31], hx("fff0b0"), 0.5, 3)
    # transom bar with rivets
    d.rectangle([x0 - 4, y0 - 2, x1 + 4, y0 + 2], fill=GOLD_D)
    d.line([(x0 - 4, y0 - 2), (x1 + 4, y0 - 2)], fill=hx("f0d890"))
    for x in range(x0, x1 + 1, 6):
        d.point((x, y0), fill=hx("f0d890"))
    # brass jambs
    for jx in (x0 - 4, x1 + 1):
        hgrad(img, (jx, y0 + 3, jx + 3, y1), hx("e8c870"), hx("7a5a20"))
    # brass doors: framed panels, a fountain motif up top, diamond lattice below, a kick plate
    for dx0, dx1 in ((x0, cx - 1), (cx + 1, x1)):
        hgrad(img, (dx0, y0 + 3, dx1, y1), hx("d4ae5c"), hx("8a6a2a"))
        mid = (dx0 + dx1) // 2
        d.rectangle([dx0 + 3, y0 + 7, dx1 - 3, y0 + 36], outline=hx("6a4c18"))
        d.line([(dx0 + 4, y0 + 8), (dx1 - 4, y0 + 8)], fill=hx("f0d890"))
        for r in (12, 9, 6):
            d.arc([mid - r, y0 + 34 - r, mid + r, y0 + 34 + r], 180, 360, fill=hx("6a4c18"))
        d.line([(mid, y0 + 12), (mid, y0 + 34)], fill=hx("6a4c18"))
        for k in range(3):
            yy = y0 + 13 + k * 5
            d.line([(mid - 3 - k, yy + 3), (mid, yy), (mid + 3 + k, yy + 3)], fill=hx("f0d890"))
        d.rectangle([dx0 + 3, y0 + 40, dx1 - 3, y1 - 13], outline=hx("6a4c18"))
        for k in range(4):
            yy = y0 + 42 + k * 8
            d.polygon([(mid, yy), (mid + 7, yy + 4), (mid, yy + 8), (mid - 7, yy + 4)], outline=hx("5a4418"))
            d.point((mid, yy + 4), fill=hx("f0d890"))
        d.rectangle([dx0 + 1, y1 - 10, dx1 - 1, y1], fill=hx("6a5020"))
        for yy in (y1 - 8, y1 - 5, y1 - 2):
            d.line([(dx0 + 2, yy), (dx1 - 2, yy)], fill=hx("8a6a2a"))
        for x in (dx0 + 2, dx1 - 2):
            for yy in (y0 + 5, y1 - 12):
                d.point((x, yy), fill=hx("f8e8a8"))
    d.line([(cx, y0 + 3), (cx, y1)], fill=hx("2a1e10"), width=2)
    light(img, "polygon", [(x0 + 4, y0 + 3), (x0 + 14, y0 + 3), (x0 + 2, y1), (x0, y1)], hx("fff4c0"), 0.35, 2)
    light(img, "polygon", [(cx + 8, y0 + 3), (cx + 14, y0 + 3), (cx + 4, y1), (cx + 1, y1)], hx("fff4c0"), 0.2, 2)
    # call buttons on the marble
    d.rectangle([x1 + 5, 94, x1 + 10, 108], fill=GOLD_D, outline=hx("f0d890"))
    d.ellipse([x1 + 6, 96, x1 + 9, 99], fill=hx("fff0c0"))
    d.ellipse([x1 + 6, 102, x1 + 9, 105], fill=hx("3a2a1a"))
    # gold reflected on the polished floor
    light(img, "rect", [x0 - 4, y1 + 1, x1 + 4, y1 + 14], hx("e8c060"), 0.22, 4)


def sconce(img, x, y):
    """Art-deco fan sconce: frosted glass shell on a stepped gold bracket."""
    d = ImageDraw.Draw(img)
    light(img, "ellipse", [x - 16, y - 22, x + 16, y + 12], hx("fff0c0"), 0.45, 6)
    d.rectangle([x - 2, y + 1, x + 2, y + 8], fill=GOLD_D)
    d.rectangle([x - 3, y + 6, x + 3, y + 8], fill=GOLD)
    d.point((x, y + 10), fill=GOLD)
    d.pieslice([x - 6, y - 7, x + 6, y + 5], 180, 360, fill=hx("fff4dc"), outline=GOLD)
    for a in (-0.9, -0.3, 0.3, 0.9):
        d.line([(x, y), (round(x + 5 * math.sin(a)), round(y - 5 * math.cos(a)))], fill=hx("e0c890"))
    d.line([(x - 6, y), (x + 6, y)], fill=GOLD)


def pilaster(img, x):
    d = ImageDraw.Draw(img)
    hgrad(img, (x - 6, 18, x + 6, FLOOR), hx("f0e6d0"), hx("a89878"))
    for k in range(3):
        d.line([(x - 3 + k * 3, 24), (x - 3 + k * 3, FLOOR - 28)], fill=hx("b8a888"))
    d.rectangle([x - 8, 18, x + 8, 24], fill=GOLD)
    d.polygon([(x - 8, 24), (x + 8, 24), (x, 32)], fill=GOLD_D)
    d.rectangle([x - 8, FLOOR - 26, x + 8, FLOOR], fill=hx("1e1a20"))
    d.line([(x - 8, FLOOR - 26), (x + 8, FLOOR - 26)], fill=GOLD)


def palm(img, x, base):
    """Kentia palm in a black-glazed deco planter."""
    d = ImageDraw.Draw(img)
    shadow(img, "ellipse", [x - 14, base - 3, x + 14, base + 4], 0.5, 2)
    # planter: flared rim, tapering glazed body, stepped gold foot
    d.polygon([(x - 11, base - 24), (x + 11, base - 24), (x + 7, base - 6), (x - 7, base - 6)], fill=hx("201c22"))
    d.rectangle([x - 12, base - 26, x + 12, base - 23], fill=GOLD_D)
    d.line([(x - 12, base - 26), (x + 12, base - 26)], fill=hx("f0d890"))
    d.ellipse([x - 10, base - 27, x + 10, base - 24], fill=hx("2a1a10"))
    for k in range(3):
        yy = base - 19 + k * 4
        w = 9 - k
        d.line([(x - w, yy), (x, yy - 3), (x + w, yy)], fill=GOLD_D if k else GOLD)
    d.line([(x - 8, base - 22), (x - 6, base - 8)], fill=hx("5a5060"))
    d.rectangle([x - 8, base - 6, x + 8, base - 3], fill=GOLD_D)
    d.rectangle([x - 6, base - 3, x + 6, base], fill=hx("1a1418"))
    d.line([(x - 8, base - 6), (x + 8, base - 6)], fill=GOLD)
    # two ringed stems
    crowns = []
    for sx, lean, h in ((-1, -0.12, 44), (2, 0.1, 36)):
        for i, t in enumerate(range(0, h, 3)):
            px, py = x + sx + lean * t, base - 26 - t
            d.line([(px - 1, py), (px + 1, py - 2)], fill=hx("6a5030") if i % 2 else hx("4a3420"), width=2)
        crowns.append((x + sx + lean * h, base - 26 - h))
    # arching fronds: a rachis that rises then droops, long leaflets hanging from it; dark fronds behind
    rnd = __import__("random").Random(x)
    fronds = []
    for c, (cx0, cy0) in enumerate(crowns):
        for k in range(7):
            ang = math.radians(-160 + k * 23 + rnd.uniform(-6, 6))
            fronds.append((cx0, cy0, ang, rnd.randint(20, 27), (k + c) % 3))
    fronds.sort(key=lambda f: (f[4], -abs(math.cos(f[2]))))
    for cx0, cy0, ang, ln, tone in fronds:
        dark, mid, lit = ((hx("123220"), hx("1a4226"), hx("24502e")), (hx("1a4226"), hx("2a6236"), hx("468a48")),
                          (hx("22542e"), hx("367a40"), hx("72b066")))[tone]
        pts = []
        for i in range(ln + 1):
            t = i / ln
            pts.append((cx0 + math.cos(ang) * ln * t, cy0 + math.sin(ang) * ln * t * (1 - t) * 1.6 + 14 * t * t))
        for i in range(2, ln - 1, 2):
            px, py = pts[i]
            leaf = 7 * math.sin(math.pi * i / ln) + 2
            side = 1 if math.cos(ang) >= 0 else -1
            d.line([(px, py), (px + side * leaf * 0.5, py + leaf)], fill=mid)
            d.line([(px, py), (px - side * leaf * 0.2, py + leaf * 0.9)], fill=dark)
        d.line(pts, fill=lit)

def chandelier(img, x):
    """Three-tier crystal waterfall chandelier on a gold crown."""
    d = ImageDraw.Draw(img)
    light(img, "ellipse", [x - 70, -20, x + 70, 90], hx("fff0c0"), 0.45, 18)
    d.line([(x, 0), (x, 16)], fill=GOLD_D)
    for yy in range(2, 16, 4):
        d.ellipse([x - 1, yy, x + 1, yy + 2], fill=GOLD)
    d.polygon([(x - 6, 16), (x + 6, 16), (x + 3, 20), (x - 3, 20)], fill=GOLD, outline=GOLD_D)
    for k, (w, y, drop) in enumerate(((19, 22, 9), (14, 31, 8), (9, 40, 7))):
        light(img, "ellipse", [x - w - 2, y - 3, x + w + 2, y + 6], hx("fff8e0"), 0.6, 2)
        d.polygon([(x - w, y), (x + w, y), (x + w - 3, y + 4), (x - w + 3, y + 4)], fill=GOLD, outline=GOLD_D)
        d.line([(x - w + 1, y), (x + w - 1, y)], fill=hx("fff0b0"))
        for i, xx in enumerate(range(x - w + 2, x + w - 1, 3)):
            ln = drop - (2 if i % 2 else 0)
            d.line([(xx, y + 5), (xx, y + 4 + ln)], fill=hx("e8ecf8"))
            d.point((xx, y + 5 + ln), fill=hx("ffffff") if (i + k) % 3 else hx("b8d0f0"))
        for xx in (x - w // 2, x + w // 2):
            d.ellipse([xx - 1, y - 3, xx + 1, y], fill=hx("fffce8"))
    d.line([(x, 44), (x, 52)], fill=GOLD)
    d.ellipse([x - 2, 52, x + 2, 56], fill=hx("f0f4ff"), outline=hx("a8b8d8"))


def urn(img):
    d = ImageDraw.Draw(img)
    d.rectangle([352, 116, 360, 150], fill=hx("2a2428"))
    d.ellipse([346, 108, 366, 118], fill=hx("c0a050"))
    d.ellipse([349, 110, 363, 115], fill=hx("4a4048"))
    d.rectangle([348, 148, 364, 152], fill=GOLD_D)
    shadow(img, "ellipse", [344, 150, 372, 156], 0.45, 2)


def revolving_door(img):
    """Brass revolving door onto State St: a glazed drum with four wings, a lettered canopy, fixed side lights."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 394, 30, 478, 137
    cx = (x0 + x1) // 2
    d.rectangle([x0 - 4, y0 - 8, x1 + 2, y1], fill=hx("2a2018"))
    # canopy: black glass sign with gilt lettering and a stepped cornice
    d.rectangle([x0 - 4, y0 - 8, x1 + 2, y0 + 4], fill=hx("141012"))
    d.line([(x0 - 4, y0 - 8), (x1 + 2, y0 - 8)], fill=GOLD)
    d.line([(x0 - 4, y0 + 4), (x1 + 2, y0 + 4)], fill=GOLD)
    d.line([(x0 - 4, y0 + 6), (x1 + 2, y0 + 6)], fill=GOLD_D)
    text(img, (cx, y0 - 2), "STATE ST", GOLD, size=8)
    for x in (x0 + 2, x1 - 4):
        d.polygon([(x - 2, y0 - 2), (x, y0 - 5), (x + 2, y0 - 2), (x, y0 + 1)], fill=GOLD)
    # night street through the glass: a far building, a lamp and a passing cab's lights (the rain falls in the scene)
    g0, g1 = y0 + 8, y1 - 4
    vgrad(img, (x0, g0, x1, g1), hx("16203a"), hx("2a2a3a"))
    d.rectangle([x0 + 30, g0 + 10, x0 + 70, g1 - 30], fill=hx("1a1a28"))
    for wx in range(x0 + 33, x0 + 68, 6):
        for wy in range(g0 + 13, g1 - 34, 8):
            if (wx * 7 + wy * 3) % 5 < 2:
                d.rectangle([wx, wy, wx + 2, wy + 3], fill=hx("c8a050"))
    d.rectangle([x0, g1 - 18, x1, g1], fill=hx("1e1e28"))
    d.line([(x0, g1 - 18), (x1, g1 - 18)], fill=hx("4a4a5a"))
    for hx0 in (x0 + 52, x0 + 62):
        d.ellipse([hx0, g1 - 14, hx0 + 4, g1 - 11], fill=hx("fff0b0"))
    light(img, "ellipse", [x0 + 44, g1 - 20, x0 + 74, g1 - 4], hx("f0d080"), 0.35, 4)
    d.line([(x0 + 24, 58), (x0 + 24, g1 - 18)], fill=hx("2a2a30"), width=2)
    d.line([(x0 + 21, 58), (x0 + 27, 58)], fill=hx("2a2a30"))
    d.ellipse([x0 + 21, 52, x0 + 27, 58], fill=hx("f0d890"))
    light(img, "ellipse", [x0 + 12, 42, x0 + 36, 66], hx("f0c060"), 0.4, 4)
    # fixed side lights in brass frames
    for sx0, sx1 in ((x0, x0 + 12), (x1 - 12, x1)):
        d.rectangle([sx0, g0, sx1, g1], outline=GOLD, width=2)
        d.line([(sx0, 96), (sx1, 96)], fill=GOLD, width=2)
    # the drum: curved glass enclosure, a centre post and four wings in perspective
    dx0, dx1 = x0 + 14, x1 - 14
    d.arc([dx0, g0 - 4, dx1, g0 + 10], 0, 180, fill=GOLD, width=2)
    d.arc([dx0, g1 - 8, dx1, g1 + 6], 0, 180, fill=GOLD, width=2)
    for xx in (dx0, dx1):
        d.line([(xx, g0 + 3), (xx, g1 - 1)], fill=GOLD, width=2)
    light(img, "rect", [dx0 + 3, g0 + 4, dx0 + 9, g1 - 4], hx("a0b8e0"), 0.18, 1)
    # wings: one swung towards us on the left, one receding on the right, one seen edge-on behind the post
    def wing(far_x, top_y, bot_y, near):
        col = GOLD if near else GOLD_D
        quad = [(cx, g0 + 7), (far_x, top_y), (far_x, bot_y), (cx, g1 - 3)]
        light(img, "polygon", quad, hx("c8d8f0"), 0.22 if near else 0.12, 0)
        kick = [(cx, g1 - 11), (far_x, bot_y - (10 if near else 7)), (far_x, bot_y), (cx, g1 - 3)]
        d.polygon(kick, fill=hx("8a6a2a") if near else hx("5a4418"))
        d.line([kick[0], kick[1]], fill=hx("f0d890") if near else GOLD_D)
        d.line([(cx, g0 + 7), (far_x, top_y)], fill=col, width=2 if near else 1)
        d.line([(far_x, top_y), (far_x, bot_y)], fill=col, width=2 if near else 1)
        d.line([(far_x, bot_y), (cx, g1 - 3)], fill=col)
        mid_far = (top_y + bot_y) // 2 + 2
        d.line([(cx + (far_x - cx) // 3, 94), (far_x + (3 if far_x < cx else -3), mid_far)],
               fill=hx("f8e8b0") if near else GOLD)
    d.line([(cx, g0 + 6), (cx, g1 - 3)], fill=GOLD_D, width=5)
    wing(dx1 - 6, g0 + 10, g1 - 6, False)
    wing(dx0 + 3, g0 + 13, g1 + 3, True)
    d.rectangle([cx - 1, g0 + 4, cx + 1, g1], fill=GOLD)
    d.line([(cx - 1, g0 + 4), (cx - 1, g1)], fill=hx("fff0b0"))
    d.ellipse([cx - 3, g0 + 2, cx + 3, g0 + 6], fill=GOLD)
    light(img, "rect", [x0, g0, x1, g1], hx("6080c0"), 0.12, 4)
    # brass threshold ring on the marble
    d.ellipse([dx0 - 2, y1 - 5, dx1 + 2, y1 + 3], outline=GOLD)


def wall_clock(img, cx=300, cy=48):
    """Sunburst wall clock on the pilaster between the elevator and the staff door."""
    d = ImageDraw.Draw(img)
    sunburst(d, cx, cy, 12, 16, GOLD, GOLD_D, 0, 2 * math.pi)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=GOLD_D)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=hx("f4ead0"), outline=hx("6a4c18"))
    for i in range(12):
        a = i * math.pi / 6
        d.point((round(cx + 6 * math.sin(a)), round(cy - 6 * math.cos(a))), fill=hx("2a2018"))
    d.line([(cx, cy), (cx, cy - 5)], fill=hx("1e1a14"))
    d.line([(cx, cy), (cx + 4, cy + 2)], fill=hx("1e1a14"))
    d.point((cx, cy), fill=hx("a01818"))


def uplighter(img, x, y=44):
    """Alabaster bowl uplighter on a pilaster, washing the fluting with light."""
    d = ImageDraw.Draw(img)
    light(img, "polygon", [(x - 6, y), (x + 6, y), (x + 14, y - 24), (x - 14, y - 24)], hx("fff4d0"), 0.4, 4)
    d.chord([x - 7, y - 4, x + 7, y + 6], 0, 180, fill=hx("f4ead8"), outline=GOLD_D)
    d.line([(x - 7, y + 1), (x + 7, y + 1)], fill=GOLD)
    d.polygon([(x - 2, y + 6), (x + 2, y + 6), (x, y + 10)], fill=GOLD_D)
    d.line([(x - 4, y + 3), (x + 4, y + 3)], fill=hx("fffaf0"))


def mirror(img):
    """A tall gilt mirror over the urn, catching the chandelier."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 350, 44, 374, 102
    d.rounded_rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], 10, fill=GOLD_D)
    d.rounded_rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], 9, outline=hx("f0d890"))
    vgrad(img, (x0, y0 + 2, x1, y1), hx("b8aa90"), hx("8a8070"))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], 8, fill=255)
    glass = img.copy()
    gd = ImageDraw.Draw(glass)
    vgrad(glass, (x0, y0, x1, y1), hx("c8bca0"), hx("8a8070"))
    gd.line([(x0 + 3, y1 - 6), (x1 - 3, y0 + 18)], fill=hx("e8e0d0"), width=2)
    gd.line([(x0 + 3, y1 - 16), (x1 - 8, y0 + 18)], fill=hx("d8d0c0"))
    gd.ellipse([x1 - 9, y0 + 6, x1 - 5, y0 + 10], fill=hx("fff4d0"))
    img.paste(glass, (0, 0), m)
    d.polygon([(x0 + 8, y0 - 3), (x1 - 8, y0 - 3), ((x0 + x1) // 2, y0 - 9)], fill=GOLD)


def service_door(img):
    """Plain staff door to the service elevator, tucked between the palm and the urn."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 312, 66, 342, 137
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1], fill=hx("8a7a5a"))
    vgrad(img, (x0, y0, x1, y1), hx("c8b894"), hx("a89874"))
    d.rectangle([x0, y0, x1, y1], outline=hx("6a5a3a"))
    for py0, py1 in ((y0 + 5, y0 + 30), (y0 + 36, y1 - 6)):
        d.rectangle([x0 + 4, py0, x1 - 4, py1], outline=hx("8a7a5a"))
        d.line([(x0 + 5, py0 + 1), (x1 - 5, py0 + 1)], fill=hx("e0d4b4"))
    d.rectangle([x0 + 3, y0 + 14, x1 - 3, y0 + 21], fill=hx("2a2018"))
    text(img, ((x0 + x1) // 2, y0 + 18), "STAFF", GOLD, size=6)
    d.ellipse([x1 - 7, 102, x1 - 3, 106], fill=GOLD)
    shadow(img, "rect", [x0, y1 - 2, x1, y1], 0.4, 2)


def paint(include_desk=True):
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    plaque_and_cubbies(img)
    for x in (146, 300, 384):
        pilaster(img, x)
    elevator(img)
    sconce(img, 190, 74)
    sconce(img, 280, 74)
    service_door(img)
    wall_clock(img)
    mirror(img)
    for x in (146, 384):
        uplighter(img, x)
    palm(img, 172, 140)
    palm(img, 290, 140)
    urn(img)
    revolving_door(img)
    chandelier(img, 340)
    chandelier(img, 172)
    if include_desk:
        desk(img)
    light(img, "polygon", [(0, 0), (W, 0), (W, 60), (0, 60)], hx("fff8e0"), 0.1, 20)
    img = tall(img, ceiling)
    vignette(img, 0.4, tint=(40, 30, 40))
    return img


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("1e140c"), hx("3a2a1a"))
    # coffered ceiling with gold rosettes
    for x in range(-8, W, 40):
        d.rectangle([x + 3, 2, x + 36, TOP - 4], fill=hx("2a1e12"), outline=GOLD_D)
        d.rectangle([x + 6, 5, x + 33, TOP - 7], outline=hx("4a3620"))
        cx = x + 20
        sunburst(d, cx, 14, 6, 8, GOLD_D, hx("5a4220"), 0, 2 * math.pi)
        d.point((cx, 14), fill=GOLD)
    d.line([(0, TOP - 2), (W, TOP - 2)], fill=GOLD_D)
    for x in (340, 172):
        d.ellipse([x - 7, 0, x + 7, 6], fill=GOLD_D)
        d.line([(x, 0), (x, TOP)], fill=GOLD_D)
        light(img, "ellipse", [x - 60, -10, x + 60, 70], hx("fff0c0"), 0.3, 14)


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "lobby.png")
    mask = Image.new("L", (W, H + TOP), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([10, 98 + TOP, 146, 152 + TOP], fill=255)
    md.rectangle([86, 74 + TOP, 100, 98 + TOP], fill=255)
    md.rectangle([114, 90 + TOP, 128, 98 + TOP], fill=255)
    md.rectangle([36, 94 + TOP, 68, 98 + TOP], fill=255)
    save(cut(px, mask), "rooms", "lobby_fg.png")
    return px
