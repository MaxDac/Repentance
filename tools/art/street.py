"""A Chicago street outside the Loop, painted in day and night variants."""
from PIL import Image, ImageDraw
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, text,
                     save, city)

VP = (240, 128)
STREET_Y = 138
ROAD = [(122, FULL_H - 1), (358, FULL_H - 1), (278, STREET_Y), (202, STREET_Y)]
LEFT_WALK = [(0, FULL_H - 1), (122, FULL_H - 1), (202, STREET_Y), (154, 132), (0, 132)]
RIGHT_WALK = [(358, FULL_H - 1), (W - 1, FULL_H - 1), (W - 1, 132), (326, 132), (278, STREET_Y)]

BUILDINGS = [
    {"name": "cafe", "box": (0, 58, 92, STREET_Y), "body": "stone", "shop": "LUNCH", "awning": hx("8a5c2c"),
     "lit": [0, 2, 5], "escape": False},
    {"name": "tailor", "box": (92, 70, 164, STREET_Y), "body": "brick", "shop": "TAILOR", "awning": hx("6a7a68"),
     "lit": [1, 4], "escape": True},
    {"name": "news", "box": (164, 84, 220, STREET_Y), "body": "stone", "shop": "NEWS", "awning": hx("745c40"),
     "lit": [0, 3], "escape": False},
    {"name": "books", "box": (260, 84, 316, STREET_Y), "body": "stone", "shop": "BOOKS", "awning": hx("3e5e7e"),
     "lit": [2, 4], "escape": False},
    {"name": "hotel", "box": (316, 66, 398, STREET_Y), "body": "brick", "shop": "HOTEL", "awning": hx("6a3040"),
     "lit": [0, 2, 5, 7], "escape": True},
    {"name": "drugs", "box": (398, 52, W - 1, STREET_Y), "body": "stone", "shop": "DRUGS", "awning": hx("48644c"),
     "lit": [1, 3, 6], "escape": False},
]


def brick_fill(img, box, c1, c2, mortar, seed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=mortar)
    rnd = random.Random(seed)
    for r, y in enumerate(range(y0, y1, 7)):
        off = 0 if r % 2 else 6
        for x in range(x0 - off, x1, 12):
            d.rectangle([max(x0, x), y, min(x1, x + 10), min(y1, y + 5)], fill=mix(c1, c2, rnd.random()))


def day_skyline(img, box, seed=17):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    vgrad(img, (x0, y0, x1, y1), hx("9dc3ea"), hx("e8edf0"))
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        bw = rnd.randint(10, 24)
        bh = rnd.randint(24, 70)
        col = rnd.choice([hx("8a93a0"), hx("707b88"), hx("9ea6b2")])
        d.rectangle([x, y1 - bh, min(x1, x + bw), y1], fill=col)
        if rnd.random() < 0.4:
            d.rectangle([x + 3, y1 - bh - 5, min(x1, x + bw - 3), y1 - bh], fill=mul(col, 0.9))
        for wy in range(y1 - bh + 4, y1 - 2, 5):
            for wx in range(x + 2, x + bw - 1, 4):
                if rnd.random() < 0.3:
                    d.point((wx, wy), fill=mul(col, 1.15))
        x += bw + rnd.randint(1, 4)
    for cx, cy, rx, ry in ((84, 48, 38, 12), (140, 40, 28, 10), (274, 34, 34, 11), (356, 44, 42, 13)):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=hx("edf2f4"))


def draw_background(img, mode):
    d = ImageDraw.Draw(img)
    if mode == "day":
        vgrad(img, (0, 0, W - 1, FULL_H - 1), hx("b7d5ef"), hx("f0e1c7"))
        day_skyline(img, (156, 24, 324, 126))
        d.polygon([(180, STREET_Y), VP, (300, STREET_Y), (324, 132), (156, 132)], fill=hx("8590a0"))
        light(img, "ellipse", [40, 10, 210, 130], hx("fff0c8"), 0.18, 20)
    else:
        vgrad(img, (0, 0, W - 1, FULL_H - 1), hx("0b1020"), hx("1a1824"))
        city(img, (156, 22, 324, 126), seed=19, lit=0.42, haze=hx("2f3552"))
        d.polygon([(180, STREET_Y), VP, (300, STREET_Y), (324, 132), (156, 132)], fill=hx("1a1d28"))
        shadow(img, "rect", [0, 0, W - 1, FULL_H - 1], 0.15, 24, tint=hx("08101a"))


