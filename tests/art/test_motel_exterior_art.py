"""Pixel-exact checks for the motel back alley and its fire-escape landing."""
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
from art import common, motel_exterior

ROOMS = ROOT / "assets" / "art" / "rooms"


class MotelExteriorArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name) / "rooms"
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            motel_exterior.build()

    def assert_images_equal(self, actual, expected):
        self.assertEqual(actual.size, expected.size)
        self.assertIsNone(ImageChops.difference(actual.convert("RGB"), expected.convert("RGB")).getbbox())

    def test_committed_art_matches_the_generator(self):
        names = sorted(path.name for path in self.generated.glob("*.png"))
        self.assertEqual(names, ["motel_alley.png", "motel_alley_crate.png", "motel_alley_crate_under.png",
                                 "motel_alley_ladder.png", "motel_fire_escape.png", "motel_fire_escape_fg.png"])
        for name in names:
            with self.subTest(asset=name), Image.open(self.generated / name) as generated, \
                    Image.open(ROOMS / name) as committed:
                self.assert_images_equal(committed, generated)

    def test_backgrounds_fill_the_viewport_and_are_opaque(self):
        for name in ("motel_alley", "motel_fire_escape"):
            with self.subTest(room=name), Image.open(ROOMS / f"{name}.png") as image:
                self.assertEqual(image.size, (480, 270))
                if image.mode == "RGBA":
                    self.assertEqual(image.getchannel("A").getextrema(), (255, 255))
                self.assertLessEqual(len(image.convert("RGB").getcolors(480 * 270)), 160)

    def test_alley_overlays_match_variants_at_scene_positions(self):
        scene = (ROOT / "scenes" / "rooms" / "motel_alley.tscn").read_text()
        base, pal = motel_exterior.alley_pal()
        with Image.open(ROOMS / "motel_alley.png") as background:
            self.assert_images_equal(background, common.pixelize(base, pal))
        composed = {}
        for name, flags, before, _ in motel_exterior.ALLEY_OVERLAYS:
            resource_id = re.search(rf'path="res://assets/art/rooms/{name}\.png" id="([^"]+)"', scene)[1]
            node = next(block for block in re.split(r"(?=\[node )", scene)
                        if f'texture = ExtResource("{resource_id}")' in block)
            x, y = map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", node).groups())
            after = common.pixelize(motel_exterior.paint_alley(**flags), pal)
            start = composed.get(tuple(sorted(before.items())))
            if start is None:
                start = common.pixelize(motel_exterior.paint_alley(**before), pal)
            with self.subTest(overlay=name), Image.open(ROOMS / f"{name}.png") as overlay:
                self.assertLessEqual(x + overlay.width, 480)
                self.assertLessEqual(y + overlay.height, 270)
                self.assert_images_equal(overlay, after.crop((x, y, x + overlay.width, y + overlay.height)))
                image = start.copy()
                image.paste(overlay, (x, y))
                self.assert_images_equal(image, after)
                composed[tuple(sorted(flags.items()))] = image

    def test_alley_base_has_no_crate_by_the_cans(self):
        base = motel_exterior.paint_alley()
        home = motel_exterior.paint_alley(crate="home")
        self.assertIsNotNone(ImageChops.difference(base, home).getbbox())

    def test_front_rail_is_cut_from_the_landing_and_sorted_in_front_of_the_floor(self):
        scene = (ROOT / "scenes" / "rooms" / "motel_fire_escape.tscn").read_text()
        node = next(block for block in re.split(r"(?=\[node )", scene) if 'name="RailFront"' in block)
        x, y = map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", node).groups())
        offset = int(re.search(r"offset = Vector2\(0, (-\d+)\)", node)[1])
        walk_bottom = max(map(int, re.search(r"polygon = PackedVector2Array\(([^)]*)\)", scene)[1]
                              .replace(" ", "").split(",")[1::2]))
        self.assertGreater(y, walk_bottom, "everyone on the landing stands behind the rail")
        with Image.open(ROOMS / "motel_fire_escape.png") as background, \
                Image.open(ROOMS / "motel_fire_escape_fg.png") as front:
            top = y + offset
            self.assertEqual((x, top), (0, motel_exterior.FE_FG_Y))
            alpha = front.getchannel("A")
            self.assertEqual(alpha.getextrema(), (0, 255))
            self.assertEqual(alpha.histogram()[1:255], [0] * 254, "the cut-out is hard-edged")
            crop = background.convert("RGBA").crop((0, top, front.width, top + front.height))
            crop.putalpha(alpha)
            self.assert_images_equal(front, crop)
            hatch = alpha.crop((motel_exterior.HATCH[0] + 6, 0, motel_exterior.HATCH[1] + 4, front.height))
            self.assertIsNone(hatch.getbbox(), "the rail breaks at the hatch for the ladder")


if __name__ == "__main__":
    unittest.main()
