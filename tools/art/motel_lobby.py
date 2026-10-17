"""The lobby of a cheap motel off a back alley, at night in the rain: the opposite of the Aurelian.

Peeling wallpaper and water stains, a bare bulb over a scuffed front desk with a bell, a guest register and a
pigeonhole key board (one key missing), a roped-off staircase, a sagging armchair and a spittoon under a rain-streaked
window that lets in the red neon of the MOTEL sign, and the front door to the alley with an umbrella stand beside it.

Writes assets/art/rooms/motel_lobby.png (480x270), the counter front and everything standing on it as a foreground
layer (motel_lobby_counter.png, drawn over the desk clerk standing behind it) and the umbrella in its stand
(motel_lobby_umbrella.png, hidden once taken). Their crop origins are printed and go into
scenes/rooms/motel_lobby.tscn."""
from PIL import Image, ImageDraw, ImageChops
import math
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save, cut)
from .furniture import Room3D

FLOOR = 176
R = Room3D(FLOOR, 240, -200)
CEIL = 18

PAPER = hx("6e6a40")
PAPER_D = hx("4a4628")
PLASTER = hx("7e765a")
STAIN = hx("7a5a2c")
WAINS = hx("3a2a1c")
WAINS_D = hx("20160e")
WOOD = hx("4a3220")
WOOD_D = hx("24180e")
BRASS = hx("b08a3a")
BRASS_D = hx("5a4218")
NEON = hx("ff3a30")
NEON_HI = hx("ffb0a0")
BULB = hx("ffe8a8")

DOOR = (12, 60, 92)            # front door x0, x1, top (back wall)
STAND = (66, 78, 4, 12, 22)    # umbrella stand x0, x1, z0, z1, height
WINDOW = (96, 154, 58, 134)    # street window x0, x1, y0, y1
CHAIR = (100, 148, 8, 34)      # armchair x0, x1, z0, z1
SPITTOON = (162, 40)           # x, z
COUNTER = (248, 398, 24, 44, 34)  # front desk x0, x1, z0, z1, height
KEYS = (322, 388, 96, 138)     # key board x0, x1, y0, y1
STAIRS = (414, 462, 110)       # stair opening x0, x1, height
BULB_X = 300

COUNTER_BASELINE = 196         # screen row of the counter's front foot: anyone standing above it is behind the desk

GLYPHS = {
    "G": ("111", "100", "101", "101", "111"),
    "U": ("101", "101", "101", "101", "111"),
    "E": ("111", "100", "110", "100", "111"),
    "S": ("111", "100", "111", "001", "111"),
    "T": ("111", "010", "010", "010", "010"),
    "O": ("111", "101", "101", "101", "111"),
    "N": ("101", "111", "111", "101", "101"),
    "L": ("100", "100", "100", "100", "111"),
    "Y": ("101", "101", "010", "010", "010"),
    "C": ("111", "100", "100", "100", "111"),
    "R": ("110", "101", "110", "101", "101"),
    "D": ("110", "101", "101", "101", "110"),
    "I": ("1", "1", "1", "1", "1"),
    "M": ("10001", "11011", "10101", "10001", "10001"),
    "A": ("010", "101", "111", "101", "101"),
    "1": ("01", "11", "01", "01", "01"),
    "9": ("111", "101", "111", "001", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "$": ("010", "111", "110", "011", "111"),
    " ": ("0", "0", "0", "0", "0"),
}


def tiny_width(s):
    return sum(len(GLYPHS[c][0]) + 1 for c in s) - 1


def tiny_text(d, x, y, s, col):
    for ch in s:
        g = GLYPHS[ch]
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    d.point((x + c, y + r), fill=col)
        x += len(g[0]) + 1


def P(x, y, z):
    px, py = R.P(x, y, z)
    return (round(px), round(py))


def blob(cx, cy, rx, ry, seed, n=14, jag=0.3):
    """A wobbly closed outline (stains, peeled patches, puddles)."""
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rnd.uniform(-jag, jag)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    return pts


# ============================================================================================ shell

def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, CEIL), hx("2a2a22"), hx("3e3c30"))
    noise(img, (0, 0, W - 1, CEIL), 4, 701)
    # a brown ring where the room upstairs leaks
    shadow(img, "polygon", blob(214, 6, 40, 9, 702), 0.45, 3, STAIN)
    d.line([(60, 4), (74, 9), (90, 6), (108, 12)], fill=hx("1a1a14"))
    d.rectangle([0, CEIL - 2, W - 1, CEIL], fill=hx("2a2016"))
    d.line([(0, CEIL - 2), (W, CEIL - 2)], fill=hx("4e3e2a"))


