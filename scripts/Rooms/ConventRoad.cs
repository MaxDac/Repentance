using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The convent entrance on arrival. When Micah leaves, the road is empty: he lights up in the middle of it, runs out
/// of leads, and spots the motel sign down the hill.
/// </summary>
public partial class ConventRoad : Room
{
    public override async Task OnEnter(string entry)
    {
        if (!State.HasFlag("convent_departed"))
        {
            if (State.HasFlag("seen_convent_exterior")) return;
            await Game.Run(async () =>
            {
                await Think("The end of a dark road on the North Side. My ribs remember every one of Sal's knuckles.");
                await Say("Gothic arches, iron spikes and a saint in every window. They built the place to point toward heaven. From down here, it looks like a warning.");
                State.SetFlag("seen_convent_exterior");
            });
            return;
        }
        if (State.HasFlag("eleanor_found")) return;
        await Game.Run(async () =>
        {
            if (!State.HasFlag("convent_dead_end_done")) await DeadEnd();
            await Game.ChangeRoom("motel_alley", "start");
        });
    }

    private async Task DeadEnd()
    {
        await Wait(0.8);
        await Game.WalkTo(new Vector2(240, 214));
        Player.Face(Facing.Down);
        await Player.PlayPose("micah_smoke");
        await Talk("convent_dead_end");
        State.SetFlag("convent_dead_end_done");
        Player.SetPose(null);
        await Say("*flick*");
        await Think("I flicked the butt into the gutter and went down the hill.");
        await Game.Hud.Fade(1, 1.5);
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (target.Id != "door") return false;
        if (verb == Verb.Look)
        {
            await Say(State.HasFlag("convent_departed")
                ? "Oak and iron. Sister Agatha's already bolted it behind me."
                : "Oak and iron beneath a pointed arch. A heavy door for a house of mercy.");
            return true;
        }
        if (verb is Verb.Walk or Verb.Hand)
        {
            if (State.HasFlag("convent_departed")) await Say("Bolted from the inside. The sister's said her last word.");
            else await Game.ChangeRoom("convent_corridor", "start");
            return true;
        }
        return false;
    }
}