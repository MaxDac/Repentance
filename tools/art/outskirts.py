"""Outskirts of Chicago: open fields, hedgerow, road, and a distant skyline under a heavy sky."""
import math
import random
from PIL import Image, ImageDraw, ImageFilter
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save

HORIZON = 116


def sky(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, HORIZON + 18), hx("6c7686"), hx("d2ccb8"))
    for y in range(8, HORIZON - 6, 10):
        c = mix(hx("7a8392"), hx("c8c0ae"), y / max(1, HORIZON))
        d.line([(0, y), (W - 1, y)], fill=mul(c, 0.92 if y < 54 else 0.96))
    for box, col, k, blur in (
        ([18, 18, 220, 76], hx("bcc0c4"), 0.22, 14),
        ([180, 12, 388, 68], hx("d2d4d0"), 0.18, 18),
        ([286, 28, 474, 84], hx("b9c0c7"), 0.22, 16),
        ([70, 56, 428, 112], hx("e0d5ba"), 0.1, 24),
    ):
        light(img, "ellipse", box, col, k, blur)
    shadow(img, "ellipse", [-40, -14, 250, 88], 0.16, 18, hx("4a5060"))
    shadow(img, "ellipse", [180, 4, 520, 90], 0.18, 22, hx("4c5462"))
    noise(img, (0, 0, W - 1, HORIZON + 18), 4, 301)


SKY_X0, SKY_X1 = 18, 462  # the skyline spans nearly the whole horizon
LOOP_X = 248  # the tallest towers, the Loop


def _windows(d, x, w, top, base, wall, rnd, lit_p=0.035):
    """Rows of windows: a shade darker than the wall, with the odd one already lit against the dusk."""
    dark = mul(wall, 0.82)
    for yy in range(top + 2, base - 1, 3):
        for xx in range(x + 2, x + w - 1, 2):
            if rnd.random() < lit_p:
                d.point((xx, yy), fill=hx("c8ac74"))
            elif rnd.random() < 0.8:
                d.point((xx, yy), fill=dark)


