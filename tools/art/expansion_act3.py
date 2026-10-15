"""Act 3 expansion (puzzle 15): the Harrington wine cellar under the kitchen, pitch dark until the storm lantern is
filled and lit, then the bootleggers' service stair up to the old man's study bar; the kitchen's cellar trapdoor and the
study bar-panel hatch (patched onto the committed mansion rooms, so mansion.py and its pixel tests are untouched); and
the lantern / kerosene icons.

The cellar is painted once per state and the state overlays are cut against the dark base (see act2_rooms.overlay)."""
import math
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageChops, ImageFilter
from .common import ART, W, FULL_H, hx, mix, mul, vgrad, noise, light, shadow, vignette, palette_of, pixelize, save, text
from .act2_rooms import bricks, overlay
from .mansion import grade, flagstones, _flame, _smoke
from .furniture import Room3D
from .items import _icon

H = FULL_H
CFL = 200  # where the cellar's back wall meets the floor

LANTERN_HOOK = (179, 108)
STAIR_NAIL = (388, 140)
CAN = (305, 26, 46)  # world position of the kerosene can on the crates
BARREL = (324, 372, 224, 13)  # the lying barrel of whiskey: left end, right end, axis row and radius
BARREL_FEET = 239  # the floor row under its chocks, its y-sort point
POOL = (372, 246)  # centre of the whiskey pool in front of its spigot
CELLAR_FIRE_FRAMES = 8


# ------------------------------------------------------------------------------------------------ CELLAR

def _storm_lantern(d, x, y, lit=False):
    """A tin hurricane lantern hanging by its bail from (x, y)."""
    tin, tin_d = hx("6a7468"), hx("3a4038")
    d.arc([x - 6, y, x + 6, y + 12], 180, 360, fill=hx("4a4a50"))
    d.rectangle([x - 5, y + 6, x + 5, y + 9], fill=tin)
    d.line([(x - 5, y + 6), (x + 5, y + 6)], fill=mul(tin, 1.3))
    glass = hx("ffd070") if lit else hx("8a9a9a")
    d.ellipse([x - 7, y + 9, x + 7, y + 25], fill=glass, outline=tin_d)
    if lit:
        d.ellipse([x - 3, y + 13, x + 3, y + 21], fill=hx("fff0b0"))
        d.line([(x, y + 14), (x, y + 19)], fill=hx("fffce8"))
    else:
        d.line([(x - 4, y + 12), (x - 4, y + 18)], fill=hx("c8d4d0"))
    for gx in (x - 7, x, x + 7):  # wire guards
        d.line([(gx, y + 9), (gx, y + 25)], fill=tin_d)
    d.rectangle([x - 8, y + 25, x + 8, y + 32], fill=tin, outline=tin_d)
    d.line([(x - 8, y + 28), (x + 8, y + 28)], fill=tin_d)
    d.line([(x - 9, y + 11), (x - 9, y + 27)], fill=tin_d)  # side tubes
    d.line([(x + 9, y + 11), (x + 9, y + 27)], fill=tin_d)


def _kerosene_can(d, x, y):
    """A dented one-gallon can standing with its base at (x, y)."""
    d.rectangle([x - 6, y - 15, x + 6, y], fill=hx("a83024"), outline=hx("4a1410"))
    d.line([(x - 5, y - 14), (x - 5, y - 1)], fill=hx("d85a40"))
    d.rectangle([x - 4, y - 10, x + 4, y - 5], fill=hx("d8c890"))
    d.line([(x - 3, y - 8), (x + 3, y - 8)], fill=hx("4a1410"))
    d.line([(x + 3, y - 15), (x + 7, y - 21)], fill=hx("8a8a90"), width=2)  # spout
    d.arc([x - 5, y - 21, x + 1, y - 13], 180, 360, fill=hx("2a2a2c"), width=2)  # handle
    d.point((x + 2, y - 4), fill=hx("6a1a14"))  # the dent


WHISKEY_D, WHISKEY, WHISKEY_L = hx("6a3410"), hx("b06a1c"), hx("f0c060")


