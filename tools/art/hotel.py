"""The Aurelian: a luxurious hotel room in warm daytime light."""
from PIL import Image, ImageDraw
from .common import (W, H, TOP, tall, hx, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     save, floor_boards)
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


def floor(img):
    floor_boards(img, FLOOR, H - 1, (248, -220), 22, hx("7a5132"), hx("5d3922"), hx("342012"), 111)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 112)
    R.quad(img, [(90, 0, 80), (410, 0, 80), (410, 0, 190), (90, 0, 190)], GREEN)
    R.quad(img, [(98, 0, 86), (402, 0, 86), (402, 0, 184), (98, 0, 184)], None, GOLD)
    R.quad(img, [(108, 0, 94), (392, 0, 94), (392, 0, 176), (108, 0, 176)], None, GREEN_L)
    for x in range(118, 392, 16):
        R.line(img, (x, 0, 94), (x, 0, 176), mul(GREEN_L, 0.85))
    noise(img, (60, 160, 440, H - 1), 4, 113)


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


def chandelier(img):
    d = ImageDraw.Draw(img)
    cx = 300
    d.line([(cx, 0), (cx, 8)], fill=GOLD_D)
    d.ellipse([cx - 5, 6, cx + 5, 12], fill=GOLD)
    d.polygon([(cx - 20, 12), (cx + 20, 12), (cx + 14, 20), (cx - 14, 20)], fill=GOLD, outline=GOLD_D)
    for ax in (-18, -6, 6, 18):
        d.line([(cx, 14), (cx + ax, 22)], fill=GOLD_D)
        d.ellipse([cx + ax - 2, 21, cx + ax + 2, 26], fill=hx("f8f1d8"))
    for ax in range(-12, 13, 6):
        d.line([(cx + ax, 20), (cx + ax, 26 + abs(ax) // 6)], fill=hx("e8e2d0"))
    light(img, "ellipse", [cx - 60, -20, cx + 60, 60], hx("fff4d8"), 0.14, 16)


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
    d.ellipse([288, TOP - 8, 312, TOP], fill=GOLD_D)
    d.ellipse([292, TOP - 6, 308, TOP], fill=GOLD)
    noise(img, (0, 0, W - 1, TOP), 2, 121)


