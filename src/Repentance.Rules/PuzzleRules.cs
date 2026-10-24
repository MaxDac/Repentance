using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

public readonly record struct GridPoint(int X, int Y);

/// <summary>
/// The Aurelian's service cage, as a maze of shafts and chutes. Columns are the room numbers along a floor
/// (01 west to 13 east), rows the floors (5th at the top, the basement loading bay at the bottom).
/// </summary>
public static class LiftMaze
{
    public const int Width = 13, Height = 8;

    // '#' are walls; cells sit on odd rows/columns, gaps between them are open passages.
    private static readonly string[] Grid =
    {
        "###########################",
        "# #       #   # #         #",
        "# # ##### # # # # ### ### #",
        "#       # # #   #   #   # #",
        "# ####### # # ##### ### ###",
        "#   #     # # #   #   #   #",
        "##### ##### ##### # ##### #",
        "#   #     #     #   #     #",
        "# # ##### # # # ##### #####",
        "# #   #   # # #   #   #   #",
        "# ### # ##### ### # ### # #",
        "#   #   #     #   #     # #",
        "### ### # # ### ######### #",
        "#     #   # #   #       # #",
        "##### ##### ##### ### ### #",
        "#     #           #       #",
        "###########################",
    };

    public static GridPoint Start { get; } = new(0, Height - 1);
    /// <summary>The fifth-floor linen room, right next to 507.</summary>
    public static GridPoint Target { get; } = new(7, 2);
    /// <summary>Linen rooms that look exactly like the right one, two of them stacked right above and below it.</summary>
    public static IReadOnlyList<GridPoint> Decoys { get; } =
        Array.AsReadOnly(new[]
        {
            new GridPoint(7, 1), new GridPoint(7, 3), new GridPoint(3, 2), new GridPoint(11, 2), new GridPoint(1, 0),
        });
    public static string FloorName(int row) => row == Height - 1 ? "B" : (Height - 1 - row).ToString();

    public static bool IsLinen(GridPoint p) => p == Target || Decoys.Contains(p);

    public static bool CanMove(GridPoint from, int dx, int dy)
    {
        if (Math.Abs(dx) + Math.Abs(dy) != 1) return false;
        int x = from.X + dx, y = from.Y + dy;
        if (from.X is < 0 or >= Width || from.Y is < 0 or >= Height || x is < 0 or >= Width || y is < 0 or >= Height) return false;
        return Grid[2 * from.Y + 1 + dy][2 * from.X + 1 + dx] != '#';
    }

    public static GridPoint Move(GridPoint from, int dx, int dy) =>
        CanMove(from, dx, dy) ? new GridPoint(from.X + dx, from.Y + dy) : from;

    public static bool Solved(GridPoint p) => p == Target;

    public static string Destination(GridPoint p)
    {
        if (p == Target) return "5th floor: linen room by 507";
        if (IsLinen(p)) return $"{(p.Y == Height - 1 ? "basement" : FloorName(p.Y) + Ordinal(Height - 1 - p.Y))} floor: linen room by {FloorName(p.Y)}{p.X:D2}";
        return p == Start ? "the loading bay" : "a blank wall between floors";
    }

    private static string Ordinal(int n) => n switch { 1 => "st", 2 => "nd", 3 => "rd", _ => "th" };

    private static readonly (string Id, int Dx, int Dy)[] Steps = { ("up", 0, -1), ("down", 0, 1), ("left", -1, 0), ("right", 1, 0) };

    public static (int Dx, int Dy) Step(string id)
    {
        foreach (var s in Steps) if (s.Id == id) return (s.Dx, s.Dy);
        throw new ArgumentException($"No lift direction '{id}'.", nameof(id));
    }

    /// <summary>Shortest sequence of "up"/"down"/"left"/"right" moves between two cells, or null if walled off.</summary>
    public static IReadOnlyList<string>? Route(GridPoint from, GridPoint to)
    {
        var previous = new Dictionary<GridPoint, (GridPoint From, string Step)?> { [from] = null };
        var queue = new Queue<GridPoint>();
        queue.Enqueue(from);
        while (queue.Count > 0)
        {
            var p = queue.Dequeue();
            if (p == to) break;
            foreach (var (id, dx, dy) in Steps)
            {
                if (!CanMove(p, dx, dy)) continue;
                var next = new GridPoint(p.X + dx, p.Y + dy);
                if (previous.ContainsKey(next)) continue;
                previous[next] = (p, id);
                queue.Enqueue(next);
            }
        }
        if (!previous.ContainsKey(to)) return null;
        var route = new List<string>();
        for (var step = previous[to]; step is { } s; step = previous[s.From]) route.Add(s.Step);
        route.Reverse();
        return route;
    }

