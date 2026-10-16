using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Club's dressing room, behind the stage (Second Interlude). Eleanor, in a short pink gown, at a mirror ringed
/// with bulbs; the old man, unmasked, with a glass of gin and a line of powder "as always". Taking it plays her drink
/// strip; refusing is saved ("eleanor_refused_drugs") and the scene cuts to black on "Noooo!". Either way the journal
/// goes back to Micah on the Club stage. Before he talks, she has to put the face on (Puzzle 18): face powder and
/// a puff, then the lipstick, then a pin for the curl, each one a step back into the life she wants to leave.
/// </summary>
public partial class ClubBackstage : Room
{
    public override Track? Music => Track.ClubStrings;

    public override async Task OnEnter(string entry)
    {
        if (entry != "interlude2") return;
        await Game.Run(async () =>
        {
            await Wait(0.6);
            await Think("The dressing room behind the stage. Bulbs round the mirror, and a pink gown that wouldn't keep a cat warm.");
            await Say("harrington", "Look at the state of you. Put your face on, my dear. They didn't pay to see you.");
            await Think("Her compact and her lipstick waited on the ledge under the bulbs, where she had left them on Tuesday. A lifetime ago.");
        });
    }

    public override async Task OnCue(string cue)
    {
        if (cue == "drink") await Player.PlayPose("eleanor_drink");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("harrington", Verb.Talk) when !MadeUp:
            case ("table", Verb.Hand) when !MadeUp:
                if (FindActor("harrington") is { } waiting) Player.FaceTowards(waiting.Position);
                await Say("harrington", "Put your face on first, my dear. We'll talk when you look like yourself.");
                await Think("Like herself. He meant the other one. The one in the bulbs.");
                return true;
            case ("harrington", Verb.Talk):
            case ("table", Verb.Hand):
                if (FindActor("harrington") is { } oldman) Player.FaceTowards(oldman.Position);
                await Talk("interlude_oldman");
                if (State.HasFlag("eleanor_refused_drugs"))
                {
                    await Game.Hud.Fade(1, 0.15);
                    await Wait(0.4);
                    Game.Hud.ShowCaption("Noooo!");
                    await Wait(2.2);
                    Game.Hud.ShowCaption(null);
                    await Wait(0.8);
                }
                else
                {
                    Player.SetPose(null);
                    await Think("Somewhere past the curtain, the band started up. Her cue. It always came.");
                }
                await Story.Interlude.EndSecond();
                return true;
            case ("harrington", Verb.Look):
                await Say("The old man, without his stag's head for once. He looks more like an animal without it.");
                return true;
            case ("harrington", Verb.Hand or Verb.Kick):
                await Say("Bruno's outside the door. And the old man knows it.");
                return true;
            case ("mirror", _) when verb is Verb.Look or Verb.Hand or Verb.UseItem:
                await Mirror(verb, item);
                return true;
            case ("harrington", Verb.UseItem):
                await Say("Not for him. Nothing of mine is for him. Not anymore.");
                return true;
            case ("table", Verb.Look):
                await Say("A glass of gin, already poured. A silver saucer beside it. He's thought of everything, as always.");
                return true;
            case ("rack", Verb.Look):
                await Say("Black silk, dozens of gowns, for the members' wives. I used to think a dress like that would keep me safe.");
                if (!State.HasFlag("interlude_took_puff")) await Say("Something white and soft, peeking out of a pocket.");
                return true;
            case ("rack", Verb.Hand) when !State.HasFlag("interlude_took_puff"):
                State.SetFlag("interlude_took_puff");
                State.GiveItem("puff");
                await Say("A swansdown puff, left in a gown pocket. Some wife sat at that mirror before me and covered the same things.");
                await Think("Silk on every hook, money in every seam, a car at the door whenever she wanted one. All of it hers, for as long as she smiled. That was the whole price. Only that.");
                return true;
            case ("rack", Verb.Hand):
                await Say("None of them is mine. All of them could be. That's the trouble.");
                return true;
            case ("screens", Verb.Look):
                await Say("Painted cranes, flying away. Somebody here has a sense of humour.");
                if (!State.HasFlag("interlude_took_pin")) await Say("A hairpin's caught in the silk, in one crane's wing.");
                return true;
            case ("screens", Verb.Hand) when !State.HasFlag("interlude_took_pin"):
                State.SetFlag("interlude_took_pin");
                State.GiveItem("hairpin");
                await Say("A hairpin, stuck through a crane's wing. Even the birds in here are pinned down.");
                await Think("She could fly too. Out the stage door, past Bruno, into the snow in a pink gown. She would last a night. Two, maybe. And then where? Back here, on her knees, asking.");
                return true;
            case ("screens", Verb.Hand):
                await Say("I've watched those cranes every night for a year. They never get anywhere either.");
                return true;
            case ("door", Verb.Look):
                await Say("The door to the stage. Bruno's on the other side of it, breathing.");
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await Say("The only door out of here goes to the stage. And he hasn't finished with me.");
                return true;
        }
        return false;
    }

    private bool MadeUp => State.HasFlag("interlude_made_up");

    private const string Order = "Face powder first. Then the mouth. Then the hair. The face they paid for, one piece at a time.";

    /// <summary>
    /// Puzzle 18: the makeup comes off the ledge, then goes on in order. Every step is a choice she half makes: she
    /// wants out, and she paints herself back in.
    /// </summary>
    private async Task Mirror(Verb verb, string? item)
    {
        if (MadeUp)
        {
            await Say(verb == Verb.Look
                ? "That's her. The songbird. I'd almost forgotten there was anybody underneath."
                : "Done. Don't look too close, Eleanor. Nobody else will.");
            return;
        }
        if (verb == Verb.Look)
        {
            await Say("Twenty bulbs and a woman in the middle of them. She looks expensive. She looks tired.");
            await Say(Order);
            return;
        }
        if (verb == Verb.Hand)
        {
            if (State.HasFlag("interlude_took_makeup"))
            {
                await Say(Order);
                return;
            }
            State.SetFlag("interlude_took_makeup");
            State.GiveItem("compact");
            State.GiveItem("lipstick");
            await Say("My compact and my lipstick. Gold cases, both of them. He bought me both.");
            await Think("She held them the way you hold the key to a house you're afraid to go home to.");
            await Say("The puff's gone from the compact. Somebody borrowed it. Nobody gives anything back here.");
            return;
        }

        var powdered = State.HasFlag("interlude_powdered");
        var lips = State.HasFlag("interlude_lips");
        switch (item)
        {
            case "puff_powdered" when !powdered:
                State.TakeItem("puff_powdered");
                State.SetFlag("interlude_powdered");
                await Say("Face powder over the shadows under my eyes. Over the marks on my wrist, where he held it.");
                await Think("Every pass of the puff, a little less of Eleanor. It was easier that way. It had always been easier.");
                return;
            case "lipstick" when powdered && !lips:
                State.TakeItem("lipstick");
                State.SetFlag("interlude_lips");
                await Say("The mouth next. Red, the way he likes it. The smile goes on with it.");
                await Think("She tried it in the glass. Grateful. Willing. A girl who wants for nothing. And she did want for nothing. That was the trouble.");
                return;
            case "hairpin" when lips:
                State.TakeItem("hairpin");
                State.SetFlag("interlude_made_up");
                await Say("And a curl pinned back, so it won't fall in my eyes when I sing. Pinned in place. Like the cranes.");
                await Think("She looked at the woman in the bulbs and wanted, more than anything, to wipe her off with the back of her hand.");
                await Say("I could stop. Tonight. I could just... stop.");
                await Think("Her hand didn't move. The silk, the car, the big house, the quiet when she did as she was told. And beneath all of it the smell of him, of all of them, sweet and rotten.");
                await Say("harrington", "There. Now you look like yourself. Sit down, my dear. We have a few minutes, you and I.");
                await Think("Like herself. She nearly laughed. She nearly cried. She did neither. It would only spoil the face.");
                return;
            case "puff_powdered":
                await Say("The face powder's on. Any more and I'll look like a corpse. Maybe that's the idea.");
                return;
            case "compact" or "puff":
                await Say("Face powder with my fingers would streak. The puff and the compact, together.");
                return;
            case "lipstick" when lips:
                await Say("The mouth is on. Red enough to fool anybody.");
                return;
            case "lipstick" or "hairpin":
                await Say("Not on a bare face. " + Order);
                return;
            default:
                await Say("That's not part of the face.");
                return;
        }
    }
}
