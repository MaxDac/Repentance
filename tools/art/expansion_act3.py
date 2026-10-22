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
# the lying barrel of whiskey, in cellar (Room3D) world units: centre of its footprint on the floor (x, z), length,
# head and belly radii, the chocks' lift, and its axis heading at 45 degrees, from the tail at the back left to the
# head and spigot turned out to the room at the front right
BARREL = (318.0, 236.0, 44.0, 11.0, 13.0, 2.0, 45.0)
CELLAR_FIRE_FRAMES = 8


# ------------------------------------------------------------------------------------------------ CELLAR

def _storm_lantern(d, x, y, lit=False):
    """A tin hurricane lantern hanging by its wire bail from (x, y): vented cap, the two air tubes down its sides,
    a sooted glass globe in a wire guard with the burner and wick inside, and the fuel font with its filler cap and
    wick-raiser knob. Lit, a flame stands on the wick and the tin catches it; the lit lantern is painted after the
    room's grade (see paint_cellar), so these are its final colours."""
    if lit:
        tin, tin_l, tin_d, edge = hx("8a6a44"), hx("e0a860"), hx("4a3020"), hx("24160e")
        wire, brass, rust = hx("3a2618"), hx("f0c070"), hx("6a3a1c")
    else:
        tin, tin_l, tin_d, edge = hx("6a7468"), hx("a8b4a4"), hx("3a4038"), hx("1a1e1a")
        wire, brass, rust = hx("4a4a50"), hx("b08a40"), hx("6a3a24")
    # the wire bail, its loop round the hook, and the ears it pivots in on the cap
    d.arc([x - 8, y + 1, x + 8, y + 19], 200, 340, fill=wire)
    d.ellipse([x - 1, y - 1, x + 1, y + 2], outline=wire)
    for s in (-1, 1):
        d.point((x + s * 8, y + 9), fill=edge)
    # the cap: a stepped dome with a row of vent holes and a lip over the globe
    d.polygon([(x - 2, y + 4), (x + 2, y + 4), (x + 5, y + 7), (x - 5, y + 7)], fill=tin, outline=edge)
    d.line([(x - 1, y + 5), (x + 1, y + 5)], fill=tin_l)
    d.rectangle([x - 7, y + 8, x + 7, y + 10], fill=tin, outline=edge)
    d.line([(x - 6, y + 8), (x + 5, y + 8)], fill=tin_l)
    for vx in (x - 4, x - 1, x + 2, x + 5):
        d.point((vx, y + 6), fill=hx("ffe8a0") if lit else edge)
    # the globe, and what is inside it
    if lit:
        d.ellipse([x - 6, y + 11, x + 6, y + 25], fill=hx("a85a1c"), outline=edge)
        d.ellipse([x - 5, y + 12, x + 5, y + 24], fill=hx("d88a30"))
        d.ellipse([x - 3, y + 14, x + 3, y + 23], fill=hx("f0b050"))
        d.arc([x - 5, y + 11, x + 5, y + 17], 200, 340, fill=hx("5a2a10"))  # soot on the inside of the dome
        d.polygon([(x, y + 13), (x + 2, y + 18), (x + 1, y + 21), (x - 1, y + 21), (x - 2, y + 18)],
                  fill=hx("fff4c0"))  # the flame
        d.line([(x, y + 15), (x, y + 20)], fill=hx("ffffff"))
        d.point((x, y + 13), fill=hx("ff8a30"))
        d.point((x, y + 21), fill=hx("4a8ad8"))  # the blue root on the wick
    else:
        d.ellipse([x - 6, y + 11, x + 6, y + 25], fill=hx("6a7a7a"), outline=edge)
        d.ellipse([x - 4, y + 13, x + 4, y + 24], fill=hx("4e5c5e"))
        d.arc([x - 5, y + 11, x + 5, y + 17], 200, 340, fill=hx("2a2a28"))  # old soot
        d.line([(x, y + 20), (x, y + 21)], fill=hx("1a1a18"))  # the cold wick, charred at the tip
    d.line([(x - 3, y + 13), (x - 4, y + 18)], fill=hx("fff8e0") if lit else hx("d8e4e0"))  # the glass's gleam
    d.point((x + 3, y + 22), fill=hx("ffe8b0") if lit else hx("a8b8b4"))
    d.rectangle([x - 3, y + 22, x + 3, y + 24], fill=brass, outline=edge)  # the burner collar
    # the wire guard: two stays and a hoop round the globe's belly
    for gx in (x - 4, x + 4):
        d.line([(gx, y + 11), (gx, y + 25)], fill=edge)
    d.line([(x - 6, y + 18), (x + 6, y + 18)], fill=edge)
    # the air tubes, bent in from the cap and down into the font
    for s in (-1, 1):
        d.line([(x + s * 7, y + 10), (x + s * 9, y + 12), (x + s * 9, y + 25)], fill=tin_d, width=2)
    d.line([(x - 9, y + 13), (x - 9, y + 24)], fill=tin_l)
    # the fuel font: a rolled top, a seam, a dent of rust, the filler cap and the wick-raiser knob
    d.rectangle([x - 9, y + 25, x + 9, y + 33], fill=tin, outline=edge)
    d.line([(x - 8, y + 26), (x + 8, y + 26)], fill=tin_l)
    d.line([(x - 8, y + 30), (x + 8, y + 30)], fill=tin_d)
    d.line([(x - 8, y + 27), (x - 8, y + 32)], fill=tin_l)
    d.line([(x + 8, y + 27), (x + 8, y + 32)], fill=tin_d)
    d.point((x + 5, y + 32), fill=rust)
    d.point((x - 3, y + 31), fill=rust)
    d.rectangle([x + 4, y + 23, x + 6, y + 24], fill=brass, outline=edge)  # filler cap
    d.line([(x - 11, y + 27), (x - 10, y + 27)], fill=brass)  # wick-raiser knob
    d.point((x - 11, y + 26), fill=edge)


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


