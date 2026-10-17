"""The framed close-up of the red neon MOTEL sign over the wet street, reduced to a VGA panel from the committed
picture."""
from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import closeup

UI = ROOT / "assets" / "art" / "ui"


def inner(panel):
    """The picture in art pixels (each one is SCALE x SCALE on screen)."""
    box = panel.crop((closeup.FRAME, closeup.FRAME, closeup.PW - closeup.FRAME, closeup.PH - closeup.FRAME))
    return box.resize((closeup.AW, closeup.AH), Image.NEAREST)


class MotelCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = closeup.motel_closeup(Image.open(closeup.MOTEL_SRC))

    def test_committed_panel_matches_the_build_and_is_the_same_size_as_the_others(self):
        with Image.open(UI / "motel_closeup.png") as image:
            committed = image.convert("RGB")
        self.assertEqual(committed.size, (closeup.PW, closeup.PH))
        with Image.open(UI / "rose_closeup.png") as rose:
            self.assertEqual(self.panel.size, rose.size)
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_crop_keeps_the_panel_aspect(self):
        w, h = closeup.motel_crop(Image.open(closeup.MOTEL_SRC)).size
        self.assertAlmostEqual(w / h, closeup.AW / closeup.AH, delta=0.01)

    def test_frame_is_a_dark_border(self):
        a = np.asarray(self.panel.convert("L"), dtype=float)
        self.assertLess(a[0, :].mean(), 40)
        self.assertLess(a[:, 0].mean(), 40)
        self.assertLess(a[closeup.FRAME - 1, closeup.FRAME:-closeup.FRAME].mean(), 40)

    def test_chunky_pixels(self):
        a = np.asarray(self.panel)[closeup.FRAME:-closeup.FRAME, closeup.FRAME:-closeup.FRAME]
        self.assertTrue((a[0::2] == a[1::2]).all() and (a[:, 0::2] == a[:, 1::2]).all())

    def test_limited_palette(self):
        self.assertLessEqual(len(inner(self.panel).getcolors(4096)), closeup.COLOURS)

    def test_the_neon_sign_glows_red_at_the_top_right_over_a_dark_street(self):
        a = np.asarray(inner(self.panel), dtype=float)
        x0, y0, x1, y1 = closeup.MOTEL_SIGN
        sign = a[y0:y1, x0:x1]
        r, g, b = sign[..., 0], sign[..., 1], sign[..., 2]
        neon = (r > 170) & (r > g * 1.4) & (r > b * 1.6)
        self.assertGreater(neon.mean(), 0.08, "bright red neon letters")
        self.assertGreater(r.mean(), g.mean() * 1.3)
        self.assertLess(a[:, :, :].mean(), 90, "a night scene")
        self.assertGreater(sign.mean(), a[:, :closeup.AW // 3].mean())


if __name__ == "__main__":
    unittest.main()
