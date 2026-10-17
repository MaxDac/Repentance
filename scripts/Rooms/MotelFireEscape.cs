using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 1: the motel fire escape, one floor up. Eleanor is waiting for Micah in the rain. Their talk ends Act 1:
/// Micah starts towards her and the fade takes him before he gets there. The night in her room follows the First
/// Interlude (<see cref="MotelNight"/>).
/// </summary>
public partial class MotelFireEscape : Room
{
    /// <summary>Micah and Eleanor share the office's slow jazz; it plays again in her room after the First Interlude.</summary>
    public override Track? Music => Track.OfficeJazz;

    /// <summary>How far from Eleanor Micah stands while they talk.</summary>
    private static readonly Vector2 TalkingDistance = new(-44, 4);
    /// <summary>Where his first two steps towards her stop, while she answers.</summary>
    private static readonly Vector2 FirstSteps = new(-28, 4);
    private const float SlowSteps = 26f;
    /// <summary>Slow enough that the fade to black beats him to her.</summary>
    private const float LastSteps = 16f;
    private const double FadeOut = 1.2;

    public override async Task OnEnter(string entry)
    {
        await Game.Run(async () =>
        {
            float speed = Player.Speed;
            try
            {
                if (!State.HasFlag("eleanor_found"))
                {
                    await Wait(0.8);
                    await Think("A woman on the iron landing, under the dripping window. Alone in the rain, like she'd been expecting company. I know the face. I've carried it in my pocket for two days.");
                    if (FindActor("eleanor") is { } eleanor)
                        await Game.WalkTo(eleanor.Position + TalkingDistance);
                    Player.Face(Facing.Right);
                    await Talk("eleanor_fire_escape");
                    State.SetFlag("eleanor_found");
                    if (FindActor("eleanor") is { } her)
                    {
                        Player.Speed = LastSteps;
                        _ = Game.WalkTo(her.Position + new Vector2(-2, 4));
                    }
                }
                await Game.Hud.Fade(1, FadeOut);
                Player.Stop();
            }
            finally { Player.Speed = speed; }
            await Wait(1.0);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night", fadeInSeconds: 1.2);
        });
    }

    /// <summary>"closer": Micah takes two slow steps towards Eleanor before she answers him.</summary>
    public override async Task OnCue(string cue)
    {
        if (cue != "closer" || FindActor("eleanor") is not { } eleanor) return;
        float speed = Player.Speed;
        Player.Speed = SlowSteps;
        try { await Game.WalkTo(eleanor.Position + FirstSteps); }
        finally { Player.Speed = speed; }
        Player.Face(Facing.Right);
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("ladder", Verb.Walk or Verb.Hand):
                await Say("Not now. Not after that climb.");
                return true;
            case ("window" or "door", Verb.Hand or Verb.Walk):
                await Say("Her room. Not mine to walk into.");
                return true;
        }
        return false;
    }
}
