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
  Harrington; Teddy gives Micah her photograph. At the end of the conversation Teddy steps to the corner of the
  desk by the lamp, takes out his wallet and pays the first day in advance, $22 cash: the $20 daily fee plus $2
  for expenses. Once the notes are on the desk, Micah thinks, "Twenty-two dollars. Pocket lint to him. A day's pay
  to me, and then some."; then Teddy says good evening and walks out of the room.
- Micah can't walk out on Teddy before the conversation is over.
- Micah's kit is no longer in the desk (its drawers face his own side of the desk, out of view):
  - the money: Teddy's notes on the desk;
  - the revolver: in its shoulder holster, the rig thrown over the spare coat on the coat rack;
  - the lockpick: a rolled leather pick case in the middle drawer of the filing cabinet the whiskey stands on.
    The drawer opens and closes with the hand; it slides shut by itself once the picks are taken.
  The $22 is a fictional cash holding, not a claim
  about average PI income. For purchasing-power context, the
  [NBER/BLS manufacturing weekly-earnings series](https://fred.stlouisfed.org/series/M08261USM052NNBR)
  reports $24.37 for October 1927; the $10 Sal bribe is a substantial payment, not an ordinary tip.
- Micah can't get out of his office without having taken these items. The door names each one still missing and
  where it is: "Not without my gun off the coat rack, my picks from the filing cabinet and my fee off the desk. A
  man goes out at night in this town, he goes prepared."
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
- There is a locked desk drawer, which Micah opens using the lockpick from the inventory on it. It is no hotel lock:
  Eleanor had a locksmith fit it, and it is damn hard; it snaps one of his picks before it gives (the lockpick
  stays in the inventory).
- Inside, there's a sheet of paper with a riddle in Eleanor's hand. Nothing Micah says or notes ties it to the safe
  until the safe is open:
  "Rightly He chose His Apostles; but first He left to stay in the desert to be tempted for a certain amount of
  days, He through whom all things were rightly made in the week of creation."
- **Puzzle 3 - Safe dial:** open the closet to reveal the safe. Hand or use the combination on the safe opens
  its graphical controls, not the safe itself. The dial runs 0 to 49, and the clue card only says it turns both
  ways and to listen for the tumblers. The riddle gives **12** (the apostles), **40** (the days of temptation in
  the desert) and **7** (the week of creation); "Rightly ... left ... rightly" gives the directions. Each stop that
  is right, counting from the first, drops a tumbler, and a wrong attempt says how many fell: the solution is
  **right 12 / left 40 / right 7**. The paper remains readable; wrong settings can be reset or retried. When the
  safe opens, Micah reads it back ("Twelve apostles, forty days in the desert, and seven days of creation.") and
  finds it strange that a woman like Eleanor would bring Christ into it ("Strange, a dame like her bringin' Christ
  into it.").
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

- Music: a hot band rehearsing in a back room, muffled through the wall (`BlueLanternJazz`), on every visit including the
  interlude. It plays through two choruses, breaks down on a wrong trombone note, noodles, and the drummer counts
  it back in.
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
  calls Micah back: "On second thought, I don't like you. Not one bit.", gestures to Sal (the bodyguard at
  the entrance), and on to the next scene. Sal's "Out back, pal" fades to a black screen held for two seconds (the
  beating happens off screen), then the alley fades in slowly on Micah on his knees. Being thrown out goes through
  the same blackout.

#### Street behind the club (the alley)

- New location: the road behind the club, dirty and in the shadow, with only one intermittent street lamp.
- The club's back door is propped open on a brick, showing a lit hall and a padded inner door; the band
  plays on far down the hall (`BlueLanternAlley`, picking up where the speakeasy left off). When Sal and Tony go
  back inside after the talk they shut it behind them (a door-close sound); the band is still heard faintly through
  it. In Act 3 the door is shut.
- Micah is on his knees, hands on the pavement (new kneeling pose and sprite) after a beating, Sal next to him and
  Tony behind Sal. So the player understands what happened, Sal steps up behind Micah, half turned to the screen,
  and kicks him in the belly twice with his right foot, the foot hidden behind Micah's body (new kicking sprite for
  Sal and a doubled-up sprite for Micah, a thud on each kick), then steps back and the dialogue starts. The beating splits Micah's bottom lip: from here on his close-ups (the fire-escape two-portrait panel
  and the beaten panel) show a small dark-red cut across it.
- Tony tells him that Eleanor is "hot stuff", that he sent her to a convent of nuns, and that he doesn't know
  anything else.
- Before leaving, Micah pushes up from his knees and forearms through a supported crouch to standing.
- The player regains control in the alley and clicks the street exit to travel to the convent. A black caption,
  "The next evening", covers the jump: Micah sleeps off the beating and goes up the next evening (Saturday).
  The investigation resumes days later, on Thursday; the Club invitation is for Thursday night, the Club's regular
  night.

#### Convent

- Micah arrives outside the neo-gothic convent at dusk, in the rain (the sidewalk and road wet and shining under the
  lamps, rain falling with its sound), with Eleanor absent. He thinks the beating is a day old and comments on its pointed arches, iron
  spikes and saints in the windows. The player must click the convent door to enter the corridor.
- Inside are the convent corridor and Eleanor's cell, really dark, simple and tiny,
  with a bed, a lampstand, a book and a night stand.
- In the corridor, Sister Agatha interrogates Micah: what he's doing here and what he wants with Eleanor.
  She hints at Micah's biblical name as a prophet, quoting Douay-Rheims Micheas 6:8, and says "You would do better to end the search
  here, and have nothing more to do with that Jezebel." Micah asks what she means; she retreats, telling
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
  first blows it out). He holds the lit cigarette while he thinks and, every 10 seconds while he talks, takes a drag
  (second strip: hand to mouth, the ember flares, a puff of smoke drifts off). The narration says he has
  hit a dead end.
