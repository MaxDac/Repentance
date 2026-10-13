using Xunit;

namespace Repentance.Tests;

public class MicahKitTests
{
    [Fact]
    public void NotepadThenLighterArePinned()
    {
        Assert.Equal(new[] { Notes.ItemId, MicahKit.LighterId }, MicahKit.Pinned);
        Assert.True(MicahKit.IsPinned(MicahKit.LighterId));
        Assert.False(MicahKit.IsPinned("matchbook"));
    }

    [Fact]
    public void EveryKitItemIsCatalogued()
    {
        var ids = MicahKit.Pinned.Concat(MicahKit.ActKeep(2)).Concat(MicahKit.ActKeep(3))
            .Concat(Notes.DebugRooms.SelectMany(MicahKit.DebugItems));
        Assert.All(ids, id => Assert.Contains(id, Items.All.Keys));
    }

    [Theory]
    [InlineData(2)]
    [InlineData(3)]
    public void ActResetsLeaveTheActOneCluesBehind(int act)
    {
        foreach (var clue in new[] { "matchbook", "photo", "dollar", Notes.ItemId, MicahKit.LighterId })
            Assert.False(MicahKit.KeptInAct(act, clue));
        Assert.True(MicahKit.KeptInAct(act, "revolver"));
        Assert.True(MicahKit.KeptInAct(act, "faith_ring"));
        Assert.True(MicahKit.KeptInAct(act, "cross"));
    }

    [Fact]
    public void ActThreeKeepsOnlyTheGunAndTheCommitments()
    {
        Assert.Equal(new[] { "cross", "faith_ring", "revolver" }, MicahKit.ActKeep(3).Order());
        Assert.Contains("mirror", MicahKit.ActKeep(2));
        Assert.Empty(MicahKit.ActKeep(1));
    }

    [Theory]
    [InlineData("office", 1)]
    [InlineData("lobby", 1)]
    [InlineData("library", 2)]
    [InlineData("club_stage", 2)]
    [InlineData("mansion_cellar", 3)]
    [InlineData("attic", 0)]
    [InlineData("nowhere", 0)]
    public void DebugStartsKnowTheirAct(string room, int act) => Assert.Equal(act, MicahKit.DebugAct(room));

    [Fact]
    public void DebugStartsCarryWhatThatPointOfTheStoryNeeds()
    {
        Assert.Empty(MicahKit.DebugItems("office"));
        Assert.Empty(MicahKit.DebugFlags("office"));
        Assert.Empty(MicahKit.DebugItems("attic"));
        Assert.Equal(new[] { "dollar", "lockpick", "photo", "revolver" }, MicahKit.DebugItems("lobby").Order());
        Assert.Contains("took_revolver", MicahKit.DebugFlags("lobby"));
        Assert.Equal(new[] { "card", "lockpick", "mirror", "revolver" }, MicahKit.DebugItems("library").Order());
        Assert.Equal(new[] { "revolver" }, MicahKit.DebugItems("mansion_cellar"));
        Assert.All(Notes.DebugRooms, r => Assert.DoesNotContain("matchbook", MicahKit.DebugItems(r)));
    }

    [Fact]
    public void EveryNotepadDebugRoomBelongsToAnAct()
    {
        foreach (var room in Notes.DebugRooms)
            Assert.InRange(MicahKit.DebugAct(room), 1, 3);
    }
}
