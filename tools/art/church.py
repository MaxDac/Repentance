"""Grand Catholic cathedral interior and exterior, inspired by St. Patrick's Cathedral."""
from PIL import Image, ImageDraw
import math
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save

H = FULL_H
VP = (240, 90)
STONE = hx("8d887f")
STONE_D = hx("5b5752")
STONE_L = hx("b8b1a5")
WOOD = hx("6b4124")
WOOD_D = hx("3a2416")
GOLD = hx("c6a25a")


def along(p, t, vp=VP):
    return (vp[0] + (p[0] - vp[0]) * t, vp[1] + (p[1] - vp[1]) * t)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def pointed_shape(x0, x1, y0, y1, apex=None):
    apex = apex if apex is not None else y0 - (x1 - x0) * 0.42
    cx = (x0 + x1) / 2
    return [(x0, y1), (x0, y0), (cx, apex), (x1, y0), (x1, y1)]


def rose_window(d, cx, cy, r, frame, glass):
    d.ellipse([cx - r - 4, cy - r - 4, cx + r + 4, cy + r + 4], fill=frame)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=glass)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=frame)
    for i in range(12):
        a = i * math.pi / 6
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        d.line([(cx, cy), (x, y)], fill=frame)
        d.ellipse([cx + math.cos(a) * (r * 0.55) - 4, cy + math.sin(a) * (r * 0.55) - 4,
                   cx + math.cos(a) * (r * 0.55) + 4, cy + math.sin(a) * (r * 0.55) + 4], outline=frame)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=frame, width=2)
    d.ellipse([cx - int(r * 0.58), cy - int(r * 0.58), cx + int(r * 0.58), cy + int(r * 0.58)],
              outline=frame, width=2)


def stone_tiles(img, poly, base, seam, seed):
    d = ImageDraw.Draw(img)
    d.polygon(poly, fill=base)
    top_l, top_r, bot_r, bot_l = poly
    for i in range(-6, 7):
        xb = bot_l[0] + (bot_r[0] - bot_l[0]) * (i + 6) / 12
        xt = top_l[0] + (top_r[0] - top_l[0]) * (i + 6) / 12
        d.line([(xt, top_l[1]), (xb, bot_l[1])], fill=seam)
    y, step = top_l[1], 4.0
    while y < bot_l[1]:
        left = lerp(top_l, bot_l, (y - top_l[1]) / max(1, bot_l[1] - top_l[1]))
        right = lerp(top_r, bot_r, (y - top_r[1]) / max(1, bot_r[1] - top_r[1]))
        d.line([left, right], fill=mix(base, seam, 0.6))
        y += step
        step *= 1.23
    noise(img, (int(min(p[0] for p in poly)), int(min(p[1] for p in poly)),
                int(max(p[0] for p in poly)), int(max(p[1] for p in poly))), 5, seed)


def interior_shell(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, H - 1), hx("433d3e"), hx("1e1a18"))
    vault = [(0, 0), (W - 1, 0), (360, 146), (120, 146)]
    d.polygon(vault, fill=hx("645f5b"))
    left_wall = [(0, 0), (120, 0), (164, 146), (0, 220)]
    right_wall = [(W - 1, 0), (360, 0), (316, 146), (W - 1, 220)]
    d.polygon(left_wall, fill=hx("777068"))
    d.polygon(right_wall, fill=hx("726c66"))
    side_left = [(0, 220), (164, 146), (184, H - 1), (0, H - 1)]
    side_right = [(W - 1, 220), (316, 146), (296, H - 1), (W - 1, H - 1)]
    d.polygon(side_left, fill=hx("584b42"))
    d.polygon(side_right, fill=hx("564940"))
    stone_tiles(img, [(184, 146), (296, 146), (400, H - 1), (80, H - 1)], hx("82786d"), hx("5c534c"), 71)
    noise(img, (0, 0, W - 1, 160), 6, 17)
    for t in (1.0, 1.28, 1.62, 2.02, 2.55, 3.22):
        lx, ly = along((174, 66), t)
        rx, ry = along((306, 66), t)
        ax, ay = along((240, 22), t)
        width = max(1, int(5 / t))
        for off in range(width):
            d.line([(lx, ly + off), (ax, ay)], fill=STONE_D)
            d.line([(ax, ay), (rx, ry + off)], fill=STONE_D)
        d.line([along((132, 28), t), (ax, ay)], fill=hx("8d8579"))
        d.line([along((348, 28), t), (ax, ay)], fill=hx("8d8579"))
    d.line([(240, 12), VP], fill=hx("938c80"), width=3)


