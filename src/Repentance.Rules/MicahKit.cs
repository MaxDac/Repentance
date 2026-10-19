using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>
/// What Micah carries: the items pinned to the front of his satchel for the whole story, the 1927 items each act
/// lets him keep when the journal picks up again, and what a debug start in a given room hands him.
/// </summary>
public static class MicahKit
{
    public const string LighterId = "lighter";

    /// <summary>Micah's own things, always in these first slots and never stashed; present-day Daniel carries none.</summary>
    public static readonly IReadOnlyList<string> Pinned = new[] { Notes.ItemId, LighterId };

    public static bool IsPinned(string id) => Pinned.Contains(id);

    // Act 1 leaves the case kit; the clues (photo, cash, matchbook) stay behind with the notepad holding what they said.
    // Eleanor's cloth rides along until Micah gives up on her (ending 1).
    private static readonly string[] Act2Keep = { "revolver", "lockpick", "card", "mirror", "cloth", "faith_ring", "cross" };
    // Act 3 is the gun, Eleanor's cloth and the two commitments the endings weigh.
    private static readonly string[] Act3Keep = { "revolver", "cloth", "faith_ring", "cross" };

    /// <summary>Stashed items that come back when <paramref name="act"/> starts; anything else stays in the past.</summary>
    public static IReadOnlyList<string> ActKeep(int act) => act switch
    {
        2 => Act2Keep,
        3 => Act3Keep,
        _ => Array.Empty<string>(),
    };

    public static bool KeptInAct(int act, string id) => ActKeep(act).Contains(id);

    private static readonly string[] Act2Rooms =
    {
        "church_exterior", "church_interior", "chicago_map", "library", "club_hall", "street", "rose_house",
        "newspaper_morgue", "harrington_road", "harrington_office", "club_vestibule", "club_lounge",
        "club_stage",
    };

    private static readonly string[] Act3Rooms =
    {
        "office_storm", "mansion_exterior", "mansion_kitchen", "mansion_cellar", "mansion_study", "mansion_bedroom",
        "outskirts", "prison",
    };

    // Micah's kit in his office (cash on the desk, revolver on the coat rack, picks in the cabinet), taken before he can leave in Act 1.
    private static readonly (string Item, string Flag)[] OfficeDrawer =
    {
        ("dollar", "took_dollar"), ("revolver", "took_revolver"), ("lockpick", "took_lockpick"),
    };

    /// <summary>The act a debug start in <paramref name="room"/> belongs to; 0 for the present day and unknown rooms.</summary>
    public static int DebugAct(string room) =>
        Act3Rooms.Contains(room) ? 3
        : Act2Rooms.Contains(room) ? 2
        : Notes.DebugRooms.Contains(room) ? 1
        : 0;

    /// <summary>
    /// Items a debug start in <paramref name="room"/> receives: the office drawer and Teddy's photo for 1927 rooms
    /// past the office in Act 1, the act's kit for Acts 2 and 3. Pinned items are added on entry for Micah.
    /// </summary>
    public static IReadOnlyList<string> DebugItems(string room) => DebugAct(room) switch
    {
        1 when room != "office" => OfficeDrawer.Select(d => d.Item).Prepend("photo").ToList(),
        2 => Act2Keep.Where(i => i is not ("faith_ring" or "cross")).ToList(),
        3 => Act3Keep.Where(i => i is not ("faith_ring" or "cross")).ToList(),
        _ => Array.Empty<string>(),
    };

    /// <summary>Flags that go with <see cref="DebugItems"/>, so the office drawer isn't refilled behind Micah.</summary>
    public static IReadOnlyList<string> DebugFlags(string room) =>
        DebugAct(room) >= 1 && room != "office" ? OfficeDrawer.Select(d => d.Flag).ToList() : Array.Empty<string>();

    /// <summary>
    /// The story act a debug start inside an interlude belongs to, whatever its room: 2 for the first, 3 for the
    /// second, 0 outside them.
    /// </summary>
    public static int InterludeAct(Func<string, bool> has) => has("interlude1") ? 2 : has("interlude2") ? 3 : 0;

    /// <summary>Micah's kit a debug start in an interlude stashes, for him to get back when Eleanor's part ends.</summary>
    public static IReadOnlyList<string> InterludeKit(int act) =>
        ActKeep(act).Where(i => i is not ("faith_ring" or "cross")).ToList();
}
