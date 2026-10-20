using Godot;

namespace Repentance;

/// <summary>
/// Applies <see cref="GameSettings.Fullscreen"/> to the OS window and handles the F11 / Alt+Enter toggle,
/// including on the title screen and while paused.
/// </summary>
public partial class WindowModeController : Node
{
    private readonly GameSettings _settings;
    private readonly bool _applyToWindow;
    private static readonly Vector2I WindowedSize = new(1440, 810);

    /// <param name="applyToWindow">False for automated runs, which must never resize the developer's window.</param>
    public WindowModeController(GameSettings settings, bool applyToWindow)
    {
        _settings = settings;
        // a phone or tablet always runs full screen; only desktops have a window to size
        _applyToWindow = applyToWindow && DisplayServer.GetName() != "headless" && !OS.HasFeature("mobile");
        ProcessMode = ProcessModeEnum.Always;
    }

    public WindowModeController() : this(new GameSettings(), false) { }

    public override void _Ready()
    {
        _settings.Changed += Apply;
        Apply();
    }

    public override void _ExitTree() => _settings.Changed -= Apply;

    public override void _Input(InputEvent e)
    {
        if (e is InputEventKey { Echo: true } || !e.IsActionPressed("toggle_fullscreen")) return;
        GetViewport().SetInputAsHandled();
        _settings.SetFullscreen(!_settings.Fullscreen);
    }

    private void Apply()
    {
        if (!_applyToWindow) return;
        var current = DisplayServer.WindowGetMode();
        bool isFullscreen = current is DisplayServer.WindowMode.Fullscreen or DisplayServer.WindowMode.ExclusiveFullscreen;
        if (isFullscreen == _settings.Fullscreen) return;
        var target = _settings.Fullscreen ? DisplayServer.WindowMode.Fullscreen : DisplayServer.WindowMode.Windowed;
        DisplayServer.WindowSetMode(target);
        if (target != DisplayServer.WindowMode.Windowed) return;
        DisplayServer.WindowSetSize(WindowedSize);
        var screen = DisplayServer.ScreenGetUsableRect(DisplayServer.WindowGetCurrentScreen());
        DisplayServer.WindowSetPosition(screen.Position + (screen.Size - WindowedSize) / 2);
    }
}
