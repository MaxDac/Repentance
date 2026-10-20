using Godot;
using System.Linq;

namespace Repentance;

/// <summary>Sound lost at start: Godot's fallback to the silent Dummy driver, and the relaunch that recovers from it.</summary>
public partial class Game
{
    /// <summary>Test hook: pretend the real audio drivers all failed at start.</summary>
    public bool? SoundLostOverride { get; set; }

    // The process's own arguments: Godot's OS.GetCmdlineArgs() leaves out the engine options it consumed, such as
    // --audio-driver and --headless.
    private static string[] LaunchArgs => System.Environment.GetCommandLineArgs().Skip(1).ToArray();

    /// <summary>Every real audio driver failed at start, so the game is silent until it is relaunched
    /// (see <see cref="AudioFallback"/>).</summary>
    public bool SoundLost => SoundLostOverride ??
        AudioFallback.IsUnintended(AudioServer.GetDriverName(), LaunchArgs);

    /// <summary>Saves to the autosave slot if the game can be saved, then relaunches with the same arguments; the
    /// title's Continue picks the game up again.</summary>
    public void RestartSound()
    {
        if (CanSave) SaveToSlot(SaveSystem.AutosaveSlot);
        OS.SetRestartOnExit(true, LaunchArgs);
        Timers.ReleasePending();
        GetTree().Quit();
    }

    private void ReportSoundLost()
    {
        if (SoundLost) GD.Print("No audio output device could be opened at start; sound is off until the game restarts.");
    }
}