def stained_window(img, side, t, cols):
    d = ImageDraw.Draw(img)
    if side == "left":
        outer = [along((116, 126), t), along((116, 72), t), along((128, 54), t), along((140, 72), t),
                 along((140, 126), t)]
        inset = [along((120, 122), t), along((120, 78), t), along((128, 62), t), along((136, 78), t),
                 along((136, 122), t)]
        glow = [along((110, 128), t), along((110, 68), t), along((128, 48), t), along((146, 68), t),
                along((146, 128), t)]
    else:
        outer = [along((340, 126), t), along((340, 72), t), along((352, 54), t), along((364, 72), t),
                 along((364, 126), t)]
        inset = [along((344, 122), t), along((344, 78), t), along((352, 62), t), along((360, 78), t),
                 along((360, 122), t)]
        glow = [along((334, 128), t), along((334, 68), t), along((352, 48), t), along((370, 68), t),
                along((370, 128), t)]
    light(img, "polygon", glow, mix(cols[1], hx("ffffff"), 0.35), 0.18, 8)
    d.polygon(outer, fill=STONE_D)
    d.polygon(inset, fill=cols[1])
    bx0 = int(min(p[0] for p in inset))
    bx1 = int(max(p[0] for p in inset))
    by0 = int(min(p[1] for p in inset))
    by1 = int(max(p[1] for p in inset))
    for i, col in enumerate(cols):
        x0 = bx0 + (bx1 - bx0) * i / len(cols)
        x1 = bx0 + (bx1 - bx0) * (i + 1) / len(cols)
        d.rectangle([x0, by0, x1, by1], fill=col)
    d.line([inset[0], inset[2], inset[4]], fill=hx("f4ead2"))
    d.line([((inset[0][0] + inset[4][0]) / 2, inset[1][1]), ((inset[0][0] + inset[4][0]) / 2, inset[4][1])],
           fill=hx("f4ead2"))
    d.polygon(outer, outline=STONE_L)


def interior_columns(img):
    d = ImageDraw.Draw(img)
    depths = [1.0, 1.28, 1.62, 2.02, 2.55, 3.22]
    for t in reversed(depths):
        for x0, x1 in ((152, 170), (310, 328)):
            pts = [along((x0, 154), t), along((x0, 68), t), along((x1, 68), t), along((x1, 154), t)]
            d.polygon(pts, fill=STONE)
            d.polygon([along((x0 - 4, 68), t), along((x1 + 4, 68), t), along((x1 + 3, 74), t),
                       along((x0 - 3, 74), t)], fill=STONE_L)
            d.polygon([along((x0 - 5, 154), t), along((x1 + 5, 154), t), along((x1 + 7, 160), t),
                       along((x0 - 7, 160), t)], fill=STONE_D)
            d.line([along((x0 + 2, 70), t), along((x0 + 2, 154), t)], fill=STONE_L)
            d.line([along((x1 - 2, 70), t), along((x1 - 2, 154), t)], fill=STONE_D)
        for x0, x1 in ((108, 124), (356, 372)):
            pts = [along((x0, 150), t), along((x0, 72), t), along((x1, 72), t), along((x1, 150), t)]
            d.polygon(pts, fill=hx("6a645e"))
            d.line([along((x0 + 2, 74), t), along((x0 + 2, 150), t)], fill=STONE_L)
        lx, ly = along((170, 74), t)
        rx, ry = along((310, 74), t)
        ax, ay = along((240, 28), t)
        d.line([(lx, ly), (ax, ay), (rx, ry)], fill=STONE_L, width=max(1, int(6 / t)))


