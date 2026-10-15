"""Present day: the dusty attic of an old family house, lit by a round gable window."""
from PIL import Image, ImageDraw, ImageChops, ImageFilter
import math
import random
from .common import (W, FULL_H, hx, mix, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of, text, save,
                     floor_boards)

H = FULL_H
VP = (260, 95)  # vanishing point; the attic recedes towards the gable wall
BACK = dict(x0=110, x1=410, eave=130, floor=178, apex=(260, 26))
WOOD, WOOD_D, WOOD_L = hx("6a5440"), hx("3a2c20"), hx("8a7258")
DUST = hx("f0d8a0")

# crops for the flag-driven overlays (x0, y0, x1, y1)
SPILL_BOX = (262, 184, 390, 222)
SHEET_BOX = (104, 112, 210, 199)
TRUNK_BOX = (388, 150, 476, 236)
# the suitcase lying on the floor between the radio and the hatch: front face corners, depth and lid height
SUITCASE = dict(x0=80, x1=114, top=222, bottom=232, depth=0.93, lid=26)
SUITCASE_BOX = (70, 186, 134, 240)

ACTS = {
    1: dict(
        window_top=hx("e8f0f8"),
        window_bottom=hx("b8d0e0"),
        foliage=(hx("c86a2a"), hx("d8902a"), hx("a8501e")),
        glint=hx("ffffff"),
        shaft_beam=hx("ffe0a0"),
        shaft_beam_k=0.07,
        shaft_floor=hx("ffd890"),
        shaft_floor_k=0.09,
        shaft_halo=hx("fff0d0"),
        shaft_halo_k=0.08,
        dust=DUST,
        dust_ratio=0.7,
        dust_count=70,
        desat=0.0,
        room_tint=None,
        storm_shadows=(),
        vignette_k=0.5,
        vignette_tint=(40, 30, 30),
        vignette_blur=40,
    ),
    2: dict(
        window_top=hx("d8e1e8"),
        window_bottom=hx("a5b0bc"),
        foliage=(hx("96725a"), hx("aa8464"), hx("6f594c")),
        glint=hx("d8e2ec"),
        shaft_beam=hx("d8e6ef"),
        shaft_beam_k=0.05,
        shaft_floor=hx("c7d1de"),
        shaft_floor_k=0.06,
        shaft_halo=hx("eef2f5"),
        shaft_halo_k=0.04,
        dust=hx("d8d8d0"),
        dust_ratio=0.55,
        dust_count=48,
        desat=0.18,
        room_tint=hx("88909a"),
        storm_shadows=(
            ("ellipse", [130, 122, 354, 274], 0.12, 12, hx("5a6270")),
        ),
        vignette_k=0.58,
        vignette_tint=(34, 36, 46),
        vignette_blur=42,
    ),
    3: dict(
        window_top=hx("7c8798"),
        window_bottom=hx("4e586c"),
        foliage=(hx("495160"), hx("5f6672"), hx("39404e")),
        glint=hx("bcc8da"),
        shaft_beam=hx("aebfd8"),
        shaft_beam_k=0.03,
        shaft_floor=hx("8fa2be"),
        shaft_floor_k=0.04,
        shaft_halo=hx("d7deee"),
        shaft_halo_k=0.03,
        dust=hx("c8ccd6"),
        dust_ratio=0.45,
        dust_count=36,
        desat=0.28,
        room_tint=hx("66718a"),
        storm_shadows=(
            ("polygon", [(0, 92), (140, 88), (220, 180), (0, 270)], 0.22, 16, hx("344055")),
            ("polygon", [(296, 98), (480, 84), (480, 270), (360, 270), (272, 176)], 0.18, 18, hx("2c3446")),
            ("ellipse", [120, 112, 360, 274], 0.18, 14, hx("4a556c")),
        ),
        vignette_k=0.72,
        vignette_tint=(18, 24, 44),
        vignette_blur=46,
    ),
}


def along(p, t):
    """Point at depth t on the line from the vanishing point through p (t=1 is the back wall)."""
    return (VP[0] + (p[0] - VP[0]) * t, VP[1] + (p[1] - VP[1]) * t)


def shell(img):
    d = ImageDraw.Draw(img)
    b = BACK
    # roof slopes: plank sheathing between the rafters
    left = [(b["x0"], b["eave"]), b["apex"], (b["apex"][0], 0), (0, 0), along((b["x0"], b["eave"]), 1.75)]
    right = [(b["x1"], b["eave"]), b["apex"], (b["apex"][0], 0), (W, 0), along((b["x1"], b["eave"]), 1.47)]
    d.polygon(left, fill=hx("4a3c30"))
    d.polygon(right, fill=hx("3e3228"))
    rnd = random.Random(4)
    for t in [1 + i * 0.07 for i in range(40)]:
        for side, col in ((b["x0"], hx("3a2e24")), (b["x1"], hx("30261e"))):
            e, r = along((side, b["eave"]), t), along(b["apex"], t)
            d.line([e, r], fill=mix(col, hx("5a4a3a"), rnd.random() * 0.5))
    # knee walls and back gable wall (vertical boards)
    d.polygon([along((b["x0"], b["eave"]), 1.75), (b["x0"], b["eave"]), (b["x0"], b["floor"]),
               along((b["x0"], b["floor"]), 1.75)], fill=hx("5a4a3a"))
    d.polygon([(b["x1"], b["eave"]), along((b["x1"], b["eave"]), 1.47), along((b["x1"], b["floor"]), 1.47),
               (b["x1"], b["floor"])], fill=hx("4e4034"))
    gable = [(b["x0"], b["floor"]), (b["x0"], b["eave"]), b["apex"], (b["x1"], b["eave"]), (b["x1"], b["floor"])]
    d.polygon(gable, fill=hx("6e5c48"))
    for x in range(b["x0"], b["x1"], 9):
        top = b["eave"] - (b["eave"] - b["apex"][1]) * (1 - abs(x - b["apex"][0]) / (b["apex"][0] - b["x0"]))
        d.line([(x, max(top, b["apex"][1]) + 2), (x, b["floor"])], fill=hx("54463a"))
        d.line([(x + 1, max(top, b["apex"][1]) + 2), (x + 1, b["floor"])], fill=hx("7a6852"))
    noise(img, (0, 0, W - 1, b["floor"] + 60), 5, 41)
    # rafters, nearer ones thicker
    for t in (1.0, 1.32, 1.7, 2.2, 2.9, 3.9):
        w = max(2, int(3 * t))
        for side in (b["x0"], b["x1"]):
            e, r = along((side, b["eave"]), t), along(b["apex"], t)
            d.line([e, r], fill=WOOD_D, width=w + 2)
            d.line([e, r], fill=WOOD, width=w)
            d.line([(e[0], e[1] - w // 2), (r[0], r[1] - w // 2)], fill=WOOD_L)
    # ridge beam and collar tie
    d.line([b["apex"], (b["apex"][0], 0)], fill=WOOD_D, width=8)
    d.line([(b["apex"][0] - 2, b["apex"][1]), (b["apex"][0] - 2, 0)], fill=WOOD_L)
    ct = (VP[1] - 46)
    d.line([along((150, ct + 32), 1.0), along((370, ct + 32), 1.0)], fill=WOOD_D, width=5)
    d.line([along((150, ct + 31), 1.0), along((370, ct + 31), 1.0)], fill=WOOD)
    # cobwebs in the corners
    for (cx, cy, sx) in ((b["x0"] + 2, b["eave"] + 2, 1), (b["x1"] - 2, b["eave"] + 2, -1)):
        for k in range(5):
            d.line([(cx, cy), (cx + sx * (6 + k * 4), cy + 18 - k * 4)], fill=hx("9a9080"))
        for r in (6, 11, 16):
            d.arc([cx - r, cy - r, cx + r, cy + r], 0 if sx > 0 else 90, 90 if sx > 0 else 180, fill=hx("8a8070"))


def floor(img):
    b = BACK
    tmp = Image.new("RGB", (W, H))
    floor_boards(tmp, b["floor"], H - 1, (VP[0], VP[1] - 340), 22, hx("6a5038"), hx("54402c"), hx("2a1e14"), 7)
    noise(tmp, (0, b["floor"], W - 1, H - 1), 6, 43)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([(b["x0"], b["floor"]), (b["x1"], b["floor"]), along((b["x1"], b["floor"]), 1.47),
                               (W, H), (0, H), along((b["x0"], b["floor"]), 1.75)], fill=255)
    img.paste(tmp, (0, 0), m)
    d = ImageDraw.Draw(img)
    d.line([(b["x0"], b["floor"]), (b["x1"], b["floor"])], fill=hx("2a1e14"))
    d.line([(b["x0"], b["floor"]), along((b["x0"], b["floor"]), 1.75)], fill=hx("2a1e14"))
    d.line([(b["x1"], b["floor"]), along((b["x1"], b["floor"]), 1.47)], fill=hx("2a1e14"))
    # an old rag rug
    rug = [(150, 214), (250, 214), (262, 246), (128, 246)]
    d.polygon(rug, fill=hx("5a4a5a"))
    for i, y in enumerate(range(217, 244, 4)):
        d.line([(146 - i, y), (254 + i * 1.3, y)], fill=[hx("7a5a4a"), hx("4a5a6a"), hx("8a7a50")][i % 3], width=2)
    noise(img, (128, 214, 262, 246), 6, 47)


def window(img, act=1):
    mood = ACTS[act]
    d = ImageDraw.Draw(img)
    cx, cy, r = 260, 80, 19
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=WOOD_D)
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], fill=hx("8a7a64"))
    glass = Image.new("RGB", img.size)
    vgrad(glass, (cx - r, cy - r, cx + r, cy + r), mood["window_top"], mood["window_bottom"])
    gd = ImageDraw.Draw(glass)
    # the neighbour's maple outside, in autumn
    for (lx, ly, lr, col) in ((cx - 12, cy + 6, 9, mood["foliage"][0]), (cx + 8, cy + 10, 11, mood["foliage"][1]),
                              (cx - 2, cy + 16, 8, mood["foliage"][2])):
        gd.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=col)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(glass, (0, 0), m)
    # mullions
    d.line([(cx - r, cy), (cx + r, cy)], fill=WOOD_D, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=WOOD_D, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=WOOD_D, width=2)
    d.line([(cx - 10, cy - 12), (cx - 4, cy - 15)], fill=mood["glint"])


