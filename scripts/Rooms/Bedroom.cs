using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 3, present day: Daniel reads in bed by the nightstand lamp while his wife sleeps. He keeps reading: the pages turn
/// to Eleanor first (the Second Interlude), then back to the Club, right where Act 2 left it.
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
        await Wait(0.4);
        await Say("These pages read differently. Not sure that's Micah's hand.");
        // Eleanor's night first; Story.Interlude.EndSecond takes the story back to the stage
        await Story.Interlude.BeginSecond();
    });
}
