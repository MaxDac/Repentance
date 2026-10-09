using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The Blue Lantern: a speakeasy behind a steel door on State Street.</summary>
public partial class Speakeasy : Room
{
    private const float BarrierX = 132;
    private static readonly Vector2 SalBlocking = new(156, 192);
    private static readonly Vector2 SalAside = new(196, 180);

    protected override void OnRefresh()
    {
        if (FindActor("sal") is { } sal && State.HasFlag("sal_passed") && !State.HasFlag("ending"))
            sal.Position = SalAside;
    }

    public override Vector2 ClampWalkTarget(Vector2 target)
    {
        if (!State.HasFlag("sal_passed") && target.X > BarrierX) target.X = BarrierX;
        return target;
    }

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_lantern")) return;
        State.SetFlag("seen_lantern");
        await Game.Run(async () =>
        {
            await Say("sal", "Members only, pal.");
            await Say("The Blue Lantern. Gin, jazz, and a bouncer built like a bank vault.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        bool beyondSal = target.Bounds.Position.X > BarrierX && target.Id != "sal";
        if (beyondSal && !State.HasFlag("sal_passed") && verb != Verb.Look)
        {
            await Say(Game.Pick("The big guy at the curtain isn't letting me through.", "Not without getting past the bank vault first."));
            return true;
        }

        switch (target.Id, verb)
        {
            case ("sal", Verb.Talk):
                bool wasPassed = State.HasFlag("sal_passed");
                await Talk("sal");
                if (!wasPassed && State.HasFlag("sal_passed") && FindActor("sal") is { } sal)
                    await sal.MoveTo(SalAside, 45);
                return true;
            case ("sal", Verb.UseItem) when item == "matchbook":
                await Say("sal", "I don't smoke. And I don't read. Password.");
                return true;
            case ("sal", Verb.UseItem) when item == "dollar":
                await Say("sal", "A buck? I get a buck for breathing.");
                return true;
            case ("sal", Verb.Kick or Verb.Hand):
                await Say("I'd have better luck pushing the Wrigley Building.");
                return true;

            case ("bartender", Verb.Talk):
                await Talk("bartender");
                if (State.HasFlag("photo_shown")) await Ending();
                return true;
            case ("bartender", Verb.UseItem) when item == "photo":
                if (State.HasFlag("photo_shown")) { await Talk("bartender"); return true; }
                await Talk("bartender.photo");
                await Ending();
                return true;
            case ("bartender", Verb.UseItem) when item == "dollar":
                await Say("bartender", "A buck buys you the bathtub gin. You want it? No? Smart man.");
                return true;

            case ("private_door", Verb.Hand or Verb.Kick):
                await Say("Locked. And something tells me knocking would be a career-ending move.");
                return true;
            case ("piano", Verb.Hand or Verb.Kick):
                await Say("I know two songs. Neither is appropriate for mixed company.");
                return true;
            case ("mic", Verb.Hand or Verb.Talk):
                await Say("Testing... one, two... It's not plugged in. Thank God.");
                return true;
            case ("shelves", Verb.Hand):
                await Say("Tony would break my arm. Then charge me for the bottle.");
                return true;
            case ("crates", Verb.Hand or Verb.Kick):
                await Say("Nailed shut. 'Maple syrup', my foot. That's Canadian whisky.");
                return true;
        }
        return false;
    }

    private async Task Ending()
    {
        if (State.HasFlag("ending") || FindActor("sal") is not { } sal) return;
        State.SetFlag("ending");
        await Wait(0.6);
        Player.FaceTowards(sal.Position);
        await sal.MoveTo(Player.Position + new Vector2(-34, 2), 50);
        await DialogueManager.Instance.Talk("ending");
        await Game.Hud.Fade(1, 1.2);
        Game.Hud.ShowCaption("To be continued...");
        // The demo ends here; keep the game locked on the caption.
        await new TaskCompletionSource().Task;
    }
}
