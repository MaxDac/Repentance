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
| `--pause-test` | Runs focused Space pause/resume regression checks. Prints `PAUSE TEST OK` and exits with code 0 on success |

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
- **Space** pauses/resumes gameplay, even mid-sentence. The current dialogue, movement, and timers
  stay frozen until you resume; clicks do nothing while paused. Space is inactive on the title screen
  and inside the Esc menu.
- Puzzle close-ups have their own controls, **Reset**, and **Close / Esc**. They are untimed and allow
  unlimited retries. Unsubmitted settings reset when closed; collected clues remain available.
- Use the satchel's **< / >** page buttons when carrying more than twelve items. A held item can be
  combined with an item on another page.
- **Esc** opens the pause menu: *Resume*, *Save game*, *Load game*, *Quit to title*. The title screen offers
  *Continue* (most recent save), *New game* and *Load game*.

### Saving

The game autosaves every time you enter a room, and there are 3 manual slots. Saving is only possible
between actions, not during a cutscene or conversation. Saves are JSON files in `user://saves/`
(on Windows, `%APPDATA%\Godot\app_userdata\Repentance\saves`). Each save stores the story flags, the
inventory, the story act, the Ink state, the current room and the player's position. Loading a save
doesn't replay the room's entry cutscene. Bump `SaveData.CurrentVersion` when saved decisions, identifiers or room flow
change incompatibly: older saves then show up as *Incompatible* instead of loading into a broken state. The
autoplay test uses `user://autoplay_saves/`, so it never touches your own saves.
The ten-puzzle expansion preserves completed discoveries in compatible version-3 saves using separate
original-puzzle and Act 3 schema markers. New saves do not grandfather unfinished puzzles on reload.
Version-2 saves, including saves made on the puzzle branch before this merge, remain incompatible with
main's completed Act 3, which removed the temporary ending route.
An older Act 2 save that skipped room 507 gets a temporary Hotel map marker to recover the card clues.

The ring/cross story revision uses save version 4. Earlier saves are incompatible because they lack the original
ring decision and use the previous Act 2/3 entry flow.

## The demo

0. **Prologue, the attic (today)**: Daniel calls his son Leo, who doesn't come. Lift the dust sheet, knock
   over the boxes and find a locked tool tin in the papers. The suitcase's small key opens that tin,
   not the trunk; its crowbar opens the steamer trunk. Inside is Micah's journal.
   Right-click it in the satchel and choose the hand to read it. This part doubles as the tutorial.
1. **Office**: Teddy briefs you and hands over Eleanor's photograph. The top desk drawer holds a revolver,
   a dollar and a set of lockpicks. Micah won't leave without all three.
2. **Aurelian Hotel lobby**: the concierge sees nothing. A dollar loosens the bellboy's memory and buys the
   staff elevator up to Eleanor's room. Trace its routing diagram and set the three junctions
   lower, upper, upper to reach room 507.
   Micah collects the brass box there before departing for the Blue Lantern.
3. **Room 507**: the room has been turned upside down. Pick the locked desk drawer for the safe combination,
   open the closet and enter R 12 / L 31 / R 7 on the safe's close-up controls, then take the brass box.
   Open it in the satchel with the hand: a
   perfumed, blank calling card and a matchbook from the Blue Lantern.
4. **Blue Lantern speakeasy**: Micah doesn't know the password and has to bribe Sal (mock him or refuse and
   you're thrown straight out back). Tony the bartender won't talk; when you're done he decides he doesn't
   like you, and nods to Sal.
5. **The alley behind the club**: one flickering street lamp. Micah on his knees after the beating; Tony tells
   him Eleanor is "hot stuff" and that he sent her to the nuns.
6. **The convent** (corridor → cell): Sister Agatha questions Micah, warns him off "that Jezebel", then lets
   him see Eleanor's cell. The nightstand drawer holds a comb and a little mirror with a strange symbol on
   the    back, hidden under wax. Borrow the cloth from the bed, warm the mirror at the lamp, and combine
   mirror and cloth to reveal the symbol. Micah returns the cloth and won't leave before that discovery.
7. **Outside the convent**: Eleanor, in black, is waiting for him.
8. **Motel, that night**: Micah gets dressed, Eleanor lies under the sheet. A mistake; they won't meet again,
   and Micah drops the case.
9. **End of Act One**: back in the attic at night, lamp on. Daniel is called down to dinner.
10. **Act Two, the next day**: Daniel picks the journal up again (hand on it in the satchel).
11. **Office, then cathedral steps**: Micah drinks whiskey from a cup and chooses to take his wedding ring or leave
    it behind. The original choice is saved; a left-behind ring can be collected later. He leaves for the cathedral,
    unable to think of anything but Eleanor.
12. **Inside the cathedral**: Micah tells his brother Caleb he's too far off to be saved. Caleb calls it the
   Devil's work. "I'll think about that." Coming was a mistake, and Micah walks out.
