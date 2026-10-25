# Saves and settings

## Saves

The current save format is version 13.

`SaveData` (Godot-free, JSON via `System.Text.Json`):

| Field | Content |
|---|---|
| `Version` | Must equal `SaveData.CurrentVersion` exactly |
| `SavedAtUtc` | Save time |
| `Room`, `RoomTitle` | Scene id and the title shown in slot lists |
| `X`, `Y`, `Facing` | Player position and facing |
| `StoryAct` | 1-3 |
| `Flags`, `Inventory` | From `GameState` (flags sorted) |
| `Ink` | Ink runtime state JSON (variables, visit counts) |
| `PlaytimeSeconds` | Total play time |

`SaveSystem` stores `autosave`, `slot1`-`slot5` as `user://saves/<slot>.json`, writing `<slot>.json.tmp` then
renaming. `Read` returns null for missing, corrupt, wrong-version or unknown-room files: the menu shows *Empty* for a
missing file and *Incompatible* otherwise. `Latest` (title-screen *Continue*) is the newest readable save.

- **Autosave** queued after `ChangeRoom` finishes `OnEnter`; written when the game is idle.
- **Manual save** only between actions (`Game.CanSave`: a room, not busy, not on the title). Saving to a slot that
  already holds a file (even an *Incompatible* one) asks *Overwrite Slot N?* first; *No* or Esc returns to the list.
- **Load** fades out, runs `PuzzleMigration.Normalize`, restores `GameState`, Ink and playtime, loads the room,
  places the player exactly, fades in. `OnEnter` does not run.

### Changing the format

Bump `SaveData.CurrentVersion` when saved decisions, identifiers or room flow change incompatibly (a renamed flag,
item or entry; a new act opening). Older saves then show as *Incompatible* instead of loading into a broken state.
Update the "is version N" sentence on this page and in `Walkthrough.md`:
`StoryIntegrityTests.DocsStateTheCurrentSaveVersion` checks both.

For compatible changes to puzzle progress, extend `PuzzleMigration` instead (it infers new flags from old ones and
marks the save with `puzzles_v1` / `puzzles_act3_v1`). Where a room flag can be missing from an older save of the
same version, the room recovers by itself: a convent-cell save from before Eleanor set her duffle down on entry
(no `interlude_bag_left`) loads with the bag in her hand, and her first click on the bed, nightstand or door sets
it down (`ConventCell.InterludeInteract`). An alley save from before the finish-or-leave choice moved into Tony's
shot scene (Tony wounded on the gravel, `shot_bartender` without `killed_tony`) still lets Micah use the revolver on
Tony to finish him (`Alley.OnInteract`).

| Version | Change |
|---|---|
| 13 | Act 3's Caleb visit is one-way; Rose's coffee decides endings 1/15 (`rose_forgives`) |
| 12 | Motel return after the Act 2 office, Room 507's interlude steps, the Thursday card |
| 11 | Fire-escape conversation moved from Act One to after the First Interlude; version-10 Ink state may already have consumed its choices |
| 10 | Endings 10/11 are Eleanor's weary follow (`eleanor_dismissed` removed); motel detour, motel night and storm-office room flow |
| 9 | Acts Two and Three open with Eleanor's interludes (new rooms, entries, flags) |
| 8 | Laundry bluing moved to Eleanor's brass box; State Street hub prototype removed |
| 7 | Act One convent exterior arrival; return to the corridor for Sister Agatha's farewell |

## Settings

`GameSettings` writes `user://settings.cfg`, independent of saves (loading or a new game never changes it):

```ini
[content]
nudity = false        ; Eleanor's stage sprite and close-up: dressed (false) or implied-nude variant
[display]
fullscreen = false    ; borderless, integer scaling, letterboxed; F11 / Alt+Enter anywhere
[audio]
effects_volume = 80   ; 0-100, steps of 10, wraps; 0 mutes
music_volume = 70
```

Missing file = defaults; wrong types fail the load (logged). `Changed` fires after successful loads and saves;
buses, window mode and close-ups listen to it.

## Test isolation

Normal-play launchers (`tools/run/game.sh` / `tools\run\game.ps1`) use the real player saves and settings.
Their default cleanup preserves both, removing only generated files and isolated test data; `--no-clean` /
`-NoClean` skips cleanup but still builds/imports.

Test/film data paths and cleanup: [Getting started](getting-started.md#where-your-data-goes) and
[Testing](testing.md#launchers-toolsrun). Player saves and settings are untouched; film mode can still toggle the window.
