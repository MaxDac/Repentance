"""Act 2/3 locations: Rose's terrace house at dusk, the night road behind the Harrington building, Harrington senior's
office at night, and Daniel's bedroom in the present day.

Each room is painted once per state; overlays are crops of the state variant pixelized with the base palette, so they
line up pixel-exactly when placed at the box's top-left (printed by build())."""
import math
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import (W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, palette_of, pixelize, save,
                     text, floor_boards, cut)

H = FULL_H


def bricks(img, box, col, mortar, seed, h=5, w=12):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    rnd = random.Random(seed)
    for y in range(y0, y1, h):
        off = (w // 2) if ((y - y0) // h) % 2 else 0
        for x in range(x0 - off, x1, w):
            c = mul(col, rnd.uniform(0.86, 1.1))
            d.rectangle([max(x0, x + 1), y + 1, min(x1, x + w - 1), min(y1, y + h - 1)], fill=c)
        d.line([(x0, y), (x1, y)], fill=mortar)
    noise(img, box, 6, seed)


def overlay(variant, base_px, pal, box, name):
    v = pixelize(variant, pal)
    diff = ImageChops.difference(v.crop(box), base_px.crop(box)).convert("L").point(lambda p: 255 if p else 0)
    bb = diff.getbbox()
    if not bb:
        raise ValueError(name)
    tight = (box[0] + bb[0], box[1] + bb[1], box[0] + bb[2], box[1] + bb[3])
    save(v.crop(tight), "rooms", f"{name}.png")
    print(name, "at", tight[:2])


# ------------------------------------------------------------------------------------------------ ROSE'S HOUSE

def window(d, x0, y0, x1, y1, lit, frame=hx("d8d0c0")):
    d.rectangle([x0 - 3, y0 - 6, x1 + 3, y0 - 2], fill=hx("b8ae9a"))
    d.rectangle([x0 - 2, y1, x1 + 2, y1 + 3], fill=hx("a49a86"))
    d.rectangle([x0, y0, x1, y1], fill=hx("e8b860") if lit else hx("1c2236"))
    if lit:
        d.rectangle([x0 + 2, y0 + 2, x0 + 8, y1 - 2], fill=hx("8a3a30"))
        d.rectangle([x1 - 8, y0 + 2, x1 - 2, y1 - 2], fill=hx("8a3a30"))
    else:
        d.line([(x0 + 3, y0 + 4), (x0 + 12, y0 + 14)], fill=hx("4a5470"))
    d.rectangle([x0, y0, x1, y1], outline=frame)
    my = (y0 + y1) // 2
    d.rectangle([x0, my - 1, x1, my], fill=frame)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame)


def fanlight(d, x0, y0, x1, lit, number=None, img=None):
    """The semicircular fanlight over a door: a moulded stone arch with a keystone, glass warm from the hall (or dim
    when the hall is dark) with a sheen at the top, and leaded bars in a sunburst: a small hub (carrying the house
    number painted in gilt), spokes out to the rim, a ring across the middle and a scallop of petals along the edge."""
    cx, sy = (x0 + x1) // 2, y0 - 1
    rx, ry = (x1 - x0) // 2 - 1, 13
    stone, stone_hi, stone_lo = hx("c2b8a2"), hx("e6dcc6"), hx("6e6252")
    lead = hx("2a2018") if lit else hx("101014")
    inner, outer = (hx("fff0c0"), hx("e8a850")) if lit else (hx("4a4a5a"), hx("1c2236"))
    # the arch moulding: a shadowed outer fillet, a pale bead and a stone band, then the glass's own reveal
    for k, c in ((4, stone_lo), (3, stone_hi), (2, stone), (1, hx("8a7e6a"))):
        d.pieslice([cx - rx - k, sy - ry - k, cx + rx + k, sy + ry + k], 180, 360, fill=c)
    # glass, glowing from the hub outward
    for k in range(ry, -1, -1):
        t = k / ry
        d.pieslice([cx - rx * t, sy - k, cx + rx * t, sy + k], 180, 360, fill=mix(inner, outer, t))
    # a sheen where the sky catches the upper panes
    for a, r in ((215, 0.8), (225, 0.82), (235, 0.84)):
        ang = math.radians(a)
        d.point((round(cx + rx * r * math.cos(ang)), round(sy + ry * r * math.sin(ang))),
                fill=hx("fff4d0") if lit else hx("8a96b4"))
    # the leading: five spokes fanning from the hub, and an arc of petals, one bulging into each pane
    hub_x, hub_y = 9, 8
    for i in range(1, 6):
        ang = math.radians(180 + i * 30)
        c, s = math.cos(ang), math.sin(ang)
        d.line([(round(cx + hub_x * c), round(sy + hub_y * s)), (round(cx + rx * c), round(sy + ry * s))], fill=lead)
    for i in range(6):
        a0, a1 = 180 + i * 30, 210 + i * 30
        pts = [(cx + (rx - 4 + 2.5 * math.sin(math.pi * k / 6)) * math.cos(math.radians(a0 + 5 * k)),
                sy + (ry - 4 + 2.5 * math.sin(math.pi * k / 6)) * math.sin(math.radians(a0 + 5 * k))) for k in range(7)]
        d.line([(round(px), round(py)) for px, py in pts], fill=lead)
    d.pieslice([cx - hub_x, sy - hub_y, cx + hub_x, sy + hub_y], 180, 360, fill=mix(inner, hx("fff8e0"), 0.5) if lit
               else hx("3a3c4c"), outline=lead)
    d.arc([cx - rx, sy - ry, cx + rx, sy + ry], 180, 360, fill=lead)
    if number and img is not None:
        text(img, (cx, sy - 5), number, hx("5a3810") if lit else hx("c8a040"), 8)
    # keystone, flaring upward, proud of the moulding
    top, bot = sy - ry - 7, sy - ry + 1
    d.polygon([(cx - 2, bot), (cx + 2, bot), (cx + 3, top), (cx - 3, top)], fill=stone)
    d.line([(cx - 3, top), (cx + 3, top)], fill=stone_hi)
    d.line([(cx - 3, top), (cx - 2, bot)], fill=stone_hi)
    d.line([(cx + 3, top + 1), (cx + 2, bot)], fill=stone_lo)
    d.line([(cx - 1, top + 3), (cx + 1, top + 3)], fill=hx("a49882"))


