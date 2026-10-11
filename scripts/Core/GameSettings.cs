using Godot;
using System;

namespace Repentance;

/// <summary>Player-wide preferences, separate from story progress and save slots.</summary>
public sealed class GameSettings
{
    private readonly string _path;
    public bool NudityEnabled { get; private set; }
    public event Action? Changed;

    public GameSettings(string path = "user://settings.cfg") => _path = path;

    public bool Load()
    {
        var config = new ConfigFile();
        var error = config.Load(_path);
        bool enabled = false;
        if (error != Error.Ok && error != Error.FileNotFound)
        {
            GD.PushError($"Cannot read settings {_path}: {error}");
            return false;
        }
        if (error == Error.Ok)
        {
            var value = config.GetValue("content", "nudity", false);
            if (value.VariantType != Variant.Type.Bool)
            {
                GD.PushError($"Invalid nudity setting in {_path}: expected a boolean.");
                return false;
            }
            enabled = value.AsBool();
        }
        NudityEnabled = enabled;
        Changed?.Invoke();
        return true;
    }

    public bool SetNudity(bool enabled)
    {
        var config = new ConfigFile();
        config.SetValue("content", "nudity", enabled);
        var error = config.Save(_path);
        if (error != Error.Ok)
        {
            GD.PushError($"Cannot write settings {_path}: {error}");
            return false;
        }
        NudityEnabled = enabled;
        Changed?.Invoke();
        return true;
    }
}
