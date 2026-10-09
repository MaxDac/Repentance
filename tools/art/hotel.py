"""The Aurelian: a luxurious hotel room in warm daytime light."""
from PIL import Image, ImageDraw
from .common import (W, H, TOP, tall, hx, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     save, floor_boards)

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
    # framed art
    for x0 in (178, 384):
        d.rectangle([x0, 34, x0 + 48, 68], fill=GOLD_D)
        d.rectangle([x0 + 3, 37, x0 + 45, 65], fill=hx("a69374"))
        d.polygon([(x0 + 5, 63), (x0 + 18, 46), (x0 + 28, 54), (x0 + 44, 40), (x0 + 44, 63)], fill=hx("617367"))
        d.rectangle([x0 + 5, 55, x0 + 44, 63], fill=hx("6f5441"))
    shadow(img, "ellipse", [160, -4, 230, 26], 0.14, 10, hx("a89070"))


def floor(img):
    floor_boards(img, FLOOR, H - 1, (248, -220), 22, hx("7a5132"), hx("5d3922"), hx("342012"), 111)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 112)
    d = ImageDraw.Draw(img)
    rug = [(132, 156), (396, 156), (428, 224), (96, 224)]
    d.polygon(rug, fill=GREEN)
    d.polygon([(146, 162), (382, 162), (406, 216), (118, 216)], outline=GOLD)
    d.polygon([(160, 168), (368, 168), (388, 210), (138, 210)], outline=GREEN_L)
    for x in range(150, 392, 18):
        d.line([(x, 162), (x - 16, 220)], fill=mul(GOLD, 0.8))
    for y in range(170, 214, 8):
        d.line([(142, y), (392, y)], fill=mul(GREEN_L, 0.8))
    noise(img, (96, 156, 428, 224), 5, 113)


