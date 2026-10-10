using Godot;
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

    private static readonly System.Collections.Generic.List<string> MicahItems = new();

    // End of Act 1: the same evening, dark outside and the lamp on.
    private static readonly Texture2D NightBackground = GD.Load<Texture2D>("res://assets/art/rooms/attic_night.png");
    private static readonly Texture2D NightPapers = GD.Load<Texture2D>("res://assets/art/rooms/attic_papers_night.png");
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
            SetTexture("Chair", NightChair);
            SetTexture("TrunkOpen", NightTrunkOpen);
            return;
        }
        int actIndex = Mathf.Clamp(State.StoryAct, 1, ActBackgrounds.Length) - 1;
        if (GetNodeOrNull<Sprite2D>("Background") is { } background)
            background.Texture = ActBackgrounds[actIndex];
        SetTexture("Papers", PapersTextures[actIndex]);
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
            case ("boxes", Verb.Hand or Verb.Kick):
                await Say("I've done enough damage to those boxes for one day.");
                return true;

            case ("papers", Verb.Look) when !State.HasFlag("got_crowbar"):
                await Say("Receipts, bank statements, a 1994 Pizza Hut menu... and something heavy underneath.");
                return true;
            case ("papers", Verb.Hand) when !State.HasFlag("got_crowbar"):
                State.SetFlag("got_crowbar");
                State.GiveItem("crowbar");
                await Say("A crowbar! Hidden in a box marked MISC. Fair enough.");
                await SatchelHint();
                return true;
            case ("papers", Verb.Hand):
                await Say("I'll file them later. In the recycling bin.");
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
                await Say("A key! Small, brass. Maybe it fits that trunk.");
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
            State.TakeItem("journal");
            foreach (var id in MicahItems) State.GiveItem(id);
            MicahItems.Clear();
            // pick up the 1927 story where the old lead from the Blue Lantern left it
            State.SetFlag("sal_passed");
            State.SetFlag("photo_shown");
            State.SetFlag("club_lead");
            await Game.Hud.Fade(1, 1.5);
            Game.Hud.ShowCaption("Chicago, 1927.");
            await Wait(2.8);
            Game.Hud.ShowCaption(null);
            await Game.ChangeRoom("street", "start");
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
        // Micah's pockets stay in 1927 while Daniel is in the attic
        MicahItems.Clear();
        MicahItems.AddRange(State.Inventory);
        foreach (var id in MicahItems) State.TakeItem(id);
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
}
