"""Procedural character sprites: parts drawn on layers, auto-shaded, then outlined."""
import math
from PIL import Image, ImageDraw
from .common import hx, mix, mul, save

LIGHT, LIGHT_BAND, DARK, DARK_BAND, BOTTOM = 1.16, 1.07, 0.72, 0.86, 0.92
FEATURE = hx("241816")
MOUTH = hx("68262c")


def _opaque(px, w, h, x, y):
    return 0 <= x < w and 0 <= y < h and px[x, y][3]


def _shade(layer):
    """Applies broad, readable highlight and shadow bands from an upper-left key light."""
    px = layer.load()
    w, h = layer.size
    out = layer.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            c = px[x, y]
            if c[3] == 0:
                continue
            f = 1.0
            bright = sum(1 for dx, dy in ((-1, 0), (0, -1), (-1, -1)) if not _opaque(px, w, h, x + dx, y + dy))
            dark = sum(1 for dx, dy in ((1, 0), (0, 1), (1, 1)) if not _opaque(px, w, h, x + dx, y + dy))
            if bright >= 2:
                f *= LIGHT
            elif bright == 1 or not _opaque(px, w, h, x - 2, y) or not _opaque(px, w, h, x, y - 2):
                f *= LIGHT_BAND
            if dark >= 2:
                f *= DARK
            elif dark == 1:
                f *= DARK_BAND
            if not _opaque(px, w, h, x, y + 2) or not _opaque(px, w, h, x + 2, y):
                f *= BOTTOM
            if f != 1.0:
                op[x, y] = mul(c[:3], f) + (255,)
    return out


def _outline(img):
    px = img.load()
    w, h = img.size
    out = img.copy()
    op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][3]:
                continue
            best, shadow_side = None, False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3]:
                    c = px[nx, ny]
                    if best is None or sum(c[:3]) < sum(best[:3]):
                        best = c
                    shadow_side = shadow_side or nx < x or ny < y
            if best:
                op[x, y] = mul(best[:3], 0.14 if shadow_side else 0.2) + (255,)
    return out


class Fig:
    def __init__(self, spec):
        self.s = spec
        self.fw, self.fh = spec.get("frame", (40, 80))
        self.k = spec.get("height", 68) / 68
        self.wk = spec.get("wide", 1.0)
        self.layers = []
        self.bob = 0

    def X(self, u):
        return round(self.fw / 2 + u * self.wk * self.k)

    def Y(self, u):
        return round(self.fh - 2 - (68 - u) * self.k + self.bob)

    def P(self, u, v):
        return (self.X(u), self.Y(v))

    def layer(self):
        im = Image.new("RGBA", (self.fw, self.fh))
        self.layers.append(im)
        return ImageDraw.Draw(im)

    def render(self):
        out = Image.new("RGBA", (self.fw, self.fh))
        for l in self.layers:
            out.alpha_composite(_shade(l))
        return _outline(out)


def _limb(d, a, b, w, col):
    d.line([a, b], fill=col, width=w)
    r = max(1.5, w / 2 - 0.4)
    for p in (a, b):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def _front_shoe(d, foot, col):
    d.polygon([(foot[0] - 4, foot[1] - 1), (foot[0] + 4, foot[1] - 1), (foot[0] + 5, foot[1] + 2),
               (foot[0] - 5, foot[1] + 2)], fill=col)


def _side_shoe(d, foot, col):
    d.polygon([(foot[0] - 3, foot[1] - 1), (foot[0] + 5, foot[1] - 1), (foot[0] + 6, foot[1] + 2),
               (foot[0] - 3, foot[1] + 2)], fill=col)


def _face_front(d, f, s, talk, hair):
    brow = mix(hair or FEATURE, FEATURE, 0.35) if hair else FEATURE
    d.line([f.P(-4, 10.5), f.P(-1.5, 10.5)], fill=brow)
    d.line([f.P(1.5, 10.5), f.P(4, 10.5)], fill=brow)
    d.rectangle([f.X(-4), f.Y(12), f.X(-3), f.Y(12)], fill=FEATURE)
    d.rectangle([f.X(3), f.Y(12), f.X(4), f.Y(12)], fill=FEATURE)
    nose = mix(s["skin"], FEATURE, 0.33)
    d.line([f.P(0, 12), f.P(0, 15)], fill=nose)
    d.point(f.P(0, 15), fill=mul(nose, 0.85))
    if s.get("mustache"):
        d.rectangle([f.X(-3), f.Y(15), f.X(3), f.Y(16)], fill=hair or hx("302018"))
    if talk:
        d.rectangle([f.X(-2), f.Y(17), f.X(2), f.Y(18)], fill=MOUTH)
    else:
        d.line([f.P(-2, 17), f.P(2, 17)], fill=mix(s["skin"], FEATURE, 0.45))
    d.line([f.P(-2, 19), f.P(2, 19)], fill=mul(s["skin"], 0.8))


