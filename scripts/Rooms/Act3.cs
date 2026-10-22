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

    /// <summary>
    /// Resolves the ending, records it as <c>ending_N</c> and moves to its scene. Eleanor rides out with Micah in endings
    /// 2 and 10 (<c>eleanor_rides</c>) and visits him in prison in endings 4 and 11 (<c>eleanor_visits</c>). Ending 12
    /// (Micah killed Tony and gave himself up) is Caleb in the visiting room.
    /// </summary>
    public static Task End()
    {
        int ending = Endings.Resolve(State.HasFlag);
        State.SetFlag($"ending_{ending}");
        if (ending is 2 or 3 or 10) State.SetFlag("outskirts_car");
        if (ending is 2 or 10) State.SetFlag("eleanor_rides");
        if (ending is 4 or 11) State.SetFlag("eleanor_visits");
        if (ending is 5 or 9 or 12) State.SetFlag("caleb_visits");
        if (ending == 8) State.SetFlag("eleanor_epilogue");
        return ending switch
        {
            1 => Game.ChangeRoom("rose_house", "coffee"),
            2 or 3 or 10 => Game.ChangeRoom("outskirts", "ending"),
            7 => Finish(nextMorning: false),
            8 => Game.ChangeRoom("outskirts", "eleanor_alone"),
            9 => Game.ChangeRoom("prison", "eleanor"),
            _ => Game.ChangeRoom("prison", "ending"),
        };
    }

    /// <summary>
    /// Endings 8 and 9 come after Micah's coffee at Rose's door (the coda already played Eleanor's night): records the
    /// ending and moves on to Eleanor's own last scene.
    /// </summary>
    public static Task EleanorAfterRose()
    {
        int ending = Endings.Resolve(State.HasFlag);
        State.SetFlag($"ending_{ending}");
        if (ending == 9) State.SetFlag("caleb_visits");
        else State.SetFlag("eleanor_epilogue");
        return ending == 9 ? Game.ChangeRoom("prison", "eleanor") : Game.ChangeRoom("outskirts", "eleanor_alone");
    }

    /// <summary>
    /// "End of Act Three", then the attic, where Daniel reads the last entry: the next morning, or straight on from his
    /// bed when <paramref name="nextMorning"/> is false (ending 7, which has already cut to black).
    /// </summary>
    public static async Task Finish(bool nextMorning = true)
    {
        await Game.Wait(1.0);
        await Game.Hud.Fade(1, 1.5);
        await Game.Hud.ActCards("End of Act Three", nextMorning ? "The next morning" : null);
        Attic.StashMicahItems();
        State.SetFlag("masked", false);
        State.GiveItem("journal");
        await Game.ChangeRoom("attic", "epilogue");
    }
}