- A choice of leads follows. The leads are silent choices (Micah doesn't say them aloud), and the narration, not
  Micah's voice, turns each of the first three down; a refused lead is not offered again:
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
- Micah asks the desk clerk whether he has seen Eleanor, holding her photograph up across the counter (back-view
  `micah_show_photo_back` / `micah_pocket_photo_back` sprites: only his bent arm shows, the photo is hidden by his
  back). The clerk doesn't answer, but he's visibly worried.
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
- Micah's arrival thought, then he walks to a talking distance from her. She opens: "Not many fellas climb a fire
  escape in the rain, mister. Were you looking for someone?"
- Act 1 cuts there: the screen fades to black on her question, holding a moment on black before the attic fades in
  (End of Act 1). The rest of their talk, the kiss and their night in her room follow the First Interlude (see
  *Motel fire escape, again* in Act 2).

### End of Act 1 - Present day

- Back in the attic, but it's dark and the lamp is on. Leo calls Daniel downstairs for dinner.
- The screen fades to black. "End of Act One" fades in, then fades out to an empty black screen; "Act Two" fades
  in, with "The next day" fading in below it two seconds later. Every act change uses the same cards (*End of
  Act Two*, then *Act Three* / *That night*; *End of Act Three*, then *The next morning*).
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
  A black screen shows "Chicago, 1927." for 2.5 seconds, then "First Interlude" below it on the same screen;
  both disappear and the First Interlude begins. After it, the story
  picks up with Micah on the motel fire escape, in front of Eleanor, then their night in her room, then his office.

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
   drawer, and phones Rizzo's Flowers on the candlestick telephone on the vanity (the answers are colour). Her
   packed duffle (dark brown leather: a white dress, a black suit, her pearls and nightclothes, a comb and a mirror,
   nothing Theodore paid for) stands at the foot of the bed: hand on it after the call and she takes it
   (`interlude_took_bag`); the door waits for it. From here to the convent cell she carries it (the
   `eleanor_bag_play` sheet), and before every conversation (Sal at the door, Tony, Sal at the Blue Lantern,
   Agatha) she sets it down at her feet (`eleanor_bag_down`) and takes it back afterwards (`eleanor_bag_up`).
   At the door, Sal and a second hood take her down
   the service stairs, told over black: the bellboy's memory, from her side.
   The box is a dead man's switch, not an invitation: if the Club ever drags her back, the Club goes into the
   morning paper. The card hides the Club's address; the matchbook, the bluing and the password get a reporter
   past the florist's grille and Sal to Tony, the one man who will talk. She leaves it in the room, not on her:
   the room is in her name, the hotel keeps a guest's things, a hotel safe can't be forced quietly, and if they
   catch her they search her first. The riddles keep Theodore's men out; somebody sent there on purpose, with a
   whole night, gets in.
2. **The Blue Lantern.** Colour only. Tony questions her; her answers are colour. He sends her to the convent
   for what he has seen of it, not for any debt: funny business, Father Caleb driving young girls up there after
   dark and going home alone, a padre's racket Tony doesn't want to know about. Whatever it is, it's the one place
   in town the Club won't touch. He has no line to the sisters: she is to ring the bell and keep quiet. Micah's
   narration adds that Eleanor knew where some of those girls had come from: she had brought a few to the Club
   herself. Micah hears all of this from her at the motel, so his brother's name is in it before Act 2. Before Sal drives her, she asks Tony to hold the switch: if the
   Club gets her back, he calls the Tribune city desk (not the cops: half of them drink at his bar) and says
   "Room 507, the Aurelian. The drawer, then the safe." He agrees: it is leverage on the old man. Micah's
   narration adds that she didn't know, telling him at the motel, that he had already emptied the safe (the
   Tribune morgue shows the call was made). Sal stays out of her way: the doorman's interception is off.
3. **Convent corridor, arrival.** Sister Agatha (the Mother Superior) first takes her for another of the girls who
   come to the door at night; then she knows the face and the perfume and calls her "a Jezebel from that
   hideous Club". Eleanor's replies (the Club, the old man, what she wants) are remembered for the night.
4. **Convent cell, that night.** She walks in and sets her bag down in front of the nightstand
   (`interlude_bag_left`). Hand on the bag (the `bag` hotspot, shown once it is down): she opens it, takes out her
   comb and little mirror and combs her hair (`eleanor_comb`); Hand on the bed or the nightstand only points her to
   the bag. A save from before she set it down loads with it still in her hand: the first Hand on the bed, the
   nightstand or the door (or a Walk to the door) sets it down. The scene fades slowly to black and holds it for a second (the comb and mirror stay in the cell: the
   ones Micah finds in the nightstand drawer in Act 1). When the knock comes she is
   sitting up on the edge of the bed by the pillow, awake, in her pyjamas (`eleanor_pyjama_play`, the
   `eleanor_cell_sit` pose). As the knock fades in she gets up off the bed (`eleanor_cell_rise`) and stands in front
   of it for the visit. After the knock, Agatha comes into the cell past midnight. She sincerely believes
   she has come to hear Eleanor's confession and quiet a troubled soul; the hour says she has other motives, which
   she won't admit even to herself (she is drawn to women). Micah's narration shows Eleanor seeing the opportunity:
   the Club's old trick, making the connection the depraved way, would buy her the convent's protection for as
   long as she wanted. She walks out again before the morning. The choice is saved:
   - **Tell her the truth** (`eleanor_refused_abbess`): Eleanor puts the thought away and tries to tell Agatha what
     she is running from. Ashamed and frightened, she stammers out only that there is a club and that she is on its
     stage, painted, before Agatha cuts in ("I know... I know enough of that diabolical club..."). No other detail of
     the Club is given here. Agatha reaches for her; Eleanor stops her gently. Ashamed, Agatha turns it round on her
     and puts her out at first light.
   - **Seduce her**: Agatha goes along with it at first; at the last moment she turns back, cursing Eleanor for a
     demon, and leaves. Nothing is shown.
   The Club's strings replace the convent piano from the knock until Agatha walks out.
   Eleanor leaves the convent the next morning.

- **Puzzle 17 - The brass box:** she builds the insurance Micah finds later, and locks it away herself. Her lines
  name its reader as whoever the paper sends, never Micah. She arrives with two things in her satchel: a blank slip
  of hotel paper and the only key to the lock she had a locksmith fit to the desk drawer.
  - Hand on the vanity: the open brass box (the card, the matchbook, the bluing already in it) and the bare paper
    water flower, the word inked inside.
  - Hand on the writing desk: she tears a scrap of hotel paper and writes "Give me a drink and I'll tell you the
    word."
  - Look on the clothes shows a torn red hem; hand pulls a length of red thread from it.
  - Items join two at a time. Join the scrap and the flower: the riddle-wrapped flower (both used up), loose until
    it is tied. Join it with the thread: the wrapped water flower (both used up). The thread on the bare flower or
    on the scrap alone is refused, and the loose wrapped flower won't go in the box until it is tied.
  - Join the flower and the box: the packed box.
  - Hand on the closet opens it: her dresses in a row and, at the back, the safe standing half open. Use the packed
    box on the safe (or the open closet): the box goes in, still showing through the open door. Hand on the safe
    shuts it and spins the dial. Hand on the open closet shuts it again (optional); she won't shut it on the box
    while the safe still stands open.
  - Use the blank slip on the writing desk: she writes the safe's combination as the riddle Micah finds.
    Use it on the drawer to put it in, then her key on the drawer to lock it (she keeps the key).
  - Wrong joins and wrong items on the closet, safe or drawer get a hint in her voice. The drawer waits for the
    safe, the call for the locked drawer, the bag for the call, and the door for all of them; at the door she names
    the first step still to do.
