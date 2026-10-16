# Agent notes

Godot 4.7 .NET (C#) point-and-click game. See `README.md` for the full guide.

## Workflow: local tests, then a PR, then CI

CI (`.github/workflows/ci.yml`) is what proves the game works: every suite, a Linux and Windows export, and the walk
test on the exported Linux build. Its `ci-ok` job is green only when all of them pass. So locally, run only the
minimum needed to be confident the change is right, and let CI run the rest.

Local minimum (Windows; first run clean, then add `-NoClean`). Pick the rows that match what you changed:

| Change | Run |
|---|---|
| Docs only (`*.md`, comments) | nothing |
| Any C# (`scripts/`, `tests/`) | `dotnet build`, then `tools\run\test.ps1 -Suite unit` |
| Story: `dialogue/repentance.ink`, `scripts/Rooms`, `scripts/Story`, items, endings, `Playthrough.cs` or `scripts/Debug/Playthrough/` | `-Suite unit, playthrough` |
| An AutoPlay act file or `Harness.cs` | add `autoplay` |
| Scenes: walk areas, hotspots, entries, exits | `-Suite unit, walk` |
| Art generators (`tools/art`) or `assets/art` | `-Suite art` (it compares the committed PNGs to the generators) |
| Settings menus / pause | `-Suite settings` / `-Suite pause` |
| CI, launchers (`tools/run`), export presets | nothing local beyond what you touched; CI checks it |

Don't run the full clean `tools\run\test.ps1` (about 10 minutes) or film mode before a PR unless the user asks.

Every planning session that implements its plan ends with a PR, without being asked:

1. Commit on the session branch and push it.
2. Open the PR (the app's create-PR tool, or `gh pr create`). In the description, list what changed and which
   local suites you ran.
3. Watch the PR's checks (`gh pr checks --watch`). If any job fails, read its log (`gh run view <id> --log-failed`,
   plus the uploaded `logs/` artifact), fix it, push, and repeat until `ci-ok` is green.
4. Never merge, or call the work done, while a check is red, pending or missing.

`ci-ok` is the required status check on `main` (the "main protection" ruleset), so nothing merges without the
whole suite passing. When adding a CI job, add it to `ci-ok`'s `needs`, not to the ruleset.

## Inheritance contracts

Extend matching behavior through its intended virtual hook, retaining required base initialization and cleanup.
For Godot resources, implement `_ResetState()` rather than hiding the public `ResetState()` entry point.
Use distinct names for unrelated operations, not `new` or warning suppressions to hide inherited members.
Valid overloads and overrides of intentionally empty hooks do not need redundant base calls.
CS0108/CS0114 are build errors; AutoPlay also checks for explicit same-signature method hiding.

## Running the game autonomously (Windows)

Prefer the scripts in `tools/run/` (PowerShell `.ps1`, bash `.sh`). See `docs/testing-and-film-mode.md`.
Run them through a subagent on the least powerful model (e.g. `claude-haiku-4.5`) that reports only the result and
failures; see the `run-game` skill (`.github/skills/run-game/SKILL.md`).
They reset generated files (`.godot/`, `bin/`, `obj/`, `logs/`, `screenshots/`, `frames/`, test-only user data),
then `dotnet build` and import, and apply CI's pass rule. CI runs the same scripts.

```powershell
tools\run\test.ps1                                # all suites; summary + non-zero exit on failure
tools\run\test.ps1 -Suite unit, playthrough -NoClean   # unit|art|autoplay|settings|pause|walk|playthrough
tools\run\film.ps1 -Speed 4 -Ending 3 -NoClean   # film mode: 1|2|4|8|16|60|hyper, ending 1-10|1-oldman|1-steps
tools\run\film.ps1 -Speed hyper -From ending -NoClean   # -From act1|interlude1|act2|interlude2|act3|ending
```

Godot logs go to `logs/<suite>.log`. Manual equivalents (always `godot_console.exe`; the GUI `godot.exe` can
return before the game finishes):

```powershell
dotnet build                                 # after C# changes; before the first import (Ink importer is C#)
godot_console --path . --headless --import   # required on a fresh checkout and after art/font/Ink changes
godot_console --path . -- --autoplay         # pass = output contains "AUTOPLAY OK"
godot_console --path . -- --playthrough      # pass = "PLAYTHROUGH OK" (story, every ending, save/load, sounds)
godot_console --path . -- --settings-test    # pass = "SETTINGS TEST OK"
godot_console --path . -- --pause-test       # pass = "PAUSE TEST OK"
godot_console --path . -- --walk-test        # pass = "WALK TEST OK" (movement in every room + mouse input)
godot_console --path . -- --film=4 --ending=2   # watch-only, pass = "FILM OK" (--from=act2 starts at a chapter)
dotnet test tests/Repentance.Tests/Repentance.Tests.csproj
py -3.14 -m unittest discover -s tests\art -v
```

- Don't run `--autoplay` or `--settings-test` with `--headless`: they take screenshots, which need a renderer
  (screenshots are skipped headless, but CI runs them windowed under xvfb).
- CI also fails a Godot run that logs `ERROR:`/`SCRIPT ERROR:` lines, even if the pass marker printed.
- `SceneGraphTests` (xunit) checks that every scene exit and every literal `ChangeRoom("room","entry")` call
  targets an existing entry marker, that markers and walk targets stand on the floor, and that every room is
  reachable from the attic. New rooms and entries must keep it green.
- `.godot/` is gitignored. Without the import step, nothing loads and the game logs
  `Assets are not imported`, showing a grey screen.
- To see what the game draws, record frames instead of taking a desktop screenshot:
  `godot_console --path . --write-movie <dir>\f.png --fixed-fps 30 --quit-after 120 [-- --room=lobby --skip-title]`,
  then view the last PNG. Frames are 480x270, the native resolution.
- Use `--quit-after N` (frames) on manual runs so the process always exits.
- `--autoplay` writes screenshots to `screenshots/` (gitignored).

## Story work

`Walkthrough.md` is the story spec. Implement changes in `scripts/Rooms` and `dialogue/repentance.ink`, then:

- Update the beat in the matching act file in `scripts/Debug/Playthrough/` (`Playthrough.Act1.cs` ...
  `Playthrough.Endings.cs`; the canonical story, also what film mode plays), or add one. Act 3 routes branch on
  `_route` (choices per route in `Playthrough.Endings.cs`); every route must still reach "The End".
  `Playthrough.cs` keeps the modes, the save/load round trip and the coverage gates.
- Add regressions for things that could break quietly to the matching act file in `scripts/Debug/AutoPlay/`
  (`AutoPlay.Act1.cs` ... `AutoPlay.Endings.cs`). Shared test helpers (input, puzzles, satchel, checks) live in
  `scripts/Debug/Harness.cs`, not in `AutoPlay`.
- `StoryIntegrityTests` (flags, knots, items, one-shot knots, save version in docs) and `InkWalkTests` (every
  conversation, every choice path, no Ink runtime error, every choice reachable) must stay green. Only add an
  allowlist entry (`OneShotKnots`, `UnreadFlags`, `UnsetFlags`, `IndirectItems`, `UnreachedChoices`,
  `UnheardSounds`) with a real reason; a knot with only `*` choices that the game can run twice is a dead end.
- Bump `SaveData.CurrentVersion` if the save format changes, and the version stated in README and Walkthrough.
- Choice labels must fit the choice bar (66 characters). For a longer line, add a `#short:` tag with the label to
  show and keep the spoken text; see `docs/dialogue-choice-labels.md`.
- Inventory verbs and combinations that hold in any room go in `scripts/Story/` (not in `Game`).
- New items go in the act file in `scripts/Core/Items/` that introduces them.
- `Game`, `Hud` and `AutoPlay` are partial classes split by concern to keep merges conflict-free:
  add code to the partial file for its concern rather than to the main file.
