"""Micah Jones' office: a cramped, lamp-lit detective office on a rainy night."""
from PIL import Image, ImageDraw
import math
import random
from .common import (W, H, TOP, tall, hx, mix, mul, vgrad, hgrad, noise, light, shadow, vignette, pixelize, palette_of,
                     text, city, save, floor_boards, sunburst, candlestick_phone)

FLOOR = 128


def walls(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, FLOOR), hx("3c3a2c"), hx("2a2a22"))
    # vertical stripe wallpaper
    for x in range(0, W, 8):
        d.line([(x, 0), (x, FLOOR)], fill=hx("34322a"))
        d.line([(x + 3, 0), (x + 3, FLOOR)], fill=hx("424032"))
    noise(img, (0, 0, W - 1, FLOOR), 4, 1)
    # picture rail + wainscot
    d.rectangle([0, 12, W - 1, 14], fill=hx("4a3424"))
    d.line([(0, 12), (W, 12)], fill=hx("6a4c34"))
    vgrad(img, (0, 96, W - 1, FLOOR), hx("4a3020"), hx("2e1c12"))
    for x in range(0, W, 30):
        d.rectangle([x + 3, 100, x + 26, FLOOR - 5], outline=hx("3a2416"))
        d.line([(x + 4, 101), (x + 25, 101)], fill=hx("5c3c28"))
    d.rectangle([0, 95, W - 1, 97], fill=hx("5a3a26"))
    d.rectangle([0, FLOOR - 3, W - 1, FLOOR], fill=hx("24160e"))
    # water stain + crack
    shadow(img, "ellipse", [250, 0, 300, 30], 0.25, 8, hx("806040"))
    d.line([(420, 14), (424, 26), (421, 34), (426, 44)], fill=hx("26241c"))


def floor(img):
    floor_boards(img, FLOOR, H - 1, (240, -260), 20, hx("4a2e1c"), hx("3a2416"), hx("24140c"), 3)
    noise(img, (0, FLOOR, W - 1, H - 1), 5, 2)
    d = ImageDraw.Draw(img)
    # threadbare rug in perspective
    rug = [(150, 158), (360, 158), (392, 196), (118, 196)]
    d.polygon(rug, fill=hx("5a1c1c"))
    d.polygon([(158, 162), (352, 162), (380, 192), (130, 192)], outline=hx("a07040"))
    d.polygon([(168, 166), (342, 166), (366, 188), (144, 188)], fill=hx("4a1818"), outline=hx("7a4a2a"))
    for i in range(5):
        x = 190 + i * 32
        d.polygon([(x, 172), (x + 8, 177), (x, 182), (x - 8, 177)], fill=hx("8a6a3a"))
    for x in range(120, 392, 4):
        d.line([(x, 196), (x, 198)], fill=hx("b09060"))
    noise(img, (118, 158, 392, 198), 6, 4)


DOOR = (32, 18, 84, 127)
DOOR_BOX = (27, 13 + TOP, 90, 140 + TOP)


def _grain(img, box, seed, vertical=True, k=0.8, step=(2, 4)):
    """Darkened streaks of wood grain across a box, wandering a pixel now and then; the paint underneath shows
    through, so the grain follows any gradient or light already there."""
    rnd = random.Random(seed)
    px = img.load()
    x0, y0, x1, y1 = box
    lo, hi = (x0, x1) if vertical else (y0, y1)
    a, b = (y0, y1) if vertical else (x0, x1)
    pos = lo + rnd.randint(0, 1)
    while pos <= hi:
        f, off = rnd.uniform(k, k + 0.08), 0
        for t in range(a, b + 1):
            if rnd.random() < 0.07:
                off = max(-1, min(1, off + rnd.choice((-1, 1))))
            u = pos + off
            if lo <= u <= hi:
                xy = (u, t) if vertical else (t, u)
                px[xy] = mul(px[xy], f)
        pos += rnd.randint(*step)


def _casing(img, d):
    """The moulded door casing: jambs and head with a bead and a groove, mitred corners, a crown cap above and
    plinth blocks at the floor. Identical in every door state, so the ajar/open overlays line up."""
    x0, y0, x1, y1 = DOOR
    wood, wood_l, wood_d, edge, gap = hx("3a2416"), hx("6a4a2e"), hx("24140a"), hx("1a0e06"), hx("2e1c10")
    d.rectangle([x0 - 5, y0 - 5, x0 - 1, y1], fill=wood)
    d.rectangle([x1 + 1, y0 - 5, x1 + 5, y1], fill=wood)
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y0 - 1], fill=hx("4a3020"))
    _grain(img, (x0 - 5, y0, x0 - 1, y1), 31, k=0.86)
    _grain(img, (x1 + 1, y0, x1 + 5, y1), 32, k=0.86)
    _grain(img, (x0 - 5, y0 - 5, x1 + 5, y0 - 1), 33, vertical=False, k=0.86)
    d = ImageDraw.Draw(img)
    for x, col in ((x0 - 5, edge), (x0 - 4, wood_l), (x0 - 2, wood_d), (x0 - 1, gap),
                   (x1 + 1, gap), (x1 + 2, wood_d), (x1 + 4, hx("54382a")), (x1 + 5, edge)):
        d.line([(x, y0 - 5 if x in (x0 - 5, x1 + 5) else y0), (x, y1)], fill=col)
    d.line([(x0 - 4, y0 - 4), (x1 + 4, y0 - 4)], fill=hx("7a5434"))
    d.line([(x0 - 2, y0 - 2), (x1 + 2, y0 - 2)], fill=wood_d)
    d.line([(x0 - 1, y0 - 1), (x1 + 1, y0 - 1)], fill=gap)
    # mitre joints where the head meets the jambs
    d.line([(x0 - 5, y0 - 5), (x0 - 1, y0 - 1)], fill=edge)
    d.line([(x1 + 5, y0 - 5), (x1 + 1, y0 - 1)], fill=edge)
    # the crown cap, lit along its top, throwing a line of shadow on the head
    d.rectangle([x0 - 7, y0 - 9, x1 + 7, y0 - 6], fill=hx("4a3020"))
    d.line([(x0 - 7, y0 - 9), (x1 + 7, y0 - 9)], fill=hx("8a6440"))
    d.line([(x0 - 7, y0 - 8), (x1 + 7, y0 - 8)], fill=hx("5e4028"))
    d.line([(x0 - 7, y0 - 6), (x1 + 7, y0 - 6)], fill=edge)
    for px_ in (x0 - 7, x1 + 7):
        d.line([(px_, y0 - 9), (px_, y0 - 6)], fill=edge)
    # plinth blocks the casing stands on
    for bx0, bx1 in ((x0 - 6, x0 - 1), (x1 + 1, x1 + 6)):
        d.rectangle([bx0, y1 - 12, bx1, y1], fill=hx("43291a"), outline=edge)
        d.line([(bx0 + 1, y1 - 11), (bx1 - 1, y1 - 11)], fill=hx("6a4a2e"))
        d.line([(bx0 + 1, y1 - 9), (bx1 - 1, y1 - 9)], fill=wood_d)


def _hinges(d):
    """Three brass butt hinges: only the knuckles show, in the gap on the hinge (left) side."""
    x0, y0, x1, y1 = DOOR
    for hy in (y0 + 6, y0 + 50, y1 - 15):
        d.point((x0, hy - 1), fill=BRASS_D)
        d.rectangle([x0 - 1, hy, x0 + 1, hy + 7], fill=BRASS_D)
        d.line([(x0, hy), (x0, hy + 7)], fill=BRASS)
        d.line([(x0 - 1, hy + 1), (x0 - 1, hy + 2)], fill=BRASS_L)
        d.line([(x0 - 1, hy + 4), (x0 + 1, hy + 4)], fill=hx("3a2a14"))
        d.point((x0, hy + 8), fill=BRASS_D)


def _panel(img, box, seed, vertical=True):
    """A raised panel: a shadowed recess, a bevel lit on top and left, and a grained field standing proud."""
    d = ImageDraw.Draw(img)
    a, b, c, e = box
    d.rectangle(box, outline=hx("24140a"))
    for i in (1, 2):
        d.line([(a + i, b + i), (c - i, b + i)], fill=hx("6e4c30" if i == 1 else "60422a"))
        d.line([(a + i, b + i), (a + i, e - i)], fill=hx("5a3c26"))
        d.line([(a + i, e - i), (c - i, e - i)], fill=hx("2e1c0e"))
        d.line([(c - i, b + i + 1), (c - i, e - i)], fill=hx("3a2414"))
    field = (a + 3, b + 3, c - 3, e - 3)
    if field[2] > field[0]:
        vgrad(img, field, hx("5e3e24"), hx("4a2e1a"))
        _grain(img, field, seed, vertical, k=0.78, step=(2, 3))
        d = ImageDraw.Draw(img)
        d.line([(field[0], field[1]), (field[2], field[1])], fill=hx("7a5838"))


def _mail_slot(d, x0, x1, y):
    d.rectangle([x0, y, x1, y + 3], fill=BRASS, outline=BRASS_D)
    d.line([(x0 + 1, y), (x1 - 1, y)], fill=BRASS_L)
    d.line([(x0 + 2, y + 2), (x1 - 2, y + 2)], fill=hx("1a1008"))
    d.point((x0 + 1, y + 2), fill=BRASS_D)
    d.point((x1 - 1, y + 2), fill=BRASS_D)


def _lockset(d, kx0, kx1):
    """The brass escutcheon plate with its keyhole, and the knob on it (kx0..kx1 is the knob's span)."""
    px0, px1 = kx0 + 1, kx1 - 1
    d.rectangle([px0, 79, px1, 91], fill=BRASS_D, outline=hx("3e2c14"))
    d.line([(px0, 80), (px0, 90)], fill=BRASS)
    d.point((px0, 80), fill=BRASS_L)
    kc = (px0 + px1) // 2
    d.point((kc, 88), fill=hx("1a1008"))
    d.line([(kc, 89), (kc, 90)], fill=hx("1a1008"))
    d.point((kx1 + 1, 87), fill=hx("1e1208"))
    d.point((kx1, 88), fill=hx("1e1208"))
    d.ellipse([kx0, 82, kx1, 87], fill=hx("c8a050"), outline=hx("3e2c14"))
    d.point((kx0 + 1, 83), fill=hx("fff0b0"))
    d.point((kx0 + 2, 83), fill=BRASS_L)


