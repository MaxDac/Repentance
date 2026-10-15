using Godot;
using System.Threading.Tasks;

namespace Repentance.Story;

/// <summary>
/// Story responses to wheel verbs on inventory items that hold anywhere (opening the brass box, studying the mirror
/// or the card). The room's <c>OnItemVerb</c> runs first; anything not handled here gets the default response.
/// </summary>
public static class ItemScripts
{
    public static async Task<bool> TryHandle(Game game, Verb verb, string item)
    {
        if (verb == Verb.Hand && item == "brass_box")
        {
            var state = GameState.Instance;
            state.TakeItem("brass_box");
            state.GiveItem("card");
            state.GiveItem("matchbook");
            state.GiveItem("bluing");
            state.SetFlag("opened_brass_box");
            await game.Say("The clasp gave with a click. Inside: a calling card, a matchbook, and a little vial of Mrs. Stewart's Bluing.");
            await game.Say("A business card, only two letters in it; the same perfume that permeates the whole room, only stronger... hypnotic, even.");
            await game.Say("I hold it under my nose longer than a man on a job should. Get a grip, Micah.");
            await game.Say("The matchbook: a blue lantern on the cover. The Blue Lantern, State Street.");
            await game.Say("Laundry bluing in a lady's jewellery box. Somebody meant to dye a white flower blue. She was going there herself.");
            await game.Say("Two big fellas walked her out the back door without a soul seeing. Fellas like that drink somewhere. That's where her trail goes next.");
            return true;
        }
        if (verb == Verb.Hand && item == "mirror")
        {
            await game.Hud.ShowImageWithLines(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"),
                () => game.Say("Three loops tied in one knot. No beginning, no end. It looks old. Older than the convent."));
            return true;
        }
        if (verb == Verb.Hand && item == "book")
        {
            await game.Say("Not here. A book like that wants a locked door and a desk lamp. My office has both.");
            return true;
        }
        if (item == "card" && GameState.Instance.HasFlag("card_warmed") && verb is Verb.Hand or Verb.Look)
        {
            await game.Say(GameState.Instance.HasFlag("card_reflected")
                ? "Feather: Hubbard. Lily: The Club. Leaf: 18 W. The book's ornament legend should put them in order."
                : "The ink came up in the warmth, but every letter is backward. A reflection might help.");
            await StoryPuzzles.TryDecodeCard(game);
            return true;
        }
        if (verb == Verb.Look && item == "dollar")
        {
            await game.Say($"${CashRules.Balance(GameState.Instance.HasFlag)} in cash. Two dollars for the bellboy; ten for Sal. What's left stays in my pocket.");
            return true;
        }
        return false;
    }
}
