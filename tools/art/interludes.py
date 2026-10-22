"""Item icons for Eleanor's interlude puzzles: Room 507's brass box (17) and the Club dressing room's face (18)."""
from .common import hx, save
from .items import _icon, CARD_STOCK, CARD_GILT, CARD_CURL

BRASS = hx("c89a3a")
BRASS_D = hx("7a5a1c")
BRASS_L = hx("f0cc70")
PAPER = hx("ece4d0")
INK = hx("3a3a6a")
RED = hx("c82a2a")
GOLD = hx("d8b050")


# ============================================================================================ 17 - Room 507

def eleanor_box(d, im):
    # the brass box with its lid thrown back, the card, matchbook and bluing showing inside
    d.polygon([(6, 3), (26, 3), (24, 10), (8, 10)], fill=BRASS_D)
    d.line([(9, 6), (23, 6)], fill=BRASS)
    d.rectangle([5, 10, 27, 21], fill=BRASS)
    d.rectangle([7, 11, 25, 13], fill=hx("3a2a18"))
    # the calling card Micah finds later (items.card), standing up in the box: white stock, a gilt inner rule, a pink
    # curlicue and the two dark letters
    d.rectangle([6, 5, 14, 12], fill=CARD_STOCK)
    d.line([(14, 5), (14, 12)], fill=hx("c8c0b8"))
    d.rectangle([7, 6, 13, 11], outline=CARD_GILT)
    for x, y in ((9, 8), (10, 7), (11, 8)):
        d.point((x, y), fill=CARD_CURL)
    d.line([(9, 9), (9, 10)], fill=hx("3a2a22"))
    d.line([(11, 9), (11, 10)], fill=hx("3a2a22"))
    d.rectangle([15, 9, 18, 12], fill=hx("1e2a6a"))
    d.rectangle([20, 8, 23, 12], fill=hx("1e3aa8"))
    d.line([(5, 14), (27, 14)], fill=BRASS_L)
    for x in (10, 16, 22):
        d.ellipse([x - 2, 16, x + 2, 19], outline=BRASS_D)


def pellet(d, im):
    # the bare paper flower, folded tight
    d.ellipse([9, 5, 23, 19], fill=hx("e8a0b0"))
    d.ellipse([12, 7, 19, 12], fill=hx("f8d0d8"))
    for x in (12, 16, 20):
        d.line([(x, 6), (x - 1, 18)], fill=hx("c07088"))


def riddle_scrap(d, im):
    # a torn scrap of hotel stationery, three lines in her hand
    d.polygon([(3, 6), (27, 4), (29, 9), (27, 13), (29, 19), (5, 21), (3, 15)], fill=PAPER)
    d.line([(4, 7), (26, 5)], fill=hx("8a6a3a"))
    for y, x1 in ((10, 24), (14, 22), (18, 17)):
        d.line([(7, y), (x1, y - 1)], fill=INK)


def eleanor_slip(d, im):
    # a blank slip of hotel paper, the Aurelian's gilt rule along the top: the same paper as Micah's combination slip
    d.polygon([(4, 5), (27, 3), (28, 20), (5, 21)], fill=hx("ece4d0"))
    d.line([(5, 7), (27, 5)], fill=hx("b8a060"))


def eleanor_key(d, im):
    # a small brass drawer key, the bow cut like a lily
    d.ellipse([4, 7, 13, 16], fill=BRASS)
    d.ellipse([7, 10, 10, 13], fill=(0, 0, 0, 0))
    d.point((8, 7), fill=BRASS_L)
    d.rectangle([12, 11, 26, 12], fill=BRASS)
    d.line([(13, 11), (25, 11)], fill=BRASS_L)
    d.rectangle([21, 13, 22, 16], fill=BRASS_D)
    d.rectangle([24, 13, 26, 15], fill=BRASS_D)


def red_thread(d, im):
    # a loose loop of red silk thread
    d.arc([4, 4, 22, 20], 20, 340, fill=RED, width=2)
    d.arc([10, 8, 28, 22], 200, 160, fill=hx("e04848"))
    d.line([(22, 12), (29, 5)], fill=RED)


# ============================================================================================ 18 - Club dressing room

def compact(d, im):
    # a gold compact, open, the cake of face powder inside, no puff
    d.ellipse([3, 3, 17, 13], fill=GOLD)
    d.ellipse([5, 5, 15, 11], fill=hx("a8a8b0"))
    d.ellipse([12, 9, 28, 21], fill=GOLD)
    d.ellipse([14, 11, 26, 19], fill=hx("f0d8c4"))
    d.ellipse([16, 12, 21, 15], fill=hx("fff0e4"))


def lipstick(d, im):
    # a gold tube, the red standing up out of it
    d.rectangle([12, 13, 20, 22], fill=GOLD)
    d.line([(12, 15), (20, 15)], fill=hx("8a6a20"))
    d.rectangle([13, 6, 19, 12], fill=hx("c8a040"))
    d.polygon([(14, 6), (18, 6), (18, 1), (14, 3)], fill=hx("b0182a"))
    d.line([(15, 3), (15, 6)], fill=hx("e04050"))


def _puff(d, fill, speck):
    d.ellipse([5, 5, 27, 21], fill=fill)
    for x, y in ((10, 9), (15, 7), (21, 10), (12, 15), (19, 16), (24, 13), (8, 13)):
        d.point((x, y), fill=speck)
    d.ellipse([13, 10, 19, 15], fill=hx("e8a0b0"))


def puff(d, im):
    # a swansdown puff with its pink ribbon
    _puff(d, hx("f4f0ec"), hx("d0ccc8"))


def puff_powdered(d, im):
    # the same puff, caked in face powder
    _puff(d, hx("f0d8c4"), hx("fff4ea"))
    d.point((26, 6), fill=hx("f0d8c4"))
    d.point((28, 8), fill=hx("f0d8c4"))


def hairpin(d, im):
    # a black bobby pin, open at the end
    d.line([(4, 18), (27, 6)], fill=hx("2a2a30"), width=2)
    d.line([(6, 21), (27, 9)], fill=hx("3a3a44"), width=2)
    d.arc([24, 5, 30, 11], 270, 90, fill=hx("2a2a30"), width=2)
    d.line([(9, 17), (12, 18)], fill=hx("6a6a74"))


ICONS = (("eleanor_box", eleanor_box), ("pellet", pellet), ("riddle_scrap", riddle_scrap),
         ("red_thread", red_thread), ("eleanor_slip", eleanor_slip), ("eleanor_key", eleanor_key), ("compact", compact), ("lipstick", lipstick), ("puff", puff),
         ("puff_powdered", puff_powdered), ("hairpin", hairpin))


def build():
    for name, fn in ICONS:
        save(_icon(fn), "items", f"{name}.png")
