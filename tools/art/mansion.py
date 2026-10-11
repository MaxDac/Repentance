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
        for y in range(y0, y1 + 1):
            d.line([(x0, y), (x1, y)], fill=mix(hx("fff0a0"), hx("f06818"), (y - y0) / (y1 - y0)))
        for i in range(4):
            fx = x0 + 2 + i * (w - 4) // 3
            d.polygon([(fx - 4, y1), (fx + rnd.randint(-2, 2), y0 + 4 + rnd.randint(0, 12)), (fx + 4, y1)], fill=hx("fffce0"))
        d.polygon([(x0 - 6, y0 - 12), (x1 + 6, y0 - 12), (cx + 10, y0 - 34), (cx - 8, y0 - 30)], fill=hx("201814"))
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


def paint_exterior(moved=False, wedged=False, opened=False, fire=False):
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
    for px0 in (0, 26):
        d.rectangle([px0, 132, px0 + 6, 214], fill=STONE)
        d.line([(px0 + 6, 132), (px0 + 6, 214)], fill=STONE_D)
        d.rectangle([px0 - 1, 130, px0 + 7, 133], fill=STONE_L)
        d.ellipse([px0, 122, px0 + 6, 129], fill=STONE_L, outline=STONE_D)
    vgrad(img, (7, 140, 25, 214), hx("3a4a6a"), hx("40603e"))  # the moonlit garden glimpsed through the bars
    d.ellipse([4, 150, 18, 186], fill=hx("1e3020"))
    d.ellipse([14, 162, 30, 192], fill=hx("26382a"))
    d.polygon([(7, 214), (25, 214), (20, 196), (12, 196)], fill=hx("8a8676"))
    for x in range(8, 26, 3):
        d.line([(x, 146), (x, 213)], fill=hx("121212"))
        d.polygon([(x - 1, 146), (x, 142), (x + 1, 146)], fill=hx("121212"))
    for y in (152, 180, 208):
        d.line([(7, y), (25, y)], fill=hx("121212"))
    d.arc([8, 138, 24, 154], 180, 360, fill=hx("121212"))
    d.rectangle([22, 176, 24, 180], fill=hx("6a6050"))
    # box hedge in front of the wall, a galvanised ash can by the plinth
    for i in range(10):
        x = FX + 2 + i * 4
        d.ellipse([x - 5, 192, x + 5, 214], fill=rnd.choice([hx("1a2e1a"), hx("223a1e"), hx("1e3220")]))
    for _ in range(30):
        d.point((rnd.randint(FX - 2, FX + 42), rnd.randint(194, 210)), fill=hx("3e5a32"))
    d.rectangle([108, 186, 128, 210], fill=hx("5a5c5e"), outline=hx("1e2022"))
    for y in (192, 202):
        d.line([(108, y), (128, y)], fill=hx("3a3c3e"))
    d.line([(110, 186), (110, 210)], fill=hx("8a8c8e"))
    d.ellipse([106, 182, 130, 189], fill=hx("6a6c6e"), outline=hx("1e2022"))
    d.rectangle([115, 180, 121, 183], fill=hx("3a3c3e"))
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
        d = ImageDraw.Draw(img)
        rf = random.Random(7)
        for _ in range(40):  # sparks
            x, y = rf.randint(40, W - 1), rf.randint(0, 120)
            d.point((x, y), fill=hx("ffd070"))
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
    save(pixelize(v["fire"], palette_of(v["fire"], 124)), "rooms", "mansion_exterior_fire.png")
    return px, v


# ------------------------------------------------------------------------------------------------ KITCHEN

