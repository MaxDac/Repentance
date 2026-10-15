using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Joliet, the visiting room. Micah in an inmate's jumpsuit across the table from his one visitor: Eleanor if she came
/// away with him that night (ending 4), his brother Caleb if she didn't (ending 5), Rose if he turned himself in (ending 6).
/// </summary>
public partial class Prison : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry != "ending") return;
        await Game.Run(async () =>
        {
            Game.Hud.ShowCaption("Joliet Correctional Center. Six months later.");
            await Wait(2.6);
            Game.Hud.ShowCaption(null);
            await Talk(State.HasFlag("ending_4") ? "prison_eleanor"
                : State.HasFlag("ending_6") ? "prison_rose" : "prison_caleb");
            await Act3.Finish();
        });
    }
}
