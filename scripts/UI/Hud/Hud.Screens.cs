using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Full-screen layers: the title, fades, captions and the pause banner.</summary>
public partial class Hud
{
    private const float CaptionTop = 126;
    private const int CaptionFontSize = 16;

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
            Position = new Vector2(0, CaptionTop),
            Size = new Vector2(ScreenW, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Font, FontSize = CaptionFontSize, FontColor = VerbHover },
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
        _caption.Position = new Vector2(0, CaptionTop);
        _caption.Size = new Vector2(ScreenW, 16);
        _caption.LabelSettings.FontSize = CaptionFontSize;
        _caption.Text = text ?? "";
        _caption.Visible = text != null;
    }

    /// <summary>
    /// The first <paramref name="shown"/> of <paramref name="lines"/>, one under the other. The block is laid out (centred,
    /// and at a size where the widest line fits) for all of them, so revealing the next line never moves the earlier ones.
    /// </summary>
    public void ShowCaptionLines(IReadOnlyList<string> lines, int shown)
    {
        int size = CaptionFontSize;
        while (size > 8 && lines.Max(l => Font.GetStringSize(l, HorizontalAlignment.Left, -1, size).X) > ScreenW - 16)
            size -= 8;
        var settings = _caption.LabelSettings;
        settings.FontSize = size;
        float lineHeight = Font.GetHeight(size) + settings.LineSpacing;
        float height = lineHeight * lines.Count;
        _caption.Position = new Vector2(0, Mathf.Round(CaptionTop + 8 - height / 2));
        _caption.Size = new Vector2(ScreenW, height);
        _caption.Text = string.Join("\n", lines.Take(Mathf.Clamp(shown, 0, lines.Count)));
        _caption.Visible = true;
    }
}
