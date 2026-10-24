# Getting started

## Toolchain

| Tool | Version | Used for |
|---|---|---|
| Godot **.NET** edition | 4.7.x (CI: 4.7.2) | Editor, import, running the game. The standard edition cannot load C# |
| .NET SDK | 10.x | Building `Repentance.csproj` (with its `src/` libraries), the xunit tests and `tools/music` |
| Python + Pillow + NumPy | 3.14 | Art generators and art tests only |
| `gh` | any | PRs, CI logs, releases |

**Windows**: unpack the Godot .NET editor (keep the whole folder, including `GodotSharp`). Use
`godot_console.exe` for anything automated: the GUI exe returns before the game ends.

**Arch / Omarchy**: `sudo pacman -Syu godot-mono dotnet-sdk` (`godot-mono`, not `godot`). Other distros: the .NET
download from [godotengine.org](https://godotengine.org/download/linux/), plus the .NET 10 SDK.

Launchers find Godot through `-Godot`/`--godot`, `GODOT`, `PATH` (`godot_console`, `godot-mono`, `godot4-mono`,
`godot4`, `godot`), then install folders. They reject builds without C#.

## First run

For normal interactive play, use a launcher:

```powershell
tools\run\game.ps1                         # bash: tools/run/game.sh
tools\run\game.ps1 -NoClean                # bash: tools/run/game.sh --no-clean
```

By default it removes generated caches/builds, logs, captures and test data, then builds, imports and opens the
title screen. Player saves and settings are preserved. `-NoClean`/`--no-clean` skips deletion, not build/import.
Use `-Godot <path>`/`--godot <path>` to choose an engine. The launcher waits until you quit; no automation or
timeout is added. Output goes to `logs/game.log`; runtime errors are reported as warnings, but a nonzero game
exit fails. Probe, build or import failures stop launch.

For the equivalent manual build/import/run steps without cleanup:

```powershell
dotnet build                               # 1. C# first: the Ink importer is a C# plugin
godot_console --path . --headless --import # 2. import art, fonts, compile Ink into .godot/
godot_console --path .                     # 3. play (or: --path . --editor, then F5)
```

Repeat step 1 after C# changes and step 2 after art, font or Ink changes. `.godot/` is gitignored; skipping the
import gives a grey title screen and the log line `Assets are not imported`.

Launchers:

```powershell
tools\run\test.ps1 -Suite unit            # xunit only; bash: tools/run/test.sh unit
tools\run\test.ps1 -Suite walk            # clean, build, import, run Godot
```

Cleaning, suite selection and film mode: [Testing](testing.md).

## Command-line options

User options go after `--`, e.g. `godot_console --path . --quit-after 600 -- --room=lobby --skip-title`.

| Option | Effect |
|---|---|
| `--skip-title` | Start a new game immediately |
| `--room=<scene> --entry=<marker>` | Start in a room. Seeds the notepad (`Notes.DebugStartFlags`), the act's kit (`MicahKit.DebugItems`) and the act for Act 2/3 rooms |
| `--flag=a,b` | Set flags before the start room loads |
| `--autoplay` | Regression run, screenshots to `screenshots/`. Marker `AUTOPLAY OK` |
| `--playthrough [--ending=N]` | Canonical story and every ending with save/load checks. Marker `PLAYTHROUGH OK` |
| `--film[=1\|2\|4\|8\|16\|60\|hyper] [--ending=N] [--from=<chapter>]` | Watch-only story run; chapters `act1`, `interlude1`, `act2`, `interlude2`, `act3`, `ending`. Marker `FILM OK` |
| `--settings-test` / `--pause-test` / `--walk-test` | Focused suites. Markers `SETTINGS TEST OK` / `PAUSE TEST OK` / `WALK TEST OK` |
| `--no-music` | Neither render nor play music (the requested track is still recorded). The launchers pass it to `settings`, `pause` and `walk`, which never check music |
| `--clock=fast\|normal` | Automated runs only: 60x (default) or 8x game time |

Endings: `1`-`14`, `1-oldman`, `1-steps`, `1-caleb`, `12-oldman`. Playthrough defaults to `all`; film defaults to `2` and rejects `all`.

Useful Godot options: `--quit-after N` (frames; use it for bounded diagnostic runs, not interactive play), `--headless`,
`--write-movie frames\f.png --fixed-fps 30` (record what the game draws, 480x270 PNGs), `--audio-driver Dummy`.

## Where your data goes

`user://` is `%APPDATA%\Godot\app_userdata\Repentance\` on Windows, `~/.local/share/godot/app_userdata/Repentance/`
on Linux.

| Path | Content |
|---|---|
| `user://saves/` | Player saves (`autosave`, `slot1`-`slot5`) |
| `user://settings.cfg` | Player settings |
| `user://autoplay_saves/<suite>/`, `user://autoplay_settings.cfg` | Isolated test/film data; see [Testing](testing.md#launchers-toolsrun) for cleanup |

## Troubleshooting

| Symptom | Cause |
|---|---|
| Grey title screen, fallback font, `Assets are not imported` | Run the import |
| `No loader found` for `.cs`, `Could not find type "CSharpScript"` | Non-.NET Godot build |
| Export exits 0 but no C# assemblies | `Repentance.sln` missing |
| Test passes its marker but the launcher fails | An `ERROR:` line in `logs/<suite>.log` |
| No sound; log says `falling back to the dummy driver` | No audio device at start; connect one, then **Restart sound** ([Audio](audio.md#lost-sound-device)) |