5. **The motel room.** She takes a room in sight of the convent (the motel with an empty bed and a bare chair, her
   duffle on the floor by the dresser; she is back in the black dress) and watches from the
   window for four days. On the fourth evening she sees Micah, a day after his beating, arrive at the convent door, come out again and light a cigarette in the road, then
   hears him arguing with the clerk downstairs. From the window she sees him in the alley below, on a fruit crate,
   hooking the fire-escape ladder down with the clerk's umbrella and climbing it; she steps out onto the fire escape
   to wait for him. A 3-second fade to black, a short hold on black with no caption, then the fire escape fades in:
   Micah's journal takes over again (*Motel fire escape, again*).

### Chicago, 1927

#### Motel fire escape, again

- Right after the First Interlude, over black, the journal is Micah's again: the landing fades in with Micah already
  standing in front of Eleanor, where Act 1 left them, his Act 2 satchel back. The office jazz plays.
- Eleanor repeats her opening, word for word: "Not many fellas climb a fire escape in the rain, mister. Were you
  looking for someone?" Micah asks about Eleanor Harrington, introduces himself, and the conversation goes on.
- She asks why he's trying to find her and Micah explains; the conversation has tension and attraction.
- While they talk, a framed close-up shows them side by side, Micah on the left and Eleanor on the right, in the
  same VGA style as the other close-ups. It appears immediately after Eleanor's opening line; each active
  speaker's dialogue is shown below their own portrait half.
- The panel disappears completely just before the player answers "And what do you get, if you bring me home?"
  The compensation choices and the remaining conversation take place on the landing with normal overhead speech.
- After Eleanor says "I can't go back there...", Micah answers "Then stay. Right here." and starts walking
  slowly towards her. While he walks she says "You're walking into the rain, Mr. Jones. Not out of it." As the
  line ends he reaches her and kisses her on the lips, and they hold the kiss while his narration says "I'd
  have climbed a hundred fire escapes for that. Some things a man doesn't decide. They decide him." and "And
  somewhere across town Rose was waiting up for me, the way she always did. I kissed Eleanor anyway." Only then
  does the screen fade to black, over 3 seconds. "Later that night" stays alone on the black screen for 3 seconds,
  then a 3-second fade brings in *Motel room, night*.

#### Motel room, night

- After the kiss on the fire escape and "Later that night", inside her room at the same motel, Micah is getting dressed (new dressing sprite
  for the character) while Eleanor is in the bed, under the sheet. Micah's Act 2 satchel is already back.
- They say this was probably a mistake and that they should never see each other again. Micah says he won't
  tell anyone where they can find her, and that he will give up the job.
- Micah asks what she'll do now and where she'll go. She will get away: she has friends, and money enough; he
  doesn't have to worry. The narration says Micah has a hunch it isn't the truth, but he is too ashamed to ask
  more, too ashamed to be in that room at all, and she knows it; he can see it in her eyes. So he leaves.
- Eleanor remains in bed against the pillows, covered by the white sheet. She does not rise; her lips move while
  she talks.
  The scene then fades to black: "Days later" fades in over 3 seconds, stays for 3 more and fades out over 3,
  then Micah's office fades in.

#### Office, days later

- A bottle of whiskey and a cup are in the office. Micah raises the cup, drinks, and puts it down.
- Micah's thoughts go back to the motel: he knew her answer was a lie and let it stand, too ashamed to ask; and
  every night since he has wanted her back, not saved but wanted.
- Micah chooses whether to take his wedding ring or leave it in the office; the original decision is saved.
- A left-behind ring remains visible and can be collected on a later office visit without changing the original decision.
- After the choice, Micah decides to go back to the motel to find out where she went, and the scene moves to the
  motel's back alley.

#### Behind the motel, days later

- The drop ladder is pulled up out of reach again, as before Micah hooked it down with the umbrella (the crate
  stays under it). Micah won't climb up to her room: "Up the fire escape like a second-story man again? Nix.
  Better brace the joe at the desk."
- The fire escape and the main road are refused until the clerk has talked; the motel door leads to the lobby.

#### Motel lobby, days later

- Micah asks the clerk whether the woman is still upstairs. Gone, the clerk says: checked out.
- Two rounds of questions (where she was headed, who picked her up, whether she paid or left a note) only make the
  clerk more tense; he holds on to the register and tells Micah to beat it. Micah realises something happened.
- "Nice tie, pal. Your wife's present?" "...What?" Micah grabs the tie and hauls the clerk's face down onto the
  counter (new `micah_tie_pull` and `clerk_tie_pulled` sprites) and threatens him.
- The clerk spills: two men took her, the same night, not an hour after Micah left; a big one and a young one. He
  knows nothing else. Micah lets go, and walks out to the cathedral steps.
- A notepad page, *The motel again*, records it.

#### Outside of the church (cathedral steps)

- Existing location.
- Micah thinks that two men took her the night he walked out, and he didn't even ask where she'd go; still he
  can't think of anything else but her.
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
- The greeting and Micah's story of Eleanor play over the room. When the talk turns to salvation, with Micah's
  "Right now, Caleb... I'm too far gone to be saved.", the brothers' two-portrait close-up comes up, the same
  full-size panel as the fire escape's: Micah on the left, Father Caleb on the right, both in the candlelit brick
  nave of Caleb's picture. Micah's portrait is a new picture (his fire-escape portrait cut out and set in front of
  the church), not a change to the fire-escape one. Each line sits along the panel's bottom edge under its
  speaker's portrait. The panel goes after Caleb's "Micah, wait-", before Micah walks out.

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
- Micah has to intimidate the librarian (before asking about the symbol Micah refuses to do it, and before the
  lookup he needs a precise title). Either way he requests the identified book, the librarian confirms that it
  describes ancient Celtic rituals and gives it to him if he goes away:
  - **Hand on the librarian** (canonical): Micah steps in, grabs him by the collar and drags him in
    close, the librarian stumbling forward with his feet on the floor (one animation for both, the librarian actor
    hidden), holds him through the request, then lets him go.
  - **Revolver on the librarian** (alternative): Micah draws and aims the revolver at him while he asks, then
    puts it back in its shoulder holster (`micah_holster`; every time the gun goes away he holsters it this way).
- Both routes set the same flags. With the book in hand Micah walks straight out through the hall door to the map.
- After leaving, the library isn't accessible anymore: selecting it on the map, Micah says "Better not show my face
  there for the time being".
- Leaving the library normally (the hall door on the left wall) returns to the map. The two armchairs are props:
  Micah passes behind or in front of them depending on where he stands.

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
- His recovery is shown through sitting up, rolling forward onto his hands and knees, and getting up off his knees
  as in the alley, rather than an instantaneous pose swap.
  The player is then presented with two choices:
  - Go find his wife.
  - Push forward.
- If Micah go find his wife, there will be another location, outside of a terrace house in a row of terrace.
- Otherwise, skip the next part.

#### Outside Micah's wife house

