"""Act 2/3 locations: Rose's terrace house at dusk, the night road behind the Harrington building, Harrington senior's
office at night, and Daniel's bedroom in the present day.

Each room is painted once per state; overlays are crops of the state variant pixelized with the base palette, so they
line up pixel-exactly when placed at the box's top-left (printed by build())."""
import random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import (W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, palette_of, pixelize, save,
                     text, floor_boards)

H = FULL_H


def bricks(img, box, col, mortar, seed, h=5, w=12):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    rnd = random.Random(seed)
    for y in range(y0, y1, h):
        off = (w // 2) if ((y - y0) // h) % 2 else 0
        for x in range(x0 - off, x1, w):
            c = mul(col, rnd.uniform(0.86, 1.1))
            d.rectangle([max(x0, x + 1), y + 1, min(x1, x + w - 1), min(y1, y + h - 1)], fill=c)
        d.line([(x0, y), (x1, y)], fill=mortar)
    noise(img, box, 6, seed)


def overlay(variant, base_px, pal, box, name):
    v = pixelize(variant, pal)
    diff = ImageChops.difference(v.crop(box), base_px.crop(box)).convert("L").point(lambda p: 255 if p else 0)
    bb = diff.getbbox()
    if not bb:
        raise ValueError(name)
    tight = (box[0] + bb[0], box[1] + bb[1], box[0] + bb[2], box[1] + bb[3])
    save(v.crop(tight), "rooms", f"{name}.png")
    print(name, "at", tight[:2])


# ------------------------------------------------------------------------------------------------ ROSE'S HOUSE

def window(d, x0, y0, x1, y1, lit, frame=hx("d8d0c0")):
    d.rectangle([x0 - 3, y0 - 6, x1 + 3, y0 - 2], fill=hx("b8ae9a"))
    d.rectangle([x0 - 2, y1, x1 + 2, y1 + 3], fill=hx("a49a86"))
    d.rectangle([x0, y0, x1, y1], fill=hx("e8b860") if lit else hx("1c2236"))
    if lit:
        d.rectangle([x0 + 2, y0 + 2, x0 + 8, y1 - 2], fill=hx("8a3a30"))
        d.rectangle([x1 - 8, y0 + 2, x1 - 2, y1 - 2], fill=hx("8a3a30"))
    else:
        d.line([(x0 + 3, y0 + 4), (x0 + 12, y0 + 14)], fill=hx("4a5470"))
    d.rectangle([x0, y0, x1, y1], outline=frame)
    my = (y0 + y1) // 2
    d.rectangle([x0, my - 1, x1, my], fill=frame)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=frame)


