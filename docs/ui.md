# UI (`scripts/UI`)

Code-built UI, accessed through `Game.Hud`; no UI scenes. `Hud` is a `CanvasLayer` (10, `ProcessMode.Always`);
its root control is pausable, with menu/cursor handling kept active. Coordinates: 480x270.

For interactive title, menu and input checks, use `tools/run/game.sh` / `tools\run\game.ps1`; these open the
normal title screen and retain player settings. Film mode filters input, so it is not a substitute for UI testing.

## Files

| File | Contents |
|---|---|
| `Hud.cs` | Layer construction and draw order, colors, fonts, cursor, hover label |
| `Hud/Hud.Dialogue.cs` | Speech, journal narration, choice bar |
| `Hud/Hud.Inventory.cs` | Satchel button and inventory grid |
| `Hud/Hud.Screens.cs` | Fades, captions, verse, title, pause banner |
| `Hud/Hud.Images.cs` | Full-screen images and close-up insets |
| `VerbWheel.cs` | Right-click wheel |
| `GameMenu.cs` | Title, pause, save/load slots, settings |
| `NotepadView.cs` | Full-screen notepad |
| `CloseUp.cs` | `CloseUp` record and `CloseUps` catalog |
| `PuzzlePanel.cs` / `PuzzleScreens.cs` | Puzzle frame and the seven puzzle screens |

## Draw order

Children draw in the order `Hud._Ready` adds them; keep it. Back to front: close-up inset, interface, satchel,
inventory, hover label, choice bar, speech/thought, verb wheel, title, fade and captions, cutscene images, notepad,
game menu, puzzle panel, pause overlay, cursor and held-item badge.

## Look

| Constant | Value | Use |
|---|---|---|
| `VerbColor` | `#b89a58` | Brass UI text |
| `VerbHover` | `#f8e8b0` | Hover, captions |
| `ChoiceColor` | `#8ab0d8` | Dialogue choices |
| `ThoughtColor` | `#d8b878` | Journal narration |

Fonts (`assets/fonts/`): Silkscreen 8 px (UI, black 4 px outline), Departure Mono 11 px (speech, thoughts, choices;
7 px per character), IM Fell English (verse over black), Poiret One 22 px (captions over black, stepped down to fit
the screen). Cursor: `assets/art/ui/cursor.png`; a held item shows as a
16x12 badge.

## Components

- **Speech**: 280 px wrapped label above the speaker's head in its `SpeechColor`, clamped to the screen. With a
  close-up up, speech sits under the inset (380 px; the fire-escape pair puts each speaker under their half). Beside a
  photo close-up it fills the column to the photo's right, centred on the photo.
- **Thoughts**: 440 px box at the top, sepia on a dark strip.
- **Choice bar**: replaces the interface at the bottom; rows 14 px, text width 464 px. Shows `ShownChoices`
  (`#short:` labels).
- **Inventory**: 2x6 slots of 40x28 at (110,186), paged with `<`/`>` beyond 12 items; satchel button at (444,234),
  or **I**. Picking an item keeps it open; once the cursor has been over the case or page buttons
  (`Hud.InventorySurface`), leaving them closes it. A click outside the case also closes it.
- **Verb wheel**: four 32x32 slots (Look, Hand, Talk, Kick) at radius 22 around the cursor; press-drag-release or
  click.
- **Captions and fades**: `Fade(alpha, seconds)`, chapter captions with an optional second line under them
  (`ShowCaptionSub`, the interlude titles), caption fades (`FadeCaptionIn`, `FadeCaptionSubIn`, `FadeCaptionOut`)
  and the act-change cards over black (`ActCards`), verse lines that fade in one by one (`ShowVerses`;
  `SkipVerses` cuts them short). At launch, after Godot's boot splash, `Game.Epigraph` shows Luke 15:7 this way
  under the title's rain before the title; any key, click or tap skips it. It is not replayed by *Quit to title*.
