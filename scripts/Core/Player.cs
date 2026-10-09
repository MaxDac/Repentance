using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Micah. Sprite sheet (40x80 frames, 8 columns):
/// row 0 side view: idle, walk x6, talk · row 1 front: idle, walk x4, talk · row 2 back: idle, walk x4.
/// Side frames face right and are flipped for left. Position is the feet.
/// </summary>
public partial class Player : Node2D, ISpeaker
{
    private const int Cols = 8;
    private static readonly Vector2 FrameSize = new(40, 80);

    [Export] public float Speed = 62f;
    public Color SpeechColor { get; set; } = new("f0e0a0");

    private Sprite2D _sprite = null!;
    private Facing _facing = Facing.Right;
    private readonly Queue<Vector2> _path = new();
    private TaskCompletionSource<bool>? _walkDone;
    private double _animTime;
    private bool _talking;

    public bool IsWalking => _path.Count > 0;
    public Facing Facing => _facing;
    public Vector2 HeadPosition => GlobalPosition - new Vector2(0, 74 * Scale.Y);

    public bool Talking
    {
        set { _talking = value; _animTime = 0; }
    }

    public override void _Ready()
    {
        _sprite = new Sprite2D
        {
            Texture = GD.Load<Texture2D>("res://assets/art/sprites/micah.png"),
            Hframes = Cols,
            Vframes = 3,
            Centered = false,
            Offset = new Vector2(-FrameSize.X / 2, -FrameSize.Y + 1),
        };
        AddChild(_sprite);
        UpdateFrame();
    }

    /// <summary>Walks along a path. Resolves to false if interrupted by another walk.</summary>
    public Task<bool> WalkPath(IEnumerable<Vector2> points)
    {
        _walkDone?.TrySetResult(false);
        _path.Clear();
        foreach (var p in points) _path.Enqueue(p);
        _walkDone = new TaskCompletionSource<bool>();
        if (_path.Count == 0) _walkDone.TrySetResult(true);
        return _walkDone.Task;
    }

    public void Stop()
    {
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

    private void UpdateFrame()
    {
        if (_sprite == null) return;
        bool walking = _path.Count > 0;
        int row, col;
        switch (_facing)
        {
            case Facing.Up:
                row = 2;
                col = walking ? 1 + (int)(_animTime * 7) % 4 : 0;
                break;
            case Facing.Down:
                row = 1;
                col = walking ? 1 + (int)(_animTime * 7) % 4 : (_talking && (int)(_animTime * 7) % 2 == 0 ? 5 : 0);
                break;
            default:
                row = 0;
                col = walking ? 1 + (int)(_animTime * 10) % 6 : (_talking && (int)(_animTime * 7) % 2 == 0 ? 7 : 0);
                break;
        }
        _sprite.FlipH = _facing == Facing.Left;
        _sprite.Frame = row * Cols + col;
    }
}
