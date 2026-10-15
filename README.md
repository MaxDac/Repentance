# Repentance

*Chicago, 1927. The neon says HOTEL. The rain says nothing at all.*

A point-and-click noir adventure in the spirit of *Monkey Island 2*: a 480×270 pixel-art
game with a right-click verb wheel. Today, Daniel is clearing out the attic of the old house he just
bought when he finds the journal of Micah Jones, a private eye. In 1927, Teddy Harrington III, heir to
Harrington Steel, hired Micah to find his missing wife, Eleanor.

Built with **Godot 4.7 (.NET)** and **C#**, with dialogue written in **Ink** (via GodotInk).

## Running it

Requirements: Godot 4.7.x **.NET/Mono** edition and the .NET 10 SDK.

### Tests and film mode

The quickest way to run everything, or to watch the whole game play itself at 1x, 2x or 4x, is the scripts in
`tools/run/` (they reset every generated file and rebuild first). See
**[Testing and film mode](docs/testing-and-film-mode.md)**.

```powershell
tools\run\test.ps1                 # every test suite (bash: tools/run/test.sh)
tools\run\film.ps1 -Speed 2        # watch the story (bash: tools/run/film.sh 2)
```

### Common commands

```powershell
# 1. after C# changes, and before the first import: the Ink importer is a C# plugin
dotnet build
# 2. after a fresh clone, or after new/changed art, fonts or Ink: import assets (no editor needed)
godot --path . --headless --import
# play
godot --path .
# full automated playthrough (Windows: use godot_console.exe and wait for AUTOPLAY OK)
godot_console --path . -- --autoplay
# capture what the screen shows, without a visible window: writes frames to frames\f*.png
godot_console --path . --write-movie frames\f.png --fixed-fps 30 --quit-after 120
# unit tests and art tests
dotnet test tests/Repentance.Tests/Repentance.Tests.csproj
py -3.14 -m unittest discover -s tests\art -v
```

You can also open the project in the editor (`godot --path . --editor`), which imports assets and compiles
the Ink story, then press F5.

`.godot/` (the import cache) is not committed. Running `godot --path .` on a fresh clone before importing
shows a grey title screen with a fallback font, because no texture or font can load. The game logs
`Assets are not imported` when this happens.

Command-line options (after `--`):

| Option | Effect |
|---|---|
| `--skip-title` | Skip the title screen |
| `--room=lobby --entry=office` | Start in a given room/entry (handy while building a room). Micah's notepad is pre-filled with the notes he would have taken on the way there (`Notes.DebugStartFlags`), and the satchel holds that act's kit: the office drawer and Teddy's photo past the office in Act 1, the Act 2/3 reset kit later on (`MicahKit.DebugItems`); Act 2/3 rooms also set the story act |
| `--flag=masked` | Set story flags (comma-separated) before the start room loads, e.g. `--room=club_hall --flag=masked` |
| `--autoplay` | Plays the whole demo by itself with targeted regression checks, and saves screenshots to `screenshots/`. Prints `AUTOPLAY OK` and exits with code 0 on success |
| `--playthrough` | Plays the canonical story (`scripts/Debug/Playthrough.cs`) and every ending route from a real save, with a save/load round trip after every beat and sound coverage. Prints `PLAYTHROUGH OK`. `--ending=N` (`1`-`5`, `1-oldman`, `1-steps` or `all`, the default) limits it to one route |
| `--film[=1\|2\|4]` | Film mode: the same story to watch at 1x, 2x or 4x speed, from the title to "The End"; input is ignored except Space, F11 and Esc. `--ending=N` picks the route (default 2). Prints `FILM OK` |
| `--settings-test` | Checks content, display and effects-volume settings, persistence, menus and both Eleanor variants without playing through the story. Prints `SETTINGS TEST OK` |
| `--pause-test` | Runs focused Space pause/resume regression checks. Prints `PAUSE TEST OK` and exits with code 0 on success |
| `--walk-test` | Movement checks in every room: entry markers stand on the floor, every hotspot and exit is reachable from every entry without crossing a wall, the player really walks there at the right scale, and every exit leads to an existing entry (room entry cutscenes are skipped). Then real mouse input: floor clicks, clicks off the floor, interrupting a walk, clicks ignored while busy, facing in all four directions and exits taken by clicking. Prints `WALK TEST OK` and exits with code 0 on success |
| `--clock=fast` | Default for the automated checks above (not film mode). Runs at 60× game time with vsync off, so dialogue and scripted waits do not take wall-clock story time. Every choice, flag check, pose frame and screenshot still runs. `--pause-test` still forces 1× while it asserts that pause freezes time, and `--walk-test` does the same for its mouse checks |
| `--clock=normal` | Previous automated clock: 8× game time, display timing left alone. Use this when screenshots should be closer to the paced game |

