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
    for (cx, cy, w, h, brace) in ((96, 106, 30, 28, False), (102, 86, 22, 20, True)):
        d.rectangle([cx, cy, cx + w, cy + h], fill=hx("6a4a28"))
        for py in range(cy + 7, cy + h, 7):
            d.line([(cx + 1, py), (cx + w - 1, py)], fill=hx("4a3018"))
        d.rectangle([cx, cy, cx + w, cy + h], outline=hx("2a1a0c"))
        d.rectangle([cx + 1, cy + 1, cx + 2, cy + h - 1], fill=hx("5a3c20"))
        d.rectangle([cx + w - 2, cy + 1, cx + w - 1, cy + h - 1], fill=hx("5a3c20"))
        if brace:
            d.line([(cx + 3, cy + 1), (cx + w - 3, cy + h - 1)], fill=hx("4a3018"))
        d.line([(cx + 2, cy + 2), (cx + w - 2, cy + 2)], fill=hx("8a6a3a"))
    # stencilled label, centred on the lower crate face
    text(img, (96 + 15, 106 + 15), "SOAP", hx("2a1a0c"), size=8)
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
    d.rectangle([343, 11, 473, 23], outline=hx("4a8ae8"))
    d.rectangle([345, 13, 471, 21], outline=hx("1a2a4a"))
    d.line([(404, 13), (412, 13)], fill=hx("a8d0ff"))
    d.polygon([(403, 15), (413, 15), (411, 21), (405, 21)], outline=hx("a8d0ff"))
    d.line([(408, 15), (408, 21)], fill=hx("6aa8ff"))
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


GLYPHS = {
    "P": ("111", "101", "111", "100", "100"),
    "R": ("111", "101", "110", "101", "101"),
    "I": ("1", "1", "1", "1", "1"),
    "V": ("101", "101", "101", "101", "010"),
    "A": ("010", "101", "111", "101", "101"),
    "T": ("111", "010", "010", "010", "010"),
    "E": ("111", "100", "110", "100", "111"),
}


def tiny_text(d, x, y, s, col):
    for ch in s:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    d.point((x + c, y + r), fill=col)
        x += len(g[0]) + 1


def plaque(d, cx, cy):
    """Small brass nameplate that sits well inside the door's upper panel."""
    word = "PRIVATE"
    tw = sum(len(GLYPHS[ch][0]) + 1 for ch in word) - 1
    x0, y0 = cx - tw // 2 - 2, cy - 4
    d.rectangle([x0, y0, x0 + tw + 3, y0 + 8], fill=hx("8a6a2a"))
    d.rectangle([x0, y0, x0 + tw + 3, y0 + 8], outline=hx("3a2a10"))
    d.line([(x0 + 1, y0 + 1), (x0 + tw + 2, y0 + 1)], fill=hx("d8b860"))
    tiny_text(d, x0 + 2, y0 + 2, word, hx("1e140a"))


