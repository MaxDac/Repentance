"""A cheap roadside motel room in flat, dingy daytime light."""
from PIL import Image, ImageDraw
from .common import (W, H, TOP, tall, hx, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of, save,
                     floor_boards)
from .furniture import Room3D

FLOOR = 136
WOOD = hx("6a5038")
WOOD_D = hx("342418")
R = Room3D(FLOOR, 250, -250)


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

    # Peeling wallpaper
    peel = (
        [(128, 18), (148, 14), (160, 26), (156, 44), (138, 48), (124, 34)],
        [(368, 20), (398, 18), (416, 32), (406, 54), (378, 56), (362, 38)],
        [(214, 54), (242, 48), (256, 66), (248, 86), (222, 88), (206, 72)],
    )
    for pts in peel:
        d.polygon(pts, fill=hx("a79d79"), outline=hx("5e543e"))
        inner = [(x + (1 if i % 2 else -1), y + 2) for i, (x, y) in enumerate(pts)]
        d.line(inner + [inner[0]], fill=hx("cec3a4"))

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


def window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 302, 26, 396, 92
    vgrad(img, (x0, y0, x1, y1), hx("dcd8b8"), hx("aeb89e"))
    d.rectangle([x0, 70, x1, y1], fill=hx("7b7554"))
    d.rectangle([x0, 62, x1, 70], fill=hx("938a63"))
    d.rectangle([320, 50, 332, 92], fill=hx("5f5a46"))
    d.rectangle([346, 44, 356, 92], fill=hx("655f49"))
    d.rectangle([372, 54, 382, 92], fill=hx("595542"))
    light(img, "rect", [x0, y0, x1, y1], hx("f5efc6"), 0.18, 2)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 7], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 4], fill=WOOD)
    d.rectangle([x0, y0, x1, y1], outline=hx("20140e"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("2a1a12"), width=2)
    d.line([(x0, 58), (x1, 58)], fill=hx("2a1a12"), width=2)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 8], fill=hx("4e3a2a"))

    # Thin grubby curtains
    left = [(292, 18), (324, 22), (330, 36), (324, 84), (306, 88), (296, 58)]
    right = [(406, 18), (374, 22), (368, 36), (374, 84), (392, 88), (402, 58)]
    d.polygon(left, fill=hx("c0b490"))
    d.polygon(right, fill=hx("b8ac88"))
    for x in range(298, 328, 5):
        d.line([(x, 22), (x + 1, 84)], fill=hx("a89b78"))
    for x in range(372, 402, 5):
        d.line([(x, 22), (x - 1, 84)], fill=hx("a0926e"))
    noise(img, (294, 18, 404, 88), 5, 408)
    d.line([(286, 18), (412, 18)], fill=hx("3a2c1e"), width=2)
    d.line([(350, 18), (350, 12)], fill=hx("3a2c1e"))
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


def build():
    made = paint(False)
    unmade = paint(True)
    pal = palette_of(Image.blend(made, unmade, 0.5), 128)
    save(pixelize(made, pal), "rooms", "motel_room_made.png")
    save(pixelize(unmade, pal), "rooms", "motel_room_unmade.png")
    return made
