"""The convent of the Sisters of Mercy: the vaulted corridor at dusk and Eleanor's former cell by lamplight.

Overlays for the cell: the nightstand drawer pulled open (comb and hand mirror inside) and the same drawer once
the mirror has been taken."""
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import math
import random
from .common import W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save
from .furniture import Room3D
from .church import ashlar, mask_of, quad_blocks

H = FULL_H


# ---------------------------------------------------------------- shared helpers

def parch(t, k=0.72):
    """Normalised pointed-arch profile: 0 at t=0 and t=1, 1 at the apex t=0.5."""
    t = min(max(t, 0.0), 1.0)
    tt = t if t <= 0.5 else 1 - t
    r = k
    return math.sqrt(max(0.0, r * r - (r - tt) ** 2)) / math.sqrt(r * r - (r - 0.5) ** 2)


def arch_pts(a, b, spring, rise, n=16, k=0.72):
    """World (x, y) points of a pointed arch from (a, spring) over the apex to (b, spring)."""
    return [(a + (b - a) * i / n, spring + rise * parch(i / n, k)) for i in range(n + 1)]


def lancet(a, b, sill, spring, rise, n=16):
    return [(a, sill)] + arch_pts(a, b, spring, rise, n) + [(b, sill)]


def on_wall(R, pts, z=0):
    return [R.P(x, y, z) for x, y in pts]


def lightmap(img, ambient, lights):
    """Multiplies img by an ambient level plus soft additive coloured lights: keeps textures, darkens the rest."""
    lm = Image.new("RGB", img.size, ambient)
    black = Image.new("RGB", img.size, (0, 0, 0))
    for shape, pts, col, k, blur in lights:
        if shape == "mask":
            m = pts.point(lambda v: int(v * k))
        else:
            m = Image.new("L", img.size, 0)
            d = ImageDraw.Draw(m)
            if shape == "ellipse":
                d.ellipse(pts, fill=int(255 * k))
            else:
                d.polygon(pts, fill=int(255 * k))
        if blur:
            m = m.filter(ImageFilter.GaussianBlur(blur))
        lm = ImageChops.add(lm, Image.composite(Image.new("RGB", img.size, col), black, m))
    return ImageChops.multiply(img, lm)


def flame(d, x, y, big=False):
    d.point((x, y - 1), fill=hx("fff4c0"))
    d.point((x, y), fill=hx("ffd060"))
    if big:
        d.point((x, y - 2), fill=hx("ffe890"))
        d.point((x - 1, y), fill=hx("e08a30"))
        d.point((x + 1, y), fill=hx("e08a30"))


def _bbox(a, b):
    return ImageChops.difference(a, b).getbbox()


# ---------------------------------------------------------------- the corridor at dusk

CR = Room3D(184, 240, 110, 250)
C_SP, C_AP, C_ZF = 112, 172, 150  # vault springing, crown and the corridor's depth (front wall behind the camera)
SHAFTS = (2, 76, 150, 224, 298, 372, 446)
BAYS = list(zip((-72,) + SHAFTS, SHAFTS + (520,)))
WINDOW_BAYS = (2, 4, 5)
C_STONE = hx("7a7266")
C_STONE_L = hx("aca290")
C_STONE_D = hx("3c3632")
OAK, OAK_D, OAK_L = hx("4e3220"), hx("26160c"), hx("7e5434")
IRON = hx("1e1a1a")


def c_vault(img):
    d = ImageDraw.Draw(img)
    rise = C_AP - C_SP
    rnd = random.Random(71)
    nu, nv = 14, 36
    for xa, xb in BAYS:
        for j in range(nv):
            va, vb = j / nv, (j + 1) / nv
            for i in range(nu):
                ua, ub = i / nu, (i + 1) / nu
                uc, vc = (ua + ub) / 2, (va + vb) / 2

                def y_at(u, v):
                    return C_SP + rise * max(parch(u), parch(v))
                q = [(xa + (xb - xa) * u, y_at(u, v), v * C_ZF) for u, v in ((ua, va), (ub, va), (ub, vb), (ua, vb))]
                ax, az = parch(uc), parch(vc)
                h = max(ax, az)
                col = mix(hx("8a8070"), hx("3e3836"), h * 0.85)
                if ax >= az:  # webs of the cross vault running back to the wall lunette
                    col = mul(col, 0.92 if uc < 0.5 else 0.8)
                else:
                    col = mul(col, 1.0 if vc < 0.5 else 0.86)
                col = mul(col, 1 + rnd.uniform(-0.04, 0.04))
                d.polygon([CR.P(*p) for p in q], fill=col)
    rib, rib_d = hx("b4a892"), hx("2a2422")

    def rib_line(pts, w):
        sp = [CR.P(*p) for p in pts]
        d.line([(x, y + w) for x, y in sp], fill=rib_d, width=w)
        d.line(sp, fill=rib, width=w)
    n = 30
    for xa, xb in BAYS:
        rib_line([(xa + (xb - xa) * t / n, C_SP + rise * parch(t / n), C_ZF * t / n) for t in range(n + 1)], 2)
        rib_line([(xb - (xb - xa) * t / n, C_SP + rise * parch(t / n), C_ZF * t / n) for t in range(n + 1)], 2)
        rib_line([(xa, C_AP, C_ZF / 2), (xb, C_AP, C_ZF / 2)], 1)
        rib_line([(xa + (xb - xa) * t / n, C_SP + rise * parch(t / n), 0.5) for t in range(n + 1)], 2)
        bx, by = CR.P((xa + xb) / 2, C_AP, C_ZF / 2)
        d.ellipse([bx - 3, by - 2, bx + 3, by + 2], fill=hx("a88a48"), outline=hx("3a2e1a"))
    for xs in SHAFTS:
        rib_line([(xs, C_SP + rise * parch(t / n), C_ZF * t / n) for t in range(n + 1)], 3)


def c_sky(size):
    """Dusk over the convent garden and the city beyond, seen through the lancets."""
    sky = Image.new("RGB", size)
    d = ImageDraw.Draw(sky)
    for y in range(size[1]):
        t = min(1.0, max(0.0, (y - 30) / 104))
        if t < 0.55:
            c = mix(hx("1c1c40"), hx("6a3a62"), t / 0.55)
        else:
            c = mix(hx("6a3a62"), hx("e8904c"), (t - 0.55) / 0.45)
        d.line([(0, y), (size[0], y)], fill=c)
    rnd = random.Random(5)
    # distant rooftops, a water tower and a steeple against the afterglow
    x = 0
    while x < size[0]:
        bw, top = rnd.randint(10, 26), rnd.randint(108, 124)
        d.rectangle([x, top, x + bw, 140], fill=hx("2a1a2a"))
        for wy in range(top + 3, 136, 4):
            for wx in range(x + 2, x + bw - 1, 3):
                if rnd.random() < 0.12:
                    d.point((wx, wy), fill=hx("e8b060"))
        x += bw
    d.polygon([(258, 124), (262, 92), (266, 124)], fill=hx("221626"))
    d.rectangle([330, 104, 340, 112], fill=hx("221626"))
    d.line([(331, 112), (331, 124)], fill=hx("221626"))
    d.line([(339, 112), (339, 124)], fill=hx("221626"))
    # bare garden trees in the foreground
    d.rectangle([0, 128, size[0], 140], fill=hx("160e18"))
    for tx in (96, 122, 268, 318, 350):
        def branch(x0, y0, ang, ln, depth):
            x1, y1 = x0 + math.cos(ang) * ln, y0 - math.sin(ang) * ln
            d.line([(x0, y0), (x1, y1)], fill=hx("160e18"), width=max(1, depth - 1))
            if depth > 0:
                for da in (-0.5, 0.45):
                    branch(x1, y1, ang + da + rnd.uniform(-0.2, 0.2), ln * 0.68, depth - 1)
        branch(tx, 132, math.pi / 2 + rnd.uniform(-0.2, 0.2), 16, 4)
    return sky


def c_wall(img):
    polys = []
    for xa, xb in BAYS:
        polys.append(on_wall(CR, [(xa, 0), (xb, 0)] + list(reversed(arch_pts(xa, xb, C_SP, C_AP - C_SP, 20)))))
    layer = ashlar(img.size, (0, 0, W, 190), C_STONE, 81, course=7, lo=10, hi=22, var=0.08, mortar=0.68)
    noise(layer, (0, 0, W - 1, 190), 5, 82)
    img.paste(layer, (0, 0), mask_of(img.size, polys))
    d = ImageDraw.Draw(img)
    # chamfered stone plinth and a string course at the window sills
    for y0, y1, col in ((0, 9, hx("5e5850")), (42, 45, hx("8e8676"))):
        a, b = CR.P(0, y1, 0), CR.P(W, y0, 0)
        d.rectangle([0, a[1], W, b[1]], fill=col)
        d.line([(0, a[1]), (W, a[1])], fill=C_STONE_L)
    # damp and soot staining
    for x0 in (30, 190, 330, 430):
        shadow(img, "ellipse", [x0, 100, x0 + 60, 190], 0.2, 14, hx("5a5048"))


def c_shafts(img):
    d = ImageDraw.Draw(img)
    for xs in SHAFTS:
        CR.box(img, xs - 6, xs + 6, 0, 12, 0, 8, hx("6a6256"), top=C_STONE_L, side=hx("443e38"))
        CR.box(img, xs - 4, xs + 4, 12, C_SP - 8, 0, 6, hx("857c6c"), top=C_STONE_L, side=hx("4a443c"))
        a, b = CR.P(xs - 1, 12, 6), CR.P(xs - 1, C_SP - 8, 6)
        d.line([a, b], fill=hx("a49a86"))
        a, b = CR.P(xs + 3, 12, 6), CR.P(xs + 3, C_SP - 8, 6)
        d.line([a, b], fill=hx("5a5248"))
        CR.box(img, xs - 7, xs + 7, C_SP - 8, C_SP - 2, 0, 9, hx("8a8070"), top=hx("c4b8a0"), side=hx("4e463e"))
        CR.box(img, xs - 8, xs + 8, C_SP - 2, C_SP, 0, 10, hx("a49a86"), top=hx("d0c4ac"), side=hx("5a5248"))