- Micah is outside the house. The player can choose whether to get out of the location, or ring the bell.
- It never rains on Rose's street, not even on the first visit. On arrival Micah notes it: "Funny. It's rained on me
  all week, and it stops at Rose's street."
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
  After "Wait!" (not during it) a framed close-up panel pops up over the scene, two portraits split by a bar like the
  motel fire-escape panel: Rose at her door on the left, Micah on the right. After a couple of seconds of silence,
  "Don't get into trouble again." appears beneath Rose's portrait along the panel's bottom edge, Micah answers only
  "..." beneath his own portrait, then the panel is
  removed and the scene continues.
- Rose makes clear that forgiveness is not something Micah can demand; the callback is concern, not absolution.
  Keep her third-appeal reply: "Forgiving's the easy part, Micah. Forgetting is what you keep asking for."
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
  Micah has a concrete lead on his brother from Eleanor's story at the motel: Tony told her Father Caleb drives
  girls up to the convent after dark, and that's the one door the Club won't knock on. Caleb first brushes it off
  (he drives the sisters' groceries and says their Mass). Micah's second reason: the convent belongs to the Church,
  even though Mother Superior runs it and Caleb runs the parish; so Caleb might know something. Both reasons must
  be offered before the choice "They have her, Caleb. If you know anything, tell me." Micah does not claim Caleb
  hid Eleanor in his sacristy; the established refuge is the convent.
- After Micah's plea, Caleb tells the truth about the Club. It runs a trafficking ring to keep its Thursday
  "spectacles" supplied with fresh girls: farm girls and immigrant girls taken off the trains at Union Station with
  promises of work. Some escape to Caleb's church door; he drives them up to the convent after dark (the funny
  business Tony saw), and together with the sisters he hides them (new names, a ticket to a parish out of state). Caleb can't stop the traffic, so he keeps his mouth shut,
  and in exchange the Club leaves the convent alone; if he talked, they would simply take other girls and come for
  the ones behind the convent walls. Micah calls him a hypocrite: he preaches repentance, and he could have gone
  to the press. Caleb half-concedes ("I confess the silence every week, and I mean to break it the day it won't bury
  the girls we hid. That day hasn't come.").
- Micah's brother will tell him that the Convent is probably the best way to ask. He will advise Micah not to go there,
  to give up this foolish search.
  Micah will answer "There isn't much left for me to do."
  The brother will say "You know that isn't true."
  Caleb teaches that repentance is for anyone, at any time in their life, and that the Lord forgives whoever truly
  repents. When Micah insists he is too far gone, Caleb rebukes him harshly: thinking himself beyond salvation is
  pride, arrogant and self-serving. He closes with the prodigal son.
  Micah will say nothing and get out.
- The choices and Caleb's story of the Club play over the room. The brothers' close-up from the first visit
  returns for the sermon on repentance: it comes up after "Give up this foolish search", with Micah's "There isn't
  much left for me to do.", and goes after the prodigal son, before Micah's silent thought and walk out.

#### Map of Chicago

- The convent will appear as the next location.

#### Convent

- Micah will interrogate the sister about the club and Eleanor. She will say she knows nothing, Micah will have to
  use the revolver again to threaten her.
  The sister will say "Are you crazy?!"
  Micah: "Yeah. You can say that, sister. Where's Eleanor? What goes on at that club?"
  Micah's madness is escalating with his sin (the librarian roughed up, now a nun in her own convent; later he
  shoots the mobster and kills the old man). With the gun on her, Agatha's own repentance begins: she confesses
  that she went to Eleanor's cell past midnight and called it charity, that it was all her fault and that she
  failed her. Both versions keep "She's a performer." and send Micah to Harrington senior.
  - If Eleanor seduced her, Agatha still calls Eleanor a Jezebel ("She nearly had me fooled, the whore." before
    she breaks, then "Jezebel she is. But it was my fault.").
  - If Eleanor told her the truth (`eleanor_refused_abbess`), the word Jezebel is never said: Agatha admits Eleanor tried to
    tell her and she wouldn't let her finish, and that she turned it round on Eleanor and put her out at first light, because Eleanor stopped her.
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
    to hold them together." Take the paste pot from the layout desk. Items join two at a time: the paste with
    either half gives a pasted half, and the pasted half with the other half gives the mended clipping (the paste
    is kept; it goes back on the desk when Micah leaves, or by using it on the desk). A pasted half doesn't take
    more paste; two pasted halves still join into the mended clipping.
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
- Both later visits come back to the girls: in the warning, Caleb admits he kept quiet for years and Micah calls
  him on it again; before the masked Club visit he says he has been praying on what Micah told him, and asks Micah
  to look at the girls on that stage if he goes.
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
  - **Puzzle 7 - Ladder catch:** the tapered packing wedge is visible among the crates from the start, but
    reaching for it while watched gets Micah spotted; take it after the distraction. Stack the crates to
    reach the jammed ladder catch, whose illustration shows the obstruction.
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
    opens (flag `vestibule_passed`) and Micah walks into the Club hall. The sealed card is returned to him; inside,
    the master of ceremonies doesn't ask for it again: the door has already vouched for him.

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

- Dark again, the father is called for dinner. "End of Act Two" fades out to black, then "Act Three" fades in,
  and "That night" below it (as at the end of Act 1).

### Act 3 - Present day, bedroom

- Father in the bedroom (new location) reading with the nightstand lamp on, wife covered by the blankets, light off on her side.
- Father keeps reading, then frowns: "These pages read differently. Not sure that's Micah's hand." Every ending's
  last entry answers him (see *Present*). The black screen shows "Chicago, 1927." for 2.5 seconds, then
  "Second Interlude" below it, as for the First Interlude.

### Second Interlude - Eleanor

The player moves Eleanor again. The narration is a neutral third voice. Same rules as the First Interlude: her own
satchel for what she finds there, no **N**, Micah's things stashed until the interlude ends.

