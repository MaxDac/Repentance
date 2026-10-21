# Agent rules

Godot 4.7 .NET / C# / Ink. Shared rules for Copilot and Claude Code (`CLAUDE.md` imports this file).
[Developer guide](docs/README.md). Skills for both agents: `.claude/skills/`.

| Task | Skill | Docs |
|---|---|---|
| Run the game or tests | `run-tests` | `docs/testing.md` |
| Story, dialogue, items, endings | `story-change` | `docs/story-and-dialogue.md` |
| New room, entry, exit, hotspot | `add-room` | `docs/rooms-and-scenes.md` |
| Music, sound, recorded piano | `music-change` | `docs/audio.md` |
| Finish work: commit, PR, CI | `pr-and-ci` | `docs/ci-and-release.md` |
| Publish a build | `release` | `docs/ci-and-release.md` |

## Workflow

1. Select local suites from [Testing](docs/testing.md#quick-reference): docs need none; C# needs `dotnet build`
   then `unit`. First launcher run clean, later `-NoClean`. Never the full clean suite or film mode unless asked.
   Run launchers through a subagent on the cheapest model that reports only results (`run-tests` skill).
2. A planning session that implements its plan ends with a PR, unasked: commit, push, list suites run in the PR,
   watch checks and fix until `ci-ok` is green (`pr-and-ci`). Never merge; never call work done with red, pending
   or missing checks.
3. Before opening a PR, list the open PRs. If any title does not start with `[NoStack]`, stack on them: rebase onto
   the top of that stack and target its branch, not `main`. Then register it in the native GitHub stack with `gh api`
   (append to the stack, or create one from the bottom PR) ([CI and release](docs/ci-and-release.md#stacked-pull-requests)).
4. A PR that adds or changes an image (generated art, sprites, UI, icons) shows it in the description: before and
   after previews, scaled up nearest-neighbour, attached with `gh pr edit --attach`
   ([CI and release](docs/ci-and-release.md#pull-requests)).

## Code rules

- Use [concern-specific partials](docs/architecture.md#partial-classes). Shared inventory behavior belongs in
  `scripts/Story/`; items in the introducing act's `src/Repentance.Rules/Items/` file.
- Keep [Godot-free libraries](docs/conventions.md#godot-free-libraries) (`src/`) free of Godot; Godot script classes stay in `Repentance.csproj`.
- Extend intended virtual hooks with required base initialization/cleanup. Godot resources: override
  `_ResetState()`, never hide `ResetState()`. No `new` or warning suppressions to hide inherited methods.
- Incompatible saved meaning: bump `SaveData.CurrentVersion` and the version sentences in
  `docs/saves-and-settings.md` and `Walkthrough.md`.
- Story changes update the spec, canonical playthrough and relevant regressions
  ([checklist](docs/story-and-dialogue.md#checklist-for-a-story-change)).
- [Allowlist entries](docs/testing.md#story-tests-and-allowlists) require a reason; fix content before exempting it.

## Running Godot

- Use `godot_console.exe` on Windows. Build before the first import (Ink importer is C#); import after a fresh
  checkout or art/font/Ink changes. Prefer launchers; the [test-suite pass rule](docs/testing.md#suites) includes log errors.
- Normal interactive play: `tools/run/game.sh` / `tools\run\game.ps1` cleans generated files, builds/imports and
  opens the title screen until the player quits. Player saves/settings are preserved; `--no-clean` / `-NoClean`
  skips deletion only. Runtime errors are warnings in `logs/game.log`; nonzero exits and build/import failures fail.
- Bash film speed is optional, default 1x: `film.sh --speed 4` or `film.sh -s 4`, never positional `film.sh 4`.
- Never run `--autoplay` or `--settings-test` with `--headless` (screenshots need a renderer).
- Bound diagnostic runs with `--quit-after N`, not normal interactive play;
  [record frames](docs/testing.md#seeing-what-the-game-draws), not desktop screenshots.
