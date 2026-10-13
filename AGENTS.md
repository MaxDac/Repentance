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
dotnet test tests/Repentance.Tests/Repentance.Tests.csproj
py -3.14 -m unittest discover -s tests\art -v
```

- `.godot/` is gitignored. Without the import step, nothing loads and the game logs
  `Assets are not imported`, showing a grey screen.
- To see what the game draws, record frames instead of taking a desktop screenshot:
  `godot_console --path . --write-movie <dir>\f.png --fixed-fps 30 --quit-after 120 [-- --room=lobby --skip-title]`,
  then view the last PNG. Frames are 480x270, the native resolution.
- Use `--quit-after N` (frames) on manual runs so the process always exits.
- `--autoplay` writes screenshots to `screenshots/` (gitignored).

## Story work

`Walkthrough.md` is the story spec. Implement changes in `scripts/Rooms` and `dialogue/repentance.ink`,
and cover them in `scripts/Debug/AutoPlay.cs`.
