"""A cheap roadside motel room in flat, dingy daytime light."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of, save,
                     floor_boards, text)
from .furniture import Room3D

FLOOR = 136
WOOD = hx("6a5038")
WOOD_D = hx("342418")
R = Room3D(FLOOR, 250, -250)

def wall_mirror(img, box):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 2], outline=hx("9a7850"), width=2)
    vgrad(img, box, hx("657078"), hx("3c444a"))
    d.rectangle(box, outline=hx("b0aaa0"))
    d.line([(x0 + 4, y0 + 4), (x0 + 12, y0 + 12)], fill=hx("a4b0b4"))
    d.line([(x0 + 4, y0 + 9), (x0 + 8, y0 + 13)], fill=hx("829298"))
    d.line([(x0 + 2, y1 - 2), (x1 - 2, y1 - 2)], fill=hx("50504a"))


def shell(img, night=False):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("9a9572"), hx("70694f"))
    for x in range(0, W, 10):
        d.line([(x, 0), (x, FLOOR)], fill=hx("7f7a5c"))
        d.line([(x + 4, 0), (x + 4, FLOOR)], fill=hx("9d9876"))
    for y in range(18, FLOOR - 18, 24):
        for x in range(8 + ((y // 24) % 2) * 8, W, 32):
            d.polygon([(x, y), (x + 8, y + 5), (x, y + 10), (x - 8, y + 5)], outline=hx("918b67"))
    noise(img, (0, 0, W - 1, FLOOR), 5, 401)
    vgrad(img, (0, 100, W - 1, FLOOR), hx("5a4634"), hx("34261c"))
    d.rectangle([0, 98, W - 1, 100], fill=hx("7a6246"))
    d.rectangle([0, FLOOR - 4, W - 1, FLOOR], fill=hx("23170f"))
    for x in range(0, W, 34):
        d.rectangle([x + 3, 104, x + 28, FLOOR - 8], outline=hx("443022"))
        d.line([(x + 4, 105), (x + 27, 105)], fill=hx("6e5740"))

    if not night:
        wall_mirror(img, (126, 16, 160, 47))
        wall_mirror(img, (210, 53, 254, 86))
    for x, y in ((184, 24), (278, 65), (92, 80)):
        d.line([(x, y), (x + 3, y + 5), (x + 1, y + 9)], fill=hx("a79d79"))

    # Water stains and cracks
    for box in ([118, 2, 182, 42], [300, 0, 352, 34], [392, 64, 454, 110]):
        shadow(img, "ellipse", box, 0.26, 9, hx("7c6b4a"))
    d.line([(354, 12), (350, 28), (358, 43), (348, 58), (355, 74), (347, 92)], fill=hx("2a241c"))
    d.line([(102, 16), (110, 28), (104, 42), (114, 58)], fill=hx("3a3428"))
    d.line([(355, 75), (362, 84), (360, 96), (369, 108)], fill=hx("2a241c"))
    shadow(img, "ellipse", [24, 112, 120, 132], 0.28, 6)


def floor(img):
    floor_boards(img, FLOOR, H - 1, (250, -250), 20, hx("6a5138"), hx("503b28"), hx("2a1a12"), 405)
    noise(img, (0, FLOOR, W - 1, H - 1), 6, 406)
    # threadbare rug lying flat in the middle of the room
    R.quad(img, [(150, 0, 60), (350, 0, 60), (350, 0, 150), (150, 0, 150)], hx("666046"))
    R.quad(img, [(158, 0, 66), (342, 0, 66), (342, 0, 144), (158, 0, 144)], None, hx("968460"))
    for z in range(72, 144, 8):
        R.line(img, (154, 0, z), (346, 0, z), hx("575139"))
    a, b = R.P(150, 0, 60), R.P(350, 0, 150)
    noise(img, (int(a[0]) - 30, int(a[1]), int(b[0]) + 10, int(b[1])), 7, 407)


def door(img):
    """Room 6's door, on the back wall at the far left; it leads back out to the street."""
    d = ImageDraw.Draw(img)
    x0, x1, top = 8, 44, FLOOR - 88
    d.rectangle([x0 - 4, top - 4, x1 + 4, FLOOR], fill=WOOD_D)
    d.rectangle([x0 - 2, top - 2, x1 + 2, FLOOR], fill=hx("57412d"))
    vgrad(img, (x0, top, x1, FLOOR - 1), hx("6e5440"), hx("4e3a2a"))
    for (a, b) in ((top + 6, top + 38), (top + 46, FLOOR - 8)):
        d.rectangle([x0 + 5, a, x1 - 5, b], outline=hx("3a2a1c"))
        d.line([(x0 + 6, a + 1), (x1 - 6, a + 1)], fill=hx("7c6049"))
    d.ellipse([x1 - 9, top + 44, x1 - 5, top + 48], fill=hx("b89a58"))
    d.rectangle([x0 + 14, top + 14, x0 + 22, top + 22], fill=hx("a88a4c"))
    d.text((x0 + 16, top + 13), "6", fill=hx("2a1a10"))
    noise(img, (x0, top, x1, FLOOR), 4, 412)
    shadow(img, "rect", [x0 - 2, FLOOR - 2, x1 + 8, FLOOR + 6], 0.4, 3)


IRON, IRON_L, BRASS = hx("2a2422"), hx("4a403a"), hx("a49470")


CURTAINS = (
    ([(292, 22), (315, 22), (315, 98), (292, 98)], hx("c0b490")),
    ([(383, 22), (406, 22), (406, 98), (383, 98)], hx("b8ac88")),
)


def curtains(img, night=False):
    d = ImageDraw.Draw(img)
    d.line([(288, 19), (410, 19)], fill=hx("34261e"), width=2)
    for pts, col in CURTAINS:
        if night:
            col = mix(col, hx("584052"), 0.52)
        shade, highlight = mul(col, 0.68), mix(col, hx("eedac0"), 0.15)
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        d.rectangle([x0 + 2, 24, x1 + 2, 101], fill=hx("251a1c"))
        d.polygon(pts, fill=col)
        for x in range(x0 + 2, x1 - 1, 6):
            d.ellipse([x - 1, 17, x + 2, 23], outline=hx("7a6250"))
            d.line([(x, 25), (x + 1, 98)], fill=shade, width=2)
            d.line([(x + 2, 25), (x + 3, 97)], fill=highlight, width=2)
            d.ellipse([x, 96, x + 5, 100], fill=col)
            d.arc([x, 96, x + 5, 100], 0, 180, fill=shade)
        d.line([(x0 + 1, 24), (x1 - 1, 24)], fill=highlight)
        d.line([(x0, 26), (x0, 96)], fill=shade)


def chair(img):
    X0, X1, Z0, Z1 = 236, 258, 6, 24
    sh = R.P(X0, 0, Z1), R.P(X1, 0, Z0)
    shadow(img, "rect", [sh[0][0] - 1, sh[1][1], sh[1][0] + 3, sh[0][1] + 2], 0.4, 2)
    dark, mid = hx("3a281b"), hx("5a3c27")
    for x in (X0 + 1, X1 - 1):
        R.line(img, (x, 0, Z0 + 1), (x, 46, Z0 + 1), dark, 2)
    for y in (32, 38, 44):
        R.line(img, (X0 + 1, y, Z0 + 1), (X1 - 1, y, Z0 + 1), mid, 2)
    R.box(img, X0, X1, 18, 21, Z0, Z1, hx("6a4830"), top=hx("7e5a3c"), side=hx("4a311f"))
    for x in (X0 + 1, X1 - 1):
        R.line(img, (x, 0, Z1 - 1), (x, 18, Z1 - 1), dark, 2)
    R.line(img, (X0 + 1, 7, Z1 - 1), (X1 - 1, 7, Z1 - 1), dark)


def bottle(img):
    """The rotgut bottle, standing on the floor by the chair leg."""
    d = ImageDraw.Draw(img)
    bx, by = R.P(270, 0, 14)
    bx, by = int(bx), int(by)
    d.ellipse([bx - 4, by - 1, bx + 5, by + 2], fill=hx("3e2e20"))
    d.rectangle([bx - 2, by - 9, bx + 2, by], fill=hx("6a4a1c"))
    d.rectangle([bx - 1, by - 13, bx + 1, by - 9], fill=hx("5a3e18"))
    d.rectangle([bx - 2, by - 7, bx + 2, by - 4], fill=hx("d8ccaa"))
    d.point((bx - 1, by - 8), fill=hx("c49a52"))
    d.rectangle([bx - 1, by - 14, bx + 1, by - 13], fill=hx("2a1a10"))


def dresser(img, night=False):
    X0, X1, Z0, Z1 = 410, 466, 2, 22
    R.box(img, X0, X1, 0, 42, Z0, Z1, hx("4c3a2a"), top=hx("6a5038"), side=hx("2e2218"))
    for i, y in enumerate((30, 17, 4)):
        R.quad(img, [(X0 + 3, y, Z1), (X1 - 3, y, Z1), (X1 - 3, y + 10, Z1), (X0 + 3, y + 10, Z1)], None, hx("2a1a10"))
        R.line(img, (X0 + 4, y + 9, Z1), (X1 - 4, y + 9, Z1), hx("6e5440"))
        px, py = R.P((X0 + X1) / 2, y + 5, Z1)
        ImageDraw.Draw(img).rectangle([px - 3, py, px + 3, py + 1], fill=hx("b28a46"))
    a, b = R.P(X0, 42, Z0), R.P(X1, 0, Z1)
    noise(img, (int(a[0]), int(a[1]), int(b[0]), int(b[1])), 4, 410)
    if night:
        return
    # a clouded mirror hung over it
    d = ImageDraw.Draw(img)
    d.rectangle([420, 54, 456, 88], fill=WOOD_D)
    vgrad(img, (423, 57, 453, 85), hx("a7ad98"), hx("6d7266"))
    d.rectangle([430, 62, 446, 74], fill=hx("8a9aa4"))
    d.polygon([(432, 72), (438, 66), (444, 72)], fill=hx("6a7a58"))
    d.line([(428, 60), (436, 70)], fill=hx("c8ccb8"))
    shadow(img, "ellipse", [424, 58, 452, 84], 0.2, 6, hx("8a7a5a"))


