using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The Starlight's lounge, where Teddy's father watches the stage curtain.</summary>
public partial class ClubLounge : Room
{
    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("harrington", Verb.Talk):
                await Talk("harrington");
                return true;
            case ("harrington", Verb.UseItem) when item == "photo":
                await Say("harrington", "Eleanor. She looked like that at her wedding. Like somebody waiting for a train out.");
                return true;
            case ("harrington", Verb.Hand or Verb.Kick):
                await Say("harrington", "Young man, I have outlived two wars and three business partners. Don't.");
                return true;
        }
        return false;
    }
}
