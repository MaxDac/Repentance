"""Title card, verb-wheel icons, satchel, inventory chest and cursor."""
import math
from PIL import Image, ImageChops, ImageDraw
from .common import hx, mix, vgrad, light, shadow, vignette, palette_of, pixelize, text, city, save, sunburst, noise
from .iconfx import _shade, _outline

GOLD, GOLD_D = hx("d8b050"), hx("8a6a28")


def _building(d, box, col, lit_cols, rnd, lit=0.3, step=(3, 4)):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=col)
    for wy in range(y0 + 3, y1 - 1, step[1]):
        for wx in range(x0 + 2, x1 - 1, step[0]):
            if rnd.random() < lit:
                d.point((wx, wy), fill=rnd.choice(lit_cols))


def _skyline(img):
    """Chicago, 1927, from across the river: Tribune Tower and the floodlit Wrigley Building on the left, the
    Straus Building's beehive, the Chicago Temple spire and the Jewelers Building dome on the right."""
    import random
    d = ImageDraw.Draw(img)
    rnd = random.Random(1927)
    warm = [hx("e8c060"), hx("d8a040"), hx("f0e0a0")]
    bank = 198
    # far blocks, lost in the rain haze
    x = -6
    while x < 480:
        bw = rnd.randint(10, 22)
        _building(d, (x, rnd.randint(132, 168), x + bw, bank), hx("1c1a2c"), [hx("8a7050"), hx("6a5a48")], rnd, 0.18)
        x += bw - 2
    # nearer blocks
    x = 120
    while x < 372:
        bw = rnd.randint(14, 28)
        _building(d, (x, rnd.randint(140, 176), x + bw, bank), hx("0e0e1a"), warm, rnd, 0.26)
        x += bw + rnd.randint(-2, 2)

    # Tribune Tower: a slender gothic shaft, crown ringed with flying buttresses
    stone = hx("3a3640")
    _building(d, (24, 100, 46, bank), stone, warm, rnd, 0.3)
    d.rectangle([22, 86, 48, 100], fill=stone)
    d.rectangle([26, 78, 44, 86], fill=stone)
    for bx in (22, 27, 32, 37, 42, 47):
        d.line([(bx, 72), (bx, 86)], fill=stone)
        d.point((bx, 71), fill=hx("5a5460"))
    d.rectangle([28, 88, 42, 96], fill=hx("6a5030"))
    for bx in range(29, 42, 3):
        d.line([(bx, 89), (bx, 95)], fill=hx("c89040"))

    # Wrigley Building: white terra cotta, floodlit, clock tower at its south end
    white, white_d = hx("b8b2a4"), hx("8a8478")
    _building(d, (50, 132, 140, bank), white_d, [hx("f0d890"), hx("d8b060")], rnd, 0.35)
    d.rectangle([50, 128, 140, 132], fill=white)
    _building(d, (56, 96, 78, 132), white, [hx("f0d890")], rnd, 0.2)
    d.rectangle([58, 82, 76, 96], fill=white)
    d.ellipse([62, 84, 72, 94], fill=hx("f8f0d0"), outline=hx("6a6050"))
    d.line([(67, 89), (67, 86)], fill=hx("2a2418"))
    d.line([(67, 89), (69, 89)], fill=hx("2a2418"))
    d.rectangle([60, 74, 74, 82], fill=white)
    d.rectangle([62, 68, 72, 74], fill=white_d)
    for bx in (62, 66, 70):
        d.line([(bx, 68), (bx, 74)], fill=white)
    d.polygon([(63, 68), (71, 68), (67, 58)], fill=white)
    d.line([(67, 50), (67, 58)], fill=white_d)
    light(img, "polygon", [(46, 200), (90, 200), (78, 60), (56, 60)], hx("fff0c8"), 0.22, 6)

    # Straus Building: a stepped pyramid, the glass beehive on top lit blue
    dark = hx("14141f")
    _building(d, (366, 112, 404, bank), dark, warm, rnd, 0.32)
    for i, (w, y) in enumerate(((16, 104), (12, 96), (8, 90), (5, 85))):
        d.rectangle([385 - w, y, 385 + w, y + 8], fill=dark)
    d.ellipse([381, 78, 389, 87], fill=hx("4a7ad8"))
    d.point((385, 80), fill=hx("c0e0ff"))
    light(img, "ellipse", [374, 68, 396, 96], hx("3a6ae0"), 0.45, 6)

    # Chicago Temple: the Methodist church's gothic spire on top of an office tower
    _building(d, (414, 104, 440, bank), hx("1a1824"), warm, rnd, 0.3)
    d.rectangle([418, 92, 436, 104], fill=hx("1a1824"))
    d.polygon([(420, 92), (434, 92), (427, 50)], fill=hx("22202e"))
    for bx in (418, 436):
        d.polygon([(bx - 2, 92), (bx + 2, 92), (bx, 80)], fill=hx("22202e"))
    d.line([(427, 44), (427, 50)], fill=hx("22202e"))
    d.line([(425, 46), (429, 46)], fill=hx("22202e"))
    for wy in (66, 74, 82):
        d.point((427, wy), fill=hx("e8c060"))

    # Jewelers Building: a squat tower with a domed temple on top
    _building(d, (448, 124, 480, bank), hx("12121c"), warm, rnd, 0.3)
    d.rectangle([454, 112, 474, 124], fill=hx("12121c"))
    d.pieslice([456, 100, 472, 120], 180, 360, fill=hx("1c1c2a"))
    d.point((464, 99), fill=hx("ff4040"))
    # aircraft lights on the tall ones
    for px, py in ((35, 70), (67, 49), (427, 43)):
        d.point((px, py), fill=hx("ff4040"))

    # river wall and its lamps
    d.rectangle([0, bank, 479, bank + 7], fill=hx("1a1620"))
    d.line([(0, bank), (479, bank)], fill=hx("3a3440"))
    for lx in range(18, 480, 44):
        d.line([(lx, bank - 10), (lx, bank)], fill=hx("2a2630"))
        d.rectangle([lx - 1, bank - 13, lx + 1, bank - 11], fill=hx("f8e0a0"))
        light(img, "ellipse", [lx - 8, bank - 20, lx + 8, bank - 4], hx("f0c060"), 0.5, 4)


