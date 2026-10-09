using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// The SCUMM-style interface: sentence line, 3x3 verb grid, scrolling inventory, dialogue choices,
/// speech text and screen fades. Built in code so the layout lives in one place.
/// </summary>
public partial class Hud : CanvasLayer
{
    public const int Top = 200;
    private const int SlotW = 38, SlotH = 27, InvCols = 7, InvRows = 2, InvX = 184, InvY = 213;

    public static readonly Color VerbColor = new("b89a58");
    public static readonly Color VerbHover = new("f8e8b0");
    public static readonly Color VerbActive = new("ffffff");
    public static readonly Color SentenceColor = new("9ec0e0");

    public event Action<Verb>? VerbClicked;
    public event Action<string, bool>? ItemClicked;
    public event Action<string?>? ItemHovered;
    public event Action? TitleClicked;

    public Font Font { get; private set; } = null!;

    private Label _sentence = null!;
    private Control _verbsAndInv = null!;
    private VBoxContainer _choices = null!;
    private readonly Dictionary<Verb, Button> _verbButtons = new();
    private readonly List<Button> _slots = new();
    private Button _up = null!, _down = null!;
    private int _invRow;
    private Verb? _highlight;
    private Label _speech = null!;
    private ColorRect _fade = null!;
    private Label _caption = null!;
    private TextureRect _title = null!;
    private Label _titleHint = null!;
    private TaskCompletionSource<int>? _choiceTcs;

    public bool ChoicesVisible => _choices.Visible;
    public bool CaptionVisible => _caption.Visible;

    public override void _Ready()
    {
        Layer = 10;
        Font = GD.Load<Font>("res://assets/fonts/Silkscreen-Regular.ttf");
        var theme = new Theme { DefaultFont = Font, DefaultFontSize = 8 };

        var root = new Control { Theme = theme, MouseFilter = Control.MouseFilterEnum.Ignore };
        root.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        AddChild(root);

        root.AddChild(new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/panel.png"),
            Position = new Vector2(0, Top),
            MouseFilter = Control.MouseFilterEnum.Stop,
        });

        _sentence = new Label
        {
            Position = new Vector2(0, Top + 2),
            Size = new Vector2(480, 10),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Font, FontSize = 8, FontColor = SentenceColor },
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        root.AddChild(_sentence);

        _verbsAndInv = new Control { MouseFilter = Control.MouseFilterEnum.Ignore };
        root.AddChild(_verbsAndInv);
        BuildVerbs();
        BuildInventory();

        _choices = new VBoxContainer
        {
            Position = new Vector2(8, Top + 6),
            Size = new Vector2(464, 62),
            Visible = false,
        };
        _choices.AddThemeConstantOverride("separation", 1);
        root.AddChild(_choices);

