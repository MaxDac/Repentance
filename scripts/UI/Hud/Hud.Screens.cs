using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Full-screen layers: the title, fades, captions and the pause banner.</summary>
public partial class Hud
{
    private const float CaptionTop = 126;
    private const int CaptionFontSize = 22;
    private const float CaptionSubGap = 26;
    /// <summary>The Art Deco face of the captions over black (chapter cards, "Later that night").</summary>
    public static Font CaptionFont { get; private set; } = null!;

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
            FollowsStory = false,
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

        CaptionFont = GD.Load<Font>("res://assets/fonts/PoiretOne-Regular.ttf");
        _caption = new Label
        {
            Position = new Vector2(0, CaptionTop),
            Size = new Vector2(ScreenW, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = CaptionFont, FontSize = CaptionFontSize, FontColor = VerbHover },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_caption);

        _captionSub = new Label
        {
            Position = new Vector2(0, CaptionTop + CaptionSubGap),
            Size = new Vector2(ScreenW, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = CaptionFont, FontSize = CaptionFontSize, FontColor = VerbHover },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_captionSub);

        VerseFont = GD.Load<Font>("res://assets/fonts/IMFellEnglish-Regular.ttf");
        _verses = new VBoxContainer { MouseFilter = Control.MouseFilterEnum.Ignore, Visible = false };
        _verses.AddThemeConstantOverride("separation", 2);
        root.AddChild(_verses);
    }

    private const int VerseFontSize = 22;
    private VBoxContainer _verses = null!;
    /// <summary>The printed-prayer-book serif of the verses over black.</summary>
    public static Font VerseFont { get; private set; } = null!;
    public bool VersesVisible => _verses.Visible;
    /// <summary>The verse lines revealed so far, one per line.</summary>
    public string VersesText => string.Join("\n", _verses.GetChildren().OfType<Label>().Select(l => l.Text));
    public bool VersesFading => _verses.Modulate.A < 1 || _verses.GetChildren().OfType<Label>().Any(l => l.Modulate.A is > 0 and < 1);

    /// <summary>
    /// Verses over black in <see cref="VerseFont"/>, centred: each line fades in under the previous ones over
    /// <paramref name="fadeSeconds"/>, the block holds for <paramref name="holdSeconds"/>, then fades out as one.
    /// </summary>
    public async Task ShowVerses(IReadOnlyList<string> lines, double fadeSeconds, double holdSeconds)
    {
        foreach (var child in _verses.GetChildren()) child.Free();
        int size = VerseFontSize;
        while (size > 8 && lines.Max(l => VerseFont.GetStringSize(l, HorizontalAlignment.Left, -1, size).X) > ScreenW - 16)
            size -= 2;
        float lineHeight = VerseFont.GetHeight(size);
        float height = lineHeight * lines.Count + 2 * (lines.Count - 1);
        _verses.Position = new Vector2(0, Mathf.Round(CaptionTop + 8 - height / 2));
        _verses.Size = new Vector2(ScreenW, height);
        _verses.Modulate = Colors.White;
        _verses.Visible = true;
        var settings = new LabelSettings { Font = VerseFont, FontSize = size, FontColor = VerbHover };
        foreach (var line in lines)
        {
            var label = new Label
            {
                Text = line,
                HorizontalAlignment = HorizontalAlignment.Center,
                LabelSettings = settings,
                MouseFilter = Control.MouseFilterEnum.Ignore,
                Modulate = new Color(1, 1, 1, 0),
            };
            _verses.AddChild(label);
            await TweenAlpha(label, 1, fadeSeconds);
        }
        await Timers.Wait(this, holdSeconds);
        await TweenAlpha(_verses, 0, fadeSeconds);
        _verses.Visible = false;
        foreach (var child in _verses.GetChildren()) child.QueueFree();
    }

    private async Task TweenAlpha(CanvasItem item, float alpha, double seconds)
    {
        var tw = CreateTween();
        tw.SetPauseMode(Tween.TweenPauseMode.Stop);
        tw.TweenProperty(item, "modulate:a", alpha, seconds);
        await ToSignal(tw, Tween.SignalName.Finished);
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
        _caption.Modulate = Colors.White;
        _caption.Position = new Vector2(0, CaptionTop);
        _caption.Size = new Vector2(ScreenW, 16);
        _caption.LabelSettings.FontSize = CaptionFitSize(text);
        _caption.Text = text ?? "";
        _caption.Visible = text != null;
        ShowCaptionSub(null);
    }

    /// <summary>A second caption line under the one already showing, as in "Chicago, 1927." over "First Interlude".</summary>
    public void ShowCaptionSub(string? text)
    {
        _captionSub.Modulate = Colors.White;
        _captionSub.LabelSettings.FontSize = CaptionFitSize(text);
        _captionSub.Text = text ?? "";
        _captionSub.Visible = text != null;
    }

    /// <summary>The caption size, stepped down until the line fits the screen with a margin.</summary>
    private static int CaptionFitSize(string? text)
    {
        int size = CaptionFontSize;
        while (text != null && size > 8 && CaptionFont.GetStringSize(text, HorizontalAlignment.Left, -1, size).X > ScreenW - 16)
            size -= 2;
        return size;
    }

    private const double CaptionFadeSeconds = 0.8;

    private async Task TweenCaption(float alpha, double seconds, params CanvasItem[] items)
    {
        var tw = CreateTween();
        tw.SetPauseMode(Tween.TweenPauseMode.Stop);
        tw.SetParallel();
        foreach (var item in items) tw.TweenProperty(item, "modulate:a", alpha, seconds);
        await ToSignal(tw, Tween.SignalName.Finished);
    }

    /// <summary>Shows <paramref name="text"/> as the caption, fading it in from transparent.</summary>
    public async Task FadeCaptionIn(string text, double seconds = CaptionFadeSeconds)
    {
        ShowCaption(text);
        _caption.Modulate = new Color(1, 1, 1, 0);
        await TweenCaption(1, seconds, _caption);
    }

    /// <summary>Shows <paramref name="text"/> under the current caption, fading it in from transparent.</summary>
    public async Task FadeCaptionSubIn(string text, double seconds = CaptionFadeSeconds)
    {
        ShowCaptionSub(text);
        _captionSub.Modulate = new Color(1, 1, 1, 0);
        await TweenCaption(1, seconds, _captionSub);
    }

    /// <summary>Fades the caption and its second line out, then hides them.</summary>
    public async Task FadeCaptionOut(double seconds = CaptionFadeSeconds)
    {
        if (!_caption.Visible && !_captionSub.Visible) return;
        await TweenCaption(0, seconds, _caption, _captionSub);
        ShowCaption(null);
    }

    /// <summary>
    /// Act change over black: <paramref name="endOfAct"/> fades in and out, the screen stays empty for a beat, then
    /// <paramref name="title"/> fades in with <paramref name="subtitle"/> under it two seconds later, and both fade out.
    /// The fade layer must already be black.
    /// </summary>
    public async Task ActCards(string endOfAct, string? title = null, string? subtitle = null)
    {
        await FadeCaptionIn(endOfAct);
        await Timers.Wait(this, 2.0);
        await FadeCaptionOut();
        if (title == null) return;
        await Timers.Wait(this, 0.7);
        await FadeCaptionIn(title);
        if (subtitle != null)
        {
            await Timers.Wait(this, 2.0);
            await FadeCaptionSubIn(subtitle);
        }
        await Timers.Wait(this, 2.2);
        await FadeCaptionOut();
    }
}
