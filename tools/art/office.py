"""Micah Jones' office: a cramped, lamp-lit detective office on a rainy night."""
from PIL import Image, ImageDraw
import math
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, city, save, floor_boards, sunburst)

FLOOR = 128


def walls(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("3c3a2c"), hx("2a2a22"))
    # vertical stripe wallpaper
    for x in range(0, W, 8):
        d.line([(x, 0), (x, FLOOR)], fill=hx("34322a"))
        d.line([(x + 3, 0), (x + 3, FLOOR)], fill=hx("424032"))
    noise(img, (0, 0, W - 1, FLOOR), 4, 1)
    # picture rail + wainscot
    d.rectangle([0, 12, W - 1, 14], fill=hx("4a3424"))
    d.line([(0, 12), (W, 12)], fill=hx("6a4c34"))
    vgrad(img, (0, 96, W - 1, FLOOR), hx("4a3020"), hx("2e1c12"))
    for x in range(0, W, 30):
        d.rectangle([x + 3, 100, x + 26, FLOOR - 5], outline=hx("3a2416"))
        d.line([(x + 4, 101), (x + 25, 101)], fill=hx("5c3c28"))
    d.rectangle([0, 95, W - 1, 97], fill=hx("5a3a26"))
    d.rectangle([0, FLOOR - 3, W - 1, FLOOR], fill=hx("24160e"))
    # water stain + crack
    shadow(img, "ellipse", [250, 0, 300, 30], 0.25, 8, hx("806040"))
    d.line([(420, 14), (424, 26), (421, 34), (426, 44)], fill=hx("26241c"))


def floor(img):
    floor_boards(img, FLOOR, H - 1, (240, -260), 20, hx("4a2e1c"), hx("3a2416"), hx("24140c"), 3)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 2)
    d = ImageDraw.Draw(img)
    # threadbare rug in perspective
    rug = [(150, 158), (360, 158), (392, 196), (118, 196)]
    d.polygon(rug, fill=hx("5a1c1c"))
    d.polygon([(158, 162), (352, 162), (380, 192), (130, 192)], outline=hx("a07040"))
    d.polygon([(168, 166), (342, 166), (366, 188), (144, 188)], fill=hx("4a1818"), outline=hx("7a4a2a"))
    for i in range(5):
        x = 190 + i * 32
        d.polygon([(x, 172), (x + 8, 177), (x, 182), (x - 8, 177)], fill=hx("8a6a3a"))
    for x in range(120, 392, 4):
        d.line([(x, 196), (x, 198)], fill=hx("b09060"))
    noise(img, (118, 158, 392, 198), 6, 4)


DOOR = (32, 18, 84, 127)
DOOR_BOX = (27, 13 + TOP, 90, 140 + TOP)


