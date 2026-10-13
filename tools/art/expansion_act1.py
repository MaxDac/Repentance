"""Act 1 expansion locations: the Aurelian's fifth-floor linen room (puzzle 11) and Rizzo's Flowers on State
Street, the florist front of the Blue Lantern (puzzle 12), with their state overlays and inventory icons.

Overlays are cut where a state differs from the base painting; their positions are printed and go into
scenes/rooms/hotel_linen.tscn and scenes/rooms/blue_lantern_front.tscn."""
from PIL import Image, ImageDraw, ImageChops
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, cut)
from .furniture import Room3D
from .items import _icon
from .street import NIGHT, bricks, window as street_window

# ============================================================================================ linen room

FLOOR = 176
R = Room3D(FLOOR, 240, -200)
WALL = hx("8c957a")
WALL_D = hx("5e6650")
WAINS = hx("4a3a2a")
WAINS_D = hx("2c2218")
BRASS = hx("b08a3a")
BRASS_D = hx("5e4418")
WOOD = hx("5a3a22")
WOOD_D = hx("2e1c10")
LINEN = hx("e6e0cc")
LINEN_D = hx("aaa48e")
DOOR = (396, 446, 80)          # corridor door x0, x1, top
LIFT = (12, 88, 70)


def linen_shell(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 22), hx("4a4a3c"), hx("6a6c58"))
    d.line([(0, 22), (W, 22)], fill=hx("2a2a22"))
    # steam pipe along the ceiling
    d.rectangle([0, 8, W - 1, 12], fill=hx("5a5048"))
    d.line([(0, 8), (W, 8)], fill=hx("8a7e70"))
    for x in range(20, W, 64):
        d.rectangle([x, 6, x + 4, 14], fill=hx("3a322c"))
    vgrad(img, (0, 23, W - 1, 132), mul(WALL, 1.05), WALL_D)
    noise(img, (0, 23, W - 1, 132), 4, 501)
    d.rectangle([0, 130, W - 1, 133], fill=WOOD_D)
    vgrad(img, (0, 134, W - 1, FLOOR - 4), WAINS, WAINS_D)
    for x in range(0, W, 12):
        d.line([(x, 134), (x, FLOOR - 4)], fill=mul(WAINS_D, 0.8))
        d.line([(x + 1, 134), (x + 1, FLOOR - 4)], fill=mul(WAINS, 1.15))
    noise(img, (0, 134, W - 1, FLOOR - 4), 3, 502)
    d.rectangle([0, FLOOR - 4, W - 1, FLOOR], fill=hx("1e1610"))
    # stencilled sign
    d.rectangle([110, 36, 186, 50], fill=mul(WALL_D, 0.9))
    text(img, (148, 43), "LINEN 5", hx("e8e0c0"), size=8)


def linen_floor(img):
    """Worn red and cream linoleum squares in perspective."""
    px = img.load()
    vx, vy, y1 = 240, -200, FULL_H - 1
    c1, c2 = hx("4e2420"), hx("8a8068")
    for y in range(FLOOR + 1, FULL_H):
        k = (y - vy) / (y1 - vy)
        v = int(((y1 - vy) / (y - vy)) * 22)
        for x in range(W):
            u = int((((x - vx) / k) + 2000) // 30)
            c = c1 if (u + v) % 2 else c2
            shade = 0.62 + 0.3 * (y - FLOOR) / (FULL_H - FLOOR)
            px[x, y] = mul(c, shade)
    noise(img, (0, FLOOR + 1, W - 1, FULL_H - 1), 5, 503)
    shadow(img, "rect", [0, FLOOR, W, FLOOR + 8], 0.35, 4)


def lift(img):
    d = ImageDraw.Draw(img)
    x0, x1, top = LIFT
    d.rectangle([x0 - 4, top - 6, x1 + 4, FLOOR], fill=BRASS_D)
    d.rectangle([x0 - 2, top - 4, x1 + 2, FLOOR], fill=BRASS)
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("2a2218"), hx("120e0a"))
    # inside the car: a panelled back and a little lamp
    d.rectangle([x0 + 6, top + 8, x1 - 6, FLOOR - 10], outline=hx("3e3020"))
    light(img, "ellipse", [x0 + 20, top + 2, x1 - 20, top + 30], hx("ffd890"), 0.25, 6)
    # scissor gate
    for i in range(0, x1 - x0, 8):
        d.line([(x0 + i, top + 2), (x0 + i + 8, FLOOR - 4)], fill=BRASS_D)
        d.line([(x0 + i + 8, top + 2), (x0 + i, FLOOR - 4)], fill=BRASS)
    for x in range(x0, x1 + 1, 8):
        d.line([(x, top), (x, FLOOR - 2)], fill=hx("d8b060"))
    d.rectangle([x0, top, x1, top + 2], fill=hx("d8b060"))
    # floor dial above the gate
    cx, cy = (x0 + x1) // 2, top - 10
    d.pieslice([cx - 16, cy - 14, cx + 16, cy + 14], 180, 360, fill=BRASS_D)
    d.pieslice([cx - 13, cy - 11, cx + 13, cy + 11], 180, 360, fill=hx("e8dcb8"))
    for i in range(7):
        a = 180 + i * 30
        import math
        r = 11
        d.point((cx + int(r * math.cos(math.radians(a))), cy + int(r * math.sin(math.radians(a)))), fill=hx("3a2a18"))
    d.line([(cx, cy), (cx + 8, cy - 7)], fill=hx("8a1a1a"))
    text(img, (cx, top - 22), "5", hx("d8b060"), size=8)
    # call button
    d.rectangle([x1 + 6, 112, x1 + 12, 124], fill=BRASS_D)
    d.ellipse([x1 + 7, 115, x1 + 11, 119], fill=hx("e8c070"))


def shelves(img):
    d = ImageDraw.Draw(img)
    x0, x1, y0 = 100, 196, 58
    d.rectangle([x0, y0, x1, FLOOR - 2], fill=WOOD_D)
    rnd = random.Random(511)
    for i, y in enumerate(range(y0 + 4, FLOOR - 8, 24)):
        d.rectangle([x0 + 3, y, x1 - 3, y + 20], fill=hx("1a120a"))
        x = x0 + 5
        while x < x1 - 14:
            w = rnd.randint(12, 18)
            h = rnd.randint(9, 17)
            col = mix(LINEN, LINEN_D, rnd.random() * 0.5) if rnd.random() < 0.8 else hx("a8b8c8")
            for k in range(0, h, 3):
                d.rectangle([x, y + 20 - k - 3, x + w, y + 20 - k], fill=mul(col, 0.92 + 0.08 * (k % 2)))
                d.line([(x, y + 20 - k - 3), (x + w, y + 20 - k - 3)], fill=mul(col, 1.08))
            x += w + rnd.randint(1, 3)
        d.rectangle([x0, y + 20, x1, y + 23], fill=WOOD)
        d.line([(x0, y + 20), (x1, y + 20)], fill=hx("8a6040"))
    d.rectangle([x0, y0, x0 + 3, FLOOR - 2], fill=WOOD)
    d.rectangle([x1 - 3, y0, x1, FLOOR - 2], fill=WOOD)
    shadow(img, "rect", [x1 + 1, y0 + 4, x1 + 6, FLOOR], 0.3, 3)


