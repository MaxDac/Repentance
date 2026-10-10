"""The Aurelian: a gleaming art-deco hotel lobby."""
from PIL import Image, ImageDraw
import math
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, cut, frieze, sunburst)

FLOOR = 138
GOLD, GOLD_D, CREAM = hx("d8b050"), hx("8a6a28"), hx("e8dcc0")


def walls(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("d8c8a4"), hx("b8a684"))
    noise(img, (0, 0, W - 1, FLOOR), 3, 21)
    # ceiling coffer band + chevron frieze
    vgrad(img, (0, 0, W - 1, 10), hx("3a2a1a"), hx("5a4228"))
    frieze(d, 10, 17, hx("2a1e14"), GOLD, step=8)
    d.line([(0, 18), (W, 18)], fill=GOLD_D)
    # fluted wall panels
    for x in range(0, W, 24):
        d.line([(x, 20), (x, FLOOR - 26)], fill=hx("c4b290"))
        d.line([(x + 1, 20), (x + 1, FLOOR - 26)], fill=hx("ece0c4"))
    # black marble dado with gold strip
    vgrad(img, (0, FLOOR - 24, W - 1, FLOOR), hx("2a2428"), hx("161216"))
    d.line([(0, FLOOR - 25), (W, FLOOR - 25)], fill=GOLD)
    noise(img, (0, FLOOR - 24, W - 1, FLOOR), 5, 22)
    for x in range(0, W, 40):
        d.line([(x + 5, FLOOR - 20), (x + 20, FLOOR - 4)], fill=hx("3a3238"))


def floor(img):
    d = ImageDraw.Draw(img)
    vx, vy = 240, -200
    rows, y, step = [], float(FLOOR), 6.0
    while y < H:
        rows.append(y)
        y += step
        step *= 1.12
    rows.append(H)

    def xat(xb, yy):
        return vx + (xb - vx) * (yy - vy) / (H - vy)

    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        for i in range(-30, 31):
            xa, xb2 = vx + i * 20, vx + (i + 1) * 20
            col = hx("d8ccb0") if (i + r) % 2 == 0 else hx("2a2a30")
            d.polygon([(xat(xa, ya), ya), (xat(xb2, ya), ya), (xat(xb2, yb), yb), (xat(xa, yb), yb)], fill=col)
    noise(img, (0, FLOOR, W - 1, H - 1), 6, 23)
    # gold inlay border and polish reflections
    d.line([(0, FLOOR + 2), (W, FLOOR + 2)], fill=GOLD_D)
    light(img, "ellipse", [180, FLOOR, 300, H], hx("fff4d0"), 0.25, 14)
    light(img, "ellipse", [300, FLOOR, 380, 180], hx("fff0c0"), 0.2, 10)


def plaque_and_cubbies(img):
    d = ImageDraw.Draw(img)
    d.rectangle([28, 20, 128, 36], fill=hx("1e1a14"))
    d.rectangle([30, 22, 126, 34], outline=GOLD)
    text(img, (78, 28), "THE AURELIAN", GOLD, size=8)
    d.rectangle([22, 40, 134, 92], fill=hx("4a2e1a"))
    for r in range(4):
        for c in range(8):
            x, y = 26 + c * 13, 43 + r * 12
            d.rectangle([x, y, x + 10, y + 9], fill=hx("2a180c"))
            if (r * 3 + c) % 4 == 1:
                d.rectangle([x + 2, y + 4, x + 8, y + 9], fill=hx("e0d8c0"))
            if (r + c) % 5 == 2:
                d.line([(x + 5, y + 1), (x + 5, y + 6)], fill=GOLD)
                d.point((x + 5, y + 7), fill=GOLD)


def desk(img, d=None):
    d = d or ImageDraw.Draw(img)
    vgrad(img, (14, 104, 142, 150), hx("3a2414"), hx("1e120a"))
    d.rectangle([10, 98, 146, 104], fill=hx("1e1a20"))
    d.line([(10, 98), (146, 98)], fill=hx("6a6070"))
    d.line([(10, 104), (146, 104)], fill=GOLD)
    sunburst(d, 78, 150, 34, 14, hx("6a4424"), hx("4a2c16"))
    for x in (20, 136):
        d.rectangle([x - 3, 106, x + 3, 150], fill=hx("2a1a10"))
        d.line([(x, 106), (x, 150)], fill=GOLD_D)
    d.line([(14, 150), (142, 150)], fill=GOLD)
    # bell, ledger, lamp
    d.chord([116, 92, 126, 102], 180, 360, fill=GOLD)
    d.point((121, 91), fill=GOLD)
    d.polygon([(40, 96), (64, 96), (66, 98), (38, 98)], fill=hx("e0d8c0"))
    d.line([(52, 96), (52, 98)], fill=hx("6a1a1a"))
    d.rectangle([92, 82, 94, 97], fill=GOLD_D)
    d.polygon([(86, 82), (100, 82), (96, 74), (90, 74)], fill=hx("f0e0b0"))