    public static IEnumerable<GridPoint> Cells()
    {
        for (int y = 0; y < Height; y++)
            for (int x = 0; x < Width; x++)
                yield return new GridPoint(x, y);
    }
}

public static class PuzzleRules
{
    public static bool Safe(IReadOnlyList<int> directions, IReadOnlyList<int> numbers) =>
        SafeTumblers(directions, numbers) == 3 && directions.Count == 3 && numbers.Count == 3;

    /// <summary>How many stops, in order from the first, are set right: each one drops a tumbler you can hear.</summary>
    public static int SafeTumblers(IReadOnlyList<int> directions, IReadOnlyList<int> numbers)
    {
        int[] wantDirections = { 0, 1, 0 }, wantNumbers = { 12, 40, 7 };
        if (directions.Count != 3 || numbers.Count != 3) return 0;
        int clicks = 0;
        while (clicks < 3 && directions[clicks] == wantDirections[clicks] && numbers[clicks] == wantNumbers[clicks]) clicks++;
        return clicks;
    }

    public static bool Crests(IReadOnlyList<int> symbols) => symbols.SequenceEqual(new[] { 2, 0, 1 });
    public static bool Catalogue(int motif, int entry) => motif == 1 && entry == 2;
    public static bool Cipher(IReadOnlyList<int> fragments) => fragments.SequenceEqual(new[] { 1, 2, 0 });
    public static bool Bell(IReadOnlyList<int> steps) => steps.SequenceEqual(new[] { 0, 1, 2 });
    public static bool CipherReady(bool bookRead, bool warmed, bool reflected) => bookRead && warmed && reflected;
    public static bool Pair(string first, string second, string a, string b) =>
        (first == a && second == b) || (first == b && second == a);

    /// <summary>The register page: unlabelled account dots, two of which hold the whole index figure.</summary>
    public static IReadOnlyList<GridPoint> AccountMarks { get; } = Array.AsReadOnly(new[]
    {
        new GridPoint(0, 6), new GridPoint(5, 6), new GridPoint(6, 5), new GridPoint(6, 7), new GridPoint(6, 8),
        new GridPoint(6, 9), new GridPoint(7, 5), new GridPoint(7, 6), new GridPoint(8, 5), new GridPoint(8, 7),
        new GridPoint(8, 9), new GridPoint(9, 6), new GridPoint(9, 7), new GridPoint(10, 5), new GridPoint(10, 7),
    });

    /// <summary>The index's punched holes: BANK, JUDGE, CAPTAIN, then two blank holes.</summary>
    public static IReadOnlyList<GridPoint> TracingMarks { get; } = Array.AsReadOnly(new[]
    {
        new GridPoint(3, 3), new GridPoint(0, 0), new GridPoint(2, 2), new GridPoint(1, 3), new GridPoint(2, 4),
    });

    public const int Bank = 0, Judge = 1, Captain = 2;

    /// <summary>Turns the index over (mirrored left to right) when flipped, then a quarter-turn per rotation, then slides it.</summary>
    public static GridPoint Transform(GridPoint p, int rotation, bool flipped, int x, int y)
    {
        if (flipped) p = new GridPoint(-p.X, p.Y);
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

    private static bool InRange(int rotation, int x, int y) =>
        rotation is >= 0 and < 4 && x is >= 0 and <= 10 && y is >= 0 and <= 10;

    /// <summary>Every hole of the index sits on an account dot, whatever the labels say.</summary>
    public static bool AlignmentFits(int rotation, bool flipped, int x, int y) =>
        InRange(rotation, x, y) && TracingMarks.All(p => AccountMarks.Contains(Transform(p, rotation, flipped, x, y)));

    /// <summary>The note: BANK above JUDGE, CAPTAIN left of BANK.</summary>
    public static bool AlignmentReadsAsNote(int rotation, bool flipped, int x, int y)
    {
        GridPoint Mark(int i) => Transform(TracingMarks[i], rotation, flipped, x, y);
        return Mark(Bank).Y < Mark(Judge).Y && Mark(Captain).X < Mark(Bank).X;
    }

    public static bool Alignment(int rotation, bool flipped, int x, int y) =>
        AlignmentFits(rotation, flipped, x, y) && AlignmentReadsAsNote(rotation, flipped, x, y);
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
