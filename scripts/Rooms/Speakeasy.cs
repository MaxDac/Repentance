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
        if (FindActor("sal") is { } sal && State.HasFlag("sal_passed"))
            sal.Position = SalAside;
    }

    private bool _intercepting;

    /// <summary>Micah can try to walk past Sal; the moment he crosses the curtain line, Sal steps in and the talk starts.</summary>
    public override void _Process(double delta)
    {
        if (_intercepting || State.HasFlag("sal_passed") || Game.Busy || Game.IsPaused) return;
        if (!Player.Visible || Player.Position.X <= BarrierX) return;
        _intercepting = true;
        _ = Game.Run(async () =>
        {
            Player.Stop();
            try { await Intercept(); }
            finally { _intercepting = false; }
        });
    }

    private async Task Intercept()
    {
        if (FindActor("sal") is { } sal)
        {
            await sal.MoveTo(new Vector2(Player.Position.X + 22, Player.Position.Y), 80);
            Player.FaceTowards(sal.Position);
        }
        await Say("sal", Game.Pick("Whoa, whoa. Where do you think you're goin', pal?", "Not so fast. Nobody walks past me."));
        await TalkToSal();
    }

    /// <summary>The door talk, whether Micah opens it or Sal stops him. If nobody gets anywhere, Sal walks him back.</summary>
    private async Task TalkToSal()
    {
        bool wasPassed = State.HasFlag("sal_passed");
        await Talk("sal");
        var sal = FindActor("sal");
        if (State.HasFlag("sal_passed"))
        {
            if (sal != null) await sal.MoveTo(SalAside, 45);
            if (!wasPassed) await Think("Ten dollars into a fist the size of a ham. Half of what I had left, and I haven't even had a drink.");
        }
        else if (State.HasFlag("thrown_out"))
            await ThrownOut();
        else
        {
            if (Player.Position.X > BarrierX - 8)
                await Game.WalkTo(new Vector2(BarrierX - 20, Player.Position.Y));
            if (sal != null)
            {
                await sal.MoveTo(SalBlocking, 60);
                Player.FaceTowards(sal.Position);
            }
        }
    }

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_lantern")) return;
        State.SetFlag("seen_lantern");
        await Game.Run(async () =>
        {
            await Think("Past the iced roses, a steel door, then smoke and a muted trumpet. The Blue Lantern.");
            await Say("sal", "Members only, pal.");
            await Think("Gin, jazz, and a bouncer built like a bank vault.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        bool beyondSal = target.Bounds.Position.X > BarrierX && target.Id != "sal";
        if (beyondSal && !State.HasFlag("sal_passed") && verb != Verb.Look)
        {
            await Intercept();
            return true;
        }

        switch (target.Id, verb)
        {
            case ("sal", Verb.Talk):
                if (State.HasFlag("sal_passed")) await Talk("sal");
                else await TalkToSal();
                return true;
            case ("sal", Verb.UseItem) when item == "matchbook":
                await Say("sal", "I don't smoke. And I don't read. Password.");
                return true;
            case ("sal", Verb.UseItem) when item == "dollar":
                if (State.HasFlag("sal_passed")) await Talk("sal");
                else await TalkToSal();
                return true;
            case ("sal", Verb.Kick or Verb.Hand):
                await Say("I'd have better luck pushing the Wrigley Building.");
                return true;

            case ("bartender", Verb.Talk):
                await Talk("bartender");
                await BartenderDislikes();
                return true;
            case ("bartender", Verb.UseItem) when Shows(item, "photo", "eleanor"):
                await Talk(State.HasFlag("photo_shown") ? "bartender" : "bartender.photo");
                await BartenderDislikes();
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

    /// <summary>Wise guys and tightwads get walked out the back by Sal.</summary>
    private async Task ThrownOut()
    {
        if (FindActor("sal") is { } sal)
        {
            await sal.MoveTo(Game.Player.Position + new Vector2(18, 0), 60);
        }
        await Say("Hey, easy with the suit, it's rented--");
        await Game.ChangeRoom("alley", "start");
    }

    /// <summary>
    /// In 1927 the bartender won't budge on Eleanor. When the talk is over he calls Micah back, and nods at Sal.
    /// (In Act 2, the old Club lead is already known and he just pours.)
    /// </summary>
    private async Task BartenderDislikes()
    {
        if (State.HasFlag("photo_shown")) return;
        await Talk("bartender_dislike");
        await Think("He nods at the bouncer by the door. That's never a good nod.");
        if (FindActor("sal") is { } sal)
            await sal.MoveTo(Game.Player.Position + new Vector2(-18, 0), 70);
        await Say("sal", "Out back, pal. Tony wants a word. Several, actually.");
        await Game.ChangeRoom("alley", "start");
    }
}
