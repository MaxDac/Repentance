using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The cathedral steps. In Act 2 Micah ends up here, thinking about Eleanor, and goes in.</summary>
public partial class ChurchExterior : Room
{
    public override async Task OnEnter(string entry)
    {
        if (!State.HasFlag("act2_church") || State.HasFlag("act2_church_thought")) return;
        await Game.Run(async () =>
        {
            State.SetFlag("act2_church_thought");
            await Wait(0.6);
            await Say("I couldn't turn her in. I'd decided that in a motel room, with my shirt half buttoned.");
            await Say("So why couldn't I think of anything but her? Her voice. Her hair on the pillow. \"I can't go back there.\"");
            await Say("A man in my state ends up in one of two places. The bars knew me too well. So, the other one.");
            if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
            Player.Face(Facing.Up);
            await Game.ChangeRoom("church_interior", "start");
        });
    }
}
