using Godot;
using System.Collections.Generic;
using System.Globalization;

namespace Repentance;

/// <summary>
/// A background figure cut from the painting as a horizontal strip (<see cref="Sprite2D.Hframes"/>): it rests on
/// frame 0 and, every <see cref="MinRest"/>–<see cref="MaxRest"/> seconds, plays <see cref="Sequence"/> once, e.g.
/// a man raising his cigarette to his mouth. Seeded, so recorded frames are reproducible.
/// </summary>
[GlobalClass]
public partial class IdleStrip : Sprite2D
{
    /// <summary>Comma-separated "frame:seconds" steps played after each rest, before returning to frame 0.</summary>
    [Export] public string Sequence = "";
    [Export] public float MinRest = 4f;
    [Export] public float MaxRest = 7f;
    [Export] public int Seed = 1;

    private readonly List<(int Frame, float Seconds)> _steps = new();
    private readonly RandomNumberGenerator _rng = new();
    private int _step = -1;
    private float _left;

    public override void _Ready()
    {
        _rng.Seed = (ulong)Seed;
        foreach (var part in Sequence.Split(',', System.StringSplitOptions.RemoveEmptyEntries | System.StringSplitOptions.TrimEntries))
        {
            var bits = part.Split(':');
            if (bits.Length == 2 && int.TryParse(bits[0], out var frame) && frame >= 0 && frame < Hframes * Vframes
                && float.TryParse(bits[1], NumberStyles.Float, CultureInfo.InvariantCulture, out var seconds) && seconds > 0)
                _steps.Add((frame, seconds));
            else
                GD.PushWarning($"{Name}: bad IdleStrip step '{part}'");
        }
        Rest();
    }

    private void Rest()
    {
        _step = -1;
        Frame = 0;
        _left = _rng.RandfRange(MinRest, Mathf.Max(MinRest, MaxRest));
    }

    public override void _Process(double delta)
    {
        if (_steps.Count == 0) return;
        _left -= (float)delta;
        while (_left <= 0)
        {
            if (++_step >= _steps.Count)
            {
                Rest();
                return;
            }
            Frame = _steps[_step].Frame;
            _left += _steps[_step].Seconds;
        }
    }
}