def shaft(img, act=1, seed=5):
    """Afternoon sunlight pouring through the round window, full of dust motes."""
    mood = ACTS[act]
    pts = [(246, 72), (276, 72), (322, 266), (178, 266)]
    light(img, "polygon", pts, mood["shaft_beam"], mood["shaft_beam_k"], 6)
    light(img, "ellipse", [196, 220, 322, 270], mood["shaft_floor"], mood["shaft_floor_k"], 10)
    light(img, "ellipse", [200, 40, 320, 120], mood["shaft_halo"], mood["shaft_halo_k"], 18)
    for shape, pts, k, blur, tint in mood["storm_shadows"]:
        shadow(img, shape, pts, k, blur, tint=tint)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(mood["dust_count"]):
        y = rnd.uniform(80, 250)
        t = (y - 72) / 194
        x0, x1 = 246 + (178 - 246) * t, 276 + (322 - 276) * t
        x = rnd.uniform(x0 + 3, x1 - 3)
        d.point((x, y), fill=mood["dust"] if rnd.random() < mood["dust_ratio"] else hx("ffffff"))


def hatch(img):
    d = ImageDraw.Draw(img)
    # opening in the floor with the folding ladder, warm light from the landing below
    d.polygon([(18, 236), (92, 236), (98, 266), (10, 266)], fill=hx("2a1e14"))
    d.polygon([(22, 239), (88, 239), (93, 264), (15, 264)], fill=hx("c89a60"))
    light(img, "polygon", [(22, 239), (88, 239), (93, 264), (15, 264)], hx("fff0c0"), 0.4, 3)
    vgrad(img, (24, 240, 86, 252), hx("806040"), hx("e0b878"))
    # the folding ladder: its rails rise a little above the hole and curl over into hand grips
    top = 224
    for y in (232, 244, 256):
        d.line([(34, y + 1), (74, y + 1)], fill=WOOD_D, width=3)
        d.line([(34, y), (74, y)], fill=WOOD)
        d.line([(34, y - 1), (74, y - 1)], fill=WOOD_L)
    for x in (34, 74):
        d.line([(x, top + 3), (x - 2, 266)], fill=WOOD_D, width=4)
        d.line([(x, top + 3), (x - 2, 266)], fill=WOOD_L, width=2)
        d.line([(x + 1, top + 4), (x - 1, 266)], fill=WOOD)
        d.arc([x - 1, top - 1, x + 7, top + 7], 180, 300, fill=WOOD_D, width=3)
        d.arc([x, top, x + 6, top + 6], 190, 290, fill=WOOD_L)
    for x in (34, 74):  # brass hinges where the ladder folds
        d.rectangle([x - 2, 247, x, 249], fill=hx("b8964a"))
    d.rectangle([8, 232, 18, 266], fill=hx("4a3828"))  # open trapdoor lid against the wall
    light(img, "ellipse", [0, 200, 120, 270], hx("ffd8a0"), 0.25, 12)


def _rocker_curve(p0, p1, p2, n=24):
    return [((1 - s) ** 2 * p0[0] + 2 * (1 - s) * s * p1[0] + s * s * p2[0],
             (1 - s) ** 2 * p0[1] + 2 * (1 - s) * s * p1[1] + s * s * p2[1]) for s in (i / n for i in range(n + 1))]


def _y_on(curve, x):
    return min(curve, key=lambda p: abs(p[0] - x))[1]


