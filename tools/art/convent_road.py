"""A quiet road outside the Sisters' convent at dusk: a neo-gothic stone house with its chapel gable, a tall arched
oak door behind a wrought-iron fence, a bare tree, empty sidewalk and road, gas lamps just lit under a cold
blue-violet sky.

The buildings are painted as albedo over a magenta key and lit (ambient dusk x albedo + light pools); the sky is
painted separately and shows through wherever the key survives."""
from PIL import Image, ImageDraw, ImageChops
import math
import random
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save
from .church import arch_curve, arch_poly, ashlar, mask_of
from .alley import illuminate

KEY = (255, 0, 255)
FOOT = 176       # foot of the convent facade
FENCE = 192      # fence plinth foot = back edge of the sidewalk
CURB = 240
GUTTER = 246
VP = (240, -520)
DOOR = (90, 130)           # door jambs
DOOR_SPRING = 130
LAMPS = (46, 356)
TREE = (424, 210)
STONE = hx("8a8a94")
STONE_D = hx("5a5a66")
STONE_L = hx("b4b4bc")
SLATE = hx("4a4c5c")
IRON = hx("1c1c24")
IRON_L = hx("44465a")
OAK, OAK_D, OAK_L = hx("6a3e22"), hx("3a2010"), hx("8a5a34")
WARM = (255, 178, 96)
GLASS = [hx("b0283a"), hx("2a4fa8"), hx("d9a640"), hx("3d8a5a"), hx("7a3a9a"), hx("e0d8b0")]


def stone(img, polys, base, seed, holes=(), **kw):
    xs = [p[0] for poly in polys for p in poly]
    ys = [p[1] for poly in polys for p in poly]
    box = (int(min(xs)) - 2, int(min(ys)) - 2, int(max(xs)) + 2, int(max(ys)) + 2)
    img.paste(ashlar(img.size, box, base, seed, **kw), (0, 0), mask_of(img.size, polys, holes))


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def jx(xb, y):
    return VP[0] + (xb - VP[0]) * (y - VP[1]) / (CURB - VP[1])


# --------------------------------------------------------------------------------------------- sky (emissive)