def bulb(img):
    d = ImageDraw.Draw(img)
    d.line([(244, 0), (244, 26)], fill=hx("1e1814"))
    d.ellipse([239, 26, 249, 38], fill=hx("b8b09a"))
    d.rectangle([242, 24, 246, 28], fill=hx("625948"))
    d.line([(244, 38), (244, 48)], fill=hx("a69e88"))
    light(img, "ellipse", [210, -6, 278, 74], hx("b6b078"), 0.08, 16)


def details(img, night=False):
    d = ImageDraw.Draw(img)
    if night:
        # At night the wall keeps only two pieces: the lake painting over the bed and the mirror by the chair.
        lake_painting(img)
        night_mirror(img)
        grime(d)
        return
    # Motel print: a plain rectangular frame
    d.rectangle([77, 33, 119, 63], fill=hx("6c5237"))
    d.rectangle([81, 36, 115, 59], fill=hx("cabf9f"))
    d.rectangle([86, 40, 110, 54], fill=hx("8a8f6b"))
    d.rectangle([86, 50, 110, 54], fill=hx("7f684b"))
    d.line([(87, 42), (98, 47), (108, 41)], fill=hx("9ea47f"))
    d.line([(79, 64), (117, 64)], fill=hx("2c2018"))
    # a second print and a tear-off calendar, so the wall is not one brown wash
    d.rectangle([149, 27, 197, 59], fill=hx("5c4632"))
    d.rectangle([153, 30, 193, 55], fill=hx("8aa0b0"))
    d.rectangle([153, 43, 193, 55], fill=hx("6a7a58"))
    d.polygon([(168, 43), (176, 35), (184, 43)], fill=hx("d8d0c0"))
    d.line([(151, 60), (195, 60)], fill=hx("2c2018"))
    d.rectangle([206, 30, 228, 52], fill=hx("efe6d0"), outline=hx("6a5038"))
    d.line([(206, 36), (228, 36)], fill=hx("a04040"))
    d.text((210, 38), "27", fill=hx("2a2018"))
    grime(d)


PAINTING = (60, 20, 134, 68)  # outer frame of the lake painting over the bed (night)
MIRROR = (208, 52, 252, 90)  # outer frame of the mirror over the chair (night)


