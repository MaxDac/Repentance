"""Gothic-revival cathedral after Chicago's Holy Name: the rain-soaked facade at night and the candlelit nave."""
from PIL import Image, ImageDraw
import math
import random
from .common import W, FULL_H, hx, mix, mul, noise, light, shadow, vignette, pixelize, palette_of, save, city

H = FULL_H
WARM = hx("ffc46e")
GLASS = [hx("b0283a"), hx("2a4fa8"), hx("d9a640"), hx("3d8a5a"), hx("7a3a9a"), hx("e0d8b0")]


# ---------------------------------------------------------------- shared helpers

def arch_curve(a, b, spring, k=0.6, n=14, up=-1, sq=1.0):
    """Pointed arch from (a, spring) over the apex to (b, spring). up=-1 for screen y, +1 for world heights."""
    span = b - a
    r = max(span * k, span / 2 + 1e-6)
    mid = (a + b) / 2
    c = a + r
    ae = math.acos(max(-1.0, min(1.0, (mid - c) / r)))
    pts = []
    for i in range(n + 1):
        t = math.pi + (ae - math.pi) * i / n
        pts.append((c + r * math.cos(t), spring + up * r * math.sin(t) * sq))
    return pts + [(2 * mid - x, y) for x, y in reversed(pts[:-1])]


def arch_poly(a, b, spring, base, k=0.6, n=14):
    return [(a, base)] + arch_curve(a, b, spring, k, n) + [(b, base)]


def mask_of(size, polys, holes=()):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon(p, fill=255)
    for p in holes:
        d.polygon(p, fill=0)
    return m


def ashlar(size, box, base, seed, course=6, lo=9, hi=20, var=0.09, mortar=0.7):
    """Screen-space coursed stonework: blocks of slightly varying tone with dark joints."""
    layer = Image.new("RGB", size, base)
    d = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    x0, y0, x1, y1 = box
    y = y0
    while y < y1:
        x = x0 - rnd.randint(0, hi)
        while x < x1:
            w = rnd.randint(lo, hi)
            c = mul(base, 1 + rnd.uniform(-var, var))
            d.rectangle([x, y, x + w - 1, y + course - 1], fill=c)
            d.line([(x, y), (x + w - 2, y)], fill=mul(c, 1.07))
            d.line([(x + w - 1, y), (x + w - 1, y + course - 1)], fill=mul(base, mortar))
            x += w
        d.line([(x0, y + course - 1), (x1, y + course - 1)], fill=mul(base, mortar))
        y += course
    return layer


def stone(img, polys, base, seed, holes=(), **kw):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    box = (int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 2, int(max(ys)) + 2)
    img.paste(ashlar(img.size, box, base, seed, **kw), (0, 0), mask_of(img.size, polys, holes))


def blend_px(img, x, y, col, k):
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), mix(img.getpixel((x, y)), col, k))


