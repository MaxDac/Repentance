"""Title card and UI panel background."""
from PIL import Image, ImageDraw
from .common import hx, mix, vgrad, light, vignette, pixelize, text, city, save, sunburst, noise


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


def panel():
    img = Image.new("RGB", (480, 70))
    vgrad(img, (0, 0, 479, 69), hx("1a1420"), hx("0e0a12"))
    noise(img, (0, 0, 479, 69), 3, 4)
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (480, 0)], fill=hx("c8a040"))
    d.line([(0, 2), (480, 2)], fill=hx("6a5020"))
    for x in range(0, 480, 12):
        d.polygon([(x, 0), (x + 6, 3), (x + 12, 0)], fill=hx("8a6a28"))
    save(img, "ui", "panel.png")


def build():
    title()
    panel()