def _gilt_frame(img, box, depth, lit, mid, dark, seed, from_below=False):
    """A carved moulding: graded bevel, a bead run along the middle and rosettes at the corners.

    The bevel catches light on its top and left faces, or on its bottom and right faces when lit from below."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    near, far = (dark, lit) if from_below else (lit, dark)
    for i in range(depth):
        t = i / max(1, depth - 1)
        top = mix(near, mid, t)
        bot = mix(far, mid, t)
        d.line([(x0 + i, y0 + i), (x1 - i, y0 + i)], fill=top)
        d.line([(x0 + i, y0 + i), (x0 + i, y1 - i)], fill=top)
        d.line([(x0 + i, y1 - i), (x1 - i, y1 - i)], fill=bot)
        d.line([(x1 - i, y0 + i), (x1 - i, y1 - i)], fill=bot)
    d.rectangle([x0, y0, x1, y1], outline=mul(dark, 0.55))
    d.rectangle([x0 + depth, y0 + depth, x1 - depth, y1 - depth], outline=mul(dark, 0.6))
    m = depth // 2
    bead = mix(lit, (255, 240, 190), 0.4)
    bead_near, bead_far = (mid, bead) if from_below else (bead, mid)
    for x in range(x0 + depth + 1, x1 - depth, 3):
        d.point((x, y0 + m), fill=bead_near)
        d.point((x, y1 - m), fill=bead_far)
    for y in range(y0 + depth + 1, y1 - depth, 3):
        d.point((x0 + m, y), fill=bead_near)
        d.point((x1 - m, y), fill=bead_far)
    for cx, cy in ((x0 + m, y0 + m), (x1 - m, y0 + m), (x0 + m, y1 - m), (x1 - m, y1 - m)):
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=dark)
        d.rectangle([cx - 1, cy - 1, cx + 1, cy + 1], fill=lit)
        d.point((cx, cy), fill=mul(dark, 0.6))
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            d.point((cx + ox, cy + oy), fill=mid)


def _painting_ornament(d, box, lit, mid, dark):
    """Carved gilt ornament on the lake painting's frame: a shell crest, acanthus sprays and an egg-and-dart run.

    Lit from the bedside lamp below and to the right, so the lower and right-facing faces catch the light."""
    x0, y0, x1, y1 = box
    nx = (x0 + x1) // 2
    shine = mix(lit, (255, 240, 200), 0.45)
    # egg-and-dart along the outer edge of the moulding
    for x in range(x0 + 9, x1 - 8, 4):
        d.point((x, y0 + 1), fill=mid)
        d.point((x + 1, y0 + 1), fill=mul(dark, 0.8))
        d.point((x, y1 - 1), fill=shine)
        d.point((x + 1, y1 - 1), fill=mid)
    for y in range(y0 + 9, y1 - 8, 4):
        d.point((x0 + 1, y), fill=mid)
        d.point((x0 + 1, y + 1), fill=mul(dark, 0.8))
        d.point((x1 - 1, y), fill=shine)
        d.point((x1 - 1, y + 1), fill=mid)
    # acanthus sprays curling out of each corner rosette along both rails
    m = 3
    for cx, cy, sx, sy in ((x0 + m, y0 + m, 1, 1), (x1 - m, y0 + m, -1, 1), (x0 + m, y1 - m, 1, -1), (x1 - m, y1 - m, -1, -1)):
        leaf = shine if (sx < 0 or sy < 0) else mid
        d.line([(cx + 3 * sx, cy), (cx + 7 * sx, cy)], fill=leaf)
        d.point((cx + 5 * sx, cy - 1), fill=leaf)
        d.point((cx + 6 * sx, cy + 1), fill=mul(dark, 0.9))
        d.line([(cx, cy + 3 * sy), (cx, cy + 6 * sy)], fill=leaf)
        d.point((cx - 1, cy + 5 * sy), fill=leaf)
        d.point((cx + 1, cy + 5 * sy), fill=mul(dark, 0.9))
    # a scallop-shell cartouche standing proud of the top rail, flanked by two scrolls
    d.pieslice([nx - 7, y0 - 6, nx + 7, y0 + 8], 180, 360, fill=mid, outline=mul(dark, 0.6))
    for a in range(-75, 76, 25):
        ang = math.radians(a - 90)
        end = (nx + round(6 * math.cos(ang)), y0 + 1 + round(6 * math.sin(ang)))
        d.line([(nx, y0 + 1), end], fill=dark if a < 0 else mix(mid, lit, 0.6))
    d.line([(nx - 6, y0 + 1), (nx + 6, y0 + 1)], fill=lit)
    d.point((nx, y0), fill=shine)
    for sx in (nx - 11, nx + 8):
        d.ellipse([sx, y0 - 2, sx + 3, y0 + 1], fill=mid, outline=mul(dark, 0.7))
        d.point((sx + 2, y0), fill=shine)
    # a pendant leaf hanging under the bottom rail, catching the lamp
    d.polygon([(nx - 3, y1), (nx + 3, y1), (nx, y1 + 3)], fill=lit, outline=mid)
    d.point((nx + 1, y1 + 1), fill=shine)


def lake_painting(img, wall=True):
    """An oil of a mountain lake at sundown in a gilt frame: the one thing in the room someone chose."""
    import random
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = PAINTING
    nx = (x0 + x1) // 2
    if wall:
        # The bedside lamp is below and to the right, so the frame throws its shadow up and to the left.
        shadow(img, "rect", [x0 - 5, y0 - 6, x1 - 2, y1 - 3], 0.78, 2, hx("0c0a10"))
        shadow(img, "ellipse", [nx - 12, y0 - 12, nx + 4, y0 + 2], 0.6, 2, hx("0c0a10"))
        # hanging wire from a nail
        d.line([(x0 + 14, y0 + 2), (nx, y0 - 9), (x1 - 14, y0 + 2)], fill=hx("4a4232"))
        d.rectangle([nx - 1, y0 - 10, nx + 1, y0 - 9], fill=hx("2a2018"))
    lit, mid, dark = hx("e0b860"), hx("a87c34"), hx("5a3a16")
    _gilt_frame(img, PAINTING, 6, lit, mid, dark, 61, from_below=True)
    _painting_ornament(d, PAINTING, lit, mid, dark)
    # cream linen liner with a gilt sight edge; the liner's top and left bevels fall into shadow
    lx0, ly0, lx1, ly1 = x0 + 6, y0 + 6, x1 - 6, y1 - 6
    d.rectangle([lx0, ly0, lx1, ly1], fill=hx("d8cca8"))
    d.line([(lx0, ly0), (lx1, ly0)], fill=hx("a09474"))
    d.line([(lx0, ly0), (lx0, ly1)], fill=hx("a09474"))
    d.line([(lx0 + 1, ly1), (lx1, ly1)], fill=hx("f0e6c8"))
    d.line([(lx1, ly0 + 1), (lx1, ly1)], fill=hx("f0e6c8"))
    cx0, cy0, cx1, cy1 = lx0 + 2, ly0 + 2, lx1 - 2, ly1 - 2
    d.rectangle([cx0 - 1, cy0 - 1, cx1 + 1, cy1 + 1], outline=hx("c09040"))
    px = img.load()

    def put(x, y, col, k=1.0):
        if cx0 <= x <= cx1 and cy0 <= y <= cy1:
            old = px[x, y]
            px[x, y] = mix(old[:3], col[:3], k) + tuple(old[3:])

    # the canvas: sky, two mountain ranges, a lake, pines, a cabin and a rowboat
    hz = cy0 + 15  # shoreline
    vgrad(img, (cx0, cy0, cx1, cy0 + 8), hx("3e5cb8"), hx("b080a0"))
    vgrad(img, (cx0, cy0 + 8, cx1, hz), hx("b080a0"), hx("ffa050"))
    sx, sy = cx0 + 37, hz - 5
    for y in range(cy0, hz + 1):
        for x in range(cx0, cx1 + 1):
            k = max(0.0, 1 - math.hypot(x - sx, (y - sy) * 1.4) / 15) ** 2
            put(x, y, hx("ffd890"), 0.75 * k)
    # clouds: violet bodies with undersides lit orange by the low sun
    for (qx, qy, l) in ((cx0 + 2, cy0 + 2, 11), (cx0 + 17, cy0 + 4, 13), (cx0 + 42, cy0 + 1, 10), (cx0 + 6, cy0 + 8, 7)):
        d.line([(qx + 2, qy), (qx + l - 3, qy)], fill=hx("8a6a9c"))
        d.line([(qx, qy + 1), (qx + l, qy + 1)], fill=hx("b07a9c"))
        d.line([(qx + 1, qy + 2), (qx + l - 1, qy + 2)], fill=hx("ffb07a"))
        d.point((qx + l - 1, qy + 1), fill=hx("ffd0a0"))
        d.point((qx + 3, qy - 1), fill=hx("9a7aa8"))
    d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=hx("ffe8a8"))
    d.point((sx - 1, sy - 1), fill=hx("fffae0"))
    # a streak of cloud drawn across the sun
    d.line([(sx - 8, sy + 1), (sx + 7, sy + 1)], fill=hx("e08a6a"))
    d.line([(sx - 5, sy + 2), (sx + 5, sy + 2)], fill=hx("ffc888"))
    for (bx, by) in ((cx0 + 26, cy0 + 10), (cx0 + 30, cy0 + 8), (cx0 + 22, cy0 + 12)):
        d.point((bx - 1, by - 1), fill=hx("2a2030"))
        d.point((bx, by), fill=hx("2a2030"))
        d.point((bx + 1, by - 1), fill=hx("2a2030"))
    far = [(cx0, hz - 4), (cx0 + 6, hz - 9), (cx0 + 11, hz - 6), (cx0 + 19, hz - 13), (cx0 + 26, hz - 7),
           (cx0 + 31, hz - 9), (cx0 + 37, hz - 5), (cx0 + 45, hz - 11), (cx1, hz - 6), (cx1, hz), (cx0, hz)]
    d.polygon(far, fill=hx("6a5a98"))
    for (qx, qy) in ((cx0 + 6, hz - 9), (cx0 + 19, hz - 13), (cx0 + 31, hz - 9), (cx0 + 45, hz - 11)):
        # sunlit right flanks, shadowed gullies on the left
        d.polygon([(qx, qy), (qx + 4, qy + 4), (qx + 1, qy + 6)], fill=hx("a07aa0"))
        d.line([(qx - 1, qy + 2), (qx - 3, qy + 6)], fill=hx("4e4278"))
        d.point((qx + 2, qy + 5), fill=hx("c890a8"))
    for (qx, qy) in ((cx0 + 19, hz - 13), (cx0 + 45, hz - 11), (cx0 + 6, hz - 9)):
        d.polygon([(qx - 3, qy + 3), (qx, qy), (qx + 3, qy + 3), (qx + 1, qy + 2), (qx - 1, qy + 3)], fill=hx("fff4f0"))
        d.point((qx + 1, qy + 1), fill=hx("ffd8c0"))
        d.point((qx - 2, qy + 3), fill=hx("b0a0c8"))
    near = [(cx0, hz - 2), (cx0 + 8, hz - 5), (cx0 + 15, hz - 3), (cx0 + 30, hz - 1), (cx0 + 40, hz - 4),
            (cx1, hz - 2), (cx1, hz), (cx0, hz)]
    d.polygon(near, fill=hx("2e5a36"))
    for x in range(cx0 + 1, cx1, 2):
        d.point((x, hz - 1 - (x % 3 == 0)), fill=hx("1e4026"))
    d.line([(cx0 + 8, hz - 5), (cx0 + 15, hz - 3)], fill=hx("4a7a46"))
    d.line([(cx0 + 40, hz - 4), (cx1, hz - 2)], fill=hx("5a8048"))

    def pine(qx, base, h, col, lit):
        d.line([(qx, base), (qx, base - h)], fill=col)
        for k in range(h - 1):
            w = (k * 2) // 5 + (1 if (h - k) % 3 == 0 else 0)
            y = base - h + 1 + k
            d.line([(max(cx0, qx - w), y), (min(cx1, qx + w), y)], fill=col)
            if qx + w <= cx1:
                d.point((qx + w, y), fill=lit)
            if qx - w >= cx0 and w > 0:
                d.point((qx - w, y), fill=mul(col, 0.7))
        d.point((qx, base + 1), fill=hx("3a2416"))

    # the far shore: pines and a log cabin with a lit window and smoke from the chimney
    for qx, h in ((cx1 - 1, 13), (cx1 - 4, 10), (cx1 - 18, 7), (cx1 - 20, 5)):
        pine(qx, hz, h, hx("183020"), hx("8a7a3a"))
    kx = cx1 - 15
    d.rectangle([kx, hz - 4, kx + 7, hz], fill=hx("6a4028"))
    for yy in (hz - 3, hz - 1):
        d.line([(kx, yy), (kx + 7, yy)], fill=hx("4a2a18"))
    d.line([(kx + 7, hz - 4), (kx + 7, hz)], fill=hx("a06a3a"))
    d.polygon([(kx - 1, hz - 4), (kx + 3, hz - 8), (kx + 4, hz - 8), (kx + 8, hz - 4)], fill=hx("8a2a1c"))
    d.line([(kx + 4, hz - 8), (kx + 8, hz - 4)], fill=hx("d8603a"))
    d.line([(kx - 1, hz - 4), (kx + 8, hz - 4)], fill=hx("4a1810"))
    d.line([(kx + 6, hz - 8), (kx + 6, hz - 6)], fill=hx("5a4a40"))
    for i, (qx, qy) in enumerate(((kx + 6, hz - 9), (kx + 7, hz - 10), (kx + 7, hz - 11), (kx + 8, hz - 12))):
        put(qx, qy, hx("d8b0b0"), 0.8 - 0.15 * i)
    d.rectangle([kx + 1, hz - 3, kx + 2, hz - 2], fill=hx("ffd070"))
    d.point((kx + 1, hz - 3), fill=hx("fff0b0"))
    d.rectangle([kx + 4, hz - 3, kx + 5, hz], fill=hx("2a1810"))
    # the lake mirrors everything above the shoreline, broken into ripples and sinking into the water's blue
    rnd = random.Random(65)
    src = {(x, y): px[x, y][:3] for x in range(cx0, cx1 + 1) for y in range(cy0, hz + 1)}
    for i, y in enumerate(range(hz + 1, cy1 + 1)):
        water = mix(hx("8090c8"), hx("24406c"), i / max(1, cy1 - hz - 1))
        ry = hz - i
        shift = rnd.choice((-1, 0, 0, 1)) if i > 1 else 0
        k = min(0.92, 0.42 + 0.035 * i + (0.22 if i % 3 == 2 else 0))
        for x in range(cx0, cx1 + 1):
            if ry < cy0:
                c = water
            else:
                c = mix(mul(src[(min(cx1, max(cx0, x + shift)), ry)], 0.8), water, k)
            px[x, y] = c + tuple(px[x, y][3:])
    # the sun's path across the water, and its glitter on the ripples
    for i, y in enumerate(range(hz + 2, cy1 - 1, 2)):
        w = 5 - i
        if w > 0:
            d.line([(sx - w, y), (sx + 1 + w, y)], fill=hx("ffd890"))
            d.point((sx + w + 3, y + 1), fill=hx("e0a070"))
    for _ in range(14):
        qx, qy = rnd.randint(cx0 + 16, cx1 - 2), rnd.randint(hz + 3, cy1 - 2)
        d.line([(qx, qy), (qx + rnd.randint(1, 3), qy)], fill=hx("a8b0e0") if rnd.random() < 0.6 else hx("e8b890"))
    # the cabin window trembling in the lake, and a little jetty below the cabin
    for i, y in enumerate(range(hz + 2, hz + 11, 2)):
        put(kx + 1 + (i % 2), y, hx("ffd070"), 0.85 - 0.12 * i)
    d.line([(kx - 5, hz + 2), (kx + 3, hz + 1)], fill=hx("7a5030"))
    d.line([(kx - 5, hz + 3), (kx + 3, hz + 2)], fill=hx("3a2416"))
    for qx in (kx - 4, kx - 1, kx + 2):
        d.point((qx, hz + 4), fill=hx("2a1a10"))
    # a dark wooded bank in the left foreground, its edge warmed by the sunset; mossy rocks at the waterline
    d.polygon([(cx0, hz + 2), (cx0 + 6, hz + 3), (cx0 + 12, hz + 9), (cx0 + 15, cy1), (cx0, cy1)], fill=hx("1e3420"))
    d.line([(cx0 + 6, hz + 3), (cx0 + 12, hz + 9), (cx0 + 15, cy1)], fill=hx("4a5a2a"))
    for (qx, qy) in ((cx0 + 11, hz + 9), (cx0 + 13, cy1 - 3)):
        d.ellipse([qx - 1, qy - 1, qx + 2, qy + 1], fill=hx("5a5a62"))
        d.point((qx + 1, qy - 1), fill=hx("a8a0a0"))
        d.line([(qx - 1, qy + 2), (qx + 2, qy + 2)], fill=hx("2a3a58"))
    for qx, base, h in ((cx0 + 3, cy1 - 3, 22), (cx0 + 8, hz + 7, 15), (cx0 + 12, hz + 10, 9)):
        pine(qx, base, h, hx("14281a"), hx("5a7a3a"))
    # a white birch leaning out over the water
    d.line([(cx0 + 14, cy1 - 2), (cx0 + 15, hz + 3)], fill=hx("d8d0c0"))
    for qy in (hz + 5, hz + 8, hz + 12):
        d.point((cx0 + 14 + (qy > hz + 6), qy), fill=hx("2a2420"))
    for (qx, qy) in ((cx0 + 14, hz + 2), (cx0 + 16, hz + 2), (cx0 + 15, hz + 1), (cx0 + 17, hz + 4), (cx0 + 13, hz + 4)):
        d.point((qx, qy), fill=hx("c0b040") if (qx + qy) % 2 else hx("7a8a30"))
    # a rowboat with its oars out and a fisherman, his line slack in the water
    d.line([(cx0 + 20, cy1 - 4), (cx0 + 26, cy1 - 4)], fill=hx("5a3018"))
    d.line([(cx0 + 21, cy1 - 3), (cx0 + 25, cy1 - 3)], fill=hx("3a2010"))
    d.line([(cx0 + 21, cy1 - 1), (cx0 + 25, cy1 - 1)], fill=hx("1a2a48"))
    d.line([(cx0 + 18, cy1 - 2), (cx0 + 20, cy1 - 4)], fill=hx("c0a070"))
    d.line([(cx0 + 26, cy1 - 4), (cx0 + 28, cy1 - 2)], fill=hx("c0a070"))
    d.line([(cx0 + 23, cy1 - 6), (cx0 + 23, cy1 - 5)], fill=hx("a03020"))
    d.point((cx0 + 23, cy1 - 7), fill=hx("e0a080"))
    d.line([(cx0 + 24, cy1 - 6), (cx0 + 29, cy1 - 10)], fill=hx("8a7a60"))
    d.line([(cx0 + 29, cy1 - 10), (cx0 + 30, cy1 - 4)], fill=hx("a0a8c8"))
    # reeds with seed heads in the foreground, and the painter's signature
    for rx in (cx0 + 16, cx0 + 18, cx1 - 3, cx1 - 1, cx1 - 5):
        top = cy1 - 4 - (rx % 3 == 0)
        d.line([(rx, cy1), (rx + (rx % 2), top)], fill=hx("2a3a20"))
        d.point((rx + (rx % 2), top - 1), fill=hx("6a4a2a"))
    d.line([(cx1 - 11, cy1 - 1), (cx1 - 7, cy1 - 1)], fill=hx("a03020"))
    d.point((cx1 - 10, cy1 - 2), fill=hx("a03020"))
    noise(img, (cx0, cy0, cx1, cy1), 5, 62)
    # brass title plaque on the bottom rail
    d.rectangle([nx - 6, y1 - 4, nx + 6, y1 - 1], fill=hx("c8a050"), outline=hx("5a3a16"))
    d.line([(nx - 4, y1 - 3), (nx + 3, y1 - 3)], fill=hx("6a4a20"))
    d.point((nx + 5, y1 - 2), fill=hx("fff0b0"))


def night_mirror(img, wall=True):
    """A bevelled wall mirror in a carved walnut frame, its silvering failing at the edges."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = MIRROR
    cx = (x0 + x1) // 2
    if wall:
        shadow(img, "rect", [x0 + 2, y0 - 4, x1 + 4, y1 + 4], 0.55, 2)
    # carved crest: a broken pediment with two scrolls and a fan shell in the middle
    d.polygon([(x0 + 3, y0 + 1), (cx - 6, y0 - 4), (cx + 6, y0 - 4), (x1 - 3, y0 + 1)], fill=hx("5a3820"))
    d.line([(x0 + 3, y0), (cx - 6, y0 - 5)], fill=hx("b8844c"))
    d.line([(cx + 6, y0 - 5), (x1 - 3, y0)], fill=hx("b8844c"))
    d.line([(x0 + 5, y0 + 1), (cx - 6, y0 - 3)], fill=hx("2a1a0e"))
    d.line([(cx + 6, y0 - 3), (x1 - 5, y0 + 1)], fill=hx("2a1a0e"))
    for sx in (cx - 8, cx + 6):
        d.ellipse([sx, y0 - 7, sx + 3, y0 - 4], fill=hx("5a3820"), outline=hx("b8844c"))
        d.point((sx + 1, y0 - 6), fill=hx("2a1a0e"))
    d.pieslice([cx - 5, y0 - 11, cx + 5, y0 - 1], 180, 360, fill=hx("a87444"))
    for a in (-64, -32, 0, 32, 64):
        ang = math.radians(a - 90)
        d.line([(cx, y0 - 2), (cx + round(5 * math.cos(ang)), y0 - 2 + round(5 * math.sin(ang)))], fill=hx("5a3820"))
    d.point((cx, y0 - 2), fill=hx("e0b070"))
    _gilt_frame(img, MIRROR, 5, hx("a87444"), hx("6a4426"), hx("2a1a0e"), 63)
    gx0, gy0, gx1, gy1 = x0 + 5, y0 + 5, x1 - 5, y1 - 5
    # the glass: dark depth, a lighter bevel and the room faintly behind you
    vgrad(img, (gx0, gy0, gx1, gy1), hx("4a5866"), hx("1e242e"))
    d.rectangle([gx0 + 15, gy0 + 6, gx0 + 25, gy1 - 3], fill=hx("2a2a2c"))  # the reflected door across the room
    d.rectangle([gx0 + 17, gy0 + 8, gx0 + 23, gy0 + 15], outline=hx("3a3836"))
    d.point((gx0 + 17, gy0 + 20), fill=hx("a08a50"))
    d.line([(gx0 + 2, gy1 - 5), (gx1 - 2, gy1 - 5)], fill=hx("2e2c2a"))  # the reflected dado rail
    shine = hx("b4c4cc")
    for k, (l, c) in enumerate(((10, shine), (6, hx("8a9ca8")))):
        sx = gx0 + 2 + l + k * 3
        d.line([(sx, gy0 + 2), (sx - l + 1, gy0 + 1 + l)], fill=c)
    d.line([(gx1 - 4, gy1 - 3), (gx1 - 9, gy1 - 8)], fill=hx("6a7c88"))
    d.rectangle([gx0, gy0, gx1, gy1], outline=hx("a8b8c0"))
    d.line([(gx0 + 1, gy1 - 1), (gx1 - 1, gy1 - 1)], fill=hx("5e6c76"))
    d.line([(gx1 - 1, gy0 + 1), (gx1 - 1, gy1 - 1)], fill=hx("5e6c76"))
    # desilvering: dark freckles creeping in from the bottom corners
    import random
    rnd = random.Random(64)
    px = img.load()
    for _ in range(70):
        side = rnd.random() < 0.5
        x = gx0 + 2 + int(rnd.random() ** 2 * 10) if side else gx1 - 2 - int(rnd.random() ** 2 * 10)
        y = gy1 - 2 - int(rnd.random() ** 1.6 * 22)
        col = hx("1e1a14") if rnd.random() < 0.6 else hx("5a4e3a")
        px[x, y] = col + (255,) * (len(px[x, y]) - 3)
    # a crack running from the top-right corner
    d.line([(gx1 - 1, gy0 + 1), (gx1 - 6, gy0 + 8), (gx1 - 7, gy0 + 15)], fill=hx("c8d2d6"))
    d.line([(gx1 - 6, gy0 + 8), (gx1 - 2, gy0 + 11)], fill=hx("98a4aa"))
    d.line([(gx1 - 6, gy0 + 8), (gx1 - 11, gy0 + 6)], fill=hx("98a4aa"))
    # a postcard tucked into the corner of the frame
    d.polygon([(gx0 - 2, gy1 - 13), (gx0 + 9, gy1 - 15), (gx0 + 11, gy1 - 6), (gx0, gy1 - 4)], fill=hx("e8dcc0"))
    d.polygon([(gx0, gy1 - 12), (gx0 + 8, gy1 - 13), (gx0 + 9, gy1 - 9), (gx0 + 1, gy1 - 8)], fill=hx("60a0c8"))
    d.line([(gx0 + 1, gy1 - 8), (gx0 + 9, gy1 - 9)], fill=hx("e0c080"))
    d.line([(gx0 + 6, gy1 - 13), (gx0 + 6, gy1 - 9)], fill=hx("3a5a2a"))
    d.line([(gx0 + 4, gy1 - 12), (gx0 + 8, gy1 - 11)], fill=hx("3a6a2a"))
    d.line([(gx0 + 2, gy1 - 6), (gx0 + 8, gy1 - 7)], fill=hx("a08a70"))


