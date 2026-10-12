"""The Blue Lantern: a smoky mob-run speakeasy below a laundry."""
from PIL import Image, ImageDraw
import random
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, cut, floor_boards)

FLOOR = 134
BLUE = hx("4a8ae8")


def bricks(img, box, c1, c2, mortar, seed=31):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=mortar)
    rnd = random.Random(seed)
    for r, y in enumerate(range(y0, y1, 6)):
        off = 0 if r % 2 else 6
        for x in range(x0 - off, x1, 12):
            d.rectangle([max(x0, x), y, min(x1, x + 10), min(y1, y + 4)], fill=mix(c1, c2, rnd.random()))
    noise(img, box, 6, seed)


def vestibule(img):
    d = ImageDraw.Draw(img)
    bricks(img, (0, 0, 140, FLOOR), hx("5a2a1e"), hx("3a1a14"), hx("1e1410"))
    # steel door back up to the street
    d.rectangle([18, 46, 78, 133], fill=hx("1a1a1e"))
    vgrad(img, (22, 50, 74, 133), hx("4a4e54"), hx("2a2c30"))
    for y in (60, 96, 124):
        for x in range(26, 72, 8):
            d.point((x, y), fill=hx("8a8e94"))
    d.rectangle([40, 62, 56, 68], fill=hx("101014"))  # peephole slot
    d.rectangle([64, 88, 68, 98], fill=hx("6a6e74"))
    # bare bulb
    d.line([(90, 0), (90, 20)], fill=hx("1a1a1a"))
    d.ellipse([86, 20, 94, 30], fill=hx("fff0b0"))
    light(img, "ellipse", [40, -10, 140, 100], hx("f0c070"), 0.4, 16)
    # crates and empty bottles
    for (cx, cy, w, h) in ((96, 106, 30, 28), (102, 86, 22, 20)):
        d.rectangle([cx, cy, cx + w, cy + h], fill=hx("6a4a28"))
        d.rectangle([cx, cy, cx + w, cy + h], outline=hx("2a1a0c"))
        d.line([(cx, cy), (cx + w, cy + h)], fill=hx("4a3018"))
        d.line([(cx + 2, cy + 2), (cx + w - 2, cy + 2)], fill=hx("8a6a3a"))
    text(img, (107, 121), "SOAP", hx("2a1a0c"), size=8)
    for x in (100, 106, 112):
        d.rectangle([x, 80, x + 3, 86], fill=hx("2a5a2a"))
        d.rectangle([x + 1, 77, x + 2, 80], fill=hx("2a5a2a"))
    shadow(img, "rect", [0, FLOOR - 6, 140, FLOOR], 0.4, 3)


