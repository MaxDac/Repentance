"""The Aurelian, room 507: the room Eleanor had the night she vanished. Luxurious, lived in, and turned upside down.

Overlays: the closet thrown open (with the wall safe), the safe door open, the brass box inside it, and the
lockpicked desk drawer with the slip of paper."""
from PIL import Image, ImageDraw, ImageChops
from .common import W, H, TOP, tall, hx, mul, vgrad, noise, light, shadow, vignette, pixelize, palette_of, save, city
from . import hotel
from .hotel import R, WOOD, WOOD_D, GOLD, GOLD_D, GREEN, GREEN_L, BURGUNDY, BURGUNDY_L

STEEL, STEEL_D, STEEL_L = hx("4a4c52"), hx("2a2c30"), hx("70747c")
DESK_X0, DESK_X1, DESK_Z0, DESK_Z1 = 154, 232, 2, 26
CL_X0, CL_X1, CL_Z0, CL_Z1 = 72, 124, 2, 26
SAFE_X0, SAFE_X1, SAFE_Y0, SAFE_Y1, SAFE_Z = 84, 112, 8, 34, 4


def window_night(img):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 156, 28, 230, 100
    city(img, (x0, y0, x1, y1), seed=507, lit=0.3)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 5], outline=WOOD_D, width=4)
    d.line([((x0 + x1) // 2, y0), ((x0 + x1) // 2, y1)], fill=WOOD_D, width=3)
    d.line([(x0, 60), (x1, 60)], fill=WOOD_D, width=2)
    d.rectangle([x0 - 8, y1 + 4, x1 + 8, y1 + 7], fill=hx("8c6748"))
    # one drape torn down from its rail, the other still hanging
    d.polygon([(x1 + 16, y0 - 8), (x1 - 6, y0 - 4), (x1 - 2, y0 + 44), (x1 - 8, y1 + 30), (x1 + 16, y1 + 32)], fill=BURGUNDY)
    for x in (x1 + 6, x1 + 12):
        d.line([(x, y0 - 4), (x, y1 + 28)], fill=mul(BURGUNDY, 0.72))
    d.rectangle([x0 - 20, y0 - 12, x1 + 20, y0 - 6], fill=GOLD_D)
    d.line([(x0 - 20, y0 - 12), (x1 + 20, y0 - 12)], fill=GOLD)
    d.line([(x0 - 20, y0 - 6), (x0 - 10, y0 + 8)], fill=GOLD_D, width=2)


def crooked_painting(img):
    d = ImageDraw.Draw(img)
    # the landscape above the bed, knocked askew
    d.rectangle([294, 28, 354, 64], fill=hotel.CREAM)
    d.polygon([(298, 30), (354, 36), (350, 68), (294, 62)], fill=GOLD_D)
    d.polygon([(300, 33), (351, 38), (348, 65), (297, 60)], fill=GOLD)
    d.polygon([(302, 35), (349, 40), (346, 62), (299, 58)], fill=hx("a69374"))
    d.polygon([(300, 56), (314, 44), (330, 49), (347, 42), (346, 61)], fill=hx("617367"))


def closet(img, opened=False, safe_open=False, box=False):
    X0, X1, Z0, Z1 = CL_X0, CL_X1, CL_Z0, CL_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0] - 2, a[1] - 3, b[0] + 10, a[1] + 3], 0.4, 3)
    R.box(img, X0, X1, 3, 104, Z0, Z1, mul(WOOD, 0.95), top=WOOD, side=hx("4c2f1a"))
    R.box(img, X0 - 2, X1 + 2, 104, 112, Z0, Z1 + 2, WOOD, top=hx("8a5e3c"), side=hx("4c2f1a"))
    R.box(img, X0 + 1, X1 - 1, 0, 3, Z0, Z1 - 1, WOOD_D)
    xm = (X0 + X1) / 2
    if not opened:
        for (c, e) in ((X0 + 3, xm - 1), (xm + 1, X1 - 3)):
            R.quad(img, [(c, 6, Z1), (e, 6, Z1), (e, 100, Z1), (c, 100, Z1)], hx("75492b"), hx("3e2615"))
            R.quad(img, [(c + 4, 12, Z1), (e - 4, 12, Z1), (e - 4, 94, Z1), (c + 4, 94, Z1)], None, hx("8e6040"))
        for x in (xm - 3, xm + 3):
            R.line(img, (x, 52, Z1), (x, 60, Z1), GOLD, 2)
        R.line(img, (xm, 6, Z1), (xm, 100, Z1), WOOD_D)
        # a sleeve caught in the doors
        R.quad(img, [(xm - 1, 40, Z1 + 0.5), (xm + 6, 36, Z1 + 1), (xm + 9, 18, Z1 + 3), (xm + 4, 20, Z1 + 3)], hx("b88aa0"))
        return
    # cavity, hanging rail and what's left on the hangers
    R.quad(img, [(X0 + 3, 4, Z1), (X1 - 3, 4, Z1), (X1 - 3, 100, Z1), (X0 + 3, 100, Z1)], hx("1e140c"))
    R.quad(img, [(X0 + 3, 4, Z0 + 2), (X1 - 3, 4, Z0 + 2), (X1 - 3, 100, Z0 + 2), (X0 + 3, 100, Z0 + 2)], hx("2a1a10"))
    R.line(img, (X0 + 4, 88, Z0 + 12), (X1 - 4, 88, Z0 + 12), GOLD_D, 2)
    for i, (x, col) in enumerate(((X0 + 10, hx("b88aa0")), (X0 + 22, hx("2a2a3a")), (X1 - 12, hx("d8c8b0")))):
        R.line(img, (x, 88, Z0 + 12), (x, 84, Z0 + 12), STEEL_L)
        R.quad(img, [(x - 4, 84, Z0 + 12), (x + 4, 84, Z0 + 12), (x + 6 - i, 44 + i * 6, Z0 + 12), (x - 6 + i, 44 + i * 6, Z0 + 12)], col)
    # clothes yanked off their hangers, heaped at the bottom
    R.quad(img, [(X0 + 4, 4, Z1 - 4), (X0 + 20, 12, Z1 - 6), (X0 + 26, 4, Z1 - 2)], hx("6a4a6a"))
    # wall safe set into the back
    R.quad(img, [(SAFE_X0 - 2, SAFE_Y0 - 2, SAFE_Z), (SAFE_X1 + 2, SAFE_Y0 - 2, SAFE_Z), (SAFE_X1 + 2, SAFE_Y1 + 2, SAFE_Z),
                 (SAFE_X0 - 2, SAFE_Y1 + 2, SAFE_Z)], STEEL_D)
    if not safe_open:
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z + 0.5), (SAFE_X1, SAFE_Y0, SAFE_Z + 0.5), (SAFE_X1, SAFE_Y1, SAFE_Z + 0.5),
                     (SAFE_X0, SAFE_Y1, SAFE_Z + 0.5)], STEEL, STEEL_L)
        cx, cy = R.P((SAFE_X0 + SAFE_X1) / 2, (SAFE_Y0 + SAFE_Y1) / 2, SAFE_Z + 1)
        d = ImageDraw.Draw(img)
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=STEEL_D, outline=GOLD)
        d.line([(cx, cy - 4), (cx, cy - 1)], fill=GOLD)
        hx_, hy = R.P(SAFE_X1 - 4, (SAFE_Y0 + SAFE_Y1) / 2, SAFE_Z + 1)
        d.line([(hx_, hy - 3), (hx_, hy + 3)], fill=STEEL_L, width=2)
    else:
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z - 0.5), (SAFE_X1, SAFE_Y0, SAFE_Z - 0.5), (SAFE_X1, SAFE_Y1, SAFE_Z - 0.5),
                     (SAFE_X0, SAFE_Y1, SAFE_Z - 0.5)], hx("121214"))
        # heavy door swung open on its left hinge
        R.quad(img, [(SAFE_X0, SAFE_Y0, SAFE_Z), (SAFE_X0, SAFE_Y0, SAFE_Z + 22), (SAFE_X0, SAFE_Y1, SAFE_Z + 22),
                     (SAFE_X0, SAFE_Y1, SAFE_Z)], STEEL, STEEL_L)
        if box:
            R.box(img, SAFE_X0 + 6, SAFE_X1 - 6, SAFE_Y0, SAFE_Y0 + 8, SAFE_Z - 0.4, SAFE_Z + 0.2, hx("b08a3a"), top=hx("d8b050"))
            px, py = R.P((SAFE_X0 + SAFE_X1) / 2, SAFE_Y0 + 4, SAFE_Z + 0.3)
            ImageDraw.Draw(img).point((px, py), fill=hx("6a5020"))
    # both doors flung wide
    for x in (X0, X1):
        R.quad(img, [(x, 6, Z1), (x, 6, Z1 + 24), (x, 100, Z1 + 24), (x, 100, Z1)], hx("75492b"), hx("3e2615"))
        R.quad(img, [(x, 12, Z1 + 4), (x, 12, Z1 + 20), (x, 94, Z1 + 20), (x, 94, Z1 + 4)], None, hx("8e6040"))


