"""Inventory icons (32x24)."""
from PIL import Image, ImageDraw
from .common import hx, save, text
from .iconfx import _shade, _outline


def _icon(draw_fn):
    im = Image.new("RGBA", (32, 24))
    draw_fn(ImageDraw.Draw(im), im)
    return _outline(_shade(im))


def photo(d, im):
    d.polygon([(5, 4), (26, 2), (28, 20), (7, 22)], fill=hx("e8e0cc"))
    d.polygon([(8, 6), (24, 5), (25, 17), (9, 18)], fill=hx("6a6050"))
    d.ellipse([13, 7, 19, 13], fill=hx("c8b8a0"))
    d.chord([11, 6, 21, 13], 180, 360, fill=hx("2a2018"))
    d.polygon([(11, 18), (21, 17), (19, 13), (13, 13)], fill=hx("3a3040"))


def dollar(d, im):
    d.polygon([(2, 7), (29, 5), (30, 18), (3, 20)], fill=hx("8aa878"))
    d.polygon([(5, 9), (27, 7), (28, 16), (6, 18)], outline=hx("4a6a48"))
    d.ellipse([12, 8, 20, 17], fill=hx("6a8a60"))
    text(im, (16, 12), "1", hx("2a4a28", 255), size=8)


def matchbook(d, im):
    d.rectangle([7, 4, 25, 20], fill=hx("1e2a6a"))
    d.rectangle([7, 4, 25, 8], fill=hx("142050"))
    d.ellipse([12, 10, 20, 18], fill=hx("4a7ad8"))
    d.rectangle([15, 8, 17, 10], fill=hx("c8a040"))
    d.line([(7, 18), (25, 18)], fill=hx("a08060"))


def crowbar(d, im):
    d.line([(6, 20), (24, 5)], fill=hx("8a2a20"), width=3)
    d.line([(24, 5), (27, 4), (28, 7)], fill=hx("8a2a20"), width=3)
    d.line([(6, 20), (3, 18)], fill=hx("8a2a20"), width=3)
    d.line([(8, 17), (22, 6)], fill=hx("c85a40"))


def journal(d, im):
    d.polygon([(6, 3), (25, 2), (27, 21), (8, 22)], fill=hx("4a2a1c"))
    d.line([(9, 3), (10, 22)], fill=hx("2a160c"), width=2)
    d.polygon([(25, 3), (27, 3), (28, 20), (27, 21)], fill=hx("e0d4b0"))
    d.rectangle([14, 8, 22, 12], fill=hx("c8a050"))
    d.line([(20, 2), (21, 23)], fill=hx("8a1a1a"))


def key(d, im):
    d.ellipse([3, 7, 13, 17], fill=hx("c8a040"))
    d.ellipse([6, 10, 10, 14], fill=(0, 0, 0, 0))
    d.rectangle([12, 11, 27, 13], fill=hx("c8a040"))
    d.rectangle([22, 13, 24, 17], fill=hx("c8a040"))
    d.rectangle([26, 13, 27, 16], fill=hx("c8a040"))
    d.polygon([(14, 14), (22, 14), (22, 21), (14, 21)], fill=hx("8a1a2a"))
    text(im, (18, 17), "4", hx("e8d8a0", 255), size=6)


def diary(d, im):
    d.polygon([(7, 3), (25, 3), (25, 21), (7, 21)], fill=hx("6a2a4a"))
    d.rectangle([7, 3, 9, 21], fill=hx("4a1a32"))
    d.rectangle([25, 4, 26, 20], fill=hx("e8dcc0"))
    d.rectangle([13, 9, 21, 14], fill=hx("d8b050"))
    d.rectangle([22, 10, 27, 13], fill=hx("b89040"))


def ledger(d, im):
    d.polygon([(4, 4), (28, 4), (28, 20), (4, 20)], fill=hx("2a3a2a"))
    d.rectangle([4, 4, 7, 20], fill=hx("6a4a2a"))
    d.rectangle([25, 4, 28, 20], fill=hx("6a4a2a"))
    d.rectangle([12, 8, 22, 12], fill=hx("c8b890"))
    d.line([(13, 10), (21, 10)], fill=hx("3a2a1a"))
    d.line([(6, 20), (27, 20)], fill=hx("e0d4b0"))


def map_(d, im):
    d.polygon([(3, 5), (11, 3), (20, 6), (29, 3), (29, 19), (20, 22), (11, 19), (3, 21)], fill=hx("d8c898"))
    d.line([(11, 3), (11, 19)], fill=hx("a89060"))
    d.line([(20, 6), (20, 22)], fill=hx("a89060"))
    d.line([(5, 16), (10, 12), (16, 14), (22, 9)], fill=hx("6a5a40"))
    d.line([(22, 8), (26, 12)], fill=hx("b02020"), width=2)
    d.line([(26, 8), (22, 12)], fill=hx("b02020"), width=2)


