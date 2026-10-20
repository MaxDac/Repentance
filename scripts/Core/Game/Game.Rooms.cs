using Godot;
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
        var state = GD.Load<PackedScene>(path).GetState();
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
        Room = GD.Load<PackedScene>(RoomScenePath(name)).Instantiate<Room>();
        _roomScene = name;
        _roomHost.AddChild(Room);
        Room.World.AddChild(Player);
        Player.SetCharacter(Room.ResolvePlayerCharacter());
        SyncPinned();
        Player.Visible = Room.PlayerVisibleOnLoad;
        if (Room.Ambience is { } ambience) Sfx.SetAmbient(ambience.Sound, ambience.VolumeDb);
        else Sfx.SetAmbient(null);
        Music.Play(Room.Music);
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
