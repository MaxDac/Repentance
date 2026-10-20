# Core framework (`scripts/Core`)

## `Game` (`Game.cs` + `Game/`)

Controller on `Main`; rooms access `Game.Instance` through `Room.Game`.
File map: [Architecture: Partial classes](architecture.md#partial-classes).
Entry points: `Perform` (scripted world verbs; private `Execute` dispatches), `ItemVerb` (inventory), `ChangeRoom` (travel),
`CanSave` / `CaptureSave` / `SaveToSlot` / `LoadGame` (persistence), `TogglePause` (Space pause).

To exercise normal startup and player input, use `tools/run/game.sh` / `tools\run\game.ps1`; they build/import
before opening the title screen, without enabling a debug harness. [Launch options](getting-started.md#first-run).

### Scripting API (use inside `Game.Run`)

Inside a `Room` subclass:

```csharp
await Game.Run(async () =>
{
    await Game.WalkTo(new Vector2(372, 204));    // pathfinds; ClampWalkTarget applies
    await Say("Micah says this.");               // player speaks
    await Say("concierge", "An actor speaks.");   // Actor or Voice id in this room
    await Think("Journal narration, top of screen.");
    await Talk("concierge");                      // run an Ink knot
    await Wait(0.5);                              // game-time seconds, freezes on pause
    await Game.ChangeRoom("hotel_linen", "lift");
});
```

- `Run` increments a busy counter; it does not queue or serialize concurrent calls. Input is ignored and the
  interface hidden while busy. Exceptions go to `GD.PushError` and `SequenceFailed`.
- `Execute` already wraps `OnInteract`; `DialogueManager.Talk` wraps itself. Use `Run` for independent sequences
  from `OnEnter`, `_Process` or signals; guard against starting one on every frame.
- Speech lasts by text length; a click skips the line. Lines starting with `*` play sound cues (see
  [Audio](audio.md)).
- `Game.Hud` gives access to the UI: `Game.Hud.Puzzle.Open(PuzzleKind.Lift)`, `ShowCloseUp`, fades, images.

## `GameState` (autoload)

| Member | Notes |
|---|---|
| `HasFlag`, `SetFlag(flag, value = true)` | Flags are free-form snake_case strings; `SetFlag(f, false)` clears one. `Reset` starts with the puzzle schema flags only |
| `Inventory`, `HasItem`, `GiveItem`, `TakeItem` | Ordered list; notepad and lighter stay pinned first (`EnsurePinned`/`RemovePinned`) |
| `StoryAct`, `SetStoryAct` | 1-3, clamped |
| `Changed` | Emitted on every effective change |
| `Reset`, `CaptureInto(SaveData)`, `Restore(flags, inventory, storyAct)` | New game and save/load |

`FlagRules.Evaluate(show, hide)`: all comma-separated `show` flags set and none of `hide`. Used by hotspots and
`FlagSprite`.

## World objects

| Type | Base | Purpose |
|---|---|---|
| `Room` | `Node2D` | One location; see [Rooms and scenes](rooms-and-scenes.md) |
| `Hotspot` | `Area2D` | Clickable thing. Exports `Id`, `DisplayName`, `LookText`, `WalkTo` (zero = auto), `Face`, `ExitTo`, `ExitEntry`, `ShowIfFlags`, `HideIfFlags`, `ClickPriority`. Area = child `CollisionShape2D`/`CollisionPolygon2D` |
| `Actor` | `Hotspot`, `ISpeaker` | NPC. Exports `Texture`, `Frames` (11), `FlipH`, `Baseline`, `DepthScale`, `SpeechColor`. No collision shape = sprite rectangle; opaque pixels win clicks. `MoveTo` (straight line), `FaceLeft`, `SetPose`, `PlayPose`, `SetTexture` |
| `Player` | `Node2D`, `ISpeaker` | Created once, reparented into each room's `World`. Position = feet. `SetCharacter("micah"\|"daniel"\|...)`, `WalkPath`, `Stop`, `Face`, `FaceTowards`, `Teleport`, `SetPose`, `PlayPose`, `SetPoseFrame`, `BackstepTo`. Speed 90 |
| `Voice` | `Node2D`, `ISpeaker` | Speaker placed where its text shows (`Id`, `SpeechColor`); an optional `Mouth` 3-frame sprite moves its painted lips while it talks |
| `WalkArea` | - | Visibility-graph pathfinder over the `WalkArea` polygon: `Contains`, `Clamp`, `FindPath` |
| `FlagSprite` | `Sprite2D` | Shown/hidden by `ShowIfFlags`/`HideIfFlags` |
| `LoopStrip` | `FlagSprite` | Flag-driven looping strip (`FrameSeconds`) |
| `IdleStrip` | `Sprite2D` | Intermittent idle animation (`Sequence`, `MinRest`, `MaxRest`, `Seed`) |
| `Rain` | `Node2D` | Procedural rain in areas, heavier each act (`RainWeather`, unless `FollowsStory = false`); panes a muntin apart share one field (`RainPanes`), so streaks carry on across the bars; also drives the rain ambience |
| `PosePlayback` | - | Plays pose strips for `Player` and `Actor` from their JSON metadata |

`Verb`: `Walk`, `Look`, `Hand` (take, open, use), `Talk`, `Kick` (also push/pull), `UseItem` (held item).
`Facing`: `Auto`, `Down`, `Up`, `Left`, `Right`.

### Sprites and poses

- Player and NPC sheet formats: [Art pipeline: Asset contracts](art-pipeline.md#asset-contracts).
  Player row 0: 3/4 idle, side walk x8, 3/4 talk. Row 1: front idle, walk x6, talk A/B. Row 2: back idle, walk x6.
- Outfits: `ResolvePlayerCharacter` picks `micah_masked` (flag `masked`), `micah_no_tie` (`bell_wedged`) or
  Eleanor's sheet during interludes. A pose `micah_x` uses the outfit's own copy when it exists.
- Pose playback and metadata: [Art pipeline: Action strips and poses](art-pipeline.md#action-strips-and-poses).

## Dialogue, items, rules

Godot-free types live in `src/Repentance.Rules/`; the rest in `scripts/Core/`.

| Type | File | Godot-free | Purpose |
|---|---|---|---|
| `DialogueManager` (autoload) | `DialogueManager.cs` | no | Runs Ink; see [Story and dialogue](story-and-dialogue.md) |
| `InkScan` | `InkScan.cs` | yes | Parses Ink lines (prefixes, choice labels) for runtime and tests |
| `Items`, `ItemDef` | `Items.cs`, `Items/*.cs` | yes | Item catalogue |
| `CashRules` | `Items.cs` | yes | Micah's cash (starts at 22 dollars) |
| `MicahKit` | `MicahKit.cs` | yes | Pinned items, per-act kit, debug kits |
| `Notes` | `Notes.cs` | yes | Notepad pages unlocked by flags |
| `Recipes` | `Recipes.cs` | yes | Declarative item combinations and refusal hints |
| `PuzzleRules`, `PuzzleMigration` | `PuzzleRules.cs` | yes | Puzzle answers and save normalization |
| `Endings` | `Endings.cs` | yes | Ending resolution |

## Other services

| Type | Purpose |
|---|---|
| `SaveData`, `SaveSystem` | Save model (Godot-free) and slot files; see [Saves and settings](saves-and-settings.md) |
| `GameSettings` | `settings.cfg` |
| `WindowModeController` | Full screen toggle (F11, Alt+Enter) |
| `Sfx`, `SoundSynth` | Sound effects; see [Audio](audio.md) |
| `Music`, `MusicSynth` | Music |

## Time

- Gameplay uses Godot's game time; `Wait` timers stop when the tree is paused.
- `_playtime` accumulates in `_Process` and is saved.
- Only test and film runs change `Engine.TimeScale` (60x fast clock, 8x normal, film 1-60x).
