"""Inventory icons (32x24)."""
from PIL import Image, ImageDraw
from .common import hx, save, text
from .sprites import _shade, _outline


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


def build():
    for name, fn in (("photo", photo), ("dollar", dollar), ("matchbook", matchbook)):
        save(_icon(fn), "items", f"{name}.png")
