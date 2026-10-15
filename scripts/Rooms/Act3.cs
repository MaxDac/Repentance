using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Shared Act 3 plumbing: picks the ending (<see cref="Endings.Resolve"/>) and sends Micah to its scene, then closes the
/// act and hands over to Daniel's epilogue in the attic.
/// </summary>
public static class Act3
{
    private static Game Game => Game.Instance;
    private static GameState State => GameState.Instance;

    /// <summary>Sets the derived gate flags the Ink choices read (<c>can_walk_away</c>, <c>can_spare</c>).</summary>
    public static void UpdateGates()
    {
        State.SetFlag("can_walk_away", Endings.CanWalkAwayFromBartender(State.HasFlag, State.HasItem));
        State.SetFlag("can_spare", Endings.CanSpareOldMan(State.HasFlag, State.HasItem));
    }

    /// <summary>Resolves the ending, records it as <c>ending_N</c> and moves to its scene.</summary>
    public static Task End()
    {
        int ending = Endings.Resolve(State.HasFlag);
        State.SetFlag($"ending_{ending}");
        if (ending is 2 or 3) State.SetFlag("outskirts_car");
        return ending switch
        {
            1 => Game.ChangeRoom("rose_house", "coffee"),
            2 or 3 => Game.ChangeRoom("outskirts", "ending"),
            7 => Finish(nextMorning: false),
            _ => Game.ChangeRoom("prison", "ending"),
        };
    }

    /// <summary>
    /// "End of Act Three", then the attic, where Daniel reads the last entry: the next morning, or straight on from his
    /// bed when <paramref name="nextMorning"/> is false (ending 7, which has already cut to black).
    /// </summary>
    public static async Task Finish(bool nextMorning = true)
    {
        await Game.Wait(1.0);
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("End of Act Three");
        await Game.Wait(2.5);
        if (nextMorning)
        {
            Game.Hud.ShowCaption("The next morning");
            await Game.Wait(2.2);
        }
        Game.Hud.ShowCaption(null);
        Attic.StashMicahItems();
        State.SetFlag("masked", false);
        State.GiveItem("journal");
        await Game.ChangeRoom("attic", "epilogue");
    }
}
