"""Outside the motel at night, in the rain: the back alley off the main road (the entrance under a buzzing MOTEL
sign, trash cans, a fruit crate and a fire escape whose drop ladder hangs out of reach), and the first-floor landing
of that fire escape, where Eleanor waits outside her lit window.

Both rooms are painted as albedo, lit (ambient night x albedo + neon and lamplight pools), then the light sources are
drawn over the top. The alley's states (the crate by the cans or under the ladder, the ladder lowered) are overlays:
crops of the state variant pixelized with the base palette, placed at the printed crop origins."""
import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import (W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, palette_of, pixelize, save, text,
                     cut, _mask)
from .street import bricks
from .act2_rooms import crate as fruit_crate

H = FULL_H
IRON, IRON_E, IRON_M, IRON_H = hx("12151c"), hx("7a8492"), hx("3e4552"), hx("b0b8c4")
NEON, NEON_HOT, NEON_DIM = hx("ff3048"), hx("ffb0b8"), hx("7a1a26")
AMBER, AMBER_HOT = hx("ffb050"), hx("ffe8b0")

# ------------------------------------------------------------------------------------------------ the alley

BASE = 192                       # foot of the motel's side wall
MOUTH = 92                       # the alley opens onto the main road left of this
LANDING_X, LANDING_Y = (236, 446), 100
LADDER_X = (282, 298)            # the drop ladder's rails
LADDER_CX = 290
RAISED_BOTTOM, LOWERED_BOTTOM = 150, 203
DOOR = (166, 112, 204, BASE)     # the entrance door's leaf
DOOR_SIGN = (160, 92, 210, 104)  # the small neon MOTEL over it
BLADE = (22, 24, 58, 124)        # the big sign on the front corner, seen across the alley mouth
WINDOWS = ((166, 36, 202, 84), (318, 36, 354, 90), (392, 36, 428, 90))
LIT_WINDOW = WINDOWS[1]
CRATE_HOME = (382, 174)          # by the trash cans
CRATE_UNDER = (LADDER_CX - 13, 174)
CRATE_SIZE = 26
CANS = ((418, 168), (446, 171))
LAMP = (395, 116)                # a caged bulb over the barred ground-floor window
PUDDLES = [(206, 220, 282, 230), (96, 242, 196, 258), (322, 246, 424, 262), (12, 208, 66, 216),
           (424, 214, 474, 222), (300, 206, 340, 212)]


def illuminate(img, ambient, lights):
    """albedo x (ambient + soft coloured light pools): lit surfaces keep their texture."""
    acc = Image.new("RGB", img.size, ambient)
    for shape, pts, col, k, blur in lights:
        m = _mask(img.size, shape, pts, k, blur).convert("RGB")
        acc = ImageChops.add(acc, ImageChops.multiply(Image.new("RGB", img.size, col), m))
    return ImageChops.multiply(img, acc)


def neon_text(img, xy, s, col, size=8, anchor="mm"):
    text(img, xy, s, col, size, anchor=anchor)


def sky(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 70), hx("0e1020"), hx("3a2434"))
    rnd = random.Random(5)
    for _ in range(7):  # low rain clouds lit from below by the city
        x, y = rnd.randint(-40, 520), rnd.randint(2, 40)
        light(img, "ellipse", [x - 80, y - 6, x + 80, y + 8], hx("5a3a4a"), 0.3, 7)
    d.line([(0, 18), (MOUTH, 30)], fill=hx("0a0a10"))  # a telephone wire across the street


