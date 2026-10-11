"""Focused generated-character checks and local visual review artifacts (no additional test dependencies)."""
import argparse
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from art import sprites
from art.figure import action_figure, grounded_joints
import art.figure as painter

ART = ROOT / "assets" / "art"


class CharacterArtTests(unittest.TestCase):
    def test_player_horizontal_idle_and_talk_use_three_quarter_art(self):
        self.assertGreater(sprites.PLAYER_IDLE_YAW, 45)
        self.assertLess(sprites.PLAYER_IDLE_YAW, 75)
        for name, spec in (("daniel", sprites.DANIEL), ("micah", sprites.MICAH),
                           ("micah_dressing", sprites.MICAH_DRESSING), ("micah_masked", sprites.MICAH_MASKED)):
            image = Image.open(ART / "sprites" / f"{name}.png").convert("RGBA")
            self.assertEqual(image.size, (640, 288))
            for column, extra in ((0, {}), (9, dict(mouth=1, nod=0.004))):
                with self.subTest(character=name, column=column):
                    actual = image.crop((column * 64, 0, (column + 1) * 64, 96))
                    expected = sprites.figure(spec, sprites.pose(sprites.PLAYER_IDLE_YAW, **extra), 64, 96)
                    profile = sprites.figure(spec, sprites.pose(90, **extra), 64, 96)
                    self.assertEqual(actual.tobytes(), expected.tobytes())
                    self.assertNotEqual(actual.crop((0, 0, 64, 30)).tobytes(),
                                        profile.crop((0, 0, 64, 30)).tobytes(),
                                        "the face must visibly change, not just the body")
                    ys, xs = np.nonzero(np.array(actual.getchannel("A")) == 255)
                    self.assertGreater(xs.min(), 0)
                    self.assertLess(xs.max(), 63)
                    self.assertGreater(ys.min(), 0)
                    self.assertEqual(ys.max(), 93, "keep the soles at the existing baseline")
            idle = np.array(image.crop((0, 0, 64, 96)))
            talk = np.array(image.crop((576, 0, 640, 96)))
            self.assertTrue(np.array_equal(idle[31:], talk[31:]),
                            "talking must not move the body or feet")

    def test_player_walk_and_vertical_views_keep_existing_poses(self):
        for name, spec in (("daniel", sprites.DANIEL), ("micah", sprites.MICAH),
                           ("micah_dressing", sprites.MICAH_DRESSING), ("micah_masked", sprites.MICAH_MASKED)):
            image = Image.open(ART / "sprites" / f"{name}.png").convert("RGBA")
            poses = [(0, i + 1, sprites.walk_pose(90, i)) for i in range(8)]
            for row, yaw in ((1, 16), (2, 164)):
                poses.append((row, 0, sprites.pose(yaw)))
                poses += [(row, i + 1, sprites.walk_pose(yaw, i * 8 / 6, amp=0.8)) for i in range(6)]
            poses += [(1, 7, sprites.pose(16, mouth=1)), (1, 8, sprites.pose(16, mouth=2, nod=0.004))]
            for row, column, ps in poses:
                with self.subTest(character=name, row=row, column=column):
                    frame = image.crop((column * 64, row * 96, (column + 1) * 64, (row + 1) * 96))
                    self.assertEqual(frame.tobytes(), sprites.figure(spec, ps, 64, 96).tobytes())

    def test_collapse_starts_from_the_actual_player_idle(self):
        for name in ("micah", "micah_masked"):
            normal = Image.open(ART / "sprites" / f"{name}.png").convert("RGBA").crop((0, 0, 64, 96))
            collapse = Image.open(ART / "sprites" / f"{name}_collapse.png").convert("RGBA")
            self.assertEqual(collapse.crop((64, 0, 128, 96)).tobytes(), normal.tobytes())

    def test_player_sheet_generation_is_deterministic(self):
        for name, spec in (("daniel", sprites.DANIEL), ("micah", sprites.MICAH)):
            with patch.object(sprites, "save"):
                first = sprites.player_sheet(spec, name)
                second = sprites.player_sheet(spec, name)
            self.assertEqual(first.tobytes(), second.tobytes())

    def test_resting_arm_lies_along_the_ground(self):
        _, shoulder, _, _, ankle, elbow, hand = sprites.REST
        self.assertGreater(elbow[1], shoulder[1])
        self.assertLessEqual(ankle[1] - elbow[1], 2)
        self.assertEqual(hand[1], ankle[1])
        held = Image.open(ART / "sprites" / "micah_supine.png")
        for name in ("micah_collapse", "micah_recover"):
            image = Image.open(ART / "sprites" / f"{name}.png")
            frame = image.crop((image.width - held.width, 0, image.width, held.height)) \
                if name.endswith("collapse") else image.crop((0, 0, *held.size))
            self.assertEqual(frame.tobytes(), held.tobytes(), name)

    def test_strapless_club_dresses_have_no_ribbon_spikes(self):
        for spec in (sprites.MASKED_WOMAN, sprites.MASKED_WOMAN_B, sprites.ELEANOR_STAGE_CLOTHED):
            self.assertFalse(any(decal[0] == "ribbon" for decal in spec["decals"]))
            self.assertEqual(spec["neckline"], 0.262)

    def test_supine_coat_covers_the_base_of_the_neck(self):
        image = np.array(Image.open(ART / "sprites" / "micah_supine.png").convert("RGBA"))
        shoulder = grounded_joints(sprites.REST)[1].astype(int)
        x, y = shoulder
        patch = image[y - 2:y + 2, x - 2:x + 3, :3]
        skin = painter.ramp(sprites.MICAH["skin"])
        self.assertFalse(np.any(np.all(patch[:, :, None] == skin, axis=3)),
                         "the coat collar must cover the shoulder rather than expose a skin patch")

    def test_eleanor_marked_back_hair_patch_is_darker(self):
        spec = sprites.ELEANOR_STAGE
        pose = sprites.pose(35, arms=sprites._arms("cover", "side"))
        before = np.array(sprites.figure(dict(spec, hair_back_shade=0), pose, sprites.NPC_W, sprites.FH))
        after = np.array(sprites.figure(spec, pose, sprites.NPC_W, sprites.FH))
        self.assertTrue(np.array_equal(before[:, :, 3], after[:, :, 3]), "shading must not change the silhouette")
        changed = np.any(before[:, :, :3] != after[:, :, :3], axis=2)
        self.assertGreater(np.count_nonzero(changed), 0)
        self.assertLess(after[changed, :3].mean(), before[changed, :3].mean(),
                        "darken the bright back-hair patch without lifting the dark underside")
        hair_palette = painter.ramp(spec["hair"])
        for image in (before, after):
            self.assertTrue(np.all(np.any(np.all(image[changed, None, :3] == hair_palette, axis=2), axis=1)),
                            "only hair pixels should change color")

    def test_eleanor_back_hair_has_a_little_more_volume(self):
        paint = painter._long_hair_back
        edges = []

        def record(canvas, *args):
            paint(canvas, *args)
            edges.append(np.nonzero(canvas.parts_mask("hairback"))[1].min())

        pose = sprites.pose(35, arms=sprites._arms("cover", "side"))
        with patch.object(painter, "_long_hair_back", side_effect=record):
            sprites.figure(dict(sprites.ELEANOR_STAGE, hair_back_width=1.0), pose, sprites.NPC_W, sprites.FH)
            sprites.figure(sprites.ELEANOR_STAGE, pose, sprites.NPC_W, sprites.FH)
        self.assertLess(edges[1], edges[0])
        self.assertLessEqual(edges[0] - edges[1], 2, "add only a pixel or two along the back edge")

    def test_eleanor_back_hair_is_slightly_longer(self):
        paint = painter._long_hair_back
        bottoms = []

        def record(canvas, *args):
            paint(canvas, *args)
            bottoms.append(np.nonzero(canvas.parts_mask("hairback"))[0].max())

        pose = sprites.pose(35, arms=sprites._arms("cover", "side"))
        with patch.object(painter, "_long_hair_back", side_effect=record):
            sprites.figure(dict(sprites.ELEANOR_STAGE, hair_back=0.29), pose, sprites.NPC_W, sprites.FH)
            sprites.figure(sprites.ELEANOR_STAGE, pose, sprites.NPC_W, sprites.FH)
        self.assertGreater(bottoms[1], bottoms[0])
        self.assertLessEqual(bottoms[1] - bottoms[0], 3, "extend the back only slightly")
        self.assertEqual(sprites.ELEANOR_STAGE["hair_front"], 0.34)
        self.assertEqual(sprites.ELEANOR_STAGE["hair_bulge"], 0.03)

    def test_eleanor_front_locks_remain_in_all_animation_frames(self):
        original = painter._hair_front
        checks = []

        def check_lock(canvas, *args):
            existing_hair = canvas.parts_mask("hair").copy()
            original(canvas, *args)
            new_hair = canvas.parts_mask("hair") & ~existing_hair
            checks.append(np.count_nonzero(new_hair))

        with patch.object(painter, "_hair_front", side_effect=check_lock):
            arms = sprites._arms("cover", "side")
            poses = [sprites.pose(35, arms=arms), sprites.pose(35, arms=arms, mouth=1),
                     sprites.pose(35, arms=arms, mouth=2, nod=0.004)]
            poses += [sprites.npc_walk_pose(arms, i) for i in range(8)]
            for pose in poses:
                sprites.figure(sprites.ELEANOR_STAGE, pose, sprites.NPC_W, sprites.FH)
        self.assertEqual(len(checks), 11)
        self.assertTrue(all(count > 0 for count in checks), "retain front-hair coverage in every view")

    def test_eleanor_hair_bump_is_smaller_than_the_original(self):
        spec = sprites.ELEANOR_STAGE
        self.assertEqual(spec["hair_front"], 0.34)
        self.assertGreater(spec["hair_bulge"], 0)
        self.assertLess(spec["hair_bulge"], 0.07)
        for phi in (35, 90):
            pose = sprites.pose(phi, arms=sprites._arms("cover", "side"))
            subtle = np.array(sprites.figure(spec, pose, sprites.NPC_W, sprites.FH))
            flat = np.array(sprites.figure(dict(spec, hair_bulge=0), pose, sprites.NPC_W, sprites.FH))
            original = np.array(sprites.figure(dict(spec, hair_bulge=0.07), pose, sprites.NPC_W, sprites.FH))
            self.assertFalse(np.array_equal(subtle, flat), "new art must differ from the rejected flat contour")
            self.assertFalse(np.array_equal(subtle, original), "new art must differ from the original large projection")
            self.assertLess(np.nonzero(subtle[:, :, 3] == 255)[1].max(),
                            np.nonzero(original[:, :, 3] == 255)[1].max(),
                            "front silhouette should project less than the original")

    def test_eleanor_club_variants_have_matching_animation_layouts(self):
        nude = Image.open(ART / "sprites" / "eleanor_stage.png")
        dressed = Image.open(ART / "sprites" / "eleanor_stage_clothed.png")
        self.assertEqual(nude.size, (56 * 11, 96))
        self.assertEqual(dressed.size, nude.size)
        self.assertNotEqual(nude.tobytes(), dressed.tobytes())
        for i in range(11):
            self.assertIsNotNone(dressed.crop((i * 56, 0, (i + 1) * 56, 96)).getbbox())

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

    def test_door_reach_is_the_idle_pose_then_an_extended_arm(self):
        for name, spec, yaw in (("micah_open_door", sprites.MICAH, sprites.PLAYER_IDLE_YAW),
                                ("teddy_open_door", sprites.TEDDY, 35),
                                ("rose_open_door", sprites.ROSE, 20)):
            clip = json.loads((ART / "sprites" / f"{name}.json").read_text())
            image = Image.open(ART / "sprites" / f"{name}.png").convert("RGBA")
            width, height = clip["width"], clip["height"]
            frames = [image.crop((i * width, 0, (i + 1) * width, height)) for i in range(4)]
            expected = sprites.figure(spec, sprites.pose(yaw), width, height)
            self.assertEqual(frames[0].tobytes(), expected.tobytes(), name)
            self.assertEqual(frames[3].tobytes(), frames[0].tobytes(), name)
            idle_right = np.nonzero(np.array(frames[0].getchannel("A")) >= 250)[1].max()
            reach_right = np.nonzero(np.array(frames[1].getchannel("A")) >= 250)[1].max()
            self.assertGreater(reach_right, idle_right + 6, name)
            self.assertNotEqual(frames[1].tobytes(), frames[2].tobytes(), name)

    def test_harrington_fall_topples_without_leaving_the_frame(self):
        clip = json.loads((ART / "sprites" / "harrington_fall.json").read_text())
        image = Image.open(ART / "sprites" / "harrington_fall.png").convert("RGBA")
        width, height = clip["width"], clip["height"]
        self.assertGreater(width, 64)
        spans = []
        for index in range(len(clip["frames"])):
            frame = image.crop((index * width, 0, (index + 1) * width, height))
            ys, xs = np.nonzero(np.array(frame.getchannel("A")) >= 250)
            spans.append(int(xs.max() - xs.min()))
            self.assertGreater(xs.min(), 0)
            self.assertLess(xs.max(), width - 1)
        self.assertGreater(spans[-1], spans[0] + 12, "the last frame should be the body gone over")

    def test_kneeling_rise_starts_from_the_actual_held_pose(self):
        held = Image.open(ART / "sprites" / "micah_kneel.png")
        rise = Image.open(ART / "sprites" / "micah_kneel_rise.png")
        self.assertEqual(held.tobytes(), rise.crop((0, 0, *held.size)).tobytes())

    def test_motel_sleeper_stays_painted_in_the_bed(self):
        source = (ROOT / "scripts" / "Rooms" / "MotelNight.cs").read_text(encoding="utf-8")
        self.assertNotIn("eleanor_sheet_rise", source)
        self.assertNotIn("eleanor_bed_turn", source)
        night = np.array(Image.open(ART / "rooms" / "motel_night.png").convert("RGB"))
        rails = np.array(Image.open(ART / "rooms" / "motel_night_rails.png").convert("RGB"))
        pillow = np.abs(night[140:175, 90:150].astype(int) - rails[140:175, 90:150].astype(int)).sum()
        self.assertGreater(pillow, 400, "the painted sleeper is missing from the pillow")

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
