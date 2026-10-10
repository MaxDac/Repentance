# Repentance walkthrough

This file describes the story as it is **currently implemented**. To change the game, edit this file:
the difference from the committed version is what still has to be implemented. Anything not
described here (other verbs, flavour lines) is left to the implementation.

## Act 1

### Present day - The attic

- Daniel (the dad) is in the attic, calling his son Leo, but Leo doesn't come over ("In a minute!").
- Daniel can lift the dust sheet and knock over the boxes, spilling the old papers.
- In the suitcase there is a key, but it can't open the large steamer trunk.
- **Puzzle 1 - Tool tin:** searching the spilled papers uncovers a locked tool tin with a small-key outline
  stamped beside its lock. Use the suitcase key on the tin to take the crowbar. Only that crowbar opens the trunk.
- In the trunk Daniel finds Micah Jones's journal and starts reading it (hand on the journal in the satchel).
  The caption "Chicago, 1927." leads to Micah's office.

### Chicago, 1927

#### Micah's office

- Micah's thoughts, then the conversation with Teddy Harrington III about his missing fiancée, Eleanor
  Harrington; Teddy gives Micah her photograph. At the end of the conversation Teddy walks out of the room.
- Micah can't walk out on Teddy before the conversation is over.
- The top drawer of the desk holds a revolver, the money (one dollar) and a lockpick. Micah takes all three
  (the bottom drawer only holds unpaid bills).
- Micah can't get out of his office without having taken these items.
- The door leads to the Aurelian Hotel lobby.

#### Hotel (Aurelian Hotel lobby)

- Micah's goal is to get into the room Eleanor was staying in before she disappeared.
- The conversations with the concierge and the bellboy stay as they were: the concierge has seen nothing.
- Micah has to bribe the bellboy with the dollar; the bellboy lets him take the staff elevator up to
  Eleanor's room (and mentions the Blue Lantern).
- Before the bribe, the revolving door leads out to the street.
- **Puzzle 2 - Service lift:** after the bribe, the bellboy points to the routing diagram beside the staff door.
  The close-up shows three junctions: at A, upper goes to laundry and lower to B; at B, upper goes to C and
  lower to the kitchen; at C, upper goes to room 507 and lower to the roof. Set **lower, upper, upper** and
  dispatch the lift. A wrong route stays in the lobby and highlights where it went wrong.
  Once solved, the lift works normally on return visits.
- After the bribe, Micah will not depart for the Blue Lantern until he has collected the brass box in
  room 507. Older saves that already passed the hotel without these clues get a temporary Hotel map
  marker to retrieve them; returning to the lobby then leads back to the Act 2 map.

#### Eleanor's room at the hotel (room 507)

- New location: a luxurious but lived-in hotel room, ransacked, everything upside down.
- There is a locked desk drawer, which Micah opens using the lockpick from the inventory on it.
- Inside, there's a sheet of paper with the safe combination (key number).
- **Puzzle 3 - Safe dial:** open the closet to reveal the safe. Hand or use the combination on the safe opens
  its graphical controls, not the safe itself. Enter **R 12 / L 31 / R 7** in the three direction/number rows
  and submit. The paper remains readable; wrong settings can be reset or retried.
- Inside the safe there is a brass box. Micah opens it in the inventory with the hand, revealing:
  - a perfumed business card, blank except for some decorations;
  - a matchbook with the name of the club, the Blue Lantern (next location).
- Leaving the room goes back down to the lobby; the revolving door now leads to the club.

#### Club (the Blue Lantern speakeasy)

- At the door, Sal the guard asks for the password. Micah doesn't know it and has to bribe his way in again.
  If he doesn't cooperate, or makes fun of Sal, he is thrown out and moves directly to the next scene.
- Until Sal lets him in, Sal blocks the way to the bar.
- If Micah bribes Sal, he can speak with Tony the bartender. Tony won't budge, and when the conversation ends he
  calls Micah back: "You know what, I think I don't really like you at all", gestures to Sal (the bodyguard at
  the entrance), and on to the next scene.

#### Street behind the club (the alley)

- New location: the road behind the club, dirty and in the shadow, with only one intermittent street lamp.
- Micah is on his knees, hands on the pavement (new kneeling pose and sprite) after a beating, Sal next to him and
  Tony behind Sal.
- Tony tells him that Eleanor is "hot stuff", that he sent her to a convent of nuns, and that he doesn't know
  anything else. The scene then moves to the convent.

#### Convent

- Two new locations in neo-gothic style: the convent corridor, and Eleanor's cell, really dark, simple and tiny,
  with a bed, a lampstand, a book and a night stand.
- In the corridor, Sister Agatha interrogates Micah: what he's doing here and what he wants with Eleanor.
  She hints at Micah's biblical name as a prophet, and says the exact words "you would be better off finish the
  search now, and never have anything to do with that Jezebel". Micah asks what she means; she retreats, telling
  him that if he really wants, he can have a look at her room.
