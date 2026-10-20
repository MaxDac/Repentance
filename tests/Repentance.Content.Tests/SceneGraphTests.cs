using System.Globalization;
using System.Text.RegularExpressions;
using Xunit;

namespace Repentance.Tests;

/// <summary>
/// Static checks over scenes/rooms/*.tscn and every ChangeRoom call: each transition lands on a real entry marker,
/// every marker and walk target is on the room's floor, and every room can be reached from the attic.
/// </summary>
public class SceneGraphTests
{
    /// <summary>Entries deliberately off the floor: the player is hidden there and teleported before he can move.</summary>
    private static readonly HashSet<string> OffFloorEntries = new();

    private sealed record HotspotDef(string Node, string Id, (float X, float Y)? WalkTo, string ExitTo, string ExitEntry, bool Door);

    private sealed record RoomDef(
        string Name,
        string? Script,
        List<(float X, float Y)>? Floor,
        Dictionary<string, (float X, float Y)?> Entries,
        List<HotspotDef> Hotspots);

    private static readonly Lazy<string> Root = new(() =>
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "project.godot"))) return dir.FullName;
        throw new InvalidOperationException("project.godot not found above the test binaries");
    });

    private static readonly Lazy<Dictionary<string, RoomDef>> Rooms = new(() =>
        Directory.GetFiles(Path.Combine(Root.Value, "scenes", "rooms"), "*.tscn")
            .Select(ParseRoom)
            .ToDictionary(r => r.Name));

    private static readonly Regex NodeHeader = new(@"^\[node name=""([^""]+)""(?:[^\]]*?\bparent=""([^""]*)"")?[^\]]*\]");
    private static readonly Regex Vec = new(@"Vector2\(\s*([-\d.eE]+)\s*,\s*([-\d.eE]+)\s*\)");
    private static readonly Regex ChangeRoomCall = new(@"ChangeRoom\(\s*""([^""]+)""\s*,\s*""([^""]+)""\s*\)");

    private static float F(string s) => float.Parse(s, CultureInfo.InvariantCulture);

    private static RoomDef ParseRoom(string path)
    {
        var text = File.ReadAllText(path).Replace("\r\n", "\n");
        string? rootScript = null;
        var scripts = Regex.Matches(text, @"\[ext_resource type=""Script"" path=""res://([^""]+)"" id=""([^""]+)""\]")
            .ToDictionary(m => m.Groups[2].Value, m => m.Groups[1].Value);
        List<(float, float)>? floor = null;
        var entries = new Dictionary<string, (float, float)?>();
        var hotspots = new List<HotspotDef>();
        foreach (var block in Regex.Split(text, @"\n(?=\[node )"))
        {
            var header = NodeHeader.Match(block);
            if (!header.Success) continue;
            string name = header.Groups[1].Value, parent = header.Groups[2].Value;
            string? Prop(string key) =>
                Regex.Match(block, $@"\n{key} = (.+)") is { Success: true } m ? m.Groups[1].Value.Trim() : null;
            if (!header.Groups[2].Success)
            {
                if (Prop("script") is { } s && Regex.Match(s, @"ExtResource\(""([^""]+)""\)") is { Success: true } sm)
                    rootScript = scripts.GetValueOrDefault(sm.Groups[1].Value);
                continue;
            }
            if (name == "WalkArea" && parent == "." && Prop("polygon") is { } poly)
            {
                var args = Regex.Match(poly, @"\(([^)]*)\)").Groups[1].Value;
                var nums = args.Split(',', StringSplitOptions.RemoveEmptyEntries).Select(s => F(s.Trim())).ToArray();
                floor = Enumerable.Range(0, nums.Length / 2).Select(i => (nums[2 * i], nums[2 * i + 1])).ToList();
            }
            else if (parent == "Entries")
            {
                entries[name] = Prop("position") is { } pos && Vec.Match(pos) is { Success: true } v
                    ? (F(v.Groups[1].Value), F(v.Groups[2].Value)) : null;
            }
            if (Prop("Id") is { } id)
            {
                (float, float)? walkTo = Prop("WalkTo") is { } w && Vec.Match(w) is { Success: true } wv
                    ? (F(wv.Groups[1].Value), F(wv.Groups[2].Value)) : null;
                hotspots.Add(new HotspotDef(name, id.Trim('"'), walkTo,
                    Prop("ExitTo")?.Trim('"') ?? "", Prop("ExitEntry")?.Trim('"') ?? "", Prop("Door") == "true"));
            }
        }
        return new RoomDef(Path.GetFileNameWithoutExtension(path), rootScript, floor, entries, hotspots);
    }

    /// <summary>(file relative to the repo, room, entry) for every literal ChangeRoom("room", "entry") call.</summary>
    private static IEnumerable<(string File, string Room, string Entry)> ChangeRoomCalls() =>
        SourceFiles.All(Root.Value).SelectMany(f => ChangeRoomCalls(f));

    private static IEnumerable<(string File, string Room, string Entry)> ChangeRoomCalls(string file)
    {
        var rel = Path.GetRelativePath(Root.Value, file).Replace('\\', '/');
        return ChangeRoomCall.Matches(File.ReadAllText(file)).Select(m => (rel, m.Groups[1].Value, m.Groups[2].Value));
    }

    private static bool OnFloor(List<(float X, float Y)> poly, (float X, float Y) p)
    {
        bool inside = false;
        for (int i = 0, j = poly.Count - 1; i < poly.Count; j = i++)
        {
            var (xi, yi) = poly[i];
            var (xj, yj) = poly[j];
            if ((yi > p.Y) != (yj > p.Y) && p.X < (xj - xi) * (p.Y - yi) / (yj - yi) + xi) inside = !inside;
        }
        return inside;
    }

    [Fact]
    public void RoomScenes_AreFound() => Assert.True(Rooms.Value.Count > 20, $"only {Rooms.Value.Count} room scenes parsed");

    [Fact]
    public void EveryRoomHasEntries() =>
        Assert.Empty(Rooms.Value.Values.Where(r => r.Entries.Count == 0).Select(r => r.Name));

    [Fact]
    public void SceneExits_LeadToExistingEntries()
    {
        var problems = new List<string>();
        foreach (var room in Rooms.Value.Values)
        foreach (var h in room.Hotspots.Where(h => h.ExitTo != ""))
        {
            if (!Rooms.Value.TryGetValue(h.ExitTo, out var target))
                problems.Add($"{room.Name}/{h.Id} exits to missing room '{h.ExitTo}'");
            else if (!target.Entries.ContainsKey(h.ExitEntry))
                problems.Add($"{room.Name}/{h.Id} exits to {h.ExitTo} entry '{h.ExitEntry}', which has no marker");
        }
        Assert.Empty(problems);
    }

    [Fact]
    public void DoorHotspots_LeadToAnotherRoom()
    {
        var doors = Rooms.Value.Values.SelectMany(r => r.Hotspots.Where(h => h.Door).Select(h => (Room: r, Hotspot: h))).ToList();
        Assert.True(doors.Count > 20, $"only {doors.Count} door hotspots found");
        var problems = new List<string>();
        foreach (var (room, h) in doors)
        {
            if (h.ExitTo != "") continue;
            var script = room.Script is { } s ? File.ReadAllText(Path.Combine(Root.Value, s)) : "";
            if (!script.Contains($"\"{h.Id}\"") || !script.Contains("ChangeRoom("))
                problems.Add($"{room.Name}/{h.Id} is a Door but neither exits nor is handled by a room script that changes room");
        }
        Assert.Empty(problems);
    }

    [Fact]
    public void ChangeRoomCalls_LeadToExistingEntries()
    {
        var calls = ChangeRoomCalls().ToList();
        Assert.True(calls.Count > 50, $"only {calls.Count} ChangeRoom calls found");
        var problems = new List<string>();
        foreach (var (file, roomName, entry) in calls)
        {
            if (!Rooms.Value.TryGetValue(roomName, out var room)) problems.Add($"{file}: ChangeRoom to missing room '{roomName}'");
            else if (!room.Entries.ContainsKey(entry)) problems.Add($"{file}: {roomName} has no entry marker '{entry}'");
        }
        Assert.Empty(problems);
    }

    [Fact]
    public void EntryMarkers_StandOnTheFloor()
    {
        var problems = new List<string>();
        foreach (var room in Rooms.Value.Values.Where(r => r.Floor != null))
        foreach (var (name, pos) in room.Entries)
        {
            var key = $"{room.Name}/{name}";
            if (pos is not { } p) problems.Add($"{key} has no position");
            else if (!OnFloor(room.Floor!, p) && !OffFloorEntries.Contains(key)) problems.Add($"{key} {p} is off the walk area");
        }
        Assert.Empty(problems);
    }

    [Fact]
    public void OffFloorAllowlist_IsStillNeeded()
    {
        foreach (var key in OffFloorEntries)
        {
            var parts = key.Split('/');
            var room = Rooms.Value[parts[0]];
            Assert.True(room.Entries.TryGetValue(parts[1], out var pos) && pos is { } p && !OnFloor(room.Floor!, p),
                $"{key} is back on the floor; drop it from the allowlist");
        }
    }

    [Fact]
    public void ExplicitWalkTargets_StandOnTheFloor()
    {
        var problems = Rooms.Value.Values
            .Where(r => r.Floor != null)
            .SelectMany(r => r.Hotspots
                .Where(h => h.WalkTo is { } w && (w.X != 0 || w.Y != 0) && !OnFloor(r.Floor!, w))
                .Select(h => $"{r.Name}/{h.Node} ({h.Id}) WalkTo {h.WalkTo} is off the walk area"))
            .ToList();
        Assert.Empty(problems);
    }

    /// <summary>
    /// Hotspots without ExitTo whose way out the room script runs. Where a cutscene leaves the room on its own, the
    /// hotspot is the failsafe for when it stops short (an error in <c>Game.Run</c> hands control back mid-scene), and
    /// calls the same method the cutscene ends with.
    /// </summary>
    private static readonly (string Room, string Hotspot)[] ScriptedExits =
    {
        ("alley", "street"), ("church_exterior", "doors"), ("club_backstage", "door"), ("club_hall", "street_door"),
        ("club_stage", "lounge_exit"), ("club_vestibule", "inner_door"), ("convent_road", "road"),
        ("harrington_office", "window"), ("mansion_exterior", "gate"), ("motel_fire_escape", "ladder"),
        ("motel_fire_escape", "door"), ("motel_night", "door"), ("office", "door"), ("rose_house", "exit"),
        ("street", "street"),
    };

    /// <summary>Rooms with no hotspot out, and why that is fine.</summary>
    private static readonly Dictionary<string, string> NoManualExit = new()
    {
        ["attic"] = "Daniel's attic: the journal and the hatch scenes move the story on, and Micah and Eleanor never stand here",
        ["bedroom"] = "Daniel's bedroom: reading on in bed is the way out, and Micah and Eleanor never stand here",
        ["chicago_map"] = "the map is itself the way out: every pin changes room",
        ["prison"] = "an ending: the credits follow",
    };

    [Fact]
    public void ScriptedExits_AreHandledByTheRoomScript()
    {
        var problems = new List<string>();
        foreach (var (roomName, id) in ScriptedExits)
        {
            if (!Rooms.Value.TryGetValue(roomName, out var room)) { problems.Add($"{roomName}: no such room"); continue; }
            if (room.Hotspots.All(h => h.Id != id)) problems.Add($"{roomName}: no hotspot '{id}'");
            var script = room.Script is { } s ? File.ReadAllText(Path.Combine(Root.Value, s)) : "";
            if (!script.Contains($"\"{id}\"")) problems.Add($"{roomName}: script does not handle '{id}'");
        }
        Assert.Empty(problems);
    }

    [Fact]
    public void EveryRoom_HasAWayOut()
    {
        var scripted = ScriptedExits.Select(m => m.Room).ToHashSet();
        var stuck = Rooms.Value.Values
            .Where(r => !r.Hotspots.Any(h => h.ExitTo != "" || h.Door) && !scripted.Contains(r.Name) && !NoManualExit.ContainsKey(r.Name))
            .Select(r => r.Name)
            .OrderBy(n => n);
        Assert.Empty(stuck);
        foreach (var name in NoManualExit.Keys)
            Assert.True(Rooms.Value.TryGetValue(name, out var room) && !room.Hotspots.Any(h => h.ExitTo != "" || h.Door),
                $"{name} has a way out now; drop it from {nameof(NoManualExit)}");
    }

    [Fact]
    public void EveryRoom_IsReachableFromTheAttic()
    {
        var rooms = Rooms.Value;
        var byScript = rooms.Values.Where(r => r.Script != null).GroupBy(r => r.Script!).ToDictionary(g => g.Key, g => g.Select(r => r.Name).ToList());
        var edges = rooms.Keys.ToDictionary(k => k, _ => new HashSet<string>());
        var global = new HashSet<string>();
        foreach (var room in rooms.Values)
        foreach (var h in room.Hotspots.Where(h => h.ExitTo != ""))
            edges[room.Name].Add(h.ExitTo);
        foreach (var file in SourceFiles.Game(Root.Value))
        {
            var rel = Path.GetRelativePath(Root.Value, file).Replace('\\', '/');
            var targets = ChangeRoomCalls(file).Select(c => c.Room).ToList();
            if (byScript.TryGetValue(rel, out var sources))
                foreach (var s in sources) edges[s].UnionWith(targets);
            else
                global.UnionWith(targets); // shared helpers (Act3, Game) can be called from anywhere in the story
        }

        var seen = new HashSet<string> { "attic" };
        var queue = new Queue<string>(seen);
        bool addedGlobal = false;
        while (queue.Count > 0 || !addedGlobal)
        {
            if (queue.Count == 0)
            {
                addedGlobal = true;
                foreach (var g in global.Where(seen.Add)) queue.Enqueue(g);
                continue;
            }
            foreach (var next in edges.GetValueOrDefault(queue.Dequeue()) ?? new HashSet<string>())
                if (rooms.ContainsKey(next) && seen.Add(next)) queue.Enqueue(next);
        }
        Assert.Empty(rooms.Keys.Except(seen).OrderBy(k => k));
    }
}
