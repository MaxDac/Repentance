using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The road outside the convent. Eleanor is waiting, dressed in black. Nobody else is around.</summary>
public partial class ConventRoad : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("eleanor_found")) return;
        await Game.Run(async () =>
        {
            await Wait(0.8);
            if (FindActor("eleanor") is { } eleanor)
                await Game.WalkTo(eleanor.Position + new Godot.Vector2(-44, 4));
            Player.Face(Facing.Right);
            await Talk("eleanor_road");
            State.SetFlag("eleanor_found");
            await Wait(0.8);
            await Game.ChangeRoom("motel_night", "start");
        });
    }
}
