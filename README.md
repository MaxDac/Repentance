# Repentance

*Chicago, 1927. The neon says HOTEL. The rain says nothing at all.*

A point-and-click noir adventure in the spirit of *Monkey Island 2*: a 480×270 pixel-art
game with a right-click verb wheel. Today, Daniel is clearing out the attic of the old house he just
bought when he finds the journal of Micah Jones, a private eye. In 1927, Teddy Harrington III, heir to
Harrington Steel, hired Micah to find his missing wife, Eleanor.

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

- **Left click** on the floor to walk. Left click on an object does the obvious thing: talk to people,
  go through exits, look at everything else.
- **Right click** on an object opens the **verb wheel**: 👁 *Look*, ✋ *Hand* (take, use, open, push),
  👄 *Talk*, 🥾 *Kick*. Click an icon, or hold the right button and release it over one.
- **Satchel** (bottom right) opens the inventory. Left-click an item to hold it as the cursor, then click
  it on an object or person to use or give it (or on another item to combine them). Right-click
  anywhere to put it back. Right-click an item in the satchel to open its verb wheel.
- Click during speech to skip the line.

## The demo

0. **Prologue, the attic (today)**: Daniel calls his son Leo, who doesn't come. Lift the dust sheet, knock
   over the boxes, find the crowbar in the papers and use it on the steamer trunk (the key in the suitcase
   doesn't fit it). Inside is Micah's journal.
   Right-click it in the satchel and choose the hand to read it. This part doubles as the tutorial.
1. **Office**: Teddy briefs you and hands over Eleanor's photograph. The top desk drawer holds a revolver,
   a dollar and a set of lockpicks. Micah won't leave without all three.
2. **Aurelian Hotel lobby**: the concierge sees nothing. A dollar loosens the bellboy's memory and buys the
   staff elevator up to Eleanor's room.
3. **Room 507**: the room has been turned upside down. Pick the locked desk drawer for the safe combination,
   open the closet to find the safe, and take the brass box. Open it in the satchel with the hand: a
   perfumed, blank calling card and a matchbook from the Blue Lantern.
4. **Blue Lantern speakeasy**: Micah doesn't know the password and has to bribe Sal (mock him or refuse and
   you're thrown straight out back). Tony the bartender won't talk; when you're done he decides he doesn't
   like you, and nods to Sal.
5. **The alley behind the club**: one flickering street lamp. Micah on his knees after the beating; Tony tells
   him Eleanor is "hot stuff" and that he sent her to the nuns.
6. **The convent** (corridor → cell): Sister Agatha questions Micah, warns him off "that Jezebel", then lets
   him see Eleanor's cell. The nightstand drawer holds a comb and a little mirror with a strange symbol on
   the back. Micah won't leave without the mirror.
7. **Outside the convent**: Eleanor, in black, is waiting for him.
8. **Motel, that night**: Micah gets dressed, Eleanor lies under the sheet. A mistake; they won't meet again,
   and Micah drops the case.
9. **End of Act One**: back in the attic at night, lamp on. Daniel is called down to dinner.
10. **Act Two, the next day**: Daniel picks the journal up again (hand on it in the satchel).

From here the *temporary* storyline strings together every remaining location:

11. **Starlight club** (street → hall → lounge → stage): in the lounge, Teddy's father, old Theodore Harrington,
   is watching the curtain too. On stage, "Nora" is Eleanor. Teddy owes Moretti, and Teddy's
   bookkeeper is dead. She gives you the key to her old suite.
12. **Aurelian suite 4**: her diary is hidden in the vanity.
13. **Cathedral**: Father Caleb, Micah's estranged brother, reads the diary and points you to the library.
14. **Public library**: Rose, Micah's estranged wife and a librarian, tells you where to look. The ledger behind
   the shelves holds a motel receipt.
15. **Motel room 6**: a map is hidden in the bed.
16. **Outskirts**: dig where the map says to find the bookkeeper's tin box... and Sal is waiting. *To be continued.*

## Project layout

```
assets/art/          generated pixel art (rooms, sprites, items, ui)
assets/fonts/        Silkscreen pixel font (OFL)
dialogue/            repentance.ink - all conversations, one knot per character
scenes/Main.tscn     entry scene (Game.cs)
scenes/rooms/        one .tscn per room
scripts/Core/        the adventure framework
scripts/Rooms/       per-room puzzle scripts
scripts/UI/          Hud (hover label, satchel, inventory, choices, speech, fades, cursor) and VerbWheel
scripts/Debug/       AutoPlay smoke test
tools/               Python art generator
```

### Framework at a glance (`scripts/Core`)

| Type | Role |
|---|---|
| `Game` | Main controller. Handles input (left click, right-click wheel, held item), executes verbs and changes rooms. Exposes the script helpers `Say`, `WalkTo`, `Wait`, `Run` and `ChangeRoom` |
| `GameState` (autoload) | Story flags and inventory; emits `Changed` |
| `DialogueManager` (autoload) | Runs Ink knots; binds `has_item`, `has_flag`, `give_item`, `take_item` and `set_flag` |
| `Room` | Base class for rooms. Handles walk area, perspective scaling, entries and hotspot lookup. Its `PlayerCharacter` export (`micah` or `daniel`) picks the player sprite. Override `OnEnter`, `OnInteract`, `OnItemVerb`, `OnCombine` and `ClampWalkTarget` |
| `Hotspot` | `Area2D` with a collision shape. Has `Id`, `DisplayName`, `LookText`, `WalkTo`, `Face`, `ExitTo`/`ExitEntry`, flag-based visibility and `ClickPriority` |
| `Actor` | An NPC: a hotspot with a 3-frame (idle + two talk frames) sprite strip, a speech colour, depth scaling and `MoveTo` |
| `Player` | The player character (Micah, or Daniel in the prologue): 4-direction walk cycles, pathfinding along the walk polygon |
| `Verbs` | `Verb` enum (`Walk`, `Look`, `Hand`, `Talk`, `Kick`, `UseItem`) and the wheel's labels and icons |
| `Voice` | An off-screen speaker (Leo, tutorial hints) for `Say("id", ...)` and Ink lines |
| `WalkArea` | Polygon visibility-graph pathfinder |
| `FlagSprite` | A sprite shown or hidden by story flags (e.g. the open drawer) |
| `Items` | Inventory item catalogue (name, icon, description) |

### Adding a room

1. Draw a 480×270 background (or add a generator in `tools/art/`) into `assets/art/rooms/`.
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

All art is generated procedurally with Python and Pillow, so it can be tweaked and re-rendered. It is placeholder-quality but detailed.
The characters come from `tools/art/figure.py`, a small 3D-ish figure painter whose look is inspired by
early-90s VGA adventures such as *Indiana Jones and the Fate of Atlantis*: tall, naturally proportioned
bodies, shading lit from the top left, a darker outline on each material ("sel-out") and dithered fabric.
Each character is a spec dict in `tools/art/sprites.py`.

```powershell
py -3.14 -m pip install --upgrade pillow numpy
py -3.14 tools\gen_art.py            # everything
py -3.14 tools\gen_art.py lobby      # a single step: sprites, items, office, lobby, eleanor_room, speakeasy, alley, convent, convent_road, ui
```

You can replace any PNG with hand-drawn art (Aseprite, Pixelorama...) as long as it keeps the same
size: rooms are 480×200, player frames are 64×96 in a 10×3 sheet (rows: side, front, back; see `Player.cs` for the column layout), NPCs are 3-frame 56×96 strips (idle, two talk frames), and items are 32×24.

## Credits

See [CREDITS.md](CREDITS.md).