def _tower(d, x, w, top, base, wall, kind, rnd, windows=True):
    """One building: a wall lit on its left edge and shaded on its right, windows, and a crown by kind -
    "flat" (perhaps a water tank on stilts), "setback" (stepped like a ziggurat), "pyramid" (a deco roof and
    lantern), "spire", "gothic" (buttressed crown and pinnacles), "clock" (a white tiered clock tower)."""
    lit, shade = mul(wall, 1.16), mul(wall, 0.8)
    if kind == "setback":
        tiers = [(x, w, top + 14), (x + 2, w - 4, top + 6), (x + 4, w - 8, top)]
        for tx, tw, tt in tiers:
            if tw < 3:
                continue
            d.rectangle([tx, tt, tx + tw, base], fill=wall)
            d.line([(tx, tt), (tx, base)], fill=lit)
            d.line([(tx + tw, tt), (tx + tw, base)], fill=shade)
            d.line([(tx, tt), (tx + tw, tt)], fill=lit)
        if windows:
            _windows(d, x, w, top + 14, base, wall, rnd)
            _windows(d, x + 4, w - 8, top + 2, top + 14, wall, rnd)
        return
    d.rectangle([x, top, x + w, base], fill=wall)
    d.line([(x, top), (x, base)], fill=lit)
    d.line([(x + w, top), (x + w, base)], fill=shade)
    if windows:
        _windows(d, x, w, top + 2, base, wall, rnd)
    cx = x + w / 2
    if kind == "pyramid":
        d.polygon([(x + 1, top), (cx, top - w * 0.7), (x + w - 1, top)], fill=mul(wall, 0.92))
        d.line([(cx, top - w * 0.7), (x + 1, top)], fill=lit)
        d.rectangle([cx - 1, top - w * 0.7 - 3, cx + 1, top - w * 0.7], fill=wall)
        d.line([(cx, top - w * 0.7 - 7), (cx, top - w * 0.7 - 3)], fill=shade)
        d.point((cx, top - w * 0.7 - 8), fill=hx("d06048"))  # an aircraft beacon, just lit
    elif kind == "spire":
        d.rectangle([x + 2, top - 6, x + w - 2, top], fill=wall)
        d.rectangle([x + 3, top - 11, x + w - 3, top - 6], fill=wall)
        d.polygon([(x + 3, top - 11), (cx, top - 26), (x + w - 3, top - 11)], fill=mul(wall, 1.05))
        d.line([(cx, top - 26), (x + 3, top - 11)], fill=lit)
        d.line([(x + 2, top - 6), (x + 2, top)], fill=lit)
    elif kind == "gothic":
        d.rectangle([x + 2, top - 8, x + w - 2, top], fill=wall)
        for bx in range(x + 2, x + w - 1, 3):  # the flying buttresses of the crown
            d.line([(bx, top - 8), (bx, top)], fill=lit)
            d.line([(bx, top - 11), (bx, top - 8)], fill=wall)
        d.line([(x + 1, top - 2), (x + 3, top - 9)], fill=wall)
        d.line([(x + w - 1, top - 2), (x + w - 3, top - 9)], fill=wall)
        d.rectangle([cx - 2, top - 14, cx + 2, top - 8], fill=wall)
        d.point((cx, top - 15), fill=wall)
    elif kind == "clock":
        white, white_d = hx("b4b0a4"), hx("8c887e")
        d.rectangle([x, top, x + w, base], fill=white)
        d.line([(x + w, top), (x + w, base)], fill=white_d)
        _windows(d, x, w, top + 2, base, white, rnd, 0.02)
        d.rectangle([x + 2, top - 8, x + w - 2, top], fill=white)
        d.ellipse([cx - 2, top - 7, cx + 2, top - 3], fill=hx("e8e4d8"), outline=white_d)
        d.rectangle([x + 3, top - 13, x + w - 3, top - 8], fill=white)
        d.polygon([(x + 3, top - 13), (cx, top - 19), (x + w - 3, top - 13)], fill=white_d)
        d.line([(cx, top - 23), (cx, top - 19)], fill=white_d)
    elif kind == "flat":
        d.rectangle([x - 1, top - 1, x + w + 1, top], fill=lit)  # the cornice
        if w > 8 and rnd.random() < 0.55:  # a timber water tank on its stilts
            tx = x + rnd.randint(2, w - 6)
            d.line([(tx, top - 3), (tx, top)], fill=shade)
            d.line([(tx + 4, top - 3), (tx + 4, top)], fill=shade)
            d.rectangle([tx, top - 7, tx + 4, top - 3], fill=mul(wall, 0.9))
            d.polygon([(tx - 1, top - 7), (tx + 2, top - 10), (tx + 5, top - 7)], fill=mul(wall, 0.9))


