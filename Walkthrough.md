# Repentance walkthrough

This file describes the story as it is **currently implemented**. To change the game, edit this file:
the difference from the committed version is what still has to be implemented. Anything not
described here (other verbs, flavour lines) is left to the implementation.

## Act 1

### Present day - The attic

- Daniel (the dad) is in the attic, calling his son Leo, but Leo doesn't come over ("In a minute!").
- Daniel can lift the dust sheet and knock over the boxes, spilling the old papers.
- In the suitcase there is a key, but it can't open the large steamer trunk.
- **Puzzle 1 - Tool tin:** the tin is too heavy to hide under loose papers. Searching the boxes again opens the
  MISC box; inside is a locked tool tin with a little brass padlock, which Daniel sets on top of the box below. Use the suitcase key on the tin to take the crowbar. Only that crowbar opens the trunk.
- In the trunk Daniel finds Micah Jones's journal and starts reading it (hand on the journal in the satchel).
  The caption "Chicago, 1927." leads to Micah's office.

### Chicago, 1927

#### Micah's office

- Micah's thoughts, then the conversation with Teddy Harrington III about his missing wife, Eleanor
  Harrington; Teddy gives Micah her photograph. At the end of the conversation Teddy walks out of the room.
- Micah can't walk out on Teddy before the conversation is over.
- The top drawer of the desk holds a revolver, the money ($22 cash) and a lockpick. Micah takes all three
  and shuts the drawer; it stays shut for the rest of the story
  (the bottom drawer only holds unpaid bills).
  The cash is framed as his existing fictional $20 daily fee plus $2 from a previous job, not a claim
  about average PI income. For purchasing-power context, the
  [NBER/BLS manufacturing weekly-earnings series](https://fred.stlouisfed.org/series/M08261USM052NNBR)
  reports $24.37 for October 1927; the $10 Sal bribe is a substantial payment, not an ordinary tip.
- Micah can't get out of his office without having taken these items.
- The door leads to the Aurelian Hotel lobby.

#### Hotel (Aurelian Hotel lobby)

- Micah's goal is to get into the room Eleanor was staying in before she disappeared.
- Micah arrives from State Street through the revolving door and walks into the lobby.
- The conversations with the concierge and the bellboy stay as they were: the concierge has seen nothing.
- Micah has to bribe the bellboy with $1 from his cash for his memory, then with
  another $1 to visit Eleanor's room: the second dollar lets him take the staff elevator up to the fifth-floor
  linen room next to Eleanor's room. Between the two dollars, Micah won't leave through the revolving door.
- The bellboy's memory: on Tuesday night, having a smoke out back, he saw two big fellas (broken nose, cheap suit,
  expensive cigar) escort Eleanor out of the service door and away down the alley in a car with no lights,
  without anybody seeing. He doesn't mention the Blue Lantern; the matchbook in the brass box makes that connection.
- Before the bellboy's memory, Micah won't leave through the revolving door either: somebody in the lobby saw
  her go.
- **Puzzle 2 - Service lift maze:** after the bribe, the bellboy explains that the staff cage runs a maze of
  shafts and laundry chutes behind the walls, that every floor has an identical linen room, that he wants the
  fifth-floor one right next to 507, and that rooms count up west (01, by the stairs) to east (13, by the fire escape).
  The close-up is a dense 13x8 maze: columns are the room positions along a floor, rows the floors from the basement
  loading bay (B, bottom left, where the cage starts) to the seventh floor. The arrow buttons, the arrow keys or a
  drag across the maze move the cage one cell at a time; walls stop it. Linen rooms (L) sit on the 7th floor by 701, the 5th floor by 503 and 511, the 6th floor
  by 607 and the 4th floor by 407 (directly above and below the right one), and the 5th floor by 507: only the
  last is right. The shortest way is 54 moves, winds through the whole hotel and passes many dead ends; the
  decoys next to the target are far away through the shafts. Dispatching anywhere else stays in the lobby and
  says where the cage would have stopped; Reset brings the cage back to the loading bay. Once solved, the lift works normally on return visits.
- After the bribe, Micah will not depart for the Blue Lantern until he has collected the brass box in
  room 507. Saves from before the five-location expansion (version 5 and earlier) are incompatible and do
  not load. The temporary Hotel map recovery applies only to an accepted current-version save that reached
  Act 2 without the card clues: it leads through the linen room, as below, and returning to the lobby then
  leads back to the Act 2 map.

#### Fifth-floor linen room at the hotel

- New location: the Aurelian's linen room on the fifth floor, where the routed staff lift lets out. Linen
  shelves, a laundry chute, a rack of maids' uniforms, a housekeeping cart and the corridor door to room 507.
- The corridor door is night-bolted from the far side. Look: "Night bolt on the far side. The transom's cracked
  open an inch - a hook could reach it." The lockpick is refused ("No keyhole on this side. The bolt's the only
  lock.") and a plain hanger slides off the bolt.
- **Puzzle 11 - Night bolt:** take a spare wire hanger from the laundry rack and the pliers from the
  housekeeping cart. Combine the hanger with the pliers in the inventory to bend a wire hook (the pliers go
  back on the cart). Use the wire hook on the corridor door: Micah draws the bolt through the transom and
  crosses to room 507. From then on the door stays open both ways.
- The staff lift goes back down to the lobby.

#### Eleanor's room at the hotel (room 507)

- New location: a luxurious but lived-in hotel room, ransacked, everything upside down.
- There is a locked desk drawer, which Micah opens using the lockpick from the inventory on it.
- Inside, there's a sheet of paper with the safe combination, written as three references instead of numbers:
  "Those who sat at His table. The days of the month He was born. The day He rested."
- **Puzzle 3 - Safe dial:** open the closet to reveal the safe. Hand or use the combination on the safe opens
  its graphical controls, not the safe itself. The references give **12** (the apostles), **31** (December) and
  **7** (the day of rest); the paper gives no directions, so the player has to try them. Each stop that is right,
  counting from the first, drops a tumbler, and a wrong attempt says how many fell, so the directions can be found
  by trying each one: the solution is **right 12 / left 31 / right 7**. The paper remains readable; wrong
  settings can be reset or retried. When the safe opens, Micah finds it strange that a woman like Eleanor would
  bring Christ into it ("Strange, a dame like her bringin' Christ into it.").
