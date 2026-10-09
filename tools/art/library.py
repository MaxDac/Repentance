"""An opulent old private library: dark wood shelves, firelight and scholarly clutter."""
from PIL import Image, ImageDraw
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
    vgrad(glass, (x0, y0, x1, y1), hx("23344a"), hx("64728c"))
    gd = ImageDraw.Draw(glass)
    for cx, cy, r, col in ((344, 82, 18, hx("283522")), (372, 74, 22, hx("314126")), (396, 88, 16, hx("24301d"))):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    gd.ellipse([338, 40, 356, 58], fill=hx("d8d2b0"))
    gd.line([(346, 42), (346, 56)], fill=hx("f0ead0"))
    gd.line([(339, 50), (353, 50)], fill=hx("f0ead0"))
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
    light(img, "polygon", [(328, 30), (404, 30), (468, 198), (286, 198)], hx("8094bc"), 0.18, 12)
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
    for lx in range(firebox[0] + 6, firebox[2] - 6, 12):
        d.line([(lx, firebox[3]), (lx + 10, firebox[1] + 24)], fill=hx("2a2a2a"))
    logs = [(206, 144, 236, 150), (230, 140, 260, 148), (246, 144, 278, 151)]
    for ax, ay, bx, by in logs:
        d.rectangle([ax, ay, bx, by], fill=hx("5c351f"))
        d.line([(ax + 2, ay + 1), (bx - 2, ay + 1)], fill=hx("7d5133"))
    flame_cols = [hx("ffda7a"), hx("f49a28"), hx("ffd7b0"), hx("d95819")]
    flames = [
        [(214, 146), (220, 128), (230, 146)],
        [(226, 148), (238, 120), (250, 148)],
        [(244, 146), (258, 126), (270, 147)],
    ]
    for pts, col in zip(flames, flame_cols):
        d.polygon(pts, fill=col)
    d.ellipse([222, 146, 262, 154], fill=hx("f07424"))
    light(img, "ellipse", [194, 110, 286, 170], hx("ffb45a"), 0.48, 16)
    light(img, "ellipse", [148, 86, 330, 182], hx("905428"), 0.18, 24)
    mantle_items(img)


def mantle_items(img):
    d = ImageDraw.Draw(img)
    d.ellipse([202, 30, 276, 54], fill=hx("2a1711"))
    d.ellipse([208, 34, 270, 50], fill=hx("cdb890"))
    d.line([(239, 42), (250, 37)], fill=hx("28160f"))
    d.line([(239, 42), (239, 33)], fill=hx("28160f"))
    for x in (184, 289):
        d.rectangle([x, 28, x + 9, 52], fill=hx("8c7a5a"))
        d.ellipse([x - 2, 24, x + 11, 31], fill=hx("bca670"))
        d.ellipse([x, 25, x + 9, 29], fill=hx("eadcb0"))
    d.rectangle([158, 46, 322, 58], fill=MAHOGANY_L)
    d.line([(160, 48), (320, 48)], fill=hx("8a5a3e"))
    shadow(img, "rect", [158, 56, 322, 63], 0.35, 4)