def _lying_barrel(img, xl, xr, cy, r, open=False):
    """An oak barrel on its side, axis running left-right: bulging staves shaded round the belly, iron hoops, and the
    head (with its planks, chime and a brass spigot) showing as an ellipse at the right end. Opened, the spigot is
    turned along the pipe and the old man's whiskey runs out of it in a thin amber rope."""
    shadow(img, "ellipse", [xl - 2, cy + r - 4, xr + 6, cy + r + 5], 0.6, 3)
    d = ImageDraw.Draw(img)
    for cx in (xl + 8, xr - 10):  # wooden chocks
        d.polygon([(cx - 5, cy + r + 2), (cx + 5, cy + r + 2), (cx + 3, cy + r - 3), (cx - 3, cy + r - 3)],
                  fill=hx("5a4228"), outline=hx("2a1a0c"))
    hw = 5  # half-width of the head ellipse
    body_r = xr - hw
    xc, half = (xl + body_r) / 2, (body_r - xl) / 2
    oak_l, oak, oak_d = hx("a8784a"), hx("7a5432"), hx("3a2414")
    for x in range(xl, body_r + 1):
        u = (x - xc) / half
        h = r * (1 - 0.16 * u * u)
        for y in range(int(cy - h), int(cy + h) + 1):
            v = (y - cy) / h  # -1 top .. 1 bottom
            k = 1.15 - 0.55 * (v + 1) / 2 - 0.25 * max(0.0, v) ** 2
            c = mix(oak_d, oak_l, max(0.0, min(1.0, k - 0.25)))
            d.point((x, y), fill=c)
    for s in (-0.66, -0.3, 0.05, 0.4, 0.74):  # stave joints follow the bulge
        pts = []
        for x in range(xl, body_r + 1):
            u = (x - xc) / half
            pts.append((x, cy + s * r * (1 - 0.16 * u * u)))
        d.line(pts, fill=mul(oak_d, 1.2))
    d.line([(x, cy - r * (1 - 0.16 * ((x - xc) / half) ** 2) + 2) for x in range(xl + 3, body_r - 2)],
           fill=hx("c89a64"))  # the sheen along the top
    for hxp in (xl + 2, xl + 9, body_r - 9, body_r - 2):  # iron hoops
        u = (hxp - xc) / half
        h = r * (1 - 0.16 * u * u)
        d.line([(hxp, cy - h), (hxp, cy + h)], fill=hx("2a2a2e"), width=2)
        d.point((hxp, int(cy - h) + 1), fill=hx("7a7a84"))
        d.point((hxp - 1, int(cy - h) + 3), fill=hx("5a5a62"))
    # the left end turns away into shadow; the right end is the head
    hr = r * 0.84
    d.ellipse([xl - 3, cy - hr, xl + 3, cy + hr], fill=mul(oak_d, 0.8))
    d.ellipse([body_r - hw, cy - hr, body_r + hw, cy + hr], fill=hx("8a6038"), outline=oak_d)
    for k in (-0.5, 0, 0.5):  # head planks
        yy = cy + k * hr
        d.line([(body_r - hw + 1, yy), (body_r + hw - 1, yy)], fill=hx("5a3a20"))
    d.arc([body_r - hw + 1, cy - hr + 2, body_r + hw - 1, cy + hr - 2], 260, 100, fill=hx("b08a5a"))
    d.rectangle([body_r + hw - 1, cy + 2, body_r + hw + 3, cy + 4], fill=hx("b08a3a"))  # brass spigot
    tx = body_r + hw + 3
    d.line([(tx, cy + 4), (tx, cy + 7)], fill=hx("806020"))
    if open:
        d.line([(tx - 1, cy + 1), (tx + 1, cy + 1)], fill=hx("d8b060"))  # the handle, turned along the pipe
        for y in range(cy + 8, cy + r + 9):  # the whiskey, falling and fanning out as it nears the flags
            f = (y - cy - 8) / (r + 1)
            x = tx + 2.5 * f * f
            d.line([(x - 0.5 * f, y), (x + 0.5 + 0.8 * f, y)], fill=WHISKEY)
            if y % 3 == 0:
                d.point((int(x), y), fill=WHISKEY_L)
    else:
        d.point((tx, cy + 9), fill=WHISKEY)  # a drip of the old man's whiskey
    d.ellipse([xc - 2, cy - r + 2, xc + 2, cy - r + 5], fill=hx("4a2c16"))  # the bung on top


def _whiskey_pool(img, cx, cy):
    """The whiskey spreading over the flags in front of the barrel: a pool with a dark rim, runnels finding the
    joints between the stones, and the lantern caught in it as streaks of gold."""
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 30, cy - 5, cx + 18, cy + 6], fill=WHISKEY_D)
    d.ellipse([cx - 28, cy - 4, cx + 16, cy + 4], fill=WHISKEY)
    d.polygon([(cx - 28, cy), (cx - 54, cy + 3), (cx - 56, cy + 5), (cx - 30, cy + 3)], fill=WHISKEY_D)  # runnels
    d.polygon([(cx + 10, cy + 3), (cx + 24, cy + 12), (cx + 22, cy + 13), (cx + 6, cy + 5)], fill=WHISKEY_D)
    d.line([(cx - 52, cy + 4), (cx - 30, cy + 2)], fill=WHISKEY)
    for x0, y0, n in ((cx - 18, cy - 2, 10), (cx - 4, cy + 1, 8), (cx + 4, cy - 2, 6)):  # reflections
        d.line([(x0, y0), (x0 + n, y0)], fill=WHISKEY_L)


