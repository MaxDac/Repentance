// REPENTANCE - all game dialogue.
// Lines are "SPEAKER: text" where SPEAKER is an actor/voice id in upper case. MICAH and DANIEL are the
// player character (DANIEL in the present-day prologue). Unprefixed lines are spoken by the player.
// "THOUGHT: text" is Micah's journal narration in the 1927 scenes: first person, present tense, shown in faded
// ink at the top of the screen. Use it for his inner monologue; anything said aloud stays MICAH.
// Choice text is spoken by the player unless it starts with "(".
// Room scripts start conversations with DialogueManager.Instance.Talk("knot").

EXTERNAL has_item(id)
EXTERNAL has_flag(flag)
EXTERNAL knows_note(id)
EXTERNAL cash_amount()
EXTERNAL give_item(id)
EXTERNAL take_item(id)
EXTERNAL set_flag(flag)

VAR pushes = 0
// Eleanor's persuasion (docs/eleanor-persuasion.md): every line scores by type; the total after four turns decides.
VAR persuade_score = 0
CONST PERSUADE_POSSESSIVE = 4
CONST PERSUADE_RATIONAL = 2
CONST PERSUADE_POSITIVE = 1
CONST PERSUADE_CLUMSY = 0
CONST PERSUADE_THRESHOLD = 10

-> END

// ---------------------------------------------------------------- PROLOGUE: THE ATTIC (present day)

=== attic_intro ===
DANIEL: Leo! LEO! Come up and give me a hand!
LEO: In a minute!
DANIEL: That's what you said an hour ago.
DANIEL: "Sold as is, including contents." I should have asked what the contents were.
DANIEL: Three generations of somebody else's junk. Right. One box at a time.
-> END

=== leo_call ===
DANIEL: Leo!
LEO: Whaaat?
+ [Come up here and help me sort the attic!]
    LEO: I'm in the middle of a match! Five minutes!
    DANIEL: Five minutes. Sure. See you at Christmas.
+ [The old owners left a lot of stuff up here. Could be treasure.]
    LEO: Unless it's a gaming PC, I'm good.
    DANIEL: It's mostly tax returns and a creepy mannequin.
    LEO: Then I'm good.
+ [Did you finish your homework?]
    LEO: ...
    LEO: Sorry, can't hear you! Bad signal!
    DANIEL: We live in the same house.
+ [(Never mind)]
- -> END

=== journal ===
DANIEL: "Property of Micah Jones. Private Investigator. Chicago."
DANIEL: The first entry is dated October 1927. The ink has faded, but the handwriting is steady.
DANIEL: "If you're reading this, I'm either dead, or I finally found the nerve to confess."
DANIEL: "Either way, somebody ought to know what happened to Eleanor Harrington. And what I did about it."
DANIEL: "God forgive me. I'm not sure I ever will."
DANIEL: ...Leo! You've GOT to see this!
LEO: In a minute!
DANIEL: Fine. More for me.
-> END

=== dinner_call ===
LEO: DAD! DINNER!
DANIEL: ...Dinner? It's dark out already.
LEO: Mom says if you're not down in two minutes, your plate goes to the dog!
DANIEL: Coming! I'm coming.
DANIEL: "Were you looking for someone?" ...You found her, Micah. Now what?
-> END

=== attic_act2 ===
DANIEL: Morning, attic. Morning, dress form.
DANIEL: I barely slept. Kept seeing a man on his knees in an alley, a hundred years ago.
DANIEL: Right. Where were we, Micah?
-> END

=== journal_act2 ===
DANIEL: The next entry. Same steady hand, but the ink is darker. Pressed harder into the page.
DANIEL: "I told myself I was done with the Harringtons. Chicago had other plans."
DANIEL: Wait. These first pages aren't about him at all. "What follows, she told me at the motel, in the dark. I wrote it down the next morning, as near to her words as I could."
-> END

// ---------------------------------------------------------------- FIRST INTERLUDE (Eleanor, before Micah's Act 2)
// Micah's journal, written from what Eleanor told him at the motel: THOUGHT is his third-person narration of her
// night, ELEANOR is the player. The choices only colour the scenes, except Agatha's night visit (interlude_agatha_night).

=== interlude_aurelian ===
THOUGHT: Tuesday night, the Aurelian. Room 507. The bed turned down, the dresses on their hangers, the chair squared to the desk.
THOUGHT: She left it neater than she ever kept that marriage. The mess came after, when Theodore's men came looking for what she'd hidden.
THOUGHT: She packed one bag, light enough to run with. The rest of what she packed was insurance: if the Club ever dragged her back, the Club would go into the morning paper with her.
THOUGHT: Not on her; they'd search her first. In the room, in her name, behind a dial Theodore's men couldn't count to.
ELEANOR: The box. The safe. The drawer. Then a telephone call, and the door. Don't look back, Ellie.
-> END

=== interlude_rizzo ===
ELEANOR: Operator? Rizzo's Flowers, on State Street. Yes. I'll hold.
RIZZO: Rizzo's. We're closed.
ELEANOR: Not to me, you're not. This is the lady who sends lilies every Thursday.
RIZZO: Lotta ladies send lilies. Who's askin'?
+ [Somebody who always paid her bills on time.]
    RIZZO: Then you got the wrong number, lady. Nobody pays on time.
    ELEANOR: I did. Ask Tony.
+ [Tell Tony it's Eleanor. He'll know.]
    RIZZO: ...Hold on.
    THOUGHT: She said she could hear the jazz through the receiver, and a glass breaking, and a man laughing at it.
+ [Someone who knows what you keep under the roses.]
    RIZZO: Lady, you got a smart mouth for a telephone.
    ELEANOR: It's the only part of me that ever got me anywhere.
- RIZZO: Tony says sit tight. Somebody'll come up for you.
ELEANOR: The service stairs. Tell them to use the service stairs.
-> END

=== interlude_sal ===
THOUGHT: They came up the service stairs, like she'd asked. Sal from the Blue Lantern door, and a hood with a broken nose she never got the name of.
SAL: Mrs. Harrington. Tony sends his regards. Keep your head down and walk like you're bored.
ELEANOR: I've had years of practice.
THOUGHT: The bellboy saw them go: a lady between two large men, going down the back way like the guest of honour. He told me they were escorting her. She told me she'd never been so sober in her life.
-> END