def rain(img, seed, n=700, box=(0, 0, W, H), col=hx("8fa4c8"), k=0.32):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y = rnd.randint(box[0], box[2]), rnd.randint(box[1], box[3])
        ln = rnd.randint(3, 7)
        for i in range(ln):
            blend_px(img, x - i // 3, y + i, col, k * (1 - i / (ln + 1)))


def glass_cells(d, poly_fn, u0, u1, v0, v1, nu, nv, cols, rnd, lead):
    """Fills a (u, v) window panel with jewel-coloured cells separated by leading."""
    for i in range(nu):
        for j in range(nv):
            ua, ub = u0 + (u1 - u0) * i / nu, u0 + (u1 - u0) * (i + 1) / nu
            va, vb = v0 + (v1 - v0) * j / nv, v0 + (v1 - v0) * (j + 1) / nv
            c = rnd.choice(cols)
            d.polygon([poly_fn(ua, va), poly_fn(ub, va), poly_fn(ub, vb), poly_fn(ua, vb)], fill=c, outline=lead)


# ---------------------------------------------------------------- exterior: the facade at night

STONE = hx("575862")
STONE_D = hx("33343e")
STONE_L = hx("8a8a92")
TOWERS = ((72, 152), (328, 408))
PORCH = 198
STEP_BOTTOM = 234


def tenement(img, x0, x1, top, seed, ground):
    d = ImageDraw.Draw(img)
    base = hx("4c2b24")
    layer = Image.new("RGB", img.size, base)
    ld = ImageDraw.Draw(layer)
    rnd = random.Random(seed)
    for y in range(top, STEP_BOTTOM, 3):
        off = 3 if (y // 3) % 2 else 0
        for x in range(x0 - off, x1 + 6, 6):
            ld.rectangle([x, y, x + 5, y + 2], fill=mul(base, 1 + rnd.uniform(-0.14, 0.12)))
        ld.line([(x0, y + 2), (x1, y + 2)], fill=mul(base, 0.55))
    img.paste(layer, (0, 0), mask_of(img.size, [[(x0, top), (x1, top), (x1, STEP_BOTTOM), (x0, STEP_BOTTOM)]]))
    d.rectangle([x0, top - 7, x1, top - 1], fill=hx("26222a"))
    d.line([(x0, top - 7), (x1, top - 7)], fill=hx("5c5664"))
    for x in range(x0, x1, 4):
        d.rectangle([x, top - 1, x + 1, top + 1], fill=hx("1c181e"))
    cols = [x0 + 9 + i * 26 for i in range((x1 - x0 - 6) // 26)]
    for y in range(top + 14, ground - 30, 34):
        for x in cols:
            d.rectangle([x - 2, y - 3, x + 15, y - 1], fill=hx("6e625a"))
            d.rectangle([x - 1, y + 24, x + 14, y + 25], fill=hx("6e625a"))
            lit = rnd.random() < 0.45
            pane = hx("e2a456") if lit else hx("161a2a")
            d.rectangle([x, y, x + 13, y + 23], fill=pane)
            if lit:
                d.rectangle([x, y, x + 13, y + rnd.randint(4, 12)], fill=hx("b8763a"))
                light(img, "rect", [x - 4, y - 4, x + 17, y + 27], hx("ffb050"), 0.18, 4)
            else:
                d.line([(x + 1, y + 1), (x + 6, y + 6)], fill=hx("3a4466"))
            d.line([(x, y + 11), (x + 13, y + 11)], fill=hx("2a1c18"))
            d.line([(x + 6, y), (x + 6, y + 23)], fill=hx("2a1c18"))
    d.rectangle([x0, ground - 4, x1, ground], fill=hx("2c2428"))
    d.rectangle([x0 + 4, ground + 6, x1 - 4, STEP_BOTTOM - 2], fill=hx("141620"))
    d.rectangle([x0 + 6, ground + 8, x1 - 6, ground + 18], fill=hx("6a4a2a"))
    light(img, "rect", [x0 + 6, ground + 8, x1 - 6, ground + 18], hx("ffcc80"), 0.4, 2)
    for x in range(x0 + 8, x1 - 6, 8):
        d.line([(x, ground + 20), (x, STEP_BOTTOM - 2)], fill=hx("26283a"))


def sky_and_street_back(img):
    city(img, (0, 0, W - 1, 130), seed=19, lit=0.2, haze=hx("3a3450"))
    rnd = random.Random(5)
    for _ in range(12):
        x, y = rnd.randint(-40, 520), rnd.randint(-10, 60)
        light(img, "ellipse", [x - 80, y - 9, x + 80, y + 11], hx("4c4a6a"), 0.22, 10)
    light(img, "ellipse", [444, 10, 466, 32], hx("dfe4f4"), 0.55, 5)
    light(img, "ellipse", [410, -20, 500, 70], hx("8090c0"), 0.2, 20)
    d = ImageDraw.Draw(img)
    d.rectangle([60, 40, 76, STEP_BOTTOM], fill=hx("0b0c14"))
    d.rectangle([404, 40, 422, STEP_BOTTOM], fill=hx("0b0c14"))
    tenement(img, -6, 64, 74, 3, 186)
    tenement(img, 416, W + 6, 88, 4, 186)
    # a fire escape zig-zagging down the left tenement
    for y in (108, 142, 176):
        d.rectangle([2, y, 58, y + 1], fill=hx("16141a"))
        for x in range(2, 58, 3):
            d.line([(x, y - 7), (x, y)], fill=hx("16141a"))
        d.line([(2, y - 7), (58, y - 7)], fill=hx("16141a"))
        d.line([(50, y), (14, y + 33)], fill=hx("201c22"), width=2)


def buttress(img, x0, x1, top, side, seed):
    """A stepped buttress: lit front face plus a receding side face toward the centre of the facade."""
    d = ImageDraw.Draw(img)
    stone(img, [[(x0, top), (x1, top), (x1, PORCH), (x0, PORCH)]], mul(STONE, 1.08), seed, course=6, lo=7, hi=14)
    stages = ((150, PORCH, 8), (96, 150, 5), (top, 96, 3))
    for y0, y1, wd in stages:
        if side > 0:
            face = [(x1, y0), (x1 + wd, y0 + wd // 2), (x1 + wd, y1), (x1, y1)]
        else:
            face = [(x0, y0), (x0 - wd, y0 + wd // 2), (x0 - wd, y1), (x0, y1)]
        d.polygon(face, fill=STONE_D)
        for y in range(y0 + 6, y1, 6):
            d.line([face[0][0], y, face[1][0], y + wd // 2], fill=mul(STONE_D, 0.8))
        # weathering (sloped set-off) catching the city glow
        if y0 > top:
            d.polygon([(x0 - 1, y0 - 3), (x1 + 1, y0 - 3), (x1 + 2, y0 + 1), (x0 - 2, y0 + 1)], fill=STONE_L)
            d.line([(x0 - 2, y0 + 2), (x1 + 2, y0 + 2)], fill=STONE_D)
    d.line([(x0, top), (x0, PORCH)], fill=mul(STONE, 0.7))


def pinnacle(d, cx, base, tip, w):
    d.rectangle([cx - w, base - 10, cx + w, base], fill=STONE)
    d.line([(cx - w, base - 10), (cx - w, base)], fill=STONE_L)
    d.polygon([(cx - w - 1, base - 10), (cx + w + 1, base - 10), (cx + w, base - 12), (cx - w, base - 12)], fill=STONE_L)
    d.polygon([(cx - w, base - 12), (cx, tip), (cx + w, base - 12)], fill=STONE)
    d.polygon([(cx, base - 12), (cx, tip), (cx + w, base - 12)], fill=STONE_D)
    for y in range(base - 15, tip + 2, -4):
        t = (base - 12 - y) / max(1, base - 12 - tip)
        hw = w * (1 - t)
        d.point((int(cx - hw - 1), y), fill=STONE_L)
        d.point((int(cx + hw + 1), y), fill=STONE_L)
    d.line([(cx, tip), (cx, tip - 4)], fill=STONE_L)
    d.line([(cx - 1, tip - 2), (cx + 1, tip - 2)], fill=STONE_L)


def spire(img, x0, x1, base):
    d = ImageDraw.Draw(img)
    cx = (x0 + x1) / 2
    tip = (cx, base - 120)
    q = (x1 - x0) / 4
    faces = [((x0, base), (cx - q, base), mul(STONE_D, 0.9)), ((cx - q, base), (cx + q, base), mul(STONE, 0.92)),
             ((cx + q, base), (x1, base), mul(STONE, 1.1))]
    for a, b, col in faces:
        d.polygon([a, b, tip], fill=col)
        for y in range(base - 4, -1, -4):
            t = (base - y) / (base - tip[1])
            xa, xb = a[0] + (cx - a[0]) * t, b[0] + (cx - b[0]) * t
            d.line([(xa, y), (xb, y)], fill=mul(col, 0.8))
    for ex in (x0, cx - q, cx + q, x1):
        d.line([(ex, base), tip], fill=STONE_L if ex > cx else mul(STONE, 0.75))
        for y in range(base - 5, -1, -6):
            t = (base - y) / (base - tip[1])
            x = ex + (cx - ex) * t
            d.point((int(x) + (1 if ex > cx else -1), y), fill=STONE_L)
    # lucarne (gabled spire light)
    lx = int(cx)
    d.polygon([(lx - 8, base), (lx - 8, base - 10), (lx, base - 19), (lx + 8, base - 10), (lx + 8, base)], fill=STONE)
    d.polygon([(lx - 8, base - 10), (lx, base - 19), (lx + 8, base - 10)], outline=STONE_L)
    d.polygon(arch_poly(lx - 4, lx + 4, base - 8, base, 0.7, 6), fill=hx("0c0d14"))
    for y in range(base - 8, base, 2):
        d.line([(lx - 3, y), (lx + 3, y)], fill=hx("34343e"))


def tower(img, x0, x1, seed, right):
    d = ImageDraw.Draw(img)
    stone(img, [[(x0, 40), (x1, 40), (x1, PORCH), (x0, PORCH)]], STONE, seed)
    spire(img, x0 + 14, x1 - 14, 34)
    # parapet with pierced quatrefoils
    d.rectangle([x0 + 10, 30, x1 - 10, 42], fill=STONE)
    d.line([(x0 + 10, 30), (x1 - 10, 30)], fill=STONE_L)
    d.rectangle([x0 + 10, 42, x1 - 10, 44], fill=STONE_D)
    for x in range(x0 + 18, x1 - 14, 9):
        d.ellipse([x - 3, 33, x + 3, 39], fill=hx("1a1b26"))
        d.point((x, 36), fill=STONE)
    cx = (x0 + x1) // 2
    # belfry: a pair of tall louvred lancets under one hood
    d.polygon(arch_poly(cx - 24, cx + 24, 66, 112, 0.62), fill=mul(STONE, 0.82))
    d.line(arch_curve(cx - 25, cx + 25, 66, 0.62), fill=STONE_L)
    for a in (cx - 20, cx + 3):
        d.polygon(arch_poly(a, a + 17, 70, 110, 0.75), fill=hx("0a0b12"))
        for y in range(64, 110, 3):
            d.line([(a + 1, y), (a + 16, y)], fill=hx("2a2a36"))
            d.line([(a + 1, y + 1), (a + 16, y + 1)], fill=hx("14141c"))
        d.line(arch_curve(a, a + 17, 70, 0.75, 8), fill=STONE_L)
        d.line([(a + 17, 70), (a + 17, 110)], fill=STONE_L)
        d.line([(a, 70), (a, 110)], fill=STONE_D)
    d.ellipse([cx - 4, 52, cx + 4, 60], fill=hx("0a0b12"), outline=STONE_L)
    d.rectangle([cx - 24, 110, cx + 24, 113], fill=STONE_L)
    # string course
    d.rectangle([x0 + 4, 114, x1 - 4, 117], fill=STONE_L)
    d.line([(x0 + 4, 118), (x1 - 4, 118)], fill=hx("1c1c26"))
    if not right:
        # tall lower lancet, faintly lit from a side chapel
        d.polygon(arch_poly(cx - 13, cx + 13, 140, 182, 0.7), fill=mul(STONE, 0.75))
        d.polygon(arch_poly(cx - 10, cx + 10, 141, 180, 0.72), fill=hx("2a2030"))
        rnd = random.Random(seed)
        glass_cells(ImageDraw.Draw(img), lambda u, v: (u, v), cx - 10, cx + 10, 128, 180, 4, 9,
                    [hx("7a3020"), hx("8a6a30"), hx("2a3a6a"), hx("6a2a40")], rnd, hx("1a1418"))
        d.polygon(arch_poly(cx - 13, cx + 13, 140, 128, 0.7)[1:-1] + [(cx + 13, 128), (cx + 13, 120), (cx - 13, 120),
                                                                    (cx - 13, 128)], fill=mul(STONE, 0.75))
        d.line(arch_curve(cx - 13, cx + 13, 140, 0.7), fill=STONE_L, width=2)
        d.line([(cx, 128), (cx, 180)], fill=hx("4a4a52"))
        d.rectangle([cx - 14, 181, cx + 14, 184], fill=STONE_L)
        light(img, "rect", [cx - 10, 128, cx + 10, 180], hx("ff9a50"), 0.22, 3)
    else:
        # small lancet over the glass-fronted parish notice case
        d.polygon(arch_poly(cx - 7, cx + 7, 130, 144, 0.7), fill=hx("181a26"))
        d.line(arch_curve(cx - 8, cx + 8, 130, 0.7), fill=STONE_L)
        d.rectangle([cx - 22, 148, cx + 22, 180], fill=hx("2a1a12"))
        d.rectangle([cx - 20, 150, cx + 20, 178], fill=hx("4a3828"))
        d.rectangle([cx - 18, 152, cx + 18, 176], fill=hx("d8ccb0"))
        rnd = random.Random(8)
        for i, (px, py, pw, ph) in enumerate(((cx - 16, 154, 14, 10), (cx + 1, 154, 15, 7), (cx - 16, 166, 10, 8),
                                               (cx - 4, 164, 9, 10), (cx + 7, 163, 9, 11))):
            d.rectangle([px, py, px + pw, py + ph], fill=(hx("f2ead8"), hx("e8d090"), hx("c8d8e8"))[i % 3])
            for yy in range(py + 2, py + ph - 1, 2):
                d.line([(px + 2, yy), (px + rnd.randint(4, pw - 1), yy)], fill=hx("6a5a4a"))
        d.line([(cx - 18, 152), (cx - 6, 176)], fill=hx("f8f4ff"))
        d.rectangle([cx - 24, 145, cx + 24, 148], fill=hx("3a2416"))
        light(img, "rect", [cx - 18, 152, cx + 18, 176], hx("fff0c0"), 0.2, 3)
    d.rectangle([x0 + 2, 186, x1 - 2, PORCH], fill=mul(STONE, 0.85))
    d.line([(x0 + 2, 186), (x1 - 2, 186)], fill=STONE_L)
    buttress(img, x0, x0 + 14, 44, 1 if not right else -1, seed + 1)
    buttress(img, x1 - 14, x1, 44, 1 if not right else -1, seed + 2)
    pinnacle(d, x0 + 7, 44, 4, 6)
    pinnacle(d, x1 - 7, 44, 4, 6)


def rose_window(img, cx, cy, r):
    s = 4
    big = Image.new("RGBA", (r * 2 * s + 16 * s, r * 2 * s + 16 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    c = big.width / 2
    R = r * s
    frame = hx("6e6e78") + (255,)
    lead = hx("22202a") + (255,)
    d.ellipse([c - R - 5 * s, c - R - 5 * s, c + R + 5 * s, c + R + 5 * s], fill=hx("3e3e48") + (255,))
    d.ellipse([c - R - 3 * s, c - R - 3 * s, c + R + 3 * s, c + R + 3 * s], fill=frame)
    d.ellipse([c - R, c - R, c + R, c + R], fill=lead)
    rnd = random.Random(12)
    for ring, (r0, r1, n) in enumerate(((0.36, 0.62, 12), (0.64, 0.98, 24))):
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            col = (GLASS[0], GLASS[1], GLASS[2], GLASS[1], GLASS[0], GLASS[4])[(i + ring) % 6]
            pts = [(c + math.cos(a0 + (a1 - a0) * t) * R * rr, c + math.sin(a0 + (a1 - a0) * t) * R * rr)
                   for rr, rng in ((r0, range(7)), (r1, range(6, -1, -1))) for t in [k / 6 for k in rng]]
            d.polygon(pts, fill=mix(col, hx("ffe0a0"), rnd.uniform(0.15, 0.45)) + (255,))
    d.ellipse([c - R * 0.34, c - R * 0.34, c + R * 0.34, c + R * 0.34], fill=hx("f0c060") + (255,))
    for i in range(12):
        a = 2 * math.pi * i / 12
        d.line([(c + math.cos(a) * R * 0.34, c + math.sin(a) * R * 0.34), (c + math.cos(a) * R, c + math.sin(a) * R)],
               fill=frame, width=int(1.6 * s))
        ex, ey = c + math.cos(a + math.pi / 12) * R * 0.8, c + math.sin(a + math.pi / 12) * R * 0.8
        d.ellipse([ex - R * 0.17, ey - R * 0.17, ex + R * 0.17, ey + R * 0.17], outline=frame, width=s)
    d.ellipse([c - R * 0.63, c - R * 0.63, c + R * 0.63, c + R * 0.63], outline=frame, width=int(1.6 * s))
    d.ellipse([c - R * 0.34, c - R * 0.34, c + R * 0.34, c + R * 0.34], outline=frame, width=int(1.6 * s))
    for i in range(4):
        a = math.pi / 4 + i * math.pi / 2
        ex, ey = c + math.cos(a) * R * 0.15, c + math.sin(a) * R * 0.15
        d.ellipse([ex - R * 0.12, ey - R * 0.12, ex + R * 0.12, ey + R * 0.12], outline=frame, width=s)
    d.ellipse([c - 2 * s, c - 2 * s, c + 2 * s, c + 2 * s], fill=frame)
    small = big.resize((big.width // s, big.height // s), Image.Resampling.LANCZOS)
    light(img, "ellipse", [cx - r - 14, cy - r - 14, cx + r + 14, cy + r + 14], hx("ff9a40"), 0.3, 12)
    img.paste(small, (int(cx - small.width / 2), int(cy - small.height / 2)), small)


def portal(img):
    d = ImageDraw.Draw(img)
    spring = 124
    orders = [(186, 294), (192, 288), (198, 282), (204, 276), (210, 270)]
    # recessed jambs: each order steps further into the wall and deeper into shadow
    for i, (a, b) in enumerate(orders):
        depth = i / (len(orders) - 1)
        roll = i % 2 == 0
        col = mix(mul(STONE, 1.15 if roll else 0.72), STONE_D, depth * 0.55)
        d.polygon(arch_poly(a, b, spring, PORCH - 2, 0.58, 18), fill=col)
        if roll:
            d.line(arch_curve(a + 1, b - 1, spring, 0.58, 18), fill=mix(STONE_L, col, depth * 0.5))
            d.line([(a + 1, spring), (a + 1, PORCH - 6)], fill=mix(STONE_L, col, depth * 0.5))
            d.line([(b - 2, spring), (b - 2, PORCH - 6)], fill=mul(col, 0.7))
    # tympanum with a carved Christ in majesty
    d.polygon(arch_poly(212, 268, spring, 112, 0.58, 16), fill=mul(STONE, 0.9))
    stone(img, [arch_poly(213, 267, spring, 112, 0.58, 16)], mul(STONE, 0.95), 61, course=4, lo=5, hi=9)
    d.ellipse([230, 90, 250, 112], fill=mul(STONE, 1.25), outline=STONE_D)
    d.ellipse([237, 92, 243, 98], fill=STONE_L)
    d.polygon([(235, 98), (245, 98), (247, 111), (233, 111)], fill=mul(STONE, 1.1))
    d.line([(240, 99), (240, 110)], fill=STONE_D)
    for ax in (222, 258):
        d.polygon([(ax - 4, 112), (ax, 100), (ax + 4, 112)], fill=mul(STONE, 1.05))
        d.ellipse([ax - 2, 98, ax + 2, 102], fill=STONE_L)
    # lintel and the iron-banded oak doors (one leaf ajar - candlelight leaks through)
    d.rectangle([209, 112, 271, 116], fill=STONE_L)
    d.line([(209, 116), (271, 116)], fill=STONE_D)
    d.rectangle([212, 117, 268, PORCH - 2], fill=hx("2a1a10"))
    for x in range(213, 268, 4):
        d.line([(x, 117), (x, PORCH - 3)], fill=hx("1c110a"))
        d.line([(x + 1, 117), (x + 1, PORCH - 3)], fill=hx("3a2416"))
    for y in (126, 152, 180):
        for x0, x1, s in ((214, 238, 1), (242, 266, -1)):
            d.rectangle([x0, y, x1, y + 2], fill=hx("16161a"))
            d.line([(x0, y), (x1, y)], fill=hx("4a4a52"))
            ex = x1 if s > 0 else x0
            d.arc([ex - 4, y - 3, ex + 4, y + 5], 270 if s > 0 else 90, 90 if s > 0 else 270, fill=hx("16161a"))
    d.rectangle([239, 117, 241, PORCH - 2], fill=hx("ffd890"))
    light(img, "rect", [238, 117, 242, PORCH - 2], WARM, 0.55, 3)
    for hx_ in (233, 247):
        d.ellipse([hx_ - 3, 160, hx_ + 3, 166], outline=hx("8a7a50"))
    d.rectangle([212, PORCH - 3, 268, PORCH - 2], fill=hx("ffcf80"))
    # capitals band and hood-mould with crockets and a finial
    d.rectangle([184, spring - 4, 296, spring], fill=mul(STONE, 1.2))
    for x in range(186, 296, 3):
        d.point((x, spring - 2), fill=STONE_D)
    hood = arch_curve(182, 298, spring - 2, 0.58, 22)
    d.line(hood, fill=STONE_L, width=2)
    for x, y in hood[2:-2:3]:
        d.ellipse([x - 1.5, y - 2.5, x + 1.5, y + 0.5], fill=STONE_L)
    ax, ay = min(hood, key=lambda p: p[1])
    d.polygon([(ax - 3, ay), (ax, ay - 10), (ax + 3, ay)], fill=STONE_L)
    d.ellipse([ax - 3, ay - 9, ax + 3, ay - 5], fill=STONE_L)


STATUE_RAMP = [hx("1e1e26"), hx("3a3a46"), hx("5e5e6a"), hx("86848e"), hx("aeacb2"), hx("d4d2d6")]
GILT = hx("c8a860")
GILT_L = hx("f0d890")


def _ramp(v):
    v = max(0.0, min(1.0, v)) * (len(STATUE_RAMP) - 1)
    i = min(int(v), len(STATUE_RAMP) - 2)
    return mix(STATUE_RAMP[i], STATUE_RAMP[i + 1], v - i)


def _carve(img, form, cx, side, y0, y1):
    """Turns a carved relief (an L layer of 0..255 heights/albedo) into lit stone.

    side=+1 lights the figure from the right (the lantern beside the door), -1 from the left."""
    from PIL import ImageFilter
    px, fp = img.load(), form.load()
    mask = form.point(lambda v: 255 if v else 0)
    grown = mask.filter(ImageFilter.MaxFilter(3))
    mp, gp = mask.load(), grown.load()
    for y in range(y0, y1 + 1):
        for x in range(int(cx) - 12, int(cx) + 13):
            if mp[x, y]:
                lit = 0.86 + 0.24 * max(0.0, min(1.0, ((x - cx) * side + 7) / 14))
                v = fp[x, y] / 255 * lit
                if not mp[x + side, y]:
                    # rim of lantern light along the edge that faces the door
                    px[x, y] = mix(_ramp(v + 0.2), WARM, 0.3 * max(0.0, 1 - abs(y - 132) / 50))
                    continue
                if not mp[x - side, y]:
                    v -= 0.12
                px[x, y] = _ramp(v)
            elif gp[x, y] and abs(x - cx) <= 9:
                px[x, y] = STATUE_RAMP[0]


def _halo(d, cx, top):
    d.ellipse([cx - 6, top + 1, cx + 6, top + 12], fill=hx("34322e"), outline=hx("9a8048"))
    d.arc([cx - 6, top + 1, cx + 6, top + 12], 200, 340, fill=GILT)
    for a in range(0, 360, 45):
        r = math.radians(a)
        d.point((round(cx + 4 * math.cos(r)), round(top + 6.5 + 4 * math.sin(r))), fill=hx("6a5838"))


def saint_peter(img, cx, side):
    """St Peter: curly hair and beard, mantle slung over a shoulder, the keys hanging from one hand, a book."""
    form = Image.new("L", img.size, 0)
    f = ImageDraw.Draw(form)
    _halo(ImageDraw.Draw(img), cx, 125)
    s = side
    # tunic, flaring to the plinth with a hem broken over the feet
    f.polygon([(cx - 6, 142), (cx + 6, 142), (cx + 8, 175), (cx - 8, 175)], fill=120)
    # mantle over the far shoulder, its hem falling diagonally across the body
    f.polygon([(cx - 7 * s, 140), (cx + 2 * s, 140), (cx + 7 * s, 153), (cx + 5 * s, 158), (cx - 3 * s, 165),
               (cx - 8 * s, 170), (cx - 8 * s, 150)], fill=200)
    f.line([(cx + 7 * s, 153), (cx + 5 * s, 158), (cx - 3 * s, 165), (cx - 8 * s, 170)], fill=225)
    for k in range(3):
        f.line([(cx - (5 - k * 3) * s, 142), (cx - (7 - k * 4) * s, 163 - k * 3)], fill=90)
        f.line([(cx - (4 - k * 3) * s, 143), (cx - (6 - k * 4) * s, 162 - k * 3)], fill=240)
    for x in (-5, -2, 1, 4):
        f.line([(cx + x, 162 + abs(x)), (cx + x + (x > 0), 175)], fill=70)
        f.line([(cx + x + 1, 164 + abs(x)), (cx + x + 1, 174)], fill=190)
    f.line([(cx - 8, 175), (cx + 8, 175)], fill=120)
    for fx in (cx - 3, cx + 2):
        f.ellipse([fx - 1, 174, fx + 2, 177], fill=200)
    # shoulders and the arm that holds the keys up against the chest
    f.polygon([(cx - 7, 142), (cx - 3, 139), (cx + 3, 139), (cx + 7, 142), (cx + 7, 145), (cx - 7, 145)], fill=165)
    f.polygon([(cx + 6 * s, 141), (cx + 8 * s, 146), (cx + 7 * s, 152), (cx + 2 * s, 152), (cx + 2 * s, 149),
               (cx + 5 * s, 148)], fill=185)
    f.line([(cx + 7 * s, 146), (cx + 6 * s, 151)], fill=120)
    f.ellipse([cx - 1, 149, cx + 2, 152], fill=225)
    # the book clasped under the other arm
    bx = cx - 7 * s
    f.polygon([(bx, 152), (bx + 4 * s, 151), (bx + 5 * s, 158), (bx + s, 159)], fill=215)
    f.line([(bx + s, 159), (bx + 5 * s, 158)], fill=90)
    f.line([(bx + 2 * s, 153), (bx + 4 * s, 157)], fill=150)
    # head: curly hair, deep-set eyes, a short curly beard
    f.ellipse([cx - 3, 129, cx + 3, 137], fill=185)
    f.chord([cx - 4, 128, cx + 4, 136], 180, 360, fill=105)
    for hx_ in (-3, -1, 1, 3):
        f.point((cx + hx_, 129 + (hx_ % 2)), fill=95)
        f.point((cx + hx_, 131), fill=165)
    f.line([(cx - 2, 132), (cx + 2, 132)], fill=230)
    f.point((cx - 1, 133), fill=60)
    f.point((cx + 1, 133), fill=60)
    f.line([(cx, 133), (cx, 134)], fill=235)
    f.polygon([(cx - 3, 135), (cx + 3, 135), (cx + 3, 138), (cx + 1, 141), (cx - 1, 141), (cx - 3, 138)], fill=150)
    for bx_, by_ in ((-2, 137), (0, 138), (2, 137), (-1, 140), (1, 140)):
        f.point((cx + bx_, by_), fill=100)
    f.point((cx, 136), fill=70)
    _carve(img, form, cx, side, 124, 178)
    d = ImageDraw.Draw(img)
    # the keys of heaven, gilt and crossed over the chest, the bits turned outwards
    for (ax, ay), (bx_, by_) in (((cx - 4, 144), (cx + 4, 158)), ((cx + 4, 144), (cx - 4, 158))):
        d.line([(ax, ay), (bx_, by_)], fill=GILT)
        d.ellipse([ax - 1, ay - 2, ax + 1, ay], outline=GILT_L)
        dx = 1 if bx_ > ax else -1
        d.point((bx_ + dx, by_ - 1), fill=GILT_L)
        d.point((bx_ + dx, by_ + 1), fill=GILT)
    d.ellipse([cx - 1, 149, cx + 2, 152], fill=_ramp(0.85))
    d.point((cx, 150), fill=_ramp(1.0))


def saint_paul(img, cx, side):
    """St Paul: bald crown, long forked beard, both hands on the pommel of a sword, a book on his arm."""
    form = Image.new("L", img.size, 0)
    f = ImageDraw.Draw(form)
    _halo(ImageDraw.Draw(img), cx, 125)
    s = side
    f.polygon([(cx - 6, 142), (cx + 6, 142), (cx + 8, 175), (cx - 8, 175)], fill=120)
    # the mantle wrapped over both arms and gathered at the waist
    f.polygon([(cx - 7, 140), (cx + 7, 140), (cx + 8, 158), (cx + 4, 163), (cx - 4, 163), (cx - 8, 158)], fill=200)
    f.line([(cx - 8, 158), (cx - 4, 163), (cx + 4, 163), (cx + 8, 158)], fill=225)
    for x in (-6, -3, 3, 6):
        f.line([(cx + x, 145), (cx + x + (1 if x > 0 else -1), 157)], fill=90)
        f.line([(cx + x + 1, 146), (cx + x + 1 + (1 if x > 0 else -1), 156)], fill=235)
    for x in (-5, -2, 1, 4):
        f.line([(cx + x, 165), (cx + x + (x > 0), 175)], fill=70)
        f.line([(cx + x + 1, 166), (cx + x + 1, 174)], fill=190)
    f.line([(cx - 8, 175), (cx + 8, 175)], fill=120)
    for fx in (cx - 3, cx + 2):
        f.ellipse([fx - 1, 174, fx + 2, 177], fill=200)
    # the book on the near forearm
    bx = cx + 6 * s
    f.polygon([(bx, 147), (bx + 3 * s, 146), (bx + 4 * s, 153), (bx + s, 154)], fill=215)
    f.line([(bx + s, 154), (bx + 4 * s, 153)], fill=90)
    # both hands folded on the pommel
    f.ellipse([cx - 2, 145, cx + 2, 149], fill=210)
    f.line([(cx - 1, 147), (cx + 1, 147)], fill=150)
    # head: bald dome, fringe of hair, long forked beard to the chest
    f.ellipse([cx - 3, 129, cx + 3, 137], fill=190)
    f.point((cx - 1, 130), fill=235)
    f.line([(cx - 3, 132), (cx - 3, 135)], fill=120)
    f.line([(cx + 3, 132), (cx + 3, 135)], fill=120)
    f.line([(cx - 2, 132), (cx + 2, 132)], fill=225)
    f.point((cx - 1, 133), fill=60)
    f.point((cx + 1, 133), fill=60)
    f.line([(cx, 133), (cx, 134)], fill=235)
    f.polygon([(cx - 3, 135), (cx + 3, 135), (cx + 2, 141), (cx + 1, 144), (cx, 142), (cx - 1, 144), (cx - 2, 141)], fill=150)
    for by_ in (137, 139, 141):
        f.point((cx - 1, by_), fill=105)
        f.point((cx + 1, by_ + 1), fill=105)
    f.point((cx, 136), fill=70)
    _carve(img, form, cx, side, 124, 178)
    d = ImageDraw.Draw(img)
    # the sword of his martyrdom, point down between the feet
    d.line([(cx, 149), (cx, 172)], fill=hx("d0d8e0"))
    d.line([(cx - s, 150), (cx - s, 171)], fill=hx("6a7078"))
    d.point((cx, 173), fill=hx("8a9098"))
    d.line([(cx - 3, 149), (cx + 3, 149)], fill=GILT)
    d.point((cx - 3 * s, 149), fill=GILT_L)
    d.point((cx, 144), fill=GILT_L)


def statue_niche(img, x0, x1, seed):
    d = ImageDraw.Draw(img)
    cx = (x0 + x1) // 2
    d.polygon(arch_poly(x0, x1, 128, 178, 0.7), fill=hx("23242e"))
    # a fluted shell hood in the head of the niche and a shadowed back wall
    top = min(y for _, y in arch_curve(x0, x1, 128, 0.7))
    for k in range(-3, 4):
        d.line([(cx, 128), (cx + k * 3, top + 2 + abs(k) * 1.5)], fill=hx("383a46"))
    d.line([(x0 + 1, 128), (x1 - 1, 128)], fill=hx("44464f"))
    for y in range(131, 177, 6):
        d.line([(x0 + 1, y), (x1 - 1, y)], fill=hx("1c1d26"))
    d.line(arch_curve(x0 - 1, x1 + 1, 128, 0.7), fill=STONE_L)
    # crocketed gable over the niche with a finial
    d.polygon([(cx - 8, 112), (cx, 100), (cx + 8, 112)], outline=STONE_L)
    for t in (0.3, 0.6):
        d.point((round(cx - 8 + 8 * t), round(112 - 12 * t) - 1), fill=STONE_L)
        d.point((round(cx + 8 - 8 * t), round(112 - 12 * t) - 1), fill=STONE_L)
    d.line([(cx, 100), (cx, 97)], fill=STONE_L)
    d.point((cx - 1, 98), fill=STONE_L)
    d.point((cx + 1, 98), fill=STONE_L)
    # moulded plinth and a carved corbel of leaves
    d.rectangle([x0 - 2, 178, x1 + 2, 182], fill=STONE_L)
    d.line([(x0 - 2, 178), (x1 + 2, 178)], fill=hx("b0b0b6"))
    d.line([(x0 - 2, 182), (x1 + 2, 182)], fill=STONE_D)
    for x in range(x0, x1 + 1, 3):
        d.point((x, 180), fill=STONE)
    d.polygon([(x0, 183), (x1, 183), (cx + 4, 189), (cx - 4, 189)], fill=STONE)
    for k in (-1, 0, 1):
        d.polygon([(cx + k * 5 - 2, 183), (cx + k * 5 + 2, 183), (cx + k * 3, 188)], fill=mul(STONE, 1.25))
        d.line([(cx + k * 5, 184), (cx + k * 3, 187)], fill=STONE_D)


def lantern(img, x, y):
    d = ImageDraw.Draw(img)
    d.line([(x, y - 6), (x, y - 2)], fill=hx("101014"))
    d.polygon([(x - 5, y - 1), (x + 5, y - 1), (x, y - 6)], fill=hx("16161c"))
    d.rectangle([x - 4, y, x + 4, y + 11], fill=hx("ffd890"))
    d.line([(x, y), (x, y + 11)], fill=hx("2a2620"))
    d.line([(x - 4, y + 5), (x + 4, y + 5)], fill=hx("2a2620"))
    d.rectangle([x - 4, y, x + 4, y + 11], outline=hx("16161c"))
    d.polygon([(x - 3, y + 12), (x + 3, y + 12), (x, y + 16)], fill=hx("16161c"))
    light(img, "ellipse", [x - 30, y - 24, x + 30, y + 36], WARM, 0.32, 14)
    light(img, "ellipse", [x - 7, y - 3, x + 7, y + 14], hx("fff4c0"), 0.6, 3)


def facade(img):
    d = ImageDraw.Draw(img)
    stone(img, [[(150, 0), (330, 0), (330, PORCH), (150, PORCH)]], STONE, 31)
    # soot streaks running down from every ledge
    rnd = random.Random(44)
    for _ in range(46):
        x = rnd.randint(60, 420)
        y = rnd.choice((44, 62, 118, 124, 186)) + rnd.randint(-2, 2)
        shadow(img, "rect", [x, y, x + rnd.randint(2, 6), y + rnd.randint(14, 50)], 0.22, 2, hx("20202a"))
    # rose window in a pointed surround above a gallery string course
    d.polygon(arch_poly(206, 274, 40, 62, 0.75), fill=mul(STONE, 0.78))
    d.line(arch_curve(205, 275, 40, 0.75), fill=STONE_L, width=2)
    d.line([(205, 40), (205, 62)], fill=STONE_L)
    d.line([(274, 40), (274, 62)], fill=STONE_D)
    rose_window(img, 240, 34, 23)
    d.rectangle([150, 62, 330, 65], fill=STONE_L)
    d.line([(150, 66), (330, 66)], fill=hx("1c1c26"))
    for x in range(156, 326, 10):
        if 178 < x < 298:
            continue
        d.polygon(arch_poly(x, x + 7, 72, 82, 0.7, 4), fill=hx("2a2b36"))
    for x0 in (156, 300):
        d.polygon(arch_poly(x0, x0 + 24, 20, 56, 0.7), fill=mul(STONE, 0.8))
        d.polygon(arch_poly(x0 + 4, x0 + 20, 24, 54, 0.75), fill=hx("16181f"))
        d.line([(x0 + 12, 22), (x0 + 12, 54)], fill=mul(STONE, 0.9))
    portal(img)
    statue_niche(img, 160, 178, 1)
    statue_niche(img, 302, 320, 2)
    lantern(img, 178, 128)
    lantern(img, 302, 128)
    # the saints are carved after the lanterns so the glare does not wash out their faces
    saint_peter(img, 169, 1)
    saint_paul(img, 311, -1)
    d.rectangle([150, 186, 330, PORCH], fill=mul(STONE, 0.85))
    d.line([(150, 186), (184, 186)], fill=STONE_L)
    d.line([(296, 186), (330, 186)], fill=STONE_L)
    for (x0, x1), seed, right in ((TOWERS[0], 71, False), (TOWERS[1], 73, True)):
        tower(img, x0, x1, seed, right)


def steps(img):
    d = ImageDraw.Draw(img)
    d.rectangle([60, PORCH, 420, PORCH + 3], fill=hx("6e6c72"))
    n = 6
    for i in range(n):
        y0 = PORCH + 3 + i * (STEP_BOTTOM - PORCH - 3) / n
        y1 = PORCH + 3 + (i + 1) * (STEP_BOTTOM - PORCH - 3) / n
        x0, x1 = 84 - i * 1.5, 396 + i * 1.5
        d.rectangle([x0, y0, x1, y0 + 1], fill=hx("7a7880"))
        d.rectangle([x0, y0 + 2, x1, y1], fill=hx("3c3c46"))
        d.line([(x0, y1 - 1), (x1, y1 - 1)], fill=hx("26262e"))
    noise(img, (60, PORCH, 420, STEP_BOTTOM), 6, 9)
    # cheek walls with iron lamp standards
    for x0, x1 in ((58, 86), (394, 422)):
        stone(img, [[(x0, 182), (x1, 182), (x1, STEP_BOTTOM), (x0, STEP_BOTTOM)]], mul(STONE, 0.95), x0, course=7)
        d.rectangle([x0 - 2, 179, x1 + 2, 183], fill=STONE_L)
        d.line([(x0 - 2, 184), (x1 + 2, 184)], fill=STONE_D)
        cx = (x0 + x1) // 2
        d.rectangle([cx - 4, 172, cx + 4, 179], fill=hx("16161c"))
        d.rectangle([cx - 1, 120, cx + 1, 172], fill=hx("1a1a20"))
        d.line([(cx - 1, 120), (cx - 1, 172)], fill=hx("3a3a46"))
        for y in (140, 160):
            d.rectangle([cx - 2, y, cx + 2, y + 2], fill=hx("16161c"))
        d.line([(cx - 8, 116), (cx + 8, 116)], fill=hx("16161c"))
        for gx in (cx - 7, cx + 7):
            d.ellipse([gx - 4, 106, gx + 4, 116], fill=hx("fff0c0"))
            light(img, "ellipse", [gx - 24, 88, gx + 24, 134], WARM, 0.35, 12)
            d.line([(gx, 103), (gx, 106)], fill=hx("16161c"))
        d.ellipse([cx - 3, 100, cx + 3, 104], fill=hx("16161c"))
        light(img, "ellipse", [cx - 60, 176, cx + 60, 262], WARM, 0.18, 18)
    light(img, "polygon", [(212, PORCH), (268, PORCH), (300, STEP_BOTTOM), (180, STEP_BOTTOM)], WARM, 0.22, 10)


def pavement(img):
    d = ImageDraw.Draw(img)
    top, curb = STEP_BOTTOM, 262
    # reflections of everything above in the wet paving
    src = img.crop((0, top - (curb - top) * 3, W, top)).resize((W, curb - top)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    d.rectangle([0, top, W, curb], fill=hx("1c1e28"))
    for y in range(top, curb, 9):
        d.line([(0, y), (W, y)], fill=hx("2c2e3a"))
    for i in range(-20, 21):
        x = 240 + i * 26
        d.line([(x + (x - 240) * 0.0, top), (x + (x - 240) * 0.25, curb)], fill=hx("2a2c38"))
    refl = Image.blend(img.crop((0, top, W, curb)), src, 0.42)
    img.paste(refl, (0, top))
    rnd = random.Random(3)
    for _ in range(9):
        x, y = rnd.randint(0, W), rnd.randint(top + 4, curb - 4)
        shadow(img, "ellipse", [x - 26, y - 3, x + 26, y + 3], 0.25, 2, hx("8090c0"))
    for x in (72, 408, 178, 302, 240):
        light(img, "rect", [x - 3, top + 2, x + 3, curb], WARM, 0.25, 3)
    d.rectangle([0, curb, W, curb + 2], fill=hx("6a6a72"))
    d.rectangle([0, curb + 3, W, H], fill=hx("101218"))
    for x in range(0, W, 7):
        d.point((x, curb + 5), fill=hx("2a2c38"))
    light(img, "rect", [0, curb + 3, W, H], hx("4a5a8a"), 0.15, 2)


def shade(img, y0, y1, f0, f1, tint=(0, 0, 0), keep=170):
    """Darken rows y0..y1 by a factor ramping f0 -> f1, sparing glowing pixels brighter than `keep`."""
    px = img.load()
    for y in range(max(0, y0), min(H, y1)):
        t = (y - y0) / max(1, y1 - y0)
        f = f0 + (f1 - f0) * t
        for x in range(W):
            r, g, b = px[x, y]
            if max(r, g, b) > keep and (r > b + 30):
                continue
            px[x, y] = (int(r * f + tint[0] * (1 - f)), int(g * f + tint[1] * (1 - f)),
                        int(b * f + tint[2] * (1 - f)))


def paint_exterior():
    img = Image.new("RGB", (W, H))
    sky_and_street_back(img)
    facade(img)
    steps(img)
    pavement(img)
    shade(img, 0, 150, 0.55, 1.0, tint=(14, 16, 34))
    shade(img, 150, 200, 1.0, 0.92, tint=(14, 16, 34))
    light(img, "ellipse", [0, -60, W, 130], hx("3a3a70"), 0.12, 40)
    rain(img, 77, 900)
    vignette(img, 0.45, tint=(20, 22, 44), blur=40)
    return img


# ---------------------------------------------------------------- interior: down the nave to the altar

HY, F, E = 112, 240.0, 3.5  # horizon, focal length (px), eye height (m): 1 m at the near floor edge ~ 43 px
COLS = (5.2, 10.6, 16.0, 21.4, 26.8)
NAVE_X, AISLE_X, APSE_Z = 5.0, 8.6, 29.0
ARC_SPRING, ARC_APEX, V_SPRING = 4.3, 7.0, 9.6
RAIL_Z, STEP_Z, ALTAR_Z, REREDOS_Z = 22.6, 23.2, 26.0, 27.3
I_STONE = hx("6c6660")
I_STONE_D = hx("36302e")
I_STONE_L = hx("a49a8a")
OAK = hx("4a2c1a")
OAK_D = hx("24140c")
OAK_L = hx("8a5a34")


def P(X, Y, Z):
    s = F / Z
    return (240 + X * s, HY + (E - Y) * s)


def wall_pt(x):
    return lambda z, y: P(x, y, z)


def quad_blocks(d, fn, u0, u1, v0, v1, du, dv, color, seed, mortar=0.72):
    rnd = random.Random(seed)
    v, row = v0, 0
    while v < v1 - 1e-6:
        vb = min(v1, v + dv)
        u = u0 - (du / 2 if row % 2 else 0)
        while u < u1 - 1e-6:
            ua, ub = max(u0, u), min(u1, u + du)
            c = color(rnd, row, u)
            q = [fn(ua, v), fn(ub, v), fn(ub, vb), fn(ua, vb)]
            big = abs(q[2][1] - q[1][1]) > 3 and abs(q[1][0] - q[0][0]) + abs(q[1][1] - q[0][1]) > 4
            d.polygon(q, fill=c, outline=mul(c, mortar) if big else None)
            u += du
        v, row = vb, row + 1


def stone_color(base, var=0.08):
    return lambda rnd, row, u: mul(base, 1 + rnd.uniform(-var, var))


def vault(img):
    d = ImageDraw.Draw(img)
    prof = arch_curve(-NAVE_X, NAVE_X, V_SPRING, 0.62, 16, up=1, sq=0.45)
    bays = list(zip(COLS[:-1], COLS[1:])) + [(COLS[-1], APSE_Z)]
    for z0, z1 in reversed(bays):
        steps_ = 10
        for j in range(steps_):
            za, zb = z0 + (z1 - z0) * j / steps_, z0 + (z1 - z0) * (j + 1) / steps_
            t = (j + 0.5) / steps_
            for i in range(len(prof) - 1):
                (xa, ya), (xb, yb) = prof[i], prof[i + 1]
                lateral = abs((xa + xb) / 2) / NAVE_X > abs(2 * t - 1)
                h = ((ya + yb) / 2 - V_SPRING) / 2.7
                col = mix(hx("7a7064"), hx("4a4446"), h * 0.8)
                col = mul(col, 0.82 if lateral else 1.0)
                if (xa + xb) / 2 < 0 and lateral:
                    col = mul(col, 0.9)
                d.polygon([P(xa, ya, za), P(xb, yb, za), P(xb, yb, zb), P(xa, ya, zb)], fill=col)
    rib = hx("b0a490")
    rib_d = hx("2e2826")
    for z0, z1 in bays:
        n = 24
        diag1 = [P(-NAVE_X + 2 * NAVE_X * t / n, _arch_y(prof, -NAVE_X + 2 * NAVE_X * t / n), z0 + (z1 - z0) * t / n)
                 for t in range(n + 1)]
        diag2 = [P(NAVE_X - 2 * NAVE_X * t / n, _arch_y(prof, NAVE_X - 2 * NAVE_X * t / n), z0 + (z1 - z0) * t / n)
                 for t in range(n + 1)]
        w = max(1, int(0.22 * F / ((z0 + z1) / 2)))
        for line in (diag1, diag2):
            d.line([(x, y + 1) for x, y in line], fill=rib_d, width=w)
            d.line(line, fill=rib, width=w)
        d.line([P(0, _arch_y(prof, 0), z0), P(0, _arch_y(prof, 0), z1)], fill=rib, width=max(1, w - 1))
        boss = P(0, _arch_y(prof, 0), (z0 + z1) / 2)
        r = max(1, w)
        d.ellipse([boss[0] - r - 1, boss[1] - r, boss[0] + r + 1, boss[1] + r], fill=hx("c8a050"))
    for z in COLS:
        w = max(1, int(0.32 * F / z))
        line = [P(x, y, z) for x, y in prof]
        d.line([(x, y + w) for x, y in line], fill=rib_d, width=w)
        d.line(line, fill=rib, width=w)


def _arch_y(prof, x):
    for (xa, ya), (xb, yb) in zip(prof, prof[1:]):
        if min(xa, xb) <= x <= max(xa, xb) and xa != xb:
            return ya + (yb - ya) * (x - xa) / (xb - xa)
    return prof[len(prof) // 2][1]


def apse(img):
    d = ImageDraw.Draw(img)
    prof = arch_curve(-NAVE_X, NAVE_X, V_SPRING, 0.62, 16, up=1, sq=0.45)
    poly = [P(-NAVE_X, 0.45, APSE_Z)] + [P(x, y, APSE_Z) for x, y in prof] + [P(NAVE_X, 0.45, APSE_Z)]
    d.polygon(poly, fill=hx("4a4240"))
    quad_blocks(d, lambda x, y: P(x, y, APSE_Z), -NAVE_X, NAVE_X, 0.45, V_SPRING, 0.9, 0.5,
                stone_color(hx("5a524c")), 5)
    rnd = random.Random(21)
    for x0, cols in ((-3.2, [hx("2a4fa8"), hx("b0283a"), hx("3a2a8a")]), (-0.8, [hx("d9a640"), hx("b0283a"), hx("2a4fa8")]),
                     (1.6, [hx("2a4fa8"), hx("3d8a5a"), hx("b0283a")])):
        x1 = x0 + 1.6
        outline = [P(x, y, APSE_Z) for x, y in arch_poly(x0, x1, 9.0, 4.2, 0.7, 8)[1:-1]]
        poly = [P(x0, 4.2, APSE_Z)] + outline + [P(x1, 4.2, APSE_Z)]
        d.polygon(poly, fill=hx("101018"))
        layer = img.copy()
        glass_cells(ImageDraw.Draw(layer), lambda u, v: P(u, v, APSE_Z), x0, x1, 4.2, 10.2, 2, 8, cols, rnd,
                    hx("101018"))
        img.paste(layer, (0, 0), mask_of(img.size, [poly]))
        d = ImageDraw.Draw(img)
        d.line(outline, fill=hx("8a8070"))
        light(img, "polygon", poly, hx("8098e0"), 0.25, 4)


def side_aisle(img, side):
    d = ImageDraw.Draw(img)
    s = side
    X = s * AISLE_X
    z0, z1 = COLS[0], COLS[-1]
    # ceiling of the aisle, its outer wall and the floor beyond the arcade
    d.polygon([P(s * NAVE_X, 6.4, z0), P(X, 6.4, z0), P(X, 6.4, z1), P(s * NAVE_X, 6.4, z1)], fill=hx("24201e"))
    wall = [P(X, 0, z0), P(X, 6.4, z0), P(X, 6.4, z1), P(X, 0, z1)]
    d.polygon(wall, fill=hx("4a4440"))
    quad_blocks(d, wall_pt(X), z0, z1, 0, 6.4, 0.9, 0.45, stone_color(hx("4e4842")), 30 + s)
    cols = [hx("b0283a"), hx("c8402a"), hx("d9a640"), hx("7a2040"), hx("2a4fa8")] if s < 0 else \
        [hx("2a4fa8"), hx("1e3a8a"), hx("4a78c8"), hx("d9a640"), hx("7a3a9a")]
    rnd = random.Random(40 + s)
    for za, zb in zip(COLS[:-1], COLS[1:]):
        wa, wb = za + 1.0, zb - 1.0
        d.line([P(X, 0, za), P(X, 6.4, za)], fill=hx("2a2420"), width=max(1, int(0.5 * F / za)))
        outline = arch_curve(wa, wb, 4.6, 0.7, 10, up=1)
        poly = [P(X, 1.5, wa)] + [P(X, y, z) for z, y in outline] + [P(X, 1.5, wb)]
        d.polygon(poly, fill=hx("2a2228"))
        lead = hx("140e12")
        m = mask_of(img.size, [poly])
        layer = img.copy()
        ld = ImageDraw.Draw(layer)
        glass_cells(ld, lambda u, v: P(X, v, u), wa, wb, 1.5, 6.4, 4, 12, cols, rnd, lead)
        img.paste(layer, (0, 0), m)
        d = ImageDraw.Draw(img)
        mid = (wa + wb) / 2
        d.line([P(X, 1.5, mid), P(X, 4.6, mid)], fill=hx("6a6058"), width=max(1, int(0.14 * F / mid)))
        d.line(poly + [poly[0]], fill=hx("7a7064"), width=max(1, int(0.12 * F / mid)))
        d.line([P(X, 1.45, wa - 0.2), P(X, 1.45, wb + 0.2)], fill=hx("8a8070"), width=max(1, int(0.12 * F / mid)))
        light(img, "polygon", poly, cols[0], 0.35, 3)
        light(img, "polygon", poly, hx("fff0e0"), 0.12, 2)
    d.polygon([P(s * NAVE_X, 0, z0), P(X, 0, z0), P(X, 0, z1), P(s * NAVE_X, 0, z1)], fill=hx("2e2826"))


def nave_wall(img, side):
    s = side
    X = s * NAVE_X
    z0, z1 = COLS[0], APSE_Z
    layer = Image.new("RGB", img.size, I_STONE)
    d = ImageDraw.Draw(layer)
    quad_blocks(d, wall_pt(X), z0, z1, 0, V_SPRING, 0.9, 0.45, stone_color(hx("6a645c")), 50 + s)
    holes = []
    for za, zb in zip(COLS[:-1], COLS[1:]):
        a, b = za + 0.45, zb - 0.45
        curve = arch_curve(a, b, ARC_SPRING, 0.62, 16, up=1)
        holes.append([P(X, 0, a)] + [P(X, y, z) for z, y in curve] + [P(X, 0, b)])
        # moulded arch orders around the opening
        for off, col, wd in ((0.35, hx("8a8274"), 0.16), (0.12, hx("3a3432"), 0.1)):
            c2 = arch_curve(a - off, b + off, ARC_SPRING, 0.62, 16, up=1)
            d.line([P(X, y, z) for z, y in c2], fill=col, width=max(1, int(wd * F / ((za + zb) / 2))))
        # triforium: a dark blind arcade
        for k in range(5):
            ta = a + (b - a) * k / 5 + 0.12
            tb = a + (b - a) * (k + 1) / 5 - 0.12
            tri = [P(X, 7.2, ta)] + [P(X, y, z) for z, y in arch_curve(ta, tb, 7.75, 0.7, 6, up=1)] + [P(X, 7.2, tb)]
            d.polygon(tri, fill=hx("1c1818"))
        d.line([P(X, 7.15, a), P(X, 7.15, b)], fill=hx("9a9282"), width=max(1, int(0.1 * F / za)))
        d.line([P(X, 8.05, a), P(X, 8.05, b)], fill=hx("9a9282"), width=max(1, int(0.1 * F / za)))
        # clerestory: a pair of glowing lancets per bay
        rnd = random.Random(int(za * 10) + s)
        for k in range(2):
            ca = a + (b - a) * (0.12 + 0.46 * k)
            cb = ca + (b - a) * 0.3
            cl = [P(X, 8.2, ca)] + [P(X, y, z) for z, y in arch_curve(ca, cb, 9.1, 0.7, 6, up=1)] + [P(X, 8.2, cb)]
            d.polygon(cl, fill=hx("101018"))
            sub = mask_of(img.size, [cl])
            gl = layer.copy()
            glass_cells(ImageDraw.Draw(gl), lambda u, v: P(X, v, u), ca, cb, 8.2, 9.9, 2, 4,
                        [hx("2a4fa8"), hx("b0283a"), hx("d9a640"), hx("3a2a7a")], rnd, hx("101018"))
            layer.paste(gl, (0, 0), sub)
    poly = [P(X, 0, z0), P(X, V_SPRING, z0), P(X, V_SPRING, z1), P(X, 0, z1)]
    img.paste(layer, (0, 0), mask_of(img.size, [poly], holes))


def floor(img):
    d = ImageDraw.Draw(img)
    marble = (hx("6a625a"), hx("3a3230"))

    def tile(rnd, row, u):
        c = marble[(row + int(math.floor(u / 0.9 + 100))) % 2]
        return mul(c, 1 + rnd.uniform(-0.06, 0.06))

    fn = lambda x, z: P(x, 0, z)
    quad_blocks(d, fn, -AISLE_X, AISLE_X, 4.2, STEP_Z, 0.9, 0.9, tile, 3, mortar=0.85)
    # crimson runner down the central aisle
    d.polygon([P(-0.75, 0, 4.0), P(0.75, 0, 4.0), P(0.75, 0, STEP_Z), P(-0.75, 0, STEP_Z)], fill=hx("6a1418"))
    for x in (-0.62, 0.62):
        d.line([P(x, 0, 4.0), P(x, 0, STEP_Z)], fill=hx("b08a3a"))
    for x in (-0.75, 0.75):
        d.line([P(x, 0, 4.0), P(x, 0, STEP_Z)], fill=hx("2a0a0c"))
    noise(img, (180, 140, 300, H), 5, 7)
    # sanctuary: two steps up to a pale marble floor
    for z, y0, y1 in ((STEP_Z, 0, 0.22), (STEP_Z + 0.35, 0.22, 0.45)):
        d.polygon([P(-NAVE_X, y0, z), P(NAVE_X, y0, z), P(NAVE_X, y1, z), P(-NAVE_X, y1, z)], fill=hx("8a8274"))
        d.polygon([P(-NAVE_X, y1, z), P(NAVE_X, y1, z), P(NAVE_X, y1, z + 0.35), P(-NAVE_X, y1, z + 0.35)],
                  fill=hx("c8beaa"))
    quad_blocks(d, lambda x, z: P(x, 0.45, z), -NAVE_X, NAVE_X, STEP_Z + 0.7, APSE_Z, 1.0, 1.0,
                lambda rnd, row, u: (hx("b4ab98"), hx("8a3a30"))[(row + int(u + 100)) % 2], 8, mortar=0.9)


def column(img, X, Z, near=False):
    d = ImageDraw.Draw(img)
    s = F / Z
    r = 0.45
    xa, xb = 240 + (X - r) * s, 240 + (X + r) * s
    yb = HY + E * s
    yc = HY + (E - ARC_SPRING) * s
    top = HY + (E - V_SPRING) * s
    # clustered shafts: a core with four attached colonnettes, lit warmly from the sanctuary side
    toward = -1 if X > 0 else 1
    n = 7
    for i in range(n):
        t = (i + 0.5) / n
        x0, x1 = xa + (xb - xa) * i / n, xa + (xb - xa) * (i + 1) / n
        lit = t if toward > 0 else 1 - t
        shade = 0.45 + 0.75 * lit * (1 - abs(2 * t - 1) * 0.3)
        col = mul(hx("7a7268"), shade)
        if i % 2 == 0:
            col = mul(col, 1.08)
        d.rectangle([x0, yc, x1, yb], fill=col)
        if i % 2 == 0 and x1 - x0 >= 2:
            d.line([(x0, yc), (x0, yb)], fill=mul(col, 0.7))
    # vaulting shaft carried up the nave wall to the springing of the ribs
    vx0, vx1 = 240 + (X + toward * r * 0.2 - 0.14) * s, 240 + (X + toward * r * 0.2 + 0.14) * s
    d.rectangle([vx0, top, vx1, yc], fill=hx("8a8274"))
    d.line([(vx0, top), (vx0, yc)], fill=hx("4a4440") if toward > 0 else hx("b8ae9c"))
    d.rectangle([vx0 - 0.1 * s, top - 0.2 * s, vx1 + 0.1 * s, top], fill=hx("c0b49c"))
    # foliage capital and abacus
    d.rectangle([xa - 0.12 * s, yc - 0.12 * s, xb + 0.12 * s, yc + 0.35 * s], fill=hx("8a8070"))
    rnd = random.Random(int(Z * 7))
    for _ in range(int(s * 1.2)):
        px = rnd.uniform(xa - 0.1 * s, xb + 0.1 * s)
        py = rnd.uniform(yc, yc + 0.33 * s)
        d.point((px, py), fill=rnd.choice((hx("b8aa90"), hx("5a5248"), hx("c8a860"))))
    d.rectangle([xa - 0.18 * s, yc - 0.2 * s, xb + 0.18 * s, yc - 0.05 * s], fill=hx("b8ae9c"))
    # moulded plinth
    if not near:
        d.rectangle([xa - 0.15 * s, yb - 0.55 * s, xb + 0.15 * s, yb], fill=hx("5a524a"))
        d.line([(xa - 0.15 * s, yb - 0.55 * s), (xb + 0.15 * s, yb - 0.55 * s)], fill=hx("a49a8a"))
        d.rectangle([xa - 0.05 * s, yb - 0.75 * s, xb + 0.05 * s, yb - 0.55 * s], fill=hx("6a6258"))


def pews(img):
    d = ImageDraw.Draw(img)
    rows = []
    z = 9.8
    while z < RAIL_Z - 0.8:
        rows.append(z)
        z += 0.95
    for z in reversed(rows):
        s = F / z
        for side in (-1, 1):
            xi, xo = side * 1.0, side * 4.4
            top, bot = 0.95, 0.05
            back = [P(xi, top, z), P(xo, top, z), P(xo, bot, z), P(xi, bot, z)]
            d.polygon(back, fill=OAK)
            # panelled back
            if s > 14:
                for k in range(1, 6):
                    px = xi + (xo - xi) * k / 6
                    d.line([P(px, top - 0.12, z), P(px, bot + 0.1, z)], fill=OAK_D)
            d.line([P(xi, bot + 0.02, z), P(xo, bot + 0.02, z)], fill=OAK_D, width=max(1, int(0.08 * s)))
            # moulded top rail catching the candlelight
            d.polygon([P(xi, top + 0.04, z), P(xo, top + 0.04, z), P(xo, top + 0.04, z + 0.12),
                       P(xi, top + 0.04, z + 0.12)], fill=OAK_L)
            d.line([P(xi, top, z), P(xo, top, z)], fill=hx("b07a48"))
            # aisle-facing pew end with a carved poppy-head
            end = [P(xi, 0, z - 0.05), P(xi, 1.0, z - 0.05), P(xi, 1.12, z + 0.25), P(xi, 1.0, z + 0.6),
                   P(xi, 0, z + 0.6)]
            d.polygon(end, fill=mul(OAK, 1.25))
            d.line([end[0], end[1], end[2], end[3]], fill=OAK_L)
            if s > 16:
                c = P(xi, 0.6, z + 0.27)
                d.point(c, fill=OAK_D)
    # deep shadow between rows and under the benches
    shadow(img, "polygon", [P(-4.6, 0, 9.6), P(-1.0, 0, 9.6), P(-1.0, 0, RAIL_Z), P(-4.6, 0, RAIL_Z)], 0.35, 3)
    shadow(img, "polygon", [P(1.0, 0, 9.6), P(4.6, 0, 9.6), P(4.6, 0, RAIL_Z), P(1.0, 0, RAIL_Z)], 0.35, 3)


def sanctuary(img):
    d = ImageDraw.Draw(img)
    # reredos: a gilded Gothic screen with a great crucifix
    z = REREDOS_Z
    rx = 3.1
    d.polygon([P(-rx, 0.45, z), P(-rx, 5.0, z), P(rx, 5.0, z), P(rx, 0.45, z)], fill=hx("6a5030"))
    for k in range(7):
        x0 = -rx + 2 * rx * k / 7 + 0.08
        x1 = -rx + 2 * rx * (k + 1) / 7 - 0.08
        tall = k == 3
        top = 7.6 if tall else (6.0 if k in (2, 4) else 5.4)
        d.polygon([P(x0, 1.6, z), P(x0, top - 0.8, z), P((x0 + x1) / 2, top, z), P(x1, top - 0.8, z), P(x1, 1.6, z)],
                  fill=hx("8a6a34") if not tall else hx("4a2a20"))
        d.line([P(x0, top - 0.8, z), P((x0 + x1) / 2, top, z), P(x1, top - 0.8, z)], fill=hx("e8c870"))
        d.line([P((x0 + x1) / 2, top, z), P((x0 + x1) / 2, top + 0.5, z)], fill=hx("e8c870"))
        if not tall:
            n = P((x0 + x1) / 2, 2.0, z)
            m = P((x0 + x1) / 2, 3.6, z)
            d.polygon(arch_poly(n[0] - 2, n[0] + 2, m[1], n[1], 0.7, 4), fill=hx("2a1a14"))
            d.line([(n[0], m[1] + 1), (n[0], n[1] - 1)], fill=hx("e0d0b0"))
    for x in (-rx, rx):
        d.line([P(x, 0.45, z), P(x, 6.8, z)], fill=hx("e8c870"))
        pa = P(x, 6.8, z)
        d.polygon([(pa[0] - 2, pa[1]), (pa[0], pa[1] - 8), (pa[0] + 2, pa[1])], fill=hx("c8a050"))
    d.line([P(-rx, 1.6, z), P(rx, 1.6, z)], fill=hx("e8c870"))
    light(img, "polygon", [P(-rx, 0.45, z), P(-rx, 7.6, z), P(rx, 7.6, z), P(rx, 0.45, z)], hx("ffc060"), 0.28, 6)
    # the crucifix is painted over the screen's glow so the candlelight does not wash it out
    cx, cy0 = P(0, 2.3, z)
    _, cy1 = P(0, 6.4, z)
    _, ca = P(0, 5.5, z)
    cx, cy0, cy1, ca = round(cx), round(cy0), round(cy1), round(ca)
    hw = round(0.8 * F / z) + 1
    # the great crucifix: a dark wooden cross, gilt-edged where the candles catch its left and top faces,
    # its four ends flared into gilt terminals, with an ivory corpus
    wood, edge, wood_d = hx("4a2614"), hx("b88a38"), hx("100804")
    gilt, gilt_l, gilt_d = hx("d8b050"), hx("fff4c0"), hx("6a4818")
    d.rectangle([cx + 1, cy1 + 2, cx + 4, cy0 + 2], fill=hx("1e100a"))
    d.rectangle([cx - hw + 2, ca + 2, cx + hw + 2, ca + 4], fill=hx("1e100a"))
    d.rectangle([cx - 2, cy1, cx + 2, cy0], fill=wood)
    d.rectangle([cx - hw, ca - 1, cx + hw, ca + 2], fill=wood)
    d.line([(cx - 2, cy1), (cx - 2, cy0)], fill=edge)
    d.line([(cx + 2, cy1), (cx + 2, ca - 2)], fill=wood_d)
    d.line([(cx + 2, ca + 3), (cx + 2, cy0)], fill=wood_d)
    d.line([(cx - hw, ca - 1), (cx - 3, ca - 1)], fill=edge)
    d.line([(cx + 3, ca - 1), (cx + hw, ca - 1)], fill=edge)
    d.line([(cx - hw, ca + 2), (cx - 3, ca + 2)], fill=wood_d)
    d.line([(cx + 3, ca + 2), (cx + hw, ca + 2)], fill=wood_d)
    for (tx, ty, vertical) in ((cx, cy1, True), (cx, cy0, True), (cx - hw, ca, False), (cx + hw, ca, False)):
        if vertical:
            d.rectangle([tx - 3, ty - 1, tx + 3, ty + 1], fill=gilt)
            d.line([(tx - 3, ty - 1), (tx + 2, ty - 1)], fill=gilt_l)
            d.line([(tx - 2, ty + 1), (tx + 3, ty + 1)], fill=gilt_d)
        else:
            d.rectangle([tx - 1, ty - 2, tx + 1, ty + 3], fill=gilt)
            d.line([(tx - 1, ty - 2), (tx - 1, ty + 2)], fill=gilt_l)
            d.line([(tx + 1, ty - 1), (tx + 1, ty + 3)], fill=gilt_d)
    for ox, oy in ((-4, -3), (4, -3), (-4, 4), (4, 4)):
        d.point((cx + ox, ca + oy), fill=gilt_l)
    # the corpus: title board, bowed head with a gilt halo, arms along the beam, loincloth and crossed feet
    ivory, ivory_d = hx("f4e6cc"), hx("9a7e62")
    d.line([(cx - 1, ca - 6), (cx + 1, ca - 6)], fill=hx("fff8e8"))
    d.point((cx - 1, ca - 4), fill=gilt)
    d.point((cx + 1, ca - 4), fill=gilt_l)
    d.point((cx, ca - 4), fill=gilt)
    d.rectangle([cx - 1, ca - 3, cx, ca - 2], fill=ivory)
    d.point((cx, ca - 2), fill=ivory_d)
    d.line([(cx - hw + 2, ca), (cx + hw - 2, ca)], fill=ivory)
    d.line([(cx + 2, ca + 1), (cx + hw - 2, ca + 1)], fill=ivory_d)
    d.line([(cx - hw + 2, ca + 1), (cx - 2, ca + 1)], fill=ivory_d)
    d.rectangle([cx - 1, ca - 1, cx, ca + 8], fill=ivory)
    d.line([(cx, ca + 1), (cx, ca + 8)], fill=ivory_d)
    d.line([(cx - 1, ca + 7), (cx + 1, ca + 7)], fill=hx("fffaf0"))
    d.line([(cx - 1, ca + 9), (cx - 1, ca + 13)], fill=ivory)
    d.line([(cx, ca + 9), (cx, ca + 12)], fill=ivory_d)
    d.point((cx, ca + 14), fill=ivory_d)
    d.point((cx - 1, ca + 15), fill=gilt)    # the high altar: white linen over marble, six tall candles
    za = ALTAR_Z
    ax = 1.7
    d.polygon([P(-ax, 0.45, za), P(-ax, 1.45, za), P(ax, 1.45, za), P(ax, 0.45, za)], fill=hx("d8d0bc"))
    d.polygon([P(-ax, 1.45, za), P(ax, 1.45, za), P(ax, 1.45, za + 0.8), P(-ax, 1.45, za + 0.8)], fill=hx("f4eedc"))
    d.polygon([P(-ax, 1.45, za), P(ax, 1.45, za), P(ax, 1.15, za), P(-ax, 1.15, za)], fill=hx("f8f4e8"))
    d.line([P(-0.5, 1.12, za), P(0.5, 1.12, za)], fill=hx("c8a040"))
    for k in range(3):
        x = -1.2 + 1.2 * k
        p0, p1 = P(x - 0.25, 0.6, za), P(x + 0.25, 1.05, za)
        d.rectangle([p0[0], p1[1], p1[0], p0[1]], fill=hx("b8ae98"), outline=hx("8a8070"))
    d.rectangle([P(-0.3, 1.45, za + 0.4)[0], P(0, 2.1, za + 0.4)[1], P(0.3, 1.45, za + 0.4)[0],
                 P(0, 1.45, za + 0.4)[1]], fill=hx("d8b050"))
    for x in (-1.5, -1.0, -0.55, 0.55, 1.0, 1.5):
        b = P(x, 1.45, za + 0.5)
        t = P(x, 2.6 - abs(x) * 0.25, za + 0.5)
        d.line([b, (b[0], t[1])], fill=hx("f0e8d0"))
        d.point((b[0], t[1] - 1), fill=hx("fff8c0"))
        light(img, "ellipse", [b[0] - 4, t[1] - 5, b[0] + 4, t[1] + 3], hx("ffd070"), 0.7, 2)
    # communion rail of white marble
    zr = RAIL_Z
    for side in (-1, 1):
        x0, x1 = side * 0.9, side * NAVE_X
        d.polygon([P(x0, 0, zr), P(x0, 0.85, zr), P(x1, 0.85, zr), P(x1, 0, zr)], fill=hx("a49a88"))
        k = 0.3
        x = x0
        while abs(x) < NAVE_X - 0.1:
            p0, p1 = P(x, 0.1, zr), P(x, 0.75, zr)
            d.line([p0, p1], fill=hx("3e3632"))
            x += side * k
        d.polygon([P(x0, 0.85, zr), P(x1, 0.85, zr), P(x1, 0.95, zr + 0.2), P(x0, 0.95, zr + 0.2)], fill=hx("e0d8c8"))
    # sanctuary lamp burning red
    lp = P(1.4, 4.4, 24.5)
    d.line([P(1.4, 9, 24.5), lp], fill=hx("6a5030"))
    d.ellipse([lp[0] - 1, lp[1], lp[0] + 2, lp[1] + 3], fill=hx("ff4030"))
    light(img, "ellipse", [lp[0] - 8, lp[1] - 6, lp[0] + 9, lp[1] + 10], hx("ff3020"), 0.4, 4)


def confessional(img):
    d = ImageDraw.Draw(img)
    z0, z1 = 7.9, 8.9
    x0, x1 = 5.3, 7.9
    h = 2.75
    side = [P(x0, 0, z0), P(x0, h, z0), P(x0, h, z1), P(x0, 0, z1)]
    d.polygon(side, fill=OAK_D)
    for k in (0.33, 0.66):
        zz = z0 + (z1 - z0) * k
        d.line([P(x0, 0.1, zz), P(x0, h - 0.2, zz)], fill=hx("140a06"))
    d.polygon([P(x0, h, z0), P(x1, h, z0), P(x1, h, z1), P(x0, h, z1)], fill=hx("2a1a10"))
    front = [P(x0, 0, z0), P(x0, h, z0), P(x1, h, z0), P(x1, 0, z0)]
    d.polygon(front, fill=OAK)
    s = F / z0
    w = (x1 - x0) / 3
    for k in range(3):
        a, b = x0 + w * k + 0.1, x0 + w * (k + 1) - 0.1
        top = 2.25 if k == 1 else 2.05
        pa, pb = P(a, 0.1, z0), P(b, top, z0)
        curve = [P(x, y, z0) for x, y in arch_curve(a, b, top - 0.35, 0.7, 8, up=1)]
        opening = [P(a, 0.1, z0)] + curve + [P(b, 0.1, z0)]
        if k == 1:
            d.polygon(opening, fill=hx("3a2416"))
            for yy in (0.4, 1.2):
                d.rectangle([P(a + 0.12, yy + 0.6, z0)[0], P(a, yy + 0.6, z0)[1], P(b - 0.12, yy, z0)[0],
                             P(b, yy, z0)[1]], outline=hx("24140c"))
            g = P((a + b) / 2, 1.75, z0)
            d.rectangle([g[0] - 4, g[1] - 5, g[0] + 4, g[1] + 3], fill=hx("140a06"))
            for gx in range(int(g[0]) - 3, int(g[0]) + 4, 2):
                d.line([(gx, g[1] - 4), (gx, g[1] + 2)], fill=hx("8a6a40"))
            d.point((g[0] + 5, P(0, 1.0, z0)[1]), fill=hx("c8a050"))
        else:
            d.polygon(opening, fill=hx("4a0e14"))
            for i in range(1, 5):
                xx = a + (b - a) * i / 5
                d.line([P(xx, 0.15, z0), P(xx, top - 0.4, z0)], fill=hx("300810"))
                d.line([P(xx + 0.05, 0.15, z0), P(xx + 0.05, top - 0.45, z0)], fill=hx("6a1a22"))
            d.line([P(a, top - 0.35, z0), P(b, top - 0.35, z0)], fill=hx("c8a050"))
        d.line(curve, fill=OAK_L)
    for x in (x0, x0 + w, x0 + 2 * w, x1):
        d.line([P(x, 0, z0), P(x, h, z0)], fill=hx("24140c"), width=max(1, int(0.08 * s)))
    # carved cornice with Gothic cresting and a cross
    d.polygon([P(x0 - 0.05, h, z0), P(x1 + 0.05, h, z0), P(x1 + 0.05, h - 0.18, z0), P(x0 - 0.05, h - 0.18, z0)],
              fill=OAK_L)
    for i in range(14):
        xx = x0 + (x1 - x0) * (i + 0.5) / 14
        b = P(xx, h, z0)
        d.line([b, (b[0], b[1] - 3)], fill=OAK_L)
    cx = P((x0 + x1) / 2, h, z0)
    d.line([cx, (cx[0], cx[1] - 12)], fill=hx("c8a050"), width=2)
    d.line([(cx[0] - 4, cx[1] - 8), (cx[0] + 4, cx[1] - 8)], fill=hx("c8a050"), width=2)
    light(img, "polygon", front, hx("ff9a50"), 0.12, 8)


def pedestal(img, p0, p1, s):
    """A moulded stone pedestal with a gilt IHS monogram on its front panel."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = round(p0[0]), round(p0[1]), round(p1[0]), round(p1[1])
    d.rectangle([x0, y0, x1, y1], fill=hx("8a8274"))
    d.line([(x0, y0), (x0, y1)], fill=hx("a89e8c"))
    d.line([(x1, y0), (x1, y1)], fill=hx("5e584e"))
    # cornice: a wide cap over a cavetto and a bead
    d.rectangle([x0 - 2, y0 - 2, x1 + 2, y0 + 1], fill=hx("b8ae9c"))
    d.line([(x0 - 2, y0 - 2), (x1 + 2, y0 - 2)], fill=hx("d8ccb4"))
    d.line([(x0 - 1, y0 + 2), (x1 + 1, y0 + 2)], fill=hx("6a6256"))
    for x in range(x0, x1 + 1, 2):
        d.point((x, y0 + 3), fill=hx("a49a88"))
    # recessed front panel with the IHS monogram under a small cross
    px0, py0, px1, py1 = x0 + 3, y0 + 6, x1 - 3, y0 + 19
    d.rectangle([px0, py0, px1, py1], fill=hx("766e62"), outline=hx("5a5248"))
    d.line([(px0 + 1, py1), (px1, py1)], fill=hx("a49a88"))
    d.line([(px1, py0 + 1), (px1, py1)], fill=hx("a49a88"))
    mx, my = (px0 + px1) // 2, py0 + 4
    gold, gold_l = hx("c8a050"), hx("f0d488")
    d.line([(mx - 5, my + 2), (mx - 5, my + 8)], fill=gold)  # I
    d.line([(mx - 3, my + 2), (mx - 3, my + 8)], fill=gold)  # H
    d.line([(mx - 1, my + 2), (mx - 1, my + 8)], fill=gold)
    d.line([(mx - 3, my + 5), (mx - 1, my + 5)], fill=gold)
    d.line([(mx + 3, my + 2), (mx + 1, my + 2), (mx + 1, my + 5), (mx + 3, my + 5), (mx + 3, my + 8), (mx + 1, my + 8)],
           fill=gold)  # S
    d.line([(mx - 2, my - 3), (mx - 2, my + 1)], fill=gold)
    d.line([(mx - 3, my - 2), (mx - 1, my - 2)], fill=gold)
    d.point((mx - 2, my - 3), fill=gold_l)
    # the plinth flares out at the floor
    d.rectangle([x0 - 2, y1 - 4, x1 + 2, y1], fill=hx("9a9282"))
    d.line([(x0 - 2, y1 - 4), (x1 + 2, y1 - 4)], fill=hx("c0b6a2"))


def sacred_heart(img, cx, top, foot):
    """The Sacred Heart: Christ in a white tunic and a gold-hemmed red mantle, a cruciform halo behind his head,
    his right hand raised in blessing and his left drawing the eye to the flaming heart on his breast."""
    d = ImageDraw.Draw(img)
    WHITE, WHITE_M, WHITE_D, WHITE_L = hx("e8dcc4"), hx("bcac94"), hx("8a7c6a"), hx("fff8ec")
    RED, RED_L, RED_D, RED_DD = hx("a8282c"), hx("d85448"), hx("741820"), hx("461014")
    GOLD, GOLD_L, GOLD_D = hx("d8a848"), hx("ffe090"), hx("a07830")
    SKIN, SKIN_D = hx("e8b898"), hx("b07c64")
    HAIR, HAIR_D, HAIR_L = hx("6a4024"), hx("3e2414"), hx("9a6a40")
    y = lambda k: top + k
    # a gilt halo with the arms of the cross showing round the head
    d.ellipse([cx - 7, y(-2), cx + 7, y(12)], fill=GOLD_D)
    d.ellipse([cx - 6, y(-1), cx + 6, y(11)], fill=GOLD)
    d.arc([cx - 7, y(-2), cx + 7, y(12)], 140, 260, fill=GOLD_L)
    for (ax, ay, bx, by) in ((cx - 6, y(4), cx - 4, y(4)), (cx + 4, y(4), cx + 6, y(4)), (cx, y(-1), cx, y(0))):
        d.line([(ax, ay), (bx, by)], fill=hx("b02a2a"))
    # the white tunic, from the shoulders to the hem
    d.polygon([(cx - 5, y(11)), (cx + 5, y(11)), (cx + 7, y(16)), (cx + 8, y(36)), (cx - 8, y(36)), (cx - 7, y(16))],
              fill=WHITE)
    d.line([(cx - 7, y(16)), (cx - 8, y(36))], fill=WHITE_L)
    for fx in (-4, -1, 2):
        d.line([(cx + fx, y(30)), (cx + fx + (1 if fx > 0 else -1), y(36))], fill=WHITE_M)
    d.line([(cx - 3, y(31)), (cx - 4, y(36))], fill=WHITE_L)
    # the red mantle: over his left shoulder, down his side and wrapped across the hips
    d.polygon([(cx + 2, y(10)), (cx + 6, y(11)), (cx + 9, y(17)), (cx + 10, y(29)), (cx + 9, y(35)), (cx + 2, y(34)),
               (cx - 6, y(32)), (cx - 9, y(28)), (cx - 7, y(24)), (cx + 1, y(21)), (cx + 3, y(16))], fill=RED)
    # candlelight from the left: the folds across the hips lit, the far side in shadow
    d.line([(cx - 8, y(28)), (cx - 6, y(25)), (cx + 1, y(22))], fill=RED_L)
    d.line([(cx - 5, y(27)), (cx + 3, y(24))], fill=RED_L)
    d.line([(cx - 4, y(30)), (cx + 5, y(27))], fill=RED_D)
    d.line([(cx + 9, y(17)), (cx + 10, y(29)), (cx + 9, y(35))], fill=RED_DD)
    d.line([(cx + 6, y(14)), (cx + 7, y(32))], fill=RED_D)
    d.line([(cx + 4, y(18)), (cx + 4, y(22))], fill=RED_D)
    d.line([(cx - 2, y(32)), (cx + 6, y(30))], fill=RED_D)
    # the gold hem along the mantle's edges
    d.line([(cx - 9, y(28)), (cx - 7, y(24)), (cx + 1, y(21)), (cx + 3, y(16)), (cx + 2, y(10))], fill=GOLD)
    d.line([(cx - 6, y(32)), (cx + 2, y(34)), (cx + 9, y(35))], fill=GOLD_D)
    # the tunic's hem below the mantle, and his bare feet on the little gilt base
    d.line([(cx - 7, y(36)), (cx + 7, y(36))], fill=WHITE_D)
    d.ellipse([cx - 9, y(37), cx + 9, y(41)], fill=hx("6a5a3a"))
    d.arc([cx - 9, y(37), cx + 9, y(41)], 0, 180, fill=GOLD_D)
    d.arc([cx - 9, y(37), cx + 9, y(41)], 120, 190, fill=GOLD_L)
    d.line([(cx - 8, y(39)), (cx + 8, y(39))], fill=GOLD)
    for fx in (-3, 2):
        d.line([(cx + fx, y(37)), (cx + fx + 1, y(37))], fill=SKIN)
        d.point((cx + fx + 1, y(38)), fill=SKIN_D)
    # his right hand raised in blessing, the wide sleeve falling back from the wrist
    d.polygon([(cx - 5, y(11)), (cx - 8, y(10)), (cx - 10, y(12)), (cx - 10, y(16)), (cx - 7, y(19)), (cx - 6, y(15))],
              fill=WHITE)
    d.line([(cx - 10, y(12)), (cx - 10, y(16))], fill=WHITE_L)
    d.line([(cx - 7, y(17)), (cx - 6, y(14))], fill=WHITE_M)
    d.rectangle([cx - 11, y(7), cx - 9, y(10)], fill=SKIN)
    d.line([(cx - 11, y(5)), (cx - 11, y(6))], fill=hx("f4ccb0"))
    d.line([(cx - 10, y(4)), (cx - 10, y(6))], fill=SKIN)
    d.line([(cx - 9, y(8)), (cx - 9, y(10))], fill=SKIN_D)
    d.point((cx - 8, y(8)), fill=SKIN)
    d.line([(cx - 11, y(11)), (cx - 8, y(11))], fill=WHITE_L)
    # his left hand at his side, turned to point at the heart
    d.line([(cx + 4, y(18)), (cx + 2, y(17))], fill=SKIN)
    d.point((cx + 5, y(18)), fill=WHITE_M)
    # the Sacred Heart: crowned with thorns, a flame and a small cross rising from it, rays around it
    hx0, hy0 = cx - 2, y(14)
    for (ox, oy) in ((-2, -1), (2, -1), (-3, 1), (3, 1), (0, -3), (-2, 4), (2, 4)):
        d.point((hx0 + ox, hy0 + oy), fill=GOLD_L)
    d.point((hx0 - 1, hy0), fill=hx("e03030"))
    d.point((hx0 + 1, hy0), fill=hx("c02028"))
    d.line([(hx0 - 1, hy0 + 1), (hx0 + 1, hy0 + 1)], fill=hx("c02028"))
    d.point((hx0, hy0 + 2), fill=hx("901820"))
    d.point((hx0 - 1, hy0), fill=hx("ff6050"))
    d.point((hx0 - 2, hy0 + 1), fill=hx("2e4a22"))
    d.point((hx0 + 2, hy0 + 1), fill=hx("2e4a22"))
    d.point((hx0, hy0 - 1), fill=hx("ffb040"))
    d.point((hx0, hy0 - 2), fill=GOLD)
    # long hair parted in the middle and falling to the shoulders
    d.ellipse([cx - 4, y(0), cx + 4, y(9)], fill=HAIR)
    d.polygon([(cx - 4, y(4)), (cx - 5, y(11)), (cx - 2, y(11)), (cx - 2, y(6))], fill=HAIR)
    d.polygon([(cx + 4, y(4)), (cx + 5, y(11)), (cx + 2, y(11)), (cx + 2, y(6))], fill=HAIR_D)
    d.line([(cx - 4, y(4)), (cx - 4, y(10))], fill=HAIR_L)
    d.point((cx, y(0)), fill=HAIR_D)
    # the face, a short forked beard, and the eyes looking down to whoever kneels at the rack
    d.ellipse([cx - 2, y(2), cx + 2, y(8)], fill=SKIN)
    d.line([(cx + 2, y(4)), (cx + 2, y(6))], fill=SKIN_D)
    d.point((cx - 1, y(4)), fill=hx("5a3626"))
    d.point((cx + 1, y(4)), fill=hx("5a3626"))
    d.point((cx, y(5)), fill=SKIN_D)
    d.point((cx - 2, y(4)), fill=hx("fff0e0"))
    d.line([(cx - 1, y(6)), (cx + 1, y(6))], fill=HAIR)
    d.polygon([(cx - 2, y(7)), (cx + 2, y(7)), (cx + 1, y(9)), (cx, y(10)), (cx - 1, y(9))], fill=HAIR)
    d.point((cx, y(7)), fill=hx("a85a50"))
    d.point((cx - 1, y(8)), fill=HAIR_L)
    d.point((cx + 1, y(8)), fill=HAIR_D)


def votives(img):
    d = ImageDraw.Draw(img)
    # the Sacred Heart on a pedestal, the votive rack burning at his feet
    sx, sz = -6.1, 10.0
    s = F / sz
    p0 = P(sx - 0.45, 1.25, sz)
    p1 = P(sx + 0.45, 0, sz)
    pedestal(img, p0, p1, s)
    head = P(sx, 2.9, sz)
    feet = P(sx, 1.3, sz)
    # three-tier iron rack of red glass votives
    rz = 8.9
    xa, xb = -7.0, -5.0
    rs = F / rz
    for tier, (y, dz) in enumerate(((0.55, 0.3), (0.72, 0.15), (0.89, 0.0))):
        z = rz + dz
        a, b = P(xa, y, z), P(xb, y, z)
        d.rectangle([a[0], a[1], b[0], a[1] + 0.06 * rs], fill=hx("1a1414"))
        n = 9
        rnd = random.Random(tier)
        for k in range(n):
            x = xa + (xb - xa) * (k + 0.5) / n
            c = P(x, y + 0.06, z)
            lit = rnd.random() < 0.7
            d.rectangle([c[0] - 1, c[1] - 2, c[0] + 1, c[1]], fill=hx("c02028") if lit else hx("5a1018"))
            if lit:
                d.point((c[0], c[1] - 3), fill=hx("fff0a0"))
    for x in (xa, xb):
        d.line([P(x, 0, rz), P(x, 0.92, rz)], fill=hx("1a1414"))
    d.line([P(xa - 0.1, 0.92, rz), P(xb + 0.1, 0.92, rz)], fill=hx("2a2220"))
    g0, g1 = P(xa, 1.0, rz), P(xb, 0.5, rz)
    light(img, "ellipse", [g0[0] - 18, g0[1] - 30, g1[0] + 18, g1[1] + 14], hx("ffa040"), 0.45, 10)
    light(img, "ellipse", [head[0] - 22, head[1] - 10, head[0] + 22, feet[1] + 30], hx("ffb060"), 0.22, 10)
    # painted after the glow, in colours already warmed by it, so the candlelight does not bleach him
    sacred_heart(img, round(head[0]), round(head[1]), round(feet[1]))
    stand = P(-4.3, 0, 9.2)
    top = P(-4.3, 1.1, 9.2)
    d.line([stand, top], fill=hx("2a2220"))
    d.rectangle([top[0] - 4, top[1] - 1, top[0] + 4, top[1] + 1], fill=hx("6a4a28"))


def light_and_haze(img):
    # moonlight through the left windows, falling across the nave in coloured shafts
    for za, zb in zip(COLS[1:-1], COLS[2:]):
        wa, wb = za + 1.0, zb - 1.0
        top_a, top_b = P(-AISLE_X, 5.6, wa), P(-AISLE_X, 5.6, wb)
        dx = 2.6
        floor_a, floor_b = P(-AISLE_X + dx * 2.2, 0, wa + 1.2), P(-AISLE_X + dx * 2.2, 0, wb + 1.2)
        pts = [top_a, top_b, floor_b, floor_a]
        for col, k in ((hx("c04048"), 0.14), (hx("d8b060"), 0.1)):
            light(img, "polygon", pts, col, k, 9)
        light(img, "ellipse", [floor_a[0] - 18, floor_b[1] - 4, floor_a[0] + 26, floor_a[1] + 6], hx("d05050"), 0.18, 6)
    for za, zb in zip(COLS[1:-1], COLS[2:]):
        wa, wb = za + 1.0, zb - 1.0
        top_a, top_b = P(AISLE_X, 5.6, wa), P(AISLE_X, 5.6, wb)
        floor_a, floor_b = P(AISLE_X - 5.7, 0, wa + 1.2), P(AISLE_X - 5.7, 0, wb + 1.2)
        light(img, "polygon", [top_a, top_b, floor_b, floor_a], hx("4a70d0"), 0.12, 9)
    # candle warmth gathering at the altar, incense hanging in the air
    light(img, "ellipse", [170, 60, 310, 170], hx("ffb050"), 0.3, 26)
    light(img, "ellipse", [200, 96, 280, 150], hx("ffd890"), 0.22, 12)
    rnd = random.Random(9)
    for _ in range(16):
        x, y = rnd.randint(150, 330), rnd.randint(60, 150)
        light(img, "ellipse", [x - 40, y - 7, x + 40, y + 7], hx("a89880"), 0.1, 8)
    shadow(img, "rect", [0, 0, W, 40], 0.35, 30, hx("302830"))


def paint_interior():
    img = Image.new("RGB", (W, H), hx("141012"))
    vault(img)
    apse(img)
    for side in (-1, 1):
        side_aisle(img, side)
    floor(img)
    for side in (-1, 1):
        nave_wall(img, side)
    sanctuary(img)
    for z in reversed(COLS[1:]):
        for side in (-1, 1):
            column(img, side * NAVE_X, z)
    pews(img)
    votives(img)
    confessional(img)
    for side in (-1, 1):
        column(img, side * NAVE_X, COLS[0], near=True)
    light_and_haze(img)
    shade(img, 0, 70, 0.6, 1.0, tint=(16, 12, 14))
    shade(img, 214, H, 1.0, 0.72, tint=(16, 12, 14))
    vignette(img, 0.55, tint=(40, 28, 30), blur=44)
    return img


def build():
    interior = paint_interior()
    exterior = paint_exterior()
    statue = interior.crop((80, 116, 108, 200))
    save(pixelize(interior, palette_of(interior, 128) + palette_of(statue, 12)), "rooms", "church_interior.png")
    statues = Image.new("RGB", (60, 56))
    statues.paste(exterior.crop((158, 124, 188, 180)), (0, 0))
    statues.paste(exterior.crop((298, 124, 328, 180)), (30, 0))
    save(pixelize(exterior, palette_of(exterior, 128) + palette_of(statues, 12)), "rooms", "church_exterior.png")
    return interior, exterior