def door(img, state="closed"):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    if state != "closed":
        d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 8], fill=hx("3a2416"))
        vgrad(img, (x0, y0, x1, y1), hx("6a6458"), hx("3a342c"))
        d.polygon([(x0 + 4, y1 - 10), (x1 - 4, y1 - 10), (x1 - 10, y1), (x0 + 10, y1)], fill=hx("5a4634"))
        d.ellipse([(x0 + x1) // 2 - 6, y0 + 8, (x0 + x1) // 2 + 6, y0 + 18], fill=hx("f8e8b0"))
        d.rectangle([x0 + 8, y0 + 28, x1 - 18, y1 - 16], fill=hx("2e2a24"))
        if state == "ajar":
            # hinged on the left; the knob edge swings in first, opening a gap on the right
            fx = x1 - 18
            d.polygon([(x0, y0), (fx, y0 - 2), (fx, y1 + 2), (x0, y1)], fill=hx("4e321c"))
            vgrad(img, (x0 + 5, y0 + 6, fx - 5, 70), hx("c8c098"), hx("8a8a6a"))
            noise(img, (x0 + 5, y0 + 6, fx - 5, 70), 6, 5)
            d.rectangle([x0 + 5, y0 + 6, fx - 5, 70], outline=hx("2a180c"))
            for py in (78, 102):
                d.rectangle([x0 + 6, py, fx - 6, py + 18], outline=hx("2e1c0e"))
            d.line([(fx, y0 - 2), (fx, y1 + 2)], fill=hx("2a180c"))
            # the face is foreshortened to ~2/3 of its width, so the knob narrows with it
            d.ellipse([fx - 8, 82, fx - 5, 87], fill=hx("c8a050"))
            d.point((fx - 7, 83), fill=hx("fff0b0"))
        else:
            d.rectangle([x0, y0, x0 + 9, y1], fill=hx("4e321c"))
            d.rectangle([x0 + 1, y0 + 8, x0 + 7, 66], fill=hx("c8c098"))
            d.line([(x0 + 9, y0), (x0 + 9, y1)], fill=hx("2a180c"))
            # swung wide open and seen almost edge-on: the knob is a thin sliver
            d.rectangle([x0 + 3, 82, x0 + 4, 86], fill=hx("c8a050"))
            d.point((x0 + 3, 83), fill=hx("fff0b0"))
        d.line([(x0 + 1, y1), (x1 - 1, y1)], fill=hx("d8c080"))
        return
    x0, y0, x1, y1 = DOOR
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1], fill=hx("3a2416"))
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y0 - 2], fill=hx("5a3a24"))
    vgrad(img, (x0, y0, x1, y1), hx("5a3a22"), hx("3e2616"))
    d.rectangle([x0, y0, x1, y1], outline=hx("2a180c"))
    # frosted glass with backlit corridor
    vgrad(img, (x0 + 7, y0 + 7, x1 - 7, 70), hx("c8c098"), hx("8a8a6a"))
    noise(img, (x0 + 7, y0 + 7, x1 - 7, 70), 6, 5)
    d.rectangle([x0 + 7, y0 + 7, x1 - 7, 70], outline=hx("2a180c"))
    for t, y in (("MICAH", 34), ("JONES", 44), ("P.I.", 56)):
        text(img, ((x0 + x1) // 2, y), t, hx("1e1a14"), size=8, mirror=True)
    # silhouette of a waiting stranger? no - empty corridor bulb glow
    light(img, "ellipse", [x0 + 12, y0 + 10, x1 - 12, 50], hx("f8e8b0"), 0.35, 8)
    # lower panels
    for py in (78, 102):
        d.rectangle([x0 + 8, py, x1 - 8, py + 18], outline=hx("2e1c0e"))
        d.line([(x0 + 9, py + 1), (x1 - 9, py + 1)], fill=hx("6a4a2e"))
    d.ellipse([x1 - 12, 82, x1 - 7, 87], fill=hx("c8a050"))
    d.point((x1 - 11, 83), fill=hx("fff0b0"))
    # light leaking under the door
    d.line([(x0 + 1, y1), (x1 - 1, y1)], fill=hx("d8c080"))
    light(img, "rect", [x0, y1, x1, y1 + 10], hx("806830"), 0.35, 4)


def cabinet(img, whiskey=True):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 108, 60, 146, 127
    hgrad(img, (x0, y0, x1, y1), hx("5a5e5a"), hx("3a3e3a"))
    d.rectangle([x0, y0, x1, y1], outline=hx("1e201e"))
    for i in range(3):
        y = y0 + 4 + i * 21
        d.rectangle([x0 + 3, y, x1 - 3, y + 18], outline=hx("2a2e2a"))
        d.line([(x0 + 4, y + 1), (x1 - 4, y + 1)], fill=hx("7a7e78"))
        d.rectangle([x0 + 14, y + 4, x1 - 14, y + 6], fill=hx("b0a888"))
        d.rectangle([x0 + 16, y + 9, x1 - 16, y + 12], fill=hx("d8d0b0"))
    noise(img, (x0, y0, x1, y1), 4, 9)
    if whiskey:
        bottle(d, 115, 36)
    # diploma
    d.rectangle([110, 20, 144, 42], fill=hx("6a4a24"))
    d.rectangle([113, 23, 141, 39], fill=hx("d8cca8"))
    for y in (27, 31, 34):
        d.line([(117, y), (137, y)], fill=hx("6a6050"))
    d.ellipse([124, 34, 130, 39], fill=hx("a02020"))
    shadow(img, "rect", [146, 62, 154, 127], 0.5, 3)


def bottle(d, x, y):
    """The whiskey bottle, its cap's top-left corner at (x + 2, y): 9 px wide, 24 px tall."""
    d.rectangle([x, y + 8, x + 8, y + 23], fill=hx("6a3a14"))
    d.rectangle([x + 2, y + 2, x + 6, y + 8], fill=hx("6a3a14"))
    d.rectangle([x + 2, y, x + 6, y + 2], fill=hx("1a1a1a"))
    d.rectangle([x + 1, y + 13, x + 7, y + 18], fill=hx("d8c890"))
    d.line([(x + 1, y + 9), (x + 1, y + 22)], fill=hx("c08040"))


def cup(d, x, y):
    """The tin cup of whiskey (the office_cup sprite) with its top-left corner at (x, y)."""
    d.rectangle([x + 1, y + 2, x + 7, y + 10], fill=hx("b8b4a4"))
    d.rectangle([x + 2, y + 3, x + 6, y + 5], fill=hx("a86024"))
    d.rectangle([x + 7, y + 4, x + 9, y + 8], outline=hx("b8b4a4"))
    d.line([(x + 2, y + 9), (x + 6, y + 9)], fill=hx("e0d8bc"))


# Act 3: the bottle and the cup end up on the desk, between the lamp and the case files (art coordinates)
DESK_BOTTLE = (214, 80)
DESK_CUP = (224, 92)


def coat_rack(img, hat=True):
    d = ImageDraw.Draw(img)
    d.line([(162, 30), (162, 126)], fill=hx("2a1a10"), width=2)
    d.polygon([(154, 127), (170, 127), (162, 120)], fill=hx("2a1a10"))
    for dx in (-6, 6):
        d.line([(162, 32), (162 + dx, 28)], fill=hx("2a1a10"))
    # spare fedora and scarf
    if hat:
        d.ellipse([150, 28, 172, 33], fill=hx("2a2a30"))
        d.rectangle([155, 22, 168, 30], fill=hx("2a2a30"))
        d.line([(155, 28), (168, 28)], fill=hx("6a1a1a"))
    d.polygon([(158, 34), (166, 34), (168, 70), (163, 68), (160, 72), (157, 40)], fill=hx("6a2420"))


def clock(img):
    d = ImageDraw.Draw(img)
    cx, cy, r = 230, 38, 13
    sunburst(d, cx, cy, r + 6, 24, hx("a08040"), hx("6a5228"), 0, 2 * math.pi)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hx("2a2018"))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=hx("e0d4b0"))
    for i in range(12):
        a = i * math.pi / 6
        d.point((cx + (r - 4) * math.cos(a), cy + (r - 4) * math.sin(a)), fill=hx("2a2018"))
    d.line([(cx, cy), (cx + 5, cy - 4)], fill=hx("1a1410"))  # ~1:50 am
    d.line([(cx, cy), (cx - 1, cy - 8)], fill=hx("1a1410"))


