"""The alley behind the Blue Lantern at night: wet cobbles, the club's back door under a blue glass lantern,
trash cans, bootleg crates, a fire escape and a single gooseneck street lamp that keeps failing.

The room is painted as albedo and then lit (ambient moonlight x albedo + light pools), twice: with the lamp
dead and with it burning. alley.png is the dead-lamp version; alley_lamp.png is the lit version cropped to
where the two differ, so the game can flicker the lamp by toggling the overlay."""
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import math
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, text,
                     save, cut, _mask)
from .street import bricks

BASE = 186                 # foot of the back wall
VP = (50, 150)             # the passage on the left runs away to this point
NEAR_X0, NEAR_X1 = 0, 100  # passage mouth at the plane of the back wall
POST_X, POST_FOOT = 156, 196
SHADE = (188, 62)
DOOR = (314, 124, 348, BASE)
LEAF = 8                   # how much of the swung-in door leaf shows when it is propped ajar
LANTERN = (331, 106)
PUDDLES = [(150, 238, 236, 252), (300, 244, 380, 258), (80, 204, 128, 211), (392, 220, 446, 229),
           (250, 196, 290, 201), (20, 252, 70, 262)]

IRON, IRON_L = hx("26282e"), hx("4a4e58")
WARM = (255, 172, 92)
BLUE = hx("4a8ae8")
MOON_COLORS = [hx("515e7d"), hx("8e99b5"), hx("bbc4d4"), hx("e0e3e5")]


def illuminate(img, ambient, lights):
    """albedo x (ambient + sum of soft coloured light pools) - lit surfaces keep their texture."""
    acc = Image.new("RGB", img.size, ambient)
    for shape, pts, col, k, blur in lights:
        m = _mask(img.size, shape, pts, k, blur).convert("RGB")
        acc = ImageChops.add(acc, ImageChops.multiply(Image.new("RGB", img.size, col), m))
    return ImageChops.multiply(img, acc)


def toward(p, t):
    """Point a fraction t of the way from p to the vanishing point."""
    return (p[0] + (VP[0] - p[0]) * t, p[1] + (VP[1] - p[1]) * t)


# --------------------------------------------------------------------------------------------- sky & walls

