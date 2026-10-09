"""A cheap roadside motel room in flat, dingy daytime light."""
from PIL import Image, ImageDraw
from .common import (W, H, TOP, tall, hx, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of, save,
                     floor_boards)

FLOOR = 136
WOOD = hx("6a5038")
WOOD_D = hx("342418")


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
        [(44, 30), (70, 26), (84, 42), (78, 65), (56, 70), (40, 52)],
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
    d = ImageDraw.Draw(img)
    rug = [(148, 162), (292, 162), (316, 198), (128, 198)]
    d.polygon(rug, fill=hx("666046"))
    d.polygon([(156, 166), (286, 166), (306, 194), (138, 194)], outline=hx("968460"))
    for y in range(170, 194, 5):
        d.line([(144, y), (302, y)], fill=hx("575139"))
    noise(img, (128, 162, 316, 198), 7, 407)
    for x in (72, 76, 80, 392, 396):
        d.line([(x, 160), (x + 20, 238)], fill=hx("433224"))


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
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 46, 74, 194, 146
    shadow(img, "ellipse", [40, 144, 204, 156], 0.5, 4)
    # iron frame
    for x in (52, 186):
        d.line([(x, 62), (x, 146)], fill=hx("2a2422"), width=3)
        d.point((x, 60), fill=hx("8e8470"))
    d.line([(52, 68), (186, 68)], fill=hx("3a302c"), width=3)
    d.line([(52, 82), (186, 82)], fill=hx("3a302c"), width=2)
    for x in range(64, 178, 18):
        d.line([(x, 68), (x, 82)], fill=hx("5e5448"))

    d.rectangle([58, 82, 180, 142], fill=hx("b7ae95"))
    hgrad(img, (58, 82, 180, 142), hx("bfb59a"), hx("968c73"))
    d.rectangle([58, 82, 180, 142], outline=hx("5a4b3a"))
    noise(img, (58, 82, 180, 142), 4, 409)

    if not unmade:
        d.polygon([(60, 98), (180, 98), (174, 142), (66, 142)], fill=hx("6f7558"))
        d.line([(60, 104), (180, 104)], fill=hx("8c9270"))
        d.line([(70, 140), (170, 140)], fill=hx("5b6148"))
        d.rectangle([68, 84, 118, 98], fill=hx("d5ccb3"))
        d.line([(72, 90), (114, 90)], fill=hx("b7ad96"))
        light(img, "polygon", [(60, 98), (120, 98), (114, 142), (66, 142)], hx("aab08a"), 0.12, 4)
    else:
        d.polygon([(58, 98), (170, 98), (152, 116), (182, 132), (166, 144), (72, 144), (62, 132)], fill=hx("d4cab1"))
        d.polygon([(82, 102), (180, 102), (176, 126), (136, 122), (144, 142), (90, 140), (74, 120)], fill=hx("6d7355"))
        d.polygon([(66, 84), (116, 82), (126, 97), (72, 102)], fill=hx("d7cfb8"))
        d.line([(74, 90), (108, 88)], fill=hx("b3aa94"))
        d.line([(94, 108), (148, 116)], fill=hx("c8bea5"))
        d.line([(118, 124), (154, 136)], fill=hx("4f5640"))
        d.line([(150, 100), (176, 114)], fill=hx("8b916c"))
        shadow(img, "polygon", [(136, 122), (182, 132), (166, 144), (144, 142)], 0.18, 3)
    d.rectangle([58, 142, 180, 146], fill=hx("4c3a2a"))


def nightstand(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 208, 94, 244, 138
    vgrad(img, (x0, y0, x1, y1), hx("674b35"), hx("453021"))
    d.rectangle([x0, y0, x1, y1], outline=hx("23170f"))
    d.rectangle([x0 + 3, y0 + 4, x1 - 3, y0 + 18], outline=hx("302014"))
    d.rectangle([x0 + 3, y0 + 24, x1 - 3, y1 - 4], outline=hx("302014"))
    d.rectangle([x0 + 15, 112, x0 + 21, 114], fill=hx("ac8a4a"))
    d.rectangle([x0 + 15, 128, x0 + 21, 130], fill=hx("ac8a4a"))
    d.rectangle([214, 88, 230, 94], fill=hx("a79d86"))
    d.line([(216, 90), (228, 90)], fill=hx("6b6458"))
    shadow(img, "rect", [206, 138, 248, 148], 0.45, 3)


def chair(img):
    d = ImageDraw.Draw(img)
    shadow(img, "ellipse", [316, 150, 382, 160], 0.45, 3)
    d.line([(330, 104), (326, 152)], fill=hx("3a281b"), width=3)
    d.line([(360, 104), (364, 152)], fill=hx("3a281b"), width=3)
    d.line([(330, 104), (360, 104)], fill=hx("533825"), width=4)
    d.line([(334, 118), (356, 118)], fill=hx("63422c"), width=3)
    d.line([(338, 104), (338, 152)], fill=hx("4a321f"), width=2)
    d.line([(352, 104), (352, 152)], fill=hx("4a321f"), width=2)
    d.polygon([(324, 150), (366, 150), (374, 162), (318, 162)], fill=hx("6a4830"))
    d.line([(330, 150), (326, 188)], fill=hx("352216"), width=3)
    d.line([(360, 150), (364, 188)], fill=hx("352216"), width=3)
    d.line([(334, 154), (340, 188)], fill=hx("40291a"), width=2)
    d.line([(352, 154), (348, 188)], fill=hx("40291a"), width=2)
    d.line([(326, 174), (364, 174)], fill=hx("4a311f"))
    d.line([(338, 112), (352, 144)], fill=hx("2a1c12"))


def dresser(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 404, 92, 466, 142
    hgrad(img, (x0, y0, x1, y1), hx("5c4733"), hx("342518"))
    d.rectangle([x0, y0, x1, y1], outline=hx("1e130c"))
    for y in (98, 114, 130):
        d.rectangle([x0 + 4, y, x1 - 4, y + 12], outline=hx("2a1a10"))
        d.line([(x0 + 5, y + 1), (x1 - 5, y + 1)], fill=hx("72563d"))
        d.rectangle([x0 + 26, y + 5, x0 + 34, y + 7], fill=hx("b28a46"))
    noise(img, (x0, y0, x1, y1), 4, 410)
    shadow(img, "rect", [402, 142, 470, 152], 0.5, 3)


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
    d.polygon([(246, 34), (286, 32), (288, 62), (244, 64)], fill=hx("6c5237"))
    d.polygon([(250, 36), (282, 35), (284, 59), (248, 60)], fill=hx("cabf9f"))
    d.rectangle([254, 40, 278, 54], fill=hx("8a8f6b"))
    d.rectangle([254, 50, 278, 54], fill=hx("7f684b"))
    d.line([(255, 42), (266, 47), (276, 41)], fill=hx("9ea47f"))
    d.line([(252, 62), (280, 60)], fill=hx("2c2018"))
    # Scuffs and grime around the baseboards
    for x in range(18, W, 28):
        d.line([(x, FLOOR - 8), (x + 8, FLOOR - 4)], fill=hx("271b13"))
    for (x, y) in ((264, 146), (278, 154), (292, 164), (418, 152)):
        d.ellipse([x, y, x + 10, y + 4], fill=hx("4a392b"))


def paint(unmade=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img)
    bed(img, unmade)
    nightstand(img)
    chair(img)
    dresser(img)
    details(img)
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
