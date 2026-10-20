using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The cathedral steps. In Act 2 Micah ends up here, thinking about Eleanor, and goes in. In Act 3 Bruno dumps him
/// here after the Club, and Micah decides whether to keep going.
/// </summary>
public partial class ChurchExterior : Room
{
    public override Track? Music => Track.StreetTraffic;

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
            await Think("Two men took her, the night I walked out. I didn't ask where she'd go. I didn't want to hear the answer.");
            await Think("So why can't I think of anything but her? Her voice. Her hair on the pillow. \"I can't go back there.\"");
            await Think("A man in my state ends up in one of two places. The bars know me too well. So, the other one.");
            await GoIn();
        });
    }

    /// <summary>Act 2: up the steps and in. The street exit takes him there too until he has been inside.</summary>
    private async Task GoIn()
    {
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        Player.Face(Facing.Up);
        await Game.ChangeRoom("church_interior", "start");
    }

    /// <summary>Act 3 before the choice: the only way Micah is on these steps in Act 3 is beaten, Bruno's delivery.</summary>
    private bool LeftBeaten => State.StoryAct == 3 && !State.HasFlag("keep_going") && !State.HasFlag(Endings.GaveUpSteps);

    /// <summary>Act 3: on the cathedral steps, beaten. Keep going for Eleanor, or give up and go to Rose.</summary>
    private async Task Beaten()
    {
        Player.SetPose("micah_supine");
        await Wait(1.5);
        await Think("Cathedral steps. Somebody has a sense of humour. Probably Bruno. Probably not.");
        // after his first line, his face from above, flat on the stones, while he argues with himself; gone before he gets up
        Game.Hud.ShowCloseUp(CloseUps.Beaten);
        await Think("My ribs are talking to each other. My mouth tastes like a penny.");
        await Think("What am I doing? She told me to go home. She looked at me like a stranger who'd wandered onto the stage.");
        await Think("Caleb's in there, a hundred feet away, praying for me. Rose is across town, not praying for anybody.");
        await Think("I keep calling it saving her. But it's her I want. Her voice. Her skin. Another night like that one.");
        await Think("Rose and Tommy ought to be in my heart. Eleanor's there instead. And God help me, I don't want to let her go.");
        Game.Hud.HideCloseUp();
        if (!await Player.PlayPose("micah_recover")) return;
        await Choose();
    }

    /// <summary>On his feet: keep going, or give up. The doors and the street run it too, in case the cutscene stopped short.</summary>
    private async Task Choose()
    {
        Game.Hud.HideCloseUp(0);
        Player.SetPose(null);
        Player.Face(Facing.Down);
        await Wait(0.6);
        await Talk("beaten_choice");
        if (State.HasFlag("keep_going"))
        {
            await Think("Not yet. Not while she's in there with them.");
            State.SetFlag("micah_at_desk");
            await Game.ChangeRoom("office", "act3");
        }
        else
        {
            await Think("Enough. Enough for one life.");
            State.SetFlag(Endings.GaveUpSteps);
            await Act3.End();
        }
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("doors" or "exit", Verb.Walk or Verb.Hand) when LeftBeaten:
                await Choose();
                return true;
            case ("doors" or "exit", Verb.Walk or Verb.Hand) when State.HasFlag("act2_church"):
                await GoIn();
                return true;
        }
        return false;
    }
}
