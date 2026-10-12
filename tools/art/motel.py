"""A cheap roadside motel room in flat, dingy daytime light."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of, save,
                     floor_boards, text)
from .furniture import Room3D

FLOOR = 136
WOOD = hx("6a5038")
WOOD_D = hx("342418")
R = Room3D(FLOOR, 250, -250)

def wall_mirror(img, box):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline=hx("9a7850"), width=2)
    vgrad(img, box, hx("657078"), hx("3c444a"))
    d.rectangle(box, outline=hx("b0aaa0"))
    d.line([(x0 + 4, y0 + 4), (x0 + 12, y0 + 12)], fill=hx("a4b0b4"))
    d.line([(x0 + 4, y0 + 9), (x0 + 8, y0 + 13)], fill=hx("829298"))
    d.line([(x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], fill=hx("50504a"))


def shell(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("9a9572"), hx("70694f"))
    for x in range(0, W, 10):
        d.line([(x, 0), (x, FLOOR)], fill=hx("7f7a5c"))
        d.line([(x + 4, 0), (x + 4, FLOOR)], fill=hx("9d9876"))
    for y in range(18, FLOOR - 18, 24):
        for x in range(8 + ((y // 24) % 2) * 8, W, 32):
            d.polygon([(x, y), (x + 8, y + 5), (x, y + 10), (x - 8, y + 5)], outline=hx("918b67"))
    noise(img, (0, 0, W - 1, FLOOR), 5, 401)
    vgrad(img, (0, 100, W - 1, FLOOR), hx("5a4634"), hx("34261c"))
    d.rectangle([0, 98, W - 1, 100], fill=hx("7a6246"))
    d.rectangle([0, FLOOR - 4, W - 1, FLOOR], fill=hx("23170f"))
    for x in range(0, W, 34):
        d.rectangle([x + 3, 104, x + 28, FLOOR - 8], outline=hx("443022"))
        d.line([(x + 4, 105), (x + 27, 105)], fill=hx("6e5740"))

    wall_mirror(img, (126, 16, 160, 47))
    wall_mirror(img, (210, 53, 254, 86))
    for x, y in ((184, 24), (278, 65), (92, 80)):
        d.line([(x, y), (x + 3, y + 5), (x + 1, y + 9)], fill=hx("a79d79"))

    # Water stains and cracks
    for box in ([118, 2, 182, 42], [300, 0, 352, 34], [392, 64, 454, 110]):
        shadow(img, "ellipse", box, 0.26, 9, hx("7c6b4a"))
    d.line([(354, 12), (350, 28), (358, 43), (348, 58), (355, 74), (347, 92)], fill=hx("2a241c"))
    d.line([(102, 16), (110, 28), (104, 42), (114, 58)], fill=hx("3a3428"))
    d.line([(355, 75), (362, 84), (360, 96), (369, 108)], fill=hx("2a241c"))
    shadow(img, "ellipse", [24, 112, 120, 132], 0.28, 6)


def floor(img):
    floor_boards(img, FLOOR, H - 1, (250, -250), 20, hx("6a5138"), hx("503b28"), hx("2a1a12"), 405)
    noise(img, (0, FLOOR, W - 1, H - 1), 6, 406)
    # threadbare rug lying flat in the middle of the room
    R.quad(img, [(150, 0, 60), (350, 0, 60), (350, 0, 150), (150, 0, 150)], hx("666046"))
    R.quad(img, [(158, 0, 66), (342, 0, 66), (342, 0, 144), (158, 0, 144)], None, hx("968460"))
    for z in range(72, 144, 8):
        R.line(img, (154, 0, z), (346, 0, z), hx("575139"))
    a, b = R.P(150, 0, 60), R.P(350, 0, 150)
    noise(img, (int(a[0]) - 30, int(a[1]), int(b[0]) + 10, int(b[1])), 7, 407)


def door(img):
    """Room 6's door, on the back wall at the far left; it leads back out to the street."""
    d = ImageDraw.Draw(img)
    x0, x1, top = 8, 44, FLOOR - 88
    d.rectangle([x0 - 4, top - 4, x1 + 4, FLOOR], fill=WOOD_D)
    d.rectangle([x0 - 2, top - 2, x1 + 2, FLOOR], fill=hx("57412d"))
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("6e5440"), hx("4e3a2a"))
    for (a, b) in ((top + 6, top + 38), (top + 46, FLOOR - 8)):
        d.rectangle([x0 + 5, a, x1 - 5, b], outline=hx("3a2a1c"))
        d.line([(x0 + 6, a + 1), (x1 - 6, a + 1)], fill=hx("7c6049"))
    d.ellipse([x1 - 9, top + 44, x1 - 5, top + 48], fill=hx("b89a58"))
    d.rectangle([x0 + 14, top + 14, x0 + 22, top + 22], fill=hx("a88a4c"))
    d.text((x0 + 16, top + 13), "6", fill=hx("2a1a10"))
    noise(img, (x0, top, x1, FLOOR), 4, 412)
    shadow(img, "rect", [x0 - 2, FLOOR - 2, x1 + 8, FLOOR + 6], 0.4, 3)


IRON, IRON_L, BRASS = hx("2a2422"), hx("4a403a"), hx("a49470")


CURTAINS = (
    ([(292, 22), (315, 22), (315, 98), (292, 98)], hx("c0b490")),
    ([(383, 22), (406, 22), (406, 98), (383, 98)], hx("b8ac88")),
)


