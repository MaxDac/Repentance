using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Hubbard Street outside the Club: only the Act 2 cutscene where Bruno throws Micah out.</summary>
public partial class Street : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry == "thrown_out") await Game.Run(ThrownOut);
    }

    /// <summary>Act 2: Bruno dumps Micah on the pavement outside the Club. He thinks about Rose and Tommy, then chooses.</summary>
    private async Task ThrownOut()
    {
        Player.SetPose("micah_supine");
        await Wait(1.2);
        // his face from above, flat on the pavement, while he argues with himself; gone before he gets up
        Game.Hud.ShowCloseUp(CloseUps.Beaten);
        await Think("The pavement on Hubbard Street is cold under my back, and it doesn't ask questions. I like that in a pavement.");
        await Think("What am I doing, lying in the gutter for a woman I met four days ago?");
        await Think("I have a wife. On paper, anyway. And a boy who's eleven now, if I've counted right. Tommy.");
        await Think("I walked out on them because the bottle was easier to talk to. Now I walk into the night for a stranger.");
        await Think("At the library I thanked God Rose wasn't at her desk. She's been in my head every minute since.");
        await Think("Maybe that's the joke. Maybe it's easier to save somebody you don't owe anything to.");
        Game.Hud.HideCloseUp();
        if (!await Player.PlayPose("micah_recover")) return;
        Player.SetPose(null);
        Player.Face(Facing.Down);
        await Wait(0.5);
        await Talk("street_choice");
        if (State.HasFlag("go_rose"))
            await Game.ChangeRoom("rose_house", "start");
        else
            await Game.ChangeRoom("chicago_map", "start");
    }
}
