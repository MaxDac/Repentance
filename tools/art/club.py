"""A secretive private club: velvet booths, lounge, and a shadowy stage room."""
from PIL import Image, ImageDraw
from .common import (W, H, TOP, FULL_H, tall, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize,
                     palette_of, save, floor_boards)

FLOOR = 146
WALL_TOP = hx("241117")
WALL_MID = hx("34161d")
WALL_LOW = hx("24100f")
WOOD = hx("5a3320")
WOOD_DARK = hx("24140c")
WOOD_DEEP = hx("180d08")
VELVET = hx("6e1620")
VELVET_DARK = hx("38070e")
BRASS = hx("b68c42")
LAMPLIGHT = hx("f0c272")


def ceiling_band(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("13080c"), WALL_TOP)
    d.rectangle([0, 0, W - 1, 3], fill=WOOD_DEEP)
    d.rectangle([0, 4, W - 1, 6], fill=WOOD)
    d.line([(0, 4), (W, 4)], fill=mul(WOOD, 1.2))
    d.rectangle([0, 8, W - 1, TOP], fill=hx("1c0d11"))
    for x in range(0, W, 28):
        d.rectangle([x, 0, x + 10, 6], fill=hx("20120e"))
    for x in range(0, W, 10):
        d.line([(x, 10), (x, TOP)], fill=hx("1a0c10"))
    noise(img, (0, 0, W - 1, TOP), 4, 701)


