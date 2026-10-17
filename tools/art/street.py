"""State Street on a wet 1920s Chicago night: a side-on block of facades - the
Aurelian, an alley, a brick walk-up with the motel office and a lunch counter, the public library and a corner
drugstore - above a wide wet sidewalk, a granite curb and a strip of cobbles with a sedan parked at the kerb.
Down the cross street on the right the cathedral rises behind the L.

Lamp posts, the hydrant and the car stand nearer the camera than anyone on the sidewalk, so they are also cut
out into street_night_fg.png, which the scene y-sorts in front of the characters."""
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import math
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, cut)

BASE = 168          # foot of the facades / back edge of the sidewalk
CURB = 244          # top edge of the curb (front edge of the sidewalk)
GUTTER = 250
ROAD_GROUND = 268   # where the car's tyres touch the cobbles
VP = (240, -520)    # sidewalk joints converge very gently (the floor is almost orthographic, like the room scaling)
LAMPS = (144, 316)
CAR_X = 242
HYDRANT_X = 226

NIGHT = {
    "sky0": hx("070a16"), "sky1": hx("1c1a2c"), "haze": hx("3a2e3c"),
    "far": hx("121626"), "far2": hx("0c0f1c"),
    "stone": hx("5a524c"), "stone_d": hx("3c3634"), "stone_l": hx("6e665c"),
    "granite": hx("201e26"), "granite_l": hx("3a3644"),
    "brick1": hx("4e2622"), "brick2": hx("3a1a18"), "mortar": hx("201614"),
    "lib": hx("4a4c52"), "lib_d": hx("33343a"), "lib_l": hx("5e6068"),
    "terra": hx("4a3a30"),
    "iron": hx("14161c"), "iron_l": hx("3a404c"),
    "wood": hx("2a1a12"), "wood_l": hx("4a3020"),
    "glass": hx("10141e"), "glass_l": hx("26304a"),
    "lit": hx("f2c878"), "lit2": hx("d89a50"), "blind": hx("b88a4c"),
    "walk0": hx("23252e"), "walk1": hx("2e313c"), "joint": hx("15161c"),
    "curb": hx("5a5866"), "curb_d": hx("2c2a34"),
    "cob1": hx("1e1e26"), "cob2": hx("2a2a34"), "cob_l": hx("4a4a5a"),
    "car": hx("2a141a"), "car_d": hx("160a0e"), "car_l": hx("6a3a44"),
    "chrome": hx("9a9aa8"), "tyre": hx("0e0e12"), "spoke": hx("8a7a64"),
    "neon_red": hx("ff5048"), "neon_green": hx("60ff90"), "bulb": hx("ffe6a0"),
    "awn1": hx("6a1c20"), "awn2": hx("a89c84"),
}
DAY = {
    "sky0": hx("8c96a4"), "sky1": hx("c4c6c4"), "haze": hx("b8b6b0"),
    "far": hx("8a909c"), "far2": hx("767c8a"),
    "stone": hx("b2a690"), "stone_d": hx("8a7e6c"), "stone_l": hx("c8bea8"),
    "granite": hx("3e3a42"), "granite_l": hx("6a6470"),
    "brick1": hx("8a4434"), "brick2": hx("6a3024"), "mortar": hx("8e7c6c"),
    "lib": hx("a4a6a6"), "lib_d": hx("7c7e80"), "lib_l": hx("bcbebc"),
    "terra": hx("9a7a5c"),
    "iron": hx("26282e"), "iron_l": hx("5a606a"),
    "wood": hx("4a2e1c"), "wood_l": hx("6a4a30"),
    "glass": hx("3c4858"), "glass_l": hx("8a9aac"),
    "lit": hx("c8b088"), "lit2": hx("9a8466"), "blind": hx("c2ae86"),
    "walk0": hx("6a6a6c"), "walk1": hx("7c7c7c"), "joint": hx("4a4a4e"),
    "curb": hx("a8a69e"), "curb_d": hx("6a6a68"),
    "cob1": hx("4a4846"), "cob2": hx("5a5652"), "cob_l": hx("8a8682"),
    "car": hx("1e3a2e"), "car_d": hx("10201a"), "car_l": hx("5a8270"),
    "chrome": hx("c8ccd0"), "tyre": hx("1a1a1c"), "spoke": hx("c8b890"),
    "neon_red": hx("a06460"), "neon_green": hx("6a8a74"), "bulb": hx("d8d0b8"),
    "awn1": hx("8a2a2a"), "awn2": hx("d8ccb0"),
}


