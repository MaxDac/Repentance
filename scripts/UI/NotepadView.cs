using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Full-screen reader for Micah's notepad: one note per page, newest page first, turned with the arrow buttons,
/// the arrow keys or the mouse wheel. N, Escape or the close button put it away.
/// </summary>
public partial class NotepadView : Control
{
    private static readonly Rect2 Paper = new(28, 10, 424, 250);
    private static readonly Color PaperColor = new("e8dcb8");
    private static readonly Color RuleColor = new("a8b4c8");
    private static readonly Color MarginColor = new("c87070");
    private static readonly Color InkColor = new("2a2018");
    private static readonly Color TitleColor = new("6a1a1a");
    private const float BodyLeft = 52, BodyTop = 44, LineStep = 12;

    private readonly List<NoteDef> _pages = new();
    private Label _title = null!, _body = null!, _counter = null!, _hint = null!;
    private TextureRect _sketch = null!;
    private Button _prev = null!, _next = null!, _close = null!;
    private TaskCompletionSource? _closed;

    public bool IsOpen => Visible;
    public int Page { get; private set; }
    public int PageCount => Math.Max(1, _pages.Count);
    public string? PageId => Page < _pages.Count ? _pages[Page].Id : null;
    public string PageTitle => _title.Text;
    public string PageText => _body.Text;
    public bool SketchVisible => _sketch.Visible;

    public Vector2 PrevCenter => _prev.GetGlobalRect().GetCenter();
    public Vector2 NextCenter => _next.GetGlobalRect().GetCenter();
    public Vector2 CloseCenter => _close.GetGlobalRect().GetCenter();

    public override void _Ready()
    {
        Visible = false;
        MouseFilter = MouseFilterEnum.Stop;
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        GuiInput += e =>
        {
            if (e is not InputEventMouseButton { Pressed: true } mb) return;
            if (mb.ButtonIndex == MouseButton.WheelUp) Turn(-1);
            else if (mb.ButtonIndex == MouseButton.WheelDown) Turn(1);
            AcceptEvent();
        };

        _title = Text(TitleColor, new Vector2(BodyLeft, Paper.Position.Y + 16), new Vector2(Paper.Size.X - 64, 12));
        _body = Text(InkColor, new Vector2(BodyLeft, BodyTop - 9), new Vector2(Paper.Size.X - 48, 180));
        _body.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        _body.LabelSettings.LineSpacing = LineStep - Hud.Font.GetHeight(8);
        _counter = Text(InkColor, new Vector2(Paper.Position.X, Paper.End.Y - 20), new Vector2(Paper.Size.X, 12));
        _counter.HorizontalAlignment = HorizontalAlignment.Center;
        _hint = Hud.MakeOutlinedLabel(Hud.VerbColor);
        _hint.Text = "Arrows turn the page - N or Esc to close";
        _hint.HorizontalAlignment = HorizontalAlignment.Center;
        _hint.Position = new Vector2(0, Paper.End.Y - 1);
        _hint.Size = new Vector2(Hud.ScreenW, 10);
        AddChild(_hint);

        _sketch = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            MouseFilter = MouseFilterEnum.Ignore,
            Visible = false,
        };
        AddChild(_sketch);

