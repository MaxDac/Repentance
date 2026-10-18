using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The motel fire escape, one floor up, where Eleanor waits for Micah in the rain. Act 1 ends on her first question:
/// Micah climbs up, walks to her, she asks it, and the fade takes them to the attic. After the First Interlude
/// (entry "interlude1") the landing fades in with Micah already in front of her; she asks it again and their talk goes
/// on: Micah walks slowly to her while she answers him, kisses her, and only after his narration does the slow fade
/// take them, "Later that night", into her room (<see cref="MotelNight"/>).
/// </summary>
public partial class MotelFireEscape : Room
{
    /// <summary>Micah and Eleanor share the office's slow jazz; it plays again in her room afterwards.</summary>
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
    /// <summary>After the kiss: fade to black, "Later that night" alone on black, fade into her room.</summary>
    public const double NightFade = 3.0, NightCaption = 3.0;

    private Task? _approach;

    public override async Task OnEnter(string entry)
    {
        if (entry == "interlude1" || State.StoryAct >= 2)
        {
            await TheNight();
            return;
        }
        await Game.Run(async () =>
        {
            if (!State.HasFlag("eleanor_found"))
            {
                await Wait(0.8);
                await Think("A woman on the iron landing, under the dripping window. Alone in the rain, like she'd been expecting company. I know the face. I've carried it in my pocket for two days.");
                if (FindActor("eleanor") is { } eleanor)
                    await Game.WalkTo(eleanor.Position + TalkingDistance);
                Player.Face(Facing.Right);
                await Talk("eleanor_fire_escape_opening");
                State.SetFlag("eleanor_found");
            }
            await Game.Hud.Fade(1, FadeOut);
            Player.Stop();
            await Wait(1.0);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night", fadeInSeconds: 1.2);
        });
    }

    /// <summary>After the First Interlude: the rest of their talk, the kiss, and "Later that night".</summary>
    private async Task TheNight()
    {
        await Game.Run(async () =>
        {
            float speed = Player.Speed;
            try
            {
                if (FindActor("eleanor") is { } eleanor)
                    Player.Teleport(eleanor.Position + TalkingDistance, Facing.Right);
                await Wait(0.6);
                await Talk("eleanor_fire_escape");
                await Game.Hud.Fade(1, NightFade);
                Player.Stop();
            }
            finally { Player.Speed = speed; }
            Game.Hud.ShowCaption("Later that night");
            await Wait(NightCaption);
            Game.Hud.ShowCaption(null);
            await Game.ChangeRoom("motel_night", "start", fadeInSeconds: NightFade);
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
