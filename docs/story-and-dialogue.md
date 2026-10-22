# Story and dialogue

[Walkthrough](../Walkthrough.md) is the spec; [Story overview](story-overview.md) is the spoiler recap.

## Where story lives

| What | Where |
|---|---|
| Conversations | `dialogue/repentance.ink` (one file, 88 snake_case knots; `repentance.ink.import` must keep `is_main_file=true`) |
| Room behavior | `scripts/Rooms/<Room>.cs` |
| Item verbs, combinations, shared puzzles valid in any room | `scripts/Story/ItemScripts.cs`, `CombineScripts.cs`, `StoryPuzzles.cs` |
| Eleanor's interludes and coda | `scripts/Story/Interlude.cs` |
| Ending plumbing | `scripts/Rooms/Act3.cs`, rules in `src/Repentance.Rules/Endings.cs` |
| Items | `src/Repentance.Rules/Items/Items.{Micah,Act1,Act2,Act3}.cs` (the act that introduces them) |
| Notepad pages | `src/Repentance.Rules/Notes.cs` |
| Combination recipes | `src/Repentance.Rules/Recipes.cs` |
| Puzzle answers | `src/Repentance.Rules/PuzzleRules.cs` |
| Canonical playthrough (also film mode) | `scripts/Debug/Playthrough/Playthrough.{Act1,Act2,Act3,Endings}.cs` |
| Regression checks | `scripts/Debug/AutoPlay/AutoPlay.*.cs` |

## Ink conventions

External functions (declared at the top of the `.ink`, bound in `DialogueManager`):

