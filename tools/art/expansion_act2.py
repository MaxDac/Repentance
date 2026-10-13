"""Act 2 expansion locations: the Chicago Tribune's newspaper morgue (puzzle 13) and the vestibule of the Hall of the
Procession (puzzle 14), plus the inventory icons those puzzles hand out.

Like act2_rooms, each room is painted once per state; overlays are crops of the state variant pixelized with the base
palette, so they line up pixel-exactly when placed at the top-left printed by build()."""
import random
from PIL import Image, ImageDraw, ImageChops
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, palette_of, pixelize, save, text
from .act2_rooms import overlay
from .items import _icon, invitation

H = FULL_H
FLOOR = 190


# ------------------------------------------------------------------------------------------------ THE TRIBUNE MORGUE

DRAWERS = "ABCDEFGHIJKL"  # three cabinets, four rows, filed row by row: H is the middle cabinet, third row
CAB_X = (92, 132, 172)
CAB_Y = (98, 122, 146, 170)
MAP_BOX = (224, 34, 334, 120)
LASALLE = (262, 82)  # where the Harrington Building sits on the Loop map


def _drawer(d, img, x, y, letter, opened):
    if opened:
        # pulled out a hand's width: the dark well, folder tabs riffled, the front hanging lower
        d.rectangle([x + 1, y - 2, x + 37, y + 8], fill=hx("0e0e0a"))
        for i, fx in enumerate(range(x + 4, x + 35, 5)):
            d.rectangle([fx, y - 1 + (i % 2), fx + 3, y + 6], fill=hx("b8aa82") if i % 3 else hx("d8cca8"))
        d.rectangle([x - 2, y + 8, x + 40, y + 30], fill=hx("6a6a5a"), outline=hx("1a1a14"))
        d.rectangle([x + 15, y + 12, x + 23, y + 18], fill=hx("e8e0c8"), outline=hx("2a2a20"))
        text(img, (x + 19, y + 15), letter, hx("1a1a14"), size=8)
        d.rectangle([x + 13, y + 22, x + 25, y + 24], fill=hx("b0aa90"))
        return
    d.rectangle([x + 1, y, x + 37, y + 22], fill=hx("5a5a4c"), outline=hx("22221a"))
    d.line([(x + 2, y + 1), (x + 36, y + 1)], fill=hx("7a7a68"))
    d.rectangle([x + 15, y + 4, x + 23, y + 10], fill=hx("e0d8c0"), outline=hx("2a2a20"))
    text(img, (x + 19, y + 7), letter, hx("1a1a14"), size=8)
    d.rectangle([x + 13, y + 14, x + 25, y + 16], fill=hx("a8a490"))


def _loop_map(d, img, pin):
    x0, y0, x1, y1 = MAP_BOX
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], fill=hx("3a2614"), outline=hx("140a04"))
    d.rectangle([x0, y0, x1, y1], fill=hx("d4c8a2"))
    for gx in range(x0 + 4, x1, 7):
        d.line([(gx, y0), (gx, y1)], fill=hx("b8aa82"))
    for gy in range(y0 + 3, y1, 6):
        d.line([(x0, gy), (x1, gy)], fill=hx("b8aa82"))
    # LaSalle Street runs heavier through the middle of the Loop
    d.line([(LASALLE[0], y0), (LASALLE[0], y1)], fill=hx("8a7a58"))
    # the lake to the east, the river across the top and down the west side
    d.polygon([(x1 - 12, y0), (x1, y0), (x1, y1), (x1 - 8, y1)], fill=hx("6a88a0"))
    d.line([(x0, y0 + 14), (x0 + 18, y0 + 16), (x1 - 12, y0 + 18)], fill=hx("587890"), width=3)
    d.line([(x0 + 18, y0 + 16), (x0 + 16, y1)], fill=hx("587890"), width=3)
    rnd = random.Random(1327)
    for _ in range(46):
        px, py = rnd.randint(x0 + 22, x1 - 16), rnd.randint(y0 + 22, y1 - 4)
        d.point((px, py), fill=hx(rnd.choice(("8a1a1a", "1a2a6a", "1a1a1a", "2a5a2a"))))
    if pin:
        # the mended clipping pinned up beside a fat red pin on LaSalle
        cx, cy = LASALLE
        d.rectangle([cx + 2, cy - 3, cx + 18, cy + 9], fill=hx("ece4cc"), outline=hx("6a6050"))
        d.line([(cx + 4, cy), (cx + 16, cy)], fill=hx("2a2a2a"))
        for ly in (cy + 3, cy + 5, cy + 7):
            d.line([(cx + 4, ly), (cx + 15, ly)], fill=hx("8a8270"))
        d.line([(cx + 2, cy + 3), (cx + 18, cy + 3)], fill=hx("c8b878"))
        d.line([(cx, cy), (cx + 6, cy - 1)], fill=hx("2a2a2a"))
        d.ellipse([cx - 3, cy - 3, cx + 2, cy + 2], fill=hx("d02020"), outline=hx("6a0a0a"))
        d.point((cx - 2, cy - 2), fill=hx("ff8a7a"))
    # brass plate under the frame
    d.rectangle([254, 126, 304, 134], fill=hx("a08a40"), outline=hx("4a3a14"))
    text(img, (279, 130), "THE LOOP", hx("2a2010"), size=8)


