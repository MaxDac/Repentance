using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The convent entrance on arrival; Eleanor waits outside when Micah leaves.</summary>
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
            await Wait(0.8);
            await Think("A woman in black by the gate, alone on an empty road. I know the face. I've carried it in my pocket all night.");
            if (FindActor("eleanor") is { } eleanor)
                await Game.WalkTo(eleanor.Position + new Godot.Vector2(-44, 4));
            Player.Face(Facing.Right);
            await Talk("eleanor_road");
            State.SetFlag("eleanor_found");
            await Wait(0.8);
            await Game.Hud.Fade(1, 1.5);
            await Game.ChangeRoom("motel_night", "start", fadeInSeconds: 1.5);
        });
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
