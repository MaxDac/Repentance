using Godot;

namespace Repentance;

/// <summary>
/// Something in a room the player can interact with. Give it one or more CollisionShape2D /
/// CollisionPolygon2D children to define the clickable area. Room scripts handle custom
/// behaviour by Id; unhandled verbs fall back to sensible default lines.
/// </summary>
[GlobalClass]
public partial class Hotspot : Area2D
{
    [Export] public string Id = "";
    [Export] public string DisplayName = "";
    [Export(PropertyHint.MultilineText)] public string LookText = "";
    /// <summary>Where the player walks to before interacting (room coordinates). Zero = auto.</summary>
    [Export] public Vector2 WalkTo;
    [Export] public Facing Face = Facing.Auto;
    /// <summary>If set, "Walk to"/"Open" moves the player to this room (file name in scenes/rooms).</summary>
    [Export] public string ExitTo = "";
    [Export] public string ExitEntry = "";
    /// <summary>Comma-separated flags that must all be set for this hotspot to exist.</summary>
    [Export] public string ShowIfFlags = "";
    /// <summary>Comma-separated flags; if any is set the hotspot is hidden.</summary>
    [Export] public string HideIfFlags = "";
    /// <summary>Higher wins when hotspots overlap (otherwise the smaller one wins).</summary>
    [Export] public int ClickPriority;

    public bool IsExit => ExitTo != "";

    public bool Active => IsVisibleInTree();

    public virtual bool Contains(Vector2 point)
    {
        foreach (var child in GetChildren())
        {
            if (child is CollisionShape2D cs && cs.Shape != null && !cs.Disabled)
            {
                var local = cs.GlobalTransform.AffineInverse() * point;
                if (cs.Shape.GetRect().HasPoint(local)) return true;
            }
            else if (child is CollisionPolygon2D cp && !cp.Disabled)
            {
                var local = cp.GlobalTransform.AffineInverse() * point;
                if (Geometry2D.IsPointInPolygon(local, cp.Polygon)) return true;
            }
        }
        return false;
    }

    /// <summary>Bounding rectangle in room coordinates.</summary>
    public virtual Rect2 Bounds
    {
        get
        {
            Rect2? r = null;
            foreach (var child in GetChildren())
            {
                Rect2 cr;
                if (child is CollisionShape2D cs && cs.Shape != null)
                    cr = cs.GlobalTransform * cs.Shape.GetRect();
                else if (child is CollisionPolygon2D cp && cp.Polygon.Length > 0)
                {
                    cr = new Rect2(cp.GlobalTransform * cp.Polygon[0], Vector2.Zero);
                    foreach (var p in cp.Polygon) cr = cr.Expand(cp.GlobalTransform * p);
                }
                else continue;
                r = r?.Merge(cr) ?? cr;
            }
            return r ?? new Rect2(GlobalPosition, Vector2.One);
        }
    }

    public string Title => DisplayName != "" ? DisplayName : Id;
}