SPIKE_X = 314
DESK_Y = 156  # top of the layout desk: about belt height on Micah standing in front of it


def _sheet(d, x0, y, col, edge="6a6050"):
    """A sheet of copy stuck flat on the spike, a little askew, typed lines across it and the hole the spike made."""
    d.polygon([(x0, y), (x0 + 21, y - 2), (x0 + 22, y + 4), (x0 + 1, y + 6)], fill=hx(col), outline=hx(edge))
    for k in (2, 4):
        d.line([(x0 + 3, y + k), (x0 + 8, y + k - 1)], fill=hx("8a8270"))
        d.line([(x0 + 13, y + k - 1), (x0 + 19, y + k - 2)], fill=hx("8a8270"))
    d.point((SPIKE_X, y + 1), fill=hx("2a2a24"))


def _spike_stand(d, taken):
    sx = SPIKE_X
    # a small oak stand, lit along its front edge, the wastebasket underneath
    d.rectangle([292, 150, 340, 156], fill=hx("5a3c24"), outline=hx("1e1208"))
    d.line([(293, 151), (339, 151)], fill=hx("7a5634"))
    d.line([(293, 155), (339, 155)], fill=hx("3a2614"))
    for lx in (296, 332):
        d.rectangle([lx, 156, lx + 4, FLOOR + 4], fill=hx("3a2614"), outline=hx("1e1208"))
        d.line([(lx + 1, 157), (lx + 1, FLOOR + 3)], fill=hx("5a3c24"))
    d.polygon([(304, 166), (328, 166), (325, FLOOR + 6), (307, FLOOR + 6)], fill=hx("4a4a42"), outline=hx("1a1a14"))
    d.line([(304, 167), (328, 167)], fill=hx("6a6a60"))
    for x in range(308, 326, 4):
        d.line([(x, 169), (x, FLOOR + 4)], fill=hx("2e2e28"))
    d.ellipse([306, 160, 316, 168], fill=hx("c8c0a8"), outline=hx("6a6050"))
    d.ellipse([314, 162, 324, 169], fill=hx("b8b098"), outline=hx("5a5242"))
    # the spike: a cast-iron foot, a steel collar, and a needle of polished steel lit on the lamp side
    d.ellipse([302, 144, 326, 153], fill=hx("1a1a18"), outline=hx("0a0a08"))
    d.ellipse([305, 144, 323, 149], fill=hx("3a3a36"))
    d.arc([305, 144, 323, 149], 190, 290, fill=hx("7a7a72"))
    d.rectangle([sx - 2, 140, sx + 3, 145], fill=hx("5a5a54"), outline=hx("1a1a18"))
    d.line([(sx - 1, 141), (sx - 1, 144)], fill=hx("9a9a92"))
    d.line([(sx, 140), (sx, 102)], fill=hx("d4d4cc"))
    d.line([(sx + 1, 140), (sx + 1, 104)], fill=hx("5a5a54"))
    d.point((sx, 101), fill=hx("a8a8a0"))
    d.point((sx, 100), fill=hx("f4f4ec"))
    # dead copy, rammed down to the foot
    for y, x0, c in ((136, 303, "c0b89c"), (132, 304, "d0c8ae"), (128, 303, "c8c0a8")):
        _sheet(d, x0, y, c)
    if taken:
        return
    # the torn bottom half of the Harrington clipping on top: ragged edge up, the photo caption, the address line
    x0, y = 304, 123
    d.polygon([(x0, y), (x0 + 21, y - 2), (x0 + 22, y + 5), (x0 + 1, y + 7)], fill=hx("ece4cc"), outline=hx("8a8270"))
    for i, tx in enumerate(range(x0 + 1, x0 + 21, 2)):
        d.point((tx, round(y - 2 * (tx - x0) / 21) - 1 - (i % 2)), fill=hx("ece4cc"))
    d.rectangle([x0 + 3, y + 1, x0 + 8, y + 4], fill=hx("6a6458"))
    d.line([(x0 + 4, y + 2), (x0 + 7, y + 2)], fill=hx("9a9282"))
    d.line([(x0 + 10, y + 1), (x0 + 19, y)], fill=hx("2a2a2a"))
    d.line([(x0 + 10, y + 3), (x0 + 18, y + 2)], fill=hx("6a6252"))
    d.line([(x0 + 3, y + 6), (x0 + 18, y + 4)], fill=hx("8a8270"))
    d.point((sx, y + 2), fill=hx("2a2a24"))