def _frost(img, box, seed):
    """Frosted glass: a fine grit, sparse brighter specks, and the shadow of the glazing bead along the top."""
    import random as _r
    noise(img, box, 7, 5)
    rnd = random.Random(seed)
    d = ImageDraw.Draw(img)
    gx0, gy0, gx1, gy1 = box
    for _ in range((gx1 - gx0) * (gy1 - gy0) // 40):
        x, y = rnd.randint(gx0, gx1), rnd.randint(gy0, gy1)
        d.point((x, y), fill=mix(img.getpixel((x, y)), hx("e8e2c0"), 0.5))
    shadow(img, "rect", [gx0, gy0, gx1, gy0 + 1], 0.35, 0)


def _glint(img, box):
    """Two thin diagonal streaks of reflected light across the corners of the pane."""
    gx0, gy0, gx1, gy1 = box
    for s, w in ((9, 3), (14, 1)):
        light(img, "polygon", [(gx0 + s, gy0), (gx0 + s + w, gy0), (gx0, gy0 + s + w), (gx0, gy0 + s)],
              hx("fffbe8"), 0.3, 0)
        light(img, "polygon", [(gx1 - s, gy1), (gx1 - s - w, gy1), (gx1, gy1 - s - w), (gx1, gy1 - s)],
              hx("fffbe8"), 0.22, 0)


def _bead(d, box):
    gx0, gy0, gx1, gy1 = box
    d.rectangle([gx0 - 1, gy0 - 1, gx1 + 1, gy1 + 1], outline=hx("6a4a2e"))
    d.line([(gx0 - 1, gy1 + 1), (gx1 + 1, gy1 + 1)], fill=hx("2e1c0e"))
    d.line([(gx1 + 1, gy0), (gx1 + 1, gy1 + 1)], fill=hx("3a2414"))
    d.rectangle(box, outline=hx("2a180c"))


def door(img, state="closed"):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOOR
    if state != "closed":
        d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1 + 8], fill=hx("3a2416"))
        _casing(img, d)
        d = ImageDraw.Draw(img)
        vgrad(img, (x0, y0, x1, y1), hx("6a6458"), hx("3a342c"))
        d.polygon([(x0 + 4, y1 - 10), (x1 - 4, y1 - 10), (x1 - 10, y1), (x0 + 10, y1)], fill=hx("5a4634"))
        d.ellipse([(x0 + x1) // 2 - 6, y0 + 8, (x0 + x1) // 2 + 6, y0 + 18], fill=hx("f8e8b0"))
        d.rectangle([x0 + 8, y0 + 28, x1 - 18, y1 - 16], fill=hx("2e2a24"))
        if state == "ajar":
            # hinged on the left; the knob edge swings in first, opening a gap on the right
            fx = x1 - 18
            d.polygon([(x0, y0), (fx, y0 - 2), (fx, y1 + 2), (x0, y1)], fill=hx("4e321c"))
            _grain(img, (x0 + 1, y0, fx - 1, y1), 41, k=0.82)
            _grain(img, (x0 + 5, y0 + 1, fx - 5, y0 + 4), 42, vertical=False, k=0.84)
            _grain(img, (x0 + 5, 72, fx - 5, 92), 43, vertical=False, k=0.84)
            d = ImageDraw.Draw(img)
            glass = (x0 + 5, y0 + 6, fx - 5, 70)
            vgrad(img, glass, hx("c8c098"), hx("8a8a6a"))
            _frost(img, glass, 44)
            d = ImageDraw.Draw(img)
            _bead(d, glass)
            # the lettering slides out of view with the glass; only the gilt glint of the pane is left
            _glint(img, glass)
            # the panels foreshortened to ~2/3 of their width
            _panel(img, (x0 + 6, 93, x0 + 16, 121), 45)
            _panel(img, (x0 + 19, 93, fx - 5, 121), 46)
            d = ImageDraw.Draw(img)
            _mail_slot(d, x0 + 11, fx - 11, 75)
            d.line([(fx, y0 - 2), (fx, y1 + 2)], fill=hx("2a180c"))
            d.line([(fx + 1, y0 - 1), (fx + 1, y1 + 1)], fill=hx("6a4a2e"))
            # the face is foreshortened to ~2/3 of its width, so the knob narrows with it
            _lockset(d, fx - 8, fx - 5)
        else:
            d.rectangle([x0, y0, x0 + 9, y1], fill=hx("4e321c"))
            _grain(img, (x0, y0, x0 + 8, y1), 47, k=0.82, step=(2, 3))
            d = ImageDraw.Draw(img)
            d.rectangle([x0 + 1, y0 + 8, x0 + 7, 66], fill=hx("c8c098"))
            noise(img, (x0 + 1, y0 + 8, x0 + 7, 66), 6, 5)
            d = ImageDraw.Draw(img)
            d.line([(x0 + 1, y0 + 8), (x0 + 1, 66)], fill=hx("8a8a6a"))
            d.line([(x0 + 2, y0 + 10), (x0 + 5, y0 + 13)], fill=hx("f0ecd8"))
            # swung wide open and seen almost edge-on: panels, slot and knob are thin slivers
            for py0, py1 in ((93, 121),):
                d.rectangle([x0 + 1, py0, x0 + 7, py1], outline=hx("2a180c"))
                d.line([(x0 + 2, py0 + 1), (x0 + 6, py0 + 1)], fill=hx("6e4c30"))
                d.line([(x0 + 4, py0 + 1), (x0 + 4, py1 - 1)], fill=hx("2a180c"))
            d.rectangle([x0 + 3, 75, x0 + 5, 77], fill=BRASS_D)
            d.point((x0 + 3, 75), fill=BRASS_L)
            d.rectangle([x0 + 3, 79, x0 + 4, 91], fill=BRASS_D)
            d.rectangle([x0 + 3, 82, x0 + 4, 86], fill=hx("c8a050"))
            d.point((x0 + 3, 83), fill=hx("fff0b0"))
            d.line([(x0 + 9, y0), (x0 + 9, y1)], fill=hx("2a180c"))
        _hinges(d)
        d.line([(x0 + 1, y1), (x1 - 1, y1)], fill=hx("d8c080"))
        return
    d.rectangle([x0 - 5, y0 - 5, x1 + 5, y1], fill=hx("3a2416"))
    _casing(img, d)
    # the slab: stiles grained upright, the rails across
    vgrad(img, (x0, y0, x1, y1), hx("5a3a22"), hx("3e2616"))
    _grain(img, (x0 + 1, y0 + 1, x1 - 1, y1 - 1), 51, k=0.8)
    for ry0, ry1 in ((y0 + 1, y0 + 5), (72, 92), (122, y1 - 1)):
        vgrad(img, (x0 + 7, ry0, x1 - 7, ry1), mix(hx("5a3a22"), hx("3e2616"), (ry0 - y0) / (y1 - y0)),
              mix(hx("5a3a22"), hx("3e2616"), (ry1 - y0) / (y1 - y0)))
        _grain(img, (x0 + 7, ry0, x1 - 7, ry1), 52 + ry0, vertical=False, k=0.8)
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], outline=hx("2a180c"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("6a4a2e"))
    d.line([(x1 - 1, y0 + 2), (x1 - 1, y1 - 1)], fill=hx("2e1c0e"))
    # frosted glass with backlit corridor, the gilt-edged sign painted on it read backwards from inside
    glass = (x0 + 7, y0 + 7, x1 - 7, 70)
    vgrad(img, glass, hx("c8c098"), hx("8a8a6a"))
    _frost(img, glass, 53)
    d = ImageDraw.Draw(img)
    _bead(d, glass)
    for t, y in (("MICAH", 34), ("JONES", 44), ("P.I.", 56)):
        text(img, ((x0 + x1) // 2, y + 1), t, hx("a8782c"), size=8, mirror=True)
        text(img, ((x0 + x1) // 2, y), t, hx("1e1a14"), size=8, mirror=True)
    # silhouette of a waiting stranger? no - empty corridor bulb glow
    light(img, "ellipse", [x0 + 12, y0 + 10, x1 - 12, 50], hx("f8e8b0"), 0.35, 8)
    _glint(img, glass)
    # the raised panels below the lock rail
    _panel(img, (x0 + 7, 93, x0 + 23, 121), 54)
    _panel(img, (x1 - 23, 93, x1 - 7, 121), 55)
    d = ImageDraw.Draw(img)
    _mail_slot(d, x0 + 17, x1 - 17, 75)
    _lockset(d, x1 - 12, x1 - 7)
    _hinges(d)
    # scuffs on the bottom rail where shoes have pushed it shut
    for sx, col in ((x0 + 12, "2e1c0e"), (x0 + 13, "2e1c0e"), (x1 - 15, "6a4a2e"), (x0 + 30, "2e1c0e")):
        d.point((sx, 124), fill=hx(col))
    # light leaking under the door
    d.line([(x0 + 1, y1), (x1 - 1, y1)], fill=hx("d8c080"))
    light(img, "rect", [x0, y1, x1, y1 + 10], hx("806830"), 0.35, 4)


CAB = (108, 60, 146, 127)
# the middle drawer pulled out (with or without the picks on the files), the picks alone (screen coordinates)
CAB_OPEN_BOX = (102, 82 + TOP, 152, 119 + TOP)
CAB_PICKS_BOX = (118, 85 + TOP, 140, 95 + TOP)
BRASS, BRASS_L, BRASS_D = hx("b8904a"), hx("e8c878"), hx("6a4c24")


def _cab_front(d, x0, y0, x1, y1, lit=0):
    """One steel drawer front: a pressed face, the brass label holder with its card, the cup pull under it."""
    face = hx("5e625c") if not lit else hx("6a6e66")
    d.rectangle([x0, y0, x1, y1], fill=face, outline=hx("262826"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("8a8e86"))
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=hx("3a3e3a"))
    d.line([(x1 - 1, y0 + 2), (x1 - 1, y1 - 2)], fill=hx("464a46"))
    cx = (x0 + x1) // 2
    d.rectangle([cx - 6, y0 + 3, cx + 6, y0 + 7], fill=hx("ddd2b0"), outline=BRASS_D)
    d.line([(cx - 6, y0 + 3), (cx + 6, y0 + 3)], fill=BRASS)
    d.line([(cx - 4, y0 + 5), (cx + 2, y0 + 5)], fill=hx("6a6050"))
    d.rectangle([cx - 5, y0 + 10, cx + 5, y0 + 13], fill=BRASS_D)
    d.line([(cx - 5, y0 + 10), (cx + 5, y0 + 10)], fill=BRASS_L)
    d.line([(cx - 4, y0 + 11), (cx + 4, y0 + 11)], fill=BRASS)
    d.line([(cx - 3, y0 + 12), (cx + 3, y0 + 12)], fill=hx("2a2418"))


def cabinet(img, whiskey=True, open_=None):
    """The steel filing cabinet with the whiskey on top. open_ is None (shut), or the contents of the pulled-out
    middle drawer: () or ("lockpick",)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = CAB
    shadow(img, "rect", [x1, y0 + 2, x1 + 8, y1], 0.5, 3)
    hgrad(img, (x0, y0, x1, y1), hx("666c66"), hx("3a3e3a"))
    d.rectangle([x0, y0, x1, y1], outline=hx("1e201e"))
    # a lipped top, lit along its front edge
    d.rectangle([x0 - 1, y0, x1 + 1, y0 + 2], fill=hx("4a4e4a"))
    d.line([(x0 - 1, y0), (x1 + 1, y0)], fill=hx("9a9e94"))
    d.line([(x0 - 1, y0 + 2), (x1 + 1, y0 + 2)], fill=hx("2a2c2a"))
    # the kick plate, scuffed by years of shoes
    d.rectangle([x0 + 1, y1 - 3, x1 - 1, y1], fill=hx("242624"))
    for sx in (114, 121, 137):
        d.point((sx, y1 - 2), fill=hx("5a5e58"))
    for i in range(3):
        fy = y0 + 4 + i * 21
        _cab_front(d, x0 + 3, fy, x1 - 3, fy + 18)
    # the lock cylinder in the top corner
    d.ellipse([x1 - 7, y0 + 4, x1 - 4, y0 + 7], fill=BRASS_D)
    d.point((x1 - 6, y0 + 5), fill=BRASS_L)
    noise(img, (x0, y0, x1, y1), 4, 9)
    # a dent and a rust bloom low on the side
    d.point((x0 + 5, 112), fill=hx("2e322e"))
    d.point((x0 + 6, 113), fill=hx("7a7e76"))
    d.point((x1 - 4, 120), fill=hx("6a4a30"))
    d.point((x1 - 5, 121), fill=hx("5a3a24"))
    if open_ is not None:
        _cab_open(img, d, open_)
    if whiskey:
        bottle(d, 115, 36)
        shadow(img, "rect", [117, 58, 126, 60], 0.4, 1)


def _cab_open(img, d, contents):
    fy = 60 + 4 + 21
    # the empty slot the drawer came out of
    d.rectangle([111, fy, 143, fy + 18], fill=hx("121412"))
    # the drawer's insides, seen from above: rows of manila folders, a tab standing up here and there
    d.polygon([(111, fy + 1), (143, fy + 1), (148, fy + 12), (106, fy + 12)], fill=hx("2a2c2a"))
    for j, y in enumerate(range(fy + 3, fy + 12, 2)):
        spread = (y - fy) * 5 // 11
        d.line([(111 - spread + 1, y), (143 + spread - 1, y)], fill=hx("c8a860") if j % 2 else hx("a88a48"))
        d.line([(111 - spread + 1, y + 1), (143 + spread - 1, y + 1)], fill=hx("4a3c22"))
    for tx, ty in ((115, fy + 2), (131, fy + 4), (139, fy + 8)):
        d.rectangle([tx, ty, tx + 3, ty + 1], fill=hx("e0c888"))
    # the front, pulled out towards the room and catching more of the lamp
    _cab_front(d, 106, fy + 12, 148, fy + 31, lit=1)
    shadow(img, "rect", [106, fy + 32, 148, fy + 35], 0.55, 1)
    if "lockpick" in contents:
        # the rolled leather pick case lying on the files, a pair of steel handles poking out of the end
        d.rounded_rectangle([120, fy + 3, 134, fy + 7], 2, fill=hx("5a3420"))
        d.line([(121, fy + 3), (133, fy + 3)], fill=hx("8a5a34"))
        d.line([(121, fy + 7), (133, fy + 7)], fill=hx("2a160a"))
        for sx in range(122, 134, 2):
            d.point((sx, fy + 5), fill=hx("a87a4a"))
        d.line([(127, fy + 2), (127, fy + 8)], fill=hx("2a180c"))
        d.line([(134, fy + 4), (138, fy + 3)], fill=hx("c8c8d0"))
        d.line([(134, fy + 6), (138, fy + 6)], fill=hx("9a9aa4"))
        d.point((138, fy + 3), fill=hx("e8e8f0"))


def diploma(img):
    """Micah's licence, framed in gilt and hung on a wire from the picture rail."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 111, 17, 143, 33
    d.line([(127, 14), (x0 + 5, y0)], fill=hx("8a7a5a"))
    d.line([(127, 14), (x1 - 5, y0)], fill=hx("8a7a5a"))
    d.point((127, 14), fill=BRASS_L)
    shadow(img, "rect", [x0 + 2, y0 + 2, x1 + 2, y1 + 2], 0.5, 1)
    d.rectangle([x0, y0, x1, y1], fill=hx("9a7030"), outline=hx("4a3010"))
    d.line([(x0 + 1, y0 + 1), (x1 - 1, y0 + 1)], fill=hx("e8c470"))
    d.line([(x0 + 1, y0 + 1), (x0 + 1, y1 - 1)], fill=hx("c89e50"))
    d.line([(x0 + 1, y1 - 1), (x1 - 1, y1 - 1)], fill=hx("6a4a1c"))
    d.line([(x1 - 1, y0 + 1), (x1 - 1, y1 - 1)], fill=hx("6a4a1c"))
    vgrad(img, (x0 + 3, y0 + 3, x1 - 3, y1 - 3), hx("ece2c2"), hx("d4c49c"))
    d.rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], outline=hx("5a3c14"))
    # the heading, the copy, his name, two signatures and the state's seal on its ribbons
    d.line([(x0 + 9, y0 + 5), (x1 - 9, y0 + 5)], fill=hx("2a2418"))
    d.line([(x0 + 11, y0 + 6), (x1 - 11, y0 + 6)], fill=hx("4a4030"))
    d.line([(x0 + 7, y0 + 8), (x1 - 7, y0 + 8)], fill=hx("9a9078"))
    d.line([(x0 + 12, y0 + 10), (x1 - 12, y0 + 10)], fill=hx("3a3060"))
    d.line([(x0 + 7, y0 + 12), (x1 - 7, y0 + 12)], fill=hx("9a9078"))
    for sx in (x0 + 5, x1 - 10):
        d.line([(sx, y1 - 4), (sx + 1, y1 - 5), (sx + 3, y1 - 4), (sx + 5, y1 - 5)], fill=hx("3a3060"))
    cx = (x0 + x1) // 2
    d.line([(cx - 1, y1 - 4), (cx - 2, y1 - 2)], fill=hx("2a4a8a"))
    d.line([(cx + 1, y1 - 4), (cx + 2, y1 - 2)], fill=hx("2a4a8a"))
    d.ellipse([cx - 2, y1 - 7, cx + 2, y1 - 3], fill=hx("a01e1e"))
    d.point((cx - 1, y1 - 6), fill=hx("e05050"))


def bottle(d, x, y):
    """The whiskey bottle, its cap's top-left corner at (x + 2, y): 9 px wide, 24 px tall. Round-shouldered, a third
    gone, the label a cream band with a red stripe; the lamp catches the glass down its left side."""
    glass, amber, amber_d, empty = hx("3a2a1a"), hx("8a4a14"), hx("5a2e0c"), hx("2e2a26")
    d.rectangle([x + 3, y, x + 5, y + 1], fill=hx("1a1a1a"))
    d.point((x + 3, y), fill=hx("4a4a4a"))
    d.rectangle([x + 3, y + 2, x + 5, y + 7], fill=empty)
    d.point((x + 3, y + 3), fill=hx("7a7064"))
    d.polygon([(x + 3, y + 7), (x + 5, y + 7), (x + 8, y + 10), (x, y + 10)], fill=empty)
    d.rectangle([x, y + 10, x + 8, y + 23], fill=glass)
    d.rectangle([x, y + 12, x + 8, y + 23], fill=amber)
    d.line([(x, y + 12), (x + 8, y + 12)], fill=hx("b06a24"))
    d.line([(x + 8, y + 12), (x + 8, y + 23)], fill=amber_d)
    d.rectangle([x + 1, y + 14, x + 7, y + 19], fill=hx("ddcc98"))
    d.line([(x + 1, y + 16), (x + 7, y + 16)], fill=hx("8a1e1e"))
    d.point((x + 3, y + 18), fill=hx("4a3a28"))
    d.point((x + 5, y + 18), fill=hx("4a3a28"))
    d.line([(x + 1, y + 9), (x + 1, y + 13)], fill=hx("8a7a6a"))
    d.line([(x + 1, y + 20), (x + 1, y + 22)], fill=hx("d89048"))
    d.line([(x, y + 23), (x + 8, y + 23)], fill=amber_d)


def cup(d, x, y):
    """The tin cup of whiskey (the office_cup sprite) with its top-left corner at (x, y)."""
    d.rectangle([x + 1, y + 2, x + 7, y + 10], fill=hx("b8b4a4"))
    d.rectangle([x + 2, y + 3, x + 6, y + 5], fill=hx("a86024"))
    d.rectangle([x + 7, y + 4, x + 9, y + 8], outline=hx("b8b4a4"))
    d.line([(x + 2, y + 9), (x + 6, y + 9)], fill=hx("e0d8bc"))


# Act 3: the bottle and the cup end up on the desk, between the lamp and the case files (art coordinates)
DESK_BOTTLE = (214, 80)
DESK_CUP = (224, 92)

RACK_X = 162
# the shoulder rig with the revolver, thrown over the spare coat on the rack (screen coordinates)
HOLSTER_BOX = (154, 29 + TOP, 176, 62 + TOP)


def coat_rack(img, hat=True, holster=False):
    """A bentwood coat rack: the spare trench coat with a red scarf round its collar, the spare fedora (a bullet hole
    in the crown) on the left hook, and - until Micah straps it on - his shoulder rig thrown over the coat."""
    d = ImageDraw.Draw(img)
    x = RACK_X
    wood, wood_l, wood_d = hx("4a2c18"), hx("7a5034"), hx("1e120a")
    shadow(img, "ellipse", [x - 12, 124, x + 12, 130], 0.5, 2)
    for pts in ([(x, 113), (x - 4, 121), (x - 8, 126)], [(x, 113), (x + 4, 121), (x + 8, 126)]):
        d.line(pts, fill=wood, width=2)
        d.point(pts[-1], fill=wood_d)
    d.line([(x, 113), (x, 127)], fill=wood_d, width=2)
    d.rectangle([x - 1, 24, x + 1, 116], fill=wood)
    d.line([(x - 1, 25), (x - 1, 115)], fill=wood_l)
    d.line([(x + 1, 25), (x + 1, 115)], fill=wood_d)
    for ry in (96, 108, 113):
        d.line([(x - 2, ry), (x + 2, ry)], fill=wood_d)
        d.point((x - 2, ry - 1), fill=wood_l)
    d.ellipse([x - 2, 20, x + 2, 24], fill=wood)
    d.point((x - 1, 21), fill=wood_l)
    for k in (-1, 1):
        d.line([(x, 29), (x + 4 * k, 30), (x + 7 * k, 28), (x + 8 * k, 25)], fill=wood_l if k < 0 else wood)
        d.point((x + 8 * k, 24), fill=BRASS)
    # the trench coat, hung by its loop, lit from the lamp on its right
    tan, tan_l, tan_d, tan_dd = hx("7e6a46"), hx("a8925e"), hx("564630"), hx("3a2e1e")
    d.polygon([(157, 32), (167, 32), (172, 38), (174, 62), (176, 90), (150, 90), (152, 62), (153, 38)], fill=tan)
    d.polygon([(153, 38), (156, 40), (155, 74), (151, 74)], fill=tan_d)
    d.polygon([(172, 38), (175, 41), (177, 74), (173, 74)], fill=tan_l)
    d.polygon([(158, 32), (166, 32), (164, 46), (162, 48), (160, 46)], fill=tan_dd)
    d.line([(158, 32), (161, 47)], fill=tan_l)
    d.line([(166, 32), (163, 47)], fill=tan_d)
    for fx0, fx1 in ((157, 155), (163, 163), (169, 171)):
        d.line([(fx0, 63), (fx1, 89)], fill=tan_d)
    d.line([(166, 64), (167, 89)], fill=tan_l)
    d.rectangle([152, 58, 174, 60], fill=tan_d)
    d.line([(152, 58), (174, 58)], fill=tan_l)
    d.rectangle([161, 57, 164, 61], outline=hx("3a2a1a"))
    d.line([(166, 61), (168, 70)], fill=tan_d)
    d.line([(150, 90), (176, 90)], fill=tan_dd)
    for by in (44, 50):
        d.point((158, by), fill=tan_dd)
        d.point((167, by), fill=tan_dd)
    # the red scarf round the collar, its ends hanging down the left of the front
    red, red_l, red_d = hx("7a2420"), hx("a83a30"), hx("4a1210")
    d.polygon([(157, 32), (167, 32), (165, 36), (159, 36)], fill=red)
    d.polygon([(157, 35), (160, 35), (155, 62), (152, 62)], fill=red)
    d.polygon([(159, 35), (162, 35), (158, 56), (155, 56)], fill=red_d)
    d.line([(158, 36), (154, 61)], fill=red_l)
    for fx in range(152, 157):
        d.point((fx, 63), fill=red_d if fx % 2 else red)
    if hat:
        felt, felt_l, felt_d = hx("34343c"), hx("5a5a64"), hx("1a1a20")
        d.ellipse([144, 26, 164, 31], fill=felt_d)
        d.ellipse([144, 25, 164, 30], fill=felt)
        d.rounded_rectangle([148, 18, 160, 28], 3, fill=felt)
        d.line([(149, 19), (149, 26)], fill=felt_l)
        d.line([(153, 19), (155, 21)], fill=felt_d)
        d.rectangle([148, 25, 160, 26], fill=hx("6a1a1a"))
        d.line([(145, 27), (151, 27)], fill=felt_l)
        # the bullet hole: a dark pinprick, its frayed rim catching the light
        d.point((157, 21), fill=hx("0a0a0c"))
        d.point((158, 21), fill=hx("7a7a84"))
        d.point((157, 22), fill=hx("5a5a64"))
    if holster:
        _holster(d)


# the snub .38 in its holster, drawn lying down - barrel right and sheathed, butt down and out (one character per pixel)
REVOLVER = (
    "..lb...................",
    "..bdb.....kkkkkkkk.....",
    "...bLLLLLLbhhhhhhhhk...",
    "...bGbbdbbbHHHHHHHHHk..",
    "..wbbbbdbbbHHsHHsHHHk..",
    "..wWbbbdbbbHHHHHHHHk...",
    ".wWWdbbdbbdkkkkkkkk....",
    ".wKWWd.d..d............",
    ".wWKWdd..dd............",
    "wWKWK..dd..............",
    "wKWKW..................",
    "wWKWK..................",
    "GlLLd..................",
)
REVOLVER_AT = (160, 37)
# hung upright, as a shoulder holster hangs: the drawing turned a quarter clockwise, barrel down, grip up top
REVOLVER_UPRIGHT = tuple("".join(col) for col in zip(*REVOLVER[::-1]))
REVOLVER_INK = {"b": "2e3442", "d": "14161e", "L": "8a96ae", "l": "b8c2d6", "G": "eef4ff",
                "W": "6a3a1a", "w": "a8683a", "K": "3a1c0a",
                "H": "7a4620", "h": "b07440", "k": "3e2010", "s": "d8a868"}


def _holster(d):
    """The shoulder rig thrown over the spare coat: a strap over each shoulder down to the holster hanging upright on
    the chest, and in it the snub .38 - blued cylinder and hammer, trigger guard, checkered walnut grip - drawn pixel
    by pixel so it reads at a glance against the tan coat."""
    strap, strap_l, strap_d = hx("4a2810"), hx("8a5a30"), hx("24120a")
    for top, bot in (((157, 32), (161, 41)), ((168, 32), (170, 48))):
        d.line([top, bot], fill=strap, width=2)
        d.line([(top[0] - 1, top[1]), (bot[0] - 1, bot[1])], fill=strap_l)
    d.line([(154, 31), (170, 31)], fill=strap_d)
    for bx, by in ((159, 36), (169, 40)):
        d.point((bx, by), fill=BRASS_L)
    ox, oy = REVOLVER_AT
    for y, row in enumerate(REVOLVER_UPRIGHT):
        for x, ch in enumerate(row):
            if ch != ".":
                d.point((ox + x, oy + y), fill=hx(REVOLVER_INK[ch]))

def clock(img, hour=9, minute=0):
    """The deco wall clock: a sunburst round a brass bezel, the hands set to hour:minute."""
    d = ImageDraw.Draw(img)
    cx, cy, r = 230, 38, 13
    sunburst(d, cx, cy, r + 6, 24, hx("a08040"), hx("6a5228"), 0, 2 * math.pi)
    for i in range(24):
        a = 2 * math.pi * (i + 0.5) / 24
        d.point((cx + (r + 5) * math.cos(a), cy + (r + 5) * math.sin(a)), fill=hx("e8c878"))
    d.ellipse([cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1], fill=hx("3a2810"))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hx("c89a48"))
    d.arc([cx - r, cy - r, cx + r, cy + r], 180, 300, fill=hx("f0d488"))
    d.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], fill=hx("e6dab8"))
    d.arc([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2], 20, 160, fill=hx("bcae88"))
    for i in range(12):
        a = i * math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        if i % 3 == 0:
            d.line([(cx + (r - 6) * ca, cy + (r - 6) * sa), (cx + (r - 3) * ca, cy + (r - 3) * sa)], fill=hx("1e1610"))
        else:
            d.point((round(cx + (r - 4) * ca), round(cy + (r - 4) * sa)), fill=hx("4a3e2c"))

    def hand(frac, length, col, width=1):
        a = 2 * math.pi * frac
        d.line([(cx, cy), (round(cx + length * math.sin(a)), round(cy - length * math.cos(a)))], fill=col, width=width)

    hand(((hour % 12) + minute / 60) / 12, 6, hx("1a1410"), 2)
    hand(minute / 60, 9, hx("1a1410"))
    hand(0.62, 9, hx("a02020"))
    d.point((cx, cy), fill=BRASS_L)


