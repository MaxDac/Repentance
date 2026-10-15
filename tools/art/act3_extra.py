"""Act 3 extras: the prison visiting room and the getaway car."""
import math
import random
from PIL import Image, ImageDraw
from .common import W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, palette_of, pixelize, save, text

H = FULL_H


# ------------------------------------------------------------------------------------------------ PRISON

SEAT_Y = 222  # the seated figures' soles (sprite bottom row)
MICAH_X, VISITOR_X = 196, 284  # the two sitters, mirror images about the table's centre column
TABLE = (204, 178, 277, 230)  # recomputed by build_prison from the painted table's bounding box


def _prison_room():
    from .furniture import Room3D
    return Room3D(186, 290, 96, 520)


SIT_Z = 140  # depth of the sitters and the table


def _wx(R, xs, z=SIT_Z):
    """World x of a screen column at depth z."""
    return R.vx + (xs - R.vx) / R.s(z)


WL, WR, CH, DADO = 60, 420, 160, 62  # side walls, ceiling and the tiled dado's height, in back-wall pixels


def _tiles(img, R, quad_fn, cols, rows, col, grout, rnd, wear=0.12):
    """Glazed wall tiles on a plane: quad_fn(u0, v0, u1, v1) gives the four world points of the cell."""
    d = ImageDraw.Draw(img)
    for i in range(len(cols) - 1):
        for j in range(len(rows) - 1):
            k = rnd.uniform(0.9, 1.06)
            c = mul(col, k)
            if rnd.random() < wear:
                c = mix(c, hx("b8b49c"), 0.35)  # a chipped, paler tile
            d.polygon([R.P(*p) for p in quad_fn(cols[i], rows[j], cols[i + 1], rows[j + 1])], fill=c, outline=grout)


def _crack(d, x, y, n, rnd, col, dx=1):
    """A hairline crack wandering down the plaster, the odd short branch splitting off."""
    for i in range(n):
        nx, ny = x + (dx if rnd.random() < 0.55 else 0), y + 1
        d.point((nx, ny), fill=col)
        if i > 3 and rnd.random() < 0.08:
            _crack(d, nx, ny, n // 3, rnd, col, -dx)
        x, y = nx, ny


def _guard():
    """The warder by the door: navy tunic buttoned to the throat, peaked cap, hands clasped behind his back."""
    from .figure import figure as fig, pose
    from .sprites import WATCHMAN
    spec = dict(WATCHMAN, h=WATCHMAN["h"] * 1.2 / 1.36, coat=dict(col="26304a", top=0.40, hem=0.6, flare=0.0),
                decals=[("buttons", 0.24, 0.44, 4, "b8a060"), ("belt", 0.43, "1a1a1e")])
    return fig(spec, pose(20, arms={1: ("swing", -8, 4, 16), -1: ("swing", -8, 4, 16)}), 48, 96)


def _wall_clock(img, d, cx, cy):
    """An institutional wall clock hung from the heating pipe: black bezel, cream dial, ten past two."""
    ink = hx("141414")
    d.rectangle([cx - 1, cy - 16, cx + 1, cy - 11], fill=hx("3a3a34"))  # the hanging bracket
    d.point((cx - 1, cy - 16), fill=hx("8a8a80"))
    d.rectangle([cx - 3, cy - 17, cx + 3, cy - 16], fill=hx("2a2a26"))
    shadow(img, "ellipse", [cx - 10, cy - 9, cx + 13, cy + 14], 0.35, 1)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=hx("1e1e1c"))
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=hx("34342e"))
    d.arc([cx - 11, cy - 11, cx + 11, cy + 11], 190, 290, fill=hx("8a8a80"))  # bezel highlight
    d.arc([cx - 11, cy - 11, cx + 11, cy + 11], 20, 110, fill=hx("101010"))
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=hx("ece6d4"))
    d.arc([cx - 9, cy - 9, cx + 9, cy + 9], 0, 140, fill=hx("c8c0a8"))  # the dial shaded under the rim
    d.arc([cx - 8, cy - 8, cx + 8, cy + 8], 10, 120, fill=hx("dcd4bc"))
    for i in range(12):
        a = i * math.pi / 6
        x, y = cx + 7 * math.sin(a), cy - 7 * math.cos(a)
        if i % 3 == 0:  # the quarter marks are bars pointing at the centre
            x2, y2 = cx + 5.5 * math.sin(a), cy - 5.5 * math.cos(a)
            d.line([(round(x), round(y)), (round(x2), round(y2))], fill=ink)
        else:
            d.point((round(x), round(y)), fill=hx("4a4a44"))
    d.line([(cx, cy), (cx + 3, cy - 1)], fill=ink, width=2)  # hour hand just past two
    d.line([(cx, cy), (cx + 2, cy - 6)], fill=ink)  # minute hand at ten past
    d.line([(cx, cy), (cx - 2, cy + 5)], fill=hx("a02820"))  # the red sweep hand
    d.point((cx, cy), fill=hx("b8a060"))
    d.point((cx - 5, cy - 5), fill=hx("ffffff"))  # a glint on the glass
    d.point((cx - 4, cy - 6), fill=hx("ffffff"))
    d.point((cx - 6, cy - 3), fill=hx("f8f4e8"))


