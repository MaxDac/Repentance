# Testing and film mode

Everything that checks the story, and how to watch the whole game play itself.

## Quick start

Windows (PowerShell):

```powershell
tools\run\test.ps1                      # every suite, from a clean slate
tools\run\test.ps1 -Suite unit, walk    # just some suites
tools\run\film.ps1                      # film mode, 1x
tools\run\film.ps1 -Speed 2
tools\run\film.ps1 -Speed 4 -Ending 5
```

### Linux prerequisites

Repentance needs Godot 4.7.x **.NET/Mono** and the **.NET 10 SDK**. On Arch Linux / Omarchy:

```bash
sudo pacman -Syu godot-mono dotnet-sdk
godot-mono --version
dotnet --list-sdks                 # must include a 10.x SDK
```

Install **`godot-mono`**, not `godot`: the standard `godot` package has no C# support.
The launchers select `godot-mono` automatically; manual Godot commands on this distribution should also use
`godot-mono` (for example, `godot-mono --path . --editor`).
Other distributions can use the official **.NET** editor download described below.

### Bash launchers (Linux / macOS / Git Bash)

```bash
tools/run/test.sh
tools/run/test.sh unit walk
tools/run/film.sh            # 1x
tools/run/film.sh 2
tools/run/film.sh 4 --ending 5
```

Both scripts find Godot 4 .NET in this order: `-Godot <path>` / `--godot <path>`, then the `GODOT` environment
variable, then `godot_console`, `godot-mono`, `godot4-mono`, `godot4` or `godot` on `PATH`, then the usual install folders (on Windows,
`%LOCALAPPDATA%\Godot`). Each executable is checked for Godot 4 with C# support **before any clean reset**.
Automatic discovery skips incompatible executables; an incompatible explicit path or `GODOT` value fails immediately.
Python 3 with `pillow` and `numpy` is needed for the art suite only; it's found on
`PATH`, in `%LOCALAPPDATA%\Programs\Python`, or through the `PYTHON` environment variable.

