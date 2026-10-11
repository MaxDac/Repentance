using System.Linq;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Micah's office, 9 PM. Teddy Harrington is waiting when the game starts. In Act 3 Micah ends up back here, at his
/// desk, working out who could know where Eleanor is.
/// </summary>
public partial class Office : Room
{
    // Micah starts Act 3 seated behind the desk (a sprite), so the walking player is hidden until he stands up.
    public override bool PlayerVisibleOnLoad => ShowPlayer && !State.HasFlag("micah_at_desk");

    public override async Task OnEnter(string entry)
    {
        if (entry == "act3" && State.HasFlag("micah_at_desk"))
        {
            await Game.Run(AtTheDesk);
            return;
        }
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

    /// <summary>Act 3: thinking it over at the desk, then out the door to the Blue Lantern.</summary>
    private async Task AtTheDesk()
    {
        await Wait(1.0);
        await Say("Back behind my own desk. The bottle's still empty. Some things you can count on.");
        await Say("Where would they take her? Not the Club, not tonight. Not the hotel. Not Teddy's, he'd have to explain her.");
        await Say("The convent's done with me. Caleb would sooner pray than talk. The cops are on somebody's payroll.");
        await Say("Who knows where the Club keeps its girls? Who delivers to people like that, and keeps his mouth shut?");
        await Say("The Blue Lantern. Tony and his gorilla. The mob knows every back door in this town. They deliver to most of them.");
        State.SetFlag("micah_at_desk", false);
        Player.Teleport(new Godot.Vector2(160, 172), Facing.Left);
        Player.Visible = true;
        await Wait(0.4);
        await Game.WalkTo(new Godot.Vector2(58, 172));
        // tonight Sal and Tony are inside; Micah has the alley to himself
        State.SetFlag("alley3");
        State.SetFlag("alley3_sal_inside");
        State.SetFlag("alley3_tony_inside");
        await Game.ChangeRoom("alley", "act3");
    }

    private static readonly string[] DrawerFlags = { "took_revolver", "took_dollar", "took_lockpick" };

    /// <summary>How many of the drawer's things (revolver, dollar, lockpicks) Micah hasn't taken yet.</summary>
    private int DrawerLeft() => DrawerFlags.Count(f => !State.HasFlag(f));

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
            case ("door", Verb.Walk or Verb.Hand) when DrawerLeft() > 0:
                await Say("Not without my things from the top drawer. A man goes out at night in this town, he goes prepared.");
                return true;
            case ("door", Verb.Walk or Verb.Hand) when State.HasFlag("on_map"):
                await Game.ChangeRoom("chicago_map", "start");
                return true;

            case ("drawer", Verb.Hand):
                if (State.HasFlag("drawer_open"))
                {
                    State.SetFlag("drawer_open", false);
                    return true;
                }
                State.SetFlag("drawer_open");
                await Say(DrawerLeft() switch
                {
                    0 => "Empty. The story of my life.",
                    3 => "My revolver, my entire savings: one dollar, and my picks.",
                    _ => "What's left of the important things.",
                });
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
                State.GiveItem("revolver");
                State.SetFlag("took_revolver");
                await Say("Last time I carried it, I shot a mailbox. Let's hope the mailboxes behave tonight.");
                return true;
            case ("lockpick", Verb.Hand):
                State.GiveItem("lockpick");
                State.SetFlag("took_lockpick");
                await Say("My picks. A locked door is just a question nobody's asked politely yet.");
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

    public override async Task<bool> OnItemVerb(Verb verb, string item)
    {
        if (item != "book" || verb != Verb.Hand) return false;
        if (State.HasFlag("read_book"))
        {
            await Say("Groves, wells, bonfires on the hills. I've read enough of it for one lifetime.");
            return true;
        }
        State.SetFlag("read_book");
        await Say("\"Rites of the Old Isles.\" Midsummer fires. Oak groves. Wells you whisper your sins into.");
        await Say("Druids and dew and the turning of the seasons. Pretty, if you're a farmer. I'm not.");
        await Say("Wait. Something slipped out from between the pages. A little sheet of paper.");
        State.GiveItem("address");
        State.SetFlag("club_unlocked");
        await Say("An address, in a woman's hand. \"The Club, 18 W. Hubbard.\" Just that. A place that doesn't need a name.");
        return true;
    }
}
