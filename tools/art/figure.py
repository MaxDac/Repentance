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
        self.seamless = ()  # parts that meet without the darker "behind" seam (e.g. bare torso and legs)

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
            if part in self.seamless:
                sh &= ~np.isin(self.part, [self.parts[n] for n in self.seamless if n in self.parts])
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
        sl = np.isin(self.part, [self.parts[n] for n in self.seamless if n in self.parts])
        sp_ = np.pad(sl, 1)
        for nb, nbl, nsl in ((pp[:-2, 1:-1], bp[:-2, 1:-1], sp_[:-2, 1:-1]), (pp[2:, 1:-1], bp[2:, 1:-1], sp_[2:, 1:-1]),
                             (pp[1:-1, :-2], bp[1:-1, :-2], sp_[1:-1, :-2]), (pp[1:-1, 2:], bp[1:-1, 2:], sp_[1:-1, 2:])):
            behind |= (nb > self.part) & ~(bl & nbl) & ~(sl & nsl)
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
    c.seamless = spec.get("seamless", ())
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
        nd = spec.get("neck_drop", 0.0)  # a longer bare neck: the top of the chest starts lower below the chin
        levels = [(0.19 + nd, 0.04, 0.034), (0.212 + nd * 0.7, sw * 0.62, 0.05), (0.232 + nd * 0.4, sw * 0.86, 0.058),
                  (0.25, sw * 1.0, 0.064), (0.31, sw * 0.95, 0.07),
                  (0.40, waist, spec.get("waist_z", 0.058)), (0.47, hipw, 0.064), (0.53, hipw * 0.86, 0.056)]
        left, right = [], []
        if spec.get("profile"):  # explicit (y, half-width, back z, front z): a slim, flat-backed torso in profile
            levels = [(y, ax, (zf - zb) / 2.5, (zf + zb) / 2) for y, ax, zb, zf in spec["profile"]]
        else:
            levels = [(y, ax, az, 0.004) for y, ax, az in levels]
        for y, ax, az, zc in levels:
            cxy = P(body([shift * min(1.0, max(0.0, (y - 0.3) / 0.2)), y, zc]))
            k = 1.0 if y < 0.3 else BULK
            w = H * math.sqrt((ax * k * cp) ** 2 + (az * 1.25 * sp) ** 2)
            tilt = 0.5 * math.copysign(1.0, cp) * ax * k * sp * H * PITCH  # far shoulder sits higher, as the arms do
            left.append((cxy[0] - w, cxy[1] + tilt))
            right.append((cxy[0] + w, cxy[1] - tilt))
        shape = list(c.poly(left + right[::-1], curve=0.9))
        for s in (1, -1):  # rounded shoulder caps centred on the arm joints, so the shoulder flows into the sleeve
            cx_, cy_, cd_ = P(body([s * (sw + 0.004), spec.get("cap_y", 0.268), 0.0]))
            cr = spec.get("cap_r", 1.0)  # slender figures get small, sloping shoulder caps
            cap = c.ellipse((cx_, cy_ - 0.5 * cd_ * H * PITCH + (1 - cr) * H * 0.02), H * 0.035 * BULK * cr,
                            H * 0.032 * BULK * cr)
            new = cap[0] & ~shape[0]
            blend = cap[0] & shape[0]
            for i in (1, 2, 3):
                shape[i] = np.where(new, cap[i], np.where(blend, (shape[i] + cap[i]) / 2, shape[i]))
            shape[0] = shape[0] | cap[0]
        c.put(tuple(shape), torso, "torso")
        if col.get("rear"):  # rounded seat swelling out at the back of the near hip, easing into the thighs
            side, back, ry = (*col["rear"], 0.525)[:3]
            rc = P(body([side, ry, -back]))
            rx = H * math.sqrt((hipw * 0.62 * cp) ** 2 + (0.03 * sp) ** 2)
            c.put(c.ellipse((rc[0], rc[1]), rx, H * 0.055), torso, "torso", cast=False, clip=c.mat < 0)
        if col.get("bust") and spec.get("profile") and abs(sp) > 0.3:
            # turned to the side: the same small bust in every frame, one pixel proud of the chest line for three
            # rows, whatever the yaw or stride, kept in front of an arm hanging at her side
            f = 1 if sp > 0 else -1
            t = c.parts_mask("torso")
            by = int(round(P(body([0, spec.get("bust_y", 0.292), 0.04]))[1]))

            def front(y):
                xs = np.nonzero(t[y])[0]
                return None if not len(xs) else (xs[-1] if f > 0 else xs[0])
            near = [x for x in (front(y) for y in range(by - 3, by + 5)) if x is not None]
            if near:
                M = max(near) if f > 0 else min(near)  # the most forward point of the chest round it
                bump = np.zeros((c.h, c.w), bool)
                for k, d in ((-1, 1), (0, 2), (1, 2), (2, 1)):  # pixels proud of the chest: a soft peak
                    y, x0 = by + k, front(by + k)
                    if x0 is None:
                        continue
                    for x in range(x0 + f, M + (d + 1) * f, f):
                        if 0 <= x < c.w:
                            bump[y, x] = True
                            c.mat[y, x], c.part[y, x], c.n[y, x], c.bias[y, x] = (c.mat[y, x0], c.part[y, x0],
                                                                                  c.n[y, x0], c.bias[y, x0])
                if col.get("bust_hi"):  # dark cloth: light catches the top of the curve
                    top = bump & ~np.vstack([np.zeros((1, c.w), bool), bump[:-1]])
                    c.bias[top] += col["bust_hi"]
                c.bust_px = (f, bump, c.mat.copy(), c.part.copy(), c.n.copy(), c.bias.copy())
        elif col.get("bust"):  # a soft bust curve standing proud of the chest in profile: bust = forward depth
            for s in (1, -1):
                bc = P(body([s * 0.03, spec.get("bust_y", 0.292), col["bust"]]))
                rx = H * math.sqrt((0.032 * cp) ** 2 + (0.03 * sp) ** 2)
                bm = c.ellipse((bc[0], bc[1]), rx, H * 0.03)
                c.put(bm, torso, "torso", cast=False, clip=c.mat < 0)
                if col.get("bust_hi") and abs(sp) > 0.3:  # dark cloth: light catches the top of the curve
                    m = bm[0] & c.parts_mask("torso")
                    edge = m & ~np.vstack([np.zeros((1, c.w), bool), m[:-1]])
                    fwd = (c.X - bc[0]) * math.copysign(1.0, sp) > 0
                    c.bias[edge & fwd] += col["bust_hi"]
        if col.get("abdomen"):
            c.recolor(c.parts_mask("torso") & (c.Y >= P(body([0, spec.get("abdomen_top", 0.37), 0]))[1]),
                      col["abdomen"])
        c.recolor(c.parts_mask("torso") & (c.Y >= P(body([0, hem_top, 0]))[1]), pelvis_col)
        if col.get("neckline"):  # strapless/low-cut dress: bare skin above a slightly dipping neckline
            nl = P(body([0, col["neckline"], 0.05]))
            dip = np.clip(1 - np.abs(c.X - nl[0]) / max(H * sw * abs(cp) + 1, 1), 0, 1) * H * 0.012
            c.recolor(c.parts_mask("torso") & (c.Y < nl[1] + dip), skin)
        coat = col.get("coat")
        if coat:
            if spec.get("fitted"):  # the dress follows her waist in, then out over the seat
                coat = dict(coat, wz=spec.get("waist_z", 0.058), rear=col.get("rear"), flat_front=spec.get("flat_front"))
            _skirt(c, coat, body, P, legs, H, waist, hipw, cp, sp)
    add(2.0, trunk)

    # ---- arms ----
    arm_pts = {}
    for s in (1, -1):
        kind, f, o, e = ps["arms"][s]
        sh = body([s * (sw + 0.008), spec.get("shoulder_y", 0.284), 0.0])  # below the cap top: the cap forms the contour
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
        elif kind == "cover":  # one hand lowered over the lap
            el = body([s * (sw + 0.006), 0.40, 0.0])
            wr = body([s * 0.03, 0.50, 0.07])
            hand = body([s * 0.0, 0.535, 0.075])
        elif kind == "clutch":  # both hands holding a wrapped sheet up against the chest, elbows tucked in
            el = body([s * (sw + 0.004), 0.385, 0.03])
            wr = body([s * 0.03, 0.31, 0.08])
            hand = body([s * 0.008, 0.29, 0.088])
        elif kind == "side":  # hanging still, drawn back behind the flank
            el = body([s * (sw - 0.01), 0.40, -0.035])
            wr = body([s * (hipw - 0.01), 0.50, -0.045])
            hand = body([s * (hipw - 0.012), 0.54, -0.04])
        elif kind in ("cup", "drink"):
            el = body([s * (sw + 0.02), 0.40, 0.15])
            hand = body([s * 0.02, 0.2025 if kind == "drink" else 0.39, 0.10])
            wr = hand + np.array([s * 0.015, 0.035, 0.018])
        elif kind == "hold":  # a glass in the hand: f = hand height, o = reach forward, e = how far it's tipped (0..1)
            el = body([s * (sw + 0.02), 0.40, min(0.15, 0.04 + o * 0.55)])
            hand = body([s * 0.02, f, o])
            wr = hand + np.array([s * 0.015, 0.035, 0.018])
        elif kind == "pts":  # explicit elbow, wrist and hand positions in the body frame (f, o, e)
            el, wr, hand = (body(list(v)) for v in (f, o, e))
        elif kind == "temple":  # hand raised beside the head, a held gun pointing back into the temple
            el = body([s * (sw + 0.11), 0.12, -0.03])
            hand = body([s * 0.08, 0.09, 0.0])
            wr = hand + (el - hand) * 0.2
        else:
            fr, orr, er = (math.radians(x) for x in (f, o, e))
            d1 = np.array([s * math.sin(orr), math.cos(orr) * math.cos(fr), math.cos(orr) * math.sin(fr)])
            el = sh + 0.142 * d1
            d2 = np.array([s * math.sin(orr) * 0.3, math.cos(fr + er), math.sin(fr + er)])
            d2 /= np.linalg.norm(d2)
            wr = el + 0.145 * d2
            hand = wr + 0.036 * d2
        arm_pts[s] = (sh, el, wr, hand)
        Ds = P(sh)[2]

        def arm(s=s, sh=sh, el=el, wr=wr, hand=hand, kind=kind):
            if kind == "clutch" and cp < -0.25:  # seen from behind, arms folded over the chest are hidden by the back
                return
            sleeve = col.get("sleeves", torso)
            fore = col.get("forearm", sleeve)
            part = f"arm{s}"
            k, hk = col.get("arm_r", 1.0), max(col.get("arm_r", 1.0), 0.7)
            c.put(c.capsule(P(sh), P(el), H * 0.034 * BULK * k, H * 0.031 * BULK * k), sleeve, part)
            c.put(c.capsule(P(el), P(wr), H * 0.031 * BULK * k, H * 0.027 * BULK * k), fore, part)
            if col.get("garter"):  # an elastic sleeve garter round the upper arm, a little above the elbow
                (ax, ay, _), (bx, by, _) = P(sh), P(el)
                ln = max(math.hypot(bx - ax, by - ay), 1e-6)
                along = ((c.X - ax) * (bx - ax) + (c.Y - ay) * (by - ay)) / ln
                c.recolor(c.parts_mask(part) & (np.abs(along - ln * 0.6) < 0.75), col["garter"], dither=False)
            if col.get("cuff") and fore != skin:
                c.put(c.capsule(P(wr), P(wr), H * 0.026 * hk, H * 0.026 * hk), col["cuff"], part)
            # ps["hand_in_coat"]: the hand of that arm is slipped inside the coat front, out of sight
            if hand is not None and ps.get("hand_in_coat") != s:
                c.put(c.capsule(P(wr), P(hand), H * 0.025 * hk, H * 0.021 * hk), skin, f"hand{s}", dither=False)
        # a hand held up to the head goes in front of it (ps["front_arms"]: arms raised in front of the face);
        # col["far_arm_behind"]: the far arm stays behind a bare-armed dress in near-front and near-back views
        bias = 0.0 if col.get("far_arm_behind") and Ds < 0 else 0.05 * abs(cp)
        add(2.9 if kind == "temple" or s in ps.get("front_arms", ()) else 2.0 + Ds + bias, arm)

    if col.get("cloak"):
        add(2.4, lambda: _cloak(c, col["cloak"], body, P, legs, H, sw, cp, sp))

    if ps.get("cup"):
        def cup(s=ps["cup"]):
            hand = arm_pts[s][3]
            if ps.get("glass") == "gin":  # a small tumbler of bathtub gin; ps["full"] says whether any is left
                tip = ps["arms"][s][3]
                rim = hand + np.array([0, -0.038 + 0.01 * tip, -0.04 * tip])
                bottom = hand + np.array([0, 0.01, 0.01 * tip])
                c.put(c.capsule(P(bottom), P(rim), H * 0.028, H * 0.033), "aac4cc", "cup", dither=False)
                if ps.get("full"):
                    c.put(c.capsule(P(rim), P(rim), H * 0.022, H * 0.022), "e4ecd2", "gin", dither=False)
                return
            tipped = ps["arms"][s][0] == "drink"
            rim = hand + np.array([0, -0.07, -0.028 if tipped else 0])
            bottom = hand + np.array([0, 0.015, 0.015])
            c.put(c.capsule(P(bottom), P(rim), H * 0.035, H * 0.04), "b8b4a4", "cup", dither=False)
            c.put(c.capsule(P(rim), P(rim), H * 0.025, H * 0.025), "a86024", "whiskey", dither=False)
        add(3.0, cup)

    if ps.get("candlestick"):  # a brass candlestick gripped by the stem in the hand of arm side, foot outwards
        def candlestick(spec_=ps["candlestick"]):
            s, way = spec_ if isinstance(spec_, tuple) else (spec_, None)
            _, el, wr, hand = arm_pts[s]
            d = np.array(way, float) if way is not None else hand - el
            d /= max(np.linalg.norm(d), 1e-6)
            brass = "c8a040"
            fist = hand - d * 0.006
            foot = fist + d * 0.085
            c.put(c.capsule(P(fist - d * 0.035), P(foot), H * 0.011, H * 0.012), brass, "candlestick", dither=False)
            c.put(c.capsule(P(fist + d * 0.04), P(fist + d * 0.04), H * 0.018, H * 0.018), brass, "candlestick",
                  dither=False)
            c.put(c.capsule(P(foot), P(foot + d * 0.008), H * 0.03, H * 0.03), brass, "candlestick", dither=False)
            c.put(c.capsule(P(fist - d * 0.035), P(fist - d * 0.04), H * 0.024, H * 0.024), brass, "candlestick",
                  dither=False)
            c.put(c.capsule(P(fist - d * 0.045), P(fist - d * 0.075), H * 0.01, H * 0.01), "f0e8d0", "candle",
                  dither=False)
            c.put(c.capsule(P(wr), P(fist), H * 0.025, H * 0.022), col["skin"], f"hand{s}", dither=False)
        add(2.0 + P(arm_pts[(ps["candlestick"][0] if isinstance(ps["candlestick"], tuple) else ps["candlestick"])][0])[2]
            + 0.08, candlestick)

    if ps.get("powder"):  # a pinch of white powder held up in the fingertips of arm ps["powder"]
        def powder(s=ps["powder"]):
            tip = P(arm_pts[s][3] + np.array([0, -0.012, 0.012]))
            c.dot(tip[0], tip[1], "+f4f2ee")
            c.dot(tip[0] + 1, tip[1], "+e8e4e0")
        add(3.1, powder)

    if ps.get("gun"):  # a revolver in the hand of arm ps["gun"], barrel along the forearm (or ps["gun_dir"])
        def gun(s=ps["gun"]):
            _, el, wr, hand = arm_pts[s]
            d = np.array(ps["gun_dir"], float) if ps.get("gun_dir") else hand - el
            d = d / max(np.linalg.norm(d), 1e-6)
            up = np.array([0, -1.0, 0]) - d * (-d[1])
            up /= max(np.linalg.norm(up), 1e-6)
            steel, wood = "4a4c58", "5a3a24"
            fist = hand - d * 0.01
            # the grip, raked back below the fist, then the fist closed round it
            c.put(c.capsule(P(fist + up * 0.004), P(fist - up * 0.05 - d * 0.02), H * 0.016, H * 0.018), wood, "gun",
                  dither=False)
            c.put(c.capsule(P(wr), P(fist), H * 0.028, H * 0.027), col["skin"], f"hand{s}", dither=False)
            # frame and cylinder sitting on top of the fist, hammer cocked back, barrel with a front sight
            base_ = fist + up * 0.026
            c.put(c.capsule(P(base_ - d * 0.02), P(base_ + d * 0.03), H * 0.017, H * 0.017), steel, "gun", dither=False)
            c.put(c.capsule(P(base_ + d * 0.004), P(base_ + d * 0.026), H * 0.023, H * 0.023), steel, "gun",
                  dither=False)
            c.put(c.capsule(P(base_ - d * 0.022), P(base_ - d * 0.036 + up * 0.016), H * 0.008, H * 0.007), steel,
                  "gun", dither=False)
            bar = base_ + up * 0.006
            muzzle = bar + d * 0.115
            c.put(c.capsule(P(bar + d * 0.02), P(muzzle), H * 0.012, H * 0.011), steel, "gun", dither=False)
            c.put(c.capsule(P(muzzle - d * 0.006 + up * 0.012), P(muzzle - d * 0.006 + up * 0.012), H * 0.006,
                            H * 0.006), steel, "gun", dither=False)
            # trigger guard under the frame, just ahead of the fist
            g = P(fist + d * 0.03 - up * 0.004)
            c.dot(g[0], g[1], "1a1a20")
        add(2.95 if ps["arms"][ps["gun"]][0] == "temple" else 2.0 + P(arm_pts[ps["gun"]][0])[2] + 0.08, gun)

    if col.get("held_mask"):  # a mask taken off and held in the hand of arm side, face out: (side, plate, accent)
        def held(spec_=col["held_mask"]):
            s, mc, ac = spec_
            hx_, hy_ = P(arm_pts[s][3])[:2]
            hx_ += s * 1.0
            for k in (1, -1):  # the antlers, branching up off the brow
                c.put(c.capsule((hx_ + k * 1.2, hy_ - 2.6), (hx_ + k * 3.4, hy_ - 6.4), 0.7, 0.5), ac, "prop",
                      dither=False)
                c.put(c.capsule((hx_ + k * 2.6, hy_ - 5.0), (hx_ + k * 1.6, hy_ - 7.4), 0.5, 0.4), ac, "prop",
                      dither=False)
            c.put(c.ellipse((hx_, hy_ - 0.6), 2.3, 2.6), mc, "prop", dither=False)
            c.put(c.capsule((hx_, hy_ + 0.8), (hx_, hy_ + 3.6), 1.4, 0.9), mc, "prop", dither=False)
            for k in (1, -1):
                c.dot(math.floor(hx_ + k * 1.0), math.floor(hy_ - 1.0), "141016")
            c.dot(math.floor(hx_), math.floor(hy_ + 3.6), "141016")
        add(3.0, held)

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
        if col.get("open_collar") and cp > 0.05:  # top button undone: the collar parts at the throat over bare skin
            fx = P(body([0, 0.2, 0.05]))[0]
            notch = band & (np.abs(c.X - fx) < max(neck_r * 0.85 * cp, 0.6))
            c.recolor(notch, col["skin"])
    add(2.05, collar)

    def head():
        _head(c, col, P, body, H, cp, sp, nod)
    add(2.6, head)
    if col.get("hair_style") == "long":
        # The mane falls behind the neck and shoulders unless the figure is seen from the back.
        add(1.9 if facing else 2.7, lambda: _long_hair_back(c, col, P, body, H, cp, sp, nod))
    if col.get("hat") in ("veil", "hood"):
        add(1.9 if facing else 2.7, lambda: _veil_back(c, col, P, body, H, cp, sp, nod))
    if col.get("hair_front") and facing:
        add(2.65, lambda: _hair_front(c, col, P, body, H, cp, sp, nod))

    for _, fn in sorted(prims, key=lambda kv: kv[0]):
        fn()
    if getattr(c, "bust_px", None) is not None:  # the bust stays in front of an arm hanging at her side
        f, bump, mat, part, n, bias = c.bust_px
        arm = c.parts_mask("arm1", "arm-1", "hand1", "hand-1")
        over = bump & arm
        for y in np.nonzero(over.any(1))[0]:  # an arm reaching across in front of her chest stays on top
            bx, ax = np.nonzero(bump[y])[0], np.nonzero(arm[y])[0]
            if (ax * f).max() > (bx * f).max():
                over[y] = False
        over &= c.parts_mask("arm1", "arm-1")
        c.mat[over], c.part[over], c.n[over], c.bias[over] = mat[over], part[over], n[over], bias[over]

    if col.get("front_line") and abs(cp) > 0.3:  # three-quarter view: a straight, vertical front from waist to thighs
        r0, r1 = (int(P(body([0, v, 0]))[1]) for v in col["front_line"])
        sgn = 1 if sp >= 0 else -1
        body_px = (c.mat >= 0) & ~c.parts_mask("hair", "hairback", "hand1", "hand-1")
        fronts = [(np.nonzero(body_px[y])[0] * sgn).max() for y in range(r0, r1 + 1) if body_px[y].any()]
        if fronts:
            cut = c.parts_mask("torso", "arm1", "arm-1") & (np.arange(c.w)[None, :] * sgn > min(fronts))
            cut[:r0] = cut[r1 + 1:] = False
            c.mat[cut], c.part[cut], c.bias[cut] = -1, -1, 0
    _decals(c, col, P, body, H, cp, sp, legs, ps)
    if facing:
        _face(c, col, P, body, H, cp, sp, nod, ps["mouth"])
        if col.get("mask"):
            _mask(c, col, P, body, H, cp, sp, nod)
    elif col.get("mask") and col["mask"][0] == "animal":  # ears and antlers still show from behind
        _mask(c, col, P, body, H, cp, sp, nod)
    if ps.get("front_arms"):  # the face's painted features stay behind hands raised in front of it
        over = c.parts_mask(*(f"{k}{s}" for s in ps["front_arms"] for k in ("arm", "hand")))
        c.ink = [(x, y, k) for x, y, k in c.ink if not (0 <= x < c.w and 0 <= y < c.h and over[y, x])]
    if ps.get("marks") is not None:  # screen positions of the hands and the mouth, for props painted on afterwards
        for s in arm_pts:
            ps["marks"][f"hand{s}"] = P(arm_pts[s][3])[:2]
            ps["marks"][f"wrist{s}"] = P(arm_pts[s][2])[:2]
        ps["marks"]["mouth"] = P(body([0, 0.074 + nod + 0.05 * HEAD, 0.062 * HEAD]))[:2]
    shx = (P(legs[1][2])[0] + P(legs[-1][2])[0]) / 2
    return c.render(shadow_box=((shx, base + 0.6), H * 0.15, 1.7))