def sky(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 130), hx("0c1226"), hx("2a2c48"))
    rnd = random.Random(11)
    for _ in range(40):
        x, y = rnd.randint(0, W - 1), rnd.randint(0, 40)
        d.point((x, y), fill=mix(hx("8890b0"), hx("e0e4f0"), rnd.random()))
    for _ in range(6):
        x, y = rnd.randint(-40, 520), rnd.randint(0, 30)
        light(img, "ellipse", [x - 70, y - 5, x + 70, y + 6], hx("50587a"), 0.25, 6)
    # a water tower on the roof across the alley
    d.rectangle([418, 4, 452, 20], fill=hx("16141c"))
    d.polygon([(416, 4), (435, -6), (454, 4)], fill=hx("16141c"))
    for x in (420, 434, 449):
        d.line([(x, 20), (x + (x - 434) // 7, 30)], fill=hx("16141c"))
    for y in (8, 13, 17):
        d.line([(418, y), (452, y)], fill=hx("221e28"))


def passage(img):
    """A slot between buildings on the left, running back to a lamplit street."""
    d = ImageDraw.Draw(img)
    t_far = 0.76
    ltop, rtop = (NEAR_X0, 14), (NEAR_X1, 22)
    lfoot, rfoot = (NEAR_X0, BASE), (NEAR_X1, BASE)
    flt, frt, flf, frf = toward(ltop, t_far), toward(rtop, t_far), toward(lfoot, t_far), toward(rfoot, t_far)
    # the street at the far end: a building opposite with a lit shopfront
    fx0, fx1 = int(flf[0]), int(frf[0])
    vgrad(img, (fx0, int(flt[1]) - 30, fx1, int(flf[1])), hx("3a3446"), hx("8a7058"))
    d.rectangle([fx0, int(flt[1]) - 6, fx1, int(flf[1]) - 8], fill=hx("4a3a36"))
    d.rectangle([fx0 + 3, int(flf[1]) - 22, fx1 - 4, int(flf[1]) - 10], fill=hx("e8b870"))
    d.line([(fx0 + 3, int(flf[1]) - 16), (fx1 - 4, int(flf[1]) - 16)], fill=hx("6a4a30"))
    d.rectangle([fx0, int(flf[1]) - 8, fx1, int(flf[1])], fill=hx("7a6a5a"))
    # walls of the passage: dark brick converging on VP
    wall = hx("5a3a32")
    left = [ltop, flt, flf, lfoot]
    right = [rtop, frt, frf, rfoot]
    d.polygon(left, fill=mul(wall, 0.8))
    d.polygon(right, fill=wall)
    for (top, foot, poly) in ((ltop, lfoot, left), (rtop, rfoot, right)):
        for y in range(int(top[1]) + 4, BASE, 5):
            p = (top[0], y)
            d.line([p, toward(p, t_far)], fill=mul(wall, 0.55))
        for i in range(1, 18):
            t = t_far * (1 - (1 - i / 18) ** 1.7)
            a, b = toward(top, t), toward(foot, t)
            for yy in range(int(a[1]), int(b[1]), 10):
                d.line([(a[0], yy), (a[0], yy + 4)], fill=mul(wall, 0.6))
    # a pipe and a window on the right wall
    d.line([toward((96, 20), 0), toward((96, BASE), 0)], fill=IRON)
    w0, w1 = toward((NEAR_X1, 70), 0.25), toward((NEAR_X1, 104), 0.38)
    d.polygon([w0, toward((NEAR_X1, 70), 0.38), w1, toward((NEAR_X1, 104), 0.25)], fill=hx("1a2030"))
    # cobbled floor of the passage
    floor = [lfoot, rfoot, frf, flf]
    d.polygon(floor, fill=hx("4a4852"))
    rnd = random.Random(152)
    rows = [t_far * (1 - (1 - i / 16) ** 1.6) for i in range(17)]
    for row, (near, far) in enumerate(zip(rows, rows[1:])):
        for col in range(-1, 12):
            x0 = col * 10 + (5 if row % 2 else 0)
            x1 = x0 + 9
            a, b = toward((max(0, x0), BASE), near), toward((min(100, x1), BASE), near)
            c, e = toward((min(100, x1), BASE), far), toward((max(0, x0), BASE), far)
            if x1 <= 0 or x0 >= 100:
                continue
            color = mix(hx("42434e"), hx("85879a"), rnd.uniform(0.1, 0.65))
            d.polygon([a, b, c, e], fill=color)
            d.line([a, b], fill=mul(color, 1.3))
            d.line([e, c], fill=hx("292b36"))
    # A wet gutter, drain grate, scattered rubbish and a broken chair give the narrow road a human scale.
    d.line([toward((10, BASE), 0.05), toward((10, BASE), 0.7)], fill=hx("99a2ba"), width=1)
    d.polygon([(20, 182), (37, 182), (39, 178), (24, 178)], fill=hx("252936"))
    for x in range(24, 38, 3):
        d.line([(x, 181), (x + 2, 178)], fill=hx("737c92"))
    d.polygon([(30, 174), (36, 173), (34, 176), (29, 176)], fill=hx("9b8b76"))
    d.line([(77, 173), (80, 160), (88, 160), (87, 174)], fill=hx("725745"), width=2)
    d.line([(79, 167), (88, 167)], fill=hx("9b7960"), width=2)
    d.line([(81, 160), (82, 155), (87, 156)], fill=hx("725745"), width=2)
    # a garbage pail and a broken chair half-way down
    p = toward((70, BASE), 0.35)
    d.rectangle([p[0] - 5, p[1] - 14, p[0] + 5, p[1]], fill=hx("6a6e74"))
    d.line([(p[0] - 6, p[1] - 14), (p[0] + 6, p[1] - 14)], fill=hx("9a9ea4"))
    return floor, (fx0, int(flt[1]) - 30, fx1, int(flf[1]))


def back_wall(img):
    d = ImageDraw.Draw(img)
    bricks(img, (NEAR_X1, 26, W - 1, BASE), hx("8a4a3a"), hx("663226"), hx("3a2a26"), 71)
    # stone coping along the parapet and a cast-iron cornice
    d.rectangle([NEAR_X1, 20, W - 1, 26], fill=hx("7a7670"))
    d.line([(NEAR_X1, 20), (W, 20)], fill=hx("a8a49c"))
    d.line([(NEAR_X1, 27), (W, 27)], fill=hx("2a2224"))
    for x in range(NEAR_X1 + 4, W, 12):
        d.rectangle([x, 27, x + 3, 30], fill=hx("4a4240"))
    # corner quoins where the wall turns into the passage
    for i, y in enumerate(range(30, BASE, 12)):
        w = 10 if i % 2 else 6
        d.rectangle([NEAR_X1, y, NEAR_X1 + w, y + 10], fill=hx("7a7268"))
        d.line([(NEAR_X1, y + 11), (NEAR_X1 + w, y + 11)], fill=hx("3a3230"))
    # ghost sign of an old coal & ice dealer
    d.rectangle([132, 34, 292, 52], fill=mix(hx("7a4232"), hx("a89a7a"), 0.35))
    text(img, (212, 43), "COAL  &  ICE", mix(hx("7a4232"), hx("d8ccb0"), 0.55), size=8)
    rnd = random.Random(5)
    for _ in range(90):
        x, y = rnd.randint(132, 292), rnd.randint(34, 52)
        d.point((x, y), fill=mix(hx("7a4232"), hx("663226"), rnd.random()))
    # upstairs windows: soot-dark, one boarded up
    for x0 in (128, 196, 262):
        d.rectangle([x0 - 2, 60, x0 + 24, 64], fill=hx("8a8278"))
        d.rectangle([x0, 64, x0 + 22, 96], fill=hx("1c2232"))
        d.line([(x0, 80), (x0 + 22, 80)], fill=hx("3a3a40"))
        d.line([(x0 + 11, 64), (x0 + 11, 96)], fill=hx("3a3a40"))
        d.line([(x0 + 2, 94), (x0 + 12, 66)], fill=hx("34405a"))
        d.rectangle([x0 - 3, 97, x0 + 25, 99], fill=hx("8a8278"))
    for y in (68, 76, 84, 90):
        d.rectangle([262, y, 284, y + 5], fill=mix(hx("6a5038"), hx("4a3a2a"), (y % 3) / 3))
    # an old arched doorway, bricked up
    d.rectangle([112, 112, 146, BASE], fill=hx("3a2a26"))
    bricks(img, (115, 122, 143, BASE - 1), hx("7a4436"), hx("5a3024"), hx("3a2a26"), 73, h=4, w=9)
    d.chord([112, 100, 146, 128], 180, 360, fill=hx("8a8278"))
    d.chord([116, 104, 142, 124], 180, 360, fill=hx("5a3024"))
    # barred cellar window just above the cobbles
    d.rectangle([212, 152, 250, 176], fill=hx("8a8278"))
    d.rectangle([215, 155, 247, 173], fill=hx("12141c"))
    for x in range(218, 247, 5):
        d.line([(x, 155), (x, 173)], fill=hx("4a4c54"))
    d.rectangle([210, 176, 252, 179], fill=hx("9a9288"))
    # downpipe with a cracked shoe, spilling into the cobbles
    d.rectangle([296, 28, 300, 180], fill=hx("4c4a4e"))
    d.line([(296, 28), (296, 180)], fill=hx("7a787e"))
    for y in range(40, 180, 26):
        d.rectangle([295, y, 301, y + 2], fill=hx("38363a"))
    d.polygon([(296, 180), (300, 180), (306, 188), (300, 189)], fill=hx("4c4a4e"))
    d.line([(304, 189), (306, 196)], fill=hx("8ea0c0"))
    # electrical conduit and a junction box
    d.line([(150, 108), (290, 108)], fill=hx("3a3a40"))
    d.rectangle([272, 102, 282, 114], fill=hx("4a4c52"))
    d.line([(277, 114), (277, 150)], fill=hx("3a3a40"))
    # grime: soot from the cornice, damp rising from the ground
    for _ in range(40):
        x = rnd.randint(NEAR_X1, W)
        y = rnd.choice((27, 99, 179))
        shadow(img, "rect", [x, y, x + rnd.randint(2, 7), y + rnd.randint(10, 40)], 0.25, 2, hx("20202a"))
    shadow(img, "rect", [NEAR_X1, BASE - 26, W, BASE], 0.3, 8, hx("303040"))


def door(img, ajar=False):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    d.rectangle([x0 - 4, y0 - 6, x1 + 4, y1], fill=hx("8a8278"))
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1], fill=hx("2a2c30"))
    if ajar:
        door_ajar(img)
    else:
        door_leaf(img)
    step(d)
    lantern(d)


def door_leaf(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    vgrad(img, (x0, y0, x1, y1), hx("5a6a68"), hx("3e4a48"))
    for y in (y0 + 4, (y0 + y1) // 2, y1 - 6):
        for x in range(x0 + 3, x1 - 1, 4):
            d.point((x, y), fill=hx("9aa8a4"))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1)], fill=hx("7a8a88"))
    # a peep slot, a heavy handle and a padlock hasp
    d.rectangle([x0 + 10, y0 + 14, x0 + 24, y0 + 18], fill=hx("16181a"))
    d.line([(x0 + 10, y0 + 13), (x0 + 24, y0 + 13)], fill=hx("9aa8a4"))
    d.rectangle([x1 - 7, y0 + 30, x1 - 4, y0 + 40], fill=hx("b8b0a0"))
    d.rectangle([x1 - 6, y0 + 42, x1 - 4, y0 + 45], fill=hx("8a7a50"))