| Function | Does |
|---|---|
| `has_item(id)`, `give_item(id)`, `take_item(id)` | Inventory |
| `has_flag(f)`, `set_flag(f)` | Flags (shared with C#) |
| `knows_note(id)` | Holds the notepad and the page is unlocked |
| `cash_amount()` | `CashRules.Balance` while holding `dollar`, else 0 |

Line prefixes (an upper-case word of at most 15 characters, then `:`):

| Line | Effect |
|---|---|
| `text` (no prefix) or `MICAH: text` | The player speaks |
| `SPEAKER: text` | Actor or `Voice` with `Id` = speaker (lower-cased) in the current room; falls back to the player |
| `THOUGHT: text` | Micah's journal narration, faded sepia at the top; first person, present tense, no mouth movement. Same as `Think()` in C# |
| `INSET: id` / `INSET: none` / `INSET: none_now` | Show a close-up from `CloseUps`, fade it out, remove it instantly |
| `IMAGE: name` | Full-screen `assets/art/ui/name.png`, waits for a click |
| `CUE: name` | Calls `Room.OnCue(name)` and waits: room staging mid-conversation |
| `*Bang*` (line starting with `*`) | Plays the matching sound cue ([Audio](audio.md)) |

Start a conversation from C# with `await Talk("knot")`. It runs inside `Game.Run`.

### Choices

- Micah speaks the chosen text, unless it starts with `(` (e.g. `(Leave)`).
- `*` choices are one-shot, `+` sticky. Repeatable knots need a sticky exit or fallback after choices are exhausted.
  Intentionally one-shot knots belong in `OneShotKnots` with a reason.
- **66-character limit**: the choice bar is 464 px of 7 px monospace characters (`InkScan.MaxChoiceChars`). For a
  longer line keep the spoken text and add a short label **inside the brackets**:

  ```ink
  * [Bathtub? Swell. The dirtier the hooch, the better I like it. Set 'em up, pal. #short: Bathtub? Swell. Set 'em up, pal.]
  ```

  Only add `#short:` when needed (an unneeded tag fails the test); it must be shorter and at most 66 characters.
  Leave room for inline `{...}` expansion. Tests pick choices by full text, not short labels.
  If the font or bar changes, recompute `floor(width / advance)` and update
  `MaxChoiceChars`; `AutoPlay.ChoiceBarLimitTest` fails until it matches.
- Find long labels: `dotnet test tests/Repentance.Content.Tests --filter FitsTheChoiceBar`.

### Voice and scripture

- 1927 noir, first person. Thoughts are journal entries; speech to objects or people stays speech.
- Biblical lines are paraphrases or thematic applications, not quotations, unless marked; keep them to two sentences
  inside the conversation, not sermons. Repentance is turning back and receiving grace, not earning it. Caleb
  carries the invitation (central line in `caleb_act2`); Agatha's condemnation is the contrast, until she confesses her own failure at gunpoint (`nun_threat2`); Rose stays cautious
  (forgiveness is not restored trust). The placements are listed in [Story overview](story-overview.md#scripture).
- Doctrine: Caleb is a Catholic priest of 1927; Micah is a baptised Catholic who practises irregularly, Protestant
  in his theology, Catholic in the forms he uses. Keep the seal (Caleb never repeats what he heard in confession,
  wherever he heard it, nor hints at it), absolution only after sorrow and a purpose of amendment, and hope rather than verdicts for the dead. Check new lines against [Theology](theology.md).

## Flags

Flags are snake_case strings in `GameState`, set from C# (`State.SetFlag`) or Ink (`set_flag`). Common patterns:
`seen_<room>` (first-visit cutscenes), `took_<item>`, `knows_<thing>`, `<thing>_open`, `<scene>_done`,
`ending_<N>`. Hotspots and `FlagSprite`s show/hide on them. Every flag read must be set somewhere and vice versa
(`StoryIntegrityTests`; exceptions in `UnreadFlags`, `UnsetFlags`).

## Items

```csharp
new ItemDef("photo", "photograph", "res://assets/art/items/photo.png", "...description...")
```

- Icons are 32x24 PNGs in `assets/art/items/`. A duplicate id throws at startup.
- Every item must be obtainable (`StoryIntegrityTests`; exceptions in `IndirectItems`).
- Cash is the `dollar` item; the balance (22 at start) is derived from payment flags in `CashRules`.
- `MicahKit`: `notepad` and `lighter` are pinned first. Act transitions retain acquired items listed in
  `ActKeep`: Act 2 keeps `revolver, lockpick, card, mirror, cloth, faith_ring, cross`; Act 3 keeps
  `revolver, cloth, faith_ring, cross`. Daniel and Eleanor never carry Micah's pinned items.
- The notepad (`Notes`): `NoteDef(Id, Title, Unlock[], Lines, Sketch)`. A page shows when any `Unlock` flag is set;
  lines can need an extra flag. Showing the notepad counts as showing the clue (`Room.Shows`).

## Combinations and puzzles

- Simple combinations: add a `Recipe` (inputs, result, consumed items, line, optional catalyst/tool/flag) to
  `Recipes`, and wrong pairs with a hint to `Refusals`. Recipes are symmetric.
- Combinations with staging (room change, image, puzzle screen): `Story.CombineScripts.TryCombine`, which runs first.
- Puzzle screens are opened with `await Game.Hud.Puzzle.Open(PuzzleKind.X)` (returns `false` on cancel); answers
  live in `PuzzleRules` (e.g. safe: directions `0,1,0`, numbers `12,40,7`). Puzzles are untimed and retryable.
- Changed saved puzzle progress: follow [migration/versioning rules](saves-and-settings.md#changing-the-format).

### Riddles and ordered steps

For interlude puzzles 17 and 18, order is enforced in the room script: each step is a `case` guarded by the flags of
the steps before it, and an out-of-order attempt gets a hint line instead of an action. The guarded case goes before
the one that acts. Keep each step's flag on the item or room so a save made halfway loads back halfway. The safe and
alarm bell instead validate their ordered settings in their puzzle screens through `PuzzleRules`.

| Puzzle | Steps and flags | Out of order |
|---|---|---|
| 17, Room 507 (`EleanorRoom`) | box packed (`interlude_box_packed`) -> closet opened (`interlude_closet_open`) -> box in the half-open safe (`interlude_box_in_safe`) -> safe shut (`interlude_safe_locked`) -> combination written on her blank slip at the desk (`interlude_riddle_written`) -> riddle in the drawer (`interlude_riddle_in_drawer`) -> drawer locked with her key (`interlude_drawer_locked`) -> call on the vanity telephone (`interlude_phoned`) -> her packed duffle taken from the foot of the bed (`interlude_took_bag`) | the closet, safe and drawer say what comes first; the telephone and door name the first missing step (the door last asks for the bag); the slip and key are restored from progress on entering |
| 18, dressing room (`ClubBackstage`) | powder (`interlude_powdered`) -> lipstick (`interlude_lips`) -> hairpin (`interlude_made_up`) | lipstick on a bare face, or the hairpin before the mouth, is refused and kept |
| Safe, Room 507 (`PuzzleKind.Safe`) | directions right, left, right; numbers 12, 40, 7 on a 0-49 dial (`PuzzleRules.Safe`) | the handle says how many tumblers fell; nothing is used up |
| Alarm bell (`MansionExterior`, `PuzzleKind.Bell`) | plan: hold the hammer, tie it, release the hand (`PuzzleRules.Bell`) | any other plan (cutting the wire would ring the gong) stops before he touches it |

Room numbers on the service-lift note follow `LiftMaze.Width` (501 to 513); `NotesTests` checks it.

### Decisions

Most story decisions are Ink choices that set a flag (`~ set_flag(...)`); the room script reads the flag after the
knot ends and chooses where to go. Giving up on the steps is the exception: "(Give up.)" in `beaten_choice` sets
nothing, and `ChurchExterior` sets `gave_up_steps` when `keep_going` is absent. Choices behind a gate read derived
flags (`can_walk_away`, `can_spare`) that
`Act3.UpdateGates` sets from `Endings` helpers just before the knot. For the bedroom branches, Eleanor's two refusals
(`eleanor_refused_abbess`, `eleanor_refused_drugs`) are combined through `Endings.EleanorHeldOut`, which needs both.
`ClubBackstage` also reads `eleanor_refused_drugs` directly, to play the blackout instead of the ordinary departure.
The full branch map is in [Story overview](story-overview.md#branches-and-endings). Eleanor's persuasion is not a
single choice but a weighted score over four turns: see [Eleanor's persuasion](eleanor-persuasion.md) before changing
its lines.

To add a branch: set a new flag from the choice, add the gate helper to `Endings` if the choice is conditional, give
`Endings.Resolve` a case in the right priority (and `EndingsTests` a row), route the scene in `Act3.End`, add a
`Playthrough` route that reaches "The End", and an `AutoPlay` regression for any combination of flags that could
send the story the wrong way.

## Acts and interludes

| Transition | Code | Effect |
|---|---|---|
| Prologue -> Act 1 | `Attic` (journal read) | Daniel reads; play moves to the 1927 office |
| Act 1 -> 2 | `Attic.EndOfActOne` | Stash items, `attic_night`, dinner call, "End of Act One", `StoryAct = 2` |
| First interlude | `Interlude.BeginFirst` / `EndFirst` | Flag `interlude1`, play Eleanor from her hotel room; `EndFirst` restores the Act 2 kit and resumes Micah on `motel_fire_escape` entry `interlude1` (the talk and the kiss), then `motel_night`, "Days later", the office and the motel return (`motel_return`, `motel_clerk_return`) |
| Act 2 -> 3 | `Attic.EndOfActTwo` | Stash, clear `masked`, `StoryAct = 3`, present-day bedroom |
| Second interlude | `Interlude.BeginSecond` / `Taken` / `EndSecond` | Flag `interlude2`, `motel_night` -> `club_backstage`; restores the Act 3 kit, sets `masked`, `club_stage` |
| Eleanor's coda | flags `eleanor_coda`, `eleanor_epilogue` | Eleanor plays again after the old man's prayer |

`Interlude.EleanorPlays` is true during any of the four flags: Eleanor's sheet is used, the notepad is hidden, generic
exits are blocked, and `Interlude.DefaultLine` replaces generic lines. In the two interludes (`Interlude.SatchelOpen`)
she has her own satchel for Puzzles 17 and 18: she takes, joins and uses only what she finds there, and `EndFirst`/
`EndSecond` clear it before Micah's kit comes back. In the coda and epilogue the satchel is hidden and held items are refused.
Rooms visited in an interlude branch on these flags (e.g. `Speakeasy.InterludeInteract`).

## Endings

`Endings.Resolve(hasFlag)` - first match wins:

| Order | Condition | Ending |
|---|---|---|
| 0 | `alarm_stayed`, else `alarm_ran` | 14 (shot in the kitchen; Caleb writes), else 13 (out of Chicago, alone) |
| 1 | `eleanor_struck` | 8 if `eleanor_burned`, else 9 |
| 2 | `eleanor_weary` | 10 if `StaysFree`, else 11 |
| 3 | `surrendered_tony`, or `killed_tony` and `spared_oldman` | 12 (prison, Caleb, after Tony) |
| 4 | `gave_up_steps`, `walked_away` or `spared_oldman` | 1 (Rose) |
| 5 | `repented` | 6 |
| 6 | `shot_eleanor` or `shot_himself` | 7 |
| 7 | `StaysFree` | 2 if `eleanor_convinced`, else 3 (outskirts) |
| 8 | otherwise | 4 if `eleanor_convinced`, else 5 (prison) |

Endings 8-11 require `EleanorHeldOut` (`eleanor_refused_abbess` and `eleanor_refused_drugs`). `EleanorFollows` is
`eleanor_convinced` or `eleanor_weary` (she comes to the kitchen); only a convinced Eleanor speaks on the way out,
a weary one follows in silence ("Not one more word in this house"). `KeepsJournal`:
1, 6, 8, 9, 10, 11, 12. Every ending but 7 and 14 has the "The next morning" caption (`Act3.Finish`); the Joliet
visits open on "Six months later", ending 12 on "A year later" (`Prison.OnEnter`). `Act3.End` resolves, sets `ending_N` and moves to the ending room. Gate helpers:
`CanWalkAwayFromBartender`, `CanSpareOldMan` (after `killed_tony` it also needs `confessed_tony`), `CanOfferCross`,
`ChurchReturned`, `InsistedForgiveness`. `TonyWantsRevenge` (`shot_bartender` without `killed_tony`) is the Tony-alive
case the epilogues tell. `warned_tony` (the warning shot into the wall) leaves Tony unhurt, so no revenge; he gives the key but not
the alarm, and opening the kitchen door without a look at it rings the bell (`alarm_footsteps`): run (`alarm_ran`)
or stay (`alarm_stayed`).
Every route must reach "The End" (`Playthrough` routes `1`-`14`, `1-oldman`, `1-steps`, `12-oldman`).
In Eleanor's coda, `MansionBedroom.ClampWalkTarget` keeps her on the bed side of the old man until she strikes, so no
click or refusal walks her past him to the door.

## Checklist for a story change

1. Update `Walkthrough.md`.
2. Implement in `.ink`, `scripts/Rooms`, `scripts/Story`, items, notes.
3. Update the beat in `scripts/Debug/Playthrough/Playthrough.ActN.cs` (Act 3 routes branch on `_route`); add a
   regression in `scripts/Debug/AutoPlay/AutoPlay.ActN.cs` for anything that could break quietly. Shared input and
   puzzle helpers live in `scripts/Debug/Harness.cs`.
4. Check [save compatibility](saves-and-settings.md#changing-the-format).
5. Run `dotnet build`, `tools\run\test.ps1 -Suite unit, playthrough` (add `autoplay` if you touched AutoPlay or
   `Harness.cs`).

The unit tests that guard the story (`StoryIntegrityTests`, `InkWalkTests`) and their allowlists are described in
[Testing](testing.md#story-tests-and-allowlists). Agents: `.claude/skills/story-change/SKILL.md`.

For hands-on story review use `tools/run/game.sh` / `tools\run\game.ps1` (normal player data, no automation).
For a requested watch-only review, `tools/run/film.sh --speed 4 --ending 5` selects speed explicitly; omit
`--speed` for 1x or use `-s 4`. These reviews do not replace the required test suites.