class _Barrel:
    """The barrel's geometry in the cellar's perspective: its frame, the bulge of the staves and the spigot."""

    def __init__(self, x, z, length, r_end, r_mid, lift, heading):
        a = math.radians(heading)
        self.R = Room3D(CFL, 240, 100)
        self.len, self.r_end, self.r_mid = length, r_end, r_mid
        self.A = np.array([math.cos(a), 0.0, math.sin(a)])  # along the axis, tail to head
        self.N = np.array([math.sin(a), 0.0, -math.cos(a)])  # level, across the axis
        self.UP = np.array([0.0, 1.0, 0.0])
        self.C = np.array([x, lift + r_mid, z])

    def proj(self, p):
        p = np.asarray(p, float)
        s = self.R.s(p[..., 2])
        return np.stack([self.R.vx + (p[..., 0] - self.R.vx) * s, self.R.vy + (self.R.floor - self.R.vy) * s
                         - p[..., 1] * s], -1)

    def radius(self, u):
        t = 2 * u / self.len
        return self.r_end + (self.r_mid - self.r_end) * (1 - t * t)

    def top(self, u):
        """Screen point on the crown of the staves at u along the axis."""
        return self.proj(self.C + self.A * u + self.UP * self.radius(u) * 0.97)

    def spigot(self):
        base = self.C + self.A * self.len / 2 - self.UP * self.r_end * 0.5
        return base, base + self.A * 4.5

    def floor_under(self, p):
        return self.proj(np.array([p[0], 0.0, p[2]]))

    def footprint(self, pad=2.0):
        return [self.floor_under(self.C + s1 * self.A * (self.len / 2 + pad) + s2 * self.N * (self.r_mid + pad))
                for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


GEO = _Barrel(*BARREL)
BARREL_FEET = int(round(max(p[1] for p in GEO.footprint(0)))) - 2  # the floor row at its front, its y-sort point
_t = GEO.floor_under(GEO.spigot()[1])
POOL = (int(round(_t[0])) + 8, int(round(_t[1])) + 2)  # centre of the whiskey pool, spreading out under the tap
LIGHT = np.array([-0.45, 0.75, 0.5]) / np.linalg.norm([-0.45, 0.75, 0.5])


def _zsplat(zbuf, col, pts, rgb, g):
    """Projects surface samples into the frame, keeping the nearest (largest z) sample at every pixel."""
    h, w = zbuf.shape
    xy = np.rint(g.proj(pts)).astype(int)
    z = pts[:, 2]
    ok = (xy[:, 0] >= 0) & (xy[:, 0] < w) & (xy[:, 1] >= 0) & (xy[:, 1] < h)
    xy, z, rgb = xy[ok], z[ok], rgb[ok]
    idx = xy[:, 1] * w + xy[:, 0]
    order = np.lexsort((z, idx))
    idx, z, rgb = idx[order], z[order], rgb[order]
    last = np.r_[idx[1:] != idx[:-1], True]
    idx, z, rgb = idx[last], z[last], rgb[last]
    zf, cf = zbuf.reshape(-1), col.reshape(-1, 3)
    near = z >= zf[idx]
    zf[idx[near]] = z[near]
    cf[idx[near]] = rgb[near]


def _lying_barrel(img, open=False, g=GEO):
    """An oak barrel on its side on two chocks, modelled in the cellar's own perspective with its axis at 45 degrees
    across the floor: bulging staves shaded round the belly, iron hoops, the bung on top, and the head (boards, the
    chime's shadow and a brass spigot) turned out to the room. Opened, the spigot is turned along the pipe and the old
    man's whiskey runs out of it in a thin amber rope."""
    w, h = img.size
    zbuf = np.full((h, w), -1e9)
    col = np.zeros((h, w, 3))
    oak_l, oak_d = np.array(hx("b07e4e"), float), np.array(hx("2e1c10"), float)
    iron, iron_l = np.array(hx("26262a"), float), np.array(hx("7a7a84"), float)
    tone = 1 + 0.07 * np.random.default_rng(7).standard_normal(20)
    # ---- the staves ----
    U, T = np.meshgrid(np.arange(-g.len / 2, g.len / 2 + 0.01, 0.2), np.arange(0, 2 * math.pi, 0.012))
    U, T = U.ravel(), T.ravel()
    nrm = np.cos(T)[:, None] * g.N + np.sin(T)[:, None] * g.UP
    pts = g.C + U[:, None] * g.A + g.radius(U)[:, None] * nrm
    lam = np.clip(nrm @ LIGHT, 0, 1)
    sv = T * 20 / (2 * math.pi)
    k = np.clip((0.18 + 0.95 * lam) * tone[sv.astype(int) % 20], 0, 1)
    rgb = oak_d + (oak_l - oak_d) * k[:, None]
    rgb[sv % 1 < 0.1] *= 0.55  # the joints between the staves
    au = np.abs(U)
    hoop = ((au > g.len / 2 - 3.6) & (au < g.len / 2 - 1.6)) | ((au > g.len / 2 - 10.5) & (au < g.len / 2 - 8.5))
    rgb[hoop] = (iron + (iron_l - iron) * (lam ** 3)[:, None])[hoop]
    rgb[(au < 1.4) & (np.abs(T - math.radians(100)) < 0.12)] = hx("2a180c")  # the bung
    _zsplat(zbuf, col, pts, rgb, g)
    # ---- the head, set a little inside the chime ----
    Rh, Th = np.meshgrid(np.arange(0, g.r_end, 0.15), np.arange(0, 2 * math.pi, 0.01))
    Rh, Th = Rh.ravel(), Th.ravel()
    lx, ly = Rh * np.cos(Th), Rh * np.sin(Th)
    pts = g.C + g.A * (g.len / 2 - 0.8) + lx[:, None] * g.N + ly[:, None] * g.UP
    kh = min(1.0, 0.43 + 0.95 * max(0.0, float(g.A @ LIGHT)))
    rgb = np.tile(np.array(mix(hx("2e1c10"), hx("9a6c40"), kh), float), (len(Rh), 1))
    rgb[np.abs((lx / g.r_end * 2.5) % 1 - 0.5) > 0.42] *= 0.55  # the boards of the head
    rgb[Rh > g.r_end - 1.6] *= 0.6  # the chime's shadow
    rgb *= (1 - 0.18 * ly / g.r_end)[:, None]
    _zsplat(zbuf, col, pts, rgb, g)
    # ---- its shadow, and the chocks under it ----
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in g.footprint()], fill=170)
    m = m.filter(ImageFilter.GaussianBlur(3))
    img.paste(Image.composite(ImageChops.multiply(img, Image.new("RGB", img.size, (0, 0, 0))), img, m))
    d = ImageDraw.Draw(img)
    faces = ((0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6))
    fcol = [hx(c) for c in ("4a3420", "6a4a2c", "5a4026", "3a2818", "5a4026", "7a5834")]
    for uc in (-g.len * 0.3, g.len * 0.3):
        pts = []
        for s1 in (-1, 1):
            for s2 in (-1, 1):
                q = g.C + g.A * (uc + 2.5 * s1) + g.N * (g.r_mid * 0.95 * s2)
                pts += [np.array([q[0], 0.0, q[2]]), np.array([q[0], 4.0, q[2]])]
        for fi in sorted(range(6), key=lambda i: np.mean([pts[j][2] for j in faces[i]])):
            d.polygon([tuple(g.proj(pts[j])) for j in faces[fi]], fill=fcol[fi], outline=hx("22160a"))
    arr = np.asarray(img).copy()
    hit = zbuf > -1e8
    arr[hit] = np.clip(col[hit], 0, 255).astype(np.uint8)
    img.paste(Image.fromarray(arr))
    # ---- the brass spigot ----
    d = ImageDraw.Draw(img)
    b0, t0 = g.spigot()
    pb, pt = g.proj(b0), g.proj(t0)
    d.line([tuple(pb), tuple(pt)], fill=hx("c89a40"), width=3)
    d.line([(pb[0], pb[1] - 1), (pt[0], pt[1] - 1)], fill=hx("f0d080"))
    d.ellipse([pb[0] - 2, pb[1] - 2, pb[0] + 2, pb[1] + 2], outline=hx("5a3a1a"))  # its flange on the head
    tap = g.proj(t0 - g.UP * 2.5)
    d.line([tuple(pt), tuple(tap)], fill=hx("806020"))
    if open:
        hp = g.proj(t0 + g.UP * 2 - g.A * 1.2)
        d.line([tuple(hp), (hp[0] + 2, hp[1])], fill=hx("d8b060"))  # the handle, turned along the pipe
        y0, y1 = int(tap[1]) + 1, int(g.floor_under(t0)[1])
        for y in range(y0, y1 + 1):  # the whiskey, falling and fanning out as it nears the flags
            f = (y - y0) / max(1, y1 - y0)
            x = tap[0] + 1.5 * f * f
            d.line([(x - 0.4 * f, y), (x + 0.5 + 0.8 * f, y)], fill=WHISKEY)
            if y % 3 == 0:
                d.point((int(x), y), fill=WHISKEY_L)
    else:
        d.point((tap[0], tap[1] + 2), fill=WHISKEY)  # a drip of the old man's whiskey


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
    along the top of the barrel and up its head, smoke rolling up into the vault. The flames are marked emissive in
    em."""
    tau = 2 * math.pi
    top = [GEO.top(u) for u in (-14, -4, 6, 15)]
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for i, (sx, sy) in enumerate(((cx - 10, cy - 50), (top[1][0], top[1][1] - 30))):
        _smoke(layer, sx, sy, 130, -40 + 30 * i, 12, (t + i * 0.5) % 1.0, 7, 1520 + i)
    layer.putalpha(layer.getchannel("A").point(lambda a: a * 3 // 5))
    fl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fl)
    d.ellipse([cx - 31, cy - 5, cx + 19, cy + 6], fill=hx("3a5ac8"))
    d.ellipse([cx - 26, cy - 3, cx + 14, cy + 3], fill=hx("7a9af0"))
    d.line([(cx - 55, cy + 4), (cx - 30, cy + 2)], fill=hx("4a6ad8"), width=2)
    d.polygon([(cx + 10, cy + 3), (cx + 24, cy + 12), (cx + 22, cy + 13), (cx + 6, cy + 5)], fill=hx("3a5ac8"))
    # along the crown of the staves the tongues stay low, so the barrel shows between them
    for (x, y), h, w, ph in zip(top, (16, 24, 20, 28), (3, 4, 3, 4), (0.71, 0.05, 0.53, 0.38)):
        _flame(d, x, y + 2, h, w, t, ph, lean=0.4 * math.sin(tau * (t + ph)))
    sp = GEO.proj(GEO.spigot()[1])
    _flame(d, sp[0] - 1, sp[1] + 3, 22, 4, t, 0.9, lean=0.3)  # up the head from the spigot
    tongues = ((-44, 4, 10, 2, 0.27), (-28, 1, 14, 3, 0.45), (-18, 2, 26, 4, 0.0), (-8, 3, 40, 6, 0.31),
               (2, 2, 48, 6, 0.62), (10, 3, 30, 5, 0.17), (17, 1, 16, 3, 0.83))  # (dx, dy, height, half-width, phase)
    for dx, dy, h, w, ph in tongues:
        _flame(d, cx + dx, cy + dy, h, w, t, ph, lean=0.4 * math.sin(tau * (t + ph)))
    for k in range(6):  # sparks spiralling up off the barrel
        q = (t * 2 + k / 6) % 1.0
        x = cx - 34 + k * 9 + 4 * math.sin(tau * (q + k * 0.21))
        d.point((x, cy - 20 - q * 80), fill=hx("ffc060") if q < 0.6 else hx("a85a2a"))
    em.paste(255, mask=fl.getchannel("A"))
    out = Image.alpha_composite(Image.alpha_composite(img.convert("RGBA"), layer), fl).convert("RGB")
    img.paste(out)


def _kitchen_stair(img, rnd):
    """The kitchen stair down from the trapdoor: a dark hollow under it with the cook's sacks, crocks and broom, a far
    stringer, nine treads on riser boards (worn pale where feet land, nailed at the ends, one split and patched), a
    near stringer bolted at each tread, and a handrail on square balusters ending in a newel post at the floor."""
    def near(y):  # the near stringer's top edge
        return 70 + (y - 22) * 92 / 182

    def rail(x):  # the handrail runs parallel to the stringer, a little over 30 px above it
        return 22 + (x - 72) * 182 / 92 - 32

    shadow(img, "polygon", [(22, 26), (114, 204), (0, 204), (0, 70)], 0.55, 6)
    d = ImageDraw.Draw(img)
    # stored under the stair: a corn broom against the wall, two burlap sacks, a pair of stoneware crocks
    d.line([(10, 118), (22, 196)], fill=hx("6a4a2a"), width=2)
    d.polygon([(18, 188), (27, 188), (31, 204), (14, 204)], fill=hx("b0904a"), outline=hx("5a4420"))
    for x in (19, 22, 25, 28):
        d.line([(x, 190), (x + (x - 22) // 3, 203)], fill=hx("806428"))
    d.rectangle([18, 189, 27, 190], fill=hx("6a2a1a"))
    for x0, top, col in ((30, 172, hx("8a7650")), (50, 180, hx("7a6646"))):
        d.polygon([(x0 + 3, top + 6), (x0 + 8, top), (x0 + 13, top), (x0 + 17, top + 6), (x0 + 21, 203),
                   (x0, 203)], fill=col, outline=hx("3a2e1a"))
        d.line([(x0 + 6, top + 6), (x0 + 15, top + 6)], fill=hx("4a3a20"))  # the tie
        for y in range(top + 10, 203, 4):  # coarse weave
            d.line([(x0 + 3, y), (x0 + 18, y + 1)], fill=mul(col, 0.86))
        d.line([(x0 + 4, top + 12), (x0 + 3, 200)], fill=mul(col, 1.15))
    for x0, h in ((74, 16), (86, 12)):
        d.rectangle([x0, 204 - h, x0 + 9, 203], fill=hx("b8a880"), outline=hx("4a4030"))
        d.rectangle([x0, 204 - h, x0 + 9, 204 - h + 3], fill=hx("6a4a2a"))  # the brown glazed shoulder
        d.line([(x0 + 2, 206 - h), (x0 + 2, 202)], fill=hx("e0d4b0"))
    # the far stringer
    d.polygon([(19, 22), (25, 22), (117, 204), (111, 204)], fill=hx("4a3420"))
    d.line([(25, 22), (117, 204)], fill=hx("6a4a2e"))
    for i in range(9):
        ty, tx0 = 34 + i * 19, 24 + i * 10
        tx1 = tx0 + 46
        if i:  # the riser board under the previous tread's nosing, two planks wide
            d.rectangle([tx0, ty - 11, tx1, ty - 1], fill=hx("7a5838"))
            d.line([(tx0, ty - 11), (tx1, ty - 11)], fill=hx("2a1c10"))
            d.line([(tx0, ty - 10), (tx1, ty - 10)], fill=hx("4a3420"))
            d.line([(tx0, ty - 6), (tx1, ty - 6)], fill=hx("5a4028"))
            d.line([(tx0, ty - 1), (tx1, ty - 1)], fill=hx("4a3420"))
            for gx in (tx0 + 9, tx0 + 23, tx0 + 37):
                d.line([(gx, ty - 9), (gx + rnd.choice((-1, 0, 1)), ty - 2)], fill=hx("6a4c30"))
        d.rectangle([tx0, ty, tx1, ty + 4], fill=hx("9a7648"))
        d.line([(tx0, ty), (tx1, ty)], fill=hx("d8b07a"))  # the rounded nosing catching the light
        d.line([(tx0 + 14, ty + 1), (tx0 + 32, ty + 1)], fill=hx("c09a66"))  # worn pale where feet land
        d.line([(tx0 + 18, ty + 2), (tx0 + 28, ty + 2)], fill=hx("b08a5a"))
        for _ in range(3):  # grain
            gx = rnd.randint(tx0 + 2, tx1 - 10)
            d.line([(gx, ty + 3), (gx + rnd.randint(4, 9), ty + 3)], fill=hx("6a4e30"))
        for nx in (tx0 + 2, tx1 - 2):
            d.point((nx, ty + 2), fill=hx("2a2420"))
        if i == 5:  # a split tread, patched with a cleat
            d.line([(tx0 + 30, ty + 1), (tx0 + 40, ty + 3)], fill=hx("2a1c10"))
            d.rectangle([tx0 + 34, ty + 5, tx0 + 41, ty + 6], fill=hx("6a5a40"))
        d.rectangle([tx0, ty + 5, tx1, ty + 7], fill=hx("2a1c10"))
    # the near stringer, its top edge lit, a bolt where each tread lands
    d.polygon([(67, 22), (73, 22), (165, 204), (159, 204)], fill=hx("5a4028"))
    d.line([(67, 22), (159, 204)], fill=hx("8a6a44"))
    d.line([(73, 22), (165, 204)], fill=hx("2a1c10"))
    for i in range(9):
        ty = 34 + i * 19
        bx = int(near(ty)) + 2
        d.point((bx, ty + 3), fill=hx("1a1614"))
        d.point((bx - 1, ty + 2), fill=hx("9a8a70"))
    # square balusters up from the stringer to the handrail, then the newel post at the foot
    for i in range(9):
        ty = 34 + i * 19
        bx = int(near(ty)) + 1
        top = int(rail(bx)) + 2
        d.rectangle([bx, top, bx + 1, ty], fill=hx("6a4a2e"))
        d.line([(bx, top), (bx, ty)], fill=hx("9a7448"))
        d.rectangle([bx - 1, top + 3, bx + 2, top + 4], fill=hx("4a3420"))
        d.rectangle([bx - 1, ty - 4, bx + 2, ty - 3], fill=hx("4a3420"))
    nx0, ntop = 159, 160
    d.rectangle([nx0, ntop, nx0 + 6, 204], fill=hx("5a4028"), outline=hx("2a1c10"))
    d.line([(nx0 + 1, ntop + 1), (nx0 + 1, 203)], fill=hx("8a6a44"))
    d.rectangle([nx0 - 1, ntop - 4, nx0 + 7, ntop], fill=hx("6a4a2e"), outline=hx("2a1c10"))  # its cap
    d.rectangle([nx0 + 2, ntop - 7, nx0 + 4, ntop - 4], fill=hx("6a4a2e"))  # a turned finial
    d.line([(72, int(rail(72))), (nx0 + 1, int(rail(nx0 + 1)))], fill=hx("5a3c24"), width=4)
    d.line([(72, int(rail(72)) - 1), (nx0, int(rail(nx0)) - 1)], fill=hx("b89060"))
    d.line([(72, int(rail(72)) + 2), (nx0, int(rail(nx0)) + 2)], fill=hx("2a1c10"))
    for k in range(3):  # a web strung between the top balusters
        d.line([(near(34) + 2, rail(near(34)) + 6 + k * 6), (near(53) + 2, rail(near(53)) + 10 + k * 5)],
               fill=hx("8a8478"))


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
    _kitchen_stair(img, rnd)
    d = ImageDraw.Draw(img)
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
        _lying_barrel(img, open=barrel_open)
    if pool:
        _whiskey_pool(img, *POOL)
    if fire:
        _cellar_fire(img, em, *POOL, fire_t)
    d = ImageDraw.Draw(img)
    hang = lit and not lantern_down
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
        if hang:  # the lantern hung at the stair foot, painted over its own light so the tin and flame stay crisp
            _storm_lantern(ImageDraw.Draw(img), nx, ny, lit=True)
    else:
        pools = [hatch, (hx0, hy0 + 18, 26, 30, (0.55, 0.55, 0.7), 0.8),
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
    cx, cy = POOL
    overlay(v["whiskey"], lit_px, pal, (cx - 60, cy - 8, cx + 30, cy + 16), "mansion_cellar_whiskey")
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
