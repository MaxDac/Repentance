using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Club's dressing room, behind the stage (Second Interlude). Eleanor, in a short pink gown, at a mirror ringed
/// with bulbs; the old man, unmasked, with a glass of gin and a line of powder "as always". Taking it plays her drink
/// strip; refusing is saved ("eleanor_refused_drugs") and the scene cuts to black on "Noooo!". Either way the journal
/// goes back to Micah on the Club stage.
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
            await Say("harrington", "Sit down, my dear. We have a few minutes, you and I.");
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
            case ("mirror", Verb.Look):
                await Say("Twenty bulbs and a woman in the middle of them. She looks expensive. She looks tired.");
                return true;
            case ("mirror", Verb.Hand):
                await Say("Powder, lipstick, a curl pinned back. The face they paid for, put on one piece at a time.");
                return true;
            case ("table", Verb.Look):
                await Say("A glass of gin, already poured. A silver saucer beside it. He's thought of everything, as always.");
                return true;
            case ("rack", Verb.Look or Verb.Hand):
                await Say("Black gowns, dozens of them, for the members' wives. None of them is mine.");
                return true;
            case ("screens", Verb.Look or Verb.Hand):
                await Say("Painted cranes, flying away. Somebody here has a sense of humour.");
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
}