def door_ajar(img):
    """Swung inward on its left hinges: painted dark here; door_glow lights the hall, the leaf and the brick."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    d.rectangle([x0, y0, x1, y1], fill=hx("2a1c14"))


def door_glow(img):
    """The hall behind the ajar door is a light source: a bulb on a cord, wainscoted walls, worn boards and a
    second, padded door at the far end with light round its edges. The steel leaf stands swung in on the left,
    its foot on a brick."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    gx0 = x0 + LEAF + 1
    ix0, iy0, ix1, iy1 = gx0 + 6, y0 + 13, x1 - 7, y1 - 9          # the inner door's frame, down the hall
    # ceiling, right wall (plaster over a dark wainscot) and floorboards, all running to the inner door
    d.polygon([(gx0, y0), (x1, y0), (ix1, iy0), (ix0, iy0)], fill=hx("2e1c12"))
    vgrad(img, (ix1, y0, x1, y1), hx("6a4424"), hx("94622e"))
    for x in range(ix1, x1 + 1):
        t = (x - ix1) / (x1 - ix1)
        top, foot = iy0 + (y0 - iy0) * t, iy1 + (y1 - iy1) * t
        wain = foot - (foot - top) * 0.38
        d.line([(x, wain), (x, foot)], fill=hx("4a2814"))
        d.point((x, wain), fill=hx("b07a3c"))
    d.line([(ix1, iy0), (x1, y0)], fill=hx("4a2c18"))
    d.polygon([(gx0, y1), (x1, y1), (ix1, iy1), (ix0, iy1)], fill=hx("8a5426"))
    for k in range(1, 5):
        fx = gx0 + (x1 - gx0) * k / 5
        d.line([(fx, y1), (ix0 + (ix1 - ix0) * k / 5, iy1)], fill=hx("6a3c1a"))
    d.line([(gx0, y1 - 1), (x1, y1 - 1)], fill=hx("c88a44"))
    # the inner door: padded leather in a dark jamb, brass studs, a knob, a peep slot and light leaking round it
    d.rectangle([ix0 - 1, iy0 - 1, ix1 + 1, iy1], fill=hx("24140c"))
    vgrad(img, (ix0, iy0, ix1, iy1 - 1), hx("5a2418"), hx("3e1810"))
    d.rectangle([ix0 + 2, iy0 + 3, ix1 - 2, iy0 + 18], outline=hx("2a100a"))
    d.rectangle([ix0 + 2, iy0 + 21, ix1 - 2, iy1 - 4], outline=hx("2a100a"))
    for sx in range(ix0 + 1, ix1, 3):
        d.point((sx, iy0 + 1), fill=hx("c8a050"))
        d.point((sx, iy1 - 2), fill=hx("c8a050"))
    d.rectangle([ix0 + 3, iy0 + 7, ix1 - 3, iy0 + 8], fill=hx("ffd890"))   # the slot, lit from the club
    d.line([(ix0 + 3, iy0 + 6), (ix1 - 3, iy0 + 6)], fill=hx("8a6a38"))
    d.point((ix1 - 2, iy0 + 20), fill=hx("ffe0a0"))                         # brass knob
    d.point((ix1 - 2, iy0 + 21), fill=hx("a07a30"))
    d.line([(ix0, iy1), (ix1, iy1)], fill=hx("ffd080"))                     # light under the door
    d.line([(ix1 + 1, iy0), (ix1 + 1, iy1)], fill=hx("c88440"))             # and down its latch side
    # a bare bulb on a cord, with a brass socket
    bx = (gx0 + x1) // 2 + 1
    d.line([(bx, y0), (bx, y0 + 4)], fill=hx("1a120c"))
    d.rectangle([bx - 1, y0 + 5, bx + 1, y0 + 6], fill=hx("a07a30"))
    d.point((bx - 1, y0 + 5), fill=hx("e0c070"))
    d.ellipse([bx - 2, y0 + 7, bx + 2, y0 + 11], fill=hx("ffe8b0"))
    d.point((bx, y0 + 12), fill=hx("ffe8b0"))
    d.point((bx - 1, y0 + 8), fill=hx("ffffff"))
    light(img, "ellipse", [bx - 9, y0 + 1, bx + 9, y0 + 18], hx("ffc070"), 0.4, 3)
    light(img, "rect", [gx0 + 2, y0 + 12, x1 - 2, y0 + 30], hx("706050"), 0.12, 4)  # smoke under the bulb
    d = ImageDraw.Draw(img)
    # the steel leaf, swung in: its inside face catches the hall light; hinges, a drop bar's bracket, its edge
    d.polygon([(x0, y0), (x0 + LEAF, y0 + 4), (x0 + LEAF, y1 - 4), (x0, y1)], fill=hx("38403e"))
    d.line([(x0 + LEAF, y0 + 4), (x0 + LEAF, y1 - 4)], fill=hx("c08a50"))
    d.line([(x0 + LEAF - 1, y0 + 4), (x0 + LEAF - 1, y1 - 4)], fill=hx("6a5a48"))
    for hy in (y0 + 6, y1 - 10):
        d.rectangle([x0, hy, x0 + 1, hy + 3], fill=hx("1a1c1e"))
    d.rectangle([x0 + 3, y0 + 30, x0 + 6, y0 + 33], fill=hx("1a1c1e"))
    d.point((x0 + 5, y0 + 31), fill=hx("8a7a60"))
    # the brick under it: a red common brick, its top in the light, a chipped corner and a shadow
    bx0, by0, bx1, by1 = x0 + LEAF - 4, y1 - 5, x0 + LEAF + 5, y1 - 1
    d.line([(bx0 + 1, by1 + 1), (bx1 + 2, by1 + 1)], fill=hx("2a1a12"))
    d.rectangle([bx0, by0, bx1, by1], fill=hx("8a3424"))
    d.line([(bx0, by0), (bx1 - 1, by0)], fill=hx("d0784c"))
    d.line([(bx1, by0 + 1), (bx1, by1)], fill=hx("b0583a"))
    d.line([(bx0, by1), (bx1, by1)], fill=hx("5a1e14"))
    d.point((bx1, by0), fill=hx("2a1c14"))
    for px_, py_ in ((bx0 + 2, by0 + 2), (bx0 + 5, by0 + 1), (bx0 + 7, by0 + 3)):
        d.point((px_, py_), fill=hx("6a2418"))
    d.point((bx0 + 3, by0 + 1), fill=hx("a8a090"))                            # old mortar


