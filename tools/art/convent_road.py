"""A quiet road outside the Sisters' convent at dusk: a neo-gothic stone house filling the whole view, with its
entrance gable, chapel and cloister wing, a tall arched oak door behind a wrought-iron fence, empty sidewalk and
road, gas lamps just lit under a sliver of cold blue-violet sky.

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
DOOR = (94, 146)           # door jambs
DOOR_SPRING = 118
DOOR_MID = (DOOR[0] + DOOR[1]) // 2
LAMPS = (46, 440)
CHAPEL = (300, 420)
GREAT = (332, 388)         # the great lancet's jambs
EAVES = 34
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


def roof(d, x0, x1, top):
    d.polygon([(x0, EAVES), (x1, EAVES), (x1 - 10, top), (x0 + 10, top)], fill=SLATE)
    for y in range(top + 2, EAVES, 3):
        d.line([(x0, y), (x1, y)], fill=mul(SLATE, 0.8))
    for x in range(x0, x1, 5):
        for y in range(top + 2, EAVES, 6):
            d.line([(x + (y // 3) % 2 * 2, y), (x + (y // 3) % 2 * 2, y + 2)], fill=mul(SLATE, 0.85))


def wing(img, rnd, glows, x0, x1, windows, buttresses, seed):
    """A two-storey stretch of the house: slate roof, ashlar wall, string courses and rows of lancets."""
    d = ImageDraw.Draw(img)
    roof(d, x0, x1, 2)
    stone(img, [rect(x0, EAVES, x1, FOOT)], STONE, seed, course=7, lo=10, hi=22)
    d.rectangle([x0, EAVES, x1, EAVES + 4], fill=STONE_L)
    d.line([(x0, EAVES + 5), (x1, EAVES + 5)], fill=STONE_D)
    d.rectangle([x0, 94, x1, 96], fill=STONE_L)
    d.line([(x0, 97), (x1, 97)], fill=STONE_D)
    d.rectangle([x0, FOOT - 8, x1, FOOT], fill=mul(STONE, 0.75))
    d.line([(x0, FOOT - 8), (x1, FOOT - 8)], fill=STONE_L)
    for (wx, lit_up, lit_dn) in windows:
        p = lancet(d, wx, wx + 18, 56, 84, lit_up, rnd)
        if lit_up:
            glows.append(p)
        p = lancet(d, wx, wx + 18, 120, 158, lit_dn, rnd)
        if lit_dn:
            glows.append(p)
    for x in buttresses:
        buttress(img, x, x + 8, 118)


def main_block(img, rnd, glows):
    d = ImageDraw.Draw(img)
    wing(img, rnd, glows, -6, CHAPEL[0] + 6,
         ((16, False, True), (44, True, False), (186, False, False), (222, True, True), (258, False, True)),
         (2, 209, 245, 282), 21)
    # dormers and a chimney stack on the main roof
    for dx in (22, 200, 250):
        d.polygon([(dx, 32), (dx, 14), (dx + 9, 4), (dx + 18, 14), (dx + 18, 32)], fill=mul(STONE, 0.9))
        d.polygon(arch_poly(dx + 4, dx + 14, 18, 30, 0.62, 6), fill=hx("1e2238"))
        d.line([(dx - 1, 15), (dx + 9, 3), (dx + 19, 15)], fill=STONE_L, width=2)
    d.rectangle([230, -2, 242, 8], fill=mul(STONE, 0.8))
    d.rectangle([228, 6, 244, 9], fill=STONE_L)


def cloister_wing(img, rnd, glows):
    wing(img, rnd, glows, CHAPEL[1] - 6, W + 6, ((430, True, False), (458, False, True)), (), 37)


def entrance_bay(img, rnd, glows):
    d = ImageDraw.Draw(img)
    stone(img, [[(66, 40), (120, -14), (174, 40), (174, FOOT), (66, FOOT)]], mul(STONE, 1.04), 23, course=6)
    d.line([(64, 41), (120, -15), (176, 41)], fill=STONE_L, width=3)
    d.line([(64, 43), (120, -12), (176, 43)], fill=STONE_D)
    for x, y in ((72, 35), (82, 25), (92, 15), (148, 15), (158, 25), (168, 35)):
        d.ellipse([x - 2, y - 3, x + 2, y + 1], fill=STONE_L)
    # corner shafts framing the bay
    for x in (66, 168):
        d.rectangle([x, 40, x + 6, FOOT], fill=mul(STONE, 1.12))
        d.line([(x + 6, 40), (x + 6, FOOT)], fill=STONE_D)
        d.rectangle([x - 1, 40, x + 7, 43], fill=STONE_L)
    # roundel with a quatrefoil
    d.ellipse([109, 5, 131, 27], fill=STONE_L)
    d.ellipse([111, 7, 129, 25], fill=hx("c89048"))
    for k in range(4):
        ang = k * math.pi / 2 + math.pi / 4
        cx, cy = 120 + 4.5 * math.cos(ang), 16 + 4.5 * math.sin(ang)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=hx("e8c070"))
    d.line([(111, 16), (129, 16)], fill=STONE_D)
    d.line([(120, 7), (120, 25)], fill=STONE_D)
    glows.append([(111, 7), (129, 7), (129, 25), (111, 25)])
    # niche with the Virgin
    d.polygon(arch_poly(110, 130, 48, 75, 0.7), fill=hx("2a2a3a"))
    d.line(arch_curve(109, 131, 48, 0.7), fill=STONE_L, width=2)
    d.rectangle([107, 75, 133, 78], fill=STONE_L)
    fig = hx("c8c8cc")
    ox, oy = 9, -22
    d.ellipse([107 + ox, 60 + oy, 113 + ox, 67 + oy], fill=fig)
    d.polygon([(105 + ox, 66 + oy), (115 + ox, 66 + oy), (117 + ox, 97 + oy), (103 + ox, 97 + oy)], fill=hx("8a9ab8"))
    d.polygon([(107 + ox, 68 + oy), (113 + ox, 68 + oy), (114 + ox, 96 + oy), (106 + ox, 96 + oy)], fill=fig)
    d.line([(108 + ox, 74 + oy), (112 + ox, 78 + oy)], fill=mul(fig, 0.75))
    d.arc([105 + ox, 56 + oy, 115 + ox, 66 + oy], 200, 340, fill=hx("e0c070"))
    # moulded arch around the door, on clustered colonnettes with carved capitals
    a, b = DOOR
    for i, (pa, pb) in enumerate(((a - 12, b + 12), (a - 8, b + 8), (a - 4, b + 4))):
        col = (STONE_L, mul(STONE, 0.8), mul(STONE, 1.05))[i]
        d.polygon(arch_poly(pa, pb, DOOR_SPRING, FOOT, 0.62, 22), fill=col)
        d.line(arch_curve(pa, pb, DOOR_SPRING, 0.62, 22), fill=STONE_D)
    for x in (a - 10, a - 6, b + 6, b + 10):
        d.line([(x, DOOR_SPRING + 2), (x, FOOT)], fill=STONE_D)
    for x0 in (a - 13, b + 3):
        d.rectangle([x0, DOOR_SPRING - 4, x0 + 10, DOOR_SPRING + 1], fill=STONE_L)
        for k in range(3):
            d.point((x0 + 2 + k * 3, DOOR_SPRING - 2), fill=STONE_D)
    door(img)


def door(img):
    d = ImageDraw.Draw(img)
    a, b = DOOR
    poly = arch_poly(a, b, DOOR_SPRING, FOOT, 0.62, 22)
    d.polygon(poly, fill=OAK)
    m = mask_of(img.size, [poly])
    planks = Image.new("RGB", img.size, OAK)
    pd = ImageDraw.Draw(planks)
    for x in range(a, b + 1, 5):
        pd.line([(x, 80), (x, FOOT)], fill=OAK_D)
        pd.line([(x + 1, 80), (x + 1, FOOT)], fill=OAK_L)
    rnd = random.Random(5)
    for _ in range(40):  # grain and weathering
        x, y = rnd.randint(a, b), rnd.randint(86, FOOT - 4)
        pd.line([(x, y), (x, y + rnd.randint(3, 8))], fill=mul(OAK, rnd.uniform(0.75, 1.15)))
    img.paste(planks, (0, 0), m)
    mid = DOOR_MID
    d.line([(mid, 88), (mid, FOOT)], fill=OAK_D, width=2)
    # wrought strap hinges with curled ends, iron studs, a grille and two ring pulls
    for y in (110, 140, 166):
        d.rectangle([a + 1, y, mid - 4, y + 2], fill=IRON)
        d.rectangle([mid + 4, y, b - 1, y + 2], fill=IRON)
        d.ellipse([mid - 9, y - 2, mid - 3, y + 4], fill=IRON)
        d.ellipse([mid + 3, y - 2, mid + 9, y + 4], fill=IRON)
        d.arc([a + 1, y - 3, a + 7, y + 3], 90, 270, fill=IRON)
        d.arc([b - 7, y - 3, b - 1, y + 3], 270, 90, fill=IRON)
    for y in range(100, FOOT - 4, 12):
        for x in (a + 4, mid - 7, mid + 7, b - 4):
            d.point((x, y), fill=IRON_L)
    d.rectangle([mid - 9, 120, mid + 9, 130], fill=hx("161420"))
    d.rectangle([mid - 10, 119, mid + 10, 131], outline=IRON)
    for x in range(mid - 8, mid + 9, 3):
        d.line([(x, 120), (x, 130)], fill=IRON_L)
    for x in (mid - 9, mid + 3):
        d.ellipse([x, 148, x + 6, 154], outline=hx("8a7a50"))
        d.point((x + 3, 147), fill=hx("8a7a50"))
    d.line(arch_curve(a, b, DOOR_SPRING, 0.62, 22), fill=OAK_D, width=2)
    # stone steps down to the gate
    for i, y in enumerate((FOOT, FOOT + 5, FOOT + 10)):
        x0, x1 = a - 14 - i * 3, b + 14 + i * 3
        d.rectangle([x0, y, x1, y + 5], fill=mul(STONE, 0.85))
        d.line([(x0, y), (x1, y)], fill=STONE_L)
        d.line([(x0, y + 5), (x1, y + 5)], fill=STONE_D)


CHAPEL_GLASS = []


def chapel(img, rnd, glows):
    d = ImageDraw.Draw(img)
    x0, x1 = CHAPEL
    apex, top = (x0 + x1) // 2, -20
    stone(img, [[(x0, 40), (apex, top), (x1, 40), (x1, FOOT), (x0, FOOT)]], mul(STONE, 0.96), 29, course=7)
    d.line([(x0 - 3, 42), (apex, top - 2), (x1 + 3, 42)], fill=STONE_L, width=3)
    # rose window high in the gable
    d.ellipse([apex - 12, 2, apex + 12, 26], fill=STONE_L)
    rose = Image.new("RGB", img.size, hx("201828"))
    rd = ImageDraw.Draw(rose)
    for k in range(8):
        ang = k * math.pi / 4
        cx, cy = apex + 6 * math.cos(ang), 14 + 6 * math.sin(ang)
        rd.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=GLASS[k % len(GLASS)])
    rd.ellipse([apex - 3, 11, apex + 3, 17], fill=GLASS[2])
    rose_poly = [(apex + 10 * math.cos(t / 8 * math.pi), 14 + 10 * math.sin(t / 8 * math.pi)) for t in range(16)]
    img.paste(rose, (0, 0), mask_of(img.size, [rose_poly]))
    CHAPEL_GLASS.append(rose_poly)
    # the great lancet, alight for vespers
    ga, gb = GREAT
    p = arch_poly(ga, gb, 80, 162, 0.62, 18)
    d.polygon(arch_poly(ga - 5, gb + 5, 80, 164, 0.62, 18), fill=STONE_L)
    d.polygon(p, fill=hx("2a2040"))
    cells = Image.new("RGB", img.size, hx("201828"))
    cd = ImageDraw.Draw(cells)
    for y in range(40, 162, 6):
        for x in range(ga, gb, 5):
            cd.rectangle([x, y, x + 4, y + 5], fill=rnd.choice(GLASS), outline=hx("201828"))
    # a saint in red and gold in the central light
    cd.ellipse([apex - 5, 66, apex + 5, 76], fill=hx("e0c070"))
    cd.ellipse([apex - 3, 68, apex + 3, 74], fill=hx("e8d8b0"))
    cd.polygon([(apex - 6, 76), (apex + 6, 76), (apex + 8, 120), (apex - 8, 120)], fill=hx("b0283a"))
    img.paste(cells, (0, 0), mask_of(img.size, [p]))
    for x in (ga + 18, gb - 18):
        d.line([(x, 62), (x, 162)], fill=STONE_D, width=2)
    for y in (100, 130):
        d.line([(ga, y), (gb, y)], fill=STONE_D)
    d.line(arch_curve(ga - 5, gb + 5, 80, 0.62, 18), fill=STONE_L, width=2)
    d.rectangle([ga - 8, 164, gb + 8, 168], fill=STONE_L)
    CHAPEL_GLASS.append(p)
    # small lancets either side
    for xa in (x0 + 10, x1 - 20):
        lancet(d, xa, xa + 10, 104, 150, False, rnd, sill=False)
    d.rectangle([x0, FOOT - 8, x1, FOOT], fill=mul(STONE, 0.75))
    d.line([(x0, FOOT - 8), (x1, FOOT - 8)], fill=STONE_L)
    for (bx, btop) in ((x0 - 4, 50), (x1 - 6, 50)):
        buttress(img, bx, bx + 10, btop)
        d.polygon([(bx + 2, btop - 10), (bx + 5, btop - 24), (bx + 8, btop - 10)], fill=STONE_L)


def yard_and_fence(img):
    d = ImageDraw.Draw(img)
    # a strip of clipped box hedge behind the railings
    d.rectangle([-2, FOOT, W + 2, FENCE - 8], fill=hx("2e3a2c"))
    rnd = random.Random(7)
    for x in range(0, W + 6, 6):
        if DOOR[0] - 24 < x < DOOR[1] + 20:
            continue
        d.ellipse([x - 4, FOOT - 6 + rnd.randint(0, 3), x + 5, FOOT + 6], fill=rnd.choice([hx("34422e"), hx("3c4a34"), hx("28342a")]))
    # plinth
    d.rectangle([-2, FENCE - 8, W + 2, FENCE], fill=mul(STONE, 0.8))
    d.line([(-2, FENCE - 8), (W + 2, FENCE - 8)], fill=STONE_L)
    for x in range(0, W + 2, 24):
        d.line([(x, FENCE - 7), (x, FENCE)], fill=STONE_D)
    # railings with spear tips, broken by the gate
    g0, g1 = DOOR[0] - 26, DOOR[1] + 26
    for x in range(0, W + 5, 5):
        if g0 - 4 < x < g1 + 4:
            continue
        d.line([(x, 152), (x, FENCE - 8)], fill=IRON)
        d.polygon([(x - 1, 152), (x, 147), (x + 1, 152)], fill=IRON)
    for y in (156, FENCE - 12):
        d.line([(0, y), (g0 - 4, y)], fill=IRON, width=2)
        d.line([(g1 + 4, y), (W, y)], fill=IRON, width=2)
        d.line([(0, y - 1), (g0 - 4, y - 1)], fill=IRON_L)
        d.line([(g1 + 4, y - 1), (W, y - 1)], fill=IRON_L)
    for x in range(8, W, 20):  # scroll ornaments
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
    main_block(img, rnd, glows)
    cloister_wing(img, rnd, glows)
    chapel(img, rnd, glows)
    entrance_bay(img, rnd, glows)
    yard_and_fence(img)
    ground(img)
    # anything still magenta is open sky
    r, g, b = img.split()
    scene = ImageChops.lighter(ImageChops.lighter(r.point(lambda v: 255 if v < 200 else 0),
                                                  b.point(lambda v: 255 if v < 200 else 0)),
                               g.point(lambda v: 255 if v > 60 else 0))
    # lighting: cool dusk ambient and sky fill, gas lamps, the door lantern, window spill
    lights = [
        ("rect", [-20, -20, W + 20, 120], (40, 40, 70), 1.0, 40),
        ("ellipse", [LAMPS[0] - 106, 160, LAMPS[0] + 114, 262], WARM, 0.45, 20),
        ("ellipse", [LAMPS[1] - 110, 160, LAMPS[1] + 110, 262], WARM, 0.5, 20),
        ("ellipse", [LAMPS[0] - 30, 64, LAMPS[0] + 30, 160], WARM, 0.5, 16),
        ("ellipse", [LAMPS[1] - 30, 64, LAMPS[1] + 30, 160], WARM, 0.5, 16),
        ("ellipse", [DOOR_MID - 60, 70, DOOR_MID + 60, 210], WARM, 0.55, 16),   # lanterns by the door
        ("ellipse", [GREAT[0] - 20, 150, GREAT[1] + 20, 200], (220, 120, 140), 0.35, 14),  # coloured spill under the great window
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
    for lx in (DOOR[0] - 22, DOOR[1] + 22):
        lantern(d, lx, 104)
    for x in LAMPS:
        gas_lamp(d, x)
        light(out, "ellipse", [x - 30, 62, x + 30, 128], hx("ffd890"), 0.5, 12)
        light(out, "ellipse", [x - 70, 30, x + 70, 170], hx("f0b060"), 0.16, 26)
        light(out, "ellipse", [x - 8, 84, x + 8, 106], hx("fff4d0"), 0.6, 3)
    for lx in (DOOR[0] - 22, DOOR[1] + 22):
        light(out, "ellipse", [lx - 20, 84, lx + 20, 128], hx("ffd890"), 0.45, 10)
    light(out, "rect", [GREAT[0], 50, GREAT[1], 162], hx("c080a0"), 0.12, 8)
    # dusk gloom: shade the bottom of the facade and the near road, cold rim on the roofs
    shadow(out, "rect", [-20, FOOT - 30, W + 20, FENCE], 0.2, 14, hx("4a4a80"))
    shadow(out, "rect", [-20, GUTTER, W + 20, FULL_H + 20], 0.35, 10, hx("3a3a6a"))
    light(out, "rect", [0, 0, W, 6], hx("8a8ac0"), 0.15, 3)
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