def c_windows(img, sky):
    d = ImageDraw.Draw(img)
    glass_polys = []
    for i in WINDOW_BAYS:
        xa, xb = BAYS[i]
        xc = (xa + xb) / 2
        outer = lancet(xc - 19, xc + 19, 44, 116, 40)
        inner = lancet(xc - 12, xc + 12, 52, 118, 32)
        d.polygon(on_wall(CR, outer, 0), fill=hx("8c8474"))
        d.line(on_wall(CR, outer, 0)[1:-1], fill=hx("c8bca4"), width=2)
        # deep splayed reveal: sill lit by the glow, jambs in shade
        g = on_wall(CR, inner, -14)
        d.polygon([CR.P(xc - 19, 44, 0), CR.P(xc + 19, 44, 0), g[-1], g[0]], fill=hx("b8aa92"))
        d.polygon([CR.P(xc - 19, 44, 0), CR.P(xc - 19, 116, 0), CR.P(xc - 12, 118, -14), g[0]], fill=hx("6a6256"))
        d.polygon([CR.P(xc + 19, 44, 0), CR.P(xc + 19, 116, 0), CR.P(xc + 12, 118, -14), g[-1]], fill=hx("787062"))
        glass_polys.append(g)
    m = mask_of(img.size, glass_polys)
    gl = sky.copy()
    gd = ImageDraw.Draw(gl)
    for k in range(-60, 120):  # diamond quarries
        x = k * 7
        gd.line([(x, 0), (x + 140, 140)], fill=hx("1a1418"))
        gd.line([(x, 140), (x + 140, 0)], fill=hx("1a1418"))
    gl = Image.blend(gl, sky, 0.45)
    img.paste(gl, (0, 0), m)
    d = ImageDraw.Draw(img)
    for i, g in zip(WINDOW_BAYS, glass_polys):
        xa, xb = BAYS[i]
        xc = (xa + xb) / 2
        for y in (76, 100):
            d.line([CR.P(xc - 12, y, -14), CR.P(xc + 12, y, -14)], fill=IRON, width=1)
        d.line(g + [g[0]], fill=hx("2a2420"))
    return glass_polys


def c_entrance(img):
    """The way in from the cloister: a pointed oak door with iron strapwork."""
    d = ImageDraw.Draw(img)
    xc = 39
    for off, col in ((8, hx("948a78")), (5, hx("5a5248")), (3, hx("a89e8a"))):
        d.polygon(on_wall(CR, lancet(xc - 18 - off, xc + 18 + off, 0, 64, 22 + off)), fill=col)
    d.polygon(on_wall(CR, lancet(xc - 18, xc + 18, 0, 64, 22)), fill=hx("2a2220"))
    door = on_wall(CR, lancet(xc - 17, xc + 17, 0, 64, 21), -5)
    m = mask_of(img.size, [door])
    layer = img.copy()
    ld = ImageDraw.Draw(layer)
    x0, x1 = int(min(p[0] for p in door)), int(max(p[0] for p in door))
    y0, y1 = int(min(p[1] for p in door)), int(max(p[1] for p in door))
    rnd = random.Random(12)
    for x in range(x0, x1 + 1, 5):
        ld.rectangle([x, y0, x + 4, y1], fill=mul(OAK, 1 + rnd.uniform(-0.1, 0.1)))
        ld.line([(x, y0), (x, y1)], fill=OAK_D)
    for y in (y1 - 14, y1 - 40, y0 + 18):
        ld.rectangle([x0, y, x1, y + 2], fill=IRON)
        for x in range(x0 + 2, x1, 6):
            ld.point((x, y + 1), fill=hx("5a5048"))
    layer.paste(Image.new("RGB", img.size, OAK_D), (0, 0), mask_of(img.size, [[(xc - 1, y0), (xc + 1, y0), (xc + 1, y1), (xc - 1, y1)]]))
    img.paste(layer, (0, 0), m)
    d = ImageDraw.Draw(img)
    hx_, hy = CR.P(xc + 8, 30, -5)
    d.ellipse([hx_ - 3, hy - 3, hx_ + 3, hy + 3], outline=hx("6a5a40"))
    d.point((hx_, hy - 3), fill=hx("a08a5a"))
    # worn stone step in front
    CR.box(img, xc - 22, xc + 22, 0, 2, 0, 8, hx("6e675c"), top=hx("9a9282"), side=hx("4a443c"))
    # holy-water stoup beside the door
    sx, sy = CR.P(68, 40, 2)
    d.pieslice([sx - 4, sy - 4, sx + 4, sy + 4], 0, 180, fill=hx("a49a86"), outline=hx("5a5248"))


def c_cell_door(img):
    d = ImageDraw.Draw(img)
    x0, x1, top = 393, 427, 66
    d.polygon([CR.P(x0 - 5, 0, 0), CR.P(x1 + 5, 0, 0), CR.P(x1 + 5, top + 8, 0), CR.P(x0 - 5, top + 8, 0)], fill=hx("958b78"))
    d.polygon([CR.P(x0 - 3, top + 2, 0), CR.P(x1 + 3, top + 2, 0), CR.P(x1 + 3, top + 8, 0), CR.P(x0 - 3, top + 8, 0)],
              fill=hx("b0a690"))
    d.polygon([CR.P(x0, 0, 0), CR.P(x1, 0, 0), CR.P(x1, top, 0), CR.P(x0, top, 0)], fill=hx("231a14"))
    a, b = CR.P(x0, top, -3), CR.P(x1, 0, -3)
    rnd = random.Random(31)
    for x in range(int(a[0]), int(b[0]) + 1, 6):
        d.rectangle([x, a[1], min(x + 5, b[0]), b[1]], fill=mul(hx("5a3c26"), 1 + rnd.uniform(-0.08, 0.08)))
        d.line([(x, a[1]), (x, b[1])], fill=OAK_D)
    for y in (a[1] + 8, b[1] - 10):
        d.rectangle([a[0], y, b[0], y + 2], fill=hx("3e2818"))
    d.line([(a[0] + 2, (a[1] + b[1]) / 2 - 8), (a[0] + 20, (a[1] + b[1]) / 2 + 8)], fill=hx("3e2818"), width=2)
    lx, ly = b[0] - 6, (a[1] + b[1]) / 2 + 2
    d.rectangle([lx - 1, ly - 3, lx + 3, ly + 3], fill=IRON)
    d.line([(lx - 6, ly), (lx + 1, ly)], fill=hx("5a5048"), width=2)
    # little card holder where her name used to be
    cx = (a[0] + b[0]) / 2
    d.rectangle([cx - 5, a[1] + 14, cx + 5, a[1] + 19], fill=hx("6a5a40"))
    d.rectangle([cx - 4, a[1] + 15, cx + 4, a[1] + 18], fill=hx("2a1e14"))


