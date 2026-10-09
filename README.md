# Repentance

*Chicago, 1927. The neon says HOTEL. The rain says nothing at all.*

A point-and-click noir adventure in the spirit of *Monkey Island 2*: a 480×270 pixel-art
game with a nine-verb SCUMM interface. You play Micah Jones, a private eye. Teddy Harrington III,
heir to Harrington Steel, hires him to find his missing wife, Eleanor.

Built with **Godot 4.7 (.NET)** and **C#**, with dialogue written in **Ink** (via GodotInk).

## Running it

Requirements: Godot 4.7.x **.NET/Mono** edition and the .NET 10 SDK.

```powershell
dotnet build
# open the project in the Godot editor (imports assets + compiles the Ink story), then press F5
godot --path . --editor
```

Command-line options (after `--`):

| Option | Effect |
|---|---|
| `--skip-title` | Skip the title screen |
| `--room=lobby --entry=office` | Start in a given room/entry (handy while building a room) |
| `--autoplay` | Plays the whole demo by itself and saves screenshots to `screenshots/`. Prints `AUTOPLAY OK` and exits with code 0 on success |

```powershell
godot --path . -- --autoplay
```

### Controls

- **Left click**: perform the sentence shown above the verbs. The default verb is *Walk to*.
- **Right click** on an object: its default verb (*Talk to* for people, *Walk to* for exits, *Look at* for everything else).
- **Inventory**: right-click an item to look at it. To use an item, click *Use* or *Give*, then the item, then the target.
- Click during speech to skip the line.

## The demo

1. **Office**: Teddy briefs you and hands over Eleanor's photograph. There's a dollar in the top desk drawer.
2. **Aurelian Hotel lobby**: the concierge sees nothing. A dollar loosens the bellboy's memory.
   The brass urn hides a matchbook from the Blue Lantern with a password inside.
3. **Blue Lantern speakeasy**: give Sal the password, then show the bartender the photo... *To be continued.*

## Project layout

```
assets/art/          generated pixel art (rooms, sprites, items, ui)
assets/fonts/        Silkscreen pixel font (OFL)
dialogue/            repentance.ink - all conversations, one knot per character
scenes/Main.tscn     entry scene (Game.cs)
scenes/rooms/        one .tscn per room
scripts/Core/        the adventure framework
scripts/Rooms/       per-room puzzle scripts
scripts/UI/Hud.cs    verbs, inventory, dialogue choices, speech text, fades
scripts/Debug/       AutoPlay smoke test
tools/               Python art generator
```

### Framework at a glance (`scripts/Core`)

| Type | Role |
|---|---|
| `Game` | Main controller. Handles input, builds the sentence line, executes verbs and changes rooms. Exposes the script helpers `Say`, `WalkTo`, `Wait`, `Run` and `ChangeRoom` |
| `GameState` (autoload) | Story flags and inventory; emits `Changed` |
| `DialogueManager` (autoload) | Runs Ink knots; binds `has_item`, `has_flag`, `give_item`, `take_item` and `set_flag` |
| `Room` | Base class for rooms. Handles walk area, perspective scaling, entries and hotspot lookup. Override `OnEnter`, `OnInteract`, `OnCombine` and `ClampWalkTarget` |
| `Hotspot` | `Area2D` with a collision shape. Has `Id`, `DisplayName`, `LookText`, `WalkTo`, `Face`, `ExitTo`/`ExitEntry`, flag-based visibility and `ClickPriority` |
| `Actor` | An NPC: a hotspot with a 2-frame (idle/talk) sprite sheet, a speech colour and `MoveTo` |
| `Player` | Micah: 4-direction walk cycles, pathfinding along the walk polygon |
| `WalkArea` | Polygon visibility-graph pathfinder |
| `FlagSprite` | A sprite shown or hidden by story flags (e.g. the open drawer) |
| `Items` | Inventory item catalogue (name, icon, description) |

### Adding a room

1. Draw a 480×200 background (or add a generator in `tools/art/`) into `assets/art/rooms/`.
2. Duplicate a scene in `scenes/rooms/`. The node layout is:
   - `Background` (Sprite2D)
   - `WalkArea` (Polygon2D, hidden at runtime)
   - `Entries` (Marker2Ds, with `metadata/facing`: 1=down, 2=up, 3=left, 4=right)
   - `Hotspots`
   - `World` (y-sorted: actors and foreground props)
3. Add a script deriving from `Room` in `scripts/Rooms/` and handle verbs in `OnInteract` with `switch (target.Id, verb)`.
4. Link it with a hotspot whose `ExitTo` is the scene file name and whose `ExitEntry` is the marker name.

Foreground props that characters can walk behind go inside `World` as Sprite2Ds with
`position.y = baseline` and `offset.y = -baseline`, so y-sorting puts them in front of anyone standing above that line.

### Writing dialogue

Edit `dialogue/repentance.ink`. Lines use the format `SPEAKER: text`, where the speaker is an actor `Id` in upper case and `MICAH` is the player.
Micah speaks the choice text aloud, unless it starts with `(`.
Start a conversation from a room script with `await Talk("knot")`.
Ink compiles on import in the editor; `repentance.ink.import` must keep `is_main_file=true`.

### Regenerating the art

All art is generated procedurally with Python and Pillow, so it can be tweaked and re-rendered. It is placeholder-quality but detailed:

```powershell
py -3.14 -m pip install --upgrade pillow
py -3.14 tools\gen_art.py            # everything
py -3.14 tools\gen_art.py lobby      # a single step: sprites, items, office, lobby, speakeasy, ui
```

You can replace any PNG with hand-drawn art (Aseprite, Pixelorama...) as long as it keeps the same
size: rooms are 480×200, Micah's frames are 40×80 in an 8×3 sheet, NPCs are 2-frame strips, and items are 32×24.

## Credits

See [CREDITS.md](CREDITS.md).
