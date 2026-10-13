using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Full-screen point-and-click interface: hover label next to the cursor, right-click verb wheel,
/// satchel button + inventory case, dialogue choices, speech text, fades and the custom cursor.
/// Built in code so the layout lives in one place.
/// </summary>
public partial class Hud : CanvasLayer
{
    public const int ScreenW = 480, ScreenH = 270;
    private const int SlotW = 40, SlotH = 28, InvCols = 6, InvRows = 2;
    private static readonly Vector2 InvPos = new(110, 186);
    private static readonly Vector2 SatchelPos = new(444, 234);

    public static readonly Color VerbColor = new("b89a58");
    public static readonly Color VerbHover = new("f8e8b0");
    public static readonly Color ChoiceColor = new("8ab0d8");

    public event Action<string, bool, Vector2>? ItemClicked;
    public event Action<string?>? ItemHovered;
    public static Font Font { get; private set; } = null!;
    public VerbWheel Wheel { get; private set; } = null!;
    public GameMenu Menu { get; private set; } = null!;
    public PuzzlePanel Puzzle { get; private set; } = null!;

    private Control _interface = null!;
    private Control _hoverLayer = null!;
    private Label _hover = null!;
    private TextureButton _satchel = null!;
    private Control _inventory = null!;
    private readonly List<Button> _slots = new();
    private ColorRect _choicesBg = null!;
    private VBoxContainer _choices = null!;
    private Label _speech = null!;
    private ColorRect _fade = null!;
    private Label _caption = null!;
    private TextureRect _image = null!;
    private TaskCompletionSource? _imageTcs;
    private TextureRect _inset = null!;
    private Tween? _insetTween;
    private bool _insetShown;
    private CloseUp? _closeUp;
    private GameSettings? _settings;
    private TextureRect _title = null!;
    private Control _pause = null!;
    private TextureRect _cursor = null!;
    private TextureRect _cursorItem = null!;
    private Texture2D _cursorTex = null!;
    private TaskCompletionSource<int>? _choiceTcs;
    private int _inventoryPage;
    private Button _previousPage = null!, _nextPage = null!;
    private Label _pageLabel = null!;
    public int InventoryPage => _inventoryPage;

    public bool ChoicesVisible => _choices.Visible;
    public bool CaptionVisible => _caption.Visible;
    public string CaptionText => _caption.Text;
    public bool InventoryOpen => _inventory.Visible;
    public bool InterfaceVisible => _interface.Visible;
    public Rect2 HoverRect => _hover.Visible && _hoverLayer.Visible ? _hover.GetGlobalRect() : new Rect2();
    public bool HoverDrawsOverInventory => _hoverLayer.GetIndex() > _inventory.GetIndex();
    public bool TitleVisible => _title.Visible;
    public bool PauseVisible => _pause.Visible;
    public bool SpeechVisible => _speech.Visible;
    public string SpeechText => _speech.Text;
    public Rect2 SpeechRect => _speech.GetRect();
    public Rect2 InsetRect => _inset.GetRect();
    public float FadeAlpha => _fade.Color.A;

    public static Label MakeOutlinedLabel(Color color) => new()
    {
        LabelSettings = new LabelSettings { Font = Font, FontSize = 8, FontColor = color, OutlineSize = 4, OutlineColor = new Color(0, 0, 0) },
        MouseFilter = Control.MouseFilterEnum.Ignore,
    };

