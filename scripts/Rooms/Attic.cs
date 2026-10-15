using Godot;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Prologue, present day. Daniel sorts the attic of the house he just bought, full of the previous
/// owners' family junk. Doubles as the tutorial: look (left click), the verb wheel (right click),
/// kick, the satchel and using an item on something. Opening the trunk finds Micah's journal; reading
/// it takes the story back to Chicago, 1927.
/// </summary>
public partial class Attic : Room
{
    private static readonly Texture2D[] ActBackgrounds =
    {
        GD.Load<Texture2D>("res://assets/art/rooms/attic_act1.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_act2.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_act3.png"),
    };

    private static readonly Texture2D[] PapersTextures =
    {
        GD.Load<Texture2D>("res://assets/art/rooms/attic_papers.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_papers_act2.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_papers_act3.png"),
    };

    // the MISC carton searched open, with the tool tin set down on the box below it
    private static readonly Texture2D[] BoxOpenTextures =
    {
        GD.Load<Texture2D>("res://assets/art/rooms/attic_box_open.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_box_open_act2.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_box_open_act3.png"),
    };

    private static readonly Texture2D[] ChairTextures =
    {
        GD.Load<Texture2D>("res://assets/art/rooms/attic_chair.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_chair_act2.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_chair_act3.png"),
    };

    private static readonly Texture2D[] TrunkOpenTextures =
    {
        GD.Load<Texture2D>("res://assets/art/rooms/attic_trunk_open.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_trunk_open_act2.png"),
        GD.Load<Texture2D>("res://assets/art/rooms/attic_trunk_open_act3.png"),
    };

    private Task Hint(string text) => Say("hint", text);

    private const string StashPrefix = "stash_";

    /// <summary>Micah's pockets stay in 1927 while Daniel is in the present: stashed as flags so they survive saves.</summary>
    public static void StashMicahItems()
    {
        var gs = GameState.Instance;
        foreach (var id in System.Linq.Enumerable.ToList(gs.Inventory))
        {
            // pinned items (notepad, lighter) aren't stashed: they are Micah's by definition and come back with him
            if (!MicahKit.IsPinned(id)) gs.SetFlag(StashPrefix + id);
            gs.TakeItem(id);
        }
    }

    /// <summary>
    /// Starts <paramref name="act"/> in 1927: gives back the stashed items that act still needs, leaves the rest in the
    /// past for good, and drops Daniel's journal.
    /// </summary>
    public static void RestoreMicahItems(int act)
    {
        var gs = GameState.Instance;
        gs.TakeItem("journal");
        foreach (var flag in System.Linq.Enumerable.ToList(gs.Flags))
        {
            if (!flag.StartsWith(StashPrefix)) continue;
            gs.SetFlag(flag, false);
            string id = flag[StashPrefix.Length..];
            if (MicahKit.KeptInAct(act, id)) gs.GiveItem(id);
        }
    }

    // End of Act 1: the same evening, dark outside and the lamp on.
    private static readonly Texture2D NightBackground = GD.Load<Texture2D>("res://assets/art/rooms/attic_night.png");
    private static readonly Texture2D NightPapers = GD.Load<Texture2D>("res://assets/art/rooms/attic_papers_night.png");
    private static readonly Texture2D NightBoxOpen = GD.Load<Texture2D>("res://assets/art/rooms/attic_box_open_night.png");
    private static readonly Texture2D NightChair = GD.Load<Texture2D>("res://assets/art/rooms/attic_chair_night.png");
    private static readonly Texture2D NightTrunkOpen = GD.Load<Texture2D>("res://assets/art/rooms/attic_trunk_open_night.png");

    private Task SatchelHint()
    {
        if (State.HasFlag("satchel_hint")) return Task.CompletedTask;
        State.SetFlag("satchel_hint");
        return Hint("(Your things go in the satchel, bottom right. Click an item to hold it, then click where to use it.)");
    }