- **GameMenu** (runs while paused): title (Continue, New game, Load game, Settings, Quit game), pause (Resume, Save,
  Load, Settings, Quit to title, Quit to desktop with a *Quit without saving?* confirmation; the quit entries are
  hidden on mobile), slots (autosave + 3; unreadable = *Incompatible*, missing = *Empty*), settings.
- **NotepadView**: one page per unlocked note, newest first; arrows, mouse wheel; N/Esc/X closes.

## Close-ups

`CloseUp` = id, texture under `assets/art/ui/` (or a function of settings) and fade times. Catalog: `stage`
(`stage_closeup` with nudity on, `stage_closeup_clothed` off), `rose` (Act 2's "Wait!" and Act 3's coffee), `beaten`, `fire_escape` and `church` (two
portraits), `heraldry`, `motel`, and `vows` (`vows_photo`, ending 1's epilogue). `Photo = true` (`vows`) places the picture
32 px from the left edge, vertically centred, with speech beside it.

```csharp
Game.Hud.ShowCloseUp(CloseUps.Rose);   // Ink: INSET: rose
Game.Hud.HideCloseUp();                 // Ink: INSET: none
Game.Hud.HideCloseUp(0);                // Ink: INSET: none_now
```

The Hud swaps variants when settings change and hides insets on room change. To add one: source picture in
`tools/art/src/`, panel in `tools/art/closeup.py` (`framed` or `framed_pair`), a `CloseUps` entry.

## Puzzle screens

`await Game.Hud.Puzzle.Open(PuzzleKind.X)` returns `true` when solved, `false` on cancel. `PuzzlePanel` provides the frame
(`puzzle_frame.png`), title, clue card, feedback strip, Reset, optional Submit and Close/Esc; screens draw in the
left work area (about x 14-272, y 31-204). Untimed, unlimited retries; unsubmitted input resets on close.

Screens that call `DirectionPad` (`Lift`, `Alignment`) also move with the arrow keys (`ui_up/down/left/right`,
held keys repeat) and with left-button or touch drags that start on the work area: `SwipeGesture`
(`src/Repentance.Rules/`, Godot-free) emits one step per `SwipeStep` (one 14px cell) along the drag's dominant axis.
All three go through `PuzzleScreen.Step`, so pause blocks them like the pad buttons.

| `PuzzleKind` | Screen | Rule in `PuzzleRules` |
|---|---|---|
| `Lift` | `LiftMazeScreen` (staff lift maze) | lift maze |
| `Safe` | `SafeScreen` (room 507: 3 stops, direction + number 0-49) | `Safe` |
| `Catalogue` | `CatalogueScreen` (motif then author, no Submit) | catalogue |
| `Cipher` | `CipherScreen` (feather, lily, leaf) | cipher |
| `Crests` | `CrestsScreen` (sun, moon, star) | crests |
| `Bell` | `BellScreen` (alarm hammer steps) | bell |
| `Alignment` | `AlignmentScreen` (auditor's index) | alignment |

New puzzle: rule in `PuzzleRules` (+ unit test), a screen class in `PuzzleScreens.cs`, a `PuzzleKind` value, art in
`tools/art/puzzles.py`, and a call from the room or `Story.StoryPuzzles`.

## Touch

`emulate_mouse_from_touch` is off; `TouchInput` (`scripts/Core/`, a Game child that runs while paused) turns the first
finger into the mouse and key events the rest of the UI already handles, so no control needs touch code of its own.
`TouchPointer` (`src/Repentance.Rules/`, Godot-free, unit-tested) decides: a tap is a left click, holding still for
`HoldSeconds` (0.45s) within `Slop` (6px) is a right press that the finger then drags and releases, and moving first is a
left drag (puzzle swipes, the notepad's page swipe). Events are injected with `Viewport.PushInput`. The Android back
button is Esc (`quit_on_go_back=false`).

`TouchInput.UsingTouch` turns on with any touch and off on real mouse motion. While on, the Hud (`Hud.Touch.cs`)
hides the crosshair and shows **MENU** (Esc) and **NOTES** (N, once the notepad is carried) bottom left; AutoPlay's
`TouchTest` drives them. On `mobile` the window-mode controller leaves the window alone and Settings drops *Full screen*.
