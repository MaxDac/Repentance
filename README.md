<img src="assets/art/ui/icon.png" alt="Repentance icon: a white pixel-art cross on black" width="96" align="right">

# Repentance
*Chicago, 1927. The neon says HOTEL. The rain says nothing at all.*

## Purpose

Repentance is a **collaborative point-and-click adventure of Christian inspiration**. It is a non-profit project:
the game is free, it is built together by its contributors, and **nobody may profit from it**, from its code or from its content.
The licences below forbid every commercial use and every derivative work, so that the game stays what it is meant
to be: a story about sin, grace and repentance, offered freely.

## The game

A noir adventure in the spirit of *Monkey Island 2*: a 480×270 pixel-art game with a right-click verb wheel.
Today, Daniel is clearing out the attic of the old house he just bought when he finds the journal of Micah Jones,
a private eye. In 1927, Teddy Harrington III, heir to Harrington Steel, hired Micah to find his missing wife,
Eleanor.

Built with **Godot 4.7 (.NET)** and **C#**, with dialogue written in **Ink** (via GodotInk).

## Play

- Download a build from [Releases](https://github.com/MaxDac/Repentance/releases) when available, or run it from source:
  `tools\run\game.ps1` (Windows) or `tools/run/game.sh` (Linux). Setup: [Getting started](docs/getting-started.md).
- Controls and settings: [Playing](docs/playing.md).

## Contribute

Contributions of code, art, dialogue, tests and docs are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md).

- [docs/](docs/README.md): developer guide (architecture, rooms, story, UI, audio, saves, art, testing, CI and release).
- [Walkthrough.md](Walkthrough.md): the story spec and solution; [story overview](docs/story-overview.md).
- [AGENTS.md](AGENTS.md): rules for AI agents (Copilot and Claude Code); skills in `.claude/skills/`.

## License

Repentance is source-available, **non-commercial** and **no-derivatives**. You may play it and share it unchanged
for free. You may not sell it, use it commercially, or publish modified versions or other games built from it.
Forks are allowed only to propose changes to this repository through pull requests (see
[CONTRIBUTING.md](CONTRIBUTING.md)).

- **Code** (`scripts/`, `scenes/`, `tests/`, `tools/`, project files): [PolyForm Strict 1.0.0](LICENSE).
- **Creative content** (`assets/` art and audio, `dialogue/`, `docs/`, `Walkthrough.md`):
  [CC BY-NC-ND 4.0](LICENSE-ASSETS.md).
- Third-party components (GodotInk, fonts) keep their own licences; see [CREDITS.md](CREDITS.md).

## Credits

See [CREDITS.md](CREDITS.md).
