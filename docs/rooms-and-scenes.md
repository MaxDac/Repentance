# Rooms and scenes

38 rooms. Each is `scenes/rooms/<scene>.tscn` (snake_case; the id used by `ChangeRoom` and `ExitTo`) with a
script `scripts/Rooms/<PascalCase>.cs` deriving from `Room` (namespace `Repentance.Rooms`).

## Scene layout

```text
<Room>            Node2D, room script
  Background      Sprite2D 480x270, Centered off (assets/art/rooms/)
  WalkArea        Polygon2D: walkable floor, hidden at runtime
    <hole>        optional Polygon2D: an obstacle cut out of the floor (metadata show_if_flags / hide_if_flags)
  Entries         Node2D
    <entry>       Marker2D, metadata/facing: 1 down, 2 up, 3 left, 4 right
  Hotspots        Node2D
    <Hotspot>     Hotspot or Actor, with CollisionShape2D/CollisionPolygon2D children
  World           Node2D, y-sorted: actors, foreground props, the player
```

Optional: `Rain`, `FlagSprite`/`LoopStrip` overlays (alternate states cropped by the art generator), `Voice` nodes,
`IdleStrip`s.

Foreground props the player walks behind go in `World` as `Sprite2D` with `position.y = baseline` and
`offset.y = -baseline`, so y-sorting draws them over anyone standing above that line. A prop the player walks round
also gets a `WalkArea` hole under its footprint; holes follow the flags on every `Refresh` (see the Room 507
interlude bench, checked by `WalkTest.HoleTests`).

## Room exports

| Export | Default | Meaning |
|---|---|---|
| `FarScale` / `NearScale` | 0.86 / 1.0 | Character scale at `FarY` / `NearY` (linear, clamped) |
| `FarY` / `NearY` | 130 / 198 | Floor depth range |
| `RoomName` | "" | Title shown in saves |
| `PlayerCharacter` | `micah` | Player sheet (`daniel` in the attic prologue) |
| `ShowPlayer` | true | False for screens like `chicago_map` |
| `Floor` | `Wood` | Footstep sound: `Wood`, `Stone`, `Carpet` |

## Room hooks

| Override | Use |
|---|---|
| `void OnArriving(string entry)` | Still black, before the fade-in: stage the arrival's first frame (a held pose). Skipped with `OnEnter` |
| `Task OnEnter(string entry)` | Arrival cutscene. Guard one-shots with a flag (`seen_lobby`). Not replayed on load |
| `Task<bool> OnInteract(Verb, Hotspot, string? item)` | Main handler. `switch (target.Id, verb)`; return `true` if handled |
| `Task<bool> OnCombine(string item, string other)` | Room-only item combinations |
| `Task OnCombined(string result)` | Follow-up after a `Recipes` combination succeeds (the morgue pins the clipping) |
| `Task<bool> OnItemVerb(Verb, string item)` | Room-only verbs on satchel items |
| `Task OnCue(string cue)` | Stage business for Ink `CUE: name` lines |
| `void OnRefresh()` | After every `GameState.Changed` (visibility already refreshed) |
| `Verb? LeftClickVerb(Hotspot)` | Change the left-click default for a hotspot |
| `Vector2 ClampWalkTarget(Vector2)` | Block parts of the floor (a doorman, a curtain) |
| `Track? Music` | Room music; the same track continues across rooms |
| `(Sound, float)? Ambience` | Default: rain if a `Rain` node exists (0 dB outdoors when it covers >30% of the screen, else -9 dB), louder each act (`RainWeather`); none once `RainStopped` |
| `bool RainStopped` | True where someone is saved: hides every `Rain` node and silences the ambience, live on state changes. Exteriors and window rooms must draw `Rain` unless listed dry in `RainTests` |
| `bool PlayerVisibleOnLoad` | Hide the player for an entry cutscene |
| `string ResolvePlayerCharacter()` | Outfit/character logic |