def chair(img):
    """Micah's chair behind the desk: button-tufted oxblood leather, brass nail heads round the back, rolled arms."""
    d = ImageDraw.Draw(img)
    leather, lit, dark, crease = hx("5e2c1c"), hx("8a4a30"), hx("3a1a10"), hx("2e140c")
    d.rounded_rectangle([231, 63, 267, 104], 9, fill=hx("24100a"))
    d.rounded_rectangle([233, 65, 265, 104], 8, fill=leather)
    hgrad(img, (236, 70, 262, 100), hx("6a3422"), hx("44200e"))
    d = ImageDraw.Draw(img)
    buttons = []
    for j, y in enumerate(range(71, 101, 6)):
        for x in range(238 + (j % 2) * 4, 263, 8):
            buttons.append((x, y))
    for x, y in buttons:
        for nx, ny in ((x + 4, y + 6), (x - 4, y + 6)):
            if (nx, ny) in buttons:
                d.line([(x, y), (nx, ny)], fill=crease)
    for x, y in buttons:
        d.point((x - 2, y + 3), fill=lit if x < 252 else hx("6a3422"))
        d.point((x, y), fill=hx("140806"))
        d.point((x - 1, y - 1), fill=lit)
    for i in range(0, 31, 3):
        a = math.pi + math.pi * i / 30
        d.point((round(249 + 14 * math.cos(a)), round(72 + 7 * math.sin(a))), fill=BRASS)
    for y in range(74, 102, 3):
        d.point((234, y), fill=BRASS)
        d.point((264, y), fill=BRASS)
    # rolled arms either side
    for ax0, ax1, top in ((225, 236, lit), (262, 273, dark)):
        d.rounded_rectangle([ax0, 85, ax1, 104], 4, fill=leather)
        d.line([(ax0 + 2, 86), (ax1 - 2, 86)], fill=top)
        d.line([(ax0 + 1, 89), (ax1 - 1, 89)], fill=crease)
    light(img, "ellipse", [234, 66, 252, 96], hx("806040"), 0.3, 4)


