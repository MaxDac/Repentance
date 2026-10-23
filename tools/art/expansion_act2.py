"""Act 2 expansion locations: the Chicago Tribune's newspaper morgue (puzzle 13) and the vestibule of the Hall of the
Procession (puzzle 14), plus the inventory icons those puzzles hand out.

Like act2_rooms, each room is painted once per state; overlays are crops of the state variant pixelized with the base
palette, so they line up pixel-exactly when placed at the top-left printed by build()."""
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, palette_of, pixelize, save, text
from .act2_rooms import overlay
from .items import _icon, invitation
from . import chicago_map

H = FULL_H
FLOOR = 190


# ------------------------------------------------------------------------------------------------ THE TRIBUNE MORGUE

DRAWERS = "ABCDEFGHIJKL"  # three cabinets, four rows, filed row by row: H is the middle cabinet, third row
CAB_X = (92, 132, 172)
CAB_Y = (98, 122, 146, 170)
MAP_BOX = (224, 34, 334, 120)
# The Loop on the 1920 Fred Wild street map the location-select screen prints (source-scan pixels): the river's
# branches to the north and west, Grant Park and the lake shore to the east, Congress Street to the south.
LOOP_SRC = (830, 500, 1380, 930)


def _on_loop_map(scan_pt):
    x0, y0, x1, y1 = MAP_BOX
    sx0, sy0, sx1, sy1 = LOOP_SRC
    return (round(x0 + (scan_pt[0] - sx0) * (x1 - x0) / (sx1 - sx0)),
            round(y0 + (scan_pt[1] - sy0) * (y1 - y0) / (sy1 - sy0)))


# the Harrington Building on LaSalle Street, the same spot the location-select map pins
LASALLE = _on_loop_map(chicago_map.scan_point(chicago_map.MARKERS["harrington"][0]))

MANILA = ("d6c290", "c4ae7a", "e0d0a4", "b8a06c", "ccb888")


def _folders(d, x, y):
    """Hanging files seen from above in the pulled-out drawer: each folder's top edge, back to front, its tab up."""
    rnd = random.Random(1309)
    rows = list(range(y + 1, y + 12, 2))
    for i, fy in enumerate(rows):
        t = i / (len(rows) - 1)
        lx, rx = round(x + 2 - 3 * t), round(x + 36 + 3 * t)
        depth = 0.62 + 0.38 * t  # the back of the drawer is in the cabinet's shadow
        col = mul(hx(MANILA[i % len(MANILA)]), depth)
        harrington = i == 3
        if harrington:
            # Harrington's file, pulled up from the others: a clipping's corner showing over its lip
            d.rectangle([lx + 9, fy - 4, lx + 20, fy - 1], fill=hx("ece4cc"), outline=hx("7a7260"))
            d.line([(lx + 11, fy - 3), (lx + 18, fy - 3)], fill=hx("3a3a34"))
            d.point((lx + 15, fy - 2), fill=hx("8a8270"))
            fy -= 2
        d.rectangle([lx, fy, rx, fy + 1], fill=col)
        d.line([(lx, fy), (rx, fy)], fill=mul(col, 1.18))
        d.line([(lx, fy + 2), (rx, fy + 2)], fill=mul(col, 0.42))
        # creases where the folder's sides bend over the hanging rods, and dog-ears
        for cx in (lx + 1, rx - 1):
            d.point((cx, fy + 1), fill=mul(col, 0.7))
        d.point((lx + rnd.randint(4, 30), fy), fill=mul(col, 0.8))
        # the tab, staggered left/middle/right down the drawer, a typed label strip on it
        tx = lx + 3 + (i % 3) * 11
        tab = hx("f2ead2") if harrington else mul(col, 1.08)
        d.rectangle([tx, fy - 2, tx + 7, fy - 1], fill=tab)
        d.line([(tx, fy - 2), (tx + 7, fy - 2)], fill=mul(tab, 1.1))
        d.point((tx - 1, fy - 1), fill=mul(col, 0.6))
        d.point((tx + 8, fy - 1), fill=mul(col, 0.6))
        d.line([(tx + 2, fy - 1), (tx + 5, fy - 1)], fill=hx("a01e1a") if harrington else mul(col, 0.45))
    # a pressboard guide card at the front, its index tab taller than the folders
    gy = rows[-1] + 2
    d.rectangle([x - 1, gy, x + 39, gy + 1], fill=hx("6a8478"))
    d.line([(x - 1, gy), (x + 39, gy)], fill=hx("8aa496"))
    d.rectangle([x + 28, gy - 3, x + 35, gy], fill=hx("7a9488"), outline=hx("3a4a40"))
    d.point((x + 31, gy - 2), fill=hx("e8e0c8"))
    d.point((x + 32, gy - 2), fill=hx("e8e0c8"))


def _drawer(d, img, x, y, letter, opened):
    if opened:
        # pulled out on its runners: the empty slot in the cabinet, steel side walls, the folders seen from above,
        # and the front hanging lower and nearer
        d.rectangle([x + 1, y, x + 37, y + 22], fill=hx("0e0e0a"), outline=hx("1a1a14"))
        d.line([(x + 2, y + 1), (x + 36, y + 1)], fill=hx("26261e"))
        d.polygon([(x + 1, y - 1), (x + 37, y - 1), (x + 40, y + 13), (x - 2, y + 13)], fill=hx("2a2a22"))
        for side, sx0, sx1 in ((-1, x + 1, x - 2), (1, x + 37, x + 40)):
            d.line([(sx0, y - 1), (sx1, y + 13)], fill=hx("8a8a76") if side < 0 else hx("4a4a3e"))
            d.line([(sx0 - side, y - 1), (sx1 - side, y + 13)], fill=hx("6a6a5a"))
        d.line([(x + 1, y - 1), (x + 37, y - 1)], fill=hx("5a5a4c"))
        _folders(d, x, y)
        fy = y + 14
        d.rectangle([x - 2, fy, x + 40, fy + 22], fill=hx("6a6a5a"), outline=hx("1a1a14"))
        d.line([(x - 1, fy + 1), (x + 39, fy + 1)], fill=hx("9a9a86"))
        d.line([(x - 1, fy + 2), (x - 1, fy + 21)], fill=hx("80806e"))
        d.line([(x + 39, fy + 2), (x + 39, fy + 21)], fill=hx("4a4a3e"))
        d.line([(x - 1, fy + 21), (x + 39, fy + 21)], fill=hx("4a4a3e"))
        # brass card holder with the letter, and the pull with its lit upper lip
        d.rectangle([x + 14, fy + 3, x + 24, fy + 10], fill=hx("a08a40"), outline=hx("3a2a0c"))
        d.rectangle([x + 15, fy + 4, x + 23, fy + 9], fill=hx("ece4cc"))
        text(img, (x + 19, fy + 7), letter, hx("1a1a14"), size=8)
        d.rectangle([x + 12, fy + 14, x + 26, fy + 17], fill=hx("4a4a3e"), outline=hx("1a1a14"))
        d.line([(x + 13, fy + 14), (x + 25, fy + 14)], fill=hx("c8c4b0"))
        d.line([(x + 13, fy + 15), (x + 25, fy + 15)], fill=hx("8a8676"))
        return
    d.rectangle([x + 1, y, x + 37, y + 22], fill=hx("5a5a4c"), outline=hx("22221a"))
    d.line([(x + 2, y + 1), (x + 36, y + 1)], fill=hx("7a7a68"))
    d.rectangle([x + 15, y + 4, x + 23, y + 10], fill=hx("e0d8c0"), outline=hx("2a2a20"))
    text(img, (x + 19, y + 7), letter, hx("1a1a14"), size=8)
    d.rectangle([x + 13, y + 14, x + 25, y + 16], fill=hx("a8a490"))


