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


PHONE, PHONE_M, PHONE_L, NICKEL = hx("121016"), hx("2c2a34"), hx("5a5664"), hx("c4c4cc")
NICKEL_D, CORD, CORD_L, CARD = hx("7c7c88"), hx("2a1e18"), hx("5a4434"), hx("e8dcc0")


def braided_cord(d, pts, step=2):
    """A cloth-braided cord: dark brown, flecked lighter every few pixels along its length."""
    d.line(pts, fill=CORD)
    n = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        k = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(int(k)):
            if n % step == 0:
                d.point((round(x0 + (x1 - x0) * i / k), round(y0 + (y1 - y0) * i / k)), fill=CORD_L)
            n += 1


def candlestick_phone(img, x, y, dial=False):
    """A black Western Electric candlestick telephone standing with its foot centred on (x, y): a flared, stepped
    foot, a column ringed in nickel, the mouthpiece trumpet turned to the room with its nickel rim and dark throat,
    and the receiver hanging by its bell on the nickel switchhook, its braided cord looping down to the foot.
    Without a dial (a hotel extension: lifting the receiver rings the switchboard) the foot carries a number card;
    dial=True puts a nickel finger wheel on the foot's face instead, for a private line."""
    d = ImageDraw.Draw(img)
    shadow(img, "ellipse", [x - 7, y - 2, x + 7, y + 2], 0.45, 1)
    # the receiver cord, from the end of the receiver down and round into the foot
    braided_cord(d, [(x + 7, y - 6), (x + 8, y - 3), (x + 7, y), (x + 4, y)])
    # flared foot, stepped dome
    if dial:
        d.ellipse([x - 6, y - 3, x + 6, y + 2], fill=PHONE)
        d.line([(x - 5, y - 3), (x + 2, y - 3)], fill=PHONE_L)
    else:
        d.ellipse([x - 5, y - 3, x + 5, y + 1], fill=PHONE)
        d.line([(x - 4, y - 3), (x + 1, y - 3)], fill=PHONE_L)
    d.point((x - 5, y - 1), fill=PHONE_M)
    d.ellipse([x - 3, y - 5, x + 3, y - 2], fill=PHONE)
    d.line([(x - 2, y - 5), (x, y - 5)], fill=PHONE_M)
    if dial:
        # the finger wheel on the foot's face: a nickel ring, its holes, the white number card in the hub
        d.ellipse([x - 3, y - 2, x + 2, y + 2], fill=NICKEL_D)
        d.line([(x - 2, y - 2), (x + 1, y - 2)], fill=NICKEL)
        for hx_, hy_ in ((x - 2, y - 1), (x - 2, y + 1), (x + 1, y + 1)):
            d.point((hx_, hy_), fill=PHONE)
        d.point((x - 1, y), fill=CARD)
        d.point((x + 2, y - 1), fill=NICKEL)
    else:
        # the number card on its face
        d.line([(x - 1, y), (x + 1, y)], fill=CARD)
        d.point((x, y), fill=hx("8a2020"))
    # column with a nickel collar at the foot and another under the mouthpiece
    d.rectangle([x, y - 17, x + 1, y - 6], fill=PHONE)
    d.line([(x, y - 16), (x, y - 7)], fill=PHONE_L)
    d.line([(x - 1, y - 6), (x + 2, y - 6)], fill=NICKEL_D)
    d.point((x - 1, y - 6), fill=NICKEL)
    d.line([(x, y - 17), (x + 1, y - 17)], fill=NICKEL)
    # the mouthpiece: a short neck, the trumpet flaring to the room, nickel rim round a dark throat
    d.polygon([(x - 1, y - 18), (x + 2, y - 18), (x + 3, y - 20), (x - 2, y - 20)], fill=PHONE)
    d.point((x - 1, y - 19), fill=PHONE_L)
    d.ellipse([x - 3, y - 23, x + 4, y - 19], fill=NICKEL_D)
    d.line([(x - 2, y - 23), (x + 1, y - 23)], fill=NICKEL)
    d.ellipse([x - 2, y - 22, x + 3, y - 20], fill=hx("060608"))
    d.point((x - 1, y - 21), fill=PHONE_M)
    # the nickel switchhook out of the column's side, its fork cradling the receiver
    d.line([(x + 2, y - 14), (x + 4, y - 14)], fill=NICKEL)
    d.point((x + 4, y - 15), fill=NICKEL)
    d.point((x + 7, y - 15), fill=NICKEL_D)
    # the receiver hanging from the fork by its bell: earpiece cup at the top, ribbed handle below
    d.ellipse([x + 3, y - 17, x + 8, y - 14], fill=PHONE)
    d.line([(x + 4, y - 17), (x + 6, y - 17)], fill=PHONE_L)
    d.rectangle([x + 5, y - 14, x + 6, y - 6], fill=PHONE)
    d.line([(x + 5, y - 13), (x + 5, y - 7)], fill=PHONE_L)
    for ry in (y - 12, y - 10, y - 8):
        d.point((x + 6, ry), fill=PHONE_M)
    d.line([(x + 5, y - 14), (x + 6, y - 14)], fill=NICKEL_D)
    d.line([(x + 5, y - 5), (x + 6, y - 5)], fill=PHONE_M)


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
