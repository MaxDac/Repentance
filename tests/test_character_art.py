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
                           ("micah_dressing", sprites.MICAH_DRESSING), ("micah_masked", sprites.MICAH_MASKED),
                           ("micah_no_tie", sprites.MICAH_NO_TIE)):
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

    def test_club_animal_masks_are_distinct_cloaked_figures(self):
        plain = Image.open(ART / "sprites" / "masked_man.png").convert("RGBA")
        npcs = {name: spec for name, spec, *_ in sprites.NPCS}
        for kind in painter.ANIMAL_MASKS:
            name = f"masked_{kind}"
            self.assertIn(name, npcs)
            self.assertEqual(npcs[name]["mask"][:2], ("animal", kind))
            self.assertEqual(npcs[name]["hat"], sprites.MASKED_MAN["hat"], "animal masks keep the cowl")
            image = Image.open(ART / "sprites" / f"{name}.png").convert("RGBA")
            self.assertEqual(image.size, plain.size)
            for column in range(image.width // 56):
                with self.subTest(mask=kind, column=column):
                    box = (column * 56, 0, (column + 1) * 56, 96)
                    frame, base = image.crop(box), plain.crop(box)
                    self.assertNotEqual(frame.crop((0, 0, 56, 34)).tobytes(), base.crop((0, 0, 56, 34)).tobytes(),
                                        "the head must show the animal mask")
                    ys, xs = np.nonzero(np.array(frame.getchannel("A")) > 0)
                    self.assertGreater(ys.min(), 0, "antlers and ears must not clip at the top")
                    self.assertGreater(xs.min(), 0)
                    self.assertLess(xs.max(), 55)
        for kind in ("stag", "hare"):
            image = Image.open(ART / "sprites" / f"masked_{kind}.png").convert("RGBA")
            top = np.nonzero(np.array(image.crop((0, 0, 56, 96)).getchannel("A")) > 0)[0].min()
            plain_top = np.nonzero(np.array(plain.crop((0, 0, 56, 96)).getchannel("A")) > 0)[0].min()
            self.assertLess(top, plain_top, f"the {kind}'s crest must rise above the cowl")

    def test_white_mask_is_a_bauta_half_mask_with_a_long_nose(self):
        self.assertEqual(sprites.MASKED_MAN["mask"][0], "bauta")
        self.assertEqual(sprites.MICAH_MASKED["mask"], sprites.MASKED_MAN["mask"])
        oval = dict(sprites.MASKED_MAN, mask=("full", sprites.MASKED_MAN["mask"][1]))

        def ivory(spec, yaw):
            a = np.array(sprites.figure(spec, sprites.pose(yaw), 64, 96).convert("RGBA"))[:34].astype(int)
            ys, xs = np.nonzero((a[..., 3] > 0) & (a[..., :3].sum(-1) > 450))
            return a, ys, xs

        _, bys, bxs = ivory(sprites.MASKED_MAN, 90)
        _, oys, oxs = ivory(oval, 90)
        self.assertGreater(bxs.max(), oxs.max(), "in profile the nose must stand proud of the plain plate")
        for yaw in (16, sprites.PLAYER_IDLE_YAW, 90):
            with self.subTest(yaw=yaw):
                a, ys, xs = ivory(sprites.MASKED_MAN, yaw)
                _, oys, _ = ivory(oval, yaw)
                self.assertLess(ys.max(), oys.max(), "the Bauta stops under the nose, leaving the chin bare")
                below = a[ys.max() + 1:ys.max() + 4, xs.min():xs.max() + 1]
                skin = (below[..., 3] > 0) & (below[..., 0] - below[..., 2] > 15)
                self.assertTrue(skin.any(), "the bare mouth and chin show under the mask")
                self.assertLess(below[..., :3][skin].sum(-1).max(), 400, "the bare chin sits in shadow")

    def test_player_walk_and_vertical_views_keep_existing_poses(self):
        for name, spec in (("daniel", sprites.DANIEL), ("micah", sprites.MICAH),
                           ("micah_dressing", sprites.MICAH_DRESSING), ("micah_masked", sprites.MICAH_MASKED),
                           ("micah_no_tie", sprites.MICAH_NO_TIE)):
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
        for name in ("micah_masked",):
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
        self.assertEqual(hand[1], elbow[1])
        self.assertEqual(hand[1], 91)
        held = Image.open(ART / "sprites" / "micah_supine.png")
        image = Image.open(ART / "sprites" / "micah_recover.png")
        self.assertEqual(image.crop((0, 0, *held.size)).tobytes(), held.tobytes())

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
        self.assertEqual(sprites.ELEANOR_STAGE["hair_bulge"], 0.0, "no stray hair proud of the chest")
        self.assertEqual(sprites.ELEANOR_STAGE["hair_front_w"], 0.7, "slim but continuous front locks over the chest")

    def test_eleanor_stage_lock_joins_the_back_hair_only_in_profile(self):
        arms = sprites._arms("cover", "side")
        bare = dict(sprites.ELEANOR_STAGE, hair_front_root=0.0)

        def changed(p):
            a = sprites.figure(sprites.ELEANOR_STAGE, p, sprites.NPC_W, sprites.FH)
            b = sprites.figure(bare, p, sprites.NPC_W, sprites.FH)
            return int((np.array(a) != np.array(b)).any(-1).sum())

        self.assertGreater(changed(sprites.npc_walk_pose(arms, 0)), 0, "the root bridges the neck under the jaw")
        self.assertEqual(changed(sprites.pose(35, arms=arms)), 0, "the idle and talk frames stay as they are")

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
        self.assertEqual(spec["hair_bulge"], 0, "the locks lie on the body, no stray hair proud of the chest")
        for phi in (35, 90):
            pose = sprites.pose(phi, arms=sprites._arms("cover", "side"))
            subtle = np.array(sprites.figure(spec, pose, sprites.NPC_W, sprites.FH))
            flat = np.array(sprites.figure(dict(spec, bust_peak=()), pose, sprites.NPC_W, sprites.FH))
            original = np.array(sprites.figure(dict(spec, hair_bulge=0.07), pose, sprites.NPC_W, sprites.FH))
            self.assertFalse(np.array_equal(subtle, flat), "the chest keeps its soft bust curve, not a flat contour")
            self.assertFalse(np.array_equal(subtle, original), "new art must differ from the original large projection")
            def front(img):  # summed forward reach of each row, so the bust peeking past the lock still counts
                rows = img[:, :, 3] == 255
                return sum(int(np.nonzero(r)[0].max()) for r in rows if r.any())
            self.assertLess(front(subtle), front(original),
                            "front silhouette should project less than the original")

    def test_eleanor_club_variants_have_matching_animation_layouts(self):
        nude = Image.open(ART / "sprites" / "eleanor_stage.png")
        dressed = Image.open(ART / "sprites" / "eleanor_stage_clothed.png")
        self.assertEqual(nude.size, (56 * 11, 96))
        self.assertEqual(dressed.size, nude.size)
        self.assertNotEqual(nude.tobytes(), dressed.tobytes())
        for i in range(11):
            self.assertIsNotNone(dressed.crop((i * 56, 0, (i + 1) * 56, 96)).getbbox())

    def test_eleanor_club_variants_wear_the_same_hair(self):
        """Dressed or not, her long hair falls in front over her chest, as in the stage close-up."""
        for key in ("hair", "hair_style", "hair_front", "hair_front_w", "hair_front_root", "hair_back",
                    "hair_back_width", "hair_back_shade", "hair_bulge"):
            with self.subTest(key=key):
                self.assertIn(key, sprites.ELEANOR_STAGE_CLOTHED)
                self.assertEqual(sprites.ELEANOR_STAGE_CLOTHED[key], sprites.ELEANOR_STAGE[key])

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
        for name in ("micah_recover", "micah_kneel_rise",
                     "micah_masked_collapse", "eleanor_sheet_rise"):
            clip = json.loads((ART / "sprites" / f"{name}.json").read_text())
            image = Image.open(ART / "sprites" / f"{name}.png")
            width = clip["width"]
            frames = [image.crop((i * width, 0, (i + 1) * width, clip["height"])).tobytes()
                      for i in range(len(clip["frames"]))]
            self.assertEqual(len(frames), len(set(frames)), name)

    def test_draw_ends_on_the_held_aim(self):
        for prefix in ("micah", "micah_no_tie"):
            with self.subTest(prefix=prefix):
                clip = json.loads((ART / "sprites" / f"{prefix}_draw.json").read_text())
                strip = Image.open(ART / "sprites" / f"{prefix}_draw.png").convert("RGBA")
                aim = Image.open(ART / "sprites" / f"{prefix}_aim.png").convert("RGBA")
                width, height = clip["width"], clip["height"]
                self.assertEqual((width, height), aim.size)
                frames = [strip.crop((i * width, 0, (i + 1) * width, height)).tobytes()
                          for i in range(len(clip["frames"]))]
                self.assertEqual(frames[-1], aim.tobytes(), "the draw lands on the held aim")
                self.assertEqual(len(frames), len(set(frames)), "every step of the draw is its own frame")

    def test_aim_back_steps_blend_between_aim_levels(self):
        back = json.loads((ART / "sprites" / "micah_aim_back.json").read_text())
        lower = json.loads((ART / "sprites" / "micah_aim_lower.json").read_text())
        back_img = Image.open(ART / "sprites" / "micah_aim_back.png").convert("RGBA")
        lower_img = Image.open(ART / "sprites" / "micah_aim_lower.png").convert("RGBA")
        self.assertEqual(back["width"], lower["width"])
        width, height = back["width"], back["height"]
        steps = sprites.AIM_BACK_FRAMES
        runs = len(back["frames"]) // steps
        self.assertEqual(runs * steps, len(back["frames"]))
        self.assertEqual(runs, len(lower["frames"]))
        crop = lambda img, i: img.crop((i * width, 0, (i + 1) * width, height)).tobytes()
        for run in range(runs):
            with self.subTest(run=run):
                frames = [crop(back_img, run * steps + k) for k in range(steps)]
                self.assertEqual(frames[0], crop(lower_img, max(run - 1, 0)), "each step starts at the previous aim")
                self.assertEqual(len(frames), len(set(frames)), "the legs walk through the step")

    def test_mansion_rise_starts_from_the_bed_sprite(self):
        clip = json.loads((ART / "sprites" / "eleanor_mansion_rise.json").read_text())
        strip = Image.open(ART / "sprites" / "eleanor_mansion_rise.png").convert("RGBA")
        self.assertEqual(len(clip["frames"]), 6)
        width, height = clip["width"], clip["height"]
        frames = [strip.crop((i * width, 0, (i + 1) * width, height)).tobytes() for i in range(6)]
        self.assertEqual(len(frames), len(set(frames)))
        source = (ROOT / "scripts" / "Rooms" / "MansionBedroom.cs").read_text(encoding="utf-8")
        self.assertIn('PlayPose("eleanor_mansion_rise")', source)
        self.assertIn("EleanorRise = new(382, 226)", source)

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
            ankle = grounded_joints(joints)[4]
            self.assertEqual(ankle[0], 98)
            if joints == sprites.REST:
                self.assertEqual(ankle[1], 83)
                self.assertEqual(grounded_joints(joints)[6][1], 91)
            elif joints == sprites.KNEEL:
                # the shin rises behind to a foot standing on its tucked toes, which touch the floor under the ankle
                self.assertLess(ankle[1], 91)
                img, _ = sprites.kneeling_figure(dict(sprites.MICAH, h=sprites.MICAH["h"] * sprites.SCALE), joints)
                alpha = img.getchannel("A")
                self.assertTrue(any(alpha.getpixel((x, 91)) == 255 for x in range(94, 99)))
            else:
                self.assertEqual(ankle[1], 91)

    def test_grounded_bodies_are_completely_horizontal(self):
        for joints in (sprites.REST, sprites.HARRINGTON_PRONE):
            hip, shoulder, head, knee, ankle, _, _ = grounded_joints(joints)
            self.assertEqual({point[1] for point in (hip, shoulder, head, knee, ankle)}, {83})

    def test_harrington_drops_to_knees_then_holds_the_same_face_down_frame(self):
        clip = json.loads((ART / "sprites" / "harrington_fall.json").read_text())
        image = Image.open(ART / "sprites" / "harrington_fall.png")
        width, height = clip["width"], clip["height"]
        standing = image.crop(((width - 56) // 2, 0, (width + 56) // 2, height))
        normal = Image.open(ART / "sprites" / "harrington_gown.png").crop((0, 0, 56, 96))
        self.assertEqual(standing.tobytes(), normal.tobytes(), "start without an idle-pose jump")
        self.assertGreater(clip["frames"][1]["head"][1], clip["frames"][0]["head"][1])
        self.assertGreaterEqual(clip["frames"][1]["seconds"], 0.3, "hold the kneeling stage")
        final = image.crop((image.width - width, 0, image.width, height))
        self.assertEqual(final.tobytes(), Image.open(ART / "sprites" / "harrington_shot.png").tobytes())
        self.assertGreater(sprites.HARRINGTON_PRONE[2][0], sprites.HARRINGTON_PRONE[1][0],
                           "right-facing head rotated downward toward the floor")

    def test_sal_knocked_from_behind_kneels_then_lies_face_down(self):
        clip = json.loads((ART / "sprites" / "sal_knockout.json").read_text())
        image = Image.open(ART / "sprites" / "sal_knockout.png")
        width, height = clip["width"], clip["height"]
        standing = image.crop(((width - 56) // 2, 0, (width + 56) // 2, height))
        idle = Image.open(ART / "sprites" / "sal.png").crop((0, 0, 56, 96))
        self.assertEqual(standing.tobytes(), idle.tobytes(), "start from Sal's idle pose")
        heads = [frame["head"] for frame in clip["frames"]]
        self.assertGreater(heads[1][1], heads[0][1], "down on his knees")
        self.assertGreaterEqual(clip["frames"][1]["seconds"], 0.3, "hold the kneeling stage")
        self.assertGreater(heads[-1][0], heads[0][0] + 40, "pitched forward, head to the right")
        final = image.crop((image.width - width, 0, image.width, height))
        self.assertEqual(final.tobytes(), Image.open(ART / "sprites" / "sal_out.png").tobytes())
        self.assertFalse((ART / "sprites" / "sal_supine.png").exists(), "the old on-his-back pose is gone")

    def test_sal_kicks_from_his_idle_pose_and_back(self):
        clip = json.loads((ART / "sprites" / "sal_kick.json").read_text())
        image = Image.open(ART / "sprites" / "sal_kick.png")
        width, height = clip["width"], clip["height"]
        frames = [image.crop((i * width, 0, (i + 1) * width, height)) for i in range(len(clip["frames"]))]
        idle = Image.open(ART / "sprites" / "sal.png").crop((0, 0, 56, 96))
        for at in (0, -1):
            standing = frames[at].crop(((width - 56) // 2, 0, (width + 56) // 2, height))
            self.assertEqual(standing.tobytes(), idle.tobytes(), "start and end on Sal's idle pose")
        self.assertEqual(len({frame.tobytes() for frame in frames[1:4]}), 3, "wind-up, strike and recoil differ")
        strike = np.array(frames[2])[..., 3]
        self.assertGreater(np.nonzero(strike.any(axis=0))[0].max(), width // 2 + 16, "the foot drives out in front")
        self.assertAlmostEqual(sum(f["seconds"] for f in clip["frames"][:2]), 0.45, msg="the toe lands 0.45 s in")

    def test_kicked_micah_doubles_up_and_settles_back_on_his_knees(self):
        clip = json.loads((ART / "sprites" / "micah_kicked.json").read_text())
        image = Image.open(ART / "sprites" / "micah_kicked.png")
        width, height = clip["width"], clip["height"]
        frames = [image.crop((i * width, 0, (i + 1) * width, height)) for i in range(len(clip["frames"]))]
        self.assertEqual(len({frame.tobytes() for frame in frames}), len(frames))
        self.assertEqual(frames[-1].tobytes(), Image.open(ART / "sprites" / "micah_kneel.png").tobytes(),
                         "ends on the held kneeling pose")

    def test_tony_shot_in_the_shoulder_folds_down_onto_his_back(self):
        clip = json.loads((ART / "sprites" / "bartender_fall.json").read_text())
        image = Image.open(ART / "sprites" / "bartender_fall.png").convert("RGBA")
        width, height = clip["width"], clip["height"]
        frames = [image.crop((i * width, 0, (i + 1) * width, height)) for i in range(len(clip["frames"]))]
        idle = Image.open(ART / "sprites" / "bartender.png").crop((0, 0, 56, 96))
        self.assertEqual(frames[0].crop(((width - 56) // 2, 0, (width + 56) // 2, height)).tobytes(), idle.tobytes())
        heads = [frame["head"][1] for frame in clip["frames"]]
        self.assertEqual(heads, sorted(heads), "he only ever goes down")
        self.assertLess(clip["frames"][-1]["head"][0], 96, "on his back, head away from where he faced")
        final = frames[-1]
        self.assertEqual(final.tobytes(), Image.open(ART / "sprites" / "bartender_shot.png").convert("RGBA").tobytes())

        def blood(frame):
            px = np.array(frame).astype(int)
            return np.nonzero((px[..., 3] > 0) & (px[..., 0] > 90) & (px[..., 1] < 40) & (px[..., 2] < 40))

        self.assertEqual(blood(frames[0])[0].size, 0, "no blood before the shot")
        hip, shoulder = grounded_joints(sprites.SHOULDER_SHOT[-1])[:2]
        ys, xs = blood(final)
        self.assertGreater(xs.size, 10)
        self.assertLess(abs(xs.mean() - shoulder[0]), abs(xs.mean() - hip[0]), "the wound is at the shoulder")
        ankle = grounded_joints(sprites.SHOULDER_SHOT[-1])[4]
        self.assertLess(xs.max(), (shoulder[0] + ankle[0]) / 2, "no blood down the legs")

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

    def test_kneeling_rise_pushes_up_forward_from_the_planted_foot(self):
        keys = [sprites.KNEEL, sprites.KNEEL_PUSH, sprites.KNEEL_BACK, sprites.KNEE_UP, sprites.PUSH_OFF,
                sprites.NEARLY_UP]
        for i, joints in enumerate(keys):
            with self.subTest(key=i):
                hip, shoulder, head = grounded_joints(joints)[:3]
                self.assertEqual(grounded_joints(joints)[4][0], 98, "the near foot stays planted")
                self.assertGreaterEqual(shoulder[0], hip[0], "the trunk never leans back")
                self.assertGreaterEqual(head[0], shoulder[0] - 1, "the head stays over or ahead of the shoulders")
        hips = [grounded_joints(k)[0][1] for k in keys[2:]]
        self.assertEqual(hips[1:], sorted(hips[1:], reverse=True), "once kneeling up, the hips only rise")
        for joints in keys[3:]:
            fknee, fankle, fheel, ftoe = joints[7:11]
            self.assertEqual((fheel[1], ftoe[1]), (90, 91), "the raised far foot stands flat on the floor")

    def test_kneeling_rise_has_no_red_tie_streak_until_it_turns_to_idle(self):
        tie = next(d[5] for d in sprites.MICAH["decals"] if d[0] == "strip" and d[3] == 0.007)
        red = np.array([int(tie[i:i + 2], 16) for i in (0, 2, 4)])
        clip = json.loads((ART / "sprites" / "micah_kneel_rise.json").read_text())
        strip = Image.open(ART / "sprites" / "micah_kneel_rise.png").convert("RGBA")
        width, height = clip["width"], clip["height"]
        for i in range(len(clip["frames"]) - 2):
            with self.subTest(frame=i):
                frame = np.array(strip.crop((i * width, 0, (i + 1) * width, height)))
                pixels = frame[frame[..., 3] > 0][:, :3].astype(int)
                self.assertFalse((np.abs(pixels - red).sum(axis=1) < 30).any())

    def test_kneeling_micah_is_on_knees_and_forearms_without_a_red_tie_streak(self):
        hip, shoulder, head, knee, ankle, elbow, hand = sprites.KNEEL
        self.assertLess(knee[1] - hip[1], 20)
        self.assertGreater(knee[1] - hip[1], 14, "hips raised over the knees")
        self.assertLess(abs(elbow[0] - shoulder[0]), 3, "elbows planted under the shoulders")
        self.assertEqual(elbow[1], hand[1], "forearms flat on the floor")
        self.assertGreater(hand[0], elbow[0] + 8, "forearms reaching forward")
        self.assertGreater(shoulder[1], hip[1], "shoulders lower than the hips")
        self.assertLessEqual(head[1], shoulder[1], "head lifted clear of the forearms")
        spec = dict(sprites.MICAH, h=sprites.MICAH["h"] * sprites.SCALE)
        tie = next(d[5] for d in sprites.MICAH["decals"] if d[0] == "strip" and d[3] == 0.007)
        img, _ = sprites.kneeling_figure(spec, sprites.KNEEL)
        pixels = np.array(img.convert("RGB")).reshape(-1, 3).astype(int)
        red = np.array([int(tie[i:i + 2], 16) for i in (0, 2, 4)])
        self.assertFalse((np.abs(pixels - red).sum(axis=1) < 30).any(), "tie painted along the bent-over trunk")

    def test_micah_without_his_tie_after_the_alarm_bell(self):
        tie = next(d[5] for d in sprites.MICAH["decals"] if d[0] == "strip" and d[3] == 0.007)
        red = np.array([int(tie[i:i + 2], 16) for i in (0, 2, 4)])

        def has_tie(path):
            pixels = np.array(Image.open(path).convert("RGBA")).reshape(-1, 4).astype(int)
            pixels = pixels[pixels[:, 3] == 255][:, :3]
            return (np.abs(pixels - red).sum(axis=1) < 40).any()

        self.assertTrue(has_tie(ART / "sprites" / "micah.png"))
        self.assertTrue(has_tie(ART / "sprites" / "micah_draw.png"))
        for name in ("micah_no_tie",) + tuple(f"micah_no_tie_{pose}" for pose in sprites.NO_TIE_POSES):
            with self.subTest(sprite=name):
                self.assertTrue((ART / "sprites" / f"{name}.png").is_file())
                self.assertFalse(has_tie(ART / "sprites" / f"{name}.png"), "the tie is left on the bell")
        for pose in sprites.NO_TIE_POSES:
            with self.subTest(pose=pose):
                shared = json.loads((ART / "sprites" / f"micah_{pose}.json").read_text())
                variant = json.loads((ART / "sprites" / f"micah_no_tie_{pose}.json").read_text())
                self.assertEqual([f["seconds"] for f in shared["frames"]], [f["seconds"] for f in variant["frames"]])
                self.assertEqual((shared["width"], shared["height"]), (variant["width"], variant["height"]))
        # the collar parts at the throat over bare skin, front on
        front = np.array(Image.open(ART / "sprites" / "micah_no_tie.png").convert("RGB").crop((0, 96, 64, 192))).astype(int)
        tied = np.array(Image.open(ART / "sprites" / "micah.png").convert("RGB").crop((0, 96, 64, 192))).astype(int)
        skin = np.array([int(sprites.MICAH["skin"][i:i + 2], 16) for i in (0, 2, 4)])
        throat = lambda img: (np.abs(img[30:40, 26:38] - skin).sum(axis=2) < 60).sum()
        self.assertGreater(throat(front), throat(tied) + 4, "an open collar shows skin at the throat")

    def test_motel_sleeper_stays_painted_in_the_bed(self):
        source = (ROOT / "scripts" / "Rooms" / "MotelNight.cs").read_text(encoding="utf-8")
        self.assertNotIn("eleanor_sheet_rise", source)
        self.assertNotIn("eleanor_bed_turn", source)
        night = np.array(Image.open(ART / "rooms" / "motel_night.png").convert("RGB"))
        rails = np.array(Image.open(ART / "rooms" / "motel_night_rails.png").convert("RGB"))
        pillow = np.abs(night[140:175, 90:150].astype(int) - rails[140:175, 90:150].astype(int)).sum()
        self.assertGreater(pillow, 400, "the painted sleeper is missing from the pillow")

    def test_motel_sleeper_talks_with_her_lips_in_place(self):
        strip = Image.open(ART / "rooms" / "motel_eleanor_talk.png").convert("RGB")
        night = Image.open(ART / "rooms" / "motel_night.png").convert("RGB")
        scene = (ROOT / "scenes" / "rooms" / "motel_night.tscn").read_text(encoding="utf-8")
        self.assertIn('Mouth = NodePath("../EleanorMouth")', scene)
        self.assertIn("res://assets/art/rooms/motel_eleanor_talk.png", scene)
        node = scene.split('[node name="EleanorMouth"', 1)[1].split("[node", 1)[0]
        self.assertIn("hframes = 3", node)
        self.assertIn('HideIfFlags = "interlude1,interlude2"', node)
        x, y = (int(v) for v in node.split("position = Vector2(", 1)[1].split(")", 1)[0].split(", "))
        self.assertEqual(strip.width % 3, 0)
        w, h = strip.width // 3, strip.height
        self.assertLessEqual(w * h, 64, "only the lips move, not the whole face")
        frames = [strip.crop((k * w, 0, (k + 1) * w, h)).tobytes() for k in range(3)]
        self.assertEqual(frames[0], night.crop((x, y, x + w, y + h)).tobytes(), "frame 0 is the painted room")
        self.assertEqual(len(set(frames)), 3, "closed, open and half-open lips are all distinct")

    def test_eleanor_talking_only_opens_her_lips_in_place(self):
        image = np.array(Image.open(ART / "sprites" / "eleanor_play.png").convert("RGBA"))
        frame = lambda row, col: image[row * 96:(row + 1) * 96, col * 64:(col + 1) * 64]
        columns = []
        for row, talk in ((0, 9), (1, 7), (1, 8)):
            with self.subTest(row=row, talk=talk):
                ys, xs = np.nonzero((frame(row, 0) != frame(row, talk)).any(axis=2))
                self.assertGreater(len(xs), 0)
                self.assertLessEqual(xs.max() - xs.min(), 1, "the open mouth stays as narrow as the closed lips")
                self.assertLessEqual(ys.max() - ys.min(), 2, "no nod, tilt or squash of the head")
                if row == 1:
                    columns.append(set(xs.tolist()))
        self.assertEqual(columns[0], columns[1], "both talk frames open the same lips, not a shifted mouth")

    def test_eleanor_nape_is_covered_and_pearls_follow_the_neck(self):
        image = np.array(Image.open(ART / "sprites" / "eleanor_play.png").convert("RGBA")).astype(int)
        frame = lambda row, col: image[row * 96:(row + 1) * 96, col * 64:(col + 1) * 64]
        skin = np.array([int(sprites.ELEANOR["skin"][i:i + 2], 16) for i in (0, 2, 4)])
        pearl, shade = np.array([0xf2, 0xee, 0xe4]), np.array([0xb8, 0xb0, 0xa4])
        near = lambda f, col, tol=40: (np.abs(f[..., :3] - col).sum(axis=2) < tol) & (f[..., 3] == 255)
        for col in range(1, 9):
            with self.subTest(walk=col):
                f = frame(0, col)
                bare = near(f, skin, 120) & ~near(f, pearl) & ~near(f, shade)
                self.assertFalse(bare[34:46, :34].any(), "no bare nape behind the high-necked bodice")
                self.assertTrue(near(f, pearl)[33:46].any(), "the strand shows over her near shoulder")
        front = near(frame(1, 0), pearl)[33:46]
        xs = np.nonzero(front)[1]
        self.assertTrue((xs <= 30).any() and (xs >= 34).any(), "the strand rounds both sides of the neck")
        self.assertFalse(near(frame(2, 0), pearl).any(), "no pearls seen from behind")

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
        width = 64 if path.stem in ("micah", "daniel", "micah_dressing", "micah_masked", "micah_no_tie",
                                    "micah_hatless_bottle") else 56
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
