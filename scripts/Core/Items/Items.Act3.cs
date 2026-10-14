namespace Repentance;

public static partial class Items
{
    /// <summary>Act 3: the Harrington mansion.</summary>
    private static ItemDef[] Act3Items() => new ItemDef[]
    {
        new("audit_folder", "numbered account register", "res://assets/art/items/audit_folder.png",
            "Harrington Steel - Private. A register of numbered accounts, not the signed evidence. Align the auditor's index at BANK, JUDGE and CAPTAIN on the study desk to locate the payment sheets in the drawer."),
        new("audit_tracing", "auditor's index", "res://assets/art/items/audit_tracing.png",
            "Harrington Steel - Private. A transparent index with BANK, JUDGE and CAPTAIN marks. BANK goes above JUDGE, CAPTAIN left of BANK. Align it on the register at the study desk before entering the bedroom."),
        new("kitchen_key", "iron key", "res://assets/art/items/kitchen_key.png",
            "A black iron key off the lintel of the Harrington kitchen. The mob's delivery boys know where everything is."),
        new("documents", "documents", "res://assets/art/items/documents.png",
            "A folder of Harrington Steel's dirty work: payoffs, a judge's name, a union man who fell off a girder. Insurance."),
        // Puzzle 15 - Harrington wine cellar.
        new("lantern", "storm lantern", "res://assets/art/items/lantern.png",
            "A tin storm lantern off the cellar hook. The font is bone dry."),
        new("kerosene", "kerosene can", "res://assets/art/items/kerosene.png",
            "A dented can of kerosene from the delivery crates. It sloshes. Enough for a lantern."),
        new("lantern_filled", "filled lantern", "res://assets/art/items/lantern_filled.png",
            "The storm lantern, fuelled and trimmed. It only needs a light."),
        new("lantern_lit", "lit lantern", "res://assets/art/items/lantern_lit.png",
            "The storm lantern, burning low and steady. Enough light to find a stair by."),
    };
}
