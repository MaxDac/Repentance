"""The Harrington alley's looping trash fire and the close-up of the heraldry at the foot of the portrait."""
from pathlib import Path
import re
import sys
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import act2_rooms, closeup

ROOMS = ROOT / "assets" / "art" / "rooms"
UI = ROOT / "assets" / "art" / "ui"


def node_position(scene, node):
    text = (ROOT / "scenes" / "rooms" / scene).read_text(encoding="utf-8")
    block = text.split(f'[node name="{node}"', 1)[1].split("[node ", 1)[0]
    x, y = re.search(r"position = Vector2\(([-\d.]+), ([-\d.]+)\)", block).groups()
    return int(float(x)), int(float(y))


class FlamesStripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Image.open(ROOMS / "harrington_road_flames.png") as im:
            cls.strip = np.asarray(im.convert("RGB")).astype(int)
        x0, y0, x1, y1 = act2_rooms.FIRE_BOX
        cls.w, cls.h = x1 - x0, y1 - y0

    def frame(self, i):
        return self.strip[:, i * self.w:(i + 1) * self.w]

    def test_strip_holds_every_frame_of_the_fire_box(self):
        self.assertEqual(self.strip.shape[:2], (self.h, self.w * act2_rooms.FIRE_FRAMES))

    def test_node_sits_on_the_fire_box(self):
        self.assertEqual(node_position("harrington_road.tscn", "Flames"), act2_rooms.FIRE_BOX[:2])

    def test_first_frame_continues_the_lit_fire_overlay(self):
        with Image.open(ROOMS / "harrington_road.png") as base, Image.open(ROOMS / "harrington_road_fire.png") as fire:
            lit = base.convert("RGBA")
            lit.alpha_composite(fire.convert("RGBA"), node_position("harrington_road.tscn", "Fire"))
            expected = np.asarray(lit.convert("RGB").crop(act2_rooms.FIRE_BOX)).astype(int)
        self.assertLessEqual(np.abs(self.frame(0) - expected).mean(), 2.0)

    def test_flames_and_smoke_move_between_frames(self):
        for i in range(act2_rooms.FIRE_FRAMES):
            nxt = (i + 1) % act2_rooms.FIRE_FRAMES
            changed = (np.abs(self.frame(i) - self.frame(nxt)).sum(axis=2) > 30).mean()
            self.assertGreater(changed, 0.03, f"frame {i} -> {nxt} barely changes")


class HeraldryCloseupTests(unittest.TestCase):
    def test_committed_panel_matches_the_build(self):
        with Image.open(UI / "heraldry_closeup.png") as im:
            committed = np.asarray(im.convert("RGB"))
        built = np.asarray(closeup.heraldry_closeup().convert("RGB"))
        self.assertEqual(committed.shape, built.shape)
        self.assertTrue((committed == built).all())

    def test_band_carries_three_beast_and_sky_pairs(self):
        self.assertEqual([(beast, sky) for beast, sky, *_ in act2_rooms.HERALDRY],
                         [("raven", "star"), ("lion", "sun"), ("stag", "moon")])


if __name__ == "__main__":
    unittest.main()