def curtains(img, night=False):
    d = ImageDraw.Draw(img)
    d.line([(288, 19), (410, 19)], fill=hx("34261e"), width=2)
    for pts, col in CURTAINS:
        if night:
            col = mix(col, hx("584052"), 0.52)
        shade, highlight = mul(col, 0.68), mix(col, hx("eedac0"), 0.15)
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        d.rectangle([x0 + 2, 24, x1 + 2, 101], fill=hx("251a1c"))
        d.polygon(pts, fill=col)
        for x in range(x0 + 2, x1 - 1, 6):
            d.ellipse([x - 1, 17, x + 2, 23], outline=hx("7a6250"))
            d.line([(x, 25), (x + 1, 98)], fill=shade, width=2)
            d.line([(x + 2, 25), (x + 3, 97)], fill=highlight, width=2)
            d.ellipse([x, 96, x + 5, 100], fill=col)
            d.arc([x, 96, x + 5, 100], 0, 180, fill=shade)
        d.line([(x0 + 1, 24), (x1 - 1, 24)], fill=highlight)
        d.line([(x0, 26), (x0, 96)], fill=shade)


def window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 302, 26, 396, 92
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 7], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 4], fill=WOOD)
    vgrad(img, (x0, y0, x1, y1), hx("dcd8b8"), hx("aeb89e"))
    d.rectangle([x0, 70, x1, y1], fill=hx("7b7554"))
    d.rectangle([x0, 62, x1, 70], fill=hx("938a63"))
    d.rectangle([320, 50, 332, 92], fill=hx("5f5a46"))
    d.rectangle([346, 44, 356, 92], fill=hx("655f49"))
    d.rectangle([372, 54, 382, 92], fill=hx("595542"))
    light(img, "rect", [x0, y0, x1, y1], hx("f5efc6"), 0.18, 2)
    d.rectangle([x0, y0, x1, y1], outline=hx("20140e"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("2a1a12"), width=2)
    d.line([(x0, 58), (x1, 58)], fill=hx("2a1a12"), width=2)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 8], fill=hx("4e3a2a"))

    curtains(img)
    shadow(img, "rect", [296, 26, 402, 90], 0.08, 2, hx("d8d0b0"))

    # Sickly daylight spill
    light(img, "polygon", [(322, 92), (376, 92), (454, 224), (254, 224)], hx("e8dfaa"), 0.22, 10)
    light(img, "ellipse", [286, 90, 438, 190], hx("d8d28e"), 0.14, 18)


def bed(img, unmade=False):
    """A narrow iron bed pushed lengthways against the back wall: knee-high mattress, head end on the right."""
    X0, X1, Z0, Z1 = 52, 140, 4, 42
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z0)
    shadow(img, "rect", [a[0] - 2, b[1] - 2, b[0] + 6, a[1] + 3], 0.45, 3)
    # back posts and end panels (behind the mattress)
    for x, top in ((X0, 30), (X1, 46)):
        R.line(img, (x, 0, Z0), (x, top, Z0), IRON, 2)
    # mattress on a sagging spring frame
    R.box(img, X0 + 2, X1 - 2, 12, 15, Z0 + 2, Z1 - 2, IRON_L)
    sheet, sheet_d = hx("cfc6ad"), hx("a59c84")
    R.box(img, X0 + 2, X1 - 2, 15, 24, Z0 + 2, Z1 - 2, sheet, top=hx("ddd4bc"), side=sheet_d)
    blanket, blanket_l = hx("6f7558"), hx("8c9270")
    if not unmade:
        R.box(img, X0 + 1, X1 - 22, 12, 24.6, Z0 + 1, Z1 - 1, blanket, top=blanket_l, side=hx("565b44"))
        R.line(img, (X1 - 22, 24.6, Z0 + 1), (X1 - 22, 24.6, Z1 - 1), hx("e6dfca"))  # turned-down sheet
        R.box(img, X1 - 18, X1 - 5, 24, 28, Z0 + 7, Z1 - 7, hx("e2dac4"), top=hx("eee7d4"), side=hx("b8af98"))
        for x in range(X0 + 12, X1 - 24, 14):
            R.line(img, (x, 24.6, Z1 - 1), (x - 1, 12, Z1 - 1), hx("5f644b"))
    else:
        R.box(img, X0 + 1, X0 + 26, 12, 29, Z0 + 3, Z1 - 1, blanket, top=blanket_l, side=hx("565b44"))
        R.quad(img, [(X0 + 26, 24.2, Z0 + 8), (X0 + 46, 24.2, Z0 + 14), (X0 + 40, 24.2, Z1 - 4), (X0 + 26, 24.2, Z1 - 2)],
               blanket_l)
        R.box(img, X1 - 26, X1 - 12, 24, 28, Z0 + 14, Z1 - 3, hx("e2dac4"), top=hx("eee7d4"), side=hx("b8af98"))
        for (p, q) in (((X0 + 50, 24.1, Z0 + 10), (X0 + 70, 24.1, Z1 - 8)), ((X0 + 62, 24.1, Z0 + 6), (X1 - 30, 24.1, Z0 + 20))):
            R.line(img, p, q, hx("aaa088"))
    # side rail, front posts and end panels (in front of the mattress)
    R.line(img, (X0, 12, Z1), (X1, 12, Z1), IRON, 2)
    for x, top, mid in ((X0, 30, 20), (X1, 46, 32)):
        R.line(img, (x, 0, Z1), (x, top, Z1), IRON, 2)
        R.line(img, (x, top, Z0), (x, top, Z1), IRON, 2)
        R.line(img, (x, mid, Z0), (x, mid, Z1), IRON)
        for z in range(Z0 + 6, Z1 - 3, 6):
            R.line(img, (x, mid, z), (x, top, z), IRON_L)
        for z in (Z0, Z1):
            px, py = R.P(x, top + 1.5, z)
            ImageDraw.Draw(img).ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=BRASS)
    if unmade:  # the top sheet dragged half off, hanging over the rail
        R.quad(img, [(X0 + 30, 24, Z1 - 1), (X0 + 52, 24, Z1 - 1), (X0 + 56, 6, Z1 + 1), (X0 + 27, 8, Z1 + 1)], sheet)
        R.line(img, (X0 + 40, 22, Z1), (X0 + 42, 8, Z1 + 1), sheet_d)


