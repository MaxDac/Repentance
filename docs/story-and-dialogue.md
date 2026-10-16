# Story and dialogue

[Walkthrough](../Walkthrough.md) is the spec; [Story overview](story-overview.md) is the spoiler recap.

## Where story lives

| What | Where |
|---|---|
| Conversations | `dialogue/repentance.ink` (one file, 78 snake_case knots; `repentance.ink.import` must keep `is_main_file=true`) |
| Room behavior | `scripts/Rooms/<Room>.cs` |
| Item verbs, combinations, shared puzzles valid in any room | `scripts/Story/ItemScripts.cs`, `CombineScripts.cs`, `StoryPuzzles.cs` |
| Eleanor's interludes and coda | `scripts/Story/Interlude.cs` |
| Ending plumbing | `scripts/Rooms/Act3.cs`, rules in `scripts/Core/Endings.cs` |
| Items | `scripts/Core/Items/Items.{Micah,Act1,Act2,Act3}.cs` (the act that introduces them) |
| Notepad pages | `scripts/Core/Notes.cs` |
| Combination recipes | `scripts/Core/Recipes.cs` |
| Puzzle answers | `scripts/Core/PuzzleRules.cs` |
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
- Find long labels: `dotnet test tests/Repentance.Tests/Repentance.Tests.csproj --filter FitsTheChoiceBar`.

### Voice and scripture

- 1927 noir, first person. Thoughts are journal entries; speech to objects or people stays speech.
- Biblical lines are paraphrases or thematic applications, not quotations, unless marked; keep them to two sentences
  inside the conversation, not sermons. Repentance is turning back and receiving grace, not earning it. Caleb
  carries the invitation (central line in `caleb_act2`); Agatha's condemnation is the contrast; Rose stays cautious
  (forgiveness is not restored trust). The placements are listed in [Story overview](story-overview.md#scripture).

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
  live in `PuzzleRules` (e.g. safe: directions `0,1,0`, numbers `4,31,17`). Puzzles are untimed and retryable.
- Changed saved puzzle progress: follow [migration/versioning rules](saves-and-settings.md#changing-the-format).

## Acts and interludes

| Transition | Code | Effect |
|---|---|---|
| Prologue -> Act 1 | `Attic` (journal read) | Daniel reads; play moves to the 1927 office |
| Act 1 -> 2 | `Attic.EndOfActOne` | Stash items, `attic_night`, dinner call, "End of Act One", `StoryAct = 2` |
| First interlude | `Interlude.BeginFirst` / `EndFirst` | Flag `interlude1`, play Eleanor from her hotel room; restores the Act 2 kit, back to the office |
| Act 2 -> 3 | `Attic.EndOfActTwo` | Stash, clear `masked`, `StoryAct = 3`, present-day bedroom |
| Second interlude | `Interlude.BeginSecond` / `Taken` / `EndSecond` | Flag `interlude2`, `motel_night` -> `club_backstage`; restores the Act 3 kit, sets `masked`, `club_stage` |
| Eleanor's coda | flags `eleanor_coda`, `eleanor_epilogue` | Eleanor plays again after the old man's prayer |

`Interlude.EleanorPlays` is true during any of the four flags: Eleanor's sheet is used, the notepad and satchel
are hidden, held items are refused, generic exits are blocked, and `Interlude.DefaultLine` replaces generic lines.
Rooms visited in an interlude branch on these flags (e.g. `Speakeasy.InterludeInteract`).

## Endings

`Endings.Resolve(hasFlag)` - first match wins:

| Order | Condition | Ending |
|---|---|---|
| 1 | `eleanor_struck` | 8 if `eleanor_burned`, else 9 |
| 2 | `eleanor_dismissed` | 10 |
| 3 | `gave_up_steps`, `walked_away` or `spared_oldman` | 1 (Rose) |
| 4 | `repented` | 6 |
| 5 | `shot_eleanor` or `shot_himself` | 7 |
| 6 | `StaysFree` | 2 if `eleanor_convinced`, else 3 (outskirts) |
| 7 | otherwise | 4 if `eleanor_convinced`, else 5 (prison) |

Endings 8-10 require `EleanorHeldOut` (`eleanor_refused_abbess` and `eleanor_refused_drugs`). `KeepsJournal`:
1, 6, 8, 9, 10. `Act3.End` resolves, sets `ending_N` and moves to the ending room. Gate helpers:
`CanWalkAwayFromBartender`, `CanSpareOldMan`, `CanOfferCross`, `ChurchReturned`, `InsistedForgiveness`.
Every route must reach "The End" (`Playthrough` routes `1`-`10`, `1-oldman`, `1-steps`).

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