    public override void _Ready()
    {
        Layer = 10;
        // keeps the pause input, cursor and menu alive while gameplay is paused
        ProcessMode = ProcessModeEnum.Always;
        Font = GD.Load<Font>("res://assets/fonts/Silkscreen-Regular.ttf");
        // .godot/ is not committed: a fresh checkout has no imported assets until the editor (or --import) runs
        if (Font == null)
            GD.PushError("Assets are not imported (fresh checkout?). Run `godot --path . --headless --import` once, then start the game again.");
        var theme = new Theme { DefaultFont = Font, DefaultFontSize = 8 };

        var root = new Control
        {
            Theme = theme,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            ProcessMode = ProcessModeEnum.Pausable,
        };
        root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        AddChild(root);

        _inset = new TextureRect { Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
        root.AddChild(_inset);

        _interface = new Control { MouseFilter = Control.MouseFilterEnum.Ignore };
        _interface.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        root.AddChild(_interface);

        _hover = MakeOutlinedLabel(VerbHover);

        _satchel = new TextureButton
        {
            TextureNormal = GD.Load<Texture2D>("res://assets/art/ui/satchel.png"),
            Position = SatchelPos,
            FocusMode = Control.FocusModeEnum.None,
            TooltipText = "",
        };
        _satchel.Pressed += () => ShowInventory(!_inventory.Visible);
        _satchel.MouseEntered += () => _satchel.Modulate = new Color(1.3f, 1.2f, 1f);
        _satchel.MouseExited += () => _satchel.Modulate = Colors.White;
        _interface.AddChild(_satchel);

        BuildInventory(root);

        // above the inventory case, so item names over the top row aren't hidden behind its frame
        _hoverLayer = new Control { MouseFilter = Control.MouseFilterEnum.Ignore };
        _hoverLayer.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _hoverLayer.AddChild(_hover);
        root.AddChild(_hoverLayer);

        _choicesBg = new ColorRect { Color = new Color(0.04f, 0.03f, 0.06f, 0.88f), Visible = false };
        root.AddChild(_choicesBg);
        _choices = new VBoxContainer { Visible = false };
        _choices.AddThemeConstantOverride("separation", 1);
        root.AddChild(_choices);

        _speech = new Label
        {
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            LabelSettings = new LabelSettings
            {
                Font = Font, FontSize = 8, OutlineSize = 4, OutlineColor = new Color(0, 0, 0), LineSpacing = 1,
            },
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Visible = false,
        };
        root.AddChild(_speech);

        Wheel = new VerbWheel { Name = "VerbWheel" };
        root.AddChild(Wheel);

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

        _image = new TextureRect { Visible = false, MouseFilter = Control.MouseFilterEnum.Ignore };
        _image.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _image.GuiInput += e =>
        {
            if (e is InputEventMouseButton { Pressed: true }) CloseImage();
        };
        root.AddChild(_image);

        Menu = new GameMenu { Name = "GameMenu" };
        root.AddChild(Menu);

        Puzzle = new PuzzlePanel { Name = "PuzzlePanel" };
        root.AddChild(Puzzle);

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

        _cursorTex = GD.Load<Texture2D>("res://assets/art/ui/cursor.png");
        _cursor = new TextureRect { Texture = _cursorTex, MouseFilter = Control.MouseFilterEnum.Ignore };
        root.AddChild(_cursor);
        // a held item rides beside the crosshair as a half-size badge, so the pointer itself never changes size
        _cursorItem = new TextureRect
        {
            MouseFilter = Control.MouseFilterEnum.Ignore,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            Size = CursorItemSize,
            // exactly half size: linear sampling averages each 2x2 block instead of dropping pixels
            TextureFilter = CanvasItem.TextureFilterEnum.Linear,
            Visible = false,
        };
        root.AddChild(_cursorItem);
        Input.MouseMode = Input.MouseModeEnum.Hidden;

        GameState.Instance.Changed += RefreshInventory;
        RefreshInventory();
    }

    /// <summary>Last mouse position in game pixels (tracked from motion events, so synthetic input works too).</summary>
    public Vector2 MousePos { get; private set; } = new(ScreenW / 2f, ScreenH / 2f);

    public override void _Input(InputEvent e)
    {
        if (e is InputEventMouse m) MousePos = m.Position;
        if (e.IsAction("pause_game"))
        {
            if (e.IsActionPressed("pause_game") && e is not InputEventKey { Echo: true })
                Game.Instance.TogglePause();
            GetViewport().SetInputAsHandled();
            return;
        }
        if (Game.Instance.IsPaused) GetViewport().SetInputAsHandled();
    }

    public void ShowPause(bool show) => _pause.Visible = show;

    public override void _Process(double delta)
    {
        _cursor.Position = MousePos.Floor() - (_cursor.Texture.GetSize() / 2).Floor();
        _cursorItem.Position = MousePos.Floor() + new Vector2(4, 4);
        _hoverLayer.Visible = _interface.Visible;
    }

    private void BuildInventory(Control root)
    {
        // full-screen catcher: clicking outside the case closes it
        _inventory = new Control { Visible = false, MouseFilter = Control.MouseFilterEnum.Stop };
        _inventory.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _inventory.GuiInput += e =>
        {
            if (e is InputEventMouseButton { Pressed: true }) ShowInventory(false);
        };
        root.AddChild(_inventory);
        _inventory.AddChild(new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/inventory.png"),
            Position = InvPos,
            MouseFilter = Control.MouseFilterEnum.Stop,
        });

        var normal = new StyleBoxFlat { BgColor = new Color("140c08"), BorderColor = new Color("3a2814") };
        normal.SetBorderWidthAll(1);
        var hover = new StyleBoxFlat { BgColor = new Color("2a1c10"), BorderColor = new Color("d8b050") };
        hover.SetBorderWidthAll(1);
        for (int r = 0; r < InvRows; r++)
        for (int c = 0; c < InvCols; c++)
        {
            var b = new Button
            {
                Position = InvPos + new Vector2(10 + c * SlotW, 7 + r * SlotH),
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
            _inventory.AddChild(b);
            _slots.Add(b);
        }
        _previousPage = new Button { Text = "<", Position = new Vector2(110, 249), Size = new Vector2(30, 18), FocusMode = Control.FocusModeEnum.None };
        _nextPage = new Button { Text = ">", Position = new Vector2(340, 249), Size = new Vector2(30, 18), FocusMode = Control.FocusModeEnum.None };
        _pageLabel = MakeOutlinedLabel(VerbHover);
        _pageLabel.Position = new Vector2(197, 253);
        _previousPage.Pressed += () => { _inventoryPage--; ItemHovered?.Invoke(null); RefreshInventory(); };
        _nextPage.Pressed += () => { _inventoryPage++; ItemHovered?.Invoke(null); RefreshInventory(); };
        _inventory.AddChild(_previousPage);
        _inventory.AddChild(_nextPage);
        _inventory.AddChild(_pageLabel);
    }

    private string? ItemInSlot(int slot)
    {
        var inv = GameState.Instance.Inventory;
        slot += _inventoryPage * InvCols * InvRows;
        return slot < inv.Count ? inv[slot] : null;
    }

    /// <summary>Screen position of an inventory slot (used by the autoplay test).</summary>
    public Vector2 SlotCenter(int slot) => _slots[slot % _slots.Count].Position + _slots[slot % _slots.Count].Size / 2;
    public Vector2 InventoryPageCenter(bool next) => (next ? _nextPage : _previousPage).GetGlobalRect().GetCenter();

    public Vector2 SatchelCenter => SatchelPos + _satchel.Size / 2;

    private void OnSlotInput(int slot, InputEvent e)
    {
        if (e is not InputEventMouseButton { Pressed: true } mb) return;
        _slots[slot].AcceptEvent();
        if (ItemInSlot(slot) is not { } item || mb.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        ItemClicked?.Invoke(item, mb.ButtonIndex == MouseButton.Right, mb.GlobalPosition);
    }

    public void RefreshInventory()
    {
        int pages = Math.Max(1, (GameState.Instance.Inventory.Count + _slots.Count - 1) / _slots.Count);
        _inventoryPage = Math.Clamp(_inventoryPage, 0, pages - 1);
        _previousPage.Disabled = _inventoryPage == 0;
        _nextPage.Disabled = _inventoryPage == pages - 1;
        _pageLabel.Text = $"Page {_inventoryPage + 1}/{pages}";
        for (int s = 0; s < _slots.Count; s++)
        {
            var id = ItemInSlot(s);
            _slots[s].Icon = id == null ? null : GD.Load<Texture2D>(Items.Get(id).IconPath);
        }
        _satchel.Disabled = false;
    }

    public void ShowInventory(bool show)
    {
        if (show && Game.Instance.Busy) return;
        _inventory.Visible = show;
        if (!show) ItemHovered?.Invoke(null);
    }

    /// <summary>Label shown just above the cursor ("Trunk", "Use crowbar on trunk").</summary>
    public void SetHover(string? text, Vector2 mouse)
    {
        _hover.Visible = !string.IsNullOrEmpty(text);
        if (!_hover.Visible) return;
        _hover.Text = text;
        var size = _hover.GetMinimumSize();
        var pos = new Vector2(mouse.X - size.X / 2, mouse.Y - size.Y - 8);
        if (pos.Y < 2) pos.Y = mouse.Y + 10;
        pos.X = Mathf.Clamp(pos.X, 2, ScreenW - size.X - 2);
        _hover.Position = pos.Round();
    }

    /// <summary>Shows the held inventory item as a small badge beside the crosshair (null = crosshair only).</summary>
    public void SetCursorItem(string? item)
    {
        _cursorItem.Visible = item != null;
        _cursorItem.Texture = item == null ? null : GD.Load<Texture2D>(Items.Get(item).IconPath);
    }

    public bool CursorItemVisible => _cursorItem.Visible;
    public Vector2 CursorSize => _cursor.Texture.GetSize();
    public static readonly Vector2 CursorItemSize = new(16, 12);

    /// <summary>Hides the satchel and labels during cutscenes (MI style).</summary>
    public void SetInterfaceVisible(bool visible)
    {
        _interface.Visible = visible && !_choices.Visible;
        if (!visible && _inventory.Visible) ShowInventory(false);
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
                CustomMinimumSize = new Vector2(ScreenW - 16, 12),
                ClipText = true,
            };
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
        float h = options.Count * 13 + 8;
        _choicesBg.Position = new Vector2(0, ScreenH - h);
        _choicesBg.Size = new Vector2(ScreenW, h);
        _choices.Position = new Vector2(8, ScreenH - h + 4);
        _choices.Size = new Vector2(ScreenW - 16, h - 8);
        _choices.Visible = _choicesBg.Visible = true;
        _interface.Visible = false;
        _choiceTcs = new TaskCompletionSource<int>();
        return _choiceTcs.Task;
    }

    public void HideChoices() => _choices.Visible = _choicesBg.Visible = false;

    /// <summary>Displays speech above a point (room coordinates == screen coordinates).</summary>
    public void ShowSpeech(string text, Vector2 head, Color color)
    {
        if (_insetShown)
        {
            ShowSpeechOverInset(text, color);
            return;
        }
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
        if (head.X + textHalf > ScreenW - 2) shift = ScreenW - 2 - (head.X + textHalf);
        pos.X += shift;
        pos.Y = Mathf.Clamp(pos.Y, 2, ScreenH - size.Y - 2);
        _speech.Position = pos.Round();
        _speech.Visible = true;
    }

    public void HideSpeech() => _speech.Visible = false;

    /// <summary>While a close-up fills the screen, speech sits along its bottom edge, clear of the face.</summary>
    private void ShowSpeechOverInset(string text, Color color)
    {
        const int width = 380;
        var size = Font.GetMultilineStringSize(text, HorizontalAlignment.Center, width, 8);
        _speech.Text = text;
        _speech.LabelSettings.FontColor = color;
        _speech.Size = new Vector2(width, size.Y);
        float bottom = _inset.Position.Y + _inset.Size.Y - 8;
        _speech.Position = new Vector2((ScreenW - width) / 2f, bottom - size.Y).Round();
        _speech.Visible = true;
    }

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
    /// and above it, and speech moves to the panel's bottom edge. Stays until <see cref="HideCloseUp"/> or the next
    /// room change. Showing the one already up does nothing.
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

    private void ShowInset(Texture2D texture, double seconds)
    {
        _insetTween?.Kill();
        _inset.Texture = texture;
        var size = texture.GetSize();
        _inset.Size = size;
        _inset.Position = ((new Vector2(ScreenW, ScreenH) - size) / 2).Floor();
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

    public void CloseImage()
    {
        if (Game.Instance.IsPaused) return;
        _image.Visible = false;
        _image.MouseFilter = Control.MouseFilterEnum.Ignore;
        _interface.Visible = true;
        _imageTcs?.TrySetResult();
        _imageTcs = null;
    }
}
