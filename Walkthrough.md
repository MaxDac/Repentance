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

- Micah's thoughts, then the conversation with Teddy Harrington III about his missing wife, Eleanor
  Harrington; Teddy gives Micah her photograph. At the end of the conversation Teddy walks out of the room.
- Micah can't walk out on Teddy before the conversation is over.
- The top drawer of the desk holds a revolver, the money ($22 cash) and a lockpick. Micah takes all three
  (the bottom drawer only holds unpaid bills).
  The cash is framed as his existing fictional $20 daily fee plus $2 from a previous job, not a claim
  about average PI income. For purchasing-power context, the
  [NBER/BLS manufacturing weekly-earnings series](https://fred.stlouisfed.org/series/M08261USM052NNBR)
  reports $24.37 for October 1927; the $10 Sal bribe is a substantial payment, not an ordinary tip.
- Micah can't get out of his office without having taken these items.
- The door leads to the Aurelian Hotel lobby.

#### Hotel (Aurelian Hotel lobby)

- Micah's goal is to get into the room Eleanor was staying in before she disappeared.
- The conversations with the concierge and the bellboy stay as they were: the concierge has seen nothing.
- Micah has to bribe the bellboy with $1 from his cash; the bellboy lets him take the staff elevator up to
  the fifth-floor linen room next to Eleanor's room (and mentions the Blue Lantern).
- Before the bribe, the revolving door leads out to the street.
- **Puzzle 2 - Service lift:** after the bribe, the bellboy points to the routing diagram beside the staff door.
  The close-up shows three junctions: at A, upper goes to laundry and lower to B; at B, upper goes to C and
  lower to the kitchen; at C, upper goes to the fifth-floor linen room (next to 507) and lower to the roof. Set **lower, upper, upper** and
  dispatch the lift. A wrong route stays in the lobby and highlights where it went wrong.
  Once solved, the lift works normally on return visits.
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
- Inside, there's a sheet of paper with the safe combination (key number).
- **Puzzle 3 - Safe dial:** open the closet to reveal the safe. Hand or use the combination on the safe opens
  its graphical controls, not the safe itself. Enter **R 12 / L 31 / R 7** in the three direction/number rows
  and submit. The paper remains readable; wrong settings can be reset or retried.
- Inside the safe there is a brass box. Micah opens it in the inventory with the hand, revealing:
  - a perfumed business card, blank except for some decorations; Micah remarks that the perfume is strange, but quite attractive;
  - a matchbook with the name of the club, the Blue Lantern (next location).
- Leaving the room goes back across the corridor to the linen room and the staff lift; in the lobby the
  revolving door now leads to the club's front.

#### Rizzo's Flowers, State Street (the Blue Lantern front)

- New location: a florist's on State Street in the rain, closed for the night. The Blue Lantern is behind its
  cold room. A regular waits by the cold-room door with a blue carnation in his buttonhole, and the
  chalkboard in the window reads "Members' buttonholes - blue carnations only".
- The cold-room door has a speaking grille: "A slot at eye height. Somebody inside checks lapels before they
  check faces." Knocking, or offering anything else, gets "No blue in my buttonhole, no hatch."; a white
  carnation gets a hint toward the bluing.
- **Puzzle 12 - Blue carnation:** take a white carnation from the bucket (a nickel in the tin) and the bottle of
  Mrs. Stewart's Bluing from the sidewalk shelf. Combine them in the inventory to dye the carnation blue (the
  bluing goes back on the shelf). Use the blue carnation on the grille: the hatch opens and Micah is let
  through the cold room into the speakeasy. Afterwards the door opens for him directly.
- The street exit on the left leads back to State Street; the speakeasy's steel door leads back out here.

#### Club (the Blue Lantern speakeasy)

- Inside the cold-room entrance, Sal the guard still asks for the password; the blue carnation only got Micah
  past the florist's grille. Micah doesn't know it and can give him $10 as a bribe.
  Micah starts with $22, twice the combined $1 bellboy and $10 Sal payments. The cash remains in his inventory:
  $21 after the bellboy and $11 after Sal. Repeated conversations never charge either bribe again.
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
- Before leaving, Micah pushes up from his hands and knees through a supported crouch to standing.

#### Convent

- Two new locations in neo-gothic style: the convent corridor, and Eleanor's cell, really dark, simple and tiny,
  with a bed, a lampstand, a book and a night stand.
- In the corridor, Sister Agatha interrogates Micah: what he's doing here and what he wants with Eleanor.
  She hints at Micah's biblical name as a prophet, quoting Douay-Rheims Micheas 6:8, and says "you would be better off finishing the
  search now, and never having anything to do with that Jezebel". Micah asks what she means; she retreats, telling
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
- The scene ends when Eleanor says "I can't go back there..."

