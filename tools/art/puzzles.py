"""Targeted props, clue plates and inventory icons for the ten story puzzles."""
from PIL import Image, ImageDraw
from .common import hx, save, text
from .items import _icon, mirror


def waxed_mirror(d, im):
    mirror(d, im)
    d.ellipse([5, 3, 20, 17], fill=hx("ba9a62"))
    d.line([(7, 9), (17, 7), (13, 14)], fill=hx("e4c68c"), width=2)


def cloth(d, im):
    d.polygon([(4, 6), (25, 4), (28, 18), (7, 21)], fill=hx("e6dfc8"))
    d.polygon([(8, 7), (18, 6), (16, 14), (6, 16)], fill=hx("f4f0e2"))
    d.line([(8, 8), (21, 7), (23, 17)], fill=hx("a69f90"))
    d.line([(11, 6), (13, 19)], fill=hx("c4bcaa"))
    d.line([(16, 8), (20, 16)], fill=hx("b8b0a0"))


def wedge(d, im):
    d.polygon([(4, 18), (27, 9), (27, 19)], fill=hx("b58a4f"))
    d.line([(4, 18), (27, 9)], fill=hx("ead097"))
    for y, x1 in ((12, 22), (15, 25), (17, 26)):
        d.line([(8, y), (x1, y - 3)], fill=hx("8a6234"))
    d.line([(15, 17), (24, 13)], fill=hx("674c2e"))


def base(d, im):
    d.rectangle([4, 3, 28, 21], fill=hx("d8c898"), outline=hx("6a5a40"))
    for x in (10, 16, 22):
        d.line([(x, 4), (x, 20)], fill=hx("a3916c"))
    for y in (8, 13, 18):
        d.line([(5, y), (27, y)], fill=hx("a3916c"))
    for x, y in ((18, 8), (18, 16), (8, 8)):
        d.ellipse([x - 2, y - 2, x + 2, y + 2], outline=hx("6a5a40"))


def tracing(d, im):
    d.polygon([(4, 4), (28, 4), (28, 20), (4, 20)], fill=hx("7c9ba8", 150), outline=hx("c4e3ec"))
    for x, y in ((8, 8), (18, 8), (8, 17)):
        d.line([(x - 2, y), (x + 2, y)], fill=hx("e6f4f8"))
        d.line([(x, y - 2), (x, y + 2)], fill=hx("e6f4f8"))
    d.rectangle([19, 13, 25, 19], outline=hx("a43a32"))


GOLD, GOLD_HI, GOLD_LO = hx("c9a25e"), hx("f0d79a"), hx("6e5630")
INK, PANEL = hx("12131a"), hx("1c1d27")


def _stepped(d, box, fill, outline, step=3):
    """Rectangle with Art Deco stepped corners."""
    x0, y0, x1, y1 = box
    pts = [(x0 + step, y0), (x1 - step, y0), (x1 - step, y0 + 1), (x1 - 1, y0 + 1), (x1 - 1, y0 + step - 1),
           (x1, y0 + step - 1), (x1, y1 - step), (x1 - 1, y1 - step), (x1 - 1, y1 - 1), (x1 - step, y1 - 1),
           (x1 - step, y1), (x0 + step, y1), (x0 + step, y1 - 1), (x0 + 1, y1 - 1), (x0 + 1, y1 - step),
           (x0, y1 - step), (x0, y0 + step - 1), (x0 + 1, y0 + step - 1), (x0 + 1, y0 + 1), (x0 + step, y0 + 1)]
    d.polygon(pts, fill=fill, outline=outline)