def _neck(c, col, P, body, H):
    neck_r = H * col.get("neck_r", 0.029) * BULK
    lean = col.get("neck_lean", 0.0)  # a slender neck rises slightly forward from the shoulders to the jaw
    c.put(c.capsule(P(body([0, 0.13, lean])), P(body([0, 0.228, -0.004 - lean])), neck_r, neck_r * 1.08),
          col.get("neck", col["skin"]), "neck")


def _head(c, col, P, body, H, cp, sp, nod):
    """Skull, jaw, profile features, ear, hair and hat (the painted face dots come later from _face)."""
    skin = col["skin"]
    hx_, hy_, _ = P(body([0.0, 0.074 + nod, 0.008]))
    hrx = H * HEAD * math.sqrt((col.get("face_w", 0.048) * cp) ** 2 + (0.056 * sp) ** 2)
    hry = H * 0.077 * HEAD
    fs = math.copysign(1.0, sp) if abs(sp) > 1e-3 else 0.0
    facing = cp > -0.25

    def ell3(center, ax, ay, az):
        x, y, _ = P(center)
        return (x, y), H * math.sqrt((ax * cp) ** 2 + (az * sp) ** 2), H * ay

    if col.get("chin_cut") or col.get("clean_jaw"):
        before = (c.mat.copy(), c.part.copy(), c.n.copy(), c.bias.copy())
    if abs(sp) > 0.3:  # back of the skull: heads are deeper than they are wide
        oc, orx, ory = ell3(body([0, 0.068 + nod, -0.018 * HEAD]), 0.045 * HEAD, 0.064 * HEAD, 0.052 * HEAD)
        c.put(c.ellipse(oc, orx, ory), skin, "head", dither=False)
    c.put(c.ellipse((hx_, hy_), hrx, hry), skin, "head", dither=False)
    jc, jrx, jry = ell3(body([0, 0.118 + nod, 0.018]), col.get("jaw_w", 0.039) * HEAD, 0.044 * HEAD, 0.05 * HEAD)
    c.put(c.ellipse(jc, jrx, jry), skin, "head", dither=False)
    if col.get("chin_w") and facing:  # a square jaw: fill the round jaw out to its corners
        cw = col["chin_w"] * HEAD
        a = P(body([-cw, 0.118 + nod + 0.036 * HEAD, 0.024]))
        b = P(body([cw, 0.118 + nod + 0.036 * HEAD, 0.024]))
        c.put(c.capsule(a[:2], b[:2], H * 0.014, H * 0.014), skin, "head", dither=False)
    if abs(sp) > 0.3:
        ys = 0.074 + nod
        # brow ridge, nose and chin give the profile its shape
        c.put(c.capsule(P(body([0, ys - 0.012 * HEAD, 0.058 * HEAD])), P(body([0, ys - 0.004 * HEAD, 0.06 * HEAD])), 0.5, 0.5),
              skin, "head", dither=False)
        c.put(c.capsule(P(body([0, ys + 0.008 * HEAD, 0.058 * HEAD])), P(body([0, ys + 0.028 * HEAD, 0.066 * HEAD])), 0.55, 0.7),
              skin, "head", dither=False)
        c.put(c.capsule(P(body([0, ys + 0.066 * HEAD, 0.05 * HEAD])), P(body([0, ys + 0.078 * HEAD, 0.046 * HEAD])), 0.8, 0.8),
              skin, "head", dither=False)
    if col.get("chin_cut"):  # lift the chin: drop the lowest rows of every head column, showing what lay behind
        head = c.parts_mask("head")
        cut = head.copy()
        cut[:-1] &= ~head[1:]
        cut &= c.Y > hy_
        for _ in range(col["chin_cut"] - 1):
            cut[:-1] |= cut[1:] & head[:-1]
        for dst, src in zip((c.mat, c.part, c.n, c.bias), before):
            dst[cut] = src[cut]
    if col.get("full_jaw") and facing and abs(sp) < 0.65:
        # a turned head loses the far cheek and jaw, leaving the mouth on the outline: round the lower face out
        # to an oval round the mouth, lit like the near cheek, the far jaw tapering gently in to a small round chin
        mx_, my_ = (math.floor(v) for v in P(body([0, 0.074 + nod + 0.05 * HEAD, 0.062 * HEAD]))[:2])
        m = np.zeros((c.h, c.w), bool)
        turn = 1 if abs(sp) > 0.45 else 0  # further round, the far cheek really is hidden: a slimmer oval
        for dy_, left, right in ((-2, 3, 3), (-1, 3, 2), (0, 3, 2), (1, 2, 1), (2, 1, 0)):
            if 0 <= my_ + dy_ < c.h:
                m[my_ + dy_, max(mx_ - left, 0):max(mx_ + right - turn, mx_) + 1] = True
        m &= ~c.parts_mask("head", "hair", "hairback")
        ones = np.ones((c.h, c.w))
        c.put((m, ones * 0.1, ones * 0.15, ones), skin, "head", dither=False, cast=False)
    if abs(cp) > 0.1 and abs(sp) > 0.15 and facing:
        ex, ey, _ = P(body([-fs * 0.05 * 1, 0.088 + nod, -0.006]))
        ear_side = -1 if sp > 0 else 1
        ex, ey, ed = P(body([ear_side * 0.05, 0.088 + nod, -0.008]))
        if ed > -0.02 and col.get("hair_style") not in ("long", "bob"):
            c.put(c.ellipse((ex, ey), H * 0.011, H * 0.017), skin, "ear", dither=False)
    _hair(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod)
    if col.get("chignon") and abs(sp) > 0.2 or col.get("chignon") and cp < -0.25:
        # a low knot of hair at the nape, behind the skull and never over the face
        kc = P(body([0, 0.128 + nod, -0.066]))
        r = H * col["chignon"]
        m, kx, ky, kz = c.ellipse((kc[0], kc[1]), r * 1.15, r * 0.85)
        if facing:
            m &= ~c.parts_mask("head")
        c.put((m, kx, ky, kz), col["hair"], "hair", dither=False, cast=False)
        c.bias[m & (np.floor(c.X + c.Y) % 3 == 0)] -= 1
    # Faces are lit from the front: lift the jaw shadow so it does not read as stubble, and keep only a
    # one-tone shade on the far cheek.
    face = c.parts_mask("head") & (c.Y > hy_ - 1)
    c.bias[face] += 1
    if col.get("soft_face"):
        c.bias[c.parts_mask("neck") & (c.Y > hy_ - 1)] += 1
    _hat(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod)
    if col.get("clean_jaw") and facing:
        # where the skull ellipse meets the square jaw a lone head pixel can stick out of the jaw outline with
        # nothing above or below it: show what lay behind it instead
        head = c.parts_mask("head")
        up, down = np.zeros_like(head), np.zeros_like(head)
        up[1:], down[:-1] = head[:-1], head[1:]
        spur = head & ~up & ~down & (c.Y > hy_)
        for dst, src in zip((c.mat, c.part, c.n, c.bias), before):
            dst[spur] = src[spur]


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
    if coat.get("wz"):
        wt = width(waist + 0.004, coat["wz"] * 1.25)
    if all(abs(l[1][1] - l[0][1]) < 0.12 for l in legs.values()):
        _seated_skirt(c, coat, body, P, legs, H, flare, tc, hc, wt, wh)
        return
    xs = []
    pad = coat.get("hem_pad", 0.045)  # hem reach past each leg at the hem line
    for s, leg in legs.items():
        p = _leg_at(leg, hem)
        if p is None:
            p = leg[2]
        q = P(p)
        xs += [q[0] - H * (pad + flare), q[0] + H * (pad + flare)]
    hem_y = P(np.array([0, hem, 0]))[1]
    # coat["hem_legs"]: the hem follows the legs alone, narrowing below the hips when they stand together
    hips = [] if coat.get("hem_legs") else [hc[0] - wh * 1.05, hc[0] + wh * 1.05]
    lo, hi = min(xs + hips), max(xs + hips)
    pts = [(tc[0] - wt, tc[1]), (hc[0] - wh, hc[1]), (lo, hem_y), (hi, hem_y), (hc[0] + wh, hc[1]), (tc[0] + wt, tc[1])]
    if coat.get("flat_front") and abs(sp) > 0.3:
        # a flat belly: in profile the front of the skirt hangs straight down from the waist, only the stepping
        # leg pushing the hem forward
        f = 1 if sp > 0 else -1
        fx = tc[0] + f * wt
        i = 4 if f > 0 else 1
        pts[i] = (fx, hc[1])
        edge = [x for x in xs if (x - fx) * f > 0]
        if f > 0:
            pts[3] = (max(edge + [fx]), hem_y)
        else:
            pts[2] = (min(edge + [fx]), hem_y)
    c.put(c.poly(pts), coat["col"], "coat")
    if coat.get("rear"):  # the cloth drawn over the seat, standing out behind the back line
        side, back, ry = (*coat["rear"], 0.525)[:3]
        rc = P(body([side, ry, -back]))
        rx = H * math.sqrt((hipw * 0.62 * cp) ** 2 + (0.03 * sp) ** 2)
        c.put(c.ellipse((rc[0], rc[1]), rx, H * 0.055), coat["col"], "coat", cast=False, clip=c.mat < 0)


