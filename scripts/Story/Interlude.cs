using System;
using System.Threading.Tasks;
using Repentance.Rooms;

namespace Repentance.Story;

/// <summary>
/// The two Eleanor interludes (the start of Act 2 and of Act 3) and her coda in the mansion: who the player is, the
/// hand-offs in and out of Micah's journal, and the lines she says where a room has nothing special for her.
/// Flags: "interlude1" / "interlude2" while an interlude plays, "eleanor_coda" in the mansion after the prayer,
/// "eleanor_epilogue" for her last scene in endings 8 and 10.
/// </summary>
public static class Interlude
{
    private static Game Game => Game.Instance;
    private static GameState State => GameState.Instance;

    public const string First = "interlude1";
    public const string Second = "interlude2";
    public const string Coda = "eleanor_coda";
    public const string Epilogue = "eleanor_epilogue";

    /// <summary>Beat flags of the interludes, cleared when Micah's journal takes the story back.</summary>
    private static readonly string[] FirstBeats =
    {
        "interlude_box_packed", "interlude_safe_locked", "interlude_drawer_locked", "interlude_phoned",
        "interlude_agatha_met", "interlude_agatha_sorry", "interlude_agatha_proud",
    };
    private static readonly string[] SecondBeats = { "interlude_goons_in", "interlude_door_kicked" };

    /// <summary>True while the player is Eleanor (an interlude, the coda, or her epilogue scene).</summary>
    public static bool EleanorPlays(Func<string, bool> has) =>
        has("interlude1") || has("interlude2") || has("eleanor_coda") || has("eleanor_epilogue");

    /// <summary>Eleanor's player sheet for <paramref name="room"/>, or null when Micah (or Daniel) plays there.</summary>
    public static string? PlayerSheet(string room, Func<string, bool> has)
    {
        if (has("eleanor_coda")) return "eleanor_sheet_play";
        if (has("interlude2") && room == "club_backstage") return "eleanor_gown_play";
        if (has("interlude1") || has("interlude2")) return "eleanor_play";
        if (has("eleanor_epilogue") && room == "outskirts") return "eleanor_play";
        return null;
    }

    private static async Task Captions(string title)
    {
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("Chicago, 1927.");
        await Game.Wait(2.8);
        Game.Hud.ShowCaption(title);
        await Game.Wait(2.8);
        Game.Hud.ShowCaption(null);
    }

    /// <summary>Daniel opens the journal in Act 2: the story goes back to the night Eleanor left the Aurelian.</summary>
    public static async Task BeginFirst()
    {
        Attic.StashMicahItems();
        State.SetFlag("interlude1");
        await Captions("First Interlude");
        await Game.ChangeRoom("eleanor_room", "interlude");
    }

    /// <summary>Micah reaches the convent: his journal takes over again, at his office the morning of Act 2.</summary>
    public static async Task EndFirst()
    {
        await Game.Hud.Fade(1, 1.5);
        State.SetFlag("interlude1", false);
        foreach (var flag in FirstBeats) State.SetFlag(flag, false);
        // pick up the 1927 story where the old lead from the Blue Lantern left it
        State.SetFlag("sal_passed");
        State.SetFlag("photo_shown");
        State.SetFlag("club_lead");
        // The office opening leads to the cathedral, then the city map.
        State.SetFlag("act2_church");
        State.SetFlag("on_map");
        Attic.RestoreMicahItems(2);
        Game.Hud.ShowCaption("Chicago, 1927.");
        await Game.Wait(2.8);
        Game.Hud.ShowCaption(null);
        await Game.ChangeRoom("office", "act2");
    }

    /// <summary>Daniel reads on in bed: the pages turn to the motel, the night after Micah left Eleanor there.</summary>
    public static async Task BeginSecond()
    {
        Attic.StashMicahItems();
        State.SetFlag("interlude2");
        await Captions("Second Interlude");
        await Game.ChangeRoom("motel_night", "interlude2");
    }

    /// <summary>The Order's men take Eleanor from the motel to the Club's dressing room.</summary>
    public static async Task Taken()
    {
        await Game.Hud.Fade(1, 0.6);
        await Game.Wait(1.2);
        await Game.ChangeRoom("club_backstage", "interlude2");
    }

    /// <summary>Eleanor goes on stage: Micah's journal picks the night up from the stage, as before.</summary>
    public static async Task EndSecond()
    {
        await Game.Hud.Fade(1, 1.5);
        State.SetFlag("interlude2", false);
        foreach (var flag in SecondBeats) State.SetFlag(flag, false);
        Attic.RestoreMicahItems(3);
        State.SetFlag("masked");
        await Game.ChangeRoom("club_stage", "act3");
    }

    /// <summary>What Eleanor says to an exit her scene hasn't opened.</summary>
    public static string BlockedExitLine(string room) => room switch
    {
        "mansion_bedroom" or "mansion_study" or "mansion_kitchen" or "mansion_cellar" => "Not that way. Not back to him.",
        "club_backstage" => "There's only one door out of here, and it leads to the stage.",
        _ => "Not yet.",
    };

    /// <summary>Eleanor's line when a room has nothing particular for her on <paramref name="target"/>.</summary>
    public static string DefaultLine(string room, string target, Verb verb, bool person, Func<string[], string> pick) =>
        verb switch
        {
            Verb.Look => pick(new[] { "Nothing I haven't seen before.", "I've seen enough of this place already." }),
            Verb.Talk => person ? "Not now." : pick(new[] { "Talking to the furniture. That's what it's come to.", "No answer. Nobody ever answers." }),
            Verb.Kick => person ? "Not with these shoes." : pick(new[] { "That wouldn't help anyone.", "A lady doesn't kick the furniture. Not where anyone can see." }),
            _ => person ? "Better not." : pick(new[] { "Leave it.", "It's not mine to touch.", "Never mind that." }),
        };
}