def desk(img):
    d = ImageDraw.Draw(img)
    chair(img)
    d = ImageDraw.Draw(img)
    # the top: oak, its grain running along it, a lit edge and a dark lip
    d.polygon([(168, 110), (348, 110), (344, 101), (172, 101)], fill=hx("6a3e22"))
    for gy, gc in ((103, "5a3420"), (105, "74482a"), (107, "5e3820"), (108, "70442a")):
        d.line([(172 - (gy - 101) // 2, gy), (344 + (gy - 101) // 2, gy)], fill=hx(gc))
    noise(img, (170, 102, 346, 109), 3, 13)
    d = ImageDraw.Draw(img)
    d.line([(172, 101), (344, 101)], fill=hx("8a5a34"))
    d.rectangle([168, 110, 348, 112], fill=hx("3a2010"))
    d.line([(168, 110), (348, 110)], fill=hx("8a5a34"))
    # the modesty panel facing the client: no drawers this side, three raised panels between fluted pilasters
    vgrad(img, (176, 113, 340, 152), hx("4e2c18"), hx("361e10"))
    noise(img, (176, 113, 340, 152), 4, 11)
    d = ImageDraw.Draw(img)
    d.rectangle([176, 113, 340, 115], fill=hx("2a160a"))
    d.line([(176, 116), (340, 116)], fill=hx("6a4024"))
    for a, b in ((186, 230), (238, 278), (286, 330)):
        d.rectangle([a, 121, b, 144], fill=hx("462814"))
        d.line([(a, 121), (b, 121)], fill=hx("74482a"))
        d.line([(a, 121), (a, 144)], fill=hx("5e3820"))
        d.line([(a, 144), (b, 144)], fill=hx("24140a"))
        d.line([(b, 121), (b, 144)], fill=hx("2a160a"))
        d.rectangle([a + 4, 125, b - 4, 140], fill=hx("4e2c18"), outline=hx("2e180a"))
        d.line([(a + 5, 126), (b - 5, 126)], fill=hx("6a4024"))
    for px in (179, 233, 281, 335):
        for fx in (px, px + 2):
            d.line([(fx, 119), (fx, 146)], fill=hx("2a160a"))
        d.line([(px + 1, 119), (px + 1, 146)], fill=hx("5e3820"))
    d.rectangle([174, 148, 342, 152], fill=hx("2a160a"))
    d.line([(174, 148), (342, 148)], fill=hx("6a4024"))
    shadow(img, "rect", [176, 150, 344, 160], 0.55, 4)


def lamp(img, lamp_on=True):
    """The green banker's lamp: cased-glass shade on a brass harp, a pull chain, an oval brass foot."""
    d = ImageDraw.Draw(img)
    d.ellipse([187, 97, 205, 103], fill=BRASS_D)
    d.ellipse([188, 97, 204, 101], fill=BRASS)
    d.line([(191, 98), (199, 98)], fill=BRASS_L)
    d.rectangle([195, 89, 197, 99], fill=BRASS)
    d.line([(195, 90), (195, 98)], fill=BRASS_L)
    d.line([(197, 90), (197, 98)], fill=BRASS_D)
    d.rectangle([194, 93, 198, 94], fill=BRASS_D)
    green, green_l, green_d = ((hx("1e6a3a"), hx("6ac080"), hx("0e3a1e")) if lamp_on else
                               (hx("16402a"), hx("2e5e40"), hx("0a2214")))
    d.chord([184, 82, 210, 96], 180, 360, fill=green)
    d.arc([184, 82, 210, 96], 180, 360, fill=green_d)
    d.arc([187, 84, 207, 94], 200, 250, fill=green_l)
    d.line([(184, 89), (210, 89)], fill=BRASS)
    d.line([(185, 90), (209, 90)], fill=BRASS_D)
    if lamp_on:
        d.line([(188, 91), (206, 91)], fill=hx("fff0c0"))
    d.line([(204, 90), (204, 95)], fill=BRASS_L)
    d.point((204, 96), fill=BRASS)


def papers(img):
    """A green leather blotter with the case files on it, a typed report on top, an inkwell and a fountain pen."""
    d = ImageDraw.Draw(img)
    d.polygon([(229, 101), (277, 101), (280, 108), (226, 108)], fill=hx("244a30"))
    d.line([(229, 101), (277, 101)], fill=hx("3a6a46"))
    for c in ([(229, 101), (235, 101), (232, 108), (226, 108)], [(271, 101), (277, 101), (280, 108), (274, 108)]):
        d.polygon(c, fill=hx("8a6a40"))
    d.polygon([(237, 97), (263, 96), (266, 104), (235, 105)], fill=hx("8a7040"))
    d.polygon([(238, 95), (262, 94), (264, 101), (236, 102)], fill=hx("c4a460"))
    d.line([(236, 102), (264, 101)], fill=hx("7a6034"))
    d.line([(236, 103), (265, 102)], fill=hx("d0b470"))
    d.rectangle([254, 92, 259, 94], fill=hx("d4b470"))
    d.polygon([(240, 92), (259, 91), (261, 97), (238, 98)], fill=hx("ece4c8"))
    d.line([(240, 92), (259, 91)], fill=hx("fffae8"))
    for i, y in enumerate((93, 94, 95, 96)):
        d.line([(242, y), (257 - (i % 2) * 4, y - 1)], fill=hx("7a7468"))
    d.rectangle([243, 92, 245, 92], fill=hx("b0b0b8"))
    # the inkwell, and the pen lying across the blotter
    d.rectangle([229, 97, 233, 101], fill=hx("1a1a2a"))
    d.point((230, 98), fill=hx("6a6a8a"))
    d.rectangle([230, 96, 232, 96], fill=BRASS)
    d.line([(242, 106), (251, 104)], fill=hx("141418"))
    d.point((243, 106), fill=hx("5a5a64"))
    d.point((252, 104), fill=BRASS_L)


def ashtray(img):
    """A heavy glass ashtray: two stubbed butts and a cigarette left out in the notch, burned down and gone cold."""
    d = ImageDraw.Draw(img)
    d.ellipse([293, 98, 309, 103], fill=hx("26262c"))
    d.ellipse([293, 96, 309, 102], fill=hx("5a5a66"))
    d.arc([293, 96, 309, 102], 160, 290, fill=hx("b0b0bc"))
    d.ellipse([296, 97, 306, 100], fill=hx("1a1a1e"))
    d.line([(297, 99), (299, 98)], fill=hx("d8d0c0"))
    d.point((300, 98), fill=hx("4a4440"))
    d.point((301, 99), fill=hx("c8c0b0"))
    d.point((302, 99), fill=hx("8a8a8a"))
    d.line([(303, 98), (308, 96)], fill=hx("ece4d4"))
    d.point((309, 96), fill=hx("8a8484"))
    d.point((310, 95), fill=hx("4a4440"))


DESK_PHONE = (322, 103)
# Teddy's notes on the corner of the desk nearest the client's chair (screen coordinates)
CASH_BOX = (168, 99 + TOP, 189, 111 + TOP)


def desk_cash(img):
    """Twenty-two dollars: a twenty and two ones, fanned where Teddy laid them down."""
    d = ImageDraw.Draw(img)
    shadow(img, "rect", [171, 106, 187, 109], 0.4, 1)
    for pts, face in (([(171, 105), (180, 104), (181, 107), (172, 108)], "6a8a5a"),
                      ([(174, 103), (183, 103), (183, 106), (174, 106)], "6a8a5a"),
                      ([(177, 104), (186, 105), (185, 108), (176, 107)], "5a7a4a")):
        d.polygon(pts, fill=hx("a8c098"))
        cx = sum(p[0] for p in pts) // 4
        cy = sum(p[1] for p in pts) // 4
        d.line([(cx - 3, cy), (cx + 3, cy)], fill=hx(face))
        d.point((cx, cy), fill=hx("d8e4c0"))
    d.point((184, 106), fill=hx("2a3a24"))
    d.point((185, 106), fill=hx("2a3a24"))


def desk_props(img, lamp_on=True, storm=False, cash=False):
    lamp(img, lamp_on)
    papers(img)
    ashtray(img)
    candlestick_phone(img, *DESK_PHONE, dial=True)
    if cash:
        desk_cash(img)
    d = ImageDraw.Draw(img)
    if storm:
        return
    if not lamp_on:
        bottle(d, *DESK_BOTTLE)
        cup(d, *DESK_CUP)
        return
    # lamp pool of light
    light(img, "ellipse", [150, 70, 260, 130], hx("f0d890"), 0.55, 14)
    light(img, "polygon", [(186, 92), (210, 92), (232, 104), (166, 104)], hx("fff0c0"), 0.5, 3)


WINDOW = (352, 16, 470, 98)


def lights_out(img):
    """Act 3: the lamp is off. The room sinks into blue shadow; only the window and its neon spill stay lit."""
    x0, y0, x1, y1 = WINDOW
    glass = img.crop((x0, y0, x1 + 1, y1 + 1))
    shadow(img, "rect", [0, 0, W, H], 0.72, 0, hx("6a6a9a"))
    img.paste(glass, (x0, y0))
    light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("4a6aa8"), 0.2, 10)
    light(img, "ellipse", [380, 110, 480, 200], hx("ff3030"), 0.14, 20)
    # a red rim of HOTEL light catching the bottle on the desk
    bx, by = DESK_BOTTLE
    light(img, "rect", [bx + 6, by + 8, bx + 8, by + 22], hx("ff4a4a"), 0.35, 1)


def radiator(img):
    """A cast-iron column radiator in flaking silver paint, fed by a pipe out of the floor through a red valve."""
    d = ImageDraw.Draw(img)
    iron, iron_l, iron_d = hx("6a6a64"), hx("9e9e94"), hx("34342f")
    d.rectangle([365, 119, 367, 128], fill=iron_d)
    d.line([(365, 119), (365, 128)], fill=iron)
    d.rectangle([365, 119, 372, 121], fill=iron)
    d.line([(366, 119), (372, 119)], fill=iron_l)
    d.rectangle([366, 117, 369, 119], fill=iron_d)
    d.line([(367, 114), (367, 117)], fill=iron_d)
    d.ellipse([364, 112, 370, 115], fill=hx("8a2a20"))
    d.point((365, 113), fill=hx("d05a48"))
    for x in range(372, 452, 6):
        d.rectangle([x + 4, 106, x + 6, 108], fill=iron_d)
        d.rectangle([x + 4, 121, x + 6, 123], fill=iron_d)
    for x in range(372, 452, 6):
        d.rounded_rectangle([x, 104, x + 4, 126], 2, fill=iron)
        d.line([(x + 1, 106), (x + 1, 124)], fill=iron_l)
        d.line([(x + 4, 106), (x + 4, 124)], fill=iron_d)
        for by in (110, 116):
            d.point((x + 2, by), fill=iron_l)
            d.point((x + 3, by + 1), fill=iron_d)
            d.point((x + 2, by + 2), fill=iron_l)
    noise(img, (370, 104, 454, 126), 5, 21)
    d = ImageDraw.Draw(img)
    for rx, ry in ((381, 118), (405, 107), (430, 122), (446, 112)):
        d.point((rx, ry), fill=hx("6a4a30"))
    for fx in (373, 447):
        d.rectangle([fx, 126, fx + 3, 128], fill=iron_d)
    d.point((454, 106), fill=BRASS)
    d.point((455, 106), fill=BRASS_D)


def window(img, neon=True):
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WINDOW
    # the rain is animated in-game (Rain node in office.tscn)
    city(img, (x0, y0, x1, y1), seed=11, lit=0.28 if neon else 0.0, rain=False)
    # the red neon HOTEL blade sign on the building across, bulbs chasing round its frame (all dead in the blackout)
    d.line([(438, 49), (446, 49)], fill=hx("1a1418"))
    d.line([(438, 85), (446, 85)], fill=hx("1a1418"))
    d.rectangle([427, 42, 439, 92], fill=hx("1a0c10"), outline=hx("3a2a2e"))
    for i, by in enumerate(range(44, 92, 3)):
        on = neon and i % 3 != 1
        d.point((428, by), fill=hx("e8c060" if on else "3a3020"))
        d.point((438, by), fill=hx("e8c060" if neon and i % 3 != 2 else "3a3020"))
    for i, ch in enumerate("HOTEL"):
        dim = neon and ch == "T"
        text(img, (433, 50 + i * 9), ch, hx(("c83030" if dim else "ff5a5a") if neon else "3a2226"), size=8)
    if neon:
        light(img, "rect", [420, 40, 446, 94], hx("ff2a2a"), 0.35, 6)
    window_frame(img)
    d.rectangle([x0 - 8, y1 + 3, x1 + 8, y1 + 6], fill=hx("4a3020"))
    d.line([(x0 - 8, y1 + 3), (x1 + 8, y1 + 3)], fill=hx("7a5434"))
    d.line([(x0 - 8, y1 + 6), (x1 + 8, y1 + 6)], fill=hx("24140a"))
    radiator(img)
    # cold neon spill + blind stripes on the floor and wall
    light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("4a6aa8"), 0.18, 10)
    for i in range(6):
        y = 150 + i * 8
        light(img, "polygon", [(330 + i * 4, y), (440 + i * 6, y), (444 + i * 6, y + 3), (334 + i * 4, y + 3)],
              hx("8090c0"), 0.22, 1)
    if neon:
        light(img, "ellipse", [380, 110, 480, 200], hx("ff3030"), 0.12, 20)


def paint(door_state="closed", lamp_on=True, cab=None, holster=False, cash=False):
    """The office. cab: None (the filing cabinet shut) or the contents of its pulled-out middle drawer; holster: the
    revolver still hanging on the coat rack; cash: Teddy's money on the desk."""
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    door(img, door_state)
    diploma(img)
    cabinet(img, whiskey=lamp_on, open_=cab)
    coat_rack(img, holster=holster)
    clock(img)
    window(img)
    desk(img)
    desk_props(img, lamp_on, cash=cash)
    if not lamp_on:
        lights_out(img)
    img = tall(img, ceiling)
    if not lamp_on:
        shadow(img, "rect", [0, 0, W, TOP], 0.72, 0, hx("6a6a9a"))
    vignette(img, 0.55)
    return img


# =====================================================================================================================
# The storm after the alley: the power is out on the whole block, lamp and HOTEL sign dead. The cup and Micah's hat
# are on the desk (the bottle is in his hand until he sets it down). Painted twice: black, and under a lightning flash.
# =====================================================================================================================
STORM_HAT = (240, 89)       # art coordinates of the hat's bounding box top-left (22 x 13)
STORM_HAT_BOX = (238, 87 + TOP, 264, 103 + TOP)
STORM_BOTTLE_BOX = (212, 78 + TOP, 225, 105 + TOP)
# the glass below the blinds, where the lightning shows the reflection (screen coordinates)
STORM_GLASS_BOX = (348, 46 + TOP, 474, 102 + TOP)
STORM_REFLECTION_X = 392    # aligned with the real Micah at the scene's window entry
STORM_REFLECTION_SCALE = 0.92
STORM_REFLECTION_OPACITY = 0.45
STORM_REFLECTION_RISE = 4   # keep the eyes just above the real Micah's head
STORM_MICAH_REFLECTION_OFFSET = -16


def fedora(d, x, y):
    """Micah's fedora lying on the desk, its top-left at (x, y): 22 x 13."""
    felt, band, dark = hx("6e4a30"), hx("1a120e"), hx("4a3020")
    d.ellipse([x, y + 7, x + 21, y + 12], fill=dark)
    d.ellipse([x, y + 6, x + 21, y + 11], fill=felt)
    d.rounded_rectangle([x + 5, y, x + 16, y + 9], 3, fill=felt)
    d.line([(x + 9, y + 1), (x + 11, y + 3)], fill=dark)  # the pinch in the crown
    d.rectangle([x + 5, y + 6, x + 16, y + 7], fill=band)
    d.line([(x + 6, y + 1), (x + 6, y + 5)], fill=hx("8a6444"))


def storm_desk(img, hat=True, bottle=False):
    d = ImageDraw.Draw(img)
    cup(d, *DESK_CUP)
    if bottle:
        bottle_(d, *DESK_BOTTLE)
    if hat:
        fedora(d, *STORM_HAT)


bottle_ = bottle


def _bolt(img, seed):
    """A forked lightning bolt in the sky above the roofs, behind the window glass."""
    import random
    rng = random.Random(seed)
    d = ImageDraw.Draw(img)
    x, y = 384, 47
    pts = [(x, y)]
    while y < 74:
        x += rng.randint(-4, 3)
        y += rng.randint(3, 6)
        pts.append((x, y))
    d.line(pts, fill=hx("f4f6ff"), width=1)
    fx, fy = pts[len(pts) // 2]
    d.line([(fx, fy), (fx - 6, fy + 5), (fx - 8, fy + 11)], fill=hx("c8d4ff"))
    light(img, "polygon", [(p[0] - 1, p[1]) for p in pts] + [(p[0] + 2, p[1]) for p in pts[::-1]], hx("c8d4ff"), 0.5, 3)


def paint_storm(lit=False, hat=True, bottle=False, door_state="closed"):
    img = Image.new("RGB", (W, H))
    walls(img)
    floor(img)
    door(img, door_state)
    diploma(img)
    cabinet(img, whiskey=False)
    coat_rack(img, hat=False)
    clock(img, 1, 50)
    window(img, neon=False)
    desk(img)
    desk_props(img, lamp_on=False, storm=True)
    storm_desk(img, hat, bottle)
    x0, y0, x1, y1 = WINDOW
    if lit:
        # the sky flares white behind the roofs; the flash pours in cold and flat, hard on the side facing the glass
        sky = Image.new("RGB", (x1 - x0 + 1, y1 - y0 + 1), hx("b8c4e8"))
        glass = img.crop((x0, y0, x1 + 1, y1 + 1))
        img.paste(Image.blend(glass, sky, 0.3), (x0, y0))
        _bolt(img, 3)
        window_frame(img)
        shadow(img, "rect", [0, 0, W, H], 0.4, 0, hx("5a6a9a"))
        # the window's shape thrown across the floor, the mullion and bar as dark crosses in it
        light(img, "polygon", [(352, 98), (470, 98), (470, 240), (250, 240)], hx("c8d8ff"), 0.22, 6)
        shadow(img, "polygon", [(409, 98), (413, 98), (392, 240), (384, 240)], 0.25, 2)
        light(img, "rect", [x0 - 6, y0 - 6, x1 + 6, y1 + 6], hx("e8eeff"), 0.18, 6)
    else:
        window_frame(img)
        glass = img.crop((x0, y0, x1 + 1, y1 + 1))
        shadow(img, "rect", [0, 0, W, H], 0.9, 0, hx("2a2a4a"))
        img.paste(Image.blend(glass, Image.new("RGB", glass.size, hx("10141e")), 0.7), (x0, y0))
        light(img, "polygon", [(352, 16), (470, 16), (500, 200), (300, 200)], hx("3a4a78"), 0.12, 10)
    img = tall(img, ceiling)
    shadow(img, "rect", [0, 0, W, TOP], 0.45 if lit else 0.9, 0, hx("5a6a9a" if lit else "2a2a4a"))
    vignette(img, 0.6)
    return img


def window_frame(img):
    """The window's frame, mullion, sash lock and half-drawn venetian blinds (painted again over a repainted glass)."""
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = WINDOW
    wood, wood_l, wood_d = hx("3a2414"), hx("6a4a2c"), hx("1a0e06")
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=wood, width=4)
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=wood_d)
    d.line([(x0 - 3, y0 - 3), (x1 + 3, y0 - 3)], fill=wood_l)
    d.line([(x0 - 3, y0 - 3), (x0 - 3, y1 + 3)], fill=wood_l)
    d.rectangle([x0 - 1, y0 - 1, x1 + 1, y1 + 1], outline=wood_d)
    d.line([(411, y0), (411, y1)], fill=wood, width=3)
    d.line([(410, y0), (410, y1)], fill=wood_l)
    d.line([(x0, 56), (x1, 56)], fill=wood, width=2)
    d.line([(x0, 55), (x1, 55)], fill=wood_l)
    d.rectangle([408, 53, 414, 57], fill=hx("8a6a30"))
    d.line([(409, 54), (412, 54)], fill=hx("e0c070"))
    # slats lit along their tops; one pried down at Micah's eye level, the way he looks out at the street
    for y in range(y0, 44, 3):
        d.line([(x0, y), (x1, y)], fill=hx("9a9280"))
        d.line([(x0, y + 1), (x1, y + 1)], fill=hx("6a6452"))
    d.line([(374, 41), (388, 41)], fill=hx("12141c"))
    d.line([(374, 42), (388, 42)], fill=hx("9a9280"))
    d.line([(374, 43), (388, 43)], fill=hx("6a6452"))
    for tx in (x0 + 18, x1 - 18):
        d.line([(tx, y0), (tx, 44)], fill=hx("c8c0a8"))
    d.rectangle([x0, 44, x1, 46], fill=hx("7a7262"))
    d.line([(x0, 44), (x1, 44)], fill=hx("b4ac94"))
    d.line([(x0, 46), (x1, 46)], fill=hx("3e382c"))
    for cx, cy in ((x0 + 8, 64), (x0 + 11, 60)):
        d.line([(cx, 47), (cx, cy)], fill=hx("c8c0a0"))
        d.rectangle([cx - 1, cy, cx + 1, cy + 3], fill=hx("a89870"))
        d.point((cx, cy + 3), fill=hx("6a5a3a"))