def _face_side(d, f, s, talk, hair):
    brow = mix(hair or FEATURE, FEATURE, 0.35) if hair else FEATURE
    d.line([f.P(0.5, 10.5), f.P(3.2, 10.5)], fill=brow)
    d.rectangle([f.X(2), f.Y(12), f.X(3), f.Y(12)], fill=FEATURE)
    d.line([f.P(-1, 12), f.P(-1, 15)], fill=mul(s["skin"], 0.82))
    if s.get("mustache"):
        d.line([f.P(3, 16), f.P(6, 16)], fill=hair or hx("302018"), width=2)
    d.line([f.P(3, 18), f.P(5, 18)], fill=MOUTH if talk else mix(s["skin"], FEATURE, 0.4), width=2 if talk else 1)
    d.point(f.P(-4, 13), fill=mul(s["skin"], 0.82))


def _side(f, phase, walking, talk):
    s = f.s
    a = math.sin(phase) * 0.52 if walking else 0.0
    if walking:
        f.bob = -1 if abs(math.sin(phase)) < 0.5 else 0
    lw = max(4, round(5.4 * f.k))
    hip = f.P(0, 48)
    leg_len = (66 - 48) * f.k

    def leg(ang, col, lift):
        d = f.layer()
        foot = (hip[0] + leg_len * math.sin(ang), min(f.Y(66) - lift, hip[1] + leg_len * math.cos(ang) - lift))
        knee = ((hip[0] + foot[0]) / 2 + 1.5, (hip[1] + foot[1]) / 2)
        _limb(d, hip, knee, lw, col)
        _limb(d, knee, foot, lw, col)
        _side_shoe(d, foot, s["shoes"])

    back_lift = 2 if walking and math.cos(phase) < -0.3 else 0
    front_lift = 2 if walking and math.cos(phase) > 0.3 else 0
    # back arm
    d = f.layer()
    sh = f.P(0, 24)
    hand = (sh[0] + 17 * f.k * math.sin(a * 0.9), sh[1] + 17 * f.k * math.cos(a * 0.9))
    _limb(d, sh, hand, lw, mul(s["coat"], 0.8))
    d.rectangle([hand[0] - 2, hand[1] - 1, hand[0] + 1, hand[1] + 2], fill=mul(s["skin"], 0.85))
    leg(-a, mul(s["pants"], 0.8), back_lift)
    leg(a, s["pants"], front_lift)
    # torso / coat
    d = f.layer()
    hem = 48 + s.get("coat_len", 8)
    d.polygon([f.P(-6, 22), f.P(5, 21), f.P(8, hem), f.P(-7, hem)], fill=s["coat"])
    d.polygon([f.P(1, 22), f.P(5, 22), f.P(3, 33)], fill=s.get("shirt", hx("d8d0c0")))
    if s.get("belt"):
        d.line([f.P(-6, 38), f.P(6, 38)], fill=mul(s["coat"], 0.65), width=2)
    if s.get("apron"):
        d.polygon([f.P(1, 37), f.P(7, 37), f.P(8, hem + 6), f.P(2, hem + 6)], fill=s["apron"])
    d.line([f.P(4.5, 22), f.P(2.5, 33)], fill=mul(s["coat"], 0.72), width=2)
    d.line([f.P(-4.5, 23), f.P(-5.5, hem - 2)], fill=mul(s["coat"], 0.88))
    # front arm
    d = f.layer()
    hand = (sh[0] + 17 * f.k * math.sin(-a * 0.9), sh[1] + 17 * f.k * math.cos(-a * 0.9))
    _limb(d, sh, hand, lw, s["coat"])
    d.rectangle([hand[0] - 2, hand[1] - 1, hand[0] + 1, hand[1] + 2], fill=s["skin"])
    # head
    d = f.layer()
    d.rectangle([f.X(-2), f.Y(18), f.X(3), f.Y(25)], fill=mul(s["skin"], 0.82))
    d.ellipse([f.X(-6), f.Y(5), f.X(5), f.Y(21)], fill=s["skin"])
    d.polygon([f.P(1, 18), f.P(5, 20), f.P(3, 22), f.P(-2, 21)], fill=mul(s["skin"], 0.94))
    d.polygon([f.P(4, 11.5), f.P(7, 14.5), f.P(4, 17)], fill=s["skin"])
    hair = s.get("hair")
    if hair and not s.get("bald"):
        d.chord([f.X(-6), f.Y(4), f.X(5), f.Y(16)], 180, 360, fill=hair)
        d.rectangle([f.X(-6), f.Y(9), f.X(-2), f.Y(17)], fill=hair)
    _face_side(d, f, s, talk, hair)
    _hat(f, "side")


