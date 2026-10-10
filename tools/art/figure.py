"""Volumetric pixel-figure painter in the style of early-90s LucasArts VGA sprites.

Figures are posed as a 3D skeleton (body frame: x = the character's own right, y = down, z = forward, all in
fractions of the figure height), turned by a yaw angle and projected orthographically with a slight camera pitch.
Every body part is a shaded volume (tapered capsules, ellipsoids, row-cylinder polygons) carrying a surface normal.
Shading quantises the normals against an upper-left key light onto a 5-tone hue-shifted ramp per material, parts
cast a one-pixel shadow onto what lies behind them, and the silhouette is "sel-out" (darkest tone of the material on
the shadow side, one tone darker on the lit side) instead of a black outline.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from .common import hx, BAYER

LIGHT = np.array([-0.5, -0.65, 0.58])
LIGHT /= np.linalg.norm(LIGHT)
BULK = 1.16  # FOTA figures are solid and broad-shouldered, not wiry
HEAD = 1.17  # ...with large heads that read at a distance
PITCH = 0.2  # how much nearer points drop on screen (camera looks slightly down at the floor)
COOL = np.array(hx("241c3c"), float)
WARM = np.array(hx("fff2cc"), float)
FACT = (0.40, 0.60, 0.80, 1.0, 1.17)
COOLT = (0.40, 0.24, 0.09, 0.0, 0.0)
WARMT = (0.0, 0.0, 0.0, 0.0, 0.16)
BAY = (np.array(BAYER, float) + 0.5) / 16.0


def ramp(base):
    b = np.array(hx(base), float)
    tones = []
    for f, c, w in zip(FACT, COOLT, WARMT):
        v = b * f
        v = v * (1 - c) + COOL * c
        v = v * (1 - w) + WARM * w
        tones.append(np.clip(v, 0, 255))
    return np.array(tones).astype(np.uint8)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.mat = np.full((h, w), -1, int)
        self.n = np.zeros((h, w, 3))
        self.part = np.full((h, w), -1, int)
        self.bias = np.zeros((h, w), int)
        yy, xx = np.mgrid[0:h, 0:w]
        self.X, self.Y = xx + 0.5, yy + 0.5
        self.ramps, self.dith, self.mats, self.parts = [], [], {}, {}
        self.ink = []
        self.shadow = np.zeros((h, w), bool)
        self.blend_parts, self.blend_zone = (), np.zeros((h, w), bool)
        self.blend_w = np.zeros((h, w))  # 1 = shade as one mass with the back, fading to 0 towards the armpit

    def _blend_ids(self):
        return [self.parts[n] for n in self.blend_parts if n in self.parts]

    def m(self, col, dither=True):
        key = (col, dither)
        if key not in self.mats:
            self.mats[key] = len(self.ramps)
            self.ramps.append(ramp(col))
            self.dith.append(dither)
        return self.mats[key]

    def pid(self, part):
        return self.parts.setdefault(part, len(self.parts))

    def put(self, shape, col, part, dither=True, cast=True, clip=None):
        mask, nx, ny, nz = shape
        if clip is not None:
            mask = mask & clip
        if not mask.any():
            return mask
        p = self.pid(part)
        if cast:
            sh = np.zeros_like(mask)
            sh[1:, 1:] = mask[:-1, :-1]
            sh &= ~mask & (self.mat >= 0) & (self.part != p)
            if part in self.blend_parts:
                sh &= ~(self.blend_zone & np.isin(self.part, self._blend_ids()))
            self.bias[sh] -= 1
        self.mat[mask] = self.m(col, dither)
        n = np.stack([nx, ny, nz], -1)
        n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        self.n[mask] = n[mask]
        self.part[mask] = p
        self.bias[mask] = 0
        return mask

    def parts_mask(self, *names):
        ids = [self.parts[n] for n in names if n in self.parts]
        return np.isin(self.part, ids)

    def recolor(self, mask, col, dither=True, bias=0):
        mask = mask & (self.mat >= 0)
        self.mat[mask] = self.m(col, dither)
        self.bias[mask] += bias

    def dot(self, x, y, col):
        self.ink.append((int(math.floor(x)), int(math.floor(y)), col))

    # --- shapes -------------------------------------------------------------------------------------------------
    def capsule(self, a, b, ra, rb):
        ax, ay = a[0], a[1]
        dx, dy = b[0] - ax, b[1] - ay
        l2 = max(dx * dx + dy * dy, 1e-6)
        t = np.clip(((self.X - ax) * dx + (self.Y - ay) * dy) / l2, 0, 1)
        ex, ey = self.X - (ax + t * dx), self.Y - (ay + t * dy)
        r = ra + (rb - ra) * t
        d = np.sqrt(ex * ex + ey * ey)
        q = np.clip(d / np.maximum(r, 0.3), 0, 1)
        dd = np.maximum(d, 1e-6)
        return d <= r + 0.2, ex / dd * q, ey / dd * q, np.sqrt(1 - q * q) + 0.05

    def ellipse(self, c, rx, ry, ang=0.0):
        ca, sa = math.cos(ang), math.sin(ang)
        dx, dy = self.X - c[0], self.Y - c[1]
        u = (dx * ca + dy * sa) / np.maximum(rx, 0.4)
        v = (-dx * sa + dy * ca) / max(ry, 0.4)
        q = u * u + v * v
        mask = q <= 1.0 + 0.25 / max(min(np.min(rx), ry), 0.5)
        qn = np.clip(q, 0, 1)
        return mask, u * ca - v * sa, u * sa + v * ca, np.sqrt(1 - qn) + 0.05

    def poly(self, pts, curve=0.85):
        im = Image.new("L", (self.w, self.h), 0)
        ImageDraw.Draw(im).polygon([(float(x), float(y)) for x, y in pts], fill=255)
        mask = np.array(im) > 0
        nx = np.zeros((self.h, self.w))
        for y in np.nonzero(mask.any(1))[0]:
            xs = np.nonzero(mask[y])[0]
            mid, half = (xs[0] + xs[-1] + 1) / 2.0, max((xs[-1] - xs[0] + 1) / 2.0, 0.5)
            nx[y] = np.clip((self.X[y] - mid) / half, -1, 1) * curve
        ny = np.full_like(nx, -0.12)
        return mask, nx, ny, np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1)) + 0.05

    # --- output -------------------------------------------------------------------------------------------------
    def render(self, shadow_box=None, light=None):
        filled = self.mat >= 0
        # shoulders and back read as one mass: blend arm/torso normals into a shared cross-section near the top
        u = np.isin(self.part, self._blend_ids()) & self.blend_zone
        for y in np.nonzero(u.any(1))[0]:
            xs = np.nonzero(u[y])[0]
            mid, half = (xs[0] + xs[-1] + 1) / 2.0, max((xs[-1] - xs[0] + 1) / 2.0, 0.5)
            nx = np.clip((self.X[y, xs] - mid) / half, -1, 1) * 0.85
            cs = np.stack([nx, np.full_like(nx, -0.12), np.sqrt(np.clip(1 - nx * nx - 0.0144, 0, 1)) + 0.05], -1)
            wt = self.blend_w[y, xs][:, None]
            n = wt * cs + (1 - wt) * self.n[y, xs]
            self.n[y, xs] = n / np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-6)
        s = np.einsum("hwc,c->hw", self.n, LIGHT if light is None else light)
        v = 0.42 + 0.58 * s
        bay = np.tile(BAY, (self.h // 4 + 1, self.w // 4 + 1))[: self.h, : self.w]
        dith = np.array(self.dith + [False])[self.mat]
        thr = np.where(dith, 0.5 + (bay - 0.5) * 0.04, 0.5)
        tone = np.floor(v * 4 + thr).astype(int) + np.maximum(self.bias, -2)
        pad = np.pad(filled, 1)
        inner = pad[:-2, 1:-1] & pad[2:, 1:-1] & pad[1:-1, :-2] & pad[1:-1, 2:]
        edge = filled & ~inner
        tone = np.where(edge, np.where(s < 0.22, 0, np.minimum(tone - 1, 2)), tone)  # crisp outline even on lit edges
        # a part lying behind another part gets a darker seam where they meet
        pp = np.pad(self.part, 1, constant_values=-1)
        behind = np.zeros_like(filled)
        bl = np.isin(self.part, self._blend_ids()) & self.blend_zone
        bp = np.pad(bl, 1)
        for nb, nbl in ((pp[:-2, 1:-1], bp[:-2, 1:-1]), (pp[2:, 1:-1], bp[2:, 1:-1]),
                        (pp[1:-1, :-2], bp[1:-1, :-2]), (pp[1:-1, 2:], bp[1:-1, 2:])):
            behind |= (nb > self.part) & ~(bl & nbl)
        tone = np.where(filled & ~edge & behind, tone - 1, tone)
        tone = np.clip(tone, 0, 4)
        out = np.zeros((self.h, self.w, 4), np.uint8)
        if shadow_box is not None:
            m, _, _, _ = self.ellipse(*shadow_box)
            out[m & ~filled] = (12, 8, 16, 90)
        ramps = np.array(self.ramps) if self.ramps else np.zeros((1, 5, 3), np.uint8)
        ys, xs = np.nonzero(filled)
        out[ys, xs, :3] = ramps[self.mat[ys, xs], tone[ys, xs]]
        out[ys, xs, 3] = 255
        for x, y, col in self.ink:
            if 0 <= x < self.w and 0 <= y < self.h and (out[y, x, 3] == 255 or len(col) == 7):
                out[y, x, :3] = hx(col.lstrip("+"))
                out[y, x, 3] = 255
        return Image.fromarray(out, "RGBA")


# =====================================================================================================================
# Poses
# =====================================================================================================================
# Side walk, near (right) leg: thigh swing forward (deg), knee flex (deg), foot pitch (deg, toe up > 0).
# The far leg runs the same table four frames later; arms counter-swing.
WALK8 = [(27, 4, 14), (17, 14, 0), (3, 6, 0), (-12, 3, 0), (-25, 8, -16), (-17, 36, -38), (5, 55, -18), (21, 28, 6)]


def _walk_leg(phase, amp=1.0):
    """Interpolates WALK8 at a fractional frame position (0..8)."""
    i = int(math.floor(phase)) % 8
    t = phase - math.floor(phase)
    a, b = WALK8[i], WALK8[(i + 1) % 8]
    return tuple((a[k] + (b[k] - a[k]) * t) * amp for k in range(3))


def pose(phi, **kw):
    p = dict(phi=phi, legs={1: (3, 2, 0), -1: (-3, 6, -6)}, arms={1: ("swing", 4, 6, 10), -1: ("swing", -2, 6, 12)},
             lean=0.0, shift=0.0, spread=0.012, mouth=0, nod=0.0, tilt=0.0)
    p.update(kw)
    return p


def walk_pose(phi, phase, amp=1.0, arm_amp=0.75):
    legs = {1: _walk_leg(phase, amp), -1: _walk_leg(phase + 4, amp)}
    arms = {s: ("swing", -legs[s][0] * arm_amp, 5, 12 + max(0.0, -legs[s][0] * arm_amp) * 0.9) for s in (1, -1)}
    return pose(phi, legs=legs, arms=arms, lean=3.0 * amp, spread=0.004)


# =====================================================================================================================
# Figure assembly
# =====================================================================================================================
def _rot_x(v, ang):
    """Rotates (y, z) of v about the x axis; positive angle lifts +z upwards (towards -y)."""
    c, s = math.cos(ang), math.sin(ang)
    return np.array([v[0], v[1] * c - v[2] * s, v[1] * s + v[2] * c])


def figure(spec, ps, fw=56, fh=80):
    H = spec["h"]
    c = Canvas(fw, fh)
    phi = math.radians(ps["phi"])
    cp, sp = math.cos(phi), math.sin(phi)
    cx, base = fw / 2.0 + spec.get("dx", 0), fh - 3.0
    sw, hw = spec.get("sw", 0.135) * 0.8, spec.get("hw", 0.052)  # FOTA shoulders are narrow and sloping
    lean = math.radians(ps["lean"])
    shift = ps["shift"]

    # ---- skeleton (body frame) ----
    legs = {}
    for s in (1, -1):
        a, k, pitch = (math.radians(x) for x in ps["legs"][s])
        hip = np.array([s * hw + shift, 0.5, 0.0])
        knee = hip + 0.235 * np.array([s * ps["spread"], math.cos(a), math.sin(a)])
        ank = knee + 0.215 * np.array([s * ps["spread"], math.cos(a - k), math.sin(a - k)])
        heel = ank + _rot_x(np.array([0, 0.026, -0.022]), pitch)
        toe = ank + _rot_x(np.array([0, 0.03, spec.get("foot", 0.072)]), pitch)
        legs[s] = [hip, knee, ank, heel, toe]
    sole = max(max(l[3][1], l[4][1]) for l in legs.values()) + 0.018
    dy = 1.0 - sole

    def body(p):
        p = np.array(p, float)
        if p[1] < 0.5:
            p[2] += (0.5 - p[1]) * math.tan(lean)
        p[1] += dy
        return p

    c.blend_parts = ("torso", "arm1", "arm-1")
    y_full, y_end = base + (0.29 + dy - 1.0) * H, base + (0.37 + dy - 1.0) * H  # cap .. armpit
    c.blend_zone = c.Y < y_end
    c.blend_w = np.clip((y_end - c.Y) / (y_end - y_full), 0, 1)

    def P(p):
        bx, by, bz = p
        X = -bx * cp + bz * sp
        D = bx * sp + bz * cp
        return (cx + X * H, base + (by - 1.0) * H + D * H * PITCH, D)

    for s in legs:
        legs[s] = [l + np.array([0, dy, 0]) for l in legs[s]]

    def ell3(center, ax, ay, az):
        x, y, _ = P(center)
        return (x, y), H * math.sqrt((ax * cp) ** 2 + (az * sp) ** 2), H * ay

    prims = []  # (key, fn)

    def add(key, fn):
        prims.append((key, fn))

    col = spec
    skin = col["skin"]
    pants = col.get("pants")
    boots = col.get("boots")
    shoes = col["shoes"]
    leg_r = spec.get("leg_r", 1.0)

    # ---- legs ----
    for s in (1, -1):
        hip, knee, ank, heel, toe = legs[s]
        Dk = P(knee)[2]

        def leg(s=s, hip=hip, knee=knee, ank=ank, heel=heel, toe=toe):
            part = f"leg{s}"
            thigh = pants or col.get("stockings", skin)
            shin = boots or col.get("stockings") or pants or skin
            c.put(c.capsule(P(hip), P(knee), H * 0.05 * leg_r * BULK, H * 0.037 * leg_r * BULK), thigh, part)
            c.put(c.capsule(P(knee), P(ank), H * 0.037 * leg_r * BULK, H * 0.029 * leg_r * BULK), shin, part)
            if pants and not boots:  # trouser cuff falls over the shoe
                c.put(c.capsule(P(ank - np.array([0, 0.02, 0])), P(ank + np.array([0, 0.012, 0])),
                                H * 0.03 * leg_r * BULK, H * 0.031 * leg_r * BULK), pants, part)
            c.put(c.capsule(P(heel), P(toe), H * 0.024, H * 0.02), shoes, f"shoe{s}", dither=False)
        add(1.0 + Dk, leg)

    # ---- torso ----
    torso = col["torso"]
    pelvis_col = col.get("pelvis", pants or torso)
    waist = spec.get("waist", 0.085)
    hipw = spec.get("hipw", 0.098)

    def trunk():
        hem_top = spec.get("top_hem", 0.45)
        levels = [(0.19, 0.04, 0.034), (0.212, sw * 0.62, 0.05), (0.232, sw * 0.86, 0.058), (0.25, sw * 1.0, 0.064), (0.31, sw * 0.95, 0.07),
                  (0.40, waist, 0.058), (0.47, hipw, 0.064), (0.53, hipw * 0.86, 0.056)]
        left, right = [], []
        for y, ax, az in levels:
            cxy = P(body([shift * min(1.0, max(0.0, (y - 0.3) / 0.2)), y, 0.004]))
            k = 1.0 if y < 0.3 else BULK
            w = H * math.sqrt((ax * k * cp) ** 2 + (az * 1.25 * sp) ** 2)
            tilt = 0.5 * math.copysign(1.0, cp) * ax * k * sp * H * PITCH  # far shoulder sits higher, as the arms do
            left.append((cxy[0] - w, cxy[1] + tilt))
            right.append((cxy[0] + w, cxy[1] - tilt))
        shape = list(c.poly(left + right[::-1], curve=0.9))
        for s in (1, -1):  # rounded shoulder caps centred on the arm joints, so the shoulder flows into the sleeve
            cx_, cy_, cd_ = P(body([s * (sw + 0.004), 0.268, 0.0]))
            cap = c.ellipse((cx_, cy_ - 0.5 * cd_ * H * PITCH), H * 0.035 * BULK, H * 0.032 * BULK)
            new = cap[0] & ~shape[0]
            blend = cap[0] & shape[0]
            for i in (1, 2, 3):
                shape[i] = np.where(new, cap[i], np.where(blend, (shape[i] + cap[i]) / 2, shape[i]))
            shape[0] = shape[0] | cap[0]
        c.put(tuple(shape), torso, "torso")
        if col.get("abdomen"):
            c.recolor(c.parts_mask("torso") & (c.Y >= P(body([0, spec.get("abdomen_top", 0.37), 0]))[1]),
                      col["abdomen"])
        c.recolor(c.parts_mask("torso") & (c.Y >= P(body([0, hem_top, 0]))[1]), pelvis_col)
        coat = col.get("coat")
        if coat:
            _skirt(c, coat, body, P, legs, H, waist, hipw, cp, sp)
    add(2.0, trunk)

    # ---- arms ----
    arm_pts = {}
    for s in (1, -1):
        kind, f, o, e = ps["arms"][s]
        sh = body([s * (sw + 0.008), 0.284, 0.0])  # below the cap top: the torso's shoulder cap forms the contour
        if kind == "hip":
            el = body([s * (sw + 0.07), 0.345, -0.035])
            wr = body([s * (hipw - 0.005), 0.455, 0.0])
            hand = body([s * (hipw - 0.02), 0.475, 0.01])
        elif kind == "pocket":
            el = body([s * (sw + 0.012), 0.385, -0.015])
            wr = body([s * (hipw + 0.004), 0.51, 0.02])
            hand = None
        elif kind == "fold":  # hands clasped in front (priest, concierge)
            el = body([s * (sw + 0.005), 0.39, 0.012])
            wr = body([s * 0.022, 0.45, 0.075])
            hand = body([s * 0.004, 0.462, 0.085])
        else:
            fr, orr, er = (math.radians(x) for x in (f, o, e))
            d1 = np.array([s * math.sin(orr), math.cos(orr) * math.cos(fr), math.cos(orr) * math.sin(fr)])
            el = sh + 0.142 * d1
            d2 = np.array([s * math.sin(orr) * 0.3, math.cos(fr + er), math.sin(fr + er)])
            d2 /= np.linalg.norm(d2)
            wr = el + 0.145 * d2
            hand = wr + 0.045 * d2
        arm_pts[s] = (sh, el, wr, hand)
        Ds = P(sh)[2]

        def arm(s=s, sh=sh, el=el, wr=wr, hand=hand):
            sleeve = col.get("sleeves", torso)
            fore = col.get("forearm", sleeve)
            part = f"arm{s}"
            c.put(c.capsule(P(sh), P(el), H * 0.034 * BULK, H * 0.031 * BULK), sleeve, part)
            c.put(c.capsule(P(el), P(wr), H * 0.031 * BULK, H * 0.027 * BULK), fore, part)
            if col.get("cuff") and fore != skin:
                c.put(c.capsule(P(wr), P(wr), H * 0.026, H * 0.026), col["cuff"], part)
            if hand is not None:
                c.put(c.capsule(P(wr), P(hand), H * 0.027, H * 0.025), skin, f"hand{s}", dither=False)
        add(2.0 + Ds + 0.05 * abs(cp), arm)

    # ---- head ----
    nod = ps["nod"]
    facing = cp > -0.25

    neck_r = H * 0.029 * BULK

    def neck():
        _neck(c, col, P, body, H)
    add(1.95, neck)

    def collar():
        if not col.get("collar"):
            return
        nx0, ny0, _ = P(body([0, 0.2, 0.0]))
        band = c.parts_mask("torso") & (c.Y < ny0 + H * 0.02) & (np.abs(c.X - nx0) < neck_r * 1.55)
        c.recolor(band, col["collar"])
        c.bias[band & (c.Y < ny0 + H * 0.012)] += 1
    add(2.05, collar)

    def head():
        _head(c, col, P, body, H, cp, sp, nod)
    add(2.6, head)
    if col.get("hair_style") == "long":
        # The mane falls behind the neck and shoulders unless the figure is seen from the back.
        add(1.9 if facing else 2.7, lambda: _long_hair_back(c, col, P, body, H, cp, sp, nod))
    if col.get("hat") == "veil":
        add(1.9 if facing else 2.7, lambda: _veil_back(c, col, P, body, H, cp, sp, nod))

    for _, fn in sorted(prims, key=lambda kv: kv[0]):
        fn()

    _decals(c, col, P, body, H, cp, sp, legs, ps)
    if facing:
        _face(c, col, P, body, H, cp, sp, nod, ps["mouth"])
    shx = (P(legs[1][2])[0] + P(legs[-1][2])[0]) / 2
    return c.render(shadow_box=((shx, base + 0.6), H * 0.15, 1.7))


def _neck(c, col, P, body, H):
    neck_r = H * 0.029 * BULK
    c.put(c.capsule(P(body([0, 0.13, 0.0])), P(body([0, 0.228, -0.004])), neck_r, neck_r * 1.08),
          col.get("neck", col["skin"]), "neck")


def _head(c, col, P, body, H, cp, sp, nod):
    """Skull, jaw, profile features, ear, hair and hat (the painted face dots come later from _face)."""
    skin = col["skin"]
    hx_, hy_, _ = P(body([0.0, 0.074 + nod, 0.008]))
    hrx = H * HEAD * math.sqrt((0.048 * cp) ** 2 + (0.056 * sp) ** 2)
    hry = H * 0.077 * HEAD
    fs = math.copysign(1.0, sp) if abs(sp) > 1e-3 else 0.0
    facing = cp > -0.25

    def ell3(center, ax, ay, az):
        x, y, _ = P(center)
        return (x, y), H * math.sqrt((ax * cp) ** 2 + (az * sp) ** 2), H * ay

    if abs(sp) > 0.3:  # back of the skull: heads are deeper than they are wide
        oc, orx, ory = ell3(body([0, 0.068 + nod, -0.018 * HEAD]), 0.045 * HEAD, 0.064 * HEAD, 0.052 * HEAD)
        c.put(c.ellipse(oc, orx, ory), skin, "head", dither=False)
    c.put(c.ellipse((hx_, hy_), hrx, hry), skin, "head", dither=False)
    jc, jrx, jry = ell3(body([0, 0.118 + nod, 0.018]), 0.039 * HEAD, 0.047 * HEAD, 0.05 * HEAD)
    c.put(c.ellipse(jc, jrx, jry), skin, "head", dither=False)
    if abs(sp) > 0.3:
        ys = 0.074 + nod
        # brow ridge, nose and chin give the profile its shape
        c.put(c.capsule(P(body([0, ys - 0.012 * HEAD, 0.058 * HEAD])), P(body([0, ys - 0.004 * HEAD, 0.06 * HEAD])), 0.5, 0.5),
              skin, "head", dither=False)
        c.put(c.capsule(P(body([0, ys + 0.008 * HEAD, 0.058 * HEAD])), P(body([0, ys + 0.028 * HEAD, 0.066 * HEAD])), 0.55, 0.7),
              skin, "head", dither=False)
        c.put(c.capsule(P(body([0, ys + 0.066 * HEAD, 0.05 * HEAD])), P(body([0, ys + 0.078 * HEAD, 0.046 * HEAD])), 0.8, 0.8),
              skin, "head", dither=False)
    if abs(cp) > 0.1 and abs(sp) > 0.15 and facing:
        ex, ey, _ = P(body([-fs * 0.05 * 1, 0.088 + nod, -0.006]))
        ear_side = -1 if sp > 0 else 1
        ex, ey, ed = P(body([ear_side * 0.05, 0.088 + nod, -0.008]))
        if ed > -0.02 and col.get("hair_style") not in ("long", "bob"):
            c.put(c.ellipse((ex, ey), H * 0.011, H * 0.017), skin, "ear", dither=False)
    _hair(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod)
    # Faces are lit from the front: lift the jaw shadow so it does not read as stubble, and keep only a
    # one-tone shade on the far cheek.
    face = c.parts_mask("head") & (c.Y > hy_ - 1)
    c.bias[face] += 1
    if col.get("soft_face"):
        c.bias[c.parts_mask("neck") & (c.Y > hy_ - 1)] += 1
    _hat(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod)


def _leg_at(leg, y):
    """Point on a leg's thigh/shin chain at body height y (or None)."""
    pts = leg[:3]
    for a, b in zip(pts, pts[1:]):
        if (a[1] - y) * (b[1] - y) <= 0 and abs(b[1] - a[1]) > 1e-6:
            t = (y - a[1]) / (b[1] - a[1])
            return a + (b - a) * t
    return None


