using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Harrington wine cellar, under the kitchen: black as a coal hole. A storm lantern on a hook, delivery crates (one
/// sloshes - kerosene) and, at the back, the bootleggers' stair up to a panel behind the old man's study bar. Fill the
/// lantern, light it with Micah's lighter and the stair is there to be climbed. It is the only way into the house: the
/// baize door upstairs is bolted from the study side.
/// </summary>
public partial class MansionCellar : Room
{
    private const string EscapeRefusal = "Not back in there. Somebody's on the stairs by now.";

    private bool Lit => State.HasFlag("cellar_lit");

    public override async Task OnEnter(string entry)
    {
        if (Lit || State.HasFlag("seen_mansion_cellar")) return;
        State.SetFlag("seen_mansion_cellar");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Say("Black as a coal hole. I can make out a lantern on a hook and some crates.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
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

    private async Task LightCellar()
    {
        State.TakeItem("lantern_lit");
        State.SetFlag("cellar_lit");
        await Say("I hang the lantern on a nail at the back. Racks of wine, the kind nobody's allowed to drink.");
        await Say("And behind them, stone steps going up to a panel. A bootleggers' stair, straight to the old man's bar.");
    }
}
