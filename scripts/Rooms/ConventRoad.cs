using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The convent entrance on arrival. When Micah leaves, the road is empty: he lights up in the middle of it, runs out
/// of leads, and spots the motel sign down the hill.
/// </summary>
public partial class ConventRoad : Room
{
    public override Track? Music => Track.StreetTraffic;

    public override async Task OnEnter(string entry)
    {
        if (!State.HasFlag("convent_departed"))
        {
            if (State.HasFlag("seen_convent_exterior")) return;
            await Game.Run(async () =>
            {
                await Think("I slept the day off and came up the hill at dusk, in the rain. A day later, my ribs still remember every one of Sal's knuckles.");
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
        await TalkSmoking(Talk("convent_dead_end"));
        State.SetFlag("convent_dead_end_done");
        Player.SetPose(null);
        await Say("*flick*");
        await Think("I flicked the butt into the gutter and went down the hill.");
        await Game.Hud.Fade(1, 1.5);
    }

    /// <summary>Seconds between drags on the cigarette while he talks.</summary>
    public const double DragEvery = 10;

    /// <summary>Drags Micah has taken on his cigarette since the room loaded.</summary>
    public int Drags { get; private set; }

    /// <summary>The conversation, with Micah taking a drag every <see cref="DragEvery"/> seconds until it ends.</summary>
    private async Task TalkSmoking(Task talk)
    {
        while (await Task.WhenAny(talk, Wait(DragEvery)) != talk)
        {
            if (Player.PoseName != "micah_smoke_drag" && Player.PoseName != "micah_smoke") break;
            Drags++;
            if (!await Player.PlayPose("micah_smoke_drag")) break;
        }
        await talk;
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