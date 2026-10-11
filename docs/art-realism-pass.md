# Art realism pass

A pixel audit of the generated rooms, props, and character strips. Painters in `tools/art` were corrected and the committed PNGs were regenerated with `py -3.14 tools/gen_art.py`. No PNG was hand-edited. Body proportions in `tools/art/figure.py` (`HEAD` / `BULK`) were left alone.

## What was wrong

The failures were not “needs more polygons.” They were shapes that did not read as the thing they claimed to be:

- A club portrait that was a brown oval and a dark trapezoid — a skull, not a man.
- Stage seats that were flat dark blocks with no wooden back.
- A bedroom wife who was only a head under the quilt, with no shoulder or gown.
- Motel and map walls that faded into one wash, or a blank paper margin.
- Inventory icons that were silhouettes: a revolver without a cylinder or sight, a card with no name, a cloth and a wedge with no grain.
- Story actions that the script described and the sprite never played: opening the office door, Harrington falling before the shot.

## Before / after

| Subject | Before | After |
|---|---|---|
| Club hall portrait | Brown oval head, dark cloak polygon. After palette reduction it collapsed into one blob. | Bust: black hair, skin far from the suit ramp, eyes, mustache, white shirt, red tie. |
| Club stage | Seats were cushion-colored blocks. The aisle was one dark polygon. | Wooden backs (`6a4030`) and bases under each cushion. A worn red aisle carpet with weave lines. |
| Speakeasy floor | One dark board fill from curtain to bar. | A paler worn path, board highlights, and beer spills in the corners. |
| Convent cell | Two damp patches, then empty plaster. | A third damp patch, a nail where a picture hung, and a tide-mark. Still a poor cell. |
| Motel room | One print on a brown wall. The dresser mirror was a green wash. | A second landscape print, a tear-off calendar reading `27`, and a window reflected in the mirror. |
| Chicago map | `SOUTH SIDE` sat in the bottom margin. The south-west paper was blank. | Label moved to `(78, 208)`. A stock-yards hatch fills `(16, 218)–(58, 250)`. |
| Outskirts | A short, narrow skyline and round tree blobs with no underside. | Taller, wider blocks. Tree masses have a darker underside and a lit top. |
| Harrington road windows | Lit windows were a flat night rectangle. | Dark interiors stay dark; some panes show a shade, a lamp, or a diagonal reflection. The locked lit `ROAD_WINDOW` crop was not moved. |
| Rose house sidewalk | Even expansion joints. | Joints stagger, with a cracked slab. |
| Bedroom | Wife crop was `0.3 * hW` (a head). Quilt started at `X0 + 23` and covered the shoulder. | Crop is `0.64 * hW` (head, neck, near shoulder). Quilt starts at `X0 + 36`. Daniel stays in profile so the journal hand offset still lands. |
| Revolver icon | Barrel and grip only. | Cylinder, front sight, and a short sight line. |
| Calling card | A heart and a gold point. | `MJ` and a baseline, so it reads as Micah’s card. |
| Documents / cloth / wedge | Flat paper, one fold, a plain triangle. | A lifted paper corner, extra cloth folds, and wood grain on the wedge. |
| Office door | One closed door painted into the room. | Closed plate is unchanged. `office_door_ajar.png` and `office_door_open.png` are overlays of the same palette, cropped from `DOOR_BOX`. |
| Mansion bed sheet | The cloth over Eleanor's chest graded into the same peach as her shoulder. | Stamped white after the lamp (`248,246,242`), with a cool fold, so it stays linen. |

## Action sprites

These are generated strips, not extra story beats. Playback uses the existing pose player.

| Strip | Size | What it does | Where it plays |
|---|---|---|---|
| `micah_open_door` | 4 × 92×96 | Idle at yaw 55, near arm reaches, pulls, returns to idle. | Act 2 office exit. Player faces left so the reach meets the door. |
| `teddy_open_door` | 4 × 92×96 | Same reach at Teddy’s yaw 35. | Teddy leaving the office. |
| `rose_open_door` | 4 × 92×96 | Same reach at yaw 20. Rose’s profile silhouette only gains about 7 px; the arm is still past the idle edge. | Rose opening her door. She faces right. |
| `harrington_fall` | 4 × 176×128 | A short topple (0°, 16°, 34°, 50°) that stays inside the frame, then the existing shot pose takes over. | Mansion bedroom, before the gunshot. |
Motel night does not play `eleanor_sheet_rise`. Eleanor stays in the painted bed from the original sleeper: head and shoulder on the pillow, the rest under the sheet, including the near-side skirt. She does not stand up.

The near arm is `s = -1`. On a right-facing 3/4 view that is the screen-right arm. `s = 1` hides the reach behind the body; an earlier pass used that and the door gesture did not read.

Door strips are wider than the 64×96 walk sheet, so the first frame is the idle pose drawn at strip width, not a byte-identical crop of `micah.png`.

## Rooms left alone

Office interior (closed), lobby, alley, attic, street, church, library, kitchen, mansion exterior, and the convent corridor. Those already had readable objects, or a locked crop (attic bulb, library clock, motel curtain) that a broad repaint would break. Eleanor’s sheet and the existing collapse / kneel / drink strips were not redesigned.

## How to check

```powershell
py -3.14 -m unittest tests.test_character_art tests.art.test_scene_improvements tests.art.test_location_art tests.art.test_reconciliation_art
godot_console.exe --path . -- --autoplay
```

Focused asserts: the club portrait crop contains skin and dark eyes; the wife crop is wider than it is tall; each door strip starts on `figure(spec, pose(yaw))` and the reach extends past that idle; Harrington’s fall frames are distinct and unclipped.
