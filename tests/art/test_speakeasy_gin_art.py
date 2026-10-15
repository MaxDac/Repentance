"""Blue Lantern bathtub gin: Micah's drinking strip and the counter glass."""
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
from art import common, speakeasy, sprites

GLASS = (0xaa, 0xc4, 0xcc, 255)
GIN = (0xe4, 0xec, 0xd2, 255)
FRAME = (64, 96)


class SpeakeasyGinArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.build_gin()
            speakeasy.build_gin()

    def test_committed_assets_match_generators(self):
        for folder, name in (("sprites", "micah_gin"), ("rooms", "speakeasy_gin"), ("rooms", "speakeasy_gin_empty")):
            with self.subTest(asset=name), Image.open(self.generated / folder / f"{name}.png") as generated, \
                    Image.open(ROOT / "assets" / "art" / folder / f"{name}.png") as committed:
                self.assertEqual(generated.size, committed.size)
                difference = ImageChops.difference(generated.convert("RGBA"), committed.convert("RGBA"))
                self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))
        generated = json.loads((self.generated / "sprites" / "micah_gin.json").read_text())
        committed = json.loads((ROOT / "assets" / "art" / "sprites" / "micah_gin.json").read_text())
        self.assertEqual(generated, committed)

    def frames(self):
        with Image.open(self.generated / "sprites" / "micah_gin.png") as strip:
            strip = strip.convert("RGBA")
            self.assertEqual(strip.height, FRAME[1])
            self.assertEqual(strip.width % FRAME[0], 0)
            return [strip.crop((i * FRAME[0], 0, (i + 1) * FRAME[0], FRAME[1])) for i in range(strip.width // FRAME[0])]

    @staticmethod
    def pixels(image, colour):
        return [(x, y) for y in range(image.height) for x in range(image.width) if image.getpixel((x, y)) == colour]

    def test_micah_lifts_the_glass_to_his_mouth_and_sets_it_down(self):
        frames = self.frames()
        self.assertEqual(len(frames), 7)
        glass = [self.pixels(f, GLASS) for f in frames]
        self.assertTrue(all(glass))
        mean_y = [sum(y for _, y in g) / len(g) for g in glass]
        top = min(range(len(frames)), key=lambda i: mean_y[i])
        self.assertEqual(top, 3)
        self.assertGreater(mean_y[0] - mean_y[top], 6)
        self.assertGreaterEqual(mean_y[top], 18)
        self.assertLessEqual(mean_y[top], 30)
        bottom = [max(y for _, y in g) for g in glass]
        self.assertEqual(bottom[-1], bottom[0])

    def test_the_gin_is_gone_after_the_drink(self):
        frames = self.frames()
        self.assertTrue(self.pixels(frames[0], GIN))
        self.assertFalse(self.pixels(frames[-1], GIN))

    def test_counter_glasses(self):
        for name, full in (("speakeasy_gin", True), ("speakeasy_gin_empty", False)):
            with self.subTest(asset=name), Image.open(self.generated / "rooms" / f"{name}.png") as image:
                image = image.convert("RGBA")
                self.assertEqual(image.size, (5, 7))
                self.assertEqual(bool(self.pixels(image, GIN)), full)
                self.assertEqual(image.getchannel("A").getextrema(), (255, 255))


if __name__ == "__main__":
    unittest.main()
