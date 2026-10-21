using Godot;
using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// One puzzle shown inside the shared <see cref="PuzzlePanel"/> chrome. The panel owns the frame, title, clue card,
/// feedback strip and the Reset / Submit / Close footer; a screen only builds its own controls in the work area
/// (x 14-272, y 31-204), draws its diagram there, and judges the answer.
/// </summary>
public abstract class PuzzleScreen
{
    protected static readonly Color Gold = Hud.VerbHover;
    protected static readonly Color Blue = new("65b8ef");
    protected static readonly Color Dim = new("464c50");

    protected PuzzlePanel Panel { get; private set; } = null!;
    protected readonly int[] Settings = new int[3];

    public abstract string Title { get; }
    public virtual string SubmitText => "Submit";
    /// <summary>False when picking a control is itself the answer (the catalogue entries).</summary>
    public virtual bool HasSubmit => true;
    public abstract string Clue { get; }

    public static PuzzleScreen For(PuzzleKind kind) => kind switch
    {
        PuzzleKind.Lift => new LiftMazeScreen(),
        PuzzleKind.Safe => new SafeScreen(),
        PuzzleKind.Catalogue => new CatalogueScreen(),
        PuzzleKind.Cipher => new CipherScreen(),
        PuzzleKind.Crests => new CrestsScreen(),
        PuzzleKind.Bell => new BellScreen(),
        PuzzleKind.Alignment => new AlignmentScreen(),
        _ => throw new ArgumentOutOfRangeException(nameof(kind)),
    };

    public void Attach(PuzzlePanel panel)
    {
        Panel = panel;
        Build();
        Refresh();
    }

    protected abstract void Build();

    /// <summary>Called by the footer's submit button: true solves the puzzle, otherwise the message goes to the feedback strip.</summary>
    public abstract (bool Solved, string Feedback) Check();

    public virtual void Reset() => Array.Clear(Settings);

    public virtual void Refresh() { }

    public virtual void Draw(CanvasItem canvas) { }

    protected Button Button(string id, string text, float x, float y, float width, Action action, float height = 22) =>
        Panel.AddButton(id, text, new Rect2(x, y, width, height), () =>
        {
            action();
            Refresh();
            Panel.QueueRedraw();
        });

    protected Label Label(string text, float x, float y, float width) => Panel.AddLabel(text, new Rect2(x, y, width, 14));

    /// <summary>Up/left/right/down pad: 16px buttons on a 3x3 grid (2px gaps, empty middle) centred on (cx, cy).</summary>
    /// <remarks>The same moves also answer the arrow keys and swipes across the work area (see <see cref="Step"/>).</remarks>
    protected void DirectionPad(float cx, float cy, Action<int, int> move)
    {
        const float size = 16, step = size + 2;
        _move = move;
        foreach (var (id, dx, dy) in new[] { ("up", 0, -1), ("left", -1, 0), ("right", 1, 0), ("down", 0, 1) })
            Panel.AddPadButton(id, new Vector2(dx, dy),
                new Rect2(cx - size / 2 + dx * step, cy - size / 2 + dy * step, size, size), () => Step(dx, dy));
    }

    private Action<int, int>? _move;

    /// <summary>The work area: a drag that starts here (not on a control) steers a direction-pad puzzle.</summary>
    public static readonly Rect2 WorkArea = new(14, 31, 258, 173);

    /// <summary>True when the screen has a direction pad, so arrow keys and swipes move it.</summary>
    public bool HasDirections => _move != null;

    /// <summary>Drag distance per step: one diagram cell.</summary>
    public virtual float SwipeStep => 14;

    /// <summary>One direction-pad move, from a pad button, an arrow key or a swipe.</summary>
    public void Step(int dx, int dy)
    {
        if (_move == null) return;
        _move(dx, dy);
        Refresh();
        Panel.QueueRedraw();
    }

    protected void Say(string feedback) => Panel.SetFeedback(feedback);

    protected static void Text(CanvasItem canvas, Vector2 at, string text, Color? color = null) =>
        canvas.DrawString(Hud.Font, at, text, fontSize: 8, modulate: color ?? Gold);

    protected Button? Find(string id) => Panel.FindButton(id);
}

/// <summary>Three cycling wheels, read in order. Cipher, crests and the bell share it.</summary>
public abstract class WheelScreen : PuzzleScreen
{
    protected abstract string[] Options { get; }
    protected virtual string Face(int wheel, int option) => Options[option];

    protected override void Build()
    {
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"s{i}", "", 28, 83 + i * 38, 218, () => Settings[index] = (Settings[index] + 1) % Options.Length);
        }
    }

    public override void Refresh()
    {
        for (int i = 0; i < 3; i++)
            if (Find($"s{i}") is { } wheel) wheel.Text = Face(i, Settings[i]);
    }
}

