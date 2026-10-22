using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// A framed close-up panel popped up over the scene (built by tools/art/closeup.py into assets/art/ui/).
/// The Hud does the rest: fades, speech along the panel's bottom edge (beneath the speaker's own portrait on a
/// two-portrait panel, or in captions below it), swapping variants when settings change,
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

    /// <summary>Speaker on the left of a two-portrait panel (the player counts as their character, e.g. "micah");
    /// speech from anyone but
    /// <see cref="RightSpeaker"/> goes beneath this portrait.</summary>
    public string? LeftSpeaker { get; init; }

    /// <summary>Speaker on the right of a two-portrait panel (the player counts as their character); their speech goes beneath the
    /// right portrait. Set it to split speech per portrait instead of centring it across the panel.</summary>
    public string? RightSpeaker { get; init; }

    public bool TwoPortraits => RightSpeaker != null;

    /// <summary>A comic strip: a short two-portrait panel along the top of the screen, each line in a caption under
    /// its speaker's half instead of over the picture, and Micah's narration in a caption across the whole panel.</summary>
    public bool CaptionsBelow { get; init; }

    public string TexturePath(GameSettings? settings) => $"res://assets/art/ui/{Texture(settings)}.png";
}

/// <summary>Every close-up in the game.</summary>
public static class CloseUps
{
    /// <summary>Eleanor in the Club's spotlight, the stag, boar and wolf behind her; dressed unless nudity is on.</summary>
    public static readonly CloseUp Stage = new("stage",
        s => s?.NudityEnabled == true ? "stage_closeup" : "stage_closeup_clothed");

    /// <summary>Rose at her door, calling Micah back, on the left; Micah on the right, with nothing to say.</summary>
    public static readonly CloseUp Rose = new("rose", "rose_closeup")
    {
        LeftSpeaker = "rose", RightSpeaker = "micah",
    };

    /// <summary>Micah flat on the cathedral steps in Act 3.</summary>
    public static readonly CloseUp Beaten = new("beaten", "beaten_closeup");

    /// <summary>The motel sign down the road from the convent, the long shot Micah spots in Act 1.</summary>
    public static readonly CloseUp Motel = new("motel", "motel_closeup");

    /// <summary>On the motel fire escape, after the First Interlude: Micah on the left, Eleanor on the right.</summary>
    public static readonly CloseUp FireEscape = new("fire_escape", "fire_escape_closeup")
    {
        LeftSpeaker = "micah", RightSpeaker = "eleanor",
    };

    /// <summary>The brothers in the cathedral nave, a comic strip: Micah on the left, Father Caleb on the right,
    /// each line captioned under its speaker.</summary>
    public static readonly CloseUp Church = new("church", "church_closeup")
    {
        LeftSpeaker = "micah", RightSpeaker = "caleb", CaptionsBelow = true,
    };

    /// <summary>The band of heraldry at the foot of Harrington senior's portrait: raven and star, lion and sun,
    /// stag and moon.</summary>
    public static readonly CloseUp Heraldry = new("heraldry", "heraldry_closeup");

    /// <summary>Micah and Rose the day they renewed their vows, a sepia print on a cream card, in Daniel's epilogue
    /// to ending 1.</summary>
    public static readonly CloseUp Vows = new("vows", "vows_photo", 0.8, 0.6) { Photo = true };

    private static readonly Dictionary<string, CloseUp> ById = new()
    {
        [Stage.Id] = Stage, [Rose.Id] = Rose, [Beaten.Id] = Beaten, [FireEscape.Id] = FireEscape, [Heraldry.Id] = Heraldry,
        [Motel.Id] = Motel, [Vows.Id] = Vows, [Church.Id] = Church,
    };

    public static CloseUp Get(string id) =>
        ById.TryGetValue(id, out var c) ? c : throw new ArgumentException($"Unknown close-up \"{id}\"", nameof(id));
}
