using System.Threading.Tasks;
using Repentance.Story;

namespace Repentance;

/// <summary>Inventory verbs and combining two items. Story-specific responses live in <c>scripts/Story</c>.</summary>
public partial class Game
{
    /// <summary>The player is Eleanor (an interlude or her coda): no inventory verbs, no combining.</summary>
    public bool IsEleanor => Player.Character.StartsWith("eleanor");

    private async Task<bool> CombineItems(string first, string second)
    {
        var state = GameState.Instance;
        if (Room?.PlayerCharacter != "micah" || IsEleanor || !state.HasItem(first) || !state.HasItem(second)) return false;
        if (await CombineScripts.TryCombine(this, first, second)) return true;
        var outcome = Recipes.Evaluate(first, second, state.HasItem);
        if (outcome == null) return false;
        Recipes.Apply(outcome, id => state.TakeItem(id), id => state.GiveItem(id), id => state.SetFlag(id));
        await Say(outcome.Line);
        return true;
    }

    /// <summary>Applies a wheel verb to an inventory item (also used by the autoplay test).</summary>
    public Task ItemVerb(Verb verb, string item) => Run(async () =>
    {
        // Micah's things stay out of Eleanor's hands (the satchel is hidden while she plays)
        if (IsEleanor) return;
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
                Hud.ShowInventory(false);
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
}