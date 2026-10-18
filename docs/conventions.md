# Conventions

## Where code goes

| Code | Place |
|---|---|
| Room behavior | `scripts/Rooms/<Room>.cs` (one class per scene) |
| Inventory verbs and combinations valid in any room | `scripts/Story/` |
| Story puzzles shared by rooms | `scripts/Story/` (`StoryPuzzles`) |
| New items | the act file in `src/Repentance.Rules/Items/` that introduces them |
| Pure rules (puzzles, endings, recipes, notes, kits, save data, Ink scan) | `src/Repentance.Rules/` |
| Sound and music synthesis | `src/Repentance.Audio/` |
| UI | `scripts/UI/` (code-built, no scenes) |
| Test helpers shared by suites | `scripts/Debug/Harness.cs` |
| Canonical story steps | `scripts/Debug/Playthrough/Playthrough.<Act>.cs` |
| Regressions | `scripts/Debug/AutoPlay/AutoPlay.<Area>.cs` |
| Dialogue | `dialogue/repentance.ink` |
| Normal-game, film and test launchers / shared helpers | `tools/run/` |
| Recorded instrument notes and track renders (C#) | `tools/music/` |

## Partial classes

Use the concern-specific partial, not the main file. [File map](architecture.md#partial-classes).

## Godot-free libraries

The solution splits by concern; all projects share `Directory.Build.props` (nullable, CS0108/CS0114 as errors).

| Project | Contents | References |
|---|---|---|
| `Repentance.csproj` | The Godot game: `scripts/` (framework, rooms, story, UI, debug) | Rules, Audio, Godot, Ink |
| `src/Repentance.Rules` | `Items*`, `SaveData`, `PuzzleRules`, `SwipeGesture`, `Endings`, `Recipes`, `Notes`, `MicahKit`, `InkScan`, `RainWeather` | - |
| `src/Repentance.Audio` | `SoundSynth*`, `MusicSynth*`, `Recordings` | - |
| `tests/Repentance.Tests` | xunit | Rules, Audio, Ink |
| `tools/music` | Music tool | Audio |

The libraries have no Godot reference, so Godot types do not compile there; put the Godot side in a game class
(`Sfx`, `Music`, `SaveSystem`...). Godot only registers script classes (nodes, resources) from the game
assembly, so anything Godot-facing stays in `scripts/`. Everything keeps the `Repentance` namespace; members the
tests need but the game must not see are `internal` (the libraries grant `InternalsVisibleTo` to the tests).
`src/` has a `.gdignore` and `Repentance.csproj` excludes `src/**` from its own compile items. Add new projects
to `Repentance.sln`, which Godot needs for export.

## Inheritance contracts

- Extend behavior through its intended virtual hook (`OnEnter`, `OnLook`, `_ResetState()`...) and keep the base
  class's required initialization and cleanup.
- For Godot resources, implement `_ResetState()`; never hide the public `ResetState()`.
- Unrelated operations get distinct names. No `new` modifiers or warning suppressions to hide inherited members:
  CS0108 and CS0114 are build errors, and AutoPlay (`AutoPlay.Inheritance.cs`) also checks for same-signature
  hiding.
- Overloads, and overrides of intentionally empty hooks, need no redundant base call.

## Async and time

- Story code is `async Task`; launch independent sequences through `Game.Run` (sets `Busy`, reports exceptions;
  does not serialize concurrent calls). [Scripting API](core-framework.md#scripting-api-use-inside-gamerun).
- Wait with `Game.Wait` / game-time timers so the pause freezes it; never `Task.Delay`.

## Story text

Follow [Ink conventions](story-and-dialogue.md#ink-conventions) for choice labels, cues and voice.
Exact Scripture quotations use Douay-Rheims; paraphrases are identified in the
[story recap](story-overview.md#scripture). `Walkthrough.md` is the story spec.

## Comments and docs

Comment only what needs clarifying. Update the matching page in `docs/` with the change, and `Walkthrough.md` for
story changes.

Launcher changes also require consistent examples throughout `docs/`, `AGENTS.md`, `CLAUDE.md` and the shared
skills. Reuse `common.sh`/`common.ps1` for discovery, safe cleanup, build/import and logging; normal play's
marker-free execution must not disable film/test completion checks.