def our_lady(img, cx, fy, hy):
    """The painted plaster Madonna: blue mantle over a cream gown, hands joined, on a cloud and crescent moon,
    crowned with twelve stars.  cx is the centre line, fy the top of the pedestal and hy the top of her head."""
    d = ImageDraw.Draw(img)
    BLUE, BLUE_L, BLUE_D, RIM = hx("4a74c0"), hx("82a8e8"), hx("223c78"), hx("b8d0f0")
    GOWN, GOWN_D, GOWN_L = hx("ece4d4"), hx("b4a894"), hx("fffaf0")
    SKIN, SKIN_D = hx("f4cca8"), hx("b8805e")
    GOLD, GOLD_D = hx("e8c050"), hx("9a7428")
    # mantle: a hood over the head, falling wide to a flared hem
    mantle = [(cx - 5, hy + 2), (cx - 4, hy - 1), (cx - 2, hy - 2), (cx + 2, hy - 2), (cx + 4, hy - 1), (cx + 5, hy + 2),
              (cx + 6, hy + 9), (cx + 8, hy + 13), (cx + 9, hy + 24), (cx + 10, hy + 38), (cx + 12, fy - 2),
              (cx + 9, fy - 1), (cx + 6, fy - 3), (cx - 6, fy - 3), (cx - 9, fy - 1), (cx - 12, fy - 2),
              (cx - 10, hy + 38), (cx - 9, hy + 24), (cx - 8, hy + 13), (cx - 6, hy + 9)]
    d.polygon(mantle, fill=BLUE)
    # shadowed right side and folds
    d.polygon([(cx + 4, hy + 10), (cx + 8, hy + 13), (cx + 9, hy + 24), (cx + 10, hy + 38), (cx + 12, fy - 2),
               (cx + 9, fy - 1), (cx + 7, fy - 3), (cx + 6, hy + 26)], fill=BLUE_D)
    d.line([(cx + 8, hy + 20), (cx + 9, fy - 4)], fill=BLUE)
    d.line([(cx - 7, hy + 16), (cx - 8, fy - 5)], fill=BLUE_L)
    d.line([(cx - 5, hy + 22), (cx - 6, fy - 6)], fill=hx("3a5ea8"))
    d.line([(cx - 4, hy), (cx - 5, hy + 3)], fill=BLUE_L)
    # pale rim along her left so she stands clear of the night-blue niche
    d.line([(cx - 5, hy + 2), (cx - 6, hy + 9), (cx - 8, hy + 13), (cx - 9, hy + 24), (cx - 10, hy + 38),
            (cx - 12, fy - 2)], fill=RIM)
    d.line([(cx - 4, hy - 1), (cx - 2, hy - 2), (cx + 2, hy - 2)], fill=RIM)
    # gown in the opening of the mantle
    gown = [(cx - 2, hy + 10), (cx + 2, hy + 10), (cx + 4, hy + 28), (cx + 6, fy - 3), (cx - 6, fy - 3),
            (cx - 4, hy + 28)]
    d.polygon(gown, fill=GOWN)
    d.polygon([(cx + 1, hy + 24), (cx + 3, hy + 24), (cx + 5, fy - 3), (cx + 2, fy - 3)], fill=GOWN_D)
    d.line([(cx - 2, hy + 27), (cx - 3, fy - 4)], fill=GOWN_D)
    d.line([(cx - 3, hy + 30), (cx - 4, fy - 5)], fill=GOWN_L)
    d.line([(cx, hy + 28), (cx, fy - 4)], fill=GOWN_L)
    # gold trim down both edges of the mantle and along the hem
    d.line([(cx - 2, hy + 10), (cx - 4, hy + 28), (cx - 6, fy - 3)], fill=GOLD)
    d.line([(cx + 2, hy + 10), (cx + 4, hy + 28), (cx + 6, fy - 3)], fill=GOLD_D)
    d.line([(cx - 12, fy - 2), (cx - 9, fy - 1), (cx - 6, fy - 3)], fill=GOLD)
    d.line([(cx + 6, fy - 3), (cx + 9, fy - 1), (cx + 12, fy - 2)], fill=GOLD_D)
    # blue sash knotted at the waist, its ends hanging
    d.line([(cx - 3, hy + 24), (cx + 3, hy + 24)], fill=BLUE_L)
    d.line([(cx - 3, hy + 25), (cx + 3, hy + 25)], fill=BLUE)
    d.line([(cx, hy + 26), (cx - 1, hy + 34)], fill=BLUE)
    d.line([(cx + 1, hy + 26), (cx + 1, hy + 32)], fill=BLUE_D)
    # sleeves meeting at the breast, hands joined in prayer
    d.polygon([(cx - 5, hy + 16), (cx - 1, hy + 18), (cx - 1, hy + 21), (cx - 5, hy + 20)], fill=GOWN)
    d.polygon([(cx + 5, hy + 16), (cx + 1, hy + 18), (cx + 1, hy + 21), (cx + 5, hy + 20)], fill=GOWN_D)
    d.polygon([(cx - 1, hy + 21), (cx - 1, hy + 15), (cx, hy + 13), (cx + 1, hy + 15), (cx + 1, hy + 21)], fill=SKIN)
    d.line([(cx + 1, hy + 15), (cx + 1, hy + 21)], fill=SKIN_D)
    d.line([(cx - 2, hy + 16), (cx - 2, hy + 21)], fill=GOWN_D)
    d.line([(cx + 2, hy + 16), (cx + 2, hy + 21)], fill=hx("8a7e6c"))
    # white veil framing the face, under the hood
    d.polygon([(cx - 4, hy + 1), (cx + 4, hy + 1), (cx + 4, hy + 9), (cx + 2, hy + 12), (cx - 2, hy + 12),
               (cx - 4, hy + 9)], fill=hx("eef0f8"))
    d.line([(cx + 4, hy + 2), (cx + 4, hy + 9)], fill=hx("a8acc0"))
    # face, gently bowed: hand-placed pixels so it reads as a young woman at this size
    face = ("..HHH..",
            ".HHsHH.",
            "HHssssH",
            "HsesesH",
            "HbsnsbH",
            "HssssSH",
            ".SsmsS.",
            "..SsS..")
    ink = {"H": hx("5a3826"), "s": SKIN, "S": SKIN_D, "e": hx("5a3428"), "b": hx("ec9c88"),
           "n": hx("e8b896"), "m": hx("d47a74")}
    for r, row in enumerate(face):
        for c, ch in enumerate(row):
            if ch in ink:
                d.point((cx - 3 + c, hy + 1 + r), fill=ink[ch])
    # slender neck and the round neckline of the gown, so the veil only frames her face
    d.rectangle([cx - 1, hy + 9, cx + 1, hy + 10], fill=SKIN)
    d.point((cx + 1, hy + 9), fill=SKIN_D)
    d.line([(cx - 2, hy + 11), (cx + 2, hy + 11)], fill=GOWN)
    d.point((cx - 2, hy + 10), fill=GOWN)
    d.point((cx + 2, hy + 10), fill=GOWN_D)
    # bare feet peeping from the hem, on a little cloud and a gilded crescent moon
    for x in (cx - 2, cx + 1):
        d.line([(x, fy - 3), (x + 1, fy - 3)], fill=SKIN)
    d.polygon([(cx - 9, fy - 3), (cx - 7, fy - 1), (cx - 3, fy), (cx + 3, fy), (cx + 7, fy - 1), (cx + 9, fy - 3),
               (cx + 7, fy - 2), (cx, fy - 1), (cx - 7, fy - 2)], fill=GOLD)
    d.line([(cx - 3, fy), (cx + 3, fy)], fill=GOLD_D)
    for x, r in ((cx - 6, 2), (cx - 2, 2), (cx + 3, 2), (cx + 7, 1)):
        d.ellipse([x - r, fy - 1, x + r, fy + 2], fill=hx("d8d0c4"))
    d.line([(cx - 8, fy + 2), (cx + 8, fy + 2)], fill=hx("8a8478"))
    # crown of twelve stars
    for k in range(12):
        a = math.pi * (0.04 + 0.92 * k / 11)
        sx, sy = round(cx - math.cos(a) * 10), round(hy + 4 - math.sin(a) * 10)
        d.point((sx, sy), fill=hx("fff2a8"))
        if k % 2 == 0:
            d.point((sx, sy - 1), fill=GOLD)
            d.point((sx, sy + 1), fill=GOLD_D)


def c_niche(img):
    """Our Lady in a pointed niche, the votive stand burning beneath her."""
    d = ImageDraw.Draw(img)
    xc = 187
    for off, col in ((4, hx("a89e8a")), (0, hx("3c3430"))):
        d.polygon(on_wall(CR, lancet(xc - 18 - off, xc + 18 + off, 60 - off, 124, 30 + off)), fill=col)
    back = on_wall(CR, lancet(xc - 15, xc + 15, 62, 124, 28), -8)
    d.polygon(back, fill=hx("2c3a5e"))
    for i in range(14):
        sx, sy = CR.P(xc - 12 + (i * 37) % 24, 70 + (i * 23) % 76, -8)
        d.point((sx, sy), fill=hx("c8a850"))
    # pedestal
    CR.box(img, xc - 11, xc + 11, 60, 66, -8, 4, hx("948a78"), top=hx("c8bca4"), side=hx("5a5248"))
    # wrought-iron votive stand on the floor before her
    z = 12
    for x in (xc - 16, xc + 16):
        d.line([CR.P(x, 0, z), CR.P(x, 30, z)], fill=IRON)
    for tier, (y, dz) in enumerate(((22, -3), (30, 0))):
        a, b = CR.P(xc - 18, y, z + dz), CR.P(xc + 18, y, z + dz)
        d.rectangle([a[0], a[1], b[0], a[1] + 2], fill=IRON)
        rnd = random.Random(tier + 3)
        n = 7 if tier == 0 else 6
        for k in range(n):
            c = CR.P(xc - 16 + 32 * (k + 0.5) / n, y, z + dz)
            lit = rnd.random() < 0.8
            d.rectangle([c[0] - 1, c[1] - 3, c[0] + 1, c[1] - 1], fill=hx("b82028") if lit else hx("5a1018"))
            if lit:
                d.point((c[0], c[1] - 4), fill=hx("fff0a0"))
    for x in (xc - 22, xc + 22):  # two tall pricket candles on the pedestal shelf
        b, t = CR.P(x, 66, 0), CR.P(x, 78, 0)
        d.line([(b[0], b[1]), (b[0], b[1] - 2)], fill=hx("8a6a30"), width=3)
        d.rectangle([t[0] - 1, t[1], t[0] + 1, b[1] - 2], fill=hx("ece4cc"))
        flame(d, int(t[0]), int(t[1]) - 1, True)
    # brass offering box
    CR.box(img, xc + 22, xc + 30, 0, 18, 6, 12, hx("5a3c22"), top=hx("8a6a3a"), side=hx("3a2614"))
    s = CR.P(xc + 26, 18, 9)
    d.line([(s[0] - 2, s[1]), (s[0] + 2, s[1])], fill=IRON)


def statue_layer(size, xc=187):
    """Our Lady alone on a transparent layer, at her place on the pedestal."""
    fx, fy = CR.P(xc, 66, -2)
    _, hy = CR.P(xc, 118, -2)
    cx, fy, hy = round(fx), round(fy), round(hy)
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    our_lady(layer, cx, fy, hy)
    return layer, cx, fy, hy


def c_statue(img):
    """Paints Our Lady after the dusk lightmap, under her own softer candle tint, so her colours survive."""
    layer, cx, fy, hy = statue_layer(img.size)
    light(img, "ellipse", [cx - 12, hy - 9, cx + 12, hy + 15], hx("e8c070"), 0.18, 3)
    tint = Image.new("RGB", img.size, hx("e0d4d4"))
    vgrad(tint, (0, hy - 2, img.width - 1, fy + 3), hx("e0d4d4"), hx("f0d0b0"))
    lit = ImageChops.multiply(layer.convert("RGB"), tint)
    img.paste(lit, (0, 0), layer.getchannel("A"))


