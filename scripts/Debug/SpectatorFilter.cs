using Godot;

namespace Repentance;

/// <summary>
/// Film mode's input guard. Added as the last child of the root, it sees every event first and swallows the viewer's
/// clicks and keys, so the film can't be skipped or steered. Space (pause) and F11 (full screen) still work, and Esc
/// stops the film. The film's own puzzle and satchel clicks pass, flagged by <see cref="Injecting"/>.
/// </summary>
public partial class SpectatorFilter : Node
{
    /// <summary>True while the harness pushes its own event; <c>Viewport.PushInput</c> dispatches synchronously.</summary>
    internal static bool Injecting;

    public override void _Ready() => ProcessMode = ProcessModeEnum.Always;

    public override void _Input(InputEvent e)
    {
        if (Injecting || e is InputEventMouseMotion) return;
        if (e is InputEventKey { Pressed: true, Echo: false, Keycode: Key.Escape })
        {
            GetViewport().SetInputAsHandled();
            GD.Print("FILM STOPPED by the viewer");
            Engine.TimeScale = 1;
            GetTree().Quit(0);
            return;
        }
        if (e.IsAction("pause_game") || e.IsAction("toggle_fullscreen")) return;
        GetViewport().SetInputAsHandled();
    }
}
