"""Asset contracts and pixel-exact checks for the club and Harrington generators."""
import contextlib
import io
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageChops, ImageStat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from art import act2_rooms, club, common, sprites


def luminance(image):
    return ImageStat.Stat(image.convert("L")).mean[0]


class AssetContractsTests(unittest.TestCase):
    def test_all_generated_images_decode_and_have_visible_pixels(self):
        for path in (ROOT / "assets" / "art").rglob("*.png"):
            with self.subTest(asset=path.name), Image.open(path) as image:
                image.load()
                self.assertIn(image.mode, ("RGB", "RGBA"))
                self.assertIsNotNone(image.convert("RGBA").getchannel("A").getbbox())

    def test_location_backgrounds_fill_the_viewport(self):
        for path in (ROOT / "scenes" / "rooms").glob("*.tscn"):
            scene = path.read_text()
            resources = {resource_id: asset for asset, resource_id in re.findall(
                r'\[ext_resource type="Texture2D" path="res://([^"]+)" id="([^"]+)"\]',
                scene)}
            background = re.search(r'\[node name="Background"[^\]]*\]([^\[]*)', scene)
            self.assertIsNotNone(background, path.name)
            texture = re.search(r'texture = ExtResource\("([^"]+)"\)', background[1])
            with self.subTest(room=path.stem), Image.open(ROOT / resources[texture[1]]) as image:
                self.assertEqual(image.size, (480, 270))
                self.assertEqual(image.convert("RGBA").getchannel("A").getextrema(), (255, 255))

    def test_fixed_art_references_exist(self):
        for folder, extension in (("scenes", "*.tscn"), ("scripts", "*.cs")):
            for path in (ROOT / folder).rglob(extension):
                for asset in re.findall(r'"res://(assets/art/[^"{}]+\.png)"', path.read_text()):
                    with self.subTest(source=path.name, asset=asset):
                        self.assertTrue((ROOT / asset).is_file())

    def test_animation_frames_and_padding_match_runtime_layout(self):
        for name in ("micah", "daniel", "micah_dressing", "micah_masked",
                     "eleanor_play", "eleanor_gown_play", "eleanor_sheet_play"):
            with Image.open(ROOT / "assets" / "art" / "sprites" / f"{name}.png") as image:
                self.assertEqual(image.size, (640, 288))
                alpha = image.getchannel("A")
                for row, count in enumerate((10, 9, 7)):
                    for column in range(10):
                        frame = alpha.crop((column * 64, row * 96, (column + 1) * 64, (row + 1) * 96))
                        with self.subTest(sprite=name, row=row, column=column):
                            self.assertEqual(frame.getbbox() is not None, column < count)
        for name, *_ in sprites.NPCS:
            with Image.open(ROOT / "assets" / "art" / "sprites" / f"{name}.png") as image:
                self.assertEqual(image.size, (616, 96))
                for column in range(11):
                    with self.subTest(sprite=name, column=column):
                        self.assertIsNotNone(image.getchannel("A").crop(
                            (column * 56, 0, (column + 1) * 56, 96)).getbbox())

    def test_inventory_icons_fit_runtime_slots(self):
        for path in (ROOT / "assets" / "art" / "items").glob("*.png"):
            with self.subTest(item=path.name), Image.open(path) as image:
                self.assertEqual(image.size, (32, 24))
                self.assertEqual(image.mode, "RGBA")


class LocationRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.generated = Path(cls.directory.name)
        with patch.object(common, "ART", cls.directory.name), contextlib.redirect_stdout(io.StringIO()):
            club.build()
            act2_rooms.build_road()
            act2_rooms.build_office()

    def assert_images_equal(self, actual, expected):
        self.assertEqual(actual.size, expected.size)
        self.assertIsNone(ImageChops.difference(actual.convert("RGB"), expected.convert("RGB")).getbbox())

    def test_committed_art_matches_generators(self):
        for path in (self.generated / "rooms").glob("*.png"):
            with self.subTest(asset=path.name), Image.open(path) as generated, Image.open(
                    ROOT / "assets" / "art" / "rooms" / path.name) as committed:
                self.assert_images_equal(committed, generated)

    def test_club_uses_individual_limited_palettes(self):
        for name in ("club_hall", "club_lounge", "club_stage"):
            with self.subTest(room=name), Image.open(self.generated / "rooms" / f"{name}.png") as image:
                self.assertEqual(image.size, (480, 270))
                self.assertLessEqual(len(image.getcolors(480 * 270)), 128)

    def test_sofas_remain_velvet_not_flat_light_pools(self):
        image = club.lounge_scene()
        back = image.crop((80, 152, 164, 164))
        self.assertLess(luminance(back), 65)
        self.assertGreater(len(back.getcolors(back.width * back.height)), 20)
        self.assertGreater(ImageStat.Stat(back).mean[0], ImageStat.Stat(back).mean[1] * 1.3)

    def test_office_window_is_dark_like_the_rest(self):
        # It's night and Harrington has gone home: his window must not stand out from the row.
        image = act2_rooms.paint_road()
        x0, y0, x1, y1 = act2_rooms.ROAD_WINDOW
        office = image.crop((x0, y0, x1 + 1, y1 + 1))
        other_window = image.crop((x0 - 124, y0, x1 - 123, y1 + 1))
        self.assertLess(abs(luminance(office) - luminance(other_window)), 6)
        self.assertLess(luminance(office), 60)

    def test_office_floor_does_not_erase_furniture_bases(self):
        with patch.object(act2_rooms, "light"), patch.object(act2_rooms, "vignette"):
            image = act2_rooms.paint_office()
        # The floor starts at 196, but the desk pedestals and closet extend down to 204.
        for x, outline in ((186, "1e1209"), (314, "1e1209"), (372, "140a04"), (456, "140a04")):
            with self.subTest(edge=x):
                expected = tuple(value * tint // 255
                                 for value, tint in zip(common.hx(outline), (118, 128, 186)))
                self.assertEqual(image.getpixel((x, 201)), expected)

    def test_harrington_overlays_match_variants_at_scene_positions(self):
        for name, paint, variants in (
            ("harrington_road", act2_rooms.paint_road,
             (("fire", dict(fire=True), {}), ("crates", dict(stacked=True), {}),
              ("ladder", dict(stacked=True, freed=True), dict(stacked=True)))),
            ("harrington_office", act2_rooms.paint_office,
             (("drawer_left", dict(left=True), {}), ("drawer_right", dict(right=True), {}),
              ("closet", dict(closet=True), {}),
              ("secret", dict(closet=True, secret=True), dict(closet=True)))),
        ):
            scene = (ROOT / "scenes" / "rooms" / f"{name}.tscn").read_text()
            if name == "harrington_road":
                base = paint()
                pal = act2_rooms.road_palette(base, paint(fire=True), paint(stacked=True))
            else:
                blend = paint()
                for _, flags, _ in variants:
                    blend = Image.blend(blend, paint(**flags), 0.4)
                pal = common.palette_of(blend, 124)
            combined = common.pixelize(paint(), pal)
            combined_flags = {}
            for suffix, flags, base_flags in variants:
                asset = f"{name}_{suffix}.png"
                resource_id = re.search(rf'path="res://assets/art/rooms/{re.escape(asset)}" id="([^"]+)"', scene)[1]
                node = next(block for block in re.split(r"(?=\[node )", scene)
                            if f'texture = ExtResource("{resource_id}")' in block)
                position = re.search(r"position = Vector2\((\d+), (\d+)\)", node)
                x, y = map(int, position.groups())
                before, after = common.pixelize(paint(**base_flags), pal), common.pixelize(paint(**flags), pal)
                with self.subTest(overlay=asset), Image.open(self.generated / "rooms" / asset) as overlay:
                    box = (x, y, x + overlay.width, y + overlay.height)
                    self.assertLessEqual(box[2], 480)
                    self.assertLessEqual(box[3], 270)
                    self.assert_images_equal(overlay, after.crop(box))
                    composed = before.copy()
                    composed.paste(overlay, (x, y))
                    self.assert_images_equal(composed, after)
                    combined.paste(overlay, (x, y))
                    combined_flags.update(flags)
            with self.subTest(room=name, state="all overlays"):
                self.assert_images_equal(combined, common.pixelize(paint(**combined_flags), pal))


    def test_club_portrait_is_the_stag_from_the_source_picture(self):
        image = Image.new("RGB", (60, 72))
        club.painting(image, 5, 4, 55, 68)
        canvas = image.crop((9, 8, 52, 65))
        self.assertGreater(len(canvas.getcolors(canvas.width * canvas.height)), 100, "a picture, not flat shapes")
        self.assertNotIn(common.hx("e0a878"), {colour for _, colour in canvas.getcolors(4096)}, "no flat skin oval")
        # the antlers' bone and the stag's brown head are the brightest, warmest part of the canvas
        top = ImageStat.Stat(canvas.crop((0, 0, canvas.width, canvas.height // 2))).mean
        self.assertGreater(top[0], top[2])
        source = club.painting_source()
        self.assertAlmostEqual(source.width / source.height, canvas.width / canvas.height, delta=0.03)

    def test_bedroom_puts_daniel_in_front_and_hides_his_wife(self):
        self.assertEqual(len(act2_rooms._bed_figures(1.2)), 2, "only Daniel is painted; she's under the quilt")
        with contextlib.redirect_stdout(io.StringIO()):
            _, dan, wife = act2_rooms.paint_bedroom()
        self.assertGreater(wife[1], dan[1], "her shape under the quilt sits lower than his head")
        self.assertGreater(wife[0], dan[0])



if __name__ == "__main__":
    unittest.main()
