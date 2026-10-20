using System;
using System.Threading.Tasks;
using Godot;

namespace Repentance.Story;

/// <summary>
/// Eleanor's dark brown leather duffle in the First Interlude: she takes it from Room 507 ("interlude_took_bag") and
/// carries it (the "eleanor_bag_play" sheet) to the Blue Lantern and the convent, until she leaves it by the cell's
/// nightstand ("interlude_bag_left"). Before every conversation she sets it down at her feet and takes it back after.
/// </summary>
public static class EleanorBag
{
    public const string Sheet = "eleanor_bag_play";
    public const string Plain = "eleanor_play";
    public const string FloorTexture = "res://assets/art/sprites/duffle_bag.png";
    public const string OpenTexture = "res://assets/art/sprites/duffle_bag_open.png";

    private static Player Player => Game.Instance.Player;
    private static Sprite2D? _floor;
    private static Facing _facing = Facing.Right;

    /// <summary>True while the player is Eleanor with the bag in her hand.</summary>
    public static bool Carrying => Player.Character == Sheet;

    /// <summary>
    /// The bag on the floor where her strips leave it: a full 64x96 frame anchored like hers, a pixel in front of her
    /// feet so the y-sort draws it over her shoes.
    /// </summary>
    public static Sprite2D FloorSprite(Vector2 feet, float scale, bool flipped, bool open = false) => new()
    {
        Texture = GD.Load<Texture2D>(open ? OpenTexture : FloorTexture),
        Centered = false,
        Offset = new Vector2(-32, -94),
        Position = feet + new Vector2(0, 1),
        Scale = Vector2.One * scale,
        FlipH = flipped,
    };

    /// <summary>Sets the bag down at her feet, if she has it, and leaves it there; true when she did.</summary>
    public static async Task<bool> SetDown()
    {
        if (!Carrying || Game.Instance.Room is not { } room) return false;
        if (Player.Facing is not (Facing.Left or Facing.Right)) Player.Face(Facing.Right);
        _facing = Player.Facing;
        await Player.PlayPose("eleanor_bag_down");
        Drop(room);
        Player.SetCharacter(Plain);
        return true;
    }

    /// <summary>Takes the bag back from where <see cref="SetDown"/> left it.</summary>
    public static async Task PickUp()
    {
        Player.Face(_facing);
        Lift();
        Player.SetCharacter(Sheet);
        await Player.PlayPose("eleanor_bag_up");
        Player.SetPose(null);
    }

    /// <summary>
    /// Runs a conversation with the bag at her feet: she sets it down before, takes it back after. Without the bag in
    /// hand the conversation just runs.
    /// </summary>
    public static async Task Around(Func<Task> talk)
    {
        var down = await SetDown();
        try { await talk(); }
        finally
        {
            if (down) await PickUp();
        }
    }

    private static void Drop(Room room)
    {
        Lift();
        _floor = FloorSprite(Player.Position, Player.Scale.Y, _facing == Facing.Left);
        room.World.AddChild(_floor);
    }

    private static void Lift()
    {
        if (_floor != null && GodotObject.IsInstanceValid(_floor)) _floor.QueueFree();
        _floor = null;
    }
}
