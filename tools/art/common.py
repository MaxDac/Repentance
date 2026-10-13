"""Shared painting helpers for the procedural placeholder art."""
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
import math
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ART = os.path.join(ROOT, "assets", "art")
FONT = os.path.join(ROOT, "assets", "fonts", "Silkscreen-Regular.ttf")
W, H = 480, 240  # painting area of the 1920s rooms (floor extended towards the camera)
TOP = 30  # ceiling band painted above them; rooms are W x (H + TOP) = 480x270, the full screen
FULL_H = H + TOP
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def hx(s, a=None):
    s = s.lstrip("#")
    c = (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    return c if a is None else c + (a,)


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def mul(c, f):
    return tuple(clamp(c[i] * f) for i in range(3)) + tuple(c[3:])


def vgrad(img, box, c1, c2):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        d.line([(x0, y), (x1, y)], fill=mix(c1, c2, (y - y0) / max(1, y1 - y0)))


def hgrad(img, box, c1, c2):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    for x in range(x0, x1 + 1):
        d.line([(x, y0), (x, y1)], fill=mix(c1, c2, (x - x0) / max(1, x1 - x0)))


def noise(img, box, amp, seed=0):
    rnd = random.Random(seed)
    px = img.load()
    x0, y0, x1, y1 = box
    for y in range(max(0, y0), min(img.height - 1, y1) + 1):
        for x in range(max(0, x0), min(img.width - 1, x1) + 1):
            n = rnd.randint(-amp, amp)
            c = px[x, y]
            px[x, y] = (clamp(c[0] + n), clamp(c[1] + n), clamp(c[2] + n)) + tuple(c[3:])


def _mask(size, shape, pts, k, blur):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    if shape == "ellipse":
        d.ellipse(pts, fill=int(255 * k))
    elif shape == "rect":
        d.rectangle(pts, fill=int(255 * k))
    else:
        d.polygon(pts, fill=int(255 * k))
    if blur:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return m


def light(img, shape, pts, col, k=0.6, blur=10):
    """Screen-blends a soft coloured light into the image."""
    m = _mask(img.size, shape, pts, k, blur)
    lit = ImageChops.screen(img, Image.new("RGB", img.size, col))
    img.paste(Image.composite(lit, img, m))


def shadow(img, shape, pts, k=0.5, blur=6, tint=(0, 0, 0)):
    """Multiplies a soft (optionally tinted) shadow into the image."""
    m = _mask(img.size, shape, pts, k, blur)
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, tint))
    img.paste(Image.composite(dark, img, m))


def vignette(img, k=0.6, tint=(12, 10, 30), blur=40):
    m = Image.new("L", img.size, int(255 * k))
    w, h = img.size
    ImageDraw.Draw(m).ellipse([-w * 0.12, -h * 0.4, w * 1.12, h * 1.3], fill=0)
    m = m.filter(ImageFilter.GaussianBlur(blur))
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, tint))
    img.paste(Image.composite(dark, img, m))