def step(d):
    x0, y0, x1, y1 = DOOR
    # concrete step
    d.rectangle([x0 - 8, y1, x1 + 8, y1 + 5], fill=hx("8a8680"))
    d.line([(x0 - 8, y1), (x1 + 8, y1)], fill=hx("b0aca4"))
    d.line([(x0 - 8, y1 + 5), (x1 + 8, y1 + 5)], fill=hx("3a383c"))


def lantern(d):
    """The blue glass lantern on a scrolled wrought bracket - the only sign of the club."""
    lx, ly = LANTERN
    d.line([(lx - 14, ly - 8), (lx, ly - 8)], fill=IRON, width=2)
    d.line([(lx - 14, ly - 13), (lx - 14, ly + 1)], fill=IRON, width=2)
    d.point((lx - 15, ly - 11), fill=IRON_L)                                # wall bolts
    d.point((lx - 15, ly - 1), fill=IRON_L)
    d.arc([lx - 14, ly - 8, lx - 3, ly + 4], 270, 360, fill=IRON)
    d.arc([lx - 9, ly - 13, lx - 3, ly - 8], 180, 360, fill=IRON)          # a scroll over the arm
    d.point((lx - 9, ly - 10), fill=IRON)
    d.line([(lx, ly - 8), (lx, ly - 6)], fill=IRON)
    # hood: a stepped iron cap with a ball finial and a lip that overhangs the glass
    d.polygon([(lx - 7, ly - 3), (lx + 7, ly - 3), (lx + 3, ly - 6), (lx - 3, ly - 6)], fill=IRON)
    d.line([(lx - 2, ly - 5), (lx + 2, ly - 5)], fill=IRON_L)
    d.line([(lx - 7, ly - 3), (lx + 7, ly - 3)], fill=IRON_L)
    d.rectangle([lx - 1, ly - 8, lx + 1, ly - 7], fill=IRON)
    lantern_glass(d)


def lantern_glass(d):
    """Drawn again after lighting: the glass is a light source, not a lit surface. Three leaded panes show, the
    side ones darker; a flame burns inside; an iron band and drip cone close the bottom."""
    lx, ly = LANTERN
    d.polygon([(lx - 6, ly - 2), (lx + 6, ly - 2), (lx + 5, ly + 10), (lx - 5, ly + 10)], fill=hx("2a5ab8"))
    d.polygon([(lx - 3, ly - 2), (lx + 3, ly - 2), (lx + 2, ly + 10), (lx - 2, ly + 10)], fill=hx("3a7ae8"))
    d.ellipse([lx - 2, ly + 1, lx + 2, ly + 7], fill=hx("8ac0ff"))
    d.line([(lx, ly + 2), (lx, ly + 6)], fill=hx("e8f4ff"))                 # the flame
    d.point((lx, ly + 3), fill=hx("ffffff"))
    d.point((lx, ly + 7), fill=hx("ffd890"))                               # its wick
    d.line([(lx - 3, ly - 2), (lx - 2, ly + 10)], fill=IRON)               # corner posts
    d.line([(lx + 3, ly - 2), (lx + 2, ly + 10)], fill=IRON)
    d.line([(lx - 6, ly - 2), (lx - 5, ly + 10)], fill=hx("1e2a4a"))
    d.line([(lx + 6, ly - 2), (lx + 5, ly + 10)], fill=hx("1e2a4a"))
    d.line([(lx - 5, ly + 4), (lx - 4, ly + 4)], fill=hx("1e3a6a"))        # leading on the side panes
    d.line([(lx + 4, ly + 4), (lx + 5, ly + 4)], fill=hx("1e3a6a"))
    d.point((lx - 5, ly), fill=hx("c0e0ff"))                                # a glint on the glass
    d.point((lx + 1, ly - 1), fill=hx("c0e0ff"))
    d.line([(lx - 6, ly - 2), (lx + 6, ly - 2)], fill=IRON)
    d.line([(lx - 5, ly + 10), (lx + 5, ly + 11)], fill=IRON, width=2)
    d.line([(lx - 5, ly + 10), (lx + 5, ly + 10)], fill=IRON_L)
    d.polygon([(lx - 3, ly + 12), (lx + 3, ly + 12), (lx, ly + 15)], fill=IRON)
    d.point((lx, ly + 16), fill=IRON)


