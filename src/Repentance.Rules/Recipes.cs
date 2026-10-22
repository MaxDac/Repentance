using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>
/// An inventory combination of exactly two items. <see cref="Consumes"/> leave the satchel; <see cref="Catalysts"/>
/// must be held and are never consumed (Micah's lighter lights the wax and the lantern alike, the morgue paste pot
/// pastes either half). A puzzle that needs three things joins two, then the result with the third.
/// </summary>
public sealed record Recipe(string A, string B, string Result, string[] Consumes, string Line,
    string[]? Catalysts = null, string? Flag = null)
{
    public IEnumerable<string> Inputs => new[] { A, B };
}

/// <summary>A combination that is refused with an in-character hint (wrong signet, cold wax, dry wick).</summary>
public sealed record Refusal(string A, string B, string Line);

public sealed record CombineOutcome(string Line, string? Result, IReadOnlyList<string> Consumed, string? Flag);

/// <summary>Collect-and-combine table for puzzles 11-15, 17 and 18. Godot-free so it can be unit tested.</summary>
public static class Recipes
{
    public static readonly Recipe[] All =
    {
        // 11 - Aurelian linen room.
        new("hanger", "pliers", "wire_hook", new[] { "hanger", "pliers" },
            "I twist the hanger straight and bend a hook into the end with the pliers. The pliers go back on the cart.",
            Flag: "made_wire_hook"),
        // 12 - Rizzo's Flowers.
        new("carnation", "bluing", "blue_carnation", new[] { "carnation", "bluing" },
            "A splash of bluing in the stem water, a minute's wait, and the carnation drinks itself blue. The vial is empty now.",
            Flag: "made_blue_carnation"),
        // 13 - Tribune morgue.
        // Two at a time: paste on either half, then the pasted half onto the other. The paste pot is only borrowed.
        new("paste", "clipping_top", "clipping_top_pasted", new[] { "clipping_top" },
            "A thumb of paste along the torn edge. It'll stay tacky long enough to find its other half.",
            Catalysts: new[] { "paste" }),
        new("paste", "clipping_bottom", "clipping_bottom_pasted", new[] { "clipping_bottom" },
            "A thumb of paste along the torn edge. It'll stay tacky long enough to find its other half.",
            Catalysts: new[] { "paste" }),
        new("clipping_top_pasted", "clipping_bottom", "clipping", new[] { "clipping_top_pasted", "clipping_bottom" },
            "Edge to edge, a press of the thumb, and the two halves are one story again. The address reads clean.",
            Flag: "mended_clipping"),
        new("clipping_bottom_pasted", "clipping_top", "clipping", new[] { "clipping_bottom_pasted", "clipping_top" },
            "Edge to edge, a press of the thumb, and the two halves are one story again. The address reads clean.",
            Flag: "mended_clipping"),
        // 14 - Club vestibule.
        new(MicahKit.LighterId, "sealing_wax", "wax_soft", new[] { "sealing_wax" },
            "I hold the lighter under the stick until the end goes glossy and soft. The lighter goes back in my pocket.",
            Catalysts: new[] { MicahKit.LighterId }, Flag: "wax_softened"),
        new("wax_soft", "invitation", "invitation_waxed", new[] { "wax_soft", "invitation" },
            "A fat red drop of wax on the fold of the invitation. It won't stay soft for ever. It'll wait for a seal, though."),
        new("signet_raven", "invitation_waxed", "sealed_invitation", new[] { "signet_raven", "invitation_waxed" },
            "The raven presses clean into the wax. First of the procession. I hang the ring back in its cloak.",
            Flag: "invitation_sealed"),
        // 15 - Harrington wine cellar.
        new("lantern", "kerosene", "lantern_filled", new[] { "lantern", "kerosene" },
            "I fill the lantern's font from the can and trim the wick. Smells like every garage in Cicero."),
        new("lantern_filled", MicahKit.LighterId, "lantern_lit", new[] { "lantern_filled" },
            "One flick of the lighter, a careful hand on the chimney, and the cellar finds its edges again.",
            Catalysts: new[] { MicahKit.LighterId }, Flag: "lantern_lit"),
        // 17 - Room 507, First Interlude (Eleanor). The riddle round the pellet, then the thread round both.
        new("pellet", "riddle_scrap", "pellet_wrapped", new[] { "pellet", "riddle_scrap" },
            "The riddle round the pellet, words inward. It won't stay wrapped on its own. I need something to tie it with."),
        new("pellet_wrapped", "red_thread", "eleanor_flower", new[] { "pellet_wrapped", "red_thread" },
            "The red thread round both, twice, in a bow. A sweet nobody would eat."),
        new("eleanor_flower", "eleanor_box", "eleanor_box_packed", new[] { "eleanor_flower", "eleanor_box" },
            "The flower in with the card, the matchbook and the bluing. Lid down. Everything the Tribune would need to find their Club, if they ever drag me back.",
            Flag: "interlude_box_packed"),
        // 18 - The Club's dressing room, Second Interlude (Eleanor).
        new("compact", "puff", "puff_powdered", new[] { "compact", "puff" },
            "The puff into the cake, a tap on the rim. A cloud of face powder, the colour they like me best."),
    };

