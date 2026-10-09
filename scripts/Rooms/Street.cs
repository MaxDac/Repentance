using Godot;

namespace Repentance.Rooms;

public partial class Street : Room
{
    private static readonly Texture2D DayBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_day.png");
    private static readonly Texture2D NightBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_night.png");

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is not { } background) return;
        background.Texture = State.HasFlag("is_night") || !State.HasFlag("is_day") ? NightBackground : DayBackground;
    }
}
