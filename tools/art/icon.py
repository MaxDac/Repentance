"""The game icon: a white pixel-art cross fading into a black ground, for the window, the Windows .exe and the
Linux desktop entry."""
import os

import numpy as np
from PIL import Image

from . import common
from .common import save

N = 32
SIZES = (16, 32, 48, 64, 128, 256)
LEVELS = np.array([0, 0.06, 0.14, 0.26, 0.42, 0.62, 0.8, 1.0])


def master():
    """The 32x32 cross: 3 px arms, white at the head greying to the foot, with a stepped glow in the black."""
    yy, xx = np.mgrid[0:N, 0:N].astype(float) + 0.5
    c = N / 2
    arm = 1.5
    cross = ((np.abs(xx - c) <= arm) & (yy >= 6) & (yy <= N - 5)) | \
        ((np.abs(yy - 12) <= arm) & (xx >= 10) & (xx <= N - 10))
    pts = np.argwhere(cross) + 0.5
    dist = np.min(np.hypot(yy[..., None] - pts[:, 0], xx[..., None] - pts[:, 1]), -1)
    glow = np.exp(-dist / 2.2) * 0.45
    shade = np.clip(1.0 - (yy - 6) / (N - 11) * 0.4, 0.6, 1.0)
    val = np.where(cross, shade, glow)
    g = (LEVELS[np.abs(val[..., None] - LEVELS).argmin(-1)] * 255).astype("uint8")
    return Image.fromarray(np.stack([g, g, g], -1), "RGB")


def sized(img, size):
    return img.resize((size, size), Image.Resampling.NEAREST)


def build(dist=None):
    dist = dist or os.path.join(common.ROOT, "dist", "linux")
    img = master()
    save(sized(img, 256), "ui", "icon.png")
    frames = [sized(img, s).convert("RGBA") for s in SIZES]
    ico = os.path.join(common.ART, "ui", "icon.ico")
    frames[-1].save(ico, sizes=[(s, s) for s in SIZES], append_images=frames[:-1])
    print("wrote", os.path.relpath(ico, common.ROOT))
    for s in SIZES:
        path = os.path.join(dist, "icons", "hicolor", f"{s}x{s}", "apps", "repentance.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sized(img, s).save(path)
        print("wrote", os.path.relpath(path, common.ROOT))
