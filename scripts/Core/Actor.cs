using Godot;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Anything that can show speech text above its head.</summary>
public interface ISpeaker
{
    Vector2 HeadPosition { get; }
    Color SpeechColor { get; }
    bool Talking { set; }
}

/// <summary>
/// A non-player character. It is also a hotspot; if it has no collision shape the sprite
/// rectangle is used as the clickable area. Sprite sheet: one row, frame 0 = idle, then talk frames
/// (1 for a two-frame strip; 1 and 2 for the three-frame strips painted by tools/art/sprites.py).
/// The node position is the character's feet, which sit <see cref="Baseline"/> pixels above the frame bottom.
/// </summary>
[GlobalClass]
public partial class Actor : Hotspot, ISpeaker
{
    [Export] public Texture2D? Texture;
    [Export] public int Frames = 3;
    [Export] public bool FlipH;
    [Export] public int Baseline = 3;
    /// <summary>Scale with depth like the player (<see cref="Room.ScaleAt"/>).</summary>
    [Export] public bool DepthScale = true;
    [Export] public Color SpeechColor { get; set; } = Colors.White;

    private Sprite2D? _sprite;
    private bool _talking;
    private double _talkTime;
    private Vector2? _moveTarget;
    private float _moveSpeed;
    private TaskCompletionSource? _moveDone;

    public Vector2 FrameSize => Texture == null ? new Vector2(16, 40) : new Vector2(Texture.GetWidth() / Frames, Texture.GetHeight());

    public Vector2 HeadPosition => GlobalPosition - new Vector2(0, FrameSize.Y * GlobalScale.Y + 3);

    public bool Talking
    {
        set { _talking = value; _talkTime = 0; UpdateFrame(); }
    }

    public override void _Ready()
    {
        if (Texture == null) return;
        _sprite = new Sprite2D
        {
            Texture = Texture,
            Hframes = Frames,
            Centered = false,
            FlipH = FlipH,
            Offset = new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y + Baseline),
        };
        AddChild(_sprite);
        ApplyDepthScale();
    }

    private void ApplyDepthScale()
    {
        if (!DepthScale) return;
        for (Node? n = GetParent(); n != null; n = n.GetParent())
            if (n is Room r) { Scale = Vector2.One * r.ScaleAt(Position.Y); return; }
    }

    public override void _Process(double delta)
    {
        if (_talking)
        {
            _talkTime += delta;
            UpdateFrame();
        }
        if (_moveTarget is { } target)
        {
            Position = Position.MoveToward(target, _moveSpeed * (float)delta);
            ApplyDepthScale();
            if (Position.DistanceTo(target) < 0.01f)
            {
                _moveTarget = null;
                _moveDone?.TrySetResult();
            }
        }
    }

    /// <summary>Slides the actor to a point (room coordinates). Simple, but enough for cutscenes.</summary>
    public Task MoveTo(Vector2 target, float speed = 40)
    {
        _moveDone?.TrySetResult();
        _moveDone = new TaskCompletionSource();
        _moveTarget = target;
        _moveSpeed = speed;
        if (_sprite != null && Mathf.Abs(target.X - Position.X) > 1)
            _sprite.FlipH = target.X < Position.X;
        return _moveDone.Task;
    }

    /// <summary>Turns the actor to face screen-left (true) or screen-right (false) without moving.</summary>
    public void FaceLeft(bool left)
    {
        FlipH = left;
        if (_sprite != null) _sprite.FlipH = left;
    }

    private static readonly int[] TalkCycle = { 1, 2, 1, 0, 2, 1, 2, 0 };

    private void UpdateFrame()
    {
        if (_sprite == null) return;
        if (!_talking || Frames < 2) { _sprite.Frame = 0; return; }
        int tick = (int)(_talkTime * 7);
        _sprite.Frame = Frames >= 3 ? TalkCycle[tick % TalkCycle.Length] : (tick % 2 == 0 ? 1 : 0);
    }

    private Rect2 SpriteRect => new(new Vector2(-Mathf.Floor(FrameSize.X / 2) + 8, -FrameSize.Y + Baseline + 8),
        FrameSize - new Vector2(16, 8));

    public override bool Contains(Vector2 point)
    {
        if (GetChildCount() > (_sprite == null ? 0 : 1)) return base.Contains(point);
        return SpriteRect.Grow(-2).HasPoint(ToLocal(point));
    }

    public override Rect2 Bounds
    {
        get
        {
            if (GetChildCount() > (_sprite == null ? 0 : 1)) return base.Bounds;
            return GlobalTransform * SpriteRect;
        }
    }
}