def _bez(p0, p1, p2, n=24):
    return [((1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0],
             (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1]) for u in (i / (n - 1) for i in range(n))]


def _tube(d, pts, r0, r1, fill=255, S=4):
    """Circles along a polyline (crop pixels), radius tapering r0 -> r1, drawn on a canvas S times larger."""
    import numpy as np
    pts = [np.array(p, float) for p in pts]
    seg = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]
    total, run = max(sum(seg), 1e-6), 0.0
    for a, b, L in zip(pts, pts[1:], seg):
        for i in range(max(2, int(L * S * 2))):
            u = i / max(1, int(L * S * 2) - 1)
            x, y = (a + (b - a) * u) * S
            r = (r0 + (r1 - r0) * (run + L * u) / total) * S
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill)
        run += L


def _poly(d, pts, fill=255, S=4):
    d.polygon([(x * S, y * S) for x, y in pts], fill=fill)


def _ell(d, cx, cy, rx, ry, fill=255, S=4):
    d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=fill)


def reflection(glass, stage):
    """The lightning shows Micah in the window glass, from the waist up (the sill cuts him off), and the thing holding
    him. stage 1: a horned shadow looms behind his reflection, one claw over his shoulder and an arm across his chest;
    stage 2: it bows over him, a hand over his mouth, and the dark rises up him to the neck.
    glass: the lit crop of STORM_GLASS_BOX (RGB); returns it with the reflection painted on."""
    from .sprites import MICAH_HATLESS, FW, FH, figure, pose
    import numpy as np
    import random
    S = 4
    rng = random.Random(stage * 7)
    base = glass.convert("RGBA")
    w, h = base.size
    sill = h - 5          # the glass ends on the sill (art y 98)
    cx = STORM_REFLECTION_X - STORM_GLASS_BOX[0]
    # Micah's reflection: faced towards the room, cut off at the waist, cold and translucent
    fig = figure(MICAH_HATLESS, pose(8), FW, FH)
    fig = fig.crop(fig.getbbox())
    bust = fig.crop((0, 0, fig.width, int(fig.height * 0.48)))
    k = 31 / bust.height
    bust = bust.resize((round(bust.width * k), 31), Image.BOX)
    a = np.array(bust).astype(float)
    tone = a[..., :3].mean(axis=2, keepdims=True)
    a[..., :3] = tone * np.array([0.62, 0.68, 0.9]) + np.array([16, 20, 34])
    a[..., 3] = np.where(a[..., 3] > 90, 225 if stage == 1 else 120, 0)
    bust = Image.fromarray(a.clip(0, 255).astype("uint8"))
    bx, by = cx - bust.width // 2, sill - bust.height
    if stage == 1:
        bx += STORM_MICAH_REFLECTION_OFFSET
    top = by  # his head's top

    # --- the demon, painted 4x and brought down ---------------------------------------------------------------------
    big = (w * S, h * S)
    body, arms = Image.new("L", big, 0), Image.new("L", big, 0)
    detail = Image.new("L", big, 0)   # lighter muscle and horn ridges, inside the silhouette
    db, da, dd = ImageDraw.Draw(body), ImageDraw.Draw(arms), ImageDraw.Draw(detail)
    hx_, hy = (cx - 9, top + 4) if stage == 1 else (cx, top - 1)  # at his ear; then over him
    sy = top + 6 if stage == 1 else top + 5       # shoulder line, hunched up level with his chin
    # skull: long, narrow, a pointed jaw, a heavy brow
    _ell(db, hx_, hy, 4.6, 5.4)
    _poly(db, [(hx_ - 4, hy + 1), (hx_ + 4, hy + 1), (hx_ + 1.6, hy + 9), (hx_ - 1.6, hy + 9)])
    _poly(db, [(hx_ - 5.5, hy - 1), (hx_ + 5.5, hy - 1), (hx_ + 4, hy + 1.5), (hx_ - 4, hy + 1.5)])
    for k_ in (-1, 1):  # ram-curled horns, thick at the skull, swept out and up to a point
        curve = (_bez((hx_ + k_ * 3, hy - 3), (hx_ + k_ * 12, hy - 4), (hx_ + k_ * 11, hy - 15)) if stage == 1 else
                 _bez((hx_ + k_ * 3, hy - 3), (hx_ + k_ * 9, hy - 9), (hx_ + k_ * 15, hy - 3)))
        _tube(db, curve, 2.1, 0.35)
        for i in range(3, len(curve) - 4, 3):  # ridges
            x, y = curve[i]
            _ell(dd, x, y, 1.3, 0.35)
    # neck and great hunched shoulders, the trunk spreading to the sill
    _poly(db, [(hx_ - 3, hy + 6), (hx_ + 3, hy + 6), (cx + 6, sy), (cx - 6, sy)])
    for k_ in (-1, 1):
        _ell(db, cx + k_ * 15, sy + 3, 9, 6.5)
        _ell(dd, cx + k_ * 16, sy + 1, 4.5, 2, fill=255)  # the deltoid catching the light
    spread = 27 if stage == 1 else 31
    _poly(db, [(cx - 22, sy + 2), (cx + 22, sy + 2), (cx + spread, h), (cx - spread, h)])
    # smoke curling off the flanks: the thing doesn't end, it frays
    for k_ in (-1, 1):
        for j in range(3):
            y0 = sy + 9 + j * 8 + rng.uniform(-1, 1)
            x0 = cx + k_ * (22 + (y0 - sy) * (spread - 22) / (h - sy))
            end = (x0 + k_ * rng.uniform(7, 11), y0 - rng.uniform(8, 13))
            _tube(db, _bez((x0 - k_ * 3, y0 + 2), (x0 + k_ * 7, y0), end), 2.2, 0.2)
    # ribs and the line of the arm along the flanks
    for k_ in (-1, 1):
        for j in range(3):
            y = sy + 12 + j * 4
            _tube(dd, _bez((cx + k_ * 13, y), (cx + k_ * 18, y - 1.5), (cx + k_ * 21, y + 1)), 0.35, 0.25)

    def claw(d, start, tips, r=0.75):
        for tip in tips:
            mid = ((start[0] + tip[0]) / 2 + (tip[1] - start[1]) * 0.15, (start[1] + tip[1]) / 2 - 1)
            _tube(d, _bez(start, mid, tip), r, 0.15)

    if stage == 1:
        mx = cx + STORM_MICAH_REFLECTION_OFFSET  # the grip follows his painted reflection, not the real Micah
        # the far arm comes round his waist and across his chest, its claws spread over his heart
        _tube(da, [(cx - 17, sy + 4), (mx - 21, sy + 16), (mx - 13, sy + 22), (mx - 6, sy + 20)], 2.6, 1.6)
        claw(da, (mx - 6, sy + 20), [(mx + 3, sy + 13), (mx + 4, sy + 16), (mx + 4, sy + 19), (mx + 1, sy + 22)])
        # the near hand has come over his shoulder from behind, long fingers hooked down his collarbone
        _ell(da, mx + 10, sy + 1, 2.4, 1.8)
        claw(da, (mx + 10, sy + 1), [(mx + 3, sy + 7), (mx + 5, sy + 9), (mx + 8, sy + 10), (mx + 12, sy + 8)])
    else:
        # one hand clamped over his mouth, the other gripping the crown of his head
        _tube(da, [(cx - 17, sy + 4), (cx - 19, sy + 14), (cx - 11, top + 11), (cx - 5, top + 9)], 2.7, 1.7)
        claw(da, (cx - 5, top + 9), [(cx + 4, top + 7), (cx + 5, top + 9), (cx + 4, top + 11), (cx + 1, top + 13)])
        _tube(da, [(cx + 16, sy + 2), (cx + 13, top - 2), (cx + 6, top - 3)], 2.4, 1.6)
        claw(da, (cx + 6, top - 3), [(cx - 3, top), (cx - 1, top + 2), (cx + 1, top + 3), (cx + 4, top + 3)])
        # the dark welling up him from the sill to the throat
        rise = [(bx - 3, h), (bx - 3, top + 15)]
        for i in range(0, bust.width + 7, 2):
            rise.append((bx - 3 + i, top + 13 + rng.uniform(-1.5, 2.5)))
        rise += [(bx + bust.width + 3, top + 15), (bx + bust.width + 3, h)]
        _poly(da, rise)
        for i in range(4):
            x0 = bx + 2 + i * bust.width / 4
            _tube(da, _bez((x0, top + 14), (x0 + rng.uniform(-3, 3), top + 11), (x0 + rng.uniform(-2, 2), top + 8)),
                  1.2, 0.2)

    def down(m, cut=110):
        m = np.array(m.resize((w, h), Image.BOX))
        return np.where(m > cut, 1.0, 0.0)

    m_body, m_arms, m_det = down(body), down(arms), down(detail, 70)

    def layer(mask, rgb, alpha=245):
        arr = np.zeros((h, w, 4), np.uint8)
        arr[..., :3] = rgb
        arr[..., 3] = (mask * alpha).astype(np.uint8)
        return Image.fromarray(arr)

    def rim(mask):
        """The flash catches the top and the window-side (left) edges of a shape."""
        up = np.zeros_like(mask)
        up[1:] = mask[:-1]
        left = np.zeros_like(mask)
        left[:, 1:] = mask[:, :-1]
        return mask * (1 - up), mask * (1 - left) * (1 - (mask * (1 - up)))

    shade = (9, 7, 14)
    out = Image.new("RGBA", base.size)
    out.alpha_composite(layer(m_body, shade))
    out.alpha_composite(layer(m_body * m_det, (30, 28, 44)))
    r_top, r_side = rim(m_body)
    out.alpha_composite(layer(r_top, (92, 102, 140), 220))
    out.alpha_composite(layer(r_side, (58, 64, 92), 200))
    out.alpha_composite(bust, (bx, by))
    out.alpha_composite(layer(m_arms, shade))
    a_top, a_side = rim(m_arms)
    out.alpha_composite(layer(a_top, (86, 94, 130), 210))
    out.alpha_composite(layer(a_side, (52, 58, 86), 190))
    px = ImageDraw.Draw(out)
    # eyes: slanted coals with a bloom; a seam of teeth in the jaw
    for k_ in (-1, 1):
        ex, ey = round(hx_ + k_ * 2), round(hy)
        px.point((ex, ey), fill=(255, 92, 60, 255))
        px.point((ex + k_, ey - 1), fill=(200, 36, 28, 255))
        for ox, oy in ((0, 1), (-k_, 0)):
            q = out.getpixel((ex + ox, ey + oy))
            out.putpixel((ex + ox, ey + oy), (max(q[0], 90), q[1], q[2], 255))
    for i in range(-2, 3):
        px.point((round(hx_) + i, round(hy + 5 + (i % 2))), fill=(118, 110, 104, 255) if stage == 2 or i % 2 else
                 (70, 64, 62, 255))
    # Shrink around Micah's centerline and the sill, fading only the apparition, not the window behind it.
    inverse = 1 / STORM_REFLECTION_SCALE
    out = out.transform(out.size, Image.Transform.AFFINE,
                        (inverse, 0, cx * (1 - inverse), 0, inverse,
                         sill * (1 - inverse) + STORM_REFLECTION_RISE * inverse),
                        Image.Resampling.NEAREST)
    out.putalpha(out.getchannel("A").point(lambda alpha: round(alpha * STORM_REFLECTION_OPACITY)))
    base.alpha_composite(out)
    # the reflection is in the glass: the window's mullion, bar and sill stay in front of it
    g = np.array(glass.convert("RGBA"))
    o = np.array(base)
    for (x0, y0, x1, y1) in ((410 - 348, 0, 413 - 348, h), (0, 55 - 46, w, 58 - 46), (0, sill, w, h)):
        o[y0:y1, x0:x1] = g[y0:y1, x0:x1]
    return Image.fromarray(o).convert("RGB")