def _layout_desk(d, paste):
    y = DESK_Y
    # the top, seen a little from above, a lit front edge, a shallow drawer, and a stretcher between the legs
    d.rectangle([344, y - 4, 464, y], fill=hx("7a5634"))
    d.line([(344, y - 4), (464, y - 4)], fill=hx("8e6a42"))
    d.rectangle([342, y, 466, y + 5], fill=hx("6a4a2a"), outline=hx("1e1208"))
    d.line([(343, y + 1), (465, y + 1)], fill=hx("8a643a"))
    for lx in (348, 454):
        d.rectangle([lx, y + 5, lx + 6, FLOOR + 6], fill=hx("4a3018"), outline=hx("1e1208"))
        d.line([(lx + 1, y + 6), (lx + 1, FLOOR + 5)], fill=hx("6a4a2a"))
    d.rectangle([388, y + 5, 428, y + 13], fill=hx("5a3c22"), outline=hx("1e1208"))
    d.rectangle([404, y + 8, 412, y + 10], fill=hx("a08a40"), outline=hx("4a3a14"))
    d.rectangle([354, y + 26, 454, y + 29], fill=hx("4a3018"), outline=hx("2a1a0c"))
    # tomorrow's dummy pages, pasted up in columns
    for x0 in (374, 402):
        d.polygon([(x0 + 2, y - 5), (x0 + 25, y - 5), (x0 + 24, y - 1), (x0, y - 1)], fill=hx("e4dcc4"),
                  outline=hx("8a8270"))
        d.line([(x0 + 3, y - 4), (x0 + 22, y - 4)], fill=hx("3a3a34"))
        for gx in range(x0 + 4, x0 + 23, 5):
            d.line([(gx, y - 3), (gx - 1, y - 2)], fill=hx("8a8270"))
    # gooseneck lamp: weighted foot, a brass-jointed arm, a green enamel shade tipped over the pages
    bx = 360
    d.ellipse([bx - 8, y - 6, bx + 8, y - 1], fill=hx("1a2e1c"), outline=hx("0a140a"))
    d.ellipse([bx - 6, y - 6, bx + 6, y - 3], fill=hx("2e4e30"))
    d.point((bx - 3, y - 5), fill=hx("7aaa7a"))
    d.rectangle([bx + 4, y - 5, bx + 5, y - 4], fill=hx("a08a40"))
    d.line([(bx, y - 6), (bx, y - 22)], fill=hx("b09a50"))
    d.line([(bx + 1, y - 6), (bx + 1, y - 22)], fill=hx("4a3a14"))
    d.ellipse([bx - 2, y - 26, bx + 3, y - 21], fill=hx("a08a40"), outline=hx("3a2a0c"))
    d.line([(bx + 2, y - 25), (bx + 14, y - 35)], fill=hx("c8b060"))
    d.line([(bx + 3, y - 24), (bx + 15, y - 34)], fill=hx("4a3a14"))
    d.ellipse([bx + 13, y - 38, bx + 18, y - 33], fill=hx("a08a40"), outline=hx("3a2a0c"))
    sx = bx + 16
    d.polygon([(sx - 4, y - 37), (sx + 4, y - 37), (sx + 11, y - 25), (sx - 11, y - 25)], fill=hx("2a5a2e"),
              outline=hx("0e1e10"))
    d.line([(sx - 3, y - 36), (sx - 9, y - 26)], fill=hx("6a9a68"))
    d.line([(sx + 3, y - 36), (sx + 9, y - 26)], fill=hx("1a3a1e"))
    d.ellipse([sx - 5, y - 40, sx + 5, y - 35], fill=hx("1e3e22"), outline=hx("0e1e10"))
    d.point((sx, y - 41), fill=hx("c8b060"))
    d.line([(sx - 11, y - 25), (sx + 11, y - 25)], fill=hx("0e1e10"))
    d.ellipse([sx - 10, y - 26, sx + 10, y - 22], fill=hx("e8dcb0"))
    d.ellipse([sx - 3, y - 25, sx + 3, y - 21], fill=hx("fff4cc"))
    # the paste pot at the end, brush standing in it
    if paste:
        d.ellipse([428, y - 3, 446, y + 1], fill=hx("5a3e22"))
        return
    d.rectangle([428, y - 14, 446, y], fill=hx("e8e4d8"), outline=hx("4a4a44"))
    d.rectangle([428, y - 10, 446, y - 6], fill=hx("6a2a2a"))
    d.line([(430, y - 9), (444, y - 9)], fill=hx("8a4a3a"))
    d.ellipse([428, y - 17, 446, y - 11], fill=hx("f0ecdc"), outline=hx("4a4a44"))
    d.line([(440, y - 14), (446, y - 28)], fill=hx("8a6a3a"), width=2)
    d.rectangle([438, y - 16, 442, y - 13], fill=hx("c8c0a0"))


