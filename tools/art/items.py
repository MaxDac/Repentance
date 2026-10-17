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
    d.ellipse([10, 5, 17, 12], outline=hx("2a2a32"))
    d.rectangle([12, 7, 15, 10], fill=hx("2e2e36"))
    d.arc([16, 10, 22, 16], 0, 180, fill=hx("3a3a42"))
    d.point((5, 6), fill=hx("c8c8d0"))
    d.line([(6, 8), (8, 8)], fill=hx("7a7a84"))


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
    d.line([(8, 16), (22, 15)], fill=hx("6a5a4a"))
    d.text((9, 8), "MJ", fill=hx("3a2a22"))


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
    """A white Venetian Bauta half-mask, face on: a flat brow, a heavy carved brow ridge over almond eye holes and a
    long nose jutting down past the plate's square lower edge. The mouth and chin are left bare. Black ribbon ties
    trail off the sides."""
    ivory, shade, deep, hi, hole = hx("ece4cc"), hx("cfc4a6"), hx("a89c80"), hx("fbf7ec"), hx("141016")
    d.line([(8, 7), (2, 6)], fill=hx("16141a"), width=2)
    d.line([(24, 7), (30, 6)], fill=hx("16141a"), width=2)
    d.polygon([(11, 1), (21, 1), (24, 4), (25, 9), (24, 14), (21, 16), (11, 16), (8, 14), (7, 9), (8, 4)],
              fill=ivory)
    d.polygon([(21, 1), (24, 4), (25, 9), (24, 14), (21, 16), (20, 10)], fill=shade)  # the cheek turning away
    d.line([(11, 2), (20, 2)], fill=hi)
    d.line([(9, 5), (14, 6)], fill=deep)  # the heavy brow ridge, dipping to the bridge of the nose
    d.line([(18, 6), (23, 5)], fill=deep)
    d.polygon([(10, 8), (12, 7), (14, 8), (13, 9), (11, 9)], fill=hole)
    d.polygon([(18, 8), (20, 7), (22, 8), (21, 9), (19, 9)], fill=hole)
    d.line([(9, 15), (23, 15)], fill=shade)  # the square lower edge
    d.polygon([(15, 6), (17, 6), (18, 14), (19, 19), (13, 19), (14, 14)], fill=ivory)  # the long nose
    d.polygon([(17, 6), (18, 14), (19, 19), (17, 19)], fill=shade)
    d.line([(15, 6), (14, 14)], fill=hi)
    d.line([(14, 19), (18, 19)], fill=deep)  # the nose's underside

