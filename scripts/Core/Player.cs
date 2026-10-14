using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// The playable character (Micah, or Daniel in the prologue). Sprite sheet (64x96 frames, 10 columns, painted by
/// tools/art/figure.py): row 0: 3/4 idle, side walk x8, 3/4 talk · row 1 front 3/4: idle, walk x6, talk A, talk B ·
/// row 2 back 3/4: idle, walk x6. Horizontal frames face right and are flipped for left. Position is the feet, which sit
/// <see cref="Baseline"/> pixels above the bottom of each frame.
/// </summary>
public partial class Player : Node2D, ISpeaker
{
    private const int Cols = 10;
    private const int Baseline = 3;
    private static readonly Vector2 FrameSize = new(64, 96);
    /// <summary>Ground covered by one side-walk frame at scale 1 (an 8-frame cycle is two steps of ~0.39 x height).</summary>
    private const float SideStridePerFrame = 7.7f;
    private const float FrontWalkFps = 11f;

    [Export] public float Speed = 90f;
    public Color SpeechColor { get; set; } = new("f0e0a0");

    private Sprite2D _sprite = null!;
    private Facing _facing = Facing.Right;
    private readonly Queue<Vector2> _path = new();
    private TaskCompletionSource<bool>? _walkDone;
    private double _animTime;
    private bool _talking;
    private PosePlayback _poses = null!;
    public PosePlayback Poses => _poses;

    public bool IsWalking => _path.Count > 0;
    public Facing Facing => _facing;
    /// <summary>Speech anchor: a few pixels above the top of the head (or hat), which sits ~83px above the feet.</summary>
    public Vector2 HeadPosition => _poses?.Active == true
        ? ToGlobal(_poses.HeadOffset - new Vector2(0, 7))
        : GlobalPosition - new Vector2(0, 92 * Scale.Y);

    public bool Talking
    {
        get => _talking;
        set { _talking = value; _animTime = 0; }
    }

    /// <summary>Who the player controls: "micah" (1927) or "daniel" (the present-day prologue).</summary>
    public string Character { get; private set; } = "micah";

    public override void _Ready()
    {
        _sprite = new Sprite2D
        {
            Hframes = Cols,
            Vframes = 3,
            Centered = false,
            Offset = new Vector2(-FrameSize.X / 2, -FrameSize.Y + Baseline),
        };
        AddChild(_sprite);
        _poses = new PosePlayback(_sprite);
        SetCharacter(Character);
    }

    /// <summary>Swaps the sprite sheet (assets/art/sprites/{id}.png) and speech colour.</summary>
    public void SetCharacter(string id)
    {
        Character = id;
        SpeechColor = id == "daniel" ? new Color("b8d8e8") : new Color("f0e0a0");
        if (_sprite == null) return;
        _poses.Clear();
        _sprite.Texture = GD.Load<Texture2D>($"res://assets/art/sprites/{id}.png");
        _sprite.Hframes = Cols;
        _sprite.Vframes = 3;
        _sprite.Offset = new Vector2(-FrameSize.X / 2, -FrameSize.Y + Baseline);
        UpdateFrame();
    }

    /// <summary>
    /// Holds a single-frame pose (assets/art/sprites/{id}.png, one 64x96 frame, e.g. "micah_kneel") instead of the
    /// sheet animation. Null goes back to the normal sheet.
    /// </summary>
    public void SetPose(string? id)
    {
        if (id == null) { SetCharacter(Character); return; }
        Stop();
        _poses.Hold(id, _facing == Facing.Left);
    }

    /// <summary>The held or playing pose, or null while the normal sheet is shown.</summary>
    public string? PoseName => _poses.Active ? _poses.Action : null;

    public Task<bool> PlayPose(string id)
    {
        Stop();
        return _poses.Play(id, _facing == Facing.Left);
    }

    public override void _ExitTree() => _poses?.Clear();

    /// <summary>Walks along a path. Resolves to false if interrupted by another walk.</summary>
    public Task<bool> WalkPath(IEnumerable<Vector2> points)
    {
        if (_poses.Active) SetCharacter(Character);
        _walkDone?.TrySetResult(false);
        _path.Clear();
        foreach (var p in points) _path.Enqueue(p);
        _walkDone = new TaskCompletionSource<bool>();
        if (_path.Count == 0) _walkDone.TrySetResult(true);
        return _walkDone.Task;
    }

    public void Stop()
    {
        if (_poses?.Active == true) SetCharacter(Character);
        _path.Clear();
        _walkDone?.TrySetResult(false);
    }

    public void Face(Facing f)
    {
        if (f != Facing.Auto) _facing = f;
        UpdateFrame();
    }

    public void FaceTowards(Vector2 p)
    {
        var d = p - GlobalPosition;
        if (Mathf.Abs(d.X) >= Mathf.Abs(d.Y) * 0.6f) Face(d.X < 0 ? Facing.Left : Facing.Right);
        else Face(d.Y < 0 ? Facing.Up : Facing.Down);
    }

    public void Teleport(Vector2 p, Facing f = Facing.Auto)
    {
        Stop();
        Position = p;
        Face(f);
        UpdateScale();
    }

    public override void _Process(double delta)
    {
        _poses.Process(delta);
        _animTime += delta;
        if (_path.Count > 0)
        {
            var target = _path.Peek();
            var dir = target - Position;
            var step = Speed * Scale.Y * (float)delta;
            if (Mathf.Abs(dir.X) > 0.5f || Mathf.Abs(dir.Y) > 0.5f)
            {
                if (Mathf.Abs(dir.X) >= Mathf.Abs(dir.Y) * 0.8f) _facing = dir.X < 0 ? Facing.Left : Facing.Right;
                else _facing = dir.Y < 0 ? Facing.Up : Facing.Down;
            }
            var len = dir.Length();
            var stepLen = step * (1f - 0.4f * Mathf.Abs(dir.Y) / Mathf.Max(len, 0.0001f));
            if (len <= stepLen)
            {
                Position = target;
                _path.Dequeue();
                if (_path.Count == 0) _walkDone?.TrySetResult(true);
            }
            else Position += dir / len * stepLen;
            UpdateScale();
        }
        UpdateFrame();
    }

    private void UpdateScale()
    {
        for (var n = GetParent(); n != null; n = n.GetParent())
            if (n is Room r) { Scale = Vector2.One * r.ScaleAt(Position.Y); return; }
    }

    private static readonly int[] TalkFrontCols = { 7, 8, 7, 0 };

    private void UpdateFrame()
    {
        if (_sprite == null) return;
        if (_poses.Active) { _poses.Flipped = _facing == Facing.Left; return; }
        bool walking = _path.Count > 0;
        int row, col;
        switch (_facing)
        {
            case Facing.Up:
                row = 2;
                col = walking ? 1 + (int)(_animTime * FrontWalkFps) % 6 : 0;
                break;
            case Facing.Down:
                row = 1;
                col = walking ? 1 + (int)(_animTime * FrontWalkFps) % 6 : (_talking ? TalkFrontCols[(int)(_animTime * 7) % 4] : 0);
                break;
            default:
                row = 0;
                col = walking ? 1 + (int)(_animTime * Speed / SideStridePerFrame) % 8
                    : (_talking && (int)(_animTime * 7) % 2 == 0 ? 9 : 0);
                break;
        }
        _sprite.FlipH = _facing == Facing.Left;
        _sprite.Frame = row * Cols + col;
    }
}