def _ceiling_lamp(d):
    """Enamel dome on a chain from a ceiling rose: brass socket, white underside, a bare bulb glowing in it."""
    cx = 250
    d.rectangle([cx - 5, 10, cx + 5, 13], fill=hx("3a3a30"), outline=hx("14140e"))
    for y in range(14, 21):
        d.point((cx, y), fill=hx("8a8a70") if y % 2 else hx("2a2a20"))
        d.point((cx + 1, y), fill=hx("4a4a3a") if y % 2 else hx("1a1a14"))
    d.rectangle([cx - 3, 20, cx + 4, 24], fill=hx("a08a40"), outline=hx("4a3a14"))
    d.line([(cx - 2, 21), (cx - 2, 23)], fill=hx("e0c870"))
    d.polygon([(cx - 6, 24), (cx + 7, 24), (cx + 16, 32), (cx + 22, 36), (cx - 21, 36), (cx - 15, 32)],
              fill=hx("2a5a2e"), outline=hx("0e1e10"))
    d.line([(cx - 5, 25), (cx - 16, 33)], fill=hx("7aaa78"))
    d.line([(cx - 4, 25), (cx - 13, 32)], fill=hx("4a7a4a"))
    d.line([(cx + 7, 25), (cx + 18, 34)], fill=hx("1a3a1e"))
    d.line([(cx - 21, 36), (cx + 22, 36)], fill=hx("c8b060"))
    d.ellipse([cx - 19, 35, cx + 20, 41], fill=hx("e8dcb0"), outline=hx("8a7a50"))
    d.ellipse([cx - 5, 35, cx + 6, 43], fill=hx("fff4cc"), outline=hx("e0c070"))
    d.point((cx - 2, 37), fill=hx("ffffff"))