def _front(f, phase, walking, talk, back=False):
    s = f.s
    lw = max(4, round(5.4 * f.k))
    lift_l = 3 if walking and math.sin(phase) > 0.3 else 0
    lift_r = 3 if walking and math.sin(phase) < -0.3 else 0
    if walking and (lift_l or lift_r):
        f.bob = -1
    for side, lift in ((-1, lift_l), (1, lift_r)):
        d = f.layer()
        hip = f.P(4 * side, 48)
        foot = (f.X(5.2 * side), f.Y(66) - lift)
        _limb(d, hip, foot, lw, s["pants"])
        _front_shoe(d, foot, s["shoes"])
    d = f.layer()
    hem = 48 + s.get("coat_len", 8)
    d.polygon([f.P(-8, 22), f.P(8, 22), f.P(10, hem), f.P(-10, hem)], fill=s["coat"])
    if not back:
        d.polygon([f.P(-4, 22), f.P(4, 22), f.P(0, 35)], fill=s.get("shirt", hx("d8d0c0")))
        if s.get("tie"):
            d.polygon([f.P(-1, 22), f.P(1, 22), f.P(1.5, 31), f.P(0, 35), f.P(-1.5, 31)], fill=s["tie"])
        d.line([f.P(-4, 22), f.P(0, 35)], fill=mul(s["coat"], 0.7), width=2)
        d.line([f.P(4, 22), f.P(0, 35)], fill=mul(s["coat"], 1.12), width=2)
        if s.get("buttons"):
            for v in (36, 40, 44):
                d.rectangle([f.X(-2), f.Y(v), f.X(-1), f.Y(v) + 1], fill=s["buttons"])
                d.rectangle([f.X(1), f.Y(v), f.X(2), f.Y(v) + 1], fill=s["buttons"])
        if s.get("apron"):
            d.rectangle([f.X(-7), f.Y(37), f.X(7), f.Y(hem + 6)], fill=s["apron"])
    if s.get("belt"):
        d.line([f.P(-8, 38), f.P(8, 38)], fill=mul(s["coat"], 0.66), width=2)
        if not back:
            d.rectangle([f.X(-1), f.Y(36), f.X(1), f.Y(38)], fill=hx("b89a50"))
    sw = math.sin(phase) * 2 if walking else 0
    for side in (-1, 1):
        d = f.layer()
        sh = f.P(9 * side, 24)
        hand = (f.X(11.5 * side), f.Y(42) + round(sw * side))
        _limb(d, sh, hand, lw, s["coat"])
        d.rectangle([hand[0] - 2, hand[1], hand[0] + 1, hand[1] + 3], fill=s["skin"])
    d = f.layer()
    d.rectangle([f.X(-2), f.Y(18), f.X(2), f.Y(24)], fill=mul(s["skin"], 0.82))
    d.ellipse([f.X(-6.5), f.Y(5), f.X(6.5), f.Y(21)], fill=s["skin"])
    hair = s.get("hair")
    if back:
        if hair and not s.get("bald"):
            d.ellipse([f.X(-6.5), f.Y(4), f.X(6.5), f.Y(18)], fill=hair)
            d.rectangle([f.X(-5), f.Y(11), f.X(5), f.Y(18)], fill=hair)
    else:
        if hair and not s.get("bald"):
            d.chord([f.X(-6.5), f.Y(4), f.X(6.5), f.Y(15)], 180, 360, fill=hair)
            d.rectangle([f.X(-6), f.Y(10), f.X(-4), f.Y(16)], fill=hair)
            d.rectangle([f.X(4), f.Y(10), f.X(6), f.Y(16)], fill=hair)
        _face_front(d, f, s, talk, hair)
    _hat(f, "back" if back else "front")


def _hat(f, view):
    s = f.s
    hat = s.get("hat")
    if not hat:
        return
    d = f.layer()
    c = s["hat_col"]
    if hat == "fedora":
        if view == "side":
            d.polygon([f.P(-5.5, 1.5), f.P(4, 1), f.P(6, 8), f.P(-6, 8.5)], fill=c)
            d.line([f.P(-5.5, 7), f.P(5.5, 7)], fill=s.get("band", hx("1a1010")), width=2)
            d.line([f.P(-10, 9), f.P(9, 8)], fill=c, width=3)
        else:
            d.polygon([f.P(-6, 1.5), f.P(6, 1.5), f.P(6.5, 8), f.P(-6.5, 8)], fill=c)
            d.line([f.P(-1.5, 1.5), f.P(0, 3.5)], fill=mul(c, 0.6))
            d.line([f.P(-6.5, 7), f.P(6.5, 7)], fill=s.get("band", hx("1a1010")), width=2)
            d.ellipse([f.X(-11), f.Y(7.5), f.X(11), f.Y(10.5)], fill=c)
    elif hat == "cap":
        d.chord([f.X(-7), f.Y(4), f.X(7), f.Y(14)], 180, 360, fill=c)
        if view == "side":
            d.line([f.P(1.5, 8.5), f.P(9, 9)], fill=mul(c, 0.8), width=3)
        else:
            d.ellipse([f.X(-7), f.Y(7.5), f.X(7), f.Y(10.5)], fill=mul(c, 0.85))
    elif hat == "pillbox":
        d.rectangle([f.X(-4.5), f.Y(2.5), f.X(4.5), f.Y(8.5)], fill=c)
        d.line([f.P(-4.5, 7), f.P(4.5, 7)], fill=hx("d8b040"), width=2)