KFL = 204  # where the back wall meets the floor
CANDLE = (322, 150)  # the flame, roughly; recomputed from the table in paint_kitchen
TILE, TILE_D, PLASTER = hx("d8d4c4"), hx("9a978a"), hx("c8bc9a")


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
    # a kitchen clock over the back door and a calendar by the dresser
    d.ellipse([36, 44, 60, 68], fill=hx("4a3220"), outline=hx("1a120a"))
    d.ellipse([39, 47, 57, 65], fill=hx("ece4cc"))
    for k in range(12):
        t = k * math.pi / 6
        d.point((48 + 7 * math.cos(t), 56 + 7 * math.sin(t)), fill=hx("2a2a2a"))
    d.line([(48, 56), (48, 50)], fill=hx("1a1a1a"))
    d.line([(48, 56), (52, 58)], fill=hx("1a1a1a"))
    d.rectangle([47, 68, 49, 82], fill=hx("4a3220"))
    d.ellipse([44, 80, 52, 88], fill=hx("c8a048"))
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
    # ---- the back door to the yard, four panes of moonlit glass, a bolt, the cook's apron on a hook ----
    bx0, bx1, by0 = 24, 72, 98
    d.rectangle([bx0 - 4, by0 - 4, bx1 + 4, KFL], fill=hx("5a4a36"))
    d.rectangle([bx0, by0, bx1, KFL], fill=hx("4a3a28"))
    d.line([(bx0, by0), (bx0, KFL)], fill=hx("2a2014"))
    vgrad(img, (bx0 + 5, by0 + 5, bx1 - 5, by0 + 44), hx("3a4a7a"), hx("6a7aa8"))
    ed.rectangle([bx0 + 5, by0 + 5, bx1 - 5, by0 + 44], fill=150)
    d.ellipse([bx0 + 28, by0 + 9, bx0 + 36, by0 + 17], fill=hx("eeeed8"))
    ed.ellipse([bx0 + 28, by0 + 9, bx0 + 36, by0 + 17], fill=255)
    d.polygon([(bx0 + 5, by0 + 44), (bx0 + 5, by0 + 32), (bx0 + 16, by0 + 26), (bx0 + 30, by0 + 34), (bx1 - 5, by0 + 28),
               (bx1 - 5, by0 + 44)], fill=hx("1a2a24"))  # the garden's trees through the glass
    d.line([(48, by0 + 5), (48, by0 + 44)], fill=hx("4a3a28"), width=2)
    d.line([(bx0 + 5, by0 + 24), (bx1 - 5, by0 + 24)], fill=hx("4a3a28"), width=2)
    for a, b in ((by0 + 52, by0 + 76), (by0 + 82, KFL - 8)):
        for px0, px1 in ((bx0 + 5, 46), (50, bx1 - 5)):
            d.rectangle([px0, a, px1, b], fill=hx("40321f"), outline=hx("2a2014"))
            d.line([(px0, b), (px1, b)], fill=hx("6a5638"))
    d.rectangle([bx1 - 7, by0 + 54, bx1 - 4, by0 + 58], fill=hx("c8a048"))
    d.rectangle([bx0 + 2, by0 + 48, bx0 + 12, by0 + 50], fill=hx("6a6a70"))  # bolt
    d.rectangle([80, 116, 82, 118], fill=hx("6a6a70"))
    d.polygon([(76, 118), (88, 118), (92, 170), (72, 170)], fill=hx("dcd8c8"))  # apron
    d.line([(78, 140), (88, 140)], fill=hx("a8a494"))
    d.line([(76, 118), (72, 170)], fill=hx("a8a494"))
    # a broom propped in the corner of the frame
    d.line([(90, 120), (96, KFL - 12)], fill=hx("8a6a40"), width=2)
    d.polygon([(90, KFL - 14), (102, KFL - 14), (106, KFL), (88, KFL)], fill=hx("a88a50"))
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
    p = R.P(rx0 + 86, 74, 12)  # a kettle on the back burner
    d.ellipse([p[0] - 8, p[1] - 12, p[0] + 8, p[1] + 1], fill=hx("8a8a90"), outline=hx("3a3a3e"))
    d.arc([p[0] - 5, p[1] - 18, p[0] + 5, p[1] - 8], 180, 360, fill=hx("2a2a2c"))
    d.line([(p[0] + 7, p[1] - 6), (p[0] + 13, p[1] - 10)], fill=hx("8a8a90"), width=2)
    d.point((p[0] - 4, p[1] - 9), fill=hx("e8e8f0"))
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
    d.line([(244, 60), (258, 60)], fill=hx("4a3a28"), width=2)
    for i, (x, r) in enumerate(((246, 6), (254, 5))):
        d.line([(x, 60), (x, 66)], fill=hx("6a5a3a"))
        d.ellipse([x - r, 66, x + r, 66 + 2 * r], fill=hx("b8683a"), outline=hx("5a2a14"))
        d.ellipse([x - r + 2, 68, x - r + 4, 70], fill=hx("f0b080"))
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
    for row, (ya, yb) in enumerate(((70, 100), (102, 132))):  # plates standing on the shelves, cups on hooks
        for i, x in enumerate(range(dx0 + 12, dx1 - 14, 13)):
            c = hx("ece8dc") if (i + row) % 3 else hx("dcdcf0")
            d.ellipse([x, yb - 22, x + 11, yb - 1], fill=c, outline=hx("8a8676"))
            d.ellipse([x + 3, yb - 19, x + 8, yb - 4], outline=hx("3a5a9a") if (i + row) % 3 == 0 else hx("b8b0a0"))
    for i, x in enumerate(range(dx0 + 14, dx1 - 12, 11)):
        d.line([(x, 134), (x, 136)], fill=hx("8a7a5a"))
        d.rectangle([x - 3, 137, x + 3, 142], fill=hx("e8e4d8"), outline=hx("8a8676"))
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
    d.rectangle([gx0 - 5, gy0 - 5, gx1 + 5, KFL], fill=hx("6a5038"))
    d.line([(gx0 - 5, gy0 - 5), (gx1 + 5, gy0 - 5)], fill=hx("9a7a54"))
    vgrad(img, (gx0, gy0, gx1, KFL), hx("2e5a3a"), hx("224a2e"))
    noise(img, (gx0, gy0, gx1, KFL), 6, 84)
    for x in (gx0 + 3, gx1 - 3):
        for y in range(gy0 + 3, KFL - 1, 6):
            d.point((x, y), fill=hx("d8b860"))
    for y in (gy0 + 3, gy0 + 52, KFL - 3):
        for x in range(gx0 + 3, gx1 - 2, 6):
            d.point((x, y), fill=hx("d8b860"))
    d.rectangle([gx0 + 6, gy0 + 40, gx0 + 12, gy0 + 64], fill=hx("c8a048"), outline=hx("6a5420"))  # brass push plate
    d.line([(gx0 + 7, gy0 + 41), (gx0 + 7, gy0 + 63)], fill=hx("f0d890"))
    d.rectangle([396, 22, 472, 78], fill=hx("5a3e24"), outline=hx("2a1c10"))
    d.rectangle([398, 24, 470, 30], fill=hx("7a5634"))
    rooms = 8
    for i in range(rooms):
        x = 402 + i * 9
        d.rectangle([x - 1, 34, x + 5, 40], fill=hx("e8dcbc"))
        d.line([(x + 2, 42), (x + 2, 52)], fill=hx("2a2014"))
        d.polygon([(x - 1, 60), (x + 2, 52), (x + 5, 60)], fill=hx("b89040"))
        d.point((x + 1, 55), fill=hx("f0d890"))
        d.rectangle([x + 1, 62, x + 3, 70], fill=hx("1a1a1a") if i != 5 else hx("a02020"))  # one flag still down
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
    # ---- light: moonlight through the back door's glass, the candle if it's lit ----
    light(img, "polygon", [(bx0 + 5, by0 + 5), (bx1 - 5, by0 + 5), (150, H), (40, H)], hx("5a6aa8"), 0.35, 8)
    fxx, fyy = flame
    pools = [(48, 200, 70, 70, (0.62, 0.7, 1.0), 0.6)]
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
    v = {"lit": paint_kitchen(lit=True), "gas": paint_kitchen(gas=True)}
    pal = palette_of(Image.blend(Image.blend(base, v["lit"], 0.4), v["gas"], 0.3), 124)
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_kitchen.png")
    fx, fy = paint_kitchen.flame
    print("kitchen flame", paint_kitchen.flame, "taps", paint_kitchen.taps)
    overlay(v["gas"], px, pal, paint_kitchen.taps, "mansion_kitchen_gas")
    overlay(v["lit"], px, pal, (0, 0, W, H), "mansion_kitchen_candle")
    return px, v


