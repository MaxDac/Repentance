using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// A framed close-up panel popped up over the scene (built by tools/art/closeup.py into assets/art/ui/).
/// The Hud does the rest: fades, speech along the panel's bottom edge, swapping variants when settings change,
/// and clearing it on a room change. Add a new one to <see cref="CloseUps"/>, then show it with
/// <see cref="Hud.ShowCloseUp"/> or from ink with "INSET: id".
/// </summary>
/// <param name="Id">Name used by ink ("INSET: id") and checks.</param>
/// <param name="Texture">The picture's name under assets/art/ui/, which may depend on the settings (variants).</param>
/// <param name="FadeIn">Seconds to fade in.</param>
/// <param name="FadeOut">Seconds to fade out.</param>
public sealed record CloseUp(string Id, Func<GameSettings?, string> Texture, double FadeIn = 0.4, double FadeOut = 0.3)
{
    public CloseUp(string id, string texture, double fadeIn = 0.4, double fadeOut = 0.3)
        : this(id, _ => texture, fadeIn, fadeOut) { }

    /// <summary>A photograph: a small print on the left of the screen, with speech in a column to its right.</summary>
    public bool Photo { get; init; }

    public string TexturePath(GameSettings? settings) => $"res://assets/art/ui/{Texture(settings)}.png";
}

/// <summary>Every close-up in the game.</summary>
public static class CloseUps
{
    /// <summary>Eleanor in the Club's spotlight, the stag, boar and wolf behind her; dressed unless nudity is on.</summary>
    public static readonly CloseUp Stage = new("stage",
        s => s?.NudityEnabled == true ? "stage_closeup" : "stage_closeup_clothed");

    /// <summary>Rose at her door, calling Micah back, on the left; Micah on the right, with nothing to say.</summary>
    public static readonly CloseUp Rose = new("rose", "rose_closeup");

    /// <summary>Micah flat on the cathedral steps in Act 3.</summary>
    public static readonly CloseUp Beaten = new("beaten", "beaten_closeup");

    /// <summary>The motel sign down the road from the convent, the long shot Micah spots in Act 1.</summary>
    public static readonly CloseUp Motel = new("motel", "motel_closeup");

    /// <summary>On the motel fire escape, after the First Interlude: Micah on the left, Eleanor on the right.</summary>
    public static readonly CloseUp FireEscape = new("fire_escape", "fire_escape_closeup");

    /// <summary>The band of heraldry at the foot of Harrington senior's portrait: raven and star, lion and sun,
    /// stag and moon.</summary>
    public static readonly CloseUp Heraldry = new("heraldry", "heraldry_closeup");

    /// <summary>Micah and Rose the day they renewed their vows, a sepia print on a cream card, in Daniel's epilogue
    /// to ending 1.</summary>
    public static readonly CloseUp Vows = new("vows", "vows_photo", 0.8, 0.6) { Photo = true };

    private static readonly Dictionary<string, CloseUp> ById = new()
    {
        [Stage.Id] = Stage, [Rose.Id] = Rose, [Beaten.Id] = Beaten, [FireEscape.Id] = FireEscape, [Heraldry.Id] = Heraldry,
        [Motel.Id] = Motel, [Vows.Id] = Vows,
    };

    public static CloseUp Get(string id) =>
        ById.TryGetValue(id, out var c) ? c : throw new ArgumentException($"Unknown close-up \"{id}\"", nameof(id));
}
