// REPENTANCE - all game dialogue.
// Lines are "SPEAKER: text" where SPEAKER is an actor id in upper case (MICAH = the player).
// Choice text is spoken by Micah unless it starts with "(".
// Room scripts start conversations with DialogueManager.Instance.Talk("knot").

EXTERNAL has_item(id)
EXTERNAL has_flag(flag)
EXTERNAL give_item(id)
EXTERNAL take_item(id)
EXTERNAL set_flag(flag)

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
* {has_item("matchbook")} [Sweet Caroline's sister.]
    SAL: ...
    SAL: Go on in. Keep your hands where I can see 'em.
    ~ set_flag("sal_passed")
    -> END
+ [(Leave)]
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
* {has_item("photo")} [Seen her around?]
    -> bartender.photo
+ [(Leave)]
    -> END
= photo
BARTENDER: ...
BARTENDER: Put that away, pal. Put it away right now.
BARTENDER: You know whose girl that is now? No, you don't. Nobody does. That's how it stays.
~ set_flag("photo_shown")
-> END
= after
BARTENDER: I got nothing more to say to you, pal. Drink or leave.
-> END

=== ending ===
SAL: Hey. Gumshoe.
SAL: Mr. Moretti would like a word. In private.
MICAH: Funny. I was just about to ask for one.
-> END
