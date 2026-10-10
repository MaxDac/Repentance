"""Location-select screen: a creased, yellowed 1927 street map of Chicago lying on a dark desk under a lamp.

Lake Michigan to the east, the river's Y through the middle, the street grid, parks, a compass rose and a title
cartouche. Three location pins are painted into map.png; the fourth (THE STARLIGHT) is exported separately as a
cropped transparent overlay (map_club.png) that lines up pixel-exactly when pasted at CLUB_BOX's top-left."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math
import random
import numpy as np
from .common import W, FULL_H, FONT, hx, mix, mul, light, shadow, vignette, pixelize, palette_of, save, text

PAPER = (8, 7, 471, 262)
PAPER_C = hx("d8c89c")
PAPER_D = hx("b8a272")
BLOCK = hx("cbb98a")
STREET = hx("a08a62")
AVENUE = hx("7a6444")
INK = hx("3a2a1c")
WATER = hx("7f93a0")
WATER_D = hx("4c5e6c")
WATER_L = hx("a4b4bc")
PARK = hx("a4ac78")
PARK_D = hx("7c8858")
PIN = hx("b8242a")
PIN_D = hx("5a0e12")
PIN_L = hx("f07a6a")
PLATE = hx("ece0bc")
PLATE_D = hx("4a3420")

FORK = (232, 112)
MAIN = [FORK, (262, 110), (300, 111), (340, 109), (372, 108), (392, 107)]
NORTH = [FORK, (222, 96), (214, 78), (204, 58), (196, 38), (184, 20), (176, 0)]
SOUTH = [FORK, (236, 128), (240, 146), (236, 166), (222, 184), (198, 200), (164, 218), (130, 238), (96, 262)]

# Marker pin positions (head centre) and labels; plates hang below the pins.
MARKERS = {
    "library": ((322, 52), "LIBRARY"),
    "cathedral": ((118, 116), "CATHEDRAL"),
    "office": ((292, 150), "OFFICE"),
}
CLUB = ((312, 206), "THE STARLIGHT")


def shore_x(y):
    """Lake Michigan shoreline (land to the west)."""
    return int(378 + 6 * math.sin(y / 37.0) + 3 * math.sin(y / 11.0 + 1.3) + (y - 135) * 0.05)


def desk(img):
    a = np.zeros((FULL_H, W, 3), np.float32)
    ys, xs = np.mgrid[0:FULL_H, 0:W]
    grain = np.sin(ys * 0.9 + np.sin(xs * 0.03) * 4.0) * 0.5 + np.sin(ys * 2.3 + xs * 0.01) * 0.25
    base = np.array(hx("3a2216"), np.float32)
    dark = np.array(hx("1c0f09"), np.float32)
    t = (grain + 0.75) / 1.5
    a[:] = base * t[..., None] + dark * (1 - t[..., None])
    img.paste(Image.fromarray(a.clip(0, 255).astype(np.uint8)))


def paper_mask():
    rnd = random.Random(11)
    x0, y0, x1, y1 = PAPER
    pts = []
    for x in range(x0, x1, 6):
        pts.append((x, y0 + rnd.randint(0, 1)))
    for y in range(y0, y1, 6):
        pts.append((x1 - rnd.randint(0, 1), y))
    for x in range(x1, x0, -6):
        pts.append((x, y1 - rnd.randint(0, 1)))
    for y in range(y1, y0, -6):
        pts.append((x0 + rnd.randint(0, 1), y))
    m = Image.new("L", (W, FULL_H), 0)
    d = ImageDraw.Draw(m)
    d.polygon(pts, fill=255)
    # a dog-eared bottom-right corner
    d.polygon([(x1 - 9, y1 + 1), (x1 + 1, y1 + 1), (x1 + 1, y1 - 9)], fill=0)
    return m


def paper(img):
    m = paper_mask()
    shadow(img, "rect", [PAPER[0] + 3, PAPER[1] + 4, PAPER[2] + 4, PAPER[3] + 4], k=0.8, blur=3)
    rng = np.random.default_rng(3)
    ys, xs = np.mgrid[0:FULL_H, 0:W]
    x0, y0, x1, y1 = PAPER
    edge = np.minimum.reduce([xs - x0, x1 - xs, ys - y0, y1 - ys]).astype(np.float32)
    age = np.clip(1 - edge / 26.0, 0, 1) ** 2
    blot = np.array(Image.fromarray((rng.random((FULL_H // 8 + 1, W // 8 + 1)) * 255).astype(np.uint8))
                    .resize((W, FULL_H), Image.Resampling.BICUBIC), np.float32) / 255.0
    t = np.clip(age * 0.8 + (blot - 0.5) * 0.35, 0, 1)
    pc = np.array(PAPER_C, np.float32)
    pd = np.array(PAPER_D, np.float32)
    col = pc * (1 - t[..., None]) + pd * t[..., None]
    col += rng.normal(0, 3.0, (FULL_H, W, 1))
    sheet = Image.fromarray(col.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(sheet)
    d.polygon([(x1 - 9, y1 - 9), (x1 - 9, y1), (x1, y1 - 9)], fill=mul(PAPER_D, 0.85))
    d.line([(x1 - 9, y1), (x1, y1 - 9)], fill=mul(PAPER_D, 0.7))
    img.paste(sheet, (0, 0), m)
    return m


def land_blocks(img, m):
    """Built-up blocks, the street grid and a few diagonal avenues."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = PAPER
    gx0, gy0 = x0 + 4, y0 + 4
    for y in range(gy0, y1 - 4, 8):
        for x in range(gx0, x1 - 4, 8):
            if x + 6 < shore_x(y + 3) - 2:
                d.rectangle([x + 1, y + 1, x + 6, y + 6], fill=BLOCK)
    for y in range(gy0, y1 - 3, 8):
        d.line([(x0 + 3, y), (shore_x(y) - 1, y)], fill=AVENUE if (y - gy0) % 32 == 0 else STREET)
    for x in range(gx0, 400, 8):
        col = AVENUE if (x - gx0) % 32 == 0 else STREET
        for y in range(y0 + 3, y1 - 3):
            if x < shore_x(y) - 1:
                d.point((x, y), fill=col)
    for a, b in [((228, 104), (40, 12)), ((236, 122), (40, 214)), ((240, 150), (70, 258)), ((232, 112), (60, 112))]:
        d.line([a, b], fill=AVENUE, width=1)


