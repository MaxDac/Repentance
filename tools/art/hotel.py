"""The Aurelian: a luxurious hotel room in warm daytime light."""
import math
import random
from PIL import Image, ImageDraw
from .common import (W, H, TOP, tall, hx, mul, mix, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     save)
from .furniture import Room3D

FLOOR = 146
CREAM = hx("eadfc8")
CREAM_D = hx("bba889")
GOLD = hx("d2af62")
GOLD_D = hx("7b5c26")
WOOD = hx("6b4428")
WOOD_D = hx("3a2414")
GREEN = hx("31533f")
GREEN_L = hx("55735d")
BURGUNDY = hx("6b2430")
BURGUNDY_L = hx("8e4150")
R = Room3D(FLOOR, 248, -220)
CHANDELIER_X = 284  # the ceiling rose and the chandelier under it, clear of the painting


def shell(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("f0e6d2"), CREAM_D)
    noise(img, (0, 0, W - 1, FLOOR), 3, 101)
    d.rectangle([0, 0, W - 1, 10], fill=hx("cab28a"))
    d.line([(0, 10), (W, 10)], fill=GOLD_D)
    d.rectangle([0, 16, W - 1, 18], fill=GOLD)
    for x in range(0, W, 40):
        d.rectangle([x + 6, 24, x + 34, 108], outline=hx("d8c8aa"))
        d.line([(x + 7, 25), (x + 33, 25)], fill=hx("faf0dc"))
    vgrad(img, (0, 108, W - 1, FLOOR), hx("b79d7f"), hx("876b52"))
    d.rectangle([0, 106, W - 1, 108], fill=GOLD_D)
    for x in range(0, W, 48):
        d.rectangle([x + 5, 114, x + 42, FLOOR - 7], outline=hx("6f573f"))
        d.line([(x + 6, 115), (x + 41, 115)], fill=hx("c8ae8c"))
    d.rectangle([0, FLOOR - 5, W - 1, FLOOR], fill=WOOD_D)
    # a gilt-framed landscape above the bed
    x0, y0, x1, y1 = 296, 30, 352, 62
    d.rectangle([x0, y0, x1, y1], fill=GOLD_D)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], fill=GOLD)
    d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], fill=hx("a69374"))
    d.polygon([(x0 + 5, y1 - 6), (x0 + 18, y0 + 13), (x0 + 30, y0 + 20), (x1 - 6, y0 + 8), (x1 - 5, y1 - 5)], fill=hx("617367"))
    d.rectangle([x0 + 5, y1 - 10, x1 - 5, y1 - 5], fill=hx("6f5441"))
    shadow(img, "rect", [x0 + 2, y1, x1 + 3, y1 + 3], 0.2, 2)


OAK = [hx("8a5a34"), hx("7a4e2c"), hx("946640"), hx("6e4426"), hx("845532")]
SEAM = hx("2e1a0e")
N, PW = 4, 6.0             # herringbone: planks four widths long, PW room units wide
_REF = [(i, 0, 0, i) for i in range(N)] + [(0, j, 1, j - 1) for j in range(1, N + 1)]


def _brick(i, j):
    """Which plank of the herringbone holds cell (i, j): (vertical?, lattice a, lattice b, cell along the plank)."""
    for rx, ry, v, k in _REF:
        dx, dy = i - rx, j - ry
        s, t = dx + dy, dx - dy
        if s % 2 == 0 and t % (2 * N) == 0:
            return v, s // 2, t // (2 * N), k
    raise ValueError


def _room_xz(px, py):
    s = (py + 0.5 - R.vy) / (R.floor - R.vy)
    return R.vx + (px + 0.5 - R.vx) / s, R.d0 * (1 - 1 / s)


RUG = (90, 410, 80, 190)
# madder field, indigo medallion and border, ivory and saffron outlines
MADDER, MADDER_D, INDIGO, INDIGO_L, IVORY, SAFFRON, RUG_GREEN = (hx("8a2a26"), hx("6a1c1c"), hx("1f2a4a"),
                                                                  hx("34466e"), hx("e6d8b4"), hx("c89a3c"), hx("3f6a4e"))


