using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Dialogue choices, speech text and Micah's journal thoughts.</summary>
public partial class Hud
{
    private const int ChoiceRowH = 14, ChoiceGap = 1;

    private static Vector2 MeasureDialogue(string text, float width) =>
        DialogueFont.GetMultilineStringSize(text, HorizontalAlignment.Center, width, DialogueFontSize);

    private void BuildChoices(Control root)
    {
        _choicesBg = new ColorRect { Color = new Color(0.04f, 0.03f, 0.06f, 0.88f), Visible = false };
        root.AddChild(_choicesBg);
        _choices = new VBoxContainer { Visible = false };
        _choices.AddThemeConstantOverride("separation", ChoiceGap);
        root.AddChild(_choices);
    }

    private void BuildSpeech(Control root)
    {
        _speech = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            LabelSettings = new LabelSettings
            {
                Font = DialogueFont, FontSize = DialogueFontSize, OutlineSize = 4, OutlineColor = new Color(0, 0, 0), LineSpacing = 0,
            },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_speech);

        // Micah's journal narration: faded ink along the top, over a faint strip so it reads on any background
        _thoughtBg = new ColorRect { Color = new Color(0.04f, 0.03f, 0.02f, 0.55f), Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
        root.AddChild(_thoughtBg);
        _thought = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            LabelSettings = new LabelSettings
            {
                Font = DialogueFont, FontSize = DialogueFontSize, FontColor = ThoughtColor, OutlineSize = 4,
                OutlineColor = new Color(0.08f, 0.05f, 0.02f), LineSpacing = 0,
            },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_thought);
    }

    public Task<int> ShowChoices(IReadOnlyList<string> options)
    {
        foreach (var c in _choices.GetChildren()) c.QueueFree();
        for (int i = 0; i < options.Count; i++)
        {
            int idx = i;
            var b = new Button
            {
                Text = options[i],
                Flat = true,
                Alignment = HorizontalAlignment.Left,
                FocusMode = Control.FocusModeEnum.None,
                CustomMinimumSize = new Vector2(ChoiceTextWidth, ChoiceRowH),
                ClipText = true,
            };
            b.AddThemeFontOverride("font", DialogueFont);
            b.AddThemeFontSizeOverride("font_size", DialogueFontSize);
            b.AddThemeColorOverride("font_color", ChoiceColor);
            b.AddThemeColorOverride("font_hover_color", VerbHover);
            b.AddThemeColorOverride("font_pressed_color", Colors.White);
            b.AddThemeColorOverride("font_hover_pressed_color", Colors.White);
            var empty = new StyleBoxEmpty();
            foreach (var s in new[] { "normal", "hover", "pressed", "hover_pressed", "focus" })
                b.AddThemeStyleboxOverride(s, empty);
            b.Pressed += async () =>
            {
                await Game.Instance.WaitUntilResumed();
                HideChoices();
                _choiceTcs?.TrySetResult(idx);
            };
            _choices.AddChild(b);
        }
        float h = options.Count * (ChoiceRowH + ChoiceGap) + 8;
        _choicesBg.Position = new Vector2(0, ScreenH - h);
        _choicesBg.Size = new Vector2(ScreenW, h);
        _choices.Position = new Vector2(8, ScreenH - h + 4);
        _choices.Size = new Vector2(ChoiceTextWidth, h - 8);
        _choices.Visible = _choicesBg.Visible = true;
        _interface.Visible = false;
        _choiceTcs = new TaskCompletionSource<int>();
        return _choiceTcs.Task;
    }

    public void HideChoices() => _choices.Visible = _choicesBg.Visible = false;

    /// <summary>Width a choice label can use before the bar clips it.</summary>
    public const int ChoiceTextWidth = ScreenW - 16;

    /// <summary>The labels on the choice bar's buttons, top to bottom (tests).</summary>
    public IReadOnlyList<string> ChoiceTexts
    {
        get
        {
            var texts = new List<string>();
            foreach (var c in _choices.GetChildren())
                if (c is Button b && !b.IsQueuedForDeletion()) texts.Add(b.Text);
            return texts;
        }
    }

    /// <summary>Film mode: draws the option about to be picked in the hover colour.</summary>
    public void HighlightChoice(int index)
    {
        if (index < _choices.GetChildCount() && _choices.GetChild(index) is Button b)
            b.AddThemeColorOverride("font_color", VerbHover);
    }

    /// <summary>Displays speech above a point (room coordinates == screen coordinates).</summary>
    public void ShowSpeech(string text, ISpeaker speaker)
    {
        var head = speaker.HeadPosition;
        var color = speaker.SpeechColor;
        if (_insetShown)
        {
            ShowSpeechOverInset(text, speaker);
            return;
        }
        const int width = 280;
        var size = MeasureDialogue(text, width);
        _speech.Text = text;
        _speech.LabelSettings.FontColor = color;
        _speech.Size = new Vector2(width, size.Y);
        var pos = new Vector2(head.X - width / 2f, head.Y - size.Y - 2);
        // clamp horizontally by moving the box but keeping it centred over the text
        float textHalf = Mathf.Min(width, size.X) / 2f + 3;
        float shift = 0;
        if (head.X - textHalf < 2) shift = 2 - (head.X - textHalf);
        if (head.X + textHalf > ScreenW - 2) shift = ScreenW - 2 - (head.X + textHalf);
        pos.X += shift;
        pos.Y = Mathf.Clamp(pos.Y, 2, ScreenH - size.Y - 2);
        _speech.Position = pos.Round();
        _speech.Visible = true;
    }

    public void HideSpeech() => _speech.Visible = false;

    /// <summary>Shows a line of Micah's journal narration centred along the top of the screen.</summary>
    public void ShowThought(string text)
    {
        var size = MeasureDialogue(text, ThoughtWidth);
        _thought.Text = text;
        _thought.Size = new Vector2(ThoughtWidth, size.Y);
        _thought.Position = new Vector2((ScreenW - ThoughtWidth) / 2f, ThoughtTop).Round();
        float stripW = Mathf.Min(ThoughtWidth, size.X) + 12;
        _thoughtBg.Position = new Vector2((ScreenW - stripW) / 2f, ThoughtTop - 3).Round();
        _thoughtBg.Size = new Vector2(stripW, size.Y + 6).Round();
        _thought.Visible = _thoughtBg.Visible = true;
    }

    public void HideThought() => _thought.Visible = _thoughtBg.Visible = false;

    /// <summary>While a close-up fills the screen, speech sits along its bottom edge, clear of the face.</summary>
    private void ShowSpeechOverInset(string text, ISpeaker speaker)
    {
        float width = 380;
        float x = (ScreenW - width) / 2f;
        if (_closeUp == CloseUps.Convent)
        {
            const int padding = 12;
            float half = _inset.Size.X / 2f;
            width = half - padding * 2;
            x = _inset.Position.X + padding;
            if (speaker is Actor { Id: "eleanor" }) x += half;
        }
        var size = MeasureDialogue(text, width);
        _speech.Text = text;
        _speech.LabelSettings.FontColor = speaker.SpeechColor;
        _speech.Size = new Vector2(width, size.Y);
        float bottom = _inset.Position.Y + _inset.Size.Y - 8;
        _speech.Position = new Vector2(x, bottom - size.Y).Round();
        _speech.Visible = true;
    }
}
