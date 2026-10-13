"""Rizzo's Flowers (the Blue Lantern front): the smoking regular is an animated strip, not part of the painting."""
import contextlib
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import common, expansion_act1

ROOMS = ROOT / "assets" / "art" / "rooms"
SCENE = ROOT / "scenes" / "rooms" / "blue_lantern_front.tscn"


def is_carnation_blue(px):
    r, g, b = px[:3]
    return b >= 150 and b - r >= 80 and b - g >= 40


def is_ember(px):
    r, g, b = px[:3]
    return r >= 190 and r - b >= 90 and g >= 60


def regular_node():
    scene = SCENE.read_text()
    node = re.search(r'\[node name="Regular" type="Sprite2D" parent="\."\]([^\[]*)', scene)
    assert node, "the scene has no Regular sprite"
    return node[1]


class FloristArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.background = Image.open(ROOMS / "blue_lantern_front.png").convert("RGB")
        cls.strip = Image.open(ROOMS / "blue_lantern_front_regular.png").convert("RGBA")
        node = regular_node()
        cls.frames_n = int(re.search(r"hframes = (\d+)", node)[1])
        x, y = re.search(r"position = Vector2\((\d+), (\d+)\)", node).groups()
        cls.origin = (int(x), int(y))
        cls.width = cls.strip.width // cls.frames_n
        cls.frames = [cls.strip.crop((k * cls.width, 0, (k + 1) * cls.width, cls.strip.height))
                      for k in range(cls.frames_n)]

    def test_strip_matches_scene_layout(self):
        self.assertEqual(self.frames_n, len(expansion_act1.SMOKE_POSES))
        self.assertEqual(self.strip.width % self.frames_n, 0)
        self.assertIn('ExtResource("8_regular")', regular_node())
        self.assertIn("IdleStrip", SCENE.read_text())
        x, y = self.origin
        self.assertLessEqual(y + self.strip.height, expansion_act1.BASE + 6)
        # the figure still stands where the regular's look/talk hotspot is
        self.assertTrue(x <= expansion_act1.REGULAR_X <= x + self.width)
        for k, frame in enumerate(self.frames):
            with self.subTest(frame=k):
                self.assertIsNotNone(frame.getchannel("A").getbbox())

    def test_sequence_steps_exist_in_the_strip(self):
        steps = re.search(r'Sequence = "([^"]+)"', regular_node())[1]
        for step in steps.split(","):
            frame, seconds = step.split(":")
            self.assertTrue(0 < int(frame) < self.frames_n, step)
            self.assertGreater(float(seconds), 0)

    def test_every_frame_wears_the_blue_carnation(self):
        for k, frame in enumerate(self.frames):
            with self.subTest(frame=k):
                blue = sum(1 for px in frame.get_flattened_data() if px[3] and is_carnation_blue(px))
                self.assertGreaterEqual(blue, 8)

    def test_the_arm_rises_to_the_mouth_with_a_glowing_cigarette(self):
        idle, mouth = self.frames[0], self.frames[3]
        self.assertIsNotNone(ImageChops.difference(idle, mouth).getbbox())
        for k, frame in enumerate(self.frames):
            with self.subTest(frame=k):
                self.assertTrue(any(px[3] and is_ember(px) for px in frame.get_flattened_data()))
        # resting, the ember hangs at his side; at the mouth it glows just under the brim
        def ember_y(frame):
            return min(y for y in range(frame.height) for x in range(frame.width)
                       if frame.getpixel((x, y))[3] and is_ember(frame.getpixel((x, y))))
        self.assertGreater(ember_y(idle), 40)
        self.assertLess(ember_y(mouth), 24)

    def test_the_brim_hides_his_face(self):
        # head bowed: hardly any skin shows between the hat and the collar
        idle = self.frames[0]
        cx = expansion_act1.REGULAR_X - self.origin[0]
        skin = 0
        for y in range(0, 20):
            for x in range(cx - 6, cx + 7):
                r, g, b, a = idle.getpixel((x, y))
                skin += a and r > 110 and r - b > 30 and g > 70
        self.assertLessEqual(skin, 4)

    def test_painting_has_no_baked_regular_or_figure_behind_the_glass(self):
        bg = self.background
        x, y = self.origin
        for name, box in (("regular", (x, y, x + self.width, y + self.strip.height)),
                          ("shop window", (136, 96, 168, 150))):
            with self.subTest(area=name):
                region = bg.crop(box)
                self.assertFalse(any(is_carnation_blue(px) for px in region.get_flattened_data()))
        # the figure is only in the strip, so with no strip the wall shows where he stands
        cx = expansion_act1.REGULAR_X
        r, _, b = ImageStat.Stat(bg.crop((cx - 4, 120, cx + 4, 140))).mean
        self.assertGreater(r, b + 10)

    def test_florist_art_matches_generator(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(common, "ART", tmp), contextlib.redirect_stdout(io.StringIO()):
                expansion_act1.build_florist()
            for path in (Path(tmp) / "rooms").glob("*.png"):
                with self.subTest(asset=path.name), Image.open(path) as generated, Image.open(
                        ROOMS / path.name) as committed:
                    self.assertEqual(generated.size, committed.size)
                    self.assertIsNone(ImageChops.difference(generated.convert("RGBA"),
                                                            committed.convert("RGBA")).getbbox())


if __name__ == "__main__":
    unittest.main()