#### Motel room, night

- Inside the motel room, Micah is getting dressed (new dressing sprite for the character) while Eleanor is in the
  bed, under the sheet.
- They say this was probably a mistake and that they should never see each other again. Micah says he won't
  tell anyone where they can find her, and that he will give up the job.
- Eleanor remains in bed against the pillows, covered by the white sheet. She does not rise.
  The scene then fades back to the attic.

### End of Act 1 - Present day

- Back in the attic, but it's dark and the lamp is on. Leo calls Daniel downstairs for dinner.
- Micah's 1927 inventory is put aside during the present-day scenes and given back when the story returns to 1927.

## Act 2

### Present Day

- The next day, Daniel is back in the attic and returns to reading the journal (hand on it in the satchel).
  The caption "Chicago, 1927." leads to Micah's office.

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
  How his efforts led them to her remains uncertain; the MoC does not confirm a tail.
  Then the MoC will call a brute (another character, in normal dress, tie and jacket) and ask to escort Micah out.

#### Streets of Chicago

- Micah is on the pavement, supine. Narrating voice, which is really Micah's thought, will ask himself what is he doing,
  questions about his life, why he abandoned his wife and son.
- His recovery is shown through sitting, a supported crouch, and standing rather than an instantaneous pose swap.
  The player is then presented with two choices:
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
  On "Wait!" a framed close-up panel of Rose at her door pops up over the scene, in the same style as Eleanor's stage
  close-up; the dialogue moves to the panel's bottom edge, and the panel is removed after "Don't get into trouble again.",
  before the door closes.
- Rose makes clear that forgiveness is not something Micah can demand; the callback is concern, not absolution.
  Keep her third-appeal reply: "Forgiving is easy, Micah. Forgetting is the part you keep asking for."
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
  Keep the choice "They have her, Caleb. If you know anything, tell me." Micah does not claim Caleb hid her
  in his sacristy; the established refuge is the convent.
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
  - Look at the wall map: "Map of the Loop, pins for every address the paper ever printed." Use the mended
    clipping on it: Micah pins the Harrington Building, LaSalle Street (flag `harrington_located`).
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
- Choosing the Club puts Micah, masked, in the Club vestibule; there is no going back to the map from there. The
  back door on the street is refused too ("Through the front tonight, with the procession.").

#### Club vestibule

- A small entry hall: a brass plaque, a coat-check counter, a rack with three hooded cloaks and a locked inner
  door with a brass card slot. The street door won't let Micah back out.