def _cellar_fire(img, em, cx, cy, t):
    """The whiskey alight at phase t (looping on 1): a blue skin of flame over the pool, orange tongues over it
    and up the barrel, smoke rolling up into the vault. The flames are marked emissive in em."""
    tau = 2 * math.pi
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for i, (sx, sy) in enumerate(((cx - 14, cy - 50), (cx - 36, cy - 44))):
        _smoke(layer, sx, sy, 130, -40 + 30 * i, 12, (t + i * 0.5) % 1.0, 7, 1520 + i)
    layer.putalpha(layer.getchannel("A").point(lambda a: a * 3 // 5))
    fl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fl)
    d.ellipse([cx - 31, cy - 5, cx + 19, cy + 6], fill=hx("3a5ac8"))
    d.ellipse([cx - 26, cy - 3, cx + 14, cy + 3], fill=hx("7a9af0"))
    d.line([(cx - 55, cy + 4), (cx - 30, cy + 2)], fill=hx("4a6ad8"), width=2)
    tongues = ((-38, -12, 40, 5, 0.71), (-26, -16, 52, 6, 0.05), (-14, -15, 30, 4, 0.53),  # along the barrel
               (-48, 4, 12, 3, 0.45), (-24, 2, 30, 5, 0.0), (-12, 3, 48, 6, 0.31), (0, 2, 56, 7, 0.62),
               (10, 3, 36, 5, 0.17), (17, 1, 18, 3, 0.83))  # (dx, dy, height, half-width, phase), back to front
    for dx, dy, h, w, ph in tongues:
        _flame(d, cx + dx, cy + dy, h, w, t, ph, lean=0.4 * math.sin(tau * (t + ph)))
    for k in range(6):  # sparks spiralling up off the barrel
        q = (t * 2 + k / 6) % 1.0
        x = cx - 30 + k * 9 + 4 * math.sin(tau * (q + k * 0.21))
        d.point((x, cy - 20 - q * 80), fill=hx("ffc060") if q < 0.6 else hx("a85a2a"))
    em.paste(255, mask=fl.getchannel("A"))
    out = Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), layer), fl).convert("RGB")
    img.paste(out)


