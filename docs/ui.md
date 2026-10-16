# UI (`scripts/UI`)

Code-built UI, accessed through `Game.Hud`; no UI scenes. `Hud` is a `CanvasLayer` (10, `ProcessMode.Always`);
its root control is pausable, with menu/cursor handling kept active. Coordinates: 480x270.

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
7 px per character), IM Fell English (verse over black). Cursor: `assets/art/ui/cursor.png`; a held item shows as a
16x12 badge.

## Components

- **Speech**: 280 px wrapped label above the speaker's head in its `SpeechColor`, clamped to the screen. With a
  close-up up, speech sits under the inset (380 px; the convent pair puts each speaker under their half).
- **Thoughts**: 440 px box at the top, sepia on a dark strip.
- **Choice bar**: replaces the interface at the bottom; rows 14 px, text width 464 px. Shows `ShownChoices`
  (`#short:` labels).
- **Inventory**: 2x6 slots of 40x28 at (110,186), paged with `<`/`>` beyond 12 items; satchel button at (444,234),
  or **I**.
- **Verb wheel**: four 32x32 slots (Look, Hand, Talk, Kick) at radius 22 around the cursor; press-drag-release or
  click.
- **Captions and fades**: `Fade(alpha, seconds)`, chapter captions, verse lines that fade in one by one.
- **GameMenu** (runs while paused): title (Continue, New game, Load game, Settings), pause (Resume, Save, Load,
  Settings, Quit to title), slots (autosave + 3; unreadable = *Incompatible*, missing = *Empty*), settings.
- **NotepadView**: one page per unlocked note, newest first; arrows, mouse wheel; N/Esc/X closes.

## Close-ups

`CloseUp` = id, texture under `assets/art/ui/` (or a function of settings) and fade times. Catalog: `stage`
(`stage_closeup` with nudity on, `stage_closeup_clothed` off), `rose`, `beaten`, `convent` (two portraits),
`heraldry`.

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

| `PuzzleKind` | Screen | Rule in `PuzzleRules` |
|---|---|---|
| `Lift` | `LiftMazeScreen` (staff lift maze) | lift maze |
| `Safe` | `SafeScreen` (room 507: 3 stops, direction + number) | `Safe` |
| `Catalogue` | `CatalogueScreen` (motif then author, no Submit) | catalogue |
| `Cipher` | `CipherScreen` (feather, lily, leaf) | cipher |
| `Crests` | `CrestsScreen` (sun, moon, star) | crests |
| `Bell` | `BellScreen` (alarm hammer steps) | bell |
| `Alignment` | `AlignmentScreen` (auditor's index) | alignment |

New puzzle: rule in `PuzzleRules` (+ unit test), a screen class in `PuzzleScreens.cs`, a `PuzzleKind` value, art in
`tools/art/puzzles.py`, and a call from the room or `Story.StoryPuzzles`.