def palette_of(img, n=128):
    q = img.quantize(colors=n, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[: n * 3]
    return [tuple(pal[i:i + 3]) for i in range(0, len(pal), 3)]


def pixelize(img, pal=None, n=128, spread=12):
    """Reduces to a limited palette with ordered (Bayer) dithering - the classic VGA look."""
    pal = pal or palette_of(img, n)
    src = img.load()
    out = Image.new("RGB", img.size)
    dst = out.load()
    cache = {}
    for y in range(img.height):
        row = BAYER[y % 4]
        for x in range(img.width):
            r, g, b = src[x, y][:3]
            o = (row[x % 4] - 7.5) * spread / 16
            key = (clamp(r + o) >> 2, clamp(g + o) >> 2, clamp(b + o) >> 2)
            c = cache.get(key)
            if c is None:
                rr, gg, bb = key[0] * 4 + 2, key[1] * 4 + 2, key[2] * 4 + 2
                c = min(pal, key=lambda p: 3 * (p[0] - rr) ** 2 + 4 * (p[1] - gg) ** 2 + 2 * (p[2] - bb) ** 2)
                cache[key] = c
            dst[x, y] = c
    return out


def text(img, xy, s, col, size=8, mirror=False, anchor="mm"):
    font = ImageFont.truetype(FONT, size)
    layer = Image.new("L", img.size, 0)
    ImageDraw.Draw(layer).text(xy, s, fill=255, font=font, anchor=anchor)
    if mirror:
        x = int(xy[0])
        box = (x - 60, 0, x + 60, img.height)
        reg = layer.crop(box).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        layer.paste(reg, box)
    layer = layer.point(lambda v: 255 if v > 100 else 0)
    img.paste(Image.new(img.mode, img.size, col), (0, 0), layer)


def city(img, box, seed=7, lit=0.3, haze=hx("3a2a4a"), rain=True):
    """Night skyline with lit windows, deco spires and (unless it is animated in-game) painted rain."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    vgrad(img, (x0, y0, x1, y1), hx("070a18"), haze)
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        bw, bh = rnd.randint(8, 20), rnd.randint(int((y1 - y0) * 0.3), int((y1 - y0) * 0.6))
        d.rectangle([x, y1 - bh, min(x1, x + bw), y1], fill=hx("161a2e"))
        x += bw
    x = x0 - 4
    while x < x1:
        bw, bh = rnd.randint(12, 26), rnd.randint(int((y1 - y0) * 0.35), int((y1 - y0) * 0.85))
        top = y1 - bh
        col = hx("0a0c16")
        d.rectangle([max(x0, x), top, min(x1, x + bw), y1], fill=col)
        if rnd.random() < 0.35:
            d.rectangle([max(x0, x + 3), top - 4, min(x1, x + bw - 3), top], fill=col)
            d.rectangle([max(x0, x + 6), top - 8, min(x1, x + bw - 6), top - 4], fill=col)
            cx = x + bw // 2
            if rnd.random() < 0.6 and x0 <= cx <= x1:
                d.line([(cx, top - 16), (cx, top - 8)], fill=col)
                d.point((cx, top - 17), fill=hx("ff4040"))
        for wy in range(top + 3, y1 - 1, 4):
            for wx in range(x + 2, x + bw - 1, 3):
                if x0 <= wx <= x1 and rnd.random() < lit:
                    d.point((wx, wy), fill=rnd.choice([hx("e8c060"), hx("d8a040"), hx("f0e0a0")]))
        x += bw + rnd.randint(0, 3)
    if not rain:
        return
    for _ in range(int((x1 - x0) * (y1 - y0) / 60)):
        rx, ry = rnd.randint(x0 + 1, x1), rnd.randint(y0, y1 - 4)
        d.line([(rx, ry), (rx - 1, ry + 3)], fill=hx("4a5a7a"))


def tall(img, band):
    """Places a W x H room painting below a TOP-pixel ceiling band painted by band(canvas)."""
    out = Image.new("RGB", (W, FULL_H))
    out.paste(img, (0, TOP))
    band(out)
    return out


def save(img, *parts):
    path = os.path.join(ART, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("wrote", os.path.relpath(path, ROOT))


def cut(img, mask):
    """RGBA copy of img visible only where mask is set (foreground layers)."""
    out = img.convert("RGBA")
    out.putalpha(mask)
    return out


def frieze(d, y0, y1, bg, fg, x0=0, x1=W - 1, step=10):
    d.rectangle([x0, y0, x1, y1], fill=bg)
    for x in range(x0, x1, step):
        d.line([(x, y1 - 1), (x + step // 2, y0 + 1), (x + step, y1 - 1)], fill=fg)


def sunburst(d, cx, cy, r, n, c1, c2, start=math.pi, end=2 * math.pi):
    for i in range(n):
        a0 = start + (end - start) * i / n
        a1 = start + (end - start) * (i + 1) / n
        d.polygon([(cx, cy), (cx + r * math.cos(a0), cy + r * math.sin(a0)),
                   (cx + r * math.cos(a1), cy + r * math.sin(a1))], fill=c1 if i % 2 else c2)


def floor_boards(img, y0, y1, vp, spacing, c1, c2, seam, seed=1):
    """Perspective wooden floor converging on vanishing point vp."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    vx, vy = vp

    def xat(xb, y):
        return vx + (xb - vx) * (y - vy) / (y1 - vy)

    for i in range(-40, 41):
        xa, xb = vx + i * spacing, vx + (i + 1) * spacing
        d.polygon([(xat(xa, y0), y0), (xat(xb, y0), y0), (xb, y1), (xa, y1)], fill=mix(c1, c2, rnd.random()))
        d.line([(xat(xa, y0), y0), (xa, y1)], fill=seam)
    y, step = float(y0), 3.0
    while y < y1:
        d.line([(0, int(y)), (img.width, int(y))], fill=mix(seam, c1, 0.4))
        y += step
        step *= 1.25
