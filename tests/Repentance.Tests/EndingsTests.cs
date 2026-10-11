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
        Assert.False(Endings.CanWalkAwayFromBartender(Flags(), Flags("faith_ring")));
        foreach (string visit in new[] { "church_before_office", "church_before_club", "church_act3_return" })
        {
            Assert.True(Endings.CanWalkAwayFromBartender(Flags(visit), Flags("faith_ring")));
            Assert.False(Endings.CanWalkAwayFromBartender(Flags(visit), Flags("cross")));
        }
    }

    [Fact]
    public void SparingTheOldManNeedsChurchAndInsistingWithRose()
    {
        var both = Flags("faith_ring", "cross");
        Assert.False(Endings.CanSpareOldMan(Flags("church_before_club"), both));
        Assert.False(Endings.CanSpareOldMan(Flags("rose_wait"), both));
        Assert.True(Endings.CanSpareOldMan(Flags("rose_wait", "church_before_office"), both));
    }

    [Fact]
    public void ProgressiveGatesCoverEveryFlagAndItemCombination()
    {
        for (int mask = 0; mask < 64; mask++)
        {
            string[] candidates = { "church_before_office", "church_before_club", "church_act3_return", "rose_wait", "faith_ring", "cross" };
            var selected = candidates.Where((_, bit) => (mask & (1 << bit)) != 0).ToArray();
            var flags = Flags(selected.Where(f => f is not ("faith_ring" or "cross")).ToArray());
            var items = Flags(selected.Where(f => f is "faith_ring" or "cross").ToArray());
            bool church = (mask & 7) != 0;
            bool middle = church && (mask & 16) != 0;
            bool late = middle && (mask & 8) != 0 && (mask & 32) != 0;
            Assert.Equal(middle, Endings.CanWalkAwayFromBartender(flags, items));
            Assert.Equal(late, Endings.CanSpareOldMan(flags, items));
            Assert.Equal(1, Endings.Resolve(Flags("gave_up_steps")));
        }
    }

    [Theory]
    [InlineData(1, true, true, false, false)]
    [InlineData(2, false, true, false, false)]
    [InlineData(2, true, false, false, false)]
    [InlineData(2, true, true, false, true)]
    [InlineData(2, true, true, true, false)]
    [InlineData(3, true, false, false, true)]
    [InlineData(3, true, true, false, true)]
    [InlineData(3, true, false, true, false)]
    public void CrossOfferDependsOnActOriginalDecisionAndAcceptance(int act, bool met, bool left, bool accepted, bool expected)
    {
        var flags = new List<string> { left ? "ring_left_act2" : "ring_taken_act2" };
        if (met) flags.Add("caleb_met");
        if (accepted) flags.Add("took_cross");
        Assert.Equal(expected, Endings.CanOfferCross(act, Flags(flags.ToArray())));
        flags.AddRange(new[] { "took_faith_ring", "cross_refused" });
        Assert.Equal(expected, Endings.CanOfferCross(act, Flags(flags.ToArray())));
    }
}
