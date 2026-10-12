"""Framed close-up panels popped up over a scene, Monkey Island 2 style.

Each is built from an original generated picture committed under tools/art/src/ and reduced to a VGA close-up:
chunky pixels, a tight palette and ordered dithering, inside a dark bevelled frame.

- stage_closeup: Eleanor on the Club stage, the stag and the hooded mask behind her. The clothed variant paints a
  dark velvet dress over her shoulders and chest; the picture is otherwise the same.
- beaten_closeup: Micah flat on his back on the cathedral steps in Act 3, looking up from under his hat.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

from .common import ROOT, hx, palette_of, pixelize, save

SRC = os.path.join(ROOT, "tools", "art", "src", "stage_closeup.png")
BEATEN_SRC = os.path.join(ROOT, "tools", "art", "src", "beaten_closeup.png")
AW, AH = 220, 113  # art pixels, the picture's 1.95:1, so both masked men stay in view
SCALE = 2  # doubled into chunky pixels, nearly filling the 480x270 screen
IW, IH = AW * SCALE, AH * SCALE
FRAME = 5
PW, PH = IW + 2 * FRAME, IH + 2 * FRAME
COLOURS = 32

# the neckline, in source pixels: a scoop between the shoulders, sleeves over the shoulder tops
NECK_X, NECK_HALF = 1010, 290
NECK_TOP, NECK_DIP = 805, 75
DRESS = np.array(hx("4a0e16"), float)  # oxblood velvet
DRESS_LIGHT = np.array(hx("a8323a"), float)
TRIM = np.array(hx("c89a48"), float)  # a thin gold edge along the neckline


def neckline(x):
    """Top edge of the dress at source column x."""
    u = np.clip((x - NECK_X) / NECK_HALF, -1, 1)
    return NECK_TOP + NECK_DIP * (1 - u * u)


def skin_mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 110) & (r > g) & (g > b) & (r - b > 35)


def dress(img):
    """Covers the skin below the neckline in velvet, shaded by the light that fell on her."""
    a = np.array(img, float)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    below = yy > neckline(xx)
    m = skin_mask(a) & below
    lum = a.mean(-1)
    lit = np.clip((lum - 150) / 90, 0, 1)[..., None]
    a[m] = (DRESS + (DRESS_LIGHT - DRESS) * lit ** 1.5)[m]
    edge = m & ~(yy - 14 > neckline(xx))
    a[edge] = TRIM * (0.75 + 0.35 * lit[edge])
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"), "RGB")


def shared_palette(src):
    """One palette for both variants, so they differ only where the dress is."""
    nude = src.convert("RGB").resize((AW, AH), Image.BOX)
    clothed = dress(src.convert("RGB")).resize((AW, AH), Image.BOX)
    both = Image.new("RGB", (AW, AH * 2))
    both.paste(nude, (0, 0))
    both.paste(clothed, (0, AH))
    return palette_of(both, COLOURS)


def crop_to_panel(img):
    """Crops a picture to the panel's aspect, trimming the bottom first so heads and hats stay in view."""
    w, h = img.size
    if w / h > AW / AH:
        cw = round(h * AW / AH)
        x = (w - cw) // 2
        return img.crop((x, 0, x + cw, h))
    return img.crop((0, 0, w, round(w * AH / AW)))


def framed(small, pal):
    """The art-pixel picture, dithered to its palette, doubled and set in a dark bevelled frame."""
    inner = pixelize(small, pal, spread=8).resize((IW, IH), Image.NEAREST)
    panel = Image.new("RGB", (PW, PH), hx("08060a"))
    panel.paste(inner, (FRAME, FRAME))
    d = ImageDraw.Draw(panel)
    d.rectangle([0, 0, PW - 1, PH - 1], outline=hx("000000"))
    d.rectangle([2, 2, PW - 3, PH - 3], outline=hx("8a6a3a"))
    d.rectangle([FRAME - 1, FRAME - 1, PW - FRAME, PH - FRAME], outline=hx("000000"))
    return panel


def stage_closeup(src, clothed, pal=None):
    """Eleanor's panel, nude or with the painted dress."""
    img = src.convert("RGB")
    if clothed:
        img = dress(img)
    return framed(img.resize((AW, AH), Image.BOX), pal or shared_palette(src))


def beaten_closeup(src):
    """Micah's panel on the cathedral steps."""
    small = crop_to_panel(src.convert("RGB")).resize((AW, AH), Image.BOX)
    return framed(small, palette_of(small, COLOURS))


def build():
    src = Image.open(SRC)
    pal = shared_palette(src)
    save(stage_closeup(src, clothed=False, pal=pal), "ui", "stage_closeup.png")
    save(stage_closeup(src, clothed=True, pal=pal), "ui", "stage_closeup_clothed.png")
    save(beaten_closeup(Image.open(BEATEN_SRC)), "ui", "beaten_closeup.png")