def fire_escape(img):
    d = ImageDraw.Draw(img)
    x0, x1 = 362, 476
    # windows behind it, one with a lamp still on
    for wx, lit in ((376, False), (436, True)):
        for wy in (46, 104):
            d.rectangle([wx - 2, wy - 4, wx + 24, wy], fill=hx("8a8278"))
            if lit and wy == 104:
                vgrad(img, (wx, wy, wx + 22, wy + 30), hx("f0c070"), hx("c08040"))
                d.rectangle([wx, wy, wx + 22, wy + 12], fill=hx("b08a50"))
            else:
                d.rectangle([wx, wy, wx + 22, wy + 30], fill=hx("1c2232"))
                d.line([(wx + 2, wy + 28), (wx + 12, wy + 2)], fill=hx("34405a"))
            d.line([(wx, wy + 15), (wx + 22, wy + 15)], fill=hx("3a3a40"))
            d.line([(wx + 11, wy), (wx + 11, wy + 30)], fill=hx("3a3a40"))
            d.rectangle([wx - 3, wy + 31, wx + 25, wy + 33], fill=hx("8a8278"))
    for py in (82, 140):
        # cast shadow of the platform on the bricks
        shadow(img, "polygon", [(x0 + 6, py + 4), (x1 + 6, py + 4), (x1 + 6, py + 12), (x0 + 6, py + 12)], 0.5, 2)
        d.rectangle([x0, py, x1, py + 2], fill=IRON)
        d.line([(x0, py), (x1, py)], fill=IRON_L)
        d.line([(x0, py - 12), (x1, py - 12)], fill=IRON, width=2)
        for x in range(x0, x1 + 1, 4):
            d.line([(x, py - 12), (x, py)], fill=IRON)
        for x in (x0, x1):
            d.line([(x, py - 13), (x, py + 2)], fill=IRON, width=2)
        d.polygon([(x0 + 2, py + 3), (x0 + 12, py + 3), (x0 + 2, py + 14)], fill=IRON)
    # stair between the platforms
    d.line([(x1 - 10, 140), (x0 + 30, 82)], fill=IRON, width=2)
    d.line([(x1 - 4, 140), (x0 + 36, 82)], fill=IRON)
    for i in range(10):
        t = i / 9
        ax, ay = (x1 - 10) + (x0 + 30 - (x1 - 10)) * t, 140 - 58 * t
        d.line([(ax, ay), (ax + 6, ay)], fill=IRON_L)
    # stair up to the roof
    d.line([(x0 + 20, 82), (x1 - 20, 30)], fill=IRON, width=2)
    # drop ladder hauled up out of reach
    for x in (x0 + 52, x0 + 62):
        d.line([(x, 142), (x, 170)], fill=IRON)
    for y in range(146, 170, 4):
        d.line([(x0 + 52, y), (x0 + 62, y)], fill=IRON)
    # a shirt left out on the railing
    d.polygon([(x0 + 70, 70), (x0 + 84, 70), (x0 + 86, 84), (x0 + 68, 84)], fill=hx("a8a49a"))
    d.line([(x0 + 77, 70), (x0 + 77, 84)], fill=hx("7a766e"))


def wires(img):
    d = ImageDraw.Draw(img)
    for (a, b, sag, col) in (((0, 10), (W, 22), 10, hx("0a0a10")), ((0, 30), (W, 16), 8, hx("101018"))):
        pts = []
        for i in range(41):
            t = i / 40
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + sag * 4 * t * (1 - t)))
        d.line(pts, fill=col)


# --------------------------------------------------------------------------------------------- ground