def _rug_colour(x, z):
    x0, x1, z0, z1 = RUG
    e = min(x - x0, x1 - x, z - z0, z1 - z)        # depth into the rug from its nearest edge
    if e < 2:
        return IVORY if e > 1 else SAFFRON
    if e < 4:
        return MADDER_D
    if e < 14:                                        # main border: indigo with a running vine of rosettes
        along = (x - x0) if min(z - z0, z1 - z) <= min(x - x0, x1 - x) else (z - z0)
        mid = abs(e - 9)
        if mid > 4:
            return SAFFRON
        ph = along % 16
        r = math.hypot(ph - 8, (e - 9) * 1.6)
        if r < 2.2:
            return IVORY if r < 1 else MADDER
        if r < 4 and int(ph) % 2 == 0:
            return SAFFRON
        wave = 9 + 2.6 * math.sin(along / 16 * 2 * math.pi + math.pi / 2)
        if abs(e - wave) < 0.8:
            return RUG_GREEN
        return INDIGO
    if e < 16:
        return IVORY
    # field: a medallion in the middle, spandrels in the corners
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    fx, fz = (x - cx) / 84, (z - cz) / 38
    m = abs(fx) + abs(fz) * 1.0 + 0.25 * math.cos(math.atan2(fz, fx) * 8) * math.hypot(fx, fz)
    if m < 0.18:
        return SAFFRON if m < 0.09 else MADDER
    if m < 0.75:
        if abs(m - 0.42) < 0.03:
            return IVORY
        return INDIGO_L if m < 0.42 else INDIGO
    if m < 0.8:
        return IVORY
    # corners: indigo spandrels with an ivory edge
    for sx, sz in ((x0 + 16, z0 + 16), (x1 - 16, z0 + 16), (x0 + 16, z1 - 16), (x1 - 16, z1 - 16)):
        c = abs(x - sx) / 46 + abs(z - sz) / 26
        if c < 1:
            return IVORY if c > 0.92 else INDIGO
    # field: a herati lattice - diamonds of fine dark lines with a rosette at every other crossing
    lx, lz = (x - x0) % 20 - 10, (z - z0) % 14 - 7
    row = int((z - z0) // 14) + int((x - x0) // 20)
    if abs(abs(lx) / 10 + abs(lz) / 7 - 1) < 0.08:
        return MADDER_D
    if row % 2 == 0 and abs(lx) / 2.6 + abs(lz) / 1.8 < 1:
        return SAFFRON if abs(lx) / 2.6 + abs(lz) / 1.8 > 0.45 else IVORY
    if row % 2 == 1 and abs(lx) < 0.8 and abs(lz) < 1.6:
        return RUG_GREEN
    return MADDER


def floor(img):
    """Herringbone oak parquet with a walnut border along the skirting, under a Persian rug with fringed ends. Painted per
    pixel by projecting each floor pixel back into the room."""
    px = img.load()
    rnd = random.Random(146)
    tone = {}
    x0, x1, z0, z1 = RUG
    for py in range(FLOOR, H):
        for pxx in range(W):
            x, z = _room_xz(pxx, py)
            if x0 <= x <= x1 and z0 <= z <= z1:
                c = _rug_colour(x, z)
                # worn pile: a little speckle
                n = rnd.uniform(-0.06, 0.06)
                px[pxx, py] = mul(c, 1 + n)
                continue
            if z < 7:                                 # a walnut border band along the skirting, a maple string
                c = hx("4a2c18") if z < 5.5 else hx("b08a58")
                px[pxx, py] = mul(c, 1 + rnd.uniform(-0.05, 0.05))
                continue
            u, v = (x + z) / (PW * math.sqrt(2)), (x - z) / (PW * math.sqrt(2))
            i, j = math.floor(u), math.floor(v)
            vert, a, b, k = _brick(i, j)
            key = (vert, a, b)
            if key not in tone:
                tone[key] = (OAK[rnd.randrange(len(OAK))], rnd.uniform(0, 100))
            base, seed = tone[key]
            fu, fv = u - i, v - j
            across = fu if vert else fv
            along = (k + (fv if vert else fu)) / N
            # grain: fine streaks along the plank, darker toward one end
            g = 0.06 * math.sin(across * 9 + seed) + 0.04 * math.sin(across * 23 + seed * 2) - 0.05 * along
            c = mul(base, 1 + g)
            # seams on the plank sides and ends
            edge = across < 0.16 or (k == 0 and (fv if vert else fu) < 0.06)
            px[pxx, py] = mix(c, SEAM, 0.75) if edge else c
    # fringe on the two short ends of the rug, knotted tassels on the floor
    d = ImageDraw.Draw(img)
    for xe, dirn in ((x0, -1), (x1, 1)):
        for zz in range(z0 + 1, z1, 2):
            a = R.P(xe, 0, zz)
            b = R.P(xe + dirn * 5, 0, zz + 0.6)
            d.line([a, b], fill=IVORY if zz % 4 else mul(IVORY, 0.8))
    # a soft wear patch in the pile and a polished sheen on the boards in front of the window
    shadow(img, "polygon", [R.P(x0, 0, z0), R.P(x1, 0, z0), R.P(x1, 0, z0 + 6), R.P(x0, 0, z0 + 6)], 0.2, 2)
    light(img, "polygon", [R.P(150, 0, 4), R.P(230, 0, 4), R.P(250, 0, 80), R.P(130, 0, 80)], hx("f0d8b0"), 0.1, 6)


def door(img):
    d = ImageDraw.Draw(img)
    x0, x1, top = 14, 58, FLOOR - 96
    d.rectangle([x0 - 6, top - 8, x1 + 6, FLOOR], fill=WOOD_D)
    d.rectangle([x0 - 8, top - 10, x1 + 8, top - 6], fill=GOLD_D)
    d.rectangle([x0 - 3, top - 3, x1 + 3, FLOOR], fill=hx("6b4428"))
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("80553a"), hx("5a3822"))
    for (a, b) in ((top + 6, top + 40), (top + 48, FLOOR - 8)):
        for (c, e) in ((x0 + 5, (x0 + x1) // 2 - 2), ((x0 + x1) // 2 + 2, x1 - 5)):
            d.rectangle([c, a, e, b], outline=hx("3e2615"))
            d.line([(c + 1, a + 1), (e - 1, a + 1)], fill=hx("9a6e4c"))
    d.rectangle([x1 - 8, top + 42, x1 - 5, top + 52], fill=GOLD_D)
    d.ellipse([x1 - 10, top + 45, x1 - 4, top + 50], fill=GOLD)
    noise(img, (x0, top, x1, FLOOR), 3, 131)
    shadow(img, "rect", [x0 - 2, FLOOR - 2, x1 + 8, FLOOR + 5], 0.35, 3)


def sconces(img):
    d = ImageDraw.Draw(img)
    for cx in (136, 254):
        d.rectangle([cx - 3, 52, cx + 3, 66], fill=GOLD_D)
        d.line([(cx, 66), (cx, 70)], fill=GOLD)
        d.polygon([(cx - 7, 54), (cx + 7, 54), (cx + 5, 44), (cx - 5, 44)], fill=hx("efe2c4"), outline=GOLD_D)
        light(img, "ellipse", [cx - 20, 30, cx + 20, 76], hx("fff4db"), 0.16, 6)


def bed(img, unmade=False):
    """A double bed with its burgundy upholstered headboard against the right, lengthways along the back wall."""
    X0, X1, Z0, Z1 = 264, 380, 4, 62
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 4, a[1] - 6, b[0] + 6, a[1] + 4], 0.45, 4)
    # headboard: a tall tufted panel, seen from its padded face
    R.box(img, X1 - 4, X1, 0, 56, Z0, Z1, WOOD_D, top=GOLD_D, side=BURGUNDY)
    R.quad(img, [(X1 - 4, 22, Z0 + 3), (X1 - 4, 22, Z1 - 3), (X1 - 4, 52, Z1 - 3), (X1 - 4, 52, Z0 + 3)], BURGUNDY_L, mul(BURGUNDY, 0.6))
    for y in (30, 38, 46):
        for z in range(Z0 + 8, Z1 - 4, 9):
            px, py = R.P(X1 - 4, y, z + (4 if y == 38 else 0))
            img.putpixel((int(px), int(py)), mul(BURGUNDY, 0.55))
    # frame rail and mattress
    R.box(img, X0, X1 - 4, 6, 16, Z0, Z1, WOOD, top=hx("8a5e3c"), side=WOOD_D)
    R.box(img, X0 + 1, X1 - 5, 16, 26, Z0 + 1, Z1 - 1, hx("e8dcc6"), top=hx("f4ecdc"), side=hx("c4b49a"))
    if not unmade:
        R.box(img, X0, X1 - 30, 12, 27, Z0, Z1 + 1, GREEN, top=GREEN_L, side=mul(GREEN, 0.75))
        R.box(img, X1 - 30, X1 - 24, 25, 27.6, Z0, Z1 + 1, hx("f4ecdc"), top=hx("faf5ea"), side=hx("cfc2aa"))
        R.line(img, (X0, 14, Z1 + 1), (X1 - 30, 14, Z1 + 1), GOLD)
        for x in range(X0 + 14, X1 - 32, 16):
            R.line(img, (x, 27, Z1 + 1), (x - 1, 13, Z1 + 1), mul(GREEN, 0.8))
        for (z0, z1) in ((Z0 + 4, Z0 + 26), (Z0 + 30, Z1 - 4)):
            R.box(img, X1 - 22, X1 - 6, 26, 33, z0, z1, hx("f6efdf"), top=hx("fdf8ee"), side=hx("c8baa3"))
        R.box(img, X1 - 26, X1 - 20, 26, 30, Z0 + 18, Z0 + 38, BURGUNDY_L, top=hx("a8586a"), side=BURGUNDY)
    else:
        R.box(img, X0, X0 + 30, 14, 31, Z0 + 2, Z1 + 1, GREEN, top=GREEN_L, side=mul(GREEN, 0.75))
        R.quad(img, [(X0 + 30, 26.2, Z0 + 6), (X0 + 52, 26.2, Z0 + 12), (X0 + 44, 26.2, Z1 - 6), (X0 + 30, 26.2, Z1)], GREEN_L)
        R.quad(img, [(X0 + 44, 26, Z1 - 2), (X0 + 70, 26, Z1 - 1), (X0 + 74, 8, Z1 + 2), (X0 + 40, 10, Z1 + 2)], hx("f4ecdc"))
        R.line(img, (X0 + 56, 24, Z1), (X0 + 58, 10, Z1 + 2), hx("c4b49a"))
        for (p, q) in (((X0 + 60, 26.1, Z0 + 10), (X0 + 84, 26.1, Z1 - 10)), ((X0 + 78, 26.1, Z0 + 6), (X1 - 30, 26.1, Z0 + 26)),
                       ((X0 + 86, 26.1, Z1 - 8), (X1 - 26, 26.1, Z1 - 16))):
            R.line(img, p, q, hx("cbbca4"))
        R.box(img, X1 - 24, X1 - 8, 26, 32, Z0 + 6, Z0 + 28, hx("f3ead8"), top=hx("faf5ea"), side=hx("c0b096"))
        R.box(img, X1 - 40, X1 - 22, 26, 31, Z0 + 32, Z1 - 6, hx("f3ead8"), top=hx("faf5ea"), side=hx("c0b096"))
    # footboard and posts in front
    R.box(img, X0 - 4, X0, 0, 32, Z0, Z1 + 1, WOOD, top=hx("8a5e3c"), side=hx("5a3822"))
    R.quad(img, [(X0 - 4, 10, Z0 + 5), (X0 - 4, 10, Z1 - 4), (X0 - 4, 27, Z1 - 4), (X0 - 4, 27, Z0 + 5)], None, WOOD_D)
    for (x, top) in ((X0 - 2, 36), (X1 - 2, 60)):
        R.line(img, (x, 0, Z1 + 1), (x, top, Z1 + 1), WOOD_D, 3)
        px, py = R.P(x, top + 1, Z1 + 1)
        ImageDraw.Draw(img).ellipse([px - 2, py - 2, px + 2, py + 2], fill=GOLD)
    light(img, "polygon", [R.P(X0, 27, Z0), R.P(X1 - 30, 27, Z0), R.P(X1 - 30, 27, Z1), R.P(X0, 27, Z1)], hx("fff4df"), 0.08, 6)


