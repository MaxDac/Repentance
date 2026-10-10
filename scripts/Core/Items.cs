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
            "A blue lantern on the cover: The Blue Lantern, State Street. No password inside. Just matches."),
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
        ["suitcase_key"] = new("suitcase_key", "small key", "res://assets/art/items/suitcase_key.png",
            "A small brass key from the lining of an old suitcase. It opens something. Something small."),
        ["revolver"] = new("revolver", "revolver", "res://assets/art/items/revolver.png",
            "My .38. Loaded, oiled, and as reluctant as its owner."),
        ["lockpick"] = new("lockpick", "lockpicks", "res://assets/art/items/lockpick.png",
            "A roll of lockpicks. A souvenir from a burglar I once let off easy. He said I'd need them more than him."),
        ["combination"] = new("combination", "slip of paper", "res://assets/art/items/combination.png",
            "Hotel stationery, in Eleanor's hand: \"R 12 - L 31 - R 7\". Not a phone number."),
        ["brass_box"] = new("brass_box", "brass box", "res://assets/art/items/brass_box.png",
            "A little brass box, engraved with lilies. Something slides around inside."),
        ["card"] = new("card", "business card", "res://assets/art/items/card.png",
            "A calling card, heavy stock, gilt edges. No name, no address. Just curlicues, and a perfume that isn't Eleanor's."),
        ["mirror"] = new("mirror", "little mirror", "res://assets/art/items/mirror.png",
            "Eleanor's little hand mirror. On the back, scratched into the wood, three loops tied in a knot that never ends."),
    };

    public static ItemDef Get(string id) => All[id];
}