def _river(img, top):
    """Dark water reflecting the skyline, broken into wavering horizontal strokes."""
    import random
    rnd = random.Random(31)
    w, h = img.size
    src = img.crop((0, top - (h - top), w, top)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    water = Image.new("RGB", (w, h - top))
    vgrad(water, (0, 0, w - 1, h - top - 1), hx("0c0e1c"), hx("06070e"))
    sp, wp = src.load(), water.load()
    for y in range(h - top):
        fade = 0.55 * (1 - y / (h - top)) + 0.12
        shift = int(round(2.5 * math.sin(y * 0.9) + rnd.uniform(-1.5, 1.5)))
        for x in range(w):
            r, g, b = sp[min(w - 1, max(0, x + shift)), y]
            # only the lights carry onto the water
            k = fade if r + g + b > 300 else fade * 0.25
            wr, wg, wb = wp[x, y]
            wp[x, y] = (clamp_px(wr + r * k), clamp_px(wg + g * k), clamp_px(wb + b * k))
    d = ImageDraw.Draw(water)
    for _ in range(140):
        x, y = rnd.randint(0, w - 1), rnd.randint(2, h - top - 1)
        d.line([(x, y), (x + rnd.randint(3, 10), y)], fill=hx("1a2236"))
    img.paste(water, (0, top))


def clamp_px(v):
    return 255 if v > 255 else int(v)


TITLE_PLATE = (112, 64, 368, 118)
# ziggurat plate: base, middle step, top step (x0, x1, top y); all share the base's bottom edge
_PLATE_STEPS = ((112, 368, 80), (176, 304, 72), (208, 272, 64))
_GW, _GH = 12, 22  # deco letter cell


def _glyph(ch):
    """Condensed Broadway-style capitals: heavy stems, hairline bars, high waist. Returns 22 rows of '#'/'.'."""
    if ch == "E":
        rows = ["#" * 12] * 2 + ["####" + "." * 8] * 5 + ["#########..."] + ["####" + "." * 8] * 12 + ["#" * 12] * 2
    elif ch in "PR":
        bowl = ["##########..", "###########."] + ["####....####"] * 4 + ["###########.", "##########.."]
        if ch == "P":
            rows = bowl + ["####" + "." * 8] * 14
        else:
            rows = bowl
            for i in range(14):
                s = 4 + round(4 * i / 13)
                r = ["#" if x < 4 or s <= x < s + 4 else "." for x in range(12)]
                rows.append("".join(r))
    elif ch == "N":
        rows = []
        for y in range(22):
            s = round(2 + 6 * y / 21)
            rows.append("".join("#" if x < 2 or x >= 10 or s <= x < s + 4 else "." for x in range(12)))
    elif ch == "T":
        rows = ["#" * 12] * 2 + ["....####...."] * 20
    elif ch == "A":
        rows = []
        for y in range(22):
            left, right = round(5 - 5 * y / 21), round(6 + 5 * y / 21)
            r = ["."] * 12
            for x in range(left, left + 2):
                r[x] = "#"
            for x in range(max(left, right - 3), right + 1):
                r[x] = "#"
            if y == 14:
                for x in range(left, right + 1):
                    r[x] = "#"
            rows.append("".join(r))
    elif ch == "C":
        rows = (["..##########", ".###########"] + ["####......##"] * 2 + ["####" + "." * 8] * 14 +
                ["####......##"] * 2 + [".###########", "..##########"])
    else:
        raise ValueError(ch)
    assert len(rows) == _GH and all(len(r) == _GW for r in rows), ch
    return rows


_GOLD_ROWS = [hx("f8e8b0")] * 4 + [hx("f0d080")] * 4 + [hx("e0b850")] * 5 + [hx("c89838")] * 5 + [hx("a07028")] * 4


def _deco_word(img, s, cx, top, gap=6):
    width = len(s) * _GW + (len(s) - 1) * gap
    x0 = cx - width // 2
    px = img.load()
    for i, ch in enumerate(s):
        for y, row in enumerate(_glyph(ch)):
            for x, c in enumerate(row):
                if c == "#":
                    # a dark drop shadow, then the gold letter
                    sx, sy = x0 + i * (_GW + gap) + x, top + y
                    if px[sx + 1, sy + 1][3] == 255 and px[sx + 1, sy + 1][:3] == hx("0e0a10"):
                        px[sx + 1, sy + 1] = hx("2a1808", 255)
                    px[sx, sy] = _GOLD_ROWS[y] + (255,)
    return x0, x0 + width


def _plate_outline(inset):
    (bx0, bx1, by0), (mx0, mx1, my0), (tx0, tx1, ty0) = _PLATE_STEPS
    by1, i = TITLE_PLATE[3], inset
    return [(bx0 + i, by1 - i), (bx0 + i, by0 + i), (mx0 + i, by0 + i), (mx0 + i, my0 + i), (tx0 + i, my0 + i),
            (tx0 + i, ty0 + i), (tx1 - i, ty0 + i), (tx1 - i, my0 + i), (mx1 - i, my0 + i), (mx1 - i, by0 + i),
            (bx1 - i, by0 + i), (bx1 - i, by1 - i)]


def _title_plate():
    """Art deco nameplate drawn crisply over the pixelised background: stepped ziggurat, sunburst, speed lines."""
    plate = Image.new("RGBA", (480, 270))
    d = ImageDraw.Draw(plate)
    ink, gold, gold_d = hx("0e0a10", 255), hx("c8a040", 255), hx("6a5020", 255)
    d.polygon(_plate_outline(0), fill=ink, outline=gold)
    d.polygon(_plate_outline(3), outline=gold_d)
    # sunburst rising from behind the word into the top step
    cx, cy = 240, 87
    sunburst(d, cx, cy, 18, 14, hx("4a3818", 255), ink)
    d.arc([cx - 18, cy - 18, cx + 18, cy + 18], 180, 360, fill=gold_d)
    d.pieslice([cx - 5, cy - 5, cx + 5, cy + 5], 180, 360, fill=gold)
    d.rectangle([cx - 20, cy, cx + 20, cy + 1], fill=ink)
    w0, w1 = _deco_word(plate, "REPENTANCE", 240, 90)
    # streamline speed lines either side of the word
    for k, (y, n) in enumerate(((96, 22), (100, 16), (104, 10))):
        col = gold if k == 1 else gold_d
        d.line([(w0 - 6 - n, y), (w0 - 6, y)], fill=col)
        d.line([(w1 + 5, y), (w1 + 5 + n, y)], fill=col)
    # a hairline under the word
    d.line([(w0, 114), (w1 - 1, 114)], fill=gold_d)
    return plate


def _title_paint():
    img = Image.new("RGB", (480, 270))
    vgrad(img, (0, 0, 479, 200), hx("05060e"), hx("2e1e34"))
    for cx, cy, rx, ry in ((90, 30, 140, 14), (330, 18, 170, 12), (250, 52, 200, 10), (60, 64, 120, 8)):
        shadow(img, "ellipse", [cx - rx, cy - ry, cx + rx, cy + ry], 0.5, 8, hx("100c18"))
    light(img, "rect", [0, 150, 479, 200], hx("6a3a3a"), 0.3, 20)
    _skyline(img)
    _river(img, 206)
    d = ImageDraw.Draw(img)
    for lx in range(18, 480, 44):
        for y in range(208, 262, 3):
            k = 1 - (y - 208) / 54
            half = 1 + (y - 208) // 18
            d.line([(lx - half, y), (lx + half, y)], fill=mix(hx("0c0e1c"), hx("e8b860"), 0.75 * k))
    # Wrigley's piers and cornice catch the floodlights
    for px in range(52, 140, 6):
        d.line([(px, 134), (px, 196)], fill=hx("a29c90"))
    d.line([(50, 128), (140, 128)], fill=hx("e8e0cc"))
    # outline the Straus pyramid against the sky
    for w, y in ((16, 104), (12, 96), (8, 90), (5, 85)):
        d.line([(385 - w, y), (385 + w, y)], fill=hx("34345a"))
    light(img, "rect", list(TITLE_PLATE), hx("e0a040"), 0.2, 12)
    vignette(img, 0.7)
    return img


def title():
    """Background without rain (Hud animates it with a Rain node) and the deco plate drawn over the rain."""
    plain, plate = _title_paint(), _title_plate()
    # keep the window and lamp golds exact; median cut alone washes them towards white
    pal = palette_of(plain, 96) + [hx("e8c060"), hx("d8a040"), hx("f0e0a0"), hx("f8e0a0")]
    bg = pixelize(plain, pal)
    save(bg, "ui", "title.png")
    save(plate, "ui", "title_logo.png")


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
    """9x9 crosshair; the hotspot is the centre dot at (4, 4), so the click point is always visible."""
    im = Image.new("RGBA", (9, 9))
    light = {(4, 1), (4, 2), (4, 6), (4, 7), (1, 4), (2, 4), (6, 4), (7, 4), (4, 4)}
    for x, y in light:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (x + dx, y + dy) not in light:
                    im.putpixel((x + dx, y + dy), hx("101010") + (255,))
    for p in light:
        im.putpixel(p, hx("f0e8c8") + (255,))
    save(im, "ui", "cursor.png")


def _trinity_paths(cx, cy, a, ring, step=0.5):
    """Triquetra (one closed curve made of three half-circles meeting in three points) and an interlaced ring,
    as dense screen-space polylines."""
    r = a * math.sqrt(3)
    path = []
    for th in (90, 330, 210):  # A -> C -> B: the arcs join tip to tip
        ccx, ccy = a * math.cos(math.radians(th)), a * math.sin(math.radians(th))
        n = int(math.pi * r / step)
        for i in range(n):
            t = math.radians(th + 90) + math.pi * i / n
            path.append((cx + ccx + r * math.cos(t), cy - (ccy + r * math.sin(t))))
    n = int(2 * math.pi * ring / step)
    circle = [(cx + ring * math.cos(2 * math.pi * i / n), cy - ring * math.sin(2 * math.pi * i / n)) for i in range(n)]
    return [path, circle]


def _crossings(paths, gap=20):
    """Self/mutual crossings of closed polylines: list of (point, (comp, index), (comp, index))."""
    import numpy as np
    segs = []
    for ci, p in enumerate(paths):
        q = np.array(p)
        segs.append((ci, q, np.roll(q, -1, axis=0)))
    out = []
    for i, (ca, a0, a1) in enumerate(segs):
        for cb, b0, b1 in segs[i:]:
            for k in range(len(a0)):
                p, r = a0[k], a1[k] - a0[k]
                s = b1 - b0
                den = r[0] * s[:, 1] - r[1] * s[:, 0]
                qp = b0 - p
                with np.errstate(divide="ignore", invalid="ignore"):
                    t = (qp[:, 0] * s[:, 1] - qp[:, 1] * s[:, 0]) / den
                    u = (qp[:, 0] * r[1] - qp[:, 1] * r[0]) / den
                hit = np.nonzero((np.abs(den) > 1e-9) & (t >= 0) & (t < 1) & (u >= 0) & (u < 1))[0]
                for j in hit:
                    if ca == cb:
                        dd = abs(j - k)
                        if j <= k or min(dd, len(a0) - dd) < gap:
                            continue
                    pt = p + r * t[j]
                    if all(math.dist(pt, o[0]) > 3 for o in out):
                        out.append((tuple(pt), (ca, k), (cb, j)))
    return out


def triquetra():
    """Back of a small antique hand mirror: walnut set in a tarnished silver rim, with a triquetra interlaced
    with a ring painted on it in dried, blood-dark ink (480x270)."""
    import numpy as np
    import random
    w, h = 480, 270
    cx, cy, R = 240.0, 124.0, 116.0
    rim = 15.0
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    rnd = np.random.default_rng(27)
    L = np.array([-0.5, -0.62, 0.6])
    L /= np.linalg.norm(L)

    # dark cloth background
    img = np.zeros((h, w, 3))
    img[:] = np.array(hx("120d10"), float)
    img *= (1.0 - 0.45 * np.clip(np.hypot(xx - cx, yy - cy) / 300, 0, 1))[..., None]
    img += rnd.normal(0, 2.0, (h, w))[..., None]
    # contact shadow under the mirror
    sh = np.clip(1 - np.hypot((xx - cx - 8) / (R + 14), (yy - cy - 10) / (R + 10)), 0, 1)
    img *= (1 - 0.6 * np.clip(sh * 6, 0, 1))[..., None]

    # handle: a turned silver shank running off the bottom of the screen
    hx0 = xx - cx
    half = 15 - (yy - (cy + R)) * 0.05
    hm = (yy > cy + R - 8) & (np.abs(hx0) < half)
    t = np.clip(hx0 / np.maximum(half, 1), -1, 1)
    hn = np.stack([t, np.full_like(t, -0.1), np.sqrt(np.clip(1 - t * t, 0, 1))], -1)
    hl = np.clip(hn @ L, 0, 1)
    silver = np.array(hx("8c867a"), float)
    hcol = silver[None, None] * (0.35 + 0.85 * hl[..., None])
    rings = (np.abs(((yy - (cy + R)) % 34) - 17) < 2.2)
    hcol = np.where(rings[..., None], hcol * 0.55, hcol)
    img = np.where(hm[..., None], hcol, img)

    # silver rim, shaded as a rounded torus, with a bead border
    d = np.hypot(xx - cx, yy - cy)
    ux, uy = (xx - cx) / np.maximum(d, 1e-6), (yy - cy) / np.maximum(d, 1e-6)
    rm = (d <= R) & (d > R - rim)
    tt = np.clip((d - (R - rim / 2)) / (rim / 2), -1, 1)
    n = np.stack([ux * tt, uy * tt, np.sqrt(np.clip(1 - tt * tt, 0, 1))], -1)
    lit = np.clip(n @ L, 0, 1)
    spec = np.clip(lit - 0.82, 0, 1) * 4
    rc = silver[None, None] * (0.3 + 0.9 * lit[..., None]) + 120 * spec[..., None]
    ang = np.arctan2(yy - cy, xx - cx)
    beads = (np.abs(d - (R - rim * 0.5)) < 2.6) & (np.cos(ang * 60) > 0.35)
    rc = np.where(beads[..., None], rc * 1.18 + 10, rc)
    groove = np.abs(d - (R - rim + 2.5)) < 1.0
    rc = np.where(groove[..., None], rc * 0.45, rc)
    # black-green tarnish in the hollows
    tarn = np.clip(np.sin(xx / 9.0 + np.sin(yy / 13.0) * 2) * np.sin(yy / 7.0 + xx / 31.0) + rnd.normal(0, 0.35, (h, w)), 0, 1)
    rc = rc * (1 - 0.45 * tarn[..., None]) + np.array(hx("1e2418"), float) * 0.45 * tarn[..., None]
    img = np.where(rm[..., None], rc, img)

    # walnut back with a wavy grain, darkened where the rim shades it
    inner = d <= R - rim
    gx = xx + 7 * np.sin(yy / 31.0) + 3 * np.sin(yy / 9.0 + xx / 40.0)
    grain = 0.5 + 0.5 * np.sin(gx * 0.42 + 2.5 * np.sin(gx / 23.0))
    fine = rnd.normal(0, 0.06, (h, w))
    wood = np.array(hx("2c1a10"), float)[None, None] * (1 - grain[..., None]) + \
        np.array(hx("4e3020"), float)[None, None] * grain[..., None]
    wood *= (1 + fine)[..., None]
    rim_sh = np.clip(1 - (R - rim - d) / 12, 0, 1) * np.clip(-(ux * L[0] + uy * L[1]) * 1.4 + 0.3, 0, 1)
    dome = 0.85 + 0.25 * np.clip(-(xx - cx) / R * 0.6 - (yy - cy) / R * 0.6, -1, 1)
    wood *= ((1 - 0.6 * rim_sh) * dome)[..., None]
    img = np.where(inner[..., None], wood, img)

    base = Image.fromarray(np.clip(img, 0, 255).astype("uint8"), "RGB")

    # the sign: a triquetra interlaced with a ring, painted in a broad stroke with gaps at the under-crossings
    paths = _trinity_paths(cx, cy, 42.0, 60.0)
    xs = _crossings(paths)
    events = {0: []}
    for i, (pt, a, b) in enumerate(xs):
        for comp, idx in (a, b):
            if comp == 0:
                events[0].append((idx, i))
    # over/under: walk the triquetra alternating; the ring takes the opposite of the triquetra at each crossing
    state = {}
    for k, (idx, i) in enumerate(sorted(events[0])):
        state.setdefault(i, []).append((idx, k % 2 == 0))
    owner = {}
    for i, (pt, a, b) in enumerate(xs):
        if a[0] == 0 and b[0] == 0:
            vis = state[i]
            owner[i] = (0, vis[0][0] if vis[0][1] else vis[1][0])
        else:
            (c0, i0) = a if a[0] == 0 else b
            (c1, i1) = b if a[0] == 0 else a
            owner[i] = (0, i0) if dict(state[i])[i0] else (1, i1)
    layer = Image.new("RGBA", (w, h))
    dr = ImageDraw.Draw(layer)
    wd = 9.0
    ink, edge, scratch = hx("7e1e14", 255), hx("2a0806", 255), hx("b0482a", 255)

    def stamp(pts, rad, col):
        for x, y in pts:
            dr.ellipse([x - rad, y - rad, x + rad, y + rad], fill=col)

    def strand(pts):
        stamp(pts, wd / 2 + 1.6, edge)
        stamp(pts, wd / 2, ink)
        stamp(pts[::5], 0.5, scratch)

    for p in paths:
        strand(p)
    for i, (comp, idx) in owner.items():
        p = paths[comp]
        n = len(p)
        span = int(wd * 2.2 / 0.5)
        seg = [p[(idx + k) % n] for k in range(-span, span + 1)]
        core = [p[(idx + k) % n] for k in range(-int(span * 0.6), int(span * 0.6) + 1)]
        stamp(core, wd / 2 + 4.2, (0, 0, 0, 0))
        stamp(seg[3:-3], wd / 2 + 1.6, edge)
        stamp(seg, wd / 2, ink)
        stamp(seg[::5], 0.5, scratch)

    # dried, flaking ink: wood shows through in places
    la = np.array(layer).astype(float)
    wear = rnd.random((h, w))
    blot = 0.5 + 0.5 * np.sin(xx / 5.3 + np.sin(yy / 4.1) * 1.7) * np.sin(yy / 6.7 - xx / 11.0)
    a_ = la[..., 3] / 255.0
    a_ *= np.where((wear * blot) > 0.62, 0.35, 1.0)
    la[..., :3] *= (0.85 + 0.3 * blot)[..., None]
    la[..., 3] = a_ * 255 * 0.92
    layer = Image.fromarray(np.clip(la, 0, 255).astype("uint8"), "RGBA")
    out = base.convert("RGBA")
    out.alpha_composite(layer)
    out = out.convert("RGB")

    # a few scratches gouged into the wood around the sign
    d2 = ImageDraw.Draw(out)
    rr = random.Random(5)
    for _ in range(26):
        a0 = rr.uniform(0, 2 * math.pi)
        rad = rr.uniform(70, R - rim - 4)
        x0, y0 = cx + rad * math.cos(a0), cy + rad * math.sin(a0)
        ln, an = rr.uniform(3, 9), a0 + rr.uniform(-1.2, 1.2) + math.pi / 2
        d2.line([(x0, y0), (x0 + ln * math.cos(an), y0 + ln * math.sin(an))], fill=hx("6a4a32"))
    light(out, "ellipse", [cx - R - 30, cy - R - 40, cx + R - 40, cy + R - 60], hx("d0a070"), 0.12, 30)
    vignette(out, 0.75)
    save(pixelize(out, n=64, spread=10), "ui", "triquetra.png")


def build():
    title()
    triquetra()
    for name, fn in (("verb_look", eye), ("verb_hand", hand), ("verb_talk", mouth), ("verb_kick", boot)):
        save(_icon(fn), "ui", f"{name}.png")
    lo, hi = slot()
    save(lo, "ui", "wheel_slot.png")
    save(hi, "ui", "wheel_slot_hi.png")
    save(_icon(satchel, 30), "ui", "satchel.png")
    chest()
    cursor()