def cloak(d, im):
    """A long black hooded cloak, folded over on itself."""
    d.polygon([(10, 2), (22, 2), (27, 21), (5, 21)], fill=hx("16141a"))
    d.ellipse([11, 1, 21, 9], fill=hx("221e28"))
    d.ellipse([13, 3, 19, 8], fill=hx("0a080c"))
    for x in (10, 15, 20):
        d.line([(x + 1, 9), (x - 1 + (x - 15) // 3, 20)], fill=hx("2a2632"))
    d.line([(5, 21), (27, 21)], fill=hx("2e2a36"))

def kitchen_key(d, im):
    """A big black iron door key, the kind that lives on a lintel."""
    d.ellipse([2, 6, 12, 16], fill=hx("3a3a3e"))
    d.ellipse([5, 9, 9, 13], fill=(0, 0, 0, 0))
    d.rectangle([11, 10, 28, 12], fill=hx("3a3a3e"))
    d.rectangle([22, 12, 25, 18], fill=hx("3a3a3e"))
    d.rectangle([26, 12, 28, 16], fill=hx("3a3a3e"))
    d.line([(12, 10), (27, 10)], fill=hx("6a6a70"))


def documents(d, im):
    """A buff cardboard folder tied with red tape, papers sticking out."""
    d.polygon([(4, 6), (27, 4), (28, 20), (5, 21)], fill=hx("c8a868"))
    d.polygon([(7, 3), (25, 2), (26, 6), (7, 7)], fill=hx("ece4d0"))
    d.line([(9, 4), (22, 3)], fill=hx("6a6a6a"))
    d.polygon([(6, 8), (12, 7), (13, 12), (7, 13)], fill=hx("f4efe2"))
    d.line([(16, 5), (17, 21)], fill=hx("a02020"), width=2)
    d.line([(4, 13), (28, 12)], fill=hx("a02020"))
    d.text((7, 14), "HS", fill=hx("4a3a1a"))


def faith_ring(d, im):
    d.ellipse([7, 5, 25, 19], outline=hx("d8b050"), width=4)
    d.arc([7, 5, 25, 19], 190, 285, fill=hx("fff0b0"), width=2)


def cross(d, im):
    d.arc([6, 1, 26, 16], 0, 180, fill=hx("b8c0c8"))
    d.rectangle([15, 9, 18, 22], fill=hx("c8d0d8"))
    d.rectangle([11, 13, 22, 16], fill=hx("c8d0d8"))
    d.line([(16, 10), (16, 21)], fill=hx("f0f0e8"))


def notepad(d, im):
    """Micah's reporter's pad: cream pages on a card back, a spiral binding across the top, and a pencil."""
    d.polygon([(6, 5), (23, 4), (24, 22), (7, 22)], fill=hx("6a5038"))
    d.polygon([(7, 5), (22, 4), (23, 21), (8, 21)], fill=hx("e8dcb8"))
    for y in (9, 12, 15, 18):
        d.line([(9, y), (21, y - 1)], fill=hx("9aa4b8"))
    d.line([(10, 8), (18, 7)], fill=hx("3a3028"))
    d.line([(10, 11), (16, 10)], fill=hx("3a3028"))
    for x in range(9, 23, 3):
        d.ellipse([x - 1, 2, x + 1, 6], outline=hx("b8c0c8"))
    d.line([(20, 21), (29, 9)], fill=hx("d8a838"), width=2)
    d.line([(29, 9), (30, 8)], fill=hx("e0b8a0"), width=2)
    d.point((19, 22), fill=hx("2a2018"))


def lighter(d, im):
    """Micah's brass trench lighter, lid flipped open on its hinge and the flame up."""
    d.rectangle([11, 11, 21, 22], fill=hx("b88a38"))
    d.rectangle([11, 11, 13, 22], fill=hx("e0b860"))
    d.line([(11, 14), (21, 14)], fill=hx("7a5a20"))
    d.rectangle([20, 4, 24, 11], fill=hx("a07a30"))
    d.rectangle([13, 8, 18, 11], fill=hx("8a8a8e"))
    for x in (14, 16):
        d.point((x, 9), fill=hx("3a3a3e"))
    d.ellipse([13, 1, 18, 9], fill=hx("e88a28"))
    d.ellipse([14, 4, 17, 8], fill=hx("fff0a0"))


def umbrella(d, im):
    """A gentleman's black umbrella, furled and strapped, on a curved wooden crook."""
    ax, ay, bx, by = 5.0, 20.0, 19.0, 8.0  # canopy from the ferrule end to the rib tips by the shaft
    ux, uy = (bx - ax) / 14.0, (by - ay) / 14.0
    nx, ny = -uy * 0.76, ux * 0.76  # perpendicular, scaled to unit length
    pts_l, pts_r = [], []
    for i in range(15):
        t = i / 14.0
        w = 0.6 + 3.2 * t ** 0.8 if t < 0.88 else 3.4 - (t - 0.88) * 14
        cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
        pts_l.append((cx + nx * w, cy + ny * w))
        pts_r.append((cx - nx * w, cy - ny * w))
    d.polygon(pts_l + pts_r[::-1], fill=hx("23242c"))
    # folds of the furled silk catching the light
    d.line([(7, 18), (17, 8)], fill=hx("4a4e5e"))
    d.line([(9, 18), (18, 11)], fill=hx("363844"))
    d.line([(6, 18), (14, 9)], fill=hx("3a3c4a"))
    d.point((12, 12), fill=hx("6a7084"))
    d.point((15, 9), fill=hx("6a7084"))
    # the strap and its button
    d.line([(11, 11), (15, 15)], fill=hx("121218"), width=2)
    d.point((13, 13), fill=hx("9a9aa4"))
    # steel ferrule at the tip
    d.line([(2, 23), (5, 20)], fill=hx("8a8c94"), width=1)
    d.point((2, 23), fill=hx("c8cad0"))
    # the wooden shaft and crook handle
    d.line([(19, 8), (23, 4)], fill=hx("6a4220"), width=2)
    d.arc([21, 0, 31, 10], 160, 400, fill=hx("8a5a2e"), width=3)
    d.arc([21, 0, 31, 10], 190, 290, fill=hx("c08a50"))
    d.point((29, 8), fill=hx("5a3418"))


def build():
    for name, fn in (("photo", photo), ("dollar", dollar), ("matchbook", matchbook), ("crowbar", crowbar),
                     ("journal", journal),
                     ("suitcase_key", suitcase_key), ("revolver", revolver),
                     ("lockpick", lockpick), ("combination", combination), ("brass_box", brass_box),
                     ("card", card), ("mirror", mirror), ("book", book), ("address", address),
                     ("invitation", invitation), ("mask", mask), ("cloak", cloak),
                     ("kitchen_key", kitchen_key), ("documents", documents),
                     ("faith_ring", faith_ring), ("cross", cross), ("notepad", notepad), ("lighter", lighter),
                     ("umbrella", umbrella)):
        save(_icon(fn), "items", f"{name}.png")
