using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 3, present day: Daniel reads in bed by the nightstand lamp while his wife sleeps. He keeps reading, and the
/// story goes back to the Club, right where Act 2 left it.
/// </summary>
public partial class Bedroom : Room
{
    public override Task OnEnter(string entry) => Game.Run(async () =>
    {
        await Wait(1.0);
        await Say("*rustle*");
        await Talk("bedroom");
        await Wait(0.6);
        await Say("Where was I. The stage...");
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("Chicago, 1927.");
        await Wait(2.8);
        Game.Hud.ShowCaption(null);
        Attic.RestoreMicahItems(3);
        State.SetFlag("masked");
        await Game.ChangeRoom("club_stage", "act3");
    });
}