1. **The motel room, after Micah has gone.** Colour only. A knock at the door. Eleanor goes to it but stops
   halfway; the door is kicked in, and Bruno and a second goon (new sprite) walk in and stand between her and it.
   They followed "your detective" there. Her answers are colour; Bruno tells her to bring her coat, her hat and her
   duffle ("Coat. Hat. The bag, too."; it rides in the Club's car from then on), and they walk her out through the
   broken door, over black.
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
  - Hand on the compact and the lipstick on the dressing table: her compact of face powder (no puff) and her
    lipstick, each gone from the table once taken. The perfume and the hairbrush beside them are only looked at.
  - Hand on the costume rail: a swansdown puff in a member's wife's gown pocket.
  - Hand on the painted screens: a hairpin clipped to the silk.
  - Join the puff and the compact, then use them on the mirror, in order: the face powder, the lipstick, the
    hairpin. Out of order, she says so ("Face powder first. Then the mouth. Then the hair."). Look on the mirror
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
  unless he allows it, and they come back every Thursday to bow. The girls are part of it: a new face on the stage
  every Thursday, and a secret every man in the room shares, which binds them tighter than any oath.
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
  to the end of act 3 (caption "End of Act Three"); if Eleanor held out, her escape with Caleb comes first (ending 1).
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
- The bartender tells him to bug off, these people are really dangerous (they bring girls in off the trains like
  crates of oranges, and nobody asks), and he'd be better off with a bullet in his skull.
- At this point, the player must choose between firing the revolver into his shoulder, firing it into the wall by his
  head (the warning shot), or walking away, because it's not worth it.
  The option to walk away is available only if Micah carries his wedding ring and returned to Caleb before Harrington's
  office, before the masked Club visit, or through the Act 3 office route. The cross is not required here.
- If the player walks out, he's going to his wife's house (caption *End of Act Three*).
- If he fires, Tony is hit in the shoulder: he clutches it, his legs fold straight down under him and he ends up on
  his back, with the blood on his shoulder and pooling on the ground under it.
- The bartender screams, and he tell him to go directly to the house of Harrington father, he explains how to get inside
  from the kitchen, because they provide them with booze. Pressed ("And?"), he also gives up the burglar bell wired to
  the kitchen door since the Feds came sniffing, swearing on his mother that's everything.
- Tony on his back in the gravel, the dialogue ends with Micah's thoughts saying the problem out loud: Tony knows his
  name, his office and Rose's street, and Tony is the mob. Then the player chooses, as a dialogue choice:
  - **(Leave him bleeding, and go.)**: Micah leaves Tony alive and walks out of the alley on his own, back to his
    office before the mansion. Tony's revenge follows him into every ending (below, *Tony's revenge*).
  - **(Finish him. He knows my name.)** (`finish_tony`): after the dialogue Micah walks round to stand past his head,
    facing back down the alley, and points the revolver down at it (`micah_aim_down` strip, held on
    `micah_aim_down_held`, then `micah_holster_down` raises it and puts it away). Tony begs; Micah shoots him
    through the head in cold blood so he can't tell anybody who
    shot him (`killed_tony`, knots `bartender_kill` and `bartender_dead`; new `bartender_dead` sprite, Tony still on
    his back, a wound in his temple and the pool spread under his head, shown the moment the shot goes off).
    Repentance becomes much harder from here; see *The night after Tony*.
