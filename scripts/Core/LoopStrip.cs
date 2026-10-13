using Godot;

namespace Repentance;

/// <summary>
/// A flag-controlled overlay cut as a horizontal strip (<see cref="Sprite2D.Hframes"/>) that loops its frames for as
/// long as it's visible, e.g. the flames and smoke of a burning trash can.
/// </summary>
[GlobalClass]
public partial class LoopStrip : FlagSprite
{
    [Export] public float FrameSeconds = 0.1f;

    private float _left;

    public override void _Process(double delta)
    {
        if (!Visible || Hframes * Vframes < 2 || FrameSeconds <= 0) return;
        _left -= (float)delta;
        while (_left <= 0)
        {
            Frame = (Frame + 1) % (Hframes * Vframes);
            _left += FrameSeconds;
        }
    }
}