def ground(img):
    d = ImageDraw.Draw(img)
    # damp stone footing along the wall
    d.rectangle([NEAR_X1, BASE, W, BASE + 4], fill=hx("6a6660"))
    d.line([(NEAR_X1, BASE), (W, BASE)], fill=hx("8a8680"))
    d.rectangle([0, BASE + 5, W, FULL_H], fill=hx("2a2a30"))
    rnd = random.Random(91)
    y, row = BASE + 5, 0
    while y < FULL_H:
        h = 3 + min(5, (y - BASE) // 16)
        x = -rnd.randint(0, 10)
        while x < W:
            w = rnd.randint(6, 10) + (y - BASE) // 14
            c = mix(hx("5e5c66"), hx("767480"), rnd.random())
            d.rounded_rectangle([x + 1, y, x + w - 1, y + h - 1], radius=1, fill=c)
            d.line([(x + 2, y), (x + w - 3, y)], fill=mul(c, 1.18))
            d.line([(x + 2, y + h - 1), (x + w - 3, y + h - 1)], fill=mul(c, 0.75))
            x += w
        y += h + 1
        row += 1
    noise(img, (0, BASE + 5, W - 1, FULL_H - 1), 6, 92)
    # broken asphalt patches poured over the cobbles
    for (cx, cy, rx, ry) in ((250, 216, 70, 14), (404, 250, 64, 12), (52, 228, 40, 9)):
        pts = []
        for i in range(36):
            a = 2 * math.pi * i / 36
            r = 1 + rnd.uniform(-0.18, 0.12) + 0.12 * math.sin(a * 3 + cx)
            pts.append((cx + rx * r * math.cos(a), cy + ry * r * math.sin(a)))
        d.polygon(pts, fill=hx("4c4c56"))
        d.line(pts + [pts[0]], fill=hx("34343c"))
        noise(img, (cx - rx, cy - ry, cx + rx, cy + ry), 3, cx)
    for _ in range(26):  # cracks in the patches and the cobbles
        x, y = rnd.randint(0, W), rnd.randint(BASE + 8, FULL_H - 2)
        for _ in range(rnd.randint(3, 6)):
            nx, ny = x + rnd.randint(-5, 5), y + rnd.randint(-1, 2)
            d.line([(x, y), (nx, ny)], fill=hx("1c1c22"))
            x, y = nx, ny
    noise(img, (0, BASE + 5, W - 1, FULL_H - 1), 4, 93)
    # storm drain
    d.rectangle([120, 254, 150, 262], fill=hx("16161a"))
    for x in range(122, 150, 3):
        d.line([(x, 255), (x, 261)], fill=hx("5a5a62"))
    d.rectangle([118, 252, 152, 253], fill=hx("6a6a72"))
    # litter: newspapers, a broken bottle, cigarette ends
    for (x, y, a) in ((262, 248, 0), (96, 236, 1), (430, 210, 2)):
        pts = [(x, y), (x + 14, y - 2 + a), (x + 16, y + 6), (x + 2, y + 8 - a)]
        d.polygon(pts, fill=hx("a8a08a"))
        d.line([(x + 3, y + 2), (x + 12, y + 1)], fill=hx("5a5648"))
        d.line([(x + 3, y + 4), (x + 11, y + 4)], fill=hx("5a5648"))
    for (x, y) in ((360, 226), (366, 228), (72, 212)):
        d.polygon([(x, y), (x + 3, y - 2), (x + 4, y + 1)], fill=hx("3a6a3a"))
    for (x, y) in ((188, 232), (232, 216), (276, 238), (318, 204)):
        d.line([(x, y), (x + 2, y)], fill=hx("c8c0b0"))


def puddles_albedo(img):
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in PUDDLES:
        d.ellipse([x0, y0, x1, y1], fill=hx("22283a"))


# --------------------------------------------------------------------------------------------- props

def trash_cans(img):
    d = ImageDraw.Draw(img)
    for i, (x0, top) in enumerate(((380, 170), (404, 172))):
        x1, g = x0 + 20, 202 + i * 2
        shadow(img, "ellipse", [x0 - 4, g - 3, x1 + 8, g + 3], 0.6, 2)
        hgradbox(img, (x0, top, x1, g), hx("8a8e94"), hx("4a4e54"))
        for x in range(x0 + 3, x1, 4):
            d.line([(x, top + 3), (x, g - 1)], fill=hx("5a5e64"))
        for y in (top + 6, g - 6):
            d.line([(x0, y), (x1, y)], fill=hx("a8acb2"))
        d.rectangle([x0 - 1, top - 2, x1 + 1, top], fill=hx("9a9ea4"))
        d.rectangle([x0 - 2, top + 9, x0, top + 13], fill=hx("6a6e74"))
        d.rectangle([x1, top + 9, x1 + 2, top + 13], fill=hx("6a6e74"))
        if i == 0:
            d.ellipse([x0 - 1, top - 5, x1 + 1, top + 1], fill=hx("8a8e94"))
            d.rectangle([x0 + 8, top - 7, x0 + 12, top - 5], fill=hx("6a6e74"))
    # the second can has lost its lid; rubbish spills over
    d.ellipse([403, 168, 425, 174], fill=hx("1a1a1e"))
    d.polygon([(406, 170), (412, 162), (418, 166), (422, 170)], fill=hx("8a8270"))
    d.ellipse([428, 190, 440, 210], fill=hx("7a7e84"), outline=hx("a8acb2"))
    d.ellipse([432, 198, 436, 202], fill=hx("4a4e54"))
    for (x, y, c) in ((426, 210, hx("8a8270")), (436, 214, hx("5a4030")), (420, 212, hx("a8a08a"))):
        d.ellipse([x - 4, y - 2, x + 4, y + 2], fill=c)
    # a stray cat on the closed lid, eyes catching the lantern
    cx, cy = 390, 163
    d.ellipse([cx - 6, cy - 4, cx + 4, cy + 3], fill=hx("16141a"))
    d.ellipse([cx + 2, cy - 8, cx + 8, cy - 2], fill=hx("16141a"))
    d.polygon([(cx + 2, cy - 7), (cx + 3, cy - 11), (cx + 5, cy - 7)], fill=hx("16141a"))
    d.polygon([(cx + 5, cy - 7), (cx + 7, cy - 11), (cx + 8, cy - 6)], fill=hx("16141a"))
    d.line([(cx - 6, cy + 1), (cx - 10, cy - 6)], fill=hx("16141a"), width=2)


def hgradbox(img, box, c1, c2):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    mid = x0 + (x1 - x0) * 0.35
    for x in range(x0, x1 + 1):
        t = abs(x - mid) / max(1, x1 - x0)
        d.line([(x, y0), (x, y1)], fill=mix(c1, c2, min(1, t * 1.6)))


def crate(img, x0, y0, x1, y1, label=None, seed=0):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    d.rectangle([x0, y0, x1, y1], fill=hx("8a6a44"))
    for y in range(y0 + 2, y1, 6):
        d.line([(x0, y), (x1, y)], fill=hx("5a4228"))
    for x in (x0, x1 - 3):
        d.rectangle([x, y0, x + 3, y1], fill=hx("a07c50"))
    d.line([(x0 + 3, y0 + 2), (x1 - 3, y1 - 2)], fill=hx("a07c50"), width=2)
    d.rectangle([x0, y0, x1, y1], outline=hx("3a2a18"))
    for _ in range(6):
        x, y = rnd.randint(x0 + 2, x1 - 2), rnd.randint(y0 + 2, y1 - 2)
        d.point((x, y), fill=hx("3a2a18"))
    if label:
        text(img, ((x0 + x1) // 2, (y0 + y1) // 2), label, hx("2a2430"), size=8)


def crates(img):
    shadow(img, "rect", [430, 196, 480, 208], 0.6, 3)
    crate(img, 434, 170, 474, 204, "SOAP", 1)
    crate(img, 438, 140, 472, 170, "B.L.", 2)
    shadow(img, "rect", [100, 190, 140, 198], 0.6, 3)
    crate(img, 104, 168, 134, 194, None, 3)
    d = ImageDraw.Draw(img)
    for x, c in ((110, hx("3a6a3a")), (116, hx("6a4a1a")), (124, hx("3a6a3a"))):  # empties on the crate
        d.rectangle([x, 158, x + 3, 167], fill=c)
        d.rectangle([x + 1, 154, x + 2, 158], fill=c)
        d.point((x, 160), fill=mul(c, 1.8))
    # burlap sacks slumped by the bricked arch
    d.ellipse([140, 176, 162, 196], fill=hx("7a6a4a"))
    d.ellipse([146, 170, 158, 180], fill=hx("6a5a3e"))
    d.line([(144, 186), (158, 184)], fill=hx("5a4a30"))


def lamppost(img, on):
    d = ImageDraw.Draw(img)
    x, g = POST_X, POST_FOOT
    shadow(img, "ellipse", [x - 10, g - 3, x + 12, g + 3], 0.6, 2)
    d.polygon([(x - 7, g), (x - 5, g - 4), (x - 4, g - 16), (x + 4, g - 16), (x + 5, g - 4), (x + 7, g)], fill=IRON)
    for y in (g - 16, g - 10, g - 4):
        d.rectangle([x - 5, y - 1, x + 5, y], fill=IRON_L)
    d.rectangle([x - 2, 66, x + 1, g - 16], fill=IRON)
    d.line([(x - 2, 68), (x - 2, g - 17)], fill=IRON_L)
    d.rectangle([x - 3, 130, x + 2, 133], fill=IRON)
    # gooseneck arm out over the alley
    sx, sy = SHADE
    pts = []
    for i in range(21):
        a = math.pi * i / 20
        pts.append((x + (sx - x) / 2 - (sx - x) / 2 * math.cos(a), 66 - 16 * math.sin(a)))
    d.line(pts, fill=IRON, width=3)
    d.line([(px, py - 1) for px, py in pts], fill=IRON_L)
    d.line([(sx, sy - 6), (sx, sy)], fill=IRON, width=2)
    # enamel dish shade and the bulb under it
    bulb = hx("fff8e0") if on else hx("6a6458")
    d.ellipse([sx - 4, sy + 1, sx + 4, sy + 9], fill=bulb)
    if on:
        d.ellipse([sx - 2, sy + 3, sx + 2, sy + 7], fill=hx("ffffff"))
    shade(d, on)


def shade(d, on):
    """The enamel dish: opaque from above, so the bulb's glow only spills out under its rim."""
    sx, sy = SHADE
    d.polygon([(sx - 13, sy + 4), (sx - 4, sy - 2), (sx + 4, sy - 2), (sx + 13, sy + 4)], fill=hx("2e4036"))
    d.line([(sx - 9, sy + 1), (sx - 3, sy - 1)], fill=hx("3e5246"))
    d.line([(sx - 13, sy + 4), (sx + 13, sy + 4)], fill=hx("e8e4d8") if on else hx("8a8880"))
    d.line([(sx - 4, sy - 2), (sx + 4, sy - 2)], fill=hx("4a5a50"))


# --------------------------------------------------------------------------------------------- light

def lighting(img, on, far_box, ajar=False):
    sx, sy = SHADE
    lx, ly = LANTERN
    fx0, fy0, fx1, fy1 = far_box
    lights = [
        ("rect", [NEAR_X1, -20, W + 20, 70], (28, 34, 62), 1.0, 30),             # moonlight on the upper wall
        ("ellipse", [-30, -40, 160, 110], (30, 36, 70), 1.0, 30),               # open sky over the passage
        ("ellipse", [fx0 - 20, fy0, fx1 + 20, fy1 + 26], (200, 150, 96), 0.9, 10),  # street at the far end
        ("polygon", [(fx0, fy1), (fx1, fy1), (NEAR_X1 - 6, BASE + 30), (NEAR_X0 + 10, BASE + 30)],
         (120, 90, 60), 0.5, 10),
        ("ellipse", [lx - 46, ly - 40, lx + 46, ly + 80], (40, 90, 200), 0.9, 18),  # blue lantern
        ("ellipse", [lx - 60, BASE - 10, lx + 70, BASE + 34], (30, 60, 150), 0.6, 14),
        ("rect", [430, 98, 466, 150], (180, 120, 60), 0.6, 10),                 # the lit window upstairs
    ]
    if on:
        lights += [
            ("ellipse", [92, 192, 330, 266], WARM, 1.0, 18),           # pool on the cobbles
            ("ellipse", [140, 204, 270, 250], (255, 200, 130), 0.8, 12),
            ("ellipse", [96, 84, 290, 236], (220, 160, 100), 0.8, 22),  # wash on the wall behind
            ("ellipse", [sx - 30, sy + 6, sx + 30, sy + 50], (200, 150, 90), 0.5, 10),
        ]
    else:
        lights += [("ellipse", [sx - 8, sy, sx + 8, sy + 12], (120, 70, 30), 0.6, 4)]
    if ajar:
        x0, y0, x1, y1 = DOOR
        lights += [("polygon", [(x0 + LEAF, y1), (x1, y1), (x1 + 16, y1 + 18), (x0 + 2, y1 + 18)], (170, 100, 44), 0.8, 4)]
    img = illuminate(img, (46, 52, 90), lights)
    # deep shadows: the passage, under the fire escape, the corners
    shadow(img, "polygon", [(0, 0), (NEAR_X1, 22), (NEAR_X1, BASE), (60, 170), (40, 150), (0, 140)], 0.25, 10)
    shadow(img, "rect", [440, 150, W + 20, FULL_H + 20], 0.35, 24)
    shadow(img, "rect", [-20, 236, 70, FULL_H + 20], 0.3, 20)
    # glows that read as light sources (screen-blended)
    light(img, "ellipse", [lx - 6, ly - 4, lx + 6, ly + 12], hx("6ab0ff"), 0.35, 3)
    light(img, "ellipse", [lx - 30, ly - 26, lx + 30, ly + 36], BLUE, 0.25, 12)
    light(img, "ellipse", [cat_eye := 393, 154, 399, 157], hx("a0e0ff"), 0.0, 0)
    d = ImageDraw.Draw(img)
    lantern_glass(d)
    if ajar:
        door_glow(img)
        d = ImageDraw.Draw(img)
    glints(img, on)
    d.point((394, 155), fill=hx("b8f0ff"))
    d.point((397, 155), fill=hx("b8f0ff"))
    light(img, "rect", [fx0 - 2, fy0, fx1 + 2, fy1], hx("e0a860"), 0.18, 6)
    light(img, "ellipse", [20, -40, 100, 50], hx("8090c0"), 0.25, 18)
    if on:
        # the glow starts under the rim and fans downward; nothing shines up through the dish
        light(img, "polygon", [(sx - 13, sy + 5), (sx + 13, sy + 5), (sx + 34, sy + 40), (sx - 34, sy + 40)],
              hx("ffc870"), 0.28, 8)
        light(img, "ellipse", [sx - 6, sy + 3, sx + 6, sy + 11], hx("fff4d0"), 0.7, 1)
        light(img, "polygon", [(sx - 12, sy + 6), (sx + 12, sy + 6), (310, 250), (80, 250)], hx("f0a860"), 0.13, 8)
        light(img, "rect", [sx - 4, 200, sx + 4, 262], hx("ffe0a0"), 0.3, 3)  # streak on the wet stones
    shade(ImageDraw.Draw(img), on)
    return img


def moon(img):
    """A crisp lunar disc and shaded maria inside the existing misty halo, rather than a blurred white dot."""
    d = ImageDraw.Draw(img)
    dark, middle, bright, rim = MOON_COLORS
    d.ellipse([51, 1, 65, 15], fill=middle)
    d.ellipse([52, 2, 64, 14], fill=bright)
    d.arc([52, 2, 64, 14], 110, 285, fill=rim)
    for box in ([58, 4, 62, 8], [55, 8, 60, 12], [54, 4, 56, 6]):
        d.ellipse(box, fill=middle)
        d.arc(box, 20, 140, fill=rim)
    d.point((55, 5), fill=dark)
    d.point((61, 11), fill=middle)


def glints(img, on):
    """Specular sparkle on the wet cobble tops: warm under the lamp, a few cold ones from the moon."""
    rnd = random.Random(17)
    px = img.load()
    for _ in range(500):
        x, y = rnd.randint(0, W - 1), rnd.randint(BASE + 6, FULL_H - 1)
        r1, r2 = rnd.random(), rnd.random()
        dx, dy = (x - 206) / 120, (y - 228) / 36
        k = max(0.0, 1 - dx * dx - dy * dy)
        if k > 0 and r1 < 0.8:
            if on:
                px[x, y] = mix(px[x, y], (255, 220, 160), 0.25 + 0.5 * k)
        elif r2 < 0.18:
            px[x, y] = mix(px[x, y], (130, 150, 210), 0.35)


def reflections(img):
    """Puddles mirror the wall above them (flipped about the wall foot), rippled and darkened."""
    depth = FULL_H - BASE
    src = img.crop((0, BASE - depth, W, BASE)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    src = src.filter(ImageFilter.GaussianBlur(1.0))
    rip = Image.new("RGB", src.size)
    rnd = random.Random(4)
    for y in range(src.height):
        dx = int(round(math.sin(y * 0.8 + rnd.random()) * (1 + y / 40)))
        rip.paste(src.crop((0, y, W, y + 1)), (dx, y))
    rip = ImageChops.multiply(rip, Image.new("RGB", rip.size, (170, 180, 220)))
    mask = Image.new("L", (W, depth), 0)
    md = ImageDraw.Draw(mask)
    for y in range(depth):
        md.line([(0, y), (W, y)], fill=int(255 * 0.22 * (1 - y / depth)))
    for (x0, y0, x1, y1) in PUDDLES:
        md.ellipse([x0, y0 - BASE, x1, y1 - BASE], fill=200)
    mask = mask.filter(ImageFilter.GaussianBlur(1.0))
    region = img.crop((0, BASE, W, FULL_H))
    img.paste(Image.composite(ImageChops.lighter(region, rip), region, mask), (0, BASE))
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in PUDDLES:
        rim = img.getpixel(((x0 + x1) // 2, y0))
        d.arc([x0, y0, x1, y1], 200, 340, fill=mul(rim, 1.35))


def paint(on, ajar=False):
    img = Image.new("RGB", (W, FULL_H))
    sky(img)
    wires(img)
    _, far_box = passage(img)
    back_wall(img)
    door(img, ajar)
    fire_escape(img)
    ground(img)
    puddles_albedo(img)
    crates(img)
    trash_cans(img)
    lamppost(img, on)
    img = lighting(img, on, far_box, ajar)
    reflections(img)
    vignette(img, 0.5, tint=(14, 14, 34), blur=46)
    moon(img)
    return img


def door_overlay(closed, ajar):
    """The ajar door as an overlay: opaque only where it differs from the closed-door image under it."""
    diff = ImageChops.difference(closed, ajar).point(lambda v: 255 if v else 0)
    mask = ImageChops.lighter(ImageChops.lighter(*diff.split()[:2]), diff.split()[2])
    box = mask.getbbox()
    return cut(ajar, mask).crop(box), box


def variants():
    """The four pixelized states on one shared palette: lamp off/on, door shut/ajar."""
    off, on = paint(False), paint(True)
    ajar_off, ajar_on = paint(False, ajar=True), paint(True, ajar=True)
    both = Image.new("RGB", (W * 4, FULL_H))
    for i, img in enumerate((off, on, ajar_off, ajar_on)):
        both.paste(img, (W * i, 0))
    pal = palette_of(both, 124) + MOON_COLORS
    return tuple(pixelize(i, pal) for i in (off, on, ajar_off, ajar_on))


def build():
    """alley_door_open.png sits between the background and the lamp overlay; alley_door_open_lamp.png is a child
    of the lamp overlay, so the propped door stays right whichever way the lamp flickers."""
    px_off, px_on, px_ajar_off, px_ajar_on = variants()
    save(px_off, "rooms", "alley.png")
    box = ImageChops.difference(px_off, px_on).getbbox()
    save(px_on.crop(box), "rooms", "alley_lamp.png")
    print(f"  alley_lamp.png at {box[:2]} size {(box[2] - box[0], box[3] - box[1])}")
    for name, closed, ajar in (("alley_door_open.png", px_off, px_ajar_off),
                               ("alley_door_open_lamp.png", px_on, px_ajar_on)):
        overlay, at = door_overlay(closed, ajar)
        save(overlay, "rooms", name)
        print(f"  {name} at {at[:2]} size {overlay.size}")
    return px_off
