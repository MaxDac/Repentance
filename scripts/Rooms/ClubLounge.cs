using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The Club's lounge: masked members waiting for the rite on the stage beyond the curtain.</summary>
public partial class ClubLounge : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_club_lounge")) return;
        State.SetFlag("seen_club_lounge");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Sofas full of white faces and carved animal heads, and not one of them a face. Half the city council could be in this room.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("guest", Verb.Talk):
                await Say(Game.Pick("I lean in. The mask leans back. Neither of us says a word.",
                    "She looks through me, like I'm the one wearing a mask. I am.",
                    "A man nods at me and points at the stage curtain. It's starting."));
                return true;
            case ("guest", Verb.Hand or Verb.Kick):
                await Say("Start a fight in here, and I'd be the one on the stage tonight.");
                return true;
            case ("guest", Verb.UseItem) when Shows(item, "photo", "eleanor"):
                await Say("Show Eleanor's photograph to a room full of masks. They'd know who I was before I put it away.");
                return true;
        }
        return false;
    }
}
