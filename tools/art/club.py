"""A secretive private club: curtained privees, lounge, and a shadowy stage room."""
import math
import random
from PIL import Image, ImageDraw
from .common import (W, H, TOP, FULL_H, tall, hx, mix, mul, clamp, vgrad, noise, light, shadow, vignette, pixelize,
                     save, floor_boards)

FLOOR = 146
WALL_TOP = hx("241117")
WALL_MID = hx("34161d")
WALL_LOW = hx("24100f")
WOOD = hx("5a3320")
WOOD_DARK = hx("24140c")
WOOD_DEEP = hx("180d08")
VELVET = hx("6e1620")
VELVET_DARK = hx("38070e")
BRASS = hx("b68c42")
LAMPLIGHT = hx("f0c272")


def ceiling_band(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("13080c"), WALL_TOP)
    d.rectangle([0, 0, W - 1, 3], fill=WOOD_DEEP)
    d.rectangle([0, 4, W - 1, 6], fill=WOOD)
    d.line([(0, 4), (W, 4)], fill=mul(WOOD, 1.2))
    d.rectangle([0, 8, W - 1, TOP], fill=hx("1c0d11"))
    for x in range(0, W, 28):
        d.rectangle([x, 0, x + 10, 6], fill=hx("20120e"))
    for x in range(0, W, 10):
        d.line([(x, 10), (x, TOP)], fill=hx("1a0c10"))
    noise(img, (0, 0, W - 1, TOP), 4, 701)


