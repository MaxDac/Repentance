"""Motel fire escape, end of Act 1: Micah steps in and kisses Eleanor (one strip played on the player)."""
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

SPRITES = ROOT / "assets" / "art" / "sprites"


def same(a, b):
    difference = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA"))
    return all(channel.getbbox() is None for channel in difference.split())


class FireEscapeKissArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name) / "sprites"
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.kiss_strip()
        cls.meta = json.loads((cls.generated / "micah_kiss.json").read_text())

    def frames(self):
        with Image.open(self.generated / "micah_kiss.png") as strip:
            strip = strip.convert("RGBA")
            w, h = self.meta["width"], self.meta["height"]
            return [strip.crop((i * w, 0, (i + 1) * w, h)) for i in range(strip.width // w)]

    def test_committed_assets_match_generator(self):
        with Image.open(self.generated / "micah_kiss.png") as generated, Image.open(SPRITES / "micah_kiss.png") as committed:
            self.assertEqual(generated.size, committed.size)
            self.assertTrue(same(generated, committed))
        self.assertEqual(self.meta, json.loads((SPRITES / "micah_kiss.json").read_text()))

    def test_first_frame_is_both_idle_sprites_where_they_stood(self):
        """No pose jump when the strip replaces Micah's sheet and the hidden Eleanor actor."""
        first = self.frames()[0]
        anchor_x = int(self.meta["frames"][0]["anchor"][0])
        with Image.open(SPRITES / "micah.png") as sheet:
            micah = sheet.convert("RGBA").crop((0, 0, sprites.FW, sprites.FH))
        with Image.open(SPRITES / "eleanor.png") as strip:
            eleanor = strip.convert("RGBA").crop((0, 0, sprites.NPC_W, sprites.FH)).transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        expected = Image.new("RGBA", first.size)
        expected.alpha_composite(eleanor, (anchor_x + sprites.KISS_GAP - sprites.NPC_W // 2, -sprites.KISS_RISE))
        expected.alpha_composite(micah, (anchor_x - sprites.FW // 2, 0))
        self.assertTrue(same(first, expected))

    def test_they_close_in_and_hold_the_kiss(self):
        frames = self.frames()
        self.assertEqual(len(frames), len(sprites.KISS_KEYS))
        gaps = []
        for image in frames:
            alpha = image.getchannel("A").load()
            # the space between their faces at mouth height
            row = [x for x in range(image.width) if alpha[x, 26]]
            gaps.append(sum(1 for x in range(min(row), max(row)) if not alpha[x, 26]))
        self.assertGreater(gaps[0], 0)
        self.assertEqual(gaps[-1], 0, "their faces meet in the held kiss")
        self.assertGreater(self.meta["frames"][-1]["seconds"], self.meta["frames"][0]["seconds"])


if __name__ == "__main__":
    unittest.main()