def skyline(img, y_base=HORIZON + 2, seed=19):
    """Chicago, wide across the horizon: a far rank of towers lost in the haze, and in front the Loop - deco setbacks
    and pyramids, a gothic crown, needle spires, a white clock tower, water tanks on the low blocks - thinning to
    gas holders, grain elevators and smoking stacks at the edges, all sinking into the smoke of the city."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    haze = hx("8a8680")

    def height(x, far):
        k = math.exp(-((x - LOOP_X) / 120) ** 2)
        return (10 + 34 * k + rnd.randint(-4, 8) * (0.4 + k)) * (0.8 if far else 1.0)

    x = SKY_X0 + 6
    while x < SKY_X1 - 6:  # the far rank, pale in the haze
        bw = rnd.randint(5, 13)
        h = height(x, True) + 6
        _tower(d, x, bw, int(y_base - h), y_base, mix(hx("5a5a62"), haze, 0.45), rnd.choice(("flat", "flat", "setback")),
               rnd, windows=False)
        x += bw + rnd.randint(0, 2)
    # the edges: industry. Gas holders, grain elevators, stacks
    for gx, gw, gh in ((30, 22, 16), (424, 26, 14)):
        col = mix(hx("4a4a50"), haze, 0.25)
        d.rectangle([gx, y_base - gh, gx + gw, y_base], fill=col)
        for k in range(gx + 2, gx + gw, 4):
            d.line([(k, y_base - gh - 2), (k, y_base)], fill=mul(col, 0.8))
        d.line([(gx - 1, y_base - gh - 2), (gx + gw + 1, y_base - gh - 2)], fill=mul(col, 0.8))
        d.line([(gx - 1, y_base - gh + 6), (gx + gw + 1, y_base - gh + 6)], fill=mul(col, 0.85))
    for ex in (64, 388):
        col = mix(hx("4e4c4e"), haze, 0.2)
        for k in range(4):
            d.rectangle([ex + k * 5, y_base - 22, ex + k * 5 + 4, y_base], fill=col)
            d.line([(ex + k * 5, y_base - 22), (ex + k * 5, y_base)], fill=mul(col, 1.15))
        d.rectangle([ex + 3, y_base - 30, ex + 13, y_base - 22], fill=col)
        d.polygon([(ex + 2, y_base - 30), (ex + 8, y_base - 35), (ex + 14, y_base - 30)], fill=col)
    stacks = (48, 92, 118, 360, 404, 448)
    for sx in stacks:
        h = rnd.randint(22, 30)
        d.rectangle([sx, y_base - h, sx + 2, y_base], fill=hx("3e3c40"))
        d.line([(sx - 1, y_base - h), (sx + 3, y_base - h)], fill=hx("2e2c30"))
    # the Loop: landmarks in their places, and the blocks between them
    landmarks = {150: ("setback", 14, 30), 176: ("spire", 7, 36), 198: ("clock", 9, 38), 214: ("gothic", 10, 44),
                 236: ("setback", 18, 40), 258: ("pyramid", 14, 50), 280: ("flat", 12, 36), 296: ("spire", 6, 42),
                 314: ("setback", 16, 30), 336: ("pyramid", 10, 26)}
    rl = random.Random(seed + 1)
    x = 104
    walls = (hx("44444c"), hx("3c3e46"), hx("4c4a50"), hx("3a3a40"))
    while x < 370:
        lm = next((v for k, v in landmarks.items() if abs(k - x) < 6), None)
        if lm:
            kind, bw, h = lm
        else:
            kind = rl.choice(("flat", "flat", "flat", "setback"))
            bw, h = rl.randint(6, 12), max(8, int(height(x, False) * rl.uniform(0.45, 0.8)))
        _tower(d, x, bw, y_base - h, y_base, rl.choice(walls), kind, rl)
        x += bw + rl.randint(1, 3)
    for x in list(range(SKY_X0 + 26, 104, 9)) + list(range(372, SKY_X1 - 24, 9)):  # low blocks out to the edges
        bw = rl.randint(5, 8)
        _tower(d, x, bw, y_base - rl.randint(6, 13), y_base, rl.choice(walls), "flat", rl)
    sm = Image.new("L", img.size, 0)  # the stacks' smoke, drifting east
    sd = ImageDraw.Draw(sm)
    for sx in stacks:
        top = y_base - 32
        for k in range(10):
            r = 2 + k * 0.9
            sd.ellipse([sx + 1 + k * 4 - r, top - k * 1.6 - r * 0.6, sx + 1 + k * 4 + r, top - k * 1.6 + r * 0.6],
                       fill=int(150 * (1 - k / 11)))
    sm = sm.filter(ImageFilter.GaussianBlur(1.6))
    img.paste(Image.composite(Image.new("RGB", img.size, hx("6e6a68")), img, sm))
    light(img, "rect", [SKY_X0 - 10, y_base - 12, SKY_X1 + 10, y_base + 4], hx("c4b89e"), 0.32, 6)  # the city's haze


def distant_fields(img):
    d = ImageDraw.Draw(img)
    d.rectangle([0, HORIZON, W - 1, 160], fill=hx("66704c"))
    d.polygon([(0, HORIZON), (W, HORIZON), (W, 150), (0, 144)], fill=hx("6f7754"))
    d.polygon([(0, 132), (W, 126), (W, 140), (0, 147)], fill=hx("8a815e"))
    d.polygon([(0, HORIZON + 4), (148, HORIZON + 2), (248, 128), (0, 140)], fill=hx("73744d"))
    d.polygon([(248, 128), (W, 124), (W, 144), (280, 146)], fill=hx("7f7650"))
    for pts, col in (
        ([(0, 140), (170, 130), (252, 141), (0, 156)], hx("5f6848")),
        ([(252, 141), (W, 132), (W, 156), (274, 154)], hx("706d49")),
    ):
        d.polygon(pts, fill=col)
    noise(img, (0, HORIZON, W - 1, 158), 5, 302)


def road(img):
    d = ImageDraw.Draw(img)
    left = [(228, HORIZON + 1), (262, HORIZON + 1), (334, FULL_H - 1), (160, FULL_H - 1)]
    d.polygon(left, fill=hx("8a785f"))
    d.polygon([(239, HORIZON + 8), (257, HORIZON + 8), (308, FULL_H - 1), (190, FULL_H - 1)], fill=hx("958168"))
    d.line([(245, HORIZON + 8), (208, FULL_H - 1)], fill=hx("6b5f4e"))
    d.line([(255, HORIZON + 7), (291, FULL_H - 1)], fill=hx("6b5f4e"))
    for y in range(HORIZON + 18, FULL_H, 12):
        w = (y - HORIZON) * 0.32
        d.line([(240 - w, y), (258 + w, y)], fill=hx("a18f74"))
    noise(img, (158, HORIZON, 336, FULL_H - 1), 9, 303)
    shadow(img, "polygon", [(214, HORIZON + 12), (246, HORIZON + 6), (184, FULL_H), (126, FULL_H)], 0.14, 10, hx("4e5242"))


LEAF = (hx("18261a"), hx("203220"), hx("2a4026"), hx("36502c"), hx("466234"), hx("5a7a3e"), hx("72904c"))


def foliage(d, cx, cy, rx, ry, rnd, tint=1.0, density=0.55):
    """A mass of leaves: a dark core, then clumps of leaves shaded by where they sit (lit from the overcast sky above
    and a little to the left), the brightest picked out with a glint, and single leaves breaking the outline."""
    tau = 2 * math.pi
    d.ellipse([cx - rx, cy - ry * 0.9, cx + rx, cy + ry], fill=mul(LEAF[0], tint))
    clumps = []
    for _ in range(int(rx * ry * density)):
        a, rr = rnd.uniform(0, tau), rnd.random() ** 0.5
        x, y = cx + math.cos(a) * rr * rx, cy + math.sin(a) * rr * ry
        lv = 0.55 - 0.45 * ((x - cx) / rx * 0.45 + (y - cy) / ry * 0.9) + rnd.uniform(-0.18, 0.18)
        clumps.append((lv, x, y, rnd.uniform(1.0, 2.6)))
    for lv, x, y, r in sorted(clumps):
        c = LEAF[max(0, min(len(LEAF) - 1, int(lv * len(LEAF))))]
        d.ellipse([x - r, y - r * 0.75, x + r, y + r * 0.75], fill=mul(c, tint))
        if lv > 0.78:
            d.point((x - r * 0.4, y - r * 0.5), fill=mul(LEAF[-1], tint * 1.1))
    for _ in range(int(rx * 1.4)):
        a = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
        x, y = cx + math.cos(a) * rx * rnd.uniform(0.92, 1.12), cy + math.sin(a) * ry * rnd.uniform(0.92, 1.15)
        d.point((x, y), fill=mul(LEAF[rnd.randint(2, 4)], tint))


def field_trees(img, seed=43):
    """Little elms and oaks dotted along the far fields, blue with distance."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for x, s in ((10, 1.0), (86, 0.7), (128, 0.55), (356, 0.6), (392, 0.8), (468, 1.1)):
        base = HORIZON + 8 + int(s * 4)
        d.line([(x, base), (x, base - 5 * s)], fill=hx("3a4038"))
        for k in range(3):
            fx, fy = x + rnd.uniform(-3, 3) * s, base - (7 + rnd.uniform(0, 3)) * s
            r = (3 + rnd.uniform(0, 2)) * s
            d.ellipse([fx - r, fy - r * 0.8, fx + r, fy + r * 0.8], fill=mix(hx("3e4a3a"), hx("6e7466"), 0.3 + k * 0.12))
        d.point((x - s, base - 9 * s), fill=hx("7a8070"))


