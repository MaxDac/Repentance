"""The Chicago map: a real 1920 street map with tacks and tags that line up with the scene's markers and hotspots."""
from itertools import combinations
from pathlib import Path
import re
import sys
import unittest

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import chicago_map, common

SCENE = (ROOT / "scenes" / "rooms" / "chicago_map.tscn").read_text()
SCRIPT = (ROOT / "scripts" / "Rooms" / "ChicagoMap.cs").read_text()
ROOMS = ROOT / "assets" / "art" / "rooms"
CAPTION_TOP = 234
# ChicagoMap.Shows never puts these on the map together
EXCLUSIVE = {frozenset(p) for p in (("club", "tribune"), ("club", "harrington"), ("tribune", "harrington"))}


def places():
    """(hotspot id, scene node, marker key) for every place the room script can show."""
    out = []
    for spot, node in re.findall(r'\("(\w+)", "(\w+)"\)', SCRIPT.split("Places =", 1)[1].split("};", 1)[0]):
        texture = re.search(rf'\[node name="{node}" type="Sprite2D" parent="Markers"\][^\[]*'
                            r'texture = ExtResource\("([^"]+)"\)', SCENE)[1]
        key = re.search(rf'path="res://assets/art/rooms/map_(\w+)\.png" id="{texture}"', SCENE)[1]
        out.append((spot, node, key))
    return out


def marker_position(node):
    block = re.search(rf'\[node name="{node}" type="Sprite2D" parent="Markers"\]([^\[]*)', SCENE)[1]
    return tuple(map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", block).groups()))


def hotspot_rect(node, spot):
    centre = re.search(rf'parent="Hotspots/{node}"\]\nposition = Vector2\((\d+), (\d+)\)', SCENE).groups()
    size = re.search(rf'id="Rect_{spot}"\]\nsize = Vector2\((\d+), (\d+)\)', SCENE).groups()
    (cx, cy), (w, h) = map(int, centre), map(int, size)
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


class ChicagoMapArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.places = places()
        cls.pal = chicago_map.palette()

    def test_every_place_has_a_tack_and_a_tag(self):
        self.assertEqual({key for *_, key in self.places}, set(chicago_map.MARKERS))

    def test_the_map_is_printed_from_the_1920_scan(self):
        with Image.open(chicago_map.SRC) as scan:
            self.assertEqual(scan.mode, "L")
            self.assertGreaterEqual(scan.width, 1600)
        with Image.open(ROOMS / "map.png") as image:
            self.assertEqual(image.size, (480, 270))
            # a dense street map, not a few drawn lines: many distinct tones inside the paper
            self.assertGreater(len(image.crop(chicago_map.PRINT).getcolors(4096)), 60)

    def test_overlays_line_up_with_the_marker_nodes(self):
        with Image.open(ROOMS / "map.png") as background:
            base = background.convert("RGBA")
        for spot, node, key in self.places:
            with self.subTest(place=key), Image.open(ROOMS / f"map_{key}.png") as overlay:
                expected = chicago_map.paint_base()
                chicago_map.marker(expected, key)
                chicago_map.pencil(expected)
                chicago_map.lighting(expected)
                expected = common.pixelize(expected, self.pal).convert("RGBA")
                composed = base.copy()
                composed.alpha_composite(overlay.convert("RGBA"), marker_position(node))
                self.assertIsNone(ImageChops.difference(composed, expected).getbbox())

    def test_hotspots_cover_tack_and_tag_and_clear_the_caption(self):
        for spot, node, key in self.places:
            x0, y0, x1, y1 = hotspot_rect(node, spot)
            bx0, by0, bx1, by1 = chicago_map.marker_box(key)
            with self.subTest(place=key):
                self.assertLessEqual(x0, bx0)
                self.assertLessEqual(y0, by0)
                self.assertGreaterEqual(x1, bx1)
                self.assertGreaterEqual(y1, by1)
                self.assertLess(y1, CAPTION_TOP)

    def test_places_shown_together_do_not_overlap(self):
        for (a, na, _), (b, nb, _) in combinations(self.places, 2):
            if frozenset((a, b)) in EXCLUSIVE:
                continue
            ax0, ay0, ax1, ay1 = hotspot_rect(na, a)
            bx0, by0, bx1, by1 = hotspot_rect(nb, b)
            with self.subTest(pair=(a, b)):
                self.assertTrue(ax1 <= bx0 or bx1 <= ax0 or ay1 <= by0 or by1 <= ay0)


if __name__ == "__main__":
    unittest.main()
