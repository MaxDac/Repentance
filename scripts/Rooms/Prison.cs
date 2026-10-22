using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Joliet, the visiting room. Micah in an inmate's jumpsuit across the table from his one visitor: Eleanor if she came
/// away with him that night (ending 4), his brother Caleb if she didn't (ending 5), Rose if he turned himself in (ending 6).
/// In ending 12 it's Caleb again, after Micah killed Tony and gave himself up. In ending 11 Eleanor, worn out, comes once to wish him his peace; in ending 9 it's Eleanor in the jumpsuit, confessing to Caleb.
/// </summary>
public partial class Prison : Room
{
    /// <summary>The inmate's seat, where Eleanor's speech anchor moves in ending 9.</summary>
    private static readonly Vector2 InmateSpeech = new(196, 150);

    /// <summary>
    /// No rain outside the window when Micah turned himself in (endings 6 and 12) or Eleanor confesses (ending 9).
    /// </summary>
    protected override bool RainStopped =>
        State.HasFlag("ending_6") || State.HasFlag("ending_9") || State.HasFlag("ending_12");

    /// <summary>No music in the visiting room, only near silence: a guard's few steps, a chair moved.</summary>
    public override Track? Music => Track.PrisonParlour;

    public override async Task OnEnter(string entry)
    {
        if (entry == "eleanor")
        {
            await Game.Run(async () =>
            {
                if (GetNodeOrNull<Node2D>("EleanorVoice") is { } voice) voice.Position = InmateSpeech;
                Game.Hud.ShowCaption("Joliet Correctional Center, the women's wing. Six months later.");
                await Wait(2.6);
                Game.Hud.ShowCaption(null);
                await Talk("prison_eleanor_caleb");
                await Act3.Finish();
            });
            return;
        }
        if (entry != "ending") return;
        await Game.Run(async () =>
        {
            Game.Hud.ShowCaption("Joliet Correctional Center. Six months later.");
            await Wait(2.6);
            Game.Hud.ShowCaption(null);
            await Talk(State.HasFlag("ending_4") ? "prison_eleanor"
                : State.HasFlag("ending_11") ? "prison_eleanor_peace"
                : State.HasFlag("ending_6") ? "prison_rose"
                : State.HasFlag("ending_12") ? "prison_caleb_tony" : "prison_caleb");
            await Act3.Finish();
        });
    }
}
