using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>
/// An inventory combination. <see cref="Consumes"/> leave the satchel; <see cref="Catalysts"/> must be held and are
/// never consumed (Micah's lighter lights the wax and the lantern alike). <see cref="Requires"/> are held tools that aren't one of
/// the two combined items (the morgue paste pot); <see cref="Missing"/> explains what is needed when they aren't held.
/// </summary>
public sealed record Recipe(string A, string B, string Result, string[] Consumes, string Line,
    string[]? Catalysts = null, string[]? Requires = null, string? Missing = null, string? Flag = null)
{
    public IEnumerable<string> Inputs => new[] { A, B };
}

/// <summary>A combination that is refused with an in-character hint (wrong signet, cold wax, dry wick).</summary>
public sealed record Refusal(string A, string B, string Line);

public sealed record CombineOutcome(string Line, string? Result, IReadOnlyList<string> Consumed, string? Flag);

/// <summary>Collect-and-combine table for puzzles 11-15. Godot-free so it can be unit tested.</summary>
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
        new("clipping_top", "clipping_bottom", "clipping", new[] { "clipping_top", "clipping_bottom" },
            "A thumb of paste along the tear and the two halves are one story again. The address reads clean.",
            Requires: new[] { "paste" },
            Missing: "Torn straight through the address. I'd need something to hold them together.",
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
    };

    public static readonly Refusal[] Refusals =
    {
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
        if (recipe.Requires != null && !recipe.Requires.All(hasItem))
            return new CombineOutcome(recipe.Missing ?? "I'm missing something.", null, Array.Empty<string>(), null);
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
