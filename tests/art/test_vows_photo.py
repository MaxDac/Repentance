"""The vow-renewal photo shown in ending 1's epilogue: a sepia studio print reduced to VGA pixels on a cream card."""
from pathlib import Path
import colorsys
import sys
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import closeup

UI = ROOT / "assets" / "art" / "ui"
M = closeup.MOUNT


def picture(photo):
    """The print in art pixels (each one is SCALE x SCALE on screen)."""
    box = photo.convert("RGB").crop((M, M, closeup.PHOTO_PW - M, closeup.PHOTO_PH - M))
    return box.resize((closeup.PHOTO_AW, closeup.PHOTO_AH), Image.NEAREST)


class VowsPhotoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.photo = closeup.vows_photo(Image.open(closeup.VOWS_SRC))

    def test_committed_photo_matches_the_build(self):
        with Image.open(UI / "vows_photo.png") as image:
            committed = image.convert("RGBA")
        self.assertEqual(committed.size, (closeup.PHOTO_PW, closeup.PHOTO_PH))
        self.assertTrue((np.asarray(committed) == np.asarray(self.photo)).all(), "regenerate with gen_art.py closeup")

    def test_photo_sized_portrait_on_the_left_of_the_screen(self):
        w, h = self.photo.size
        self.assertGreater(h, w * 1.3, "portrait, like a print")
        self.assertLessEqual(h, 270 - 20)
        self.assertLessEqual(w, 480 // 2 - 40, "leaves room for speech beside it")
        self.assertEqual(closeup.PHOTO_IH, closeup.IH, "as tall as the other close-ups' pictures")

    def test_crop_keeps_the_photo_aspect_inside_the_sources_border(self):
        w, h = closeup.vows_crop(Image.open(closeup.VOWS_SRC)).size
        self.assertAlmostEqual(w / h, closeup.PHOTO_AW / closeup.PHOTO_AH, delta=0.01)

    def test_chunky_pixels(self):
        a = np.asarray(self.photo.convert("RGB"))[M:-M, M:-M]
        self.assertTrue((a[0::2] == a[1::2]).all() and (a[:, 0::2] == a[:, 1::2]).all())

    def test_limited_sepia_palette(self):
        colours = picture(self.photo).getcolors(4096)
        self.assertLessEqual(len(colours), closeup.COLOURS)
        for _, (r, g, b) in colours:
            self.assertTrue(r >= g >= b, "warm brown tones only")
            self.assertLess(colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)[1], 0.7)

    def test_cream_card_mount_lighter_than_the_print(self):
        a = np.asarray(self.photo.convert("RGB"), dtype=float)
        mount = a[4:M - 2, 20:-20]
        self.assertGreater(mount.mean(), 190)
        self.assertGreater(mount.mean(), a[M:-M, M:-M].mean() + 40)

    def test_worn_corners_are_cut_away(self):
        alpha = np.asarray(self.photo)[..., 3]
        for y, x in ((0, 0), (0, -1), (-1, 0), (-1, -1)):
            self.assertEqual(alpha[y, x], 0)
        self.assertTrue((alpha[M:-M, M:-M] == 255).all())


if __name__ == "__main__":
    unittest.main()
