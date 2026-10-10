using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

public enum PuzzleKind { Lift, Safe, Catalogue, Cipher, Crests, Alignment, Survey }

public partial class PuzzlePanel : Control
{
    private readonly Dictionary<string, Button> _buttons = new();
    private readonly int[] _settings = new int[3];
    private readonly int[] _numbers = new int[3];
    private TaskCompletionSource<bool>? _completion;
    private Label _feedback = null!;
    private Label _clue = null!;
    private int _x, _y, _rotation, _motif;
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
        Array.Clear(_settings);
        Array.Clear(_numbers);
        _x = _y = _rotation = 0;
        _motif = -1;
        Kind = kind;
        _completion = new TaskCompletionSource<bool>();
        var task = _completion.Task;
        Visible = true;
        Game.Instance.Hud.ShowInventory(false);
        Game.Instance.Hud.Wheel.Close();
        Label(kind switch
        {
            PuzzleKind.Lift => "STAFF LIFT - ROUTING",
            PuzzleKind.Safe => "ROOM 507 - SAFE",
            PuzzleKind.Catalogue => "RESTRICTED CATALOGUE",
            PuzzleKind.Cipher => "REFLECTED CALLING CARD",
            PuzzleKind.Crests => "HARRINGTON - FALSE BACK",
            PuzzleKind.Alignment => "COUNTY MAP - TRACING",
            _ => "BURIAL SURVEY - NORTH UP",
        }, 18, 8, 440);
        _feedback = Label("Read the clues. Nothing here is timed.", 18, 244, 440);
        _clue = Label("", 282, 38, 178, 168);
        _clue.AutowrapMode = TextServer.AutowrapMode.WordSmart;
        switch (kind)
        {
            case PuzzleKind.Lift: BuildLift(); break;
            case PuzzleKind.Safe: BuildSafe(); break;
            case PuzzleKind.Catalogue: BuildCatalogue(); break;
            case PuzzleKind.Cipher: BuildCipher(); break;
            case PuzzleKind.Crests: BuildCrests(); break;
            case PuzzleKind.Alignment: BuildAlignment(); break;
            case PuzzleKind.Survey: BuildSurvey(); break;
        }
        Button("reset", "Reset", 18, 218, 68, Reset);
        Button("close", "Close / Esc", 364, 218, 98, () => Finish(false));
        QueueRedraw();
        return task;
    }

    public override void _Input(InputEvent e)
    {
        if (!IsOpen || !e.IsActionPressed("ui_cancel")) return;
        GetViewport().SetInputAsHandled();
        Finish(false);
    }

    private Label Label(string text, float x, float y, float width, float height = 18)
    {
        var label = new Label
        {
            Text = text, Position = new Vector2(x, y), Size = new Vector2(width, height),
            MouseFilter = MouseFilterEnum.Ignore,
        };
        label.AddThemeFontOverride("font", Hud.Font);
        label.AddThemeFontSizeOverride("font_size", 8);
        label.AddThemeColorOverride("font_color", Hud.VerbHover);
        AddChild(label);
        return label;
    }

    private void Button(string id, string text, float x, float y, float width, Action action)
    {
        var button = new Button
        {
            Text = text, Position = new Vector2(x, y), Size = new Vector2(width, 22),
            FocusMode = FocusModeEnum.None,
        };
        button.AddThemeFontOverride("font", Hud.Font);
        button.AddThemeFontSizeOverride("font_size", 8);
        button.Pressed += action;
        AddChild(button);
        _buttons.Add(id, button);
    }

    public Vector2 ButtonCenter(string id) =>
        _buttons.TryGetValue(id, out var button) ? button.GetGlobalRect().GetCenter() :
            throw new ArgumentException($"No puzzle control '{id}'.", nameof(id));

    private void Finish(bool solved)
    {
        var completion = _completion;
        _completion = null;
        Visible = false;
        completion?.TrySetResult(solved);
    }

    private void Submit(bool correct, string wrong)
    {
        if (correct) Finish(true);
        else _feedback.Text = wrong;
    }

    private void Reset()
    {
        Array.Clear(_settings);
        Array.Clear(_numbers);
        _x = _y = _rotation = 0;
        _motif = -1;
        RefreshControls();
        _feedback.Text = "Reset. Your items and clues are still yours.";
        QueueRedraw();
    }

    private void BuildLift()
    {
        _clue.Text = "Trace the diagram from the loading bay to 507. A, B and C each choose an upper or lower route.";
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"s{i}", "", 28, 142 + i * 23, 218, () =>
            {
                _settings[index] = 1 - _settings[index];
                RefreshControls();
                QueueRedraw();
            });
        }
        Button("submit", "Dispatch", 180, 218, 108, () =>
            Submit(PuzzleRules.Lift(_settings), $"Route stops at {PuzzleRules.LiftDestination(_settings)}. Try again."));
        RefreshControls();
    }

    private void BuildSafe()
    {
        _clue.Text = GameState.Instance.HasItem("combination")
            ? "Eleanor's paper:\nR 12\nL 31\nR 7\n\nSet direction and number for each stop. No extra turns required."
            : "The desk drawer may contain the numbers. Close this panel to investigate.";
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            int y = 80 + i * 38;
            Label($"STOP {i + 1}", 24, y - 18, 100);
            Button($"d{i}", "", 24, y, 72, () => { _settings[index] = 1 - _settings[index]; RefreshControls(); });
            Button($"m{i}", "-1", 104, y, 34, () => { _numbers[index] = (_numbers[index] + 39) % 40; RefreshControls(); });
            Button($"n{i}", "", 146, y, 50, () => { _numbers[index] = (_numbers[index] + 1) % 40; RefreshControls(); });
            Button($"t{i}", "+10", 204, y, 44, () => { _numbers[index] = (_numbers[index] + 10) % 40; RefreshControls(); });
        }
        Button("submit", "Turn handle", 180, 218, 108, () =>
            Submit(PuzzleRules.Safe(_settings, _numbers), "The handle holds. Check all three directions and numbers."));
        RefreshControls();
    }

    private void BuildCatalogue()
    {
        _clue.Text = "Mirror: three connected loops.\n\nMotif index:\nCeltic traditions -> A. R. Bell\n\nFind Bell in the author listings.";
        string[] motifs = { "Separate rings", "Celtic traditions", "Four-point knot" };
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"motif{i}", motifs[i], 20, 73 + i * 25, 240, () =>
            {
                _motif = index;
                _feedback.Text = index == 1 ? "Connected triquetra. Now select Bell's entry." : "That plate differs from the mirror's three joined loops.";
            });
        }
        string[] entries = { "Ash: Wells / C-02", "Birch: Groves / C-09", "Bell: Rites / C-17" };
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"entry{i}", entries[i], 20, 148 + i * 23, 240, () =>
                Submit(PuzzleRules.Catalogue(_motif, index), "Match the motif, then the author. Nothing is checked out."));
        }
    }

    private void BuildCipher()
    {
        _clue.Text = "Book's ornament legend:\nFIRST: lily\nSECOND: leaf\nTHIRD: feather\n\nReflection fragments:\nFeather: Hubbard\nLily: The Club\nLeaf: 18 W.";
        BuildWheels(new[] { "Feather", "Lily", "Leaf" }, () =>
            Submit(PuzzleRules.Cipher(_settings), "Those fragments are out of order. Consult the ornament legend."));
    }

    private void BuildCrests()
    {
        var gs = GameState.Instance;
        _clue.Text = (gs.HasItem("invitation") ? "Invitation procession:\nRaven, lion, stag.\n\n" : "Find an invitation in the desk.\n\n") +
            (gs.HasFlag("portrait_key_seen") ? "Portrait's heraldic key:\nRaven = star\nLion = sun\nStag = moon" :
            "Inspect the portrait for the heraldic key.");
        BuildWheels(new[] { "SUN", "MOON", "STAR" }, () =>
            Submit(PuzzleRules.Crests(_settings), "The doors hold. Translate each crest in procession order."));
    }

    private void BuildWheels(string[] labels, Action submit)
    {
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"s{i}", labels[0], 28, 83 + i * 38, 218, () =>
            {
                _settings[index] = (_settings[index] + 1) % 3;
                RefreshControls();
                QueueRedraw();
            });
        }
        Button("submit", "Submit", 180, 218, 108, submit);
    }

    private void BuildAlignment()
    {
        _clue.Text = "Align all THREE marks.\nW: windmill / C: creek\nF: fence gate\nGold: map / Blue: tracing";
        Button("left", "<", 282, 148, 40, () => Move(-1, 0));
        Button("right", ">", 370, 148, 40, () => Move(1, 0));
        Button("up", "^", 326, 125, 40, () => Move(0, -1));
        Button("down", "v", 326, 171, 40, () => Move(0, 1));
        Button("rotate", "Quarter turn", 282, 195, 152, () => { _rotation = (_rotation + 1) % 4; QueueRedraw(); });
        Button("submit", "Join pieces", 180, 218, 108, () =>
            Submit(PuzzleRules.Alignment(_rotation, _x, _y), "All three marks must overlap, not just the X."));
    }

    private void Move(int x, int y)
    {
        _x = Math.Clamp(_x + x, 0, 10);
        _y = Math.Clamp(_y + y, 0, 10);
        QueueRedraw();
    }

    private void BuildSurvey()
    {
        _clue.Text = "NORTH IS UP.\nEach step: 5 paces.\n\nPost: (2,8)\nCreek: (5,10)\n\n30 paces EAST of post.\n10 paces NORTH of creek.\n\nClick a grid point.";
        for (int x = 0; x <= 10; x++)
            for (int y = 0; y <= 10; y++)
            {
                int col = x, row = y;
                var cell = new Button
                {
                    Position = GridPosition(new GridPoint(x, y)) - new Vector2(6, 6),
                    Size = new Vector2(12, 12), Flat = true, FocusMode = FocusModeEnum.None,
                    TooltipText = $"Column {x}, row {y}",
                };
                cell.Pressed += () => { _x = col; _y = row; QueueRedraw(); };
                AddChild(cell);
                _buttons.Add($"cell{x}_{y}", cell);
            }
        Button("submit", "Mark burial", 180, 218, 108, () =>
            Submit(PuzzleRules.Survey(_x, _y), "That point fails the pace/bearing notes. Count from both landmarks."));
    }

    private void RefreshControls()
    {
        for (int i = 0; i < 3; i++)
        {
            if (_buttons.TryGetValue($"s{i}", out var wheel))
                wheel.Text = Kind switch
                {
                    PuzzleKind.Lift => $"{(char)('A' + i)}: {(_settings[i] == 0 ? "UPPER" : "LOWER")}",
                    PuzzleKind.Crests => new[] { "SUN", "MOON", "STAR" }[_settings[i]],
                    _ => new[] { "Feather", "Lily", "Leaf" }[_settings[i]],
                };
            if (_buttons.TryGetValue($"d{i}", out var direction))
                direction.Text = _settings[i] == 0 ? "RIGHT" : "LEFT";
            if (_buttons.TryGetValue($"n{i}", out var number)) number.Text = $"{_numbers[i]} +";
        }
    }

    private static Vector2 GridPosition(GridPoint p) => new(36 + p.X * 14, 64 + p.Y * 14);

    public override void _Draw()
    {
        DrawRect(new Rect2(0, 0, 480, 270), new Color("171821"));
        DrawRect(new Rect2(8, 4, 464, 236), new Color("907346"), false, 2);
        if (Kind is PuzzleKind.Alignment or PuzzleKind.Survey)
        {
            for (int i = 0; i <= 10; i++)
            {
                DrawLine(GridPosition(new GridPoint(i, 0)), GridPosition(new GridPoint(i, 10)), new Color("464c50"));
                DrawLine(GridPosition(new GridPoint(0, i)), GridPosition(new GridPoint(10, i)), new Color("464c50"));
                DrawString(Hud.Font, new Vector2(32 + i * 14, 51), i.ToString(), fontSize: 8, modulate: Hud.VerbHover);
                DrawString(Hud.Font, new Vector2(12, 68 + i * 14), i.ToString(), fontSize: 8, modulate: Hud.VerbHover);
            }
            if (Kind == PuzzleKind.Alignment)
            {
                for (int i = 0; i < 3; i++)
                {
                    var p = GridPosition(PuzzleRules.MapMarks[i]);
                    DrawCircle(p, 5, Hud.VerbHover);
                    DrawString(Hud.Font, p + new Vector2(5, -5), new[] { "W", "C", "F" }[i], fontSize: 8, modulate: Hud.VerbHover);
                    var mark = PuzzleRules.Transform(PuzzleRules.TracingMarks[i], _rotation, _x, _y);
                    if (mark.X is >= 0 and <= 10 && mark.Y is >= 0 and <= 10)
                        DrawArc(GridPosition(mark), 6, 0, Mathf.Tau, 16, new Color("65b8ef"), 2);
                }
                DrawString(Hud.Font, new Vector2(32, 36), $"Offset {_x},{_y}  Turn {_rotation * 90}", fontSize: 8, modulate: Hud.VerbHover);
            }
            else
            {
                DrawString(Hud.Font, GridPosition(new GridPoint(2, 8)) + new Vector2(4, -5), "POST", fontSize: 8, modulate: Hud.VerbHover);
                DrawString(Hud.Font, GridPosition(new GridPoint(5, 10)) + new Vector2(4, -5), "CREEK", fontSize: 8, modulate: Hud.VerbHover);
                DrawCircle(GridPosition(new GridPoint(_x, _y)), 5, new Color("65b8ef"));
            }
        }
        if (Kind == PuzzleKind.Lift)
        {
            var gold = Hud.VerbHover;
            Vector2 a = new(55, 63), b = new(120, 93), c = new(188, 63);
            DrawString(Hud.Font, new Vector2(24, 42), "Loading bay -> A", fontSize: 8, modulate: gold);
            DrawLine(a, new Vector2(25, 80), _settings[0] == 0 ? new Color("65b8ef") : gold, 2);
            DrawLine(a, b, _settings[0] == 1 ? new Color("65b8ef") : gold, 2);
            DrawLine(b, c, _settings[1] == 0 ? new Color("65b8ef") : gold, 2);
            DrawLine(b, new Vector2(150, 123), _settings[1] == 1 ? new Color("65b8ef") : gold, 2);
            DrawLine(c, new Vector2(242, 42), _settings[2] == 0 ? new Color("65b8ef") : gold, 2);
            DrawLine(c, new Vector2(242, 96), _settings[2] == 1 ? new Color("65b8ef") : gold, 2);
            foreach (var (p, text) in new[] { (a, "A"), (b, "B"), (c, "C"),
                (new Vector2(20, 95), "Laundry"), (new Vector2(144, 139), "Kitchen"),
                (new Vector2(218, 36), "507"), (new Vector2(220, 114), "Roof") })
                DrawString(Hud.Font, p + new Vector2(2, -3), text, fontSize: 8, modulate: gold);
        }
        if (Kind == PuzzleKind.Crests)
        {
            for (int i = 0; i < 3; i++)
            {
                var center = new Vector2(258, 94 + i * 38);
                switch (_settings[i])
                {
                    case 0:
                        DrawCircle(center, 7, Hud.VerbHover);
                        for (int j = 0; j < 8; j++)
                        {
                            var ray = Vector2.FromAngle(j * Mathf.Tau / 8);
                            DrawLine(center + ray * 9, center + ray * 12, Hud.VerbHover);
                        }
                        break;
                    case 1:
                        DrawCircle(center, 9, Hud.VerbHover);
                        DrawCircle(center + new Vector2(5, -3), 8, new Color("171821"));
                        break;
                    default:
                        var points = new Vector2[10];
                        for (int j = 0; j < 10; j++)
                            points[j] = center + Vector2.FromAngle(j * Mathf.Tau / 10 - Mathf.Pi / 2) * (j % 2 == 0 ? 11 : 5);
                        DrawColoredPolygon(points, Hud.VerbHover);
                        break;
                }
            }
        }
        if (Kind == PuzzleKind.Catalogue)
        {
            var texture = GD.Load<Texture2D>("res://assets/art/ui/catalogue_plates.png");
            DrawTexture(texture, new Vector2(22, 30));
        }
    }
}
