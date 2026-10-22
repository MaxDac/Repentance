using Godot;
using System;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Close-up insets and full-screen pictures.</summary>
public partial class Hud
{
    private void BuildImage(Control root)
    {
        _image = new TextureRect { Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
        _image.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _image.GuiInput += e =>
        {
            if (e is not InputEventMouseButton { Pressed: true }) return;
            // while a held picture is being described, a click only skips the line
            if (_imageHeld) Game.Instance.SkipSpeech();
            else CloseImage();
        };
        root.AddChild(_image);
    }

    /// <summary>True from <see cref="ShowCloseUp"/> until <see cref="HideCloseUp"/>, even while it fades.</summary>
    public bool InsetVisible => _insetShown;
    /// <summary>The picture currently framed (its file name), e.g. "stage_closeup_clothed".</summary>
    public string InsetName => _inset.Texture?.ResourcePath.GetFile().GetBaseName() ?? "";
    /// <summary>The close-up shown, or null.</summary>
    public CloseUp? CurrentCloseUp => _insetShown ? _closeUp : null;

    /// <summary>Lets close-ups follow the player's settings: a variant swaps in place when they change.</summary>
    public void BindSettings(GameSettings settings)
    {
        if (_settings != null) _settings.Changed -= RefreshCloseUp;
        _settings = settings;
        _settings.Changed += RefreshCloseUp;
        Menu.BindSettings(settings);
    }

    public override void _ExitTree()
    {
        if (_settings != null) _settings.Changed -= RefreshCloseUp;
    }

    private void RefreshCloseUp()
    {
        if (_insetShown && _closeUp != null) ShowInset(LoadCloseUp(_closeUp), 0);
    }

    private Texture2D LoadCloseUp(CloseUp closeUp) => GD.Load<Texture2D>(closeUp.TexturePath(_settings));

    /// <summary>
    /// Frames a close-up centred over the scene without blocking it: the room, speech and choices stay live around
    /// and above it, and speech moves to the panel's bottom edge. A <see cref="CloseUp.Photo"/> sits on the left
    /// instead, with speech beside it; a <see cref="CloseUp.CaptionsBelow"/> strip sits along the top, with captions
    /// under it. Stays until <see cref="HideCloseUp"/> or the next room change. Showing the one
    /// already up does nothing.
    /// </summary>
    public void ShowCloseUp(CloseUp closeUp, double? fadeIn = null)
    {
        if (_insetShown && _closeUp == closeUp) return;
        _closeUp = closeUp;
        ShowInset(LoadCloseUp(closeUp), fadeIn ?? closeUp.FadeIn);
    }

    public void HideCloseUp(double? fadeOut = null)
    {
        double seconds = fadeOut ?? _closeUp?.FadeOut ?? 0.3;
        _closeUp = null;
        HideInset(seconds);
    }

    /// <summary>Gap between a photo and the left edge of the screen, and between it and the speech beside it.</summary>
    private const int PhotoMargin = 32;

    /// <summary>Top of a comic-strip panel, leaving the rest of the screen for its captions.</summary>
    private const int CaptionPanelTop = 4;

    private void ShowInset(Texture2D texture, double seconds)
    {
        _insetTween?.Kill();
        _inset.Texture = texture;
        var size = texture.GetSize();
        _inset.Size = size;
        _inset.Position = ((new Vector2(ScreenW, ScreenH) - size) / 2).Floor();
        if (_closeUp?.Photo == true) _inset.Position = _inset.Position with { X = PhotoMargin };
        if (_closeUp?.CaptionsBelow == true) _inset.Position = _inset.Position with { Y = CaptionPanelTop };
        _inset.Visible = true;
        _insetShown = true;
        _inset.Modulate = new Color(1, 1, 1, seconds > 0 ? 0 : 1);
        if (seconds <= 0) return;
        _insetTween = CreateTween();
        _insetTween.TweenProperty(_inset, "modulate:a", 1f, seconds);
    }

    private void HideInset(double seconds)
    {
        _insetTween?.Kill();
        _insetTween = null;
        _insetShown = false;
        if (!_inset.Visible) return;
        if (seconds <= 0)
        {
            _inset.Visible = false;
            return;
        }
        _insetTween = CreateTween();
        _insetTween.TweenProperty(_inset, "modulate:a", 0f, seconds);
        _insetTween.TweenCallback(Callable.From(() => _inset.Visible = false));
    }

    public bool ImageVisible => _image.Visible;
    private bool _imageHeld;

    /// <summary>Shows a full-screen picture (a close-up) until the player clicks.</summary>
    public Task ShowImage(Texture2D texture)
    {
        _imageTcs?.TrySetResult();
        _image.Texture = texture;
        _image.Visible = true;
        _image.MouseFilter = Control.MouseFilterEnum.Stop;
        _interface.Visible = false;
        _imageTcs = new TaskCompletionSource();
        return _imageTcs.Task;
    }

    /// <summary>
    /// Shows a full-screen picture while the given lines are spoken over it: clicks skip the lines, and only once
    /// they are done does the next click close the picture.
    /// </summary>
    public async Task ShowImageWithLines(Texture2D texture, Func<Task> lines)
    {
        var closed = ShowImage(texture);
        _imageHeld = true;
        _speech.ZIndex = 1;
        try { await lines(); }
        finally
        {
            _imageHeld = false;
            _speech.ZIndex = 0;
        }
        await closed;
    }

    public bool ImageHeld => _imageHeld;

    public void CloseImage()
    {
        if (Game.Instance.IsPaused || _imageHeld) return;
        _image.Visible = false;
        _image.MouseFilter = Control.MouseFilterEnum.Ignore;
        _interface.Visible = true;
        _imageTcs?.TrySetResult();
        _imageTcs = null;
    }
}