    protected override void OnRefresh()
    {
        if (State.HasFlag("attic_night"))
        {
            if (GetNodeOrNull<Sprite2D>("Background") is { } night)
                night.Texture = NightBackground;
            SetTexture("Papers", NightPapers);
            SetTexture("BoxOpen", NightBoxOpen);
            SetTexture("Chair", NightChair);
            SetTexture("TrunkOpen", NightTrunkOpen);
            return;
        }
        int actIndex = Mathf.Clamp(State.StoryAct, 1, ActBackgrounds.Length) - 1;
        if (GetNodeOrNull<Sprite2D>("Background") is { } background)
            background.Texture = ActBackgrounds[actIndex];
        SetTexture("Papers", PapersTextures[actIndex]);
        SetTexture("BoxOpen", BoxOpenTextures[actIndex]);
        SetTexture("Chair", ChairTextures[actIndex]);
        SetTexture("TrunkOpen", TrunkOpenTextures[actIndex]);
    }

    private void SetTexture(string nodePath, Texture2D texture)
    {
        if (GetNodeOrNull<Sprite2D>(nodePath) is { } sprite)
            sprite.Texture = texture;
    }

    public override async Task OnEnter(string entry)
    {
        if (entry == "night")
        {
            await EndOfActOne();
            return;
        }
        if (entry == "night2")
        {
            await EndOfActTwo();
            return;
        }
        if (entry == "epilogue")
        {
            await Epilogue();
            return;
        }
        if (State.HasFlag("attic_intro")) return;
        State.SetFlag("attic_intro");
        await Game.Run(async () =>
        {
            await Wait(0.6);
            await Talk("attic_intro");
            await Hint("(Left-click to walk or look at things. Right-click on something for the action wheel.)");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("hatch", Verb.Talk):
                await Talk("leo_call");
                return true;
            case ("hatch", Verb.Walk or Verb.Hand):
                await Say("Not before I've made a dent in this mess. I promised.");
                return true;
            case ("hatch", Verb.Kick):
                await Say("Kicking the hatch shut would only trap me up here. With the dress form.");
                return true;

            case ("sheet", Verb.Hand):
                State.SetFlag("sheet_lifted");
                await Say("A rocking chair. Under a sheet. In an attic. Not creepy at all.");
                return true;
            case ("chair", Verb.Kick):
                await Say("It rocks. All by itself. For way too long.");
                return true;
            case ("chair", Verb.Hand):
                await Say("I'm not sitting in it. Whoever sat in it last is probably still sitting in it.");
                return true;

            case ("boxes", Verb.Hand or Verb.Kick) when !State.HasFlag("boxes_spilled"):
                State.SetFlag("boxes_spilled");
                await Say(verb == Verb.Kick ? "Oops." : "Let's start with the top one... whoa, whoa, WHOA!");
                await Say("Great. Thirty years of tax returns, all over the floor.");
                return true;
            case ("boxes", Verb.Look) when State.HasFlag("boxes_spilled") && !State.HasFlag("tool_tin_found"):
                await Say("TAXES gave up everything it had. MISC is still taped shut, and something in it went CLUNK when the stack came down.");
                return true;
            case ("boxes", Verb.Hand) when State.HasFlag("boxes_spilled") && !State.HasFlag("tool_tin_found"):
                State.SetFlag("tool_tin_found");
                await Say("Let's try that again. Gently. MISC first...");
                await Say("Old newspaper, a broken picture frame... and a tool tin. Heavy. I'll set it on the box below.");
                await Say("A little brass padlock on it: a little key, then. Not much of a riddle, but I'll take it.");
                return true;
            case ("boxes", Verb.Kick) when State.HasFlag("boxes_spilled") && !State.HasFlag("tool_tin_found"):
                await Say("Kicking them is how the tax returns ended up on the floor. Something's rattling in MISC, though.");
                return true;
            case ("boxes", Verb.Hand or Verb.Kick):
                await Say("I've done enough damage to those boxes for one day.");
                return true;

            case ("papers", Verb.Look):
                await Say("Receipts, bank statements, a 1994 Pizza Hut menu. Nothing worth keeping.");
                return true;
            case ("papers", Verb.Hand):
                await Say("I'll file them later. In the recycling bin.");
                return true;
            case ("tool_tin", Verb.Look or Verb.Hand):
                await Say(State.HasFlag("got_crowbar") ? "The tin is empty now." : "A small locked tool tin. That little suitcase key might fit.");
                return true;
            case ("tool_tin", Verb.UseItem) when item == "suitcase_key" && !State.HasFlag("got_crowbar"):
                State.SetFlag("got_crowbar");
                State.GiveItem("crowbar");
                await Say("The small key turns. Inside, a crowbar. A small lock gets me into the big one.");
                await SatchelHint();
                return true;

            case ("trunk", Verb.Look):
                await Say(State.HasFlag("trunk_open")
                    ? "Mothballs and an old overcoat. Whoever packed this wanted it forgotten."
                    : "A steamer trunk. Brass corners, and initials on the lid: M. J. It's locked.");
                return true;
            case ("trunk", Verb.Hand) when !State.HasFlag("trunk_open"):
                await Say("Locked. The key's probably been at the bottom of Lake Michigan for decades.");
                return true;
            case ("trunk", Verb.UseItem) when item == "suitcase_key" && !State.HasFlag("trunk_open"):
                await Say("It slides in... and won't turn. Not even a little. Wrong lock.");
                await Say("Figures. The small key opens some small thing. This is a big thing.");
                return true;
            case ("trunk", Verb.Kick) when !State.HasFlag("trunk_open"):
                State.SetFlag("trunk_kicked");
                await Say("OW! Solid oak. I need some leverage, not a broken toe.");
                return true;
            case ("trunk", Verb.UseItem) when item == "crowbar" && !State.HasFlag("trunk_open"):
                State.TakeItem("crowbar");
                State.SetFlag("trunk_open");
                await Say("Come on... come on...");
                await Say("*CRACK*");
                await Say("Mothballs. An overcoat that's seen better decades. And under it...");
                State.GiveItem("journal");
                await Say("A journal. Leather, really old. \"M. Jones\" stamped on the cover.");
                await Hint("(Right-click the journal in your satchel and use the hand to read it.)");
                return true;
            case ("trunk", Verb.Hand or Verb.Kick):
                await Say("It's open. Nothing else in there but mothballs.");
                return true;

            case ("suitcase", Verb.Look) when !State.HasFlag("got_suitcase_key"):
                await Say("A battered suitcase. Something rattles inside it when I nudge it with my foot.");
                return true;
            case ("suitcase", Verb.Hand) when !State.HasFlag("got_suitcase_key"):
                State.SetFlag("got_suitcase_key");
                State.GiveItem("suitcase_key");
                await Say("Empty... no, wait. Something's sewn into the lining.");
                await Say("A key! Small, brass. Maybe it fits something else up here.");
                await SatchelHint();
                return true;
            case ("suitcase", Verb.Hand):
                await Say("Empty now. Even the lining.");
                return true;

            case ("radio", Verb.Hand):
                await Say("Click... nothing. It hasn't played a note since before my grandfather was born.");
                return true;
            case ("radio", Verb.Kick):
                await Say("The \"percussive maintenance\" approach. Still nothing.");
                return true;
            case ("dress_form", Verb.Talk):
                await Say("Hi. Nice to meet you. ...Leo's right, I need to get out more.");
                return true;
            case ("dress_form", Verb.Hand or Verb.Kick):
                await Say("I'd rather not touch her. It. I'd rather not touch it.");
                return true;
            case ("window", Verb.Hand):
                await Say("Painted shut. Like every other window in this house.");
                return true;
            case ("painting", Verb.Hand):
                await Say("Some stern-looking people in very stiff collars. They can stay up here.");
                return true;
        }
        return false;
    }

    public override async Task<bool> OnItemVerb(Verb verb, string item)
    {
        if (item != "journal" || verb != Verb.Hand) return false;
        if (State.StoryAct >= 2)
        {
            await Talk("journal_act2");
            RestoreMicahItems(2);
            // pick up the 1927 story where the old lead from the Blue Lantern left it
            State.SetFlag("sal_passed");
            State.SetFlag("photo_shown");
            State.SetFlag("club_lead");
            // The office opening leads to the cathedral, then the city map.
            State.SetFlag("act2_church");
            State.SetFlag("on_map");
            await Game.Hud.Fade(1, 1.5);
            Game.Hud.ShowCaption("Chicago, 1927.");
            await Wait(2.8);
            Game.Hud.ShowCaption(null);
            await Game.ChangeRoom("office", "act2");
            return true;
        }
        await Talk("journal");
        State.TakeItem("journal");
        State.TakeItem("suitcase_key");
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("Chicago, 1927.");
        await Wait(2.8);
        Game.Hud.ShowCaption(null);
        await Game.ChangeRoom("office", "start");
        return true;
    }

    /// <summary>
    /// Back from 1927: it got dark while Daniel was reading and the lamp is on. Leo calls him down for dinner. Then
    /// Act 2 begins, the next day, with Daniel back in the attic and the journal in hand.
    /// </summary>
    private Task EndOfActOne() => Game.Run(async () =>
    {
        StashMicahItems();
        State.SetFlag("attic_night");
        Refresh();
        Player.Face(Facing.Down);
        await Game.Hud.Fade(0, 1.2);
        await Wait(0.8);
        await Say("...");
        await Talk("dinner_call");
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("End of Act One");
        await Wait(2.5);
        Game.Hud.ShowCaption("Act Two - The next day");
        await Wait(2.5);
        Game.Hud.ShowCaption(null);
        State.SetFlag("attic_night", false);
        State.SetStoryAct(2);
        State.GiveItem("journal");
        Refresh();
        Player.Teleport(EntryPoint("start"), Facing.Down);
        await Game.Hud.Fade(0, 1.2);
        await Talk("attic_act2");
        await Hint("(Right-click the journal in your satchel and use the hand to keep reading.)");
    });

    /// <summary>
    /// Back from the Club: it got dark again while Daniel was reading. Leo calls him for dinner, and Act 3 picks up
    /// that night, with Daniel reading in bed.
    /// </summary>
    private Task EndOfActTwo() => Game.Run(async () =>
    {
        StashMicahItems();
        State.GiveItem("journal");
        State.SetFlag("masked", false);
        State.SetFlag("attic_night");
        Refresh();
        Player.Face(Facing.Down);
        await Game.Hud.Fade(0, 1.2);
        await Wait(0.8);
        await Say("...");
        await Talk("dinner_call2");
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("End of Act Two");
        await Wait(2.5);
        Game.Hud.ShowCaption("Act Three - That night");
        await Wait(2.5);
        Game.Hud.ShowCaption(null);
        State.SetFlag("attic_night", false);
        State.SetStoryAct(3);
        await Game.ChangeRoom("bedroom", "start");
    });

    private int EndingNumber() => Enumerable.Range(1, 7).FirstOrDefault(n => State.HasFlag($"ending_{n}"));

    /// <summary>
    /// After Act 3: Daniel reads the last entry. He keeps the journal for Leo if Micah found his way back
    /// (<see cref="Endings.KeepsJournal"/>); otherwise it goes back in the trunk.
    /// </summary>
    private Task Epilogue() => Game.Run(async () =>
    {
        await Wait(0.8);
        await Talk("epilogue");
        if (!Endings.KeepsJournal(EndingNumber()))
        {
            await Game.WalkTo(new Vector2(384, 224));
            Player.Face(Facing.Right);
            State.TakeItem("journal");
            if (!State.HasFlag("ending_7"))
                await Say("Back in the trunk you go. Somebody else can find you in another hundred years.");
        }
        await Wait(0.6);
        await Game.Hud.Fade(1, 2.0);
        Game.Hud.ShowCaption("The End");
        // the story is over: keep the game on the caption until a load or a new game
        await Game.HoldTheEnd();
        Game.Hud.ShowCaption(null);
    });
}