def _skirt(c, coat, body, P, legs, H, waist, hipw, cp, sp):
    """Coat tails / dress: a row-shaded polygon from the waist to the hem following both legs."""
    top, hem = body([0, coat.get("top", 0.42), 0])[1], body([0, coat["hem"], 0])[1]
    flare = coat.get("flare", 0.03)

    def width(ax, az):
        return H * math.sqrt((ax * cp) ** 2 + (az * sp) ** 2)

    tc = P(body([0, coat.get("top", 0.42), 0]))
    hc = P(body([0, 0.5, 0]))
    wt, wh = width(waist + 0.012, 0.064), width(hipw + 0.016, 0.07)
    xs = []
    for s, leg in legs.items():
        p = _leg_at(leg, hem)
        if p is None:
            p = leg[2]
        q = P(p)
        xs += [q[0] - H * (0.045 + flare), q[0] + H * (0.045 + flare)]
    hem_y = P(np.array([0, hem, 0]))[1]
    lo, hi = min(xs + [hc[0] - wh * 1.05]), max(xs + [hc[0] + wh * 1.05])
    pts = [(tc[0] - wt, tc[1]), (hc[0] - wh, hc[1]), (lo, hem_y), (hi, hem_y), (hc[0] + wh, hc[1]), (tc[0] + wt, tc[1])]
    c.put(c.poly(pts), coat["col"], "coat")


