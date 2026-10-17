using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Past the city limits, where the bookkeeper's drive ended in Act 2. In Act 3 it's where Micah's car stops on the way out
/// of Chicago: with Eleanor beside him (ending 2) or alone (ending 3). In ending 10 she gets out with him, then walks off down
/// the road on her own to look for her peace. In ending 8 it's Eleanor, on her own.
/// </summary>
public partial class Outskirts : Room
{
    /// <summary>Eleanor walks out of the city free in ending 8: the rain has stopped.</summary>
    protected override bool RainStopped => State.HasFlag("ending_8");

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

    /// <summary>Ending 8: Eleanor on her own at the edge of the city, on foot, leaving it. No car, no Micah.</summary>
    private async Task EleanorAlone()
    {
        await Wait(1.0);
        await Game.WalkTo(new Vector2(232, 252));
        Player.Face(Facing.Right);
        await Talk("ending_eleanor_alone");
        State.SetFlag("eleanor_epilogue", false);
        await Act3.Finish();
    }

    /// <summary>Where Eleanor walks off to in ending 10: down the road, past the car and out of the picture.</summary>
    private static readonly Vector2 RoadAway = new(520, 246);

    private async Task Ending()
    {
        if (State.HasFlag("ending_10"))
        {
            await Weary();
            return;
        }
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

    /// <summary>
    /// Ending 10: the two of them get out of the car, as in ending 2, but she's worn out, and says goodbye. She walks off
    /// down the road alone; Micah stays by the car.
    /// </summary>
    private async Task Weary()
    {
        await Wait(1.0);
        await Say("*Two car doors slam in the dark.*");
        var eleanor = FindActor("eleanor");
        if (eleanor != null) _ = eleanor.MoveTo(new Vector2(272, 250), 40);
        await Game.WalkTo(new Vector2(232, 252));
        Player.Face(Facing.Right);
        await Think("Prairie dark and a cold wind off the stubble. She talked all the way out of the city. Now she won't look at me.");
        await Talk("ending_weary_road");
        if (eleanor != null)
        {
            await eleanor.MoveTo(RoadAway, 34);
            eleanor.Visible = false;
        }
        await Think("She doesn't look back. I don't follow her. For once in my life, I let somebody go.");
        await Act3.Finish();
    }
}