def desk(img):
    d = ImageDraw.Draw(img)
    # chair behind desk
    d.rectangle([232, 70, 266, 104], fill=hx("3a1e14"))
    d.rounded_rectangle([234, 66, 264, 100], 6, fill=hx("5a2a1c"))
    for x in range(238, 262, 6):
        for y in range(70, 98, 7):
            d.point((x, y), fill=hx("c09050"))
    light(img, "ellipse", [236, 66, 252, 96], hx("806040"), 0.3, 4)
    # top
    d.polygon([(168, 110), (348, 110), (344, 101), (172, 101)], fill=hx("6a3e22"))
    d.line([(172, 101), (344, 101)], fill=hx("8a5a34"))
    d.rectangle([168, 110, 348, 112], fill=hx("3a2010"))
    # body
    vgrad(img, (176, 113, 340, 152), hx("4e2c18"), hx("361e10"))
    noise(img, (176, 113, 340, 152), 4, 11)
    for px0 in (182, 284):
        d.rectangle([px0, 116, px0 + 50, 150], outline=hx("24140a"))
        for dy in (116, 133):
            d.rectangle([px0 + 3, dy + 2, px0 + 47, dy + 14], outline=hx("2a160a"))
            d.line([(px0 + 4, dy + 3), (px0 + 46, dy + 3)], fill=hx("6a4024"))
            d.rectangle([px0 + 21, dy + 7, px0 + 29, dy + 9], fill=hx("b8904a"))
    d.rectangle([236, 116, 280, 150], fill=hx("2a160c"))
    shadow(img, "rect", [176, 150, 344, 160], 0.55, 4)


def desk_props(img, lamp_on=True, storm=False):
    d = ImageDraw.Draw(img)
    # banker's lamp
    d.rectangle([194, 92, 198, 101], fill=hx("b8904a"))
    d.ellipse([188, 98, 204, 102], fill=hx("8a6a34"))
    d.chord([184, 82, 210, 96], 180, 360, fill=hx("1e6a3a" if lamp_on else "16402a"))
    d.line([(186, 89), (208, 89)], fill=hx("4aa060" if lamp_on else "24583a"))
    # stack of case files, typewriter-ish papers
    d.polygon([(238, 96), (262, 95), (264, 101), (236, 102)], fill=hx("c8bc98"))
    d.polygon([(240, 93), (260, 92), (262, 97), (238, 98)], fill=hx("e0d8b8"))
    d.line([(244, 95), (256, 94)], fill=hx("6a6050"))
    # ashtray with smoking cigarette
    d.ellipse([294, 97, 308, 102], fill=hx("4a4a50"))
    d.ellipse([297, 98, 305, 100], fill=hx("1e1e22"))
    d.line([(303, 98), (309, 96)], fill=hx("e8e0d0"))
    d.point((309, 96), fill=hx("ff6020"))
    for i, (sx, sy) in enumerate([(310, 92), (311, 86), (309, 80), (311, 74)]):
        d.point((sx, sy), fill=mix(hx("8a8a90"), hx("3c3a2c"), i / 4))
    # telephone
    d.rectangle([316, 94, 330, 101], fill=hx("16161a"))
    d.ellipse([318, 90, 328, 98], fill=hx("16161a"))
    d.line([(314, 88), (332, 88)], fill=hx("16161a"), width=3)
    d.ellipse([320, 93, 326, 97], fill=hx("c8c0a8"))
    if storm:
        return
    if not lamp_on:
        bottle(d, *DESK_BOTTLE)
        cup(d, *DESK_CUP)
        return
    # lamp pool of light
    light(img, "ellipse", [150, 70, 260, 130], hx("f0d890"), 0.55, 14)
    light(img, "polygon", [(186, 92), (210, 92), (232, 104), (166, 104)], hx("fff0c0"), 0.5, 3)


WINDOW = (352, 16, 470, 98)


def lights_out(img):
    """Act 3: the lamp is off. The room sinks into blue shadow; only the window and its neon spill stay lit."""
    x0, y0, x1, y1 = WINDOW
    glass = img.crop((x0, y0, x1 + 1, y1 + 1))
    shadow(img, "rect", [0, 0, W, H], 0.72, 0, hx("6a6a9a"))
    img.paste(glass, (x0, y0))
    light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("4a6aa8"), 0.2, 10)
    light(img, "ellipse", [380, 110, 480, 200], hx("ff3030"), 0.14, 20)
    # a red rim of HOTEL light catching the bottle on the desk
    bx, by = DESK_BOTTLE
    light(img, "rect", [bx + 6, by + 8, bx + 8, by + 22], hx("ff4a4a"), 0.35, 1)