- In the cell, the night stand has a drawer holding a comb and a little mirror.
- **Puzzle 4 - Waxed mirror:** take the mirror, whose wooden back is covered in wax. Inspecting it and the
  lamp explains that gentle warmth softens wax; searching the bed supplies a borrowed clean cloth.
  Use the mirror on the lamp, then combine the cloth and mirror in either order. Micah wipes away the wax
  and returns the cloth to the bed, revealing a Celtic triquetra (trinity knot).
  The symbol is shown full screen, and can then be inspected again from the inventory.
- Micah keeps the revealed mirror; the comb stays in the drawer.
- If the player tries to leave the cell before revealing the symbol, Micah says "There is still something to be
  found in this room."

#### Road outside the convent

- When Micah gets out, he finds Eleanor there, outside, dressed in black. No one is passing.
- She asks why he's trying to find her and Micah explains; the conversation has tension and attraction.
- The scene ends when Eleanor says "I can't return back there..."

#### Motel room, night

- Inside the motel room, Micah is getting dressed (new dressing sprite for the character) while Eleanor is in the
  bed, under the sheet.
- They say this was probably a mistake and that they should never see each other again. Micah says he won't
  tell anyone where they can find her, and that he will give up the job.

### End of Act 1 - Present day

- Back in the attic, but it's dark and the lamp is on. Leo calls Daniel downstairs for dinner.
- Micah's 1927 inventory is put aside during the present-day scenes and given back when the story returns to 1927.

## Act 2

### Present Day

- The next day, Daniel is back in the attic and returns to reading the journal (hand on it in the satchel).
  The caption "Chicago, 1927." leads to the church.

### Chicago, 1927

#### Outside of the church (cathedral steps)

- Existing location.
- Micah thinks that, even though he couldn't turn her in, he can't think of anything else but her.
- After this thought, he walks up to the doors and enters the church.

#### Inside the church

- Existing location.
- Micah walks over to his brother, Father Caleb, and talks about the situation. During the conversation he tells
  his brother that, right now, he's too far off to be saved.
- Caleb replies that this is crap, no one is beyond salvation, and that thinking that is the Devil's work.
- Micah replies "I'll think about that", then says that coming here was a mistake, and walks out. The scene moves
  to the map.

#### Map of Chicago

- New location: an old map of Chicago, 1927. Micah isn't drawn on the map.
- On the first visit, Micah says "I have to find her again".
- Three locations are available: the Library, the Church (cathedral) and his Office.
- Selecting the Church: Micah refuses to go back ("Coming there was a mistake once already").

#### Library

- At the library, after hours, there is a night librarian (new male character) instead of Rose.
- Micah asks him about the strange symbol; it is shown full screen during the conversation, then the scene
  returns to both Micah and the librarian.
- The librarian asks him where he got that mirror. Micah won't tell him, so the librarian answers that he won't
  tell him anything either.
- **Puzzle 5 - Restricted catalogue:** after the refusal, inspect the desk catalogue. Compare the mirror's
  connected triquetra with the motif plates: select Celtic traditions, whose index lists **A. R. Bell**.
  The author listings identify **Rites of the Old Isles, shelf C-17**. Select that entry.
  The volume is behind locked glass; Micah cannot simply take it from the shelves or ladder.
- Micah has to threaten the librarian with the revolver (use the revolver on him; before asking about the symbol
  Micah refuses to do it, and before the lookup he needs a precise title). He requests the identified book.
  The librarian confirms that it describes ancient Celtic rituals and gives it
  to him if he goes away. The scene returns to the map.
- After this the library isn't accessible anymore: selecting it on the map, Micah says "Better not show my face
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
  Then the MoC will call a brute (another character, in normal dress, tie and jacket) and ask to escort Micah out.

#### Streets of Chicago

- Micah is on the pavement, supine. Narrating voice, which is really Micah's thought, will ask himself what is he doing,
  questions about his life, why he abandoned his wife and son.
- He get up, and the player will be presented with two choices:
  - Go find his wife.
  - Push forward.
- If Micah go find his wife, there will be another location, outside of a terrace house in a row of terrace.
- Otherwise, skip the next part.

#### Outside Micah's wife house

- Micah is outside the house. The player can choose whether to get out of the location, or ring the bell.
- If the player let Micah ring the bell, a door will open and Micah's wife will get out.
- Dialog is tense: the wife asks why he's here, he has no business being here.
- Simulate a dialog where the player has two options: keep pushing for forgiveness, or just leave: keep pushing means that
  the dialog will go on, but the option to leave will be always present.
- There will have to be 5 phrases in which Micah will push the wife for her forgiveness, after which only the leave
  phrase will be available.
- If the player decides to keep pushing at least three times, before going out of the location, the wife will call him
  back with a "Wait!": Micah will turn, a pause of at least 3 seconds, then the wife will say "Don't get into trouble again."
- Then, the wife will close the door, and Micah will go out.

#### Map of Chicago

- Now, also the Club will not be a selectable location, Micah will say "No use returning there now."
- Simulate the other locations, but no use going there, apart from the Convent.

#### Church