def nightstand(img):
    X0, X1, Z0, Z1 = 148, 172, 3, 22
    R.box(img, X0, X1, 0, 30, Z0, Z1, hx("5a4130"), top=hx("74563e"), side=hx("3c2a1d"))
    R.quad(img, [(X0 + 2, 18, Z1), (X1 - 2, 18, Z1), (X1 - 2, 27, Z1), (X0 + 2, 27, Z1)], None, hx("2a1c12"))
    R.quad(img, [(X0 + 2, 3, Z1), (X1 - 2, 3, Z1), (X1 - 2, 15, Z1), (X0 + 2, 15, Z1)], None, hx("2a1c12"))
    for y in (22, 9):
        px, py = R.P((X0 + X1) / 2, y, Z1)
        ImageDraw.Draw(img).rectangle([px - 2, py, px + 2, py + 1], fill=hx("ac8a4a"))
    # ashtray and a water glass
    R.box(img, 152, 160, 30, 31.5, 9, 16, hx("5e5a52"), top=hx("8a857a"))
    R.box(img, 164, 167, 30, 36, 10, 13, hx("a9b2a6"), top=hx("d8e0d4"))


def chair(img):
    X0, X1, Z0, Z1 = 236, 258, 6, 24
    sh = R.P(X0, 0, Z1), R.P(X1, 0, Z0)
    shadow(img, "rect", [sh[0][0] - 1, sh[1][1], sh[1][0] + 3, sh[0][1] + 2], 0.4, 2)
    dark, mid = hx("3a281b"), hx("5a3c27")
    for x in (X0 + 1, X1 - 1):
        R.line(img, (x, 0, Z0 + 1), (x, 46, Z0 + 1), dark, 2)
    for y in (32, 38, 44):
        R.line(img, (X0 + 1, y, Z0 + 1), (X1 - 1, y, Z0 + 1), mid, 2)
    R.box(img, X0, X1, 18, 21, Z0, Z1, hx("6a4830"), top=hx("7e5a3c"), side=hx("4a311f"))
    for x in (X0 + 1, X1 - 1):
        R.line(img, (x, 0, Z1 - 1), (x, 18, Z1 - 1), dark, 2)
    R.line(img, (X0 + 1, 7, Z1 - 1), (X1 - 1, 7, Z1 - 1), dark)


def bottle(img):
    """The rotgut bottle, standing on the floor by the chair leg."""
    d = ImageDraw.Draw(img)
    bx, by = R.P(270, 0, 14)
    bx, by = int(bx), int(by)
    d.ellipse([bx - 4, by - 1, bx + 5, by + 2], fill=hx("3e2e20"))
    d.rectangle([bx - 2, by - 9, bx + 2, by], fill=hx("6a4a1c"))
    d.rectangle([bx - 1, by - 13, bx + 1, by - 9], fill=hx("5a3e18"))
    d.rectangle([bx - 2, by - 7, bx + 2, by - 4], fill=hx("d8ccaa"))
    d.point((bx - 1, by - 8), fill=hx("c49a52"))
    d.rectangle([bx - 1, by - 14, bx + 1, by - 13], fill=hx("2a1a10"))


def dresser(img):
    X0, X1, Z0, Z1 = 410, 466, 2, 22
    R.box(img, X0, X1, 0, 42, Z0, Z1, hx("4c3a2a"), top=hx("6a5038"), side=hx("2e2218"))
    for i, y in enumerate((30, 17, 4)):
        R.quad(img, [(X0 + 3, y, Z1), (X1 - 3, y, Z1), (X1 - 3, y + 10, Z1), (X0 + 3, y + 10, Z1)], None, hx("2a1a10"))
        R.line(img, (X0 + 4, y + 9, Z1), (X1 - 4, y + 9, Z1), hx("6e5440"))
        px, py = R.P((X0 + X1) / 2, y + 5, Z1)
        ImageDraw.Draw(img).rectangle([px - 3, py, px + 3, py + 1], fill=hx("b28a46"))
    a, b = R.P(X0, 42, Z0), R.P(X1, 0, Z1)
    noise(img, (int(a[0]), int(a[1]), int(b[0]), int(b[1])), 4, 410)
    # a clouded mirror hung over it
    d = ImageDraw.Draw(img)
    d.rectangle([420, 54, 456, 88], fill=WOOD_D)
    vgrad(img, (423, 57, 453, 85), hx("a7ad98"), hx("6d7266"))
    d.rectangle([430, 62, 446, 74], fill=hx("8a9aa4"))
    d.polygon([(432, 72), (438, 66), (444, 72)], fill=hx("6a7a58"))
    d.line([(428, 60), (436, 70)], fill=hx("c8ccb8"))
    shadow(img, "ellipse", [424, 58, 452, 84], 0.2, 6, hx("8a7a5a"))


def bulb(img):
    d = ImageDraw.Draw(img)
    d.line([(244, 0), (244, 26)], fill=hx("1e1814"))
    d.ellipse([239, 26, 249, 38], fill=hx("b8b09a"))
    d.rectangle([242, 24, 246, 28], fill=hx("625948"))
    d.line([(244, 38), (244, 48)], fill=hx("a69e88"))
    light(img, "ellipse", [210, -6, 278, 74], hx("b6b078"), 0.08, 16)