def _seated_skirt(c, coat, body, P, legs, H, flare, tc, hc, wt, wh):
    """A dress or cassock on a sitting figure: it wraps the hips, lies over the lap along the thighs and falls from
    the knees to the hem, leaving the chair visible beneath the thighs."""
    seat = max(l[0][1] for l in legs.values()) + 0.045
    sy = P(np.array([0, seat, 0]))[1]
    c.put(c.poly([(tc[0] - wt, tc[1]), (hc[0] - wh, hc[1]), (hc[0] - wh * 0.97, sy - 2), (hc[0] - wh * 0.7, sy),
                  (hc[0] + wh, sy), (hc[0] + wh, hc[1]), (tc[0] + wt, tc[1])]), coat["col"], "coat")
    below = coat["hem"] - 0.735  # how far the hem hangs below the knee when standing
    for s in sorted(legs, key=lambda k: -P(legs[k][1])[2]):
        hip, knee, ank = legs[s][:3]
        fwd = (knee - hip) / max(np.linalg.norm(knee - hip), 1e-6)
        lap = c.capsule(P(hip - fwd * 0.03), P(knee + fwd * 0.012), H * 0.064, H * 0.05)
        c.put(lap, coat["col"], "coat")
        hem_y = min(knee[1] + 0.03 + below, ank[1] - 0.012)
        if hem_y <= knee[1] + 0.03:
            continue
        kz = knee[2]
        pts = [knee + np.array([0, 0.0, -0.035]), knee + np.array([0, -0.01, 0.05]),
               np.array([knee[0], hem_y, kz + 0.06 + flare]), np.array([knee[0], hem_y, kz - 0.045 - flare * 0.5])]
        m = c.put(c.poly([P(p)[:2] for p in pts], curve=0.7), coat["col"], "coat")
        # a couple of soft folds falling from the knee
        for off in (0.012, 0.035):
            top_ = P(knee + np.array([0, 0.02, off]))
            bot = P(np.array([knee[0], hem_y, kz + off * 1.4]))
            t = np.clip((c.Y - top_[1]) / max(bot[1] - top_[1], 1), 0, 1)
            fold = (np.abs(c.X - (top_[0] + (bot[0] - top_[0]) * t)) < 0.5) & (c.Y > top_[1]) & (c.Y < bot[1] - 1)
            c.bias[m & fold] -= 1


