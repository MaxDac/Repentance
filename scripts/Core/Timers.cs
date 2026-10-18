using Godot;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Every awaited <see cref="SceneTreeTimer"/> goes through <see cref="Wait"/>, which counts the waits still pending.
/// Quitting while C# awaits a timer leaks the timer's managed reference and makes Godot abort at shutdown
/// ("Leaked unsafe reference", then <c>!rc_owner</c>), so automated runs let <see cref="Pending"/> reach 0 first.
/// </summary>
public static class Timers
{
    /// <summary>Timer waits not yet resumed (main thread only).</summary>
    public static int Pending { get; private set; }

    public static async Task Wait(Node node, double seconds, bool processAlways = false, bool ignoreTimeScale = false)
    {
        var timer = node.GetTree().CreateTimer(seconds, processAlways, ignoreTimeScale: ignoreTimeScale);
        Pending++;
        try { await node.ToSignal(timer, SceneTreeTimer.SignalName.Timeout); }
        finally { Pending--; }
    }
}
