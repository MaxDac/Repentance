using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

public enum PuzzleKind { Lift, Safe, Catalogue, Cipher, Crests, Bell, Alignment }

/// <summary>
/// The shared Art Deco puzzle screen: frame, title cartouche, clue card, feedback strip and the Reset / Submit /
/// Close footer. Each puzzle is a <see cref="PuzzleScreen"/> that fills the work area on the left.
/// </summary>
public partial class PuzzlePanel : Control
{
    private static readonly Color Parchment = new("e8dcc0");
    private readonly Dictionary<string, Button> _buttons = new();
    private TaskCompletionSource<bool>? _completion;
    private PuzzleScreen? _screen;
    private Label _feedback = null!;
    private Label _clue = null!;
    private Texture2D? _frame;
    public PuzzleKind Kind { get; private set; }
    public bool IsOpen => Visible;

    public override void _Ready()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;
        Visible = false;
    }

    public Task<bool> Open(PuzzleKind kind)
    {
        if (_completion != null) throw new InvalidOperationException("A puzzle is already open.");
        foreach (var child in GetChildren())
        {
            RemoveChild(child);
            child.QueueFree();
        }
        _buttons.Clear();
        Kind = kind;
        _screen = PuzzleScreen.For(kind);
        _completion = new TaskCompletionSource<bool>();
        var task = _completion.Task;
        Visible = true;
        Game.Instance.Hud.ShowInventory(false);
        Game.Instance.Hud.Wheel.Close();
        _frame ??= GD.Load<Texture2D>("res://assets/art/ui/puzzle_frame.png");

        var title = AddLabel(_screen.Title, new Rect2(140, 9, 200, 14));
        title.HorizontalAlignment = HorizontalAlignment.Center;
        _feedback = AddLabel("Read the clues. Nothing here is timed.", new Rect2(20, 244, 440, 14));
        _clue = AddLabel(_screen.Clue, new Rect2(290, 46, 168, 152), wrap: true);
        _clue.AddThemeColorOverride("font_color", Parchment);

        _screen.Attach(this);
        AddButton("reset", "Reset", new Rect2(18, 210, 70, 22), Reset);
        if (_screen.HasSubmit) AddButton("submit", _screen.SubmitText, new Rect2(186, 210, 108, 22), Submit);
        AddButton("close", "Close / Esc", new Rect2(368, 210, 96, 22), () => Finish(false));
        QueueRedraw();
        return task;
    }

    public override void _Input(InputEvent e)
    {
        if (!IsOpen || !e.IsActionPressed("ui_cancel")) return;
        GetViewport().SetInputAsHandled();
        Finish(false);
    }

    public Label AddLabel(string text, Rect2 rect, bool wrap = false)
    {
        var label = new Label
        {
            AutowrapMode = wrap ? TextServer.AutowrapMode.WordSmart : TextServer.AutowrapMode.Off,
            Text = text, Position = rect.Position,
            MouseFilter = MouseFilterEnum.Ignore,
        };
        label.AddThemeFontOverride("font", Hud.Font);
        label.AddThemeFontSizeOverride("font_size", 8);
        label.AddThemeColorOverride("font_color", Hud.VerbHover);
        AddChild(label);
        label.Size = rect.Size;
        return label;
    }

    public Button AddButton(string id, string text, Rect2 rect, Action action)
    {
        var button = new Button
        {
            Text = text, Position = rect.Position, Size = rect.Size,
            FocusMode = FocusModeEnum.None,
        };
        DecoStyle(button);
        button.Pressed += action;
        AddChild(button);
        _buttons.Add(id, button);
        return button;
    }

    /// <summary>A small square direction button: the 16x16 deco pad plate with a drawn arrow instead of a glyph.</summary>
    public Button AddPadButton(string id, Vector2 direction, Rect2 rect, Action action)
    {
        var button = new Button { Position = rect.Position, Size = rect.Size, FocusMode = FocusModeEnum.None };
        _padNormal ??= Box("deco_pad", 4, 1);
        _padHover ??= Box("deco_pad_hover", 4, 1);
        _padPressed ??= Box("deco_pad_pressed", 4, 1);
        button.AddThemeStyleboxOverride("normal", _padNormal);
        button.AddThemeStyleboxOverride("hover", _padHover);
        button.AddThemeStyleboxOverride("pressed", _padPressed);
        button.AddThemeStyleboxOverride("hover_pressed", _padPressed);
        button.AddThemeStyleboxOverride("focus", new StyleBoxEmpty());
        var arrow = new Control { MouseFilter = MouseFilterEnum.Ignore };
        arrow.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        arrow.Draw += () =>
        {
            var c = rect.Size / 2;
            var side = new Vector2(-direction.Y, direction.X);
            var color = button.IsPressed() ? new Color("fff6d8")
                : button.IsHovered() ? Hud.VerbHover : Hud.VerbColor.Lightened(0.25f);
            arrow.DrawColoredPolygon(new[] { c + direction * 3, c - direction * 3 + side * 4, c - direction * 3 - side * 4 }, color);
        };
        button.MouseEntered += arrow.QueueRedraw;
        button.MouseExited += arrow.QueueRedraw;
        button.ButtonDown += arrow.QueueRedraw;
        button.ButtonUp += arrow.QueueRedraw;
        button.AddChild(arrow);
        button.Pressed += action;
        AddChild(button);
        _buttons.Add(id, button);
        return button;
    }

    private static StyleBoxTexture? _normal, _hover, _pressed, _padNormal, _padHover, _padPressed;

    private static StyleBoxTexture Box(string file, int margin = 0, int content = 0)
    {
        var box = new StyleBoxTexture
        {
            Texture = GD.Load<Texture2D>($"res://assets/art/ui/{file}.png"),
            TextureMarginLeft = 7, TextureMarginRight = 7, TextureMarginTop = 6, TextureMarginBottom = 6,
            ContentMarginLeft = 6, ContentMarginRight = 6, ContentMarginTop = 2, ContentMarginBottom = 2,
        };
        if (margin > 0)
        {
            box.TextureMarginLeft = box.TextureMarginRight = box.TextureMarginTop = box.TextureMarginBottom = margin;
            box.ContentMarginLeft = box.ContentMarginRight = box.ContentMarginTop = box.ContentMarginBottom = content;
        }
        return box;
    }

    /// <summary>Stepped gold frame, inner keyline and corner studs: a nine-patch from tools/art/puzzles.py.</summary>
    private static void DecoStyle(Button button)
    {
        _normal ??= Box("deco_button");
        _hover ??= Box("deco_button_hover");
        _pressed ??= Box("deco_button_pressed");
        button.AddThemeStyleboxOverride("normal", _normal);
        button.AddThemeStyleboxOverride("hover", _hover);
        button.AddThemeStyleboxOverride("pressed", _pressed);
        button.AddThemeStyleboxOverride("hover_pressed", _pressed);
        button.AddThemeStyleboxOverride("focus", new StyleBoxEmpty());
        button.AddThemeFontOverride("font", Hud.Font);
        button.AddThemeFontSizeOverride("font_size", 8);
        button.AddThemeColorOverride("font_color", Hud.VerbColor.Lightened(0.25f));
        button.AddThemeColorOverride("font_hover_color", Hud.VerbHover);
        button.AddThemeColorOverride("font_pressed_color", new Color("fff6d8"));
        button.AddThemeColorOverride("font_hover_pressed_color", new Color("fff6d8"));
    }

    public Button? FindButton(string id) => _buttons.GetValueOrDefault(id);

    public Vector2 ButtonCenter(string id) =>
        _buttons.TryGetValue(id, out var button) ? button.GetGlobalRect().GetCenter() :
            throw new ArgumentException($"No puzzle control '{id}'.", nameof(id));

    public void SetFeedback(string text) => _feedback.Text = text;

    public void Solve() => Finish(true);

    private void Finish(bool solved)
    {
        var completion = _completion;
        _completion = null;
        Visible = false;
        completion?.TrySetResult(solved);
    }

    private void Submit()
    {
        if (_screen == null) return;
        var (solved, feedback) = _screen.Check();
        if (solved) Finish(true);
        else _feedback.Text = feedback;
        QueueRedraw();
    }

    private void Reset()
    {
        _screen?.Reset();
        _screen?.Refresh();
        _feedback.Text = "Reset. Your items and clues are still yours.";
        QueueRedraw();
    }

    public override void _Draw()
    {
        if (_frame != null) DrawTexture(_frame, Vector2.Zero);
        else DrawRect(new Rect2(0, 0, 480, 270), new Color("12131a"));
        _screen?.Draw(this);
    }
}
