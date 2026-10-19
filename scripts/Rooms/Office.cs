using System.Linq;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Micah's office, 9 PM. Teddy Harrington is waiting when the game starts. In Act 3 Micah ends up back here, the lamp
/// off and the whiskey on the desk, staring out of the window and working out who could know where Eleanor is.
/// </summary>
public partial class Office : Room
{
    public override Track? Music => Track.OfficeJazz;

    private const string Art = "res://assets/art/rooms/";

    public override void _Ready()
    {
        // Teddy only waits here in Act 1; later acts (also when reached by a debug room jump) never show him.
        if (State.StoryAct >= 2) State.SetFlag("teddy_gone");
        // Act 3: the lamp stays off and the bottle and cup have moved to the desk
        bool dark = State.StoryAct >= 3;
        State.SetFlag("office_lamp_off", dark);
        if (dark) UseDarkArt();
        // whoever left last opened the door; it's shut again by the time anyone comes back
        State.SetFlag("office_door_open", false);
        State.SetFlag("office_door_ajar", false);
        // saves from before Teddy paid in person: he's gone, so the money he left is on the desk
        if (State.HasFlag("teddy_gone") && !State.HasFlag("took_dollar")) State.SetFlag("teddy_paid");
        // once the picks are out of the filing cabinet its drawer stays shut for the rest of the story
        if (State.HasFlag("took_lockpick")) State.SetFlag("cabinet_open", false);
        base._Ready();
        _glint = GetNodeOrNull<Godot.Sprite2D>("WeddingRing/Glint");
    }

    private void UseDarkArt()
    {
        foreach (var (node, file) in new[]
                 {
                     ("Background", "office_act3"), ("DoorAjar", "office_act3_door_ajar"),
                     ("DoorOpen", "office_act3_door_open"), ("CabinetOpen", "office_act3_cabinet_open"),
                     ("CabinetLockpick", "office_act3_cabinet_lockpick"), ("Holster", "office_act3_holster"),
                     ("DeskCash", "office_act3_cash"),
                 })
            if (GetNodeOrNull<Godot.Sprite2D>(node) is { } sprite)
                sprite.Texture = Godot.GD.Load<Godot.Texture2D>($"{Art}{file}.png");
    }

    private const double GlintEvery = 3.5, GlintFrameTime = 0.08;
    private Godot.Sprite2D? _glint;
    private double _glintClock;

    /// <summary>The ring is only a couple of gold pixels; every few seconds it catches the lamp light and sparkles.</summary>
    public override void _Process(double delta)
    {
        if (_glint == null) return;
        _glintClock = (_glintClock + delta) % GlintEvery;
        int frame = (int)(_glintClock / GlintFrameTime);
        _glint.Visible = frame < _glint.Hframes;
        if (_glint.Visible) _glint.Frame = frame;
    }