def pew(img, side, t):
    d = ImageDraw.Draw(img)
    if side == "left":
        top = [along((104, 156), t), along((170, 156), t), along((178, 166), t), along((94, 166), t)]
        front = [along((94, 166), t), along((178, 166), t), along((182, 184), t), along((88, 184), t)]
        back = [along((104, 144), t), along((170, 144), t), along((170, 156), t), along((104, 156), t)]
        cap = [along((160, 144), t), along((170, 144), t), along((178, 184), t), along((168, 184), t)]
    else:
        top = [along((310, 156), t), along((376, 156), t), along((386, 166), t), along((302, 166), t)]
        front = [along((302, 166), t), along((386, 166), t), along((392, 184), t), along((298, 184), t)]
        back = [along((310, 144), t), along((376, 144), t), along((376, 156), t), along((310, 156), t)]
        cap = [along((310, 144), t), along((320, 144), t), along((312, 184), t), along((302, 184), t)]
    d.polygon(front, fill=WOOD_D)
    d.polygon(back, fill=mul(WOOD, 1.18))
    d.polygon(top, fill=WOOD)
    d.polygon(cap, fill=mul(WOOD, 1.12))
    d.line([top[0], top[1]], fill=hx("9a6a44"))
    d.line([back[0], back[1]], fill=hx("a87a54"))


def interior_pews(img):
    for t in reversed((1.15, 1.38, 1.68, 2.02, 2.42, 2.9)):
        pew(img, "left", t)
        pew(img, "right", t)
    shadow(img, "polygon", [(66, 186), (182, 168), (188, H - 1), (44, H - 1)], 0.22, 8, hx("403838"))
    shadow(img, "polygon", [(298, 168), (414, 186), (436, H - 1), (292, H - 1)], 0.22, 8, hx("403838"))


def altar(img):
    d = ImageDraw.Draw(img)
    d.polygon([(194, 146), (286, 146), (294, 164), (186, 164)], fill=hx("4f443d"))
    d.polygon([(204, 138), (276, 138), (282, 146), (198, 146)], fill=hx("d8d1c0"))
    d.rectangle([214, 146, 266, 172], fill=hx("a98e72"))
    d.line([(214, 146), (266, 146)], fill=hx("eadfb8"))
    d.rectangle([233, 100, 247, 138], fill=hx("836548"))
    d.rectangle([236, 84, 244, 104], fill=GOLD)
    d.rectangle([228, 92, 252, 98], fill=GOLD)
    d.ellipse([180, 126, 188, 136], fill=GOLD)
    d.ellipse([292, 126, 300, 136], fill=GOLD)
    d.rectangle([183, 132, 185, 150], fill=hx("e7ddb2"))
    d.rectangle([295, 132, 297, 150], fill=hx("e7ddb2"))
    light(img, "ellipse", [172, 126, 194, 154], hx("ffd88a"), 0.28, 6)
    light(img, "ellipse", [286, 126, 308, 154], hx("ffd88a"), 0.28, 6)
    light(img, "ellipse", [202, 82, 278, 156], hx("f4d694"), 0.18, 16)


def stained_light(img):
    colors = [
        (hx("7a3040"), [(86, 148), (126, 138), (162, H - 1), (88, H - 1)]),
        (hx("385a9a"), [(114, 156), (150, 146), (206, H - 1), (132, H - 1)]),
        (hx("b48a30"), [(138, 164), (170, 154), (238, H - 1), (166, H - 1)]),
        (hx("b48a30"), [(242, 154), (312, 146), (350, H - 1), (272, H - 1)]),
        (hx("305894"), [(274, 144), (332, 136), (392, H - 1), (316, H - 1)]),
        (hx("803040"), [(306, 136), (352, 128), (430, H - 1), (348, H - 1)])
    ]
    for col, pts in colors:
        light(img, "polygon", pts, col, 0.24, 12)
    light(img, "ellipse", [176, 182, 310, 266], hx("e4be76"), 0.18, 24)