def _long_hair_back(c, col, P, body, H, cp, sp, nod):
    """Voluminous wavy mane falling to the shoulder blades (drawn behind the head)."""
    hc = P(body([0, 0.15 + nod, -0.03]))
    rx = H * math.sqrt((0.115 * cp) ** 2 + (0.09 * sp) ** 2)
    m, nx, ny, nz = c.ellipse((hc[0] - 0.045 * H * sp, hc[1]), rx, H * 0.14)
    wave = np.sin(c.Y / 1.7) * 0.9
    m2, _, _, _ = c.ellipse((hc[0] - 0.045 * H * sp, hc[1]), rx + wave, H * 0.14)
    top = P(body([0, 0.02 + nod, 0]))[1]
    keep = m2 & (c.Y > top)
    if abs(sp) > 0.15 and cp > -0.25:
        # In profile/3-4 the mane must stay behind the jaw, never under the chin.
        hx0, hy0 = P(body([0, 0.077 + nod, 0.0]))[:2]
        keep &= ~(((c.X - hx0) * math.copysign(1.0, sp) > -1.5) & (c.Y > hy0 + 1))
    c.put((keep, nx, ny, nz), col["hair"], "hairback", cast=False)


def _hair(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod):
    style = col.get("hair_style", "short")
    hair = col["hair"]
    fs = sp
    vol = {"short": 0.9, "bald": 0.2, "long": 3.0, "bob": 2.2, "slick": 0.5}[style]
    m, nx, ny, nz = c.ellipse((hx_ - (0.25 + 0.012 * H) * fs, hy_ - 0.6), hrx + vol + 0.008 * H * abs(fs), hry + vol * 0.8)
    u = np.clip((c.X - hx_) / max(hrx, 1), -1, 1)
    front = hy_ - hry * (0.5 if style in ("long", "bob") else 0.64) + (0.5 if style == "slick" else 0)
    nape = hy_ + hry * (0.55 if style != "bob" else 0.95)
    if style == "long":
        nape = hy_ + hry * 1.15
    # how much a column is "back of the head" vs face
    back = np.clip(-u * fs * 1.8 + 0.15, 0, 1)
    sides = np.clip((np.abs(u) - 0.72) * 4.0, 0, 1) * abs(cp)
    if style in ("long", "bob"):
        sides = np.clip((np.abs(u) - 0.55) * 3.0, 0, 1) * max(abs(cp), 0.3)
        sides *= np.where(u * fs > 0, np.clip(1 - abs(sp) * (5.0 if style == "long" else 2.4), 0, 1), 1.0)
        side_line = hy_ + hry * (0.95 if style == "long" else 0.75)
    else:
        side_line = hy_ + hry * 0.15
    line = front + (nape - front) * back
    line = np.maximum(line, front + (side_line - front) * sides)
    if cp < -0.25:  # seen from behind: all hair
        line = np.full_like(line, nape)
    mask = m & (c.Y < line)
    if style == "bald":
        mask &= (c.Y > hy_ - hry * 0.1) & (back > 0.3 if cp > -0.25 else True)
    c.put((mask, nx, ny, nz), hair, "hair", dither=False)
    if style != "bald":
        # FOTA hair has a lit crown and a darker underside rather than a flat helmet
        top = hy_ - hry - vol * 0.8
        hm = c.parts_mask("hair")
        c.bias[hm & (c.Y > top + 1.2) & (c.Y < top + 3.2) & ((c.X - hx_) * (1 if fs >= 0 else -1) < hrx * 0.4)] += 1
        c.bias[hm & (c.Y > hy_ + hry * 0.05)] -= 1
    if style in ("long", "bob"):
        stripe = (np.floor(c.X * 2 + np.round(2 * np.sin(c.Y / 2.1))) % 5 == 0)
        c.bias[c.parts_mask("hair", "hairback") & stripe] -= 1