def paint_morgue(drawer=False, spike=False, paste=False, pin=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # tired institutional green above a brown wainscot; pipes under the ceiling
    vgrad(img, (0, 0, W - 1, FLOOR), hx("4a5240"), hx("343a2c"))
    d.rectangle([0, 0, W - 1, 12], fill=hx("22261c"))
    for y, c in ((16, "5a5a50"), (21, "4a4a42")):
        d.rectangle([0, y, W - 1, y + 2], fill=hx(c))
    d.rectangle([0, 142, W - 1, FLOOR], fill=hx("3a2a1c"))
    d.rectangle([0, 140, W - 1, 143], fill=hx("5a4228"))
    for x in range(0, W, 30):
        d.line([(x, 146), (x, FLOOR - 2)], fill=hx("2a1c10"))
    noise(img, (0, 0, W - 1, FLOOR), 4, 1301)
    # worn linoleum, squares running back to the wall
    vgrad(img, (0, FLOOR, W - 1, H - 1), hx("4a4436"), hx("5e5644"))
    for i, y in enumerate((FLOOR, 198, 208, 220, 234, 251)):
        d.line([(0, y), (W - 1, y)], fill=hx("2e2a20"))
    for k in range(-12, 13):
        d.line([(W // 2 + k * 30, FLOOR), (W // 2 + k * 52, H - 1)], fill=hx("2e2a20"))
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 1302)
    # the door out, frosted glass lettered backwards from this side
    d.rectangle([12, 66, 76, FLOOR + 2], fill=hx("3a2614"), outline=hx("140a04"))
    d.rectangle([18, 72, 70, FLOOR], fill=hx("4e321c"), outline=hx("1e1208"))
    d.rectangle([24, 78, 64, 126], fill=hx("9aa496"), outline=hx("1e1208"))
    text(img, (44, 98), "MORGUE", hx("2a2a24"), size=8, mirror=True)
    d.rectangle([24, 136, 64, 182], outline=hx("2a1a0c"))
    d.ellipse([62, 146, 67, 151], fill=hx("c8a858"))
    # three steel filing cabinets; the clippings filed by name
    d.rectangle([88, 92, 214, 96], fill=hx("4a4a40"))
    for cx in CAB_X:
        d.rectangle([cx - 2, 94, cx + 40, FLOOR + 2], fill=hx("44443a"), outline=hx("1a1a14"))
    for i, letter in enumerate(DRAWERS):
        x, y = CAB_X[i % 3], CAB_Y[i // 3]
        if letter != "H":
            _drawer(d, img, x, y, letter, False)
    _drawer(d, img, CAB_X[1], CAB_Y[2], "H", drawer)
    # a box of old editions stacked on the cabinets
    d.rectangle([96, 76, 126, 92], fill=hx("8a7450"), outline=hx("3a2a14"))
    d.rectangle([178, 82, 206, 92], fill=hx("c8bc98"), outline=hx("5a5040"))
    for y in (85, 88):
        d.line([(180, y), (204, y)], fill=hx("6a6050"))
    _loop_map(d, img, pin)
    _spike_stand(d, spike)
    _layout_desk(d, paste)
    _ceiling_lamp(d)
    light(img, "polygon", [(234, 38), (266, 38), (420, H - 1), (80, H - 1)], hx("c8a868"), 0.22, 18)
    light(img, "ellipse", [236, 28, 264, 50], hx("ffe8a8"), 0.35, 5)
    light(img, "ellipse", [358, 128, 420, 164], hx("e0c070"), 0.24, 7)
    shadow(img, "rect", [0, FLOOR, W - 1, FLOOR + 10], 0.25, 4)
    vignette(img, 0.55, (14, 14, 10), 40)
    return img


def build_morgue():
    base = paint_morgue()
    v = {"drawer": paint_morgue(drawer=True), "spike": paint_morgue(spike=True),
         "paste": paint_morgue(paste=True), "pin": paint_morgue(pin=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.4)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "newspaper_morgue.png")
    overlay(v["drawer"], px, pal, (126, 140, 178, 182), "newspaper_morgue_drawer")
    overlay(v["spike"], px, pal, (298, 112, 330, 136), "newspaper_morgue_spike")
    overlay(v["paste"], px, pal, (424, 124, 452, 160), "newspaper_morgue_paste")
    overlay(v["pin"], px, pal, (254, 74, 284, 96), "newspaper_morgue_pin")
    return px


# ------------------------------------------------------------------------------------------------ THE VESTIBULE

# hung out of procession order, so the plaque and the invitation have to tell Micah which one leads
CLOAKS = (("lion", 228, "d8b048"), ("stag", 258, "8a6a3a"), ("raven", 288, "c8ccd4"))
INNER = (368, 46, 452, FLOOR + 2)


def _emblem(d, kind, cx, cy, col):
    c = hx(col)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=hx("1a1418"), outline=c)
    if kind == "raven":
        d.polygon([(cx - 3, cy), (cx, cy - 2), (cx + 3, cy - 1), (cx + 1, cy + 2)], fill=c)
    elif kind == "lion":
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)
    else:
        d.line([(cx - 2, cy - 3), (cx, cy), (cx + 2, cy - 3)], fill=c)
        d.line([(cx, cy), (cx, cy + 2)], fill=c)


def paint_vestibule(wax=False, door=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gold, gold_d = hx("c8a050"), hx("7a5a24")
    # wine-dark damask walls, a gilt frieze, a black ceiling
    vgrad(img, (0, 0, W - 1, FLOOR), hx("4a1624"), hx("2a0a14"))
    rnd = random.Random(1401)
    for y in range(40, 170, 16):
        for x in range((y // 16 % 2) * 12, W, 24):
            d.polygon([(x, y - 4), (x + 4, y), (x, y + 4), (x - 4, y)], fill=hx("561c2c"))
    d.rectangle([0, 0, W - 1, 20], fill=hx("140a10"))
    d.rectangle([0, 20, W - 1, 24], fill=gold_d)
    for x in range(0, W, 10):
        d.polygon([(x, 24), (x + 5, 30), (x + 10, 24)], fill=gold_d)
    d.rectangle([0, 166, W - 1, FLOOR], fill=hx("1e0a10"))
    d.line([(0, 166), (W - 1, 166)], fill=gold)
    noise(img, (0, 0, W - 1, FLOOR), 4, 1402)
    # black and white marble, the checks widening towards us
    rows = (FLOOR, 198, 208, 220, 235, 252, H)
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        for k in range(-14, 14):
            xa0, xa1 = W // 2 + k * (24 + r * 4), W // 2 + (k + 1) * (24 + r * 4)
            xb0, xb1 = W // 2 + k * (28 + r * 4), W // 2 + (k + 1) * (28 + r * 4)
            c = hx("a49a8c") if (k + r) % 2 else hx("1e1a1c")
            d.polygon([(xa0, ya), (xa1, ya), (xb1, yb), (xb0, yb)], fill=c)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 1403)
    # the street door we came in by
    d.rectangle([14, 62, 74, FLOOR + 2], fill=hx("2a160c"), outline=hx("0a0402"))
    d.line([(44, 62), (44, FLOOR + 2)], fill=hx("0a0402"))
    for x0 in (20, 50):
        d.rectangle([x0, 70, x0 + 18, 120], outline=hx("140a04"))
        d.rectangle([x0, 130, x0 + 18, 182], outline=hx("140a04"))
    d.rectangle([40, 140, 42, 152], fill=gold)
    d.rectangle([46, 140, 48, 152], fill=gold)
    # the coat check: a hatch in the wall, a counter with the house wax laid out for the summons
    d.rectangle([86, 66, 198, 142], fill=hx("120608"), outline=gold_d)
    for x in range(98, 192, 14):
        d.line([(x, 78), (x, 84)], fill=hx("8a7a50"))
        d.polygon([(x - 5, 84), (x + 5, 84), (x + 6, 128), (x - 6, 128)], fill=hx("1e1a22"))
    d.rectangle([116, 54, 168, 64], fill=gold_d, outline=hx("3a2a10"))
    text(img, (142, 59), "CLOAKS", hx("1a1008"), size=8)
    d.rectangle([80, 142, 204, 148], fill=hx("6a2a1a"), outline=gold)
    d.rectangle([84, 148, 200, FLOOR + 2], fill=hx("3a1018"), outline=hx("140408"))
    for x0 in (90, 130, 170):
        d.rectangle([x0, 154, x0 + 26, FLOOR - 4], outline=gold_d)
    d.ellipse([90, 136, 100, 143], fill=gold)
    d.rectangle([94, 134, 96, 136], fill=gold)
    d.rectangle([150, 139, 182, 142], fill=hx("2a2028"), outline=gold_d)
    if not wax:
        d.rectangle([154, 136, 176, 139], fill=hx("a01818"))
        d.rectangle([154, 136, 176, 136], fill=hx("d04040"))
        d.rectangle([176, 137, 178, 138], fill=hx("e8e0d0"))
    # the cloak rack: three hooded cloaks, an emblem worked at each breast, a signet on each clasp
    d.rectangle([214, 52, 302, 56], fill=gold_d)
    d.rectangle([256, 56, 260, FLOOR], fill=gold_d)
    d.ellipse([244, FLOOR - 4, 272, FLOOR + 4], fill=gold_d)
    for kind, cx, col in CLOAKS:
        d.line([(cx, 56), (cx, 64)], fill=gold)
        d.ellipse([cx - 8, 62, cx + 8, 78], fill=hx("1a161e"))
        d.polygon([(cx - 8, 72), (cx + 8, 72), (cx + 14, 172), (cx - 14, 172)], fill=hx("16141a"))
        d.line([(cx, 80), (cx, 172)], fill=hx("0c0a10"))
        d.line([(cx - 8, 74), (cx - 13, 168)], fill=hx("26222c"))
        _emblem(d, kind, cx, 98, col)
        d.ellipse([cx - 2, 76, cx + 2, 80], outline=gold)
    # the brass plaque and the inner door with its card slot
    d.rectangle([316, 94, 360, 118], fill=hx("b08a3a"), outline=hx("4a3412"))
    d.rectangle([318, 96, 358, 116], outline=hx("e0c070"))
    for y in (101, 105, 109):
        d.line([(322, y), (354, y)], fill=hx("5a4418"))
    x0, y0, x1, y1 = INNER
    d.rectangle([x0 - 6, y0 - 6, x1 + 6, y1], fill=gold_d, outline=hx("2a1a08"))
    d.pieslice([x0 - 6, y0 - 26, x1 + 6, y0 + 14], 180, 360, fill=gold_d)
    d.pieslice([x0, y0 - 20, x1, y0 + 8], 180, 360, fill=hx("1a0a0e"))
    mx = (x0 + x1) // 2
    if door:
        d.rectangle([x0, y0, x1, y1], fill=hx("2a0e0a"))
        d.polygon([(mx - 16, y1), (mx + 16, y1), (mx + 8, y0 + 60), (mx - 8, y0 + 60)], fill=hx("6a1418"))
        d.polygon([(x0, y0), (x0 + 12, y0 + 6), (x0 + 12, y1 - 4), (x0, y1)], fill=hx("2a0a10"), outline=hx("0a0204"))
        d.polygon([(x1, y0), (x1 - 12, y0 + 6), (x1 - 12, y1 - 4), (x1, y1)], fill=hx("2a0a10"), outline=hx("0a0204"))
    else:
        d.rectangle([x0, y0, x1, y1], fill=hx("2a0a10"), outline=hx("0a0204"))
        d.line([(mx, y0), (mx, y1)], fill=hx("0a0204"))
        for a, b in ((x0 + 6, mx - 6), (mx + 6, x1 - 6)):
            d.rectangle([a, y0 + 10, b, y0 + 60], outline=gold_d)
            d.rectangle([a, y0 + 92, b, y1 - 10], outline=gold_d)
        d.rectangle([mx - 9, 114, mx + 9, 128], fill=hx("b08a3a"), outline=hx("4a3412"))
        d.rectangle([mx - 6, 120, mx + 6, 122], fill=hx("0a0204"))
        d.rectangle([mx - 7, 140, mx - 5, 152], fill=gold)
        d.rectangle([mx + 5, 140, mx + 7, 152], fill=gold)
    # sconces
    for sx in (206, 310, 464):
        d.rectangle([sx - 2, 70, sx + 2, 80], fill=gold)
        d.polygon([(sx - 5, 62), (sx + 5, 62), (sx + 3, 70), (sx - 3, 70)], fill=hx("f0d088"))
        light(img, "ellipse", [sx - 34, 36, sx + 34, 110], hx("e0a050"), 0.2, 14)
    if door:
        light(img, "polygon", [(x0, y0), (x1, y0), (x1 + 30, H - 1), (x0 - 30, H - 1)], hx("e08040"), 0.3, 10)
    vignette(img, 0.6, (16, 6, 12), 40)
    return img


def build_vestibule():
    base = paint_vestibule()
    v = {"wax": paint_vestibule(wax=True), "door": paint_vestibule(door=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.4)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "club_vestibule.png")
    overlay(v["wax"], px, pal, (150, 132, 182, 142), "club_vestibule_wax")
    overlay(v["door"], px, pal, (320, 20, 479, H - 1), "club_vestibule_door")
    return px


# ------------------------------------------------------------------------------------------------ ICONS

def _newsprint(d, top, bottom):
    for y in range(top, bottom, 3):
        d.line([(6, y), (25, y)], fill=hx("8a8474"))


def clipping_top(d, im):
    """The upper half of a clipping: the headline, torn ragged straight through the address."""
    pts = [(4, 3), (27, 2), (28, 13)] + [(26 - i * 3, 13 + (i % 2) * 2) for i in range(8)] + [(4, 14)]
    d.polygon(pts, fill=hx("e6dec4"))
    d.rectangle([6, 4, 25, 6], fill=hx("1e1c1a"))
    _newsprint(d, 9, 13)


def clipping_bottom(d, im):
    """The lower half: column type and the edge of a photograph, torn ragged at the top."""
    pts = [(4, 9)] + [(4 + i * 3, 9 + (i % 2) * 2) for i in range(1, 8)] + [(27, 10), (28, 21), (5, 22)]
    d.polygon(pts, fill=hx("e6dec4"))
    d.rectangle([18, 13, 25, 19], fill=hx("6a6458"))
    for y in range(13, 21, 3):
        d.line([(7, y), (15, y)], fill=hx("8a8474"))


def clipping(d, im):
    """The two halves pasted back together on a backing sheet, the seam yellow with paste."""
    d.polygon([(3, 2), (28, 1), (29, 22), (4, 22)], fill=hx("e6dec4"))
    d.rectangle([6, 3, 25, 5], fill=hx("1e1c1a"))
    _newsprint(d, 8, 11)
    for i in range(8):
        d.line([(4 + i * 3, 12 + (i % 2)), (6 + i * 3, 12 + ((i + 1) % 2))], fill=hx("c8b060"))
    d.rectangle([18, 15, 25, 20], fill=hx("6a6458"))
    for y in range(15, 21, 3):
        d.line([(7, y), (15, y)], fill=hx("8a8474"))


def paste(d, im):
    """A squat stoneware paste pot, the brush standing in it."""
    d.line([(19, 1), (23, 10)], fill=hx("8a6a3a"), width=2)
    d.rectangle([9, 9, 23, 21], fill=hx("e8e4d8"))
    d.rectangle([9, 13, 23, 16], fill=hx("6a2a2a"))
    d.ellipse([9, 7, 23, 11], fill=hx("f4f0e4"))
    d.ellipse([11, 8, 21, 10], fill=hx("d8d0b8"))


def sealing_wax(d, im):
    """A stick of red sealing wax, cold and square-cut."""
    d.polygon([(4, 16), (24, 6), (27, 10), (7, 20)], fill=hx("a81c1c"))
    d.polygon([(24, 6), (27, 10), (28, 8), (25, 4)], fill=hx("d84a40"))
    d.line([(6, 16), (23, 8)], fill=hx("d04040"))


def wax_soft(d, im):
    """The wax stick, its end glossy and slumping, a drip about to fall."""
    sealing_wax(d, im)
    d.ellipse([22, 3, 30, 11], fill=hx("e83a2a"))
    d.ellipse([24, 10, 28, 16], fill=hx("d02a20"))
    d.point((24, 5), fill=hx("ffb0a0"))


def _seal(d, col, mark=None):
    d.ellipse([18, 9, 28, 19], fill=hx(col))
    d.arc([18, 9, 28, 19], 200, 340, fill=hx("e06050"))
    if mark:
        d.polygon([(20, 14), (23, 12), (26, 13), (24, 16)], fill=hx(mark))


def invitation_waxed(d, im):
    """The invitation with a soft red blob of wax waiting for a seal."""
    invitation(d, im)
    _seal(d, "b82020")


def sealed_invitation(d, im):
    """The invitation sealed in red, the raven pressed into the wax."""
    invitation(d, im)
    _seal(d, "9a1818", "3a0606")


def _signet(d, face, mark):
    d.ellipse([7, 8, 25, 22], outline=hx("c8a040"), width=3)
    d.ellipse([10, 1, 22, 11], fill=hx("a88030"))
    d.ellipse([12, 2, 20, 10], fill=hx(face))
    mark(d)


def signet_raven(d, im):
    """A gold signet with an onyx face: a raven in flight cut into it."""
    _signet(d, "16141a", lambda d: d.polygon([(13, 6), (16, 4), (19, 5), (17, 8)], fill=hx("c8ccd4")))


def signet_lion(d, im):
    """A gold signet: a lion's maned head on a red face."""
    _signet(d, "7a1a1a", lambda d: d.ellipse([14, 4, 18, 8], fill=hx("e8c060")))


def signet_stag(d, im):
    """A gold signet: a stag's antlers on a green face."""
    def mark(d):
        d.line([(13, 3), (16, 6), (19, 3)], fill=hx("e8c060"))
        d.line([(16, 6), (16, 9)], fill=hx("e8c060"))
    _signet(d, "1e4a2a", mark)


ICONS = (("clipping_top", clipping_top), ("clipping_bottom", clipping_bottom), ("clipping", clipping),
         ("paste", paste), ("sealing_wax", sealing_wax), ("wax_soft", wax_soft),
         ("invitation_waxed", invitation_waxed), ("sealed_invitation", sealed_invitation),
         ("signet_raven", signet_raven), ("signet_lion", signet_lion), ("signet_stag", signet_stag))


def build():
    build_morgue()
    build_vestibule()
    for name, fn in ICONS:
        save(_icon(fn), "items", f"{name}.png")
