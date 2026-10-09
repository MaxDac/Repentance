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
/// rectangle is used as the clickable area. Sprite sheet: one row, frame 0 = idle, frame 1 = talking.
/// The node position is the character's feet.
/// </summary>
[GlobalClass]
public partial class Actor : Hotspot, ISpeaker
{
    [Export] public Texture2D? Texture;
    [Export] public int Frames = 2;
    [Export] public bool FlipH;
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
            Offset = new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y),
        };
        AddChild(_sprite);
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

    private void UpdateFrame()
    {
        if (_sprite == null) return;
        _sprite.Frame = _talking && Frames > 1 && ((int)(_talkTime * 7) % 2 == 0) ? 1 : 0;
    }

    private Rect2 SpriteRect => new(new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y), FrameSize);

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
