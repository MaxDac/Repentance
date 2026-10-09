"""Procedural character sprites: parts drawn on layers, auto-shaded, then outlined."""
import math
from PIL import Image, ImageDraw
from .common import hx, mul, save

LIGHT, DARK, BOTTOM = 1.22, 0.68, 0.86


def _shade(layer):
    """Lights the left edge and darkens right/bottom edges of a part (key light from upper left)."""
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
            if x == 0 or px[x - 1, y][3] == 0:
                f *= LIGHT
            if x == w - 1 or px[x + 1, y][3] == 0:
                f *= DARK
            elif x < w - 2 and px[x + 2, y][3] == 0:
                f *= 0.86
            if y == h - 1 or px[x, y + 1][3] == 0:
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
            best = None
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and px[nx, ny][3]:
                    c = px[nx, ny]
                    if best is None or sum(c[:3]) < sum(best[:3]):
                        best = c
            if best:
                op[x, y] = mul(best[:3], 0.32) + (255,)
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
    r = w / 2 - 0.5
    for p in (a, b):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)


def _side(f, phase, walking, talk):
    s = f.s
    a = math.sin(phase) * 0.42 if walking else 0.0
    if walking:
        f.bob = -1 if abs(math.sin(phase)) < 0.5 else 0
    lw = max(3, round(4.5 * f.k))
    hip = f.P(0, 46)
    leg_len = (66 - 46) * f.k

    def leg(ang, col, lift):
        d = f.layer()
        foot = (hip[0] + leg_len * math.sin(ang), min(f.Y(66) - lift, hip[1] + leg_len * math.cos(ang) - lift))
        knee = ((hip[0] + foot[0]) / 2 + 1, (hip[1] + foot[1]) / 2)
        _limb(d, hip, knee, lw, col)
        _limb(d, knee, foot, lw, col)
        d.polygon([(foot[0] - 2, foot[1] - 1), (foot[0] + 4, foot[1] - 1), (foot[0] + 5, foot[1] + 2),
                   (foot[0] - 2, foot[1] + 2)], fill=s["shoes"])

    back_lift = 2 if walking and math.cos(phase) < -0.3 else 0
    front_lift = 2 if walking and math.cos(phase) > 0.3 else 0
    # back arm
    d = f.layer()
    sh = f.P(0, 23)
    hand = (sh[0] + 17 * f.k * math.sin(a * 0.9), sh[1] + 17 * f.k * math.cos(a * 0.9))
    _limb(d, sh, hand, lw, mul(s["coat"], 0.8))
    d.ellipse([hand[0] - 1.5, hand[1] - 1, hand[0] + 1.5, hand[1] + 2], fill=mul(s["skin"], 0.85))
    leg(-a, mul(s["pants"], 0.8), back_lift)
    leg(a, s["pants"], front_lift)
    # torso / coat
    d = f.layer()
    hem = 46 + s.get("coat_len", 8)
    d.polygon([f.P(-5, 21), f.P(5, 21), f.P(6, hem), f.P(-6, hem)], fill=s["coat"])
    if s.get("belt"):
        d.line([f.P(-5, 37), f.P(5, 37)], fill=mul(s["coat"], 0.7), width=2)
    if s.get("apron"):
        d.polygon([f.P(1, 36), f.P(6, 36), f.P(7, hem + 6), f.P(2, hem + 6)], fill=s["apron"])
    d.line([f.P(4, 21), f.P(2, 31)], fill=mul(s["coat"], 0.75))
    d.polygon([f.P(3, 21), f.P(5, 21), f.P(5, 27)], fill=s.get("shirt", hx("d8d0c0")))
    # front arm
    d = f.layer()
    hand = (sh[0] + 17 * f.k * math.sin(-a * 0.9), sh[1] + 17 * f.k * math.cos(-a * 0.9))
    _limb(d, sh, hand, lw, s["coat"])
    d.ellipse([hand[0] - 1.5, hand[1] - 1, hand[0] + 1.5, hand[1] + 2], fill=s["skin"])
    # head
    d = f.layer()
    d.rectangle([f.X(-1), f.Y(17), f.X(2), f.Y(22)], fill=mul(s["skin"], 0.85))
    d.ellipse([f.X(-4), f.Y(7), f.X(4), f.Y(19)], fill=s["skin"])
    d.polygon([f.P(3, 12), f.P(6, 15), f.P(3, 16)], fill=s["skin"])
    hair = s.get("hair")
    if hair and not s.get("bald"):
        d.chord([f.X(-5), f.Y(6), f.X(4), f.Y(16)], 180, 360, fill=hair)
        d.rectangle([f.X(-5), f.Y(10), f.X(-2), f.Y(16)], fill=hair)
    d.point(f.P(2, 12), fill=hx("201818"))
    d.point(f.P(-1, 13), fill=mul(s["skin"], 0.75))
    if s.get("mustache"):
        d.line([f.P(3, 16), f.P(5, 16)], fill=s.get("hair", hx("302018")))
    d.line([f.P(2, 17), f.P(4, 17)], fill=hx("6a2a2a") if talk else mul(s["skin"], 0.7), width=2 if talk else 1)
    _hat(f, "side")