def window(img, neon=True):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 352, 16, 470, 98
    # the rain is animated in-game (Rain node in office.tscn)
    city(img, (x0, y0, x1, y1), seed=11, lit=0.28 if neon else 0.0, rain=False)
    # red neon HOTEL sign on the building across (dead in the storm blackout)
    d.rectangle([428, 44, 438, 90], fill=hx("1a0c10"))
    for i, ch in enumerate("HOTEL"):
        text(img, (433, 49 + i * 9), ch, hx("ff4a4a" if neon else "3a2226"), size=8)
    if neon:
        light(img, "rect", [420, 40, 446, 94], hx("ff2a2a"), 0.35, 6)
    # frame, mullion, blinds half-drawn
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=hx("2a1a10"), width=4)
    d.line([(411, y0), (411, y1)], fill=hx("2a1a10"), width=3)
    d.line([(x0, 56), (x1, 56)], fill=hx("2a1a10"), width=2)
    for y in range(y0, 46, 3):
        d.line([(x0, y), (x1, y)], fill=hx("8a8270"))
        d.line([(x0, y + 1), (x1, y + 1)], fill=hx("5a5446"))
    d.line([(x0 + 10, 46), (x0 + 10, 60)], fill=hx("c8c0a0"))
    d.rectangle([x0 - 8, y1 + 3, x1 + 8, y1 + 6], fill=hx("4a3020"))
    # radiator
    for x in range(372, 452, 6):
        d.rounded_rectangle([x, 104, x + 4, 126], 2, fill=hx("6a6a64"))
    d.rectangle([370, 120, 454, 122], fill=hx("4a4a46"))
    # cold neon spill + blind stripes on the floor and wall
    light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("4a6aa8"), 0.18, 10)
    for i in range(6):
        y = 150 + i * 8
        light(img, "polygon", [(330 + i * 4, y), (440 + i * 6, y), (444 + i * 6, y + 3), (334 + i * 4, y + 3)],
              hx("8090c0"), 0.22, 1)
    if neon:
        light(img, "ellipse", [380, 110, 480, 200], hx("ff3030"), 0.12, 20)


def paint(drawer=None, door_state="closed", lamp_on=True):
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    door(img, door_state)
    cabinet(img, whiskey=lamp_on)
    coat_rack(img)
    clock(img)
    window(img)
    desk(img)
    desk_props(img, lamp_on)
    if drawer is not None:
        open_drawer(img, drawer)
    if not lamp_on:
        lights_out(img)
    img = tall(img, ceiling)
    if not lamp_on:
        shadow(img, "rect", [0, 0, W, TOP], 0.72, 0, hx("6a6a9a"))
    vignette(img, 0.55)
    return img


# =====================================================================================================================
# The storm after the alley: the power is out on the whole block, lamp and HOTEL sign dead. The cup and Micah's hat
# are on the desk (the bottle is in his hand until he sets it down). Painted twice: black, and under a lightning flash.
# =====================================================================================================================
STORM_HAT = (240, 89)       # art coordinates of the hat's bounding box top-left (22 x 13)
STORM_HAT_BOX = (238, 87 + TOP, 264, 103 + TOP)
STORM_BOTTLE_BOX = (212, 78 + TOP, 225, 105 + TOP)
# the glass below the blinds, where the lightning shows the reflection (screen coordinates)
STORM_GLASS_BOX = (348, 46 + TOP, 474, 102 + TOP)


def fedora(d, x, y):
    """Micah's fedora lying on the desk, its top-left at (x, y): 22 x 13."""
    felt, band, dark = hx("6e4a30"), hx("1a120e"), hx("4a3020")
    d.ellipse([x, y + 7, x + 21, y + 12], fill=dark)
    d.ellipse([x, y + 6, x + 21, y + 11], fill=felt)
    d.rounded_rectangle([x + 5, y, x + 16, y + 9], 3, fill=felt)
    d.line([(x + 9, y + 1), (x + 11, y + 3)], fill=dark)  # the pinch in the crown
    d.rectangle([x + 5, y + 6, x + 16, y + 7], fill=band)
    d.line([(x + 6, y + 1), (x + 6, y + 5)], fill=hx("8a6444"))


def storm_desk(img, hat=True, bottle=False):
    d = ImageDraw.Draw(img)
    cup(d, *DESK_CUP)
    if bottle:
        bottle_(d, *DESK_BOTTLE)
    if hat:
        fedora(d, *STORM_HAT)


bottle_ = bottle


