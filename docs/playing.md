# Playing Repentance

How to start the game: [Getting started](getting-started.md#first-run). Story spoilers:
[Story overview](story-overview.md).

## Controls

- At launch a verse (Luke 15:7) fades in over black before the title screen; any key, click or tap skips it.
- **Left click** on the floor to walk. Left click on an object does the obvious thing: talk to people,
  go through exits, look at everything else. A character drawn in front of an object is the one you point at.
  On the map of Chicago, hovering a place shows its description at the bottom and a left click goes there.
- **Right click** on an object opens the **verb wheel**: 👁 *Look*, ✋ *Hand* (take, use, open, push),
  👄 *Talk*, 🥾 *Kick*. Click an icon, or hold the right button and release it over one.
- **Satchel** (bottom right) or **I** opens the inventory. Left-click an item to hold it (a small icon follows the cursor), then click
  it on an object or person to use or give it (or on another item to combine them). Right-click
  anywhere to put it back. Right-click an item in the satchel to open its verb wheel. Picking an item leaves the
  satchel open, so a second click combines; moving the cursor off the satchel closes it.
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
  unlimited retries. Unsubmitted settings reset when closed; collected clues remain available. Puzzles with an
  arrow pad (the staff lift, the auditor's index) also move with the **arrow keys** or by **dragging/swiping**
  across the diagram, one step per cell.
- Use the satchel's **< / >** page buttons when carrying more than twelve items. A held item can be
  combined with an item on another page.
- **Esc** opens the pause menu: *Resume*, *Save game*, *Load game*, *Settings*, *Quit to title*, *Quit to desktop*
  (asks *Quit without saving?* first). The title screen offers *Continue* (most recent save), *New game*, *Load game*,
  *Settings* and *Quit game*. The quit entries are not offered on Android.
- When the story ends on *The End*, a click, a key or ten seconds return to the title screen.

### Touch (Android)

- **Tap** is a left click. **Touch and hold** (about half a second) is a right click: it opens the verb wheel, which
  stays open when you lift your finger; tap an icon, or keep holding and slide onto one before lifting.
- **MENU** (bottom left) or the phone's **back** gesture/button is Esc. **NOTES** opens the notepad; swipe its pages
  left or right.
- With an item held, touch and hold anywhere puts it back. Dragging works on the arrow-pad puzzles as with a mouse.
- The crosshair and the touch buttons hide as soon as a mouse moves; the *Full screen* setting is not offered (the
  game is always full screen on a phone).

## Settings

Stored in `user://settings.cfg`, separate from saves (details: [Saves and settings](saves-and-settings.md)):

- **Nudity**: Off by default (Eleanor's dressed club sprite); On uses the implied-nude variant.
- **Full screen**: Off by default; **F11** or **Alt+Enter** anywhere. Borderless, whole-pixel scaling.
- **Effects volume** (80%) and **Music volume** (70%): left click louder, right click quieter, steps of 10%.

Sound and music are synthesized by the game (music as each room needs it), apart from the recorded piano, sax and
bass. The game autosaves on every room change
and has five manual slots; saving over an occupied slot asks for confirmation first.
