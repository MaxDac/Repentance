using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Godot falls back to its silent Dummy audio driver for the whole run when no output device can be opened at start
/// (a headset that is off, a device held exclusively by another app). It never retries, so the game offers a restart.
/// </summary>
public static class AudioFallback
{
    public const string DummyDriver = "Dummy";

    /// <summary>True when <paramref name="driverName"/> is the Dummy driver but the engine arguments didn't ask for it
    /// (<c>--audio-driver Dummy</c> or <c>--headless</c>), i.e. every real driver failed.</summary>
    public static bool IsUnintended(string driverName, IReadOnlyList<string> engineArgs)
    {
        if (!string.Equals(driverName, DummyDriver, StringComparison.OrdinalIgnoreCase)) return false;
        for (int i = 0; i < engineArgs.Count; i++)
        {
            var arg = engineArgs[i];
            if (arg == "--") break;
            if (arg == "--headless") return false;
            if (arg == "--audio-driver" && i + 1 < engineArgs.Count && IsDummy(engineArgs[i + 1])) return false;
            if (arg.StartsWith("--audio-driver=", StringComparison.Ordinal) && IsDummy(arg["--audio-driver=".Length..]))
                return false;
        }
        return true;
    }

    private static bool IsDummy(string name) => string.Equals(name, DummyDriver, StringComparison.OrdinalIgnoreCase);
}