def main_road(img):
    """The main road through the alley mouth: the block across the street with an all-night lunch-room at street
    level (signboard, scalloped awning, a counter and stools behind plate glass), sash windows upstairs, a lamp on
    the far kerb, and the wet road between."""
    d = ImageDraw.Draw(img)
    d.rectangle([0, 34, MOUTH, 186], fill=hx("2a2228"))
    d.polygon([(0, 34), (40, 34), (40, 28), (MOUTH, 28), (MOUTH, 40), (0, 40)], fill=hx("221c22"))
    bricks(img, (0, 40, MOUTH, 150), hx("4a2e2e"), hx("3a2426"), hx("1e1618"), 7, 4, 9)
    rnd = random.Random(8)
    for x in range(4, MOUTH - 8, 16):
        for y in (50, 76, 102):
            lit = rnd.random() < 0.35
            # a stone lintel, a sash with its meeting rail and a sill under each upstairs window
            d.rectangle([x - 1, y - 2, x + 9, y - 1], fill=hx("6a5a50"))
            d.rectangle([x, y, x + 8, y + 14], fill=hx("e0a050") if lit else hx("141820"))
            if lit:
                d.rectangle([x, y, x + 8, y + 5], fill=hx("a86a30"))  # the blind half down
                d.line([(x + 4, y + 5), (x + 4, y + 6)], fill=hx("6a4020"))
            else:
                d.line([(x + 1, y + 2), (x + 3, y)], fill=hx("2a3040"))  # a glint on the dark pane
            d.line([(x, y + 7), (x + 8, y + 7)], fill=hx("3a2a24"))
            d.line([(x + 4, y), (x + 4, y + 14)], fill=hx("3a2a24"))
            d.line([(x - 1, y + 15), (x + 9, y + 15)], fill=hx("6a5a50"))
    # the lunch-room's signboard across the fascia (lettered once the light is on, in lunch_room_lit)
    d.rectangle([0, 134, MOUTH, 149], fill=hx("1a1416"))
    d.rectangle([2, 136, 72, 147], fill=hx("1c3a2c"))
    d.rectangle([2, 136, 72, 147], outline=hx("8a7a50"))
    # the lunch-room: plate glass, a scalloped awning, a counter seen through the window
    d.rectangle([0, 150, MOUTH, 186], fill=hx("1a1416"))
    d.rectangle([4, 160, MOUTH - 4, 182], fill=hx("e8b060"))
    d.rectangle([4, 172, MOUTH - 4, 182], fill=hx("8a5a30"))
    for x in range(0, MOUTH, 6):
        stripe = hx("a83a30") if (x // 6) % 2 else hx("d8c8b0")
        d.polygon([(x, 150), (x + 6, 150), (x + 8, 157), (x + 2, 157)], fill=stripe)
        d.pieslice([x + 2, 155, x + 8, 161], 0, 180, fill=stripe)  # the valance's scallops
    d.line([(0, 150), (MOUTH, 150)], fill=hx("3a2420"))
    for x in range(0, MOUTH, 12):  # the awning's iron arms
        d.point((x + 1, 151), fill=hx("16161c"))
    # the far kerb, the road, and a lamp on the far side
    d.rectangle([0, 186, MOUTH, 189], fill=hx("6a6660"))
    d.rectangle([0, 190, MOUTH, BASE + 4], fill=hx("2a2a32"))
    lx = 78
    d.line([(lx, 112), (lx, 186)], fill=hx("1a1a20"), width=2)
    d.rectangle([lx - 3, 106, lx + 3, 113], fill=hx("1a1a20"))
    return (0, 150, MOUTH, 196)


def lunch_room_lit(img):
    """The lunch-room's lit interior and its signboard, painted over the lit picture: a door on the left, a
    coffee urn and a pie case on the back counter, the counterman in his white jacket, a lone customer hunched
    over a cup on one of the stools, and the window's mullions and gilt lettering over it all."""
    d = ImageDraw.Draw(img)
    wall, wall_d = hx("f0c070"), hx("c88a48")
    d.rectangle([4, 161, MOUTH - 4, 171], fill=wall)
    d.line([(4, 165), (MOUTH - 4, 165)], fill=wall_d)                    # the back shelf
    for x in range(20, 70, 6):                                           # cups and plates on it
        d.rectangle([x, 163, x + 2, 164], fill=hx("fff0d0"))
    # the coffee urn: a chrome cylinder with a domed lid and a tap
    d.rectangle([22, 166, 27, 171], fill=hx("b8b0a0"))
    d.line([(22, 166), (22, 171)], fill=hx("fff0d0"))
    d.line([(27, 166), (27, 171)], fill=hx("6a6050"))
    d.rectangle([23, 165, 26, 165], fill=hx("8a8070"))
    d.point((28, 169), fill=hx("4a4030"))
    # a glass pie case with a wedge gone
    d.rectangle([36, 167, 44, 171], fill=hx("ffe8b0"))
    d.rectangle([36, 167, 44, 171], outline=hx("a87a40"))
    d.chord([37, 168, 43, 172], 180, 360, fill=hx("c07a38"))
    d.point((40, 169), fill=hx("ffe8b0"))
    # the counterman behind the counter, white jacket and paper cap
    d.rectangle([58, 166, 63, 171], fill=hx("fff8e8"))
    d.rectangle([59, 162, 62, 165], fill=hx("c88a60"))
    d.rectangle([58, 161, 63, 161], fill=hx("ffffff"))
    d.line([(57, 168), (55, 170)], fill=hx("fff8e8"))
    # the counter top and the counter front
    d.rectangle([4, 172, MOUTH - 4, 173], fill=hx("d8c8a8"))
    d.rectangle([4, 174, MOUTH - 4, 182], fill=hx("6a4020"))
    for x in range(8, MOUTH - 4, 8):
        d.line([(x, 175), (x, 181)], fill=hx("4a2a14"))
    # stools: round seats on chrome posts, one taken
    for x in range(14, MOUTH - 8, 12):
        d.rectangle([x - 2, 175, x + 2, 176], fill=hx("a83a30"))
        d.line([(x - 2, 175), (x + 2, 175)], fill=hx("e06050"))
        d.line([(x, 177), (x, 181)], fill=hx("b8b0a0"))
        d.line([(x - 2, 182), (x + 2, 182)], fill=hx("8a8070"))
    cx = 50  # the customer, coat and hat, hunched on his stool
    d.polygon([(cx - 4, 175), (cx - 3, 168), (cx + 1, 166), (cx + 3, 168), (cx + 3, 175)], fill=hx("2a1c18"))
    d.rectangle([cx - 1, 163, cx + 2, 165], fill=hx("2a1c18"))
    d.line([(cx - 3, 163), (cx + 4, 163)], fill=hx("1a1210"))
    d.line([(cx + 3, 170), (cx + 6, 171)], fill=hx("2a1c18"))
    d.point((cx + 6, 171), fill=hx("ffffff"))
    # the door at the left end, its glass lit, and the window's mullions
    d.rectangle([4, 160, 13, 182], fill=hx("3a2418"))
    d.rectangle([6, 162, 11, 172], fill=hx("ffd890"))
    d.line([(6, 167), (11, 167)], fill=hx("3a2418"))
    d.point((11, 176), fill=hx("e0b060"))
    d.rectangle([4, 159, MOUTH - 4, 159], fill=hx("2a1a14"))
    for x in (34, 60):
        d.line([(x, 160), (x, 182)], fill=hx("2a1a14"))
    # gilt lettering on the glass
    text(img, (47, 178), "EATS", hx("ffe8b0"), 8)
    # the signboard
    text(img, (37, 142), "LUNCH ROOM", hx("f0e0b0"), 8)
    for x in range(4, 72, 4):
        d.point((x, 148), fill=hx("fff0c0") if (x // 4) % 3 else hx("6a4020"))
    light(img, "rect", [0, 134, 76, 150], hx("ffd890"), 0.18, 4)
    d.line([(78, 150), (78, 186)], fill=hx("1a1a20"), width=2)  # the far lamp's post stands in front of it all
    d.line([(77, 150), (77, 186)], fill=hx("4a3a30"))


def motel_wall(img):
    d = ImageDraw.Draw(img)
    bricks(img, (MOUTH, 14, W - 1, BASE), hx("5e3a32"), hx("443028"), hx("221a1a"), 21)
    rnd = random.Random(23)
    # soot and rain streaks down the bricks, under every sill and from the cornice
    streaks = Image.new("RGB", img.size, (255, 255, 255))
    sd = ImageDraw.Draw(streaks)
    for _ in range(60):
        x = rnd.randint(MOUTH, W)
        y0 = rnd.choice([14, 14, 92, 96, 108])
        sd.line([(x, y0), (x + rnd.randint(-1, 1), y0 + rnd.randint(20, 90))], fill=(150, 150, 160),
                width=rnd.randint(1, 4))
    for x0, y0, x1, y1 in WINDOWS:
        sd.rectangle([x0 + 2, y1 + 4, x1 - 2, y1 + 40], fill=(170, 170, 180))
    streaks = streaks.filter(ImageFilter.GaussianBlur(1.5))
    img.paste(ImageChops.multiply(img, streaks))
    # the parapet coping and a plain brick cornice
    d.rectangle([MOUTH, 8, W - 1, 14], fill=hx("6a645c"))
    d.line([(MOUTH, 8), (W - 1, 8)], fill=hx("948c80"))
    d.line([(MOUTH, 14), (W - 1, 14)], fill=hx("201818"))
    for x in range(MOUTH + 2, W, 8):
        d.rectangle([x, 15, x + 4, 18], fill=hx("4a2a24"))
    # the front corner: stone quoins where the side wall turns onto the main road
    for i, y in enumerate(range(18, BASE, 11)):
        w = 10 if i % 2 else 6
        d.rectangle([MOUTH, y, MOUTH + w, y + 9], fill=hx("7a7064"))
        d.line([(MOUTH, y), (MOUTH + w, y)], fill=hx("968a7c"))
        d.line([(MOUTH, y + 10), (MOUTH + w, y + 10)], fill=hx("2a2220"))
    # a stone string course at the first floor and a sooty plinth
    d.rectangle([MOUTH, 104, W - 1, 107], fill=hx("5a524a"))
    d.line([(MOUTH, 104), (W - 1, 104)], fill=hx("7a7064"))
    d.rectangle([MOUTH, BASE - 6, W - 1, BASE], fill=hx("322826"))
    d.line([(MOUTH, BASE - 6), (W - 1, BASE - 6)], fill=hx("4a3c38"))
    # a painted-out ghost advert high on the wall
    d.rectangle([236, 18, 452, 30], fill=mix(hx("5a3028"), hx("9a8a70"), 0.25))
    text(img, (344, 24), "ROOMS  BY THE NIGHT OR WEEK", mix(hx("5a3028"), hx("c8b898"), 0.45), 8)
    # the drainpipe with its brackets and a shoe that spills onto the cobbles
    px = 228
    d.line([(px, 14), (px, BASE + 2)], fill=hx("16161c"), width=3)
    d.line([(px - 1, 14), (px - 1, BASE + 2)], fill=hx("4a4650"))
    for by in range(26, BASE, 28):
        d.rectangle([px - 3, by, px + 3, by + 1], fill=hx("26242a"))
    d.polygon([(px - 2, BASE - 2), (px + 2, BASE - 2), (px + 7, BASE + 4), (px + 1, BASE + 4)], fill=hx("16161c"))


def sash(img, box, lit=False):
    """A first-floor sash window: brick soldier arch, a dark reveal, two sashes, a stone sill; lit ones glow through
    a drawn yellow blind and keep the shadow of the cross-bars."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 4, y0 - 7, x1 + 4, y0 - 2], fill=hx("6a6258"))
    d.line([(x0 - 4, y0 - 7), (x1 + 4, y0 - 7)], fill=hx("8a8072"))
    d.line([(x0 - 4, y0 - 2), (x1 + 4, y0 - 2)], fill=hx("2a2020"))
    d.rectangle([x0 - 2, y0 - 1, x1 + 2, y1], fill=hx("140e0e"))
    if lit:
        vgrad(img, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), hx("f0c070"), hx("c88438"))
    else:
        vgrad(img, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), hx("242a3c"), hx("0e1018"))
        d.line([(x0 + 4, y0 + 18), (x0 + 14, y0 + 6)], fill=hx("3a4258"))
        d.line([(x0 + 6, y0 + 22), (x0 + 16, y0 + 10)], fill=hx("2a3044"))
        d.rectangle([x0 + 2, y0 + 2, x1 - 2, y0 + 9], fill=hx("3a3428"))
    frame = hx("5e5850")
    d.rectangle([x0, y0, x1, y1], outline=frame, width=2)
    my = (y0 + y1) // 2
    d.rectangle([x0, my - 1, x1, my + 1], fill=frame)
    d.line([((x0 + x1) // 2, y0 + 2), ((x0 + x1) // 2, y1 - 2)], fill=frame)
    d.rectangle([x0 - 3, y1 + 1, x1 + 3, y1 + 3], fill=hx("7a7064"))
    d.line([(x0 - 3, y1 + 1), (x1 + 3, y1 + 1)], fill=hx("9a8e80"))
    d.line([(x0 - 3, y1 + 4), (x1 + 3, y1 + 4)], fill=hx("1e1616"))


def door(img):
    """The motel's entrance: a heavy plank door painted bottle green and peeling, a wired-glass transom lit from the
    lobby, a brass knob, a stencilled ROOMS, a worn stone step; the little neon sign over the frame."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    d.rectangle([x0 - 5, y0 - 18, x1 + 5, y1], fill=hx("3a3430"))
    d.line([(x0 - 5, y0 - 18), (x1 + 5, y0 - 18)], fill=hx("5a524a"))
    d.rectangle([x0 - 2, y0 - 15, x1 + 2, y1], fill=hx("16120e"))
    d.rectangle([x0, y0 - 13, x1, y0 - 3], fill=hx("6a5a3a"))  # transom glass (re-lit later)
    d.rectangle([x0, y0, x1, y1], fill=hx("2e4636"))
    rnd = random.Random(31)
    for x in range(x0 + 1, x1, 6):  # planks
        d.line([(x, y0), (x, y1)], fill=hx("1e3026"))
        d.line([(x + 1, y0), (x + 1, y1)], fill=hx("3a5a44"))
    for _ in range(26):  # peeling paint, bare wood showing through
        px, py = rnd.randint(x0 + 2, x1 - 4), rnd.randint(y0 + 2, y1 - 3)
        d.rectangle([px, py, px + rnd.randint(1, 3), py + rnd.randint(0, 2)], fill=hx("4a5a48"))
    for by in (y0 + 10, y1 - 14):  # ledges
        d.rectangle([x0, by, x1, by + 2], fill=hx("26392c"))
        d.line([(x0, by), (x1, by)], fill=hx("4a6a54"))
    text(img, ((x0 + x1) // 2 + 1, y0 + 28), "ROOMS", hx("a8a08a"), 8)
    d.ellipse([x1 - 7, y0 + 44, x1 - 3, y0 + 48], fill=hx("b8964a"))
    d.point((x1 - 6, y0 + 45), fill=hx("ffe0a0"))
    d.rectangle([x1 - 6, y0 + 50, x1 - 4, y0 + 53], fill=hx("7a6030"))
    for hy in (y0 + 8, y1 - 18):  # strap hinges
        d.rectangle([x0, hy, x0 + 12, hy + 2], fill=hx("16181c"))
    # the step, worn hollow in the middle
    d.rectangle([x0 - 8, y1, x1 + 8, y1 + 5], fill=hx("6e6a64"))
    d.line([(x0 - 8, y1), (x1 + 8, y1)], fill=hx("9a968e"))
    d.line([(x0 + 8, y1 + 1), (x1 - 8, y1 + 1)], fill=hx("4e4a46"))
    d.line([(x0 - 8, y1 + 5), (x1 + 8, y1 + 5)], fill=hx("26242a"))
    # the sign's sheet-iron box and brackets (its tubes are drawn after lighting)
    sx0, sy0, sx1, sy1 = DOOR_SIGN
    d.rectangle([sx0, sy0, sx1, sy1], fill=hx("1a1416"), outline=hx("3a3034"))
    for bx in (sx0 + 6, sx1 - 6):
        d.line([(bx, sy0 - 4), (bx, sy0)], fill=IRON)
    d.line([(sx1 - 2, sy1), (sx1 + 6, sy1 + 10), (sx1 + 6, BASE - 8)], fill=hx("101014"))  # its cable


def ground_window(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 380, 124, 410, 150
    d.rectangle([x0 - 2, y0 - 4, x1 + 2, y1 + 3], fill=hx("4a4038"))
    d.rectangle([x0, y0, x1, y1], fill=hx("0e0e14"))
    for x in range(x0 + 3, x1, 5):
        d.line([(x, y0), (x, y1)], fill=hx("3a3a42"))
    d.line([(x0, y0 + 10), (x1, y0 + 10)], fill=hx("3a3a42"))
    # a caged lamp over it on a short arm
    lx, ly = LAMP
    d.line([(lx, ly - 6), (lx + 8, ly - 6)], fill=IRON, width=2)
    d.line([(lx + 8, ly - 10), (lx + 8, ly - 2)], fill=IRON, width=2)
    d.polygon([(lx - 6, ly - 1), (lx - 2, ly - 5), (lx + 2, ly - 5), (lx + 6, ly - 1)], fill=hx("2e4036"))
    # an electric meter by the door, and a hand-painted arrow to the front desk
    d.rectangle([128, 132, 142, 150], fill=hx("2a2a30"), outline=hx("4a4a52"))
    d.ellipse([131, 136, 139, 144], fill=hx("6a6a62"))
    d.line([(135, 150), (135, BASE - 6)], fill=hx("16161a"))


def fire_escape(d, lowered=False):
    """The landing along the first floor: balusters between top and middle rails, a kick plate, the grating's front
    edge, knee brackets; the drop ladder hangs from goosenecks over the left of it, its lower flight slid up behind
    the upper one, or let all the way down to the cobbles."""
    x0, x1 = LANDING_X
    y = LANDING_Y
    top, mid = y - 28, y - 14
    for x in range(x0 + 3, x1 + 1, 5):
        d.line([(x, top), (x, y)], fill=IRON)
        d.point((x - 1, top + 3), fill=IRON_M)
    for ry in (top, mid):
        d.line([(x0, ry), (x1, ry)], fill=IRON, width=2)
        d.line([(x0, ry - 1), (x1, ry - 1)], fill=IRON_E)
    d.rectangle([x0, y - 4, x1, y - 1], fill=IRON)
    d.line([(x0, y - 4), (x1, y - 4)], fill=IRON_M)
    for px in (x0, x1, 340, 384):
        d.rectangle([px - 1, top - 2, px + 1, y + 4], fill=IRON)
        d.line([(px - 1, top - 2), (px - 1, y + 4)], fill=IRON_E)
        d.point((px, top - 3), fill=IRON_H)
    d.rectangle([x0, y, x1, y + 5], fill=IRON)
    d.line([(x0, y), (x1, y)], fill=IRON_H)
    d.line([(x0, y + 1), (x1, y + 1)], fill=IRON_E)
    for x in range(x0 + 1, x1, 3):
        d.line([(x, y + 3), (x + 1, y + 5)], fill=IRON_M)
    d.line([(x0, y + 6), (x1, y + 6)], fill=hx("0a0c10"))
    for bx in (x0 + 4, 340, 384, x1 - 4):
        s = -1 if bx < 340 else 1
        d.line([(bx, y + 6), (bx, y + 28)], fill=IRON, width=2)
        d.line([(bx + 9 * s, y + 6), (bx, y + 26)], fill=hx("262c36"), width=2)
        d.rectangle([bx - 2, y + 24, bx + 2, y + 29], fill=IRON_M)
        d.point((bx, y + 27), fill=IRON_H)
    # the stair up to the roof at the far end: two stringers, treads, and a handrail
    for k in range(2):
        d.line([(400 + 8 * k, y - 1), (480 + 8 * k, y - 81)], fill=IRON, width=2)
    d.line([(400, y - 1), (480, y - 81)], fill=IRON_E)
    for k in range(1, 9):
        sx, sy = 400 + k * 9, y - k * 9
        d.line([(sx, sy), (sx + 8, sy)], fill=IRON_M, width=2)
        d.point((sx + 1, sy - 1), fill=IRON_H)
    d.line([(396, y - 30), (476, y - 110)], fill=IRON, width=2)
    for k in range(1, 9, 2):
        d.line([(400 + k * 9, y - k * 9), (396 + k * 9, y - 30 - k * 9)], fill=IRON)
    # the drop ladder
    lx0, lx1 = LADDER_X
    bottom = LOWERED_BOTTOM if lowered else RAISED_BOTTOM
    for x in (lx0, lx1):
        d.line([(x, y - 14), (x, bottom)], fill=IRON, width=3)
        d.line([(x - 1, y - 14), (x - 1, bottom)], fill=IRON_E)
        d.arc([x - 1, y - 18, x + 5, y - 10], 180, 360, fill=IRON, width=2)
        d.point((x, y - 17), fill=IRON_H)
        d.rectangle([x - 2, y + 18, x + 2, y + 22], fill=hx("40464e"))  # guide clamps
        d.line([(x - 2, y + 18), (x + 2, y + 18)], fill=IRON_H)
        d.rectangle([x - 2, bottom - 2, x + 2, bottom], fill=IRON)
    for ry in range(y + 10, bottom - 1, 8):
        d.line([(lx0 + 1, ry), (lx1 - 1, ry)], fill=hx("161a22"), width=3)
        d.line([(lx0 + 1, ry - 1), (lx1 - 1, ry - 1)], fill=IRON_H)
    if not lowered:
        for x in (lx0 + 3, lx1 - 3):
            d.line([(x, y + 9), (x, bottom - 4)], fill=hx("3a404c"))
        for ry in range(y + 14, bottom - 4, 8):
            d.line([(lx0 + 4, ry), (lx1 - 4, ry)], fill=hx("262c36"))
        # the counterweight chain looped up to the landing
        d.line([(lx1 + 2, bottom - 2), (lx1 + 6, y + 6)], fill=hx("2a2e36"))
    else:
        d.line([(lx0 - 3, bottom + 1), (lx1 + 3, bottom + 1)], fill=hx("08080c"))


def ground(img):
    d = ImageDraw.Draw(img)
    d.rectangle([MOUTH, BASE, W - 1, BASE + 4], fill=hx("4a4642"))
    d.line([(MOUTH, BASE), (W - 1, BASE)], fill=hx("6a6660"))
    d.rectangle([0, BASE + 5, W - 1, H - 1], fill=hx("26262c"))
    rnd = random.Random(77)
    y = BASE + 5
    while y < H:
        h = 3 + min(5, (y - BASE) // 15)
        x = -rnd.randint(0, 10)
        while x < W:
            w = rnd.randint(6, 10) + (y - BASE) // 13
            c = mix(hx("4e4c56"), hx("6a6874"), rnd.random())
            d.rounded_rectangle([x + 1, y, x + w - 1, y + h - 1], radius=1, fill=c)
            d.line([(x + 2, y), (x + w - 3, y)], fill=mul(c, 1.2))
            d.line([(x + 2, y + h - 1), (x + w - 3, y + h - 1)], fill=mul(c, 0.72))
            x += w
        y += h + 1
    noise(img, (0, BASE + 5, W - 1, H - 1), 5, 78)
    # a gutter of running water along the middle of the alley
    for x in range(0, W, 2):
        yy = 236 + int(2 * math.sin(x / 23))
        d.point((x, yy), fill=hx("2a3040"))
        d.point((x + 1, yy + 1), fill=hx("1c2030"))
    for x0, y0, x1, y1 in PUDDLES:
        d.ellipse([x0, y0, x1, y1], fill=hx("1c2232"))
    # litter: a sodden newspaper, a broken bottle, cigarette ends by the door
    d.polygon([(130, 222), (146, 219), (150, 226), (134, 229)], fill=hx("8a8470"))
    d.line([(134, 224), (146, 222)], fill=hx("4a4638"))
    d.polygon([(440, 244), (443, 241), (445, 245)], fill=hx("2a5a32"))
    for x, y in ((172, 204), (190, 208), (214, 202)):
        d.line([(x, y), (x + 2, y)], fill=hx("c8c0b0"))


def trash_cans(img):
    d = ImageDraw.Draw(img)
    for i, (x0, top) in enumerate(CANS):
        x1, g = x0 + 22, 200 + i
        shadow(img, "ellipse", [x0 - 4, g - 3, x1 + 8, g + 3], 0.6, 2)
        for x in range(x0, x1 + 1):
            u = (x - x0) / (x1 - x0)
            f = 0.5 + 0.5 * math.cos((u - 0.3) * math.pi * 1.1)
            d.line([(x, top), (x, g)], fill=mix(hx("2a2c30"), hx("8a8e94"), max(0.0, min(1.0, f))))
        for ry in (top + 8, g - 8):
            d.line([(x0 + 1, ry), (x1 - 1, ry)], fill=hx("a8acb2"))
            d.line([(x0 + 1, ry + 1), (x1 - 1, ry + 1)], fill=hx("2e3034"))
        d.rectangle([x0 - 1, top - 2, x1 + 1, top], fill=hx("9a9ea4"))
        d.rectangle([x0 - 2, top + 10, x0, top + 14], fill=hx("6a6e74"))
        d.rectangle([x1, top + 10, x1 + 2, top + 14], fill=hx("6a6e74"))
    # the first wears its lid, a dent in it holding rain; the second's lid lies against it, the rubbish spills
    x0, top = CANS[0]
    d.ellipse([x0 - 2, top - 6, x0 + 24, top + 1], fill=hx("7a7e84"), outline=hx("2a2c30"))
    d.ellipse([x0 + 6, top - 4, x0 + 16, top - 1], fill=hx("3a4258"))
    d.rectangle([x0 + 9, top - 8, x0 + 13, top - 6], fill=hx("5a5e64"))
    x0, top = CANS[1]
    d.ellipse([x0, top - 3, x0 + 22, top + 2], fill=hx("16161a"))
    d.polygon([(x0 + 3, top), (x0 + 8, top - 8), (x0 + 15, top - 5), (x0 + 20, top)], fill=hx("8a8270"))
    d.ellipse([x0 + 24, 186, x0 + 34, 204], fill=hx("6a6e74"), outline=hx("a4a8ae"))
    for x, y, c in ((x0 - 6, 206, hx("8a8270")), (x0 + 6, 208, hx("5a4030"))):
        d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=c)


def crate_at(img, pos):
    x0, y0 = pos
    s = CRATE_SIZE
    shadow(img, "rect", [x0 - 2, y0 + s - 2, x0 + s + 4, y0 + s + 3], 0.6, 2)
    fruit_crate(ImageDraw.Draw(img), x0, y0, s, seed=5)


def lighting(img, far_box, lowered):
    sx0, sy0, sx1, sy1 = DOOR_SIGN
    scx = (sx0 + sx1) // 2
    bx0, by0, bx1, by1 = BLADE
    wx0, wy0, wx1, wy1 = LIT_WINDOW
    fx0, fy0, fx1, fy1 = far_box
    lights = [
        ("rect", [MOUTH, -20, W + 20, 60], (26, 26, 50), 1.0, 30),               # the city's glow on the upper wall
        ("ellipse", [bx0 - 60, by0 - 40, bx1 + 60, by1 + 60], (170, 34, 54), 1.0, 26),  # the big sign's red
        ("ellipse", [-60, 150, 200, 290], (150, 30, 50), 0.9, 24),             # ... on the wet stones
        ("ellipse", [fx0 - 10, fy0 - 10, fx1 + 20, fy1 + 30], (200, 140, 80), 0.6, 12),  # the lunch-room
        ("ellipse", [scx - 44, sy0 - 30, scx + 44, sy1 + 60], (180, 40, 60), 1.0, 16),  # the door sign
        ("ellipse", [scx - 70, BASE - 8, scx + 70, BASE + 50], (160, 40, 60), 0.8, 14),
        ("rect", [DOOR[0], DOOR[1] - 14, DOOR[2], DOOR[1] + 10], (150, 110, 60), 0.4, 6),  # under the transom
        ("ellipse", [wx0 - 34, wy0 - 10, wx1 + 34, wy1 + 50], (190, 130, 60), 0.9, 16),  # the lit window
        ("ellipse", [wx0 - 60, BASE - 4, wx1 + 60, BASE + 40], (70, 50, 40), 0.6, 18),
        ("ellipse", [LAMP[0] - 70, LAMP[1] - 10, LAMP[0] + 80, LAMP[1] + 90], (150, 112, 70), 0.9, 18),  # the lamp
        ("ellipse", [LAMP[0] - 90, BASE - 10, LAMP[0] + 90, BASE + 44], (140, 104, 64), 0.8, 16),
        ("ellipse", [LADDER_CX - 50, LANDING_Y, LADDER_CX + 50, BASE + 20], (110, 70, 70), 0.8, 16),  # spill
    ]
    img = illuminate(img, (40, 42, 72), lights)
    shadow(img, "rect", [LANDING_X[0] - 6, LANDING_Y + 6, LANDING_X[1] + 6, LANDING_Y + 40], 0.3, 10)
    shadow(img, "rect", [450, 120, W + 20, H + 20], 0.2, 24)
    d = ImageDraw.Draw(img)
    # the light sources themselves, drawn over the lit picture
    sash(img, LIT_WINDOW, lit=True)
    d.rectangle([wx0 + 2, wy0 + 2, wx1 - 2, wy0 + 20], fill=hx("e09a48"))  # the blind
    d.line([(wx0 + 2, wy0 + 20), (wx1 - 2, wy0 + 20)], fill=hx("8a5a28"))
    d.ellipse([(wx0 + wx1) // 2 - 1, wy0 + 21, (wx0 + wx1) // 2 + 1, wy0 + 23], outline=hx("8a5a28"))
    d.rectangle([DOOR[0], DOOR[1] - 13, DOOR[2], DOOR[1] - 3], fill=hx("d89a50"))
    for x in range(DOOR[0] + 3, DOOR[2], 5):  # the wire mesh in the transom
        d.line([(x, DOOR[1] - 13), (x + 4, DOOR[1] - 3)], fill=hx("8a5a30"))
    lunch_room_lit(img)
    d.rectangle([57, 106, 63, 112], fill=hx("fff0c0"))
    light(img, "ellipse", [44, 94, 76, 124], hx("ffd890"), 0.5, 6)
    blade_sign(img)
    door_sign(img)
    lx, ly = LAMP
    d.ellipse([lx - 2, ly - 2, lx + 2, ly + 3], fill=hx("fff0c0"))
    for x in (lx - 2, lx, lx + 2):  # the wire cage
        d.line([(x, ly - 1), (x, ly + 3)], fill=hx("6a5a40"))
    light(img, "ellipse", [lx - 8, ly - 6, lx + 8, ly + 10], hx("ffd890"), 0.45, 4)
    light(img, "polygon", [(lx - 6, ly), (lx + 6, ly), (lx + 40, BASE + 20), (lx - 40, BASE + 20)], hx("e8b060"),
          0.12, 10)
    light(img, "ellipse", [wx0 - 10, wy0 - 6, wx1 + 10, wy1 + 8], hx("ffc070"), 0.25, 8)
    # the railing stands black against the lit window: redraw the fire escape over the glow there
    iron = img.copy()
    fire_escape(ImageDraw.Draw(iron), lowered)
    box = (wx0 - 3, wy0 - 3, wx1 + 4, wy1 + 5)
    img.paste(iron.crop(box), box[:2])
    return img


def blade_sign(img):
    """The motel's big sign, bolted to the front corner and hanging out over the main road: a riveted sheet-iron
    box with a cornice and a finial, red neon MOTEL letters on their dark cans, a chaser of amber bulbs round the
    edge (some dead), the conduit feeding it and a little VACANCY board hung underneath on chains."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = BLADE
    for by in (y0 + 10, y1 - 10):  # the brackets back to the corner, with a tie rod and its turnbuckle
        d.line([(x1, by), (MOUTH + 2, by)], fill=IRON, width=2)
        d.line([(x1 + 4, by), (MOUTH + 2, by - 10)], fill=IRON)
        d.line([(x1 + 1, by - 1), (MOUTH + 2, by - 1)], fill=IRON_M)
        d.rectangle([x1 + 14, by - 6, x1 + 16, by - 4], fill=IRON_E)
    d.line([(x1 - 6, y0 - 3), (x1 - 6, y0 - 8), (MOUTH + 2, y0 - 8)], fill=hx("26242a"))  # the conduit
    # the box: a shadowed side face for depth, the front panel, a cornice and a finial on top
    d.rectangle([x0 - 3, y0 + 1, x0, y1 - 1], fill=hx("120a0c"))
    d.rectangle([x0, y0, x1, y1], fill=hx("1c1012"), outline=hx("3a2024"))
    d.rectangle([x0 - 4, y0 - 3, x1 + 1, y0 - 1], fill=hx("2a1a1c"))
    d.line([(x0 - 4, y0 - 3), (x1 + 1, y0 - 3)], fill=hx("5a3a3c"))
    d.rectangle([x0 - 2, y1 + 1, x1 - 1, y1 + 2], fill=hx("2a1a1c"))
    cx = (x0 + x1) // 2 + 1
    d.line([(cx, y0 - 4), (cx, y0 - 7)], fill=IRON_M)
    d.ellipse([cx - 2, y0 - 11, cx + 2, y0 - 7], fill=hx("3a2a2c"), outline=hx("5a3a3c"))
    for y in range(y0 + 4, y1 - 2, 6):  # rivet rows down both edges, rust bleeding from them
        for x in (x0 + 1, x1 - 1):
            d.point((x, y), fill=hx("5a3a3c"))
            d.point((x, y + 2), fill=hx("3a1a14"))
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=hx("6a4020"))
    # the letters' sheet-metal cans, a shade darker than the panel, behind the tubes
    for i, ch in enumerate("MOTEL"):
        cy = y0 + 14 + i * 18
        d.rectangle([cx - 8, cy - 8, cx + 6, cy + 7], fill=hx("140a0c"), outline=hx("2e1a1e"))
        text(img, (cx + 1, cy + 1), ch, hx("3a0e14"), 16)
        text(img, (cx, cy), ch, NEON, 16)
        if i < 4:  # the blacked-out jumper tube down to the next letter
            d.line([(cx - 1, cy + 8), (cx - 1, cy + 10)], fill=hx("4a1a20"))
    light(img, "rect", [x0 - 4, y0 - 4, x1 + 4, y1 + 4], hx("ff2a40"), 0.35, 8)
    for i, ch in enumerate("MOTEL"):
        text(img, (cx, y0 + 14 + i * 18), ch, NEON_HOT, 8)
    # the chaser: bulbs every 4px round the border, every third one dead
    k = 0
    border = ([(x, y0 + 2) for x in range(x0 + 2, x1 - 1, 4)] + [(x1 - 2, y) for y in range(y0 + 2, y1 - 1, 4)] +
              [(x, y1 - 2) for x in range(x1 - 2, x0 + 1, -4)] + [(x0 + 2, y) for y in range(y1 - 2, y0 + 1, -4)])
    for p in border:
        d.point(p, fill=hx("6a4020") if k % 3 == 2 else AMBER_HOT)
        k += 1
    # the VACANCY board, hung on two chains under the box
    vx0, vy0, vx1, vy1 = x0 + 1, y1 + 4, x1 - 1, y1 + 11
    for x in (vx0 + 3, vx1 - 3):
        for y in range(y1 + 3, vy0, 2):
            d.point((x, y), fill=IRON_E)
    d.rectangle([vx0, vy0, vx1, vy1], fill=hx("101a14"), outline=hx("2a3a30"))
    text(img, ((vx0 + vx1) // 2 + 1, (vy0 + vy1) // 2 + 1), "VACANCY", hx("70ff98"), 8)
    light(img, "rect", [vx0 - 3, vy0 - 3, vx1 + 3, vy1 + 3], hx("40c070"), 0.25, 4)
    light(img, "ellipse", [x0 - 30, y0 - 20, x1 + 30, y1 + 20], hx("c01830"), 0.22, 18)


def door_sign(img):
    """The little sign over the entrance, red tubes in a black box; the T has gone dim and buzzes."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR_SIGN
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], fill=hx("200c10"))
    cx, cy = (x0 + x1) // 2 + 1, (y0 + y1) // 2 + 1
    light(img, "rect", [x0 - 2, y0 - 2, x1 + 2, y1 + 2], hx("ff2a40"), 0.35, 4)
    text(img, (cx, cy), "MOTEL", NEON, 8)
    # dim the T: a dead tube shows the glass's dull red
    tx = cx - 1
    px = img.load()
    for yy in range(y0 + 2, y1 - 1):
        for xx in range(tx - 3, tx + 3):
            if px[xx, yy] == NEON:
                px[xx, yy] = NEON_DIM
    light(img, "ellipse", [x0 - 20, y0 - 14, x1 + 20, y1 + 16], hx("e02040"), 0.25, 10)


def reflections(img):
    """Puddles mirror what stands above them (flipped about the wall foot), rippled and darkened; the neon smears
    long streaks down the wet stones."""
    depth = H - BASE
    src = img.crop((0, BASE - depth, W, BASE)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    src = src.filter(ImageFilter.GaussianBlur(1.0))
    rip = Image.new("RGB", src.size)
    rnd = random.Random(9)
    for y in range(src.height):
        dx = int(round(math.sin(y * 0.9 + rnd.random()) * (1 + y / 30)))
        rip.paste(src.crop((0, y, W, y + 1)), (dx, y))
    rip = ImageChops.multiply(rip, Image.new("RGB", rip.size, (190, 180, 210)))
    mask = Image.new("L", (W, depth), 0)
    md = ImageDraw.Draw(mask)
    for y in range(depth):
        md.line([(0, y), (W, y)], fill=int(255 * 0.2 * (1 - y / depth)))
    for x0, y0, x1, y1 in PUDDLES:
        md.ellipse([x0, y0 - BASE, x1, y1 - BASE], fill=210)
    mask = mask.filter(ImageFilter.GaussianBlur(0.8))
    region = img.crop((0, BASE, W, H))
    img.paste(Image.composite(ImageChops.lighter(region, rip), region, mask), (0, BASE))
    d = ImageDraw.Draw(img)
    for x0, y0, x1, y1 in PUDDLES:
        rim = img.getpixel(((x0 + x1) // 2, y0))
        d.arc([x0, y0, x1, y1], 200, 340, fill=mul(rim, 1.4))
        d.point(((x0 + x1) // 2 + 6, (y0 + y1) // 2), fill=hx("8a90b0"))  # a raindrop's ring
    # neon streaks on the stones under the signs
    scx = (DOOR_SIGN[0] + DOOR_SIGN[2]) // 2
    light(img, "rect", [scx - 10, BASE + 8, scx + 10, 262], hx("ff3048"), 0.18, 3)
    light(img, "rect", [BLADE[0] + 4, BASE + 8, BLADE[2] - 4, 268], hx("ff3048"), 0.2, 4)
    light(img, "rect", [LIT_WINDOW[0] + 4, 214, LIT_WINDOW[2] - 4, 262], hx("ffb050"), 0.08, 4)


def glints(img):
    rnd = random.Random(19)
    px = img.load()
    for _ in range(600):
        x, y = rnd.randint(0, W - 1), rnd.randint(BASE + 6, H - 1)
        r = rnd.random()
        if x < 220 and r < 0.35:
            px[x, y] = mix(px[x, y], (255, 120, 140), 0.35)
        elif r < 0.12:
            px[x, y] = mix(px[x, y], (150, 160, 210), 0.35)


def paint_alley(crate=None, lowered=False):
    """crate: None (not in the picture: the base), "home" (by the cans) or "under" (under the drop ladder)."""
    img = Image.new("RGB", (W, H))
    sky(img)
    far_box = main_road(img)
    motel_wall(img)
    for box in WINDOWS:
        sash(img, box, lit=box == LIT_WINDOW)
    door(img)
    ground_window(img)
    fire_escape(ImageDraw.Draw(img), lowered)
    ground(img)
    trash_cans(img)
    if crate == "home":
        crate_at(img, CRATE_HOME)
    elif crate == "under":
        crate_at(img, CRATE_UNDER)
    img = lighting(img, far_box, lowered)
    reflections(img)
    glints(img)
    vignette(img, 0.45, (14, 10, 26), 44)
    return img


def alley_palette(base, *variants):
    blend = base
    for v in variants:
        blend = Image.blend(blend, v, 0.35)
    return palette_of(blend, 116) + [NEON, NEON_HOT, NEON_DIM, AMBER, AMBER_HOT, hx("f0c070"), hx("d89a50"),
                                     hx("e09a48"), hx("fff0c0"), hx("c01830"), hx("5a1420"), hx("2a1418"),
                                     hx("70ff98"), hx("101a14")]


def overlay(variant, before, pal, box, name):
    """Crops the pixelized variant where it differs from `before`, saves it and returns the crop origin."""
    v = pixelize(variant, pal)
    diff = ImageChops.difference(v.crop(box), before.crop(box)).convert("L").point(lambda p: 255 if p else 0)
    bb = diff.getbbox()
    if not bb:
        raise ValueError(name)
    tight = (box[0] + bb[0], box[1] + bb[1], box[0] + bb[2], box[1] + bb[3])
    save(v.crop(tight), "rooms", f"{name}.png")
    print(name, "at", tight[:2])
    return tight[:2]


ALLEY_OVERLAYS = (  # name, variant, the variant it is drawn over, the box it must stay inside
    ("motel_alley_crate", dict(crate="home"), {}, (340, 140, 430, H)),
    ("motel_alley_crate_under", dict(crate="under"), {}, (250, 140, 330, H)),
    ("motel_alley_ladder", dict(crate="under", lowered=True), dict(crate="under"), (250, 60, 330, H)),
)


def alley_pal():
    base = paint_alley()
    return base, alley_palette(base, *(paint_alley(**v) for _, v, _, _ in ALLEY_OVERLAYS))


def build_alley():
    base, pal = alley_pal()
    save(pixelize(base, pal), "rooms", "motel_alley.png")
    for name, flags, before, box in ALLEY_OVERLAYS:
        overlay(paint_alley(**flags), pixelize(paint_alley(**before), pal), pal, box, name)


# ------------------------------------------------------------------------------------------------ the landing

FOOT = 176                       # where the landing's grating meets the wall
EDGE = 214                       # the landing's front edge: a shallow strip of grating, the alley open below it
FE_RAIL_H = 40                   # the safety rail's height at the front edge, about a man's hip
FE_TOP, FE_MID = EDGE - FE_RAIL_H, EDGE - FE_RAIL_H // 2
FE_RAIL_END = 466                # the right-hand end of the landing, where the rail turns back to the wall
FE_RAIL_RUNS = ((0, 18, (16,)), (64, FE_RAIL_END, (64, 160, 262, 364, FE_RAIL_END)))  # (x0, x1, posts) either side of the hatch
FE_FG_Y = FE_TOP - 4             # the top of the foreground layer holding the front rail
FE_VP = (240, -420)              # the grating's long bars converge very gently on this point
HATCH = (22, 56)                 # the opening the drop ladder comes up through, at the front left
HATCH_TOP = 192                  # the hatch's back edge on the grating
FE_DOOR = (212, 70, 256, FOOT)
FE_WINDOWS = ((108, 62, 158, 150), (314, 62, 364, 150))
FE_LIT = FE_WINDOWS[1]           # Eleanor's room


def fe_x(xb, y):
    """x at depth y of a line through (xb, EDGE) running back to the vanishing point."""
    vx, vy = FE_VP
    return vx + (xb - vx) * (y - vy) / (EDGE - vy)


def below(img):
    """The alley one floor down, seen through the grating: wet cobbles, neon smeared in the puddles."""
    d = ImageDraw.Draw(img)
    vgrad(img, (0, FOOT, W - 1, H - 1), hx("101016"), hx("1a1a22"))
    rnd = random.Random(52)
    for _ in range(260):
        x, y = rnd.randint(0, W - 1), rnd.randint(FOOT, H - 1)
        d.rectangle([x, y, x + rnd.randint(3, 6), y + 1], fill=mix(hx("22222a"), hx("34343e"), rnd.random()))
    for cx, cy, rx, ry, col in ((90, 210, 60, 9, hx("6a1a2a")), (300, 236, 70, 8, hx("5a3a20")),
                                (420, 196, 40, 6, hx("4a1622")), (180, 262, 50, 6, hx("3a2a30"))):
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col)
        d.ellipse([cx - rx // 2, cy - ry // 2, cx + rx // 3, cy + ry // 3], fill=mul(col, 1.5))
    # the lid of a trash can and the crate's top, far down
    d.ellipse([370, 238, 398, 246], fill=hx("3a3c42"))
    d.rectangle([150, 196, 176, 206], fill=hx("4a3a24"))


def landing(img):
    """The grating, seen from just above: front-to-back bearing bars converging on the wall, cross bars every few
    pixels, the angle-iron front edge, the hatch for the ladder and a low rail in the foreground."""
    d = ImageDraw.Draw(img)
    h0, h1 = HATCH
    # the cross bars, closer together towards the wall
    y, step = float(FOOT + 2), 3.0
    while y < EDGE:
        yy = int(y)
        d.line([(fe_x(0, yy) - 40, yy), (fe_x(W, yy) + 40, yy)], fill=IRON, width=1)
        d.line([(fe_x(0, yy) - 40, yy + 1), (fe_x(W, yy) + 40, yy + 1)], fill=hx("2a3038"))
        y += step
        step = min(7.0, step * 1.08)
    # the bearing bars
    for xb in range(-40, W + 40, 9):
        d.line([(fe_x(xb, FOOT), FOOT), (xb, EDGE)], fill=IRON, width=2)
        d.line([(fe_x(xb, FOOT) - 1, FOOT), (xb - 1, EDGE)], fill=IRON_M)
    # the hatch the drop ladder comes up through: a frame round a hole straight down to the alley
    top = HATCH_TOP
    hole = [(fe_x(h0, top), top), (fe_x(h1, top), top), (h1, EDGE), (h0, EDGE)]
    img2 = Image.new("RGB", img.size)
    below(img2)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(hole, fill=255)
    img.paste(img2, (0, 0), m)
    d.line(hole + [hole[0]], fill=IRON, width=2)
    d.line([hole[0], hole[1]], fill=IRON_H)
    # where the grating meets the wall: a channel bolted to the bricks
    d.rectangle([0, FOOT - 2, W - 1, FOOT + 2], fill=IRON)
    d.line([(0, FOOT - 2), (W - 1, FOOT - 2)], fill=IRON_E)
    for x in range(10, W, 40):
        d.point((x, FOOT), fill=IRON_H)
    # the front edge
    d.rectangle([0, EDGE, W - 1, EDGE + 5], fill=IRON)
    d.line([(0, EDGE), (W - 1, EDGE)], fill=IRON_H)
    d.line([(0, EDGE + 1), (W - 1, EDGE + 1)], fill=IRON_E)
    for x in range(4, W, 3):
        d.line([(x, EDGE + 3), (x + 1, EDGE + 5)], fill=IRON_M)


def fe_ladder(d):
    """The top of the drop ladder rising out of the hatch: rails curving over into goosenecks, round rungs. Drawn
    over the lit picture, rimmed red by the big sign round the corner."""
    h0, h1 = HATCH
    l0, l1 = h0 + 6, h1 - 6
    t = HATCH_TOP - 24           # the top of the goosenecks
    body, rim, hot = hx("161a22"), hx("b04858"), hx("ff8a98")
    for x in (l0, l1):
        d.line([(x, t + 12), (x, H)], fill=body, width=4)
        d.line([(x - 2, t + 14), (x - 2, H)], fill=rim)
        d.arc([x - 2, t, x + 12, t + 26], 180, 360, fill=body, width=4)
        d.arc([x - 2, t, x + 12, t + 26], 190, 250, fill=rim)
        d.line([(x + 11, t + 12), (x + 11, t + 30)], fill=body, width=3)
        d.point((x + 2, t + 1), fill=hot)
        d.rectangle([x - 3, t + 40, x + 3, t + 44], fill=hx("3a3e48"))
        d.line([(x - 3, t + 40), (x + 3, t + 40)], fill=rim)
    for ry in range(t + 32, H, 9):
        d.line([(l0 + 2, ry), (l1 - 2, ry)], fill=body, width=3)
        d.line([(l0 + 2, ry - 1), (l1 - 2, ry - 1)], fill=rim)


def fe_rails(d):
    """The safety railing up the right-hand end, back to the wall, and the one along the front edge."""
    # the right-hand end: a post at the front and one against the wall, rails between them in perspective
    fx, wx = FE_RAIL_END, int(fe_x(FE_RAIL_END, FOOT))
    k = (FOOT - FE_VP[1]) / (EDGE - FE_VP[1])  # how much smaller the rail stands back at the wall
    wall_top, wall_mid = round(FOOT - FE_RAIL_H * k), round(FOOT - FE_RAIL_H * k / 2)
    for (x, yb, yt) in ((wx, FOOT, wall_top),):
        d.line([(x, yb), (x, yt)], fill=IRON, width=3)
        d.line([(x - 1, yb), (x - 1, yt)], fill=IRON_E)
    for fy, wy in ((FE_TOP, wall_top), (FE_MID, wall_mid)):
        d.line([(fx, fy), (wx, wy)], fill=IRON, width=2)
        d.line([(fx, fy - 1), (wx, wy - 1)], fill=IRON_E)
    for i in range(1, 4):
        t = i / 4
        x = round(fx + (wx - fx) * t)
        d.line([(x, EDGE + (FOOT - EDGE) * t), (x, FE_TOP + (wall_top - FE_TOP) * t)], fill=IRON)
    fe_front_rail(d)


def fe_front_rail(d, mask=False):
    """The safety rail standing on the front edge, between the characters and the drop: square posts bolted to the
    edge channel, a top rail and a mid rail of flat bar, close-set pickets and a toe plate. It breaks at the hatch,
    where the drop ladder's goosenecks are the handhold. With mask=True every part is drawn in white, giving the
    foreground layer's cut-out."""
    body, edge, hi, toe = (255,) * 4 if mask else (IRON, IRON_E, IRON_H, hx("1c2028"))
    for x0, x1, posts in FE_RAIL_RUNS:
        d.rectangle([x0, EDGE - 5, x1, EDGE], fill=toe)
        d.line([(x0, EDGE - 5), (x1, EDGE - 5)], fill=edge)
        for x in range(x0 + 3, x1 - 1, 5):
            d.line([(x, FE_TOP + 2), (x, EDGE - 6)], fill=body)
        d.rectangle([x0, FE_MID - 1, x1, FE_MID], fill=body)
        d.line([(x0, FE_MID - 1), (x1, FE_MID - 1)], fill=edge)
        d.rectangle([x0, FE_TOP - 1, x1, FE_TOP + 1], fill=body)
        d.line([(x0, FE_TOP - 1), (x1, FE_TOP - 1)], fill=hi)
        for px in posts:
            d.rectangle([px - 1, FE_TOP - 3, px + 2, EDGE + 4], fill=body)
            d.line([(px - 1, FE_TOP - 3), (px - 1, EDGE + 4)], fill=edge)
            d.rectangle([px - 2, FE_TOP - 4, px + 3, FE_TOP - 3], fill=body)


def fe_wall(img):
    d = ImageDraw.Draw(img)
    bricks(img, (0, 0, W - 1, FOOT), hx("5a3a32"), hx("402c26"), hx("201818"), 63, 6, 13)
    rnd = random.Random(64)
    streaks = Image.new("RGB", img.size, (255, 255, 255))
    sd = ImageDraw.Draw(streaks)
    for _ in range(50):
        x = rnd.randint(0, W)
        y0 = rnd.choice([0, 0, 20, 154])
        sd.line([(x, y0), (x + rnd.randint(-1, 1), y0 + rnd.randint(20, 120))], fill=(150, 146, 150),
                width=rnd.randint(1, 5))
    for x0, y0, x1, y1 in FE_WINDOWS:
        sd.rectangle([x0 + 4, y1 + 6, x1 - 4, FOOT], fill=(160, 160, 170))
    streaks = streaks.filter(ImageFilter.GaussianBlur(2))
    img.paste(ImageChops.multiply(img, streaks))
    # the stair up to the next landing at the far right, and that landing's underside across the top
    d.rectangle([0, 0, W - 1, 12], fill=IRON)
    for x in range(0, W, 4):
        d.line([(x, 2), (x + 2, 11)], fill=IRON_M)
    d.line([(0, 12), (W - 1, 12)], fill=IRON_H)
    d.line([(0, 13), (W - 1, 13)], fill=hx("08080c"))
    for k in range(2):
        d.line([(420 + 10 * k, FOOT), (500 + 10 * k, 12)], fill=IRON, width=3)
    for k in range(1, 9):
        y = FOOT - k * 18
        x = 420 + (FOOT - y) * 80 / (FOOT - 12)
        d.line([(x, y), (x + 10, y)], fill=IRON_M, width=2)
        d.line([(x, y - 1), (x + 10, y - 1)], fill=IRON_H)
    # drips off the landing above
    for x in range(6, W, 23):
        d.line([(x, 14), (x, 14 + rnd.randint(1, 3))], fill=hx("6a7a9a"))
    # the drainpipe
    d.line([(286, 14), (286, FOOT)], fill=hx("16161c"), width=4)
    d.line([(285, 14), (285, FOOT)], fill=hx("4a4650"))
    for by in range(30, FOOT, 36):
        d.rectangle([282, by, 290, by + 1], fill=hx("26242a"))


def fe_sash(img, box, lit):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 5, y0 - 9, x1 + 5, y0 - 3], fill=hx("6a6258"))
    d.line([(x0 - 5, y0 - 9), (x1 + 5, y0 - 9)], fill=hx("8a8072"))
    d.line([(x0 - 5, y0 - 3), (x1 + 5, y0 - 3)], fill=hx("2a2020"))
    d.rectangle([x0 - 3, y0 - 2, x1 + 3, y1], fill=hx("140e0e"))
    if not lit:
        vgrad(img, (x0 + 3, y0 + 3, x1 - 3, y1 - 3), hx("262c40"), hx("0c0e16"))
        d.rectangle([x0 + 3, y0 + 3, x1 - 3, y0 + 16], fill=hx("3a3428"))
        for by in range(y0 + 5, y0 + 16, 2):
            d.line([(x0 + 3, by), (x1 - 3, by)], fill=hx("2a261e"))
        for gx, gy in ((x0 + 6, y0 + 30), (x0 + 8, y0 + 64)):
            d.line([(gx, gy + 10), (gx + 12, gy - 2)], fill=hx("3a4258"))
            d.line([(gx + 4, gy + 12), (gx + 16, gy)], fill=hx("2a3044"))
    fe_sash_frame(d, box)
    d.rectangle([x0 - 5, y1 + 1, x1 + 5, y1 + 5], fill=hx("7a7064"))
    d.line([(x0 - 5, y1 + 1), (x1 + 5, y1 + 1)], fill=hx("a09484"))
    d.line([(x0 - 5, y1 + 6), (x1 + 5, y1 + 6)], fill=hx("1e1616"))


def fe_sash_frame(d, box):
    x0, y0, x1, y1 = box
    frame, frame_d = hx("6a6258"), hx("3a3430")
    d.rectangle([x0, y0, x1, y1], outline=frame, width=3)
    my = (y0 + y1) // 2
    d.rectangle([x0, my - 2, x1, my + 1], fill=frame)
    d.line([(x0 + 3, my + 2), (x1 - 3, my + 2)], fill=frame_d)
    for gx in (x0 + (x1 - x0) // 2,):
        d.line([(gx, y0 + 3), (gx, y1 - 3)], fill=frame, width=2)
    d.point(((x0 + x1) // 2, my - 3), fill=hx("b8a470"))


def lit_glass(img):
    """Eleanor's window, a light source: lamplight through a thin muslin curtain, its folds, the shadow of the
    lamp's shade on it, and the sash bars dark against it."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = FE_LIT
    vgrad(img, (x0 + 3, y0 + 3, x1 - 3, y1 - 3), hx("f4cc80"), hx("c8843a"))
    for x in range(x0 + 4, x1 - 3, 4):  # folds in the curtain
        d.line([(x, y0 + 4), (x + 1, y1 - 4)], fill=hx("d89a50"))
        d.line([(x + 2, y0 + 4), (x + 3, y1 - 4)], fill=hx("ffe0a0"))
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y0 + 6], fill=hx("8a5a30"))  # the curtain rod
    cx = x0 + 16
    d.polygon([(cx - 6, y1 - 30), (cx + 6, y1 - 30), (cx + 9, y1 - 20), (cx - 9, y1 - 20)], fill=hx("a86a30"))
    d.line([(cx, y1 - 20), (cx, y1 - 6)], fill=hx("a86a30"), width=2)
    fe_sash_frame(d, FE_LIT)
    # the lower sash is pushed up a hand's width: a dark gap where the curtain stirs
    d.rectangle([x0 + 3, y1 - 6, x1 - 3, y1 - 3], fill=hx("3a2414"))


def fe_door(img):
    """The door off the landing into the first floor: a riveted iron frame on three strap hinges, a sheet-steel leaf
    with a bevelled panel, a wired-glass light in the top half (dark corridor behind), a stencilled FIRE EXIT and a
    riveted kick plate. The lever handle is drawn after the lighting, in fe_door_lit."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = FE_DOOR
    d.rectangle([x0 - 6, y0 - 8, x1 + 6, y1], fill=IRON)
    d.line([(x0 - 6, y0 - 8), (x1 + 6, y0 - 8)], fill=IRON_H)
    d.line([(x0 - 6, y0 - 8), (x0 - 6, y1)], fill=IRON_E)
    for y in range(y0 - 4, y1, 8):
        for x in (x0 - 3, x1 + 3):
            d.point((x, y), fill=IRON_E)
    vgrad(img, (x0, y0, x1, y1), hx("4a4c50"), hx("34363a"))
    d.line([(x0, y0), (x0, y1)], fill=hx("6a6c70"))
    d.line([(x1, y0), (x1, y1)], fill=hx("1e2024"))
    # a pressed panel round the whole leaf: lit top and left edges, shadowed bottom and right
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 21], outline=hx("2a2c30"))
    d.line([(x0 + 4, y0 + 4), (x1 - 4, y0 + 4)], fill=hx("5e6064"))
    d.line([(x0 + 4, y0 + 4), (x0 + 4, y1 - 22)], fill=hx("5e6064"))
    # strap hinges on the frame side
    for hy in (y0 + 8, (y0 + y1) // 2, y1 - 26):
        d.rectangle([x0 - 2, hy, x0 + 6, hy + 2], fill=hx("2a2c30"))
        d.line([(x0 - 2, hy), (x0 + 6, hy)], fill=hx("6a6c70"))
        d.point((x0 + 4, hy + 1), fill=hx("8a8c90"))
        d.rectangle([x0 - 2, hy - 1, x0, hy + 3], fill=hx("1e2024"))
    gx0, gy0, gx1, gy1 = x0 + 7, y0 + 8, x1 - 7, y0 + 46
    d.rectangle([gx0 - 2, gy0 - 2, gx1 + 2, gy1 + 2], fill=hx("1a1c20"))
    vgrad(img, (gx0, gy0, gx1, gy1), hx("2a2e3a"), hx("181a22"))
    glass = img.crop((gx0, gy0, gx1 + 1, gy1 + 1))
    gd = ImageDraw.Draw(glass)
    for k in range(0, gx1 - gx0 + 40, 4):  # the wire mesh, both ways
        gd.line([(k, 0), (k - 40, 40)], fill=hx("30343e"))
        gd.line([(k - 40, 0), (k, 40)], fill=hx("2c303a"))
    img.paste(glass, (gx0, gy0))
    d.line([(gx1 - 8, gy0 + 2), (gx1 - 2, gy0 + 2), (gx1 - 2, gy0 + 10)], fill=hx("4a5060"))  # a glint
    d.rectangle([gx0 - 2, gy0 - 2, gx1 + 2, gy1 + 2], outline=hx("5a5c62"))
    for x in range(gx0 - 1, gx1 + 2, 6):  # the glazing bead's screws
        d.point((x, gy0 - 2), fill=hx("7a7c80"))
        d.point((x, gy1 + 2), fill=hx("7a7c80"))
    # the kick plate, riveted, scuffed bright where boots have hit it
    d.rectangle([x0, y1 - 18, x1, y1], fill=hx("2e3034"))
    d.line([(x0, y1 - 18), (x1, y1 - 18)], fill=hx("5a5c60"))
    for x in range(x0 + 3, x1, 6):
        d.point((x, y1 - 15), fill=hx("6a6c70"))
        d.point((x, y1 - 3), fill=hx("6a6c70"))
    for x, y in ((x0 + 10, y1 - 10), (x0 + 22, y1 - 8), (x0 + 30, y1 - 11)):
        d.line([(x, y), (x + 3, y - 1)], fill=hx("5a5c60"))
    # rust round the bottom corners
    d.point((x0 + 1, y1 - 19), fill=hx("5a3020"))
    d.point((x1 - 1, y1 - 20), fill=hx("5a3020"))


FE_HANDLE = (FE_DOOR[2] - 6, FE_DOOR[1] + 74)  # the lever's spindle


def fe_door_lit(img):
    """Over the lit picture: the stencilled FIRE EXIT, chipped, and the lever handle catching the window's light
    from the right - a backplate with its screws, the lock cylinder above the spindle, a rose and the lever itself."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = FE_DOOR
    tx, ty = (x0 + x1) // 2 + 1, y0 + 58
    text(img, (tx, ty), "FIRE EXIT", hx("7a2a24"), 8)
    px = img.load()
    for x in range(x0 + 4, x1 - 3):  # stencil bridges and flaked paint
        for y in range(ty - 4, ty + 4):
            if px[x, y] == hx("7a2a24") and ((x - x0) % 5 == 0 and y == ty or (x * 7 + y * 3) % 23 == 0):
                px[x, y] = hx("2e3034")
    d.line([(x0 + 6, ty - 6), (x1 - 6, ty - 6)], fill=hx("4a2420"))   # the stencil's guide lines
    d.line([(x0 + 6, ty + 5), (x1 - 6, ty + 5)], fill=hx("3a2420"))
    # rim light from the window on the hinges' knuckles and straps, the kick plate's edge and rivets
    for hy in (y0 + 8, (y0 + y1) // 2, y1 - 26):
        d.line([(x0 - 1, hy), (x0 + 6, hy)], fill=hx("4a4a50"))
        d.point((x0 - 1, hy + 1), fill=hx("5a5a60"))
        d.point((x0 + 4, hy + 1), fill=hx("6a6a70"))
    d.line([(x0 + 1, y1 - 18), (x1 - 1, y1 - 18)], fill=hx("3e3e44"))
    for x in range(x0 + 3, x1, 6):
        d.point((x, y1 - 15), fill=hx("4e4e54"))
        d.point((x, y1 - 3), fill=hx("4e4e54"))
    for x, y in ((x0 + 10, y1 - 10), (x0 + 22, y1 - 8), (x0 + 30, y1 - 11)):
        d.line([(x, y), (x + 3, y - 1)], fill=hx("3e3e44"))
    hx_, hy = FE_HANDLE
    # backplate
    d.rectangle([hx_ - 3, hy - 9, hx_ + 2, hy + 6], fill=hx("26282e"))
    d.rectangle([hx_ - 2, hy - 8, hx_ + 1, hy + 5], fill=hx("4a4c54"))
    d.line([(hx_ + 1, hy - 8), (hx_ + 1, hy + 5)], fill=hx("8a8478"))
    d.point((hx_ - 1, hy - 7), fill=hx("9a9a9a"))
    d.point((hx_ - 1, hy + 4), fill=hx("9a9a9a"))
    # the lock cylinder and its keyhole
    d.ellipse([hx_ - 2, hy - 6, hx_ + 1, hy - 3], fill=hx("8a7a50"))
    d.point((hx_ - 1, hy - 5), fill=hx("16161a"))
    d.point((hx_ - 1, hy - 4), fill=hx("16161a"))
    # the rose and the lever reaching back towards the hinges
    d.ellipse([hx_ - 2, hy - 1, hx_ + 1, hy + 2], fill=hx("6a6c70"))
    d.rectangle([hx_ - 11, hy, hx_ - 1, hy + 1], fill=hx("5a5c62"))
    d.line([(hx_ - 11, hy), (hx_ - 1, hy)], fill=hx("b8b0a0"))
    d.rectangle([hx_ - 12, hy, hx_ - 11, hy + 2], fill=hx("4a4c54"))
    d.point((hx_ - 3, hy), fill=hx("f0e0c0"))
    d.line([(hx_ - 11, hy + 2), (hx_ - 2, hy + 2)], fill=hx("16161a"))  # its shadow on the leaf
    # the coffee can by the drainpipe catches the window on its right side and rim
    cx, cy = 262, FOOT + 2
    d.line([(cx + 7, cy - 10), (cx + 7, cy - 1)], fill=hx("a84a38"))
    d.line([(cx + 6, cy - 9), (cx + 6, cy - 2)], fill=hx("7a3428"))
    d.line([(cx + 1, cy - 11), (cx + 8, cy - 11)], fill=hx("c8a070"))
    d.line([(cx + 4, cy - 6), (cx + 7, cy - 6)], fill=hx("c84a3a"))
    d.line([(cx + 4, cy - 8), (cx + 7, cy - 8)], fill=hx("b8a078"))


def fe_props(img):
    """A coffee can of cigarette ends and a milk bottle by the drainpipe; a dead geranium on the sill."""
    d = ImageDraw.Draw(img)
    x, y = 262, FOOT + 2  # against the wall, so they show over the top rail
    # the coffee can: rolled rims, a paper label band with a red-and-cream brand, butts sticking out of the top
    can, can_d, can_l = hx("8a3a30"), hx("4a1e18"), hx("c86a50")
    d.rectangle([x, y - 11, x + 8, y], fill=can)
    d.line([(x, y - 11), (x, y)], fill=can_l)
    d.line([(x + 7, y - 11), (x + 7, y)], fill=can_d)
    d.line([(x + 8, y - 11), (x + 8, y)], fill=hx("2a1210"))
    for ry in (y - 11, y - 1):
        d.line([(x, ry), (x + 8, ry)], fill=hx("c8a070"))
    d.rectangle([x + 1, y - 8, x + 7, y - 4], fill=hx("d8c090"))
    d.line([(x + 1, y - 6), (x + 7, y - 6)], fill=hx("a83a30"))
    d.point((x + 3, y - 7), fill=hx("4a2a18"))
    d.point((x + 5, y - 5), fill=hx("4a2a18"))
    d.ellipse([x, y - 13, x + 8, y - 10], fill=hx("2a1a14"))
    for k, (bx, by) in enumerate(((x + 2, y - 14), (x + 4, y - 15), (x + 6, y - 14), (x + 3, y - 13))):
        d.line([(bx, by), (bx + (1 if k % 2 else -1), by + 2)], fill=hx("e0d8c8"))
        d.point((bx, by), fill=hx("c88a50") if k != 1 else hx("4a4040"))
    d.point((x + 9, y - 1), fill=hx("e0d8c8"))  # one that missed
    # the milk bottle: shoulders, a long neck, a foil cap, the dairy's name on the glass and an inch of milk left
    bx = x + 13
    glass, glass_l, glass_d = hx("a8b0b8"), hx("eef0f2"), hx("5a6068")
    d.rectangle([bx, y - 12, bx + 6, y], fill=glass)
    d.polygon([(bx, y - 12), (bx + 6, y - 12), (bx + 5, y - 15), (bx + 1, y - 15)], fill=glass)
    d.rectangle([bx + 2, y - 18, bx + 4, y - 15], fill=glass)
    d.rectangle([bx + 1, y - 20, bx + 5, y - 18], fill=hx("c8a040"))
    d.line([(bx + 1, y - 20), (bx + 5, y - 20)], fill=hx("f0d890"))
    d.rectangle([bx + 1, y - 3, bx + 5, y - 1], fill=hx("f4f2ea"))
    d.line([(bx + 1, y - 3), (bx + 5, y - 3)], fill=hx("ffffff"))
    d.line([(bx + 1, y - 9), (bx + 5, y - 9)], fill=hx("a83a30"))
    d.line([(bx + 2, y - 7), (bx + 4, y - 7)], fill=hx("a83a30"))
    d.line([(bx, y - 12), (bx, y)], fill=glass_l)
    d.line([(bx + 2, y - 17), (bx + 2, y - 15)], fill=glass_l)
    d.line([(bx + 6, y - 12), (bx + 6, y)], fill=glass_d)
    d.line([(bx, y), (bx + 6, y)], fill=glass_d)
    shadow(img, "rect", [x - 1, y, bx + 9, y + 2], 0.5, 1)
    sx0, sy0, sx1, sy1 = FE_LIT
    d.polygon([(sx1 - 16, sy1), (sx1 - 4, sy1), (sx1 - 6, sy1 - 8), (sx1 - 14, sy1 - 8)], fill=hx("8a4a2a"))
    for k in range(4):
        d.line([(sx1 - 10, sy1 - 8), (sx1 - 16 + 4 * k, sy1 - 18 + (k % 2) * 3)], fill=hx("4a3a20"))


def paint_fire_escape():
    img = Image.new("RGB", (W, H))
    fe_wall(img)
    for box in FE_WINDOWS:
        fe_sash(img, box, box == FE_LIT)
    fe_door(img)
    below(img)
    landing(img)
    fe_props(img)
    fe_rails(ImageDraw.Draw(img))
    wx0, wy0, wx1, wy1 = FE_LIT
    lights = [
        ("ellipse", [-120, -40, 140, 300], (170, 34, 54), 1.0, 40),             # the big sign round the corner
        ("ellipse", [wx0 - 70, wy0 - 30, wx1 + 70, FOOT + 30], (200, 140, 70), 1.0, 26),  # the lit window
        ("polygon", [(wx0 - 10, FOOT), (wx1 + 10, FOOT), (wx1 + 50, EDGE), (wx0 - 50, EDGE)], (150, 100, 50), 0.8,
         14),
        ("rect", [-20, -20, W + 20, 40], (26, 26, 48), 1.0, 30),                 # the city's glow
        ("rect", [-20, FOOT, W + 20, H + 20], (40, 36, 60), 0.6, 20),
    ]
    img = illuminate(img, (44, 44, 76), lights)
    shadow(img, "rect", [-20, 0, W + 20, 30], 0.35, 12)
    lit_glass(img)
    fe_door_lit(img)
    light(img, "ellipse", [wx0 - 12, wy0 - 10, wx1 + 12, wy1 + 12], hx("ffc070"), 0.22, 10)
    d = ImageDraw.Draw(img)
    fe_ladder(d)
    # the top rail catches the neon from the left
    for y in (FE_TOP - 1,):
        for x in range(0, 200, 2):
            d.point((x, y), fill=mix(img.getpixel((x, y)), (255, 90, 110), 0.5 * (1 - x / 200)))
    rnd = random.Random(70)
    px = img.load()
    for _ in range(300):  # wet sheen on the grating's bars
        x, y = rnd.randint(0, W - 1), rnd.randint(FOOT + 3, EDGE)
        c = px[x, y]
        if sum(c) < 120:
            continue
        px[x, y] = mix(c, (255, 120, 140) if x < 200 else (255, 210, 150), 0.4)
    vignette(img, 0.45, (14, 10, 26), 44)
    return img


def build_fire_escape():
    img = paint_fire_escape()
    pal = palette_of(img, 116) + [hx("f4cc80"), hx("ffe0a0"), hx("d89a50"), hx("c8843a"), hx("8a5a30"),
                                  hx("3a2414"), hx("ff3048"), hx("12151c"), hx("a84a38"), hx("7a3428"), hx("c8a070"),
                                  hx("b8a078")]
    save(pixelize(img, pal), "rooms", "motel_fire_escape.png")
    save(fire_escape_front(pixelize(img, pal)), "rooms", "motel_fire_escape_fg.png")


def fire_escape_front(px):
    """The front safety rail cut out of the finished background, for the scene to y-sort in front of the characters
    standing on the landing. Cropped to the rail's rows; the scene places it at (0, FE_FG_Y)."""
    mask = Image.new("L", (W, H), 0)
    fe_front_rail(ImageDraw.Draw(mask), mask=True)
    return cut(px, mask).crop((0, FE_FG_Y, W, EDGE + 5))


def build():
    build_alley()
    build_fire_escape()