def draw_pavement(img, mode):
    d = ImageDraw.Draw(img)
    walk_a, walk_b = (hx("b2a894"), hx("8d8370")) if mode == "day" else (hx("4a4650"), hx("2e2d34"))
    road_a, road_b = (hx("5c5a58"), hx("403d3a")) if mode == "day" else (hx("2a2930"), hx("18181c"))
    d.polygon(LEFT_WALK, fill=walk_a)
    d.polygon(RIGHT_WALK, fill=walk_a)
    d.polygon(ROAD, fill=road_a)
    noise(img, (0, STREET_Y - 4, W - 1, FULL_H - 1), 7 if mode == "day" else 5, 91 if mode == "day" else 92)

    for y in range(STREET_Y + 10, FULL_H, 14):
        t = (y - STREET_Y) / max(1, FULL_H - STREET_Y)
        lx0 = int(154 + (122 - 154) * t)
        lx1 = int(202 + (122 - 202) * t)
        rx0 = int(278 + (358 - 278) * t)
        rx1 = int(326 + (W - 1 - 326) * t)
        d.line([(lx0, y), (lx1, y)], fill=mix(walk_b, walk_a, 0.25))
        d.line([(rx0, y), (rx1, y)], fill=mix(walk_b, walk_a, 0.25))

    curb = hx("d0c7b0") if mode == "day" else hx("7a7488")
    d.line([(122, FULL_H - 1), (202, STREET_Y)], fill=curb, width=2)
    d.line([(358, FULL_H - 1), (278, STREET_Y)], fill=curb, width=2)
    for off in (-18, 18):
        rail = [(VP[0] + off + 12, STREET_Y + 8), (VP[0] + off * 2, FULL_H - 1)]
        d.line(rail, fill=hx("7a6a54") if mode == "day" else hx("5a5248"), width=2)
        d.line([(rail[0][0] + 10, rail[0][1]), (rail[1][0] + 10, rail[1][1])],
               fill=hx("665846") if mode == "day" else hx("474038"), width=2)
    for y in range(STREET_Y + 18, FULL_H, 18):
        t = (y - STREET_Y) / max(1, FULL_H - STREET_Y)
        x0 = int(220 + (174 - 220) * t)
        x1 = int(260 + (306 - 260) * t)
        d.line([(x0, y), (x1, y)], fill=mul(road_b, 1.1))


