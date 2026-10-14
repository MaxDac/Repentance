# Agent notes

Godot 4.7 .NET (C#) point-and-click game. See `README.md` for the full guide.

## Running the game autonomously (Windows)

Prefer the scripts in `tools/run/` (PowerShell `.ps1`, bash `.sh`). See `docs/testing-and-film-mode.md`.
They reset generated files (`.godot/`, `bin/`, `obj/`, `logs/`, `screenshots/`, `frames/`, test-only user data),
then `dotnet build` and import, and apply CI's pass rule. CI runs the same scripts.

```powershell
tools\run\test.ps1                                # all suites; summary + non-zero exit on failure
tools\run\test.ps1 -Suite unit, playthrough -NoClean   # unit|art|autoplay|settings|pause|walk|playthrough
tools\run\film.ps1 -Speed 4 -Ending 3 -NoClean   # film mode: 1|2|4, ending 1-5|1-oldman|1-steps
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
godot_console --path . -- --film=4 --ending=2   # watch-only, pass = "FILM OK"
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

- Update the beat in `scripts/Debug/Playthrough.cs` (the canonical story, also what film mode plays), or add one.
  Act 3 routes branch on `_route`; every route must still reach "The End".
- Add regressions for things that could break quietly to the matching act file in `scripts/Debug/AutoPlay/`
  (`AutoPlay.Act1.cs` ... `AutoPlay.Endings.cs`). Shared test helpers (input, puzzles, satchel, checks) live in
  `scripts/Debug/Harness.cs`, not in `AutoPlay`.
- `StoryIntegrityTests` (flags, knots, items, one-shot knots, save version in docs) and `InkWalkTests` (every
  conversation, every choice path, no Ink runtime error, every choice reachable) must stay green. Only add an
  allowlist entry (`OneShotKnots`, `UnreadFlags`, `UnsetFlags`, `IndirectItems`, `UnreachedChoices`,
  `UnheardSounds`) with a real reason; a knot with only `*` choices that the game can run twice is a dead end.
- Bump `SaveData.CurrentVersion` if the save format changes, and the version stated in README and Walkthrough.
- Inventory verbs and combinations that hold in any room go in `scripts/Story/` (not in `Game`).
- New items go in the act file in `scripts/Core/Items/` that introduces them.
- `Game`, `Hud` and `AutoPlay` are partial classes split by concern to keep merges conflict-free:
  add code to the partial file for its concern rather than to the main file.