def _loop_map(d, img, pin):
    x0, y0, x1, y1 = MAP_BOX
    w, h = x1 - x0 + 1, y1 - y0 + 1
    # the frame: dark oak, mitred at the corners, a lit inner bevel along the top and left, a gilt slip
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], fill=hx("3a2614"), outline=hx("140a04"))
    d.line([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4)], fill=hx("6a4a2a"))
    d.line([(x0 - 4, y0 - 4), (x0 - 4, y1 + 4)], fill=hx("5a3c22"))
    d.line([(x0 - 4, y1 + 4), (x1 + 4, y1 + 4)], fill=hx("1e1208"))
    d.line([(x1 + 4, y0 - 4), (x1 + 4, y1 + 4)], fill=hx("24160a"))
    for (ax, ay), (bx, by) in (((x0 - 4, y0 - 4), (x0 - 1, y0 - 1)), ((x1 + 4, y0 - 4), (x1 + 1, y0 - 1)),
                               ((x0 - 4, y1 + 4), (x0 - 1, y1 + 1)), ((x1 + 4, y1 + 4), (x1 + 1, y1 + 1))):
        d.line([(ax, ay), (bx, by)], fill=hx("1a0e06"))
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=hx("8a7438"))
    d.line([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1)], fill=hx("c8a858"))
    # the sheet: aged paper, browner towards the frame, the lake washed blue-grey, the street map printed on it
    rng = np.random.default_rng(1327)
    ys, xs = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xs, w - 1 - xs, ys, h - 1 - ys]).astype(np.float32)
    age = np.clip(1 - edge / 9.0, 0, 1) ** 2 + rng.normal(0, 0.05, (h, w))
    t = np.clip(age * 0.7, 0, 1)[..., None]
    col = np.array(hx("d8cca4"), np.float32) * (1 - t) + np.array(hx("a8925e"), np.float32) * t
    lake = Image.new("L", (w, h), 0)
    sx0, sy0, sx1, sy1 = LOOP_SRC
    shore = [(np.subtract(_on_loop_map(p), (x0, y0))) for p in chicago_map.SHORE if sy0 - 100 <= p[1] <= sy1 + 100]
    ImageDraw.Draw(lake).polygon([tuple(p) for p in shore] + [(w, h), (w, 0)], fill=255)
    lake = np.asarray(lake.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255.0
    col = col * (1 - lake * 0.6) + np.array(hx("7e98a8"), np.float32) * lake * 0.6
    col += rng.normal(0, 2.0, (h, w, 1))
    ink = chicago_map.ink_in(LOOP_SRC, (w, h))[..., None] * (0.82 - t * 0.2) * (1 - lake * 0.45)
    col = col * (1 - ink) + np.array(hx("2a2016"), np.float32) * ink
    img.paste(Image.fromarray(col.clip(0, 255).astype(np.uint8)), (x0, y0))
    # stories the desk has followed: a scatter of coloured map tacks
    rnd = random.Random(1327)
    for _ in range(14):
        while True:
            px, py = rnd.randint(x0 + 6, x1 - 18), rnd.randint(y0 + 8, y1 - 6)
            if abs(px - LASALLE[0]) > 8 or abs(py - LASALLE[1]) > 8:
                break
        c = hx(rnd.choice(("b82a2c", "2c4c9c", "2e7a44", "26262a")))
        d.point((px + 1, py + 1), fill=hx("4a3a24"))
        d.rectangle([px - 1, py - 1, px, py], fill=c)
        d.point((px - 1, py - 1), fill=mix(c, hx("ffffff"), 0.55))
    if pin:
        # the mended clipping pinned up beside a fat red pin on LaSalle
        cx, cy = LASALLE
        d.rectangle([cx + 3, cy - 2, cx + 18, cy + 9], fill=hx("4a3a24"))
        d.rectangle([cx + 2, cy - 3, cx + 17, cy + 8], fill=hx("ece4cc"), outline=hx("6a6050"))
        d.rectangle([cx + 4, cy - 1, cx + 8, cy + 3], fill=hx("6a6458"))
        d.line([(cx + 10, cy - 1), (cx + 15, cy - 1)], fill=hx("2a2a2a"))
        d.line([(cx + 10, cy + 1), (cx + 15, cy + 1)], fill=hx("6a6252"))
        d.line([(cx + 2, cy + 4), (cx + 17, cy + 4)], fill=hx("c8b878"))
        for ly in (cy + 6, cy + 7):
            d.line([(cx + 4, ly), (cx + 15, ly)], fill=hx("8a8270"))
        d.line([(cx + 1, cy + 1), (cx + 5, cy + 2)], fill=hx("4a3a24"))
        d.line([(cx, cy), (cx + 4, cy)], fill=hx("b4b8bc"))
        d.ellipse([cx - 4, cy - 4, cx + 1, cy + 1], fill=hx("d02020"), outline=hx("6a0a0a"))
        d.point((cx - 3, cy - 3), fill=hx("ff8a7a"))
        d.point((cx - 2, cy - 3), fill=hx("f4c0b0"))
    # the glass: a long glint across the top corner and a duller one low down
    light(img, "polygon", [(x0 + 66, y0), (x0 + 76, y0), (x0 + 40, y1), (x0 + 34, y1)], hx("f0f0e0"), 0.13, 1)
    light(img, "polygon", [(x0 + 82, y0), (x0 + 85, y0), (x0 + 50, y1), (x0 + 48, y1)], hx("f0f0e0"), 0.08, 0)
    _plaque(d, img)


PLAQUE = (248, 128, 300, 138)


def _plaque(d, img):
    """A cast brass plate screwed to the wall: bevelled edge, an engraved border, the name cut in and lit below."""
    x0, y0, x1, y1 = PLAQUE
    d.rectangle([x0 + 1, y0 + 1, x1 + 1, y1 + 1], fill=hx("1a1408"))
    d.rectangle([x0, y0, x1, y1], fill=hx("a88c3e"), outline=hx("3a2a0c"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("ecd488"))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=hx("d8bc6a"))
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=hx("6a5420"))
    d.line([(x1 - 1, y0 + 1), (x1 - 1, y1 - 1)], fill=hx("6a5420"))
    # tarnish gathered in the corners, a polished streak where the cleaner's rag goes
    for px_, py_ in ((x0 + 2, y1 - 2), (x1 - 2, y1 - 2), (x1 - 3, y1 - 2), (x0 + 2, y0 + 2)):
        d.point((px_, py_), fill=hx("6a6a3a"))
    d.line([(x0 + 14, y0 + 2), (x0 + 30, y0 + 2)], fill=hx("c8ac5c"))
    # engraved border, with a slot-headed screw in each end
    d.rectangle([x0 + 5, y0 + 2, x1 - 5, y1 - 2], outline=hx("6a5420"))
    d.line([(x0 + 6, y1 - 1), (x1 - 5, y1 - 1)], fill=hx("c8ac5c"))
    for sx in (x0 + 2, x1 - 3):
        sy = (y0 + y1) // 2 - 1
        d.rectangle([sx, sy, sx + 1, sy + 1], fill=hx("8a7a50"))
        d.point((sx, sy), fill=hx("e8dca8"))
        d.point((sx + 1, sy + 1), fill=hx("3a2a0c"))
    cx, cy = (x0 + x1) // 2 + 1, (y0 + y1) // 2 + 1
    text(img, (cx, cy + 1), "THE LOOP", hx("e4cc80"), size=8)
    text(img, (cx, cy), "THE LOOP", hx("2a1e08"), size=8)


SPIKE_X = 314
DESK_Y = 156  # top of the layout desk: about belt height on Micah standing in front of it


def _sheet(d, x0, y, col, rnd, pencil=False):
    """A sheet of dead copy rammed down on the spike, seen a little from above: a skewed slab of paper with a lit
    near edge, a curled corner, typed lines across it, sometimes a blue-pencil slash, and the hole the spike made."""
    c = hx(col)
    tilt = rnd.choice((-1, 0, 1))
    pts = [(x0, y + 1 + tilt), (x0 + 24, y - tilt), (x0 + 25, y + 4 - tilt), (x0 + 1, y + 5 + tilt)]
    d.polygon(pts, fill=c, outline=mul(c, 0.55))
    d.line([(x0 + 1, y + 5 + tilt), (x0 + 25, y + 4 - tilt)], fill=mul(c, 1.12))
    d.line([(x0 + 1, y + 6 + tilt), (x0 + 25, y + 5 - tilt)], fill=mul(c, 0.45))
    for k in (2, 3):
        for a, b in ((3, 9), (12, 21)):
            if rnd.random() < 0.85:
                d.line([(x0 + a, y + k + tilt), (x0 + b, y + k)], fill=mul(c, 0.66))
    if pencil:
        d.line([(x0 + 4, y + 4 + tilt), (x0 + 10, y + 1 + tilt)], fill=hx("3a5a9a"))
    corner = rnd.choice((x0, x0 + 23))
    d.point((corner + 1, y + tilt - (0 if corner == x0 else -1)), fill=mul(c, 1.2))
    d.point((corner + 1, y + 1 + tilt), fill=mul(c, 0.7))
    d.point((SPIKE_X, y + 2), fill=hx("1a1a18"))