def panel_wall(img, floor_y, seed):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, floor_y), WALL_MID, WALL_LOW)
    d.rectangle([0, 92, W - 1, floor_y], fill=WOOD_DARK)
    d.line([(0, 91), (W, 91)], fill=WOOD)
    d.line([(0, floor_y), (W, floor_y)], fill=WOOD_DEEP)
    for x in range(6, W, 36):
        d.rectangle([x, 98, min(W - 6, x + 28), floor_y - 7], outline=hx("3a2216"))
        d.line([(x + 1, 99), (min(W - 7, x + 27), 99)], fill=mul(WOOD, 1.1))
    for y in range(8, 90, 12):
        for x in range((y // 12) % 2 * 8, W, 16):
            d.polygon([(x, y + 5), (x + 5, y), (x + 10, y + 5), (x + 5, y + 10)], fill=hx("3a1a20"))
    noise(img, (0, 0, W - 1, floor_y), 4, seed)


def room_shell(img, floor_y, vp, seed):
    d = ImageDraw.Draw(img)
    panel_wall(img, floor_y, seed)
    d.polygon([(0, 0), (112, 0), (156, floor_y), (0, floor_y)], fill=hx("18090d"))
    d.polygon([(W - 113, 0), (W - 1, 0), (W - 1, floor_y), (324, floor_y)], fill=hx("18090d"))
    d.polygon([(108, 0), (W - 109, 0), (324, floor_y), (156, floor_y)], fill=mul(WALL_MID, 1.08))
    d.line([(156, floor_y), (324, floor_y)], fill=mul(WOOD, 0.8))
    floor_boards(img, floor_y, H - 1, vp, 18, hx("4a2a1a"), hx("2e180f"), hx("150907"), seed + 10)
    noise(img, (0, floor_y, W - 1, H - 1), 5, seed + 20)


def drape(img, box, seed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for x in range(x0, x1, 4):
        col = VELVET if (x // 4) % 2 else VELVET_DARK
        d.rectangle([x, y0, min(x1, x + 3), y1], fill=col)
    d.rectangle([x0, y0 - 3, x1, y0], fill=BRASS)
    light(img, "rect", [x0, y0, x0 + 6, y1], hx("ff9070"), 0.15, 3)
    noise(img, (x0, y0, x1, y1), 3, seed)


def lamp(full_img, x, top_y, pool_box, cone_box=None):
    d = ImageDraw.Draw(full_img)
    d.line([(x, 0), (x, top_y - 9)], fill=WOOD_DEEP)
    d.polygon([(x - 8, top_y - 9), (x + 8, top_y - 9), (x + 6, top_y + 3), (x - 6, top_y + 3)], fill=BRASS)
    d.line([(x - 7, top_y - 8), (x + 7, top_y - 8)], fill=mul(BRASS, 1.2))
    d.ellipse([x - 3, top_y - 3, x + 3, top_y + 3], fill=LAMPLIGHT)
    if cone_box:
        x0, y0, x1, y1 = cone_box
        light(full_img, "polygon", [(x - 2, top_y + 1), (x + 2, top_y + 1), (x1, y1), (x0, y1)], LAMPLIGHT, 0.18, 10)
    light(full_img, "ellipse", pool_box, LAMPLIGHT, 0.38, 16)


def booth(img, box, side, curtain_frac=0.35, seed=0):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], 7, fill=hx("110708"), outline=WOOD_DEEP)
    vgrad(img, (x0 + 4, y0 + 4, x1 - 4, y1 - 8), hx("271017"), hx("14080b"))
    drw = int((x1 - x0) * curtain_frac)
    if side == "left":
        drape(img, (x0 + 4, y0 + 4, x0 + drw, y1 - 8), seed + 1)
    else:
        drape(img, (x1 - drw, y0 + 4, x1 - 4, y1 - 8), seed + 1)
    seat_y = y1 - 20
    d.rectangle([x0 + 10, seat_y, x1 - 10, y1 - 9], fill=VELVET_DARK)
    d.rounded_rectangle([x0 + 10, seat_y - 14, x1 - 10, seat_y + 3], 5, fill=VELVET)
    for px in range(x0 + 18, x1 - 12, 12):
        d.point((px, seat_y - 5), fill=BRASS)
    t0 = x0 + 18 if side == "left" else x0 + 10
    t1 = x1 - 10 if side == "left" else x1 - 18
    d.ellipse([t0, y1 - 18, t1, y1 - 10], fill=WOOD_DEEP)
    d.ellipse([t0 + 1, y1 - 18, t1 - 1, y1 - 12], fill=mul(WOOD, 0.9))
    cx = (x0 + x1) // 2
    d.line([(cx, y1 - 13), (cx, y1 - 3)], fill=WOOD_DEEP)
    d.line([(cx - 5, y1 - 3), (cx + 5, y1 - 3)], fill=WOOD_DEEP)
    d.rectangle([cx - 12, y1 - 23, cx - 9, y1 - 16], fill=hx("9aa0a6"))
    d.ellipse([cx + 5, y1 - 20, cx + 13, y1 - 16], fill=hx("322a2a"))
    shadow(img, "ellipse", [x0 + 5, y1 - 1, x1 - 5, y1 + 9], 0.5, 4)


def sofa(img, box, seed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], 9, fill=VELVET_DARK, outline=WOOD_DEEP)
    d.rounded_rectangle([x0 + 4, y0 - 16, x1 - 4, y0 + 8], 8, fill=VELVET)
    d.rounded_rectangle([x0 - 4, y0 - 10, x0 + 10, y1], 6, fill=VELVET)
    d.rounded_rectangle([x1 - 10, y0 - 10, x1 + 4, y1], 6, fill=VELVET)
    for px in range(x0 + 10, x1 - 8, 14):
        d.point((px, y0 - 4), fill=BRASS)
    noise(img, (x0, y0 - 16, x1, y1), 3, seed)
    shadow(img, "ellipse", [x0 + 4, y1 - 1, x1 - 4, y1 + 8], 0.45, 4)


def low_table(img, box, seed, glasses=2):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.ellipse([x0, y0, x1, y0 + 7], fill=WOOD_DEEP)
    d.ellipse([x0 + 1, y0, x1 - 1, y0 + 5], fill=mul(WOOD, 0.95))
    cx = (x0 + x1) // 2
    d.line([(cx, y0 + 5), (cx, y1)], fill=WOOD_DEEP, width=2)
    d.line([(cx - 7, y1), (cx + 7, y1)], fill=WOOD_DEEP)
    for i in range(glasses):
        gx = x0 + 8 + i * 10
        d.rectangle([gx, y0 - 6, gx + 3, y0], fill=hx("a0a6ad"))
        d.rectangle([gx + 1, y0 - 4, gx + 2, y0 - 1], fill=hx("b47028"))
    noise(img, (x0, y0, x1, y1), 2, seed)


def hall_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, FLOOR, (240, -250), 101)
    d = ImageDraw.Draw(img)
    d.polygon([(208, 26), (272, 26), (290, 82), (190, 82)], fill=hx("16090c"))
    drape(img, (214, 30, 266, 82), 109)
    d.rectangle([228, 38, 252, 47], fill=hx("10080a"))
    d.line([(234, 43), (246, 43)], fill=BRASS)
    booths = [
        ((18, 82, 118, 146), "left", 86),
        ((64, 48, 138, 104), "left", 122),
        ((342, 48, 416, 104), "right", 356),
        ((362, 82, 462, 146), "right", 394),
    ]
    for i, (box, side, _) in enumerate(booths):
        booth(img, box, side, 0.38 if i in (0, 3) else 0.32, 120 + i * 7)
    d.polygon([(194, 146), (286, 146), (320, H - 1), (160, H - 1)], fill=hx("2c1115"))
    d.polygon([(202, 150), (278, 150), (306, H - 1), (174, H - 1)], outline=BRASS)
    light(img, "ellipse", [180, 144, 300, 226], hx("7a1d24"), 0.16, 18)
    shadow(img, "ellipse", [150, 148, 330, H - 1], 0.2, 10, hx("40181a"))
    full = tall(img, ceiling_band)
    for box, _, lx in booths:
        _, y0, _, y1 = box
        lamp(full, lx, TOP + 14, [lx - 42, TOP + y0 - 2, lx + 42, TOP + y1 + 36], (lx - 22, TOP + y0, lx + 22, TOP + y1))
    shadow(full, "rect", [0, TOP + 132, W - 1, FULL_H - 1], 0.16, 12, hx("502124"))
    vignette(full, 0.72, tint=(38, 14, 18), blur=52)
    return full