def parks(img):
    d = ImageDraw.Draw(img)
    rnd = random.Random(4)

    def park(poly):
        d.polygon(poly, fill=PARK, outline=PARK_D)
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        for _ in range(int((max(xs) - min(xs)) * (max(ys) - min(ys)) / 14)):
            x, y = rnd.randint(min(xs) + 1, max(xs) - 1), rnd.randint(min(ys) + 1, max(ys) - 1)
            if img.getpixel((x, y))[:3] == PARK:
                d.point((x, y), fill=PARK_D)

    # Lincoln Park along the north lakefront, Grant Park by the Loop, Jackson Park down south
    park([(shore_x(10) - 26, 10), (shore_x(10) - 1, 10), (shore_x(70) - 1, 70), (shore_x(70) - 16, 70)])
    park([(shore_x(118) - 14, 118), (shore_x(118) - 1, 118), (shore_x(170) - 1, 170), (shore_x(170) - 14, 170)])
    park([(shore_x(236) - 30, 236), (shore_x(236) - 1, 236), (shore_x(258) - 1, 258), (shore_x(258) - 30, 258)])
    # Humboldt, Garfield and Douglas parks on the West Side
    park([(36, 68), (68, 68), (68, 92), (36, 92)])
    park([(28, 150), (60, 150), (60, 170), (28, 170)])
    park([(76, 182), (100, 182), (100, 200), (76, 200)])


