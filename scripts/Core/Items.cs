using System.Collections.Generic;

namespace Repentance;

public sealed record ItemDef(string Id, string Name, string IconPath, string Description);

/// <summary>Inventory item catalogue. Add new items here and drop a 32x24 icon in assets/art/items.</summary>
public static class Items
{
    public static readonly Dictionary<string, ItemDef> All = new()
    {
        [Notes.ItemId] = new(Notes.ItemId, "notepad", "res://assets/art/items/notepad.png",
            "My notepad. Everything I've learned on the case, in pencil."),
        [MicahKit.LighterId] = new(MicahKit.LighterId, "lighter", "res://assets/art/items/lighter.png",
            "My brass lighter. It's lit more cigarettes than I should have smoked, and it never misses."),
        ["faith_ring"] = new("faith_ring", "wedding ring", "res://assets/art/items/faith_ring.png",
            "My wedding ring. Rose kept her promises. It's time I kept mine."),
        ["cross"] = new("cross", "cross pendant", "res://assets/art/items/cross.png",
            "Caleb's cross, on a silver chain. A reminder that the way back isn't closed."),
        ["photo"] = new("photo", "photograph", "res://assets/art/items/photo.png",
            "Eleanor Harrington. Pretty, poised, and looking at the camera like it owed her money."),
        ["dollar"] = new("dollar", "cash", "res://assets/art/items/dollar.png",
            "My cash for the case. Two dollars for the bellboy; ten to get past Sal."),
        ["matchbook"] = new("matchbook", "matchbook", "res://assets/art/items/matchbook.png",
            "A blue lantern on the cover: The Blue Lantern, State Street. No password inside. A calling card for a speakeasy."),
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
            "Hotel stationery, in Eleanor's hand: \"Those who sat at His table. The days of the month He was born. The day He rested.\" No directions."),
        ["brass_box"] = new("brass_box", "brass box", "res://assets/art/items/brass_box.png",
            "A little brass box, engraved with lilies. Something slides around inside."),
        ["card"] = new("card", "business card", "res://assets/art/items/card.png",
            "A calling card, heavy stock, gilt edges. No name, no address; only two letters lost in the curlicues. It carries her perfume, stronger than anywhere in her room."),
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
        // Puzzle 11 - Aurelian linen room.
        ["hanger"] = new("hanger", "wire hanger", "res://assets/art/items/hanger.png",
            "A laundry hanger, stiff steel wire. Straightened and bent at the end, it would make a fair hook."),
        ["pliers"] = new("pliers", "housekeeping pliers", "res://assets/art/items/pliers.png",
            "Housekeeping's pliers, borrowed off the cart. They'll bend wire. I'll put them back."),
        ["wire_hook"] = new("wire_hook", "wire hook", "res://assets/art/items/wire_hook.png",
            "A straightened hanger with a hook bent into the end. Long enough to reach through a transom."),
        // Puzzle 12 - Rizzo's Flowers.
        ["carnation"] = new("carnation", "white carnation", "res://assets/art/items/carnation.png",
            "A white carnation from Rizzo's bucket, stem still wet. The members here wear blue."),
        ["bluing"] = new("bluing", "laundry bluing", "res://assets/art/items/bluing.png",
            "Mrs. Stewart's Liquid Bluing. Turns grey linen white, and white things blue if you're careless."),
        ["blue_carnation"] = new("blue_carnation", "blue carnation", "res://assets/art/items/blue_carnation.png",
            "A carnation dyed blue through its own stem. A member's buttonhole, as far as a grille can tell."),
        // Puzzle 13 - Tribune morgue.
        ["clipping_top"] = new("clipping_top", "top half of a clipping", "res://assets/art/items/clipping_top.png",
            "\"HARRINGTON BUILDS...\" The headline and half a column, torn straight through the address."),
        ["clipping_bottom"] = new("clipping_bottom", "bottom half of a clipping", "res://assets/art/items/clipping_bottom.png",
            "The bottom of a Tribune column, torn across: \"...Building, LaS\" and a photo caption. It needs its other half."),
        ["paste"] = new("paste", "paste pot", "res://assets/art/items/paste.png",
            "A pot of library paste with a brush in the lid. Every newspaper runs on it."),
        ["clipping"] = new("clipping", "mended clipping", "res://assets/art/items/clipping.png",
            "\"Harrington senior keeps his offices at the Harrington Building, LaSalle Street.\" Somebody ought to put a pin in that."),
        // Puzzle 14 - Club vestibule.
        ["sealing_wax"] = new("sealing_wax", "stick of sealing wax", "res://assets/art/items/sealing_wax.png",
            "Red sealing wax from the coat-check counter. Hard as a church pew until it meets a flame."),
        ["wax_soft"] = new("wax_soft", "softened wax", "res://assets/art/items/wax_soft.png",
            "The end of the wax stick, warm and glossy. It wants something to drip on."),
        ["invitation_waxed"] = new("invitation_waxed", "waxed invitation", "res://assets/art/items/invitation_waxed.png",
            "The invitation with a fat drop of red wax on the fold, waiting for a seal. Procession crests: raven, lion, stag."),
        ["sealed_invitation"] = new("sealed_invitation", "sealed invitation", "res://assets/art/items/sealed_invitation.png",
            "Black card, gold edges, sealed with the raven - first of the procession. My summons."),
        ["signet_raven"] = new("signet_raven", "raven signet", "res://assets/art/items/signet_raven.png",
            "A heavy signet ring with a raven cut into the face. Borrowed from a cloak on the rack."),
        ["signet_lion"] = new("signet_lion", "lion signet", "res://assets/art/items/signet_lion.png",
            "A signet ring cut with a lion. Borrowed from a cloak on the rack."),
        ["signet_stag"] = new("signet_stag", "stag signet", "res://assets/art/items/signet_stag.png",
            "A signet ring cut with a stag. Borrowed from a cloak on the rack."),
        // Puzzle 15 - Harrington wine cellar.
        ["lantern"] = new("lantern", "storm lantern", "res://assets/art/items/lantern.png",
            "A tin storm lantern off the cellar hook. The font is bone dry."),
        ["kerosene"] = new("kerosene", "kerosene can", "res://assets/art/items/kerosene.png",
            "A dented can of kerosene from the delivery crates. It sloshes. Enough for a lantern."),
        ["lantern_filled"] = new("lantern_filled", "filled lantern", "res://assets/art/items/lantern_filled.png",
            "The storm lantern, fuelled and trimmed. It only needs a light."),
        ["lantern_lit"] = new("lantern_lit", "lit lantern", "res://assets/art/items/lantern_lit.png",
            "The storm lantern, burning low and steady. Enough light to find a stair by."),
    };

    public static ItemDef Get(string id) => All[id];
}

public static class CashRules
{
    /// <summary>The bellboy's first dollar buys his memory, the second the staff door to Eleanor's room.</summary>
    public const int BellboyBribe = 1;
    public const int BellboyRoomBribe = 1;
    public const int SalBribe = 10;
    public const int StartingCash = 22;

    public static int Balance(System.Func<string, bool> hasFlag) =>
        !hasFlag("took_dollar") ? 0 : StartingCash
            - (hasFlag("knows_lantern") ? BellboyBribe : 0)
            - (hasFlag("bellboy_room_paid") ? BellboyRoomBribe : 0)
            - (hasFlag("sal_passed") ? SalBribe : 0);
}
