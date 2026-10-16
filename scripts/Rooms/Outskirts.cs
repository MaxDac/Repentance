using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Past the city limits, where the bookkeeper's drive ended in Act 2. In Act 3 it's where Micah's car stops on the way out
/// of Chicago: with Eleanor beside him (ending 2) or alone (ending 3). In endings 8 and 10 it's Eleanor, on her own.
/// </summary>
public partial class Outskirts : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry == "ending")
        {
            await Game.Run(Ending);
            return;
        }
        if (entry == "eleanor_alone")
        {
            await Game.Run(EleanorAlone);
            return;
        }
        if (State.HasFlag("seen_outskirts")) return;
        State.SetFlag("seen_outskirts");
        await Game.Run(() => Think("The last fence post, the last streetlight, the last place a man would go to bury something."));
    }

    /// <summary>Endings 8 and 10: Eleanor on her own at the edge of the city, on foot, leaving it. No car, no Micah.</summary>
    private async Task EleanorAlone()
    {
        await Wait(1.0);
        await Game.WalkTo(new Vector2(232, 252));
        Player.Face(Facing.Right);
        await Talk("ending_eleanor_alone");
        State.SetFlag("eleanor_epilogue", false);
        await Act3.Finish();
    }

    private async Task Ending()
    {
        bool together = State.HasFlag("ending_2");
        bool nextMorning = !together && State.HasFlag(Endings.MansionExploded);
        if (nextMorning)
        {
            Game.Hud.ShowCaption("The next morning");
            await Wait(2.6);
            Game.Hud.ShowCaption(null);
        }
        await Wait(1.0);
        await Say(together ? "*Two car doors slam in the dark.*"
            : nextMorning ? "*A car door slams.*" : "*A car door slams in the dark.*");
        if (together && FindActor("eleanor") is { } eleanor)
            _ = eleanor.MoveTo(new Vector2(272, 250), 40);
        await Game.WalkTo(new Vector2(232, 252));
        Player.Face(Facing.Right);
        await Think(together ? "Prairie dark and a cold wind off the stubble. Chicago is a dirty glow behind us, and she's still here."
            : nextMorning ? "Grey light over the stubble fields. A morning paper on the passenger seat. I haven't had the nerve to open it."
            : "Prairie dark and a cold wind off the stubble. The passenger seat is empty. Maybe it always was.");
        await Talk(together ? "ending_together" : "ending_alone");
        await Act3.Finish();
    }
}