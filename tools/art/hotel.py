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


def window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 156, 28, 230, 100
    sky = Image.new("RGB", img.size)
    vgrad(sky, (x0, y0, x1, y1), hx("f3f0df"), hx("b9d3de"))
    img.paste(sky.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
    for bx, bw, bh, col in ((158, 14, 22, hx("89939b")), (174, 18, 32, hx("78818a")), (194, 12, 18, hx("97a0a5")),
                            (208, 20, 26, hx("6d767e"))):
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=col)
        for wy in range(y1 - bh + 3, y1 - 2, 4):
            d.line([(bx + 2, wy), (bx + bw - 2, wy)], fill=mul(col, 0.7))
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], outline=WOOD_D, width=4)
    d.rectangle([x0, y0, x1, y1], outline=hx("f7ecd4"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=WOOD_D, width=3)
    d.line([(x0, 60), (x1, 60)], fill=WOOD_D, width=2)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 7], fill=hx("8c6748"))
    # sheers and burgundy drapes, tied back
    d.polygon([(x0 - 2, y0 - 2), (x0 + 12, y0 + 8), (x0 + 14, y1 + 2), (x0 - 2, y1 + 4)], fill=hx("dcd0be"))
    d.polygon([(x1 + 2, y0 - 2), (x1 - 12, y0 + 8), (x1 - 14, y1 + 2), (x1 + 2, y1 + 4)], fill=hx("dcd0be"))
    d.polygon([(x0 - 16, y0 - 8), (x0 + 6, y0 - 4), (x0 + 2, y0 + 44), (x0 + 8, y1 + 30), (x0 - 16, y1 + 32)], fill=BURGUNDY)
    d.polygon([(x1 + 16, y0 - 8), (x1 - 6, y0 - 4), (x1 - 2, y0 + 44), (x1 - 8, y1 + 30), (x1 + 16, y1 + 32)], fill=BURGUNDY)
    for x in (x0 - 12, x0 - 6, x1 + 6, x1 + 12):
        d.line([(x, y0 - 4), (x, y1 + 28)], fill=mul(BURGUNDY, 0.72))
    d.rectangle([x0 - 20, y0 - 12, x1 + 20, y0 - 6], fill=GOLD_D)
    d.line([(x0 - 20, y0 - 12), (x1 + 20, y0 - 12)], fill=GOLD)
    for cx in (x0 - 4, x1 + 4):
        d.ellipse([cx - 4, y0 + 40, cx + 4, y0 + 48], fill=GOLD)
    light(img, "rect", [x0, y0, x1, y1], hx("fff7e2"), 0.22, 5)


def window_light(img):
    light(img, "polygon", [(166, 104), (222, 104), (300, H - 1), (150, H - 1)], hx("fff2cf"), 0.12, 12)
    light(img, "ellipse", [140, 140, 300, 230], hx("ffe5b0"), 0.08, 16)


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


def wardrobe(img):
    X0, X1, Z0, Z1 = 72, 124, 2, 26
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 2, a[1] - 3, b[0] + 10, a[1] + 3], 0.4, 3)
    R.box(img, X0, X1, 3, 104, Z0, Z1, mul(WOOD, 0.95), top=WOOD, side=hx("4c2f1a"))
    R.box(img, X0 - 2, X1 + 2, 104, 112, Z0, Z1 + 2, WOOD, top=hx("8a5e3c"), side=hx("4c2f1a"))
    R.box(img, X0 + 1, X1 - 1, 0, 3, Z0, Z1 - 1, WOOD_D)
    xm = (X0 + X1) / 2
    for (c, e) in ((X0 + 3, xm - 1), (xm + 1, X1 - 3)):
        R.quad(img, [(c, 30, Z1), (e, 30, Z1), (e, 98, Z1), (c, 98, Z1)], hx("75492b"), hx("3e2615"))
        R.quad(img, [(c + 4, 36, Z1), (e - 4, 36, Z1), (e - 4, 92, Z1), (c + 4, 92, Z1)], None, hx("8e6040"))
    for y in (8, 18):
        R.quad(img, [(X0 + 3, y, Z1), (X1 - 3, y, Z1), (X1 - 3, y + 8, Z1), (X0 + 3, y + 8, Z1)], None, hx("3e2615"))
        R.line(img, (xm - 4, y + 4, Z1), (xm + 4, y + 4, Z1), GOLD)
    for x in (xm - 3, xm + 3):
        R.line(img, (x, 60, Z1), (x, 68, Z1), GOLD, 2)
    R.line(img, (xm, 30, Z1), (xm, 98, Z1), WOOD_D)
    noise(img, (int(a[0]), 30, int(b[0]), int(a[1])), 3, 141)


