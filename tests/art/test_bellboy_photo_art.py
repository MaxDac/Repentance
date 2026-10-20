"""The Aurelian lobby: Micah shows the bellboy Eleanor's photograph and puts it away again."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, sprites

MOUNT = sprites.PHOTO_CARD[0]
FRAME = (64, 96)
NAMES = ("micah_show_photo", "micah_pocket_photo")


class BellboyPhotoArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.build_show_photo()

    def test_committed_assets_match_generators(self):
        for name in NAMES:
            with self.subTest(asset=name), Image.open(self.generated / "sprites" / f"{name}.png") as generated, \
                    Image.open(ROOT / "assets" / "art" / "sprites" / f"{name}.png") as committed:
                self.assertEqual(generated.size, committed.size)
                difference = ImageChops.difference(generated.convert("RGBA"), committed.convert("RGBA"))
                self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))
                self.assertEqual(json.loads((self.generated / "sprites" / f"{name}.json").read_text()),
                                 json.loads((ROOT / "assets" / "art" / "sprites" / f"{name}.json").read_text()))

    def frames(self, name):
        with Image.open(self.generated / "sprites" / f"{name}.png") as strip:
            strip = strip.convert("RGBA")
            self.assertEqual(strip.height, FRAME[1])
            return [strip.crop((i * FRAME[0], 0, (i + 1) * FRAME[0], FRAME[1])) for i in range(strip.width // FRAME[0])]

    @staticmethod
    def card(image):
        return [(x, y) for y in range(image.height) for x in range(image.width) if image.getpixel((x, y)) == MOUNT]

    def test_the_photo_comes_out_of_the_coat_and_is_held_out(self):
        frames = self.frames("micah_show_photo")
        self.assertEqual(len(frames), 5)
        cards = [self.card(f) for f in frames]
        self.assertFalse(cards[0] or cards[1])
        self.assertTrue(all(cards[2:]))
        drawn_x = min(x for x, _ in cards[2])
        shown_x = min(x for x, _ in cards[-1])
        self.assertGreater(shown_x - drawn_x, 4)  # held out towards the bellboy
        self.assertLessEqual(shown_x - FRAME[0] // 2, 17)  # halfway to him, not in his face
        shown_y = sum(y for _, y in cards[-1]) / len(cards[-1])
        self.assertGreaterEqual(shown_y, 18)
        self.assertLessEqual(shown_y, 40)  # about his face, not down at his waist

    def test_putting_it_away_reverses_the_strip(self):
        shown, pocketed = self.frames("micah_show_photo"), self.frames("micah_pocket_photo")
        self.assertEqual(len(pocketed), len(shown))
        for a, b in zip(shown, reversed(pocketed)):
            self.assertIsNone(ImageChops.difference(a, b).getbbox())
        self.assertFalse(self.card(pocketed[-1]))


if __name__ == "__main__":
    unittest.main()
