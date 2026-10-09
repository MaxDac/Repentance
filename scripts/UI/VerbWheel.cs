using Godot;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Right-click verb wheel: four brass discs around the cursor. Pick a verb either by releasing the right
/// button over an icon (press-drag-release) or by clicking an icon; clicking elsewhere cancels.
/// </summary>
public partial class VerbWheel : Control
{
    private const float Radius = 22, HitRadius = 15;
    private static readonly Vector2 SlotSize = new(32, 32);

    private readonly TextureRect[] _slots = new TextureRect[4];
    private Texture2D _slotTex = null!, _slotHi = null!;
    private Label _label = null!;
    private Vector2 _center;
    private int _hover = -1;
    private string _object = "";
    private ulong _openedAt;
    private TaskCompletionSource<Verb?>? _tcs;

    public bool IsOpen => _tcs != null;

    public override void _Ready()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;
        Visible = false;
        _slotTex = GD.Load<Texture2D>("res://assets/art/ui/wheel_slot.png");
        _slotHi = GD.Load<Texture2D>("res://assets/art/ui/wheel_slot_hi.png");
        for (int i = 0; i < 4; i++)
        {
            var slot = new TextureRect { Texture = _slotTex, MouseFilter = MouseFilterEnum.Ignore };
            slot.AddChild(new TextureRect
            {
                Texture = GD.Load<Texture2D>(Verbs.Icon(Verbs.Wheel[i])),
                Position = new Vector2(4, 4),
                MouseFilter = MouseFilterEnum.Ignore,
            });
            AddChild(slot);
            _slots[i] = slot;
        }
        _label = Hud.MakeOutlinedLabel(Hud.VerbHover);
        AddChild(_label);
    }

    /// <summary>Slot centre for a wheel verb, in screen coordinates (used by the autoplay test).</summary>
    public Vector2 SlotCenter(Verb v)
    {
        int i = System.Array.IndexOf(Verbs.Wheel, v);
        var dir = i switch { 0 => Vector2.Up, 1 => Vector2.Right, 2 => Vector2.Down, _ => Vector2.Left };
        return _center + dir * Radius;
    }

    public Task<Verb?> Open(Vector2 at, string objectName)
    {
        _tcs?.TrySetResult(null);
        var vp = GetViewportRect().Size;
        const float m = Radius + 17;
        _center = new Vector2(Mathf.Clamp(at.X, m, vp.X - m), Mathf.Clamp(at.Y, m, vp.Y - m - 10));
        _object = objectName;
        for (int i = 0; i < 4; i++)
            _slots[i].Position = (SlotCenter(Verbs.Wheel[i]) - SlotSize / 2).Round();
        _hover = -1;
        UpdateHover(at);
        _openedAt = Time.GetTicksMsec();
        Visible = true;
        _tcs = new TaskCompletionSource<Verb?>();
        return _tcs.Task;
    }

    public void Close(Verb? result = null)
    {
        Visible = false;
        var tcs = _tcs;
        _tcs = null;
        tcs?.TrySetResult(result);
    }

    private int SlotAt(Vector2 p)
    {
        for (int i = 0; i < 4; i++)
            if (p.DistanceTo(SlotCenter(Verbs.Wheel[i])) <= HitRadius) return i;
        return -1;
    }

    private void UpdateHover(Vector2 p)
    {
        _hover = SlotAt(p);
        for (int i = 0; i < 4; i++) _slots[i].Texture = i == _hover ? _slotHi : _slotTex;
        _label.Text = _hover < 0 ? _object : $"{Verbs.Label(Verbs.Wheel[_hover])} {_object}";
        var size = _label.GetMinimumSize();
        var pos = new Vector2(_center.X - size.X / 2, _center.Y + Radius + 17);
        pos.X = Mathf.Clamp(pos.X, 2, GetViewportRect().Size.X - size.X - 2);
        _label.Position = pos.Round();
    }

    public override void _GuiInput(InputEvent e)
    {
        if (!IsOpen) return;
        switch (e)
        {
            case InputEventMouseMotion mm:
                UpdateHover(mm.Position);
                break;
            case InputEventMouseButton { ButtonIndex: MouseButton.Right, Pressed: false } mb:
                // press-drag-release; a quick click just leaves the wheel open
                if (SlotAt(mb.Position) is var s and >= 0 && Time.GetTicksMsec() - _openedAt > 150)
                    Close(Verbs.Wheel[s]);
                break;
            case InputEventMouseButton { Pressed: true } mb:
                var slot = SlotAt(mb.Position);
                Close(slot >= 0 && mb.ButtonIndex == MouseButton.Left ? Verbs.Wheel[slot] : null);
                break;
        }
        AcceptEvent();
    }
}