def _cloak(c, cloak, body, P, legs, H, sw, cp, sp):
    """A long hooded cloak hanging from the neck to the ankles, closed over the arms: one bell-shaped drape whose
    hem follows the legs, with a few dark fold lines and the front opening."""
    hem = cloak.get("hem", 0.95)

    def width(ax, az):
        return H * math.sqrt((ax * cp) ** 2 + (az * sp) ** 2)

    levels = [(0.205, 0.05, 0.05), (0.235, sw + 0.03, 0.08), (0.27, sw + 0.055, 0.105), (0.36, sw + 0.065, 0.13),
              (0.55, sw + 0.075, 0.15)]
    left, right = [], []
    for y, ax, az in levels:
        q = P(body([0, y, 0.0]))
        w = width(ax, az)
        left.append((q[0] - w, q[1]))
        right.append((q[0] + w, q[1]))
    xs = []
    hem_y = P(body([0, hem, 0]))[1]
    for leg in legs.values():
        p = _leg_at(leg, hem)
        q = P(p if p is not None else leg[2])
        xs += [q[0] - H * 0.07, q[0] + H * 0.07]
    mid = P(body([0, hem, 0]))[0]
    wh = width(sw + 0.085, 0.165)
    lo, hi = min(xs + [mid - wh]), max(xs + [mid + wh])
    pts = left + [(lo, hem_y)] + [(hi, hem_y)] + right[::-1]
    m = c.put(c.poly(pts, curve=0.6), cloak["col"], "coat")
    if m is None:
        return
    # vertical folds fanning out from the shoulders
    top_y = P(body([0, 0.3, 0]))[1]
    cx0 = P(body([0, 0.3, 0]))[0]
    for k in (-0.62, -0.25, 0.25, 0.62):
        x_top = cx0 + k * width(sw + 0.04, 0.11)
        x_bot = mid + k * 1.2 * (hi - lo) / 2
        t = np.clip((c.Y - top_y) / max(hem_y - top_y, 1), 0, 1)
        fold = (np.abs(c.X - (x_top + (x_bot - x_top) * t)) < 0.6) & (c.Y > top_y)
        c.bias[m & fold] -= 1
    # the front opening: a lighter edge down the middle, only seen from the front
    if cp > 0.3:
        for y in np.arange(0.24, hem, 0.004):
            q = P(body([0, y, 0.12]))
            ix, iy = math.floor(q[0]), math.floor(q[1])
            if 0 <= iy < c.h and 0 <= ix < c.w and m[iy, ix]:
                c.bias[iy, ix] += 1


def _long_hair_back(c, col, P, body, H, cp, sp, nod):
    """Voluminous wavy mane falling to the shoulder blades (drawn behind the head)."""
    hc = P(body([0, 0.15 + nod, -0.03]))
    rx = H * math.sqrt((0.115 * cp) ** 2 + (0.09 * sp) ** 2) * col.get("hair_back_width", 1.0)
    extension = H * (col.get("hair_back", 0.29) - 0.29) / 2
    center = (hc[0] - 0.045 * H * sp, hc[1] + extension)
    ry = H * 0.14 + extension
    m, nx, ny, nz = c.ellipse(center, rx, ry)
    wave = np.sin(c.Y / 1.7) * 0.9
    m2, _, _, _ = c.ellipse(center, rx + wave, ry)
    top = P(body([0, 0.02 + nod, 0]))[1]
    keep = m2 & (c.Y > top)
    if abs(sp) > 0.15 and cp > -0.25:
        # In profile/3-4 the mane must stay behind the jaw, never under the chin.
        hx0, hy0 = P(body([0, 0.077 + nod, 0.0]))[:2]
        keep &= ~(((c.X - hx0) * math.copysign(1.0, sp) > -1.5) & (c.Y > hy0 + 1))
    c.put((keep, nx, ny, nz), col["hair"], "hairback", cast=False)
    upper = c.parts_mask("hairback") & (c.Y < P(body([0, 0.20 + nod, 0]))[1])
    c.bias[upper] += col.get("hair_back_shade", 0)


def _hair_front(c, col, P, body, H, cp, sp, nod):
    """Long wavy locks brought forward over the shoulders, falling down the chest to col["hair_front"] (body y)."""
    end = col["hair_front"]
    over = c.parts_mask("torso", "hair", "hairback")
    chin = P(body([0, 0.165 + nod, 0]))[1]
    lock = np.zeros_like(over)
    nx = ny = nz = None
    for s in (1, -1):
        n = 14
        for i in range(n + 1):
            t = i / n
            y = 0.175 + nod * (1 - t) + (end - 0.175) * t
            x = s * (0.075 - 0.035 * t) + 0.008 * math.sin(t * 7.0 + s)
            # an optional forward swell at chest height, where the locks may stand proud of the torso outline
            bump = col.get("hair_bulge", 0.0) * math.exp(-((t - 0.62) / 0.2) ** 2)
            cx, cy, _ = P(body([x, y, 0.02 + 0.05 * t + bump]))
            r = H * (0.03 - 0.014 * t)
            m, ex, ey, ez = c.ellipse((cx, cy), r, r * 1.2)
            proud = bump > 0 and bump >= 0.4 * col["hair_bulge"]
            # never across the face; below the shoulders it only lies on the body (save for the chest swell)
            m &= (True if proud else over) & (c.Y > chin)
            if nx is None:
                nx, ny, nz = ex, ey, ez
            else:
                nx, ny, nz = (np.where(m & ~lock, ex, nx), np.where(m & ~lock, ey, ny), np.where(m & ~lock, ez, nz))
            lock |= m
    c.put((lock, nx, ny, nz), col["hair"], "hair", cast=False)
    stripe = (np.floor(c.X * 2 + np.round(2 * np.sin(c.Y / 2.1))) % 5 == 0)
    c.bias[lock & stripe] -= 1


def _hair(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod):
    style = col.get("hair_style", "short")
    hair = col["hair"]
    fs = sp
    vol = col.get("hair_vol", {"short": 0.9, "bald": 0.2, "long": 3.0, "bob": 2.2, "slick": 0.5, "cropped": 0.3}[style])
    cropped = style == "cropped"  # short back and sides: close to the skull, ears and nape left bare
    back_off, back_w = (0.1 + 0.004 * H, 0.003 * H) if cropped else (0.25 + 0.012 * H, 0.008 * H)
    m, nx, ny, nz = c.ellipse((hx_ - back_off * fs, hy_ - 0.6), hrx + vol + back_w * abs(fs), hry + vol * 0.8)
    u = np.clip((c.X - hx_) / max(hrx, 1), -1, 1)
    front = hy_ - hry * (0.5 if style in ("long", "bob") else 0.64) + (0.5 if style == "slick" else 0)
    nape = hy_ + hry * (0.55 if style != "bob" else 0.95)
    if cropped:
        nape = hy_ + hry * 0.45
    if style == "long":
        nape = hy_ + hry * 1.15
    # how much a column is "back of the head" vs face
    back = np.clip(-u * fs * 1.8 + 0.15, 0, 1)
    sides = np.clip((np.abs(u) - 0.72) * 4.0, 0, 1) * abs(cp)
    if style in ("long", "bob"):
        sides = np.clip((np.abs(u) - col.get("hair_side", 0.55)) * 3.0, 0, 1) * max(abs(cp), 0.3)
        sides *= np.where(u * fs > 0, np.clip(1 - abs(sp) * (5.0 if style == "long" else 2.4), 0, 1), 1.0)
        side_line = hy_ + hry * (0.95 if style == "long" else 0.75)
    else:
        side_line = hy_ + hry * (-0.15 if cropped else 0.15)
    line = front + (nape - front) * back
    line = np.maximum(line, front + (side_line - front) * sides)
    fringe = None
    if col.get("fringe") and cp > -0.25:  # a straight fringe cut just above the brows
        fringe = (np.abs(u) < 0.95) & (c.Y < hy_ - hry * col["fringe"])
        line = np.where(np.abs(u) < 0.95, np.maximum(line, hy_ - hry * col["fringe"]), line)
    if cp < -0.25:  # seen from behind: all hair
        line = np.full_like(line, nape)
    mask = m & (c.Y < line)
    if style == "bald":
        mask &= (c.Y > hy_ - hry * 0.1) & (back > 0.3 if cp > -0.25 else True)
    c.put((mask, nx, ny, nz), hair, "hair", dither=False)
    if col.get("combover"):  # a few long strands combed sideways across the bare crown, the scalp between them
        strands = m & (c.Y < hy_ - hry * 0.5) & (np.floor(c.Y) % 2 == 1) & (np.floor(c.X + c.Y) % 3 != 0)
        c.put((strands, nx, ny, nz), col["combover"], "hair", dither=False, cast=False)
    if style != "bald":
        # FOTA hair has a lit crown and a darker underside rather than a flat helmet
        top = hy_ - hry - vol * 0.8
        hm = c.parts_mask("hair")
        c.bias[hm & (c.Y > top + 1.2) & (c.Y < top + 3.2) & ((c.X - hx_) * (1 if fs >= 0 else -1) < hrx * 0.4)] += 1
        c.bias[hm & (c.Y > hy_ + hry * 0.05)] -= 1
    if style in ("long", "bob"):
        stripe = (np.floor(c.X * 2 + np.round(2 * np.sin(c.Y / 2.1))) % 5 == 0)
        c.bias[c.parts_mask("hair", "hairback") & stripe] -= 1
    if fringe is not None:  # combed-down strands: darker partings running down to the cut
        hm = c.parts_mask("hair") & fringe & (c.Y > hy_ - hry * 0.95)
        c.bias[hm & (np.floor(c.X) % 3 == 0)] -= 1


