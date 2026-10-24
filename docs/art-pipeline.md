# Art pipeline

Python/Pillow painters in `tools/art/` generate committed art under `assets/art/`; Python is not needed at runtime.
**Edit the painter, regenerate, commit both.** Never hand-edit generated PNGs: the `art` suite compares them to generators.

## Commands

```powershell
py -3.14 -m pip install --upgrade pillow numpy
py -3.14 tools\gen_art.py                   # everything
py -3.14 tools\gen_art.py sprites motel     # some steps
py -3.14 -m unittest discover -s tests\art -v
py -3.14 tests\test_character_art.py
```

Steps: `sprites`, `items`, `office`, `lobby`, `eleanor_room`, `speakeasy`, `alley`, `convent`, `convent_road`,
`chicago_map`, `street`, `attic`, `club`, `library`, `motel`, `motel_exterior`, `motel_lobby`, `outskirts`, `church`, `rose_house`, `harrington`,
`bedroom`, `act3`, `ui`, `puzzles`, `expansion_act1`, `expansion_act2`, `expansion_act3`, `closeup`, `icon`.

After regenerating, run `godot_console --path . --headless --import` (stale imports show old textures).
Alternatively, `tools/run/game.sh` / `tools\run\game.ps1` cleans generated caches, builds/imports and opens
normal play for visual review. `--no-clean` / `-NoClean` preserves existing captures while still rebuilding/importing.

## Modules (`tools/art/`)

| Module | Paints |
|---|---|
| `common.py` | Shared canvas (480 wide, 240 painting + 30 interface band), palettes, quantization, dithering, save helpers |
| `figure.py` | 3D-ish figure painter: proportions (`HEAD`, `BULK`), yaw, poses, top-left light, sel-out outlines, dithered cloth |
| `sprites.py` | Character specs and every sprite sheet and action strip (+ pose JSON) |
| `furniture.py` | Perspective furniture |
| `items.py` | 32x24 inventory icons |
| `ui.py` | Cursor, interface, satchel, verb icons, title, frames |
| `puzzles.py` | Puzzle props, clue plates, screen art |
| `closeup.py` | Close-up panels from `tools/art/src/` pictures |
| `icon.py`, `iconfx.py` | Game icon (`assets/art/ui/icon.png`, `icon.ico`, `dist/linux/icons/hicolor`) |
| `office.py`, `lobby.py`, `hotel.py`, `hotel_mess.py`, `speakeasy.py`, `alley.py`, `attic.py`, `street.py`, `chicago_map.py`, `convent.py`, `convent_road.py`, `club.py`, `library.py`, `motel.py`, `motel_exterior.py`, `motel_lobby.py`, `outskirts.py`, `church.py`, `mansion.py`, `act2_rooms.py`, `act3_rooms.py`, `act3_extra.py`, `expansion_act1..3.py` | Rooms, their state overlays and foreground layers |

`tools/art/src/` holds the source pictures reduced into close-ups and the club's stag portrait, the public-domain 1920
Chicago street map scan that `chicago_map.py` prints the map screen from, and the Caveat font for its handwritten pin
tags (see [CREDITS.md](../CREDITS.md)).

## Asset contracts

| Asset | Size / format |
|---|---|
| Room background | 480x270 (`assets/art/rooms/`) |
| Player sheet | 64x96 frames, 10x3 (rows: horizontal, front, back; columns in `Player.cs`) |
| NPC strip | 11 frames of 56x96: idle, 2 talk, walk 1-8 (side view) |
| Item icon | 32x24 (`assets/art/items/`) |
| Action strip | PNG + JSON: `width`, `height`, `frames[{anchor, head, seconds, bounds}]` (frame pixels) |
| Close-up | 220x113 art area doubled, 32 colors, ordered dither, in a frame |
| Photo close-up | 72x113 art area doubled, 32 sepia colors, ordered dither, on a 9 px cream card mount (RGBA, worn corners) |
| Overlays / foreground | Own crop size and scene position |

Club rooms use separate 128-color palettes. Replacement art must preserve these contracts and be incorporated into
the generator; otherwise regeneration overwrites it and art tests fail.

The mansion exterior shares a 124-color palette across its background and state overlays, reserving three shades
for the lantern's light source and glass. Its bin, tied-bell and open-door crops are fixed to the existing scene
positions; do not tighten them to palette-dependent difference bounds.

## Action strips and poses

Story actions (opening a door, collapsing, kneeling, drinking) are strips beside the walk sheets, played by
`PosePlayback` (mirrors anchor and head with the art, game time, holds the last frame) via `Player.PlayPose` /
`Actor.PlayPose`. They return `false` if interrupted; call `SetPose(null)` after a completed action. Strips wider than
64x96 start on the idle pose drawn at strip width, not a crop of `micah.png`. In `figure.py`, the near arm on a
right-facing 3/4 view is `s = -1`. A spec with `far_arm_behind` (Eleanor's pink gown) keeps the far arm behind the
dress in the front and back 3/4 rows, instead of painting it over the torso edge. Its coat's `hem_legs` and `hem_pad`
make the hem follow the legs (padding past each leg) rather than the hip width.

## Visual checks

- Fix shapes that don't read as what they claim (a portrait that collapses to a blob after palette reduction, seats
  without backs, icons that are silhouettes); judge at native size and enlarged.
- Keep faces readable through palette reduction: skin far from the clothing ramps, explicit eyes.
- Keep grounded poses aligned across animation frames.
- After changing a room painter, regenerate its state overlays and check the printed crop origins against the node
  positions in the scene. Moving a crop without its node misaligns the object.
- Locked crops (attic bulb, library clock, motel curtain, Harrington road window) must not move.
- The mansion alarm's tie uses the fixed `BELL_TIE_BOX` crop at `(337, 69)`, matching its scene node even when the
  knot or tails shrink. Keep the gong at 18-20 pixels wide and the hanging tie ends within a six-pixel span;
  regenerate every exterior state together so the smaller alarm and its palette agree.
- Shared painters (the mansion and motel bed figure) must stay identical across rooms; per-room differences go in
  parameters (sheet color), not copies.
- Passing tests is not visual approval: look at the frames (see [Testing](testing.md#seeing-what-the-game-draws)).
- Show changed images as before/after previews in the PR description
  ([CI and release](ci-and-release.md#pull-requests)).
