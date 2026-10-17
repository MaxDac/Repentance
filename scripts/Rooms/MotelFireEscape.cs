using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 1: the motel fire escape, one floor up. Eleanor is waiting for Micah in the rain. Their talk ends Act 1:
/// Micah walks slowly to her while she answers him, kisses her, and only after his narration does the fade take
/// them. The night in her room follows the First Interlude (<see cref="MotelNight"/>).
/// </summary>
public partial class MotelFireEscape : Room
{
    /// <summary>Micah and Eleanor share the office's slow jazz; it plays again in her room after the First Interlude.</summary>
    public override Track? Music => Track.OfficeJazz;

    /// <summary>How far from Eleanor Micah stands while they talk.</summary>
    private static readonly Vector2 TalkingDistance = new(-44, 4);
    /// <summary>
    /// Where he stops in front of her for the kiss: KISS_GAP pixels short of her, KISS_RISE nearer the railing, as the
    /// micah_kiss strip (tools/art/sprites.py) draws them both.
    /// </summary>
    public static readonly Vector2 KissSpot = new(-22, 2);
    /// <summary>Slow, so she says her last line while he walks to her.</summary>
    private const float SlowSteps = 16f;
    private const double FadeOut = 1.2;

    private Task? _approach;

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

    public override async Task OnCue(string cue)
    {
        if (FindActor("eleanor") is not { } eleanor) return;
        switch (cue)
        {
            // "closer": Micah starts walking slowly to her; she answers him while he walks
            case "closer":
                Player.Speed = SlowSteps;
                _approach = Game.WalkTo(eleanor.Position + KissSpot);
                break;
            // "kiss": he reaches her and kisses her, and holds it through his narration until the fade
            case "kiss":
                if (_approach != null) await _approach;
                _approach = null;
                Player.Teleport(eleanor.Position + KissSpot, Facing.Right);
                eleanor.Visible = false;
                await Player.PlayPose("micah_kiss");
                break;
        }
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