GARMENTS = ((220, "maid"), (242, "jacket"), (264, "maid"))
RAIL_Y = 82


def hanger_shape(d, cx, y, col):
    d.arc([cx - 3, y - 6, cx + 1, y - 2], 180, 360, fill=col)
    d.line([(cx + 1, y - 4), (cx + 1, y - 1)], fill=col)
    d.line([(cx, y), (cx - 9, y + 7)], fill=col)
    d.line([(cx, y), (cx + 9, y + 7)], fill=col)
    d.line([(cx - 9, y + 7), (cx + 9, y + 7)], fill=col)


def maid_uniform(d, cx, y):
    """Black dress with puffed sleeves, white collar and cuffs, a bibbed white apron tied at the waist."""
    black, black_hi, black_d = hx("26262e"), hx("40404c"), hx("101014")
    white, white_d = hx("e4dece"), hx("aaa490")
    waist = y + 30
    # puffed sleeves behind the shoulders, white cuffs
    for s in (-1, 1):
        d.polygon([(cx + s * 7, y + 8), (cx + s * 12, y + 11), (cx + s * 12, y + 19), (cx + s * 8, y + 20)], fill=black)
        d.line([(cx + s * 12, y + 18), (cx + s * 9, y + 20)], fill=white)
    # bodice narrowing to the waist, then a full skirt
    d.polygon([(cx - 8, y + 8), (cx + 8, y + 8), (cx + 6, waist), (cx - 6, waist)], fill=black)
    d.polygon([(cx - 6, waist), (cx + 6, waist), (cx + 11, y + 80), (cx - 11, y + 80)], fill=black)
    d.line([(cx - 8, y + 9), (cx - 6, waist), (cx - 11, y + 79)], fill=black_hi)
    d.line([(cx + 8, y + 9), (cx + 6, waist), (cx + 11, y + 79)], fill=black_d)
    d.line([(cx - 11, y + 80), (cx + 11, y + 80)], fill=black_d)
    for fx in (-5, 0, 5):  # skirt folds
        d.line([(cx + fx * 0.6, waist + 6), (cx + fx, y + 79)], fill=black_d)
    # collar
    d.polygon([(cx - 4, y + 8), (cx, y + 12), (cx + 4, y + 8)], fill=white)
    # apron: straps over the shoulders, bib, waistband, skirt with a hem
    d.line([(cx - 5, y + 9), (cx - 4, y + 16)], fill=white)
    d.line([(cx + 5, y + 9), (cx + 4, y + 16)], fill=white)
    d.rectangle([cx - 4, y + 16, cx + 4, waist - 1], fill=white)
    d.line([(cx + 4, y + 16), (cx + 4, waist - 1)], fill=white_d)
    d.rectangle([cx - 7, waist, cx + 7, waist + 1], fill=white)
    d.polygon([(cx - 6, waist + 2), (cx + 6, waist + 2), (cx + 8, y + 70), (cx - 8, y + 70)], fill=white)
    d.line([(cx + 6, waist + 2), (cx + 8, y + 70)], fill=white_d)
    d.line([(cx - 7, y + 67), (cx + 7, y + 67)], fill=white_d)
    d.line([(cx - 2, waist + 4), (cx - 3, y + 66)], fill=white_d)


def porter_jacket(d, cx, y):
    """A short white porter's jacket: sleeves hanging at the sides, lapels, a row of brass buttons."""
    white, white_d, white_dd = hx("d8d2c0"), hx("a49e8a"), hx("7a7464")
    hem = y + 52
    for s in (-1, 1):
        d.polygon([(cx + s * 8, y + 9), (cx + s * 11, y + 12), (cx + s * 11, y + 46), (cx + s * 8, y + 46)],
                  fill=white_d)
        d.line([(cx + s * 11, y + 44), (cx + s * 8, y + 44)], fill=white_dd)
    d.polygon([(cx - 8, y + 8), (cx + 8, y + 8), (cx + 9, hem), (cx - 9, hem)], fill=white)
    d.line([(cx + 8, y + 9), (cx + 9, hem)], fill=white_d)
    d.line([(cx - 9, hem), (cx + 9, hem)], fill=white_dd)
    # lapels and the opening
    d.line([(cx - 4, y + 8), (cx, y + 18)], fill=white_dd)
    d.line([(cx + 4, y + 8), (cx, y + 18)], fill=white_dd)
    d.line([(cx, y + 18), (cx, hem)], fill=white_d)
    for by in range(y + 22, hem - 2, 7):
        d.point((cx + 2, by), fill=BRASS)
    d.line([(cx - 7, y + 34), (cx - 3, y + 34)], fill=white_d)  # pocket


def rack(img, with_hanger):
    d = ImageDraw.Draw(img)
    x0, x1 = 206, 294
    chrome, chrome_d = hx("b8bcc0"), hx("5a5e64")
    for x in (x0, x1):
        d.rectangle([x - 1, RAIL_Y, x + 1, FLOOR + 6], fill=chrome_d)
        d.line([(x - 1, RAIL_Y), (x - 1, FLOOR + 6)], fill=chrome)
        d.line([(x - 8, FLOOR + 6), (x + 8, FLOOR + 6)], fill=chrome_d, width=2)
        for cx in (x - 7, x + 7):
            d.ellipse([cx - 2, FLOOR + 6, cx + 2, FLOOR + 10], fill=hx("161616"))
    d.rectangle([x0 - 2, RAIL_Y - 2, x1 + 2, RAIL_Y], fill=chrome)
    d.line([(x0 - 2, RAIL_Y + 1), (x1 + 2, RAIL_Y + 1)], fill=chrome_d)
    for cx, kind in GARMENTS:
        hanger_shape(d, cx, RAIL_Y + 1, hx("8a8c90"))
        (maid_uniform if kind == "maid" else porter_jacket)(d, cx, RAIL_Y)
    if with_hanger:
        hanger_shape(d, 284, RAIL_Y + 1, hx("c8ccd0"))
    shadow(img, "rect", [x0 - 4, FLOOR + 4, x1 + 10, FLOOR + 12], 0.4, 3)


