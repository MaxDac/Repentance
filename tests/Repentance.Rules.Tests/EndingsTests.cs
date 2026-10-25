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

    [Theory]
    [InlineData(true, 3)]
    [InlineData(false, 5)]
    public void RefusalFlagDoesNotChangeTheOrdinaryEndings(bool free, int ending)
    {
        var flags = new List<string> { "eleanor_refused" };
        if (free) flags.Add("took_documents");
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
    [InlineData(12, true)]
    [InlineData(13, false)]
    [InlineData(14, false)]
    public void OnlyTheRepentantEndingsKeepTheJournal(int ending, bool keeps) =>
        Assert.Equal(keeps, Endings.KeepsJournal(ending));

    [Theory]
    // turning himself in at Caleb's church, or after the Our Father; with or without the papers
    [InlineData(12, "shot_bartender", "killed_tony", "surrendered_tony")]
    [InlineData(12, "shot_bartender", "killed_tony", "confessed_tony", "spared_oldman")]
    [InlineData(12, "shot_bartender", "killed_tony", "confessed_tony", "spared_oldman", "took_documents")]
    // Eleanor's coda returning to bed after the prayer is 12 too; striking him is still hers
    [InlineData(12, Abbess, Drugs, "killed_tony", "confessed_tony", "spared_oldman")]
    [InlineData(8, Abbess, Drugs, "killed_tony", "confessed_tony", "spared_oldman", "eleanor_struck", "eleanor_burned")]
    [InlineData(9, Abbess, Drugs, "killed_tony", "confessed_tony", "spared_oldman", "eleanor_struck")]
    // straight to the mansion after killing Tony: the shoot endings are unchanged
    [InlineData(3, "killed_tony", "shot_oldman", "mansion_exploded")]
    [InlineData(5, "killed_tony", "shot_oldman")]
    [InlineData(6, "killed_tony", "confessed_tony", "repented")]
    // Tony left alive changes no outcome
    [InlineData(1, "shot_bartender", "spared_oldman")]
    public void KillingTonyEndsInPrisonWhenMicahRepents(int ending, params string[] flags) =>
        Assert.Equal(ending, Endings.Resolve(Flags(flags)));

    [Fact]
    public void AfterKillingTonyTheOurFatherAlsoNeedsTheConfession()
    {
        var items = Flags("faith_ring", "cross");
        string[] gates = { "rose_wait", "church_before_office" };
        Assert.True(Endings.CanSpareOldMan(Flags(gates), items));
        Assert.False(Endings.CanSpareOldMan(Flags([.. gates, "killed_tony"]), items));
        Assert.True(Endings.CanSpareOldMan(Flags([.. gates, "killed_tony", "confessed_tony"]), items));
        // the confession doesn't replace the other gates
        Assert.False(Endings.CanSpareOldMan(Flags("church_before_office", "killed_tony", "confessed_tony"), items));
        Assert.False(Endings.CanSpareOldMan(Flags([.. gates, "killed_tony", "confessed_tony"]), Flags("faith_ring")));
    }

    [Fact]
    public void OnlyALiveTonyWantsRevenge()
    {
        Assert.False(Endings.TonyWantsRevenge(Flags()));
        Assert.True(Endings.TonyWantsRevenge(Flags("shot_bartender")));
        Assert.False(Endings.TonyWantsRevenge(Flags("shot_bartender", "killed_tony")));
        Assert.False(Endings.TonyWantsRevenge(Flags("warned_tony")));
    }

    [Theory]
    [InlineData(13, "warned_tony", "alarm_ran")]
    [InlineData(14, "warned_tony", "alarm_stayed")]
    // the bell stops the night at the kitchen door: nothing Micah could have set before it changes that
    [InlineData(13, "warned_tony", "alarm_ran", Abbess, Drugs, "church_act3_return", "rose_wait")]
    [InlineData(14, "warned_tony", "alarm_stayed", Abbess, Drugs, "eleanor_convinced")]
    // a warning shot with the alarm found in time changes no outcome
    [InlineData(1, "warned_tony", "spared_oldman")]
    [InlineData(5, "warned_tony", "shot_oldman")]
    [InlineData(8, "warned_tony", Abbess, Drugs, "spared_oldman", "eleanor_struck", "eleanor_burned")]
    public void TheAlarmDecidesBeforeEverythingElse(int ending, params string[] flags) =>
        Assert.Equal(ending, Endings.Resolve(Flags(flags)));

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
    public void CalebGetsEleanorOutAfterAnEarlyGiveUpOrTheAlarmWhenSheHeldOut()
    {
        Assert.True(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "gave_up_steps")));
        Assert.True(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "walked_away")));
        Assert.Equal(1, Endings.Resolve(Flags(Abbess, Drugs, "walked_away")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Abbess, "gave_up_steps")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Drugs, "walked_away")));
        // the Our Father, with Eleanor back in bed in her coda, is ending 1 without the escape
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "spared_oldman")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "surrendered_tony", "killed_tony")));
        // the alarm: Micah ran (13) or was shot in the kitchen (14), and Eleanor is still in the house for Caleb
        Assert.True(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "warned_tony", "alarm_ran")));
        Assert.True(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "warned_tony", "alarm_stayed")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Abbess, "warned_tony", "alarm_ran")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Drugs, "warned_tony", "alarm_stayed")));
        Assert.False(Endings.EleanorEscapesWithCaleb(Flags(Abbess, Drugs, "mansion_exploded")));
    }

    [Fact]
    public void FreeEleanorWearsWhiteOnlyIfSheHeldOut()
    {
        Assert.Equal("eleanor_white", Endings.EleanorFreeOutfit(Flags(Abbess, Drugs)));
        Assert.Equal("eleanor_suit", Endings.EleanorFreeOutfit(Flags(Abbess, "eleanor_convinced")));
        Assert.Equal("eleanor_suit", Endings.EleanorFreeOutfit(Flags(Drugs)));
        Assert.Equal("eleanor_suit", Endings.EleanorFreeOutfit(Flags()));
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
