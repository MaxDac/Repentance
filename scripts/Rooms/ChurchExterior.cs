using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The cathedral steps. In Act 2 Micah ends up here, thinking about Eleanor, and goes in. In Act 3 Bruno dumps him
/// here after the Club, and Micah decides whether to keep going.
/// </summary>
public partial class ChurchExterior : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry == "beaten")
        {
            await Game.Run(Beaten);
            return;
        }
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

    /// <summary>Act 3: on the cathedral steps, beaten. Keep going for Eleanor, or give up and go to Rose.</summary>
    private async Task Beaten()
    {
        Player.SetPose("micah_supine");
        await Wait(1.5);
        await Say("Cathedral steps. Somebody has a sense of humour. Probably Bruno. Probably not.");
        await Say("My ribs are talking to each other. My mouth tastes like a penny.");
        await Say("What am I doing? She told me to go home. She looked at me like a stranger who'd wandered onto the stage.");
        await Say("Caleb's in there, a hundred feet away, praying for me. Rose is across town, not praying for anybody.");
        Player.SetPose(null);
        Player.Face(Facing.Down);
        await Wait(0.6);
        await Talk("beaten_choice");
        if (State.HasFlag("keep_going"))
        {
            await Say("Not yet. Not while she's in there with them.");
            State.SetFlag("micah_at_desk");
            await Game.ChangeRoom("office", "act3");
        }
        else
        {
            await Say("Enough. Enough for one life.");
            State.SetFlag(Endings.GaveUpSteps);
            await Act3.End();
        }
    }
}
