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
/// (1 for a two-frame strip; 1 and 2 for the strips painted by tools/art/sprites.py), then — in the 11-frame strips
/// painted by tools/art/sprites.py — frames 3-10 are a side-view walk cycle facing screen-right, played by
/// <see cref="MoveTo"/>. The node position is the character's feet, which sit <see cref="Baseline"/> pixels above
/// the frame bottom.
/// </summary>
[GlobalClass]
public partial class Actor : Hotspot, ISpeaker
{
    private const int WalkStart = 3;
    private const int WalkFrames = 8;
    /// <summary>Unscaled distance covered per walk frame; matches the player's side stride.</summary>
    private const float StridePerFrame = 7.7f;

    [Export] public Texture2D? Texture;
    [Export] public int Frames = WalkStart + WalkFrames;
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
    private float _walkDistance;
    private PosePlayback? _poses;
    public PosePlayback? Poses => _poses;

    private bool CanWalk => Frames >= WalkStart + WalkFrames;

    public Vector2 FrameSize => _poses?.Active == true
        ? new Vector2(_sprite!.Texture.GetWidth() / _sprite.Hframes, _sprite.Texture.GetHeight())
        : Texture == null ? new Vector2(16, 40) : new Vector2(Texture.GetWidth() / Frames, Texture.GetHeight());

    public Vector2 HeadPosition => _poses?.Active == true
        ? ToGlobal(_poses.HeadOffset - new Vector2(0, 7))
        : GlobalPosition - new Vector2(0, FrameSize.Y * GlobalScale.Y + 3);

    public bool Talking
    {
        set { _talking = value; _talkTime = 0; UpdateFrame(); }
    }

    public override void _Ready()
    {
        if (Texture == null) return;
        Frames = FitFrames(Texture.GetWidth(), Frames);
        _sprite = new Sprite2D
        {
            Texture = Texture,
            Hframes = Frames,
            Centered = false,
            FlipH = FlipH,
            Offset = new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y + Baseline),
        };
        AddChild(_sprite);
        _poses = new PosePlayback(_sprite);
        ApplyDepthScale();
    }

    /// <summary>
    /// The 3-frame strips (idle + two talk frames) are usually placed with the 11-frame default; slicing them as 11
    /// shows thin slivers that change with every talk frame. Fall back to a frame count that divides the strip.
    /// </summary>
    public static int FitFrames(int width, int frames)
    {
        if (frames > 0 && width % frames == 0) return frames;
        foreach (int f in new[] { WalkStart + WalkFrames, 3, 2 })
            if (width % f == 0) return f;
        return 1;
    }

    private void ApplyDepthScale()
    {
        if (!DepthScale) return;
        for (Node? n = GetParent(); n != null; n = n.GetParent())
            if (n is Room r) { Scale = Vector2.One * r.ScaleAt(Position.Y); return; }
    }

    public override void _Process(double delta)
    {
        _poses?.Process(delta);
        if (_talking)
        {
            _talkTime += delta;
            UpdateFrame();
        }
        if (_moveTarget is { } target)
        {
            var from = Position;
            Position = Position.MoveToward(target, _moveSpeed * (float)delta);
            _walkDistance += from.DistanceTo(Position) / Mathf.Max(Scale.Y, 0.01f);
            ApplyDepthScale();
            if (Position.DistanceTo(target) < 0.01f)
            {
                _moveTarget = null;
                _moveDone?.TrySetResult();
            }
            UpdateFrame();
        }
    }

    /// <summary>Walks the actor in a straight line to a point (room coordinates). Simple, but enough for cutscenes.</summary>
    public Task MoveTo(Vector2 target, float speed = 40)
    {
        if (_poses?.Active == true) SetPose(null);
        _moveDone?.TrySetResult();
        _moveDone = new TaskCompletionSource();
        _moveTarget = target;
        _moveSpeed = speed;
        _walkDistance = 0;
        if (_sprite != null && Mathf.Abs(target.X - Position.X) > 1)
            FaceLeft(target.X < Position.X);
        return _moveDone.Task;
    }

    /// <summary>Turns the actor to face screen-left (true) or screen-right (false) without moving.</summary>
    public void FaceLeft(bool left)
    {
        FlipH = left;
        if (_sprite != null) _sprite.FlipH = left;
        if (_poses?.Active == true) _poses.Flipped = left;
    }

    public void SetPose(string? id)
    {
        if (_sprite == null || _poses == null)
            throw new System.InvalidOperationException($"Actor {Id} has no sprite.");
        _moveTarget = null;
        _moveDone?.TrySetResult();
        if (id != null) { _poses.Hold(id, FlipH); return; }
        _poses.Clear();
        _sprite.Texture = Texture;
        _sprite.Hframes = Frames;
        _sprite.Vframes = 1;
        _sprite.Offset = new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y + Baseline);
        UpdateFrame();
    }

    public Task<bool> PlayPose(string id)
    {
        if (_poses == null) throw new System.InvalidOperationException($"Actor {Id} has no sprite.");
        _moveTarget = null;
        _moveDone?.TrySetResult();
        return _poses.Play(id, FlipH);
    }

    public override void _ExitTree()
    {
        _poses?.Clear();
        _moveDone?.TrySetCanceled();
    }

    /// <summary>Swaps the actor's sprite (e.g. a single-frame pose like lying on the ground); feet stay where they are.</summary>
    public void SetTexture(Texture2D texture, int frames = 1)
    {
        _poses?.Clear();
        Texture = texture;
        Frames = frames;
        _talking = false;
        if (_sprite == null) { _Ready(); return; }
        _sprite.Texture = texture;
        _sprite.Hframes = frames;
        _sprite.Vframes = 1;
        _sprite.Frame = 0;
        _sprite.Offset = new Vector2(-Mathf.Floor(FrameSize.X / 2), -FrameSize.Y + Baseline);
    }

    private static readonly int[] TalkCycle = { 1, 2, 1, 0, 2, 1, 2, 0 };

    private void UpdateFrame()
    {
        if (_sprite == null || _poses?.Active == true) return;
        if (_moveTarget != null && CanWalk)
        {
            _sprite.Frame = WalkStart + (1 + (int)(_walkDistance / StridePerFrame)) % WalkFrames;
            return;
        }
        if (!_talking || Frames < 2) { _sprite.Frame = 0; return; }
        int tick = (int)(_talkTime * 7);
        _sprite.Frame = Frames >= 3 ? TalkCycle[tick % TalkCycle.Length] : (tick % 2 == 0 ? 1 : 0);
    }

    private Rect2 SpriteRect => _poses?.Active == true ? _poses.Bounds
        : new(new Vector2(-Mathf.Floor(FrameSize.X / 2) + 8, -FrameSize.Y + Baseline + 8), FrameSize - new Vector2(16, 8));

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