/// <summary>Issue #51: the staff cage, driven through the Drake's maze of service shafts to the right linen room.</summary>
public sealed class LiftMazeScreen : PuzzleScreen
{
    private const float Cell = 14, OriginX = 28, OriginY = 54;
    private GridPoint _car = LiftMaze.Start;
    private readonly List<GridPoint> _trail = new() { LiftMaze.Start };

    public override string Title => "STAFF LIFT - SERVICE SHAFTS";
    public override string SubmitText => "Dispatch";
    public override string Clue =>
        "The bellboy:\n\"Fifth floor. The linen room right next to 507.\"\n\"Rooms count up west to east.\"\n\n" +
        "Steer the cage from the loading bay (B) through the shafts, then dispatch it. Every floor has a linen room (L).";

    protected override void Build() => DirectionPad(242, 108, (dx, dy) => Drive(dx, dy));

    private void Drive(int dx, int dy)
    {
        if (!LiftMaze.CanMove(_car, dx, dy))
        {
            Say("The cage bumps brick. No shaft that way.");
            return;
        }
        _car = LiftMaze.Move(_car, dx, dy);
        int seen = _trail.IndexOf(_car);
        if (seen >= 0) _trail.RemoveRange(seen + 1, _trail.Count - seen - 1);
        else _trail.Add(_car);
        Say(LiftMaze.IsLinen(_car)
            ? $"A linen room. Floor {LiftMaze.FloorName(_car.Y)}, between rooms {Room(_car.X - 1)} and {Room(_car.X + 1)}."
            : $"Floor {LiftMaze.FloorName(_car.Y)}, behind room {Room(_car.X)}.");
    }

    private string Room(int column) =>
        column < 0 ? "the stairs" : column >= LiftMaze.Width ? "the fire escape" :
        _car.Y == LiftMaze.Height - 1 ? "the boiler" : $"{LiftMaze.FloorName(_car.Y)}{column + 1:D2}";

    public override (bool, string) Check() =>
        LiftMaze.Solved(_car) ? (true, "") :
        LiftMaze.IsLinen(_car) ? (false, $"The cage opens on the wrong linen room: {LiftMaze.Destination(_car)}.") :
        (false, $"The cage would stop at {LiftMaze.Destination(_car)}. Find a linen room first.");

    public override void Reset()
    {
        _car = LiftMaze.Start;
        _trail.Clear();
        _trail.Add(LiftMaze.Start);
    }

    private static Vector2 Corner(int x, int y) => new(OriginX + x * Cell, OriginY + y * Cell);
    public static Vector2 Center(GridPoint p) => Corner(p.X, p.Y) + new Vector2(Cell / 2, Cell / 2);

    public override void Draw(CanvasItem canvas)
    {
        for (int x = 0; x < LiftMaze.Width; x++) Text(canvas, Corner(x, 0) + new Vector2(1, -4), $"{x + 1:D2}");
        for (int y = 0; y < LiftMaze.Height; y++) Text(canvas, Corner(0, y) + new Vector2(-10, 10), LiftMaze.FloorName(y));
        foreach (var p in LiftMaze.Cells())
            if (LiftMaze.IsLinen(p))
            {
                canvas.DrawRect(new Rect2(Corner(p.X, p.Y) + new Vector2(2, 2), new Vector2(Cell - 4, Cell - 4)), new Color("3b3424"));
                Text(canvas, Center(p) + new Vector2(-3, 4), "L");
            }
        Text(canvas, Center(LiftMaze.Start) + new Vector2(-3, 4), "B", Dim.Lightened(0.4f));
        for (int i = 1; i < _trail.Count; i++) canvas.DrawLine(Center(_trail[i - 1]), Center(_trail[i]), Blue, 2);
        var wall = new Color("c9a25e");
        foreach (var p in LiftMaze.Cells())
        {
            var c = Corner(p.X, p.Y);
            if (!LiftMaze.CanMove(p, 1, 0)) canvas.DrawLine(c + new Vector2(Cell, 0), c + new Vector2(Cell, Cell), wall, 2);
            if (!LiftMaze.CanMove(p, 0, 1)) canvas.DrawLine(c + new Vector2(0, Cell), c + new Vector2(Cell, Cell), wall, 2);
            if (p.X == 0) canvas.DrawLine(c, c + new Vector2(0, Cell), wall, 2);
            if (p.Y == 0) canvas.DrawLine(c, c + new Vector2(Cell, 0), wall, 2);
        }
        var car = Center(_car);
        canvas.DrawRect(new Rect2(car - new Vector2(4, 4), new Vector2(8, 8)), Blue);
        canvas.DrawRect(new Rect2(car - new Vector2(4, 4), new Vector2(8, 8)), new Color("171821"), false, 1);
        Text(canvas, new Vector2(28, 184), "B loading bay   L linen room");
        Text(canvas, new Vector2(28, 196), "west: stairs   east: fire escape");
        Text(canvas, new Vector2(231, 74), "CAGE");
    }
}