def details(img):
    d = ImageDraw.Draw(img)
    # Crooked motel print
    d.polygon([(78, 34), (118, 32), (120, 62), (76, 64)], fill=hx("6c5237"))
    d.polygon([(82, 36), (114, 35), (116, 59), (80, 60)], fill=hx("cabf9f"))
    d.rectangle([86, 40, 110, 54], fill=hx("8a8f6b"))
    d.rectangle([86, 50, 110, 54], fill=hx("7f684b"))
    d.line([(87, 42), (98, 47), (108, 41)], fill=hx("9ea47f"))
    d.line([(84, 62), (112, 60)], fill=hx("2c2018"))
    # a second print and a tear-off calendar, so the wall is not one brown wash
    d.polygon([(150, 28), (196, 26), (198, 58), (148, 60)], fill=hx("5c4632"))
    d.polygon([(154, 31), (192, 29), (194, 54), (152, 56)], fill=hx("8aa0b0"))
    d.polygon([(154, 44), (194, 42), (194, 54), (152, 56)], fill=hx("6a7a58"))
    d.polygon([(168, 40), (178, 36), (182, 44)], fill=hx("d8d0c0"))
    d.rectangle([206, 30, 228, 52], fill=hx("efe6d0"), outline=hx("6a5038"))
    d.line([(206, 36), (228, 36)], fill=hx("a04040"))
    d.text((210, 38), "27", fill=hx("2a2018"))
    # Scuffs and grime around the baseboards
    for x in range(18, W, 28):
        d.line([(x, FLOOR - 8), (x + 8, FLOOR - 4)], fill=hx("271b13"))
    for (x, y) in ((304, 168), (318, 176), (380, 190), (196, 200)):
        d.ellipse([x, y, x + 10, y + 4], fill=hx("4a392b"))


def paint(unmade=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img)
    details(img)
    door(img)
    bed(img, unmade)
    nightstand(img)
    chair(img)
    dresser(img)
    bottle(img)
    bulb(img)
    img = tall(img, ceiling)
    vignette(img, 0.62, tint=(34, 32, 20), blur=46)
    return img


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("4c4736"), hx("7a7255"))
    for x in range(0, W, 12):
        d.line([(x, 8), (x, TOP)], fill=hx("665f49"))
        d.line([(x + 5, 8), (x + 5, TOP)], fill=hx("877f62"))
    noise(img, (0, 0, W - 1, TOP), 4, 411)
    d.rectangle([0, 0, W - 1, 4], fill=hx("312418"))
    d.rectangle([0, 6, W - 1, 8], fill=hx("5e4b34"))
    d.line([(0, 8), (W, 8)], fill=hx("2a1d12"))
    shadow(img, "ellipse", [214, 0, 276, 30], 0.18, 8, hx("6f6145"))
    d.line([(248, 6), (242, 14), (248, 22)], fill=hx("443a2d"))


# --- night: Eleanor asleep under the sheet, a bedside lamp turned low, neon through the window -------------------

WIN = (302, 26, 396, 92)
LAMP_W = (163, 30, 13)  # world position of the bedside lamp's foot on the nightstand
NIGHT_EXTRA = [hx(c) for c in ("ff3a4a", "c8203a", "ff8090", "4a8cff", "2a5ad0", "a0c8ff", "fff2c8", "ffd27a",
                               "e09a44", "f0e6c0", "d8c690", "a8935e", "a83e3c", "3a2418", "1e120c", "3a2014", "5a3422", "8a5638",
                               "e8b890", "b88060", "5a3020", "f0dcb0", "a88a64")]


def window_night(img):
    """Frame and curtains only; the glass is painted after the room has been darkened."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WIN
    d.rectangle([x0, y0, x1, y1], fill=hx("101420"))
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 7], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 4], fill=WOOD)
    d.rectangle([x0, y0, x1, y1], fill=hx("101420"))
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 8], fill=hx("4e3a2a"))
    curtains(img)


def glass_night(img, flicker=1.0):
    """Night outside the glass: rooftops against an indigo sky and the motel's neon sign right outside."""
    x0, y0, x1, y1 = WIN
    layer = Image.new("RGB", img.size)
    vgrad(layer, (x0, y0, x1, y1), hx("0a0c22"), hx("2a1838"))
    ld = ImageDraw.Draw(layer)
    for (sx, sy) in ((330, 32), (342, 29), (360, 36), (368, 30)):
        ld.point((sx, sy), fill=hx("a0a8c8"))
    ld.rectangle([x0, 64, x1, y1], fill=hx("0a0810"))
    ld.rectangle([x0, 58, 330, 64], fill=hx("0a0810"))
    ld.rectangle([352, 52, 366, 64], fill=hx("0a0810"))
    ld.point((340, 70), fill=hx("e8c060"))
    ld.point((358, 68), fill=hx("e8c060"))
    # neon: a red MOTEL sign and a blue VACANCY strip below it, glowing in the wet air
    light(layer, "ellipse", [326, 34, 398, 70], hx("c8203a"), 0.45 * flicker, 8)
    light(layer, "ellipse", [334, 64, 398, 90], hx("2a5ad0"), 0.45, 6)
    text(layer, (351, 49), "MOTEL", hx("ff3a4a"), size=8)
    text(layer, (351, 76), "VACANCY", hx("4a8cff"), size=8)
    ld.line([(330, 42), (392, 42)], fill=hx("ff8090"))
    ld.line([(330, 56), (392, 56)], fill=hx("ff8090"))
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    md.rectangle([x0, y0, x1, y1], fill=255)
    for pts, _ in CURTAINS:
        md.polygon(pts, fill=0)
    img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("140c0a"), width=2)
    d.line([(x0, 58), (x1, 58)], fill=hx("140c0a"), width=2)
    d.rectangle([x0, y0, x1, y1], outline=hx("140c0a"))
    curtains(img, night=True)


def _ell(d, c, rx, ry, col):
    d.ellipse([c[0] - rx, c[1] - ry, c[0] + rx, c[1] + ry], fill=col)


