using Xunit;

namespace Repentance.Tests;

public class ItemsTests
{
    [Fact]
    public void Catalogue_IsNotEmpty() => Assert.NotEmpty(Items.All);

    [Fact]
    public void EveryItem_KeyMatchesIdAndHasContent()
    {
        foreach (var (key, def) in Items.All)
        {
            Assert.Equal(key, def.Id);
            Assert.False(string.IsNullOrWhiteSpace(def.Name));
            Assert.False(string.IsNullOrWhiteSpace(def.Description));
            Assert.StartsWith("res://assets/art/items/", def.IconPath);
        }
    }

    [Fact]
    public void Get_UnknownItem_Throws() =>
        Assert.Throws<KeyNotFoundException>(() => Items.Get("nope"));

    [Theory]
    [InlineData(false, false, false, 0)]
    [InlineData(true, false, false, 22)]
    [InlineData(true, true, false, 21)]
    [InlineData(true, true, true, 11)]
    public void CashTracksCollectedFundsAndEachBribe(bool collected, bool bellboy, bool sal, int expected)
    {
        bool Has(string flag) => flag switch
        {
            "took_dollar" => collected,
            "knows_lantern" => bellboy,
            "sal_passed" => sal,
            _ => false,
        };
        Assert.Equal(expected, CashRules.Balance(Has));
        Assert.Equal(2 * (CashRules.BellboyBribe + CashRules.SalBribe), CashRules.StartingCash);
    }
}