def c_bench(img):
    X0, X1, Z0, Z1 = 306, 364, 3, 17
    a, b = CR.P(X0, 0, Z1), CR.P(X1, 0, Z0)
    shadow(img, "rect", [a[0] - 2, b[1] - 2, b[0] + 6, a[1] + 3], 0.45, 3)
    for x in (X0 + 3, X1 - 3):
        CR.box(img, x - 2, x + 2, 0, 40, Z0, Z0 + 3, OAK, top=OAK_L, side=OAK_D)
    for y in (24, 34):
        CR.box(img, X0, X1, y, y + 4, Z0, Z0 + 2, mul(OAK, 1.1), top=OAK_L, side=OAK_D)
    for x in (X0 + 3, X1 - 3):
        CR.box(img, x - 2, x + 2, 0, 15, Z1 - 4, Z1, OAK, top=OAK_L, side=OAK_D)
    CR.line(img, (X0 + 3, 4, Z1 - 2), (X1 - 3, 4, Z1 - 2), OAK_D, 2)
    CR.box(img, X0 - 2, X1 + 2, 15, 18, Z0, Z1 + 1, mul(OAK, 1.15), top=hx("8e6240"), side=OAK_D)


def crucifix_geom(xc=463, y0=58):
    """Screen centre line, top and foot of the upright, and the crossbar row of the corridor crucifix."""
    a, b = CR.P(xc, y0 + 52, 1), CR.P(xc, y0, 1)
    return round(a[0]), round(a[1]), round(b[1]), round(CR.P(xc, y0 + 40, 1)[1])


# hand-pixelled corpus: arms raised from the nailed hands, head bowed to his right under the crown of thorns,
# white loincloth knotted at the hip, knees bent and the feet crossed over one nail
CORPUS = ("n...................n",
          "sS.................Ss",
          ".sS.......tTtt....Ss.",
          "..sS.....tHsHt...Ss..",
          "...sS....HssSH..Ss...",
          "....sSS..HsSH..SSs...",
          "......sS..HS..SS.....",
          ".......sSssSSSs......",
          "........ssssSS.......",
          "........sSsSSS.......",
          "........ssSsSS.......",
          "........sSsSSS.......",
          "........sssSS........",
          ".........ssSS........",
          "........wwwWWW.......",
          "........wwwwWWw......",
          ".........wwWWw.......",
          ".........ssSS........",
          ".........ssSS........",
          "..........sSS........",
          "..........sS.........",
          "..........sS.........",
          ".........sSS.........",
          ".........sSS.........",
          ".........snS.........",
          "..........bb.........")


