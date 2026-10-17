# Developer documentation

Godot 4.7 .NET, C# (.NET 10), Ink via GodotInk; 480x270, generated art and synthesized audio.
Player controls: [root README](../README.md).

Normal play: `tools/run/game.sh` or `tools\run\game.ps1` cleans generated files, builds/imports and opens the
game; player saves/settings are preserved. Setup and cleanup options: [Getting started](getting-started.md#first-run).
Watch-only film: `tools/run/film.sh` (1x by default), or `--speed 4` / `-s 4`; see [Testing](testing.md).

## Reading order

1. [Getting started](getting-started.md) - toolchain, build, import, run, command-line options.
2. [Architecture](architecture.md) - boot, runtime objects, interactions and file map.
3. [Conventions](conventions.md) - where new code goes and contracts to preserve.
4. Use the reference for the area you are changing:

| Page | Covers |
|---|---|
| [Core framework](core-framework.md) | `Game` and its partials, `GameState`, `Player`, `Actor`, `Hotspot`, `WalkArea`, poses, helpers |
| [Rooms and scenes](rooms-and-scenes.md) | Room scene layout, room scripts, entries/exits, adding a room, scene invariants |
| [Story and dialogue](story-and-dialogue.md) | Ink conventions, `DialogueManager`, flags, items, acts, interludes, puzzles, endings |
| [Story overview](story-overview.md) | Spoiler recap; authoritative spec: [Walkthrough](../Walkthrough.md) |
| [UI](ui.md) | `Hud`, speech, choices, satchel, close-ups, verb wheel, menus, notepad, puzzle screens |
| [Audio](audio.md) | Synthesized sound effects and music |
| [Saves and settings](saves-and-settings.md) | Save format and versioning, slots, migration, `settings.cfg` |
| [Art pipeline](art-pipeline.md) | Python generators, asset formats, art tests |
| [Testing](testing.md) | Launchers, suites, harness, film mode, story tests, allowlists |
| [CI and release](ci-and-release.md) | CI jobs, `ci-ok`, exports, releases, the icon |
| [Conventions](conventions.md) | Code rules: partial classes, Godot-free code, inheritance, where new code goes |

## Other sources

- [Walkthrough](../Walkthrough.md) - story spec.
- [AGENTS](../AGENTS.md) and [skills](../.claude/skills/) - shared Copilot / Claude Code workflows.
- [Contributing](../CONTRIBUTING.md), [credits](../CREDITS.md), [code licence](../LICENSE),
  [content licence](../LICENSE-ASSETS.md).
