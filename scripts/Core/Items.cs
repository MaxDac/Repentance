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
        ["crowbar"] = new("crowbar", "crowbar", "res://assets/art/items/crowbar.png",
            "A rusty crowbar. Every attic has one. Nobody knows why."),
        ["journal"] = new("journal", "journal", "res://assets/art/items/journal.png",
            "Cracked leather, stamped \"M. Jones\". Somebody wrote a lot in this, and pressed hard."),
        ["key"] = new("key", "room key", "res://assets/art/items/key.png",
            "Brass, heavy, with a red tag: Aurelian Hotel, suite 4. Eleanor's room."),
        ["diary"] = new("diary", "diary", "res://assets/art/items/diary.png",
            "Eleanor's diary. Locked with a toy clasp. Some secrets come with training wheels."),
        ["ledger"] = new("ledger", "ledger", "res://assets/art/items/ledger.png",
            "Harrington Steel's other set of books. The numbers add up. That's the problem."),
        ["map"] = new("map", "map", "res://assets/art/items/map.png",
            "A hand-drawn map of the county road. An X past the last fence post, east of town."),
        ["evidence"] = new("evidence", "tin box", "res://assets/art/items/evidence.png",
            "A rusted tin box: Moretti's IOUs, signed by Teddy, and a gold cufflink. T.H."),
    };

    public static ItemDef Get(string id) => All[id];
}
