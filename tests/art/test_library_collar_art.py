"""Library: Micah grabs the librarian by the collar and lets him go (two strips played on the player)."""
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
NAMES = ("micah_collar", "micah_collar_release")


def same(a, b):
    difference = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA"))
    return all(channel.getbbox() is None for channel in difference.split())


class LibraryCollarArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name) / "sprites"
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.collar_strips()
        cls.meta = {n: json.loads((cls.generated / f"{n}.json").read_text()) for n in NAMES}

    def frames(self, name):
        with Image.open(self.generated / f"{name}.png") as strip:
            strip = strip.convert("RGBA")
            w, h = self.meta[name]["width"], self.meta[name]["height"]
            return [strip.crop((i * w, 0, (i + 1) * w, h)) for i in range(strip.width // w)]

    def idle(self):
        """Both idle sprites exactly where they stood: Micah's sheet and the hidden librarian actor."""
        anchor_x = int(self.meta["micah_collar"]["frames"][0]["anchor"][0])
        with Image.open(SPRITES / "micah.png") as sheet:
            micah = sheet.convert("RGBA").crop((0, 0, sprites.FW, sprites.FH))
        with Image.open(SPRITES / "librarian.png") as strip:
            librarian = strip.convert("RGBA").crop((0, 0, sprites.NPC_W, sprites.FH)).transpose(
                Image.Transpose.FLIP_LEFT_RIGHT)
        expected = Image.new("RGBA", (sprites.COLLAR_W, sprites.FH))
        expected.alpha_composite(librarian, (anchor_x + sprites.COLLAR_GAP - sprites.NPC_W // 2, -sprites.COLLAR_RISE))
        expected.alpha_composite(micah, (anchor_x - sprites.FW // 2, 0))
        return expected

    def test_committed_assets_match_generator(self):
        for name in NAMES:
            with Image.open(self.generated / f"{name}.png") as generated, Image.open(SPRITES / f"{name}.png") as committed:
                self.assertEqual(generated.size, committed.size)
                self.assertTrue(same(generated, committed), name)
            self.assertEqual(self.meta[name], json.loads((SPRITES / f"{name}.json").read_text()))

    def test_grab_starts_and_release_ends_on_the_idle_sprites(self):
        """No pose jump when the strips replace Micah's sheet and the hidden librarian actor."""
        self.assertTrue(same(self.frames("micah_collar")[0], self.idle()))
        self.assertTrue(same(self.frames("micah_collar_release")[-1], self.idle()))

    def test_release_starts_on_the_held_grab(self):
        self.assertTrue(same(self.frames("micah_collar")[-1], self.frames("micah_collar_release")[0]))
        self.assertGreater(self.meta["micah_collar"]["frames"][-1]["seconds"],
                           self.meta["micah_collar"]["frames"][0]["seconds"])

    def test_they_close_in_for_the_grab(self):
        def gap(image, y):
            alpha = image.getchannel("A").load()
            row = [x for x in range(image.width) if alpha[x, y]]
            return sum(1 for x in range(min(row), max(row)) if not alpha[x, y]) if row else 99

        first, held = self.frames("micah_collar")[0], self.frames("micah_collar")[-1]
        self.assertGreater(min(gap(first, y) for y in range(26, 40)), 0)
        self.assertEqual(min(gap(held, y) for y in range(26, 40)), 0, "Micah's hand is on the librarian's collar")

    def librarian_box(self, frame):
        """The librarian is everything right of Micah's own sprite."""
        anchor_x = int(self.meta["micah_collar"]["frames"][0]["anchor"][0])
        return frame.getchannel("A").crop((anchor_x + sprites.FW // 2, 0, frame.width, frame.height)).getbbox()

    def test_librarian_keeps_his_feet_on_the_floor(self):
        floor = self.librarian_box(self.frames("micah_collar")[0])[3]
        for name in NAMES:
            for i, frame in enumerate(self.frames(name)):
                self.assertEqual(self.librarian_box(frame)[3], floor, f"{name} frame {i}: Micah can't lift him")

    def test_micah_drags_the_librarian_nearer(self):
        first, held = self.frames("micah_collar")[0], self.frames("micah_collar")[-1]
        self.assertLessEqual(self.librarian_box(held)[2], self.librarian_box(first)[2] - 8)


if __name__ == "__main__":
    unittest.main()