def paint_prison():
    """Joliet, the visiting room: a long table under a hanging lamp, institutional
    green tiles and cracked cream plaster, a barred window high on the back wall, a riveted steel door and its warder."""
    R = _prison_room()
    FL = R.floor
    rnd = random.Random(1927)
    img = Image.new("RGB", (W, H), hx("2a2a26"))
    d = ImageDraw.Draw(img)
    Z = 400  # far enough towards the camera to run off screen

    # ---- ceiling: grimy whitewash between two iron beams ----
    R.quad(img, [(WL, CH, 0), (WR, CH, 0), (WR, CH, Z), (WL, CH, Z)], hx("8a8676"))
    vgrad(img, (0, 0, W - 1, 26), hx("4e4c44"), hx("7a786a"))
    for z in (60, 200):
        R.quad(img, [(WL, CH, z), (WR, CH, z), (WR, CH - 6, z), (WL, CH - 6, z)], hx("3a3a36"))
        R.quad(img, [(WL, CH - 6, z), (WR, CH - 6, z), (WR, CH - 6, z + 8), (WL, CH - 6, z + 8)], hx("2a2a28"))

    # ---- back wall: cream plaster above a dado of green glazed tiles ----
    plaster, plaster_d = hx("c4bc9a"), hx("a8a07e")
    vgrad(img, (WL, FL - CH, WR, FL - DADO), mul(plaster, 0.86), plaster)
    noise(img, (WL, FL - CH, WR, FL - DADO), 5, 11)
    # water stains creeping down from the ceiling and up from the dado
    for x, w_ in ((96, 40), (300, 56), (380, 30)):
        shadow(img, "ellipse", [x - w_ // 2, FL - CH - 14, x + w_ // 2, FL - CH + 22], 0.35, 6, (150, 130, 90))
    shadow(img, "ellipse", [228, FL - DADO - 18, 292, FL - DADO + 4], 0.25, 8, (120, 120, 90))
    tile, grout = hx("4e7a5e"), hx("2e4a3a")
    _tiles(img, R, lambda u0, v0, u1, v1: [(u0, v0, 0), (u1, v0, 0), (u1, v1, 0), (u0, v1, 0)],
           list(range(WL, WR + 1, 8)), [0, 6] + list(range(12, DADO + 1, 6)), tile, grout, rnd)
    # bull-nose capping and a dark skirting row
    R.quad(img, [(WL, DADO, 0), (WR, DADO, 0), (WR, DADO + 3, 0), (WL, DADO + 3, 0)], hx("2e5a40"))
    d.line([R.P(WL, DADO + 3, 0), R.P(WR, DADO + 3, 0)], fill=hx("8ab896"))
    R.quad(img, [(WL, 0, 0), (WR, 0, 0), (WR, 6, 0), (WL, 6, 0)], hx("24382c"))

    # ---- side walls, receding to the camera ----
    for x, k in ((WL, 0.78), (WR, 0.66)):
        R.quad(img, [(x, DADO, 0), (x, CH, 0), (x, CH, Z), (x, DADO, Z)], mul(plaster, k))
        _tiles(img, R, lambda u0, v0, u1, v1, x=x: [(x, v0, u0), (x, v0, u1), (x, v1, u1), (x, v1, u0)],
               list(range(0, Z, 10)), [0, 6] + list(range(12, DADO + 1, 6)), mul(tile, k + 0.1), mul(grout, k), rnd)
        R.quad(img, [(x, DADO, 0), (x, DADO + 3, 0), (x, DADO + 3, Z), (x, DADO, Z)], mul(hx("2e5a40"), k + 0.1))
        R.quad(img, [(x, 0, 0), (x, 6, 0), (x, 6, Z), (x, 0, Z)], mul(hx("24382c"), k))
        d.line([R.P(x, 0, 0), R.P(x, CH, 0)], fill=mul(plaster_d, 0.6))
    # a heating pipe along the top of the back wall, dropping down the right-hand corner
    pipe = hx("5a5a52")
    R.quad(img, [(WL, CH - 14, 1), (WR, CH - 14, 1), (WR, CH - 18, 1), (WL, CH - 18, 1)], pipe)
    d.line([R.P(WL, CH - 14, 1), R.P(WR, CH - 14, 1)], fill=hx("2a2a26"))
    d.line([R.P(WL, CH - 18, 1), R.P(WR, CH - 18, 1)], fill=hx("8a8a80"))
    for x in range(WL + 30, WR, 70):
        R.quad(img, [(x, CH - 12, 1), (x + 2, CH - 12, 1), (x + 2, CH - 20, 1), (x, CH - 20, 1)], hx("2a2a26"))
    R.quad(img, [(WR - 8, 0, 1), (WR - 4, 0, 1), (WR - 4, CH - 14, 1), (WR - 8, CH - 14, 1)], pipe)
    d.line([R.P(WR - 8, 0, 1), R.P(WR - 8, CH - 14, 1)], fill=hx("8a8a80"))

    # ---- floor: worn linoleum squares, scuffed paler where the chairs go ----
    for i, x in enumerate(range(WL, WR, 20)):
        for j, z in enumerate(range(0, Z, 20)):
            c = hx("6a5a40") if (i + j) % 2 else hx("4a4032")
            c = mul(c, rnd.uniform(0.93, 1.05))
            R.quad(img, [(x, 0, z), (x + 20, 0, z), (x + 20, 0, z + 20), (x, 0, z + 20)], c)
    noise(img, (0, FL, W - 1, H - 1), 6, 12)
    light(img, "ellipse", [150, 206, 330, 250], hx("8a8068"), 0.3, 12)
    for _ in range(26):  # scuffs and heel marks
        x, y = rnd.randint(70, 410), rnd.randint(FL + 4, H - 4)
        d.line([(x, y), (x + rnd.randint(2, 8), y + rnd.choice((0, 1)))], fill=hx("2e2a22"))
    # a floor drain
    dc = R.P(150, 0, 190)
    d.ellipse([dc[0] - 7, dc[1] - 2, dc[0] + 7, dc[1] + 2], fill=hx("2a2620"), outline=hx("1a1814"))
    for k in (-4, 0, 4):
        d.line([(dc[0] + k, dc[1] - 1), (dc[0] + k, dc[1] + 1)], fill=hx("4a463a"))

    # ---- the barred window, high on the back wall ----
    wx0, wx1, wy0, wy1 = 152, 222, 104, 140
    R.quad(img, [(wx0 - 4, wy0 - 5, 0), (wx1 + 4, wy0 - 5, 0), (wx1 + 4, wy1 + 4, 0), (wx0 - 4, wy1 + 4, 0)], hx("8a8468"))
    R.quad(img, [(wx0, wy0, 0), (wx1, wy0, 0), (wx1, wy1, 0), (wx0, wy1, 0)], hx("3a3a34"))  # the deep reveal
    R.quad(img, [(wx0 + 4, wy0 + 2, 0), (wx1 - 2, wy0 + 2, 0), (wx1 - 2, wy1 - 2, 0), (wx0 + 4, wy1 - 2, 0)], hx("c8d0d4"))
    vgrad(img, (wx0 + 4, FL - wy1 + 2, wx1 - 2, FL - wy0 - 2), hx("dfe6ea"), hx("a8b4bc"))
    for x in range(wx0 + 6, wx1 - 1, 12):  # wired glass panes
        d.line([(x, FL - wy1 + 2), (x, FL - wy0 - 2)], fill=hx("8a949a"))
    d.line([(wx0 + 4, FL - (wy0 + wy1) // 2), (wx1 - 2, FL - (wy0 + wy1) // 2)], fill=hx("8a949a"))
    for x in range(wx0 + 9, wx1 - 2, 8):  # iron bars in front
        d.line([(x, FL - wy1), (x, FL - wy0)], fill=hx("1e1e1c"), width=2)
        d.point((x, FL - wy1 + 1), fill=hx("6a6a64"))
    d.line([(wx0, FL - wy1 + 6), (wx1, FL - wy1 + 6)], fill=hx("1e1e1c"), width=2)
    d.line([(wx0, FL - wy0 - 6), (wx1, FL - wy0 - 6)], fill=hx("1e1e1c"), width=2)
    R.quad(img, [(wx0 - 6, wy0 - 5, 0), (wx1 + 6, wy0 - 5, 0), (wx1 + 6, wy0 - 3, 6), (wx0 - 6, wy0 - 3, 6)], hx("a49c80"))

    # ---- radiator under the window ----
    R.box(img, 160, 214, 2, 30, 2, 9, hx("6a6a60"), top=hx("8a8a7e"), side=hx("4a4a42"))
    for x in range(162, 214, 4):
        R.line(img, (x, 4, 9), (x, 28, 9), hx("44443c"))
    R.line(img, (212, 30, 5), (212, 104, 5), hx("5a5a52"), 2)

    # ---- painted enamel notice, clear of everything ----
    sx0, sy0 = 66, FL - 132
    d.rectangle([sx0, sy0, sx0 + 76, sy0 + 26], fill=hx("ece4cc"), outline=hx("2a2620"))
    d.rectangle([sx0 + 2, sy0 + 2, sx0 + 74, sy0 + 24], outline=hx("8a2420"))
    for cx, cy in ((sx0 + 1, sy0 + 1), (sx0 + 75, sy0 + 1), (sx0 + 1, sy0 + 25), (sx0 + 75, sy0 + 25)):
        d.point((cx, cy), fill=hx("4a4a44"))
    text(img, (sx0 + 38, sy0 + 8), "NO TOUCHING", hx("2a2420"))
    text(img, (sx0 + 38, sy0 + 17), "15 MINUTES", hx("8a2420"))
    shadow(img, "rect", [sx0 + 2, sy0 + 27, sx0 + 78, sy0 + 29], 0.4, 1)

    # ---- the steel door, riveted, with a judas slot, and the clock in its wire cage above ----
    dx0, dx1, dh = 334, 384, 98
    R.quad(img, [(dx0 - 5, 0, 0), (dx1 + 5, 0, 0), (dx1 + 5, dh + 5, 0), (dx0 - 5, dh + 5, 0)], hx("2a2c2a"))
    steel = hx("5e665e")
    R.quad(img, [(dx0, 0, 0), (dx1, 0, 0), (dx1, dh, 0), (dx0, dh, 0)], steel)
    hgrad(img, (dx0 + 1, FL - dh + 1, dx1 - 1, FL - 1), hx("6e766c"), hx("4a524a"))
    for y in (8, 46, 88):  # cross straps
        d.rectangle([dx0 + 1, FL - y - 5, dx1 - 1, FL - y], fill=hx("4e564e"))
        d.line([(dx0 + 1, FL - y - 5), (dx1 - 1, FL - y - 5)], fill=hx("889088"))
        for x in range(dx0 + 4, dx1 - 2, 6):
            d.point((x, FL - y - 3), fill=hx("a8b0a4"))
            d.point((x, FL - y - 2), fill=hx("262a26"))
    for x in (dx0 + 3, dx1 - 4):  # edge rivets
        for y in range(FL - dh + 4, FL - 3, 7):
            d.point((x, y), fill=hx("a8b0a4"))
            d.point((x, y + 1), fill=hx("262a26"))
    d.rectangle([dx0 + 17, FL - 78, dx1 - 17, FL - 70], fill=hx("161816"), outline=hx("889088"))  # judas slot
    d.rectangle([dx0 + 17, FL - 78, dx0 + 22, FL - 70], fill=hx("4e564e"))
    d.rectangle([dx1 - 12, FL - 52, dx1 - 4, FL - 36], fill=hx("3a3e3a"), outline=hx("1a1c1a"))  # lock box
    d.point((dx1 - 8, FL - 46), fill=hx("0a0a0a"))
    d.line([(dx1 - 10, FL - 40), (dx1 - 6, FL - 40)], fill=hx("b8b0a0"))
    for y in (FL - 84, FL - 22):  # strap hinges
        d.rectangle([dx0 - 4, y, dx0 + 12, y + 4], fill=hx("2e322e"))
        d.line([(dx0 - 4, y), (dx0 + 12, y)], fill=hx("7a827a"))
    text(img, ((dx0 + dx1) // 2, FL - dh - 12), "C-3", hx("e8e0c8"))
    _wall_clock(img, d, (dx0 + dx1) // 2, FL - dh - 34)

    # ---- the warder by the door ----
    g = _guard()
    gz = 14
    gx, gy = R.P(402, 0, gz)
    img.paste(g, (int(gx - g.width / 2), int(gy - (g.height - 3))), g)

    # ---- a bench along the left wall, a spittoon, a notice board ----
    R.box(img, WL, WL + 14, 14, 18, 30, 120, hx("6a4e34"), top=hx("8a6a48"), side=hx("4a3624"))
    for z in (34, 74, 116):
        R.box(img, WL + 2, WL + 4, 0, 14, z, z + 2, hx("3a2a1c"))
        R.box(img, WL + 10, WL + 12, 0, 14, z, z + 2, hx("3a2a1c"))
    sp = R.P(96, 0, 30)
    d.ellipse([sp[0] - 5, sp[1] - 9, sp[0] + 5, sp[1] + 1], fill=hx("8a7038"), outline=hx("4a3a1c"))
    d.ellipse([sp[0] - 4, sp[1] - 10, sp[0] + 4, sp[1] - 7], fill=hx("2a2010"), outline=hx("b89a58"))
    d.line([(sp[0] - 3, sp[1] - 5), (sp[0] - 3, sp[1] - 2)], fill=hx("c8aa68"))
    R.quad(img, [(WL, 92, 40), (WL, 126, 40), (WL, 126, 100), (WL, 92, 100)], hx("6a4a30"))
    R.quad(img, [(WL, 94, 42), (WL, 124, 42), (WL, 124, 98), (WL, 94, 98)], hx("9a7a58"))
    for z0, y0, c in ((46, 104, "e8e2d0"), (60, 110, "d8d0b8"), (76, 100, "ece6d6"), (84, 112, "c8c0a8")):
        R.quad(img, [(WL, y0, z0), (WL, y0 + 10, z0), (WL, y0 + 10, z0 + 10), (WL, y0, z0 + 10)], hx(c))

    # ---- cracks in the plaster ----
    for x, y, n in ((86, FL - CH + 4, 16), (300, FL - CH + 2, 22), (272, FL - DADO - 4, 10), (410, FL - 120, 14)):
        _crack(d, x, y, n, rnd, hx("7a7258"), dx=rnd.choice((-1, 1)))

    # ---- the two chairs, set either end of the table ----
    paint_chairs(img)

    # ---- the hanging lamp over the table and its warm cone; the window's cold shaft ----
    lc = R.P(_wx(R, 240), 112, SIT_Z)
    top = R.P(_wx(R, 240), CH, SIT_Z)
    d.line([(lc[0], top[1]), (lc[0], lc[1] - 6)], fill=hx("1e1e1a"))
    d.polygon([(lc[0] - 3, lc[1] - 7), (lc[0] + 3, lc[1] - 7), (lc[0] + 15, lc[1]), (lc[0] - 15, lc[1])], fill=hx("2e4a3a"))
    d.line([(lc[0] - 2, lc[1] - 6), (lc[0] - 12, lc[1] - 1)], fill=hx("5a7a66"))
    d.rectangle([lc[0] - 2, lc[1] - 9, lc[0] + 2, lc[1] - 7], fill=hx("6a6a60"))
    d.ellipse([lc[0] - 14, lc[1] - 1, lc[0] + 14, lc[1] + 2], fill=hx("fff4d8"))
    d.ellipse([lc[0] - 3, lc[1], lc[0] + 3, lc[1] + 3], fill=hx("ffffff"))
    light(img, "polygon", [(lc[0] - 12, lc[1] + 1), (lc[0] + 12, lc[1] + 1), (lc[0] + 66, 232), (lc[0] - 66, 232)],
          hx("f0d8a0"), 0.32, 10)
    light(img, "ellipse", [lc[0] - 70, 196, lc[0] + 70, 236], hx("f0d8a0"), 0.28, 10)
    light(img, "ellipse", [lc[0] - 22, lc[1] - 16, lc[0] + 22, lc[1] + 10], hx("fff0c0"), 0.45, 6)
    light(img, "polygon", [(wx0 + 4, FL - wy1), (wx1 - 2, FL - wy1), (wx1 + 80, 252), (wx0 + 40, 252)],
          hx("c8d8e4"), 0.18, 10)
    light(img, "polygon", [(wx0 + 50, 238), (wx1 + 60, 238), (wx1 + 78, 252), (wx0 + 60, 252)], hx("dce4ea"), 0.22, 4)
    for _ in range(40):  # dust in the light
        t = rnd.random()
        x = wx0 + 10 + t * 110 + rnd.uniform(-20, 20)
        y = FL - wy1 + t * 140
        if 0 <= x < W and 0 <= y < H:
            img.putpixel((int(x), int(y)), mix(img.getpixel((int(x), int(y))), hx("f0f0e8"), 0.4))
    vignette(img, 0.6, (14, 18, 16), 44)
    return img


def paint_chairs(img):
    """Plain ladder-back institutional chairs side-on: the backs behind the sitters, the seats under them."""
    R = _prison_room()
    wood, wood_d, wood_l = hx("5a3e26"), hx("38261a"), hx("7e5a3a")
    z0, z1, seat, back_h = SIT_Z - 9, SIT_Z + 9, 13.0, 42
    for x, sgn in ((MICAH_X, 1), (VISITOR_X, -1)):
        xb, xf = _wx(R, x - sgn * 8), _wx(R, x + sgn * 13)
        lo, hi = sorted((xb, xf))
        shadow(img, "polygon", [R.P(lo - 2, 0, z0 - 2), R.P(hi + 2, 0, z0 - 2), R.P(hi + 2, 0, z1 + 2),
                                R.P(lo - 2, 0, z1 + 2)], 0.5, 2)
        for z in (z0, z1 - 1.2):  # legs, the back ones running up into the back posts
            R.box(img, xf - 0.6, xf + 0.6, 0, seat, z, z + 1.2, wood_d if z == z0 else wood, top=wood, side=wood_d)
            R.box(img, xb - 0.6, xb + 0.6, 0, back_h, z, z + 1.2, wood_d if z == z0 else wood, top=wood_l,
                  side=wood_d)
        R.box(img, lo, hi, 6, 7, z0 + 0.6, z1 - 0.6, wood_d, top=wood_d)  # stretcher
        R.box(img, lo - 0.5, hi + 0.5, seat - 1.5, seat, z0 - 0.5, z1 + 0.5, wood, top=wood_l, side=wood_d)
        for y in (24, 31, back_h - 4):  # rails of the ladder back
            R.box(img, xb - 0.5, xb + 0.5, y, y + 2.5, z0, z1, wood, top=wood_l, side=wood_d)


def paint_table():
    """Foreground: the visiting-room table in perspective, drawn over the sitters' knees.
    Returns the RGBA layer cropped to its box and that box's top-left corner."""
    R = _prison_room()
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    z0, z1, top = SIT_Z - 12, SIT_Z + 18, 19.5
    x0, x1 = _wx(R, MICAH_X + 12), _wx(R, VISITOR_X - 12)
    wood, wood_d, wood_l = hx("6e4e30", 255), hx("3a2616", 255), hx("8e6a44", 255)
    # legs (the back pair first), then the apron and the top
    for x, z in ((x0 + 2, z0 + 2), (x1 - 4, z0 + 2), (x0 + 2, z1 - 4), (x1 - 4, z1 - 4)):
        c = wood_d if z == z0 + 2 else hx("4e3420", 255)
        R.quad(img, [(x, 0, z + 2), (x + 2.5, 0, z + 2), (x + 2.5, top - 3, z + 2), (x, top - 3, z + 2)], c)
    R.quad(img, [(x0, top - 4, z1), (x1, top - 4, z1), (x1, top - 1, z1), (x0, top - 1, z1)], hx("4e3420", 255))
    R.quad(img, [(x0 - 1, top - 1, z0 - 1), (x1 + 1, top - 1, z0 - 1), (x1 + 1, top - 1, z1 + 1),
                 (x0 - 1, top - 1, z1 + 1)], wood_d)
    R.quad(img, [(x0 - 1, top, z0 - 1), (x1 + 1, top, z0 - 1), (x1 + 1, top, z1 + 1), (x0 - 1, top, z1 + 1)], wood)
    # worn grain on the top, lighter where elbows have polished it
    for z in range(z0 + 3, z1, 5):
        d.line([R.P(x0 + 1, top, z), R.P(x1 - 1, top, z)], fill=hx("624428", 255))
    d.line([R.P(x0 - 1, top, z1 + 1), R.P(x1 + 1, top, z1 + 1)], fill=wood_l)
    for x in (x0 + 8, x1 - 8):
        p = R.P(x, top, (z0 + z1) / 2)
        d.ellipse([p[0] - 5, p[1] - 1, p[0] + 5, p[1] + 1], fill=hx("86603c", 255))
    box = img.getbbox()
    return img.crop(box), box[:2]


def build_prison():
    global TABLE
    t, (tx, ty) = paint_table()
    TABLE = (tx, ty, tx + t.width - 1, ty + t.height - 1)
    base = paint_prison()
    save(pixelize(base, n=120), "rooms", "prison.png")
    pal = palette_of(t.convert("RGB"), 24)
    a = t.getchannel("A")
    t = pixelize(t.convert("RGB"), pal, spread=6).convert("RGBA")
    t.putalpha(a)
    save(t, "rooms", "prison_table.png")
    print("prison_table at", TABLE[:2])


# ------------------------------------------------------------------------------------------------ THE CAR

CAR_W, CAR_H = 168, 74


def paint_car():
    """A black 1927 Packard-style sedan in profile, nose to the left, under an overcast moon.

    Drawn four times oversize and filtered down so the curves of the fenders and roof stay clean. RGBA; the tyres
    rest on row CAR_H - 3, the last rows hold a soft contact shadow."""
    import math
    k = 4
    w, h = CAR_W, CAR_H
    big = Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)

    def P(pts):
        return [(x * k, y * k) for x, y in pts]

    def E(cx, cy, rx, ry, **kw):
        d.ellipse([(cx - rx) * k, (cy - ry) * k, (cx + rx) * k, (cy + ry) * k], **kw)

    def L(pts, col, wd=1.0):
        d.line(P(pts), fill=col, width=max(1, int(wd * k)), joint="curve")

    def arc(cx, cy, r, a0, a1, n=24):
        return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
                 cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

    black, body, body_l, body_h = hx("101216", 255), hx("1c2026", 255), hx("343a44", 255), hx("6a7482", 255)
    under = hx("08090b", 255)
    chrome, chrome_d, chrome_h = hx("9aa0a6", 255), hx("50565c", 255), hx("e4e8ea", 255)
    glass, glass_l = hx("2a3644", 255), hx("5a6c7e", 255)
    tyre, white = hx("16161a", 255), hx("c8c8c0", 255)
    ground = 71
    fw, rw, r = 32, 128, 13.5  # wheel centres and radius
    wy = ground - r

    # contact shadow
    d.ellipse([6 * k, (ground - 2) * k, 162 * k, (ground + 2.6) * k], fill=(0, 0, 0, 110))

    # chassis shadow between the wheels, frame rail, spare tyre on the trunk rack
    d.rectangle([20 * k, 50 * k, 150 * k, 58 * k], fill=under)
    E(158, 42, 6.5, 14, fill=tyre)
    E(158, 42, 4.5, 11, fill=white)
    E(158, 42, 3.4, 9, fill=hx("3a3a3a", 255))
    E(158.6, 42, 1.4, 3, fill=chrome)

    # wheels: black tyre, whitewall, wire spokes, chrome hub
    for cx in (fw, rw):
        E(cx, wy, r, r, fill=tyre)
        E(cx, wy, r - 2.2, r - 2.2, fill=white)
        E(cx, wy, r - 3.6, r - 3.6, fill=hx("26282c", 255))
        E(cx, wy, r - 4.6, r - 4.6, fill=hx("1a1c20", 255))
        for i in range(16):
            a = math.radians(i * 22.5 + 6)
            L([(cx + 2.4 * math.cos(a), wy + 2.4 * math.sin(a)),
               (cx + (r - 4.6) * math.cos(a + 0.35), wy + (r - 4.6) * math.sin(a + 0.35))], hx("8a8e92", 255), 0.4)
        E(cx, wy, 3.2, 3.2, fill=chrome_d)
        E(cx, wy, 2.4, 2.4, fill=chrome)
        E(cx - 0.6, wy - 0.7, 0.9, 0.9, fill=chrome_h)
        L(arc(cx, wy, r - 0.6, 200, 290, 10), hx("3a3c40", 255), 0.6)  # moonlight on the tread

    # lower body: cowl, doors, rear quarter, with the belt line around y 31
    body_pts = [(17, 27), (64, 25), (68, 24), (150, 24), (156, 28), (158, 36), (157, 48), (150, 51), (20, 51), (16, 46)]
    d.polygon(P(body_pts), fill=body)
    # the cabin: upright windscreen, long flat roof rounding into the back
    roof = [(64, 25), (66, 6), (70, 3.2), (138, 3.2)] + arc(138, 17, 14, -90, 0, 12)[1:] + [(152, 26)]
    d.polygon(P(roof), fill=body)
    # windows with chrome reveals
    wins = [[(70, 8), (98, 8), (98, 23), (69, 23)], [(102, 8), (126, 8), (126, 23), (102, 23)],
            [(130, 8), (138, 8)] + arc(138, 17, 9, -90, -10, 6)[1:] + [(147, 23), (130, 23)]]
    for wp in wins:
        d.polygon(P(wp), fill=chrome_d)
        cx0 = sum(x for x, _ in wp) / len(wp)
        inner = [(x + (1 if x < cx0 else -1), y + (1 if y < 15 else -1)) for x, y in wp]
        d.polygon(P(inner), fill=glass)
        xs = [x for x, _ in inner]
        L([(min(xs) + 2, 21), (min(xs) + 9, 10)], glass_l, 1.2)  # a pale streak of sky in the glass
    E(66.6, 14, 1.1, 9, fill=chrome_d)  # windscreen pillar
    L([(66, 6), (70, 3.2), (138, 3.2)], body_h, 0.9)  # moonlit roof edge
    L(arc(138, 17, 14, -90, -20, 8), body_l, 0.9)
    # chrome belt moulding and door shut lines, handles, hinges
    L([(17, 27), (64, 25.4), (152, 25.4)], chrome, 0.8)
    L([(18, 31), (156, 31)], body_l, 0.6)
    for x in (68.5, 100, 128.5):
        L([(x, 24), (x, 50)], black, 0.6)
    for x in (95, 103.5):
        L([(x, 29.5), (x + 3, 29.5)], chrome_h, 0.9)
    for x, y in ((70, 34), (70, 45), (101.5, 34), (101.5, 45)):
        E(x, y, 0.8, 1.2, fill=chrome_d)
    L([(20, 49.5), (150, 49.5)], under, 1.4)  # ambient occlusion under the sills

    # the long hood with its louvres, cowl lamps, radiator shell and ornament
    d.polygon(P([(14, 21), (64, 22.5), (64, 34), (14, 36)]), fill=body)
    L([(14, 21.3), (64, 22.6)], body_h, 0.9)
    L([(18, 26.5), (64, 26.5)], body_l, 0.5)  # hood hinge line
    for x in range(36, 60, 3):
        L([(x, 28.5), (x + 0.8, 33.5)], black, 0.8)
        L([(x + 1, 28.5), (x + 1.8, 33.5)], body_l, 0.4)
    E(63, 21, 1.6, 1.4, fill=chrome)  # cowl lamp
    d.polygon(P([(7, 18), (15, 19), (15.5, 45), (6.5, 45)]), fill=chrome_d)  # radiator shell
    d.polygon(P([(8.4, 19.6), (14, 20.4), (14.3, 43.6), (8, 43.6)]), fill=hx("2a2c30", 255))
    for x in (9.4, 10.6, 11.8, 13.0):
        L([(x, 20.6), (x, 43)], hx("6a6e72", 255), 0.4)
    L([(7, 18.2), (7, 45)], chrome_h, 0.8)
    L([(7.2, 18), (15, 19)], chrome_h, 0.8)
    E(11, 16.6, 2.4, 1.6, fill=chrome)  # radiator cap
    d.polygon(P([(10, 15.4), (12.5, 9.5), (16.5, 10.5), (13, 12.5), (12.5, 15.4)]), fill=chrome)  # winged mascot
    L([(12.5, 9.5), (16.5, 10.5)], chrome_h, 0.5)

    # fenders: sweeping arches over the wheels running into a ribbed running board
    front = arc(fw, wy + 1, r + 4.2, 185, 330, 20) + [(56, 53), (56, 55.5)] + arc(fw, wy + 1, r + 2.0, 330, 185, 20)
    d.polygon(P(front), fill=body)
    L(arc(fw, wy + 1, r + 4, 195, 300, 14), body_h, 0.8)
    rear = [(112, 55.5), (112, 53)] + arc(rw, wy + 1, r + 4.2, 210, 355, 20) + [(146, 53)] + \
        arc(rw, wy + 1, r + 2.0, 355, 210, 20)
    d.polygon(P(rear), fill=body)
    L(arc(rw, wy + 1, r + 4, 225, 320, 12), body_h, 0.8)
    d.polygon(P([(52, 53), (116, 53), (116, 56), (52, 56)]), fill=hx("1a1a1c", 255))
    L([(52, 53.2), (116, 53.2)], chrome, 0.6)
    for x in range(56, 114, 4):
        L([(x, 54.2), (x + 2, 54.2)], hx("4a4c50", 255), 0.4)

    # headlamps on their bar, bumpers, tail lamp
    L([(2, 33), (20, 33)], chrome_d, 1.2)
    E(4.5, 30, 4.6, 5.2, fill=chrome)
    E(4.0, 30, 3.4, 4.0, fill=hx("d8d0a0", 255))
    E(3.0, 28.6, 1.3, 1.5, fill=hx("fffbe0", 255))
    L([(0.5, 46), (14, 46)], chrome, 1.4)
    L([(0.5, 45.4), (14, 45.4)], chrome_h, 0.5)
    L([(152, 51), (166, 51)], chrome, 1.4)
    E(155, 34, 1.4, 2, fill=hx("8a1c14", 255))
    E(154.6, 33.4, 0.5, 0.7, fill=hx("e05a40", 255))

    img = big.resize((w, h), Image.LANCZOS)
    px = img.load()
    for y in range(h):
        for x in range(w):
            r_, g_, b_, a_ = px[x, y]
            if y < ground - 2:
                px[x, y] = (r_, g_, b_, 255 if a_ >= 110 else 0)
    return img


def build_car():
    save(paint_car(), "sprites", "car.png")