def sky():
    img = Image.new("RGB", (W, FULL_H))
    vgrad(img, (0, 0, W - 1, 90), hx("141634"), hx("3a3466"))
    vgrad(img, (0, 90, W - 1, 190), hx("3a3466"), hx("7a5e86"))
    rnd = random.Random(3)
    d = ImageDraw.Draw(img)
    for _ in range(36):
        x, y = rnd.randint(0, W - 1), rnd.randint(0, 50)
        d.point((x, y), fill=mix(hx("8890c0"), hx("e8ecff"), rnd.random() * (1 - y / 60)))
    # long thin clouds catching the last light
    for _ in range(10):
        x, y = rnd.randint(-40, 520), rnd.randint(30, 120)
        light(img, "ellipse", [x - 90, y - 3, x + 90, y + 4], hx("9a7aa8"), 0.3, 4)
        shadow(img, "ellipse", [x - 70, y + 2, x + 60, y + 7], 0.15, 3, hx("3a3466"))
    # crescent moon
    d.ellipse([436, 18, 450, 32], fill=hx("eef0ff"))
    d.ellipse([440, 15, 454, 29], fill=mix(hx("141634"), hx("3a3466"), 0.25))
    light(img, "ellipse", [412, -6, 476, 56], hx("8a90c8"), 0.25, 16)
    # far roofs beyond the garden wall: chimneys, a church tower and the odd lit window
    far = hx("2a2640")
    x = 330
    while x < W:
        bw, top = rnd.randint(16, 30), rnd.randint(104, 128)
        d.rectangle([x, top, x + bw, 190], fill=far)
        d.polygon([(x - 2, top), (x + bw // 2, top - 8), (x + bw + 2, top)], fill=far)
        if rnd.random() < 0.6:
            cx = x + rnd.randint(3, bw - 5)
            d.rectangle([cx, top - 12, cx + 3, top], fill=far)
        for wy in range(top + 6, 150, 9):
            for wx in range(x + 3, x + bw - 3, 7):
                if rnd.random() < 0.18:
                    d.rectangle([wx, wy, wx + 2, wy + 3], fill=hx("e0a058"))
        x += bw + rnd.randint(0, 4)
    d.rectangle([452, 70, 464, 190], fill=hx("221e36"))
    d.polygon([(450, 70), (458, 46), (466, 70)], fill=hx("221e36"))
    d.line([(458, 38), (458, 46)], fill=hx("221e36"))
    d.line([(455, 41), (461, 41)], fill=hx("221e36"))
    light(img, "rect", [320, 100, W, 160], hx("8a6a8a"), 0.15, 14)
    return img


# --------------------------------------------------------------------------------------------- convent (albedo)

def lancet(d, x0, x1, spring, base, lit, rnd, sill=True):
    d.polygon(arch_poly(x0 - 2, x1 + 2, spring, base + 1, 0.62), fill=STONE_L)
    glass = hx("e8b060") if lit else hx("1e2238")
    d.polygon(arch_poly(x0, x1, spring, base, 0.62), fill=glass)
    if lit:
        d.rectangle([x0, spring + 2, x1, spring + 2 + rnd.randint(4, 10)], fill=hx("c08848"))
    else:
        d.line([(x0 + 2, base - 2), (x1 - 3, spring)], fill=hx("3a4064"))
    mid = (x0 + x1) // 2
    d.line([(mid, spring - 8), (mid, base)], fill=STONE_D)
    for y in range(spring + 8, base, 9):
        d.line([(x0, y), (x1, y)], fill=STONE_D)
    if sill:
        d.rectangle([x0 - 4, base + 1, x1 + 4, base + 4], fill=STONE_L)
        d.line([(x0 - 4, base + 5), (x1 + 4, base + 5)], fill=STONE_D)
    hood = arch_curve(x0 - 4, x1 + 4, spring, 0.62)
    d.line(hood, fill=STONE_L, width=2)
    return arch_poly(x0, x1, spring, base, 0.62)


def buttress(img, x0, x1, top):
    d = ImageDraw.Draw(img)
    stone(img, [rect(x0, top, x1, FOOT)], mul(STONE, 0.92), x0, course=7)
    for y in (top + 40, top + 80):
        if y < FOOT - 10:
            d.polygon([(x0 - 2, y), (x1 + 2, y), (x1 + 2, y + 3), (x0 - 2, y + 6)], fill=STONE_L)
    d.polygon([(x0, top), (x1, top), ((x0 + x1) / 2, top - 10)], fill=STONE_L)
    d.line([(x1, top), (x1, FOOT)], fill=STONE_D)


def main_block(img, rnd, glows):
    d = ImageDraw.Draw(img)
    # steep slate roof with two dormers and a chimney
    d.polygon([(-6, 58), (238, 58), (224, 22), (8, 22)], fill=SLATE)
    for y in range(24, 58, 3):
        d.line([(8 - (y - 22) * 0.39, y), (224 + (y - 22) * 0.39, y)], fill=mul(SLATE, 0.8))
    for x in range(0, 236, 5):
        for y in range(24, 58, 6):
            d.line([(x + (y // 3) % 2 * 2, y), (x + (y // 3) % 2 * 2, y + 2)], fill=mul(SLATE, 0.85))
    d.line([(8, 22), (224, 22)], fill=mul(SLATE, 1.3))
    d.rectangle([24, 4, 34, 24], fill=mul(STONE, 0.8))
    d.rectangle([22, 2, 36, 5], fill=STONE_L)
    for dx in (44, 178):
        d.polygon([(dx, 54), (dx, 36), (dx + 9, 26), (dx + 18, 36), (dx + 18, 54)], fill=mul(STONE, 0.9))
        d.polygon(arch_poly(dx + 4, dx + 14, 40, 52, 0.62, 6), fill=hx("1e2238"))
        d.line([(dx - 1, 37), (dx + 9, 25), (dx + 19, 37)], fill=STONE_L, width=2)
    stone(img, [rect(-6, 58, 238, FOOT)], STONE, 21, course=7, lo=10, hi=22)
    d.rectangle([-6, 58, 238, 62], fill=STONE_L)
    d.line([(-6, 63), (238, 63)], fill=STONE_D)
    d.rectangle([-6, 108, 238, 110], fill=STONE_L)
    d.rectangle([-6, FOOT - 8, 238, FOOT], fill=mul(STONE, 0.75))
    d.line([(-6, FOOT - 8), (238, FOOT - 8)], fill=STONE_L)
    for (x0, lit_up, lit_dn) in ((12, False, True), (44, True, False), (162, False, False), (196, True, True)):
        p = lancet(d, x0, x0 + 18, 78, 102, lit_up, rnd)
        if lit_up:
            glows.append(p)
        p = lancet(d, x0, x0 + 18, 128, 158, lit_dn, rnd)
        if lit_dn:
            glows.append(p)
    for x in (2, 70, 148, 228):
        buttress(img, x, x + 8, 112)


def entrance_bay(img, rnd, glows):
    d = ImageDraw.Draw(img)
    stone(img, [[(74, 48), (110, 14), (146, 48), (146, FOOT), (74, FOOT)]], mul(STONE, 1.04), 23, course=6)
    d.line([(72, 49), (110, 13), (148, 49)], fill=STONE_L, width=3)
    d.line([(72, 51), (110, 16), (148, 51)], fill=STONE_D)
    for x, y in ((80, 43), (90, 34), (100, 25), (120, 25), (130, 34), (140, 43)):
        d.ellipse([x - 2, y - 3, x + 2, y + 1], fill=STONE_L)
    # cross on the apex
    d.rectangle([108, 0, 112, 14], fill=STONE_L)
    d.rectangle([104, 3, 116, 6], fill=STONE_L)
    # roundel with a quatrefoil
    d.ellipse([101, 27, 119, 45], fill=STONE_L)
    d.ellipse([103, 29, 117, 43], fill=hx("c89048"))
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        cx, cy = 110 + 3.5 * math.cos(ang), 36 + 3.5 * math.sin(ang)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=hx("e8c070"))
    d.line([(103, 36), (117, 36)], fill=STONE_D)
    d.line([(110, 29), (110, 43)], fill=STONE_D)
    glows.append([(103, 29), (117, 29), (117, 43), (103, 43)])
    # niche with the Virgin
    d.polygon(arch_poly(101, 119, 62, 98, 0.7), fill=hx("2a2a3a"))
    d.line(arch_curve(100, 120, 62, 0.7), fill=STONE_L, width=2)
    d.rectangle([98, 98, 122, 101], fill=STONE_L)
    fig = hx("c8c8cc")
    d.ellipse([107, 60, 113, 67], fill=fig)
    d.polygon([(105, 66), (115, 66), (117, 97), (103, 97)], fill=hx("8a9ab8"))
    d.polygon([(107, 68), (113, 68), (114, 96), (106, 96)], fill=fig)
    d.line([(108, 74), (112, 78)], fill=mul(fig, 0.75))
    d.arc([105, 56, 115, 66], 200, 340, fill=hx("e0c070"))
    # moulded arch around the door
    a, b = DOOR
    for i, (pa, pb) in enumerate(((a - 8, b + 8), (a - 5, b + 5), (a - 2, b + 2))):
        col = (STONE_L, mul(STONE, 0.8), mul(STONE, 1.05))[i]
        d.polygon(arch_poly(pa, pb, DOOR_SPRING, FOOT, 0.62, 18), fill=col)
    d.rectangle([a - 10, DOOR_SPRING - 3, b + 10, DOOR_SPRING], fill=STONE_L)
    door(img)


def door(img):
    d = ImageDraw.Draw(img)
    a, b = DOOR
    poly = arch_poly(a, b, DOOR_SPRING, FOOT, 0.62, 18)
    d.polygon(poly, fill=OAK)
    m = mask_of(img.size, [poly])
    planks = Image.new("RGB", img.size, OAK)
    pd = ImageDraw.Draw(planks)
    for x in range(a, b + 1, 5):
        pd.line([(x, 90), (x, FOOT)], fill=OAK_D)
        pd.line([(x + 1, 90), (x + 1, FOOT)], fill=OAK_L)
    img.paste(planks, (0, 0), m)
    mid = (a + b) // 2
    d.line([(mid, 104), (mid, FOOT)], fill=OAK_D, width=2)
    # wrought strap hinges, a grille and a ring pull
    for y in (124, 150, 168):
        d.rectangle([a + 1, y, mid - 3, y + 2], fill=IRON)
        d.rectangle([mid + 3, y, b - 1, y + 2], fill=IRON)
        d.ellipse([mid - 7, y - 1, mid - 3, y + 3], fill=IRON)
        d.ellipse([mid + 3, y - 1, mid + 7, y + 3], fill=IRON)
    d.rectangle([mid - 6, 134, mid + 6, 142], fill=hx("161420"))
    for x in range(mid - 5, mid + 6, 3):
        d.line([(x, 134), (x, 142)], fill=IRON_L)
    d.ellipse([mid + 4, 152, mid + 10, 158], outline=hx("8a7a50"))
    d.line(arch_curve(a, b, DOOR_SPRING, 0.62, 18), fill=OAK_D, width=2)
    # stone steps down to the gate
    for i, y in enumerate((FOOT, FOOT + 5, FOOT + 10)):
        x0, x1 = a - 10 - i * 3, b + 10 + i * 3
        d.rectangle([x0, y, x1, y + 5], fill=mul(STONE, 0.85))
        d.line([(x0, y), (x1, y)], fill=STONE_L)
        d.line([(x0, y + 5), (x1, y + 5)], fill=STONE_D)


CHAPEL_GLASS = []


def chapel(img, rnd, glows):
    d = ImageDraw.Draw(img)
    x0, x1, apex = 238, 334, 14
    stone(img, [[(x0, 62), (286, apex), (x1, 62), (x1, FOOT), (x0, FOOT)]], mul(STONE, 0.96), 29, course=7)
    d.line([(x0 - 3, 64), (286, apex - 2), (x1 + 3, 64)], fill=STONE_L, width=3)
    # bell-cote on the gable
    d.rectangle([278, 0, 294, apex + 4], fill=mul(STONE, 0.95))
    d.polygon(arch_poly(281, 291, 6, apex + 2, 0.62, 6), fill=hx("1a1a2a"))
    d.ellipse([283, 6, 289, 12], fill=hx("8a7040"))
    d.rectangle([276, 0, 296, 2], fill=STONE_L)
    # the great lancet, alight for vespers
    p = arch_poly(266, 306, 86, 160, 0.62, 16)
    d.polygon(arch_poly(262, 310, 86, 162, 0.62, 16), fill=STONE_L)
    d.polygon(p, fill=hx("2a2040"))
    cells = Image.new("RGB", img.size, hx("201828"))
    cd = ImageDraw.Draw(cells)
    for y in range(60, 160, 6):
        for x in range(266, 306, 5):
            cd.rectangle([x, y, x + 4, y + 5], fill=rnd.choice(GLASS), outline=hx("201828"))
    img.paste(cells, (0, 0), mask_of(img.size, [p]))
    for x in (279, 293):
        d.line([(x, 74), (x, 160)], fill=STONE_D, width=2)
    d.line(arch_curve(262, 310, 86, 0.62, 16), fill=STONE_L, width=2)
    d.rectangle([258, 162, 314, 166], fill=STONE_L)
    CHAPEL_GLASS.append(p)
    # small lancets either side
    for xa in (246, 318):
        lancet(d, xa, xa + 8, 116, 150, False, rnd, sill=False)
    d.rectangle([x0, FOOT - 8, x1, FOOT], fill=mul(STONE, 0.75))
    d.line([(x0, FOOT - 8), (x1, FOOT - 8)], fill=STONE_L)
    for (bx, top) in ((x0 - 2, 70), (x1 - 8, 70)):
        buttress(img, bx, bx + 10, top)
        d.polygon([(bx + 2, top - 10), (bx + 5, top - 24), (bx + 8, top - 10)], fill=STONE_L)


def garden_wall(img):
    d = ImageDraw.Draw(img)
    stone(img, [rect(334, 150, W + 4, FENCE)], mul(STONE, 0.85), 41, course=8, lo=12, hi=24)
    d.rectangle([334, 146, W, 151], fill=STONE_L)
    d.line([(334, 152), (W, 152)], fill=STONE_D)
    rnd = random.Random(42)
    for _ in range(26):  # ivy over the coping
        x, y = rnd.randint(336, W), rnd.randint(146, 176)
        d.ellipse([x - 3, y - 2, x + 3, y + 2], fill=rnd.choice([hx("2a3a2a"), hx("34442e"), hx("223022")]))


def yard_and_fence(img):
    d = ImageDraw.Draw(img)
    # a strip of clipped box hedge behind the railings
    d.rectangle([-2, FOOT, 334, FENCE - 8], fill=hx("2e3a2c"))
    rnd = random.Random(7)
    for x in range(0, 334, 6):
        if DOOR[0] - 20 < x < DOOR[1] + 16:
            continue
        d.ellipse([x - 4, FOOT - 6 + rnd.randint(0, 3), x + 5, FOOT + 6], fill=rnd.choice([hx("34422e"), hx("3c4a34"), hx("28342a")]))
    # plinth
    d.rectangle([-2, FENCE - 8, 336, FENCE], fill=mul(STONE, 0.8))
    d.line([(-2, FENCE - 8), (336, FENCE - 8)], fill=STONE_L)
    for x in range(0, 336, 24):
        d.line([(x, FENCE - 7), (x, FENCE)], fill=STONE_D)
    # railings with spear tips, broken by the gate
    g0, g1 = DOOR[0] - 22, DOOR[1] + 22
    for x in range(0, 334, 5):
        if g0 - 4 < x < g1 + 4:
            continue
        d.line([(x, 152), (x, FENCE - 8)], fill=IRON)
        d.polygon([(x - 1, 152), (x, 147), (x + 1, 152)], fill=IRON)
    for y in (156, FENCE - 12):
        d.line([(0, y), (g0 - 4, y)], fill=IRON, width=2)
        d.line([(g1 + 4, y), (334, y)], fill=IRON, width=2)
        d.line([(0, y - 1), (g0 - 4, y - 1)], fill=IRON_L)
        d.line([(g1 + 4, y - 1), (334, y - 1)], fill=IRON_L)
    for x in range(8, 334, 20):  # scroll ornaments
        if g0 - 6 < x < g1 + 6:
            continue
        d.arc([x - 4, 158, x + 4, 166], 0, 360, fill=IRON)
    # gate piers with stone caps
    for px in (g0 - 8, g1 + 1):
        stone(img, [rect(px, 136, px + 9, FENCE)], STONE, px, course=6, lo=4, hi=9)
        d.rectangle([px - 2, 132, px + 11, 136], fill=STONE_L)
        d.ellipse([px + 1, 124, px + 8, 132], fill=STONE_L)
    # the gate leaves stand open, swung back against the piers
    for (xa, xb) in ((g0 + 1, g0 + 9), (g1 - 9, g1 - 1)):
        for x in range(xa, xb + 1, 2):
            d.line([(x, 146), (x, FENCE - 2)], fill=IRON)
        d.line([(xa, 150), (xb, 150)], fill=IRON, width=2)
        d.line([(xa, FENCE - 6), (xb, FENCE - 6)], fill=IRON, width=2)


def ground(img):
    d = ImageDraw.Draw(img)
    rows = [FENCE, 200, 210, 222, CURB]
    vgrad(img, (0, FENCE, W - 1, CURB), hx("8a8690"), hx("9a96a0"))
    rnd = random.Random(81)
    for r in range(len(rows) - 1):
        for xb in range(-200, W + 240, 44):
            off = 0 if r % 2 else 22
            xa, xb2 = xb + off, xb + off + 44
            poly = [(jx(xa, rows[r]), rows[r]), (jx(xb2, rows[r]), rows[r]),
                    (jx(xb2, rows[r + 1]), rows[r + 1]), (jx(xa, rows[r + 1]), rows[r + 1])]
            d.polygon(poly, fill=mul(mix(hx("86828c"), hx("9a96a0"), rnd.random()), 1.0))
            d.line([poly[0], poly[3]], fill=hx("5a5662"))
        d.line([(0, rows[r]), (W, rows[r])], fill=hx("5a5662"))
    noise(img, (0, FENCE, W - 1, CURB), 5, 82)
    for _ in range(10):
        x, y = rnd.randint(0, W), rnd.randint(FENCE + 3, CURB - 3)
        for _ in range(rnd.randint(3, 6)):
            nx, ny = x + rnd.randint(-4, 4), y + rnd.randint(-1, 2)
            d.line([(x, y), (nx, ny)], fill=hx("625e6a"))
            x, y = nx, ny
    # granite curb, gutter and setts
    d.rectangle([0, CURB, W, CURB + 2], fill=hx("b0aeb8"))
    d.rectangle([0, CURB + 3, W, GUTTER], fill=hx("6a6874"))
    for x in range(0, W, 40):
        d.line([(x, CURB), (x, GUTTER)], fill=hx("5a5862"))
    d.rectangle([0, GUTTER + 1, W, GUTTER + 2], fill=hx("4a4856"))
    d.rectangle([0, GUTTER + 3, W, FULL_H], fill=hx("4a4852"))
    y, h = GUTTER + 3, 3
    while y < FULL_H:
        x = -rnd.randint(0, 8)
        while x < W:
            w = rnd.randint(7, 11)
            c = mix(hx("5a5864"), hx("6e6c78"), rnd.random())
            d.rounded_rectangle([x + 1, y, x + w - 1, y + h - 1], radius=1, fill=c)
            d.line([(x + 2, y), (x + w - 3, y)], fill=mul(c, 1.15))
            x += w
        y += h + 1
        h = min(6, h + 1)
    # dry leaves blown against the railings and the curb
    for _ in range(70):
        x = rnd.randint(0, W - 1)
        y = rnd.choice((FENCE + rnd.randint(0, 6), CURB - rnd.randint(1, 5), rnd.randint(FENCE, CURB)))
        c = rnd.choice([hx("8a5a2a"), hx("a0702e"), hx("6a3a1e"), hx("b08a40")])
        d.point((x, y), fill=c)
        d.point((x + 1, y), fill=mul(c, 0.8))


def tree(img):
    d = ImageDraw.Draw(img)
    bx, by = TREE
    rnd = random.Random(12)
    bark = hx("2a2428")
    # iron grate round the tree pit
    d.ellipse([bx - 16, by - 3, bx + 16, by + 4], fill=hx("2a2a32"))
    for x in range(bx - 14, bx + 15, 3):
        d.line([(x, by - 2), (x, by + 3)], fill=hx("4a4a56"))

    def branch(x, y, ang, ln, wdt, depth):
        if depth == 0 or ln < 3:
            return
        nx, ny = x + math.cos(ang) * ln, y - math.sin(ang) * ln
        d.line([(x, y), (nx, ny)], fill=bark, width=max(1, int(wdt)))
        n = 2 if depth > 2 else rnd.choice((1, 2, 2, 3))
        for i in range(n):
            spread = rnd.uniform(0.25, 0.6)
            a2 = ang + (spread if i % 2 else -spread) + rnd.uniform(-0.15, 0.15)
            branch(nx, ny, a2, ln * rnd.uniform(0.66, 0.82), wdt * 0.68, depth - 1)

    d.polygon([(bx - 6, by), (bx - 3, by - 20), (bx - 3, by - 70), (bx + 3, by - 70), (bx + 3, by - 20), (bx + 7, by)],
              fill=bark)
    d.line([(bx - 1, by - 4), (bx - 1, by - 66)], fill=hx("4a4048"))
    branch(bx, by - 68, math.pi / 2 + 0.35, 38, 5, 7)
    branch(bx, by - 68, math.pi / 2 - 0.3, 42, 5, 7)
    branch(bx - 1, by - 50, math.pi - 0.5, 30, 3, 5)
    branch(bx + 1, by - 56, 0.45, 28, 3, 5)


def gas_lamp(d, x):
    g = CURB - 2
    d.polygon([(x - 7, g), (x - 5, g - 4), (x - 4, g - 18), (x + 4, g - 18), (x + 5, g - 4), (x + 7, g)], fill=IRON)
    for y in (g - 18, g - 11, g - 4):
        d.rectangle([x - 5, y - 1, x + 5, y], fill=IRON_L)
    d.rectangle([x - 2, 108, x + 1, g - 18], fill=IRON)
    d.line([(x - 2, 110), (x - 2, g - 19)], fill=IRON_L)
    d.line([(x - 10, 116), (x + 10, 116)], fill=IRON, width=2)  # lamplighter's ladder bar
    d.rectangle([x - 4, 104, x + 3, 108], fill=IRON)
    # four-pane lantern with a crown
    d.polygon([(x - 7, 84), (x + 7, 84), (x + 4, 104), (x - 4, 104)], fill=hx("ffe6a0"))
    d.line([(x, 84), (x, 104)], fill=IRON)
    d.polygon([(x - 7, 84), (x + 7, 84), (x + 4, 104), (x - 4, 104)], outline=IRON)
    d.polygon([(x - 9, 84), (x, 74), (x + 9, 84)], fill=IRON)
    d.line([(x, 70), (x, 74)], fill=IRON)
    d.ellipse([x - 2, 67, x + 2, 71], fill=IRON)


# --------------------------------------------------------------------------------------------- assembly

def paint():
    rnd = random.Random(9)
    glows = []
    CHAPEL_GLASS.clear()
    img = Image.new("RGB", (W, FULL_H), KEY)
    garden_wall(img)
    chapel(img, rnd, glows)
    main_block(img, rnd, glows)
    entrance_bay(img, rnd, glows)
    yard_and_fence(img)
    ground(img)
    tree(img)
    # anything still magenta is open sky
    r, g, b = img.split()
    scene = ImageChops.lighter(ImageChops.lighter(r.point(lambda v: 255 if v < 200 else 0),
                                                  b.point(lambda v: 255 if v < 200 else 0)),
                               g.point(lambda v: 255 if v > 60 else 0))
    # lighting: cool dusk ambient and sky fill, gas lamps, the door lantern, window spill
    lights = [
        ("rect", [-20, -20, W + 20, 120], (40, 40, 70), 1.0, 40),
        ("ellipse", [-60, 160, 160, 262], WARM, 0.45, 20),
        ("ellipse", [250, 160, 470, 262], WARM, 0.5, 20),
        ("ellipse", [LAMPS[0] - 30, 64, LAMPS[0] + 30, 160], WARM, 0.5, 16),
        ("ellipse", [LAMPS[1] - 30, 64, LAMPS[1] + 30, 160], WARM, 0.5, 16),
        ("ellipse", [62, 96, 160, 210], WARM, 0.55, 16),   # lantern by the door
        ("ellipse", [250, 150, 320, 200], (220, 120, 140), 0.35, 14),  # coloured spill under the great window
    ]
    for p in glows:
        xs, ys = [q[0] for q in p], [q[1] for q in p]
        lights.append(("rect", [min(xs) - 8, max(ys) - 4, max(xs) + 8, max(ys) + 18], (200, 130, 70), 0.5, 6))
    lit = illuminate(img, (92, 90, 136), lights)
    out = sky()
    out.paste(lit, (0, 0), scene)
    d = ImageDraw.Draw(out)
    # emissive things on top: window glass, the lamps, the door lantern
    for p in glows:
        m = mask_of(out.size, [p])
        out.paste(Image.blend(out, ImageChops.screen(out, Image.new("RGB", out.size, (200, 140, 70))), 0.6), (0, 0), m)
    for p in CHAPEL_GLASS:
        m = mask_of(out.size, [p])
        out.paste(Image.blend(out, ImageChops.screen(out, Image.new("RGB", out.size, (70, 50, 60))), 0.8), (0, 0), m)
    lantern(d, 146, 112)
    for x in LAMPS:
        gas_lamp(d, x)
        light(out, "ellipse", [x - 30, 62, x + 30, 128], hx("ffd890"), 0.5, 12)
        light(out, "ellipse", [x - 70, 30, x + 70, 170], hx("f0b060"), 0.16, 26)
        light(out, "ellipse", [x - 8, 84, x + 8, 106], hx("fff4d0"), 0.6, 3)
    light(out, "ellipse", [126, 92, 166, 136], hx("ffd890"), 0.45, 10)
    light(out, "rect", [264, 70, 308, 160], hx("c080a0"), 0.12, 8)
    # dusk gloom: shade the bottom of the facade and the near road, cold rim on the roofs
    shadow(out, "rect", [-20, FOOT - 30, 340, FENCE], 0.2, 14, hx("4a4a80"))
    shadow(out, "rect", [-20, GUTTER, W + 20, FULL_H + 20], 0.35, 10, hx("3a3a6a"))
    light(out, "rect", [0, 20, 240, 26], hx("8a8ac0"), 0.15, 3)
    vignette(out, 0.45, tint=(24, 22, 52), blur=44)
    return out


def lantern(d, x, y):
    d.line([(x - 8, y - 8), (x, y - 8)], fill=IRON, width=2)
    d.line([(x, y - 8), (x, y - 4)], fill=IRON)
    d.polygon([(x - 6, y - 3), (x + 6, y - 3), (x, y - 8)], fill=IRON)
    d.rectangle([x - 4, y - 2, x + 4, y + 10], fill=hx("ffd890"))
    d.line([(x, y - 2), (x, y + 10)], fill=hx("6a4a2a"))
    d.rectangle([x - 4, y - 2, x + 4, y + 10], outline=IRON)
    d.polygon([(x - 3, y + 11), (x + 3, y + 11), (x, y + 15)], fill=IRON)


def build():
    img = paint()
    pal = palette_of(img, 128)
    px = pixelize(img, pal)
    save(px, "rooms", "convent_road.png")
    return px
