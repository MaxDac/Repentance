namespace Repentance;

public static partial class Items
{
    /// <summary>Act 2: the library, the Tribune morgue, the Harrington office and the Club vestibule.</summary>
    private static ItemDef[] Act2Items() => new ItemDef[]
    {
        new("wedge", "packing wedge", "res://assets/art/items/wedge.png",
            "A tapered wooden packing wedge. It could hold the fire-escape spring catch out of the way."),
        new("book", "book of Celtic rituals", "res://assets/art/items/book.png",
            "\"Rites of the Old Isles,\" by A. R. Bell. Green leather gone soft as a glove. The same knot is stamped on the cover."),
        new("address", "address", "res://assets/art/items/address.png",
            "The deciphered calling-card address, copied onto a slip: \"The Club, 18 W. Hubbard.\""),
        new("invitation", "invitation", "res://assets/art/items/invitation.png",
            "Black card, gold edges. \"The Club. Thursday, at the turning of the night.\" Procession crests, left to right: raven, lion, stag."),
        new("mask", "white Bauta mask", "res://assets/art/items/mask.png",
            "A white Venetian Bauta: heavy brow, empty eyes, a long nose, and nothing below it but shadow. It looks like everybody and nobody."),
        new("cloak", "black cloak", "res://assets/art/items/cloak.png",
            "A long black cloak with a deep hood. It smells of cedar and somebody else's cigars."),
        // Puzzle 13 - Tribune morgue.
        new("clipping_top", "top half of a clipping", "res://assets/art/items/clipping_top.png",
            "\"HARRINGTON BUILDS...\" The headline and half a column, torn straight through the address."),
        new("clipping_bottom", "bottom half of a clipping", "res://assets/art/items/clipping_bottom.png",
            "The bottom of a Tribune column, torn across: \"...Building, LaS\" and a photo caption. It needs its other half."),
        new("paste", "paste pot", "res://assets/art/items/paste.png",
            "A pot of library paste with a brush in the lid. Every newspaper runs on it."),
        new("clipping", "mended clipping", "res://assets/art/items/clipping.png",
            "\"Harrington senior keeps his offices at the Harrington Building, LaSalle Street.\" Somebody ought to put a pin in that."),
        // Puzzle 14 - Club vestibule.
        new("sealing_wax", "stick of sealing wax", "res://assets/art/items/sealing_wax.png",
            "Red sealing wax from the coat-check counter. Hard as a church pew until it meets a flame."),
        new("wax_soft", "softened wax", "res://assets/art/items/wax_soft.png",
            "The end of the wax stick, warm and glossy. It wants something to drip on."),
        new("invitation_waxed", "waxed invitation", "res://assets/art/items/invitation_waxed.png",
            "The invitation with a fat drop of red wax on the fold, waiting for a seal. Procession crests: raven, lion, stag."),
        new("sealed_invitation", "sealed invitation", "res://assets/art/items/sealed_invitation.png",
            "Black card, gold edges, sealed with the raven - first of the procession. My summons."),
        new("signet_raven", "raven signet", "res://assets/art/items/signet_raven.png",
            "A heavy signet ring with a raven cut into the face. Borrowed from a cloak on the rack."),
        new("signet_lion", "lion signet", "res://assets/art/items/signet_lion.png",
            "A signet ring cut with a lion. Borrowed from a cloak on the rack."),
        new("signet_stag", "stag signet", "res://assets/art/items/signet_stag.png",
            "A signet ring cut with a stag. Borrowed from a cloak on the rack."),
        // Puzzle 17 - Room 507, First Interlude. Eleanor's own things, in her own words.
        new("eleanor_box", "open brass box", "res://assets/art/items/eleanor_box.png",
            "My brass box, lid up. The card, the matchbook, the bluing. Not enough yet to get a reporter past the door."),
        new("pellet", "bare paper flower", "res://assets/art/items/pellet.png",
            "A water flower, folded tight. The word's inked inside, where only water will find it. Bare, it's just a sweet."),
        new("riddle_scrap", "scrap of stationery", "res://assets/art/items/riddle_scrap.png",
            "Aurelian notepaper, torn small. In my hand: \"Give me a drink and I'll tell you the word.\""),
        new("red_thread", "red thread", "res://assets/art/items/red_thread.png",
            "A length of red silk thread from the hem of my good dress. It was coming down anyway."),
        new("eleanor_flower", "wrapped water flower", "res://assets/art/items/water_flower.png",
            "The pellet with the riddle round it, tied in red. A reporter will know to drown it. Theodore's men won't look twice."),
        new("eleanor_box_packed", "packed brass box", "res://assets/art/items/brass_box.png",
            "The brass box, shut on everything. The card, the matchbook, the bluing, the flower. It belongs in the safe."),
        new("eleanor_slip", "blank slip of paper", "res://assets/art/items/eleanor_slip.png",
            "A slip of Aurelian notepaper, still blank. The safe's combination goes on it, in words nobody else would count."),
        new("eleanor_riddle", "slip of paper", "res://assets/art/items/combination.png",
            "Sunday school in my own hand. His Apostles, His days in the desert, His week of creation. It goes in the drawer."),
        new("eleanor_key", "little brass key", "res://assets/art/items/eleanor_key.png",
            "The only key to the lock I had fitted to the desk drawer. It goes where I go."),
    };
}