def _hat(c, col, P, body, H, hx_, hy_, hrx, hry, cp, sp, nod):
    hat = col.get("hat")
    if not hat:
        return
    hc = col["hat_col"]
    if hat == "fedora":
        by = hy_ - hry * col.get("brim_y", 0.42)
        brx = H * col.get("brim_w", 0.092)
        bry = 1.0 + brx * PITCH * abs(cp) * 0.9
        snap = 0.12 * sp
        m = c.put(c.ellipse((hx_ + 0.6 * sp, by), brx, bry, snap), hc, "brim")
        crx = H * math.sqrt((0.054 * cp) ** 2 + (0.062 * sp) ** 2)
        crown_h = col.get("crown_h", 0.045)
        ccy = by - H * crown_h * 0.78
        crown = c.ellipse((hx_ - 0.4 * sp, ccy), crx, H * crown_h)
        if col.get("crown_pinch"):  # the crown tapers towards a flat-topped, pinched peak
            taper = np.clip((by - c.Y) / max(H * crown_h * 1.6, 1), 0, 1) * col["crown_pinch"]
            crown = (crown[0] & (np.abs(c.X - (hx_ - 0.4 * sp)) <= crx * (1 - taper) + 0.5),) + tuple(crown[1:])
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
    elif hat == "visor":
        # a desk clerk's celluloid eyeshade: a thin band round the brow and a translucent green bill jutting forward
        by = hy_ - hry * 0.42
        c.put(c.ellipse((hx_, by), hrx + 0.6, 1.0), col.get("band", hc), "band", dither=False, cast=False)
        bill = P(body([0, 0.034 + nod, 0.09]))
        brx = H * math.sqrt((0.056 * cp) ** 2 + (0.05 * sp) ** 2)
        c.put(c.ellipse((bill[0] + 0.3 * sp, bill[1] + 0.3), brx, 1.6), hc, "bill", dither=False)
        c.bias[c.parts_mask("head") & (c.Y > by) & (c.Y < by + 3)] -= 1
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
    elif hat == "hood":
        # A cloak's hood pulled up over the head, leaving only the face (or the mask) showing.
        fx, fy, _ = P(body([0, 0.086 + nod, 0.045]))
        frx, fry = max(hrx * (0.55 + 0.2 * abs(cp)), 2.4), hry * 0.8
        face = c.ellipse((fx, fy), frx, fry)[0] if cp > -0.25 else np.zeros_like(c.mat, bool)
        hood = c.ellipse((hx_ - 0.9 * sp, hy_ - 0.6), hrx + 2.2, hry + 2.0)
        c.put(hood, hc, "veil", clip=~face & (c.Y < hy_ + hry * 0.75))
        c.bias[c.parts_mask("veil") & (c.Y < hy_ - hry * 0.6) & ((c.X - hx_) * (1 if sp >= 0 else -1) < 0)] += 1
    elif hat == "cowl":
        # A deep monk's cowl: peaked at the back of the crown, pulled low over the brow and falling in one piece
        # onto the shoulders, where the cloak takes over. The face opening sits in shadow.
        fx, fy, _ = P(body([0, 0.09 + nod, 0.05]))
        frx, fry = max(hrx * (0.5 + 0.22 * abs(cp)), 2.4), hry * 0.78
        face = c.ellipse((fx, fy), frx, fry)[0] if cp > -0.25 else np.zeros_like(c.mat, bool)
        back = -math.copysign(1.0, sp) if abs(sp) > 0.15 else 0.0
        hood = c.ellipse((hx_ + back * 1.2, hy_ - 0.8), hrx + 3.2, hry + 2.8)
        apex = (hx_ + back * (hrx + 2.5), hy_ - hry - 5.5)
        peak = c.poly([(hx_ - hrx - 1.5, hy_ - hry * 0.2), apex, (hx_ + hrx + 1.5, hy_ - hry * 0.2)])
        lo = P(body([0, 0.245, -0.01]))
        drape_w = H * math.sqrt((0.105 * cp) ** 2 + (0.085 * sp) ** 2)
        drape = c.poly([(hx_ - hrx - 3, hy_), (hx_ + hrx + 3, hy_), (lo[0] + drape_w, lo[1]), (lo[0] - drape_w, lo[1])])
        for shape in (drape, peak, hood):
            c.put(shape, hc, "veil", clip=~face)
        rim = c.ellipse((fx, fy), frx + 1.3, fry + 1.3)[0] & ~face & c.parts_mask("veil")
        c.bias[rim] += 1
        # the head inside the cowl is lost in shadow except where the mask catches the light
        c.bias[c.parts_mask("head", "hair", "ear") & face] -= 2
    elif hat == "cowl_down":
        # the cowl pushed back off the head, bunched round the neck and lying over the shoulders
        neck_ = P(body([0, 0.17, -0.02]))
        lo = P(body([0, 0.26, -0.01]))
        top_w = H * math.sqrt((0.06 * cp) ** 2 + (0.05 * sp) ** 2)
        drape_w = H * math.sqrt((0.11 * cp) ** 2 + (0.09 * sp) ** 2)
        drape = c.poly([(neck_[0] - top_w, neck_[1]), (neck_[0] + top_w, neck_[1]),
                        (lo[0] + drape_w, lo[1]), (lo[0] - drape_w, lo[1])])
        c.put(drape, hc, "veil", clip=~c.parts_mask("head", "ear", "hair"))
        c.bias[c.parts_mask("veil") & (c.Y < neck_[1] + 1.5)] += 1


def _mask(c, col, P, body, H, cp, sp, nod):
    """A ritual mask over the face: ("full", colour) covers the whole face, ("half", colour) is a domino over the eyes,
    ("animal", kind, colour, accent) is a carved beast's face (see _animal_mask), ("bauta", colour) is the Venetian
    Bauta (see _bauta_mask)."""
    if col["mask"][0] == "animal":
        return _animal_mask(c, col, P, body, H, cp, sp, nod)
    if col["mask"][0] == "bauta":
        return _bauta_mask(c, col, P, body, H, cp, sp, nod)
    style, mc = col["mask"]
    fx, fy, _ = P(body([0, 0.08 + nod, 0.05]))
    hrx = H * HEAD * math.sqrt((0.048 * cp) ** 2 + (0.056 * sp) ** 2)
    frx, fry = max(hrx * (0.62 + 0.25 * abs(cp)), 2.6), H * 0.077 * HEAD * 0.86
    region = c.parts_mask("head")
    ey = P(body([0, 0.074 + nod, 0.056 * HEAD]))[1]
    if style == "half":
        region &= (c.Y > ey - 2.5) & (c.Y < ey + 2.0)
    m = c.put(c.ellipse((fx, fy), frx, fry), mc, "mask", dither=False, cast=False, clip=region)
    if m is None or not m.any():
        return
    # The painted features under the mask disappear; only two dark eye holes show through.
    keep = []
    for x, y, ic in c.ink:
        if 0 <= y < c.h and 0 <= x < c.w and (m[y, x] or (style == "full" and region[y, x])):
            continue
        keep.append((x, y, ic))
    c.ink = keep
    fs = 0 if abs(sp) < 0.12 else (1 if sp > 0 else -1)
    for s in (1, -1):
        if s * 0.4 * sp + 0.92 * cp < 0.1:
            continue
        ex, ey2, _ = P(body([s * 0.022 * HEAD, 0.074 + nod, 0.056 * HEAD]))
        ex = math.floor(ex) - (fs if abs(sp) > 0.85 else 0)
        c.dot(ex, math.floor(ey2), "141016")


def _bauta_mask(c, col, P, body, H, cp, sp, nod):
    """The Venetian Bauta worn as a half-mask: an ivory papier-mache plate over the brow, eyes and nose, cut square
    just under a long ridged nose. The mouth and chin stay bare, lost in the cowl's shadow. In profile the nose
    stands proud of the plate."""
    _, mc = col["mask"]
    K = HEAD

    def S(x, y, z):  # head-relative point (head units: y from the eye line, z forward)
        return P(body([x * K, 0.074 + nod + y * K, z * K]))[:2]

    fx, fy, _ = P(body([0, 0.08 + nod, 0.05]))
    hrx = H * K * math.sqrt((0.048 * cp) ** 2 + (0.056 * sp) ** 2)
    frx, fry = max(hrx * (0.62 + 0.25 * abs(cp)), 2.6), H * 0.077 * K * 0.86
    region = c.parts_mask("head")
    hem = S(0, 0.036, 0.06)[1]  # the plate's square lower edge, just under the nose
    ys, xs = np.nonzero(region | c.ellipse((fx, fy), frx, fry)[0])
    x0, x1, y0, y1 = xs.min() - 2, xs.max() + 2, ys.min() - 1, ys.max() + 2
    c.ink = [(x, y, ic) for x, y, ic in c.ink if not (x0 <= x <= x1 and y0 <= y <= y1)]
    plate = c.put(c.ellipse((fx, fy), frx, fry), mc, "mask", dither=False, cast=False, clip=region & (c.Y < hem))
    if plate is None or not plate.any():
        return
    # the bare skin round the plate, the mouth and chin below it, overshadowed by the plate and the cowl
    c.recolor(c.parts_mask("head", "ear", "neck"), col.get("mask_shadow", "9a7058"), dither=False)
    # the long nose, standing proud of the face down to the plate's edge
    c.put(c.capsule(S(0, -0.014, 0.062), S(0, 0.03, 0.084), 0.8, 1.1), mc, "nose", dither=False, cast=False,
          clip=c.Y < hem + 0.5)
    m = c.parts_mask("mask", "nose")
    ey = S(0, 0, 0.056)[1]
    c.bias[m & (c.Y > ey - 2.2) & (c.Y < ey - 0.6)] -= 1  # the carved brow over the eyes
    c.bias[c.parts_mask("head", "ear", "neck") & ~m & (c.Y >= hem - 1) & (c.Y < hem + 1)] -= 1  # the plate's shadow

    fs = 0 if abs(sp) < 0.12 else (1 if sp > 0 else -1)
    for s in (1, -1):
        if s * 0.4 * sp + 0.92 * cp < 0.1:
            continue
        ex, ey2 = S(s * 0.022, 0.0, 0.056)
        ex = math.floor(ex) - (fs if abs(sp) > 0.85 else 0)
        c.dot(ex, math.floor(ey2), "141016")