def window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 34, 22, 150, 106
    sky = Image.new("RGB", img.size)
    vgrad(sky, (x0, y0, x1, y1), hx("f3f0df"), hx("b9d3de"))
    hgrad(sky, (x0, y0, x1, y1), hx("f8f2e4"), hx("a7c7d9"))
    img.paste(sky.crop((x0, y0, x1 + 1, y1 + 1)), (x0, y0))
    for bx, bw, bh, col in ((42, 18, 20, hx("89939b")), (64, 22, 28, hx("78818a")), (88, 15, 18, hx("97a0a5")),
                            (108, 20, 24, hx("6d767e")), (128, 15, 16, hx("8b9499"))):
        d.rectangle([bx, y1 - bh, bx + bw, y1], fill=col)
        for wy in range(y1 - bh + 3, y1 - 2, 4):
            d.line([(bx + 2, wy), (bx + bw - 2, wy)], fill=mul(col, 0.7))
    d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y0 + 2], fill=hx("8c6748"))
    d.rectangle([x0 - 2, y1 - 2, x1 + 2, y1 + 2], fill=hx("5d3821"))
    d.rectangle([x0 - 2, y0 - 2, x0 + 2, y1 + 2], fill=hx("7b5639"))
    d.rectangle([x1 - 2, y0 - 2, x1 + 2, y1 + 2], fill=hx("5d3821"))
    d.rectangle([x0, y0, x1, y1], outline=hx("f7ecd4"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=WOOD_D, width=3)
    d.line([(x0, 61), (x1, 61)], fill=WOOD_D, width=2)
    # sheers and drapes
    d.polygon([(x0 - 4, y0 - 4), (x0 + 16, y0 + 10), (x0 + 22, y1 + 8), (x0 - 4, y1 + 10)], fill=hx("d6c9b7"))
    d.polygon([(x1 + 4, y0 - 4), (x1 - 16, y0 + 10), (x1 - 22, y1 + 8), (x1 + 4, y1 + 10)], fill=hx("d6c9b7"))
    d.polygon([(x0 - 16, y0 - 8), (x0 + 10, y0 + 2), (x0 + 20, y1 + 18), (x0 - 12, y1 + 18)], fill=BURGUNDY)
    d.polygon([(x1 + 16, y0 - 8), (x1 - 10, y0 + 2), (x1 - 20, y1 + 18), (x1 + 12, y1 + 18)], fill=BURGUNDY)
    d.rectangle([x0 - 20, y0 - 10, x1 + 20, y0 - 4], fill=GOLD_D)
    d.ellipse([x0 - 18, y0 + 26, x0 - 8, y0 + 36], fill=GOLD)
    d.ellipse([x1 + 8, y0 + 26, x1 + 18, y0 + 36], fill=GOLD)
    light(img, "polygon", [(56, 34), (128, 34), (316, 228), (120, 228)], hx("fff2cf"), 0.28, 8)
    light(img, "ellipse", [120, 100, 304, 226], hx("ffe5b0"), 0.18, 14)
    light(img, "rect", [x0, y0, x1, y1], hx("fff7e2"), 0.22, 5)


def sconces(img):
    d = ImageDraw.Draw(img)
    for cx in (186, 424):
        d.rectangle([cx - 4, 52, cx + 4, 68], fill=GOLD_D)
        d.polygon([(cx - 8, 70), (cx + 8, 70), (cx + 5, 84), (cx - 5, 84)], fill=hx("efe2c4"))
        d.line([(cx - 6, 70), (cx + 6, 70)], fill=GOLD)
        light(img, "ellipse", [cx - 18, 50, cx + 18, 88], hx("fff4db"), 0.14, 6)


def chandelier(img):
    d = ImageDraw.Draw(img)
    cx = 286
    d.line([(cx, 0), (cx, 28)], fill=GOLD_D)
    d.ellipse([cx - 8, 24, cx + 8, 34], fill=GOLD)
    d.polygon([(cx - 26, 36), (cx + 26, 36), (cx + 18, 50), (cx - 18, 50)], fill=GOLD, outline=GOLD_D)
    d.polygon([(cx - 18, 50), (cx + 18, 50), (cx + 10, 62), (cx - 10, 62)], fill=hx("ead9b0"), outline=GOLD_D)
    for ax in (-24, 0, 24):
        d.line([(cx, 40), (cx + ax, 56)], fill=GOLD_D)
        d.line([(cx + ax, 56), (cx + ax, 64)], fill=GOLD_D)
        d.ellipse([cx + ax - 4, 62, cx + ax + 4, 70], fill=hx("f8f1d8"))
    light(img, "ellipse", [cx - 70, 0, cx + 70, 84], hx("fff4d8"), 0.12, 18)


def desk(img):
    d = ImageDraw.Draw(img)
    # chair
    d.rounded_rectangle([64, 120, 100, 168], 6, fill=GREEN, outline=WOOD_D)
    for x in (72, 92):
        d.line([(x, 164), (x - 3, 190)], fill=WOOD_D, width=2)
    d.line([(84, 166), (84, 192)], fill=WOOD_D, width=2)
    # writing desk
    d.polygon([(22, 134), (132, 134), (126, 126), (28, 126)], fill=mul(WOOD, 1.1))
    d.rectangle([22, 134, 132, 170], fill=WOOD)
    d.rectangle([30, 140, 64, 168], outline=WOOD_D)
    d.rectangle([90, 140, 124, 168], outline=WOOD_D)
    d.rectangle([68, 140, 86, 170], fill=WOOD_D)
    for x in (42, 112):
        d.rectangle([x - 4, 149, x + 4, 152], fill=GOLD)
    for x in (30, 124):
        d.line([(x, 170), (x - 4, 208)], fill=WOOD_D, width=3)
    for x in (56, 98):
        d.line([(x, 170), (x + 2, 208)], fill=WOOD_D, width=3)
    shadow(img, "rect", [20, 170, 134, 210], 0.38, 4)
    # desk props
    d.polygon([(46, 123), (88, 121), (92, 132), (42, 133)], fill=hx("ece0c6"))
    d.line([(54, 126), (82, 124)], fill=hx("8c7d69"))
    d.line([(54, 129), (80, 127)], fill=hx("8c7d69"))
    d.rectangle([100, 116, 108, 132], fill=GOLD_D)
    d.ellipse([94, 121, 114, 126], fill=GOLD)
    d.point((104, 114), fill=hx("fff0b6"))
    d.ellipse([30, 121, 40, 127], fill=hx("2e3a3a"))
    d.line([(35, 118), (35, 123)], fill=hx("d0c0a0"))
    light(img, "ellipse", [18, 108, 146, 164], hx("fff3d5"), 0.12, 10)


def armchair(img):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([18, 176, 70, 218], 10, fill=BURGUNDY, outline=WOOD_D)
    d.rounded_rectangle([26, 184, 62, 210], 8, fill=BURGUNDY_L, outline=mul(BURGUNDY, 0.6))
    d.line([(24, 214), (20, 234)], fill=WOOD_D, width=2)
    d.line([(64, 214), (68, 234)], fill=WOOD_D, width=2)
    d.line([(34, 214), (32, 234)], fill=WOOD_D, width=2)
    d.line([(54, 214), (56, 234)], fill=WOOD_D, width=2)
    d.ellipse([72, 196, 96, 202], fill=GOLD_D)
    d.rectangle([80, 200, 88, 220], fill=WOOD_D)
    d.ellipse([70, 216, 98, 224], fill=WOOD)
    d.ellipse([76, 204, 92, 216], fill=hx("b7d2e3"))
    light(img, "ellipse", [24, 182, 64, 210], hx("ffd7d0"), 0.08, 6)


def dresser(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 404, 112, 464, 174
    d.rectangle([x0, y0, x1, y1], fill=mul(WOOD, 0.88))
    d.rectangle([x0, y0 - 6, x1, y0], fill=mul(WOOD, 1.06))
    for y in (118, 140):
        d.rectangle([x0 + 5, y, x1 - 5, y + 18], outline=WOOD_D)
        d.rectangle([x0 + 27, y + 7, x0 + 33, y + 10], fill=GOLD)
    d.rectangle([414, 88, 454, 108], fill=GOLD_D)
    d.rectangle([417, 91, 451, 105], fill=hx("b4c3c8"))
    d.line([(434, 91), (434, 105)], fill=GOLD)
    shadow(img, "rect", [402, 172, 468, 186], 0.4, 4)


def bed(img, unmade=False):
    d = ImageDraw.Draw(img)
    # bed frame and headboard stay identical across states
    d.rounded_rectangle([210, 58, 406, 102], 14, fill=BURGUNDY, outline=WOOD_D)
    d.rounded_rectangle([220, 66, 396, 96], 10, fill=BURGUNDY_L, outline=mul(BURGUNDY, 0.7))
    d.line([(308, 66), (308, 96)], fill=mul(BURGUNDY, 0.55))
    frame = [(198, 102), (418, 102), (438, 184), (178, 184)]
    foot = [(178, 184), (438, 184), (446, 202), (170, 202)]
    d.polygon(frame, fill=hx("d9c9b2"), outline=WOOD_D)
    d.polygon(foot, fill=mul(WOOD, 0.92), outline=WOOD_D)
    d.line([(178, 184), (438, 184)], fill=hx("f7efe2"))
    d.line([(186, 191), (430, 191)], fill=mul(WOOD, 1.08))
    for x in (196, 422):
        d.line([(x, 182), (x - 4, 208)], fill=WOOD_D, width=3)
    shadow(img, "ellipse", [180, 194, 444, 210], 0.44, 4)

    if not unmade:
        cover = [(204, 106), (412, 106), (430, 178), (186, 178)]
        d.polygon(cover, fill=GREEN_L, outline=mul(GREEN, 0.8))
        d.polygon([(210, 109), (406, 109), (414, 126), (202, 126)], fill=hx("f1e8d7"))
        d.line([(214, 122), (402, 122)], fill=hx("d9cfbd"))
        d.line([(206, 138), (422, 138)], fill=mul(GREEN, 0.78))
        d.line([(200, 154), (426, 154)], fill=mul(GREEN, 0.78))
        d.line([(194, 170), (430, 170)], fill=mul(GREEN, 0.78))
        d.polygon([(222, 96), (286, 96), (294, 118), (216, 118)], fill=hx("f6efdf"), outline=hx("c8baa3"))
        d.polygon([(320, 96), (384, 96), (392, 118), (314, 118)], fill=hx("f6efdf"), outline=hx("c8baa3"))
        d.polygon([(280, 110), (324, 110), (328, 124), (276, 124)], fill=hx("dcb897"), outline=hx("8e6b46"))
        light(img, "polygon", [(216, 108), (364, 108), (414, 178), (250, 178)], hx("fff4df"), 0.12, 8)
    else:
        d.polygon([(204, 106), (412, 106), (430, 178), (186, 178)], fill=hx("eee3d0"))
        d.polygon([(214, 108), (406, 108), (414, 128), (204, 128)], fill=hx("f7f0e3"))
        d.polygon([(250, 122), (408, 126), (430, 180), (248, 166), (214, 144)], fill=GREEN_L, outline=mul(GREEN, 0.76))
        d.polygon([(186, 156), (248, 138), (262, 176), (194, 178)], fill=GREEN_L, outline=mul(GREEN, 0.76))
        d.line([(238, 129), (286, 138), (306, 132), (336, 144)], fill=hx("d8ccb9"))
        d.line([(224, 140), (250, 151), (240, 163), (272, 170)], fill=hx("cbbca4"))
        d.line([(302, 138), (352, 154), (374, 148), (394, 160)], fill=hx("cbbca4"))
        d.polygon([(226, 98), (294, 94), (298, 118), (214, 122)], fill=hx("f3ead8"), outline=hx("c0b096"))
        d.polygon([(322, 98), (388, 104), (382, 126), (308, 120)], fill=hx("f3ead8"), outline=hx("c0b096"))
        d.line([(232, 106), (252, 112), (274, 104)], fill=hx("d4c6ae"))
        d.line([(330, 110), (354, 116), (374, 112)], fill=hx("d4c6ae"))
        light(img, "polygon", [(214, 108), (350, 108), (412, 170), (266, 178)], hx("fff6e7"), 0.1, 8)


def paint(unmade=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img)
    sconces(img)
    dresser(img)
    desk(img)
    armchair(img)
    bed(img, unmade)
    chandelier(img)
    light(img, "ellipse", [80, 18, 284, 116], hx("fff8eb"), 0.14, 18)
    img = tall(img, ceiling)
    vignette(img, 0.28, tint=(84, 62, 36), blur=34)
    return img


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("c8af87"), hx("eadcc2"))
    for x in range(0, W, 40):
        d.rectangle([x + 4, 4, x + 36, TOP - 5], outline=hx("e8d7b8"))
    d.line([(0, TOP - 3), (W, TOP - 3)], fill=GOLD_D)
    d.line([(0, TOP - 1), (W, TOP - 1)], fill=WOOD_D)
    d.ellipse([270, 2, 302, 16], fill=GOLD_D)
    d.ellipse([274, 5, 298, 15], fill=GOLD)
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
