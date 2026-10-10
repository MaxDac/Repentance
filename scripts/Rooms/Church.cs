using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The cathedral interior: a little peace, and a lot of guilt.</summary>
public partial class Church : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry == "map")
        {
            await Game.Run(FromMap);
            return;
        }
        if (State.HasFlag("act2_church"))
        {
            await Act2Visit();
            return;
        }
        if (State.HasFlag("seen_church_interior")) return;
        State.SetFlag("seen_church_interior");
        await Game.Run(() => Say("The nave swallowed the street noise whole. Even my footsteps sounded guilty in here."));
    }

    /// <summary>Act 2: Micah talks to his brother, then walks out on him and onto the streets of Chicago.</summary>
    private Task Act2Visit() => Game.Run(async () =>
    {
        State.SetFlag("seen_church_interior");
        await Wait(0.4);
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        await Talk("caleb_act2");
        State.SetFlag("act2_church", false);
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    });

    /// <summary>
    /// Act 2, from the map: after the Club, Micah presses Caleb about it; later visits only get warnings, and whether
    /// Micah came back before Harrington's office and before the Club is remembered.
    /// </summary>
    private async Task FromMap()
    {
        await Wait(0.4);
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        if (!State.HasFlag("caleb_club"))
        {
            await Talk("caleb_club");
            // Micah doesn't answer that one. He just leaves.
            await Wait(1.2);
        }
        else if (State.HasFlag("harrington_done"))
        {
            State.SetFlag("church_before_club");
            await Talk("caleb_last");
        }
        else
        {
            State.SetFlag("church_before_office");
            await Talk("caleb_warn");
        }
        await LeaveToMap();
    }

    private async Task LeaveToMap()
    {
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("doors", Verb.Walk or Verb.Hand) when State.HasFlag("club_out"):
                await Game.ChangeRoom("chicago_map", "start");
                return true;
            case ("caleb", Verb.Talk):
                await Talk("caleb");
                return true;
            case ("caleb", Verb.UseItem) when item == "diary":
                await Talk("caleb");
                return true;
            case ("caleb", Verb.UseItem) when item == "photo":
                await Say("caleb", "Eleanor. She sat in that pew for two nights before she said a word. Is she safe?");
                return true;
            case ("caleb", Verb.Hand):
                await Say("The last time I touched my brother it was with a fist. Not tonight.");
                return true;
            case ("confessional", Verb.Walk or Verb.Hand):
                await Say("Not tonight. It'd take more than one Saturday to get through my list.");
                return true;
        }
        return false;
    }
}