def curtain(img):
    d = ImageDraw.Draw(img)
    d.rectangle([136, 0, 182, FLOOR], fill=hx("1a0c0c"))
    for x in range(140, 180, 4):
        c = hx("7a1420") if (x // 4) % 2 else hx("4a0a14")
        d.rectangle([x, 8, x + 3, FLOOR], fill=c)
    d.rectangle([134, 0, 184, 8], fill=hx("a08030"))
    d.chord([150, 4, 170, 14], 0, 180, fill=hx("a08030"))
    light(img, "rect", [140, 8, 150, FLOOR], hx("ff8060"), 0.15, 3)


def main_room(img):
    d = ImageDraw.Draw(img)
    x0 = 182
    vgrad(img, (x0, 0, W - 1, FLOOR), hx("1a2034"), hx("101420"))
    # dark wood wainscot and wallpaper diamonds
    for y in range(6, 90, 12):
        for x in range(x0 + ((y // 12) % 2) * 6, W, 12):
            d.polygon([(x, y), (x + 4, y + 6), (x, y + 12), (x - 4, y + 6)], fill=hx("1e2640"))
    vgrad(img, (x0, 94, W - 1, FLOOR), hx("2a1a14"), hx("160c08"))
    d.line([(x0, 94), (W, 94)], fill=hx("6a5020"))
    # neon sign
    d.rectangle([340, 8, 476, 26], fill=hx("0a0c18"))
    text(img, (408, 17), "BLUE LANTERN", hx("a8d0ff"), size=8)
    light(img, "rect", [334, 2, 482, 32], BLUE, 0.5, 8)


def stage(img):
    d = ImageDraw.Draw(img)
    d.polygon([(184, 112), (236, 112), (236, 132), (184, 132)], fill=hx("3a2014"))
    d.line([(184, 112), (236, 112)], fill=hx("8a6030"))
    # backdrop drape + spotlight
    for x in range(186, 234, 4):
        d.rectangle([x, 20, x + 3, 112], fill=hx("2a3a6a") if (x // 4) % 2 else hx("1a2448"))
    light(img, "polygon", [(205, 0), (215, 0), (236, 112), (186, 112)], hx("c0d8ff"), 0.35, 6)
    # microphone
    d.line([(210, 78), (210, 112)], fill=hx("a0a0a8"))
    d.ellipse([207, 72, 213, 80], fill=hx("c8c8d0"))
    d.line([(206, 112), (214, 112)], fill=hx("a0a0a8"))


def piano(img):
    d = ImageDraw.Draw(img)
    d.rectangle([240, 82, 288, 120], fill=hx("16100e"))
    d.rectangle([240, 82, 288, 85], fill=hx("3a2a20"))
    d.rectangle([243, 96, 285, 100], fill=hx("e8e4d8"))
    for x in range(244, 285, 3):
        d.line([(x, 96), (x, 98)], fill=hx("16100e"))
    d.rectangle([244, 120, 247, 133], fill=hx("16100e"))
    d.rectangle([281, 120, 284, 133], fill=hx("16100e"))
    d.rectangle([258, 76, 270, 82], fill=hx("e0d8c0"))  # sheet music
    d.rectangle([252, 118, 276, 124], fill=hx("2a1a14"))  # stool
    light(img, "rect", [240, 82, 250, 120], hx("8090c0"), 0.2, 2)


def back_door(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 292, 52, 326, 133
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1], fill=hx("0e0a08"))
    vgrad(img, (x0, y0, x1, y1), hx("2a4a34"), hx("16281c"))
    d.rectangle([x0 + 4, y0 + 6, x1 - 4, y0 + 34], outline=hx("102018"))
    d.rectangle([x0 + 4, y0 + 42, x1 - 4, y1 - 6], outline=hx("102018"))
    text(img, ((x0 + x1) // 2, y0 + 20), "PRIVATE", hx("c0a050"), size=8)
    d.ellipse([x1 - 9, 92, x1 - 5, 96], fill=hx("c0a050"))
    light(img, "rect", [x0, y1 - 2, x1, y1 + 4], hx("f0c060"), 0.4, 2)


def bar(img):
    d = ImageDraw.Draw(img)
    # back shelves with bottles and a mirror
    d.rectangle([338, 28, 478, 94], fill=hx("2a1a12"))
    vgrad(img, (344, 32, 472, 54), hx("3a4a5a"), hx("1e2630"))
    rnd = random.Random(5)
    for sy in (58, 76):
        d.rectangle([340, sy + 14, 476, sy + 16], fill=hx("5a3a20"))
        x = 344
        while x < 472:
            h = rnd.randint(8, 13)
            col = rnd.choice([hx("6a3a14"), hx("2a5a2a"), hx("8a6a2a"), hx("4a2a4a"), hx("a8a8b0")])
            d.rectangle([x, sy + 14 - h, x + 3, sy + 13], fill=col)
            d.rectangle([x + 1, sy + 14 - h - 3, x + 2, sy + 14 - h], fill=col)
            d.point((x, sy + 15 - h), fill=mul(col, 1.6))
            x += rnd.randint(5, 8)
    light(img, "rect", [338, 28, 478, 94], BLUE, 0.15, 6)
    # bar counter (foreground layer)
    d.rectangle([334, 96, 480, 102], fill=hx("4a2a18"))
    d.line([(334, 96), (480, 96)], fill=hx("a07040"))
    vgrad(img, (338, 103, 480, 140), hx("3a2014"), hx("1e100a"))
    for x in range(346, 480, 22):
        d.rectangle([x, 108, x + 16, 134], outline=hx("2a160c"))
        d.line([(x + 1, 109), (x + 15, 109)], fill=hx("5a3622"))
    d.line([(336, 136), (480, 136)], fill=hx("b08a40"), width=2)  # brass foot rail
    # glasses on the counter
    for x in (356, 448):
        d.rectangle([x, 90, x + 4, 96], fill=hx("a8b0b8"))
        d.rectangle([x + 1, 92, x + 3, 95], fill=hx("c08030"))
    shadow(img, "rect", [334, 138, 480, 150], 0.5, 4)


def lanterns(img):
    d = ImageDraw.Draw(img)
    for x in (210, 300, 380):
        d.line([(x, 0), (x, 30)], fill=hx("101010"))
        d.polygon([(x - 6, 30), (x + 6, 30), (x + 4, 44), (x - 4, 44)], fill=hx("6aa8ff"))
        d.line([(x - 6, 30), (x + 6, 30)], fill=hx("202020"), width=2)
        d.line([(x, 30), (x, 44)], fill=hx("2a4a8a"))
        light(img, "ellipse", [x - 40, 0, x + 40, 90], BLUE, 0.45, 14)


def tables(img):
    d = ImageDraw.Draw(img)
    for (x, y) in ((214, 152), (300, 162)):
        shadow(img, "ellipse", [x - 20, y + 18, x + 20, y + 26], 0.6, 3)
        d.ellipse([x - 16, y - 4, x + 16, y + 4], fill=hx("2a1a12"))
        d.ellipse([x - 16, y - 5, x + 16, y + 2], fill=hx("e0dcd0"))
        d.line([(x, y + 2), (x, y + 20)], fill=hx("1a100a"), width=2)
        d.line([(x - 6, y + 21), (x + 6, y + 21)], fill=hx("1a100a"))
        d.rectangle([x - 4, y - 8, x - 1, y - 2], fill=hx("a8b0b8"))
        d.ellipse([x + 3, y - 4, x + 9, y - 1], fill=hx("3a3a40"))
        d.point((x + 8, y - 4), fill=hx("ff6020"))


def haze(img):
    rnd = random.Random(77)
    for _ in range(14):
        x, y = rnd.randint(150, 480), rnd.randint(10, 120)
        light(img, "ellipse", [x - 40, y - 8, x + 40, y + 8], hx("6070a0"), 0.18, 8)


def paint():
    img = Image.new("RGB", (W, H))
    main_room(img)
    floor_boards(img, FLOOR, H - 1, (300, -300), 16, hx("2a1c16"), hx("1e140e"), hx("0e0806"), 9)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 33)
    d = ImageDraw.Draw(img)
    # the path from the curtain to the bar is worn pale; the corners stay black with spilled beer
    d.polygon([(196, FLOOR + 6), (268, FLOOR + 2), (310, H - 1), (214, H - 1)], fill=hx("3a281c"))
    for y in range(FLOOR + 12, H - 4, 8):
        d.line([(188, y), (292, y + 2)], fill=hx("4a3424"))
    for box in ((210, 168, 248, 176), (250, 190, 286, 198), (40, 200, 78, 210)):
        d.ellipse(box, fill=hx("1a100c"))
    d.ellipse([236, 176, 252, 184], fill=hx("6a5030"))
    vestibule(img)
    curtain(img)
    stage(img)
    piano(img)
    back_door(img)
    bar(img)
    lanterns(img)
    haze(img)
    light(img, "ellipse", [20, FLOOR - 10, 140, H], hx("f0c070"), 0.18, 16)
    img = tall(img, ceiling)
    vignette(img, 0.6, tint=(10, 10, 30))
    return img


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (182, 0, W - 1, TOP), hx("0a0c14"), hx("1a2034"))
    bricks(img, (0, 0, 136, TOP), hx("4a2218"), hx("2e1410"), hx("180f0c"), seed=35)
    d.rectangle([136, 0, 182, TOP], fill=hx("120808"))
    # floor joists of the laundry upstairs
    for x in range(-10, W, 34):
        d.rectangle([x, 0, x + 8, 5], fill=hx("2a1c14"))
        d.line([(x, 5), (x + 8, 5)], fill=hx("120a06"))
    # pipes: cold water, steam, and a dripping waste pipe
    d.rectangle([0, 8, W - 1, 11], fill=hx("3a3c42"))
    d.line([(0, 8), (W, 8)], fill=hx("6a6e76"))
    d.rectangle([0, 16, W - 1, 20], fill=hx("5a3a26"))
    d.line([(0, 16), (W, 16)], fill=hx("8a5a3a"))
    for x in range(30, W, 96):
        d.rectangle([x, 6, x + 3, 13], fill=hx("2a2c30"))
        d.rectangle([x + 40, 14, x + 44, 22], fill=hx("3a2416"))
    d.line([(260, 20), (260, 24)], fill=hx("6a8ab0"))
    for x in (90, 210, 300, 380):
        d.line([(x, 0), (x, TOP)], fill=hx("101010"))
    for x in (210, 300, 380):
        light(img, "ellipse", [x - 36, 0, x + 36, 80], BLUE, 0.35, 12)
    light(img, "ellipse", [40, 0, 140, 80], hx("f0c070"), 0.3, 14)


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "speakeasy.png")
    mask = Image.new("L", (W, H + TOP), 0)
    ImageDraw.Draw(mask).rectangle([334, 88 + TOP, 480, 140 + TOP], fill=255)
    save(cut(px, mask), "rooms", "speakeasy_fg.png")
    return px