def _hawthorn(d, img, x, base, rnd, lean=0):
    """A hedgerow hawthorn grown out into a small tree: a forked, gnarled trunk, branches reaching out, and crowns
    of foliage at their ends."""
    bark, bark_l = hx("2a241e"), hx("4a4034")
    d.polygon([(x - 3, base), (x + 3, base), (x + 2 + lean, base - 40), (x - 1 + lean, base - 40)], fill=bark)
    d.line([(x - 2, base), (x - 1 + lean, base - 40)], fill=bark_l)
    ends = []
    for ang, ln in ((-2.3, 26), (-1.9, 30), (-1.35, 32), (-0.9, 26), (-0.6, 20)):
        sx, sy = x + lean, base - 34 - rnd.randint(0, 6)
        ex, ey = sx + math.cos(ang) * ln, sy + math.sin(ang) * ln
        d.line([(sx, sy), ((sx + ex) / 2 + rnd.randint(-2, 2), (sy + ey) / 2), (ex, ey)], fill=bark, width=2)
        ends.append((ex, ey))
    for ex, ey in ends:
        foliage(d, ex, ey, rnd.randint(11, 15), rnd.randint(9, 12), rnd, tint=0.9)
    for ex, ey in ends[1:4]:
        foliage(d, (ex + x + lean) / 2, ey + 8, rnd.randint(9, 12), rnd.randint(7, 9), rnd, tint=0.95)
    for _ in range(14):  # the haws: dark red berries in the crown
        ex, ey = rnd.choice(ends)
        d.point((ex + rnd.randint(-10, 10), ey + rnd.randint(-4, 8)), fill=hx("7a2a22"))