def _front(f, phase, walking, talk, back=False):
    s = f.s
    lw = max(3, round(4.5 * f.k))
    lift_l = 3 if walking and math.sin(phase) > 0.3 else 0
    lift_r = 3 if walking and math.sin(phase) < -0.3 else 0
    if walking and (lift_l or lift_r):
        f.bob = -1
    for side, lift in ((-1, lift_l), (1, lift_r)):
        d = f.layer()
        hip = f.P(3 * side, 46)
        foot = (f.X(3.5 * side), f.Y(66) - lift)
        _limb(d, hip, foot, lw, s["pants"])
        d.rectangle([foot[0] - 2, foot[1] - 1, foot[0] + 2, foot[1] + 2], fill=s["shoes"])
    d = f.layer()
    hem = 46 + s.get("coat_len", 8)
    d.polygon([f.P(-7, 21), f.P(7, 21), f.P(8.5, hem), f.P(-8.5, hem)], fill=s["coat"])
    if not back:
        d.polygon([f.P(-3, 21), f.P(3, 21), f.P(0, 33)], fill=s.get("shirt", hx("d8d0c0")))
        if s.get("tie"):
            d.polygon([f.P(-0.6, 22), f.P(0.6, 22), f.P(1, 31), f.P(0, 33), f.P(-1, 31)], fill=s["tie"])
        d.line([f.P(-3, 21), f.P(0, 34)], fill=mul(s["coat"], 0.7))
        d.line([f.P(3, 21), f.P(0, 34)], fill=mul(s["coat"], 1.15))
        if s.get("buttons"):
            for v in (36, 40, 44):
                d.point(f.P(-2, v), fill=s["buttons"])
                d.point(f.P(2, v), fill=s["buttons"])
        if s.get("apron"):
            d.rectangle([f.X(-6), f.Y(37), f.X(6), f.Y(hem + 6)], fill=s["apron"])
    if s.get("belt"):
        d.line([f.P(-7, 37), f.P(7, 37)], fill=mul(s["coat"], 0.7), width=2)
        if not back:
            d.rectangle([f.X(-1), f.Y(36), f.X(1), f.Y(38)], fill=hx("b89a50"))
    sw = math.sin(phase) * 2 if walking else 0
    for side in (-1, 1):
        d = f.layer()
        sh = f.P(8 * side, 22)
        hand = (f.X(9.5 * side), f.Y(41) + round(sw * side))
        _limb(d, sh, hand, lw, s["coat"])
        d.ellipse([hand[0] - 1.5, hand[1], hand[0] + 1.5, hand[1] + 3], fill=s["skin"])
    d = f.layer()
    d.rectangle([f.X(-2), f.Y(17), f.X(2), f.Y(22)], fill=mul(s["skin"], 0.85))
    d.ellipse([f.X(-5), f.Y(7), f.X(5), f.Y(19)], fill=s["skin"])
    hair = s.get("hair")
    if back:
        if hair and not s.get("bald"):
            d.ellipse([f.X(-5), f.Y(6), f.X(5), f.Y(17)], fill=hair)
    else:
        if hair and not s.get("bald"):
            d.chord([f.X(-5), f.Y(6), f.X(5), f.Y(14)], 180, 360, fill=hair)
            d.rectangle([f.X(-5), f.Y(10), f.X(-4), f.Y(14)], fill=hair)
            d.rectangle([f.X(4), f.Y(10), f.X(5), f.Y(14)], fill=hair)
        for side in (-1, 1):
            d.point(f.P(2 * side, 12), fill=hx("201818"))
            d.point(f.P(2 * side, 11), fill=mul(hair or s["skin"], 0.8))
        d.point(f.P(0, 14), fill=mul(s["skin"], 0.75))
        if s.get("mustache"):
            d.line([f.P(-2, 15), f.P(2, 15)], fill=hair or hx("302018"))
        if talk:
            d.rectangle([f.X(-1), f.Y(16), f.X(1), f.Y(17)], fill=hx("5a2020"))
        else:
            d.line([f.P(-1, 16.5), f.P(1, 16.5)], fill=mul(s["skin"], 0.65))
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
            d.polygon([f.P(-4, 2), f.P(3, 1.5), f.P(4.5, 8), f.P(-4.5, 8)], fill=c)
            d.line([f.P(-4.5, 7), f.P(4.5, 7)], fill=s.get("band", hx("1a1010")), width=2)
            d.line([f.P(-8, 9), f.P(8, 8)], fill=c, width=2)
        else:
            d.polygon([f.P(-5, 1.5), f.P(5, 1.5), f.P(5.5, 8), f.P(-5.5, 8)], fill=c)
            d.line([f.P(-1, 1.5), f.P(0, 3)], fill=mul(c, 0.6))
            d.line([f.P(-5.5, 7), f.P(5.5, 7)], fill=s.get("band", hx("1a1010")), width=2)
            d.ellipse([f.X(-9), f.Y(7.5), f.X(9), f.Y(10)], fill=c)
    elif hat == "cap":
        d.chord([f.X(-6), f.Y(4), f.X(6), f.Y(13)], 180, 360, fill=c)
        if view == "side":
            d.line([f.P(2, 8.5), f.P(8, 9)], fill=mul(c, 0.8), width=2)
        else:
            d.ellipse([f.X(-6), f.Y(7.5), f.X(6), f.Y(10)], fill=mul(c, 0.85))
    elif hat == "pillbox":
        d.rectangle([f.X(-4), f.Y(3), f.X(4), f.Y(8)], fill=c)
        d.line([f.P(-4, 7), f.P(4, 7)], fill=hx("d8b040"))