def _animal_mask(c, col, P, body, H, cp, sp, nod):
    """A carved wood or bone beast's face after the animals of Celtic folklore: the plate covers the face like the
    white mask, a muzzle or beak juts forward along the facing direction, and ears or antlers rise through the cowl
    so the silhouette names the beast even from behind. col["mask"] = ("animal", kind, plate colour, accent colour),
    kind one of ANIMAL_MASKS."""
    _, kind, mc, ac = col["mask"]
    K = HEAD
    facing = cp > -0.25

    def S(x, y, z):  # head-relative point (head units: y from the eye line, z forward)
        return P(body([x * K, 0.074 + nod + y * K, z * K]))[:2]

    def cap(a, b, ra, rb, colour, part="snout"):
        return c.put(c.capsule(S(*a), S(*b), ra, rb), colour, part, dither=False)

    # ---- ears and antlers, rising through the cowl ----
    for s in (1, -1):
        if kind == "stag":  # branching antlers: a beam sweeping up, out and back, a brow tine and a top tine
            cap((s * 0.03, -0.075, -0.005), (s * 0.06, -0.13, -0.025), 1.1, 0.8, ac, "horn")
            cap((s * 0.06, -0.13, -0.025), (s * 0.085, -0.172, -0.05), 0.8, 0.5, ac, "horn")
            cap((s * 0.06, -0.13, -0.025), (s * 0.034, -0.168, -0.01), 0.7, 0.4, ac, "horn")
            cap((s * 0.042, -0.1, -0.012), (s * 0.08, -0.112, 0.02), 0.7, 0.4, ac, "horn")
            cap((s * 0.045, -0.035, 0.0), (s * 0.08, -0.05, -0.01), 1.0, 0.5, mc, "horn")
        elif kind == "boar":
            cap((s * 0.035, -0.06, 0.0), (s * 0.06, -0.115, -0.01), 1.4, 0.5, mc, "horn")
        elif kind == "wolf":  # tall pointed ears
            c.put(c.poly([S(s * 0.008, -0.065, 0.012), S(s * 0.06, -0.05, -0.02), S(s * 0.047, -0.165, -0.012)]),
                  mc, "horn", dither=False)
            cap((s * 0.036, -0.085, 0.0), (s * 0.042, -0.115, -0.008), 0.5, 0.3, ac, "horn")
        elif kind == "bear":  # small round ears
            c.put(c.ellipse(S(s * 0.046, -0.074, -0.005), 1.9, 1.8), mc, "horn", dither=False)
            c.dot(*S(s * 0.046, -0.074, 0.0), _dark(ac, 1))
        elif kind == "hare":  # long upright ears with a darker inner groove
            cap((s * 0.02, -0.07, -0.005), (s * 0.036, -0.192, -0.02), 1.5, 1.1, mc, "horn")
            cap((s * 0.024, -0.095, 0.0), (s * 0.034, -0.18, -0.014), 0.45, 0.35, ac, "horn")
    if kind == "boar":  # a bristled ridge over the crown
        cap((0, -0.07, 0.01), (0, -0.115, -0.04), 1.3, 0.7, ac, "horn")
    elif kind == "raven":  # a swept-back crest of carved feathers
        cap((0, -0.07, 0.01), (0, -0.13, -0.05), 1.4, 0.5, mc, "horn")
    if not facing:
        return

    # ---- the face plate ----
    fx, fy, _ = P(body([0, 0.08 + nod, 0.05]))
    hrx = H * K * math.sqrt((0.048 * cp) ** 2 + (0.056 * sp) ** 2)
    frx, fry = max(hrx * (0.62 + 0.25 * abs(cp)), 2.6), H * 0.077 * K * 0.86
    region = c.parts_mask("head")
    plate = c.put(c.ellipse((fx, fy), frx, fry), mc, "mask", dither=False, cast=False, clip=region)
    if plate is None or not plate.any():
        return
    c.ink = [(x, y, ic) for x, y, ic in c.ink if not (0 <= y < c.h and 0 <= x < c.w and region[y, x])]
    ey = S(0, 0, 0.056)[1]
    if kind in ("wolf", "boar", "bear"):  # a heavy carved brow over the eye holes
        c.bias[plate & (c.Y > ey - 2.5) & (c.Y < ey - 0.5)] -= 1

    # ---- muzzle, snout or beak ----
    tip = None
    if kind == "stag":
        cap((0, 0.01, 0.06), (0, 0.045, 0.11), 1.6, 1.1, mc)
        tip = (0, 0.045, 0.115)
    elif kind == "boar":
        cap((0, 0.02, 0.06), (0, 0.04, 0.1), 2.0, 2.0, mc)
        cap((0, 0.04, 0.1), (0, 0.04, 0.112), 1.8, 1.8, ac)
        for s in (1, -1):
            if s * 0.4 * sp + 0.92 * cp > 0.1:
                cap((s * 0.014, 0.052, 0.102), (s * 0.022, 0.024, 0.11), 0.6, 0.4, "e8e0cc", "tusk")
        tip = (0, 0.04, 0.116)
    elif kind == "wolf":
        cap((0, 0.01, 0.06), (0, 0.05, 0.125), 1.8, 0.9, mc)
        tip = (0, 0.05, 0.128)
    elif kind == "bear":
        cap((0, 0.02, 0.06), (0, 0.04, 0.098), 2.2, 1.8, mc)
        c.put(c.ellipse(S(0, 0.036, 0.104), 1.1, 0.9), ac, "nose", dither=False)
    elif kind == "raven":  # a long beak hooking down
        cap((0, 0.005, 0.06), (0, 0.04, 0.12), 1.9, 1.2, ac)
        cap((0, 0.04, 0.12), (0, 0.08, 0.15), 1.2, 0.4, ac)
    elif kind == "hare":
        cap((0, 0.03, 0.06), (0, 0.04, 0.086), 1.6, 1.4, mc)
        tip = (0, 0.036, 0.09)
    if tip is not None:
        c.dot(*S(*tip), "141016")

    # ---- the eye holes ----
    fs = 0 if abs(sp) < 0.12 else (1 if sp > 0 else -1)
    for s in (1, -1):
        if s * 0.4 * sp + 0.92 * cp < 0.1:
            continue
        ex, ey2 = S(s * 0.022, 0.0, 0.056)
        ex = math.floor(ex) - (fs if abs(sp) > 0.85 else 0)
        c.dot(ex, math.floor(ey2), "141016")