    public override async Task OnEnter(string entry)
    {
        if (entry == "act2" && !State.HasFlag("act2_office_done"))
        {
            await Game.Run(Act2Opening);
            return;
        }
        if (entry == "act3" && State.HasFlag("micah_at_desk"))
        {
            await Game.Run(AtTheWindow);
            return;
        }
        if (State.HasFlag("teddy_gone")) return;
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Rain ticks on the window. The radiator knocks. Nine o'clock, and the bottle's already lower than the day.");
            await Think("Another night, another bottle. And a client in my chair, too well dressed for this floor.");
            await Talk("teddy");
            await TeddyLeaves();
        });
    }

    private async Task Act2Opening()
    {
        await Think("The office again. Teddy's twenty a day is gone, and the bottle's still here. Loyal, the bottle.");
        await Game.WalkTo(new Godot.Vector2(124, 172));
        Player.Face(Facing.Right);
        State.SetFlag("office_cup_held");
        Player.SetPose("micah_cup");
        await Wait(0.5);
        Player.SetPose("micah_drink");
        await Wait(1.2);
        Player.SetPose("micah_cup");
        await Wait(0.5);
        Player.SetPose(null);
        State.SetFlag("office_cup_held", false);
        State.SetFlag("act2_whiskey_drunk");
        await Think("Whiskey. It burns going down. It doesn't burn away a thing.");
        await Talk("office_ring");
        State.SetFlag("act2_office_done");
        await Game.WalkTo(new Godot.Vector2(58, 172));
        await OpenTheDoor(player: true);
        await Game.ChangeRoom("church_exterior", "start");
    }

    private async Task TeddyLeaves()
    {
        if (!State.HasFlag("teddy_briefed") || FindActor("teddy") is not { } teddy) return;
        await PayTheFirstDay(teddy);
        await Say("teddy", "Good evening, Jones. Do try not to embarrass me.");
        await teddy.MoveTo(new Godot.Vector2(58, 170), 55);
        await OpenTheDoor(player: false);
        State.SetFlag("teddy_gone");
        await CloseTheDoor();
        await Think("Harrington Steel. Funny how the rich always lose the things they never paid attention to.");
        await Think("A wife who walked out. I know a thing or two about that. Just never from his side of the door.");
    }

    /// <summary>
    /// Teddy's first day in advance: at the corner of the desk by the lamp, the wallet out of his breast pocket, a few
    /// notes peeled off and laid down for Micah to pick up. Micah's remark comes once the money is on the desk.
    /// </summary>
    private async Task PayTheFirstDay(Actor teddy)
    {
        if (State.HasFlag("teddy_paid")) return;
        teddy.FaceLeft(false);
        await Say("teddy", "Before I forget. Twenty for the day, and two for your quaint expenses.");
        await teddy.MoveTo(DeskCorner, 45);
        teddy.FaceLeft(false);
        await teddy.PlayPose("teddy_wallet");
        await teddy.PlayPose("teddy_leave_notes");
        State.SetFlag("teddy_paid");
        await Wait(0.2);
        teddy.SetPose(null);
        await Think("Twenty-two dollars. Pocket lint to him. A day's pay to me, and then some.");
    }

    /// <summary>Where Teddy stands to reach the corner of the desk, just left of it.</summary>
    private static readonly Godot.Vector2 DeskCorner = new(159, 176);

    /// <summary>
    /// The frosted door swings in on its left hinges, then the leaf is clear of the frame. The knob is on the right,
    /// so the actor faces right to reach it.
    /// </summary>
    private async Task OpenTheDoor(bool player)
    {
        State.SetFlag("office_door_ajar");
        await Wait(0.12);
        if (player)
        {
            Player.Face(Facing.Right);
            await Player.PlayPose("micah_open_door");
        }
        else if (FindActor("teddy") is { } teddy)
        {
            teddy.FaceLeft(false);
            await teddy.PlayPose("teddy_open_door");
            teddy.SetPose(null);
        }
        State.SetFlag("office_door_ajar", false);
        State.SetFlag("office_door_open");
    }

    private async Task CloseTheDoor()
    {
        State.SetFlag("office_door_open", false);
        State.SetFlag("office_door_ajar");
        await Wait(0.28);
        State.SetFlag("office_door_ajar", false);
    }

    /// <summary>
    /// Act 3: in the dark, the whiskey poured on the desk behind him, Micah stands at the window with his back to the
    /// room, thinking it over under the HOTEL sign; then he turns round and heads for the Blue Lantern.
    /// </summary>
    private async Task AtTheWindow()
    {
        Player.Face(Facing.Up);
        await Wait(1.0);
        await Think("Back in my own office. Lamp off. The whiskey's still there. Some things you can count on.");
        await Think("Thanks to my efforts, he said. How'd they find her through me? Somebody on my heels? Something I let slip?");
        await Think("Aw, what's the difference? They've got her just the same.");
        await Think("Where would they take her? Not the Club, not tonight. Not the hotel. Not Teddy's, he'd have to explain her.");
        await Think("The convent's done with me. Caleb would sooner pray than talk. The cops are on somebody's payroll.");
        await Think("Who knows where the Club keeps its girls? Who delivers to people like that, and keeps his mouth shut?");
        await Think("The Blue Lantern. Tony and his gorilla. The mob knows every back door in this town. They deliver to most of them.");
        State.SetFlag("micah_at_desk", false);
        Player.Face(Facing.Left);
        await Wait(0.4);
        await Think("Before I go: my wedding ring, and Caleb's door. Last chances to remember who I'm supposed to be coming home to.");
    }

    private async Task LeaveAct3()
    {
        State.SetFlag("visit_caleb_act3", false);
        await Talk("office_act3_destination");
        if (State.HasFlag("visit_caleb_act3"))
        {
            await Game.ChangeRoom("church_interior", "act3");
            return;
        }
        // tonight Sal and Tony are inside; Micah has the alley to himself
        State.SetFlag("alley3");
        State.SetFlag("alley3_sal_inside");
        State.SetFlag("alley3_tony_inside");
        await Game.ChangeRoom("alley", "act3");
    }

    /// <summary>
    /// Micah's kit for the night (the flag set when he takes each thing) and how he calls it, with where it is, so the
    /// door tells the player what is left and where to look.
    /// </summary>
    private static readonly (string Flag, string Name)[] Kit =
    {
        ("took_revolver", "my gun off the coat rack"), ("took_lockpick", "my picks from the filing cabinet"),
        ("took_dollar", "my fee off the desk"),
    };

    /// <summary>What Micah still has to pick up before he goes out, in his words ("my gun off the coat rack and ...").</summary>
    private string? MissingKit()
    {
        var names = Kit.Where(k => !State.HasFlag(k.Flag)).Select(k => k.Name).ToList();
        return names.Count switch
        {
            0 => null,
            1 => names[0],
            _ => string.Join(", ", names.Take(names.Count - 1)) + " and " + names[^1],
        };
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Walk or Verb.Hand) when State.StoryAct == 3:
                await OpenTheDoor(player: true);
                await LeaveAct3();
                return true;
            case ("faith_ring", Verb.Hand):
                State.GiveItem("faith_ring");
                State.SetFlag("took_faith_ring");
                await Say("I've left this behind long enough.");
                return true;
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
            case ("door", Verb.Walk or Verb.Hand) when MissingKit() is { } missing:
                await Say($"Not without {missing}. A man goes out at night in this town, he goes prepared.");
                return true;
            case ("door", Verb.Walk or Verb.Hand) when State.HasFlag("on_map"):
                await OpenTheDoor(player: true);
                await Game.ChangeRoom("chicago_map", "start");
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await OpenTheDoor(player: true);
                return false;

            case ("filing", Verb.Hand) when State.HasFlag("cabinet_open"):
                State.SetFlag("cabinet_open", false);
                return true;
            case ("filing", Verb.Hand) when !State.HasFlag("took_lockpick"):
                State.SetFlag("cabinet_open");
                await Say("The middle drawer. Old files, and my picks rolled up in front where I can reach them.");
                return true;
            case ("filing", Verb.Hand):
                await Say("C for Cases. Empty. D for Debts. Overflowing. Unpaid bills I'm not opening again until 1931.");
                return true;
            case ("filing", Verb.Kick):
                await Say("Kicking my own filing cabinet. That's a new low, even for me.");
                return true;

            case ("dollar", Verb.Hand):
                State.GiveItem("dollar");
                State.SetFlag("took_dollar");
                await Say("Twenty-two dollars. Teddy's first day, paid in advance. Better make it count.");
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
                await Wait(0.2);
                State.SetFlag("cabinet_open", false);
                return true;

            case ("bottle", Verb.Hand) when State.HasFlag("office_lamp_off"):
                await Say("Not tonight. Tonight I need my hands steady.");
                return true;
            case ("cup", Verb.Hand) when State.HasFlag("office_lamp_off"):
                await Say("I poured it. I don't have to drink it.");
                return true;
            case ("lamp", Verb.Hand) when State.HasFlag("office_lamp_off"):
                await Say("Leave it off. I can think in the dark. I've had the practice.");
                return true;
            case ("lamp", Verb.Look) when State.HasFlag("office_lamp_off"):
                await Say("The green banker's lamp, switched off. The HOTEL sign does the lighting tonight.");
                return true;
            case ("bottle", Verb.Hand):
                await Say("Whiskey. It never gave me a good answer.");
                return true;
            case ("cup", Verb.Hand):
                await Say("I've had enough for tonight.");
                return true;
            case ("phone", Verb.Hand or Verb.Talk):
                await Say("Nobody to call. Nobody who'd answer, anyway.");
                return true;
            case ("window", Verb.Hand):
                await Say("Then I'd hear the city. I hear enough of it already.");
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
            case ("radiator", Verb.UseItem) when item == "card":
                State.SetFlag("card_warmed");
                await Say("In the radiator's warmth, ink rises between the curlicues. Backward writing. I'll need a reflection.");
                await Game.Hud.ShowImage(Godot.GD.Load<Godot.Texture2D>("res://assets/art/ui/card_reversed.png"));
                await Story.StoryPuzzles.TryDecodeCard(Game);
                return true;
        }
        return false;
    }

    public override async Task<bool> OnItemVerb(Verb verb, string item)
    {
        if (item != "book" || verb != Verb.Hand) return false;
        if (State.HasFlag("read_book"))
        {
            await Say("Concealed messages: gentle warmth, then a reflection. Ornament order: lily, leaf, feather.");
            await Story.StoryPuzzles.TryDecodeCard(Game);
            return true;
        }
        State.SetFlag("read_book");
        await Say("\"Rites of the Old Isles.\" Midsummer fires. Oak groves. Wells you whisper your sins into.");
        await Say("Druids and dew and the turning of the seasons. Pretty, if you're a farmer. I'm not.");
        await Say("A page about concealed messages. Gentle warmth brings up the ink; a mirror turns the writing back.");
        await Say("The ornaments give the order: lily first, leaf second, feather last. Those curlicues on the hotel card weren't just decoration.");
        await Story.StoryPuzzles.TryDecodeCard(Game);
        return true;
    }
}