def _hat(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod):
    hat = col.get("hat")
    if not hat:
        return
    hc = col["hat_col"]
    if hat == "fedora":
        by = hy_ - hry * 0.42
        brx = H * 0.092
        bry = 1.0 + H * 0.092 * PITCH * abs(cp) * 0.9
        snap = 0.12 * sp
        m = c.put(c.ellipse((hx_ + 0.6 * sp, by), brx, bry, snap), hc, "brim")
        crx = H * math.sqrt((0.054 * cp) ** 2 + (0.062 * sp) ** 2)
        ccy = by - H * 0.035
        crown = c.ellipse((hx_ - 0.4 * sp, ccy), crx, H * 0.045)
        c.put(crown, hc, "crown", clip=c.Y < by + 0.4)
        band = c.parts_mask("crown") & (c.Y >= by - 2.2) & (c.Y < by - 0.4)
        c.recolor(band, col.get("band", "1a120e"), dither=False)
        dent = c.parts_mask("crown") & (c.Y < ccy - H * 0.03) & (np.abs(c.X - (hx_ - 0.4 * sp)) < 1.0)
        c.bias[dent] -= 1
        c.bias[c.parts_mask("head", "ear", "hair") & (c.Y > by) & (c.Y < by + 2.6)] -= 1
        c.hat_line = by
    elif hat == "pillbox":
        cc = (hx_ + 0.5 * sp, hy_ - hry * 0.75)
        c.put(c.ellipse(cc, H * 0.045, H * 0.03, -0.25 * (1 if sp >= 0 else -1)), hc, "crown")
        c.recolor(c.parts_mask("crown") & (c.Y > cc[1] + 0.5), col.get("band", "e8c050"), dither=False)
    elif hat == "cap":
        c.put(c.ellipse((hx_ - 0.3 * sp, hy_ - hry * 0.5), hrx + 1.4, hry * 0.62), hc, "crown",
              clip=c.Y < hy_ - hry * 0.2)
        bill = P(body([0, 0.04 + nod, 0.07]))
        c.put(c.capsule((hx_ + 0.5 * sp, hy_ - hry * 0.3), (bill[0] + 0.5 * sp, bill[1]), 1.2, 1.0), hc, "bill")
        c.bias[c.parts_mask("head") & (c.Y > hy_ - hry * 0.3) & (c.Y < hy_ - hry * 0.3 + 2)] -= 1
    elif hat == "veil":
        # Religious habit: a white coif/wimple framing the face and wrapping the throat, under a black veil.
        coif = col.get("coif", "e8e4dc")
        fx, fy, _ = P(body([0, 0.086 + nod, 0.045]))
        frx, fry = max(hrx * (0.5 + 0.18 * abs(cp)), 2.2), hry * 0.74
        face = c.ellipse((fx, fy), frx, fry)[0]
        wrap = c.ellipse((hx_ + 0.3 * sp, hy_ + 0.6), hrx + 1.5, hry + 1.3)
        throat = c.capsule(P(body([0, 0.14 + nod, 0.004])), P(body([0, 0.222, -0.004])), H * 0.046, H * 0.056)
        c.put(throat, coif, "coif", clip=~face)
        c.put(wrap, coif, "coif", clip=~face)
        frame = c.ellipse((fx, fy + 0.6), frx + 1.6, fry + 1.4)[0] | ((c.Y > fy) & (np.abs(c.X - fx) < frx + 1.6))
        hood = c.ellipse((hx_ - 0.9 * sp, hy_ - 0.4), hrx + 2.4, hry + 2.0)
        c.put(hood, hc, "veil", clip=~frame & (c.Y < hy_ + hry * 0.55))
        c.bias[c.parts_mask("veil") & (c.Y < hy_ - hry * 0.6) & ((c.X - hx_) * (1 if sp >= 0 else -1) < 0)] += 1