13. **Map of Chicago**: "I have to find her again." Pick the library, the cathedral or the office.
14. **Library, after hours**: ask the night librarian about the knot (shown full screen). He wants to know where
   the mirror came from; Micah won't say, so neither will he. Consult the desk catalogue: match the
   Celtic triquetra and select Bell's *Rites of the Old Isles*, C-17. The restricted shelves are locked.
   Micah uses the revolver on the librarian to obtain that book. He hands
   over a book of Celtic rituals, and the library is off limits from then on.
15. **Office**: read the book's concealed-ink instructions, warm the hotel card on the radiator and combine
   it with the mirror. Order the reflected fragments lily, leaf, feather to obtain the Club address.
   The steps can be discovered in a different order; all three clues remain available.

From here the story follows Walkthrough.md:

16. **Club** (hall): the Master of Ceremonies knows exactly why Micah is asking: Eleanor is "already with us,
   safe, and where she belongs". A brute shows Micah out.
17. **The street**: Micah on the pavement, asking himself why he left his wife and son. Go find his wife, or push
   forward.
18. **Rose's house** (optional): ring the bell. Push for forgiveness up to five times, or leave; push at least
   three times and Rose calls him back: "Don't get into trouble again."
19. **Cathedral**: press Caleb about the club. He points Micah to the convent and begs him to give up.
    On repeat visits Caleb offers a cross if Micah originally left the ring; if he originally took it, offers begin
    only in Act Three. Refusing allows another offer on the next eligible visit; accepting gives the pendant once.
20. **Convent**: Sister Agatha knows nothing until Micah draws the revolver on her. Eleanor is a performer;
   try Harrington senior.
21. **Behind the Harrington Building, at night**: set the trash can alight with the matchbook so the watchman
   runs inside to phone the fire department. Take the packing wedge, stack the crates and use the wedge
   on the jammed ladder catch before climbing in.
22. **Harrington's office**: pick the locked right drawer for an invitation to the club; behind the closet's false
   back are a white mask and a cloak. Match the invitation's raven/lion/stag procession to the portrait's
   heraldic key; set the false-back lock to STAR / SUN / MOON.
23. **Club, masked**: through the hall and the lounge, full of masked men and women, to the stage, where Eleanor
   stands among three masked men. **End of Act Two**: back in the attic, dinner again.
24. **Act Three, the bedroom**: Daniel reads in bed while his wife sleeps.
25. **Club**: "Are you satisfied, now, mister Jones?" Draw the revolver or don't; either way Bruno knocks Micah out.
26. **Outside the cathedral**: give up (ending 1), or keep going:
27. **The office**: at his desk, Micah works out who knows where the Club keeps its girls: Tony, at the Blue Lantern.
    After standing he can collect the ring. Leaving offers Caleb or the Blue Lantern; Caleb visits return to the
    office and can repeat until the cross is accepted. Act Three visits also count toward the church-return requirement.
28. **The alley**: break the street lamp, kick the trash cans in the dark to lure Sal out, knock him down with
   the revolver, then knock on the back door. With Tony at gunpoint, shoot him in the leg, or (only if Micah went
   back to Caleb while hunting for Eleanor **and carries his wedding ring**) walk away (ending 1). Tony sends him to old Harrington's house.
29. **The Harrington mansion**: the key on the lintel would ring an alarm bell wired to the kitchen door. Look at
   the door to spot it, take the key and push the coal bin under the bell. In the close-up, plan hold hammer,
   tie hammer, release hand; cutting the wire would release the spring. Then open the door.
30. **Kitchen and study**: optionally take the right drawer's account register and the left drawer's auditor's
   index. At the study desk, combine them and align BANK/JUDGE/CAPTAIN (one clockwise turn, offset 6,3)
   to locate and take the signed payoff sheets. The register alone is not evidence. Entering the bedroom
   ends this opportunity; skipping remains possible and preserves the prison endings.