def _wildflowers(d, rnd, xs, ys, n, avoid=None):
    """Queen Anne's lace, goldenrod and chicory along the field edge: stalks with white umbels, yellow plumes and
    blue stars."""
    for _ in range(n):
        x, y = rnd.randint(*xs), rnd.randint(*ys)
        if avoid and avoid(x, y):
            continue
        kind = rnd.random()
        h = rnd.randint(5, 11)
        d.line([(x, y), (x + rnd.choice((-1, 0, 1)), y - h)], fill=hx("4a5a32"))
        tx, ty = x, y - h
        if kind < 0.45:
            d.line([(tx - 2, ty), (tx + 2, ty)], fill=hx("e4e0d0"))
            d.point((tx, ty - 1), fill=hx("f4f0e4"))
            d.point((tx - 1, ty - 1), fill=hx("c8c4b4"))
        elif kind < 0.8:
            for k in range(4):
                d.point((tx + (k % 2), ty - k), fill=hx("d8b030") if k % 2 else hx("b8901e"))
            d.point((tx + 1, ty + 1), fill=hx("a8841a"))
        else:
            d.point((tx, ty), fill=hx("7a8cc8"))
            d.point((tx + 1, ty + 3), fill=hx("6a7ab4"))


def _bramble(d, x, y, rnd):
    """A bramble arching out of the hedge foot: a thorny purple cane, a few leaves, blackberries and a white flower."""
    pts = []
    span, rise = rnd.randint(10, 18) * rnd.choice((-1, 1)), rnd.randint(6, 12)
    for i in range(9):
        f = i / 8
        pts.append((x + span * f, y - rise * math.sin(math.pi * f) * (1 - 0.3 * f)))
    d.line(pts, fill=hx("4a2a30"))
    for px, py in pts[1:-1:2]:
        d.point((px, py - 1), fill=hx("6a3a3a"))
        d.ellipse([px - 1, py, px + 1, py + 2], fill=LEAF[3])
    for px, py in pts[2:-1:3]:
        d.point((px, py + 2), fill=hx("1a1020"))
    d.point(pts[4], fill=hx("ece4dc"))


