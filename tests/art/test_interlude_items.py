"""Eleanor's interlude item icons (puzzles 17 and 18): the committed PNGs match the generator, alpha included."""
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, interludes


class InterludeItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.art = Path(cls.directory.name) / "art"
        with patch.object(common, "ART", str(cls.art)), contextlib.redirect_stdout(io.StringIO()):
            interludes.build()

    def test_committed_icons_match_generator(self):
        for name, _ in interludes.ICONS:
            with self.subTest(name=name), Image.open(self.art / "items" / f"{name}.png") as generated, \
                    Image.open(ROOT / "assets" / "art" / "items" / f"{name}.png") as committed:
                self.assertEqual(committed.size, (32, 24))
                self.assertTrue((np.asarray(generated.convert("RGBA")) == np.asarray(committed.convert("RGBA"))).all(),
                                "regenerate with gen_art.py interludes")

    def test_every_icon_is_drawn(self):
        for name, fn in interludes.ICONS:
            with self.subTest(name=name):
                alpha = np.asarray(interludes._icon(fn))[:, :, 3]
                self.assertGreater((alpha > 0).sum(), 40)


if __name__ == "__main__":
    unittest.main()
