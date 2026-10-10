using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The Aurelian Hotel lobby: marble, brass and people who have seen nothing.</summary>
public partial class Lobby : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_lobby")) return;
        State.SetFlag("seen_lobby");
        await Game.Run(() => Say("The Aurelian. Where the rich come to forget, and the help is paid to forget harder."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("concierge", Verb.Talk):
                await Talk("concierge");
                return true;
            case ("concierge", Verb.UseItem) when item == "dollar":
                await Say("concierge", "A single dollar, sir? That is not a bribe. That is an insult.");
                return true;
            case ("concierge", Verb.UseItem) when item == "photo":
                await Say("concierge", "A lovely portrait, sir. I have never seen her in my life. Or yours.");
                return true;

            case ("bellboy", Verb.Talk):
                await Talk("bellboy");
                return true;
            case ("bellboy", Verb.UseItem) when item == "dollar":
                await Talk("bellboy_tip");
                return true;
            case ("bellboy", Verb.UseItem) when item == "photo":
                await Say("bellboy", "Pretty. But pictures don't pay my rent, mister.");
                return true;

            case ("bell", Verb.Hand or Verb.Kick):
                await Say("Ding.");
                await Say("concierge", "I am standing directly in front of you, sir.");
                return true;

            case ("urn", Verb.Hand or Verb.Kick):
                await Say("Nothing in there but sand and cigar stubs.");
                return true;

            case ("service_door", Verb.Walk or Verb.Hand) when State.HasFlag("staff_elevator"):
                await Say("Staff elevator. Fifth floor, room 507. Nobody looks twice at a man who uses the back door.");
                await Game.ChangeRoom("eleanor_room", "lobby");
                return true;
            case ("service_door", Verb.Walk or Verb.Hand):
                await Say("Staff only. And the concierge is watching it like it owes him money.");
                return true;
            case ("service_door", Verb.Kick):
                await Say("Kicking down a door in the lobby. Subtle, Micah.");
                return true;

            case ("revolving_door", Verb.Walk or Verb.Hand) when !State.HasFlag("knows_lantern") || State.HasFlag("club_lead"):
                await Game.ChangeRoom("street", "lobby");
                return true;
            case ("revolving_door", Verb.Kick):
                await Say("It's a revolving door. It only goes round in circles. Like this case.");
                return true;

            case ("elevator", Verb.Hand or Verb.Kick):
                await Say("\"Out of order.\" In a joint this fancy? Somebody upstairs is paying for privacy.");
                return true;
            case ("palm", Verb.Hand):
                await Say("I've got nowhere to put a palm tree. I barely have somewhere to put me.");
                return true;
            case ("cubbies", Verb.Hand):
                await Say("Not with the concierge watching me like a hawk with a promotion.");
                return true;
        }
        return false;
    }
}
