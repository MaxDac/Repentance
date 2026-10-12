using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

public readonly record struct GridPoint(int X, int Y);

public static class PuzzleRules
{
    public static bool Lift(IReadOnlyList<int> switches) =>
        switches.Count == 3 && switches[0] == 1 && switches[1] == 0 && switches[2] == 0;

    public static string LiftDestination(IReadOnlyList<int> switches) =>
        switches.Count != 3 ? "Invalid route" :
        switches[0] != 1 ? "A: laundry" :
        switches[1] != 0 ? "B: kitchen" :
        switches[2] != 0 ? "C: roof" : "5th floor: linen";

    public static bool Safe(IReadOnlyList<int> directions, IReadOnlyList<int> numbers) =>
        directions.SequenceEqual(new[] { 0, 1, 0 }) && numbers.SequenceEqual(new[] { 12, 31, 7 });

    public static bool Crests(IReadOnlyList<int> symbols) => symbols.SequenceEqual(new[] { 2, 0, 1 });
    public static bool Catalogue(int motif, int entry) => motif == 1 && entry == 2;
    public static bool Cipher(IReadOnlyList<int> fragments) => fragments.SequenceEqual(new[] { 1, 2, 0 });
    public static bool Bell(IReadOnlyList<int> steps) => steps.SequenceEqual(new[] { 0, 1, 2 });
    public static bool CipherReady(bool bookRead, bool warmed, bool reflected) => bookRead && warmed && reflected;
    public static bool Pair(string first, string second, string a, string b) =>
        (first == a && second == b) || (first == b && second == a);

    public static IReadOnlyList<GridPoint> AccountMarks { get; } =
        Array.AsReadOnly(new[] { new GridPoint(6, 3), new GridPoint(6, 5), new GridPoint(3, 3) });
    public static IReadOnlyList<GridPoint> TracingMarks { get; } =
        Array.AsReadOnly(new[] { new GridPoint(0, 0), new GridPoint(2, 0), new GridPoint(0, 3) });

    public static GridPoint Transform(GridPoint p, int rotation, int x, int y)
    {
        var turned = rotation switch
        {
            0 => p,
            1 => new GridPoint(-p.Y, p.X),
            2 => new GridPoint(-p.X, -p.Y),
            3 => new GridPoint(p.Y, -p.X),
            _ => throw new ArgumentOutOfRangeException(nameof(rotation)),
        };
        return new GridPoint(turned.X + x, turned.Y + y);
    }

    public static bool Alignment(int rotation, int x, int y) =>
        rotation is >= 0 and < 4 && x is >= 0 and <= 10 && y is >= 0 and <= 10 &&
        TracingMarks.Select(p => Transform(p, rotation, x, y)).SequenceEqual(AccountMarks);
}

public static class PuzzleMigration
{
    public const string SchemaFlag = "puzzles_v1";
    public const string Act3SchemaFlag = "puzzles_act3_v1";

    public static void Normalize(SaveData data)
    {
        NormalizeAct3(data);
        if (data.Flags.Contains(SchemaFlag)) return;
        var flags = new HashSet<string>(data.Flags, StringComparer.Ordinal);
        bool Has(string item) => data.Inventory.Contains(item) || flags.Contains("stash_" + item);
        if (flags.Contains("trunk_open") || Has("journal")) flags.Add("tool_tin_found");
        if (data.Room == "eleanor_room" || flags.Contains("seen_eleanor_room") ||
            flags.Contains("eleanor_drawer_open") || flags.Contains("safe_open") || Has("brass_box") ||
            Has("card") || data.StoryAct >= 2)
            flags.Add("lift_routed");
        if (Has("mirror") || flags.Contains("got_mirror"))
        {
            flags.Add("took_mirror");
            flags.Add("got_mirror");
        }
        if (flags.Contains("read_book") || flags.Contains("club_unlocked") || Has("address"))
        {
            flags.UnionWith(new[] { "read_book", "card_warmed", "card_reflected", "card_decoded", "club_unlocked" });
            if (!Has("address"))
            {
                if (Has("journal")) flags.Add("stash_address");
                else data.Inventory.Add("address");
            }
        }
        else if (!Has("card") && !Has("brass_box") && (data.StoryAct == 2 ||
            flags.Contains("sal_passed") || flags.Contains("nun_talked") ||
            data.Room is "speakeasy" or "alley" or "convent_corridor" or "convent_cell" or "convent_road" or "motel_night"))
        {
            flags.Add("recover_hotel");
            flags.Add("staff_elevator");
        }
        if (flags.Contains("library_banned") || Has("book")) flags.Add("catalogue_identified");
        if (data.Room == "harrington_office" || flags.Contains("seen_harrington_office") ||
            flags.Contains("harrington_done")) flags.Add("ladder_freed");
        if (flags.Contains("secret_open") || flags.Contains("took_mask") || Has("mask"))
            flags.Add("harrington_closet_open");
        flags.Add(SchemaFlag);
        data.Flags = flags.OrderBy(f => f, StringComparer.Ordinal).ToList();
    }

    private static void NormalizeAct3(SaveData data)
    {
        if (data.Flags.Contains(Act3SchemaFlag)) return;
        var flags = new HashSet<string>(data.Flags, StringComparer.Ordinal);
        bool Has(string item) => data.Inventory.Contains(item) || flags.Contains("stash_" + item);
        if (flags.Contains("door_open") || flags.Contains("bell_wedged") ||
            flags.Contains("seen_mansion_kitchen") || flags.Contains("entered_bedroom") || flags.Contains("escaping") ||
            data.Room is "mansion_kitchen" or "mansion_study" or "mansion_bedroom")
            flags.UnionWith(new[] { "alarm_noticed", "bin_moved", "bell_wedged" });
        if (flags.Contains(Endings.TookDocuments) || Has("documents"))
            flags.UnionWith(new[] { Endings.TookDocuments, "audit_identified", "audit_folder_taken" });
        flags.Add(Act3SchemaFlag);
        data.Flags = flags.OrderBy(f => f, StringComparer.Ordinal).ToList();
    }
}
