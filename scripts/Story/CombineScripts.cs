using Godot;
using System.Threading.Tasks;

namespace Repentance.Story;

/// <summary>
/// Story combinations that need more than the <see cref="Recipes"/> table: a flag check, a picture, or a puzzle.
/// Called before the recipes, and only when Micah holds both items.
/// </summary>
public static class CombineScripts
{
    public static async Task<bool> TryCombine(Game game, string first, string second)
    {
        var state = GameState.Instance;
        if (PuzzleRules.Pair(first, second, "cloth", "mirror_waxed"))
        {
            if (!state.HasFlag("mirror_warmed"))
            {
                await game.Say("The cloth won't shift cold wax. Gentle warmth first.");
                return true;
            }
            state.TakeItem("mirror_waxed");
            state.TakeItem("cloth");
            state.GiveItem("mirror");
            state.SetFlag("got_mirror");
            await game.Say("The wax lifts cleanly. I put the borrowed cloth back on the bed.");
            await game.Hud.ShowImageWithLines(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"),
                () => game.Say("Three loops tied in one knot. No beginning, no end. Scratched deep, on purpose."));
            return true;
        }
        if (PuzzleRules.Pair(first, second, "card", "mirror"))
        {
            if (!state.HasFlag("card_warmed"))
            {
                await game.Say("Blank paper in a mirror is still blank paper.");
                return true;
            }
            state.SetFlag("card_reflected");
            if (!state.HasFlag("read_book"))
                await game.Say("Words among the ornaments, in no sensible order. I need a guide to those markings.");
            await StoryPuzzles.TryDecodeCard(game);
            return true;
        }
        if (PuzzleRules.Pair(first, second, "audit_folder", "audit_tracing"))
        {
            await StoryPuzzles.TryReadAccounts(game);
            return true;
        }
        return false;
    }
}
