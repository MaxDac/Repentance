"""Final PNG, lighting and state-composition contracts for the screenshot corrections."""
import contextlib
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import act2_rooms, attic, common, library, mansion, motel, outskirts


def luminance(image):
    return ImageStat.Stat(image.convert("L")).mean[0]


class SceneImprovementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            for build in (motel.build, attic.build, library.build, act2_rooms.build_rose,
                          mansion.build_study, mansion.build_bedroom, mansion.build_exterior, outskirts.build):
                build()

    def assert_image_equal(self, a, b):
        self.assertEqual(a.size, b.size)
        difference = ImageChops.difference(a.convert("RGBA"), b.convert("RGBA"))
        self.assertTrue(all(channel.getbbox() is None for channel in difference.split()))

    def test_committed_pngs_match_the_painters(self):
        for path in self.generated.rglob("*.png"):
            relative = path.relative_to(self.generated)
            with self.subTest(asset=str(relative)), Image.open(path) as generated, \
                    Image.open(ROOT / "assets" / "art" / relative) as committed:
                self.assert_image_equal(generated, committed)

    def test_motel_mirrors_have_rectangular_frames(self):
        image = Image.new("RGB", (480, 240))
        for box in ((126, 16, 160, 47), (210, 53, 254, 86)):
            motel.wall_mirror(image, box)
            x0, y0, x1, y1 = box
            for x, y in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                self.assertEqual(image.getpixel((x, y)), common.hx("b0aaa0"))
            self.assertTrue(np.all(np.asarray(image)[y0, x0:x1 + 1] == common.hx("b0aaa0")))

    def test_motel_curtains_cover_the_window_bars(self):
        expected = Image.new("RGB", (480, 240))
        motel.curtains(expected, night=True)
        actual = Image.new("RGB", (480, 240))
        motel.glass_night(actual)
        for x in (310, 389):
            for y in (58, 65, 90):
                self.assertEqual(actual.getpixel((x, y)), expected.getpixel((x, y)))
        self.assertGreaterEqual(len(expected.crop((292, 26, 316, 96)).getcolors(2000)), 3)

    def test_attic_bulb_is_bright_in_every_final_background(self):
        for name in ("attic_act1", "attic_act2", "attic_act3", "attic_night"):
            with self.subTest(state=name), Image.open(self.generated / "rooms" / f"{name}.png") as image:
                bulb = luminance(image.crop((258, 33, 263, 39)))
                nearby = luminance(image.crop((245, 32, 250, 38)))
                self.assertGreater(bulb, 200)
                self.assertGreater(bulb - nearby, 60)

    def test_night_bulb_lights_the_gable_not_just_the_standing_lamp(self):
        image = attic.paint_night()
        self.assertGreater(luminance(image.crop((208, 46, 228, 64))), 45)
        self.assertGreater(luminance(image.crop((208, 46, 228, 64))),
                           luminance(image.crop((20, 46, 40, 64))) + 15)

    def test_library_hearth_has_no_flames_or_fire_glow(self):
        image = Image.new("RGB", (480, 240))
        library.fireplace(image)
        hearth = np.asarray(image.crop((188, 72, 290, 153))).astype(int)
        self.assertLess(hearth.max(), 150)
        self.assertLess(luminance(image.crop((216, 120, 272, 138))), 35)

    def test_books_have_separate_spines_and_binding_detail(self):
        image = Image.new("RGB", (100, 30))
        library.book_rows(ImageDraw.Draw(image), 0, 2, 99, 28, 7)
        self.assertGreater(len(image.getcolors(3000)), 16)
        row = np.asarray(image)[15]
        self.assertGreater(np.count_nonzero(np.all(row == 0, axis=1)), 8)
        self.assertGreater(np.count_nonzero(np.all(np.asarray(image) == common.hx("c8a25a"), axis=2)), 5)

    def test_road_window_and_floor_are_character_scaled(self):
        x0, y0, x1, y1 = act2_rooms.ROAD_WINDOW
        self.assertGreaterEqual(y1 - y0, 70)
        self.assertGreaterEqual(200 - act2_rooms.LANDING_Y, 90)
        self.assertLessEqual(200 - act2_rooms.LANDING_Y, 115)
        self.assertGreaterEqual(x1 - x0, 40)
        for freed, bottom in ((False, 156), (True, 196)):
            image = Image.new("RGB", (480, 270))
            act2_rooms.fire_escape(ImageDraw.Draw(image), freed)
            self.assertNotEqual(image.getpixel((328, bottom)), (0, 0, 0))
            self.assertEqual(image.getpixel((328, bottom + 1)), (0, 0, 0))

    def test_trash_flames_keep_orange_shells_and_bright_cores(self):
        image = Image.open(ROOT / "assets" / "art" / "rooms" / "harrington_road_fire.png")
        scene = (ROOT / "scenes" / "rooms" / "harrington_road.tscn").read_text()
        fire_node = re.search(r'\[node name="Fire"[^\]]*\]([^\[]*)', scene)[1]
        x, y = map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", fire_node).groups())
        composed = Image.open(ROOT / "assets" / "art" / "rooms" / "harrington_road.png").copy()
        composed.paste(image, (x, y))
        image = composed
        fire = np.asarray(image.crop((37, 135, 68, 174))).astype(int)
        self.assertGreater(np.count_nonzero((fire[:, :, 0] > 200) & (fire[:, :, 1] > 180)), 10)
        self.assertGreater(np.count_nonzero((fire[:, :, 0] > 180) & (fire[:, :, 1] < 160)), 50)
        self.assertGreater(len(image.crop((37, 135, 68, 174)).getcolors(2000)), 8)

    def test_bedroom_sky_has_no_ladder_like_reflections(self):
        image = mansion.paint_bedroom()
        lower_glass = np.asarray(image.crop((269, 107, 281, 139))).astype(int)
        self.assertLess(lower_glass.max(), 130)
        self.assertGreater(luminance(image.crop((271, 47, 281, 56))), 170)

    def test_study_water_has_no_ladder_like_reflections(self):
        image = mansion.paint_study()
        self.assertLess(np.asarray(image.crop((287, 81, 310, 107))).max(), 130)

    def test_catch_is_a_mechanism_not_a_framed_icon(self):
        for name in ("ladder_catch", "ladder_freed"):
            with Image.open(ROOT / "assets" / "art" / "rooms" / f"{name}.png") as image:
                alpha = np.asarray(image.getchannel("A"))
                self.assertLess(np.count_nonzero(alpha), alpha.size * 0.6)
                self.assertEqual(alpha[2, 11], 0)
                self.assertEqual(alpha[15, 12], 0)
                self.assertNotEqual(alpha[4, 1], 0)

    def test_library_clock_has_a_round_face_and_distinct_hands(self):
        image = Image.new("RGB", (480, 240))
        library.mantle_items(image)
        self.assertEqual(image.getpixel((239, 23)), common.hx("302418"))
        self.assertEqual(image.getpixel((243, 31)), common.hx("302418"))
        self.assertEqual(image.getpixel((232, 29)), common.hx("362a20"))
        self.assertEqual(image.getpixel((235, 32)), common.hx("e8dfc8"))

    def test_library_shelf_trim_stays_behind_the_clock(self):
        expected = Image.new("RGB", (480, 240))
        library.mantle_items(expected)
        common.shadow(expected, "ellipse", [0, 0, 479, 40], 0.22, 12, common.hx("2a130d"))
        library.sunlight(expected)
        actual = library.paint()
        for y in (21, 22, 24):
            self.assertEqual(actual.getpixel((239, y + common.TOP)),
                             expected.getpixel((239, y)))

    def test_library_has_no_upper_shelf_above_the_mantel(self):
        image = Image.new("RGB", (480, 240))
        library.shelves(image)
        for x in (180, 210, 270, 300):
            for y in range(20, 25):
                self.assertEqual(image.getpixel((x, y)), (0, 0, 0))

    def test_library_ladder_has_aligned_rungs_and_grounded_wheels(self):
        image = Image.new("RGB", (480, 240))
        library.ladder(image)
        for y in range(38, 175, 11):
            x = int(420 - 29 * (y - 26) / 155) + 8
            self.assertEqual(image.getpixel((x, y)), common.hx("b8945e"))
        for x in (391, 409):
            self.assertNotEqual(image.getpixel((x, 185)), (0, 0, 0))

    def test_eleanor_sheet_covers_lower_torso_not_neck(self):
        image = np.asarray(mansion._eleanor_in_bed())
        cloth = np.asarray(mansion._sheet_on(mansion._bare_eleanor(), mansion.SHEET, mansion.SHEET_LIT))
        sheet = cloth[:, :, 3] == 255
        np.testing.assert_array_equal(image[sheet], cloth[sheet])
        ys, _ = np.nonzero(sheet)
        self.assertGreater(len(ys), 20)
        self.assertGreaterEqual(ys.min(), 19)
        self.assertLessEqual(ys.min(), 22, "the white sheet must cover the marked chest area")
        self.assertGreater(ys.max(), 38)

    def test_both_beds_use_the_same_eleanor_figure_with_room_linen(self):
        from PIL import ImageOps
        from art import motel
        motel_figure = ImageOps.mirror(mansion._eleanor_in_bed())
        mansion_figure = ImageOps.mirror(mansion._mansion_eleanor_in_bed())
        np.testing.assert_array_equal(np.array(motel_figure.getchannel("A")), np.array(mansion_figure.getchannel("A")))
        skin = np.array(ImageOps.mirror(mansion._bare_eleanor()))
        cloth = np.array(ImageOps.mirror(mansion._sheet_on(mansion._bare_eleanor(), mansion.SHEET, mansion.SHEET_LIT)))
        bare = (skin[:, :, 3] == 255) & (cloth[:, :, 3] == 0)
        np.testing.assert_array_equal(np.array(motel_figure)[bare], np.array(mansion_figure)[bare])
        bedroom = mansion.paint_bedroom("eleanor")
        bx, by = mansion._eleanor_origin(mansion.Room3D(mansion.BFL, 240, 100))
        night = motel.paint_night()
        for room, (x, y), figure in ((bedroom, (bx, by), mansion_figure), (night, motel.ELEANOR_ORIGIN, motel_figure)):
            opaque = np.array(figure.getchannel("A")) == 255
            crop = np.array(room.crop((x, y, x + figure.width, y + figure.height)))
            shown = opaque.copy()
            if room is night:
                # The motel trims only the lap-sheet spill behind its near head post.
                shown[20:, motel.HEAD_POST_X - x:] = False
            np.testing.assert_array_equal(crop[shown], np.array(figure)[:, :, :3][shown])
        for name in ("motel_night", "mansion_bed"):
            image = np.array(Image.open(self.generated / "rooms" / f"{name}.png").convert("RGB"))
            white = (image.min(axis=2) >= 100) & (image.max(axis=2) - image.min(axis=2) <= 20)
            self.assertGreater(np.count_nonzero(white), 60, f"{name}: white linen disappeared during quantization")
        for color in (mansion.SHEET, mansion.SHEET_LIT):
            self.assertLessEqual(max(color), 155, "motel linen should not glow against the night room")
        from art import sprites
        self.assertEqual(mansion.MANSION_SHEET, common.hx(sprites.ELEANOR_SHEET["torso"]),
                         "Harrington's sheet is the white one Eleanor later wraps herself in")

    def test_mansion_sheet_covers_the_whole_bed_with_her_body_beneath(self):
        image = np.asarray(mansion.paint_bedroom("eleanor")).astype(int)
        white = (image.min(axis=2) >= 150) & (image.max(axis=2) - image.min(axis=2) <= 24)
        R = mansion.Room3D(mansion.BFL, 240, 100)
        x0, x1, z1 = mansion.BED["x0"], mansion.BED["x1"], mansion.BED["z1"]
        left, right = int(R.P(x0, 0, z1 + 4)[0]) + 2, int(R.P(x1, 0, z1)[0]) - 2
        drape = white[187:198, left:right]
        self.assertTrue(drape.all(axis=0).all(), "the sheet must hang over the full length of the bed")
        crest = [int(np.argmax(white[150:190, x])) + 150 for x in range(left, right)]
        feet, knees = min(crest[316 - left:328 - left]), min(crest[346 - left:360 - left])
        hollow = max(crest[333 - left:340 - left])
        mattress = int(R.P(x0, mansion.BED["top"], z1)[1])
        self.assertLess(knees, mattress - 8, "her knees must lift the sheet")
        self.assertLess(feet, mattress - 5, "her feet must lift the sheet")
        self.assertGreater(hollow, max(feet, knees) + 1, "the shins dip between feet and knees")
        outside = white[175:206, :int(R.P(x0 - 4, 0, z1)[0]) - 1]
        self.assertFalse(outside.any(), "the sheet must not spill past the foot posts")
        head_post = int(R.P(x1 + 4, 0, z1 + 4)[0]) + 1
        self.assertFalse(white[186:206, head_post:head_post + 12].any(), "the sheet must not spill past the head posts")

    def test_sheet_spreads_over_the_lap_instead_of_clipping_to_the_standing_body(self):
        body = np.asarray(mansion._bare_eleanor())
        cloth = np.asarray(mansion._sheet_on(mansion._bare_eleanor(), mansion.SHEET, mansion.SHEET_LIT))
        mask = cloth[:, :, 3] == 255
        self.assertGreater(np.count_nonzero(mask & (body[:, :, 3] == 0)), 100)
        self.assertGreater(np.count_nonzero(mask[38]), np.count_nonzero(mask[25]) + 6)
        lower_body = body[30:, :, 3] == 255
        self.assertTrue(np.all(mask[30:][lower_body]), "the seated lap must cover the lower body")

    def test_cotton_folds_have_finite_tapered_ends_and_curved_valleys(self):
        outline = [(0, 0), (39, 0), (39, 39), (0, 39)]
        flat = np.asarray(mansion.linen_surface((40, 40), outline, []), dtype=int)
        with np.errstate(invalid="raise"):
            folded = np.asarray(mansion.linen_surface((40, 40), outline, [
                ([(10, 5), (13, 15), (23, 24), (20, 34)], 1.5, 30),
            ]), dtype=int)
        difference = flat[:, :, 0] - folded[:, :, 0]
        self.assertGreater(difference[15, 13], 15)
        self.assertGreater(difference[24, 23], 15)
        self.assertLess(abs(difference[5, 10]), 2)
        self.assertLess(abs(difference[34, 20]), 2)
        self.assertGreater(difference[15, 13], difference[15, 23] + 10)
        self.assertGreater(difference[24, 23], difference[24, 13] + 10)

    def test_motel_head_moves_only_five_pixels_right_and_two_back(self):
        from PIL import ImageOps
        from art import sprites
        figure = mansion._bare_eleanor()
        skin = sprites.ELEANOR["skin"]
        spec = dict(sprites.ELEANOR, torso=skin, pelvis=skin, sleeves=skin,
                    coat=None, neckline=None, decals=[])
        canonical = sprites.figure(spec, sprites.pose(16, arms=sprites._arms("side")),
                                   sprites.FW, sprites.FH).convert("RGBA")
        canonical.putalpha(canonical.getchannel("A").point(lambda v: 255 if v >= 250 else 0))
        bx, by, right, _ = canonical.getbbox()
        self.assert_image_equal(figure.crop((8, 0, 28, 19)), canonical.crop((bx, by, right, by + 19)))
        original = ImageOps.mirror(figure.crop((8, 0, 28, 19))).getbbox()
        current = ImageOps.mirror(figure.crop((0, 0, figure.width, 19))).getbbox()
        self.assertEqual(motel.ELEANOR_ORIGIN[0] + current[0] - (111 + original[0]), 5)
        self.assertEqual(motel.ELEANOR_ORIGIN[1] + current[1] - (114 + original[1]), -2)

    def test_motel_bed_shows_a_body_and_a_clean_frame(self):
        flat = Image.new("RGBA", (480, 240), mansion.SHEET + (255,))
        mound = np.asarray(motel.body_mound(flat, [motel.LEGS])).astype(int)[:, :, 0]
        for x, y in motel.LEGS[1:-1]:
            self.assertGreater(mound[y - 3, x], mound[y + 5, x] + 40, f"no leg relief at x={x}")
        pair = np.asarray(motel.body_mound(flat, [motel.LEGS, motel.FAR_LEG])).astype(int)[:, :, 0]
        self.assertFalse(np.array_equal(pair, mound), "the far leg adds no second ridge")
        rails = np.asarray(Image.open(self.generated / "rooms" / "motel_night_rails.png").getchannel("A"))
        self.assertEqual(rails[168:176, 50:130].max(), 0, "the near side rail reads as a floor line")
        night = np.asarray(Image.open(self.generated / "rooms" / "motel_night.png").convert("RGB")).astype(int)
        behind_post = night[130:165, motel.HEAD_POST_X + 2:motel.HEAD_POST_X + 7]
        linen = (behind_post.min(axis=2) >= 70) & (np.ptp(behind_post, axis=2) <= 12)
        self.assertEqual(np.count_nonzero(linen), 0, "cotton hangs through the head frame")

    def test_neutral_linen_does_not_repaint_either_foreground_frame(self):
        mask = Image.new("RGBA", (480, 240))
        motel.bed_rails_night(mask)
        foreground = np.asarray(mask.getchannel("A")) == 255
        with patch.object(motel, "white_bed_linen"):
            original = np.asarray(motel.paint_night(rails=True))[common.TOP:]
        current = np.asarray(motel.paint_night(rails=True))[common.TOP:]
        np.testing.assert_array_equal(current[foreground], original[foreground])

        mask = Image.new("RGBA", (480, 270))
        mansion._bed_front(mask, mansion.Room3D(mansion.BFL, 240, 100))
        foreground = np.asarray(mask.getchannel("A")) == 255
        with patch.object(mansion, "_restamp_white_sheet"):
            original = np.asarray(mansion.paint_bedroom("eleanor"))
        current = np.asarray(mansion.paint_bedroom("eleanor"))
        np.testing.assert_array_equal(current[foreground], original[foreground])

    def test_mansion_bed_has_no_side_rail_across_the_bedding(self):
        R = mansion.Room3D(mansion.BFL, 240, 100)
        mask = Image.new("RGBA", (480, 270))
        mansion._bed_front(mask, R)
        alpha = np.asarray(mask.getchannel("A")) == 255
        x0, x1, z1 = mansion.BED["x0"], mansion.BED["x1"], mansion.BED["z1"]
        left, right = R.P(x0 + 1, 0, z1)[0], R.P(x1 - 1, 0, z1)[0]
        top_of_base = int(R.P(x0, 5, z1 + 3)[1])
        bottom_of_cover = int(R.P(x0, 24, z1 + 1)[1])
        between_posts = alpha[bottom_of_cover:top_of_base, int(left) + 1:int(right)]
        self.assertFalse(between_posts.any(), "no frame rail may cross the hanging bedding")

    def test_bed_sprites_reconstruct_both_room_states(self):
        scene = (ROOT / "scenes" / "rooms" / "mansion_bedroom.tscn").read_text()
        base = mansion.paint_bedroom()
        occupied, empty = mansion.paint_bedroom("eleanor"), mansion.paint_bedroom("empty")
        pal = mansion.bedroom_palette(base, occupied, empty, mansion.paint_bedroom(screen=True))
        for name, variant, node in (("mansion_bed", occupied, "Bed"),
                                    ("mansion_bed_empty", empty, "BedEmpty")):
            block = re.search(rf'\[node name="{node}" type="Sprite2D"[^\]]*\]([^\[]*)', scene)[1]
            position = re.search(r"position = Vector2\((\d+), (\d+)\)", block)
            with self.subTest(state=name), Image.open(self.generated / "rooms" / f"{name}.png") as sprite:
                composed = common.pixelize(base, pal).convert("RGBA")
                composed.alpha_composite(sprite, tuple(map(int, position.groups())))
                self.assert_image_equal(composed, common.pixelize(variant, pal))

    def test_bedroom_screen_is_a_low_y_sorted_sprite_micah_shows_over(self):
        scene = (ROOT / "scenes" / "rooms" / "mansion_bedroom.tscn").read_text()
        block = re.search(r'\[node name="Screen" type="Sprite2D" parent="World"\]([^\[]*)', scene)[1]
        x, feet = map(int, re.search(r"position = Vector2\((\d+), (\d+)\)", block).groups())
        offset = int(re.search(r"offset = Vector2\(0, (-?\d+)\)", block)[1])
        self.assertEqual(feet, mansion.SCREEN_FEET)
        self.assertGreater(feet, 214, "Micah's spot behind the screen must sort behind it")
        with Image.open(self.generated / "rooms" / "mansion_bedroom_screen.png") as sprite:
            top = feet + offset
            self.assertGreaterEqual(top, 150, "the screen must be low enough to show his hat and shoulders")
            self.assertLessEqual(x, 107 - 13)
            self.assertGreaterEqual(x + sprite.width, 107 + 13)

    def test_bedroom_fire_strip_loops_and_starts_on_the_background(self):
        x0, y0, x1, y1 = mansion.BED_FIRE_BOX
        with Image.open(self.generated / "rooms" / "mansion_bedroom_fire.png") as strip, \
                Image.open(self.generated / "rooms" / "mansion_bedroom.png") as room:
            w = x1 - x0
            self.assertEqual(strip.size, (w * mansion.BED_FIRE_FRAMES, y1 - y0))
            self.assert_image_equal(strip.crop((0, 0, w, y1 - y0)), room.crop(mansion.BED_FIRE_BOX))
            frames = {strip.crop((i * w, 0, (i + 1) * w, y1 - y0)).tobytes() for i in range(mansion.BED_FIRE_FRAMES)}
            self.assertEqual(len(frames), mansion.BED_FIRE_FRAMES, "every frame of the flames must move")

    def test_outskirts_skyline_fills_the_horizon_over_a_textured_hedgerow(self):
        with Image.open(self.generated / "rooms" / "outskirts.png") as room:
            px = np.asarray(room.convert("RGB")).astype(int)
        sky = px[30:40].mean(axis=2).mean(axis=0)
        towers = px[96:114].mean(axis=2).min(axis=0) < sky - 30
        self.assertGreater(towers.mean(), 0.75, "the skyline spans most of the horizon")
        self.assertGreater((px[60:96].mean(axis=2) < 90).sum(), 150, "towers rise well above the horizon")
        hedge = Image.fromarray(px[150:200, 0:200].astype("uint8"))
        self.assertGreater(len(hedge.getcolors(4000)), 20, "the hedge is modelled leaf by leaf, not flat blobs")

    def test_burning_mansion_is_a_looping_strip_of_flames_and_smoke(self):
        scene = (ROOT / "scenes" / "rooms" / "mansion_exterior.tscn").read_text()
        block = re.search(r'\[node name="Fire" type="Sprite2D" parent="\."\]([^\[]*)', scene)[1]
        self.assertIn(f"hframes = {mansion.EXT_FIRE_FRAMES}", block)
        self.assertIn('ShowIfFlags = "mansion_exploded"', block)
        self.assertIn("LoopStrip", re.search(r'script = ExtResource\("([^"]+)"\)', block)[1])
        with Image.open(self.generated / "rooms" / "mansion_exterior_fire.png") as strip:
            self.assertEqual(strip.size, (common.W * mansion.EXT_FIRE_FRAMES, 270))
            frames = [np.asarray(strip.crop((i * common.W, 0, (i + 1) * common.W, 270)).convert("RGB")).astype(int)
                      for i in range(mansion.EXT_FIRE_FRAMES)]
        self.assertEqual(len({f.tobytes() for f in frames}), mansion.EXT_FIRE_FRAMES, "the flames and smoke must move")
        for f in frames:
            roof = f[0:30, 60:460]
            self.assertLess(roof.mean(), 120, "a bank of smoke rolls off the roof")
            above_window = f[20:40, 64:90]
            self.assertGreater(((above_window[..., 0] > 220) & (above_window[..., 2] < 140)).sum(), 6,
                               "flames lick out above the upper windows")


if __name__ == "__main__":
    unittest.main()
