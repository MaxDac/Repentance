"""Outskirts of Chicago: open fields, hedgerow, road, and a distant skyline under a heavy sky."""
from PIL import Image, ImageDraw
import random
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save

HORIZON = 116


def sky(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, HORIZON + 18), hx("6c7686"), hx("d2ccb8"))
    for y in range(8, HORIZON - 6, 10):
        c = mix(hx("7a8392"), hx("c8c0ae"), y / max(1, HORIZON))
        d.line([(0, y), (W - 1, y)], fill=mul(c, 0.92 if y < 54 else 0.96))
    for box, col, k, blur in (
        ([18, 18, 220, 76], hx("bcc0c4"), 0.22, 14),
        ([180, 12, 388, 68], hx("d2d4d0"), 0.18, 18),
        ([286, 28, 474, 84], hx("b9c0c7"), 0.22, 16),
        ([70, 56, 428, 112], hx("e0d5ba"), 0.1, 24),
    ):
        light(img, "ellipse", box, col, k, blur)
    shadow(img, "ellipse", [-40, -14, 250, 88], 0.16, 18, hx("4a5060"))
    shadow(img, "ellipse", [180, 4, 520, 90], 0.18, 22, hx("4c5462"))
    noise(img, (0, 0, W - 1, HORIZON + 18), 4, 301)


def skyline(img, x0=170, y_base=HORIZON + 2, width=110, seed=19):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    haze = hx("7d7a78")
    d.rectangle([x0 - 8, y_base - 2, x0 + width + 8, y_base + 3], fill=mix(haze, hx("8e876e"), 0.25))
    x = x0
    while x < x0 + width:
        bw = rnd.randint(3, 9)
        bh = rnd.randint(6, 18)
        top = y_base - bh
        col = rnd.choice([hx("48484e"), hx("3d3f46"), hx("55535a")])
        d.rectangle([x, top, min(x0 + width, x + bw), y_base], fill=col)
        if rnd.random() < 0.22:
            cap = rnd.randint(2, 5)
            d.rectangle([x + 1, top - cap, min(x0 + width, x + bw - 1), top], fill=col)
            if rnd.random() < 0.45:
                cx = min(x0 + width, x + bw // 2)
                d.line([(cx, top - cap - 4), (cx, top - cap)], fill=col)
        x += bw + rnd.randint(1, 3)
    light(img, "rect", [x0 - 18, y_base - 20, x0 + width + 22, y_base + 8], hx("cbbca0"), 0.08, 12)


def distant_fields(img):
    d = ImageDraw.Draw(img)
    d.polygon([(0, HORIZON), (W, HORIZON), (W, 150), (0, 144)], fill=hx("6f7754"))
    d.polygon([(0, 132), (W, 126), (W, 140), (0, 147)], fill=hx("8a815e"))
    d.polygon([(0, HORIZON + 4), (148, HORIZON + 2), (248, 128), (0, 140)], fill=hx("73744d"))
    d.polygon([(248, 128), (W, 124), (W, 144), (280, 146)], fill=hx("7f7650"))
    for pts, col in (
        ([(0, 140), (170, 130), (252, 141), (0, 156)], hx("5f6848")),
        ([(252, 141), (W, 132), (W, 156), (274, 154)], hx("706d49")),
    ):
        d.polygon(pts, fill=col)
    noise(img, (0, HORIZON, W - 1, 158), 5, 302)


def road(img):
    d = ImageDraw.Draw(img)
    left = [(228, HORIZON + 1), (262, HORIZON + 1), (334, FULL_H - 1), (160, FULL_H - 1)]
    d.polygon(left, fill=hx("8a785f"))
    d.polygon([(239, HORIZON + 8), (257, HORIZON + 8), (308, FULL_H - 1), (190, FULL_H - 1)], fill=hx("958168"))
    d.line([(245, HORIZON + 8), (208, FULL_H - 1)], fill=hx("6b5f4e"))
    d.line([(255, HORIZON + 7), (291, FULL_H - 1)], fill=hx("6b5f4e"))
    for y in range(HORIZON + 18, FULL_H, 12):
        w = (y - HORIZON) * 0.32
        d.line([(240 - w, y), (258 + w, y)], fill=hx("a18f74"))
    noise(img, (158, HORIZON, 336, FULL_H - 1), 9, 303)
    shadow(img, "polygon", [(214, HORIZON + 12), (246, HORIZON + 6), (184, FULL_H), (126, FULL_H)], 0.14, 10, hx("4e5242"))


def hedge(img, seed=41):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    base_y = 150
    pts = [(-20, 154)]
    for x in range(-20, W + 25, 14):
        y = base_y + rnd.randint(-8, 8) - int(abs(x - 250) / 95)
        if 220 < x < 294:
            y += 18
        pts.append((x, y))
    pts += [(W + 20, 202), (-20, 202)]
    d.polygon(pts, fill=hx("2c4228"))
    for _ in range(260):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(138, 196)
        if 214 < x < 302 and y < 170:
            continue
        r = rnd.randint(2, 5)
        col = rnd.choice([hx("314b2b"), hx("3b582f"), hx("243a22"), hx("4a6338")])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
    for x in range(18, W, 34):
        top = 146 + rnd.randint(-8, 5)
        d.line([(x, 190), (x + rnd.randint(-2, 2), top)], fill=hx("1f2919"))
    noise(img, (0, 136, W - 1, 202), 9, 304)
    shadow(img, "rect", [0, 156, W - 1, 210], 0.18, 8, hx("22301f"))
    light(img, "ellipse", [40, 134, 250, 178], hx("6f7b50"), 0.12, 16)


def foreground(img, seed=53):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    vgrad(img, (0, 154, W - 1, FULL_H - 1), hx("6d7148"), hx("4f5636"))
    d.polygon([(0, 168), (144, 158), (196, 182), (0, FULL_H)], fill=hx("60663f"))
    d.polygon([(304, 158), (W, 166), (W, FULL_H), (270, 188)], fill=hx("5c613b"))
    d.polygon([(0, 192), (124, 174), (188, FULL_H), (0, FULL_H)], fill=hx("56603a"))
    d.polygon([(320, 176), (W, 190), (W, FULL_H), (286, FULL_H)], fill=hx("545c37"))
    for _ in range(460):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(156, FULL_H - 1)
        if 166 < x < 338 and y > 170:
            continue
        col = rnd.choice([hx("657043"), hx("76804b"), hx("49522f"), hx("857752")])
        d.line([(x, y), (x + rnd.randint(-2, 2), y - rnd.randint(2, 8))], fill=col)
    noise(img, (0, 154, W - 1, FULL_H - 1), 10, 305)
    light(img, "ellipse", [220, 148, 410, 252], hx("b8a476"), 0.09, 22)


def paint():
    img = Image.new("RGB", (W, FULL_H))
    sky(img)
    skyline(img)
    distant_fields(img)
    road(img)
    foreground(img)
    hedge(img)
    shadow(img, "ellipse", [-20, 190, 180, 278], 0.12, 22, hx("384028"))
    light(img, "ellipse", [230, 120, 480, 250], hx("d4bc88"), 0.08, 28)
    return img


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    vignette(px, 0.58, tint=(22, 24, 30), blur=42)
    save(px, "rooms", "outskirts.png")
    return px
