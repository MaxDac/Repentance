using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Act 1: the motel fire escape, one floor up. Eleanor is waiting for Micah in the rain.</summary>
public partial class MotelFireEscape : Room
{
    /// <summary>Micah and Eleanor share the office's slow jazz; it carries on into her room.</summary>
    public override Track? Music => Track.OfficeJazz;

    public override async Task OnEnter(string entry)
    {
        await Game.Run(async () =>
        {
            if (!State.HasFlag("eleanor_found"))
            {
                await Wait(0.8);
                await Think("A woman on the iron landing, under the dripping window. Alone in the rain, like she'd been expecting company. I know the face. I've carried it in my pocket for two days.");
                if (FindActor("eleanor") is { } eleanor)
                    await Game.WalkTo(eleanor.Position + new Vector2(-44, 4));
                Player.Face(Facing.Right);
                await Talk("eleanor_fire_escape");
                State.SetFlag("eleanor_found");
                await Wait(0.8);
            }
            await Game.Hud.Fade(1, 1.5);
            await Game.ChangeRoom("motel_night", "start", fadeInSeconds: 1.5);
        });
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