def desk(img, drawer_open=False, paper=False):
    X0, X1, Z0, Z1 = DESK_X0, DESK_X1, DESK_Z0, DESK_Z1
    a, b = R.P(X0, 0, Z1), R.P(X1, 0, Z1)
    shadow(img, "rect", [a[0], a[1] - 4, b[0] + 6, a[1] + 3], 0.35, 3)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z0 + 2), (x, 24, Z0 + 2), WOOD_D, 2)
    R.box(img, X0, X1, 20, 26, Z0, Z1, mul(WOOD, 0.9), top=WOOD, side=WOOD_D)
    R.box(img, X0 - 1, X1 + 1, 26, 28, Z0, Z1 + 1, hx("7d5232"), top=hx("8e6040"), side=WOOD_D)
    for x in (X0 + 2, X1 - 2):
        R.line(img, (x, 0, Z1 - 2), (x, 20, Z1 - 2), WOOD_D, 2)
    # left drawer: locked, brass keyhole; right drawer: yanked out and dumped
    c = X0 + 6
    R.quad(img, [(c, 21, Z1), (c + 24, 21, Z1), (c + 24, 25, Z1), (c, 25, Z1)], None, WOOD_D)
    R.line(img, (c + 11, 23, Z1), (c + 13, 23, Z1), GOLD)
    c2 = X1 - 30
    R.quad(img, [(c2, 21, Z1), (c2 + 24, 21, Z1), (c2 + 24, 25, Z1), (c2, 25, Z1)], hx("120a06"))
    R.box(img, c2 + 6, c2 + 30, 0, 4, Z1 + 14, Z1 + 26, WOOD, top=hx("2a1a10"), side=WOOD_D)
    # stationery scattered, inkwell tipped over
    R.quad(img, [(X0 + 22, 28.1, 8), (X0 + 46, 28.1, 6), (X0 + 48, 28.1, 18), (X0 + 24, 28.1, 20)], hx("ece0c6"))
    R.box(img, X0 + 8, X0 + 16, 28, 31, 12, 16, hx("2e3a3a"), top=hx("4a5656"))
    R.quad(img, [(X0 + 16, 28.1, 12), (X0 + 30, 28.1, 14), (X0 + 26, 28.1, 22), (X0 + 14, 28.1, 18)], hx("141c2a"))
    if drawer_open:
        R.box(img, c, c + 24, 20, 25, Z1, Z1 + 12, hx("6a4428"), top=hx("1e120a"), side=WOOD_D)
        R.line(img, (c + 11, 23, Z1 + 12), (c + 13, 23, Z1 + 12), GOLD)
        if paper:
            R.quad(img, [(c + 6, 25.1, Z1 + 3), (c + 18, 25.1, Z1 + 2), (c + 19, 25.1, Z1 + 9), (c + 7, 25.1, Z1 + 10)],
                   hx("f4ecdc"))
            R.line(img, (c + 8, 25.2, Z1 + 5), (c + 16, 25.2, Z1 + 5), hx("3a3a6a"))
            R.line(img, (c + 8, 25.2, Z1 + 7), (c + 15, 25.2, Z1 + 7), hx("3a3a6a"))