def rocking_chair(img):
    """A hand-carved rocking chair seen three-quarters from the left, facing the window: spindle back under a carved
    crest rail, scrolled arms, a thick seat, turned legs on long curved rockers."""
    d = ImageDraw.Draw(img)
    O = (16, -7)  # from the chair's near side to its far side
    far = lambda p: (p[0] + O[0], p[1] + O[1])
    dark, mid, lit, hi = hx("2e1c10"), hx("5a3a24"), hx("8a5c38"), hx("b88452")
    fdark, fmid = hx("24160c"), hx("442c1a")

    def stick(a, b, w, col, edge, glint=None):
        d.line([a, b], fill=edge, width=w + 1)
        d.line([a, b], fill=col, width=w)
        if glint:
            d.line([(a[0] + w // 2, a[1]), (b[0] + w // 2, b[1])], fill=glint)

    rocker = _rocker_curve((108, 179), (142, 197), (178, 184))
    seat_y, back_x, front_x = 170, 128, 160
    legs = ((back_x, seat_y, back_x - 3), (front_x, seat_y, front_x + 3))
    shadow(img, "polygon", [(110, 190), (182, 192), (198, 186), (128, 182)], 0.4, 3)
    # far side: rocker, legs and arm, in shadow
    fr = [far(p) for p in rocker]
    d.line(fr, fill=fdark, width=3)
    d.line([(x, y - 1) for x, y in fr], fill=fmid)
    for (x, top, foot) in legs:
        stick(far((x, top)), (foot + O[0], _y_on(fr, foot + O[0])), 2, fmid, fdark)
    fa0, fa1 = far((front_x + 1, seat_y)), far((front_x - 1, 150))
    stick(fa0, fa1, 2, fmid, fdark)
    stick(far((back_x - 6, 146)), far((front_x + 2, 150)), 2, fmid, fdark)
    # the back: posts leaning back, five turned spindles, a lower rail and the carved crest
    np0, np1 = (back_x, seat_y), (back_x - 9, 124)
    fp0, fp1 = far(np0), far(np1)
    for i in range(1, 6):
        t = i / 6
        top = (np1[0] + (fp1[0] - np1[0]) * t, np1[1] + (fp1[1] - np1[1]) * t + 4)
        bot = (np0[0] - 2 + (fp0[0] - np0[0]) * t, np0[1] - 7 + (fp0[1] - np0[1]) * t)
        stick(top, bot, 1, mid, dark)
        mx, my = (top[0] + bot[0]) / 2, (top[1] + bot[1]) / 2
        d.line([(mx - 1, my), (mx + 1, my)], fill=lit)  # the turned bulge
    stick((np0[0] - 2, np0[1] - 7), (fp0[0] - 2, fp0[1] - 7), 2, mid, dark, lit)
    stick(fp0, (fp1[0], fp1[1]), 2, fmid, fdark)
    crest = [(np1[0] - 1, np1[1] + 1), (np1[0] + 3, np1[1] - 3), ((np1[0] + fp1[0]) / 2, np1[1] - 7),
             (fp1[0] + 1, fp1[1] - 3), (fp1[0] + 1, fp1[1] + 4), ((np1[0] + fp1[0]) / 2, np1[1] - 1),
             (np1[0] + 1, np1[1] + 6)]
    d.polygon(crest, fill=mid, outline=dark)
    d.line([crest[1], crest[2], crest[3]], fill=hi)
    cx_, cy_ = (np1[0] + fp1[0]) / 2 + 1, np1[1] - 3  # a carved fan in the middle of the crest
    for a in (-60, -30, 0, 30, 60):
        d.line([(cx_, cy_ + 2), (cx_ + 3 * math.sin(math.radians(a)), cy_ + 2 - 3 * math.cos(math.radians(a)))],
               fill=dark)
    d.point((cx_, cy_ + 2), fill=hi)
    for k in (0.2, 0.8):  # notches along the crest
        nx, ny = np1[0] + (fp1[0] - np1[0]) * k, np1[1] + (fp1[1] - np1[1]) * k + 2
        d.point((nx, ny), fill=dark)
    # seat: a thick plank with a rounded front edge
    s0, s1 = (back_x - 2, seat_y), (front_x + 2, seat_y)
    d.polygon([s0, s1, far(s1), far(s0)], fill=lit, outline=dark)
    d.line([(s0[0] + 2, seat_y - 1), (far(s1)[0] - 2, far(s1)[1] + 1)], fill=mid)
    d.line([(s1[0] - 1, seat_y - 1), (far(s1)[0] - 1, far(s1)[1])], fill=hi)
    d.rectangle([s0[0], seat_y, s1[0], seat_y + 2], fill=mid, outline=dark)
    d.line([(s0[0] + 1, seat_y + 1), (s1[0] - 1, seat_y + 1)], fill=lit)
    # near posts, legs, rocker and arm
    stick((np0[0], np0[1] + 2), np1, 3, mid, dark, lit)
    d.ellipse([np1[0] - 2, np1[1] - 4, np1[0] + 2, np1[1]], fill=lit, outline=dark)  # finial
    d.ellipse([fp1[0] - 2, fp1[1] - 4, fp1[0] + 2, fp1[1]], fill=mid, outline=fdark)
    for (x, top, foot) in legs:
        bottom = (foot, _y_on(rocker, foot))
        stick((x, top + 2), bottom, 2, mid, dark, lit)
        my = (top + bottom[1]) / 2 + 1
        d.line([((x + foot) / 2 - 2, my), ((x + foot) / 2 + 2, my)], fill=hi)  # turned bead
        d.point(((x + foot) / 2 - 2, my + 1), fill=dark)
    stick((back_x - 1, seat_y + 9), (front_x + 2, seat_y + 9), 1, mid, dark)  # stretcher
    d.line(rocker, fill=dark, width=4)
    d.line([(x, y - 1) for x, y in rocker], fill=mid, width=2)
    d.line([(x, y - 2) for x, y in rocker[3:-3]], fill=hi)
    stick((front_x + 1, seat_y), (front_x - 1, 150), 2, mid, dark, lit)  # arm post
    arm = [(back_x - 6, 146), (front_x - 4, 149), (front_x + 3, 150)]
    d.line(arm, fill=dark, width=4)
    d.line(arm, fill=lit, width=2)
    d.line([(back_x - 5, 145), (front_x + 2, 149)], fill=hi)
    d.ellipse([front_x + 1, 147, front_x + 6, 152], fill=lit, outline=dark)  # scrolled hand grip
    d.point((front_x + 4, 149), fill=dark)
    light(img, "polygon", [far(np1), (front_x + 8, 150), (front_x + 8, seat_y), far(s1)], hx("fff0d0"), 0.12, 3)


def sheet_furniture(img, lifted=False):
    d = ImageDraw.Draw(img)
    if not lifted:
        d.polygon([(116, 192), (112, 168), (120, 140), (134, 126), (160, 122), (184, 130), (194, 150), (192, 172),
                   (200, 192)], fill=hx("c8c0b0"))
        for (a, bb) in (((134, 128), (128, 190)), ((160, 124), (158, 190)), ((184, 132), (182, 190)),
                        ((122, 150), (190, 156))):
            d.line([a, bb], fill=hx("a8a090"))
        d.line([(114, 170), (196, 172)], fill=hx("e0d8c8"))
        light(img, "polygon", [(120, 140), (134, 126), (160, 122), (150, 190), (116, 190)], hx("fff0d0"), 0.2, 6)
        shadow(img, "polygon", [(184, 130), (194, 150), (200, 192), (176, 192)], 0.3, 4)
        shadow(img, "ellipse", [110, 186, 206, 198], 0.45, 3)
    else:
        rocking_chair(img)
        # the sheet, dropped in a heap beside it
        heap = [(184, 197), (186, 188), (192, 181), (200, 180), (207, 186), (208, 197)]
        d.polygon(heap, fill=hx("c8c0b0"), outline=hx("8a8274"))
        d.line([(190, 186), (196, 196)], fill=hx("a8a090"))
        d.line([(199, 182), (202, 195)], fill=hx("a8a090"))
        d.line([(187, 192), (193, 190)], fill=hx("e8e0d0"))
        light(img, "polygon", [(192, 181), (200, 180), (207, 186), (200, 190)], hx("fff0d0"), 0.25, 2)


CARTON = dict(front=hx("a08458"), top=hx("c8aa76"), side=hx("b49466"), edge=hx("4e3a22"), tape=hx("d0bc8c"),
              inner=hx("bea274"), hole=hx("241a10"))
BOX_DEPTH = 0.12
# cartons against the gable wall, drawn bottom first: (x0, y0, x1, y1) of the front face, and the marker label
STACK = (((338, 158, 382, 190), "XMAS"), ((284, 152, 340, 190), "TAXES\n87-94"), ((344, 140, 372, 158), ""),
         ((314, 126, 340, 152), "MISC"))
OPEN_BOX = STACK[3][0]  # the box Daniel opens on his second search
TIN_AT = (288, 151)  # front-bottom-left corner of the tool tin, set down on top of the TAXES box
BOX_OPEN_BOX = (276, 104, 352, 156)  # crop for the opened-box overlay (box flaps and the tin)


def _box_points(box):
    x0, y0, x1, y1 = box
    k = 1 - BOX_DEPTH
    return along((x0, y0), k), along((x1, y0), k), along((x0, y1), k)


def carton(img, box, label="", opened=False):
    """A cardboard carton seen from the front and a little above, its left side towards the window."""
    d = ImageDraw.Draw(img)
    c = CARTON
    x0, y0, x1, y1 = box
    b0, b1, bl = _box_points(box)
    d.polygon([(x0, y0), b0, bl, (x0, y1)], fill=c["side"], outline=c["edge"])
    hgrad(img, (x0, y0, x1, y1), mix(c["front"], c["top"], 0.2), mix(c["front"], c["edge"], 0.3))
    shadow(img, "rect", [x0, y1 - 6, x1, y1 + 2], 0.25, 3)
    d.rectangle([x0, y0, x1, y1], outline=c["edge"])
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=mix(c["top"], c["front"], 0.3))
    mx, bmx = (x0 + x1) // 2, ((b0[0] + b1[0]) / 2, b0[1])
    if not opened:
        d.polygon([(x0, y0), (x1, y0), b1, b0], fill=c["top"], outline=c["edge"])
        d.line([(mx, y0), bmx], fill=c["tape"], width=3)
        d.line([(mx, y0), bmx], fill=mix(c["tape"], c["edge"], 0.45))
        d.rectangle([mx - 1, y0, mx + 1, y0 + 5], fill=c["tape"])
        d.line([(mx, y0 + 1), (mx, y0 + 5)], fill=mix(c["tape"], c["edge"], 0.3))
    else:
        top = [(x0, y0), (x1, y0), b1, b0]
        d.polygon(top, fill=c["hole"])
        # the lit inside of the far wall, crumpled newspaper and the dent where the tin lay
        d.polygon([b0, b1, (b1[0], b1[1] + 2), (b0[0], b0[1] + 2)], fill=mix(c["inner"], c["hole"], 0.45))
        d.polygon([(x0 + 3, y0 - 1), (x0 + 9, y0 - 3), (x0 + 12, y0 - 1), (x0 + 7, y0)], fill=hx("b8b4a8"))
        d.line([(x0 + 5, y0 - 1), (x0 + 10, y0 - 2)], fill=hx("6a6a70"))
        d.polygon([(x1 - 9, y0 - 2), (x1 - 4, y0 - 4), (x1 - 2, y0 - 1), (x1 - 7, y0)], fill=hx("9a968c"))
        f = 8
        d.polygon([b0, b1, (b1[0] + 1, b1[1] - f), (b0[0] - 1, b0[1] - f)], fill=c["inner"], outline=c["edge"])
        d.line([(b0[0], b0[1] - 1), (b1[0], b1[1] - 1)], fill=mix(c["inner"], c["edge"], 0.4))
        d.polygon([(x0, y0), b0, (b0[0] - f, b0[1] - 2), (x0 - f, y0 + 1)], fill=c["top"], outline=c["edge"])
        d.polygon([(x1, y0), b1, (b1[0] + f - 2, b1[1] - 3), (x1 + f - 2, y0 - 1)],
                  fill=mix(c["inner"], c["edge"], 0.25), outline=c["edge"])
        d.polygon([(x0, y0), (x1, y0), (x1 - 1, y0 + 6), (x0 + 1, y0 + 6)], fill=c["inner"], outline=c["edge"])
        d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=mix(c["inner"], hx("ffffff"), 0.2))
        d.line([(mx - 1, y0 + 5), (mx + 1, y0 + 5)], fill=c["tape"])  # the slit tape
    if label:
        lines = label.split("\n")
        cy = (y0 + y1) // 2 + 2 - 4 * (len(lines) - 1) + (2 if opened else 0)
        for i, line in enumerate(lines):
            text(img, ((x0 + x1) // 2, cy + 8 * i), line, hx("2a2a3a"), size=8)
    for (cx, cy) in ((x0 + 1, y1 - 3), (x1 - 3, y1 - 3)):  # crushed bottom corners
        d.line([(cx, cy), (cx + 2, cy + 2)], fill=mix(c["front"], c["edge"], 0.6))


def tool_tin(img, at=TIN_AT):
    """A red enamel tool tin with a carrying handle, its hasp shut by a little brass padlock."""
    d = ImageDraw.Draw(img)
    x, y = at
    w, h = 18, 8
    shadow(img, "rect", [x - 2, y - 3, x + w + 3, y + 1], 0.6, 1)
    back = along((x, y - h), 0.93)
    dx, dy = back[0] - x, back[1] - (y - h)
    lid = [(x, y - h), (x + w, y - h), (x + w + dx, y - h + dy), (x + dx, y - h + dy)]
    d.polygon([(x, y - h), (x + dx, y - h + dy), (x + dx, y + dy), (x, y)], fill=hx("7a1e18"))
    d.polygon(lid, fill=hx("d4523e"))
    d.line([(x + dx + 1, y - h + dy), (x + w + dx - 1, y - h + dy)], fill=hx("e87a60"))
    hgrad(img, (x, y - h, x + w, y), hx("c03a2c"), hx("8a2218"))
    d.rectangle([x, y - h, x + w, y], outline=hx("4a1210"))
    d.line([(x + 1, y - h + 1), (x + w - 1, y - h + 1)], fill=hx("e8705a"))
    d.line([(x + 1, y - h + 3), (x + w - 1, y - h + 3)], fill=hx("5a1610"))
    for px_ in (x + 2, x + w - 2):  # hinges
        d.point((px_, y - h + 2), fill=hx("c8c0b0"))
    # folding handle over the lid
    hy = y - h + dy // 2
    d.line([(x + 5, hy), (x + 5, hy - 4), (x + 13, hy - 4), (x + 13, hy)], fill=hx("2a2a30"), width=1)
    d.line([(x + 6, hy - 4), (x + 12, hy - 4)], fill=hx("a8a8b0"))
    # hasp and padlock
    cx = x + w // 2
    d.rectangle([cx - 1, y - h + 1, cx + 1, y - h + 4], fill=hx("b8b4a8"))
    d.arc([cx - 2, y - h + 2, cx + 2, y - h + 6], 180, 360, fill=hx("e0dcd0"))
    d.rectangle([cx - 2, y - h + 4, cx + 2, y - 1], fill=hx("e0b850"), outline=hx("7a5a1c"))
    d.point((cx, y - h + 6), fill=hx("2a2010"))
    # chipped enamel
    for (px_, py_) in ((x + 3, y - 2), (x + 15, y - 5), (x + 1, y - 1), (x + 16, y - 1)):
        d.point((px_, py_), fill=hx("6a6870"))


def boxes(img, opened=False):
    for box, label in STACK:
        carton(img, box, label, opened and box == OPEN_BOX)
    shadow(img, "rect", [282, 186, 386, 194], 0.4, 3)
    if opened:
        tool_tin(img)
    else:
        d = ImageDraw.Draw(img)
        x0, y0 = OPEN_BOX[0], OPEN_BOX[1]
        d.polygon([(x0 + 4, y0 - 1), (x0 + 16, y0 - 5), (x0 + 19, y0 - 1)], fill=hx("e8e0d0"))  # paper peeking out


def spilled(img):
    """The tax returns across the floor."""
    d = ImageDraw.Draw(img)
    rnd = random.Random(12)
    for _ in range(26):
        x, y = rnd.randint(268, 374), rnd.randint(190, 212)
        w, h = rnd.randint(8, 13), rnd.randint(4, 6)
        sk = rnd.randint(-3, 3)
        col = rnd.choice([hx("e8e0d0"), hx("d8d0b8"), hx("f0ece0"), hx("c8d0d8")])
        d.polygon([(x, y), (x + w, y + sk), (x + w, y + h + sk), (x, y + h)], fill=col, outline=hx("8a8070"))
        d.line([(x + 2, y + 2), (x + w - 2, y + 2 + sk)], fill=hx("8a8a9a"))


def trunk(img, opened=False):
    """A canvas-covered steamer trunk with oak slats and brass corners, seen three-quarter from the room."""
    d = ImageDraw.Draw(img)
    x0, x1, yt, ys, yb = 398, 466, 176, 196, 230  # front face: top, lid seam, bottom
    k = 0.93
    canvas, canvas_d, canvas_l = hx("3e4e3c"), hx("26321f"), hx("54664c")
    oak, oak_d, oak_l = hx("6a4a2a"), hx("3a2814"), hx("8e6a3e")
    brass, brass_d, brass_l = hx("b8964a"), hx("6a5020"), hx("e8cc80")
    edge = hx("141a12")
    top = ys if opened else yt  # with the lid thrown back, the body ends at the seam
    bt0, bt1 = along((x0, top), k), along((x1, top), k)
    bb0 = along((x0, yb), k)
    shadow(img, "polygon", [(x0 - 4, yb + 1), (x1 + 6, yb + 2), (x1 + 2, yb - 6), bb0], 0.55, 3)

    # left end, turned towards the window light only a little
    d.polygon([(x0, top), bt0, bb0, (x0, yb)], fill=canvas_d, outline=edge)
    sy = along((x0, ys), k)
    d.line([(x0, ys), sy], fill=oak_d, width=2)
    for yy in (top + 3, yb - 4):
        d.line([(x0, yy), along((x0, yy), k)], fill=oak_d)
    hy = (ys + yb) // 2 + 1  # leather end handle in its brass cleats
    hp0, hp1 = along((x0, hy), 0.985), along((x0, hy), 0.945)
    d.rectangle([hp1[0] - 1, hp1[1] - 1, hp1[0], hp1[1] + 1], fill=brass_d)
    d.rectangle([hp0[0] - 1, hp0[1] - 1, hp0[0], hp0[1] + 1], fill=brass_d)
    d.line([(hp1[0], hp1[1] + 1), (hp1[0] + 1, hp1[1] + 4), (hp0[0] - 1, hp0[1] + 4), (hp0[0], hp0[1] + 1)],
           fill=hx("4a2a14"))

    if not opened:
        # the lid top, slightly domed, with its two oak slats running back
        d.polygon([(x0, yt), (x1, yt), bt1, bt0], fill=canvas_l, outline=edge)
        d.line([(x0 + 1, yt - 1), (x1 - 1, yt - 1)], fill=hx("6a7a5a"))
        d.line([(bt0[0] + 2, bt0[1] + 1), (bt1[0] - 2, bt1[1] + 1)], fill=hx("4a5a44"))
        for sx in (x0 + 15, x1 - 15):
            bx = along((sx, yt), k)
            d.polygon([(sx - 2, yt), (sx + 2, yt), (bx[0] + 2, bx[1]), (bx[0] - 2, bx[1])], fill=oak, outline=oak_d)
            d.line([(sx - 1, yt - 1), (bx[0] - 1, bx[1] + 1)], fill=oak_l)
        for (cx, cy) in (bt0, bt1):
            d.rectangle([cx - 1, cy, cx + 2, cy + 2], fill=brass)

    # the front: canvas over boards, with a little weave
    tmp = Image.new("RGB", img.size)
    hgrad(tmp, (x0, yt, x1, yb), canvas_d, canvas)
    noise(tmp, (x0, yt, x1, yb), 6, seed=31)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).rectangle([x0, ys if opened else yt, x1, yb], fill=255)
    img.paste(tmp, (0, 0), m)
    d.rectangle([x0, ys if opened else yt, x1, yb], outline=edge)
    # oak bands round the body (and the lid, when shut)
    bands = [(ys + 2, ys + 5), (yb - 6, yb - 3)] + ([] if opened else [(yt + 2, yt + 5), (ys - 7, ys - 4)])
    for (a, b) in bands:
        d.rectangle([x0 + 1, a, x1 - 1, b], fill=oak, outline=oak_d)
        d.line([(x0 + 2, a + 1), (x1 - 2, a + 1)], fill=oak_l)
        for rx in range(x0 + 6, x1 - 3, 9):
            d.point((rx, (a + b) // 2), fill=brass_l)
    for sx in (x0 + 15, x1 - 15):  # upright slats
        d.rectangle([sx - 2, ys if opened else yt, sx + 2, yb], fill=oak, outline=oak_d)
        d.line([(sx - 1, (ys if opened else yt) + 1), (sx - 1, yb - 1)], fill=oak_l)
        for ry in range((ys if opened else yt) + 3, yb - 1, 6):
            d.point((sx, ry), fill=brass_l)
    # lid seam with its brass valance
    if not opened:
        d.line([(x0, ys), (x1, ys)], fill=edge)
        d.line([(x0 + 1, ys - 1), (x1 - 1, ys - 1)], fill=brass_d)
    d.line([(x0 + 1, ys + 1), (x1 - 1, ys + 1)], fill=brass)

    # travel labels: a round hotel sticker, a red steamship tag, a torn customs slip
    lx, ly = x0 + 21, ys + 9
    d.ellipse([lx, ly, lx + 12, ly + 9], fill=hx("d8c08a"), outline=hx("8a7448"))
    d.ellipse([lx + 3, ly + 2, lx + 9, ly + 7], outline=hx("a0503a"))
    d.line([(lx + 4, ly + 4), (lx + 8, ly + 4)], fill=hx("4a3a2a"))
    rx, ry = x1 - 31, ys + 17
    d.rectangle([rx, ry, rx + 11, ry + 7], fill=hx("a84030"), outline=hx("5a1e14"))
    d.line([(rx + 1, ry + 2), (rx + 10, ry + 2)], fill=hx("e8dcc0"))
    d.line([(rx + 2, ry + 5), (rx + 7, ry + 5)], fill=hx("e0b080"))
    d.polygon([(x1 - 13, ys + 9), (x1 - 5, ys + 8), (x1 - 4, ys + 14), (x1 - 8, ys + 13), (x1 - 12, ys + 15)],
              fill=hx("c8c0a8"), outline=hx("7a7460"))
    d.line([(x1 - 11, ys + 11), (x1 - 6, ys + 10)], fill=hx("5a6a8a"))

    # leather straps buckled over the front
    for sx in (x0 + 8, x1 - 8):
        top = ys + 1 if opened else yt
        d.rectangle([sx - 1, top, sx + 1, yb], fill=hx("4a2a14"))
        d.line([(sx - 1, top), (sx - 1, yb)], fill=hx("6a4024"))
        by = ys + 6
        d.rectangle([sx - 2, by, sx + 2, by + 3], outline=brass)
        d.point((sx, by + 1), fill=brass_l)

    # brass corner caps with rivets
    for (cx, cy, fx, fy) in ((x0, yt if not opened else ys, 1, 1), (x1, yt if not opened else ys, -1, 1),
                             (x0, yb, 1, -1), (x1, yb, -1, -1)):
        pts = [(cx, cy), (cx + 6 * fx, cy), (cx + 6 * fx, cy + 2 * fy), (cx + 2 * fx, cy + 6 * fy), (cx, cy + 6 * fy)]
        d.polygon(pts, fill=brass, outline=brass_d)
        d.point((cx + 2 * fx, cy + 2 * fy), fill=brass_l)
    for cy in ((yt if not opened else ys), yb):
        d.rectangle([bt0[0] - 1 if cy != yb else bb0[0] - 1, (bt0[1] if cy != yb else bb0[1]) - 1,
                     (bt0[0] if cy != yb else bb0[0]) + 1, (bt0[1] if cy != yb else bb0[1]) + 1], fill=brass_d)

    # the lock: a brass plate and, when shut, the hasp coming down from the lid
    cx = (x0 + x1) // 2
    d.rectangle([cx - 4, ys + 1, cx + 4, ys + 9], fill=brass, outline=brass_d)
    d.line([(cx - 3, ys + 2), (cx + 3, ys + 2)], fill=brass_l)
    d.rectangle([cx - 1, ys + 5, cx, ys + 7], fill=hx("1a1008"))
    if not opened:
        d.rectangle([cx - 3, ys - 5, cx + 3, ys + 3], fill=brass, outline=brass_d)
        d.line([(cx - 2, ys - 4), (cx + 2, ys - 4)], fill=brass_l)
    # scuffs and worn canvas
    for (sx, sy) in ((x0 + 4, yb - 9), (x1 - 22, yb - 8), (x0 + 30, ys + 20)):
        d.point((sx, sy), fill=hx("6a7a5e"))
    d.line([(x0 + 33, yb - 9), (x0 + 37, yb - 10)], fill=canvas_d)

    if opened:
        # lid thrown back against the paintings, its papered lining towards the room
        lt = 152
        l0, l1 = (bt0[0] - 1, lt), (bt1[0] + 2, lt - 1)
        d.polygon([bt0, bt1, l1, l0], fill=canvas_d, outline=edge)
        i0, i1 = (bt0[0] + 3, bt0[1] - 2), (bt1[0] - 2, bt1[1] - 2)
        j0, j1 = (l0[0] + 3, l0[1] + 3), (l1[0] - 3, l1[1] + 3)
        tmp = Image.new("RGB", img.size)
        vgrad(tmp, (int(j0[0]), int(j0[1]), int(i1[0]), int(i1[1])), hx("7a4444"), hx("5a2c2e"))
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon([i0, i1, j1, j0], fill=255)
        img.paste(tmp, (0, 0), m)
        d.polygon([i0, i1, j1, j0], outline=oak_d)
        for yy in range(int(j0[1]) + 4, int(i0[1]) - 1, 5):  # faded stripes in the lining paper
            d.line([(j0[0] + 1, yy), (j1[0] - 1, yy)], fill=hx("6a3838"))
        for xx in range(int(j0[0]) + 6, int(j1[0]), 8):
            for yy in range(int(j0[1]) + 6, int(i0[1]) - 2, 5):
                d.point((xx + (yy // 5) % 2 * 4, yy), fill=hx("9a6a50"))
        # ribbons crossing the lid, pinned with brass buttons, holding a photograph
        d.line([(j0[0] + 1, j0[1] + 1), (i1[0] - 1, i1[1] - 1)], fill=hx("c8b080"))
        d.line([(j1[0] - 1, j1[1] + 1), (i0[0] + 1, i0[1] - 1)], fill=hx("c8b080"))
        mx, my = (j0[0] + i1[0]) / 2, (j0[1] + i1[1]) / 2
        d.rectangle([mx - 6, my - 5, mx + 4, my + 4], fill=hx("e0d6bc"), outline=hx("8a8068"))
        d.rectangle([mx - 4, my - 3, mx + 2, my + 2], fill=hx("6a6258"))
        d.ellipse([mx - 2, my - 2, mx, my], fill=hx("a89a88"))
        for (px_, py_) in (j0, j1, i0, i1, (mx, my)):
            d.point((px_ + (1 if px_ < mx else -1), py_ + (1 if py_ < my else -1)), fill=brass_l)
        # lid edge banding and the stay strap holding it up
        d.line([l0, l1], fill=oak)
        d.line([(l0[0], l0[1] + 1), (l1[0], l1[1] + 1)], fill=oak_d)
        d.line([(l1[0] - 1, l1[1] + 6), (bt1[0] - 1, bt1[1] - 1)], fill=hx("4a2a14"))
        d.line([(l1[0] + 1, l1[1]), (bt1[0] + 1, bt1[1])], fill=hx("26321f"))
        # the open body: a sliding tray inside, the fedora resting in it
        d.polygon([(x0, ys), (x1, ys), bt1, bt0], fill=hx("1a1210"), outline=edge)
        d.polygon([(x0 + 2, ys - 1), (x1 - 2, ys - 1), (bt1[0] - 2, bt1[1] + 4), (bt0[0] + 2, bt0[1] + 4)],
                  fill=hx("4a3424"))
        d.line([(x0 + 2, ys - 1), (x1 - 2, ys - 1)], fill=hx("7a5a3a"))
        d.line([(cx + 8, ys - 1), (cx + 8, bt1[1] + 4)], fill=hx("2a1c12"))  # tray divider
        d.polygon([(cx + 12, ys - 2), (cx + 22, ys - 4), (cx + 26, ys - 2), (cx + 16, ys)], fill=hx("c8bca0"),
                  outline=hx("7a7058"))  # folded letters
        d.line([(cx + 15, ys - 2), (cx + 22, ys - 3)], fill=hx("6a6a8a"))
        # an old fedora: brim, crown with its pinch and a dark band
        fx = x0 + 10
        d.ellipse([fx, ys - 5, fx + 24, ys + 1], fill=hx("3a3028"), outline=hx("1a1410"))
        d.line([(fx + 3, ys - 4), (fx + 20, ys - 4)], fill=hx("5a4a3a"))
        d.polygon([(fx + 5, ys - 3), (fx + 6, ys - 10), (fx + 11, ys - 12), (fx + 13, ys - 10), (fx + 15, ys - 12),
                   (fx + 19, ys - 10), (fx + 19, ys - 3)], fill=hx("4a3a30"), outline=hx("1a1410"))
        d.line([(fx + 12, ys - 10), (fx + 12, ys - 7)], fill=hx("2a2018"))
        d.line([(fx + 7, ys - 9), (fx + 10, ys - 10)], fill=hx("6a5848"))
        d.rectangle([fx + 6, ys - 6, fx + 18, ys - 4], fill=hx("1a1010"))
        d.point((fx + 17, ys - 5), fill=hx("5a3a2a"))


def _shaded(img, outline, box, dark, lit, edge=None):
    """Fills a silhouette with a horizontal light-to-dark ramp (the window and bulb are to the right)."""
    tmp = Image.new("RGB", img.size)
    x0, y0, x1, y1 = box
    xm = x0 + (x1 - x0) * 2 // 3
    hgrad(tmp, (x0, y0, xm, y1), dark, lit)
    hgrad(tmp, (xm, y0, x1, y1), lit, edge or mix(lit, dark, 0.5))
    m = Image.new("L", img.size, 0)
    outline(ImageDraw.Draw(m))
    img.paste(tmp, (0, 0), m)


def dress_form(img):
    d = ImageDraw.Draw(img)
    cx = 225
    shadow(img, "ellipse", [cx - 14, 188, cx + 16, 196], 0.5, 2)
    # tripod stand and pole
    for (fx, fy) in ((cx - 11, 193), (cx + 12, 193), (cx + 2, 196)):
        d.line([(cx, 184), (fx, fy)], fill=hx("2a1e14"), width=2)
        d.point((fx, fy - 1), fill=hx("8a6a44"))
    d.line([(cx, 168), (cx, 186)], fill=hx("2a1e14"), width=3)
    d.line([(cx + 1, 168), (cx + 1, 186)], fill=hx("8a6a44"))
    d.rectangle([cx - 2, 176, cx + 2, 178], fill=hx("b08a48"))
    side = [(-3, 120), (-4, 126), (-10, 129), (-11, 134), (-11, 140), (-8, 145), (-7, 151), (-9, 157), (-11, 162),
            (-11, 168)]
    body = [(cx + dx, y) for dx, y in side] + [(cx - dx, y) for dx, y in reversed(side)]
    _shaded(img, lambda md: (md.polygon(body, fill=255), md.ellipse([cx - 11, 165, cx + 11, 171], fill=255)),
            (cx - 11, 118, cx + 11, 171), hx("5a3c3c"), hx("c49c90"), hx("8a6462"))
    # seams, the hem and the neck cap
    for sx in (-1, 1):
        d.line([(cx + sx * 6, 129), (cx + sx * 7, 138), (cx + sx * 4, 151), (cx + sx * 6, 160), (cx + sx * 6, 170)],
               fill=hx("6a4644"))
    d.line([(cx, 127), (cx, 170)], fill=hx("8a6462"))
    d.line([(cx - 7, 151), (cx + 7, 151)], fill=hx("7a5452"))
    d.arc([cx - 11, 165, cx + 11, 171], 0, 180, fill=hx("3a2424"))
    d.ellipse([cx - 4, 115, cx + 4, 120], fill=hx("3a2a1c"))
    d.ellipse([cx - 2, 114, cx + 1, 116], fill=hx("8a6a44"))
    light(img, "ellipse", [cx - 2, 130, cx + 8, 146], hx("ffe8d8"), 0.25, 2)
    # a tape measure draped round the neck
    tape = hx("e8c860")
    d.line([(cx - 3, 125), (cx - 7, 129), (cx - 8, 140), (cx - 7, 147)], fill=tape)
    d.line([(cx + 3, 125), (cx + 7, 129), (cx + 9, 138), (cx + 8, 152)], fill=tape)
    d.line([(cx - 3, 125), (cx + 3, 125)], fill=tape)
    for (tx, ty) in ((cx - 8, 133), (cx - 8, 139), (cx + 9, 136), (cx + 9, 142), (cx + 8, 148)):
        d.point((tx, ty), fill=hx("3a2a1c"))
    d.point((cx + 3, 140), fill=hx("e8e0d0"))  # pin heads
    d.point((cx - 2, 136), fill=hx("c83838"))


def radio(img):
    """A cathedral radio on a little bedside cabinet: gothic fretwork over the grille cloth, a dial and three knobs."""
    d = ImageDraw.Draw(img)
    # the cabinet: a solid box with a drawer and a fielded panel, standing on short turned feet
    shadow(img, "polygon", [(44, 211), (90, 211), (100, 204), (60, 204)], 0.5, 2)
    for fx in (48, 85):
        d.rectangle([fx, 209, fx + 2, 213], fill=hx("2a1c10"))
        d.point((fx + 1, 210), fill=hx("8a6c4c"))
    back = lambda p: along(p, 0.96)
    d.polygon([(87, 199), back((87, 199)), back((87, 209)), (87, 209)], fill=hx("806448"), outline=hx("3a2a1c"))
    hgrad(img, (47, 199, 87, 209), hx("4a3424"), hx("7a5c40"))
    d.rectangle([47, 199, 87, 209], outline=hx("2a1c10"))
    d.line([(48, 203), (86, 203)], fill=hx("2a1c10"))  # drawer
    d.line([(48, 204), (86, 204)], fill=hx("8a6c4c"))
    d.rectangle([65, 200, 69, 201], fill=hx("c8a050"))
    d.point((67, 202), fill=hx("6a4a1c"))
    d.rectangle([51, 205, 83, 208], outline=hx("3a2818"))  # fielded panel
    d.line([(52, 205), (82, 205)], fill=hx("8a6c4c"))
    # the top, overhanging a little, its far edge disappearing under the radio
    d.polygon([(45, 197), (89, 197), back((89, 197)), back((45, 197))], fill=hx("8a6a48"), outline=hx("3a2a1c"))
    d.rectangle([45, 197, 89, 199], fill=hx("6a5038"), outline=hx("2a1c10"))
    d.line([(46, 197), (88, 197)], fill=hx("a88a64"))
    # cabinet: right side face, then the front
    sil = lambda md, ox=0, oy=0: (md.rectangle([48 + ox, 170 + oy, 80 + ox, 196 + oy], fill=255),
                                  md.ellipse([48 + ox, 154 + oy, 80 + ox, 186 + oy], fill=255))
    side = Image.new("L", img.size, 0)
    sil(ImageDraw.Draw(side), 3, -1)
    img.paste(Image.new("RGB", img.size, hx("8a5a30")), (0, 0), side)
    _shaded(img, sil, (48, 154, 80, 196), hx("3a1c0c"), hx("7a4422"), hx("5a3016"))
    d.arc([48, 154, 80, 186], 180, 360, fill=hx("b07a44"))
    d.arc([50, 156, 78, 184], 190, 350, fill=hx("2a1408"))
    d.line([(48, 170), (48, 196)], fill=hx("2a1408"))
    d.line([(80, 170), (80, 196)], fill=hx("b07a44"))
    # grille: three lancets of cloth behind the fretwork
    d.chord([53, 160, 75, 182], 180, 360, fill=hx("2a1408"))
    d.rectangle([53, 171, 75, 184], fill=hx("2a1408"))
    for (lx, top) in ((54, 167), (61, 162), (69, 167)):
        cloth = [(lx, 184), (lx, top + 4), (lx + 2.5, top), (lx + 5, top + 4), (lx + 5, 184)]
        d.polygon(cloth, fill=hx("c8a868"))
        for y in range(top + 2, 184, 2):
            d.line([(lx + 1, y), (lx + 4, y)], fill=hx("a88a50"))
    d.line([(53, 184), (75, 184)], fill=hx("b07a44"))
    # dial window and knobs
    d.chord([58, 185, 70, 193], 180, 360, fill=hx("f0dca8"), outline=hx("2a1408"))
    d.line([(64, 189), (66, 186)], fill=hx("a02818"))
    for kx in (53, 64, 74):
        d.ellipse([kx - 2, 191, kx + 2, 195], fill=hx("1e1008"))
        d.point((kx + 1, 192), fill=hx("c8a050"))
    d.rectangle([46, 195, 83, 197], fill=hx("2a1408"))
    light(img, "ellipse", [66, 156, 80, 170], hx("ffd8a0"), 0.3, 2)


def suitcase(img, opened=False):
    """A battered leather suitcase lying flat on the floor, handle towards the room; opened, its lid stands up."""
    d = ImageDraw.Draw(img)
    x0, x1, yt, yb = SUITCASE["x0"], SUITCASE["x1"], SUITCASE["top"], SUITCASE["bottom"]
    k = SUITCASE["depth"]
    leather, dark, edge, brass = hx("7e4430"), hx("4a2418"), hx("2a1a10"), hx("c8a050")
    ys = yt + 4 if opened else yt  # the lid's own rim is part of the front face while it is shut
    b0, b1 = along((x0, ys), k), along((x1, ys), k)
    bb1 = along((x1, yb), k)
    shadow(img, "polygon", [(x0 - 2, yb + 1), (x1 + 2, yb + 1), (bb1[0] + 4, bb1[1] + 1), (b1[0], yb - 6)], 0.55, 2)
    # right end
    d.polygon([(x1, ys), b1, bb1, (x1, yb)], fill=hx("5e2e1e"), outline=edge)
    d.point((x1 + 2, yb - 2), fill=brass)
    if not opened:
        d.polygon([(x0, yt), (x1, yt), b1, b0], fill=hx("9a5a3e"), outline=edge)
        tmp = Image.new("RGB", img.size)
        hgrad(tmp, (x0, int(b0[1]), int(b1[0]), yt), hx("8a4c34"), hx("b4744e"))
        m = Image.new("L", img.size, 0)
        ImageDraw.Draw(m).polygon([(x0 + 1, yt - 1), (x1 - 1, yt - 1), (b1[0] - 1, b1[1] + 1), (b0[0] + 1, b0[1] + 1)],
                                  fill=255)
        img.paste(tmp, (0, 0), m)
        for sx in (x0 + 8, x1 - 10):  # straps running over the lid
            bx = along((sx, yt), k)
            d.line([(sx, yt), bx], fill=hx("3a2014"), width=3)
            d.line([(sx + 1, yt), (bx[0] + 1, bx[1])], fill=hx("5a3020"))
        d.ellipse([x0 + 16, yt - 7, x0 + 25, yt - 3], fill=hx("e0d0a8"), outline=hx("8a7050"))  # hotel sticker
        d.line([(x0 + 17, yt - 5), (x0 + 24, yt - 5)], fill=hx("b03828"))
        d.point((b1[0] - 3, b1[1] + 2), fill=brass)
        d.point((b0[0] + 2, b0[1] + 1), fill=brass)
    else:
        # the lid, thrown back on its hinges: its lining faces the room, torn where the key was sewn in
        lift = SUITCASE["lid"]
        l0, l1 = (b0[0] + 2, b0[1] - lift), (b1[0] + 2, b1[1] - lift)
        d.polygon([b0, b1, l1, l0], fill=hx("6a2430"), outline=edge)
        d.line([(b0[0] + 1, b0[1] - 1), (l0[0] + 1, l0[1] + 1)], fill=hx("a86a4a"))
        d.line([(l0[0] + 1, l0[1] + 1), (l1[0] - 1, l1[1] + 1)], fill=hx("b4744e"))
        d.line([(b1[0] - 1, b1[1] - 1), (l1[0] - 1, l1[1] + 1)], fill=hx("4a2418"))
        px_, py_ = b0[0] + 4, b0[1] - 7  # an elastic pocket across the bottom of the lid
        d.polygon([(px_, py_), (b1[0] - 2, py_), (b1[0] - 2, b1[1] - 2), (px_, b0[1] - 2)], fill=hx("5a1e28"))
        d.line([(px_, py_), (b1[0] - 2, py_)], fill=hx("9a4a58"))
        for gx in range(int(px_) + 3, int(b1[0]) - 2, 4):
            d.line([(gx, py_ + 1), (gx, py_ + 2)], fill=hx("4a1820"))
        # the lining slit open along a seam near the top, a long flap peeled back to one side
        sx0, sy0 = l0[0] + 5, l0[1] + 5
        sx1, sy1 = l1[0] - 6, l1[1] + 7
        d.polygon([(sx0, sy0), (sx1, sy1), (sx1 - 2, sy1 + 3), (sx0 + 3, sy0 + 2)], fill=hx("1a0a0c"))
        d.polygon([(sx1, sy1), (sx1 - 2, sy1 + 3), (sx1 + 3, sy1 + 9), (sx1 + 5, sy1 + 4)], fill=hx("a24c5a"),
                  outline=hx("4a1a22"))  # the flap, folded down at the right
        d.line([(sx1 + 1, sy1 + 3), (sx1 + 3, sy1 + 7)], fill=hx("c8707a"))
        for i in range(0, int(sx1 - sx0) - 1, 3):  # cut stitches along the top edge of the slit
            t = i / max(1, sx1 - sx0)
            d.point((sx0 + i, sy0 + (sy1 - sy0) * t - 1), fill=hx("c8a878"))
        # inside the case: the far wall catches the light, the bottom is in shadow
        d.polygon([(x0, ys), (x1, ys), b1, b0], fill=hx("2a0e12"), outline=edge)
        d.polygon([b0, b1, (b1[0] - 1, b1[1] + 3), (b0[0] + 1, b0[1] + 3)], fill=hx("7a2c38"))
        d.polygon([(x0 + 2, ys - 1), (x1 - 2, ys - 1), (x1 - 3, ys - 3), (x0 + 3, ys - 3)], fill=hx("4a1a22"))
        d.polygon([(x0 + 6, ys - 2), (x0 + 13, ys - 6), (x0 + 19, ys - 4), (x0 + 12, ys - 1)], fill=hx("d8ccb4"),
                  outline=hx("8a8070"))  # old tissue paper
        d.line([(x0 + 9, ys - 3), (x0 + 15, ys - 5)], fill=hx("a8a090"))
    # the front: lid and body halves, two brass latches and the leather handle
    hgrad(img, (x0, ys, x1, yb), dark, leather)
    d.rectangle([x0, ys, x1, yb], outline=edge)
    d.line([(x0 + 1, ys + 1), (x1 - 1, ys + 1)], fill=hx("a86a4a"))
    if not opened:
        d.line([(x0 + 1, yt + 4), (x1 - 1, yt + 4)], fill=edge)
        d.line([(x0 + 1, yt + 5), (x1 - 1, yt + 5)], fill=hx("9a5a40"))
    for sx in (x0 + 8, x1 - 10):
        d.rectangle([sx - 1, ys, sx + 1, yb], fill=hx("3a2014"))
        d.rectangle([sx - 2, yb - 4, sx + 2, yb - 2], outline=hx("d8b060"))
    for lx in (x0 + 4, x1 - 6):
        if opened:
            d.rectangle([lx, ys - 1, lx + 2, ys + 1], fill=brass)
        else:
            d.rectangle([lx, yt + 3, lx + 2, yt + 6], fill=brass, outline=hx("6a4a1c"))
    hx0 = (x0 + x1) // 2
    d.line([(hx0 - 4, ys + 3), (hx0 - 3, ys + 1), (hx0 + 3, ys + 1), (hx0 + 4, ys + 3)], fill=hx("1e120a"), width=2)
    d.point((hx0 - 4, ys + 3), fill=brass)
    d.point((hx0 + 4, ys + 3), fill=brass)
    for (cx, cy) in ((x0, ys), (x1 - 1, ys), (x0, yb - 1), (x1 - 1, yb - 1)):
        d.rectangle([cx, cy, cx + 1, cy + 1], fill=brass)
    for (sx, sy) in ((x0 + 14, yb - 2), (x1 - 3, ys + 3)):  # scuffs
        d.point((sx, sy), fill=hx("a87458"))

def hat_box(img):
    """A round, striped hat box with its lid on and a ribbon bow."""
    d = ImageDraw.Draw(img)
    cx, r, ry, top, bot = 97, 11, 3, 170, 188
    shadow(img, "ellipse", [cx - r - 1, bot - 2, cx + r + 5, bot + 5], 0.5, 2)
    body = lambda md: (md.rectangle([cx - r, top, cx + r, bot], fill=255),
                       md.ellipse([cx - r, bot - ry, cx + r, bot + ry], fill=255))
    _shaded(img, body, (cx - r, top, cx + r, bot + ry), hx("4a1a26"), hx("b0566a"), hx("7a3042"))
    for a in range(-75, 90, 22):
        sx = cx + r * math.sin(math.radians(a))
        shade = 0.35 + 0.65 * (1 - abs(a - 30) / 120)
        col = mix(hx("4a3a3a"), hx("f0e0c8"), shade)
        sag = ry * math.cos(math.radians(a))
        d.line([(sx, top + 3 + sag), (sx, bot + sag)], fill=col)
    # lid
    lid = lambda md: (md.rectangle([cx - r - 1, top - 5, cx + r + 1, top + 1], fill=255),
                      md.ellipse([cx - r - 1, top - 2, cx + r + 1, top + 4], fill=255))
    _shaded(img, lid, (cx - r - 1, top - 5, cx + r + 1, top + 4), hx("3a1420"), hx("8a3a4c"), hx("5a2232"))
    d.ellipse([cx - r - 1, top - 8, cx + r + 1, top - 2], fill=hx("b86a7a"), outline=hx("5a2232"))
    light(img, "ellipse", [cx - 2, top - 8, cx + 10, top - 3], hx("ffe0e0"), 0.3, 1)
    d.line([(cx - 2, top - 1), (cx - 2, top + 5)], fill=hx("e8d8b0"))
    d.polygon([(cx - 2, top - 1), (cx - 6, top - 3), (cx - 6, top + 1)], fill=hx("e8d8b0"))
    d.polygon([(cx - 2, top - 1), (cx + 2, top - 3), (cx + 2, top + 1)], fill=hx("d8c49a"))


def portraits(img):
    """Two old family portraits leaning on the right knee wall: a group in a gilt frame and an oval in walnut."""
    group = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(group)
    gilt, gilt_d, gilt_l = hx("a08040"), hx("5a4420"), hx("e0c070")
    # the family group, in a deep gilt frame with a moulded inner lip
    d.polygon([(418, 150), (452, 146), (456, 186), (420, 188)], fill=gilt, outline=gilt_d)
    d.line([(419, 151), (451, 147)], fill=gilt_l)
    d.line([(419, 151), (421, 187)], fill=gilt_l)
    d.polygon([(421, 153), (450, 149), (453, 183), (423, 185)], fill=hx("7a5a28"))
    for (fx, fy) in ((420, 150), (450, 147), (453, 184), (421, 186)):  # carved corner bosses
        d.rectangle([fx, fy, fx + 1, fy + 1], fill=gilt_l)
    d.polygon([(423, 155), (449, 151), (451, 181), (425, 183)], fill=hx("34301f"))
    d.polygon([(423, 155), (449, 151), (449, 157), (423, 161)], fill=hx("3e3826"))
    d.polygon([(425, 172), (450, 168), (451, 181), (425, 183)], fill=hx("2a2418"))  # floor of the studio
    d.polygon([(427, 160), (437, 158), (437, 172), (427, 173)], fill=hx("4a4030"))  # a painted drape
    d.line([(429, 160), (430, 172)], fill=hx("5a5038"))
    skin, coat, collar = hx("c8a080"), hx("1a1614"), hx("e8e0d0")
    # father standing behind, wide moustache and a stiff collar
    d.ellipse([437, 156, 441, 161], fill=skin)
    d.line([(437, 156), (441, 156)], fill=hx("2a2018"))
    d.line([(438, 160), (440, 160)], fill=hx("3a2a20"))
    d.point((438, 158), fill=hx("2a1a14"))
    d.point((440, 158), fill=hx("2a1a14"))
    d.polygon([(435, 163), (443, 162), (444, 178), (434, 179)], fill=coat)
    d.rectangle([438, 161, 440, 163], fill=collar)
    d.point((439, 164), fill=hx("6a2020"))
    # mother seated in front, hair in a bun, high-necked dark dress with a cameo
    d.ellipse([430, 163, 434, 167], fill=skin)
    d.ellipse([430, 161, 434, 164], fill=hx("3a2a1c"))
    d.point((432, 160), fill=hx("3a2a1c"))
    d.polygon([(429, 168), (435, 168), (437, 181), (427, 182)], fill=hx("2a1e24"))
    d.point((432, 169), fill=hx("e8d8c0"))
    d.line([(428, 175), (436, 174)], fill=hx("3a2e34"))
    # a boy in a sailor collar, and a girl with a white bow
    d.ellipse([443, 166, 446, 169], fill=skin)
    d.polygon([(442, 170), (447, 170), (447, 178), (442, 178)], fill=hx("2a3040"))
    d.line([(443, 170), (446, 171)], fill=collar)
    d.ellipse([445, 170, 448, 173], fill=skin)
    d.point((446, 169), fill=collar)
    d.point((447, 169), fill=collar)
    d.polygon([(444, 174), (449, 173), (450, 180), (444, 180)], fill=hx("5a4a3a"))
    d.line([(424, 156), (448, 152)], fill=hx("6a5838"))  # varnish catching the bulb
    d.line([(425, 182), (450, 179)], fill=gilt_d)
    # a small brass title plate on the frame
    d.rectangle([435, 185, 441, 186], fill=gilt_l)

    img.paste(group, (0, -16), group)  # hung high, so the family looks out over the trunk

    # the oval portrait of a stern old man, in a dark walnut frame
    oval = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(oval)
    d.polygon([(448, 156), (474, 154), (476, 186), (450, 188)], fill=hx("5a3a20"), outline=hx("2a180a"))
    d.line([(449, 157), (473, 155)], fill=hx("8a5a30"))
    d.line([(449, 157), (451, 187)], fill=hx("7a4e28"))
    d.polygon([(451, 159), (472, 157), (473, 184), (453, 186)], fill=hx("c8b890"))  # cream mat
    d.ellipse([454, 160, 471, 184], fill=hx("4a3e2c"), outline=hx("8a7448"))
    d.ellipse([456, 162, 469, 178], fill=hx("524432"))  # the studio backdrop, lighter behind the head
    sitter = Image.new("RGBA", img.size, (0, 0, 0, 0))
    s_ = ImageDraw.Draw(sitter)
    skin, skin_d, hair = hx("c8a484"), hx("9a7860"), hx("b8b0a0")
    # broad shoulders in a dark frock coat, white wing collar and a black cravat
    s_.polygon([(455, 184), (456, 178), (459, 175), (466, 175), (469, 178), (470, 184)], fill=hx("1e1a16"))
    s_.line([(459, 176), (461, 183)], fill=hx("3a322a"))  # lapels
    s_.line([(466, 176), (464, 183)], fill=hx("3a322a"))
    s_.polygon([(461, 174), (464, 174), (465, 177), (462, 179), (460, 177)], fill=hx("e8e0d0"))
    s_.rectangle([462, 176, 463, 178], fill=hx("141010"))
    s_.point((466, 181), fill=hx("c8a050"))  # watch chain
    s_.line([(466, 181), (468, 182)], fill=hx("a88a40"))
    # neck and head: receding grey hair, ears, heavy brows, mutton-chop whiskers and a moustache
    s_.rectangle([461, 172, 464, 174], fill=skin_d)
    s_.ellipse([459, 164, 466, 174], fill=skin)
    s_.point((458, 169), fill=skin_d)
    s_.point((467, 169), fill=skin_d)
    s_.line([(460, 164), (465, 164)], fill=hair)
    s_.point((459, 165), fill=hair)
    s_.point((466, 165), fill=hair)
    s_.line([(460, 167), (461, 167)], fill=hx("6a6258"))  # brows
    s_.line([(464, 167), (465, 167)], fill=hx("6a6258"))
    s_.point((460, 168), fill=hx("2a1a14"))
    s_.point((465, 168), fill=hx("2a1a14"))
    s_.line([(462, 168), (462, 170)], fill=skin_d)  # nose
    s_.line([(459, 169), (459, 173)], fill=hair)  # whiskers down the cheeks
    s_.line([(466, 169), (466, 173)], fill=hair)
    s_.line([(460, 171), (465, 171)], fill=hx("d8d0c0"))  # moustache
    s_.line([(461, 173), (464, 173)], fill=hx("8a6a58"))  # the thin, disapproving mouth
    s_.point((465, 166), fill=hx("e0c0a0"))  # light from the bulb
    clip = Image.new("L", img.size, 0)
    ImageDraw.Draw(clip).ellipse([455, 161, 470, 183], fill=255)
    oval.paste(sitter, (0, 0), ImageChops.multiply(sitter.getchannel("A"), clip))
    for (cx, cy) in ((452, 160), (471, 158), (472, 183), (454, 185)):
        d.point((cx, cy), fill=hx("a88a40"))
    img.paste(oval, (0, -8), oval)


def clutter(img):
    d = ImageDraw.Draw(img)
    dress_form(img)
    radio(img)
    portraits(img)
    # a hat box tucked under the left eave
    hat_box(img)
    # Pendant socket; the emissive glass is painted after the room's colour grade.
    d.line([(260, 0), (260, 28)], fill=hx("1a1410"))
    d.rectangle([257, 27, 263, 31], fill=hx("3a3028"))
    d.line([(266, 29), (268, 49)], fill=hx("9a8a70"))
    d.ellipse([267, 49, 269, 52], fill=hx("6a5038"))


def hanging_bulb(img):
    light(img, "ellipse", [246, 20, 274, 52], hx("ffd080"), 0.48, 6)
    d = ImageDraw.Draw(img)
    d.rectangle([257, 27, 263, 31], fill=hx("504438"))
    d.line([(258, 28), (262, 28)], fill=hx("a89870"))
    d.ellipse([255, 31, 265, 41], fill=hx("ffda8a"), outline=hx("e0ad58"))
    d.ellipse([257, 32, 263, 39], fill=hx("fff8dc"))
    d.line([(259, 34), (261, 36), (259, 37)], fill=hx("ffffff"))


def bulb_pool(img):
    light(img, "ellipse", [140, -40, 380, 170], hx("ffc878"), 0.22, 28)
    light(img, "polygon", [(254, 38), (266, 38), (420, 250), (100, 250)], hx("e8ac60"), 0.22, 26)
    light(img, "ellipse", [140, 170, 380, 254], hx("ffd090"), 0.2, 26)


# the tool tin's enamel and brass, and the dark inside the opened box: too small to survive the median cut
DAY_EXTRA = [hx(c) for c in ("e8705a", "d4523e", "c03a2c", "a42c22", "8a2218", "5a1610", "e0b850", "241a10")]
NIGHT_EXTRA = [hx(c) for c in ("fff8d8", "ffe0a0", "ffd890", "f0b860", "d89848", "d88a3a", "c87830", "a86a2a",
                                 "8a5a24", "e8e8d0", "c8c8b4", "6a7898")]
LAMP = dict(x=268, base=182, shade_top=112, shade_bot=128, top_w=8, bot_w=15)


def night_glass(img):
    """The round window at night: deep blue sky, a few stars, the moon behind the bare maple."""
    cx, cy, r = 260, 80, 19
    glass = Image.new("RGB", img.size)
    vgrad(glass, (cx - r, cy - r, cx + r, cy + r), hx("0c1430"), hx("1c2a4c"))
    gd = ImageDraw.Draw(glass)
    for (sx, sy) in ((cx - 13, cy - 6), (cx + 4, cy - 14), (cx + 13, cy - 3), (cx - 5, cy - 2)):
        gd.point((sx, sy), fill=hx("c8d0e8"))
    mx, my = cx + 8, cy - 9
    gd.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=hx("e8e8d0"))
    gd.ellipse([mx - 3, my - 3, mx - 1, my - 1], fill=hx("c8c8b4"))
    gd.ellipse([mx + 1, my + 1, mx + 4, my + 3], fill=hx("ccccb8"))
    light(glass, "ellipse", [mx - 14, my - 14, mx + 14, my + 14], hx("8090b8"), 0.35, 5)
    for (lx, ly, lr) in ((cx - 12, cy + 8, 9), (cx + 8, cy + 12, 11), (cx - 2, cy + 18, 8)):
        gd.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=hx("0a0e18"))
    gd.line([(cx - 4, cy + 20), (cx - 2, cy + 4), (cx + 6, cy - 4)], fill=hx("0a0e18"), width=2)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(glass, (0, 0), m)
    d = ImageDraw.Draw(img)
    frame = hx("1e1812")
    d.line([(cx - r, cy), (cx + r, cy)], fill=frame, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=frame, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=frame, width=2)
    d.line([(cx - 10, cy - 12), (cx - 4, cy - 15)], fill=hx("6a7898"))


def lamp(img, lit=True):
    """An old standard lamp; the ceiling pendant supplies the light when it is off."""
    d = ImageDraw.Draw(img)
    L = LAMP
    x, st, sb, tw, bw = L["x"], L["shade_top"], L["shade_bot"], L["top_w"], L["bot_w"]
    shadow(img, "ellipse", [x - 14, L["base"] - 3, x + 16, L["base"] + 3], 0.5, 2)
    d.ellipse([x - 8, L["base"] - 3, x + 8, L["base"] + 1], fill=hx("2a1c10"))
    d.ellipse([x - 7, L["base"] - 4, x + 7, L["base"]], fill=hx("6a4a24"))
    d.line([(x, L["base"] - 3), (x, sb)], fill=hx("2a1c10"), width=3)
    d.line([(x - 1, L["base"] - 3), (x - 1, sb)], fill=hx("b08a48"))
    d.ellipse([x - 2, 158, x + 2, 161], fill=hx("8a6a30"))
    # the bulb glows under the shade's lower rim
    d.ellipse([x - 4, sb - 2, x + 4, sb + 4], fill=hx("fff8d8") if lit else hx("9a8058"))
    shade = [(x - tw, st), (x + tw, st), (x + bw, sb), (x - bw, sb)]
    d.polygon(shade, fill=hx("f0b860"))
    tmp = Image.new("RGB", img.size)
    hgrad(tmp, (x - bw, st, x + bw, sb), hx("d88a3a") if lit else hx("8a6842"), hx("ffd890") if lit else hx("c8a878"))
    hgrad(tmp, (x, st, x + bw, sb), hx("ffe0a0") if lit else hx("c8a878"), hx("c87830") if lit else hx("8a6842"))
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).polygon(shade, fill=255)
    img.paste(tmp, (0, 0), m)
    for k in range(-3, 4):
        d.line([(x + k * tw / 4, st + 1), (x + k * bw / 4, sb - 1)], fill=hx("d89848"))
    d.line([(x - tw, st), (x + tw, st)], fill=hx("8a5a24"))
    d.line([(x - bw, sb), (x + bw, sb)], fill=hx("a86a2a"), width=2)
    for k in (-10, -4, 2, 8):  # fringe
        d.line([(x + k, sb + 1), (x + k, sb + 3)], fill=hx("c88a3a"))
    if lit:
        light(img, "ellipse", [x - 22, st - 10, x + 22, sb + 12], hx("ffd890"), 0.35, 6)


def relight_night(img):
    """The ceiling bulb illuminates the gable and floor; moonlight remains secondary."""
    x, sb = 260, 36
    dark = ImageChops.multiply(img, Image.new("RGB", img.size, (62, 70, 112)))
    warm = ImageChops.multiply(img, Image.new("RGB", img.size, (255, 206, 140)))
    warm = ImageChops.screen(warm, Image.new("RGB", img.size, (34, 18, 4)))
    m = Image.new("L", img.size, 0)
    md = ImageDraw.Draw(m)
    md.ellipse([x - 230, -70, x + 230, 280], fill=150)
    m = m.filter(ImageFilter.GaussianBlur(32))
    core = Image.new("L", img.size, 0)
    cd = ImageDraw.Draw(core)
    cd.ellipse([x - 95, -40, x + 95, 148], fill=220)
    cd.polygon([(x - 8, sb), (x + 8, sb), (x + 160, 250), (x - 160, 250)], fill=200)
    cd.ellipse([x - 130, 178, x + 130, 246], fill=180)
    core = core.filter(ImageFilter.GaussianBlur(26))
    m = ImageChops.lighter(m, core)
    hatch_glow = Image.new("L", img.size, 0)
    ImageDraw.Draw(hatch_glow).polygon([(14, 236), (96, 236), (102, 270), (6, 270)], fill=230)
    ImageDraw.Draw(hatch_glow).ellipse([-10, 196, 120, 280], fill=90)
    m = ImageChops.lighter(m, hatch_glow.filter(ImageFilter.GaussianBlur(8)))
    out = Image.composite(warm, dark, m)
    # cool moonlight falling through the round window
    light(out, "polygon", [(246, 72), (276, 72), (330, 266), (186, 266)], hx("5068a8"), 0.1, 8)
    return out


def paint(act=1, spill=False, lifted=False, opened=False, box_open=False, suitcase_open=False):
    if act == "night":
        return paint_night(spill, lifted, opened, box_open, suitcase_open)
    mood = ACTS[act]
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img, act)
    clutter(img)
    boxes(img, box_open)
    sheet_furniture(img, lifted)
    suitcase(img, suitcase_open)
    trunk(img, opened)
    if spill:
        spilled(img)
    hatch(img)
    shaft(img, act)
    if mood["desat"] > 0:
        grey = img.convert("L").convert("RGB")
        img = Image.blend(img, grey, mood["desat"])
    if mood["room_tint"] is not None:
        shadow(img, "rect", [0, 0, W - 1, H - 1], 0.12 if act == 2 else 0.18, 18 if act == 2 else 24,
               tint=mood["room_tint"])
    bulb_pool(img)
    vignette(img, mood["vignette_k"], tint=mood["vignette_tint"], blur=mood["vignette_blur"])
    hanging_bulb(img)
    return img


def paint_night(spill=False, lifted=False, opened=False, box_open=False, suitcase_open=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img, 1)
    clutter(img)
    boxes(img, box_open)
    sheet_furniture(img, lifted)
    suitcase(img, suitcase_open)
    trunk(img, opened)
    if spill:
        spilled(img)
    hatch(img)
    img = relight_night(img)
    bulb_pool(img)
    night_glass(img)
    lamp(img, lit=False)
    vignette(img, 0.7, tint=(14, 14, 32), blur=46)
    hanging_bulb(img)
    return img


def build():
    act1 = paint(1)
    act1_alt = paint(1, True, True, True, True, True)
    pal = palette_of(_side_by_side(act1, act1_alt), 128) + DAY_EXTRA

    outputs = {}
    for act in (1, 2, 3):
        px = pixelize(paint(act), pal)
        outputs[act] = px
        save(px, "rooms", f"attic_act{act}.png")
        if act == 1:
            save(px, "rooms", "attic.png")

    overlay_boxes = (("attic_papers", SPILL_BOX), ("attic_chair", SHEET_BOX), ("attic_trunk_open", TRUNK_BOX),
                     ("attic_box_open", BOX_OPEN_BOX), ("attic_suitcase_open", SUITCASE_BOX))
    for act in (1, 2, 3):
        alt = pixelize(paint(act, True, True, True, True, True), pal)
        shut = pixelize(paint(act, True, True, True, True, False), pal)
        for name, box in overlay_boxes:
            suffix = "" if act == 1 else f"_act{act}"
            save(_overlay(alt, shut, name, box), "rooms", f"{name}{suffix}.png")

    night, night_alt = paint("night"), paint("night", True, True, True, True, True)
    night_pal = palette_of(_side_by_side(night, night_alt), 116) + NIGHT_EXTRA + DAY_EXTRA[3:6]
    save(pixelize(night, night_pal), "rooms", "attic_night.png")
    night_shut = pixelize(paint("night", True, True, True, True, False), night_pal)
    night_alt = pixelize(night_alt, night_pal)
    for name, box in overlay_boxes:
        save(_overlay(night_alt, night_shut, name, box), "rooms", f"{name}_night.png")
    return outputs[1]


def _overlay(alt, shut, name, box):
    """Crops an overlay. The open suitcase's lid rises into the chair's crop, so its overlay keeps only the pixels
    that opening the suitcase changes and is transparent elsewhere."""
    crop = alt.crop(box)
    if name != "attic_suitcase_open":
        return crop
    diff = ImageChops.difference(crop.convert("RGB"), shut.crop(box).convert("RGB")).convert("L")
    mask = diff.point(lambda v: 255 if v else 0)
    out = crop.convert("RGBA")
    out.putalpha(mask)
    return out


def _side_by_side(a, b):
    """Both states in one image, so the palette keeps the overlay colours (the red tin) unblended."""
    out = Image.new("RGB", (a.width * 2, a.height))
    out.paste(a, (0, 0))
    out.paste(b, (a.width, 0))
    return out