def crucifix_layer(size):
    """The walnut cross, its INRI titulus and the ivory corpus on a transparent layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, top, foot, arm = crucifix_geom()
    WOOD, WOOD_L, WOOD_D = hx("4e2e1a"), hx("8a5a36"), hx("2a180c")
    # upright and crossbar, lit from the windows on the left, with little rounded finials
    d.rectangle([x - 2, top, x + 2, foot], fill=WOOD)
    d.line([(x - 2, top), (x - 2, foot)], fill=WOOD_L)
    d.line([(x + 2, top), (x + 2, foot)], fill=WOOD_D)
    d.rectangle([x - 12, arm - 2, x + 12, arm + 2], fill=WOOD)
    d.line([(x - 12, arm - 2), (x + 12, arm - 2)], fill=WOOD_L)
    d.line([(x - 12, arm + 2), (x + 12, arm + 2)], fill=WOOD_D)
    for ex, ey in ((x - 13, arm), (x + 13, arm), (x, top - 1)):
        d.rectangle([ex - 1, ey - 1, ex + 1, ey + 1], fill=WOOD_L)
        d.point((ex + 1, ey + 1), fill=WOOD_D)
    d.rectangle([x - 2, foot - 1, x + 2, foot], fill=WOOD_D)
    # INRI titulus above his head
    d.rectangle([x - 3, top + 2, x + 3, top + 5], fill=hx("e8dcb8"))
    d.line([(x - 3, top + 5), (x + 3, top + 5)], fill=hx("a89670"))
    for i, dy in ((-2, 3), (0, 3), (2, 3), (-1, 4), (1, 4)):
        d.point((x + i, top + dy), fill=hx("6a3a24"))
    # the corpus, hands on the crossbar
    ink = {"s": hx("ecdcbe"), "S": hx("a88e6c"), "H": hx("6a4428"), "t": hx("a8955a"), "T": hx("5a4a28"),
           "w": hx("fbf8f0"), "W": hx("b8b0a0"), "n": hx("2a2622"), "b": hx("8a1a18")}
    ox, oy = x - len(CORPUS[0]) // 2, arm - 2
    for r, row in enumerate(CORPUS):
        for c, ch in enumerate(row):
            if ch in ink:
                d.point((ox + c, oy + r), fill=ink[ch])
    return layer


def c_crucifix(img):
    """Only the cast shadow is painted under the dusk light; the cross itself goes on afterwards."""
    x, top, foot, arm = crucifix_geom()
    shadow(img, "rect", [x - 10, top + 2, x + 16, foot + 3], 0.3, 2)


def c_crucifix_lit(img):
    layer = crucifix_layer(img.size)
    x, top, foot, _ = crucifix_geom()
    tint = Image.new("RGB", img.size, hx("b8acb0"))
    vgrad(tint, (0, top, img.width - 1, foot), hx("c4b6b0"), hx("948890"))
    img.paste(ImageChops.multiply(layer.convert("RGB"), tint), (0, 0), layer.getchannel("A"))


def c_floor(img):
    d = ImageDraw.Draw(img)
    flags = (hx("7a7266"), hx("5e574e"))

    def tile(rnd, row, u):
        c = flags[(row + int(math.floor(u / 28 + 100))) % 2]
        return mul(c, 1 + rnd.uniform(-0.08, 0.08))
    quad_blocks(d, lambda x, z: CR.P(x, 0, z), -700, 1200, 0, 206, 28, 14, tile, 91, mortar=0.7)
    noise(img, (0, 184, W - 1, H - 1), 5, 92)
    shadow(img, "rect", [0, 184, W, 190], 0.4, 3)


def paint_corridor():
    img = Image.new("RGB", (W, H), hx("1a1616"))
    c_vault(img)
    c_wall(img)
    sky = c_sky(img.size)
    glass = c_windows(img, sky)
    c_floor(img)
    c_entrance(img)
    c_cell_door(img)
    c_shafts(img)
    c_niche(img)
    c_crucifix(img)
    c_bench(img)
    # dusk: the windows and the votives are the only real light
    lights = []
    for i, g in zip(WINDOW_BAYS, glass):
        xa, xb = BAYS[i]
        xc = (xa + xb) / 2
        out = lancet(xc - 12, xc + 12, 52, 118, 32)
        patch = [CR.P(x + 0.32 * y, 0, 0.9 * y) for x, y in out]
        lights.append(("polygon", patch, hx("b06838"), 0.55, 5))
        lights.append(("polygon", [CR.P(xc - 12, 52, 0), CR.P(xc + 12, 52, 0)] + [patch[-1], patch[0]],
                       hx("6a4a50"), 0.35, 10))
        lights.append(("ellipse", [xc - 50, 20, xc + 50, 160], hx("4a3a50"), 0.6, 20))
    lights.append(("ellipse", [117, 60, 257, 240], hx("a06030"), 0.55, 26))
    lights.append(("ellipse", [160, 130, 214, 196], hx("c08040"), 0.4, 10))
    img = lightmap(img, (96, 86, 112), lights)
    c_statue(img)
    c_crucifix_lit(img)
    for g in glass:
        light(img, "polygon", g, hx("f0a060"), 0.22, 3)
    for i in WINDOW_BAYS:
        xa, xb = BAYS[i]
        xc = (xa + xb) / 2
        shaft = [CR.P(xc - 12, 110, -10), CR.P(xc + 12, 110, -10), CR.P(xc + 12 + 0.32 * 52, 0, 0.9 * 52 + 30),
                 CR.P(xc - 12 + 0.32 * 52, 0, 0.9 * 52 + 30)]
        light(img, "polygon", shaft, hx("c08060"), 0.07, 8)
    light(img, "ellipse", [172, 100, 202, 160], hx("ffc070"), 0.18, 8)
    shadow(img, "rect", [0, 0, W, 30], 0.45, 18, hx("1c1622"))
    vignette(img, 0.5, tint=(36, 28, 40), blur=40)
    return img


# ---------------------------------------------------------------- Eleanor's cell by lamplight

LR = Room3D(194, 240, 100, 190)
XL, XR, L_SP, L_AP, L_ZM = 110, 370, 100, 136, 160
PLASTER = hx("8e877a")
NS_X0, NS_X1, NS_Z0, NS_Z1, NS_H = 296, 326, 2, 24, 26  # nightstand
DR_Y0, DR_Y1, DR_OUT = 15, 23, 22  # drawer rows and how far it is pulled out
BED_X0, BED_X1, BED_Z0, BED_Z1 = 334, 368, 2, 74
LAMP_X, LAMP_Z, LAMP_H = 276, 10, 58
WIN_X, WIN_Y0 = 240, 86


def l_vault(img):
    d = ImageDraw.Draw(img)
    rise = L_AP - L_SP
    nu, nz = 26, 40
    rnd = random.Random(201)
    for j in range(nz):
        za, zb = L_ZM * j / nz, L_ZM * (j + 1) / nz
        for i in range(nu):
            ua, ub = i / nu, (i + 1) / nu
            uc = (ua + ub) / 2
            col = mix(PLASTER, hx("4a4640"), parch(uc) * 0.5)
            col = mul(col, (0.8 if uc < 0.5 else 0.95) * (1 + rnd.uniform(-0.03, 0.03)))
            q = [(XL + (XR - XL) * u, L_SP + rise * parch(u), z) for u, z in ((ua, za), (ub, za), (ub, zb), (ua, zb))]
            d.polygon([LR.P(*p) for p in q], fill=col)
    # a plain transverse band and the wall arch
    for z in (0.5, 70):
        pts = [LR.P(XL + (XR - XL) * t / 30, L_SP + rise * parch(t / 30), z) for t in range(31)]
        d.line([(x, y + 2) for x, y in pts], fill=hx("4a443c"), width=3)
        d.line(pts, fill=hx("aaa292"), width=3)
    noise(img, (0, 0, W - 1, 110), 4, 202)


def plaster(img, poly, base, seed):
    layer = Image.new("RGB", img.size, base)
    rnd = random.Random(seed)
    d = ImageDraw.Draw(layer)
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    box = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
    for _ in range(int((box[2] - box[0]) * (box[3] - box[1]) / 90)):
        x, y = rnd.randint(box[0], box[2]), rnd.randint(box[1], box[3])
        r = rnd.randint(2, 7)
        d.ellipse([x - r, y - r * 0.6, x + r, y + r * 0.6], fill=mul(base, 1 + rnd.uniform(-0.07, 0.05)))
    noise(layer, box, 4, seed + 1)
    img.paste(layer, (0, 0), mask_of(img.size, [poly]))


def l_walls(img):
    d = ImageDraw.Draw(img)
    back = on_wall(LR, [(XL, 0), (XR, 0)] + list(reversed(arch_pts(XL, XR, L_SP, L_AP - L_SP, 24))))
    plaster(img, back, PLASTER, 211)
    left = [LR.P(XL, 0, 0), LR.P(XL, L_SP, 0), LR.P(XL, L_SP, L_ZM), LR.P(XL, 0, L_ZM)]
    right = [LR.P(XR, 0, 0), LR.P(XR, L_SP, 0), LR.P(XR, L_SP, L_ZM), LR.P(XR, 0, L_ZM)]
    plaster(img, left, mul(PLASTER, 0.8), 221)
    plaster(img, right, mul(PLASTER, 0.9), 231)
    # cracks and damp in the old plaster
    d.line([LR.P(150, 96, 0), LR.P(156, 80, 0), LR.P(150, 66, 0), LR.P(158, 52, 0)], fill=hx("4a443c"))
    d.line([LR.P(XR, 90, 30), LR.P(XR, 74, 38), LR.P(XR, 66, 34)], fill=hx("4a443c"))
    for box in ([160, 150, 230, 196], [XL - 40, 120, XL + 10, 210], [250, 70, 310, 118]):
        shadow(img, "ellipse", box, 0.2, 12, hx("6a5a48"))
    # a nail where a picture used to hang, and a tide-mark of damp. Still a poor cell.
    d.point(LR.P(200, 78, 0), fill=hx("2a2620"))
    d.line([LR.P(188, 92, 0), LR.P(214, 96, 0), LR.P(206, 108, 0)], fill=hx("7a6a58"))
    # dark skirting where floor meets the walls
    for x0, x1 in ((XL, XL), (XR, XR)):
        d.polygon([LR.P(x0, 0, 0), LR.P(x0, 6, 0), LR.P(x1, 6, L_ZM), LR.P(x1, 0, L_ZM)], fill=hx("3a3430"))
    d.polygon([LR.P(XL, 0, 0), LR.P(XR, 0, 0), LR.P(XR, 6, 0), LR.P(XL, 6, 0)], fill=hx("3a3430"))
    # corner shading
    for pts in ([LR.P(XL, 0, 0), LR.P(XL, L_SP, 0), LR.P(XL + 14, L_SP, 0), LR.P(XL + 14, 0, 0)],
                [LR.P(XR, 0, 0), LR.P(XR, L_SP, 0), LR.P(XR - 10, L_SP, 0), LR.P(XR - 10, 0, 0)]):
        shadow(img, "polygon", pts, 0.35, 6)


def l_floor(img):
    d = ImageDraw.Draw(img)
    flags = (hx("6a6258"), hx("5a534a"))

    def tile(rnd, row, u):
        return mul(flags[(row + int(u // 24)) % 2], 1 + rnd.uniform(-0.1, 0.1))
    quad_blocks(d, lambda x, z: LR.P(x, 0, z), XL, XR, 0, L_ZM, 24, 18, tile, 251, mortar=0.65)
    a, b = LR.P(XL, 0, 0), LR.P(XR, 0, L_ZM)
    noise(img, (0, int(a[1]), W - 1, H - 1), 6, 252)
    shadow(img, "rect", [0, a[1], W, a[1] + 6], 0.4, 3)


def l_window(img):
    """A small barred lancet high in the end wall; the moon is somewhere beyond it."""
    d = ImageDraw.Draw(img)
    outer = lancet(WIN_X - 13, WIN_X + 13, WIN_Y0 - 4, 110, 18)
    inner = lancet(WIN_X - 7, WIN_X + 7, WIN_Y0, 112, 14)
    d.polygon(on_wall(LR, outer, 0), fill=hx("a49c8c"))
    g = on_wall(LR, inner, -12)
    d.polygon([LR.P(WIN_X - 13, WIN_Y0 - 4, 0), LR.P(WIN_X + 13, WIN_Y0 - 4, 0), g[-1], g[0]], fill=hx("b8b0a0"))
    d.polygon([LR.P(WIN_X - 13, WIN_Y0 - 4, 0), LR.P(WIN_X - 13, 110, 0), LR.P(WIN_X - 7, 112, -12), g[0]], fill=hx("6e675c"))
    d.polygon(g, fill=hx("2a3460"))
    d.ellipse([g[0][0] + 4, g[len(g) // 2][1] + 4, g[0][0] + 9, g[len(g) // 2][1] + 9], fill=hx("d8dcf0"))
    d.ellipse([g[0][0] + 5, g[len(g) // 2][1] + 3, g[0][0] + 10, g[len(g) // 2][1] + 8], fill=hx("2a3460"))
    for x in (WIN_X - 3.5, WIN_X, WIN_X + 3.5):
        d.line([LR.P(x, WIN_Y0, -12), LR.P(x, 124, -12)], fill=IRON)
    d.line([LR.P(WIN_X - 7, 100, -12), LR.P(WIN_X + 7, 100, -12)], fill=IRON)
    d.line(g + [g[0]], fill=hx("2a2420"))
    return g


def l_door(img):
    """The way back out to the corridor, in the near left wall."""
    d = ImageDraw.Draw(img)
    z0, z1, top = 40, 64, 62
    frame = [LR.P(XL, 0, z0 - 4), LR.P(XL, top + 5, z0 - 4), LR.P(XL, top + 5, z1 + 4), LR.P(XL, 0, z1 + 4)]
    d.polygon(frame, fill=hx("5a4a3a"))
    leaf = [LR.P(XL, 0, z0), LR.P(XL, top, z0), LR.P(XL, top, z1), LR.P(XL, 0, z1)]
    d.polygon(leaf, fill=hx("4a3020"))
    rnd = random.Random(261)
    for k in range(7):
        za, zb = z0 + (z1 - z0) * k / 7, z0 + (z1 - z0) * (k + 1) / 7
        d.polygon([LR.P(XL, 1, za), LR.P(XL, top - 1, za), LR.P(XL, top - 1, zb), LR.P(XL, 1, zb)],
                  fill=mul(hx("553824"), 1 + rnd.uniform(-0.1, 0.1)), outline=hx("2a1a10"))
    for y in (14, top - 14):
        d.polygon([LR.P(XL, y, z0), LR.P(XL, y + 3, z0), LR.P(XL, y + 3, z1), LR.P(XL, y, z1)], fill=hx("2e1e12"))
    a, b = LR.P(XL, 34, z0 + 6), LR.P(XL, 34, z0 + 12)
    d.line([a, b], fill=hx("6a6050"), width=2)
    d.ellipse([a[0] - 2, a[1] - 2, a[0] + 2, a[1] + 2], fill=hx("8a7a5a"))


def l_crucifix_geom():
    """Screen centre line, top and foot of the upright, and the crossbar row of the cell crucifix over the bed."""
    xc = (BED_X0 + BED_X1) / 2
    top, foot = LR.P(xc, 94, 0), LR.P(xc, 50, 0)
    return round(top[0]), round(top[1]), round(foot[1]), round(LR.P(xc, 84, 0)[1])


def l_crucifix(img):
    """Only the dried palm and the shadow cast away from the lamp go under the lamplight; the cross is laid on after."""
    d = ImageDraw.Draw(img)
    x, top, foot, arm = l_crucifix_geom()
    shadow(img, "rect", [x - 10, top + 2, x + 17, foot + 3], 0.3, 2)
    shadow(img, "rect", [x - 1, top + 1, x + 6, foot + 2], 0.25, 1)
    # a sprig of dried palm tucked behind it
    for k, (dx, dy) in enumerate(((13, -14), (16, -10), (10, -16))):
        d.line([(x + 2, arm - 1), (x + dx, arm + dy)], fill=mul(hx("8a7a4a"), 1 - 0.1 * k))
    for t in range(3, 12, 2):
        px, py = x + 2 + t, arm - 1 - round(t * 1.15)
        d.point((px - 1, py - 1), fill=hx("9a8a54"))
        d.point((px + 1, py + 1), fill=hx("6a5a34"))


def l_crucifix_layer(size):
    """A dark oak cross with trefoil ends, its INRI titulus and the hand-pixelled ivory corpus, on a transparent layer."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, top, foot, arm = l_crucifix_geom()
    WOOD, WOOD_L, WOOD_D, GRAIN = hx("5a361e"), hx("94643c"), hx("2a180c"), hx("462814")
    GILT, CLEAR = hx("c8a050"), (0, 0, 0, 0)
    half = 13
    # upright and crossbar, lit from the lamp on the left; grain runs along each beam
    d.rectangle([x - 2, top, x + 2, foot], fill=WOOD)
    d.rectangle([x - half, arm - 2, x + half, arm + 2], fill=WOOD)
    for y in range(top + 1, foot, 3):
        d.point((x + (y // 3) % 3 - 1, y), fill=GRAIN)
    for xx in range(x - half + 1, x + half, 4):
        d.point((xx, arm + (xx // 4) % 3 - 1), fill=GRAIN)
    d.line([(x - 2, top), (x - 2, foot)], fill=WOOD_L)
    d.line([(x + 2, top), (x + 2, foot)], fill=WOOD_D)
    d.line([(x - half, arm - 2), (x + half, arm - 2)], fill=WOOD_L)
    d.line([(x - half, arm + 2), (x + half, arm + 2)], fill=WOOD_D)
    # rounded ends with a gilt boss on the three arms
    for ex, ey in ((x - half - 1, arm), (x + half + 1, arm), (x, top - 1)):
        d.rectangle([ex - 2, ey - 2, ex + 2, ey + 2], fill=WOOD)
        for cx, cy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            d.point((ex + cx, ey + cy), fill=CLEAR)
        d.point((ex - 1, ey - 1), fill=WOOD_L)
        d.point((ex + 1, ey + 1), fill=WOOD_D)
        d.point((ex, ey), fill=GILT)
    # stepped foot block
    d.rectangle([x - 4, foot - 3, x + 4, foot], fill=WOOD)
    d.line([(x - 4, foot - 3), (x + 4, foot - 3)], fill=WOOD_L)
    d.line([(x - 4, foot), (x + 4, foot)], fill=WOOD_D)
    # gilt rays behind the crossing
    for dx, dy in ((-4, -4), (4, -4), (-5, 0), (5, 0)):
        d.point((x + dx, arm + dy), fill=GILT)
    # INRI titulus above his head
    d.rectangle([x - 4, top + 3, x + 4, top + 7], fill=hx("e8dcb8"))
    d.line([(x - 4, top + 7), (x + 4, top + 7)], fill=hx("a89670"))
    d.line([(x + 4, top + 3), (x + 4, top + 7)], fill=hx("a89670"))
    for i, dy in ((-3, 4), (-3, 6), (-1, 4), (-1, 5), (-1, 6), (1, 4), (1, 6), (3, 4), (3, 6), (2, 5)):
        d.point((x + i, top + dy), fill=hx("6a3a24"))
    # the corpus, hands nailed to the crossbar
    ink = {"s": hx("ecdcbe"), "S": hx("a88e6c"), "H": hx("6a4428"), "t": hx("a8955a"), "T": hx("5a4a28"),
           "w": hx("fbf8f0"), "W": hx("b8b0a0"), "n": hx("2a2622"), "b": hx("8a1a18")}
    ox, oy = x - len(CORPUS[0]) // 2, arm - 1
    for r, row in enumerate(CORPUS):
        for c, ch in enumerate(row):
            if ch in ink:
                d.point((ox + c, oy + r), fill=ink[ch])
    # blood from the nailed hands and the wound in his side
    for p in ((ox + 1, oy + 2), (ox + len(CORPUS[0]) - 2, oy + 2), (ox + 13, oy + 9)):
        d.point(p, fill=hx("8a1a18"))
    return layer


def l_crucifix_lit(img):
    """The lamp is to the left of the cross: its left side is warmer and brighter."""
    layer = l_crucifix_layer(img.size)
    x, top, foot, _ = l_crucifix_geom()
    tint = Image.new("RGB", img.size, hx("b49478"))
    td = ImageDraw.Draw(tint)
    for xx in range(x - 17, x + 18):
        td.line([(xx, top - 4), (xx, foot + 2)], fill=mix(hx("e8ccaa"), hx("987a66"), (xx - x + 17) / 34))
    img.paste(ImageChops.multiply(layer.convert("RGB"), tint), (0, 0), layer.getchannel("A"))


def l_lamp_geom():
    """Screen centre line, floor row and tray row of the lampstand."""
    base, top = LR.P(LAMP_X, 0, LAMP_Z), LR.P(LAMP_X, LAMP_H, LAMP_Z)
    return int(top[0]), int(base[1]), int(top[1])


def l_lamp(img):
    """Only the stand's pool of shadow goes under the lamplight; the stand and lamp are laid on after, undithered.
    Returns the flame point the room's lights are centred on."""
    x, floor, y = l_lamp_geom()
    shadow(img, "ellipse", [x - 10, floor - 3, x + 10, floor + 3], 0.55, 2)
    return (x, y - 12)


def l_lamp_layer(size):
    """A wrought-iron stand on scrolled tripod feet, a drip tray, a brass oil font with burner and wick key, and a
    glass chimney round a lit flame, on a transparent layer. Lit from the flame above and a little left."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x, floor, y = l_lamp_geom()
    IRON_D, IRON, IRON_L, IRON_H = hx("140f0c"), hx("2a201a"), hx("4a3a2e"), hx("7a6048")
    # tripod: two splayed legs with curled toes and a third leg going back behind the shaft
    hub = floor - 7
    d.line([(x, hub), (x, floor - 3)], fill=IRON_D, width=2)
    for s in (-1, 1):
        d.line([(x, hub + 1), (x + 4 * s, floor - 2), (x + 7 * s, floor)], fill=IRON, width=2)
        d.point((x + 8 * s, floor - 1), fill=IRON)
        d.point((x + 8 * s, floor - 2), fill=IRON_L)
        d.point((x + 7 * s, floor + 1), fill=IRON_D)
    d.line([(x - 1, hub + 1), (x - 3, floor - 2)], fill=IRON_L)
    d.point((x + 1, floor - 2), fill=IRON_D)
    d.rectangle([x - 2, hub - 2, x + 1, hub], fill=IRON)
    d.line([(x - 2, hub - 2), (x + 1, hub - 2)], fill=IRON_L)
    # the shaft: dark core, a lit left edge that brightens towards the flame
    d.rectangle([x - 1, y + 2, x, hub - 3], fill=IRON)
    for yy in range(y + 2, hub - 2):
        t = (yy - y) / (hub - y)
        d.point((x - 1, yy), fill=mix(IRON_H, IRON_L, t))
        d.point((x, yy), fill=mix(IRON, IRON_D, t))
    # turned knops on the shaft
    for ky in (y + 16, y + 34):
        d.rectangle([x - 2, ky - 1, x + 1, ky + 1], fill=IRON)
        d.line([(x - 2, ky - 1), (x, ky - 1)], fill=IRON_H)
        d.point((x + 1, ky + 1), fill=IRON_D)
    # drip tray under the font
    d.rectangle([x - 7, y, x + 6, y + 1], fill=IRON)
    d.line([(x - 7, y), (x + 6, y)], fill=IRON_H)
    d.line([(x - 6, y + 2), (x + 5, y + 2)], fill=IRON_D)
    d.point((x - 8, y), fill=IRON_L)
    d.point((x + 7, y), fill=IRON_L)
    # brass font: rounded, highlight towards the upper left
    BR_D, BR, BR_L, BR_H = hx("5a3c12"), hx("9a6e26"), hx("d0a048"), hx("fff0b0")
    d.ellipse([x - 6, y - 8, x + 5, y - 1], fill=BR, outline=BR_D)
    d.line([(x - 4, y - 7), (x + 2, y - 7)], fill=BR_L)
    d.line([(x - 5, y - 6), (x - 5, y - 4)], fill=BR_L)
    d.point((x - 3, y - 6), fill=BR_H)
    d.point((x - 2, y - 6), fill=BR_H)
    d.line([(x - 3, y - 2), (x + 3, y - 2)], fill=BR_D)
    d.line([(x - 5, y - 4), (x + 4, y - 4)], fill=hx("b8863a"))  # stamped band round the belly
    # burner collar and wick key
    d.rectangle([x - 3, y - 11, x + 2, y - 9], fill=BR_D)
    d.line([(x - 3, y - 11), (x + 2, y - 11)], fill=BR_L)
    d.point((x - 2, y - 10), fill=BR)
    d.line([(x + 3, y - 10), (x + 4, y - 10)], fill=BR_D)
    d.rectangle([x + 5, y - 11, x + 6, y - 9], fill=BR_L)
    d.point((x + 6, y - 9), fill=BR_D)
    # glass chimney: bulb round the flame, narrowing to a neck; glass is see-through, its edges catch the light
    glass = (255, 236, 196, 110)
    bulb = [(x - 2, y - 12), (x - 4, y - 14), (x - 4, y - 19), (x - 2, y - 22), (x - 2, y - 28),
            (x + 1, y - 28), (x + 1, y - 22), (x + 3, y - 19), (x + 3, y - 14), (x + 1, y - 12)]
    d.polygon(bulb, fill=glass)
    edge, edge_d = hx("fff4d8"), hx("c8a878")
    d.line([(x - 2, y - 12), (x - 4, y - 14), (x - 4, y - 19), (x - 2, y - 22), (x - 2, y - 28)], fill=edge)
    d.line([(x + 1, y - 12), (x + 3, y - 14), (x + 3, y - 19), (x + 1, y - 22), (x + 1, y - 28)], fill=edge_d)
    d.line([(x - 2, y - 28), (x + 1, y - 28)], fill=edge)
    # the flame: a white-hot core in an orange teardrop on the wick
    d.point((x - 1, y - 21), fill=hx("ffe890"))
    d.line([(x - 1, y - 20), (x - 1, y - 14)], fill=hx("fffce8"))
    d.line([(x, y - 19), (x, y - 15)], fill=hx("ffe070"))
    d.line([(x - 2, y - 18), (x - 2, y - 15)], fill=hx("ffc050"))
    d.point((x, y - 14), fill=hx("ff9a30"))
    d.point((x - 2, y - 14), fill=hx("ff9a30"))
    d.point((x - 1, y - 13), fill=hx("3a2410"))  # the wick
    return layer


def l_nightstand(img, drawer=False, comb=False, mirror=False):
    X0, X1, Z0, Z1 = NS_X0, NS_X1, NS_Z0, NS_Z1
    d = ImageDraw.Draw(img)
    a, b = LR.P(X0, 0, Z1), LR.P(X1, 0, Z0)
    shadow(img, "rect", [a[0] - 3, b[1] - 2, b[0] + 4, a[1] + 3], 0.5, 3)
    wood, wood_l, wood_d = hx("6a4a30"), hx("8e6844"), hx("3a2618")
    for x in (X0 + 2, X1 - 2):
        LR.line(img, (x, 0, Z0 + 2), (x, NS_H - 2, Z0 + 2), wood_d, 2)
    LR.box(img, X0, X1, 6, NS_H - 2, Z0, Z1, wood, top=wood_l, side=wood_d)
    LR.box(img, X0 - 1, X1 + 1, NS_H - 2, NS_H, Z0, Z1 + 1, mul(wood, 1.1), top=hx("9a744c"), side=wood_d)
    for x in (X0 + 1.5, X1 - 1.5):
        LR.line(img, (x, 0, Z1 - 1.5), (x, 6, Z1 - 1.5), wood_d, 2)
    LR.line(img, (X0 + 1, 6, Z1), (X1 - 1, 6, Z1), wood_d)
    # lower shelf
    LR.quad(img, [(X0 + 2, 2, Z0 + 2), (X1 - 2, 2, Z0 + 2), (X1 - 2, 2, Z1 - 2), (X0 + 2, 2, Z1 - 2)], hx("4a3220"))
    # the breviary on top: black leather, gilt edges and a red ribbon
    LR.box(img, X0 + 6, X1 - 9, NS_H, NS_H + 3, Z0 + 6, Z1 - 5, hx("1e1a1e"), top=hx("2e2830"), side=hx("141014"))
    LR.line(img, (X0 + 6.5, NS_H + 1.5, Z1 - 5), (X1 - 9.5, NS_H + 1.5, Z1 - 5), hx("c8a050"))
    LR.line(img, (X0 + 12, NS_H + 3, Z1 - 5), (X0 + 13, NS_H - 3, Z1 - 4.8), hx("a82028"))
    LR.line(img, (X0 + 8, NS_H + 3.1, Z0 + 10), (X0 + 10, NS_H + 3.1, Z0 + 10), hx("8a7040"))
    LR.line(img, (X0 + 9, NS_H + 3.1, Z0 + 9), (X0 + 9, NS_H + 3.1, Z0 + 12), hx("8a7040"))
    c0, c1 = X0 + 3, X1 - 3
    if not drawer:
        LR.quad(img, [(c0, DR_Y0, Z1), (c1, DR_Y0, Z1), (c1, DR_Y1, Z1), (c0, DR_Y1, Z1)], hx("5e4028"), wood_d)
        LR.line(img, (c0 + 1, DR_Y1 - 1, Z1), (c1 - 1, DR_Y1 - 1, Z1), hx("8a6440"))
        kx, ky = LR.P((c0 + c1) / 2, (DR_Y0 + DR_Y1) / 2, Z1)
        d.ellipse([kx - 1.5, ky - 1.5, kx + 1.5, ky + 1.5], fill=hx("b8944a"))
        return
    LR.quad(img, [(c0, DR_Y0, Z1), (c1, DR_Y0, Z1), (c1, DR_Y1, Z1), (c0, DR_Y1, Z1)], hx("120c08"))
    zf = Z1 + DR_OUT
    fl = DR_Y1 - 3  # the drawer is shallow: its floor sits just below the rim
    # drawer box: inside back, floor, rims, then the front panel
    LR.quad(img, [(c0, DR_Y1, Z1 - 2), (c1, DR_Y1, Z1 - 2), (c1, fl, Z1 - 2), (c0, fl, Z1 - 2)], hx("24180e"))
    LR.quad(img, [(c0, fl, Z1 - 2), (c1, fl, Z1 - 2), (c1, fl, zf), (c0, fl, zf)], hx("6a4c30"))
    for k in range(1, 4):
        LR.line(img, (c0, fl, Z1 + k * DR_OUT / 4), (c1, fl, Z1 + k * DR_OUT / 4), hx("5e4228"))
    LR.quad(img, [(c0, fl, Z1 - 2), (c0 + 1, fl, Z1 - 2), (c0 + 1, fl, zf), (c0, fl, zf)], hx("3a2818"))
    LR.line(img, (c0, DR_Y1, Z1 - 2), (c0, DR_Y1, zf), hx("9a7450"))
    LR.line(img, (c1, DR_Y1, Z1 - 2), (c1, DR_Y1, zf), hx("9a7450"))
    LR.line(img, (c0, DR_Y1, Z1 - 2), (c1, DR_Y1, Z1 - 2), hx("8a6440"))
    if comb:  # tortoiseshell comb lying across the left of the drawer, teeth towards us
        x0, y0 = LR.P(c0 + 2, fl, Z1 + 4)
        x0, y0 = int(x0), int(y0)
        d.rectangle([x0, y0, x0 + 13, y0 + 1], fill=hx("9a521e"))
        d.line([(x0, y0), (x0 + 13, y0)], fill=hx("e8a858"))
        for k in (2, 6, 10):
            d.point((x0 + k, y0 + 1), fill=hx("4a2408"))
        for k in range(0, 14):
            d.line([(x0 + k, y0 + 2), (x0 + k, y0 + 4)], fill=hx("c88440") if k % 2 == 0 else hx("3a2010"))
    if mirror:  # little round hand mirror on the right, handle towards us
        mx, my = LR.P(c1 - 7, fl, Z1 + 6)
        mx, my = int(mx), int(my)
        d.line([(mx + 1, my + 3), (mx + 3, my + 8)], fill=hx("7a5432"), width=2)
        d.ellipse([mx - 6, my - 3, mx + 6, my + 4], fill=hx("c09850"), outline=hx("5a3c1c"))
        d.ellipse([mx - 4, my - 2, mx + 4, my + 3], fill=hx("d0e0f0"))
        d.line([(mx - 3, my), (mx - 1, my - 2)], fill=hx("f4f8fc"))
        d.point((mx + 2, my + 1), fill=hx("7a8ca0"))
    # pulled-out front panel and knob
    LR.quad(img, [(c0, DR_Y0, zf), (c1, DR_Y0, zf), (c1, DR_Y1, zf), (c0, DR_Y1, zf)], hx("6a4a2e"), wood_d)
    LR.line(img, (c0 + 1, DR_Y1 - 1, zf), (c1 - 1, DR_Y1 - 1, zf), hx("9a7450"))
    kx, ky = LR.P((c0 + c1) / 2, (DR_Y0 + DR_Y1) / 2, zf)
    d.ellipse([kx - 1.5, ky - 1.5, kx + 1.5, ky + 1.5], fill=hx("c8a050"))


def l_bed(img):
    """A narrow iron bed along the right wall: thin straw mattress, coarse grey blanket, flat pillow."""
    X0, X1, Z0, Z1 = BED_X0, BED_X1, BED_Z0, BED_Z1
    d = ImageDraw.Draw(img)
    a, b = LR.P(X0, 0, Z1), LR.P(X1, 0, Z0)
    shadow(img, "polygon", [LR.P(X0 - 2, 0, Z0), LR.P(X1, 0, Z0), LR.P(X1, 0, Z1 + 2), LR.P(X0 - 2, 0, Z1 + 4)], 0.6, 3)
    iron, iron_l = hx("26221e"), hx("4a423a")
    # head frame against the wall
    for x in (X0, X1):
        LR.line(img, (x, 0, Z0), (x, 34, Z0), iron, 2)
    LR.line(img, (X0, 34, Z0), (X1, 34, Z0), iron, 2)
    LR.line(img, (X0, 26, Z0), (X1, 26, Z0), iron)
    for x in range(X0 + 6, X1 - 2, 6):
        LR.line(img, (x, 14, Z0), (x, 34, Z0), iron_l)
    # spring frame, mattress, blanket, pillow
    LR.box(img, X0 + 1, X1 - 1, 10, 12, Z0 + 1, Z1 - 1, iron)
    LR.box(img, X0 + 1, X1 - 1, 12, 17, Z0 + 1, Z1 - 1, hx("a49470"), top=hx("bcae88"), side=hx("7a6c50"))
    LR.box(img, X0 + 4, X1 - 4, 17, 21, Z0 + 2, Z0 + 14, hx("d0c8b4"), top=hx("e0d8c4"), side=hx("a8a08c"))
    blanket, blanket_l, blanket_d = hx("5a5650"), hx("6e6a62"), hx("3e3a36")
    LR.box(img, X0, X1, 6, 18, Z0 + 15, Z1 - 1, blanket, top=blanket_l, side=blanket_d)
    LR.line(img, (X0 + 0.5, 18.2, Z0 + 15), (X1 - 0.5, 18.2, Z0 + 15), hx("d8d0bc"))
    for z in range(Z0 + 20, Z1 - 2, 9):
        LR.line(img, (X0, 18, z), (X0, 7, z + 1), hx("4a4640"))
        LR.line(img, (X0 + 2, 18.1, z), (X1 - 2, 18.1, z + 2), hx("625e56"))
    for z in (Z0 + 18, Z1 - 6):  # woven stripe near each end of the blanket
        LR.line(img, (X0, 17.9, z), (X1, 17.9, z), hx("3e3a36"))
        LR.line(img, (X0, 18, z), (X0, 6, z), hx("3e3a36"))
    rnd = random.Random(271)
    p0, p1 = LR.P(X0, 18, Z0 + 15), LR.P(X0, 6, Z1)
    for _ in range(140):
        x, y = rnd.uniform(p0[0], p1[0] + 30), rnd.uniform(p0[1] - 10, p1[1])
        px, py = int(x), int(y)
        if 0 <= px < W and 0 <= py < H:
            c = img.getpixel((px, py))
            if abs(c[0] - c[2]) < 14 and 40 < c[0] < 140:
                img.putpixel((px, py), mul(c, rnd.choice((0.88, 1.12))))
    # foot frame
    for x in (X0, X1):
        LR.line(img, (x, 0, Z1), (x, 26, Z1), iron, 2)
        px, py = LR.P(x, 27, Z1)
        d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=hx("6a5e4a"))
    LR.line(img, (X0, 26, Z1), (X1, 26, Z1), iron, 2)
    LR.line(img, (X0, 20, Z1), (X1, 20, Z1), iron)
    for x in range(X0 + 6, X1 - 2, 6):
        LR.line(img, (x, 12, Z1), (x, 26, Z1), iron_l)
    LR.line(img, (X0, 11, Z0), (X0, 11, Z1), iron, 2)


def paint_cell(drawer=False, comb=False, mirror=False):
    img = Image.new("RGB", (W, H), hx("141210"))
    l_vault(img)
    l_walls(img)
    l_floor(img)
    g = l_window(img)
    l_door(img)
    l_crucifix(img)
    l_bed(img)
    l_nightstand(img, drawer, comb, mirror)
    fx, fy = l_lamp(img)
    patch, beam, core, moon = moon_patch(img.size)
    lights = [
        ("ellipse", [fx - 110, fy - 70, fx + 110, fy + 110], hx("8a5428"), 0.9, 34),
        ("ellipse", [fx - 55, fy - 34, fx + 60, fy + 70], hx("b06a34"), 0.6, 18),
        ("ellipse", [fx - 22, fy - 18, fx + 22, fy + 20], hx("ffd090"), 0.45, 8),
        ("ellipse", [fx - 190, fy - 150, fx + 150, fy + 60], hx("4a3020"), 0.6, 40),
        ("mask", moon, hx("6878b0"), 0.75, 1),
        ("polygon", beam, hx("303a60"), 0.35, 3),
        ("polygon", g, hx("6070a0"), 0.8, 2),
    ]
    img = lightmap(img, (46, 46, 72), lights)
    light(img, "ellipse", [fx - 7, fy - 9, fx + 7, fy + 7], hx("ffe0a0"), 0.5, 4)
    light(img, "polygon", beam, hx("8898c8"), 0.09, 3)
    light(img, "polygon", core, hx("a8b4e0"), 0.06, 2)
    l_crucifix_lit(img)
    lamp = l_lamp_layer(img.size)
    img.paste(lamp.convert("RGB"), (0, 0), lamp.getchannel("A"))
    vignette(img, 0.6, tint=(16, 14, 26), blur=40)
    return img


# Moonlight falls steeply and straight through the lancet: a window point at height y lands MOON_DEPTH * y in front
# of the wall directly below itself, so the arch's point lands nearest the camera and the shaft stays upright.
MOON_DEPTH = 0.55


def moon_on_floor(x, y):
    return LR.P(x, 0, MOON_DEPTH * y)


def _hull(pts):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in pts))

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
        return out[:-1]
    return half(pts) + half(list(reversed(pts)))


def moon_patch(size):
    """The lancet's moonlit shape on the flagstones with the shadows of its bars and transom cut out of it, the shaft
    joining the glass to it, and a brighter core down the middle of the shaft."""
    inner = lancet(WIN_X - 7, WIN_X + 7, WIN_Y0, 112, 14)
    patch = [moon_on_floor(x, y) for x, y in inner]
    beam = _hull(on_wall(LR, inner, -12) + patch)
    narrow = lancet(WIN_X - 4, WIN_X + 4, WIN_Y0 + 4, 112, 10)
    core = _hull(on_wall(LR, narrow, -12) + [moon_on_floor(x, y) for x, y in narrow])
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.polygon(patch, fill=255)
    for x in (WIN_X - 3.5, WIN_X, WIN_X + 3.5):
        d.line([moon_on_floor(x, WIN_Y0), moon_on_floor(x, 126)], fill=0)
    d.line([moon_on_floor(WIN_X - 7, 100), moon_on_floor(WIN_X + 7, 100)], fill=0)
    clip = Image.new("L", size, 0)
    ImageDraw.Draw(clip).polygon(patch, fill=255)
    return patch, beam, core, ImageChops.darker(m, clip)


def build():
    corridor = paint_corridor()
    px = pixelize(corridor, palette_of(corridor, 128))
    # Our Lady is too small for dithering: her face and robes keep their exact undithered colours
    px.paste(corridor, (0, 0), statue_layer(corridor.size)[0].getchannel("A"))
    px.paste(corridor, (0, 0), crucifix_layer(corridor.size).getchannel("A"))
    save(px, "rooms", "convent_corridor.png")

    base = paint_cell()
    full = paint_cell(drawer=True, comb=True, mirror=True)
    only_comb = paint_cell(drawer=True, comb=True)
    pal = palette_of(Image.blend(base, full, 0.5), 128)
    # the crucifix and the lampstand are too small for dithering: they keep their exact colours, as in the corridor
    cross = ImageChops.lighter(l_crucifix_layer(base.size).getchannel("A"),
                               l_lamp_layer(base.size).getchannel("A").point(lambda v: 255 if v else 0))
    px, drawer, comb = (pixelize(im, pal) for im in (base, full, only_comb))
    for out, src in ((px, base), (drawer, full), (comb, only_comb)):
        out.paste(src, (0, 0), cross)
    save(px, "rooms", "convent_cell.png")
    a, b = _bbox(px, drawer), _bbox(px, comb)
    box = (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))
    save(drawer.crop(box), "rooms", "convent_cell_drawer.png")
    save(comb.crop(box), "rooms", "convent_cell_drawer_comb.png")
    print(f"  convent_cell_drawer(.png/_comb.png) at {box[:2]} size {(box[2] - box[0], box[3] - box[1])}")
    cell_bed_art()
    return corridor, base


# The First Interlude's night in the cell: where the player stands while she sits on the bed (room pixels, where the
# room's perspective scale is 1), the room box her sitting sprite covers, and the point of the bed's near edge, by the
# pillow, she sits on.
CELL_SIT_AT = (364, 236)
CELL_SIT_BOX = (300, 120, 470, 262)
CELL_SEAT = (BED_X0 + 5, 18, BED_Z0 + 30)  # just clear of the nightstand, her legs in front of it


def cell_bed_art():
    """eleanor_cell_sit: awake in her pyjamas on the edge of the bed by the pillow, facing the door, her hands on the
    blanket beside her, feet on the floor. Drawn in room pixels as seen, then mirrored so the player (facing left, so
    flipped) shows it the right way round."""
    import math
    import numpy as np
    from PIL import ImageOps
    from .sprites import ELEANOR_PYJAMA, figure, pose, FW, FH, action_strip, PLAYER_IDLE_YAW, SCALE
    x0, y0, x1, y1 = CELL_SIT_BOX
    w, h = x1 - x0, y1 - y0
    px, py = CELL_SIT_AT
    hip = LR.P(*CELL_SEAT)
    floor_y = LR.P(BED_X0, 0, CELL_SEAT[2])[1]
    drop = floor_y - hip[1]
    # the room's perspective scale where her feet are, relative to the player's at CELL_SIT_AT (from convent_cell.tscn)
    def depth(y):
        return 0.92 + (y - 197) / (265 - 197) * (1.06 - 0.92)

    # seated, the seat rounds up her back from the blanket to the waist
    spec = dict(ELEANOR_PYJAMA, h=ELEANOR_PYJAMA["h"] * depth(floor_y) / depth(py), rear=(0.035, 0.075, 0.47, 0.08))
    H = spec["h"] * SCALE
    thigh = 84

    def sole(knee):
        a, k = math.radians(thigh), math.radians(knee)
        return 0.5 + 0.235 * math.cos(a) + 0.215 * math.cos(a - k) + 0.03 + 0.018

    knee = min(range(30, 100), key=lambda k: abs((sole(k) - 0.5) * H - drop))  # feet flat on the floor

    def resting(s):  # arm hanging straight, the hand flat on the blanket beside her hip
        return ("pts", (s * 0.118, 0.37, -0.02), (s * 0.125, 0.49, 0.0), (s * 0.125, 0.52, 0.015))

    ps = pose(PLAYER_IDLE_YAW, arms={1: resting(1), -1: resting(-1)},
              legs={1: (thigh, knee, 0), -1: (thigh - 4, knee - 4, 0)})
    fig = np.asarray(ImageOps.mirror(figure(spec, ps, FW, FH))).copy()
    fig[fig[..., 3] < 255] = 0  # no floor shadow: she sits on the bed
    base_y = FH - 3.0
    fx = round(hip[0] - FW / 2) - x0
    fy = round(hip[1] - (base_y - (sole(knee) - 0.5) * H)) - y0
    img = Image.new("RGBA", (w, h))
    img.alpha_composite(Image.fromarray(fig, "RGBA"), (fx, fy))
    head = (fx + FW // 2, round(fy + base_y - (sole(knee) - 0.06) * H))
    action_strip("eleanor_cell_sit", [(ImageOps.mirror(img), (w - head[0], head[1]))], [1.0],
                 anchor=(w - (px - x0), py - y0))