def nightstand(img, lamp=True):
    X0, X1, Z0, Z1 = 388, 410, 3, 24
    R.box(img, X0, X1, 0, 28, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.quad(img, [(X0 + 2, 16, Z1), (X1 - 2, 16, Z1), (X1 - 2, 25, Z1), (X0 + 2, 25, Z1)], None, WOOD_D)
    R.line(img, (X0 + 9, 21, Z1), (X0 + 13, 21, Z1), GOLD)
    if not lamp:
        return
    R.box(img, X0 + 8, X0 + 14, 28, 30, 10, 16, GOLD_D, top=GOLD)
    R.line(img, (X0 + 11, 30, 13), (X0 + 11, 40, 13), GOLD_D)
    R.quad(img, [(X0 + 5, 40, 16), (X0 + 17, 40, 16), (X0 + 14, 48, 16), (X0 + 8, 48, 16)], hx("efe2c4"), GOLD_D)
    lx, ly = R.P(X0 + 11, 44, 16)
    light(img, "ellipse", [lx - 24, ly - 18, lx + 24, ly + 22], hx("fff2cc"), 0.16, 8)


def vanity(img):
    X0, X1, Z0, Z1 = 418, 470, 2, 22
    d = ImageDraw.Draw(img)
    # oval gilt mirror on the wall
    d.ellipse([426, 44, 462, 94], fill=GOLD_D)
    d.ellipse([428, 46, 460, 92], fill=GOLD)
    d.ellipse([431, 49, 457, 89], fill=hx("b4c3c8"))
    d.line([(438, 58), (446, 76)], fill=hx("dfe8ea"))
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
    R.box(img, X1 - 18, X1 - 8, 30, 31.5, 8, 16, hx("e6d8c0"), top=hx("f2e8d6"))
    # upholstered stool
    S0, S1, Sz0, Sz1 = 432, 452, 30, 42
    for x in (S0 + 2, S1 - 2):
        for z in (Sz0 + 2, Sz1 - 2):
            R.line(img, (x, 0, z), (x, 13, z), WOOD_D, 2)
    R.box(img, S0, S1, 13, 17, Sz0, Sz1, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("c8af87"), hx("eadcc2"))
    for x in range(0, W, 40):
        d.rectangle([x + 4, 4, x + 36, TOP - 5], outline=hx("e8d7b8"))
    d.line([(0, TOP - 3), (W, TOP - 3)], fill=GOLD_D)
    d.line([(0, TOP - 1), (W, TOP - 1)], fill=WOOD_D)
    noise(img, (0, 0, W - 1, TOP), 2, 121)
    # a moulded ceiling rose: a ring of leaves round a gilt boss
    d.ellipse([CHANDELIER_X - 15, TOP - 10, CHANDELIER_X + 15, TOP + 1], fill=hx("d9c6a2"), outline=hx("b8a07a"))
    for k in range(14):
        a = k / 14 * 2 * math.pi
        ex, ey = CHANDELIER_X + 11.5 * math.cos(a), TOP - 5 + 3.4 * math.sin(a)
        d.ellipse([ex - 2, ey - 1, ex + 1, ey + 1], fill=hx("f0e4c8") if math.sin(a + 0.6) < 0 else hx("a88e66"))
    d.ellipse([CHANDELIER_X - 6, TOP - 8, CHANDELIER_X + 6, TOP - 2], fill=GOLD_D)
    d.ellipse([CHANDELIER_X - 5, TOP - 8, CHANDELIER_X + 4, TOP - 3], fill=GOLD)
    d.point([(CHANDELIER_X - 3, TOP - 7), (CHANDELIER_X - 2, TOP - 7)], fill=hx("f4dc96"))