def ceiling(img):
    d = ImageDraw.Draw(img)
    vgrad(img, (0, 0, W - 1, TOP), hx("1e1c16"), hx("3c3a2c"))
    for x in range(0, W, 8):
        d.line([(x, 9), (x, TOP)], fill=hx("2e2c24"))
        d.line([(x + 3, 9), (x + 3, TOP)], fill=hx("38362a"))
    noise(img, (0, 0, W - 1, TOP), 4, 41)
    # crown moulding
    d.rectangle([0, 0, W - 1, 4], fill=hx("16120c"))
    d.rectangle([0, 5, W - 1, 7], fill=hx("4a3424"))
    d.line([(0, 5), (W, 5)], fill=hx("6a4c34"))
    d.line([(0, 8), (W, 8)], fill=hx("24160e"))
    # the water stain started up here
    shadow(img, "ellipse", [244, 8, 306, 44], 0.3, 8, hx("806040"))
    d.line([(424, 6), (420, 14), (423, 22), (420, 30)], fill=hx("26241c"))
    # ceiling bulb on a cord, switched off
    d.line([(300, 0), (300, 14)], fill=hx("16120c"))
    d.ellipse([297, 14, 303, 21], fill=hx("6a6858"))
    d.point((299, 16), fill=hx("a8a690"))