def bricks(img, box, c1, c2, mortar, seed, h=5, w=11):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=mortar)
    rnd = random.Random(seed)
    for r, y in enumerate(range(y0, y1 + 1, h)):
        off = (r % 2) * (w // 2)
        for x in range(x0 - off, x1 + 1, w):
            a, b = max(x0, x), min(x1, x + w - 2)
            if b >= a:
                d.rectangle([a, y, b, min(y1, y + h - 2)], fill=mix(c1, c2, rnd.random()))
    noise(img, box, 4, seed)


def ashlar(img, box, c, seed, course=9, block=22):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    d.rectangle(box, fill=c)
    for r, y in enumerate(range(y0, y1 + 1, course)):
        off = (r % 2) * (block // 2)
        for x in range(x0 - off, x1 + 1, block):
            a, b = max(x0, x + 1), min(x1, x + block - 1)
            if b >= a and y + 1 <= y1:
                d.rectangle([a, y + 1, b, min(y1, y + course - 1)], fill=mul(c, 0.94 + rnd.random() * 0.1))
        d.line([(x0, y), (x1, y)], fill=mul(c, 0.78))
    noise(img, box, 4, seed)


def window(img, box, m, lit, seed=0, blind=0.4, sash=True, sill=None, silhouette=False):
    """A double-hung window with frame, sill, glass and a pull-down blind."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=mul(m["iron"], 1.3))
    if lit:
        vgrad(img, (x0, y0, x1, y1), m["lit"], m["lit2"])
    else:
        vgrad(img, (x0, y0, x1, y1), m["glass_l"], m["glass"])
        d.line([(x0 + 1, y1 - 3), (x0 + (x1 - x0) // 2, y0 + 2)], fill=mix(m["glass_l"], m["glass"], 0.3))
    if blind:
        by = y0 + int((y1 - y0) * blind)
        col = m["blind"] if lit else mul(m["glass_l"], 0.8)
        d.rectangle([x0, y0, x1, by], fill=col)
        for y in range(y0 + 2, by, 2):
            d.line([(x0, y), (x1, y)], fill=mul(col, 0.86))
        d.line([(x0, by), (x1, by)], fill=mul(col, 0.6))
        d.point(((x0 + x1) // 2, by + 1), fill=mul(col, 0.5))
    if silhouette and lit:
        sx = x0 + (x1 - x0) // 2 + rnd.randint(-2, 2)
        d.ellipse([sx - 2, y1 - 13, sx + 2, y1 - 9], fill=m["lit2"] if False else mul(m["lit2"], 0.45))
        d.rectangle([sx - 4, y1 - 8, sx + 4, y1], fill=mul(m["lit2"], 0.45))
    if sash:
        my = (y0 + y1) // 2
        d.line([(x0, my), (x1, my)], fill=mul(m["iron"], 1.4))
        d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=mul(m["iron"], 1.4))
    if sill:
        d.rectangle([x0 - 3, y1 + 1, x1 + 3, y1 + 3], fill=sill)
        d.line([(x0 - 3, y1 + 4), (x1 + 3, y1 + 4)], fill=mul(sill, 0.5))


# --------------------------------------------------------------------------------------------- sky & distance

def sky(img, m, mode):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, BASE), m["sky0"], m["sky1"])
    rnd = random.Random(5)
    # low clouds lit from below by the city
    for _ in range(26):
        cx, cy = rnd.randint(-20, W + 20), rnd.randint(-6, 60)
        rx, ry = rnd.randint(30, 80), rnd.randint(5, 12)
        col = mix(m["sky0"], m["haze"], 0.35 + cy / 140)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
    img.paste(img.filter(ImageFilter.GaussianBlur(4)).crop((0, 0, W, 90)), (0, 0))
    # distant towers above the low roofs
    rnd = random.Random(23)
    x = 150
    while x < 430:
        bw, top = rnd.randint(14, 30), rnd.randint(0, 34)
        col = m["far"] if rnd.random() < 0.5 else m["far2"]
        d.rectangle([x, top, x + bw, 120], fill=col)
        if rnd.random() < 0.5:  # deco setbacks and a spire
            d.rectangle([x + 3, top - 6, x + bw - 3, top], fill=col)
            d.rectangle([x + 6, top - 11, x + bw - 6, top - 6], fill=col)
            d.line([(x + bw // 2, top - 20), (x + bw // 2, top - 11)], fill=col)
            if mode == "night":
                d.point((x + bw // 2, top - 21), fill=hx("ff4a3a"))
        for wy in range(top + 3, 120, 4):
            for wx in range(x + 2, x + bw - 1, 3):
                if rnd.random() < (0.22 if mode == "night" else 0.0):
                    d.point((wx, wy), fill=rnd.choice([hx("d8b060"), hx("e8c878"), hx("b08848")]))
        x += bw + rnd.randint(-4, 6)
    light(img, "rect", [0, 40, W, 170], m["haze"], 0.35 if mode == "night" else 0.25, 30)


def vista(img, m, mode):
    """The cross street on the right: the L crossing it and the cathedral at the end of the block."""
    d = ImageDraw.Draw(img)
    vx, vy = 452, 112
    x0 = 420

    def at(x, y, f):
        return (x + (vx - x) * f, y + (vy - y) * f)

    # cathedral at the end of the street
    cath = hx("0a0c16") if mode == "night" else mix(m["far2"], m["lib_d"], 0.3)
    for tx in (438, 474):
        d.rectangle([tx - 7, 34, tx + 7, 126], fill=cath)
        d.polygon([(tx - 7, 34), (tx, 4), (tx + 7, 34)], fill=cath)
        d.line([(tx, 0), (tx, 4)], fill=cath)
        d.line([(tx - 1, 1), (tx + 1, 1)], fill=cath)
        for wy in (46, 66):
            d.rectangle([tx - 2, wy, tx + 2, wy + 10], fill=mul(cath, 0.6))
            d.pieslice([tx - 2, wy - 2, tx + 2, wy + 2], 180, 360, fill=mul(cath, 0.6))
    d.polygon([(445, 70), (456, 50), (467, 70), (467, 126), (445, 126)], fill=mul(cath, 0.92))
    rose = m["lit"] if mode == "night" else mul(cath, 0.7)
    d.ellipse([450, 74, 462, 86], fill=mul(cath, 0.5))
    d.ellipse([451, 75, 461, 85], fill=mix(rose, hx("c04030"), 0.4) if mode == "night" else rose)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.line([(456, 80), (456 + 5 * math.cos(r), 80 + 5 * math.sin(r))], fill=mul(cath, 0.5))
    d.polygon([(451, 126), (451, 108), (456, 100), (461, 108), (461, 126)], fill=mul(cath, 0.5))
    if mode == "night":
        light(img, "ellipse", [440, 64, 472, 96], hx("e08a50"), 0.35, 6)
        d.polygon([(452, 126), (452, 109), (456, 103), (460, 109), (460, 126)], fill=hx("6a4a30"))
    # haze between the cathedral and the street
    light(img, "rect", [x0, 96, W, 140], m["haze"], 0.3, 10)

    # cross-street floor
    road = [(x0, BASE), (W, BASE), (W, 128), (x0 + 20, 126)]
    d.polygon(road, fill=mix(m["cob1"], m["haze"], 0.25))
    for f in (0.2, 0.4, 0.6, 0.75):
        y = BASE + (vy - BASE) * f
        d.line([(x0, y), (W, y)], fill=mix(m["cob1"], m["joint"], 0.5))

    # the L: a riveted girder deck on lattice columns, a train rattling across
    deck_y = 70
    col_foot = BASE + (vy - BASE) * 0.45
    for cx in (428, 462):
        d.rectangle([cx - 2, deck_y + 8, cx + 2, col_foot], fill=m["iron"])
        for y in range(deck_y + 10, int(col_foot), 6):
            d.line([(cx - 2, y), (cx + 2, y + 6)], fill=m["iron_l"])
    d.rectangle([x0, deck_y, W, deck_y + 8], fill=m["iron"])
    for x in range(x0, W, 5):
        d.line([(x, deck_y + 1), (x + 4, deck_y + 7)], fill=m["iron_l"])
        d.line([(x + 4, deck_y + 1), (x, deck_y + 7)], fill=m["iron_l"])
    d.line([(x0, deck_y), (W, deck_y)], fill=mul(m["iron_l"], 1.3))
    car_col = hx("1e2420") if mode == "night" else hx("4a5a4a")
    d.rectangle([x0, deck_y - 13, W, deck_y - 1], fill=car_col)
    d.line([(x0, deck_y - 13), (W, deck_y - 13)], fill=mul(car_col, 1.6))
    for wx in range(x0 + 2, W, 6):
        d.rectangle([wx, deck_y - 10, wx + 2, deck_y - 7], fill=m["lit2"] if mode == "night" else m["glass_l"])
    if mode == "night":
        light(img, "rect", [x0, deck_y - 14, W, deck_y], hx("f0c070"), 0.15, 4)
        light(img, "ellipse", [436, deck_y - 4, 446, deck_y + 4], hx("a0c0ff"), 0.6, 2)

    # side walls of the cross street (drugstore side on the left, a low warehouse on the right)
    lw = [(x0, 20), at(x0, 20, 0.62), at(x0, BASE, 0.62), (x0, BASE)]
    d.polygon(lw, fill=mul(m["terra"], 0.62))
    for f in (0.12, 0.28, 0.44):
        p0, p1 = at(x0, 40, f), at(x0, 40, f + 0.08)
        q0, q1 = at(x0, 120, f), at(x0, 120, f + 0.08)
        d.polygon([p0, p1, q1, q0], fill=m["lit2"] if (mode == "night" and f != 0.28) else m["glass"])
    rw = [(W, 70), at(W, 70, 0.6), at(W, BASE, 0.6), (W, BASE)]
    d.polygon(rw, fill=mul(m["brick2"], 0.7))
    d.line([rw[0], rw[1]], fill=mul(m["brick1"], 1.1))
    shadow(img, "polygon", lw, 0.3, 2)


# --------------------------------------------------------------------------------------------- buildings

def aurelian(img, m, mode):
    d = ImageDraw.Draw(img)
    x0, x1 = 0, 140
    ashlar(img, (x0, 0, x1, BASE), m["stone"], 3, course=8, block=20)
    # upper storeys: tall windows with deco spandrels
    for i, cx in enumerate((20, 49, 78, 107)):
        window(img, (cx - 8, -20, cx + 8, -2), m, lit=(mode == "night" and i in (0, 3)), seed=i, blind=0.5,
               sill=m["stone_l"])
        window(img, (cx - 8, 10, cx + 8, 38), m, lit=(mode == "night" and i in (1, 2)), seed=10 + i,
               blind=(0.3, 0.6, 0.45, 0.8)[i], sill=m["stone_l"], silhouette=(i == 2))
        d.rectangle([cx - 8, 42, cx + 8, 48], fill=m["stone_d"])
        d.polygon([(cx - 6, 47), (cx, 43), (cx + 6, 47)], outline=m["stone_l"])
    for px in (6, 34, 63, 93, 122):
        d.line([(px, -2), (px, 50)], fill=m["stone_l"])
        d.line([(px + 1, -2), (px + 1, 50)], fill=m["stone_d"])
    # belt course with a deco zigzag
    d.rectangle([x0, 50, x1, 56], fill=m["stone_l"])
    for x in range(x0, x1, 8):
        d.line([(x, 55), (x + 4, 51), (x + 8, 55)], fill=m["stone_d"])
    d.line([(x0, 57), (x1, 57)], fill=mul(m["stone_d"], 0.7))
    # rusticated ground floor
    for y in range(64, BASE - 16, 8):
        d.line([(x0, y), (x1, y)], fill=mul(m["stone_d"], 0.8))
    # corner quoins (the Aurelian's front is round the corner, to the left)
    for y in range(0, BASE, 12):
        d.rectangle([0, y, 5 + (y // 12) % 2 * 3, y + 10], fill=m["stone_l"])
    # ground floor windows into the side lounge
    for (wx0, wx1) in ((12, 44), (110, 134)):
        d.rectangle([wx0 - 3, 84, wx1 + 3, 150], fill=m["stone_d"])
        d.pieslice([wx0 - 3, 76, wx1 + 3, 94], 180, 360, fill=m["stone_d"])
        lit = mode == "night"
        vgrad(img, (wx0, 88, wx1, 146), m["lit"] if lit else m["glass_l"], m["lit2"] if lit else m["glass"])
        d.pieslice([wx0, 80, wx1, 96], 180, 360, fill=m["lit"] if lit else m["glass_l"])
        for x in range(wx0 + 8, wx1, 8):
            d.line([(x, 82), (x, 146)], fill=mul(m["wood"], 1.2))
        d.line([(wx0, 104), (wx1, 104)], fill=mul(m["wood"], 1.2))
        # half drawn curtains and a potted palm against the light
        cur = mul(hx("6a1c24"), 0.9 if lit else 0.6)
        d.rectangle([wx0, 86, wx0 + 4, 146], fill=cur)
        d.rectangle([wx1 - 4, 86, wx1, 146], fill=cur)
        sil = mul(m["lit2"], 0.35) if lit else mul(m["glass"], 0.7)
        px = (wx0 + wx1) // 2
        d.rectangle([px - 3, 136, px + 3, 146], fill=sil)
        for a in (-70, -40, -10, 20, 50, 80):
            r = math.radians(a - 90)
            d.line([(px, 134), (px + 12 * math.cos(r), 134 + 9 * math.sin(r) + 4)], fill=sil, width=2)
    # entrance: brass doors under a fanlight and a bulb-lit canopy
    d.rectangle([56, 70, 100, BASE], fill=mul(m["stone_d"], 0.7))
    door_lit = m["lit"] if mode == "night" else mix(m["lit"], m["glass"], 0.5)
    vgrad(img, (60, 92, 96, BASE - 1), door_lit, m["lit2"])
    brass = hx("b08838") if mode == "night" else hx("a08848")
    for dx in (60, 78):
        d.rectangle([dx, 92, dx + 17, BASE - 1], outline=brass)
        d.rectangle([dx + 1, 93, dx + 16, 97], fill=brass)
        d.rectangle([dx + 1, BASE - 12, dx + 16, BASE - 1], fill=mul(brass, 0.7))
        d.line([(dx + 3, 126), (dx + 14, 126)], fill=mul(brass, 1.2))
    d.rectangle([77, 92, 78, BASE - 1], fill=mul(brass, 0.6))
    d.rectangle([60, 78, 96, 90], fill=mul(brass, 0.5))
    for i in range(9):
        a = math.pi + math.pi * (i + 0.5) / 9
        d.line([(78, 90), (78 + 17 * math.cos(a), 90 + 11 * math.sin(a))], fill=brass)
    # canopy: a shallow marquee box with the hotel's name and a row of bulbs
    d.line([(44, 52), (52, 64)], fill=m["iron"], width=1)
    d.line([(112, 52), (104, 64)], fill=m["iron"], width=1)
    d.rectangle([38, 64, 118, 76], fill=hx("2a1418") if mode == "night" else hx("5a2a2a"))
    d.rectangle([38, 63, 118, 64], fill=brass)
    d.rectangle([38, 76, 118, 77], fill=brass)
    text(img, (78, 70), "HOTEL AURELIAN", hx("f8e0a0") if mode == "night" else hx("e8d8b0"), size=8)
    for x in range(40, 118, 4):
        d.point((x, 79), fill=m["bulb"])
    # granite plinth
    d.rectangle([x0, BASE - 16, 55, BASE], fill=m["granite"])
    d.rectangle([101, BASE - 16, x1, BASE], fill=m["granite"])
    d.line([(x0, BASE - 16), (55, BASE - 16)], fill=m["granite_l"])
    d.line([(101, BASE - 16), (x1, BASE - 16)], fill=m["granite_l"])
    # blade sign
    d.line([(126, 6), (140, 6)], fill=m["iron"])
    d.line([(126, 60), (140, 60)], fill=m["iron"])
    d.rectangle([122, 2, 136, 62], fill=hx("1c0c10") if mode == "night" else hx("5a2026"))
    d.rectangle([122, 2, 136, 62], outline=m["neon_red"])
    for i, ch in enumerate("HOTEL"):
        text(img, (129, 10 + i * 11), ch, hx("ffe8d8") if mode == "night" else hx("e8d8c8"), size=8)
    if mode == "night":
        light(img, "rect", [118, -4, 140, 66], m["neon_red"], 0.45, 7)
        light(img, "rect", [34, 70, 122, 100], hx("ffd890"), 0.4, 8)
        light(img, "rect", [56, 86, 100, BASE], hx("ffd890"), 0.25, 6)
    shadow(img, "rect", [38, 77, 118, 92], 0.35, 4)


def alley(img, m, mode):
    d = ImageDraw.Draw(img)
    x0, x1 = 140, 172
    bricks(img, (x0, 0, x1, BASE), mul(m["brick1"], 0.45), mul(m["brick2"], 0.45), mul(m["mortar"], 0.6), 61)
    # Aurelian's side wall receding into the alley
    side = [(x0, 0), (152, 12), (152, 160), (x0, BASE)]
    d.polygon(side, fill=mul(m["stone_d"], 0.55))
    for y in range(18, 160, 10):
        d.line([(x0, y + (BASE - y) * 0 - 4), (152, y)], fill=mul(m["stone_d"], 0.45))
    # cobbled alley floor
    d.polygon([(x0, BASE), (x1, BASE), (x1, 160), (152, 160)], fill=mul(m["cob1"], 0.8))
    for y in (162, 165):
        d.line([(146, y), (x1, y)], fill=mul(m["cob_l"], 0.5))
    # the unmarked steel door, a caged bulb and the club's garbage
    steel = hx("2a3430") if mode == "night" else hx("4a5450")
    d.rectangle([154, 96, 170, 160], fill=mul(steel, 0.6))
    d.rectangle([155, 98, 169, 160], fill=steel)
    for y in (104, 128, 152):
        for x in range(157, 169, 4):
            d.point((x, y), fill=mul(steel, 1.8))
    d.rectangle([159, 108, 165, 110], fill=mul(steel, 0.4))
    d.line([(158, 89), (166, 89)], fill=m["iron"])
    d.ellipse([160, 89, 164, 93], fill=m["bulb"] if mode == "night" else mul(m["bulb"], 0.7))
    d.rectangle([152, 146, 157, 160], fill=hx("3a3e40") if mode == "night" else hx("6a6e70"))
    d.line([(152, 146), (157, 146)], fill=mul(m["chrome"], 0.6))
    shadow(img, "rect", [x0, 0, x1, 60], 0.5, 12)
    if mode == "night":
        light(img, "ellipse", [146, 80, 178, 136], hx("d0e0b0"), 0.35, 8)
        light(img, "ellipse", [150, 140, 174, 172], hx("d0e0b0"), 0.15, 4)
        shadow(img, "polygon", side, 0.4, 2)


def walkup(img, m, mode):
    """Two-storey brick walk-up: motel office, lunch counter, bookshop upstairs, fire escape, newsstand."""
    d = ImageDraw.Draw(img)
    x0, x1 = 172, 310
    bricks(img, (x0, 14, x1, BASE), m["brick1"], m["brick2"], m["mortar"], 71)
    # coping, cornice with brackets and dentils
    d.rectangle([x0, 12, x1, 15], fill=m["stone_l"])
    d.rectangle([x0 - 2, 26, x1 + 2, 33], fill=mul(m["iron_l"], 0.9))
    d.line([(x0 - 2, 26), (x1 + 2, 26)], fill=mul(m["iron_l"], 1.4))
    for x in range(x0, x1, 4):
        d.rectangle([x, 31, x + 1, 33], fill=mul(m["iron"], 1.1))
    for x in range(x0 + 4, x1, 22):
        d.rectangle([x, 33, x + 3, 38], fill=mul(m["iron_l"], 0.7))
    shadow(img, "rect", [x0, 34, x1, 40], 0.5, 2)
    # upstairs windows; the middle three-light window is the bookshop
    window(img, (182, 44, 196, 66), m, lit=(mode == "night"), seed=3, blind=0.35, sill=m["stone_l"])
    window(img, (206, 44, 220, 66), m, lit=False, seed=4, blind=0.7, sill=m["stone_l"])
    for i, wx in enumerate((252, 268, 284)):
        window(img, (wx, 44, wx + 14, 66), m, lit=(mode == "night"), seed=5 + i, blind=0.25, sash=False)
    d.rectangle([249, 67, 301, 69], fill=m["stone_l"])
    d.rectangle([254, 55, 297, 64], fill=hx("2a1a10"))
    text(img, (276, 60), "BOOKS", hx("e8c060") if mode == "night" else hx("c8a048"), size=8)
    for wx0, wx1 in ((182, 196), (206, 220), (252, 298)):
        d.rectangle([wx0 - 2, 40, wx1 + 2, 43], fill=m["stone_l"])
    # fire escape: balcony, railing, drop ladder and the ladder to the roof
    iron = m["iron"]
    d.line([(176, 68), (226, 68)], fill=iron, width=2)
    d.line([(176, 58), (226, 58)], fill=iron)
    for x in range(176, 227, 3):
        d.line([(x, 58), (x, 68)], fill=iron)
    d.line([(222, 16), (222, 68)], fill=iron)
    d.line([(226, 16), (226, 68)], fill=iron)
    for y in range(18, 66, 4):
        d.line([(222, y), (226, y)], fill=iron)
    d.line([(184, 70), (184, 92)], fill=iron)
    d.line([(190, 70), (190, 92)], fill=iron)
    for y in range(72, 92, 4):
        d.line([(184, y), (190, y)], fill=iron)
    for x in range(178, 228, 3):  # its shadow on the brick
        d.point((x + 2, 71), fill=mul(m["mortar"], 0.8))
    # shopfront fascia
    d.rectangle([x0, 72, x1, 84], fill=m["wood"])
    d.line([(x0, 72), (x1, 72)], fill=m["wood_l"])
    d.line([(x0, 84), (x1, 84)], fill=mul(m["wood"], 0.6))
    # motel office door
    d.rectangle([179, 86, 207, BASE], fill=mul(m["wood"], 0.6))
    d.rectangle([182, 88, 204, BASE], fill=m["wood"])
    gl = m["lit2"] if mode == "night" else m["glass_l"]
    d.rectangle([185, 92, 201, 122], fill=gl)
    d.line([(193, 92), (193, 122)], fill=m["wood"])
    d.rectangle([185, 128, 201, 160], outline=m["wood_l"])
    d.point((200, 128), fill=m["chrome"])
    d.rectangle([180, 86, 206, 88], fill=m["wood_l"])
    # the sagging MOTEL sign on a bracket, a couple of bulbs dead
    d.line([(204, 36), (246, 36)], fill=iron, width=2)
    d.line([(204, 46), (222, 36)], fill=iron)
    sign = Image.new("RGBA", (48, 20), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sign)
    sd.rectangle([1, 1, 46, 18], fill=(hx("3a2a14") if mode == "night" else hx("6a5030")) + (255,),
                 outline=(hx("8a6a30") if mode == "night" else hx("9a7a48")) + (255,))
    text(sign, (24, 10), "MOTEL", (hx("ffd890") if mode == "night" else hx("e8d0a0")) + (255,), size=8)
    for i, x in enumerate(range(4, 45, 5)):
        on = mode == "night" and i not in (2, 6)
        sd.point((x, 3), fill=(m["bulb"] if on else hx("3a3428")) + (255,))
        sd.point((x, 16), fill=(m["bulb"] if on and i != 4 else hx("3a3428")) + (255,))
    sign = sign.rotate(-7, resample=Image.Resampling.NEAREST, expand=True)
    d.line([(210, 36), (210, 42)], fill=iron)
    d.line([(242, 36), (242, 46)], fill=iron)
    img.paste(sign, (202, 38), sign)
    # lunch counter window under a striped awning
    d.rectangle([212, 88, 278, BASE], fill=m["wood"])
    lit = mode == "night"
    vgrad(img, (215, 98, 275, 150), m["lit"] if lit else m["glass_l"], m["lit2"] if lit else m["glass"])
    sil = mul(m["lit2"], 0.4) if lit else mul(m["glass"], 0.75)
    d.rectangle([215, 132, 275, 136], fill=sil)                     # counter
    for sx in (222, 238, 254, 268):                                # stools
        d.rectangle([sx - 3, 138, sx + 3, 140], fill=sil)
        d.line([(sx, 140), (sx, 150)], fill=sil)
    d.rectangle([258, 112, 266, 131], fill=sil)                     # coffee urn
    d.ellipse([257, 108, 267, 116], fill=sil)
    d.ellipse([228, 112, 236, 120], fill=sil)                       # a man hunched over his coffee
    d.polygon([(224, 138), (226, 122), (238, 120), (242, 132), (240, 138)], fill=sil)
    d.line([(245, 98), (245, 150)], fill=m["wood"], width=2)
    text(img, (230, 105), "LUNCH", hx("f0c050") if lit else hx("d8b050"), size=8)
    d.rectangle([215, 151, 275, BASE - 1], fill=hx("2c3a36") if lit else hx("4a6a62"))
    for x in range(215, 276, 4):
        d.line([(x, 151), (x, BASE - 1)], fill=mul(hx("2c3a36") if lit else hx("4a6a62"), 0.75))
    awn_top, awn_bot = 76, 94
    for i, x in enumerate(range(208, 284, 6)):
        col = m["awn1"] if i % 2 else m["awn2"]
        col = mul(col, 0.55) if lit else col
        d.polygon([(x, awn_top), (x + 6, awn_top), (x + 7, awn_bot), (x + 1, awn_bot)], fill=col)
        d.chord([x + 1, awn_bot - 3, x + 7, awn_bot + 3], 0, 180, fill=col)
    d.line([(207, awn_top), (283, awn_top)], fill=m["iron"])
    shadow(img, "rect", [208, awn_top, 284, awn_top + 6], 0.3, 2)
    # newsstand against the wall
    green = hx("1e3024") if mode == "night" else hx("3e5a44")
    d.rectangle([280, 120, 308, BASE], fill=green)
    d.polygon([(277, 116), (311, 116), (309, 122), (279, 122)], fill=mul(green, 0.7))
    d.line([(277, 116), (311, 116)], fill=mul(green, 1.8))
    d.rectangle([281, 123, 307, 131], fill=mul(green, 0.6))
    text(img, (294, 127), "NEWS", hx("e8d8a0") if mode == "night" else hx("f0e8c8"), size=8)
    rnd = random.Random(44)
    for x in range(282, 306, 6):  # magazines pinned up behind the counter
        c = rnd.choice([hx("a83a2a"), hx("c8a038"), hx("3a5a8a"), hx("d8d0c0")])
        d.rectangle([x, 133, x + 4, 140], fill=mul(c, 0.7 if lit else 1.0))
    d.rectangle([280, 146, 308, 149], fill=mul(green, 1.4))
    for i, x in enumerate(range(281, 307, 5)):  # stacked evening editions
        paper = hx("c8c4b4") if mode == "night" else hx("e8e4d8")
        d.rectangle([x, 142 - i % 2, x + 4, 146], fill=paper)
        d.line([(x + 1, 143), (x + 3, 143)], fill=mul(paper, 0.4))
    d.rectangle([284, BASE - 8, 296, BASE - 1], fill=hx("b8b4a4") if lit else hx("dcd8cc"))  # tied bundle
    d.line([(290, BASE - 8), (290, BASE - 1)], fill=hx("5a4a30"))
    if lit:
        light(img, "ellipse", [282, 128, 306, 150], hx("ffe0a0"), 0.35, 4)
        light(img, "rect", [212, 92, 280, 152], hx("ffd890"), 0.25, 8)
        light(img, "rect", [204, 30, 252, 66], hx("ffc870"), 0.25, 6)
        light(img, "rect", [184, 90, 202, 124], hx("ffc870"), 0.2, 4)


def library(img, m, mode):
    d = ImageDraw.Draw(img)
    x0, x1 = 310, 400
    ashlar(img, (x0, 6, x1, BASE), m["lib"], 9, course=10, block=24)
    # entablature: cornice with modillions, inscribed frieze
    d.rectangle([x0 - 2, 4, x1 + 2, 12], fill=m["lib_l"])
    d.line([(x0 - 2, 4), (x1 + 2, 4)], fill=mul(m["lib_l"], 1.15))
    for x in range(x0, x1, 5):
        d.rectangle([x, 12, x + 2, 14], fill=m["lib_d"])
    shadow(img, "rect", [x0, 14, x1, 17], 0.4, 1)
    d.rectangle([x0, 17, x1, 29], fill=mul(m["lib"], 1.05))
    text(img, (355, 23), "PUBLIC LIBRARY", mul(m["lib_d"], 0.6), size=8)
    d.rectangle([x0, 30, x1, 33], fill=m["lib_l"])
    # columns
    for cx in (320, 390):
        d.rectangle([cx - 7, 34, cx + 7, 39], fill=m["lib_l"])
        d.ellipse([cx - 9, 34, cx - 4, 39], outline=m["lib_d"])
        d.ellipse([cx + 4, 34, cx + 9, 39], outline=m["lib_d"])
        hgrad(img, (cx - 6, 40, cx + 6, 154), m["lib_l"], m["lib_d"])
        for fx in range(cx - 4, cx + 6, 3):
            d.line([(fx, 41), (fx, 153)], fill=mul(m["lib_d"], 0.85))
        d.rectangle([cx - 8, 154, cx + 8, 160], fill=m["lib_l"])
        d.line([(cx - 8, 160), (cx + 8, 160)], fill=m["lib_d"])
    # deep arched doorway with bronze-studded doors and a fanlight
    d.rectangle([334, 64, 376, 160], fill=mul(m["lib_d"], 0.55))
    d.pieslice([334, 44, 376, 84], 180, 360, fill=mul(m["lib_d"], 0.55))
    d.arc([332, 42, 378, 86], 180, 360, fill=m["lib_l"], width=2)
    d.rectangle([338, 82, 372, 160], fill=m["wood"])
    for dx in (338, 356):
        d.rectangle([dx + 2, 86, dx + 15, 118], outline=m["wood_l"])
        d.rectangle([dx + 2, 124, dx + 15, 156], outline=m["wood_l"])
        for y in range(90, 156, 8):
            d.point((dx + 8, y), fill=hx("a08040"))
    d.line([(355, 82), (355, 160)], fill=mul(m["wood"], 0.5))
    fan = m["lit2"] if mode == "night" else m["glass"]
    d.pieslice([340, 52, 370, 82], 180, 360, fill=fan)
    for i in range(6):
        a = math.pi + math.pi * (i + 0.5) / 6
        d.line([(355, 81), (355 + 15 * math.cos(a), 81 + 15 * math.sin(a))], fill=m["wood"])
    d.rectangle([338, 80, 372, 82], fill=m["lib_l"])
    # steps
    d.rectangle([328, 160, 382, 164], fill=m["lib_l"])
    d.rectangle([324, 164, 386, BASE], fill=mul(m["lib_l"], 0.9))
    d.line([(328, 160), (382, 160)], fill=mul(m["lib_l"], 1.15))
    d.line([(324, 164), (386, 164)], fill=mul(m["lib_l"], 1.15))
    # bracket lanterns
    for lx in (330, 380):
        d.line([(lx, 72), (lx + (4 if lx < 355 else -4), 72)], fill=m["iron"])
        d.rectangle([lx - 3, 70, lx + 3, 82], fill=m["iron"])
        d.rectangle([lx - 2, 72, lx + 2, 80], fill=m["bulb"] if mode == "night" else mul(m["bulb"], 0.7))
        d.polygon([(lx - 4, 70), (lx, 66), (lx + 4, 70)], fill=m["iron"])
        if mode == "night":
            light(img, "ellipse", [lx - 16, 58, lx + 16, 96], hx("ffd890"), 0.4, 6)
    if mode == "night":
        light(img, "rect", [338, 50, 372, 84], hx("ffc070"), 0.2, 4)
        shadow(img, "rect", [334, 84, 376, 160], 0.25, 4)


def drugstore(img, m, mode):
    d = ImageDraw.Draw(img)
    x0, x1 = 400, 420
    d.rectangle([x0, 18, x1, BASE], fill=m["terra"])
    for y in range(22, BASE, 7):
        d.line([(x0, y), (x1, y)], fill=mul(m["terra"], 0.8))
    d.rectangle([x0 - 1, 16, x1 + 1, 21], fill=mul(m["terra"], 1.25))
    window(img, (404, 30, 416, 54), m, lit=False, seed=31, blind=0.6, sash=True)
    # corner shop window full of apothecary globes
    d.rectangle([x0, 94, x1, BASE], fill=m["wood"])
    lit = mode == "night"
    vgrad(img, (402, 100, 418, 150), m["lit"] if lit else m["glass_l"], m["lit2"] if lit else m["glass"])
    d.ellipse([403, 120, 409, 128], fill=hx("c02828"))
    d.ellipse([411, 116, 417, 124], fill=hx("28a050"))
    d.line([(406, 116), (406, 120)], fill=hx("c02828"))
    d.line([(414, 112), (414, 116)], fill=hx("28a050"))
    d.rectangle([402, 152, 418, BASE - 1], fill=mul(m["terra"], 0.6))
    # vertical DRUGS sign
    d.line([(404, 58), (424, 58)], fill=m["iron"])
    d.rectangle([406, 60, 420, 120], fill=hx("0c1410") if lit else hx("3a4a40"))
    d.rectangle([406, 60, 420, 120], outline=m["neon_green"] if lit else mul(m["neon_green"], 0.8))
    for i, ch in enumerate("DRUGS"):
        text(img, (413, 68 + i * 11), ch, m["neon_green"] if lit else hx("d8e0d0"), size=8)
    if lit:
        light(img, "rect", [398, 54, 428, 126], m["neon_green"], 0.4, 8)
        light(img, "rect", [400, 96, 420, 152], hx("ffd890"), 0.25, 5)
    shadow(img, "rect", [x1 - 3, 18, x1 + 1, BASE], 0.3, 1)


# --------------------------------------------------------------------------------------------- ground

def jx(xb, y):
    """x of a sidewalk joint that meets the curb at xb, at height y (gentle perspective)."""
    return VP[0] + (xb - VP[0]) * (y - VP[1]) / (CURB - VP[1])


PUDDLES = [(36, 226, 104, 236), (176, 188, 232, 196), (300, 214, 352, 222), (382, 182, 420, 188),
           (124, 206, 150, 211)]


def sidewalk(img, m, mode):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, BASE, W - 1, CURB), m["walk0"], m["walk1"])
    rnd = random.Random(81)
    rows = [BASE, 176, 188, 203, 222, CURB]
    for r in range(len(rows) - 1):
        for xb in range(-200, W + 240, 46):
            off = 0 if r % 2 else 23
            xa, xb2 = xb + off, xb + off + 46
            k = 0.95 + rnd.random() * 0.1
            poly = [(jx(xa, rows[r]), rows[r]), (jx(xb2, rows[r]), rows[r]),
                    (jx(xb2, rows[r + 1]), rows[r + 1]), (jx(xa, rows[r + 1]), rows[r + 1])]
            src = mix(m["walk0"], m["walk1"], (rows[r] - BASE) / (CURB - BASE))
            d.polygon(poly, fill=mul(src, k))
            d.line([poly[0], poly[3]], fill=m["joint"])
        d.line([(0, rows[r]), (W, rows[r])], fill=m["joint"])
    noise(img, (0, BASE, W - 1, CURB), 5, 82)
    # cracks
    for _ in range(14):
        x, y = rnd.randint(0, W), rnd.randint(BASE + 4, CURB - 4)
        for _ in range(rnd.randint(3, 7)):
            nx, ny = x + rnd.randint(-4, 4), y + rnd.randint(-1, 2)
            d.line([(x, y), (nx, ny)], fill=mul(m["joint"], 0.9))
            x, y = nx, ny
    # steel cellar doors in front of the lunch counter
    plate = hx("2a2c34") if mode == "night" else hx("5a5c62")
    d.polygon([(jx(220, 174), 174), (jx(272, 174), 174), (jx(272, 186), 186), (jx(220, 186), 186)], fill=plate)
    d.line([(jx(246, 174), 174), (jx(246, 186), 186)], fill=mul(plate, 0.6))
    for y in range(176, 186, 3):
        for x in range(222, 270, 4):
            d.point((jx(x, y) + (y % 2) * 2, y), fill=mul(plate, 1.4))
    # foot of the walls in shadow
    shadow(img, "rect", [0, BASE - 2, W, BASE + 6], 0.55, 3)


def curb_and_road(img, m, mode):
    d = ImageDraw.Draw(img)
    d.rectangle([0, CURB, W, CURB + 2], fill=m["curb"])
    d.rectangle([0, CURB + 3, W, GUTTER], fill=m["curb_d"])
    for x in range(0, W, 38):
        d.line([(x, CURB), (x, GUTTER)], fill=mul(m["curb_d"], 0.7))
    d.line([(0, CURB), (W, CURB)], fill=mul(m["curb"], 1.2))
    # gutter water
    d.rectangle([0, GUTTER + 1, W, GUTTER + 3], fill=mix(m["cob1"], m["glass_l"], 0.4))
    # cobbles and a streetcar rail
    rnd = random.Random(91)
    d.rectangle([0, GUTTER + 4, W, FULL_H], fill=mul(m["cob1"], 0.7))
    y, h = GUTTER + 4, 3
    row = 0
    while y < FULL_H:
        x = -rnd.randint(0, 8)
        while x < W:
            w = rnd.randint(6, 10) + row // 2
            c = mix(m["cob1"], m["cob2"], rnd.random())
            d.rounded_rectangle([x + 1, y, x + w - 1, y + h - 1], radius=1, fill=c)
            d.line([(x + 2, y), (x + w - 3, y)], fill=mix(c, m["cob_l"], 0.4))
            x += w
        y += h + 1
        h = min(6, h + 1)
        row += 1
    d.rectangle([0, 262, W, 263], fill=mul(m["chrome"], 0.45))
    d.line([(0, 262), (W, 262)], fill=mul(m["chrome"], 0.8))


def reflections(img, m, mode):
    """Wet paving mirrors the lit facades: a rippled, blurred, flipped copy blended into the sidewalk."""
    src = img.crop((0, BASE - (CURB - BASE), W, BASE)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    src = src.filter(ImageFilter.GaussianBlur(1.2))
    rip = Image.new("RGB", src.size)
    rnd = random.Random(7)
    for y in range(src.height):
        dx = int(round(math.sin(y * 0.9 + rnd.random()) * (1 + y / 30)))
        rip.paste(src.crop((0, y, W, y + 1)), (dx, y))
    rip = rip.resize((W, CURB - BASE), Image.Resampling.BILINEAR)
    mask = Image.new("L", (W, CURB - BASE), 0)
    md = ImageDraw.Draw(mask)
    base_k = 0.32 if mode == "night" else 0.22
    for y in range(CURB - BASE):
        md.line([(0, y), (W, y)], fill=int(255 * base_k * (1 - y / (CURB - BASE)) ** 0.6))
    for (px0, py0, px1, py1) in PUDDLES:
        md.ellipse([px0, py0 - BASE, px1, py1 - BASE], fill=int(255 * (0.75 if mode == "night" else 0.6)))
    mask = mask.filter(ImageFilter.GaussianBlur(1.5))
    region = img.crop((0, BASE, W, CURB))
    blend = ImageChops.screen(region, rip) if mode == "night" else Image.blend(region, rip, 0.7)
    img.paste(Image.composite(blend, region, mask), (0, BASE))
    d = ImageDraw.Draw(img)
    for (px0, py0, px1, py1) in PUDDLES:  # puddle rims
        d.arc([px0, py0, px1, py1], 200, 340, fill=mul(m["walk1"], 1.3))
    # long vertical streaks under the brightest signs
    if mode == "night":
        for (x, w, col, k) in ((129, 5, m["neon_red"], 0.4), (78, 30, hx("ffd890"), 0.35),
                               (245, 50, hx("ffd890"), 0.3), (413, 6, m["neon_green"], 0.4),
                               (162, 4, hx("d0e0b0"), 0.25), (330, 3, hx("ffd890"), 0.3),
                               (380, 3, hx("ffd890"), 0.3)):
            light(img, "rect", [x - w // 2, BASE + 2, x + w // 2, CURB - 6], col, k, 3)


# --------------------------------------------------------------------------------------------- near objects

def lamppost(d, x, m, mode):
    iron, hi = m["iron"], m["iron_l"]
    g = CURB
    d.polygon([(x - 8, g), (x - 6, g - 4), (x - 5, g - 18), (x + 5, g - 18), (x + 6, g - 4), (x + 8, g)], fill=iron)
    for y in (g - 18, g - 12, g - 4):
        d.rectangle([x - 6, y - 1, x + 6, y], fill=hi)
    d.rectangle([x - 2, 70, x + 2, g - 18], fill=iron)
    d.line([(x - 1, 72), (x - 1, g - 19)], fill=hi)
    for y in (110, 150):
        d.rectangle([x - 3, y, x + 3, y + 3], fill=iron)
        d.line([(x - 3, y), (x + 3, y)], fill=hi)
    d.rectangle([x - 4, 64, x + 4, 70], fill=iron)
    d.line([(x - 4, 64), (x + 4, 64)], fill=hi)
    glow = hx("fff0c0") if mode == "night" else hx("d8d4c8")
    d.ellipse([x - 7, 42, x + 7, 66], fill=glow)
    d.ellipse([x - 4, 46, x + 3, 60], fill=hx("fffaf0") if mode == "night" else hx("eceae4"))
    d.chord([x - 8, 38, x + 8, 50], 180, 360, fill=iron)
    d.rectangle([x - 8, 43, x + 8, 45], fill=iron)
    d.line([(x, 30), (x, 38)], fill=iron)
    d.ellipse([x - 1, 28, x + 1, 30], fill=iron)


def hydrant(d, x, m, mode):
    red = hx("6a1a18") if mode == "night" else hx("a8302a")
    g = CURB
    d.rectangle([x - 6, g - 3, x + 6, g], fill=mul(red, 0.7))
    d.rectangle([x - 4, g - 18, x + 4, g - 3], fill=red)
    d.rectangle([x - 7, g - 14, x + 7, g - 10], fill=red)
    d.chord([x - 4, g - 23, x + 4, g - 14], 180, 360, fill=red)
    d.rectangle([x - 1, g - 25, x + 1, g - 22], fill=red)
    d.line([(x - 3, g - 17), (x - 3, g - 4)], fill=mul(red, 1.6))
    d.rectangle([x - 5, g - 19, x + 5, g - 18], fill=mul(red, 1.3))


def fender(d, wx, wy, a0, a1, col, hi):
    """A pressed-steel wing over a wheel: the band between two arcs, highlighted along its crown."""
    outer, inner = [], []
    for i in range(25):
        t = math.radians(a0 + (a1 - a0) * i / 24)
        outer.append((wx + 22 * math.cos(t), wy + 21 * math.sin(t)))
        inner.append((wx + 17 * math.cos(t), wy + 17 * math.sin(t)))
    d.polygon(outer + inner[::-1], fill=col)
    d.line(outer[3:-3], fill=hi)


def wheel(d, wx, g, m):
    tyre, spoke, chrome = m["tyre"], m["spoke"], m["chrome"]
    d.ellipse([wx - 15, g - 30, wx + 15, g], fill=tyre)
    d.arc([wx - 14, g - 29, wx + 14, g - 1], 200, 300, fill=mul(tyre, 3.0))
    d.ellipse([wx - 10, g - 25, wx + 10, g - 5], fill=mul(tyre, 1.8))
    for ang in range(0, 360, 24):
        r = math.radians(ang)
        d.line([(wx + 2 * math.cos(r), g - 15 + 2 * math.sin(r)), (wx + 9 * math.cos(r + 0.3), g - 15 + 9 * math.sin(r + 0.3))],
               fill=mul(spoke, 0.85))
    d.ellipse([wx - 10, g - 25, wx + 10, g - 5], outline=spoke)
    d.ellipse([wx - 3, g - 18, wx + 3, g - 12], fill=chrome)
    d.point((wx - 1, g - 17), fill=(255, 255, 255))


def automobile(d, x0, m, mode):
    """A 1920s two-door sedan in profile, nose to the left, parked at the kerb."""
    g = ROAD_GROUND
    body, dark, hi = m["car"], m["car_d"], m["car_l"]
    chrome, tyre = m["chrome"], m["tyre"]
    fw, rw = x0 + 38, x0 + 138
    # chassis shadow and splash aprons
    d.rectangle([x0 + 14, g - 30, x0 + 160, g - 22], fill=mul(dark, 0.6))
    d.ellipse([x0 + 154, g - 56, x0 + 170, g - 24], fill=tyre)
    d.arc([x0 + 156, g - 54, x0 + 168, g - 26], 300, 60, fill=mul(chrome, 0.6))
    # hood
    d.polygon([(x0 + 18, g - 58), (x0 + 66, g - 61), (x0 + 66, g - 27), (x0 + 18, g - 30)], fill=body)
    # cabin with a rounded rear quarter and a trunk bustle
    cab = [(x0 + 64, g - 61), (x0 + 69, g - 76), (x0 + 76, g - 79), (x0 + 136, g - 79)]
    for i in range(1, 9):
        t = math.radians(-90 + 90 * i / 8)
        cab.append((x0 + 136 + 16 * math.cos(t), g - 63 + 16 * math.sin(t)))
    cab += [(x0 + 154, g - 44), (x0 + 162, g - 38), (x0 + 163, g - 30), (x0 + 158, g - 26), (x0 + 64, g - 26)]
    d.polygon(cab, fill=body)
    d.polygon([(x0 + 64, g - 61), (x0 + 69, g - 76), (x0 + 76, g - 79), (x0 + 136, g - 79)] +
              [(x0 + 136 + 16 * math.cos(math.radians(-90 + 90 * i / 8)), g - 63 + 16 * math.sin(math.radians(-90 + 90 * i / 8)))
               for i in range(1, 9)] + [(x0 + 152, g - 55), (x0 + 64, g - 55)], fill=mix(body, dark, 0.45))
    d.line([(x0 + 76, g - 79), (x0 + 136, g - 79)], fill=hi)
    d.polygon([(x0 + 64, g - 77), (x0 + 74, g - 80), (x0 + 74, g - 77)], fill=dark)
    d.arc([x0 + 120, g - 79, x0 + 152, g - 47], 270, 350, fill=hi)
    d.line([(x0 + 18, g - 58), (x0 + 66, g - 61)], fill=hi)
    # windows with a slanting sheen
    glass = mix(m["glass"], m["glass_l"], 0.25)
    d.polygon([(x0 + 70, g - 58), (x0 + 73, g - 72), (x0 + 77, g - 74), (x0 + 105, g - 74), (x0 + 105, g - 58)], fill=glass)
    d.polygon([(x0 + 110, g - 74), (x0 + 134, g - 74), (x0 + 142, g - 71), (x0 + 146, g - 64), (x0 + 147, g - 58),
               (x0 + 110, g - 58)], fill=glass)
    for sx in (80, 120):
        d.polygon([(x0 + sx, g - 58), (x0 + sx + 7, g - 74), (x0 + sx + 11, g - 74), (x0 + sx + 4, g - 58)],
                  fill=mix(glass, m["glass_l"], 0.55))
    d.line([(x0 + 65, g - 61), (x0 + 70, g - 77)], fill=chrome)
    # beltline, doors, handle, hood louvres
    d.line([(x0 + 18, g - 55), (x0 + 156, g - 55)], fill=hi)
    d.line([(x0 + 18, g - 54), (x0 + 156, g - 54)], fill=dark)
    d.line([(x0 + 107, g - 76), (x0 + 107, g - 27)], fill=dark)
    d.line([(x0 + 67, g - 56), (x0 + 67, g - 27)], fill=dark)
    d.rectangle([x0 + 100, g - 50, x0 + 104, g - 49], fill=chrome)
    for x in range(x0 + 32, x0 + 60, 3):
        d.line([(x, g - 50), (x, g - 38)], fill=dark)
    d.line([(x0 + 18, g - 34), (x0 + 160, g - 34)], fill=mul(body, 1.3))
    # wheels, wings and running board
    wheel(d, fw, g, m)
    wheel(d, rw, g, m)
    fender(d, fw, g - 15, 165, 352, dark, hi)
    fender(d, rw, g - 15, 188, 378, dark, hi)
    d.rectangle([x0 + 58, g - 25, x0 + 118, g - 21], fill=dark)
    d.line([(x0 + 58, g - 25), (x0 + 118, g - 25)], fill=mul(chrome, 0.6))
    # radiator shell, cap, headlamp, bumpers, spare
    d.rectangle([x0 + 11, g - 62, x0 + 19, g - 29], fill=mul(chrome, 0.75))
    d.rectangle([x0 + 13, g - 60, x0 + 17, g - 31], fill=mul(dark, 0.8))
    for y in range(g - 58, g - 31, 3):
        d.line([(x0 + 13, y), (x0 + 17, y)], fill=mul(chrome, 0.35))
    d.rectangle([x0 + 14, g - 66, x0 + 16, g - 62], fill=chrome)
    d.line([(x0 + 6, g - 36), (x0 + 12, g - 36)], fill=mul(chrome, 0.7))
    d.line([(x0 + 8, g - 36), (x0 + 8, g - 41)], fill=mul(chrome, 0.7))
    d.ellipse([x0 + 3, g - 51, x0 + 13, g - 41], fill=mul(chrome, 0.8))
    d.ellipse([x0 + 4, g - 50, x0 + 9, g - 42], fill=hx("c8c0a8") if mode == "night" else hx("d0d4d8"))
    d.rectangle([x0 - 3, g - 28, x0 + 8, g - 26], fill=chrome)
    d.line([(x0 + 2, g - 26), (x0 + 2, g - 22)], fill=mul(chrome, 0.6))
    d.rectangle([x0 + 160, g - 28, x0 + 172, g - 26], fill=chrome)


def near_layer(m, mode):
    layer = Image.new("RGBA", (W, FULL_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in LAMPS:
        lamppost(d, x, m, mode)
    hydrant(d, HYDRANT_X, m, mode)
    automobile(d, CAR_X, m, mode)
    return layer


# --------------------------------------------------------------------------------------------- weather & light

def lamp_light(img, m, mode):
    for x in LAMPS:
        if mode == "night":
            light(img, "ellipse", [x - 80, 160, x + 80, 252], hx("f0c070"), 0.32, 18)
            light(img, "rect", [x - 4, CURB + 4, x + 4, FULL_H], hx("ffe0a0"), 0.35, 3)
        else:
            shadow(img, "ellipse", [x - 30, CURB - 3, x + 4, CURB + 2], 0.25, 2)


def halos(img, mode):
    if mode != "night":
        return
    for x in LAMPS:
        light(img, "ellipse", [x - 34, 22, x + 34, 88], hx("ffd890"), 0.55, 12)
        light(img, "ellipse", [x - 70, -10, x + 70, 130], hx("f0b060"), 0.18, 26)


def car_shading(img, m, mode):
    x0, g = CAR_X, ROAD_GROUND
    shadow(img, "ellipse", [x0 - 6, g - 6, x0 + 176, g + 6], 0.7, 3)
    if mode == "night":
        # warm rim from the lamp behind the car, cold sheen on the roof
        light(img, "ellipse", [x0 + 120, g - 84, x0 + 220, g - 10], hx("f0c070"), 0.35, 10)
        light(img, "rect", [x0 + 70, g - 82, x0 + 150, g - 77], hx("8090c0"), 0.3, 2)
        light(img, "ellipse", [x0 - 6, g - 54, x0 + 10, g - 38], hx("ffe8b0"), 0.25, 3)


def paint(mode):
    m = NIGHT if mode == "night" else DAY
    img = Image.new("RGB", (W, FULL_H))
    sky(img, m, mode)
    vista(img, m, mode)
    aurelian(img, m, mode)
    alley(img, m, mode)
    walkup(img, m, mode)
    library(img, m, mode)
    drugstore(img, m, mode)
    sidewalk(img, m, mode)
    curb_and_road(img, m, mode)
    reflections(img, m, mode)
    lamp_light(img, m, mode)
    if mode == "night":
        shadow(img, "rect", [-40, -40, W + 40, FULL_H + 40], 0.18, 0, tint=hx("4050a0"))
    near = near_layer(m, mode)
    img.paste(near, (0, 0), near)
    car_shading(img, m, mode)
    halos(img, mode)
    if mode == "day":
        vignette(img, 0.25, tint=(150, 150, 160), blur=44)
    else:
        vignette(img, 0.55, tint=(20, 22, 44), blur=50)
    return img, near.getchannel("A").point(lambda v: 255 if v else 0)


def build():
    for mode in ("night",):
        base, mask = paint(mode)
        pal = palette_of(base, 128)
        px = pixelize(base, pal)
        save(px, "rooms", f"street_{mode}.png")
        save(cut(px, mask), "rooms", f"street_{mode}_fg.png")
