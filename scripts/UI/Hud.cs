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
    public NotepadView Notepad { get; private set; } = null!;

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
    public bool InsetDrawn => _inset.Visible && _inset.Modulate.A > 0;
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

        // children draw in the order they are added: keep this sequence when adding new layers
        BuildSatchel();
        BuildInventory(root);
        BuildHoverLayer(root);
        BuildChoices(root);
        BuildSpeech(root);

        Wheel = new VerbWheel { Name = "VerbWheel" };
        root.AddChild(Wheel);

        BuildTitle(root);
        BuildFadeAndCaption(root);
        BuildImage(root);

        Notepad = new NotepadView { Name = "Notepad" };
        root.AddChild(Notepad);

        Menu = new GameMenu { Name = "GameMenu" };
        root.AddChild(Menu);

        Puzzle = new PuzzlePanel { Name = "PuzzlePanel" };
        root.AddChild(Puzzle);

        BuildPause(root);
        BuildCursor(root);
        Input.MouseMode = Input.MouseModeEnum.Hidden;

        GameState.Instance.Changed += RefreshInventory;
        RefreshInventory();
    }

    private void BuildHoverLayer(Control root)
    {
        _hover = MakeOutlinedLabel(VerbHover);
        // above the inventory case, so item names over the top row aren't hidden behind its frame
        _hoverLayer = new Control { MouseFilter = Control.MouseFilterEnum.Ignore };
        _hoverLayer.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _hoverLayer.AddChild(_hover);
        root.AddChild(_hoverLayer);
    }

    private void BuildCursor(Control root)
    {
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

    public override void _Process(double delta)
    {
        _cursor.Position = MousePos.Floor() - (_cursor.Texture.GetSize() / 2).Floor();
        _cursorItem.Position = MousePos.Floor() + new Vector2(4, 4);
        _hoverLayer.Visible = _interface.Visible;
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
}