def door(d, x0, y0, x1, y1, col, number=None, img=None):
    d.rectangle([x0 - 5, y0 - 16, x1 + 5, y1], fill=hx("b0a690"))
    d.pieslice([x0, y0 - 14, x1, y0 + 12], 180, 360, fill=hx("e0b868"))
    for a in range(5):
        cx = (x0 + x1) // 2
        d.line([(cx, y0 - 1), (x0 + 3 + a * (x1 - x0 - 6) // 4, y0 - 11)], fill=hx("6a5a40"))
    d.rectangle([x0, y0, x1, y1], fill=col)
    for (a, b, c, e) in ((x0 + 4, y0 + 5, (x0 + x1) // 2 - 2, y0 + 38), ((x0 + x1) // 2 + 2, y0 + 5, x1 - 4, y0 + 38),
                         (x0 + 4, y0 + 44, (x0 + x1) // 2 - 2, y1 - 6), ((x0 + x1) // 2 + 2, y0 + 44, x1 - 4, y1 - 6)):
        d.rectangle([a, b, c, e], outline=mul(col, 0.62))
        d.line([(a + 1, b + 1), (c - 1, b + 1)], fill=mul(col, 1.3))
    d.ellipse([x1 - 9, y0 + 41, x1 - 6, y0 + 44], fill=hx("d8b450"))
    if number and img is not None:
        text(img, ((x0 + x1) // 2, y0 - 5), number, hx("3a2a1a"), 8)


def stoop(d, x0, x1, top):
    for i in range(3):
        y = top + i * 6
        d.rectangle([x0 - i * 4, y, x1 + i * 4, y + 6], fill=mix(hx("9c968a"), hx("6a665e"), i / 3))
        d.line([(x0 - i * 4, y), (x1 + i * 4, y)], fill=hx("c4beb0"))


def railings(d, x0, x1, y0, y1):
    d.line([(x0, y0), (x1, y0)], fill=hx("161618"), width=2)
    for x in range(x0, x1 + 1, 5):
        d.line([(x, y0 - 3), (x, y1)], fill=hx("1c1c20"))
        d.point((x, y0 - 4), fill=hx("3a3a40"))


def paint_rose(opened=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 40), hx("2a2c58"), hx("c8705a"))
    # chimneys against the dusk
    for x in (36, 112, 212, 286, 376, 440):
        d.rectangle([x, 4, x + 14, 30], fill=hx("3a2420"))
        d.rectangle([x - 2, 2, x + 16, 6], fill=hx("2a1a18"))
        d.rectangle([x + 3, 0, x + 6, 3], fill=hx("6a4a3a"))
    houses = ((0, 150, hx("6e3a2e"), 31), (150, 330, hx("7c4634"), 32), (330, W, hx("66382e"), 33))
    for x0, x1, col, seed in houses:
        bricks(img, (x0, 26, x1 - 1, 214), col, mul(col, 0.62), seed)
        d.rectangle([x0, 24, x1 - 1, 32], fill=hx("8a8270"))
        d.line([(x0, 33), (x1 - 1, 33)], fill=hx("3a3024"))
        d.line([(x1 - 1, 24), (x1 - 1, 214)], fill=hx("2e1c16"))
    # upper floor windows
    for x0, x1, _, _ in houses:
        cw = (x1 - x0)
        for i, fx in enumerate((0.22, 0.62)):
            wx = x0 + int(cw * fx)
            window(d, wx, 52, wx + 32, 104, lit=(x0 == 150 and i == 0) or (x0 == 330 and i == 1))
    # neighbours' doors and ground windows
    door(d, 30, 120, 66, 198, hx("26303a"))
    window(d, 86, 124, 128, 178, lit=False)
    door(d, 410, 120, 446, 198, hx("4a2626"))
    window(d, 348, 124, 390, 178, lit=True)
    # Rose's door: deep green, number 7
    door(d, 222, 110, 258, 198, hx("23402e"), "7", img)
    window(d, 278, 122, 320, 178, lit=True)
    window(d, 166, 122, 204, 178, lit=False)
    # brass bell push beside the door
    d.rectangle([265, 146, 271, 156], fill=hx("8a6a2a"))
    d.ellipse([266, 149, 270, 153], fill=hx("e0c060"))
    if opened:
        # the door swung in: a warm hall, wallpaper, a stair rail and the door leaf's edge
        d.rectangle([222, 110, 258, 198], fill=hx("e8c27a"))
        for x in range(224, 258, 6):
            d.line([(x, 112), (x, 160)], fill=hx("d4a868"))
        d.rectangle([222, 160, 258, 198], fill=hx("8a5a34"))
        d.line([(240, 198), (258, 170)], fill=hx("5a3a20"), width=2)
        for x in range(244, 258, 4):
            d.line([(x, 198 - (x - 240) * 28 // 18), (x, 186 - (x - 240) * 28 // 18)], fill=hx("4a2e18"))
        d.rectangle([222, 110, 228, 198], fill=hx("18301f"))
        d.line([(228, 110), (228, 198)], fill=hx("0c1810"))
        d.rectangle([224, 112, 227, 116], fill=hx("fff0c0"))
    for x0, x1 in ((24, 72), (216, 264), (404, 452)):
        stoop(d, x0, x1, 198)
    railings(d, 0, 18, 202, 214)
    railings(d, 82, 206, 202, 214)
    railings(d, 278, 396, 202, 214)
    railings(d, 464, W - 1, 202, 214)
    # pavement and kerb
    vgrad(img, (0, 214, W - 1, 256), hx("6a6660"), hx("4e4a46"))
    for x in range(-40, W + 40, 40):
        d.line([(x, 214), (x - 24, 256)], fill=hx("3e3a36"))
    for y in (226, 240):
        d.line([(0, y), (W, y)], fill=hx("44403c"))
    d.rectangle([0, 256, W - 1, 260], fill=hx("8a8680"))
    vgrad(img, (0, 261, W - 1, H - 1), hx("2a2a2e"), hx("1e1e22"))
    noise(img, (0, 214, W - 1, H - 1), 5, 34)
    # lamp post
    d.rectangle([124, 120, 127, 254], fill=hx("161618"))
    d.rectangle([120, 250, 131, 256], fill=hx("161618"))
    d.polygon([(118, 108), (134, 108), (130, 120), (122, 120)], fill=hx("f4dc9a"), outline=hx("161618"))
    d.rectangle([118, 104, 134, 108], fill=hx("161618"))
    # dusk: cool everything down, then the lamp and lit windows glow
    dusk = ImageChops.multiply(img, Image.new("RGB", img.size, (150, 150, 196)))
    img.paste(dusk)
    light(img, "ellipse", [70, 70, 180, 260], hx("e0a050"), 0.45, 24)
    for box in ([270, 112, 330, 190], [340, 114, 400, 190], [150, 44, 196, 112], [372, 44, 420, 112]):
        light(img, "rect", box, hx("d89040"), 0.35, 10)
    if opened:
        light(img, "polygon", [(222, 110), (258, 110), (290, 224), (196, 224)], hx("f0b860"), 0.55, 10)
    vignette(img, 0.5, (20, 16, 40), 46)
    return img


def build_rose():
    base, opened = paint_rose(), paint_rose(True)
    pal = palette_of(Image.blend(base, opened, 0.5), 120)
    px = pixelize(base, pal)
    save(px, "rooms", "rose_house.png")
    overlay(opened, px, pal, (190, 100, 300, 230), "rose_house_door")
    return px


# ------------------------------------------------------------------------------------------------ HARRINGTON ROAD

def crate(d, x0, y0, s=26):
    d.rectangle([x0, y0, x0 + s, y0 + s], fill=hx("6a5232"), outline=hx("2a1e10"))
    for i in range(1, 4):
        d.line([(x0 + 1, y0 + i * s // 4), (x0 + s - 1, y0 + i * s // 4)], fill=hx("4a3820"))
    d.line([(x0 + 2, y0 + 2), (x0 + s - 2, y0 + s - 2)], fill=hx("8a6a40"), width=2)
    d.rectangle([x0, y0, x0 + s, y0 + 2], fill=hx("8a6c44"))


def paint_road(fire=False, stacked=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, 60), hx("0a0c1c"), hx("1a1c34"))
    rnd = random.Random(41)
    for _ in range(26):
        d.point((rnd.randint(0, 120), rnd.randint(0, 50)), fill=hx("8a90b0"))
    # the Harrington building: dark brick, six floors, a fire escape on the right
    bricks(img, (130, 0, W - 1, 200), hx("3a2a2a"), hx("221818"), 42, 5, 14)
    # a lower warehouse wall on the left, beyond the street mouth
    bricks(img, (0, 70, 128, 200), hx("33302e"), hx("1e1c1a"), 43, 5, 12)
    d.rectangle([0, 64, 128, 70], fill=hx("4a4642"))
    for fy in (12, 62, 112):
        for x in range(150, 460, 46):
            if 300 <= x <= 400 and fy < 120:
                continue
            d.rectangle([x, fy, x + 22, fy + 32], fill=hx("12141e"))
            d.rectangle([x - 2, fy + 32, x + 24, fy + 35], fill=hx("4a3c38"))
    # The one lit office window is also the player's destination.
    d.rectangle([330, 20, 368, 60], fill=hx("c8a060"))
    for x in range(332, 368, 5):
        d.line([(x, 22), (x, 58)], fill=hx("9a7448"))
    d.rectangle([326, 60, 372, 64], fill=hx("5a4a44"))
    d.line([(349, 20), (349, 60)], fill=hx("3a3a4a"))
    d.line([(330, 40), (368, 40)], fill=hx("3a3a4a"))
    # fire escape: landing, stair and the pulled-up drop ladder
    iron = hx("101014")
    for ly in (64, 118):
        d.rectangle([306, ly, 396, ly + 3], fill=iron)
        d.line([(306, ly - 14), (396, ly - 14)], fill=iron)
        for x in range(306, 397, 6):
            d.line([(x, ly - 14), (x, ly)], fill=iron)
        d.line([(306, ly), (396, ly)], fill=hx("565464"))
    d.line([(312, 118), (390, 66)], fill=iron, width=2)
    d.line([(319, 120), (397, 68)], fill=iron)
    for i in range(12):
        x, y = 314 + i * 6, 116 - i * 4
        d.line([(x, y), (x + 7, y + 2)], fill=hx("5a5460"))
    for x0 in (330, 338):
        d.line([(x0, 120), (x0, 160)], fill=iron)
    for y in range(124, 160, 6):
        d.line([(330, y), (338, y)], fill=iron)
        d.line([(331, y), (337, y)], fill=hx("5a5460"))
    d.line([(404, 0), (404, 198)], fill=hx("16161c"), width=3)
    d.line([(403, 0), (403, 198)], fill=hx("4a4248"))
    text(img, (255, 185), "HARRINGTON STEEL", hx("74685a"), 8)
    # back door, a bare bulb over it
    d.rectangle([156, 118, 194, 200], fill=hx("2a2620"))
    d.rectangle([160, 122, 190, 200], fill=hx("4a3a28"))
    d.rectangle([162, 124, 188, 156], outline=hx("2a2016"))
    d.rectangle([162, 162, 188, 196], outline=hx("2a2016"))
    d.ellipse([184, 160, 187, 163], fill=hx("b89a50"))
    d.rectangle([172, 104, 178, 110], fill=hx("201c18"))
    d.ellipse([171, 109, 179, 117], fill=hx("fff0b0"))
    # cobbles, wet
    vgrad(img, (0, 200, W - 1, H - 1), hx("1c1e26"), hx("2c2e36"))
    for y in range(204, H, 7):
        off = (y // 7 % 2) * 6
        for x in range(-off, W, 12):
            d.arc([x, y, x + 11, y + 6], 180, 360, fill=hx("3a3c46"))
    noise(img, (0, 200, W - 1, H - 1), 6, 44)
    for x0, y, x1 in ((16, 232, 96), (256, 246, 302), (374, 225, 456)):
        d.line([(x0, y), (x1, y)], fill=hx("424656"))
        d.line([(x0 + 8, y + 2), (x1 - 6, y + 2)], fill=hx("323644"))
    d.line([(0, 200), (W, 200)], fill=hx("12121a"))
    # trash can at the street corner
    d.rectangle([40, 176, 66, 206], fill=hx("4a4c50"), outline=hx("1a1a1e"))
    for y in (184, 194):
        d.line([(40, y), (66, y)], fill=hx("2e3034"))
    d.rectangle([37, 172, 69, 177], fill=hx("5a5c60"), outline=hx("1a1a1e"))
    d.polygon([(42, 172), (52, 164), (60, 172)], fill=hx("c8c0a8"))
    # the crates: by the wall on the right, or stacked under the ladder
    if stacked:
        crate(d, 320, 174)
        crate(d, 322, 148, 22)
    else:
        crate(d, 420, 176)
        crate(d, 447, 182, 20)
    # night and the bulb's pool of light over the door
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, (120, 128, 176))))
    light(img, "polygon", [(170, 112), (180, 112), (232, 230), (118, 230)], hx("e8c070"), 0.5, 12)
    light(img, "ellipse", [162, 98, 188, 124], hx("fff0b0"), 0.8, 4)
    light(img, "rect", [330, 20, 368, 60], hx("e0a050"), 0.18, 6)
    if fire:
        d = ImageDraw.Draw(img)
        for i, (fx, fh) in enumerate(((44, 20), (50, 28), (56, 24), (62, 16))):
            d.polygon([(fx - 4, 172), (fx, 172 - fh), (fx + 4, 172)], fill=hx("e86a20"))
            d.polygon([(fx - 2, 172), (fx, 176 - fh), (fx + 2, 172)], fill=hx("ffd060"))
        light(img, "ellipse", [0, 110, 110, 240], hx("e07030"), 0.6, 18)
    vignette(img, 0.55, (8, 8, 24), 40)
    return img


def build_road():
    base = paint_road()
    variants = paint_road(fire=True), paint_road(stacked=True)
    pal = palette_of(Image.blend(Image.blend(base, variants[0], 0.5), variants[1], 0.5), 120)
    px = pixelize(base, pal)
    save(px, "rooms", "harrington_road.png")
    overlay(variants[0], px, pal, (0, 0, W, H), "harrington_road_fire")
    overlay(variants[1], px, pal, (300, 120, 476, 212), "harrington_road_crates")
    return px


def _daub(img, shape, pts, col, k=1.0, blur=0, clip=None):
    """Normal-blends a flat colour through a (soft) mask - a brush stroke for the supersampled portrait."""
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    getattr(d, shape)(pts, fill=int(255 * k)) if shape != "line" else d.line(pts[0], fill=int(255 * k), width=pts[1])
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    if clip is not None:
        m = ImageChops.multiply(m, clip)
    img.paste(Image.composite(Image.new("RGB", img.size, col), img, m))


def harrington_portrait(w, h):
    """Oil portrait of Theodore Harrington Sr.: an old patrician in three-quarter view, bald crown with white hair
    at the temples, heavy white brows, deep-set pale eyes and a hard mouth, in evening dress with a wing collar.
    Painted at 4x and scaled down so the shading stays soft under the room's pixelization."""
    S = 4
    W4, H4 = w * S, h * S
    img = Image.new("RGB", (W4, H4))
    vgrad(img, (0, 0, W4 - 1, H4 - 1), hx("4a3a26"), hx("1c140c"))
    _daub(img, "ellipse", [W4 * 0.05, H4 * 0.02, W4 * 0.95, H4 * 0.8], hx("6a5434"), 0.6, 30)  # glow behind the head
    cx, cy = W4 * 0.5, H4 * 0.38  # face centre
    fw, fh = W4 * 0.235, H4 * 0.235
    # coat and shoulders
    _daub(img, "polygon", [(-10, H4), (W4 * 0.06, H4 * 0.74), (W4 * 0.3, H4 * 0.64), (W4 * 0.7, H4 * 0.64),
                           (W4 * 0.94, H4 * 0.74), (W4 + 10, H4)], hx("15121a"), 1, 2)
    _daub(img, "polygon", [(W4 * 0.1, H4 * 0.78), (W4 * 0.3, H4 * 0.66), (W4 * 0.36, H4 * 0.72), (W4 * 0.2, H4)],
          hx("3a3644"), 0.7, 6)  # light on the near shoulder
    # shirt front, wing collar, bow tie, satin lapels
    _daub(img, "polygon", [(cx - W4 * 0.12, H4 * 0.66), (cx + W4 * 0.1, H4 * 0.66), (cx + W4 * 0.05, H4),
                           (cx - W4 * 0.07, H4)], hx("e8e2d4"), 1, 1)
    _daub(img, "polygon", [(cx - W4 * 0.22, H4 * 0.66), (cx - W4 * 0.08, H4 * 0.7), (cx - W4 * 0.07, H4),
                           (cx - W4 * 0.2, H4)], hx("2a2632"), 1, 1)
    _daub(img, "polygon", [(cx + W4 * 0.18, H4 * 0.66), (cx + W4 * 0.07, H4 * 0.7), (cx + W4 * 0.05, H4),
                           (cx + W4 * 0.18, H4)], hx("221e28"), 1, 1)
    for s in (-1, 1):
        _daub(img, "polygon", [(cx - W4 * 0.01, H4 * 0.66), (cx + s * W4 * 0.1, H4 * 0.64), (cx + s * W4 * 0.07, H4 * 0.7)],
              hx("f4f0e6"), 1, 1)
        _daub(img, "polygon", [(cx - W4 * 0.01, H4 * 0.69), (cx + s * W4 * 0.08, H4 * 0.66), (cx + s * W4 * 0.08, H4 * 0.73)],
              hx("0c0a0e"), 1, 1)
    _daub(img, "ellipse", [cx - W4 * 0.03, H4 * 0.675, cx + W4 * 0.01, H4 * 0.71], hx("0c0a0e"), 1, 1)
    # neck, with the loose skin of age
    _daub(img, "polygon", [(cx - fw * 0.62, cy + fh * 0.5), (cx + fw * 0.55, cy + fh * 0.5), (cx + fw * 0.5, H4 * 0.68),
                           (cx - fw * 0.55, H4 * 0.68)], hx("b88c70"), 1, 2)
    _daub(img, "polygon", [(cx + fw * 0.1, cy + fh * 0.6), (cx + fw * 0.55, cy + fh * 0.5), (cx + fw * 0.5, H4 * 0.68),
                           (cx + fw * 0.1, H4 * 0.68)], hx("8a6450"), 0.7, 4)
    # the head: skull and jowls, then light from the upper left and shadow on the far side
    face = Image.new("L", img.size, 0)
    fd = ImageDraw.Draw(face)
    fd.ellipse([cx - fw, cy - fh * 1.08, cx + fw, cy + fh * 0.62], fill=255)
    fd.ellipse([cx - fw * 0.82, cy - fh * 0.2, cx + fw * 0.86, cy + fh * 0.86], fill=255)
    face = face.filter(ImageFilter.GaussianBlur(1.5))
    _daub(img, "rectangle", [0, 0, W4, H4], hx("d2a888"), 1, 0, face)
    _daub(img, "ellipse", [cx - fw * 1.1, cy - fh * 1.2, cx + fw * 0.3, cy + fh * 0.3], hx("f0d0b4"), 0.75, 12, face)
    _daub(img, "ellipse", [cx + fw * 0.35, cy - fh * 0.9, cx + fw * 1.4, cy + fh], hx("8a5e48"), 0.85, 14, face)
    _daub(img, "ellipse", [cx - fw * 0.7, cy + fh * 0.45, cx + fw * 0.9, cy + fh * 1.1], hx("9a6c54"), 0.55, 10, face)
    _daub(img, "ellipse", [cx - fw * 0.55, cy - fh * 1.0, cx + fw * 0.05, cy - fh * 0.6], hx("fff0dc"), 0.6, 8, face)  # bald dome
    for i in range(3):  # forehead lines
        y = cy - fh * (0.52 - i * 0.1)
        _daub(img, "line", ([(cx - fw * 0.55, y), (cx + fw * 0.3, y - 2)], 2), hx("a87a60"), 0.35, 1.5, face)
    # ear on the near (right) side and the white hair round the back of the head at the temples
    _daub(img, "ellipse", [cx + fw * 0.82, cy - fh * 0.2, cx + fw * 1.1, cy + fh * 0.32], hx("b07c64"), 1, 2)
    _daub(img, "ellipse", [cx + fw * 0.88, cy - fh * 0.1, cx + fw * 1.02, cy + fh * 0.2], hx("7a5040"), 0.6, 2)
    for x0, x1 in ((cx - fw * 1.08, cx - fw * 0.78), (cx + fw * 0.7, cx + fw * 1.08)):
        _daub(img, "ellipse", [x0, cy - fh * 0.62, x1, cy + fh * 0.05], hx("aaa69e"), 0.95, 4)
        _daub(img, "ellipse", [x0 + 2, cy - fh * 0.55, x1 - 2, cy - fh * 0.2], hx("ccc8c0"), 0.6, 3)
    # deep-set eyes under heavy white brows
    for s, ex in ((-1, cx - fw * 0.42), (1, cx + fw * 0.3)):
        ey = cy - fh * 0.12
        r = fw * (0.2 if s < 0 else 0.18)
        _daub(img, "ellipse", [ex - r * 1.5, ey - r * 1.1, ex + r * 1.5, ey + r * 1.1], hx("7a5040"), 0.7, 5)
        _daub(img, "ellipse", [ex - r, ey - r * 0.38, ex + r, ey + r * 0.42], hx("e4dccc"), 1, 1)
        _daub(img, "ellipse", [ex - r * 0.45 - 2, ey - r * 0.4, ex + r * 0.45 - 2, ey + r * 0.42], hx("5a7080"), 1, 0.5)
        _daub(img, "ellipse", [ex - r * 0.2 - 2, ey - r * 0.18, ex + r * 0.2 - 2, ey + r * 0.2], hx("141016"), 1, 0)
        _daub(img, "line", ([(ex - r * 1.05, ey - r * 0.32), (ex, ey - r * 0.55), (ex + r * 1.05, ey - r * 0.25)], 3),
              hx("6a4434"), 1, 0.8)  # heavy upper lid
        _daub(img, "line", ([(ex - r * 0.8, ey + r * 0.75), (ex + r * 0.9, ey + r * 0.7)], 2), hx("9a6a56"), 0.7, 1.5)
        _daub(img, "polygon", [(ex - r * 1.4, ey - r * 0.9), (ex - r * 0.2, ey - r * 1.55), (ex + r * 1.4, ey - r * 1.1),
                               (ex + r * 1.3, ey - r * 0.7), (ex - r * 1.2, ey - r * 0.55)], hx("9a948a"), 0.95, 1.5)
    # nose: a long aquiline nose with its shadow cast to the right
    nx = cx - fw * 0.08
    _daub(img, "polygon", [(nx - 3, cy - fh * 0.1), (nx + 6, cy - fh * 0.1), (nx + fw * 0.2, cy + fh * 0.3),
                           (nx + 2, cy + fh * 0.36), (nx - fw * 0.22, cy + fh * 0.3)], hx("c49478"), 1, 2)
    _daub(img, "polygon", [(nx + 6, cy - fh * 0.05), (nx + fw * 0.24, cy + fh * 0.3), (nx + fw * 0.1, cy + fh * 0.36)],
          hx("8a5a46"), 0.8, 3)
    _daub(img, "line", ([(nx - 1, cy - fh * 0.08), (nx - fw * 0.06, cy + fh * 0.26)], 3), hx("f4dcc4"), 0.8, 1.5)
    for dx in (-fw * 0.14, fw * 0.12):
        _daub(img, "ellipse", [nx + dx - 4, cy + fh * 0.3, nx + dx + 4, cy + fh * 0.36], hx("5a3428"), 0.9, 1)
    # nasolabial folds, a thin hard mouth turned down at the corners, the chin
    _daub(img, "line", ([(nx - fw * 0.26, cy + fh * 0.3), (cx - fw * 0.42, cy + fh * 0.62)], 3), hx("8a5e48"), 0.7, 2)
    _daub(img, "line", ([(nx + fw * 0.26, cy + fh * 0.3), (cx + fw * 0.36, cy + fh * 0.62)], 3), hx("7a5040"), 0.8, 2)
    my = cy + fh * 0.53
    _daub(img, "line", ([(cx - fw * 0.34, my + 3), (cx - fw * 0.1, my), (cx + fw * 0.2, my), (cx + fw * 0.32, my + 4)], 3),
          hx("5a2e28"), 1, 0.8)
    _daub(img, "line", ([(cx - fw * 0.22, my + 4), (cx + fw * 0.18, my + 4)], 2), hx("a8705c"), 0.6, 1.5)
    _daub(img, "ellipse", [cx - fw * 0.28, cy + fh * 0.7, cx + fw * 0.2, cy + fh * 0.84], hx("e8c4a4"), 0.5, 4)
    noise(img, (0, 0, W4 - 1, H4 - 1), 5, 54)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------------------------------------ HARRINGTON'S OFFICE

def paint_office(left=False, right=False, closet=False, secret=False):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    # panelled walls
    vgrad(img, (0, 0, W - 1, 196), hx("3a2618"), hx("2a1a10"))
    for x in range(0, W, 40):
        d.rectangle([x + 4, 110, x + 36, 186], outline=hx("1e1209"))
        d.line([(x + 5, 111), (x + 35, 111)], fill=hx("5a3c24"))
    d.rectangle([0, 100, W - 1, 104], fill=hx("5a3a22"))
    d.rectangle([0, 0, W - 1, 8], fill=hx("1e140c"))
    noise(img, (0, 0, W - 1, 196), 4, 51)
    vgrad(img, (0, 196, W - 1, H - 1), hx("3a1a1a"), hx("4a2222"))
    d.polygon([(90, 214), (390, 214), (420, 262), (60, 262)], fill=hx("4e2428"), outline=hx("7a5a2a"))
    d.polygon([(96, 218), (384, 218), (410, 258), (70, 258)], outline=hx("a07a46"))
    for x in range(114, 380, 32):
        d.polygon([(x, 236), (x + 7, 230), (x + 14, 236), (x + 7, 242)], outline=hx("805238"))
    noise(img, (0, 196, W - 1, H - 1), 5, 53)
    # window on the left: the fire escape and the city at night
    d.rectangle([24, 30, 112, 160], fill=hx("4a3220"))
    d.rectangle([30, 36, 106, 154], fill=hx("141a30"))
    rnd = random.Random(52)
    for _ in range(18):
        x, y = rnd.randint(32, 104), rnd.randint(90, 150)
        d.rectangle([x, y, x + 1, y + 2], fill=hx("c8a858"))
    for y in (100, 140):
        d.line([(30, y), (106, y)], fill=hx("0a0a10"), width=2)
    for x in range(30, 107, 6):
        d.line([(x, 128), (x, 140)], fill=hx("0a0a10"))
    d.rectangle([66, 36, 69, 154], fill=hx("4a3220"))
    d.rectangle([30, 92, 106, 95], fill=hx("4a3220"))
    d.rectangle([20, 160, 116, 166], fill=hx("5a3c26"))
    # Harrington senior's portrait in a heavy gilt frame, a little brass picture light above it
    d.rectangle([212, 16, 284, 102], fill=hx("6a4a1a"))
    d.rectangle([214, 18, 282, 100], fill=hx("b08a3a"))
    d.rectangle([217, 21, 279, 97], fill=hx("7a5a22"))
    img.paste(harrington_portrait(58, 72), (219, 23))
    d.line([(214, 18), (282, 18)], fill=hx("d8b860"))
    d.line([(214, 18), (214, 100)], fill=hx("d8b860"))
    d.rectangle([238, 10, 258, 13], fill=hx("8a7a3a"))
    d.line([(248, 13), (248, 16)], fill=hx("6a5a2a"))
    # filing cabinet
    d.rectangle([128, 120, 168, 200], fill=hx("4a4a44"), outline=hx("1a1a18"))
    for y in (128, 152, 176):
        d.rectangle([132, y, 164, y + 20], outline=hx("2a2a26"))
        d.rectangle([144, y + 8, 152, y + 10], fill=hx("a8a490"))
    # the desk: two pedestals, a drawer in each
    d.rectangle([182, 142, 318, 150], fill=hx("6a4426"), outline=hx("1e1209"))
    d.rectangle([186, 150, 230, 204], fill=hx("4e321c"), outline=hx("1e1209"))
    d.rectangle([270, 150, 314, 204], fill=hx("4e321c"), outline=hx("1e1209"))
    d.rectangle([230, 150, 270, 160], fill=hx("3a2614"))
    for (x0, opened) in ((190, left), (274, right)):
        if opened:
            d.rectangle([x0 - 4, 160, x0 + 40, 182], fill=hx("6a4628"), outline=hx("1e1209"))
            d.rectangle([x0 - 2, 156, x0 + 38, 162], fill=hx("2a1a0e"))
            d.rectangle([x0 + 2, 157, x0 + 34, 161], fill=hx("e0d8c0") if x0 == 190 else hx("f0ead8"))
            if x0 == 274:
                d.rectangle([x0 + 10, 157, x0 + 26, 160], fill=hx("c8a040"))
        else:
            d.rectangle([x0, 156, x0 + 36, 174], outline=hx("2a1a0c"))
            d.rectangle([x0 + 14, 164, x0 + 22, 166], fill=hx("c8a858"))
            if x0 == 274:
                d.rectangle([x0 + 17, 168, x0 + 19, 171], fill=hx("0a0604"))
        d.rectangle([x0, 180, x0 + 36, 198], outline=hx("2a1a0c"))
    # desk top clutter: blotter, inkwell, a dark lamp
    d.rectangle([236, 138, 268, 142], fill=hx("2a3a2a"))
    d.rectangle([240, 135, 263, 138], fill=hx("c0b090"))
    d.line([(244, 136), (260, 136)], fill=hx("5a5044"))
    d.ellipse([200, 136, 208, 142], fill=hx("16161a"))
    d.rectangle([294, 124, 296, 142], fill=hx("8a7a3a"))
    d.polygon([(286, 124), (304, 124), (300, 116), (290, 116)], fill=hx("2a4a2a"))
    # the closet (wardrobe), tall, on the right
    wx0, wx1, wy0, wy1 = 372, 456, 52, 204
    d.rectangle([wx0 - 4, wy0 - 6, wx1 + 4, wy0], fill=hx("4a2e18"))
    d.rectangle([wx0, wy0, wx1, wy1], fill=hx("3e2614"), outline=hx("140a04"))
    if closet:
        d.rectangle([wx0 + 4, wy0 + 4, wx1 - 4, wy1 - 10], fill=hx("120a06"))
        d.line([(wx0 + 6, wy0 + 16), (wx1 - 6, wy0 + 16)], fill=hx("8a8a80"))
        for i, c in enumerate(("2a2a30", "4a3a2a", "26262e")):
            cx = wx0 + 18 + i * 20
            d.polygon([(cx - 8, wy0 + 20), (cx + 8, wy0 + 20), (cx + 10, wy0 + 96), (cx - 10, wy0 + 96)], fill=hx(c))
            d.line([(cx, wy0 + 16), (cx, wy0 + 20)], fill=hx("8a8a80"))
        if secret:
            # the back panel slid aside: a hidden niche with the white mask and the black cloak
            d.rectangle([wx0 + 10, wy0 + 100, wx1 - 10, wy1 - 14], fill=hx("060302"))
            d.rectangle([wx1 - 18, wy0 + 100, wx1 - 8, wy1 - 14], fill=hx("5a3a20"))
            d.ellipse([wx0 + 22, wy0 + 104, wx0 + 40, wy0 + 126], fill=hx("ece8e0"))
            d.rectangle([wx0 + 26, wy0 + 112, wx0 + 29, wy0 + 114], fill=hx("060302"))
            d.rectangle([wx0 + 33, wy0 + 112, wx0 + 36, wy0 + 114], fill=hx("060302"))
            d.polygon([(wx0 + 44, wy0 + 104), (wx0 + 62, wy0 + 104), (wx0 + 66, wy1 - 16), (wx0 + 40, wy1 - 16)],
                      fill=hx("141218"))
        else:
            d.rectangle([wx0 + 10, wy0 + 100, wx1 - 10, wy1 - 14], fill=hx("2a1a0c"), outline=hx("140a04"))
            d.line([((wx0 + wx1) // 2, wy0 + 100), ((wx0 + wx1) // 2, wy1 - 14)], fill=hx("140a04"))
        # the doors swung open to either side
        d.polygon([(wx0, wy0), (wx0 - 14, wy0 + 6), (wx0 - 14, wy1 + 4), (wx0, wy1)], fill=hx("4a2e18"), outline=hx("140a04"))
        d.polygon([(wx1, wy0), (wx1 + 14, wy0 + 6), (wx1 + 14, wy1 + 4), (wx1, wy1)], fill=hx("4a2e18"), outline=hx("140a04"))
    else:
        mx = (wx0 + wx1) // 2
        d.line([(mx, wy0), (mx, wy1)], fill=hx("140a04"))
        for x0, x1 in ((wx0 + 6, mx - 6), (mx + 6, wx1 - 6)):
            d.rectangle([x0, wy0 + 10, x1, wy0 + 70], outline=hx("1e1208"))
            d.rectangle([x0, wy0 + 80, x1, wy1 - 12], outline=hx("1e1208"))
        d.rectangle([mx - 5, 128, mx - 3, 136], fill=hx("c8a858"))
        d.rectangle([mx + 3, 128, mx + 5, 136], fill=hx("c8a858"))
    # moonlight: everything cold, a blue shaft from the window
    img.paste(ImageChops.multiply(img, Image.new("RGB", img.size, (118, 128, 186))))
    light(img, "polygon", [(30, 36), (106, 36), (300, 262), (110, 262)], hx("5a70b0"), 0.35, 14)
    light(img, "ellipse", [268, 100, 326, 174], hx("d8a058"), 0.16, 10)
    light(img, "ellipse", [218, 12, 278, 74], hx("e0b868"), 0.12, 8)
    vignette(img, 0.6, (8, 8, 22), 40)
    return img


def build_office():
    base = paint_office()
    v = {"drawer_left": paint_office(left=True), "drawer_right": paint_office(right=True),
         "closet": paint_office(closet=True), "secret": paint_office(closet=True, secret=True)}
    blend = base
    for img in v.values():
        blend = Image.blend(blend, img, 0.4)
    pal = palette_of(blend, 124)
    px = pixelize(base, pal)
    save(px, "rooms", "harrington_office.png")
    overlay(v["drawer_left"], px, pal, (180, 150, 236, 206), "harrington_office_drawer_left")
    overlay(v["drawer_right"], px, pal, (264, 150, 320, 206), "harrington_office_drawer_right")
    overlay(v["closet"], px, pal, (350, 40, 476, 212), "harrington_office_closet")
    # the niche is drawn over the open closet, so it's cut against the open-closet state
    closet_px = pixelize(v["closet"], pal)
    overlay(v["secret"], closet_px, pal, (350, 40, 476, 212), "harrington_office_secret")
    return px


# ------------------------------------------------------------------------------------------------ DANIEL'S BEDROOM

# the couple were painted at the standing height of the other rooms and filled the bed; in bed they read smaller
BED_FIGURE_H = 62


def _bed_figures(sD, sW):
    """Daniel sitting up in bed reading, seen in profile, and his wife asleep on her side facing the room (head and
    shoulders only: the quilt covers the rest, top of the head towards the headboard). Returns RGBA crops, the hands'
    offset from Daniel's seat corner and the wife's crop."""
    from .figure import figure, pose
    from .sprites import DANIEL, ELEANOR
    hD = BED_FIGURE_H * sD
    ps = pose(90, legs={1: (86, 0, 0), -1: (84, 4, 0)}, arms={1: ("swing", 22, 4, 82), -1: ("swing", 28, 4, 78)},
              lean=-7.0, nod=0.01)
    a = figure(dict(DANIEL, h=hD), ps, int(hD * 1.2), int(hD * 1.3))
    a.putalpha(a.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    a = a.crop(a.getbbox())
    hand = (0.31 * hD, -0.255 * hD)
    hW = BED_FIGURE_H * sW
    wife = dict(ELEANOR, h=hW, hair="2e1c14", torso="c4b0cc", sleeves="ecc4a2", neckline=0.262, asleep=True,
                lips="b0645a", decals=[])
    wife.pop("coat", None)
    b = figure(wife, pose(0, arms={1: ("swing", 2, 4, 6), -1: ("swing", 2, 4, 6)}), int(hW * 0.6), int(hW * 1.1))
    b.putalpha(b.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
    bb = b.getbbox()
    b = b.crop((bb[0], bb[1], bb[2], int(bb[1] + 0.3 * hW))).rotate(90, expand=True)
    return a, hand, b


def paint_bedroom():
    """Present day, past one in the morning. A double bed side-on, headboard against the left wall: Daniel sits up on
    the far side reading Micah's journal by his lamp; his wife sleeps on the near side, turned towards the room.
    Returns the picture, Daniel's head and the wife's head (speech anchors)."""
    import math
    import numpy as np
    from .furniture import Room3D

    class Zoomed(Room3D):
        """The camera moved in: world units stay the back-wall pixels of the other rooms, the picture is K times bigger
        about the vanishing point's column."""
        K = 1.3

        def s(self, z):
            return Room3D.s(self, z * self.K) * self.K

        def P(self, x, y, z):
            s = Room3D.s(self, z * self.K)
            return self.vx + (x - self.vx) * self.K * s, self.vy + (self.floor - self.vy) * s - y * self.K * s

    FL = 150  # back-wall floor row
    R = Zoomed(FL, 260, 24, 380)
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    WX = 176  # the left wall plane
    ZMAX = 205
    # ---- room: oak floor, painted walls, skirting ----
    floor_boards(img, FL, H, (260, 24), 16, hx("9a7250"), hx("8a6444"), hx("5e4230"), seed=3)
    vgrad(img, (0, 0, W - 1, FL), hx("b4ac9c"), hx("c2baaa"))
    noise(img, (0, 0, W - 1, FL), 3, 5)
    R.quad(img, [(WX, 0, 0), (WX, 200, 0), (WX, 200, ZMAX), (WX, 0, ZMAX)], hx("a49c8c"))
    R.quad(img, [(WX, 0, 0), (W + 60, 0, 0), (W + 60, 4, 0), (WX, 4, 0)], hx("ece6d8"))
    R.quad(img, [(WX, 0, 0), (WX, 4, 0), (WX, 4, ZMAX), (WX, 0, ZMAX)], hx("dcd6c8"))
    d.line([R.P(WX, 0, 0), R.P(WX, 200, 0)], fill=hx("948c7c"))
    # ---- the window on the back wall: blind half down, the night city behind ----
    wx0, wx1, wy0, wy1 = 290, 362, 54, 132
    d.rectangle([wx0 - 3, FL - wy1 - 3, wx1 + 3, FL - wy0 + 3], fill=hx("f0ece2"))
    d.rectangle([wx0, FL - wy1, wx1, FL - wy0], fill=hx("141a2c"))
    rnd = random.Random(4)
    d.polygon([(wx0, FL - wy0), (wx0, FL - wy0 - 26), (wx0 + 12, FL - wy0 - 26), (wx0 + 12, FL - wy0 - 40),
               (wx0 + 26, FL - wy0 - 40), (wx0 + 26, FL - wy0 - 22), (wx0 + 40, FL - wy0 - 22),
               (wx0 + 40, FL - wy0 - 46), (wx0 + 52, FL - wy0 - 46), (wx0 + 52, FL - wy0 - 30), (wx1, FL - wy0 - 30),
               (wx1, FL - wy0)], fill=hx("0c0f18"))
    for _ in range(30):
        x, y = rnd.randint(wx0 + 2, wx1 - 3), rnd.randint(FL - wy0 - 44, FL - wy0 - 4)
        if img.getpixel((x, y)) == hx("0c0f18"):
            d.rectangle([x, y, x + 1, y], fill=rnd.choice([hx("f0c870"), hx("e8d8a0"), hx("a0b0c8")]))
    d.rectangle([wx0, FL - wy1, wx1, FL - wy1 + 28], fill=hx("e4dcc8"))
    for y in range(FL - wy1 + 3, FL - wy1 + 28, 3):
        d.line([(wx0, y), (wx1, y)], fill=hx("c8c0ac"))
    d.line([((wx0 + wx1) // 2, FL - wy1 + 28), ((wx0 + wx1) // 2, FL - wy0)], fill=hx("f0ece2"), width=2)
    d.rectangle([wx0 - 6, FL - wy0 + 3, wx1 + 6, FL - wy0 + 6], fill=hx("f0ece2"))
    for cx0 in (wx0 - 18, wx1 + 4):  # linen curtains
        d.rectangle([cx0, FL - wy1 - 8, cx0 + 14, FL - wy0 + 20], fill=hx("c8b898"))
        for x in range(cx0 + 3, cx0 + 14, 4):
            d.line([(x, FL - wy1 - 8), (x, FL - wy0 + 20)], fill=hx("a89a7c"))
    d.line([(wx0 - 22, FL - wy1 - 9), (wx1 + 22, FL - wy1 - 9)], fill=hx("3a3430"), width=2)
    # ---- a chest of drawers on the back wall: a plant, two photos; a print above it ----
    R.box(img, 368, 418, 0, 30, 0, 16, hx("6a4a32"), top=hx("84603f"), side=hx("4a3222"))
    for y0 in (3, 12, 21):
        R.quad(img, [(370, y0, 16), (416, y0, 16), (416, y0 + 7.5, 16), (370, y0 + 7.5, 16)], None, hx("3a2618"))
        px_, py_ = R.P(393, y0 + 4, 16)
        d.rectangle([px_ - 4, py_, px_ + 4, py_ + 1], fill=hx("c8b080"))
    R.box(img, 372, 379, 30, 35, 4, 10, hx("b06a48"), top=hx("c47c58"))
    pc = R.P(375.5, 35, 7)
    for ang, ln in ((-60, 14), (-90, 18), (-120, 13), (-40, 10), (-145, 11)):
        ex, ey = pc[0] + ln * math.cos(math.radians(ang)), pc[1] + ln * math.sin(math.radians(ang))
        d.line([pc, (ex, ey)], fill=hx("3a6a3a"), width=2)
        d.ellipse([ex - 3, ey - 2, ex + 3, ey + 2], fill=hx("4a8248"))
    for fx, fh_ in ((392, 9), (404, 7)):
        R.box(img, fx, fx + 7, 30, 30 + fh_, 7, 8, hx("2a2a2a"))
        a0, a1 = R.P(fx + 1, 30 + fh_ - 1, 8), R.P(fx + 6, 31, 8)
        d.rectangle([a0[0], a0[1], a1[0], a1[1]], fill=hx("a8b4b0"))
    d.rectangle([398, 26, 452, 80], fill=hx("2a2620"))
    d.rectangle([401, 29, 449, 77], fill=hx("f0ece2"))
    d.rectangle([406, 34, 444, 72], fill=hx("6a8aa0"))
    d.polygon([(406, 72), (415, 54), (423, 62), (432, 46), (444, 60), (444, 72)], fill=hx("3a5a6a"))
    d.ellipse([430, 37, 437, 44], fill=hx("e8d8b0"))
    # ---- a framed print on the left wall above the headboard ----
    R.quad(img, [(WX, 54, 40), (WX, 82, 40), (WX, 82, 76), (WX, 54, 76)], hx("2a2620"))
    R.quad(img, [(WX, 56, 42), (WX, 80, 42), (WX, 80, 74), (WX, 56, 74)], hx("f0ece2"))
    R.quad(img, [(WX, 59, 46), (WX, 77, 46), (WX, 77, 70), (WX, 59, 70)], hx("c88a5a"))
    R.quad(img, [(WX, 59, 46), (WX, 66, 46), (WX, 70, 58), (WX, 65, 70), (WX, 59, 70)], hx("8a4a3a"))
    # ---- rug ----
    R.quad(img, [(196, 0, 108), (296, 0, 108), (296, 0, 150), (196, 0, 150)], hx("7a3a34"))
    R.quad(img, [(200, 0.05, 111), (292, 0.05, 111), (292, 0.05, 147), (200, 0.05, 147)], None, hx("c8a888"))

    # ---- Daniel's nightstand, in the far corner ----
    wood, wood_d, wood_l = hx("6a4630"), hx("46301e"), hx("86603f")
    R.box(img, WX, WX + 22, 0, 26, 2, 22, wood, top=wood_l, side=wood_d)
    R.quad(img, [(WX + 2, 15, 22), (WX + 20, 15, 22), (WX + 20, 23, 22), (WX + 2, 23, 22)], None, hx("2a1c10"))
    R.box(img, WX + 12, WX + 19, 26, 29, 10, 13, hx("161616"), top=hx("2a2a2a"))  # the alarm clock
    clk = R.P(WX + 15.5, 27.5, 13)
    # his lamp (lit): painted bright so the night grade leaves it glowing warm
    lamp = R.P(WX + 7, 26, 8)
    d.rectangle([lamp[0] - 1, lamp[1] - 52, lamp[0] + 1, lamp[1]], fill=hx("b0a080"))
    d.ellipse([lamp[0] - 5, lamp[1] - 2, lamp[0] + 5, lamp[1] + 2], fill=hx("8a7a5a"))
    light(img, "ellipse", [lamp[0] - 26, lamp[1] - 80, lamp[0] + 26, lamp[1] - 30], hx("fff4d0"), 0.5, 8)
    d.polygon([(lamp[0] - 10, lamp[1] - 50), (lamp[0] + 10, lamp[1] - 50), (lamp[0] + 8, lamp[1] - 64),
               (lamp[0] - 8, lamp[1] - 64)], fill=hx("fffff0"))
    d.line([(lamp[0] - 10, lamp[1] - 50), (lamp[0] + 10, lamp[1] - 50)], fill=hx("f0d090"))
    # ---- the bed: X0 headboard .. X1 foot, Z0 far side .. Z1 near side ----
    X0, X1, Z0, Z1, TOP_ = WX, WX + 92, 26, 98, 24
    shadow(img, "polygon", [R.P(X0, 0, Z0 - 2), R.P(X1 + 3, 0, Z0 - 2), R.P(X1 + 5, 0, Z1 + 3), R.P(X0, 0, Z1 + 3)],
           0.55, 3)
    R.box(img, X0, X0 + 4, 0, 50, Z0 - 2, Z1 + 2, hx("6a7a8a"), top=hx("808f9e"), side=hx("56646f"))
    for z in range(Z0 + 4, Z1, 12):
        R.line(img, (X0 + 4, 12, z), (X0 + 4, 47, z), hx("56646f"))
    R.box(img, X0 + 4, X1, 3, 11, Z0, Z1, wood, top=wood_l, side=wood_d)
    for x in (X0 + 6, X1 - 3):
        R.line(img, (x, 0, Z1 - 1), (x, 3, Z1 - 1), wood_d, 2)
    R.box(img, X0 + 5, X1 - 1, 11, TOP_, Z0 + 1, Z1 - 1, hx("ece8e0"), top=hx("f6f2ea"), side=hx("cfc9bd"))

    def pillow(x0, x1, z0, z1, y0, y1, lean=0.0):
        """A soft pillow: the hull of a rounded rectangle at its base and its crown, the crown shaded lighter."""
        cx_, cz_, rx_, rz_ = (x0 + x1) / 2, (z0 + z1) / 2, (x1 - x0) / 2, (z1 - z0) / 2
        base, crown = [], []
        for i in range(36):
            t = i / 36 * 2 * math.pi
            c, s = math.cos(t), math.sin(t)
            ex, ez = cx_ + rx_ * math.copysign(abs(c) ** 0.4, c), cz_ + rz_ * math.copysign(abs(s) ** 0.4, s)
            base.append(R.P(ex, y0, ez))
            crown.append(R.P(ex + lean, y1, ez))
        m = Image.new("L", img.size, 0)
        md = ImageDraw.Draw(m)
        md.polygon(base, fill=255)
        md.polygon(crown, fill=255)
        for p, q in zip(base, crown):
            md.line([p, q], fill=255, width=2)
        img.paste(hx("cfc9be"), mask=m)
        d.polygon(crown, fill=hx("e6e2d8"))
        cc = R.P(cx_ + lean, y1, cz_)
        d.polygon([(cc[0] + (p[0] - cc[0]) * 0.82, cc[1] + (p[1] - cc[1]) * 0.75) for p in crown], fill=hx("f2eee6"))

    pillow(X0 + 5, X0 + 19, Z0 + 3, Z0 + 31, TOP_, 40, lean=1.0)  # Daniel's, propped up against the headboard
    pillow(X0 + 5, X0 + 25, Z0 + 37, Z1 - 4, TOP_, 29)            # hers, flat

    # ---- the people ----
    zD, zW = Z0 + 17, Z0 + 52
    dan, hand, wife = _bed_figures(R.s(zD), R.s(zW))
    seat = R.P(X0 + 13, TOP_ - 1, zD)
    img.paste(dan.convert("RGB"), (int(seat[0]), int(seat[1] - dan.height)), dan)
    dan_head = (int(seat[0] + dan.width * 0.32), int(seat[1] - dan.height))
    hp = R.P(X0 + 7, TOP_ + 7, zW)  # where the crown of her head rests on the pillow
    wpos = (int(hp[0]), int(hp[1] - wife.height * 0.55))
    img.paste(wife.convert("RGB"), wpos, wife)
    wife_head = (int(hp[0] + wife.width * 0.3), wpos[1])

    # ---- the quilt: a height field over the two of them, its top edge folded back under her chin ----
    QX0, QX1 = X0 + 23, X1 + 1.5

    def hgt(x, z):
        h = TOP_ + 1.5
        t = min(max((x - (X0 + 20)) / (X1 - X0 - 24), 0), 1)
        h += (3.6 - 1.2 * t) * math.exp(-((z - zD) / 7.5) ** 2)                      # his legs
        h += 3.5 * math.exp(-((x - (X1 - 9)) / 4.0) ** 2 - ((z - zD) / 6.0) ** 2)    # toes
        h += 6.0 * math.exp(-((x - (X0 + 27)) / 7.0) ** 2 - ((z - zW) / 10.0) ** 2)  # her shoulder
        h += 7.5 * math.exp(-((x - (X0 + 54)) / 10.0) ** 2 - ((z - zW) / 11.0) ** 2)  # hip
        h += 4.0 * math.exp(-((x - (X0 + 76)) / 8.0) ** 2 - ((z - zW - 7) / 9.0) ** 2)  # drawn-up knees
        h += 2.5 * math.exp(-((x - (X1 - 10)) / 7.0) ** 2 - ((z - zW - 3) / 8.0) ** 2)  # feet
        return h + 0.35 * math.sin(x * 0.3 + z * 0.2)

    q_dark, q_light = np.array(hx("34506c")), np.array(hx("7c9ab4"))
    L = np.array([-0.45, 0.8, 0.4])
    L /= np.linalg.norm(L)
    step = 1.5
    xs = np.arange(QX0, QX1 + 0.01, step)
    zs = np.arange(Z0 - 1, Z1 + 1.01, step)
    Hm = np.array([[hgt(x, z) for x in xs] for z in zs])

    def qcol(n, seam=False):
        n = n / np.linalg.norm(n)
        k = float(np.clip(n @ L, 0, 1)) ** 1.4
        c = q_dark + (q_light - q_dark) * (0.25 + 0.75 * k)
        return tuple(int(v * (0.9 if seam else 1.0)) for v in c)

    for j in range(len(zs) - 1):
        for i in range(len(xs) - 1):
            x, z = xs[i], zs[j]
            n = np.array([-(Hm[j, i + 1] - Hm[j, i]) / step, 1.0, -(Hm[j + 1, i] - Hm[j, i]) / step])
            seam = (x - QX0) % 14 < step * 0.99 or (z - Z0) % 14 < step * 0.99
            R.quad(img, [(x, Hm[j, i], z), (x + step, Hm[j, i + 1], z), (x + step, Hm[j + 1, i + 1], z + step),
                         (x, Hm[j + 1, i], z + step)], qcol(n, seam))
    # the folded-back band of sheet along the top edge
    for j in range(len(zs) - 1):
        z = zs[j]
        R.quad(img, [(QX0 - 2.5, Hm[j, 0] + 0.5, z), (QX0 + 2, Hm[j, 1] + 0.5, z), (QX0 + 2, Hm[j + 1, 1] + 0.5, z + step),
                     (QX0 - 2.5, Hm[j + 1, 0] + 0.5, z + step)], hx("f0ece4"))
    R.line(img, (QX0 + 2, Hm[0, 1] + 0.5, zs[0]), (QX0 + 2, Hm[-1, 1] + 0.5, zs[-1]), hx("c0bab0"))
    # the drape over the near side and the foot, in soft vertical folds
    for i in range(len(xs) - 1):
        x = xs[i]
        f = 0.5 + 0.5 * math.sin(x * 0.5)
        col = tuple(int(v) for v in q_dark + (q_light - q_dark) * (0.18 + 0.3 * f))
        R.quad(img, [(x, Hm[-1, i], Z1 + 1), (x + step, Hm[-1, i + 1], Z1 + 1), (x + step, 7, Z1 + 2 + f),
                     (x, 7, Z1 + 2 + f)], col)
    for j in range(len(zs) - 1):
        z = zs[j]
        f = 0.5 + 0.5 * math.sin(z * 0.45)
        col = tuple(int(v) for v in q_dark + (q_light - q_dark) * (0.3 + 0.3 * f))
        R.quad(img, [(QX1, Hm[j, -1], z), (QX1, Hm[j + 1, -1], z + step), (QX1 + 1 + f, 7, z + step),
                     (QX1 + 1 + f, 7, z)], col)

    # ---- the journal in Daniel's hands: open, its brown leather back towards us ----
    bx, by = seat[0] + hand[0], seat[1] + hand[1]
    k = R.s(zD) / 1.5
    bk = lambda pts: [(bx + px * k, by + py * k) for px, py in pts]
    d.polygon(bk([(-3, 3), (1, 4), (7, -12), (3, -13)]), fill=hx("f2ead6"))
    d.polygon(bk([(1, 4), (5, 4), (11, -11), (7, -12)]), fill=hx("6a3a22"))
    d.line(bk([(1, 4), (7, -12)]), fill=hx("3a2014"))
    d.ellipse(bk([(-1, -2), (5, 4)]), fill=hx("e0b090"))

    # ---- night grade: cold everywhere, warm in a pool around Daniel's lamp ----
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot((xx - lamp[0]) / 1.25, (yy - lamp[1]) * 1.1)
    w = np.exp(-(dist / 120.0) ** 1.6)[..., None]
    night, warm = np.array([0.36, 0.40, 0.62]), np.array([1.05, 0.84, 0.6])
    arr = np.asarray(img, dtype=np.float32) * (night + (warm - night) * w)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    for i in range(3):  # 1:47 as three red ticks
        d.point((clk[0] - 2 + i * 2, clk[1]), fill=hx("ff4a30"))
    vignette(img, 0.5, (8, 8, 24), 40)
    return img, dan_head, wife_head


def build_bedroom():
    img, dan, wife = paint_bedroom()
    px = pixelize(img, palette_of(img, 112))
    save(px, "rooms", "bedroom.png")
    print("bedroom: Daniel's head", dan, "wife's head", wife)
    return px

def build():
    build_rose()
    build_road()
    build_office()
    build_bedroom()