def lounge_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, FLOOR, (240, -230), 201)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([12, 62, 60, 142], 5, fill=hx("100609"), outline=WOOD_DEEP)
    d.rounded_rectangle([420, 54, 468, 146], 5, fill=hx("100609"), outline=WOOD_DEEP)
    drape(img, (436, 58, 464, 142), 211)
    sofa(img, (68, 136, 174, 162), 220)
    sofa(img, (306, 136, 412, 162), 221)
    sofa(img, (180, 112, 300, 138), 222)
    sofa(img, (150, 164, 238, 190), 223)
    sofa(img, (242, 164, 330, 190), 224)
    d.polygon([(152, 152), (328, 152), (356, 205), (124, 205)], fill=hx("4a141b"))
    d.polygon([(162, 156), (318, 156), (342, 198), (138, 198)], outline=BRASS)
    for x in (108, 240, 372):
        d.line([(x, 86), (x, 124)], fill=hx("1c0c10"))
        d.rectangle([x - 12, 82, x + 12, 86], fill=BRASS)
    for box in ([40, 46, 170, 138], [310, 46, 440, 138], [176, 54, 304, 138]):
        light(img, "ellipse", box, LAMPLIGHT, 0.2, 18)
    light(img, "ellipse", [146, 96, 338, 178], hx("9a2830"), 0.1, 16)
    shadow(img, "rect", [0, 0, 56, FLOOR], 0.22, 10, hx("20090c"))
    shadow(img, "rect", [W - 56, 0, W - 1, FLOOR], 0.22, 10, hx("20090c"))
    full = tall(img, ceiling_band)
    for x, pool in ((108, [60, TOP + 72, 158, TOP + 190]), (240, [182, TOP + 44, 298, TOP + 164]),
                    (372, [322, TOP + 72, 420, TOP + 190])):
        lamp(full, x, TOP + 10, pool, (x - 18, TOP + 82, x + 18, TOP + 126))
    vignette(full, 0.68, tint=(34, 12, 18), blur=50)
    return full


def stage_backdrop(img):
    d = ImageDraw.Draw(img)
    d.polygon([(156, 40), (324, 40), (346, 110), (134, 110)], fill=hx("110708"))
    drape(img, (168, 44, 312, 110), 301)
    d.polygon([(184, 110), (296, 110), (314, 132), (166, 132)], fill=WOOD_DARK)
    d.line([(184, 110), (296, 110)], fill=mul(WOOD, 1.1))
    d.polygon([(196, 114), (284, 114), (298, 128), (182, 128)], fill=hx("311418"))


def seating_row(img, y, width, height, inset, col):
    d = ImageDraw.Draw(img)
    x0 = inset
    x1 = W - inset
    seat_w = max(10, int(width / 7))
    gap = max(3, int(seat_w * 0.22))
    x = x0
    while x + seat_w <= x1:
        d.rounded_rectangle([x, y, x + seat_w, y + height], 3, fill=col)
        d.rectangle([x + 2, y + height - 4, x + seat_w - 2, y + height + 2], fill=mul(col, 0.75))
        x += seat_w + gap


def stage_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, 136, (240, -180), 320)
    d = ImageDraw.Draw(img)
    stage_backdrop(img)
    for i, y in enumerate((84, 102, 120, 140, 162, 186)):
        col = mix(hx("251114"), hx("080405"), i / 5)
        seating_row(img, y, 264 - i * 24, 10 + max(0, 4 - i), 74 + i * 10, col)
    d.polygon([(0, 136), (W - 1, 136), (W - 1, H - 1), (0, H - 1)], fill=hx("12070a"))
    d.polygon([(168, 132), (312, 132), (362, H - 1), (118, H - 1)], fill=hx("1c0b0f"))
    for x in range(120, 360, 12):
        d.line([(x, 160), (x - 12, 230)], fill=hx("18080c"))
    shadow(img, "rect", [0, 72, W - 1, H - 1], 0.26, 18, hx("22090c"))
    full = tall(img, ceiling_band)
    lamp(full, 240, TOP + 4, [176, TOP + 62, 304, TOP + 190], (210, TOP + 38, 270, TOP + 160))
    light(full, "polygon", [(236, TOP + 10), (244, TOP + 10), (282, TOP + 162), (198, TOP + 162)], hx("fff0c2"), 0.34, 9)
    light(full, "ellipse", [186, TOP + 102, 294, TOP + 172], hx("f8d28a"), 0.32, 12)
    light(full, "ellipse", [182, TOP + 110, 298, TOP + 148], hx("a8242a"), 0.12, 10)
    vignette(full, 0.82, tint=(26, 8, 12), blur=58)
    shadow(full, "rect", [0, TOP + 144, W - 1, H + TOP], 0.12, 20, hx("160609"))
    return full


def build():
    hall = hall_scene()
    lounge = lounge_scene()
    stage = stage_scene()
    pal = palette_of(Image.blend(Image.blend(hall, lounge, 0.5), stage, 0.4), 128)
    out = {
        "club_hall.png": pixelize(hall, pal),
        "club_lounge.png": pixelize(lounge, pal),
        "club_stage.png": pixelize(stage, pal),
    }
    for name, img in out.items():
        save(img, "rooms", name)
    return out["club_hall.png"]
