using Xunit;

namespace Repentance.Tests;

public class EndingsTests
{
    private static Func<string, bool> Flags(params string[] set) => f => Array.IndexOf(set, f) >= 0;

    [Theory]
    [InlineData("gave_up_steps")]
    [InlineData("walked_away")]
    [InlineData("spared_oldman")]
    public void GivingUpAnywhereLeadsBackToRose(string flag)
    {
        Assert.Equal(1, Endings.Resolve(Flags(flag)));
        Assert.Equal(1, Endings.Resolve(Flags(flag, "eleanor_convinced", "mansion_exploded")));
    }

    [Theory]
    [InlineData(true, true, false, 2)]
    [InlineData(true, false, true, 2)]
    [InlineData(true, true, true, 2)]
    [InlineData(false, true, false, 3)]
    [InlineData(false, false, true, 3)]
    [InlineData(true, false, false, 4)]
    [InlineData(false, false, false, 5)]
    public void ShootingTheOldManEndsByEleanorAndLeverage(bool convinced, bool exploded, bool documents, int ending)
    {
        var flags = new List<string>();
        if (convinced) flags.Add("eleanor_convinced");
        if (exploded) flags.Add("mansion_exploded");
        if (documents) flags.Add("took_documents");
        Assert.Equal(ending, Endings.Resolve(Flags(flags.ToArray())));
    }

    [Fact]
    public void WalkingAwayNeedsAChurchReturn()
    {
        Assert.False(Endings.CanWalkAwayFromBartender(Flags()));
        Assert.True(Endings.CanWalkAwayFromBartender(Flags("church_before_office")));
        Assert.True(Endings.CanWalkAwayFromBartender(Flags("church_before_club")));
    }

    [Fact]
    public void SparingTheOldManNeedsChurchAndInsistingWithRose()
    {
        Assert.False(Endings.CanSpareOldMan(Flags("church_before_club")));
        Assert.False(Endings.CanSpareOldMan(Flags("rose_wait")));
        Assert.True(Endings.CanSpareOldMan(Flags("rose_wait", "church_before_office")));
    }
}