def _painting_grade(size):
    """The bedside lamp sits below and to the right of the painting: warm at the bottom-right, shadowed at the top-left."""
    x0, y0, x1, y1 = PAINTING
    grade = Image.new("RGB", size, (232, 204, 168))
    px = grade.load()
    for y in range(max(0, y0 - 12), min(size[1], y1 + 6)):
        for x in range(max(0, x0 - 4), min(size[0], x1 + 4)):
            t = max(0.0, min(1.0, 0.55 * (x - x0) / (x1 - x0) + 0.45 * (y - y0) / (y1 - y0)))
            px[x, y] = mix((70, 64, 92), (255, 230, 180), t ** 1.15)
    return grade


def night_wall_glints(img):
    """After the night grade: both pieces repainted in their own light so their detail survives the dark.

    The painting takes the bedside lamp's warmth; the mirror stays cool and catches the neon from the window."""
    for paint_fn, grade in ((lake_painting, _painting_grade(img.size)), (night_mirror, (176, 168, 200))):
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        paint_fn(layer, wall=False)
        tint = grade if isinstance(grade, Image.Image) else Image.new("RGB", img.size, grade)
        rgb = ImageChops.multiply(layer.convert("RGB"), tint)
        img.paste(rgb, (0, 0), layer.getchannel("A"))
    x0, y0, x1, y1 = MIRROR
    gx0, gy0, gx1, gy1 = x0 + 5, y0 + 5, x1 - 5, y1 - 5
    # the neon grazes the glass from the window side: red above, blue below, fading leftwards
    for col, box in ((hx("c03048"), (gx1 - 10, gy0 + 1, gx1 + 4, gy0 + 14)), (hx("2a5ad0"), (gx1 - 10, gy0 + 14, gx1 + 4, gy1 - 1))):
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).ellipse(box, fill=110)
        m = m.filter(ImageFilter.GaussianBlur(2))
        clip = Image.new("L", img.size, 0)
        ImageDraw.Draw(clip).rectangle([gx0 + 1, gy0 + 1, gx1 - 1, gy1 - 1], fill=255)
        m = ImageChops.multiply(m, clip)
        img.paste(ImageChops.screen(img, Image.new("RGB", img.size, col)), (0, 0), m)
    d = ImageDraw.Draw(img)
    px0, py0, px1, py1 = PAINTING
    for (x, y) in ((px1 - 1, py0 + 14), (px1 - 1, py0 + 30), (px1 - 3, py1 - 3), (px1 - 18, py1 - 1), (px1 - 34, py1 - 1)):
        d.point((x, y), fill=hx("ffe0a0"))


