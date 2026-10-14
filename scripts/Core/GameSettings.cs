using Godot;
using System;

namespace Repentance;

/// <summary>Player-wide preferences, separate from story progress and save slots.</summary>
public sealed class GameSettings
{
    public const int DefaultEffectsVolume = 80;
    public const int VolumeStep = 10;

    private readonly string _path;
    public bool NudityEnabled { get; private set; }
    public bool Fullscreen { get; private set; }
    /// <summary>Sound-effect volume, 0-100 in steps of <see cref="VolumeStep"/>.</summary>
    public int EffectsVolume { get; private set; } = DefaultEffectsVolume;
    public event Action? Changed;

    public GameSettings(string path = "user://settings.cfg") => _path = path;

    public bool Load()
    {
        var config = new ConfigFile();
        var error = config.Load(_path);
        bool nudity = false, fullscreen = false;
        int effects = DefaultEffectsVolume;
        if (error != Error.Ok && error != Error.FileNotFound)
        {
            GD.PushError($"Cannot read settings {_path}: {error}");
            return false;
        }
        if (error == Error.Ok &&
            (!ReadBool(config, "content", "nudity", out nudity) ||
             !ReadBool(config, "display", "fullscreen", out fullscreen) ||
             !ReadVolume(config, "audio", "effects_volume", out effects)))
            return false;
        NudityEnabled = nudity;
        Fullscreen = fullscreen;
        EffectsVolume = effects;
        Changed?.Invoke();
        return true;
    }

    public bool SetNudity(bool enabled) => Save(enabled, Fullscreen, EffectsVolume);

    public bool SetFullscreen(bool enabled) => Save(NudityEnabled, enabled, EffectsVolume);

    public bool SetEffectsVolume(int percent) => Save(NudityEnabled, Fullscreen, ClampVolume(percent));

    /// <summary>The next volume step up (<paramref name="up"/>) or down, wrapping around between 0 and 100.</summary>
    public static int CycleVolume(int percent, bool up)
    {
        int next = ClampVolume(percent) + (up ? VolumeStep : -VolumeStep);
        return next > 100 ? 0 : next < 0 ? 100 : next;
    }

    private static int ClampVolume(int percent) =>
        Math.Clamp((int)Math.Round(percent / (double)VolumeStep) * VolumeStep, 0, 100);

    private bool ReadBool(ConfigFile config, string section, string key, out bool result)
    {
        result = false;
        var value = config.GetValue(section, key, false);
        if (value.VariantType != Variant.Type.Bool)
        {
            GD.PushError($"Invalid {key} setting in {_path}: expected a boolean.");
            return false;
        }
        result = value.AsBool();
        return true;
    }

    private bool ReadVolume(ConfigFile config, string section, string key, out int result)
    {
        result = DefaultEffectsVolume;
        var value = config.GetValue(section, key, DefaultEffectsVolume);
        if (value.VariantType != Variant.Type.Int)
        {
            GD.PushError($"Invalid {key} setting in {_path}: expected a whole number from 0 to 100.");
            return false;
        }
        result = ClampVolume(value.AsInt32());
        return true;
    }

    private bool Save(bool nudity, bool fullscreen, int effects)
    {
        var config = new ConfigFile();
        config.SetValue("content", "nudity", nudity);
        config.SetValue("display", "fullscreen", fullscreen);
        config.SetValue("audio", "effects_volume", effects);
        var error = config.Save(_path);
        if (error != Error.Ok)
        {
            GD.PushError($"Cannot write settings {_path}: {error}");
            return false;
        }
        NudityEnabled = nudity;
        Fullscreen = fullscreen;
        EffectsVolume = effects;
        Changed?.Invoke();
        return true;
    }
}
