using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, that same night. Micah gets dressed. Eleanor stays in the bed under the sheet, on her back,
/// looking at the ceiling. They agree never to see each other again. End of the first act of the journal.
/// </summary>
public partial class MotelNight : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("motel_night_done")) return;
        await Game.Run(async () =>
        {
            await Wait(1.0);
            await Talk("motel_night");
            State.SetFlag("motel_night_done");
            await Wait(0.6);
            await Game.Hud.Fade(1, 1.5);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night");
        });
    }
}