def grime(d):
    # Scuffs and grime around the baseboards
    for x in range(18, W, 28):
        d.line([(x, FLOOR - 8), (x + 8, FLOOR - 4)], fill=hx("271b13"))
    for (x, y) in ((304, 168), (318, 176), (380, 190), (196, 200)):
        d.ellipse([x, y, x + 10, y + 4], fill=hx("4a392b"))


def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("4c4736"), hx("7a7255"))
    for x in range(0, W, 12):
        d.line([(x, 8), (x, TOP)], fill=hx("665f49"))
        d.line([(x + 5, 8), (x + 5, TOP)], fill=hx("877f62"))
    noise(img, (0, 0, W - 1, TOP), 4, 411)
    d.rectangle([0, 0, W - 1, 4], fill=hx("312418"))
    d.rectangle([0, 6, W - 1, 8], fill=hx("5e4b34"))
    d.line([(0, 8), (W, 8)], fill=hx("2a1d12"))
    shadow(img, "ellipse", [214, 0, 276, 30], 0.18, 8, hx("6f6145"))
    d.line([(248, 6), (242, 14), (248, 22)], fill=hx("443a2d"))


# --- night: Eleanor asleep under the sheet, a bedside lamp turned low, neon through the window -------------------

WIN = (302, 26, 396, 92)
LAMP_W = (163, 30, 13)  # world position of the bedside lamp's foot on the nightstand
NIGHT_EXTRA = [hx(c) for c in ("ff3a4a", "c8203a", "ff8090", "4a8cff", "2a5ad0", "a0c8ff", "fff2c8", "ffd27a",
                               "e09a44", "f0e6c0", "d8c690", "a8935e", "a83e3c", "3a2418", "1e120c", "3a2014", "5a3422", "8a5638",
                               "e8b890", "b88060", "5a3020", "f0dcb0", "a88a64")]


def window_night(img):
    """Frame and curtains only; the glass is painted after the room has been darkened."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WIN
    d.rectangle([x0, y0, x1, y1], fill=hx("101420"))
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 7], fill=WOOD_D)
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y1 + 4], fill=WOOD)
    d.rectangle([x0, y0, x1, y1], fill=hx("101420"))
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 8], fill=hx("4e3a2a"))
    curtains(img)


def glass_night(img, flicker=1.0):
    """Night outside the glass: rooftops against an indigo sky and the motel's neon sign right outside."""
    x0, y0, x1, y1 = WIN
    layer = Image.new("RGB", img.size)
    vgrad(layer, (x0, y0, x1, y1), hx("0a0c22"), hx("2a1838"))
    ld = ImageDraw.Draw(layer)
    for (sx, sy) in ((330, 32), (342, 29), (360, 36), (368, 30)):
        ld.point((sx, sy), fill=hx("a0a8c8"))
    ld.rectangle([x0, 64, x1, y1], fill=hx("0a0810"))
    ld.rectangle([x0, 58, 330, 64], fill=hx("0a0810"))
    ld.rectangle([352, 52, 366, 64], fill=hx("0a0810"))
    ld.point((340, 70), fill=hx("e8c060"))
    ld.point((358, 68), fill=hx("e8c060"))
    # neon: a red MOTEL sign and a blue VACANCY strip below it, glowing in the wet air
    light(layer, "ellipse", [326, 34, 398, 70], hx("c8203a"), 0.45 * flicker, 8)
    light(layer, "ellipse", [334, 64, 398, 90], hx("2a5ad0"), 0.45, 6)
    text(layer, (351, 49), "MOTEL", hx("ff3a4a"), size=8)
    text(layer, (351, 76), "VACANCY", hx("4a8cff"), size=8)
    ld.line([(330, 42), (392, 42)], fill=hx("ff8090"))
    ld.line([(330, 56), (392, 56)], fill=hx("ff8090"))
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    md.rectangle([x0, y0, x1, y1], fill=255)
    for pts, _ in CURTAINS:
        md.polygon(pts, fill=0)
    img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=hx("140c0a"), width=2)
    d.line([(x0, 58), (x1, 58)], fill=hx("140c0a"), width=2)
    d.rectangle([x0, y0, x1, y1], outline=hx("140c0a"))
    curtains(img, night=True)


def _ell(d, c, rx, ry, col):
    d.ellipse([c[0] - rx, c[1] - ry, c[0] + rx, c[1] + ry], fill=col)


def bed_night(img, rails=True):
    """Iron bed and mattress support; the neutral occupied linen is painted after the room grade."""
    X0, X1, Z0, Z1 = 52, 140, 4, 42
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z0)
    shadow(img, "rect", [a[0] - 2, b[1] - 2, b[0] + 6, a[1] + 3], 0.45, 3)
    for x, top in ((X0, 30), (X1, 46)):
        R.line(img, (x, 0, Z0), (x, top, Z0), IRON, 2)
    R.box(img, X0 + 2, X1 - 2, 12, 15, Z0 + 2, Z1 - 2, IRON_L)
    R.box(img, X0 + 2, X1 - 2, 15, 24, Z0 + 2, Z1 - 2, hx("cfc6ad"), top=hx("ddd4bc"), side=hx("a59c84"))
    # two pillows at the head end, the back one propped against the rail
    R.box(img, X1 - 17, X1 - 4, 24, 31, Z0 + 3, Z0 + 16, hx("d8d0ba"), top=hx("e6dfcc"), side=hx("b0a690"))
    R.box(img, X1 - 20, X1 - 4, 24, 28, Z0 + 12, Z1 - 5, hx("e2dac4"), top=hx("eee7d4"), side=hx("b8af98"))
    # The occupied drape is painted in screen space after lighting, not as rigid world-space quads.
    # the blanket kicked into a heap at the foot, half off the end
    R.quad(img, [(X0 - 2, 22, Z0 + 4), (X0 + 14, 27, Z0 + 6), (X0 + 18, 26, Z1 - 4), (X0 - 2, 22, Z1)],
           hx("6f7558"))
    R.quad(img, [(X0 + 2, 26, Z0 + 10), (X0 + 12, 29, Z0 + 12), (X0 + 14, 27, Z1 - 8), (X0 + 2, 25, Z1 - 6)],
           hx("8c9270"))
    R.line(img, (X0 + 4, 26, Z0 + 14), (X0 + 12, 27.5, Z1 - 10), hx("565b44"))
    if rails:
        bed_rails_night(img)
    R.quad(img, [(X0 - 1, 23, Z1), (X0 + 16, 24, Z1), (X0 + 14, 4, Z1 + 2), (X0 - 3, 6, Z1 + 2)], hx("6f7558"))
    R.line(img, (X0 + 6, 22, Z1 + 1), (X0 + 5, 6, Z1 + 2), hx("565b44"))


def bed_rails_night(img):
    X0, X1, Z0, Z1 = 52, 140, 4, 42
    d = ImageDraw.Draw(img)
    # No near side rail: the hanging sheet hides it, and drawn in front it read as a stray floor line.
    for x, top_, mid in ((X0, 30, 20), (X1, 46, 32)):
        R.line(img, (x, 0, Z1), (x, top_, Z1), IRON, 2)
        R.line(img, (x, top_, Z0), (x, top_, Z1), IRON, 2)
        R.line(img, (x, mid, Z0), (x, mid, Z1), IRON)
        for z in range(Z0 + 6, Z1 - 3, 6):
            R.line(img, (x, mid, z), (x, top_, z), IRON_L)
        for z in (Z0, Z1):
            px, py = R.P(x, top_ + 1.5, z)
            d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=BRASS)


# The wider lap adds six pixels before the mirrored head: net head shift is five right, two back.
ELEANOR_ORIGIN = (110, 112)


# Eleanor's legs under the cover, hip to toes, in screen space at mid-mattress depth:
# the near leg first, the far one a little deeper (higher on screen) and to the right.
LEGS = [(122, 123), (113, 121), (102, 120), (93, 122), (86, 123), (81, 121)]
FAR_LEG = [(x + 3, y - 5) for x, y in LEGS]
# The near head post; Eleanor's lap sheet must stop behind it rather than hang through the frame.
HEAD_POST_X = 134


def _leg_height(path, xx, yy, radius):
    distance = np.full(xx.shape, np.inf)
    along = np.zeros(xx.shape)
    lengths = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    travelled, total = 0.0, sum(lengths)
    for a, b, length in zip(path, path[1:], lengths):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = np.clip(((xx - a[0]) * dx + (yy - a[1]) * dy) / length ** 2, 0, 1)
        dist = np.hypot(xx - a[0] - t * dx, yy - a[1] - t * dy)
        nearest = dist < distance
        along[nearest] = (travelled + t * length)[nearest] / total
        distance = np.minimum(distance, dist)
        travelled += length
    # Thighs are fuller than shins; the feet lift the cover again at the far end.
    girth = radius * (1.15 - 0.45 * along + 0.35 * np.exp(-((along - 0.97) / 0.06) ** 2))
    return np.exp(-(distance / girth) ** 2), distance, girth