def interior_candles(img):
    d = ImageDraw.Draw(img)
    for x, y in ((154, 176), (326, 176), (128, 194), (352, 194)):
        d.rectangle([x, y, x + 2, y + 10], fill=hx("e6dcc0"))
        d.point((x + 1, y - 1), fill=hx("fff4a0"))
        light(img, "ellipse", [x - 6, y - 8, x + 10, y + 12], hx("ffd890"), 0.24, 6)


def paint_interior():
    img = Image.new("RGB", (W, H))
    interior_shell(img)
    for t, cols in ((1.04, [hx("6a3058"), hx("2f62a5"), hx("d9a84c")]),
                    (1.42, [hx("8f3434"), hx("3c5fb0"), hx("d2a250")]),
                    (2.04, [hx("7b2e52"), hx("3e63a8"), hx("bf9540")])):
        stained_window(img, "left", t, cols)
        stained_window(img, "right", t, cols[::-1])
    altar(img)
    interior_columns(img)
    interior_pews(img)
    interior_candles(img)
    stained_light(img)
    shadow(img, "ellipse", [150, 116, 330, 154], 0.18, 14, hx("56504a"))
    vignette(img, 0.5, tint=(54, 40, 26), blur=44)
    return img


def exterior_bg(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 184), hx("c9d7e5"), hx("eff1e6"))
    d.rectangle([0, 184, W - 1, H - 1], fill=hx("7e7468"))
    d.rectangle([0, 210, W - 1, H - 1], fill=hx("675b50"))
    for x0, x1, top, col in ((0, 54, 82, hx("958a84")), (24, 76, 72, hx("8a8078")), (404, W - 1, 88, hx("91857f")),
                             (370, 430, 74, hx("847872"))):
        d.rectangle([x0, top, x1, 184], fill=col)
        for y in range(top + 12, 170, 22):
            d.line([(x0 + 6, y), (x1 - 6, y)], fill=mul(col, 0.72))
    d.rectangle([0, 184, W - 1, 188], fill=hx("5c544e"))
    d.line([(0, 232), (W - 1, 232)], fill=hx("8c8277"))


def pointed_portal(d, x0, x1, top, bottom, stone, door):
    d.polygon(pointed_shape(x0, x1, top, bottom), fill=stone)
    d.polygon(pointed_shape(x0 + 5, x1 - 5, top + 6, bottom - 2, top - 12), fill=door)
    d.line([(x0 + 5, bottom - 8), (x1 - 5, bottom - 8)], fill=mul(door, 0.7))


def tower_openings(d, x0, y0):
    for yy in (y0 + 16, y0 + 34):
        d.polygon(pointed_shape(x0 + 8, x0 + 26, yy, yy + 20, yy - 10), fill=hx("38404c"))
        d.line([(x0 + 17, yy + 2), (x0 + 17, yy + 18)], fill=hx("9ca7b4"))