    public static readonly Refusal[] Refusals =
    {
        new("clipping_top", "clipping_bottom", "Torn straight through the address. I'd need something to hold them together."),
        new("paste", "clipping_top_pasted", "That edge is pasted already. It wants its other half, not more paste."),
        new("paste", "clipping_bottom_pasted", "That edge is pasted already. It wants its other half, not more paste."),
        new("clipping_top_pasted", "clipping_bottom_pasted", "One pasted edge is plenty. Any more and the address drowns in it."),
        new("paste", "clipping", "It's mended. Any more paste and it'll stick to my fingers instead."),
        new("sealing_wax", "invitation", "Hard as a church pew. Needs a flame."),
        new("signet_raven", "invitation", "There's no wax on it to take the seal."),
        new("signet_lion", "invitation_waxed", "The lion. Second in line - not first."),
        new("signet_stag", "invitation_waxed", "The stag walks last in the procession. The plaque wants the first."),
        new("signet_lion", "invitation", "No wax, and the wrong bird. Or beast."),
        new("signet_stag", "invitation", "No wax, and the wrong beast."),
        new("lantern", MicahKit.LighterId, "Dry wick. Needs fuel first."),
        new("carnation", MicahKit.LighterId, "Burning it won't make it blue."),
        // the matchbook is a clue now; an old save that still carries one is pointed at the lighter
        new("sealing_wax", "matchbook", "These matches are the Blue Lantern's calling card. My lighter will do the job."),
        new("lantern_filled", "matchbook", "I'll keep the Blue Lantern's matches. My lighter will do the job."),
        // Eleanor's puzzles: wrap the pellet before it goes in the box; powder needs the puff
        new("pellet", "eleanor_box", "Bare, it's a sweet in a box. It needs a word to go with it."),
        new("riddle_scrap", "eleanor_box", "A riddle with nothing to answer it. The flower first."),
        new("red_thread", "pellet", "Thread round a bare pellet. It needs the riddle wrapped round it first."),
        new("red_thread", "riddle_scrap", "The thread's to tie the riddle round something. The little pellet."),
        new("red_thread", "eleanor_box", "The box locks on its own. The thread's for the flower."),
        new("pellet_wrapped", "eleanor_box", "Loose like that, the riddle will slip off in the box. It needs tying first."),
        new("eleanor_riddle", "eleanor_box", "The combination doesn't go in with what it guards. It goes in the drawer."),
        new("eleanor_riddle", "eleanor_box_packed", "The combination doesn't go in with what it guards. It goes in the drawer."),
        new("eleanor_slip", "riddle_scrap", "Two slips, two riddles. One for the flower, one for the safe. The desk first."),
        new("eleanor_key", "eleanor_box", "That key's for the desk drawer, not the box."),
        new("compact", "lipstick", "Powder first, then the mouth. And I'll need the puff for the powder."),
        new("puff", "lipstick", "The puff's for powder, not for lips."),
    };

    public static bool Matches(string first, string second, string a, string b) =>
        (first == a && second == b) || (first == b && second == a);

    public static Recipe? Find(string first, string second) =>
        All.FirstOrDefault(r => Matches(first, second, r.A, r.B));

    /// <summary>Resolves a combination; null when the pair is not part of the table.</summary>
    public static CombineOutcome? Evaluate(string first, string second, Func<string, bool> hasItem)
    {
        if (!hasItem(first) || !hasItem(second)) return null;
        var recipe = Find(first, second);
        if (recipe == null)
        {
            var refusal = Refusals.FirstOrDefault(r => Matches(first, second, r.A, r.B));
            return refusal == null ? null : new CombineOutcome(refusal.Line, null, Array.Empty<string>(), null);
        }
        return new CombineOutcome(recipe.Line, recipe.Result, recipe.Consumes, recipe.Flag);
    }

    /// <summary>Applies an outcome to inventory/flags through the supplied callbacks.</summary>
    public static void Apply(CombineOutcome outcome, Action<string> take, Action<string> give, Action<string> setFlag)
    {
        if (outcome.Result == null) return;
        foreach (var item in outcome.Consumed) take(item);
        give(outcome.Result);
        if (outcome.Flag != null) setFlag(outcome.Flag);
    }
}
