using Godot;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Full-screen layers: the title, fades, captions and the pause banner.</summary>
public partial class Hud
{
    private void BuildTitle(Control root)
    {
        _title = new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/title.png"),
            Visible = false,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        root.AddChild(_title);
        // rain falls over the skyline and the river, behind the gold plate
        _title.AddChild(new Rain
        {
            Name = "TitleRain",
            Areas = new() { new Rect2(0, 0, ScreenW, ScreenH) },
            Density = 2.6f,
            Speed = 300f,
            Slant = -0.22f,
            Length = 6,
            Layers = 3,
            Tint = new Color(0.58f, 0.66f, 0.86f, 0.5f),
            SplashAreas = new() { new Rect2(0, 210, ScreenW, ScreenH - 210) },
            SplashRate = 4f,
            Seed = 1927,
        });
        _title.AddChild(new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/title_logo.png"),
            MouseFilter = Control.MouseFilterEnum.Ignore,
        });
    }

    private void BuildFadeAndCaption(Control root)
    {
        _fade = new ColorRect { Color = new Color(0, 0, 0, 1), MouseFilter = Control.MouseFilterEnum.Ignore };
        _fade.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        root.AddChild(_fade);

        _caption = new Label
        {
            Position = new Vector2(0, 126),
            Size = new Vector2(ScreenW, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Font, FontSize = 16, FontColor = VerbHover },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_caption);
    }

    private void BuildPause(Control root)
    {
        _pause = new Control
        {
            Visible = false,
            MouseFilter = Control.MouseFilterEnum.Stop,
            ProcessMode = ProcessModeEnum.Always,
        };
        _pause.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        var pauseLabel = MakeOutlinedLabel(VerbHover);
        pauseLabel.Text = "Paused - Space to resume";
        pauseLabel.HorizontalAlignment = HorizontalAlignment.Center;
        pauseLabel.Position = new Vector2(0, 4);
        pauseLabel.Size = new Vector2(ScreenW, 12);
        _pause.AddChild(pauseLabel);
        root.AddChild(_pause);
    }

    public void ShowPause(bool show) => _pause.Visible = show;

    public async Task Fade(float alpha, double seconds)
    {
        var tw = CreateTween();
        tw.SetPauseMode(Tween.TweenPauseMode.Stop);
        tw.TweenProperty(_fade, "color:a", alpha, seconds);
        await ToSignal(tw, Tween.SignalName.Finished);
    }

    public void ShowTitle(bool show)
    {
        _title.Visible = show;
        _title.MouseFilter = show ? Control.MouseFilterEnum.Stop : Control.MouseFilterEnum.Ignore;
    }

    /// <summary>Large centred text drawn above the fade layer (chapter cards, "To be continued...").</summary>
    public void ShowCaption(string? text)
    {
        _caption.Text = text ?? "";
        _caption.Visible = text != null;
    }
}