# ------------------------------------------------------------------------------------------------ STUDY

SFL = 204
OAK, OAK_D, OAK_L = hx("5a3a20"), hx("2e1c0e"), hx("7a5432")


def bookshelf(img, rnd, x0, y0, x1, y1, shelf=24):
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
    while y + shelf < y1 - 18:
        d.rectangle([x0 + 4, y, x1 - 4, y + shelf - 3], fill=hx("140a04"))
        x = x0 + 5
        while x < x1 - 6:
            r = rnd.random()
            if r < 0.06 and x < x1 - 16:  # a little bronze, a clock, a gap
                d.polygon([(x, y + shelf - 3), (x + 10, y + shelf - 3), (x + 7, y + shelf - 12), (x + 3, y + shelf - 12)],
                          fill=hx("6a5a2a"))
                d.ellipse([x + 2, y + shelf - 18, x + 8, y + shelf - 11], fill=hx("8a7a3a"))
                x += 12
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
    d.polygon([(x0, y1 - 6), (x0 + 8, y1 - 10), (x0 + 25, y1 - 3), (x1, y1 - 2), (x1, y1), (x0, y1)],
              fill=hx("31342e"))
    d.rectangle(box, outline=hx("302820"))
    d.rectangle([x0 + 12, y1 + 6, x1 - 12, y1 + 9], fill=hx("c8a048"))
    d.line([(x0 + 15, y1 + 7), (x1 - 15, y1 + 7)], fill=hx("624a24"))