def evidence(d, im):
    d.rectangle([4, 7, 28, 20], fill=hx("5a5a62"))
    d.rectangle([4, 7, 28, 10], fill=hx("74747c"))
    d.rectangle([14, 11, 18, 15], fill=hx("c8a040"))
    d.polygon([(7, 4), (14, 6), (13, 9), (6, 8)], fill=hx("e0d8c0"))
    d.ellipse([20, 3, 25, 8], fill=hx("d8b050"))


def suitcase_key(d, im):
    d.ellipse([6, 8, 13, 15], fill=hx("b89040"))
    d.ellipse([8, 10, 11, 13], fill=(0, 0, 0, 0))
    d.rectangle([12, 11, 24, 12], fill=hx("b89040"))
    d.rectangle([20, 13, 21, 15], fill=hx("b89040"))
    d.rectangle([23, 13, 24, 14], fill=hx("b89040"))


def revolver(d, im):
    d.rectangle([4, 7, 20, 10], fill=hx("4a4a52"))
    d.rectangle([4, 7, 20, 8], fill=hx("7a7a84"))
    d.rectangle([16, 6, 22, 12], fill=hx("3a3a42"))
    d.polygon([(20, 10), (26, 10), (29, 20), (23, 21)], fill=hx("5a3420"))
    d.line([(24, 12), (26, 19)], fill=hx("7a4a2a"))
    d.arc([16, 10, 22, 16], 0, 180, fill=hx("3a3a42"))
    d.point((5, 6), fill=hx("4a4a52"))


def lockpick(d, im):
    d.polygon([(3, 9), (14, 9), (14, 19), (3, 19)], fill=hx("4a2a1a"))
    d.line([(3, 14), (14, 14)], fill=hx("2a160c"))
    for i, y in enumerate((8, 11, 14)):
        d.line([(10, y + 2), (27, y)], fill=hx("a8a8b0"))
        d.line([(27, y), (28, y - 1 + i % 2 * 2)], fill=hx("a8a8b0"))
    d.rectangle([6, 9, 9, 19], fill=hx("6a3a24"))


def combination(d, im):
    d.polygon([(4, 5), (27, 3), (28, 20), (5, 21)], fill=hx("ece4d0"))
    d.line([(5, 7), (27, 5)], fill=hx("b8a060"))
    for y in (10, 14, 18):
        d.line([(8, y), (24, y - 1)], fill=hx("3a3a6a"))


def brass_box(d, im):
    d.rectangle([5, 9, 27, 20], fill=hx("b08a3a"))
    d.polygon([(5, 9), (27, 9), (25, 5), (7, 5)], fill=hx("d8b050"))
    d.line([(5, 9), (27, 9)], fill=hx("6a5020"))
    d.ellipse([13, 12, 19, 17], outline=hx("6a5020"))
    d.point((16, 14), fill=hx("6a5020"))
    d.rectangle([15, 8, 17, 11], fill=hx("8a6a28"))


def card(d, im):
    d.polygon([(4, 6), (28, 5), (28, 19), (4, 20)], fill=hx("f0e8e0"))
    d.polygon([(6, 8), (26, 7), (26, 17), (6, 18)], outline=hx("c8a050"))
    d.arc([10, 9, 16, 15], 90, 360, fill=hx("a0405a"))
    d.arc([16, 10, 22, 16], 270, 180, fill=hx("a0405a"))
    d.point((16, 12), fill=hx("c8a050"))


def mirror(d, im):
    """Small round hand mirror lying at an angle: tarnished silver frame, pale glass, short turned handle."""
    d.line([(17, 15), (26, 22)], fill=hx("9a9488"), width=4)
    d.ellipse([23, 19, 28, 23], fill=hx("8a8478"))
    d.line([(18, 15), (25, 21)], fill=hx("c8c2b4"))
    d.ellipse([3, 1, 22, 19], fill=hx("a8a294"))
    d.ellipse([5, 3, 20, 17], fill=hx("6a6660"))
    d.ellipse([6, 4, 19, 16], fill=hx("8aa6b8"))
    d.chord([6, 4, 19, 16], 200, 290, fill=hx("c8dce6"))
    d.line([(9, 13), (14, 7)], fill=hx("e8f2f4"))
    d.point((15, 6), fill=hx("e8f2f4"))
    d.rectangle([16, 14, 18, 16], fill=hx("b8b2a4"))


