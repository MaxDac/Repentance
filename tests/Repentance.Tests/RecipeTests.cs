using Xunit;

namespace Repentance.Tests;

public class RecipeTests
{
    private static Func<string, bool> Holding(params string[] items) => items.Contains;

    [Fact]
    public void EveryRecipeAndRefusalUsesCataloguedItems()
    {
        foreach (var recipe in Recipes.All)
        {
            Assert.Contains(recipe.A, Items.All.Keys);
            Assert.Contains(recipe.B, Items.All.Keys);
            Assert.Contains(recipe.Result, Items.All.Keys);
            Assert.All(recipe.Consumes, id => Assert.Contains(id, recipe.Inputs));
            Assert.All(recipe.Requires ?? Array.Empty<string>(), id => Assert.Contains(id, Items.All.Keys));
        }
        foreach (var refusal in Recipes.Refusals)
        {
            Assert.Contains(refusal.A, Items.All.Keys);
            Assert.Contains(refusal.B, Items.All.Keys);
            Assert.Null(Recipes.Find(refusal.A, refusal.B));
        }
    }

    [Fact]
    public void PairsAreUniqueAndSymmetric()
    {
        var keys = Recipes.All.Select(r => string.Join("+", new[] { r.A, r.B }.Order())).ToList();
        Assert.Equal(keys.Count, keys.Distinct().Count());
        foreach (var recipe in Recipes.All)
        {
            var held = Holding(recipe.A, recipe.B, "paste");
            Assert.Equal(recipe.Result, Recipes.Evaluate(recipe.A, recipe.B, held)!.Result);
            Assert.Equal(recipe.Result, Recipes.Evaluate(recipe.B, recipe.A, held)!.Result);
        }
    }

    [Fact]
    public void LighterIsNeverConsumedAndTheMatchbookLightsNothing()
    {
        Assert.All(Recipes.All, r => Assert.DoesNotContain(MicahKit.LighterId, r.Consumes));
        Assert.All(Recipes.All.Where(r => r.Inputs.Contains(MicahKit.LighterId)),
            r => Assert.Contains(MicahKit.LighterId, r.Catalysts ?? Array.Empty<string>()));
        Assert.DoesNotContain(Recipes.All, r => r.Inputs.Contains("matchbook"));
    }

    [Fact]
    public void FullChainsEndWithTheUsableItemAndKeepTheLighter()
    {
        var bag = new HashSet<string> { MicahKit.LighterId, "hanger", "pliers", "carnation", "bluing",
            "clipping_top", "clipping_bottom", "paste", "sealing_wax", "invitation", "signet_raven",
            "lantern", "kerosene" };
        void Combine(string a, string b)
        {
            var outcome = Recipes.Evaluate(a, b, bag.Contains);
            Assert.NotNull(outcome?.Result);
            Recipes.Apply(outcome!, id => bag.Remove(id), id => bag.Add(id), _ => { });
        }
        Combine("hanger", "pliers");
        Combine("bluing", "carnation");
        Combine("clipping_bottom", "clipping_top");
        Combine("sealing_wax", MicahKit.LighterId);
        Combine("invitation", "wax_soft");
        Combine("invitation_waxed", "signet_raven");
        Combine("kerosene", "lantern");
        Combine(MicahKit.LighterId, "lantern_filled");
        Assert.Equal(new[] { "blue_carnation", "clipping", "lantern_lit", "lighter", "paste", "sealed_invitation", "wire_hook" },
            bag.Order());
    }

    [Fact]
    public void HalvesWithoutPasteExplainWhatIsMissing()
    {
        var outcome = Recipes.Evaluate("clipping_top", "clipping_bottom", Holding("clipping_top", "clipping_bottom"));
        Assert.NotNull(outcome);
        Assert.Null(outcome!.Result);
        Assert.Contains("hold them together", outcome.Line);
    }

    [Theory]
    [InlineData("sealing_wax", "invitation", "flame")]
    [InlineData("signet_lion", "invitation_waxed", "not first")]
    [InlineData("signet_stag", "invitation_waxed", "first")]
    [InlineData("lantern", "lighter", "fuel")]
    [InlineData("sealing_wax", "matchbook", "lighter")]
    [InlineData("lantern_filled", "matchbook", "lighter")]
    public void WrongCombinationsAreRefusedWithAHint(string a, string b, string hint)
    {
        var outcome = Recipes.Evaluate(a, b, Holding(a, b));
        Assert.NotNull(outcome);
        Assert.Null(outcome!.Result);
        Assert.Empty(outcome.Consumed);
        Assert.Contains(hint, outcome.Line);
    }

    [Fact]
    public void UnheldOrUnknownPairsFallThrough()
    {
        Assert.Null(Recipes.Evaluate("hanger", "pliers", Holding("hanger")));
        Assert.Null(Recipes.Evaluate("photo", "dollar", Holding("photo", "dollar")));
    }
}