def deco_button(state):
    """32x22 nine-patch (7px side, 6px top/bottom margins): stepped gold frame, inner keyline, corner studs."""
    fill, rim, line = {"normal": (hx("1f3036"), GOLD, GOLD_LO),
                       "hover": (hx("2d474e"), GOLD_HI, GOLD),
                       "pressed": (hx("5b4524"), GOLD_HI, GOLD_HI)}[state]
    im = Image.new("RGBA", (32, 22))
    d = ImageDraw.Draw(im)
    _stepped(d, (0, 0, 31, 21), fill, rim)
    d.rectangle([3, 3, 28, 18], outline=line)
    if state != "pressed":
        d.line([(4, 4), (27, 4)], fill=hx("ffffff", 40))
        d.line([(4, 17), (27, 17)], fill=hx("000000", 90))
    for x, y in ((2, 2), (29, 2), (2, 19), (29, 19)):
        im.putpixel((x, y), GOLD_HI if state != "normal" else GOLD)
    return im


def deco_pad(state):
    """16x16 nine-patch (4px margins) for direction pads: the deco button's frame, keyline and studs, smaller."""
    fill, rim, line = {"normal": (hx("1f3036"), GOLD, GOLD_LO),
                       "hover": (hx("2d474e"), GOLD_HI, GOLD),
                       "pressed": (hx("5b4524"), GOLD_HI, GOLD_HI)}[state]
    im = Image.new("RGBA", (16, 16))
    d = ImageDraw.Draw(im)
    _stepped(d, (0, 0, 15, 15), fill, rim, step=2)
    d.rectangle([2, 2, 13, 13], outline=line)
    if state != "pressed":
        d.line([(3, 3), (12, 3)], fill=hx("ffffff", 40))
        d.line([(3, 12), (12, 12)], fill=hx("000000", 90))
    return im


def _fan(d, cx, cy, r, start, end, col):
    import math
    for i in range(6):
        a = math.radians(start + (end - start) * i / 5)
        d.line([(cx, cy), (cx + r * math.cos(a), cy + r * math.sin(a))], fill=col)
    d.arc([cx - r, cy - r, cx + r, cy + r], start, end, fill=col)
    d.arc([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], start, end, fill=col)


def puzzle_frame():
    """The shared puzzle screen: deco frame, title cartouche, work area, clue card, footer and feedback strip."""
    im = Image.new("RGBA", (480, 270), INK)
    d = ImageDraw.Draw(im)
    for x in range(0, 480, 6):
        d.line([(x, 0), (x, 269)], fill=hx("161720"))
    _stepped(d, (3, 3, 476, 266), None, GOLD, step=8)
    _stepped(d, (6, 6, 473, 263), None, GOLD_LO, step=6)
    for cx, cy, a0 in ((7, 7, 0), (472, 7, 90), (472, 262, 180), (7, 262, 270)):
        _fan(d, cx, cy, 16, a0, a0 + 90, GOLD_LO)
    # title cartouche, stepped like a skyscraper crown
    d.polygon([(130, 6), (350, 6), (342, 26), (138, 26)], fill=PANEL, outline=GOLD)
    d.line([(144, 23), (336, 23)], fill=GOLD_LO)
    for x in (120, 112, 104):
        d.line([(x, 16), (x + 6, 16)], fill=GOLD)
    for x in (354, 362, 370):
        d.line([(x, 16), (x + 6, 16)], fill=GOLD)
    # work area
    _stepped(d, (14, 31, 272, 204), hx("171a22"), GOLD_LO, step=4)
    # clue card
    _stepped(d, (280, 31, 466, 204), hx("221f22"), GOLD, step=4)
    d.rectangle([284, 35, 462, 200], outline=GOLD_LO)
    d.polygon([(330, 31), (416, 31), (410, 41), (336, 41)], fill=GOLD_LO)
    text(im, (373, 36), "CLUES", INK, size=8)
    # footer rule with a central chevron
    d.line([(16, 236), (226, 236)], fill=GOLD_LO)
    d.line([(254, 236), (464, 236)], fill=GOLD_LO)
    d.polygon([(232, 236), (240, 231), (248, 236), (240, 241)], outline=GOLD)
    d.rectangle([14, 241, 466, 259], fill=hx("0e0f14"), outline=GOLD_LO)
    return im


