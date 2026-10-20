"""Act 2 motel return: Micah hauling the desk clerk down onto the counter by his tie."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, sprites

ART = ROOT / "assets" / "art"
NAMES = ("micah_tie_pull", "clerk_tie_pulled")


def frames(name):
    meta = json.loads((ART / "sprites" / f"{name}.json").read_text())
    with Image.open(ART / "sprites" / f"{name}.png") as image:
        sheet = image.convert("RGBA")
    w, h = meta["width"], meta["height"]
    return meta, [sheet.crop((i * w, 0, (i + 1) * w, h)) for i in range(len(meta["frames"]))]


class MotelTieArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.tie_pull_strips()

    def test_committed_assets_match_generator(self):
        for name in NAMES:
            with self.subTest(asset=name), Image.open(self.generated / "sprites" / f"{name}.png") as generated, \
                    Image.open(ART / "sprites" / f"{name}.png") as committed:
                self.assertEqual(generated.size, committed.size)
                difference = ImageChops.difference(generated.convert("RGBA"), committed.convert("RGBA"))
                self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))
            self.assertEqual(json.loads((self.generated / "sprites" / f"{name}.json").read_text()),
                             json.loads((ART / "sprites" / f"{name}.json").read_text()))

    def test_micah_reaches_out_and_hauls_back(self):
        meta, images = frames("micah_tie_pull")
        self.assertEqual(len(images), 4)
        right = [b[0] + b[2] for b in (f["bounds"] for f in meta["frames"])]
        self.assertGreater(right[1], right[0] + 8, "the reach goes out over the desk")
        self.assertLess(right[3], right[2], "the yank pulls the fist back towards him")

    def test_clerk_ends_face_down_on_the_desktop_with_his_legs_hidden(self):
        meta, images = frames("clerk_tie_pulled")
        self.assertEqual(len(images), 3)
        feet = meta["frames"][0]["anchor"][1]
        for image in images:
            alpha = np.asarray(image.getchannel("A"))
            rows = np.nonzero(alpha.max(axis=1))[0]
            self.assertLess(rows.max(), feet - sprites.CLERK_CUT, "the desk hides him below the desktop")
        heads = [f["head"] for f in meta["frames"]]
        self.assertGreater(heads[2][1], heads[0][1] + 25, "his head comes down onto the counter")
        self.assertGreater(heads[2][0], heads[0][0] + 10, "pulled forward, across the desk towards Micah")


if __name__ == "__main__":
    unittest.main()
