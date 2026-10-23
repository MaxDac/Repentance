using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Harrington wine cellar, under the kitchen: black as a coal hole. A storm lantern on a hook, delivery crates (one
/// sloshes - kerosene) and, at the back, the bootleggers' stair up to a panel behind the old man's study bar. Fill the
/// lantern, light it with Micah's lighter and the stair is there to be climbed. It is the only way into the house: the
/// baize door upstairs is bolted from the study side. On the way out, Micah can come back down, open the Club's whiskey
/// barrel, take the lantern off its nail and set the cellar alight under the house.
/// </summary>
public partial class MansionCellar : Room
{
    public override Track? Music => Track.MansionDread;

    private const string EscapeRefusal = "Not back in there. Somebody's on the stairs by now.";

    private bool Lit => State.HasFlag("cellar_lit");
    private bool Escaping => State.HasFlag("escaping");
    private bool Open => State.HasFlag("barrel_open");
    private bool Coda => State.HasFlag("eleanor_coda");

    public override async Task OnEnter(string entry)
    {
        if (Coda)
        {
            if (State.HasFlag("took_hung_lantern")) return;
            await Game.Run(() => Think("The cellar. Micah's lantern still burned on its nail, and the Club's whiskey lay on its side by the racks."));
            return;
        }
        if (Escaping && !State.HasFlag("cellar_fire") && !State.HasFlag("seen_cellar_escape"))
        {
            State.SetFlag("seen_cellar_escape");
            await Game.Run(async () =>
            {
                await Wait(0.4);
                await Think("The Club's whiskey, in a barrel on the floor. Enough proof down here to light up the Gold Coast.");
            });
            return;
        }
        if (Lit || State.HasFlag("seen_mansion_cellar")) return;
        State.SetFlag("seen_mansion_cellar");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Down the steps into the cold. The dark here has weight, like a confessional with the priest gone home.");
            await Think("Black as a coal hole. I can make out a lantern on a hook and some crates.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (Coda) return await CodaInteract(verb, target, item);
        switch (target.Id, verb)
        {
            case ("kitchen_steps", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_kitchen", "cellar");
                return true;

            case ("lantern", Verb.Look):
                await Say("A storm lantern on a hook. Dry as a bone, by the weight of it.");
                return true;
            case ("lantern", Verb.Hand):
                State.SetFlag("took_lantern");
                State.GiveItem("lantern");
                await Say("A tin storm lantern. Wick's fine. Tank's empty.");
                return true;

            case ("crates", Verb.Look) when !State.HasFlag("took_kerosene"):
                await Say("Delivery crates. One of them sloshes - kerosene.");
                return true;
            case ("crates", Verb.Look):
                await Say("Altar wine, by the stencil. Prohibition never reached this cellar.");
                return true;
            case ("crates", Verb.Hand) when !State.HasFlag("took_kerosene"):
                State.SetFlag("took_kerosene");
                State.GiveItem("kerosene");
                await Say("On the crates, a can of kerosene. Somebody down here liked to see what he was carrying.");
                return true;
            case ("crates", Verb.Hand):
                await Say("Wine. Not what I came for.");
                return true;

            case ("barrel", Verb.Look) when Open:
                await Say("Whiskey all over the flags. The cellar smells like a speakeasy at closing time.");
                return true;
            case ("barrel", Verb.Look):
                await Say("Canadian rye, by the stencil, lying on its side. The spigot weeps a little.");
                return true;
            case ("barrel", Verb.Hand or Verb.Kick) when !Escaping:
                await Say("I could use a drink. That's exactly why I won't. Eleanor's upstairs.");
                return true;
            case ("barrel", Verb.Hand or Verb.Kick) when Open:
                await Say("It's running. Let it.");
                return true;
            case ("barrel", Verb.Hand or Verb.Kick):
                State.SetFlag("barrel_open");
                await Say("I knock the spigot wide open. Good Canadian rye, a dollar a glass on Rush Street, all over the floor.");
                await Think(State.HasFlag("took_hung_lantern") ? "Now the flame." : "Now a flame. The lantern's still on its nail.");
                return true;
            case ("barrel", Verb.UseItem) when item == "lantern_lit" && !Escaping:
                await Say("Not why I'm here. Eleanor's somewhere upstairs.");
                return true;
            case ("barrel", Verb.UseItem) when item == "lantern_lit" && !Open:
                await Say("A lantern against a closed barrel just warms the oak. It wants opening first.");
                return true;
            case ("barrel", Verb.UseItem) when item == "lantern_lit":
                await SetFire();
                return true;
            case ("barrel", Verb.UseItem) when item is MicahKit.LighterId or "matchbook":
                await Say(Escaping && Open
                    ? "Light that with my hand and I go up with it. I want something I can throw."
                    : "Not why I'm here. Eleanor's somewhere upstairs.");
                return true;

            case ("hung_lantern", Verb.Hand) when !Escaping:
                await Say("It's lighting my way back. Leave it where it is.");
                return true;
            case ("hung_lantern", Verb.Hand):
                State.SetFlag("took_hung_lantern");
                State.GiveItem("lantern_lit");
                await Say("I lift the lantern off its nail. Still burning, and hot through the bail.");
                return true;

            case ("stair" or "dark", Verb.UseItem) when item == "lantern_lit" && !Lit:
                await LightCellar();
                return true;
            case ("stair" or "dark", Verb.UseItem) when item == "lantern_filled":
                await Say("Full of kerosene and not a flame in it. It wants my lighter.");
                return true;
            case ("stair" or "dark", Verb.UseItem) when item == "lantern":
                await Say("An empty lantern lights nothing.");
                return true;
            case ("stair" or "dark", Verb.UseItem) when item is MicahKit.LighterId or "matchbook":
                await Say("A flame in my fist gives me three seconds of cellar. I need something that stays lit.");
                return true;

            case ("stair", Verb.Hand or Verb.Walk) when State.HasFlag("escaping"):
                await Say(EscapeRefusal);
                return true;
            case ("stair", Verb.Hand or Verb.Walk) when !Lit:
                await Say("I'm not walking into a cellar stair blind.");
                return true;
            case ("stair", Verb.Hand or Verb.Walk):
                await Say("Up the bootleggers' stair, to the panel at the top.");
                await Game.ChangeRoom("mansion_study", "cellar");
                return true;
            case ("stair", Verb.Look) when !Lit:
                await Say("Something back there. Too dark to tell what.");
                return true;

            case ("dark", Verb.Look):
                await Say("Black as a coal hole. I can make out a lantern on a hook and some crates.");
                return true;
            case ("dark", Verb.Hand or Verb.Kick):
                await Say("I'd only find the corners with my shins.");
                return true;
        }
        return false;
    }

    /// <summary>
    /// Eleanor's fire: the lantern Micah hung on its nail on the way in goes into her satchel, the barrel's spigot opens
    /// by hand, and the lantern used on the running whiskey sets the cellar alight.
    /// </summary>
    private async Task<bool> CodaInteract(Verb verb, Hotspot target, string? item)
    {
        bool lantern = State.HasItem("lantern_lit");
        bool burned = State.HasFlag(Endings.EleanorBurned);
        switch (target.Id, verb)
        {
            case ("kitchen_steps", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_kitchen", "cellar");
                return true;
            case ("stair", Verb.Hand or Verb.Walk):
                await Say("eleanor", "Not back up there. Not back to him.");
                return true;
            case ("hung_lantern", Verb.Hand):
                State.SetFlag("took_hung_lantern");
                State.GiveItem("lantern_lit");
                await Say("eleanor", "Micah's lantern, still burning. Hot through the handle. I'll hold it anyway.");
                return true;
            case ("barrel", Verb.Hand or Verb.Kick) when burned || Open:
                await Say("eleanor", burned ? "Let it burn." : lantern
                    ? "It's running. All it wants now is the flame in my hand."
                    : "It's running. All it wants now is a flame. Micah's lantern is still burning on its nail.");
                return true;
            case ("barrel", Verb.Hand or Verb.Kick):
                State.SetFlag("barrel_open");
                await Say("eleanor", "I open the spigot all the way. The Club's rye, all over the flags. Twenty years of Thursdays.");
                await Think(lantern ? "It wanted a flame. She had one in her hand." : "It wanted a flame. Micah's lantern still burned on its nail.");
                return true;
            case ("barrel", Verb.UseItem) when item == "lantern_lit" && !Open:
                await Say("eleanor", "Against the oak, it would only warm the wood. The spigot first.");
                return true;
            case ("barrel", Verb.UseItem) when item == "lantern_lit" && !burned:
                await EleanorFire();
                return true;
            case ("barrel", Verb.Look):
                await Say("eleanor", "The Club's whiskey. They poured it for the gentlemen on Thursdays, and for me, before I went on.");
                return true;
            case ("crates" or "lantern", Verb.Hand):
                await Say("eleanor", "Nothing of mine down here.");
                return true;
        }
        return false;
    }

    private async Task EleanorFire()
    {
        State.TakeItem("lantern_lit");
        await Talk("coda_fire");
        State.SetFlag(Endings.EleanorBurned);
        State.SetFlag("cellar_fire");
        await Say("*FWOOOSH*");
        await Game.WalkTo(new Vector2(110, 226));
        await Game.ChangeRoom("mansion_kitchen", "cellar");
    }

    private async Task SetFire()
    {
        State.TakeItem("lantern_lit");
        await Say("I step back to the stair, swing the lantern once, and let it go.");
        State.SetFlag("cellar_fire");
        await Say("*FWOOOSH*");
        await Say("Blue across the floor, then orange, crawling up the oak. The Club's whiskey, all going up at once.");
        await Think("They drank to their own health down here for twenty years. Let them drink to this.");
        await Game.WalkTo(new Vector2(110, 226));
        await Game.ChangeRoom("mansion_kitchen", "cellar");
    }

    private async Task LightCellar()
    {
        State.TakeItem("lantern_lit");
        State.SetFlag("cellar_lit");
        await Say("I hang the lantern on a nail at the back. Racks of wine, the kind nobody's allowed to drink.");
        await Say("And behind them, stone steps going up to a panel. A bootleggers' stair, straight to the old man's bar.");
        await Think("A rich man's back stair for his bottles. Every vice in this city has a service entrance.");
    }
}