def paint_study(left=False, right=False, docs=True, closet=False):
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
    bookshelf(img, rnd, 78, 30, 150, SFL)
    d = ImageDraw.Draw(img)
    # ---- the closet: a tall panelled door flush in the panelling ----
    wx0, wx1, wy0, wy1 = 160, 214, 70, SFL
    d.rectangle([wx0 - 4, wy0 - 8, wx1 + 4, wy1], fill=OAK_L)
    d.rectangle([wx0 - 6, wy0 - 11, wx1 + 6, wy0 - 6], fill=hx("8a6440"))
    d.line([(wx0 - 6, wy0 - 6), (wx1 + 6, wy0 - 6)], fill=OAK_D)
    if closet:
        d.rectangle([wx0, wy0, wx1, wy1], fill=hx("0e0804"))
        shadow(img, "rect", [wx0, wy0, wx1, wy1], 0.4, 4)
        d = ImageDraw.Draw(img)
        d.line([(wx0 + 2, wy0 + 10), (wx1 - 2, wy0 + 10)], fill=hx("8a8a80"))
        for i, (c, w2) in enumerate((("2a2a32", 9), ("4a3a2a", 8), ("5a1e26", 7))):
            cx = wx0 + 12 + i * 15
            d.polygon([(cx - 3, wy0 + 10), (cx + 3, wy0 + 10), (cx + w2, wy0 + 18), (cx + w2 + 1, wy0 + 84),
                       (cx - w2 - 1, wy0 + 84), (cx - w2, wy0 + 18)], fill=hx(c))
            d.line([(cx, wy0 + 12), (cx, wy0 + 84)], fill=mul(hx(c), 0.6))
            d.line([(cx - w2, wy0 + 18), (cx - w2 - 1, wy0 + 84)], fill=mul(hx(c), 1.4))
        d.rectangle([wx0 + 4, wy0 + 2, wx1 - 4, wy0 + 6], fill=hx("2a1e14"))
        d.ellipse([wx0 + 8, wy0 - 2, wx0 + 24, wy0 + 4], fill=hx("3a3a3a"))  # a homburg on the shelf
        d.rectangle([wx0 + 6, wy1 - 18, wx1 - 6, wy1 - 2], fill=hx("4a3a28"), outline=hx("1a120a"))  # a valise
        d.line([(wx0 + 20, wy1 - 18), (wx0 + 20, wy1 - 22), (wx0 + 32, wy1 - 22), (wx0 + 32, wy1 - 18)], fill=hx("2a1e14"))
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
    d.ellipse([292, 40, 304, 52], fill=hx("f4f0d8"))
    light(img, "ellipse", [278, 28, 318, 64], hx("6a78b0"), 0.4, 6)
    d = ImageDraw.Draw(img)
    vgrad(img, (gx0, 78, gx1, gy1), hx("1a2440"), hx("0e1428"))  # Lake Michigan
    d.line([(gx0, 78), (gx1, 78)], fill=hx("3a4470"))
    for x in range(gx0 + 2, 270, 5):  # the lights of the shore drive, far off
        d.point((x, 77), fill=hx("e8c070"))
    ed.rectangle([gx0, gy0, gx1, gy1], fill=170)
    d.rectangle([278, gy0, 281, gy1], fill=OAK_L)
    d.rectangle([gx0, 66, gx1, 69], fill=OAK_L)
    for x in range(gx0, gx1, 13):
        d.line([(x, gy0), (x, 66)], fill=OAK)
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
    for i, (x, c, hgt) in enumerate(((354, "8a4a1a", 14), (366, "c8a060", 12), (380, "6a2a2a", 16))):
        p = R.P(x, 40, 10)
        d.rectangle([p[0] - 3, p[1] - hgt + 4, p[0] + 3, p[1]], fill=hx(c))
        d.rectangle([p[0] - 1, p[1] - hgt, p[0] + 1, p[1] - hgt + 4], fill=hx(c))
        d.point((p[0] - 2, p[1] - hgt + 6), fill=hx("f0e0c0"))
    p = R.P(398, 40, 10)  # soda siphon and a tray of glasses
    d.rectangle([p[0] - 3, p[1] - 14, p[0] + 3, p[1]], fill=hx("4a6a8a"))
    d.rectangle([p[0] - 2, p[1] - 18, p[0] + 2, p[1] - 14], fill=hx("b8b8c0"))
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
    # on the desk: a green banker's lamp, blotter, inkstand, telephone
    p = R.P(318, DH, 30)
    d.rectangle([p[0] - 1, p[1] - 14, p[0] + 1, p[1]], fill=hx("a8842e"))
    d.ellipse([p[0] - 5, p[1] - 2, p[0] + 5, p[1] + 2], fill=hx("a8842e"))
    d.polygon([(p[0] - 12, p[1] - 12), (p[0] + 6, p[1] - 12), (p[0] + 4, p[1] - 18), (p[0] - 10, p[1] - 18)], fill=hx("1e5a34"))
    d.line([(p[0] - 10, p[1] - 18), (p[0] + 4, p[1] - 18)], fill=hx("5aa070"))
    p = R.P(270, DH, 34)
    d.rectangle([p[0] - 16, p[1] - 3, p[0] + 16, p[1] + 2], fill=hx("1a2a1a"))
    d.rectangle([p[0] - 12, p[1] - 2, p[0] + 10, p[1] + 1], fill=hx("e0d8c0"))
    p = R.P(240, DH, 28)
    d.rectangle([p[0] - 6, p[1] - 3, p[0] + 6, p[1]], fill=hx("6a5018"))
    d.rectangle([p[0] - 4, p[1] - 6, p[0] - 1, p[1] - 3], fill=hx("1a1a3a"))
    d.line([(p[0] + 2, p[1] - 3), (p[0] + 6, p[1] - 12)], fill=hx("e8e0d0"))  # quill
    p = R.P(296, DH, 28)  # candlestick telephone
    d.ellipse([p[0] - 3, p[1] - 1, p[0] + 3, p[1] + 1], fill=hx("1a1a1a"))
    d.line([(p[0], p[1]), (p[0], p[1] - 12)], fill=hx("1a1a1a"), width=2)
    d.ellipse([p[0] - 2, p[1] - 15, p[0] + 2, p[1] - 11], fill=hx("1a1a1a"))
    d.line([(p[0] + 2, p[1] - 9), (p[0] + 5, p[1] - 6)], fill=hx("1a1a1a"), width=2)
    # ---- a globe on its stand, front right ----
    gp = R.P(430, 0, 70)
    gx, gy = gp
    d.line([(gx - 8, gy), (gx, gy - 14), (gx + 8, gy)], fill=OAK_D, width=2)
    d.line([(gx, gy - 14), (gx, gy - 22)], fill=OAK_D, width=2)
    d.ellipse([gx - 13, gy - 48, gx + 13, gy - 22], fill=hx("8a7a4a"), outline=hx("3a2a10"))
    d.polygon([(gx - 8, gy - 42), (gx - 2, gy - 44), (gx + 2, gy - 36), (gx - 4, gy - 30), (gx - 9, gy - 34)], fill=hx("5a6a3a"))
    d.polygon([(gx + 4, gy - 30), (gx + 10, gy - 34), (gx + 9, gy - 26)], fill=hx("5a6a3a"))
    d.arc([gx - 16, gy - 51, gx + 16, gy - 19], 200, 340, fill=hx("a8842e"), width=2)
    # ---- light: the moon through the window across the desk and rug ----
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
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
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
SHEET = (126, 124, 117)
SHEET_LIT = (151, 146, 135)
SHEET_FOLD = (77, 79, 80)
SHEET_SIDE = (99, 98, 93)


