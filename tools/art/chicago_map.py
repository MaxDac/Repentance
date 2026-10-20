"""Location-select screen: a real 1920 street map of downtown Chicago, folded and yellowed, on a dark desk under a lamp.

The map is the Loop and Near North Side of the Fred Wild Company's *Double Indexed Street Map of Chicago* (1920,
public domain; scan via Wikimedia Commons, AGS Library UWM), cropped and kept greyscale in
src/chicago_1920_fred_wild.png. It is printed onto aged paper here, the lake given a faint wash, then folded, stained
and lit. map.png carries no pins: each place in MARKERS is a map tack pinning a handwritten paper tag, exported as a
cropped transparent overlay (map_<key>.png) that lines up pixel-exactly at the top-left printed by build(); the map
room shows the ones the story has opened up."""
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from functools import lru_cache
import os
import random
import numpy as np
from .common import ROOT, W, FULL_H, hx, mix, mul, light, shadow, vignette, pixelize, palette_of, save

SRC = os.path.join(ROOT, "tools", "art", "src", "chicago_1920_fred_wild.png")
HAND = os.path.join(ROOT, "tools", "art", "src", "Caveat.ttf")

PAPER = (8, 7, 471, 262)
PRINT = (10, 9, 469, 260)
PAPER_C = hx("dccca0")
PAPER_D = hx("b49e6e")
INK = hx("2e2418")
WATER = hx("9aa8a4")
TAG = hx("efe5c8")
TAG_D = hx("c4b48c")
TAG_INK = hx("23253a")
STEEL = hx("b4b8bc")
STEEL_D = hx("5c6066")

# Lake Michigan east of this shore, in source-map pixels (the 1750-wide scan); Municipal Pier is left unwashed.
SHORE = [(1156, 0), (1169, 50), (1188, 138), (1231, 188), (1300, 269), (1313, 313), (1344, 375), (1356, 413),
         (1375, 438), (1375, 500), (1369, 550), (1325, 563), (1300, 588), (1306, 964)]
PIER = (1370, 452, 1700, 490)

# Tack colours: head, rim/shade, highlight.
RED = (hx("b82a2c"), hx("5e1014"), hx("f28a7a"))
BLUE = (hx("2c4c9c"), hx("101e4a"), hx("8aa8ec"))
GREEN = (hx("2e7a44"), hx("10361c"), hx("8ad49a"))
YELLOW = (hx("d8a82a"), hx("6a4a0c"), hx("fbe496"))
WHITE = (hx("dcdcd4"), hx("6c6c68"), hx("ffffff"))
BLACK = (hx("26262a"), hx("08080a"), hx("8c8c96"))

# Needle point on the map (roughly where the place really was), the tag text, tack colour and which side the tag
# hangs (+1 right of the pin, -1 left) with a vertical nudge.
MARKERS = {
    "cathedral": ((289, 97), "Holy Name", RED, 1, -2),          # State & Superior
    "tribune": ((306, 140), "Tribune", BLUE, 1, 0),             # Michigan Ave, north bank of the river
    "club": ((285, 140), "18 W. Hubbard", BLACK, -1, 1),        # Hubbard between State and Dearborn
    "library": ((307, 188), "Library", GREEN, 1, 0),            # Michigan & Washington
    "harrington": ((264, 212), "Harrington", YELLOW, -1, 0),    # LaSalle Street
    "office": ((163, 182), "Office", WHITE, 1, 0),              # West Madison, off Halsted
    "convent": ((213, 40), "Convent", BLUE, 1, 0),              # Near North, by Division
    "hotel": ((335, 68), "Aurelian", RED, 1, 0),                # the Gold Coast end of Michigan Ave
}


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


@lru_cache(maxsize=1)
def ink_coverage():
    """How much printer's ink lies on each screen pixel of the print area (0..1), area-averaged from the scan."""
    with Image.open(SRC) as scan:
        src = np.asarray(scan.convert("L"), np.float32)
    white, black = np.percentile(src, 80), np.percentile(src, 2)
    ink = np.clip((white - src) / (white - black), 0, 1)
    x0, y0, x1, y1 = PRINT
    small = Image.fromarray((ink * 255).astype(np.uint8)).resize((x1 - x0, y1 - y0), Image.Resampling.BOX)
    cov = np.asarray(small, np.float32) / 255.0
    return np.clip(cov * 1.35, 0, 1) ** 0.85