def _bolt(img, seed):
    """A forked lightning bolt in the sky above the roofs, behind the window glass."""
    import random
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    x, y = 384, 47
    pts = [(x, y)]
    while y < 74:
        x += rng.randint(-4, 3)
        y += rng.randint(3, 6)
        pts.append((x, y))
    d.line(pts, fill=hx("f4f6ff"), width=1)
    fx, fy = pts[len(pts) // 2]
    d.line([(fx, fy), (fx - 6, fy + 5), (fx - 8, fy + 11)], fill=hx("c8d4ff"))
    light(img, "polygon", [(p[0] - 1, p[1]) for p in pts] + [(p[0] + 2, p[1]) for p in pts[::-1]], hx("c8d4ff"), 0.5, 3)


def paint_storm(lit=False, hat=True, bottle=False, door_state="closed"):
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    door(img, door_state)
    cabinet(img, whiskey=False)
    coat_rack(img, hat=False)
    clock(img)
    window(img, neon=False)
    desk(img)
    desk_props(img, lamp_on=False, storm=True)
    storm_desk(img, hat, bottle)
    x0, y0, x1, y1 = WINDOW
    if lit:
        # the sky flares white behind the roofs; the flash pours in cold and flat, hard on the side facing the glass
        sky = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1), hx("b8c4e8"))
        glass = img.crop((x0, y0, x1 + 1, y1 + 1))
        img.paste(Image.blend(glass, sky, 0.3), (x0, y0))
        _bolt(img, 3)
        window_frame(img)
        shadow(img, "rect", [0, 0, W, H], 0.4, 0, hx("5a6a9a"))
        # the window's shape thrown across the floor, the mullion and bar as dark crosses in it
        light(img, "polygon", [(352, 98), (470, 98), (470, 240), (250, 240)], hx("c8d8ff"), 0.22, 6)
        shadow(img, "polygon", [(409, 98), (413, 98), (392, 240), (384, 240)], 0.25, 2)
        light(img, "rect", [x0 - 6, y0 - 6, x1 + 6, y1 + 6], hx("e8eeff"), 0.18, 6)
    else:
        window_frame(img)
        glass = img.crop((x0, y0, x1 + 1, y1 + 1))
        shadow(img, "rect", [0, 0, W, H], 0.9, 0, hx("2a2a4a"))
        img.paste(Image.blend(glass, Image.new("RGB", glass.size, hx("10141e")), 0.7), (x0, y0))
        light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("3a4a78"), 0.12, 10)
    img = tall(img, ceiling)
    shadow(img, "rect", [0, 0, W, TOP], 0.45 if lit else 0.9, 0, hx("5a6a9a" if lit else "2a2a4a"))
    vignette(img, 0.6)
    return img


