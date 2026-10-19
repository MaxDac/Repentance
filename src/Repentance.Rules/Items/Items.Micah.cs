namespace Repentance;

public static partial class Items
{
    /// <summary>Micah's own things, carried in every act.</summary>
    private static ItemDef[] MicahItems() => new ItemDef[]
    {
        new(Notes.ItemId, "notepad", "res://assets/art/items/notepad.png",
            "My notepad. Everything I've learned on the case, in pencil."),
        new(MicahKit.LighterId, "lighter", "res://assets/art/items/lighter.png",
            "My brass lighter. It's lit more cigarettes than I should have smoked, and it never misses."),
        new("faith_ring", "wedding ring", "res://assets/art/items/faith_ring.png",
            "My wedding ring. Rose kept her promises. It's time I kept mine."),
        new("cross", "cross pendant", "res://assets/art/items/cross.png",
            "Caleb's cross, on a silver chain. A reminder that the way back isn't closed."),
    };
}
