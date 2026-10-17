<img src="assets/art/ui/icon.png" alt="Repentance icon: a white pixel-art cross on black" width="96" align="right">

# Repentance
*Chicago, 1927. The neon says HOTEL. The rain says nothing at all.*

A point-and-click noir adventure in the spirit of *Monkey Island 2*: a 480×270 pixel-art
game with a right-click verb wheel. Today, Daniel is clearing out the attic of the old house he just
bought when he finds the journal of Micah Jones, a private eye. In 1927, Teddy Harrington III, heir to
Harrington Steel, hired Micah to find his missing wife, Eleanor.

Built with **Godot 4.7 (.NET)** and **C#**, with dialogue written in **Ink** (via GodotInk).

## Quick start

Requires Godot 4.7.x **.NET** and the .NET 10 SDK.

Normal play: `tools/run/game.sh` (Linux) or `tools\run\game.ps1` (PowerShell). The launcher cleans generated
files, builds/imports and opens the game; player saves/settings are preserved. Use `--no-clean` / `-NoClean`
to skip deletion. For manual steps without cleanup:

```powershell
dotnet build                               # before the first import: the Ink importer is C#
godot_console --path . --headless --import # after a fresh clone or art/font/Ink changes
godot_console --path .                    # Windows: console executable; Linux: godot-mono
tools\run\test.ps1 -Suite unit             # tests (bash: tools/run/test.sh unit)
```

Setup and troubleshooting: [Getting started](docs/getting-started.md).
Automated play and film mode: [Testing](docs/testing.md).

## Documentation

- [docs/](docs/README.md): architecture, framework, rooms, story, UI, audio, saves, art, testing, CI and release.
- [Walkthrough.md](Walkthrough.md): the story spec and solution.
- [docs/story-overview.md](docs/story-overview.md): the game beat by beat.
- [AGENTS.md](AGENTS.md): rules for AI agents (Copilot and Claude Code); skills in `.claude/skills/`.

## Controls

- **Left click** on the floor to walk. Left click on an object does the obvious thing: talk to people,
  go through exits, look at everything else. A character drawn in front of an object is the one you point at.
  On the map of Chicago, hovering a place shows its description at the bottom and a left click goes there.
- **Right click** on an object opens the **verb wheel**: 👁 *Look*, ✋ *Hand* (take, use, open, push),
  👄 *Talk*, 🥾 *Kick*. Click an icon, or hold the right button and release it over one.
- **Satchel** (bottom right) or **I** opens the inventory. Left-click an item to hold it (a small icon follows the cursor), then click
  it on an object or person to use or give it (or on another item to combine them). Right-click
  anywhere to put it back. Right-click an item in the satchel to open its verb wheel.
- **N** (or look/hand on the notepad, always Micah's first satchel slot) opens Micah's notepad full screen.
  **< / >**, the arrow keys or the mouse wheel turn its pages; **N**, **Esc** or **X** close it. Showing the
  notepad works wherever only the information matters (Eleanor's likeness, the triquetra, the safe riddle,
  the crests, the Harrington address). Micah's lighter is always the second slot and lights every fire.
- Each act in 1927 starts with a reset satchel: the notepad, the lighter and only the items that act still
  needs (`MicahKit.ActKeep`).
- Click during speech to skip the line.
- **Space** pauses/resumes gameplay, even mid-sentence. The current dialogue, movement, and timers
  stay frozen until you resume; clicks do nothing while paused. Space is inactive on the title screen
  and inside the Esc menu.
- Puzzle close-ups have their own controls, **Reset**, and **Close / Esc**. They are untimed and allow
  unlimited retries. Unsubmitted settings reset when closed; collected clues remain available.
- Use the satchel's **< / >** page buttons when carrying more than twelve items. A held item can be
  combined with an item on another page.
- **Esc** opens the pause menu: *Resume*, *Save game*, *Load game*, *Settings*, *Quit to title*. The title screen offers
  *Continue* (most recent save), *New game*, *Load game* and *Settings*.

### Settings

Stored in `user://settings.cfg`, separate from saves:

- **Nudity**: Off by default (Eleanor's dressed club sprite); On uses the implied-nude variant.
- **Full screen**: Off by default; **F11** or **Alt+Enter** anywhere. Borderless, whole-pixel scaling.
- **Effects volume** (80%) and **Music volume** (70%): left click louder, right click quieter, steps of 10%.

All sound and music are synthesized at startup; there are no audio files. The game autosaves on every room change
and has three manual slots.

## Credits

See [CREDITS.md](CREDITS.md).

## License

Repentance is source-available and non-commercial. You may fork, modify and share it, but you
may not sell it or use it commercially.

- **Code** (`scripts/`, `scenes/`, `tests/`, `tools/`, project files): [PolyForm Noncommercial 1.0.0](LICENSE).
- **Creative content** (`assets/` art and audio, `dialogue/`, `docs/`, `Walkthrough.md`):
  [CC BY-NC-SA 4.0](LICENSE-ASSETS.md).
- Third-party components (GodotInk, the Silkscreen font) keep their own licences; see [CREDITS.md](CREDITS.md).

Contributions are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).
