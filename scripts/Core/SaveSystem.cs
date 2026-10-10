using Godot;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>Reads and writes save files in user://saves: one autosave plus <see cref="ManualSlots"/> manual slots.</summary>
public static class SaveSystem
{
    public const string AutosaveSlot = "autosave";
    public const int ManualSlots = 3;

    /// <summary>Save folder; the autoplay test points this elsewhere so it never touches the player's saves.</summary>
    public static string Directory { get; set; } = "user://saves";

    public static string ManualSlot(int index) => $"slot{index + 1}";

    public static IEnumerable<string> AllSlots =>
        Enumerable.Range(0, ManualSlots).Select(ManualSlot).Prepend(AutosaveSlot);

    private static string PathFor(string slot) => $"{Directory}/{slot}.json";

    public static bool Write(string slot, SaveData data)
    {
        DirAccess.MakeDirRecursiveAbsolute(Directory);
        var path = PathFor(slot);
        var tmp = path + ".tmp";
        using (var file = FileAccess.Open(tmp, FileAccess.ModeFlags.Write))
        {
            if (file == null)
            {
                GD.PushError($"Cannot write save {tmp}: {FileAccess.GetOpenError()}");
                return false;
            }
            file.StoreString(SaveSerializer.Serialize(data));
        }
        // write-then-rename so a crash mid-save never leaves a half-written slot
        var err = DirAccess.RenameAbsolute(tmp, path);
        if (err != Error.Ok)
        {
            GD.PushError($"Cannot finalize save {path}: {err}");
            return false;
        }
        return true;
    }

    public static bool Exists(string slot) => FileAccess.FileExists(PathFor(slot));

    /// <summary>The save in a slot, or null if the slot is empty, corrupt or from an incompatible version.</summary>
    public static SaveData? Read(string slot)
    {
        if (!Exists(slot)) return null;
        using var file = FileAccess.Open(PathFor(slot), FileAccess.ModeFlags.Read);
        var data = file == null ? null : SaveSerializer.TryDeserialize(file.GetAsText());
        // a room that was renamed or removed since the save was made can't be restored
        return data != null && ResourceLoader.Exists(Game.RoomScenePath(data.Room)) ? data : null;
    }

    /// <summary>The most recent readable save across all slots (for "Continue").</summary>
    public static SaveData? Latest() => AllSlots
        .Select(Read)
        .Where(d => d != null)
        .OrderByDescending(d => d!.SavedAtUtc)
        .FirstOrDefault();

    public static void Delete(string slot)
    {
        if (Exists(slot)) DirAccess.RemoveAbsolute(PathFor(slot));
    }
}
