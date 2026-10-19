using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Every awaited <see cref="SceneTreeTimer"/> goes through <see cref="Wait"/>, which tracks the timers still pending.
/// Quitting while C# holds a timer's wrapper leaks its managed reference and makes Godot abort at shutdown
/// ("Leaked unsafe reference", then <c>!rc_owner</c>), so automated runs call <see cref="ReleasePending"/> first.
/// </summary>
public static class Timers
{
    // main thread only
    private static readonly HashSet<SceneTreeTimer> _pending = new();

    /// <summary>Timer waits not yet resumed.</summary>
    public static int Pending => _pending.Count;

    public static async Task Wait(Node node, double seconds, bool processAlways = false, bool ignoreTimeScale = false)
    {
        var timer = node.GetTree().CreateTimer(seconds, processAlways, ignoreTimeScale: ignoreTimeScale);
        _pending.Add(timer);
        try { await node.ToSignal(timer, SceneTreeTimer.SignalName.Timeout); }
        finally
        {
            _pending.Remove(timer);
            timer.Dispose();
        }
    }

    /// <summary>Drops the managed references to timers still pending (their waits never resume); call just before quitting.</summary>
    public static void ReleasePending()
    {
        foreach (var timer in _pending) timer.Dispose();
        _pending.Clear();
    }
}