def panel_wall(img, floor_y, seed):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, floor_y), WALL_MID, WALL_LOW)
    d.rectangle([0, 92, W - 1, floor_y], fill=WOOD_DARK)
    d.line([(0, 91), (W, 91)], fill=WOOD)
    d.line([(0, floor_y), (W, floor_y)], fill=WOOD_DEEP)
    for x in range(6, W, 36):
        d.rectangle([x, 98, min(W - 6, x + 28), floor_y - 7], outline=hx("3a2216"))
        d.line([(x + 1, 99), (min(W - 7, x + 27), 99)], fill=mul(WOOD, 1.1))
    for y in range(8, 90, 12):
        for x in range((y // 12) % 2 * 8, W, 16):
            d.polygon([(x, y + 5), (x + 5, y), (x + 10, y + 5), (x + 5, y + 10)], fill=hx("3a1a20"))
    noise(img, (0, 0, W - 1, floor_y), 4, seed)


def room_shell(img, floor_y, vp, seed):
    d = ImageDraw.Draw(img)
    panel_wall(img, floor_y, seed)
    d.polygon([(0, 0), (112, 0), (156, floor_y), (0, floor_y)], fill=hx("18090d"))
    d.polygon([(W - 113, 0), (W - 1, 0), (W - 1, floor_y), (324, floor_y)], fill=hx("18090d"))
    d.polygon([(108, 0), (W - 109, 0), (324, floor_y), (156, floor_y)], fill=mul(WALL_MID, 1.08))
    d.line([(156, floor_y), (324, floor_y)], fill=mul(WOOD, 0.8))
    floor_boards(img, floor_y, H - 1, vp, 18, hx("4a2a1a"), hx("2e180f"), hx("150907"), seed + 10)
    noise(img, (0, floor_y, W - 1, H - 1), 5, seed + 20)


def drape(img, box, seed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for x in range(x0, x1, 4):
        col = VELVET if (x // 4) % 2 else VELVET_DARK
        d.rectangle([x, y0, min(x1, x + 3), y1], fill=col)
    d.rectangle([x0, y0 - 3, x1, y0], fill=BRASS)
    light(img, "rect", [x0, y0, x0 + 6, y1], hx("ff9070"), 0.15, 3)
    noise(img, (x0, y0, x1, y1), 3, seed)


def lamp(full_img, x, top_y, pool_box, cone_box=None):
    d = ImageDraw.Draw(full_img)
    d.line([(x, 0), (x, top_y - 9)], fill=WOOD_DEEP)
    d.polygon([(x - 8, top_y - 9), (x + 8, top_y - 9), (x + 6, top_y + 3), (x - 6, top_y + 3)], fill=BRASS)
    d.line([(x - 7, top_y - 8), (x + 7, top_y - 8)], fill=mul(BRASS, 1.2))
    d.ellipse([x - 3, top_y - 3, x + 3, top_y + 3], fill=LAMPLIGHT)
    if cone_box:
        x0, y0, x1, y1 = cone_box
        light(full_img, "polygon", [(x - 2, top_y + 1), (x + 2, top_y + 1), (x1, y1), (x0, y1)], LAMPLIGHT, 0.08, 10)
    light(full_img, "ellipse", pool_box, LAMPLIGHT, 0.06, 12)


def sofa(img, box, seed):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], 9, fill=VELVET_DARK, outline=WOOD_DEEP)
    d.rounded_rectangle([x0 + 4, y0 - 16, x1 - 4, y0 + 8], 8, fill=VELVET)
    d.rounded_rectangle([x0 - 4, y0 - 10, x0 + 10, y1], 6, fill=VELVET)
    d.rounded_rectangle([x1 - 10, y0 - 10, x1 + 4, y1], 6, fill=VELVET)
    d.line([(x0 + 10, y0 + 5), (x1 - 10, y0 + 5)], fill=VELVET_DARK)
    d.rounded_rectangle([x0 + 10, y0 + 7, x1 - 10, y0 + 15], 2, fill=mul(VELVET, 0.8), outline=VELVET_DARK)
    for px in range(x0 + 16, x1 - 12, 18):
        d.line([(px, y0 - 10), (px, y0 + 2)], fill=mul(VELVET, 0.65))
        d.point((px + 1, y0 - 4), fill=mul(VELVET, 1.4))
        d.line([(px, y0 + 8), (px, y0 + 14)], fill=VELVET_DARK)
    d.line([(x0 + 5, y0 - 13), (x1 - 5, y0 - 13)], fill=mul(VELVET, 1.25))
    for px in (x0 + 4, x1 - 6):
        d.rectangle([px, y1, px + 2, y1 + 4], fill=WOOD_DEEP)
    noise(img, (x0, y0 - 16, x1, y1), 3, seed)
    shadow(img, "ellipse", [x0 + 4, y1 - 1, x1 - 4, y1 + 8], 0.45, 4)


def low_table(img, box, seed, glasses=2):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.ellipse([x0, y0, x1, y0 + 7], fill=WOOD_DEEP)
    d.ellipse([x0 + 1, y0, x1 - 1, y0 + 5], fill=mul(WOOD, 0.95))
    cx = (x0 + x1) // 2
    d.line([(cx, y0 + 5), (cx, y1)], fill=WOOD_DEEP, width=2)
    d.line([(cx - 7, y1), (cx + 7, y1)], fill=WOOD_DEEP)
    for i in range(glasses):
        gx = x0 + 8 + i * 10
        d.rectangle([gx, y0 - 6, gx + 3, y0], fill=hx("a0a6ad"))
        d.rectangle([gx + 1, y0 - 4, gx + 2, y0 - 1], fill=hx("b47028"))
    noise(img, (x0, y0, x1, y1), 2, seed)


HALL_VP = (240, 96)  # eye level of a standing figure at the back of the hall
HALL_BACK = (64, 416)  # back wall span; the side walls recede from its edges


def hp(u, h, s):
    """Hall perspective: u = offset from centre, h = height above floor (back-wall px), s = nearness."""
    return (HALL_VP[0] + u * s, HALL_VP[1] + (FLOOR - HALL_VP[1] - h) * s)


def side_quad(side, s0, s1, h0, h1):
    u = (HALL_BACK[1] - HALL_VP[0]) * (1 if side == "right" else -1)
    return [hp(u, h0, s0), hp(u, h1, s0), hp(u, h1, s1), hp(u, h0, s1)]


def hall_walls(img):
    d = ImageDraw.Draw(img)
    bx0, bx1 = HALL_BACK
    vgrad(img, (bx0, 0, bx1, FLOOR), hx("2e1219"), hx("1e0b10"))
    for y in range(34, 100, 12):
        for x in range(bx0 + (y // 12) % 2 * 8, bx1, 16):
            d.polygon([(x, y + 4), (x + 4, y), (x + 8, y + 4), (x + 4, y + 8)], fill=hx("341620"))
    d.rectangle([bx0, 0, bx1, 22], fill=hx("1a0a0e"))
    d.line([(bx0, 23), (bx1, 23)], fill=WOOD)
    d.line([(bx0, 24), (bx1, 24)], fill=WOOD_DEEP)
    d.rectangle([bx0, 104, bx1, FLOOR], fill=WOOD_DARK)
    d.line([(bx0, 103), (bx1, 103)], fill=mul(WOOD, 1.15))
    d.line([(bx0, 104), (bx1, 104)], fill=WOOD)
    for x in range(bx0 + 6, bx1 - 20, 30):
        d.rectangle([x, 110, x + 24, FLOOR - 9], outline=hx("3a2216"))
        d.line([(x + 1, 111), (x + 23, 111)], fill=mul(WOOD, 1.05))
    d.rectangle([bx0, FLOOR - 5, bx1, FLOOR], fill=WOOD_DEEP)
    for side in ("left", "right"):
        s_edge = (HALL_VP[0] - 0) / (HALL_VP[0] - bx0) + 0.05
        d.polygon(side_quad(side, 1.0, s_edge, 0, 240), fill=hx("1a090d"))
        d.polygon(side_quad(side, 1.0, s_edge, 0, 62), fill=hx("160b07"))
        d.line(side_quad(side, 1.0, s_edge, 62, 62)[1:3], fill=hx("3a2014"))
        d.line(side_quad(side, 1.0, s_edge, 121, 121)[1:3], fill=hx("2a160e"))
        d.polygon(side_quad(side, 1.0, s_edge, 0, 5), fill=WOOD_DEEP)
        d.line([hp(-176 if side == "left" else 176, 0, 1.0), hp(-176 if side == "left" else 176, 260, 1.0)],
               fill=hx("0e0507"))
    noise(img, (0, 0, W - 1, FLOOR + 20), 3, 141)


def street_door(img):
    d = ImageDraw.Draw(img)
    d.polygon(side_quad("left", 1.05, 1.33, 0, 90), fill=WOOD_DEEP)
    d.polygon(side_quad("left", 1.08, 1.30, 0, 84), fill=hx("2a160d"))
    for h0, h1 in ((10, 38), (46, 76)):
        d.polygon(side_quad("left", 1.11, 1.18, h0, h1), outline=hx("1a0c07"))
        d.polygon(side_quad("left", 1.20, 1.27, h0, h1), outline=hx("1a0c07"))
    kx, ky = hp(-176, 40, 1.12)
    d.ellipse([kx - 1, ky - 1, kx + 1, ky + 1], fill=BRASS)
    lx, ly = hp(-176, 84, 1.08)
    d.line([(lx, ly + 1), hp(-176, 0, 1.08)], fill=hx("4a2a18"))


def lounge_arch(img):
    d = ImageDraw.Draw(img)

    def arch(s0, s1, h_spring, h_top):
        sm, rs = (s0 + s1) / 2, (s1 - s0) / 2
        pts = [hp(176, 0, s0), hp(176, h_spring, s0)]
        for i in range(1, 12):
            a = math.pi * i / 12
            pts.append(hp(176, h_spring + (h_top - h_spring) * math.sin(a), sm - rs * math.cos(a)))
        return pts + [hp(176, h_spring, s1), hp(176, 0, s1)]

    d.polygon(arch(1.02, 1.32, 70, 98), fill=WOOD_DEEP)
    d.polygon(arch(1.04, 1.30, 68, 92), fill=hx("4a2416"))
    d.polygon(arch(1.07, 1.30, 66, 86), fill=hx("3e1e12"))
    light(img, "polygon", arch(1.10, 1.30, 50, 70), hx("c07838"), 0.3, 8)
    light(img, "polygon", [hp(176, 0, 1.06), hp(176, 0, 1.30), (330, 220), (350, 172)], LAMPLIGHT, 0.1, 14)


def curtain_panel(px, y0, y1, x_at, folds, phase, seed):
    """Paints one velvet panel between x_at(y) -> (left, right) edges, with folds following its shape."""
    rnd = random.Random(seed)
    hi, lo, deep = hx("8c2230"), hx("4a0c14"), hx("16030a")
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, y1 - y0)
        xl, xr = x_at(y)
        if xr - xl < 1:
            continue
        for x in range(int(xl), int(xr) + 1):
            u = (x - xl) / max(1.0, xr - xl)
            f = 0.5 + 0.5 * math.sin(2 * math.pi * u * folds + phase)
            col = mix(deep, mix(lo, hi, f), 0.35 + 0.65 * f)
            col = mul(col, 1.12 - 0.5 * t)
            if x - xl < 1.5 or xr - x < 1.5:
                col = mul(col, 0.55)
            n = rnd.randint(-3, 3)
            px[x, y] = (clamp(col[0] + n), clamp(col[1] + n), clamp(col[2] + n))


def privee(img, x0, x1, y0, numeral, seed):
    """A recessed private room in the back wall, its velvet curtains drawn on darkness."""
    d = ImageDraw.Draw(img)
    y1 = FLOOR
    vx, vy = HALL_VP
    left_of_centre = (x0 + x1) / 2 < vx

    def inner(x, y, k):
        return (vx + (x - vx) * k, vy + (y - vy) * k)

    d.rectangle([x0 - 7, y0 - 15, x1 + 7, y1], fill=WOOD_DEEP)
    d.rectangle([x0 - 5, y0 - 13, x1 + 5, y1], fill=hx("3a2014"))
    d.line([(x0 - 5, y0 - 13), (x1 + 5, y0 - 13)], fill=mul(WOOD, 1.3))
    d.rectangle([x0 - 9, y0 - 18, x1 + 9, y0 - 15], fill=WOOD)
    d.line([(x0 - 9, y0 - 18), (x1 + 9, y0 - 18)], fill=BRASS)
    for x in (x0 - 4, x1 + 1):
        d.line([(x, y0 - 11), (x, y1 - 1)], fill=hx("4c2a18"))
        d.line([(x + 2, y0 - 11), (x + 2, y1 - 1)], fill=WOOD_DEEP)
    cx = (x0 + x1) // 2
    d.rectangle([cx - 7, y0 - 11, cx + 7, y0 - 4], fill=hx("7a5a2a"), outline=hx("2a1a0c"))
    for i in range(numeral):
        nx = cx - (numeral - 1) * 2 + i * 4
        d.line([(nx, y0 - 9), (nx, y0 - 6)], fill=hx("1a0e06"))

    d.rectangle([x0, y0, x1, y1], fill=hx("050203"))
    k = 0.9
    ix0, iy0 = inner(x0, y0, k)
    ix1, iy1 = inner(x1, y1, k)
    d.polygon([(x0, y0), (x1, y0), (ix1, iy0), (ix0, iy0)], fill=hx("0c0507"))
    d.polygon([(x0, y1), (x1, y1), (ix1, iy1), (ix0, iy1)], fill=hx("120609"))
    if left_of_centre:
        d.polygon([(x0, y0), (ix0, iy0), (ix0, iy1), (x0, y1)], fill=hx("1e0b10"))
    else:
        d.polygon([(x1, y0), (ix1, iy0), (ix1, iy1), (x1, y1)], fill=hx("1e0b10"))

    bx0, by0 = inner(x0 + 8, 112, 0.72)
    bx1, by1 = inner(x1 - 8, 132, 0.72)
    d.rounded_rectangle([bx0, by0, bx1, by1], 3, fill=hx("12060a"))
    d.line([(bx0 + 2, by0), (bx1 - 2, by0)], fill=hx("1c0a0e"))
    gx, gy = inner(cx + (5 if left_of_centre else -5), 128, 0.76)
    d.point((gx, gy), fill=hx("3a2a26"))

    cx0, cy0 = (int(ix0) + 1, int(iy0) + 9)
    cx1, cy1 = (int(ix1) - 1, int(iy1))
    gap_c = (cx0 + cx1) / 2 + (3 if left_of_centre else -3)
    h = cy1 - cy0

    def gap(y):
        t = (y - cy0) / max(1, h)
        return 0.6 + 9 * t ** 2.4

    px = img.load()
    curtain_panel(px, cy0, cy1, lambda y: (cx0, gap_c - gap(y)), 4, 0.6, seed)
    curtain_panel(px, cy0, cy1, lambda y: (gap_c + gap(y), cx1), 4, 2.2, seed + 1)

    rnd = random.Random(seed + 2)
    for x in range(cx0, cx1 + 1, 2):
        dy = rnd.randint(0, 1)
        d.line([(x, cy1 - 1 + dy), (x + 1, cy1 - 1 + dy)], fill=hx("2a060c"))
    d.rectangle([cx0 - 1, cy0 - 9, cx1 + 1, cy0 - 1], fill=hx("5a1018"))
    for x in range(cx0, cx1, 8):
        d.chord([x - 1, cy0 - 5, x + 9, cy0 + 4], 0, 180, fill=hx("6e1620"))
        d.arc([x - 1, cy0 - 5, x + 9, cy0 + 4], 0, 180, fill=hx("2a060c"))
        d.point((x + 4, cy0 + 4), fill=BRASS)
    d.line([(cx0 - 1, cy0 - 9), (cx1 + 1, cy0 - 9)], fill=BRASS)
    for tx in (cx0 + 2, cx1 - 2):
        d.line([(tx, cy0 + 26), (tx, cy0 + 36)], fill=hx("8a6a30"))
        d.polygon([(tx - 1, cy0 + 36), (tx + 1, cy0 + 36), (tx + 2, cy0 + 41), (tx - 2, cy0 + 41)], fill=BRASS)

    shadow(img, "rect", [cx0, cy0, cx1, cy0 + 14], 0.4, 4)
    shadow(img, "polygon", [(gap_c - 14, cy1), (gap_c + 14, cy1), (gap_c + 4, cy0 + h // 3), (gap_c - 4, cy0 + h // 3)],
           0.35, 5)
    shadow(img, "rect", [x0 - 10, y1 - 2, x1 + 10, y1 + 6], 0.55, 3)


def sconce(img, x, y):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 2, y + 2, x + 2, y + 9], fill=hx("6a4c22"))
    d.line([(x, y + 9), (x, y + 13)], fill=BRASS)
    d.polygon([(x - 5, y - 6), (x + 5, y - 6), (x + 3, y + 2), (x - 3, y + 2)], fill=hx("d8a860"))
    d.line([(x - 5, y - 6), (x + 5, y - 6)], fill=hx("fff0c0"))
    light(img, "ellipse", [x - 10, y - 36, x + 10, y - 2], LAMPLIGHT, 0.22, 6)
    light(img, "ellipse", [x - 22, y - 18, x + 22, y + 34], LAMPLIGHT, 0.16, 12)
    light(img, "ellipse", [x - 4, y - 6, x + 4, y + 1], hx("fff2c8"), 0.55, 2)


def cigar_stand(img, x0, x1, y0):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0 + 10, x1, FLOOR], fill=WOOD_DARK, outline=WOOD_DEEP)
    d.line([(x0 + 1, y0 + 11), (x1 - 1, y0 + 11)], fill=mul(WOOD, 1.25))
    d.rectangle([x0 + 4, y0 + 16, x1 - 4, FLOOR - 5], outline=hx("3a2216"))
    d.rectangle([x0 - 1, y0, x1 + 1, y0 + 10], fill=hx("2a2224"), outline=BRASS)
    for row, yy in enumerate((y0 + 3, y0 + 6)):
        for x in range(x0 + 2 + row, x1 - 2, 3):
            d.line([(x, yy), (x + 1, yy)], fill=hx("6a3a1e"))
    d.line([(x0 + 1, y0 + 1), (x0 + 7, y0 + 1)], fill=hx("c8c0b8"))
    shadow(img, "rect", [x0 - 3, FLOOR - 1, x1 + 3, FLOOR + 4], 0.5, 2)


def painting(img, x0, y0, x1, y1):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=hx("5a4220"), outline=hx("2a1a0a"))
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=hx("1c1410"))
    vgrad(img, (x0 + 4, y0 + 4, x1 - 4, y1 - 4), hx("2a2018"), hx("120c0a"))
    cx = (x0 + x1) // 2
    d.ellipse([cx - 6, y0 + 10, cx + 4, y0 + 22], fill=hx("4a3428"))
    d.polygon([(cx - 14, y1 - 4), (cx - 8, y0 + 22), (cx + 6, y0 + 22), (cx + 12, y1 - 4)], fill=hx("2c1c18"))
    light(img, "rect", [x0, y0, x1, y0 + 10], LAMPLIGHT, 0.12, 4)