ANIMAL_MASKS = ("stag", "boar", "wolf", "bear", "raven", "hare")


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
        elif kind == "knot" and cp > 0.05:  # tie knot in the collar, lit on top: (knot, y, colour, highlight)
            _, y, colour, light = d
            kx, ky, _ = P(body([0, y, 0.05]))
            kx, ky = math.floor(kx), math.floor(ky)
            knot = c.parts_mask(*body_parts)
            for ddx, ddy, lit in ((-1, 0, 0), (0, 0, 1), (1, 0, 1), (2, 0, 0), (0, 1, 0), (1, 1, 0)):
                if 0 <= ky + ddy < c.h and 0 <= kx + ddx < c.w and knot[ky + ddy, kx + ddx]:
                    c.dot(kx + ddx, ky + ddy, light if lit else colour)
        elif kind == "pearls" and cp > 0.05:  # a single strand: (pearls, y, colour)
            _, y, colour = d
            for i, u in enumerate((-0.03, -0.015, 0.0, 0.015, 0.03)):
                px, py, _ = P(body([u, y + 0.012 * (1 - (u / 0.03) ** 2), 0.055]))
                if i % 2 == 0 or abs(cp) > 0.7:
                    c.dot(px, py, colour)
        elif kind == "strand" and cp > -0.25:  # a long rope of pearls looping down the chest: (strand, y0, y1, w, colour, shade?)
            _, y0, y1, w, colour = d[:5]
            shade = d[5] if len(d) > 5 else colour
            on = c.parts_mask("torso", "coat")
            last = None
            for i, t in enumerate(np.linspace(-1, 1, 41)):
                px, py, pd = P(body([w * t, y0 + (y1 - y0) * (1 - t * t), 0.06]))
                pos = (math.floor(px), math.floor(py))
                if pos == last:
                    continue
                last = pos
                ix, iy = pos
                if 0 <= iy < c.h and 0 <= ix < c.w and on[iy, ix] and pd > -0.03:
                    c.dot(px, py, colour if i % 2 == 0 else shade)
        elif kind == "pleats":  # knife pleats down the skirt below y: (pleats, y)
            _, y = d
            yb = P(body([0, y, 0]))[1]
            c.bias[c.parts_mask("coat") & (c.Y > yb) & (np.floor(c.X) % 3 == 0)] -= 1
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
        if col.get("front_gaze") and abs(sp) < 0.5:
            # facing the viewer: eyes set evenly either side of the nose, whites outside, pupils looking ahead
            nose_x = pt(0.0, 0.03, 0.072)[0]
            outer = 1 if ex > nose_x or (ex == nose_x and s * fs > 0) else -1
            ex, look = nose_x + 2 * outer, -outer
            if col.get("level_eyes"):  # one shared row, so a slight turn does not tilt the eye line
                ey = pt((1 if sp >= 0 else -1) * 0.022, 0.0, 0.056)[1]  # the near eye's row
        if col.get("asleep"):  # closed lids: just the curved lash line
            lash = _dark(col.get("brow") or col["hair"], 1)
            c.dot(ex, ey, lash)
            c.dot(ex - look, ey, lash)
            c.dot(ex, ey - 3 if female else ey - 2, brow)
            c.dot(ex - look, ey - 3 if female else ey - 2, brow)
            continue
        if col.get("deep_eyes"):
            # deep-set under a heavy, low brow: dark irises with only a sliver of muted white
            if col.get("front_gaze") and abs(sp) < 0.5:
                ex -= outer  # close-set, clear of the cheek outline
            ey += 1  # set below a shaded socket so the iris does not merge into the brow
            c.dot(ex, ey, eye)
            if near or abs(cp) > 0.85:
                c.dot(ex - look, ey, col.get("eye_white", "e6ded4"))
                c.dot(ex - look, ey - 1, tone(2))
            c.dot(ex, ey - 1, tone(2))
            for dx in (-1, 0, 1):
                c.dot(ex + dx, ey - 2, brow)
            continue
        c.dot(ex, ey, eye)
        gaze = col.get("front_gaze") and abs(sp) < 0.5
        wx = ex - look
        if gaze:
            # keep the white on the face: if it would sit on the outline, tuck it inside the iris instead
            head = c.parts_mask("head")
            on = lambda x: 0 <= x < c.w and 0 <= ey < c.h and head[ey, x]
            if not (on(wx) and on(wx - look)):
                wx = ex + look
        if near or abs(cp) > 0.85 or gaze:
            c.dot(wx, ey, col.get("eye_white", "e6ded4"))
        lash = _dark(col.get("brow") or col["hair"], 1) if female else tone(1)
        c.dot(ex, ey - 1, lash)
        if gaze and female:  # the upper lid runs over the white too, so the eye reads as an almond
            c.dot(wx, ey - 1, lash)
        if near and not female:
            c.dot(ex - look, ey - 1, lash)
        if not female:
            c.dot(ex, ey + 1, tone(2))  # lower lid / bag
        by = ey - (3 if female else 2)
        c.dot(ex, by, brow)
        c.dot(ex - look, by + (0 if female else 0), brow)
        if not female and near:
            c.dot(ex + look, by, brow)
        if female and near and not gaze:
            c.dot(ex + (1 if s > 0 else -1) * (1 if fs == 0 else 0), by + 1, brow)
        if col.get("specs"):  # round wire rims round the eye and its white, with a bridge over the nose
            rim = col["specs"]
            x0, x1 = min(ex, ex - look), max(ex, ex - look)
            for x in range(x0, x1 + 1):
                c.dot(x, ey - 1, rim)
                c.dot(x, ey + 1, rim)
            c.dot(x0 - 1, ey, rim)
            c.dot(x1 + 1, ey, rim)

    # ---- nose ----
    nx_, ny_, _ = pt(0.0, 0.03, 0.072)
    if side:
        nx_ -= fs
    if not side:
        if not col.get("deep_eyes"):  # deep-set eyes sit on this row
            c.dot(nx_ + 1, ny_ - 2, tone(2))  # shadow down the right flank (key light from the left)
        c.dot(nx_ + 1, ny_ - 1, tone(2))
        if not col.get("deep_eyes"):
            c.dot(nx_ - 1 if fs >= 0 else nx_, ny_ - 2, tone(4))  # bridge highlight
    c.dot(nx_ + (1 if fs >= 0 else 0), ny_, tone(1))  # nostril / underside
    c.dot(nx_ + (0 if fs >= 0 else 1), ny_ + 1, tone(2))

    # ---- mouth ----
    mx, my, _ = pt(0.0, 0.05, 0.062)
    if col.get("full_jaw") and abs(sp) < 0.65 and not side:
        # the rounded-out far jaw: clean skin from the eye to the chin, without the dark cheek outline, edge shade
        # or neck seam breaking it into stray pixels round the mouth; a soft shade only on its edge and chin
        head, neck = c.parts_mask("head"), c.parts_mask("neck")
        for y in range(pt(0.022, 0.0, 0.056)[1] + 1, c.h - 1):
            xs_ = np.nonzero(head[y])[0]
            if not len(xs_):
                continue
            if y < my:
                if xs_[-1] > mx + 1:
                    c.dot(xs_[-1], y, tone(3))
                continue
            for x in xs_[xs_ >= mx - 2]:
                c.dot(x, y, tone(3) if x == xs_[-1] or not head[y + 1, x] else tone(4))
                for k in (1, 2):  # the throat under the chin: one soft shade, no grey seam
                    yy = y + k
                    if yy < c.h and not head[yy, x] and neck[yy, x] and abs(x - mx) <= 2 and neck[yy, x + 1]:
                        c.dot(x, yy, tone(3))
    if side:
        mx -= fs
    wid = 1 if side else (2 if abs(cp) < 0.7 or not female else 3)
    xs = [mx - (wid // 2) + i for i in range(wid)]
    lip = col.get("lips") or tone(1)
    lip_lo = col.get("lips_lo") or (_dark(lip, 4) if col.get("lips") else tone(2))
    if col.get("mustache"):
        for x in xs + [xs[-1] + 1, xs[0] - 1]:
            c.dot(x, my - 1, _dark(col["hair"], 1))
    if mouth == 0 and col.get("small_lips") and female:  # a neat closed mouth: one row, two pixels at most
        for x in (xs[:2] if not side else xs):
            c.dot(x, my, lip)
    elif mouth == 0:
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
    if not (col.get("full_jaw") and abs(sp) < 0.65 and not side):
        c.dot(mx, my + 3, tone(2))  # chin shadow
    if col.get("stubble"):
        # a few days' growth: a broken stipple on the chin and along the jaw below the mouth
        head = c.parts_mask("head")
        rows = np.nonzero(head.any(1))[0]
        bottom = rows.max() if len(rows) else my + 3
        for y in range(ny_ + 1, bottom + 1):
            xs_ = np.nonzero(head[y])[0] if 0 <= y < c.h else []
            if not len(xs_):
                continue
            edge = {xs_[0], xs_[-1]}
            for x in xs_:
                if fs and (x - mx) * fs < -3:  # the back of the skull, not the jaw
                    continue
                if y <= my:  # above the mouth only the jawline itself
                    if x in edge and y > ny_ + 1:
                        c.dot(x, y, col["stubble"])
                    continue
                if y == my + 1 and x in xs and mouth != 0:  # keep the open mouth clear
                    continue
                if (x + y) % 2 == 0 or y >= bottom or x in edge:
                    c.dot(x, y, col["stubble"])
    if female and not side and not col.get("small_lips"):
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


def grounded_joints(joints, fw=192):
    points = [np.array(p, float) for p in joints]
    shift = np.array([fw / 2 + 2 - points[4][0], 0])
    return [p + shift for p in points]


def _drape_sheet(c, drape, hip, shoulder, knee, ankle, floor=92.0):
    """A bed sheet wrapped from the armpits to the ankles of an articulated (screen-space) figure. It hugs the body,
    and its loose edge hangs straight down under gravity from every part of the body, until it rests on the floor,
    where the hem spreads out a little. The far arm stays under it; the near arm is drawn over it afterwards."""
    col = drape["col"]
    chest = shoulder + (hip - shoulder) * 0.14
    foot = ankle + np.array([3.0, 0.0])
    chain = [(chest, 6.0), (hip, 6.5), (knee, 4.8), (foot, 3.6)]
    hang = drape.get("hang", 12.0)
    curtain = np.zeros((c.h, c.w), bool)
    pooled = []
    for (a, ra), (b, rb) in zip(chain, chain[1:]):
        c.put(c.capsule(a, b, ra, rb), col, "sheet")
        da, db = min(floor, a[1] + hang), min(floor, b[1] + hang)
        pts = [(a[0] - ra * 0.3, a[1]), (b[0] + rb * 0.3, b[1]), (b[0], db), (a[0], da)]
        m = c.put(c.poly(pts, curve=0.3), col, "sheet")
        curtain |= m
        pooled += [p[0] for p, d in ((a, da), (b, db)) if d >= floor - 0.5]
    if pooled:
        x0, x1 = min(pooled) - 5, max(pooled) + 5
        m = c.put(c.poly([(x0, floor + 0.5), (x0 + 3, floor - 3), (x1 - 3, floor - 3), (x1, floor + 0.5)], curve=0.2),
                  col, "sheet")
        curtain |= m
    # Vertical folds where the cloth hangs free, and a darker hem along the floor.
    body = np.zeros_like(curtain)
    for (a, ra), (b, rb) in zip(chain, chain[1:]):
        body |= c.capsule(a, b, ra, rb)[0]
    free = curtain & ~body
    folds = free & (np.floor(c.X).astype(int) % 5 == 0) & (c.Y < floor - 1.5)
    c.bias[folds] -= 1
    c.bias[free & (c.Y > floor - 1.5)] -= 1
    if hip[1] < floor - 12:
        # Upright enough for the cloth to fall free from the hips: a loose bell over the folded legs, spreading on
        # the floor, with folds radiating from the hip.
        tip = min(knee[0], foot[0]) - 4, max(knee[0], foot[0], hip[0]) + 7
        top = hip + (shoulder - hip) * 0.1
        bell = [(top[0] - 6, top[1]), (top[0] + 6, top[1]), (tip[1], floor + 0.5), (tip[0], floor + 0.5)]
        m = c.put(c.poly(bell, curve=0.5), col, "sheet")
        im = Image.new("L", (c.w, c.h), 0)
        d = ImageDraw.Draw(im)
        for k in range(1, 5):
            fx = tip[0] + (tip[1] - tip[0]) * k / 5
            d.line([(top[0] + (k - 2.5) * 2, top[1] + 4), (fx, floor - 1)], fill=255)
        c.bias[m & (np.array(im) > 0)] -= 1
        c.bias[m & (c.Y > floor - 1.5)] -= 1


def _draped_skirt(c, col, waist, hip, knee, across, length, floor=92.5):
    """Coat tails hanging with gravity in an action frame: the front panel lies over the thigh and falls from the knee,
    the back panel drops straight from the seat, and whatever is longer than the drop to the floor pools behind."""
    thigh = knee - hip
    t = thigh / np.linalg.norm(thigh)
    n = max((np.array([-t[1], t[0]]), np.array([t[1], -t[0]])), key=lambda v: v[0] - v[1])  # the knee's top/front
    length *= 1 + 0.45 * t[0] ** 2  # the lower the knee, the more cloth reaches the floor
    seat = hip - across * 6
    drop = seat[1] + length
    pool = max(0.0, drop - floor)
    back_low = np.array([seat[0] - 1, min(drop, floor)])
    tip = back_low + (-min(pool * 2, 6), 0)
    over = knee + n * 3.5
    front = knee + t * 3 + n
    front_hem = np.array([front[0] + 0.5, min(floor, max(front[1], knee[1]) + min(7.0, max(2.5, length - np.linalg.norm(thigh))))])
    sag = (front_hem + back_low) / 2 + (0, 2)
    sag[1] = min(sag[1], floor)
    pts = [waist - across * 5, seat, back_low, tip, sag, front_hem, front, over, waist + across * 5]
    m = c.put(c.poly(pts), col, "coat")
    for a, b in ((hip + (-2, 3), (back_low + tip) / 2 + (1, -1)), (hip + (1, 4), sag + (0, -1)),
                 (knee + (-1, 2), front_hem + (-1, -1))):  # folds running down to the hem
        c.bias[m & c.capsule(np.array(a, float), np.array(b, float), 0.5, 0.6)[0]] -= 1


def action_figure(spec, joints, fw=192, fh=96, chest_down=False, coat_drape=False, plain_chest=False, head_sprite=None,
                  toes_tucked=False):
    """Articulated screen-space pose. Contact points stay fixed; limbs, clothes and the head are painted separately.
    chest_down: the trunk is bent over the floor (hands and knees), so the shirt front and tie face the ground and are
    hidden behind the coat's flank instead of being drawn along the spine, and the coat skirt hangs from the hips.
    joints may carry four more points, the far leg's knee, ankle, heel and toe (otherwise it shadows the near one).
    coat_drape: the coat skirt hangs with gravity, over the thigh and down to the floor, instead of following the thigh.
    plain_chest: no shirt or tie along the trunk and the collar in the coat's colour, for a profile seen low down.
    head_sprite: (image, neck point) of ready-made head art pasted upright on the neck instead of painting the head;
    the shoulder and collar are then one rounded mass of coat.
    toes_tucked: kneeling with the shins raised off the floor behind, so the feet stand upright on their tucked toes
    (heel up, sole facing back) instead of lying along the shin."""
    H = spec["h"]
    c = Canvas(fw, fh)
    # Keep the weight-bearing ankle fixed across the entire sequence, with space for a body lying to its left.
    points = grounded_joints(joints, fw)
    hip, shoulder, head, knee, ankle, elbow, hand = points[:7]
    far_leg = points[7:11] if len(points) >= 11 else None
    up = shoulder - hip
    up /= np.linalg.norm(up)
    across = np.array([-up[1], up[0]])
    torso, skin = spec["torso"], spec["skin"]
    pants = spec.get("pants", torso)
    if head_sprite is not None or chest_down:  # the coat shoulder and the upper sleeve shade as one mass, no seam
        c.blend_parts = ("torso", "arm", "collar")
        along = elbow - shoulder
        t = ((c.X - shoulder[0]) * along[0] + (c.Y - shoulder[1]) * along[1]) / max(along @ along, 1e-6)
        c.blend_zone = c.capsule(shoulder + up * 3, elbow, 7, 5)[0]
        c.blend_w = np.clip(1.2 - t, 0, 1)

    def limb(a, b, ra, rb, col, part):
        c.put(c.capsule(a, b, ra, rb), col, part, dither=col != skin)

    ak = spec.get("arm_r", 1.0)
    for far in (True, False):
        off = np.array([-3, -2]) if far else np.zeros(2)
        part = "farleg" if far else "leg"
        if far and far_leg is not None:
            fknee, fankle, fheel, ftoe = far_leg
            limb(hip + off, fknee, 4.3, 3.1, pants, part)
            limb(fknee, fankle, 3.1, 2.4, pants, part)
            limb(fheel, ftoe, 2, 1.5, spec["shoes"], part)
        else:
            limb(hip + off, knee + off, 4.3, 3.1, pants, part)
            limb(knee + off, ankle + off, 3.1, 2.4, pants, part)
            if toes_tucked:
                limb(ankle + off + (-2, -2), np.array([ankle[0] + off[0] - 1, 91.0]), 2, 1.5, spec["shoes"], part)
            else:
                limb(ankle + off + (-2, -1), ankle + off + (5, 0), 2, 1.5, spec["shoes"], part)
        if far:
            limb(shoulder + off, elbow + off, 3 * ak, 2.5 * ak, spec.get("sleeves", torso), "fararm")
            limb(elbow + off, hand + off, 2.5 * ak, 2 * ak, spec.get("sleeves", torso), "fararm")
    waist = hip + up * 10
    limb(hip, waist, 6, 5, torso, "torso")
    limb(waist, shoulder, 5, 6, torso, "torso")
    drape = spec.get("drape")
    if drape:
        _drape_sheet(c, drape, hip, shoulder, knee, ankle)
    coat = None if drape else spec.get("coat")
    if coat:
        tail = hip + (knee - hip) * min(1, (coat["hem"] - 0.5) / 0.24)
        if coat_drape:
            _draped_skirt(c, coat["col"], waist, hip, knee, across, np.linalg.norm(tail - hip))
        else:
            if chest_down:
                # The skirt wraps the upright thigh and its front panel hangs under the belly, rather than being
                # spread across the trunk's axis (a sliver down the thigh).
                back = np.array([-(tail - hip)[1], (tail - hip)[0]]) / np.linalg.norm(tail - hip)
                back = back if back @ up < 0 else -back
                pts = [waist - across * 5, hip + back * 6, tail + back * 5, tail - back * 4, waist + across * 5]
            else:
                pts = [waist - across * 5, hip - across * 6, tail - across * 5,
                       tail + across * 5, hip + across * 6, waist + across * 5]
            c.put(c.poly(pts), coat["col"], "coat")
    # Shirt opening and tie follow the trunk, not the screen's vertical axis.
    if not spec.get("cloak") and not chest_down and not drape and not plain_chest:
        shirt = shoulder - up * 5
        limb(shoulder, shirt, 2, 1.4, "e3d7bf", "shirt")
        tie = next((d[5] for d in spec.get("decals", []) if d[0] == "strip" and d[3] == 0.007), None)
        if tie:
            limb(shoulder - up * 2, shoulder - up * 9, 0.7, 0.6, tie, "tie")
    hk = max(ak, 0.7)
    limb(shoulder + across * (0 if chest_down else 2), elbow, 3.2 * ak, 2.7 * ak, spec.get("sleeves", torso), "arm")
    limb(elbow, hand - (hand - elbow) * 0.12, 2.7 * ak, 2 * ak, spec.get("sleeves", torso), "arm")
    limb(hand - (hand - elbow) * 0.12, hand, 2 * hk, 1.7 * hk, skin, "hand")
    if spec.get("cloak"):
        points = [shoulder - across * 8, hip - across * 10, knee - across * 6,
                  ankle + (3, 0), knee + across * 7, hip + across * 10, shoulder + across * 8]
        m = c.put(c.poly(points, curve=0.6), spec["cloak"]["col"], "cloak")
        seam = c.capsule(shoulder, hip + (knee - hip) * 0.6, 0.6, 0.8)[0]
        c.bias[m & seam] += 1
    head_axis = head - shoulder
    if head_sprite is not None:  # one rounded mass of coat over the shoulder and up round the neck
        neck = shoulder + head_axis * 0.3
        ang = math.atan2(across[1], across[0])
        c.put(c.ellipse(shoulder + across * 0.5 + head_axis * 0.05, 5.6, 4.6, ang), torso, "torso")
        c.put(c.capsule(shoulder, neck + (0, 1), 3.2, 2.6), torso, "torso")
    elif plain_chest:  # the coat's collar turned up round the neck, then a little skin under the jaw
        neck = shoulder + head_axis * 0.5
        limb(shoulder, shoulder + head_axis * 0.3, 2.6, 2.3, torso, "collar")
        limb(shoulder + head_axis * 0.3, neck, 1.8, 1.6, skin, "neck")
    elif coat and abs(head_axis[0]) > abs(head_axis[1]):
        neck = shoulder + head_axis * 0.55
        # bent over the floor the shirt collar faces the ground, so only the coat's shows
        limb(shoulder, neck, 2.3, 2, torso if chest_down else spec.get("collar", torso), "collar")
        limb(neck, shoulder + head_axis * 0.75, 1.7, 1.5, skin, "neck")
    else:
        neck = shoulder + head_axis * 0.25
        limb(shoulder, neck, 2.3, 2, skin, "neck")
    img = c.render(shadow_box=((fw / 2, 94), 36, 1.2))
    if head_sprite is not None:
        art, (bx, by) = head_sprite
        img.alpha_composite(art, (round(neck[0] - bx), round(neck[1] - by)))
        return img, tuple(head)
    # The screen-space head painter retains each character's hat, hair and mask.
    hc = Canvas(64, 64)
    phi = math.radians(80)
    cp, sp = math.cos(phi), math.sin(phi)

    def P(p):
        x, y, z = p
        return (32 + (-x * cp + z * sp) * H, 40 + (y - 0.2) * H + (x * sp + z * cp) * H * PITCH, 0)
    ident = lambda p: np.array(p, float)
    _head(hc, spec, P, ident, H, cp, sp, 0)
    if spec.get("hair_style") == "long":
        _long_hair_back(hc, spec, P, ident, H, cp, sp, 0)
    _face(hc, spec, P, ident, H, cp, sp, 0, 0)
    if spec.get("mask"):
        _mask(hc, spec, P, ident, H, cp, sp, 0)
    hp = np.array(P([0, 0.074, 0.008])[:2])
    direction = head - neck
    angle = math.degrees(math.atan2(direction[0], -direction[1]))
    lt = math.radians(angle)
    light = np.array([math.cos(lt) * LIGHT[0] + math.sin(lt) * LIGHT[1],
                      -math.sin(lt) * LIGHT[0] + math.cos(lt) * LIGHT[1], LIGHT[2]])
    painted = hc.render(light=light).rotate(-angle, resample=Image.Resampling.NEAREST,
                                           center=tuple(hp))
    img.alpha_composite(painted, (round(head[0] - hp[0]), round(head[1] - hp[1])))
    return img, tuple(head)

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
        k, hk = col.get("arm_r", 1.0), max(col.get("arm_r", 1.0), 0.7)
        c.put(c.capsule(P(sh), P(el), H * 0.034 * BULK * k, H * 0.031 * BULK * k), sleeve, part)
        c.put(c.capsule(P(el), P(wr), H * 0.031 * BULK * k, H * 0.027 * BULK * k), fore, part)
        if col.get("cuff") and fore != skin:
            c.put(c.capsule(P(wr), P(wr), H * 0.026 * hk, H * 0.026 * hk), col["cuff"], part)
        c.put(c.capsule(P(wr), P(hand), H * 0.027 * hk, H * 0.024 * hk), skin, f"hand{s}", dither=False)

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
