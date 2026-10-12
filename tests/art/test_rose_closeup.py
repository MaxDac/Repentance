"""The framed close-up of Rose calling Micah back from her door, reduced to a VGA panel from the committed picture."""
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


class RoseCloseupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel = closeup.rose_closeup(Image.open(closeup.ROSE_SRC))

    def test_committed_panel_matches_the_build_and_is_the_same_size_as_eleanors(self):
        committed = Image.open(UI / "rose_closeup.png").convert("RGB")
        self.assertEqual(committed.size, (closeup.PW, closeup.PH))
        self.assertEqual(self.panel.size, Image.open(UI / "stage_closeup.png").size)
        self.assertTrue((np.asarray(committed) == np.asarray(self.panel)).all(), "regenerate with gen_art.py closeup")

    def test_crop_keeps_the_panel_aspect(self):
        w, h = closeup.rose_crop(Image.open(closeup.ROSE_SRC)).size
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

    def test_her_face_is_warm_in_the_middle_between_the_dark_brick(self):
        a = np.asarray(inner(self.panel), dtype=float)
        face = a[45:80, 95:125]
        r, g, b = face[..., 0].mean(), face[..., 1].mean(), face[..., 2].mean()
        self.assertTrue(r > g > b and r > 150, "warm skin tones")
        self.assertGreater(face.mean(), a[:, :15].mean() * 3)


if __name__ == "__main__":
    unittest.main()
