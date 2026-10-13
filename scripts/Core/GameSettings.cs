using Godot;
using System;

namespace Repentance;

/// <summary>Player-wide preferences, separate from story progress and save slots.</summary>
public sealed class GameSettings
{
    private readonly string _path;
    public bool NudityEnabled { get; private set; }
    public bool Fullscreen { get; private set; }
    public event Action? Changed;

    public GameSettings(string path = "user://settings.cfg") => _path = path;

    public bool Load()
    {
        var config = new ConfigFile();
        var error = config.Load(_path);
        bool nudity = false, fullscreen = false;
        if (error != Error.Ok && error != Error.FileNotFound)
        {
            GD.PushError($"Cannot read settings {_path}: {error}");
            return false;
        }
        if (error == Error.Ok &&
            (!ReadBool(config, "content", "nudity", out nudity) ||
             !ReadBool(config, "display", "fullscreen", out fullscreen)))
            return false;
        NudityEnabled = nudity;
        Fullscreen = fullscreen;
        Changed?.Invoke();
        return true;
    }

    public bool SetNudity(bool enabled) => Save(enabled, Fullscreen);

    public bool SetFullscreen(bool enabled) => Save(NudityEnabled, enabled);

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

    private bool Save(bool nudity, bool fullscreen)
    {
        var config = new ConfigFile();
        config.SetValue("content", "nudity", nudity);
        config.SetValue("display", "fullscreen", fullscreen);
        var error = config.Save(_path);
        if (error != Error.Ok)
        {
            GD.PushError($"Cannot write settings {_path}: {error}");
            return false;
        }
        NudityEnabled = nudity;
        Fullscreen = fullscreen;
        Changed?.Invoke();
        return true;
    }
}