@lru_cache(maxsize=1)
def lake_mask():
    """The lake's area on screen, softened, for a faint wash under the ink."""
    with Image.open(SRC) as scan:
        sw, sh = scan.size
    x0, y0, x1, y1 = PRINT
    sx, sy = (x1 - x0) / sw, (y1 - y0) / sh
    pts = [(x0 + x * sx, y0 + y * sy) for x, y in SHORE] + [(x1, y1), (x1, y0)]
    m = Image.new("L", (W, FULL_H), 0)
    d = ImageDraw.Draw(m)
    d.polygon(pts, fill=255)
    px0, py0, px1, py1 = PIER
    d.rectangle([x0 + px0 * sx, y0 + py0 * sy, x0 + px1 * sx, y0 + py1 * sy], fill=0)
    return m.filter(ImageFilter.GaussianBlur(1.5))


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
    col = np.array(PAPER_C, np.float32) * (1 - t[..., None]) + np.array(PAPER_D, np.float32) * t[..., None]
    lake = np.asarray(lake_mask(), np.float32)[..., None] / 255.0
    col = col * (1 - lake * 0.35) + np.array(mix(WATER, PAPER_C, 0.2), np.float32) * lake * 0.35
    col += rng.normal(0, 2.5, (FULL_H, W, 1))
    # printer's ink, slightly faded where the paper has aged most
    px0, py0, px1, py1 = PRINT
    ink = np.zeros((FULL_H, W), np.float32)
    ink[py0:py1, px0:px1] = ink_coverage()
    ink *= 0.92 - t * 0.2
    col = col * (1 - ink[..., None]) + np.array(INK, np.float32) * ink[..., None]
    sheet = Image.fromarray(col.clip(0, 255).astype(np.uint8))
    d = ImageDraw.Draw(sheet)
    d.polygon([(x1 - 9, y1 - 9), (x1 - 9, y1), (x1, y1 - 9)], fill=mul(PAPER_D, 0.85))
    d.line([(x1 - 9, y1), (x1, y1 - 9)], fill=mul(PAPER_D, 0.7))
    img.paste(sheet, (0, 0), m)


def creases(img):
    """Fold lines: a darker valley with a highlit ridge beside it, and the wear where folds cross."""
    x0, y0, x1, y1 = PAPER
    for x in (124, 240, 356):
        shadow(img, "rect", [x, y0 + 1, x, y1 - 1], k=0.26, blur=0)
        light(img, "rect", [x + 1, y0 + 1, x + 1, y1 - 1], hx("fff4d0"), k=0.22, blur=0)
    y = 135
    shadow(img, "rect", [x0 + 1, y, x1 - 1, y], k=0.26, blur=0)
    light(img, "rect", [x0 + 1, y + 1, x1 - 1, y + 1], hx("fff4d0"), k=0.22, blur=0)
    for x in (124, 240, 356):
        light(img, "ellipse", [x - 3, y - 2, x + 3, y + 3], hx("fff0c8"), k=0.3, blur=1)
    # coffee ring stain
    m = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(m)
    d.ellipse([60, 206, 96, 238], outline=70, width=2)
    d.ellipse([64, 210, 92, 234], fill=18)
    m = m.filter(ImageFilter.GaussianBlur(0.6))
    stain = Image.new("RGB", img.size, hx("8a5a2a"))
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


def hand_font():
    f = ImageFont.truetype(HAND, 11 * 4)
    f.set_variation_by_axes([600])
    return f


def tag_rect(key):
    """Screen (x0, y0, x1, y1) of a place's paper tag; the tack pierces it near its inner end."""
    (px, py), label, _, side, dy = MARKERS[key]
    w = int(hand_font().getlength(label) / 4) + (10 if side > 0 else 13)
    top = py - 6 + dy
    return (px - 3, top, px - 3 + w, top + 11) if side > 0 else (px + 3 - w, top, px + 3, top + 11)


def marker_box(key):
    """Screen-space (x0, y0, x1, y1) bounds of a marker: tag, its shadow, the tack head, needle and their shadows."""
    (px, py), *_ = MARKERS[key]
    tx0, ty0, tx1, ty1 = tag_rect(key)
    return (min(tx0, px - 8), min(ty0, py - 12), max(tx1 + 3, px + 8), max(ty1 + 3, py + 5))


def tag(img, key):
    (px, py), label, _, side, _ = MARKERS[key]
    x0, y0, x1, y1 = tag_rect(key)
    rnd = random.Random(sum(map(ord, key)))
    shadow(img, "rect", [x0 + 1, y0 + 2, x1 + 1, y1 + 2], k=0.45, blur=0.6)
    d = ImageDraw.Draw(img)
    # torn far end: a ragged column of paper
    far = x1 if side > 0 else x0
    poly = [(x0 if side > 0 else x1, y0)]
    for y in range(y0, y1 + 1, 2):
        poly.append((far - side * rnd.randint(0, 1), y))
    poly += [(far, y1), (x0 if side > 0 else x1, y1)]
    d.polygon(poly, fill=TAG)
    d.line([(min(x0, x1) + 1, y1), (max(x0, x1) - 1, y1)], fill=mix(TAG, TAG_D, 0.6))
    d.line([(x0 if side > 0 else x1, y0), (x0 if side > 0 else x1, y1)], fill=mix(TAG, TAG_D, 0.3))
    # the handwriting, in a fountain-pen blue-black, in the part of the tag clear of the tack
    f = hand_font()
    tx = (x0 + 7 if side > 0 else x0 + 3)
    layer = Image.new("L", ((x1 - x0) * 4, (y1 - y0 + 2) * 4), 0)
    ImageDraw.Draw(layer).text((((tx - x0) * 4), -6), label, fill=255, font=f)
    layer = layer.resize((x1 - x0, y1 - y0 + 2), Image.Resampling.BOX).point(lambda v: min(255, int(v * 1.5)))
    img.paste(Image.new("RGB", layer.size, TAG_INK), (x0, y0), layer)


