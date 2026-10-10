"""Act 3 locations: the back of the Harrington mansion at night (kitchen door, alarm bell, coal bin), the dark kitchen,
Harrington senior's study, his bedroom, the prison visiting room, and the car on the outskirts road.

Like act2_rooms, each room is painted once per state and the state overlays are cut against the base so they line up
pixel-exactly at the printed top-left."""
import random
from PIL import Image, ImageDraw, ImageChops
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, palette_of, pixelize, save
from .act2_rooms import bricks, overlay

H = FULL_H


def moonlit(img, k=(110, 120, 180)):
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, k)))


def ashlar(img, box, col, seed, h=12, w=30):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    for row, y in enumerate(range(y0, y1, h)):
        off = (w // 2) if row % 2 else 0
        for x in range(x0 - off, x1, w):
            c = mul(col, rnd.uniform(0.9, 1.08))
            d.rectangle([max(x0, x + 1), y + 1, min(x1, x + w - 1), min(y1, y + h - 1)], fill=c)
    noise(img, box, 5, seed)


def tall_window(d, x0, y0, x1, y1, lit=False, fire=False):
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 5], fill=hx("c8c0ac"))
    glass = hx("f0a030") if fire else hx("d8b060") if lit else hx("141a2c")
    d.rectangle([x0, y0, x1, y1], fill=glass)
    if fire:
        for i in range(4):
            fx = x0 + 3 + i * (x1 - x0 - 6) // 3
            d.polygon([(fx - 4, y1), (fx, y0 + 8 + (i % 2) * 10), (fx + 4, y1)], fill=hx("fff0a0"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("c8c0ac"))
    for y in range(y0 + (y1 - y0) // 3, y1, (y1 - y0) // 3):
        d.line([(x0, y), (x1, y)], fill=hx("c8c0ac"))


# ------------------------------------------------------------------------------------------------ MANSION, BACK

BELL = (318, 62, 344, 92)
BIN_HOME = (396, 172, 446, 210)
BIN_MOVED = (306, 172, 356, 210)


def coal_bin(d, box):
    x0, y0, x1, y1 = box
    d.rectangle([x0, y0 + 8, x1, y1], fill=hx("4a3424"), outline=hx("1a120a"))
    d.polygon([(x0 - 2, y0 + 8), (x1 + 2, y0 + 8), (x1, y0), (x0, y0 + 4)], fill=hx("5a4030"), outline=hx("1a120a"))
    for x in range(x0 + 8, x1, 10):
        d.line([(x, y0 + 9), (x, y1 - 1)], fill=hx("3a2618"))
    d.rectangle([x0 + 4, y1 - 12, x1 - 4, y1 - 9], fill=hx("2a2a2e"))
    d.text((x0 + 12, y0 + 14), "COAL", fill=hx("8a7a5a"))


def paint_exterior(moved=False, wedged=False, opened=False, fire=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 40), hx("0a0c1c"), hx("1c2238"))
    rnd = random.Random(71)
    for _ in range(40):
        d.point((rnd.randint(0, W - 1), rnd.randint(0, 30)), fill=hx("8890b0"))
    # the back of the mansion: pale ashlar, a cornice, tall dark windows upstairs
    ashlar(img, (0, 20, W - 1, 210), hx("8e8676"), 72)
    d.rectangle([0, 16, W - 1, 24], fill=hx("a8a08c"))
    d.line([(0, 25), (W - 1, 25)], fill=hx("3a362e"))
    d.rectangle([0, 104, W - 1, 108], fill=hx("a49c88"))
    for x in (24, 108, 192, 372, 444):
        tall_window(d, x, 38, x + 26, 92, lit=(x == 444), fire=fire)
    for x in (40, 150):
        tall_window(d, x, 124, x + 36, 176, fire=fire)
    tall_window(d, 384, 124, 418, 160, fire=fire)
    # service door to the kitchen, under a heavy stone lintel, three steps down to the yard
    dx0, dy0, dx1, dy1 = 250, 120, 288, 200
    d.rectangle([dx0 - 8, dy0 - 10, dx1 + 8, dy0 - 1], fill=hx("b8b09c"), outline=hx("4a4436"))
    d.line([(dx0 - 8, dy0 - 1), (dx1 + 8, dy0 - 1)], fill=hx("2a261e"))
    if opened:
        d.rectangle([dx0, dy0, dx1, dy1], fill=hx("0a0806"))
        d.polygon([(dx0, dy0), (dx0 - 10, dy0 + 4), (dx0 - 10, dy1 + 2), (dx0, dy1)], fill=hx("3e4a3a"), outline=hx("141a12"))
    else:
        d.rectangle([dx0, dy0, dx1, dy1], fill=hx("3e4a3a"), outline=hx("141a12"))
        d.rectangle([dx0 + 5, dy0 + 6, dx1 - 5, dy0 + 34], outline=hx("26302a"))
        d.rectangle([dx0 + 5, dy0 + 42, dx1 - 5, dy1 - 6], outline=hx("26302a"))
        d.rectangle([dx1 - 8, dy0 + 40, dx1 - 5, dy0 + 44], fill=hx("b89a50"))
    for i in range(3):
        d.rectangle([dx0 - 6 - i * 3, dy1 + i * 4, dx1 + 6 + i * 3, dy1 + 4 + i * 4], fill=mix(hx("9a9484"), hx("6a665c"), i / 3))
    # the alarm: a wire from the door frame's top corner up the wall to a red bell box with its gong and hammer
    d.line([(dx1 + 2, dy0 - 1), (dx1 + 2, BELL[3] + 6), (BELL[0] + 13, BELL[3] + 6), (BELL[0] + 13, BELL[3])],
           fill=hx("1a1a1a"))
    bx0, by0, bx1, by1 = BELL
    d.rectangle([bx0 + 4, by0, bx1 - 4, by0 + 10], fill=hx("8a1a18"), outline=hx("2a0806"))
    d.ellipse([bx0, by0 + 8, bx1, by1], fill=hx("c8a040"), outline=hx("5a4010"))
    d.ellipse([bx0 + 9, by0 + 17, bx1 - 9, by1 - 9], fill=hx("8a6a20"))
    if wedged:
        # Micah's tie, jammed between the hammer and the gong
        d.polygon([(bx1 - 6, by0 + 12), (bx1 + 2, by0 + 14), (bx1 + 4, by1 + 8), (bx1, by1 + 10), (bx1 - 4, by0 + 18)],
                  fill=hx("7b1f2a"), outline=hx("3a0a10"))
    else:
        d.rectangle([bx1 - 4, by0 + 14, bx1 + 2, by0 + 16], fill=hx("3a3a3a"))
        d.ellipse([bx1, by0 + 12, bx1 + 5, by0 + 18], fill=hx("4a4a4a"))
    # the coal bin, shoved under the bell or still by the coal hole
    coal_bin(d, BIN_MOVED if moved else BIN_HOME)
    if not moved:
        d.rectangle([BIN_MOVED[0] + 6, 204, BIN_MOVED[2] - 6, 208], fill=hx("4a463c"))
    d.rectangle([452, 196, 476, 206], fill=hx("1a1816"), outline=hx("4a463c"))  # coal hole hatch
    # yard: flagstones, a low hedge and the garden gate on the left
    vgrad(img, (0, 210, W - 1, H - 1), hx("4a4a46"), hx("3a3a36"))
    for y in range(214, H, 14):
        off = 18 if (y // 14) % 2 else 0
        for x in range(-off, W, 36):
            d.rectangle([x + 1, y + 1, x + 35, y + 13], outline=hx("2a2a28"))
    noise(img, (0, 210, W - 1, H - 1), 6, 73)
    d.rectangle([0, 186, 26, 222], fill=hx("1e2a1a"))
    d.rectangle([4, 150, 22, 222], fill=hx("2a2620"))
    for x in range(6, 22, 4):
        d.line([(x, 152), (x, 220)], fill=hx("4a4436"))
    if fire:
        light(img, "ellipse", [-80, -40, W + 80, 230], hx("f08030"), 0.5, 30)
    moonlit(img, (150, 160, 210) if not fire else (230, 200, 190))
    light(img, "ellipse", [400, 20, 480, 110], hx("c89040"), 0.25, 14)
    vignette(img, 0.55, (8, 8, 20), 40)
    return img


def build_exterior():
    base = paint_exterior()
    v = {"moved": paint_exterior(moved=True), "wedged": paint_exterior(wedged=True), "open": paint_exterior(opened=True),
         "fire": paint_exterior(moved=True, wedged=True, opened=True, fire=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.3)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_exterior.png")
    overlay(v["moved"], px, pal, (300, 166, 452, 212), "mansion_exterior_bin")
    overlay(v["wedged"], px, pal, (BELL[0] - 2, BELL[1] - 2, BELL[2] + 8, BELL[3] + 14), "mansion_exterior_tie")
    overlay(v["open"], px, pal, (236, 116, 292, 204), "mansion_exterior_door")
    save(pixelize(v["fire"], palette_of(v["fire"], 124)), "rooms", "mansion_exterior_fire.png")


# ------------------------------------------------------------------------------------------------ KITCHEN

CANDLE = (318, 150)


def paint_kitchen(lit=False, gas=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # white tiles up to the dado, cream plaster above
    vgrad(img, (0, 0, W - 1, 200), hx("bcb4a0"), hx("a8a08c"))
    for y in range(110, 200, 8):
        for x in range(0, W, 8):
            d.rectangle([x, y, x + 7, y + 7], outline=hx("8a8676"))
    d.rectangle([0, 104, W - 1, 110], fill=hx("4a6a5a"))
    # back door on the left (to the yard) and the green baize door to the house on the right
    d.rectangle([24, 98, 72, 202], fill=hx("4a3a2a"), outline=hx("1a120a"))
    d.rectangle([30, 106, 66, 140], fill=hx("1a2236"))
    d.line([(48, 106), (48, 140)], fill=hx("4a3a2a"))
    d.rectangle([62, 152, 65, 158], fill=hx("b89a50"))
    d.rectangle([410, 96, 458, 202], fill=hx("2a4a32"), outline=hx("0e1a10"))
    for y in range(102, 200, 10):
        d.point((414, y), fill=hx("b89a50"))
        d.point((454, y), fill=hx("b89a50"))
    d.rectangle([416, 146, 419, 152], fill=hx("b89a50"))
    # the range: black cast iron, a hood, gas taps along the front
    d.rectangle([110, 52, 238, 70], fill=hx("2a2a2c"))
    d.polygon([(110, 70), (238, 70), (226, 96), (122, 96)], fill=hx("3a3a3e"))
    d.rectangle([118, 128, 230, 200], fill=hx("1a1a1c"), outline=hx("060606"))
    d.rectangle([114, 122, 234, 130], fill=hx("2e2e32"))
    for x in (126, 158, 190):
        d.rectangle([x, 144, x + 26, 168], fill=hx("26262a"), outline=hx("4a4a4e"))
        d.rectangle([x + 10, 154, x + 16, 158], fill=hx("8a8a8e"))
    d.rectangle([126, 174, 222, 194], fill=hx("26262a"), outline=hx("4a4a4e"))
    for i, x in enumerate(range(124, 230, 14)):
        on = gas and i < 4
        d.ellipse([x, 132, x + 6, 138], fill=hx("c8a040") if on else hx("8a8a8e"))
        d.line([(x + 3, 132), (x + (6 if on else 3), 135 if on else 132)], fill=hx("1a1a1a"))
    # copper pans on a rail
    d.line([(250, 70), (390, 70)], fill=hx("6a5a3a"), width=2)
    for i, x in enumerate(range(258, 386, 22)):
        r = 8 + (i % 3) * 2
        d.line([(x, 70), (x, 76)], fill=hx("6a5a3a"))
        d.ellipse([x - r, 76, x + r, 76 + 2 * r], fill=hx("b8683a"), outline=hx("6a3a1a"))
    # dresser with plates
    d.rectangle([250, 98, 388, 130], fill=hx("6a4a2a"), outline=hx("2a1a0a"))
    for x in range(256, 386, 14):
        d.ellipse([x, 104, x + 11, 115], fill=hx("e8e4d8"), outline=hx("8a8676"))
    # the big deal table, with a candlestick and a box of kitchen matches
    d.rectangle([260, 160, 384, 168], fill=hx("a8885a"), outline=hx("4a3a1a"))
    for x in (266, 374):
        d.rectangle([x, 168, x + 6, 204], fill=hx("7a6040"))
    cx, cy = CANDLE
    d.rectangle([cx - 4, cy + 6, cx + 4, cy + 10], fill=hx("c8a040"))
    d.rectangle([cx - 1, cy - 6, cx + 1, cy + 6], fill=hx("f0ead8"))
    d.rectangle([340, 156, 352, 160], fill=hx("c84030"), outline=hx("5a1a10"))
    # flagstone floor
    vgrad(img, (0, 200, W - 1, H - 1), hx("6a6458"), hx("54504a"))
    for y in range(204, H, 16):
        off = 20 if (y // 16) % 2 else 0
        for x in range(-off, W, 40):
            d.rectangle([x + 1, y + 1, x + 39, y + 15], outline=hx("3a3830"))
    noise(img, (0, 0, W - 1, H - 1), 4, 81)
    # dark: only the moon through the back door's glass, and the candle if it's lit
    moonlit(img, (70, 78, 120))
    light(img, "polygon", [(30, 106), (66, 106), (160, 268), (40, 268)], hx("3a4a80"), 0.3, 10)
    if lit:
        d.ellipse([cx - 2, cy - 12, cx + 2, cy - 6], fill=hx("fff0b0"))
        light(img, "ellipse", [cx - 90, cy - 70, cx + 90, cy + 90], hx("e0a050"), 0.55, 24)
        ImageDraw.Draw(img).ellipse([cx - 2, cy - 12, cx + 2, cy - 6], fill=hx("fff6c8"))
    vignette(img, 0.6, (6, 6, 16), 40)
    return img


def build_kitchen():
    base = paint_kitchen()
    v = {"lit": paint_kitchen(lit=True), "gas": paint_kitchen(gas=True)}
    pal = palette_of(Image.blend(Image.blend(base, v["lit"], 0.4), v["gas"], 0.3), 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_kitchen.png")
    overlay(v["gas"], px, pal, (118, 128, 234, 142), "mansion_kitchen_gas")
    overlay(v["lit"], px, pal, (CANDLE[0] - 100, CANDLE[1] - 80, CANDLE[0] + 100, CANDLE[1] + 100), "mansion_kitchen_candle")


# ------------------------------------------------------------------------------------------------ STUDY

def paint_study(left=False, right=False, docs=True, closet=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 200), hx("2a3a2e"), hx("1e2a22"))
    d.rectangle([0, 0, W - 1, 8], fill=hx("1a140c"))
    d.rectangle([0, 128, W - 1, 134], fill=hx("4a3220"))
    noise(img, (0, 0, W - 1, 200), 4, 91)
    # door to the kitchen passage (left) and to the bedroom (right)
    for x0, x1 in ((18, 64), (420, 466)):
        d.rectangle([x0 - 4, 82, x1 + 4, 204], fill=hx("5a3c22"))
        d.rectangle([x0, 88, x1, 204], fill=hx("3e2614"), outline=hx("140a04"))
        d.rectangle([x0 + 5, 94, x1 - 5, 140], outline=hx("2a1a0c"))
        d.rectangle([x0 + 5, 148, x1 - 5, 196], outline=hx("2a1a0c"))
        hx0 = x1 - 9 if x0 < 200 else x0 + 6
        d.rectangle([hx0, 144, hx0 + 3, 148], fill=hx("c8a858"))
    # bookcases
    rnd = random.Random(92)
    for bx0, bx1 in ((80, 150), (346, 404)):
        d.rectangle([bx0, 30, bx1, 202], fill=hx("3a2414"), outline=hx("140a04"))
        for y in range(40, 196, 26):
            d.rectangle([bx0 + 4, y, bx1 - 4, y + 22], fill=hx("1a0e06"))
            x = bx0 + 5
            while x < bx1 - 6:
                bw = rnd.randint(3, 6)
                c = rnd.choice(["6a1a1a", "1a3a2a", "2a2a4a", "6a5a2a", "4a2a1a", "8a7a5a"])
                d.rectangle([x, y + 22 - rnd.randint(14, 21), x + bw - 1, y + 21], fill=hx(c))
                x += bw + (1 if rnd.random() < 0.2 else 0)
    # a closet between bookcase and desk
    wx0, wx1, wy0, wy1 = 160, 214, 70, 204
    d.rectangle([wx0 - 3, wy0 - 5, wx1 + 3, wy0], fill=hx("4a2e18"))
    if closet:
        d.rectangle([wx0, wy0, wx1, wy1], fill=hx("120a06"), outline=hx("140a04"))
        d.line([(wx0 + 4, wy0 + 12), (wx1 - 4, wy0 + 12)], fill=hx("8a8a80"))
        for i, c in enumerate(("2a2a30", "5a1e26")):
            cx = wx0 + 16 + i * 22
            d.polygon([(cx - 8, wy0 + 16), (cx + 8, wy0 + 16), (cx + 10, wy0 + 90), (cx - 10, wy0 + 90)], fill=hx(c))
        d.rectangle([wx0 + 6, wy1 - 20, wx1 - 6, wy1 - 6], fill=hx("2a1e14"))
        d.polygon([(wx1, wy0), (wx1 + 12, wy0 + 5), (wx1 + 12, wy1 + 3), (wx1, wy1)], fill=hx("4a2e18"), outline=hx("140a04"))
    else:
        d.rectangle([wx0, wy0, wx1, wy1], fill=hx("3e2614"), outline=hx("140a04"))
        d.rectangle([wx0 + 6, wy0 + 8, wx1 - 6, wy0 + 64], outline=hx("1e1208"))
        d.rectangle([wx0 + 6, wy0 + 72, wx1 - 6, wy1 - 10], outline=hx("1e1208"))
        d.rectangle([wx1 - 10, 136, wx1 - 8, 144], fill=hx("c8a858"))
    # window with the moon, heavy drapes
    d.rectangle([236, 26, 324, 112], fill=hx("4a3220"))
    d.rectangle([242, 32, 318, 106], fill=hx("161c34"))
    d.ellipse([292, 40, 306, 54], fill=hx("e8e4c8"))
    d.rectangle([278, 32, 281, 106], fill=hx("4a3220"))
    d.rectangle([242, 66, 318, 69], fill=hx("4a3220"))
    d.polygon([(226, 20), (246, 20), (240, 120), (222, 124)], fill=hx("5a1a1e"))
    d.polygon([(314, 20), (334, 20), (338, 124), (320, 120)], fill=hx("5a1a1e"))
    # the desk: a pedestal of drawers each side
    d.rectangle([224, 150, 336, 158], fill=hx("6a4426"), outline=hx("1e1209"))
    d.rectangle([228, 158, 270, 204], fill=hx("4e321c"), outline=hx("1e1209"))
    d.rectangle([290, 158, 332, 204], fill=hx("4e321c"), outline=hx("1e1209"))
    for x0, opened in ((231, left), (293, right)):
        if opened:
            d.rectangle([x0 - 4, 168, x0 + 40, 188], fill=hx("6a4628"), outline=hx("1e1209"))
            d.rectangle([x0 - 2, 164, x0 + 38, 170], fill=hx("2a1a0e"))
            if x0 == 231:
                d.rectangle([x0 + 6, 165, x0 + 30, 168], fill=hx("6a3a20"))  # a cigar box
            elif docs:
                d.rectangle([x0 + 2, 164, x0 + 34, 169], fill=hx("c8b48a"))
                d.rectangle([x0 + 14, 164, x0 + 20, 166], fill=hx("a02020"))
        else:
            d.rectangle([x0, 164, x0 + 36, 182], outline=hx("2a1a0c"))
            d.rectangle([x0 + 14, 172, x0 + 22, 174], fill=hx("c8a858"))
        d.rectangle([x0, 186, x0 + 36, 200], outline=hx("2a1a0c"))
    d.rectangle([306, 132, 308, 150], fill=hx("8a7a3a"))
    d.polygon([(298, 132), (316, 132), (312, 124), (302, 124)], fill=hx("2a4a2a"))
    d.rectangle([248, 146, 282, 150], fill=hx("2a3a2a"))
    # carpet
    vgrad(img, (0, 200, W - 1, H - 1), hx("3a1a1a"), hx("4a2222"))
    d.rectangle([80, 214, 400, 262], outline=hx("7a5a2a"))
    noise(img, (0, 200, W - 1, H - 1), 5, 93)
    moonlit(img, (118, 128, 186))
    light(img, "polygon", [(242, 32), (318, 32), (380, 262), (200, 262)], hx("5a70b0"), 0.3, 14)
    vignette(img, 0.6, (8, 8, 22), 40)
    return img


def build_study():
    base = paint_study()
    v = {"left": paint_study(left=True), "right": paint_study(right=True), "empty": paint_study(right=True, docs=False),
         "closet": paint_study(closet=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.35)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_study.png")
    overlay(v["left"], px, pal, (222, 160, 276, 192), "mansion_study_drawer_left")
    overlay(v["right"], px, pal, (284, 160, 338, 192), "mansion_study_drawer_right")
    overlay(v["empty"], px, pal, (284, 160, 338, 192), "mansion_study_drawer_empty")
    overlay(v["closet"], px, pal, (150, 60, 232, 208), "mansion_study_closet")


# ------------------------------------------------------------------------------------------------ BEDROOM

def _eleanor_in_bed():
    """Eleanor sitting up against the pillows, bare shoulders; the sheet covers her from the chest down."""
    from .sprites import ELEANOR_SHEET, figure, pose, _arms, FW, FH
    f = figure(dict(ELEANOR_SHEET, torso="ecc4a2", decals=[]), pose(16, arms=_arms("fold")), FW, FH).convert("RGBA")
    f.putalpha(f.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    bb = f.getbbox()
    return f.crop((bb[0], bb[1], bb[2], bb[1] + 44))


def paint_bedroom(empty=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # damask walls, a picture rail, a dado
    vgrad(img, (0, 0, W - 1, 200), hx("4a2a30"), hx("3a2026"))
    rnd = random.Random(101)
    for y in range(20, 196, 16):
        for x in range((y // 16 % 2) * 12, W, 24):
            d.polygon([(x, y - 4), (x + 4, y), (x, y + 4), (x - 4, y)], fill=hx("56323a"))
    d.rectangle([0, 14, W - 1, 18], fill=hx("6a4a2a"))
    d.rectangle([0, 150, W - 1, 156], fill=hx("5a3a22"))
    d.rectangle([0, 156, W - 1, 200], fill=hx("3a2418"))
    noise(img, (0, 0, W - 1, 200), 4, 102)
    # door to the study (left) and the other door, to the landing (right)
    for x0, x1 in ((10, 52), (432, 474)):
        d.rectangle([x0 - 4, 84, x1 + 4, 204], fill=hx("6a4a2a"))
        d.rectangle([x0, 90, x1, 204], fill=hx("4a2e18"), outline=hx("140a04"))
        d.rectangle([x0 + 5, 96, x1 - 5, 142], outline=hx("2a1a0c"))
        d.rectangle([x0 + 5, 150, x1 - 5, 196], outline=hx("2a1a0c"))
    # fireplace with a low fire: the only warm light in the room
    d.rectangle([150, 104, 222, 200], fill=hx("c8c0b0"), outline=hx("4a4436"))
    d.rectangle([144, 98, 228, 106], fill=hx("dcd4c4"))
    d.rectangle([164, 140, 208, 200], fill=hx("140c08"))
    d.polygon([(170, 200), (178, 182), (186, 194), (192, 178), (200, 200)], fill=hx("e07028"))
    d.polygon([(178, 200), (186, 188), (192, 200)], fill=hx("f8d070"))
    d.rectangle([156, 60, 216, 96], fill=hx("b08a3a"))
    d.rectangle([160, 64, 212, 92], fill=hx("2a3a4a"))
    # the four-poster: headboard against the back wall, the canopy above
    bx0, bx1 = 262, 418
    d.rectangle([bx0 - 6, 30, bx1 + 6, 40], fill=hx("6a1a22"))
    for x in (bx0 - 4, bx1):
        d.rectangle([x, 30, x + 4, 206], fill=hx("3a2014"))
    d.polygon([(bx0 - 6, 40), (bx0 + 16, 40), (bx0 + 6, 150), (bx0 - 4, 150)], fill=hx("5a141c"))
    d.polygon([(bx1 - 14, 40), (bx1 + 6, 40), (bx1 + 4, 150), (bx1 - 4, 150)], fill=hx("5a141c"))
    d.rectangle([bx0 + 10, 92, bx1 - 10, 150], fill=hx("4a2a18"), outline=hx("1e1208"))
    d.rectangle([bx0 + 20, 100, bx1 - 20, 140], outline=hx("6a4a2a"))
    d.rectangle([bx0, 150, bx1, 200], fill=hx("6a1a22"), outline=hx("2a0a0e"))
    d.rectangle([bx0 + 4, 140, bx1 - 4, 176], fill=hx("ece8e0"))
    for px_ in (bx0 + 30, bx1 - 70):
        d.ellipse([px_, 128, px_ + 44, 150], fill=hx("f4f0e8"), outline=hx("c8c4bc"))
    if empty:
        # the sheet's gone with her: a bare mattress and a thrown-back blanket
        d.rectangle([bx0 + 4, 150, bx1 - 4, 176], fill=hx("d8d0bc"))
        d.polygon([(bx0 + 4, 168), (bx0 + 70, 160), (bx0 + 90, 176), (bx0 + 4, 180)], fill=hx("8a2a32"))
    else:
        el = _eleanor_in_bed()
        ex = bx1 - 70 + 22 - el.width // 2
        img.paste(el, (ex, 150 - el.height + 16), el)
        d = ImageDraw.Draw(img)
        d.polygon([(bx0 + 4, 156), (ex - 6, 154), (ex + 4, 150), (ex + el.width - 4, 150), (bx1 - 4, 154), (bx1 - 4, 178),
                   (bx0 + 4, 178)], fill=hx("ece8e0"))
        for i in range(4):
            d.line([(ex - 10 + i * 14, 156), (ex - 20 + i * 18, 176)], fill=hx("c8c4bc"))
    # folding screen, three panels, painted with herons
    sx = 74
    for i in range(3):
        x0 = sx + i * 22
        top = 96 + (i % 2) * 4
        d.polygon([(x0, top), (x0 + 22, top + (4 if i % 2 == 0 else -4)), (x0 + 22, 210), (x0, 210)], fill=hx("2a1a12"),
                  outline=hx("0e0806"))
        d.rectangle([x0 + 3, top + 6, x0 + 19, 202], fill=hx("c8b88a"))
        d.line([(x0 + 6, top + 50), (x0 + 12, top + 36), (x0 + 15, top + 40)], fill=hx("2a2a2a"))
        d.ellipse([x0 + 8, top + 42, x0 + 16, top + 52], fill=hx("e8e4d8"))
    # carpet
    vgrad(img, (0, 200, W - 1, H - 1), hx("2a1a3a"), hx("3a2448"))
    d.rectangle([40, 216, 440, 264], outline=hx("8a6a2a"))
    noise(img, (0, 200, W - 1, H - 1), 5, 103)
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, (150, 140, 170))))
    light(img, "ellipse", [80, 110, 300, 300], hx("e08040"), 0.45, 30)
    light(img, "ellipse", [250, 60, 440, 200], hx("a0a0c0"), 0.15, 20)
    vignette(img, 0.55, (10, 6, 16), 40)
    return img


def build_bedroom():
    base = paint_bedroom()
    empty = paint_bedroom(empty=True)
    pal = palette_of(Image.blend(base, empty, 0.4), 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_bedroom.png")
    overlay(empty, px, pal, (262, 80, 420, 200), "mansion_bedroom_empty")


# ------------------------------------------------------------------------------------------------ PRISON

SEAT_Y = 222  # the seated figures' soles
TABLE = (206, 190, 274, 226)


def paint_prison():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    bricks(img, (0, 0, W - 1, 200), hx("7a8474"), hx("5a6456"), 111, h=6, w=14)
    d.rectangle([0, 120, W - 1, 200], fill=hx("4a5a4a"))
    d.line([(0, 120), (W - 1, 120)], fill=hx("2a342a"), width=2)
    noise(img, (0, 120, W - 1, 200), 4, 112)
    # a high barred window throwing a grey square of daylight
    d.rectangle([200, 26, 280, 70], fill=hx("c8ccd0"))
    for x in range(206, 280, 10):
        d.line([(x, 26), (x, 70)], fill=hx("2a2a2a"), width=2)
    d.rectangle([196, 22, 284, 74], outline=hx("3a3a3a"))
    # steel door with a judas hole, and the guard's chair beside it
    d.rectangle([396, 78, 450, 204], fill=hx("5a5e62"), outline=hx("1e2022"))
    for y in range(86, 200, 12):
        d.line([(398, y), (448, y)], fill=hx("4a4e52"))
    d.rectangle([416, 104, 430, 110], fill=hx("141618"))
    d.rectangle([440, 140, 444, 150], fill=hx("2a2a2a"))
    d.text((330, 80), "NO TOUCHING", fill=hx("2a2a2a"))
    d.rectangle([326, 76, 402, 92], outline=hx("2a2a2a"))
    # a clock
    d.ellipse([90, 40, 118, 68], fill=hx("e8e4d8"), outline=hx("2a2a2a"))
    d.line([(104, 54), (104, 44)], fill=hx("1a1a1a"))
    d.line([(104, 54), (111, 57)], fill=hx("1a1a1a"))
    # concrete floor
    vgrad(img, (0, 200, W - 1, H - 1), hx("6a6a64"), hx("54544e"))
    noise(img, (0, 200, W - 1, H - 1), 6, 113)
    # the two chairs at the table: backs behind the sitters
    for x, back in ((196, 182), (284, 298)):
        d.rectangle([back - 2, 150, back + 2, SEAT_Y], fill=hx("3a2a1a"))
        d.rectangle([x - 14, SEAT_Y - 22, x + 14, SEAT_Y - 19], fill=hx("4a3624"))
        for lx in (x - 12, x + 10):
            d.rectangle([lx, SEAT_Y - 19, lx + 2, SEAT_Y], fill=hx("3a2a1a"))
    light(img, "polygon", [(200, 26), (280, 26), (330, 230), (170, 230)], hx("e0e4e8"), 0.25, 16)
    vignette(img, 0.5, (14, 16, 18), 40)
    return img


def paint_table():
    """Foreground: the visiting-room table, drawn over the sitters' laps."""
    img = Image.new("RGBA", (TABLE[2] - TABLE[0] + 1, TABLE[3] - TABLE[1] + 1), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = img.size
    d.rectangle([0, 0, w - 1, 5], fill=hx("7a5a3a", 255), outline=hx("2a1a0a", 255))
    d.line([(1, 1), (w - 2, 1)], fill=hx("9a7a52", 255))
    d.rectangle([2, 6, w - 3, 12], fill=hx("5a4028", 255))
    d.rectangle([w // 2 - 1, 6, w // 2 + 1, 18], fill=hx("2a2a2a", 255))  # the partition plank down the middle
    for x in (4, w - 8):
        d.rectangle([x, 12, x + 4, h - 1], fill=hx("4a3420", 255))
    return img


def build_prison():
    base = paint_prison()
    save(pixelize(base, n=110), "rooms", "prison.png")
    t = paint_table()
    save(t, "rooms", "prison_table.png")
    print("prison_table at", TABLE[:2])


# ------------------------------------------------------------------------------------------------ THE CAR

def paint_car():
    """A black 1920s sedan in profile, nose to the left; RGBA, wheels resting on the bottom row."""
    w, h = 124, 58
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body, dark, chrome = hx("1e2024", 255), hx("0e0e10", 255), hx("b8b8b0", 255)
    # cabin, a box with a slight rake, two side windows
    d.polygon([(40, 6), (108, 4), (112, 30), (36, 30)], fill=body, outline=dark)
    d.polygon([(46, 10), (72, 9), (72, 26), (44, 26)], fill=hx("5a6a7a", 255))
    d.polygon([(76, 9), (104, 8), (106, 26), (76, 26)], fill=hx("5a6a7a", 255))
    d.line([(46, 10), (60, 22)], fill=hx("8a9aa8", 255))
    # long hood, radiator, mudguards and running board
    d.rectangle([4, 26, 116, 42], fill=body, outline=dark)
    d.rectangle([2, 18, 10, 40], fill=chrome)
    d.rectangle([4, 20, 8, 38], fill=hx("4a4a48", 255))
    d.ellipse([8, 20, 16, 28], fill=hx("e8e0b0", 255), outline=chrome)
    d.pieslice([10, 30, 50, 60], 180, 360, fill=body, outline=dark)
    d.pieslice([78, 30, 118, 60], 180, 360, fill=body, outline=dark)
    d.rectangle([44, 42, 84, 45], fill=hx("2e2e30", 255))
    d.line([(54, 18), (56, 18)], fill=chrome)
    d.rectangle([60, 22, 63, 23], fill=chrome)  # door handle
    d.line([(74, 9), (74, 42)], fill=dark)
    for cx in (30, 98):
        d.ellipse([cx - 13, h - 27, cx + 13, h - 1], fill=hx("141414", 255))
        d.ellipse([cx - 7, h - 21, cx + 7, h - 7], fill=hx("c8b880", 255))
        for i in range(8):
            import math
            a = i * math.pi / 4
            d.line([(cx, h - 14), (cx + 6 * math.cos(a), h - 14 + 6 * math.sin(a))], fill=hx("6a5a3a", 255))
        d.ellipse([cx - 2, h - 16, cx + 2, h - 12], fill=chrome)
    d.rectangle([110, 22, 118, 26], fill=hx("6a1a10", 255))  # tail lamp
    return img


def build_car():
    save(paint_car(), "sprites", "car.png")


def build():
    build_exterior()
    build_kitchen()
    build_study()
    build_bedroom()
    build_prison()
    build_car()