def hall_scene():
    img = Image.new("RGB", (W, H))
    floor_boards(img, FLOOR, H - 1, HALL_VP, 16, hx("3e2216"), hx("2a150c"), hx("120705"), 111)
    noise(img, (0, FLOOR, W - 1, H - 1), 4, 121)
    hall_walls(img)
    street_door(img)
    lounge_arch(img)
    privee(img, 84, 170, 58, 1, 131)
    privee(img, 310, 396, 58, 2, 137)
    painting(img, 214, 44, 266, 90)
    cigar_stand(img, 222, 258, 112)
    d = ImageDraw.Draw(img)
    rug = [hp(-62, 0, 1.3), hp(62, 0, 1.3), hp(62, 0, 2.5), hp(-62, 0, 2.5)]
    d.polygon(rug, fill=hx("3a0f16"))
    d.polygon([hp(-54, 0, 1.36), hp(54, 0, 1.36), hp(54, 0, 2.4), hp(-54, 0, 2.4)], outline=hx("8a6a34"))
    d.polygon([hp(0, 0, 1.55), hp(34, 0, 1.9), hp(0, 0, 2.2), hp(-34, 0, 1.9)], outline=hx("6a1a22"))
    noise(img, (40, 158, 440, 224), 3, 151)
    for x in (192, 288):
        sconce(img, x, 74)
    for x0, x1 in ((84, 170), (310, 396)):
        light(img, "ellipse", [x0 - 8, FLOOR - 4, x1 + 8, FLOOR + 22], LAMPLIGHT, 0.08, 10)
    shadow(img, "rect", [0, 0, HALL_BACK[0] + 2, H - 1], 0.35, 14, hx("12050a"))
    shadow(img, "rect", [HALL_BACK[1] - 2, 0, W - 1, H - 1], 0.25, 14, hx("12050a"))
    shadow(img, "rect", [0, FLOOR, W - 1, FLOOR + 6], 0.3, 4)
    full = tall(img, ceiling_band)
    fd = ImageDraw.Draw(full)
    lx, ly = 240, TOP + 16
    fd.line([(lx, 0), (lx, ly - 8)], fill=WOOD_DEEP)
    fd.polygon([(lx - 10, ly), (lx + 10, ly), (lx + 6, ly - 8), (lx - 6, ly - 8)], fill=hx("7a5a26"))
    fd.line([(lx - 10, ly), (lx + 10, ly)], fill=BRASS)
    fd.ellipse([lx - 3, ly - 1, lx + 3, ly + 3], fill=LAMPLIGHT)
    light(full, "polygon", [(lx - 4, ly), (lx + 4, ly), (lx + 70, TOP + 200), (lx - 70, TOP + 200)], LAMPLIGHT, 0.08, 12)
    light(full, "ellipse", [lx - 80, TOP + 160, lx + 80, TOP + 222], LAMPLIGHT, 0.2, 16)
    light(full, "ellipse", [222, TOP + 104, 258, TOP + 124], LAMPLIGHT, 0.18, 6)
    vignette(full, 0.75, tint=(30, 10, 14), blur=50)
    shadow(full, "rect", [0, FULL_H - 30, W - 1, FULL_H - 1], 0.3, 14, hx("300c10"))
    return full


