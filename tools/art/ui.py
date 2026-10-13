"""Title card, verb-wheel icons, satchel, inventory chest and cursor."""
import math
from PIL import Image, ImageDraw
from .common import hx, mix, vgrad, light, vignette, pixelize, text, city, save, sunburst, noise
from .iconfx import _shade, _outline

GOLD, GOLD_D = hx("d8b050"), hx("8a6a28")


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