def body_mound(cloth, legs, radius=5.0, lift=1.2):
    """Shade leg-shaped height fields into flat linen: lamp-facing slopes lift, near slopes fall into shadow."""
    rgba = np.asarray(cloth).astype(float)
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[:h, :w].astype(float)
    fields = [_leg_height(path, xx, yy, radius) for path in legs]
    # Where the legs overlap the higher one wins, leaving a shallow valley between them.
    height = np.max([f[0] for f in fields], axis=0) * lift
    gy, gx = np.gradient(height)
    shade = 22 * height + 150 * gy - 40 * gx
    for near, far in zip(legs, legs[1:]):
        # The cover sags into a crease between neighbouring legs.
        gap, _, _ = _leg_height([((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(near, far)],
                                xx, yy, 1.2)
        shade -= 12 * gap
    # The cover pulls taut over the near shin and drops a soft shadow along the near side.
    _, distance, girth = fields[0]
    shade -= 16 * np.exp(-((distance - girth * 1.25) / 1.5) ** 2) * (yy > np.interp(xx, *zip(*sorted(legs[0]))))
    from .mansion import SHEET_FOLD, SHEET_LIT
    rgba[:, :, :3] = np.clip(rgba[:, :, :3] + shade[:, :, None], SHEET_FOLD, SHEET_LIT)
    return Image.fromarray(rgba.astype("uint8"), "RGBA")


def white_bed_linen(img, empty=False):
    from .mansion import linen_surface, SHEET, SHEET_SIDE
    for outline, center in (
        ([(124, 104), (134, 106), (138, 110), (136, 122), (131, 124), (122, 120), (122, 108)],
         (130, 113)),
        ([(121, 115), (133, 116), (138, 123), (133, 129), (120, 127), (117, 122)],
         (128, 122)),
    ):
        pillow = linen_surface((W, H), outline, [
            ([(125, center[1] + 4), (130, center[1] + 5), (135, center[1] + 2)], 1.1, 18),
        ], SHEET, loft=[(*center, 6, 5, 14)])
        ImageDraw.Draw(pillow).rectangle([HEAD_POST_X, 0, W, H], fill=(0, 0, 0, 0))
        img.paste(pillow, (0, TOP), pillow)
    # Screen coordinates follow the projected mattress: the lap rises at the head,
    # then the sheet turns over the near edge and hangs in unequal scallops.
    side = linen_surface((W, H), [
        (54, 128), (67, 130), (83, 129), (99, 131), (116, 129), (132, 128),
        (132, 144), (128, 155), (118, 156), (112, 153), (98, 155),
        (88, 152), (76, 154), (66, 151), (51, 152), (49, 146),
    ], [
        ([(59, 129), (62, 138), (59, 150)], 2.0, 23),
        ([(78, 130), (75, 137), (77, 146), (81, 153)], 2.3, 28),
        ([(99, 132), (104, 139), (101, 150)], 2.4, 26),
        ([(123, 129), (119, 138), (120, 148), (117, 154)], 1.7, 22),
    ], SHEET_SIDE, falloff=0.85)
    top = linen_surface((W, H), [
        (55, 118), (65, 115), (74, 116), (82, 113), (87, 112), (92, 109),
        (99, 106), (107, 105), (114, 107), (120, 111), (127, 113), (133, 117),
        (132, 128), (122, 132), (112, 131), (99, 134), (86, 131),
        (75, 132), (64, 130), (53, 133),
    ], [
        ([(58, 121), (65, 122), (73, 120)], 1.3, 17),
        ([(74, 116), (79, 121), (87, 123), (94, 128)], 1.7, 27),
        ([(102, 115), (96, 120), (98, 126), (107, 130)], 1.6, 25),
        ([(120, 119), (113, 123), (112, 128)], 1.5, 20),
        ([(61, 128), (68, 127), (73, 129)], 1.0, 14),
    ], SHEET, falloff=0.35)
    img.paste(side, (0, TOP), side)
    if empty:  # nobody under it: the sheet lies thrown back, rumpled but flat
        img.paste(top, (0, TOP), top)
        return
    img.paste(body_mound(top, [LEGS, FAR_LEG]), (0, TOP), top)
    # Cotton compressed under the seated hip and between the two pillows.
    shadow(img, "ellipse", [120, 145, 138, 157], 0.25, 2)


def sleeper(img):
    from PIL import ImageOps
    from .mansion import _eleanor_in_bed
    eleanor = ImageOps.mirror(_eleanor_in_bed())
    # Trim the lap sheet's spill past the near head post so the iron frame stays clean.
    alpha = eleanor.getchannel("A")
    ImageDraw.Draw(alpha).rectangle([HEAD_POST_X - ELEANOR_ORIGIN[0], 20, eleanor.width, eleanor.height], fill=0)
    eleanor.putalpha(alpha)
    img.paste(eleanor, ELEANOR_ORIGIN, eleanor)

def nightstand_night(img):
    X0, X1, Z0, Z1 = 148, 172, 3, 22
    R.box(img, X0, X1, 0, 30, Z0, Z1, hx("5a4130"), top=hx("74563e"), side=hx("3c2a1d"))
    R.quad(img, [(X0 + 2, 18, Z1), (X1 - 2, 18, Z1), (X1 - 2, 27, Z1), (X0 + 2, 27, Z1)], None, hx("2a1c12"))
    R.quad(img, [(X0 + 2, 3, Z1), (X1 - 2, 3, Z1), (X1 - 2, 15, Z1), (X0 + 2, 15, Z1)], None, hx("2a1c12"))
    for y in (22, 9):
        px, py = R.P((X0 + X1) / 2, y, Z1)
        ImageDraw.Draw(img).rectangle([px - 2, py, px + 2, py + 1], fill=hx("ac8a4a"))
    R.box(img, 150, 157, 30, 31.5, 13, 19, hx("5e5a52"), top=hx("8a857a"))  # ashtray
    R.box(img, 150, 153, 30, 36, 6, 9, hx("a9b2a6"), top=hx("d8e0d4"))  # half-empty glass


def lamp_night(img):
    """The little bedside lamp, its shade glowing, drawn after the relight."""
    d = ImageDraw.Draw(img)
    x, y, z = LAMP_W
    bx, by = R.P(x, y, z)
    d.ellipse([bx - 3, by - 1, bx + 3, by + 1], fill=hx("4a3420"))
    d.line([(bx, by), (bx, by - 9)], fill=hx("6a5030"), width=2)
    d.ellipse([bx - 2, by - 6, bx + 2, by - 2], fill=hx("8a6a3a"))
    shade = [(bx - 3, by - 16), (bx + 3, by - 16), (bx + 6, by - 9), (bx - 6, by - 9)]
    d.polygon(shade, fill=hx("ffd27a"))
    d.line([(bx - 1, by - 15), (bx - 3, by - 10)], fill=hx("fff2c8"))
    d.line([(bx + 2, by - 15), (bx + 4, by - 10)], fill=hx("e09a44"))
    d.line([(bx - 6, by - 9), (bx + 6, by - 9)], fill=hx("e09a44"))
    d.line([(bx - 3, by - 16), (bx + 3, by - 16)], fill=hx("c8803a"))
    light(img, "ellipse", [bx - 12, by - 24, bx + 12, by - 2], hx("ffd27a"), 0.3, 4)


def clothes(img):
    """Micah's trench coat flung over the chair back and his fedora dropped on the seat."""
    X0, X1, Z0, Z1 = 236, 258, 6, 24
    trench_coat(img, R.P(X0, 46, Z0 + 1), R.P(X1, 21, Z0 + 1))
    fedora(img, R.P(X0 + 12, 21, Z1 - 1))


COAT = dict(deep=hx("4e3818"), dark=hx("765a2a"), mid=hx("a07c40"), base=hx("b08a4a"), light=hx("c8a262"),
            lit=hx("dcbc80"), seam=hx("62481e"), button=hx("2e2014"), brass=hx("d8b050"))
LINING = (hx("d8c8a0"), hx("8a2a22"), hx("2a201a"))


def trench_coat(img, top_left, seat_right):
    """A belted, double-breasted trench coat folded over a chair back, lit from the lamp on the left.

    ``top_left`` is the screen point of the chair's top rail at its left post and ``seat_right`` the back of the
    seat at its right post; the coat is painted pixel by pixel around them so its details stay legible."""
    c = COAT
    d = ImageDraw.Draw(img)
    x0, y0 = round(top_left[0]), round(top_left[1])
    x1, y1 = round(seat_right[0]), round(seat_right[1])
    cx = (x0 + x1) // 2
    # the body hangs over the rail, wider than the chair, and bunches where it meets the seat
    body = [(x0 - 3, y0 + 2), (x0 + 2, y0 - 2), (x1 - 2, y0 - 2), (x1 + 3, y0 + 2), (x1 + 4, y1 - 3), (x1 + 2, y1),
            (x0 - 2, y1), (x0 - 4, y1 - 3)]
    d.polygon(body, fill=c["base"], outline=c["deep"])
    # broad vertical folds: shadow on the right of each ridge, light on its left
    for fx, depth in ((x0 + 3, 9), (cx + 4, 12), (x1 - 3, 8)):
        d.line([(fx, y0 + 6), (fx + 1, y1 - 2)], fill=c["dark"])
        d.line([(fx + 1, y0 + 8), (fx + 2, y1 - 3)], fill=c["mid"])
        d.line([(fx - 1, y0 + depth), (fx - 1, y1 - 2)], fill=c["light"])
    d.line([(x0 - 3, y0 + 3), (x0 - 3, y1 - 3)], fill=c["lit"])
    d.line([(x1 + 3, y0 + 3), (x1 + 3, y1 - 3)], fill=c["dark"])
    # the turned-up collar over the rail, with the check lining showing underneath
    collar = [(x0 + 1, y0 - 3), (cx - 1, y0 - 4), (cx + 1, y0 - 4), (x1 - 1, y0 - 3), (x1 - 3, y0 + 2),
              (x0 + 3, y0 + 2)]
    d.polygon(collar, fill=c["light"], outline=c["deep"])
    d.line([(x0 + 2, y0 - 3), (cx - 1, y0 - 4)], fill=c["lit"])
    pale, red, dark = LINING
    d.line([(cx - 4, y0 - 1), (cx + 4, y0 - 1)], fill=mix(pale, c["mid"], 0.45))
    for lx in (cx - 3, cx + 1):
        d.point((lx, y0 - 1), fill=red)
    d.point((cx + 3, y0 - 1), fill=dark)
    # notched lapels running down to the double-breasted front
    lap_y = y0 + 11
    d.polygon([(x0 + 3, y0 + 2), (cx - 2, y0 + 2), (cx, lap_y), (x0 + 5, y0 + 7)], fill=c["light"], outline=c["seam"])
    d.polygon([(x1 - 3, y0 + 2), (cx + 2, y0 + 2), (cx, lap_y), (x1 - 5, y0 + 7)], fill=c["mid"], outline=c["seam"])
    d.point((x0 + 5, y0 + 4), fill=c["deep"])
    d.point((x1 - 5, y0 + 4), fill=c["deep"])
    d.line([(cx, lap_y), (cx + 1, y1 - 1)], fill=c["seam"])
    for by in (lap_y + 1, lap_y + 5):
        for bx in (cx - 4, cx + 4):
            d.point((bx, by), fill=c["button"])
            d.point((bx - 1, by - 1), fill=c["light"])
    # shoulder epaulette and a gun flap on the left breast
    d.rectangle([x0 - 2, y0 + 1, x0 + 3, y0 + 2], fill=c["mid"], outline=c["seam"])
    d.point((x0 + 2, y0 + 1), fill=c["button"])
    d.line([(x0 + 1, y0 + 9), (x0 + 6, y0 + 8)], fill=c["seam"])
    # the belt, buckled, with its tail hanging down past the chair
    by = y1 - 6
    d.rectangle([x0 - 4, by, x1 + 4, by + 2], fill=c["dark"])
    d.line([(x0 - 4, by), (x1 + 4, by)], fill=c["mid"])
    d.rectangle([cx - 2, by - 1, cx + 2, by + 3], outline=c["brass"])
    d.point((cx - 2, by - 1), fill=hx("f0d890"))
    d.line([(cx, by), (cx, by + 2)], fill=c["deep"])
    d.polygon([(x1 + 3, by), (x1 + 6, by + 1), (x1 + 7, by + 16), (x1 + 5, by + 17), (x1 + 4, by + 2)], fill=c["dark"],
              outline=c["deep"])
    d.line([(x1 + 5, by + 2), (x1 + 6, by + 15)], fill=c["mid"])
    # slanted pockets either side of the belt
    d.line([(x0 + 1, by + 3), (x0 + 5, by + 5)], fill=c["seam"])
    d.line([(x1 - 1, by + 3), (x1 - 5, by + 5)], fill=c["seam"])
    # a sleeve slipped off the left side, almost to the floor, with its strapped cuff
    sl_top, sl_bot = y0 + 3, y1 + 16
    d.polygon([(x0 - 4, sl_top), (x0 + 1, sl_top + 2), (x0 - 1, sl_bot), (x0 - 7, sl_bot - 1)], fill=c["mid"],
              outline=c["deep"])
    d.line([(x0 - 4, sl_top + 2), (x0 - 6, sl_bot - 2)], fill=c["lit"])
    d.line([(x0 - 2, sl_top + 6), (x0 - 3, sl_top + 14)], fill=c["dark"])
    d.line([(x0 - 7, sl_bot - 4), (x0 - 1, sl_bot - 3)], fill=c["deep"])
    d.point((x0 - 3, sl_bot - 3), fill=c["brass"])
    d.line([(x0 - 6, sl_bot), (x0 - 2, sl_bot + 1)], fill=pale)


def fedora(img, centre):
    """A brown felt fedora, pinched at the front, with a dark band and bow; lit from the left."""
    d = ImageDraw.Draw(img)
    x, y = round(centre[0]), round(centre[1])
    felt_d, felt, felt_l, felt_lit = hx("140c06"), hx("3e2818"), hx("6e4a30"), hx("a87a4c")
    band = hx("0a0604")
    shadow(img, "ellipse", [x - 12, y - 1, x + 13, y + 6], 0.6, 1)
    # brim: the far half shaded, the near edge rolled down and catching the lamp
    d.ellipse([x - 11, y - 4, x + 11, y + 4], fill=felt, outline=felt_d)
    d.arc([x - 11, y - 4, x + 11, y + 4], 190, 350, fill=mix(felt, felt_d, 0.5))
    d.line([(x - 9, y + 2), (x + 2, y + 4)], fill=felt_lit)
    d.line([(x + 3, y + 3), (x + 8, y + 2)], fill=felt_l)
    d.point((x - 11, y - 1), fill=felt_lit)
    d.point((x + 11, y - 1), fill=felt_l)
    # tapered crown: lit left plane, shaded right plane, a centre crease and two front pinches
    crown = [(x - 7, y - 1), (x - 6, y - 7), (x - 4, y - 10), (x, y - 9), (x + 4, y - 10), (x + 6, y - 7),
             (x + 7, y - 1)]
    d.polygon(crown, fill=felt, outline=felt_d)
    d.polygon([(x - 6, y - 2), (x - 5, y - 7), (x - 3, y - 9), (x - 1, y - 8), (x - 2, y - 2)], fill=felt_l)
    d.line([(x - 5, y - 3), (x - 5, y - 7)], fill=felt_lit)
    d.line([(x - 3, y - 9), (x - 2, y - 9)], fill=felt_lit)
    d.polygon([(x + 2, y - 2), (x + 2, y - 7), (x + 5, y - 7), (x + 6, y - 2)], fill=mix(felt, felt_d, 0.45))
    d.line([(x, y - 8), (x, y - 5)], fill=felt_d)
    d.point((x - 2, y - 6), fill=felt_d)
    d.point((x + 2, y - 6), fill=felt_d)
    # grosgrain band with its bow on the left
    d.rectangle([x - 7, y - 3, x + 7, y - 2], fill=band)
    d.line([(x - 6, y - 3), (x - 2, y - 3)], fill=hx("3a2a1c"))
    d.rectangle([x - 6, y - 4, x - 5, y - 1], fill=band)


def relight_night(img):
    """Night grade: the room sinks into blue-black, the lamp keeps a warm pool by the bed, neon washes the floor."""
    lx, ly = R.P(LAMP_W[0], LAMP_W[1] + 12, LAMP_W[2])
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, (52, 56, 96)))
    warm = ImageChops.multiply(img, Image.new("RGB", img.size, (255, 196, 128)))
    warm = ImageChops.screen(warm, Image.new("RGB", img.size, (26, 12, 2)))
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    md.ellipse([lx - 150, ly - 90, lx + 150, ly + 110], fill=90)
    m = m.filter(ImageFilter.GaussianBlur(36))
    core = Image.new("L", img.size, 0)
    cd = ImageDraw.Draw(core)
    cd.ellipse([lx - 90, ly - 40, lx + 40, ly + 50], fill=200)  # the bed and her face
    cd.ellipse([lx - 50, ly - 50, lx + 50, ly + 70], fill=190)
    cd.polygon([(lx - 6, ly), (lx + 6, ly), (lx + 40, ly - 70), (lx - 40, ly - 70)], fill=120)  # up the wall
    core = core.filter(ImageFilter.GaussianBlur(14))
    m = ImageChops.lighter(m, core)
    out = Image.composite(warm, dark, m)
    # neon from the window: red and blue bands across the floor, the curtains backlit
    light(out, "polygon", [(310, 92), (350, 92), (330, 228), (230, 228)], hx("c8203a"), 0.12, 16)
    light(out, "polygon", [(350, 92), (394, 92), (470, 228), (330, 228)], hx("2a5ad0"), 0.11, 16)
    light(out, "rect", [292, 18, 406, 90], hx("a03050"), 0.22, 4)
    light(out, "ellipse", [270, 0, 430, 120], hx("6a2040"), 0.12, 20)
    return out


