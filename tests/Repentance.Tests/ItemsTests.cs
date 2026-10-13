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
    [InlineData(false, false, false, false, 0)]
    [InlineData(true, false, false, false, 22)]
    [InlineData(true, true, false, false, 21)]
    [InlineData(true, true, true, false, 20)]
    [InlineData(true, true, true, true, 10)]
    public void CashTracksCollectedFundsAndEachBribe(bool collected, bool bellboy, bool room, bool sal, int expected)
    {
        bool Has(string flag) => flag switch
        {
            "took_dollar" => collected,
            "knows_lantern" => bellboy,
            "bellboy_room_paid" => room,
            "sal_passed" => sal,
            _ => false,
        };
        Assert.Equal(expected, CashRules.Balance(Has));
        Assert.True(CashRules.StartingCash >= CashRules.BellboyBribe + CashRules.BellboyRoomBribe + CashRules.SalBribe);
    }
}
