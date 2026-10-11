"""Focused generated-character checks and local visual review artifacts (no additional test dependencies)."""
import argparse
import json
import sys
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from art import sprites
from art.figure import action_figure, grounded_joints

ART = ROOT / "assets" / "art"


class CharacterArtTests(unittest.TestCase):
    def test_action_contracts(self):
        for path in (ART / "sprites").glob("*.json"):
            with self.subTest(clip=path.stem):
                clip = json.loads(path.read_text())
                image = Image.open(path.with_suffix(".png")).convert("RGBA")
                width, height = clip["width"], clip["height"]
                self.assertEqual(image.size, (width * len(clip["frames"]), height))
                contact = clip["frames"][0]["anchor"]
                for index, data in enumerate(clip["frames"]):
                    frame = image.crop((index * width, 0, (index + 1) * width, height))
                    opaque = np.array(frame.getchannel("A")) >= 250
                    ys, xs = np.nonzero(opaque)
                    self.assertGreater(len(xs), 0)
                    self.assertGreater(xs.min(), 0, "left-edge clipping")
                    self.assertLess(xs.max(), width - 1, "right-edge clipping")
                    self.assertGreater(ys.min(), 0, "top-edge clipping")
                    self.assertLess(ys.max(), height - 1, "bottom-edge clipping")
                    self.assertEqual(data["anchor"], contact)
                    self.assertTrue(0 <= data["head"][0] < width and 0 <= data["head"][1] < height)
                    self.assertGreater(data["seconds"], 0)
                    bounds = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1),
                              int(ys.max() - ys.min() + 1)]
                    self.assertEqual(data["bounds"], bounds)

    def test_distinct_intermediate_frames(self):
        for name in ("micah_collapse", "micah_recover", "micah_kneel_rise",
                     "micah_masked_collapse", "eleanor_sheet_rise"):
            clip = json.loads((ART / "sprites" / f"{name}.json").read_text())
            image = Image.open(ART / "sprites" / f"{name}.png")
            width = clip["width"]
            frames = [image.crop((i * width, 0, (i + 1) * width, clip["height"])).tobytes()
                      for i in range(len(clip["frames"]))]
            self.assertEqual(len(frames), len(set(frames)), name)

    def test_recovery_rejoins_normal_sheet(self):
        normal = Image.open(ART / "sprites" / "micah.png").crop((0, 0, 64, 96))
        for name in ("micah_recover", "micah_kneel_rise"):
            image = Image.open(ART / "sprites" / f"{name}.png")
            final = image.crop((image.width - 128, 0, image.width - 64, 96))
            self.assertEqual(final.tobytes(), normal.tobytes())

    def test_generation_is_deterministic(self):
        spec = dict(sprites.MICAH, h=sprites.MICAH["h"] * sprites.SCALE)
        a, ah = action_figure(spec, sprites.SIT)
        b, bh = action_figure(spec, sprites.SIT)
        self.assertEqual(a.tobytes(), b.tobytes())
        self.assertEqual(ah, bh)

    def test_ground_contact_does_not_skate(self):
        for joints in sprites.FALL + [sprites.SIT, sprites.CROUCH, sprites.HALF_UP, sprites.KNEEL]:
            self.assertEqual(tuple(grounded_joints(joints)[4]), (98, 91))

    def test_kneeling_rise_starts_from_the_actual_held_pose(self):
        held = Image.open(ART / "sprites" / "micah_kneel.png")
        rise = Image.open(ART / "sprites" / "micah_kneel_rise.png")
        self.assertEqual(held.tobytes(), rise.crop((0, 0, *held.size)).tobytes())

    def test_motel_foreground_is_a_transparent_rail_layer(self):
        rails = Image.open(ART / "rooms" / "motel_night_rails.png")
        self.assertEqual(rails.size, (480, 270))
        self.assertEqual(rails.mode, "RGBA")
        alpha = np.array(rails.getchannel("A"))
        self.assertGreater(np.count_nonzero(alpha), 0)
        self.assertLess(np.count_nonzero(alpha), 2500)
        self.assertEqual(alpha[119, 102], 0, "Eleanor's final head is outside the near rail")
        clip = json.loads((ART / "sprites" / "eleanor_sheet_rise.json").read_text())
        for frame in clip["frames"]:
            x = round(110 + frame["head"][0] - frame["anchor"][0])
            y = round(194 + frame["head"][1] - frame["anchor"][1])
            self.assertEqual(alpha[y, x], 0, "a bedpost must not cover Eleanor's head")


def artifacts(destination):
    destination.mkdir(parents=True, exist_ok=True)
    before = destination / "sprites-before"
    paths = sorted((ART / "sprites").glob("*.png"))
    models = [p for p in paths if not p.with_suffix(".json").exists()]
    contact = Image.new("RGB", (350, len(models) * 108), "#282834")
    draw = ImageDraw.Draw(contact)
    for row, path in enumerate(models):
        width = 64 if path.stem in ("micah", "daniel", "micah_dressing", "micah_masked") else 56
        draw.text((4, row * 108 + 8), path.stem, fill="#e4ddcc")
        for x, source in ((150, before / path.name), (250, path)):
            if source.exists():
                img = Image.open(source).convert("RGBA").crop((0, 0, width, 96))
                contact.paste(img, (x, row * 108 + 4), img)
    contact.save(destination / "characters-before-after.png")
    contact.resize((700, contact.height * 2), Image.Resampling.NEAREST).save(destination / "characters-enlarged.png")
    background = Image.open(ART / "rooms" / "motel_night.png").convert("RGBA")
    rails = Image.open(ART / "rooms" / "motel_night_rails.png")
    clip = json.loads((ART / "sprites" / "eleanor_sheet_rise.json").read_text())
    strip = Image.open(ART / "sprites" / "eleanor_sheet_rise.png")
    rooms = Image.new("RGB", (480 * 3, 270 * ((len(clip["frames"]) + 2) // 3)))
    for i, frame in enumerate(clip["frames"]):
        room = background.copy()
        pose = strip.crop((128 * i, 0, 128 * (i + 1), 104))
        if i >= 4:
            room.alpha_composite(rails)
        room.alpha_composite(pose, (110 - int(frame["anchor"][0]), 194 - int(frame["anchor"][1])))
        if i < 4:
            room.alpha_composite(rails)
        rooms.paste(room, ((i % 3) * 480, (i // 3) * 270))
    rooms.save(destination / "motel-rise-frames.png")
    for path in (ART / "sprites").glob("*.json"):
        image = Image.open(path.with_suffix(".png")).convert("RGBA")
        review = Image.new("RGBA", image.size, "#282834")
        review.alpha_composite(image)
        review.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST).save(destination / f"{path.stem}-enlarged.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path)
    args = parser.parse_args()
    if args.artifacts:
        artifacts(args.artifacts)
    unittest.main(argv=[sys.argv[0]])