def window_frame(img):
    """The window's frame, mullion and blinds again, over a repainted glass."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WINDOW
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=hx("2a1a10"), width=4)
    d.line([(411, y0), (411, y1)], fill=hx("2a1a10"), width=3)
    d.line([(x0, 56), (x1, 56)], fill=hx("2a1a10"), width=2)
    for y in range(y0, 46, 3):
        d.line([(x0, y), (x1, y)], fill=hx("8a8270"))
        d.line([(x0, y + 1), (x1, y + 1)], fill=hx("5a5446"))


def _bez(p0, p1, p2, n=24):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in (i / (n - 1) for i in range(n))]


def _tube(d, pts, r0, r1, fill=255, S=4):
    """Circles along a polyline (crop pixels), radius tapering r0 -> r1, drawn on a canvas S times larger."""
    import numpy as np
    pts = [np.array(p, float) for p in pts]
    seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]
    total, run = max(sum(seg), 1e-6), 0.0
    for a, b, L in zip(pts, pts[1:], seg):
        for i in range(max(2, int(L * S * 2))):
            u = i / max(1, int(L * S * 2) - 1)
            x, y = (a + (b - a) * u) * S
            r = (r0 + (r1 - r0) * (run + L * u) / total) * S
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
        run += L


def _poly(d, pts, fill=255, S=4):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)


def _ell(d, cx, cy, rx, ry, fill=255, S=4):
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)


def reflection(glass, stage):
    """The lightning shows Micah in the window glass, from the waist up (the sill cuts him off), and the thing holding
    him. stage 1: a horned shadow looms behind his reflection, one claw over his shoulder and an arm across his chest;
    stage 2: it bows over him, a hand over his mouth, and the dark rises up him to the neck.
    glass: the lit crop of STORM_GLASS_BOX (RGB); returns it with the reflection painted on."""
    from .sprites import MICAH_HATLESS, FW, FH, figure, pose
    import numpy as np
    import random
    S = 4
    rng = random.Random(stage * 7)
    base = glass.convert("RGBA")
    w, h = base.size
    sill = h - 5          # the glass ends on the sill (art y 98)
    cx = 92               # centred in the right pane
    # Micah's reflection: faced towards the room, cut off at the waist, cold and translucent
    fig = figure(MICAH_HATLESS, pose(8), FW, FH)
    fig = fig.crop(fig.getbbox())
    bust = fig.crop((0, 0, fig.width, int(fig.height * 0.48)))
    k = 31 / bust.height
    bust = bust.resize((round(bust.width * k), 31), Image.BOX)
    a = np.array(bust).astype(float)
    tone = a[..., :3].mean(axis=2, keepdims=True)
    a[..., :3] = tone * np.array([0.62, 0.68, 0.9]) + np.array([16, 20, 34])
    a[..., 3] = np.where(a[..., 3] > 90, 225 if stage == 1 else 120, 0)
    bust = Image.fromarray(a.clip(0, 255).astype("uint8"))
    bx, by = cx - bust.width // 2, sill - bust.height
    top = by  # his head's top

    # --- the demon, painted 4x and brought down ---------------------------------------------------------------------
    big = (w * S, h * S)
    body, arms = Image.new("L", big, 0), Image.new("L", big, 0)
    detail = Image.new("L", big, 0)   # lighter muscle and horn ridges, inside the silhouette
    db, da, dd = ImageDraw.Draw(body), ImageDraw.Draw(arms), ImageDraw.Draw(detail)
    hx_, hy = (cx - 9, top + 4) if stage == 1 else (cx, top - 1)  # at his ear; then over him
    sy = top + 6 if stage == 1 else top + 5       # shoulder line, hunched up level with his chin
    # skull: long, narrow, a pointed jaw, a heavy brow
    _ell(db, hx_, hy, 4.6, 5.4)
    _poly(db, [(hx_ - 4, hy + 1), (hx_ + 4, hy + 1), (hx_ + 1.6, hy + 9), (hx_ - 1.6, hy + 9)])
    _poly(db, [(hx_ - 5.5, hy - 1), (hx_ + 5.5, hy - 1), (hx_ + 4, hy + 1.5), (hx_ - 4, hy + 1.5)])
    for k_ in (-1, 1):  # ram-curled horns, thick at the skull, swept out and up to a point
        curve = (_bez((hx_ + k_ * 3, hy - 3), (hx_ + k_ * 12, hy - 4), (hx_ + k_ * 11, hy - 15)) if stage == 1 else
                 _bez((hx_ + k_ * 3, hy - 3), (hx_ + k_ * 9, hy - 9), (hx_ + k_ * 15, hy - 3)))
        _tube(db, curve, 2.1, 0.35)
        for i in range(3, len(curve) - 4, 3):  # ridges
            x, y = curve[i]
            _ell(dd, x, y, 1.3, 0.35)
    # neck and great hunched shoulders, the trunk spreading to the sill
    _poly(db, [(hx_ - 3, hy + 6), (hx_ + 3, hy + 6), (cx + 6, sy), (cx - 6, sy)])
    for k_ in (-1, 1):
        _ell(db, cx + k_ * 15, sy + 3, 9, 6.5)
        _ell(dd, cx + k_ * 16, sy + 1, 4.5, 2, fill=255)  # the deltoid catching the light
    spread = 27 if stage == 1 else 31
    _poly(db, [(cx - 22, sy + 2), (cx + 22, sy + 2), (cx + spread, h), (cx - spread, h)])
    # smoke curling off the flanks: the thing doesn't end, it frays
    for k_ in (-1, 1):
        for j in range(3):
            y0 = sy + 9 + j * 8 + rng.uniform(-1, 1)
            x0 = cx + k_ * (22 + (y0 - sy) * (spread - 22) / (h - sy))
            end = (x0 + k_ * rng.uniform(7, 11), y0 - rng.uniform(8, 13))
            _tube(db, _bez((x0 - k_ * 3, y0 + 2), (x0 + k_ * 7, y0), end), 2.2, 0.2)
    # ribs and the line of the arm along the flanks
    for k_ in (-1, 1):
        for j in range(3):
            y = sy + 12 + j * 4
            _tube(dd, _bez((cx + k_ * 13, y), (cx + k_ * 18, y - 1.5), (cx + k_ * 21, y + 1)), 0.35, 0.25)

    def claw(d, start, tips, r=0.75):
        for tip in tips:
            mid = ((start[0] + tip[0]) / 2 + (tip[1] - start[1]) * 0.15, (start[1] + tip[1]) / 2 - 1)
            _tube(d, _bez(start, mid, tip), r, 0.15)

    if stage == 1:
        # the far arm comes round his waist and across his chest, its claws spread over his heart
        _tube(da, [(cx - 17, sy + 4), (cx - 21, sy + 16), (cx - 13, sy + 22), (cx - 6, sy + 20)], 2.6, 1.6)
        claw(da, (cx - 6, sy + 20), [(cx + 3, sy + 13), (cx + 4, sy + 16), (cx + 4, sy + 19), (cx + 1, sy + 22)])
        # the near hand has come over his shoulder from behind, long fingers hooked down his collarbone
        _ell(da, cx + 10, sy + 1, 2.4, 1.8)
        claw(da, (cx + 10, sy + 1), [(cx + 3, sy + 7), (cx + 5, sy + 9), (cx + 8, sy + 10), (cx + 12, sy + 8)])
    else:
        # one hand clamped over his mouth, the other gripping the crown of his head
        _tube(da, [(cx - 17, sy + 4), (cx - 19, sy + 14), (cx - 11, top + 11), (cx - 5, top + 9)], 2.7, 1.7)
        claw(da, (cx - 5, top + 9), [(cx + 4, top + 7), (cx + 5, top + 9), (cx + 4, top + 11), (cx + 1, top + 13)])
        _tube(da, [(cx + 16, sy + 2), (cx + 13, top - 2), (cx + 6, top - 3)], 2.4, 1.6)
        claw(da, (cx + 6, top - 3), [(cx - 3, top), (cx - 1, top + 2), (cx + 1, top + 3), (cx + 4, top + 3)])
        # the dark welling up him from the sill to the throat
        rise = [(bx - 3, h), (bx - 3, top + 15)]
        for i in range(0, bust.width + 7, 2):
            rise.append((bx - 3 + i, top + 13 + rng.uniform(-1.5, 2.5)))
        rise += [(bx + bust.width + 3, top + 15), (bx + bust.width + 3, h)]
        _poly(da, rise)
        for i in range(4):
            x0 = bx + 2 + i * bust.width / 4
            _tube(da, _bez((x0, top + 14), (x0 + rng.uniform(-3, 3), top + 11), (x0 + rng.uniform(-2, 2), top + 8)),
                  1.2, 0.2)

    def down(m, cut=110):
        m = np.array(m.resize((w, h), Image.BOX))
        return np.where(m > cut, 1.0, 0.0)

    m_body, m_arms, m_det = down(body), down(arms), down(detail, 70)

    def layer(mask, rgb, alpha=245):
        arr = np.zeros((h, w, 4), np.uint8)
        arr[..., :3] = rgb
        arr[..., 3] = (mask * alpha).astype(np.uint8)
        return Image.fromarray(arr)

    def rim(mask):
        """The flash catches the top and the window-side (left) edges of a shape."""
        up = np.zeros_like(mask)
        up[1:] = mask[:-1]
        left = np.zeros_like(mask)
        left[:, 1:] = mask[:, :-1]
        return mask * (1 - up), mask * (1 - left) * (1 - (mask * (1 - up)))

    shade = (9, 7, 14)
    out = base.copy()
    out.alpha_composite(layer(m_body, shade))
    out.alpha_composite(layer(m_body * m_det, (30, 28, 44)))
    r_top, r_side = rim(m_body)
    out.alpha_composite(layer(r_top, (92, 102, 140), 220))
    out.alpha_composite(layer(r_side, (58, 64, 92), 200))
    out.alpha_composite(bust, (bx, by))
    out.alpha_composite(layer(m_arms, shade))
    a_top, a_side = rim(m_arms)
    out.alpha_composite(layer(a_top, (86, 94, 130), 210))
    out.alpha_composite(layer(a_side, (52, 58, 86), 190))
    px = ImageDraw.Draw(out)
    # eyes: slanted coals with a bloom; a seam of teeth in the jaw
    for k_ in (-1, 1):
        ex, ey = round(hx_ + k_ * 2), round(hy)
        px.point((ex, ey), fill=(255, 92, 60, 255))
        px.point((ex + k_, ey - 1), fill=(200, 36, 28, 255))
        for ox, oy in ((0, 1), (-k_, 0)):
            q = out.getpixel((ex + ox, ey + oy))
            out.putpixel((ex + ox, ey + oy), (max(q[0], 90), q[1], q[2], 255))
    for i in range(-2, 3):
        px.point((round(hx_) + i, round(hy + 5 + (i % 2))), fill=(118, 110, 104, 255) if stage == 2 or i % 2 else
                 (70, 64, 62, 255))
    # the reflection is in the glass: the window's mullion, bar and sill stay in front of it
    g = np.array(glass.convert("RGBA"))
    o = np.array(out)
    for (x0, y0, x1, y1) in ((410 - 348, 0, 413 - 348, h), (0, 55 - 46, w, 58 - 46), (0, sill, w, h)):
        o[y0:y1, x0:x1] = g[y0:y1, x0:x1]
    return Image.fromarray(o).convert("RGB")

def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("1e1c16"), hx("3c3a2c"))
    for x in range(0, W, 8):
        d.line([(x, 9), (x, TOP)], fill=hx("2e2c24"))
        d.line([(x + 3, 9), (x + 3, TOP)], fill=hx("38362a"))
    noise(img, (0, 0, W - 1, TOP), 4, 41)
    # crown moulding
    d.rectangle([0, 0, W - 1, 4], fill=hx("16120c"))
    d.rectangle([0, 5, W - 1, 7], fill=hx("4a3424"))
    d.line([(0, 5), (W, 5)], fill=hx("6a4c34"))
    d.line([(0, 8), (W, 8)], fill=hx("24160e"))
    # the water stain started up here
    shadow(img, "ellipse", [244, 8, 306, 44], 0.3, 8, hx("806040"))
    d.line([(424, 6), (420, 14), (423, 22), (420, 30)], fill=hx("26241c"))
    # ceiling bulb on a cord, switched off
    d.line([(300, 0), (300, 14)], fill=hx("16120c"))
    d.ellipse([297, 14, 303, 21], fill=hx("6a6858"))
    d.point((299, 16), fill=hx("a8a690"))


DRAWER_BOX = (276, 109 + TOP, 342, 139 + TOP)
# per-item crops inside the open drawer (screen coords, i.e. art y + TOP)
ITEM_BOXES = {
    "revolver": (289, 118 + TOP, 307, 128 + TOP),
    "dollar": (307, 118 + TOP, 321, 128 + TOP),
    "lockpick": (321, 118 + TOP, 332, 128 + TOP),
}


def open_drawer(img, contents):
    d = ImageDraw.Draw(img)
    # top drawer pulled out towards the camera
    d.polygon([(286, 116), (332, 116), (336, 129), (282, 129)], fill=hx("6a4024"))
    d.rectangle([282, 129, 336, 135], fill=hx("4a2a16"))
    d.rectangle([304, 131, 312, 133], fill=hx("b8904a"))
    d.polygon([(289, 118), (329, 118), (332, 127), (286, 127)], fill=hx("24140a"))
    if "revolver" in contents:
        # a snub .38 lying on its side, barrel to the left: steel barrel and cylinder, walnut grip
        d.rectangle([290, 120, 298, 121], fill=hx("9a9aa4"))
        d.line([(290, 120), (297, 120)], fill=hx("c8c8d0"))
        d.rectangle([297, 119, 302, 123], fill=hx("6a6a74"))
        d.line([(298, 120), (301, 120)], fill=hx("b0b0b8"))
        d.point((303, 119), fill=hx("6a6a74"))
        d.line([(299, 124), (301, 125)], fill=hx("6a6a74"))
        d.polygon([(301, 122), (304, 121), (306, 126), (303, 127)], fill=hx("8a5430"))
        d.line([(304, 122), (305, 125)], fill=hx("b07848"))
    if "dollar" in contents:
        # a flat greenback, pale border and a dark portrait oval
        d.rectangle([309, 120, 319, 125], fill=hx("a8c098"))
        d.rectangle([310, 121, 318, 124], fill=hx("6a8a5a"))
        d.ellipse([312, 121, 316, 124], fill=hx("c8d8b0"))
        d.point((314, 122), fill=hx("4a6a48"))
    if "lockpick" in contents:
        d.rectangle([322, 121, 326, 125], fill=hx("4a2a1a"))
        d.line([(325, 121), (330, 120)], fill=hx("a8a8b0"))
        d.line([(325, 123), (330, 123)], fill=hx("a8a8b0"))


GLINT_FRAMES = 5
GLINT_SIZE = 7


def ring_glint():
    """A horizontal strip of GLINT_FRAMES 7x7 frames: a four-pointed sparkle that flares from the ring's highlight
    and fades back. The centre pixel (3, 3) sits on the highlight."""
    strip = Image.new("RGBA", (GLINT_SIZE * GLINT_FRAMES, GLINT_SIZE))
    core, arm, tip = (255, 250, 220, 255), (255, 236, 170, 220), (255, 224, 140, 120)
    for f, reach in enumerate((0, 1, 3, 2, 1)):
        ox, c = f * GLINT_SIZE, GLINT_SIZE // 2
        strip.putpixel((ox + c, c), core)
        for r in range(1, reach + 1):
            col = arm if r < reach or reach == 1 else tip
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                strip.putpixel((ox + c + dx, c + dy), col)
    return strip


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "office.png")
    for state in ("ajar", "open"):
        save(pixelize(paint(door_state=state), pal).crop(DOOR_BOX), "rooms", f"office_door_{state}.png")
    save(pixelize(paint(()), pal).crop(DRAWER_BOX), "rooms", "office_drawer_open.png")
    for item, box in ITEM_BOXES.items():
        save(pixelize(paint((item,)), pal).crop(box), "rooms", f"office_drawer_{item}.png")
    # Act 3: the lamp off, the whiskey on the desk; the overlays that can still show get dark twins
    dark = paint(lamp_on=False)
    dark_pal = palette_of(dark, 128)
    save(pixelize(dark, dark_pal), "rooms", "office_act3.png")
    for state in ("ajar", "open"):
        save(pixelize(paint(door_state=state, lamp_on=False), dark_pal).crop(DOOR_BOX), "rooms",
             f"office_act3_door_{state}.png")
    save(pixelize(paint((), lamp_on=False), dark_pal).crop(DRAWER_BOX), "rooms", "office_act3_drawer_open.png")
    for item, box in ITEM_BOXES.items():
        save(pixelize(paint((item,), lamp_on=False), dark_pal).crop(box), "rooms", f"office_act3_drawer_{item}.png")
    # the ring is only a glint of gold on the desk: two bright pixels and a shadowed band
    ring = Image.new("RGBA", (3, 2))
    d = ImageDraw.Draw(ring)
    d.point((0, 0), fill=hx("b08838"))
    d.point((1, 0), fill=hx("f0d070"))
    d.point((2, 0), fill=hx("c89a40"))
    d.point((1, 1), fill=hx("6a5020"))
    save(ring, "rooms", "office_ring.png")
    save(ring_glint(), "rooms", "office_ring_glint.png")
    build_storm()
    sprite = Image.new("RGBA", (10, 12))
    cup(ImageDraw.Draw(sprite), 0, 0)
    save(sprite, "rooms", "office_cup.png")
    return px


def build_storm():
    for lit in (False, True):
        suffix = "_lit" if lit else ""
        base = paint_storm(lit)
        pal = palette_of(base, 128)
        save(pixelize(base, pal), "rooms", f"office_storm{suffix}.png")
        # the hat taken off the desk, the bottle set down on it: each overlay crops the same spot of a repaint

        save(pixelize(paint_storm(lit, hat=False, bottle=True), pal).crop(STORM_BOTTLE_BOX), "rooms",
             f"office_storm_bottle{suffix}.png")
        save(pixelize(paint_storm(lit, hat=False), pal).crop(STORM_HAT_BOX), "rooms",
             f"office_storm_no_hat{suffix}.png")
        if lit:
            glass = pixelize(base, pal).crop(STORM_GLASS_BOX)
            for stage in (1, 2):
                save(reflection(glass, stage), "rooms", f"office_storm_demon_{stage}.png")
        else:
            for state in ("ajar", "open"):
                save(pixelize(paint_storm(door_state=state), pal).crop(DOOR_BOX), "rooms",
                     f"office_storm_door_{state}.png")
    print("office_storm overlays: hat", STORM_HAT_BOX[:2], "bottle", STORM_BOTTLE_BOX[:2], "glass",
          STORM_GLASS_BOX[:2], "door", DOOR_BOX[:2])