GLINT_FRAMES = 5
GLINT_SIZE = 7


def ring_glint():
    """A horizontal strip of GLINT_FRAMES 7x7 frames: a four-pointed sparkle that flares from the ring's highlight
    and fades back. The centre pixel (3, 3) sits on the highlight."""
    strip = Image.new("RGBA", (GLINT_SIZE * GLINT_FRAMES, GLINT_SIZE))
    core, arm, tip = (255, 250, 220, 255), (255, 236, 170, 220), (255, 224, 140, 120)
    for f, reach in enumerate((0, 1, 3, 2, 1)):
        ox, c = f * GLINT_SIZE, GLINT_SIZE // 2
        strip.putpixel((ox + c, c), core)
        for r in range(1, reach + 1):
            col = arm if r < reach or reach == 1 else tip
            for dx, dy in ((r, 0), (-r, 0), (0, r), (0, -r)):
                strip.putpixel((ox + c + dx, c + dy), col)
    return strip


def build():
    base = paint()
    pal = palette_of(paint(holster=True), 128)  # the revolver's steel and walnut need their own inks
    px = pixelize(base, pal)
    save(px, "rooms", "office.png")
    for state in ("ajar", "open"):
        save(pixelize(paint(door_state=state), pal).crop(DOOR_BOX), "rooms", f"office_door_{state}.png")
    overlays = [("cabinet_open", CAB_OPEN_BOX, {"cab": ()}), ("cabinet_lockpick", CAB_PICKS_BOX, {"cab": ("lockpick",)}),
                ("holster", HOLSTER_BOX, {"holster": True}), ("cash", CASH_BOX, {"cash": True})]
    for name, box, kw in overlays:
        save(pixelize(paint(**kw), pal).crop(box), "rooms", f"office_{name}.png")
    # Act 3: the lamp off, the whiskey on the desk; the overlays that can still show get dark twins
    dark = paint(lamp_on=False)
    dark_pal = palette_of(dark, 128)
    save(pixelize(dark, dark_pal), "rooms", "office_act3.png")
    for state in ("ajar", "open"):
        save(pixelize(paint(door_state=state, lamp_on=False), dark_pal).crop(DOOR_BOX), "rooms",
             f"office_act3_door_{state}.png")
    for name, box, kw in overlays:
        if name != "holster":  # the gun went out with Micah in Act 1: by Act 3 the rack holds only the coat
            save(pixelize(paint(lamp_on=False, **kw), dark_pal).crop(box), "rooms", f"office_act3_{name}.png")
    # the ring is only a glint of gold on the desk: two bright pixels and a shadowed band
    ring = Image.new("RGBA", (3, 2))
    d = ImageDraw.Draw(ring)
    d.point((0, 0), fill=hx("b08838"))
    d.point((1, 0), fill=hx("f0d070"))
    d.point((2, 0), fill=hx("c89a40"))
    d.point((1, 1), fill=hx("6a5020"))
    save(ring, "rooms", "office_ring.png")
    save(ring_glint(), "rooms", "office_ring_glint.png")
    build_storm()
    sprite = Image.new("RGBA", (10, 12))
    cup(ImageDraw.Draw(sprite), 0, 0)
    save(sprite, "rooms", "office_cup.png")
    return px


