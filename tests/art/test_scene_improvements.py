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
from art import act2_rooms, attic, common, library, mansion, motel


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
                          mansion.build_study, mansion.build_bedroom):
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
        sheet = np.all(image[:, :, :3] == common.hx("e8e0d0"), axis=2) & (image[:, :, 3] == 255)
        ys, _ = np.nonzero(sheet)
        self.assertGreater(len(ys), 20)
        self.assertGreaterEqual(ys.min(), 27)
        self.assertGreater(ys.max(), 38)

    def test_bed_sprites_reconstruct_both_room_states(self):
        scene = (ROOT / "scenes" / "rooms" / "mansion_bedroom.tscn").read_text()
        base = mansion.paint_bedroom()
        occupied, empty = mansion.paint_bedroom("eleanor"), mansion.paint_bedroom("empty")
        pal = common.palette_of(Image.blend(Image.blend(base, occupied, 0.4), empty, 0.3), 124)
        for name, variant, node in (("mansion_bed", occupied, "Bed"),
                                    ("mansion_bed_empty", empty, "BedEmpty")):
            block = re.search(rf'\[node name="{node}" type="Sprite2D"[^\]]*\]([^\[]*)', scene)[1]
            position = re.search(r"position = Vector2\((\d+), (\d+)\)", block)
            with self.subTest(state=name), Image.open(self.generated / "rooms" / f"{name}.png") as sprite:
                composed = common.pixelize(base, pal).convert("RGBA")
                composed.alpha_composite(sprite, tuple(map(int, position.groups())))
                self.assert_image_equal(composed, common.pixelize(variant, pal))


if __name__ == "__main__":
    unittest.main()
