using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Loading, entering and leaving rooms.</summary>
public partial class Game
{
    public static string RoomScenePath(string room) => $"res://scenes/rooms/{room}.tscn";

    /// <summary>Test hook: room changes skip <see cref="Room.OnEnter"/> cutscenes and the autosave.</summary>
    public bool SkipRoomEnter { get; set; }

    /// <summary>File name (in scenes/rooms) of the loaded room.</summary>
    public string RoomScene => _roomScene;

    /// <summary>Entry name that places the player on a room's first marker, for tools that visit every room.</summary>
    public const string FirstEntry = "__first__";

    /// <summary>Why <paramref name="room"/>/<paramref name="entry"/> is not a valid destination, or null if it is.</summary>
    public static string? RoomTargetError(string room, string entry)
    {
        var path = RoomScenePath(room);
        if (!ResourceLoader.Exists(path)) return $"no room scene {path}";
        if (entry == FirstEntry) return null;
        var state = RoomPackedScene(room).GetState();
        for (var i = 0; i < state.GetNodeCount(); i++)
            if (state.GetNodePath(i).ToString() == $"./Entries/{entry}") return null;
        return $"room '{room}' has no entry marker '{entry}'";
    }

    /// <summary>
    /// The door the player is going through swings open (once per action): rooms whose door opens on screen call this
    /// with the animation, and <see cref="ChangeRoom"/> calls it for any <see cref="Hotspot.Door"/> it leaves by.
    /// </summary>
    public void OpenDoor()
    {
        if (_doorOpened) return;
        _doorOpened = true;
        Sfx.Play(Sound.DoorOpen);
    }

    public async Task ChangeRoom(string name, string entry, double fadeInSeconds = 0.35)
    {
        // a typo would otherwise leave the player on a grey screen; stay put and fail loudly instead
        if (RoomTargetError(name, entry) is { } error)
        {
            GD.PushError($"ChangeRoom({name}, {entry}): {error}");
            return;
        }
        _busy++;
        // a player walking through a door hears it open as the screen fades and shut behind them in the new room
        bool door = _actionTarget is { Door: true };
        _actionTarget = null;
        try
        {
            if (door) OpenDoor();
            await Hud.Fade(1, 0.35);
            LoadRoomScene(name);
            var marker = Room!.GetNodeOrNull<Node2D>($"Entries/{entry}");
            var facing = marker != null && marker.HasMeta("facing") ? (Facing)marker.GetMeta("facing").AsInt32() : Facing.Down;
            Player.Teleport(Room.EntryPoint(entry), facing);
            if (!SkipRoomEnter) Room.OnArriving(entry);
            await Hud.Fade(0, fadeInSeconds);
            if (door) Sfx.Play(Sound.DoorClose);
        }
        finally
        {
            _busy--;
            _doorOpened = false;
        }
        if (SkipRoomEnter) return;
        await Room!.OnEnter(entry);
        // written once the player is back in control, so entry cutscenes have already set their flags
        _autosavePending = true;
    }

    private void LoadRoomScene(string name)
    {
        UnloadRoom();
        Hud.HideCloseUp(0);
        Room = RoomPackedScene(name).Instantiate<Room>();
        _roomScene = name;
        _roomHost.AddChild(Room);
        Room.World.AddChild(Player);
        Player.SetCharacter(Room.ResolvePlayerCharacter());
        SyncPinned();
        Player.Visible = Room.PlayerVisibleOnLoad;
        if (Room.Ambience is { } ambience) Sfx.SetAmbient(ambience.Sound, ambience.VolumeDb);
        else Sfx.SetAmbient(null);
        Music.Play(Room.Music);
        var exits = Room.Hotspots.Where(h => h.Visible && h.ExitTo != "").Select(h => h.ExitTo).Distinct().ToList();
        Music.Prefetch(NeighbourMusic(exits));
        ReleaseRoomScenes(exits.Append(name).ToHashSet());
    }

    /// <summary>The music of the rooms these exits lead to, so it is rendered before the player goes there.</summary>
    private static List<Track> NeighbourMusic(IEnumerable<string> exits)
    {
        var tracks = new List<Track>();
        foreach (var exit in exits)
            if (RoomMusic(exit) is { } track) tracks.Add(track);
        return tracks;
    }

    /// <summary>
    /// Room scenes loaded through <see cref="RoomPackedScene"/>, held until <see cref="ReleaseRoomScenes"/> disposes
    /// them. Godot's resource cache does not own a loaded resource, so a dropped <c>GD.Load</c> result leaves the
    /// scene owned by a weak C# wrapper alone; if the GC collects it and the next load revives the cached scene
    /// before its finaliser runs, Godot 4.7.2 keeps a dead GC handle and later logs "Handle is not initialized"
    /// (godotengine/godot#124587). Holding the wrapper and disposing it explicitly leaves no such window.
    /// </summary>
    private static readonly Dictionary<string, PackedScene> RoomScenes = new();

    private static PackedScene RoomPackedScene(string room)
    {
        if (!RoomScenes.TryGetValue(room, out var scene))
            RoomScenes[room] = scene = GD.Load<PackedScene>(RoomScenePath(room));
        return scene;
    }

    /// <summary>Disposes the held room scenes except <paramref name="keep"/>, so only the current room's neighbourhood stays in memory.</summary>
    private static void ReleaseRoomScenes(IReadOnlySet<string> keep)
    {
        foreach (var room in RoomScenes.Keys.Where(r => !keep.Contains(r)).ToList())
        {
            RoomScenes[room].Dispose();
            RoomScenes.Remove(room);
        }
    }

    /// <summary>
    /// The music a room would play now, read from an instance of its script alone: building the whole scene would
    /// load its art just to ask.
    /// </summary>
    private static Track? RoomMusic(string room)
    {
        if (!ResourceLoader.Exists(RoomScenePath(room))) return null;
        if (RoomScript(room)?.Call("new").As<Room>() is not { } probe) return null;
        var track = probe.Music;
        probe.Free();
        return track;
    }

    /// <summary>
    /// Room root scripts read by <see cref="RoomMusic"/>, held for the whole run: a dropped wrapper of a script the
    /// next scene load revives would hit the same dead GC handle as <see cref="RoomScenes"/>. Scripts hold no art.
    /// </summary>
    private static readonly Dictionary<string, Script?> RoomScripts = new();

    private static Script? RoomScript(string room)
    {
        if (RoomScripts.TryGetValue(room, out var script)) return script;
        var state = RoomPackedScene(room).GetState();
        for (int i = 0; i < state.GetNodePropertyCount(0) && script == null; i++)
            if (state.GetNodePropertyName(0, i) == "script")
                script = state.GetNodePropertyValue(0, i).As<Script>();
        return RoomScripts[room] = script;
    }

    /// <summary>Micah always carries his notepad and lighter in the first slots; Daniel, in the present day, never does.</summary>
    private void SyncPinned()
    {
        if (IsMicah) GameState.Instance.EnsurePinned();
        else GameState.Instance.RemovePinned();
    }

    public bool IsMicah => Player.Character.StartsWith("micah");

    private void UnloadRoom()
    {
        _actionId++;
        Player.Stop();
        SetCarried(null);
        Hud.ShowInventory(false);
        Hud.Wheel.Close();
        Hud.SetHover(null, Hud.MousePos);
        if (Room == null) return;
        Room.World.RemoveChild(Player);
        // detached now so a reload of the same room keeps its node name instead of getting "@Node2D@N"
        _roomHost.RemoveChild(Room);
        Room.QueueFree();
        Room = null;
        _roomScene = "";
    }
}