        _prev = PageButton("<", new Vector2(Paper.Position.X + 16, Paper.End.Y - 24), () => Turn(-1));
        _next = PageButton(">", new Vector2(Paper.End.X - 46, Paper.End.Y - 24), () => Turn(1));
        _close = PageButton("X", new Vector2(Paper.End.X - 26, Paper.Position.Y + 10), Close);
        _close.Size = new Vector2(16, 16);
    }

    private Label Text(Color color, Vector2 pos, Vector2 size)
    {
        var l = new Label
        {
            Position = pos,
            Size = size,
            LabelSettings = new LabelSettings { Font = Hud.Font, FontSize = 8, FontColor = color },
            MouseFilter = MouseFilterEnum.Ignore,
        };
        AddChild(l);
        return l;
    }

    private Button PageButton(string text, Vector2 pos, Action pressed)
    {
        var b = new Button { Text = text, Position = pos, Size = new Vector2(30, 18), FocusMode = FocusModeEnum.None };
        b.Pressed += pressed;
        AddChild(b);
        return b;
    }

    /// <summary>Opens on the newest note; completes when the notepad is put away.</summary>
    public Task Open()
    {
        if (IsOpen && _closed != null) return _closed.Task;
        _pages.Clear();
        _pages.AddRange(Notes.Visible(GameState.Instance.HasFlag));
        _closed = new TaskCompletionSource();
        Visible = true;
        ShowPage(PageCount - 1);
        return _closed.Task;
    }

    public void Close()
    {
        if (!IsOpen) return;
        Visible = false;
        var done = _closed;
        _closed = null;
        done?.TrySetResult();
    }

    public void Turn(int delta) => ShowPage(Page + delta);

    private void ShowPage(int page)
    {
        Page = Math.Clamp(page, 0, PageCount - 1);
        _prev.Disabled = Page == 0;
        _next.Disabled = Page >= PageCount - 1;
        _counter.Text = $"{Page + 1} / {PageCount}";

        var note = Page < _pages.Count ? _pages[Page] : null;
        _title.Text = note?.Title ?? "Notes";
        _body.Text = note == null
            ? "Nothing yet. A detective's notepad fills up the moment somebody starts lying to him."
            : string.Join("\n", Notes.Lines(note, GameState.Instance.HasFlag).Select(l => "- " + l));

        var sketch = note?.Sketch is { } path ? GD.Load<Texture2D>(path) : null;
        _sketch.Visible = sketch != null;
        _sketch.Texture = sketch;
        // a sketch takes the right half of the page; the text keeps to the left
        float bodyWidth = Paper.Size.X - 48;
        if (sketch != null)
        {
            bodyWidth = 180;
            _sketch.Position = new Vector2(BodyLeft + bodyWidth + 12, BodyTop - 6);
            _sketch.Size = new Vector2(Paper.End.X - 16 - _sketch.Position.X, 150);
        }
        _body.Size = new Vector2(bodyWidth, 180);
        QueueRedraw();
    }

    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), new Color(0, 0, 0, 0.8f));
        DrawRect(new Rect2(Paper.Position + new Vector2(3, 3), Paper.Size), new Color(0, 0, 0, 0.5f));
        DrawRect(Paper, new Color("6a5038"));
        var sheet = Paper.Grow(-2);
        DrawRect(sheet, PaperColor);
        // each ruled line sits just under a line of handwriting
        float baseline = BodyTop - 9 + Hud.Font.GetAscent(8) + 2;
        for (float y = baseline; y < Paper.End.Y - 26; y += LineStep)
            DrawLine(new Vector2(sheet.Position.X, y), new Vector2(sheet.End.X, y), RuleColor);
        DrawLine(new Vector2(BodyLeft - 6, sheet.Position.Y), new Vector2(BodyLeft - 6, sheet.End.Y), MarginColor);
        // the spiral binding along the top edge
        for (float x = Paper.Position.X + 14; x < Paper.End.X - 10; x += 12)
        {
            DrawRect(new Rect2(x, Paper.Position.Y - 4, 4, 9), new Color("b8c0c8"));
            DrawRect(new Rect2(x + 1, Paper.Position.Y - 3, 2, 7), new Color("586068"));
        }
    }

    public override void _Input(InputEvent e)
    {
        if (!IsOpen || e is InputEventKey { Echo: true }) return;
        if (e.IsActionPressed("ui_left")) Turn(-1);
        else if (e.IsActionPressed("ui_right")) Turn(1);
        else if (e.IsActionPressed("ui_cancel") || e.IsActionPressed("toggle_notepad")) Close();
        else return;
        GetViewport().SetInputAsHandled();
    }
}
