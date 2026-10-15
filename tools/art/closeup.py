"""Framed close-up panels popped up over a scene, Monkey Island 2 style.

Each is built from an original generated picture committed under tools/art/src/ and reduced to a VGA close-up:
chunky pixels, a tight palette and ordered dithering, inside a dark bevelled frame.

- stage_closeup: Eleanor on the Club stage, the stag and the hooded mask behind her, long locks of hair falling over
  her breasts. The clothed variant is its own picture: the same one in a dark velvet dress over her shoulders and chest.
- rose_closeup: Rose calling Micah back from her door.
- beaten_closeup: Micah flat on his back after a beating (Hubbard Street in Act 2, the cathedral steps in Act 3), looking up from under his hat.
- convent_closeup: outside the convent at the end of Act 1, Micah on the left and Eleanor on the right, two portraits
  in one panel split by a bar in the frame's colours.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

from .common import ROOT, hx, palette_of, pixelize, save

SRC = os.path.join(ROOT, "tools", "art", "src", "stage_closeup.png")
CLOTHED_SRC = os.path.join(ROOT, "tools", "art", "src", "stage_closeup_clothed.png")
ROSE_SRC = os.path.join(ROOT, "tools", "art", "src", "rose_closeup.png")
BEATEN_SRC = os.path.join(ROOT, "tools", "art", "src", "beaten_closeup.png")
AW, AH = 220, 113  # art pixels, the picture's 1.95:1, so both masked men stay in view
SCALE = 2  # doubled into chunky pixels, nearly filling the 480x270 screen
IW, IH = AW * SCALE, AH * SCALE
FRAME = 5
PW, PH = IW + 2 * FRAME, IH + 2 * FRAME
COLOURS = 32
# two-portrait panels: each half in art pixels, either side of a bar in the frame's colours
BAR = 4
HALF = (AW - BAR) // 2
MICAH_SRC = os.path.join(ROOT, "tools", "art", "src", "convent_micah.png")
ELEANOR_SRC = os.path.join(ROOT, "tools", "art", "src", "convent_eleanor.png")
MICAH_FACE_X, ELEANOR_FACE_X = 672, 665  # face centres in the 1344x768 sources
# One palette for both stage variants, so they differ only where the dress is. Pinned to the one the pictures had
# before the locks of hair were painted in, so her face reduces to exactly the same pixels as it always did.
STAGE_PALETTE = [hx(c) for c in """
f6d3a3 f6d1a2 f6cf9d e6af84 c07c5c 865338 4d3124 26282b 252729 242628 781f27 4f1b1b 242223 1e2022 18181a 141518
111316 101114 0d0e11 0a0c0f 0a090b 060608 030405 030204 010202 010102 010101 010100 010001 000101 000001 000000
""".split()]


def stage_closeup(src, pal=STAGE_PALETTE):
    """Eleanor on the stage, framed; src is the nude or the clothed picture."""
    return framed(src.convert("RGB"), pal)


def rose_crop(src):
    """Rose in her doorway, trimmed evenly top and bottom to the panel's 1.95:1 so her face stays centred."""
    img = src.convert("RGB")
    w, h = img.size
    ch = round(w * AH / AW)
    top = (h - ch) // 2
    return img.crop((0, top, w, top + ch))


def rose_closeup(src):
    """Rose calling Micah back from the door: "Wait!"."""
    img = rose_crop(src)
    return framed(img, palette_of(img.resize((AW, AH), Image.BOX), COLOURS))


def crop_to_panel(img):
    """Crops a picture to the panel's aspect, trimming the bottom first so heads and hats stay in view."""
    w, h = img.size
    if w / h > AW / AH:
        cw = round(h * AW / AH)
        x = (w - cw) // 2
        return img.crop((x, 0, x + cw, h))
    return img.crop((0, 0, w, round(w * AH / AW)))


def beaten_closeup(src):
    """Micah flat on his back on the cathedral steps, looking up from under his hat."""
    img = crop_to_panel(src.convert("RGB"))
    return framed(img, palette_of(img.resize((AW, AH), Image.BOX), COLOURS))


