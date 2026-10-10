// REPENTANCE - all game dialogue.
// Lines are "SPEAKER: text" where SPEAKER is an actor/voice id in upper case. MICAH and DANIEL are the
// player character (DANIEL in the present-day prologue). Unprefixed lines are spoken by the player.
// Choice text is spoken by the player unless it starts with "(".
// Room scripts start conversations with DialogueManager.Instance.Talk("knot").

EXTERNAL has_item(id)
EXTERNAL has_flag(flag)
EXTERNAL give_item(id)
EXTERNAL take_item(id)
EXTERNAL set_flag(flag)

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
    LEO: Definitely good.
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
DANIEL: "I won't tell anyone where they can find you." Then why write it all down, Micah?
-> END

=== attic_act2 ===
DANIEL: Morning, attic. Morning, dress form.
DANIEL: I barely slept. Kept seeing a man on his knees in an alley, a hundred years ago.
DANIEL: Right. Where were we, Micah?
-> END

=== journal_act2 ===
DANIEL: The next entry. Same steady hand, but the ink is darker. Pressed harder into the page.
DANIEL: "I told myself I was done with the Harringtons. Chicago had other plans."
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
    MICAH: Uh-huh. What business is the coat check girl in?
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
TEDDY: Don't crease it. The frame alone cost more than your furniture.
-> teddy.opts
= photo_then_case
~ give_item("photo")
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
* {has_item("photo")} [Have you seen this woman?]
    CONCIERGE: The Aurelian prides itself on discretion, sir.
    CONCIERGE: I see nothing. I remember less. It is why I am paid so handsomely.
    ~ set_flag("concierge_stonewall")
    -> concierge.opts
* [Nice place.]
    CONCIERGE: Thank you, sir. The marble is Italian. The clientele, increasingly, is not from anywhere respectable.
    -> concierge.opts
+ [(Leave)]
    CONCIERGE: Do enjoy your evening, sir. Elsewhere, ideally.
    -> END

=== bellboy ===
{has_flag("knows_lantern"): -> bellboy.after}
{has_flag("bellboy_wants_money"):
    BELLBOY: Back again, mister? My memory's still hungry.
- else:
    BELLBOY: Help you, mister? Bags? Directions? Gossip?
}
- (opts)
* [Gossip?]
    BELLBOY: Gossip costs extra. Everything costs extra in this joint.
    ~ set_flag("bellboy_wants_money")
    -> bellboy.opts
* {has_item("photo")} [Seen this lady?]
    BELLBOY: Maybe I have, maybe I haven't. My memory works better when it's been fed.
    ~ set_flag("bellboy_wants_money")
    -> bellboy.opts
