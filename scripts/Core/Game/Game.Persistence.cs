using Godot;
using System;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Saving and loading games.</summary>
public partial class Game
{
    /// <summary>Writes the autosave slot after every room change (turned off by tests that don't want it).</summary>
    public bool AutosaveEnabled { get; set; } = true;

    /// <summary>Saving is only allowed between actions, when no script, dialogue or fade is running.</summary>
    public bool CanSave => Room != null && !Busy && !_onTitle;

    public SaveData CaptureSave()
    {
        var data = new SaveData
        {
            SavedAtUtc = DateTime.UtcNow,
            Room = _roomScene,
            RoomTitle = Room?.RoomName ?? "",
            X = Player.Position.X,
            Y = Player.Position.Y,
            Facing = (int)Player.Facing,
            Ink = DialogueManager.Instance.SaveInk(),
            PlaytimeSeconds = _playtime,
        };
        GameState.Instance.CaptureInto(data);
        return data;
    }

    public bool SaveToSlot(string slot) => CanSave && SaveSystem.Write(slot, CaptureSave());

    /// <summary>Restores a save: game state, Ink state, room and the player's exact spot. Entry cutscenes don't replay.</summary>
    public async Task LoadGame(SaveData data)
    {
        _busy++;
        ReleaseTheEnd();
        try
        {
            await Hud.Fade(1, 0.35);
            PuzzleMigration.Normalize(data);
            GameState.Instance.Restore(data.Flags, data.Inventory, data.StoryAct);
            DialogueManager.Instance.LoadInk(data.Ink);
            _playtime = data.PlaytimeSeconds;
            _autosavePending = false;
            LoadRoomScene(data.Room);
            Player.Teleport(new Vector2(data.X, data.Y), (Facing)data.Facing);
            await Hud.Fade(0, 0.35);
        }
        finally { _busy--; }
    }
}
