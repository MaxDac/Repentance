"""An opulent old private library by day: dark wood shelves, sunlight slanting in, the desk lamp cold."""
from PIL import Image, ImageDraw
import math
import random
import numpy as np
from .common import (W, H, TOP, hx, mul, vgrad, noise, light, shadow, vignette,
                     pixelize, palette_of, tall, save, floor_boards, cut)

FLOOR = 154
MAHOGANY = hx("4c2416")
MAHOGANY_D = hx("2a130d")
MAHOGANY_L = hx("70402a")
BURGUNDY = hx("5b1f22")
GOLD = hx("c8a25a")


def shell(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("4e3326"), hx("21150f"))
    for x in range(0, W, 7):
        d.line([(x, 0), (x, FLOOR)], fill=hx("3a241b"))
    for y in range(18, FLOOR, 22):
        d.line([(0, y), (W - 1, y)], fill=hx("2c1914"))
    d.rectangle([0, 0, W - 1, FLOOR], outline=hx("1c0e0a"))
    d.rectangle([0, 112, W - 1, FLOOR], fill=hx("3a2014"))
    d.rectangle([0, 110, W - 1, 113], fill=GOLD)
    d.line([(0, 114), (W - 1, 114)], fill=MAHOGANY_D)
    for x in range(0, W, 32):
        d.rectangle([x + 4, 118, x + 28, FLOOR - 4], outline=hx("26130d"))
        d.line([(x + 5, 119), (x + 27, 119)], fill=MAHOGANY_L)
    d.rectangle([0, FLOOR - 4, W - 1, FLOOR], fill=hx("1a0c08"))
    noise(img, (0, 0, W - 1, FLOOR), 4, 11)
    shadow(img, "ellipse", [44, 22, 124, 74], 0.14, 14, hx("6a4a30"))


def parquet_floor(img):
    floor_boards(img, FLOOR, H - 1, (240, -220), 19, hx("5b321d"), hx("3e2114"), hx("241109"), 23)
    d = ImageDraw.Draw(img)
    for y in range(FLOOR + 18, H, 22):
        d.line([(0, y), (W - 1, y)], fill=hx("332015"))
    for y in range(FLOOR + 10, H - 6, 14):
        off = (y - FLOOR) // 6
        for x in range(-20, W + 20, 28):
            d.line([(x + off, y), (x + 16 + off, y + 10)], fill=hx("6a4128"))
            d.line([(x + 16 + off, y), (x + off, y + 10)], fill=hx("2e160d"))
    rug = [(116, 172), (364, 172), (398, 226), (82, 226)]
    d.polygon(rug, fill=BURGUNDY)
    d.polygon([(126, 178), (354, 178), (384, 220), (96, 220)], outline=GOLD)
    d.polygon([(138, 184), (342, 184), (368, 214), (112, 214)], fill=hx("431418"), outline=hx("9a7442"))
    for i in range(6):
        x = 154 + i * 30
        d.polygon([(x, 195), (x + 9, 199), (x, 203), (x - 9, 199)], fill=hx("9a7442"))
    for x in range(94, 388, 4):
        d.line([(x, 220), (x, 222)], fill=hx("b79256"))
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 29)
    noise(img, (82, 172, 398, 226), 6, 31)


WINDOW = (354, 20, 398, 132)  # the glass (x0, y0, x1, y1), between the fireplace's side shelf and the right bookcase
RIGHT_CASE = (408, 474)  # the tall glass-front bookcase right of the window
LADDER_X = 440  # where the rolling ladder's left rail hooks onto its rail