Helpers: `Game`, `State`, `Player`, `Say`, `Think`, `Talk`, `Wait`, `FindActor`, `FindHotspot`,
`FindSpeaker`, `EntryPoint`, `ScaleAt`, `Shows(item, physical, note)` (physical item or notepad with the known note).
Async usage: [Scripting API](core-framework.md#scripting-api-use-inside-gamerun).

### Typical script

```csharp
public partial class Lobby : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_lobby")) return;
        State.SetFlag("seen_lobby");
        await Game.Run(async () => await Think("The Aurelian."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("concierge", Verb.Talk):
                await Talk("concierge");
                return true;
            case ("bellboy", Verb.UseItem) when item == "dollar":
                await Talk("bellboy_tip");
                return true;
            case ("service_door", Verb.Walk or Verb.Hand) when State.HasFlag("staff_elevator"):
                if (!await Game.Hud.Puzzle.Open(PuzzleKind.Lift)) return true;
                await Game.ChangeRoom("hotel_linen", "lift");
                return true;
        }
        return false;   // LookText, exits and generic lines
    }
}
```

Order `case`s from most to least specific: gated `when` cases before the ungated fallback for the same hotspot.

## Exits

A hotspot with `ExitTo = "<scene>"` and `ExitEntry = "<marker>"` changes room on Walk or Hand if the room script
does not handle it. Scripted moves use `Game.ChangeRoom("<scene>", "<marker>")` with **literal** strings, so tests
can check them. City travel goes through `chicago_map` (flag `on_map`). While the player is Eleanor (interludes),
generic exits are closed (`Interlude.BlockedExitLine`) and held items refused: her rooms script their own way out.

## Invariants (checked by tests)

| Check | Test |
|---|---|
| Every exit and literal `ChangeRoom("room","entry")` targets an existing scene and marker | `SceneGraphTests` (unit) |
| Entry markers and explicit `WalkTo` points stand on the `WalkArea` polygon (allowlist `OffFloorEntries`, currently empty) | `SceneGraphTests` |
| Every room is reachable from the attic | `SceneGraphTests` |
| From every entry, every hotspot and exit is reachable without crossing a wall, at the right scale; exits land exactly on their entry | `--walk-test` (`walk` suite) |
| Floor clicks, clamping, interruption, facing, clicks ignored while busy | `--walk-test` |

`WalkTest` skips `OnEnter` cutscenes and autosave, and sets `sal_passed` so the speakeasy curtain does not block it.

## Adding a room

1. Background: a painter in `tools/art/` writing `assets/art/rooms/<scene>.png` (480x270), registered as a step in
   `tools/gen_art.py`. See [Art pipeline](art-pipeline.md).
2. Scene: duplicate a similar `.tscn`, keep the node layout, set exports, draw `WalkArea`, add entry markers with
   `metadata/facing`, hotspots (with `Id`, `DisplayName`, `LookText`) and exits.
3. Script: `scripts/Rooms/<Name>.cs`, `public partial class <Name> : Room`; attach it to the root.
4. Link it: an exit hotspot elsewhere with `ExitTo`/`ExitEntry`, or a literal `ChangeRoom`, so it is reachable.
5. Story: dialogue in `dialogue/repentance.ink`, items in `src/Repentance.Rules/Items/`, a beat in
   `scripts/Debug/Playthrough/` (see [Story and dialogue](story-and-dialogue.md)). If a debug start there needs
   items or notes, update `MicahKit.DebugItems` / `Notes.DebugStartFlags`.
6. Check [save compatibility](saves-and-settings.md#changing-the-format) if saved room/entry identifiers change.
7. Run `dotnet build`, then `tools\run\test.ps1 -Suite unit, walk`; add `playthrough` for story and `art` for art.

Agents: `.claude/skills/add-room/SKILL.md`.

For a normal interactive check after editing a room, `tools/run/game.sh` / `tools\run\game.ps1` rebuilds/imports
and starts at the title screen. Use direct Godot [debug-room options](getting-started.md#command-line-options)
for targeted diagnostics; the normal-play launchers do not forward debug arguments.
