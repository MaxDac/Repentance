using System.Threading.Tasks;

namespace Repentance.Story;

/// <summary>Story puzzles finished from more than one place (an inventory combination, a room hotspot or the autoplay test).</summary>
public static class StoryPuzzles
{
    public static async Task TryReadAccounts(Game game)
    {
        var state = GameState.Instance;
        if (game.Room is not Rooms.MansionStudy || state.HasFlag("entered_bedroom"))
        {
            await game.Say("I need the study desk to lay these out. Once I go through that bedroom door, I won't get another chance.");
            return;
        }
        if (!state.HasItem("audit_folder") || !state.HasItem("audit_tracing"))
        {
            await game.Say("The numbered accounts need the auditor's index. The other desk drawer might have it.");
            return;
        }
        if (!await game.Hud.Puzzle.Open(PuzzleKind.Alignment)) return;
        state.TakeItem("audit_folder");
        state.TakeItem("audit_tracing");
        state.GiveItem("documents");
        state.SetFlag("audit_identified");
        state.SetFlag(Endings.TookDocuments);
        await game.Say("Bank, judge, captain. The index identifies the numbered pocket in the drawer. Inside: signed payment sheets. Names, dates, signatures. Into the coat. Insurance.");
        await game.Think("Under the bank drafts, a page headed \"Thursdays\". Girls' first names, a railway station beside each, and a price. Caleb's fourteen were the lucky ones.");
    }

    public static async Task TryDecodeCard(Game game)
    {
        var state = GameState.Instance;
        if (state.HasFlag("card_decoded") || !state.HasItem("card") || !state.HasItem("mirror") ||
            !PuzzleRules.CipherReady(state.HasFlag("read_book"), state.HasFlag("card_warmed"), state.HasFlag("card_reflected")))
            return;
        if (!await game.Hud.Puzzle.Open(PuzzleKind.Cipher)) return;
        state.SetFlag("card_decoded");
        state.GiveItem("address");
        state.SetFlag("club_unlocked");
        await game.Say("Lily, leaf, feather. The Club, 18 W. Hubbard. I copy it onto a slip. A place that doesn't need a name.");
    }
}
