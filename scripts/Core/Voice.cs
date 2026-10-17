using Godot;

namespace Repentance;

/// <summary>
/// An off-screen speaker (someone shouting from downstairs, a radio...). Place it where the
/// text should appear; dialogue lines "ID: text" are routed here when <see cref="Id"/> matches.
/// </summary>
[GlobalClass]
public partial class Voice : Node2D, ISpeaker
{
    [Export] public string Id = "";
    [Export] public Color SpeechColor { get; set; } = Colors.White;
    /// <summary>Optional lips painted over the room (closed, open, half open) that move while this voice speaks.</summary>
    [Export] public Sprite2D? Mouth;

    public Vector2 HeadPosition => GlobalPosition;

    private static readonly int[] TalkCycle = { 1, 2, 1, 0, 2, 1, 2, 0 };
    private bool _talking;
    private double _talkTime;

    public bool Talking
    {
        set
        {
            _talking = value;
            _talkTime = 0;
            UpdateMouth();
        }
    }

    public override void _Process(double delta)
    {
        if (!_talking) return;
        _talkTime += delta;
        UpdateMouth();
    }

    private void UpdateMouth()
    {
        if (Mouth is not { Hframes: >= 3 } mouth) return;
        mouth.Frame = _talking ? TalkCycle[(int)(_talkTime * 7) % TalkCycle.Length] : 0;
    }
}