def book(d, im):
    """Old dark-green leather book of Celtic rites: raised spine bands, worn page edges, a gilt triquetra."""
    d.polygon([(6, 2), (25, 2), (26, 21), (7, 22)], fill=hx("1e3a2a"))
    d.polygon([(25, 3), (27, 4), (28, 20), (26, 21)], fill=hx("d8caa0"))
    for y in (8, 12, 16):
        d.line([(26, y), (27, y)], fill=hx("b0a078"))
    d.rectangle([6, 2, 9, 22], fill=hx("122618"))
    for y in (5, 11, 18):
        d.line([(6, y), (9, y)], fill=hx("a07a34"))
    d.polygon([(11, 4), (23, 4), (23, 19), (11, 20)], outline=hx("8a6a2c"))
    g = hx("e8bc54")
    for x, y in ((17, 6), (16, 7), (18, 7), (15, 8), (19, 8), (15, 9), (19, 9), (16, 10), (18, 10),
                 (13, 11), (14, 11), (21, 11), (20, 11), (12, 12), (12, 13), (22, 12), (22, 13),
                 (13, 14), (14, 14), (21, 14), (20, 14), (15, 14), (19, 14), (16, 15), (17, 15), (18, 15),
                 (15, 12), (19, 12), (16, 13), (18, 13), (17, 11)):
        d.point((x, y), fill=g)
    d.point((17, 9), fill=hx("2e5a3e"))


def address(d, im):
    """A small torn scrap of notepaper, creased where it was folded, with a scrawled pencil address."""
    d.polygon([(4, 9), (25, 4), (28, 14), (26, 15), (24, 14), (21, 16), (18, 15), (15, 17), (12, 16), (9, 18),
               (7, 18)], fill=hx("ece2c4"))
    d.polygon([(4, 9), (25, 4), (26, 8), (5, 13)], fill=hx("f6eed6"))
    d.line([(5, 13), (26, 8)], fill=hx("c4b48c"))
    d.polygon([(25, 4), (28, 14), (26, 8)], fill=hx("d4c6a0"))
    ink = hx("2e2a44")
    d.line([(7, 10), (8, 9), (9, 10), (11, 9), (12, 9), (13, 8)], fill=ink)
    d.line([(15, 8), (16, 7), (17, 8), (19, 6), (20, 7), (22, 6)], fill=ink)
    d.line([(8, 15), (9, 14), (11, 14), (12, 13), (14, 13)], fill=ink)
    d.line([(16, 12), (17, 11), (19, 12), (20, 11), (23, 10)], fill=ink)


def invitation(d, im):
    """A black invitation card edged in gold, the endless knot embossed in the middle."""
    d.polygon([(3, 5), (28, 3), (29, 19), (4, 21)], fill=hx("1a1620"))
    d.polygon([(5, 7), (26, 5), (27, 17), (6, 19)], outline=hx("c8a050"))
    g = hx("e8c060")
    d.arc([11, 7, 17, 13], 90, 360, fill=g)
    d.arc([15, 7, 21, 13], 180, 90, fill=g)
    d.arc([13, 10, 19, 16], 270, 180, fill=g)


def mask(d, im):
    """A white full-face mask: plain porcelain, two almond eye holes and a closed, painted mouth."""
    d.ellipse([9, 1, 23, 22], fill=hx("ece8e0"))
    d.chord([9, 1, 23, 22], 300, 60, fill=hx("d4cec4"))
    d.polygon([(11, 9), (14, 8), (15, 10), (12, 11)], fill=hx("141016"))
    d.polygon([(21, 9), (18, 8), (17, 10), (20, 11)], fill=hx("141016"))
    d.line([(16, 11), (16, 14)], fill=hx("c4beb4"))
    d.line([(14, 17), (18, 17)], fill=hx("8a3a3a"))
    d.line([(9, 9), (5, 8)], fill=hx("2a2028"))
    d.line([(23, 9), (27, 8)], fill=hx("2a2028"))


def cloak(d, im):
    """A long black hooded cloak, folded over on itself."""
    d.polygon([(10, 2), (22, 2), (27, 21), (5, 21)], fill=hx("16141a"))
    d.ellipse([11, 1, 21, 9], fill=hx("221e28"))
    d.ellipse([13, 3, 19, 8], fill=hx("0a080c"))
    for x in (10, 15, 20):
        d.line([(x + 1, 9), (x - 1 + (x - 15) // 3, 20)], fill=hx("2a2632"))
    d.line([(5, 21), (27, 21)], fill=hx("2e2a36"))


def build():
    for name, fn in (("photo", photo), ("dollar", dollar), ("matchbook", matchbook), ("crowbar", crowbar),
                     ("journal", journal), ("key", key), ("diary", diary), ("ledger", ledger), ("map", map_),
                     ("evidence", evidence), ("suitcase_key", suitcase_key), ("revolver", revolver),
                     ("lockpick", lockpick), ("combination", combination), ("brass_box", brass_box),
                     ("card", card), ("mirror", mirror), ("book", book), ("address", address),
                     ("invitation", invitation), ("mask", mask), ("cloak", cloak)):
        save(_icon(fn), "items", f"{name}.png")