- Micah will have to ask his brother about the Club. The brother will be reluctant, and Micah will have to press.
- Micah's brother will tell him that the Convent is probably the best way to ask. He will advise Micah not to go there,
  to give up this foolish search.
  Micah will answer "There's little left for me to do, at this point."
  The brother will say "You know that that's not the case.:
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
- At this point, also the Convent won't be available as a location.

#### Map of Chicago

- Only the Cathedral and the office of Harringhton father will be available.
- The only way forward will be the office of Harringhton, but Micah can go to the church, where the brother can
  tell him not to go forward again.
  You have to save as a state of the game whether, at this point, Micah will return to the church at least once.

#### Office of Harringhton father

- Two new locations, office of Harringhton father and the road below, at night.
- **Road behind the Harrington Building, at night**: a watchman guards the back door and the alley; a trash can,
  a pile of wooden crates and a fire escape whose ladder is pulled up, leading to a lit third-floor window.
  - While the watchman is there, touching the crates or the fire escape gets Micah spotted: the watchman
    shoos him back down the alley, and the back door is locked anyway. Threatening him with the revolver or kicking him is refused.
  - Step 1: use the Blue Lantern matchbook on the trash can. It catches fire, the watchman shouts "Fire!" and
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
  raven, lion, stag. The portrait's heraldic key associates raven with star, lion with sun and stag with moon.
  Open the closet and inspect its false-back panel. Set the three graphical wheels to
  **STAR / SUN / MOON** and submit. Neither a hand nor lockpicks bypasses the lock.
  The double doors reveal the original white mask and cloak.

#### Map of Chicago

- The office of Harringhton father will disappear, and the Club will reappear. The Church will be still available,
  and you'll have to save to the state of the game whether the player will decide to go to the Church and talk
  with Micah's brother once more.

#### Club

- When Micah's enters the Club, he will be dressed with a white mask and a cloak. You will have to generate this 
  new dress and sprite.
- The club will be filled with a number of masked men with the same white mask as Micah (you can use the same model)
  and women dressed with a black mask and succint dresses (even here, you can use the smae model and sprite multiple times).
- When Micah will reach the stage, he will find Eleanor, with the same succint dress but without the black mask, at the 
  center of the stage, with three masked men around her.

### End of Act 2 - Present day, the attic

- Dark again, the father is called for dinner.

### Act 3 - Present day, bedroom

- Father in the bedroom (new location) reading with the nightstand lamp on, wife covered by the blankets, light off on her side.
- Father keeps reading.

#### Club

- Same scene as the end of Act 2.
- One of the masked man turn to Micah, dreesed as himsel "Are you satisfied, now, mister Jones?"
- At this point, everyone turns to him.
- The same man who spoke first continues: "Given that you returned Eleanor to us, you'll be forgiven for this intrusion,
  but this is enough for you."
- At this point, the player has two choices in dialogue:
  - Use the revolver, but this will end with another man coming from behind and knocking him out.
  - Do nothing, and the same man from behind will knock him out nonetheless.
  - The man from behind is Bruno, the brute who escorted Micah out of the Club earlier.

#### Churc, outside

- Micah is supine on the pavement, again, beaten.
- Again, his thoughts will appear as narrating voice, saying what is he doing.
- At this point, the player can have two choices: keep going for Eleanor, or giving up.
- If the player decides to give up, the next location will be again in front of his wife's house, where he will ask her
  whether she would be available some time for a cup of coffe, his ex wife answering why not, and the game jumps
  to the end of act 3 (caption "End of Act Three").
- If the player decide to keep pushing, keep to the next.
- For now, continue with the temporary storyline. 



#### Temporary storyline (from the Starlight)

The existing temporary storyline strings together the remaining locations:

- **Puzzle 9 - Motel room 6, map overlay:** searching the bed yields a county-map fragment; the dresser
  yields a transparent tracing. Combine them in either order to open the alignment close-up.
  Move the tracing on the discrete grid and rotate it in quarter turns until its windmill, creek and fence
  registration marks all match the base map. The asymmetric arrangement has one solution: one clockwise
  turn and offset (6, 3). Correct alignment merges the pieces into the map and reveals the bearing notes.
  A fragment alone cannot unlock the road out of town; cancellation retains both pieces.
- **Puzzle 10 - Outskirts, survey:** use the completed map on the fence post. The notes specify thirty paces
  east of that post and ten paces north of the creek bend. In the north-up survey, each grid step is five paces;
  the fence is at column 2, row 8 and the creek bend at column 5, row 10. Mark column **8**, row **8**.
  This identifies the burial hotspot; digging at a suspicious patch beforehand cannot grant evidence.
  Digging at the identified spot reveals the bookkeeper's tin box... and Sal is waiting.
  *To be continued.*

All ten puzzles are untimed, have repeatable clues and unlimited retries, and preserve useful inventory
items. Close-ups offer reset and close; Escape closes them. Unsubmitted settings reset on reopening.
The satchel has pages so every collected item remains accessible. Completed discoveries in older saves
remain completed; an unfinished new puzzle does not complete merely by saving and loading.
