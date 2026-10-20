using System.Threading.Tasks;
using Repentance.Story;

namespace Repentance;

/// <summary>Inventory verbs and combining two items. Story-specific responses live in <c>scripts/Story</c>.</summary>
public partial class Game
{
    /// <summary>The player is Eleanor (an interlude or her coda). Only in the interludes may she use her own satchel.</summary>
    public bool IsEleanor => Player.Character.StartsWith("eleanor");

    /// <summary>Eleanor plays and holds a satchel of her own (the interludes, not her coda).</summary>
    private bool EleanorSatchel => IsEleanor && Interlude.SatchelOpen(GameState.Instance.HasFlag);

    private async Task<bool> CombineItems(string first, string second)
    {
        var state = GameState.Instance;
        if (Room?.PlayerCharacter != "micah" || (IsEleanor && !EleanorSatchel) || !state.HasItem(first) || !state.HasItem(second)) return false;
        if (!IsEleanor && await CombineScripts.TryCombine(this, first, second)) return true;
        var outcome = Recipes.Evaluate(first, second, state.HasItem);
        if (outcome == null) return false;
        Recipes.Apply(outcome, id => state.TakeItem(id), id => state.GiveItem(id), id => state.SetFlag(id));
        await Say(outcome.Line);
        if (outcome.Result != null && Room != null) await Room.OnCombined(outcome.Result);
        return true;
    }

    /// <summary>Applies a wheel verb to an inventory item (also used by the autoplay test).</summary>
    public Task ItemVerb(Verb verb, string item) => Run(async () =>
    {
        // Micah's things stay out of Eleanor's hands: in the interludes she handles only what she found herself
        if (IsEleanor)
        {
            if (EleanorSatchel && item != Notes.ItemId && GameState.Instance.HasItem(item)) await EleanorItemVerb(verb, item);
            return;
        }
        if (item == Notes.ItemId && verb is Verb.Look or Verb.Hand)
        {
            Hud.ShowInventory(false);
            await Hud.Notepad.Open();
            return;
        }
        if (Room != null && await Room.OnItemVerb(verb, item)) return;
        if (await ItemScripts.TryHandle(this, verb, item)) return;
        switch (verb)
        {
            case Verb.Look:
                await Say(Items.Get(item).Description);
                break;
            case Verb.Hand:
                SetCarried(item);
                break;
            case Verb.Talk:
                await Say(Pick("I'm not that lonely. Yet.", "It doesn't answer. Thankfully."));
                break;
            default:
                await Say("I'd rather not break my own things.");
                break;
        }
    });

    /// <summary>Eleanor's own satchel in the interludes: her voice, no Micah item scripts.</summary>
    private async Task EleanorItemVerb(Verb verb, string item)
    {
        switch (verb)
        {
            case Verb.Look:
                await Say(Items.Get(item).Description);
                break;
            case Verb.Hand:
                SetCarried(item);
                break;
            case Verb.Talk:
                await Say(Pick("Talking to my own things. It's been a long night.", "It keeps my secrets better than I do."));
                break;
            default:
                await Say("I need it in one piece.");
                break;
        }
    }
}