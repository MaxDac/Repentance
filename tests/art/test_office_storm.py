"""The demonic apparition stays in the glass, behind the real Micah."""
from pathlib import Path
import re
import sys
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import office


class OfficeStormTests(unittest.TestCase):
    def test_apparition_is_smaller_and_translucent_in_both_flashes(self):
        with Image.open(ROOT / "assets" / "art" / "rooms" / "office_storm_lit.png") as background:
            glass = background.convert("RGB").crop(office.STORM_GLASS_BOX)
        original = np.array(glass).astype(int)
        for stage in (1, 2):
            with self.subTest(stage=stage):
                subtle = np.array(office.reflection(glass, stage)).astype(int)
                with patch.object(office, "STORM_REFLECTION_OPACITY", 1):
                    opaque = np.array(office.reflection(glass, stage)).astype(int)
                    with patch.object(office, "STORM_REFLECTION_SCALE", 1):
                        full_size = np.array(office.reflection(glass, stage)).astype(int)
                contrast = np.abs(subtle - original).sum() / np.abs(opaque - original).sum()
                self.assertGreater(contrast, 0.4)
                self.assertLess(contrast, 0.5)
                bounds = []
                for image in (opaque, full_size):
                    ys, xs = np.where(np.any(image != original, axis=2))
                    bounds.append((np.ptp(xs) + 1, np.ptp(ys) + 1))
                for shrunk, full in zip(*bounds):
                    self.assertAlmostEqual(shrunk / full, office.STORM_REFLECTION_SCALE, delta=0.04)

    def test_apparition_aligns_with_real_micah_not_the_other_pane(self):
        scene = (ROOT / "scenes" / "rooms" / "office_storm.tscn").read_text()
        entry = re.search(r'\[node name="window" type="Marker2D" parent="Entries"\]\n'
                          r'position = Vector2\((\d+), (\d+)\)', scene)
        self.assertIsNotNone(entry)
        self.assertEqual(office.STORM_REFLECTION_X, int(entry[1]))
        lightning = re.search(r'\[node name="Lightning".*?(?=\n\[node)', scene, re.S)[0]
        self.assertIn("z_index = -10", lightning)
        for stage in (1, 2):
            with self.subTest(stage=stage):
                node = re.search(rf'\[node name="Demon{stage}".*?(?=\n\[node)', scene, re.S)[0]
                x, y = office.STORM_GLASS_BOX[:2]
                self.assertIn(f"position = Vector2({x}, {y})", node)

    def test_both_stages_match_painter_and_remain_partly_visible_around_micah(self):
        art = ROOT / "assets" / "art"
        with Image.open(art / "rooms" / "office_storm_lit.png") as background:
            glass = background.convert("RGB").crop(office.STORM_GLASS_BOX)
        with Image.open(art / "sprites" / "micah_hatless_bottle.png") as sheet:
            # Player's back-facing idle frame, at the window entry's depth scale and feet anchor.
            player = sheet.crop((0, 192, 64, 288))
        scale = 0.86 + (168 - 164) / (262 - 164) * (1.1 - 0.86)
        player = player.resize((round(64 * scale), round(96 * scale)), Image.Resampling.NEAREST)
        mask = Image.new("L", glass.size)
        mask.paste(player.getchannel("A"), (
            round(office.STORM_REFLECTION_X - 32 * scale - office.STORM_GLASS_BOX[0]),
            round(168 - 93 * scale - office.STORM_GLASS_BOX[1])))
        covered = np.array(mask) > 0
        for stage in (1, 2):
            with self.subTest(stage=stage), Image.open(
                    art / "rooms" / f"office_storm_demon_{stage}.png") as committed:
                expected = office.reflection(glass, stage)
                np.testing.assert_array_equal(np.array(committed.convert("RGB")), np.array(expected))
                changed = np.any(np.array(expected) != np.array(glass), axis=2)
                self.assertGreater(np.count_nonzero(changed & covered), 100)
                self.assertGreater(np.count_nonzero(changed & ~covered), 100)
                pixels = np.array(expected).astype(int)
                eyes = (pixels[..., 0] > pixels[..., 1] + 30) & (pixels[..., 0] > pixels[..., 2] + 20)
                self.assertGreaterEqual(np.count_nonzero(eyes & ~covered), 4)
                # Frame, sash and sill are still in front of the painted apparition.
                for box in ((62, 0, 65, glass.height), (0, 9, glass.width, 12),
                            (0, glass.height - 5, glass.width, glass.height)):
                    np.testing.assert_array_equal(np.array(expected.crop(box)), np.array(glass.crop(box)))


if __name__ == "__main__":
    unittest.main()
