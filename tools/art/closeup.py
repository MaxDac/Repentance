"""Framed close-up panels popped up over a scene, Monkey Island 2 style.

Each is built from an original generated picture committed under tools/art/src/ and reduced to a VGA close-up:
chunky pixels, a tight palette and ordered dithering, inside a dark bevelled frame.

- stage_closeup: Eleanor on the Club stage, the stag and the hooded mask behind her, long locks of hair falling over
  her breasts. The clothed variant is its own picture: the same one in a dark velvet dress over her shoulders and chest.
- rose_closeup: Rose calling Micah back from her door.
- beaten_closeup: Micah flat on his back after a beating (Hubbard Street in Act 2, the cathedral steps in Act 3), looking up from under his hat.
- convent_closeup: outside the convent at the end of Act 1, Micah on the left and Eleanor on the right, two portraits
  in one panel split by a bar in the frame's colours. Micah's picture is zoomed so his face is the same size as hers.
- motel_closeup: a red neon MOTEL sign over a rain-soaked Chicago street at night.
- vows_photo: Micah and Rose on the day they renewed their vows (ending 1's epilogue), a portrait-shaped sepia
  studio print on a cream 1920s card mount with worn corners, instead of the dark frame.
"""
import os

import numpy as np
from PIL import Image, ImageDraw

from .common import ROOT, hx, palette_of, pixelize, save

SRC = os.path.join(ROOT, "tools", "art", "src", "stage_closeup.png")
CLOTHED_SRC = os.path.join(ROOT, "tools", "art", "src", "stage_closeup_clothed.png")
ROSE_SRC = os.path.join(ROOT, "tools", "art", "src", "rose_closeup.png")
BEATEN_SRC = os.path.join(ROOT, "tools", "art", "src", "beaten_closeup.png")
MOTEL_SRC = os.path.join(ROOT, "tools", "art", "src", "motel_street.png")
MOTEL_TOP = 245 / 1024  # just above the neon sign in the square source, so the wet street below stays in view
MOTEL_SIGN, MOTEL_NEON = (138, 6, 188, 28), 6  # the sign's letters in panel art pixels, and the colours kept for them
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
# the vow-renewal photo: a portrait print, as tall as the other close-ups' pictures, on a cream card mount
VOWS_SRC = os.path.join(ROOT, "tools", "art", "src", "vows_photo.png")
VOWS_BORDER = 26  # the source's own worn border, trimmed so only the studio picture is reduced
PHOTO_AW, PHOTO_AH = 72, AH
PHOTO_IW, PHOTO_IH = PHOTO_AW * SCALE, PHOTO_AH * SCALE
MOUNT = 9
PHOTO_PW, PHOTO_PH = PHOTO_IW + 2 * MOUNT, PHOTO_IH + 2 * MOUNT
MICAH_FACE_X, ELEANOR_FACE_X = 672, 665  # face centres in the 1344x768 sources
# Face boxes in the sources (brow to chin, cheek to cheek) and the eye lines. Micah's picture is zoomed so his face
# box covers the same area as Eleanor's, with his eyes on her eye line, so both faces come out the same size.
MICAH_FACE_W, MICAH_FACE_H, MICAH_EYES_Y = 260, 235, 265
ELEANOR_FACE_W, ELEANOR_FACE_H, ELEANOR_EYES_Y = 280, 320, 245
MICAH_ZOOM = ((ELEANOR_FACE_W * ELEANOR_FACE_H) / (MICAH_FACE_W * MICAH_FACE_H)) ** 0.5
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


def motel_crop(src):
    """The rainy street, trimmed to the panel's 1.95:1 from just above the MOTEL sign down into the wet street."""
    img = src.convert("RGB")
    w, h = img.size
    ch = round(w * AH / AW)
    top = min(round(h * MOTEL_TOP), h - ch)
    return img.crop((0, top, w, top + ch))


def motel_closeup(src):
    """The red neon MOTEL sign over a rain-soaked street at night."""
    img = motel_crop(src)
    small = img.resize((AW, AH), Image.BOX)
    # the neon is a sliver of the picture: give the sign its own reds so the reduction keeps it glowing
    sign = small.crop(MOTEL_SIGN)
    return framed(img, palette_of(small, COLOURS - MOTEL_NEON) + palette_of(sign, MOTEL_NEON))