def frame(spec, view, phase=0.0, walking=False, talk=False):
    f = Fig(spec)
    if view == "side":
        _side(f, phase, walking, talk)
    else:
        _front(f, phase, walking, talk, back=(view == "back"))
    return f.render()


MICAH = dict(skin=hx("d8a480"), hair=hx("2a1e18"), hat="fedora", hat_col=hx("4a3a30"), band=hx("1a1010"),
             coat=hx("9a8058"), coat_len=10, belt=True, shirt=hx("d8d4c4"), tie=hx("6a1a22"),
             pants=hx("3a3430"), shoes=hx("2a1a14"))
TEDDY = dict(skin=hx("e8c0a0"), hair=hx("a07838"), mustache=True, coat=hx("d8d0b8"), coat_len=4,
             shirt=hx("f0ece0"), tie=hx("3a6a9a"), pants=hx("c8c0a8"), shoes=hx("eae6dc"))
CONCIERGE = dict(skin=hx("e0b090"), hair=hx("8a8a8a"), mustache=True, coat=hx("5a1a2a"), coat_len=4,
                 shirt=hx("f0ece0"), tie=hx("1a1a1a"), pants=hx("2a1a20"), shoes=hx("1a1414"),
                 buttons=hx("d8b040"))
BELLBOY = dict(skin=hx("c89070"), hair=hx("3a2418"), hat="pillbox", hat_col=hx("a82020"), coat=hx("b02424"),
               coat_len=0, shirt=hx("f0ece0"), pants=hx("2a1a20"), shoes=hx("1a1414"), buttons=hx("e8c040"),
               height=58)
SAL = dict(skin=hx("c89878"), hair=hx("1a1414"), hat="cap", hat_col=hx("3a3a40"), coat=hx("2e2e36"), coat_len=4,
           shirt=hx("a8a090"), pants=hx("26262c"), shoes=hx("141414"), frame=(48, 84), height=74, wide=1.35)
BARTENDER = dict(skin=hx("d8a888"), bald=True, hair=hx("3a2a20"), mustache=True, coat=hx("3a2a2a"), coat_len=0,
                 shirt=hx("e8e4d8"), tie=hx("2a1a1a"), apron=hx("e0dcd0"), pants=hx("2a2424"), shoes=hx("141414"))


DANIEL = dict(skin=hx("e0b090"), hair=hx("5a4636"), coat=hx("3e5a4e"), coat_len=0, shirt=hx("c8c4b8"),
              pants=hx("3a4a6a"), shoes=hx("d8d4cc"), buttons=None)


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