def frame(spec, view, phase=0.0, walking=False, talk=False):
    f = Fig(spec)
    if view == "side":
        _side(f, phase, walking, talk)
    else:
        _front(f, phase, walking, talk, back=(view == "back"))
    return f.render()


MICAH = dict(skin=hx("d8a480"), hair=hx("2a1d16"), hat="fedora", hat_col=hx("584337"), band=hx("17100d"),
             coat=hx("b18a43"), coat_len=10, belt=True, shirt=hx("e3d7bf"), tie=hx("7b1f2a"),
             pants=hx("4a433b"), shoes=hx("2b1b14"))
TEDDY = dict(skin=hx("e7c1a3"), hair=hx("9f7430"), mustache=True, coat=hx("dfd2a7"), coat_len=4,
             shirt=hx("f5efe2"), tie=hx("3e7cad"), pants=hx("ccb78d"), shoes=hx("efe7d5"))
CONCIERGE = dict(skin=hx("e0b090"), hair=hx("8c8b84"), mustache=True, coat=hx("7a1f31"), coat_len=4,
                 shirt=hx("f6efe2"), tie=hx("171717"), pants=hx("2a1b24"), shoes=hx("181213"),
                 buttons=hx("dcb548"))
BELLBOY = dict(skin=hx("ca9272"), hair=hx("3a2418"), hat="pillbox", hat_col=hx("c62924"), coat=hx("cf2e26"),
               coat_len=0, shirt=hx("f4ebdf"), pants=hx("312028"), shoes=hx("181213"), buttons=hx("f0c74b"),
               height=58)
SAL = dict(skin=hx("c99878"), hair=hx("171313"), hat="cap", hat_col=hx("47525c"), coat=hx("394148"), coat_len=4,
           shirt=hx("b5ab97"), pants=hx("26262c"), shoes=hx("141414"), frame=(48, 84), height=74, wide=1.35)
BARTENDER = dict(skin=hx("d7a786"), bald=True, hair=hx("3a2a20"), mustache=True, coat=hx("453131"), coat_len=0,
                 shirt=hx("ebe6d8"), tie=hx("2a1818"), apron=hx("e7e0d0"), pants=hx("2b2424"), shoes=hx("141414"))


DANIEL = dict(skin=hx("e0b090"), hair=hx("5a4636"), coat=hx("476d5c"), coat_len=0, shirt=hx("d1cab9"),
              pants=hx("4d6288"), shoes=hx("ddd7ca"), buttons=None)


def sheet(frames, cols, fw, fh, rows):
    out = Image.new("RGBA", (cols * fw, rows * fh))
    for r, row in enumerate(frames):
        for c, im in enumerate(row):
            out.paste(im, (c * fw, r * fh))
    return out


def player_sheet(spec, name):
    """Walkable character: side (idle, 6 walk, talk), front (idle, 4 walk, talk), back (idle, 4 walk)."""
    two_pi = 2 * math.pi
    side = [frame(spec, "side")] + [frame(spec, "side", two_pi * i / 6, True) for i in range(6)] + \
           [frame(spec, "side", talk=True)]
    front = [frame(spec, "front")] + [frame(spec, "front", two_pi * i / 4 + 0.8, True) for i in range(4)] + \
            [frame(spec, "front", talk=True)]
    back = [frame(spec, "back")] + [frame(spec, "back", two_pi * i / 4 + 0.8, True) for i in range(4)]
    save(sheet([side, front, back], 8, 40, 80, 3), "sprites", f"{name}.png")


def build():
    player_sheet(MICAH, "micah")
    player_sheet(DANIEL, "daniel")
    for name, spec, view in (("teddy", TEDDY, "front"), ("concierge", CONCIERGE, "front"),
                             ("bellboy", BELLBOY, "front"), ("sal", SAL, "front"),
                             ("bartender", BARTENDER, "front")):
        fw, fh = spec.get("frame", (40, 80))
        save(sheet([[frame(spec, view), frame(spec, view, talk=True)]], 2, fw, fh, 1), "sprites", f"{name}.png")
