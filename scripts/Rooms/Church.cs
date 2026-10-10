using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The cathedral interior: a little peace, and a lot of guilt.</summary>
public partial class Church : Room
{
    public override async Task OnEnter(string entry)
    {
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

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
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
