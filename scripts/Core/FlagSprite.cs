using Godot;

namespace Repentance;

/// <summary>A sprite that shows/hides itself based on story flags (e.g. an opened drawer overlay).</summary>
[GlobalClass]
public partial class FlagSprite : Sprite2D
{
    [Export] public string ShowIfFlags = "";
    [Export] public string HideIfFlags = "";

    public void Refresh() => Visible = FlagRules.Evaluate(ShowIfFlags, HideIfFlags);
}
