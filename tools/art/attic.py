"""Present day: the dusty attic of an old family house, lit by a round gable window."""
from PIL import Image, ImageDraw
import random
from .common import (W, FULL_H, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, save, floor_boards)

H = FULL_H
VP = (260, 95)  # vanishing point; the attic recedes towards the gable wall
BACK = dict(x0=110, x1=410, eave=130, floor=178, apex=(260, 26))
WOOD, WOOD_D, WOOD_L = hx("6a5440"), hx("3a2c20"), hx("8a7258")
DUST = hx("f0d8a0")

# crops for the flag-driven overlays (x0, y0, x1, y1)
SPILL_BOX = (262, 184, 390, 222)
SHEET_BOX = (108, 118, 204, 196)
TRUNK_BOX = (388, 150, 476, 236)


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


def window(img):
    d = ImageDraw.Draw(img)
    cx, cy, r = 260, 80, 19
    d.ellipse([cx - r - 5, cy - r - 5, cx + r + 5, cy + r + 5], fill=WOOD_D)
    d.ellipse([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], fill=hx("8a7a64"))
    glass = Image.new("RGB", img.size)
    vgrad(glass, (cx - r, cy - r, cx + r, cy + r), hx("e8f0f8"), hx("b8d0e0"))
    gd = ImageDraw.Draw(glass)
    # the neighbour's maple outside, in autumn
    for (lx, ly, lr, col) in ((cx - 12, cy + 6, 9, hx("c86a2a")), (cx + 8, cy + 10, 11, hx("d8902a")),
                              (cx - 2, cy + 16, 8, hx("a8501e"))):
        gd.ellipse([lx - lr, ly - lr, lx + lr, ly + lr], fill=col)
    m = Image.new("L", img.size, 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(glass, (0, 0), m)
    # mullions
    d.line([(cx - r, cy), (cx + r, cy)], fill=WOOD_D, width=2)
    d.line([(cx, cy - r), (cx, cy + r)], fill=WOOD_D, width=2)
    d.arc([cx - r, cy - r, cx + r, cy + r], 0, 360, fill=WOOD_D, width=2)
    d.line([(cx - 10, cy - 12), (cx - 4, cy - 15)], fill=hx("ffffff"))


def shaft(img, seed=5):
    """Afternoon sunlight pouring through the round window, full of dust motes."""
    pts = [(246, 72), (276, 72), (322, 266), (178, 266)]
    light(img, "polygon", pts, hx("ffe0a0"), 0.32, 6)
    light(img, "ellipse", [196, 220, 322, 270], hx("ffd890"), 0.35, 10)
    light(img, "ellipse", [200, 40, 320, 120], hx("fff0d0"), 0.25, 18)
    d = ImageDraw.Draw(img)
    rnd = random.Random(seed)
    for _ in range(70):
        y = rnd.uniform(80, 250)
        t = (y - 72) / 194
        x0, x1 = 246 + (178 - 246) * t, 276 + (322 - 276) * t
        x = rnd.uniform(x0 + 3, x1 - 3)
        d.point((x, y), fill=DUST if rnd.random() < 0.7 else hx("ffffff"))


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


def boxes(img):
    d = ImageDraw.Draw(img)
    stack = ((296, 152, 344, 190, "TAXES 87-94"), (336, 160, 376, 190, "XMAS"), (302, 120, 340, 152, "MISC"),
             (338, 136, 368, 160, ""))
    for (x0, y0, x1, y1, label) in stack:
        d.rectangle([x0, y0, x1, y1], fill=hx("a08458"))
        d.rectangle([x0, y0, x1, y0 + 3], fill=hx("b89a68"))
        d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y0 + 3)], fill=hx("6a5434"))
        d.rectangle([x0, y0, x1, y1], outline=hx("5a4428"))
        d.line([(x1 - 1, y0), (x1 - 1, y1)], fill=hx("806640"))
        if label:
            text(img, ((x0 + x1) // 2, (y0 + y1) // 2 + 2), label, hx("2a2a3a"), size=8)
    shadow(img, "rect", [294, 186, 380, 194], 0.4, 3)
    d.polygon([(304, 118), (318, 114), (322, 120)], fill=hx("e8e0d0"))  # paper peeking out


def spilled(img):
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


def clutter(img):
    d = ImageDraw.Draw(img)
    # dress form
    d.ellipse([214, 124, 236, 150], fill=hx("8a6a6a"))
    d.polygon([(216, 140), (234, 140), (238, 170), (212, 170)], fill=hx("7a5a5a"))
    d.line([(225, 170), (225, 190)], fill=hx("2a1e14"), width=2)
    d.line([(216, 192), (234, 192)], fill=hx("2a1e14"), width=2)
    d.rectangle([222, 118, 228, 124], fill=hx("2a1e14"))
    d.line([(214, 146), (236, 146)], fill=hx("c8b080"))
    # cathedral radio on a crate, against the left knee wall
    d.rectangle([40, 196, 88, 226], fill=hx("6a5038"), outline=hx("3a2a1c"))
    d.line([(40, 210), (88, 210)], fill=hx("4a3828"))
    d.rectangle([48, 168, 80, 196], fill=hx("5a3418"))
    d.chord([48, 156, 80, 182], 180, 360, fill=hx("5a3418"))
    d.chord([53, 162, 75, 186], 180, 360, fill=hx("c8a868"))
    for x in range(56, 74, 3):
        d.line([(x, 166), (x, 182)], fill=hx("6a4a28"))
    d.ellipse([56, 186, 62, 192], fill=hx("c8a050"))
    d.ellipse([66, 186, 72, 192], fill=hx("c8a050"))
    # paintings leaning on the right knee wall
    d.polygon([(418, 150), (452, 146), (456, 186), (420, 188)], fill=hx("a08040"))
    d.polygon([(422, 154), (449, 150), (452, 182), (424, 184)], fill=hx("2a3a4a"))
    d.ellipse([430, 158, 444, 174], fill=hx("6a7a7a"))
    d.polygon([(448, 156), (474, 154), (476, 186), (450, 188)], fill=hx("5a3a20"))
    # suitcases and a hat box tucked under the left eave
    d.rectangle([4, 186, 36, 206], fill=hx("6a3a2a"), outline=hx("2a1a10"))
    d.line([(14, 184), (26, 184)], fill=hx("2a1a10"), width=2)
    d.ellipse([86, 176, 108, 190], fill=hx("8a3a4a"))
    d.rectangle([86, 170, 108, 183], fill=hx("8a3a4a"))
    d.ellipse([86, 164, 108, 176], fill=hx("a84a5a"))
    # unlit bulb hanging from the ridge
    d.line([(260, 0), (260, 28)], fill=hx("1a1410"))
    d.ellipse([256, 28, 264, 37], fill=hx("c8c4b0"))
    d.line([(262, 36), (264, 52)], fill=hx("c8c4b0"))


def paint(spill=False, lifted=False, opened=False):
    img = Image.new("RGB", (W, H))
    shell(img)
    floor(img)
    window(img)
    clutter(img)
    boxes(img)
    sheet_furniture(img, lifted)
    trunk(img, opened)
    if spill:
        spilled(img)
    hatch(img)
    shaft(img)
    vignette(img, 0.5, tint=(40, 30, 30))
    return img


def build():
    base = paint()
    pal = palette_of(Image.blend(base, paint(True, True, True), 0.5), 128)
    px = pixelize(base, pal)
    save(px, "rooms", "attic.png")
    alt = pixelize(paint(True, True, True), pal)
    for name, box in (("attic_papers", SPILL_BOX), ("attic_chair", SHEET_BOX), ("attic_trunk_open", TRUNK_BOX)):
        save(alt.crop(box), "rooms", f"{name}.png")
    return px
