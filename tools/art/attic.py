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
SHEET_BOX = (108, 118, 204, 196)
TRUNK_BOX = (388, 150, 476, 236)

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
    for x in (34, 74):
        d.line([(x, 212), (x - 2, 266)], fill=WOOD_D, width=4)
        d.line([(x, 212), (x - 2, 266)], fill=WOOD_L, width=2)
    for y in (220, 232, 246, 258):
        d.line([(34, y), (74, y)], fill=WOOD, width=3)
        d.line([(34, y - 1), (74, y - 1)], fill=WOOD_L)
    d.rectangle([8, 232, 18, 266], fill=hx("4a3828"))  # open trapdoor lid against the wall
    light(img, "ellipse", [0, 200, 120, 270], hx("ffd8a0"), 0.25, 12)


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
    else:
        # a rocking chair, and the sheet in a heap beside it
        for x in (128, 172):
            d.line([(x, 132), (x + 2, 184)], fill=hx("4a3020"), width=3)
        for y in range(136, 160, 6):
            d.line([(128, y), (172, y)], fill=hx("5a3a24"), width=2)
        d.rectangle([124, 160, 178, 166], fill=hx("6a4a30"))
        d.arc([110, 170, 196, 200], 200, 340, fill=hx("3a2416"), width=3)
        for x in (130, 172):
            d.line([(x, 166), (x - 2, 186)], fill=hx("4a3020"), width=2)
        d.polygon([(178, 194), (182, 180), (196, 176), (204, 184), (202, 194)], fill=hx("c8c0b0"))
        d.line([(186, 180), (192, 192)], fill=hx("a8a090"))
    shadow(img, "ellipse", [110, 186, 206, 198], 0.45, 3)


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
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 396, 190, 468, 230
    shadow(img, "rect", [x0 - 2, y1 - 2, x1 + 6, y1 + 6], 0.5, 3)
    d.rectangle([x0, y0, x1, y1], fill=hx("3a4a3a"))
    d.rectangle([x0, y0, x1, y1], outline=hx("1a2018"))
    for x in (x0 + 16, x1 - 16):
        d.rectangle([x - 2, y0, x + 2, y1], fill=hx("6a4a2a"))
    for (cx, cy) in ((x0, y0), (x1 - 5, y0), (x0, y1 - 5), (x1 - 5, y1 - 5)):
        d.rectangle([cx, cy, cx + 5, cy + 5], fill=hx("b8964a"))
    # travel labels
    d.ellipse([x0 + 22, y0 + 8, x0 + 34, y0 + 18], fill=hx("c8b080"))
    d.rectangle([x1 - 30, y0 + 20, x1 - 20, y0 + 28], fill=hx("a84030"))
    if not opened:
        d.rectangle([x0, y0 - 10, x1, y0], fill=hx("44543e"))
        d.line([(x0, y0 - 10), (x1, y0 - 10)], fill=hx("6a7a5a"))
        d.line([(x0, y0), (x1, y0)], fill=hx("1a2018"))
        for x in (x0 + 16, x1 - 16):
            d.rectangle([x - 2, y0 - 10, x + 2, y0], fill=hx("6a4a2a"))
        d.rectangle([(x0 + x1) // 2 - 4, y0 - 4, (x0 + x1) // 2 + 4, y0 + 6], fill=hx("8a6a30"))
        d.ellipse([(x0 + x1) // 2 - 2, y0 + 1, (x0 + x1) // 2 + 2, y0 + 5], fill=hx("2a1a0a"))
    else:
        # lid thrown back against the wall, the dark inside, an old fedora
        d.polygon([(x0, y0), (x1, y0), (x1 + 2, y0 - 36), (x0 - 2, y0 - 36)], fill=hx("44543e"))
        d.polygon([(x0 + 4, y0 - 2), (x1 - 4, y0 - 2), (x1 - 2, y0 - 32), (x0 + 2, y0 - 32)], fill=hx("6a3a3a"))
        d.polygon([(x0 + 2, y0), (x1 - 2, y0), (x1 - 4, y0 + 8), (x0 + 4, y0 + 8)], fill=hx("1a1210"))
        d.ellipse([x0 + 10, y0 + 1, x0 + 34, y0 + 7], fill=hx("3a3028"))
        d.rectangle([x0 + 15, y0 - 4, x0 + 29, y0 + 3], fill=hx("4a3a30"))
        d.line([(x0 + 15, y0 + 1), (x0 + 29, y0 + 1)], fill=hx("1a1010"))
        d.rectangle([(x0 + x1) // 2 - 4, y0 + 2, (x0 + x1) // 2 + 4, y0 + 8], fill=hx("6a5a30"))


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
    """A cathedral radio on a fruit crate: gothic fretwork over the grille cloth, a dial and three knobs."""
    d = ImageDraw.Draw(img)
    # crate
    d.rectangle([40, 196, 88, 226], fill=hx("6a5038"), outline=hx("3a2a1c"))
    for y in (203, 211, 219):
        d.line([(41, y), (87, y)], fill=hx("3a2a1c"))
        d.line([(41, y + 1), (87, y + 1)], fill=hx("8a6c4c"))
    for x in (43, 85):
        d.line([(x, 197), (x, 225)], fill=hx("4a3828"), width=2)
        for y in (199, 207, 215, 223):
            d.point((x, y), fill=hx("a89070"))
    d.rectangle([86, 196, 88, 226], fill=hx("806448"))
    shadow(img, "rect", [44, 194, 90, 200], 0.4, 2)
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


def suitcase(img):
    """A battered leather suitcase lying against the left knee wall."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 4, 189, 32, 207
    tb = (x1 + 6, y0 - 4)
    shadow(img, "rect", [x0, y1 - 2, x1 + 8, y1 + 3], 0.5, 2)
    d.polygon([(x1, y0), tb, (tb[0], y1 - 3), (x1, y1)], fill=hx("9a5a40"), outline=hx("2a1a10"))
    d.polygon([(x0, y0), (x1, y0), tb, (x0 + 6, y0 - 4)], fill=hx("a86a4a"), outline=hx("2a1a10"))
    hgrad(img, (x0, y0, x1, y1), hx("4a2418"), hx("7e4430"))
    d.rectangle([x0, y0, x1, y1], outline=hx("2a1a10"))
    # lid seam, straps with buckles, brass corner caps, a handle and a hotel sticker
    d.line([(x0 + 1, y0 + 5), (x1 - 1, y0 + 5)], fill=hx("2a1a10"))
    d.line([(x0 + 1, y0 + 6), (x1 - 1, y0 + 6)], fill=hx("9a5a40"))
    for sx in (x0 + 7, x1 - 8):
        d.rectangle([sx, y0, sx + 2, y1], fill=hx("3a2014"))
        d.line([(sx + 3 + (tb[0] - x1) * (sx - x0) // (x1 - x0) // 2, y0 - 3), (sx + 1, y0)], fill=hx("3a2014"), width=2)
        d.rectangle([sx - 1, y0 + 4, sx + 3, y0 + 7], outline=hx("d8b060"))
    for (cx, cy) in ((x0, y0), (x1 - 2, y0), (x0, y1 - 2), (x1 - 2, y1 - 2)):
        d.rectangle([cx, cy, cx + 2, cy + 2], fill=hx("c8a050"))
    d.line([(14, y0 - 2), (15, y0 - 4), (21, y0 - 4), (22, y0 - 2)], fill=hx("1e120a"), width=2)
    d.ellipse([20, y0 + 9, 27, y0 + 15], fill=hx("e0d0a8"))
    d.line([(20, y0 + 12), (27, y0 + 12)], fill=hx("b03828"), width=2)
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("a86a4a"))


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


def clutter(img):
    d = ImageDraw.Draw(img)
    dress_form(img)
    radio(img)
    # paintings leaning on the right knee wall
    d.polygon([(418, 150), (452, 146), (456, 186), (420, 188)], fill=hx("a08040"))
    d.polygon([(422, 154), (449, 150), (452, 182), (424, 184)], fill=hx("2a3a4a"))
    d.ellipse([430, 158, 444, 174], fill=hx("6a7a7a"))
    d.polygon([(448, 156), (474, 154), (476, 186), (450, 188)], fill=hx("5a3a20"))
    # a suitcase and a hat box tucked under the left eave
    suitcase(img)
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


def paint(act=1, spill=False, lifted=False, opened=False, box_open=False):
    if act == "night":
        return paint_night(spill, lifted, opened, box_open)
    mood = ACTS[act]
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img, act)
    clutter(img)
    boxes(img, box_open)
    sheet_furniture(img, lifted)
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


def paint_night(spill=False, lifted=False, opened=False, box_open=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img, 1)
    clutter(img)
    boxes(img, box_open)
    sheet_furniture(img, lifted)
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
    act1_alt = paint(1, True, True, True, True)
    pal = palette_of(_side_by_side(act1, act1_alt), 128) + DAY_EXTRA

    outputs = {}
    for act in (1, 2, 3):
        px = pixelize(paint(act), pal)
        outputs[act] = px
        save(px, "rooms", f"attic_act{act}.png")
        if act == 1:
            save(px, "rooms", "attic.png")

    overlay_boxes = (("attic_papers", SPILL_BOX), ("attic_chair", SHEET_BOX), ("attic_trunk_open", TRUNK_BOX),
                     ("attic_box_open", BOX_OPEN_BOX))
    for act in (1, 2, 3):
        alt = pixelize(paint(act, True, True, True, True), pal)
        for name, box in overlay_boxes:
            suffix = "" if act == 1 else f"_act{act}"
            save(alt.crop(box), "rooms", f"{name}{suffix}.png")

    night, night_alt = paint("night"), paint("night", True, True, True, True)
    night_pal = palette_of(_side_by_side(night, night_alt), 116) + NIGHT_EXTRA + DAY_EXTRA[3:6]
    save(pixelize(night, night_pal), "rooms", "attic_night.png")
    night_alt = pixelize(night_alt, night_pal)
    for name, box in overlay_boxes:
        save(night_alt.crop(box), "rooms", f"{name}_night.png")
    return outputs[1]


def _side_by_side(a, b):
    """Both states in one image, so the palette keeps the overlay colours (the red tin) unblended."""
    out = Image.new("RGB", (a.width * 2, a.height))
    out.paste(a, (0, 0))
    out.paste(b, (a.width, 0))
    return out
