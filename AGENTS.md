# Agent notes

Godot 4.7 .NET (C#) point-and-click game. See `README.md` for the full guide.

## Running the game autonomously (Windows)

Always use `godot_console.exe`; the GUI `godot.exe` can return before the game finishes.

```powershell
dotnet build                                 # after C# changes; before the first import (Ink importer is C#)
godot_console --path . --headless --import   # required on a fresh checkout and after art/font/Ink changes
godot_console --path . -- --autoplay         # pass = output contains "AUTOPLAY OK"
godot_console --path . -- --settings-test    # pass = "AUTOPLAY OK"
godot_console --path . -- --pause-test       # pass = "PAUSE TEST OK"
godot_console --path . -- --walk-test        # pass = "WALK TEST OK" (movement in every room + mouse input)
dotnet test tests/Repentance.Tests/Repentance.Tests.csproj
py -3.14 -m unittest discover -s tests\art -v
```

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

`Walkthrough.md` is the story spec. Implement changes in `scripts/Rooms` and `dialogue/repentance.ink`,
and cover them in the matching act file in `scripts/Debug/AutoPlay/` (`AutoPlay.Act1.cs` ... `AutoPlay.Endings.cs`).

- Inventory verbs and combinations that hold in any room go in `scripts/Story/` (not in `Game`).
- New items go in the act file in `scripts/Core/Items/` that introduces them.
- `Game`, `Hud` and `AutoPlay` are partial classes split by concern to keep merges conflict-free:
  add code to the partial file for its concern rather than to the main file.
