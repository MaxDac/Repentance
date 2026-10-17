"""Motel lobby: the background, the umbrella overlay and the front desk drawn over the clerk behind it."""
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
from art import common, motel_lobby

SCENE = ROOT / "scenes" / "rooms" / "motel_lobby.tscn"
FRAME = (56, 96)
NPC_BASELINE = 3


def scene_nodes():
    """Node name -> its properties (raw strings) from the room's .tscn."""
    nodes, current = {}, None
    for line in SCENE.read_text(encoding="utf-8").splitlines():
        m = re.match(r'\[node name="([^"]+)"', line)
        if m:
            current = nodes.setdefault(m.group(1), {})
            continue
        if line.startswith("["):
            current = None
        elif current is not None and " = " in line:
            key, value = line.split(" = ", 1)
            current[key] = value
    return nodes


def vec(value):
    x, y = re.match(r"Vector2\(([-\d.]+),\s*([-\d.]+)\)", value).groups()
    return float(x), float(y)


class MotelLobbyArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name) / "rooms"
        out = io.StringIO()
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(out):
            motel_lobby.build()
        cls.origins = {name: (int(x), int(y)) for name, x, y in
                       re.findall(r"(motel_lobby_\w+)\.png at \((\d+), (\d+)\)", out.getvalue())}
        cls.nodes = scene_nodes()

    def image(self, name):
        with Image.open(self.generated / f"{name}.png") as image:
            return image.convert("RGBA")

    def test_committed_assets_match_generator(self):
        for name in ("motel_lobby", "motel_lobby_umbrella", "motel_lobby_counter"):
            with self.subTest(asset=name), Image.open(ROOT / "assets" / "art" / "rooms" / f"{name}.png") as committed:
                generated = self.image(name)
                self.assertEqual(generated.size, committed.size)
                difference = ImageChops.difference(generated, committed.convert("RGBA"))
                self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))

    def test_background_fills_the_screen(self):
        background = self.image("motel_lobby")
        self.assertEqual(background.size, (480, 270))
        self.assertEqual(background.getchannel("A").getextrema(), (255, 255))

    def test_umbrella_overlay_sits_at_its_crop_origin(self):
        node = self.nodes["Umbrella"]
        self.assertEqual(vec(node["position"]), self.origins["motel_lobby_umbrella"])
        self.assertEqual(node["HideIfFlags"], '"took_umbrella"')
        umbrella = self.image("motel_lobby_umbrella")
        self.assertGreater(umbrella.height, umbrella.width)

    def test_counter_front_sits_at_its_crop_origin_and_baseline(self):
        node = self.nodes["CounterFront"]
        x, baseline = vec(node["position"])
        _, offset = vec(node["offset"])
        self.assertEqual(baseline, motel_lobby.COUNTER_BASELINE)
        self.assertEqual((x, baseline + offset), self.origins["motel_lobby_counter"])

    def test_counter_hides_the_clerks_legs_but_not_his_head(self):
        clerk = self.nodes["Clerk"]
        cx, feet = vec(clerk["position"])
        counter = self.nodes["CounterFront"]
        ox, baseline = vec(counter["position"])
        oy = baseline + vec(counter["offset"])[1]
        self.assertLess(feet, baseline, "the clerk must y-sort behind the desk")
        room = self.nodes["MotelLobby"]
        far_y, near_y = float(room["FarY"]), float(room["NearY"])
        far, near = float(room["FarScale"]), float(room["NearScale"])
        t = min(1.0, max(0.0, (feet - far_y) / (near_y - far_y)))
        scale = far + (near - far) * t
        top = feet + (NPC_BASELINE - FRAME[1]) * scale
        alpha = self.image("motel_lobby_counter").getchannel("A")

        def covered(x, y):
            px, py = round(x - ox), round(y - oy)
            return 0 <= px < alpha.width and 0 <= py < alpha.height and alpha.getpixel((px, py)) == 255

        legs = [(cx + dx, y) for dx in range(-8, 9, 2) for y in range(round(feet - 38 * scale), round(feet) + 1)]
        self.assertTrue(all(covered(x, y) for x, y in legs))
        head = [(cx + dx, y) for dx in range(-6, 7, 2) for y in range(round(top), round(top + 24 * scale))]
        self.assertFalse(any(covered(x, y) for x, y in head))


if __name__ == "__main__":
    unittest.main()