* [How's business?]
    BELLBOY: Swell. Rich folks tip in advice. "Buy steel, kid." With what?
    -> bellboy.opts
+ [(Leave)]
    BELLBOY: I'll be here. I'm always here.
    -> END
= after
BELLBOY: Blue Lantern, mister. Steel door, State Street alley. You didn't hear it from me.
BELLBOY: And the lady's room is 507. Staff door, service elevator. You didn't hear that either.
-> END

=== bellboy_tip ===
BELLBOY: Now you're speaking my language, mister.
~ take_item("dollar")
BELLBOY: The dame in the picture? Tuesday night. Left with a big fella. Broken nose, cheap suit, expensive cigar.
BELLBOY: Out the revolving door, toward State Street. Toward the Blue Lantern, if you catch my drift.
MICAH: The Blue Lantern?
BELLBOY: Speakeasy. Down the alley, steel door. You'll need the password.
BELLBOY: And no, I don't know it. But a guy like that leaves matches everywhere. Butts too. Like a chimney with legs.
~ set_flag("knows_lantern")
MICAH: Her room. The one she had Tuesday. I want a look.
BELLBOY: Front desk won't give you the time of day, never mind a key. But that dollar buys you the back way.
BELLBOY: Staff door, by the palm. Service elevator to five, room 507. Maids leave it on the latch.
BELLBOY: Fair warning, mister: somebody already turned it over. And it wasn't housekeeping.
~ set_flag("staff_elevator")
-> END

// ---------------------------------------------------------------- SPEAKEASY

=== sal ===
{has_flag("sal_passed"): -> sal.after}
SAL: ...
SAL: Password.
- (opts)
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
* [(Fold a ten into his paw)]
    MICAH: Maybe Mr. Hamilton here knows the password.
    SAL: ...
    SAL: Yeah. Hamilton's a member.
    SAL: Go on in. Keep your hands where I can see 'em.
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
* [What've you got?]
    BARTENDER: Gin. Gin with ice. Gin that tastes like it was made in a bathtub. Because it was.
    -> bartender.opts
* [Nice place.]
    BARTENDER: It's a dump. But it's a dump with a band on Fridays.
    -> bartender.opts
* [I'm looking for a woman. Eleanor Harrington.]
    -> bartender.photo
+ [(Leave)]
    -> END
= photo
BARTENDER: ...
BARTENDER: Never heard of her. And I got a real bad memory for faces, pal. Especially faces that ask questions.
- (photo_opts)
* [She was seen leaving the Aurelian with one of your regulars.]
    BARTENDER: Lots of people get seen. Then one day they stop getting seen. Funny how that works.
    -> bartender.photo_opts
* [I could make it worth your while.]
    BARTENDER: Your money's no good here, mister. Your questions neither.
    -> bartender.photo_opts
+ [(Drop it)]
    -> END
= after
BARTENDER: The Starlight, pal. Now drink or leave.
-> END

=== bartender_dislike ===
BARTENDER: Hey. Gumshoe.
BARTENDER: You know what, I think I don't really like you at all.
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
NUN: This is a house of God, not a waiting room. What are you doing here, young man?
MICAH: Looking for someone. Eleanor Harrington.
NUN: And what would you want with her?
* [Her husband hired me to find her.]
    NUN: Her husband. Yes. I am sure he is very worried. About something.
* [I just want to know she's safe.]
    NUN: Men always say that. Usually just before they make a woman less safe.
- NUN: What is your name?
MICAH: Micah. Micah Jones.
NUN: Micah. Like the prophet. "He hath shewed thee, O man, what is good." Do you remember the rest?
MICAH: My mother did. I stopped listening somewhere around "walk humbly".
NUN: Then listen now, Micah. You would be better off finish the search now, and never have anything to do with that Jezebel.
MICAH: Jezebel? What do you mean by that?
NUN: ...
NUN: I have said too much already. It is not my place to judge. Only to pray.
NUN: Her room is the last door, at the end of the corridor. If you really want, you can have a look at it.
NUN: Then go. And God be with you, Micah Jones. You will need Him.
~ set_flag("nun_talked")
-> END
= again
NUN: The last door, at the end. Look if you must. Then go.
-> END

// ---------------------------------------------------------------- OUTSIDE THE CONVENT

=== eleanor_road ===
ELEANOR: Sister Agatha said a man came asking for me. A man with a split lip and a prophet's name.
ELEANOR: Why are you looking for me, Mr. Jones?
MICAH: Your husband hired me to bring you home.
ELEANOR: Teddy. Of course. And what do you get, if you bring me home?
* [Twenty dollars a day, plus expenses.]
    ELEANOR: Twenty a day. I used to spend that on gloves.
* [Right now? I'm not so sure anymore.]
    ELEANOR: That's the first honest thing a man has said to me in a month.
- ELEANOR: You're bleeding. Hold still.
MICAH: You do this for every man who comes looking for you?
ELEANOR: Only the ones who get beaten on my account. It's a short list. You're at the top of it.
MICAH: The sister called you a Jezebel.
ELEANOR: And what do you call me, Mr. Jones?
MICAH: I haven't decided yet. I'm not sure I want to.
ELEANOR: You could tell Teddy you never found me.
MICAH: I could. I'm a lousy liar.
ELEANOR: Then I'll teach you. It's easy. You just have to want something badly enough.
MICAH: Come away from here. Not back to Teddy. Anywhere.
ELEANOR: I can't return back there...
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
ELEANOR: Goodbye, Micah Jones.
MICAH: Goodbye, Eleanor.
-> END
= after
BARTENDER: The Starlight, pal. Now drink or leave.
-> END

// ---------------------------------------------------------------- THE STARLIGHT CLUB

=== harrington ===
{has_flag("harrington_met"): -> harrington.again}
HARRINGTON: You're blocking my view of the curtain, young man.
MICAH: Micah Jones. I work for your son.
HARRINGTON: Then you have my sympathies. Theodore Harrington. The one who built the steel mill, not the one losing it.
- (opts)
* [What brings you to a place like this?]
    HARRINGTON: The same thing as you, I expect. The singer.
    HARRINGTON: I've known Eleanor since her debut. The blonde hair was Teddy's idea. Everything else was hers.
    -> harrington.opts
* [What do you think of your son?]
    HARRINGTON: Teddy was a disappointment in short pants, and he has kept up the tradition.
    HARRINGTON: If he's hired a detective, Mr. Jones, he's frightened. Find out of what.
    -> harrington.opts
* [Enjoy the show.]
    HARRINGTON: At my age one enjoys everything. It might be the last time.
    ~ set_flag("harrington_met")
    -> END
= again
HARRINGTON: The singer is through the curtain, Mr. Jones. I'm only the audience.
-> END

=== eleanor ===
{has_flag("eleanor_met"): -> eleanor.again}
ELEANOR: Show's over, mister. Autographs are a dime, and I'm all out of pencils.
MICAH: Evening, Mrs. Harrington.
ELEANOR: ...Nobody's called me that in four days. They were four very nice days.
- (opts)
* [Your husband hired me to bring you home.]
    ELEANOR: Teddy didn't hire you to find me. He hired you to find what I took.
    MICAH: And what did you take?
    ELEANOR: His other set of books.
    -> eleanor.opts
* [What's in the books?]
    ELEANOR: Teddy owes Vincent Moretti more than Harrington Steel is worth. He's been paying with the company's money.
    ELEANOR: When the company bookkeeper found out, he went for a drive past the city limits. He didn't drive back.
    -> eleanor.opts
* [Who's been hiding you?]
    ELEANOR: A priest at the cathedral. Father Caleb Jones. He found me a bed and this job.
    MICAH: Jones.
    ELEANOR: A relative of yours?
    MICAH: My kid brother. We haven't spoken in six years.
    ELEANOR: He prays for you, you know. Every night. I've heard him.
    -> eleanor.opts
* [How do I help you?]
    ELEANOR: I wrote everything down in my diary. I left it in the vanity at the Aurelian when I ran. Suite 4.
    ELEANOR: Moretti's men watch the lobby. I can't go back. You can.
    ~ give_item("key")
    ELEANOR: Take my key. Bring the diary to Father Caleb. He'll know what to do with it.
    MICAH: And you?
    ELEANOR: I'll be here. Singing about men who never come back.
    ~ set_flag("eleanor_met")
    -> END
= again
ELEANOR: The Aurelian, suite 4. Then the cathedral. Please, Mr. Jones.
-> END

// ---------------------------------------------------------------- CATHEDRAL

=== caleb_act2 ===
CALEB: Can I help you, my son?
CALEB: ...Micah?
MICAH: Hello, Caleb. Or is it "Father" now?
CALEB: Six years. You look like a man who hasn't slept for most of them.
~ set_flag("caleb_met")
MICAH: I didn't come to confess. I came to talk. There's a difference, isn't there?
CALEB: Not as much as you'd like. Sit. The pews don't charge by the hour.
MICAH: There's a woman. I was paid to find her. I found her, and then I let her go.
MICAH: And I can't stop thinking about her. Or about what I did this week. What I let happen.
MICAH: Right now, Caleb... I'm too far off to be saved.
CALEB: That's crap, Micah.
CALEB: Forgive my language, Lord. But it is. No one is beyond salvation. Nobody. Not even you.
CALEB: A man who decides he's past saving has stopped listening to God and started listening to somebody else.
CALEB: That's the Devil's work, brother. It's the oldest trick he has.
MICAH: I'll think about that.
MICAH: ...Coming here was a mistake.
CALEB: Micah, wait-
-> END

=== caleb ===
{has_flag("library_lead"): -> caleb.after}
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
    CALEB: Ask her yourself. She's still at the library, still alphabetizing the world into making sense.
    CALEB: She keeps your picture in her desk drawer. Face down. But she keeps it.
    MICAH: That's something.
    -> caleb.opts
* {has_item("diary")} [Eleanor sent me with this.]
    ~ take_item("diary")
    CALEB: Her diary. She trusted you with it. That's more than she trusted me.
    CALEB: ...Here. "Teddy's ledger is safe. Among a hundred thousand books, where nobody reads."
    CALEB: The public library, Micah. Rose's library.
    MICAH: Of all the bookshelves in Chicago.
    CALEB: God has a sense of humor. Mostly at our family's expense.
    ~ set_flag("library_lead")
    -> END
+ [(Leave)]
    CALEB: Go with God, Micah. He's been waiting for you longer than I have.
    -> END
= after
CALEB: The library. And Micah... be kind to her.
-> END

// ---------------------------------------------------------------- LIBRARY

=== librarian ===
{has_flag("librarian_refused"): -> librarian.again}
{not has_flag("librarian_met"):
    LIBRARIAN: Shh. The reading room closes at ten, sir. What can I do for you?
    ~ set_flag("librarian_met")
- else:
    LIBRARIAN: Yes?
}
- (opts)
* {has_item("mirror")} [I want to know about a symbol.]
    MICAH: Three loops in one knot. Scratched into the back of a lady's mirror.
    IMAGE: triquetra
    LIBRARIAN: ...
    LIBRARIAN: Where did you get that mirror?
    MICAH: That's between me and the mirror.
    LIBRARIAN: Then what that knot means is between me and my books. Good evening, sir.
    ~ set_flag("librarian_refused")
    -> END
* [Where's the day librarian? Mrs. Jones.]
    LIBRARIAN: Mrs. Jones keeps Christian hours, sir. I keep the other kind.
    -> librarian.opts
+ [(Leave)]
    LIBRARIAN: Mind the step. And the silence.
    -> END
= again
LIBRARIAN: I've nothing to say to a man who won't tell me where he gets his mirrors.
-> END

=== librarian_threat ===
MICAH: Let's try that again. Slower, this time.
LIBRARIAN: Good Lord. Put that away! This is a library!
MICAH: Then keep your voice down. The knot.
LIBRARIAN: C-Celtic. A triquetra. Old, very old, from before the saints ever reached Ireland.
LIBRARIAN: Groves and wells and fires on the hilltops. Rites nobody has any business remembering.
LIBRARIAN: There's a book. "Rites of the Old Isles." A rare thing. We had a request for it just last month.
LIBRARIAN: Take it. Take it and go away, and please don't come back.
~ give_item("book")
MICAH: Pleasure doing business. Late fees are on me.
-> END

=== rose ===
{not has_flag("rose_met"):
    ROSE: We're closing, sir, so unless you have a card-
    ROSE: ...Micah.
    MICAH: Hello, Rose.
    ROSE: Eight months without a word, and you walk in here dripping on my floor.
    ~ set_flag("rose_met")
- else:
    ROSE: You're still here. That's a first.
}
- (opts)
* [I'm sorry.]
    ROSE: You always are. It's the one thing you were ever reliable about.
    -> rose.opts
* [You look well.]
    ROSE: I sleep now. Nobody calls at three in the morning to say you're in the hospital again.
    -> rose.opts
* {has_flag("library_lead")} [A woman hid something here. Dark hair, about this tall.]
    ROSE: Last Tuesday. She asked for the county land records, then asked to be left alone.
    ROSE: Right-hand stacks, top shelf. Nobody has touched those since the Taft administration.
    ROSE: Is she in trouble?
    MICAH: She's in the kind of trouble I'm good at.
    ROSE: That's what worries me.
    ~ set_flag("rose_tip")
    -> END
+ [(Leave)]
    ROSE: Goodbye, Micah. Try the front door this time. You used to prefer the window.
    -> END

// ---------------------------------------------------------------- THE OUTSKIRTS

=== ending ===
SAL: Hey. Gumshoe.
SAL: Nice night for digging.
SAL: Mr. Moretti would like a word. In private. Bring the box.
MICAH: Funny. I was just about to ask for one.
-> END