def cart(img, with_pliers):
    X0, X1, Z0, Z1 = 300, 364, 2, 24
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 2, a[1] - 3, b[0] + 8, a[1] + 4], 0.45, 3)
    grey, grey_d = hx("5a5850"), hx("34322c")
    for x in (X0 + 2, X1 - 2):
        for z in (Z0 + 2, Z1 - 2):
            R.line(img, (x, 4, z), (x, 40, z), grey_d, 2)
    R.box(img, X0, X1, 6, 9, Z0, Z1, grey, top=hx("6a685e"), side=grey_d)
    # laundry bag on the bottom shelf
    R.box(img, X0 + 4, X1 - 20, 9, 26, Z0 + 4, Z1 - 4, hx("c8c0a4"), top=hx("dcd4b8"))
    R.box(img, X1 - 18, X1 - 4, 9, 20, Z0 + 4, Z1 - 4, hx("a8b4c0"), top=hx("bcc8d4"))
    R.box(img, X0, X1, 40, 43, Z0, Z1, grey, top=hx("727066"), side=grey_d)
    # tray on top: a soap box, a brush and a duster
    R.box(img, X0 + 6, X0 + 18, 43, 48, Z0 + 6, Z0 + 14, hx("d8c070"), top=hx("e8d488"))
    R.box(img, X0 + 22, X0 + 34, 43, 46, Z0 + 4, Z0 + 10, hx("6a4a2a"), top=hx("8a6a3a"))
    d = ImageDraw.Draw(img)
    p = R.P(X1 - 6, 44, Z0 + 4)
    d.line([(p[0], p[1]), (p[0] + 2, p[1] - 22)], fill=hx("5a3a20"), width=2)
    d.ellipse([p[0] - 3, p[1] - 30, p[0] + 7, p[1] - 20], fill=hx("c8c0b0"))
    for x in (X0, X1):
        for z in (Z0 + 2, Z1 - 2):
            q = R.P(x, 0, z)
            d.ellipse([q[0] - 2, q[1] - 3, q[0] + 2, q[1] + 1], fill=hx("101010"))
    if with_pliers:
        q = R.P(X0 + 40, 43, Z0 + 16)
        x, y = int(q[0]), int(q[1])
        d.line([(x - 8, y + 1), (x, y - 1)], fill=hx("a82a24"), width=2)
        d.line([(x - 8, y - 3), (x, y - 1)], fill=hx("c83a30"), width=2)
        d.line([(x, y - 1), (x + 6, y - 2)], fill=hx("b8bcc0"), width=2)
        d.point((x, y - 1), fill=hx("40444a"))