def bed_night(img, rails=True):
    """Iron bed and mattress support; the neutral occupied linen is painted after the room grade."""
    X0, X1, Z0, Z1 = 52, 140, 4, 42
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z0)
    shadow(img, "rect", [a[0] - 2, b[1] - 2, b[0] + 6, a[1] + 3], 0.45, 3)
    for x, top in ((X0, 30), (X1, 46)):
        R.line(img, (x, 0, Z0), (x, top, Z0), IRON, 2)
    R.box(img, X0 + 2, X1 - 2, 12, 15, Z0 + 2, Z1 - 2, IRON_L)
    R.box(img, X0 + 2, X1 - 2, 15, 24, Z0 + 2, Z1 - 2, hx("cfc6ad"), top=hx("ddd4bc"), side=hx("a59c84"))
    # two pillows at the head end, the back one propped against the rail
    R.box(img, X1 - 17, X1 - 4, 24, 31, Z0 + 3, Z0 + 16, hx("d8d0ba"), top=hx("e6dfcc"), side=hx("b0a690"))
    R.box(img, X1 - 20, X1 - 4, 24, 28, Z0 + 12, Z1 - 5, hx("e2dac4"), top=hx("eee7d4"), side=hx("b8af98"))
    # The occupied drape is painted in screen space after lighting, not as rigid world-space quads.
    # the blanket kicked into a heap at the foot, half off the end
    R.quad(img, [(X0 - 2, 22, Z0 + 4), (X0 + 14, 27, Z0 + 6), (X0 + 18, 26, Z1 - 4), (X0 - 2, 22, Z1)],
           hx("6f7558"))
    R.quad(img, [(X0 + 2, 26, Z0 + 10), (X0 + 12, 29, Z0 + 12), (X0 + 14, 27, Z1 - 8), (X0 + 2, 25, Z1 - 6)],
           hx("8c9270"))
    R.line(img, (X0 + 4, 26, Z0 + 14), (X0 + 12, 27.5, Z1 - 10), hx("565b44"))
    if rails:
        bed_rails_night(img)
    R.quad(img, [(X0 - 1, 23, Z1), (X0 + 16, 24, Z1), (X0 + 14, 4, Z1 + 2), (X0 - 3, 6, Z1 + 2)], hx("6f7558"))
    R.line(img, (X0 + 6, 22, Z1 + 1), (X0 + 5, 6, Z1 + 2), hx("565b44"))


def bed_rails_night(img):
    X0, X1, Z0, Z1 = 52, 140, 4, 42
    d = ImageDraw.Draw(img)
    # No near side rail: the hanging sheet hides it, and drawn in front it read as a stray floor line.
    for x, top_, mid in ((X0, 30, 20), (X1, 46, 32)):
        R.line(img, (x, 0, Z1), (x, top_, Z1), IRON, 2)
        R.line(img, (x, top_, Z0), (x, top_, Z1), IRON, 2)
        R.line(img, (x, mid, Z0), (x, mid, Z1), IRON)
        for z in range(Z0 + 6, Z1 - 3, 6):
            R.line(img, (x, mid, z), (x, top_, z), IRON_L)
        for z in (Z0, Z1):
            px, py = R.P(x, top_ + 1.5, z)
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=BRASS)


# The wider lap adds six pixels before the mirrored head: net head shift is five right, two back.
ELEANOR_ORIGIN = (110, 112)


# Eleanor's legs under the cover, hip to toes, in screen space at mid-mattress depth:
# the near leg first, the far one a little deeper (higher on screen) and to the right.
LEGS = [(122, 123), (113, 121), (102, 120), (93, 122), (86, 123), (81, 121)]
FAR_LEG = [(x + 3, y - 5) for x, y in LEGS]
# The near head post; Eleanor's lap sheet must stop behind it rather than hang through the frame.
HEAD_POST_X = 134


def _leg_height(path, xx, yy, radius):
    distance = np.full(xx.shape, np.inf)
    along = np.zeros(xx.shape)
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    travelled, total = 0.0, sum(lengths)
    for a, b, length in zip(path, path[1:], lengths):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = np.clip(((xx - a[0]) * dx + (yy - a[1]) * dy) / length ** 2, 0, 1)
        dist = np.hypot(xx - a[0] - t * dx, yy - a[1] - t * dy)
        nearest = dist < distance
        along[nearest] = (travelled + t * length)[nearest] / total
        distance = np.minimum(distance, dist)
        travelled += length
    # Thighs are fuller than shins; the feet lift the cover again at the far end.
    girth = radius * (1.15 - 0.45 * along + 0.35 * np.exp(-((along - 0.97) / 0.06) ** 2))
    return np.exp(-(distance / girth) ** 2), distance, girth


