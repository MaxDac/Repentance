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
    [InlineData(false, true, true, 3)]
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
    public void RepentingAfterTheShotEndsInJailWhateverTheLeverage()
    {
        Assert.Equal(6, Endings.Resolve(Flags("repented")));
        Assert.Equal(6, Endings.Resolve(Flags("repented", "mansion_exploded", "took_documents")));
        Assert.Equal(1, Endings.Resolve(Flags("spared_oldman", "repented")));
    }

    [Fact]
    public void ShootingEleanorOverridesTheLeverage()
    {
        Assert.Equal(7, Endings.Resolve(Flags("shot_eleanor")));
        Assert.Equal(7, Endings.Resolve(Flags("shot_eleanor", "mansion_exploded", "took_documents")));
    }

    [Fact]
    public void ShootingHimselfWithEleanorAliveIsEndingSeven()
    {
        Assert.Equal(7, Endings.Resolve(Flags("shot_himself")));
        Assert.Equal(7, Endings.Resolve(Flags("shot_himself", "eleanor_refused", "took_documents")));
    }

    [Theory]
    [InlineData(1, true)]
    [InlineData(2, false)]
    [InlineData(5, false)]
    [InlineData(6, true)]
    [InlineData(7, false)]
    [InlineData(8, true)]
    [InlineData(9, true)]
    [InlineData(10, true)]
    [InlineData(11, true)]
    public void OnlyTheRepentantEndingsKeepTheJournal(int ending, bool keeps) =>
        Assert.Equal(keeps, Endings.KeepsJournal(ending));

    private const string Abbess = "eleanor_refused_abbess", Drugs = "eleanor_refused_drugs";

    [Theory]
    // Eleanor's coda: struck and burned, struck only; and her following Micah, worn out, after the shot
    [InlineData(8, Abbess, Drugs, "spared_oldman", "eleanor_struck", "eleanor_burned")]
    [InlineData(9, Abbess, Drugs, "spared_oldman", "eleanor_struck")]
    [InlineData(10, Abbess, Drugs, "shot_oldman", "eleanor_weary", "mansion_exploded")]
    [InlineData(10, Abbess, Drugs, "shot_oldman", "eleanor_weary", "took_documents")]
    [InlineData(11, Abbess, Drugs, "shot_oldman", "eleanor_weary")]
    // the refusals alone never change an outcome
    [InlineData(1, Abbess, Drugs, "gave_up_steps")]
    [InlineData(1, Abbess, Drugs, "walked_away")]
    [InlineData(1, Abbess, Drugs, "spared_oldman")]
    [InlineData(1, Abbess, "gave_up_steps")]
    [InlineData(5, Drugs, "shot_oldman")]
    [InlineData(2, Abbess, "eleanor_convinced", "mansion_exploded")]
    [InlineData(7, Drugs, "shot_eleanor")]
    // the coda's flags win over everything Micah's part could have set
    [InlineData(10, Abbess, Drugs, "eleanor_weary", "eleanor_convinced", "mansion_exploded")]
    [InlineData(11, Abbess, Drugs, "eleanor_weary", "eleanor_convinced")]
    [InlineData(8, Abbess, Drugs, "eleanor_struck", "eleanor_burned", "mansion_exploded", "took_documents")]
    public void EleanorsEndingsTakePrecedence(int ending, params string[] flags) =>
        Assert.Equal(ending, Endings.Resolve(Flags(flags)));

    [Fact]
    public void EleanorHoldsOutOnlyIfSheRefusedBothTimes()
    {
        Assert.True(Endings.EleanorHeldOut(Flags(Abbess, Drugs)));
        Assert.False(Endings.EleanorHeldOut(Flags(Abbess)));
        Assert.False(Endings.EleanorHeldOut(Flags(Drugs)));
        Assert.False(Endings.EleanorHeldOut(Flags()));
    }

    [Fact]
    public void EleanorFollowsWhenConvincedOrWornOut()
    {
        Assert.True(Endings.EleanorFollows(Flags("eleanor_convinced")));
        Assert.True(Endings.EleanorFollows(Flags("eleanor_weary")));
        Assert.False(Endings.EleanorFollows(Flags("eleanor_refused")));
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
        flags.Add("took_faith_ring");
        Assert.Equal(expected, Endings.CanOfferCross(act, Flags(flags.ToArray())));
    }
}
