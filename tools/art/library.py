"""An opulent old private library by day: dark wood shelves, sunlight slanting in, the desk lamp cold."""
from PIL import Image, ImageDraw
import math
import random
from .common import (W, H, TOP, hx, mul, vgrad, noise, light, shadow, vignette,
                     pixelize, palette_of, tall, save, floor_boards)

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


def arched_window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 314, 20, 414, 132
    arch = [x0, y0 - 28, x1, y0 + 36]
    d.rectangle([x0 - 6, y0 + 14, x1 + 6, y1 + 4], fill=MAHOGANY_D)
    d.pieslice([x0 - 6, y0 - 34, x1 + 6, y0 + 38], 180, 360, fill=MAHOGANY_D)
    glass = Image.new("RGB", img.size, 0)
    # a clear midday sky over sunlit treetops
    vgrad(glass, (x0, y0 - 28, x1, y1), hx("a8cce8"), hx("e8eee4"))
    gd = ImageDraw.Draw(glass)
    for cx, cy, r, col in ((344, 82, 18, hx("6c9a4c")), (372, 74, 22, hx("7eac58")), (396, 88, 16, hx("5e8a42"))):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([x0, y0 + 12, x1, y1], fill=255)
    md.pieslice(arch, 180, 360, fill=255)
    img.paste(glass, (0, 0), mask)
    d.rectangle([x0, y0 + 12, x1, y1], outline=hx("20100b"), width=3)
    d.arc(arch, 180, 360, fill=hx("20100b"), width=3)
    for xx in (346, 380):
        d.line([(xx, y0 + 4), (xx, y1)], fill=hx("20100b"), width=2)
    d.line([(x0, 76), (x1, 76)], fill=hx("20100b"), width=2)
    d.line([(x0 + 10, 108), (x1 - 10, 108)], fill=hx("2c1812"))
    d.polygon([(292, 18), (330, 18), (352, 146), (316, 146)], fill=hx("5a1e26"))
    d.polygon([(436, 18), (398, 18), (376, 146), (412, 146)], fill=hx("47151c"))
    for x in (304, 420):
        d.line([(x, 18), (x + (-8 if x > 360 else 8), 142)], fill=hx("8a5c42"), width=2)
    light(img, "polygon", [(328, 30), (404, 30), (468, 198), (286, 198)], hx("fff2d0"), 0.22, 12)
    shadow(img, "polygon", [(300, 18), (332, 18), (318, 156), (284, 156)], 0.2, 7, hx("28140f"))


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
    bookcase(img, 352, 464, 10, 7)
    d = ImageDraw.Draw(img)
    # middle upper shelves flanking the fireplace
    for x0, x1, seed in ((132, 166, 13), (312, 346, 17)):
        d.rectangle([x0, 20, x1, 108], fill=MAHOGANY)
        d.rectangle([x0 + 4, 24, x1 - 4, 104], fill=hx("27130d"))
        for sy in (44, 68, 92):
            d.rectangle([x0 + 4, sy, x1 - 4, sy + 3], fill=MAHOGANY_L)
            book_rows(d, x0 + 6, sy - 16, x1 - 6, sy, seed + sy)
        d.rectangle([x0, 20, x1, 108], outline=hx("160906"))


def desk(img):
    # roughly waist height for the ~85px characters, kept below the fireplace opening
    d = ImageDraw.Draw(img)
    shadow(img, "polygon", [(186, 200), (294, 200), (304, 212), (176, 212)], 0.3, 5)
    d.polygon([(188, 167), (292, 167), (287, 161), (193, 161)], fill=hx("6f3d26"))
    d.line([(194, 161), (286, 161)], fill=hx("8d593b"))
    d.rectangle([190, 167, 290, 194], fill=hx("5a2c1b"), outline=hx("2a120b"))
    d.line([(190, 168), (290, 168)], fill=hx("2a120b"))
    for px0 in (194, 260):
        d.rectangle([px0, 170, px0 + 26, 192], outline=hx("26110b"))
        for yy in (172, 182):
            d.rectangle([px0 + 2, yy, px0 + 24, yy + 8], outline=hx("30170f"))
            d.rectangle([px0 + 11, yy + 4, px0 + 15, yy + 4], fill=GOLD)
    d.rectangle([222, 170, 258, 194], fill=hx("2e150d"))
    for lx, dx in ((194, -3), (286, 3)):
        d.line([(lx, 194), (lx + dx, 206)], fill=hx("30140c"), width=3)
        d.line([(lx, 194), (lx + dx, 206)], fill=hx("5a2b1a"), width=1)