def _crumple(d, rnd, cx, cy, r, col):
    """A ball of crumpled copy: a lumpy outline, facets lit from the lamp above-left, creases and typed flecks."""
    c = hx(col)
    pts = []
    for k in range(10):
        a = k * 6.2832 / 10 + rnd.uniform(-0.2, 0.2)
        rr = r * rnd.uniform(0.78, 1.08)
        pts.append((cx + rr * math.cos(a), cy + rr * 0.86 * math.sin(a)))
    d.polygon(pts, fill=mul(c, 0.82), outline=mul(c, 0.4))
    # the lit upper-left facets and the shadowed underside
    d.polygon([pts[5], pts[6], pts[7], (cx, cy)], fill=mul(c, 1.12))
    d.polygon([pts[4], pts[5], (cx, cy)], fill=c)
    d.polygon([pts[7], pts[8], (cx + 1, cy)], fill=mul(c, 0.95))
    d.polygon([pts[1], pts[2], pts[3], (cx, cy + 1)], fill=mul(c, 0.62))
    # creases run in from the edge to the knot of the fold
    for k in (0, 3, 6, 8):
        px_, py_ = pts[k]
        d.line([(round(px_), round(py_)), (round((px_ + cx) / 2), round((py_ + cy) / 2))], fill=mul(c, 0.55))
    for _ in range(2):
        tx, ty = cx + rnd.randint(-r + 2, r - 3), cy + rnd.randint(-r // 2, r // 2)
        d.line([(tx, ty), (tx + 2, ty)], fill=mul(c, 0.5))
    d.point((round(pts[6][0]) + 1, round(pts[6][1]) + 1), fill=mul(c, 1.25))


def _wastebasket(d, img):
    """A woven wire basket under the stand, near full: crumpled copy heaped above the rim and showing through the
    mesh, a torn sheet hanging over the front, and a ball that missed lying on the linoleum."""
    rnd = random.Random(1341)
    top, bot, lx0, lx1, bx0, bx1 = 166, FLOOR + 6, 302, 330, 306, 326
    shadow(img, "ellipse", [300, bot - 3, 336, bot + 4], 0.55, 2)
    d = ImageDraw.Draw(img)
    d.ellipse([lx0, top - 3, lx1, top + 3], fill=hx("161612"))
    # paper heaped in the mouth, the back ones darker under the stand's shadow
    for cx, cy, r, col in ((309, 162, 5, "a8a08a"), (322, 161, 5, "b0a890"), (315, 160, 6, "d4ccb4"),
                           (326, 164, 4, "c8c0a4"), (306, 165, 4, "d8d0b8")):
        _crumple(d, rnd, cx, cy, r, col)
    # the body: dark inside, paper crowding the mesh, then the wires woven across it
    body = [(lx0, top), (lx1, top), (bx1, bot), (bx0, bot)]
    inner = Image.new("RGB", img.size, hx("24241e"))
    di = ImageDraw.Draw(inner)
    for _ in range(9):
        px_, py_ = rnd.randint(lx0, lx1), rnd.randint(top + 2, bot - 8)
        di.ellipse([px_ - 4, py_ - 3, px_ + 4, py_ + 3], fill=hx(rnd.choice(("6a6656", "7e7866", "5a564a"))))
    for k in range(-40, 40, 4):
        di.line([(lx0 + k, top), (lx0 + k + 34, bot)], fill=hx("6e6e62"))
        di.line([(lx1 - k, top), (lx1 - k - 34, bot)], fill=hx("4e4e46"))
    for y in range(top + 6, bot, 7):
        di.line([(0, y), (W, y)], fill=hx("5a5a50"))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(body, fill=255)
    img.paste(inner, (0, 0), m)
    shadow(img, "polygon", [(lx1 - 9, top), (lx1, top), (bx1, bot), (bx1 - 7, bot)], 0.35, 1)
    light(img, "polygon", [(lx0, top), (lx0 + 6, top), (bx0 + 5, bot), (bx0, bot)], hx("e0c890"), 0.12, 1)
    d = ImageDraw.Draw(img)
    d.line(body + [body[0]], fill=hx("1a1a14"))
    # a rolled rim round the mouth and a band round the foot
    d.arc([lx0, top - 3, lx1, top + 3], 0, 180, fill=hx("8a8a7e"), width=2)
    d.arc([lx0, top - 3, lx1, top + 3], 200, 340, fill=hx("4a4a42"))
    d.line([(lx0 + 2, top + 2), (lx0 + 8, top + 3)], fill=hx("c8c8b8"))
    d.rectangle([bx0, bot - 3, bx1, bot - 1], fill=hx("44443c"), outline=hx("1a1a14"))
    d.line([(bx0 + 1, bot - 3), (bx1 - 1, bot - 3)], fill=hx("6e6e62"))
    # a torn sheet caught on the rim, hanging down the front
    d.polygon([(312, top), (320, top + 1), (319, top + 9), (316, top + 8), (313, top + 10)], fill=hx("ccc4aa"),
              outline=hx("6a6050"))
    d.line([(314, top + 3), (318, top + 3)], fill=hx("7a7462"))
    d.line([(314, top + 5), (317, top + 5)], fill=hx("7a7462"))
    d.line([(312, top + 1), (320, top + 1)], fill=hx("e8e0c8"))
    # the one that missed
    _crumple(d, rnd, 343, FLOOR + 5, 4, "cec6ac")


def _spike_stand(d, img, taken):
    sx = SPIKE_X
    # a small oak stand, lit along its front edge, the wastebasket underneath
    d.rectangle([292, 150, 340, 156], fill=hx("5a3c24"), outline=hx("1e1208"))
    d.line([(293, 151), (339, 151)], fill=hx("7a5634"))
    d.line([(293, 155), (339, 155)], fill=hx("3a2614"))
    for lx in (296, 332):
        d.rectangle([lx, 156, lx + 4, FLOOR + 4], fill=hx("3a2614"), outline=hx("1e1208"))
        d.line([(lx + 1, 157), (lx + 1, FLOOR + 3)], fill=hx("5a3c24"))
    _wastebasket(d, img)
    d = ImageDraw.Draw(img)
    # the spike: a domed cast-iron foot on a felt pad, a turned steel collar, and a long needle lit on the lamp side
    d.ellipse([305, 148, 327, 153], fill=hx("2a4a2a"))
    d.ellipse([306, 144, 326, 152], fill=hx("161614"), outline=hx("060604"))
    d.ellipse([308, 143, 324, 149], fill=hx("34342e"))
    d.ellipse([311, 142, 321, 146], fill=hx("484842"))
    d.arc([308, 143, 324, 149], 185, 280, fill=hx("9a9a90"))
    d.arc([311, 142, 321, 146], 190, 260, fill=hx("c0c0b6"))
    d.point((310, 149), fill=hx("6a6a64"))
    d.rectangle([sx - 2, 138, sx + 2, 142], fill=hx("6a6a64"), outline=hx("1a1a18"))
    d.line([(sx - 1, 139), (sx - 1, 141)], fill=hx("c4c4bc"))
    d.line([(sx - 3, 142), (sx + 3, 142)], fill=hx("2a2a28"))
    d.line([(sx, 138), (sx, 108)], fill=hx("dcdcd4"))
    d.line([(sx + 1, 138), (sx + 1, 110)], fill=hx("4e4e48"))
    d.point((sx, 107), fill=hx("a8a8a0"))
    d.point((sx, 106), fill=hx("fafaf2"))
    # a day's dead copy rammed down to the foot: galleys, carbons, a yellow flimsy, blue-pencilled leads
    rnd = random.Random(1323)
    stack = ((136, "bab29a", False), (134, "d2caae", True), (132, "c6ccd0", False), (130, "e0d49c", False),
             (128, "cec6aa", True), (126, "d8d0b8", False))
    for y, c, pencil in stack:
        _sheet(d, sx - 12 + rnd.randint(-2, 1), y, c, rnd, pencil)
    if taken:
        return
    # the torn bottom half of the Harrington clipping on top: ragged edge up, the photo, the caption, the address
    x0, y = sx - 11, 121
    d.polygon([(x0, y), (x0 + 22, y - 2), (x0 + 23, y + 5), (x0 + 1, y + 7)], fill=hx("ece4cc"), outline=hx("8a8270"))
    for i, tx in enumerate(range(x0 + 1, x0 + 22, 2)):
        d.point((tx, round(y - 2 * (tx - x0) / 22) - 1 - (i % 2)), fill=hx("ece4cc"))
    d.line([(x0 + 1, y + 7), (x0 + 23, y + 5)], fill=hx("4a4436"))
    d.rectangle([x0 + 3, y + 1, x0 + 8, y + 4], fill=hx("6a6458"))
    d.line([(x0 + 4, y + 2), (x0 + 7, y + 2)], fill=hx("9a9282"))
    d.line([(x0 + 10, y + 1), (x0 + 20, y)], fill=hx("2a2a2a"))
    d.line([(x0 + 10, y + 3), (x0 + 19, y + 2)], fill=hx("6a6252"))
    d.line([(x0 + 3, y + 6), (x0 + 19, y + 4)], fill=hx("8a8270"))
    d.point((sx, y + 2), fill=hx("1a1a18"))


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
    # shears and a trimmed column beside the paste, always on the desk
    d.polygon([(455, y - 4), (464, y - 5), (464, y - 2), (456, y - 1)], fill=hx("dcd4bc"), outline=hx("8a8270"))
    for k in (457, 460):
        d.line([(k, y - 3), (k + 2, y - 3)], fill=hx("6a6252"))
    d.line([(457, y - 6), (464, y - 9)], fill=hx("b8b8b0"))
    d.line([(457, y - 5), (464, y - 7)], fill=hx("7a7a72"))
    d.ellipse([453, y - 8, 456, y - 5], outline=hx("2a2a24"))
    d.ellipse([453, y - 5, 456, y - 2], outline=hx("2a2a24"))
    _paste_pot(d, y, paste)


def _paste_pot(d, y, taken):
    """The paste pot at the end of the desk: a stoneware crock with its label, paste slopped over the rim, the brush."""
    if taken:
        # a damp ring where it stood, a skin of dried paste and a couple of drips
        d.ellipse([429, y - 3, 445, y + 1], fill=hx("5a3e22"))
        d.ellipse([431, y - 2, 443, y], fill=hx("6e5032"))
        d.arc([429, y - 3, 445, y + 1], 200, 340, fill=hx("c8bea0"))
        for px_, py_ in ((426, y - 2), (448, y - 1), (447, y - 3)):
            d.point((px_, py_), fill=hx("d8d0b4"))
        return
    x0, x1 = 430, 444
    top = y - 15
    d.ellipse([x0 - 2, y - 3, x1 + 2, y + 1], fill=hx("3a2614"))
    # glazed body, rounded shoulders, a light edge on the lamp side
    d.rectangle([x0, top + 2, x1, y - 1], fill=hx("d8d0b8"), outline=hx("4a4a40"))
    d.ellipse([x0, y - 3, x1, y], fill=hx("b8b098"), outline=hx("4a4a40"))
    d.line([(x0 + 1, top + 3), (x0 + 1, y - 2)], fill=hx("f4f0e0"))
    d.line([(x0 + 2, top + 3), (x0 + 2, y - 3)], fill=hx("e8e2cc"))
    d.line([(x1 - 1, top + 3), (x1 - 1, y - 2)], fill=hx("9a9280"))
    d.line([(x1 - 2, top + 4), (x1 - 2, y - 3)], fill=hx("b0a890"))
    # the paper label: a red band round the crock, a cream panel with a line of black lettering
    d.rectangle([x0 + 1, top + 6, x1 - 1, top + 11], fill=hx("8a2a24"))
    d.line([(x0 + 1, top + 6), (x1 - 1, top + 6)], fill=hx("b04a3a"))
    d.rectangle([x0 + 4, top + 7, x1 - 4, top + 10], fill=hx("e8dcb8"))
    d.line([(x0 + 5, top + 8), (x1 - 5, top + 8)], fill=hx("2a1a14"))
    d.line([(x0 + 1, top + 12), (x1 - 1, top + 12)], fill=hx("4a1a14"))
    # rim, the paste heaped inside with a wet sheen, slopped over and running down the side
    d.ellipse([x0 - 1, top - 1, x1 + 1, top + 4], fill=hx("e4dcc4"), outline=hx("4a4a40"))
    d.ellipse([x0 + 1, top, x1 - 1, top + 3], fill=hx("f4eedc"))
    d.ellipse([x0 + 3, top - 1, x0 + 9, top + 2], fill=hx("fffaf0"))
    d.point((x0 + 4, top), fill=hx("ffffff"))
    for dx, ln in ((2, 6), (12, 3)):
        d.line([(x0 + dx, top + 3), (x0 + dx, top + 3 + ln)], fill=hx("f8f2e0"))
        d.point((x0 + dx, top + 4 + ln), fill=hx("fffaf0"))
    # the brush stood in it: bristles in the paste, a tin ferrule, a long varnished handle tipped to the wall
    d.line([(437, top + 1), (438, top - 2)], fill=hx("c8b890"), width=2)
    d.rectangle([437, top - 6, 440, top - 2], fill=hx("a8a8a0"), outline=hx("4a4a44"))
    d.point((438, top - 5), fill=hx("e8e8e0"))
    d.line([(439, top - 6), (446, top - 16)], fill=hx("8a5a2a"), width=2)
    d.line([(438, top - 7), (445, top - 16)], fill=hx("c08a4a"))
    d.point((446, top - 17), fill=hx("3a2614"))
    # the crock's lid set down beside it, upside down, a glob of paste on it
    d.ellipse([445, y - 3, 452, y], fill=hx("c8c0a8"), outline=hx("4a4a40"))
    d.point((448, y - 2), fill=hx("f4eedc"))


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


def _carton(d, rnd, x0, y0, x1, y1, col, label=True, handle=True, string=False):
    """A cardboard archive carton: overhanging lid, lit top edge, finger hole, an inked label, scuffed corners."""
    c = hx(col)
    d.rectangle([x0, y0 + 4, x1, y1], fill=c, outline=hx("2a1e0e"))
    d.line([(x0 + 1, y0 + 5), (x0 + 1, y1 - 1)], fill=mul(c, 1.18))
    d.line([(x1 - 1, y0 + 5), (x1 - 1, y1 - 1)], fill=mul(c, 0.72))
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=mul(c, 0.78))
    # corrugated seams down the front, faint
    for sx in range(x0 + 5, x1 - 2, 6):
        d.line([(sx, y0 + 7), (sx, y1 - 2)], fill=mul(c, 0.9))
    # the lid: a lip all round, lighter on top where the lamp catches it
    d.rectangle([x0 - 1, y0, x1 + 1, y0 + 4], fill=mul(c, 1.1), outline=hx("2a1e0e"))
    d.line([(x0, y0 + 1), (x1, y0 + 1)], fill=mul(c, 1.38))
    d.line([(x0, y0 + 5), (x1, y0 + 5)], fill=mul(c, 0.55))
    for cx_, cy_ in ((x0, y0 + 1), (x1, y0 + 1), (x0, y1 - 1), (x1, y1 - 1)):
        d.point((cx_, cy_), fill=mul(c, 1.5))
    # a torn corner showing the fluting, and scuffs
    d.polygon([(x1 - 4, y1), (x1, y1), (x1, y1 - 4)], fill=mul(c, 0.6))
    d.line([(x1 - 3, y1), (x1, y1 - 3)], fill=mul(c, 1.3))
    for _ in range((x1 - x0) // 4):
        d.point((rnd.randint(x0 + 2, x1 - 2), rnd.randint(y0 + 6, y1 - 2)), fill=mul(c, rnd.choice((0.82, 1.15))))
    if handle:
        hx0 = (x0 + x1) // 2 + 4
        d.rounded_rectangle([hx0 - 3, y0 + 7, hx0 + 3, y0 + 9], 1, fill=hx("140e06"))
        d.line([(hx0 - 2, y0 + 10), (hx0 + 2, y0 + 10)], fill=mul(c, 1.25))
    if label:
        lx, ly = x0 + 3, y0 + 7
        d.rectangle([lx, ly, lx + 9, ly + 7], fill=hx("e4dcc0"), outline=hx("6a6050"))
        d.line([(lx + 2, ly + 2), (lx + 7, ly + 2)], fill=hx("1a1a2a"))
        d.line([(lx + 2, ly + 4), (lx + 6, ly + 4)], fill=hx("4a4a5a"))
        d.point((lx + 7, ly + 5), fill=hx("8a1a1a"))
    if string:
        sx = (x0 + x1) // 2 - 3
        d.line([(sx, y0), (sx, y1)], fill=hx("d8c89a"))
        d.line([(x0, (y0 + y1) // 2 + 3), (x1, (y0 + y1) // 2 + 3)], fill=hx("d8c89a"))
        d.ellipse([sx - 2, y0 - 2, sx + 2, y0 + 1], outline=hx("c8b880"))
        d.line([(sx + 1, y0 + 1), (sx + 3, y0 + 4)], fill=hx("c8b880"))


def _bundle(d, x0, y0, x1, layers, rnd):
    """Bound back numbers stacked flat: folded spines, ragged page edges, twine round the lot."""
    y = y0
    for i in range(layers):
        h = 3 + (i % 2)
        dx = rnd.randint(-1, 1)
        d.rectangle([x0 + dx, y, x1 + dx, y + h], fill=hx(("d8ccaa", "c8bc98", "e0d6b8")[i % 3]),
                    outline=hx("6a6050"))
        d.line([(x0 + dx + 1, y + 1), (x1 + dx - 1, y + 1)], fill=hx("f0e8d0"))
        for px_ in range(x0 + dx + 2, x1 + dx - 1, 3):
            d.point((px_, y + h - 1), fill=hx("9a8e70"))
        d.line([(x0 + dx, y), (x0 + dx, y + h)], fill=hx("8a7a58"))
        y += h + 1
    tx = (x0 + x1) // 2 + 2
    d.line([(tx, y0 - 1), (tx, y - 1)], fill=hx("b89a5a"))
    d.line([(tx + 1, y0 - 1), (tx + 1, y - 1)], fill=hx("6a5430"))
    d.line([(tx - 2, y0 - 2), (tx + 4, y0 - 2)], fill=hx("b89a5a"))


def _archive_stacks(d, img):
    rnd = random.Random(1311)
    # left cabinet: two cartons of back numbers, the top one tied and set a little askew
    _carton(d, rnd, 94, 74, 128, 92, "8a7048", string=False)
    _carton(d, rnd, 99, 60, 124, 74, "a08a5c", label=True, handle=False, string=True)
    # middle cabinet: a pile of bound editions under a dusty ledger
    _bundle(d, 136, 80, 166, 3, rnd)
    d.rectangle([139, 75, 163, 79], fill=hx("3a2a4a"), outline=hx("140a1a"))
    d.line([(140, 76), (162, 76)], fill=hx("5a4a6a"))
    d.rectangle([139, 75, 142, 79], fill=hx("6a2a1a"))
    d.line([(144, 78), (162, 78)], fill=hx("d8ccaa"))
    # right cabinet: an open carton, its flaps up, folders and loose clippings standing in it
    x0, y0, x1, y1 = 176, 74, 208, 92
    for fx, col in ((179, "e0d4b0"), (184, "c8a878"), (189, "d8ccaa"), (194, "b8a070"), (199, "e8dcc0")):
        top = y0 - 4 + rnd.randint(0, 4)
        d.rectangle([fx, top, fx + 5, y0 + 6], fill=hx(col), outline=hx("6a6050"))
        d.line([(fx + 1, top + 1), (fx + 3, top + 1)], fill=hx("2a2a2a") if fx % 2 else hx("8a1a1a"))
    _carton(d, rnd, x0, y0 + 4, x1, y1, "9a7e50", label=False, handle=True)
    d.polygon([(x0 - 1, y0 + 4), (x0 - 6, y0 - 4), (x0 - 4, y0 - 5), (x0 + 3, y0 + 4)], fill=hx("8a7048"),
              outline=hx("2a1e0e"))
    d.polygon([(x1 + 1, y0 + 4), (x1 + 5, y0 - 3), (x1 + 3, y0 - 4), (x1 - 3, y0 + 4)], fill=hx("b0965e"),
              outline=hx("2a1e0e"))
    d.rectangle([x0 + 4, y0 + 10, x0 + 13, y0 + 15], fill=hx("e4dcc0"), outline=hx("6a6050"))
    d.line([(x0 + 6, y0 + 12), (x0 + 11, y0 + 12)], fill=hx("1a1a2a"))
    # dust along the cabinet tops
    for x in range(90, 214, 3):
        d.point((x, 92), fill=hx("6a6a58") if x % 2 else hx("56564a"))


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
    # archive boxes and bound editions stacked on the cabinets
    _archive_stacks(d, img)
    _loop_map(d, img, pin)
    _spike_stand(d, img, spike)
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
    # the printed map would soak up most of a shared palette; give it its own share so the room keeps its colours
    rest = blend.copy()
    rest.paste(blend.getpixel((MAP_BOX[0] - 12, MAP_BOX[1] + 20)), MAP_BOX)
    pal = palette_of(rest, 108) + palette_of(blend.crop(MAP_BOX), 28)
    pal += [hx(c) for c in ("b82a2c", "2c4c9c", "2e7a44", "d02020", "ff8a7a", "6a0a0a",
                                     "a88c3e", "ecd488", "d8bc6a", "6a5420", "c8ac5c", "3a2a0c")]
    px = pixelize(base, pal)
    save(px, "rooms", "newspaper_morgue.png")
    overlay(v["drawer"], px, pal, (122, 136, 182, 184), "newspaper_morgue_drawer")
    overlay(v["spike"], px, pal, (298, 112, 334, 136), "newspaper_morgue_spike")
    overlay(v["paste"], px, pal, (424, 124, 452, 160), "newspaper_morgue_paste")
    lx, ly = LASALLE
    overlay(v["pin"], px, pal, (lx - 6, ly - 6, lx + 21, ly + 12), "newspaper_morgue_pin")
    return px


# ------------------------------------------------------------------------------------------------ THE VESTIBULE

# hung out of procession order, so the plaque and the invitation have to tell Micah which one leads
CLOAKS = (("lion", 228, "d8b048"), ("stag", 258, "8a6a3a"), ("raven", 288, "c8ccd4"))
INNER = (368, 46, 452, FLOOR + 2)


GOLD, GOLD_D, GOLD_L, GOLD_DK = hx("c8a050"), hx("7a5a24"), hx("f0d088"), hx("4a3412")


def _emblem(d, kind, cx, cy, col):
    """An embroidered roundel: a gold-thread ring around the house beast, worked in its own metal."""
    c, c_d = hx(col), mul(hx(col), 0.6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=hx("120e14"), outline=GOLD_D)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=c_d)
    for a in range(0, 360, 45):
        v = _dir(a)
        d.point((cx + round(v[0] * 7), cy + round(v[1] * 7)), fill=GOLD)
    if kind == "raven":
        d.polygon([(cx - 4, cy + 2), (cx - 1, cy - 2), (cx + 2, cy - 3), (cx + 4, cy - 2), (cx + 2, cy),
                   (cx + 1, cy + 3), (cx - 2, cy + 3)], fill=c)
        d.line([(cx + 4, cy - 2), (cx + 5, cy - 1)], fill=GOLD)
        d.line([(cx - 3, cy + 1), (cx + 1, cy - 1)], fill=c_d)
        d.line([(cx - 4, cy + 3), (cx - 5, cy + 4)], fill=c)
        d.point((cx + 2, cy - 2), fill=hx("120e14"))
    elif kind == "lion":
        for a in range(0, 360, 30):
            v = _dir(a)
            d.line([(cx, cy), (cx + round(v[0] * 4), cy + round(v[1] * 4))], fill=c_d)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=c_d)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)
        d.point((cx - 1, cy - 1), fill=hx("120e14"))
        d.point((cx + 1, cy - 1), fill=hx("120e14"))
        d.point((cx, cy + 1), fill=c_d)
    else:
        d.polygon([(cx - 2, cy - 1), (cx + 2, cy - 1), (cx + 1, cy + 3), (cx - 1, cy + 3)], fill=c)
        for s in (-1, 1):
            d.line([(cx + s, cy - 1), (cx + 3 * s, cy - 4), (cx + 4 * s, cy - 6)], fill=c)
            d.line([(cx + 3 * s, cy - 4), (cx + 5 * s, cy - 4)], fill=c)
            d.line([(cx + 2 * s, cy - 2), (cx + 3 * s, cy - 2)], fill=c_d)
        d.point((cx, cy + 3), fill=c_d)


def _dir(deg):
    import math
    return math.cos(math.radians(deg)), math.sin(math.radians(deg))


def _hung_cloak(d, x, hem, w, c, rnd, lining=None, fur=False):
    """A member's coat on a wooden hanger in the cloakroom, numbered brass tag on the hook."""
    d.line([(x, 84), (x, 87)], fill=hx("8a7a50"))
    d.rectangle([x + 1, 86, x + 3, 88], fill=GOLD)
    d.line([(x - 6, 90), (x, 87), (x + 6, 90)], fill=hx("6a4a28"))
    body = [(x - 6, 90), (x + 6, 90), (x + 8, 96), (x + w, hem), (x + w // 2, hem + 1), (x, hem - 1),
            (x - w // 2, hem + 1), (x - w, hem), (x - 8, 96)]
    d.polygon(body, fill=c)
    for k in range(-2, 3):
        fx = x + k * w * 2 // 5
        d.line([(x + k * 2, 94), (fx, hem - 1)], fill=mul(c, 0.55))
        d.line([(x + k * 2 + 1, 95), (fx + 1, hem - 2)], fill=mul(c, 1.35))
    d.line([(x - 8, 96), (x - w, hem)], fill=mul(c, 1.6))
    if lining:
        d.polygon([(x, 92), (x + 1, 92), (x + 3, hem - 1), (x - 1, hem - 1)], fill=hx(lining))
    if fur:
        for i in range(10):
            d.point((x - 6 + i + rnd.randint(0, 1), 89 + rnd.randint(0, 3)), fill=hx(rnd.choice(("8a7a68", "6a5a4a", "a89880"))))
    else:
        d.polygon([(x - 6, 90), (x + 6, 90), (x + 3, 95), (x - 3, 95)], fill=mul(c, 0.7))
    for by in range(100, hem - 6, 8):
        d.point((x + 2, by), fill=hx("2a2a2a") if not lining else GOLD_D)


def _hatch(d, img, gold, gold_d):
    """The cloakroom hatch: a gilt frame, a rolled shutter, hats on the shelf and the members' coats behind."""
    d.rectangle([84, 62, 200, 142], fill=gold_d)
    d.line([(84, 62), (200, 62)], fill=GOLD_L)
    d.line([(84, 62), (84, 142)], fill=gold)
    d.line([(200, 62), (200, 142)], fill=GOLD_DK)
    for x in range(86, 200, 4):
        d.point((x, 63), fill=gold)
        d.point((x + 2, 64), fill=GOLD_DK)
    d.rectangle([87, 65, 197, 142], outline=GOLD_DK)
    d.line([(88, 66), (88, 141)], fill=gold)
    for cx, cy in ((85, 63), (199, 63)):
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=gold, outline=GOLD_DK)
        d.point((cx, cy), fill=GOLD_L)
    vgrad(img, (90, 66, 194, 141), hx("221016"), hx("0a0406"))
    for x in range(96, 194, 9):
        d.line([(x, 72), (x, 141)], fill=hx("1a0a10"))
    noise(img, (90, 66, 194, 141), 3, 1404)
    # the roll-down shutter, rolled up into its box
    d.rectangle([89, 66, 195, 71], fill=hx("3a2a1c"), outline=hx("140a06"))
    for y in (68, 70):
        d.line([(90, y), (194, y)], fill=hx("201610"))
    d.line([(90, 67), (194, 67)], fill=hx("5a4430"))
    # hat shelf, three hats
    d.rectangle([90, 78, 194, 80], fill=hx("4a2a14"))
    d.line([(90, 78), (194, 78)], fill=hx("7a4a24"))
    d.line([(90, 81), (194, 81)], fill=hx("080204"))
    d.ellipse([96, 72, 106, 80], fill=hx("3a3430"))
    d.rectangle([96, 76, 106, 78], fill=hx("3a3430"))
    d.line([(94, 77), (108, 77)], fill=hx("4a4440"))
    d.line([(97, 76), (105, 76)], fill=hx("5a1a1a"))
    d.rectangle([128, 70, 136, 77], fill=hx("26222a"))
    d.line([(125, 77), (139, 77)], fill=hx("36323c"))
    d.line([(128, 75), (136, 75)], fill=hx("6a1a22"))
    d.line([(129, 71), (129, 74)], fill=hx("2e2a34"))
    d.polygon([(170, 77), (172, 72), (176, 71), (180, 72), (182, 77)], fill=hx("5a4a36"))
    d.line([(168, 77), (184, 77)], fill=hx("6a5a44"))
    d.line([(173, 72), (179, 72)], fill=hx("221a12"))
    d.polygon([(150, 77), (162, 77), (160, 74), (152, 74)], fill=hx("4a3a5a"))
    d.line([(150, 76), (162, 76)], fill=hx("6a5a7a"))
    # brass hanging rail
    d.rectangle([90, 83, 194, 84], fill=gold_d)
    d.line([(90, 83), (194, 83)], fill=gold)
    for bx in (92, 192):
        d.rectangle([bx - 1, 81, bx + 1, 85], fill=GOLD_DK)
    # a hat box and an umbrella stand, half-hidden under the coats
    d.rectangle([92, 128, 106, 141], fill=hx("5a2a3a"))
    d.ellipse([92, 125, 106, 131], fill=hx("6a3448"), outline=hx("2a1018"))
    d.line([(92, 134), (106, 134)], fill=hx("c8b080"))
    d.rectangle([183, 122, 193, 141], fill=hx("3a3a40"), outline=hx("141418"))
    d.line([(184, 123), (184, 140)], fill=hx("6a6a74"))
    for ux, uc in ((185, "4a2a14"), (188, "1a1a1a"), (191, "6a4a24")):
        d.line([(ux, 122), (ux, 108)], fill=hx("1a1a1e"))
        d.arc([ux - 3, 104, ux + 1, 110], 180, 360, fill=hx(uc))
    rnd = random.Random(1405)
    coats = (("2a2a32", None, False), ("1e1a1a", "6a1420", False), ("2e2418", None, True), ("1a1c26", None, False),
             ("241e22", "4a2a5a", False), ("2a2420", None, False), ("1c1a1e", "6a1420", True))
    for i, (col, lining, fur) in enumerate(coats):
        x = 100 + i * 13
        if i % 2:
            _hung_cloak(d, x, 130, 9, mul(hx(col), 0.75), rnd, lining, fur)
    for i, (col, lining, fur) in enumerate(coats):
        x = 100 + i * 13
        if not i % 2:
            _hung_cloak(d, x, 136, 10, hx(col), rnd, lining, fur)
    shadow(img, "rect", [90, 66, 194, 92], 0.25, 5)
    shadow(img, "rect", [90, 120, 194, 141], 0.35, 4)
    # the CLOAKS cartouche above, scrolled at both ends
    for sx in (114, 170):
        d.ellipse([sx - 4, 52, sx + 4, 60], fill=gold_d, outline=GOLD_DK)
        d.ellipse([sx - 2, 54, sx + 1, 57], outline=gold)
    d.rectangle([114, 51, 170, 61], fill=gold, outline=GOLD_DK)
    d.line([(115, 52), (169, 52)], fill=GOLD_L)
    d.line([(115, 60), (169, 60)], fill=gold_d)
    d.rectangle([117, 53, 167, 59], outline=gold_d)
    text(img, (142, 57), "CLOAKS", hx("2a1808"), size=8)
    for nx in (119, 165):
        d.point((nx, 56), fill=GOLD_DK)


def _counter(d, img, gold, gold_d, wax):
    """The coat-check counter: mahogany, raised gilt panels, the bell, the ledger and the house wax."""
    d.rectangle([82, 148, 202, FLOOR + 2], fill=hx("3a1018"), outline=hx("140408"))
    rnd = random.Random(1406)
    for _ in range(40):
        gx, gy = rnd.randint(84, 200), rnd.randint(150, 180)
        d.line([(gx, gy), (gx, gy + rnd.randint(3, 9))], fill=hx(rnd.choice(("461420", "300c14"))))
    for px in (82, 121, 160, 198):
        d.rectangle([px, 148, px + 4, 182], fill=hx("4a1620"))
        d.line([(px, 148), (px, 182)], fill=hx("6a2a30"))
        d.line([(px + 4, 148), (px + 4, 182)], fill=hx("1a0408"))
        d.rectangle([px, 150, px + 4, 152], fill=gold_d)
    for x0, x1 in ((88, 119), (127, 158), (166, 196)):
        y0, y1 = 154, 180
        d.rectangle([x0, y0, x1, y1], fill=hx("2a0810"), outline=gold_d)
        d.polygon([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1), (x1 - 4, y0 + 4), (x0 + 4, y0 + 4)], fill=hx("5a2030"))
        d.polygon([(x0 + 1, y0 + 1), (x0 + 4, y0 + 4), (x0 + 4, y1 - 4), (x0 + 1, y1 - 1)], fill=hx("4a1826"))
        d.polygon([(x0 + 1, y1 - 1), (x0 + 4, y1 - 4), (x1 - 4, y1 - 4), (x1 - 1, y1 - 1)], fill=hx("1a0408"))
        d.polygon([(x1 - 1, y0 + 1), (x1 - 1, y1 - 1), (x1 - 4, y1 - 4), (x1 - 4, y0 + 4)], fill=hx("22060c"))
        d.rectangle([x0 + 4, y0 + 4, x1 - 4, y1 - 4], fill=hx("401220"))
        mx, my = (x0 + x1) // 2, (y0 + y1) // 2
        d.polygon([(mx, my - 6), (mx + 8, my), (mx, my + 6), (mx - 8, my)], outline=gold_d)
        d.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=gold, outline=GOLD_DK)
        d.point((mx - 1, my - 1), fill=GOLD_L)
    d.rectangle([80, 182, 204, FLOOR + 2], fill=hx("1e0608"))
    d.line([(80, 182), (204, 182)], fill=gold)
    d.line([(80, 184), (204, 184)], fill=gold_d)
    # the top, overhanging, with a gilt nosing
    d.rectangle([78, 141, 206, 148], fill=hx("5a1e14"))
    d.line([(78, 141), (206, 141)], fill=hx("9a4a2c"))
    d.line([(78, 142), (206, 142)], fill=hx("7a3220"))
    d.line([(78, 145), (206, 145)], fill=gold_d)
    d.line([(78, 146), (206, 146)], fill=gold)
    d.line([(78, 148), (206, 148)], fill=hx("140408"))
    shadow(img, "rect", [82, 149, 202, 154], 0.5, 2)
    # service bell
    d.ellipse([88, 139, 102, 142], fill=GOLD_DK)
    d.ellipse([90, 133, 100, 141], fill=gold, outline=gold_d)
    d.arc([91, 134, 99, 140], 200, 290, fill=GOLD_L)
    d.point((92, 135), fill=hx("fff0c0"))
    d.rectangle([94, 130, 96, 133], fill=gold_d)
    d.point((95, 130), fill=GOLD_L)
    # the claim ledger, open, a ribbon hanging over the edge
    d.polygon([(106, 141), (136, 141), (133, 136), (109, 136)], fill=hx("e8dcc0"), outline=hx("6a5a40"))
    d.line([(121, 136), (121, 141)], fill=hx("8a7a5a"))
    for ly in (137, 139):
        d.line([(110, ly), (119, ly)], fill=hx("8a8070"))
        d.line([(123, ly), (132, ly)], fill=hx("8a8070"))
    d.line([(124, 141), (125, 146)], fill=hx("a01818"))
    # inkwell and pen
    d.rectangle([140, 137, 145, 141], fill=hx("101018"), outline=hx("2a2a3a"))
    d.rectangle([141, 135, 144, 137], fill=gold)
    d.line([(143, 135), (148, 126)], fill=hx("e8e0d0"))
    d.line([(147, 127), (149, 125)], fill=hx("c8c0b0"))
    # the seal tray; the stick of house wax lies on it until it's taken
    d.rectangle([150, 138, 182, 141], fill=hx("2a2028"), outline=gold_d)
    d.line([(151, 138), (181, 138)], fill=gold)
    d.rectangle([156, 139, 176, 140], fill=hx("3a1a2a"))
    if not wax:
        d.rectangle([154, 135, 176, 137], fill=hx("a01818"))
        d.line([(154, 135), (172, 135)], fill=hx("e05050"))
        d.line([(154, 137), (176, 137)], fill=hx("600a0a"))
        d.rectangle([171, 135, 176, 137], fill=hx("e8e0d0"))
        d.line([(172, 136), (175, 136)], fill=hx("a01818"))
        d.point((154, 136), fill=hx("701010"))
    # a chamberstick for melting it, and the claim tickets on their spike
    d.ellipse([185, 139, 197, 142], fill=gold_d, outline=GOLD_DK)
    d.arc([195, 137, 199, 141], 270, 90, fill=gold_d)
    d.rectangle([189, 130, 192, 139], fill=hx("e8e0c8"))
    d.line([(189, 130), (189, 139)], fill=hx("fff8e8"))
    d.polygon([(190, 124), (192, 128), (190, 130), (189, 128)], fill=hx("f8e090"))
    d.point((190, 128), fill=hx("fffff0"))
    d.line([(201, 141), (201, 132)], fill=hx("8a8a8a"))
    for ty in (136, 138, 140):
        d.rectangle([198, ty, 204, ty + 1], fill=hx("d8c898") if ty % 4 else hx("c8a878"))
    light(img, "ellipse", [174, 112, 206, 144], hx("f0c070"), 0.25, 6)


def _cloak(d, kind, cx, col):
    """A black ceremonial cloak hung by its hood: gold-thread hem, cord girdle, emblem roundel, signet on the clasp."""
    black, deep, sheen, rim = hx("16141a"), hx("08060c"), hx("2a2632"), hx("3c3646")
    d.line([(cx, 56), (cx, 60)], fill=GOLD)
    d.arc([cx - 2, 58, cx + 2, 63], 0, 180, fill=GOLD)
    hem = [(cx + 15, 172), (cx + 11, 175), (cx + 7, 171), (cx + 3, 174), (cx - 2, 172), (cx - 6, 175),
           (cx - 10, 171), (cx - 15, 173)]
    body = [(cx - 9, 80), (cx + 9, 80), (cx + 12, 92)] + hem + [(cx - 12, 92)]
    d.polygon(body, fill=black)
    # folds: deep troughs with a sheen on each crest, rim-lit from the sconces
    for k in (-3, -1, 1, 3):
        top, bot = cx + k * 2, cx + k * 4
        d.line([(top, 92), (bot, 172)], fill=deep)
        d.line([(top + 1, 94), (bot + 2, 170)], fill=sheen)
    d.line([(cx - 12, 92), (cx - 15, 172)], fill=rim)
    d.line([(cx + 12, 92), (cx + 15, 172)], fill=hx("0e0c12"))
    # the cloak parts down the front over a crimson lining
    d.polygon([(cx - 1, 106), (cx + 1, 106), (cx + 4, 173), (cx - 3, 173)], fill=hx("4a0c16"))
    d.line([(cx - 1, 106), (cx - 3, 173)], fill=GOLD_D)
    d.line([(cx + 1, 106), (cx + 4, 173)], fill=deep)
    for i in range(len(hem) - 1):
        (ax, ay), (bx, by) = hem[i], hem[i + 1]
        d.line([(ax, ay - 3), (bx, by - 3)], fill=GOLD_D)
    # the hood, hung from its peak; the face opening a black hollow
    hood = [(cx - 1, 61), (cx + 1, 61), (cx + 9, 70), (cx + 11, 80), (cx + 7, 88), (cx - 7, 88), (cx - 11, 80),
            (cx - 9, 70)]
    d.polygon(hood, fill=hx("1c1822"))
    d.line([(cx - 1, 62), (cx - 9, 71), (cx - 11, 80)], fill=rim)
    d.line([(cx, 62), (cx - 4, 70)], fill=deep)
    d.line([(cx, 62), (cx + 5, 70)], fill=deep)
    d.polygon([(cx - 6, 86), (cx - 6, 76), (cx - 3, 70), (cx + 3, 70), (cx + 6, 76), (cx + 6, 86)], fill=hx("050308"))
    d.line([(cx - 6, 86), (cx - 6, 76), (cx - 3, 70), (cx, 69)], fill=sheen)
    d.line([(cx + 6, 76), (cx + 6, 86)], fill=hx("0e0c12"))
    d.line([(cx - 4, 74), (cx - 4, 85)], fill=hx("100c14"))
    # clasp, chain and the signet ring hanging from it
    for sx in (cx - 5, cx + 5):
        d.ellipse([sx - 2, 86, sx + 2, 90], fill=GOLD, outline=GOLD_DK)
        d.point((sx - 1, 87), fill=GOLD_L)
    d.line([(cx - 3, 88), (cx, 90), (cx + 3, 88)], fill=GOLD_D)
    d.ellipse([cx - 2, 90, cx + 2, 95], outline=GOLD)
    d.rectangle([cx - 1, 94, cx + 1, 96], fill=hx(col), outline=GOLD_DK)
    _emblem(d, kind, cx, 106, col)
    # a cord girdle, knotted, two tassels
    d.line([(cx - 12, 124), (cx - 6, 127), (cx, 128), (cx + 6, 127), (cx + 12, 124)], fill=GOLD_D, width=2)
    for x in range(cx - 10, cx + 11, 3):
        d.point((x, 126 + (1 if abs(x - cx) < 6 else 0)), fill=GOLD)
    d.ellipse([cx - 2, 126, cx + 2, 130], fill=GOLD)
    for tx, ty in ((cx - 2, 144), (cx + 3, 140)):
        d.line([(cx, 129), (tx, ty)], fill=GOLD_D)
        d.polygon([(tx - 1, ty), (tx + 1, ty), (tx + 2, ty + 5), (tx - 2, ty + 5)], fill=GOLD)
        d.line([(tx, ty + 1), (tx, ty + 5)], fill=GOLD_D)


def _stand(d, img, gold, gold_d):
    shadow(img, "ellipse", [226, FLOOR - 4, 290, FLOOR + 10], 0.6, 3)
    for fx, fy in ((236, FLOOR + 3), (280, FLOOR + 3), (258, FLOOR + 7)):
        d.line([(258, FLOOR - 6), (fx, fy)], fill=gold_d, width=3)
        d.line([(258, FLOOR - 7), (fx, fy - 1)], fill=gold)
        d.ellipse([fx - 3, fy - 2, fx + 3, fy + 2], fill=gold_d, outline=GOLD_DK)
    d.rectangle([255, 56, 261, FLOOR - 4], fill=gold_d)
    d.line([(256, 56), (256, FLOOR - 4)], fill=gold)
    d.line([(257, 56), (257, FLOOR - 4)], fill=GOLD_L)
    d.line([(261, 56), (261, FLOOR - 4)], fill=GOLD_DK)
    for cy in (64, 120, 176, FLOOR - 6):
        d.ellipse([252, cy - 2, 264, cy + 2], fill=gold, outline=GOLD_DK)
        d.line([(254, cy - 1), (258, cy - 1)], fill=GOLD_L)
    for s in (-1, 1):
        d.line([(258, 74), (258 + 10 * s, 64), (258 + 16 * s, 57)], fill=gold_d, width=2)
        d.arc([258 + (4 if s > 0 else -14), 60, 258 + (14 if s > 0 else -4), 70], 0, 360, fill=GOLD_DK)
    d.rectangle([212, 51, 304, 56], fill=gold_d)
    d.line([(212, 52), (304, 52)], fill=gold)
    d.line([(212, 53), (304, 53)], fill=GOLD_L)
    d.line([(212, 56), (304, 56)], fill=GOLD_DK)
    for fx in (210, 306):
        d.ellipse([fx - 3, 50, fx + 3, 57], fill=gold, outline=GOLD_DK)
        d.point((fx - 1, 52), fill=GOLD_L)
    d.ellipse([253, 43, 263, 53], fill=gold, outline=GOLD_DK)
    d.point((256, 46), fill=GOLD_L)
    d.polygon([(258, 36), (260, 43), (256, 43)], fill=gold)


def _inner_door(d, img, gold, gold_d, door):
    x0, y0, x1, y1 = INNER
    mx = (x0 + x1) // 2
    # fluted pilasters and an arched, gilt surround with a keystone and a fanlight
    for px in (359, 453):
        d.rectangle([px, 52, px + 8, y1], fill=gold_d, outline=GOLD_DK)
        for fx in (px + 2, px + 4, px + 6):
            d.line([(fx, 58), (fx, y1 - 12)], fill=GOLD_DK)
            d.line([(fx + 1, 58), (fx + 1, y1 - 12)], fill=gold)
        d.rectangle([px - 2, 46, px + 10, 52], fill=gold, outline=GOLD_DK)
        d.line([(px - 1, 47), (px + 9, 47)], fill=GOLD_L)
        for vx in (px + 1, px + 7):
            d.ellipse([vx - 2, 47, vx + 2, 51], outline=GOLD_DK)
        d.rectangle([px - 2, y1 - 10, px + 10, y1], fill=gold, outline=GOLD_DK)
        d.line([(px - 2, y1 - 6), (px + 10, y1 - 6)], fill=GOLD_DK)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1], fill=GOLD_DK)
    d.pieslice([356, 20, 464, 72], 180, 360, fill=gold_d, outline=GOLD_DK)
    d.arc([358, 22, 462, 70], 190, 350, fill=gold)
    for a in range(190, 360, 14):
        v = _dir(a)
        d.line([(410 + v[0] * 46, 46 + v[1] * 20), (410 + v[0] * 54, 46 + v[1] * 26)], fill=GOLD_DK)
    d.pieslice([x0, 28, x1, 64], 180, 360, fill=hx("1a080e"), outline=GOLD_DK)
    for a in range(195, 360, 22):
        v = _dir(a)
        d.line([(410, 46), (410 + v[0] * 42, 46 + v[1] * 18)], fill=gold_d)
    d.pieslice([400, 38, 420, 54], 180, 360, fill=gold_d, outline=GOLD_DK)
    d.point((410, 42), fill=GOLD_L)
    d.polygon([(404, 18), (416, 18), (414, 30), (406, 30)], fill=gold, outline=GOLD_DK)
    d.ellipse([407, 20, 413, 26], fill=hx("1a080e"), outline=GOLD_L)
    d.point((410, 23), fill=gold)
    d.rectangle([x0 - 2, 45, x1 + 2, 46], fill=gold)
    if door:
        # the procession hall beyond: a red runner between candlelit walls, light at the far end
        vx0, vx1, vy0, vy1 = mx - 8, mx + 8, 98, 142
        d.rectangle([x0, y0, x1, y1], fill=hx("140408"))
        d.polygon([(x0, y0), (x1, y0), (vx1, vy0), (vx0, vy0)], fill=hx("0e0206"))
        d.polygon([(x0, y0), (vx0, vy0), (vx0, vy1), (x0, y1)], fill=hx("2e0a12"))
        d.polygon([(x1, y0), (vx1, vy0), (vx1, vy1), (x1, y1)], fill=hx("220810"))
        d.polygon([(x0, y1), (x1, y1), (vx1, vy1), (vx0, vy1)], fill=hx("3a1410"))
        for t in (0.25, 0.5, 0.72):
            lx = round(x0 + (vx0 - x0) * t)
            d.line([(lx, round(y0 + (vy0 - y0) * t)), (lx, round(y1 + (vy1 - y1) * t))], fill=hx("1a0408"))
            rx = round(x1 + (vx1 - x1) * t)
            d.line([(rx, round(y0 + (vy0 - y0) * t)), (rx, round(y1 + (vy1 - y1) * t))], fill=hx("140206"))
        d.polygon([(mx - 18, y1), (mx + 18, y1), (mx + 4, vy1), (mx - 4, vy1)], fill=hx("7a1418"))
        d.line([(mx - 15, y1), (mx - 3, vy1)], fill=GOLD_D)
        d.line([(mx + 15, y1), (mx + 3, vy1)], fill=GOLD_D)
        vgrad(img, (vx0, vy0, vx1, vy1), hx("f0b060"), hx("c05028"))
        for fx in (mx - 4, mx + 3):
            d.polygon([(fx - 2, vy1), (fx + 2, vy1), (fx + 1, vy0 + 26), (fx, vy0 + 23), (fx - 1, vy0 + 26)], fill=hx("1a0a0a"))
        for t, s in ((0.2, 4), (0.45, 3), (0.65, 2)):
            for side in (x0 + (vx0 - x0) * t, x1 + (vx1 - x1) * t):
                cy = round(y0 + (vy0 - y0) * t + 30 * (1 - t))
                sx = round(side)
                d.line([(sx, cy), (sx, cy + s)], fill=GOLD)
                d.ellipse([sx - 1, cy - s, sx + 1, cy], fill=hx("f8d888"))
                light(img, "ellipse", [sx - 3 * s, cy - 3 * s, sx + 3 * s, cy + 2 * s], hx("e08040"), 0.25, 2)
        # the leaves, swung in against the walls
        for a, b in ((x0, x0 + 12), (x1, x1 - 12)):
            d.polygon([(a, y0), (b, y0 + 6), (b, y1 - 4), (a, y1)], fill=hx("2a0a10"), outline=hx("0a0204"))
            d.polygon([(a + (b - a) // 4, y0 + 14), (b - (b - a) // 4, y0 + 17), (b - (b - a) // 4, y0 + 58),
                       (a + (b - a) // 4, y0 + 60)], outline=gold_d)
            d.polygon([(a + (b - a) // 4, y0 + 94), (b - (b - a) // 4, y0 + 94), (b - (b - a) // 4, y1 - 12),
                       (a + (b - a) // 4, y1 - 10)], outline=gold_d)
            d.line([(b, y0 + 6), (b, y1 - 4)], fill=hx("4a1420"))
        light(img, "polygon", [(vx0, vy0), (vx1, vy0), (x1 + 30, H - 1), (x0 - 30, H - 1)], hx("e08040"), 0.3, 10)
        return
    for a, b in ((x0, mx), (mx, x1)):
        vgrad(img, (a, y0, b, y1), hx("3a0e18"), hx("22060c"))
    d.rectangle([x0, y0, x1, y1], outline=hx("0a0204"))
    d.line([(mx, y0), (mx, y1)], fill=hx("0a0204"))
    d.line([(mx + 1, y0), (mx + 1, y1)], fill=hx("4a1620"))
    for a, b in ((x0 + 6, mx - 6), (mx + 6, x1 - 6)):
        for p0, p1 in ((y0 + 10, y0 + 60), (y0 + 116, y1 - 10)):
            d.rectangle([a, p0, b, p1], fill=hx("2a0810"), outline=gold_d)
            d.polygon([(a + 1, p0 + 1), (b - 1, p0 + 1), (b - 4, p0 + 4), (a + 4, p0 + 4)], fill=hx("5a1a28"))
            d.polygon([(a + 1, p0 + 1), (a + 4, p0 + 4), (a + 4, p1 - 4), (a + 1, p1 - 1)], fill=hx("4a1422"))
            d.polygon([(a + 1, p1 - 1), (a + 4, p1 - 4), (b - 4, p1 - 4), (b - 1, p1 - 1)], fill=hx("12020a"))
            d.polygon([(b - 1, p0 + 1), (b - 1, p1 - 1), (b - 4, p1 - 4), (b - 4, p0 + 4)], fill=hx("1a040c"))
            d.rectangle([a + 4, p0 + 4, b - 4, p1 - 4], fill=hx("36101a"))
            cx, cy = (a + b) // 2, (p0 + p1) // 2
            r = min(8, (p1 - p0) // 2 - 6)
            d.polygon([(cx, cy - r), (cx + 6, cy), (cx, cy + r), (cx - 6, cy)], outline=gold_d)
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=gold, outline=GOLD_DK)
            for v in ((-2, 0), (2, 0), (0, -2), (0, 2)):
                d.point((cx + v[0], cy + v[1]), fill=GOLD_DK)
            d.point((cx, cy), fill=GOLD_L)
    # studs down the meeting stiles, hinges on the hanging stiles
    for sy in range(y0 + 6, y1 - 4, 10):
        for sx in (mx - 3, mx + 4):
            d.point((sx, sy), fill=gold)
            d.point((sx, sy + 1), fill=GOLD_DK)
    for hy in (y0 + 16, y0 + 74, y1 - 24):
        for hx0 in (x0, x1 - 3):
            d.rectangle([hx0, hy, hx0 + 3, hy + 8], fill=gold_d, outline=GOLD_DK)
            d.point((hx0 + 1, hy + 2), fill=gold)
    # the card slot, in an engraved brass plate
    d.rectangle([mx - 11, 111, mx + 11, 129], fill=hx("b08a3a"), outline=GOLD_DK)
    d.line([(mx - 10, 112), (mx + 10, 112)], fill=GOLD_L)
    d.line([(mx - 10, 112), (mx - 10, 128)], fill=hx("d8b060"))
    d.line([(mx - 10, 128), (mx + 10, 128)], fill=gold_d)
    d.rectangle([mx - 8, 114, mx + 8, 126], outline=gold_d)
    for sx, sy in ((mx - 9, 113), (mx + 9, 113), (mx - 9, 127), (mx + 9, 127)):
        d.point((sx, sy), fill=GOLD_DK)
    d.line([(mx - 5, 116), (mx + 5, 116)], fill=gold_d)
    d.rectangle([mx - 6, 119, mx + 6, 121], fill=hx("0a0204"))
    d.line([(mx - 6, 122), (mx + 6, 122)], fill=GOLD_L)
    d.line([(mx - 6, 118), (mx + 6, 118)], fill=GOLD_DK)
    d.line([(mx - 3, 124), (mx + 3, 124)], fill=gold_d)
    # pull handles on long backplates, a keyhole under the right one
    for s in (-1, 1):
        bx = mx + 7 * s
        d.rounded_rectangle([bx - 3, 132, bx + 3, 158], 2, fill=gold_d, outline=GOLD_DK)
        d.line([(bx - 2, 133), (bx - 2, 157)], fill=gold)
        d.rectangle([bx - 1, 135, bx + 1, 151], fill=gold, outline=GOLD_DK)
        d.line([(bx, 135), (bx, 151)], fill=GOLD_L)
    d.ellipse([mx + 6, 153, mx + 8, 155], fill=hx("0a0204"))
    # brass kick plates and the threshold
    for a, b in ((x0 + 2, mx - 2), (mx + 2, x1 - 2)):
        d.rectangle([a, y1 - 9, b, y1 - 2], fill=gold_d, outline=GOLD_DK)
        d.line([(a + 1, y1 - 8), (b - 1, y1 - 8)], fill=gold)
        for sx in (a + 2, b - 2):
            d.point((sx, y1 - 5), fill=GOLD_DK)
    d.rectangle([x0 - 4, y1 - 1, x1 + 4, y1 + 1], fill=gold, outline=GOLD_DK)


def _vest_sconce(d, img, sx, oy=8):
    """A gilt wall sconce: an oval backplate, a scrolled arm, a drip cup and a frosted tulip shade with its bulb lit."""
    # glow on the damask behind it first, so the brass reads on top
    light(img, "ellipse", [sx - 34, 36 + oy, sx + 34, 110 + oy], hx("e0a050"), 0.2, 14)
    light(img, "ellipse", [sx - 12, 44 + oy, sx + 12, 58 + oy], hx("ffd890"), 0.18, 5)
    # backplate: an oval with a beaded rim and a boss in the middle
    d.ellipse([sx - 4, 72 + oy, sx + 4, 92 + oy], fill=GOLD_D, outline=GOLD_DK)
    d.ellipse([sx - 3, 73 + oy, sx + 3, 91 + oy], outline=GOLD)
    d.line([(sx - 2, 75 + oy), (sx - 2, 89 + oy)], fill=GOLD_L)
    for by in range(75 + oy, 91 + oy, 3):
        d.point((sx + 3, by), fill=GOLD_DK)
    d.ellipse([sx - 2, 80 + oy, sx + 2, 84 + oy], fill=GOLD, outline=GOLD_DK)
    d.point((sx - 1, 81 + oy), fill=hx("fff0c0"))
    # a finial and a little tassel dropping below the plate
    d.polygon([(sx - 2, 92 + oy), (sx + 2, 92 + oy), (sx, 96 + oy)], fill=GOLD_D)
    d.line([(sx, 96 + oy), (sx, 98 + oy)], fill=GOLD_D)
    d.polygon([(sx - 1, 98 + oy), (sx + 1, 98 + oy), (sx + 2, 102 + oy), (sx - 2, 102 + oy)], fill=hx("8a1a24"))
    d.line([(sx, 99 + oy), (sx, 102 + oy)], fill=hx("c84050"))
    # the scrolled arm, curling out of the boss and up to the cup
    d.arc([sx - 1, 76 + oy, sx + 7, 86 + oy], 270, 90, fill=GOLD)
    d.arc([sx, 77 + oy, sx + 6, 85 + oy], 270, 90, fill=GOLD_DK)
    d.line([(sx + 3, 76 + oy), (sx + 1, 72 + oy), (sx, 69 + oy)], fill=GOLD)
    d.point((sx + 2, 74 + oy), fill=GOLD_L)
    d.ellipse([sx + 5, 84 + oy, sx + 7, 86 + oy], fill=GOLD_D)
    # drip cup / bobeche
    d.ellipse([sx - 5, 66 + oy, sx + 5, 70 + oy], fill=GOLD_D, outline=GOLD_DK)
    d.line([(sx - 4, 67 + oy), (sx + 3, 67 + oy)], fill=GOLD_L)
    for px_ in range(sx - 4, sx + 5, 2):
        d.point((px_, 70 + oy), fill=GOLD)
    # frosted tulip shade, scalloped at the lip, the bulb burning through it
    shade = [(sx - 3, 66 + oy), (sx + 3, 66 + oy), (sx + 5, 62 + oy), (sx + 6, 57 + oy), (sx + 5, 54 + oy), (sx + 3, 55 + oy), (sx + 1, 53 + oy),
             (sx - 1, 53 + oy), (sx - 3, 55 + oy), (sx - 5, 54 + oy), (sx - 6, 57 + oy), (sx - 5, 62 + oy)]
    d.polygon(shade, fill=hx("c8843a"), outline=hx("5a2e10"))
    for rx in (sx - 3, sx + 2):
        d.line([(rx, 55 + oy), (rx + (1 if rx > sx else -1), 64 + oy)], fill=hx("9a5a24"))
    d.line([(sx - 4, 62 + oy), (sx - 5, 57 + oy)], fill=hx("f0c070"))
    d.line([(sx + 4, 62 + oy), (sx + 5, 57 + oy)], fill=hx("7a3e16"))
    d.ellipse([sx - 1, 59 + oy, sx + 1, 63 + oy], fill=hx("fff8e0"))
    d.point((sx, 60 + oy), fill=hx("ffffff"))
    for lx in (sx - 5, sx - 1, sx + 3):
        d.point((lx, 55 + oy), fill=hx("f8d890"))
    light(img, "ellipse", [sx - 2, 58 + oy, sx + 2, 64 + oy], hx("fff2c8"), 0.3, 1)


def paint_vestibule(wax=False, door=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    gold, gold_d = GOLD, GOLD_D
    # wine-dark damask walls, a gilt frieze, a black ceiling
    vgrad(img, (0, 0, W - 1, FLOOR), hx("4a1624"), hx("2a0a14"))
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
    _hatch(d, img, gold, gold_d)
    _counter(d, img, gold, gold_d, wax)
    # the cloak stand: three hooded cloaks, an emblem worked at each breast, a signet on each clasp
    _stand(d, img, gold, gold_d)
    for kind, cx, col in CLOAKS:
        _cloak(d, kind, cx, col)
    # the brass plaque and the inner door with its card slot
    d.rectangle([314, 94, 354, 118], fill=hx("b08a3a"), outline=hx("4a3412"))
    d.rectangle([316, 96, 352, 116], outline=hx("e0c070"))
    for y in (101, 105, 109):
        d.line([(320, y), (348, y)], fill=hx("5a4418"))
    _inner_door(d, img, gold, gold_d, door)
    # sconces
    for sx in (206, 310, 464):
        _vest_sconce(d, img, sx)
    shadow(img, "ellipse", [214, 168, 302, 196], 0.3, 6)
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


PASTE = "c8b060"
PASTE_SHINE = "f8f0c0"


def clipping_top_pasted(d, im):
    """The upper half with a glossy line of paste along its torn edge."""
    clipping_top(d, im)
    edge = [(26 - i * 3, 13 + (i % 2) * 2) for i in range(8)]
    d.line(edge, fill=hx(PASTE), width=2)
    for x, y in edge[1::3]:
        d.point((x, y - 1), fill=hx(PASTE_SHINE))


def clipping_bottom_pasted(d, im):
    """The lower half with a glossy line of paste along its torn edge."""
    clipping_bottom(d, im)
    edge = [(4 + i * 3, 9 + (i % 2) * 2) for i in range(1, 8)]
    d.line(edge, fill=hx(PASTE), width=2)
    for x, y in edge[::3]:
        d.point((x, y + 1), fill=hx(PASTE_SHINE))


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
         ("clipping_top_pasted", clipping_top_pasted), ("clipping_bottom_pasted", clipping_bottom_pasted),
         ("paste", paste), ("sealing_wax", sealing_wax), ("wax_soft", wax_soft),
         ("invitation_waxed", invitation_waxed), ("sealed_invitation", sealed_invitation),
         ("signet_raven", signet_raven), ("signet_lion", signet_lion), ("signet_stag", signet_stag))


def build():
    build_morgue()
    build_vestibule()
    for name, fn in ICONS:
        save(_icon(fn), "items", f"{name}.png")
