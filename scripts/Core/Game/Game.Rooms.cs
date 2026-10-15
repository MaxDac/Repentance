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

    public async Task ChangeRoom(string name, string entry)
    {
        _busy++;
        try
        {
            await Hud.Fade(1, 0.35);
            LoadRoomScene(name);
            var marker = Room!.GetNodeOrNull<Node2D>($"Entries/{entry}");
            var facing = marker != null && marker.HasMeta("facing") ? (Facing)marker.GetMeta("facing").AsInt32() : Facing.Down;
            Player.Teleport(Room.EntryPoint(entry), facing);
            await Hud.Fade(0, 0.35);
        }
        finally { _busy--; }
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
        Room.QueueFree();
        Room = null;
        _roomScene = "";
    }
}
