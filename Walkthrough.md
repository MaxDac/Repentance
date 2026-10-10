# Repentance walkthrough

This file describes the story as it is **currently implemented**. To change the game, edit this file:
the difference from the committed version is what still has to be implemented. Anything not
described here (other verbs, flavour lines) is left to the implementation.

## Act 1

### Present day - The attic

- Daniel (the dad) is in the attic, calling his son Leo, but Leo doesn't come over ("In a minute!").
- Daniel can lift the dust sheet and knock over the boxes, spilling the old papers.
- In the suitcase there is a key, but it can't open the large steamer trunk.
- Only the crowbar hidden in the papers from the boxes can open the trunk.
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

#### Eleanor's room at the hotel (room 507)

- New location: a luxurious but lived-in hotel room, ransacked, everything upside down.
- There is a locked desk drawer, which Micah opens using the lockpick from the inventory on it.
- Inside, there's a sheet of paper with the safe combination (key number).
- Micah opens the closet to reveal the safe, and opens the safe using the combination on it.
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
- Behind the little mirror there is a strange symbol, a Celtic triquetra (trinity knot), shown as a full-screen
  image when Micah takes the mirror (and again with the hand on the mirror in the inventory).
- Micah only takes the little mirror; the comb stays in the drawer.
- If the player tries to leave the cell before taking the mirror, Micah says "There is still something to be
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
- Micah has to threaten the librarian with the revolver (use the revolver on him; before asking about the symbol
  Micah refuses to do it). The librarian tells him there's a book describing ancient Celtic rituals and gives it
  to him if he goes away. The scene returns to the map.
- After this the library isn't accessible anymore: selecting it on the map, Micah says "Better not show my face
  there for the time being".
- Leaving the library normally returns to the map.

#### Office

- Leaving the office returns to the map.
- In his office, if Micah opens the book (hand on it in the inventory), he finds some naturalistic rituals he
  doesn't care about, and a little sheet of paper with an address: the Starlight club.
  Opening the book anywhere else, Micah says he'll read it at the office.
- A new location is now available on the map: the club (the Starlight).
- Selecting the club resumes the story from the club, as described below.

#### Temporary storyline (from the Starlight)

The existing temporary storyline strings together the remaining locations:

- **Starlight club** (hall, lounge, stage): in the lounge, Teddy's father, old Theodore Harrington, is watching
  the curtain too. On stage, "Nora" is Eleanor. Teddy owes Moretti, and Teddy's bookkeeper is dead. She gives
  Micah the key to her old suite. The club's street door leads to the street.
- **Aurelian suite 4** (from the street): her diary is hidden in the vanity.
- **Cathedral**: Caleb reads the diary and points Micah to the library.
- **Public library**: Rose, Micah's estranged wife and a librarian, tells him where to look. The ledger behind the
  right-hand shelves holds a motel receipt.
- **Motel room 6**: a map is hidden in the bed.
- **Outskirts**: digging where the map says reveals the bookkeeper's tin box... and Sal is waiting.
  *To be continued.*