def portrait_crop(src, cx, zoom=1.0, eyes_y=None, target_eyes_y=None):
    """One half of a two-portrait panel, as wide as the half's aspect, centred on the face at cx. At zoom 1 it is
    the full height; zoomed in, it is 1/zoom of the height, placed so the eyes at eyes_y land where target_eyes_y
    sits in a full-height crop."""
    img = src.convert("RGB")
    w, h = img.size
    ch = round(h / zoom)
    cw = round(ch * HALF / AH)
    y = 0 if eyes_y is None else int(np.clip(round(eyes_y - target_eyes_y / zoom), 0, h - ch))
    x = int(np.clip(cx - cw // 2, 0, w - cw))
    return img.crop((x, y, x + cw, y + ch))


def convent_closeup(micah, eleanor):
    """Outside the convent, the first time they meet: Micah on the left, Eleanor on the right, faces the same size."""
    left = portrait_crop(micah, MICAH_FACE_X, MICAH_ZOOM, MICAH_EYES_Y, ELEANOR_EYES_Y)
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


def vows_crop(src):
    """The studio picture inside the source's own worn border, trimmed to the photo's art aspect."""
    img = src.convert("RGB")
    w, h = img.size
    x0, y0 = VOWS_BORDER, VOWS_BORDER
    cw = w - 2 * VOWS_BORDER
    ch = round(cw * PHOTO_AH / PHOTO_AW)
    return img.crop((x0, y0, x0 + cw, y0 + ch))


def vows_photo(src):
    """Micah and Rose on the day they renewed their vows: a 1920s studio print in sepia, chunky VGA pixels, on a
    cream card mount with worn, chipped corners."""
    from PIL import ImageOps
    from .common import noise, vgrad
    grey = ImageOps.autocontrast(vows_crop(src).convert("L"), cutoff=1)
    toned = ImageOps.colorize(grey, black=hx("1e1209"), mid=hx("8a6640"), white=hx("f2e0b8"))
    small = toned.resize((PHOTO_AW, PHOTO_AH), Image.BOX)
    inner = pixelize(small, palette_of(small, COLOURS), spread=8).resize((PHOTO_IW, PHOTO_IH), Image.NEAREST)
    card = Image.new("RGB", (PHOTO_PW, PHOTO_PH))
    vgrad(card, (0, 0, PHOTO_PW - 1, PHOTO_PH - 1), hx("eadcbc"), hx("d6c398"))
    noise(card, (0, 0, PHOTO_PW - 1, PHOTO_PH - 1), 4, 1927)
    d = ImageDraw.Draw(card)
    for x, y, r in ((6, 30, 2), (PHOTO_PW - 9, 70, 1), (14, PHOTO_PH - 6, 2), (PHOTO_PW - 20, 4, 1)):  # foxing
        d.ellipse([x - r, y - r, x + r, y + r], fill=hx("c4a878"))
    d.rectangle([3, 3, PHOTO_PW - 4, PHOTO_PH - 4], outline=hx("c8b184"))  # the mount's pressed line
    card.paste(inner, (MOUNT, MOUNT))
    d.rectangle([MOUNT - 1, MOUNT - 1, PHOTO_PW - MOUNT, PHOTO_PH - MOUNT], outline=hx("4a3620"))
    d.rectangle([0, 0, PHOTO_PW - 1, PHOTO_PH - 1], outline=hx("8a744e"))
    photo = card.convert("RGBA")
    px = photo.load()
    # worn corners: rounded off, the top right and bottom left chipped deeper
    for (cx, cy), depth in (((0, 0), 3), ((1, 0), 5), ((0, 1), 4), ((1, 1), 3)):
        for i in range(depth):
            for j in range(depth - i):
                x = i if cx == 0 else PHOTO_PW - 1 - i
                y = j if cy == 0 else PHOTO_PH - 1 - j
                px[x, y] = (0, 0, 0, 0)
    return photo


def build():
    nude, clothed = Image.open(SRC), Image.open(CLOTHED_SRC)
    save(stage_closeup(nude), "ui", "stage_closeup.png")
    save(stage_closeup(clothed), "ui", "stage_closeup_clothed.png")
    save(rose_closeup(Image.open(ROSE_SRC)), "ui", "rose_closeup.png")
    save(beaten_closeup(Image.open(BEATEN_SRC)), "ui", "beaten_closeup.png")
    save(motel_closeup(Image.open(MOTEL_SRC)), "ui", "motel_closeup.png")
    save(convent_closeup(Image.open(MICAH_SRC), Image.open(ELEANOR_SRC)), "ui", "convent_closeup.png")
    save(heraldry_closeup(), "ui", "heraldry_closeup.png")
    save(vows_photo(Image.open(VOWS_SRC)), "ui", "vows_photo.png")