def elevator(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 196, 60, 274, 137
    d.rectangle([x0 - 6, y0 - 22, x1 + 6, y1], fill=hx("2a2018"))
    sunburst(d, (x0 + x1) // 2, y0 - 2, 34, 16, GOLD, hx("a8822e"))
    d.rectangle([x0 - 6, y0 - 4, x1 + 6, y0], fill=GOLD_D)
    # floor indicator dial
    d.chord([222, 32, 248, 52], 180, 360, fill=hx("1e1a14"), outline=GOLD)
    d.line([(235, 42), (241, 35)], fill=hx("e04040"))
    # brass doors with geometric pattern
    for dx0, dx1 in ((x0, (x0 + x1) // 2 - 1), ((x0 + x1) // 2 + 1, x1)):
        hgrad(img, (dx0, y0 + 2, dx1, y1), hx("c8a050"), hx("8a6a2a"))
        cx = (dx0 + dx1) // 2
        for k in range(4):
            yy = y0 + 14 + k * 16
            d.polygon([(cx, yy), (cx + 8, yy + 8), (cx, yy + 16), (cx - 8, yy + 8)], outline=hx("5a4418"))
    d.line([((x0 + x1) // 2, y0 + 2), ((x0 + x1) // 2, y1)], fill=hx("2a1e10"), width=2)
    light(img, "rect", [x0, y0, x0 + 14, y1], hx("fff4c0"), 0.25, 3)


def pilaster(img, x):
    d = ImageDraw.Draw(img)
    hgrad(img, (x - 6, 18, x + 6, FLOOR), hx("f0e6d0"), hx("a89878"))
    for k in range(3):
        d.line([(x - 3 + k * 3, 24), (x - 3 + k * 3, FLOOR - 28)], fill=hx("b8a888"))
    d.rectangle([x - 8, 18, x + 8, 24], fill=GOLD)
    d.polygon([(x - 8, 24), (x + 8, 24), (x, 32)], fill=GOLD_D)
    d.rectangle([x - 8, FLOOR - 26, x + 8, FLOOR], fill=hx("1e1a20"))
    d.line([(x - 8, FLOOR - 26), (x + 8, FLOOR - 26)], fill=GOLD)


def palm(img, x, base):
    d = ImageDraw.Draw(img)
    d.polygon([(x - 9, base - 18), (x + 9, base - 18), (x + 6, base), (x - 6, base)], fill=hx("2a2a30"))
    d.line([(x - 9, base - 15), (x + 9, base - 15)], fill=GOLD)
    d.line([(x, base - 18), (x + 1, base - 40)], fill=hx("4a3a20"), width=2)
    for i in range(9):
        a = math.pi + i * math.pi / 8
        top = base - 40
        mx, my = x + 10 * math.cos(a), top + 9 * math.sin(a) - 4
        ex, ey = x + 20 * math.cos(a), top + 5 * math.sin(a) + 5
        col = hx("2e6a3a") if i % 2 else hx("1e4a2a")
        d.line([(x, base - 40), (mx, my), (ex, ey)], fill=col, width=3)
    shadow(img, "ellipse", [x - 12, base - 2, x + 12, base + 4], 0.5, 2)


def chandelier(img, x):
    d = ImageDraw.Draw(img)
    d.line([(x, 0), (x, 24)], fill=GOLD_D)
    for k, w in enumerate((18, 13, 8)):
        y = 24 + k * 7
        d.polygon([(x - w, y), (x + w, y), (x + w - 4, y + 6), (x - w + 4, y + 6)], fill=GOLD, outline=GOLD_D)
        for xx in range(x - w + 2, x + w - 1, 4):
            d.line([(xx, y + 6), (xx, y + 10)], fill=hx("f0f0ff"))
    light(img, "ellipse", [x - 70, -20, x + 70, 90], hx("fff0c0"), 0.45, 18)


def urn(img):
    d = ImageDraw.Draw(img)
    d.rectangle([352, 116, 360, 150], fill=hx("2a2428"))
    d.ellipse([346, 108, 366, 118], fill=hx("c0a050"))
    d.ellipse([349, 110, 363, 115], fill=hx("4a4048"))
    d.rectangle([348, 148, 364, 152], fill=GOLD_D)
    shadow(img, "ellipse", [344, 150, 372, 156], 0.45, 2)


def revolving_door(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 394, 30, 478, 137
    d.rectangle([x0 - 4, y0 - 6, x1 + 2, y1], fill=hx("2a2018"))
    d.rectangle([x0 - 4, y0 - 6, x1 + 2, y0], fill=GOLD_D)
    text(img, ((x0 + x1) // 2, y0 - 2), "STATE ST", hx("1e1a14"), size=8)
    # night street outside glows blue through glass
    vgrad(img, (x0 + 2, y0 + 2, x1 - 2, y1), hx("1a2440"), hx("2a2a3a"))
    for k in range(18):
        x = x0 + 6 + (k * 37) % (x1 - x0 - 10)
        y = y0 + 8 + (k * 53) % 70
        d.line([(x, y), (x - 1, y + 3)], fill=hx("4a5a7a"))
    d.ellipse([x0 + 10, 50, x0 + 16, 56], fill=hx("f0d890"))  # street lamp
    light(img, "ellipse", [x0 + 4, 44, x0 + 22, 62], hx("f0c060"), 0.4, 4)
    for xx in (x0 + 2, (x0 + x1) // 2, x1 - 2):
        d.line([(xx, y0), (xx, y1)], fill=GOLD, width=2)
    d.line([(x0 + 26, y0 + 4), (x0 + 26, y1 - 2)], fill=hx("8a6a28"), width=3)
    d.line([(x1 - 22, y0 + 4), (x1 - 22, y1 - 2)], fill=hx("6a5020"), width=2)
    d.line([(x0 + 2, 96), (x1 - 2, 96)], fill=GOLD, width=2)
    light(img, "rect", [x0, y0, x1, y1], hx("6080c0"), 0.12, 4)


def service_door(img):
    """Plain staff door to the service elevator, tucked between the palm and the urn."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 312, 66, 342, 137
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1], fill=hx("8a7a5a"))
    vgrad(img, (x0, y0, x1, y1), hx("c8b894"), hx("a89874"))
    d.rectangle([x0, y0, x1, y1], outline=hx("6a5a3a"))
    for py0, py1 in ((y0 + 5, y0 + 30), (y0 + 36, y1 - 6)):
        d.rectangle([x0 + 4, py0, x1 - 4, py1], outline=hx("8a7a5a"))
        d.line([(x0 + 5, py0 + 1), (x1 - 5, py0 + 1)], fill=hx("e0d4b4"))
    d.rectangle([x0 + 3, y0 + 14, x1 - 3, y0 + 21], fill=hx("2a2018"))
    text(img, ((x0 + x1) // 2, y0 + 18), "STAFF", GOLD, size=6)
    d.ellipse([x1 - 7, 102, x1 - 3, 106], fill=GOLD)
    shadow(img, "rect", [x0, y1 - 2, x1, y1], 0.4, 2)


def paint(include_desk=True):
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    plaque_and_cubbies(img)
    for x in (146, 300, 384):
        pilaster(img, x)
    elevator(img)
    service_door(img)
    palm(img, 172, 140)
    palm(img, 290, 140)
    urn(img)
    revolving_door(img)
    chandelier(img, 340)
    chandelier(img, 172)
    if include_desk:
        desk(img)
    light(img, "polygon", [(0, 0), (W, 0), (W, 60), (0, 60)], hx("fff8e0"), 0.1, 20)
    img = tall(img, ceiling)
    vignette(img, 0.4, tint=(40, 30, 40))
    return img


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("1e140c"), hx("3a2a1a"))
    # coffered ceiling with gold rosettes
    for x in range(-8, W, 40):
        d.rectangle([x + 3, 2, x + 36, TOP - 4], fill=hx("2a1e12"), outline=GOLD_D)
        d.rectangle([x + 6, 5, x + 33, TOP - 7], outline=hx("4a3620"))
        cx = x + 20
        sunburst(d, cx, 14, 6, 8, GOLD_D, hx("5a4220"), 0, 2 * math.pi)
        d.point((cx, 14), fill=GOLD)
    d.line([(0, TOP - 2), (W, TOP - 2)], fill=GOLD_D)
    for x in (340, 172):
        d.ellipse([x - 7, 0, x + 7, 6], fill=GOLD_D)
        d.line([(x, 0), (x, TOP)], fill=GOLD_D)
        light(img, "ellipse", [x - 60, -10, x + 60, 70], hx("fff0c0"), 0.3, 14)


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "lobby.png")
    mask = Image.new("L", (W, H + TOP), 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([10, 98 + TOP, 146, 152 + TOP], fill=255)
    md.rectangle([86, 74 + TOP, 100, 98 + TOP], fill=255)
    md.rectangle([114, 90 + TOP, 128, 98 + TOP], fill=255)
    md.rectangle([36, 94 + TOP, 68, 98 + TOP], fill=255)
    save(cut(px, mask), "rooms", "lobby_fg.png")
    return px
