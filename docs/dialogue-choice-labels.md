# Dialogue choice labels that fit the choice bar

The choice bar at the bottom of the screen (`Hud.ShowChoices`) shows one option per row. Each row is a single
line that is clipped, not wrapped, so a label that is too long is cut off at the right edge of the screen.

## The width rule

- The bar's text width is `Hud.ChoiceTextWidth` = `ScreenW - 16` = **464 px** (the native screen is 480x270).
- Dialogue uses Departure Mono at `Hud.DialogueFontSize` = 11 px. The font is monospace, with an advance of
  350/550 em, so every character is **7 px** wide.
- So a label fits when it has **at most 66 characters** (66 x 7 = 462 px). That number is
  `InkScan.MaxChoiceChars`.

## Shortening a choice

The full sentence stays the choice text: it is what Micah says once the player picks it. To show something
shorter in the bar, add an Ink choice tag `#short:` **inside the brackets**:

```ink
* {menu && cash_amount() >= 1} [Bathtub? Swell. The dirtier the hooch, the better I like it. Set 'em up, pal. #short: Bathtub? Swell. Set 'em up, pal.]
    -> bartender.gin
```

- Choice bar shows: `Bathtub? Swell. Set 'em up, pal.`
- Micah says: `Bathtub? Swell. The dirtier the hooch, the better I like it. Set 'em up, pal.`

Do not change the spoken text to make it fit; only add or edit the `#short:` label.

### How it works

- Ink 1.1 keeps tags out of the choice text: at runtime `choice.Text` is the full sentence and `choice.Tags`
  holds `short: ...`.
- `DialogueManager` builds two lists for every offer. The full labels go to `AutoChoose`, `ChoicesOffered`,
  coverage and `game.Say`. `ShownChoices` holds the `#short:` label when a choice has one (`InkScan.ShownLabel`),
  and is what `Hud.ShowChoices` displays. Film mode and AutoPlay screenshots draw `ShownChoices` too.
- Playthrough and AutoPlay pick choices by their full text, so a short label never changes which option a test
  picks.
- `InkScan` drops tags from `InkChoice.Label` (still equal to the runtime text) and stores the bar label in
  `InkChoice.Shown`.

### Writing a short label

- Keep Micah's meaning and voice. Usually the first clause or two is enough: the player reads the full line a
  moment later.
- Keep it at most 66 characters, and shorter than the full line. Leave some room if the label has inline `{...}`
  content, because the static check counts only the literal text.
- Only add `#short:` when the full text does not fit. The unit test fails on a tag that isn't needed.
- Silent choices like `(Leave)` must fit as written; they are not spoken, so there is nothing to shorten.

## Checks

| Check | Suite | What it catches |
|---|---|---|
| `StoryIntegrityTests.EveryChoiceFitsTheChoiceBar` | unit | a static label over 66 characters, an empty or longer `#short:`, or an unneeded one |
| `InkWalkTests.EveryOfferedChoiceFitsTheChoiceBar` | unit | the same for the labels the Ink runtime actually offers, tags read the way the game reads them |
| `AutoPlay.ChoiceBarLimitTest` | autoplay | `MaxChoiceChars` no longer matching the real font and bar width |
| `AutoPlay.CheckChoiceBar` (every offer) | autoplay | a label measured wider than the bar, or buttons not matching `ShownChoices` |
| `AutoPlay.ShortChoiceLabelTest` | autoplay | the bar not using the short label, or Micah not speaking the full line |

To find labels that are too long, run `dotnet test tests/Repentance.Tests/Repentance.Tests.csproj --filter
FitsTheChoiceBar`: the failure lists each line number, its length and its text.

## If the font, size or bar changes

Recompute the limit as `floor(ChoiceTextWidth / advance)`, where advance = font advance (em units) / units per
em x font size in px. Update `InkScan.MaxChoiceChars`; `AutoPlay.ChoiceBarLimitTest` fails until it matches. For
a proportional font, a character limit is no longer exact: the AutoPlay measurement (`CheckChoiceBar`) is the
real check, so keep the unit-test limit conservative.
