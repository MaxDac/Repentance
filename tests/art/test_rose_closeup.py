"""The two-portrait close-up at Rose's door: Rose calling Micah back on the left, Micah on the right, in one framed
VGA panel built like the convent one."""
from pathlib import Path
import sys
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import closeup

UI = ROOT / "assets" / "art" / "ui"
F = closeup.FRAME
BAR_X = F + closeup.HALF * closeup.SCALE
BAR_W = closeup.BAR * closeup.SCALE


def halves(panel):
    """Each portrait in art pixels."""
    a = np.asarray(panel)
    s = closeup.SCALE
    return a[F:-F, F:BAR_X][::s, ::s].astype(float), a[F:-F, BAR_X + BAR_W:-F][::s, ::s].astype(float)


class RoseCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = closeup.rose_closeup(Image.open(closeup.ROSE_SRC), Image.open(closeup.MICAH_SRC))

    def test_committed_panel_matches_the_build_and_is_the_same_size_as_eleanors(self):
        committed = Image.open(UI / "rose_closeup.png").convert("RGB")
        self.assertEqual(committed.size, (closeup.PW, closeup.PH))
        self.assertEqual(self.panel.size, Image.open(UI / "stage_closeup.png").size)
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_micah_is_zoomed_so_his_face_matches_roses(self):
        z = closeup.ROSE_MICAH_ZOOM
        self.assertAlmostEqual(closeup.MICAH_FACE_W * closeup.MICAH_FACE_H * z * z,
                               closeup.ROSE_FACE_W * closeup.ROSE_FACE_H, delta=1)
        w, h = closeup.portrait_crop(Image.open(closeup.ROSE_SRC), closeup.ROSE_FACE_X).size
        self.assertAlmostEqual(w / h, closeup.HALF / closeup.AH, delta=0.01)

    def test_frame_is_a_dark_border(self):
        a = np.asarray(self.panel.convert("L"), dtype=float)
        self.assertLess(a[0, :].mean(), 40)
        self.assertLess(a[:, 0].mean(), 40)
        self.assertLess(a[F - 1, F:-F].mean(), 40)

    def test_a_framed_bar_splits_the_two_portraits_down_the_middle(self):
        a = np.asarray(self.panel, dtype=float)
        self.assertLess(a[F:-F, BAR_X:BAR_X + BAR_W].mean(), 70, "a dark bar")
        self.assertLessEqual(abs((BAR_X + BAR_W / 2) - closeup.PW / 2), 1, "centred")

    def test_chunky_pixels_in_each_half(self):
        a = np.asarray(self.panel)
        for half in (a[F:-F, F:BAR_X], a[F:-F, BAR_X + BAR_W:-F]):
            self.assertTrue((half[0::2] == half[1::2]).all() and (half[:, 0::2] == half[:, 1::2]).all())

    def test_one_limited_palette_for_both(self):
        left, right = halves(self.panel)
        colours = {tuple(c) for c in np.concatenate([left.reshape(-1, 3), right.reshape(-1, 3)])}
        self.assertLessEqual(len(colours), closeup.COLOURS)

    def test_rose_on_the_left_warm_face_over_a_white_blouse(self):
        left, _ = halves(self.panel)
        face = left[45:75, 40:68]
        r, g, b = face[..., 0].mean(), face[..., 1].mean(), face[..., 2].mean()
        self.assertTrue(r > g > b and r > 150, "warm skin tones")
        blouse = left[100:, 30:70]
        self.assertGreater(blouse.mean(), 150, "a light blouse below")

    def test_micah_on_the_right_in_his_yellow_coat(self):
        _, right = halves(self.panel)
        coat = right[95:, 10:30]
        r, g, b = coat[..., 0].mean(), coat[..., 1].mean(), coat[..., 2].mean()
        self.assertTrue(r > b + 40 and g > b + 30, "the yellow trench coat at the bottom left of his half")


if __name__ == "__main__":
    unittest.main()