The standard Godot edition cannot run this C# game. If the log says `No loader found` for `.cs` files or
`Could not find type "CSharpScript"`, install the **.NET/Mono** editor from
[Godot's downloads](https://godotengine.org/download/archive/) and point the launcher at its executable:

```bash
tools/run/film.sh --godot "$HOME/godot/Godot_v4.7.2-stable_mono_linux_x86_64/Godot_v4.7.2-stable_mono_linux.x86_64"
# Or set GODOT once for both launchers:
export GODOT="/path/to/Godot_dotnet_executable"
```

### Clean reset

Unless you pass `-NoClean` / `--no-clean`, both scripts first delete everything generated and start anew:

- `.godot/` (the import cache, including the compiled Ink), `.mono/`, `bin/`, `obj/`, and `tests/**/bin|obj`;
- `screenshots/`, `frames/`, `logs/`;
- the test-only user data: `user://autoplay_saves/` and `user://autoplay_settings.cfg`
  (on Windows, under `%APPDATA%\Godot\app_userdata\Repentance\`).

Then they run `dotnet build` and `godot --headless --import` (the build comes first, because the Ink importer is C#).
Import output is saved to `logs/import.log`; a nonzero exit or an error line stops the launcher before the game starts,
including in film mode.
**Your own saves (`user://saves/`) and settings (`user://settings.cfg`) are never touched.**

## Film mode

Plays the game by itself from the title screen to "The End", the way the story should go, and quits. It's for
watching: your mouse and keyboard can't skip lines or change anything. Only these keys work:

| Key | Action |
|---|---|
| Space | Pause / resume |
| F11 (or Alt+Enter) | Full screen |
| Esc | Stop the film and quit |

| Option | Values |
|---|---|
| Speed (`-Speed`, first argument in bash) | `1` (normal), `2`, `4` |
| Ending (`-Ending`, `--ending`) | `2` (default), `1`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10` (Eleanor's endings: she refuses both times), plus the other two ways to reach ending 1: `1-oldman`, `1-steps` |

When Micah has a decision to make, the choices stay on screen for a moment and the one picked is highlighted before
the story continues. The film uses the test-only save and settings files and plays with real sound.
The log goes to `logs/film_<speed>x.log`. Unlike the tests, `ERROR:` lines in the log are shown as warnings rather
failing the film (without an audio device, for instance, Godot logs WASAPI errors and plays silently); the test
suites run with `--audio-driver Dummy`.

Without the scripts: `godot_console --path . -- --film=2 --ending=3` (after a build and import).

## The suites

| Suite | What it covers | Pass marker |
|---|---|---|
| `unit` | xunit: save data, puzzles, notes, scene graph, plus the story checks below | `dotnet test` exit code |
| `art` | Python regression tests for the generated art | `unittest` exit code |
| `playthrough` | The canonical story, every ending route, save/load everywhere, sound coverage | `PLAYTHROUGH OK` |
| `autoplay` | Targeted regressions: puzzles cancelled and retried, wrong items, mouse, wheel, inventory, notepad, poses, dialogue variants, endings via seeded state | `AUTOPLAY OK` |
| `settings` | Content, display and volume settings, persistence and menus | `SETTINGS TEST OK` |
| `pause` | Space pause/resume freezes and resumes everything | `PAUSE TEST OK` |
| `walk` | Movement in every room, reachability of every hotspot and exit, real mouse input | `WALK TEST OK` |

A Godot suite passes only if Godot exits with status 0, the marker is printed, **and** the log has no
`ERROR:`, `SCRIPT ERROR:`, `USER ERROR:` or `Unhandled exception` line. `Game.Run` turns script exceptions into
`GD.PushError`, so a run can reach its marker after one. Godot logs are in `logs/<suite>.log`; AutoPlay screenshots
are in `screenshots/`. CI runs the very same scripts (`.github/workflows/ci.yml`), so a local pass means a CI pass.

### CI: what gates a merge

`.github/workflows/ci.yml` runs on every pull request and every push to `main`:

| Job | What it does |
|---|---|
| `unit-tests` | `tools/run/test.sh unit` |
| `art-tests` | `tools/run/test.sh art` |
| `godot-tests (<suite>)` | `tools/run/test.sh <suite>` for `autoplay`, `settings`, `pause`, `walk` and `playthrough`, under xvfb |
| `export (linux / windows)` | Exports the `Linux` and `Windows Desktop` presets exactly as `release.yml` does; the Linux build then runs `--walk-test` itself, so the shipped build is proven to boot and load every room |
| `ci-ok` | Passes only if every job above passed |

`ci-ok` is the only required status check on `main` (the "main protection" ruleset, under Settings → Rules), so a
pull request can't be merged until the whole suite passes. New jobs go in `ci-ok`'s `needs`, not in the ruleset. Godot (and its export templates) are installed by the shared
`.github/actions/setup-godot` action, which `release.yml` uses too.

Because CI runs everything, local runs before a pull request can be limited to the suites that match the change;
`AGENTS.md` has the table.

All the Godot suites share one harness (`scripts/Debug/Harness.cs`): the `--clock` option, the checks and the
marker, waits, mouse input, screenshots, and a separate save folder per suite (`user://autoplay_saves/<suite>`).

### `--playthrough`: the story, end to end

`Playthrough` is the single description of how the story should go. It's a list of named beats
(`attic`, `office`, `lobby`, … `club_stage`, then the Act 3 beats), each doing what a player does: walk, look, use
items, solve the puzzles and pick the choices. The beats live in one file per act in `scripts/Debug/Playthrough/`
(`Playthrough.Act1.cs`, `Act2`, `Act3`, and `Endings` for the choices each route takes and the checks on "The End");
`scripts/Debug/Playthrough.cs` keeps the modes, the save/load round trip and the coverage gates.

- **Every ending, for real.** Acts 1 and 2 are played once. At the Club vestibule the run saves to a manual slot,
  then reloads that save and plays each Act 3 route through to "The End": endings 2, 3, 4, 5, 6, 7 and the three ways to
  ending 1 (Tony, the old man, the steps). No state is seeded.
- **Decisions.** Every Ink choice the beats pick is logged; the run fails if a choice its route wants is never offered by the time the route reaches "The End".
- **Save/load at every beat.** After each beat the game saves, loads that save and compares the flags, items, act,
  room, position and Ink state. A save that doesn't restore exactly what was there fails the run.
- **No dead ends.** A beat that can't reach what it needs (an exit, an item, a choice) times out and fails, naming
  the beat. A story that stops early never prints the marker.
- **Sound.** Every `Sound` effect must be played at least once over the whole run. A sound that's never heard
  must be listed in `UnheardSounds` with a reason (the list is empty). Every music `Track` must also play at least
  once.

`--ending=N` (or `all`, the default) limits the run to one route.

### Story checks in xunit

- **`StoryIntegrityTests`**: static checks over `dialogue/repentance.ink`, the C# and the scenes.
  - every knot the game calls exists, and every knot is called or diverted to;
  - every flag that is read can be set, and every flag that is set is read;
  - every item exists and can be obtained;
  - knots with only one-time (`*`) choices are listed in `OneShotKnots` with the reason the game plays them once
    (otherwise a second conversation runs Ink out of content, as the convent nun once did);
  - `README.md` and `Walkthrough.md` state the current save version.
- **`InkWalkTests`**: an exhaustive walk of every conversation the game starts. It compiles the Ink and, from each
  `Talk(...)` target, tries every path of choices, talking again where the game allows it, in the story's world, with
  every flag on and in 24 random worlds. It fails on any Ink runtime error (a dead end) and on any choice no path can
  reach (unless it's listed in `UnreachedChoices`).

The parser both use is `scripts/Core/InkScan.cs` (Godot-free, linked into the test project).

## Allowlists

Each one needs a reason next to every entry, and each fails when an entry is no longer needed.

| List | File | For |
|---|---|---|
| `OneShotKnots` | `tests/Repentance.Tests/StoryIntegrityTests.cs` | Knots with only one-time choices that the game plays once |
| `UnreadFlags` | same | Flags set only so tests or the recipe book can check them |
| `UnsetFlags` | same | Flags read but set in a way the scan can't see |
| `IndirectItems` | same | Items given by code the scan can't follow |
| `UnreachedChoices` | `tests/Repentance.Tests/InkWalkTests.cs` | Ink choices no conversation path reaches |
| `UnheardSounds` | `scripts/Debug/Playthrough.cs` | Sounds the story never plays |

## Changing the story

1. Update `Walkthrough.md` (the spec), then `scripts/Rooms` and `dialogue/repentance.ink`.
2. Update the matching beat in the act file in `scripts/Debug/Playthrough/` so the canonical story still plays through; add a beat for a new
   room or step.
3. Add a regression to the matching act file in `scripts/Debug/AutoPlay/` for anything that could break quietly (a wrong item, a cancelled puzzle).
4. Run the suites that match the change (`tools\run\test.ps1 -Suite unit, playthrough`, plus `autoplay` if you added a
   regression) and open a pull request; CI runs every suite and the exports. Watch `tools\run\film.ps1 -Speed 4` when
   you want to see the new story play.
5. If the save format changes, bump `SaveData.CurrentVersion` and the version stated in `README.md` and
   `Walkthrough.md` (a test checks they agree).