- Knocking again after the shot is refused: nobody's coming out of that door after a gunshot.
- **The warning shot** (`warned_tony`, knot `bartender_miss`): the bullet goes into the bricks by Tony's ear. Scared
  and unhurt, Tony gives the Gold Coast, the kitchen door and the key on the lintel ("walk right in like the delivery
  boys"), too quickly: he leaves out the alarm. He goes back inside and bolts the door; knocking is refused. No blood,
  so no debt with the mob and no revenge in the endings. The street leads to the office in the storm, as after the
  shoulder.

#### The night after Tony (the kill route)

- The street opens onto the map of Chicago, at night, with only three pins: the **Blue Lantern** (back to the alley,
  where Tony hasn't moved), **Caleb's church** and the **Harrington mansion** (new map pins). A one-time intro on the
  map says the city has shrunk to three places. The church and the mansion are both final choices: neither leads
  back to the map.
- **The mansion:** through the office in the storm (Micah remembers both shots), then the mansion as usual, with
  no confession. The Our Father is not offered in the old man's bedroom, even with the ring, the cross and the
  forgiveness appeals: a man who killed to cover his tracks can't pray his way past the old man before saying it out
  loud.
- **The church:** Caleb sees the blood on Micah's cuff, and Micah confesses (`caleb_tony`). Caleb asks
  whether he is sorry, not scared, and for his promise of no more blood and to do what he can for Tony's mother; gives a penance (prayer for Tony and his
  mother) and absolves him. Then, as his brother and not as a penance, he offers to walk him to the station on
  Maxwell Street (see [Theology](docs/theology.md)). Micah's first words about Tony play over the room; the
  brothers' close-up comes up with Caleb's "Kneel down, Micah." and stays through the confession and the choice, going before Micah leaves:
  - **"(Turn yourself in.)":** `surrendered_tony`; fade, *End of Act Three*, ending 12.
  - **"Not yet. Eleanor's still in that house.":** `confessed_tony`; Micah promises to walk in on his own two feet
    after her, and goes on through the office in the storm to the mansion. With the confession, the Our Father is
    offered again on the usual terms, and after the prayer Micah keeps his promise: ending 12 instead of ending 1.

#### Office, the storm

- Narration only: the journal's narrating voice is the only voice in the scene. No music; rain on the glass and
  thunder.
- A storm has knocked the power out on the whole block: the banker's lamp and the HOTEL sign are dark and the office
  is completely black, lit only by lightning at the window (`Thunder` follows each flash after a short delay).
- Micah stands at the window, his back to the room, without his hat, drinking from the whiskey bottle. The hat lies
  on the desk next to the cup.
- The narrating voice describes his slow descent into sin: irresistible, a road he can't stop walking down even
  though he knows abundantly well how it ends.
- At the climax it says that sin is a beast that climbs inside a man and walks him down the road of depravity.
  Lightning strikes twice (light, dark, light): in the first flash the window's reflection shows a black demon
  shadow holding Micah's reflection; in the second the reflection is almost swallowed by the shadow. The real Micah
  doesn't move.
- The player regains control. The door refuses him while he is bareheaded.
- Clicking the hat (hand): Micah walks to the desk, leaves the bottle there, picks up the hat and puts it on.
- The player must then click the door to leave; the next stop is the mansion.

#### Outside of the Harrington mansion, behind the kitchen

- Music: from here to the last mansion room, one unbroken dissonant thriller loop (double bass, pizzicato clusters,
  bowed cello, one brief high trumpet stab), also under Eleanor's coda; it stops when the story leaves the house.
- Tony's key-on-the-lintel shortcut is wired to an alarm. Inspect the door or reach for the key to notice
  the taut wire; move the coal bin under the bell to reach its hammer.
- After the warning shot Micah doesn't know about the alarm: taking the key doesn't reveal it, but a look at the door,
  the lintel, the wire or the bell does (and then the night goes on as usual). Opening the door before that rings the
  bell (`AlarmBell`), and heavy feet come down the back stairs (`alarm_footsteps`):
  - **Run** (`alarm_ran`): ending 13.
  - **Stay. She's in there.** (`alarm_stayed`): into the kitchen, where two of the Club's men (charcoal overcoat and
    fedora, grey suit and flat cap; `gunman_a`/`gunman_b` sprites with draw and aim strips) wait at the cook's table.
    "Bell's for the delivery boys, pal." Micah gets as far as "I'm here for Eleanor Har...": two shots, he falls
    backwards on the tiles (`micah_gunned_down`/`micah_gunned_dead`), cut to black, ending 14.
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
  desk. The register page is a field of fifteen unlabelled account dots; the index is an irregular figure of
  five punched holes, three marked BANK/JUDGE/CAPTAIN and two blank. Slide, rotate and flip (turn over) the
  index until all five holes sit on dots. The figure fits in exactly two places, and many placements cover
  four of the five dots. Only the note decides between the two fits: BANK above JUDGE and CAPTAIN left of
  BANK. The other fit leaves CAPTAIN right of BANK, and submitting it says the marks don't read as the note
  says. The solution is flipped, turned 180 degrees, offset **(6, 9)**. The aligned window identifies the drawer pocket containing signed payoff
  sheets, which Micah takes as the existing documents item. Besides the payoffs, the sheets record the Club's
  Thursday payments: girls' names, stations and prices. Cancellation keeps both clues.
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
    - **Exception (endings 10 and 11).** If Eleanor told the Mother Superior the truth and refused the old man's gin and
      powder in the interludes, there is no persuasion. Worn out, emptied by too much at once, she only says
      "Let's get out of here, quick." (`eleanor_weary`) and follows Micah, as if he had convinced her: no turning
      himself in, no leaving her, no shooting her. On the weary route Eleanor follows through the kitchen in silence (the fire, the
      documents), and Micah keeps the revolver. The fire or the documents give ending 10, neither gives ending 11.
    - Eleanor always gets four turns, each with four lines for Micah, one of each type. Every line scores points,
      and after the fourth turn a total of at least 10 out of 16 convinces her (`eleanor_convinced`):
      possessive 4, rational 2, positive 1, clumsy 0. The persuasion only happens when Eleanor gave in at least once in
      the interludes, so she answers the possessive, earthly way of the men who already own her, the old man's way.
      One clumsy line can be overcome, two can't, and at least one possessive line is needed. Eleanor answers each
      line in character, and Micah's thoughts hint when a line drew her in or when she is out of reach.
      Every line, its type, its reply, the arithmetic and the Ink implementation are in
      [Eleanor's persuasion](docs/eleanor-persuasion.md), which must be kept in step with the Ink.
    - On the first turn he can instead leave her and walk out to turn himself in (ending 6), whatever
      evidence he carries.
    - After two turns, "(Leave her.)" is offered (turns 3 and 4): Eleanor lets him go and he escapes alone.
    - After three turns, "(Shoot Eleanor.)" is offered (turn 4 only), ending 7: she drops to her knees under the
      sheet and falls face-down, blood spreading from her stomach.
    - If all four turns fail, Micah hears footsteps on the landing behind the other door, men coming up the stairs.
      He has three choices: pull the trigger on himself (ending 7, Eleanor lives), shoot Eleanor and then himself
      (ending 7), or leave her to them and escape alone.
    - Whenever Micah turns the gun on himself or on Eleanor, he draws it again (he holstered it once the old man fell).
      Turning it on himself, he doesn't pray. He looks away at an empty corner of the room and says
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
    at least three forgiveness appeals. If Micah killed Tony, it also needs his confession to Caleb (`confessed_tony`).
    If this is the case, the option reads "Our Father..." and Micah starts the
    prayer straight away. He says it a verse at a time ("Our Father... who art in heaven..." through "deliver us from
    evil"), walking backwards towards the door and lowering the gun gradually with each verse, while the old man talks
    into every pause to distract him (mockery, Caleb, Eleanor, money, "Nobody forgives a man like you"). Micah reaches
    the door and walks out without the "Amen". The screen fades to black and the end of the prayer appears one line at
    a time, a second apart: "For Thine is the Kingdom, the Power and the Glory.", "Forever and ever.", "Amen.".
    Then the scene skips to *End of Act 3* (ending 1; ending 12 if Micah killed Tony, who keeps his promise to Caleb).
  - **Eleanor's coda.** If Eleanor told the Mother Superior the truth and refused the old man's gin and powder, the prayer
    doesn't end the act. After the last line the bedroom comes back with the player as Eleanor in the sheet and
    Harrington standing at the foot of the bed with his back to her, facing the door Micah left by and listening
    for his car. Two choices:
    - **Return to bed** (her rise played backwards): ending 1, as above (12 on the kill route).
    - **The candlestick** on the nightstand, a step from where she stands: she takes it while he mutters at the door
      ("There. A Ford. Of course it's a Ford."), steps up behind him and strikes, without crossing the room (new
      sprites: her swing, his fall forward, no wound). She leaves through the study (she had only ever seen it from the doorway), taking the old man's
      "Thursday book" (the Club's ledger of the girls: she always knew where he kept it), and the kitchen; the doors back to the bedroom
      refuse her. She has her own satchel again, empty when the coda starts (Micah's things are put aside and come
      back to him when it ends; a lantern she didn't use is left behind). The cellar is optional: the lit lantern
      hangs on its nail (Micah came in that way) and goes into her satchel; hand on the whiskey barrel opens its
      spigot, and the lantern used on the running whiskey sets the cellar alight. The kitchen door leads outside, a
      short beat in her voice, without Micah's escape; if she set the fire, the house goes up behind her (*CRASH*,
      the windows orange one by one). Then Micah's coffee scene at Rose's (as in
      ending 1), followed by ending 8 (she burned the house) or ending 9 (she didn't). On the kill route there is no
      coffee scene: Micah has gone to the station, and the endings tell it from Joliet.

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
- He offers coffee without claiming she owes him forgiveness or reconciliation. The promises said again in the journal
  happen later, after he has begun showing change rather than merely promising it.
  Keep Micah's "Nothing you owe me." and the journal's "A year since that cup of coffee." Rose recalls "Last time
  you were here, you wanted me to forgive you." only if he asked her for it on her doorstep (`rose_wait`); if he
  said good night first, she only asks "What do you want?".
- In this case, the journal ends with Micah back with his wife, saying their promises again at his brother's church, with his blessing (or, if he
  shot Tony and they left Chicago, saying their promises again at St. Anne's downstate, with Caleb's blessing).
- In the present day, when Daniel reads the vows entry, a photograph of Micah and Rose on that day pops up on the
  left of the screen: a 1920s sepia studio print, pixelised like the other close-ups, on a cream card mount with worn
  corners, the size of a photo rather than a full panel. Daniel's lines sit in a column to its right. It appears with
  the vows entry (INSET: vows) and goes after "...when he has somebody to tell them to."
- Only if Micah took the signed papers from the study (possible on the Our Father route), the journal adds that
  Caleb carried them to the Tribune himself; a grand jury followed, and the Club's Thursdays ended. Without the
  papers, there is no mention.
- **Eleanor's escape, with Caleb.** If Eleanor held out both times (the truth to the Mother Superior, the old man's gin
  and powder refused) and Micah gave up before the mansion (on the church steps, or walking away from Tony), it is
  still ending 1, but after Rose's "Why not." the screen fades to the outskirts at night (`caleb_escape`). The rain
  has stopped. The player is Eleanor in her white dress and pearls, from the duffle she had packed for running;
  Caleb stands beside her, and the scene plays by itself. Three nights after the Club, Caleb got her out of the old
  man's house:
  - Eleanor: it's one thing for him to sneak a few of the other girls out the back, but she's their star; they won't
    take it lying down, and they'll come after him. Caleb: "I know. But I'm tired of playing their game."
  - Practical arrangements: a parishioner's produce truck passes before dawn and takes her downstate to Springfield,
    where Caleb's friends, the Franciscan sisters, put her up with no questions until a family he knows can take her
    on to St. Louis; he gives her an envelope with a little money.
  - Eleanor knows Caleb for Micah's brother by his hands, and tells him Micah came for her into the Club, masked,
    and was carried out.
  - Eleanor learns that Micah went home to his wife, and is glad of it. Her last words, as the truck's lights come
    up the road: "Say hi to Micah."
  - Then *End of Act Three*. The journal's last entry is ending 1's, but the Second Interlude's source changes: Caleb
    passed on what she told him the night he got her out of Chicago, at her asking.

#### Option 2 - Outskirts, with Eleanor

- Previously generated location
- This ending is accessible only if Micah manages to convince Eleanor in the Harrington mansion, and manages to set it on fire
  or finds the documents in the mansion.
- They both say goodbye to Chicago, and get into a car, which has to be generated in the location.
- At the gate Eleanor takes the duffle she had packed for running from the Club's car and changes in Micah's car
  during the drive: a black skirt suit cut above the knee, and no pearls.
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
- Eleanor wears the black suit of ending 2.
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

- Accessible if Micah shoots the old man, then on the first persuasion turn leaves Eleanor to turn
  himself in. It overrides the evidence and the fire: there is no kitchen escape.
- In the prison parlour, Rose (new seated sprite) visits. Micah says he's sorry; Rose doesn't know if she can forgive
  him and doesn't really understand why he asked her to come, but she'll try.
- The journal ends: "I made a lot of awful choices, but now I know, I returned to the faith..."
- Only if Micah carried the signed papers, the journal adds that he handed them over with his confession, and the
  girls' names came out at his trial: the Club's Thursdays ended there.

#### Option 7 - The bedroom - Murder and suicide

- Accessible if Micah shoots the old man, fails to convince Eleanor, and then shoots her (on the fourth turn, or at
  the footsteps), or shoots himself at the footsteps.
- If he shoots her, Eleanor falls like the old man (new sprites: kneeling, then face-down under the sheet, the stain
  growing into a pool). Either way, Micah looks away at an empty corner, says "Forgive me... all of you...", raises
  the revolver to his temple; cut to black, then the shot.
- *End of Act Three* follows straight away; the present-day attic scene has no "The next morning" caption.
- If Micah shot only himself, Eleanor survives; Caleb's entry says so.
- The last entry is written by Caleb, from what the Club's men said in court (or, if Micah shot only himself, from
  what Eleanor told him after the funeral; she heard him ask forgiveness, and Caleb leaves what that word weighed to
  God). If Micah confessed Tony first, Caleb writes only that a bartender named Tony was found behind the Blue Lantern,
  and that the rest he may not write (the seal). He couldn't make Micah repent, he prays for his soul still,
  finishing the journal is the only thing that eases his pain, and he warns whoever reads it not to walk in his
  brother's footsteps.

#### Endings 8 to 11 - Eleanor's own way

These need Eleanor to have held out **both** times: telling the Mother Superior the truth instead of seducing her
(First Interlude) and refusing the old man's gin and powder
(Second Interlude). The refusals alone change nothing: an early give-up still gives ending 1 (with Eleanor's escape
with Caleb after the coffee, see Option 1), and so does Eleanor
returning to bed in her coda. Endings 2-7 need her to have given in at least once.

#### Option 8 - Outskirts, Eleanor alone, after the fire

- Eleanor's coda: she strikes Harrington and burns the house. Micah's coffee scene at Rose's comes first, as in
  ending 1.
- Then the outskirts at night: Eleanor alone, in a white dress with her pearls (from the duffle she had packed for
  running, still in the Club's car at the gate), walking out of the city. No car, no Micah, no
  newspaper.
- Micah keeps the journal; the last entry is his, copied from a letter she sent him at Rose's, without a return
  address. Before leaving the city she mailed the old man's Thursday book to the Tribune; the letter says the paper
  printed it, and the Club's Thursdays ended.

#### Option 9 - Prison - Eleanor confesses

- Eleanor's coda: she strikes Harrington and leaves without burning the house. Micah's coffee scene at Rose's comes
  first.
- The prison parlour: Eleanor in an inmate's jumpsuit, seated where Micah sits (new sprite), Caleb across the
  table. She confesses her life's crimes and asks for Micah: "He's with his wife now." "It's better this way."
  She was afraid of him and wanted him dead, and can't tell which held the candlestick; Caleb tells her to be sorry
  for every part of her that wanted him dead, she is, for all of it, and he absolves her (see [Theology](docs/theology.md)). At her
  own trial she named the Club and the girls in open court; she tells Caleb so, which keeps the exposure public
  rather than under the seal of confession.
- The last entry is Caleb's: he added her pages to his brother's journal from what she told the court and what she told
  him again plainly afterwards, at her asking. He records that her testimony ended the Club's Thursdays, and that she did what he had not had the courage to do.

#### Option 10 - Outskirts, Eleanor leaves for her peace

- The shoot route with both refusals ("Let's get out of here, quick."), and the mansion burned or Micah took the
  documents.
- The outskirts at night, the car as in ending 2: two car doors slam, and they both get out. She is tired, not
  angry, in a white dress with her pearls: at the gate she took her packed duffle from the Club's car and changed in
  Micah's. She says "I can't go on like this, Micah, I can't be with you. I need ... peace." and walks off down the
  road alone, out of sight. Micah stays by the car.
- The last entry is Micah's, hopeful: he is looking for his own peace (sober, writing to Rose, back at Caleb's
  church on Sundays). She told him the Second Interlude on the road, before she got out of the car.
- Only if Micah took the signed papers, she asks him to take them to the newspapers, not keep them for himself;
  the last entry says he did, and the Club's Thursdays ended. The fire alone gives no mention.

#### Option 11 - Prison, Eleanor visits for the last time

- The shoot route with both refusals, and neither the fire nor the documents.
- The prison parlour, Micah in the jumpsuit, Eleanor across the table in her white dress and pearls. She doesn't go back to
  Theodore. She says "I hope you find your peace, Micah. I'm going to try to find mine, with the help of the
  Lord..." and leaves.
- The last entry is Micah's, hopeful: he looks for his peace behind bars (the Our Father, Caleb's visits, letters to
  Rose). She told him the Second Interlude across the parlour table.

#### Option 12 - Prison - Caleb, after Tony

- Micah killed Tony and turned himself in: from Caleb's church ("(Turn yourself in.)"), or after the Our Father
  having confessed first, including when Eleanor returns to bed in her coda. If she strikes the old man instead, it
  is ending 8 or 9, told from Joliet.
- The prison parlour, Caleb visiting (`caleb_visits`), a year on (caption "Joliet Correctional Center. A year
  later."; the other Joliet endings say six months); the rain has stopped. Micah asks after the old man
  (if he spared him; whether the Club's Thursdays ended depends on the documents) or after Eleanor (if he never got to
  the Gold Coast). He writes every month to Tony's mother in Cicero, and she sends the letters back unopened. Caleb
  brings a crayon drawing from Tommy.
- The last entry is Micah's: a life sentence, the killing written plainly, the documents handed in with his
  confession if he took them, the letters to Tony's mother, Rose visiting on first Sundays. Caleb's note says Eleanor
  came to him months after, told him all of it and asked him to write it in. Daniel keeps the journal for Leo.

#### Option 13 - Outskirts - Out of Chicago, alone

- After the warning shot, the alarm rang and Micah ran. His car stops at the city's edge (`ending_out`): a bell and
  some feet on the stairs were all it took; she's still in that house; he's out of the job and out of the city.
- The journal's last pages are from a rented room in Omaha. Caleb writes care of general delivery and has passed on
  what Eleanor told him in the spring, at her asking; Micah copied it in. He never wrote to Rose. The
  revolver is on the washstand, six in the cylinder, and he only ever needed the one: the last line, then a blank page. Daniel: "...Jesus, Micah."
  Daniel throws the journal back in the trunk.

#### Option 14 - The Harrington kitchen - Caleb's last pages

- After the warning shot, the alarm rang and Micah went in anyway; the Club's two men shot him in the kitchen.
- The last pages are in Caleb's hand: Eleanor told him the rest on the church steps the spring after, and asked
  him to set it down. He sees her at Mass and can do nothing else. The police wrote it down as a burglar shot by the household. "He died walking toward her and not away. That is not repentance. But
  it was the right direction." Caleb says Mass for him. Daniel puts the journal back; no "That's enough of you".

#### Tony's revenge

Tony knows who shot him, and he's the mob. Alive, he follows Micah; dead, Micah carries him:

| Ending | Tony shot, alive | Tony killed |
|---|---|---|
| 1 | They leave Chicago the week after the coffee; they say their promises again at St. Anne's, a Catholic church downstate, and Caleb blesses them. | Not possible. |
| 2, 3 | Out of town or past caring: no mention. | 2: she never asked what took him so long. 3: Tony's on the ceiling too. |
| 4, 5, 6 | A man in the yard says Tony sends his regards; Micah sleeps with his back to the wall. | Tried for Tony too (6: he told the cop himself). |
| 7 | No mention. | Caleb's entry names Tony; if Micah confessed it, only that Tony was found behind the Blue Lantern, and the rest under the seal. |
| 8 | They left Chicago; her letter is sent on by Caleb to the house downstate. | Her letter reaches Joliet; Rose reads it across the visiting-room table. |
| 9 | Micah lives downstate; Tony's men looked for him all winter. | Micah serves his own sentence for Tony. |
| 10 | Micah looks for his peace far from Chicago. | Nobody's come for him; he hears every car that slows down. |
| 11 | Tony sends his regards in the yard. | Tried for Tony too. |
| 12 | Not possible. | The letters to Tony's mother. |

After the warning shot (endings 13 and 14, and any other ending reached by spotting the alarm) Tony wasn't hurt, so
none of the revenge lines play.

### Present

The story ends with the father reading the last entry and commenting briefly. If Micah returned to his wife (ending 1)
or found his faith in prison (endings 6 and 12), or the journal ends on Eleanor's own way (endings 8 to 11), the father
keeps the journal, saying "Maybe Leo would like to read it some day." In endings 7 and 14 he respects Caleb's last pages
and puts the journal back, maybe for Leo in a couple of years. In all other endings (2 to 5 and 13), he throws the
journal back in the trunk. Every ending but 7 and 14 has the "The next morning" caption.

Every last entry also says where the Second Interlude's pages came from, answering Daniel's "Not sure that's
Micah's hand", and Daniel closes on it ("So that's whose hand it was." / "So he never really knew."):

| Ending | Who wrote the Second Interlude, and from what |
|---|---|
| 1 | Micah: Caleb passed it on; she came to Holy Name months later and asked him to (after Eleanor's escape with Caleb: she told Caleb the night he got her out, and asked him to pass it on). |
| 2 | Micah: she told him on the road. |
| 3 | Micah: what the Club's men said in court (she never testified, whether she lived or not). |
| 4 | Micah: she told him across the parlour table. |
| 5, 6 | Caleb's note: he heard it from her after the trial. |
| 7 | Caleb: what the Club's men said in court; or, if Micah shot only himself, she told him after the funeral. |
| 8 | Micah: a letter from her, no return address: at Rose's house if Tony was never shot, sent on downstate by Caleb if Tony survived the shoulder shot, or to Joliet if Micah killed Tony. |
| 9 | Caleb: what she told the court, and told him again plainly afterwards, at her asking (never the confession itself). |
| 10 | Micah: she told him on the road, before she got out of the car. |
| 11 | Micah: she told him across the parlour table, the one time she came. |
| 12 | Caleb's note: she told him months later and asked him to write it in. |
| 13 | Micah: Caleb's letters pass on what she told him in the spring, at her asking. |
| 14 | Caleb: she told him on the church steps the spring after Micah died, and asked him to set it down. |

The First Interlude is always Micah's: she told him during the night at the motel.

### Puzzle pacing and saves

Micah's seventeen added/expanded puzzles are distributed **8 in Act 1, 6 in Act 2, and 3 in Act 3**; Eleanor has one
in each interlude (Puzzles 17 and 18, in Room 507 and backstage at the Club). Puzzle 19 (the motel fire escape),
Micah's eighth in Act 1, takes an item from the motel lobby to use in its back alley. Puzzles 11-15
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
is version 12 (`SaveData.CurrentVersion`); earlier versions are incompatible with the Thursday Club night, the motel
return after the Act 2 office, Room 507's new interlude steps, the fire-escape conversation moving after the First Interlude, Eleanor's weary follow in endings
10 and 11, the motel detour and storm-office room flow, the Eleanor interludes, the bluing moving into the
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

The adventure remains a compact, single-case indie point-and-click: seventeen puzzles for Micah and two for Eleanor, the alley encounter, optional
dialogue, two playable Eleanor interludes and fourteen ending outcomes. The five collect-and-combine locations each sit on a route the story already
took (the hotel stairs, the speakeasy door, the Harrington lead, the masked Club and the mansion entrance)
rather than opening side quests.
Its single-case investigation is closer in scope to [The Blackwell Legacy](https://store.steampowered.com/app/80330/)
than the broader [Kathy Rain (2016)](https://store.steampowered.com/app/370910/),
[Technobabylon](https://store.steampowered.com/app/307580/) or [Unavowed](https://store.steampowered.com/app/336140/).
These are scope comparisons, not measured human completion times. Reading, solving puzzles, optional visits
and replaying endings change duration; accelerated autoplay must not be advertised as adventure length.