31. **The bedroom**: old Harrington with Eleanor. Shoot him, or (only if Micah went back to Caleb *and* pressed
   Rose at least three times **and carries both ring and cross**) lower the gun (ending 1). Then talk Eleanor into leaving ("I didn't come all this
   way...", or later "Every time I've seen you...").
32. **The escape**: in the kitchen, optionally turn on the gas and light the candle; the house blows up behind them.
33. **Endings**: 1 coffee with Rose; 2 out of town with Eleanor (convinced, and ledgers or explosion); 3 out of town
   alone (not convinced, ledgers or explosion); 4 prison, Eleanor visits (convinced, nothing to bargain with);
   5 prison, Caleb visits. Each ends Act Three; the next morning Daniel keeps the journal for Leo if Micah returned
   to Rose, saying "maybe Leo would like to read it some day". Otherwise, he puts it back in the trunk. *The End.*

## Project layout

```
assets/art/          generated pixel art (rooms, sprites, items, ui)
assets/fonts/        Silkscreen pixel font (OFL)
dialogue/            repentance.ink - all conversations, one knot per character
scenes/Main.tscn     entry scene (Game.cs)
scenes/rooms/        one .tscn per room
scripts/Core/        the adventure framework
scripts/Rooms/       per-room puzzle scripts
scripts/UI/           Hud (hover label, satchel, inventory, choices, speech, fades, cursor), VerbWheel and GameMenu (title/pause/save slots)
scripts/Debug/       AutoPlay smoke test
tools/               Python art generator
```

### Framework at a glance (`scripts/Core`)

| Type | Role |
|---|---|
| `Game` | Main controller. Handles input (left click, right-click wheel, held item), executes verbs and changes rooms. Exposes the script helpers `Say`, `WalkTo`, `Wait`, `Run` and `ChangeRoom` |
| `GameState` (autoload) | Story flags and inventory; emits `Changed`. `CaptureInto`/`Restore` copy it to and from a save |
| `SaveData` / `SaveSystem` | The save file model and its JSON serializer (Godot-free and unit tested), and the autosave plus slot files in `user://saves` |
| `DialogueManager` (autoload) | Runs Ink knots; binds `has_item`, `has_flag`, `give_item`, `take_item` and `set_flag` |
| `Room` | Base class for rooms. Handles walk area, perspective scaling, entries and hotspot lookup. Its `PlayerCharacter` export (`micah` or `daniel`) picks the player sprite. Override `OnEnter`, `OnInteract`, `OnItemVerb`, `OnCombine` and `ClampWalkTarget` |
| `Hotspot` | `Area2D` with a collision shape. Has `Id`, `DisplayName`, `LookText`, `WalkTo`, `Face`, `ExitTo`/`ExitEntry`, flag-based visibility and `ClickPriority` |
| `Actor` | An NPC: a hotspot with an 11-frame sprite strip (idle, two talk frames, an 8-frame walk cycle), a speech colour, depth scaling and `MoveTo` (which plays the walk cycle) |
| `Player` | The player character (Micah, or Daniel in the prologue): 4-direction walk cycles, pathfinding along the walk polygon |
| `Verbs` | `Verb` enum (`Walk`, `Look`, `Hand`, `Talk`, `Kick`, `UseItem`) and the wheel's labels and icons |
| `Voice` | An off-screen speaker (Leo, tutorial hints) for `Say("id", ...)` and Ink lines |
| `WalkArea` | Polygon visibility-graph pathfinder |
| `FlagSprite` | A sprite shown or hidden by story flags (e.g. the open drawer) |
| `Items` | Inventory item catalogue (name, icon, description) |
| `PuzzleRules` / `PuzzleMigration` | Godot-free puzzle validators and one-time legacy-save normalization |
| `PuzzlePanel` | Modal route, dial, catalogue, cipher, crest, alarm-plan and account-index controls |

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
Regenerate only the new puzzle props, icons and clue plates with `py -3.14 tools\gen_art.py puzzles`.
There are no imported 3D models: figure skeletons and perspective furniture are painted into PNGs by
`tools/art/figure.py` and `tools/art/furniture.py`.
The characters come from `tools/art/figure.py`, a small 3D-ish figure painter whose look is inspired by
early-90s VGA adventures such as *Indiana Jones and the Fate of Atlantis*: tall, naturally proportioned
bodies, shading lit from the top left, a darker outline on each material ("sel-out") and dithered fabric.
Each character is a spec dict in `tools/art/sprites.py`.

```powershell
py -3.14 -m pip install --upgrade pillow numpy
py -3.14 tools\gen_art.py            # everything
py -3.14 tools\gen_art.py lobby      # a single step: sprites, items, office, lobby, eleanor_room, speakeasy, alley, convent, convent_road, chicago_map, ui
py -3.14 tools\gen_art.py club harrington  # club rooms and Harrington's building/office, including puzzle overlays
py -3.14 -m unittest discover -s tests\art -v  # image contracts and location rendering regressions
```

You can replace any PNG with hand-drawn art (Aseprite, Pixelorama...) as long as it keeps the same
size: backgrounds are 480×270, player frames are 64×96 in a 10×3 sheet (rows: side, front, back; see `Player.cs` for the column layout), NPCs are 11-frame 56×96 strips (idle, two talk frames, walk 1-8 in side view), and items are 32×24.
Puzzle overlays and foreground layers keep their own crop sizes and scene positions. After regeneration,
check the printed overlay coordinates against the corresponding scene; moving a crop without its node
misaligns the object. Club rooms use their own 128-colour palettes so the stage's darkness does not
flatten the lounge's velvet and brass.

## Credits

See [CREDITS.md](CREDITS.md).