def body_mound(cloth, legs, radius=5.0, lift=1.2):
    """Shade leg-shaped height fields into flat linen: lamp-facing slopes lift, near slopes fall into shadow."""
    rgba = np.asarray(cloth).astype(float)
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[:h, :w].astype(float)
    fields = [_leg_height(path, xx, yy, radius) for path in legs]
    # Where the legs overlap the higher one wins, leaving a shallow valley between them.
    height = np.max([f[0] for f in fields], axis=0) * lift
    gy, gx = np.gradient(height)
    shade = 22 * height + 150 * gy - 40 * gx
    for near, far in zip(legs, legs[1:]):
        # The cover sags into a crease between neighbouring legs.
        gap, _, _ = _leg_height([((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(near, far)],
                                xx, yy, 1.2)
        shade -= 12 * gap
    # The cover pulls taut over the near shin and drops a soft shadow along the near side.
    _, distance, girth = fields[0]
    shade -= 16 * np.exp(-((distance - girth * 1.25) / 1.5) ** 2) * (yy > np.interp(xx, *zip(*sorted(legs[0]))))
    from .mansion import SHEET_FOLD, SHEET_LIT
    rgba[:, :, :3] = np.clip(rgba[:, :, :3] + shade[:, :, None], SHEET_FOLD, SHEET_LIT)
    return Image.fromarray(rgba.astype("uint8"), "RGBA")


def white_bed_linen(img):
    from .mansion import linen_surface, SHEET, SHEET_SIDE
    for outline, center in (
        ([(124, 104), (134, 106), (138, 110), (136, 122), (131, 124), (122, 120), (122, 108)],
         (130, 113)),
        ([(121, 115), (133, 116), (138, 123), (133, 129), (120, 127), (117, 122)],
         (128, 122)),
    ):
        pillow = linen_surface((W, H), outline, [
            ([(125, center[1] + 4), (130, center[1] + 5), (135, center[1] + 2)], 1.1, 18),
        ], SHEET, loft=[(*center, 6, 5, 14)])
        ImageDraw.Draw(pillow).rectangle([HEAD_POST_X, 0, W, H], fill=(0, 0, 0, 0))
        img.paste(pillow, (0, TOP), pillow)
    # Screen coordinates follow the projected mattress: the lap rises at the head,
    # then the sheet turns over the near edge and hangs in unequal scallops.
    side = linen_surface((W, H), [
        (54, 128), (67, 130), (83, 129), (99, 131), (116, 129), (132, 128),
        (132, 144), (128, 155), (118, 156), (112, 153), (98, 155),
        (88, 152), (76, 154), (66, 151), (51, 152), (49, 146),
    ], [
        ([(59, 129), (62, 138), (59, 150)], 2.0, 23),
        ([(78, 130), (75, 137), (77, 146), (81, 153)], 2.3, 28),
        ([(99, 132), (104, 139), (101, 150)], 2.4, 26),
        ([(123, 129), (119, 138), (120, 148), (117, 154)], 1.7, 22),
    ], SHEET_SIDE, falloff=0.85)
    top = linen_surface((W, H), [
        (55, 118), (65, 115), (74, 116), (82, 113), (87, 112), (92, 109),
        (99, 106), (107, 105), (114, 107), (120, 111), (127, 113), (133, 117),
        (132, 128), (122, 132), (112, 131), (99, 134), (86, 131),
        (75, 132), (64, 130), (53, 133),
    ], [
        ([(58, 121), (65, 122), (73, 120)], 1.3, 17),
        ([(74, 116), (79, 121), (87, 123), (94, 128)], 1.7, 27),
        ([(102, 115), (96, 120), (98, 126), (107, 130)], 1.6, 25),
        ([(120, 119), (113, 123), (112, 128)], 1.5, 20),
        ([(61, 128), (68, 127), (73, 129)], 1.0, 14),
    ], SHEET, falloff=0.35)
    img.paste(side, (0, TOP), side)
    img.paste(body_mound(top, [LEGS, FAR_LEG]), (0, TOP), top)
    # Cotton compressed under the seated hip and between the two pillows.
    shadow(img, "ellipse", [120, 145, 138, 157], 0.25, 2)


def sleeper(img):
    from PIL import ImageOps
    from .mansion import _eleanor_in_bed
    eleanor = ImageOps.mirror(_eleanor_in_bed())
    # Trim the lap sheet's spill past the near head post so the iron frame stays clean.
    alpha = eleanor.getchannel("A")
    ImageDraw.Draw(alpha).rectangle([HEAD_POST_X - ELEANOR_ORIGIN[0], 20, eleanor.width, eleanor.height], fill=0)
    eleanor.putalpha(alpha)
    img.paste(eleanor, ELEANOR_ORIGIN, eleanor)

def nightstand_night(img):
    X0, X1, Z0, Z1 = 148, 172, 3, 22
    R.box(img, X0, X1, 0, 30, Z0, Z1, hx("5a4130"), top=hx("74563e"), side=hx("3c2a1d"))
    R.quad(img, [(X0 + 2, 18, Z1), (X1 - 2, 18, Z1), (X1 - 2, 27, Z1), (X0 + 2, 27, Z1)], None, hx("2a1c12"))
    R.quad(img, [(X0 + 2, 3, Z1), (X1 - 2, 3, Z1), (X1 - 2, 15, Z1), (X0 + 2, 15, Z1)], None, hx("2a1c12"))
    for y in (22, 9):
        px, py = R.P((X0 + X1) / 2, y, Z1)
        ImageDraw.Draw(img).rectangle([px - 2, py, px + 2, py + 1], fill=hx("ac8a4a"))
    R.box(img, 150, 157, 30, 31.5, 13, 19, hx("5e5a52"), top=hx("8a857a"))  # ashtray
    R.box(img, 150, 153, 30, 36, 6, 9, hx("a9b2a6"), top=hx("d8e0d4"))  # half-empty glass


def lamp_night(img):
    """The little bedside lamp, its shade glowing, drawn after the relight."""
    d = ImageDraw.Draw(img)
    x, y, z = LAMP_W
    bx, by = R.P(x, y, z)
    d.ellipse([bx - 3, by - 1, bx + 3, by + 1], fill=hx("4a3420"))
    d.line([(bx, by), (bx, by - 9)], fill=hx("6a5030"), width=2)
    d.ellipse([bx - 2, by - 6, bx + 2, by - 2], fill=hx("8a6a3a"))
    shade = [(bx - 3, by - 16), (bx + 3, by - 16), (bx + 6, by - 9), (bx - 6, by - 9)]
    d.polygon(shade, fill=hx("ffd27a"))
    d.line([(bx - 1, by - 15), (bx - 3, by - 10)], fill=hx("fff2c8"))
    d.line([(bx + 2, by - 15), (bx + 4, by - 10)], fill=hx("e09a44"))
    d.line([(bx - 6, by - 9), (bx + 6, by - 9)], fill=hx("e09a44"))
    d.line([(bx - 3, by - 16), (bx + 3, by - 16)], fill=hx("c8803a"))
    light(img, "ellipse", [bx - 12, by - 24, bx + 12, by - 2], hx("ffd27a"), 0.3, 4)


def clothes(img):
    """Micah's trench coat flung over the chair back and his fedora dropped on the seat."""
    X0, X1, Z0, Z1 = 236, 258, 6, 24
    coat, coat_d, coat_l = hx("ae8848"), hx("7a5c2c"), hx("c8a060")
    R.quad(img, [(X0 - 2, 48, Z0 + 1), (X1 + 2, 47, Z0 + 1), (X1 + 3, 20, Z0 + 4), (X0 - 3, 21, Z0 + 4)], coat)
    R.quad(img, [(X0 - 3, 21, Z0 + 4), (X1 + 3, 20, Z0 + 4), (X1 + 2, 21, Z0 + 12), (X0 - 2, 21, Z0 + 10)], coat_d)
    R.line(img, (X0 - 2, 48, Z0 + 1), (X1 + 2, 47, Z0 + 1), coat_l)
    R.line(img, (X0 + 9, 46, Z0 + 1), (X0 + 7, 22, Z0 + 4), coat_d)  # lapel fold
    R.line(img, (X0 + 13, 44, Z0 + 1), (X0 + 14, 30, Z0 + 2), coat_d)
    # a sleeve hanging down the side to the floor, and the belt trailing
    R.quad(img, [(X0 - 3, 40, Z0 + 2), (X0 + 2, 40, Z0 + 2), (X0 + 1, 3, Z0 + 6), (X0 - 5, 4, Z0 + 6)], coat_d)
    R.line(img, (X0 - 4, 38, Z0 + 2), (X0 - 4, 6, Z0 + 6), coat)
    R.line(img, (X1 + 2, 26, Z0 + 4), (X1 + 4, 8, Z0 + 8), hx("6a4e26"), 2)
    # fedora on the seat
    d = ImageDraw.Draw(img)
    hx_, hy_ = R.P(X0 + 13, 21, Z1 - 6)
    d.ellipse([hx_ - 8, hy_ - 2, hx_ + 8, hy_ + 2], fill=hx("4a3a2c"))
    d.rectangle([hx_ - 5, hy_ - 6, hx_ + 5, hy_], fill=hx("5c4838"))
    d.ellipse([hx_ - 5, hy_ - 8, hx_ + 5, hy_ - 4], fill=hx("6c5644"))
    d.line([(hx_ - 1, hy_ - 7), (hx_ + 1, hy_ - 5)], fill=hx("4a3a2c"))
    d.rectangle([hx_ - 5, hy_ - 2, hx_ + 5, hy_ - 1], fill=hx("1a120e"))


def relight_night(img):
    """Night grade: the room sinks into blue-black, the lamp keeps a warm pool by the bed, neon washes the floor."""
    lx, ly = R.P(LAMP_W[0], LAMP_W[1] + 12, LAMP_W[2])
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, (52, 56, 96)))
    warm = ImageChops.multiply(img, Image.new("RGB", img.size, (255, 196, 128)))
    warm = ImageChops.screen(warm, Image.new("RGB", img.size, (26, 12, 2)))
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    md.ellipse([lx - 150, ly - 90, lx + 150, ly + 110], fill=90)
    m = m.filter(ImageFilter.GaussianBlur(36))
    core = Image.new("L", img.size, 0)
    cd = ImageDraw.Draw(core)
    cd.ellipse([lx - 90, ly - 40, lx + 40, ly + 50], fill=200)  # the bed and her face
    cd.ellipse([lx - 50, ly - 50, lx + 50, ly + 70], fill=190)
    cd.polygon([(lx - 6, ly), (lx + 6, ly), (lx + 40, ly - 70), (lx - 40, ly - 70)], fill=120)  # up the wall
    core = core.filter(ImageFilter.GaussianBlur(14))
    m = ImageChops.lighter(m, core)
    out = Image.composite(warm, dark, m)
    # neon from the window: red and blue bands across the floor, the curtains backlit
    light(out, "polygon", [(310, 92), (350, 92), (330, 228), (230, 228)], hx("c8203a"), 0.12, 16)
    light(out, "polygon", [(350, 92), (394, 92), (470, 228), (330, 228)], hx("2a5ad0"), 0.11, 16)
    light(out, "rect", [292, 18, 406, 90], hx("a03050"), 0.22, 4)
    light(out, "ellipse", [270, 0, 430, 120], hx("6a2040"), 0.12, 20)
    return out


