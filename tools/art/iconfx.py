"""Flat-icon shading and outlining shared by inventory and UI art."""
from .common import mul

LIGHT, LIGHT_BAND, DARK, DARK_BAND, BOTTOM = 1.16, 1.07, 0.72, 0.86, 0.92


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