def chute(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 330, 70, 368, 100
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], fill=hx("3a3a36"))
    vgrad(img, (x0, y0, x1, y1), hx("7a7c74"), hx("4a4c46"))
    d.line([(x0, y0 + 3), (x1, y0 + 3)], fill=hx("9a9c94"))
    d.rectangle([(x0 + x1) // 2 - 5, y1 - 8, (x0 + x1) // 2 + 5, y1 - 5], fill=hx("2a2a26"))
    text(img, ((x0 + x1) // 2, y0 + 12), "CHUTE", hx("e8e0c8"), size=8)


def corridor_door(img, open_):
    d = ImageDraw.Draw(img)
    x0, x1, top = DOOR
    d.rectangle([x0 - 6, top - 26, x1 + 6, FLOOR], fill=WOOD_D)
    d.rectangle([x0 - 3, top - 23, x1 + 3, FLOOR], fill=WOOD)
    # transom, a hopper light cracked open at the top
    ty0, ty1 = top - 20, top - 4
    vgrad(img, (x0, ty0, x1, ty1), hx("9aa078"), hx("6a704e"))
    d.rectangle([x0, ty0, x1, ty0 + 5], fill=hx("0e0c0a"))
    d.polygon([(x0, ty0 + 6), (x1, ty0 + 6), (x1 + 2, ty0 + 3), (x0 - 2, ty0 + 3)], fill=hx("c8c8a0"))
    d.line([(x1 - 3, ty0 + 3), (x1 - 3, ty0 + 8)], fill=hx("a8a8a0"))
    for x in range(x0 + 6, x1, 10):
        d.line([(x, ty0 + 5), (x, ty1)], fill=hx("5a5a40"))
    d.line([(x0, ty1 + 1), (x1, ty1 + 1)], fill=WOOD_D, width=2)
    if not open_:
        vgrad(img, (x0, top, x1, FLOOR - 1), hx("7a5034"), hx("4a2e1a"))
        for (a, b) in ((top + 6, top + 40), (top + 48, FLOOR - 8)):
            d.rectangle([x0 + 5, a, x1 - 5, b], outline=hx("2e1c10"))
            d.line([(x0 + 6, a + 1), (x1 - 6, a + 1)], fill=hx("9a6e4c"))
        d.ellipse([x0 + 4, top + 50, x0 + 9, top + 55], fill=BRASS)
        noise(img, (x0, top, x1, FLOOR), 3, 521)
        return
    # the corridor beyond: carpet runner, flock paper and the door of 507 across the way
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("5a2a30"), hx("3a1820"))
    for y in range(top + 4, FLOOR - 30, 8):
        for x in range(x0 + 2, x1, 8):
            d.point((x + (y // 8) % 2 * 4, y), fill=hx("7a4048"))
    d.polygon([(x0, FLOOR - 1), (x1, FLOOR - 1), (x1 - 8, FLOOR - 22), (x0 + 8, FLOOR - 22)], fill=hx("6a1e22"))
    d.line([(x0 + 14, FLOOR - 22), (x0 + 8, FLOOR - 1)], fill=hx("c8a050"))
    d.line([(x1 - 14, FLOOR - 22), (x1 - 8, FLOOR - 1)], fill=hx("c8a050"))
    ox0, ox1 = x0 + 12, x1 - 12
    d.rectangle([ox0 - 2, top + 16, ox1 + 2, FLOOR - 22], fill=hx("2a1a10"))
    vgrad(img, (ox0, top + 18, ox1, FLOOR - 22), hx("8a5a38"), hx("5a3a22"))
    d.rectangle([ox0 + 8, top + 24, ox1 - 8, top + 30], fill=BRASS_D)
    text(img, ((ox0 + ox1) // 2, top + 27), "507", hx("f0d080"), size=8)
    d.ellipse([ox1 - 6, top + 48, ox1 - 2, top + 52], fill=BRASS)
    light(img, "ellipse", [x0 - 10, top - 4, x1 + 10, top + 40], hx("ffd8a0"), 0.3, 8)
    # the door leaf swung back against the corridor wall, bolt drawn
    d.polygon([(x1 - 4, top), (x1, top - 2), (x1, FLOOR), (x1 - 4, FLOOR - 2)], fill=hx("3a2416"))
    d.rectangle([x1 - 4, top + 50, x1 - 1, top + 54], fill=hx("a8a8a0"))


def bulb(img):
    d = ImageDraw.Draw(img)
    cx = 254
    d.line([(cx, 12), (cx, 34)], fill=hx("1a1a16"))
    d.rectangle([cx - 2, 34, cx + 2, 38], fill=hx("6a5a3a"))
    d.ellipse([cx - 4, 37, cx + 4, 46], fill=hx("fff2c0"))
    light(img, "ellipse", [cx - 70, 0, cx + 70, 90], hx("ffe0a0"), 0.22, 18)
    light(img, "polygon", [(cx - 30, 46), (cx + 30, 46), (cx + 170, FULL_H), (cx - 170, FULL_H)], hx("ffd890"), 0.12, 24)


def paint_linen(hanger=True, pliers=True, door_open=False):
    img = Image.new("RGB", (W, FULL_H))
    linen_shell(img)
    linen_floor(img)
    lift(img)
    shelves(img)
    chute(img)
    corridor_door(img, door_open)
    rack(img, hanger)
    cart(img, pliers)
    bulb(img)
    vignette(img, 0.5, tint=(40, 34, 30), blur=40)
    return img


# ============================================================================================ florist front

BASE = 176
CURB = 246
M = NIGHT
GREEN = hx("1e3a2a")
GREEN_L = hx("3a6a4a")
GOLD = hx("d8b050")
COLD_DOOR = (362, 410, 78)
SHELF = (266, 308)


def florist_facade(img):
    d = ImageDraw.Draw(img)
    bricks(img, (0, 0, W - 1, BASE), M["brick1"], M["brick2"], M["mortar"], 601)
    # cornice and upstairs windows
    d.rectangle([0, 0, W - 1, 6], fill=M["stone_d"])
    for x in (80, 150, 220, 290):
        street_window(img, (x, 10, x + 26, 26), M, lit=(x == 150), seed=x, blind=0.6, sash=False,
                      sill=M["stone_d"])
    # neighbouring building to the left: stone with a lamp post in front
    d.rectangle([0, 0, 52, BASE], fill=M["stone_d"])
    for y in range(8, BASE, 9):
        d.line([(0, y), (52, y)], fill=mul(M["stone_d"], 0.8))
    d.rectangle([52, 0, 55, BASE], fill=M["iron"])
    # florist fascia and awning
    d.rectangle([60, 32, 340, 52], fill=GREEN)
    d.rectangle([60, 32, 340, 33], fill=GOLD)
    d.rectangle([60, 51, 340, 52], fill=GOLD)
    text(img, (200, 42), "RIZZO'S FLOWERS", GOLD, size=8)
    for i, x in enumerate(range(62, 340, 10)):
        col = GREEN_L if i % 2 else hx("c8c0a8")
        d.polygon([(x, 54), (x + 10, 54), (x + 12, 64), (x + 2, 64)], fill=col)
    d.line([(62, 64), (342, 64)], fill=mul(GREEN, 0.7))
    shadow(img, "rect", [60, 64, 342, 74], 0.4, 3)


ROSE = hx("b82838")
STEM, STEM_D, LEAF = hx("3a6a3a"), hx("1e3a22"), hx("4a8a44")


def bloom(d, x, y, kind, col):
    """One flower head a few pixels across: a shaded silhouette, petal edges and a centre."""
    sh, hi = mul(col, 0.62), mix(col, hx("ffffff"), 0.35)
    if kind == "rose":
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=sh)
        d.ellipse([x - 2, y - 2, x + 1, y + 1], fill=col)
        d.point((x, y), fill=mul(col, 0.45))
        d.point((x - 1, y), fill=mul(col, 0.45))
        d.point((x - 1, y - 1), fill=hi)
    elif kind == "carnation":
        d.ellipse([x - 2, y - 1, x + 2, y + 2], fill=col)
        for k in (-2, 0, 2):
            d.point((x + k, y - 2), fill=col)
        for k in (-1, 1):
            d.point((x + k, y - 1), fill=sh)
        d.line([(x - 1, y + 2), (x + 1, y + 2)], fill=sh)
        d.point((x, y + 3), fill=STEM)
    elif kind == "lily":
        for dx, dy in ((-3, 0), (3, 0), (-2, -2), (2, -2), (-1, 2), (1, 2)):
            d.line([(x, y), (x + dx, y + dy)], fill=col)
        d.point((x - 2, y - 1), fill=hi)
        d.point((x + 2, y - 1), fill=sh)
        d.point((x, y), fill=hx("c86a28"))
        d.point((x, y - 1), fill=hx("e8a040"))
    else:   # daisy / aster: a ring of petals round a dark eye
        for dx, dy in ((0, -2), (-2, 0), (2, 0), (0, 2), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            d.point((x + dx, y + dy), fill=col)
        d.point((x - 1, y - 2), fill=hi)
        d.point((x, y), fill=hx("6a3a18") if kind == "daisy" else mul(col, 0.5))


def potted(d, rnd, x, w, sy, col, kind, pot):
    """A small pot on a shop shelf with a few stems, leaves and distinct blooms."""
    d.polygon([(x, sy - 7), (x + w, sy - 7), (x + w - 1, sy), (x + 1, sy)], fill=pot)
    d.rectangle([x - 1, sy - 8, x + w + 1, sy - 7], fill=mix(pot, hx("ffffff"), 0.18))
    d.line([(x + w - 1, sy - 6), (x + w - 2, sy - 1)], fill=mul(pot, 0.7))
    heads = []
    for i in range(rnd.randint(4, 5)):
        fx = x + 1 + (w - 2) * (i + 0.5) / 5 + rnd.randint(-1, 1)
        fy = sy - 12 - rnd.randint(0, 9)
        heads.append((round(fx), fy))
        d.line([(round(fx), fy + 2), (x + w // 2 + (round(fx) - x - w // 2) // 2, sy - 8)], fill=STEM)
    for _ in range(3):
        lx, ly = x + rnd.randint(1, w - 1), sy - 9 - rnd.randint(0, 4)
        s = rnd.choice((-1, 1))
        d.line([(lx, ly), (lx + 2 * s, ly - 1)], fill=LEAF)
    for fx, fy in sorted(heads, key=lambda h: h[1]):
        bloom(d, fx, fy, kind, col)


def bucket_flowers(d, bx, kind, col, avoid=None):
    """An armful of cut flowers standing in a zinc bucket: stems, leaves, then clearly separate heads."""
    r = random.Random(bx)
    heads = []
    tries = 0
    while len(heads) < 13 and tries < 400:
        tries += 1
        fx, fy = bx + r.randint(-13, 13), 139 + r.randint(0, 13)
        if avoid and avoid[0] <= fx <= avoid[2] and avoid[1] <= fy <= avoid[3]:
            continue
        if any(abs(fx - hx_) < 5 and abs(fy - hy) < 4 for hx_, hy in heads):
            continue
        heads.append((fx, fy))
    for fx, fy in heads:
        d.line([(fx, fy + 2), (bx + (fx - bx) // 3, 158)], fill=STEM)
    for fx, fy in heads[::2]:
        mx, my = (fx + bx) // 2, (fy + 158) // 2
        s = 1 if fx < bx else -1
        d.polygon([(mx, my), (mx - 3 * s, my - 2), (mx - 4 * s, my - 1)], fill=LEAF)
        d.point((mx - 2 * s, my - 1), fill=STEM_D)
    for fx, fy in sorted(heads, key=lambda h: h[1]):
        bloom(d, fx, fy, kind, col)


def zinc_bucket(img, bx):
    d = ImageDraw.Draw(img)
    pts = [(bx - 12, 157), (bx + 12, 157), (bx + 10, BASE - 1), (bx - 10, BASE - 1)]
    d.polygon(pts, fill=hx("6a7078"))
    hgrad(img, (bx - 6, 158, bx + 9, BASE - 2), hx("7a8088"), hx("4a5058"))
    d.line([(bx - 11, 158), (bx - 9, BASE - 2)], fill=hx("9aa0a8"))
    d.line([(bx + 11, 158), (bx + 9, BASE - 2)], fill=hx("3a4048"))
    d.rectangle([bx - 13, 156, bx + 13, 157], fill=hx("a8b0b8"))
    d.line([(bx - 13, 158), (bx + 13, 158)], fill=hx("4a5058"))
    d.line([(bx - 11, 161), (bx + 11, 161)], fill=hx("4a5058"))
    d.line([(bx - 11, 162), (bx + 11, 162)], fill=hx("8a9098"))
    d.line([(bx - 10, BASE - 1), (bx + 10, BASE - 1)], fill=hx("3a4048"))


def display_window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 70, 72, 212, 150
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, BASE], fill=mul(GREEN, 0.8))
    vgrad(img, (x0, y0, x1, y1), hx("6a7a4a"), hx("3a4a2a"))
    rnd = random.Random(611)
    # shelves of potted flowers inside the shop
    kinds = ((hx("c83040"), "rose"), (hx("e8e4d8"), "carnation"), (hx("e8c040"), "daisy"), (hx("d878a0"), "aster"))
    pots = (hx("8a5a3a"), hx("6a6a70"), hx("9a6a48"))
    for sy in (98, 124):
        d.rectangle([x0, sy, x1, sy + 2], fill=hx("4a3020"))
        d.line([(x0, sy + 3), (x1, sy + 3)], fill=hx("2a1a10"))
        x = x0 + 4
        while x < x1 - 8:
            w = rnd.randint(8, 13)
            col, kind = rnd.choice(kinds)
            potted(d, rnd, x, w, sy, col, kind, rnd.choice(pots))
            x += w + 3
    # a fern hanging in the window
    for i in range(9):
        d.line([(110, y0 + 4), (100 + i * 3, y0 + 18 + (i % 3) * 3)], fill=hx("3a7a3a"))
    light(img, "rect", [x0, y0, x1, y1], hx("ffe8b0"), 0.3, 6)
    # reflections on the glass and the frame
    for k in range(3):
        d.line([(x0 + 10 + k * 40, y1), (x0 + 30 + k * 40, y0)], fill=mix(hx("c8d0c0"), hx("6a7a4a"), 0.6))
    d.rectangle([x0, y0, x1, y1], outline=mul(GREEN, 0.6))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=mul(GREEN, 0.6), width=2)
    # chalkboard propped in the corner of the window
    cx0, cy0, cx1, cy1 = 170, 116, 206, 148
    d.rectangle([cx0 - 2, cy0 - 2, cx1 + 2, cy1 + 2], fill=hx("6a4a2a"))
    d.rectangle([cx0, cy0, cx1, cy1], fill=hx("1e2422"))
    for i, y in enumerate((121, 126, 131)):
        d.line([(cx0 + 4, y), (cx1 - 4 - i * 5, y)], fill=hx("c8ccc4"))
    d.ellipse([cx0 + 13, 135, cx0 + 21, 143], fill=hx("4a80f0"))
    d.ellipse([cx0 + 15, 137, cx0 + 19, 141], fill=hx("80b0ff"))
    d.line([(cx0 + 17, 143), (cx0 + 17, 147)], fill=hx("6aa86a"))
    # stall below the window with zinc buckets: roses, white carnations, lilies
    d.rectangle([x0 - 6, 150, x1 + 6, 156], fill=hx("4a3020"))
    d.line([(x0 - 6, 150), (x1 + 6, 150)], fill=hx("7a5a3a"))
    for bx, fl, kind in ((84, ROSE, "rose"), (142, hx("eeeae0"), "carnation"), (190, hx("e8d080"), "lily")):
        zinc_bucket(img, bx)
        # the lilies keep clear of the chalked blue carnation behind them
        bucket_flowers(d, bx, kind, fl, avoid=(cx0 + 10, 132, cx0 + 24, 149) if kind == "lily" else None)
    text(img, (142, 170), "5c", hx("e8e4d0"), size=8)


def shop_door(img):
    d = ImageDraw.Draw(img)
    x0, x1, top = 222, 258, 74
    d.rectangle([x0 - 3, top - 3, x1 + 3, BASE], fill=mul(GREEN, 0.7))
    vgrad(img, (x0, top, x1, BASE - 1), GREEN_L, GREEN)
    vgrad(img, (x0 + 5, top + 5, x1 - 5, top + 50), hx("2a3440"), hx("141a22"))
    text(img, ((x0 + x1) // 2, top + 30), "CLOSED", hx("c8c0a0"), size=8)
    d.rectangle([x0 + 5, top + 58, x1 - 5, BASE - 8], outline=mul(GREEN, 0.6))
    d.ellipse([x1 - 8, top + 54, x1 - 4, top + 58], fill=GOLD)


def bluing_shelf(img, with_bluing):
    d = ImageDraw.Draw(img)
    x0, x1 = SHELF
    d.rectangle([x0, 100, x0 + 2, BASE], fill=hx("4a3020"))
    d.rectangle([x1 - 2, 100, x1, BASE], fill=hx("4a3020"))
    for y in (110, 134, 158):
        d.rectangle([x0, y, x1, y + 3], fill=hx("6a4a2a"))
        d.line([(x0, y), (x1, y)], fill=hx("9a7a4a"))
    # potted geraniums on top, tins of plant food and the bottles in the middle
    for px_ in (272, 288, 300):
        d.polygon([(px_ - 5, 101), (px_ + 5, 101), (px_ + 4, 109), (px_ - 4, 109)], fill=hx("a8583a"))
        for k in range(5):
            d.ellipse([px_ - 5 + k * 2, 94 - (k % 2) * 3, px_ - 2 + k * 2, 97 - (k % 2) * 3], fill=hx("c83040"))
        d.line([(px_, 101), (px_ - 2, 96)], fill=hx("3a6a3a"))
    for tx in (270, 279):
        d.rectangle([tx, 150, tx + 6, 157], fill=hx("8a8a70"))
        d.rectangle([tx, 152, tx + 6, 154], fill=hx("c8a040"))
    for bx, col in ((271, hx("6a4a2a")), (279, hx("3a5a3a"))):
        d.rectangle([bx, 122, bx + 5, 133], fill=col)
        d.rectangle([bx + 1, 119, bx + 4, 122], fill=mul(col, 0.8))
    if with_bluing:
        bx = 292
        d.rectangle([bx, 120, bx + 7, 133], fill=hx("1e3aa8"))
        d.rectangle([bx + 2, 116, bx + 5, 120], fill=hx("142a80"))
        d.rectangle([bx + 2, 114, bx + 5, 116], fill=hx("6a4a2a"))
        d.rectangle([bx, 124, bx + 7, 129], fill=hx("e8dcb0"))
        d.line([(bx + 1, 126), (bx + 6, 126)], fill=hx("1e3aa8"))
        d.line([(bx + 1, 121), (bx + 1, 132)], fill=hx("5a7ae8"))
    # watering can on the bottom shelf
    d.ellipse([284, 146, 300, 158], fill=hx("6a7a6a"))
    d.line([(299, 150), (305, 144)], fill=hx("6a7a6a"), width=2)
    shadow(img, "rect", [x1 + 1, 104, x1 + 6, BASE], 0.3, 3)


def cold_door(img, open_):
    d = ImageDraw.Draw(img)
    x0, x1, top = COLD_DOOR
    d.rectangle([x0 - 5, top - 5, x1 + 5, BASE], fill=M["iron"])
    vgrad(img, (x0, top, x1, BASE - 1), hx("2e4a3a"), hx("18281e"))
    for y in (top + 6, (top + BASE) // 2, BASE - 8):
        for x in range(x0 + 4, x1 - 2, 7):
            d.point((x, y), fill=hx("6a8a74"))
    text(img, ((x0 + x1) // 2, top + 46), "COLD", hx("b8c0a8"), size=8)
    text(img, ((x0 + x1) // 2, top + 56), "ROOM", hx("b8c0a8"), size=8)
    d.rectangle([x1 - 8, top + 50, x1 - 4, top + 64], fill=hx("6a6e74"))
    # speaking grille at eye height
    gx0, gy0, gx1, gy1 = x0 + 14, top + 22, x1 - 14, top + 32
    d.rectangle([gx0 - 2, gy0 - 2, gx1 + 2, gy1 + 2], fill=hx("8a8e94"))
    if open_:
        vgrad(img, (gx0, gy0, gx1, gy1), hx("ffd890"), hx("c88a40"))
        d.ellipse([gx0 + 4, gy0 + 3, gx0 + 8, gy0 + 6], fill=hx("f0f0e0"))
        d.ellipse([gx1 - 8, gy0 + 3, gx1 - 4, gy0 + 6], fill=hx("f0f0e0"))
        d.point((gx0 + 6, gy0 + 4), fill=hx("101010"))
        d.point((gx1 - 6, gy0 + 4), fill=hx("101010"))
        d.rectangle([gx0, gy0 - 12, gx1, gy0 - 3], fill=hx("6a6e74"))
        light(img, "ellipse", [gx0 - 20, gy0 - 14, gx1 + 20, gy1 + 22], hx("ffc870"), 0.4, 6)
    else:
        d.rectangle([gx0, gy0, gx1, gy1], fill=hx("4a4e54"))
        for x in range(gx0 + 2, gx1, 3):
            d.line([(x, gy0 + 1), (x, gy1 - 1)], fill=hx("26282c"))
    # unlit blue glass lantern on a bracket over the door
    lx = (x0 + x1) // 2
    d.line([(lx - 12, top - 14), (lx, top - 14)], fill=M["iron"])
    d.line([(lx, top - 14), (lx, top - 10)], fill=M["iron"])
    d.polygon([(lx - 4, top - 10), (lx + 4, top - 10), (lx + 3, top - 1), (lx - 3, top - 1)], fill=hx("2a3a7a"))
    d.line([(lx - 2, top - 8), (lx - 2, top - 3)], fill=hx("4a6ad8"))
    # three steps' worth of worn concrete at the foot
    d.rectangle([x0 - 6, BASE - 2, x1 + 6, BASE + 2], fill=hx("4a4a52"))


CARNATION = (hx("2e5ad8"), hx("5a8af0"), hx("a8c8ff"))
EMBER = (hx("c84a20"), hx("ff8a3a"), hx("ffd890"))
REGULAR_X = 442
# the smoker's strip: idle, arm rising, hand at the mouth, drawing on it, arm falling with a puff, idle with the
# puff drifting off. Each pose is the cigarette hand's elbow and hand offsets from the regular's centre line.
SMOKE_POSES = (
    {"elbow": (14, 136), "hand": (13, 150), "ember": 0, "puff": None},
    {"elbow": (17, 136), "hand": (11, 126), "ember": 0, "puff": None},
    {"elbow": (14, 130), "hand": (3, 114), "ember": 1, "puff": None},
    {"elbow": (14, 130), "hand": (3, 114), "ember": 2, "puff": None},
    {"elbow": (17, 136), "hand": (11, 126), "ember": 1, "puff": ((-3, 115, 2), (-6, 112, 2))},
    {"elbow": (14, 136), "hand": (13, 150), "ember": 0, "puff": ((-13, 101, 3), (-17, 96, 2), (-9, 106, 2))},
)


def _puff(d, cx, cy, r):
    """A dithered cloud of smoke: dense in the middle, every other pixel towards the edge so the wall shows."""
    dense, thin = hx("9a9eaa"), hx("6a6e7c")
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r - 1, cx + r + 2):
            q = ((x - cx) / (r + 1)) ** 2 + ((y - cy) / r) ** 2
            if q <= 0.5:
                d.point((x, y), fill=dense)
            elif q <= 1 and (x + y) % 2 == 0:
                d.point((x, y), fill=thin)


def regular(img, pose=0):
    """A member waiting by the wall in a dark overcoat, head bowed so the fedora hides his face, a blue carnation
    bright in his buttonhole and a cigarette in his hand. Painted on its own layer (the game animates the smoking);
    returns the figure's mask."""
    p = SMOKE_POSES[pose]
    fig = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fig)
    cx = REGULAR_X
    coat, coat_d, coat_l = hx("2c2a34"), hx("18171e"), hx("4a4856")
    skin, skin_d = hx("8a6a58"), hx("4a3830")
    hat, hat_d, hat_l, band = hx("3a3632"), hx("221f1d"), hx("5e5852"), hx("121012")
    # trouser legs and shoes
    d.rectangle([cx - 7, 162, cx - 2, BASE - 3], fill=hx("1c1a20"))
    d.rectangle([cx + 2, 162, cx + 7, BASE - 3], fill=hx("16151a"))
    d.line([(cx - 6, 163), (cx - 6, BASE - 4)], fill=hx("2c2a32"))
    d.rectangle([cx - 9, BASE - 3, cx - 1, BASE], fill=hx("0c0b0e"))
    d.rectangle([cx + 1, BASE - 3, cx + 9, BASE], fill=hx("0c0b0e"))
    d.line([(cx - 8, BASE - 3), (cx - 3, BASE - 3)], fill=hx("4a4650"))
    # overcoat: hunched shoulders, flared skirt, belt, the lamp catching its left edge
    d.polygon([(cx - 10, 116), (cx + 10, 116), (cx + 12, 123), (cx + 13, 164), (cx - 13, 164), (cx - 12, 123)],
              fill=coat)
    d.polygon([(cx + 3, 118), (cx + 10, 116), (cx + 12, 123), (cx + 13, 164), (cx + 4, 164)], fill=coat_d)
    d.line([(cx - 12, 123), (cx - 13, 163)], fill=coat_l)
    d.line([(cx + 12, 124), (cx + 13, 163)], fill=hx("34323e"))
    d.line([(cx - 10, 117), (cx - 5, 116)], fill=coat_l)
    d.rectangle([cx - 13, 141, cx + 13, 143], fill=coat_d)
    d.rectangle([cx - 1, 141, cx + 1, 143], fill=hx("8a8070"))
    d.line([(cx, 128), (cx, 163)], fill=coat_d)
    for y in (132, 150):
        d.point((cx - 2, y), fill=hx("0e0d12"))
    # a sliver of shirt and tie between the lapels
    d.polygon([(cx - 3, 117), (cx + 3, 117), (cx, 126)], fill=hx("b8b4aa"))
    d.line([(cx, 118), (cx, 125)], fill=hx("5a1a20"))
    d.line([(cx - 5, 117), (cx - 1, 128)], fill=coat_l)
    d.line([(cx + 5, 117), (cx + 1, 128)], fill=coat_d)
    # collar turned up against the rain
    d.polygon([(cx - 9, 117), (cx - 7, 109), (cx - 3, 112), (cx - 3, 117)], fill=coat)
    d.line([(cx - 9, 116), (cx - 7, 109)], fill=coat_l)
    d.polygon([(cx + 9, 117), (cx + 7, 109), (cx + 3, 112), (cx + 3, 117)], fill=coat_d)
    # the other hand deep in its pocket
    d.line([(cx - 12, 124), (cx - 11, 145)], fill=coat_d)
    d.line([(cx - 11, 146), (cx - 6, 148)], fill=hx("0e0d12"))
    # blue carnation in the left buttonhole, ruffled, catching the light
    dark, mid, hi = CARNATION
    d.ellipse([cx - 10, 119, cx - 4, 125], fill=dark)
    d.ellipse([cx - 9, 119, cx - 5, 123], fill=mid)
    for x in (cx - 9, cx - 7, cx - 5):
        d.point((x, 118), fill=mid)
    d.point((cx - 8, 120), fill=hi)
    d.point((cx - 6, 121), fill=hi)
    d.point((cx - 7, 122), fill=dark)
    d.point((cx - 9, 123), fill=mid)
    d.line([(cx - 6, 125), (cx - 5, 127)], fill=hx("3a7a3a"))
    # the chin, just showing under the brim
    d.rectangle([cx - 2, 111, cx + 2, 112], fill=skin_d)
    d.line([(cx - 1, 113), (cx + 1, 113)], fill=skin_d)
    # the smoking arm: sleeve, cuff, hand and cigarette
    ex, ey = cx + p["elbow"][0], p["elbow"][1]
    hx_, hy = cx + p["hand"][0], p["hand"][1]
    d.line([(cx + 10, 119), (ex, ey), (hx_ + 1, hy + 2)], fill=coat_d, width=5, joint="curve")
    d.line([(cx + 12, 121), (ex - 2, ey)], fill=coat, width=1)
    d.ellipse([hx_ - 1, hy - 1, hx_ + 2, hy + 2], fill=skin)
    d.point((hx_ + 2, hy + 1), fill=skin_d)
    d.point((hx_ - 1, hy), fill=mix(skin, hx("e0b090"), 0.5))
    ember = EMBER[p["ember"]]
    if p["hand"][1] > 130:
        d.line([(hx_ - 4, hy + 2), (hx_ - 2, hy + 2)], fill=hx("e8e4dc"))
        d.point((hx_ - 5, hy + 2), fill=ember)
        for k, (wx, wy) in enumerate(((-5, 0), (-4, -2), (-5, -4), (-6, -6), (-5, -8))):
            if k % 2 == 0 or p["puff"] is None:
                d.point((hx_ + wx, hy + wy), fill=hx("7a7e8a"))
    else:
        d.point((hx_ - 2, hy + 1), fill=hx("e8e4dc"))
        d.point((hx_ - 3, hy + 1), fill=ember)
    # fedora, tipped forward over the face and seen from above: a wide brim, the pinched crown sitting at its back,
    # and the front lip dipping over where the eyes would be
    d.ellipse([cx - 12, 101, cx + 12, 112], fill=hat_d)
    d.arc([cx - 12, 101, cx + 12, 112], 160, 300, fill=hat_l)
    d.polygon([(cx - 6, 105), (cx - 6, 98), (cx - 4, 95), (cx + 4, 95), (cx + 6, 98), (cx + 6, 105)], fill=hat)
    d.polygon([(cx - 6, 105), (cx - 6, 98), (cx - 4, 95), (cx - 2, 95), (cx - 3, 98), (cx - 3, 105)],
              fill=mix(hat, hat_l, 0.45))
    d.ellipse([cx - 4, 95, cx + 4, 100], fill=mix(hat, hat_l, 0.3))
    d.line([(cx, 95), (cx, 100)], fill=hat_d)
    d.point((cx - 1, 96), fill=hat_l)
    d.rectangle([cx - 6, 103, cx + 6, 105], fill=band)
    d.chord([cx - 12, 101, cx + 12, 113], 0, 180, fill=hat_d)
    d.arc([cx - 12, 101, cx + 12, 113], 25, 155, fill=hx("34302c"))
    d.line([(cx - 11, 107), (cx - 5, 110)], fill=mix(hat_d, hat_l, 0.5))
    if p["puff"]:
        for px_, py_, r in p["puff"]:
            _puff(d, cx + px_, py_, r)
    img.paste(fig, (0, 0), fig)
    mask = fig.getchannel("A")
    light(img, "ellipse", [cx - 12, 115, cx - 1, 129], hx("4a80f0"), 0.3, 3)
    if p["hand"][1] > 130:
        tx, ty = hx_ - 5, hy + 2
    else:
        tx, ty = hx_ - 3, hy + 1
    light(img, "ellipse", [tx - 3, ty - 3, tx + 3, ty + 2], hx("ff9040"), 0.15 + 0.15 * p["ember"], 1)
    return mask


def lamppost(img):
    d = ImageDraw.Draw(img)
    x = 28
    d.rectangle([x - 2, 40, x + 2, BASE + 30], fill=M["iron"])
    d.rectangle([x - 5, BASE + 24, x + 5, BASE + 32], fill=M["iron"])
    d.polygon([(x - 8, 34), (x + 8, 34), (x + 5, 24), (x - 5, 24)], fill=hx("e8d8a0"))
    d.rectangle([x - 9, 34, x + 9, 37], fill=M["iron"])
    light(img, "ellipse", [x - 60, 0, x + 60, 80], hx("ffe0a0"), 0.25, 14)


def florist_ground(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, BASE + 1, W - 1, CURB), M["walk1"], M["walk0"])
    y, step = BASE + 1, 6.0
    while y < CURB:
        d.line([(0, int(y)), (W, int(y))], fill=M["joint"])
        y += step
        step *= 1.3
    for x in range(-200, W + 200, 40):
        d.line([(240 + (x - 240) * 0.85, BASE + 1), (x, CURB)], fill=M["joint"])
    d.rectangle([0, CURB, W - 1, CURB + 5], fill=M["curb"])
    d.line([(0, CURB + 5), (W, CURB + 5)], fill=M["curb_d"])
    rnd = random.Random(631)
    for y in range(CURB + 6, FULL_H, 4):
        for x in range(-(y % 8), W, 8):
            d.rectangle([x, y, x + 6, y + 2], fill=mix(M["cob1"], M["cob2"], rnd.random()))
    noise(img, (0, BASE + 1, W - 1, FULL_H - 1), 4, 632)
    # wet reflections of the window and the lamp
    light(img, "rect", [80, BASE + 6, 200, CURB - 4], hx("ffe0a0"), 0.12, 6)
    light(img, "rect", [20, BASE + 10, 36, CURB], hx("ffe0a0"), 0.18, 4)


def paint_florist(bluing=True, grille_open=False, pose=None):
    """The street front. The regular is animated in the scene, so he is only painted when a smoking pose is given;
    returns the painting and the regular's mask (None without him)."""
    img = Image.new("RGB", (W, FULL_H))
    florist_facade(img)
    display_window(img)
    shop_door(img)
    bluing_shelf(img, bluing)
    cold_door(img, grille_open)
    florist_ground(img)
    # where the regular always stands: his shadow belongs to the pavement
    shadow(img, "ellipse", [REGULAR_X - 15, BASE - 2, REGULAR_X + 15, BASE + 5], 0.5, 2)
    mask = None if pose is None else regular(img, pose)
    lamppost(img)
    shadow(img, "rect", [-40, -40, W + 40, FULL_H + 40], 0.15, 0, tint=hx("4050a0"))
    # the rain itself is animated in the scene (scripts/Core/Rain.cs)
    vignette(img, 0.5, tint=(20, 22, 44), blur=46)
    return img, mask


# ============================================================================================ items

def hanger(d, im):
    c = hx("b8bcc4")
    d.arc([13, 1, 19, 7], 180, 30, fill=c)
    d.line([(16, 7), (16, 9)], fill=c)
    d.line([(16, 9), (3, 19)], fill=c, width=2)
    d.line([(16, 9), (29, 19)], fill=c, width=2)
    d.line([(3, 19), (29, 19)], fill=c, width=2)


def pliers(d, im):
    d.line([(3, 20), (15, 12)], fill=hx("b02a24"), width=3)
    d.line([(6, 22), (16, 14)], fill=hx("d03c30"), width=3)
    d.ellipse([13, 10, 18, 15], fill=hx("8a8e94"))
    d.polygon([(16, 10), (28, 4), (29, 6), (18, 13)], fill=hx("b8bcc4"))
    d.polygon([(17, 13), (29, 8), (29, 10), (18, 15)], fill=hx("8a8e94"))


def wire_hook(d, im):
    c = hx("c0c4cc")
    d.line([(3, 21), (25, 5)], fill=c, width=2)
    d.arc([22, 1, 30, 9], 200, 90, fill=c, width=2)
    d.line([(4, 21), (7, 21)], fill=hx("8a8e94"))


def _flower(d, col, hi):
    d.line([(16, 12), (12, 23)], fill=hx("3a7a3a"), width=2)
    d.polygon([(12, 18), (8, 15), (11, 20)], fill=hx("4a8a4a"))
    d.polygon([(14, 12), (18, 12), (17, 15), (15, 15)], fill=hx("3a7a3a"))
    for x, y in ((10, 6), (16, 3), (22, 6), (12, 10), (20, 10), (16, 7)):
        d.ellipse([x - 4, y - 3, x + 4, y + 3], fill=col)
    for x, y in ((11, 5), (17, 2), (21, 7), (15, 8)):
        d.point((x, y), fill=hi)


def carnation(d, im):
    _flower(d, hx("ece8dc"), hx("ffffff"))


def blue_carnation(d, im):
    _flower(d, hx("3a6ae0"), hx("9ac0ff"))


def bluing(d, im):
    d.rectangle([11, 7, 21, 22], fill=hx("1e3aa8"))
    d.rectangle([13, 3, 19, 7], fill=hx("142a80"))
    d.rectangle([13, 1, 19, 3], fill=hx("6a4a2a"))
    d.rectangle([11, 11, 21, 18], fill=hx("e8dcb0"))
    d.line([(13, 13), (19, 13)], fill=hx("1e3aa8"))
    d.line([(13, 16), (18, 16)], fill=hx("8a2a2a"))
    d.line([(12, 8), (12, 21)], fill=hx("5a7ae8"))


# ============================================================================================ build

def _overlay(base, state, name):
    diff = ImageChops.difference(base, state).convert("L").point(lambda v: 255 if v else 0)
    box = diff.getbbox()
    if box is None:
        raise ValueError(f"{name} does not differ from its base")
    save(cut(state, diff).crop(box), "rooms", f"{name}.png")
    print(f"  {name}.png at {box[:2]}")
    return box


def build_linen():
    variants = {
        "base": paint_linen(hanger=False, pliers=False),
        "hanger": paint_linen(hanger=True, pliers=False),
        "pliers": paint_linen(hanger=False, pliers=True),
        "door": paint_linen(hanger=False, pliers=False, door_open=True),
    }
    pal = palette_of(Image.blend(variants["base"], variants["door"], 0.5), 128)
    px = {k: pixelize(v, pal) for k, v in variants.items()}
    save(px["base"], "rooms", "hotel_linen.png")
    _overlay(px["base"], px["hanger"], "hotel_linen_hanger")
    _overlay(px["base"], px["pliers"], "hotel_linen_pliers")
    _overlay(px["base"], px["door"], "hotel_linen_door_open")
    return px["base"]


def build_florist():
    variants = {
        "base": paint_florist(bluing=False)[0],
        "bluing": paint_florist(bluing=True)[0],
        "grille": paint_florist(bluing=False, grille_open=True)[0],
    }
    frames = [paint_florist(bluing=False, pose=k) for k in range(len(SMOKE_POSES))]
    box = frames[0][1].getbbox()
    for _, mask in frames[1:]:
        b = mask.getbbox()
        box = (min(box[0], b[0]), min(box[1], b[1]), max(box[2], b[2]), max(box[3], b[3]))
    # the palette sees the regular at full contrast; the carnation, the cigarette's ember and the stall's roses are a
    # handful of pixels each, so their colours are pinned so quantising cannot grey them out or turn the roses orange
    src = Image.blend(variants["base"], variants["grille"], 0.5)
    src.paste(frames[0][0].crop(box), box[:2])
    pal = palette_of(src, 128) + list(CARNATION) + list(EMBER) + [ROSE, mul(ROSE, 0.62), mul(ROSE, 0.45)]
    px = {k: pixelize(v, pal) for k, v in variants.items()}
    save(px["base"], "rooms", "blue_lantern_front.png")
    _overlay(px["base"], px["bluing"], "blue_lantern_front_bluing")
    _overlay(px["base"], px["grille"], "blue_lantern_front_grille_open")
    fw, fh = box[2] - box[0], box[3] - box[1]
    strip = Image.new("RGBA", (fw * len(frames), fh), (0, 0, 0, 0))
    for k, (frame, mask) in enumerate(frames):
        strip.paste(cut(pixelize(frame, pal), mask).crop(box), (k * fw, 0))
    save(strip, "rooms", "blue_lantern_front_regular.png")
    print(f"  blue_lantern_front_regular.png at {box[:2]}, {len(frames)} frames of {fw}x{fh}")
    return px["base"]


def build_items():
    for name, fn in (("hanger", hanger), ("pliers", pliers), ("wire_hook", wire_hook), ("carnation", carnation),
                     ("bluing", bluing), ("blue_carnation", blue_carnation)):
        save(_icon(fn), "items", f"{name}.png")


def build():
    build_linen()
    build_florist()
    build_items()
