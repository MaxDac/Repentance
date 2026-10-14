using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, that same night. Micah gets dressed. Eleanor stays against the pillows under the white sheet.
/// They agree never to see each other again. End of the first act of the journal.
/// </summary>
public partial class MotelNight : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("motel_night_done")) return;
        await Game.Run(async () =>
        {
            await Wait(1.0);
            await Think("A motel at the edge of town. A buzzing sign, a cracked basin, her stockings over the chair.");
            await Think("I'm buttoning my shirt in the dark like a thief. Rose's face keeps turning up behind my eyes.");
            await Talk("motel_night");
            State.SetFlag("motel_night_done");
            await Think("I close the door on her softly. Rose, the boy, and now Eleanor. I'm getting good at doors.");
            await Wait(0.6);
            await Game.Hud.Fade(1, 1.5);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night");
        });
    }
}