def build_storm():
    for lit in (False, True):
        suffix = "_lit" if lit else ""
        base = paint_storm(lit)
        pal = palette_of(base, 128)
        save(pixelize(base, pal), "rooms", f"office_storm{suffix}.png")
        # the hat taken off the desk, the bottle set down on it: each overlay crops the same spot of a repaint

        save(pixelize(paint_storm(lit, hat=False, bottle=True), pal).crop(STORM_BOTTLE_BOX), "rooms",
             f"office_storm_bottle{suffix}.png")
        save(pixelize(paint_storm(lit, hat=False), pal).crop(STORM_HAT_BOX), "rooms",
             f"office_storm_no_hat{suffix}.png")
        if lit:
            glass = pixelize(base, pal).crop(STORM_GLASS_BOX)
            for stage in (1, 2):
                save(reflection(glass, stage), "rooms", f"office_storm_demon_{stage}.png")
        else:
            for state in ("ajar", "open"):
                save(pixelize(paint_storm(door_state=state), pal).crop(DOOR_BOX), "rooms",
                     f"office_storm_door_{state}.png")
    print("office_storm overlays: hat", STORM_HAT_BOX[:2], "bottle", STORM_BOTTLE_BOX[:2], "glass",
          STORM_GLASS_BOX[:2], "door", DOOR_BOX[:2])