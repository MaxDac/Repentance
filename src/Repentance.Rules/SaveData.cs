using System;
using System.Collections.Generic;
using System.Text.Json;

namespace Repentance;

/// <summary>
/// Everything needed to restore a game. Room progress is entirely flag-driven, so flags, inventory,
/// story act, Ink state and the player's room/position describe a game completely.
/// Godot-free so it can be unit tested.
/// </summary>
public sealed class SaveData
{
    /// <summary>Bump when saved decisions, identifiers or room flow change incompatibly.</summary>
    public const int CurrentVersion = 12;

    public int Version { get; set; } = CurrentVersion;
    public DateTime SavedAtUtc { get; set; }
    /// <summary>Room scene file name (res://scenes/rooms/{Room}.tscn).</summary>
    public string Room { get; set; } = "";
    /// <summary>Human-readable room name shown in the slot list.</summary>
    public string RoomTitle { get; set; } = "";
    public float X { get; set; }
    public float Y { get; set; }
    public int Facing { get; set; }
    public int StoryAct { get; set; } = 1;
    public List<string> Flags { get; set; } = new();
    public List<string> Inventory { get; set; } = new();
    /// <summary>Ink runtime state JSON (visit counts, variables); empty when no conversation has run yet.</summary>
    public string Ink { get; set; } = "";
    public double PlaytimeSeconds { get; set; }
}

public static class SaveSerializer
{
    private static readonly JsonSerializerOptions Options = new() { WriteIndented = true };

    public static string Serialize(SaveData data) => JsonSerializer.Serialize(data, Options);

    /// <summary>Parses a save; returns null for corrupt, incomplete or incompatible files instead of throwing.</summary>
    public static SaveData? TryDeserialize(string? json)
    {
        if (string.IsNullOrWhiteSpace(json)) return null;
        try
        {
            var data = JsonSerializer.Deserialize<SaveData>(json, Options);
            if (data == null || data.Version != SaveData.CurrentVersion || string.IsNullOrEmpty(data.Room)) return null;
            data.Flags ??= new();
            data.Inventory ??= new();
            data.Ink ??= "";
            data.RoomTitle ??= "";
            return data;
        }
        catch (JsonException)
        {
            return null;
        }
    }
}