def draw_windows(img, building, mode):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = building["box"]
    cols = max(2, (x1 - x0 - 10) // 18)
    wx = x0 + 7
    idx = 0
    win_dark = hx("405468") if mode == "day" else hx("10141e")
    lit_cols = [hx("f8dfa0"), hx("dcb868"), hx("f0d090")]
    for row, y in enumerate(range(y0 + 10, y1 - 34, 17)):
        x = wx + (row % 2) * 2
        for _ in range(cols):
            box = [x, y, x + 9, y + 11]
            fill = lit_cols[(idx + row) % len(lit_cols)] if (mode == "night" and idx in building["lit"]) else win_dark
            if mode == "day":
                fill = mix(fill, hx("d7e4ee"), 0.65)
            d.rectangle(box, fill=fill, outline=mul(fill, 0.5))
            x += 16
            idx += 1


def fire_escape(img, building, mode):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = building["box"]
    metal = hx("404850") if mode == "day" else hx("1f252d")
    for y in range(y0 + 18, y1 - 18, 22):
        d.line([(x1 - 18, y), (x1 - 4, y)], fill=metal)
        d.line([(x1 - 18, y + 4), (x1 - 4, y + 4)], fill=metal)
        d.line([(x1 - 18, y), (x1 - 18, y + 6)], fill=metal)
        d.line([(x1 - 4, y), (x1 - 4, y + 6)], fill=metal)
    d.line([(x1 - 12, y0 + 18), (x1 - 12, y1 - 10)], fill=metal)
    for y in range(y0 + 30, y1 - 4, 7):
        d.line([(x1 - 16, y), (x1 - 8, y)], fill=metal)


def storefront(img, building, mode):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = building["box"]
    awn_y = y1 - 26
    glass = hx("adc7d6") if mode == "day" else hx("1e2532")
    warm = hx("efd49a")
    inner_left = x0 + 8
    inner_right = x1 - 10
    pane_w = max(10, min(16, (x1 - x0 - 22) // 3))
    door_left = inner_left + pane_w + 4
    door_right = inner_right - pane_w - 4
    d.rectangle([x0 + 4, y1 - 28, x1 - 4, y1 - 4], fill=hx("3b2a20"))
    d.rectangle([inner_left, y1 - 24, inner_left + pane_w, y1 - 4], fill=glass if mode == "day" else warm)
    d.rectangle([inner_right - pane_w, y1 - 24, inner_right, y1 - 4], fill=glass if mode == "day" else warm)
    if door_right > door_left:
        d.rectangle([door_left, y1 - 24, door_right, y1 - 4], fill=hx("2a2018"))
    awn = building["awning"] if mode == "day" else mul(building["awning"], 0.6)
    d.polygon([(x0 + 3, awn_y), (x1 - 3, awn_y), (x1 - 10, awn_y + 12), (x0 + 10, awn_y + 12)], fill=awn)
    for x in range(x0 + 8, x1 - 8, 12):
        d.line([(x, awn_y), (x + 5, awn_y + 12)], fill=mul(awn, 0.65))
    text(img, ((x0 + x1) // 2, awn_y - 8), building["shop"], hx("e8dec2") if mode == "day" else warm, size=8)
    if mode == "night":
        light(img, "rect", [x0 + 4, y1 - 32, x1 - 4, y1 - 2], hx("f0ba68"), 0.18, 6)


def draw_facades(img, mode):
    d = ImageDraw.Draw(img)
    for i, building in enumerate(BUILDINGS):
        x0, y0, x1, y1 = building["box"]
        if building["body"] == "brick":
            c1, c2, mortar = ((hx("9a4d3b"), hx("733728"), hx("d1aa8a")) if mode == "day"
                               else (hx("4c2330"), hx("31151c"), hx("24181a")))
            brick_fill(img, (x0, y0, x1, y1), c1, c2, mortar, 110 + i)
        else:
            stone = hx("c2b39a") if mode == "day" else hx("514740")
            d.rectangle([x0, y0, x1, y1], fill=stone)
            for y in range(y0 + 8, y1, 13):
                d.line([(x0, y), (x1, y)], fill=mul(stone, 0.85))
        d.rectangle([x0, y0, x1, y0 + 6], fill=hx("87674c") if mode == "day" else hx("2d2424"))
        d.line([(x0, y1), (x1, y1)], fill=hx("2a221e"))
        draw_windows(img, building, mode)
        storefront(img, building, mode)
        if building["escape"]:
            fire_escape(img, building, mode)
        d.rectangle([x0 + 5, y1 - 47, x1 - 5, y1 - 31], outline=hx("5c4634") if mode == "day" else hx("1b181a"))
        if mode == "day":
            light(img, "rect", [x0, y0, x1, y1], hx("fff2cc"), 0.08, 10)
        else:
            shadow(img, "rect", [x0, y0, x1, y1], 0.2, 6, tint=hx("0a1018"))


def lamppost(img, x, mode):
    d = ImageDraw.Draw(img)
    top = 116
    metal = hx("46505c") if mode == "day" else hx("161b22")
    d.line([(x, top), (x, 238)], fill=metal, width=3)
    d.line([(x - 10, top + 10), (x + 6, top)], fill=metal, width=2)
    d.ellipse([x + 4, top - 2, x + 12, top + 6], fill=hx("d8c488") if mode == "day" else hx("ffe0a0"))
    d.rectangle([x - 4, 238, x + 4, 242], fill=metal)
    if mode == "night":
        light(img, "ellipse", [x - 54, 132, x + 60, 250], hx("f0c070"), 0.45, 18)
        light(img, "ellipse", [x - 8, top - 12, x + 28, top + 20], hx("ffd488"), 0.4, 8)


def automobile(img, mode):
    d = ImageDraw.Draw(img)
    body = hx("28303c") if mode == "day" else hx("10141a")
    gloss = hx("6c7684") if mode == "day" else hx("3a4250")
    trim = hx("d8c8a0")
    pts = [(300, 224), (316, 208), (366, 208), (392, 214), (404, 226), (394, 234), (310, 234)]
    d.polygon(pts, fill=body)
    d.polygon([(320, 210), (344, 196), (364, 196), (378, 210)], fill=gloss)
    d.rectangle([319, 211, 377, 214], fill=gloss)
    for cx in (326, 382):
        d.ellipse([cx - 10, 226, cx + 10, 246], fill=hx("191919"))
        d.ellipse([cx - 6, 230, cx + 6, 242], fill=hx("ddd8cc"))
    d.line([(304, 224), (400, 224)], fill=trim)
    d.point((397, 220), fill=hx("f0d090"))
    if mode == "night":
        light(img, "polygon", [(392, 220), (430, 214), (464, 226), (424, 236)], hx("f0d8a0"), 0.22, 8)
    shadow(img, "ellipse", [302, 236, 406, 252], 0.4, 4)


def street_details(img, mode):
    d = ImageDraw.Draw(img)
    for x in (94, 382):
        lamppost(img, x, mode)
    automobile(img, mode)

    bench = hx("765236") if mode == "day" else hx("2d221c")
    d.rectangle([54, 214, 86, 220], fill=bench)
    d.line([(58, 220), (58, 235)], fill=bench)
    d.line([(82, 220), (82, 235)], fill=bench)
    d.line([(54, 214), (86, 214)], fill=mul(bench, 1.25))

    sign_col = hx("e6d6aa") if mode == "day" else hx("d0b870")
    d.rectangle([231, 102, 249, 124], fill=hx("40362d") if mode == "day" else hx("161618"))
    text(img, (240, 113), "EL", sign_col, size=8)
    d.rectangle([236, 124, 244, 138], fill=hx("40362d") if mode == "day" else hx("161618"))

    for x, y in ((26, 168), (164, 176), (438, 164)):
        d.rectangle([x, y, x + 8, y + 14], fill=hx("564436") if mode == "day" else hx("241d1a"))
        d.rectangle([x + 1, y + 2, x + 7, y + 9], fill=hx("d0c4a0") if mode == "day" else hx("50452e"))
    if mode == "night":
        shadow(img, "polygon", [(0, 150), (110, 150), (162, 270), (0, 270)], 0.18, 10, tint=hx("04080e"))
        shadow(img, "polygon", [(W - 1, 150), (370, 150), (324, 270), (W - 1, 270)], 0.18, 10, tint=hx("04080e"))


def paint(mode):
    img = Image.new("RGB", (W, FULL_H))
    draw_background(img, mode)
    draw_pavement(img, mode)
    draw_facades(img, mode)
    street_details(img, mode)
    if mode == "day":
        vignette(img, 0.22, tint=(198, 184, 160), blur=44)
    else:
        vignette(img, 0.58, tint=(18, 20, 40), blur=52)
    return img


def build():
    for mode in ("day", "night"):
        base = paint(mode)
        pal = palette_of(base, 128)
        px = pixelize(base, pal)
        save(px, "rooms", f"street_{mode}.png")
