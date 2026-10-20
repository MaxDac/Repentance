using Godot;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Plays the game by touch: the first finger drives a <see cref="TouchPointer"/> whose taps, long presses and drags
/// reach the game as the mouse clicks it already understands (Godot's own mouse emulation is off, so a long press
/// doesn't click first). The Android back button acts as Esc.
/// </summary>
public partial class TouchInput : Node
{
    /// <summary>True since the last touch, until a real mouse moves: the HUD hides the crosshair and shows touch buttons.</summary>
    public static bool UsingTouch { get; private set; }

    private static bool _injecting;
    private readonly TouchPointer _pointer = new();
    private readonly Queue<InputEvent> _pending = new();
    private int _finger = -1;
    private MouseButtonMask _held;
    private Vector2 _last;

    public override void _Ready() => ProcessMode = ProcessModeEnum.Always;

    private static double Now => Time.GetTicksMsec() / 1000.0;

    public override void _Input(InputEvent e)
    {
        switch (e)
        {
            case InputEventScreenTouch touch:
                GetViewport().SetInputAsHandled();
                UsingTouch = true;
                if (touch.Pressed && _finger < 0)
                {
                    _finger = touch.Index;
                    Queue(_pointer.Down(touch.Position.X, touch.Position.Y, Now));
                }
                else if (!touch.Pressed && touch.Index == _finger)
                {
                    _finger = -1;
                    Queue(_pointer.Up(touch.Position.X, touch.Position.Y, Now));
                }
                break;
            case InputEventScreenDrag drag:
                GetViewport().SetInputAsHandled();
                if (drag.Index == _finger) Queue(_pointer.Move(drag.Position.X, drag.Position.Y, Now));
                break;
            case InputEventMouseMotion when !_injecting:
                UsingTouch = false;
                break;
        }
    }

    public override void _Notification(int what)
    {
        if (what == NotificationWMGoBackRequest) PressKey(Key.Escape);
    }

    public override void _Process(double delta)
    {
        Queue(_pointer.Tick(Now));
        while (_pending.Count > 0) Push(_pending.Dequeue());
    }

    /// <summary>Presses and releases a key next frame, as the touch buttons' stand-in for the keyboard.</summary>
    public void PressKey(Key key)
    {
        foreach (var pressed in new[] { true, false })
            _pending.Enqueue(new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = pressed });
    }

    private void Queue(IReadOnlyList<PointerAction> actions)
    {
        foreach (var a in actions)
        {
            var at = new Vector2(a.X, a.Y);
            switch (a.Kind)
            {
                case PointerKind.Move:
                    _pending.Enqueue(new InputEventMouseMotion
                    {
                        Position = at, GlobalPosition = at, Relative = at - _last, ButtonMask = _held,
                    });
                    break;
                default:
                    bool right = a.Kind is PointerKind.RightDown or PointerKind.RightUp;
                    bool pressed = a.Kind is PointerKind.LeftDown or PointerKind.RightDown;
                    var mask = right ? MouseButtonMask.Right : MouseButtonMask.Left;
                    _held = pressed ? _held | mask : _held & ~mask;
                    _pending.Enqueue(new InputEventMouseButton
                    {
                        Position = at, GlobalPosition = at, Pressed = pressed, ButtonMask = _held,
                        ButtonIndex = right ? MouseButton.Right : MouseButton.Left,
                    });
                    break;
            }
            _last = at;
        }
    }

    private void Push(InputEvent e)
    {
        _injecting = true;
        try { GetViewport().PushInput(e, true); }
        finally { _injecting = false; }
    }
}