def mess(img):
    """Everything the searchers threw on the floor."""
    d = ImageDraw.Draw(img)
    # the desk chair, on its back
    R.box(img, 186, 210, 0, 3, 34, 48, BURGUNDY, top=BURGUNDY_L, side=mul(BURGUNDY, 0.7))
    R.box(img, 210, 214, 0, 14, 34, 48, mul(WOOD, 0.85), top=WOOD, side=WOOD_D)
    for z in (36, 46):
        R.line(img, (186, 6, z), (172, 8, z), WOOD_D, 2)
    # papers, letters and an emptied handbag
    for i, (x, z, col) in enumerate(((130, 60, hx("ece0c6")), (146, 74, hx("f4ecdc")), (236, 64, hx("e8dcc0")),
                                     (252, 90, hx("ece0c6")), (118, 96, hx("f0e6d2")), (300, 104, hx("e8dcc0")))):
        R.quad(img, [(x, 0.2, z), (x + 12, 0.2, z - 1 + i % 3), (x + 13, 0.2, z + 8), (x + 1, 0.2, z + 9)], col)
    R.quad(img, [(222, 0.3, 100), (238, 0.3, 98), (240, 0.3, 108), (224, 0.3, 112)], hx("2a1a2a"))
    # a dress, a fur stole and a stocking dragged across the rug
    R.quad(img, [(96, 0.2, 110), (128, 0.2, 104), (136, 0.2, 124), (104, 0.2, 134), (90, 0.2, 126)], hx("b88aa0"))
    R.line(img, (100, 0.3, 114), (126, 0.3, 120), hx("8a5a72"))
    R.quad(img, [(330, 0.2, 120), (370, 0.2, 116), (372, 0.2, 126), (334, 0.2, 130)], hx("9a8a76"))
    R.line(img, (380, 0.3, 96), (408, 0.3, 110), hx("d8c0a8"), 2)
    # pillows thrown down, one slashed open with its feathers out
    R.box(img, 256, 276, 0, 6, 76, 92, hx("f3ead8"), top=hx("faf5ea"), side=hx("c0b096"))
    R.line(img, (260, 6.1, 84), (272, 6.1, 82), hx("8a7a66"))
    for i in range(14):
        x, z = 240 + (i * 37) % 60, 70 + (i * 23) % 40
        px, py = R.P(x, 0.3, z)
        d.point((px, py), fill=hx("fdf8ee"))
    # the nightstand lamp knocked over, shade rolled away
    R.quad(img, [(412, 0.2, 40), (424, 0.2, 38), (426, 0.2, 48), (414, 0.2, 50)], hx("efe2c4"), GOLD_D)
    R.line(img, (402, 1, 34), (414, 1, 42), GOLD_D, 2)
    # vanity: both drawers pulled out, a perfume bottle spilt
    R.box(img, 420, 438, 14, 20, 22, 32, mul(WOOD, 0.92), top=hx("2a1a10"), side=WOOD_D)
    R.box(img, 450, 468, 0, 6, 34, 44, mul(WOOD, 0.92), top=hx("2a1a10"), side=WOOD_D)
    R.quad(img, [(440, 0.2, 52), (452, 0.2, 54), (448, 0.2, 60)], hx("c9a0b8"))


