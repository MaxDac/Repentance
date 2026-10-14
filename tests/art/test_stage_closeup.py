"""The framed close-ups (Eleanor on the Club's stage, Micah on the cathedral steps), reduced to VGA panels from the committed pictures."""
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


class StageCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nude = closeup.stage_closeup(Image.open(closeup.SRC))
        cls.clothed = closeup.stage_closeup(Image.open(closeup.CLOTHED_SRC))

    def test_committed_panels_match_the_build_and_fit_the_screen(self):
        # nearly the whole 480x270 screen, with the room still showing around it
        self.assertTrue(480 - 60 <= closeup.PW <= 480 - 20)
        self.assertTrue(270 - 60 <= closeup.PH <= 270 - 20)
        for name, panel in (("stage_closeup", self.nude), ("stage_closeup_clothed", self.clothed)):
            with self.subTest(name=name):
                committed = Image.open(UI / f"{name}.png").convert("RGB")
                self.assertEqual(committed.size, (closeup.PW, closeup.PH))
                self.assertTrue((np.asarray(committed) == np.asarray(panel)).all(), "regenerate with gen_art.py closeup")

    def test_frame_is_a_dark_border(self):
        a = np.asarray(self.nude.convert("L"), dtype=float)
        self.assertLess(a[0, :].mean(), 40)
        self.assertLess(a[:, 0].mean(), 40)
        self.assertLess(a[closeup.FRAME - 1, closeup.FRAME:-closeup.FRAME].mean(), 40)

    def test_chunky_pixels(self):
        a = np.asarray(self.nude)[closeup.FRAME:-closeup.FRAME, closeup.FRAME:-closeup.FRAME]
        self.assertTrue((a[0::2] == a[1::2]).all() and (a[:, 0::2] == a[:, 1::2]).all())

    def test_limited_palette(self):
        for panel in (self.nude, self.clothed):
            self.assertLessEqual(len(inner(panel).getcolors(4096)), closeup.COLOURS)

    def test_her_face_is_lit_in_the_middle_over_the_darker_men(self):
        a = np.asarray(inner(self.nude), dtype=float)
        face = a[41:64, 101:119]
        r, g, b = face[..., 0].mean(), face[..., 1].mean(), face[..., 2].mean()
        self.assertTrue(r > g > b and r > 150, "warm skin tones")
        self.assertGreater(face.mean(), a[92:, :37].mean() * 2)

    def test_clothed_only_dresses_her_chest(self):
        a = np.asarray(inner(self.nude), dtype=int)
        c = np.asarray(inner(self.clothed), dtype=int)
        ys, xs = np.nonzero((a != c).any(-1))
        self.assertGreater(len(ys), 400)
        self.assertGreater(ys.min(), 78)  # below the collarbones
        self.assertTrue(64 < xs.min() and xs.max() < 160)  # not on the men
        for x0, x1 in ((70, 80), (143, 153)):  # her sides, either side of the locks of hair
            side = c[101:, x0:x1]
            self.assertGreater(side[..., 0].mean(), side[..., 1].mean() * 2, "dark red velvet")

    def test_her_hair_covers_her_breasts(self):
        a = np.asarray(inner(self.nude), dtype=float)
        c = np.asarray(inner(self.clothed), dtype=float)
        for x0, x1 in ((88, 100), (122, 135)):  # one long lock over each breast, in both variants
            with self.subTest(x=x0):
                self.assertLess(a[95:, x0:x1].mean(), 40)
                self.assertLess(c[95:, x0:x1].mean(), 40)


class BeatenCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = closeup.beaten_closeup(Image.open(closeup.BEATEN_SRC))

    def test_committed_panel_matches_the_build_and_the_stage_panel_size(self):
        committed = Image.open(UI / "beaten_closeup.png").convert("RGB")
        self.assertEqual(committed.size, (closeup.PW, closeup.PH))
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_framed_chunky_and_limited(self):
        a = np.asarray(self.panel)
        self.assertLess(a[0, :].mean(), 40)
        b = a[closeup.FRAME:-closeup.FRAME, closeup.FRAME:-closeup.FRAME]
        self.assertTrue((b[0::2] == b[1::2]).all() and (b[:, 0::2] == b[:, 1::2]).all())
        self.assertLessEqual(len(inner(self.panel).getcolors(4096)), closeup.COLOURS)

    def test_his_face_is_lit_in_the_middle_above_the_yellow_coat(self):
        a = np.asarray(inner(self.panel), dtype=float)
        face = a[30:55, 98:122]
        self.assertTrue(face[..., 0].mean() > face[..., 2].mean() + 30, "warm skin")
        coat = a[95:, 30:70]
        self.assertTrue(coat[..., 0].mean() > 120 and coat[..., 1].mean() > 90 and coat[..., 2].mean() < 70, "yellow trench coat")
        stones = a[:60, :25]
        self.assertLess(stones.mean(), face.mean())


if __name__ == "__main__":
    unittest.main()