def lounge_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, FLOOR, HALL_VP, 201)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([12, 62, 60, 142], 5, fill=hx("100609"), outline=WOOD_DEEP)
    d.rounded_rectangle([420, 54, 468, 146], 5, fill=hx("100609"), outline=WOOD_DEEP)
    drape(img, (436, 58, 464, 142), 211)
    d.polygon([(152, 152), (328, 152), (356, 205), (124, 205)], fill=hx("4a141b"))
    d.polygon([(162, 156), (318, 156), (342, 198), (138, 198)], outline=BRASS)
    sofa(img, (68, 136, 174, 162), 220)
    sofa(img, (306, 136, 412, 162), 221)
    sofa(img, (180, 112, 300, 138), 222)
    low_table(img, (198, 126, 282, 140), 225, glasses=3)
    for x in (108, 240, 372):
        d.line([(x, 86), (x, 124)], fill=hx("1c0c10"))
        d.rectangle([x - 12, 82, x + 12, 86], fill=BRASS)
    for box in ([40, 46, 170, 138], [310, 46, 440, 138], [176, 54, 304, 138]):
        light(img, "ellipse", box, LAMPLIGHT, 0.04, 18)
    light(img, "ellipse", [146, 96, 338, 178], hx("9a2830"), 0.1, 16)
    shadow(img, "rect", [0, 0, 56, FLOOR], 0.22, 10, hx("20090c"))
    shadow(img, "rect", [W - 56, 0, W - 1, FLOOR], 0.22, 10, hx("20090c"))
    full = tall(img, ceiling_band)
    for x, pool in ((108, [60, TOP + 72, 158, TOP + 190]), (240, [182, TOP + 44, 298, TOP + 164]),
                    (372, [322, TOP + 72, 420, TOP + 190])):
        lamp(full, x, TOP + 10, pool, (x - 18, TOP + 82, x + 18, TOP + 126))
    vignette(full, 0.68, tint=(34, 12, 18), blur=50)
    return full