def desk(img):
    X0, X1, Z0, Z1 = 154, 232, 2, 26
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0], a[1] - 4, b[0] + 6, a[1] + 3], 0.35, 3)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z0 + 2), (x, 24, Z0 + 2), WOOD_D, 2)
    R.box(img, X0, X1, 20, 26, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.box(img, X0 - 1, X1 + 1, 26, 28, Z0, Z1 + 1, hx("7d5232"), top=hx("8e6040"), side=WOOD_D)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z1 - 2), (x, 20, Z1 - 2), WOOD_D, 2)
    for c in (X0 + 6, X1 - 30):
        R.quad(img, [(c, 21, Z1), (c + 24, 21, Z1), (c + 24, 25, Z1), (c, 25, Z1)], None, WOOD_D)
        R.line(img, (c + 10, 23, Z1), (c + 14, 23, Z1), GOLD)
    # stationery, inkwell and the black bakelite telephone
    R.quad(img, [(X0 + 22, 28.1, 8), (X0 + 46, 28.1, 6), (X0 + 48, 28.1, 18), (X0 + 24, 28.1, 20)], hx("ece0c6"))
    R.line(img, (X0 + 28, 28.2, 10), (X0 + 42, 28.2, 9), hx("8c7d69"))
    R.line(img, (X0 + 28, 28.2, 14), (X0 + 42, 28.2, 13), hx("8c7d69"))
    R.box(img, X0 + 8, X0 + 14, 28, 32, 10, 16, hx("2e3a3a"), top=hx("4a5656"))
    R.line(img, (X0 + 12, 32, 13), (X0 + 15, 40, 12), hx("e8dcc0"))
    R.box(img, X1 - 18, X1 - 6, 28, 32, 8, 20, hx("1a1614"), top=hx("2e2824"), side=hx("0e0c0a"))
    R.box(img, X1 - 19, X1 - 5, 33, 35, 12, 16, hx("1a1614"), top=hx("3a3430"), side=hx("0e0c0a"))
    R.line(img, (X1 - 19, 32, 14), (X1 - 19, 34, 14), hx("1a1614"), 2)
    R.line(img, (X1 - 5, 32, 14), (X1 - 5, 34, 14), hx("1a1614"), 2)
    px, py = R.P(X1 - 12, 32.2, 20)
    ImageDraw.Draw(img).ellipse([px - 2, py - 1, px + 2, py + 1], fill=hx("d8d0c0"))
    # a lamp at the left end
    R.box(img, X0 + 30, X0 + 36, 28, 30, 6, 12, GOLD_D, top=GOLD)
    R.line(img, (X0 + 33, 30, 9), (X0 + 33, 44, 9), GOLD_D)
    R.quad(img, [(X0 + 27, 44, 12), (X0 + 39, 44, 12), (X0 + 36, 52, 12), (X0 + 30, 52, 12)], hx("efe2c4"), GOLD_D)
    lx, ly = R.P(X0 + 33, 48, 12)
    light(img, "ellipse", [lx - 26, ly - 18, lx + 26, ly + 24], hx("fff2cc"), 0.16, 8)
    # the desk chair, pushed in
    C0, C1, Cz0, Cz1 = 182, 204, 22, 36
    for x in (C0 + 1, C1 - 1):
        R.line(img, (x, 0, Cz0 + 1), (x, 18, Cz0 + 1), WOOD_D, 2)
    R.box(img, C0, C1, 16, 19, Cz0, Cz1, mul(WOOD, 0.85), top=BURGUNDY_L, side=WOOD_D)
    for x in (C0 + 1, C1 - 1):
        R.line(img, (x, 0, Cz1 - 1), (x, 40, Cz1 - 1), WOOD_D, 2)
    R.quad(img, [(C0 + 2, 26, Cz1 - 1), (C1 - 2, 26, Cz1 - 1), (C1 - 2, 38, Cz1 - 1), (C0 + 2, 38, Cz1 - 1)], BURGUNDY, WOOD_D)
    R.line(img, (C0, 40, Cz1 - 1), (C1, 40, Cz1 - 1), WOOD, 2)


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


def nightstand(img):
    X0, X1, Z0, Z1 = 388, 410, 3, 24
    R.box(img, X0, X1, 0, 28, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.quad(img, [(X0 + 2, 16, Z1), (X1 - 2, 16, Z1), (X1 - 2, 25, Z1), (X0 + 2, 25, Z1)], None, WOOD_D)
    R.line(img, (X0 + 9, 21, Z1), (X0 + 13, 21, Z1), GOLD)
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


def paint(unmade=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    door(img)
    window(img)
    sconces(img)
    wardrobe(img)
    desk(img)
    bed(img, unmade)
    nightstand(img)
    vanity(img)
    window_light(img)
    chandelier(img)
    img = tall(img, ceiling)
    vignette(img, 0.26, tint=(84, 62, 36), blur=34)
    return img


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


def build():
    made = paint(False)
    unmade = paint(True)
    pal = palette_of(Image.blend(made, unmade, 0.5), 128)
    made_px = pixelize(made, pal)
    unmade_px = pixelize(unmade, pal)
    save(made_px, "rooms", "hotel_room_made.png")
    save(unmade_px, "rooms", "hotel_room_unmade.png")
    return made_px