def _fence_post(d, x, base, top):
    """The one fence post left standing: split, weathered oak leaning a little, a staple at the top and a strand of
    barbed wire sagging off into the hedge, its loose end hanging."""
    wood, wood_l, wood_d = hx("6a6050"), hx("8e8470"), hx("3a3428")
    d.polygon([(x, base), (x + 5, base), (x + 7, top + 1), (x + 3, top), (x + 2, top + 2)], fill=wood)
    d.line([(x, base), (x + 2, top + 2)], fill=wood_l)
    d.line([(x + 5, base), (x + 7, top + 1)], fill=wood_d)
    for k in (8, 19, 31):  # grain and splits
        d.line([(x + 3, top + k), (x + 4, top + k + 9)], fill=wood_d)
    d.line([(x + 3, top), (x + 4, top + 5)], fill=wood_d)
    d.ellipse([x + 2, top + 30, x + 4, top + 32], fill=hx("2a241c"))  # a knot
    for k in range(3):  # lichen
        d.point((x + 1 + k, top + 14 + k * 9), fill=hx("9aa070"))
    wire = [(x + 6, top + 8), (x + 20, top + 14), (x + 32, top + 16), (x + 40, top + 15)]
    d.line(wire, fill=hx("2a2a2c"))
    for px in range(x + 10, x + 40, 6):
        py = top + 8 + 8 * math.sin(math.pi * (px - x - 6) / 34)
        d.line([(px - 1, py - 1), (px + 1, py + 1)], fill=hx("2a2a2c"))
        d.line([(px - 1, py + 1), (px + 1, py - 1)], fill=hx("2a2a2c"))
    d.line([(x + 1, top + 20), (x - 6, top + 24), (x - 9, top + 34), (x - 8, top + 40)], fill=hx("2a2a2c"))
    d.point((x + 6, top + 8), fill=hx("a0a0a8"))
    d.point((x + 1, top + 20), fill=hx("a0a0a8"))