=== interlude_tony ===
BARTENDER: Mrs. Harrington. In my bar, at this hour, with the whole North Side looking for you.
ELEANOR: Hello, Tony. You still water the gin?
BARTENDER: Only for people I like. What do you want?
+ [A place to hide. Somewhere they won't think to look.]
    BARTENDER: There ain't a place in this city they won't look. There's only places they won't go.
+ [A drink first. Then a place to hide.]
    BARTENDER: The drink's on the house. The hiding'll cost you.
    THOUGHT: She told me she didn't touch it. She just held the glass, to have something to hold.
+ [I need to disappear, Tony. Tonight.]
    BARTENDER: People don't disappear, lady. They just end up someplace nobody thought to dig.
- BARTENDER: Who's after you? The husband?
+ [The husband's the least of it.]
    BARTENDER: That's what I was afraid of.
+ [His father.]
    BARTENDER: ...Yeah. I figured you'd say that.
+ [(Say nothing.)]
    BARTENDER: Fine. The less I know, the longer I live.
- BARTENDER: The convent. Up on the North Side, behind the iron spikes.
BARTENDER: Funny business up there, see? Father Caleb pulls up after dark with a flivver full of skirts, young ones, and drives home alone. What kind of racket a padre's runnin', I don't wanna know.
BARTENDER: But it's the one joint in this town the Club won't touch. They'll turn every flop and speak inside out lookin' for you. Not them walls.
THOUGHT: She told me she knew where some of those girls had come from. She'd brought a few of them to the Club herself.
ELEANOR: A convent. Me.
BARTENDER: You want to stay alive, or you want to stay you? Pick one. Sal'll drive you. Ring the bell and keep your trap shut.
ELEANOR: One more thing, Tony. If the Club ever gets me back, you'll hear. You hear everything.
BARTENDER: And?
ELEANOR: Then you pick up a telephone. Not the cops; half of them drink here. The Tribune city desk.
ELEANOR: You say: Room 507, the Aurelian. The drawer, then the safe. You don't give your name.
BARTENDER: What's in the safe?
ELEANOR: Their Club. Enough to get a reporter as far as your bar, and you as far as the old man's throat.
BARTENDER: A dead lady's insurance. ...Fine. I hope I never have to make that call.
THOUGHT: She told me all of it that night at the motel. She didn't know the safe was already empty. I'd emptied it myself.
THOUGHT: She said Tony wouldn't take her money. That frightened her more than anything else he said.
-> END

=== interlude_agatha ===
NUN: Another one at the door after Compline. They always come at night, the poor lambs. Let me look at you.
NUN: ...No. I know that face. I know that perfume. A Jezebel from that hideous Club, come to hide her paint behind our walls.
+ [I'm not here to sin, Sister. I'm here to hide.]
    ~ set_flag("interlude_agatha_sorry")
    NUN: Every sinner says that. It's the oldest prayer there is.
+ [Jezebel was a queen, Sister. I've only been a wife.]
    ~ set_flag("interlude_agatha_proud")
    NUN: And the dogs ate her in the street. Mind your tongue in this house.
+ [(Say nothing. Lower your eyes.)]
    NUN: Silence. Well. That's a start. We'll see how long it lasts.
- NUN: Mother Superior, if you must call me anything. Sister Agatha, to the Lord.
NUN: The last cell on the left. Lights out at nine. You will not leave it until you're told.
~ set_flag("interlude_agatha_met")
THOUGHT: She told me Agatha watched her all the way down that corridor. Not like a nun watches a sinner. Like a cat watches a door.
-> END

// The night visit: Agatha believes she has come to hear a confession; the hour says otherwise. Eleanor sees the old
// Club trick would buy her the convent. Telling the truth is saved (eleanor_refused_abbess, one of the two refusals
// the endings 8-11 need); seducing her ends with Agatha cursing her. Either way nun_threat2 has Agatha confess in Act 2.
=== interlude_agatha_night ===
THOUGHT: Past midnight. A candle under the door, then the door. Agatha, in her night veil, with the candle in both hands like she was carrying it to an altar.
NUN: You're awake. I thought you would be. A troubled soul doesn't sleep. I've come to hear you, child, if you want to be heard.
{
- has_flag("interlude_agatha_proud"):
    NUN: A queen, you said. Queens have the most to confess. I've been thinking of it ever since.
- has_flag("interlude_agatha_sorry"):
    NUN: Here to hide, you said. Nobody hides from God. But you might lay it down, here, tonight.
- else:
    NUN: You lowered your eyes to me in the corridor. I couldn't stop thinking of it. Of you, alone in here.
}
ELEANOR: It's past midnight, Mother. The priest hears confessions on Saturdays.
NUN: The priest isn't here. I am. Let me help you carry it.
THOUGHT: She set the candle on the night stand and stopped a step short of the cot, closer than a confessor stands. Her hands didn't know where to go.
THOUGHT: Eleanor told me she saw it straight away. Not a nun's look. A lonely woman's, one who'd never let herself name what she wanted.
THOUGHT: And she saw what it was worth. One night, the way the Club had taught her, and Agatha would keep her behind these walls as long as she liked. No Club, no old man. Nobody comes into a convent.
THOUGHT: She'd bought every door she'd ever had that way. This one would have been the easiest.
+ [(Tell her the truth. All of it.)]
    ~ set_flag("eleanor_refused_abbess")
    THOUGHT: She told me she put the thought away like a knife back in a drawer. Then she tried to tell Agatha what she was running from. It wouldn't come.
    ELEANOR: Mother, I... there's a... a club. In the city. I...
    ELEANOR: They put me on a stage. Painted. I'm... I'm the one they paint, and then I...
    NUN: I know... I know enough of that diabolical club, child. Hush. You needn't say another word.
    THOUGHT: Agatha took her hand. Then her face, both hands, the way you'd hold something you were afraid to drop. And she leaned in.
    ELEANOR: No, Mother. Not you too.
    NUN: I...
    NUN: What have you... You did this. You put this in my head, with your painted mouth and your stories. Out of my house at first light.
    THOUGHT: She took the candle and left her the dark. Eleanor said she slept like a child, after. The first time in years.
+ [(Seduce her. One night, and the convent is yours.)]
    THOUGHT: So she did what she knew. She let her voice go small and took Agatha's hand, and held it a moment too long.
    ELEANOR: Nobody's held my hand since I was a girl, Mother. Don't let go. Please.
    NUN: I won't. Hush, now. I won't.
    THOUGHT: The candle shook. Agatha didn't let go. Eleanor said she'd done this a hundred times, for a hundred men, and she knew to the second when it would turn.
    NUN: No.
    NUN: No! Begone, Satan! You are no girl. You are a demon in a girl's skin, sent here to try me!
    ELEANOR: I didn't send for you, Mother. You came.
    NUN: Out of my house at first light. And may God have more mercy on you than I can.
    THOUGHT: She told me she laughed, after the door slammed. Then she cried, and she didn't know which of them she was crying for.
- -> END

=== interlude_motel_window ===
THOUGHT: She took a room at the flophouse down the hill from the convent, the one with the sign that buzzes. From the first floor window you can see the convent door. She watched it for four days.
THOUGHT: On the fourth evening, a man with a split lip and a day-old limp came up that road in the rain and rang the bell. Me.
ELEANOR: Well. Theodore sent somebody after all. And he sent a sad one.
THOUGHT: She watched them let me in. She didn't need Agatha to tell her who I was; Theodore only ever hired one kind of man.
THOUGHT: She watched me come out again, alone, and stand in the middle of the road and light a cigarette like a man at the end of a rope.
ELEANOR: Coat. Gloves. And a face that's run out of places to look.
THOUGHT: Then I came down the hill, and she heard me through the floor, leaning on the clerk. She heard him tell me nobody goes up.
THOUGHT: A minute later she saw me in the alley under her window: up on a fruit crate in the rain, fishing for the fire-escape ladder with the clerk's umbrella.
ELEANOR: Well, look at that. A man who won't take no from a desk clerk.
THOUGHT: So she opened the window and stepped out on the fire escape, into the rain, and waited while I climbed. That was the first test she ever set me, and the easiest.
-> END

// ---------------------------------------------------------------- OFFICE

=== teddy ===
{has_flag("teddy_briefed"): -> teddy.again}
TEDDY: You're Jones? The detective?
MICAH: Depends who's asking. And whether they're paying.
TEDDY: Theodore Harrington. The Third. Harrington Steel. Perhaps you've heard of it.
MICAH: I've heard of steel.
TEDDY: My wife, Eleanor, has... misplaced herself. Three days ago.
- (opts)
* [What happened?]
    TEDDY: We dined at the Aurelian on Tuesday. I stepped away for a moment.
    TEDDY: A brief conversation with a charming young lady from the coat check. Purely business.
    MICAH: Uh-huh. Since when is the coat check a business meeting?
    TEDDY: When I returned, Eleanor was gone. So was her coat. Rather ironic, I suppose.
    -> teddy.opts
* [Why not go to the police?]
    TEDDY: The police talk to newspapers. Newspapers talk to Father's shareholders.
    TEDDY: Discretion, Mr. Jones. That's what I'm paying for.
    -> teddy.opts
* [Do you have a picture of her?]
    -> teddy.photo
* [I'll take the case.]
    {not has_item("photo"):
        TEDDY: You'll need this, I imagine.
        -> teddy.photo_then_case
    }
    -> teddy.take_case
= photo
TEDDY: Naturally.
~ give_item("photo")
THOUGHT: Dark hair, pale eyes, a mouth that's keeping a secret. The camera loved her. I'd bet Teddy never did.
TEDDY: Don't crease it. The sitting alone cost more than your furniture.
-> teddy.opts
= photo_then_case
~ give_item("photo")
THOUGHT: Dark hair, pale eyes, a mouth that's keeping a secret. The camera loved her. I'd bet Teddy never did.
-> teddy.take_case
= take_case
TEDDY: Splendid. Your usual fee, plus a bonus when she's home.
MICAH: Twenty a day. Plus expenses.
TEDDY: Expenses. How quaint.
TEDDY: Start at the Aurelian. Discreetly. I have a club to get to.
~ set_flag("teddy_briefed")
-> END
= again
TEDDY: Well? Why are you still here? The Aurelian, Jones. Chop chop.
-> END

// ---------------------------------------------------------------- LOBBY

=== concierge ===
CONCIERGE: Good evening, sir. Welcome to the Aurelian.
- (opts)
* [I'm looking for a woman.]
    CONCIERGE: Sir will find the Aurelian is not that sort of establishment.
    -> concierge.opts
* {has_item("photo") or knows_note("eleanor")} [Have you seen this woman?]
    CONCIERGE: The Aurelian prides itself on discretion, sir.
    CONCIERGE: I make a point of seeing nothing. And of remembering less. That is why they pay me.
    -> concierge.opts
* [Nice place.]
    CONCIERGE: Thank you, sir. The marble is Italian. The guests, I'm afraid, are not what they used to be.
    -> concierge.opts
+ [(Leave)]
    CONCIERGE: Do enjoy your evening, sir. Elsewhere, ideally.
    -> END

=== bellboy ===
{has_flag("knows_lantern"): -> bellboy.after}
{has_flag("bellboy_wants_money"):
    BELLBOY: Back again, mister? Memory's still for sale.
- else:
    BELLBOY: Help you, mister? Bags? Directions? Gossip?
}
- (opts)
* [Gossip?]
    BELLBOY: Gossip costs extra. Everything costs extra in this joint.
    ~ set_flag("bellboy_wants_money")
    -> bellboy.opts
* {has_item("photo") or knows_note("eleanor")} [Seen this lady?]
    CUE: show_photo
    BELLBOY: Maybe I have, maybe I haven't. My memory works better when it's been fed.
    CUE: pocket_photo
    ~ set_flag("bellboy_wants_money")
    -> bellboy.opts
* [How's business?]
    BELLBOY: Swell. Rich folks tip in advice. "Buy steel, kid." With what?
    -> bellboy.opts
+ [(Leave)]
    BELLBOY: I'll be here. I'm always here.
    -> END
= after
BELLBOY: Back door, Tuesday night, two big fellas either side of her. Nobody saw nothin'. Including me.
{has_flag("staff_elevator"):
    BELLBOY: And the lady's room is 507. Staff door, service elevator. You didn't hear that either.
- else:
    BELLBOY: Her room's another dollar, mister. The first one only bought my memory.
}
-> END

=== bellboy_tip ===
{has_flag("staff_elevator"): -> bellboy.after}
{has_flag("knows_lantern"): -> bellboy_tip.room}
{cash_amount() < 1:
    MICAH: His memory's for sale, and I'm a dollar short.
    -> END
}
BELLBOY: Now you're speaking my language, mister.
MICAH: One dollar. For your memory.
BELLBOY: The dame in the picture? Tuesday night. Late. I was out back having a smoke I ain't allowed to have.
BELLBOY: Service door opens, and out she comes. Big fella either side of her. Broken nose, cheap suit, expensive cigar.
BELLBOY: Not dragging her, mister. Escorting her. Like she was the guest of honour and the party didn't want her to leave.
MICAH: Who were they?
BELLBOY: The kind of fellas who make sure nobody saw 'em. Nobody did. Car with no lights, gone down the alley. That's all my memory's got.
THOUGHT: Escorted, not dragged. Either she went quietly, or she knew exactly where she was going.
~ set_flag("knows_lantern")
MICAH: Her room. The one she had Tuesday. I want a look.
BELLBOY: That's another dollar, mister. The first one bought my memory. The back way costs extra.
MICAH: Everything costs extra in this joint.
BELLBOY: Now you're learning.
-> END
= room
{cash_amount() < 1:
    MICAH: The back way costs a dollar, and I'm a dollar short.
    -> END
}
MICAH: Another dollar. For the back way.
~ set_flag("bellboy_room_paid")
BELLBOY: Front desk won't give you the time of day, never mind a key. That dollar buys the back way.
BELLBOY: Staff door's by the palm. The service cage runs a maze of shafts and laundry chutes behind the walls. Chart's on the panel.
BELLBOY: Every floor's got a linen room, and they all look the same. You want the fifth floor, the one right next to 507.
BELLBOY: Rooms count up west to east, mister. 501's by the stairs. 513's by the fire escape. Night maid bolts the corridor door, though.
BELLBOY: Fair warning, mister: somebody already turned it over. And it wasn't housekeeping.
~ set_flag("staff_elevator")
-> END

// ---------------------------------------------------------------- SPEAKEASY

=== sal ===
{has_flag("sal_passed"): -> sal.after}
SAL: ...
SAL: Password.
- (opts)
* {has_flag("knows_password")} [Moonshine.]
    SAL: ...
    SAL: Who gave you that?
    MICAH: A lady who knows the place better than you'd think.
    SAL: Huh. Go on in. Keep your hands where I can see 'em.
    ~ set_flag("sal_password")
    ~ set_flag("sal_passed")
    -> END
* [Swordfish?]
    SAL: No.
    -> sal.opts
* [Open sesame?]
    SAL: Get lost.
    -> sal.opts
* [All right. I don't know the password.]
    -> sal.bribe
+ [(Leave)]
    -> END
= bribe
SAL: Then you don't know nothin', and nothin' don't get in.
MICAH: Matchbook says the Blue Lantern. Doesn't say a word about a password.
SAL: Matches are free. The door ain't.
- (bribe_opts)
* {cash_amount() >= 10} [(Give him ten dollars)]
    MICAH: Ten dollars. Maybe that'll open the door.
    SAL: ...
    SAL: That'll do.
    SAL: Go on in. Keep your hands where I can see 'em.
    ~ set_flag("sal_bribed")
    ~ set_flag("sal_passed")
    -> END
* [What's the matter, big fella? Forgot it yourself?]
    SAL: ...
    SAL: You're a funny guy. I like funny guys. I like 'em out back.
    ~ set_flag("thrown_out")
    -> END
* [I don't pay to get into a gin joint.]
    SAL: You don't pay, you don't drink. You don't drink, you don't stay.
    SAL: Out back. Now.
    ~ set_flag("thrown_out")
    -> END
= after
SAL: You're in, ain't you? Don't make me regret it.
-> END

=== bartender ===
{has_flag("photo_shown"): -> bartender.after}
BARTENDER: What'll it be?
- (opts)
* (menu) [What've you got?]
    BARTENDER: Gin. Gin with ice. Gin that tastes like it was made in a bathtub. Because it was.
    -> bartender.opts
* {menu && cash_amount() >= 1 && !has_flag("lantern_gin")} [Bathtub? Swell. The dirtier the hooch, the better I like it. Set 'em up, pal. #short: Bathtub? Swell. Set 'em up, pal.]
    -> bartender.gin
* [Nice place.]
    BARTENDER: It's a dump. But it's a dump with a band on Fridays.
    -> bartender.opts
* [I'm looking for a woman. Eleanor Harrington.]
    -> bartender.photo
+ [(Leave)]
    -> END
= gin
BARTENDER: A man of refined tastes. That'll be a buck.
~ set_flag("lantern_gin_paid")
BARTENDER: Bathtub's finest. Don't ask which bathtub.
~ set_flag("lantern_gin_poured")
CUE: gin
~ set_flag("lantern_gin")
MICAH: Smooth as a cement mixer. Just how I like it.
BARTENDER: Glad you approve. Ain't many do.
THOUGHT: It goes down like a lit match. For half a minute, the room is warm and nobody's missing.
-> bartender.opts
= photo
BARTENDER: ...
BARTENDER: Never heard of her. And I got a real bad memory for faces, pal. Especially faces that ask questions.
THOUGHT: He went still a second too long at her name. Never heard of her, my eye.
- (photo_opts)
* [She left the Aurelian with one of your regulars. People saw.]
    BARTENDER: Lots of people get seen. Then one day they stop getting seen. Funny how that works.
    -> bartender.photo_opts
* [I could make it worth your while.]
    BARTENDER: Your money's no good here, mister. Your questions neither.
    -> bartender.photo_opts
+ [(Drop it)]
    -> END
= after
BARTENDER: The Club. Hubbard Street. No sign on the door. That's all you get. Drink, or get out.
-> END

=== bartender_dislike ===
BARTENDER: Hey. Gumshoe.
BARTENDER: On second thought, I don't like you. Not one bit.
-> END

// ---------------------------------------------------------------- THE ALLEY BEHIND THE BLUE LANTERN

=== alley ===
BARTENDER: Stay down, gumshoe. You look good down there.
MICAH: ...I've been worse. I just can't remember when.
SAL: Want I should give him another, Tony?
BARTENDER: Nah. He's listening now. Ain't you listening?
MICAH: I'm all ears. The rest of me's on the pavement.
BARTENDER: The dame. Eleanor. She's hot stuff, see? Too hot for this joint, too hot for this town.
BARTENDER: She come in here a few nights back, scared out of her mind. I sent her to the nuns. The convent up on the North Side.
BARTENDER: That's it. That's all I know. I don't know nothin' else, and I don't wanna.
MICAH: Why tell me at all?
BARTENDER: 'Cause a mug who takes a beating like that and keeps asking is gonna find out anyway. Better from me than from Moretti.
SAL: Come back here again and we bury you. Capisce?
-> END

// ---------------------------------------------------------------- THE CONVENT

=== nun ===
{has_flag("nun_talked"): -> nun.again}
NUN: This is a house of God, not a waiting room, and Vespers are long over. What are you doing here at this hour, young man?
MICAH: Looking for someone. Eleanor Harrington.
NUN: And what would you want with her?
* [Her husband hired me to find her.]
    NUN: Her husband. Yes. I am sure he is very worried. About something.
* [I just want to know she's safe.]
    NUN: Men always say that. Usually just before they make a woman less safe.
- NUN: What is your name?
MICAH: Micah. Micah Jones.
NUN: Micah. Like the prophet. "I will shew thee, O man, what is good." Do you remember the rest?
MICAH: My mother did. I stopped listening somewhere around "love mercy".
NUN: Then listen now, Micah. You would do better to end the search here, and have nothing more to do with that Jezebel.
MICAH: Jezebel? What do you mean by that?
NUN: ...
NUN: I have said too much already. It is not my place to judge. Only to pray.
NUN: The last door, at the end of the corridor. Look, if you must.
NUN: Then go. And God be with you, Micah Jones. You will need Him.
THOUGHT: Jezebel. Painted, thrown from a window, left for the dogs. Mother made sure we boys knew how that one ended.
~ set_flag("nun_talked")
-> END
= again
NUN: The last door, at the end. Look if you must. Then go.
-> END

// ---------------------------------------------------------------- OUTSIDE THE CONVENT

=== nun_farewell ===
NUN: What do you hope to find in all this, Detective?
MICAH: I don't know, sister, but I can't stop at this point.
NUN: Then go with God. And remember that finding a thing is not the same as knowing what to do with it.
~ set_flag("nun_farewell_done")
-> END

=== convent_dead_end ===
THOUGHT: The road was empty. No Eleanor under the trees, no taxi pulling away, no footprints in the wet. Just me and the rain and the convent bell.
THOUGHT: Going on four days she'd been gone from that cell. Four days is a long head start in a town this size. I'd hit a dead end, and I knew it.
- (leads)
* [(Go back to the Blue Lantern and lean on Tony.)]
    THOUGHT: Back to the Blue Lantern? Sure, and let Sal finish the job he started in the alley.
    THOUGHT: Tony had said it plain: come back and they bury me. Moretti's boys don't bluff.
    -> leads
* [(Go back to Harrington and ask what he left out.)]
    THOUGHT: Teddy Harrington. Hair oil and a handshake like a wet fish.
    THOUGHT: No. I didn't want to see that mug again until the job was done.
    THOUGHT: If I ever wanted it done. I didn't like that thought, so I put it back where I found it.
    -> leads
* [(Take it to the cops at the Chicago Avenue station.)]
    THOUGHT: And tell them what? A rich man's wife took a powder and the nuns won't talk?
    THOUGHT: Half that precinct was on Moretti's payroll. The other half was on Harrington's.
    -> leads
+ [(Call it a night. Back to the office.)]
    MICAH: Nothing for it. Back to the office, a bottle, and a long think.
    THOUGHT: Then I saw it, down the hill where the road bends: a tall sign buzzing amber and blue through the rain.
    INSET: motel
    MICAH: A flophouse...
    MICAH: Maybe she took a powder from Sister Agatha and holed up there. It's a long shot, but I'm fresh out of angles.
    MICAH: Nobody looks for a dame like Eleanor in a dump like that. Which makes it just the place to look.
    INSET: none
    -> END

=== motel_clerk ===
{has_flag("clerk_talked"): -> motel_clerk.again}
CLERK: Rooms are a dollar a night. Pay in advance, no visitors, no questions.
MICAH: I'm not after a room. I'm after a woman. Dark hair, fur collar, a face you'd remember. Name of Eleanor.
CUE: show_photo
CLERK: ...
CLERK: Never saw her.
CUE: pocket_photo
THOUGHT: He said it to the register. A man who never saw anybody doesn't usually sweat through his collar saying so.
* [You're sweating, friend. It's not that warm in here.]
    CLERK: It's the radiator. Landlord won't fix it.
    MICAH: The landlord. Who's that, then?
    CLERK: Fella who owns the place. He's... he's particular about who comes and goes.
* [I'm no cop. I just want to know she's all right.]
    CLERK: Everybody's all right here, mister. Everybody keeps quiet and everybody stays all right.
    MICAH: That sounds like something somebody told you to say.
    CLERK: It sounds like good sense.
- MICAH: Who are you scared of? Me?
CLERK: You? No. You're a fella asking questions. Fellas asking questions come and go.
CLERK: The fellas who come round Fridays for the envelope, they don't go. They come back.
MICAH: Moretti's crowd collect here?
CLERK: I didn't say a name. You heard me, I didn't say a name.
* [Then let me upstairs and I'll find her myself.]
* [A dollar for the room key. Any room on the first floor.]
- CLERK: No. Nobody goes up those stairs tonight. Not you, not anybody. That's the rule.
CLERK: If you're smart, you'll walk out that door and forget this dump's here. I sure would.
THOUGHT: Somebody upstairs, then. And somebody else had told him to keep her there, or to keep her quiet.
~ set_flag("clerk_talked")
-> END
= again
CLERK: I told you, mister. Nobody goes up. Go home.
-> END

// Act 2, days after the motel night: Micah comes back to make sure Eleanor got away, and the clerk won't say how.
=== motel_clerk_return ===
{has_flag("motel_return_done"): -> motel_clerk_return.again}
CLERK: You again. Rooms are still a dollar, and you still ain't getting one.
MICAH: The dame upstairs. First floor, the room over the alley. She still there?
CLERK: ...
CLERK: Gone. Checked out.
THOUGHT: Checked out. Nobody checks out of a joint like this. They just stop paying.
* [She say where she was headed?]
* [She leave in a cab? Somebody pick her up?]
- CLERK: I don't know nothing about it, mister. I keep the book. I don't keep track.
THOUGHT: His hands have found the register again. He's holding on to it like a life raft.
* [A dame doesn't just evaporate. Did she pay up? Leave a note?]
* [You saw her go. Who was she with?]
- CLERK: I told you. Gone. That's all. Now beat it, before... just beat it.
THOUGHT: Before what? He isn't scared of me. He's scared of something that already happened.
MICAH: Nice tie, pal. Your wife's present?
CLERK: ...What?
CUE: tie
CLERK: Agh! Lemme go!
MICAH: Listen close, pal, 'cause I'm only asking once more. I left her upstairs. What happened to her?
MICAH: Sing, or you'll be eating this counter till Friday, and Moretti's boys can have what's left of you.
CLERK: Two men! Two men took her! The same night you was here. Not an hour after you blew.
MICAH: What men? Whose?
CLERK: I don't know! A big one and a young one. They didn't sign the book, mister. They went up, they came down with her, they drove off.
CLERK: That's all I know. I swear on my mother. Nothing else.
CUE: release
~ set_flag("motel_return_done")
THOUGHT: Two men, the night I left. While I was walking home feeling sorry for myself, they were walking her down those stairs.
-> END
= again
CLERK: I told you everything, mister. Two men. Now please. Go.
-> END

=== eleanor_fire_escape_opening ===
// End of Act 1: the scene cuts on her question; eleanor_fire_escape repeats it after the First Interlude.
ELEANOR: Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?
-> END

=== eleanor_fire_escape ===
ELEANOR: Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?
INSET: fire_escape
MICAH: Eleanor Harrington. You wouldn't happen to know her?
ELEANOR: That depends on who's asking.
MICAH: Micah Jones. Private detective.
ELEANOR: Tony's boys said a gumshoe came around asking for me, with a prophet's name.
ELEANOR: They gave him a split lip to remember them by.
ELEANOR: Why are you looking for me, Mr. Jones?
MICAH: Your husband hired me to bring you home.
ELEANOR: Teddy. Of course. And what do you get, if you bring me home?
INSET: none_now
* [Twenty dollars a day, plus expenses.]
    ELEANOR: Twenty a day. I used to spend that on gloves.
* [Right now, I'm not so sure.]
    ELEANOR: That's the first honest thing a man has said to me in a month.
- ELEANOR: You're bleeding. Hold still.
THOUGHT: Her fingers on my split lip, cool as rain. Rose used to do that, a long time ago.
MICAH: You do this for every man who comes looking for you?
ELEANOR: Only the ones who get beaten on my account. It's a short list. You're at the top of it.
MICAH: The sister called you a Jezebel.
ELEANOR: And what do you call me, Mr. Jones?
MICAH: I haven't decided yet. I'm not sure I want to.
ELEANOR: You could tell Teddy you never found me.
MICAH: I could. I'm a lousy liar.
ELEANOR: Then I'll teach you. It's easy. You just have to want something badly enough.
MICAH: I want you to come away. Not back to Teddy. Anywhere.
ELEANOR: I can't go back there...
MICAH: Then stay. Right here.
CUE: closer
ELEANOR: You're walking into the rain, Mr. Jones. Not out of it.
CUE: kiss
THOUGHT: I'd have climbed a hundred fire escapes for that. Some things a man doesn't decide. They decide him.
THOUGHT: And somewhere across town Rose was waiting up for me, the way she always did. I kissed Eleanor anyway.
-> END

// ---------------------------------------------------------------- MOTEL, NIGHT

=== motel_night ===
ELEANOR: Putting your shoes on already? Most men at least wait for the sun.
MICAH: Most men aren't working for your husband.
ELEANOR: Were. You were working for him.
MICAH: ...
ELEANOR: This was a mistake, wasn't it?
MICAH: Probably. The best one I ever made, but still a mistake.
ELEANOR: We should never see each other again, Micah.
MICAH: I know.
MICAH: I won't tell anyone where they can find you. Not Teddy, not Moretti, not the nuns.
MICAH: And I'm giving up the job. Teddy can keep his twenty a day.
ELEANOR: He'll hate you for it.
MICAH: He'll have to get in line.
MICAH: What'll you do now? Where'll you go?
ELEANOR: Away. Out of Chicago, before the week's out.
ELEANOR: I have friends, Micah. And money enough to reach them. You don't have to worry about me.
THOUGHT: Friends. Money. I have a hunch neither one is true.
THOUGHT: I should ask which friends, and where, and how much. I don't. I'm too ashamed to ask. Too ashamed to be standing in this room at all.
THOUGHT: And she knows it. I can see it in her eyes. She's letting me off the hook, and I let her.
ELEANOR: Goodbye, Micah Jones.
MICAH: Goodbye, Eleanor.
-> END

// ---------------------------------------------------------------- THE CLUB

=== moc ===
MOC: Good evening, sir. This is a private club, and I don't believe you were invited.
MICAH: I was in the neighborhood. Doing some reading.
MOC: How edifying. And what does a gentleman like you read?
- (opts)
* [Midsummer fires. Oak groves. Wells people whisper their sins into.]
    MOC: Farmers' tales. Why would a man like you care what farmers did on the longest night of the year?
    -> opts
* [A library book. It helped me decipher the card with your address.]
    MOC: We are a club. People who like us write our address down. Why are you asking, Mr...?
    MICAH: Jones. Micah Jones.
    -> opts
* [Do the bonfires burn here too? Is that what the robe is for?]
    MOC: The robe is for the members, Mr. Jones. The questions seem to be yours. Why are you asking?
    -> opts
* -> done
- (done) MOC: Enough. I know why you are asking, Mr. Jones. And it has nothing to do with druids.
MOC: You are here because of Eleanor.
-> END

=== moc_eleanor ===
MICAH: Do you know where she is?
MOC: Of course! Thanks to your efforts, she is already with us, safe, and where she belongs!
MICAH: My efforts...?
THOUGHT: Thanks to me. He says it like a compliment, and it goes in like a knife.
MOC: Bruno. The gentleman is leaving.
BRUTE: This way, pal. Nice and easy. Or the other way.
-> END

=== moc_masked ===
MOC: The raven's seal. The door has already spoken for you, brother.
MOC: ...Welcome. The rite is about to begin. Go on through to the stage.
-> END

=== moc_again ===
MOC: The stage, brother. They are waiting.
-> END

// Act 3 opens with the stag taking his mask off: Harrington senior, in front of the whole Club.
=== harrington_unmask ===
~ set_flag("harrington_unmasked")
HARRINGTON: No more masks, Mr. Jones. Not tonight. Let them all see.
HARRINGTON: You look disappointed. What were you expecting? A high priest? Some farmers' god out of the woods?
HARRINGTON: Bonfires. Antlers. Old words from the old country. Theatre, Mr. Jones. All of it.
HARRINGTON: Look around you. Judges. Aldermen. A bishop. The man who owns the stockyards. A hundred men who run this city.
HARRINGTON: And not one of them will lift a finger tonight unless I allow it.
HARRINGTON: You've seen my girls. A new face on that stage every Thursday, and not one man in this room asks where she came from.
HARRINGTON: That is the beauty of it. A secret every man here shares binds him tighter than any oath.
HARRINGTON: That is the whole rite. That is why we meet. Power that never shows itself is only a rumour.
HARRINGTON: So now and then, it has to show its face. I show them mine. And they bow.
HARRINGTON: And next Thursday they will come back, and bow again.
-> END

=== club_caught ===
HARRINGTON: You brought Eleanor back to us. For that, the intrusion is forgiven. This is as far as you go.
INSET: none
* [(Draw the revolver.)]
    MICAH: Nobody move. Eleanor, come down off that stage. We're leaving.
    HARRINGTON: Go on, my dear. Answer him.
    ELEANOR: I am where I belong, Mr. Jones.
    THOUGHT: Mr. Jones. Not Micah. Like a girl reciting lines somebody else taught her.
    MICAH: Eleanor. Look at me.
    ELEANOR: I am where I belong.
* [(Do nothing.)]
    MICAH: ...
    ELEANOR: Thank you for bringing me back, Mr. Jones. Go home, Mr. Jones.
    MICAH: Eleanor...?
    ELEANOR: Thank you for bringing me back.
* [Our Father...]
    MICAH: ...who art in heaven... hallowed be Thy name...
    HARRINGTON: How childish...
    HARRINGTON: This is ruining the mood.
    THOUGHT: He lifts two fingers, the way a man calls for the check. Not at me. At somebody behind me.
- -> END

// ---------------------------------------------------------------- CATHEDRAL

=== caleb_act2 ===
CALEB: Can I help you, my son?
CALEB: ...Micah?
THOUGHT: My kid brother in a Roman collar. He still looks at me like I'm the one who ought to know the way.
MICAH: Hello, Caleb. Or is it "Father" now?
CALEB: Six years. You look like a man who hasn't slept for most of them.
~ set_flag("caleb_met")
MICAH: I didn't come to confess. I came to talk. There's a difference, isn't there?
CALEB: Not as much as you'd like. Sit. The pews don't charge by the hour.
MICAH: There's a woman. I was paid to find her. I found her, and then I let her go.
MICAH: The same night I walked out on her, two men walked her out of that flophouse. I didn't even ask where she'd go.
MICAH: And I can't stop thinking about her. Or about what I did this week. What I let happen.
INSET: church
MICAH: Right now, Caleb... I'm too far gone to be saved.
CALEB: That's crap, Micah.
CALEB: Forgive my language, Lord. But it is. No one is beyond salvation. Nobody. Not even you.
CALEB: A man who decides he's past saving has stopped listening to God and started listening to somebody else.
CALEB: That's the Devil's work, brother. It's the oldest trick he has.
CALEB: Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace.
MICAH: Grace. I tried praying, Caleb. In France, in the mud. Last week, at my desk, with the bottle watching.
MICAH: Our Father, who art in heaven, hallowed be Thy name... and then nothing. I can't get past it.
MICAH: Ma taught us both the whole thing before we could tie our shoes. I don't remember the rest.
CALEB: Then start there. He remembers the rest.
MICAH: I'll think about that.
MICAH: ...Coming here was a mistake.
CALEB: Micah, wait-
INSET: none
-> END

=== caleb ===
{not has_flag("caleb_met"):
    CALEB: Can I help you, my son?
    CALEB: ...Micah?
    MICAH: Hello, Caleb. Or is it "Father" now?
    CALEB: Six years. You look like a man who sleeps in his coat.
    MICAH: Only when it's raining.
    ~ set_flag("caleb_met")
- else:
    CALEB: Back so soon? Careful, Micah. People will think you've found religion.
}
- (opts)
* [How have you been?]
    CALEB: I hear confessions, I bury the poor, I pray for my brother. Two out of three are going well.
    -> caleb.opts
* [How's Rose?]
    CALEB: Ask her yourself. She's still at the library, still putting the world in alphabetical order, as if that would make it behave.
    CALEB: She keeps your picture in her desk drawer. Face down. But she keeps it.
    MICAH: That's something.
    -> caleb.opts
+ [(Leave)]
    CALEB: Go with God, Micah. He's been waiting for you longer than I have.
    -> END

// ---------------------------------------------------------------- LIBRARY

=== librarian ===
{has_flag("librarian_refused"): -> librarian.again}
{not has_flag("librarian_met"):
    LIBRARIAN: Shh. It's the middle of the day, sir, and folks are reading. What can I do for you?
    ~ set_flag("librarian_met")
- else:
    LIBRARIAN: Yes?
}
- (opts)
* {has_item("mirror") or knows_note("triquetra")} [I want to know about a symbol.]
    MICAH: Three loops in one knot. Scratched into the back of a lady's mirror.
    IMAGE: triquetra
    LIBRARIAN: ...
    LIBRARIAN: Where did you get that mirror?
    MICAH: That's between me and the mirror.
    LIBRARIAN: Then what that knot means is between me and my books. Good day, sir.
    ~ set_flag("librarian_refused")
    -> END
* [Busy day?]
    LIBRARIAN: Students, widows, and one gentleman who reads the obituaries for pleasure. Busy enough, sir.
    -> librarian.opts
+ [(Leave)]
    LIBRARIAN: Mind the step. And the silence.
    -> END
= again
LIBRARIAN: I've nothing to say to a man who won't say where he got that mirror.
-> END

=== librarian_threat ===
MICAH: Let's try that again. Slower, this time.
LIBRARIAN: Good Lord. Put that away! This is a library!
MICAH: Then keep your voice down. Bell. "Rites of the Old Isles." C-17. The book about this knot.
LIBRARIAN: A triquetra. C-Celtic. Old. Older than the saints in Ireland.
LIBRARIAN: Groves and wells and fires on the hilltops. Rites nobody has any business remembering.
LIBRARIAN: Y-yes. Bell's book. C-17. A rare book. Someone asked for it just last month.
LIBRARIAN: Take it. Take it and go, and please don't come back.
~ give_item("book")
MICAH: Pleasure doing business. Late fees are on me.
-> END

=== librarian_collar ===
MICAH: Let's try that again. Closer, this time.
LIBRARIAN: Unhand me! This is a library!
MICAH: Then keep your voice down. Bell. "Rites of the Old Isles." C-17. The book about this knot.
LIBRARIAN: A triquetra. C-Celtic. Old. Older than the saints in Ireland.
LIBRARIAN: Groves and wells and fires on the hilltops. Rites nobody has any business remembering.
LIBRARIAN: Y-yes. Bell's book. C-17. A rare book. Someone asked for it just last month.
LIBRARIAN: Let go of me and it's yours. Take it and go, and please don't come back.
~ give_item("book")
MICAH: See? We're getting along fine.
-> END

// ---------------------------------------------------------------- ACT 2: AFTER THE CLUB

=== street_choice ===
* [(Go find Rose.)]
    ~ set_flag("go_rose")
* [(Push forward.)]
- -> END

=== rose_house ===
ROSE: Micah.
THOUGHT: Rose, one hand on the door, not opening it an inch wider. Older. So am I. She wears it better.
ROSE: It's past eleven. What are you doing here?
MICAH: I was passing by.
ROSE: Nobody passes by this street, Micah. You have no business being here. Not anymore.
- (opts)
+ {pushes == 0} [I came to say I'm sorry, Rose.]
    ~ pushes = 1
    ROSE: You always are. It's the one thing you were ever reliable about.
    -> opts
+ {pushes == 1} [I know what I did. I left you and Tommy alone, and I called it work. #short: I know what I did. I left you and Tommy alone.]
    ~ pushes = 2
    ROSE: You called it a lot of things. Tommy called it "When's Daddy coming home?" For a year.
    -> opts
+ {pushes == 2} [I'm not asking you to take me back. Just to forgive me.]
    ~ pushes = 3
    ROSE: Forgiving's the easy part, Micah. Forgetting is what you keep asking for.
    -> opts
+ {pushes == 3} [I've done something terrible this week. I need to hear it from somebody. From you. #short: I've done something terrible. I need to hear it from you.]
    ~ pushes = 4
    ROSE: And there it is. You're not here for us. You're here because you need something.
    -> opts
+ {pushes == 4} [Please, Rose. Just say it. Once.]
    ~ pushes = 5
    ROSE: ...
    ROSE: Go home, Micah.
    -> opts
+ [Good night, Rose.]
    {pushes >= 3:
        ~ set_flag("rose_wait")
        ROSE: Good night.
    - else:
        ROSE: You're running away again. It was always too hard for you... too hard on you. Don't bother ringing this bell again, Micah Jones.
    }
    -> END

=== rose_leave ===
+ [(Walk away without a word.)]
    ~ set_flag("rose_avoided")
+ [(Not yet.)]
- -> END

=== rose_coffee ===
ROSE: Micah? It's the middle of the night. God, your face...
{
- has_flag("spared_oldman"):
    MICAH: Tonight I had a gun on a man who deserved it more than anybody I ever met.
    MICAH: I put it away and walked out. Nobody will ever know but me. And now you.
- has_flag("walked_away"):
    MICAH: Tonight I had a gun on a man. I lowered it and walked away.
    MICAH: First smart thing I've done all week.
- else:
    MICAH: It looks worse than it is. It usually does.
}
{has_flag("rose_wait"):
    ROSE: What do you want? Last time you were here, you wanted me to forgive you.
- else:
    ROSE: What do you want?
}
INSET: rose
MICAH: Nothing you owe me.
MICAH: I'm not asking you to believe I've changed. I want to start showing you.
MICAH: Would you have a cup of coffee with me? Sometime. Daylight. A table between us.
ROSE: ...
ROSE: Coffee.
MICAH: Just coffee. You can bring Tommy, if he wants to see what his old man looks like.
ROSE: ...Why not.
INSET: none
-> END

=== caleb_club ===
CALEB: Micah. Twice in one week. People will start to talk.
MICAH: There's a club on Hubbard. No sign on the door, a man in a robe at the bell. They have Eleanor.
CALEB: A club? Micah, what would a priest know about clubs?
- (opts)
* (hid) [Tony told Eleanor you drive girls up to the convent after dark.]
    MICAH: That's where he sent her to hide. The one door the Club won't knock on, he said. And you're the one with the car.
    CALEB: I drive the sisters' groceries, and I drive up to say their Mass. That's all a priest's car is for.
    -> opts
* (roof) [The convent answers to the Church. And you're the Church on this side of town. #short: The convent answers to the Church. And you're the Church.]
    CALEB: The convent is Mother Superior's house, not mine. I say Mass for the sisters. I don't keep their books.
    MICAH: But it's all one roof, in the end. Somebody under it might have heard something. Maybe you.
    -> opts
* {hid and roof} [They have her, Caleb. If you know anything, tell me.]
    CALEB: ...
    CALEB: I don't know anything about her. But I hear things. A priest always does.
    CALEB: That Club keeps its Thursdays. Spectacles, they call them. And spectacles need new faces. Fresh ones.
    CALEB: Girls off the trains at Union Station. Farm girls, girls off the boat. Somebody meets them with a smile and the promise of work in a nice house.
    CALEB: Performers, the Club calls them afterwards. Some of them get away, to my church door. I drive them up to the convent after dark, and the sisters keep them till it's safe.
    CALEB: We hide them. A new name, a ticket, a parish in Milwaukee or a farm in Iowa that doesn't ask. Fourteen girls, so far.
    MICAH: Fourteen. And the ones who don't get away?
    CALEB: ...
    THOUGHT: He looks at the altar, not at me. That's my answer.
    MICAH: You knew. All this time you knew what goes on in that place, and you said Mass on Sunday like the city was clean.
    CALEB: The Club leaves the convent alone, Micah. That's the bargain. I keep my mouth shut, and nobody comes knocking for the girls behind those walls.
    CALEB: If I talk, they take other girls off the next train, and they come for the ones we've hidden. Nothing changes but the graves.
    MICAH: You could have walked into the Tribune. A priest, with fourteen girls' stories. They'd have printed it.
    CALEB: And half the men who'd set the type drink at that Club on Thursdays.
    MICAH: So you pray, and you keep quiet. And you preach repentance to me.
    MICAH: You're a hypocrite, Caleb.
    CALEB: I know what I am. I confess the silence every week, and I mean to break it the day it won't bury the girls we hid. That day hasn't come.
    CALEB: If anybody knows anything about Eleanor, it's the sisters. The convent is the best place to ask.
    -> rest
- (rest)
CALEB: But don't go, Micah. Give up this foolish search. Whatever she is to you, it isn't worth it.
INSET: church
MICAH: There isn't much left for me to do.
CALEB: You know that isn't true.
CALEB: Repentance isn't for saints at the end of their lives, Micah. It's for anyone, any day they still draw breath.
CALEB: If a man truly repents, the Lord forgives him. Every time.
MICAH: Not a man like me, Caleb. I'm too far gone.
CALEB: Listen to yourself. You think your sins are too big for God to forgive? That's not humility, brother. That's pride.
CALEB: You've always been arrogant, Micah. Always the one who had to carry everything, so nobody could ever ask anything of you.
CALEB: Despair is just another way of putting yourself first. If you're past saving, you never have to change.
CALEB: The prodigal thought he was past it too. Then he turned for home, and his father ran to meet him.
~ set_flag("caleb_club")
INSET: none
-> END

=== office_ring ===
THOUGHT: My wedding ring, on the desk where I left it.
THOUGHT: Rose kept hers on long after I stopped coming home.
* [(Take the wedding ring.)]
    ~ set_flag("ring_taken_act2")
    ~ set_flag("took_faith_ring")
    ~ give_item("faith_ring")
    THOUGHT: A promise doesn't stop being a promise because I broke it.
* [(Leave the wedding ring in the office.)]
    ~ set_flag("ring_left_act2")
    THOUGHT: Not yet. I don't know how to carry it.
- -> END

=== office_act3_destination ===
+ [(Visit Caleb at the church.)]
    ~ set_flag("visit_caleb_act3")
+ [(Go to the Blue Lantern.)]
- -> END

=== caleb_repeat ===
CALEB: The sisters may have answers. That doesn't mean you have to keep chasing them.
MICAH: I know what you said, Caleb.
CALEB: Then remember what else I said. You still have a family.
-> END

=== caleb_act3_return ===
CALEB: Micah. Your face... Sit down.
MICAH: If I sit down, I might not get up again.
CALEB: Then stop running. Whatever happened tonight, don't make it worse.
CALEB: Rose and Tommy are still there. You can still choose them.
-> END

=== caleb_cross ===
CALEB: Take this cross, brother. Not as a bargain with God. As a reminder.
CALEB: There's a way back for everybody. Even you.
+ [(Accept the cross pendant.)]
    ~ give_item("cross")
    ~ set_flag("took_cross")
    MICAH: I'll keep it with me, Caleb.
    CALEB: Then remember what it means.
+ [(Refuse the cross pendant.)]
    MICAH: Keep it. I can't take it tonight.
    CALEB: I'll ask again when you come back.
- -> END

=== caleb_warn ===
CALEB: Sister Agatha telephoned. She said a man with your face pointed a gun at her.
MICAH: I asked nicely first.
CALEB: Repentance means more than asking nicely. Put the gun away.
CALEB: Micah, listen to me. Whatever you're about to do next, don't. Turn around. Go to Rose. Go anywhere else.
CALEB: There's still a way back. There always is. But not where you're going.
MICAH: You kept quiet about those girls for years, Caleb. Don't tell me where I'm going.
CALEB: ...That's fair. It's fair. But I'm still asking.
MICAH: Good night, Caleb.
-> END

=== caleb_last ===
CALEB: You've got that look. The one you had the night before you shipped out to France.
MICAH: I'm going back to the Club tonight. Dressed for the occasion.
CALEB: Then I can't stop you. I never could.
CALEB: I've been praying on what you called me. You weren't wrong. If you go in there, look at the girls on that stage. Somebody ought to.
CALEB: God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him.
CALEB: I'll pray for you, brother. It's all you ever left me to do.
-> END

=== nun_club ===
NUN: You again. Twice in one week. You smell of whiskey and trouble, young man.
MICAH: There's a club on Hubbard Street. Eleanor Harrington is there. Father Jones says you hide the girls who run from it.
NUN: I know nothing about clubs. I know nothing about their women. Go with God, Mr. Jones.
* [Where is she, sister?]
    NUN: I told you. I know nothing. Good night.
* [What happens in that club?]
    NUN: Nothing I would know about. Good night.
- (asked)
~ set_flag("nun_club_asked")
-> END

// Agatha's own confession, at gunpoint. Eleanor's night choice (interlude_agatha_night) decides whether she still
// calls her a Jezebel; both keep "She's a performer." (the harrington_senior note) and the Harrington senior lead.
=== nun_threat2 ===
NUN: Are you crazy?!
MICAH: Yeah. You can say that, sister. Where's Eleanor? What goes on at that club?
{
- has_flag("eleanor_refused_abbess"):
    NUN: Put that thing down. Please. I'll tell you. God knows I owe her that much.
    NUN: She's a performer. That's what they call them, at that Club. She tried to tell me, in her cell. I wouldn't let her finish. I knew enough.
    NUN: And I'd gone to that cell past midnight, with a candle, and called it charity. When she stopped me, I turned it round on her and put her out at first light.
    NUN: It was my fault, Mr. Jones. All of it. She came to this house for shelter, and I failed her.
- else:
    NUN: You belong with that Jezebel. Burn with her, then. I am done with you.
    NUN: She's a performer. She nearly had me fooled, the whore.
    NUN: ...No. God forgive me. I went to her cell. Past midnight, with a candle, and I called it charity.
    NUN: Jezebel she is. But it was my fault, Mr. Jones. She came to this house for shelter, and I failed her.
}
NUN: You want answers? Go see Harrington senior.
-> END

=== beaten_choice ===
* [(Keep going. For Eleanor.)]
    ~ set_flag("keep_going")
* [(Give up.)]
- -> END
// ---------------------------------------------------------------- ACT 3: THE BLUE LANTERN, THE MANSION

=== bartender_gun ===
BARTENDER: Sal? Sal, what's all the... oh. Oh, no.
MICAH: Evening, Tony. Sal's taking a nap. You and me are going to talk.
MICAH: Eleanor Harrington. The Club has her back. Where is she?
BARTENDER: Are you out of your mind? Beat it, Jones. You don't know who these people are.
BARTENDER: They own judges. They own cops. They own the men who own the cops.
BARTENDER: They bring girls in off the trains like crates of oranges, and nobody in this city asks what's in the crate.
BARTENDER: You'd be better off with a bullet in your skull. Quicker. Cheaper, too.
THOUGHT: The revolver weighs more than it did this morning. Tony's sweating. So am I.
* [(Shoot him in the shoulder.)]
    ~ set_flag("shot_bartender")
* [(Fire into the wall by his head.)]
    ~ set_flag("warned_tony")
* {has_flag("can_walk_away")} [(Lower the gun. It's not worth it.)]
    MICAH: ...You're right, Tony. It's not worth it. None of it is.
    ~ set_flag("walked_away")
- -> END

// The warning shot: a brick by Tony's ear, not Tony. Scared and unhurt, he gives the house and the key, but not the
// alarm on the kitchen door; MansionExterior rings it if Micah opens the door without spotting it first.
=== bartender_miss ===
BARTENDER: Jesus, Mary and Joseph! You're crazy! You're actually crazy!
MICAH: That was the wall, Tony. I've got five more, and you've only got the one head. Where is she?
BARTENDER: The old man's! Harrington's place, on the Gold Coast! They took her to him tonight!
BARTENDER: Go round the back, to the kitchen. We bring the booze in that way, every Thursday. There's a key on the lintel over the door.
BARTENDER: Just walk right in like the delivery boys do, Jones. Nobody'll even look up.
THOUGHT: He says it too quick, and he won't look at me. Tony never could keep a straight face on a short pour.
MICAH: You never saw me tonight, Tony.
BARTENDER: Saw who? I've been inside all night, polishing glasses. Ask anybody.
-> END

=== bartender_shot ===
BARTENDER: AAAAH! My shoulder! You shot me, you crazy son of a...
MICAH: I've got five more, Tony. And you've got another shoulder. Where is she?
BARTENDER: The old man's! Harrington's place, on the Gold Coast! They took her to him tonight!
BARTENDER: Go round the back, to the kitchen. We bring the booze in that way, every Thursday.
BARTENDER: There's a key on the lintel over the kitchen door. Just walk in like the delivery boys do.
MICAH: And?
BARTENDER: And... there's a bell. A burglar alarm, wired to that door. The old man had it put in after the Feds came sniffing. Open it cold and it rings the whole house awake.
BARTENDER: That's everything, I swear it! On my mother!
MICAH: Keep pressing on that shoulder, Tony, and get it looked at. Tell them you slipped.
BARTENDER: Slipped. Sure. And when they ask me who I slipped on, Jones? I pour for these people. They'll ask.
THOUGHT: The Gold Coast. The kitchen door. The delivery boys' key.
THOUGHT: He knows my name. He knows my office, and Rose's street. Everybody on Halsted does. By tomorrow, so will everybody he pours for.
THOUGHT: The gun's still warm in my hand, and the street's right there.
* [(Leave him bleeding, and go.)]
    THOUGHT: I shot a man tonight. My hand doesn't shake. That's what scares me.
* [(Finish him. He knows my name.)]
    ~ set_flag("finish_tony")
- -> END

=== bartender_dismiss ===
BARTENDER: Scram, pal. I already spilled everything I know.
-> END

// Micah chose to finish Tony, on his back in the alley after the first shot, so he can't tell the mob. Alley walks
// him round to aim down at Tony's head, plays this knot, then fires the shot before bartender_dead.
=== bartender_kill ===
BARTENDER: Jones? What are you... no. No, no, I told you! I told you everything!
MICAH: You did, Tony. That's the trouble. You'll tell them everything too.
BARTENDER: I won't! On my mother, I won't say a--
-> END

=== bartender_dead ===
~ set_flag("killed_tony")
THOUGHT: The second shot is louder than the first. Or I'm listening harder.
THOUGHT: He's got nothing left to tell anybody. The rain's already washing him toward the drain, like everything else in this alley.
THOUGHT: Nobody saw. Nobody but God, Caleb would say. Tonight that's one too many.
-> END

// After Tony: Micah at Caleb's church, past midnight, with Tony's blood on his cuff. Caleb hears his confession and
// absolves him once he is sorry and promises no more blood. Then, as his brother and not as a penance (a confessor may
// urge it, never impose it), he asks him to walk to the police with him. Going on to the mansion first is the promise
// the Our Father needs (Endings.CanSpareOldMan). See docs/theology.md.
=== caleb_tony ===
CALEB: Micah? It's past midnight. What... There's blood on your cuff.
MICAH: It's Tony's. The bartender at the Blue Lantern. I shot him, Caleb. Twice.
MICAH: The second time he was on his back in the rain, and he'd already told me everything. He knew my face. I told myself he'd send them after Rose and Tommy.
CALEB: ...
INSET: church
CALEB: Kneel down, Micah. Not for me. Say it the way Ma taught us.
MICAH: Bless me, Father, for I have sinned. I killed a man tonight. To save my own skin.
CALEB: Are you sorry for it? Not scared, Micah. Sorry.
MICAH: I'm sorry. God help me, I'm sorry.
CALEB: Then no more blood. Not tonight, not for her, not for anybody. Promise me.
MICAH: No more blood. I promise.
CALEB: And his mother. Whatever you can do for her, as long as you live, you do it.
MICAH: I will.
CALEB: For your penance, pray for Tony, and for his mother, every night you've got.
CALEB: Ego te absolvo a peccatis tuis, in nomine Patris, et Filii, et Spiritus Sancti.
CALEB: That's between you and God now, and it's done. This next part isn't your penance. I'm asking as your brother.
CALEB: The station on Maxwell Street is open all night. I'll walk you there myself. Tonight, while you still mean it.
* [(Turn yourself in.)]
    ~ set_flag("surrendered_tony")
    MICAH: All right. Walk with me, Caleb. I don't trust my legs.
    CALEB: Then lean on me. I'm used to it.
* [Not yet. Eleanor's still in that house.]
    ~ set_flag("confessed_tony")
    MICAH: After her, I'll walk in there on my own two feet. I swear it.
    CALEB: On your own two feet. I'll be on the station steps at sunrise, Micah. Don't make me wait for nothing.
- INSET: none
-> END

// The alarm, on the warning-shot route: Tony left the bell out. Running is ending 13 (Outskirts); going in anyway is
// ending 14 (the kitchen ambush).
=== alarm_footsteps ===
THOUGHT: Feet on the back stairs. Heavy ones, and more than one pair. Nobody in this house sleeps in slippers.
THOUGHT: "Walk right in like the delivery boys." Tony knew. He sent me to ring the doorbell.
+ [(Run.)]
    ~ set_flag("alarm_ran")
+ [(Stay. She's in there.)]
    ~ set_flag("alarm_stayed")
- -> END

// Ending 14: the Club's two men in the Harrington kitchen, waiting at the cook's table. MansionKitchen fires the shots.
=== kitchen_ambush ===
THOUGHT: Two of them, at the cook's table, with the light off. Like they've been waiting for me all week.
GUNMAN: Bell's for the delivery boys, pal. You don't look like a delivery boy.
MICAH: I'm here for Eleanor Har...
-> END

=== harrington_eleanor ===
HARRINGTON: There, now. It's not so bad, is it? Being back where you belong.
ELEANOR: ...
HARRINGTON: You ran to the nuns, and then to a drunk who calls himself a detective. And where did they bring you? Home.
HARRINGTON: Theodore will have you back. He always does. The Club will have you on Thursdays. And I will have you whenever I please.
ELEANOR: Yes, Mr. Harrington.
HARRINGTON: Good girl.
THOUGHT: Good girl. Like he's talking to a spaniel. My hand finds the revolver before the rest of me decides.
-> END

=== oldman_taunt ===
HARRINGTON: Well. Mr. Jones, again. You weren't listening earlier tonight. My son's money paid for that coat, I believe.
MICAH: Get away from her.
HARRINGTON: Or what? You'll shoot an old man in his dressing gown? You haven't got the guts. You'd have done it by now.
HARRINGTON: And for whom? Look at her. She's a whore, Mr. Jones. A beautiful one, I grant you. But her place is here.
ELEANOR: Micah...
THOUGHT: One old man in a silk gown. My finger on the trigger, and Caleb's voice somewhere far behind it.
* [(Shoot him.)]
    ~ set_flag("shot_oldman")
* {has_flag("can_spare")} [Our Father...]
    ~ set_flag("spared_oldman")
    -> oldman_prayer
- -> END

// Micah backs out of the room saying the prayer he couldn't finish, a verse at a time; the old man talks into every gap.
// CUE: step moves him back towards the door and lowers the gun a little more (MansionBedroom.OnCue).
=== oldman_prayer ===
MICAH: ...who art in heaven...
CUE: step
HARRINGTON: Prayers? In my house? Put the gun down if you're going to pray, Mr. Jones. You look ridiculous.
MICAH: Hallowed be... hallowed be Thy name.
CUE: step
HARRINGTON: That's your brother talking. The priest. Does he know where you are tonight? Does he know what you came here to do?
MICAH: Thy kingdom come. Thy will be done, on earth as it is in heaven.
CUE: step
HARRINGTON: Look at her, Mr. Jones. Look at her. You came all this way. You can still have her. I'm an old man; I can be generous.
MICAH: Give us this day our daily bread.
CUE: step
HARRINGTON: Bread. I can give you bread. I can give you a house on the lake and a seat at the table on Thursdays. Name it.
MICAH: And forgive us our trespasses...
MICAH: ...as we forgive those who trespass against us.
CUE: step
HARRINGTON: Forgive? Nobody forgives a man like you. Not your wife. Not your God. Ask the girl what forgiveness is worth.
MICAH: And lead us not into temptation...
CUE: step
HARRINGTON: You'll be back. They always come back, Mr. Jones. Every one of them.
MICAH: ...but deliver us from evil.
CUE: door
{has_flag("killed_tony"):
    THOUGHT: Further than I've got since France. He's still talking when I reach the door. Let him. Caleb's waiting on the station steps at sunrise, and I promised him my own two feet.
- else:
    THOUGHT: Further than I've got since France. He's still talking when I reach the door. Let him. I know where I'm going.
}
-> END

// Eleanor's persuasion: four turns, four lines on each, one of each type. Every line adds its type's points to
// persuade_score; after the fourth turn PERSUADE_THRESHOLD or more convinces her. She only gets here having given in
// at least once in the interludes, so the possessive, earthly lines (the old man's way) reach her best. One clumsy line
// can be overcome, two can't. The full logic, every line and the arithmetic are in docs/eleanor-persuasion.md: keep
// it in step. "(Leave her.)" is offered from the third turn, "(Shoot Eleanor.)" on the fourth. If the fourth turn ends
// without her, eleanor_refused sends MansionBedroom to the footsteps and eleanor_footsteps.
=== eleanor_persuade ===
~ persuade_score = 0
ELEANOR: You... you killed him. Micah, what have you done?
MICAH: Get dressed. We're leaving.
ELEANOR: Leaving? To go where? There's no place in this city they can't find me.
// turn 1
* [I didn't come all this way to leave you here, Eleanor.]
    ~ persuade_score += PERSUADE_POSSESSIVE
    ELEANOR: All this way. For me.
    ELEANOR: He used to say that. That he'd come all the way back from the lake, just for me.
    THOUGHT: She hears it. The way she must have heard it from him.
* [Then we don't stay in this city. We're out of it tonight.]
    ~ persuade_score += PERSUADE_RATIONAL
    ELEANOR: Out of it. You say it like it's a door you can just walk through.
* [We'll find somewhere quiet. Somewhere nobody knows your name.]
    ~ persuade_score += PERSUADE_POSITIVE
    ELEANOR: Nobody knowing my name. That's a nice dream, Micah. I stopped having it.
* [You can't stay here. Not now. They'll pin it on you.]
    ~ persuade_score += PERSUADE_CLUMSY
    ELEANOR: They'll pin it on whoever they like. They always do.
    THOUGHT: Wrong thing to say. She's talking to the carpet now, not to me.
* [(Leave her, and turn yourself in.)]
    ~ set_flag("repented")
    THOUGHT: The gun under my arm weighs nothing now. It's the rest of me that's heavy.
    MICAH: No. You're right. I'm not taking anybody anywhere. Not tonight, not ever again.
    MICAH: I'm going to walk out of here, find the first cop who isn't on this family's payroll, and tell him what I did.
    ELEANOR: There isn't one, Micah. Not in this city.
    MICAH: Then I'll keep walking until I find one.
    THOUGHT: I came here to save somebody. All this time, I had the wrong one in mind.
    -> END
// turn 2
- ELEANOR: Theodore will be here by morning. He'll know what to do. He always does.
* [Whatever comes in the morning, you won't face it alone.]
    ~ persuade_score += PERSUADE_POSITIVE
    ELEANOR: Alone is the one thing I've never been allowed to be, Micah.
* [Theodore's a coward. I'll handle him.]
    ~ persuade_score += PERSUADE_CLUMSY
    ELEANOR: With that? You'd have to shoot every Harrington in Chicago. There are more of them than bullets.
    {persuade_score + PERSUADE_POSSESSIVE * 2 >= PERSUADE_THRESHOLD:
        THOUGHT: Wrong thing to say. She's talking to the carpet now, not to me.
    }
* [Forget Theodore. You've got me now.]
    ~ persuade_score += PERSUADE_POSSESSIVE
    ELEANOR: Got you.
    ELEANOR: That's what they all say. And somehow I always end up believing it.
    THOUGHT: She doesn't pull away. I don't like why.
* [He'll take you back like he always does. And lend you out again on Thursdays. #short: He'll take you back. And lend you out again on Thursdays.]
    ~ persuade_score += PERSUADE_RATIONAL
    ELEANOR: ...
    ELEANOR: Yes. He will. He'll even say he's sorry about it.
// turn 3
- ELEANOR: And what would I do out there? I don't know how to be anything but theirs.
{persuade_score + PERSUADE_POSSESSIVE * 2 < PERSUADE_THRESHOLD:
    THOUGHT: Her eyes keep going to the other door. I'm losing her.
}
* [You can be anything you like. A singer. A nurse. Anything.]
    ~ persuade_score += PERSUADE_CLUMSY
    ELEANOR: The Club said that too, the first night. Anything I liked.
    {persuade_score + PERSUADE_POSSESSIVE >= PERSUADE_THRESHOLD:
        THOUGHT: Wrong thing to say. She's talking to the carpet now, not to me.
    }
* [You'd find work, like anybody. Out there nobody owns you.]
    ~ persuade_score += PERSUADE_RATIONAL
    ELEANOR: Work. I suppose I'd learn. I learned everything else.
* [Then be mine instead. I'll look after you.]
    ~ persuade_score += PERSUADE_POSSESSIVE
    ELEANOR: Yours, instead of theirs.
    ELEANOR: At least it would be one man's.
    {persuade_score + PERSUADE_POSSESSIVE >= PERSUADE_THRESHOLD:
        THOUGHT: I sound like him. She's listening anyway. Maybe because of it.
    }
* [You don't have to know tonight. You only have to walk through that door. #short: You only have to walk through that door tonight.]
    ~ persuade_score += PERSUADE_POSITIVE
    ELEANOR: One door.
    ELEANOR: I've walked through a lot of doors, Micah. I never once picked which.
* [(Leave her.)]
    -> leave
// turn 4
- ELEANOR: Why do you even care, Micah? What do you want from me?
{persuade_score + PERSUADE_POSSESSIVE < PERSUADE_THRESHOLD:
    THOUGHT: Further away with every word. Somewhere I can't follow, in the same room.
}
* [Nothing. Come or stay, it's yours to decide. But decide it yourself, for once. #short: Nothing. Come or stay, but decide it yourself, for once.]
    ~ persuade_score += PERSUADE_POSITIVE
    ELEANOR: Nobody ever asked me. Not once. Not him, not Theodore, not the nuns.
* [Theodore paid me to find you. I'm only finishing the job.]
    ~ persuade_score += PERSUADE_CLUMSY
    ELEANOR: So I'm a job. Twenty dollars a day, and expenses.
* [Every time I've seen you, you've said you can't go back there. Now you don't have to. #short: You said you can't go back there. Now you don't have to.]
    ~ persuade_score += PERSUADE_RATIONAL
    ELEANOR: I did say it. I say a lot of things, to a lot of men. That one I meant.
* [You. I've wanted you since the first time I saw your photograph.]
    ~ persuade_score += PERSUADE_POSSESSIVE
    ELEANOR: There it is. No speeches. Just wanting.
    ELEANOR: At least you're honest about it. They never were.
* [(Leave her.)]
    -> leave
* [(Shoot Eleanor.)]
    ~ set_flag("shot_eleanor")
    THOUGHT: She won't come. She'll stay here with him, on his carpet, in his house, for the rest of her life.
    THOUGHT: Then let the rest of her life be short. The gun comes up again before the rest of me can stop it.
    -> END
- ~ temp convinced = persuade_score >= PERSUADE_THRESHOLD
{convinced:
    ELEANOR: ...
    ELEANOR: You talk like them, Micah. Like every man who ever wanted me.
    ELEANOR: God help me, maybe that's why I believe you.
    ~ set_flag("eleanor_convinced")
    -> eleanor_comes
}
~ set_flag("eleanor_refused")
ELEANOR: Then I've decided. I'm staying, Micah.
ELEANOR: Please. Just go. Before they come.
-> END

= leave
MICAH: Suit yourself. I'm not dying in this house for somebody who won't walk out of it.
ELEANOR: Goodbye, Micah.
THOUGHT: I don't look back. If I look back, I stay.
-> END

// The persuasion ran out and the men are on the stairs: the last choice in the bedroom.
=== eleanor_footsteps ===
THOUGHT: Two men. Maybe three. Coming up the stairs, in no hurry. They don't need to hurry.
THOUGHT: She isn't coming. A door behind me, a gun under my arm, and maybe ten seconds to choose.
* [(Pull the trigger on myself.)]
    ~ set_flag("shot_himself")
    THOUGHT: No more running. Not from them, not from Caleb, not from the man in the mirror.
    ELEANOR: Micah... Micah, no...
    -> END
* [(Shoot Eleanor.)]
    ~ set_flag("shot_eleanor")
    THOUGHT: She'll stay here with him, on his carpet, in his house, for the rest of her life.
    THOUGHT: Then let the rest of her life be short. The gun comes up again before the rest of me can stop it.
    -> END
* [(Leave her to them.)]
    MICAH: That's my cue. Goodbye, Eleanor.
    -> END


=== eleanor_comes ===
ELEANOR: All right. All right. Don't let go of my hand.
THOUGHT: Her hand is cold and small in mine. For the first time in years I know exactly where I'm going.
-> END

// ---------------------------------------------------------------- ACT 3: ENDINGS

=== ending_together ===
THOUGHT: At the gate she fetched her duffle from the Club's car, packed for running. She changed in mine while I drove: a black suit, the skirt above the knee. The sheet's somewhere on the road behind us.
ELEANOR: So this is where Chicago ends.
MICAH: It doesn't end. It just runs out of streetlights.
ELEANOR: Where are we going?
MICAH: West. Until the money runs out, or the road does.
{has_flag("took_documents"):
    MICAH: And if anybody comes asking, I've got a folder on Harrington Steel. Enough to make them stop.
}
{has_flag("mansion_exploded"):
    ELEANOR: The whole house, Micah. There's nothing left of them back there.
    MICAH: There's plenty left of them. Just not in that house.
}
ELEANOR: Say goodbye, then.
MICAH: Goodbye, Chicago. You were never any good to me.
ELEANOR: Goodbye, Chicago.
THOUGHT: She says it like a prayer. I say it like a man settling a tab. Then we get back in the car.
-> END

=== ending_alone ===
THOUGHT: The last fence post. The last streetlight. The last place a man goes to bury something.
MICAH: She wouldn't come with me. Even with him on the carpet and the whole Club on its way.
{has_flag("took_documents"):
    THOUGHT: I've got the old man's papers in my coat. Enough to keep the cops off me for the rest of my life.
}
{has_flag("mansion_exploded"):
    MICAH: The morning paper lists the dead. Eleanor Harrington. There it is, in black and white.
    MICAH: I told myself I was saving her. I left her there and lit the fuse.
    MICAH: They know who died. They don't know what I did.
}
THOUGHT: Free. That's the word for it. Free as a dog nobody wants.
-> END

// Ending 13: he ran from the alarm, and Eleanor's still in that house.
=== ending_out ===
THOUGHT: The last fence post. The last streetlight. I didn't stop for any of them.
MICAH: A bell, and some feet on the stairs. That's all it took. I heard them coming and I ran.
MICAH: She's still in that house. Thursdays, the old man said. Every Thursday.
MICAH: I'm out. Out of the job, out of the city. Chicago can have what's left of Micah Jones. I'm not coming back for it.
-> END

=== prison_eleanor ===
THOUGHT: Six months of grey walls and grey soup. Today, a visitor. The guard says she came in a black suit, like a widow.
ELEANOR: Hello, Micah.
MICAH: You came. The guard bet me a cigarette you wouldn't.
ELEANOR: They said a lot of things about you. In court, mostly.
MICAH: You were never in that courtroom. Not your name, not your face. I kept you out of it. Out of all of it.
ELEANOR: I know. And I'm grateful, Micah. I really am.
ELEANOR: But I have to go on from here. I'm going back to Theodore.
MICAH: To Teddy. After all of it.
ELEANOR: He's the only door that was ever open to me. You knew that, the first night.
ELEANOR: Goodbye, Micah.
THOUGHT: She doesn't look back at the door. I can't blame her. I never once looked back at mine.
-> END

=== prison_caleb ===
THOUGHT: Six months of grey walls and grey soup. Today, my brother, in his collar, turning his hat in his hands.
CALEB: Micah.
MICAH: Father.
CALEB: How are you holding up?
MICAH: Three meals a day. That's two more than I managed outside.
CALEB: I went to see Rose.
MICAH: And?
CALEB: ...
MICAH: She doesn't want anything to do with me. You can say it, Caleb.
CALEB: She asked me not to bring Tommy. Not yet. Maybe not ever.
MICAH: And Eleanor's living with Harrington's son. In the big house with the view of the lake. I read the papers.
CALEB: I'll pray for you, brother.
MICAH: You always say that. One of these days I'd like to know what you ask for.
THOUGHT: He goes out into the daylight. I go back to my cell and think about Rose, and Tommy, and what Caleb asks for.
-> END

=== prison_rose ===
THOUGHT: Six months of grey walls and grey soup. I wrote to her every week. Today, for the first time, she wrote back. Today, she came.
ROSE: Micah.
MICAH: Rose. You came.
ROSE: I almost didn't. I sat on the bus outside the gate for an hour.
MICAH: I'm sorry, Rose. For all of it. For the bottle, for the nights, for Tommy waiting by the window. For what I did in that house.
MICAH: I'm not asking you for anything. I just needed to say it to your face, once, sober.
ROSE: I don't know if I can forgive you, Micah. I honestly don't.
ROSE: I don't even really understand why you called me here. What you want from me, after everything.
MICAH: Nothing. That's the strange part. Just for you to know I'm sorry.
ROSE: ...
ROSE: I'll try. That's all I can promise. I'll try.
THOUGHT: She doesn't reach across the table. But she doesn't hurry to the door, either. It's more than I deserve. It's more than I had.
-> END

// Ending 12: Micah killed Tony and turned himself in for it, from Caleb's church or after the Our Father. Caleb walked
// him in, and visits.
=== prison_caleb_tony ===
THOUGHT: A year of grey walls and grey soup. Today, my brother, in his collar, the same as every first Sunday.
CALEB: Micah.
MICAH: Father. Still the only man in Chicago who visits a murderer on purpose.
CALEB: I walked you in through that door. I'm not going to stop walking now.
{has_flag("spared_oldman"):
MICAH: The old man?
CALEB: Alive, and still talking, I'm told. To anybody who'll listen.
{has_flag("took_documents"):
    CALEB: But not to the grand jury. The papers you handed in with your confession did the talking there. The girls' names, the trains, the prices. The Club's finished, Micah. No more Thursdays.
    MICAH: Then one thing I did that night was worth doing.
- else:
    MICAH: And the Club?
    CALEB: Thursdays, the same as ever. I'm sorry, brother.
}
- else:
MICAH: Eleanor?
CALEB: Back in the big house on the Gold Coast. Nobody went for her that night.
MICAH: Nobody. Not me, either. I picked this instead.
CALEB: You picked right. It doesn't feel right. That's how you know.
}
MICAH: Tony had a mother. In Cicero. I write to her every month. She sends them back unopened.
CALEB: Keep writing. That's not for her to answer. It's for you to send.
MICAH: And Rose?
CALEB: She asked me to bring you this.
THOUGHT: A drawing in crayon. A man in a hat, behind bars that look like a fence, and a boy waving through them.
MICAH: He's got her eyes. And God help him, my chin.
THOUGHT: Life, the judge said, and Caleb in the back row said Amen like it was a Sunday. I've got the time. I'm using it.
-> END

// ---------------------------------------------------------------- ELEANOR'S OWN WAY (endings 8 to 11)
// Only when she refused both Agatha and the old man (Endings.EleanorHeldOut).

// Endings 10 and 11: Micah has shot the old man; instead of the persuasion, Eleanor, worn out, just wants to leave.
=== eleanor_weary ===
ELEANOR: ...
THOUGHT: She looks at him on the carpet for a long time. No scream. No tears. Just tired, tired all the way down, like somebody who's been carrying a trunk up the stairs for years and has finally set it down.
ELEANOR: Let's get out of here, quick.
MICAH: Eleanor--
ELEANOR: Not now, Micah. Not one more word in this house. I haven't got anything left to say in it.
~ set_flag("eleanor_weary")
THOUGHT: She doesn't take my hand. She just comes, holding the sheet round her like it weighs a ton.
-> END

// Ending 10: the edge of the city, the car, and Eleanor walking away from it.
=== ending_weary_road ===
THOUGHT: At the gate she took her duffle, packed for running, off the back seat of the Club's car, and changed in mine on the way: a plain white dress, and her pearls. The sheet's somewhere behind us on the road. She still wouldn't look at me.
MICAH: West, then. Until the money runs out, or the road does.
ELEANOR: ...
ELEANOR: I told you all of it in the car, Micah. The motel, after you'd gone. The old man's gin. You know everything now.
MICAH: I know enough.
{has_flag("mansion_exploded"):
    ELEANOR: The whole house. I watched it in the mirror the whole way, until it was only a glow.
}
ELEANOR: Then you know why. I can't go on like this, Micah, I can't be with you. I need ... peace.
MICAH: Peace. Out here? There's nothing out here but stubble and wind.
ELEANOR: That's why. Nobody out here wants anything from me.
{has_flag("took_documents"):
    ELEANOR: One more thing. The old man's papers in your coat. The girls' names are in there. Don't keep them for yourself, Micah. Give them to the newspapers.
    MICAH: ...All right. For them.
}
ELEANOR: Go home, Micah. Find yours.
-> END

// Ending 11: Joliet; Eleanor visits once, and only to say goodbye.
=== prison_eleanor_peace ===
THOUGHT: Six months of grey walls and grey soup. Today, a visitor. No hat, a plain white dress and her pearls, like a woman on her way to early Mass.
ELEANOR: Hello, Micah.
MICAH: Eleanor. I didn't think you'd come.
ELEANOR: Neither did I. I nearly turned round at the gate.
MICAH: You were never in that courtroom. Not your name, not your face. I made sure of that much.
ELEANOR: I know. Thank you.
MICAH: Are you going back to him? To Theodore?
ELEANOR: No. Not to Theodore, not to the Club, not to anybody. I'm so tired, Micah. I've been tired since I was nineteen.
ELEANOR: I came to tell you the rest of it. The motel, after you left. The old man's gin. You ought to know what you shot him for.
THOUGHT: She told me. Quietly, across the table, while the guard watched the clock.
ELEANOR: I hope you find your peace, Micah. I'm going to try to find mine, with the help of the Lord...
THOUGHT: She gets up and goes, and doesn't look back. It doesn't feel like a door closing. It feels like one opening, somewhere I can't see yet.
-> END

// Endings 1, 8 and 9: after Micah's prayer, the player is Eleanor in the sheet, and the old man has his back to her.
=== coda_wake ===
THOUGHT: The door closed on the last of his prayer. The old man stood at the foot of the bed looking at it, his back to her, and laughed, a little, the way he laughed at the theatre.
HARRINGTON: A prayer. In my house. In my bedroom.
HARRINGTON: Get back into bed, my dear. I'll be with you in a moment. I want to hear the car leave.
THOUGHT: On the nightstand at her elbow, the brass candlestick. The bed, warm and waiting. And his back, for once, turned, an arm's length away.
-> END

=== coda_bed ===
ELEANOR: Yes, Mr. Harrington.
THOUGHT: She got back into the walnut bed, and pulled the sheet up, and looked at the ceiling. She had had a lot of practice at that, too.
-> END

=== coda_strike ===
THOUGHT: Brass, heavy as a sin. He never turned round. He never heard her bare feet on the carpet.
THOUGHT: He went down onto his own rug without a word, the first time in his life he had nothing to say.
ELEANOR: Good girl.
THOUGHT: She didn't look at him twice. The door Micah had used stood open on the dark of the study.
-> END

=== coda_fire ===
THOUGHT: The Club's rye ran out over the flags, the whiskey they poured on Thursdays. Micah's lantern burned in her hand.
ELEANOR: You always said this house would outlive us all.
THOUGHT: She set the lantern down in the whiskey, and took the kitchen steps two at a time.
-> END

=== coda_outside ===
{has_flag("eleanor_burned"):
    THOUGHT: Behind her, the windows of the big house went orange one by one, like it was throwing a party she wasn't invited to.
- else:
    THOUGHT: Behind her, the big house stood dark and quiet, as if nothing had happened in it at all. Nothing ever had, as far as the papers would know.
}
ELEANOR: Goodbye, Mr. Harrington.
THOUGHT: She walked down to the road barefoot, with the cook's coat from the kitchen peg over the sheet. Nobody stopped her. Nobody ever looked twice at a woman leaving that house before dawn.
-> END

// Ending 9: Joliet, Eleanor in a jumpsuit, and Caleb, who came because she asked for a priest.
=== prison_eleanor_caleb ===
THOUGHT: The women's wing at Joliet. Grey walls, grey soup. She asked for a priest, and they sent the one whose name she knew.
CALEB: Mrs. Harrington. They said you asked for me by name.
ELEANOR: Eleanor. Nobody's called me Mrs. Harrington since the trial. They call me 4471.
ELEANOR: You're his brother. You have his hands.
CALEB: I've been told. What can I do for you, Eleanor?
ELEANOR: I want to confess, Father. All of it. Not just the old man. All of it.
CALEB: Then I'm listening. Take your time. We have the hour.
THOUGHT: She told him. The Club, the Thursdays, the gin and the powder. The convent, and Agatha's candle. The motel. A walnut bed, and a brass candlestick, and the back of an old man's head.
ELEANOR: I told the court the rest, Father. Out loud, with the reporters writing. The Thursdays. The girls off the trains. The men in the front row.
ELEANOR: The Club's finished. They say the building's for sale.
CALEB: I know. I read every word.
THOUGHT: He didn't tell her how many years he had kept the same words behind his teeth. She knew it anyway. She said it was in his hands.
ELEANOR: How is he? Micah.
{has_flag("killed_tony"):
    CALEB: Here. The men's wing, across the yard. He turned himself in the morning after that night, for a bartender he killed.
    ELEANOR: ...
    ELEANOR: Then he stopped running. It's better this way.
- else:
    CALEB: He's with his wife now.
    ELEANOR: ...
    ELEANOR: It's better this way.
}
CALEB: Do you repent of these sins, Eleanor? Truly?
ELEANOR: I was afraid of him. And I wanted him dead. God help me, I can't tell you which hand held the candlestick.
CALEB: Then don't sort it. Be sorry for every part of you that wanted him dead, and leave the sorting to God.
ELEANOR: ...I am, Father. For all of it. And I won't call that part good.
CALEB: Ego te absolvo a peccatis tuis, in nomine Patris, et Filii, et Spiritus Sancti.
ELEANOR: Amen.
THOUGHT: She said it was the first time anybody had raised a hand over her without wanting something for it.
-> END

// Ending 8: Eleanor alone at the edge of the city, leaving it.
=== ending_eleanor_alone ===
THOUGHT: The same night. The sky over the North Shore still glowed orange behind her, and the fire bells hadn't stopped.
THOUGHT: At the gate stood the Club's car, the duffle she'd packed for running still on the back seat. In the dark she put on a white dress and her pearls, and left the sheet and the cook's coat in the ditch.
ELEANOR: So this is where Chicago ends. Just runs out of streetlights.
THOUGHT: The old man's Thursday book was in a brown envelope under her arm, addressed to the city desk of the Tribune. The first mailbox past the city limits would do.
{has_flag("killed_tony"):
    ELEANOR: Find your peace, Micah Jones. I'll write to you one day, and tell you what became of me. It might even be good news.
- else:
    ELEANOR: Go home to your wife, Micah Jones. I'll write to her one day, and tell her you were a good man once. It might even be true.
}
ELEANOR: Goodbye, Chicago.
THOUGHT: She said it like she was closing a door. Softly. The way you close it on something that's finally asleep.
-> END

// Ending 1, after an early give-up, if Eleanor held out: Caleb has got her out of the old man's house. Endings 13 and 14
// too, after the alarm: Micah ran from the bell (13) or was shot dead in the kitchen (14), and she heard it from upstairs.
=== ending_eleanor_caleb ===
{has_flag("ending_13") || has_flag("ending_14"):
    THOUGHT: A week after the bell rang in the old man's kitchen. The edge of the city, past the last streetlight, and for once the rain had stopped.
- else:
    THOUGHT: Three nights after the Club. The edge of the city, past the last streetlight, and for once the rain had stopped.
}
THOUGHT: She had slipped out of the old man's house before it woke, with the duffle she'd packed for running, and changed into the white dress and her pearls. The priest had been waiting at the corner with his collar turned up, like a man who had done it before.
ELEANOR: It's one thing, Father, sneaking a girl or two out the back of the Club. Nobody misses a girl or two.
ELEANOR: But I'm their star. They won't take this lying down. They'll come after you.
CALEB: I know.
CALEB: But I'm tired of playing their game.
ELEANOR: ...
CALEB: There's a produce truck through here before dawn. Walt, from the parish. He'll take you as far as Springfield, and he won't ask you a thing. He doesn't ask me anything either.
CALEB: The Franciscan sisters there will put you up for a week or two, until a family I know can take you on to St. Louis. Nobody at the Club has ever heard of any of them.
CALEB: And this. It isn't much.
ELEANOR: An envelope. From the poor box, Father?
CALEB: From the poor box. You're poor tonight.
ELEANOR: You're his brother, aren't you? Micah's. You have his hands.
CALEB: So people tell me.
{
- has_flag("ending_14"):
    ELEANOR: He came for me too, you know. Into the Club, in one of their masks, and they carried him out.
    CALEB: And then to the house.
    ELEANOR: I heard the bell from upstairs. Then the shots. Two of them, and then nothing at all. The old man told me over breakfast whose they'd been.
    CALEB: I buried him on Tuesday.
    ELEANOR: He died on that kitchen floor for me. I never asked him to.
    CALEB: No. He walked in all the same. Toward you, not away. I hold on to that.
- has_flag("ending_13"):
    ELEANOR: He came for me too, you know. Into the Club, in one of their masks, and they carried him out.
    CALEB: And then to the house. The night the bell rang in the kitchen. That was him.
    ELEANOR: I heard it from upstairs, and the Club's men go down the back stairs. They found nobody. Only the kitchen door, open on the rain.
    CALEB: He ran. Out of Chicago, that same night. He hasn't written to Rose. Not to me either, yet.
    ELEANOR: ...Good. One of us should get out of this city alive.
- else:
    ELEANOR: He came for me too, you know. Into the Club, in one of their masks, and they carried him out.
    CALEB: I know. He went home instead. To Rose, and a cup of coffee.
    ELEANOR: ...Good. That's where he belongs. Not chasing me through other men's houses.
}
THOUGHT: Headlights came up the road out of the dark, slow, the way a man drives when he's carrying crates of cabbages and a secret.
ELEANOR: That'll be Walt.
ELEANOR: Thank you, Father. For not asking what I'd done before you'd help me.
CALEB: I didn't need to. Go on. Before I change my mind about the poor box.
{
- has_flag("ending_14"):
    ELEANOR: Light a candle for Micah, Father.
    CALEB: Every Sunday.
- has_flag("ending_13"):
    ELEANOR: If he ever writes to you, tell him I got out too.
- else:
    ELEANOR: Say hi to Micah.
}
-> END

// ---------------------------------------------------------------- PRESENT DAY: END OF ACT 2, ACT 3

=== dinner_call2 ===
LEO: DAD! DINNER!
DANIEL: ...It's dark already? Again?
LEO: Mom says it's the second night in a row, and the dog is getting used to your plate!
DANIEL: Coming! I'm coming.
DANIEL: Animal masks and a woman on a stage. What did you get yourself into, Micah?
-> END

=== bedroom ===
MOM: Mmh... Dan. It's one in the morning. Turn that off.
DANIEL: Five more minutes. He's back at the Club. He just walked up to the stage.
MOM: Who is?
DANIEL: Micah. The detective. From the attic.
MOM: ...Goodnight, Dan.
DANIEL: Five more minutes.
-> END

// ---------------------------------------------------------------- SECOND INTERLUDE (Eleanor, before Micah's Act 3)
// Pages in another hand: a neutral narrator (THOUGHT) and Eleanor as the player. Who wrote them comes out in the
// epilogue. The goons are colour; the old man's offer (interlude_oldman) is saved when she refuses it.

=== interlude_motel ===
THOUGHT: The motel, the same night. His side of the bed still warm, then not. She lay awake and listened to the sign buzz.
THOUGHT: She had told him never to come back. She had meant it. She kept looking at the door anyway.
-> END

=== interlude_goons ===
THOUGHT: Two of them. The big one from the Club's back stairs, Bruno, and a younger one in a borrowed suit, with his hands in his pockets like he was cold.
BRUTE: Evening, Mrs. Harrington. Your detective left a trail a blind man could follow. We just followed it.
GOON: Nice place. Real classy. The sign's missing a letter.
+ [Who sent you? Theodore?]
    BRUTE: The young master don't send nobody anywhere. You know who sent us.
+ [I'll scream.]
    BRUTE: Go ahead. Motels like this, nobody comes. They turn the radio up.
+ [Let me put my shoes on, at least.]
    GOON: Sure, lady. Take your time. We got all night.
    BRUTE: No, we don't.
- GOON: He said you'd be trouble. You don't look like trouble.
ELEANOR: Then he's wrong about one of us.
BRUTE: Coat. Hat. The bag, too. And no tricks with the window. It's a long way down for a lady.
THOUGHT: They didn't touch her. They didn't have to. She knew the way to the car better than they did.
-> END

// The old man's dressing-room offer. "Take it" plays her drink-and-powder strip (CUE drink); refusing is saved
// (eleanor_refused_drugs, the other refusal endings 8-11 need), and ClubBackstage cuts to black on "Noooo!".
=== interlude_oldman ===
HARRINGTON: There she is. My songbird, home from the woods.
HARRINGTON: The nuns. A motel. A drunk who calls himself a detective. You've had quite a holiday, my dear.
ELEANOR: It wasn't a holiday.
HARRINGTON: No. I suppose it wasn't. Look at you. Painted like a saint in a window, and not a drop of colour under it. You need something to put the colour back.
THOUGHT: A glass of gin on the dressing table, and beside it, on a silver saucer, a little white line, laid out neat as a signature. As always.
+ [I don't want it tonight.]
    HARRINGTON: You always say that. And then the band starts, and you want it more than you want to breathe.
+ [Where's Theodore?]
    HARRINGTON: In the front row, where a husband belongs. Clapping, as he's told.
+ [(Look at the mirror, not at him.)]
    THOUGHT: The bulbs round the glass made her look like somebody else. She told herself it was somebody else. It had always helped, before.
- HARRINGTON: Drink, my dear. It makes the stage shorter. It makes the night shorter. It makes everything so much easier, for everyone.
+ [(Take the glass, and the powder.)]
    ELEANOR: As always.
    CUE: drink
    HARRINGTON: Good girl. There's my songbird.
    THOUGHT: The gin, then the powder. The mirror went soft at the edges, and so did she. She stopped being afraid of the stage somewhere between the two.
+ [(Push it away.) No. Not tonight. Not ever again.]
    ~ set_flag("eleanor_refused_drugs")
    HARRINGTON: ...
    HARRINGTON: That wasn't a question, my dear.
    THOUGHT: He set the mask down on the dressing table, very carefully, the way a man takes off his gloves.
- -> END

=== epilogue ===
DANIEL: The last entry. The handwriting's different. Shakier.
{
- has_flag("ending_8"):
    {
    - has_flag("killed_tony"):
        DANIEL: "A letter came to Joliet today, where I serve my time for Tony. No return address, a Chicago postmark, and inside it the rest of that night, in her hand."
    - has_flag("shot_bartender"):
        DANIEL: "We left Chicago the week after that coffee. Tony knew my face, and the men he pours for never forget one. A man doesn't bring that to his wife's door."
        DANIEL: "A letter came today, sent on by Caleb to the house downstate. No return address, a Chicago postmark, and inside it the rest of that night, in her hand."
    - else:
        DANIEL: "A letter came to Rose's house today. No return address, a Chicago postmark, and inside it the rest of that night, in her hand."
    }
    DANIEL: "The motel, the Order's men, the old man's gin she wouldn't drink. And what she did with his candlestick after I'd gone. I've copied it all into the pages before these, in her words. I owed her that much."
    DANIEL: "The Harrington house burned to the cellar the night I left it. The papers said a gas main. Nobody ever asked me, and I never said."
    DANIEL: "A week later the Tribune printed the old man's Thursday book, page by page: the girls, the trains, the men who paid. She had mailed it to them on her way out of the city. The Club never opened on a Thursday again."
    {has_flag("killed_tony"):
        DANIEL: "Rose knows. I passed her the letter across the visiting-room table. She read it twice, and folded it, and kept it."
    - else:
        DANIEL: "Rose knows. She read the letter at the kitchen table, and folded it, and put the kettle on."
    }
    DANIEL: ...So that's whose hand it was. Hers, copied out by his.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_9"):
    DANIEL: Wait. This isn't Micah's writing. It's signed... Father Caleb Jones.
    DANIEL: "My brother kept these pages honestly, as far as he knew. What he could not know, I have added from what she told the court, and what she told me again plainly afterwards, and asked me to set down. She said someone should write it down who wouldn't make her prettier than she was."
    {
    - has_flag("killed_tony"):
        DANIEL: "My brother serves his own sentence at Joliet, for a bartender called Tony; he walked in and gave himself up the morning after. Eleanor Harrington serves hers across the yard. I visit them both, the same Sunday. I am not sure which of them is freer."
    - has_flag("shot_bartender"):
        DANIEL: "Micah drinks coffee now, and goes to Mass with his wife, in a town downstate. The bartender he shot, Tony, knew his face, and the men Tony pours for looked for him all winter. Eleanor Harrington serves her sentence at Joliet. I visit them both. I am not sure which of them is freer."
    - else:
        DANIEL: "Micah drinks coffee now, and goes to Mass with his wife. Eleanor Harrington serves her sentence at Joliet. I visit them both. I am not sure which of them is freer."
    }
    DANIEL: "At her trial she named the Club, and the girls, and the trains, in open court. The Club's Thursdays ended with her testimony. She did, in one afternoon, what I had not the courage to do in all my years of silence. My brother called me a hypocrite for it. He was right."
    DANIEL: "Whoever reads this: she said no, twice, when no was the hardest word in Chicago. Remember that about her, if you remember anything."
    DANIEL: ...So that's whose hand it was. Caleb's.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_10"):
    DANIEL: "A year, near enough, since the prairie road. I haven't had a drink since that night. Some days that's the only thing I've done right. Some days it's enough."
    DANIEL: "She told me the rest of it in the car that night, the motel and the old man's gin, before she got out and walked off down the road. I wrote it in the way she said it. She went looking for her peace. I hope she found it."
    {
    - has_flag("killed_tony"):
        DANIEL: "And Tony. I went back and put a second bullet in him, on his back in that alley, so he couldn't tell anybody my name. Nobody's come for me. I hear every car that slows down outside."
        DANIEL: "I'm looking for my peace, but I know where it starts, and it starts at a police station. I write to Rose every Sunday. Every Sunday I sit at the back of a church where nobody knows me, and I don't go up for Communion. Not yet."
    - has_flag("shot_bartender"):
        DANIEL: "I'm looking for mine, though not in Chicago. Tony knows my face, and the men he pours for never forget one. I write to Rose every Sunday, care of Caleb, and every Sunday I sit at the back of a church in a town with one street. She hasn't written back yet. I'll keep writing."
    - else:
        DANIEL: "I'm looking for mine. I write to Rose every Sunday, and every Sunday I sit at the back of Caleb's church. She hasn't written back yet. I'll keep writing."
    }
    {has_flag("took_documents"):
        DANIEL: "I did what she asked with the old man's papers. I left them on the city desk at the Tribune, in an envelope with no name on it. The Club's Thursdays ended that winter."
    }
    DANIEL: ...So that's whose hand it was. Micah's, from what she told him on the road.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_11"):
    DANIEL: "She came once, and never again. I didn't expect her to. She told me the rest of it across the parlour table, the motel and the old man's gin, and I wrote it in that same night, so I wouldn't lose a word."
    DANIEL: "She said she hoped I'd find my peace. I'm trying. The Our Father every morning, start to finish. Caleb on the first Sunday of the month. A letter to Rose every week. Two came back. The third one, she kept."
    {
    - has_flag("killed_tony"):
        DANIEL: "They tried me for the old man. Then somebody found Tony behind the Blue Lantern, and they tried me for him too. I didn't deny it. Some things you can't say the Our Father over until you've said them out loud."
    - has_flag("shot_bartender"):
        DANIEL: "Tony's friends have friends in here. A man in the yard told me Tony sends his regards, and asks after my shoulder. I sleep with my back to the wall."
    }
    DANIEL: "Peace isn't a place you get to, Caleb says. It's a direction. I'm facing it, at least."
    DANIEL: ...So that's whose hand it was. Micah's, from across a prison table.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_1"):
    {has_flag("shot_bartender"):
        DANIEL: "We left Chicago the week after that cup of coffee, Rose and Tommy and me. Tony knew my face, and the men he pours for never forget one. A man doesn't bring that to his wife's door."
        INSET: vows
        DANIEL: "A year since that cup of coffee. Rose and I said our promises again at St. Anne's, a wooden Catholic church downstate. Caleb came down on the train and blessed us. Tommy stood up for me. He has her eyes and, God help him, my chin."
    - else:
        INSET: vows
        DANIEL: "A year since that cup of coffee. Rose and I said our promises again today, at Caleb's church. He blessed us. Tommy stood up for me. He has her eyes and, God help him, my chin."
    }
    DANIEL: "I don't need this journal anymore. A man doesn't need to write things down when he has somebody to tell them to."
    INSET: none
    {has_flag("took_documents"):
        DANIEL: "The old man's papers didn't stay in my coat. Caleb carried them into the Tribune himself, the morning after that coffee. He said he owed fourteen girls that walk."
        DANIEL: "A grand jury sat in the spring. The Club on Hubbard Street is a furniture showroom now. No more Thursdays, and no more girls off the trains."
    }
    {has_flag("caleb_escape"):
        DANIEL: "One more thing, so the pages are honest. What happened to Eleanor after the motel, she told Caleb at the edge of the city, the night he got her out of Chicago, and asked him to let me know. He did, a week later, over a cup of coffee. What she told him, I wrote in, and the rest I guessed."
    - else:
        DANIEL: "One more thing, so the pages are honest. What happened to Eleanor after the motel, Caleb passed on to me, months later: she came to Holy Name and told him, on the rectory steps, and asked him to let me know. What she told him, I wrote in, and the rest I guessed."
    }
    DANIEL: ...So that's whose hand those pages were. Micah's, guessing.
    DANIEL: ...Huh. He made it. He actually made it.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_2"):
    DANIEL: "She left again. The third time. Took the car, and what was left of the money."
    DANIEL: "She always comes back, and I always open the door. The bottle is the only one in this house that never lies to me."
    DANIEL: "She told me the rest of it in the car that night, the motel and the old man's gin. I wrote it down the way she said it. It's the only part of her I ever really had."
    {has_flag("killed_tony"):
        DANIEL: "And Tony, on his back in that alley, with my second bullet in him. She never asked what took me so long getting to the Gold Coast. I never said."
    }
    DANIEL: He got the girl. And then the girl got him.
- has_flag("ending_3"):
    DANIEL: "I see her every night. On the ceiling. At the bottom of the glass. The old man on the carpet, and the look on her face."
    {has_flag("killed_tony"):
        DANIEL: "Tony's up there with them. On his back in the rain, asking me why. He'd told me everything."
    }
    DANIEL: "One bullet left in the revolver. I always was bad at keeping things."
    {has_flag("mansion_exploded"):
        DANIEL: "What happened to her after the motel, I put together from what the Club's men said in court. She wasn't there to say it herself."
    - else:
        DANIEL: "What happened to her after the motel, I put together from what the Club's men said in court. She never testified. I never asked her."
    }
    DANIEL: So he never really knew. He wrote her pages from a courtroom bench.
    DANIEL: The rest of the page is stained. Whiskey... and something darker.
    DANIEL: ...Jesus, Micah.
- has_flag("ending_6"):
    DANIEL: "Rose came again today. She brought Tommy's drawings. She doesn't say she forgives me, and I don't ask her to."
    DANIEL: "I said the whole Our Father this morning, start to finish, the way Ma taught us. Caleb says I sound like a choirboy with a hangover."
    DANIEL: "I made a lot of awful choices, but now I know, I returned to the faith..."
    {
    - has_flag("killed_tony"):
        DANIEL: "I told that cop about Tony too. He wrote it down without looking up. Two men dead by my hand: Tony, so he couldn't name me, and then Harrington. Caleb says the Lord forgives that. Tony's mother doesn't, and I don't ask her to."
    - has_flag("shot_bartender"):
        DANIEL: "Tony's friends have friends in here. A man in the yard told me Tony sends his regards, and asks after my shoulder. I sleep with my back to the wall, and I say my prayers facing it."
    }
    {has_flag("took_documents"):
        DANIEL: "I gave that cop the old man's papers along with my confession. The girls' names were in them, and the prices, and the trains. They read them out at my trial."
        DANIEL: "The papers called it a scandal for a week. The Club never opened its doors on a Thursday again. That's the one thing I did in that house I'm not sorry for."
    }
    DANIEL: There's a note pinned to the page, in another hand: "She told me the rest herself, after the trial. I have written it in for him. - C."
    DANIEL: So that's whose hand it was.
    DANIEL: ...He found his way back. Behind bars, but he found it.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_7"):
    DANIEL: Wait. It isn't Micah's handwriting at all. It's signed... Father Caleb Jones.
    {has_flag("shot_eleanor"):
        DANIEL: "These are my brother's last pages, and he could not write them, so I have. I took them from what the Club's men said in court, and from what I could bear to imagine."
    - else:
        DANIEL: "These are my brother's last pages, and he could not write them, so I have. What happened to her before that night, she told me herself, after the funeral."
    }
    {has_flag("shot_eleanor"):
        DANIEL: "He shot Mr. Harrington on his own carpet. He shot the girl he had gone to save. Then he turned the revolver on himself. The papers called it a lovers' quarrel. It was not."
    - else:
        DANIEL: "He shot Mr. Harrington on his own carpet. The girl he had gone to save would not go with him, and there were men on the stairs. He turned the revolver on himself, in front of her. She lived. The papers called it a madman's grief. It was not."
        DANIEL: "She heard him ask forgiveness before the end. I don't know what that word weighed. God does."
    }
    {
    - has_flag("confessed_tony"):
        DANIEL: "Earlier that night a bartender named Tony was found behind the Blue Lantern. What else I know of it, I may not write."
    - has_flag("killed_tony"):
        DANIEL: "Earlier that night he had killed a bartender called Tony behind the Blue Lantern, a man who had already told him everything he wanted. I learned it from the police, afterwards."
    }
    DANIEL: "I prayed for him every day of his life, and I could not make him turn back. I pray for his soul still. Finishing his journal is the only thing that eases the pain."
    DANIEL: "If you are reading this, whoever you are, and whenever: do not walk in my brother's footsteps. It is never too late to turn around, until it is."
    DANIEL: ...
    DANIEL: I don't know if this is good for anyone else, but I'll respect Caleb's decision.
    DANIEL: I'll put the journal back. Maybe in a couple of years I'll give it to Leo...
- has_flag("ending_12"):
    DANIEL: "A year in Joliet. Life, the judge said. Caleb in the back row said Amen, like it was a Sunday."
    DANIEL: "I killed a man who'd already told me everything, so he couldn't tell anybody else. There's no prettier way to write it, so I won't try."
    {has_flag("spared_oldman"):
        DANIEL: "I said the Our Father in the old man's bedroom with a gun in my hand, and walked out without the Amen. I finished it on the station steps at sunrise, with Caleb holding my arm."
    - else:
        DANIEL: "I never got to the Gold Coast. Caleb walked me to the station on Maxwell Street that same night, holding my arm like we were boys crossing State Street."
    }
    {has_flag("took_documents"):
        DANIEL: "The old man's papers went in with my confession. The grand jury read every name. The Club's Thursdays are over, and that's the one debt I paid in full."
    }
    DANIEL: "Tony had a mother in Cicero. I write to her every month. She sends them back unopened. Caleb says that's not for her to answer. It's for me to send."
    DANIEL: "Rose comes on the first Sunday. She doesn't say she forgives me. Last month she brought Tommy."
    DANIEL: There's a note pinned to the page, in another hand: "She came to me months after, and told me all of it, and asked me to write it in. I have, for him. - C."
    DANIEL: So that's whose hand it was.
    DANIEL: ...A killer who walked himself into a cell. I don't know what to call that. Caleb would.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_13"):
    DANIEL: "Omaha. A rented room over a feed store, with one window, and it looks east. I keep the blind down."
    {has_flag("caleb_escape"):
        DANIEL: "I ran. The bell went off and the feet came down the stairs, and I ran, and left her in that house. A week later my brother walked her out of it. A priest with a poor-box envelope did what I couldn't, and I'm in Omaha."
        DANIEL: "Caleb found me, the way he always does. He writes care of general delivery. She told him the rest the night he got her out of Chicago, and asked him to pass it on, and he did. I've copied it into the pages before these. It's the only brave thing in this book, and none of it is mine."
    - else:
        DANIEL: "I ran. The bell went off and the feet came down the stairs, and I ran, and she's still in that house. The Club's car still pulls up at that door, and I'm in Omaha."
        DANIEL: "Caleb found me, the way he always does. He writes care of general delivery. She came to him in the spring, and told him, and asked him to pass it on, and he did. I've copied it into the pages before these. It's the only brave thing in this book, and none of it is mine."
    }
    DANIEL: "I never wrote to Rose. Better she thinks I'm at the bottom of the lake. Better for Tommy."
    DANIEL: "The revolver's on the washstand. Six in the cylinder. I only ever needed the one."
    DANIEL: So he found out in the end. From his brother's letters, in a room in Omaha.
    DANIEL: That's the last line. The rest of the page is blank.
    DANIEL: ...Jesus, Micah.
- has_flag("ending_14"):
    DANIEL: Wait. It isn't Micah's handwriting at all. It's signed... Father Caleb Jones.
    {has_flag("caleb_escape"):
        DANIEL: "These are my brother's last pages, and he could not write them, so I have. What happened to her before that night, she told me herself, at the edge of the city the night I got her out of Chicago, and asked me to set it down."
    - else:
        DANIEL: "These are my brother's last pages, and he could not write them, so I have. What happened to her before that night, she told me herself, the spring after, on the church steps, and asked me to set it down."
    }
    DANIEL: "He went to the Harrington house past midnight, for her, with a key a bartender had told him of. There was a bell on the kitchen door that the bartender had not told him of. It rang, and he heard them coming, and he could have run."
    DANIEL: "He went in. Two of the Club's men were waiting in the dark at the cook's table. They shot him on the kitchen tiles before he could finish her name."
    {has_flag("caleb_escape"):
        DANIEL: "The police wrote it down as a burglar, shot by the household. The old man's lawyers saw to that. A week after I buried him, I put her on a produce truck before dawn, out of Chicago. I do not know where she is now, and I have stopped asking. It is the one thing I did right that winter, and it came too late for him."
    - else:
        DANIEL: "The police wrote it down as a burglar, shot by the household. The old man's lawyers saw to that. She is still in that house. I see her at Mass on Sundays, and I can do nothing else, and God forgive me, it is not enough."
    }
    DANIEL: "He died walking toward her and not away. That is not repentance. But it was the right direction, and I hold on to it. I say Mass for him, and leave the rest to God's mercy."
    DANIEL: ...
    DANIEL: He never got to the end of the road. Caleb walked the last of it for him, on paper.
    DANIEL: I'll put the journal back. Maybe in a couple of years I'll give it to Leo...
- else:
    DANIEL: "Rose. Tommy. I know you won't come, and I don't blame you. I'd have stayed away from me too."
    DANIEL: "Tommy, be a better man than your father. It isn't a high bar. Rose, I'm sorry. I always was. I just never said it right."
    DANIEL: "They took my belt. They left me the sheets."
    {
    - has_flag("killed_tony"):
        DANIEL: "They tried me for the old man, and then for Tony. I didn't deny either. There was nobody left to lie for."
    - has_flag("shot_bartender"):
        DANIEL: "Tony's friends have friends in here. A man in the yard told me Tony sends his regards. I don't sleep much."
    }
    {has_flag("ending_4"):
        DANIEL: "Eleanor comes on Sundays. She told me the rest of it across the parlour table, a little every week. The motel. The old man's gin. I wrote it in. Somebody should."
    - else:
        DANIEL: There's a note pinned to the page, in another hand: "She told me the rest herself, after the trial. I have written it in for him. - C."
        DANIEL: So that's whose hand it was.
    }
    DANIEL: A goodbye letter. To his wife and his kid. He never sent it.
}
{not has_flag("ending_1") && not has_flag("ending_6") && not has_flag("ending_7") && not has_flag("ending_8") && not has_flag("ending_9") && not has_flag("ending_10") && not has_flag("ending_11") && not has_flag("ending_12") && not has_flag("ending_13") && not has_flag("ending_14"):
    DANIEL: That's enough of you for one lifetime, Micah Jones.
}
-> END