def build():
    for state in ("normal", "hover", "pressed"):
        save(deco_button(state), "ui", "deco_button.png" if state == "normal" else f"deco_button_{state}.png")
        save(deco_pad(state), "ui", "deco_pad.png" if state == "normal" else f"deco_pad_{state}.png")
    save(puzzle_frame(), "ui", "puzzle_frame.png")
    for name, fn in (("mirror_waxed", waxed_mirror), ("cloth", cloth), ("wedge", wedge),
                     ("audit_folder", base), ("audit_tracing", tracing)):
        save(_icon(fn), "items", name + ".png")

    save(_icon(wedge).resize((24, 18), Image.Resampling.NEAREST), "rooms", "packing_wedge.png")

    for released in (False, True):
        catch = Image.new("RGBA", (14, 18))
        d = ImageDraw.Draw(catch)
        d.polygon([(0, 2), (6, 2), (6, 6), (3, 6), (3, 16), (0, 16)], fill=hx("363944"))
        d.line([(0, 2), (5, 2)], fill=hx("8a929a"))
        d.line([(1, 6), (1, 16)], fill=hx("78808a"))
        d.line([(3, 8), (5, 6), (6, 9), (8, 6), (9, 9)], fill=hx("a0a4aa"))
        d.line([(3, 12), (10, 12), (11, 9)], fill=hx("606872"), width=2)
        for x, y in ((1, 4), (1, 14)):
            d.point((x, y), fill=hx("c4c4bc"))
        if released:
            d.polygon([(6, 11), (13, 8), (13, 11)], fill=hx("b88a4c"))
            d.line([(7, 10), (12, 9)], fill=hx("e0ba78"))
        else:
            d.line([(10, 12), (10, 15), (5, 15)], fill=hx("92969c"), width=2)
        save(catch, "rooms", "ladder_freed.png" if released else "ladder_catch.png")

    plates = Image.new("RGBA", (230, 34))
    d = ImageDraw.Draw(plates)
    gold = hx("e4c38a")
    for x in (10, 25, 40):
        d.ellipse([x, 9, x + 10, 19], outline=gold, width=2)
    # Three intersecting pointed loops, unlike the separate rings and four-point knot.
    for points in ([(107, 2), (97, 18), (107, 26), (117, 18), (107, 2)],
                   [(92, 27), (98, 9), (111, 11), (119, 24), (92, 27)],
                   [(123, 27), (116, 9), (104, 11), (96, 24), (123, 27)]):
        d.line(points, fill=gold, width=2)
    d.line([(190, 3), (177, 17), (190, 30), (203, 17), (190, 3)], fill=gold, width=2)
    d.line([(177, 4), (204, 29), (204, 4), (177, 29), (177, 4)], fill=gold, width=2)
    save(plates, "ui", "catalogue_plates.png")

    card = Image.new("RGB", (480, 270), hx("171821"))
    d = ImageDraw.Draw(card)
    d.rectangle([34, 48, 446, 214], fill=hx("e4d9bc"), outline=hx("a68854"), width=3)
    for y, ornament, words in ((84, "Feather", "Hubbard"), (132, "Lily", "The Club"), (180, "Leaf", "18 W.")):
        text(card, (112, y), ornament, hx("5e462e"), size=8)
        text(card, (305, y), words, hx("383244"), size=12, mirror=True)
    text(card, (240, 25), "Warmth reveals reversed writing", gold, size=8)
    save(card, "ui", "card_reversed.png")
    marker = Image.new("RGBA", (64, 28))
    d = ImageDraw.Draw(marker)
    d.rectangle([0, 0, 63, 27], fill=hx("352821", 230), outline=gold)
    text(marker, (32, 14), "HOTEL", gold, size=8)
    save(marker, "rooms", "map_hotel.png")