/// <summary>Issue #53: a three-stop dial; each right stop drops a tumbler. The clue card says nothing of Eleanor's paper.</summary>
public sealed class SafeScreen : PuzzleScreen
{
    private const int DialSize = 50;
    private readonly int[] _numbers = new int[3];

    public override string Title => "ROOM 507 - SAFE";
    public override string SubmitText => "Turn handle";
    public override string Clue => "A three-stop dial, 0 to 49.\n\nIt turns both ways. Listen for the tumblers.";

    protected override void Build()
    {
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            int y = 64 + i * 44;
            Label($"STOP {i + 1}", 26, y - 16, 100);
            Button($"d{i}", "", 24, y, 72, () => Settings[index] = 1 - Settings[index]);
            Button($"m{i}", "-1", 104, y, 34, () => _numbers[index] = (_numbers[index] + DialSize - 1) % DialSize);
            Button($"n{i}", "", 146, y, 50, () => _numbers[index] = (_numbers[index] + 1) % DialSize);
            Button($"t{i}", "+10", 204, y, 44, () => _numbers[index] = (_numbers[index] + 10) % DialSize);
        }
    }

    public override (bool, string) Check()
    {
        if (PuzzleRules.Safe(Settings, _numbers)) return (true, "");
        return (false, PuzzleRules.SafeTumblers(Settings, _numbers) switch
        {
            0 => "The handle holds. Not a single tumbler fell.",
            1 => "One tumbler drops with a click. Then nothing.",
            _ => "Two tumblers click home. The last one slips.",
        });
    }

    public override void Reset()
    {
        base.Reset();
        Array.Clear(_numbers);
    }

    public override void Refresh()
    {
        for (int i = 0; i < 3; i++)
        {
            if (Find($"d{i}") is { } direction) direction.Text = Settings[i] == 0 ? "RIGHT" : "LEFT";
            if (Find($"n{i}") is { } number) number.Text = $"{_numbers[i]} +";
        }
    }
}

public sealed class CatalogueScreen : PuzzleScreen
{
    private int _motif = -1;

    public override string Title => "RESTRICTED CATALOGUE";
    public override string Clue => "Mirror: three connected loops.\n\nMotif index:\nCeltic traditions -> A. R. Bell\n\nFind Bell in the author listings.";

    protected override void Build()
    {
        string[] motifs = { "Separate rings", "Celtic traditions", "Four-point knot" };
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"motif{i}", motifs[i], 24, 74 + i * 22, 236, () =>
            {
                _motif = index;
                Say(index == 1 ? "Connected triquetra. Now select Bell's entry." : "That plate differs from the mirror's three joined loops.");
            }, 20);
        }
        string[] entries = { "Ash: Wells / C-02", "Birch: Groves / C-09", "Bell: Rites / C-17" };
        for (int i = 0; i < 3; i++)
        {
            int index = i;
            Button($"entry{i}", entries[i], 24, 142 + i * 21, 236, () =>
            {
                if (PuzzleRules.Catalogue(_motif, index)) Panel.Solve();
                else Say("Match the motif, then the author. Nothing is checked out.");
            }, 20);
        }
    }

    public override bool HasSubmit => false;
    public override (bool, string) Check() => (false, "Pick the motif, then the author's entry.");

    public override void Reset() => _motif = -1;

    public override void Draw(CanvasItem canvas) =>
        canvas.DrawTexture(GD.Load<Texture2D>("res://assets/art/ui/catalogue_plates.png"), new Vector2(28, 36));
}

public sealed class CipherScreen : WheelScreen
{
    public override string Title => "REFLECTED CALLING CARD";
    public override string Clue => "Book's ornament legend:\nFIRST: lily\nSECOND: leaf\nTHIRD: feather\n\nReflection fragments:\nFeather: Hubbard\nLily: The Club\nLeaf: 18 W.";
    protected override string[] Options { get; } = { "Feather", "Lily", "Leaf" };

    public override (bool, string) Check() =>
        (PuzzleRules.Cipher(Settings), "Those fragments are out of order. Consult the ornament legend.");
}

public sealed class CrestsScreen : WheelScreen
{
    public override string Title => "HARRINGTON - FALSE BACK";
    protected override string[] Options { get; } = { "SUN", "MOON", "STAR" };

    public override string Clue => "Three dials. Three symbols.";

    public override (bool, string) Check() =>
        (PuzzleRules.Crests(Settings), "The doors hold.");

