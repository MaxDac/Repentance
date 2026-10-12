// REPENTANCE - all game dialogue.
// Lines are "SPEAKER: text" where SPEAKER is an actor/voice id in upper case. MICAH and DANIEL are the
// player character (DANIEL in the present-day prologue). Unprefixed lines are spoken by the player.
// Choice text is spoken by the player unless it starts with "(".
// Room scripts start conversations with DialogueManager.Instance.Talk("knot").

EXTERNAL has_item(id)
EXTERNAL has_flag(flag)
EXTERNAL cash_amount()
EXTERNAL give_item(id)
EXTERNAL take_item(id)
EXTERNAL set_flag(flag)

VAR pushes = 0

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
TEDDY: Don't crease it. The sitting alone cost more than your furniture.
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
    CONCIERGE: I make a point of seeing nothing. And of remembering less. That is why they pay me.
    ~ set_flag("concierge_stonewall")
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
{has_flag("knows_lantern"): -> bellboy.after}
{cash_amount() < 1:
    MICAH: His memory's for sale, and I'm a dollar short.
    -> END
}
BELLBOY: Now you're speaking my language, mister.
MICAH: One dollar. For your memory.
BELLBOY: The dame in the picture? Tuesday night. Left with a big fella. Broken nose, cheap suit, expensive cigar.
BELLBOY: Out the revolving door, toward State Street. Toward the Blue Lantern, if you catch my drift.
MICAH: The Blue Lantern?
BELLBOY: Speakeasy. Down the alley, steel door. You'll need the password.
BELLBOY: And no, I don't know it. A fella like that leaves matches everywhere, though. Cigarette butts, too. You could follow him by the ash.
~ set_flag("knows_lantern")
MICAH: Her room. The one she had Tuesday. I want a look.
BELLBOY: Front desk won't give you the time of day, never mind a key. That dollar buys the back way.
BELLBOY: Staff lift's in routing mode. Diagram's by the service door. Trace the branches to the fifth-floor linen room before you dispatch it.
BELLBOY: Staff door's by the palm. Linen room's right next to 507. Night maid bolts the corridor door, though.
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
* {cash_amount() >= 10} [(Give him ten dollars)]
    MICAH: Ten dollars. Maybe that'll open the door.
    SAL: ...
    SAL: That'll do.
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
NUN: This is a house of God, not a waiting room. What are you doing here, young man?
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
* [Right now, I'm not so sure.]
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
MICAH: I want you to come away. Not back to Teddy. Anywhere.
ELEANOR: I can't go back there...
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
MOC: Bruno. The gentleman is leaving.
BRUTE: This way, pal. Nice and easy. Or the other way.
-> END

=== moc_masked ===
MOC: Your invitation, brother.
MOC: ...Welcome. The rite is about to begin. Go on through to the stage.
-> END

=== moc_again ===
MOC: The stage, brother. They are waiting.
-> END

=== club_caught ===
LEADER: You returned Eleanor to us. For that, the intrusion is forgiven. This is as far as you go.
* [(Draw the revolver.)]
    ~ set_flag("drew_revolver")
    MICAH: Nobody move. Eleanor, come down off that stage. We're leaving.
    ELEANOR: Oh, Micah. You never did understand.
* [(Do nothing.)]
    MICAH: ...
    ELEANOR: Go home, Micah.
- -> END

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
MICAH: Right now, Caleb... I'm too far gone to be saved.
CALEB: That's crap, Micah.
CALEB: Forgive my language, Lord. But it is. No one is beyond salvation. Nobody. Not even you.
CALEB: A man who decides he's past saving has stopped listening to God and started listening to somebody else.
CALEB: That's the Devil's work, brother. It's the oldest trick he has.
CALEB: Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace.
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
    CALEB: Ask her yourself. She's still at the library, still putting the world in alphabetical order, as if that would make it behave.
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

// ---------------------------------------------------------------- ACT 2: AFTER THE CLUB

=== street_choice ===
* [(Go find Rose.)]
    ~ set_flag("go_rose")
* [(Push forward.)]
- -> END

=== rose_house ===
ROSE: Micah.
ROSE: It's past eleven. What are you doing here?
MICAH: I was passing by.
ROSE: Nobody passes by this street, Micah. You have no business being here. Not anymore.
- (opts)
+ {pushes == 0} [I came to say I'm sorry, Rose.]
    ~ pushes = 1
    ROSE: You always are. It's the one thing you were ever reliable about.
    -> opts
+ {pushes == 1} [I know what I did. I left you and Tommy alone, and I called it work.]
    ~ pushes = 2
    ROSE: You called it a lot of things. Tommy called it "When's Daddy coming home?" For a year.
    -> opts
+ {pushes == 2} [I'm not asking you to take me back. Just to forgive me.]
    ~ pushes = 3
    ROSE: Forgiving's the easy part, Micah. Forgetting is what you keep asking for.
    -> opts
+ {pushes == 3} [I've done something terrible this week. I need to hear it from somebody. From you.]
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
    }
    ROSE: Good night.
    -> END

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
{has_flag("rose_done"):
    ROSE: What do you want? Last time you were here, you wanted me to forgive you.
- else:
    ROSE: What do you want?
}
MICAH: Nothing you owe me.
MICAH: I'm not asking you to believe I've changed. I want to start showing you.
MICAH: Would you have a cup of coffee with me? Sometime. Daylight. A table between us.
ROSE: ...
ROSE: Coffee.
MICAH: Just coffee. You can bring Tommy, if he wants to see what his old man looks like.
ROSE: ...Why not.
-> END

=== caleb_club ===
CALEB: Micah. Twice in one week. People will start to talk.
MICAH: There's a club on Hubbard. No sign on the door, a man in a robe at the bell. They have Eleanor.
CALEB: ...I don't know anything about clubs.
- (opts)
* [You went as white as the altar cloth, Caleb.]
    CALEB: It's late, Micah. Go home.
    -> opts
* [They have her, Caleb. If you know anything, tell me.]
    CALEB: ...
    CALEB: There are women who go there. Performers, they call them. When the Club is done with them, the sisters at the convent take some of them in.
    CALEB: If anybody knows anything, it's the sisters. The convent is the best place to ask.
    -> rest
- (rest)
CALEB: But don't go, Micah. Give up this foolish search. Whatever she is to you, it isn't worth it.
MICAH: There isn't much left for me to do.
CALEB: You know that isn't true.
CALEB: The prodigal thought so too. Then he turned for home, and his father ran to meet him.
~ set_flag("caleb_club")
-> END

=== office_ring ===
MICAH: My wedding ring. On the desk, where I left it.
MICAH: Rose kept hers on long after I stopped coming home.
* [(Take the wedding ring.)]
    ~ set_flag("ring_taken_act2")
    ~ set_flag("took_faith_ring")
    ~ give_item("faith_ring")
    MICAH: A promise doesn't stop being a promise because I broke it.
* [(Leave the wedding ring in the office.)]
    ~ set_flag("ring_left_act2")
    MICAH: Not yet. I don't know how to carry it.
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
    ~ set_flag("cross_refused")
    MICAH: Keep it. I can't take it tonight.
    CALEB: I'll ask again when you come back.
- -> END

=== caleb_warn ===
CALEB: Sister Agatha telephoned. She said a man with your face pointed a gun at her.
MICAH: I asked nicely first.
CALEB: Repentance means more than asking nicely. Put the gun away.
CALEB: Micah, listen to me. Whatever you're about to do next, don't. Turn around. Go to Rose. Go anywhere else.
CALEB: There's still a way back. There always is. But not where you're going.
MICAH: Good night, Caleb.
-> END

=== caleb_last ===
CALEB: You've got that look. The one you had the night before you shipped out to France.
MICAH: I'm going back to the Club tonight. Dressed for the occasion.
CALEB: Then I can't stop you. I never could.
CALEB: God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him.
CALEB: I'll pray for you, brother. It's all you ever left me to do.
-> END

=== nun_club ===
NUN: You again. Twice in one week. You smell of whiskey and trouble, young man.
MICAH: There's a club on Hubbard Street. Eleanor Harrington is there. Father Jones says you take in their women.
NUN: I know nothing about clubs. I know nothing about their women. Go with God, Mr. Jones.
* [Where is she, sister?]
    NUN: I told you. I know nothing. Good night.
* [What happens in that club?]
    NUN: Nothing I would know about. Good night.
- (asked)
~ set_flag("nun_club_asked")
-> END

=== nun_threat2 ===
NUN: Are you crazy?!
MICAH: Yeah. You can say that, sister. Where's Eleanor? What goes on at that club?
NUN: You belong with that Jezebel. Burn with her, then. I am done with you.
NUN: She's a performer. She nearly had me fooled, the whore.
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
MICAH: Eleanor Harrington. The Club took her back tonight. Where is she?
BARTENDER: Are you out of your mind? Beat it, Jones. You don't know who these people are.
BARTENDER: They own judges. They own cops. They own the men who own the cops.
BARTENDER: You'd be better off with a bullet in your skull. Quicker. Cheaper, too.
* [(Shoot him in the leg.)]
    ~ set_flag("shot_bartender")
* {has_flag("can_walk_away")} [(Lower the gun. It's not worth it.)]
    MICAH: ...You're right, Tony. It's not worth it. None of it is.
    ~ set_flag("walked_away")
- -> END

=== bartender_shot ===
BARTENDER: AAAAH! My leg! You shot me, you crazy son of a...
MICAH: I've got five more. Where is she?
BARTENDER: The old man's! Harrington's place, on the Gold Coast! They took her to him tonight!
BARTENDER: Go round the back, to the kitchen. We bring the booze in that way, every Thursday.
BARTENDER: There's a key on the lintel over the kitchen door. Just walk in like the delivery boys do.
MICAH: Get that leg looked at, Tony. Tell them you slipped.
-> END

=== harrington_eleanor ===
HARRINGTON: There, now. It's not so bad, is it? Being back where you belong.
ELEANOR: ...
HARRINGTON: You ran to the nuns, and then to a drunk who calls himself a detective. And where did they bring you? Home.
HARRINGTON: Theodore will have you back. He always does. The Club will have you on Thursdays. And I will have you whenever I please.
ELEANOR: Yes, Mr. Harrington.
HARRINGTON: Good girl.
-> END

=== oldman_taunt ===
HARRINGTON: Well. Mr. Jones. My son's money paid for that coat, I believe.
MICAH: Get away from her.
HARRINGTON: Or what? You'll shoot an old man in his dressing gown? You haven't got the guts. You'd have done it by now.
HARRINGTON: And for whom? Look at her. She's a whore, Mr. Jones. A beautiful one, I grant you. But her place is here.
ELEANOR: Micah...
* [(Shoot him.)]
    ~ set_flag("shot_oldman")
* {has_flag("can_spare")} [(Lower the gun.)]
    MICAH: Yeah. I'm done with this. All of it.
    ~ set_flag("spared_oldman")
- -> END

=== eleanor_persuade ===
ELEANOR: You... you killed him. Micah, what have you done?
MICAH: Get dressed. We're leaving.
ELEANOR: Leaving? To go where? There's no place in this city they can't find me.
* [You can't stay here. Not now. They'll pin it on you.]
    ELEANOR: They'll pin it on whoever they like. They always do.
* [I didn't come all this way to leave you here, Eleanor.]
    ELEANOR: ...
    ELEANOR: You mean it. God help you, you actually mean it.
    ~ set_flag("eleanor_convinced")
* [He had it coming. They all do.]
    ELEANOR: And who decides that? You? With a gun in your hand?
- {has_flag("eleanor_convinced"): -> eleanor_comes}
ELEANOR: Please, Micah. Just go. Before they come.
* [Nobody's coming. The house is asleep.]
    ELEANOR: This house never sleeps.
* [I'll go to the police. I'll tell them everything.]
    ELEANOR: The police? The police dine here on Sundays.
* [Every time I've seen you, you've said you can't go back there. Now you don't have to.]
    ELEANOR: ...
    ~ set_flag("eleanor_convinced")
    -> eleanor_comes
- -> END

=== eleanor_comes ===
ELEANOR: All right. All right. Don't let go of my hand.
-> END

// ---------------------------------------------------------------- ACT 3: ENDINGS

=== ending_together ===
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
-> END

=== ending_alone ===
MICAH: The last fence post. The last streetlight. The last place a man goes to bury something.
MICAH: She wouldn't come with me. Even with him on the carpet and the whole Club on its way.
{has_flag("took_documents"):
    MICAH: I've got the old man's papers in my coat. Enough to keep the cops off me for the rest of my life.
}
{has_flag("mansion_exploded"):
    MICAH: The morning paper lists the dead. Eleanor Harrington. There it is, in black and white.
    MICAH: I told myself I was saving her. I left her there and lit the fuse.
    MICAH: They know who died. They don't know what I did.
}
MICAH: Free. That's the word for it. Free as a dog nobody wants.
-> END

=== prison_eleanor ===
ELEANOR: Hello, Micah.
MICAH: You came. The guard bet me a cigarette you wouldn't.
ELEANOR: They said a lot of things about you. In court, mostly.
MICAH: You were never in that courtroom. Not your name, not your face. I kept you out of it. Out of all of it.
ELEANOR: I know. And I'm grateful, Micah. I really am.
ELEANOR: But I have to go on from here. I'm going back to Theodore.
MICAH: To Teddy. After all of it.
ELEANOR: He's the only door that was ever open to me. You knew that, the first night.
ELEANOR: Goodbye, Micah.
-> END

=== prison_caleb ===
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

=== epilogue ===
DANIEL: The last entry. The handwriting's different. Shakier.
{
- has_flag("ending_1"):
    DANIEL: "A year since that cup of coffee. Rose and I renewed our vows today, at Caleb's church. Tommy stood up for me. He has her eyes and, God help him, my chin."
    DANIEL: "I don't need this journal anymore. A man doesn't need to write things down when he has somebody to tell them to."
    DANIEL: ...Huh. He made it. He actually made it.
    DANIEL: Maybe Leo would like to read it some day.
- has_flag("ending_2"):
    DANIEL: "She left again. The third time. Took the car, and what was left of the money."
    DANIEL: "She always comes back, and I always open the door. The bottle is the only one in this house that never lies to me."
    DANIEL: He got the girl. And then the girl got him.
- has_flag("ending_3"):
    DANIEL: "I see her every night. On the ceiling. At the bottom of the glass. The old man on the carpet, and the look on her face."
    DANIEL: "One bullet left in the revolver. I always was bad at keeping things."
    DANIEL: The rest of the page is stained. Whiskey... and something darker.
    DANIEL: ...Jesus, Micah.
- else:
    DANIEL: "Rose. Tommy. I know you won't come, and I don't blame you. I'd have stayed away from me too."
    DANIEL: "Tommy, be a better man than your father. It isn't a high bar. Rose, I'm sorry. I always was. I just never said it right."
    DANIEL: "They took my belt. They left me the sheets."
    DANIEL: A goodbye letter. To his wife and his kid. He never sent it.
}
{not has_flag("ending_1"):
    DANIEL: That's enough of you for one lifetime, Micah Jones.
}
-> END