def back_door(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 292, 52, 326, 133
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1], fill=hx("0e0a08"))
    vgrad(img, (x0, y0, x1, y1), hx("2a4a34"), hx("16281c"))
    d.rectangle([x0 + 4, y0 + 6, x1 - 4, y0 + 34], outline=hx("102018"))
    d.rectangle([x0 + 4, y0 + 42, x1 - 4, y1 - 6], outline=hx("102018"))
    plaque(d, (x0 + x1) // 2, y0 + 17)
    d.ellipse([x1 - 9, 92, x1 - 5, 96], fill=hx("c0a050"))
    light(img, "rect", [x0, y1 - 2, x1, y1 + 4], hx("f0c060"), 0.4, 2)


def bottle(d, x, base, kind, rnd):
    """Draws one back-bar bottle standing on `base`; returns its width."""
    edge = hx("140a06")
    if kind == "decanter":
        w, body, neck = 8, rnd.randint(7, 8), 2
        liquid, glass = hx("a8561a"), hx("7a8a90")
    elif kind == "gin":
        w, body, neck = 6, rnd.randint(8, 9), 4
        liquid, glass = hx("9ab4bc"), hx("7a96a0")
    elif kind == "wine":
        w, body, neck = 6, rnd.randint(8, 9), 5
        liquid, glass = hx("16301a"), hx("24481e")
    elif kind == "rye":
        w, body, neck = 6, rnd.randint(9, 10), 4
        liquid, glass = hx("8a3c10"), hx("5a3014")
    else:
        w, body, neck = 7, rnd.randint(8, 10), 3
        liquid, glass = hx("b8681a"), hx("6a3c16")
    top = base - body + 1
    hi = mix(liquid, hx("fff4d0"), 0.6)
    d.rectangle([x, top, x + w - 1, base], fill=edge)
    d.rectangle([x + 1, top, x + w - 2, base], fill=glass)
    level = top + (0 if kind in ("gin", "wine") else rnd.randint(1, 3))
    d.rectangle([x + 1, level, x + w - 2, base], fill=liquid)
    d.line([(x + w - 2, level), (x + w - 2, base)], fill=mul(liquid, 0.55))
    d.line([(x + 1, top + 1), (x + 1, base - 1)], fill=hi)
    if kind == "decanter":
        # squat cut-glass decanter with a ball stopper
        d.line([(x + 1, top), (x + w - 2, top)], fill=mix(glass, hx("ffffff"), 0.3))
        d.rectangle([x + 3, top - 2, x + 4, top - 1], fill=glass)
        d.rectangle([x + 2, top - 5, x + 5, top - 3], fill=hx("b0c8d0"))
        d.point((x + 2, top - 5), fill=edge)
        d.point((x + 5, top - 5), fill=edge)
        d.line([(x + 2, base - 2), (x + w - 3, base - 2)], fill=mul(liquid, 0.7))
        return w
    # rounded shoulder, neck and cap
    d.point((x, top), fill=hx("2a1a12"))
    d.point((x + w - 1, top), fill=hx("2a1a12"))
    d.line([(x + 1, top - 1), (x + w - 2, top - 1)], fill=edge)
    d.line([(x + 2, top - 1), (x + w - 3, top - 1)], fill=glass)
    nx0 = x + (w - 2) // 2
    nx1 = nx0 + 1
    d.rectangle([nx0, top - 1 - neck, nx1, top - 2], fill=glass)
    d.point((nx0, top - 1 - neck + 1), fill=mix(glass, hx("ffffff"), 0.3))
    cap = rnd.choice([hx("c0a050"), hx("8a1a14"), hx("1e1e22"), hx("d8d0c0")])
    d.rectangle([nx0, top - 2 - neck, nx1, top - 1 - neck], fill=cap)
    # paper label across the middle of the body
    if kind != "gin" or rnd.random() < 0.5:
        ly = base - body // 2 - 1
        lab = rnd.choice([hx("e0d0a8"), hx("d8c088"), hx("e8dcc0"), hx("c8a868")])
        d.rectangle([x + 1, ly, x + w - 2, ly + 3], fill=lab)
        d.line([(x + 1, ly + 3), (x + w - 2, ly + 3)], fill=mul(lab, 0.7))
        d.line([(x + 2, ly + 1), (x + w - 3, ly + 1)], fill=rnd.choice([hx("7a1a10"), hx("1e2a4a"), hx("2a2a2a")]))
    return w


def bar(img):
    d = ImageDraw.Draw(img)
    # back shelves with bottles and a mirror
    d.rectangle([338, 28, 478, 94], fill=hx("2a1a12"))
    vgrad(img, (344, 32, 472, 54), hx("3a4a5a"), hx("1e2630"))
    rnd = random.Random(5)
    kinds = ["whiskey", "whiskey", "whiskey", "decanter", "gin", "wine", "whiskey", "rye"]
    for sy in (58, 76):
        base = sy + 13
        d.rectangle([340, sy + 14, 476, sy + 16], fill=hx("5a3a20"))
        d.line([(340, sy + 14), (476, sy + 14)], fill=hx("8a6038"))
        x = 345
        while x < 464:
            kind = rnd.choice(kinds)
            x += bottle(d, x, base, kind, rnd) + rnd.randint(1, 3)
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


RUG_VP = (300, -300)
RUG_BACK, RUG_FRONT = 148, 230
RUG_X0, RUG_X1 = 192, 290  # front edge


def _rug_x(xf, y):
    vx, vy = RUG_VP
    return vx + (xf - vx) * (y - vy) / (RUG_FRONT - vy)


def runner(img):
    """Long oriental runner from the curtain to the bar, in the floor's perspective."""
    px = img.load()
    vy = RUG_VP[1]
    zb, zf = 1 / (RUG_BACK - vy), 1 / (RUG_FRONT - vy)
    length = 4.2  # rug length in rug widths
    field, field2 = hx("5a181a"), hx("4a1416")
    border, gold, navy, cream = hx("1a2440"), hx("a8843e"), hx("121c32"), hx("c8b890")
    shadow(img, "polygon", [(_rug_x(RUG_X0, RUG_BACK) - 2, RUG_BACK + 2), (_rug_x(RUG_X1, RUG_BACK) + 2, RUG_BACK + 2),
                            (RUG_X1 + 3, RUG_FRONT + 3), (RUG_X0 - 3, RUG_FRONT + 3)], 0.45, 2)
    for y in range(RUG_BACK, RUG_FRONT + 1):
        xa, xb = _rug_x(RUG_X0, y), _rug_x(RUG_X1, y)
        v = (zb - 1 / (y - vy)) / (zb - zf) * length
        for x in range(int(round(xa)), int(round(xb)) + 1):
            u = (x - xa) / (xb - xa)
            ev = min(v, length - v)
            edge = min(min(u, 1 - u), ev)
            if edge < 0.03:
                c = hx("2a1a14")
            elif edge < 0.05:
                c = gold
            elif edge < 0.15:
                # border band with a running chevron
                t = (edge - 0.05) / 0.10
                along = v if min(u, 1 - u) <= ev else u
                c = border
                if abs(((along * 6) % 1.0) - 0.5) * 2 < 0.3 and 0.3 < t < 0.7:
                    c = cream
                elif abs(t - 0.5) < 0.12:
                    c = hx("7a2420")
            elif edge < 0.17:
                c = gold
            else:
                # field: alternating tones and repeating diamond medallions
                c = field if int(v * 4) % 2 == 0 else field2
                mv = (v - 0.2) % 1.0 - 0.5
                du = abs(u - 0.5) * 2.4 + abs(mv) * 2.0
                if du < 0.22:
                    c = gold
                elif du < 0.34:
                    c = navy
                elif du < 0.42:
                    c = cream
                elif du < 0.52:
                    c = hx("7a2420")
                # small corner sprigs between medallions
                su, sv = abs(u - 0.5), abs(((v + 0.3) % 1.0) - 0.5)
                if 0.18 < su < 0.24 and sv < 0.06:
                    c = navy
            px[x, y] = c
    # fringe at both ends
    d = ImageDraw.Draw(img)
    for y, dy in ((RUG_BACK, -2), (RUG_FRONT, 3)):
        xa, xb = _rug_x(RUG_X0, y), _rug_x(RUG_X1, y)
        for x in range(int(xa) + 1, int(xb), 2):
            d.line([(x, y + (1 if dy > 0 else -1)), (x, y + dy)], fill=cream)
    # light falls from the stage onto the far end; the near end sits in the dark
    light(img, "ellipse", [180, RUG_BACK - 10, 300, RUG_BACK + 50], hx("8090c0"), 0.15, 10)


def paint():
    img = Image.new("RGB", (W, H))
    main_room(img)
    floor_boards(img, FLOOR, H - 1, (300, -300), 16, hx("2a1c16"), hx("1e140e"), hx("0e0806"), 9)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 33)
    d = ImageDraw.Draw(img)
    runner(img)
    # the corners stay black with spilled beer
    d.ellipse((40, 200, 78, 210), fill=hx("1a100c"))
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
    build_gin()
    return px


GIN_GLASS_AT = (398, 120)  # top-left in the room: on the counter beside the painted glasses, where micah_gin picks it up and sets it down


def gin_glass(full):
    """Tony's tumbler of bathtub gin on the counter (5x7), full or drained, in the colours micah_gin holds it in."""
    from .figure import ramp
    glass, gin = ramp("aac4cc"), ramp("e4ecd2")
    inside = mix(tuple(int(v) for v in glass[1]), hx("4a2a18"), 0.5)
    img = Image.new("RGBA", (5, 7))
    px = img.load()
    for y in range(7):
        for x in range(5):
            if y == 6 or x in (0, 4):
                tone = 4 if x == 0 and y < 6 else 1 if x == 4 else 2
                px[x, y] = tuple(int(v) for v in glass[tone]) + (255,)
            elif y == 0:
                px[x, y] = tuple(int(v) for v in glass[3]) + (255,)
            elif full:
                px[x, y] = tuple(int(v) for v in gin[3 if y == 1 else 2 if x == 1 else 1]) + (255,)
            else:
                px[x, y] = inside + (255,)
    return img


def build_gin():
    save(gin_glass(True), "rooms", "speakeasy_gin.png")
    save(gin_glass(False), "rooms", "speakeasy_gin_empty.png")