def book_rows(d, x0, y0, x1, y1, seed):
    rnd = random.Random(seed)
    x = x0 + 2
    while x < x1 - 3:
        bw = rnd.randint(4, 8)
        col = rnd.choice([
            hx("7a2c22"), hx("5a1c1c"), hx("6b4c24"), hx("33441f"),
            hx("3b2e56"), hx("8c7a3c"), hx("7e5c3a"), hx("6a232f")
        ])
        d.rectangle([x, y0, min(x1 - 1, x + bw), y1], fill=col)
        if rnd.random() < 0.35:
            stripe = x + max(1, bw // 2)
            d.line([(stripe, y0 + 1), (stripe, y1 - 1)], fill=GOLD)
        if rnd.random() < 0.16 and x + bw + 6 < x1:
            lean = rnd.randint(2, 5)
            d.polygon([(x, y1), (x + bw + 2, y1), (x + bw - lean, y0), (x - lean, y0)], fill=mul(col, 0.82))
            x += bw + 2
        x += bw + 1


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
    d.rectangle([144, 20, 334, 24], fill=hx("6d4b33"))
    d.line([(144, 24), (334, 24)], fill=GOLD)


def desk(img):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([160, 116, 320, 180], 8, fill=hx("5a2c1b"))
    d.rounded_rectangle([166, 120, 314, 176], 7, outline=hx("2a120b"))
    d.polygon([(156, 122), (324, 122), (316, 112), (164, 112)], fill=hx("6f3d26"))
    d.line([(166, 113), (314, 113)], fill=hx("8d593b"))
    for px0 in (170, 260):
        d.rectangle([px0, 126, px0 + 44, 173], outline=hx("26110b"))
        for yy in (129, 149):
            d.rectangle([px0 + 4, yy, px0 + 40, yy + 16], outline=hx("30170f"))
            d.rectangle([px0 + 18, yy + 7, px0 + 26, yy + 9], fill=GOLD)
    d.rectangle([216, 126, 260, 173], fill=hx("2e150d"))
    for lx in (178, 306):
        d.line([(lx, 176), (lx - 10, 220)], fill=hx("30140c"), width=4)
        d.line([(lx, 176), (lx - 10, 220)], fill=hx("5a2b1a"), width=2)
    for lx in (304, 172):
        d.line([(lx, 176), (lx + 8, 220)], fill=hx("30140c"), width=4)
        d.line([(lx, 176), (lx + 8, 220)], fill=hx("5a2b1a"), width=2)
    shadow(img, "polygon", [(150, 178), (330, 178), (348, 224), (132, 224)], 0.28, 10)


def desk_props(img):
    d = ImageDraw.Draw(img)
    # oil lamp
    d.ellipse([182, 104, 210, 112], fill=hx("8a622a"))
    d.rectangle([193, 90, 199, 104], fill=hx("a67838"))
    d.ellipse([188, 84, 204, 94], fill=hx("ead8a8"))
    d.ellipse([190, 86, 202, 92], fill=hx("fff0b8"))
    d.polygon([(194, 82), (197, 74), (200, 82)], fill=hx("ffd870"))
    light(img, "ellipse", [150, 64, 250, 138], hx("ffd08a"), 0.58, 18)
    light(img, "polygon", [(180, 104), (212, 104), (238, 122), (154, 122)], hx("fff0c8"), 0.48, 5)
    # papers, quill, magnifier
    d.polygon([(222, 102), (260, 100), (262, 116), (218, 118)], fill=hx("d7c5a0"))
    d.line([(228, 106), (254, 105)], fill=hx("7a6a54"))
    d.line([(228, 110), (252, 109)], fill=hx("7a6a54"))
    d.line([(244, 98), (270, 110)], fill=hx("e8e0d0"))
    d.polygon([(244, 98), (249, 96), (246, 101)], fill=hx("d0d0d0"))
    d.ellipse([272, 102, 286, 116], outline=hx("b88a4c"), width=2)
    d.line([(284, 114), (292, 121)], fill=hx("b88a4c"), width=2)
    # globe
    d.line([(292, 89), (292, 112)], fill=hx("7b572e"), width=2)
    d.arc([281, 84, 303, 106], 190, 350, fill=hx("9d7440"), width=2)
    d.ellipse([282, 74, 302, 94], fill=hx("56745c"))
    d.line([(291, 75), (291, 93)], fill=hx("a0c29a"))
    d.line([(284, 84), (300, 84)], fill=hx("a0c29a"))
    light(img, "ellipse", [280, 72, 306, 98], hx("d8c890"), 0.25, 4)


def chairs(img):
    d = ImageDraw.Draw(img)
    # left chair
    d.rounded_rectangle([86, 134, 150, 186], 12, fill=hx("4f2317"))
    d.rounded_rectangle([94, 128, 142, 164], 10, fill=hx("6a2c1f"))
    d.rectangle([90, 164, 146, 186], fill=hx("5a261b"))
    for x in (98, 138):
        d.line([(x, 182), (x - 8, 220)], fill=hx("38180f"), width=3)
    for x in (110, 146):
        d.line([(x, 182), (x + 8, 220)], fill=hx("38180f"), width=3)
    # right chair
    d.rounded_rectangle([338, 138, 400, 188], 12, fill=hx("482116"))
    d.rounded_rectangle([344, 132, 394, 166], 10, fill=hx("60281c"))
    d.rectangle([344, 166, 394, 188], fill=hx("542318"))
    for x in (350, 388):
        d.line([(x, 184), (x - 8, 220)], fill=hx("34140d"), width=3)
    for x in (362, 398):
        d.line([(x, 184), (x + 8, 220)], fill=hx("34140d"), width=3)
    # small side table
    d.ellipse([144, 176, 182, 184], fill=hx("744128"))
    d.line([(152, 180), (148, 214)], fill=hx("3a190f"), width=2)
    d.line([(174, 180), (178, 214)], fill=hx("3a190f"), width=2)
    d.ellipse([156, 166, 170, 176], fill=hx("6c8a52"))
    d.line([(162, 166), (162, 176)], fill=hx("8cb47a"))
    shadow(img, "ellipse", [74, 184, 166, 226], 0.3, 7)
    shadow(img, "ellipse", [330, 186, 412, 228], 0.3, 7)


def ladder(img):
    d = ImageDraw.Draw(img)
    rail = [(418, 28), (392, 156)]
    d.line(rail, fill=hx("85603a"), width=4)
    d.line([(430, 30), (404, 158)], fill=hx("5f3d23"), width=4)
    for t in range(0, 7):
        x = 416 - t * 4
        y = 42 + t * 16
        d.line([(x, y), (x + 18, y + 2)], fill=hx("a27a46"), width=2)
    d.ellipse([382, 150, 438, 162], outline=hx("987246"), width=2)
    d.ellipse([386, 152, 434, 160], outline=hx("3a2416"))
    shadow(img, "polygon", [(390, 156), (432, 160), (442, 224), (378, 224)], 0.15, 8)


def paint():
    img = Image.new("RGB", (W, H))
    shell(img)
    arched_window(img)
    fireplace(img)
    shelves(img)
    parquet_floor(img)
    chairs(img)
    desk(img)
    desk_props(img)
    ladder(img)
    light(img, "ellipse", [150, 118, 334, 236], hx("9a5426"), 0.11, 18)
    shadow(img, "ellipse", [0, 0, W - 1, 40], 0.22, 12, hx("2a130d"))
    return tall(img, ceiling)


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
    vignette(base, 0.58, tint=(62, 40, 18), blur=42)
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "library.png")
    return px
