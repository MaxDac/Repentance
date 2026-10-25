# Testing

## Local test policy

CI runs every suite on every pull request ([CI and release](ci-and-release.md#ci-githubworkflowsciyml)), so agents
do not repeat them locally:

- Before a PR, the only local check is a quiet compile for C# or Ink changes:
  `dotnet build -v q -clp:ErrorsOnly`. Docs and config changes need nothing.
- Test suites, `test.ps1` / `test.sh`, `dotnet test` (even one `--filter`ed class), `harness`, film mode and frame
  capture run only when the user explicitly asks. Claude Code prompts before running them.
- A planning session that will change code asks the user which [test level](#test-levels) to run after
  implementation, records the answer in the plan, and runs that level before opening the PR.
- A failing check is diagnosed from its CI log and artifacts, read filtered to the failing lines
  ([Reading a CI failure](ci-and-release.md#reading-a-ci-failure)), then fixed and pushed; CI is the rerun.
- Tools that are not tests stay available when a task needs them: `tools/music render` to listen, art generation,
  `dotnet build`.

People running the game by hand are not bound by this; the rest of this page describes every suite and launcher.

### Test levels

Each level adds suites to the one above it. Level 0 is the default; level 5 is what CI runs. Run the first launch
of a level clean; later runs in the same session can use `-NoClean` / `--no-clean`.

| Level | Adds | Checks | Command (PowerShell; bash: `tools/run/test.sh <suites>`) |
|---|---|---|---|
| 0 None | `dotnet build` | It compiles; CI runs everything | `dotnet build -v q -clp:ErrorsOnly` |
| 1 Basic | `unit` | Rules, scene graph, story integrity, Ink walk, music synth; no Godot | `tools\run\test.ps1 -Suite unit` |
| 2 Tooling | `launcher`, `art` | Run scripts and generated art; Python, no Godot | `tools\run\test.ps1 -Suite unit, launcher, art` |
| 3 Interaction | `walk`, `settings`, `pause` | Movement in every room, menus, pause (a few minutes) | `tools\run\test.ps1 -Suite unit, launcher, art, walk, settings, pause` |
| 4 Story | `playthrough`, `resume-act2`, `resume-act3` | Every ending, save/load, resume in a fresh launch (~18 min more) | `tools\run\test.ps1 -Suite unit, launcher, art, walk, settings, pause, playthrough, resume-act2, resume-act3` |
| 5 Full | `autoplay` | Targeted regressions and screenshots: every suite, as CI | `tools\run\test.ps1` |

Exports, packaging and Android are never run locally ([What only CI runs](#what-only-ci-runs)).

Groups can also be picked on their own: answer the planning question with group names or suites, e.g.
`Basic, Story` or `unit, playthrough`, and only those run, in the launcher's order
(`tools\run\test.ps1 -Suite unit, playthrough, resume-act2, resume-act3`). The groups are those added at each level:
Basic, Tooling, Interaction, Story, and Full, which adds `autoplay`. `resume-act2` / `resume-act3` need
`playthrough` in the same run (it keeps the checkpoints they load).

## Quick reference

One entry point runs every local suite: `tools\run\test.ps1` (Windows) or `tools/run/test.sh` (Linux, macOS, Git
Bash). With no suite it runs `all`: unit tests (including story integrity and the Ink walk), art, launcher and every
Godot end-to-end suite, then prints a summary. `harness.ps1` / `harness.sh` run just the launcher tests.

```powershell
tools\run\test.ps1                           # everything, from a clean slate (~15 min)
tools\run\test.ps1 -Suite unit, walk         # some suites (first run clean)
tools\run\harness.ps1 -k film                # launcher tests only; extra arguments go to unittest
tools\run\test.ps1 -Suite unit -NoClean      # skip deletion of generated files
tools\run\film.ps1 -Speed 4 -Ending 5        # watch the game play itself
tools\run\film.ps1 -Speed hyper -From ending -Ending 8   # 60x, straight to the ending
```

```bash
tools/run/test.sh unit walk --no-clean
tools/run/harness.sh -k film
tools/run/film.sh --speed 4 --ending 5
tools/run/film.sh -s hyper --from ending --ending 8
tools/run/film.sh --ending prison-caleb-visits   # endings by title too; see film.sh --help
```

CI runs every suite on every PR; agents run them locally only on request ([policy](#local-test-policy)). With no
`-Suite`, the launcher runs all suites from a clean slate (~15 min). The table shows which suites cover a change:
the CI checks to watch, and what to run when a local run is requested.

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
| Launchers (`tools/run/`) | `launcher` |
| CI, export presets, `tools/package` | no local suite; validate the changed tooling, then CI ([CI only](#what-only-ci-runs)) |

## Suites

| Suite | Runs | Covers | Pass |
|---|---|---|---|
| `unit` | `dotnet test` on each `tests/*.Tests` project | Godot-free rules, scene graph, story integrity, Ink walk | exit code |
| `art` | Python `unittest` in `tests/` | Generated art matches the generators and contracts | exit code |
| `launcher` | `harness.ps1` / `harness.sh` (`tests/test_run_scripts.py`) | Game, test and film launchers, Bash and PowerShell, against fake Godot/dotnet; no Godot needed | exit code |
| `playthrough` | `--playthrough` | Canonical story, every ending, save/load after every beat, sound/music coverage | `PLAYTHROUGH OK` |
| `resume-act2`, `resume-act3` | `--playthrough --resume=act2\|act3` | A fresh launch loads a checkpoint `playthrough` kept and plays on to "The End" (run `playthrough` first) | `RESUME OK` |
| `autoplay` | `--autoplay` | Targeted regressions: puzzles, wrong items, mouse, wheel, inventory, notepad, poses, dialogue variants, seeded endings; screenshots | `AUTOPLAY OK` |
| `settings` | `--settings-test --no-music` | Content, display, volume settings, persistence, menus, both Eleanor variants | `SETTINGS TEST OK` |
| `pause` | `--pause-test --no-music` | Space freezes and resumes everything | `PAUSE TEST OK` |
| `walk` | `--walk-test --no-music` | Movement and reachability in every room, real mouse input | `WALK TEST OK` |

A Godot suite passes only if Godot exits 0, prints the marker, **and** `logs/<suite>.log` has no `ERROR:`,
`SCRIPT ERROR:`, `USER ERROR:` or `Unhandled exception` line (`Game.Run` turns exceptions into `GD.PushError`, so a
run can reach its marker after one). Test suites use `--audio-driver Dummy`; CI uses the same pass rule.
`settings`, `pause` and `walk` never check music, so they run with `--no-music`: rendering tracks keeps the CPU
and GC busy, and on a slow runner that stalls frames in timing-sensitive checks. `autoplay` and `playthrough`
assert that music plays, so they keep it on.
Every run quits through `Harness.Finish`, which calls `Timers.ReleasePending` first: if C# still holds a pending
`SceneTreeTimer` at quit, Godot aborts at shutdown ("Leaked unsafe reference", `!rc_owner`). Await timers through
`Timers.Wait`, not `ToSignal(GetTree().CreateTimer(...))`. `Finish` then waits for any music render still running
(`Music.StopRendering`; its worker forces a full GC) and runs the GC, waiting for pending finalizers: Godot's
shutdown disposes only the wrappers C# still holds, so one collected but not yet finalized leaks its object ("RID
allocations of type GodotShape2D were leaked") or is finalized mid-teardown. Dispose wrappers of scene-owned
resources you only read, as `Hotspot.ShapeRect` does. Don't drop a `GD.Load` result a later load can revive: Godot's
resource cache does not own it, so the GC can collect its wrapper, and if a load revives the cached resource before
the finalizer runs, Godot 4.7.2 keeps a dead GC handle and logs `Handle is not initialized` from
`SwapGCHandleForType` ([godot#124587](https://github.com/godotengine/godot/issues/124587)). Hold the wrapper and
`Dispose` it when done, as `Game.RoomPackedScene` and `Game.ReleaseRoomScenes` do for room scenes. Art that rooms
share (an actor's texture) can't be held that way, so `Game.FinalizeCollectedWrappers` runs the GC and waits for
pending finalizers before each room scene is loaded or instantiated.
A local pass does not cover exported builds; see [What only CI runs](#what-only-ci-runs).

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

`tests/test_run_scripts.py` tests the launchers themselves: the `launcher` suite, or `harness.ps1` / `harness.sh`
directly (CI's unit job runs it on Linux). It runs on Windows, Linux and macOS, each test through Bash and through
PowerShell 7 (`pwsh`); a missing shell skips its tests. On Windows, Bash is Git Bash, never the WSL `bash.exe`
stub; set `LAUNCHER_TEST_BASH` to choose another.

## What only CI runs

Every local suite above also runs in CI ([CI and release](ci-and-release.md#ci-githubworkflowsciyml)). These
checks run only in CI, because they need export templates, packaging tools or a clean Windows machine:

- `export (linux / windows)`: exports both presets, builds the AppImage and Windows installer, runs `--walk-test`
  from the AppImage, checks the `.exe` icon and the desktop entry.
- `android-export`: a debug-signed APK with the C# assembly inside.
- `windows-installer`: silent install, shortcut and uninstall checks.

For changes touching these, push and watch CI (`pr-and-ci` skill); [Export](ci-and-release.md#export) shows the
matching local export command.

## The harness (`scripts/Debug/`)

`Harness` supplies `--clock` (fast 60x by default, normal 8x; restored to 1x at the end), checks, failure accounting,
markers and exit codes, `WaitIdle`/`Until`/`Observe`, synthetic mouse and
keyboard input (`Viewport.PushInput`), screenshots to `screenshots/`, a wiped per-suite save folder, and shared
puzzle/satchel helpers. Put new shared helpers here, not in `AutoPlay`. `Harness.Begin` turns off
`Game.EndReturnsToTitle`, so "The End" stays up for the ending checks (players leave it for the title with a click,
a key or `Game.TheEndSeconds`; `AutoPlay` checks that with the setting back on).

`game.Wait`, `WaitIdle` and `Until` count game seconds, which the clock scales; `Observe` counts real seconds. Wait
with `Observe` for anything timed in real time, such as the touch long press (`TouchPointer.HoldSeconds`).

### `Playthrough` (`--playthrough`, `--film`)

Named beats (`Beat(id, body)`) walk, look, use items, solve puzzles and pick choices. Beats:
`Playthrough/Playthrough.Act1.cs` ... `Act3.cs`; Act 3 routes branch on
`_route`, and `Playthrough.Endings.cs` holds each route's choices and "The End" checks. `Playthrough.cs` keeps the
modes, the save/load round trip and the coverage gates.

- Acts 1-2 play once; at the Club vestibule the run saves, then reloads that save for every route: `2 3 4 5 6 7
  7-alone 1 1-oldman 1-steps 1-steps-caleb 1-caleb 1-bed 15 15-caleb 15-steps 15-steps-caleb 15-oldman 15-bed 8
  8-kill 9 9-kill 10 11 12 12-oldman 12-bed 13 13-caleb 14 14-caleb` (every ending, and every variant with its own
  scenes). No seeded state. `--ending=N` runs one route.
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
(`ending` = the route's deciding scene; `act3` with a `-steps` route is refused): the earlier story still plays for real,
muted at 60x behind a black "Fast-forwarding" cover (`FilmCover`), so items and decisions are right; reaching
`ending` takes about one route's time. Choices linger on screen so you can read them. `SpectatorFilter` ignores
viewer input except Space (pause), F11 / Alt+Enter, and Esc (prints `FILM STOPPED`, exits 0). Uses real sound and
the test save/settings files. Log: `logs/film_<speed>x.log` (`..._from_<chapter>.log` with `--from`); `ERROR:`
lines are warnings here (no audio device logs errors).

Launchers: `film.ps1 -Speed <s> -Ending <n|title> -From <chapter>`;
`film.sh --speed <s> --ending <n|title> --from <chapter>`. Bash also accepts `-s <s>` and `--speed=<s>`.
Speed is optional and defaults to 1x in both launchers; Bash no longer accepts positional speed (`film.sh 4`).
The launchers also take each ending by a case-insensitive title and pass Godot the number; the table is in
`film.sh --help` and `Get-Help tools\run\film.ps1 -Parameter Ending`:

| Number | Title | Route |
|---|---|---|
| 1 | `walk-away` | Micah lowers the gun on Tony; coffee with Rose |
| 1-oldman | `spare-the-old-man` | He prays the Our Father and spares the old man; coffee with Rose |
| 1-steps | `give-up` | He gives up on the cathedral steps; coffee with Rose |
| 1-steps-caleb | `give-up-eleanor-escapes` | As 1-steps, and Eleanor held out; Rose, then Eleanor and Caleb |
| 1-caleb | `eleanor-escapes` | Eleanor held out, he lowers the gun on Tony; Rose, then Eleanor and Caleb |
| 1-bed | `eleanor-back-to-bed` | Eleanor held out, he prays; she goes back to bed, he goes to Rose |
| 2 | `escape-together` | Evidence or fire, Eleanor convinced; out of town with her |
| 3 | `escape-alone` | Evidence or fire, Eleanor not convinced; out of town alone |
| 4 | `prison-eleanor-visits` | Neither, Eleanor convinced; prison, Eleanor visits |
| 5 | `prison-caleb-visits` | Neither, Eleanor not convinced; prison, Caleb visits |
| 6 | `turn-himself-in` | He turns himself in; prison, Rose visits |
| 7 | `last-entry` | He shoots Eleanor, then himself; Caleb writes the last entry |
| 7-alone | `last-entry-alone` | Four turns without her, the footsteps; he shoots himself alone |
| 8 | `eleanor-burns-the-house` | Eleanor strikes the old man and burns the cellar; Rose, then Eleanor alone |
| 8-kill | `kill-tony-eleanor-burns` | As 12-oldman, Eleanor held out; she strikes him and burns the cellar |
| 9 | `eleanor-confesses` | Eleanor strikes the old man; Rose, then she confesses to Caleb in prison |
| 9-kill | `kill-tony-eleanor-confesses` | As 12-oldman, Eleanor held out; she strikes him and confesses to Caleb |
| 10 | `she-leaves-by-the-car` | Eleanor follows after the shot, evidence or fire; she leaves him by the car |
| 11 | `she-visits-once` | Eleanor follows after the shot, nothing taken; prison, she visits once |
| 12 | `kill-tony-surrender` | He kills Tony, confesses to Caleb and turns himself in; prison, Caleb visits |
| 12-oldman | `kill-tony-pray` | He kills Tony, confesses, spares the old man, then gives himself up |
| 12-bed | `kill-tony-eleanor-back-to-bed` | As 12-oldman, Eleanor held out; she goes back to bed, he to the station |
| 13 | `alarm-run` | A warning shot; the unseen alarm rings and he runs; out of Chicago, alone |
| 13-caleb | `alarm-run-eleanor-escapes` | As 13, and Eleanor held out; then Eleanor and Caleb at the city's edge |
| 14 | `alarm-ambush` | A warning shot; the unseen alarm rings and he goes in; shot in the kitchen |
| 14-caleb | `alarm-ambush-eleanor-escapes` | As 14, and Eleanor held out; then Eleanor and Caleb at the city's edge |
| 15 | `sunday-visits` | He walks away from Tony without having pressed Rose; she refuses the coffee |
| 15-caleb | `sundays-eleanor-escapes` | As 15, and Eleanor held out; Rose's door, then Eleanor and Caleb |
| 15-steps | `sundays-give-up` | As 1-steps without having pressed Rose; she refuses the coffee |
| 15-steps-caleb | `sundays-give-up-eleanor-escapes` | As 15-steps, and Eleanor held out; Rose's door, then Eleanor and Caleb |
| 15-oldman | `sundays-spare-the-old-man` | As 1-oldman without having pressed Rose; she refuses the coffee |
| 15-bed | `sundays-eleanor-back-to-bed` | As 1-bed without having pressed Rose; she refuses the coffee |

Numbers follow [Branches and endings](story-overview.md#branches-and-endings).
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
- `tests/test_run_scripts.py` (`launcher` suite): launcher argument parsing, cleaning, pass rules, Godot discovery,
  ending titles.

## Seeing what the game draws

Record frames instead of taking screenshots of the desktop:

```powershell
godot_console --path . --write-movie frames\f.png --fixed-fps 30 --quit-after 120 -- --room=lobby --skip-title
```

Then open the last PNG (480x270).