def paint(closet_open=False, safe_open=False, box=False, drawer_open=False, paper=False):
    img = Image.new("RGB", (W, H))
    hotel.shell(img)
    crooked_painting(img)
    hotel.floor(img)
    hotel.door(img)
    window_night(img)
    hotel.sconces(img)
    closet(img, closet_open, safe_open, box)
    desk(img, drawer_open, paper)
    hotel.bed(img, True)
    hotel.nightstand(img)
    hotel.vanity(img)
    mess(img)
    hotel.chandelier(img)
    img = tall(img, hotel.ceiling)
    # night: the only light comes from the sconces and the city outside
    dark = Image.new("RGB", img.size, (70, 70, 120))
    img = ImageChops.multiply(img, Image.blend(dark, Image.new("RGB", img.size, (255, 240, 210)), 0.55))
    light(img, "ellipse", [96, 40, 296, 140], hx("ffe0a0"), 0.18, 18)
    light(img, "polygon", [(166, 134), (222, 134), (300, H + TOP - 1), (150, H + TOP - 1)], hx("6a80c0"), 0.1, 12)
    vignette(img, 0.4, tint=(30, 24, 40), blur=34)
    return img


def _bbox(a, b):
    return ImageChops.difference(a, b).getbbox()


def build():
    base = paint()
    pal = palette_of(base, 128)
    px = pixelize(base, pal)
    save(px, "rooms", "eleanor_room.png")
    states = {
        "closet": pixelize(paint(closet_open=True), pal),
        "safe": pixelize(paint(closet_open=True, safe_open=True), pal),
        "box": pixelize(paint(closet_open=True, safe_open=True, box=True), pal),
        "drawer": pixelize(paint(drawer_open=True), pal),
        "paper": pixelize(paint(drawer_open=True, paper=True), pal),
    }
    # each overlay is cut where it differs from the layer it sits on; positions go into eleanor_room.tscn
    for name, under, over in (("closet_open", px, "closet"), ("safe_open", states["closet"], "safe"),
                              ("brass_box", states["safe"], "box"), ("drawer_open", px, "drawer"),
                              ("paper", states["drawer"], "paper")):
        box = _bbox(under, states[over])
        save(states[over].crop(box), "rooms", f"eleanor_room_{name}.png")
        print(f"  eleanor_room_{name}.png at {box[:2]}")
    return px