def _veil_back(c, col, P, body, H, cp, sp, nod):
    """The black veil falling from the crown over the shoulders and down the back."""
    hx_, hy_, _ = P(body([0, 0.074 + nod, -0.02]))
    lo = P(body([0, 0.36, -0.05]))
    top_w = H * math.sqrt((0.062 * cp) ** 2 + (0.06 * sp) ** 2)
    bot_w = H * math.sqrt((0.12 * cp) ** 2 + (0.08 * sp) ** 2)
    back = -H * 0.02 * sp
    pts = [(hx_ - top_w + back * 0.5, hy_ - H * 0.04), (hx_ + top_w + back * 0.5, hy_ - H * 0.04),
           (lo[0] + bot_w + back, lo[1]), (lo[0] - bot_w + back, lo[1])]
    c.put(c.poly(pts), col["hat_col"], "veilback")


def _front_strip(c, P, body, H, y0, y1, w0, w1, parts, col, cp, sp, z=0.07, dither=True, bias=0, x0=0.0):
    """Recolours a vertical band down the front of the body (lapels, shirt, tie, apron, buttons)."""
    if cp < -0.2:
        return
    mask = c.parts_mask(*parts)
    out = np.zeros_like(mask)
    for yy in np.arange(y0, y1, 0.004):
        t = (yy - y0) / max(y1 - y0, 1e-6)
        w = w0 + (w1 - w0) * t
        a, b = P(body([x0 - w, yy, z])), P(body([x0 + w, yy, z]))
        row = int(math.floor(a[1]))
        if 0 <= row < c.h:
            lo, hi = sorted((a[0], b[0]))
            lo, hi = lo - 0.0, hi + (0.0 if hi - lo > 0.6 else 0.6)
            out[row] |= (c.X[row] >= lo) & (c.X[row] <= hi + 0.5)
    c.recolor(mask & out, col, dither=dither, bias=bias)