def arched_window(img):
    """A tall, narrow round-headed window: a fanlight of leaded spokes over divided panes, a keystone, a stone sill
    with a potted fern, a brass latch, and drapes tied back so the midday sky over the rooftops shows."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WINDOW
    cx, r = (x0 + x1) // 2, (x1 - x0) // 2
    spring = y0 + 12  # where the arch springs from the straight jambs
    arch = [x0, spring - r, x1, spring + r]
    lead, frame = hx("2c1c14"), hx("20100b")
    # carved surround with a lit inner moulding
    d.rectangle([x0 - 6, spring, x1 + 6, y1 + 4], fill=MAHOGANY_D)
    d.pieslice([x0 - 6, spring - r - 6, x1 + 6, spring + r + 6], 180, 360, fill=MAHOGANY_D)
    d.arc([x0 - 4, spring - r - 4, x1 + 4, spring + r + 4], 180, 360, fill=MAHOGANY_L)
    d.line([(x0 - 4, spring), (x0 - 4, y1 + 2)], fill=MAHOGANY_L)
    d.line([(x1 + 4, spring), (x1 + 4, y1 + 2)], fill=hx("1a0c08"))
    # the view: a clear midday sky with a drift of cloud, the city's rooftops and a water tower, treetops below
    glass = Image.new("RGB", img.size, 0)
    vgrad(glass, (x0, spring - r, x1, y1), hx("9cc4e6"), hx("e6eee6"))
    gd = ImageDraw.Draw(glass)
    for ex, ey, rx, ry in ((362, 40, 9, 3), (370, 37, 7, 3), (388, 58, 8, 2)):
        gd.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=hx("f4f6f2"))
    for bx0, top, bx1, col in ((354, 92, 364, hx("8a96a6")), (364, 84, 372, hx("9aa4b2")),
                               (372, 96, 386, hx("7e8a9a")), (386, 88, 398, hx("909cac"))):
        gd.rectangle([bx0, top, bx1, y1], fill=col)
        for wy in range(top + 3, 108, 5):
            for wx in range(bx0 + 2, bx1 - 1, 3):
                gd.point((wx, wy), fill=hx("c8d2dc"))
    gd.rectangle([388, 78, 394, 84], fill=hx("6e665e"))
    gd.polygon([(387, 78), (391, 73), (395, 78)], fill=hx("5a524c"))
    gd.line([(389, 84), (389, 88)], fill=hx("4a4440"))
    gd.line([(393, 84), (393, 88)], fill=hx("4a4440"))
    for tx, ty, tr, col in ((358, 116, 9, hx("6c9a4c")), (374, 112, 11, hx("7eac58")), (392, 118, 9, hx("5e8a42"))):
        gd.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=col)
        gd.point((tx - tr // 2, ty - tr // 2), fill=hx("a8cc78"))
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([x0, spring, x1, y1], fill=255)
    md.pieslice(arch, 180, 360, fill=255)
    img.paste(glass, (0, 0), mask)
    # fanlight: leaded spokes from a half-round hub, closed off by the transom at the springing line
    for a in (198, 225, 252, 288, 315, 342):
        rad = math.radians(a)
        d.line([(cx + 6 * math.cos(rad), spring + 6 * math.sin(rad)),
                (cx + r * math.cos(rad), spring + r * math.sin(rad))], fill=lead)
    d.pieslice([cx - 6, spring - 6, cx + 6, spring + 6], 180, 360, fill=MAHOGANY_D, outline=frame)
    d.arc([cx - 12, spring - 12, cx + 12, spring + 12], 180, 360, fill=lead)
    # casement frame, central mullion, glazing bars and the meeting rail
    d.rectangle([x0, spring, x1, y1], outline=frame, width=3)
    d.arc(arch, 180, 360, fill=frame, width=3)
    d.line([(x0, spring), (x1, spring)], fill=frame, width=2)
    d.line([(cx, spring), (cx, y1)], fill=frame, width=2)
    for yy in (56, 104):
        d.line([(x0, yy), (x1, yy)], fill=lead)
    d.line([(x0, 80), (x1, 80)], fill=frame, width=2)
    for xx in (x0 + 11, x1 - 11):
        d.line([(xx, spring + 2), (xx, y1 - 2)], fill=lead)
    # brass latch on the meeting rail and a glint on the inner edge of the frame
    d.rectangle([cx - 2, 77, cx + 2, 79], fill=hx("8a6a30"))
    d.line([(cx - 1, 77), (cx + 1, 77)], fill=hx("e8c870"))
    d.line([(x0 + 3, spring + 3), (x0 + 3, y1 - 3)], fill=hx("6a4a36"))
    # keystone at the crown of the arch
    ky = spring - r - 7
    d.polygon([(cx - 5, ky), (cx + 5, ky), (cx + 3, ky + 9), (cx - 3, ky + 9)], fill=hx("6c4c36"), outline=frame)
    d.line([(cx - 4, ky + 1), (cx - 3, ky + 7)], fill=hx("8a6448"))
    # stone sill and a fern in a terracotta pot on it
    d.rectangle([x0 - 9, y1 + 4, x1 + 9, y1 + 8], fill=hx("8a7a66"))
    d.line([(x0 - 9, y1 + 4), (x1 + 9, y1 + 4)], fill=hx("b8a88e"))
    d.line([(x0 - 8, y1 + 9), (x1 + 8, y1 + 9)], fill=hx("2a160e"))
    d.polygon([(x0 + 5, y1 - 2), (x0 + 13, y1 - 2), (x0 + 12, y1 + 4), (x0 + 6, y1 + 4)], fill=hx("9a5a36"))
    d.line([(x0 + 5, y1 - 2), (x0 + 13, y1 - 2)], fill=hx("c07a4a"))
    for fx, fy in ((-5, -9), (-3, -12), (0, -13), (3, -12), (5, -8), (-6, -4), (6, -4)):
        d.line([(x0 + 9, y1 - 2), (x0 + 9 + fx, y1 - 2 + fy)], fill=hx("4e7a3a"))
        d.point((x0 + 9 + fx, y1 - 2 + fy), fill=hx("7eac58"))
    # drapes on short brass rods either side, gathered by gold tie-backs so the glass stays clear
    for side in (-1, 1):
        edge = x0 if side < 0 else x1
        out, inn = edge + side * 12, edge - side * 3
        col, fold = (hx("5a1e26"), hx("3e1218")) if side < 0 else (hx("47151c"), hx("2e0c12"))
        d.line([(edge + side * 15, 12), (edge - side * 2, 12)], fill=hx("a8823e"), width=2)
        d.ellipse([edge + side * 15 - 2, 10, edge + side * 15 + 2, 14], fill=GOLD)
        drape = [(out, 13), (inn, 13), (edge - side, 52), (edge + side * 6, 94), (edge, 146), (out - side * 2, 146),
                 (edge + side * 10, 94)]
        d.polygon(drape, fill=col)
        d.line([(edge + side * 4, 14), (edge + side * 8, 92)], fill=fold)
        d.line([(edge + side * 8, 98), (edge + side * 5, 144)], fill=fold)
        d.line([(inn, 14), (edge - side, 50)], fill=hx("8a3a3e"))
        d.ellipse([edge + side * 8 - 3, 92, edge + side * 8 + 3, 97], fill=GOLD, outline=hx("6a4a1e"))
        d.line([(edge + side * 8, 97), (edge + side * 8, 104)], fill=hx("a8823e"))
        d.point((edge + side * 8, 105), fill=GOLD)
    light(img, "polygon", [(x0 - 2, 30), (x1 + 2, 30), (x1 + 58, 198), (x0 - 70, 198)], hx("fff2d0"), 0.22, 12)
    shadow(img, "polygon", [(x0 - 12, 14), (x0 + 2, 14), (x0 - 4, 156), (x0 - 18, 156)], 0.2, 6, hx("28140f"))


def fireplace(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 170, 58, 308, 154
    d.rectangle([x0 - 12, y0 - 6, x1 + 12, y1], fill=hx("5a4030"))
    d.rectangle([x0 - 18, y0 - 14, x1 + 18, y0 - 6], fill=hx("6c4c36"))
    d.rectangle([x0 - 22, y0 - 18, x1 + 22, y0 - 14], fill=GOLD)
    d.rectangle([x0 - 22, y0 - 10, x0 - 12, y1], fill=hx("493224"))
    d.rectangle([x1 + 12, y0 - 10, x1 + 22, y1], fill=hx("493224"))
    firebox = [x0 + 18, y0 + 14, x1 - 18, y1]
    vgrad(img, tuple(firebox), hx("26140c"), hx("0f0705"))
    d.rectangle(firebox, outline=hx("120806"))
    for y in range(firebox[1] + 8, firebox[3], 9):
        d.line([(firebox[0] + 2, y), (firebox[2] - 2, y)], fill=hx("34241e"))
        for x in range(firebox[0] + 6 + (y // 9 % 2) * 8, firebox[2], 16):
            d.line([(x, y - 8), (x, y)], fill=hx("34241e"))
    logs = [(206, 144, 236, 150), (230, 140, 260, 148), (246, 144, 278, 151)]
    for ax, ay, bx, by in logs:
        d.rectangle([ax, ay, bx, by], fill=hx("5c351f"))
        d.line([(ax + 2, ay + 1), (bx - 2, ay + 1)], fill=hx("7d5133"))
    for x in range(204, 284, 9):
        d.line([(x, 135), (x, 151)], fill=hx("24262a"), width=2)
        d.line([(x, 135), (x, 139)], fill=hx("585452"))
    d.rectangle([202, 147, 284, 150], fill=hx("363638"))
    d.line([(202, 147), (284, 147)], fill=hx("68605a"))


def mantle_items(img):
    d = ImageDraw.Draw(img)
    d.rectangle([158, 46, 322, 58], fill=MAHOGANY_L)
    d.line([(160, 48), (320, 48)], fill=hx("8a5a3e"))
    d.ellipse([223, 13, 255, 39], fill=hx("342018"), outline=GOLD)
    d.rectangle([223, 26, 255, 44], fill=hx("42291e"))
    d.rectangle([219, 43, 259, 46], fill=hx("6a4430"), outline=hx("28160f"))
    d.line([(225, 28), (225, 42)], fill=hx("9a7044"))
    d.line([(253, 28), (253, 42)], fill=hx("26140e"))
    d.ellipse([228, 18, 250, 40], fill=GOLD)
    d.ellipse([230, 20, 248, 38], fill=hx("e8dfc8"), outline=hx("725638"))
    for i in range(12):
        angle = i * math.pi / 6
        x, y = round(239 + 7 * math.sin(angle)), round(29 - 7 * math.cos(angle))
        d.point((x, y), fill=hx("362a20"))
        if i % 3 == 0:
            d.point((round(239 + 6 * math.sin(angle)), round(29 - 6 * math.cos(angle))), fill=hx("362a20"))
    d.line([(239, 29), (239, 23)], fill=hx("302418"))
    d.line([(239, 29), (243, 31)], fill=hx("302418"))
    d.point((239, 29), fill=hx("9a6434"))
    for x in (188, 293):
        d.ellipse([x - 5, 43, x + 5, 46], fill=hx("a88a50"))
        d.line([(x, 33), (x, 43)], fill=hx("b89a5a"), width=2)
        d.ellipse([x - 3, 32, x + 3, 35], fill=hx("8a6a38"))
        d.rectangle([x - 2, 23, x + 2, 32], fill=hx("ded4b8"))
        d.line([(x, 21), (x, 23)], fill=hx("342820"))
    shadow(img, "rect", [158, 56, 322, 63], 0.35, 4)


def book_rows(d, x0, y0, x1, y1, seed):
    rnd = random.Random(seed)
    x = x0 + 2
    while x < x1 - 3:
        bw = min(rnd.randint(4, 8), x1 - 2 - x)
        top = min(y1 - 3, y0 + rnd.randint(0, 4))
        col = rnd.choice([
            hx("7a2c22"), hx("5a1c1c"), hx("6b4c24"), hx("33441f"),
            hx("3b2e56"), hx("8c7a3c"), hx("7e5c3a"), hx("6a232f")
        ])
        d.rectangle([x, top, x + bw - 1, y1 - 1], fill=col)
        d.line([(x, top), (x, y1 - 1)], fill=mul(col, 1.3))
        d.line([(x + bw - 1, top), (x + bw - 1, y1 - 1)], fill=mul(col, 0.55))
        d.line([(x + 1, top), (x + bw - 2, top)], fill=hx("a69a78"))
        if bw >= 5 and y1 - top >= 8:
            for yy in (top + 3, y1 - 4):
                d.line([(x + 1, yy), (x + bw - 2, yy)], fill=mul(GOLD, 0.72))
            d.rectangle([x + 2, top + 6, x + bw - 3, top + 7], fill=mul(col, 0.6))
            d.point((x + 2, top + 6), fill=GOLD)
        x += bw + rnd.choice((1, 1, 2))


def bookcase(img, x0, x1, shelf_top=14, seed=0):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, shelf_top, x1, FLOOR], fill=MAHOGANY)
    d.rectangle([x0 + 6, shelf_top + 8, x1 - 6, FLOOR - 8], fill=hx("28130d"))
    for xx in (x0, x0 + 10, x1 - 10, x1):
        d.rectangle([xx, shelf_top, xx + 4, FLOOR], fill=MAHOGANY_D)
    shelf_ys = [34, 58, 82, 106, 130]
    for i, sy in enumerate(shelf_ys):
        d.rectangle([x0 + 8, sy, x1 - 8, sy + 4], fill=MAHOGANY_L)
        book_rows(d, x0 + 10, sy - 18, x1 - 10, sy, seed * 17 + i * 19 + 5)
    d.rectangle([x0 + 8, 132, x1 - 8, FLOOR - 10], fill=hx("2a1610"))
    book_rows(d, x0 + 12, 136, x1 - 12, FLOOR - 14, seed * 23 + 99)
    d.rectangle([x0, shelf_top, x1, FLOOR], outline=hx("180b08"))
    for y in range(18, FLOOR, 8):
        d.line([(x0 + 5, y), (x0 + 9, y)], fill=hx("7a4c2f"))
        d.line([(x1 - 9, y), (x1 - 5, y)], fill=hx("7a4c2f"))
    light(img, "rect", [x0 + 12, 18, x1 - 12, FLOOR - 16], hx("8c6434"), 0.06, 10)
    shadow(img, "rect", [x0, 0, x1, FLOOR], 0.1, 10)


def shelves(img):
    bookcase(img, 16, 128, 10, 2)
    bookcase(img, *RIGHT_CASE, 10, 7)
    d = ImageDraw.Draw(img)
    # middle upper shelves flanking the fireplace
    for x0, x1, seed in ((132, 166, 13), (312, 346, 17)):
        d.rectangle([x0, 20, x1, 108], fill=MAHOGANY)
        d.rectangle([x0 + 4, 24, x1 - 4, 104], fill=hx("27130d"))
        for sy in (44, 68, 92):
            d.rectangle([x0 + 4, sy, x1 - 4, sy + 3], fill=MAHOGANY_L)
            book_rows(d, x0 + 6, sy - 16, x1 - 6, sy, seed + sy)
        d.rectangle([x0, 20, x1, 108], outline=hx("160906"))


# The writing desk is a real prop: build() cuts it out of the painting into library_desk.png, drawn by a
# Y-sorted Sprite2D in library.tscn so Micah passes behind it (north) or in front of it (south).
DESK_BOX = (176, 160, 304, 238)  # crop of the desk sprite in screen coordinates (x0, y0, x1, y1), exclusive
DESK_SORT = (240, 236)  # Sprite2D position in library.tscn: where the front feet meet the floor


def desk_shadow(img):
    shadow(img, "polygon", [(184, 198), (296, 198), (306, 210), (174, 210)], 0.34, 4)


def desk(img):
    """A walnut pedestal desk, roughly waist height for the ~85px characters, below the fireplace opening."""
    d = ImageDraw.Draw(img)
    top, lip, body, plinth, feet = 160, 167, 170, 198, 206
    # top: a moulded walnut edge around a tooled green leather writing surface
    d.polygon([(186, lip), (294, lip), (288, top), (192, top)], fill=hx("6f3d26"))
    d.line([(192, top), (288, top)], fill=hx("8d593b"))
    d.polygon([(196, lip - 1), (284, lip - 1), (280, top + 2), (200, top + 2)], fill=hx("2e4a32"))
    d.polygon([(198, lip - 2), (282, lip - 2), (279, top + 3), (201, top + 3)], outline=hx("a8884a"))
    d.rectangle([185, lip, 295, lip + 2], fill=hx("7a4430"))
    d.line([(185, lip), (295, lip)], fill=hx("b07850"))
    d.line([(185, lip + 3), (295, lip + 3)], fill=hx("2a120b"))
    # carcass: two pedestals of three drawers either side of a recessed kneehole
    vgrad(img, (188, body, 292, plinth), hx("62301e"), hx("47200f"))
    d.rectangle([188, body, 292, plinth], outline=hx("2a120b"))
    d.rectangle([222, body + 1, 258, plinth], fill=hx("2a130b"))
    d.rectangle([224, body + 9, 256, plinth], fill=hx("3a1a10"), outline=hx("1e0c07"))
    for yy in range(body + 12, plinth, 4):
        d.line([(226, yy), (254, yy)], fill=hx("43200f"))
    d.rectangle([222, body + 1, 258, body + 7], fill=hx("55291a"), outline=hx("26110b"))
    d.rectangle([238, body + 3, 242, body + 4], fill=GOLD)
    d.line([(223, body + 8), (257, body + 8)], fill=hx("140805"))
    for px0 in (191, 260):
        for k, (y0, y1) in enumerate(((body + 2, body + 9), (body + 11, body + 18), (body + 20, plinth - 2))):
            d.rectangle([px0, y0, px0 + 28, y1], fill=hx("5e2e1c"), outline=hx("26110b"))
            d.line([(px0 + 1, y0 + 1), (px0 + 27, y0 + 1)], fill=hx("7e4630"))
            d.line([(px0 + 1, y1 - 1), (px0 + 27, y1 - 1)], fill=hx("3e1c10"))
            cy = (y0 + y1) // 2
            d.rectangle([px0 + 11, cy - 1, px0 + 17, cy], fill=hx("8a6a30"))
            d.line([(px0 + 12, cy - 1), (px0 + 16, cy - 1)], fill=hx("e8c870"))
            d.point((px0 + 14, cy + 1), fill=hx("2a1a0c"))
            if k == 0:
                d.rectangle([px0 + 3, cy - 1, px0 + 6, cy + 1], fill=hx("a88a4a"))
        d.line([(px0 - 1, body + 1), (px0 - 1, plinth)], fill=hx("7a4430"))
    # plinth and bun feet
    for x0, x1 in ((188, 222), (258, 292)):
        d.rectangle([x0 - 1, plinth, x1 + 1, plinth + 3], fill=hx("3a1a10"))
        d.line([(x0 - 1, plinth), (x1 + 1, plinth)], fill=hx("8a5238"))
        for fx in (x0 + 3, x1 - 3):
            d.ellipse([fx - 3, plinth + 3, fx + 3, feet], fill=hx("3e1c10"), outline=hx("1e0c07"))
            d.point((fx - 1, plinth + 5), fill=hx("8a5238"))
    d.line([(222, plinth), (258, plinth)], fill=hx("1e0c07"))


def desk_props(img):
    d = ImageDraw.Draw(img)
    # oil lamp, unlit in the daytime: brass font, cold glass chimney, a dark wick
    d.ellipse([197, 158, 211, 163], fill=hx("6a4a1e"))
    d.ellipse([198, 157, 210, 161], fill=hx("a67838"))
    d.ellipse([200, 150, 208, 157], fill=hx("b88a40"))
    d.point((202, 152), fill=hx("f0d890"))
    d.rectangle([203, 146, 205, 150], fill=hx("8a622a"))
    d.polygon([(202, 146), (206, 146), (207, 141), (206, 136), (202, 136), (201, 141)], fill=hx("b8b4a0"))
    d.line([(202, 137), (202, 145)], fill=hx("e8e4d4"))
    d.line([(204, 136), (204, 133)], fill=hx("3a2c20"))
    # a small oak card-catalogue box, one drawer pulled out with index cards
    d.rectangle([212, 152, 226, 163], fill=hx("8a5a30"), outline=hx("3a1e10"))
    d.line([(213, 153), (225, 153)], fill=hx("b07c46"))
    for yy in (155, 159):
        d.rectangle([214, yy, 224, yy + 2], fill=hx("6e4424"), outline=hx("3a1e10"))
        d.point((219, yy + 1), fill=GOLD)
    d.polygon([(214, 160), (224, 160), (226, 164), (212, 164)], fill=hx("7a4c28"))
    for x in (215, 217, 219, 221, 223):
        d.line([(x, 158), (x, 161)], fill=hx("ece2c8"))
    # open ledger, quill in an inkwell, magnifier
    d.polygon([(230, 160), (246, 159), (247, 165), (229, 166)], fill=hx("d7c5a0"))
    d.line([(238, 159), (238, 166)], fill=hx("9a8a6a"))
    for yy in (161, 163):
        d.line([(231, yy), (236, yy)], fill=hx("7a6a54"))
        d.line([(240, yy), (245, yy)], fill=hx("7a6a54"))
    d.rectangle([249, 160, 253, 164], fill=hx("1c1c24"), outline=hx("8a7a5a"))
    d.line([(251, 160), (257, 151)], fill=hx("e8e0d0"))
    d.line([(255, 153), (257, 151)], fill=hx("ffffff"))
    d.ellipse([256, 160, 263, 165], outline=hx("c89a54"))
    d.point((258, 161), fill=hx("e8f0f0"))
    d.line([(262, 164), (266, 166)], fill=hx("5a2a18"))
    # globe on a brass meridian stand
    d.ellipse([271, 161, 281, 164], fill=hx("5a3a1a"))
    d.line([(276, 155), (276, 162)], fill=hx("7b572e"))
    d.arc([268, 142, 284, 158], 120, 420, fill=hx("c8a25a"))
    d.ellipse([270, 143, 282, 155], fill=hx("4a6a7a"))
    d.polygon([(272, 146), (276, 145), (277, 149), (274, 151), (272, 149)], fill=hx("7a9a5a"))
    d.polygon([(278, 148), (281, 149), (280, 153), (278, 152)], fill=hx("8aa860"))
    d.line([(276, 143), (276, 155)], fill=hx("a0c29a"))
    d.line([(270, 149), (282, 149)], fill=hx("a0c29a"))
    d.point((273, 145), fill=hx("e8f4f0"))


def desk_mask():
    """Opaque pixels of the desk and its props (paint coordinates): painted over two grounds, they agree."""
    grounds = []
    for col in ((255, 0, 255), (0, 255, 0)):
        g = Image.new("RGB", (W, H), col)
        desk(g)
        desk_props(g)
        grounds.append(np.asarray(g).astype(int))
    same = np.all(grounds[0] == grounds[1], axis=2)
    return Image.fromarray((same * 255).astype("uint8"), "L")


def chairs(img):
    d = ImageDraw.Draw(img)
    for x0, top in ((96, 142), (346, 146)):
        x1, seat = x0 + 40, top + 31
        shadow(img, "ellipse", [x0 - 6, seat + 17, x1 + 7, seat + 34], 0.25, 5)
        for x, dx in ((x0 + 5, -3), (x1 - 5, 3)):
            d.line([(x, seat + 5), (x + dx, seat + 31)], fill=hx("29160e"), width=3)
            d.line([(x, seat + 6), (x + dx, seat + 28)], fill=hx("76503a"))
        d.rounded_rectangle([x0 + 3, top, x1 - 3, seat], 5, fill=hx("3a1c16"), outline=hx("28120e"))
        d.rounded_rectangle([x0 + 6, top + 3, x1 - 6, seat - 3], 4, fill=hx("70332a"), outline=hx("8a4a38"))
        d.line([(x0 + 8, top + 7), (x1 - 8, top + 7)], fill=hx("864334"))
        for x in (x0 + 14, x0 + 26):
            for y in (top + 12, top + 23):
                d.point((x, y), fill=hx("402019"))
                d.point((x + 1, y + 1), fill=hx("94523e"))
        d.rounded_rectangle([x0 + 4, seat - 2, x1 - 4, seat + 7], 2, fill=hx("76382c"), outline=hx("381a12"))
        d.line([(x0 + 7, seat), (x1 - 7, seat)], fill=hx("a05a40"))
        for x in (x0, x1 - 5):
            d.rounded_rectangle([x, seat - 10, x + 5, seat + 8], 2, fill=hx("54281e"), outline=hx("2c160e"))
            d.line([(x + 1, seat - 9), (x + 4, seat - 9)], fill=hx("9a5840"))
    # small side table
    d.ellipse([144, 176, 182, 184], fill=hx("744128"))
    d.line([(152, 180), (148, 214)], fill=hx("3a190f"), width=2)
    d.line([(174, 180), (178, 214)], fill=hx("3a190f"), width=2)
    d.ellipse([156, 166, 170, 176], fill=hx("6c8a52"))
    d.line([(162, 166), (162, 176)], fill=hx("8cb47a"))


def ladder(img):
    d = ImageDraw.Draw(img)
    rx0, rx1 = RIGHT_CASE[0] + 2, RIGHT_CASE[1] - 2
    d.line([(rx0, 21), (rx1, 21)], fill=hx("202024"), width=3)
    d.line([(rx0, 20), (rx1, 20)], fill=hx("82786a"))
    for x in (rx0 + 4, (rx0 + rx1) // 2 + 3, rx1 - 4):
        d.line([(x, 17), (x, 25)], fill=hx("54504a"), width=2)
    for top_x in (LADDER_X, LADDER_X + 18):
        d.arc([top_x - 3, 18, top_x + 3, 30], 180, 350, fill=hx("9a8868"), width=2)
        d.line([(top_x, 26), (top_x - 29, 181)], fill=hx("362418"), width=4)
        d.line([(top_x - 1, 27), (top_x - 30, 180)], fill=hx("a27a46"), width=2)
    for y in range(38, 175, 11):
        x = LADDER_X - 29 * (y - 26) / 155
        d.line([(x + 2, y + 1), (x + 16, y + 1)], fill=hx("38261a"), width=3)
        d.line([(x + 2, y), (x + 16, y)], fill=hx("b8945e"), width=2)
    for x in (LADDER_X - 29, LADDER_X - 11):
        d.rectangle([x - 2, 177, x + 2, 182], fill=hx("56504a"))
        d.ellipse([x - 3, 180, x + 3, 186], fill=hx("242426"), outline=hx("867c6a"))
        d.point((x, 183), fill=hx("b8aa90"))
    shadow(img, "ellipse", [LADDER_X - 40, 183, LADDER_X + 5, 189], 0.18, 3)


def paint(include_desk=True):
    img = Image.new("RGB", (W, H))
    shell(img)
    arched_window(img)
    fireplace(img)
    shelves(img)
    mantle_items(img)
    parquet_floor(img)
    chairs(img)
    desk_shadow(img)
    if include_desk:
        desk(img)
        desk_props(img)
    ladder(img)
    shadow(img, "ellipse", [0, 0, W - 1, 40], 0.22, 12, hx("2a130d"))
    sunlight(img)
    return tall(img, ceiling)


def sunlight(img):
    """Midday sun from the tall window on the right: an even daylight fill, slanting shafts and bright patches
    on the parquet and rug."""
    light(img, "rect", [0, 0, W - 1, H - 1], hx("fff0d8"), 0.13, 0)
    for top, foot in (((358, 0), (374, 0)), ((380, 0), (396, 0))):
        (a, _), (b, _) = top, foot
        light(img, "polygon", [(a, 0), (b, 0), (b - 190, 212), (a - 210, 212)], hx("fff0c8"), 0.2, 9)
    # the window's panes thrown across the rug, the mullions leaving darker bars
    for i in range(2):
        for j in range(3):
            x, y = 112 + j * 26 - i * 9, 182 + i * 14
            light(img, "polygon", [(x, y), (x + 22, y), (x + 15, y + 11), (x - 7, y + 11)], hx("ffe8b8"), 0.26, 1)
    rnd = random.Random(73)
    d = ImageDraw.Draw(img)
    for _ in range(26):
        y = rnd.randint(20, 190)
        x = rnd.randint(250, 400) - (y * 200) // 212
        d.point((x, y), fill=hx("f8ecd0"))


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("26140e"), hx("4c2d1f"))
    for x in range(0, W, 10):
        d.line([(x, 8), (x, TOP)], fill=hx("3a2116"))
    d.rectangle([0, 0, W - 1, 4], fill=hx("180a06"))
    d.rectangle([0, 5, W - 1, 8], fill=GOLD)
    d.rectangle([0, 9, W - 1, 12], fill=MAHOGANY_D)
    d.rectangle([0, 13, W - 1, 15], fill=MAHOGANY_L)
    d.line([(0, 16), (W - 1, 16)], fill=hx("1e0d08"))
    pendant(img)
    noise(img, (0, 0, W - 1, TOP), 4, 41)


def pendant(img):
    """The brass pendant lamp in the middle of the ceiling, cold in the daytime: a canopy and rod, a ribbed domed
    shade with a beaded gold rim, an amber glass bowl under it and a finial drop."""
    d = ImageDraw.Draw(img)
    cx = 240
    brass, brass_d, brass_l = hx("8a6a30"), hx("4a3418"), hx("e8c870")
    # ceiling canopy and rod
    d.ellipse([cx - 6, -2, cx + 6, 3], fill=brass, outline=brass_d)
    d.line([(cx - 3, 1), (cx + 1, 1)], fill=brass_l)
    d.line([(cx, 3), (cx, 8)], fill=brass_d, width=2)
    d.line([(cx - 1, 3), (cx - 1, 8)], fill=hx("b89a5a"))
    d.rectangle([cx - 2, 7, cx + 2, 9], fill=brass, outline=brass_d)
    # domed shade: dark walnut-brown metal with ribs, lit from the window on the right
    d.chord([cx - 12, 9, cx + 12, 25], 180, 360, fill=hx("6d4a26"))
    d.chord([cx - 12, 9, cx + 12, 25], 270, 360, fill=hx("86603a"))
    for rx in (-8, -3, 3, 8):
        d.line([(cx + rx // 2, 10), (cx + rx, 16)], fill=hx("4a2e16"))
    d.arc([cx - 9, 11, cx + 9, 22], 290, 330, fill=hx("c8a070"))
    # beaded gold rim
    d.rectangle([cx - 12, 16, cx + 12, 17], fill=GOLD)
    d.line([(cx - 12, 18), (cx + 12, 18)], fill=brass_d)
    for bx in range(cx - 11, cx + 12, 3):
        d.point((bx, 16), fill=brass_l)
    # amber glass bowl and finial
    d.chord([cx - 9, 12, cx + 9, 24], 0, 180, fill=hx("b07a3a"))
    d.chord([cx - 9, 12, cx + 9, 24], 0, 90, fill=hx("d4a05a"))
    d.point((cx + 4, 20), fill=hx("f0d090"))
    d.line([(cx - 6, 19), (cx + 6, 19)], fill=hx("7a4e22"))
    d.ellipse([cx - 2, 23, cx + 2, 27], fill=brass, outline=brass_d)
    d.point((cx - 1, 24), fill=brass_l)
    d.point((cx, 28), fill=brass)


def build():
    base = paint()
    vignette(base, 0.32, tint=(120, 96, 70), blur=42)
    pal = palette_of(base, 128)
    room = paint(include_desk=False)
    vignette(room, 0.32, tint=(120, 96, 70), blur=42)
    px = pixelize(room, pal)
    save(px, "rooms", "library.png")
    mask = Image.new("L", base.size, 0)
    mask.paste(desk_mask(), (0, TOP))
    x0, y0, x1, y1 = DESK_BOX
    bx0, by0, bx1, by1 = mask.getbbox()
    assert x0 <= bx0 and y0 <= by0 and bx1 <= x1 and by1 <= y1, f"desk {mask.getbbox()} outside {DESK_BOX}"
    save(cut(pixelize(base, pal), mask).crop(DESK_BOX), "rooms", "library_desk.png")
    return px
