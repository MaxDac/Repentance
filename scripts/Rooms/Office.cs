using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Micah's office, 9 PM. Teddy Harrington is waiting when the game starts.</summary>
public partial class Office : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("teddy_gone")) return;
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Say("Another night, another empty bottle. And a client. A well-dressed one.");
            await Talk("teddy");
            await TeddyLeaves();
        });
    }

    private async Task TeddyLeaves()
    {
        if (!State.HasFlag("teddy_briefed") || FindActor("teddy") is not { } teddy) return;
        await Say("teddy", "Good evening, Jones. Do try not to embarrass me.");
        await teddy.MoveTo(new Godot.Vector2(58, 170), 55);
        State.SetFlag("teddy_gone");
        await Say("Harrington Steel. Funny how the rich always lose the things they never paid attention to.");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("teddy", Verb.Talk):
                await Talk("teddy");
                await TeddyLeaves();
                return true;
            case ("teddy", Verb.UseItem):
                await Say("teddy", "Keep it, Jones. You clearly need it more than I do.");
                return true;

            case ("door", Verb.Walk or Verb.Hand) when !State.HasFlag("teddy_gone"):
                await Say("Walking out on a paying client? Not this month.");
                return true;

            case ("drawer", Verb.Hand):
                if (State.HasFlag("drawer_open"))
                {
                    State.SetFlag("drawer_open", false);
                    return true;
                }
                State.SetFlag("drawer_open");
                await Say(State.HasFlag("took_dollar")
                    ? "A revolver. Nothing else. The story of my life."
                    : "My revolver, and my entire savings: one dollar.");
                return true;
            case ("drawer", Verb.Kick):
                await Say("Kicking my own desk. That's a new low, even for me.");
                return true;
            case ("drawer2", Verb.Hand):
                await Say("Unpaid bills. I'm not opening that again until 1931.");
                return true;

            case ("dollar", Verb.Hand):
                State.GiveItem("dollar");
                State.SetFlag("took_dollar");
                await Say("Don't spend it all at once, Micah.");
                return true;
            case ("revolver", Verb.Hand):
                await Say("It stays in the drawer. Last time I carried it, I shot a mailbox.");
                return true;

            case ("bottle", Verb.Hand):
                await Say("Empty. Like most of my promises.");
                return true;
            case ("phone", Verb.Hand or Verb.Talk):
                await Say("Nobody to call. Nobody who'd answer, anyway.");
                return true;
            case ("window", Verb.Hand):
                await Say("Then I'd hear the city. I hear enough of it already.");
                return true;
            case ("filing", Verb.Hand):
                await Say("C for Cases. Empty. D for Debts. Overflowing.");
                return true;
            case ("coat", Verb.Hand):
                await Say("I'm already wearing my coat. That's my other coat. It's for when this one's at the pawnshop.");
                return true;
            case ("clock", Verb.Hand or Verb.Kick):
                await Say("Turning back time? If only it were that easy.");
                return true;
            case ("radiator", Verb.Hand or Verb.Kick):
                await Say("It knocks all night. Like a creditor. Or a conscience.");
                return true;
        }
        return false;
    }
}