def paint_night(rails=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window_night(img)
    details(img)
    door(img)
    bed_night(img, rails=rails)
    nightstand_night(img)
    chair(img)
    clothes(img)
    dresser(img)
    bottle(img)
    bulb(img)
    img = relight_night(img)
    glass_night(img)
    lamp_night(img)
    img = tall(img, ceiling_night)
    vignette(img, 0.72, tint=(14, 12, 30), blur=46)
    lit_frame = img.copy() if rails else None
    white_bed_linen(img)
    if not rails:
        sleeper(img)
    else:
        rail_mask = Image.new("RGBA", (W, H))
        bed_rails_night(rail_mask)
        img.paste(lit_frame.crop((0, TOP, W, TOP + H)), (0, TOP), rail_mask.getchannel("A"))
    return img


def ceiling_night(img):
    ceiling(img)
    band = img.crop((0, 0, W, TOP + 1))
    band = ImageChops.multiply(band, Image.new("RGB", band.size, (52, 56, 96)))
    img.paste(band, (0, 0))


def build():
    made = paint(False)
    unmade = paint(True)
    pal = palette_of(Image.blend(made, unmade, 0.5), 128)
    save(pixelize(made, pal), "rooms", "motel_room_made.png")
    save(pixelize(unmade, pal), "rooms", "motel_room_unmade.png")
    night = paint_night()
    from .mansion import LINEN_PALETTE
    palette = palette_of(night, 102) + NIGHT_EXTRA + LINEN_PALETTE
    save(pixelize(night, palette), "rooms", "motel_night.png")
    rail_mask = Image.new("RGBA", (W, H))
    bed_rails_night(rail_mask)
    alpha = Image.new("L", night.size)
    alpha.paste(rail_mask.getchannel("A"), (0, TOP))
    foreground = pixelize(paint_night(rails=True), palette).convert("RGBA")
    foreground.putalpha(alpha)
    save(foreground, "rooms", "motel_night_rails.png")
    eleanor_rise(palette)
    return made


def eleanor_rise(palette):
    """Bed-scale, lamp-lit Eleanor and the one sheet she holds; points are in final room pixels."""
    from .sprites import action_strip
    import numpy as np
    anchor, position = (64, 100), (110, 194)

    def local(p):
        return (round(p[0] - position[0] + anchor[0]), round(p[1] - position[1] + anchor[1]))

    frames = []
    # Head, shoulder, hip, knee, foot, supporting hand.
    poses = [
        ((125, 146), (115, 151), (93, 153), (76, 155), (57, 160), (108, 157)),
        ((124, 138), (116, 148), (95, 155), (78, 157), (59, 162), (110, 163)),
        ((123, 130), (119, 144), (102, 159), (83, 160), (64, 163), (111, 165)),
        ((124, 127), (122, 141), (108, 159), (94, 166), (85, 174), (132, 162)),
        ((121, 125), (121, 139), (113, 159), (102, 168), (102, 184), (130, 158)),
        ((116, 123), (116, 137), (110, 158), (105, 174), (102, 191), (125, 159)),
        ((110, 121), (111, 135), (106, 155), (104, 175), (102, 192), (116, 155)),
        ((105, 119), (106, 133), (104, 154), (102, 174), (102, 192), (108, 149)),
        ((102, 119), (103, 133), (103, 153), (102, 174), (102, 192), (103, 145)),
    ]
    for index, points in enumerate(poses):
        img = Image.new("RGBA", (128, 104))
        d = ImageDraw.Draw(img)
        head, shoulder, hip, knee, foot, hand = [np.array(local(p), float) for p in points]
        skin, shade, hair = hx("e8b890"), hx("b88060"), hx("3a2014")
        _ell(d, tuple(shoulder + (0, 4)), 5, 6, skin)
        # The same hem drapes over the near mattress edge, then gathers around her planted feet.
        gather = max(0, 1 - index / 5)
        front = [tuple(shoulder + (-5, 6)), tuple(hip + (-7, 5)), tuple(knee + (-6, 4)),
                 tuple(foot + (-6, 1)), tuple(foot + (-5, 1 + 16 * gather)),
                 tuple(knee + (4, 2 + 15 * gather)), tuple(hip + (7, 1 + 15 * gather)),
                 tuple(shoulder + (5, 6))]
        d.polygon(front, fill=hx("cfc6ad"), outline=hx("a88a64"))
        d.line([tuple(shoulder + (4, 8)), tuple(hip + (5, 2)), tuple(knee + (4, 3)), tuple(foot + (4, 0))],
               fill=hx("a88a64"), width=2)
        for a, b in ((shoulder + (-3, 7), hip + (-3, 5)), (hip + (2, 3), knee + (2, 3)),
                     (knee + (-2, 4), foot + (-2, 0))):
            d.line([tuple(a), tuple(b)], fill=hx("f0dcb0"))
        if gather:
            d.line([tuple(knee + (0, 5)), tuple(knee + (1, 2 + 15 * gather))], fill=hx("a88a64"))
        d.line([tuple(head + (0, 4)), tuple(shoulder)], fill=skin, width=4)
        d.line([tuple(shoulder + (2, 4)), tuple(hand)], fill=shade, width=4)
        d.line([tuple(shoulder + (1, 3)), tuple(hand)], fill=skin, width=2)
        grip = shoulder + (-3, 7)
        d.line([tuple(shoulder + (-4, 3)), tuple(grip)], fill=skin, width=3)
        d.line([tuple(shoulder + (-5, 7)), tuple(shoulder + (5, 7))], fill=hx("f0dcb0"), width=2)
        _ell(d, (head[0] + 2, head[1] + 2), 6, 7 if index > 1 else 4, hair)
        if index > 1:
            d.polygon([(head[0] + 3, head[1] - 3), (head[0] + 6, head[1] + 3),
                       (head[0] + 7, head[1] + 10), (head[0] + 9, head[1] + 17),
                       (head[0] + 4, head[1] + 18), (head[0] + 3, head[1] + 8)], fill=hair)
            d.line([(head[0] + 5, head[1] + 5), (head[0] + 4, head[1] + 10),
                    (head[0] + 7, head[1] + 15)], fill=hx("5a3422"))
        _ell(d, (head[0], head[1]), 4, 5, skin)
        d.arc([head[0] - 5, head[1] - 6, head[0] + 5, head[1] + 4], 180, 330, fill=hx("8a5638"), width=2)
        d.line([(head[0] - 3, head[1] - 1), (head[0] - 1, head[1] - 1)], fill=hx("3a2418"))
        d.point((head[0] - 4, head[1] + 1), fill=hx("fff2c8"))
        d.point((head[0] - 3, head[1] + 3), fill=hx("a83e3c"))
        alpha = img.getchannel("A")
        img = pixelize(img, palette, spread=4).convert("RGBA")
        img.putalpha(alpha)
        frames.append((img, tuple(head)))
    action_strip("eleanor_sheet_rise", frames, [0.18, 0.24, 0.28, 0.26, 0.3, 0.25, 0.24, 0.24, 0.3], anchor=anchor)
