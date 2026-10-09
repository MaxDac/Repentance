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

    public Vector2 HeadPosition => GlobalPosition;

    public bool Talking { set { } }
}
