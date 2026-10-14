namespace Repentance;

public static partial class Items
{
    /// <summary>Act 1: the office, the Aurelian Hotel, the Blue Lantern and the convent.</summary>
    private static ItemDef[] Act1Items() => new ItemDef[]
    {
        new("photo", "photograph", "res://assets/art/items/photo.png",
            "Eleanor Harrington. Pretty, poised, and looking at the camera like it owed her money."),
        new("dollar", "cash", "res://assets/art/items/dollar.png",
            "My cash for the case. Two dollars for the bellboy; ten to get past Sal."),
        new("matchbook", "matchbook", "res://assets/art/items/matchbook.png",
            "A blue lantern on the cover: The Blue Lantern, State Street. No password inside. A calling card for a speakeasy."),
        new("crowbar", "crowbar", "res://assets/art/items/crowbar.png",
            "A rusty crowbar. Every attic has one. Nobody knows why."),
        new("journal", "journal", "res://assets/art/items/journal.png",
            "Cracked leather, stamped \"M. Jones\". Somebody wrote a lot in this, and pressed hard."),
        new("key", "room key", "res://assets/art/items/key.png",
            "Brass, heavy, with a red tag: Aurelian Hotel, suite 4. Eleanor's room."),
        new("diary", "diary", "res://assets/art/items/diary.png",
            "Eleanor's diary. Locked with a toy clasp. Some secrets come with training wheels."),
        new("ledger", "ledger", "res://assets/art/items/ledger.png",
            "Harrington Steel's other set of books. The numbers add up. That's the problem."),
        new("mirror_waxed", "waxed mirror", "res://assets/art/items/mirror_waxed.png",
            "A hand mirror whose wooden back is covered in cold wax. Gentle lamplight could soften it; a clean cloth could wipe it away."),
        new("cloth", "borrowed clean cloth", "res://assets/art/items/cloth.png",
            "A clean cloth borrowed from the convent bed. Good for wiping softened wax; I'll return it afterward."),
        new("suitcase_key", "small key", "res://assets/art/items/suitcase_key.png",
            "A small brass key from the lining of an old suitcase. It opens something. Something small."),
        new("revolver", "revolver", "res://assets/art/items/revolver.png",
            "My .38. Loaded, oiled, and as reluctant as its owner."),
        new("lockpick", "lockpicks", "res://assets/art/items/lockpick.png",
            "A roll of lockpicks. A souvenir from a burglar I once let off easy. He said I'd need them more than him."),
        new("combination", "slip of paper", "res://assets/art/items/combination.png",
            "Hotel stationery, in Eleanor's hand: \"Those who sat at His table. The days of the month He was born. The day He rested.\" No directions."),
        new("brass_box", "brass box", "res://assets/art/items/brass_box.png",
            "A little brass box, engraved with lilies. Something slides around inside."),
        new("card", "business card", "res://assets/art/items/card.png",
            "A calling card, heavy stock, gilt edges. No name, no address; only two letters lost in the curlicues. It carries her perfume, stronger than anywhere in her room."),
        new("mirror", "little mirror", "res://assets/art/items/mirror.png",
            "Eleanor's little hand mirror. On the back, scratched into the wood, three loops tied in a knot that never ends."),
        // Puzzle 11 - Aurelian linen room.
        new("hanger", "wire hanger", "res://assets/art/items/hanger.png",
            "A laundry hanger, stiff steel wire. Straightened and bent at the end, it would make a fair hook."),
        new("pliers", "housekeeping pliers", "res://assets/art/items/pliers.png",
            "Housekeeping's pliers, borrowed off the cart. They'll bend wire. I'll put them back."),
        new("wire_hook", "wire hook", "res://assets/art/items/wire_hook.png",
            "A straightened hanger with a hook bent into the end. Long enough to reach through a transom."),
        // Puzzle 12 - Rizzo's Flowers.
        new("carnation", "white carnation", "res://assets/art/items/carnation.png",
            "A white carnation from Rizzo's bucket, stem still wet. The members here wear blue."),
        new("bluing", "laundry bluing", "res://assets/art/items/bluing.png",
            "Mrs. Stewart's Liquid Bluing. Turns grey linen white, and white things blue if you're careless."),
        new("blue_carnation", "blue carnation", "res://assets/art/items/blue_carnation.png",
            "A carnation dyed blue through its own stem. A member's buttonhole, as far as a grille can tell."),
    };
}