def _decals(c, col, P, body, H, cp, sp, legs, ps):
    body_parts = ("torso", "coat", "hips")
    for d in col.get("decals", []):
        kind = d[0]
        if kind == "strip":  # (strip, y0, y1, w0, w1, colour, parts?)
            _, y0, y1, w0, w1, colour = d[:6]
            parts = d[6] if len(d) > 6 else body_parts
            _front_strip(c, P, body, H, y0, y1, w0, w1, parts, colour, cp, sp)
        elif kind == "line":  # dark seam down the front
            _, y0, y1 = d[:3]
            seam = col["coat"]["col"] if col.get("coat") else col["torso"]
            _front_strip(c, P, body, H, y0, y1, 0, 0, body_parts, seam, cp, sp, bias=-1)
        elif kind == "belt":
            _, y, colour = d
            yb = P(body([0, y, 0]))[1]
            c.recolor(c.parts_mask(*body_parts) & (c.Y >= yb) & (c.Y < yb + max(1.0, H * 0.022)), colour, dither=False)
        elif kind == "bow" and cp > 0.05:  # bow tie at the throat: (bow, y, colour)
            _, y, colour = d
            bx, by_, _ = P(body([0, y, 0.05]))
            bx, by_ = math.floor(bx), math.floor(by_)
            for ddx, ddy in ((-2, -1), (-2, 0), (-2, 1), (-1, 0), (0, 0), (1, 0), (2, -1), (2, 0), (2, 1)):
                c.dot(bx + ddx, by_ + ddy, colour)
            c.dot(bx - 1, by_ - 1, colour)
            c.dot(bx + 1, by_ + 1, colour)
        elif kind == "pearls" and cp > 0.05:  # a single strand: (pearls, y, colour)
            _, y, colour = d
            for i, u in enumerate((-0.03, -0.015, 0.0, 0.015, 0.03)):
                px, py, _ = P(body([u, y + 0.012 * (1 - (u / 0.03) ** 2), 0.055]))
                if i % 2 == 0 or abs(cp) > 0.7:
                    c.dot(px, py, colour)
        elif kind == "patch" and cp > 0.05:  # small square on the chest (pocket square): (patch, x, y, colour)
            _, x, y, colour = d
            px, py, _ = P(body([x, y, 0.07]))
            for ddx, ddy in ((0, 0), (1, 0), (0, -1)):
                c.dot(px + ddx, py + ddy, colour)
        elif kind == "buttons":
            _, y0, y1, n, colour = d[:5]
            if cp > 0.05:
                for i in range(n):
                    yy = y0 + (y1 - y0) * i / max(n - 1, 1)
                    for s in ((-1, 1) if len(d) > 5 and d[5] else (0,)):
                        p = P(body([s * 0.025, yy, 0.072]))
                        c.dot(p[0], p[1], colour)
        elif kind == "ribbon":  # off-centre front band (an untied tie end): (ribbon, x, y0, y1, w, colour, parts?)
            _, x, y0, y1, w, colour = d[:6]
            parts = d[6] if len(d) > 6 else body_parts
            _front_strip(c, P, body, H, y0, y1, w, w, parts, colour, cp, sp, x0=x, dither=False)
        elif kind == "rosary" and cp > 0.05:  # beads hanging from the belt to a cross: (rosary, x, y0, y1, bead, cross)
            _, x, y0, y1, bead, cross = d
            last = None
            for i, yy in enumerate(np.arange(y0, y1, 0.008)):
                sway = 0.01 * math.sin((yy - y0) / max(y1 - y0, 1e-6) * math.pi)
                px, py, _ = P(body([x + sway, yy, 0.075]))
                pos = (math.floor(px), math.floor(py))
                if pos != last and i % 2 == 0:
                    c.dot(px, py, bead)
                last = pos
            px, py, _ = P(body([x, y1, 0.075]))
            px, py = math.floor(px), math.floor(py)
            for ddx, ddy in ((0, 0), (0, 1), (0, 2), (0, 3), (-1, 1), (1, 1)):
                c.dot(px + ddx, py + ddy, "+" + cross)
        elif kind == "hang":  # braces unclipped behind, looping down beside the hips: (hang, y_top, drop, colour)
            _, top, drop, colour = d
            for s in (1, -1):
                ok = c.parts_mask("torso", f"leg{s}")
                xo, xw = 0.05, col.get("hipw", 0.098) + 0.012
                for u in np.linspace(-1, 1, 90):
                    k = 1 - u * u
                    p = P(body([s * (xo + (xw - xo) * k), top + drop * k ** 0.7, -0.07 * u]))
                    nD = s * k * sp + (-u) * cp
                    ix, iy = math.floor(p[0]), math.floor(p[1])
                    if nD > -0.05 and 0 <= ix < c.w and 0 <= iy < c.h and ok[iy, ix]:
                        c.dot(p[0], p[1], colour)


