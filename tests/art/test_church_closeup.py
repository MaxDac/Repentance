"""The two-portrait close-up in the cathedral: Micah on the left, cut out of his fire-escape picture and stood in
front of the nave from Caleb's picture, Caleb on the right in his collar. A shorter panel than the others, so each
speaker's line fits in a strip below his half."""
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


def warmth(px):
    return px[..., 0].mean() - px[..., 2].mean()


class ChurchCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.caleb = Image.open(closeup.CALEB_SRC)
        cls.micah = closeup.church_micah(Image.open(closeup.MICAH_SRC), Image.open(closeup.MICAH_MASK), cls.caleb,
                                         Image.open(closeup.CALEB_MASK))
        cls.panel = closeup.church_closeup(cls.micah, cls.caleb)

    def test_committed_source_and_panel_match_the_build(self):
        source = Image.open(closeup.CHURCH_MICAH_SRC).convert("RGB")
        self.assertTrue((np.asarray(source) == np.asarray(self.micah)).all(), "regenerate with gen_art.py closeup")
        committed = Image.open(UI / "church_closeup.png").convert("RGB")
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_a_new_picture_leaves_the_fire_escape_one_alone(self):
        self.assertNotEqual(Path(closeup.CHURCH_MICAH_SRC).name, Path(closeup.MICAH_SRC).name)
        self.assertEqual(Image.open(closeup.MICAH_SRC).size, self.micah.size)
        fire_escape = np.asarray(Image.open(UI / "fire_escape_closeup.png").convert("RGB"))
        rebuilt = closeup.fire_escape_closeup(Image.open(closeup.MICAH_SRC), Image.open(closeup.ELEANOR_SRC))
        self.assertTrue((fire_escape == np.asarray(rebuilt)).all())

    def test_as_wide_as_the_others_but_shorter_leaving_a_caption_strip(self):
        w, h = self.panel.size
        self.assertEqual(w, closeup.PW)
        self.assertEqual(h, closeup.CHURCH_AH * closeup.SCALE + 2 * F)
        self.assertLessEqual(h, 270 - 100, "room for seven caption lines below")

    def test_faces_are_matched(self):
        caleb_ch = 896 / closeup.CHURCH_CALEB_ZOOM
        micah_ch = 768 / closeup.CHURCH_MICAH_ZOOM
        caleb_face = (closeup.CALEB_FACE_W * closeup.CALEB_FACE_H) ** 0.5 / caleb_ch
        micah_face = (closeup.MICAH_FACE_W * closeup.MICAH_FACE_H) ** 0.5 / micah_ch
        self.assertAlmostEqual(caleb_face, micah_face, delta=0.005)

    def test_frame_bar_and_chunky_pixels(self):
        a = np.asarray(self.panel, dtype=float)
        self.assertLess(np.asarray(self.panel.convert("L"), dtype=float)[0, :].mean(), 40)
        self.assertLess(a[F:-F, BAR_X:BAR_X + BAR_W].mean(), 70, "a dark bar")
        self.assertLessEqual(abs((BAR_X + BAR_W / 2) - closeup.PW / 2), 1, "centred")
        p = np.asarray(self.panel)
        for half in (p[F:-F, F:BAR_X], p[F:-F, BAR_X + BAR_W:-F]):
            self.assertTrue((half[0::2] == half[1::2]).all() and (half[:, 0::2] == half[:, 1::2]).all())

    def test_one_limited_palette_for_both(self):
        left, right = halves(self.panel)
        colours = {tuple(c) for c in np.concatenate([left.reshape(-1, 3), right.reshape(-1, 3)])}
        self.assertLessEqual(len(colours), closeup.COLOURS)

    def test_micah_on_the_left_in_his_coat_in_front_of_warm_brick(self):
        left, _ = halves(self.panel)
        coat = left[64:, 5:25]
        self.assertGreater(coat[..., 1].mean(), coat[..., 2].mean() + 25, "the yellow trench coat")
        wall = np.concatenate([left[20:50, :8], left[20:50, -8:]])
        self.assertGreater(warmth(wall), 50, "candlelit brick behind him, not the blue night street")

    def test_caleb_on_the_right_in_black_with_a_white_collar(self):
        _, right = halves(self.panel)
        cassock = np.concatenate([right[66:, 8:30], right[66:, -30:-8]])
        self.assertLess(cassock.mean(), 70, "the black cassock")
        collar = right[66:74, 48:60]
        self.assertGreater(collar.max(axis=2).max(), 200, "the white tab of his collar")


if __name__ == "__main__":
    unittest.main()