def hedge(img, seed=41):
    """The hedgerow across the field: hazel and hawthorn mounds, a darker back rank and a lit front rank, parted by
    the road and by a narrow gap someone has pushed through; hawthorn trees at either end, brambles and wildflowers
    along its foot, and the last fence post."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    road = (220, 298)
    gap = (156, 178)

    def skip(x, margin):
        return road[0] - margin < x < road[1] + margin or gap[0] - margin / 2 < x < gap[1] + margin / 2

    shadow(img, "rect", [0, 184, W - 1, 204], 0.4, 4, hx("1a2418"))
    d = ImageDraw.Draw(img)
    _hawthorn(d, img, 14, 196, rnd, lean=-2)
    _hawthorn(d, img, 466, 196, rnd, lean=2)
    for a, b in ((-12, gap[0]), (gap[1], road[0]), (road[1], W + 12)):  # the hedge's body, a ragged dark mass
        top, pts = 152, []
        for x in range(a, b + 1, 3):
            edge = min(x - a, b - x)
            top = max(140, min(160, top + rnd.choice((-2, -1, 0, 1, 2))))
            pts.append((x, top + max(0.0, 1 - edge / 26) ** 1.4 * (200 - top)))
        d.polygon(pts + [(b, 200), (a, 200)], fill=mul(LEAF[0], 0.85))
    x = -8
    while x < W + 16:  # the back rank, taller and in shade
        if not skip(x, 10):
            edge = min(abs(x - road[0]), abs(x - road[1]), abs(x - gap[0]), abs(x - gap[1]))
            s = min(1.0, 0.5 + edge / 40)
            foliage(d, x, 160 + rnd.randint(-6, 5) + (1 - s) * 14, rnd.randint(9, 20) * s, rnd.randint(10, 17) * s,
                    rnd, tint=rnd.uniform(0.72, 0.86))
        x += rnd.randint(9, 22)
    for _ in range(26):  # stems glimpsed at the foot
        x = rnd.randint(0, W - 1)
        if not skip(x, 6):
            d.line([(x, 201), (x + rnd.randint(-2, 2), 192 - rnd.randint(0, 6))], fill=hx("221c16"))
    x = -4
    while x < W + 16:  # the front rank, catching the light; now and then a paler elder
        if not skip(x, 7):
            edge = min(abs(x - road[0]), abs(x - road[1]), abs(x - gap[0]), abs(x - gap[1]))
            s = min(1.0, 0.55 + edge / 36)
            tint = 1.14 if rnd.random() < 0.18 else rnd.uniform(0.92, 1.04)
            foliage(d, x + rnd.randint(-3, 3), 181 + rnd.randint(-5, 4), rnd.randint(7, 15) * s,
                    rnd.randint(7, 12) * s, rnd, tint=tint)
        x += rnd.randint(8, 18)
    for _ in range(140):  # grass growing up against the foot, so it doesn't end in a line
        x = rnd.randint(0, W - 1)
        if 200 < x < 318:
            continue
        y = rnd.randint(194, 206)
        d.line([(x, y), (x + rnd.randint(-2, 2), y - rnd.randint(3, 8))],
               fill=rnd.choice([hx("5a6a3a"), hx("6e7a44"), hx("48562e"), hx("7e7a4a")]))
    for gx in gap:  # trampled stems and a scrap of cloth snagged in the gap
        d.line([(gx, 198), (gx + (3 if gx == gap[0] else -3), 178)], fill=hx("3a3020"))
    d.polygon([(gap[0] + 2, 176), (gap[0] + 6, 177), (gap[0] + 4, 181)], fill=hx("6a5a48"))
    _fence_post(d, 400, 198, 146)
    for x in (30, 70, 104, 136, 196, 318, 352, 438):
        _bramble(d, x, 198, rnd)
    _wildflowers(d, rnd, (0, W - 1), (198, 240), 70, avoid=lambda x, y: 186 < x < 330)
    noise(img, (0, 120, W - 1, 204), 5, 304)


def foreground(img, seed=53):
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    vgrad(img, (0, 154, W - 1, FULL_H - 1), hx("6d7148"), hx("4f5636"))
    d.polygon([(0, 168), (144, 158), (196, 182), (0, FULL_H)], fill=hx("60663f"))
    d.polygon([(304, 158), (W, 166), (W, FULL_H), (270, 188)], fill=hx("5c613b"))
    d.polygon([(0, 192), (124, 174), (188, FULL_H), (0, FULL_H)], fill=hx("56603a"))
    d.polygon([(320, 176), (W, 190), (W, FULL_H), (286, FULL_H)], fill=hx("545c37"))
    for _ in range(460):
        x = rnd.randint(0, W - 1)
        y = rnd.randint(156, FULL_H - 1)
        if 166 < x < 338 and y > 170:
            continue
        col = rnd.choice([hx("657043"), hx("76804b"), hx("49522f"), hx("857752")])
        d.line([(x, y), (x + rnd.randint(-2, 2), y - rnd.randint(2, 8))], fill=col)
    noise(img, (0, 154, W - 1, FULL_H - 1), 10, 305)
    light(img, "ellipse", [220, 148, 410, 252], hx("b8a476"), 0.09, 22)


def paint():
    img = Image.new("RGB", (W, FULL_H))
    sky(img)
    skyline(img)
    distant_fields(img)
    field_trees(img)
    road(img)
    foreground(img)
    hedge(img)
    shadow(img, "ellipse", [-20, 190, 180, 278], 0.12, 22, hx("384028"))
    light(img, "ellipse", [230, 120, 480, 250], hx("d4bc88"), 0.08, 28)
    return img


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    vignette(px, 0.58, tint=(22, 24, 30), blur=42)
    save(px, "rooms", "outskirts.png")
    return px
