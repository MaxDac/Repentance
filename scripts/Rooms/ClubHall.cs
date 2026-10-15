using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Club's entrance hall on Hubbard Street. The first time, the Master of Ceremonies stops Micah at the door and
/// has Bruno throw him out. Later Micah comes back masked and cloaked, with Harrington's invitation, and is let through.
/// </summary>
public partial class ClubHall : Room
{
    public override Track? Music => Track.ClubStrings;

    private bool Masked => State.HasFlag("masked");

    public override async Task OnEnter(string entry)
    {
        if (Masked)
        {
            if (State.HasFlag("moc_masked_seen")) return;
            State.SetFlag("moc_masked_seen");
            await Game.Run(async () =>
            {
                await Wait(0.5);
                await Think("The mask breathes back at me. It smells of cedar, and of whoever wore it before.");
                await Game.WalkTo(new Vector2(84, 222));
                Player.Face(Facing.Right);
                await Think("I hold out the invitation. I don't say a word. Nobody here does, it seems.");
                await Talk("moc_masked");
            });
            return;
        }
        if (State.HasFlag("club_out")) return;
        await Game.Run(ThrownOut);
    }

    private async Task ThrownOut()
    {
        await Wait(0.5);
        await Think("No sign, no doorman outside. Inside, a man dressed for a lodge meeting in the year of our Lord 1727.");
        await Game.WalkTo(new Vector2(78, 224));
        Player.Face(Facing.Right);
        await Talk("moc");
        await Game.WalkTo(new Vector2(98, 216));
        Player.Face(Facing.Right);
        await Talk("moc_eleanor");
        State.SetFlag("brute_called");
        if (FindActor("brute") is { } brute)
        {
            await brute.MoveTo(new Vector2(130, 228), 60);
            await Say("brute", "Out.");
            var leave = brute.MoveTo(new Vector2(70, 232), 40);
            await Game.WalkTo(new Vector2(36, 228));
            await leave;
        }
        State.SetFlag("club_out");
        State.SetFlag("on_map", false);
        await Game.ChangeRoom("street", "thrown_out");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("moc", Verb.Talk):
                await Talk("moc_again");
                return true;
            case ("moc", Verb.UseItem) when item == "revolver":
                await Say("A gun in here would be the last thing I ever pulled. They have a lot more members than I have bullets.");
                return true;
            case ("moc", Verb.UseItem) when item == "sealed_invitation":
                await Say("moc", "Yes, yes, brother. I have seen it. Go through.");
                return true;
            case ("moc" or "brute" or "guest", Verb.Hand or Verb.Kick):
                await Say("Not in a room full of them. Not wearing their face.");
                return true;
            case ("brute", Verb.Talk):
                await Say("I keep walking. He doesn't recognise me. Masks are a wonderful invention.");
                return true;
            case ("guest", Verb.Talk):
                await Say(Game.Pick("The mask turns toward me, and says nothing. It doesn't need to.",
                    "A nod, mask to mask. That's all the conversation there is in here.",
                    "Nobody talks in the hall. They're saving it for the stage."));
                return true;

            case ("street_door", Verb.Walk or Verb.Hand) when Masked:
                await Say("Not now. Eleanor's in there, past those curtains. I didn't climb a fire escape to stop at the hat check.");
                return true;
        }
        return false;
    }
}
