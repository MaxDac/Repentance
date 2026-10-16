using Godot;

namespace Repentance;

/// <summary>
/// Film mode's curtain while it fast-forwards to the chapter given with <c>--from</c>: a black screen with a caption,
/// drawn over the HUD and every room, so the skipped beats play unseen.
/// </summary>
public partial class FilmCover : CanvasLayer
{
    private readonly string _text;
    private Control _root = null!;

    public FilmCover(string text)
    {
        _text = text;
        Layer = 100;
        Name = "FilmCover";
    }

    public override void _Ready()
    {
        ProcessMode = ProcessModeEnum.Always;
        _root = new Control { MouseFilter = Control.MouseFilterEnum.Ignore };
        _root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        AddChild(_root);
        var black = new ColorRect { Color = new Color(0, 0, 0, 1), MouseFilter = Control.MouseFilterEnum.Ignore };
        black.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _root.AddChild(black);
        _root.AddChild(new Label
        {
            Text = _text,
            Position = new Vector2(0, Hud.ScreenH / 2f - 8),
            Size = new Vector2(Hud.ScreenW, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Hud.Font, FontSize = 16, FontColor = Hud.VerbHover },
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });
    }

    /// <summary>Fades the curtain out (in real time, whatever the clock) and frees it.</summary>
    public void Lift(double seconds = 0.6)
    {
        if (!IsInsideTree())
        {
            QueueFree();
            return;
        }
        var tween = CreateTween().SetIgnoreTimeScale().SetPauseMode(Tween.TweenPauseMode.Process);
        tween.TweenProperty(_root, "modulate:a", 0.0, seconds);
        tween.TweenCallback(Callable.From(QueueFree));
    }
}
