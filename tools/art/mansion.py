"""Act 3: the Harrington mansion on the Gold Coast at night - the service yard behind the house (kitchen door, alarm bell,
coal bin), the dark kitchen, Harrington senior's study and his bedroom.

Each room is painted once per state; overlays are cut against the base so they line up pixel-exactly at the printed
top-left. The bedroom's bed is its own sprite, cut against a room painted without it."""
import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from .common import W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, palette_of, pixelize, save, floor_boards
from .act2_rooms import bricks, overlay
from .furniture import Room3D

H = FULL_H


# ------------------------------------------------------------------------------------------------ SHARED

def grade(img, night, pools=(), emit=None):
    """Night grade: multiplies the picture by a cold tint, warmed (or cooled) inside soft pools of light
    (cx, cy, rx, ry, multiplier, strength). Emissive pixels (lamp glass, fire) are put back ungraded."""
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    night = np.array(night, np.float32)
    mult = np.ones((h, w, 3), np.float32) * night
    for cx, cy, rx, ry, col, k in pools:
        wgt = k * np.exp(-np.hypot((xx - cx) / rx, (yy - cy) / ry) ** 1.6)
        mult += wgt[..., None] * (np.array(col, np.float32) - night)
    arr = np.asarray(img.convert("RGB"), np.float32) * mult
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if emit is not None:
        out = Image.composite(img.convert("RGB"), out, emit)
    return out


