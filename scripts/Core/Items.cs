using System.Collections.Generic;

namespace Repentance;

public sealed record ItemDef(string Id, string Name, string IconPath, string Description);

/// <summary>Inventory item catalogue. Add new items here and drop a 32x24 icon in assets/art/items.</summary>
public static class Items
{
    public static readonly Dictionary<string, ItemDef> All = new()
    {
        ["photo"] = new("photo", "photograph", "res://assets/art/items/photo.png",
            "Eleanor Harrington. Pretty, poised, and looking at the camera like it owed her money."),
        ["dollar"] = new("dollar", "dollar bill", "res://assets/art/items/dollar.png",
            "One whole dollar. My entire operating budget."),
        ["matchbook"] = new("matchbook", "matchbook", "res://assets/art/items/matchbook.png",
            "A blue lantern on the cover. Inside someone scribbled: \"Sweet Caroline's sister\"."),
    };

    public static ItemDef Get(string id) => All[id];
}