def paint_cellar(lantern=True, can=True, lit=False, barrel=False, barrel_open=False, pool=False, lantern_down=False,
                 fire_t=None):
    """lit hangs the lantern on the stair nail; lantern_down takes it back off (Micah carries it, so the light stays).
    The barrel is painted only for its own y-sorted sprites (see build_cellar), so Micah can walk behind it;
    barrel_open turns its spigot so the whiskey runs out, and pool spreads it over the flags. fire_t sets it all alight
    at that phase, barrel included, since the fire frames cover the whole room."""
    fire = fire_t is not None
    barrel = barrel or fire
    barrel_open = barrel_open or fire
    pool = pool or fire
    lantern_down = lantern_down or fire
    img = Image.new("RGB", (W, H))
    em = Image.new("L", img.size, 0)
    ed = ImageDraw.Draw(em)
    rnd = random.Random(1515)
    R = Room3D(CFL, 240, 100)
    # ---- brick barrel vault and back wall, old limewash flaking off the lower courses ----
    bricks(img, (0, 0, W - 1, CFL), hx("7a4a34"), hx("3a2a22"), 1501, h=5, w=12)
    for _ in range(26):
        x, y = rnd.randint(0, W - 1), rnd.randint(110, CFL - 6)
        light(img, "ellipse", [x - rnd.randint(8, 20), y - 5, x + rnd.randint(8, 20), y + 6], hx("8a8070"), 0.35, 3)
    d = ImageDraw.Draw(img)
    for cx in (130, 350):  # vault ribs
        d.arc([cx - 150, -60, cx + 150, 120], 200, 340, fill=hx("4a2c20"), width=6)
        d.arc([cx - 147, -57, cx + 147, 117], 200, 340, fill=hx("9a6448"), width=1)
    shadow(img, "rect", [0, 0, W, 40], 0.6, 14)
    d = ImageDraw.Draw(img)
    # ---- the kitchen trapdoor in the ceiling, top left: the only light there is ----
    vgrad(img, (24, 0, 98, 18), hx("6a7aa8"), hx("3a4a7a"))
    ed.rectangle([24, 0, 98, 18], fill=120)
    d.rectangle([20, 18, 102, 22], fill=hx("4a3424"))
    d.polygon([(98, 0), (120, 0), (112, 18), (102, 18)], fill=hx("5a4430"))  # the raised flap
    # ---- the wooden kitchen stair coming down on the left ----
    for i in range(9):
        ty = 34 + i * 19
        tx0 = 24 + i * 10
        d.rectangle([tx0, ty, tx0 + 46, ty + 4], fill=hx("8a6a44"))
        d.line([(tx0, ty), (tx0 + 46, ty)], fill=hx("b08a5a"))
        d.rectangle([tx0, ty + 5, tx0 + 46, ty + 7], fill=hx("3a2a1a"))
    d.line([(22, 22), (114, 204)], fill=hx("5a4028"), width=4)  # stringers
    d.line([(70, 22), (162, 204)], fill=hx("5a4028"), width=4)
    d.line([(80, 8), (170, 156)], fill=hx("6a4a2e"), width=2)  # handrail and its posts
    for k in range(4):
        t = (k + 1) / 5
        rx, ry = 80 + 90 * t, 8 + 148 * t
        d.line([(rx, ry), (rx, ry + 34)], fill=hx("4a3420"), width=2)
    # ---- the brick pier with the lantern hook ----
    bricks(img, (166, 24, 192, CFL), hx("8a5a40"), hx("3a2a22"), 1502, h=5, w=9)
    d = ImageDraw.Draw(img)
    d.line([(192, 24), (192, CFL)], fill=hx("3a2418"), width=2)
    hx0, hy0 = LANTERN_HOOK
    d.line([(hx0 - 4, hy0 - 6), (hx0, hy0 - 6), (hx0, hy0)], fill=hx("2a2a2e"), width=2)  # iron hook
    d.arc([hx0 - 3, hy0 - 3, hx0 + 3, hy0 + 3], 0, 200, fill=hx("2a2a2e"), width=2)
    if lantern:
        _storm_lantern(d, hx0, hy0 + 1)
    # ---- wine racks along the back wall ----
    wx0, wx1, wy0 = 204, 352, 70
    d.rectangle([wx0, wy0, wx1, CFL], fill=hx("2a1a10"))
    for x in range(wx0, wx1 + 1, 14):
        d.line([(x, wy0), (x, CFL)], fill=hx("6a4a2a"), width=2)
    for y in range(wy0, CFL + 1, 12):
        d.line([(wx0, y), (wx1, y)], fill=hx("6a4a2a"), width=2)
        for x in range(wx0 + 7, wx1, 14):
            if y + 6 < CFL and rnd.random() < 0.82:
                d.ellipse([x - 4, y + 2, x + 4, y + 10], fill=hx("1e3a22"), outline=hx("0e1a10"))
                d.point((x - 1, y + 4), fill=hx("6aa070"))
    d.rectangle([wx0 - 3, wy0 - 6, wx1 + 3, wy0], fill=hx("7a5634"))
    # ---- the bootleggers' service stair, going up the far right wall to a panel ----
    sx0 = 368
    d.rectangle([sx0, 14, W - 1, CFL], fill=hx("2a1c16"))
    d.line([(sx0, 14), (sx0, CFL)], fill=hx("4a3024"), width=3)
    for i in range(11):
        ty = 186 - i * 15
        tx0 = sx0 + 8 + i * 7
        d.rectangle([tx0, ty, min(W - 1, tx0 + 40), ty + 4], fill=hx("8a8274"))
        d.line([(tx0, ty), (min(W - 1, tx0 + 40), ty)], fill=hx("b0a894"))
        d.rectangle([tx0, ty + 5, min(W - 1, tx0 + 40), ty + 14], fill=hx("4a4238"))
    d.line([(sx0 + 4, 150), (sx0 + 82, 16)], fill=hx("6a5a48"), width=2)  # a rope rail
    d.rectangle([432, 14, 474, 30], fill=hx("5a3a20"), outline=hx("2a1a0c"))  # the back of the bar panel
    for x in (442, 454, 466):
        d.line([(x, 15), (x, 29)], fill=hx("3a2410"))
    d.rectangle([436, 21, 442, 23], fill=hx("8a8a90"))  # its bolt
    nx, ny = STAIR_NAIL
    d.rectangle([nx - 1, ny - 1, nx + 1, ny + 1], fill=hx("3a3a3e"))
    # cobwebs in the corners
    for cx, cy, sx in ((0, 24, 1), (W - 1, 14, -1), (204, 64, 1)):
        for k in range(5):
            d.line([(cx, cy), (cx + sx * (10 + k * 6), cy + 14 - k * 3)], fill=hx("9a9488"))
        d.arc([cx - 18, cy - 18, cx + 18, cy + 18], 0 if sx > 0 else 90, 90 if sx > 0 else 180, fill=hx("9a9488"))
    # ---- floor: old flagstones, straw from the deliveries ----
    flagstones(img, CFL, H - 1, 240, 100, 30, hx("6a6458"), hx("4e4a42"), hx("2a2620"), 1503)
    noise(img, (0, CFL, W - 1, H - 1), 5, 1504)
    shadow(img, "rect", [0, CFL, W, CFL + 8], 0.5, 3)
    d = ImageDraw.Draw(img)
    for _ in range(60):
        x, y = rnd.randint(180, 360), rnd.randint(CFL + 6, 250)
        d.line([(x, y), (x + rnd.randint(-4, 4), y + rnd.randint(-2, 2))], fill=hx("b89a50"))
    # ---- the delivery crates: two on the floor, one on top, straw spilling out ----
    for x0, x1, y0, y1, z0, z1, word in ((222, 274, 0, 26, 34, 62, "WINE"), (280, 330, 0, 26, 30, 60, "ALTAR"),
                                          (228, 270, 26, 50, 36, 58, None)):
        R.box(img, x0, x1, y0, y1, z0, z1, hx("a8844e"), top=hx("c09a60"), side=hx("7a5a30"))
        d = ImageDraw.Draw(img)
        a, b = R.P(x0, y1, z1), R.P(x1, y0, z1)
        for y in range(int(a[1]) + 5, int(b[1]), 6):
            d.line([(a[0] + 1, y), (b[0] - 1, y)], fill=hx("7a5a30"))
        d.line([(a[0] + 2, a[1] + 2), (b[0] - 2, b[1] - 2)], fill=hx("8a6a3a"), width=2)
        if word:
            text(img, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), word, hx("3a2410"), size=8)
        d = ImageDraw.Draw(img)
        for k in range(6):
            p = R.P(x0 + 4 + k * (x1 - x0 - 8) / 5, y1, (z0 + z1) / 2)
            d.line([p, (p[0] + rnd.randint(-3, 3), p[1] - rnd.randint(2, 5))], fill=hx("d8b860"))
    if can:
        p = R.P(*CAN)
        _kerosene_can(d, int(p[0]), int(p[1]))
    # a barrel of whiskey lying on its side out on the floor, on chocks, its head and tap turned to the room
    if barrel:
        _lying_barrel(img, *BARREL, open=barrel_open)
    if pool:
        _whiskey_pool(img, *POOL)
    if fire:
        _cellar_fire(img, em, *POOL, fire_t)
    d = ImageDraw.Draw(img)
    # ---- the lantern hung at the stair foot, once it is lit ----
    if lit and not lantern_down:
        _storm_lantern(d, nx, ny, lit=True)
        ed.ellipse([nx - 7, ny + 9, nx + 7, ny + 25], fill=255)
    # ---- light ----
    hatch = (60, 30, 80, 90, (0.55, 0.62, 0.95), 0.9)
    if fire:
        px_, py_ = POOL
        k = 0.9 + 0.1 * math.sin(2 * math.pi * fire_t) + 0.05 * math.sin(6 * math.pi * fire_t)
        pools = [hatch, (px_, py_ - 30, 240, 170, (1.75, 1.05, 0.55), k), (px_ - 10, py_ - 20, 90, 70, (2.0, 1.3, 0.7), 0.7 * k)]
        img = grade(img, (0.2, 0.18, 0.24), pools, em)
        light(img, "ellipse", [px_ - 60, py_ - 50, px_ + 40, py_ + 12], hx("f08030"), 0.35 * k, 14)
        vignette(img, 0.45, (10, 4, 4), 40)
    elif lit:
        pools = [hatch, (nx, ny + 20, 190, 150, (1.25, 0.95, 0.62), 1.0), (nx, ny + 20, 70, 60, (1.5, 1.15, 0.8), 0.6)]
        img = grade(img, (0.2, 0.2, 0.28), pools, em)
        light(img, "ellipse", [nx - 26, ny - 6, nx + 26, ny + 46], hx("f0b060"), 0.4, 10)
        vignette(img, 0.45, (8, 6, 12), 40)
    else:
        pools = [hatch, (hx0, hy0 + 18, 26, 30, (0.42, 0.42, 0.55), 0.7),
                 (276, 172, 70, 36, (0.3, 0.3, 0.4), 0.6)]
        img = grade(img, (0.07, 0.07, 0.11), pools, em)
        shadow(img, "rect", [sx0, 0, W, CFL + 20], 0.6, 10)  # the service stair stays black
        vignette(img, 0.6, (4, 4, 10), 40)
    return img


