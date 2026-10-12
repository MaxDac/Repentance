"""The framed close-up of Eleanor on the Club's stage, reduced to a VGA panel from the committed picture."""
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
        src = Image.open(closeup.SRC)
        cls.nude = closeup.stage_closeup(src, clothed=False)
        cls.clothed = closeup.stage_closeup(src, clothed=True)

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
        chest = c[101:, 92:128]
        self.assertGreater(chest[..., 0].mean(), chest[..., 1].mean() * 2, "dark red velvet")


if __name__ == "__main__":
    unittest.main()
