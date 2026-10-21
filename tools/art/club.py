"""A secretive private club: curtained privees, lounge, and a shadowy stage room."""
import math
import os
import random
from PIL import Image, ImageDraw
from .common import (W, H, TOP, FULL_H, ROOT, tall, hx, mix, mul, clamp, vgrad, noise, light, shadow, vignette,
                     pixelize, palette_of, save, floor_boards)

FLOOR = 146
# the hall's portrait, reduced from an original picture: antler tips down to the collar and tie
PAINTING_SRC = os.path.join(ROOT, "tools", "art", "src", "club_painting.png")
PAINTING_CROP = (125, 0, 705, 774)
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

    # the curtains hang in the frame itself, the pelmet tucked under the lintel, so they read as the privee's door
    cx0, cy0 = x0 + 1, y0 + 9
    cx1, cy1 = x1 - 1, y1
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


def painting_source():
    """The stag-headed member from the original picture: antlers, head and the collar and tie, no robe."""
    with Image.open(PAINTING_SRC) as src:
        return src.convert("RGB").crop(PAINTING_CROP)


def painting(img, x0, y0, x1, y1):
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=hx("5a4220"), outline=hx("2a1a0a"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=mul(hx("5a4220"), 1.4))
    d.rectangle([x0 + 3, y0 + 3, x1 - 3, y1 - 3], fill=hx("0c0908"))
    box = (x0 + 4, y0 + 4, x1 - 4, y1 - 4)
    bw, bh = box[2] - box[0] + 1, box[3] - box[1] + 1
    src = painting_source()
    scale = min(bw / src.width, bh / src.height)
    w, h = max(1, round(src.width * scale)), max(1, round(src.height * scale))
    # the original is lit cold; warm and dim it so it hangs in the hall's lamplight
    face = Image.blend(src.resize((w, h), Image.BOX), Image.new("RGB", (w, h), hx("3a2414")), 0.18)
    img.paste(face, (box[0] + (bw - w) // 2, box[1] + (bh - h) // 2))
    cx = (x0 + x1) // 2
    d.rectangle([cx - 10, y0 - 3, cx + 10, y0 - 1], fill=BRASS)
    d.line([(cx - 10, y0 - 3), (cx + 10, y0 - 3)], fill=hx("e8c880"))
    light(img, "rect", [x0, y0, x1, y0 + 14], LAMPLIGHT, 0.12, 4)


def hall_scene():
    img = Image.new("RGB", (W, H))
    floor_boards(img, FLOOR, H - 1, HALL_VP, 16, hx("3e2216"), hx("2a150c"), hx("120705"), 111)
    noise(img, (0, FLOOR, W - 1, H - 1), 4, 121)
    hall_walls(img)
    street_door(img)
    lounge_arch(img)
    privee(img, 84, 170, 58, 1, 131)
    privee(img, 310, 396, 58, 2, 137)
    painting(img, 215, 32, 265, 96)
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
    lounge_shell(img)
    lounge_alcove(img)
    hall_arch(img)
    stage_curtain(img)
    lounge_rug(img)
    for x in (156, 324):
        standard_lamp(img, x, 64)
    chesterfield(img, (180, 112, 300, 138), 222, cushions=3)
    chesterfield(img, (68, 136, 174, 162), 220, cushions=2, pillow="left", tone=0.86)
    chesterfield(img, (306, 136, 412, 162), 221, cushions=2, pillow="right", tone=0.86)
    lounge_table(img, (198, 126, 282, 140))
    light(img, "ellipse", [146, 96, 338, 178], hx("9a2830"), 0.1, 16)
    shadow(img, "rect", [0, 0, 56, FLOOR], 0.22, 10, hx("20090c"))
    shadow(img, "rect", [W - 56, 0, W - 1, FLOOR], 0.22, 10, hx("20090c"))
    full = tall(img, ceiling_band)
    for x, pool in ((108, [60, TOP + 72, 158, TOP + 190]), (372, [322, TOP + 72, 420, TOP + 190])):
        pendant(full, x, TOP + 12, pool)
    vignette(full, 0.68, tint=(34, 12, 18), blur=50)
    return full


def lounge_shell(img):
    """A flat back wall: damask above a panelled wainscot, a gilt picture rail, the boards running to it."""
    d = ImageDraw.Draw(img)
    panel_wall(img, FLOOR, 201)
    d.rectangle([0, 0, W - 1, 4], fill=WOOD_DEEP)
    d.line([(0, 5), (W - 1, 5)], fill=mul(WOOD, 1.2))
    d.line([(0, 7), (W - 1, 7)], fill=hx("6a4a24"))
    d.line([(0, 22), (W - 1, 22)], fill=hx("7a5a2a"))
    d.line([(0, 23), (W - 1, 23)], fill=WOOD_DEEP)
    for x in range(10, W, 36):
        d.rectangle([x + 2, 102, x + 24, FLOOR - 11], outline=hx("2a180e"))
        d.line([(x + 3, 103), (x + 23, 103)], fill=hx("4a2c1a"))
    d.rectangle([0, FLOOR - 5, W - 1, FLOOR], fill=WOOD_DEEP)
    d.line([(0, FLOOR - 5), (W - 1, FLOOR - 5)], fill=WOOD)
    floor_boards(img, FLOOR, H - 1, HALL_VP, 18, hx("4a2a1a"), hx("2e180f"), hx("150907"), 211)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 221)


def lounge_alcove(img):
    """The arched alcove behind the long sofa: gilt architrave, panelled reveals, a mirror lit by a picture light."""
    d = ImageDraw.Draw(img)
    x0, x1, spring, top = 170, 310, 52, 16
    cx = (x0 + x1) // 2
    # architrave
    d.rectangle([x0 - 8, spring, x1 + 8, FLOOR], fill=WOOD_DEEP)
    d.pieslice([x0 - 8, top - 8, x1 + 8, 2 * spring - top + 8], 180, 360, fill=WOOD_DEEP)
    d.rectangle([x0 - 6, spring, x1 + 6, FLOOR], fill=hx("4a2a18"))
    d.pieslice([x0 - 6, top - 6, x1 + 6, 2 * spring - top + 6], 180, 360, fill=hx("4a2a18"))
    d.arc([x0 - 6, top - 6, x1 + 6, 2 * spring - top + 6], 180, 360, fill=hx("8a6a34"))
    d.arc([x0 - 3, top - 3, x1 + 3, 2 * spring - top + 3], 190, 350, fill=BRASS)
    for x in (x0 - 6, x1 + 2):
        d.line([(x + 1, spring), (x + 1, FLOOR)], fill=hx("6a4422"))
        d.line([(x + 3, spring), (x + 3, FLOOR)], fill=WOOD_DEEP)
        d.rectangle([x - 1, spring - 2, x + 5, spring + 2], fill=hx("7a5a2a"), outline=WOOD_DEEP)
    # the back of the niche, darker than the room, damask faint on it
    d.rectangle([x0, spring, x1, FLOOR], fill=hx("2a0c14"))
    d.pieslice([x0, top, x1, 2 * spring - top], 180, 360, fill=hx("2a0c14"))
    vgrad(img, (x0 + 8, spring, x1 - 8, FLOOR), hx("3a121a"), hx("1e080c"))
    for y in range(28, 96, 10):
        for x in range(x0 + 12 + (y // 10) % 2 * 6, x1 - 10, 12):
            d.point((x, y), fill=hx("4a1a22"))
    # the reveals: the alcove has depth, panelled on each side
    for a, b, col in ((x0, x0 + 8, hx("1a060a")), (x1 - 8, x1, hx("240a10"))):
        d.rectangle([a, spring, b, FLOOR], fill=col)
        for p0, p1 in ((spring + 6, 90), (98, FLOOR - 6)):
            d.rectangle([a + 2, p0, b - 2, p1], outline=hx("3a1a14"))
    d.arc([x0 + 4, top + 4, x1 - 4, 2 * spring - top - 4], 180, 360, fill=hx("1a060a"))
    # a dado and panels inside
    d.rectangle([x0 + 8, 96, x1 - 8, FLOOR], fill=hx("26140c"))
    d.line([(x0 + 8, 95), (x1 - 8, 95)], fill=hx("6a4422"))
    for px in range(x0 + 12, x1 - 20, 24):
        d.rectangle([px, 100, px + 18, FLOOR - 6], outline=hx("3a2216"))
    # a gilt oval mirror, catching the picture light
    d.ellipse([cx - 20, 34, cx + 20, 84], fill=hx("6a4a1c"), outline=hx("2a1a0a"))
    d.ellipse([cx - 18, 36, cx + 18, 82], fill=BRASS)
    for a in range(0, 360, 20):
        v = (math.cos(math.radians(a)), math.sin(math.radians(a)))
        d.point((cx + round(v[0] * 19), 59 + round(v[1] * 24)), fill=hx("f0d088"))
    d.ellipse([cx - 15, 39, cx + 15, 79], fill=hx("4a3a3e"))
    vgrad(img, (cx - 12, 42, cx + 12, 76), hx("6a5a5c"), hx("2a1e22"))
    d.ellipse([cx - 15, 39, cx + 15, 79], outline=hx("7a5a2a"))
    d.line([(cx - 8, 46), (cx - 2, 40)], fill=hx("c8c0c0"))
    d.line([(cx - 9, 50), (cx - 1, 42)], fill=hx("8a8084"))
    d.polygon([(cx - 4, 32), (cx + 4, 32), (cx, 26)], fill=BRASS)
    # the picture light above it: a brass hood on a short arm, throwing a cone down the niche
    d.line([(cx, 18), (cx, 24)], fill=hx("6a4c22"))
    d.rectangle([cx - 3, 16, cx + 3, 19], fill=hx("6a4c22"))
    d.polygon([(cx - 10, 24), (cx + 10, 24), (cx + 8, 29), (cx - 8, 29)], fill=BRASS, outline=hx("3a2a10"))
    d.line([(cx - 9, 25), (cx + 9, 25)], fill=hx("f0d088"))
    d.line([(cx - 8, 29), (cx + 8, 29)], fill=hx("fff0c0"))
    light(img, "polygon", [(cx - 8, 29), (cx + 8, 29), (cx + 48, FLOOR), (cx - 48, FLOOR)], LAMPLIGHT, 0.14, 8)
    light(img, "ellipse", [cx - 30, 24, cx + 30, 90], LAMPLIGHT, 0.12, 10)
    shadow(img, "rect", [x0, spring - 30, x0 + 12, FLOOR], 0.3, 5)


def hall_arch(img):
    """The archway back to the hall, warm light from the corridor beyond."""
    d = ImageDraw.Draw(img)
    x0, x1, y0 = 14, 62, 60
    d.rectangle([x0 - 6, y0 + 10, x1 + 6, FLOOR], fill=WOOD_DEEP)
    d.pieslice([x0 - 6, y0 - 6, x1 + 6, y0 + 30], 180, 360, fill=WOOD_DEEP)
    d.rectangle([x0 - 4, y0 + 10, x1 + 4, FLOOR], fill=hx("4a2a18"))
    d.pieslice([x0 - 4, y0 - 4, x1 + 4, y0 + 28], 180, 360, fill=hx("4a2a18"))
    d.arc([x0 - 4, y0 - 4, x1 + 4, y0 + 28], 180, 360, fill=hx("8a6a34"))
    d.rectangle([x0, y0 + 12, x1, FLOOR], fill=hx("2a1410"))
    d.pieslice([x0, y0, x1, y0 + 24], 180, 360, fill=hx("2a1410"))
    vgrad(img, (x0 + 10, y0 + 14, x1 - 10, FLOOR - 16), hx("5a2a1c"), hx("3a1a12"))
    d.polygon([(x0, FLOOR), (x1, FLOOR), (x1 - 10, FLOOR - 16), (x0 + 10, FLOOR - 16)], fill=hx("4a2a18"))
    d.polygon([(x0 + 18, FLOOR), (x1 - 18, FLOOR), (x1 - 14, FLOOR - 16), (x0 + 14, FLOOR - 16)], fill=hx("6a1a22"))
    d.line([(x0, y0 + 12), (x0 + 10, y0 + 14)], fill=hx("1a0a08"))
    d.line([(x1, y0 + 12), (x1 - 10, y0 + 14)], fill=hx("1a0a08"))
    d.line([(x0 + 10, y0 + 14), (x0 + 10, FLOOR - 16)], fill=hx("1a0a08"))
    d.line([(x1 - 10, y0 + 14), (x1 - 10, FLOOR - 16)], fill=hx("1a0a08"))
    for sx in (x0 + 12, x1 - 12):
        d.line([(sx, y0 + 34), (sx, y0 + 38)], fill=BRASS)
        d.point((sx, y0 + 33), fill=hx("fff0c0"))
    light(img, "polygon", [(x0, y0 + 10), (x1, y0 + 10), (x1 + 20, FLOOR + 30), (x0 - 10, FLOOR + 30)], LAMPLIGHT, 0.12, 8)
    d.rectangle([x0 + 20, y0 - 9, x1 - 20, y0 - 4], fill=hx("7a5a2a"), outline=WOOD_DEEP)


def stage_curtain(img):
    """The curtained way through to the stage: a fringed pelmet, two velvet panels, one caught back on a cord."""
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = 414, 468, 52, FLOOR
    d.rectangle([x0 - 6, y0 - 8, x1 + 6, y1], fill=WOOD_DEEP)
    d.rectangle([x0 - 4, y0 - 6, x1 + 4, y1], fill=hx("4a2a18"))
    d.rectangle([x0, y0, x1, y1], fill=hx("0a0306"))
    light(img, "rect", [x0 + 26, y0 + 30, x1 - 4, y1], hx("8a2028"), 0.15, 6)
    px = img.load()
    tie = 106

    def left_panel(y):
        if y < tie:
            t = (y - y0) / (tie - y0)
            return x0, x0 + 26 - 12 * t ** 1.4
        t = (y - tie) / (y1 - tie)
        return x0, x0 + 14 + 10 * t ** 0.8

    curtain_panel(px, y0, y1, left_panel, 3, 0.4, 2111)
    curtain_panel(px, y0, y1, lambda y: (x1 - 16 - (y - y0) * 0.02, x1), 3, 1.7, 2112)
    # the tie-back cord and its tassel
    d.line([(x0, tie - 1), (x0 + 14, tie + 1)], fill=hx("c8a050"))
    d.line([(x0, tie), (x0 + 14, tie + 2)], fill=hx("7a5a24"))
    d.ellipse([x0 + 12, tie, x0 + 16, tie + 4], fill=BRASS, outline=hx("4a3412"))
    d.line([(x0 + 14, tie + 4), (x0 + 14, tie + 8)], fill=hx("c8a050"))
    d.polygon([(x0 + 12, tie + 8), (x0 + 16, tie + 8), (x0 + 17, tie + 16), (x0 + 11, tie + 16)], fill=BRASS)
    for tx in range(x0 + 12, x0 + 17, 2):
        d.line([(tx, tie + 10), (tx, tie + 16)], fill=hx("7a5a24"))
    # hem shadow on the floor and the pelmet with its swags and bullion fringe
    for x in range(x0, x1 + 1, 2):
        d.point((x, y1 - 1), fill=hx("2a060c"))
    d.rectangle([x0 - 4, y0 - 6, x1 + 4, y0 + 2], fill=hx("5a1018"))
    d.line([(x0 - 4, y0 - 6), (x1 + 4, y0 - 6)], fill=BRASS)
    d.line([(x0 - 4, y0 - 5), (x1 + 4, y0 - 5)], fill=hx("f0d088"))
    for sx in range(x0 - 4, x1 + 4, 14):
        d.chord([sx, y0 - 4, sx + 14, y0 + 10], 0, 180, fill=hx("7a1a26"))
        d.arc([sx, y0 - 4, sx + 14, y0 + 10], 0, 180, fill=hx("2a060c"))
        d.arc([sx + 2, y0 - 4, sx + 12, y0 + 6], 20, 160, fill=hx("a03040"))
        for fx in range(sx + 1, sx + 14, 2):
            fy = y0 + 3 + round(6 * math.sin(math.pi * (fx - sx) / 14))
            d.line([(fx, fy), (fx, fy + 2)], fill=BRASS)
        d.polygon([(sx - 1, y0 + 2), (sx + 1, y0 + 2), (sx + 2, y0 + 9), (sx - 2, y0 + 9)], fill=BRASS)
    light(img, "rect", [x0, y0, x0 + 8, y1], hx("ff9070"), 0.12, 3)
    shadow(img, "rect", [x0, y0 + 2, x1, y0 + 14], 0.35, 4)


def _rug_pt(quad, u, v):
    (ax, ay), (bx, by), (cx, cy), (dx, dy) = quad
    tx0, ty0 = ax + (bx - ax) * u, ay + (by - ay) * u
    tx1, ty1 = dx + (cx - dx) * u, dy + (cy - dy) * u
    return (tx0 + (tx1 - tx0) * v, ty0 + (ty1 - ty0) * v)


def lounge_rug(img):
    """A Persian rug in perspective: navy border with a running motif, a red field, a gold medallion, fringed ends."""
    d = ImageDraw.Draw(img)
    quad = [(146, 150), (334, 150), (368, 214), (112, 214)]

    def sub(u0, v0, u1, v1):
        return [_rug_pt(quad, u0, v0), _rug_pt(quad, u1, v0), _rug_pt(quad, u1, v1), _rug_pt(quad, u0, v1)]

    shadow(img, "polygon", [(q[0], q[1] + 2) for q in quad], 0.4, 3)
    d.polygon(quad, fill=hx("1e1a3a"))
    d.polygon(sub(0.015, 0.03, 0.985, 0.97), outline=hx("b08a40"))
    d.polygon(sub(0.07, 0.15, 0.93, 0.85), fill=hx("6a1620"))
    d.polygon(sub(0.07, 0.15, 0.93, 0.85), outline=hx("c8a050"))
    d.polygon(sub(0.09, 0.2, 0.91, 0.8), outline=hx("2a0a10"))
    # running motif in the border
    for i in range(24):
        u = 0.035 + i * 0.04
        for v in (0.09, 0.91):
            pt = _rug_pt(quad, u, v)
            d.point((round(pt[0]), round(pt[1])), fill=hx("c8a050") if i % 2 else hx("8a2a30"))
    for i in range(7):
        v = 0.15 + i * 0.12
        for u in (0.04, 0.96):
            pt = _rug_pt(quad, u, v)
            d.point((round(pt[0]), round(pt[1])), fill=hx("c8a050"))
    # the field: a lattice of small guls and a central medallion
    for i in range(1, 8):
        for j in range(1, 4):
            if 3 <= i <= 5 and j == 2:
                continue
            pt = _rug_pt(quad, 0.07 + i * 0.86 / 8, 0.15 + j * 0.7 / 4)
            x, y = round(pt[0]), round(pt[1])
            d.polygon([(x - 3, y), (x, y - 1), (x + 3, y), (x, y + 1)], fill=hx("8a2a2a"))
            d.point((x, y), fill=hx("d8b060"))
    d.polygon([_rug_pt(quad, 0.5, 0.28), _rug_pt(quad, 0.68, 0.5), _rug_pt(quad, 0.5, 0.72),
               _rug_pt(quad, 0.32, 0.5)], fill=hx("1e1a3a"), outline=hx("c8a050"))
    d.polygon([_rug_pt(quad, 0.5, 0.36), _rug_pt(quad, 0.6, 0.5), _rug_pt(quad, 0.5, 0.64),
               _rug_pt(quad, 0.4, 0.5)], fill=hx("a08a40"))
    d.polygon([_rug_pt(quad, 0.5, 0.42), _rug_pt(quad, 0.54, 0.5), _rug_pt(quad, 0.5, 0.58),
               _rug_pt(quad, 0.46, 0.5)], fill=hx("6a1620"))
    for u, v in ((0.18, 0.24), (0.82, 0.24), (0.18, 0.76), (0.82, 0.76)):
        pt = _rug_pt(quad, u, v)
        d.ellipse([pt[0] - 4, pt[1] - 1.5, pt[0] + 4, pt[1] + 1.5], fill=hx("1e1a3a"), outline=hx("a08a40"))
    # fringe along the near and far ends
    for i in range(60):
        u = i / 59
        a = _rug_pt(quad, u, 1.0)
        d.line([(a[0], a[1] + 1), (a[0] + 0.3, a[1] + 3)], fill=hx("d8ccb0") if i % 2 else hx("a89c80"))
        b = _rug_pt(quad, u, 0.0)
        d.point((round(b[0]), round(b[1]) - 1), fill=hx("a89c80"))
    noise(img, (112, 148, 368, 218), 3, 241)


def chesterfield(img, box, seed, cushions=2, pillow=None, tone=1.0):
    """A buttoned velvet Chesterfield: tufted back, scrolled arms with pleated fronts, nailheads, cushions, bun feet."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    VEL, VDK = mul(VELVET, tone), mul(VELVET_DARK, tone)
    v_hi, v_lo = mul(VEL, 1.3), mul(VEL, 0.7)
    shadow(img, "ellipse", [x0 - 4, y1 - 2, x1 + 4, y1 + 9], 0.5, 4)
    # back, deep-buttoned in a diamond grid
    d.rounded_rectangle([x0 + 3, y0 - 17, x1 - 3, y0 + 8], 7, fill=VEL, outline=VDK)
    d.line([(x0 + 7, y0 - 16), (x1 - 7, y0 - 16)], fill=v_hi)
    d.line([(x0 + 6, y0 - 15), (x1 - 6, y0 - 15)], fill=mul(VEL, 1.15))
    rows = (y0 - 11, y0 - 5, y0 + 1)
    buttons = []
    for r, by in enumerate(rows):
        for bx in range(x0 + 12 + (r % 2) * 6, x1 - 10, 12):
            buttons.append((bx, by))
    for bx, by in buttons:
        for ox, oy in ((6, 6), (-6, 6)):
            if (bx + ox, by + oy) in buttons:
                d.line([(bx, by), (bx + ox, by + oy)], fill=v_lo)
                d.line([(bx + 1, by), (bx + ox + 1, by + oy)], fill=mul(VEL, 1.12))
    for bx, by in buttons:
        d.point((bx, by), fill=VDK)
        d.point((bx - 1, by - 1), fill=v_hi)
    # seat base and front rail with a row of brass nailheads
    d.rounded_rectangle([x0 + 2, y0 + 6, x1 - 2, y1 - 2], 4, fill=VDK, outline=WOOD_DEEP)
    d.rectangle([x0 + 6, y1 - 6, x1 - 6, y1 - 2], fill=mul(VEL, 0.55))
    for nx in range(x0 + 8, x1 - 6, 3):
        d.point((nx, y1 - 5), fill=BRASS)
    # seat cushions with piped edges
    inner0, inner1 = x0 + 11, x1 - 11
    cw = (inner1 - inner0) / cushions
    for i in range(cushions):
        a, b = round(inner0 + i * cw), round(inner0 + (i + 1) * cw) - 1
        d.rounded_rectangle([a, y0 + 5, b, y0 + 14], 3, fill=mul(VEL, 0.92), outline=VDK)
        d.line([(a + 2, y0 + 6), (b - 2, y0 + 6)], fill=v_hi)
        d.line([(a + 2, y0 + 13), (b - 2, y0 + 13)], fill=mul(VEL, 0.6))
        d.point(((a + b) // 2, y0 + 9), fill=mul(VEL, 0.75))
    # rolled arms: a scroll on the front face, pleats radiating from its centre, nailheads down the edge
    for ax, flip in ((x0 - 4, 1), (x1 - 10, -1)):
        d.rounded_rectangle([ax, y0 - 10, ax + 14, y1], 6, fill=VEL, outline=VDK)
        d.line([(ax + 3, y0 - 9), (ax + 11, y0 - 9)], fill=v_hi)
        sx, sy = ax + 7, y0 - 4
        d.ellipse([sx - 6, sy - 5, sx + 6, sy + 5], fill=mul(VEL, 1.08), outline=VDK)
        for a in range(0, 360, 45):
            v = (math.cos(math.radians(a)), math.sin(math.radians(a)))
            d.line([(sx, sy), (sx + round(v[0] * 5), sy + round(v[1] * 4))], fill=v_lo)
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=VDK)
        d.point((sx - 3, sy - 3), fill=v_hi)
        for ny in range(sy + 7, y1 - 2, 3):
            d.point((ax + 2, ny), fill=BRASS)
            d.point((ax + 12, ny), fill=mul(BRASS, 0.7))
        d.line([(ax + (1 if flip > 0 else 13), y0 - 6), (ax + (1 if flip > 0 else 13), y1 - 2)],
               fill=v_hi if flip > 0 else v_lo)
    # turned bun feet
    for fx in (x0 + 1, x1 - 5):
        d.ellipse([fx - 1, y1 - 1, fx + 4, y1 + 4], fill=hx("3a2014"), outline=WOOD_DEEP)
        d.point((fx + 1, y1), fill=hx("7a4a2a"))
    if pillow:
        px0 = x0 + 12 if pillow == "left" else x1 - 30
        d.polygon([(px0, y0 + 4), (px0 + 2, y0 - 10), (px0 + 16, y0 - 12), (px0 + 18, y0 + 3)], fill=hx("1e3426"),
                  outline=hx("8a6a34"))
        d.line([(px0 + 3, y0 - 9), (px0 + 15, y0 - 11)], fill=hx("3a5a40"))
        d.polygon([(px0 + 9, y0 - 8), (px0 + 13, y0 - 4), (px0 + 9, y0), (px0 + 5, y0 - 4)], outline=hx("6a5a2a"))
        d.point((px0 + 9, y0 - 4), fill=hx("c8a050"))
        for tx, ty in ((px0, y0 + 4), (px0 + 18, y0 + 3), (px0 + 2, y0 - 10), (px0 + 16, y0 - 12)):
            d.point((tx, ty), fill=hx("e0c070"))
    noise(img, (x0 - 4, y0 - 17, x1 + 4, y1), 3, seed)


def lounge_table(img, box):
    """A low mahogany table: a gilt-rimmed oval top, cabriole legs, a decanter, tumblers, an ashtray, a hand of cards."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    cx = (x0 + x1) // 2
    shadow(img, "ellipse", [x0 + 4, y1 - 2, x1 - 4, y1 + 6], 0.5, 3)
    # cabriole legs: knees out, ankles in, pad feet
    for lx, s in ((x0 + 8, -1), (x1 - 8, 1), (cx - 14, -1), (cx + 14, 1)):
        d.line([(lx, y0 + 6), (lx + s * 2, y0 + 9), (lx + s, y1 - 2), (lx + s * 2, y1)], fill=WOOD_DEEP, width=2)
        d.point((lx + s * 2, y0 + 9), fill=mul(WOOD, 1.3))
        d.ellipse([lx + s * 2 - 1, y1 - 1, lx + s * 2 + 2, y1 + 1], fill=WOOD_DEEP)
    # the apron with a carved shell in the middle
    d.rectangle([x0 + 6, y0 + 5, x1 - 6, y0 + 8], fill=hx("3a1e10"), outline=WOOD_DEEP)
    d.chord([cx - 4, y0 + 5, cx + 4, y0 + 12], 0, 180, fill=hx("5a3420"), outline=WOOD_DEEP)
    # the top: a gilt rim, mahogany with a polished reflection of the picture light
    d.ellipse([x0, y0 - 1, x1, y0 + 7], fill=BRASS)
    d.ellipse([x0 + 1, y0, x1 - 1, y0 + 6], fill=hx("4a2414"))
    d.ellipse([x0 + 3, y0, x1 - 3, y0 + 5], fill=hx("5e3020"))
    d.line([(cx - 20, y0 + 2), (cx + 6, y0 + 2)], fill=hx("8a5a3a"))
    d.arc([x0, y0 - 1, x1, y0 + 7], 0, 180, fill=hx("6a4c22"))
    # decanter: a cut-glass body half full of whisky, a ball stopper
    dx = cx - 4
    d.polygon([(dx - 4, y0 + 2), (dx + 4, y0 + 2), (dx + 5, y0 - 5), (dx + 2, y0 - 9), (dx - 2, y0 - 9),
               (dx - 5, y0 - 5)], fill=hx("8a9098"), outline=hx("3a3a44"))
    d.polygon([(dx - 4, y0 + 1), (dx + 4, y0 + 1), (dx + 5, y0 - 4), (dx - 5, y0 - 4)], fill=hx("b06a22"))
    d.line([(dx - 3, y0 - 3), (dx - 3, y0)], fill=hx("e8a858"))
    d.rectangle([dx - 1, y0 - 13, dx + 1, y0 - 9], fill=hx("a0a6ad"))
    d.ellipse([dx - 2, y0 - 16, dx + 2, y0 - 12], fill=hx("c8ccd4"), outline=hx("4a4a54"))
    d.point((dx - 1, y0 - 15), fill=hx("ffffff"))
    # tumblers
    for gx in (x0 + 10, cx + 10, x1 - 16):
        d.rectangle([gx, y0 - 4, gx + 4, y0 + 1], fill=hx("a0a6ad"), outline=hx("4a4a54"))
        d.rectangle([gx + 1, y0 - 2, gx + 3, y0], fill=hx("b47028"))
        d.point((gx + 1, y0 - 3), fill=hx("ffffff"))
    # ashtray with a cigar and a thread of smoke; cards fanned beside it
    ax = x1 - 30
    d.ellipse([ax - 4, y0 + 1, ax + 4, y0 + 4], fill=hx("6a6a70"), outline=hx("2a2a30"))
    d.line([(ax, y0 + 1), (ax + 6, y0)], fill=hx("6a3a1e"))
    d.point((ax + 6, y0), fill=hx("ff8040"))
    for i, (sx, sy) in enumerate(((ax + 6, y0 - 2), (ax + 5, y0 - 5), (ax + 7, y0 - 8), (ax + 6, y0 - 11))):
        d.point((sx, sy), fill=mix(hx("8a7a80"), hx("4a3038"), i / 4))
    for i in range(4):
        kx = x0 + 18 + i * 3
        d.polygon([(kx, y0 + 4), (kx + 4, y0 + 3), (kx + 5, y0 + 5), (kx + 1, y0 + 6)], fill=hx("e8e0d0"),
                  outline=hx("6a6050"))
        d.point((kx + 2, y0 + 4), fill=hx("a01818") if i % 2 else hx("1a1a1a"))


def standard_lamp(img, x, top):
    """A standard lamp: a fringed, pleated silk shade lit from inside, a turned brass column with knops."""
    d = ImageDraw.Draw(img)
    light(img, "ellipse", [x - 30, top - 20, x + 30, top + 40], LAMPLIGHT, 0.16, 12)
    d.line([(x, top + 14), (x, 140)], fill=hx("8a6a30"), width=2)
    d.line([(x - 1, top + 14), (x - 1, 140)], fill=hx("e0c070"))
    for ky in (top + 30, top + 52, top + 66):
        d.ellipse([x - 3, ky - 2, x + 3, ky + 2], fill=BRASS, outline=hx("4a3412"))
        d.point((x - 1, ky - 1), fill=hx("fff0c0"))
    # the shade: pleats, gold braid top and bottom, a beaded fringe
    shade = [(x - 7, top), (x + 7, top), (x + 13, top + 14), (x - 13, top + 14)]
    d.polygon(shade, fill=hx("d89a50"), outline=hx("5a3412"))
    for i in range(-5, 6, 2):
        d.line([(x + i, top + 1), (x + round(i * 1.8), top + 13)], fill=hx("b87a38"))
    d.line([(x - 5, top + 1), (x - 10, top + 13)], fill=hx("ffe0a0"))
    d.line([(x - 7, top), (x + 7, top)], fill=BRASS)
    d.line([(x - 13, top + 14), (x + 13, top + 14)], fill=BRASS)
    for fx in range(x - 13, x + 14, 2):
        d.line([(fx, top + 15), (fx, top + 17)], fill=hx("a07a32"))
        d.point((fx, top + 18), fill=hx("e0c070"))
    d.ellipse([x - 11, top + 12, x + 11, top + 16], fill=hx("fff0c0"))
    d.point((x, top - 2), fill=BRASS)
    d.line([(x, top - 1), (x, top)], fill=hx("8a6a30"))
    light(img, "polygon", [(x - 12, top + 15), (x + 12, top + 15), (x + 28, top + 60), (x - 28, top + 60)], LAMPLIGHT,
          0.08, 8)


def pendant(full, x, y, pool):
    """A hanging lamp: ceiling rose, chain, brass gallery, a red silk shade with a gold fringe glowing underneath."""
    d = ImageDraw.Draw(full)
    d.ellipse([x - 5, 6, x + 5, 10], fill=BRASS, outline=WOOD_DEEP)
    for cy in range(11, y - 10):
        d.point((x, cy), fill=BRASS if cy % 3 else hx("4a3412"))
        if cy % 3 == 0:
            d.point((x + 1, cy), fill=hx("6a4c22"))
    d.rectangle([x - 2, y - 11, x + 2, y - 8], fill=BRASS, outline=hx("4a3412"))
    shade = [(x - 6, y - 8), (x + 6, y - 8), (x + 12, y + 2), (x - 12, y + 2)]
    d.polygon(shade, fill=hx("8a2a22"), outline=hx("3a0a0a"))
    for i in (-8, -3, 3, 8):
        d.line([(x + i // 2, y - 7), (x + i, y + 1)], fill=hx("6a1a18"))
    d.line([(x - 5, y - 7), (x - 10, y + 1)], fill=hx("c85a40"))
    d.line([(x - 6, y - 8), (x + 6, y - 8)], fill=BRASS)
    d.line([(x - 12, y + 2), (x + 12, y + 2)], fill=BRASS)
    for fx in range(x - 12, x + 13, 2):
        d.line([(fx, y + 3), (fx, y + 5)], fill=hx("c8a050"))
    d.ellipse([x - 10, y + 1, x + 10, y + 4], fill=hx("ffe8b0"))
    d.ellipse([x - 3, y, x + 3, y + 5], fill=hx("fffaf0"))
    light(full, "polygon", [(x - 10, y + 3), (x + 10, y + 3), (x + 34, y + 110), (x - 34, y + 110)], LAMPLIGHT,
          0.07, 12)
    light(full, "ellipse", [x - 22, y - 14, x + 22, y + 14], hx("e08060"), 0.18, 6)
    light(full, "ellipse", pool, LAMPLIGHT, 0.06, 12)


STAGE_X0, STAGE_X1 = 100, 380  # the proscenium, widened now the stalls are gone


def proscenium(img):
    """The gilt proscenium arch framing the stage, its wall darker than the house."""
    d = ImageDraw.Draw(img)
    x0, x1, y0 = STAGE_X0, STAGE_X1, 10
    d.polygon([(x0 - 28, 0), (x1 + 28, 0), (x1 - 8, 136), (x0 + 8, 136)], fill=hx("1c0a0e"))
    d.rectangle([x0, y0, x1, 136], fill=hx("2a1014"))
    for x in range(x0 + 4, x1 - 2, 8):
        for y in range(y0 + 4 + (x // 8) % 2 * 4, 40, 8):
            d.point((x, y), fill=hx("3a161c"))
    # pilasters either side, fluted, with gilt capitals and bases
    for a in (x0, x1 - 16):
        d.rectangle([a, y0 + 18, a + 16, 136], fill=hx("3a1c16"), outline=WOOD_DEEP)
        for fx in range(a + 3, a + 15, 3):
            d.line([(fx, y0 + 30), (fx, 126)], fill=hx("2a120e"))
            d.line([(fx + 1, y0 + 30), (fx + 1, 126)], fill=hx("4e2a1a"))
        d.rectangle([a - 2, y0 + 18, a + 18, y0 + 26], fill=hx("8a6a34"), outline=WOOD_DEEP)
        d.line([(a - 1, y0 + 19), (a + 17, y0 + 19)], fill=hx("e0c070"))
        for vx in (a + 1, a + 15):
            d.arc([vx - 3, y0 + 21, vx + 3, y0 + 27], 0, 360, fill=hx("5a4018"))
        d.rectangle([a - 2, 128, a + 18, 136], fill=hx("2e1a10"), outline=WOOD_DEEP)
        d.line([(a - 1, 129), (a + 17, 129)], fill=hx("4a3018"))
    # the gilt arch itself with a cartouche at its crown
    d.rectangle([x0 + 16, y0 + 18, x1 - 16, 34], fill=hx("6a4a24"))
    d.chord([x0 + 16, y0 + 4, x1 - 16, 64], 180, 360, fill=hx("6a4a24"))
    d.arc([x0 + 16, y0 + 4, x1 - 16, 64], 180, 360, fill=BRASS)
    d.arc([x0 + 20, y0 + 8, x1 - 20, 60], 180, 360, fill=hx("e0c070"))
    for k in range(10):
        a = math.pi * (k + 0.5) / 10
        px_, py_ = 240 - math.cos(a) * ((x1 - x0) / 2 - 8), 37 - math.sin(a) * 22
        d.ellipse([px_ - 1, py_ - 1, px_ + 1, py_ + 1], fill=hx("f0d088"))
    d.ellipse([228, y0, 252, y0 + 16], fill=BRASS, outline=WOOD_DEEP)
    d.ellipse([232, y0 + 3, 248, y0 + 13], fill=hx("5a1018"), outline=hx("e0c070"))
    d.text((237, y0 + 3), "R", fill=hx("e0c070"))
    for s in (-1, 1):
        d.arc([240 + s * 18 - 8, y0 + 2, 240 + s * 18 + 8, y0 + 14], 0, 360, fill=hx("8a6a34"))
        d.line([(240 + s * 12, y0 + 14), (240 + s * 30, y0 + 16)], fill=BRASS)
    shadow(img, "rect", [x0 + 16, 40, x1 - 16, 46], 0.4, 3)


def stage_backdrop(img):
    """The house curtain: a fringed valance, two velvet panels meeting at a seam, tied-back legs either side."""
    d = ImageDraw.Draw(img)
    d.rectangle([STAGE_X0 + 12, 40, STAGE_X1 - 12, 110], fill=hx("0a0406"))
    px = img.load()
    x0, x1, y0, y1 = STAGE_X0 + 32, STAGE_X1 - 32, 46, 110
    curtain_panel(px, y0, y1, lambda y: (x0, 239 - max(0, (y - 100)) * 0.3), 8, 0.3, 3011)
    curtain_panel(px, y0, y1, lambda y: (241 + max(0, (y - 100)) * 0.3, x1), 8, 2.1, 3012)
    d.line([(240, y0), (240, y1)], fill=hx("16030a"))
    for x in range(x0, x1 + 1):
        if (x // 2) % 2:
            d.point((x, y1 - 1), fill=hx("c8a050"))
        d.point((x, y1 - 2), fill=hx("7a5a24"))
    # side legs caught back with gilt cords
    for a, b, tie, s in ((x0 - 18, x0 + 2, 86, 1), (x1 - 2, x1 + 18, 86, -1)):
        def leg(y, a=a, b=b, tie=tie, s=s):
            if y < tie:
                t = max(0, (y - y0) / (tie - y0))
                w = 20 - 10 * t ** 1.3
            else:
                w = 10 + 10 * ((y - tie) / (y1 - tie)) ** 0.8
            return (a, a + w) if s > 0 else (b - w, b)
        curtain_panel(px, y0 - 4, y1, leg, 2, 1.0 if s > 0 else 2.4, 3020 + s)
        cx = a + 10 if s > 0 else b - 10
        d.line([(a if s > 0 else b, tie), (cx, tie + 1)], fill=hx("c8a050"))
        d.ellipse([cx - 2, tie - 1, cx + 2, tie + 3], fill=BRASS, outline=hx("4a3412"))
        d.polygon([(cx - 2, tie + 4), (cx + 2, tie + 4), (cx + 3, tie + 12), (cx - 3, tie + 12)], fill=BRASS)
        for tx in range(cx - 2, cx + 3, 2):
            d.line([(tx, tie + 6), (tx, tie + 12)], fill=hx("7a5a24"))
    # the valance: swags, bullion fringe, tassels between
    vl, vr, sw = STAGE_X0 + 10, STAGE_X1 - 10, 26
    d.rectangle([vl, 36, vr, 46], fill=hx("5a1018"))
    d.line([(vl, 36), (vr, 36)], fill=hx("f0d088"))
    d.line([(vl, 37), (vr, 37)], fill=BRASS)
    for sx in range(vl, vr, sw):
        d.chord([sx, 34, sx + sw, 56], 0, 180, fill=hx("7a1a26"))
        d.arc([sx, 34, sx + sw, 56], 0, 180, fill=hx("2a060c"))
        d.arc([sx + 3, 34, sx + sw - 3, 50], 15, 165, fill=hx("a03040"))
        d.arc([sx + 7, 36, sx + sw - 7, 46], 20, 160, fill=hx("8a2232"))
        for fx in range(sx + 1, sx + sw, 2):
            fy = 45 + round(10 * math.sin(math.pi * (fx - sx) / sw))
            d.line([(fx, fy), (fx, fy + 2)], fill=BRASS if fx % 4 else hx("e0c070"))
        d.ellipse([sx - 2, 42, sx + 2, 46], fill=hx("e0c070"))
        d.polygon([(sx - 1, 46), (sx + 1, 46), (sx + 3, 56), (sx - 3, 56)], fill=BRASS)
        d.line([(sx, 48), (sx, 56)], fill=hx("7a5a24"))
    shadow(img, "rect", [x0, 46, x1, 60], 0.3, 4)
    # the stage boards, an apron with footlights
    bl, br, al, ar = x0 + 18, x1 - 18, x0 - 6, x1 + 6
    d.polygon([(bl, 110), (br, 110), (ar, 146), (al, 146)], fill=WOOD_DARK)
    d.line([(bl, 110), (br, 110)], fill=mul(WOOD, 1.1))
    for x in range(bl + 4, br, 12):
        d.line([(x, 111), (240 + (x - 240) * (ar - 240) / (br - 240), 146)], fill=hx("3a2216"))
    for y in (118, 129, 140):
        k = (y - 110) / 36
        d.line([(bl - 24 * k + 2, y), (br + 24 * k - 2, y)], fill=hx("2e1a10"))
    for x, y in ((174, 124), (214, 124), (262, 120), (230, 136), (282, 132), (318, 126)):
        d.point((x, y), fill=hx("5a3a24"))
    d.polygon([(al, 146), (ar, 146), (ar, 152), (al, 152)], fill=WOOD_DEEP)
    d.line([(al, 146), (ar, 146)], fill=mul(WOOD, 1.15))
    d.line([(al, 152), (ar, 152)], fill=hx("6a4a24"))
    for x in range(al + 6, ar - 2, 6):
        d.line([(x, 148), (x, 151)], fill=hx("2a160c"))
    for x in range(al + 12, ar - 6, 16):
        d.chord([x - 5, 142, x + 5, 150], 180, 360, fill=hx("6a4a24"), outline=hx("2a1a0a"))
        d.point((x, 144), fill=hx("fff0c0"))
        light(img, "ellipse", [x - 7, 132, x + 7, 148], hx("f8d28a"), 0.18, 4)
    light(img, "rect", [al + 10, 96, ar - 10, 146], hx("f8d28a"), 0.06, 10)


def theatre_seat(d, x, y, shade):
    """A tip-up stall seen from behind: velvet top roll, a walnut shell, brass number plate, armrests."""
    vel = mix(hx("8a2030"), hx("2a0a10"), shade)
    wood = mix(hx("6a4030"), hx("241410"), shade)
    d.rounded_rectangle([x - 10, y - 9, x + 10, y - 2], 3, fill=vel, outline=mul(vel, 0.5))
    d.line([(x - 8, y - 8), (x + 8, y - 8)], fill=mul(vel, 1.45))
    for tx in (x - 5, x, x + 5):
        d.point((tx, y - 5), fill=mul(vel, 0.6))
    d.rectangle([x - 10, y - 2, x + 10, y + 11], fill=wood, outline=mul(wood, 0.5))
    d.line([(x - 9, y - 1), (x + 9, y - 1)], fill=mul(wood, 1.4))
    d.rectangle([x - 7, y + 1, x + 7, y + 9], outline=mul(wood, 0.7))
    d.rectangle([x - 3, y + 3, x + 3, y + 6], fill=mix(BRASS, hx("2a1a0a"), shade * 0.8))
    d.point((x, y + 4), fill=mul(wood, 0.6))
    for ax in (x - 12, x + 12):
        d.rectangle([ax - 1, y + 1, ax + 1, y + 13], fill=mul(wood, 0.6))
        d.rounded_rectangle([ax - 2, y, ax + 2, y + 3], 1, fill=mul(wood, 1.25))
        d.point((ax, y), fill=mix(BRASS, wood, shade))
    d.line([(x - 9, y + 12), (x + 9, y + 12)], fill=mul(wood, 0.45))


def seating(img):
    """A single front row of stalls along the right wall, on a low riser with brass-capped aisle ends."""
    d = ImageDraw.Draw(img)
    y, shade = 120, 0.3
    xs = [404 + j * 26 for j in range(3)]
    lo, hi = min(xs) - 14, max(xs) + 14
    shadow(img, "rect", [lo - 2, y + 14, hi + 2, y + 22], 0.5, 4)
    d.rectangle([lo, y + 12, hi, y + 18], fill=mix(hx("2a1014"), hx("140608"), shade))
    d.line([(lo, y + 12), (hi, y + 12)], fill=mix(BRASS, hx("1a0a08"), 0.4 + shade * 0.4))
    d.line([(lo, y + 18), (hi, y + 18)], fill=hx("0e0406"))
    for x in xs:
        theatre_seat(d, x, y, shade)
    for end in (lo + 1, hi - 1):
        d.rectangle([end - 2, y - 4, end + 2, y + 14], fill=mix(hx("5a3424"), hx("1a0c08"), shade))
        d.ellipse([end - 2, y - 6, end + 2, y - 2], fill=mix(BRASS, hx("2a1a0a"), shade))
        d.point((end, y + 4), fill=hx("e0c070"))


def side_walls(img):
    """Dado panelling and sconces on the house walls either side of the proscenium."""
    d = ImageDraw.Draw(img)
    for a, b in ((0, STAGE_X0 - 24), (STAGE_X1 + 24, W - 1)):
        d.rectangle([a, 92, b, 136], fill=hx("1e0c0e"))
        d.line([(a, 91), (b, 91)], fill=mul(WOOD, 0.8))
        d.line([(a, 92), (b, 92)], fill=WOOD_DEEP)
        for x in range(a + 4, b - 12, 22):
            d.rectangle([x, 98, x + 16, 130], outline=hx("2e1812"))
            d.line([(x + 1, 99), (x + 15, 99)], fill=hx("3a2016"))
    sconce(img, 82, 70)
    sconce(img, 432, 70)


def aisle_rug(img):
    """The aisle runner: border, a lozenge repeat, brass stair rods, a fringe where it meets the stage."""
    d = ImageDraw.Draw(img)
    quad = ((214, 152), (266, 152), (290, H - 1), (190, H - 1))
    P = lambda u, v: _rug_pt(quad, u, v)
    d.polygon([P(0, 0), P(1, 0), P(1, 1), P(0, 1)], fill=hx("2a0a10"))
    d.polygon([P(0.04, 0), P(0.96, 0), P(0.96, 1), P(0.04, 1)], fill=hx("6a1a24"))
    d.polygon([P(0.14, 0), P(0.86, 0), P(0.86, 1), P(0.14, 1)], fill=hx("4a121a"))
    for u in (0.1, 0.9):
        d.line([P(u, 0), P(u, 1)], fill=hx("a0803c"))
    for u in (0.07, 0.93):
        for k in range(0, 40):
            v = (k + 0.5) / 40
            if k % 2:
                d.point(P(u, v), fill=hx("c8a050"))
    n = 7
    for k in range(n):
        v0, v1 = k / n + 0.02, (k + 1) / n - 0.02
        vm = (v0 + v1) / 2
        d.polygon([P(0.5, v0 + 0.01), P(0.78, vm), P(0.5, v1 - 0.01), P(0.22, vm)], fill=hx("1e2a4a"), outline=hx("a0803c"))
        d.polygon([P(0.5, vm - 0.035), P(0.62, vm), P(0.5, vm + 0.035), P(0.38, vm)], fill=hx("8a2030"))
        d.point(P(0.5, vm), fill=hx("e0c070"))
        for u in (0.24, 0.76):
            d.point(P(u, v0 + 0.01), fill=hx("c8a050"))
        # brass stair rod across each tread
        a, b = P(-0.02, v1 + 0.02), P(1.02, v1 + 0.02)
        d.line([a, b], fill=hx("6a4a1c"), width=2)
        d.line([(a[0], a[1] - 1), (b[0], b[1] - 1)], fill=hx("e0c070"))
        for e in (a, b):
            d.ellipse([e[0] - 1.5, e[1] - 2, e[0] + 1.5, e[1] + 1], fill=BRASS)
    for k in range(27):
        x, y = P((k + 0.5) / 27, 0)
        d.line([(x, y - 2), (x, y)], fill=hx("c8b080"))
    noise(img, (190, 152, 290, H - 1), 4, 3301)


def spotlight(full):
    """A rigging pipe, a yoke and a can lantern with barn doors, its lens trained on the stage."""
    d = ImageDraw.Draw(full)
    d.rectangle([286, 66, 372, 69], fill=hx("2a2224"))
    d.line([(286, 66), (372, 66)], fill=hx("6a6064"))
    for x in (290, 368):
        d.line([(x, 0), (x, 66)], fill=hx("3a3034"))
        d.line([(x - 2, 64), (x + 2, 64)], fill=hx("6a6064"))
    d.line([(352, 69), (354, 80), (348, 96), (350, 110)], fill=hx("141012"))
    d.line([(326, 69), (326, 74)], fill=hx("6a6064"), width=2)
    d.rectangle([322, 70, 330, 72], fill=hx("4a4044"))
    # the yoke
    d.line([(326, 74), (314, 76), (314, 90)], fill=hx("4a4044"), width=2)
    d.line([(326, 74), (338, 78), (336, 92)], fill=hx("4a4044"), width=2)
    # the can, angled down-left towards the stage
    body = [(318, 76), (338, 84), (330, 102), (310, 94)]
    d.polygon(body, fill=hx("3a3034"), outline=hx("120c0e"))
    for t in (0.3, 0.55, 0.8):
        a = (318 + (338 - 318) * t, 76 + (84 - 76) * t)
        b = (310 + (330 - 310) * t, 94 + (102 - 94) * t)
        d.line([a, b], fill=hx("2a2226"))
    d.line([(319, 77), (337, 84)], fill=hx("7a7074"))
    d.polygon([(333, 79), (340, 76), (343, 82), (337, 85)], fill=hx("4a4044"), outline=hx("120c0e"))
    for vx in (335, 338):
        d.line([(vx, 79), (vx + 1, 83)], fill=hx("1a1214"))
    # lens and barn doors
    d.polygon([(318, 76), (310, 94), (306, 92), (314, 74)], fill=hx("fff0c2"), outline=hx("2a2226"))
    d.line([(316, 78), (310, 90)], fill=hx("ffffff"))
    d.polygon([(314, 74), (306, 68), (304, 70), (312, 77)], fill=hx("2a2226"))
    d.polygon([(306, 92), (298, 96), (300, 98), (309, 95)], fill=hx("2a2226"))
    d.ellipse([320, 86, 324, 90], fill=hx("6a6064"))
    light(full, "polygon", [(312, 76), (306, 94), (200, TOP + 146), (286, TOP + 146)], hx("fff0c2"), 0.12, 6)
    light(full, "ellipse", [302, 68, 324, 100], hx("fff0c2"), 0.3, 4)
    for k, (x, y) in enumerate(((290, 120), (276, 140), (262, 158), (250, 150), (268, 128), (238, 166))):
        full.putpixel((x, y), mix(hx("fff0c2"), full.getpixel((x, y)), 0.45 + 0.1 * (k % 2)))


def exit_drape(img):
    """The curtained way back to the lounge, one velvet panel drawn aside on a brass rod."""
    d = ImageDraw.Draw(img)
    curtain_panel(img.load(), 76, 145, lambda y: (18, 32 + max(0, y - 120) * 0.2), 2, 0.8, 3401)
    d.rectangle([16, 72, 64, 74], fill=BRASS)
    d.line([(16, 72), (64, 72)], fill=hx("f0d088"))
    for x in (16, 64):
        d.ellipse([x - 2, 71, x + 2, 75], fill=hx("e0c070"))
    for x in range(20, 34, 4):
        d.ellipse([x - 1, 72, x + 1, 77], outline=hx("8a6a34"))
    d.line([(18, 112), (33, 113)], fill=hx("c8a050"))
    d.polygon([(32, 113), (34, 113), (35, 121), (31, 121)], fill=BRASS)
    light(img, "rect", [36, 80, 62, 145], hx("5a2a1c"), 0.25, 6)


def stage_scene():
    img = Image.new("RGB", (W, H))
    room_shell(img, 136, (240, -180), 320)
    proscenium(img)
    side_walls(img)
    d = ImageDraw.Draw(img)
    d.polygon([(0, 136), (W - 1, 136), (W - 1, H - 1), (0, H - 1)], fill=hx("12070a"))
    d.polygon([(140, 132), (340, 132), (392, H - 1), (88, H - 1)], fill=hx("1c0b0f"))
    for x in range(92, 392, 12):
        d.line([(x, 160), (x - 12, 230)], fill=hx("18080c"))
    aisle_rug(img)
    stage_backdrop(img)
    d.rounded_rectangle([14, 58, 66, 146], 16, fill=hx("090407"), outline=WOOD)
    exit_drape(img)
    seating(img)
    shadow(img, "rect", [0, 72, W - 1, H - 1], 0.26, 18, hx("22090c"))
    full = tall(img, ceiling_band)
    spotlight(full)
    light(full, "ellipse", [192, TOP + 112, 290, TOP + 148], hx("f8d28a"), 0.20, 7)
    vignette(full, 0.82, tint=(26, 8, 12), blur=58)
    shadow(full, "rect", [0, TOP + 144, W - 1, H + TOP], 0.12, 20, hx("160609"))
    return full

BACKSTAGE_DOOR = (20, 74)  # x span of the stage door, left wall
BACKSTAGE_TABLE = (214, 346)  # x span of the dressing table; the mirror sits above its middle
BACKSTAGE_MIRROR = (236, 324, 34, 108)


def backstage_wall(img):
    """A cramped dressing room: faded striped paper above a scuffed dado, bare boards."""
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("3a1c22"), hx("2a1216"))
    for x in range(0, W, 14):
        d.rectangle([x, 8, x + 5, 98], fill=hx("40222a"))
        d.line([(x + 6, 8), (x + 6, 98)], fill=hx("2c1218"))
    d.rectangle([0, 0, W - 1, 4], fill=WOOD_DEEP)
    d.line([(0, 5), (W - 1, 5)], fill=mul(WOOD, 1.2))
    d.line([(0, 7), (W - 1, 7)], fill=hx("6a4a24"))
    d.rectangle([0, 99, W - 1, FLOOR], fill=hx("2a1810"))
    d.line([(0, 99), (W - 1, 99)], fill=WOOD)
    d.line([(0, 100), (W - 1, 100)], fill=hx("6a4022"))
    for x in range(4, W, 30):
        d.line([(x, 102), (x, FLOOR - 6)], fill=hx("1e100a"))
    d.rectangle([0, FLOOR - 5, W - 1, FLOOR], fill=WOOD_DEEP)
    d.line([(0, FLOOR - 5), (W - 1, FLOOR - 5)], fill=WOOD)
    # damp stains on the paper
    shadow(img, "ellipse", [140, 10, 200, 60], 0.18, 10)
    shadow(img, "ellipse", [356, 50, 420, 96], 0.14, 10)
    floor_boards(img, FLOOR, H - 1, HALL_VP, 18, hx("4a2a1a"), hx("2e180f"), hx("150907"), 3511)
    noise(img, (0, 0, W - 1, H - 1), 5, 3512)


def backstage_door(img, state="shut"):
    """The door back out to the stage: plain panelled, a brass knob. Hinged on the left, it swings out into the
    passage: "ajar" shows the leaf foreshortened with a gap of dim passage at the knob side, "open" the leaf edge-on
    against the hinge jamb and the passage beyond, lit by the stage at its far end."""
    d = ImageDraw.Draw(img)
    x0, x1 = BACKSTAGE_DOOR
    y0 = 30
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, FLOOR], fill=hx("4a2a18"), outline=WOOD_DEEP)
    d.line([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4)], fill=hx("7a5030"))
    if state != "shut":
        # the passage: black boards, a far wall warmed by the stage lights round a corner
        vgrad(img, (x0, y0, x1, FLOOR), hx("140808"), hx("0a0405"))
        light(img, "ellipse", [x0 + 8, y0 + 20, x1 + 10, FLOOR + 10], hx("c87a3a"), 0.32, 10)
        d.polygon([(x0, FLOOR), (x1, FLOOR), (x1 - 8, FLOOR - 22), (x0 + 8, FLOOR - 22)], fill=hx("2a140c"))
        for k in range(1, 4):
            d.line([(x0 + 8 * k // 2, FLOOR - 22 + 6 * k), (x1 - 8 * k // 2, FLOOR - 22 + 6 * k)], fill=hx("1a0a06"))
        d.rectangle([x0, y0, x1, FLOOR], outline=WOOD_DEEP)
        if state == "ajar":
            fx = x1 - 16
            d.polygon([(x0, y0), (fx, y0 + 3), (fx, FLOOR - 3), (x0, FLOOR)], fill=hx("2e170e"), outline=WOOD_DEEP)
            vgrad(img, (x0 + 1, y0 + 3, fx - 1, FLOOR - 3), hx("3e2214"), hx("26130c"))
            for p0, p1 in ((y0 + 10, y0 + 50), (y0 + 60, FLOOR - 12)):
                d.rectangle([x0 + 5, p0, fx - 5, p1], outline=hx("1a0c06"))
                d.line([(x0 + 6, p0 + 1), (fx - 6, p0 + 1)], fill=hx("5a3020"))
            d.line([(fx, y0 + 3), (fx, FLOOR - 3)], fill=hx("6a3a22"))
            d.ellipse([fx - 7, y0 + 55, fx - 4, y0 + 59], fill=BRASS, outline=hx("4a3412"))
            d.point((fx - 6, y0 + 56), fill=hx("fff0c0"))
        else:
            d.polygon([(x0, y0), (x0 + 7, y0 + 5), (x0 + 7, FLOOR - 5), (x0, FLOOR)], fill=hx("26130c"),
                      outline=WOOD_DEEP)
            d.line([(x0 + 7, y0 + 5), (x0 + 7, FLOOR - 5)], fill=hx("6a3a22"))
            d.rectangle([x0 + 3, y0 + 56, x0 + 4, y0 + 59], fill=BRASS)
        light(img, "polygon", [(x0, FLOOR), (x1, FLOOR), (x1 + 18, FLOOR + 18), (x0 - 6, FLOOR + 18)], hx("c87a3a"),
              0.18, 4)
        return
    d.rectangle([x0, y0, x1, FLOOR], fill=hx("3a1e12"), outline=WOOD_DEEP)
    vgrad(img, (x0 + 1, y0 + 1, x1 - 1, FLOOR - 1), hx("4a2818"), hx("2e170e"))
    for p0, p1 in ((y0 + 8, y0 + 50), (y0 + 60, FLOOR - 10)):
        d.rectangle([x0 + 7, p0, x1 - 7, p1], outline=hx("1e0e08"))
        d.line([(x0 + 8, p0 + 1), (x1 - 8, p0 + 1)], fill=hx("6a3a22"))

    d.ellipse([x1 - 10, y0 + 54, x1 - 5, y0 + 59], fill=BRASS, outline=hx("4a3412"))
    d.point((x1 - 9, y0 + 55), fill=hx("fff0c0"))
    # light from the stage leaks under the door
    d.line([(x0 + 1, FLOOR - 1), (x1 - 1, FLOOR - 1)], fill=hx("c88a48"))
    light(img, "polygon", [(x0, FLOOR), (x1, FLOOR), (x1 + 14, FLOOR + 14), (x0 - 4, FLOOR + 14)], LAMPLIGHT, 0.12, 4)


def costume_rail(img):
    """A brass rail on castors hung with the Order's black hooded robes."""
    d = ImageDraw.Draw(img)
    x0, x1, y0 = 96, 184, 56
    shadow(img, "ellipse", [x0 - 6, FLOOR - 2, x1 + 6, FLOOR + 8], 0.45, 4)
    for x in (x0, x1):
        d.line([(x, y0), (x, FLOOR + 2)], fill=hx("8a6a30"), width=2)
        d.line([(x - 6, FLOOR + 2), (x + 6, FLOOR + 2)], fill=hx("4a3412"), width=2)
        for cx in (x - 6, x + 6):
            d.ellipse([cx - 2, FLOOR + 2, cx + 2, FLOOR + 6], fill=hx("1a1010"))
    d.line([(x0, y0), (x1, y0)], fill=BRASS, width=2)
    d.line([(x0, y0 - 1), (x1, y0 - 1)], fill=hx("f0d088"))
    cloth, fold, sheen, edge = hx("1c171c"), hx("0c090c"), hx("3a3240"), hx("050405")
    for i, (cx, ln) in enumerate(((x0 + 6, 78), (x0 + 22, 82), (x0 + 38, 76), (x0 + 54, 80), (x0 + 68, 77))):
        d.arc([cx + 5, y0 - 5, cx + 11, y0 + 1], 180, 360, fill=hx("9a9aa0"))
        hem = y0 + 4 + ln
        # the robe: narrow shoulders flaring to a wide hem, the sleeves hanging at its sides
        d.polygon([(cx + 3, y0 + 5), (cx + 13, y0 + 5), (cx + 18, hem), (cx - 2, hem)], fill=cloth, outline=edge)
        d.polygon([(cx + 1, y0 + 8), (cx + 4, y0 + 7), (cx + 3, y0 + 44), (cx - 1, y0 + 46)], fill=fold, outline=edge)
        d.polygon([(cx + 12, y0 + 7), (cx + 15, y0 + 8), (cx + 17, y0 + 46), (cx + 13, y0 + 44)], fill=fold,
                  outline=edge)
        d.line([(cx + 8, y0 + 18), (cx + 6, hem - 1)], fill=fold)
        d.line([(cx + 11, y0 + 20), (cx + 13, hem - 1)], fill=fold)
        d.line([(cx + 5, y0 + 20), (cx + 2, hem - 2)], fill=sheen)
        d.line([(cx - 1, hem), (cx + 17, hem)], fill=sheen)
        # the hood hangs down the back in a peak over the shoulders, its lining showing in a dark slit
        d.polygon([(cx + 2, y0 + 3), (cx + 14, y0 + 3), (cx + 13, y0 + 15), (cx + 8, y0 + 22), (cx + 3, y0 + 15)],
                  fill=cloth, outline=edge)
        d.polygon([(cx + 6, y0 + 6), (cx + 10, y0 + 6), (cx + 8, y0 + 16)], fill=hx("070507"))
        d.line([(cx + 3, y0 + 4), (cx + 4, y0 + 14)], fill=sheen)
        # a knotted cord belt
        d.line([(cx + 2, y0 + 30), (cx + 15, y0 + 30)], fill=hx("2e262c"))
        d.line([(cx + 7, y0 + 31), (cx + 6, y0 + 42)], fill=hx("2e262c"))
        d.point((cx + 6, y0 + 43), fill=hx("4a404a"))
    noise(img, (x0, y0, x1, FLOOR), 3, 3521)


LIPSTICK_X = 292  # Eleanor's lipstick on the dressing table, left edge
COMPACT_X = 334  # her open compact, centre
# overlay crops of the two things she takes, in scene coordinates; the background is painted without them
BACKSTAGE_LIPSTICK_BOX = (LIPSTICK_X - 2, 114 - 16 + TOP, LIPSTICK_X + 15, 114 + 4 + TOP)
BACKSTAGE_COMPACT_BOX = (COMPACT_X - 9, 114 - 17 + TOP, COMPACT_X + 10, 114 + 5 + TOP)


def dressing_table(img, compact=True, lipstick=True):
    """The dressing table: a mirror ringed by bulbs; the old man's gin, glass and saucer of powder; a hairbrush and
    comb, Eleanor's lipstick, a perfume atomiser and her open compact. The lipstick and compact can be left off,
    for the background she takes them from."""
    d = ImageDraw.Draw(img)
    x0, x1 = BACKSTAGE_TABLE
    mx0, mx1, my0, my1 = BACKSTAGE_MIRROR
    top = 114
    light(img, "ellipse", [mx0 - 50, my0 - 30, mx1 + 50, FLOOR + 30], LAMPLIGHT, 0.2, 18)
    # the mirror: a plain frame, its glass catching the room in a dim smear
    d.rectangle([mx0 - 8, my0 - 8, mx1 + 8, my1 + 4], fill=hx("4a2c18"), outline=WOOD_DEEP)
    d.rectangle([mx0, my0, mx1, my1], fill=hx("4a3a40"))
    vgrad(img, (mx0 + 1, my0 + 1, mx1 - 1, my1 - 1), hx("6a5a60"), hx("2e2228"))
    d.rectangle([mx0, my0, mx1, my1], outline=hx("1a0e0a"))
    d.line([(mx0 + 8, my0 + 18), (mx0 + 26, my0 + 2)], fill=hx("c8c0c4"))
    d.line([(mx0 + 10, my0 + 26), (mx0 + 36, my0 + 2)], fill=hx("8a8088"))
    d.line([(mx1 - 20, my1 - 4), (mx1 - 4, my1 - 20)], fill=hx("7a7078"))
    # the ring of bulbs
    pts = [(x, my0 - 4) for x in range(mx0 - 2, mx1 + 3, 11)] + \
          [(x, my1 + 1) for x in range(mx0 - 2, mx1 + 3, 11)] + \
          [(mx0 - 4, y) for y in range(my0 + 8, my1 - 3, 11)] + [(mx1 + 4, y) for y in range(my0 + 8, my1 - 3, 11)]
    for bx, by in pts:
        light(img, "ellipse", [bx - 6, by - 6, bx + 6, by + 6], hx("fff0c0"), 0.3, 3)
    for i, (bx, by) in enumerate(pts):
        if i == 5:  # one bulb has gone
            d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=hx("5a5048"), outline=hx("2a2018"))
            continue
        d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=hx("fff4d0"), outline=hx("c89a50"))
        d.point((bx - 1, by - 1), fill=hx("ffffff"))
    # the table: a top with a lip, two drawers each side, the kneehole between
    shadow(img, "rect", [x0 + 2, FLOOR - 2, x1 - 2, FLOOR + 6], 0.5, 4)
    d.rectangle([x0, top + 6, x1, FLOOR], fill=hx("3a1e10"), outline=WOOD_DEEP)
    d.rectangle([x0 + 40, top + 14, x1 - 40, FLOOR], fill=hx("140a06"))
    for dx0, dx1 in ((x0 + 4, x0 + 36), (x1 - 36, x1 - 4)):
        for dy in (top + 12, top + 22):
            d.rectangle([dx0, dy, dx1, dy + 8], fill=hx("4a2814"), outline=WOOD_DEEP)
            d.point(((dx0 + dx1) // 2, dy + 4), fill=BRASS)
        d.line([(dx0 + 2, FLOOR - 1), (dx0 + 2, top + 32)], fill=WOOD_DEEP)
    d.rectangle([x0 - 4, top, x1 + 4, top + 6], fill=hx("5a3320"), outline=WOOD_DEEP)
    d.line([(x0 - 3, top + 1), (x1 + 3, top + 1)], fill=hx("8a5a36"))
    light(img, "rect", [mx0 - 10, top, mx1 + 10, top + 5], LAMPLIGHT, 0.25, 3)
    ink = hx("2a1e18")
    # gin: a tall square bottle, half full, a paper label with a red band, a cork stopper
    gx = x0 + 6
    d.rectangle([gx, top - 24, gx + 9, top + 2], fill=hx("5a7276"), outline=hx("2e3a3e"))
    d.rectangle([gx + 1, top - 10, gx + 8, top + 1], fill=hx("9abcb6"))
    d.line([(gx + 1, top - 11), (gx + 8, top - 11)], fill=hx("e8f4f0"))
    d.polygon([(gx + 1, top - 24), (gx + 8, top - 24), (gx + 6, top - 28), (gx + 3, top - 28)], fill=hx("5a7276"),
              outline=hx("2e3a3e"))
    d.rectangle([gx + 3, top - 33, gx + 6, top - 28], fill=hx("6a8286"), outline=hx("2e3a3e"))
    d.rectangle([gx + 3, top - 35, gx + 6, top - 33], fill=hx("a87a4a"), outline=hx("4a3018"))
    d.rectangle([gx + 1, top - 20, gx + 8, top - 12], fill=hx("ece2c4"), outline=hx("6a5a3a"))
    d.line([(gx + 1, top - 18), (gx + 8, top - 18)], fill=hx("a01e1e"))
    d.line([(gx + 3, top - 16), (gx + 6, top - 16)], fill=ink)
    d.line([(gx + 3, top - 14), (gx + 6, top - 14)], fill=hx("8a7a5a"))
    d.line([(gx + 1, top - 23), (gx + 1, top - 21)], fill=hx("ffffff"))
    d.line([(gx + 1, top - 9), (gx + 1, top)], fill=hx("ffffff"))
    # a cut-glass tumbler with a finger of gin: faceted sides, a heavy base
    tx = gx + 12
    d.polygon([(tx, top - 9), (tx + 8, top - 9), (tx + 7, top + 2), (tx + 1, top + 2)], fill=hx("4e6a72"),
              outline=hx("3a4a50"))
    for fx in (tx + 2, tx + 4, tx + 6):
        d.line([(fx, top - 8), (fx, top - 4)], fill=hx("a8c8cc"))
    d.rectangle([tx + 1, top - 3, tx + 6, top - 1], fill=hx("b8d4cc"))
    d.rectangle([tx + 1, top, tx + 7, top + 1], fill=hx("6a8088"))
    d.point((tx + 1, top - 8), fill=hx("ffffff"))
    # the old man's saucer: silver, a line of powder cut on it, a razor blade laid across the rim
    sx = tx + 12
    d.ellipse([sx, top - 1, sx + 14, top + 3], fill=hx("9a9aa4"), outline=hx("44444e"))
    d.ellipse([sx + 2, top, sx + 12, top + 2], fill=hx("c8c8d0"))
    d.line([(sx + 2, top - 1), (sx + 6, top - 1)], fill=hx("f0f0f4"))
    d.line([(sx + 3, top + 1), (sx + 9, top + 1)], fill=hx("fcfaf6"))
    d.point((sx + 10, top + 1), fill=hx("e8e4de"))
    d.rectangle([sx + 9, top - 2, sx + 15, top - 1], fill=hx("d8dce4"), outline=hx("5a5e68"))
    d.point((sx + 10, top - 2), fill=hx("ffffff"))
    # a silver-backed hairbrush lying bristles down, a tortoiseshell comb tucked in front of it
    bx = sx + 22
    d.rounded_rectangle([bx, top, bx + 12, top + 4], 2, fill=hx("b8b8c0"), outline=hx("4a4a54"))
    d.line([(bx + 2, top + 1), (bx + 9, top + 1)], fill=hx("f0f0f4"))
    d.point((bx + 6, top + 2), fill=hx("80808c"))
    d.rectangle([bx + 12, top + 1, bx + 19, top + 3], fill=hx("a8a8b0"), outline=hx("4a4a54"))
    for k in range(bx + 1, bx + 12, 2):
        d.point((k, top + 5), fill=hx("2a1a14"))
    d.line([(bx + 2, top + 6), (bx + 12, top + 6)], fill=hx("8a4a1a"))
    d.point((bx + 5, top + 6), fill=hx("c8843a"))
    if lipstick:
        # her lipstick, standing uncapped: a fluted gold case, the red bullet worn to a slant, the cap lying by it
        lx = LIPSTICK_X
        d.rectangle([lx, top - 8, lx + 4, top + 1], fill=hx("c8a040"), outline=hx("4a3412"))
        d.line([(lx + 1, top - 7), (lx + 1, top)], fill=hx("f8e090"))
        d.line([(lx + 3, top - 7), (lx + 3, top)], fill=hx("a07a28"))
        d.line([(lx + 1, top - 4), (lx + 3, top - 4)], fill=hx("6a4a18"))
        d.rectangle([lx + 1, top - 10, lx + 3, top - 8], fill=hx("e0c060"), outline=hx("6a4a18"))
        d.polygon([(lx + 1, top - 11), (lx + 3, top - 14), (lx + 3, top - 11)], fill=hx("d02040"),
                  outline=hx("6a0e1a"))
        d.point((lx + 2, top - 12), fill=hx("ff6a80"))
        d.rectangle([lx + 6, top - 2, lx + 12, top + 1], fill=hx("c8a040"), outline=hx("4a3412"))
        d.line([(lx + 7, top - 1), (lx + 11, top - 1)], fill=hx("f8e090"))
        d.line([(lx + 12, top - 1), (lx + 12, top)], fill=hx("6a4a18"))
    # a perfume atomiser: a faceted rose bottle, a gilt neck, a tasselled rubber bulb on its tube
    ax = LIPSTICK_X + 16
    d.polygon([(ax, top - 6), (ax + 3, top - 10), (ax + 7, top - 10), (ax + 10, top - 6), (ax + 9, top + 1),
               (ax + 1, top + 1)], fill=hx("d8909c"), outline=hx("6a3040"))
    d.line([(ax + 3, top - 8), (ax + 2, top - 1)], fill=hx("f4d0d8"))
    d.line([(ax + 5, top - 5), (ax + 5, top)], fill=hx("b06878"))
    d.rectangle([ax + 4, top - 13, ax + 6, top - 10], fill=hx("d8b050"), outline=hx("4a3412"))
    d.line([(ax + 6, top - 12), (ax + 9, top - 14), (ax + 12, top - 12)], fill=hx("4a2a2a"))
    d.ellipse([ax + 11, top - 13, ax + 16, top - 8], fill=hx("a01e2e"), outline=hx("4a0e14"))
    d.point((ax + 12, top - 12), fill=hx("e85a6a"))
    d.line([(ax + 14, top - 8), (ax + 15, top - 4)], fill=hx("d8b050"))
    d.point((ax + 15, top - 3), fill=hx("f0d070"))
    if compact:
        # her compact: open, a gold case with an engraved rim, the lid's little mirror propped up, a pan of face
        # powder with no puff in it
        cx = COMPACT_X
        d.ellipse([cx - 7, top - 2, cx + 7, top + 3], fill=hx("c8a050"), outline=hx("4a3412"))
        d.ellipse([cx - 5, top - 1, cx + 5, top + 2], fill=hx("f0dcc8"))
        d.arc([cx - 4, top - 1, cx + 4, top + 2], 200, 340, fill=hx("d8bca4"))
        d.point((cx - 6, top + 1), fill=hx("f8e090"))
        d.point((cx + 6, top + 1), fill=hx("8a6a28"))
        d.chord([cx - 7, top - 15, cx + 7, top - 1], 180, 360, fill=hx("a87a28"), outline=hx("3a2408"))
        d.chord([cx - 5, top - 13, cx + 5, top - 2], 180, 360, fill=hx("4a5668"))
        for ex in range(cx - 6, cx + 7, 3):
            d.point((ex, top - 2 - round(12 * (1 - ((ex - cx) / 7) ** 2) ** 0.5)), fill=hx("e8c870"))
        d.line([(cx - 3, top - 4), (cx + 1, top - 10)], fill=hx("e8f0f8"))
        d.point((cx + 3, top - 6), fill=hx("c8d0dc"))
        d.point((cx - 1, top - 3), fill=hx("f8d0c0"))
    noise(img, (x0 - 4, top, x1 + 4, FLOOR), 3, 3530)


def backstage_stool(img):
    """A round padded stool pulled up to the table."""
    d = ImageDraw.Draw(img)
    cx, y0 = 280, 140
    shadow(img, "ellipse", [cx - 16, y0 + 18, cx + 16, y0 + 25], 0.5, 3)
    for lx, fx in ((cx - 10, cx - 13), (cx + 10, cx + 13), (cx - 3, cx - 4), (cx + 3, cx + 4)):
        d.line([(lx, y0 + 4), (fx, y0 + 21)], fill=WOOD_DEEP, width=2)
    d.line([(cx - 11, y0 + 14), (cx + 11, y0 + 14)], fill=hx("4a2814"))
    d.ellipse([cx - 14, y0 - 2, cx + 14, y0 + 7], fill=VELVET_DARK, outline=WOOD_DEEP)
    d.ellipse([cx - 13, y0 - 3, cx + 13, y0 + 4], fill=VELVET)
    d.arc([cx - 11, y0 - 3, cx + 7, y0 + 2], 190, 300, fill=mul(VELVET, 1.4))
    for nx in range(cx - 12, cx + 13, 3):
        d.point((nx, y0 + 4 + round(1.5 * (1 - (abs(nx - cx) / 13) ** 2))), fill=BRASS)


def dressing_screen(img):
    """A three-leaf folding screen: black lacquer frames on brass hinges, painted silk panels with a crane and
    blossom on each."""
    d = ImageDraw.Draw(img)
    leaves = ((378, 404, 40, 0), (405, 431, 36, 1), (432, 458, 40, 2))
    lacquer, lacquer_hi, gilt = hx("1a0c0a"), hx("4a2a22"), hx("b88a3a")
    shadow(img, "rect", [372, FLOOR - 2, 462, FLOOR + 6], 0.45, 4)
    for x0, x1, y0, i in leaves:
        # the frame: a carved crest at the top, little feet at the bottom
        d.rectangle([x0, y0, x1, FLOOR - 1], fill=lacquer, outline=hx("0a0404"))
        d.polygon([(x0, y0), (x0 + 4, y0 - 3), (x1 - 4, y0 - 3), (x1, y0)], fill=lacquer, outline=hx("0a0404"))
        d.line([(x0 + 4, y0 - 2), (x1 - 4, y0 - 2)], fill=lacquer_hi)
        d.point(((x0 + x1) // 2, y0 - 2), fill=gilt)
        d.line([(x0 + 1, y0 + 1), (x0 + 1, FLOOR - 2)], fill=lacquer_hi)
        d.rectangle([x0 + 1, FLOOR - 1, x0 + 4, FLOOR + 2], fill=lacquer)
        d.rectangle([x1 - 4, FLOOR - 1, x1 - 1, FLOOR + 2], fill=lacquer)
        # the upper silk panel, its painted motif, and a carved lower panel
        silk = (hx("6a3a2a"), hx("7a4632"), hx("5e3224"))[i]
        px0, px1, py0, py1 = x0 + 4, x1 - 4, y0 + 4, FLOOR - 30
        vgrad(img, (px0, py0, px1, py1), mul(silk, 1.25), mul(silk, 0.8))
        d.rectangle([px0 - 1, py0 - 1, px1 + 1, py1 + 1], outline=gilt)
        rnd = random.Random(3540 + i)
        stem = [(px0 + 3, py1 - 2), (px0 + 7, py1 - 30), (px0 + 6, py0 + 28), (px1 - 3, py0 + 12)]
        d.line(stem, fill=hx("2a1810"))
        d.line([(px0 + 7, py1 - 30), (px1 - 2, py1 - 40)], fill=hx("2a1810"))
        for _ in range(9):
            sx, sy = rnd.choice(stem[1:])
            bx, by = sx + rnd.randint(-3, 3), sy + rnd.randint(-3, 3)
            d.point((min(max(bx, px0), px1), by), fill=hx("f0b8c0"))
            d.point((min(max(bx + 1, px0), px1), by), fill=hx("c87888"))
        # a crane, white with a red crown, a different stance on each leaf
        cx, cy = px0 + 8 + (i % 2) * 2, py0 + 50 + i * 4
        d.ellipse([cx - 4, cy - 2, cx + 4, cy + 2], fill=hx("ece6da"), outline=hx("8a8278"))
        d.line([(cx + 3, cy - 1), (cx + 5, cy - 8), (cx + 4 - 2 * (i == 1), cy - 11)], fill=hx("ece6da"))
        d.point((cx + 4 - 2 * (i == 1), cy - 12), fill=hx("c8202a"))
        d.line([(cx - 4, cy), (cx - 7, cy + 2)], fill=hx("2a2420"))
        d.line([(cx - 1, cy + 2), (cx - 1, cy + 10)], fill=hx("2a2420"))
        d.line([(cx + 1, cy + 2), (cx + 2 + (i == 2) * 2, cy + 10)], fill=hx("2a2420"))
        d.rectangle([px0, FLOOR - 26, px1, FLOOR - 5], fill=hx("24100c"), outline=gilt)
        d.rectangle([px0 + 3, FLOOR - 23, px1 - 3, FLOOR - 8], outline=lacquer_hi)
        d.ellipse([(px0 + px1) // 2 - 3, FLOOR - 19, (px0 + px1) // 2 + 3, FLOOR - 12], outline=gilt)
        d.point(((px0 + px1) // 2, FLOOR - 16), fill=gilt)
    # brass hinges joining the leaves
    for hxp in (404, 431):
        for hy in (48, 90, FLOOR - 20):
            d.rectangle([hxp - 1, hy, hxp + 1, hy + 5], fill=BRASS, outline=hx("4a3412"))
            d.point((hxp, hy + 1), fill=hx("fff0c0"))
    noise(img, (378, 30, 458, FLOOR), 3, 3541)


def backstage_rug(img):
    """A worn deco rug in front of the table, laid in the floor's perspective: a gilt-on-plum border, a wine field,
    a stepped diamond medallion with corner fans, fringe at the short ends and a bald patch where the stool stands."""
    d = ImageDraw.Draw(img)
    (bx0, bx1), (fx0, fx1), y0, y1 = (220, 340), (208, 352), 168, 196

    def at(u, v):
        return (bx0 + (bx1 - bx0) * u + ((fx0 + (fx1 - fx0) * u) - (bx0 + (bx1 - bx0) * u)) * v, y0 + (y1 - y0) * v)

    def quad(u0, v0, u1, v1, **kw):
        d.polygon([at(u0, v0), at(u1, v0), at(u1, v1), at(u0, v1)], **kw)

    def diamond(cu, cv, ru, rv, **kw):
        d.polygon([at(cu, cv - rv), at(cu + ru, cv), at(cu, cv + rv), at(cu - ru, cv)], **kw)

    shadow(img, "polygon", [at(0, 0.1), at(1, 0.1), at(1.02, 1.1), at(-0.02, 1.1)], 0.4, 3)
    quad(0, 0, 1, 1, fill=hx("2a1418"), outline=hx("140a0c"))
    quad(0.03, 0.12, 0.97, 0.88, fill=hx("8a6a34"))
    quad(0.045, 0.19, 0.955, 0.81, fill=hx("3a1a2a"))
    for k in range(13):  # a stepped key pattern running round the border
        u = 0.06 + k * 0.07
        d.point(at(u, 0.06), fill=hx("a8843a"))
        d.point(at(u + 0.02, 0.06), fill=hx("a8843a"))
        d.point(at(u, 0.94), fill=hx("a8843a"))
        d.point(at(u + 0.02, 0.94), fill=hx("a8843a"))
    for v in (0.3, 0.5, 0.7):
        d.point(at(0.015, v), fill=hx("a8843a"))
        d.point(at(0.985, v), fill=hx("a8843a"))
    quad(0.06, 0.24, 0.94, 0.76, fill=hx("6a2232"))
    # the medallion: stepped diamonds, plum, gilt and teal, a gilt eye at the centre
    diamond(0.5, 0.5, 0.2, 0.26, fill=hx("3a1a2a"), outline=hx("a8843a"))
    diamond(0.5, 0.5, 0.14, 0.18, fill=hx("2a5a5a"))
    diamond(0.5, 0.5, 0.09, 0.12, fill=hx("8a6a34"))
    diamond(0.5, 0.5, 0.04, 0.06, fill=hx("e0c070"))
    for cu in (0.2, 0.8):  # flanking lozenges and stripes
        diamond(cu, 0.5, 0.06, 0.12, fill=hx("2a5a5a"), outline=hx("a8843a"))
        d.point(at(cu, 0.5), fill=hx("e0c070"))
    for cu, cv in ((0.06, 0.24), (0.94, 0.24), (0.06, 0.76), (0.94, 0.76)):  # corner fans
        d.ellipse([at(cu, cv)[0] - 4, at(cu, cv)[1] - 2, at(cu, cv)[0] + 4, at(cu, cv)[1] + 2], fill=hx("8a6a34"))
    quad(0.06, 0.24, 0.94, 0.76, outline=hx("a8843a"))
    # wear: the pile rubbed through where the stool and feet go, a frayed corner
    rnd = random.Random(3551)
    for _ in range(46):
        u, v = 0.5 + rnd.gauss(0, 0.1), 0.35 + rnd.gauss(0, 0.12)
        if 0.08 < u < 0.92 and 0.15 < v < 0.85:
            px, py = at(u, v)
            d.point((round(px), round(py)), fill=hx("7a5a4a"))
    d.polygon([at(0.92, 0.88), at(1, 0.8), at(1, 1), at(0.96, 1)], fill=hx("4a2a24"))
    # fringe at the two short ends
    for k in range(10):
        v = 0.05 + k * 0.1
        lx, ly = at(0, v)
        rx, ry = at(1, v)
        d.line([(lx, ly), (lx - 3, ly + 1)], fill=hx("c8b48a"))
        if k != 8:
            d.line([(rx, ry), (rx + 3, ry + 1)], fill=hx("c8b48a"))
    noise(img, (204, 166, 356, 198), 3, 3550)


BACKSTAGE_DOOR_BOX = (BACKSTAGE_DOOR[0] - 10, 22 + TOP, BACKSTAGE_DOOR[1] + 22, FLOOR + 20 + TOP)


def backstage_scene(door="shut", makeup=True):
    img = Image.new("RGB", (W, H))
    backstage_wall(img)
    backstage_door(img, door)
    costume_rail(img)
    dressing_screen(img)
    dressing_table(img, compact=makeup, lipstick=makeup)
    backstage_stool(img)
    backstage_rug(img)
    shadow(img, "rect", [0, 0, 18, H - 1], 0.3, 10, hx("20090c"))
    shadow(img, "rect", [W - 18, 0, W - 1, H - 1], 0.3, 10, hx("20090c"))
    full = tall(img, ceiling_band)
    pendant(full, 150, TOP + 12, [96, TOP + 90, 210, TOP + 200])
    light(full, "ellipse", [200, TOP + 120, 360, TOP + 200], LAMPLIGHT, 0.08, 16)
    vignette(full, 0.7, tint=(34, 12, 18), blur=50)
    return full


def build():
    hall = hall_scene()
    lounge = lounge_scene()
    stage = stage_scene()
    backstage = backstage_scene()
    # one palette for the dressing room and its overlays, taken with the makeup on the table
    pal = palette_of(backstage, 128)
    out = {
        "club_hall.png": pixelize(hall, n=128),
        "club_lounge.png": pixelize(lounge, n=128),
        "club_stage.png": pixelize(stage, n=128),
        "club_backstage.png": pixelize(backstage_scene(makeup=False), pal),
    }
    for name, img in out.items():
        save(img, "rooms", name)
    # Eleanor's lipstick and compact, each vanishing from the table when she takes it
    full = pixelize(backstage, pal)
    for name, box in (("lipstick", BACKSTAGE_LIPSTICK_BOX), ("compact", BACKSTAGE_COMPACT_BOX)):
        save(full.crop(box), "rooms", f"club_backstage_{name}.png")
        print(f"club_backstage_{name}.png at {box[:2]}")
    # the stage door opening for the old man in the Second Interlude, on the room's own palette
    for state in ("ajar", "open"):
        save(pixelize(backstage_scene(state), pal).crop(BACKSTAGE_DOOR_BOX), "rooms", f"club_backstage_door_{state}.png")
    return out["club_hall.png"]