def lake(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = PAPER
    pts = [(shore_x(y), y) for y in range(y0, y1 + 1)] + [(x1 + 2, y1 + 2), (x1 + 2, y0 - 2)]
    d.polygon(pts, fill=WATER)
    for y in range(y0, y1 + 1):
        d.point((shore_x(y), y), fill=WATER_D)
        d.point((shore_x(y) + 1, y), fill=WATER_D)
    rnd = random.Random(9)
    for y in range(y0 + 4, y1 - 2, 5):
        sx = shore_x(y) + 4
        for k in range(4):
            off = 3 + k * 4
            xa = sx + off + (y // 5 % 2) * 2
            d.line([(xa, y), (xa + 1, y)], fill=mix(WATER, WATER_D, 0.45 - k * 0.1))
        for _ in range(3):
            xa = rnd.randint(sx + 20, x1 - 6)
            d.line([(xa, y), (xa + 2, y)], fill=WATER_L if rnd.random() < 0.3 else mix(WATER, WATER_D, 0.3))
    # harbour breakwater and the Navy Pier
    d.rectangle([shore_x(100), 100, shore_x(100) + 26, 102], fill=PAPER_D, outline=INK)


def river(img):
    d = ImageDraw.Draw(img)
    for path, wid in ((MAIN, 4), (NORTH, 3), (SOUTH, 3)):
        d.line(path, fill=WATER_D, width=wid + 2, joint="curve")
    for path, wid in ((MAIN, 4), (NORTH, 3), (SOUTH, 3)):
        d.line(path, fill=WATER, width=wid, joint="curve")
    d.ellipse([FORK[0] - 3, FORK[1] - 3, FORK[0] + 3, FORK[1] + 3], fill=WATER)
    # bridges across the main stem
    for x in range(244, 372, 16):
        d.line([(x, 106), (x, 115)], fill=AVENUE)


def compass(img, cx, cy, r):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK)
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], outline=mix(INK, WATER, 0.5))
    for i in range(8):
        a = i * math.pi / 4 - math.pi / 2
        L = r + 3 if i % 2 == 0 else r - 4
        tip = (cx + L * math.cos(a), cy + L * math.sin(a))
        s1 = (cx + 3 * math.cos(a + math.pi / 2), cy + 3 * math.sin(a + math.pi / 2))
        s2 = (cx + 3 * math.cos(a - math.pi / 2), cy + 3 * math.sin(a - math.pi / 2))
        light_c = PLATE if i % 2 == 0 else PAPER_D
        d.polygon([(cx, cy), s1, tip], fill=light_c, outline=INK)
        d.polygon([(cx, cy), s2, tip], fill=INK, outline=INK)
    d.polygon([(cx, cy - r - 3), (cx - 3, cy), (cx, cy)], fill=PIN)
    text(img, (cx, cy - r - 9), "N", INK, size=8)