def portrait_crop(src, cx):
    """One half of a two-portrait panel: the full height, as wide as the half's aspect, centred on the face at cx."""
    img = src.convert("RGB")
    w, h = img.size
    cw = round(h * HALF / AH)
    x = int(np.clip(cx - cw // 2, 0, w - cw))
    return img.crop((x, 0, x + cw, h))


def convent_closeup(micah, eleanor):
    """Outside the convent, the first time they meet: Micah on the left, Eleanor on the right."""
    left = portrait_crop(micah, MICAH_FACE_X)
    right = portrait_crop(eleanor, ELEANOR_FACE_X)
    return framed_pair(left, right)


def frame_border(panel):
    d = ImageDraw.Draw(panel)
    d.rectangle([0, 0, PW - 1, PH - 1], outline=hx("000000"))
    d.rectangle([2, 2, PW - 3, PH - 3], outline=hx("8a6a3a"))
    d.rectangle([FRAME - 1, FRAME - 1, PW - FRAME, PH - FRAME], outline=hx("000000"))
    return panel


def framed(img, pal):
    """The framed panel: the picture reduced to chunky VGA pixels inside a dark bevelled frame."""
    small = img.resize((AW, AH), Image.BOX)
    inner = pixelize(small, pal, spread=8).resize((IW, IH), Image.NEAREST)
    panel = Image.new("RGB", (PW, PH), hx("08060a"))
    panel.paste(inner, (FRAME, FRAME))
    return frame_border(panel)


def framed_pair(left, right, pal=None):
    """Two pictures side by side in one framed panel, split by a bar in the frame's colours. One palette for both."""
    a = left.resize((HALF, AH), Image.BOX)
    b = right.resize((HALF, AH), Image.BOX)
    both = Image.new("RGB", (HALF * 2, AH))
    both.paste(a, (0, 0))
    both.paste(b, (HALF, 0))
    pal = pal or palette_of(both, COLOURS)
    panel = Image.new("RGB", (PW, PH), hx("08060a"))
    panel.paste(pixelize(a, pal, spread=8).resize((HALF * SCALE, IH), Image.NEAREST), (FRAME, FRAME))
    panel.paste(pixelize(b, pal, spread=8).resize((HALF * SCALE, IH), Image.NEAREST), (PW - FRAME - HALF * SCALE, FRAME))
    d = ImageDraw.Draw(panel)
    x0 = FRAME + HALF * SCALE
    # the two halves' inner frames meet in the middle: black, gold, gold, black
    for dx, colour in ((0, "000000"), (2, "8a6a3a"), (BAR * SCALE - 3, "8a6a3a"), (BAR * SCALE - 1, "000000")):
        d.line([x0 + dx, FRAME, x0 + dx, PH - FRAME - 1], fill=hx(colour))
    return frame_border(panel)


def heraldry_closeup():
    """The foot of Harrington senior's portrait, close: the hem of his black coat, the band of heraldry, the gilt
    frame. The same painting as the portrait's band in the office (act2_rooms.heraldry), only nearer."""
    from .act2_rooms import heraldry
    from .common import noise, vgrad
    w, h = AW * 4, AH * 4
    img = Image.new("RGB", (w, h))
    coat, band = round(h * 0.16), round(h * 0.84)
    vgrad(img, (0, 0, w - 1, coat), hx("1a1626"), hx("100e18"))
    d = ImageDraw.Draw(img)
    for x in (w // 2 - 160, w // 2 + 4, w // 2 + 210):  # folds in the coat
        d.line([(x, 0), (x + 12, coat)], fill=hx("26223a"), width=6)
    d.line([(w // 2, 0), (w // 2, coat)], fill=hx("08060c"), width=4)  # where the coat closes
    heraldry(img, (0, coat, w - 1, band))
    vgrad(img, (0, band + 1, w - 1, h - 1), hx("d8b860"), hx("6a4a1a"))
    d.line([(0, band + 1), (w - 1, band + 1)], fill=hx("3a2a0c"), width=4)
    for x in range(0, w, 40):  # beading on the frame
        d.ellipse([x + 14, band + 24, x + 26, band + 36], fill=hx("f0d890"), outline=hx("7a5a22"))
    noise(img, (0, 0, w - 1, h - 1), 5, 91)
    return framed(img, palette_of(img.resize((AW, AH), Image.BOX), COLOURS))


def build():
    nude, clothed = Image.open(SRC), Image.open(CLOTHED_SRC)
    save(stage_closeup(nude), "ui", "stage_closeup.png")
    save(stage_closeup(clothed), "ui", "stage_closeup_clothed.png")
    save(rose_closeup(Image.open(ROSE_SRC)), "ui", "rose_closeup.png")
    save(beaten_closeup(Image.open(BEATEN_SRC)), "ui", "beaten_closeup.png")
    save(convent_closeup(Image.open(MICAH_SRC), Image.open(ELEANOR_SRC)), "ui", "convent_closeup.png")
    save(heraldry_closeup(), "ui", "heraldry_closeup.png")