- Inside the safe there is a brass box. Micah opens it in the inventory with the hand, revealing:
  - a perfumed business card, blank except for two letters among the decorations. It carries Eleanor's own
    perfume (Micah can't know otherwise): "A business card, only two letters in it; the same perfume that
    permeates the whole room, only stronger... hypnotic, even." The line conveys an early attraction;
  - a matchbook with the name of the club, the Blue Lantern (next location). Micah connects it to the men the
    bellboy saw: fellas like that drink somewhere, and that's where her trail goes next;
  - a little vial of Mrs. Stewart's Bluing: somebody was meant to dye a white flower blue and follow her to the
    Blue Lantern (Micah can't know who; the First Interlude answers it). The florist's puzzle needs it, so the box
    has to be opened before the club's front can be passed;
  - a Japanese water flower (a pressed-paper pellet, a dime-store novelty), tied with red thread and wrapped in a
    scrap of hotel paper with Eleanor's hurried riddle: "Give me a drink and I'll tell you the word."
- Leaving the room goes back across the corridor to the linen room and the staff lift; in the lobby the
  revolving door now leads to the club's front.

#### Rizzo's Flowers, State Street (the Blue Lantern front)

- New location: a florist's on State Street in the rain, closed for the night. The Blue Lantern is behind its
  cold room. A regular waits by the cold-room door with a blue carnation in his buttonhole, and the
  chalkboard in the window reads "Members' buttonholes - blue carnations only".
- The cold-room door has a speaking grille: "A slot at eye height. Somebody inside checks lapels before they
  check faces." Knocking, or offering anything else, gets "No blue in my buttonhole, no hatch."; a white
  carnation gets a hint that the chalkboard said blue.
- **Puzzle 12 - Blue carnation:** take a white carnation from the bucket (a nickel in the tin) and combine it in
  the inventory with Eleanor's vial of Mrs. Stewart's Bluing from the brass box to dye the carnation blue (the
  vial is used up). The sidewalk shelf only holds pots and a watering can. Use the blue carnation on the grille: the hatch opens and Micah is let
  through the cold room into the speakeasy. Afterwards the door opens for him directly.
- **Puzzle 16 - Water flower (optional):** use Eleanor's water flower on the white carnations' bucket. It
  swells and opens into a pink paper flower with **MOONSHINE** written along the petals: the Blue Lantern's
  password (flag `knows_password`; the flower stays in the bucket). Used anywhere else, Micah notes that it wants
  water.
- The street exit on the left leads back to the Aurelian's lobby; the speakeasy's steel door leads back out here.

#### Club (the Blue Lantern speakeasy)

- Inside the cold-room entrance, Sal the guard still asks for the password; the blue carnation only got Micah
  past the florist's grille. Micah has two ways in: if the water flower gave him the password, "Moonshine." is
  the first choice and Sal lets him in for free; otherwise he admits he doesn't know it and can give him $10 as a
  bribe. Playthrough and film mode take the password; AutoPlay covers the bribe.
  Micah starts with $22, enough for the bellboy's two $1 payments and Sal's $10. The cash remains in his inventory:
  $21 after the bellboy's first dollar, $20 after the second and $10 after Sal (still $20 with the password). Repeated conversations never charge either bribe again.
  If he doesn't cooperate, or makes fun of Sal, he is thrown out and moves directly to the next scene.
- Until Sal lets him in, Micah can still try to walk past him to the bar: when he crosses the curtain line Sal
  steps in front of him and the password conversation starts. Talking to Sal directly starts it as well. If
  Micah leaves the conversation without paying, Sal walks him back to the door.
- Once past Sal, he can speak with Tony the bartender. Once Tony says the gin was made in a bathtub, Micah
  can order one: "Bathtub? Swell. The dirtier the hooch, the better I like it. Set 'em up, pal." It costs $1,
  is offered once, and Micah lifts the tumbler off the counter and knocks it back (new drinking sprite); the
  empty glass stays on the bar. Using the dollar on Tony orders it too. Tony won't budge, and when the conversation ends he
  calls Micah back: "You know what, I think I don't really like you at all", gestures to Sal (the bodyguard at
  the entrance), and on to the next scene.

#### Street behind the club (the alley)

- New location: the road behind the club, dirty and in the shadow, with only one intermittent street lamp.
- Micah is on his knees, hands on the pavement (new kneeling pose and sprite) after a beating, Sal next to him and
  Tony behind Sal.
- Tony tells him that Eleanor is "hot stuff", that he sent her to a convent of nuns, and that he doesn't know
  anything else.
- Before leaving, Micah pushes up from his knees and forearms through a supported crouch to standing.
- The player regains control in the alley and clicks the street exit to travel to the convent. A black caption,
  "The next evening", covers the jump: Micah sleeps off the beating and goes up the next evening (Saturday).

#### Convent

- Micah arrives outside the neo-gothic convent at dusk, in the rain (the sidewalk and road wet and shining under the
  lamps, rain falling with its sound), with Eleanor absent. He thinks the beating is a day old and comments on its pointed arches, iron
  spikes and saints in the windows. The player must click the convent door to enter the corridor.
- Inside are the convent corridor and Eleanor's cell, really dark, simple and tiny,
  with a bed, a lampstand, a book and a night stand.
- In the corridor, Sister Agatha interrogates Micah: what he's doing here and what he wants with Eleanor.
  She hints at Micah's biblical name as a prophet, quoting Douay-Rheims Micheas 6:8, and says "you would be better off finishing the
  search now, and never having anything to do with that Jezebel". Micah asks what she means; she retreats, telling
  him that if he really wants, he can have a look at her room.
- In the cell, the night stand has a drawer holding a comb and a little mirror.
- **Puzzle 4 - Waxed mirror:** take the mirror, whose wooden back is covered in wax. Inspecting it and the
  lamp explains that gentle warmth softens wax; searching the bed supplies a borrowed clean cloth.
  On the first search, Micah admits he ought to leave her bed alone but cannot quite turn away.
  After finding the cloth, he notices her perfume and realises he has lifted it to his nose without thinking.
  Use the mirror on the lamp, then combine the cloth and mirror in either order. Micah wipes away the wax,
  revealing a Celtic triquetra (trinity knot). He means to put the cloth back on the bed but can't bring himself
  to: "I oughta put this rag back on her bed, see... but, for some reason, I just can't." He keeps Eleanor's
  perfumed cloth until the end; only giving up on her (ending 1) makes him throw it away.
  The symbol is shown full screen with Micah's remark over it; a click ends the remark and the next click
  closes the picture. It can then be inspected again from the inventory.
- Micah keeps the revealed mirror; the comb stays in the drawer.
- If the player tries to leave the cell before revealing the symbol, Micah says "There is still something to be
  found in this room."
- Leaving the cell returns Micah to the corridor, near the cell door. Talking to Sister Agatha now starts
  her farewell: "What do you hope to find in all this, Detective?" Micah answers, "I don't know, sister, but
  I can't stop at this point." Afterward, the player can click the front door to leave.
- If the player clicks the front door without first talking to her, she calls, "Detective, before you go..."
  and starts the same exchange. That exit action continues outside once the conversation finishes.
  The farewell plays only once.

#### Road outside the convent

- When Micah gets out, the road is empty: no Eleanor. He walks to the middle of the road and lights a cigarette
  with his own lighter (new smoking strip: head bowed, both hands cupped round the flame against the wind, a gust
  first blows it out). He holds the lit cigarette while he thinks and, every 5 seconds while he talks, takes a drag
  (second strip: hand to mouth, the ember flares, a puff of smoke drifts off). The narration says he has
  hit a dead end.
- A choice of leads follows. Micah turns each of the first three down, and a refused lead is not offered again:
  - back to the Blue Lantern and the mob: they would kill him;
  - more questions for Harrington: Micah doesn't like the man and, for a reason he can't name, doesn't want to see
    him until the job's done, if he ever wants it done;
  - the cops: they're on somebody's payroll.
- The last lead is the office. Before he goes, Micah spots a motel sign down the road: "A flophouse... Maybe she
  took a powder from Sister Agatha and holed up there. It's a long shot, but I'm fresh out of angles." The street
  with the motel sign appears in a framed close-up for a couple of his lines, then goes. He drops the cigarette
  and the scene moves to the motel's back alley.
- Leaving the convent road after this, or reloading there, goes straight to the motel's back alley.

#### Behind the motel (back alley)

- New location: a back alley off the main road, in the rain, with the motel's side entrance under a buzzing sign,
  trash cans, a wooden crate, and an iron fire escape whose drop ladder is pulled up out of reach. A light burns
  in a first-floor window.
- Micah has to go in through the motel door first: the alley mouth only leads back to an empty road, and the fire
  escape is out of reach until he has a reason (and a way) to use it.

#### Motel lobby

- New location: a cheap, dirty lobby, a long way from the Aurelian: peeling paper, a bare bulb, a counter with a
  bell and a register, a key board, a sagging armchair, a roped-off staircase and an umbrella stand by the door.
- Micah asks the desk clerk whether he has seen Eleanor. The clerk doesn't answer, but he's visibly worried.
  A couple of questions show that the motel belongs to the mob without anyone saying so (friends who own the
  building, men who come by on Fridays, a clerk who doesn't want trouble with them). He won't let Micah upstairs.
- **Puzzle 19 - Fire escape:** take the crook-handled umbrella from the stand; the clerk lets him take it,
  just to see him gone. In the alley, push the crate under the fire escape, then use the umbrella on the drop
  ladder: standing on the crate, Micah hooks the bottom rung and pulls the ladder down. Without the crate the
  umbrella is too short; without the umbrella the crate alone doesn't reach. The umbrella stays hooked on the
  ladder. Climbing the ladder leads to the first-floor landing.

#### Motel fire escape (first floor)

- New location: the iron landing on the first floor, sooty masonry behind it, iron grating, windows and a door
  into the floor, rain.
- Eleanor is there, outside, dressed in black.
- She opens: "Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?"
  Micah asks about Eleanor Harrington, introduces himself, and the conversation joins the existing exchange.
- She asks why he's trying to find her and Micah explains; the conversation has tension and attraction.
- While they talk, a framed close-up shows them side by side, Micah on the left and Eleanor on the right, in the
  same VGA style as the other close-ups. It appears immediately after Eleanor's opening line; each active
  speaker's dialogue is shown below their own portrait half.
- The panel disappears completely just before the player answers "And what do you get, if you bring me home?"
  The compensation choices and the remaining conversation take place on the landing with normal overhead speech.
- The scene ends when Eleanor says "I can't go back there..."

#### Motel room, night

- Inside her room at the same motel, Micah is getting dressed (new dressing sprite for the character) while Eleanor is in the
  bed, under the sheet.
- They say this was probably a mistake and that they should never see each other again. Micah says he won't
  tell anyone where they can find her, and that he will give up the job.
- Eleanor remains in bed against the pillows, covered by the white sheet. She does not rise.
  The scene then fades back to the attic.

### End of Act 1 - Present day

- Back in the attic, but it's dark and the lamp is on. Leo calls Daniel downstairs for dinner.
- Micah's 1927 inventory is put aside during the present-day scenes. When the journal picks up again, each act
  starts with a reset satchel: the notepad and lighter plus only what the rest of that act needs.
  - Act 2: revolver, lockpick, the brass box's card, the mirror, Eleanor's cloth, and Faith's ring and cross if he
    has them. The photo, the cash and the matchbook stay behind; the notepad holds what they said.
  - Act 3: the revolver, Eleanor's cloth, and Faith's ring and cross if he has them (the endings weigh them).

### Micah's journal narration

- In every 1927 scene (all acts), Micah's inner thoughts are a narrating voice taken from his journal: lines in
  faded sepia ink along the top of the screen, while Micah himself stays silent. They advance like speech (or on a
  click).
- They are written in the first person and present tense, as journal prose about the scene as it happens:
  "Another night, another bottle. And a client in my chair, too well dressed for this floor."
- Each scene opens with a short thought on Micah's first arrival, and key moments (after major conversations,
  discoveries, departures) add one. Wherever this walkthrough says Micah *thinks* something, it is narration.
- Replies to looking at or handling things, and anything said to another character, remain spoken.

### Micah's notepad

- Micah always carries a notepad, the first item in his satchel, and his lighter, the second (Daniel has
  neither). The lighter is the flame for every fire in the story. The notepad can be read full
  screen at any time with **N** or look/hand in the satchel, one page per note, paged back and forth.
- Notes are written as the story advances, from Teddy's briefing to the Harrington audit, including the
  triquetra sketched from behind the mirror.
- Where only the information matters, the notepad can be shown instead of the item: Eleanor's photo (to anyone
  asked about her), the mirror (to the librarian), the combination (to the safe), the crests (to the closet
  panel) and the mended clipping (to the morgue's wall map).

## Act 2

### Present Day

- The next day, Daniel is back in the attic and returns to reading the journal (hand on it in the satchel).
  The black captions "Chicago, 1927." and "First Interlude" lead to the First Interlude; after it, the story
  picks up in Micah's office.

### First Interlude - Eleanor

The player moves **Eleanor** (new playable sheet, black dress). The narration is Micah's journal voice, in the
third person: he is writing down what she told him during the night at the motel ("She told me she sat by that
window..."). Eleanor speaks aloud only to people and on look/hand. She carries her own satchel, empty when she
starts: she can take, join and use only what she finds in the room she is in. **N** does nothing while she plays;
Micah's things are stashed and come back when the interlude ends, and none of hers go with him.

1. **Room 507, the Aurelian, the Tuesday night.** The room is still in order (its own tidy background,
   `eleanor_room_interlude.png`): Theodore's men only turn it over after she has gone. The bench under the red
   dress is a separate object (`eleanor_room_interlude_bench.png`) and a hole in the walk area: Eleanor walks
   round it, and reaches the dress from in front of it. She packs the brass box
   (**Puzzle 17**, below), puts the combination in the
   drawer, and phones Rizzo's Flowers from the bedside (the answers are colour). At the door, Sal and a second hood take her down
   the service stairs, told over black: the bellboy's memory, from her side.
   The box is a dead man's switch, not an invitation: if the Club ever drags her back, the Club goes into the
   morning paper. The card hides the Club's address; the matchbook, the bluing and the password get a reporter
   past the florist's grille and Sal to Tony, the one man who will talk. She leaves it in the room, not on her:
   the room is in her name, the hotel keeps a guest's things, a hotel safe can't be forced quietly, and if they
   catch her they search her first. The riddles keep Theodore's men out; somebody sent there on purpose, with a
   whole night, gets in.
2. **The Blue Lantern.** Colour only. Tony questions her; her answers are colour. He owes the sisters for the
   sacramental wine and sends her to the convent. Before Sal drives her, she asks Tony to hold the switch: if the
   Club gets her back, he calls the Tribune city desk (not the cops: half of them drink at his bar) and says
   "Room 507, the Aurelian. The drawer, then the safe." He agrees: it is leverage on the old man. Micah's
   narration adds that she didn't know, telling him at the motel, that he had already emptied the safe (the
   Tribune morgue shows the call was made). Sal stays out of her way: the doorman's interception is off.
3. **Convent corridor, arrival.** Sister Agatha (the Mother Superior) calls her "another Jezebel from that
   hideous Club". Eleanor's replies (the Club, the old man, what she wants) are remembered for the night.
4. **Convent cell, that night.** After a knock, Agatha comes into the cell and talks round and round, trying to make Eleanor admit
   that she wants something impure from her, while it is the other way around. She walks out again before the
   morning. The choice is saved:
   - **Refuse**: Agatha leaves, offended (`eleanor_refused_abbess`).
   - **Indulge**: at the last moment Agatha turns back, cursing Eleanor for a demon. Nothing is shown.
   The Club's strings replace the convent piano from the knock until Agatha walks out.
   Eleanor leaves the convent the next morning.

- **Puzzle 17 - The brass box:** she builds the insurance Micah finds later, and locks it away herself. Her lines
  name its reader as whoever the paper sends, never Micah.
  - Hand on the vanity: the open brass box (the card, the matchbook, the bluing already in it) and the bare paper
    water flower, the word inked inside.
  - Hand on the writing desk: she tears a scrap of hotel paper and writes "Give me a drink and I'll tell you the
    word."
  - Look on the clothes shows a torn red hem; hand pulls a length of red thread from it.
  - Join the scrap and the flower, with the thread in the satchel: the wrapped water flower (all three used up).
    Without the thread, it won't stay wrapped.
  - Join the flower and the box, then use the packed box on the closet: it goes in the safe, locked.
  - Wrong joins and wrong items on the closet get a hint in her voice. The drawer waits for the safe, the call
    for the drawer, and the door for all three; at the door she names the first step still to do.
5. **The motel room.** She takes a room in sight of the convent (the motel with an empty bed and a bare chair) and watches from the
   window for four days. On the fourth evening she sees Micah, a day after his beating, arrive at the convent door, come out again and light a cigarette in the road, then
   hears him arguing with the clerk downstairs; she steps out onto the fire escape to wait for him, where he
   finds her. Fade to black, then Micah's office.

### Chicago, 1927

#### Office, before the cathedral

- A bottle of whiskey and a cup are in the office. Micah raises the cup, drinks, and puts it down.
- Micah chooses whether to take his wedding ring or leave it in the office; the original decision is saved.
- A left-behind ring remains visible and can be collected on a later office visit without changing the original decision.
- After the choice, Micah leaves for the cathedral steps.

#### Outside of the church (cathedral steps)

- Existing location.
- Micah thinks that, even though he couldn't turn her in, he can't think of anything else but her.
- After this thought, he walks up to the doors and enters the church.

#### Inside the church

- Existing location.
- Micah walks over to his brother, Father Caleb, and talks about the situation. During the conversation he tells
  his brother that, right now, he's too far off to be saved.
- Caleb replies that this is crap, no one is beyond salvation, and that thinking that is the Devil's work.
  His original counsel remains: "Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace."
- Micah admits he tried praying, but he no longer remembers the Our Father: "Our Father, who art in heaven, hallowed
  be Thy name... and then nothing. I can't get past it." Caleb answers: "Then start there. He remembers the rest."
- Micah replies "I'll think about that", then says that coming here was a mistake, and walks out. The scene moves
  to the map.

#### Map of Chicago

- New location: an old map of Chicago (no year printed on it). Micah isn't drawn on the map.
- On the first visit, Micah says "I have to find her again".
- Three locations are available: the Library, the Church (cathedral) and his Office.
- Hovering over a location shows its description in a parchment caption strip along the bottom of the map.
  Clicking a location travels there, or Micah says why he won't go.
- Selecting the Church: Micah refuses to go back ("Coming there was a mistake once already").

#### Library

- The library visit happens during the day. There is a librarian (new male character); Rose works at the library,
  but it is not her shift, and the librarian never mentions her.
- On arrival Micah is openly relieved that Rose isn't on duty, but it is made clear that seeing her empty desk has
  brought her back to his mind; this is part of the reason he later goes to her house.
- Micah asks him about the strange symbol; it is shown full screen during the conversation, then the scene
  returns to both Micah and the librarian.
- The librarian asks him where he got that mirror. Micah won't tell him, so the librarian answers that he won't
  tell him anything either.
- **Puzzle 5 - Restricted catalogue:** after the refusal, inspect the desk catalogue. Compare the mirror's
  connected triquetra with the motif plates: select Celtic traditions, whose index lists **A. R. Bell**.
  The author listings identify **Rites of the Old Isles, shelf C-17**. Select that entry.
  The volume is behind locked glass; Micah cannot simply take it from the shelves or ladder.
- Micah has to threaten the librarian with the revolver (use the revolver on him; before asking about the symbol
  Micah refuses to do it, and before the lookup he needs a precise title). Micah aims the revolver at him while
  he requests the identified book. The librarian confirms that it describes ancient Celtic rituals and gives it
  to him if he goes away. Micah stays in the library; the shaken librarian won't say another word, and the
  player leaves through the exit to the map.
- After leaving, the library isn't accessible anymore: selecting it on the map, Micah says "Better not show my face
  there for the time being".
- Leaving the library normally returns to the map.

#### Office

- Leaving the office returns to the map.
- **Puzzle 6 - Concealed calling card:** read the book at the office for instructions about gentle heat,
  reflected writing and ornament order: **lily, leaf, feather**. Use the hotel calling card on the radiator,
  then combine it with the revealed convent mirror in either order.
  The reflection reveals three labelled fragments: feather = "Hubbard", lily = "The Club", leaf = "18 W.".
  Arrange them using the book's ornament order in the close-up to obtain the existing address slip.
  Heating, reflection and book-reading can happen in different orders; the last prerequisite offers the
  deciphering panel. The complete address and map destination appear only when the order is correct.
  The book, card and mirror remain available. Reading the book outside the office still receives a refusal.
- A new location is now available on the map: the club (the Starlight).

#### Club (remove Starlight, the location will be called only Club)

- Micah will access the first door to find the Master of Ceremonies (another character, dressed in Freemason ritualistic dress).
- Micah will talk to the Master of Ceremonies asking whether he knows about the naturalistic rituals of the book;
  The Master of Ceremonies (MoC from now on) will not comment on those, and ask instead why Micah is asking about this.
  The conversation goes on and Micah keeps asking, but the MoC will say that he knows why he's asking, and it's because
  of Eleanor.
  Micah will get near the MoC and ask whether he knows where she is, the MoC will say "Of course! Thanks to your 
  efforts, she is already with us, safe, and where she belongs!"
  How his efforts led them to her remains uncertain; the MoC does not confirm a tail.
  Then the MoC will call a brute (another character, in normal dress, tie and jacket) and ask to escort Micah out.

#### Streets of Chicago

- Micah is on the pavement, supine. Narrating voice, which is really Micah's thought, will ask himself what is he doing,
  questions about his life, why he abandoned his wife and son. He recalls Rose's empty desk at the library: he was
  glad she wasn't there, yet she hasn't left his mind since.
- His recovery is shown through sitting, a supported crouch, and standing rather than an instantaneous pose swap.
  The player is then presented with two choices:
  - Go find his wife.
  - Push forward.
- If Micah go find his wife, there will be another location, outside of a terrace house in a row of terrace.
- Otherwise, skip the next part.

#### Outside Micah's wife house

- Micah is outside the house. The player can choose whether to get out of the location, or ring the bell.
- Leaving before ringing must be an active choice: using the exit opens a dialogue choice between
  "(Walk away without a word.)" and "(Not yet.)". "(Not yet.)" keeps Micah at the door. Walking away has the same
  outcome as leaving without insisting three times (no callback, the bell is closed to him), except that Micah never
  sees Rose and she never replies: Micah has a short closing thought and the scene returns to the map.
- If the player let Micah ring the bell, a door will open and Micah's wife will get out.
- Dialog is tense: the wife asks why he's here, he has no business being here.
- Simulate a dialog where the player has two options: keep pushing for forgiveness, or just leave: keep pushing means that
  the dialog will go on, but the option to leave will be always present.
- There will have to be 5 phrases in which Micah will push the wife for her forgiveness, after which only the leave
  phrase will be available.
- If the player decides to keep pushing at least three times, before going out of the location, the wife will call him
  back with a "Wait!": Micah will turn, then the wife will say "Don't get into trouble again."
  After "Wait!" (not during it) a framed close-up panel of Rose at her door pops up over the scene, in the same style as
  Eleanor's stage close-up; after a couple of seconds of silence, "Don't get into trouble again." appears along the
  panel's bottom edge, then the panel is removed and the scene continues.
- Rose makes clear that forgiveness is not something Micah can demand; the callback is concern, not absolution.
  Keep her third-appeal reply: "Forgiving is easy, Micah. Forgetting is the part you keep asking for."
- If Micah leaves without insisting at least three times, Rose answers: "You're running away again. It was always
  too hard for you... too hard on you. Don't bother ringing this bell again, Micah Jones." She then shuts the door
  on him straight away, not harshly but decisively; Micah thinks: "The door shut. Not hard. Just once, and for good."
- Then, the wife will close the door, and Micah will go out.

#### Map of Chicago

- Now, also the Club will not be a selectable location, Micah will say "No use returning there now."
- Simulate the other locations, but no use going there, apart from the Convent.

#### Church

- On repeat visits, Caleb offers Micah a cross pendant if he originally left the wedding ring in the office.
  If he originally took the ring, Caleb does not offer the cross until Act 3. Later ring pickup does not change this timing.
- Micah can accept or refuse; acceptance is saved and gives him the pendant. Caleb offers it again on every eligible
  return after refusal, but never during the first confession or after acceptance.
- Micah will have to ask his brother about the Club. The brother will be reluctant, and Micah will have to press.
  Micah does not suspect Caleb of being involved. He reasons his way to him: Eleanor already found refuge at the
  convent, and maybe not for the first time; the convent belongs to the Church, even though Mother Superior runs it
  and Caleb runs the parish; so Caleb might know something. Both reasons must be offered before the choice
  "They have her, Caleb. If you know anything, tell me." Micah does not claim Caleb hid her
  in his sacristy; the established refuge is the convent.
- Micah's brother will tell him that the Convent is probably the best way to ask. He will advise Micah not to go there,
  to give up this foolish search.
  Micah will answer "There's little left for me to do, at this point."
  The brother will say "You know that that's not the case."
  Caleb teaches that repentance is for anyone, at any time in their life, and that the Lord forgives whoever truly
  repents. When Micah insists he is too far gone, Caleb rebukes him harshly: thinking himself beyond salvation is
  pride, arrogant and self-serving. He closes with the prodigal son.
  Micah will say nothing and get out.

#### Map of Chicago

- The convent will appear as the next location.

#### Convent

- Micah will interrogate the sister about the club and Eleanor. She will say she knows nothing, Micah will have to
  use the revolver again to threaten her.
  The sister will say "Are you crazy, sir?!"
  Micah: "Yes, at this point, you can say so, sister. Where's Eleanor? What's with the club?"
  Sister: "You are of the same lot as that Jezebel. At this point, I'll let you burn in the flames of hell.
  She's a performer, you know. Almost caught me off guard, the whore. You might want to Harringhton senior.:
- The conversation ends with Micah not saying anything, putting away the revolver, and getting out.
  On the way out Micah thinks: "Harrington senior keeps his name off doors. The Tribune morgue keeps everybody's
  name - I'd start there."
- At this point, also the Convent won't be available as a location.

#### Map of Chicago

- The Cathedral and the Tribune (the newspaper morgue) are available; Harrington father's office is not on the map
  yet - Micah doesn't know where it is. Micah's office also remains accessible as an optional
  return and ring-pickup location; no completed lead reopens.

#### Tribune morgue

- The Chicago Tribune's archive in the basement: rows of steel filing cabinets, a copy spike and wastebasket, a
  layout desk with a paste pot, and a wall map of the Loop studded with pins. No NPC.
- **Puzzle 13 - The torn clipping:**
  - Drawer H of the filing cabinets holds the top half of a clipping, "HARRINGTON BUILDS...", torn straight
    through the address.
  - The copy spike (with the wastebasket) holds the bottom half ("...Building, LaS").
  - Combining the two halves without paste is refused: "Torn straight through the address. I'd need something
    to hold them together." Take the paste pot from the layout desk, then combine the halves into the mended
    clipping (the paste is kept; it goes back on the desk when Micah leaves, or by using it on the desk).
  - Look at the wall map: "Map of the Loop, pins for every address the paper ever printed." As soon as the
    halves are mended, Micah walks to the wall map and pins the clipping on it himself: the Harrington Building,
    LaSalle Street (flag `harrington_located`). Using a mended clipping on the map (an older save) does the same.
- Under the bottom half on the spike is the city desk's spiked tip slip: an anonymous caller, a man with bar
  noise on the line, "Room 507, the Aurelian - the drawer, then the safe"; the boy sent round found the room
  tossed and the safe open and empty. Micah knows from the motel night what it means: Tony made Eleanor's call
  once the Club had her back, and her insurance paid out on the safe Micah had already emptied. Look on the spike
  afterwards recalls the slip. Taking the bottom half shows it; there is no extra flag, item or step.
- The door leads back to the map.

#### Map of Chicago

- The Tribune disappears and Harrington father's office appears.
- Caleb's warning retains "Repentance means more than asking nicely. Put the gun away." without an added
  exact Scripture quotation. Before the masked Club visit, keep "God doesn't turn away a contrite heart, Micah.
  You don't have to be whole to turn to Him."
- The only way forward will be the office of Harringhton, but Micah can go to the church, where the brother can
  tell him not to go forward again.
  You have to save as a state of the game whether, at this point, Micah will return to the church at least once.

#### Office of Harringhton father

- Two new locations, office of Harringhton father and the road below, at night.
- **Road behind the Harrington Building, at night**: a watchman guards the back door and the alley; a trash can,
  a pile of wooden crates and a fire escape whose ladder is pulled up, leading to Harrington's dark office window.
  - While the watchman is there, touching the crates or the fire escape gets Micah spotted: the watchman
    shoos him back down the alley, and the back door is locked anyway. Threatening him with the revolver or kicking him is refused.
  - Step 1: use the lighter on the trash can. It catches fire, the watchman shouts "Fire!" and
    goes inside to phone the fire department, leaving the alley unwatched.
  - Step 2: use the hand on the crates to stack two of them under the fire escape.
  - **Puzzle 7 - Ladder catch:** after the distraction, take the tapered packing wedge visible among the
    crates. Stack the crates to reach the jammed ladder catch, whose illustration shows the obstruction.
    Use the wedge on the catch, then climb the fire escape (hand on it, or on the window).
    Both stacked crates and a freed catch are necessary; the wedge stays installed and the guard never
    returns on a gameplay timer.
- Once in the office, the player will have to search for clues, and it will have to open at least two drawers and a
  closet. The drawer will be locked, and Micah will have to use his lockpick to access to it.
- In the drawer, he will find an invitation card to the Club.
- **Puzzle 8 - Disguise compartment:** the invitation shows an ordered procession of crests:
  raven, lion, stag. The portrait's heraldic key associates raven with star, lion with sun and stag with moon:
  looking at the portrait opens a close-up of the heraldry band painted along its foot. The lock itself gives no
  hints; its clue box only reads "Three dials. Three symbols."
  Open the closet and inspect its false-back panel. Set the three graphical wheels to
  **STAR / SUN / MOON** and submit. Neither a hand nor lockpicks bypasses the lock.
  The double doors reveal the original white mask (a Venetian Bauta) and cloak.

#### Map of Chicago

- The office of Harringhton father will disappear, and the Club will reappear. The Church will be still available,
  and you'll have to save to the state of the game whether the player will decide to go to the Church and talk
  with Micah's brother once more.
- Choosing the Club puts Micah, masked, in the Club vestibule; there is no going back to the map from there. The
  back door on the street is refused too ("Through the front tonight, with the procession.").

#### Club vestibule

- A small entry hall: a brass plaque, a coat-check counter, a rack with three hooded cloaks and a locked inner
  door with a brass card slot. The street door won't let Micah back out.
- **Puzzle 14 - The sealed summons:**
  - The plaque reads: "Present your summons, sealed by the first of the procession."
  - Take the stick of sealing wax from the coat-check counter. Cold wax on the invitation is refused ("Hard as a
    church pew. Needs a flame.").
  - Combine the lighter with the sealing wax: soft wax (the lighter is never consumed). Combine the soft wax
    with the invitation: the waxed invitation.
  - Each cloak on the rack (lion, stag, raven) has a signet ring in its pocket; Micah only holds one at a time,
    taking another hangs the previous one back up. The invitation's procession is raven, lion, stag, so the
    raven is first: lion or stag on the wax is refused.
  - Combine the raven signet with the waxed invitation: the sealed invitation (the ring goes back in its cloak).
  - Use the sealed invitation on the door slot (a plain or waxed-but-unsealed invitation is refused): the door
    opens (flag `vestibule_passed`) and Micah walks into the Club hall. The sealed card is returned to him and is
    what the master of ceremonies wants to see inside.

#### Club

- When Micah's enters the Club, he will be dressed with a white mask and a cloak. The mask is a Venetian Bauta half-mask: ivory, heavy brow, eye holes and a long nose; the mouth and chin are bare, overshadowed by the mask and the cowl. You will have to generate this 
  new dress and sprite.
- The club will be filled with a number of masked men, all in the same black cloak and cowl: some with the same white mask
  as Micah, others with carved animal masks inspired by Celtic folklore (bear, raven, hare),
  and women dressed with a black mask and succint dresses (even here, you can use the smae model and sprite multiple times).
- When Micah will reach the stage, he will find Eleanor, with the same succint dress but without the black mask, at the 
  center of the stage, with three masked men around her: the leader in a horned stag mask (Cernunnos), one in a boar
  mask and one in a wolf mask.
- After Micah's first line on the stage ("The seats were full..."), a framed close-up panel pops up over the scene:
  Eleanor's face in the spotlight, zoomed and clearly defined, with hooded masked men (the stag among them) behind
  her. The stage stays visible around the panel, which stays up until the fade to black (bare shoulders, or a dark
  red dress when nudity is off).
- Eleanor's face in the close-up is emotionless. Micah notices there is nothing in her face, not fear, not shame,
  like a wound-up doll.

### End of Act 2 - Present day, the attic

- Dark again, the father is called for dinner.

### Act 3 - Present day, bedroom

- Father in the bedroom (new location) reading with the nightstand lamp on, wife covered by the blankets, light off on her side.
- Father keeps reading, then frowns: "These pages read differently. Not sure that's Micah's hand." Every ending's
  last entry answers him (see *Present*). The black captions "Chicago, 1927." and "Second Interlude" follow.

### Second Interlude - Eleanor

The player moves Eleanor again. The narration is a neutral third voice. Same rules as the First Interlude: her own
satchel for what she finds there, no **N**, Micah's things stashed until the interlude ends.

1. **The motel room, after Micah has gone.** Colour only. A knock at the door. Eleanor goes to it but stops
   halfway; the door is kicked in, and Bruno and a second goon (new sprite) walk in and stand between her and it.
   They followed "your detective" there. Her answers are colour; they walk her out through the broken door, over
   black.
2. **The Club, backstage (new room).** A dressing room with a lit mirror, in the Club's style. Eleanor wears a
   short pink gown (new playable sheet). She is alone: she puts her face on at the mirror (**Puzzle 18**, below)
   while the gin table waits. When the face is done, the stage door opens; Eleanor whispers "A foul odour of death
   and ashes. He's here.", and the old man, robed, unmasked, the stag mask in his hand, walks in and the door
   closes behind him. He talks her into gin and powder, "as always". The choice is saved:
   - **Take it**: she drinks and takes the powder (new sprite).
   - **Refuse** (`eleanor_refused_drugs`): he forces her anyway. Nothing is shown: the screen goes black and
     "Noooo!" appears over black.
   Fade to black, then the Club stage, as before.

- **Puzzle 18 - The face they paid for:** the doll's face Micah sees on stage, put on by hand. Every step is a beat
  of her conflict, and it is sad: the silk, the money and the safety she has against the rot under them and the
  wish to run, with the old man's gentle, possessive pressure to stay.
  - Hand on the mirror: her compact of face powder (no puff) and a lipstick.
  - Hand on the costume rail: a swansdown puff in a member's wife's gown pocket.
  - Hand on the painted screens: a hairpin clipped to the silk.
  - Join the puff and the compact, then use them on the mirror, in order: the face powder, the lipstick, the
    hairpin. Out of order, she says so ("Powder first. Then the mouth. Then the hair."). Look on the mirror
    repeats the order. Nothing is taken from the gin table.
  - The finished face lands on the sad note; then the old man comes in by the door, "Sit down, my dear. We have a
    few minutes", and the choice above.

#### Club

- Same scene as the end of Act 2, with the close-up panel of Eleanor framed over the stage again.
- The stag-masked leader turns to Micah, dreesed as himsel "Are you satisfied, now, mister Jones?"
- At this point, everyone turns to him.
- The close-up panel is removed. Before anything else happens, the stag takes his mask off and pushes back his cowl
  in front of everyone: he is Harrington senior, the old man whose portrait Micah saw in the LaSalle Street office
  (new sprite: bald, white-haired, the stag mask held against his chest). Nobody in the room is surprised.
- Harrington explains himself: the bonfires, the antlers and the old gods are theatre. The whole meeting exists only
  so that he can exercise his power and make it manifest; a hundred men who run the city will not lift a finger
  unless he allows it, and they come back every Thursday to bow.
- Harrington, unmasked, continues: "You brought Eleanor back to us. For that, the intrusion is forgiven. This is as
  far as you go."
- Then the player has three choices in dialogue:
  - Use the revolver, but this will end with another man coming from behind and knocking him out.
  - Do nothing, and the same man from behind will knock him out nonetheless.
  - "Our Father...": Micah gets as far as "hallowed be Thy name" before Harrington cuts him off ("How childish...
    This is ruining the mood.") and signals the man behind him, who knocks him out.
  - The man from behind is Bruno, the brute who escorted Micah out of the Club earlier.
- Eleanor only speaks robotically here: flat, formal, repeated phrases ("I am where I belong, Mr. Jones." / "Thank
  you for bringing me back."), never calling him Micah.
- Micah's masked, cloaked collapse is shown before the blackout on either choice.

#### Church, outside

- Micah is supine on the pavement, again, beaten.
- A framed close-up panel of Micah's face pops up over the scene, like Eleanor's on the stage: flat on his back on the
  stones, looking up from under his hat. It stays while he thinks, and closes before he gets up.
- Before recovering, he admits: "I keep calling it saving her. But it's her I want. Her voice. Her skin.
  Another night like that one." Then: "Rose and Tommy ought to be in my heart. Eleanor's there instead.
  And God help me, I don't want to let her go." His motive is lust, conflicting with repentance and returning home.
- He sits up and pushes himself to standing before the choice, with the same staged recovery as the street.
- Again, his thoughts will appear as narrating voice, saying what is he doing.
- At this point, the player can have two choices: keep going for Eleanor, or giving up.
- If the player decides to give up, the next location will be again in front of his wife's house, where he will ask her
  whether she would be available some time for a cup of coffe, his ex wife answering why not, and the game jumps
  to the end of act 3 (caption "End of Act Three").
- If the player decide to keep pushing, keep to the next.

#### Office

- The player returns to the office. The banker's lamp is off for the whole of Act 3 and the whiskey bottle and cup have
  moved to the desk; Micah stands at the window, his back to the room, under the HOTEL sign; narrating voice which
  describes his thoughts.
- After the opening line, he reflects: "Thanks to my efforts, he said. How'd they find her through me?
  Somebody on my heels? Something I let slip?" Then: "Aw, what's the difference? They've got her just the same."
  Neither a tail nor a betrayal is established as fact.
- He's thinking what could do next, where could Eleanor be; he concludes that the only person who could help are at the
  Blue Lantern, the mob.
- Micah stands up and the player regains control, with a final opportunity to collect a left-behind wedding ring.
- Keep the original dismissal: "The convent's done with me. Caleb would sooner pray than talk.
  The cops are on somebody's payroll."
- Keep the reminder: "Before I go: my wedding ring, and Caleb's door. Last chances to remember who I'm supposed
  to be coming home to."
- Leaving the office offers a choice: visit Caleb or continue to the Blue Lantern.
- Act 3 church visits include Caleb's counsel and the cross offer (regardless of the original ring decision), unless
  already accepted. They count as a church return and lead back to the office without replaying the desk scene.
  Micah can return again after refusing. No new recovery route is available after choosing the Blue Lantern.

#### Behind Blue Lantern, previous location from Act 1

- The existing alley sequence has three steps: break the lamp, kick the trash cans in the dark to lure
  Sal out, then use the revolver on him to knock him down. Hit from behind, Sal drops to his knees and then falls
  face-down. Only then knock on the back door to face Tony.
  Trying the noise while the lamp is lit or knocking while Sal is inside cannot bypass the sequence.
- Once the bartender is out, Micah automatically starts the dialogue with the revolver out, asking how to get to
  Eleanor.
- The bartender tells him to bug off, these people are really dangerous, and he'd be better off with a bullet in his skull.
- At this point, the player must choose between firing the revolver into his shoulder, or walking away, because it's not worth it.
  The option to walk away is available only if Micah carries his wedding ring and returned to Caleb before Harrington's
  office, before the masked Club visit, or through the Act 3 office route. The cross is not required here.
- If the player walks out, he's going to his wife's house (caption *End of Act Three*).
- If he fires, Tony is hit in the shoulder: he clutches it, his legs fold straight down under him and he ends up on
  his back, with the blood on his shoulder and pooling on the ground under it.
- The bartender screams, and he tell him to go directly to the house of Harrington father, he explains how to get inside
  from the kitchen, because they provide them with booze.
- Micah get out of the scene.

#### Outside of the Harrington mansion, behind the kitchen

- Tony's key-on-the-lintel shortcut is wired to an alarm. Inspect the door or reach for the key to notice
  the taut wire; move the coal bin under the bell to reach its hammer.
- **Puzzle 9 - Alarm restraint:** the graphical close-up shows a spring-loaded hammer restrained by
  the door wire. Cutting the wire releases it. Plan **hold hammer, tie hammer, release hand**, using
  Micah's tie to secure the hammer to its bracket, clear of the gong. "Cut wire" is a tempting wrong
  option. Incorrect plans are rejected before touching the mechanism; no alarm sounds and retries
  cost nothing. Close/reset preserves the unrestrained state. Use the lintel key only after securing it.
  The tie stays on the bell: from here on (the mansion and every ending after it) Micah goes without it, collar
  open at the throat (`micah_no_tie` sheet and its crouch/aim strips; the mask still takes precedence).
- The kitchen is dark and quiet. The green baize door to the house is **bolted from the house side**: Micah
  says so and notes that houses like this always kept another way up for the deliveries. In the floor by
  the table is a cellar trapdoor with an iron ring.
- **Puzzle 15 - The wine cellar:** the trapdoor leads down into the Harrington wine cellar, pitch black.
  Micah can make out a storm lantern on a hook and some delivery crates; the stair at the back can't be
  climbed blind. Take the lantern (empty) and look at/take from the crates: one sloshes, a can of
  kerosene. Combine **lantern + kerosene** (filled lantern), then **filled lantern + lighter** (lit
  lantern; the lighter is kept). Trying the lighter on the empty lantern gets "Dry wick. Needs fuel
  first." Use the lit lantern on the stair (or on the darkness): Micah hangs it on a nail, the cellar
  lights up, and behind the wine racks a bootleggers' service stair climbs to a panel behind the old
  man's study bar. It brings Micah into the study through the drinks cabinet. Going back through the
  study's kitchen door slides the baize bolt, so afterwards the baize door works both ways. The cellar is
  required for every entry into the mansion; the lantern isn't needed afterwards.
- Harrington's study has a closet and a desk with two drawers. The bedroom door is always accessible:
  Micah can pass straight through without collecting evidence.
- **Puzzle 10 - Auditor's index (optional):** the right drawer contains a numbered account register,
  not the signed evidence. The left drawer supplies a transparent index with the same Harrington Steel
  stamp. Combine them in either order, or use the index on the register in the open drawer, at the study
  desk. Match all three labelled BANK/JUDGE/CAPTAIN marks by rotating and sliding the index. Its note
  puts BANK above JUDGE and CAPTAIN left of BANK; the asymmetric grid has one solution: one clockwise
  turn, offset **(6, 3)**. The aligned window identifies the drawer pocket containing signed payoff
  sheets, which Micah takes as the existing documents item. Cancellation keeps both clues.
  Taking the register alone does not count as evidence. This opportunity ends on entering the bedroom,
  as before: neither inventory combination during escape nor returning through the kitchen bypasses it.
  Skipping the puzzle must retain the prison endings when the mansion does not burn.
- Next area is Harrington father's bedroom: huge bedroom with king size bed, Elearon under the sheet naked, Harrington
  father in his dressing gown. He's talking with Eleanor, telling her that it's not too bad to have returned where she
  belongs.
- Harrington refers to her established refuge: "You ran to the nuns", not a priest.
- After the dialogue, Micah, who previusly hid behind something, shows up with his revolver pointed at the old man; the
  old man turns to Micah, Eleanor get out of bed covering herself with the sheets (you have to generate this character also).
- The old man tells Micah that he doesn't have the guts to do that, and that Eleanor's place is here, she's just a whore.
- The player has two choices: either shoots the old man or not:
  - If he shoot the man with the revolver, the man is supine with blood on his stomach (you have to generate it, and the
    sprite of the man shot falling), and Micah has to convince Eleanor to follow him (generate dialogue):
    - **Exception (endings 10 and 11).** If Eleanor refused both the Mother Superior and the old man's gin and
      powder in the interludes, there is no persuasion. Worn out, emptied by too much at once, she only says
      "Let's get out of here, quick." (`eleanor_weary`) and follows Micah, as if he had convinced her: no lowering
      the gun, no leaving her, no shooting her. The kitchen escape runs as on the convinced route (the fire, the
      documents), and Micah keeps the revolver. The fire or the documents give ending 10, neither gives ending 11.
    - Eleanor always gets four turns, each with three lines for Micah. Only one line per turn is right, and only
      the four right lines in a row convince her. A wrong line silently breaks the chain: the conversation goes on,
      but she slips away (Micah's thoughts hint at it), and a right line after a wrong one no longer reaches her.
      The only way to convince her:
      1. "Then we don't stay in this city. We're out of it tonight."
      2. "He'll take you back like he always does. And lend you out again on Thursdays."
      3. "You don't have to know tonight. You only have to walk through that door."
      4. "Nothing. Come or stay, it's yours to decide. But decide it yourself, for once."
    - The wrong lines: "I didn't come all this way to leave you here, Eleanor." / "You can't stay here. Not now.
      They'll pin it on you." (turn 1); "Forget Theodore. You've got me now." / "Theodore's a coward. I'll handle
      him." (turn 2); "You'll be with me. I'll look after you." / "You can be anything you like. A singer. A nurse.
      Anything." (turn 3); "I love you, Eleanor." / "Every time I've seen you, you've said you can't go back there.
      Now you don't have to." (turn 4).
    - On the first turn he can instead lower the gun, leave her and walk out to turn himself in (ending 6), whatever
      evidence he carries.
    - After two turns, "(Leave her.)" is offered (turns 3 and 4): Eleanor lets him go and he escapes alone.
    - After three turns, "(Shoot Eleanor.)" is offered (turn 4 only), ending 7: she drops to her knees under the
      sheet and falls face-down, blood spreading from her stomach.
    - If all four turns fail, Micah hears footsteps on the landing behind the other door, men coming up the stairs.
      He has three choices: pull the trigger on himself (ending 7, Eleanor lives), shoot Eleanor and then himself
      (ending 7), or leave her to them and escape alone.
    - Whenever Micah turns the gun on himself, he doesn't pray. He looks away at an empty corner of the room and says
      "Forgive me... all of you..."; then he puts the revolver to his temple, the screen cuts to black and the shot
      is heard over black.
    - If Micah manages to convince her, they both are in the kitchen: here, Micah has the possibility to set the
      mansion on fire. Eleanor waits for him in the kitchen while he goes back down to the bootleggers' wine cellar.
    - If he doesn't manage, he's alone in the kitchen, and can set the mansion on fire either way.
    - The fire: in the cellar Micah opens the whiskey barrel (the spigot runs whiskey onto the floor), takes the
      lit lantern back off its nail and uses it on the whiskey ("*FWOOOSH*"). The barrel has to be open first;
      the lighter is too close to throw. He climbs back up to the kitchen ("Closed the Club's account. Out. Now."),
      and the trapdoor is then refused. Outside, the house burns: "The cellar goes first. Then the kitchen, then
      the study, and everything Harrington ever wrote down in it." There is no explosion. The kitchen's gas range
      and candle stay selectable, but Micah talks himself out of them: "Gas and a candle? It would explode before
      we'd be far enough. But maybe if I use all that alcohol in the cellar..." (after the fire: "No need. The
      cellar's doing the job for me.").
    - During the escape the way back is shut: the baize door gets "Not back in there. Somebody's on the stairs by
      now." and so does the bootleggers' stair in the cellar, so the bedroom confrontation can't be replayed.
  - The choice not to shot the old man is accessible at this point only if Micah insisted for forgiveness with his wife,
    **and** made a qualifying church return, **and** carries both the wedding ring and cross pendant. Insisting means
    at least three forgiveness appeals. If this is the case, the option reads "Our Father..." and Micah starts the
    prayer straight away. He says it a verse at a time ("Our Father... who art in heaven..." through "deliver us from
    evil"), walking backwards towards the door and lowering the gun gradually with each verse, while the old man talks
    into every pause to distract him (mockery, Caleb, Eleanor, money, "Nobody forgives a man like you"). Micah reaches
    the door and walks out without the "Amen". The screen fades to black and the end of the prayer appears one line at
    a time, a second apart: "For Thine is the Kingdom, the Power and the Glory.", "Forever and ever.", "Amen.".
    Then the scene skips to *End of Act 3* (ending 1).
  - **Eleanor's coda.** If Eleanor refused both the Mother Superior and the old man's gin and powder, the prayer
    doesn't end the act. After the "Amen." the bedroom comes back with the player as Eleanor in the sheet and
    Harrington standing at the foot of the bed with his back to her, facing the door Micah left by and listening
    for his car. Two choices:
    - **Return to bed** (her rise played backwards): ending 1, as above.
    - **The candlestick** on the nightstand, a step from where she stands: she takes it while he mutters at the door
      ("There. A Ford. Of course it's a Ford."), steps up behind him and strikes, without crossing the room (new
      sprites: her swing, his fall forward, no wound). She leaves through the study and the kitchen; the doors back to the bedroom
      refuse her. The cellar is optional: the lantern hangs on its nail (Micah came in that way), she takes it
      and opens the whiskey barrel over it, and the house burns. No satchel: two hand actions. The kitchen door
      leads outside, a short beat in her voice, without Micah's escape. Then Micah's coffee scene at Rose's (as in
      ending 1), followed by ending 8 (she burned the house) or ending 9 (she didn't).

### End of Act 3

- Here, there are multiple endings, depending on the choices made in the previous selection:

#### Option 1 - Outside Micah's wife

- Previously used location
- This ending is accessible if Micah refuses to go forward at any point, either outside of the Church, or if he refuses
  to shoot the bartender, or the old man.
- The Act 2 forgiveness visit and Act 3 church-steps return stay unrestricted. Only the later return choices gain the
  progressively stricter requirements above; the other endings are unchanged.
- Before ringing, Micah throws Eleanor's perfumed cloth into the street ("Into the gutter with it. No more chasin'
  that dame."). In every other ending he still has it.
- Micah is outside, rings the bell, and asks his wife whether she would accept his previous invitation ot take a coffee with him.
- He offers coffee without claiming she owes him forgiveness or reconciliation. The renewed vows in the journal
  happen later, after he has begun showing change rather than merely promising it.
  Keep Micah's "Nothing you owe me." and the journal's "A year since that cup of coffee."
- In this case, the journal ends with Micah back with his wife, renewing the vows at his brother's Church.

#### Option 2 - Outskirts, with Eleanor

- Previously generated location
- This ending is accessible only if Micah manages to convince Eleanor in the Harrington mansion, and manages to set it on fire
  or finds the documents in the mansion.
- They both say goodbye to Chicago, and get into a car, which has to be generated in the location.
- In this case, the journal ends with Micah saying that he's now an alcoholic following Eleanor betraying him multiple times.

#### Option 3 - Outskirts, without Eleanor

- Previously generated location
- This ending is accessible if Micah didn't manage to convince Eleanor, and Micah either finds the documents in the mansion
  or sets it on fire.
- Her fate remains unknown during escape; there is no evacuation narration.
- Only if the mansion burned and Eleanor refused to follow, the outskirts scene begins with "The next morning"
  and does not describe the car door slamming in the dark. Micah reads: "The morning paper lists the dead.
  Eleanor Harrington. There it is, in black and white." He admits: "I told myself I was saving her.
  I left her there and lit the fuse." The fuse is figurative; the mechanism is the cellar's whiskey and the lantern.
  "They know who died. They don't know what I did." replaces the same-night orange-sky/secrecy line.
- Documents-only escape has no newspaper death report. With Eleanor following, the outskirts scene stays
  that night and she survives. Keep "She wouldn't come with me. Even with him on the carpet and the whole Club
  on its way." on both alone routes.
- You have to generate the car in this case also, Micah gets out of the car.
- In this case, the journal ends with Micah shooting himself, and the last entry is stained with alcohol and blood.

#### Option 4 - Prison - With Eleanor

- You have to generate prison parlatory, where the prisoners speaks with whoever came to talk to them.
- This ending is accessible if Micah managed to convince Eleanor, but neither set the mansion on fire nor found the
  signed documents.
- Micah in this case has a jumpsuit for an inmate, you have to generate the model.
- Micah and Eleanor seat at a table, one in front of the other, they talk, and Micah says that he maintained her out of
  jail, and she answers that she's grateful, but she has to move forward, and that she will return to Harrington son.
- In this case, the journal ends with Micah hanging himself, the last entry is a goodbye letter for his wife and son.

#### Option 5 - Prison - With brother

- You have to generate prison parlatory, where the prisoners speaks with whoever came to talk to them.
- This ending is accessible if Micah did not manage to convince Eleanor, and neither set the mansion on fire nor
  found the signed documents.
- Micah in this case has a jumpsuit for an inmate, you have to generate the model.
- Micah and his brother seat at a table, one in front of the other, the brother asks how's he doing, he reluctantly
  says that his wife doens't want to have anything to do with him, and that Eleanor keeps living with Harrington son.
- In this case, the journal ends with Micah hanging himself, the last entry is a goodbye letter for his wife and son.

#### Option 6 - Prison - With Rose

- Accessible if Micah shoots the old man, then lowers the gun on the first persuasion turn and leaves Eleanor to turn
  himself in. It overrides the evidence and the fire: there is no kitchen escape.
- In the prison parlour, Rose (new seated sprite) visits. Micah says he's sorry; Rose doesn't know if she can forgive
  him and doesn't really understand why he asked her to come, but she'll try.
- The journal ends: "I made a lot of awful choices, but now I know, I returned to the faith..."

#### Option 7 - The bedroom - Murder and suicide

- Accessible if Micah shoots the old man, fails to convince Eleanor, and then shoots her (on the fourth turn, or at
  the footsteps), or shoots himself at the footsteps.
- If he shoots her, Eleanor falls like the old man (new sprites: kneeling, then face-down under the sheet, the stain
  growing into a pool). Either way, Micah looks away at an empty corner, says "Forgive me... all of you...", raises
  the revolver to his temple; cut to black, then the shot.
- *End of Act Three* follows straight away; the present-day attic scene has no "The next morning" caption.
- If Micah shot only himself, Eleanor survives; Caleb's entry says so.
- The last entry is written by Caleb, from what the Club's men said in court (or, if Micah shot only himself, from
  what Eleanor told him after the funeral): he couldn't make Micah repent,
  finishing the journal is the only thing that eases his pain, and he warns whoever reads it not to walk in his
  brother's footsteps.

#### Endings 8 to 11 - Eleanor's own way

These need Eleanor to have refused **both** the Mother Superior (First Interlude) and the old man's gin and powder
(Second Interlude). The refusals alone change nothing: an early give-up still gives ending 1, and so does Eleanor
returning to bed in her coda. Endings 2-7 need her to have given in at least once.

#### Option 8 - Outskirts, Eleanor alone, after the fire

- Eleanor's coda: she strikes Harrington and burns the house. Micah's coffee scene at Rose's comes first, as in
  ending 1.
- Then the outskirts at night: Eleanor alone, in her black dress, walking out of the city. No car, no Micah, no
  newspaper.
- Micah keeps the journal; the last entry is his, copied from a letter she sent him at Rose's, without a return
  address.

#### Option 9 - Prison - Eleanor confesses

- Eleanor's coda: she strikes Harrington and leaves without burning the house. Micah's coffee scene at Rose's comes
  first.
- The prison parlour: Eleanor in an inmate's jumpsuit, seated where Micah sits (new sprite), Caleb across the
  table. She confesses her life's crimes and asks for Micah: "He's with his wife now." "It's better this way."
  Caleb absolves her.
- The last entry is Caleb's: he added her pages to his brother's journal from her confession.

#### Option 10 - Outskirts, Eleanor leaves for her peace

- The shoot route with both refusals ("Let's get out of here, quick."), and the mansion burned or Micah took the
  documents.
- The outskirts at night, the car as in ending 2: two car doors slam, and they both get out. She is tired, not
  angry. She says "I can't go on like this, Micah, I can't be with you. I need ... peace." and walks off down the
  road alone, out of sight. Micah stays by the car.
- The last entry is Micah's, hopeful: he is looking for his own peace (sober, writing to Rose, back at Caleb's
  church on Sundays). She told him the Second Interlude on the road, before she got out of the car.

#### Option 11 - Prison, Eleanor visits for the last time

- The shoot route with both refusals, and neither the fire nor the documents.
- The prison parlour, Micah in the jumpsuit, Eleanor across the table, as in ending 4. She doesn't go back to
  Theodore. She says "I hope you find your peace, Micah. I'm going to try to find mine, with the help of the
  Lord..." and leaves.
- The last entry is Micah's, hopeful: he looks for his peace behind bars (the Our Father, Caleb's visits, letters to
  Rose). She told him the Second Interlude across the parlour table.

### Present

The story ends with the father reading the last entry and commenting briefly. If Micah returned to his wife (ending 1)
or found his faith in prison (ending 6), or the journal ends on Eleanor's own way (endings 8 to 11), the father
keeps the journal, saying "Maybe Leo would like to read it some day." In ending 7 he respects Caleb's decision and
puts the journal back, maybe for Leo in a couple of years. In all other endings, he throws the journal back in the
trunk. Endings 8 to 11 keep the "The next morning" caption; only ending 7 skips it.

Every last entry also says where the Second Interlude's pages came from, answering Daniel's "Not sure that's
Micah's hand", and Daniel closes on it ("So that's whose hand it was." / "So he never really knew."):

| Ending | Who wrote the Second Interlude, and from what |
|---|---|
| 1 | Micah: Caleb passed it on; she came to St. Brendan's confessional months later. |
| 2 | Micah: she told him on the road. |
| 3 | Micah: what the Club's men said in court (she never testified, whether she lived or not). |
| 4 | Micah: she told him across the parlour table. |
| 5, 6 | Caleb's note: he heard it from her after the trial. |
| 7 | Caleb: what the Club's men said in court; or, if Micah shot only himself, she told him after the funeral. |
| 8 | Micah: a letter from her, no return address, arrived at Rose's house. |
| 9 | Caleb: from her confession. |
| 10 | Micah: she told him on the road, before she got out of the car. |
| 11 | Micah: she told him across the parlour table, the one time she came. |

The First Interlude is always Micah's: she told him during the night at the motel.

### Puzzle pacing and saves

Micah's sixteen added/expanded puzzles are distributed **7 in Act 1, 6 in Act 2, and 3 in Act 3**; Eleanor has one
in each interlude (Puzzles 17 and 18, in Room 507 and backstage at the Club). Puzzle 19 (the motel fire escape)
takes an item from the motel lobby to use in its back alley. Puzzles 11-15
are collect-and-combine puzzles in five extra locations: the Aurelian linen room and Rizzo's Flowers (Act 1), the
Tribune morgue and the Club vestibule (Act 2), and the Harrington wine cellar (Act 3). Each asks Micah to gather
items in that location, join them in the satchel and use the result to continue. Micah's lighter is the only
flame: no combination consumes it, and it is pinned in the satchel, so it is still there for the cellar lantern.
The matchbook is only the Blue Lantern clue.
The final act also retains its existing three-step alley encounter. The alarm gives the pursuit route
an interactive infiltration beat; the optional index provides investigation before the confrontation.
Giving up or reconciling never requires completing a pursuit-route puzzle. The obsolete temporary
motel map and burial survey are not part of the completed Act 3.

All the puzzles are untimed, have repeatable clues and unlimited retries, and preserve useful items.
Close-ups offer reset and close; Escape closes them. Unsubmitted settings reset on reopening.
The satchel has pages so every collected item remains accessible. The current save format
is version 9 (`SaveData.CurrentVersion`); earlier versions are incompatible with the Eleanor interludes, the bluing moving into the
brass box, the removed State Street hub, the convent arrival, the five added locations and the rerouted lift,
Blue Lantern entrance, Harrington lead, masked Club entrance and mansion entrance. Completed discoveries in
compatible saves remain completed, using independent markers
for the original and Act 3 puzzles. Saving/loading never completes an unfinished new puzzle.

### Scripture and adventure scope

Sister Agatha's direct quotation uses [Douay-Rheims (Challoner), Micheas 6:8](https://drbo.org/chapter/38006.htm):
"I will shew thee, O man, what is good." Micah recalls "love mercy".
Caleb retains his original counsel, warning and contrite-heart paraphrase, without the added exact quotations.
His prodigal-son account paraphrases [Luke 15:17-20](https://drbo.org/chapter/49015.htm), not a direct quotation. Religious objects remain
reminders; Rose's response is her own choice. Tragic endings are not declarations that repentance is impossible.

The adventure remains a compact, single-case indie point-and-click: sixteen puzzles for Micah and two for Eleanor, the alley encounter, optional
dialogue, two playable Eleanor interludes and eleven ending outcomes. The five collect-and-combine locations each sit on a route the story already
took (the hotel stairs, the speakeasy door, the Harrington lead, the masked Club and the mansion entrance)
rather than opening side quests.
Its single-case investigation is closer in scope to [The Blackwell Legacy](https://store.steampowered.com/app/80330/)
than the broader [Kathy Rain (2016)](https://store.steampowered.com/app/370910/),
[Technobabylon](https://store.steampowered.com/app/307580/) or [Unavowed](https://store.steampowered.com/app/336140/).
These are scope comparisons, not measured human completion times. Reading, solving puzzles, optional visits
and replaying endings change duration; accelerated autoplay must not be advertised as adventure length.