def desk_props(img):
    d = ImageDraw.Draw(img)
    # oil lamp, unlit in the daytime: cold glass chimney, a dark wick
    d.ellipse([199, 158, 211, 162], fill=hx("8a622a"))
    d.rectangle([204, 151, 206, 158], fill=hx("a67838"))
    d.ellipse([201, 147, 209, 152], fill=hx("a8a490"))
    d.ellipse([202, 148, 208, 151], fill=hx("c8c4b0"))
    d.line([(205, 144), (205, 146)], fill=hx("3a2c20"))
    # papers, quill, magnifier
    d.polygon([(222, 160), (242, 159), (243, 165), (220, 166)], fill=hx("d7c5a0"))
    d.line([(225, 161), (239, 161)], fill=hx("7a6a54"))
    d.line([(225, 163), (238, 163)], fill=hx("7a6a54"))
    d.line([(234, 157), (248, 163)], fill=hx("e8e0d0"))
    d.ellipse([249, 159, 256, 165], outline=hx("b88a4c"))
    d.line([(255, 164), (259, 167)], fill=hx("b88a4c"))
    # globe
    d.line([(276, 151), (276, 162)], fill=hx("7b572e"))
    d.ellipse([272, 160, 281, 163], fill=hx("7b572e"))
    d.arc([269, 143, 283, 157], 190, 350, fill=hx("9d7440"))
    d.ellipse([270, 143, 282, 155], fill=hx("56745c"))
    d.line([(276, 143), (276, 155)], fill=hx("a0c29a"))
    d.line([(270, 149), (282, 149)], fill=hx("a0c29a"))
    light(img, "ellipse", [268, 141, 284, 157], hx("d8c890"), 0.2, 3)


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
    d.line([(354, 21), (462, 21)], fill=hx("202024"), width=3)
    d.line([(354, 20), (462, 20)], fill=hx("82786a"))
    for x in (360, 390, 454):
        d.line([(x, 17), (x, 25)], fill=hx("54504a"), width=2)
    for top_x in (420, 438):
        d.arc([top_x - 3, 18, top_x + 3, 30], 180, 350, fill=hx("9a8868"), width=2)
        d.line([(top_x, 26), (top_x - 29, 181)], fill=hx("362418"), width=4)
        d.line([(top_x - 1, 27), (top_x - 30, 180)], fill=hx("a27a46"), width=2)
    for y in range(38, 175, 11):
        x = 420 - 29 * (y - 26) / 155
        d.line([(x + 2, y + 1), (x + 16, y + 1)], fill=hx("38261a"), width=3)
        d.line([(x + 2, y), (x + 16, y)], fill=hx("b8945e"), width=2)
    for x in (391, 409):
        d.rectangle([x - 2, 177, x + 2, 182], fill=hx("56504a"))
        d.ellipse([x - 3, 180, x + 3, 186], fill=hx("242426"), outline=hx("867c6a"))
        d.point((x, 183), fill=hx("b8aa90"))
    shadow(img, "ellipse", [380, 183, 425, 189], 0.18, 3)


def paint():
    img = Image.new("RGB", (W, H))
    shell(img)
    arched_window(img)
    fireplace(img)
    shelves(img)
    mantle_items(img)
    parquet_floor(img)
    chairs(img)
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
    for top, foot in (((330, 0), (380, 0)), ((392, 0), (430, 0))):
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
    d.ellipse([228, 9, 252, 23], fill=hx("6d4a26"))
    d.line([(240, 0), (240, 10)], fill=hx("2a140d"))
    noise(img, (0, 0, W - 1, TOP), 4, 41)


def build():
    base = paint()
    vignette(base, 0.32, tint=(120, 96, 70), blur=42)
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "library.png")
    return px