def flagstones(img, y0, y1, vx, vy, cols, c1, c2, seam, seed, moss=None):
    """Perspective flagstone paving between rows y0..y1, staggered courses, each stone a slightly different shade."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)

    def xat(xb, y):
        return vx + (xb - vx) * (y - vy) / (y1 - vy)

    rows, y, step = [], float(y0), 6.0
    while y < y1:
        rows.append(y)
        y += step
        step *= 1.32
    rows.append(float(y1 + 40))
    for r in range(len(rows) - 1):
        ya, yb = rows[r], rows[r + 1]
        off = 0.5 if r % 2 else 0.0
        for i in range(-30, 30):
            xa, xb = vx + (i + off) * cols, vx + (i + 1 + off) * cols
            c = mix(c1, c2, rnd.random())
            poly = [(xat(xa, ya), ya), (xat(xb, ya), ya), (xat(xb, yb), yb), (xat(xa, yb), yb)]
            d.polygon(poly, fill=c, outline=seam)
            d.line([poly[0], poly[1]], fill=mul(c, 1.12))
            if moss and rnd.random() < 0.35:
                mx = xat(xa, yb) + rnd.random() * (xat(xb, yb) - xat(xa, yb))
                d.line([(mx - 3, yb), (mx + 3, yb)], fill=moss)


def rug(R, img, x0, x1, z0, z1, field, border, accent, seed=1):
    """A Persian rug lying on the floor: border, guard stripes, a central medallion and a scatter of motifs."""
    y = 0.05
    R.quad(img, [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], border)
    b = min(x1 - x0, z1 - z0) * 0.12
    R.quad(img, [(x0 + b * 0.35, y, z0 + b * 0.35), (x1 - b * 0.35, y, z0 + b * 0.35), (x1 - b * 0.35, y, z1 - b * 0.35),
                 (x0 + b * 0.35, y, z1 - b * 0.35)], None, accent)
    R.quad(img, [(x0 + b, y, z0 + b), (x1 - b, y, z0 + b), (x1 - b, y, z1 - b), (x0 + b, y, z1 - b)], field)
    d = ImageDraw.Draw(img)
    # repeating motif in the border
    n = int((x1 - x0) / 9)
    for i in range(n):
        x = x0 + (i + 0.5) * (x1 - x0) / n
        for z in (z0 + b * 0.62, z1 - b * 0.62):
            p = R.P(x, y, z)
            d.point(p, fill=accent)
            d.point((p[0] + 1, p[1]), fill=mul(accent, 0.8))
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    rx, rz = (x1 - x0) * 0.22, (z1 - z0) * 0.26
    pts = [R.P(cx + rx * math.cos(t * math.pi / 8), y, cz + rz * math.sin(t * math.pi / 8)) for t in range(16)]
    star = []
    for t in range(16):
        k = 1.0 if t % 2 == 0 else 0.62
        star.append(R.P(cx + rx * k * math.cos(t * math.pi / 8), y, cz + rz * k * math.sin(t * math.pi / 8)))
    d.polygon(pts, fill=mul(field, 1.35))
    d.polygon(star, fill=border, outline=accent)
    d.polygon([R.P(cx + rx * 0.3 * math.cos(t * math.pi / 4), y, cz + rz * 0.3 * math.sin(t * math.pi / 4)) for t in range(8)],
              fill=accent)
    rnd = random.Random(seed)
    for _ in range(int((x1 - x0) * (z1 - z0) / 70)):
        x, z = rnd.uniform(x0 + b * 1.5, x1 - b * 1.5), rnd.uniform(z0 + b * 1.5, z1 - b * 1.5)
        if ((x - cx) / (rx * 1.15)) ** 2 + ((z - cz) / (rz * 1.15)) ** 2 < 1:
            continue
        p = R.P(x, y, z)
        d.point(p, fill=rnd.choice([accent, mul(border, 1.2), mul(field, 1.4)]))
    # fringe at the near edge
    a, bb = R.P(x0, y, z1), R.P(x1, y, z1)
    for x in range(int(a[0]) + 1, int(bb[0]), 2):
        d.line([(x, a[1] + 1), (x, a[1] + 2)], fill=hx("d8ccb0"))


def panel_door(d, x0, y0, x1, y1, col, knob_left=False, frame=None, frame_w=4):
    """A six-panel door in a moulded architrave."""
    frame = frame or mul(col, 1.35)
    d.rectangle([x0 - frame_w, y0 - frame_w, x1 + frame_w, y1], fill=frame)
    d.line([(x0 - frame_w, y0 - frame_w), (x1 + frame_w, y0 - frame_w)], fill=mul(frame, 1.25))
    d.line([(x0 - frame_w, y0 - frame_w), (x0 - frame_w, y1)], fill=mul(frame, 1.15))
    d.line([(x1 + frame_w, y0 - frame_w), (x1 + frame_w, y1)], fill=mul(frame, 0.6))
    d.rectangle([x0 - frame_w - 2, y0 - frame_w - 4, x1 + frame_w + 2, y0 - frame_w - 1], fill=mul(frame, 1.1))
    d.line([(x0 - frame_w - 2, y0 - frame_w - 1), (x1 + frame_w + 2, y0 - frame_w - 1)], fill=mul(frame, 0.5))
    d.rectangle([x0, y0, x1, y1], fill=col)
    d.line([(x0, y0), (x1, y0)], fill=mul(col, 0.5))
    d.line([(x0, y0), (x0, y1)], fill=mul(col, 0.6))
    mx = (x0 + x1) // 2
    h = y1 - y0
    rows = [(y0 + 5, y0 + int(h * 0.18)), (y0 + int(h * 0.24), y0 + int(h * 0.56)), (y0 + int(h * 0.62), y1 - 6)]
    for a, b in rows:
        for px0, px1 in ((x0 + 4, mx - 2), (mx + 2, x1 - 4)):
            d.rectangle([px0, a, px1, b], fill=mul(col, 0.92))
            d.line([(px0, a), (px1, a)], fill=mul(col, 0.55))
            d.line([(px0, a), (px0, b)], fill=mul(col, 0.62))
            d.line([(px0, b), (px1, b)], fill=mul(col, 1.3))
            d.line([(px1, a), (px1, b)], fill=mul(col, 1.18))
            d.rectangle([px0 + 2, a + 2, px1 - 2, b - 2], fill=mul(col, 1.05))
    ky = y0 + int(h * 0.59)
    kx = x0 + 4 if knob_left else x1 - 6
    d.ellipse([kx - 1, ky - 1, kx + 2, ky + 2], fill=hx("d8b458"))
    d.point((kx, ky - 1), fill=hx("fff0b0"))
    d.rectangle([kx, ky + 4, kx + 1, ky + 7], fill=hx("6a5420"))


# ------------------------------------------------------------------------------------------------ MANSION, BACK

BELL = (318, 62, 344, 92)
BIN_HOME = (396, 172, 446, 210)
BIN_MOVED = (306, 172, 356, 210)
DOOR = (250, 98, 288, 196)
STONE, STONE_L, STONE_D = hx("c8bc9e"), hx("e4dabe"), hx("7e735e")
BRICK, MORTAR = hx("8a4634"), hx("5a3a30")
UPPER_Y = (40, 80)
UPPER_X = (64, 132, 196, 372, 444)


def sash(d, x0, y0, x1, y1, glass="dark", bars=False, seed=0, em=None):
    """A sash window in a stone surround: glass is "dark" (moonlit reflections, drawn curtains behind), "lit" or "fire"."""
    rnd = random.Random(seed)
    w = x1 - x0
    cx = (x0 + x1) // 2
    # flat arch of voussoirs with a keystone, a sill on two little corbels
    d.rectangle([x0 - 5, y0 - 3, x1 + 5, y1 + 2], fill=STONE)
    d.line([(x0 - 5, y0 - 3), (x0 - 5, y1 + 2)], fill=STONE_L)
    d.line([(x1 + 5, y0 - 3), (x1 + 5, y1 + 2)], fill=STONE_D)
    d.polygon([(x0 - 8, y0 - 3), (x1 + 8, y0 - 3), (x1 + 6, y0 - 11), (x0 - 6, y0 - 11)], fill=STONE)
    for i in range(1, 6):
        t = i / 6
        xb = x0 - 8 + (w + 16) * t
        xt = x0 - 6 + (w + 12) * t + (t - 0.5) * 4
        d.line([(xb, y0 - 3), (xt, y0 - 11)], fill=STONE_D)
    d.polygon([(cx - 4, y0 - 2), (cx + 4, y0 - 2), (cx + 5, y0 - 13), (cx - 5, y0 - 13)], fill=STONE_L, outline=STONE_D)
    d.line([(x0 - 8, y0 - 11), (x1 + 8, y0 - 11)], fill=STONE_L)
    d.line([(x0 - 8, y0 - 2), (x1 + 8, y0 - 2)], fill=hx("3a2a22"))
    d.rectangle([x0 - 7, y1 + 2, x1 + 7, y1 + 5], fill=STONE_L)
    d.line([(x0 - 7, y1 + 5), (x1 + 7, y1 + 5)], fill=STONE_D)
    for cxx in (x0 - 2, x1 - 1):
        d.rectangle([cxx, y1 + 6, cxx + 3, y1 + 8], fill=STONE)
    d.line([(x0 - 7, y1 + 9), (x1 + 7, y1 + 9)], fill=hx("4a2a22"))
    # reveal and glass
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], fill=STONE_D)
    if glass == "dark":
        for y in range(y0, y1 + 1):
            d.line([(x0, y), (x1, y)], fill=mix(hx("202a44"), hx("0c1020"), (y - y0) / (y1 - y0)))
        # heavy drawn curtains behind the glass, a gap between them
        gap = rnd.randint(2, 6)
        d.rectangle([x0, y0, cx - gap, y1], fill=hx("1c0e12"))
        d.rectangle([cx + gap, y0, x1, y1], fill=hx("1c0e12"))
        for x in range(x0 + 2, x1, 3):
            if abs(x - cx) > gap:
                d.line([(x, y0), (x, y1)], fill=hx("281418"))
        # the moon's sheen across the panes
        for k in range(3):
            xa = x0 + 4 + k * 3 + rnd.randint(0, 4)
            d.line([(xa, y0 + 3), (xa + 8, y0 + 13)], fill=hx("4a5a80"))
    elif glass == "lit":
        for y in range(y0, y1 + 1):
            d.line([(x0, y), (x1, y)], fill=mix(hx("ffd890"), hx("e09848"), (y - y0) / (y1 - y0)))
        d.polygon([(x0, y0), (x0 + 7, y0), (x0 + 4, y1), (x0, y1)], fill=hx("c0582a"))
        d.polygon([(x1, y0), (x1 - 7, y0), (x1 - 4, y1), (x1, y1)], fill=hx("c0582a"))
        for x in range(x0 + 1, x0 + 7, 2):
            d.line([(x, y0), (x + 1, y1)], fill=hx("9a4022"))
        for x in range(x1 - 6, x1, 2):
            d.line([(x, y0), (x - 1, y1)], fill=hx("9a4022"))
        d.rectangle([x0 + 8, y1 - 9, x1 - 8, y1], fill=hx("f8e0a0"))  # lace half-blind
        for x in range(x0 + 9, x1 - 8, 2):
            d.point((x, y1 - 8), fill=hx("c89858"))
        if em is not None:
            em.rectangle([x0, y0, x1, y1], fill=235)
    else:
        # the room ablaze behind the glass (the flames themselves are drawn over everything by _blaze): a white-hot
        # ceiling, the burning curtains hanging in charred rags at either side, and soot fanned up the stonework
        for y in range(y0, y1 + 1):
            d.line([(x0, y), (x1, y)], fill=mix(hx("fff0a0"), hx("c84818"), ((y - y0) / (y1 - y0)) ** 0.8))
        for side, xa in ((1, x0), (-1, x1)):
            for k in range(4):
                xx = xa + side * k
                d.line([(xx, y0), (xx, y0 + rnd.randint(6, y1 - y0 - 4))], fill=hx("3a1a10") if k % 2 else hx("5a2410"))
        for i in range(26):
            f = i / 25
            sx = cx + rnd.gauss(0, 4 + 10 * f)
            sy = y0 - 10 - f * 28 + rnd.randint(-2, 2)
            r = 2 + 4 * (1 - abs(sx - cx) / (w + 10)) + rnd.random() * 2
            d.ellipse([sx - r, sy - r * 0.7, sx + r, sy + r * 0.7], fill=mix(hx("120c0a"), hx("2a1c16"), rnd.random()))
        if em is not None:
            em.rectangle([x0, y0, x1, y1], fill=255)
    # sashes: frame, glazing bars and the meeting rail
    fr = hx("d8d0bc") if glass != "fire" else hx("3a2a20")
    d.rectangle([x0, y0, x1, y1], outline=fr)
    my = (y0 + y1) // 2
    d.rectangle([x0, my - 1, x1, my + 1], fill=fr)
    d.line([(cx, y0), (cx, y1)], fill=fr)
    for yy in ((y0 + my) // 2, (my + y1) // 2):
        d.line([(x0, yy), (x1, yy)], fill=fr)
    if bars:
        for x in range(x0 + 3, x1, 5):
            d.line([(x, y0 - 1), (x, y1 + 1)], fill=hx("161414"))
            d.point((x, y0 - 2), fill=hx("2a2624"))
        d.line([(x0, y0 + 4), (x1, y0 + 4)], fill=hx("161414"))
        d.line([(x0, y1 - 4), (x1, y1 - 4)], fill=hx("161414"))


def coal_bin(d, box, img=None):
    """A stout oak coal bin on runners: iron-strapped corners, a sloping hinged lid with a hasp."""
    x0, y0, x1, y1 = box
    wood, wood_d, wood_l = hx("6a4a30"), hx("3e2a1a"), hx("8a6a46")
    iron = hx("2a2826")
    # cast shadow on the flags behind and below
    d.polygon([(x0 + 2, y1), (x1 + 8, y1 - 2), (x1 + 6, y1 + 3), (x0, y1 + 3)], fill=hx("1a1816"))
    d.rectangle([x0, y0 + 10, x1, y1 - 3], fill=wood)
    for i, y in enumerate(range(y0 + 10, y1 - 3, 7)):
        d.line([(x0, y), (x1, y)], fill=wood_d)
        d.line([(x0 + 1, y + 1), (x1 - 1, y + 1)], fill=wood_l if i % 2 else mul(wood, 1.1))
    for x in range(x0 + 3, x1 - 2, 5):
        d.point((x, y0 + 14), fill=wood_d)
    # the lid: seen from slightly above, sloping back
    d.polygon([(x0 - 2, y0 + 10), (x1 + 2, y0 + 10), (x1, y0 + 1), (x0 + 1, y0 + 1)], fill=wood_l, outline=wood_d)
    for x in range(x0 + 6, x1, 8):
        d.line([(x, y0 + 2), (x - 1, y0 + 9)], fill=mul(wood_l, 0.85))
    d.line([(x0 - 2, y0 + 10), (x1 + 2, y0 + 10)], fill=hx("2a1c10"))
    # iron straps and studs
    for x in (x0, x1 - 3):
        d.rectangle([x, y0 + 10, x + 3, y1 - 3], fill=iron)
        for y in range(y0 + 13, y1 - 4, 6):
            d.point((x + 1, y), fill=hx("6a6660"))
    d.rectangle([x0, y0 + 20, x1, y0 + 22], fill=iron)
    d.rectangle([(x0 + x1) // 2 - 2, y0 + 9, (x0 + x1) // 2 + 2, y0 + 17], fill=hx("3a3632"), outline=hx("121010"))
    # runners and a little spill of coal
    d.rectangle([x0 + 1, y1 - 3, x1 - 1, y1], fill=hx("221a12"))
    for i in range(6):
        cx = x0 + 6 + i * 7
        d.ellipse([cx, y1 - 1, cx + 3, y1 + 2], fill=hx("0c0c0e"))
        d.point((cx + 1, y1 - 1), fill=hx("4a4a56"))


def ivy(d, img, seed, x0, x1, y_top, y_bot, density=1.0):
    rnd = random.Random(seed)
    leaf = [hx("1e3a1e"), hx("2a4a26"), hx("345a2e"), hx("1a2e1a")]
    stems = []
    for _ in range(int(5 * density)):
        x = rnd.uniform(x0, x1)
        y = y_bot
        pts = [(x, y)]
        while y > y_top + rnd.uniform(0, (y_bot - y_top) * 0.4):
            y -= rnd.uniform(4, 9)
            x += rnd.uniform(-5, 5)
            x = min(max(x, x0 - 10), x1 + 10)
            pts.append((x, y))
        stems.append(pts)
        d.line(pts, fill=hx("2a2016"))
    for pts in stems:
        for (x, y) in pts:
            for _ in range(int(7 * density)):
                lx, ly = x + rnd.gauss(0, 5), y + rnd.gauss(0, 4)
                c = rnd.choice(leaf)
                d.polygon([(lx, ly - 2), (lx + 2, ly), (lx, ly + 2), (lx - 2, ly)], fill=c)
                if rnd.random() < 0.25:
                    d.point((lx - 1, ly - 1), fill=hx("5a8a4a"))


IRON, IRON_HI, IRON_MID = hx("101012"), hx("5a6070"), hx("2a2c32")


def _gate_piers(d):
    """Two limestone gate piers: a stepped plinth, a sunk panel, a moulded cap and a ball finial on a neck."""
    for px0 in (-1, 26):
        d.rectangle([px0, 132, px0 + 7, 214], fill=STONE)
        d.line([(px0, 132), (px0, 214)], fill=STONE_L)
        d.line([(px0 + 7, 132), (px0 + 7, 214)], fill=STONE_D)
        d.rectangle([px0 + 2, 146, px0 + 5, 196], fill=mul(STONE, 0.86))  # the sunk panel
        d.line([(px0 + 2, 146), (px0 + 5, 146)], fill=STONE_D)
        d.line([(px0 + 2, 146), (px0 + 2, 196)], fill=STONE_D)
        d.line([(px0 + 2, 197), (px0 + 5, 197)], fill=STONE_L)
        for y in range(152, 196, 9):  # coursing joints
            d.line([(px0 + 1, y), (px0 + 1, y)], fill=STONE_D)
        d.rectangle([px0 - 1, 204, px0 + 8, 214], fill=mul(STONE, 0.92))  # plinth
        d.line([(px0 - 1, 204), (px0 + 8, 204)], fill=STONE_L)
        d.line([(px0 + 8, 204), (px0 + 8, 214)], fill=STONE_D)
        d.rectangle([px0, 136, px0 + 7, 138], fill=mul(STONE, 0.9))  # frieze under the cap
        d.line([(px0, 139), (px0 + 7, 139)], fill=STONE_D)
        d.rectangle([px0 - 2, 131, px0 + 9, 134], fill=STONE_L)  # the cap, overhanging
        d.line([(px0 - 2, 135), (px0 + 9, 135)], fill=hx("3a3028"))
        d.line([(px0 - 1, 130), (px0 + 8, 130)], fill=STONE)
        d.rectangle([px0 + 2, 128, px0 + 5, 129], fill=STONE_D)  # neck and ball
        d.ellipse([px0, 120, px0 + 7, 127], fill=STONE_L, outline=STONE_D)
        d.point((px0 + 2, 122), fill=hx("f4ecd4"))
        d.point((px0 + 3, 122), fill=hx("f4ecd4"))
        for y in range(160, 200, 13):  # weathering streaks
            d.point((px0 + 6, y), fill=mul(STONE, 0.7))


def _garden_gate(d):
    """A wrought-iron garden gate between the piers: spear-headed bars, dog bars, a band of rings, C-scrolls and a
    scrolled overthrow, strap hinges on the left and a ring latch with a padlock on the right."""
    x0, x1, top, bot = 7, 25, 146, 211
    # the overthrow: a half-round of iron with an inner scroll and a fleur-de-lys at the crown
    d.arc([x0 + 1, 130, x1 - 1, 160], 180, 360, fill=IRON, width=2)
    d.arc([x0 + 4, 136, x1 - 4, 156], 180, 360, fill=IRON)
    d.arc([x0 + 1, 130, x1 - 1, 160], 195, 300, fill=IRON_HI)
    for sx, a0, a1 in ((10, 90, 360), (19, 180, 450)):  # small scroll eyes
        d.arc([sx, 140, sx + 4, 144], a0, a1, fill=IRON)
    cx = (x0 + x1) // 2
    d.line([(cx, 130), (cx, 136)], fill=IRON)
    d.polygon([(cx - 1, 128), (cx, 125), (cx + 1, 128)], fill=IRON)
    d.point((cx - 2, 129), fill=IRON)
    d.point((cx + 2, 129), fill=IRON)
    d.point((cx, 126), fill=IRON_HI)
    # stiles and rails
    for x in (x0 + 1, x1 - 1):
        d.line([(x, top - 1), (x, bot)], fill=IRON, width=2)
        d.line([(x - 1 if x < cx else x, top), (x - 1 if x < cx else x, bot)], fill=IRON_HI if x < cx else IRON)
    for y in (top, top + 6, 178, 196, bot - 1):
        d.line([(x0 + 1, y), (x1 - 1, y)], fill=IRON)
    for y in (top, 196):
        d.line([(x0 + 2, y - 1), (x1 - 2, y - 1)], fill=IRON_MID)
    # the main bars with spear heads above the top rail
    for x in range(x0 + 5, x1 - 2, 4):
        d.line([(x, top - 4), (x, bot)], fill=IRON)
        d.polygon([(x - 1, top - 4), (x, top - 8), (x + 1, top - 4)], fill=IRON)
        d.point((x, top - 7), fill=IRON_HI)
        d.point((x - 1, top - 3), fill=IRON)
        d.point((x + 1, top - 3), fill=IRON)
        for y in range(top + 8, bot, 7):  # moonlight catching the round bars
            d.point((x, y), fill=IRON_HI)
        d.rectangle([x - 1, 177, x + 1, 179], fill=IRON_MID)  # collars on the mid rail
    # rings between the top rails and C-scrolls between the mid rails
    for x in range(x0 + 2, x1 - 3, 4):
        d.ellipse([x + 1, top + 1, x + 3, top + 5], outline=IRON)
    for x in range(x0 + 2, x1 - 3, 4):
        d.arc([x, 182, x + 3, 186], 90, 270, fill=IRON)
        d.arc([x + 1, 187, x + 4, 191], 270, 450, fill=IRON)
    # dog bars between the main bars, close to the ground
    for x in range(x0 + 3, x1 - 1, 4):
        d.line([(x, 197), (x, bot)], fill=IRON)
        d.point((x, 198), fill=IRON_HI)
    # strap hinges into the left pier and the latch on the right
    for y in (top + 3, 200):
        d.rectangle([x0 - 3, y, x0 + 6, y + 1], fill=IRON)
        d.rectangle([x0 - 2, y - 1, x0, y + 2], fill=IRON_MID)
        d.point((x0 - 1, y - 1), fill=IRON_HI)
        d.point((x0 + 4, y), fill=IRON_HI)
    d.rectangle([x1 - 3, 170, x1 + 2, 172], fill=IRON)  # latch bar into the right pier
    d.ellipse([x1 - 4, 172, x1 - 1, 176], outline=IRON)  # the ring handle
    d.rectangle([x1 - 1, 174, x1 + 2, 177], fill=hx("7a6a3a"), outline=hx("2a2010"))  # a brass padlock
    d.arc([x1 - 1, 171, x1 + 2, 176], 180, 360, fill=hx("8a8a8a"))
    d.point((x1, 175), fill=hx("1a1410"))
    for x, y in ((x0 + 9, 160), (x0 + 13, 203)):  # rust bloom
        d.point((x, y), fill=hx("5a2a18"))


def _ash_can(img, x0, y0, x1, y1):
    """A galvanised ash can: swaged bands and fine corrugations, a domed lid with a bail handle sitting slightly askew,
    side handles, a couple of dents and the moon catching its left flank."""
    d = ImageDraw.Draw(img)
    zinc, zinc_d, zinc_l = hx("6a6e72"), hx("2e3034"), hx("a8acb0")
    by0 = y0 + 8
    d.ellipse([x0 + 2, y1 - 3, x1 + 6, y1 + 2], fill=hx("16181c"))  # its shadow on the flags
    hgrad(img, (x0 + 2, by0, x1 - 2, y1 - 2), hx("8a8e92"), hx("3e4246"))
    d = ImageDraw.Draw(img)
    for x in range(x0 + 4, x1 - 2, 3):  # vertical corrugations
        d.line([(x, by0 + 2), (x, y1 - 3)], fill=mul(zinc, 0.82))
        d.line([(x + 1, by0 + 2), (x + 1, y1 - 3)], fill=mul(zinc, 1.08) if x < (x0 + x1) // 2 else mul(zinc, 0.92))
    d.line([(x0 + 2, by0), (x0 + 2, y1 - 2)], fill=zinc_d)
    d.line([(x1 - 2, by0), (x1 - 2, y1 - 2)], fill=hx("1e2024"))
    d.line([(x0 + 4, by0 + 1), (x0 + 4, y1 - 3)], fill=zinc_l)  # moonlit flank
    for y in (by0 + 6, y1 - 9):  # swaged bands
        d.line([(x0 + 2, y - 1), (x1 - 2, y - 1)], fill=zinc_l)
        d.line([(x0 + 2, y), (x1 - 2, y)], fill=mul(zinc, 1.05))
        d.line([(x0 + 2, y + 1), (x1 - 2, y + 1)], fill=zinc_d)
    d.rectangle([x0 + 1, y1 - 3, x1 - 1, y1 - 1], fill=hx("3a3c40"), outline=hx("1a1c20"))  # foot ring
    for sx in (x0, x1 - 2):  # side handles
        d.rectangle([sx, by0 + 3, sx + 2, by0 + 5], fill=hx("1e2024"))
        d.point((sx + (0 if sx == x0 else 2), by0 + 4), fill=zinc_l)
    # dents and a rust stain
    d.arc([x0 + 12, by0 + 10, x0 + 17, by0 + 15], 200, 340, fill=zinc_d)
    d.arc([x0 + 12, by0 + 11, x0 + 17, by0 + 16], 20, 160, fill=zinc_l)
    d.point((x0 + 7, y1 - 6), fill=hx("6a4a2a"))
    d.point((x0 + 8, y1 - 5), fill=hx("5a3a20"))
    # the rolled rim and the domed lid, its bail handle folded up
    d.ellipse([x0 + 1, by0 - 3, x1 - 1, by0 + 2], fill=hx("1e2024"))
    d.ellipse([x0 - 1, by0 - 5, x1 + 1, by0 + 1], fill=hx("6e7276"), outline=hx("1e2024"))
    d.arc([x0, by0 - 4, x1, by0], 150, 250, fill=zinc_l)
    d.ellipse([x0 + 4, by0 - 8, x1 - 4, by0 - 1], fill=hx("8a8e92"), outline=hx("3e4246"))
    d.arc([x0 + 5, by0 - 7, x1 - 5, by0 - 2], 180, 260, fill=hx("c8ccd0"))
    hx_ = (x0 + x1) // 2
    d.arc([hx_ - 3, by0 - 12, hx_ + 3, by0 - 5], 180, 360, fill=hx("1e2024"), width=2)
    d.point((hx_ - 2, by0 - 10), fill=zinc_l)


def paint_exterior(moved=False, wedged=False, opened=False, fire=False, fire_t=0.0):
    """The back of the house; fire_t in [0, 1) is the phase of the blaze's flame and smoke loop."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    em = Image.new("L", img.size, 0)
    ed = ImageDraw.Draw(em)
    rnd = random.Random(71)
    # ---- sky: deep blue, the moon low over the garden, a neighbour's roofs, the old elm ----
    vgrad(img, (0, 0, W - 1, 150), hx("10142e"), hx("2e3458"))
    for _ in range(60):
        x, y = rnd.randint(0, W - 1), rnd.randint(0, 40)
        d.point((x, y), fill=rnd.choice([hx("a8b0d0"), hx("70789c"), hx("e0e4f0")]))
    light(img, "ellipse", [-10, -24, 70, 50], hx("6a78b0"), 0.5, 12)
    d.ellipse([18, 4, 32, 18], fill=hx("f4f0d8"))
    d.ellipse([24, 6, 28, 10], fill=hx("dcd6bc"))
    ed.ellipse([18, 4, 32, 18], fill=255)
    # a neighbour's mansard roof and a lit dormer far beyond the garden
    d.polygon([(0, 112), (6, 92), (40, 92), (40, 112)], fill=hx("1a1c2c"))
    d.rectangle([12, 96, 18, 104], fill=hx("e0b060"))
    ed.rectangle([12, 96, 18, 104], fill=200)
    # the elm: dark masses of leaves against the sky
    for i in range(70):
        cx, cy = rnd.gauss(16, 18), rnd.gauss(70, 30)
        r = rnd.randint(5, 12)
        d.ellipse([cx - r, cy - r * 0.8, cx + r, cy + r * 0.8], fill=rnd.choice([hx("0e1810"), hx("121e14"), hx("16241a")]))
    d.polygon([(10, 150), (14, 90), (20, 60), (22, 90), (24, 150)], fill=hx("16120e"))
    for i in range(30):
        cx, cy = rnd.gauss(14, 16), rnd.gauss(52, 24)
        d.point((cx, cy), fill=hx("3a4a5a"))
    # ---- the facade: brick with limestone dressings ----
    FX = 38
    bricks(img, (FX, 24, W - 1, 190), BRICK, MORTAR, 72, h=4, w=11)
    rb = random.Random(79)
    for _ in range(300):  # weathering: soot streaks and a few paler bricks
        x, y = rb.randint(FX, W - 1), rb.randint(30, 186)
        d.line([(x, y), (x, y + rb.randint(2, 10))], fill=mul(BRICK, rb.uniform(0.7, 0.85)))
    # quoins at the corner
    for i, y in enumerate(range(24, 190, 10)):
        wq = 16 if i % 2 else 10
        d.rectangle([FX, y, FX + wq, y + 9], fill=STONE)
        d.line([(FX, y), (FX + wq, y)], fill=STONE_L)
        d.line([(FX, y + 9), (FX + wq, y + 9)], fill=STONE_D)
        d.line([(FX + wq, y), (FX + wq, y + 9)], fill=STONE_D)
    d.line([(FX, 24), (FX, 190)], fill=hx("2a1e1a"))
    # balustraded parapet and a deep cornice with dentils, chimney stacks above
    for cx0 in (150, 404):
        d.rectangle([cx0, 0, cx0 + 22, 14], fill=BRICK)
        bricks(img, (cx0, 0, cx0 + 22, 14), BRICK, MORTAR, cx0, h=4, w=9)
        d.rectangle([cx0 - 2, 0, cx0 + 24, 3], fill=STONE)
        for px_ in (cx0 + 3, cx0 + 13):
            d.rectangle([px_, -1, px_ + 5, 0], fill=hx("8a4a2a"))
    d.rectangle([FX, 6, W - 1, 9], fill=STONE_L)
    d.line([(FX, 10), (W - 1, 10)], fill=STONE_D)
    for x in range(FX + 4, W, 7):
        d.rectangle([x, 11, x + 3, 19], fill=STONE)
        d.line([(x + 1, 12), (x + 1, 18)], fill=STONE_L)
        d.line([(x + 3, 11), (x + 3, 19)], fill=STONE_D)
        d.rectangle([x - 1, 13, x + 4, 15], fill=STONE)
    for x in range(FX + 30, W, 84):
        d.rectangle([x, 9, x + 8, 20], fill=STONE)
        d.line([(x + 8, 9), (x + 8, 20)], fill=STONE_D)
    d.rectangle([FX, 20, W - 1, 24], fill=STONE_L)
    d.rectangle([FX - 2, 24, W - 1, 28], fill=STONE)
    for x in range(FX, W, 4):
        d.rectangle([x, 29, x + 2, 31], fill=STONE)
    d.line([(FX, 31), (W - 1, 31)], fill=STONE_D)
    d.rectangle([FX, 32, W - 1, 34], fill=hx("2a1c18"))
    # string course between the floors
    d.rectangle([FX, 88, W - 1, 92], fill=STONE)
    d.line([(FX, 88), (W - 1, 88)], fill=STONE_L)
    d.line([(FX, 93), (W - 1, 93)], fill=hx("3a2620"))
    # rusticated limestone plinth with the coal hole
    d.rectangle([FX, 182, W - 1, 207], fill=STONE)
    ra = random.Random(74)
    for row, y in enumerate(range(182, 207, 8)):
        off = 13 if row % 2 else 0
        for x in range(FX - off, W, 26):
            c = mul(STONE, ra.uniform(0.86, 1.02))
            d.rectangle([max(FX, x + 1), y + 1, x + 24, y + 7], fill=c)
            d.line([(max(FX, x + 1), y + 1), (x + 24, y + 1)], fill=mul(c, 1.12))
    d.line([(FX, 182), (W - 1, 182)], fill=STONE_L)
    noise(img, (FX, 182, W - 1, 207), 4, 75)
    d.rectangle([452, 192, 476, 205], fill=hx("201c1a"), outline=hx("0c0a0a"))
    for x in range(455, 474, 4):
        for y in (195, 202):
            d.point((x, y), fill=hx("5a5650"))
    d.line([(453, 192), (475, 192)], fill=hx("4a4642"))
    d.ellipse([462, 197, 466, 200], fill=hx("3a3632"))
    # ---- windows: the bedroom floor above, the service rooms below behind bars ----
    for i, x in enumerate(UPPER_X):
        lit = x == 444
        sash(d, x, UPPER_Y[0], x + 26, UPPER_Y[1], "fire" if fire else "lit" if lit else "dark", seed=80 + i, em=ed)
    for i, x in enumerate((70, 156)):
        sash(d, x, 116, x + 34, 166, "fire" if fire else "dark", bars=True, seed=90 + i, em=ed)
    sash(d, 384, 116, 416, 150, "fire" if fire else "dark", bars=True, seed=95, em=ed)
    # cast-iron downpipe with its hopper head
    d.rectangle([362, 35, 366, 206], fill=hx("26242a"))
    d.line([(363, 35), (363, 206)], fill=hx("4a4852"))
    d.polygon([(358, 34), (370, 34), (368, 42), (360, 42)], fill=hx("2a282e"), outline=hx("121014"))
    for y in range(52, 200, 26):
        d.rectangle([361, y, 367, y + 2], fill=hx("16141a"))
    # ---- the service door: a stone surround whose keystone breaks the string course ----
    dx0, dy0, dx1, dy1 = DOOR
    d.rectangle([dx0 - 7, dy0 - 4, dx1 + 7, dy1], fill=STONE)
    d.line([(dx0 - 7, dy0 - 4), (dx0 - 7, dy1)], fill=STONE_L)
    d.line([(dx1 + 7, dy0 - 4), (dx1 + 7, dy1)], fill=STONE_D)
    for y in range(dy0 + 8, dy1, 12):
        d.line([(dx0 - 7, y), (dx0 - 1, y)], fill=STONE_D)
        d.line([(dx1 + 1, y + 6), (dx1 + 7, y + 6)], fill=STONE_D)
    d.rectangle([dx0 - 12, dy0 - 15, dx1 + 12, dy0 - 3], fill=STONE)  # the lintel
    d.line([(dx0 - 12, dy0 - 15), (dx1 + 12, dy0 - 15)], fill=STONE_L)
    d.line([(dx0 - 12, dy0 - 2), (dx1 + 12, dy0 - 2)], fill=hx("2a201a"))
    d.line([(dx1 + 12, dy0 - 15), (dx1 + 12, dy0 - 3)], fill=STONE_D)
    for x in range(dx0 - 10, dx1 + 12, 6):  # Tony's dust along the top
        d.point((x, dy0 - 16), fill=hx("a49a84"))
    kx = (dx0 + dx1) // 2
    d.polygon([(kx - 6, dy0 - 3), (kx + 6, dy0 - 3), (kx + 7, dy0 - 19), (kx - 7, dy0 - 19)], fill=STONE_L, outline=STONE_D)
    d.line([(kx - 3, dy0 - 16), (kx + 3, dy0 - 16)], fill=STONE_D)
    if opened:
        # inside: the dark scullery passage, a gleam of the kitchen tiles, the door swung in against the left jamb
        vgrad(img, (dx0, dy0, dx1, dy1), hx("0c0a08"), hx("181410"))
        for y in range(dy0 + 40, dy1 - 10, 5):
            d.line([(dx0 + 14, y), (dx1, y)], fill=hx("1e1c1a"))
        d.polygon([(dx0, dy0), (dx0 + 10, dy0 + 5), (dx0 + 10, dy1 - 3), (dx0, dy1)], fill=hx("26382c"), outline=hx("0e1610"))
        d.line([(dx0 + 10, dy0 + 5), (dx0 + 10, dy1 - 3)], fill=hx("3e5444"))
        if fire:
            vgrad(img, (dx0 + 11, dy0, dx1, dy1), hx("ffd060"), hx("f06020"))
            ed.rectangle([dx0 + 11, dy0, dx1, dy1], fill=255)
    else:
        panel_door(d, dx0, dy0, dx1, dy1, hx("2e4a36"), frame=hx("2e4a36"), frame_w=0)
        d.rectangle([dx0 + 8, dy0 + 6, dx1 - 8, dy0 + 22], fill=hx("141c2a"))  # a little glazed light
        d.line([(dx0 + 10, dy0 + 8), (dx0 + 16, dy0 + 14)], fill=hx("4a5a7a"))
        d.line([((dx0 + dx1) // 2, dy0 + 6), ((dx0 + dx1) // 2, dy0 + 22)], fill=hx("2e4a36"))
        d.rectangle([dx0 + 13, dy1 - 30, dx1 - 13, dy1 - 27], fill=hx("b89a50"))  # letter plate
    # worn steps down to the yard, and a boot scraper
    for i in range(3):
        y = dy1 + i * 4
        x0_, x1_ = dx0 - 9 - i * 3, dx1 + 9 + i * 3
        d.rectangle([x0_, y, x1_, y + 4], fill=mix(hx("aaa292"), hx("7a7466"), i / 3))
        d.line([(x0_, y), (x1_, y)], fill=hx("cec6b4"))
        d.line([(x0_ + 4, y + 2), (x0_ + 10, y + 2)], fill=hx("8a8476"))
    d.rectangle([dx1 + 14, dy1 + 6, dx1 + 22, dy1 + 9], fill=hx("1a1a1c"))
    d.line([(dx1 + 15, dy1 + 6), (dx1 + 15, dy1 + 11)], fill=hx("1a1a1c"))
    d.line([(dx1 + 21, dy1 + 6), (dx1 + 21, dy1 + 11)], fill=hx("1a1a1c"))
    # the servants' lamp on its bracket, left of the door
    lx, ly = dx0 - 22, dy0 - 2
    d.line([(lx - 6, ly - 10), (lx, ly - 10), (lx, ly - 6)], fill=hx("1a1816"), width=2)
    d.rectangle([lx - 7, ly - 13, lx - 5, ly - 4], fill=hx("1a1816"))
    d.polygon([(lx - 5, ly - 6), (lx + 5, ly - 6), (lx + 3, ly - 8), (lx - 3, ly - 8)], fill=hx("1a1816"))
    d.polygon([(lx - 4, ly - 6), (lx + 4, ly - 6), (lx + 3, ly + 6), (lx - 3, ly + 6)], fill=hx("ffe6a0"))
    d.line([(lx, ly - 6), (lx, ly + 6)], fill=hx("2a2016"))
    d.rectangle([lx - 4, ly + 6, lx + 4, ly + 8], fill=hx("1a1816"))
    ed.polygon([(lx - 4, ly - 6), (lx + 4, ly - 6), (lx + 3, ly + 6), (lx - 3, ly + 6)], fill=255)
    # ---- the alarm: a wire stapled up the jamb, along the string course to the bell box ----
    bx0, by0, bx1, by1 = BELL
    bcx = (bx0 + bx1) // 2
    wire = [(dx1 + 8, dy0 + 30), (dx1 + 8, 96), (bcx, 96), (bcx, by1)]
    d.line(wire, fill=hx("141210"))
    for x in range(dx1 + 14, bcx, 8):
        d.point((x, 95), fill=hx("8a8478"))
    for y in range(dy0 + 4, dy0 + 30, 8):
        d.point((dx1 + 9, y), fill=hx("8a8478"))
    d.rectangle([dx1 + 7, dy0 + 29, dx1 + 10, dy0 + 32], fill=hx("3a3632"))
    # the bell: a red cast-iron box on a backplate, a big brass gong, the striker on its spring arm
    d.rectangle([bx0 + 2, by0 - 2, bx1 - 2, by0 + 12], fill=hx("4a1210"))
    d.rectangle([bx0 + 4, by0, bx1 - 4, by0 + 11], fill=hx("a82420"), outline=hx("3a0806"))
    d.line([(bx0 + 5, by0 + 1), (bx1 - 5, by0 + 1)], fill=hx("e05a48"))
    d.rectangle([bx0 + 8, by0 + 4, bx1 - 8, by0 + 7], fill=hx("6a1210"))
    d.ellipse([bx0, by0 + 9, bx1, by1], fill=hx("8a6418"), outline=hx("3a2808"))
    d.ellipse([bx0 + 2, by0 + 10, bx1 - 3, by1 - 3], fill=hx("c89a38"))
    d.ellipse([bx0 + 4, by0 + 11, bx0 + 14, by0 + 17], fill=hx("f4dc88"))
    d.ellipse([bx0 + 10, by0 + 17, bx1 - 10, by1 - 7], fill=hx("6a4a14"), outline=hx("3a2808"))
    d.point((bcx, by0 + 21), fill=hx("e8c870"))
    if wedged:
        # Micah's tie, folded between the hammer and the gong and knotted round the arm
        d.line([(bx1 - 2, by0 + 13), (bx1 + 4, by0 + 16)], fill=hx("2a2a2a"), width=2)
        d.polygon([(bx1 - 7, by0 + 11), (bx1 + 3, by0 + 12), (bx1 + 6, by1 + 9), (bx1 + 1, by1 + 12), (bx1 - 4, by0 + 20)],
                  fill=hx("8b2534"), outline=hx("3a0a10"))
        for k in range(3):
            y = by0 + 16 + k * 7
            d.line([(bx1 - 3 + k, y), (bx1 + 3 + k, y + 2)], fill=hx("c8a040"))
        d.ellipse([bx1 - 3, by0 + 10, bx1 + 3, by0 + 16], fill=hx("6a1a26"))
    else:
        d.line([(bx1 - 4, by0 + 6), (bx1 + 3, by0 + 9), (bx1 + 3, by0 + 14)], fill=hx("2a2a2a"), width=2)
        d.ellipse([bx1, by0 + 13, bx1 + 6, by0 + 19], fill=hx("4a4a4e"), outline=hx("161616"))
        d.point((bx1 + 2, by0 + 14), fill=hx("9a9aa0"))
    # ---- ivy up the corner and around the first window ----
    ivy(d, img, 76, FX - 2, FX + 24, 40, 190, 0.8)
    ivy(d, img, 77, FX + 296, FX + 318, 120, 184, 0.35)
    # ---- the yard: wet flagstones, the garden wall with its iron gate on the left ----
    flagstones(img, 207, H - 1, 240, 120, 30, hx("6a6862"), hx("524f4a"), hx("2a2826"), 73, moss=hx("2e3a26"))
    noise(img, (0, 207, W - 1, H - 1), 5, 73)
    shadow(img, "rect", [FX, 205, W, 214], 0.5, 3)
    # a puddle holding the lamp and the moon
    shadow(img, "ellipse", [186, 236, 262, 248], 0.45, 2, (40, 50, 90))
    light(img, "ellipse", [198, 239, 214, 244], hx("5a6890"), 0.5, 1)
    d = ImageDraw.Draw(img)
    for i in range(3):
        d.line([(226 - i, 239 + i * 3), (238 - i, 239 + i * 3)], fill=hx("6a5a40"))
    # garden wall, gate piers with ball finials and the gate itself
    bricks(img, (0, 140, FX - 1, 212), mul(BRICK, 0.9), MORTAR, 78, h=4, w=11)
    d.rectangle([0, 136, FX - 1, 140], fill=STONE)
    d.line([(0, 136), (FX - 1, 136)], fill=STONE_L)
    d.line([(0, 141), (FX - 1, 141)], fill=hx("3a2a22"))
    vgrad(img, (7, 118, 25, 135), hx("2a3050"), hx("3a4466"))  # a gap in the elm over the gateway
    vgrad(img, (7, 140, 25, 214), hx("56668a"), hx("4e7050"))  # the moonlit garden glimpsed through the bars
    d.ellipse([4, 154, 16, 186], fill=hx("2a422c"))
    d.ellipse([16, 164, 30, 194], fill=hx("324a34"))
    d.polygon([(7, 214), (25, 214), (20, 196), (12, 196)], fill=hx("9a9684"))
    _gate_piers(d)
    _garden_gate(d)
    # box hedge in front of the wall, a galvanised ash can by the plinth
    for i in range(10):
        x = FX + 2 + i * 4
        d.ellipse([x - 5, 192, x + 5, 214], fill=rnd.choice([hx("1a2e1a"), hx("223a1e"), hx("1e3220")]))
    for _ in range(30):
        d.point((rnd.randint(FX - 2, FX + 42), rnd.randint(194, 210)), fill=hx("3e5a32"))
    _ash_can(img, 106, 178, 130, 211)
    # ---- the coal bin: home by the coal hole, or shoved under the bell ----
    if not moved:
        coal_bin(d, BIN_HOME)
    else:
        for y in (209, 211):  # scrape marks across the flags
            d.line([(BIN_MOVED[2], y), (BIN_HOME[0] + 6, y)], fill=hx("3a3834"))
        for i in range(5):
            d.ellipse([BIN_HOME[0] + 8 + i * 8, 207, BIN_HOME[0] + 11 + i * 8, 210], fill=hx("0c0c0e"))
        coal_bin(d, BIN_MOVED)
    # ---- light: moonlight from the upper left, the lamp's warm pool by the door, the lit window ----
    pools = [(lx, ly + 10, 70, 60, (1.15, 0.92, 0.62), 1.0), (457, 60, 50, 40, (1.1, 0.88, 0.6), 0.7),
             (20, 0, 200, 150, (0.6, 0.66, 0.9), 0.5)]
    if fire:
        pools = [(240, 120, 320, 200, (1.3, 0.85, 0.55), 1.0)]
    img = grade(img, (0.42, 0.46, 0.7), pools, em)
    if fire:
        light(img, "ellipse", [-80, -60, W + 80, 220], hx("f07028"), 0.45, 30)
        _blaze(img, fire_t, (DOOR[0] + 11, DOOR[1], DOOR[2], DOOR[3]) if opened else None)
    else:
        light(img, "ellipse", [lx - 30, ly - 24, lx + 30, ly + 30], hx("f0b060"), 0.25, 10)
        light(img, "ellipse", [430, 30, 484, 100], hx("e0a050"), 0.2, 12)
    vignette(img, 0.5, (8, 8, 20), 40)
    return img


def build_exterior():
    base = paint_exterior()
    v = {"moved": paint_exterior(moved=True), "wedged": paint_exterior(wedged=True), "open": paint_exterior(opened=True),
         "fire": paint_exterior(moved=True, wedged=True, opened=True, fire=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.3)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_exterior.png")
    overlay(v["moved"], px, pal, (BIN_MOVED[0] - 4, BIN_MOVED[1] - 4, BIN_HOME[2] + 10, BIN_HOME[3] + 6),
            "mansion_exterior_bin")
    overlay(v["wedged"], px, pal, (BELL[0] - 2, BELL[1] - 2, BELL[2] + 10, BELL[3] + 16), "mansion_exterior_tie")
    overlay(v["open"], px, pal, (DOOR[0] - 2, DOOR[1] - 2, DOOR[2] + 2, DOOR[3] + 1), "mansion_exterior_door")
    fire = [v["fire"]] + [paint_exterior(moved=True, wedged=True, opened=True, fire=True, fire_t=i / EXT_FIRE_FRAMES)
                          for i in range(1, EXT_FIRE_FRAMES)]
    fpal = palette_of(Image.blend(fire[0], fire[EXT_FIRE_FRAMES // 2], 0.5), 160)
    strip = Image.new("RGB", (W * EXT_FIRE_FRAMES, H))
    for i, frame in enumerate(fire):
        strip.paste(pixelize(frame, fpal), (i * W, 0))
    save(strip, "rooms", "mansion_exterior_fire.png")
    print("mansion_exterior_fire:", EXT_FIRE_FRAMES, "frames")
    return px, v


EXT_FIRE_FRAMES = 16
FLAME_LAYERS = ((hx("a82a12"), 1.0, 1.0), (hx("e0601e"), 0.84, 0.78), (hx("f8a032"), 0.64, 0.56),
                (hx("ffd870"), 0.42, 0.36), (hx("fff6d8"), 0.2, 0.18))
LOWER_SASHES = ((70, 116, 104, 166), (156, 116, 190, 166), (384, 116, 416, 150))


def _flame(d, cx, base, h, w, t, ph, lean=0.0, flicker=1.0):
    """One tongue of flame, nested from a dark red skin to a white core: it narrows as it rises, ripples with a wave
    running up it, leans downwind at the tip and swells and sinks with phase t (looping on 1); a torn-off wisp
    drifts up from the tip and burns out. flicker scales how hard it leaps and sways."""
    tau = 2 * math.pi
    h *= 0.8 + flicker * (0.16 * math.sin(tau * (t + ph)) + 0.07 * math.sin(tau * (3 * t + 2 * ph)))
    if h < 1.5:
        return
    for col, hs, ws in FLAME_LAYERS:
        hh, ww = h * hs, w * ws + 0.6
        left, right = [], []
        n = 12
        for i in range(n + 1):
            f = i / n
            mid = cx + lean * f * f * h * 0.3 + flicker * (1 + w * 0.3) * f * math.sin(tau * (1.3 * f - 2 * t + ph))
            half = ww * (1 - f) ** 0.7 * (1 + 0.22 * math.sin(tau * (2 * f + t + ph)))
            left.append((mid - half, base - hh * f))
            right.append((mid + half, base - hh * f))
        d.polygon(left + right[::-1], fill=col)
    q = (2 * t + ph) % 1.0
    r = w * 0.45 * (1 - q)
    if r >= 0.6:
        wx = cx + lean * h * 0.3 + 2 * math.sin(tau * (q + ph)) + q * lean * 6
        wy = base - h * (0.95 + 0.45 * q)
        d.ellipse([wx - r, wy - r * 1.4, wx + r, wy + r * 1.4], fill=mix(hx("ffb040"), hx("b8381a"), q))


def _smoke(layer, sx, sy, rise, drift, size, t, n, seed):
    """A plume of smoke billowing up from (sx, sy): n puffs ride up it in turn, swelling, drifting downwind and
    thinning out, each a dark mass lit hot orange from below by the fire."""
    tau = 2 * math.pi
    rs = random.Random(seed)
    d = ImageDraw.Draw(layer)
    puffs = []
    for k in range(n):
        q = (t + k / n) % 1.0
        wob = rs.uniform(-1, 1)
        x = sx + drift * q + size * 0.8 * wob + 3 * math.sin(tau * (q * 1.5 + k * 0.37))
        y = sy - rise * q
        r = size * (0.45 + 1.1 * q) * rs.uniform(0.8, 1.15)
        a = int(235 * min(1.0, q * 6) * (1 - q) ** 0.6)
        puffs.append((y, x, r, a, q))
    for y, x, r, a, q in sorted(puffs, reverse=True):
        body = mix(hx("362824"), hx("282426"), min(1.0, q * 1.6))
        d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=body + (a,))
        d.ellipse([x - r * 0.8, y - r * 0.05, x + r * 0.6, y + r * 0.75],
                  fill=mix(hx("c8662c"), hx("5a4a46"), min(1.0, q * 1.3)) + (int(a * 0.7),))  # underlit
        d.ellipse([x - r * 0.3, y - r * 0.8, x + r * 0.8, y - r * 0.2], fill=hx("6a6264") + (int(a * 0.35),))  # moonlit


def _blaze(img, t, doorway=None):
    """The house going up, drawn last at phase t (looping on 1): smoke pouring out over the cornice and rolling
    off the roof in a bank, flames bursting out of every window (and the open kitchen door) and licking up the
    brick, and sparks spiralling up into the night."""
    tau = 2 * math.pi
    rgba = img.convert("RGBA")
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for i, x in enumerate(UPPER_X):  # a plume out of the top of each upper window
        _smoke(layer, x + 13, UPPER_Y[0] - 8, 90, 40, 8, (t + i * 0.29) % 1.0, 11, 300 + i)
    for i, (x0, y0, x1, y1) in enumerate(LOWER_SASHES):
        _smoke(layer, (x0 + x1) / 2, y0 - 10, 70, 30, 6, (t + i * 0.41) % 1.0, 9, 320 + i)
    if doorway is not None:
        _smoke(layer, (doorway[0] + doorway[2]) / 2, doorway[1] - 14, 90, 34, 8, t, 10, 330)
    dl = ImageDraw.Draw(layer)
    for k in range(20):  # the bank rolling along the roof, downwind
        x = (k * 28 + t * 28) % (20 * 28) - 40
        y = 2 + 5 * math.sin(tau * x / 140) + 2 * math.sin(tau * x / 61)
        r = 18 + 6 * math.sin(tau * x / 97)
        dl.ellipse([x - r, y - r * 0.7, x + r, y + r * 0.7], fill=hx("2e2a2c") + (200,))
        dl.ellipse([x - r * 0.8, y + r * 0.05, x + r * 0.6, y + r * 0.65], fill=hx("8a4426") + (130,))
    layer = layer.filter(ImageFilter.GaussianBlur(2.2))
    rgba.alpha_composite(layer)
    img.paste(rgba.convert("RGB"))
    for i, x in enumerate(UPPER_X):  # a glow on the brick around each window, breathing with the fire
        g = 0.32 + 0.08 * math.sin(tau * (t + i * 0.23))
        light(img, "ellipse", [x - 22, UPPER_Y[0] - 40, x + 48, UPPER_Y[1] + 14], hx("ff8a30"), g, 8)
    for x0, y0, x1, y1 in LOWER_SASHES:
        light(img, "ellipse", [x0 - 18, y0 - 26, x1 + 18, y1 + 12], hx("ff8a30"), 0.3, 8)
    d = ImageDraw.Draw(img)
    rf = random.Random(7)
    fl = 1.9  # the house fire leaps harder than a hearth
    for i, x in enumerate(UPPER_X):
        x0, y0, x1, y1 = x, UPPER_Y[0], x + 26, UPPER_Y[1]
        for j in range(5):
            cx = x0 + 3 + j * (x1 - x0 - 6) / 4 + rf.uniform(-1, 1)
            hj = (y1 - y0) * rf.uniform(0.9, 1.35) + (10 if j in (1, 2, 3) else 0)
            _flame(d, cx, y1 - 1, hj, rf.uniform(3.8, 5.2), t, rf.random(), lean=rf.uniform(0.2, 0.9), flicker=fl)
        _window_tongues(d, rf, x0, y0, x1, t, 3, 26)
    for x0, y0, x1, y1 in LOWER_SASHES:
        for j in range(5):
            cx = x0 + 3 + j * (x1 - x0 - 6) / 4 + rf.uniform(-1, 1)
            _flame(d, cx, y1 - 1, (y1 - y0) * rf.uniform(0.75, 1.15), rf.uniform(3.6, 5), t, rf.random(),
                   lean=rf.uniform(0.1, 0.6), flicker=fl)
        for bx in range(x0 + 3, x1, 5):  # the bars stand black against the flames
            d.line([(bx, y0 - 1), (bx, y1 + 1)], fill=hx("161414"))
        d.line([(x0, y0 + 4), (x1, y0 + 4)], fill=hx("161414"))
        d.line([(x0, y1 - 4), (x1, y1 - 4)], fill=hx("161414"))
    if doorway is not None:
        dx0, dy0, dx1, dy1 = doorway
        for j in range(7):
            cx = dx0 + 2 + j * (dx1 - dx0 - 4) / 6
            _flame(d, cx, dy1 - 1, (dy1 - dy0) * rf.uniform(0.3, 0.62), rf.uniform(3.4, 4.6), t, rf.random(),
                   lean=rf.uniform(0.0, 0.4), flicker=fl)
        _window_tongues(d, rf, dx0, dy0, dx1, t, 3, 22)
    for k in range(48):  # sparks, spiralling up off the windows
        q = (t * 2 + k / 48) % 1.0
        sx0 = UPPER_X[k % len(UPPER_X)] + 13
        x = sx0 + rf.uniform(-12, 12) + q * 40 + 5 * math.sin(tau * (q * 2 + k * 0.17))
        y = UPPER_Y[0] - 10 - q * 60 - rf.uniform(0, 20)
        d.point((x, y), fill=hx("fff0a0") if q < 0.3 else hx("ffb040") if q < 0.7 else hx("a8401a"))


def _window_tongues(d, rf, x0, y0, x1, t, n, reach):
    """Flames licking out over a window head and up the brick: n tongues that leap to about reach px and fall back
    to nothing in turn, so the fire visibly climbs out of the house."""
    for j in range(n):
        cx = x0 + (j + 0.5) * (x1 - x0) / n + rf.uniform(-2, 2)
        ph = rf.random()
        q = (t * 2 + ph) % 1.0  # each tongue leaps twice per loop
        h = reach * rf.uniform(0.7, 1.1) * math.sin(math.pi * q) ** 0.8
        if h >= 3:
            _flame(d, cx, y0 + 3, h, rf.uniform(3.2, 4.4), t, ph, lean=rf.uniform(0.4, 1.0), flicker=1.4)


# ------------------------------------------------------------------------------------------------ KITCHEN

KFL = 204  # where the back wall meets the floor
CANDLE = (322, 150)  # the flame, roughly; recomputed from the table in paint_kitchen
TILE, TILE_D, PLASTER = hx("d8d4c4"), hx("9a978a"), hx("c8bc9a")
COPPER, COPPER_L, COPPER_D, COPPER_HI = hx("b8683a"), hx("e09058"), hx("5a2a14"), hx("ffd0a0")


def _hanging_pan(d, cx, rail, r, handle):
    """A copper saucepan hung by its handle, base to the room: tinned rim, concentric spun rings, a rivetted iron
    handle with its hanging hole, the shine of the moon on its belly."""
    top = rail + handle
    d.line([(cx, rail - 1), (cx, rail + 2)], fill=hx("2a2420"))  # the S-hook
    d.arc([cx - 1, rail + 1, cx + 2, rail + 4], 90, 270, fill=hx("2a2420"))
    d.rectangle([cx - 1, rail + 3, cx + 1, top + 1], fill=hx("3a3430"))  # the cast iron handle
    d.line([(cx - 1, rail + 3), (cx - 1, top)], fill=hx("6a645c"))
    d.rectangle([cx - 1, rail + 4, cx, rail + 5], fill=hx("161210"))  # its hanging hole
    d.ellipse([cx - r, top, cx + r, top + 2 * r], fill=COPPER, outline=COPPER_D)
    cy = top + r
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], outline=mul(COPPER, 0.82))  # the base's spun rings
    if r > 5:
        d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4], outline=mul(COPPER, 0.9))
    d.arc([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], 200, 290, fill=COPPER_L)
    d.arc([cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1], 20, 110, fill=mul(COPPER, 0.6))
    d.point((cx - r // 2, cy - r // 2), fill=COPPER_HI)
    d.point((cx - r // 2 + 1, cy - r // 2), fill=COPPER_L)
    d.point((cx - r // 2, cy - r // 2 + 1), fill=COPPER_L)
    for sx in (-1, 1):  # the rivets holding the handle
        d.point((cx + sx * 2, top + 1), fill=hx("e0b080"))
    d.point((cx + r - 2, cy + 2), fill=mul(COPPER, 0.5))  # a dull patch where the verdigris is creeping


def _range_pan(d, p):
    """A copper stock pot on the back burner: a tinned rim, a dome lid with a brass knob, two loop handles, a seam
    band, and the warm shine of the copper."""
    x, y = int(p[0]), int(p[1])
    d.ellipse([x - 10, y - 2, x + 10, y + 3], fill=hx("0c0c0e"))  # its shadow on the hob
    d.rectangle([x - 8, y - 12, x + 8, y], fill=COPPER)
    for k in range(-8, 9):  # rounded shading across the drum
        t = (k + 8) / 16
        c = mix(COPPER_L, COPPER_D, t ** 1.3) if t > 0.15 else COPPER
        d.line([(x + k, y - 11), (x + k, y - 1)], fill=c)
    d.line([(x - 6, y - 11), (x - 6, y - 1)], fill=COPPER_HI)
    d.ellipse([x - 8, y - 2, x + 8, y + 2], fill=mul(COPPER, 0.7))
    d.arc([x - 8, y - 2, x + 8, y + 2], 0, 180, fill=COPPER_D)
    d.line([(x - 8, y - 6), (x + 8, y - 6)], fill=COPPER_D)  # the seam band
    d.line([(x - 8, y - 7), (x + 8, y - 7)], fill=mix(COPPER_L, COPPER, 0.5))
    for sx in (-1, 1):  # loop handles
        d.arc([x + sx * 9 - 2, y - 11, x + sx * 9 + 2, y - 7], 90 if sx > 0 else 270, 270 if sx > 0 else 450,
              fill=hx("3a3430"))
    d.ellipse([x - 9, y - 14, x + 9, y - 10], fill=hx("c8c4bc"), outline=COPPER_D)  # the tinned rim
    d.ellipse([x - 7, y - 17, x + 7, y - 11], fill=COPPER, outline=COPPER_D)  # the lid
    d.arc([x - 6, y - 16, x + 6, y - 12], 190, 300, fill=COPPER_HI)
    d.ellipse([x - 2, y - 20, x + 2, y - 16], fill=hx("c8a040"), outline=hx("5a4418"))
    d.point((x - 1, y - 19), fill=hx("fff0b0"))


def _plate(d, x, yb, w, h, pattern, rnd):
    """A dinner plate stood on its rim against the back of the rack: a glazed rim with a blue transfer border,
    the well in faint shade, a gilt line, and a highlight on the glaze."""
    x1, y0 = x + w, yb - h
    body = hx("ece8dc")
    d.ellipse([x, y0, x1, yb], fill=body, outline=hx("6a6656"))
    d.ellipse([x + 1, y0 + 1, x1 - 1, yb - 1], outline=pattern)  # the transfer-printed border
    for k in range(10):
        a = k * math.pi / 5 + 0.3
        px_ = (x + x1) / 2 + (w / 2 - 2) * math.cos(a)
        py_ = (y0 + yb) / 2 + (h / 2 - 2) * math.sin(a)
        d.point((round(px_), round(py_)), fill=mul(pattern, 1.2))
    d.ellipse([x + 3, y0 + 4, x1 - 3, yb - 4], fill=hx("e0dccc"), outline=hx("c8b878"))  # the well, gilt line
    if pattern != hx("b8b0a0"):  # a little willow scene in the middle
        cx, cy = (x + x1) // 2, (y0 + yb) // 2
        d.line([(cx - 2, cy + 2), (cx + 2, cy + 2)], fill=pattern)
        d.point((cx - 1, cy), fill=pattern)
        d.point((cx + 1, cy - 1), fill=pattern)
        d.point((cx, cy - 3), fill=mul(pattern, 1.2))
    d.arc([x + 1, y0 + 1, x1 - 1, yb - 1], 200, 250, fill=hx("ffffff"))  # glaze highlight
    d.arc([x + 1, y0 + 1, x1 - 1, yb - 1], 20, 80, fill=hx("a8a494"))


def _jug(d, x, yb, h, col):
    """A little lustre milk jug stood between the plates."""
    d.polygon([(x - 3, yb), (x + 3, yb), (x + 4, yb - h + 3), (x + 2, yb - h), (x - 3, yb - h)], fill=col,
              outline=mul(col, 0.5))
    d.point((x + 4, yb - h), fill=mul(col, 0.5))  # the lip
    d.arc([x - 6, yb - h + 2, x - 2, yb - 3], 90, 270, fill=mul(col, 0.5))
    d.line([(x - 2, yb - h + 2), (x - 2, yb - 2)], fill=mul(col, 1.4))


def _bell_board(img, x0, y0, x1, y1, n, rung=None):
    """The servants' bell board: a mahogany board under a moulded cornice, a row of brass bells on coiled springs
    fed by crank wires from above, each with an enamel room plate and a pendulum flag below."""
    d = ImageDraw.Draw(img)
    mah, mah_l, mah_d = hx("5a3420"), hx("8a5434"), hx("24140a")
    d.rectangle([x0, y0, x1, y1], fill=mah, outline=mah_d)
    for k in range(0, x1 - x0, 3):  # figure in the mahogany
        d.line([(x0 + 1 + k, y0 + 9), (x0 + 2 + k, y1 - 1)], fill=mul(mah, 0.92 if k % 2 else 1.06))
    d.rectangle([x0 - 2, y0 - 3, x1 + 2, y0 + 1], fill=mah_l, outline=mah_d)  # the cornice
    d.line([(x0 - 1, y0 - 2), (x1 + 1, y0 - 2)], fill=hx("b07a4e"))
    d.rectangle([x0 + 1, y0 + 2, x1 - 1, y0 + 6], fill=mul(mah, 1.1))
    for x in range(x0 + 2, x1 - 1, 3):  # dentils
        d.point((x, y0 + 4), fill=mah_d)
    d.rectangle([x0 - 1, y1 - 1, x1 + 1, y1 + 2], fill=mah_l, outline=mah_d)  # the base moulding
    d.rectangle([x0 + 2, y0 + 30, x1 - 2, y0 + 40], fill=hx("1c120a"), outline=mah_d)  # the glazed indicator box
    d.line([(x0 + 3, y0 + 31), (x1 - 3, y0 + 31)], fill=hx("3a2a1c"))
    step = (x1 - x0 - 4) // n
    for i in range(n):
        x = x0 + 4 + i * step + step // 2 - 1
        # the crank wire runs down from the ceiling to a coiled spring holding the bell
        d.line([(x, y0 - 3), (x, y0 + 8)], fill=hx("4a4a44"))
        for k in range(4):
            yy = y0 + 9 + k * 2
            d.line([(x - 1, yy), (x + 1, yy + 1)], fill=hx("8a8a80"))
        bt = y0 + 17
        d.polygon([(x - 3, bt + 7), (x - 2, bt + 2), (x, bt), (x + 2, bt + 2), (x + 3, bt + 7)], fill=hx("b89040"),
                  outline=hx("5a4418"))
        d.line([(x - 4, bt + 7), (x + 4, bt + 7)], fill=hx("6a5020"))  # the lip
        d.point((x - 1, bt + 2), fill=hx("fff0b0"))
        d.point((x - 2, bt + 4), fill=hx("f0d890"))
        d.point((x, bt + 8), fill=hx("2a2014"))  # the clapper
        # the pendulum flag behind the glass: down (red) if the room has rung
        down = i == rung
        d.line([(x, y0 + 31), (x, y0 + 34)], fill=hx("8a8a80"))
        d.rectangle([x - 1, y0 + 34, x + 1, y0 + 38], fill=hx("a02020") if down else hx("e8e0c8"))
        d.point((x - 1, y0 + 34), fill=hx("ffffff") if not down else hx("e05a48"))
        # the enamel room plate
        d.rectangle([x - 3, y0 + 43, x + 3, y0 + 48], fill=hx("ece4cc"), outline=hx("6a5420"))
        d.line([(x - 2, y0 + 45), (x + 1, y0 + 45)], fill=hx("3a3020"))
        d.point((x - 1, y0 + 47), fill=hx("3a3020"))
        d.point((x + 1, y0 + 47), fill=hx("3a3020"))
    d.line([(x0 + 3, y0 + 33), (x1 - 3, y0 + 37)], fill=hx("6a5a48"))  # a sheen on the indicator glass


def _wood_door(img, x0, y0, x1, y1, seed):
    """The door through to the house: bare tongue-and-groove oak boards, darkened by years of hands and steam,
    held on a ledge and brace with long strap hinges and a thumb latch."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    green, green_l, green_d = hx("6e4a2a"), hx("94683e"), hx("3a2414")  # oak: body, lit edge, shadow
    wood = hx("4a3020")  # dark grain and wear marks
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1], fill=hx("6a5038"))  # the architrave
    d.line([(x0 - 5, y0 - 5), (x1 + 5, y0 - 5)], fill=hx("9a7a54"))
    d.line([(x0 - 5, y0 - 5), (x0 - 5, y1)], fill=hx("8a6a48"))
    d.line([(x1 + 5, y0 - 5), (x1 + 5, y1)], fill=hx("3a2a1c"))
    d.line([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1)], fill=hx("3a2a1c"))
    d.rectangle([x0 - 7, y0 - 9, x1 + 7, y0 - 6], fill=hx("7a5c40"))  # the head moulding
    d.line([(x0 - 7, y0 - 9), (x1 + 7, y0 - 9)], fill=hx("a88660"))
    bw = 8
    for i, bx in enumerate(range(x0, x1, bw)):  # the boards, each a shade apart
        bx1 = min(x1, bx + bw - 1)
        c = mul(green, rnd.uniform(0.92, 1.08))
        d.rectangle([bx, y0, bx1, y1], fill=c)
        d.line([(bx, y0), (bx, y1)], fill=green_d)  # the groove
        d.line([(bx + 1, y0), (bx + 1, y1)], fill=mul(c, 1.18))  # the bead catching the light
        for k in range(3):  # grain under the paint
            gx = bx + 3 + k * 2 + rnd.randint(-1, 0)
            ys = rnd.randint(y0, y1 - 30)
            d.line([(gx, ys), (gx, ys + rnd.randint(12, 30))], fill=mul(c, 0.9))
        for _ in range(2):  # knots
            ky = rnd.randint(y0 + 8, y1 - 8)
            d.ellipse([bx + 3, ky - 1, bx + 5, ky + 2], outline=mul(c, 0.75))
        for _ in range(3):  # dents and old wear
            cxp, cyp = rnd.randint(bx + 1, bx1), rnd.randint(y0, y1)
            d.point((cxp, cyp), fill=wood)
    d.line([(x1, y0), (x1, y1)], fill=green_d)
    # ledges and a brace on the face, chamfered
    for ly in (y0 + 10, (y0 + y1) // 2, y1 - 14):
        d.rectangle([x0 + 1, ly, x1 - 1, ly + 5], fill=mul(green, 1.05))
        d.line([(x0 + 1, ly), (x1 - 1, ly)], fill=green_l)
        d.line([(x0 + 1, ly + 5), (x1 - 1, ly + 5)], fill=green_d)
        d.line([(x0 + 1, ly + 6), (x1 - 1, ly + 6)], fill=mul(green_d, 0.7))
        for bx in range(x0 + 4, x1 - 2, 8):  # clenched nails
            d.point((bx, ly + 2), fill=hx("1a1a1a"))
    d.polygon([(x0 + 2, y1 - 15), (x0 + 7, y1 - 15), (x1 - 2, (y0 + y1) // 2 + 6), (x1 - 7, (y0 + y1) // 2 + 6)],
              fill=mul(green, 1.02))
    d.line([(x0 + 2, y1 - 15), (x1 - 7, (y0 + y1) // 2 + 6)], fill=green_l)
    d.line([(x0 + 7, y1 - 15), (x1 - 2, (y0 + y1) // 2 + 6)], fill=green_d)
    for ly in (y0 + 10, (y0 + y1) // 2, y1 - 14):  # the paint rubbed off the ledges' edges
        for _ in range(4):
            d.point((rnd.randint(x0 + 2, x1 - 2), ly + rnd.choice((0, 5))), fill=wood)
    # long strap hinges with pintles on the left jamb
    for ly in (y0 + 12, y1 - 12):
        d.polygon([(x0 - 3, ly - 1), (x0 + 30, ly), (x0 + 33, ly + 1), (x0 + 30, ly + 2), (x0 - 3, ly + 3)],
                  fill=hx("1e1e22"))
        d.line([(x0 - 3, ly - 1), (x0 + 29, ly)], fill=hx("5a5a62"))
        d.ellipse([x0 + 30, ly - 1, x0 + 34, ly + 3], fill=hx("1e1e22"))  # the fleur end
        for nx in (x0 + 4, x0 + 14, x0 + 24):
            d.point((nx, ly + 1), fill=hx("7a7a84"))
        d.rectangle([x0 - 4, ly - 2, x0 - 2, ly + 4], fill=hx("2a2a2e"))
    # the thumb latch: a lift bar into a keeper, a cusped handle plate, a keyhole under it
    ky = y0 + 52
    d.rectangle([x1 - 16, ky, x1 + 2, ky + 1], fill=hx("1e1e22"))  # the latch bar
    d.line([(x1 - 16, ky), (x1 + 1, ky)], fill=hx("6a6a72"))
    d.rectangle([x1 + 1, ky - 2, x1 + 3, ky + 3], fill=hx("2a2a2e"))  # the keeper
    d.polygon([(x1 - 10, ky + 3), (x1 - 7, ky + 3), (x1 - 7, ky + 16), (x1 - 10, ky + 16)], fill=hx("1e1e22"))
    d.ellipse([x1 - 11, ky + 2, x1 - 6, ky + 5], fill=hx("26262a"))
    d.ellipse([x1 - 11, ky + 14, x1 - 6, ky + 17], fill=hx("26262a"))
    d.arc([x1 - 13, ky + 5, x1 - 5, ky + 15], 270, 90, fill=hx("2a2a2e"), width=2)  # the grip
    d.point((x1 - 9, ky + 4), fill=hx("7a7a84"))
    d.ellipse([x1 - 11, ky + 22, x1 - 7, ky + 26], fill=hx("26262a"))  # the escutcheon and keyhole
    d.point((x1 - 9, ky + 24), fill=hx("060606"))
    d.point((x1 - 9, ky + 25), fill=hx("060606"))
    for _ in range(14):  # the paint worn back to the wood round the latch by years of hands
        d.point((rnd.randint(x1 - 18, x1 - 3), rnd.randint(ky - 4, ky + 20)), fill=wood)
    d.rectangle([x0 + 1, y1 - 4, x1 - 1, y1 - 1], fill=mul(green_d, 0.9))  # scuffed bottom rail
    for bx in range(x0 + 2, x1, 3):
        d.point((bx, y1 - 3), fill=mix(wood, green_d, 0.5))


def _regulator_clock(d, cx, top):
    """A walnut wall regulator: carved crest, a brass-bezelled dial with hour and minute marks, and a glazed trunk
    showing the brass pendulum."""
    wal, wal_l, wal_d = hx("5a3a20"), hx("8a6038"), hx("24140a")
    # the crest: a broken pediment with a turned finial
    d.polygon([(cx - 15, top + 8), (cx - 3, top + 2), (cx - 3, top + 5), (cx - 12, top + 9)], fill=wal, outline=wal_d)
    d.polygon([(cx + 15, top + 8), (cx + 3, top + 2), (cx + 3, top + 5), (cx + 12, top + 9)], fill=wal, outline=wal_d)
    d.rectangle([cx - 1, top - 2, cx + 1, top + 6], fill=wal_l)
    d.ellipse([cx - 2, top - 4, cx + 2, top], fill=hx("c8a048"))
    d.rectangle([cx - 16, top + 9, cx + 16, top + 11], fill=wal_l, outline=wal_d)
    # the head, with the dial behind a round glazed door
    d.rectangle([cx - 14, top + 12, cx + 14, top + 40], fill=wal, outline=wal_d)
    d.line([(cx - 13, top + 13), (cx + 13, top + 13)], fill=wal_l)
    d.line([(cx - 13, top + 13), (cx - 13, top + 39)], fill=wal_l)
    for sx in (-1, 1):  # little carved corner spandrels
        d.point((cx + sx * 12, top + 15), fill=hx("c8a048"))
        d.point((cx + sx * 12, top + 37), fill=hx("c8a048"))
    dy = top + 26
    d.ellipse([cx - 12, dy - 12, cx + 12, dy + 12], fill=hx("b08a3a"), outline=wal_d)  # the brass bezel
    d.arc([cx - 11, dy - 11, cx + 11, dy + 11], 180, 300, fill=hx("f0d890"))
    d.ellipse([cx - 10, dy - 10, cx + 10, dy + 10], fill=hx("efe8d2"))
    d.ellipse([cx - 9, dy - 9, cx + 9, dy + 9], outline=hx("c8bfa4"))  # the chapter ring
    for k in range(60):
        t = k * math.pi / 30
        if k % 5 == 0:
            d.line([(cx + 8 * math.cos(t), dy + 8 * math.sin(t)), (cx + 6 * math.cos(t), dy + 6 * math.sin(t))],
                   fill=hx("1e1a14"))
        elif k % 2 == 0:
            d.point((cx + 8.6 * math.cos(t), dy + 8.6 * math.sin(t)), fill=hx("8a8270"))
    for t in (-math.pi / 2, 0, math.pi / 2, math.pi):  # bolder quarter marks
        d.point((cx + 7 * math.cos(t), dy + 7 * math.sin(t)), fill=hx("1e1a14"))
    d.point((cx - 3, dy + 4), fill=hx("4a4a50"))  # winding holes
    d.point((cx + 3, dy + 4), fill=hx("4a4a50"))
    d.line([(cx, dy), (cx + 4, dy - 2)], fill=hx("141414"), width=2)  # ten past ten, nearly
    d.line([(cx, dy), (cx - 3, dy - 7)], fill=hx("141414"))
    d.point((cx, dy), fill=hx("c8a048"))
    d.line([(cx - 8, dy - 6), (cx - 5, dy - 8)], fill=hx("ffffff"))  # glint on the glass
    # the glazed trunk and the pendulum swinging inside
    d.rectangle([cx - 10, top + 40, cx + 10, top + 58], fill=wal, outline=wal_d)
    d.rectangle([cx - 7, top + 43, cx + 7, top + 55], fill=hx("2a2016"))
    d.line([(cx - 7, top + 43), (cx + 7, top + 43)], fill=hx("1a120a"))
    d.line([(cx, top + 43), (cx + 1, top + 49)], fill=hx("b08a3a"))
    d.ellipse([cx - 3, top + 48, cx + 5, top + 54], fill=hx("c8a048"), outline=hx("6a5020"))
    d.point((cx - 1, top + 50), fill=hx("f8e8a8"))
    d.line([(cx - 6, top + 45), (cx - 6, top + 50)], fill=hx("5a5040"))  # reflection on the trunk glass
    d.polygon([(cx - 10, top + 58), (cx + 10, top + 58), (cx + 4, top + 63), (cx - 4, top + 63)], fill=wal,
              outline=wal_d)  # the drop finial
    d.ellipse([cx - 2, top + 62, cx + 2, top + 66], fill=wal_l, outline=wal_d)


def _apron(img, hx0, hy0):
    """The cook's striped ticking apron hung by its neck strap from a brass peg: a narrow square bib, a step out at
    the waist into a wide skirt with blue stripes falling in folds, ties hanging from the waist corners, a pocket with
    a red tea towel tucked in, the off-side in shadow, and old stains."""
    d = ImageDraw.Draw(img)
    cloth, cloth_l, cloth_d, cloth_dd = hx("bcb6a2"), hx("d6d0bc"), hx("8e8878"), hx("5e5a4e")
    stripe, stripe_d = hx("3e5684"), hx("2e3e60")
    by, wy, hy = hy0 + 8, hy0 + 22, hy0 + 52  # bib top, waist, hem
    shadow(img, "polygon", [(hx0 - 4, by + 1), (hx0 + 7, by + 1), (hx0 + 11, hy + 2), (hx0 - 8, hy + 2)], 0.45, 2)
    d = ImageDraw.Draw(img)
    # the brass peg and the neck strap over it
    d.rectangle([hx0 - 2, hy0 - 1, hx0 + 2, hy0 + 1], fill=hx("6a5028"))
    d.point((hx0 - 1, hy0 - 1), fill=hx("c8a050"))
    d.line([(hx0 - 1, hy0 + 1), (hx0 - 4, by)], fill=cloth_d, width=2)
    d.line([(hx0 + 1, hy0 + 1), (hx0 + 4, by)], fill=cloth_dd, width=2)
    # the bib: a square of ticking, narrower than the skirt
    d.rectangle([hx0 - 5, by, hx0 + 5, wy], fill=cloth)
    for sx in (-3, 0, 3):
        d.line([(hx0 + sx, by + 1), (hx0 + sx, wy - 1)], fill=stripe)
    d.line([(hx0 - 5, by), (hx0 - 5, wy)], fill=cloth_l)
    d.line([(hx0 + 5, by), (hx0 + 5, wy)], fill=cloth_dd)
    d.line([(hx0 - 5, by), (hx0 + 5, by)], fill=cloth_dd)
    # the skirt: steps out wide at the waist, hangs a touch wider at the hem
    d.polygon([(hx0 - 9, wy + 1), (hx0 + 9, wy + 1), (hx0 + 11, hy), (hx0 - 10, hy)], fill=cloth)
    for i, sx in enumerate((-7, -4, -1, 2, 5, 8)):
        d.line([(hx0 + sx, wy + 3), (hx0 + sx * 1.15, hy - 1)], fill=stripe if i % 2 else stripe_d)
    for sx in (-7.5, -1.5, 4.5):  # fold shadows
        d.line([(hx0 + sx, wy + 8), (hx0 + sx * 1.15, hy - 1)], fill=cloth_d)
    d.polygon([(hx0 + 6, wy + 1), (hx0 + 9, wy + 1), (hx0 + 11, hy), (hx0 + 8, hy)], fill=mul(cloth, 0.7))
    d.line([(hx0 + 8, wy + 1), (hx0 + 9, hy)], fill=mul(stripe, 0.7))
    d.line([(hx0 - 9, wy + 1), (hx0 - 10, hy)], fill=cloth_l)
    d.line([(hx0 + 9, wy + 1), (hx0 + 11, hy)], fill=cloth_dd)
    # the waistband, then the ties dropping from its corners
    d.rectangle([hx0 - 9, wy, hx0 + 9, wy + 2], fill=cloth_d)
    d.line([(hx0 - 10, wy + 1), (hx0 + 10, wy + 1)], fill=cloth_l)
    d.line([(hx0 - 10, wy + 1), (hx0 - 11, wy + 4), (hx0 - 11, wy + 18)], fill=cloth_d)
    d.line([(hx0 - 10, wy + 3), (hx0 - 12, wy + 16)], fill=cloth)
    d.line([(hx0 + 12, wy + 1), (hx0 + 11, wy + 4), (hx0 + 12, wy + 15)], fill=cloth_dd)
    # a frilled hem
    d.line([(hx0 - 10, hy), (hx0 + 11, hy)], fill=cloth_dd)
    for fx in range(-10, 12, 2):
        d.point((hx0 + fx, hy + 1), fill=cloth_l)
        d.point((hx0 + fx + 1, hy + 1), fill=cloth_d)
    # the pocket with a red-checked tea towel stuffed into it
    d.rectangle([hx0 - 7, wy + 8, hx0 + 1, wy + 16], fill=cloth_l, outline=cloth_dd)
    d.line([(hx0 - 6, wy + 9), (hx0, wy + 9)], fill=cloth_d)
    d.polygon([(hx0 - 5, wy + 8), (hx0 - 1, wy + 8), (hx0, wy + 3), (hx0 - 4, wy + 4)], fill=hx("9a2a26"))
    d.point((hx0 - 3, wy + 5), fill=hx("e0d0b8"))
    d.point((hx0 - 1, wy + 7), fill=hx("e0d0b8"))
    for sx, sy in ((5, 22), (-8, 26), (2, -6), (-2, 24)):  # gravy and old tea
        d.point((hx0 + sx, wy + sy), fill=hx("6a5a3a"))
        d.point((hx0 + sx + 1, wy + sy), fill=hx("7a6a4a"))

def _broom(img, x0, y0, xh, floor):
    """A corn broom leaning in a corner: turned handle, the stitched shoulder, and a flared head of straw."""
    d = ImageDraw.Draw(img)
    hy = floor - 26  # where the handle enters the head
    d.line([(x0, y0), (xh, hy)], fill=hx("6a4a26"), width=2)
    d.line([(x0, y0), (xh - 1, hy)], fill=hx("b08a5a"))
    d.ellipse([x0 - 1, y0 - 3, x0 + 2, y0], fill=hx("4a3018"))  # the hanging hole's knob
    d.point((x0 + 1, y0 + 4), fill=hx("2a1a0c"))
    shadow(img, "ellipse", [xh - 12, floor - 3, xh + 16, floor + 3], 0.5, 2)
    d = ImageDraw.Draw(img)
    straws = [hx("c8a860"), hx("a8884a"), hx("d8bc78"), hx("8a6e38"), hx("b89a58")]
    rnd = random.Random(91)
    for k in range(26):  # the head flares from the stitching to the floor
        u = k / 25
        top_x = xh - 4 + u * 8
        bot_x = xh - 9 + u * 20 + rnd.uniform(-1, 1)
        d.line([(top_x, hy + 8), (bot_x, floor - rnd.randint(0, 1))], fill=straws[rnd.randrange(len(straws))])
    d.line([(xh - 9, floor), (xh + 11, floor)], fill=hx("6a5228"))  # the worn, splayed tips
    d.polygon([(xh - 4, hy), (xh + 4, hy), (xh + 5, hy + 9), (xh - 5, hy + 9)], fill=hx("b89a58"),
              outline=hx("6a5228"))  # the bound shoulder
    for k, c in enumerate((hx("a83a2a"), hx("2a5a3a"), hx("a83a2a"))):  # the stitching bands
        y = hy + 2 + k * 3
        d.line([(xh - 4, y), (xh + 4, y)], fill=c)
        for sx in range(int(xh) - 3, int(xh) + 4, 2):
            d.point((sx, y), fill=mul(c, 1.4))


def paint_kitchen(lit=False, gas=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    em = Image.new("L", img.size, 0)
    ed = ImageDraw.Draw(em)
    rnd = random.Random(81)
    R = Room3D(KFL, 240, 100)
    # ---- ceiling, plaster, the tiled dado ----
    vgrad(img, (0, 0, W - 1, 18), hx("3a3428"), hx("5a5040"))
    d.rectangle([0, 12, W - 1, 18], fill=hx("a89c80"))
    d.line([(0, 12), (W - 1, 12)], fill=hx("d0c4a4"))
    d.line([(0, 18), (W - 1, 18)], fill=hx("5a5040"))
    for x in range(2, W, 6):
        d.point((x, 15), fill=hx("6a604c"))
    vgrad(img, (0, 19, W - 1, 100), mul(PLASTER, 0.86), PLASTER)
    noise(img, (0, 19, W - 1, 100), 5, 82)
    for _ in range(14):  # damp stains and a crack in the plaster
        x, y = rnd.randint(0, W - 1), rnd.randint(22, 96)
        shadow(img, "ellipse", [x - 8, y - 4, x + 8, y + 6], 0.12, 3, (60, 50, 20))
    d = ImageDraw.Draw(img)
    d.line([(96, 22), (100, 34), (98, 46), (103, 58)], fill=hx("8a8068"))
    # a walnut regulator clock over the back door, and a calendar by the dresser
    _regulator_clock(d, 48, 22)
    d.rectangle([243, 112, 257, 132], fill=hx("ece4cc"), outline=hx("8a8068"))
    d.rectangle([244, 113, 256, 120], fill=hx("a83a2a"))
    for y in range(123, 131, 2):
        d.line([(245, y), (255, y)], fill=hx("8a8676"))
    # an enamel pendant lamp hanging over the table
    d.line([(326, 0), (326, 30)], fill=hx("2a2a2a"))
    d.polygon([(316, 40), (336, 40), (330, 30), (322, 30)], fill=hx("2e4a3a"))
    d.line([(316, 40), (336, 40)], fill=hx("e8e4d8"))
    d.ellipse([323, 39, 329, 43], fill=hx("d8d4c4"))
    d.rectangle([0, 100, W - 1, 105], fill=hx("3e6a54"))
    d.line([(0, 100), (W - 1, 100)], fill=hx("6a9a80"))
    d.line([(0, 105), (W - 1, 105)], fill=hx("223a2e"))
    for y in range(106, KFL - 6, 5):  # white glazed subway tiles, staggered
        off = 5 if (y // 5) % 2 else 0
        d.line([(0, y), (W - 1, y)], fill=TILE_D)
        for x in range(-off, W, 10):
            d.rectangle([x + 1, y + 1, x + 9, y + 4], fill=TILE)
            d.point((x + 2, y + 1), fill=hx("f4f2ea"))
            d.line([(x, y + 1), (x, y + 4)], fill=TILE_D)
    d.rectangle([0, KFL - 6, W - 1, KFL], fill=hx("2a3a30"))
    d.line([(0, KFL - 6), (W - 1, KFL - 6)], fill=hx("5a7a68"))
    # ---- the back door to the yard: solid oak, six raised panels, a bolt, the cook's apron on a hook ----
    bx0, bx1, by0 = 24, 72, 98
    d.rectangle([bx0 - 4, by0 - 4, bx1 + 4, KFL], fill=hx("5a4a36"))
    d.line([(bx0 - 4, by0 - 4), (bx1 + 4, by0 - 4)], fill=hx("8a7656"))
    d.line([(bx1 + 4, by0 - 4), (bx1 + 4, KFL)], fill=hx("3a2e20"))
    d.rectangle([bx0 - 6, by0 - 8, bx1 + 6, by0 - 5], fill=hx("6a5840"))  # the lintel's cornice
    d.line([(bx0 - 6, by0 - 8), (bx1 + 6, by0 - 8)], fill=hx("9a8662"))
    d.rectangle([bx0, by0, bx1, KFL], fill=hx("4a3a28"))
    grain = random.Random(811)
    for k in range(9):  # the oak's grain running down the stiles and rails
        gx = bx0 + 3 + k * 5 + grain.randint(-1, 1)
        d.line([(gx, by0 + 1), (gx + grain.randint(-1, 1), KFL - 1)], fill=hx("42331f"))
    d.line([(bx0, by0), (bx0, KFL)], fill=hx("2a2014"))
    d.line([(bx0 + 1, by0), (bx1, by0)], fill=hx("5e4a32"))
    mid = (bx0 + bx1) // 2
    for a, b in ((by0 + 6, by0 + 30), (by0 + 36, by0 + 70), (by0 + 76, KFL - 8)):
        for px0, px1 in ((bx0 + 5, mid - 2), (mid + 2, bx1 - 5)):
            d.rectangle([px0, a, px1, b], fill=hx("3a2c1c"))  # the sunk moulding round the panel
            d.rectangle([px0 + 2, a + 2, px1 - 2, b - 2], fill=hx("4e3c28"))  # the raised field
            d.line([(px0 + 2, a + 2), (px1 - 2, a + 2)], fill=hx("6e5638"))
            d.line([(px0 + 2, a + 2), (px0 + 2, b - 2)], fill=hx("644e32"))
            d.line([(px1 - 2, a + 3), (px1 - 2, b - 2)], fill=hx("33261a"))
            d.line([(px0 + 3, b - 2), (px1 - 2, b - 2)], fill=hx("2e2216"))
            d.line([(px0, b), (px1, b)], fill=hx("6a5638"))
    d.rectangle([bx1 - 8, by0 + 70, bx1 - 4, by0 + 76], fill=hx("8a6a2a"))  # brass escutcheon and knob
    d.ellipse([bx1 - 9, by0 + 64, bx1 - 3, by0 + 70], fill=hx("c8a048"), outline=hx("5a4418"))
    d.point((bx1 - 7, by0 + 65), fill=hx("f0d890"))
    d.point((bx1 - 6, by0 + 74), fill=hx("1a1208"))
    for hy in (by0 + 10, KFL - 16):  # strap hinges
        d.rectangle([bx0 + 1, hy, bx0 + 9, hy + 2], fill=hx("2a2a2e"))
        d.point((bx0 + 7, hy + 1), fill=hx("6a6a70"))
    d.rectangle([bx0 + 2, by0 + 34, bx0 + 12, by0 + 36], fill=hx("6a6a70"))  # bolt
    d.rectangle([bx0 + 10, by0 + 33, bx0 + 12, by0 + 37], fill=hx("4a4a50"))
    d.line([(bx0 + 1, KFL - 1), (bx1 - 1, KFL - 1)], fill=hx("6a7aa8"))  # moonlight under the door
    ed.line([(bx0 + 1, KFL - 1), (bx1 - 1, KFL - 1)], fill=150)
    _apron(img, 87, 116)
    d = ImageDraw.Draw(img)
    # a corn broom propped in the corner of the frame
    _broom(img, 97, 112, 102, KFL)
    d = ImageDraw.Draw(img)
    # ---- the range in its chimney recess: a brick arch, a mantel shelf with tins, the black iron range ----
    rx0, rx1 = 112, 236
    bricks(img, (rx0, 40, rx1, KFL), hx("6a3a2a"), hx("3a2620"), 83, h=4, w=9)
    d.rectangle([rx0 - 6, 30, rx0, KFL], fill=hx("8a7c64"))
    d.rectangle([rx1, 30, rx1 + 6, KFL], fill=hx("6a604c"))
    d.rectangle([rx0 - 10, 26, rx1 + 10, 36], fill=hx("9a8c70"))
    d.line([(rx0 - 10, 36), (rx1 + 10, 36)], fill=hx("4a4030"))
    d.line([(rx0 - 10, 26), (rx1 + 10, 26)], fill=hx("c8b894"))
    shadow(img, "rect", [rx0, 36, rx1, 70], 0.7, 8)
    d = ImageDraw.Draw(img)
    # the hood
    d.polygon([(rx0 + 8, 72), (rx1 - 8, 72), (rx1 - 20, 46), (rx0 + 20, 46)], fill=hx("2e2e32"))
    d.line([(rx0 + 8, 72), (rx1 - 8, 72)], fill=hx("6a6a70"))
    d.rectangle([rx0 + 6, 72, rx1 - 6, 76], fill=hx("3a3a3e"))
    for i, x in enumerate(range(rx0 + 12, rx1 - 12, 14)):  # tins and a salt crock on the hood shelf
        c = [hx("8a2a20"), hx("2a4a6a"), hx("c8a040"), hx("d8d0c0"), hx("3a5a3a")][i % 5]
        hgt = 8 + (i * 3) % 6
        d.rectangle([x, 72 - hgt, x + 7, 71], fill=c)
        d.line([(x, 72 - hgt), (x + 7, 72 - hgt)], fill=mul(c, 1.3))
        d.line([(x + 7, 72 - hgt), (x + 7, 71)], fill=mul(c, 0.6))
    d.line([(rx0 + 30, 76), (rx0 + 30, 96)], fill=hx("2a2a2c"))  # flue pipe stays
    # utensils hanging from a rail under the hood
    d.line([(rx0 + 8, 82), (rx1 - 8, 82)], fill=hx("5a5a60"))
    for i, x in enumerate(range(rx0 + 16, rx1 - 10, 12)):
        d.line([(x, 82), (x, 96 + (i % 3) * 3)], fill=hx("8a8a90"))
        if i % 2:
            d.ellipse([x - 2, 95 + (i % 3) * 3, x + 2, 100 + (i % 3) * 3], fill=hx("8a8a90"))
        else:
            d.rectangle([x - 1, 94 + (i % 3) * 3, x + 1, 98 + (i % 3) * 3], fill=hx("6a5a40"))
    # the range body, drawn in perspective so it stands out of the recess
    R.box(img, rx0 + 6, rx1 - 6, 0, 74, 0, 24, hx("1e1e22"), top=hx("34343a"), side=hx("141416"))
    a, b = R.P(rx0 + 6, 74, 24), R.P(rx1 - 6, 74, 24)
    fx0, fx1, fy0 = int(a[0]), int(b[0]), int(a[1])
    fy1 = int(R.P(0, 0, 24)[1])
    d = ImageDraw.Draw(img)
    d.line([(fx0, fy0), (fx1, fy0)], fill=hx("8a8a90"))  # nickel rail
    d.rectangle([fx0, fy0 + 1, fx1, fy0 + 3], fill=hx("6a6a70"))
    # burners on the hob
    for cx in (rx0 + 26, rx0 + 56, rx0 + 86):
        p = R.P(cx, 74, 12)
        d.ellipse([p[0] - 9, p[1] - 3, p[0] + 9, p[1] + 2], fill=hx("161618"), outline=hx("4a4a50"))
        d.ellipse([p[0] - 4, p[1] - 1, p[0] + 4, p[1] + 1], fill=hx("2a2a2e"))
    _range_pan(d, R.P(rx0 + 86, 74, 12))  # a copper stock pot on the back burner
    # the brass gas taps along the front rail
    TAPS = []
    for i in range(7):
        tx = fx0 + 8 + i * (fx1 - fx0 - 16) // 6
        TAPS.append(tx)
        on = gas and i < 5
        d.ellipse([tx - 3, fy0 + 4, tx + 3, fy0 + 10], fill=hx("c8a040"), outline=hx("5a4418"))
        d.point((tx - 1, fy0 + 5), fill=hx("fff0b0"))
        if on:  # handle turned across: the gas is on
            d.line([(tx - 5, fy0 + 7), (tx + 5, fy0 + 7)], fill=hx("1a1a1a"), width=2)
        else:
            d.line([(tx, fy0 + 3), (tx, fy0 + 11)], fill=hx("1a1a1a"), width=2)
    # two oven doors and a warming drawer, nickel handles and trim
    ow = (fx1 - fx0 - 18) // 2
    for k in range(2):
        ox0 = fx0 + 6 + k * (ow + 6)
        d.rectangle([ox0, fy0 + 16, ox0 + ow, fy0 + 52], fill=hx("26262a"), outline=hx("6a6a70"))
        d.rectangle([ox0 + 4, fy0 + 20, ox0 + ow - 4, fy0 + 48], outline=hx("3a3a40"))
        d.rectangle([ox0 + 8, fy0 + 24, ox0 + ow - 8, fy0 + 30], fill=hx("2e2e34"))
        d.line([(ox0 + 10, fy0 + 18), (ox0 + ow - 10, fy0 + 18)], fill=hx("b8b8c0"), width=2)
        d.ellipse([ox0 + ow // 2 - 4, fy0 + 36, ox0 + ow // 2 + 4, fy0 + 44], fill=hx("4a4a50"), outline=hx("8a8a90"))
    d.rectangle([fx0 + 6, fy0 + 56, fx1 - 6, fy1 - 6], fill=hx("222226"), outline=hx("5a5a60"))
    d.line([(fx0 + 30, fy0 + 60), (fx1 - 30, fy0 + 60)], fill=hx("b8b8c0"), width=2)
    for x in (fx0 + 2, fx1 - 4):
        d.rectangle([x, fy1 - 4, x + 2, fy1], fill=hx("0e0e10"))
    # ---- copper pans on the wall between range and dresser ----
    d.rectangle([243, 57, 262, 58], fill=hx("4a3a28"))  # an iron rail on two brackets
    d.line([(243, 57), (262, 57)], fill=hx("7a6a50"))
    for bx in (244, 261):
        d.rectangle([bx, 55, bx + 1, 60], fill=hx("2a2420"))
    _hanging_pan(d, 249, 58, 7, 8)
    _hanging_pan(d, 258, 58, 4, 5)
    # ---- the Welsh dresser: plate rack, cornice, cupboards ----
    dx0, dx1 = 264, 392
    R.box(img, dx0, dx1, 0, 42, 0, 22, hx("6a4a2a"), top=hx("8a6a44"), side=hx("4a321c"))
    # upper rack against the wall
    d = ImageDraw.Draw(img)
    d.rectangle([dx0 + 4, 64, dx1 - 4, KFL - 42], fill=hx("4a3220"))
    d.rectangle([dx0 + 8, 70, dx1 - 8, KFL - 44], fill=hx("2a1c10"))
    d.rectangle([dx0, 56, dx1, 64], fill=hx("7a5634"))
    d.line([(dx0, 56), (dx1, 56)], fill=hx("a8804e"))
    d.line([(dx0, 64), (dx1, 64)], fill=hx("3a2614"))
    for x in range(dx0 + 2, dx1, 6):  # carved frieze
        d.point((x, 60), fill=hx("3a2614"))
    for y in (100, 132):
        d.rectangle([dx0 + 8, y, dx1 - 8, y + 2], fill=hx("6a4a2a"))
    prnd = random.Random(87)
    for row, (ya, yb) in enumerate(((70, 100), (102, 132))):  # plates standing on the shelves, cups on hooks
        d.line([(dx0 + 8, yb - 1), (dx1 - 8, yb - 1)], fill=hx("3a2614"))  # the groove the plates stand in
        for i, x in enumerate(range(dx0 + 12, dx1 - 14, 13)):
            if (i, row) == (4, 0):  # a lustre jug in the gap of a plate taken down
                _jug(d, x + 6, yb - 2, 10, hx("b88a4a"))
                continue
            pattern = (hx("3a5a9a"), hx("b8b0a0"), hx("4a6aa8"))[(i + row) % 3]
            _plate(d, x, yb - 1, 11, 21, pattern, prnd)
        d.rectangle([dx0 + 8, yb - 9, dx1 - 8, yb - 8], fill=hx("6a4a2a"))  # the plate rail across the front
        d.line([(dx0 + 8, yb - 9), (dx1 - 8, yb - 9)], fill=hx("a07a4c"))
        for x in range(dx0 + 10, dx1 - 8, 26):
            d.rectangle([x, yb - 9, x + 1, yb - 1], fill=hx("4a321c"))  # its turned spindles
    for i, x in enumerate(range(dx0 + 14, dx1 - 12, 11)):
        d.line([(x, 134), (x, 136)], fill=hx("8a7a5a"))  # brass cup hooks
        d.point((x, 134), fill=hx("d8b458"))
        d.polygon([(x - 3, 137), (x + 3, 137), (x + 2, 142), (x - 2, 142)], fill=hx("e8e4d8"), outline=hx("8a8676"))
        d.line([(x - 2, 138), (x + 2, 138)], fill=hx("3a5a9a") if i % 2 else hx("8a3a30"))  # a band round the cup
        d.point((x - 2, 139), fill=hx("ffffff"))
        d.arc([x + 2, 138, x + 6, 141], 270, 90, fill=hx("8a8676"))
    # cupboard doors on the base
    a, b = R.P(dx0, 42, 22), R.P(dx1, 0, 22)
    ax0, ay0, ax1, ay1 = int(a[0]), int(a[1]), int(b[0]), int(b[1])
    d.line([(ax0, ay0), (ax1, ay0)], fill=hx("b8925c"))
    cw = (ax1 - ax0 - 12) // 3
    for k in range(3):
        cx0 = ax0 + 4 + k * (cw + 2)
        d.rectangle([cx0, ay0 + 4, cx0 + cw, ay1 - 4], outline=hx("3a2614"))
        d.rectangle([cx0 + 3, ay0 + 7, cx0 + cw - 3, ay1 - 7], fill=hx("5e4024"))
        d.ellipse([cx0 + cw // 2 - 1, ay0 + 9, cx0 + cw // 2 + 1, ay0 + 11], fill=hx("c8a048"))
    # ---- the baize door into the house, with the servants' bell board above ----
    gx0, gx1, gy0 = 410, 458, 98
    _wood_door(img, gx0, gy0, gx1, KFL, 84)
    _bell_board(img, 396, 24, 472, 76, 8, rung=5)  # one flag still down
    d = ImageDraw.Draw(img)
    # ---- floor: big worn flagstones and a rag rug before the range ----
    flagstones(img, KFL, H - 1, 240, 100, 34, hx("7a7466"), hx("5e5a50"), hx("38342e"), 85)
    noise(img, (0, KFL, W - 1, H - 1), 5, 85)
    shadow(img, "rect", [0, KFL, W, KFL + 6], 0.4, 3)
    rug(R, img, rx0 + 4, rx1 - 4, 30, 62, hx("6a3a2a"), hx("3a2a3a"), hx("a8885a"), seed=86)
    # ---- the deal table with a candlestick and a box of matches ----
    tx0, tx1, tz0, tz1, th = 280, 372, 26, 52, 32
    R.box(img, tx0, tx1, th - 3, th, tz0, tz1, hx("b0905e"), top=hx("c8a874"), side=hx("8a6a40"))
    for lx, lz in ((tx0 + 3, tz1 - 3), (tx1 - 6, tz1 - 3), (tx0 + 3, tz0 + 3), (tx1 - 6, tz0 + 3)):
        R.box(img, lx, lx + 3, 0, th - 3, lz - 3, lz, hx("8a6a40"), side=hx("6a4e2c"))
    R.box(img, tx0 + 2, tx1 - 2, th - 9, th - 3, tz1 - 4, tz1 - 2, hx("8a6a40"))  # apron rail
    d = ImageDraw.Draw(img)
    for x in range(tx0 + 8, tx1 - 4, 10):  # scrubbed grain
        a, b = R.P(x, th, tz0 + 2), R.P(x + 2, th, tz1 - 2)
        d.line([a, b], fill=hx("b89a68"))
    base = R.P(330, th, 40)
    cx, cy = int(base[0]), int(base[1])
    d.ellipse([cx - 5, cy - 2, cx + 5, cy + 2], fill=hx("a8842e"), outline=hx("5a4418"))
    d.rectangle([cx - 1, cy - 12, cx + 1, cy - 2], fill=hx("c8a040"))
    d.rectangle([cx - 3, cy - 13, cx + 3, cy - 11], fill=hx("d8b450"))
    d.rectangle([cx - 1, cy - 22, cx + 1, cy - 13], fill=hx("f0ead8"))
    d.line([(cx, cy - 24), (cx, cy - 23)], fill=hx("1a1a1a"))
    flame = (cx, cy - 27)
    mb = R.P(346, th, 36)  # the matchbox
    d.rectangle([mb[0], mb[1] - 3, mb[0] + 10, mb[1]], fill=hx("c84030"), outline=hx("5a1a10"))
    d.line([(mb[0] + 1, mb[1] - 2), (mb[0] + 9, mb[1] - 2)], fill=hx("f0d050"))
    p = R.P(298, th, 34)  # a bread board and a knife
    d.ellipse([p[0] - 8, p[1] - 3, p[0] + 8, p[1] + 2], fill=hx("9a7444"), outline=hx("5a4020"))
    d.line([(p[0] - 4, p[1]), (p[0] + 6, p[1] - 1)], fill=hx("c8c8d0"))
    # a ladder-back chair pulled out
    R.box(img, 352, 366, 16, 18, 56, 68, hx("6a4a2a"), top=hx("8a6a44"))
    for lx, lz in ((352, 68), (364, 68), (352, 56), (364, 56)):
        R.line(img, (lx, 0, lz), (lx, 16, lz), hx("4a321c"))
    for y in (24, 30, 36):
        R.line(img, (352, y, 56), (366, y, 56), hx("6a4a2a"))
    R.line(img, (352, 16, 56), (352, 40, 56), hx("4a321c"))
    R.line(img, (366, 16, 56), (366, 40, 56), hx("4a321c"))
    # ---- light: a sliver of moonlight under the back door, the candle if it's lit ----
    light(img, "polygon", [(bx0, KFL - 2), (bx1, KFL - 2), (bx1 + 30, H), (bx0 - 20, H)], hx("5a6aa8"), 0.18, 8)
    fxx, fyy = flame
    pools = [(48, 214, 56, 40, (0.62, 0.7, 1.0), 0.45)]
    if lit:
        pools.append((fxx, fyy + 20, 120, 90, (1.3, 0.98, 0.64), 1.0))
    img = grade(img, (0.36, 0.4, 0.62), pools, em)
    d = ImageDraw.Draw(img)
    if lit:
        light(img, "ellipse", [fxx - 30, fyy - 26, fxx + 30, fyy + 26], hx("f0b060"), 0.35, 10)
        d = ImageDraw.Draw(img)
        d.ellipse([fxx - 2, fyy - 3, fxx + 2, fyy + 3], fill=hx("ffe090"))
        d.line([(fxx, fyy - 4), (fxx, fyy + 1)], fill=hx("fffce0"))
    vignette(img, 0.5, (6, 6, 16), 40)
    paint_kitchen.flame = flame
    paint_kitchen.taps = (TAPS[0] - 6, fy0 + 1, TAPS[-1] + 6, fy0 + 13)
    return img


def build_kitchen():
    base = paint_kitchen()
    # the candle-lit and gas-on variants are no longer used in the game; they only seed the committed palette
    v = {"lit": paint_kitchen(lit=True), "gas": paint_kitchen(gas=True)}
    pal = palette_of(Image.blend(Image.blend(base, v["lit"], 0.4), v["gas"], 0.3), 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_kitchen.png")
    fx, fy = paint_kitchen.flame
    print("kitchen flame", paint_kitchen.flame, "taps", paint_kitchen.taps)
    return px, v


# ------------------------------------------------------------------------------------------------ STUDY

SFL = 204
OAK, OAK_D, OAK_L = hx("5a3a20"), hx("2e1c0e"), hx("7a5432")


def _shelf_bust(d, x, base):
    """A small marble bust on a square socle: shoulders draped, neck, head with hair and a nose, lit from the left."""
    m, ml, md, mdd = hx("b8b0a0"), hx("e0dacb"), hx("847c6c"), hx("4a4438")
    d.rectangle([x + 3, base - 3, x + 10, base - 1], fill=md, outline=mdd)  # the socle
    d.line([(x + 4, base - 3), (x + 9, base - 3)], fill=m)
    d.rectangle([x + 5, base - 5, x + 8, base - 4], fill=md)
    d.polygon([(x + 1, base - 6), (x + 12, base - 6), (x + 11, base - 9), (x + 8, base - 11), (x + 5, base - 11),
               (x + 2, base - 9)], fill=m, outline=mdd)  # draped shoulders
    d.line([(x + 4, base - 9), (x + 7, base - 7)], fill=md)  # a fold of the drape
    d.line([(x + 2, base - 8), (x + 3, base - 7)], fill=ml)
    d.rectangle([x + 6, base - 13, x + 8, base - 11], fill=m)  # neck
    d.point((x + 8, base - 12), fill=md)
    d.ellipse([x + 4, base - 19, x + 10, base - 12], fill=m, outline=mdd)  # head
    d.arc([x + 4, base - 20, x + 10, base - 15], 180, 360, fill=md)  # hair
    d.point((x + 5, base - 17), fill=ml)
    d.point((x + 5, base - 16), fill=ml)
    d.point((x + 10, base - 16), fill=m)  # the nose in profile
    d.point((x + 8, base - 16), fill=mdd)  # an eye socket
    d.point((x + 9, base - 13), fill=md)


def _shelf_globe(d, x, base):
    """A library globe: turned wooden foot, brass meridian ring, blue oceans with two continents."""
    d.rectangle([x + 3, base - 2, x + 11, base - 1], fill=hx("4a2a12"))
    d.line([(x + 3, base - 2), (x + 11, base - 2)], fill=hx("8a6440"))
    d.rectangle([x + 6, base - 5, x + 8, base - 3], fill=hx("6a4426"))
    d.ellipse([x + 2, base - 17, x + 12, base - 6], fill=hx("3a5a7a"), outline=hx("1a2a3a"))
    d.polygon([(x + 4, base - 14), (x + 7, base - 15), (x + 8, base - 12), (x + 6, base - 10), (x + 4, base - 11)],
              fill=hx("8a9a5a"))  # the Americas
    d.polygon([(x + 9, base - 15), (x + 11, base - 13), (x + 10, base - 9), (x + 9, base - 11)], fill=hx("a89a5a"))
    d.line([(x + 3, base - 11), (x + 11, base - 11)], fill=hx("5a7a9a"))  # the equator
    d.arc([x + 1, base - 18, x + 13, base - 5], 200, 340, fill=hx("c8a048"))  # the brass meridian
    d.line([(x + 1, base - 12), (x + 1, base - 9)], fill=hx("c8a048"))
    d.line([(x + 13, base - 12), (x + 13, base - 9)], fill=hx("8a6a2a"))
    d.point((x + 7, base - 18), fill=hx("e0c078"))
    d.point((x + 4, base - 15), fill=hx("c0d8e8"))  # glint


def _shelf_vase(d, x, base):
    """A blue-and-white ginger jar with a domed lid and a knop."""
    w, b, bd = hx("d8d4c8"), hx("3a5aa0"), hx("5a5850")
    d.ellipse([x + 1, base - 13, x + 11, base - 1], fill=w, outline=bd)
    d.rectangle([x + 3, base - 2, x + 9, base - 1], fill=bd)  # the foot ring
    d.rectangle([x + 3, base - 15, x + 9, base - 13], fill=w, outline=bd)  # the lid
    d.arc([x + 3, base - 17, x + 9, base - 13], 180, 360, fill=bd)
    d.point((x + 6, base - 18), fill=b)  # its knop
    d.line([(x + 3, base - 10), (x + 9, base - 10)], fill=b)  # painted bands
    d.line([(x + 3, base - 4), (x + 9, base - 4)], fill=b)
    for k, (dx, dy) in enumerate(((4, -8), (6, -7), (8, -8), (5, -6), (7, -6))):  # a prunus spray between them
        d.point((x + dx, base + dy), fill=b if k % 2 == 0 else hx("6a8ac8"))
    d.point((x + 3, base - 8), fill=hx("ffffff"))
    d.point((x + 3, base - 7), fill=hx("f0f0f0"))


def _shelf_bookends(d, x, base):
    """Two brass bookends (a block with a ball finial) holding four books laid on their sides between them."""
    br, brl, brd = hx("a8842e"), hx("e0c078"), hx("4a3414")
    for bx in (x, x + 17):
        d.rectangle([bx, base - 11, bx + 3, base - 1], fill=br, outline=brd)
        d.line([(bx + 1, base - 10), (bx + 1, base - 2)], fill=brl)
        d.ellipse([bx, base - 15, bx + 3, base - 12], fill=br, outline=brd)
        d.point((bx + 1, base - 14), fill=brl)
    for k, (c, w) in enumerate(((hx("6a1a1a"), 12), (hx("1a3a2a"), 11), (hx("2a2a4a"), 12), (hx("6a5a2a"), 10))):
        y = base - 2 - k * 3
        d.rectangle([x + 4 + (12 - w) // 2, y - 2, x + 4 + (12 - w) // 2 + w, y], fill=c)
        d.line([(x + 4 + (12 - w) // 2, y - 2), (x + 4 + (12 - w) // 2 + w, y - 2)], fill=mul(c, 1.5))
        d.point((x + 6 + k % 2 * 3, y - 1), fill=hx("c8a858"))


SHELF_ORNAMENTS = {"bust": (_shelf_bust, 14), "globe": (_shelf_globe, 15), "vase": (_shelf_vase, 13),
                   "bookends": (_shelf_bookends, 22)}


def bookshelf(img, rnd, x0, y0, x1, y1, shelf=24, ornaments=None):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=OAK)
    d.rectangle([x0 - 3, y0 - 8, x1 + 3, y0], fill=OAK_L)
    d.line([(x0 - 3, y0 - 8), (x1 + 3, y0 - 8)], fill=hx("a07a4a"))
    d.line([(x0 - 3, y0), (x1 + 3, y0)], fill=OAK_D)
    for x in range(x0, x1, 5):
        d.point((x, y0 - 4), fill=OAK_D)
    d.line([(x0, y0), (x0, y1)], fill=OAK_L)
    d.line([(x1, y0), (x1, y1)], fill=OAK_D)
    y = y0 + 4
    row = 0
    ornaments = ornaments or {}
    while y + shelf < y1 - 18:
        d.rectangle([x0 + 4, y, x1 - 4, y + shelf - 3], fill=hx("140a04"))
        x = x0 + 5
        orn = ornaments.get(row)
        while x < x1 - 6:
            r = rnd.random()
            if orn and x >= orn[1]:  # an ornament standing in a gap between the books
                draw, width = SHELF_ORNAMENTS[orn[0]]
                draw(d, x + 1, y + shelf - 3)
                x += width + 2
                orn = None
                continue
            bw = rnd.randint(3, 6)
            c = hx(rnd.choice(["6a1a1a", "1a3a2a", "2a2a4a", "6a5a2a", "4a2a1a", "8a7a5a", "3a1a2a", "5a4a3a"]))
            bh = rnd.randint(shelf - 11, shelf - 4)
            if rnd.random() < 0.08:  # leaning
                d.polygon([(x, y + shelf - 3), (x + bw, y + shelf - 3), (x + bw + 4, y + shelf - 3 - bh), (x + 4, y + shelf - 3 - bh)], fill=c)
                x += bw + 4
                continue
            d.rectangle([x, y + shelf - 3 - bh, x + bw - 1, y + shelf - 4], fill=c)
            d.line([(x, y + shelf - 3 - bh), (x, y + shelf - 4)], fill=mul(c, 1.35))
            if bw > 3:
                d.line([(x + 1, y + shelf - bh + 1), (x + bw - 2, y + shelf - bh + 1)], fill=hx("c8a858"))
                d.line([(x + 1, y + shelf - 8), (x + bw - 2, y + shelf - 8)], fill=hx("a88a48"))
            x += bw
        d.rectangle([x0 + 2, y + shelf - 3, x1 - 2, y + shelf - 1], fill=OAK_L)
        y += shelf
        row += 1
    # cupboards in the base
    d.rectangle([x0 + 2, y, x1 - 2, y1], fill=OAK)
    mx = (x0 + x1) // 2
    for a, b in ((x0 + 5, mx - 2), (mx + 2, x1 - 5)):
        d.rectangle([a, y + 3, b, y1 - 3], fill=mul(OAK, 0.9), outline=OAK_D)
        d.line([(a, y1 - 3), (b, y1 - 3)], fill=OAK_L)
    d.point((mx - 4, (y + y1) // 2), fill=hx("c8a858"))
    d.point((mx + 4, (y + y1) // 2), fill=hx("c8a858"))


def steelworks_painting(img, box):
    """A lakeside industrial landscape, distinct from the city office's heraldic portrait."""
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], fill=hx("a8842e"))
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=hx("e0c078"))
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline=hx("4a3414"), width=2)
    vgrad(img, box, hx("948678"), hx("c2ac80"))
    rnd = random.Random(117)
    for _ in range(90):
        x, y = rnd.randint(x0 + 1, x1 - 3), rnd.randint(y0 + 1, y0 + 26)
        d.line([(x, y), (min(x1 - 1, x + 3), y)], fill=rnd.choice((hx("a89880"), hx("8c8078"), hx("b6a28a"))))
    d.polygon([(x0, y0 + 34), (x0 + 8, y0 + 29), (x0 + 19, y0 + 35),
               (x0 + 30, y0 + 28), (x1, y0 + 33), (x1, y0 + 44), (x0, y0 + 44)], fill=hx("596064"))
    for x, top, width in ((x0 + 6, y0 + 35, 17), (x0 + 26, y0 + 31, 19)):
        d.rectangle([x, top, x + width, y0 + 47], fill=hx("563c30"))
        d.polygon([(x - 2, top), (x + width // 2, top - 5), (x + width + 2, top)], fill=hx("34383c"))
        for wx in range(x + 2, x + width - 1, 4):
            d.rectangle([wx, top + 4, wx + 1, top + 7], fill=hx("d8ac60"))
            d.line([(wx, top + 11), (wx + 1, top + 11)], fill=hx("a88858"))
    for x, top in ((x0 + 12, y0 + 14), (x0 + 35, y0 + 10)):
        d.rectangle([x, top, x + 3, y0 + 36], fill=hx("684c3c"))
        d.line([(x, top + 2), (x + 3, top + 2)], fill=hx("342a26"))
        for k in range(4):
            d.ellipse([x - 2 - k * 3, top - 4 - k * 2, x + 3 - k * 3, top - k * 2],
                      fill=hx("77736c"))
    vgrad(img, (x0, y0 + 48, x1, y1), hx("63747a"), hx("374b56"))
    for k in range(17):
        y = rnd.randint(y0 + 49, y1 - 1)
        x = rnd.randint(x0 + 1, x1 - 7)
        d.line([(x, y), (x + rnd.randint(3, 6), y)], fill=rnd.choice((hx("8a9590"), hx("ba9c68"), hx("4a5e66"))))
    fx = x1 - 13  # a blast furnace on the quay, its mouth glowing, and the glow on its smoke and in the lake
    d.polygon([(fx, y0 + 47), (fx + 1, y0 + 30), (fx + 3, y0 + 25), (fx + 7, y0 + 25), (fx + 9, y0 + 30),
               (fx + 10, y0 + 47)], fill=hx("3e3430"))
    d.line([(fx + 1, y0 + 31), (fx + 1, y0 + 46)], fill=hx("5e4c40"))
    for k in range(3):
        d.line([(fx + 1, y0 + 33 + k * 5), (fx + 9, y0 + 33 + k * 5)], fill=hx("2a2220"))  # its iron bands
    d.rectangle([fx + 3, y0 + 40, fx + 7, y0 + 46], fill=hx("f0a040"))
    d.rectangle([fx + 4, y0 + 42, fx + 6, y0 + 46], fill=hx("fff0a0"))
    for k in range(4):
        d.ellipse([fx + 2 + k * 2, y0 + 17 - k * 4, fx + 9 + k * 3, y0 + 24 - k * 4],
                  fill=(hx("c8784a"), hx("a87058"), hx("8c7468"), hx("888078"))[k])
    d.line([(fx - 8, y0 + 47), (fx - 8, y0 + 37)], fill=hx("2a2624"))  # an ore gantry
    d.line([(fx - 8, y0 + 37), (fx + 1, y0 + 37)], fill=hx("2a2624"))
    d.line([(fx - 8, y0 + 41), (fx - 4, y0 + 37)], fill=hx("2a2624"))
    d.line([(fx - 5, y0 + 37), (fx - 5, y0 + 42)], fill=hx("4a4440"))
    d.line([(x0, y0 + 47), (x1, y0 + 47)], fill=hx("2e2a28"))  # the quay wall
    for k in range(6):
        y = y0 + 50 + k * 3
        d.line([(fx + 2 - k % 2, y), (fx + 7 + k % 2, y)], fill=mix(hx("f0a040"), hx("374b56"), k / 7))
    by = y0 + 57  # an ore freighter steaming out: long low hull, pilot house forward, funnel aft
    d.polygon([(x0 + 10, by), (x0 + 38, by), (x0 + 36, by + 3), (x0 + 12, by + 3)], fill=hx("2a2220"))
    d.line([(x0 + 10, by), (x0 + 38, by)], fill=hx("6a3a2a"))
    d.rectangle([x0 + 12, by - 3, x0 + 15, by - 1], fill=hx("d8d0c0"))
    d.point((x0 + 13, by - 2), fill=hx("f0c060"))
    d.rectangle([x0 + 33, by - 4, x0 + 35, by - 1], fill=hx("1a1a1a"))
    d.line([(x0 + 33, by - 4), (x0 + 35, by - 4)], fill=hx("b84030"))
    d.ellipse([x0 + 34, by - 9, x0 + 39, by - 5], fill=hx("6a6660"))
    d.line([(x0 + 12, by + 4), (x0 + 36, by + 4)], fill=hx("4a5e66"))  # its wake
    for bx, byy in ((x0 + 8, y0 + 6), (x0 + 15, y0 + 9), (x1 - 22, y0 + 5)):  # gulls
        d.point((bx - 1, byy), fill=hx("4a4440"))
        d.point((bx, byy + 1), fill=hx("4a4440"))
        d.point((bx + 1, byy), fill=hx("4a4440"))
    d.polygon([(x0, y1 - 6), (x0 + 8, y1 - 10), (x0 + 25, y1 - 3), (x1, y1 - 2), (x1, y1), (x0, y1)],
              fill=hx("31342e"))
    d.line([(x0 + 3, y1 - 7), (x0 + 3, y1 - 13)], fill=hx("2a2a24"))  # reeds on the near shore
    d.line([(x0 + 5, y1 - 8), (x0 + 6, y1 - 14)], fill=hx("3a3a2c"))
    d.rectangle(box, outline=hx("302820"))
    for cx, cy in ((x0 - 3, y0 - 3), (x1 + 3, y0 - 3), (x0 - 3, y1 + 3), (x1 + 3, y1 + 3)):  # carved corner rosettes
        d.rectangle([cx - 3, cy - 3, cx + 3, cy + 3], fill=hx("c8a048"), outline=hx("4a3414"))
        d.point((cx, cy), fill=hx("f0d890"))
        d.point((cx - 1, cy - 1), fill=hx("e0c078"))
    for x in range(x0 + 4, x1 - 3, 4):  # a gilt bead along the top and bottom rails
        d.point((x, y0 - 4), fill=hx("f0d890"))
        d.point((x, y1 + 4), fill=hx("6a4a1a"))
    d.rectangle([x0 + 12, y1 + 6, x1 - 12, y1 + 9], fill=hx("c8a048"))
    d.line([(x0 + 15, y1 + 7), (x1 - 15, y1 + 7)], fill=hx("624a24"))


def _coat(d, cx, top, bot, w, base, collar=None, buttons=hx("1a1410")):
    """A greatcoat on a wooden hanger: shoulders, a turned-down collar and lapels, sleeves hanging at the sides,
    a button stand and a hem, shaded down its left edge."""
    hi, lo = mul(base, 1.35), mul(base, 0.6)
    d.line([(cx, top - 3), (cx, top)], fill=hx("8a8a80"))  # the hook
    d.arc([cx - 2, top - 6, cx + 2, top - 2], 180, 360, fill=hx("8a8a80"))
    d.line([(cx - w + 1, top + 3), (cx, top), (cx + w - 1, top + 3)], fill=hx("8a6440"), width=2)  # the hanger
    d.polygon([(cx - w, top + 3), (cx + w, top + 3), (cx + w + 1, bot), (cx - w - 1, bot)], fill=base)
    d.polygon([(cx - w, top + 3), (cx - w + 4, top + 3), (cx - w + 3, bot - 8), (cx - w - 1, bot - 6)], fill=mul(base, 0.85))
    d.line([(cx - w + 4, top + 4), (cx - w + 3, bot - 8)], fill=lo)  # the sleeves
    d.line([(cx + w - 4, top + 4), (cx + w - 3, bot - 8)], fill=lo)
    d.line([(cx - w - 1, bot - 7), (cx - w + 3, bot - 8)], fill=lo)  # cuffs
    d.line([(cx + w + 1, bot - 7), (cx + w - 3, bot - 8)], fill=lo)
    c = collar or mul(base, 0.8)
    d.polygon([(cx - 4, top + 1), (cx + 4, top + 1), (cx + 5, top + 5), (cx, top + 14), (cx - 5, top + 5)], fill=c)
    d.line([(cx - 5, top + 5), (cx, top + 14), (cx + 5, top + 5)], fill=lo)  # lapels
    d.line([(cx - 3, top + 2), (cx + 3, top + 2)], fill=hi)
    d.line([(cx, top + 14), (cx, bot)], fill=lo)  # the front edge
    for k in range(3):
        d.point((cx - 2, top + 18 + k * 8), fill=buttons)
        d.point((cx + 2, top + 18 + k * 8), fill=buttons)
    d.line([(cx - w + 5, top + 34), (cx - 2, top + 34)], fill=lo)  # pocket flaps
    d.line([(cx + 2, top + 34), (cx + w - 5, top + 34)], fill=lo)
    d.line([(cx - w - 1, bot), (cx + w + 1, bot)], fill=lo)
    d.line([(cx + w, top + 4), (cx + w + 1, bot)], fill=hi)


def _closet_contents(img, x0, y0, x1, y1):
    """Inside the open closet: a dark planked interior, a hat shelf with a homburg and a hatbox, a brass rail of
    three coats on wooden hangers, a scarf hung over one, and a pair of brogues beside a strapped valise."""
    d = ImageDraw.Draw(img)
    vgrad(img, (x0, y0, x1, y1), hx("1c120a"), hx("0c0804"))
    for x in range(x0 + 7, x1, 9):  # back planks
        d.line([(x, y0 + 14), (x, y1)], fill=hx("080402"))
        d.line([(x + 1, y0 + 14), (x + 1, y1)], fill=hx("221810"))
    shadow(img, "rect", [x0, y0, x1, y1], 0.35, 4)
    d = ImageDraw.Draw(img)
    # the hat shelf
    d.rectangle([x0, y0 + 11, x1, y0 + 13], fill=hx("4a3220"))
    d.line([(x0, y0 + 11), (x1, y0 + 11)], fill=hx("6a4a2c"))
    d.line([(x0, y0 + 14), (x1, y0 + 14)], fill=hx("040200"))
    hx0 = x0 + 6  # a homburg: brim, pinched crown, ribbon
    d.ellipse([hx0, y0 + 7, hx0 + 16, y0 + 11], fill=hx("2e2e30"))
    d.polygon([(hx0 + 3, y0 + 9), (hx0 + 4, y0 + 2), (hx0 + 8, y0 + 4), (hx0 + 12, y0 + 2), (hx0 + 13, y0 + 9)],
              fill=hx("3a3a3e"))
    d.line([(hx0 + 3, y0 + 7), (hx0 + 13, y0 + 7)], fill=hx("141416"), width=2)
    d.line([(hx0 + 1, y0 + 9), (hx0 + 15, y0 + 9)], fill=hx("4e4e54"))
    bx0 = x1 - 22  # a round striped hatbox
    d.rectangle([bx0, y0 + 2, bx0 + 16, y0 + 10], fill=hx("a88a5a"))
    for k in range(bx0 + 2, bx0 + 16, 4):
        d.line([(k, y0 + 3), (k, y0 + 10)], fill=hx("7a2a26"))
    d.rectangle([bx0 - 1, y0 + 1, bx0 + 17, y0 + 3], fill=hx("c8a870"))
    # the brass rail and the coats
    ry = y0 + 22
    d.line([(x0 + 1, ry), (x1 - 1, ry)], fill=hx("a8842e"), width=2)
    d.line([(x0 + 1, ry - 1), (x1 - 1, ry - 1)], fill=hx("e0c070"))
    _coat(d, x0 + 13, ry + 2, y1 - 40, 10, hx("2e2e38"), collar=hx("1e1e26"))  # charcoal chesterfield, velvet collar
    _coat(d, x0 + 29, ry + 2, y1 - 30, 9, hx("6a5236"), buttons=hx("2a1a0e"))  # a camel overcoat
    _coat(d, x0 + 43, ry + 2, y1 - 46, 8, hx("4a1e24"), collar=hx("3a3a3a"))  # a smoking jacket
    d.line([(x0 + 26, ry + 6), (x0 + 24, ry + 40), (x0 + 22, ry + 44)], fill=hx("9a8a6a"), width=2)  # a silk scarf
    d.line([(x0 + 32, ry + 6), (x0 + 33, ry + 34)], fill=hx("b8a880"), width=2)
    for k in range(ry + 12, ry + 42, 5):
        d.point((x0 + 24, k), fill=hx("5a3a2a"))
    # the floor: brogues and a strapped valise
    for sx in (x0 + 4, x0 + 12):
        d.polygon([(sx, y1 - 3), (sx + 2, y1 - 6), (sx + 6, y1 - 6), (sx + 8, y1 - 3), (sx + 8, y1 - 1), (sx, y1 - 1)],
                  fill=hx("4a2a14"))
        d.line([(sx + 1, y1 - 4), (sx + 7, y1 - 4)], fill=hx("7a4a24"))
        d.point((sx + 4, y1 - 5), fill=hx("a8742e"))
    vx0, vx1, vy0 = x0 + 22, x1 - 4, y1 - 20
    d.rectangle([vx0, vy0, vx1, y1 - 1], fill=hx("6a4a2a"), outline=hx("2a1a0c"))
    d.line([(vx0 + 1, vy0 + 1), (vx1 - 1, vy0 + 1)], fill=hx("8a6a40"))
    d.line([(vx0, vy0 + 4), (vx1, vy0 + 4)], fill=hx("3a2614"))  # the lid seam
    for sx in (vx0 + 6, vx1 - 6):  # straps and buckles
        d.line([(sx, vy0), (sx, y1 - 1)], fill=hx("3a2614"), width=2)
        d.rectangle([sx - 1, vy0 + 5, sx + 1, vy0 + 7], outline=hx("c8a048"))
    hm = (vx0 + vx1) // 2
    d.line([(hm - 4, vy0), (hm - 4, vy0 - 4), (hm + 4, vy0 - 4), (hm + 4, vy0)], fill=hx("2a1a0c"))  # handle
    d.point((hm - 1, vy0 + 3), fill=hx("e0c070"))  # the lock
    d.point((hm + 1, vy0 + 3), fill=hx("e0c070"))
    d.rectangle([vx0 + 10, vy0 + 9, vx0 + 16, vy0 + 13], fill=hx("c8b890"))  # a steamship label
    d.line([(vx0 + 11, vy0 + 11), (vx0 + 15, vy0 + 11)], fill=hx("7a2a26"))


def _decanters(img, R):
    """The drinks tray on the cabinet: a silver tray, a cut-glass whisky decanter and a port decanter with ball
    stoppers, a square gin bottle with a label, a soda siphon and two tumblers, each with a glint."""
    d = ImageDraw.Draw(img)
    P = lambda *a: tuple(int(round(v)) for v in R.P(*a))
    ta, tb = P(350, 40, 6), P(406, 40, 14)
    ty0, ty1 = sorted((ta[1], tb[1]))
    d.rectangle([ta[0], ty0, tb[0], ty1 + 1], fill=hx("6a6a70"))  # the tray
    d.line([(ta[0], ty1 + 1), (tb[0], ty1 + 1)], fill=hx("b8b8c0"))
    d.line([(ta[0], ty0), (tb[0], ty0)], fill=hx("4a4a50"))

    def decanter(x, liquor, h):
        bx, by = P(x, 40, 10)
        d.polygon([(bx - 4, by), (bx + 4, by), (bx + 5, by - 6), (bx + 3, by - h + 4), (bx - 3, by - h + 4),
                   (bx - 5, by - 6)], fill=mix(hx("8a9aa8"), liquor, 0.7), outline=hx("2a2a30"))
        d.rectangle([bx - 4, by - 7, bx + 4, by - 1], fill=liquor)  # the liquor line
        d.line([(bx - 4, by - 7), (bx + 4, by - 7)], fill=mul(liquor, 1.4))
        for k in range(by - 6, by, 2):  # the cut facets
            d.point((bx - 2, k), fill=mul(liquor, 1.3))
            d.point((bx + 2, k), fill=mul(liquor, 0.7))
        d.rectangle([bx - 1, by - h + 1, bx + 1, by - h + 4], fill=hx("9aa8b4"))  # neck
        d.ellipse([bx - 2, by - h - 3, bx + 2, by - h + 1], fill=hx("b8c4d0"), outline=hx("4a5058"))  # stopper
        d.point((bx - 3, by - h + 6), fill=hx("f0f0f0"))
        d.point((bx - 3, by - h + 7), fill=hx("c8d0d8"))

    decanter(354, hx("a8641e"), 16)  # whisky
    decanter(368, hx("6a1a22"), 14)  # port
    gx, gy = P(381, 40, 10)  # gin: a square bottle with a paper label
    d.rectangle([gx - 3, gy - 13, gx + 3, gy], fill=hx("7a8a8c"), outline=hx("2a3032"))
    d.rectangle([gx - 1, gy - 17, gx + 1, gy - 13], fill=hx("7a8a8c"))
    d.rectangle([gx - 1, gy - 18, gx + 1, gy - 17], fill=hx("a8842e"))
    d.rectangle([gx - 2, gy - 9, gx + 2, gy - 4], fill=hx("e8dcc0"))
    d.line([(gx - 1, gy - 7), (gx + 1, gy - 7)], fill=hx("7a2a26"))
    d.point((gx - 2, gy - 12), fill=hx("f0f0f0"))
    sx, sy = P(396, 40, 10)  # the soda siphon: blue glass, chrome head and spout
    d.rectangle([sx - 3, sy - 12, sx + 3, sy], fill=hx("3e5a86"), outline=hx("1a2840"))
    for k in range(sy - 11, sy, 3):
        d.line([(sx - 2, k), (sx + 2, k)], fill=hx("2e4a72"))
    d.rectangle([sx - 2, sy - 17, sx + 2, sy - 12], fill=hx("b8b8c0"))
    d.line([(sx + 2, sy - 16), (sx + 6, sy - 15)], fill=hx("d8d8e0"))
    d.line([(sx - 2, sy - 18), (sx + 1, sy - 19)], fill=hx("8a8a90"))  # the lever
    d.point((sx - 2, sy - 10), fill=hx("a8c0e0"))
    for x in (360, 388):  # tumblers on the tray front
        tx, ty = P(x, 40, 16)
        d.rectangle([tx - 2, ty - 5, tx + 2, ty], fill=hx("5a6870"), outline=hx("a8b4bc"))
        d.line([(tx - 1, ty - 2), (tx + 1, ty - 2)], fill=hx("c88a3a"))


STUDY_MOON = (292, 40, 304, 52)


def _study_moon(img, box):
    """A waxing gibbous moon filling box exactly: a faint halo and ring, then a crisp disc shaded pixel by pixel -
    limb darkening, the terminator softening the lower left into earthshine, the grey seas (Imbrium, Serenitatis,
    Tranquillitatis, Crisium, Procellarum, Nubium) and the bright rayed craters Tycho and Copernicus."""
    x0, y0, x1, y1 = box
    cx, cy, r = (x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2, (x1 - x0 + 1) / 2
    light(img, "ellipse", [x0 - 7, y0 - 7, x1 + 7, y1 + 7], hx("8a98c8"), 0.22, 4)
    d = ImageDraw.Draw(img)
    seas = ((-0.28, -0.38, 0.30, 0.24), (0.12, -0.32, 0.20, 0.18), (0.32, 0.02, 0.24, 0.22), (0.70, -0.28, 0.12, 0.13),
            (-0.55, 0.05, 0.26, 0.42), (-0.12, 0.40, 0.20, 0.14), (0.52, 0.30, 0.13, 0.16))
    sun = np.array([0.62, -0.32, 0.72])
    sun /= np.linalg.norm(sun)
    lit_c, sea_c, dark_c = np.array(hx("fbf6e2"), float), np.array(hx("a8a490"), float), np.array(hx("8a8a96"), float)
    px = img.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            u, v = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            rr = u * u + v * v
            if rr > 1:
                continue
            mu = math.sqrt(1 - rr)
            sea = max(min(1.0, 1.6 * (1 - ((u - su) / ru) ** 2 - ((v - sv) / rv) ** 2)) for su, sv, ru, rv in seas)
            col = lit_c + (sea_c - lit_c) * max(0.0, sea) * 0.75
            col = col * (0.72 + 0.28 * mu ** 0.5)  # limb darkening
            day = min(1.0, max(0.0, (np.dot((u, v, mu), sun) + 0.08) / 0.32))
            col = dark_c + (col - dark_c) * day
            px[x, y] = tuple(int(c) for c in col)
    for (u, v), c in (((-0.10, 0.70), "ffffff"), ((-0.30, -0.06), "fffef4"), ((-0.62, -0.10), "f4f0de")):
        d.point((int(cx + u * r), int(cy + v * r)), fill=hx(c))  # Tycho, Copernicus, Kepler
    tx, ty = int(cx - 0.10 * r), int(cy + 0.70 * r)
    for dx, dy in ((-1, -1), (1, -1), (0, -2)):  # Tycho's rays
        d.point((tx + dx, ty + dy), fill=hx("efeadb"))


def paint_study(left=False, right=False, docs=True, closet=False, moon=True):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    em = Image.new("L", img.size, 0)
    ed = ImageDraw.Draw(em)
    rnd = random.Random(91)
    R = Room3D(SFL, 240, 100)
    # ---- coffered ceiling edge, green damask above oak panelling ----
    d.rectangle([0, 0, W - 1, 12], fill=hx("2a1c10"))
    for x in range(0, W, 40):
        d.rectangle([x + 3, 2, x + 36, 9], fill=hx("3a2816"))
    d.rectangle([0, 12, W - 1, 18], fill=OAK_L)
    d.line([(0, 18), (W - 1, 18)], fill=OAK_D)
    for x in range(0, W, 4):
        d.rectangle([x, 15, x + 1, 17], fill=OAK_D)
    vgrad(img, (0, 19, W - 1, 132), hx("24382a"), hx("1c2c20"))
    for y in range(22, 132, 16):  # damask lozenges
        for x in range((y // 16) % 2 * 10, W, 20):
            d.polygon([(x, y), (x + 4, y + 6), (x, y + 12), (x - 4, y + 6)], outline=hx("30483a"))
            d.point((x, y + 6), fill=hx("3a5844"))
    noise(img, (0, 19, W - 1, 132), 3, 92)
    d.rectangle([0, 132, W - 1, 138], fill=OAK_L)
    d.line([(0, 132), (W - 1, 132)], fill=hx("a07a4a"))
    d.line([(0, 138), (W - 1, 138)], fill=OAK_D)
    d.rectangle([0, 139, W - 1, SFL], fill=OAK)
    for x in range(4, W, 30):  # raised panels of the dado
        d.rectangle([x, 144, x + 24, SFL - 10], fill=mul(OAK, 0.88))
        d.line([(x, 144), (x + 24, 144)], fill=OAK_D)
        d.line([(x, 144), (x, SFL - 10)], fill=OAK_D)
        d.line([(x, SFL - 10), (x + 24, SFL - 10)], fill=OAK_L)
        d.line([(x + 24, 144), (x + 24, SFL - 10)], fill=OAK_L)
        d.rectangle([x + 3, 147, x + 21, SFL - 13], fill=mul(OAK, 1.04))
    d.rectangle([0, SFL - 6, W - 1, SFL], fill=OAK_D)
    # ---- the two doors: the back passage to the kitchen and through to the bedroom ----
    for x0, x1 in ((20, 62), (422, 464)):
        panel_door(d, x0, 94, x1, SFL, hx("4a2e16"), knob_left=x0 > 200, frame=hx("6a4628"), frame_w=4)
    # ---- the built-in bookcase on the left ----
    bookshelf(img, rnd, 78, 30, 150, SFL, ornaments={1: ("bust", 118), 2: ("globe", 92), 4: ("vase", 124), 5: ("bookends", 100)})
    d = ImageDraw.Draw(img)
    # ---- the closet: a tall panelled door flush in the panelling ----
    wx0, wx1, wy0, wy1 = 160, 214, 70, SFL
    d.rectangle([wx0 - 4, wy0 - 8, wx1 + 4, wy1], fill=OAK_L)
    d.rectangle([wx0 - 6, wy0 - 11, wx1 + 6, wy0 - 6], fill=hx("8a6440"))
    d.line([(wx0 - 6, wy0 - 6), (wx1 + 6, wy0 - 6)], fill=OAK_D)
    if closet:
        _closet_contents(img, wx0, wy0, wx1, wy1)
        d = ImageDraw.Draw(img)
        d.polygon([(wx1, wy0), (wx1 + 14, wy0 + 6), (wx1 + 14, wy1 + 4), (wx1, wy1)], fill=hx("5a3a1e"), outline=OAK_D)
        d.polygon([(wx1 + 3, wy0 + 12), (wx1 + 11, wy0 + 16), (wx1 + 11, wy0 + 62), (wx1 + 3, wy0 + 60)], outline=OAK_D)
        d.polygon([(wx1 + 3, wy0 + 70), (wx1 + 11, wy0 + 73), (wx1 + 11, wy1 - 8), (wx1 + 3, wy1 - 10)], outline=OAK_D)
    else:
        d.rectangle([wx0, wy0, wx1, wy1], fill=hx("4a2e16"))
        for a, b in ((wy0 + 6, wy0 + 60), (wy0 + 68, wy1 - 8)):
            d.rectangle([wx0 + 6, a, wx1 - 6, b], fill=mul(hx("4a2e16"), 0.9))
            d.line([(wx0 + 6, a), (wx1 - 6, a)], fill=OAK_D)
            d.line([(wx0 + 6, a), (wx0 + 6, b)], fill=OAK_D)
            d.line([(wx0 + 6, b), (wx1 - 6, b)], fill=OAK_L)
            d.line([(wx1 - 6, a), (wx1 - 6, b)], fill=OAK_L)
        d.ellipse([wx1 - 9, 134, wx1 - 5, 138], fill=hx("c8a858"))
        d.rectangle([wx1 - 8, 140, wx1 - 6, 143], fill=hx("2a1a0a"))
    # ---- the window over the lake: moon, distant shoreline and heavy velvet drapes ----
    gx0, gy0, gx1, gy1 = 242, 32, 318, 108
    d.rectangle([gx0 - 6, gy0 - 6, gx1 + 6, gy1 + 8], fill=OAK_L)
    vgrad(img, (gx0, gy0, gx1, gy1), hx("121834"), hx("2a3460"))
    rs = random.Random(93)
    for _ in range(18):
        d.point((rs.randint(gx0, gx1), rs.randint(gy0, gy0 + 30)), fill=hx("a8b0d0"))
    if not moon:  # the plain disc the room's palette was first drawn from
        d.ellipse(list(STUDY_MOON), fill=hx("f4f0d8"))
    light(img, "ellipse", [278, 28, 318, 64], hx("6a78b0"), 0.4, 6)
    if moon:
        _study_moon(img, STUDY_MOON)
    d = ImageDraw.Draw(img)
    vgrad(img, (gx0, 78, gx1, gy1), hx("1a2440"), hx("0e1428"))  # Lake Michigan
    d.line([(gx0, 78), (gx1, 78)], fill=hx("3a4470"))
    for x in range(gx0 + 2, 270, 5):  # the lights of the shore drive, far off
        d.point((x, 77), fill=hx("e8c070"))
    ed.rectangle([gx0, gy0, gx1, gy1], fill=170)
    if moon:
        ed.ellipse(list(STUDY_MOON), fill=255)  # the moon keeps its own light through the night grade
    d.rectangle([278, gy0, 281, gy1], fill=OAK_L)
    d.rectangle([gx0, 66, gx1, 69], fill=OAK_L)
    for x in range(gx0, gx1, 13):
        d.line([(x, gy0), (x, 66)], fill=OAK)
        ed.line([(x, gy0), (x, 66)], fill=170)
    d.rectangle([gx0 - 8, gy1 + 6, gx1 + 8, gy1 + 10], fill=hx("8a6440"))
    # drapes and a pelmet
    for (a, b, c2, dd) in (((226, 20), (248, 20), (244, 128), (220, 132)), ((312, 20), (334, 20), (340, 132), (316, 128))):
        d.polygon([a, b, c2, dd], fill=hx("5a161c"))
        for k in range(1, 5):
            t = k / 5
            d.line([(a[0] + (b[0] - a[0]) * t, 20), (dd[0] + (c2[0] - dd[0]) * t, (dd[1] + c2[1]) / 2)], fill=hx("3a0c10"))
            d.line([(a[0] + (b[0] - a[0]) * t + 1, 20), (dd[0] + (c2[0] - dd[0]) * t + 1, (dd[1] + c2[1]) / 2)],
                   fill=hx("7a2228"))
    d.rectangle([222, 16, 338, 24], fill=hx("6a1a20"))
    for x in range(224, 338, 6):
        d.polygon([(x, 24), (x + 6, 24), (x + 3, 28)], fill=hx("c8a048"))
    # ---- a lakeside steelworks painting above the drinks cabinet ----
    px0, py0, px1, py1 = 352, 34, 404, 100
    steelworks_painting(img, (px0, py0, px1, py1))
    d.line([(378, 14), (px0 + 2, py0 - 5)], fill=hx("6a5a3a"))
    d.line([(378, 14), (px1 - 2, py0 - 5)], fill=hx("6a5a3a"))
    # the drinks cabinet
    R.box(img, 344, 412, 0, 40, 0, 20, hx("4a2a14"), top=hx("6a4426"), side=hx("2e1a0c"))
    d = ImageDraw.Draw(img)
    a, b = R.P(344, 40, 20), R.P(412, 0, 20)
    for k in range(2):
        cx0 = a[0] + 4 + k * (b[0] - a[0] - 8) / 2
        cx1 = cx0 + (b[0] - a[0] - 8) / 2 - 2
        d.rectangle([cx0, a[1] + 4, cx1, b[1] - 4], fill=hx("3a2010"), outline=hx("1e0e06"))
        d.rectangle([cx0 + 3, a[1] + 7, cx1 - 3, b[1] - 7], outline=hx("6a4426"))
    _decanters(img, R)
    d = ImageDraw.Draw(img)
    # ---- floor: herringbone parquet, a Persian rug under the desk ----
    floor_boards(img, SFL, H - 1, (240, 100), 14, hx("7a5430"), hx("6a4626"), hx("3a2410"), 94)
    shadow(img, "rect", [0, SFL, W, SFL + 6], 0.5, 3)
    rug(R, img, 150, 410, 14, 230, hx("5a1418"), hx("1e1e3a"), hx("c8a048"), seed=95)
    # ---- the desk chair behind the desk ----
    R.box(img, 260, 302, 0, 22, 2, 18, hx("4a1a14"), top=hx("6a2a1e"))
    R.quad(img, [(262, 22, 4), (300, 22, 4), (300, 66, 2), (262, 66, 2)], hx("5a2018"))
    d = ImageDraw.Draw(img)
    for k in range(3):
        for j in range(4):
            p = R.P(266 + j * 10, 30 + k * 12, 3)
            d.point(p, fill=hx("2a0a08"))
    a = R.P(262, 66, 2)
    b = R.P(300, 66, 2)
    d.line([a, b], fill=hx("8a3a2a"))
    # ---- the partners' desk: two pedestals of drawers, a leather top ----
    DX0, DX1, DZ0, DZ1, DH = 222, 340, 20, 46, 34
    R.box(img, DX0, DX0 + 40, 0, DH - 3, DZ0 + 2, DZ1 - 1, OAK, top=OAK_L, side=OAK_D)
    R.box(img, DX1 - 40, DX1, 0, DH - 3, DZ0 + 2, DZ1 - 1, OAK, top=OAK_L, side=OAK_D)
    R.box(img, DX0 + 40, DX1 - 40, DH - 10, DH - 3, DZ0 + 4, DZ1 - 3, mul(OAK, 0.9), side=OAK_D)  # kneehole apron
    R.box(img, DX0 - 3, DX1 + 3, DH - 3, DH, DZ0, DZ1 + 1, OAK_L, top=hx("8a6440"), side=OAK)
    R.quad(img, [(DX0 + 4, DH + 0.1, DZ0 + 3), (DX1 - 4, DH + 0.1, DZ0 + 3), (DX1 - 4, DH + 0.1, DZ1 - 3),
                 (DX0 + 4, DH + 0.1, DZ1 - 3)], hx("2a4a2e"))  # green leather
    d = ImageDraw.Draw(img)
    drawers = {}
    for side, x0 in (("left", DX0 + 3), ("right", DX1 - 37)):
        a, b = R.P(x0, DH - 6, DZ1 - 1), R.P(x0 + 34, 2, DZ1 - 1)
        ax0, ay0, ax1, ay1 = int(a[0]), int(a[1]), int(b[0]), int(b[1])
        hh = (ay1 - ay0) // 3
        for k in range(3):
            y0 = ay0 + k * hh + 1
            d.rectangle([ax0, y0, ax1, y0 + hh - 2], fill=mul(OAK, 0.95), outline=OAK_D)
            d.line([(ax0 + 1, y0 + hh - 2), (ax1 - 1, y0 + hh - 2)], fill=OAK_L)
            mx = (ax0 + ax1) // 2
            d.line([(mx - 3, y0 + hh // 2), (mx + 3, y0 + hh // 2)], fill=hx("c8a858"))
        drawers[side] = (ax0, ay0 + 1, ax1, ay0 + hh - 1)
    for side, opened in (("left", left), ("right", right)):
        if not opened:
            continue
        ax0, ay0, ax1, ay1 = drawers[side]
        # the top drawer pulled out towards us: its front drops a little and the inside shows above it
        d.polygon([(ax0, ay0), (ax1, ay0), (ax1 + 4, ay0 + 9), (ax0 - 4, ay0 + 9)], fill=hx("1a0e06"), outline=OAK_L)
        d.rectangle([ax0 - 4, ay0 + 9, ax1 + 4, ay1 + 10], fill=OAK, outline=OAK_D)
        d.line([(ax0 - 3, ay1 + 10), (ax1 + 3, ay1 + 10)], fill=OAK_L)
        shadow(img, "rect", [ax0 - 4, ay1 + 11, ax1 + 4, ay1 + 14], 0.5, 1)
        d = ImageDraw.Draw(img)
        mx = (ax0 + ax1) // 2
        d.line([(mx - 3, (ay0 + ay1) // 2 + 10), (mx + 3, (ay0 + ay1) // 2 + 10)], fill=hx("c8a858"))
        ay0 += 2
        if side == "left":
            d.rectangle([ax0 + 3, ay0, ax1 - 10, ay0 + 5], fill=hx("6a3a20"))  # a cigar box
            d.line([(ax0 + 4, ay0), (ax1 - 11, ay0)], fill=hx("c8a048"))
            d.rectangle([ax1 - 7, ay0 + 1, ax1 - 2, ay0 + 4], fill=hx("2a2a2a"))
        elif docs:
            d.polygon([(ax0 + 1, ay0), (ax1 - 1, ay0), (ax1 + 1, ay0 + 6), (ax0 - 1, ay0 + 6)], fill=hx("e0cca0"))
            d.line([(ax0 + 1, ay0 + 3), (ax1 - 1, ay0 + 3)], fill=hx("a8946a"))
            d.rectangle([mx - 2, ay0, mx + 1, ay0 + 6], fill=hx("b82020"))
    paint_study.drawers = drawers
    # on the desk: a green banker's lamp, blotter with letters, inkstand with pens, telephone, a pipe and books
    p = R.P(318, DH, 30)
    lx, ly = int(p[0]), int(p[1])
    d.ellipse([lx - 6, ly - 2, lx + 6, ly + 2], fill=hx("8a6a24"), outline=hx("3a2a0a"))  # stepped brass foot
    d.ellipse([lx - 4, ly - 3, lx + 4, ly], fill=hx("c8a048"))
    d.line([(lx - 3, ly - 2), (lx, ly - 2)], fill=hx("f0d890"))
    d.rectangle([lx - 1, ly - 14, lx, ly - 3], fill=hx("c8a048"))  # the stem
    d.point((lx - 1, ly - 10), fill=hx("f0d890"))
    d.point((lx + 1, ly - 9), fill=hx("6a5018"))
    d.line([(lx - 11, ly - 13), (lx + 5, ly - 13)], fill=hx("a8842e"))  # the shade's brass rim
    d.polygon([(lx - 11, ly - 13), (lx + 5, ly - 13), (lx + 3, ly - 19), (lx - 9, ly - 19)], fill=hx("1e5a34"),
              outline=hx("0e2a18"))  # cased green glass
    d.line([(lx - 9, ly - 18), (lx + 3, ly - 18)], fill=hx("6ab080"))
    d.line([(lx - 8, ly - 16), (lx - 4, ly - 16)], fill=hx("a0e0b0"))  # the highlight on the glass
    d.line([(lx - 10, ly - 12), (lx + 4, ly - 12)], fill=hx("f8e8a0"))  # lit opal underside
    ed.rectangle([lx - 10, ly - 12, lx + 4, ly - 12], fill=200)
    d.line([(lx + 2, ly - 12), (lx + 2, ly - 8)], fill=hx("c8a048"))  # the pull chain
    d.point((lx + 2, ly - 7), fill=hx("f0d890"))
    p = R.P(270, DH, 34)  # the blotter: leather corners on green, a letter and an envelope on it
    bx, by = int(p[0]), int(p[1])
    d.rectangle([bx - 16, by - 3, bx + 16, by + 2], fill=hx("1a2a1a"), outline=hx("0a140a"))
    d.rectangle([bx - 13, by - 2, bx + 13, by + 1], fill=hx("2e4a34"))
    for cx in (bx - 16, bx + 13):
        d.rectangle([cx, by - 3, cx + 3, by + 2], fill=hx("5a2a18"))
        d.point((cx + 1, by - 3), fill=hx("8a4a2a"))
    d.polygon([(bx - 10, by - 2), (bx + 2, by - 2), (bx + 3, by + 1), (bx - 9, by + 1)], fill=hx("e8e0c8"))  # a letter
    for k in range(2):
        d.line([(bx - 8, by - 1 + k), (bx, by - 1 + k)], fill=hx("6a6a7a") if k == 0 else hx("8a8a9a"))
    d.rectangle([bx + 4, by - 2, bx + 11, by], fill=hx("d8c8a0"), outline=hx("8a7a5a"))  # an envelope
    d.point((bx + 9, by - 1), fill=hx("a02020"))  # its wax seal
    p = R.P(240, DH, 28)  # an inkstand: walnut tray, two cut-glass wells with brass lids, a pen tray and pens
    ix, iy = int(p[0]), int(p[1])
    d.rectangle([ix - 8, iy - 2, ix + 8, iy + 1], fill=hx("4a2a12"), outline=hx("1e0e06"))
    d.line([(ix - 7, iy - 2), (ix + 7, iy - 2)], fill=hx("8a6440"))
    d.line([(ix - 6, iy), (ix + 6, iy)], fill=hx("2a1a0a"))  # the pen groove
    d.line([(ix - 5, iy), (ix + 3, iy)], fill=hx("1a1a1a"))  # a dip pen lying in it
    d.point((ix + 4, iy), fill=hx("c8a048"))
    for wx in (ix - 6, ix + 1):
        d.rectangle([wx, iy - 6, wx + 4, iy - 3], fill=hx("6a7a88"), outline=hx("2a3038"))
        d.line([(wx + 1, iy - 4), (wx + 3, iy - 4)], fill=hx("1a1a3a") if wx < ix else hx("4a0a0a"))  # blue-black, red
        d.rectangle([wx + 1, iy - 8, wx + 3, iy - 7], fill=hx("c8a048"))  # brass lids
        d.point((wx + 1, iy - 8), fill=hx("f0d890"))
        d.point((wx, iy - 5), fill=hx("e0e8f0"))
    d.line([(ix + 4, iy - 7), (ix + 8, iy - 15)], fill=hx("e8e0d0"))  # a quill in the red well
    d.line([(ix + 5, iy - 9), (ix + 9, iy - 14)], fill=hx("c8c0b0"))
    d.point((ix + 8, iy - 15), fill=hx("ffffff"))
    p = R.P(296, DH, 28)  # candlestick telephone: weighted foot, column, mouthpiece, receiver on its hook, a dial
    tx, ty = int(p[0]), int(p[1])
    d.ellipse([tx - 4, ty - 2, tx + 4, ty + 1], fill=hx("1a1a1a"), outline=hx("4a4a4a"))
    d.ellipse([tx - 2, ty - 2, tx + 2, ty], fill=hx("2a2a2a"))
    d.point((tx - 2, ty - 1), fill=hx("c8c8c8"))  # the dial's finger stop
    d.rectangle([tx - 1, ty - 13, tx, ty - 2], fill=hx("1a1a1a"))
    d.line([(tx - 1, ty - 12), (tx - 1, ty - 3)], fill=hx("5a5a5a"))
    d.ellipse([tx - 3, ty - 17, tx + 2, ty - 13], fill=hx("1a1a1a"), outline=hx("3a3a3a"))  # mouthpiece
    d.point((tx - 1, ty - 15), fill=hx("4a4a4a"))
    d.line([(tx + 1, ty - 11), (tx + 3, ty - 11)], fill=hx("8a8a8a"))  # the switch hook
    d.rectangle([tx + 3, ty - 13, tx + 5, ty - 6], fill=hx("1a1a1a"))  # receiver hung on it
    d.ellipse([tx + 2, ty - 7, tx + 6, ty - 4], fill=hx("1a1a1a"), outline=hx("3a3a3a"))
    d.point((tx + 3, ty - 12), fill=hx("6a6a6a"))
    d.line([(tx + 4, ty - 4), (tx + 6, ty - 1), (tx + 9, ty)], fill=hx("2a2014"))  # the cord
    p = R.P(332, DH, 36)  # a briar pipe in a cut-glass ashtray
    ax, ay = int(p[0]), int(p[1])
    d.ellipse([ax - 4, ay - 2, ax + 4, ay + 1], fill=hx("6a7a88"), outline=hx("2a3038"))
    d.ellipse([ax - 2, ay - 1, ax + 2, ay], fill=hx("3a3a3e"))
    d.point((ax - 3, ay - 1), fill=hx("e0e8f0"))
    d.rectangle([ax - 1, ay - 4, ax + 1, ay - 1], fill=hx("6a3a1a"))
    d.line([(ax + 1, ay - 2), (ax + 6, ay - 3)], fill=hx("1a1a1a"))
    p = R.P(228, DH, 38)  # two ledgers stacked at the corner
    kx, ky = int(p[0]), int(p[1])
    for k, c in enumerate((hx("5a1a14"), hx("2a3a24"))):
        d.rectangle([kx - 6 + k, ky - 2 - k * 3, kx + 6 + k, ky - k * 3], fill=c, outline=mul(c, 0.5))
        d.line([(kx - 5 + k, ky - 1 - k * 3), (kx + 5 + k, ky - 1 - k * 3)], fill=hx("d8ccb0"))
        d.point((kx - 5 + k, ky - 2 - k * 3), fill=hx("c8a048"))    # ---- light: the moon through the window across the desk and rug ----
    light(img, "polygon", [(gx0, gy0), (gx1, gy0), (400, H), (200, H)], hx("5a6ab0"), 0.3, 12)
    pools = [(280, 70, 70, 60, (0.7, 0.78, 1.1), 0.7), (290, 220, 110, 50, (0.6, 0.66, 0.95), 0.6)]
    img = grade(img, (0.5, 0.52, 0.74), pools, em)
    vignette(img, 0.5, (8, 8, 22), 40)
    return img


def build_study():
    base = paint_study()
    v = {"left": paint_study(left=True), "right": paint_study(right=True), "empty": paint_study(right=True, docs=False),
         "closet": paint_study(closet=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.35)
    # The room's palette comes from the window with its old plain moon, so the shaded moon, which gets a few colours of
    # its own on top, leaves every other pixel of the room as it was.
    window = (226, 14, 340, 120)
    blend.paste(paint_study(moon=False).crop(window), window[:2])
    mx0, my0, mx1, my1 = STUDY_MOON
    r = (mx1 - mx0 + 1) / 2
    inside = [base.getpixel((x, y)) for y in range(my0, my1 + 1) for x in range(mx0, mx1 + 1)
              if (x + 0.5 - mx0 - r) ** 2 + (y + 0.5 - my0 - r) ** 2 <= r * r]
    strip = Image.new("RGB", (len(inside), 1))
    strip.putdata(inside)
    disc = strip.quantize(colors=8, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).getpalette()[:24]
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    box = (mx0, my0, mx1 + 1, my1 + 1)
    mask = Image.new("L", (box[2] - box[0], box[3] - box[1]))
    ImageDraw.Draw(mask).ellipse([0, 0, mask.width - 1, mask.height - 1], fill=255)
    px.paste(pixelize(base.crop(box), pal + [tuple(disc[i:i + 3]) for i in range(0, 24, 3)]), box[:2], mask)
    save(px, "rooms", "mansion_study.png")
    dl, dr = paint_study.drawers["left"], paint_study.drawers["right"]
    print("study drawers", paint_study.drawers)
    overlay(v["left"], px, pal, (dl[0] - 8, dl[1] - 6, dl[2] + 8, dl[3] + 18), "mansion_study_drawer_left")
    overlay(v["right"], px, pal, (dr[0] - 8, dr[1] - 6, dr[2] + 8, dr[3] + 18), "mansion_study_drawer_right")
    overlay(v["empty"], px, pal, (dr[0] - 8, dr[1] - 6, dr[2] + 8, dr[3] + 18), "mansion_study_drawer_empty")
    overlay(v["closet"], px, pal, (150, 50, 236, 210), "mansion_study_closet")
    return px, v


# ------------------------------------------------------------------------------------------------ BEDROOM

BFL = 204
IVORY, IVORY_D, GILT = hx("d8ceb4"), hx("8a8068"), hx("c8a048")
SILK, SILK_D = hx("8a4a52"), hx("5a2a32")
BED = dict(x0=306, x1=392, z0=10, z1=50, top=24)


# Preserve neutral linen through the warm grade without making it emissive.
SHEET = (112, 110, 103)
SHEET_LIT = (146, 141, 130)
SHEET_FOLD = (61, 61, 60)
SHEET_SIDE = (81, 80, 76)
LINEN_PALETTE = [SHEET, SHEET_LIT, SHEET_FOLD, SHEET_SIDE] + [
    tuple(round(a + (b - a) * k / 9) for a, b in zip(SHEET_FOLD, SHEET_LIT))
    for k in range(10)
]
# Harrington's sheet is the same white cotton Eleanor later wraps herself in (sprites.ELEANOR_SHEET).
MANSION_SHEET = hx("e8e4dc")
MANSION_SHEET_LIT = hx("fffff8")
MANSION_SHEET_SIDE = hx("c8c4bc")
MANSION_SHEET_FOLD = hx("aca8a5")
MANSION_LINEN_PALETTE = [MANSION_SHEET, MANSION_SHEET_LIT, MANSION_SHEET_SIDE, MANSION_SHEET_FOLD] + [
    tuple(round(a + (b - a) * k / 9) for a, b in zip(MANSION_SHEET_FOLD, MANSION_SHEET_LIT))
    for k in range(10)
]


def linen_surface(size, outline, folds, fill=SHEET, falloff=0.35, loft=None):
    """Lit cotton with finite, tapered fold valleys and a raised lip on the lamp-facing side."""
    w, h = size
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).polygon(outline, fill=255)
    yy, xx = np.mgrid[:h, :w].astype(float)
    x0, y0, x1, y1 = mask.getbbox()
    depth = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    shade = 9 - depth * 30 * falloff + (xx - x0) / max(1, x1 - x0) * 7
    if loft:
        for cx, cy, rx, ry, strength in loft:
            shade += strength * np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))
    for points, width, strength in folds:
        lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:])]
        total = sum(lengths)
        distance = np.full((h, w), np.inf)
        signed = np.zeros((h, w))
        along = np.zeros((h, w))
        travelled = 0
        for a, b, length in zip(points, points[1:], lengths):
            dx, dy = b[0] - a[0], b[1] - a[1]
            t = np.clip(((xx - a[0]) * dx + (yy - a[1]) * dy) / length ** 2, 0, 1)
            dist = np.hypot(xx - a[0] - t * dx, yy - a[1] - t * dy)
            nearest = dist < distance
            signed[nearest] = ((xx - a[0]) * dy - (yy - a[1]) * dx)[nearest] / length
            along[nearest] = (travelled + t * length)[nearest] / total
            distance = np.minimum(distance, dist)
            travelled += length
        taper = np.maximum(0, np.sin(np.pi * np.clip(along, 0, 1))) ** 0.65
        valley = np.exp(-(distance / width) ** 2)
        lip = np.exp(-((signed - width * 1.5) / (width * 1.2)) ** 2)
        lip *= np.exp(-(distance / (width * 3)) ** 2)
        shade += taper * strength * (0.65 * lip - valley)
    # A restrained weave survives palette reduction without checkerboard highlights.
    shade += ((xx * 3 + yy * 5) % 7 - 3) * 0.35
    rgb = np.clip(np.asarray(fill) + shade[:, :, None], 0, 255).astype("uint8")
    cloth = Image.fromarray(rgb).convert("RGBA")
    cloth.putalpha(mask)
    return cloth


def _bare_eleanor():
    from .sprites import ELEANOR, SHEET_BODY, figure, pose, _arms, FW, FH
    skin = ELEANOR["skin"]
    spec = dict(ELEANOR, **SHEET_BODY)
    spec.update(torso=skin, pelvis=skin, sleeves=skin, coat=None, neckline=None, collar=None,
                bust=None, decals=[])
    f = figure(spec, pose(16, arms=_arms("side")), FW, FH).convert("RGBA")
    f.putalpha(f.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    bb = f.getbbox()
    body = f.crop((bb[0], bb[1], bb[2], bb[1] + 44))
    seated = Image.new("RGBA", (max(body.width, 20) + 14, body.height))  # the sheet's outline is drawn for this width
    seated.paste(body, (8, 0))
    return seated


def _sheet_on(figure, fill, hem, side=SHEET_SIDE):
    w, h = figure.size
    outline = [(8, 20), (14, 21), (22, 20), (26, 19), (28, 23), (27, 29),
               (30, 34), (w - 1, 38), (w - 2, 41), (26, h - 1),
               (8, h - 1), (3, 41), (5, 36), (8, 30)]
    sheet = linen_surface(figure.size, outline, [
        ([(10, 21), (13, 25), (18, 28), (22, 29)], 1.15, 22),
        ([(24, 21), (22, 26), (20, 30), (14, 34)], 1.5, 26),
        ([(9, 29), (12, 33), (20, 36), (29, 37)], 1.4, 24),
        ([(27, 32), (25, 36), (24, 42)], 1.1, 20),
        ([(7, 36), (11, 39), (17, 41)], 1.0, 16),
    ], fill, falloff=0.7, loft=[(17, 27, 8, 6, 11), (23, 35, 9, 3, 8)])
    d = ImageDraw.Draw(sheet)
    d.line([(8, 20), (14, 21), (22, 20), (26, 19)], fill=hem + (255,))
    d.line([(9, 22), (14, 23), (21, 22)], fill=side + (255,))
    return sheet


def _eleanor_in_bed(fill=SHEET, hem=SHEET_LIT, side=SHEET_SIDE):
    """Eleanor sitting up against the pillows, bare shoulders; the sheet covers her from the chest down."""
    figure = _bare_eleanor()
    return Image.alpha_composite(figure, _sheet_on(figure, fill, hem, side))


def _mansion_eleanor_in_bed():
    return _eleanor_in_bed(MANSION_SHEET, MANSION_SHEET_LIT, MANSION_SHEET_SIDE)


def _full_sheet(img):
    """One white sheet over the whole mattress: feet and knees lift it toward the foot, it pools into her lap at the
    head, and its front hangs in unequal scallops over the coverlet, kept inside the posts."""
    w, h = img.size
    side = linen_surface((w, h), [
        (311, 184), (322, 185), (336, 184), (352, 185), (368, 184), (384, 185), (399, 184),
        (399, 199), (396, 203), (387, 202), (378, 204), (367, 202), (356, 204),
        (344, 202), (333, 204), (322, 202), (313, 204), (311, 199),
    ], [
        ([(318, 185), (316, 193), (318, 202)], 1.6, 30),
        ([(331, 185), (334, 193), (332, 203)], 1.8, 34),
        ([(350, 185), (347, 194), (350, 203)], 1.9, 34),
        ([(366, 185), (369, 193), (366, 202)], 1.7, 30),
        ([(383, 185), (380, 194), (383, 203)], 1.6, 28),
    ], MANSION_SHEET_SIDE, falloff=0.9, loft=[(355, 185, 60, 2.5, -12)])
    top = linen_surface((w, h), [
        (310, 183), (314, 180), (318, 176), (323, 173), (327, 174), (331, 177),
        (337, 178), (344, 174), (350, 170), (356, 169), (362, 171), (368, 175),
        (376, 178), (388, 180), (399, 181), (399, 186), (384, 186), (368, 186),
        (352, 186), (336, 186), (322, 186), (310, 186),
    ], [
        ([(316, 182), (330, 183), (348, 182), (366, 183)], 1.6, 46),
        ([(330, 176), (333, 180), (337, 183)], 1.2, 30),
        ([(360, 172), (364, 177), (370, 181)], 1.2, 26),
        ([(343, 176), (349, 178), (356, 178)], 1.0, 18),
    ], MANSION_SHEET, falloff=0.9, loft=[(323, 175, 4, 2, 8), (354, 172, 7, 3, 10)])
    img.paste(side, (0, 0), side)
    img.paste(top, (0, 0), top)
    # the cotton tucked tight between her shins and hip
    shadow(img, "ellipse", [336, 180, 346, 186], 0.12, 1)


def _eleanor_origin(R):
    from PIL import ImageOps
    el = ImageOps.mirror(_bare_eleanor())
    hp = R.P(BED["x1"] - 16, BED["top"], (BED["z0"] + BED["z1"]) / 2)
    return int(hp[0] - el.width // 2), int(hp[1] - el.height + 10)


def _restamp_white_sheet(img, R):
    """Restore the shared lamp-lit face and Harrington's white cotton after the room's rose-colored grade."""
    from PIL import ImageOps
    before = img.copy()
    frame = Image.new("RGBA", img.size)
    _bed_front(frame, R)
    x1, z0, top = BED["x1"], BED["z0"], BED["top"]
    _full_sheet(img)
    for dz, dy in ((z0 + 8, 0), (z0 + 22, 0), (z0 + 14, 5)):
        a, b = R.P(x1 - 20, top + 12 + dy, dz), R.P(x1 - 1, top + dy, dz + 14)
        ax, ay, bx, by = a[0], a[1], b[0], b[1]
        pillow = linen_surface(img.size, [
            (ax + 3, ay), (bx - 4, ay + 1), (bx - 1, ay + 4), (bx, by - 3),
            (bx - 3, by), (ax + 2, by - 1), (ax, by - 4), (ax + 1, ay + 3),
        ], [([(ax + 3, by - 2), (bx - 7, by - 3), (bx - 3, by - 6)], 1.1, 19)],
            MANSION_SHEET, falloff=0.5, loft=[((ax + bx) / 2, (ay + by) / 2, 9, 5, 15)])
        img.paste(pillow, (0, 0), pillow)
    figure = ImageOps.mirror(_mansion_eleanor_in_bed())
    img.paste(figure, _eleanor_origin(R), figure)
    img.paste(before, (0, 0), frame.getchannel("A"))


def bedroom_palette(base, occupied, empty, screen=None):
    mixed = Image.blend(Image.blend(base, occupied, 0.4), empty, 0.3)
    if screen is not None:
        mixed = Image.blend(mixed, screen, 0.3)
    pal = palette_of(mixed, 124)
    for color in MANSION_LINEN_PALETTE:
        if color not in pal:
            pal.append(color)
    return pal


def _bed(img, R, who):
    """The walnut bed, side-on with its head to the right by the nightstand: a tall carved headboard, a low footboard,
    pillows and a bare white mattress. who: "eleanor" (sitting up under the sheet) or "empty"."""
    x0, x1, z0, z1, top = BED["x0"], BED["x1"], BED["z0"], BED["z1"], BED["top"]
    WAL, WAL_D, WAL_L = hx("4a2a18"), hx("24140a"), hx("7a4a2a")
    shadow(img, "polygon", [R.P(x0 - 6, 0, z0), R.P(x1 + 6, 0, z0), R.P(x1 + 8, 0, z1 + 6), R.P(x0 - 8, 0, z1 + 6)], 0.6, 3)
    # back posts, the headboard and the footboard's far side
    R.box(img, x1, x1 + 4, 0, 62, z0 - 1, z0 + 3, WAL_D, top=WAL_L, side=WAL_D)
    R.box(img, x0 - 4, x0, 0, 36, z0 - 1, z0 + 3, WAL_D, top=WAL_L, side=WAL_D)
    R.box(img, x1, x1 + 3, 6, 56, z0 + 2, z1 - 2, WAL, side=hx("5a3420"))
    d = ImageDraw.Draw(img)
    a, b, c = R.P(x1, 56, z0 + 2), R.P(x1, 56, z1 - 2), R.P(x1, 30, z1 - 2)
    d.polygon([a, (a[0], a[1] - 5), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 9), (b[0], b[1] - 5), b], fill=hx("5a3420"))
    p0, p1 = R.P(x1, 50, z0 + 6), R.P(x1, top + 6, z1 - 6)
    d.polygon([p0, R.P(x1, 50, z1 - 6), p1, R.P(x1, top + 6, z0 + 6)], fill=SILK, outline=WAL_D)
    # the mattress: its top a sliver from up here, the sheet showing at the head end
    R.box(img, x0, x1, 6, top, z0 + 1, z1 - 1, hx("ece6d8"), top=hx("f6f2e8"), side=hx("c8c0b0"))
    d = ImageDraw.Draw(img)
    # pillows piled against the headboard
    for k, (dz, dy) in enumerate(((z0 + 8, 0), (z0 + 22, 0), (z0 + 14, 5))):
        a, b = R.P(x1 - 20, top + 12 + dy, dz), R.P(x1 - 1, top + dy, dz + 14)
        d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=4, fill=hx("f8f4ec") if k < 2 else hx("f0e8dc"), outline=hx("b8b0a0"))
        d.line([(a[0] + 3, b[1] - 2), (b[0] - 3, b[1] - 2)], fill=hx("d8d0c0"))
        if who == "empty" and k == 2:
            d.ellipse([a[0] + 5, a[1] + 3, a[0] + 13, a[1] + 7], fill=hx("d8d0c0"))  # the dent where her head was
    if who == "eleanor":
        from PIL import ImageOps
        el = ImageOps.mirror(_mansion_eleanor_in_bed())
        img.paste(el, _eleanor_origin(R), el)
    # No coverlet: the sheet is all that covered the mattress, and it went with her when she rose.
    _bed_front(img, R)


# The folding screen's hinge feet, from the back of the room to the front: it runs into the room nearly edge-on to us,
# its leaves folded tight in a sharp zig-zag so it stands on a small patch of floor. Its y-sort point is its nearest foot.
SCREEN_HINGES = ((139, 213), (130, 217), (134, 221), (125, 225), (128, 229))
SCREEN_FEET = SCREEN_HINGES[-1][1]
BED_FIRE_BOX = (164, 126, 209, 205)  # the hearth's opening, animated by mansion_bedroom_fire
BED_FIRE_FRAMES = 8


def _hearth_fire(img, xa, xb, base, t):
    """The low fire on the grate: tongues of flame that swell, lean and flicker with phase t (looping on 1), and
    wisps of smoke curling up into the chimney throat."""
    d = ImageDraw.Draw(img)
    tau = 2 * math.pi
    soot, smoke = hx("1e1410"), hx("6a6058")
    for k in range(3):  # smoke first, so the flames sit in front of it
        p = (t + k / 3) % 1.0
        for j in range(4):
            q = p + j * 0.06
            if q >= 1:
                continue
            sy = base - 14 - q * 58
            sx = (xa + xb) / 2 + (k - 1) * 6 + 4 * math.sin(tau * (q * 1.5 + k * 0.3))
            r = 2 + q * 4
            c = mix(soot, smoke, 0.55 * (1 - q) * (1 - j * 0.2))
            d.ellipse([sx - r, sy - r * 0.7, sx + r, sy + r * 0.7], fill=c)
    tongues = ((2, 9, 0.0), (7, 15, 0.35), (12, 11, 0.7), (17, 19, 0.15), (22, 10, 0.55), (27, 14, 0.85))
    layers = ((hx("c8401a"), 1.0, 1.0), (hx("f08a2a"), 0.72, 0.7), (hx("ffd070"), 0.45, 0.42), (hx("fff4d0"), 0.2, 0.2))
    for dx, h0, ph in tongues:
        cx = xa + dx
        h = h0 * (0.78 + 0.22 * math.sin(tau * (t + ph)) + 0.08 * math.sin(tau * (3 * t + ph * 2)))
        sway = 1.6 * math.sin(tau * (2 * t + ph))
        for col, hs, ws in layers:
            hh, w = h * hs, 3.2 * ws + 0.6
            pts = []
            n = 6
            for i in range(n + 1):  # up the left edge, bending with the draught
                f = i / n
                pts.append((cx - w * (1 - f) ** 0.8 + sway * f * f + 0.6 * math.sin(tau * (t * 2 + f + ph)), base - hh * f))
            for i in range(n, -1, -1):  # and back down the right
                f = i / n
                pts.append((cx + w * (1 - f) ** 0.8 + sway * f * f + 0.6 * math.sin(tau * (t * 2 + f + ph + 0.3)), base - hh * f))
            d.polygon(pts, fill=col)
    for k in range(4):  # sparks rising off the logs
        q = (t * 2 + k / 4) % 1.0
        sx = xa + 6 + k * 7 + 2 * math.sin(tau * (q + k * 0.2))
        d.point((sx, base - 6 - q * 30), fill=hx("ffc060") if q < 0.6 else hx("a85a2a"))


def _mantel_clock(d, cx, shelf):
    """A gilt French mantel clock: a stepped plinth on bun feet, a waisted drum case with an enamel dial, Roman
    hour ticks, blued hands and a bezel, a glimpse of the pendulum through a lunette, and an urn finial."""
    gilt, gilt_l, gilt_d = hx("c8a040"), hx("f0d070"), hx("6a5018")
    for fx in (cx - 8, cx + 7):  # bun feet
        d.ellipse([fx - 1, shelf - 2, fx + 2, shelf], fill=gilt_d)
    d.rectangle([cx - 9, shelf - 5, cx + 9, shelf - 2], fill=gilt, outline=gilt_d)  # plinth
    d.line([(cx - 8, shelf - 5), (cx + 8, shelf - 5)], fill=gilt_l)
    d.rectangle([cx - 4, shelf - 4, cx + 4, shelf - 3], fill=hx("2a1a0a"))  # the pendulum lunette
    d.point((cx + (1 if shelf % 2 else -1), shelf - 4), fill=gilt_l)
    d.polygon([(cx - 7, shelf - 5), (cx + 7, shelf - 5), (cx + 6, shelf - 8), (cx - 6, shelf - 8)], fill=gilt_d)
    d.ellipse([cx - 7, shelf - 21, cx + 7, shelf - 7], fill=gilt, outline=gilt_d)  # the drum
    d.arc([cx - 7, shelf - 21, cx + 7, shelf - 7], 200, 290, fill=gilt_l)
    d.ellipse([cx - 5, shelf - 19, cx + 5, shelf - 9], fill=hx("f4eedc"), outline=hx("8a7030"))  # enamel dial
    oy = shelf - 14
    for k in range(12):
        a = k * math.pi / 6
        d.point((round(cx + 4 * math.sin(a)), round(oy - 4 * math.cos(a))), fill=hx("2a2a2a"))
    d.line([(cx, oy), (cx - 2, oy - 2)], fill=hx("1a2a4a"))  # ten past ten, blued steel
    d.line([(cx, oy), (cx + 3, oy - 3)], fill=hx("1a2a4a"))
    d.point((cx, oy), fill=gilt_d)
    d.point((cx - 3, oy - 3), fill=hx("ffffff"))  # glint on the glass
    d.rectangle([cx - 1, shelf - 24, cx + 1, shelf - 21], fill=gilt)  # urn finial
    d.ellipse([cx - 2, shelf - 27, cx + 2, shelf - 23], fill=gilt, outline=gilt_d)
    d.point((cx, shelf - 28), fill=gilt_l)
    for sx in (-1, 1):  # scrolls either side
        d.arc([cx + sx * 9 - 3, shelf - 14, cx + sx * 9 + 3, shelf - 7], 90 if sx > 0 else 270, 270 if sx > 0 else 90,
              fill=gilt)


def _candlestick(d, ed, x, shelf):
    """A brass baluster candlestick: a domed foot, a knopped stem, a drip pan, a tall ivory candle with a lit wick."""
    br, br_l, br_d = hx("c8a040"), hx("f0d070"), hx("6a5018")
    d.ellipse([x - 4, shelf - 3, x + 4, shelf], fill=br, outline=br_d)  # foot
    d.line([(x - 3, shelf - 2), (x - 1, shelf - 3)], fill=br_l)
    d.rectangle([x - 1, shelf - 12, x + 1, shelf - 3], fill=br)  # stem
    for ky in (shelf - 5, shelf - 9):  # knops
        d.ellipse([x - 2, ky - 1, x + 2, ky + 1], fill=br, outline=br_d)
    d.line([(x - 1, shelf - 12), (x - 1, shelf - 3)], fill=br_l)
    d.rectangle([x - 3, shelf - 14, x + 3, shelf - 12], fill=br, outline=br_d)  # drip pan
    d.rectangle([x - 1, shelf - 24, x + 1, shelf - 14], fill=hx("f0e8d0"))  # candle
    d.line([(x + 1, shelf - 24), (x + 1, shelf - 14)], fill=hx("c8bea4"))
    d.point((x - 1, shelf - 20), fill=hx("fff8e8"))  # a wax drip
    d.point((x - 1, shelf - 19), fill=hx("fff8e8"))
    d.point((x, shelf - 25), fill=hx("2a1a0a"))  # wick
    d.polygon([(x - 1, shelf - 26), (x, shelf - 30), (x + 1, shelf - 26), (x, shelf - 25)], fill=hx("ffc860"))
    d.point((x, shelf - 27), fill=hx("fff4d0"))
    ed.ellipse([x - 2, shelf - 31, x + 2, shelf - 24], fill=255)


def _bedroom_window(img, ed, x0, y0, x1, y1):
    """The tall sash window: a moulded architrave and sill, glazing bars, a deep reveal; outside, a starry sky with
    thin cloud, a cratered moon with a halo, the lake's faint shine and the black line of the grounds' trees."""
    d = ImageDraw.Draw(img)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 6], fill=IVORY)
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=IVORY_D)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 8], fill=hx("ece4cc"))  # sill
    d.line([(x0 - 8, y1 + 8), (x1 + 8, y1 + 8)], fill=IVORY_D)
    vgrad(img, (x0, y0, x1, y1), hx("0e1430"), hx("2a3460"))
    rs = random.Random(1061)
    for _ in range(22):  # stars, thicker high up
        sx, sy = rs.randint(x0, x1), rs.randint(y0, y0 + 40)
        d.point((sx, sy), fill=hx("c8d0e8") if rs.random() < 0.3 else hx("7a84a8"))
    for cy, cx0, cx1 in ((66, x0, x0 + 30), (72, x0 + 14, x1), (38, x0 + 4, x0 + 22)):  # thin cloud, moonlit edges
        d.line([(cx0, cy), (cx1, cy)], fill=hx("3a4470"))
        d.line([(cx0 + 4, cy - 1), (cx1 - 6, cy - 1)], fill=hx("5a6490"))
    light(img, "ellipse", [262, 37, 291, 66], hx("7a88b0"), 0.18, 6)
    d = ImageDraw.Draw(img)
    d.ellipse([268, 43, 285, 60], outline=hx("4a5888"))  # a faint ring of halo
    d.ellipse([270, 45, 283, 58], fill=hx("f4f0d8"))  # the moon
    d.arc([270, 45, 283, 58], 280, 100, fill=hx("fffcec"))
    d.arc([270, 45, 283, 58], 120, 250, fill=hx("cfc8ac"))  # limb darkening on the shadowed side
    d.arc([271, 46, 282, 57], 150, 220, fill=hx("e2dcc4"))
    # the seas: Imbrium and Serenitatis high, Tranquillitatis to the right, Procellarum's long stain to the left
    d.polygon([(273, 48), (276, 47), (277, 49), (275, 51), (272, 51)], fill=hx("d2ccb2"))
    d.polygon([(278, 48), (280, 48), (281, 50), (279, 51)], fill=hx("d6d0b6"))
    d.polygon([(279, 52), (281, 51), (282, 53), (280, 55), (278, 54)], fill=hx("d4ceb4"))
    d.line([(271, 52), (272, 55)], fill=hx("d8d2ba"))
    d.point((276, 53), fill=hx("dcd6be"))  # Nubium
    for (mx, my) in ((275, 56), (277, 51), (280, 46)):  # bright rayed craters: Tycho, Copernicus, a rim
        d.point((mx, my), fill=hx("ffffff"))
    d.point((275, 57), fill=hx("fcf8e8"))
    d.point((274, 56), fill=hx("fcf8e8"))
    d.point((276, 52), fill=hx("c8c2a8"))  # Copernicus's shadowed wall
    vgrad(img, (x0, 96, x1, 104), hx("1a2244"), hx("141a36"))  # the lake, far off
    for k in range(7):  # the moon's broken path on the water
        d.point((276 + (k % 3) - 1, 97 + k), fill=hx("4a5480"))
    d.line([(x0, 96), (x1, 96)], fill=hx("2e3866"))
    rt = random.Random(1062)  # the treeline of the grounds, black against the lake
    top = 104
    for x in range(x0, x1 + 1):
        top = max(98, min(108, top + rt.choice((-1, 0, 0, 1))))
        d.line([(x, top), (x, y1)], fill=hx("0a0c18"))
    ed.rectangle([x0, y0, x1, y1], fill=170)
    # glazing: the meeting rail, the bars and a reveal shadow down the left
    d.rectangle([264, y0, 266, y1], fill=IVORY)
    for y in (y0 + 34, y0 + 70):
        d.rectangle([x0, y, x1, y + 2], fill=IVORY)
        d.line([(x0, y + 3), (x1, y + 3)], fill=hx("4a4656"))  # the bar's shadow on the night glass
    d.line([(265, y0), (265, y1)], fill=hx("fffaf0"))
    d.rectangle([x0, y0, x0 + 1, y1], fill=IVORY_D)
    d.rectangle([x0, y0, x1, y0 + 1], fill=IVORY_D)
    for y in (y0 + 30, y0 + 66):  # sash lifts
        d.point((262, y), fill=GILT)
        d.point((268, y), fill=GILT)


def _folding_screen(img):
    """A four-leaf lacquered screen standing nearly edge-on to us, running back into the room between the door and
    the hearth: the leaves folded tight in a sharp zig-zag, the two facing us painted with reeds, a heron and a red sun
    on gold leaf, the two turned away narrow and black; brass hinges, little feet and a silk robe thrown over the near
    end. Tall enough to hide a man from the bed, and set so the man crouched beside it stays in full view of the room's
    door."""
    d = ImageDraw.Draw(img)
    lac, lac_l, lac_d = hx("2a1a12"), hx("5a3a24"), hx("0e0806")

    def height(y):  # the game's depth scale (FarY 206 -> 0.94, NearY 262 -> 1.04) on a 74-pixel screen
        return 74 * (0.94 + (y - 206) / 56 * 0.1)

    hinges = [(x, y, y - height(y)) for x, y in SCREEN_HINGES]
    shadow(img, "polygon", [(x + 1, y) for x, y, _ in hinges] + [(x + 4, y + 2) for x, y, _ in reversed(hinges)],
           0.5, 1)
    d = ImageDraw.Draw(img)

    def pt(i, u, v):  # a point on leaf i: u across it (0 back hinge, 1 front), v up it (0 floor, 1 top)
        (xa, ya, ta), (xb, yb, tb) = hinges[i], hinges[i + 1]
        return (xa + (xb - xa) * u, (ya + (yb - ya) * u) * (1 - v) + (ta + (tb - ta) * u) * v)

    def quad(i, u0, u1, v0, v1, fill):
        d.polygon([pt(i, u0, v0), pt(i, u1, v0), pt(i, u1, v1), pt(i, u0, v1)], fill=fill)

    for i in range(4):
        (xa, ya, ta), (xb, yb, tb) = hinges[i], hinges[i + 1]
        facing = abs(xb - xa) > 6  # the leaves turned towards us show their painted face
        d.polygon([pt(i, 0, 0), pt(i, 1, 0), pt(i, 1, 1), pt(i, 0, 1)], fill=lac if facing else mul(lac, 0.7),
                  outline=lac_d)
        d.line([pt(i, 0, 1), pt(i, 1, 1)], fill=lac_l)  # the lacquered top rail
        if not facing:
            d.line([pt(i, 0.5, 0.06), pt(i, 0.5, 0.94)], fill=hx("6a5030"))  # a gilt edge line down the narrow leaf
            continue
        # black lacquer painted in gold: dark against the fire-lit dado, so the folded leaves read as solid
        quad(i, 0.14, 0.86, 0.06, 0.94, hx("1a100c"))
        quad(i, 0.14, 0.86, 0.06, 0.12, hx("3a3a40"))  # water along the bottom
        hill = 0.62 + 0.05 * (i % 3)
        d.line([pt(i, 0.14, hill), pt(i, 0.5, hill + 0.04), pt(i, 0.86, hill - 0.02)], fill=hx("a8823a"))
        for k, u in enumerate((0.2, 0.32, 0.45, 0.58, 0.7, 0.8)):  # gold reeds rising out of the water
            top = 0.24 + 0.09 * ((k * 5 + i) % 4)
            d.line([pt(i, u, 0.08), pt(i, u + 0.03, top)], fill=hx("c8a040") if k % 2 else hx("8a6a2a"))
            d.point(pt(i, u + 0.03, top + 0.02), fill=hx("e0c060"))  # a bulrush head
        if i == 0:  # a heron standing in the reeds, foreshortened like the leaf
            bx, by = pt(i, 0.5, 0.42)
            d.ellipse([bx - 3, by - 2, bx + 2, by + 2], fill=hx("f0ece0"))
            d.line([(bx - 1, by - 2), (bx - 2, by - 8), (bx, by - 10)], fill=hx("f0ece0"))
            d.line([(bx, by - 10), (bx + 3, by - 9)], fill=hx("c89a3a"))  # the bill
            d.point((bx - 1, by - 10), fill=hx("1a1a1a"))
            d.line([(bx - 3, by), (bx + 2, by + 1)], fill=hx("6a6a70"))  # its grey wing
            d.line([(bx, by + 2), (bx, by + 8)], fill=hx("2a2a2a"))
        if i == 2:  # the red sun over the hills, and a heron in flight under it
            sx, sy = pt(i, 0.5, 0.8)
            d.ellipse([sx - 3, sy - 3, sx + 2, sy + 3], fill=hx("c84a30"))
            d.point((sx - 2, sy - 2), fill=hx("e87a50"))
            fx, fy = pt(i, 0.45, 0.68)
            d.line([(fx - 3, fy - 1), (fx, fy + 1), (fx + 3, fy - 1)], fill=hx("f0ece0"))
        d.line([pt(i, 0.14, 0.06), pt(i, 0.14, 0.94)], fill=hx("8a6a2a"))  # the inner gilt fillet
    for i, (x, y, top) in enumerate(hinges):
        h = y - top
        d.line([(x, y - 2), (x, top)], fill=lac_d if 0 < i < 4 else lac)
        d.rectangle([x - 1, y - 2, x + 1, y], fill=lac_d)  # feet
        if 0 < i < 4:
            for v in (0.2, 0.8):  # brass hinges
                d.rectangle([x - 1, y - h * v - 1, x, y - h * v + 1], fill=hx("c8a040"))
                d.point((x - 1, y - h * v - 1), fill=hx("f0d070"))
    # a silk robe thrown over the near end: folded across the top, hanging down our side
    x, y, top = hinges[3]
    x2, _, top2 = hinges[4]
    robe, robe_l, robe_d = hx("3a5a7a"), hx("6a8aaa"), hx("22384e")
    d.polygon([(x + 1, top - 1), (x2 - 1, top2 - 2), (x2 - 2, top2 + 16), (x2 + 1, top2 + 22), (x2 + 4, top2 + 18),
               (x2 + 3, top2 + 3), (x2 + 5, top2 + 2), (x2 + 6, top2 + 12)], fill=robe)
    d.line([(x + 1, top - 1), (x2 - 1, top2 - 2)], fill=robe_l)
    d.line([(x2 + 1, top2 + 2), (x2 + 1, top2 + 19)], fill=robe_d)
    d.line([(x2 + 3, top2 + 1), (x2 + 4, top2 + 15)], fill=robe_l)
    d.line([(x2 - 1, top2 + 4), (x2 - 3, top2 + 24)], fill=hx("c8a040"))  # its sash hanging loose

def _bed_front(img, R):
    """The carved frame in front of the cotton; also supplies its exact occlusion mask."""
    x0, x1, z0, z1 = BED["x0"], BED["x1"], BED["z0"], BED["z1"]
    WAL, WAL_D, WAL_L = hx("4a2a18"), hx("24140a"), hx("7a4a2a")
    # front posts, the footboard and the headboard's near edge
    R.box(img, x0 - 4, x0, 4, 32, z0 + 3, z1 - 1, WAL, top=WAL_L, side=WAL_D)
    d = ImageDraw.Draw(img)
    a, b = R.P(x0 - 4, 28, z1 - 1), R.P(x0 - 4, 10, z0 + 6)
    for x0_, z_ in ((x0 - 4, z1 - 1), (x1, z1 - 1)):
        hgt = 38 if x0_ < x1 else 64
        R.box(img, x0_, x0_ + 4, 0, hgt, z_, z_ + 4, WAL_D, top=WAL_L, side=WAL_D)
        p = R.P(x0_ + 2, hgt, z_ + 2)
        d = ImageDraw.Draw(img)
        d.ellipse([p[0] - 3, p[1] - 6, p[0] + 3, p[1]], fill=WAL_L, outline=WAL_D)
        d.point((p[0] - 1, p[1] - 4), fill=hx("b8844a"))
    for x0_, hgt in ((x0 - 4, 36), (x1, 62)):
        p = R.P(x0_ + 2, hgt, z0 + 1)
        d.ellipse([p[0] - 3, p[1] - 6, p[0] + 3, p[1]], fill=WAL_L, outline=WAL_D)
    R.line(img, (x0 - 2, 4, z1 + 3), (x1 + 2, 4, z1 + 3), WAL)

def paint_bedroom(bed=None, screen=False, fire_t=0.0, candlestick=False):
    """The room; bed is None (the room alone), "eleanor" or "empty"; screen adds the folding screen (cut as its own
    sprite); fire_t in [0, 1) is the phase of the hearth fire's flame and smoke loop; candlestick adds the brass
    candlestick on the nightstand (cut as its own sprite, so Eleanor can take it)."""
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    em = Image.new("L", img.size, 0)
    ed = ImageDraw.Draw(em)
    R = Room3D(BFL, 240, 100)
    # ---- cornice, rose silk damask, an ivory panelled dado with gilt lines ----
    d.rectangle([0, 0, W - 1, 10], fill=hx("e4dac0"))
    d.rectangle([0, 10, W - 1, 18], fill=IVORY)
    for x in range(0, W, 5):
        d.rectangle([x, 11, x + 2, 14], fill=IVORY_D)
    d.line([(0, 18), (W - 1, 18)], fill=GILT)
    vgrad(img, (0, 19, W - 1, 136), hx("7a3e48"), hx("6a3440"))
    for y in range(22, 136, 18):
        for x in range((y // 18) % 2 * 12, W, 24):
            d.polygon([(x, y), (x + 5, y + 5), (x, y + 12), (x - 5, y + 5)], fill=hx("84464f"))
            d.point((x, y + 5), fill=hx("a86068"))
            d.line([(x - 2, y + 13), (x + 2, y + 13)], fill=hx("84464f"))
    noise(img, (0, 19, W - 1, 136), 3, 102)
    d.rectangle([0, 136, W - 1, 142], fill=IVORY)
    d.line([(0, 136), (W - 1, 136)], fill=hx("f0e8d0"))
    d.line([(0, 142), (W - 1, 142)], fill=IVORY_D)
    d.rectangle([0, 143, W - 1, BFL], fill=mul(IVORY, 0.92))
    for x in range(6, W, 32):
        d.rectangle([x, 148, x + 26, BFL - 10], outline=GILT)
        d.rectangle([x + 2, 150, x + 24, BFL - 12], outline=mul(IVORY, 0.78))
    d.rectangle([0, BFL - 6, W - 1, BFL], fill=IVORY_D)
    # ---- doors: to the study (left) and the landing (right), ivory with gilt beading ----
    for x0, x1 in ((10, 52), (432, 474)):
        panel_door(d, x0, 94, x1, BFL, hx("cfc4a8"), knob_left=x0 > 200, frame=hx("e4dac0"), frame_w=4)
        d.rectangle([x0 - 6, 82, x1 + 6, 85], fill=GILT)
    # ---- the marble fireplace, a low fire; a gilt mirror, a clock and candlesticks on the mantel ----
    fx0, fx1 = 150, 222
    d.rectangle([fx0 - 6, 40, fx1 + 6, 104], fill=GILT)
    d.rectangle([fx0 - 3, 43, fx1 + 3, 101], fill=hx("8a6a28"))
    vgrad(img, (fx0, 46, fx1, 98), hx("4a3a44"), hx("2a2230"))  # the mirror holds the room's dark and the window
    d.polygon([(fx0 + 6, 98), (fx0 + 24, 50), (fx0 + 40, 50), (fx0 + 22, 98)], fill=hx("4e4a5e"))
    d.ellipse([fx0 - 9, 34, fx0 + 1, 44], fill=GILT)
    d.ellipse([fx1 - 1, 34, fx1 + 9, 44], fill=GILT)
    d.polygon([((fx0 + fx1) / 2 - 10, 40), ((fx0 + fx1) / 2, 30), ((fx0 + fx1) / 2 + 10, 40)], fill=GILT)
    R.box(img, fx0 - 8, fx1 + 8, 102, 107, 0, 10, hx("e8e4dc"), top=hx("f4f0ea"), side=hx("b8b4ac"))
    d = ImageDraw.Draw(img)
    d.rectangle([fx0, 108, fx1, BFL], fill=hx("e0dcd2"))
    for x in (fx0, fx1 - 10):  # fluted pilasters
        d.rectangle([x, 108, x + 10, BFL], fill=hx("d4d0c6"), outline=hx("8a8680"))
        for k in range(2, 10, 3):
            d.line([(x + k, 114), (x + k, BFL - 6)], fill=hx("b4b0a6"))
    d.rectangle([fx0 + 10, 110, fx1 - 10, 120], fill=hx("ece8e0"))
    d.ellipse([(fx0 + fx1) / 2 - 5, 111, (fx0 + fx1) / 2 + 5, 119], outline=hx("a8a49a"))
    d.rectangle([fx0 + 14, 126, fx1 - 14, BFL], fill=hx("120a08"))
    d.rectangle([fx0 + 16, 128, fx1 - 16, BFL], fill=hx("1e1410"))
    for y in range(130, BFL, 6):
        d.line([(fx0 + 16, y), (fx1 - 16, y)], fill=hx("2a1c16"))
    d.rectangle([fx0 + 20, BFL - 12, fx1 - 20, BFL - 4], fill=hx("1a1a1a"))  # grate
    for gx in range(fx0 + 21, fx1 - 20, 4):
        d.line([(gx, BFL - 16), (gx, BFL - 4)], fill=hx("2a2a2a"))
    d.polygon([(fx0 + 22, BFL - 12), (fx1 - 24, BFL - 16), (fx1 - 22, BFL - 12), (fx0 + 24, BFL - 9)], fill=hx("3a2014"))  # logs
    d.polygon([(fx0 + 24, BFL - 15), (fx1 - 22, BFL - 11), (fx1 - 24, BFL - 9), (fx0 + 22, BFL - 13)], fill=hx("2e180e"))
    d.ellipse([fx1 - 26, BFL - 17, fx1 - 21, BFL - 11], fill=hx("c86a3a"))
    d.ellipse([fx0 + 21, BFL - 15, fx0 + 25, BFL - 11], fill=hx("a85a2a"))
    _hearth_fire(img, fx0 + 20, fx1 - 20, BFL - 12, fire_t)
    d = ImageDraw.Draw(img)
    d.rectangle([fx0 + 20, BFL - 8, fx1 - 20, BFL - 5], fill=hx("c84a18"))
    for k in range(fx0 + 21, fx1 - 20, 3):  # glowing coals in the ash pan
        d.point((k, BFL - 7 + (k % 2)), fill=hx("ffb040"))
    ed.rectangle([fx0 + 18, BFL - 24, fx1 - 18, BFL - 4], fill=230)
    R.box(img, fx0 - 2, fx1 + 2, 0, 4, 10, 16, hx("b8903a"), top=hx("e0c060"))  # brass fender
    d = ImageDraw.Draw(img)
    cx = (fx0 + fx1) / 2  # clock and candlesticks on the mantel shelf
    _mantel_clock(d, int(cx), 102)
    for x in (fx0 + 6, fx1 - 6):
        _candlestick(d, ed, x, 102)
    # ---- the tall window: the moon over the lake, the grounds black below ----
    gx0, gy0, gx1, gy1 = 240, 34, 290, 140
    _bedroom_window(img, ed, gx0, gy0, gx1, gy1)
    d = ImageDraw.Draw(img)
    for (a, b, c2, dd) in (((228, 26), (248, 26), (244, 150), (226, 154)), ((282, 26), (302, 26), (304, 154), (286, 150))):
        d.polygon([a, b, c2, dd], fill=hx("6a2a3a"))
        for k in range(1, 4):
            t = k / 4
            d.line([(a[0] + (b[0] - a[0]) * t, 28), (dd[0] + (c2[0] - dd[0]) * t, 150)], fill=hx("4a1a26"))
    d.chord([224, 14, 306, 44], 0, 180, fill=hx("7a3242"), outline=hx("4a1a26"))
    d.line([(224, 29), (306, 29)], fill=GILT)
    for (x, y) in ((236, 120), (294, 120)):  # tie-backs
        d.ellipse([x - 3, y - 2, x + 3, y + 4], fill=GILT)

    # ---- nightstand with a silk-shaded lamp, lit ----
    R.box(img, 402, 422, 0, 30, 2, 18, hx("5a3420"), top=hx("7a4a2a"), side=hx("3a2014"))
    d = ImageDraw.Draw(img)
    a, b = R.P(402, 30, 18), R.P(422, 0, 18)
    d.rectangle([a[0] + 2, a[1] + 3, b[0] - 2, a[1] + 10], outline=hx("2a1a0c"))
    d.point(((a[0] + b[0]) / 2, a[1] + 6), fill=GILT)
    lp = R.P(417, 30, 8)  # right of centre, leaving the front left corner clear for the candlestick
    lx, ly = round(lp[0]), round(lp[1])
    brass, brass_l, brass_d = hx("c8a040"), hx("f4d880"), hx("5a4014")
    # a turned brass base: a stepped foot, a round urn body with a lit highlight, a knopped column
    d.ellipse([lx - 5, ly - 2, lx + 5, ly + 1], fill=brass, outline=brass_d)
    d.line([(lx - 3, ly - 1), (lx + 2, ly - 1)], fill=brass_l)
    d.rectangle([lx - 2, ly - 4, lx + 2, ly - 2], fill=brass_d)
    d.ellipse([lx - 4, ly - 9, lx + 4, ly - 3], fill=brass, outline=brass_d)
    d.line([(lx - 2, ly - 8), (lx - 3, ly - 5)], fill=brass_l)
    d.point((lx - 2, ly - 7), fill=hx("fff4c8"))
    d.rectangle([lx - 1, ly - 13, lx + 1, ly - 9], fill=brass, outline=brass_d)
    d.line([(lx - 2, ly - 11), (lx + 2, ly - 11)], fill=brass_l)
    d.point((lx, ly - 12), fill=brass_l)
    # a pleated silk shade: a narrow top rim, box pleats catching the bulb, a gilt braid and a beaded fringe
    st, sb = ly - 26, ly - 14
    shade = [(lx - 8, sb), (lx + 8, sb), (lx + 5, st), (lx - 5, st)]
    d.polygon(shade, fill=hx("e8a080"))
    for k in range(-7, 8, 2):
        top_x = lx + round(k * 5 / 8)
        d.line([(top_x, st + 1), (lx + k, sb - 1)], fill=hx("c87860") if k % 4 == 1 else hx("f8c8a0"))
    d.line([(lx - 5, st), (lx + 5, st)], fill=hx("8a4a34"))
    d.line([(lx - 5, st + 1), (lx + 5, st + 1)], fill=GILT)
    d.line([(lx - 8, sb), (lx + 8, sb)], fill=GILT)
    d.line([(lx - 8, sb + 1), (lx + 8, sb + 1)], fill=hx("8a5a28"))
    for k in range(-8, 9, 2):
        d.point((lx + k, sb + 2), fill=hx("e8c870"))
    d.line([(lx - 8, sb), (lx - 5, st)], fill=hx("a85a48"))
    d.line([(lx + 8, sb), (lx + 5, st)], fill=hx("a85a48"))
    ed.polygon([(lx - 7, sb - 1), (lx + 7, sb - 1), (lx + 4, st + 2), (lx - 4, st + 2)], fill=150)
    p = R.P(408, 30, 14)  # a book and a glass of water
    d.rectangle([p[0] - 4, p[1] - 2, p[0] + 2, p[1]], fill=hx("2a3a5a"))
    if candlestick:
        _nightstand_candlestick(d, *R.P(*NIGHTSTAND_CANDLESTICK))
    # ---- floor: parquet, a pale Aubusson rug ----
    floor_boards(img, BFL, H - 1, (240, 100), 14, hx("6a4428"), hx("5a3820"), hx("2e1c0e"), 104)
    shadow(img, "rect", [0, BFL, W, BFL + 6], 0.5, 3)
    rug(R, img, 60, 430, 30, 230, hx("6a4a5a"), hx("3a2a44"), hx("d8b878"), seed=105)
    if bed:
        _bed(img, R, bed)
    if screen:  # the folding screen: its own y-sorted sprite, so Micah can stand behind it
        _folding_screen(img)
    # ---- light: firelight low on the left, the lamp's pink pool by the bed, moonlight from the window ----
    light(img, "polygon", [(gx0, gy0), (gx1, gy0), (330, H), (200, H)], hx("5a6ab0"), 0.22, 12)
    pools = [((fx0 + fx1) / 2, BFL - 10, 110, 70, (1.3, 0.85, 0.55), 1.0), (lx, ly - 10, 60, 45, (1.15, 0.95, 0.8), 0.75),
             (265, 80, 50, 70, (0.7, 0.75, 1.05), 0.5)]
    img = grade(img, (0.42, 0.4, 0.6), pools, em)
    light(img, "ellipse", [fx0 + 10, BFL - 40, fx1 - 10, BFL + 6], hx("f08040"), 0.3, 8)
    light(img, "ellipse", [lx - 13, ly - 32, lx + 13, ly - 8], hx("f0a070"), 0.16, 5)
    light(img, "polygon", [(lx - 7, ly - 13), (lx + 7, ly - 13), (lx + 14, ly + 2), (lx - 14, ly + 2)], hx("ffc890"),
          0.14, 3)
    vignette(img, 0.5, (10, 6, 16), 40)
    if bed == "eleanor":
        _restamp_white_sheet(img, R)
    return img


NIGHTSTAND_CANDLESTICK = (409, 30, 12)  # room-space foot of the candlestick, clear of the bed's footpost


def _nightstand_candlestick(d, x, y):
    """A short brass chamber candlestick, unlit: a domed foot, a knopped stem, a wide drip tray, a ring handle and a
    stub of ivory candle, all outlined dark so it reads against the lamp and the rose wall."""
    x, y = round(x), round(y)
    br, br_l, br_d, out = hx("d0a840"), hx("fce48a"), hx("7a5a1c"), hx("2a1808")
    d.ellipse([x - 4, y - 3, x + 3, y + 1], fill=br, outline=out)
    d.line([(x - 2, y - 2), (x, y - 2)], fill=br_l)
    d.rectangle([x - 2, y - 10, x + 1, y - 3], fill=br, outline=out)
    d.line([(x - 1, y - 9), (x - 1, y - 4)], fill=br_l)
    d.rectangle([x - 3, y - 7, x + 2, y - 6], fill=br_d, outline=out)
    d.arc([x + 2, y - 11, x + 6, y - 6], 270, 90, fill=out)
    d.ellipse([x - 5, y - 13, x + 4, y - 10], fill=br, outline=out)
    d.line([(x - 3, y - 12), (x + 1, y - 12)], fill=br_l)
    d.rectangle([x - 2, y - 21, x + 1, y - 13], fill=hx("f4ecd8"), outline=out)
    d.line([(x - 1, y - 20), (x - 1, y - 14)], fill=hx("fffaf0"))
    d.point((x + 1, y - 18), fill=hx("e0d0b0"))
    d.line([(x - 1, y - 23), (x - 1, y - 22)], fill=hx("1a0e04"))


def _cut_sprite(variant_px, base_px, name, folder="rooms"):
    """Everything that differs from the empty room, as an RGBA sprite; returns its top-left."""
    a = np.asarray(variant_px.convert("RGB")).astype(np.int16)
    b = np.asarray(base_px.convert("RGB")).astype(np.int16)
    mask = (np.abs(a - b).sum(axis=2) > 0)
    rgba = np.dstack([a.astype(np.uint8), (mask * 255).astype(np.uint8)])
    im = Image.fromarray(rgba, "RGBA")
    bb = im.getbbox()
    save(im.crop(bb), folder, name + ".png")
    print(f"{name} at ({bb[0]}, {bb[1]}) size {bb[2] - bb[0]}x{bb[3] - bb[1]}")
    return bb


def build_bedroom():
    base = paint_bedroom()
    v = {"eleanor": paint_bedroom("eleanor"), "empty": paint_bedroom("empty")}
    screen = paint_bedroom(screen=True)
    pal = bedroom_palette(base, v["eleanor"], v["empty"], screen)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_bedroom.png")
    occupied, empty = pixelize(v["eleanor"], pal), pixelize(v["empty"], pal)
    _cut_sprite(occupied, px, "mansion_bed")
    _cut_sprite(empty, px, "mansion_bed_empty")
    _cut_sprite(pixelize(screen, pal), px, "mansion_bedroom_screen")
    _cut_sprite(pixelize(paint_bedroom(candlestick=True), pal), px, "mansion_candlestick", "sprites")
    bed_fire_strip(pal)
    eleanor_rise_strip(occupied, empty)
    return px, v


# Where Eleanor's actor stands while she gets out of bed (her feet, room pixels), and the room box the strip covers.
ELEANOR_RISE_AT = (382, 226)
ELEANOR_RISE_BOX = (300, 104, 424, 230)


def eleanor_rise_strip(occupied, empty):
    """Eleanor getting out of the walnut bed, played by her actor at ELEANOR_RISE_AT as the bed swaps to the empty one.
    Frame 0 is everything the occupied bed adds to the empty one (her, sitting up, and the sheet over the mattress), so
    it starts pixel-for-pixel where the bed sprite leaves off; she gathers the sheet to her, sits on the front edge
    wrapped in it, slides down onto her feet and turns, the last frame being eleanor_sheet's idle frame. Drawn facing
    left in room pixels, then mirrored so the actor (facing left, so flipped) shows it the right way round."""
    from PIL import ImageOps
    from .sprites import ELEANOR_SHEET, figure, pose, _arms, NPC_W, FH, action_strip
    x0, y0, x1, y1 = ELEANOR_RISE_BOX
    w, h = x1 - x0, y1 - y0
    px, py = ELEANOR_RISE_AT
    a = np.asarray(occupied.convert("RGB")).astype(np.int16)
    b = np.asarray(empty.convert("RGB")).astype(np.int16)
    added = (np.abs(a - b).sum(axis=2) > 0)
    ys, xs = np.mgrid[0:a.shape[0], 0:a.shape[1]]

    def in_bed(keep):
        mask = added & keep
        rgba = np.dstack([a.astype(np.uint8), (mask * 255).astype(np.uint8)])
        # where the sheet has been pulled away, its new edge is a shaded fold
        edge = mask & ~np.roll(keep, 1, axis=1) & ~np.all(keep)
        rgba[edge, :3] = MANSION_SHEET_FOLD
        return Image.fromarray(rgba, "RGBA").crop((x0, y0, x1, y1))

    head_in_bed = (376 - x0, 150 - y0)
    arms = _arms("clutch")
    sheet_col = tuple(int(c, 16) for c in (ELEANOR_SHEET["torso"][i:i + 2] for i in (0, 2, 4)))

    def standing(ps, lift=0, wrap=False):
        img = Image.new("RGBA", (w, h))
        fig = ImageOps.mirror(figure(ELEANOR_SHEET, ps, NPC_W, FH))
        if lift:  # sitting up on the mattress: no floor shadow under her
            fa = np.asarray(fig).copy()
            fa[fa[..., 3] < 255] = 0
            fig = Image.fromarray(fa, "RGBA")
        if wrap:  # the sheet hangs over her lap and knees in one piece, hiding the legs down to the ankles
            fa = np.asarray(fig).copy()
            rows = np.nonzero((fa[..., 3] == 255).any(axis=1))[0]
            lit, side = np.array(sheet_col), np.array(MANSION_SHEET_SIDE)
            rgb = fa[..., :3].astype(int)
            skin = (fa[..., 3] == 255) & (rgb[..., 0] - rgb[..., 2] > 40)
            # start below her hands, which hold the sheet at her chest
            top = max(y for y in range(40, 76) if skin[y].any()) + 1
            for y in range(top, rows.max() - 2):
                xs_ = np.nonzero(fa[y, :, 3] == 255)[0]
                if len(xs_) < 2:
                    continue
                a_, b_ = xs_.min(), xs_.max()
                for x in range(a_, b_ + 1):
                    col = side if x in (a_, b_) or (x - a_) % 5 == 2 else lit
                    fa[y, x] = tuple(int(c) for c in col) + (255,)
            fig = Image.fromarray(fa, "RGBA")
        fx, fy = px - NPC_W // 2 - x0, py - FH + 3 - y0 - lift
        img.alpha_composite(fig, (fx, fy))
        return img, (fx + NPC_W - 1 - NPC_W // 2, fy + 18)

    frames = [
        (in_bed(np.ones_like(added)), head_in_bed),
        # the sheet drawn up off the foot of the bed toward her, its trailing edge slanting back over the mattress
        (in_bed(xs - 352 > (ys - 170) * 0.6), head_in_bed),
        # sitting on the mattress's front edge, the sheet clutched to her, feet hanging
        standing(pose(16, arms=arms, legs={1: (85, 90, 0), -1: (82, 88, 0)}), lift=20, wrap=True),
        standing(pose(16, arms=arms, legs={1: (50, 60, 0), -1: (48, 58, 0)}, lean=8), wrap=True),
        standing(pose(16, arms=arms)),
        standing(pose(35, arms=arms)),
    ]
    stored = [(ImageOps.mirror(img), (w - head[0], head[1])) for img, head in frames]
    action_strip("eleanor_mansion_rise", stored, [0.175, 0.15, 0.2, 0.14, 0.125, 0.15], anchor=(w - (px - x0), py - y0))
    # and back under the sheet: the same frames played backwards, from her standing turn to lying in the bed
    action_strip("eleanor_mansion_return", stored[::-1], [0.15, 0.125, 0.14, 0.2, 0.15, 0.175],
                 anchor=(w - (px - x0), py - y0))
    return frames


def bed_fire_strip(pal):
    """The hearth's flames and smoke as a strip of BED_FIRE_FRAMES crops of BED_FIRE_BOX, frame 0 matching the
    background, played by a LoopStrip."""
    x0, y0, x1, y1 = BED_FIRE_BOX
    strip = Image.new("RGB", ((x1 - x0) * BED_FIRE_FRAMES, y1 - y0))
    for i in range(BED_FIRE_FRAMES):
        strip.paste(pixelize(paint_bedroom(fire_t=i / BED_FIRE_FRAMES), pal).crop(BED_FIRE_BOX), (i * (x1 - x0), 0))
    save(strip, "rooms", "mansion_bedroom_fire.png")
    print("mansion_bedroom_fire at", BED_FIRE_BOX[:2], BED_FIRE_FRAMES, "frames")
