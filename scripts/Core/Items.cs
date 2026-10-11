using System.Collections.Generic;

namespace Repentance;

public sealed record ItemDef(string Id, string Name, string IconPath, string Description);

/// <summary>Inventory item catalogue. Add new items here and drop a 32x24 icon in assets/art/items.</summary>
public static class Items
{
    public static readonly Dictionary<string, ItemDef> All = new()
    {
        ["faith_ring"] = new("faith_ring", "wedding ring", "res://assets/art/items/faith_ring.png",
            "My wedding ring. Rose kept her promises. It's time I kept mine."),
        ["cross"] = new("cross", "cross pendant", "res://assets/art/items/cross.png",
            "Caleb's cross, on a silver chain. A reminder that the way back isn't closed."),
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
        ["mirror_waxed"] = new("mirror_waxed", "waxed mirror", "res://assets/art/items/mirror_waxed.png",
            "A hand mirror whose wooden back is covered in cold wax. Gentle lamplight could soften it; a clean cloth could wipe it away."),
        ["cloth"] = new("cloth", "borrowed clean cloth", "res://assets/art/items/cloth.png",
            "A clean cloth borrowed from the convent bed. Good for wiping softened wax; I'll return it afterward."),
        ["wedge"] = new("wedge", "packing wedge", "res://assets/art/items/wedge.png",
            "A tapered wooden packing wedge. It could hold the fire-escape spring catch out of the way."),
        ["audit_folder"] = new("audit_folder", "numbered account register", "res://assets/art/items/audit_folder.png",
            "Harrington Steel - Private. A register of numbered accounts, not the signed evidence. Align the auditor's index at BANK, JUDGE and CAPTAIN on the study desk to locate the payment sheets in the drawer."),
        ["audit_tracing"] = new("audit_tracing", "auditor's index", "res://assets/art/items/audit_tracing.png",
            "Harrington Steel - Private. A transparent index with BANK, JUDGE and CAPTAIN marks. BANK goes above JUDGE, CAPTAIN left of BANK. Align it on the register at the study desk before entering the bedroom."),
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
        ["book"] = new("book", "book of Celtic rituals", "res://assets/art/items/book.png",
            "\"Rites of the Old Isles,\" by A. R. Bell. Green leather gone soft as a glove. The same knot is stamped on the cover."),
        ["address"] = new("address", "address", "res://assets/art/items/address.png",
            "The deciphered calling-card address, copied onto a slip: \"The Club, 18 W. Hubbard.\""),
        ["invitation"] = new("invitation", "invitation", "res://assets/art/items/invitation.png",
            "Black card, gold edges. \"The Club. Saturday, at the turning of the night.\" Procession crests, left to right: raven, lion, stag."),
        ["mask"] = new("mask", "white mask", "res://assets/art/items/mask.png",
            "A white porcelain face with nothing behind its eyes. It looks like everybody and nobody."),
        ["cloak"] = new("cloak", "black cloak", "res://assets/art/items/cloak.png",
            "A long black cloak with a deep hood. It smells of cedar and somebody else's cigars."),
        ["kitchen_key"] = new("kitchen_key", "iron key", "res://assets/art/items/kitchen_key.png",
            "A black iron key off the lintel of the Harrington kitchen. The mob's delivery boys know where everything is."),
        ["documents"] = new("documents", "documents", "res://assets/art/items/documents.png",
            "A folder of Harrington Steel's dirty work: payoffs, a judge's name, a union man who fell off a girder. Insurance."),
    };

    public static ItemDef Get(string id) => All[id];
}