def facade(img):
    d = ImageDraw.Draw(img)
    d.polygon([(156, 74), (324, 74), (352, 196), (128, 196)], fill=STONE)
    d.polygon([(156, 74), (240, 42), (324, 74)], fill=hx("7b746c"))
    d.polygon([(104, 92), (156, 92), (168, 214), (92, 214)], fill=hx("858079"))
    d.polygon([(324, 92), (376, 92), (388, 214), (312, 214)], fill=hx("848079"))
    d.polygon([(92, 214), (168, 214), (176, 240), (84, 240)], fill=hx("6a625a"))
    d.polygon([(312, 214), (388, 214), (396, 240), (304, 240)], fill=hx("6a625a"))
    d.polygon([(96, 92), (132, 12), (164, 92)], fill=hx("767069"))
    d.polygon([(316, 92), (348, 12), (384, 92)], fill=hx("757068"))
    d.rectangle([122, 94, 138, 132], fill=hx("68615a"))
    d.rectangle([342, 94, 358, 132], fill=hx("68615a"))
    d.polygon([(128, 12), (132, 2), (136, 12)], fill=STONE_L)
    d.polygon([(344, 12), (348, 2), (352, 12)], fill=STONE_L)
    d.line([(132, 0), (132, 16)], fill=STONE_L)
    d.line([(348, 0), (348, 16)], fill=STONE_L)
    d.line([(126, 8), (138, 8)], fill=STONE_L)
    d.line([(342, 8), (354, 8)], fill=STONE_L)
    d.polygon([(72, 188), (104, 136), (110, 140), (88, 206)], fill=hx("8a847d"))
    d.polygon([(408, 188), (376, 136), (370, 140), (392, 206)], fill=hx("8a847d"))
    d.polygon([(52, 214), (76, 150), (86, 150), (68, 224)], fill=hx("7c7670"))
    d.polygon([(428, 214), (404, 150), (394, 150), (412, 224)], fill=hx("7c7670"))
    d.line([(156, 74), (146, 194)], fill=STONE_D)
    d.line([(324, 74), (334, 194)], fill=STONE_D)
    d.line([(240, 42), (240, 196)], fill=STONE_L)
    for x in (176, 208, 272, 304):
        d.line([(x, 82), (x, 198)], fill=mul(STONE, 0.75))
    for y in (108, 132, 156):
        d.line([(152, y), (328, y)], fill=mul(STONE, 0.78))
    noise(img, (84, 0, 396, 240), 6, 121)
    rose_window(d, 240, 112, 30, hx("635d56"), hx("6f85b0"))
    tower_openings(d, 116, 94)
    tower_openings(d, 336, 94)
    pointed_portal(d, 164, 212, 148, 206, hx("5d5852"), hx("3a2b20"))
    pointed_portal(d, 216, 264, 136, 210, hx("655e58"), hx("3a2b20"))
    pointed_portal(d, 268, 316, 148, 206, hx("5d5852"), hx("3a2b20"))
    d.polygon(pointed_shape(204, 276, 84, 142, 62), outline=STONE_L)
    for x in (162, 214, 266, 318):
        d.polygon(pointed_shape(x, x + 26, 98, 138, 82), fill=hx("6f87aa"), outline=hx("ccc6ba"))
    d.rectangle([170, 206, 310, 214], fill=hx("5e5650"))
    d.polygon([(170, 214), (310, 214), (322, 246), (158, 246)], fill=hx("71675e"))
    for i in range(7):
        y = 214 + i * 4
        d.line([(170 - i * 2, y), (310 + i * 2, y)], fill=hx("8f8376"))
    light(img, "ellipse", [184, 78, 298, 150], hx("f5efdf"), 0.12, 18)


def street_details(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, 246, W - 1, H - 1], fill=hx("5e5349"))
    d.line([(0, 246), (W - 1, 246)], fill=hx("988c7e"))
    for x in range(0, W, 34):
        d.line([(x, 258), (x + 16, 258)], fill=hx("86796d"))
    shadow(img, "rect", [94, 206, 388, H - 1], 0.18, 10, hx("4c4743"))


def paint_exterior():
    img = Image.new("RGB", (W, H))
    exterior_bg(img)
    facade(img)
    street_details(img)
    vignette(img, 0.38, tint=(26, 28, 34), blur=38)
    return img


def build():
    interior = paint_interior()
    exterior = paint_exterior()
    pal = palette_of(Image.blend(interior, exterior, 0.5), 128)
    save(pixelize(interior, pal), "rooms", "church_interior.png")
    save(pixelize(exterior, pal), "rooms", "church_exterior.png")
    return interior, exterior
