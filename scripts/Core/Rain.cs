using Godot;

namespace Repentance;

/// <summary>Falling rain drawn as thin pixel streaks over a room, in front of the characters.</summary>
[GlobalClass]
public partial class Rain : Node2D
{
    [Export] public int Drops = 150;
    [Export] public Vector2 Area = new(480, 270);
    [Export] public float Speed = 240f;
    [Export] public Color DropColor = new(0.62f, 0.70f, 0.86f, 0.42f);

    private static readonly Vector2 Streak = new(-1, 4);
    private Vector2[] _drops = System.Array.Empty<Vector2>();
    private float[] _speeds = System.Array.Empty<float>();
    private readonly RandomNumberGenerator _rng = new() { Seed = 641 };

    public override void _Ready()
    {
        _drops = new Vector2[Drops];
        _speeds = new float[Drops];
        for (int i = 0; i < Drops; i++)
        {
            _drops[i] = new Vector2(_rng.RandfRange(0, Area.X), _rng.RandfRange(0, Area.Y));
            _speeds[i] = Speed * _rng.RandfRange(0.8f, 1.2f);
        }
    }

    public override void _Process(double delta)
    {
        for (int i = 0; i < _drops.Length; i++)
        {
            var d = _drops[i] + new Vector2(-0.25f, 1f) * _speeds[i] * (float)delta;
            if (d.Y > Area.Y)
                d = new Vector2(_rng.RandfRange(0, Area.X + 20), -Streak.Y);
            if (d.X < -2)
                d.X += Area.X + 4;
            _drops[i] = d;
        }
        QueueRedraw();
    }

    public override void _Draw()
    {
        foreach (var d in _drops)
        {
            var p = d.Floor();
            DrawLine(p, p + Streak, DropColor);
        }
    }
}
