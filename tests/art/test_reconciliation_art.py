"""Generated ring, pendant and whiskey-drinking artwork contracts."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, items, office, sprites


class ReconciliationArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            office.build()
            sprites.build_drinking()
            for name in ("faith_ring", "cross"):
                common.save(items._icon(getattr(items, name)), "items", f"{name}.png")

    def test_committed_assets_match_generators(self):
        for folder, names in (
                ("rooms", ("office", "office_ring", "office_cup")),
                ("sprites", ("micah_cup", "micah_drink")),
                ("items", ("faith_ring", "cross"))):
            for name in names:
                with self.subTest(asset=name), Image.open(self.generated / folder / f"{name}.png") as generated, \
                        Image.open(ROOT / "assets" / "art" / folder / f"{name}.png") as committed:
                    self.assertEqual(generated.size, committed.size)
                    difference = ImageChops.difference(generated.convert("RGBA"), committed.convert("RGBA"))
                    self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))

    def test_drinking_raises_the_whiskey_to_micahs_mouth(self):
        def whiskey_pixels(name):
            with Image.open(self.generated / "sprites" / f"micah_{name}.png") as image:
                self.assertEqual(image.size, (64, 96))
                return [(x, y) for y in range(image.height) for x in range(image.width)
                        if image.getpixel((x, y)) == (168, 96, 36, 255)]
        held = whiskey_pixels("cup")
        raised = whiskey_pixels("drink")
        self.assertTrue(held)
        self.assertTrue(raised)
        held_y = sum(y for _, y in held) / len(held)
        raised_y = sum(y for _, y in raised) / len(raised)
        self.assertGreater(held_y - raised_y, 12)
        self.assertGreaterEqual(raised_y, 20)
        self.assertLessEqual(raised_y, 30)

    def test_office_props_and_inventory_icons_have_transparency(self):
        for folder, name, size in (
                ("rooms", "office_ring", (3, 2)), ("rooms", "office_ring_glint", (35, 7)), ("rooms", "office_cup", (10, 12)),
                ("items", "faith_ring", (32, 24)), ("items", "cross", (32, 24))):
            with self.subTest(asset=name), Image.open(self.generated / folder / f"{name}.png") as image:
                self.assertEqual(image.size, size)
                self.assertEqual(image.getchannel("A").getextrema(), (0, 255))


if __name__ == "__main__":
    unittest.main()
