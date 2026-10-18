"""The two-portrait close-up outside the convent: Micah on the left, Eleanor on the right, in one framed VGA panel."""
from pathlib import Path
import sys
import unittest
import unittest.mock
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import closeup

UI = ROOT / "assets" / "art" / "ui"
F = closeup.FRAME
BAR_X = F + closeup.HALF * closeup.SCALE  # first screen column of the centre bar
BAR_W = closeup.BAR * closeup.SCALE


def halves(panel):
    """Each portrait in art pixels."""
    a = np.asarray(panel)
    s = closeup.SCALE
    left = a[F:-F, F:BAR_X][::s, ::s]
    right = a[F:-F, BAR_X + BAR_W:-F][::s, ::s]
    return left.astype(float), right.astype(float)


class ConventCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = closeup.convent_closeup(Image.open(closeup.MICAH_SRC), Image.open(closeup.ELEANOR_SRC))

    def test_committed_panel_matches_the_build_and_is_the_same_size_as_the_others(self):
        committed = Image.open(UI / "convent_closeup.png").convert("RGB")
        self.assertEqual(committed.size, (closeup.PW, closeup.PH))
        self.assertEqual(self.panel.size, Image.open(UI / "stage_closeup.png").size)
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_portrait_crop_keeps_the_half_aspect(self):
        w, h = closeup.portrait_crop(Image.open(closeup.MICAH_SRC), closeup.MICAH_FACE_X).size
        self.assertAlmostEqual(w / h, closeup.HALF / closeup.AH, delta=0.01)
        self.assertEqual(h, 768)

    def test_micah_is_zoomed_so_his_face_matches_eleanors(self):
        z = closeup.MICAH_ZOOM
        self.assertAlmostEqual(closeup.MICAH_FACE_W * closeup.MICAH_FACE_H * z * z,
                               closeup.ELEANOR_FACE_W * closeup.ELEANOR_FACE_H, delta=1)
        w, h = closeup.portrait_crop(Image.open(closeup.MICAH_SRC), closeup.MICAH_FACE_X, z,
                                     closeup.MICAH_EYES_Y, closeup.ELEANOR_EYES_Y).size
        self.assertAlmostEqual(w / h, closeup.HALF / closeup.AH, delta=0.01)
        self.assertEqual(h, round(768 / z))

    def test_frame_is_a_dark_border(self):
        a = np.asarray(self.panel.convert("L"), dtype=float)
        self.assertLess(a[0, :].mean(), 40)
        self.assertLess(a[:, 0].mean(), 40)
        self.assertLess(a[F - 1, F:-F].mean(), 40)

    def test_a_framed_bar_splits_the_two_portraits_down_the_middle(self):
        a = np.asarray(self.panel, dtype=float)
        bar = a[F:-F, BAR_X:BAR_X + BAR_W]
        self.assertLess(bar.mean(), 70, "a dark bar")
        self.assertLessEqual(abs((BAR_X + BAR_W / 2) - closeup.PW / 2), 1, "centred")
        gold = a[F:-F, BAR_X + 2]
        self.assertTrue((gold == gold[0]).all() and gold[0, 0] > gold[0, 2], "a gold line like the frame's")

    def test_chunky_pixels_in_each_half(self):
        a = np.asarray(self.panel)
        for half in (a[F:-F, F:BAR_X], a[F:-F, BAR_X + BAR_W:-F]):
            self.assertTrue((half[0::2] == half[1::2]).all() and (half[:, 0::2] == half[:, 1::2]).all())

    def test_one_limited_palette_for_both(self):
        left, right = halves(self.panel)
        colours = {tuple(c) for c in np.concatenate([left.reshape(-1, 3), right.reshape(-1, 3)])}
        self.assertLessEqual(len(colours), closeup.COLOURS)

    def test_a_small_red_cut_crosses_micahs_bottom_lip(self):
        source = Image.open(closeup.MICAH_SRC)
        cut, _ = closeup.lip_cut(source.size, *closeup.MICAH_CUT)
        (top, left), (bottom, right) = (lambda p: (p.min(axis=0), p.max(axis=0)))(np.argwhere(np.asarray(cut)))
        self.assertLessEqual(bottom - top, 40, "a short cut, not a gash")
        self.assertLessEqual(right - left, 25, "a thin line")
        self.assertTrue(abs(top - 400) <= 6 and closeup.MICAH_FACE_X - 40 < left < closeup.MICAH_FACE_X,
                        "from the mouth line, just off centre")
        with unittest.mock.patch.object(closeup, "stamp_cut", lambda art, _: art):
            plain = closeup.convent_closeup(source, Image.open(closeup.ELEANOR_SRC))
        a, p = np.asarray(self.panel), np.asarray(plain)
        diff = (a != p).any(axis=2)
        self.assertFalse(diff[:, BAR_X:].any(), "Eleanor is untouched")
        self.assertTrue(diff.any(), "the cut survives the reduction")
        self.assertLess(diff.sum(), 200, "and stays small in the panel")
        reds = {tuple(c) for c in a[diff]}
        self.assertLessEqual(reds, {closeup.CUT, closeup.CUT_EDGE}, "only the cut's own reds change")
        self.assertIn(closeup.CUT, reds, "fresh red, not a pale line")

    def test_micah_on_the_left_in_his_yellow_coat(self):
        left, _ = halves(self.panel)
        coat = left[95:, 10:30]
        r, g, b = coat[..., 0].mean(), coat[..., 1].mean(), coat[..., 2].mean()
        self.assertTrue(r > b + 40 and g > b + 30, "the yellow trench coat at the bottom left")
        face = left[45:75, 40:68]
        self.assertTrue(face[..., 0].mean() > face[..., 2].mean() + 30, "a warm face in the middle")

    def test_eleanor_on_the_right_face_lit_over_a_black_turtleneck(self):
        _, right = halves(self.panel)
        face = right[30:65, 40:68]
        self.assertTrue(face[..., 0].mean() > face[..., 2].mean() + 30 and face.mean() > 90, "a warm face")
        neck = right[100:, 35:45]
        self.assertLess(neck.mean(), 45, "a black turtleneck below")
        self.assertGreater(face.mean(), right[:, :8].mean() * 2, "lit against the dark")


if __name__ == "__main__":
    unittest.main()