def paint_night(rails=False, empty=False):
    img = Image.new("RGB", (W, H))
    shell(img, night=True)
    floor(img)
    window_night(img)
    details(img, night=True)
    door(img)
    bed_night(img, rails=rails)
    nightstand_night(img)
    chair(img)
    clothes(img)
    dresser(img, night=True)
    bottle(img)
    img = relight_night(img)
    night_wall_glints(img)
    glass_night(img)
    lamp_night(img)
    img = tall(img, ceiling_night)
    pendant_night(img)
    vignette(img, 0.72, tint=(14, 12, 30), blur=46)
    lit_frame = img.copy() if rails else None
    white_bed_linen(img, empty=empty)
    if not rails:
        if not empty:
            sleeper(img)
    else:
        rail_mask = Image.new("RGBA", (W, H))
        bed_rails_night(rail_mask)
        img.paste(lit_frame.crop((0, TOP, W, TOP + H)), (0, TOP), rail_mask.getchannel("A"))
    return img


def ceiling_night(img):
    ceiling(img)
    band = img.crop((0, 0, W, TOP + 1))
    band = ImageChops.multiply(band, Image.new("RGB", band.size, (52, 56, 96)))
    img.paste(band, (0, 0))


PENDANT_X = 244  # the ceiling fixture over the mirror, in final (ceiling band included) pixels


