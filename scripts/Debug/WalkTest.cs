using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Movement test: in every room the player can walk, every entry marker stands on the floor, every hotspot
/// and exit can be reached from every entry without crossing a wall, the player really walks there, and every
/// exit leads to an existing entry. Then the real mouse path: floor clicks, clicks off the floor, interrupting
/// a walk, clicks ignored while busy, facing in all four directions and exits taken by clicking.
/// Prints WALK TEST OK / WALK TEST FAILED. Run with: godot -- --walk-test [--clock=fast|normal]
/// </summary>
public class WalkTest
{
    /// <summary>Entries deliberately off the floor (the player is hidden there and teleported before he can move).</summary>
    private static readonly HashSet<string> OffFloorEntries = new();
    private const float Tolerance = 1.5f;

    private Game _game = null!;
    private readonly List<string> _failures = new();
    private int _checks;

    public async Task Run(Game game)
    {
        _game = game;
        if (!AutoPlay.ApplyClock(out var clockError))
        {
            GD.Print("WALK TEST FAILED:\n  " + clockError);
            game.GetTree().Quit(1);
            return;
        }
        game.AutosaveEnabled = false;
        game.SkipRoomEnter = true;
        SaveSystem.Directory = "user://autoplay_saves/walk_test";
        GameState.Instance.Reset();
        // Sal stops Micah at the speakeasy curtain and starts a conversation; the test walks past him
        GameState.Instance.SetFlag("sal_passed");
        try
        {
            var rooms = RoomNames();
            Check(rooms.Count > 20, $"found {rooms.Count} room scenes");
            foreach (var room in rooms) await TestRoom(room);
            await InputTests();
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        GD.Print($"[walk] {_checks} checks");
        GD.Print(_failures.Count == 0 ? "WALK TEST OK" : "WALK TEST FAILED:\n  " + string.Join("\n  ", _failures));
        game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    private static List<string> RoomNames() => DirAccess.GetFilesAt("res://scenes/rooms")
        .Select(f => f.EndsWith(".remap") ? f[..^".remap".Length] : f)
        .Where(f => f.EndsWith(".tscn"))
        .Select(f => f[..^".tscn".Length])
        .Distinct()
        .OrderBy(f => f, StringComparer.Ordinal)
        .ToList();

    // ------------------------------------------------------------------ every room

    private async Task TestRoom(string name)
    {
        // an unknown entry name falls back to the first marker
        await _game.ChangeRoom(name, "__first__");
        var room = _game.Room!;
        if (!room.ShowPlayer)
        {
            GD.Print($"[walk] {name}: player not shown, skipped");
            return;
        }
        var walk = room.Walk;
        Check(walk != null, $"{name} has a walk area");
        if (walk == null) return;

        var entries = room.GetNodeOrNull<Node>("Entries")?.GetChildren().OfType<Node2D>().ToList() ?? new();
        Check(entries.Count > 0, $"{name} has entry markers");
        if (entries.Count == 0) return;
        var hotspots = room.Hotspots.ToList();
        int paths = 0;
        foreach (var entry in entries)
        {
            var key = $"{name}/{entry.Name}";
            bool onFloor = OnFloor(walk, entry.Position);
            if (OffFloorEntries.Contains(key))
                Check(!onFloor, $"{key} is still off the floor (drop it from the allowlist)");
            else
                Check(onFloor, $"entry {key} at {entry.Position} stands on the floor");

            foreach (var h in hotspots)
            {
                var target = Destination(room, h);
                var path = walk.FindPath(entry.Position, target);
                paths++;
                CheckPath(walk, walk.Clamp(entry.Position), path, target, $"{key} -> {h.Id}");
            }
        }

        // walk for real from the first entry to every hotspot in turn
        var start = entries[0];
        string startName = start.Name;
        Check(_game.Player.Position.IsEqualApprox(start.Position), $"{name}/{startName}: player placed on the entry marker");
        foreach (var h in hotspots)
        {
            var target = Destination(room, h);
            if (!await WalkAndArrive(target, $"{name}: walk to {h.Id}")) continue;
            // the walk resolves inside Player._Process, just before it rescales for the final step
            await _game.ToSignal(_game.GetTree(), SceneTree.SignalName.ProcessFrame);
            float scale = room.ScaleAt(_game.Player.Position.Y);
            Check(Mathf.IsEqualApprox(_game.Player.Scale.Y, scale, 0.001f),
                $"{name}: scale at {h.Id} is {_game.Player.Scale.Y:0.###}, expected {scale:0.###}");
        }
        // a room script that grabs control (an intercept, a cutscene) would block every later click
        Check(!_game.Busy, $"{name}: walking around leaves the game idle");

        // every exit: walk up to it from the first entry, then take it (the room is reloaded each time)
        var exits = Enumerable.Range(0, hotspots.Count).Where(i => hotspots[i].IsExit).ToList();
        foreach (var i in exits)
        {
            await _game.ChangeRoom(name, startName);
            var h = _game.Room!.Hotspots.ElementAt(i);
            string id = h.Id, to = h.ExitTo, toEntry = h.ExitEntry;
            await WalkAndArrive(Destination(_game.Room!, h), $"{name}: walk to exit {id}");
            await _game.ChangeRoom(to, toEntry);
            var marker = _game.Room!.GetNodeOrNull<Node2D>($"Entries/{toEntry}");
            Check(_game.RoomScene == to && marker != null, $"{name}.{id} leads to {to}/{toEntry}");
            if (marker != null)
                Check(_game.Player.Position.IsEqualApprox(marker.Position), $"{name}.{id}: player stands on {to}/{toEntry}");
        }
        GD.Print($"[walk] {name}: {entries.Count} entries, {hotspots.Count} hotspots, {exits.Count} exits, {paths} paths");
    }

    /// <summary>Where a click on the hotspot finally leaves the player.</summary>
    private static Vector2 Destination(Room room, Hotspot h) =>
        room.Walk!.Clamp(room.ClampWalkTarget(Game.ApproachPoint(h)));

    private static bool OnFloor(WalkArea walk, Vector2 p) => walk.Contains(p) || walk.Clamp(p).DistanceTo(p) <= Tolerance;

    /// <summary>The path ends at the target and no segment leaves the floor.</summary>
    private void CheckPath(WalkArea walk, Vector2 from, List<Vector2> path, Vector2 target, string what)
    {
        _checks++;
        if (path.Count == 0 || path[^1].DistanceTo(target) > Tolerance)
        {
            Fail($"{what}: path ends at {(path.Count == 0 ? "nothing" : path[^1])}, not {target}");
            return;
        }
        var prev = from;
        foreach (var p in path)
        {
            int steps = Math.Max(1, (int)(prev.DistanceTo(p) / 2));
            for (int s = 0; s <= steps; s++)
            {
                var q = prev.Lerp(p, s / (float)steps);
                if (!OnFloor(walk, q))
                {
                    Fail($"{what}: path {from} -> {string.Join(" -> ", path)} leaves the floor at {q}");
                    return;
                }
            }
            prev = p;
        }
    }

    private async Task<bool> WalkAndArrive(Vector2 target, string what)
    {
        var walking = _game.WalkTo(target);
        var done = await Task.WhenAny(walking, _game.Wait(60));
        bool ok = done == walking && walking.Result && _game.Player.Position.DistanceTo(target) <= Tolerance;
        Check(ok, $"{what}: arrives at {target} (at {_game.Player.Position})");
        if (!ok) _game.Player.Stop();
        return ok;
    }

    // ------------------------------------------------------------------ real mouse input

    private async Task InputTests()
    {
        double timeScale = Engine.TimeScale;
        try
        {
            await _game.ChangeRoom("street", "start");
            var room = _game.Room!;
            var walk = room.Walk!;
            var player = _game.Player;

            // a click on bare floor walks there
            var a = FloorPoint(new Vector2(300, 206));
            Click(a);
            await Until(() => !player.IsWalking && player.Position.DistanceTo(a) <= Tolerance);
            Check(player.Position.DistanceTo(a) <= Tolerance, $"click on the floor at {a} walks there (at {player.Position})");

            // a click above the floor walks to the nearest floor point
            var sky = EmptyPoint(new Vector2(260, 140), p => !walk.Contains(p));
            var clamped = walk.Clamp(sky);
            Click(sky);
            await Until(() => !player.IsWalking && player.Position.DistanceTo(clamped) <= Tolerance);
            Check(player.Position.DistanceTo(clamped) <= Tolerance,
                $"click off the floor at {sky} stops at the floor edge {clamped} (at {player.Position})");

            // facing follows the direction of the walk
            Engine.TimeScale = 1;
            await CheckFacing(new Vector2(60, 206), new Vector2(400, 206), Repentance.Facing.Right);
            await CheckFacing(new Vector2(400, 206), new Vector2(60, 206), Repentance.Facing.Left);
            await CheckFacing(new Vector2(240, 236), new Vector2(240, 176), Repentance.Facing.Up);
            await CheckFacing(new Vector2(240, 176), new Vector2(240, 236), Repentance.Facing.Down);

            // a click mid-walk cancels the old walk and heads for the new point
            player.Teleport(FloorPoint(new Vector2(40, 206)), Repentance.Facing.Right);
            var far = _game.WalkTo(new Vector2(420, 206));
            await _game.Wait(0.3);
            Check(player.IsWalking && !far.IsCompleted, "a long walk is under way");
            var b = FloorPoint(new Vector2(150, 230));
            Click(b);
            await Until(() => !player.IsWalking, 15);
            Check(far.IsCompleted && !far.Result, "a new click interrupts the walk in progress");
            Check(player.Position.DistanceTo(b) <= Tolerance, $"the interrupting click walks to {b} (at {player.Position})");

            // clicks are ignored while a script runs
            var before = player.Position;
            var busy = _game.Run(() => _game.Wait(0.6));
            await _game.Wait(0.1);
            Click(FloorPoint(new Vector2(320, 220)));
            await _game.Wait(0.3);
            Check(_game.Busy && !player.IsWalking && player.Position == before, "floor clicks are ignored while busy");
            await busy;
            Engine.TimeScale = timeScale;

            // exits by clicking: the street's motel door, and back out of the motel room
            await ClickExit("motel_door", "motel_room", "start");
            await ClickExit("exit", "street", "motel");
            await ClickExit("library_door", "library", "start");
        }
        finally
        {
            Engine.TimeScale = timeScale;
        }
    }

    private async Task CheckFacing(Vector2 from, Vector2 to, Facing expected)
    {
        var player = _game.Player;
        player.Teleport(from, expected == Repentance.Facing.Left ? Repentance.Facing.Right : Repentance.Facing.Left);
        var walking = _game.WalkTo(to);
        await _game.Wait(0.15);
        Check(player.IsWalking && player.Facing == expected, $"walking {from} -> {to} faces {expected} (faces {player.Facing})");
        await Task.WhenAny(walking, _game.Wait(15));
        Check(!player.IsWalking && player.Facing == expected, $"stopping after {from} -> {to} still faces {expected}");
    }

    private async Task ClickExit(string id, string room, string entry)
    {
        var h = _game.Room?.FindHotspot(id);
        Check(h != null, $"{_game.RoomScene} has exit {id}");
        if (h == null) return;
        var point = HotspotPoint(h);
        Check(point != null, $"{_game.RoomScene}.{id} can be clicked");
        if (point == null) return;
        Move(point.Value);
        Click(point.Value);
        await Until(() => _game.RoomScene == room && !_game.Busy, 30);
        var marker = _game.Room?.GetNodeOrNull<Node2D>($"Entries/{entry}");
        Check(_game.RoomScene == room && marker != null && _game.Player.Position.IsEqualApprox(marker.Position),
            $"clicking {id} walks out to {room}/{entry} (in {_game.RoomScene} at {_game.Player.Position})");
    }

    /// <summary>A point that clicks this hotspot and nothing in front of it, away from the satchel.</summary>
    private Vector2? HotspotPoint(Hotspot h)
    {
        var r = h.Bounds;
        var c = r.GetCenter();
        if (Clickable(c) && _game.Room!.HotspotAt(c) == h) return c;
        for (float y = r.Position.Y + 1; y < r.End.Y; y += 2)
        for (float x = r.Position.X + 1; x < r.End.X; x += 2)
        {
            var p = new Vector2(x, y);
            if (Clickable(p) && _game.Room!.HotspotAt(p) == h) return p;
        }
        return null;
    }

    private Vector2 FloorPoint(Vector2 near) => EmptyPoint(near, p => _game.Room!.Walk!.Contains(p));

    /// <summary>The closest point to <paramref name="near"/> with no hotspot under it that satisfies <paramref name="ok"/>.</summary>
    private Vector2 EmptyPoint(Vector2 near, Func<Vector2, bool> ok)
    {
        for (int r = 0; r < 200; r += 2)
        for (int dy = -r; dy <= r; dy += 2)
        for (int dx = -r; dx <= r; dx += 2)
        {
            if (Math.Max(Math.Abs(dx), Math.Abs(dy)) != r) continue;
            var p = near + new Vector2(dx, dy);
            if (Clickable(p) && ok(p) && _game.Room!.HotspotAt(p) == null) return p;
        }
        throw new InvalidOperationException($"no empty point near {near} in {_game.RoomScene}");
    }

    private static bool Clickable(Vector2 p) => p.X is > 2 and < 430 && p.Y is > 2 and < 228;

    // ------------------------------------------------------------------ helpers

    private void Move(Vector2 pos)
    {
        _game.GetViewport().PushInput(new InputEventMouseMotion { Position = pos, GlobalPosition = pos }, true);
        _game.GetViewport().WarpMouse(pos);
    }

    private void Click(Vector2 pos)
    {
        foreach (var pressed in new[] { true, false })
        {
            _game.GetViewport().PushInput(new InputEventMouseButton
            {
                Position = pos, GlobalPosition = pos, ButtonIndex = MouseButton.Left, Pressed = pressed,
            }, true);
        }
    }

    private async Task Until(Func<bool> done, double timeout = 30)
    {
        for (double t = 0; t < timeout && !done(); t += 0.05) await _game.Wait(0.05);
    }

    private void Check(bool ok, string what)
    {
        _checks++;
        if (!ok) Fail(what);
    }

    private void Fail(string what)
    {
        GD.Print($"[walk] FAIL {what}");
        _failures.Add(what);
    }
}
