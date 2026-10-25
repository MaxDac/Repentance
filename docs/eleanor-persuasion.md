# Eleanor's persuasion

The reference for the bedroom persuasion (`eleanor_persuade` in `dialogue/repentance.ink`). Read it before changing
any of its lines, weights or thresholds: the tests and the canonical playthrough pick lines by their text and expect
the totals below. The story spec is in [Walkthrough](../Walkthrough.md) (Act Three, Harrington's bedroom), and the
branch map in [Story overview](story-overview.md#branches-and-endings).

## When it runs

After Micah shoots the old man (`oldman_taunt`, "Shoot him"), `MansionBedroom` starts `eleanor_persuade` unless
Eleanor held out (`Endings.EleanorHeldOut`: she told Agatha the truth *and* refused the old man's gin and powder). If
she held out she is too worn out to argue (`eleanor_weary`, endings 10 and 11) and there is no persuasion.

## Rationale

The persuasion therefore only plays when Eleanor gave in at least once in the interludes: she seduced Agatha, took
the old man's gin and powder, or both. Having fallen back into that pattern, she answers what she knows, the
possessive, earthly, visceral voice of the men who already own her, the old man's way. Micah's lines are typed by
that voice, and each type is weighted by how strongly it reaches her:

| Type | Character | Points | Constant |
|---|---|---|---|
| Possessive | Claiming, visceral, earthly; the old man's style | 4 | `PERSUADE_POSSESSIVE` |
| Rational | The plain facts of her situation | 2 | `PERSUADE_RATIONAL` |
| Positive | Reassuring, hopeful | 1 | `PERSUADE_POSITIVE` |
| Clumsy | Tactless or beside the point | 0 | `PERSUADE_CLUMSY` |

When she is convinced, she says so in the same terms: "You talk like them, Micah. Like every man who ever wanted me.
God help me, maybe that's why I believe you." Ending 2, where she later betrays him again, follows from that.

## The rule

Four turns, four lines on each turn (one of each type, in a different order on each turn). Every line adds its
points to `persuade_score`. After the fourth turn, `persuade_score >= PERSUADE_THRESHOLD` (10 out of 16) sets
`eleanor_convinced` and she comes (`eleanor_comes`); otherwise `eleanor_refused` is set and `MansionBedroom` plays
the footsteps (`eleanor_footsteps`).

Consequences of 4 / 2 / 1 / 0 with a threshold of 10:

- **One clumsy line can be overcome, two can't.** One clumsy line leaves at most 12; two leave at most 8.
- **At least one possessive line is needed.** Without one, the maximum is 4 x 2 = 8.
- **Random picks** convince her in 53 of the 256 sequences (about 21%). A threshold of 11 would be 31 (12%), and
  12 would be 19 (7%).

Every mix of types that convinces her (the order of the turns doesn't matter, only which types were picked):

| Possessive | Rational | Positive | Clumsy | Points |
|---|---|---|---|---|
| 4 | 0 | 0 | 0 | 16 |
| 3 | 1 | 0 | 0 | 14 |
| 3 | 0 | 1 | 0 | 13 |
| 3 | 0 | 0 | 1 | 12 |
| 2 | 2 | 0 | 0 | 12 |
| 2 | 1 | 1 | 0 | 11 |
| 2 | 1 | 0 | 1 | 10 |
| 2 | 0 | 2 | 0 | 10 |
| 1 | 3 | 0 | 0 | 10 |

Near misses that don't: 2 possessive + 1 positive + 1 clumsy (9), 1 possessive + 2 rational + 1 positive (9),
4 rational (8), 2 possessive + 2 clumsy (8).

## The lines

The options appear in the order listed. Eleanor's opening lines come first on each turn.

### Turn 1: "Leaving? To go where? There's no place in this city they can't find me."

| Type | Micah | Eleanor | Micah's thought |
|---|---|---|---|
| Possessive | "I didn't come all this way to leave you here, Eleanor." | "All this way. For me." / "He used to say that. That he'd come all the way back from the lake, just for me." | "She hears it. The way she must have heard it from him." |
| Rational | "Then we don't stay in this city. We're out of it tonight." | "Out of it. You say it like it's a door you can just walk through." | |
| Positive | "We'll find somewhere quiet. Somewhere nobody knows your name." | "Nobody knowing my name. That's a nice dream, Micah. I stopped having it." | |
| Clumsy | "You can't stay here. Not now. They'll pin it on you." | "They'll pin it on whoever they like. They always do." | "Wrong thing to say. She's talking to the carpet now, not to me." |

Also offered: "(Leave her, and turn yourself in.)", which sets `repented` (ending 6) and ends the
conversation.

### Turn 2: "Theodore will be here by morning. He'll know what to do. He always does."

| Type | Micah | Eleanor | Micah's thought |
|---|---|---|---|
| Positive | "Whatever comes in the morning, you won't face it alone." | "Alone is the one thing I've never been allowed to be, Micah." | |
| Clumsy | "Theodore's a coward. I'll handle him." | "With that? You'd have to shoot every Harrington in Chicago. There are more of them than bullets." | "Wrong thing to say. She's talking to the carpet now, not to me." (only while she can still be won) |
| Possessive | "Forget Theodore. You've got me now." | "Got you." / "That's what they all say. And somehow I always end up believing it." | "She doesn't pull away. I don't like why." |
| Rational | "He'll take you back like he always does. And lend you out again on Thursdays." | "..." / "Yes. He will. He'll even say he's sorry about it." | |

### Turn 3: "And what would I do out there? I don't know how to be anything but theirs."

| Type | Micah | Eleanor | Micah's thought |
|---|---|---|---|
| Clumsy | "You can be anything you like. A singer. A nurse. Anything." | "The Club said that too, the first night. Anything I liked." | "Wrong thing to say. She's talking to the carpet now, not to me." (only while she can still be won) |
| Rational | "You'd find work, like anybody. Out there nobody owns you." | "Work. I suppose I'd learn. I learned everything else." | |
| Possessive | "Then be mine instead. I'll look after you." | "Yours, instead of theirs." / "At least it would be one man's." | "I sound like him. She's listening anyway. Maybe because of it." (only while she can still be won) |
| Positive | "You don't have to know tonight. You only have to walk through that door." | "One door." / "I've walked through a lot of doors, Micah. I never once picked which." | |

Also offered: "(Leave her.)": Micah escapes alone (endings 3 or 5).

### Turn 4: "Why do you even care, Micah? What do you want from me?"

| Type | Micah | Eleanor |
|---|---|---|
| Positive | "Nothing. Come or stay, it's yours to decide. But decide it yourself, for once." | "Nobody ever asked me. Not once. Not him, not Theodore, not the nuns." |
| Clumsy | "Theodore paid me to find you. I'm only finishing the job." | "So I'm a job. Twenty dollars a day, and expenses." |
| Rational | "The first night I met you, you said you couldn't go back there. Now you don't have to." | "I did say it. I say a lot of things, to a lot of men. That one I meant." |
| Possessive | "You. I've wanted you since the first time I saw your photograph." | "There it is. No speeches. Just wanting." / "At least you're honest about it. They never were." |

Also offered: "(Leave her.)" and "(Shoot Eleanor.)" (`shot_eleanor`, ending 7).

Then the verdict:

- **Convinced** (10 or more): "..." / "You talk like them, Micah. Like every man who ever wanted me." / "God help me,
  maybe that's why I believe you." Sets `eleanor_convinced`, then `eleanor_comes`.
- **Refused**: sets `eleanor_refused`; "Then I've decided. I'm staying, Micah." / "Please. Just go. Before they
  come." The footsteps follow.

## Hints

Micah's thoughts are the player's only feedback; the score is never shown.

- After a possessive line on turns 1-3: a warming but uneasy thought (on turn 3 only while she can still be won).
- After a clumsy line on turns 1-3, while she can still be won: "Wrong thing to say. She's talking to the carpet now,
  not to me."
- At the start of a turn, once she can no longer be won (even all-possessive lines on the remaining turns would fall
  short): turn 3 "Her eyes keep going to the other door. I'm losing her."; turn 4 "Further away with every word.
  Somewhere I can't follow, in the same room."

"Can still be won" is `persuade_score + PERSUADE_POSSESSIVE * turns_left >= PERSUADE_THRESHOLD`, where `turns_left`
is the number of turns still to play after the current line. The Ink writes it out with the literal turn count
(`* 2` after turn 2, `* 1` after turn 3).

## Ink implementation

- `VAR persuade_score = 0` and the five `CONST`s sit at the top of `dialogue/repentance.ink`. The knot resets the
  score on entry (`~ persuade_score = 0`). Saves are refused during a conversation (`Game.CanSave`), so the score
  never needs to survive a load.
- Each line is a one-shot `*` choice that adds its constant (`~ persuade_score += PERSUADE_...`), then plays
  Eleanor's reply and any hint. Turns are separated by gathers (`-`).
- After turn 4 a gather computes `~ temp convinced = persuade_score >= PERSUADE_THRESHOLD`, then branches.
- The action options are unchanged: turning himself in on turn 1 only, "(Leave her.)" on turns 3 and 4 (the
  `= leave` stitch), "(Shoot Eleanor.)" on turn 4 only. `AutoPlay.CheckPersuasionTurns` asserts those positions.
- For the ordinary persuasion outcomes, `Endings.cs` uses `eleanor_convinced` together with the fire/documents flags; it reads neither `eleanor_refused` nor the score.

## Changing the lines

- **Rewording a line**: keep its type, and check the tests that pick it by a fragment of its text:
  - `scripts/Debug/Playthrough/Playthrough.Endings.cs` (routes 2, 3, 4, 5 and 7);
  - `scripts/Debug/AutoPlay/AutoPlay.Endings.cs` (`Convinces`, `OneClumsyForgiven`, `TwoClumsy`, `OneShort`,
    `Refuses`), also used by `AutoPlay.Act3.cs`.
  Update this page's tables. Choice labels have a 66-character limit (`#short:`, see
  [Story and dialogue](story-and-dialogue.md#choices)).
- **Changing a line's type**: change its `PERSUADE_...` constant, move it in the tables, and recheck the test
  sequences above, whose comments state each total.
- **Retuning weights or the threshold**: change the `CONST`s, then recompute the rule's consequences, the winning-mix
  table and the odds here, the totals in the test comments, and the hint conditions (they assume
  `PERSUADE_POSSESSIVE` is the highest weight).
- **Adding a turn**: add a gather, raise the multipliers in the "can still be won" conditions, and update
  `CheckPersuasionTurns` (it expects four turns).
- Run `dotnet build`, then `tools\run\test.ps1 -Suite unit, playthrough, autoplay`.