- **Puzzle 14 - The sealed summons:**
  - The plaque reads: "Present your summons, sealed by the first of the procession."
  - Take the stick of sealing wax from the coat-check counter. Cold wax on the invitation is refused ("Hard as a
    church pew. Needs a flame.").
  - Combine the matchbook with the sealing wax: soft wax (the matchbook is never consumed - it is needed again
    in Act 3). Combine the soft wax with the invitation: the waxed invitation.
  - Each cloak on the rack (lion, stag, raven) has a signet ring in its pocket; Micah only holds one at a time,
    taking another hangs the previous one back up. The invitation's procession is raven, lion, stag, so the
    raven is first: lion or stag on the wax is refused.
  - Combine the raven signet with the waxed invitation: the sealed invitation (the ring goes back in its cloak).
  - Use the sealed invitation on the door slot (a plain or waxed-but-unsealed invitation is refused): the door
    opens (flag `vestibule_passed`) and Micah walks into the Club hall. The sealed card is returned to him and is
    what the master of ceremonies wants to see inside.

#### Club

- When Micah's enters the Club, he will be dressed with a white mask and a cloak. You will have to generate this 
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

### End of Act 2 - Present day, the attic

- Dark again, the father is called for dinner.

### Act 3 - Present day, bedroom

- Father in the bedroom (new location) reading with the nightstand lamp on, wife covered by the blankets, light off on her side.
- Father keeps reading.

#### Club

- Same scene as the end of Act 2, with the close-up panel of Eleanor framed over the stage again.
- The stag-masked leader turns to Micah, dreesed as himsel "Are you satisfied, now, mister Jones?"
- At this point, everyone turns to him.
- The same man who spoke first continues: "Given that you returned Eleanor to us, you'll be forgiven for this intrusion,
  but this is enough for you."
- The close-up panel is removed, then the player has two choices in dialogue:
  - Use the revolver, but this will end with another man coming from behind and knocking him out.
  - Do nothing, and the same man from behind will knock him out nonetheless.
  - The man from behind is Bruno, the brute who escorted Micah out of the Club earlier.
- Micah's masked, cloaked collapse is shown before the blackout on either choice.

#### Church, outside

- Micah is supine on the pavement, again, beaten.
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

- The player returns to the office, and is seated behind his desk; narrating voice which describes his thoughts.
- After the opening desk line, he reflects: "Thanks to my efforts, he said. How'd they find her through me?
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
  Sal out, then use the revolver on him to knock him down. Only then knock on the back door to face Tony.
  Trying the noise while the lamp is lit or knocking while Sal is inside cannot bypass the sequence.
- Once the bartender is out, Micah automatically starts the dialogue with the revolver out, asking how to get to
  Eleanor.
- The bartender tells him to bug off, these people are really dangerous, and he'd be better off with a bullet in his skull.
- At this point, the player must choose between fire the revolver on the leg, or to walk away, because it's not worth it.
  The option to walk away is available only if Micah carries his wedding ring and returned to Caleb before Harrington's
  office, before the masked Club visit, or through the Act 3 office route. The cross is not required here.
- If the player walks out, he's going to his wife's house (caption *End of Act Three*).
- If he's firing at the leg, you have to create a new model for the bartender supine, with a drop of blood from the leg.
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
- The kitchen is dark and quiet. The green baize door to the house is **bolted from the house side**: Micah
  says so and notes that houses like this always kept another way up for the deliveries. In the floor by
  the table is a cellar trapdoor with an iron ring.
- **Puzzle 15 - The wine cellar:** the trapdoor leads down into the Harrington wine cellar, pitch black.
  Micah can make out a storm lantern on a hook and some delivery crates; the stair at the back can't be
  climbed blind. Take the lantern (empty) and look at/take from the crates: one sloshes, a can of
  kerosene. Combine **lantern + kerosene** (filled lantern), then **filled lantern + matchbook** (lit
  lantern; the matchbook is kept). Trying the matchbook on the empty lantern gets "Dry wick. Needs fuel
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
  Skipping the puzzle must retain the prison endings when the mansion does not explode.
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
    - Micah has 2 turns to convince her, otherwise Micah would run away because he hear rumors from the other door.
    - If Micah manages to convince her, they both are in the kitchen: here, Micah ahs the possibility to run the gas
      and make the mansion explode.
    - If he doesn't manage, he's alone in the kitchen, and can make the mansion explode either way.
    - During the escape the way back is shut: the baize door and the cellar trapdoor both get "Not back in
      there. Somebody's on the stairs by now.", so the bedroom confrontation can't be replayed.
  - The choice not to shot the old man is accessible at this point only if Micah insisted for forgiveness with his wife,
    **and** made a qualifying church return, **and** carries both the wedding ring and cross pendant. Insisting means
    at least three forgiveness appeals. If this is the case, Micah gets out saying "Yeah... I'm done with this. All of it."
    and the scene skips to *End of Act 3*.

### End of Act 3

- Here, there are multiple endings, depending on the choices made in the previous selection:

#### Option 1 - Outside Micah's wife

- Previously used location
- This ending is accessible if Micah refuses to go forward at any point, either outside of the Church, or if he refuses
  to shoot the bartender, or the old man.
- The Act 2 forgiveness visit and Act 3 church-steps return stay unrestricted. Only the later return choices gain the
  progressively stricter requirements above; the other endings are unchanged.
- Micah is outside, rings the bell, and asks his wife whether she would accept his previous invitation ot take a coffee with him.
- He offers coffee without claiming she owes him forgiveness or reconciliation. The renewed vows in the journal
  happen later, after he has begun showing change rather than merely promising it.
  Keep Micah's "Nothing you owe me." and the journal's "A year since that cup of coffee."
- In this case, the journal ends with Micah back with his wife, renewing the vows at his brother's Church.

#### Option 2 - Outskirts, with Eleanor

- Previously generated location
- This ending is accessible only if Micah manages to convince Eleanor in the Harrington mansion, and manages to make it explode
  or finds the documents in the mansion.
- They both say goodbye to Chicago, and get into a car, which has to be generated in the location.
- In this case, the journal ends with Micah saying that he's now an alcoholic following Eleanor betraying him multiple times.

#### Option 3 - Outskirts, without Eleanor

- Previously generated location
- This ending is accessible if Micah didn't manage to convince Eleanor, and Micah either finds the documents in the mansion
  or make it explode.
- Her fate remains unknown during escape; there is no evacuation narration.
- Only if the mansion exploded and Eleanor refused to follow, the outskirts scene begins with "The next morning"
  and does not describe the car door slamming in the dark. Micah reads: "The morning paper lists the dead.
  Eleanor Harrington. There it is, in black and white." He admits: "I told myself I was saving her.
  I left her there and lit the fuse." The fuse is figurative; the mechanism remains gas and a candle.
  "They know who died. They don't know what I did." replaces the same-night orange-sky/secrecy line.
- Documents-only escape has no newspaper death report. With Eleanor following, the outskirts scene stays
  that night and she survives. Keep "She wouldn't come with me. Even with him on the carpet and the whole Club
  on its way." on both alone routes.
- You have to generate the car in this case also, Micah gets out of the car.
- In this case, the journal ends with Micah shooting himself, and the last entry is stained with alcohol and blood.

#### Option 4 - Prison - With Eleanor

- You have to generate prison parlatory, where the prisoners speaks with whoever came to talk to them.
- This ending is accessible if Micah managed to convince Eleanor, but neither made the mansion explode nor found the
  signed documents.
- Micah in this case has a jumpsuit for an inmate, you have to generate the model.
- Micah and Eleanor seat at a table, one in front of the other, they talk, and Micah says that he maintained her out of
  jail, and she answers that she's grateful, but she has to move forward, and that she will return to Harrington son.
- In this case, the journal ends with Micah hanging himself, the last entry is a goodbye letter for his wife and son.

#### Option 5 - Prison - With brother

- You have to generate prison parlatory, where the prisoners speaks with whoever came to talk to them.
- This ending is accessible if Micah did not manage to convince Eleanor, and neither made the mansion explode nor
  found the signed documents.
- Micah in this case has a jumpsuit for an inmate, you have to generate the model.
- Micah and his brother seat at a table, one in front of the other, the brother asks how's he doing, he reluctantly
  says that his wife doens't want to have anything to do with him, and that Eleanor keeps living with Harrington son.
- In this case, the journal ends with Micah hanging himself, the last entry is a goodbye letter for his wife and son.

### Present

The story ends with the father reading the last entry and commenting briefly. If Micah returned to his wife, the father
keeps the journal, saying "Maybe Leo would like to read it some day." In all other endings, he throws the journal back
in the trunk.

### Puzzle pacing and saves

The fifteen added/expanded puzzles are distributed **6 in Act 1, 6 in Act 2, and 3 in Act 3**. Puzzles 11-15
are collect-and-combine puzzles in five extra locations: the Aurelian linen room and Rizzo's Flowers (Act 1), the
Tribune morgue and the Club vestibule (Act 2), and the Harrington wine cellar (Act 3). Each asks Micah to gather
items in that location, join them in the satchel and use the result to continue. The matchbook is only ever a
flame: no combination consumes it, so it is still in the satchel for the cellar lantern.
The final act also retains its existing three-step alley encounter. The alarm gives the pursuit route
an interactive infiltration beat; the optional index provides investigation before the confrontation.
Giving up or reconciling never requires completing a pursuit-route puzzle. The obsolete temporary
motel map and burial survey are not part of the completed Act 3.

All fifteen puzzles are untimed, have repeatable clues and unlimited retries, and preserve useful items.
Close-ups offer reset and close; Escape closes them. Unsubmitted settings reset on reopening.
The satchel has pages so every collected item remains accessible. The current save format
is version 6; earlier versions are incompatible with the five added locations and the rerouted lift,
Blue Lantern entrance, Harrington lead, masked Club entrance and mansion entrance. Completed discoveries in
compatible saves remain completed, using independent markers
for the original and Act 3 puzzles. Saving/loading never completes an unfinished new puzzle.

### Scripture and adventure scope

Sister Agatha's direct quotation uses [Douay-Rheims (Challoner), Micheas 6:8](https://drbo.org/chapter/38006.htm):
"I will shew thee, O man, what is good." Micah recalls "love mercy".
Caleb retains his original counsel, warning and contrite-heart paraphrase, without the added exact quotations.
His prodigal-son account paraphrases [Luke 15:17-20](https://drbo.org/chapter/49015.htm), not a direct quotation. Religious objects remain
reminders; Rose's response is her own choice. Tragic endings are not declarations that repentance is impossible.

The adventure remains a compact, single-case indie point-and-click: fifteen puzzles, the alley encounter, optional
dialogue and five ending outcomes. The five collect-and-combine locations each sit on a route the story already
took (the hotel stairs, the speakeasy door, the Harrington lead, the masked Club and the mansion entrance)
rather than opening side quests.
Its single-case investigation is closer in scope to [The Blackwell Legacy](https://store.steampowered.com/app/80330/)
than the broader [Kathy Rain (2016)](https://store.steampowered.com/app/370910/),
[Technobabylon](https://store.steampowered.com/app/307580/) or [Unavowed](https://store.steampowered.com/app/336140/).
These are scope comparisons, not measured human completion times. Reading, solving puzzles, optional visits
and replaying endings change duration; accelerated autoplay must not be advertised as adventure length.
