"""Title card, verb-wheel icons, satchel, inventory chest and cursor."""
import math
from PIL import Image, ImageDraw
from .common import hx, mix, vgrad, light, vignette, pixelize, text, city, save, sunburst, noise
from .iconfx import _shade, _outline

GOLD, GOLD_D = hx("d8b050"), hx("8a6a28")


def title():
    img = Image.new("RGB", (480, 270))
    city(img, (0, 0, 479, 269), seed=3, lit=0.22, haze=hx("4a2a3a"))
    d = ImageDraw.Draw(img)
    sunburst(d, 240, 150, 260, 36, hx("1a1420"), hx("221a2a"))
    city(img, (0, 150, 479, 269), seed=9, lit=0.3, haze=hx("2a1a2a"))
    d.rectangle([110, 70, 370, 120], fill=hx("0e0a10"))
    d.rectangle([114, 74, 366, 116], outline=hx("c8a040"))
    d.rectangle([118, 78, 362, 112], outline=hx("6a5020"))
    text(img, (240, 95), "REPENTANCE", hx("e8c860"), size=24)
    text(img, (240, 132), "CHICAGO  1927", hx("c8b088"), size=8)
    light(img, "rect", [110, 70, 370, 120], hx("e0a040"), 0.2, 12)
    vignette(img, 0.7)
    save(pixelize(img, n=96), "ui", "title.png")


def _icon(fn, size=24):
    im = Image.new("RGBA", (size, size))
    fn(ImageDraw.Draw(im))
    return _outline(_shade(im))


def eye(d):
    d.chord([2, 6, 21, 19], 180, 360, fill=hx("f0e8d8"))
    d.chord([2, 4, 21, 19], 0, 180, fill=hx("f0e8d8"))
    d.ellipse([7, 7, 16, 16], fill=hx("4a7ab0"))
    d.ellipse([10, 10, 13, 13], fill=hx("101018"))
    d.point((9, 9), fill=hx("ffffff"))
    d.arc([2, 5, 21, 18], 180, 360, fill=hx("3a2418"), width=2)


def hand(d):
    skin = hx("e8b890")
    d.rounded_rectangle([5, 10, 18, 22], 3, fill=skin)
    for i, (x, top) in enumerate(((5, 5), (8, 2), (11, 1), (14, 3))):
        d.rounded_rectangle([x, top, x + 3, 13], 1, fill=skin)
    d.polygon([(18, 13), (22, 8), (23, 10), (19, 17)], fill=skin)
    d.rectangle([4, 20, 19, 23], fill=hx("6a1a22"))


def mouth(d):
    d.chord([2, 6, 21, 20], 0, 180, fill=hx("b02a3a"))
    d.polygon([(2, 12), (6, 7), (11, 9), (12, 9), (17, 7), (21, 12)], fill=hx("c83848"))
    d.chord([5, 9, 18, 17], 0, 180, fill=hx("2a0a10"))
    d.rectangle([7, 12, 16, 13], fill=hx("f0ece0"))
    d.line([(6, 9), (10, 8)], fill=hx("f08090"))


def boot(d):
    d.polygon([(6, 2), (14, 2), (14, 14), (21, 16), (22, 21), (4, 21), (5, 12)], fill=hx("4a2e1c"))
    d.rectangle([4, 20, 22, 22], fill=hx("1a1008"))
    d.line([(7, 6), (13, 6)], fill=hx("8a6a4a"))
    d.line([(7, 9), (13, 9)], fill=hx("8a6a4a"))
    d.line([(15, 15), (20, 17)], fill=hx("6a4a30"))


def slot():
    """Brass disc behind each wheel icon (normal + highlighted)."""
    out = []
    for hi in (False, True):
        im = Image.new("RGBA", (32, 32))
        d = ImageDraw.Draw(im)
        d.ellipse([0, 0, 31, 31], fill=hx("1a1210"))
        d.ellipse([1, 1, 30, 30], fill=GOLD if hi else GOLD_D)
        d.ellipse([3, 3, 28, 28], fill=hx("4a3a20") if hi else hx("2a2018"))
        for i in range(16):
            a = i * math.pi / 8
            d.point((15.5 + 13.5 * math.cos(a), 15.5 + 13.5 * math.sin(a)), fill=hx("fff0b0") if hi else GOLD)
        out.append(im)
    return out


def satchel(d):
    d.rounded_rectangle([3, 9, 26, 24], 3, fill=hx("6a3e22"))
    d.arc([8, 1, 21, 16], 180, 360, fill=hx("3a2014"), width=2)
    d.polygon([(3, 9), (26, 9), (24, 17), (5, 17)], fill=hx("7a4a2a"))
    d.rectangle([13, 14, 16, 18], fill=GOLD)
    d.line([(5, 21), (24, 21)], fill=hx("4a2a16"))


def chest():
    """Inventory panel: dark leather case with brass deco trim (260x70)."""
    w, h = 260, 70
    im = Image.new("RGB", (w, h))
    vgrad(im, (0, 0, w - 1, h - 1), hx("2a1a12"), hx("140c08"))
    noise(im, (0, 0, w - 1, h - 1), 4, 9)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=hx("0a0604"))
    d.rectangle([2, 2, w - 3, h - 3], outline=GOLD_D)
    d.rectangle([4, 4, w - 5, h - 5], outline=hx("4a3218"))
    for x in range(8, w - 8, 10):
        d.polygon([(x, 2), (x + 5, 5), (x + 10, 2)], fill=GOLD_D)
        d.polygon([(x, h - 3), (x + 5, h - 6), (x + 10, h - 3)], fill=GOLD_D)
    for (cx, cy) in ((2, 2), (w - 9, 2), (2, h - 9), (w - 9, h - 9)):
        d.rectangle([cx, cy, cx + 6, cy + 6], fill=GOLD)
    out = im.convert("RGBA")
    save(out, "ui", "inventory.png")


def cursor():
    im = Image.new("RGBA", (11, 11))
    d = ImageDraw.Draw(im)
    for c, w in ((hx("101010"), 3), (hx("f0e8c8"), 1)):
        d.line([(5, 0), (5, 3)], fill=c, width=w)
        d.line([(5, 7), (5, 10)], fill=c, width=w)
        d.line([(0, 5), (3, 5)], fill=c, width=w)
        d.line([(7, 5), (10, 5)], fill=c, width=w)
    save(im, "ui", "cursor.png")


def build():
    title()
    for name, fn in (("verb_look", eye), ("verb_hand", hand), ("verb_talk", mouth), ("verb_kick", boot)):
        save(_icon(fn), "ui", f"{name}.png")
    lo, hi = slot()
    save(lo, "ui", "wheel_slot.png")
    save(hi, "ui", "wheel_slot_hi.png")
    save(_icon(satchel, 30), "ui", "satchel.png")
    chest()
    cursor()
