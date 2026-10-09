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
            case ("concierge", Verb.TalkTo):
                await Talk("concierge");
                return true;
            case ("concierge", Verb.Give) when item == "dollar":
                await Say("concierge", "A single dollar, sir? That is not a bribe. That is an insult.");
                return true;
            case ("concierge", Verb.Give or Verb.Use) when item == "photo":
                await Say("concierge", "A lovely portrait, sir. I have never seen her in my life. Or yours.");
                return true;

            case ("bellboy", Verb.TalkTo):
                await Talk("bellboy");
                return true;
            case ("bellboy", Verb.Give) when item == "dollar":
                await Talk("bellboy_tip");
                return true;
            case ("bellboy", Verb.Give or Verb.Use) when item == "photo":
                await Say("bellboy", "Pretty. But pictures don't pay my rent, mister.");
                return true;

            case ("bell", Verb.Use or Verb.Push):
                await Say("Ding.");
                await Say("concierge", "I am standing directly in front of you, sir.");
                return true;

            case ("urn", Verb.PickUp or Verb.Open or Verb.Use or Verb.Pull):
                if (State.HasItem("matchbook") || State.HasFlag("found_matchbook"))
                {
                    await Say("Nothing left in there but sand and cigar stubs.");
                    return true;
                }
                State.SetFlag("found_matchbook");
                State.GiveItem("matchbook");
                await Say("Under the sand and a dozen cigar stubs... a matchbook. Blue Lantern. Somebody wrote inside it.");
                return true;

            case ("revolving_door", Verb.WalkTo or Verb.Open or Verb.Push) when !State.HasFlag("knows_lantern"):
                await Say("Back out into the rain? Not until I know where I'm going.");
                return true;
            case ("revolving_door", Verb.Push):
                await Game.ChangeRoom(target.ExitTo, target.ExitEntry);
                return true;

            case ("elevator", Verb.Use or Verb.Open or Verb.Push):
                await Say("\"Out of order.\" In a joint this fancy? Somebody upstairs is paying for privacy.");
                return true;
            case ("palm", Verb.PickUp):
                await Say("I've got nowhere to put a palm tree. I barely have somewhere to put me.");
                return true;
            case ("cubbies", Verb.PickUp or Verb.Open):
                await Say("Not with the concierge watching me like a hawk with a promotion.");
                return true;
        }
        return false;
    }
}