def door(d, x0, y0, x1, y1, col, number=None, img=None, lit=True):
    # the stone surround: a hood moulding with dentils over the arch, fluted pilasters on plinths either side
    d.rectangle([x0 - 5, y0 - 18, x1 + 5, y1], fill=hx("b0a690"))
    d.rectangle([x0 - 7, y0 - 22, x1 + 7, y0 - 19], fill=hx("c6bca6"))
    d.line([(x0 - 7, y0 - 22), (x1 + 7, y0 - 22)], fill=hx("eae0ca"))
    d.line([(x0 - 7, y0 - 18), (x1 + 7, y0 - 18)], fill=hx("4e4436"))
    for x in range(x0 - 5, x1 + 6, 3):
        d.point((x, y0 - 17), fill=hx("8a806c"))
    for jx, kx in ((x0 - 5, x0 - 1), (x1 + 1, x1 + 5)):
        for fx in range(jx + 1, kx, 2):
            d.line([(fx, y0 + 4), (fx, y1 - 8)], fill=hx("8c826e"))
        d.line([(jx, y0 + 2), (jx, y1)], fill=hx("dcd2bc"))
        d.rectangle([jx - 1, y1 - 7, kx + 1, y1], fill=hx("c0b6a0"))
        d.line([(jx - 1, y1 - 7), (kx + 1, y1 - 7)], fill=hx("e2d8c2"))
        # the impost block the arch springs from
        d.rectangle([jx - 1, y0 - 4, kx + 1, y0 + 1], fill=hx("cac0aa"))
        d.line([(jx - 1, y0 - 4), (kx + 1, y0 - 4)], fill=hx("f0e6d0"))
        d.line([(jx - 1, y0 + 2), (kx + 1, y0 + 2)], fill=hx("5e5444"))
    fanlight(d, x0, y0, x1, lit, number, img)
    # the transom bar the fanlight sits on
    d.rectangle([x0 - 1, y0 - 2, x1 + 1, y0], fill=hx("d6ccb4"))
    d.line([(x0 - 1, y0 - 2), (x1 + 1, y0 - 2)], fill=hx("f2e8d2"))
    d.line([(x0 - 1, y0), (x1 + 1, y0)], fill=hx("6a604e"))
    d.rectangle([x0, y0 + 1, x1, y1], fill=col)
    for (a, b, c, e) in ((x0 + 4, y0 + 5, (x0 + x1) // 2 - 2, y0 + 38), ((x0 + x1) // 2 + 2, y0 + 5, x1 - 4, y0 + 38),
                         (x0 + 4, y0 + 44, (x0 + x1) // 2 - 2, y1 - 6), ((x0 + x1) // 2 + 2, y0 + 44, x1 - 4, y1 - 6)):
        d.rectangle([a, b, c, e], outline=mul(col, 0.62))
        d.line([(a + 1, b + 1), (c - 1, b + 1)], fill=mul(col, 1.3))
    d.ellipse([x1 - 9, y0 + 41, x1 - 6, y0 + 44], fill=hx("d8b450"))


def street_lamp(d, x, top, foot):
    """A cast-iron gas lamp, finial at top and plinth at foot: a domed cap with a vent band, a four-sided glazed
    lantern with frame bars and a glowing mantle, a collar and scrolls under it, a ladder-rest crossbar, and a fluted
    post on a moulded base."""
    iron, iron_hi, iron_lo = hx("1c1c22"), hx("4a4a56"), hx("0c0c10")
    lt = top + 13  # the lantern's glazing, between its cap and its floor
    lb = lt + 12
    # finial and cap: a ball on a stem, a dome with a vent band, a flared brim
    d.ellipse([x - 1, top, x + 1, top + 2], fill=iron_hi)
    d.line([(x, top + 3), (x, lt - 8)], fill=iron)
    d.pieslice([x - 6, lt - 9, x + 7, lt + 1], 180, 360, fill=iron)
    d.arc([x - 6, lt - 9, x + 7, lt + 1], 200, 250, fill=iron_hi)
    for vx in range(x - 3, x + 5, 2):
        d.point((vx, lt - 3), fill=hx("f0c878"))
    d.rectangle([x - 8, lt - 2, x + 9, lt], fill=iron)
    d.line([(x - 8, lt - 2), (x + 9, lt - 2)], fill=iron_hi)
    # the lantern: a tapered glazed body, the corner bars, the glowing mantle on its burner
    body = [(x - 6, lt + 1), (x + 7, lt + 1), (x + 4, lb), (x - 3, lb)]
    d.polygon(body, fill=hx("f6d48a"))
    d.polygon([(x - 4, lt + 2), (x + 5, lt + 2), (x + 3, lb - 1), (x - 2, lb - 1)], fill=hx("ffe2a0"))
    d.ellipse([x - 1, lt + 4, x + 2, lt + 8], fill=hx("ffffff"))
    d.line([(x, lt + 9), (x + 1, lt + 9)], fill=hx("a07038"))
    d.line([(x - 1, lb - 1), (x + 2, lb - 1)], fill=iron)
    d.polygon(body, outline=iron)
    d.line([(x - 2, lt + 1), (x - 1, lb)], fill=iron)
    d.line([(x + 3, lt + 1), (x + 2, lb)], fill=iron)
    d.rectangle([x - 4, lb, x + 5, lb + 2], fill=iron)
    d.line([(x - 4, lb + 2), (x + 5, lb + 2)], fill=iron_hi)
    # the collar and its scrolls, cradling the lantern
    d.rectangle([x - 2, lb + 3, x + 3, lb + 12], fill=iron)
    d.rectangle([x - 4, lb + 4, x + 5, lb + 6], fill=iron)
    d.line([(x - 4, lb + 4), (x + 5, lb + 4)], fill=iron_hi)
    for s in (-1, 1):
        ex = x - 4 if s < 0 else x + 5
        d.line([(ex, lb + 5), (ex + 2 * s, lb + 3), (ex + 3 * s, lb + 1)], fill=iron)
        d.point((ex + 3 * s, lb), fill=iron_hi)
    # the ladder-rest crossbar, with ball ends
    bar = lb + 9
    d.line([(x - 8, bar), (x + 9, bar)], fill=iron, width=2)
    d.line([(x - 8, bar - 1), (x + 9, bar - 1)], fill=iron_hi)
    for bx in (x - 9, x + 10):
        d.ellipse([bx - 1, bar - 2, bx + 1, bar], fill=iron_hi)
    # the fluted shaft, with a band partway down
    shaft_top = lb + 12
    d.rectangle([x - 2, shaft_top, x + 3, foot - 17], fill=iron)
    for fx, c in ((x - 1, iron_hi), (x + 1, hx("2e2e38")), (x + 3, iron_lo)):
        d.line([(fx, shaft_top + 2), (fx, foot - 19)], fill=c)
    for ry in (shaft_top, foot - 44):
        d.rectangle([x - 3, ry, x + 4, ry + 2], fill=iron)
        d.line([(x - 3, ry), (x + 4, ry)], fill=iron_hi)
    # base: a ring, a bell and a plinth, wider than the post
    d.rectangle([x - 4, foot - 17, x + 5, foot - 14], fill=iron)
    d.line([(x - 4, foot - 17), (x + 5, foot - 17)], fill=iron_hi)
    d.polygon([(x - 5, foot - 4), (x + 6, foot - 4), (x + 4, foot - 14), (x - 3, foot - 14)], fill=iron)
    d.line([(x - 5, foot - 5), (x - 3, foot - 13)], fill=iron_hi)
    d.line([(x - 4, foot - 9), (x + 5, foot - 9)], fill=hx("2e2e38"))
    d.rectangle([x - 7, foot - 4, x + 8, foot], fill=iron)
    d.line([(x - 7, foot - 4), (x + 8, foot - 4)], fill=iron_hi)

def stoop(d, x0, x1, top):
    for i in range(3):
        y = top + i * 6
        d.rectangle([x0 - i * 4, y, x1 + i * 4, y + 6], fill=mix(hx("9c968a"), hx("6a665e"), i / 3))
        d.line([(x0 - i * 4, y), (x1 + i * 4, y)], fill=hx("c4beb0"))


def railings(d, x0, x1, y0, y1):
    d.line([(x0, y0), (x1, y0)], fill=hx("161618"), width=2)
    for x in range(x0, x1 + 1, 5):
        d.line([(x, y0 - 3), (x, y1)], fill=hx("1c1c20"))
        d.point((x, y0 - 4), fill=hx("3a3a40"))


ROSE_UPPER = (32, 91, 169, 224, 283, 353, 412)  # over the doors at 48, 240 and 428, and over the ground windows
ROSE_UPPER_LIT = (169, 412)
ROSE_UPPER_Y = (34, 84)
ROSE_LAMP_X = 125
ROSE_LAMP_TOP, ROSE_LAMP_FOOT = 92, 256  # the foot is also the lamp's y-sort baseline


def rose_lamp_mask():
    """The lamp post's own pixels, so the scene can y-sort it in front of whoever walks behind it."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    street_lamp(ImageDraw.Draw(layer), ROSE_LAMP_X, ROSE_LAMP_TOP, ROSE_LAMP_FOOT)
    return layer.getchannel("A").point(lambda v: 255 if v else 0)


def rose_lamp_box():
    return rose_lamp_mask().getbbox()


def paint_rose(opened=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 40), hx("2a2c58"), hx("c8705a"))
    # chimneys against the dusk
    for x in (36, 112, 212, 286, 376, 440):
        d.rectangle([x, 0, x + 14, 18], fill=hx("3a2420"))
        d.rectangle([x + 3, 0, x + 6, 1], fill=hx("6a4a3a"))
    houses = ((0, 150, hx("6e3a2e"), 31), (150, 330, hx("7c4634"), 32), (330, W, hx("66382e"), 33))
    for x0, x1, col, seed in houses:
        bricks(img, (x0, 14, x1 - 1, 214), col, mul(col, 0.62), seed)
        d.rectangle([x0, 12, x1 - 1, 20], fill=hx("8a8270"))
        d.line([(x0, 21), (x1 - 1, 21)], fill=hx("3a3024"))
        d.line([(x1 - 1, 12), (x1 - 1, 214)], fill=hx("2e1c16"))
        d.rectangle([x0, 16, x1 - 1, 18], fill=hx("b0a18a"))
        for x in range(x0 + 4, x1 - 4, 6):
            d.rectangle([x, 22, x + 3, 25], fill=hx("493027"))
        for y in (114, 188):
            d.line([(x0, y), (x1 - 1, y)], fill=mul(col, 1.18))
            d.line([(x0, y + 2), (x1 - 1, y + 2)], fill=mul(col, 0.65))
        for px in (x0 + 5, x1 - 5):
            d.line([(px, 20), (px, 211)], fill=hx("322e2a"), width=3)
            d.line([(px - 1, 20), (px - 1, 211)], fill=hx("72685a"))
            for py in (70, 132, 194):
                d.line([(px - 2, py), (px + 2, py)], fill=hx("a09078"))
    # upper floor windows
    # upper floor windows: a tall house, each first-floor window centred over the door or window below it
    for wx in ROSE_UPPER:
        window(d, wx, ROSE_UPPER_Y[0], wx + 32, ROSE_UPPER_Y[1], lit=wx in ROSE_UPPER_LIT)
    # neighbours' doors and ground windows
    door(d, 30, 120, 66, 198, hx("26303a"), lit=False)
    window(d, 86, 124, 128, 178, lit=False)
    door(d, 410, 120, 446, 198, hx("4a2626"))
    window(d, 348, 124, 390, 178, lit=True)
    # Rose's door: deep green, number 14 in the fanlight, a brass knocker on the centre stile
    door(d, 222, 110, 258, 198, hx("23402e"), "14", img)
    d.rectangle([239, 126, 241, 128], fill=hx("8a6a2a"))
    d.ellipse([237, 128, 243, 135], outline=hx("d8b450"))
    d.point((240, 135), fill=hx("f0d070"))
    window(d, 278, 122, 320, 178, lit=True)
    window(d, 166, 122, 204, 178, lit=False)
    for x0, y0, x1, y1 in (
            *((wx, ROSE_UPPER_Y[0], wx + 32, ROSE_UPPER_Y[1]) for wx in ROSE_UPPER),
            (86, 124, 128, 178), (348, 124, 390, 178),
            (278, 122, 320, 178), (166, 122, 204, 178)):
        d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1], outline=hx("594b3c"))
        d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=hx("ece0c4"))
        d.line([(x0 - 4, y1 + 4), (x1 + 4, y1 + 4)], fill=hx("493a30"))
        for x in range(x0 + 3, x0 + 9, 2):
            d.line([(x, y0 + 3), (x, y1 - 3)], fill=hx("745c4c"))
        for x in range(x1 - 8, x1 - 2, 2):
            d.line([(x, y0 + 3), (x, y1 - 3)], fill=hx("4a3836"))
        d.rectangle([x0 - 1, y1 + 1, x1 + 1, y1 + 2], fill=hx("c6bba6"))
    for x0 in (30, 222, 410):
        d.rectangle([x0 - 3, 151, x0 + 1, 156], fill=hx("b6a68c"))
    d.rectangle([262, 120, 272, 127], fill=hx("302a24"), outline=hx("bca06a"))
    d.rectangle([228, 174, 251, 177], fill=hx("8a783e"))
    for x in (36, 112, 212, 286, 376, 440):
        for y in range(4, 14, 5):
            d.line([(x + 1, y), (x + 13, y)], fill=hx("765044"))
            d.line([(x + 6 + (y // 5 % 2) * 3, y - 4), (x + 6 + (y // 5 % 2) * 3, y)], fill=hx("241a18"))
    # brass bell push beside the door
    d.rectangle([265, 146, 271, 156], fill=hx("8a6a2a"))
    d.ellipse([266, 149, 270, 153], fill=hx("e0c060"))
    if opened:
        # the door swung in: a warm hall, wallpaper, a stair rail and the door leaf's edge
        d.rectangle([222, 110, 258, 198], fill=hx("e8c27a"))
        for x in range(224, 258, 6):
            d.line([(x, 112), (x, 160)], fill=hx("d4a868"))
        d.rectangle([222, 160, 258, 198], fill=hx("8a5a34"))
        d.line([(240, 198), (258, 170)], fill=hx("5a3a20"), width=2)
        for x in range(244, 258, 4):
            d.line([(x, 198 - (x - 240) * 28 // 18), (x, 186 - (x - 240) * 28 // 18)], fill=hx("4a2e18"))
        d.rectangle([222, 110, 228, 198], fill=hx("18301f"))
        d.line([(228, 110), (228, 198)], fill=hx("0c1810"))
        d.rectangle([224, 112, 227, 116], fill=hx("fff0c0"))
    for x0, x1 in ((24, 72), (216, 264), (404, 452)):
        stoop(d, x0, x1, 198)
    railings(d, 0, 18, 202, 214)
    railings(d, 82, 206, 202, 214)
    railings(d, 278, 396, 202, 214)
    railings(d, 464, W - 1, 202, 214)
    # pavement and kerb
    vgrad(img, (0, 214, W - 1, 256), hx("6a6660"), hx("4e4a46"))
    for i, x in enumerate(range(-40, W + 40, 40)):
        shift = (i % 3 - 1) * 6
        d.line([(x + shift, 214), (x - 24 + shift, 256)], fill=hx("3e3a36"))
        if i % 4 == 0:
            d.line([(x + 8, 230), (x + 22, 244)], fill=hx("2e2c28"))
    for y in (226, 240):
        d.line([(0, y), (W, y)], fill=hx("44403c"))
    d.rectangle([0, 256, W - 1, 260], fill=hx("8a8680"))
    vgrad(img, (0, 261, W - 1, H - 1), hx("2a2a2e"), hx("1e1e22"))
    noise(img, (0, 214, W - 1, H - 1), 5, 34)
    # dusk: cool everything down, then the lamp, lit windows and lit fanlights glow
    dusk = ImageChops.multiply(img, Image.new("RGB", img.size, (150, 150, 196)))
    img.paste(dusk)
    light(img, "ellipse", [70, 70, 180, 260], hx("e0a050"), 0.45, 24)
    light(img, "ellipse", [ROSE_LAMP_X - 14, 96, ROSE_LAMP_X + 15, 126], hx("ffd890"), 0.4, 6)
    for x0, y0 in ((222, 110), (410, 120)):
        light(img, "rect", [x0 + 1, y0 - 14, x0 + 35, y0 - 1], hx("e8b060"), 0.4, 3)
    # the lamp post, painted over the glow so the iron stays crisp and the lantern keeps its own light
    street_lamp(ImageDraw.Draw(img), ROSE_LAMP_X, ROSE_LAMP_TOP, ROSE_LAMP_FOOT)
    for box in ([270, 112, 330, 190], [340, 114, 400, 190],
                *([wx - 8, ROSE_UPPER_Y[0] - 8, wx + 40, ROSE_UPPER_Y[1] + 8] for wx in ROSE_UPPER_LIT)):
        light(img, "rect", box, hx("d89040"), 0.35, 10)
    if opened:
        light(img, "polygon", [(222, 110), (258, 110), (290, 224), (196, 224)], hx("f0b860"), 0.55, 10)
    vignette(img, 0.5, (20, 16, 40), 46)
    return img


def build_rose():
    base, opened = paint_rose(), paint_rose(True)
    pal = palette_of(Image.blend(base, opened, 0.5), 120)
    px = pixelize(base, pal)
    save(px, "rooms", "rose_house.png")
    overlay(opened, px, pal, (190, 100, 300, 230), "rose_house_door")
    mask, box = rose_lamp_mask(), rose_lamp_box()
    save(cut(px, mask).crop(box), "rooms", "rose_house_lamp.png")
    print("rose_house_lamp at", box[:2])
    return px


# ------------------------------------------------------------------------------------------------ HARRINGTON ROAD

def crate(d, x0, y0, s=26, seed=0):
    """An open-topped slatted fruit crate seen from just above: the inside over the near rim, nailed slats with dark
    gaps between them, corner battens, and a grower's stencil."""
    wood, lit, ink = hx("7a5e38"), hx("a8845a"), hx("1e140a")
    t = 4
    rnd = random.Random(seed or x0 * 7 + y0)
    d.rectangle([x0, y0, x0 + s, y0 + t], fill=hx("2e2010"), outline=ink)
    d.line([(x0 + 1, y0 + 1), (x0 + s - 1, y0 + 1)], fill=hx("5a4428"))
    d.line([(x0 + 2, y0 + 2), (x0 + s - 2, y0 + 2)], fill=hx("3e2c18"))
    d.rectangle([x0, y0 + t, x0 + s, y0 + s], fill=hx("221608"), outline=ink)
    n = 3
    hs = (s - t - 1 - (n - 1)) // n
    for i in range(n):
        sy = y0 + t + 1 + i * (hs + 1)
        sy1 = y0 + s - 1 if i == n - 1 else sy + hs - 1
        c = mul(wood, rnd.uniform(0.86, 1.08))
        d.rectangle([x0 + 1, sy, x0 + s - 1, sy1], fill=c)
        d.line([(x0 + 1, sy), (x0 + s - 1, sy)], fill=mul(c, 1.25))
        d.line([(x0 + 1, sy1), (x0 + s - 1, sy1)], fill=mul(c, 0.72))
        for _ in range(2):
            gx, gy = rnd.randint(x0 + 5, x0 + s - 9), rnd.randint(sy + 1, max(sy + 1, sy1 - 1))
            d.line([(gx, gy), (gx + rnd.randint(3, 6), gy)], fill=mul(c, 0.8))
        if rnd.random() < 0.5:  # a split in the slat
            gx = rnd.randint(x0 + 6, x0 + s - 6)
            d.line([(gx, sy + 1), (gx + 2, sy1)], fill=mul(c, 0.6))
    for bx in (x0 + 1, x0 + s - 3):  # corner battens, nailed through each slat
        d.rectangle([bx, y0 + t + 1, bx + 2, y0 + s - 1], fill=mul(wood, 0.82))
        d.line([(bx, y0 + t + 1), (bx, y0 + s - 1)], fill=mul(wood, 1.1))
        for i in range(n):
            ny = y0 + t + 1 + i * (hs + 1) + hs // 2
            d.point((bx + 1, ny), fill=hx("2a2a2e"))
    d.line([(x0, y0 + t), (x0 + s, y0 + t)], fill=lit)
    cx, cy = x0 + s // 2, y0 + t + 1 + (hs + 1) + hs // 2
    d.ellipse([cx - 5, cy - 2, cx + 5, cy + 2], outline=hx("6a2a1a"))
    d.line([(cx - 2, cy), (cx + 2, cy)], fill=hx("6a2a1a"))


ROAD_WINDOW = (339, 26, 383, 98)  # Harrington's office: one of the row, as dark as the rest at this hour
LANDING_Y = 104
ROAD_WINDOW_COLS = (153, 215, 277, 339, 401)  # every window on both floors sits on this grid
ROAD_GROUND_Y = 122


def road_window(d, x, y):
    """One of the building's identical office windows: a stone lintel with a keystone, a dark reveal, a six-over-six
    sash with a blind drawn a little way down, the night sky caught in the glass, and a stone sill."""
    w, h = ROAD_WINDOW[2] - ROAD_WINDOW[0], ROAD_WINDOW[3] - ROAD_WINDOW[1]
    frame, frame_d = hx("6e6a62"), hx("3a3832")
    d.rectangle([x - 2, y - 2, x + w + 2, y + h + 1], fill=hx("1a1414"))
    d.rectangle([x - 4, y - 7, x + w + 4, y - 3], fill=hx("625850"))
    d.line([(x - 4, y - 7), (x + w + 4, y - 7)], fill=hx("847868"))
    d.line([(x - 4, y - 3), (x + w + 4, y - 3)], fill=hx("2a201c"))
    for jx in range(x - 4 + 7, x + w + 4, 7):
        d.line([(jx, y - 6), (jx, y - 4)], fill=hx("4a4038"))
    kx = x + w // 2
    d.polygon([(kx - 3, y - 9), (kx + 3, y - 9), (kx + 2, y - 2), (kx - 2, y - 2)], fill=hx("6e6258"))
    d.line([(kx - 3, y - 9), (kx + 3, y - 9)], fill=hx("8a7e70"))
    # glass, with the sky's last light at the top and the reflection of the far roofs
    vgrad(d._image, (x + 2, y + 2, x + w - 2, y + h - 2), hx("262a3e"), hx("0e1018"))
    # a blind drawn a little way down the upper sash
    d.rectangle([x + 2, y + 2, x + w - 2, y + 12], fill=hx("3c362c"))
    for by in range(y + 4, y + 12, 2):
        d.line([(x + 2, by), (x + w - 2, by)], fill=hx("2e2a22"))
    d.rectangle([x + 2, y + 12, x + w - 2, y + 13], fill=hx("4e463a"))
    d.ellipse([kx - 1, y + 14, kx + 1, y + 16], outline=hx("5a5244"))
    for gx, gy in ((x + 4, y + 18), (x + 4, y + 40)):
        d.line([(gx, gy + 8), (gx + 9, gy - 1)], fill=hx("343a52"))
        d.line([(gx + 3, gy + 10), (gx + 12, gy + 1)], fill=hx("262a3e"))
    d.line([(x + 2, y + h - 4), (x + w - 2, y + h - 4)], fill=hx("1a1c26"))
    # sashes: the frame, the meeting rail with its catch, glazing bars three panes across and two down
    d.rectangle([x, y, x + w, y + h], outline=frame, width=2)
    my = y + h // 2
    d.rectangle([x, my - 1, x + w, my + 1], fill=frame)
    d.line([(x + 2, my + 2), (x + w - 2, my + 2)], fill=frame_d)
    d.rectangle([x, y + h - 3, x + w, y + h], fill=frame)
    for gx in (x + w // 3, x + 2 * w // 3):
        d.line([(gx, y + 2), (gx, y + h - 2)], fill=frame)
    for gy in ((y + my) // 2, (my + y + h) // 2):
        d.line([(x + 2, gy), (x + w - 2, gy)], fill=frame)
    d.line([(x + 2, y + 2), (x + 2, y + h - 2)], fill=frame_d)
    d.line([(x + 2, y + 2), (x + w - 2, y + 2)], fill=frame_d)
    d.point((kx, my), fill=hx("b8a470"))
    for lx in (x + 8, x + w - 8):
        d.point((lx, y + h - 4), fill=hx("8a8270"))
    d.rectangle([x - 4, y + h + 1, x + w + 4, y + h + 4], fill=hx("7a6c60"))
    d.line([(x - 4, y + h + 1), (x + w + 4, y + h + 1)], fill=hx("a08e7c"))
    d.line([(x - 4, y + h + 4), (x + w + 4, y + h + 4)], fill=hx("2a2020"))
    d.line([(x - 2, y + h + 5), (x + w + 2, y + h + 5)], fill=hx("231a1a"))


BALCONY_X = (131, W - 1)  # the landing runs the whole office floor, from the building's corner off the right edge
BALCONY_BRACKETS = (141, 206, 268, 323, 397, 462)  # one knee bracket in every pier between the windows


def fire_escape(d, freed=False):
    """The landing along the whole office floor, its railing, brackets and the drop ladder. Every part shares one iron:
    near-black with a cold highlight on the edges that face the street."""
    iron, edge, mid, hi = hx("141820"), hx("68707c"), hx("3a414c"), hx("89909a")
    y = LANDING_Y
    x0, x1 = BALCONY_X
    # railing: evenly spaced balusters between a top rail, a middle rail and a kick plate; heavier posts at the corner
    # and over every bracket
    for x in range(x0 + 3, x1 + 1, 5):
        d.line([(x, 77), (x, y)], fill=iron)
        d.line([(x - 1, 77), (x - 1, y)], fill=mid)
    for ry in (76, 90):
        d.line([(x0, ry), (x1, ry)], fill=iron, width=2)
        d.line([(x0, ry - 1), (x1, ry - 1)], fill=edge)
    d.rectangle([x0, y - 4, x1, y - 1], fill=iron)
    d.line([(x0, y - 4), (x1, y - 4)], fill=mid)
    for px in (x0, *BALCONY_BRACKETS):
        d.rectangle([px - 1, 74, px + 1, y + 4], fill=iron)
        d.line([(px - 1, 74), (px - 1, y + 4)], fill=edge)
        d.rectangle([px - 2, 72, px + 2, 74], fill=mid)
        d.line([(px - 2, 72), (px + 2, 72)], fill=hi)
        d.point((px, 90), fill=hi)
    # the landing: an angle-iron front edge, and the grating's slats seen from below, crossed by the bearer bars
    d.rectangle([x0, y, x1, y + 5], fill=iron)
    d.line([(x0, y), (x1, y)], fill=hi)
    d.line([(x0, y + 1), (x1, y + 1)], fill=edge)
    for x in range(x0 + 1, x1, 3):
        d.line([(x, y + 3), (x + 1, y + 5)], fill=mid)
    for x in range(x0 + 6, x1, 12):
        d.point((x, y + 2), fill=hi)
    for x in range(x0 + 16, x1, 32):
        d.line([(x, y + 2), (x, y + 5)], fill=iron)
    d.line([(x0, y + 6), (x1, y + 6)], fill=hx("0c0e14"))
    # knee brackets bolted to the wall in the piers, each strut leaning away from the ladder
    for bx in BALCONY_BRACKETS:
        s = -1 if bx < 336 else 1
        d.line([(bx, y + 6), (bx, y + 30)], fill=iron, width=2)
        d.line([(bx + 8 * s, y + 6), (bx, y + 28)], fill=hx("2a303a"), width=2)
        d.line([(bx + 7 * s, y + 6), (bx, y + 6)], fill=iron, width=2)
        d.rectangle([bx - 2, y + 26, bx + 2, y + 31], fill=mid)
        for by in (y + 8, y + 29):
            d.point((bx, by), fill=hi)
    # the drop ladder: goosenecks over the kick plate, rails and round rungs, guide clamps
    bottom = 196 if freed else 156
    for x in (329, 345):
        d.line([(x, 86), (x, bottom)], fill=iron, width=3)
        d.line([(x - 1, 86), (x - 1, bottom)], fill=edge)
        d.arc([x - 1, 82, x + 5, 90], 180, 360, fill=iron, width=2)
        d.point((x, 83), fill=hi)
        d.rectangle([x - 2, 120, x + 2, 124], fill=hx("444c58"))
        d.line([(x - 2, 120), (x + 2, 120)], fill=hi)
        d.point((x, 122), fill=iron)
        d.rectangle([x - 2, bottom - 2, x + 2, bottom], fill=iron)
        d.line([(x - 1, bottom - 2), (x + 1, bottom - 2)], fill=edge)
    for ry in range(112, bottom, 8):
        d.line([(330, ry), (344, ry)], fill=hx("161c24"), width=3)
        d.line([(330, ry - 1), (344, ry - 1)], fill=hi)
        d.line([(331, ry + 1), (343, ry + 1)], fill=hx("0c0e14"))
        for x in (329, 345):
            d.point((x, ry), fill=edge)
    if not freed:  # the lower flight, slid up behind the upper one
        for x in (332, 342):
            d.line([(x, 111), (x, 154)], fill=hx("404854"))
        for ry in range(116, 154, 8):
            d.line([(333, ry), (341, ry)], fill=hx("2a303a"))


def trash_can(img, d, fire=False):
    """A galvanised can at the corner, ribbed, with drop handles, a dent and rust runs; newspapers and packing straw
    stuffed in under a lid knocked askew. Once it's burning, the lid lies on the cobbles."""
    x0, x1, top, bot = 40, 66, 177, 206
    for x in range(x0, x1 + 1):
        u = (x - x0) / (x1 - x0)
        f = 0.5 + 0.5 * math.cos((u - 0.32) * math.pi * 1.1)
        d.line([(x, top), (x, bot)], fill=mix(hx("24262a"), hx("8c9096"), max(0.0, min(1.0, f))))
    d.line([(x0, top), (x0, bot)], fill=hx("1a1a1e"))
    d.line([(x1, top), (x1, bot)], fill=hx("1a1a1e"))
    for ry in (185, 195):
        d.line([(x0 + 1, ry - 1), (x1 - 1, ry - 1)], fill=hx("6a6e74"))
        d.line([(x0 + 1, ry), (x1 - 1, ry)], fill=hx("a4a8ae"))
        d.line([(x0 + 1, ry + 1), (x1 - 1, ry + 1)], fill=hx("2e3034"))
    d.rectangle([x0, bot - 2, x1, bot], fill=hx("2a2c30"))
    d.rectangle([x0, top, x1, top + 1], fill=hx("9a9ea4"))
    for hx0, a0, a1 in ((x0 - 4, 90, 270), (x1 - 1, 270, 90)):
        d.arc([hx0, 179, hx0 + 5, 187], a0, a1, fill=hx("7a7e84"), width=1)
    d.ellipse([55, 198, 61, 203], fill=hx("4a4c52"))
    d.arc([55, 198, 61, 203], 200, 330, fill=hx("2a2c30"))
    d.arc([55, 198, 61, 203], 20, 150, fill=hx("a4a8ae"))
    for rx, ry, ln in ((46, 186, 6), (61, 196, 5), (50, 196, 3)):
        d.line([(rx, ry), (rx, ry + ln)], fill=hx("6a4a30"))
        d.point((rx + 1, ry + 1), fill=hx("8a5a34"))
    # the contents: straw, then the newspapers, folded and crumpled (burnt away once the can's alight)
    rnd = random.Random(45)
    paper, paper_d, ink = hx("d0c8b0"), hx("9a9480"), hx("6a6658")
    for _ in range(9 if not fire else 0):
        sx = rnd.randint(43, 63)
        d.line([(sx, top), (sx + rnd.randint(-5, 5), top - rnd.randint(4, 10))],
               fill=rnd.choice([hx("c8a860"), hx("a08040"), hx("dcc078")]))
    if fire:
        lx, ly = 70, 203  # the lid, knocked off onto the cobbles
        d.ellipse([lx, ly, lx + 22, ly + 8], fill=hx("4a4c50"), outline=hx("1a1a1e"))
        d.ellipse([lx + 3, ly + 1, lx + 19, ly + 6], fill=hx("6a6c72"))
        d.arc([lx + 8, ly + 2, lx + 14, ly + 6], 180, 360, fill=hx("1a1a1e"))
    else:
        # a folded broadsheet, masthead and columns, a second one crumpled beside it, a wrapper behind
        d.polygon([(38, top - 1), (42, 168), (46, 170), (44, top)], fill=hx("b8b098"))
        d.polygon([(43, top), (45, 161), (56, 159), (58, top)], fill=paper)
        d.rectangle([46, 162, 55, 164], fill=hx("2a2826"))
        d.rectangle([47, 167, 50, 170], fill=paper_d)
        for ly in range(166, top - 1, 2):
            d.line([(52, ly), (56, ly)], fill=ink)
            if ly > 171:
                d.line([(46, ly), (50, ly)], fill=ink)
        d.line([(51, 165), (51, top)], fill=paper_d)
        d.polygon([(54, top), (59, 163), (67, 166), (64, top)], fill=hx("e0d8c0"))
        for k in range(4):
            d.line([(59 + k, 168 + 2 * k), (64 + k // 2, 169 + 2 * k)], fill=ink)
        d.line([(59, 163), (54, top)], fill=paper_d)
        # the lid, propped on the papers at the back and resting on the rim at the front
        d.polygon([(36, 174), (69, 174), (69, 178), (36, 178)], fill=hx("5a5c60"), outline=hx("1a1a1e"))
        d.line([(37, 175), (68, 175)], fill=hx("8a8e94"))
        d.rectangle([49, 172, 56, 173], fill=hx("1a1a1e"))
        d.line([(50, 172), (55, 172)], fill=hx("8a8e94"))
    # a stray sheet blown onto the cobbles
    d.polygon([(96, 214), (110, 210), (116, 215), (102, 219)], fill=hx("bab29a"))
    d.line([(102, 219), (110, 210)], fill=paper_d)
    for k in range(3):
        d.line([(100 + 2 * k, 214 + k), (105 + 2 * k, 212 + k)], fill=ink)


FIRE_FRAMES = 8  # the flames and smoke loop, played by LoopStrip
FIRE_BOX = (24, 54, 82, 178)  # everything that moves stays inside this box; the glow around it is still


def _wave(t, k=1, phase=0.0):
    """A sine that loops exactly once every k cycles of t in [0, 1)."""
    return math.sin(2 * math.pi * (k * t + phase))


def trash_fire(img, t=0.0):
    """The burning trash can at phase t in [0, 1): licking flames, sparks and a column of smoke that rises one puff
    spacing per loop, so the frames repeat seamlessly."""
    light(img, "ellipse", [14, 125, 96, 218], hx("dc6020"), 0.24, 14)
    light(img, "ellipse", [22, 201, 86, 236], hx("e89438"), 0.16, 8)
    smoke = Image.new("RGBA", img.size)
    sd = ImageDraw.Draw(smoke)
    puffs = 12
    for k in reversed(range(puffs)):
        s = (k + t) / puffs  # 0 at the can's mouth, 1 where the smoke thins out
        cy = 148 - s * 84
        cx = 53 - s * 13 + 3 * math.sin(s * 6.5)
        r = 3.5 + s * 7
        fade = min(1.0, s / 0.1) * (1 - s) ** 0.8
        opacity = int(120 * fade)
        if opacity < 6:
            continue
        for dx, dy, rr in ((-0.45, 0.2, 0.75), (0.5, 0.1, 0.7), (0.0, -0.25, 0.85)):  # three lobes, a billow
            x, y, q = cx + dx * r, cy + dy * r, r * rr
            sd.ellipse([x - q, y - q * 0.85, x + q, y + q * 0.85], fill=hx("4a4852", opacity))
        sd.ellipse([cx - r * 0.7, cy - r * 0.8, cx + r * 0.1, cy - r * 0.15], fill=hx("6e6a74", opacity // 2))
    smoke = smoke.filter(ImageFilter.GaussianBlur(1.4))
    img.paste(smoke, (0, 0), smoke)
    d = ImageDraw.Draw(img)
    d.ellipse([40, 165, 67, 176], fill=hx("251a14"))
    for i, (x, top, drift) in enumerate(((42, 148, -3), (48, 138, 2), (55, 143, -2), (61, 150, 3))):
        top = round(top + 4 * _wave(t, 2, i * 0.37) + 2 * _wave(t, 3, i * 0.21))
        drift = round(drift + 2 * _wave(t, 1, i * 0.29))
        sway = round(_wave(t, 2, i * 0.5 + 0.25))
        d.polygon([(x - 4, 173), (x - 5 + sway, 160), (x - 1 + sway, 153), (x + drift, top),
                   (x + drift + 3, top + 9), (x + 2 + sway, 158), (x + 5, 168), (x + 3, 174)], fill=hx("be3d12"))
        d.polygon([(x - 3, 172), (x - 2 + sway, 163), (x + 1 + sway, 157), (x + drift + 1, top + 5),
                   (x + 4 + sway, 160), (x + 3, 170)], fill=hx("f88a20"))
        core = round(2 * _wave(t, 2, i * 0.41))
        d.polygon([(x - 2, 172), (x - 1, 162 + core), (x + 1, 158 + core), (x + 3, 165 + core),
                   (x + 4, 172)], fill=hx("ffe8a0"))
    # a lick of flame that breaks off and dies as it rises
    s = t % 1.0
    if s < 0.6:
        fy = round(140 - s * 30)
        fx = round(50 + 4 * _wave(t, 1, 0.1))
        d.polygon([(fx - 1, fy + 4), (fx, fy), (fx + 2, fy + 4)], fill=hx("f88a20") if s < 0.35 else hx("be3d12"))
    d.line([(40, 176), (66, 176)], fill=hx("d8a460"))
    rnd = random.Random(61)
    for j in range(6):
        s = (j / 6 + t) % 1.0
        x = rnd.randint(42, 63) + round(3 * math.sin(s * 6 + j))
        y = round(150 - s * 46)
        d.line([(x, y), (x + 1, y - 2)], fill=hx("ffc868") if s < 0.6 else hx("e26018"))
    for x0, y, x1 in ((38, 209, 65), (34, 216, 72), (42, 224, 61)):
        d.line([(x0, y), (x1, y)], fill=hx("946044"))


def paint_road(fire=False, stacked=False, freed=False, t=0.0):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 60), hx("0a0c1c"), hx("1a1c34"))
    rnd = random.Random(41)
    for _ in range(26):
        d.point((rnd.randint(0, 120), rnd.randint(0, 50)), fill=hx("8a90b0"))
    # A full-height ground floor and one accessible office floor above.
    bricks(img, (130, 0, W - 1, 200), hx("3a2a2a"), hx("221818"), 42, 5, 14)
    # a lower warehouse wall on the left, beyond the street mouth
    bricks(img, (0, 70, 128, 200), hx("33302e"), hx("1e1c1a"), 43, 5, 12)
    d.rectangle([0, 64, 128, 70], fill=hx("4a4642"))
    d.line([(0, 64), (128, 64)], fill=hx("6a6660"))
    d.line([(0, 70), (128, 70)], fill=hx("1a1816"))
    # a stone string course between the floors, and a plinth along the foot of the wall
    d.rectangle([130, 106, W - 1, 111], fill=hx("564a42"))
    d.line([(130, 106), (W - 1, 106)], fill=hx("7a6c60"))
    d.line([(130, 111), (W - 1, 111)], fill=hx("1e1616"))
    for jx in range(134, W, 19):
        d.line([(jx, 107), (jx, 110)], fill=hx("3e342e"))
    d.rectangle([130, 196, W - 1, 199], fill=hx("2e2624"))
    d.line([(130, 196), (W - 1, 196)], fill=hx("4a3e38"))
    # the painted-out ghost of the firm's name along the top of the wall
    text(img, (270, 10), "HARRINGTON STEEL", hx("5a4a40"), 8)
    # every office window alike, both floors, dark at this hour; the door takes the first bay on the ground floor
    for x in ROAD_WINDOW_COLS:
        road_window(d, x, ROAD_WINDOW[1])
        if x != ROAD_WINDOW_COLS[0]:
            road_window(d, x, ROAD_GROUND_Y)
    # the drainpipe, with its brackets and a hopper head under the gutter
    d.line([(392, 0), (392, 198)], fill=hx("16161c"), width=3)
    d.line([(391, 0), (391, 198)], fill=hx("4a4248"))
    d.rectangle([388, 2, 396, 8], fill=hx("16161c"))
    d.line([(388, 2), (396, 2)], fill=hx("4a4248"))
    for by in range(20, 198, 30):
        d.rectangle([389, by, 395, by + 1], fill=hx("26242a"))
    d.polygon([(389, 193), (395, 193), (398, 198), (392, 198)], fill=hx("16161c"))
    fire_escape(d, freed)
    # back door, a bare bulb over it
    d.rectangle([156, 118, 194, 200], fill=hx("2a2620"))
    d.rectangle([160, 122, 190, 200], fill=hx("4a3a28"))
    d.rectangle([162, 124, 188, 156], outline=hx("2a2016"))
    d.rectangle([162, 162, 188, 196], outline=hx("2a2016"))
    d.ellipse([184, 160, 187, 163], fill=hx("b89a50"))
    d.rectangle([172, 104, 178, 110], fill=hx("201c18"))
    d.ellipse([171, 109, 179, 117], fill=hx("fff0b0"))
    # cobbles, wet
    vgrad(img, (0, 200, W - 1, H - 1), hx("1c1e26"), hx("2c2e36"))
    for y in range(204, H, 7):
        off = (y // 7 % 2) * 6
        for x in range(-off, W, 12):
            d.arc([x, y, x + 11, y + 6], 180, 360, fill=hx("3a3c46"))
    noise(img, (0, 200, W - 1, H - 1), 6, 44)
    for x0, y, x1 in ((16, 232, 96), (256, 246, 302), (374, 225, 456)):
        d.line([(x0, y), (x1, y)], fill=hx("424656"))
        d.line([(x0 + 8, y + 2), (x1 - 6, y + 2)], fill=hx("323644"))
    d.line([(0, 200), (W, 200)], fill=hx("12121a"))
    # trash can at the street corner
    trash_can(img, d, fire)
    # the crates: by the wall on the right, or stacked under the ladder
    if stacked:
        crate(d, 320, 174, seed=3)
        crate(d, 322, 152, 22, seed=4)
    else:
        crate(d, 420, 176, seed=3)
        crate(d, 447, 182, 20, seed=4)
    # night and the bulb's pool of light over the door
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, (120, 128, 176))))
    light(img, "polygon", [(170, 112), (180, 112), (232, 230), (118, 230)], hx("e8c070"), 0.5, 12)
    light(img, "ellipse", [162, 98, 188, 124], hx("fff0b0"), 0.8, 4)
    if fire:
        trash_fire(img, t)
    vignette(img, 0.55, (8, 8, 24), 40)
    return img


def road_palette(base, fire, stacked):
    blend = Image.blend(Image.blend(base, fire, 0.5), stacked, 0.5)
    return palette_of(blend, 108) + [hx(c) for c in (
        "be3d12", "f88a20", "ffe8a0", "ffc868", "d8a460", "e26018", "946044", "edb048",
        "30313a", "464650", "5a5860", "26262e")]


def fire_strip(pal):
    """The flames and smoke as a horizontal strip of FIRE_FRAMES crops of FIRE_BOX, frame 0 matching the fire overlay."""
    x0, y0, x1, y1 = FIRE_BOX
    strip = Image.new("RGB", ((x1 - x0) * FIRE_FRAMES, y1 - y0))
    for i in range(FIRE_FRAMES):
        frame = pixelize(paint_road(fire=True, t=i / FIRE_FRAMES), pal).crop(FIRE_BOX)
        strip.paste(frame, ((x1 - x0) * i, 0))
    return strip


def build_road():
    base = paint_road()
    variants = paint_road(fire=True), paint_road(stacked=True)
    pal = road_palette(base, *variants)
    px = pixelize(base, pal)
    save(px, "rooms", "harrington_road.png")
    overlay(variants[0], px, pal, (0, 0, W, H), "harrington_road_fire")
    save(fire_strip(pal), "rooms", "harrington_road_flames.png")
    print("harrington_road_flames at", FIRE_BOX[:2], FIRE_FRAMES, "frames")
    overlay(variants[1], px, pal, (300, 120, 476, 212), "harrington_road_crates")
    overlay(paint_road(stacked=True, freed=True), pixelize(variants[1], pal), pal,
            (300, 100, 400, 210), "harrington_road_ladder")
    return px


def _daub(img, shape, pts, col, k=1.0, blur=0, clip=None):
    """Normal-blends a flat colour through a (soft) mask - a brush stroke for the supersampled portrait."""
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    getattr(d, shape)(pts, fill=int(255 * k)) if shape != "line" else d.line(pts[0], fill=int(255 * k), width=pts[1])
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    if clip is not None:
        m = ImageChops.multiply(m, clip)
    img.paste(Image.composite(Image.new("RGB", img.size, col), img, m))


HERALDRY = (("raven", "star"), ("lion", "sun"), ("stag", "moon"))  # the false back's key, in procession order
HERALD_GROUND, HERALD_GILT = hx("1e1510"), hx("b08a3a")
HERALD_BEAST, HERALD_SKY = hx("d4a848"), hx("f2e8c8")


BEAST_SS = 8  # beasts are drawn this many times larger, then reduced, so their outlines stay smooth when small


def _beast(img, kind, box, col):
    """A heraldic beast facing right in box (x, y, w, h), drawn like an engraved gold charge: a smooth silhouette,
    darker engraved lines for feathers, mane and muscle, and a pale catch-light along the top edges. The raven is
    close (wings folded), the lion walking on all four paws with its tail curled over its back, the stag trippant with a branched
    rack of antlers."""
    bx, by, bw, bh = box
    W, H = max(1, round(bw)), max(1, round(bh))
    S = BEAST_SS
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    P = lambda u, v: (u * W * S, v * H * S)
    pts = lambda *uv: [P(u, v) for u, v in uv]
    k = W * S / 100  # stroke widths are in hundredths of the box
    body, shade = col + (255,), mul(col, 0.58) + (255,)
    dark = HERALD_GROUND + (255,)
    light = tuple(round(c + (255 - c) * 0.55) for c in col) + (255,)
    face = tuple(round(c + (255 - c) * 0.2) for c in col) + (255,)
    mane = mul(col, 0.78) + (255,)

    def limb(path, width, fill=body):
        d.line(pts(*path), fill=fill, width=max(1, round(width * k)), joint="curve")
        for u, v in (path[0], path[-1]):
            r = width * k / 2
            x, y = P(u, v)
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def line(path, width, fill=shade):
        d.line(pts(*path), fill=fill, width=max(1, round(width * k)), joint="curve")

    def dot(u, v, r, fill):
        x, y = P(u, v)
        d.ellipse([x - r * k, y - r * k, x + r * k, y + r * k], fill=fill)

    if kind == "raven":
        for leg in (((0.5, 0.7), (0.49, 0.83), (0.47, 0.92)), ((0.58, 0.68), (0.6, 0.82), (0.6, 0.92))):
            limb(leg, 3.2, shade)
            x = leg[-1][0]
            for toe in ((x - 0.09, 0.95), (x + 0.08, 0.95), (x + 0.02, 0.97)):
                limb((leg[-1], toe), 2.2, shade)
        d.polygon(pts((0.0, 0.84), (0.08, 0.7), (0.22, 0.6), (0.34, 0.47), (0.46, 0.38), (0.56, 0.3),
                      (0.62, 0.2), (0.7, 0.14), (0.78, 0.14), (0.84, 0.18), (0.89, 0.2), (1.0, 0.27),
                      (0.88, 0.3), (0.8, 0.33), (0.79, 0.39), (0.74, 0.4), (0.77, 0.45), (0.71, 0.47),
                      (0.74, 0.53), (0.72, 0.62), (0.66, 0.7), (0.54, 0.75), (0.4, 0.75), (0.3, 0.76),
                      (0.18, 0.84), (0.12, 0.9), (0.04, 0.92)), fill=body)
        # the folded wing: a dark outline from the shoulder, scalloped coverts, long primaries to the tail
        line(((0.62, 0.34), (0.5, 0.36), (0.36, 0.48), (0.22, 0.64), (0.1, 0.8)), 2.2)
        line(((0.66, 0.42), (0.64, 0.56), (0.54, 0.68), (0.36, 0.72), (0.2, 0.78)), 2.2)
        for i in range(4):
            t = i / 3
            u0, v0 = 0.6 - 0.12 * t, 0.42 + 0.08 * t
            line(((u0, v0), (u0 - 0.06, v0 + 0.05), (u0 - 0.12, v0 + 0.04)), 1.6)
        for i in range(4):
            t = i / 3
            line(((0.52 - 0.04 * t, 0.56 + 0.04 * t), (0.14 + 0.02 * t, 0.8 + 0.02 * t)), 1.4)
        for i in range(3):  # tail feathers
            line(((0.22, 0.78), (0.02 + 0.04 * i, 0.86 + 0.02 * i)), 1.2)
        line(((0.84, 0.25), (0.97, 0.27)), 1.2, dark)  # the split of the beak
        line(((0.86, 0.18), (0.97, 0.26)), 1.4, light)
        line(((0.58, 0.24), (0.66, 0.16), (0.76, 0.14)), 1.6, light)
        line(((0.3, 0.5), (0.44, 0.39), (0.54, 0.32)), 1.6, light)
        dot(0.76, 0.22, 3.0, dark)
        dot(0.765, 0.21, 1.0, light)
    elif kind == "lion":
        # the tail, curled up over the back and ending in a tuft
        limb(((0.2, 0.44), (0.1, 0.4), (0.06, 0.28), (0.1, 0.16), (0.2, 0.12)), 3.6)
        d.polygon(pts((0.17, 0.14), (0.22, 0.04), (0.25, 0.1), (0.31, 0.06), (0.29, 0.14), (0.34, 0.16),
                      (0.25, 0.19)), fill=body)
        # far legs, in shade behind the body
        limb(((0.27, 0.56), (0.3, 0.72), (0.28, 0.9)), 5.6, shade)
        limb(((0.55, 0.56), (0.58, 0.74), (0.6, 0.9)), 5.4, shade)
        # body and near legs
        d.ellipse([*P(0.12, 0.36), *P(0.4, 0.66)], fill=body)
        d.polygon(pts((0.22, 0.38), (0.42, 0.36), (0.6, 0.32), (0.68, 0.46), (0.64, 0.62), (0.46, 0.6),
                      (0.3, 0.62)), fill=body)
        limb(((0.2, 0.52), (0.15, 0.68), (0.18, 0.8), (0.14, 0.9)), 6.6)
        limb(((0.62, 0.56), (0.65, 0.74), (0.66, 0.9)), 6.2)
        for u, v, f in ((0.14, 0.9, body), (0.66, 0.9, body), (0.28, 0.9, shade), (0.6, 0.9, shade)):
            d.ellipse([*P(u - 0.045, v - 0.03), *P(u + 0.06, v + 0.045)], fill=f)
        # the mane: a ring of flame-shaped locks around the head
        cx, cy = 0.74, 0.3
        locks = []
        for i in range(22):
            a = math.pi * 2 * i / 22
            r = 0.25 if i % 2 == 0 else 0.18
            locks.append((cx - 0.02 + r * math.cos(a), cy + 0.02 + r * math.sin(a) * 1.1))
        d.polygon(pts(*locks), fill=mane)
        for i in range(9):
            a = math.pi * 2 * (i + 0.5) / 9
            line(((cx - 0.02 + 0.12 * math.cos(a), cy + 0.02 + 0.13 * math.sin(a)),
                  (cx - 0.02 + 0.21 * math.cos(a + 0.18), cy + 0.02 + 0.23 * math.sin(a + 0.18))), 1.4, shade)
        # the face, turned to the right
        d.polygon(pts((0.72, 0.18), (0.82, 0.17), (0.88, 0.22), (0.95, 0.28), (0.96, 0.35), (0.9, 0.38),
                      (0.88, 0.43), (0.8, 0.44), (0.74, 0.38), (0.7, 0.28)), fill=body)
        line(((0.72, 0.18), (0.7, 0.28), (0.74, 0.38), (0.8, 0.44), (0.88, 0.43)), 1.4)
        line(((0.8, 0.2), (0.88, 0.22), (0.95, 0.28)), 1.4, face)
        line(((0.82, 0.25), (0.89, 0.26)), 1.6, dark)  # brow
        dot(0.85, 0.28, 2.2, dark)
        dot(0.95, 0.31, 1.8, dark)  # nose
        line(((0.95, 0.35), (0.9, 0.37), (0.85, 0.37)), 1.4, dark)  # mouth
        line(((0.88, 0.4), (0.84, 0.42)), 1.0, shade)
        # muscle and a highlight along the back
        line(((0.18, 0.46), (0.24, 0.56), (0.22, 0.62)), 1.6)
        line(((0.6, 0.42), (0.64, 0.54)), 1.6)
        line(((0.4, 0.58), (0.5, 0.6)), 1.2)
        line(((0.2, 0.39), (0.36, 0.37), (0.54, 0.33)), 1.6, light)
        for u in (0.12, 0.16, 0.64, 0.68):
            v = 0.93
            line(((u, v - 0.03), (u, v)), 0.9, dark)  # claws
    else:  # stag
        # far legs in shade
        limb(((0.28, 0.58), (0.3, 0.72), (0.27, 0.84), (0.28, 0.93)), 3.4, shade)
        limb(((0.6, 0.58), (0.61, 0.76), (0.62, 0.93)), 3.2, shade)
        # body and neck
        d.ellipse([*P(0.12, 0.42), *P(0.34, 0.64)], fill=body)
        d.polygon(pts((0.2, 0.43), (0.4, 0.44), (0.56, 0.42), (0.6, 0.36), (0.64, 0.28), (0.72, 0.28),
                      (0.72, 0.36), (0.69, 0.5), (0.67, 0.6), (0.5, 0.64), (0.3, 0.63)), fill=body)
        limb(((0.18, 0.52), (0.14, 0.68), (0.19, 0.8), (0.17, 0.93)), 4.6)
        limb(((0.63, 0.56), (0.7, 0.66), (0.67, 0.77), (0.7, 0.8)), 3.6)  # the raised foreleg, bent at the knee
        limb(((0.56, 0.58), (0.55, 0.76), (0.55, 0.93)), 3.8)
        for u, v in ((0.17, 0.94), (0.55, 0.94), (0.28, 0.94), (0.62, 0.94), (0.7, 0.81)):
            dot(u, v, 2.4, dark)  # hooves
        d.polygon(pts((0.13, 0.46), (0.07, 0.43), (0.09, 0.5)), fill=light)  # the white scut
        # head, ears and the rack
        d.polygon(pts((0.63, 0.3), (0.66, 0.24), (0.72, 0.22), (0.8, 0.26), (0.9, 0.31), (0.92, 0.35),
                      (0.86, 0.37), (0.76, 0.36), (0.71, 0.36)), fill=body)
        d.polygon(pts((0.66, 0.25), (0.58, 0.2), (0.6, 0.18), (0.69, 0.23)), fill=shade)
        dot(0.9, 0.33, 1.6, dark)
        dot(0.77, 0.28, 2.0, dark)
        dot(0.775, 0.275, 0.7, light)
        for ox, fill, w in ((0.66, shade, 2.0), (0.72, body, 2.4)):
            limb(((ox, 0.24), (ox - 0.02, 0.16), (ox + 0.02, 0.08), (ox + 0.0, 0.01)), w, fill)  # main beam
            limb(((ox - 0.015, 0.19), (ox + 0.07, 0.15)), w * 0.75, fill)  # brow tine
            limb(((ox - 0.01, 0.13), (ox + 0.06, 0.09)), w * 0.75, fill)
            limb(((ox + 0.015, 0.07), (ox + 0.07, 0.03)), w * 0.75, fill)
        # chest, haunch and a highlight along the back
        line(((0.68, 0.38), (0.67, 0.5)), 1.4)
        line(((0.2, 0.47), (0.26, 0.56), (0.24, 0.62)), 1.4)
        line(((0.22, 0.44), (0.4, 0.45), (0.56, 0.43)), 1.4, light)
        line(((0.68, 0.24), (0.8, 0.27), (0.9, 0.315)), 1.2, light)
    small = layer.resize((W, H), Image.LANCZOS)
    img.paste(small.convert("RGB"), (round(bx), round(by)), small.getchannel("A"))


def _sky(d, kind, box, col, ground):
    """A star, sun or moon centred in box (x, y, w, h)."""
    bx, by, bw, bh = box
    s = min(bw, bh)
    cx, cy = bx + bw / 2, by + bh / 2
    if kind == "star":
        pts = []
        for i in range(10):
            r = s * (0.48 if i % 2 == 0 else 0.2)
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        d.polygon(pts, fill=col)
    elif kind == "sun":
        for i in range(12):
            a = i * math.pi / 6
            w = 0.26 if i % 2 else 0.18
            d.polygon([(cx + s * 0.48 * math.cos(a), cy + s * 0.48 * math.sin(a)),
                       (cx + s * 0.22 * math.cos(a + w), cy + s * 0.22 * math.sin(a + w)),
                       (cx + s * 0.22 * math.cos(a - w), cy + s * 0.22 * math.sin(a - w))], fill=col)
        r = s * 0.26
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    else:
        r = s * 0.42
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
        o = s * 0.2
        d.ellipse([cx - r + o, cy - r - o * 0.4, cx + r + o, cy + r - o * 0.4], fill=ground)


def heraldry(img, box):
    """The heraldic key painted along the bottom of Harrington's portrait: three compartments, each a gold beast
    and the pale sign it stands for - raven and star, lion and sun, stag and moon. Scales to any box, so the same
    band is painted into the portrait and blown up for its close-up."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=HERALD_GROUND)
    edge = max(1, round(h * 0.06))
    d.rectangle([x0, y0, x1, y0 + edge - 1], fill=HERALD_GILT)
    d.rectangle([x0, y1 - edge + 1, x1, y1], fill=HERALD_GILT)
    cw = w / 3
    for i, (beast, sign) in enumerate(HERALDRY):
        cx0 = x0 + i * cw
        if i:
            d.rectangle([cx0 - edge // 2, y0, cx0 + (edge - 1) // 2, y1], fill=HERALD_GILT)
        inner_h = h - 4 * edge
        size = min(inner_h, cw * 0.6)  # the beast is the charge; its sign sits smaller beside it
        sky = min(size * 0.55, cw * 0.3)
        gap = (cw - size - sky) / 3
        top = y0 + (h - size) / 2
        _beast(img, beast, (cx0 + gap, top, size, size), HERALD_BEAST)
        _sky(d, sign, (cx0 + 2 * gap + size, y0 + (h - sky) / 2, sky, sky), HERALD_SKY, HERALD_GROUND)


PORTRAIT_BAND = 0.18  # the heraldry's share of the portrait's height, along the bottom


def harrington_portrait(w, h):
    """Oil portrait of Theodore Harrington Sr.: an old patrician in three-quarter view, bald crown with white hair
    at the temples, heavy white brows, deep-set pale eyes and a hard mouth, in evening dress with a wing collar.
    The heraldic key runs along the bottom. Painted at 4x and scaled down so the shading stays soft under the
    room's pixelization."""
    S = 4
    W4, H4 = w * S, h * S
    img = Image.new("RGB", (W4, H4))
    vgrad(img, (0, 0, W4 - 1, H4 - 1), hx("4a3a26"), hx("1c140c"))
    _daub(img, "ellipse", [W4 * 0.05, H4 * 0.02, W4 * 0.95, H4 * 0.8], hx("6a5434"), 0.6, 30)  # glow behind the head
    cx, cy = W4 * 0.5, H4 * 0.38  # face centre
    fw, fh = W4 * 0.235, H4 * 0.235
    # coat and shoulders
    _daub(img, "polygon", [(-10, H4), (W4 * 0.06, H4 * 0.74), (W4 * 0.3, H4 * 0.64), (W4 * 0.7, H4 * 0.64),
                           (W4 * 0.94, H4 * 0.74), (W4 + 10, H4)], hx("15121a"), 1, 2)
    _daub(img, "polygon", [(W4 * 0.1, H4 * 0.78), (W4 * 0.3, H4 * 0.66), (W4 * 0.36, H4 * 0.72), (W4 * 0.2, H4)],
          hx("3a3644"), 0.7, 6)  # light on the near shoulder
    # shirt front, wing collar, bow tie, satin lapels
    _daub(img, "polygon", [(cx - W4 * 0.12, H4 * 0.66), (cx + W4 * 0.1, H4 * 0.66), (cx + W4 * 0.05, H4),
                           (cx - W4 * 0.07, H4)], hx("e8e2d4"), 1, 1)
    _daub(img, "polygon", [(cx - W4 * 0.22, H4 * 0.66), (cx - W4 * 0.08, H4 * 0.7), (cx - W4 * 0.07, H4),
                           (cx - W4 * 0.2, H4)], hx("2a2632"), 1, 1)
    _daub(img, "polygon", [(cx + W4 * 0.18, H4 * 0.66), (cx + W4 * 0.07, H4 * 0.7), (cx + W4 * 0.05, H4),
                           (cx + W4 * 0.18, H4)], hx("221e28"), 1, 1)
    for s in (-1, 1):
        _daub(img, "polygon", [(cx - W4 * 0.01, H4 * 0.66), (cx + s * W4 * 0.1, H4 * 0.64), (cx + s * W4 * 0.07, H4 * 0.7)],
              hx("f4f0e6"), 1, 1)
        _daub(img, "polygon", [(cx - W4 * 0.01, H4 * 0.69), (cx + s * W4 * 0.08, H4 * 0.66), (cx + s * W4 * 0.08, H4 * 0.73)],
              hx("0c0a0e"), 1, 1)
    _daub(img, "ellipse", [cx - W4 * 0.03, H4 * 0.675, cx + W4 * 0.01, H4 * 0.71], hx("0c0a0e"), 1, 1)
    # neck, with the loose skin of age
    _daub(img, "polygon", [(cx - fw * 0.62, cy + fh * 0.5), (cx + fw * 0.55, cy + fh * 0.5), (cx + fw * 0.5, H4 * 0.68),
                           (cx - fw * 0.55, H4 * 0.68)], hx("b88c70"), 1, 2)
    _daub(img, "polygon", [(cx + fw * 0.1, cy + fh * 0.6), (cx + fw * 0.55, cy + fh * 0.5), (cx + fw * 0.5, H4 * 0.68),
                           (cx + fw * 0.1, H4 * 0.68)], hx("8a6450"), 0.7, 4)
    # the head: skull and jowls, then light from the upper left and shadow on the far side
    face = Image.new("L", img.size, 0)
    fd = ImageDraw.Draw(face)
    fd.ellipse([cx - fw, cy - fh * 1.08, cx + fw, cy + fh * 0.62], fill=255)
    fd.ellipse([cx - fw * 0.82, cy - fh * 0.2, cx + fw * 0.86, cy + fh * 0.86], fill=255)
    face = face.filter(ImageFilter.GaussianBlur(1.5))
    _daub(img, "rectangle", [0, 0, W4, H4], hx("d2a888"), 1, 0, face)
    _daub(img, "ellipse", [cx - fw * 1.1, cy - fh * 1.2, cx + fw * 0.3, cy + fh * 0.3], hx("f0d0b4"), 0.75, 12, face)
    _daub(img, "ellipse", [cx + fw * 0.35, cy - fh * 0.9, cx + fw * 1.4, cy + fh], hx("8a5e48"), 0.85, 14, face)
    _daub(img, "ellipse", [cx - fw * 0.7, cy + fh * 0.45, cx + fw * 0.9, cy + fh * 1.1], hx("9a6c54"), 0.55, 10, face)
    _daub(img, "ellipse", [cx - fw * 0.55, cy - fh * 1.0, cx + fw * 0.05, cy - fh * 0.6], hx("fff0dc"), 0.6, 8, face)  # bald dome
    for i in range(3):  # forehead lines
        y = cy - fh * (0.52 - i * 0.1)
        _daub(img, "line", ([(cx - fw * 0.55, y), (cx + fw * 0.3, y - 2)], 2), hx("a87a60"), 0.35, 1.5, face)
    # ear on the near (right) side and the white hair round the back of the head at the temples
    _daub(img, "ellipse", [cx + fw * 0.82, cy - fh * 0.2, cx + fw * 1.1, cy + fh * 0.32], hx("b07c64"), 1, 2)
    _daub(img, "ellipse", [cx + fw * 0.88, cy - fh * 0.1, cx + fw * 1.02, cy + fh * 0.2], hx("7a5040"), 0.6, 2)
    for x0, x1 in ((cx - fw * 1.08, cx - fw * 0.78), (cx + fw * 0.7, cx + fw * 1.08)):
        _daub(img, "ellipse", [x0, cy - fh * 0.62, x1, cy + fh * 0.05], hx("aaa69e"), 0.95, 4)
        _daub(img, "ellipse", [x0 + 2, cy - fh * 0.55, x1 - 2, cy - fh * 0.2], hx("ccc8c0"), 0.6, 3)
    # deep-set eyes under heavy white brows
    for s, ex in ((-1, cx - fw * 0.42), (1, cx + fw * 0.3)):
        ey = cy - fh * 0.12
        r = fw * (0.2 if s < 0 else 0.18)
        _daub(img, "ellipse", [ex - r * 1.5, ey - r * 1.1, ex + r * 1.5, ey + r * 1.1], hx("7a5040"), 0.7, 5)
        _daub(img, "ellipse", [ex - r, ey - r * 0.38, ex + r, ey + r * 0.42], hx("e4dccc"), 1, 1)
        _daub(img, "ellipse", [ex - r * 0.45 - 2, ey - r * 0.4, ex + r * 0.45 - 2, ey + r * 0.42], hx("5a7080"), 1, 0.5)
        _daub(img, "ellipse", [ex - r * 0.2 - 2, ey - r * 0.18, ex + r * 0.2 - 2, ey + r * 0.2], hx("141016"), 1, 0)
        _daub(img, "line", ([(ex - r * 1.05, ey - r * 0.32), (ex, ey - r * 0.55), (ex + r * 1.05, ey - r * 0.25)], 3),
              hx("6a4434"), 1, 0.8)  # heavy upper lid
        _daub(img, "line", ([(ex - r * 0.8, ey + r * 0.75), (ex + r * 0.9, ey + r * 0.7)], 2), hx("9a6a56"), 0.7, 1.5)
        _daub(img, "polygon", [(ex - r * 1.4, ey - r * 0.9), (ex - r * 0.2, ey - r * 1.55), (ex + r * 1.4, ey - r * 1.1),
                               (ex + r * 1.3, ey - r * 0.7), (ex - r * 1.2, ey - r * 0.55)], hx("9a948a"), 0.95, 1.5)
    # nose: a long aquiline nose with its shadow cast to the right
    nx = cx - fw * 0.08
    _daub(img, "polygon", [(nx - 3, cy - fh * 0.1), (nx + 6, cy - fh * 0.1), (nx + fw * 0.2, cy + fh * 0.3),
                           (nx + 2, cy + fh * 0.36), (nx - fw * 0.22, cy + fh * 0.3)], hx("c49478"), 1, 2)
    _daub(img, "polygon", [(nx + 6, cy - fh * 0.05), (nx + fw * 0.24, cy + fh * 0.3), (nx + fw * 0.1, cy + fh * 0.36)],
          hx("8a5a46"), 0.8, 3)
    _daub(img, "line", ([(nx - 1, cy - fh * 0.08), (nx - fw * 0.06, cy + fh * 0.26)], 3), hx("f4dcc4"), 0.8, 1.5)
    for dx in (-fw * 0.14, fw * 0.12):
        _daub(img, "ellipse", [nx + dx - 4, cy + fh * 0.3, nx + dx + 4, cy + fh * 0.36], hx("5a3428"), 0.9, 1)
    # nasolabial folds, a thin hard mouth turned down at the corners, the chin
    _daub(img, "line", ([(nx - fw * 0.26, cy + fh * 0.3), (cx - fw * 0.42, cy + fh * 0.62)], 3), hx("8a5e48"), 0.7, 2)
    _daub(img, "line", ([(nx + fw * 0.26, cy + fh * 0.3), (cx + fw * 0.36, cy + fh * 0.62)], 3), hx("7a5040"), 0.8, 2)
    my = cy + fh * 0.53
    _daub(img, "line", ([(cx - fw * 0.34, my + 3), (cx - fw * 0.1, my), (cx + fw * 0.2, my), (cx + fw * 0.32, my + 4)], 3),
          hx("5a2e28"), 1, 0.8)
    _daub(img, "line", ([(cx - fw * 0.22, my + 4), (cx + fw * 0.18, my + 4)], 2), hx("a8705c"), 0.6, 1.5)
    _daub(img, "ellipse", [cx - fw * 0.28, cy + fh * 0.7, cx + fw * 0.2, cy + fh * 0.84], hx("e8c4a4"), 0.5, 4)
    heraldry(img, (0, round(H4 * (1 - PORTRAIT_BAND)), W4 - 1, H4 - 1))
    noise(img, (0, 0, W4 - 1, H4 - 1), 5, 54)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------------------------------------ HARRINGTON'S OFFICE

def _bevel(d, box, hi, lo):
    """A one-pixel raised edge: light along the top and left, dark along the bottom and right."""
    x0, y0, x1, y1 = box
    d.line([(x0, y1), (x0, y0), (x1, y0)], fill=hi)
    d.line([(x0 + 1, y1), (x1, y1), (x1, y0 + 1)], fill=lo)


def _grain(d, box, col, seed, step=3):
    """Wavy vertical wood grain."""
    x0, y0, x1, y1 = box
    rnd = random.Random(seed)
    for x in range(x0 + 1, x1, step):
        x += rnd.randint(0, 1)
        pts = [(x + round(math.sin(y * 0.15 + x) * 0.8), y) for y in range(y0 + 1, y1, 3)]
        if len(pts) > 1:
            d.line(pts, fill=mul(col, rnd.uniform(0.82, 0.94)))


def filing_cabinet(img, d):
    """Four-drawer steel filing cabinet: label holders with typed cards, cup pulls, a lock at the top corner,
    the deep side in shadow, ledgers stacked on top."""
    body, edge = hx("54564e"), hx("1a1a18")
    d.rectangle([128, 120, 168, 200], fill=body, outline=edge)
    d.rectangle([162, 121, 167, 199], fill=hx("3c3d38"))  # the side, turned from the window
    d.line([(162, 121), (162, 199)], fill=hx("2a2b27"))
    d.rectangle([126, 117, 170, 121], fill=hx("6a6c64"), outline=edge)
    d.line([(127, 118), (169, 118)], fill=hx("8a8c84"))
    d.rectangle([129, 195, 161, 199], fill=hx("2c2d29"))
    for y in (124, 142, 160, 178):
        d.rectangle([131, y, 160, y + 16], fill=hx("4e5048"), outline=hx("26271f"))
        _bevel(d, (132, y + 1, 159, y + 15), hx("72746a"), hx("34352f"))
        d.rectangle([140, y + 3, 151, y + 7], fill=hx("8a7444"))
        d.rectangle([141, y + 4, 150, y + 6], fill=hx("dcd4bc"))
        d.line([(142, y + 5), (148, y + 5)], fill=hx("6a6458"))
        d.rectangle([141, y + 10, 150, y + 12], fill=hx("b4b09c"))
        d.line([(141, y + 13), (150, y + 13)], fill=hx("1e1e1a"))
        d.point((145, y + 11), fill=hx("e4e0cc"))
    d.ellipse([155, 125, 158, 128], fill=hx("b4a060"))
    d.point((156, 126), fill=hx("1a1a18"))
    # ledgers and a box file on top
    for i, (c, x0, x1) in enumerate((("5a2a20", 131, 155), ("2a3a4a", 132, 153), ("6a4a2a", 130, 156))):
        y = 114 - i * 3
        d.rectangle([x0, y, x1, y + 2], fill=hx(c), outline=hx("1a120c"))
        d.line([(x0 + 2, y + 1), (x1 - 2, y + 1)], fill=mul(hx(c), 1.5))
    d.rectangle([157, 108, 166, 116], fill=hx("b89a60"), outline=hx("3a2a14"))
    d.line([(158, 111), (165, 111)], fill=hx("6a5430"))


def _drawer_front(d, x0, y0, x1, y1, keyhole, col=hx("553620")):
    d.rectangle([x0, y0, x1, y1], fill=col, outline=hx("1e1209"))
    _bevel(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), mul(col, 1.35), mul(col, 0.6))
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], outline=mul(col, 0.75))
    mx = (x0 + x1) // 2
    my = y0 + (y1 - y0) // 2 - (2 if keyhole else 0)
    d.rectangle([mx - 5, my - 1, mx + 5, my + 1], fill=hx("6a5020"))  # brass backplate
    d.arc([mx - 4, my - 1, mx + 4, my + 5], 0, 180, fill=hx("e0c068"))  # the bail
    d.point((mx - 4, my), fill=hx("e0c068"))
    d.point((mx + 4, my), fill=hx("e0c068"))
    if keyhole:
        d.ellipse([mx - 2, my + 6, mx + 2, my + 10], fill=hx("b89a48"))
        d.rectangle([mx - 1, my + 7, mx, my + 9], fill=hx("0a0604"))


DESK_DROP = 14  # how far the desk top sits below where it was first painted: lowered to about Micah's belt


def desk(img, d, left, right):
    """A partners' desk in mahogany: moulded top, two panelled pedestals with a drawer over a cupboard in each, a
    kneehole between, a green leather blotter, a brass inkstand, a candlestick telephone and a lit banker's lamp."""
    wood, edge = hx("4e321c"), hx("1e1209")
    DROP = DESK_DROP
    # kneehole: the back panel in shadow, a shallow pencil drawer under the top
    d.rectangle([230, 164, 270, 204], fill=hx("24160a"))
    d.rectangle([232, 176, 268, 202], fill=hx("2e1c0e"), outline=hx("1a1006"))
    d.rectangle([230, 164, 270, 172], fill=hx("3e2814"), outline=edge)
    _bevel(d, (231, 165, 269, 171), hx("5a3a20"), hx("2a1a0c"))
    d.rectangle([248, 167, 252, 169], fill=hx("c8a858"))
    for x0 in (186, 270):
        d.rectangle([x0, 164, x0 + 44, 204], fill=wood)
        _grain(d, (x0 + 1, 165, x0 + 43, 203), wood, x0)
        d.line([(x0 + 1, 165), (x0 + 1, 203)], fill=hx("6a4628"))
        d.line([(x0 + 43, 165), (x0 + 43, 203)], fill=hx("341f0e"))
        d.rectangle([x0 + 1, 199, x0 + 43, 203], fill=hx("341f0e"))  # plinth
        d.line([(x0 + 1, 199), (x0 + 43, 199)], fill=hx("6a4628"))
        d.rectangle([x0, 164, x0 + 44, 204], outline=edge)
        # cupboard door with a raised panel and a little turned knob
        d.rectangle([x0 + 4, 188, x0 + 40, 197], fill=hx("4a2f1a"), outline=hx("2a1a0c"))
        _bevel(d, (x0 + 6, 190, x0 + 38, 195), hx("6e4a2c"), hx("2c1a0c"))
        d.rectangle([x0 + 9, 191, x0 + 31, 194], fill=hx("553620"))
        d.ellipse([x0 + 33, 191, x0 + 36, 194], fill=hx("c8a858"))
    for x0, opened in ((190, left), (274, right)):
        if opened:
            # pulled out towards the room: its insides, then a larger, lower front
            d.polygon([(x0, 167), (x0 + 36, 167), (x0 + 40, 173), (x0 - 4, 173)], fill=hx("2a1a0e"), outline=edge)
            d.line([(x0 - 3, 172), (x0 + 39, 172)], fill=hx("4a3018"))
            if x0 == 190:
                d.rectangle([x0 + 1, 168, x0 + 13, 172], fill=hx("7a2e1a"), outline=hx("2a0e06"))  # cigar box
                d.rectangle([x0 + 4, 169, x0 + 10, 170], fill=hx("e0c880"))
                d.line([(x0 + 15, 171), (x0 + 25, 169)], fill=hx("d0d0d8"))  # letter opener
                d.point((x0 + 15, 171), fill=hx("8a7a3a"))
                d.rectangle([x0 + 27, 168, x0 + 35, 172], fill=hx("9a5824"), outline=hx("3a1a08"))  # rye
                d.rectangle([x0 + 35, 169, x0 + 37, 171], fill=hx("3a2a1a"))
                d.line([(x0 + 28, 169), (x0 + 33, 169)], fill=hx("e8b060"))
            else:
                for i in range(3):  # bank drafts
                    d.rectangle([x0 + 1 + i, 168 + i // 2, x0 + 20 + i, 171], fill=hx("f0ead8"), outline=hx("8a8270"))
                d.line([(x0 + 4, 170), (x0 + 16, 170)], fill=hx("6a7a6a"))
                d.rectangle([x0 + 23, 168, x0 + 36, 172], fill=hx("141018"), outline=hx("c8a040"))  # the invitation
                d.point((x0 + 29, 170), fill=hx("e0c060"))
            _drawer_front(d, x0 - 4, 173, x0 + 40, 192, x0 == 274, hx("6a4628"))
        else:
            _drawer_front(d, x0, 167, x0 + 36, 186, x0 == 274)
    # the top: a moulded edge, the leather and the brass on it
    d.rectangle([180, 138 + DROP, 320, 150 + DROP], fill=hx("6a4426"), outline=edge)
    d.rectangle([181, 139 + DROP, 319, 143 + DROP], fill=hx("7a5232"))
    d.line([(181, 144 + DROP), (319, 144 + DROP)], fill=hx("a0703e"))
    d.line([(181, 148 + DROP), (319, 148 + DROP)], fill=hx("4a2c16"))
    d.rectangle([232, 139 + DROP, 270, 143 + DROP], fill=hx("2a4a32"), outline=hx("1a2a1a"))  # blotter
    for x in (232, 266):
        d.rectangle([x, 139 + DROP, x + 4, 143 + DROP], fill=hx("5a2a1a"))
    d.rectangle([241, 136 + DROP, 262, 139 + DROP], fill=hx("d8ccb0"))  # letters
    d.line([(244, 137 + DROP), (259, 137 + DROP)], fill=hx("6a6050"))
    d.rectangle([243, 135 + DROP, 258, 136 + DROP], fill=hx("ece4cc"))
    # brass inkstand with two wells and a pen
    d.rectangle([197, 140 + DROP, 215, 142 + DROP], fill=hx("a08838"), outline=hx("3a2a10"))
    for x in (200, 209):
        d.rectangle([x, 136 + DROP, x + 4, 140 + DROP], fill=hx("16161a"), outline=hx("5a5a60"))
        d.point((x + 1, 137 + DROP), fill=hx("8a8a98"))
    d.line([(205, 139 + DROP), (212, 131 + DROP)], fill=hx("1a1a1a"))
    d.point((212, 131 + DROP), fill=hx("d8b860"))
    # candlestick telephone, the receiver on its hook
    d.ellipse([217, 139 + DROP, 227, 142 + DROP], fill=hx("16141a"))
    d.rectangle([221, 126 + DROP, 223, 140 + DROP], fill=hx("1a181e"))
    d.line([(222, 127 + DROP), (222, 138 + DROP)], fill=hx("4a4850"))
    d.polygon([(218, 122 + DROP), (226, 122 + DROP), (224, 127 + DROP), (220, 127 + DROP)], fill=hx("16141a"))
    d.line([(219, 122 + DROP), (225, 122 + DROP)], fill=hx("5a5860"))
    d.line([(224, 129 + DROP), (226, 130 + DROP)], fill=hx("2a282e"))
    d.rectangle([226, 128 + DROP, 228, 136 + DROP], fill=hx("16141a"))
    d.line([(227, 136 + DROP), (226, 140 + DROP), (220, 141 + DROP)], fill=hx("1a1a1a"))
    # banker's lamp: brass foot and stem, green glass shade, the bulb glowing under it
    d.ellipse([287, 139 + DROP, 305, 143 + DROP], fill=hx("8a7a3a"), outline=hx("3a2a10"))
    d.line([(290, 140 + DROP), (300, 140 + DROP)], fill=hx("d8c070"))
    d.rectangle([295, 125 + DROP, 297, 140 + DROP], fill=hx("a08a40"))
    d.line([(295, 125 + DROP), (295, 139 + DROP)], fill=hx("e0c878"))




def _coat(d, cx, top, bottom, col, seed):
    """An overcoat on a wooden hanger: shoulders, notched lapels, a button stand, sleeves and soft folds."""
    hi, lo = mul(col, 1.45), mul(col, 0.62)
    d.line([(cx, top - 5), (cx, top - 2)], fill=hx("b0a070"))
    d.arc([cx - 2, top - 8, cx + 2, top - 4], 180, 360, fill=hx("b0a070"))
    d.polygon([(cx - 9, top + 2), (cx, top - 2), (cx + 9, top + 2)], fill=hx("7a5430"))
    body = [(cx - 9, top + 1), (cx - 3, top - 1), (cx + 3, top - 1), (cx + 9, top + 1),
            (cx + 11, bottom), (cx - 11, bottom)]
    d.polygon(body, fill=col)
    d.line([(cx - 9, top + 1), (cx - 11, bottom)], fill=lo)
    d.line([(cx + 9, top + 1), (cx + 11, bottom)], fill=lo)
    for s in (-1, 1):  # sleeves hanging at the sides
        d.line([(cx + s * 8, top + 4), (cx + s * 9, top + 46)], fill=lo)
        d.line([(cx + s * 7, top + 5), (cx + s * 8, top + 45)], fill=hi)
        d.line([(cx + s * 9, top + 46), (cx + s * 6, top + 46)], fill=lo)
    d.polygon([(cx - 3, top - 1), (cx, top + 16), (cx + 3, top - 1)], fill=hx("0e0a08"))  # empty neck
    for s in (-1, 1):  # lapels
        d.polygon([(cx + s * 3, top - 1), (cx + s * 6, top + 6), (cx + s * 4, top + 8), (cx + s * 1, top + 18)],
                  fill=hi)
        d.line([(cx + s * 3, top - 1), (cx + s * 1, top + 18)], fill=lo)
    d.line([(cx, top + 18), (cx + 1, bottom)], fill=lo)
    for y in range(top + 22, bottom - 8, 10):
        d.point((cx - 2, y), fill=hx("0a0806"))
    rnd = random.Random(seed)
    for _ in range(3):
        x = cx + rnd.randint(-6, 6)
        d.line([(x, top + rnd.randint(30, 50)), (x + rnd.choice((-1, 1)), bottom - 1)], fill=lo)
    d.line([(cx - 11, bottom), (cx + 11, bottom)], fill=lo)
    d.rectangle([cx - 4, top + 34, cx - 1, top + 35], fill=lo)  # pocket flap


def _cloak_and_mask(d, x0, y0, x1, y1):
    """The niche's floor: the black hooded cloak folded into a thick bundle, the white Bauta half-mask laid on top of it
    face up and seen side-on: the brow and the long nose rising over the bundle's roll."""
    mx = (x0 + x1) // 2
    black, fold, shine = hx("1a1820"), hx("060508"), hx("4a4458")
    # the bundle, a hood flopped over its left end, the crimson lining showing at the folds
    d.polygon([(x0 + 3, y1), (x0 + 5, y1 - 13), (x0 + 12, y1 - 17), (x1 - 10, y1 - 17), (x1 - 4, y1 - 12),
               (x1 - 3, y1)], fill=black)
    d.polygon([(x0 + 4, y1), (x0 + 3, y1 - 10), (x0 + 9, y1 - 17), (x0 + 18, y1 - 15), (x0 + 16, y1 - 4),
               (x0 + 11, y1)], fill=hx("18151e"))
    d.arc([x0 + 6, y1 - 15, x0 + 16, y1 - 3], 200, 340, fill=shine)
    d.polygon([(x0 + 9, y1 - 11), (x0 + 13, y1 - 12), (x0 + 12, y1 - 6)], fill=fold)  # inside the hood
    for y in (y1 - 11, y1 - 6):
        d.line([(x0 + 18, y), (x1 - 5, y + 1)], fill=fold)
        d.line([(x0 + 19, y - 1), (x1 - 6, y)], fill=shine)
    d.line([(x0 + 18, y1 - 2), (x1 - 4, y1 - 2)], fill=hx("4a1420"))
    d.line([(x1 - 9, y1 - 13), (x1 - 5, y1 - 2)], fill=hx("4a1420"))
    d.rectangle([x1 - 14, y1 - 9, x1 - 11, y1 - 7], fill=hx("a8a8b0"))  # the clasp
    d.line([(x1 - 11, y1 - 8), (x1 - 7, y1 - 6)], fill=hx("6a6a74"))
    # the Bauta, face up: the brow at the left, the long nose peaking towards the right where the plate stops short
    top = y1 - 17
    d.polygon([(mx - 9, top + 1), (mx - 8, top - 2), (mx - 4, top - 3), (mx + 1, top - 7), (mx + 3, top - 4),
               (mx + 6, top - 2), (mx + 7, top + 1)], fill=hx("d8d4cc"))
    d.line([(mx - 8, top - 2), (mx - 4, top - 3)], fill=hx("ece8e0"))  # the brow catching the light
    d.line([(mx - 3, top - 4), (mx + 1, top - 7)], fill=hx("ffffff"))  # the nose ridge
    d.line([(mx + 2, top - 5), (mx + 6, top - 1)], fill=hx("a8a49c"))
    d.point((mx - 5, top - 1), fill=hx("8a867e"))  # an eye hole    d.line([(mx - 13, top + 1), (mx + 13, top + 1)], fill=fold)  # the roll's shadow under the rim


LAMP_GREENS = ("0e3216", "22622e", "56a066")


def lamp_shade(d):
    """The banker's lamp's green glass shade, the lit bulb under it and the pull chain. Painted over the moonlight,
    since it's the one thing in the room making its own light."""
    dark, mid, hi = (hx(c) for c in LAMP_GREENS)
    d.polygon([(283, 139), (309, 139), (306, 131), (286, 131)], fill=mid, outline=dark)
    d.line([(287, 132), (305, 132)], fill=hi)
    d.line([(285, 135), (291, 135)], fill=hi)
    d.line([(299, 134), (306, 137)], fill=dark)
    d.line([(283, 139), (309, 139)], fill=hx("b89a48"))
    d.rectangle([288, 140, 304, 141], fill=hx("fff0b8"))
    d.line([(302, 140), (302, 145)], fill=hx("a08840"))
    d.point((302, 146), fill=hx("e0c878"))


def wardrobe(img, d, opened, secret):
    """Harrington's walnut wardrobe: cornice, raised and fielded panels, brass handles and a plinth. Open, it shows
    a hat shelf, three overcoats on a brass rail, and below them the false back, or the niche behind it."""
    wx0, wx1, wy0, wy1 = 372, 456, 52, 204
    walnut, edge = hx("3e2614"), hx("140a04")
    d.rectangle([wx0 - 7, wy0 - 11, wx1 + 7, wy0 - 7], fill=hx("5a3820"), outline=edge)  # cornice
    d.line([(wx0 - 6, wy0 - 10), (wx1 + 6, wy0 - 10)], fill=hx("8a5a32"))
    d.rectangle([wx0 - 4, wy0 - 6, wx1 + 4, wy0], fill=hx("4a2e18"), outline=edge)
    for x in range(wx0 - 2, wx1 + 3, 4):
        d.rectangle([x, wy0 - 4, x + 1, wy0 - 2], fill=hx("6a4426"))
    d.rectangle([wx0, wy0, wx1, wy1], fill=walnut)
    _grain(d, (wx0, wy0, wx1, wy1), walnut, 77, 4)
    d.rectangle([wx0 + 1, wy1 - 9, wx1 - 1, wy1 - 1], fill=hx("2e1c0e"))  # plinth
    d.line([(wx0 + 1, wy1 - 9), (wx1 - 1, wy1 - 9)], fill=hx("6a4426"))
    d.rectangle([wx0, wy0, wx1, wy1], outline=edge)
    if opened:
        ix0, iy0, ix1, iy1 = wx0 + 4, wy0 + 4, wx1 - 4, wy1 - 10
        d.rectangle([ix0, iy0, ix1, iy1], fill=hx("1a0f08"))
        d.polygon([(ix0, iy0), (ix0 + 6, iy0 + 6), (ix0 + 6, iy1 - 4), (ix0, iy1)], fill=hx("2a1a0c"))  # sides
        d.polygon([(ix1, iy0), (ix1 - 6, iy0 + 6), (ix1 - 6, iy1 - 4), (ix1, iy1)], fill=hx("221408"))
        d.rectangle([ix0 + 6, iy0 + 6, ix1 - 6, iy1 - 4], fill=hx("120a06"))
        _grain(d, (ix0 + 6, iy0 + 6, ix1 - 6, wy0 + 98), hx("1a0f08"), 78, 5)
        # hat shelf: a hat box and a homburg
        d.rectangle([ix0, wy0 + 12, ix1, wy0 + 14], fill=hx("4a2e18"))
        d.line([(ix0, wy0 + 12), (ix1, wy0 + 12)], fill=hx("6a4426"))
        d.rectangle([ix0 + 8, wy0 + 5, ix0 + 22, wy0 + 11], fill=hx("6a5a48"), outline=hx("2a2018"))
        d.line([(ix0 + 8, wy0 + 7), (ix0 + 22, wy0 + 7)], fill=hx("8a3a2a"))
        d.ellipse([ix1 - 24, wy0 + 9, ix1 - 8, wy0 + 12], fill=hx("1e1c22"))
        d.chord([ix1 - 21, wy0 + 4, ix1 - 11, wy0 + 14], 180, 360, fill=hx("26242a"))
        d.line([(ix1 - 20, wy0 + 9), (ix1 - 12, wy0 + 9)], fill=hx("4a3a2a"))
        # brass rail and three overcoats, all the same cut
        d.line([(ix0 + 2, wy0 + 20), (ix1 - 2, wy0 + 20)], fill=hx("b09a5a"))
        d.line([(ix0 + 2, wy0 + 21), (ix1 - 2, wy0 + 21)], fill=hx("5a4a2a"))
        for i, c in enumerate(("2a2a30", "4a3a2a", "26262e")):
            _coat(d, wx0 + 21 + i * 21, wy0 + 26, wy0 + 96, hx(c), 80 + i)
        # cedar blocks against the sides
        for x in (ix0 + 7, ix1 - 13):
            d.rectangle([x, wy0 + 93, x + 6, wy0 + 97], fill=hx("a0583a"), outline=hx("4a2010"))
            d.line([(x + 1, wy0 + 94), (x + 5, wy0 + 94)], fill=hx("d08a60"))
        d.rectangle([ix0, wy0 + 98, ix1, wy0 + 99], fill=hx("4a2e18"))
        px0, py0, px1, py1 = wx0 + 10, wy0 + 100, wx1 - 10, wy1 - 14
        if secret:
            # the false back opened like a pair of little doors on a velvet-lined niche
            d.rectangle([px0, py0, px1, py1], fill=hx("060302"))
            d.rectangle([px0 + 6, py0 + 2, px1 - 6, py1], fill=hx("140a10"))
            d.line([(px0 + 6, py0 + 2), (px1 - 6, py0 + 2)], fill=hx("2a1420"))
            for x in range(px0 + 9, px1 - 6, 5):
                d.line([(x, py0 + 3), (x, py1 - 6)], fill=hx("0e060a"))
            d.polygon([(px0, py0), (px0 + 6, py0 + 3), (px0 + 6, py1 - 2), (px0, py1)], fill=hx("5a3a20"),
                      outline=edge)
            d.polygon([(px1, py0), (px1 - 6, py0 + 3), (px1 - 6, py1 - 2), (px1, py1)], fill=hx("4a2e18"),
                      outline=edge)
            for x in (px0 + 3, px1 - 3):
                d.point((x, (py0 + py1) // 2), fill=hx("c8a858"))
            _cloak_and_mask(d, px0 + 6, py0 + 4, px1 - 6, py1)
        else:
            d.rectangle([px0, py0, px1, py1], fill=hx("2a1a0c"), outline=edge)
            for x in range(px0 + 8, px1, 8):  # tongue-and-groove boards
                d.line([(x, py0 + 1), (x, py1 - 1)], fill=hx("1e1208"))
                d.line([(x + 1, py0 + 1), (x + 1, py1 - 1)], fill=hx("3a2614"))
            d.line([(px1 - 2, py0 + 1), (px1 - 2, py1 - 1)], fill=hx("060302"))  # the gap down one side
            d.line([(px1 - 1, py0 + 2), (px1 - 1, py1 - 2)], fill=hx("5a3a20"))
        # the doors swung open to either side, their inner faces showing: a mirror and a tie rack
        for s, hinge in ((-1, wx0), (1, wx1)):
            far = hinge + s * 14
            d.polygon([(hinge, wy0), (far, wy0 + 6), (far, wy1 + 4), (hinge, wy1)], fill=hx("4a2e18"), outline=edge)
            d.polygon([(hinge + s * 3, wy0 + 12), (far - s * 3, wy0 + 16), (far - s * 3, wy1 - 8),
                       (hinge + s * 3, wy1 - 12)], outline=hx("2a1a0c"))
            d.line([(hinge + s * 1, wy0 + 1), (hinge + s * 1, wy1 - 1)], fill=hx("6a4426"))
        d.polygon([(wx0 - 4, wy0 + 20), (wx0 - 11, wy0 + 24), (wx0 - 11, wy0 + 80), (wx0 - 4, wy0 + 78)],
                  fill=hx("5a6a80"))
        d.line([(wx0 - 6, wy0 + 26), (wx0 - 9, wy0 + 40)], fill=hx("a8b8d0"))
        d.line([(wx1 + 4, wy0 + 30), (wx1 + 11, wy0 + 33)], fill=hx("b09a5a"))
        for i, c in enumerate(("6a1a1a", "2a3a6a", "4a4a20")):
            x = wx1 + 5 + i * 2
            d.line([(x, wy0 + 31 + i), (x, wy0 + 56 + i)], fill=hx(c), width=2)
    else:
        mx = (wx0 + wx1) // 2
        for x0, x1 in ((wx0 + 5, mx - 4), (mx + 4, wx1 - 5)):
            for y0, y1 in ((wy0 + 9, wy0 + 70), (wy0 + 78, wy1 - 14)):
                d.rectangle([x0, y0, x1, y1], fill=hx("442a16"), outline=hx("1e1208"))
                _bevel(d, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), hx("5e3c20"), hx("24140a"))
                _bevel(d, (x0 + 4, y0 + 4, x1 - 4, y1 - 4), hx("24140a"), hx("5e3c20"))
                d.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], fill=hx("4a2e18"))
                _grain(d, (x0 + 5, y0 + 5, x1 - 5, y1 - 5), hx("4a2e18"), x0 + y0, 4)
        d.line([(mx, wy0), (mx, wy1 - 9)], fill=edge)
        d.line([(mx + 1, wy0 + 1), (mx + 1, wy1 - 10)], fill=hx("5a3a20"))
        for x in (wx0 + 1, wx1 - 2):
            for y in (wy0 + 16, wy1 - 26):
                d.rectangle([x, y, x + 1, y + 6], fill=hx("a08a40"))
        d.rectangle([mx - 6, 126, mx - 3, 138], fill=hx("8a6a28"))
        d.rectangle([mx + 4, 126, mx + 7, 138], fill=hx("8a6a28"))
        d.line([(mx - 5, 127), (mx - 5, 137)], fill=hx("e0c068"))
        d.line([(mx + 5, 127), (mx + 5, 137)], fill=hx("e0c068"))
        d.rectangle([mx - 2, 140, mx + 2, 146], fill=hx("b89a48"))
        d.rectangle([mx - 1, 142, mx, 144], fill=hx("0a0604"))


PORTRAIT_FACE_BOX = (219, 23, 277, 80)
PORTRAIT_FACE_COLOURS = """
69646f 584d47 534738 3d4763 4b4138 403c4b 3c4157 41353a 3a344e 333449 3a3641 343443 343148 3b3024 392b1e 342d2f 342931
303143 2c2f40 2e2a34 33261a 30231a 282531 2a2426 27202a 2a201a 241c21 281c16 241a15 231814 1c1c29 1f1919 191927 1f1915
1e1716 181721 1d1514 1b1414 17141c 1b1411 1a1212 191313 18110e 16131b 171111 160f0e 141319 150f0f 0d1022 130d0b 120d0d
0f0b0a 0f0a07 0e0a0a 0d0a08 0b0a11 0c0805
"""


def paint_office(left=False, right=False, closet=False, secret=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # panelled walls
    vgrad(img, (0, 0, W - 1, 196), hx("3a2618"), hx("2a1a10"))
    for x in range(0, W, 40):
        d.rectangle([x + 4, 110, x + 36, 186], outline=hx("1e1209"))
        d.line([(x + 5, 111), (x + 35, 111)], fill=hx("5a3c24"))
    d.rectangle([0, 100, W - 1, 104], fill=hx("5a3a22"))
    d.rectangle([0, 0, W - 1, 8], fill=hx("1e140c"))
    noise(img, (0, 0, W - 1, 196), 4, 51)
    vgrad(img, (0, 196, W - 1, H - 1), hx("3a1a1a"), hx("4a2222"))
    d.polygon([(90, 214), (390, 214), (420, 262), (60, 262)], fill=hx("4e2428"), outline=hx("7a5a2a"))
    d.polygon([(96, 218), (384, 218), (410, 258), (70, 258)], outline=hx("a07a46"))
    for x in range(114, 380, 32):
        d.polygon([(x, 236), (x + 7, 230), (x + 14, 236), (x + 7, 242)], outline=hx("805238"))
    noise(img, (0, 196, W - 1, H - 1), 5, 53)
    # window on the left: the fire escape and the city at night
    d.rectangle([24, 30, 112, 160], fill=hx("4a3220"))
    d.rectangle([30, 36, 106, 154], fill=hx("141a30"))
    rnd = random.Random(52)
    for _ in range(18):
        x, y = rnd.randint(32, 104), rnd.randint(90, 150)
        d.rectangle([x, y, x + 1, y + 2], fill=hx("c8a858"))
    for y in (100, 140):
        d.line([(30, y), (106, y)], fill=hx("0a0a10"), width=2)
    for x in range(30, 107, 6):
        d.line([(x, 128), (x, 140)], fill=hx("0a0a10"))
    d.rectangle([66, 36, 69, 154], fill=hx("4a3220"))
    d.rectangle([30, 92, 106, 95], fill=hx("4a3220"))
    d.rectangle([20, 160, 116, 166], fill=hx("5a3c26"))
    # Harrington senior's portrait in a heavy gilt frame, a little brass picture light above it
    d.rectangle([212, 16, 284, 102], fill=hx("6a4a1a"))
    d.rectangle([214, 18, 282, 100], fill=hx("b08a3a"))
    d.rectangle([217, 21, 279, 97], fill=hx("7a5a22"))
    img.paste(harrington_portrait(58, 72), (219, 23))
    d.line([(214, 18), (282, 18)], fill=hx("d8b860"))
    d.line([(214, 18), (214, 100)], fill=hx("d8b860"))
    d.rectangle([238, 10, 258, 13], fill=hx("8a7a3a"))
    d.line([(248, 13), (248, 16)], fill=hx("6a5a2a"))
    filing_cabinet(img, d)
    desk(img, d, left, right)
    wardrobe(img, d, closet, secret)
    # moonlight: everything cold, a blue shaft from the window
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, (118, 128, 186))))
    light(img, "polygon", [(30, 36), (106, 36), (300, 262), (110, 262)], hx("5a70b0"), 0.35, 14)
    light(img, "ellipse", [268, 100 + DESK_DROP, 326, 174 + DESK_DROP], hx("d8a058"), 0.16, 10)
    light(img, "ellipse", [280, 124 + DESK_DROP, 312, 146 + DESK_DROP], hx("ffd890"), 0.3, 4)
    lamp_shade(ImageDraw.Draw(img))
    light(img, "ellipse", [218, 12, 278, 74], hx("e0b868"), 0.12, 8)
    vignette(img, 0.6, (8, 8, 22), 40)
    return img


def build_office():
    base = paint_office()
    v = {"drawer_left": paint_office(left=True), "drawer_right": paint_office(right=True),
         "closet": paint_office(closet=True), "secret": paint_office(closet=True, secret=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.4)
    pal = palette_of(blend, 124) + [hx(c) for c in LAMP_GREENS]
    px = pixelize(base, pal)
    # the furniture moves the shared palette about; the face keeps exactly the colours it was first painted in
    face = pixelize(base, [hx(c) for c in PORTRAIT_FACE_COLOURS.split()])
    px.paste(face.crop(PORTRAIT_FACE_BOX), PORTRAIT_FACE_BOX[:2])
    save(px, "rooms", "harrington_office.png")
    overlay(v["drawer_left"], px, pal, (180, 162, 236, 206), "harrington_office_drawer_left")
    overlay(v["drawer_right"], px, pal, (264, 162, 320, 206), "harrington_office_drawer_right")
    overlay(v["closet"], px, pal, (350, 40, 476, 212), "harrington_office_closet")
    # the niche is drawn over the open closet, so it's cut against the open-closet state
    closet_px = pixelize(v["closet"], pal)
    overlay(v["secret"], closet_px, pal, (350, 40, 476, 212), "harrington_office_secret")
    return px


# ------------------------------------------------------------------------------------------------ DANIEL'S BEDROOM

# the couple were painted at the standing height of the other rooms and filled the bed; in bed they read smaller
BED_FIGURE_H = 54


def _bed_figures(sD):
    """Daniel sitting up in bed reading, seen in profile. His wife is never painted: she sleeps behind him with the
    quilt pulled over her head. Returns the RGBA crop and the hands' offset from his seat corner."""
    from .figure import figure, pose
    from .sprites import DANIEL
    hD = BED_FIGURE_H * sD
    ps = pose(90, legs={1: (86, 0, 0), -1: (84, 4, 0)}, arms={1: ("swing", 22, 4, 82), -1: ("swing", 28, 4, 78)},
              lean=-7.0, nod=0.01)
    a = figure(dict(DANIEL, h=hD), ps, int(hD * 1.2), int(hD * 1.3))
    a.putalpha(a.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    a = a.crop(a.getbbox())
    hand = (0.31 * hD, -0.255 * hD)
    return a, hand


def _frange(a, b, step):
    v = a
    while v <= b + 1e-6:
        yield v
        v += step


def _bedroom_window(img, d, x0, x1, y0, y1):
    """A sash window on the back wall: painted architrave and sill, a blind half down over the night city (far and
    near skylines, lit windows, a water tower), glazing bars, and linen curtains in folds, tied back on a rod."""
    trim, trim_l, trim_d = hx("f0ece2"), hx("fffcf4"), hx("b4ad9d")
    shadow(img, "rect", [x0 - 2, y0 - 1, x1 + 8, y1 + 10], 0.3, 3)
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 2], fill=trim)
    _bevel(d, (x0 - 4, y0 - 4, x1 + 4, y1 + 2), trim_l, trim_d)
    _bevel(d, (x0 - 2, y0 - 2, x1 + 2, y1 + 1), trim_d, trim_l)
    # the sky deepens upwards; a faint glow hangs over the city
    vgrad(img, (x0, y0, x1, y1), hx("0a1024"), hx("3c4870"))
    rnd = random.Random(4)
    for _ in range(12):
        d.point((rnd.randint(x0 + 2, x1 - 2), rnd.randint(y0 + 30, y0 + 40)), fill=hx("c8d0e8"))
    far, near = hx("222c4c"), hx("0c0f18")
    x = x0
    while x < x1:  # the far skyline: low blocks in a lighter, hazier blue
        w = rnd.randint(5, 10)
        top = rnd.randint(y1 - 36, y1 - 24)
        d.rectangle([x, top, min(x + w, x1), y1], fill=far)
        for wy in range(top + 2, y1, 3):
            for wx in range(x + 1, min(x + w, x1), 2):
                if rnd.random() < 0.18:
                    d.point((wx, wy), fill=hx("7a6c4c"))
        x += w + 1
    tops = ((0, 18), (12, 28), (26, 13), (40, 33), (52, 20), (x1 - x0, 20))
    poly = [(x0, y1)]
    for (ua, ha), (ub, _) in zip(tops, tops[1:]):
        poly += [(x0 + ua, y1 - ha), (x0 + ub, y1 - ha)]
    poly.append((x1, y1))
    d.polygon(poly, fill=near)
    for ua, ha in tops[:-1]:  # parapets catch a little sky
        d.line([(x0 + ua, y1 - ha), (x0 + ua + 11, y1 - ha)], fill=hx("2a3048"))
    # a water tower on the low roof, an aerial on the tall one
    tx, ty = x0 + 30, y1 - 13
    for lx in (tx, tx + 6):
        d.line([(lx, ty), (lx + (1 if lx == tx else -1), ty - 4)], fill=near)
    d.rectangle([tx, ty - 9, tx + 7, ty - 4], fill=near)
    d.polygon([(tx - 1, ty - 9), (tx + 3.5, ty - 13), (tx + 8, ty - 9)], fill=near)
    d.line([(x0 + 46, y1 - 33), (x0 + 46, y1 - 40)], fill=near)
    d.point((x0 + 46, y1 - 41), fill=hx("e05040"))
    for _ in range(40):
        wx, wy = rnd.randint(x0 + 2, x1 - 3), rnd.randint(y1 - 32, y1 - 3)
        if img.getpixel((wx, wy)) == near and img.getpixel((wx + 1, wy)) == near:
            d.rectangle([wx, wy, wx + 1, wy], fill=rnd.choice([hx("f0c870"), hx("e8d8a0"), hx("a0b0c8")]))
    # glazing: two sashes, each two panes wide and two high; a reflection runs across the glass
    for gx in (x0 + 9, x0 + 22, x1 - 22, x1 - 9):
        d.line([(gx, y0 + 28), (gx + 8, y0 + 40)], fill=hx("2c3858"))
    ym = y0 + 48
    d.rectangle([x0, y0, x1, y1], outline=trim, width=2)
    for gx in (x0 + 18, x1 - 18):
        d.line([(gx, y0), (gx, y1)], fill=trim)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=trim, width=3)
    d.rectangle([x0, ym - 1, x1, ym + 1], fill=trim)
    d.line([(x0, ym + 2), (x1, ym + 2)], fill=trim_d)
    d.line([(x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], fill=trim_d)
    for cx in ((x0 + x1) // 2 - 6, (x0 + x1) // 2 + 6):  # sash lifts
        d.rectangle([cx - 1, ym + 2, cx + 1, ym + 3], fill=hx("b89a58"))
    # the blind: slats with a lit edge, a weighted bottom rail, a pull ring and the cord
    d.rectangle([x0 + 1, y0, x1 - 1, y0 + 27], fill=hx("e4dcc8"))
    for y in range(y0 + 3, y0 + 26, 3):
        d.line([(x0 + 1, y), (x1 - 1, y)], fill=hx("c4bca6"))
        d.line([(x0 + 1, y + 1), (x1 - 1, y + 1)], fill=hx("f0eadc"))
    d.rectangle([x0 + 1, y0, x1 - 1, y0 + 2], fill=trim_d)
    d.rectangle([x0, y0 + 26, x1, y0 + 28], fill=hx("cfc6b0"))
    d.line([(x0, y0 + 29), (x1, y0 + 29)], fill=hx("4a4a58"))
    cx = (x0 + x1) // 2
    d.line([(cx, y0 + 29), (cx, y0 + 32)], fill=hx("cfc6b0"))
    d.ellipse([cx - 2, y0 + 32, cx + 2, y0 + 36], outline=hx("d8d0bc"))
    d.line([(x1 - 4, y0 + 3), (x1 - 4, y1 - 12)], fill=hx("d8d0bc"))
    d.rectangle([x1 - 5, y1 - 12, x1 - 3, y1 - 9], fill=hx("c8b898"))
    # sill, with an apron under it
    d.rectangle([x0 - 6, y1 + 3, x1 + 6, y1 + 6], fill=trim)
    d.line([(x0 - 6, y1 + 3), (x1 + 6, y1 + 3)], fill=trim_l)
    d.line([(x0 - 6, y1 + 6), (x1 + 6, y1 + 6)], fill=trim_d)
    d.rectangle([x0 - 2, y1 + 7, x1 + 2, y1 + 9], fill=hx("e2ddd0"))
    d.line([(x0 - 2, y1 + 10), (x1 + 2, y1 + 10)], fill=hx("a49c8c"))
    # curtains: pleated, gathered by a tie-back two-thirds down, the hem flaring
    lt, dk = hx("d8caa8"), hx("9a8a6c")
    ctop, cbot, ctie = y0 - 8, y1 + 20, y1 - 10
    for side, outer in ((-1, x0 - 18), (1, x1 + 18)):
        for y in range(ctop, cbot + 1):
            if y <= ctie:
                t = (y - ctop) / (ctie - ctop)
                w = 14 - 5 * t * t
            else:
                t = (y - ctie) / (cbot - ctie)
                w = 9 + 6 * t ** 0.8
            for i in range(int(round(w)) + 1):
                u = i / max(w, 1) * 14
                f = 0.5 + 0.5 * math.sin(u * 2 * math.pi / 4.6 + 0.6)
                c = mix(dk, lt, f)
                if y >= cbot - 1:
                    c = mul(c, 0.82)
                px_ = outer + i if side < 0 else outer - i
                d.point((px_, y), fill=c)
            edge = outer + int(round(w)) if side < 0 else outer - int(round(w))
            d.point((edge, y), fill=mul(dk, 0.8))
        tx0, tx1 = (outer - 1, outer + 10) if side < 0 else (outer - 10, outer + 1)
        d.rectangle([tx0, ctie - 1, tx1, ctie + 1], fill=hx("8a6a40"))
        d.line([(tx0, ctie - 1), (tx1, ctie - 1)], fill=hx("b89060"))
        kx = tx1 if side < 0 else tx0
        d.line([(kx, ctie + 1), (kx, ctie + 5)], fill=hx("8a6a40"))
        d.rectangle([kx - 1, ctie + 5, kx + 1, ctie + 7], fill=hx("a07a48"))
        for rx in range(min(outer, outer - 14 * (side > 0)), max(outer, outer + 14 * (side < 0)) + 1, 4):
            d.ellipse([rx - 1, ctop - 3, rx + 2, ctop + 1], outline=hx("5a4e44"))
    rod_y = ctop - 1
    d.line([(x0 - 24, rod_y), (x1 + 24, rod_y)], fill=hx("3a3430"), width=2)
    d.line([(x0 - 24, rod_y - 1), (x1 + 24, rod_y - 1)], fill=hx("6a6058"))
    for fx in (x0 - 26, x1 + 26):
        d.ellipse([fx - 2, rod_y - 3, fx + 2, rod_y + 2], fill=hx("3a3430"))
        d.point((fx - 1, rod_y - 2), fill=hx("8a8078"))
    for bx in (x0 - 20, x1 + 20):
        d.rectangle([bx - 1, rod_y - 1, bx + 1, rod_y + 4], fill=hx("2a2420"))


def _leaf(d, base, ang, length, width, col, hi, rib, bend=0.0):
    """A long pointed leaf from base at ang degrees, drooping by bend; its upper half lit, a midrib down the middle."""
    a = math.radians(ang)
    ux, uy = math.cos(a), math.sin(a)
    nx, ny = -uy, ux
    spine = []
    for i in range(9):
        t = i / 8
        spine.append((base[0] + ux * length * t, base[1] + uy * length * t + bend * t * t, t))
    left = [(x + nx * width * math.sin(math.pi * t ** 0.85), y + ny * width * math.sin(math.pi * t ** 0.85))
            for x, y, t in spine]
    right = [(x - nx * width * math.sin(math.pi * t ** 0.85), y - ny * width * math.sin(math.pi * t ** 0.85))
             for x, y, t in spine]
    mid = [(x, y) for x, y, _ in spine]
    d.polygon(left + right[::-1], fill=col)
    d.polygon(left + mid[::-1], fill=hi)
    d.line(mid[1:-1], fill=rib)


def _bedroom_plant(img, d, R):
    """A peace lily in a terracotta pot: a rolled rim, dark soil, a fan of pointed leaves and two white spathes."""
    R.box(img, 371.5, 379.5, 30, 36, 4, 10, hx("b06a48"), top=hx("2e1e14"), side=hx("7a4430"))
    R.box(img, 370.5, 380.5, 35.5, 38.5, 3.5, 10.5, hx("c47c58"), top=hx("2e1e14"), side=hx("8a5038"))
    R.line(img, (370.5, 38.2, 10.5), (380.5, 38.2, 10.5), hx("e8a47c"))
    R.line(img, (371.5, 35.3, 10), (379.5, 35.3, 10), hx("7a4430"))
    R.line(img, (373, 31, 10), (373, 34.5, 10), hx("d08a64"))
    R.line(img, (371.5, 30.2, 10), (379.5, 30.2, 10), hx("5a3220"))
    pc = R.P(375.5, 38, 7)
    dark, lit, rib = hx("2a6a32"), hx("5cac58"), hx("94d080")
    for ang, ln, w, bend in ((-160, 12, 2.4, 4), (-20, 12, 2.4, 4), (-140, 15, 2.8, 3), (-40, 15, 2.8, 3),
                             (-120, 18, 3.0, 1.5), (-62, 18, 3.0, 1.5)):
        _leaf(d, pc, ang, ln, w, dark, lit, rib, bend)
    for ang, ln in ((-82, 21), (-102, 18)):  # the flowers on their stalks
        a = math.radians(ang)
        tip = (pc[0] + math.cos(a) * ln, pc[1] + math.sin(a) * ln)
        d.line([pc, tip], fill=hx("3a6a3a"))
        d.polygon([(tip[0], tip[1] + 1), (tip[0] - 2, tip[1] - 2), (tip[0], tip[1] - 6), (tip[0] + 2, tip[1] - 2)],
                  fill=hx("f4f2e6"))
        d.point((tip[0], tip[1] - 2), fill=hx("e0c860"))
    for ang, ln, w in ((-92, 16, 2.8), (-78, 11, 2.4), (-108, 12, 2.4)):
        _leaf(d, pc, ang, ln, w, dark, lit, rib, 0.5)


def _bedroom_photo(img, d, R, fx, fh, sub):
    """A small silver-framed photograph on a stand: their wedding, or a child on a beach."""
    R.box(img, fx, fx + 7, 30, 30 + fh, 7, 8, hx("8a8c90"), top=hx("c8cacc"), side=hx("5a5c60"))
    a0, a1 = R.P(fx + 1, 30 + fh - 1, 8), R.P(fx + 6, 31, 8)
    x0, y0, x1, y1 = round(a0[0]), round(a0[1]), round(a1[0]), round(a1[1])
    d.rectangle([x0, y0, x1, y1], fill=hx("d8c8a0"))
    d.line([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1)], fill=hx("e8eaec"))
    if sub == 0:
        for hx_, dress in ((x0 + 2, hx("3a3430")), (x1 - 2, hx("f4f0e4"))):
            d.rectangle([hx_ - 1, y0 + 4, hx_ + 1, y1], fill=dress)
            d.rectangle([hx_ - 1, y0 + 2, hx_, y0 + 3], fill=hx("8a6a50"))
    else:
        d.rectangle([x0, y0, x1, y0 + 3], fill=hx("a8b8c0"))
        d.rectangle([x0, y1 - 2, x1, y1], fill=hx("e0d0a0"))
        d.rectangle([(x0 + x1) // 2, y0 + 3, (x0 + x1) // 2 + 1, y1 - 2], fill=hx("6a4a3a"))
        d.point(((x0 + x1) // 2, y0 + 2), fill=hx("8a6a50"))


def _bedroom_print(img, d, box):
    """The landscape print over the chest: a moulded frame, a bevelled mat, and mountains over a lake under the moon."""
    x0, y0, x1, y1 = box
    shadow(img, "rect", [x0 + 2, y0 + 3, x1 + 3, y1 + 4], 0.35, 2)
    d.rectangle(box, fill=hx("3a2e22"))
    _bevel(d, box, hx("7a6248"), hx("16110c"))
    _bevel(d, (x0 + 2, y0 + 2, x1 - 2, y1 - 2), hx("1e1810"), hx("6a5440"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("a08a5a"))
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=hx("f0ece2"))
    p0, q0, p1, q1 = x0 + 8, y0 + 8, x1 - 8, y1 - 8
    _bevel(d, (p0 - 1, q0 - 1, p1 + 1, q1 + 1), hx("c4beb0"), hx("fffcf4"))
    vgrad(img, (p0, q0, p1, q0 + 26), hx("2a4a6e"), hx("b0c8d8"))
    light(img, "ellipse", [p0 + 20, q0 + 1, p0 + 35, q0 + 16], hx("c0ccd4"), 0.35, 2)
    d.ellipse([p0 + 24, q0 + 4, p0 + 31, q0 + 11], fill=hx("ece4c4"))
    d.ellipse([p0 + 27, q0 + 5, p0 + 30, q0 + 8], fill=hx("d8d0b0"))
    for sx, sy in ((p0 + 4, q0 + 3), (p0 + 12, q0 + 6), (p0 + 35, q0 + 3), (p0 + 9, q0 + 10)):
        d.point((sx, sy), fill=hx("e8ecf4"))
    d.polygon([(p0, q0 + 24), (p0 + 5, q0 + 16), (p0 + 10, q0 + 20), (p0 + 16, q0 + 12), (p0 + 22, q0 + 18),
               (p0 + 28, q0 + 14), (p0 + 34, q0 + 19), (p1, q0 + 16), (p1, q0 + 26), (p0, q0 + 26)], fill=hx("86a2b8"))
    near = [(p0, q0 + 28), (p0 + 9, q0 + 18), (p0 + 17, q0 + 24), (p0 + 26, q0 + 10), (p1, q0 + 24), (p1, q0 + 30),
            (p0, q0 + 30)]
    d.polygon(near, fill=hx("4e7284"))
    d.polygon([(p0 + 9, q0 + 18), (p0 + 17, q0 + 24), (p0 + 12, q0 + 30), (p0 + 9, q0 + 30)], fill=hx("2a4654"))
    d.polygon([(p0 + 26, q0 + 10), (p1, q0 + 24), (p1, q0 + 30), (p0 + 30, q0 + 30)], fill=hx("2a4654"))
    d.polygon([(p0 + 26, q0 + 10), (p0 + 22, q0 + 16), (p0 + 25, q0 + 15), (p0 + 27, q0 + 17), (p0 + 30, q0 + 14)],
              fill=hx("e8ecf0"))
    d.polygon([(p0 + 9, q0 + 18), (p0 + 7, q0 + 21), (p0 + 9, q0 + 20), (p0 + 11, q0 + 21)], fill=hx("e8ecf0"))
    d.rectangle([p0, q0 + 30, p1, q0 + 34], fill=hx("24425a"))
    for ry in (q0 + 31, q0 + 33):
        d.line([(p0 + 25, ry), (p0 + 30, ry)], fill=hx("d8d0b0"))
    d.line([(p0, q0 + 30), (p1, q0 + 30)], fill=hx("4a6a80"))
    d.rectangle([p0, q0 + 35, p1, q1], fill=hx("1c2a20"))
    for tx, th in ((p0 + 2, 9), (p0 + 6, 12), (p0 + 10, 7), (p1 - 7, 10), (p1 - 3, 13)):
        d.polygon([(tx, q1 - th), (tx - 3, q1), (tx + 3, q1)], fill=hx("142018"))
    d.point((p1 - 2, q1 - 1), fill=hx("8a6a4a"))


def _bedroom_wall_print(img, d, R, WX):
    """The print on the left wall, seen at a steep angle: a sailing boat at sunset in a dark frame and cream mat."""
    def q(pts, c):
        R.quad(img, [(WX, y, z) for y, z in pts], c)

    def rect(y0, y1, z0, z1, c):
        q([(y0, z0), (y1, z0), (y1, z1), (y0, z1)], c)

    rect(54, 82, 40, 76, hx("3a2e22"))
    rect(80.8, 82, 40, 76, hx("7a6248"))
    rect(54, 55.2, 40, 76, hx("16110c"))
    rect(54, 82, 74.8, 76, hx("7a6248"))
    rect(56, 80, 42, 74, hx("f0ece2"))
    rect(58.6, 77.4, 45.6, 70.4, hx("c4beb0"))
    rect(70, 77, 46, 70, hx("4a6488"))
    rect(66, 70, 46, 70, hx("d8885a"))
    rect(64.5, 66.5, 46, 70, hx("f4c47a"))
    q([(64.5, 54), (67, 55), (67.8, 58), (67, 61), (64.5, 62)], hx("fff0b8"))
    rect(59, 64.5, 46, 70, hx("2a4a6a"))
    for y in (63, 61.5, 60):
        rect(y, y + 0.5, 55, 61, hx("e8b878"))
    q([(62.5, 49), (64.5, 48), (64.5, 56), (62.5, 55)], hx("1e1a18"))
    rect(64.5, 75, 51.8, 52.4, hx("2a2420"))
    q([(65, 52.4), (75, 52.4), (65, 56.5)], hx("f6f0e0"))
    q([(65.5, 51.8), (72, 51.8), (65.5, 49)], hx("e0d6c4"))


def _bedroom_nightstand(img, d, R, WX, z0, z1, cols, seed):
    """A bedside cabinet against the left wall: plinth, an overhanging top, a drawer with a brass pull over an open
    shelf, and grain down the side."""
    wood, wood_d, wood_l = cols
    x1 = WX + 22
    ink = hx("2a1c10")
    R.box(img, WX, x1 - 0.5, 0, 2.5, z0 + 0.5, z1 - 0.5, mul(wood_d, 0.75), top=wood_d, side=mul(wood_d, 0.6))
    R.box(img, WX, x1, 2.5, 24, z0, z1, wood, top=wood_l, side=wood_d)
    rnd = random.Random(seed)
    for i in range(6):
        y0 = 4 + i * 3.4 + rnd.uniform(-0.6, 0.6)
        ph = rnd.uniform(0, 6)
        pts = [R.P(x1, y0 + 0.5 * math.sin(z * 0.45 + ph), z) for z in _frange(z0 + 0.8, z1 - 0.8, 1.5)]
        d.line(pts, fill=mul(wood_d, rnd.uniform(0.78, 0.9)))
    R.line(img, (x1, 2.5, z1), (x1, 24, z1), mul(wood_l, 1.05))
    R.box(img, WX, x1 + 1, 24, 26.5, z0 - 0.5, z1 + 1, mul(wood_l, 0.92), top=wood_l, side=mul(wood_d, 1.12))
    R.line(img, (WX, 26.5, z1 + 1), (x1 + 1, 26.5, z1 + 1), mul(wood_l, 1.3))
    R.line(img, (WX, 24, z1 + 1), (x1 + 1, 24, z1 + 1), mul(wood_d, 0.7))
    # the drawer, its bevelled face and pull
    R.quad(img, [(WX + 2, 14, z1), (x1 - 2, 14, z1), (x1 - 2, 22.5, z1), (WX + 2, 22.5, z1)], ink)
    R.quad(img, [(WX + 2.5, 14.5, z1), (x1 - 2.5, 14.5, z1), (x1 - 2.5, 22, z1), (WX + 2.5, 22, z1)],
           mul(wood, 1.08))
    R.line(img, (WX + 2.5, 22, z1), (x1 - 2.5, 22, z1), mul(wood_l, 1.2))
    R.line(img, (WX + 2.5, 14.6, z1), (x1 - 2.5, 14.6, z1), mul(wood_d, 0.85))
    for gy in (16.5, 19.2):
        R.line(img, (WX + 4, gy, z1), (x1 - 5, gy + 0.3, z1), mul(wood, 0.9))
    cx = WX + 11
    R.line(img, (cx - 3, 18.8, z1), (cx + 3, 18.8, z1), hx("8a6a30"), 2)
    R.line(img, (cx - 3, 19.4, z1), (cx + 3, 19.4, z1), hx("e8c870"))
    for px_ in (cx - 3.5, cx + 3.5):
        R.line(img, (px_, 18.2, z1), (px_, 19.8, z1), hx("5a4420"))
    # the open shelf below
    R.quad(img, [(WX + 2, 4.5, z1), (x1 - 2, 4.5, z1), (x1 - 2, 12.5, z1), (WX + 2, 12.5, z1)], hx("1e140a"))
    R.quad(img, [(WX + 2, 11, z1), (x1 - 2, 11, z1), (x1 - 2, 12.5, z1), (WX + 2, 12.5, z1)], hx("120c06"))
    R.line(img, (WX + 2, 4.5, z1), (x1 - 2, 4.5, z1), mul(wood_l, 1.15))


def _bedroom_lamp(img, d, base, k, lit):
    """A table lamp: brass foot, a glazed urn, brass stem with a knuckle and switch, and a pleated drum shade."""
    x, y = base
    top = y + 27 * k  # a squat bedside lamp: the switch and shade sit almost straight on the urn's collar
    brass, brass_d, brass_l = hx("a88a44"), hx("5e4a24"), hx("ecd48e")
    d.ellipse([x - 6 * k, y - 2 * k, x + 6 * k, y + 2 * k], fill=brass_d)
    d.ellipse([x - 5 * k, y - 3 * k, x + 5 * k, y + 1 * k], fill=brass)
    d.line([(x - 4 * k, y - 2 * k), (x + 1 * k, y - 3 * k)], fill=brass_l)
    glaze, glaze_d, glaze_l = hx("4a6a78"), hx("2a404c"), hx("8cb0bc")
    d.ellipse([x - 5 * k, y - 17 * k, x + 5 * k, y - 3 * k], fill=glaze)
    d.chord([x - 5 * k, y - 17 * k, x + 5 * k, y - 3 * k], 290, 70, fill=glaze_d)
    d.arc([x - 4 * k, y - 15 * k, x + 2 * k, y - 5 * k], 150, 230, fill=glaze_l)
    d.line([(x - 5 * k, y - 10 * k), (x + 5 * k, y - 10 * k)], fill=hx("c8b070"))
    d.rectangle([x - 2 * k, y - 20 * k, x + 2 * k, y - 16 * k], fill=brass)
    d.line([(x - 2 * k, y - 20 * k), (x + 2 * k, y - 20 * k)], fill=brass_l)
    d.rectangle([x - 1, top - 48 * k, x + 1, y - 20 * k], fill=brass)
    d.line([(x - 1, top - 48 * k), (x - 1, y - 20 * k)], fill=brass_l)
    d.line([(x + 1, top - 48 * k), (x + 1, y - 20 * k)], fill=brass_d)
    d.rectangle([x - 2.5 * k, top - 52 * k, x + 2.5 * k, top - 47 * k], fill=brass_d)
    d.line([(x + 2.5 * k, top - 49 * k), (x + 4.5 * k, top - 49 * k)], fill=brass)
    if lit:  # painted bright so the night grade leaves it glowing warm
        light(img, "ellipse", [x - 26 * k, top - 80 * k, x + 26 * k, y - 30 * k], hx("fff4d0"), 0.5, 8)
        d.line([(x + 3 * k, top - 49 * k), (x + 3 * k, top - 44 * k)], fill=brass_d)
        d.point((x + 3 * k, top - 43 * k), fill=brass_l)
    body, pleat, rim, inside = ((hx("fffff0"), hx("efe2bc"), hx("e8c080"), hx("fff8d8")) if lit else
                                (hx("c8bca4"), hx("a89c84"), hx("8a7e68"), hx("6a604e")))
    shade = [(x - 10 * k, top - 50 * k), (x + 10 * k, top - 50 * k), (x + 8 * k, top - 64 * k), (x - 8 * k, top - 64 * k)]
    d.polygon(shade, fill=body)
    for i in range(1, 10):
        t = i / 10
        if i % 2:
            d.line([(x - 10 * k + 20 * k * t, top - 50 * k), (x - 8 * k + 16 * k * t, top - 64 * k)], fill=pleat)
    d.polygon([(x + 4 * k, top - 50 * k), (x + 10 * k, top - 50 * k), (x + 8 * k, top - 64 * k), (x + 3 * k, top - 64 * k)],
              fill=mul(body, 0.9))
    d.ellipse([x - 8 * k, top - 65.5 * k, x + 8 * k, top - 62.5 * k], fill=inside, outline=rim)
    d.chord([x - 10 * k, top - 52 * k, x + 10 * k, top - 48 * k], 0, 180, fill=rim)
    d.line([(x - 8 * k, top - 63 * k), (x + 8 * k, top - 63 * k)], fill=rim)


def paint_bedroom():
    """Present day, past one in the morning. A double bed side-on, headboard against the left wall: Daniel sits up on
    the near side reading Micah's journal by his lamp; behind him his wife sleeps on the far side, the quilt pulled
    over her head and her lamp off. Returns the picture, Daniel's head and the wife's head (speech anchors)."""
    import math
    import numpy as np
    from .furniture import Room3D

    class Zoomed(Room3D):
        """The camera moved in: world units stay the back-wall pixels of the other rooms, the picture is K times bigger
        about the vanishing point's column."""
        K = 1.3

        def s(self, z):
            return Room3D.s(self, z * self.K) * self.K

        def P(self, x, y, z):
            s = Room3D.s(self, z * self.K)
            return self.vx + (x - self.vx) * self.K * s, self.vy + (self.floor - self.vy) * s - y * self.K * s

    FL = 150  # back-wall floor row
    R = Zoomed(FL, 260, 24, 380)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    WX = 176  # the left wall plane
    ZMAX = 205
    # ---- room: oak floor, painted walls, skirting ----
    floor_boards(img, FL, H, (260, 24), 16, hx("9a7250"), hx("8a6444"), hx("5e4230"), seed=3)
    vgrad(img, (0, 0, W - 1, FL), hx("b4ac9c"), hx("c2baaa"))
    noise(img, (0, 0, W - 1, FL), 3, 5)
    R.quad(img, [(WX, 0, 0), (WX, 200, 0), (WX, 200, ZMAX), (WX, 0, ZMAX)], hx("a49c8c"))
    R.quad(img, [(WX, 0, 0), (W + 60, 0, 0), (W + 60, 4, 0), (WX, 4, 0)], hx("ece6d8"))
    R.quad(img, [(WX, 0, 0), (WX, 4, 0), (WX, 4, ZMAX), (WX, 0, ZMAX)], hx("dcd6c8"))
    d.line([R.P(WX, 0, 0), R.P(WX, 200, 0)], fill=hx("948c7c"))
    # ---- the window on the back wall: blind half down, the night city behind ----
    wx0, wx1, wy0, wy1 = 290, 362, 54, 132
    _bedroom_window(img, d, wx0, wx1, FL - wy1, FL - wy0)
    # ---- a chest of drawers on the back wall: a plant, two photos; a print above it ----
    R.box(img, 368, 418, 0, 30, 0, 16, hx("6a4a32"), top=hx("84603f"), side=hx("4a3222"))
    for y0 in (3, 12, 21):
        R.quad(img, [(370, y0, 16), (416, y0, 16), (416, y0 + 7.5, 16), (370, y0 + 7.5, 16)], None, hx("3a2618"))
        px_, py_ = R.P(393, y0 + 4, 16)
        d.rectangle([px_ - 4, py_, px_ + 4, py_ + 1], fill=hx("c8b080"))
    for y0 in (0, 29.2):
        R.line(img, (368, y0, 16), (418, y0, 16), hx("2e1e12"))
    for x in (369, 417):
        R.line(img, (x, 0, 16), (x, 2.5, 16), hx("2e1e12"), 2)
    _bedroom_plant(img, d, R)
    for fx, fh_, sub in ((392, 9, 0), (404, 7, 1)):
        _bedroom_photo(img, d, R, fx, fh_, sub)
    _bedroom_print(img, d, (398, 26, 452, 80))
    # ---- a framed print on the left wall above the headboard ----
    _bedroom_wall_print(img, d, R, WX)
    # ---- rug ----
    R.quad(img, [(196, 0, 108), (296, 0, 108), (296, 0, 150), (196, 0, 150)], hx("7a3a34"))
    R.quad(img, [(200, 0.05, 111), (292, 0.05, 111), (292, 0.05, 147), (200, 0.05, 147)], None, hx("c8a888"))

    # ---- her nightstand, in the far corner: her lamp is off ----
    wood, wood_d, wood_l = hx("6a4630"), hx("46301e"), hx("86603f")

    def nightstand(z0, z1, lit):
        _bedroom_nightstand(img, d, R, WX, z0, z1, (wood, wood_d, wood_l), seed=int(z0))
        k = R.s((z0 + z1) / 2) / R.s(12)
        base = R.P(WX + 7, 26, (z0 + z1) / 2 - 4)
        _bedroom_lamp(img, d, base, k, lit)
        return base

    nightstand(2, 22, False)
    # ---- the bed: X0 headboard .. X1 foot, Z0 far side (hers) .. Z1 near side (his) ----
    X0, X1, Z0, Z1, TOP_ = WX, WX + 92, 26, 98, 24
    shadow(img, "polygon", [R.P(X0, 0, Z0 - 2), R.P(X1 + 3, 0, Z0 - 2), R.P(X1 + 5, 0, Z1 + 3), R.P(X0, 0, Z1 + 3)],
           0.55, 3)
    R.box(img, X0, X0 + 4, 0, 50, Z0 - 2, Z1 + 2, hx("6a7a8a"), top=hx("808f9e"), side=hx("56646f"))
    for z in range(Z0 + 4, Z1, 12):
        R.line(img, (X0 + 4, 12, z), (X0 + 4, 47, z), hx("56646f"))
    R.box(img, X0 + 4, X1, 3, 11, Z0, Z1, wood, top=wood_l, side=wood_d)
    for x in (X0 + 6, X1 - 3):
        R.line(img, (x, 0, Z1 - 1), (x, 3, Z1 - 1), wood_d, 2)
    R.box(img, X0 + 5, X1 - 1, 11, TOP_, Z0 + 1, Z1 - 1, hx("ece8e0"), top=hx("f6f2ea"), side=hx("cfc9bd"))

    def pillow(x0, x1, z0, z1, y0, y1, lean=0.0):
        """A soft pillow: the hull of a rounded rectangle at its base and its crown, the crown shaded lighter."""
        cx_, cz_, rx_, rz_ = (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2
        base, crown = [], []
        for i in range(36):
            t = i / 36 * 2 * math.pi
            c, s = math.cos(t), math.sin(t)
            ex, ez = cx_ + rx_ * math.copysign(abs(c) ** 0.4, c), cz_ + rz_ * math.copysign(abs(s) ** 0.4, s)
            base.append(R.P(ex, y0, ez))
            crown.append(R.P(ex + lean, y1, ez))
        m = Image.new("L", img.size, 0)
        md = ImageDraw.Draw(m)
        md.polygon(base, fill=255)
        md.polygon(crown, fill=255)
        for p, q in zip(base, crown):
            md.line([p, q], fill=255, width=2)
        img.paste(hx("cfc9be"), mask=m)
        d.polygon(crown, fill=hx("e6e2d8"))
        cc = R.P(cx_ + lean, y1, cz_)
        d.polygon([(cc[0] + (p[0] - cc[0]) * 0.82, cc[1] + (p[1] - cc[1]) * 0.75) for p in crown], fill=hx("f2eee6"))

    pillow(X0 + 5, X0 + 25, Z0 + 3, Z0 + 33, TOP_, 29)                # hers, flat, under the quilt
    pillow(X0 + 5, X0 + 19, Z0 + 41, Z1 - 4, TOP_, 40, lean=1.0)      # his, propped up against the headboard

    # ---- the quilt: a height field over the two of them. On her side it's pulled right up over her head; on his it
    # starts at his waist, its edge folded back ----
    zD, zW = Z0 + 55, Z0 + 18
    QX1 = X1 + 1.5

    def qstart(z):
        t = min(max((z - (Z0 + 34)) / 12.0, 0.0), 1.0)
        return X0 + 6 + 18 * t * t * (3 - 2 * t)

    def hgt(x, z):
        h = TOP_ + 1.5
        h += 5.5 * math.exp(-((x - (X0 + 15)) / 11.0) ** 4 - ((z - (Z0 + 18)) / 16.0) ** 4)  # her pillow
        h += 4.5 * math.exp(-((x - (X0 + 15)) / 5.5) ** 2 - ((z - zW) / 6.0) ** 2)         # her head
        # her body: one long ridge from shoulder to hip, so there's no dip at her waist
        h += 5.5 * math.exp(-((x - (X0 + 44)) / 21.0) ** 4 - ((z - zW) / 9.5) ** 2)
        h += 1.0 * math.exp(-((x - (X0 + 30)) / 6.0) ** 2 - ((z - zW) / 8.0) ** 2)         # shoulder
        h += 2.0 * math.exp(-((x - (X0 + 55)) / 9.0) ** 2 - ((z - zW) / 10.0) ** 2)        # hip
        h += 3.5 * math.exp(-((x - (X0 + 76)) / 8.0) ** 2 - ((z - zW - 7) / 9.0) ** 2)     # drawn-up knees
        h += 2.5 * math.exp(-((x - (X1 - 10)) / 7.0) ** 2 - ((z - zW - 3) / 8.0) ** 2)     # feet
        t = min(max((x - (X0 + 20)) / (X1 - X0 - 24), 0), 1)
        h += (3.6 - 1.2 * t) * math.exp(-((z - zD) / 7.5) ** 2)                            # his legs
        h += 3.5 * math.exp(-((x - (X1 - 9)) / 4.0) ** 2 - ((z - zD) / 6.0) ** 2)          # toes
        return h + 0.35 * math.sin(x * 0.3 + z * 0.2)

    q_dark, q_light = np.array(hx("34506c")), np.array(hx("7c9ab4"))
    L = np.array([-0.45, 0.8, 0.4])
    L /= np.linalg.norm(L)
    step = 1.5
    xs = np.arange(X0 + 6, QX1 + 0.01, step)
    zs = np.arange(Z0 - 1, Z1 + 1.01, step)
    Hm = np.array([[hgt(x, z) for x in xs] for z in zs])

    def qcol(n, seam=False):
        n = n / np.linalg.norm(n)
        k = float(np.clip(n @ L, 0, 1)) ** 1.4
        c = q_dark + (q_light - q_dark) * (0.25 + 0.75 * k)
        return tuple(int(v * (0.9 if seam else 1.0)) for v in c)

    def quilt_rows(rows):
        for j in rows:
            z = zs[j]
            x0 = qstart(z)
            for i in range(len(xs) - 1):
                x = xs[i]
                if x < x0 - step / 2:
                    continue
                n = np.array([-(Hm[j, i + 1] - Hm[j, i]) / step, 1.0, -(Hm[j + 1, i] - Hm[j, i]) / step])
                seam = (x - X0) % 14 < step * 0.99 or (z - Z0) % 14 < step * 0.99
                R.quad(img, [(x, Hm[j, i], z), (x + step, Hm[j, i + 1], z), (x + step, Hm[j + 1, i + 1], z + step),
                             (x, Hm[j + 1, i], z + step)], qcol(n, seam))
            if x0 > X0 + 8:  # on his side the top edge is a folded-back band of sheet
                x1 = qstart(z + step)
                R.quad(img, [(x0 - 2.5, hgt(x0, z) + 0.5, z), (x0 + 2, hgt(x0 + 2, z) + 0.5, z),
                             (x1 + 2, hgt(x1 + 2, z + step) + 0.5, z + step), (x1 - 2.5, hgt(x1, z + step) + 0.5, z + step)],
                       hx("f0ece4"))

    # her side of the bed first, then Daniel sitting up in front of it, then his lap and legs
    split = int(np.searchsorted(zs, zD - 9))
    quilt_rows(range(0, split))
    dan, hand = _bed_figures(R.s(zD))
    seat = R.P(X0 + 13, TOP_ - 1, zD)
    img.paste(dan.convert("RGB"), (int(seat[0]), int(seat[1] - dan.height)), dan)
    dan_head = (int(seat[0] + dan.width * 0.32), int(seat[1] - dan.height))
    quilt_rows(range(split, len(zs) - 1))
    wh = R.P(X0 + 54, hgt(X0 + 54, zW), zW)  # her hip: the one part of her that shows, behind him
    wife_head = (int(wh[0]), int(wh[1]))
    # the drape over the near side and the foot, in soft vertical folds
    for i in range(len(xs) - 1):
        x = xs[i]
        if x < qstart(Z1) - step / 2:
            continue
        f = 0.5 + 0.5 * math.sin(x * 0.5)
        col = tuple(int(v) for v in q_dark + (q_light - q_dark) * (0.18 + 0.3 * f))
        R.quad(img, [(x, Hm[-1, i], Z1 + 1), (x + step, Hm[-1, i + 1], Z1 + 1), (x + step, 7, Z1 + 2 + f),
                     (x, 7, Z1 + 2 + f)], col)
    for j in range(len(zs) - 1):
        z = zs[j]
        f = 0.5 + 0.5 * math.sin(z * 0.45)
        col = tuple(int(v) for v in q_dark + (q_light - q_dark) * (0.3 + 0.3 * f))
        R.quad(img, [(QX1, Hm[j, -1], z), (QX1, Hm[j + 1, -1], z + step), (QX1 + 1 + f, 7, z + step),
                     (QX1 + 1 + f, 7, z)], col)

    # ---- Daniel's nightstand, on his side in the near corner: the alarm clock and his lamp, lit ----
    lamp = nightstand(Z1 + 6, Z1 + 26, True)
    R.box(img, WX + 10.5, WX + 20.5, 26, 31, Z1 + 14, Z1 + 17, hx("161616"), top=hx("343434"), side=hx("0c0c0c"))
    c0, c1 = R.P(WX + 11.5, 30, Z1 + 17), R.P(WX + 19.5, 27, Z1 + 17)
    d.rectangle([c0[0], c0[1], c1[0], c1[1]], fill=hx("200806"))
    R.line(img, (WX + 10.5, 31, Z1 + 17), (WX + 20.5, 31, Z1 + 17), hx("4a4a4a"))
    for bxx in (WX + 13, WX + 17):
        R.line(img, (bxx, 31.2, Z1 + 15), (bxx + 1.5, 31.2, Z1 + 15), hx("6a6a6a"))
    clk = (round((c0[0] + c1[0]) / 2) - 6, round((c0[1] + c1[1]) / 2) - 2)
    # a paperback on the open shelf
    R.box(img, WX + 3, WX + 15, 5, 7.5, Z1 + 12, Z1 + 21, hx("e8e0cc"), top=hx("8a2a22"), side=hx("c8bea8"))

    # ---- the journal in Daniel's hands: open, its brown leather back towards us ----
    bx, by = seat[0] + hand[0], seat[1] + hand[1]
    k = R.s(zD) / 1.5
    bk = lambda pts: [(bx + px * k, by + py * k) for px, py in pts]
    d.polygon(bk([(-3, 3), (1, 4), (7, -12), (3, -13)]), fill=hx("f2ead6"))
    d.polygon(bk([(1, 4), (5, 4), (11, -11), (7, -12)]), fill=hx("6a3a22"))
    d.line(bk([(1, 4), (7, -12)]), fill=hx("3a2014"))
    d.ellipse(bk([(-1, -2), (5, 4)]), fill=hx("e0b090"))

    # ---- night grade: cold everywhere, warm in a pool around Daniel's lamp ----
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot((xx - lamp[0]) / 1.25, (yy - lamp[1]) * 1.1)
    w = np.exp(-(dist / 120.0) ** 1.6)[..., None]
    night, warm = np.array([0.36, 0.40, 0.62]), np.array([1.05, 0.84, 0.6])
    arr = np.asarray(img, dtype=np.float32) * (night + (warm - night) * w)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    glyphs = {"1": ("01", "11", "01", "01", "01"), ":": ("0", "1", "0", "1", "0"),
              "4": ("101", "101", "111", "001", "001"), "7": ("111", "001", "010", "010", "010")}
    gx = clk[0]
    for ch in "1:47":  # the alarm clock reads 1:47
        g = glyphs[ch]
        for r, row in enumerate(g):
            for c, on in enumerate(row):
                if on == "1":
                    d.point((gx + c, clk[1] + r), fill=hx("ff4a30"))
        gx += len(g[0]) + 1
    vignette(img, 0.5, (8, 8, 24), 40)
    return img, dan_head, wife_head


def build_bedroom():
    img, dan, wife = paint_bedroom()
    px = pixelize(img, palette_of(img, 112))
    save(px, "rooms", "bedroom.png")
    print("bedroom: Daniel's head", dan, "wife's head", wife)
    return px

def build():
    build_rose()
    build_road()
    build_office()
    build_bedroom()