```powershell
godot --path . -- --autoplay
godot --path . -- --autoplay --clock=normal
godot --path . -- --pause-test --clock=fast
```

On Windows, use the Godot Mono **`_console.exe`** executable for automated runs when capturing output and
exit status. The GUI executable (including some `godot` aliases) can return before the game finishes.
Wait for `AUTOPLAY OK` from the console process rather than treating a successful launcher exit as a pass.

### Controls

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

### Content settings

**Settings > Nudity** is **Off** by default. Off uses Eleanor's dressed club sprite; On uses the
implied-nude variant, with hair and hand coverage. The choice updates the club scene immediately
and applies in both Act Two and Act Three. Preferences are stored in `user://settings.cfg`,
independently of saves, so loading an older save or starting a new game cannot override the choice.
Automated checks and film mode use a separate `user://autoplay_settings.cfg` and never modify player preferences.

### Display settings

**Settings > Full screen** is **Off** (windowed, 1440x810) by default. **F11** or **Alt+Enter** toggles it
anywhere, including on the title screen and while paused. Full screen is borderless and keeps whole-pixel
scaling, so the 480x270 picture is letterboxed when the monitor isn't an exact multiple. The choice is stored
in `user://settings.cfg` alongside the content settings. Automated checks never change the real window.

### Sound

All sound effects are synthesized at startup (no audio files) and play on an **Effects** bus:

- **Footsteps** for Micah, Daniel and walking NPCs, voiced by each room's `Floor` export (`Wood`, `Stone` or `Carpet`).
- **Story cues**: narration lines starting with `*` play a matching sound: `*BANG*` is a gunshot, and
  `*Knock knock*... *knock*` keeps its rhythm. There are also cues for clangs, crashes, door slams, the doorbell and the cellar fire's whoosh.
- **Ambience**: rain loops in rooms with a `Rain` node. It sounds muffled when the rain is only seen through a window.

**Settings > Effects volume** defaults to **80%**. Left click raises it and right click lowers it, in steps of 10%
(it wraps at the ends), and each change plays a preview knock. 0% mutes the effects. The value is stored in
`user://settings.cfg` under `[audio] effects_volume`.

### Music

Music is synthesized too (`MusicSynth`): original pieces written as scores and played by synthesized instruments
(bowed strings, pipe organ, piano, clarinet, plucked bass, brushed drums) in a reverberant room. Each track is about a
minute long, rendered once at startup on a background thread as exactly one period of a seamless loop, and
plays on a **Music** bus. It keeps playing while the game is paused. A room picks its track with `Room.Music`. Moving
between rooms that share a track does not restart it.

- **Club** (vestibule, hall, lounge, stage): `ClubStrings`, a dark, 60-second string bolero in 3/4 on tritones and the
  diminished scale. One bowed double-bass ostinato runs under a repeating cello theme. A second cello, the viola and,
  at the very end, two strident violins build on it before it all falls back to the bass.
- **Church** (interior): `ChurchOrgan`, the organist trying the pipes (single notes, a scale run, a full-organ chord),
  then a short mass chorale on the flutes and the full chorus, in a long stone-nave reverb.