def wallpaper(img):
    d = ImageDraw.Draw(img)
    y0, y1 = CEIL + 1, 140
    vgrad(img, (0, y0, W - 1, y1), mul(PAPER, 1.05), PAPER_D)
    # tired stripes with a little sprig between them
    for x in range(0, W, 14):
        d.line([(x, y0), (x, y1)], fill=mul(PAPER, 0.78))
        d.line([(x + 2, y0), (x + 2, y1)], fill=mul(PAPER, 0.86))
        for y in range(y0 + 6 + (x // 14 % 2) * 8, y1, 16):
            d.point((x + 7, y), fill=hx("8a6a3e"))
            d.point((x + 6, y + 1), fill=hx("5e5a30"))
            d.point((x + 8, y + 1), fill=hx("5e5a30"))
            d.point((x + 7, y + 2), fill=hx("5e5a30"))
    noise(img, (0, y0, W - 1, y1), 5, 703)
    # grime collects at the top and along the chair rail
    shadow(img, "rect", [0, y0, W, y0 + 10], 0.4, 6)
    # water stains running down from the ceiling
    for i, (cx, cy, rx, ry) in enumerate(((196, 38, 22, 20), (360, 30, 16, 14), (36, 34, 14, 22), (250, 112, 12, 18))):
        pts = blob(cx, cy, rx, ry, 710 + i)
        shadow(img, "polygon", pts, 0.38, 4, STAIN)
        d.line(pts + [pts[0]], fill=mix(PAPER_D, STAIN, 0.5))
        d.line([(cx - 2, cy + ry - 2), (cx - 1, cy + ry + 10), (cx - 2, cy + ry + 18)], fill=mix(PAPER_D, STAIN, 0.4))


def peel(img, x, y, w, h, seed, curl="down"):
    """A strip of wallpaper come away from the plaster, curling at its loose edge."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    pts = [(x, y), (x + w, y + rnd.randint(-1, 1))]
    for k in range(5, 0, -1):
        pts.append((x + w * k / 5 + rnd.randint(-2, 1), y + h + rnd.randint(-3, 2)))
    pts.append((x + rnd.randint(-1, 1), y + h - 2))
    d.polygon(pts, fill=PLASTER)
    noise(img, (x, y, x + w, y + h + 3), 7, seed)
    d.line(pts[2:] + [pts[0]], fill=hx("3a3420"))
    # the loose flap folds back over itself
    if curl == "down":
        fy = y + h
        d.polygon([(x + 1, fy - 2), (x + w - 2, fy - 1), (x + w - 4, fy + 4), (x + 3, fy + 3)], fill=mul(PAPER, 0.92))
        d.line([(x + 3, fy + 4), (x + w - 4, fy + 5)], fill=hx("1e1a10"))
        d.line([(x + 1, fy - 2), (x + w - 2, fy - 1)], fill=hx("c8bc94"))
    else:
        d.polygon([(x + w, y), (x + w + 5, y + 3), (x + w + 4, y + h - 2), (x + w, y + h)], fill=mul(PAPER, 0.92))
        d.line([(x + w + 5, y + 3), (x + w + 4, y + h - 2)], fill=hx("1e1a10"))
        d.line([(x + w, y), (x + w, y + h)], fill=hx("c8bc94"))


def wainscot(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 139, W - 1, 142], fill=WOOD_D)
    d.line([(0, 139), (W, 139)], fill=hx("6a5034"))
    vgrad(img, (0, 143, W - 1, FLOOR - 4), WAINS, WAINS_D)
    for x in range(0, W, 16):
        d.line([(x, 143), (x, FLOOR - 4)], fill=mul(WAINS_D, 0.7))
        d.line([(x + 1, 143), (x + 1, FLOOR - 4)], fill=mul(WAINS, 1.2))
    noise(img, (0, 143, W - 1, FLOOR - 4), 5, 720)
    # scuffs and kick marks
    rnd = random.Random(721)
    for _ in range(40):
        x, y = rnd.randint(0, W - 8), rnd.randint(150, FLOOR - 6)
        d.line([(x, y), (x + rnd.randint(2, 6), y + rnd.randint(-1, 1))], fill=hx("5a4632"))
    d.rectangle([0, FLOOR - 4, W - 1, FLOOR], fill=hx("140e08"))


def planks(img):
    """Narrow pine boards running towards the camera, butt joints staggered, some boards darker or warped."""
    d = ImageDraw.Draw(img)
    vx, vy = R.vx, R.vy
    y0, y1 = FLOOR + 1, FULL_H - 1
    rnd = random.Random(730)
    spacing = 15

    def xat(xb, y):
        return vx + (xb - vx) * (y - vy) / (y1 - vy)

    seam = hx("140c06")
    for i in range(-40, 41):
        xa, xb = vx + i * spacing, vx + (i + 1) * spacing
        if xat(xb, y1) < -20 or xat(xa, y1) > W + 20:
            continue
        # each board is laid in lengths; a joint every so often, in a different place on each board
        y = float(y0)
        while y < y1:
            length = rnd.uniform(18, 46) * (y - vy) / (FLOOR - vy)
            ye = min(y1, y + length)
            col = mix(hx("4a3624"), hx("2e2216"), rnd.random() ** 1.5)
            d.polygon([(xat(xa, y), y), (xat(xb, y), y), (xat(xb, ye), ye), (xat(xa, ye), ye)], fill=col)
            d.line([(xat(xa, y) + 1, y), (xat(xb, y) - 1, y)], fill=mix(col, hx("6a5038"), 0.4))
            if ye < y1:
                d.line([(xat(xa, ye), ye), (xat(xb, ye), ye)], fill=seam)
            # nail heads at the ends of the length
            for xn in (xa + 3, xb - 3):
                d.point((round(xat(xn, y + 1)), round(y + 1)), fill=hx("0e0a06"))
            y = ye
        d.line([(xat(xa, y0), y0), (xa, y1)], fill=seam)
        d.line([(xat(xa, y0) + 1, y0), (xa + 1, y1)], fill=hx("4e3a28"))


def floor(img):
    planks(img)
    noise(img, (0, FLOOR + 1, W - 1, FULL_H - 1), 6, 731)
    d = ImageDraw.Draw(img)
    rnd = random.Random(732)
    # grime, cigarette burns and butts
    for _ in range(26):
        x, y = rnd.randint(0, W), rnd.randint(FLOOR + 6, FULL_H - 2)
        shadow(img, "ellipse", [x - 8, y - 2, x + 8, y + 2], 0.25, 2)
    for _ in range(9):
        x, y = rnd.randint(90, 420), rnd.randint(200, FULL_H - 4)
        d.line([(x, y), (x + 2, y)], fill=hx("d8d0b8"))
        d.point((x + 2, y), fill=hx("8a5a2a"))
    # a worn path from the door to the desk
    shadow(img, "polygon", [(20, 196), (70, 192), (330, 214), (340, 240), (240, 246), (30, 214)], 0.18, 10,
           hx("40342a"))
    # wet footprints from the alley
    for i in range(9):
        x = 46 + i * 26
        y = 210 + i * 3 + (4 if i % 2 else 0)
        shadow(img, "ellipse", [x - 3, y - 1, x + 3, y + 1], 0.5, 0, hx("101418"))
        d.point((x + 1, y - 1), fill=hx("6a6e74"))
    # rain blown in under the door
    shadow(img, "polygon", blob(40, 186, 26, 5, 733, 12, 0.25), 0.45, 1, hx("101820"))
    light(img, "polygon", blob(40, 185, 16, 2, 734, 10, 0.3), hx("405068"), 0.35, 1)
    shadow(img, "rect", [0, FLOOR, W, FLOOR + 8], 0.4, 4)


# ============================================================================================ west wall: door, stand

def front_door(img):
    d = ImageDraw.Draw(img)
    x0, x1, top = DOOR
    d.rectangle([x0 - 5, top - 6, x1 + 5, FLOOR], fill=WOOD_D)
    d.rectangle([x0 - 3, top - 4, x1 + 3, FLOOR], fill=hx("4e3a26"))
    d.line([(x0 - 3, top - 4), (x1 + 3, top - 4)], fill=hx("7a5e3e"))
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("4a3828"), hx("2e2218"))
    # pebbled glass in the top half: the alley's rain and darkness behind it
    gx0, gy0, gx1, gy1 = x0 + 6, top + 6, x1 - 6, top + 38
    d.rectangle([gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1], fill=hx("1a120a"))
    vgrad(img, (gx0, gy0, gx1, gy1), hx("26323e"), hx("161e28"))
    rnd = random.Random(740)
    for _ in range(70):
        x, y = rnd.randint(gx0, gx1), rnd.randint(gy0, gy1)
        d.point((x, y), fill=rnd.choice([hx("3a4a5a"), hx("101820"), hx("2e3c4a")]))
    for _ in range(6):
        x, y = rnd.randint(gx0 + 2, gx1 - 2), rnd.randint(gy0, gy1 - 10)
        d.line([(x, y), (x, y + rnd.randint(4, 9))], fill=hx("5a6a7a"))
    # a crack taped over
    d.line([(gx0 + 4, gy0 + 3), (gx0 + 14, gy0 + 16), (gx0 + 11, gy0 + 26)], fill=hx("8a9aa8"))
    d.rectangle([gx0 + 8, gy0 + 8, gx0 + 16, gy0 + 11], fill=hx("a89a70"))
    # lower panels, kicked in the past
    d.rectangle([x0 + 6, top + 46, x1 - 6, FLOOR - 8], outline=hx("1e160e"))
    d.line([(x0 + 7, top + 47), (x1 - 7, top + 47)], fill=hx("5e4834"))
    d.line([(x0 + 14, FLOOR - 20), (x0 + 22, FLOOR - 14)], fill=hx("6a5440"))
    d.line([(x0 + 22, FLOOR - 14), (x0 + 30, FLOOR - 17)], fill=hx("1a120a"))
    # knob, bolt and a chain lock
    d.ellipse([x1 - 9, top + 44, x1 - 4, top + 49], fill=BRASS)
    d.point((x1 - 8, top + 45), fill=hx("f0d890"))
    d.rectangle([x1 - 8, top + 30, x1 - 3, top + 33], fill=hx("6a6a6a"))
    for i in range(5):
        d.point((x1 - 6 - i, top + 34 + (i * i) // 4), fill=hx("8a8a8a"))
    # cold alley light leaks round the frame
    light(img, "rect", [x0 - 2, FLOOR - 2, x1 + 2, FLOOR + 3], hx("6080a0"), 0.35, 2)
    light(img, "rect", [x0, top, x0 + 2, FLOOR], hx("6080a0"), 0.25, 1)


def umbrella_stand(img, umbrella):
    d = ImageDraw.Draw(img)
    x0, x1, z0, z1, h = STAND
    zc = (z0 + z1) / 2
    cx = (x0 + x1) / 2
    fl, fr = P(x0, 0, z1), P(x1, 0, z1)
    tl, tr = P(x0, h, z1), P(x1, h, z1)
    bl, br = P(x0, h, z0), P(x1, h, z0)
    shadow(img, "ellipse", [fl[0] - 3, fl[1] - 4, fr[0] + 4, fr[1] + 2], 0.6, 2)
    # a dented zinc pail of a stand, not the Aurelian's brass
    rx = (fr[0] - fl[0]) / 2
    mid = (fl[0] + fr[0]) / 2
    body = hx("4a5048")
    d.rectangle([fl[0], tl[1], fr[0], fl[1]], fill=body)
    d.ellipse([fl[0], fl[1] - 2, fr[0], fl[1] + 2], fill=body)
    for i, x in enumerate(range(fl[0], fr[0] + 1)):
        t = (x - fl[0]) / max(1, fr[0] - fl[0])
        c = mix(hx("8a9488"), hx("2a2e28"), t ** 0.8)
        d.line([(x, tl[1] + 1), (x, fl[1])], fill=c)
    for y in (tl[1] + 5, fl[1] - 5):
        d.line([(fl[0], y), (fr[0], y)], fill=hx("2a2e28"))
        d.line([(fl[0], y + 1), (fr[0], y + 1)], fill=hx("9aa498"))
    d.point((fl[0] + 3, tl[1] + 10), fill=hx("2a2e28"))
    d.point((fl[0] + 4, tl[1] + 11), fill=hx("2a2e28"))
    # the open mouth of the stand
    top_y = (tl[1] + bl[1]) / 2
    d.ellipse([fl[0], bl[1] - 1, fr[0], tl[1] + 1], fill=hx("a4aea0"))
    d.ellipse([fl[0] + 1, bl[1], fr[0] - 1, tl[1]], fill=hx("101210"))
    if umbrella:
        ux = round(mid) - 1
        rim = round(top_y)
        # folded black canopy rising out of the stand, its strap buttoned round it
        canopy = hx("16161c")
        d.polygon([(ux - 3, rim + 1), (ux + 3, rim + 1), (ux + 1, rim - 12), (ux - 1, rim - 12)], fill=canopy)
        d.line([(ux - 2, rim), (ux, rim - 11)], fill=hx("3a3a46"))
        d.line([(ux + 2, rim), (ux + 1, rim - 11)], fill=hx("08080c"))
        d.line([(ux - 2, rim - 6), (ux + 2, rim - 6)], fill=hx("4a4a58"))
        # bare shaft and the crook handle hooked over towards the door
        d.line([(ux, rim - 12), (ux, rim - 18)], fill=hx("8a8a90"))
        handle = hx("5a2e14")
        d.line([(ux, rim - 18), (ux, rim - 24)], fill=handle, width=2)
        d.arc([ux - 8, rim - 29, ux + 1, rim - 21], 180, 360, fill=handle, width=2)
        d.line([(ux - 8, rim - 25), (ux - 8, rim - 22)], fill=handle, width=2)
        d.point((ux, rim - 27), fill=hx("b07a4a"))
        d.point((ux - 4, rim - 29), fill=hx("b07a4a"))
        d.point((ux + 1, rim - 22), fill=hx("2a1408"))


# ============================================================================================ window, chair, spittoon

def window(img):
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = WINDOW
    by = y0 + 8
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 6], fill=WOOD_D)
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=hx("5a4430"))
    d.rectangle([x0 - 7, y1 + 3, x1 + 7, y1 + 6], fill=hx("6a5038"))  # sill
    d.line([(x0 - 7, y1 + 3), (x1 + 7, y1 + 3)], fill=hx("8a6c4c"))
    # the street outside: a wet brick wall opposite, a lamp far off and the blade of the MOTEL sign
    vgrad(img, (x0, y0, x1, y1), hx("0c1018"), hx("1a1e28"))
    for y in range(y0 + 4, y1, 5):
        for x in range(x0 + (y // 5 % 2) * 4, x1, 8):
            d.rectangle([x, y, min(x1, x + 6), y + 3], fill=hx("1e1a20"))
    for wx, wy in ((x0 + 6, y0 + 10), (x0 + 22, y0 + 10)):
        d.rectangle([wx, wy, wx + 8, wy + 12], fill=hx("3a3020"))
        d.rectangle([wx + 1, wy + 1, wx + 7, wy + 11], fill=hx("6a5430"))
        d.line([(wx + 4, wy + 1), (wx + 4, wy + 11)], fill=hx("2a2018"))
    sx0, sx1 = x1 - 20, x1 - 6
    d.rectangle([sx0 - 1, y0, sx1 + 1, y1 - 6], fill=hx("1a0808"))
    d.rectangle([sx0, y0, sx1, y1 - 7], fill=hx("2a0e0e"))
    tube = NEON
    ly = by + 4
    for ch in "MOTEL":
        g = GLYPHS[ch]
        gw = len(g[0])
        scale = 2
        lx = (sx0 + sx1) // 2 - (gw * scale) // 2 + 1
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    d.rectangle([lx + c * scale, ly + r * scale, lx + c * scale + 1, ly + r * scale + 1], fill=tube)
        ly += 5 * scale + 2
    light(img, "rect", [sx0 - 14, y0, sx1 + 14, y1], NEON, 0.35, 6)
    # its letters again, smeared in the wet street at the bottom of the pane
    for k in range(4):
        d.line([(sx0 + 2 + k * 3, y1 - 4), (sx0 + 2 + k * 3, y1 - 1)], fill=mul(NEON, 0.5))
    # rain on the glass: running streaks and beads
    rnd = random.Random(750)
    for _ in range(40):
        x, y = rnd.randint(x0 + 1, x1 - 1), rnd.randint(y0, y1 - 6)
        n = rnd.randint(3, 10)
        pts = [(x + (k // 3) % 2, y + k) for k in range(n)]
        d.line(pts, fill=rnd.choice([hx("5a6878"), hx("7a8898"), hx("a05050")]))
    for _ in range(30):
        d.point((rnd.randint(x0, x1), rnd.randint(y0, y1)), fill=hx("8a98a8"))
    # sash bar and muntin
    d.rectangle([x0, (y0 + y1) // 2 - 1, x1, (y0 + y1) // 2 + 1], fill=hx("4a3828"))
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("4a3828"), width=2)
    # a yellowed roller blind, torn, rolled most of the way up
    d.rectangle([x0 - 2, y0 - 3, x1 + 2, y0], fill=hx("2a2016"))
    d.polygon([(x0, y0), (x1, y0), (x1, by + 2), (x1 - 12, by), (x1 - 16, by + 6), (x1 - 20, by + 1), (x0, by)],
              fill=hx("a8945a"))
    vgrad(img, (x0, y0 + 1, x1, y0 + 4), hx("6a5a34"), hx("a8945a"))
    d.line([(x0, by), (x1 - 20, by + 1)], fill=hx("5a4a2a"))
    d.line([(x0 + 18, y0 + 3), (x0 + 21, y0 + 8)], fill=hx("6a5a34"))
    d.ellipse([(x0 + x1) // 2 - 2, by + 1, (x0 + x1) // 2 + 2, by + 5], outline=hx("3a3020"))
    shadow(img, "rect", [x0, y0, x1, by], 0.2, 1, hx("ff8060"))


def neon_spill(img):
    """The sign's red light through the pane: a glow on the wall and a skewed patch on the floor."""
    x0, x1, y0, y1 = WINDOW
    light(img, "rect", [x0 - 30, y0 - 20, x1 + 30, y1 + 20], NEON, 0.22, 20)
    a, b = P(x0 + 4, 0, 30), P(x1 + 40, 0, 120)
    light(img, "polygon", [(x0 + 8, FLOOR + 4), (x1 + 6, FLOOR + 4), (b[0] + 30, b[1]), (a[0] - 10, b[1])], NEON, 0.2,
          10)


def armchair(img):
    d = ImageDraw.Draw(img)
    x0, x1, z0, z1 = CHAIR
    velvet, velvet_d = hx("6a2a24"), hx("3a1410")
    a, b = P(x0, 0, z1), P(x1, 0, z1)
    shadow(img, "ellipse", [a[0] - 6, a[1] - 6, b[0] + 8, b[1] + 3], 0.6, 3)
    # stubby legs
    for x, z in ((x0 + 2, z1 - 1), (x1 - 4, z1 - 1)):
        p = P(x, 0, z)
        d.rectangle([p[0], p[1] - 3, p[0] + 2, p[1]], fill=hx("1a100a"))
    # back
    R.box(img, x0, x1, 4, 46, z0, z0 + 7, velvet, top=mul(velvet, 1.1), side=velvet_d)
    bt = P(x0 + 3, 46, z0 + 7)
    btr = P(x1 - 3, 46, z0 + 7)
    d.chord([bt[0] - 1, bt[1] - 6, btr[0] + 1, bt[1] + 6], 180, 360, fill=mul(velvet, 1.05))
    # tufting buttons and a yellowed doily pinned over the worn patch
    for x in range(x0 + 8, x1 - 4, 9):
        for y in (26, 36):
            p = P(x, y, z0 + 7)
            d.point(p, fill=velvet_d)
    dl, dr = P(x0 + 14, 46, z0 + 7), P(x1 - 14, 46, z0 + 7)
    d.polygon([(dl[0], dl[1] - 2), (dr[0], dr[1] - 2), (dr[0] - 2, dr[1] + 9), ((dl[0] + dr[0]) // 2, dr[1] + 12),
               (dl[0] + 2, dl[1] + 9)], fill=hx("c8b88a"))
    for x in range(dl[0] + 2, dr[0] - 1, 3):
        d.point((x, dl[1] + 8), fill=hx("8a7a54"))
    # seat, sagging in the middle
    R.box(img, x0 + 6, x1 - 6, 4, 18, z0 + 7, z1 - 2, velvet, top=mul(velvet, 1.18), side=velvet_d)
    s0, s1 = P(x0 + 8, 18, z0 + 14), P(x1 - 8, 18, z0 + 14)
    d.chord([s0[0], s0[1] - 2, s1[0], s0[1] + 6], 0, 180, fill=mul(velvet, 0.82))
    # a split in the seat with stuffing coming out
    t = P(x0 + 30, 18, z1 - 6)
    d.polygon([(t[0] - 4, t[1]), (t[0] + 3, t[1] - 1), (t[0] + 4, t[1] + 2), (t[0] - 3, t[1] + 2)], fill=hx("d8ccaa"))
    d.line([(t[0] - 4, t[1] + 2), (t[0] + 4, t[1] + 2)], fill=velvet_d)
    # arms
    for ax0, ax1 in ((x0, x0 + 7), (x1 - 7, x1)):
        R.box(img, ax0, ax1, 4, 26, z0 + 4, z1, mul(velvet, 0.95), top=mul(velvet, 1.25), side=velvet_d)
        f = P(ax0, 26, z1)
        g = P(ax1, 26, z1)
        d.chord([f[0] - 1, f[1] - 3, g[0] + 1, f[1] + 3], 180, 360, fill=mul(velvet, 1.3))
    # bald patches on the arms
    for ax in (x0 + 3, x1 - 4):
        p = P(ax, 26, z1 - 8)
        d.line([(p[0] - 1, p[1]), (p[0] + 2, p[1])], fill=hx("8a5a3a"))
    noise(img, (a[0], P(x0, 46, z0)[1] - 6, b[0], a[1]), 6, 760)


def spittoon(img):
    d = ImageDraw.Draw(img)
    x, z = SPITTOON
    p = P(x, 0, z)
    cx, by = p
    shadow(img, "ellipse", [cx - 8, by - 3, cx + 9, by + 2], 0.6, 2)
    # a splash that missed
    shadow(img, "polygon", blob(cx + 9, by + 2, 6, 2, 770, 8), 0.5, 0, hx("2a1a0a"))
    body = [BRASS_D, hx("7a5a24"), BRASS, hx("d8b460"), BRASS, hx("7a5a24"), BRASS_D]
    # squat belly
    for i in range(-6, 7):
        h = int(round(7 * math.sqrt(1 - (i / 7) ** 2)))
        c = body[min(len(body) - 1, max(0, (i + 6) * len(body) // 13))]
        d.line([(cx + i, by - h - 1), (cx + i, by)], fill=c)
    # the neck and the wide funnel mouth
    d.rectangle([cx - 3, by - 10, cx + 3, by - 7], fill=hx("7a5a24"))
    d.ellipse([cx - 8, by - 15, cx + 8, by - 10], fill=hx("d8b460"))
    d.ellipse([cx - 6, by - 14, cx + 6, by - 11], fill=hx("1a1008"))
    d.line([(cx - 7, by - 12), (cx - 7, by - 13)], fill=hx("fff0b0"))
    d.point((cx - 3, by - 4), fill=hx("f0d890"))


# ============================================================================================ centre wall

def radiator(img):
    d = ImageDraw.Draw(img)
    x0, x1 = 186, 230
    a = P(x0, 0, 4)
    top = P(x0, 24, 4)[1]
    d.rectangle([x0, top, x1, a[1]], fill=hx("2a2420"))
    for x in range(x0 + 1, x1, 4):
        d.rectangle([x, top + 1, x + 2, a[1] - 3], fill=hx("6a5a48"))
        d.line([(x, top + 1), (x, a[1] - 3)], fill=hx("8a7a64"))
        d.point((x + 1, top + 5), fill=hx("8a4a24"))
    d.rectangle([x0, a[1] - 3, x1, a[1] - 1], fill=hx("3a2e24"))
    # rust running from a leaking valve
    d.rectangle([x1 + 1, top + 4, x1 + 4, top + 8], fill=hx("4a3a2a"))
    shadow(img, "rect", [x0 + 4, top + 6, x0 + 18, a[1]], 0.3, 2, hx("8a3a10"))


def notices(img):
    d = ImageDraw.Draw(img)
    # a cheap calendar on a nail, still on last month
    cx0, cy0 = 176, 60
    d.line([(cx0 + 10, cy0 - 4), (cx0 + 10, cy0)], fill=hx("2a2a2a"))
    d.rectangle([cx0, cy0, cx0 + 20, cy0 + 30], fill=hx("c8bc98"))
    d.rectangle([cx0, cy0, cx0 + 20, cy0 + 12], fill=hx("6a2a24"))
    d.rectangle([cx0 + 3, cy0 + 2, cx0 + 17, cy0 + 10], fill=hx("c89a6a"))
    d.line([(cx0 + 5, cy0 + 9), (cx0 + 10, cy0 + 4), (cx0 + 15, cy0 + 9)], fill=hx("3a5a6a"))
    tiny_text(d, cx0 + 3, cy0 + 14, "1927", hx("2a2018"))
    for r in range(3):
        for c in range(5):
            d.point((cx0 + 3 + c * 3, cy0 + 21 + r * 3), fill=hx("5a5040"))
    d.line([(cx0 + 20, cy0 + 1), (cx0 + 20, cy0 + 30)], fill=hx("6a604a"))
    # hand-lettered card, crooked
    nx0, ny0 = 210, 68
    w = tiny_width("NO CREDIT") + 6
    d.polygon([(nx0, ny0), (nx0 + w, ny0 + 2), (nx0 + w - 1, ny0 + 14), (nx0 - 1, ny0 + 12)], fill=hx("d8ccaa"))
    tiny_text(d, nx0 + 3, ny0 + 4, "NO CREDIT", hx("8a1a14"))
    d.point((nx0 + w // 2, ny0 + 1), fill=hx("4a4a4a"))
    # rates, chalked on a slate by the desk
    sx0, sy0 = 254, 84
    d.rectangle([sx0, sy0, sx0 + 34, sy0 + 20], fill=hx("4a3220"))
    d.rectangle([sx0 + 2, sy0 + 2, sx0 + 32, sy0 + 18], fill=hx("1e2422"))
    tiny_text(d, sx0 + 4, sy0 + 4, "ROOMS", hx("c8ccc0"))
    tiny_text(d, sx0 + 8, sy0 + 11, "$1", hx("c8ccc0"))
    d.line([(sx0 + 20, sy0 + 13), (sx0 + 28, sy0 + 12)], fill=hx("8a9088"))


# ============================================================================================ desk

def key_board(img):
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = KEYS
    shadow(img, "rect", [x0 + 2, y0 + 3, x1 + 4, y1 + 4], 0.5, 2)
    d.rectangle([x0, y0, x1, y1], fill=hx("3a2616"))
    d.rectangle([x0, y0, x1, y0 + 3], fill=hx("5a3c22"))
    d.line([(x0, y0), (x1, y0)], fill=hx("8a6640"))
    cols, rows = 6, 3
    cw = (x1 - x0 - 4) // cols
    ch = (y1 - y0 - 8) // rows
    missing = (3, 1)
    for r in range(rows):
        for c in range(cols):
            bx = x0 + 3 + c * cw
            by = y0 + 6 + r * ch
            d.rectangle([bx, by, bx + cw - 2, by + ch - 2], fill=hx("140c06"))
            d.line([(bx, by + ch - 2), (bx + cw - 2, by + ch - 2)], fill=hx("6a4a2a"))
            # brass number plate under each hole
            d.line([(bx + 3, by + ch - 1), (bx + 5, by + ch - 1)], fill=BRASS)
            hook = (bx + cw // 2 - 1, by + 2)
            d.point(hook, fill=hx("9a9a8a"))
            if (c, r) == missing:
                # an empty hook and a clean ghost of the tag on the dusty back
                d.rectangle([hook[0] - 1, hook[1] + 3, hook[0] + 1, hook[1] + 6], fill=hx("2a1e12"))
                continue
            # key on its brass ring with a big wooden tag
            d.line([(hook[0], hook[1] + 1), (hook[0], hook[1] + 3)], fill=hx("c0a050"))
            tag = hx("a8743a") if (r + c) % 3 else hx("8a5a2a")
            d.rectangle([hook[0] - 1, hook[1] + 4, hook[0] + 1, hook[1] + 7], fill=tag)
            d.point((hook[0] - 1, hook[1] + 4), fill=mix(tag, hx("ffffff"), 0.3))
    # mail stuffed in one hole
    d.polygon([(x0 + 4 + 5 * cw, y0 + 7), (x0 + 1 + 6 * cw, y0 + 9), (x0 + 1 + 6 * cw, y0 + 12),
               (x0 + 4 + 5 * cw, y0 + 12)], fill=hx("c8bc98"))


def counter(img, items=True):
    d = ImageDraw.Draw(img)
    x0, x1, z0, z1, h = COUNTER
    front = hx("5a3e26")
    a, b = P(x0, 0, z1), P(x1, 0, z1)
    shadow(img, "rect", [a[0] - 4, a[1] - 3, b[0] + 6, a[1] + 4], 0.55, 3)
    R.box(img, x0, x1, 0, h, z0, z1, front, top=hx("3a2a1c"), side=hx("2e1e12"))
    tl, tr = P(x0, h, z1), P(x1, h, z1)
    # a thick top with a lip, worn pale along the edge where elbows lean
    d.rectangle([tl[0] - 2, tl[1] - 1, tr[0] + 2, tl[1] + 2], fill=hx("4a3220"))
    d.line([(tl[0] - 2, tl[1] - 1), (tr[0] + 2, tl[1] - 1)], fill=hx("9a7a52"))
    d.line([(tl[0] - 2, tl[1] + 3), (tr[0] + 2, tl[1] + 3)], fill=hx("1a1008"))
    bl = P(x0, h, z0)
    vgrad(img, (bl[0], bl[1], tr[0], tl[1] - 2), hx("2a1e14"), hx("4a3624"))
    rnd = random.Random(780)
    for _ in range(4):
        x = rnd.randint(bl[0] + 6, tr[0] - 12)
        d.ellipse([x, tl[1] - 5, x + 6, tl[1] - 3], outline=hx("2a1a10"))
    # cheap stained panels, a sprung corner and boot marks along the bottom
    vgrad(img, (a[0], tl[1] + 4, b[0], a[1]), hx("5e4228"), hx("2e2014"))
    for x in range(a[0] + 4, b[0] - 20, 26):
        d.rectangle([x, tl[1] + 9, x + 22, a[1] - 8], outline=hx("2a1a0e"))
        d.line([(x + 1, tl[1] + 10), (x + 21, tl[1] + 10)], fill=hx("7a5a3a"))
        d.line([(x + 1, tl[1] + 10), (x + 1, a[1] - 9)], fill=hx("6a4c30"))
    d.rectangle([a[0], a[1] - 4, b[0], a[1]], fill=hx("1a1008"))
    for _ in range(18):
        x = rnd.randint(a[0], b[0] - 4)
        y = rnd.randint(a[1] - 14, a[1] - 5)
        d.line([(x, y), (x + rnd.randint(2, 5), y + rnd.randint(-1, 1))], fill=hx("2a1c10"))
    d.polygon([(b[0] - 10, tl[1] + 4), (b[0], tl[1] + 4), (b[0], tl[1] + 12)], fill=hx("c8b088"))  # veneer gone
    d.line([(b[0] - 10, tl[1] + 4), (b[0], tl[1] + 12)], fill=hx("2a1a0e"))
    noise(img, (a[0], tl[1] + 4, b[0], a[1]), 5, 781)
    if items:
        desk_items(img)


def bell_at():
    return P(268, COUNTER[4], 36)


def register_at():
    return P(352, COUNTER[4], 32)


def desk_items(img):
    d = ImageDraw.Draw(img)
    # the desk bell
    cx, by = bell_at()
    d.ellipse([cx - 5, by - 2, cx + 5, by + 1], fill=hx("2a2a2a"))
    d.chord([cx - 4, by - 8, cx + 4, by + 1], 180, 360, fill=hx("c8a040"))
    d.line([(cx - 4, by - 3), (cx + 4, by - 3)], fill=hx("6a4a18"))
    d.point((cx - 2, by - 6), fill=hx("fff0b0"))
    d.point((cx - 3, by - 5), fill=hx("f0d080"))
    d.rectangle([cx, by - 10, cx + 1, by - 8], fill=hx("b0b0b0"))
    # the guest register, open, a pen in a dry inkwell beside it
    rx, ry = register_at()
    pages = [(rx - 14, ry - 1), (rx, ry - 3), (rx + 14, ry - 1), (rx + 16, ry + 5), (rx, ry + 3), (rx - 16, ry + 5)]
    d.polygon([(p[0], p[1] + 2) for p in pages], fill=hx("2a1a10"))
    d.polygon(pages, fill=hx("d8ccaa"))
    d.line([(rx, ry - 3), (rx, ry + 3)], fill=hx("8a7a5a"))
    for k in range(3):
        d.line([(rx - 12 + k, ry + k * 2), (rx - 3, ry - 2 + k * 2)], fill=hx("6a6a7a"))
        d.line([(rx + 3, ry - 2 + k * 2), (rx + 12 - k, ry + k * 2)], fill=hx("6a6a7a"))
    d.line([(rx + 5, ry + 1), (rx + 9, ry)], fill=hx("1a1a3a"))  # the latest signature, fresh
    ix, iy = rx + 22, ry + 2
    d.rectangle([ix - 2, iy - 3, ix + 2, iy], fill=hx("1a1a20"))
    d.point((ix - 1, iy - 3), fill=hx("6a6a7a"))
    d.line([(ix, iy - 3), (ix + 4, iy - 10)], fill=hx("2a2a2a"))
    # an ashtray with a cigarette going
    ax, ay = P(304, COUNTER[4], 38)
    d.ellipse([ax - 4, ay - 1, ax + 4, ay + 2], fill=hx("6a6e66"))
    d.ellipse([ax - 3, ay - 1, ax + 3, ay + 1], fill=hx("2a2a28"))
    d.line([(ax + 1, ay), (ax + 6, ay - 1)], fill=hx("e0d8c8"))
    d.point((ax + 6, ay - 1), fill=hx("ff7020"))
    for k, (dx, dy) in enumerate(((7, -3), (6, -5), (8, -7), (9, -9), (8, -11))):
        d.point((ax + dx, ay + dy), fill=mix(hx("8a8a90"), hx("4a4a50"), k / 5))


def bulb(img):
    d = ImageDraw.Draw(img)
    cx = BULB_X
    d.line([(cx, CEIL - 2), (cx, 44)], fill=hx("14140e"))
    d.rectangle([cx - 2, 42, cx + 2, 46], fill=hx("5a4a2a"))
    d.ellipse([cx - 4, 45, cx + 4, 54], fill=BULB)
    d.point((cx - 2, 47), fill=hx("ffffff"))
    light(img, "ellipse", [cx - 90, -10, cx + 90, 120], hx("e8d080"), 0.3, 22)
    light(img, "polygon", [(cx - 20, 54), (cx + 20, 54), (cx + 130, FULL_H), (cx - 130, FULL_H)], hx("d8c070"), 0.1, 26)
    light(img, "ellipse", [cx - 10, 40, cx + 10, 60], BULB, 0.6, 4)
    # moths and flies circling it
    for dx, dy in ((-9, 40), (8, 46), (12, 36), (-5, 60), (6, 62)):
        d.point((cx + dx, dy), fill=hx("2a2418"))
    d.line([(cx - 13, 48), (cx - 11, 47)], fill=hx("6a5a3a"))


def fan(img):
    d = ImageDraw.Draw(img)
    cx = 150
    d.rectangle([cx - 1, CEIL - 2, cx + 1, 26], fill=hx("2a2a24"))
    d.ellipse([cx - 5, 25, cx + 5, 31], fill=hx("4a4a40"))
    d.line([(cx - 4, 26), (cx + 3, 26)], fill=hx("7a7a6a"))
    # two dusty blades, one hanging lower than the other
    d.polygon([(cx - 4, 28), (cx - 40, 26), (cx - 42, 29), (cx - 4, 31)], fill=hx("3a2c1e"))
    d.polygon([(cx + 4, 28), (cx + 38, 31), (cx + 39, 34), (cx + 4, 31)], fill=hx("3a2c1e"))
    d.line([(cx - 40, 26), (cx - 4, 28)], fill=hx("6a604a"))
    d.line([(cx + 4, 28), (cx + 38, 31)], fill=hx("6a604a"))
    d.ellipse([cx - 2, 31, cx + 2, 34], fill=hx("2a2a24"))
    d.line([(cx + 1, 34), (cx + 1, 42)], fill=hx("6a6a5a"))  # pull chain


# ============================================================================================ stairs

def stairs(img):
    x0, x1, h = STAIRS
    d = ImageDraw.Draw(img)
    layer = img.copy()
    ld = ImageDraw.Draw(layer)
    ot = FLOOR - h
    # the stairwell beyond the opening: dark, with a far wall in shadow
    ld.rectangle([x0, ot, x1, FLOOR], fill=hx("0e0c08"))
    far = [P(x1, 0, 0), P(x1, 0, -160), P(x1, 170, -160), P(x1, 170, 0)]
    ld.polygon(far, fill=hx("24221a"))
    for k in range(8):
        z = -k * 20
        ld.line([P(x1, 0, z), P(x1, 170, z)], fill=hx("26240f"))
    steps = 12
    rise, run = 9, 13
    for i in reversed(range(steps)):
        zf = 10 - i * run
        top = (i + 1) * rise
        tone = 0.35 + 0.75 * (steps - i) / steps
        R.box(layer, x0, x1, 0, top, zf - run, zf, mul(hx("3a2818"), tone), top=mul(hx("7a5e40"), tone),
              side=mul(hx("2a1c10"), tone))
        # worn runner tread down the middle of each step, a pale nosing on its edge
        a, b = P(x0 + 12, top, zf), P(x1 - 12, top, zf)
        c = P(x0 + 12, top, zf - run)
        ld.polygon([a, b, (b[0], c[1]), c], fill=mul(hx("6a2c24"), tone))
        ld.polygon([a, b, P(x1 - 12, top - rise, zf), P(x0 + 12, top - rise, zf)], fill=mul(hx("4a1c18"), tone))
        ld.line([P(x0, top, zf), P(x1, top, zf)], fill=mul(hx("b09068"), tone))
    # handrail on the stairwell wall
    ld.line([P(x1, 34, 10), P(x1, 34 + steps * rise, 10 - steps * run)], fill=hx("8a6a44"), width=2)
    mask = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(mask)
    md.rectangle([x0, ot, x1, FLOOR + 1], fill=255)
    md.polygon([P(x0, 0, 10), P(x1, 0, 10), P(x1, rise, 10), P(x1, rise, 0), P(x0, rise, 0), P(x0, rise, 10)],
               fill=255)
    md.polygon([P(x0, 0, 0), P(x0, 0, 10), P(x0, rise, 10), P(x0, rise, 0)], fill=255)
    shadow(layer, "rect", [x0, ot - 10, x1, ot + 40], 0.6, 12)
    img.paste(layer, (0, 0), mask)
    # the opening's frame
    d.rectangle([x0 - 4, ot - 5, x1 + 4, ot - 1], fill=WOOD_D)
    d.line([(x0 - 4, ot - 5), (x1 + 4, ot - 5)], fill=hx("7a5e3e"))
    d.rectangle([x0 - 4, ot - 1, x0 - 1, FLOOR - 1], fill=hx("4e3a26"))
    d.rectangle([x1 + 1, ot - 1, x1 + 4, FLOOR - 1], fill=hx("3a2a1a"))


def guests_only(img):
    """A chain hooked across the foot of the stairs, a card hung from it."""
    d = ImageDraw.Draw(img)
    x0, x1, _ = STAIRS
    zc = 12
    lp, rp = P(x0 - 4, 0, zc), P(x1 + 4, 0, zc)
    # newel post on the left, a brass hook screwed into the frame on the right
    post = [(lp[0] - 3, lp[1] - 40), (lp[0] + 3, lp[1])]
    d.rectangle(post, fill=hx("3a2614"))
    d.line([(lp[0] - 3, lp[1] - 40), (lp[0] - 3, lp[1])], fill=hx("7a5a36"))
    d.ellipse([lp[0] - 4, lp[1] - 45, lp[0] + 4, lp[1] - 38], fill=hx("4a3018"))
    d.point((lp[0] - 2, lp[1] - 43), fill=hx("9a7a4a"))
    hook = (x1 + 3, FLOOR - 32)
    d.rectangle([hook[0] - 1, hook[1] - 1, hook[0] + 1, hook[1] + 1], fill=BRASS)
    start = (lp[0] + 3, lp[1] - 32)
    n = 24
    pts = []
    for k in range(n + 1):
        t = k / n
        x = start[0] + (hook[0] - start[0]) * t
        y = start[1] + (hook[1] - start[1]) * t + 7 * math.sin(math.pi * t)
        pts.append((round(x), round(y)))
    for k, p in enumerate(pts):
        d.point(p, fill=hx("a8a8a0") if k % 2 else hx("5a5a54"))
    # the card
    mid = pts[n // 2]
    w = max(tiny_width("GUESTS"), tiny_width("ONLY")) + 4
    cx0, cy0 = mid[0] - w // 2, mid[1] + 3
    d.line([(mid[0] - 3, mid[1]), (cx0 + 2, cy0)], fill=hx("6a6a64"))
    d.line([(mid[0] + 3, mid[1]), (cx0 + w - 2, cy0)], fill=hx("6a6a64"))
    d.rectangle([cx0, cy0, cx0 + w, cy0 + 14], fill=hx("e0d4b0"))
    d.rectangle([cx0, cy0, cx0 + w, cy0 + 14], outline=hx("4a3e2a"))
    tiny_text(d, cx0 + (w - tiny_width("GUESTS")) // 2 + 1, cy0 + 2, "GUESTS", hx("1a1410"))
    tiny_text(d, cx0 + (w - tiny_width("ONLY")) // 2 + 1, cy0 + 8, "ONLY", hx("8a1a14"))


# ============================================================================================ composition

def paint(umbrella=True, desk=True, desk_items_=True):
    img = Image.new("RGB", (W, FULL_H))
    ceiling(img)
    wallpaper(img)
    peel(img, 70, 30, 16, 26, 790)
    peel(img, 162, 98, 12, 22, 791, curl="side")
    peel(img, 392, 46, 14, 30, 792)
    peel(img, 236, 24, 10, 14, 793)
    wainscot(img)
    floor(img)
    # the room itself is dim and cold; the bulb, the alley and the sign put back what light there is
    shadow(img, "rect", [0, 0, W, FULL_H], 0.32, 0, (40, 60, 70))
    front_door(img)
    umbrella_stand(img, umbrella)
    window(img)
    neon_spill(img)
    radiator(img)
    notices(img)
    key_board(img)
    stairs(img)
    armchair(img)
    spittoon(img)
    guests_only(img)
    if desk:
        counter(img, desk_items_)
    fan(img)
    bulb(img)
    # the corners sink into a damp, blue-green dark; the window's red holds
    vignette(img, 0.62, tint=(30, 40, 46), blur=44)
    shadow(img, "rect", [0, 0, W, CEIL + 10], 0.35, 10, (40, 40, 50))
    return img


def counter_mask():
    """Alpha of the foreground layer: the desk's front, top and lip, and whatever stands on it."""
    x0, x1, z0, z1, h = COUNTER
    mask = Image.new("L", (W, FULL_H), 0)
    md = ImageDraw.Draw(mask)
    tl, tr = P(x0, h, z1), P(x1, h, z1)
    bl, br = P(x0, h, z0), P(x1, h, z0)
    a, b = P(x0, 0, z1), P(x1, 0, z1)
    md.polygon([bl, br, tr, b, a, tl], fill=255)
    md.rectangle([tl[0] - 2, tl[1] - 1, tr[0] + 2, a[1]], fill=255)
    md.polygon([P(x0, 0, z0), P(x0, 0, z1), P(x0, h, z1), P(x0, h, z0)], fill=255)
    on = paint(umbrella=False, desk=True, desk_items_=True)
    off = paint(umbrella=False, desk=True, desk_items_=False)
    items = ImageChops.difference(on, off).convert("L").point(lambda v: 255 if v else 0)
    # only what rises above the desktop (the bell's dome, the pen, the smoke), not light spill on the wall
    box = (bl[0], bl[1] - 14, br[0] + 30, tl[1])
    keep = Image.new("L", mask.size, 0)
    keep.paste(items.crop(box), box[:2])
    return ImageChops.lighter(mask, keep)


def _overlay(base, state, name):
    diff = ImageChops.difference(base, state).convert("L").point(lambda v: 255 if v else 0)
    box = diff.getbbox()
    if box is None:
        raise ValueError(f"{name} does not differ from its base")
    save(cut(state, diff).crop(box), "rooms", f"{name}.png")
    print(f"  {name}.png at {box[:2]}")
    return box


def build():
    variants = {"base": paint(umbrella=False), "umbrella": paint(umbrella=True)}
    src = Image.blend(variants["base"], variants["umbrella"], 0.5)
    pal = palette_of(src, 124) + [NEON, mul(NEON, 0.6), BULB, hx("c8a040")]
    px = {k: pixelize(v, pal) for k, v in variants.items()}
    save(px["base"], "rooms", "motel_lobby.png")
    _overlay(px["base"], px["umbrella"], "motel_lobby_umbrella")
    mask = counter_mask()
    box = mask.getbbox()
    save(cut(px["base"], mask).crop(box), "rooms", "motel_lobby_counter.png")
    print(f"  motel_lobby_counter.png at {box[:2]}, baseline {COUNTER_BASELINE}")
    return px["base"]
