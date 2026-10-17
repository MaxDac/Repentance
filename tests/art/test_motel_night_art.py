"""Micah lighting a cigarette, the motel night clerk and the umbrella icon: generated art contracts."""
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
from art import common, items, sprites

ART = ROOT / "assets" / "art"


def opaque(image):
    return [tuple(int(v) for v in p) for p in np.asarray(image.convert("RGBA")).reshape(-1, 4) if p[3] == 255]


def colours(image):
    return set(opaque(image))


class MotelNightArtTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            sprites.build_smoke()
            name, spec, arms, extra = next(entry for entry in sprites.NPCS if entry[0] == "clerk")
            sprites.npc_strip(spec, name, arms, **dict(extra))
            common.save(items._icon(items.umbrella), "items", "umbrella.png")

    def test_committed_assets_match_generators(self):
        for folder, name in (("sprites", "micah_smoke"), ("sprites", "clerk"), ("items", "umbrella")):
            with self.subTest(asset=name), Image.open(self.generated / folder / f"{name}.png") as generated, \
                    Image.open(ART / folder / f"{name}.png") as committed:
                self.assertEqual(generated.size, committed.size)
                difference = ImageChops.difference(generated.convert("RGBA"), committed.convert("RGBA"))
                self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))
        self.assertEqual(json.loads((self.generated / "sprites" / "micah_smoke.json").read_text()),
                         json.loads((ART / "sprites" / "micah_smoke.json").read_text()))

    def test_smoke_strip_lights_up_and_holds_the_lit_cigarette_last(self):
        meta = json.loads((ART / "sprites" / "micah_smoke.json").read_text())
        frames = meta["frames"]
        self.assertTrue(6 <= len(frames) <= 9)
        self.assertTrue(1.5 <= sum(f["seconds"] for f in frames) <= 4.0)
        self.assertEqual(max(f["seconds"] for f in frames), frames[-1]["seconds"], "the held pose lingers")
        with Image.open(ART / "sprites" / "micah_smoke.png") as strip:
            strip = strip.convert("RGBA")
            w = meta["width"]
            cells = [strip.crop((i * w, 0, (i + 1) * w, meta["height"])) for i in range(len(frames))]
        flame = {sprites.EMBER[0]}
        lit = [bool(colours(cell) & set(sprites.EMBER[1:])) for cell in cells]
        self.assertFalse(lit[0], "he starts with an unlit cigarette")
        self.assertTrue(any(colours(cell) & flame for cell in cells[1:-1]), "the lighter's flame")
        self.assertTrue(lit[-1], "the ember glows in the held pose")
        self.assertFalse(colours(cells[-1]) & set(sprites.BRASS), "the lighter is put away")

    def test_clerk_strip_has_the_npc_layout_and_a_green_eyeshade(self):
        with Image.open(ART / "sprites" / "clerk.png") as strip:
            strip = strip.convert("RGBA")
            self.assertEqual(strip.size, (sprites.NPC_W * 11, sprites.FH))
            idle = strip.crop((0, 0, sprites.NPC_W, sprites.FH))
        top = idle.getbbox()[1]
        head = idle.crop((0, top, sprites.NPC_W, top + 10))
        green = [p for p in opaque(head) if p[1] > p[0] + 20 and p[1] > p[2] + 10]
        self.assertTrue(green, "the celluloid visor")

    def test_umbrella_icon_is_a_dark_canopy_on_a_wooden_crook(self):
        with Image.open(ART / "items" / "umbrella.png") as icon:
            icon = icon.convert("RGBA")
            self.assertEqual(icon.size, (32, 24))
        pixels = opaque(icon)
        wood = [p for p in pixels if p[0] > p[2] + 40 and p[0] > 90]
        canopy = [p for p in pixels if max(p[:3]) < 90 and p[2] >= p[0]]
        self.assertGreater(len(wood), 15)
        self.assertGreater(len(canopy), 60)
        self.assertGreater(len({p[:3] for p in canopy}), 3, "folds catch the light, not a flat silhouette")


if __name__ == "__main__":
    unittest.main()