- **Convent** (corridor, Eleanor's cell): `ConventPiano`, a hymn-like piano prelude in E-flat over pedalled arpeggios.
- **Office** (Micah's): `OfficeJazz`, a soft 1920s Chicago two-beat chorus for clarinet, piano, upright bass and
  brushes, filtered like an old 78 with a little surface crackle.

**Settings > Music volume** defaults to **70%** and works like Effects volume (left click louder, right click quieter,
0% mutes). The value is stored under `[audio] music_volume`.

### Saving

The game autosaves every time you enter a room, and there are 3 manual slots. Saving is only possible
between actions, not during a cutscene or conversation. Saves are JSON files in `user://saves/`
(on Windows, `%APPDATA%\Godot\app_userdata\Repentance\saves`). Each save stores the story flags, the
inventory, the story act, the Ink state, the current room and the player's position. Loading a save
doesn't replay the room's entry cutscene. Bump `SaveData.CurrentVersion` when saved decisions, identifiers or room flow
change incompatibly: older saves then show up as *Incompatible* instead of loading into a broken state. The
automated checks and film mode use `user://autoplay_saves/<suite>/`, so they never touch your own saves.
The current save format is version 8; earlier saves are incompatible because the laundry bluing now comes
from Eleanor's brass box instead of the florist's shelf, and the prototype State Street hub is gone. Version 7
added the Act One convent's playable exterior arrival and the return to the corridor for Sister Agatha's farewell.
The preceding five collect-and-combine locations reroute the staff lift, the Blue Lantern entrance,
the Harrington lead, the masked Club entrance and the
mansion entrance. The puzzle expansion's separate original-puzzle
and Act 3 schema markers preserve completed discoveries in compatible saves. New saves do not grandfather
unfinished puzzles on reload.

The cash revision changes save compatibility, not the ending requirements or ring/cross decisions.

### Releases

Linux and Windows builds are published by the manual **Release** workflow (`.github/workflows/release.yml`). It runs
the unit tests, exports both presets from `export_presets.cfg` with Godot 4.7.2 .NET, and attaches
`Repentance-vX.Y.Z-<linux|windows>-x86_64.zip` to a new GitHub Release.

```powershell
# blank version = bump the patch of the latest v* tag (first release: v0.1.0); prerelease defaults to true
gh workflow run release.yml -f version=0.2.0 -f prerelease=false
```

Exporting needs `Repentance.sln`: without it Godot exits 0 but silently leaves out the C# assemblies. AI agents can
use the `release` skill in `.github/skills/release/SKILL.md`.

## The demo

0. **Prologue, the attic (today)**: Daniel calls his son Leo, who doesn't come. Lift the dust sheet, knock
   over the boxes, then search them again: the MISC box holds a locked tool tin. The suitcase's small key opens that tin,
   not the trunk; its crowbar opens the steamer trunk. Inside is Micah's journal.
   Right-click it in the satchel and choose the hand to read it. This part doubles as the tutorial.
1. **Office**: Teddy briefs you and hands over Eleanor's photograph. The top desk drawer holds a revolver,
   $22 in cash and a set of lockpicks. Micah won't leave without all three.
2. **Aurelian Hotel lobby**: the concierge sees nothing. A dollar loosens the bellboy's memory; another buys the
   staff elevator up to Eleanor's floor. Steer the cage through the maze of service shafts from the loading bay
   to the fifth-floor linen room next to 507 (rooms count up west to east), then dispatch it.
   Micah collects the brass box in room 507 before departing for the Blue Lantern.
3. **Linen room**: the corridor door to 507 is night-bolted from the far side and has no keyhole. Take a wire
   hanger from the rack and the pliers from the housekeeping cart, combine them into a wire hook (the pliers
   go back on the cart) and use the hook on the door to lift the bolt through the transom.
   **Room 507**: the room has been turned upside down. Pick the locked desk drawer for the safe combination,
   open the closet and decode the paper's references (apostles, December, the day of rest: 12, 31, 7). It gives
   no directions; each right stop drops a tumbler, and the dial opens at right 12 / left 31 / right 7.
   Then take the brass box.
   Open it in the satchel with the hand: a
   calling card carrying her perfume, a matchbook from the Blue Lantern and a vial of laundry bluing.
4. **Rizzo's Flowers, State Street**: the Blue Lantern hides behind a florist's cold room. The chalkboard asks
   for blue carnations only. Take a white carnation from the bucket, combine it with Eleanor's
   bluing and show the blue carnation at the cold-room grille to be let in.
   **Blue Lantern speakeasy**: walking past Sal or talking to him starts the door talk. Micah doesn't know the password and can bribe Sal with $10,
   leaving $10 after all the bribes (mock him or refuse and
   you're thrown straight out back). Tony the bartender won't talk; when you're done he decides he doesn't
   like you, and nods to Sal.
5. **The alley behind the club**: one flickering street lamp. Micah on his knees after the beating; Tony tells
   him Eleanor is "hot stuff" and that he sent her to the nuns. Micah stands, then the player clicks the street exit.
6. **The convent** (exterior → corridor → cell → corridor): Micah remarks on the architecture outside;
   click the convent door to enter. Sister Agatha questions Micah, warns him off "that Jezebel", then lets
   him see Eleanor's cell. The nightstand drawer holds a comb and a little mirror with a strange symbol on
   the    back, hidden under wax. Borrow the cloth from the bed, warm the mirror at the lamp, and combine
   mirror and cloth to reveal the symbol. Micah returns the cloth and won't leave before that discovery.
   The cell door returns to the corridor. Talk to the sister for her farewell, or click the front door and
   she calls Micah back for the same exchange before letting him leave.
7. **Outside the convent**: Eleanor, in black, opens with a question about his late visit. After that opening,
   a framed close-up shows Micah on the left and Eleanor on the right, each speaking beneath their own portrait.
   It disappears before the compensation choice; the remaining conversation takes place on the road.
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
14. **Library, by day**: ask the librarian about the knot (shown full screen). He wants to know where
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
   three times and Rose calls him back: "Wait!", then a framed close-up of her at the door and "Don't get into trouble again."
19. **Cathedral**: press Caleb about the club. He points Micah to the convent and begs him to give up.
    On repeat visits Caleb offers a cross if Micah originally left the ring; if he originally took it, offers begin
    only in Act Three. Refusing allows another offer on the next eligible visit; accepting gives the pendant once.
20. **Convent**: Sister Agatha knows nothing until Micah draws the revolver on her. Eleanor is a performer;
   try Harrington senior. Micah decides to look him up at the Tribune.
    **Tribune newspaper morgue** (new map marker): take the torn top of a clipping from the H drawer, the
    bottom from the copy spike and the paste pot from the layout desk; with the paste held, combine the halves
    and pin the mended clipping on the Loop wall map. The Harrington Building replaces the Tribune on the map.
21. **Behind the Harrington Building, at night**: set the trash can alight with the matchbook so the watchman
   runs inside to phone the fire department. Take the packing wedge, stack the crates and use the wedge
   on the jammed ladder catch before climbing in.
22. **Harrington's office**: pick the locked right drawer for an invitation to the club; behind the closet's false
   back are a white Bauta mask and a cloak. Look at the portrait for a close-up of the heraldry at its foot
   (raven and star, lion and sun, stag and moon), then follow the invitation's raven/lion/stag procession; set the
   false-back lock to STAR / SUN / MOON. The lock's clue box only says "Three dials. Three symbols."
23. **Club vestibule, masked**: the street door is closed to Micah tonight; the map leads to the front. The plaque
   wants the summons sealed by the first of the procession. Soften the cloakroom's sealing wax with the
   matchbook (kept), press it on the invitation, then take the raven signet from the first cloak and seal it.
   Post the sealed invitation in the door slot.
   **Club, masked**: through the hall and the lounge, full of masked men and women (white Bauta masks and carved
   bear, raven and hare faces), to the stage, where Eleanor stands among three masked men: stag, boar and wolf. A framed close-up
   of Eleanor's face, masked men behind her, pops up over the stage until the fade.
   **End of Act Two**: back in the attic, dinner again.
24. **Act Three, the bedroom**: Daniel reads in bed while his wife sleeps.
25. **Club**: the close-up of Eleanor again; "Are you satisfied, now, mister Jones?" It closes before the choice: draw the revolver or don't; either way Bruno knocks Micah out.
26. **Outside the cathedral**: a framed close-up of Micah, flat on his back under his hat, stays up while he admits it's Eleanor
    he wants, not Rose; it closes as he gets up. Give up (ending 1), or keep going:
27. **The office**: lamp off, whiskey on the desk, Micah stares out of the window and works out who knows where the Club keeps its girls: Tony, at the Blue Lantern.
    After standing he can collect the ring. Leaving offers Caleb or the Blue Lantern; Caleb visits return to the
    office and can repeat until the cross is accepted. Act Three visits also count toward the church-return requirement.
28. **The alley**: break the street lamp, kick the trash cans in the dark to lure Sal out, knock him down with
   the revolver, then knock on the back door. With Tony at gunpoint, shoot him in the shoulder, or (only if Micah went
   back to Caleb while hunting for Eleanor **and carries his wedding ring**) walk away (ending 1). Tony sends him to old Harrington's house.
29. **The Harrington mansion**: the key on the lintel would ring an alarm bell wired to the kitchen door. Look at
   the door to spot it, take the key and push the coal bin under the bell. In the close-up, plan hold hammer,
   tie hammer, release hand; cutting the wire would release the spring. Then open the door.
30. **Kitchen, cellar and study**: the baize door to the house is bolted from the other side. Go down the cellar
   door: in the dark, take the storm lantern from its hook and the kerosene can from the crates, fill the
   lantern, light it with the matchbook (kept), use the lit lantern on the dark stair, then climb the
   bootleggers' stair to the study's bar panel.
   Walking back through the baize door unbolts it. Optionally take the right drawer's account register and the left drawer's auditor's
   index. At the study desk, combine them and align BANK/JUDGE/CAPTAIN (one clockwise turn, offset 6,3)
   to locate and take the signed payoff sheets. The register alone is not evidence. Entering the bedroom
   ends this opportunity; skipping remains possible and preserves the prison endings.
31. **The bedroom**: old Harrington with Eleanor. Shoot him, or (only if Micah went back to Caleb *and* pressed
   Rose at least three times **and carries both ring and cross**) lower the gun (ending 1). Then talk Eleanor into leaving ("I didn't come all this
   way...", or later "Every time I've seen you...").
32. **The escape**: optionally go back down to the wine cellar (Eleanor, if she came, waits in the kitchen), open the
   whiskey barrel, take the lit lantern off its nail and use it on the whiskey; the house burns behind them.
33. **Endings**: 1 coffee with Rose; 2 out of town with Eleanor (convinced, and signed evidence or fire); 3 out of town
   alone (not convinced, signed evidence or fire); 4 prison, Eleanor visits (convinced, neither signed evidence nor fire);
   5 prison, Caleb visits. Each ends Act Three; the next morning Daniel keeps the journal for Leo if Micah returned
   to Rose, saying "Maybe Leo would like to read it some day." Otherwise, he puts it back in the trunk. *The End.*

### Story notes

The core plot and five endings are unchanged; the fifteen puzzles include five collect-and-combine locations. Sal receives a cash bribe Micah can afford.
The Club blames Micah for Eleanor's capture; at his Act Three desk he wonders whether somebody followed him
or he let something slip, without establishing either as fact. While still supine outside the cathedral,
he admits that his pursuit is driven by lust for Eleanor, in conflict with returning to Rose and Tommy.
Caleb's leads refer to the established convent. Rose's doorstep reply remains "Forgiving is easy, Micah.
Forgetting is the part you keep asking for."; her callback is concern, not forgiveness earned by repeatedly asking.
Micah offers coffee with "Nothing you owe me."; the journal places renewed vows a year later.
His office reminder preserves the last opportunity to recover the wedding ring and visit Caleb.

If Eleanor refuses to follow and Micah burns the mansion, her fate remains unknown during escape.
The alone outskirts scene then begins **the next morning**: a newspaper lists Eleanor among the dead,
and Micah admits "I told myself I was saving her. I left her there and lit the fuse."
The fuse is figurative; the fire is the cellar's whiskey and the lantern. "They know who died. They don't know what I did."
replaces the previous claim that nobody will know what happened. Documents-only escape has no death report;
when Eleanor accompanies him, the scene remains that night and she survives. The existing ending outcomes remain unchanged.

Micah carries **$22** at the start of the case, enough for two $1 bellboy payments and the $10 Sal bribe, framed as a day's fee plus $2
from a previous job. The story already quotes his fee as $20 a day plus expenses. This is a fictional cash
holding, not a documented average PI income. Historical purchasing-power context comes from the
[NBER/BLS manufacturing weekly-earnings series](https://fred.stlouisfed.org/series/M08261USM052NNBR):
October 1927 weekly earnings were $24.37. The $22 reserve is about 90% of that benchmark, making the $10 door
bribe a substantial payment (about 41% of the weekly benchmark),
not an ordinary tip. Bribes deduct only their respective amounts; inventory inspection shows the remaining cash.

Exact Scripture excerpts use **Douay-Rheims (Challoner)**, appropriate to the Catholic characters:

| Dialogue | Reference |
|---|---|
| Sister Agatha's quiz | [Micheas 6:8](https://drbo.org/chapter/38006.htm) |

Caleb's counsel retains its original wording rather than added exact quotations. His prodigal-son account paraphrases
[Luke 15:17-20](https://drbo.org/chapter/49015.htm); it is not marked as a direct quotation. Ring and cross remain
reminders, not a bargain with God. Antagonists' threats and the tragic endings are not theological verdicts.

**Scope and length:** Repentance is a compact, single-case adventure: six puzzles in each of the first two acts,
then an alley encounter, an alarm puzzle, the wine-cellar lantern and optional evidence in Act Three. Its mostly linear investigation is
closer in scope to [The Blackwell Legacy](https://store.steampowered.com/app/80330/) than
[Kathy Rain (2016)](https://store.steampowered.com/app/370910/), whose published scope includes 40+ environments
and 4,000+ dialogue lines. [Technobabylon](https://store.steampowered.com/app/307580/) and
[Unavowed](https://store.steampowered.com/app/336140/) provide broader multi-protagonist/companion-based comparisons.
Those are scope comparisons, not verified completion-time claims. Reading/skipping dialogue, solving puzzles
without known answers, optional visits and replaying endings substantially change duration. Autoplay is accelerated
and includes seeded regressions; its wall-clock duration must not be advertised as adventure length.

## Project layout

```
assets/art/          generated pixel art (rooms, sprites, items, ui)
assets/fonts/        Silkscreen pixel font (OFL)
dialogue/            repentance.ink - all conversations, one knot per character
scenes/Main.tscn     entry scene (Game.cs)
scenes/rooms/        one .tscn per room
scripts/Core/        the adventure framework
scripts/Core/Game/   Game's partial files, one per concern (startup, input, items, commands, scripting, rooms, saves, pause)
scripts/Core/Items/  the item catalogue, one file per act
scripts/Story/       story logic that holds in any room (inventory verbs, item combinations, shared puzzles)
scripts/Rooms/       per-room puzzle scripts
scripts/UI/           Hud (hover label, satchel, inventory, choices, speech, fades, framed close-ups, cursor), CloseUp (the close-up catalog), VerbWheel and GameMenu (title/pause/save slots)
scripts/UI/Hud/      Hud's partial files: inventory, dialogue, screens and images
scripts/Debug/       Automated runs: Harness (shared base), Playthrough (story + film mode), AutoPlay (partials in
                     scripts/Debug/AutoPlay/, one per act plus the focused checks), WalkTest
tools/               Python art generator
```

Large classes are split into `partial` files so that changes to different features land in different files
and rarely conflict. The main file (for example `scripts/Core/Game.cs`) keeps the fields and the Godot
callbacks; add new code to the partial file for its concern, or start a new one.

### Framework at a glance (`scripts/Core`)

| Type | Role |
|---|---|
| `Game` | Main controller. Handles input (left click, right-click wheel, held item), executes verbs and changes rooms. Exposes the script helpers `Say`, `Think` (Micah's journal narration), `WalkTo`, `Wait`, `Run` and `ChangeRoom` |
| `GameState` (autoload) | Story flags and inventory; emits `Changed`. `CaptureInto`/`Restore` copy it to and from a save |
| `SaveData` / `SaveSystem` | The save file model and its JSON serializer (Godot-free and unit tested), and the autosave plus slot files in `user://saves` |
| `DialogueManager` (autoload) | Runs Ink knots; binds `has_item`, `has_flag`, `give_item`, `take_item` and `set_flag` |
| `Room` | Base class for rooms. Handles walk area, perspective scaling, entries and hotspot lookup. Its `PlayerCharacter` export (`micah` or `daniel`) picks the player sprite. Override `OnEnter`, `OnInteract`, `OnItemVerb`, `OnCombine`, `ClampWalkTarget` and `LeftClickVerb` |
| `Hotspot` | `Area2D` with a collision shape. Has `Id`, `DisplayName`, `LookText`, `WalkTo`, `Face`, `ExitTo`/`ExitEntry`, flag-based visibility and `ClickPriority` |
| `Actor` | An NPC: a hotspot with an 11-frame sprite strip (idle, two talk frames, an 8-frame walk cycle), a speech colour, depth scaling and `MoveTo` (which plays the walk cycle) |
| `Player` | The player character (Micah, or Daniel in the prologue): 4-direction walk cycles, pathfinding along the walk polygon |
| `Verbs` | `Verb` enum (`Walk`, `Look`, `Hand`, `Talk`, `Kick`, `UseItem`) and the wheel's labels and icons |
| `Voice` | An off-screen speaker (Leo, tutorial hints) for `Say("id", ...)` and Ink lines |
| `WalkArea` | Polygon visibility-graph pathfinder |
| `SoundSynth` / `Sfx` | Godot-free procedural sound effects and `*cue*` parsing, and the node that plays them (footsteps, story cues, room ambience) on the Effects bus |
| `MusicSynth` / `Music` | Godot-free synthesized music (scores for strings, organ, piano and a jazz band rendered as seamless loops), and the node that plays each room's track on the Music bus |
| `FlagSprite` | A sprite shown or hidden by story flags (e.g. the open drawer) |
| `Items` | Inventory item catalogue (name, icon, description), listed per act in `scripts/Core/Items/`; an id defined twice throws |
| `ItemScripts` / `CombineScripts` / `StoryPuzzles` (`scripts/Story`) | Story responses to inventory verbs and combinations that hold in any room, and the puzzles they share with room hotspots |
| `MicahKit` | Godot-free: the pinned notepad and lighter, the items each act keeps when its journal starts, and debug-start kits |
| `Notes` / `NotepadView` | Godot-free catalogue of Micah's notepad pages (unlocked by story flags, plus debug-start flags) and the full-screen reader |
| `PuzzleRules` / `PuzzleMigration` | Godot-free puzzle validators and one-time legacy-save normalization |
| `PuzzlePanel` / `PuzzleScreens` | Shared Art Deco puzzle frame and buttons; per-puzzle screens for the lift maze, dial, catalogue, cipher, crests, alarm plan and account index |

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
In the 1927 scenes, Micah's inner monologue is journal narration: `THOUGHT: text` in ink, or `await Think("...")`
in a room script. It is shown in faded sepia (`Hud.ThoughtColor`) along the top of the screen, blocks and skips like
speech, and nobody's mouth moves. Write it first person, present tense; keep replies to objects and lines said to
others as speech.
Start a conversation from a room script with `await Talk("knot")`.
Ink compiles on import in the editor; `repentance.ink.import` must keep `is_main_file=true`.

### Close-up panels

Framed close-ups pop up over a scene without blocking it; while one is up, speech sits along its bottom edge.
The convent's paired portraits place each speaker's speech beneath their own half.
Each is a `CloseUp` in `scripts/UI/CloseUp.cs` (the `CloseUps` catalog): an id, the picture under
`assets/art/ui/` (or a function of the settings, for variants such as Eleanor's dressed stage close-up) and fade
times. Show one with `Game.Hud.ShowCloseUp(CloseUps.Rose)` and `Game.Hud.HideCloseUp()`, or from ink with
`INSET: rose` and `INSET: none`. Use `INSET: none_now` (or `HideCloseUp(0)`) to remove a panel immediately
before a line or choice, without a lingering fade. The Hud handles the fades, the speech placement, swapping a variant when the
settings change, and hiding it on a room change.

To add one: commit the source picture under `tools/art/src/`, build the panel in `tools/art/closeup.py`
(`framed` for one picture, `framed_pair` for two side by side), add a `CloseUps` entry, then show it.

### Regenerating the art

All art is generated procedurally with Python and Pillow, so it can be tweaked and re-rendered. It is placeholder-quality but detailed.
Regenerate only the new puzzle props, icons and clue plates with `py -3.14 tools\gen_art.py puzzles`.
There are no imported 3D models: figure skeletons and perspective furniture are painted into PNGs by
`tools/art/figure.py` and `tools/art/furniture.py`.
The characters come from `tools/art/figure.py`, a small 3D-ish figure painter whose look is inspired by
early-90s VGA adventures such as *Indiana Jones and the Fate of Atlantis*: tall, naturally proportioned
bodies, shading lit from the top left, a darker outline on each material ("sel-out") and dithered fabric.
Each character is a spec dict in `tools/art/sprites.py`.

Story actions use articulated strips alongside the ordinary walk/talk sheets. Each action PNG has a matching
JSON file with the frame dimensions and per-frame `anchor`, `head`, `bounds`, and `seconds`. Anchors and head
points are measured in frame pixels; `PosePlayback` mirrors both with the artwork, plays in game time, and holds
the final frame. `Player.PlayPose` and `Actor.PlayPose` return `false` when interrupted or removed from the room;
call `SetPose(null)` after a completed action to restore ordinary animation. Existing single poses use the same
metadata. Eleanor's motel rise uses its own bed-scale, lamp-lit strip and a separate near-rail layer, not her
walking model.

```powershell
py -3.14 tools\gen_art.py sprites motel
py -3.14 tests\test_character_art.py
```

The art checks cover strip geometry, bounds, clipping, intermediate frames, restoration frames and deterministic
generation. `--autoplay` also captures each action frame, checks playback interruption and mirroring, and exercises
both knockout/recovery branches. Character quality and motion still require viewing the captures at game scale.

Room artwork is exported to PNGs and loaded as textures; Python is only used offline.
After changing a room painter, regenerate its alternate-state overlays too and update scene positions to the
printed crop origins. `py -3.14 -m unittest discover -s tests\art` checks committed images against their painters,
lighting and geometry contracts, and pixel-exact state composition, including the lowered Harrington ladder and
both mansion bed states.

```powershell
py -3.14 -m pip install --upgrade pillow numpy
py -3.14 tools\gen_art.py            # everything
py -3.14 tools\gen_art.py lobby      # a single step: sprites, items, office, lobby, eleanor_room, speakeasy, alley, convent, convent_road, chicago_map, ui
py -3.14 tools\gen_art.py club harrington  # club rooms and Harrington's building/office, including puzzle overlays; the hall's
                                           # stag portrait is reduced from tools\art\src\club_painting.png (head, antlers, collar)
py -3.14 tools\gen_art.py expansion_act1 expansion_act2 expansion_act3  # the five collect-and-combine locations, overlays and item icons
py -3.14 tools\gen_art.py closeup    # Eleanor's stage close-up and Rose's doorstep close-up, reduced to VGA pixels from the original pictures in tools\art\src\ (stage_closeup.png, rose_closeup.png); Eleanor's clothed variant paints her dress on;
                                     also Micah's close-up on the cathedral steps, from tools\art\src\beaten_closeup.png;
                                     and Micah and Eleanor outside the convent, two portraits in one panel, from
                                     tools\art\src\convent_micah.png and convent_eleanor.png; and the heraldry band at the foot
                                     of Harrington's portrait, painted by act2_rooms.heraldry
py -3.14 -m unittest discover -s tests\art -v  # image contracts and location rendering regressions
```

You can replace any PNG with hand-drawn art (Aseprite, Pixelorama...) as long as it keeps the same
size: backgrounds are 480×270, player frames are 64×96 in a 10×3 sheet (rows: horizontal, front, back; see `Player.cs` for the column layout), NPCs are 11-frame 56×96 strips (idle, two talk frames, walk 1-8 in side view), and items are 32×24.
Horizontal player idle/talk frames turn slightly toward the camera to reveal the face and chest; their walk cycles remain side-on.
Puzzle overlays and foreground layers keep their own crop sizes and scene positions. After regeneration,
check the printed overlay coordinates against the corresponding scene; moving a crop without its node
misaligns the object. Club rooms use their own 128-colour palettes so the stage's darkness does not
flatten the lounge's velvet and brass.

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