def stage_backdrop(img):
    d = ImageDraw.Draw(img)
    d.polygon([(156, 40), (324, 40), (346, 110), (134, 110)], fill=hx("110708"))
    drape(img, (168, 44, 312, 110), 301)
    d.polygon([(184, 110), (296, 110), (314, 146), (166, 146)], fill=WOOD_DARK)
    d.line([(184, 110), (296, 110)], fill=mul(WOOD, 1.1))
    for x in range(188, 296, 12):
        d.line([(x, 111), (240 + (x - 240) * 1.3, 146)], fill=hx("3a2216"))
    d.polygon([(166, 146), (314, 146), (314, 152), (166, 152)], fill=WOOD_DEEP)
    d.line([(166, 146), (314, 146)], fill=mul(WOOD, 1.15))


def stage_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, 136, (240, -180), 320)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 136), (W - 1, 136), (W - 1, H - 1), (0, H - 1)], fill=hx("12070a"))
    d.polygon([(168, 132), (312, 132), (362, H - 1), (118, H - 1)], fill=hx("1c0b0f"))
    for x in range(120, 360, 12):
        d.line([(x, 160), (x - 12, 230)], fill=hx("18080c"))
    stage_backdrop(img)
    d.rounded_rectangle([14, 58, 66, 146], 16, fill=hx("090407"), outline=WOOD)
    drape(img, (18, 76, 32, 145), 302)
    for i, y in enumerate((78, 94, 110)):
        col = mix(hx("45202a"), hx("201018"), i / 3)
        for side in (-1, 1):
            for j in range(4):
                x = 240 + side * (90 + j * 26 + i * 3)
                d.rounded_rectangle([x - 10, y, x + 10, y + 12], 3, fill=col, outline=WOOD_DEEP)
                d.line([(x - 7, y + 2), (x + 7, y + 2)], fill=mul(col, 1.3))
                d.rectangle([x - 9, y + 10, x + 9, y + 14], fill=mul(col, 0.65))
    shadow(img, "rect", [0, 72, W - 1, H - 1], 0.26, 18, hx("22090c"))
    full = tall(img, ceiling_band)
    fd = ImageDraw.Draw(full)
    fd.line([(326, 0), (326, 76)], fill=BRASS, width=2)
    fd.polygon([(316, 78), (333, 82), (326, 94), (310, 87)], fill=hx("3a3034"), outline=WOOD_DEEP)
    fd.line([(311, 87), (326, 94)], fill=hx("fff0c2"), width=2)
    light(full, "polygon", [(313, 90), (325, 94), (278, TOP + 146), (204, TOP + 146)], hx("fff0c2"), 0.12, 5)
    light(full, "ellipse", [192, TOP + 112, 290, TOP + 148], hx("f8d28a"), 0.20, 7)
    vignette(full, 0.82, tint=(26, 8, 12), blur=58)
    shadow(full, "rect", [0, TOP + 144, W - 1, H + TOP], 0.12, 20, hx("160609"))
    return full


def build():
    hall = hall_scene()
    lounge = lounge_scene()
    stage = stage_scene()
    out = {
        "club_hall.png": pixelize(hall, n=128),
        "club_lounge.png": pixelize(lounge, n=128),
        "club_stage.png": pixelize(stage, n=128),
    }
    for name, img in out.items():
        save(img, "rooms", name)
    return out["club_hall.png"]