def pendant_night(img):
    """The ceiling fixture, switched off: a stamped-tin canopy, a brass chain and socket, and a milk-glass
    schoolhouse globe. Unlit, it only catches the bedside lamp low on its left and the window neon on its right."""
    d = ImageDraw.Draw(img)
    cx = PENDANT_X
    brass_d, brass, brass_l = hx("2a2014"), hx("6a5230"), hx("b08a50")
    # the canopy: a ceiling rose plate and a small dome over the hook, their lower rims catching the lamp
    d.ellipse([cx - 8, 14, cx + 8, 21], fill=hx("2a2832"), outline=hx("16141c"))
    d.arc([cx - 8, 14, cx + 8, 21], 25, 155, fill=hx("5a5058"))
    for a in range(0, 360, 45):
        ang = math.radians(a)
        d.point((cx + round(6 * math.cos(ang)), 17 + round(2.4 * math.sin(ang))), fill=hx("3c3842"))
    d.ellipse([cx - 4, 16, cx + 4, 22], fill=brass, outline=brass_d)
    d.arc([cx - 4, 16, cx + 4, 22], 40, 150, fill=brass_l)
    d.point((cx - 1, 18), fill=hx("e0c080"))
    # the chain: links alternately face-on and edge-on
    for y in range(23, 40):
        k = (y - 23) % 4
        if k == 0:
            d.point((cx, y), fill=brass_l)
        elif k == 1:
            d.point((cx - 1, y), fill=brass)
            d.point((cx + 1, y), fill=brass_d)
        elif k == 2:
            d.point((cx - 1, y), fill=brass_l)
            d.point((cx + 1, y), fill=brass_d)
        else:
            d.point((cx, y), fill=brass_d)
    # the brass socket with its turn-key, and the fitter collar that grips the globe's neck
    d.rectangle([cx - 2, 40, cx + 2, 45], fill=brass)
    d.line([(cx - 2, 40), (cx - 2, 45)], fill=brass_l)
    d.line([(cx + 2, 40), (cx + 2, 45)], fill=brass_d)
    d.line([(cx - 1, 42), (cx + 2, 42)], fill=brass_d)
    d.line([(cx + 3, 41), (cx + 5, 41)], fill=brass)
    d.point((cx + 5, 40), fill=brass_l)
    d.rectangle([cx - 5, 46, cx + 5, 48], fill=brass, outline=brass_d)
    d.line([(cx - 4, 48), (cx + 1, 48)], fill=brass_l)
    for sx in (cx - 3, cx + 3):
        d.point((sx, 47), fill=brass_d)
    # the milk-glass globe, shaded per pixel as a sphere
    gy, rx, ry = 56.5, 8.6, 8.2
    lamp_dir = np.array((-0.72, 0.45, 0.52))
    lamp_dir /= np.linalg.norm(lamp_dir)
    neon_dir = np.array((0.86, -0.05, 0.5))
    neon_dir /= np.linalg.norm(neon_dir)
    px = img.load()
    for y in range(49, 65):
        for x in range(cx - 9, cx + 10):
            nx, ny = (x - cx) / rx, (y - gy) / ry
            r2 = nx * nx + ny * ny
            if r2 > 1:
                continue
            n = np.array((nx, ny, math.sqrt(1 - r2)))
            lam = max(0.0, float(n @ lamp_dir))
            neo = max(0.0, float(n @ neon_dir))
            neon = mix(hx("a02848"), hx("2850b0"), (y - 49) / 15)
            base = mix(hx("24242c"), hx("5c5c66"), 0.35 + 0.65 * n[2])
            c = [base[i] + lam ** 1.6 * (150, 104, 62)[i] + 0.7 * neo ** 2.2 * neon[i] for i in range(3)]
            if r2 > 0.82:
                c = [v * 0.78 for v in c]
            px[x, y] = tuple(min(255, int(v)) for v in c)
    # two painted rings round the globe, seen from below so they curve down at the front
    for ring in (51, 61):
        hw = rx * math.sqrt(max(0.0, 1 - ((ring - gy) / ry) ** 2)) - 1
        for x in range(cx - int(hw), cx + int(hw) + 1):
            y = ring + round(1.2 * (1 - ((x - cx) / hw) ** 2))
            px[x, y] = tuple(int(v * 0.7) for v in px[x, y][:3])
    # the open bottom: the glass lip and the dead bulb inside
    d.ellipse([cx - 5, 62, cx + 5, 66], fill=hx("6a6670"))
    d.ellipse([cx - 4, 63, cx + 4, 66], fill=hx("121018"))
    d.ellipse([cx - 1, 62, cx + 1, 64], fill=hx("5a5450"))
    d.point((cx - 1, 63), fill=hx("a89070"))
    d.arc([cx - 5, 62, cx + 5, 66], 110, 200, fill=hx("c8a080"))
    # highlights: neon on the right shoulder, the bedside lamp low on the left
    for (x, y, col) in ((cx + 5, 53, "e890b0"), (cx + 5, 54, "d880a8"), (cx + 6, 58, "8098e8"),
                        (cx - 5, 59, "ffd8a0"), (cx - 6, 57, "e0b080"), (cx - 3, 51, "a8a8b8")):
        d.point((x, y), fill=hx(col))


def build():
    night = paint_night()
    from .mansion import LINEN_PALETTE
    px0, py0, px1, py1 = PAINTING
    canvas = night.crop((px0 + 8, py0 + 8 + TOP, px1 - 8, py1 - 8 + TOP))
    palette = palette_of(night, 102) + NIGHT_EXTRA + LINEN_PALETTE + palette_of(canvas, 14)
    save(pixelize(night, palette), "rooms", "motel_night.png")
    rail_mask = Image.new("RGBA", (W, H))
    bed_rails_night(rail_mask)
    alpha = Image.new("L", night.size)
    alpha.paste(rail_mask.getchannel("A"), (0, TOP))
    foreground = pixelize(paint_night(rails=True), palette).convert("RGBA")
    foreground.putalpha(alpha)
    save(foreground, "rooms", "motel_night_rails.png")
    save(pixelize(paint_night(empty=True), palette), "rooms", "motel_empty.png")
    eleanor_rise(palette)
    return night


def eleanor_rise(palette):
    """Bed-scale, lamp-lit Eleanor and the one sheet she holds; points are in final room pixels."""
    from .sprites import action_strip
    import numpy as np
    anchor, position = (64, 100), (110, 194)

    def local(p):
        return (round(p[0] - position[0] + anchor[0]), round(p[1] - position[1] + anchor[1]))

    frames = []
    # Head, shoulder, hip, knee, foot, supporting hand.
    poses = [
        ((125, 146), (115, 151), (93, 153), (76, 155), (57, 160), (108, 157)),
        ((124, 138), (116, 148), (95, 155), (78, 157), (59, 162), (110, 163)),
        ((123, 130), (119, 144), (102, 159), (83, 160), (64, 163), (111, 165)),
        ((124, 127), (122, 141), (108, 159), (94, 166), (85, 174), (132, 162)),
        ((121, 125), (121, 139), (113, 159), (102, 168), (102, 184), (130, 158)),
        ((116, 123), (116, 137), (110, 158), (105, 174), (102, 191), (125, 159)),
        ((110, 121), (111, 135), (106, 155), (104, 175), (102, 192), (116, 155)),
        ((105, 119), (106, 133), (104, 154), (102, 174), (102, 192), (108, 149)),
        ((102, 119), (103, 133), (103, 153), (102, 174), (102, 192), (103, 145)),
    ]
    for index, points in enumerate(poses):
        img = Image.new("RGBA", (128, 104))
        d = ImageDraw.Draw(img)
        head, shoulder, hip, knee, foot, hand = [np.array(local(p), float) for p in points]
        skin, shade, hair = hx("e8b890"), hx("b88060"), hx("3a2014")
        _ell(d, tuple(shoulder + (0, 4)), 4, 5, skin)
        # The same hem drapes over the near mattress edge, then gathers around her planted feet.
        gather = max(0, 1 - index / 5)
        front = [tuple(shoulder + (-5, 6)), tuple(hip + (-7, 5)), tuple(knee + (-6, 4)),
                 tuple(foot + (-6, 1)), tuple(foot + (-5, 1 + 16 * gather)),
                 tuple(knee + (4, 2 + 15 * gather)), tuple(hip + (7, 1 + 15 * gather)),
                 tuple(shoulder + (5, 6))]
        d.polygon(front, fill=hx("cfc6ad"), outline=hx("a88a64"))
        d.line([tuple(shoulder + (4, 8)), tuple(hip + (5, 2)), tuple(knee + (4, 3)), tuple(foot + (4, 0))],
               fill=hx("a88a64"), width=2)
        for a, b in ((shoulder + (-3, 7), hip + (-3, 5)), (hip + (2, 3), knee + (2, 3)),
                     (knee + (-2, 4), foot + (-2, 0))):
            d.line([tuple(a), tuple(b)], fill=hx("f0dcb0"))
        if gather:
            d.line([tuple(knee + (0, 5)), tuple(knee + (1, 2 + 15 * gather))], fill=hx("a88a64"))
        d.line([tuple(head + (0, 4)), tuple(shoulder)], fill=skin, width=4)
        d.line([tuple(shoulder + (2, 4)), tuple(hand)], fill=shade, width=2)
        d.line([tuple(shoulder + (1, 3)), tuple(hand)], fill=skin, width=1)
        grip = shoulder + (-3, 7)
        d.line([tuple(shoulder + (-4, 3)), tuple(grip)], fill=skin, width=2)
        d.line([tuple(shoulder + (-5, 7)), tuple(shoulder + (5, 7))], fill=hx("f0dcb0"), width=2)
        _ell(d, (head[0] + 2, head[1] + 2), 6, 7 if index > 1 else 4, hair)
        if index > 1:
            d.polygon([(head[0] + 3, head[1] - 3), (head[0] + 6, head[1] + 3),
                       (head[0] + 7, head[1] + 10), (head[0] + 9, head[1] + 17),
                       (head[0] + 4, head[1] + 18), (head[0] + 3, head[1] + 8)], fill=hair)
            d.line([(head[0] + 5, head[1] + 5), (head[0] + 4, head[1] + 10),
                    (head[0] + 7, head[1] + 15)], fill=hx("5a3422"))
        _ell(d, (head[0], head[1]), 4, 5, skin)
        d.arc([head[0] - 5, head[1] - 6, head[0] + 5, head[1] + 4], 180, 330, fill=hx("8a5638"), width=2)
        d.line([(head[0] - 3, head[1] - 1), (head[0] - 1, head[1] - 1)], fill=hx("3a2418"))
        d.point((head[0] - 4, head[1] + 1), fill=hx("fff2c8"))
        d.point((head[0] - 3, head[1] + 3), fill=hx("a83e3c"))
        alpha = img.getchannel("A")
        img = pixelize(img, palette, spread=4).convert("RGBA")
        img.putalpha(alpha)
        frames.append((img, tuple(head)))
    action_strip("eleanor_sheet_rise", frames, [0.18, 0.24, 0.28, 0.26, 0.3, 0.25, 0.24, 0.24, 0.3], anchor=anchor)
