# Testing

## Quick reference

```powershell
tools\run\test.ps1 -Suite unit, walk         # some suites (first run clean)
tools\run\test.ps1 -Suite unit -NoClean      # skip deletion of generated files
tools\run\film.ps1 -Speed 4 -Ending 5        # watch the game play itself
tools\run\film.ps1 -Speed hyper -From ending -Ending 8   # 60x, straight to the ending
```

```bash
tools/run/test.sh unit walk --no-clean
tools/run/film.sh --speed 4 --ending 5
tools/run/film.sh -s hyper --from ending --ending 8
```

Before a PR, run only the suites matching your change; CI runs everything. With no `-Suite`, the launcher runs
all suites from a clean slate (~10 min). Do not do this or run film mode unless requested.

| Change | Suites |
|---|---|
| Docs only | none |
| Any C# | `unit` (after `dotnet build`) |
| Story: Ink, `scripts/Rooms`, `scripts/Story`, items, endings, playthrough | `unit, playthrough` |
| Saving/loading, `GameState`, state a save must carry | `unit, playthrough, resume-act2, resume-act3` |
| AutoPlay act file or `Harness.cs` | add `autoplay` |
| Scenes: walk areas, hotspots, entries, exits | `unit, walk` |
| Art generators or `assets/art` | `art` |
| Music scores, `assets/audio/{piano,sax,bass}`, `tools/music` | `unit, playthrough` (listen first with `tools/music render`, see [Audio](audio.md#music-tool)) |
| Settings menu / pause | `settings` / `pause` |
| CI, launchers, export presets | no additional suites; validate the changed tooling, then CI |

## Suites

| Suite | Runs | Covers | Pass |
|---|---|---|---|
| `unit` | `dotnet test` on each `tests/*.Tests` project | Godot-free rules, scene graph, story integrity, Ink walk | exit code |
| `art` | Python `unittest` in `tests/` | Generated art matches the generators and contracts | exit code |
| `playthrough` | `--playthrough` | Canonical story, every ending, save/load after every beat, sound/music coverage | `PLAYTHROUGH OK` |
| `resume-act2`, `resume-act3` | `--playthrough --resume=act2\|act3` | A fresh launch loads a checkpoint `playthrough` kept and plays on to "The End" (run `playthrough` first) | `RESUME OK` |
| `autoplay` | `--autoplay` | Targeted regressions: puzzles, wrong items, mouse, wheel, inventory, notepad, poses, dialogue variants, seeded endings; screenshots | `AUTOPLAY OK` |
| `settings` | `--settings-test --no-music` | Content, display, volume settings, persistence, menus, both Eleanor variants | `SETTINGS TEST OK` |
| `pause` | `--pause-test --no-music` | Space freezes and resumes everything | `PAUSE TEST OK` |
| `walk` | `--walk-test --no-music` | Movement and reachability in every room, real mouse input | `WALK TEST OK` |

A Godot suite passes only if Godot exits 0, prints the marker, **and** `logs/<suite>.log` has no `ERROR:`,
`SCRIPT ERROR:`, `USER ERROR:` or `Unhandled exception` line (`Game.Run` turns exceptions into `GD.PushError`, so a
run can reach its marker after one). Test suites use `--audio-driver Dummy`; CI uses the same pass rule.
`settings`, `pause` and `walk` never check music, so they run with `--no-music`: rendering the tracks keeps the CPU
and GC busy at boot, and on a slow runner that stalls frames in timing-sensitive checks. `autoplay` and `playthrough`
assert that music plays, so they keep it on.
Every run quits through `Harness.Finish`, which calls `Timers.ReleasePending` first: if C# still holds a pending
`SceneTreeTimer` at quit, Godot aborts at shutdown ("Leaked unsafe reference", `!rc_owner`). Await timers through
`Timers.Wait`, not `ToSignal(GetTree().CreateTimer(...))`.
A local pass does not cover CI's other suites or exported builds.

Don't run `autoplay` or `settings` with `--headless` by hand: they take screenshots, which need a renderer (CI uses
xvfb).

## Launchers (`tools/run/`)

`game.ps1`/`game.sh` (normal interactive play), `test.ps1`/`test.sh`, `film.ps1`/`film.sh`, shared
`common.ps1`/`common.sh`, and `check-godot.gd` (rejects
non-4.x or non-C# Godot before anything is deleted).

Without `-NoClean`/`--no-clean`, they delete `.godot/`, `.mono/`, `bin/`, `obj/`, `tests/**/bin|obj`,
`screenshots/`, `frames/`, `logs/` and the test user data (`user://autoplay_saves/`, `user://autoplay_settings.cfg`;
never your saves or settings). **Normal play, Godot suites and film always build and import**, including with `-NoClean`
(log `logs/import.log`; an error stops the run). `unit` uses `dotnet test`; `art` uses Python only.
Python discovery: `PYTHON`, `PATH`, or `%LOCALAPPDATA%\Programs\Python`.

Normal play: `tools/run/game.sh` or `tools\run\game.ps1`. Both support the same cleanup opt-out and engine-path
options as film/test (`--no-clean`, `--godot PATH` / `-NoClean`, `-Godot PATH`). They open the title screen with
real sound and player data, without automation or a timeout, and wait for you to quit. `logs/game.log` records
output; no test marker is required. Runtime error lines are reported as warnings (like film); nonzero exits
fail, and build/import errors prevent launch. This is not a test-suite pass.

`tests/test_run_scripts.py` tests the launchers themselves (run in CI's unit job).

## The harness (`scripts/Debug/`)

`Harness` supplies `--clock` (fast 60x by default, normal 8x; restored to 1x at the end), checks, failure accounting,
markers and exit codes, `WaitIdle`/`Until`/`Observe`, synthetic mouse and
keyboard input (`Viewport.PushInput`), screenshots to `screenshots/`, a wiped per-suite save folder, and shared
puzzle/satchel helpers. Put new shared helpers here, not in `AutoPlay`.

### `Playthrough` (`--playthrough`, `--film`)

Named beats (`Beat(id, body)`) walk, look, use items, solve puzzles and pick choices. Beats:
`Playthrough/Playthrough.Act1.cs` ... `Act3.cs`; Act 3 routes branch on
`_route`, and `Playthrough.Endings.cs` holds each route's choices and "The End" checks. `Playthrough.cs` keeps the
modes, the save/load round trip and the coverage gates.

- Acts 1-2 play once; at the Club vestibule the run saves, then reloads that save for every route: `2 3 4 5 6 7 1
  1-oldman 1-steps 8 9 10 11`. No seeded state. `--ending=N` runs one route.
- After every beat: save, load, compare room, position, facing, act, flags, inventory, Ink state.
- Fresh-launch checkpoints: the run also keeps two real saves in `user://autoplay_saves/checkpoints/` (end of Act One,
  Club vestibule) with the choices matched so far. `--resume=act2` / `--resume=act3` (suites `resume-act2`,
  `resume-act3`, CI's playthrough job) start a new Godot process, load one as the title screen's Load does, and play
  route 2 / 8 (or `--ending=N`) to "The End". The in-process round trip cannot see state a save forgets (statics,
  room or puzzle fields), since it is still in memory; a fresh process that keeps playing does. No coverage gates.
- A beat that cannot reach what it needs times out and fails, naming the beat.
- Coverage: every `Sound` and every `Track` must play (`UnheardSounds` exceptions, empty), and every choice a route
  wants must be offered.

### `AutoPlay` (`--autoplay`, `--settings-test`, `--pause-test`)

Regressions that would break quietly: one partial per area (`AutoPlay.Act1/2/3`, `Endings`, `Dialogue` (choice bar,
short labels), `Interface` (wheel, satchel, menus, save/load, notepad), `Pause`, `Presentation` (settings, poses),
`Puzzles` (cancel, retry, migration), `Inheritance` (`#if TOOLS` contracts, Ink reset)). It may seed state to reach
a branch quickly; the playthrough may not.

### `WalkTest` (`--walk-test`)

See [Rooms and scenes](rooms-and-scenes.md#invariants-checked-by-tests).

### Film mode (`--film[=1|2|4|8|16|60|hyper]`)

The playthrough to watch, from the title to "The End": speed 1x-60x (`hyper` = 60x with the frame rate uncapped),
ending `2` unless `--ending` is given. `--from=act1|interlude1|act2|interlude2|act3|ending` starts at a chapter
(`ending` = the route's deciding scene; `act3` with `1-steps` is refused): the earlier story still plays for real,
muted at 60x behind a black "Fast-forwarding" cover (`FilmCover`), so items and decisions are right; reaching
`ending` takes about one route's time. Choices linger on screen so you can read them. `SpectatorFilter` ignores
viewer input except Space (pause), F11 / Alt+Enter, and Esc (prints `FILM STOPPED`, exits 0). Uses real sound and
the test save/settings files. Log: `logs/film_<speed>x.log` (`..._from_<chapter>.log` with `--from`); `ERROR:`
lines are warnings here (no audio device logs errors).

Launchers: `film.ps1 -Speed <s> -Ending <n> -From <chapter>`;
`film.sh --speed <s> --ending <n> --from <chapter>`. Bash also accepts `-s <s>` and `--speed=<s>`.
Speed is optional and defaults to 1x in both launchers; Bash no longer accepts positional speed (`film.sh 4`).
Ending/chapter options are unchanged.
## Unit tests (`tests/*.Tests`)

Three `net10.0` xunit projects, sharing `tests/Directory.Build.props`: `Repentance.Rules.Tests` and
`Repentance.Audio.Tests` test the [Godot-free libraries](conventions.md#godot-free-libraries);
`Repentance.Content.Tests` (scene graph, story integrity, Ink walk) reads the repository's content and imports
`GodotInk.props` to compile the same Ink story.

| Class | Project | Checks |
|---|---|---|
| `ItemsTests` | Rules | Catalogue, ids, cash |
| `EndingsTests` | Rules | Resolution order and gates |
| `MicahKitTests` | Rules | Pinned items, act kits, debug kits |
| `NotesTests` | Rules | Pages, conditional lines, debug flags |
| `PuzzleTests` | Rules | Every puzzle rule, migration |
| `RecipeTests` | Rules | Recipe integrity, symmetry, refusals |
| `SaveDataTests` | Rules | Round trips, versions, corrupt input |
| `SceneGraphTests` | Content | Parses `.tscn`/`.cs`: exits and `ChangeRoom` targets exist, markers on the floor, all rooms reachable from the attic |
| `SoundSynthTests`, `MusicSynthTests` | Audio | Audibility, clipping, seams, cue parsing |
| `StoryIntegrityTests` | Content | Static story checks (below) |
| `InkWalkTests` | Content | Exhaustive Ink walk (below) |

Filter: `dotnet test tests/<Project> --filter <Name>`, or `dotnet test --filter <Name>` at the root for the whole solution.

### Story tests and allowlists

- `StoryIntegrityTests`: every knot called exists and every knot is reachable; every flag read is set and every flag
  set is read; every item exists and is obtainable; knots with only `*` choices are one-shot by design; every choice
  label fits (66 chars, `#short:` rules); `docs/saves-and-settings.md` and `Walkthrough.md` state the current save
  version.
- `InkWalkTests`: explores choice paths from every `Talk(...)` target, including repeat visits, under learned,
  cash-in-hand, all-true and 24 deterministic seeded worlds. Fails on Ink runtime errors and unreachable choices.

Add allowlist entries only with a reason. Tests reject stale entries.

| List | File | For |
|---|---|---|
| `OneShotKnots` | `StoryIntegrityTests.cs` | Knots with only `*` choices that the game plays once |
| `UnreadFlags` | same | Flags set only for tests or the recipe book |
| `UnsetFlags` | same | Flags set in a way the scan can't see |
| `IndirectItems` | same | Items given by code the scan can't follow |
| `UnreachedChoices` | `InkWalkTests.cs` | Choices no path reaches |
| `OffFloorEntries` | `SceneGraphTests.cs` | Entry markers allowed off the floor |
| `UnheardSounds` | `scripts/Debug/Playthrough.cs` | Sounds the story never plays |

## Art and launcher tests (Python)

- `tests/art/` (Pillow, NumPy): committed PNGs match their generators; lighting, geometry, overlay composition.
- `tests/test_character_art.py`: sprite sheet sizes, strips, alpha, determinism.
- `tests/test_run_scripts.py`: launcher argument parsing, cleaning, pass rules.

## Seeing what the game draws

Record frames instead of taking screenshots of the desktop:

```powershell
godot_console --path . --write-movie frames\f.png --fixed-fps 30 --quit-after 120 -- --room=lobby --skip-title
```

Then open the last PNG (480x270).