def _cut_barrel(variant, base_px, pal, name):
    """The barrel (with its shadow) as an RGBA sprite: everything that differs from the room without it."""
    a = np.asarray(pixelize(variant, pal).convert("RGB")).astype(np.int16)
    b = np.asarray(base_px.convert("RGB")).astype(np.int16)
    mask = np.abs(a - b).sum(axis=2) > 0
    im = Image.fromarray(np.dstack([a.astype(np.uint8), (mask * 255).astype(np.uint8)]), "RGBA")
    bb = im.getbbox()
    save(im.crop(bb), "rooms", name + ".png")
    print(f"{name} at ({bb[0]}, {bb[1]}) size {bb[2] - bb[0]}x{bb[3] - bb[1]}")
    return bb


def build_cellar():
    base = paint_cellar()
    lit = dict(lantern=False, can=False, lit=True)
    v = {"no_lantern": paint_cellar(lantern=False), "no_can": paint_cellar(can=False), "lit": paint_cellar(**lit),
         "whiskey": paint_cellar(**lit, pool=True), "lantern_down": paint_cellar(**lit, lantern_down=True)}
    barrel = {"barrel": paint_cellar(barrel=True), "barrel_lit": paint_cellar(**lit, barrel=True),
              "barrel_open": paint_cellar(**lit, barrel=True, barrel_open=True)}
    both = Image.new("RGB", (W * 3, H))
    both.paste(barrel["barrel"], (0, 0))
    both.paste(barrel["barrel_lit"], (W, 0))
    both.paste(paint_cellar(**lit, barrel=True, barrel_open=True, pool=True), (W * 2, 0))
    pal = palette_of(both, 124)
    px = pixelize(base, pal)
    lit_px = pixelize(v["lit"], pal)
    _cut_barrel(barrel["barrel"], px, pal, "mansion_cellar_barrel")
    for name in ("barrel_lit", "barrel_open"):
        _cut_barrel(barrel[name], lit_px, pal, "mansion_cellar_" + name)
    save(px, "rooms", "mansion_cellar.png")
    hx0, hy0 = LANTERN_HOOK
    overlay(v["no_lantern"], px, pal, (hx0 - 14, hy0 - 2, hx0 + 14, hy0 + 40), "mansion_cellar_lantern_taken")
    p = Room3D(CFL, 240, 100).P(*CAN)
    overlay(v["no_can"], px, pal, (int(p[0]) - 12, int(p[1]) - 26, int(p[0]) + 12, int(p[1]) + 4),
            "mansion_cellar_can_taken")
    overlay(v["lit"], px, pal, (0, 0, W, H), "mansion_cellar_lit")
    # the escape: cut against the lit cellar, since they sit on top of it
    nx, ny = STAIR_NAIL
    overlay(v["lantern_down"], lit_px, pal, (nx - 12, ny - 2, nx + 12, ny + 36), "mansion_cellar_lantern_down")
    bx0, bx1, by, br = BARREL
    cx, cy = POOL
    overlay(v["whiskey"], lit_px, pal, (bx0 - 40, by - br - 2, cx + 30, cy + 16), "mansion_cellar_whiskey")
    fire = [paint_cellar(**lit, fire_t=i / CELLAR_FIRE_FRAMES) for i in range(CELLAR_FIRE_FRAMES)]
    fpal = palette_of(Image.blend(fire[0], fire[CELLAR_FIRE_FRAMES // 2], 0.5), 160)
    strip = Image.new("RGB", (W * CELLAR_FIRE_FRAMES, H))
    for i, frame in enumerate(fire):
        strip.paste(pixelize(frame, fpal), (i * W, 0))
    save(strip, "rooms", "mansion_cellar_fire.png")
    print("mansion_cellar_fire:", CELLAR_FIRE_FRAMES, "frames")
    return px, v


# ------------------------------------------------------------------------------------------------ PATCHES

def _patch(room, box, draw_fn, name, relight=None):
    """Paints draw_fn onto a copy of a committed room background and saves the changed pixels (pixelized with the
    room's own colours plus the new ones) as an RGBA overlay. Returns and prints its top-left for the scene.
    relight names a committed full-frame lighting variant of the room: the patch is then re-lit by that variant's
    (blurred) brightness ratio to the base, so it can sit on top of that overlay instead."""
    with Image.open(os.path.join(ART, "rooms", room + ".png")) as im:
        base = im.convert("RGB")
    mod = base.copy()
    draw_fn(mod)
    region, before = mod.crop(box), base.crop(box)
    changed = ImageChops.difference(region, before).convert("L").point(lambda v: 255 if v > 2 else 0)
    if relight:
        with Image.open(os.path.join(ART, "rooms", relight + ".png")) as im:
            lit = im.convert("RGB").crop(box)
        soft = ImageFilter.GaussianBlur(6)
        ratio = (np.asarray(lit.filter(soft), np.float32) + 4) / (np.asarray(before.filter(soft), np.float32) + 4)
        region = Image.fromarray(np.clip(np.asarray(region, np.float32) * ratio, 0, 255).astype(np.uint8))
        before = lit
    pal = palette_of(before, 48) + palette_of(region, 48)
    px = pixelize(region, pal)
    out = px.convert("RGBA")
    out.putalpha(changed)
    bb = changed.getbbox()
    if not bb:
        raise ValueError(name)
    save(out.crop(bb), "rooms", name + ".png")
    print(name, "at", (box[0] + bb[0], box[1] + bb[1]))
    return box[0] + bb[0], box[1] + bb[1]


KITCHEN = Room3D(204, 240, 100)  # mansion.paint_kitchen's projection
KITCHEN_HATCH = (252, 330, 150, 220)  # world x0, x1, z0, z1 of the trapdoor on the kitchen floor


def _kitchen_trapdoor(img):
    R = KITCHEN
    x0, x1, z0, z1 = KITCHEN_HATCH
    shadow(img, "polygon", [R.P(x0 - 3, 0, z0 - 3), R.P(x1 + 3, 0, z0 - 3), R.P(x1 + 3, 0, z1 + 3),
                            R.P(x0 - 3, 0, z1 + 3)], 0.5, 2)
    R.quad(img, [(x0, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1)], hx("2a2630"), hx("100e14"))
    for k in range(1, 4):  # boards
        x = x0 + k * (x1 - x0) / 4
        R.line(img, (x, 0, z0), (x, 0, z1), hx("1a1410"))
        R.line(img, (x + 1.5, 0, z0), (x + 1.5, 0, z1), hx("4a3a2c"))
    for z in (z0 + 10, z1 - 10):  # iron straps
        R.line(img, (x0 + 2, 0, z), (x1 - 2, 0, z), hx("26262c"), 2)
    rp = R.P((x0 + x1) / 2, 0, z1 - 22)
    d = ImageDraw.Draw(img)
    d.ellipse([rp[0] - 6, rp[1] - 3, rp[0] + 6, rp[1] + 3], outline=hx("5a5a62"), width=2)  # the lifting ring
    d.point((rp[0] - 4, rp[1] - 2), fill=hx("8a8a94"))


def _kitchen_box():
    x0, x1, z0, z1 = KITCHEN_HATCH
    a, b = KITCHEN.P(x0 - 6, 0, z0 - 6), KITCHEN.P(x1 + 6, 0, z1 + 6)
    return int(a[0]) - 2, int(a[1]) - 2, min(W, int(b[0]) + 3), min(H, int(b[1]) + 3)


def _study_hatch(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 349, 169, 413, 203  # inside the drinks cabinet's front
    d.rectangle([x0, y0, x1, y1], fill=hx("0c0806"))
    # a narrow stone stair dropping away from the cabinet: each step a worn tread over a block riser, narrowing
    # into the shaft, lit warmer the deeper it goes by a lantern burning somewhere below
    stone, stone_d, joint = hx("4a4238"), hx("1e1a14"), hx("0a0806")
    warm = hx("b87a36")
    n, top = 5, y0 + 2
    # the shaft walls, rough blocks fading into the dark
    d.polygon([(x0, y0), (x0 + 7, y0 + 2), (x0 + 16, y1), (x0, y1)], fill=hx("16120e"))
    d.polygon([(x1, y0), (x1 - 7, y0 + 2), (x1 - 16, y1), (x1, y1)], fill=hx("100c0a"))
    for yy in range(y0 + 5, y1, 6):
        d.line([(x0, yy), (x0 + 8 + (yy - y0) // 8, yy)], fill=joint)
        d.line([(x1 - 8 - (yy - y0) // 8, yy), (x1, yy)], fill=joint)
    for k in range(n):
        t = k / (n - 1)
        a, b = x0 + 8 + k * 2, x1 - 8 - k * 2
        ty = top + k * 6
        tread = mix(mul(stone, 0.9 - 0.25 * t), warm, 0.15 + 0.4 * t)  # nearer steps grey, deeper ones lamp-warm
        d.rectangle([a, ty + 2, b, ty + 5], fill=tread)  # the tread, seen from above
        d.line([(a, ty + 2), (b, ty + 2)], fill=mul(tread, 1.25))  # the worn nosing
        d.rectangle([a, ty, b, ty + 1], fill=stone_d)  # the riser, in shadow under the step above
        for jx in range(a + 4 + (k % 2) * 7, b - 2, 14):  # joints between the slabs
            d.line([(jx, ty + 3), (jx, ty + 5)], fill=mul(tread, 0.6))
        mid = (a + b) // 2
        d.line([(mid - 6, ty + 4), (mid + 4, ty + 4)], fill=mul(tread, 0.88))  # the dip worn by feet
    for bx, by in ((x1 - 5, y0 + 4), (x1 - 12, y1 - 6)):  # iron brackets holding a rope rail down the wall
        d.rectangle([bx - 1, by - 1, bx + 1, by + 1], fill=hx("3a3632"))
    d.line([(x1 - 5, y0 + 4), (x1 - 12, y1 - 6)], fill=hx("8a7448"))
    d.line([(x1 - 4, y0 + 5), (x1 - 11, y1 - 5)], fill=hx("4a3a22"))
    light(img, "ellipse", [x0 + 14, y1 - 10, x1 - 14, y1 + 10], hx("a86a2a"), 0.55, 5)  # the lantern, down below
    d = ImageDraw.Draw(img)
    d.line([(x0, y0), (x1, y0)], fill=hx("040200"))  # the dark lip under the cabinet's top
    d.polygon([(346, 166), (337, 169), (337, 210), (346, 206)], fill=hx("2e1a0e"), outline=hx("140a04"))  # door leaves
    d.polygon([(416, 166), (425, 169), (425, 210), (416, 206)], fill=hx("2e1a0e"), outline=hx("140a04"))
    d.line([(339, 175), (339, 203)], fill=hx("4a2c16"))
    d.line([(423, 175), (423, 203)], fill=hx("4a2c16"))
    d.rectangle([x1 - 8, y0 + 2, x1 - 2, y0 + 4], fill=hx("6a6a70"))  # the bolt, drawn back


# ------------------------------------------------------------------------------------------------ ICONS

def lantern(d, im, fuel=False, lit=False):
    tin, tin_d = hx("7a8478"), hx("3a4038")
    d.arc([10, 0, 22, 10], 180, 360, fill=hx("4a4a50"), width=2)
    d.rectangle([11, 4, 21, 6], fill=tin)
    d.ellipse([10, 6, 22, 17], fill=hx("ffd070") if lit else hx("9ab0b0"))
    if lit:
        d.ellipse([13, 8, 19, 15], fill=hx("fff0b0"))
        d.line([(16, 9), (16, 13)], fill=hx("ffffff"))
    else:
        d.line([(12, 9), (12, 13)], fill=hx("e0ecec"))
        d.line([(16, 12), (16, 15)], fill=hx("2a2a2a"))  # the wick
    for x in (10, 16, 22):
        d.line([(x, 7), (x, 16)], fill=tin_d)
    d.rectangle([9, 17, 23, 22], fill=tin)
    if fuel:
        d.rectangle([11, 19, 21, 21], fill=hx("c89040"))
    d.line([(8, 8), (8, 20)], fill=tin_d)
    d.line([(24, 8), (24, 20)], fill=tin_d)


def kerosene(d, im):
    d.rectangle([8, 6, 22, 22], fill=hx("a83024"))
    d.line([(9, 7), (9, 21)], fill=hx("d85a40"))
    d.rectangle([10, 11, 20, 17], fill=hx("d8c890"))
    d.line([(11, 14), (19, 14)], fill=hx("4a1410"))
    d.line([(19, 6), (25, 1)], fill=hx("9a9aa0"), width=2)
    d.arc([8, 1, 16, 10], 180, 360, fill=hx("2a2a2c"), width=2)


def _glow(im):
    halo = Image.new("RGBA", im.size)
    ImageDraw.Draw(halo).ellipse([6, 3, 26, 21], fill=hx("ffc860", 70))
    return Image.alpha_composite(halo, im)


def build_icons():
    save(_icon(lambda d, im: lantern(d, im)), "items", "lantern.png")
    save(_icon(kerosene), "items", "kerosene.png")
    save(_icon(lambda d, im: lantern(d, im, fuel=True)), "items", "lantern_filled.png")
    save(_glow(_icon(lambda d, im: lantern(d, im, fuel=True, lit=True))), "items", "lantern_lit.png")


def build():
    build_cellar()
    _patch("mansion_kitchen", _kitchen_box(), _kitchen_trapdoor, "mansion_kitchen_trapdoor")
    _patch("mansion_study", (330, 160, 432, 214), _study_hatch, "mansion_study_hatch")
    build_icons()
