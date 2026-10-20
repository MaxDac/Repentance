using System;
using System.Threading.Tasks;
using Repentance.Rooms;

namespace Repentance.Story;

/// <summary>
/// The two Eleanor interludes (the start of Act 2 and of Act 3) and her coda in the mansion: who the player is, the
/// hand-offs in and out of Micah's journal, and the lines she says where a room has nothing special for her.
/// Flags: "interlude1" / "interlude2" while an interlude plays, "eleanor_coda" in the mansion after the prayer,
/// "eleanor_epilogue" for her last scene in ending 8.
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
        "interlude_closet_open", "interlude_box_in_safe", "interlude_riddle_written",
        "interlude_riddle_in_drawer",
        "interlude_agatha_met", "interlude_agatha_sorry", "interlude_agatha_proud",
        "interlude_took_box", "interlude_took_scrap", "interlude_took_thread",
        "interlude_took_bag", "interlude_bag_left", "interlude_pyjamas",
    };
    private static readonly string[] SecondBeats =
    {
        "interlude_goons_in", "interlude_took_makeup", "interlude_took_puff", "interlude_took_pin",
        "interlude_powdered", "interlude_lips", "interlude_made_up", "interlude_door_kicked",
        "backstage_door_ajar", "backstage_door_open",
    };

    /// <summary>True while the player is Eleanor (an interlude, the coda, or her epilogue scene).</summary>
    public static bool EleanorPlays(Func<string, bool> has) =>
        has("interlude1") || has("interlude2") || has("eleanor_coda") || has("eleanor_epilogue");

    /// <summary>
    /// True while Eleanor carries her own satchel: only during the two interludes, for the things she picks up there
    /// (puzzles 17 and 18). Her coda and epilogue keep her empty-handed.
    /// </summary>
    public static bool SatchelOpen(Func<string, bool> has) => has("interlude1") || has("interlude2");

    /// <summary>
    /// Eleanor's player sheet for <paramref name="room"/>, or null when Micah (or Daniel) plays there. In the First
    /// Interlude she carries her duffle (<see cref="EleanorBag"/>) from Room 507 to the convent cell, and is in her
    /// pyjamas in the cell when Agatha knocks.
    /// </summary>
    public static string? PlayerSheet(string room, Func<string, bool> has)
    {
        if (has("eleanor_coda")) return "eleanor_sheet_play";
        if (has("interlude2") && room == "club_backstage") return "eleanor_gown_play";
        if (has("interlude1") && room == "convent_cell" && has("interlude_pyjamas")) return "eleanor_pyjama_play";
        if (has("interlude1") && !has("interlude_bag_left")
            && (room is "speakeasy" or "convent_corridor" or "convent_cell" || (room == "eleanor_room" && has("interlude_took_bag"))))
            return EleanorBag.Sheet;
        if (has("interlude1") || has("interlude2")) return "eleanor_play";
        if (has("eleanor_epilogue") && room == "outskirts") return "eleanor_play";
        return null;
    }

    /// <summary>Over black: "Chicago, 1927." alone, then the interlude's title under it on the same screen.</summary>
    private static async Task Captions(string title)
    {
        await Game.Hud.Fade(1, 1.5);
        Game.Hud.ShowCaption("Chicago, 1927.");
        await Game.Wait(2.5);
        Game.Hud.ShowCaptionSub(title);
        await Game.Wait(2.5);
        Game.Hud.ShowCaption(null);
    }

    /// <summary>Nothing Eleanor picked up in an interlude goes back into Micah's satchel (his own was stashed on the way in).</summary>
    private static void DropEleanorItems()
    {
        foreach (var id in System.Linq.Enumerable.ToList(State.Inventory)) State.TakeItem(id);
    }

    /// <summary>Daniel opens the journal in Act 2: the story goes back to the night Eleanor left the Aurelian.</summary>
    public static async Task BeginFirst()
    {
        Attic.StashMicahItems();
        State.SetFlag("interlude1");
        await Captions("First Interlude");
        await Game.ChangeRoom("eleanor_room", "interlude");
    }

    /// <summary>
    /// Eleanor sees Micah climb the fire escape and steps out to wait for him: over black, his journal takes over again
    /// on the landing, where Act 1 left them (<see cref="MotelFireEscape"/>), then their night in her motel room.
    /// </summary>
    public static async Task EndFirst()
    {
        await Game.Hud.Fade(1, 3.0);
        State.SetFlag("interlude1", false);
        foreach (var flag in FirstBeats) State.SetFlag(flag, false);
        DropEleanorItems();
        // pick up the 1927 story where the old lead from the Blue Lantern left it
        State.SetFlag("sal_passed");
        State.SetFlag("photo_shown");
        State.SetFlag("club_lead");
        // The office opening leads to the motel return, then the cathedral, then the city map.
        State.SetFlag("act2_church");
        State.SetFlag("on_map");
        Attic.RestoreMicahItems(2);
        await Game.Wait(1.0);
        await Game.ChangeRoom("motel_fire_escape", "interlude1", fadeInSeconds: 1.5);
    }

    /// <summary>Daniel reads on in bed: the pages turn to the motel, the same night, after Micah left Eleanor there.</summary>
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
        DropEleanorItems();
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
            Verb.UseItem => person ? "That's mine. Not theirs." : pick(new[] { "That's not where it goes.", "No. That won't do it." }),
            _ => person ? "Better not." : pick(new[] { "Leave it.", "It's not mine to touch.", "Never mind that." }),
        };
}
