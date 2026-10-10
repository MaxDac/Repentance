using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Act 2: the map of Chicago. Micah picks where to look for Eleanor next.</summary>
public partial class ChicagoMap : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("map_seen")) return;
        State.SetFlag("map_seen");
        await Game.Run(() => Say("I have to find her again."));
    }

    // nobody walks on a map
    public override Vector2 ClampWalkTarget(Vector2 target) => Player.Position;

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (verb == Verb.UseItem)
        {
            await Say("I'd rather not leave anything on this map. It goes where I go.");
            return true;
        }
        if (verb is Verb.Kick or Verb.Talk)
        {
            await Say(verb == Verb.Kick ? "Kicking Chicago. Half the city would line up for a turn." : "Chicago never listened to me before.");
            return true;
        }
        if (verb == Verb.Look) return false;
        switch (target.Id)
        {
            case "library" when State.HasFlag("library_banned"):
                await Say("Better not show my face there for the time being.");
                return true;
            case "library":
                await Game.ChangeRoom("library", "start");
                return true;
            case "church":
                await Say("Caleb's sermons can wait. Coming there was a mistake once already.");
                return true;
            case "office":
                await Game.ChangeRoom("office", "door");
                return true;
            case "club":
                State.SetFlag("on_map", false);
                await Game.ChangeRoom("club_hall", "from_street");
                return true;
        }
        return false;
    }
}