def _face(c, col, P, body, H, cp, sp, nod, mouth):
    """Paints FOTA-style features: white-and-iris eyes under a lash line, shaped brows, a shaded nose with a
    nostril, two-tone lips and a chin shadow. Women get dark lashes and a touch of blush; "old" adds lines."""
    K = HEAD
    sk = ramp(col["skin"])
    tone = lambda i: "%02x%02x%02x" % tuple(int(v) for v in sk[i])
    female = bool(col.get("soft_face"))
    eye = col.get("eye", "2a1a14")
    brow = col.get("brow") or _dark(col["hair"], 0 if not col.get("old") else 2)
    fs = 0 if abs(sp) < 0.12 else (1 if sp > 0 else -1)
    side = abs(sp) > 0.85

    def pt(x, y, z):
        p = P(body([x * K, 0.074 + nod + y * K, z * K]))
        return math.floor(p[0]), math.floor(p[1]), p[2]

    # ---- eyes and brows ----
    for s in (1, -1):
        nD = s * 0.4 * sp + 0.92 * cp
        if nD < 0.1:
            continue
        ex, ey, _ = pt(s * 0.022, 0.0, 0.056)
        if side:
            ex -= fs
        near = nD > 0.55 and not side
        look = fs or -s  # iris sits towards where the character looks; front view: towards the nose
        c.dot(ex, ey, eye)
        if near or abs(cp) > 0.85:
            c.dot(ex - look, ey, "e6ded4")
        lash = _dark(col.get("brow") or col["hair"], 1) if female else tone(1)
        c.dot(ex, ey - 1, lash)
        if near and not female:
            c.dot(ex - look, ey - 1, lash)
        if not female:
            c.dot(ex, ey + 1, tone(2))  # lower lid / bag
        by = ey - (3 if female else 2)
        c.dot(ex, by, brow)
        c.dot(ex - look, by + (0 if female else 0), brow)
        if not female and near:
            c.dot(ex + look, by, brow)
        if female and near:
            c.dot(ex + (1 if s > 0 else -1) * (1 if fs == 0 else 0), by + 1, brow)

    # ---- nose ----
    nx_, ny_, _ = pt(0.0, 0.03, 0.072)
    if side:
        nx_ -= fs
    if not side:
        c.dot(nx_ + 1, ny_ - 2, tone(2))  # shadow down the right flank (key light from the left)
        c.dot(nx_ + 1, ny_ - 1, tone(2))
        c.dot(nx_ - 1 if fs >= 0 else nx_, ny_ - 2, tone(4))  # bridge highlight
    c.dot(nx_ + (1 if fs >= 0 else 0), ny_, tone(1))  # nostril / underside
    c.dot(nx_ + (0 if fs >= 0 else 1), ny_ + 1, tone(2))

    # ---- mouth ----
    mx, my, _ = pt(0.0, 0.05, 0.062)
    if side:
        mx -= fs
    wid = 1 if side else (2 if abs(cp) < 0.7 or not female else 3)
    xs = [mx - (wid // 2) + i for i in range(wid)]
    lip = col.get("lips") or tone(1)
    lip_lo = col.get("lips_lo") or (_dark(lip, 4) if col.get("lips") else tone(2))
    if col.get("mustache"):
        for x in xs + [xs[-1] + 1, xs[0] - 1]:
            c.dot(x, my - 1, _dark(col["hair"], 1))
    if mouth == 0:
        for x in xs:
            c.dot(x, my, lip if female else tone(1))
            if female:
                c.dot(x, my + 1, lip_lo)
    elif mouth == 1:
        for x in xs:
            c.dot(x, my, "3a1410")
            c.dot(x, my + 1, lip if female else tone(1))
    else:
        for x in xs:
            c.dot(x, my, lip if female else tone(1))
            c.dot(x, my + 1, "4a1a14")
    c.dot(mx, my + 3, tone(2))  # chin shadow
    if female and not side:
        c.dot(mx + (2 if fs >= 0 else -2), my - 2, _dark(lip, 4))
    if col.get("old"):
        c.dot(nx_ + 2, ny_ + 1, tone(1))  # nasolabial fold
        c.dot(nx_ + 2, ny_ + 2, tone(2))
        if not side:
            c.dot(nx_ - 2, ny_ + 1, tone(2))
            fx, fy, _ = pt(0.0, -0.045, 0.06)
            c.dot(fx - 1, fy, tone(2))
            c.dot(fx + 1, fy, tone(2))
            c.dot(fx, fy, tone(2))


def _dark(colour, tone=0):
    return "%02x%02x%02x" % tuple(int(v) for v in ramp(colour)[tone])


def sheet(rows, fw, fh, cols=None):
    cols = cols or max(len(r) for r in rows)
    out = Image.new("RGBA", (cols * fw, len(rows) * fh))
    for r, row in enumerate(rows):
        for i, im in enumerate(row):
            out.paste(im, (i * fw, r * fh))
    return out

def kneel_figure(spec, fw=64, fh=96, phi=80, head_turn=105, reach=0.95, floor=None):
    """A figure down on hands and knees (beaten to the ground), seen from the side: vertical thighs, shins flat on
    the floor, the spine bowed forward from the hips until the hands are planted under the shoulders, and the
    head hanging. The head is painted upright on its own canvas (hair and hats are shaped in screen space) and
    turned onto the end of the neck. Returns (image, head centre in frame pixels)."""
    H = spec["h"]
    col = spec
    c = Canvas(fw, fh)
    ph = math.radians(phi)
    cp, sp = math.cos(ph), math.sin(ph)
    cx, base = fw / 2.0 + spec.get("dx", 0), fh - 3.0
    sw, hw = spec.get("sw", 0.135) * 0.8, spec.get("hw", 0.052)
    leg_r = spec.get("leg_r", 1.0)
    skin, torso, pants, shoes = col["skin"], col["torso"], col.get("pants"), col["shoes"]

    def P(p):
        bx, by, bz = p
        X = -bx * cp + bz * sp
        D = bx * sp + bz * cp
        return (cx + X * H, base + (by - 1.0) * H + D * H * PITCH, D)

    # ---- legs: knees on the floor, thighs upright, shins and insteps flat behind ----
    kr, ar = 0.037 * leg_r * BULK, 0.029 * leg_r * BULK
    legs = {}
    for s in (1, -1):
        knee = np.array([s * hw, 1.0 - kr, 0.0 if s > 0 else -0.018])
        hip = knee + np.array([0, -0.232, -0.03])
        ank = np.array([s * hw, 1.0 - ar, knee[2] - 0.212])
        heel = ank + np.array([0, -0.024, -0.008])
        toe = np.array([s * hw, 1.0 - 0.02, ank[2] - 0.07])
        legs[s] = (hip, knee, ank, heel, toe)
    hipc = (legs[1][0] + legs[-1][0]) / 2
    hipc[0] = 0.0

    def bodyk(p, bow):
        return hipc + _rot_x(np.array([p[0], p[1] - 0.5, p[2]], float), -bow)

    # ---- bow the spine until the straightened arms reach the floor ----
    l1, l2 = 0.142, 0.145
    best = None
    for deg in np.arange(30, 89, 0.5):
        b = math.radians(deg)
        sh = bodyk([sw + 0.008, 0.284, 0.0], b)
        wr = np.array([sh[0], 1.0 - 0.042, sh[2] + 0.025])
        err = abs(np.linalg.norm(wr - sh) - reach * (l1 + l2))
        if best is None or err < best[0]:
            best = (err, b)
    bow = best[1]
    body = lambda p: bodyk(p, bow)

    arms = {}
    for s in (1, -1):
        sh = body([s * (sw + 0.008), 0.284, 0.0])
        wr = np.array([sh[0] + s * 0.01, 1.0 - 0.042, sh[2] + (0.025 if s > 0 else 0.045)])
        d = wr - sh
        L = min(np.linalg.norm(d), l1 + l2 - 1e-4)
        a = math.acos(np.clip((l1 * l1 + L * L - l2 * l2) / (2 * l1 * L), -1, 1))
        u = d / np.linalg.norm(d)
        # elbows bend backwards (towards -z): rotate the shoulder->wrist direction in the y/z plane
        cands = [_rot_x(u, ang) for ang in (a, -a)]
        e = min(cands, key=lambda v: v[2])
        el = sh + l1 * e
        hand = wr + np.array([0, 0.016, 0.05])
        arms[s] = (sh, el, wr, hand)

    def leg(s):
        hip, knee, ank, heel, toe = legs[s]
        part = f"leg{s}"
        thigh = pants or skin
        c.put(c.capsule(P(hip), P(knee), H * 0.05 * leg_r * BULK, H * kr), thigh, part)
        c.put(c.capsule(P(knee), P(ank), H * kr, H * ar), thigh, part)
        c.put(c.capsule(P(heel), P(toe), H * 0.024, H * 0.02), shoes, f"shoe{s}", dither=False)

    def arm(s):
        sh, el, wr, hand = arms[s]
        sleeve = col.get("sleeves", torso)
        fore = col.get("forearm", sleeve)
        part = f"arm{s}"
        c.put(c.capsule(P(sh), P(el), H * 0.034 * BULK, H * 0.031 * BULK), sleeve, part)
        c.put(c.capsule(P(el), P(wr), H * 0.031 * BULK, H * 0.027 * BULK), fore, part)
        if col.get("cuff") and fore != skin:
            c.put(c.capsule(P(wr), P(wr), H * 0.026, H * 0.026), col["cuff"], part)
        c.put(c.capsule(P(wr), P(hand), H * 0.027, H * 0.024), skin, f"hand{s}", dither=False)

    def half(ax, az):
        return math.sqrt((ax * cp) ** 2 + (az * 1.25 * sp) ** 2)

    def trunk():
        waist, hipw = spec.get("waist", 0.085), spec.get("hipw", 0.098)
        levels = [(0.53, half(hipw * 0.86, 0.056)), (0.47, half(hipw, 0.064)), (0.40, half(waist, 0.058)),
                  (0.31, half(sw * 0.95, 0.07)), (0.25, half(sw, 0.064)), (0.215, half(sw * 0.7, 0.052))]
        for (y0, r0), (y1, r1) in zip(levels, levels[1:]):
            c.put(c.capsule(P(body([0, y0, 0.004])), P(body([0, y1, 0.004])), H * r0, H * r1), torso, "torso")
        for s in (1, -1):
            c.put(c.ellipse(P(body([s * (sw + 0.004), 0.268, 0.0]))[:2], H * 0.035 * BULK, H * 0.032 * BULK),
                  torso, "torso")
        hem = col.get("pelvis", pants or torso)
        a, b = np.array(P(body([0, 0.45, 0]))[:2]), np.array(P(body([0, 0.2, 0]))[:2])
        ax = (b - a) / np.linalg.norm(b - a)
        t = (c.X - a[0]) * ax[0] + (c.Y - a[1]) * ax[1]
        if not col.get("coat"):
            c.recolor(c.parts_mask("torso") & (t < 0), hem)
        for d in col.get("decals", []):
            if d[0] == "belt":
                yb = np.array(P(body([0, d[1], 0]))[:2])
                tb = (c.X - yb[0]) * ax[0] + (c.Y - yb[1]) * ax[1]
                c.recolor(c.parts_mask("torso", "coat") & (tb > -max(1.0, H * 0.022)) & (tb <= 0), d[2], dither=False)

    def coat():
        cc = col.get("coat")
        if not cc:
            return
        hip, knee = legs[1][0], legs[1][1]
        wb = body([0, 0.40, -0.068])
        bb = body([0, 0.54, -0.08])
        wf = body([0, 0.43, 0.066])
        hem_y = min(1.0 - 0.05, hipc[1] + (cc["hem"] - 0.5) * 0.9)
        hb = np.array([0, hem_y - 0.07, min(bb[2] + 0.01, knee[2] - 0.065)])
        hf = np.array([0, hem_y, knee[2] + 0.05 + cc.get("flare", 0.0)])
        mid = np.array([0, (wf[1] + hem_y) / 2, (wf[2] + hf[2]) / 2 + 0.012])
        c.put(c.poly([P(p)[:2] for p in (wb, bb, hb, hf, mid, wf)]), cc["col"], "coat")

    def neck():
        nr = H * 0.029 * BULK
        c.put(c.capsule(P(body([0, 0.2, -0.004])), P(body([0, 0.12, 0.0])), nr * 1.08, nr), col.get("neck", skin),
              "neck")

    arm(-1)
    leg(-1)
    leg(1)
    coat()
    trunk()
    neck()
    arm(1)

    xs = [P(p)[0] for l in legs.values() for p in l] + [P(arms[1][3])[0]]
    img = c.render(shadow_box=(((min(xs) + max(xs)) / 2, base + 0.6), H * 0.32, 1.7))

    # ---- the hanging head ----
    hs = 64
    hc = Canvas(hs, hs)
    pivot_y = hs * 0.7

    def Ph(p):
        bx, by, bz = p
        X = -bx * cp + bz * sp
        D = bx * sp + bz * cp
        return (hs / 2.0 + X * H, pivot_y + (by - 0.2) * H + D * H * PITCH, D)
    ident = lambda p: np.array(p, float)
    _neck(hc, col, Ph, ident, H)
    if col.get("collar"):  # turned-up coat collar round the base of the neck
        nr = H * 0.029 * BULK
        hc.put(hc.capsule(Ph([0, 0.205, -0.01]), Ph([0, 0.24, -0.01]), nr * 1.45, nr * 1.7), col["collar"], "collar")
    _head(hc, col, Ph, ident, H, cp, sp, 0.0)
    _face(hc, col, Ph, ident, H, cp, sp, 0.0, 0)
    th = math.radians(head_turn)
    ct, st = math.cos(th), math.sin(th)
    lt = np.array([ct * LIGHT[0] + st * LIGHT[1], -st * LIGHT[0] + ct * LIGHT[1], LIGHT[2]])
    himg = hc.render(light=lt)
    pv = Ph([0, 0.2, -0.004])[:2]
    k = 4
    big = himg.resize((hs * k, hs * k), Image.NEAREST)
    big = big.rotate(-head_turn, resample=Image.NEAREST, center=(pv[0] * k, pv[1] * k))
    small = big.resize((hs, hs), Image.NEAREST)
    nk = P(body([0, 0.2, -0.004]))
    ox, oy = int(round(nk[0] - pv[0])), int(round(nk[1] - pv[1]))
    layer = Image.new("RGBA", img.size)
    layer.paste(small, (ox, oy))
    img = Image.alpha_composite(img, layer)
    hcx, hcy = Ph([0, 0.074, 0.008])[:2]
    rx, ry = hcx - pv[0], hcy - pv[1]
    head_pos = (ox + pv[0] + rx * ct - ry * st, oy + pv[1] + rx * st + ry * ct)

    # ---- land the lowest point on the standing frames' sole line and centre the pose ----
    a = np.array(img)[:, :, 3] == 255
    rows, cols = np.nonzero(a.any(1))[0], np.nonzero(a.any(0))[0]
    want = floor if floor is not None else int(base)
    dy = want - rows[-1]
    dx = int(round(fw / 2 - (cols[0] + cols[-1] + 1) / 2))
    out = Image.new("RGBA", img.size)
    out.paste(img, (dx, dy))
    return out, (head_pos[0] + dx, head_pos[1] + dy)