def _bare_eleanor():
    from .sprites import ELEANOR, figure, pose, _arms, FW, FH
    skin = ELEANOR["skin"]
    spec = dict(ELEANOR, torso=skin, pelvis=skin, sleeves=skin, coat=None, neckline=None, decals=[])
    f = figure(spec, pose(16, arms=_arms("side")), FW, FH).convert("RGBA")
    f.putalpha(f.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    bb = f.getbbox()
    return f.crop((bb[0], bb[1], bb[2], bb[1] + 44))


def _sheet_on(figure, fill, hem):
    w, h = figure.size
    mask = Image.new("L", figure.size)
    ImageDraw.Draw(mask).polygon([(0, 20), (w // 2, 22), (w - 1, 19), (w - 1, h), (0, h)], fill=255)
    yy, xx = np.mgrid[:h, :w].astype(float)
    depth = np.clip((yy - 20) / (h - 20), 0, 1)
    # Soft gathers fan out from the held hem rather than three parallel ink strokes.
    crease_a = w * 0.67 - depth * w * 0.48 + np.sin(depth * 3) * 1.5
    crease_b = w * 0.8 + depth * w * 0.1
    shade = (9 * (1 - depth) - 13 * depth
             - 17 * np.exp(-((xx - crease_a) / 1.5) ** 2)
             - 11 * np.exp(-((xx - crease_b) / 2.0) ** 2)
             + 8 * np.exp(-((xx - crease_a - 2.5) / 2.0) ** 2))
    rgb = np.clip(np.array(fill) + shade[:, :, None], 0, 255).astype("uint8")
    sheet = Image.fromarray(rgb).convert("RGBA")
    sheet.putalpha(ImageChops.multiply(mask, figure.getchannel("A")))
    d = ImageDraw.Draw(sheet)
    d.line([(1, 21), (w // 2, 23), (w - 2, 20)], fill=hem + (255,))
    sheet.putalpha(ImageChops.multiply(sheet.getchannel("A"), figure.getchannel("A")))
    return sheet


def _eleanor_in_bed():
    """Eleanor sitting up against the pillows, bare shoulders; the sheet covers her from the chest down."""
    figure = _bare_eleanor()
    return Image.alpha_composite(figure, _sheet_on(figure, SHEET, SHEET_LIT))


def _eleanor_origin(R):
    from PIL import ImageOps
    el = ImageOps.mirror(_bare_eleanor())
    hp = R.P(BED["x1"] - 16, BED["top"], (BED["z0"] + BED["z1"]) / 2)
    return int(hp[0] - el.width // 2), int(hp[1] - el.height + 10)


def _restamp_white_sheet(img, R):
    """The lamp pool tans the painted sheet into her skin. Put the linen back, white, after the light."""
    from PIL import ImageOps
    figure = ImageOps.mirror(_eleanor_in_bed())
    img.paste(figure, _eleanor_origin(R), figure)


def bedroom_palette(base, occupied, empty):
    pal = palette_of(Image.blend(Image.blend(base, occupied, 0.4), empty, 0.3), 124)
    for color in (SHEET, SHEET_LIT, SHEET_FOLD, SHEET_SIDE):
        if color not in pal:
            pal.append(color)
    return pal


def _bed(img, R, who):
    """The walnut bed, side-on with its head to the right by the nightstand: a tall carved headboard, a low footboard,
    pillows and a rose satin coverlet hanging to the rail. who: "eleanor" (sitting up against the pillows) or "empty"."""
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
    cover_end = x1 - 18 if who == "eleanor" else x1 - 44
    if who == "eleanor":
        from PIL import ImageOps
        el = ImageOps.mirror(_eleanor_in_bed())
        img.paste(el, _eleanor_origin(R), el)
        d = ImageDraw.Draw(img)
    # the coverlet over the top and down the front, a turned-down sheet at its head
    ce = cover_end
    R.quad(img, [(x0 - 1, top + 2, z0 + 1), (ce, top + 2, z0 + 1), (ce, top + 1, z1 + 1), (x0 - 1, top + 1, z1 + 1)], hx("a85a66"))
    R.quad(img, [(ce - 6, top + 2.5, z0 + 1), (ce, top + 2.5, z0 + 1), (ce, top + 1.5, z1 + 1), (ce - 6, top + 1.5, z1 + 1)], hx("f4f0e6"))
    R.quad(img, [(x0 - 1, top + 1, z1 + 1), (ce, top + 1, z1 + 1), (ce, 4, z1 + 1), (x0 - 1, 4, z1 + 1)], hx("8a4450"))
    R.quad(img, [(ce - 6, top + 1.5, z1 + 1), (ce, top + 1.5, z1 + 1), (ce, 8, z1 + 1), (ce - 6, 10, z1 + 1)], hx("e4dccc"))
    d = ImageDraw.Draw(img)
    a, b = R.P(x0 - 1, 4, z1 + 1), R.P(ce, 4, z1 + 1)
    d.line([a, b], fill=GILT)
    for x in range(int(a[0]) + 1, int(b[0]), 2):
        d.point((x, a[1] + 1), fill=hx("e0c070"))
    n = max(2, int((ce - x0) / 12))
    for k in range(n):  # satin folds
        xa = x0 + 6 + k * (ce - x0 - 10) / n
        d.line([R.P(xa, top - 2, z1 + 1), R.P(xa + 3, 6, z1 + 1)], fill=hx("6a2a36"))
        d.line([R.P(xa + 2, top - 3, z1 + 1), R.P(xa + 5, 8, z1 + 1)], fill=hx("c87a84"))
    if who == "empty":  # the sheet went with her; the coverlet thrown back in a heap
        R.quad(img, [(ce, top + 0.5, z1 + 1), (x1, top + 0.5, z1 + 1), (x1, 8, z1 + 1), (ce, 8, z1 + 1)], hx("ddd4c2"))
        d = ImageDraw.Draw(img)
        a = R.P(ce - 4, top + 6, z1 - 6)
        d.ellipse([a[0] - 10, a[1] - 3, a[0] + 8, a[1] + 7], fill=hx("b0606c"), outline=hx("6a2a36"))
        d.line([R.P(ce + 4, top + 1, z1 - 4), R.P(x1 - 22, top + 1, z0 + 6)], fill=hx("c0b6a2"))
        d.line([R.P(ce + 2, 20, z1 + 1), R.P(ce + 8, 10, z1 + 1)], fill=hx("c0b6a2"))
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
    R.line(img, (x0 - 4, 12, z1 + 4), (x1 + 4, 12, z1 + 4), WAL_D)  # the side rail under the coverlet's hem
    R.line(img, (x0 - 2, 4, z1 + 3), (x1 + 2, 4, z1 + 3), WAL)

def paint_bedroom(bed=None):
    """The room; bed is None (the room alone), "eleanor" or "empty"."""
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
    d.polygon([(fx0 + 22, BFL - 12), (fx1 - 24, BFL - 16), (fx1 - 22, BFL - 12), (fx0 + 24, BFL - 9)], fill=hx("3a2014"))  # logs
    d.ellipse([fx1 - 26, BFL - 17, fx1 - 21, BFL - 11], fill=hx("c86a3a"))
    for k, (dx, hgt) in enumerate(((2, 9), (7, 15), (12, 11), (17, 19), (22, 8), (27, 13))):
        cx = fx0 + 20 + dx
        d.polygon([(cx - 3, BFL - 12), (cx - 1, BFL - 12 - hgt * 0.6), (cx + 1, BFL - 12 - hgt), (cx + 3, BFL - 12)], fill=hx("e86a24"))
        d.polygon([(cx - 1, BFL - 12), (cx + 1, BFL - 12 - hgt * 0.55), (cx + 2, BFL - 12)], fill=hx("ffd070"))
    d.rectangle([fx0 + 20, BFL - 8, fx1 - 20, BFL - 5], fill=hx("c84a18"))
    ed.rectangle([fx0 + 18, BFL - 24, fx1 - 18, BFL - 4], fill=230)
    R.box(img, fx0 - 2, fx1 + 2, 0, 4, 10, 16, hx("b8903a"), top=hx("e0c060"))  # brass fender
    d = ImageDraw.Draw(img)
    cx = (fx0 + fx1) / 2  # clock and candlesticks on the mantel shelf
    d.rectangle([cx - 7, 90, cx + 7, 102], fill=hx("b8903a"))
    d.ellipse([cx - 5, 88, cx + 5, 98], fill=hx("f0ead8"), outline=hx("6a5018"))
    d.line([(cx, 93), (cx, 90)], fill=hx("1a1a1a"))
    d.line([(cx, 93), (cx + 2, 94)], fill=hx("1a1a1a"))
    for x in (fx0 + 4, fx1 - 4):
        d.rectangle([x - 1, 88, x + 1, 102], fill=hx("c8a040"))
        d.rectangle([x - 3, 100, x + 3, 102], fill=hx("c8a040"))
        d.rectangle([x - 1, 82, x + 1, 88], fill=hx("f0ead8"))
    # ---- the tall window, an unobstructed moon and swagged drapes ----
    gx0, gy0, gx1, gy1 = 240, 34, 290, 140
    d.rectangle([gx0 - 5, gy0 - 5, gx1 + 5, gy1 + 6], fill=IVORY)
    vgrad(img, (gx0, gy0, gx1, gy1), hx("121834"), hx("2a3460"))
    light(img, "ellipse", [266, 40, 289, 63], hx("7a88b0"), 0.12, 5)
    d.ellipse([270, 45, 283, 58], fill=hx("f4f0d8"))
    d.ellipse([273, 48, 276, 51], fill=hx("c8c6b4"))
    d.ellipse([278, 53, 280, 55], fill=hx("dcdbc8"))
    ed.rectangle([gx0, gy0, gx1, gy1], fill=170)
    d.rectangle([264, gy0, 266, gy1], fill=IVORY)
    for y in (gy0 + 34, gy0 + 70):
        d.rectangle([gx0, y, gx1, y + 2], fill=IVORY)
    for (a, b, c2, dd) in (((228, 26), (248, 26), (244, 150), (226, 154)), ((282, 26), (302, 26), (304, 154), (286, 150))):
        d.polygon([a, b, c2, dd], fill=hx("6a2a3a"))
        for k in range(1, 4):
            t = k / 4
            d.line([(a[0] + (b[0] - a[0]) * t, 28), (dd[0] + (c2[0] - dd[0]) * t, 150)], fill=hx("4a1a26"))
    d.chord([224, 14, 306, 44], 0, 180, fill=hx("7a3242"), outline=hx("4a1a26"))
    d.line([(224, 29), (306, 29)], fill=GILT)
    for (x, y) in ((236, 120), (294, 120)):  # tie-backs
        d.ellipse([x - 3, y - 2, x + 3, y + 4], fill=GILT)
    # a silk corona above where the bed's head rests
    bxs = R.P(BED["x1"] - 6, 0, 0)[0]
    d.ellipse([bxs - 10, 28, bxs + 10, 38], fill=GILT)
    d.polygon([(bxs - 8, 34), (bxs + 8, 34), (bxs + 40, 120), (bxs + 30, 124), (bxs, 40), (bxs - 30, 124), (bxs - 40, 120)],
              fill=hx("8a3e4c"))
    d.line([(bxs, 40), (bxs - 34, 122)], fill=hx("5a2232"))
    d.line([(bxs, 40), (bxs + 34, 122)], fill=hx("5a2232"))
    # ---- nightstand with a silk-shaded lamp, lit ----
    R.box(img, 402, 422, 0, 30, 2, 18, hx("5a3420"), top=hx("7a4a2a"), side=hx("3a2014"))
    d = ImageDraw.Draw(img)
    a, b = R.P(402, 30, 18), R.P(422, 0, 18)
    d.rectangle([a[0] + 2, a[1] + 3, b[0] - 2, a[1] + 10], outline=hx("2a1a0c"))
    d.point(((a[0] + b[0]) / 2, a[1] + 6), fill=GILT)
    lp = R.P(414, 30, 8)
    lx, ly = lp
    d.rectangle([lx - 1, ly - 14, lx + 1, ly], fill=hx("c8a040"))
    d.ellipse([lx - 4, ly - 2, lx + 4, ly + 1], fill=hx("c8a040"))
    d.polygon([(lx - 9, ly - 14), (lx + 9, ly - 14), (lx + 5, ly - 25), (lx - 5, ly - 25)], fill=hx("f0b088"))
    d.line([(lx - 9, ly - 14), (lx + 9, ly - 14)], fill=hx("c87858"))
    ed.polygon([(lx - 9, ly - 14), (lx + 9, ly - 14), (lx + 5, ly - 25), (lx - 5, ly - 25)], fill=220)
    p = R.P(408, 30, 14)  # a book and a glass of water
    d.rectangle([p[0] - 4, p[1] - 2, p[0] + 2, p[1]], fill=hx("2a3a5a"))
    # ---- the folding screen, painted with herons on gold ----
    for i in range(4):
        x0 = 72 + i * 18
        top = 104 + (i % 2) * 3
        dy = 3 if i % 2 == 0 else -3
        d.polygon([(x0, top), (x0 + 18, top + dy), (x0 + 18, 210), (x0, 210)], fill=hx("2a1a12"), outline=hx("0e0806"))
        d.polygon([(x0 + 2, top + 4), (x0 + 16, top + dy + 4), (x0 + 16, 200), (x0 + 2, 200)], fill=hx("c8a868") if i % 2 else hx("b89a5a"))
        d.line([(x0 + 3, 170), (x0 + 15, 166 + (i % 3) * 3)], fill=hx("6a7a4a"))
        d.line([(x0 + 8, top + 50), (x0 + 10, top + 34), (x0 + 13, top + 38)], fill=hx("2a2a2a"))
        d.ellipse([x0 + 6, top + 40, x0 + 14, top + 52], fill=hx("ece8dc"))
        d.line([(x0 + 9, top + 52), (x0 + 8, top + 64)], fill=hx("2a2a2a"))
        d.line([(x0 + 11, top + 52), (x0 + 12, top + 64)], fill=hx("2a2a2a"))
        if i == 1:
            d.ellipse([x0 + 4, top + 12, x0 + 12, top + 20], fill=hx("c84a30"))  # a red sun
    d.rectangle([72, 206, 144, 210], fill=hx("1a100a"))
    # a silk robe thrown over the top of the screen
    d.polygon([(96, 100), (116, 102), (114, 132), (110, 128), (104, 134), (98, 126)], fill=hx("3a5a7a"))
    d.line([(98, 104), (112, 104)], fill=hx("6a8aaa"))
    # ---- floor: parquet, a pale Aubusson rug ----
    floor_boards(img, BFL, H - 1, (240, 100), 14, hx("6a4428"), hx("5a3820"), hx("2e1c0e"), 104)
    shadow(img, "rect", [0, BFL, W, BFL + 6], 0.5, 3)
    rug(R, img, 60, 430, 30, 230, hx("6a4a5a"), hx("3a2a44"), hx("d8b878"), seed=105)
    if bed:
        _bed(img, R, bed)
    # ---- light: firelight low on the left, the lamp's pink pool by the bed, moonlight from the window ----
    light(img, "polygon", [(gx0, gy0), (gx1, gy0), (330, H), (200, H)], hx("5a6ab0"), 0.22, 12)
    pools = [((fx0 + fx1) / 2, BFL - 10, 110, 70, (1.3, 0.85, 0.55), 1.0), (lx, ly - 10, 80, 60, (1.2, 0.95, 0.8), 0.9),
             (265, 80, 50, 70, (0.7, 0.75, 1.05), 0.5)]
    img = grade(img, (0.42, 0.4, 0.6), pools, em)
    light(img, "ellipse", [fx0 + 10, BFL - 40, fx1 - 10, BFL + 6], hx("f08040"), 0.3, 8)
    light(img, "ellipse", [lx - 16, ly - 34, lx + 16, ly - 6], hx("f0b080"), 0.3, 6)
    vignette(img, 0.5, (10, 6, 16), 40)
    if bed == "eleanor":
        _restamp_white_sheet(img, R)
    return img


def _cut_sprite(variant_px, base_px, name):
    """Everything that differs from the empty room, as an RGBA sprite; returns its top-left."""
    a = np.asarray(variant_px.convert("RGB")).astype(np.int16)
    b = np.asarray(base_px.convert("RGB")).astype(np.int16)
    mask = (np.abs(a - b).sum(axis=2) > 0)
    rgba = np.dstack([a.astype(np.uint8), (mask * 255).astype(np.uint8)])
    im = Image.fromarray(rgba, "RGBA")
    bb = im.getbbox()
    save(im.crop(bb), "rooms", name + ".png")
    print(f"{name} at ({bb[0]}, {bb[1]}) size {bb[2] - bb[0]}x{bb[3] - bb[1]}")
    return bb


def build_bedroom():
    base = paint_bedroom()
    v = {"eleanor": paint_bedroom("eleanor"), "empty": paint_bedroom("empty")}
    pal = bedroom_palette(base, v["eleanor"], v["empty"])
    px = pixelize(base, pal)
    save(px, "rooms", "mansion_bedroom.png")
    _cut_sprite(pixelize(v["eleanor"], pal), px, "mansion_bed")
    _cut_sprite(pixelize(v["empty"], pal), px, "mansion_bed_empty")
    return px, v