def tack(img, key):
    """A ball-headed map tack driven in at a slant: steel needle, glossy head lit from the lamp, shadows on the paper."""
    (px, py), _, (c, dark, hi), *_ = MARKERS[key]
    hx_, hy_ = px - 2, py - 6
    shadow(img, "polygon", [(px, py), (px + 5, py - 2), (px + 6, py - 1)], k=0.5, blur=0)
    shadow(img, "ellipse", [hx_ - 2, hy_ + 1, hx_ + 7, hy_ + 9], k=0.55, blur=0.7)
    d = ImageDraw.Draw(img)
    d.line([(px, py), (hx_ + 1, hy_ + 3)], fill=STEEL_D)
    d.line([(px - 1, py - 1), (hx_, hy_ + 3)], fill=STEEL)
    d.ellipse([hx_ - 4, hy_ - 4, hx_ + 4, hy_ + 4], fill=dark)
    d.ellipse([hx_ - 4, hy_ - 4, hx_ + 3, hy_ + 3], fill=c)
    d.ellipse([hx_ - 3, hy_ - 3, hx_, hy_], fill=mix(c, hi, 0.5))
    d.point((hx_ - 2, hy_ - 1), fill=hi)
    d.point((hx_ - 1, hy_ - 2), fill=hi)
    d.point((hx_ - 2, hy_ - 2), fill=(255, 255, 255))
    d.line([(hx_ + 3, hy_ + 1), (hx_ + 1, hy_ + 3)], fill=mix(dark, c, 0.3))


def marker(img, key):
    tag(img, key)
    tack(img, key)


def lighting(img):
    light(img, "ellipse", [70, -10, 430, 250], hx("ffcf80"), k=0.2, blur=40)
    vignette(img, k=0.7, tint=(60, 42, 34), blur=50)


def paint_base():
    img = Image.new("RGB", (W, FULL_H))
    desk(img)
    paper(img)
    creases(img)
    return img


def _overlay(base_px, key, pal):
    """Pixelized marker cut out as an RGBA overlay (map_<key>.png) to lay over the pin-less map."""
    with_pin = paint_base()
    marker(with_pin, key)
    pencil(with_pin)
    lighting(with_pin)
    b = pixelize(with_pin, pal)
    box = marker_box(key)
    diff = np.any(np.asarray(base_px.crop(box)) != np.asarray(b.crop(box)), axis=2)
    for bg in ((0, 0, 0), (255, 255, 255)):
        probe = Image.new("RGB", (W, FULL_H), bg)
        marker(probe, key)
        diff |= np.any(np.asarray(probe.crop(box)) != np.array(bg, np.uint8), axis=2)
    ys, xs = np.nonzero(diff)
    tight = (box[0] + int(xs.min()), box[1] + int(ys.min()), box[0] + int(xs.max()) + 1, box[1] + int(ys.max()) + 1)
    crop = b.crop(tight).convert("RGBA")
    alpha = Image.fromarray((diff[tight[1] - box[1]:tight[3] - box[1], tight[0] - box[0]:tight[2] - box[0]]
                             * 255).astype(np.uint8))
    crop.putalpha(alpha)
    save(crop, "rooms", f"map_{key}.png")
    x0, y0, x1, y1 = box
    print(key, "overlay at", tight[:2], "hotspot center", ((x0 + x1) // 2, (y0 + y1) // 2), "size", (x1 - x0, y1 - y0))


def palette():
    every = paint_base()
    for key in MARKERS:
        marker(every, key)
    lighting(every)
    pal = palette_of(every, 112)
    for c, dark, hi in (RED, BLUE, GREEN, YELLOW, WHITE, BLACK):
        pal += [c, dark, hi, mix(c, hi, 0.5), mix(dark, c, 0.3)]
    return pal + [TAG, TAG_INK, STEEL, STEEL_D, (255, 255, 255)]


def build():
    """The map itself carries no pins: every location is an overlay the room shows as the story opens it up."""
    base = paint_base()
    pencil(base)
    lighting(base)
    pal = palette()
    a = pixelize(base, pal)
    save(a, "rooms", "map.png")
    for key in MARKERS:
        _overlay(a, key, pal)
    return a
