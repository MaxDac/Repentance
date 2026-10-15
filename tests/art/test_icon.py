"""The game icon: committed files match the generator, and the Linux desktop entry matches Godot's window class."""
import configparser
import contextlib
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, icon

DIST = ROOT / "dist" / "linux"


class IconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", str(cls.generated / "art")), contextlib.redirect_stdout(io.StringIO()):
            icon.build(dist=str(cls.generated / "dist"))

    def assert_same(self, a, b):
        self.assertEqual(a.size, b.size)
        self.assertTrue((np.asarray(a.convert("RGBA")) == np.asarray(b.convert("RGBA"))).all(),
                        "regenerate with gen_art.py icon")

    def ico_frames(self, path):
        with Image.open(path) as ico:
            frames = {}
            for size in sorted(ico.info["sizes"]):
                ico.size = size
                ico.load()
                frames[size[0]] = ico.copy()
            return frames

    def test_committed_png_matches_generator(self):
        with Image.open(self.generated / "art" / "ui" / "icon.png") as generated, \
                Image.open(ROOT / "assets" / "art" / "ui" / "icon.png") as committed:
            self.assertEqual(committed.size, (256, 256))
            self.assert_same(generated, committed)

    def test_committed_ico_has_every_size_and_matches_generator(self):
        generated = self.ico_frames(self.generated / "art" / "ui" / "icon.ico")
        committed = self.ico_frames(ROOT / "assets" / "art" / "ui" / "icon.ico")
        self.assertEqual(sorted(committed), list(icon.SIZES))
        for size in icon.SIZES:
            with self.subTest(size=size):
                self.assert_same(generated[size], committed[size])
                self.assert_same(committed[size], icon.sized(icon.master(), size))

    def test_committed_hicolor_icons_match_generator(self):
        for size in icon.SIZES:
            rel = Path("icons") / "hicolor" / f"{size}x{size}" / "apps" / "repentance.png"
            with self.subTest(size=size), Image.open(self.generated / "dist" / rel) as generated, \
                    Image.open(DIST / rel) as committed:
                self.assertEqual(committed.size, (size, size))
                self.assert_same(generated, committed)

    def test_white_cross_on_black(self):
        img = np.asarray(icon.master().convert("L"))
        for corner in (img[0, 0], img[0, -1], img[-1, 0], img[-1, -1]):
            self.assertEqual(corner, 0)
        self.assertEqual(img[7, 16], 255)
        self.assertGreaterEqual(img[12, 11], 204)
        self.assertLess(img[26, 16], img[7, 16])
        self.assertGreater(img[26, 16], img[26, 12])

    def test_desktop_entry_matches_the_window_class(self):
        name = re.search(r'^config/name="([^"]+)"', (ROOT / "project.godot").read_text(), re.M).group(1)
        entry = configparser.ConfigParser(interpolation=None)
        entry.optionxform = str
        entry.read(DIST / f"{name}.desktop")
        section = entry["Desktop Entry"]
        self.assertEqual(section["StartupWMClass"], name)
        self.assertEqual(section["Icon"], "repentance")
        self.assertEqual(section["Name"], name)

    def test_godot_and_windows_export_use_the_icon(self):
        project = (ROOT / "project.godot").read_text()
        self.assertIn('config/icon="res://assets/art/ui/icon.png"', project)
        self.assertIn('config/windows_native_icon="res://assets/art/ui/icon.ico"', project)
        presets = (ROOT / "export_presets.cfg").read_text()
        self.assertIn('application/icon="res://assets/art/ui/icon.ico"', presets)
        self.assertIn("application/modify_resources=true", presets)


if __name__ == "__main__":
    unittest.main()