    public override void Draw(CanvasItem canvas)
    {
        for (int i = 0; i < 3; i++)
        {
            var center = new Vector2(258, 94 + i * 38);
            switch (Settings[i])
            {
                case 0:
                    canvas.DrawCircle(center, 7, Gold);
                    for (int j = 0; j < 8; j++)
                    {
                        var ray = Vector2.FromAngle(j * Mathf.Tau / 8);
                        canvas.DrawLine(center + ray * 9, center + ray * 12, Gold);
                    }
                    break;
                case 1:
                    canvas.DrawCircle(center, 9, Gold);
                    canvas.DrawCircle(center + new Vector2(5, -3), 8, new Color("171a22"));
                    break;
                default:
                    var points = new Vector2[10];
                    for (int j = 0; j < 10; j++)
                        points[j] = center + Vector2.FromAngle(j * Mathf.Tau / 10 - Mathf.Pi / 2) * (j % 2 == 0 ? 11 : 5);
                    canvas.DrawColoredPolygon(points, Gold);
                    break;
            }
        }
    }
}

public sealed class BellScreen : WheelScreen
{
    public override string Title => "MANSION - ALARM HAMMER";
    public override string Clue => "The taut wire holds a spring-loaded hammer.\nCut it: the gong rings.\n\nA tie can secure the hammer to its bracket, but only while held back.\n\nPlan three steps.";
    protected override string[] Options { get; } = { "Hold hammer", "Tie hammer", "Release hand", "Cut wire" };
    protected override string Face(int wheel, int option) => $"{wheel + 1}. {Options[option]}";

    public override (bool, string) Check() =>
        (PuzzleRules.Bell(Settings), "I stop before touching it. Nothing rings. The hammer needs restraint.");

    public override void Draw(CanvasItem canvas)
    {
        canvas.DrawLine(new Vector2(28, 54), new Vector2(138, 54), Gold, 2);
        canvas.DrawRect(new Rect2(136, 46, 24, 16), Blue);
        canvas.DrawArc(new Vector2(222, 56), 10, -Mathf.Pi / 2, Mathf.Pi / 2, 16, Gold, 3);
        Text(canvas, new Vector2(28, 44), "TAUT WIRE");
        Text(canvas, new Vector2(126, 76), "HAMMER");
        Text(canvas, new Vector2(210, 76), "GONG");
    }
}

public sealed class AlignmentScreen : PuzzleScreen
{
    private int _x, _y, _rotation;
    private static readonly string[] Marks = { "B", "J", "C" };

    public override string Title => "HARRINGTON - AUDITOR'S INDEX";
    public override string SubmitText => "Read accounts";
    public override string Clue => "Gold: register\nBlue: index\nB: BANK / J: JUDGE\nC: CAPTAIN\nBANK above JUDGE.\nCAPTAIN left of BANK.";

    protected override void Build()
    {
        DirectionPad(233, 106, Move);
        Button("rotate", "Rotate", 205, 140, 56, () => _rotation = (_rotation + 1) % 4);
    }

    private void Move(int x, int y)
    {
        _x = Math.Clamp(_x + x, 0, 10);
        _y = Math.Clamp(_y + y, 0, 10);
    }

    public override (bool, string) Check() =>
        (PuzzleRules.Alignment(_rotation, _x, _y), "Match all three labelled marks to identify the signed sheets.");

    public override void Reset() => _x = _y = _rotation = 0;

    private static Vector2 GridPosition(GridPoint p) => new(40 + p.X * 14, 56 + p.Y * 14);

    public override void Draw(CanvasItem canvas)
    {
        for (int i = 0; i <= 10; i++)
        {
            canvas.DrawLine(GridPosition(new GridPoint(i, 0)), GridPosition(new GridPoint(i, 10)), Dim);
            canvas.DrawLine(GridPosition(new GridPoint(0, i)), GridPosition(new GridPoint(10, i)), Dim);
            Text(canvas, new Vector2(37 + i * 14, 50), i.ToString());
            Text(canvas, new Vector2(24, 59 + i * 14), i.ToString());
        }
        for (int i = 0; i < 3; i++)
        {
            var p = GridPosition(PuzzleRules.AccountMarks[i]);
            canvas.DrawCircle(p, 5, Gold);
            Text(canvas, p + new Vector2(5, -5), Marks[i]);
            var mark = PuzzleRules.Transform(PuzzleRules.TracingMarks[i], _rotation, _x, _y);
            if (mark.X is >= 0 and <= 10 && mark.Y is >= 0 and <= 10)
            {
                var position = GridPosition(mark);
                canvas.DrawArc(position, 6, 0, Mathf.Tau, 16, Blue, 2);
                Text(canvas, position + new Vector2(-10, 12), Marks[i], Blue);
            }
        }
        Text(canvas, new Vector2(203, 180), $"Offset {_x},{_y}");
        Text(canvas, new Vector2(203, 192), $"Turn {_rotation * 90}");
    }
}
