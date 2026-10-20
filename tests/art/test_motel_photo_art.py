"""The motel lobby: Micah, his back to us, holds Eleanor's photograph up for the clerk and puts it away again."""
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
NAMES = ("micah_show_photo_back", "micah_pocket_photo_back")


class MotelPhotoArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.build_show_photo_back()

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

    def test_starts_on_the_back_idle_frame(self):
        with Image.open(ROOT / "assets" / "art" / "sprites" / "micah.png") as sheet:
            idle = sheet.convert("RGBA").crop((0, 2 * FRAME[1], FRAME[0], 3 * FRAME[1]))
        self.assertIsNone(ImageChops.difference(self.frames("micah_show_photo_back")[0], idle).getbbox())

    def test_the_arm_bends_out_and_the_photo_stays_hidden(self):
        frames = self.frames("micah_show_photo_back")
        self.assertEqual(len(frames), 5)
        for frame in frames:  # his back hides the photograph
            self.assertFalse(any(frame.getpixel((x, y)) == MOUNT for y in range(frame.height) for x in range(frame.width)))
        right = [frame.getbbox()[2] for frame in frames]
        self.assertGreater(right[-1] - right[0], 4)  # the elbow juts out past his side

    def test_putting_it_away_reverses_the_strip(self):
        shown, pocketed = self.frames("micah_show_photo_back"), self.frames("micah_pocket_photo_back")
        self.assertEqual(len(pocketed), len(shown))
        for a, b in zip(shown, reversed(pocketed)):
            self.assertIsNone(ImageChops.difference(a, b).getbbox())


if __name__ == "__main__":
    unittest.main()
