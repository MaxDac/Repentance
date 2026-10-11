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


def build():
    for name, fn in (("mirror_waxed", waxed_mirror), ("cloth", cloth), ("wedge", wedge),
                     ("audit_folder", base), ("audit_tracing", tracing)):
        save(_icon(fn), "items", name + ".png")

    tin = Image.new("RGBA", (38, 24))
    d = ImageDraw.Draw(tin)
    d.rectangle([1, 4, 36, 22], fill=hx("55565e"), outline=hx("b6ac88"))
    d.rectangle([1, 4, 36, 9], fill=hx("84807a"))
    d.rectangle([16, 9, 21, 15], fill=hx("d8b66c"))
    d.ellipse([18, 10, 19, 12], fill=hx("25222a"))
    d.line([(24, 15), (32, 15), (32, 17)], fill=hx("d8b66c"))
    d.ellipse([22, 13, 26, 17], outline=hx("d8b66c"))
    save(tin, "rooms", "tool_tin.png")
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
