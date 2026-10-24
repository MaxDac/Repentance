"""The Blue Lantern's back alley: the flickering lamp and the back door propped open in Act 1 compose, at their
scene positions, into exactly the painted lamp-off/lamp-on x shut/ajar states."""
import contextlib
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import alley, common

ROOMS = ROOT / "assets" / "art" / "rooms"
NAMES = ["alley.png", "alley_door_open.png", "alley_door_open_lamp.png", "alley_lamp.png"]


def position(scene, node):
    block = next(b for b in re.split(r"(?=\[node )", scene) if b.startswith(f'[node name="{node}"'))
    return tuple(map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", block).groups()))


class AlleyArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name) / "rooms"
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            alley.build()
        cls.off, cls.on, cls.ajar_off, cls.ajar_on = alley.variants()

    def assert_images_equal(self, actual, expected):
        self.assertEqual(actual.size, expected.size)
        self.assertIsNone(ImageChops.difference(actual.convert("RGB"), expected.convert("RGB")).getbbox())

    def test_committed_art_matches_the_generator(self):
        self.assertEqual(sorted(p.name for p in self.generated.glob("*.png")), NAMES)
        for name in NAMES:
            with self.subTest(asset=name), Image.open(self.generated / name) as generated, \
                    Image.open(ROOMS / name) as committed:
                self.assert_images_equal(committed, generated)

    def test_overlays_compose_every_state_at_scene_positions(self):
        scene = (ROOT / "scenes" / "rooms" / "alley.tscn").read_text()
        lamp_at = position(scene, "Lamp")
        door_at = position(scene, "DoorOpen")
        lit_rel = position(scene, "DoorOpenLit")
        lit_at = (lamp_at[0] + lit_rel[0], lamp_at[1] + lit_rel[1])
        self.assertIn('parent="Lamp"', next(b for b in re.split(r"(?=\[node )", scene)
                                             if b.startswith('[node name="DoorOpenLit"')))
        with Image.open(ROOMS / "alley.png") as bg, Image.open(ROOMS / "alley_lamp.png") as lamp, \
                Image.open(ROOMS / "alley_door_open.png") as door, \
                Image.open(ROOMS / "alley_door_open_lamp.png") as door_lit:
            layers = {"bg": bg.convert("RGBA"), "lamp": (lamp.convert("RGBA"), lamp_at),
                      "door": (door.convert("RGBA"), door_at), "door_lit": (door_lit.convert("RGBA"), lit_at)}
            # scene draw order: background, DoorOpen (same z, later), Lamp (z -9), then its child DoorOpenLit
            for label, lit, ajar, expected in (("off", False, False, self.off), ("on", True, False, self.on),
                                               ("ajar off", False, True, self.ajar_off),
                                               ("ajar on", True, True, self.ajar_on)):
                image = layers["bg"].copy()
                order = (["door"] if ajar else []) + (["lamp"] if lit else []) + (["door_lit"] if lit and ajar else [])
                for key in order:
                    overlay, at = layers[key]
                    image.alpha_composite(overlay, at)
                with self.subTest(state=label):
                    self.assert_images_equal(image, expected)

    def test_door_overlays_are_cut_to_the_door_and_its_light(self):
        with Image.open(ROOMS / "alley_door_open.png") as door:
            self.assertEqual(door.mode, "RGBA")
            x0, y0, x1, y1 = alley.DOOR
            self.assertLessEqual(door.width, (x1 - x0) * 3)
            self.assertLessEqual(door.height, (y1 - y0) * 3)

    def test_moon_keeps_readable_surface_shading_after_palette_reduction(self):
        for image in (self.off, self.on, self.ajar_off, self.ajar_on):
            core = image.crop((54, 5, 63, 14))
            colours = {rgb for _, rgb in core.getcolors(core.width * core.height)}
            self.assertGreaterEqual(len(colours), 3, "the lunar disk must not flatten to a single colour")
            luminance = [sum(rgb) for rgb in colours]
            self.assertGreater(max(luminance) - min(luminance), 80, "craters need visible contrast")


if __name__ == "__main__":
    unittest.main()