def cartouche(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 20, 16, 146, 54
    shadow(img, "rect", [x0 + 2, y0 + 2, x1 + 2, y1 + 2], k=0.35, blur=1)
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=PLATE, outline=INK)
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=mix(INK, PLATE, 0.4))
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=PLATE, outline=INK)
        d.point((cx, cy), fill=PIN)
    text(img, ((x0 + x1) // 2, y0 + 15), "CHICAGO", INK, size=16)
    d.line([(x0 + 14, y0 + 26), (x0 + 42, y0 + 26)], fill=INK)
    d.line([(x1 - 42, y0 + 26), (x1 - 14, y0 + 26)], fill=INK)
    text(img, ((x0 + x1) // 2, y0 + 27), "1927", PIN_D, size=8)
    text(img, ((x0 + x1) // 2, y1 + 9), "STREET GUIDE", mix(INK, PAPER_D, 0.35), size=8)


def labels(img):
    faint = mix(INK, PAPER_C, 0.45)
    text(img, (424, 64), "LAKE", mix(WATER_D, INK, 0.3), size=8)
    text(img, (424, 74), "MICHIGAN", mix(WATER_D, INK, 0.3), size=8)
    text(img, (196, 140), "LOOP", faint, size=8) if False else None
    text(img, (60, 128), "WEST SIDE", faint, size=8)
    text(img, (262, 28), "NORTH SIDE", faint, size=8)
    text(img, (150, 252), "SOUTH SIDE", faint, size=8)


def creases(img):
    """Fold lines: a darker valley with a highlit ridge beside it."""
    x0, y0, x1, y1 = PAPER
    for x in (124, 240, 356):
        shadow(img, "rect", [x, y0 + 1, x, y1 - 1], k=0.22, blur=0)
        light(img, "rect", [x + 1, y0 + 1, x + 1, y1 - 1], hx("fff4d0"), k=0.18, blur=0)
    y = 135
    shadow(img, "rect", [x0 + 1, y, x1 - 1, y], k=0.22, blur=0)
    light(img, "rect", [x0 + 1, y + 1, x1 - 1, y + 1], hx("fff4d0"), k=0.18, blur=0)
    # coffee ring stain
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([60, 196, 96, 228], outline=70, width=2)
    d.ellipse([64, 200, 92, 224], fill=18)
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    stain = Image.new("RGB", img.size, hx("8a5a2a"))
    from PIL import ImageChops
    img.paste(Image.composite(ImageChops.multiply(img, stain), img, m))


def pencil(img):
    d = ImageDraw.Draw(img)
    a, b = (402, 266), (468, 236)
    d.line([(a[0] + 2, a[1] + 3), (b[0] + 2, b[1] + 3)], fill=hx("140a06"), width=4)
    d.line([a, b], fill=hx("c8901c"), width=4)
    d.line([(a[0], a[1] - 1), (b[0], b[1] - 1)], fill=hx("e8b840"), width=1)
    d.line([(a[0], a[1] + 1), (b[0], b[1] + 1)], fill=hx("8a5a10"), width=1)
    d.polygon([(b[0] - 1, b[1] - 2), (b[0] + 1, b[1] + 2), (b[0] + 9, b[1] - 4)], fill=hx("e0c8a0"))
    d.point((b[0] + 8, b[1] - 4), fill=hx("2a2a2a"))
    d.point((b[0] + 7, b[1] - 3), fill=hx("2a2a2a"))


def marker_box(pos, label):
    """Screen-space (x0, y0, x1, y1) bounds of a marker: pin head, needle shadow and label plate."""
    font = ImageFont.truetype(FONT, 8)
    tw = int(font.getlength(label))
    cx, cy = pos
    pw = tw + 8
    return (cx - pw // 2 - 1, cy - 5, cx - pw // 2 + pw + 2, cy + 23)


def marker(img, pos, label):
    font = ImageFont.truetype(FONT, 8)
    tw = int(font.getlength(label))
    cx, cy = pos
    pw = tw + 8
    px0, py0 = cx - pw // 2, cy + 9
    px1, py1 = px0 + pw, py0 + 11
    shadow(img, "rect", [px0 + 1, py0 + 1, px1 + 2, py1 + 2], k=0.55, blur=0)
    d = ImageDraw.Draw(img)
    d.line([(cx, cy + 6), (cx, py0)], fill=INK)
    d.rectangle([px0, py0, px1, py1], fill=PLATE, outline=PLATE_D)
    d.line([(px0 + 1, py1 - 1), (px1 - 1, py1 - 1)], fill=mix(PLATE, PLATE_D, 0.35))
    text(img, ((px0 + px1) // 2 + 1, (py0 + py1) // 2 + 1), label, INK, size=8)
    # pin: needle, cast shadow, glossy red head
    shadow(img, "ellipse", [cx - 1, cy - 1, cx + 6, cy + 6], k=0.5, blur=0)
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=PIN_D)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=PIN)
    d.rectangle([cx - 2, cy - 2, cx - 1, cy - 1], fill=PIN_L)


def lighting(img):
    light(img, "ellipse", [70, -10, 430, 250], hx("ffcf80"), k=0.22, blur=40)
    shadow(img, "ellipse", [-60, -60, 540, 330], k=0.0, blur=1)
    vignette(img, k=0.7, tint=(60, 42, 34), blur=50)


def paint_base():
    img = Image.new("RGB", (W, FULL_H))
    desk(img)
    paper(img)
    land_blocks(img, None)
    parks(img)
    lake(img)
    river(img)
    labels(img)
    cartouche(img)
    compass(img, 428, 182, 14)
    creases(img)
    return img


def build():
    base = paint_base()
    for pos, label in MARKERS.values():
        marker(base, pos, label)
    with_club = base.copy()
    marker(with_club, *CLUB)
    for im in (base, with_club):
        pencil(im)
        lighting(im)
    pal = palette_of(with_club, 120) + [PIN, PIN_D, PIN_L, mul(PIN, 0.8), mul(PIN, 0.65), mul(PIN_L, 0.8), PLATE, mul(PLATE, 0.85)]
    a = pixelize(base, pal)
    b = pixelize(with_club, pal)
    save(a, "rooms", "map.png")
    box = marker_box(*CLUB)
    diff = np.any(np.asarray(a.crop(box)) != np.asarray(b.crop(box)), axis=2)
    for bg in ((0, 0, 0), (255, 255, 255)):
        probe = Image.new("RGB", (W, FULL_H), bg)
        marker(probe, *CLUB)
        diff |= np.any(np.asarray(probe.crop(box)) != np.array(bg, np.uint8), axis=2)
    ys, xs = np.nonzero(diff)
    tight = (box[0] + int(xs.min()), box[1] + int(ys.min()), box[0] + int(xs.max()) + 1, box[1] + int(ys.max()) + 1)
    crop = b.crop(tight).convert("RGBA")
    alpha = Image.fromarray((diff[tight[1] - box[1]:tight[3] - box[1], tight[0] - box[0]:tight[2] - box[0]]
                             * 255).astype(np.uint8))
    crop.putalpha(alpha)
    save(crop, "rooms", "map_club.png")
    print("map_club box", tight)
    for key, (pos, label) in list(MARKERS.items()) + [("club", CLUB)]:
        x0, y0, x1, y1 = marker_box(pos, label)
        print(key, "center", ((x0 + x1) // 2, (y0 + y1) // 2), "size", (x1 - x0, y1 - y0))
    return a