        _speech = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            LabelSettings = new LabelSettings
            {
                Font = Font, FontSize = 8, OutlineSize = 4, OutlineColor = new Color(0, 0, 0),
                LineSpacing = 1,
            },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_speech);

        _title = new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/title.png"),
            Visible = false,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        root.AddChild(_title);
        _titleHint = new Label
        {
            Text = "Click to begin",
            Position = new Vector2(0, 150),
            Size = new Vector2(480, 10),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Font, FontSize = 8, FontColor = VerbColor },
        };
        _title.AddChild(_titleHint);
        _title.GuiInput += e =>
        {
            if (e is InputEventMouseButton { Pressed: true }) TitleClicked?.Invoke();
        };

        _fade = new ColorRect { Color = new Color(0, 0, 0, 1), MouseFilter = Control.MouseFilterEnum.Ignore };
        _fade.SetAnchorsPreset(Control.LayoutPreset.FullRect);
        root.AddChild(_fade);

        _caption = new Label
        {
            Position = new Vector2(0, 126),
            Size = new Vector2(480, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Font, FontSize = 16, FontColor = VerbHover },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_caption);

        GameState.Instance.Changed += RefreshInventory;
        RefreshInventory();
    }

    public override void _Process(double delta)
    {
        if (_title.Visible)
            _titleHint.Modulate = new Color(1, 1, 1, 0.55f + 0.45f * Mathf.Sin(Time.GetTicksMsec() / 300f));
    }

    private Button MakeTextButton(string text, Color color)
    {
        var b = new Button
        {
            Text = text,
            Flat = true,
            Alignment = HorizontalAlignment.Left,
            FocusMode = Control.FocusModeEnum.None,
            ButtonMask = MouseButtonMask.Left | MouseButtonMask.Right,
        };
        b.AddThemeColorOverride("font_color", color);
        b.AddThemeColorOverride("font_hover_color", VerbHover);
        b.AddThemeColorOverride("font_pressed_color", VerbActive);
        b.AddThemeColorOverride("font_hover_pressed_color", VerbActive);
        var empty = new StyleBoxEmpty();
        foreach (var s in new[] { "normal", "hover", "pressed", "hover_pressed", "focus" })
            b.AddThemeStyleboxOverride(s, empty);
        return b;
    }

    private void BuildVerbs()
    {
        for (int i = 0; i < Verbs.Grid.Length; i++)
        {
            var v = Verbs.Grid[i];
            var b = MakeTextButton(Verbs.Label(v), VerbColor);
            b.Position = new Vector2(8 + (i % 3) * 58, Top + 14 + (i / 3) * 16);
            b.Size = new Vector2(56, 14);
            b.Pressed += () => VerbClicked?.Invoke(v);
            _verbsAndInv.AddChild(b);
            _verbButtons[v] = b;
        }
    }

    private void BuildInventory()
    {
        var normal = new StyleBoxFlat { BgColor = new Color("140f18"), BorderColor = new Color("3a2c40") };
        normal.SetBorderWidthAll(1);
        var hover = new StyleBoxFlat { BgColor = new Color("241a2a"), BorderColor = new Color("b89a58") };
        hover.SetBorderWidthAll(1);
        for (int r = 0; r < InvRows; r++)
        for (int c = 0; c < InvCols; c++)
        {
            var b = new Button
            {
                Position = new Vector2(InvX + c * SlotW, InvY + r * SlotH),
                Size = new Vector2(SlotW - 2, SlotH - 2),
                FocusMode = Control.FocusModeEnum.None,
                IconAlignment = HorizontalAlignment.Center,
                ButtonMask = MouseButtonMask.Left | MouseButtonMask.Right,
            };
            b.AddThemeStyleboxOverride("normal", normal);
            b.AddThemeStyleboxOverride("hover", hover);
            b.AddThemeStyleboxOverride("pressed", hover);
            b.AddThemeStyleboxOverride("disabled", normal);
            b.AddThemeStyleboxOverride("focus", new StyleBoxEmpty());
            var slot = _slots.Count;
            b.GuiInput += e => OnSlotInput(slot, e);
            b.MouseEntered += () => ItemHovered?.Invoke(ItemInSlot(slot));
            b.MouseExited += () => ItemHovered?.Invoke(null);
            _verbsAndInv.AddChild(b);
            _slots.Add(b);
        }
        _up = MakeTextButton("^", VerbColor);
        _up.Position = new Vector2(InvX + InvCols * SlotW + 4, InvY + 4);
        _up.Size = new Vector2(20, 16);
        _up.Pressed += () => { _invRow = Math.Max(0, _invRow - 1); RefreshInventory(); };
        _down = MakeTextButton("v", VerbColor);
        _down.Position = new Vector2(InvX + InvCols * SlotW + 4, InvY + SlotH + 6);
        _down.Size = new Vector2(20, 16);
        _down.Pressed += () => { _invRow++; RefreshInventory(); };
        _verbsAndInv.AddChild(_up);
        _verbsAndInv.AddChild(_down);
    }

    private string? ItemInSlot(int slot)
    {
        var inv = GameState.Instance.Inventory;
        int i = _invRow * InvCols + slot;
        return i < inv.Count ? inv[i] : null;
    }

    private void OnSlotInput(int slot, InputEvent e)
    {
        if (e is InputEventMouseButton { Pressed: true } mb && ItemInSlot(slot) is { } item &&
            mb.ButtonIndex is MouseButton.Left or MouseButton.Right)
        {
            ItemClicked?.Invoke(item, mb.ButtonIndex == MouseButton.Right);
            GetViewport().SetInputAsHandled();
        }
    }

    public void RefreshInventory()
    {
        var inv = GameState.Instance.Inventory;
        int maxRow = Math.Max(0, (inv.Count - 1) / InvCols - (InvRows - 1));
        _invRow = Math.Clamp(_invRow, 0, maxRow);
        for (int s = 0; s < _slots.Count; s++)
        {
            var id = ItemInSlot(s);
            _slots[s].Icon = id == null ? null : GD.Load<Texture2D>(Items.Get(id).IconPath);
            _slots[s].TooltipText = "";
        }
        _up.Visible = _invRow > 0;
        _down.Visible = _invRow < maxRow;
    }

    public void SetSentence(string text) => _sentence.Text = text;

    public void HighlightVerb(Verb? verb)
    {
        if (_highlight is { } old && _verbButtons.TryGetValue(old, out var ob))
            ob.AddThemeColorOverride("font_color", VerbColor);
        _highlight = verb;
        if (verb is { } v && _verbButtons.TryGetValue(v, out var nb))
            nb.AddThemeColorOverride("font_color", VerbHover);
    }

    /// <summary>Hides verbs/inventory during cutscenes (MI style).</summary>
    public void SetInterfaceVisible(bool visible)
    {
        _verbsAndInv.Visible = visible && !_choices.Visible;
        _sentence.Visible = visible;
    }

    public Task<int> ShowChoices(IReadOnlyList<string> options)
    {
        foreach (var c in _choices.GetChildren()) c.QueueFree();
        for (int i = 0; i < options.Count; i++)
        {
            int idx = i;
            var b = MakeTextButton(options[i], new Color("8ab0d8"));
            b.CustomMinimumSize = new Vector2(464, 12);
            b.ClipText = true;
            b.Pressed += () =>
            {
                _choices.Visible = false;
                _choiceTcs?.TrySetResult(idx);
            };
            _choices.AddChild(b);
        }
        _choices.Visible = true;
        _verbsAndInv.Visible = false;
        _sentence.Visible = false;
        _choiceTcs = new TaskCompletionSource<int>();
        return _choiceTcs.Task;
    }

    public void HideChoices() => _choices.Visible = false;

    /// <summary>Displays speech above a point (room coordinates == screen coordinates).</summary>
    public void ShowSpeech(string text, Vector2 head, Color color)
    {
        const int width = 220;
        var size = Font.GetMultilineStringSize(text, HorizontalAlignment.Center, width, 8);
        _speech.Text = text;
        _speech.LabelSettings.FontColor = color;
        _speech.Size = new Vector2(width, size.Y);
        var pos = new Vector2(head.X - width / 2f, head.Y - size.Y - 2);
        // clamp horizontally by moving the box but keeping it centred over the text
        float textHalf = Mathf.Min(width, size.X) / 2f + 3;
        float shift = 0;
        if (head.X - textHalf < 2) shift = 2 - (head.X - textHalf);
        if (head.X + textHalf > 478) shift = 478 - (head.X + textHalf);
        pos.X += shift;
        pos.Y = Mathf.Clamp(pos.Y, 2, Top - size.Y - 2);
        _speech.Position = pos.Round();
        _speech.Visible = true;
    }

    public void HideSpeech() => _speech.Visible = false;

    public async Task Fade(float alpha, double seconds)
    {
        var tw = CreateTween();
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
