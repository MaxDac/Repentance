using Xunit;

namespace Repentance.Tests;

public class SaveDataTests
{
    private static SaveData Sample() => new()
    {
        SavedAtUtc = new DateTime(2026, 10, 10, 9, 30, 0, DateTimeKind.Utc),
        Room = "lobby",
        RoomTitle = "Aurelian Hotel",
        X = 212.5f,
        Y = 188f,
        Facing = 3,
        StoryAct = 2,
        Flags = new() { "seen_lobby", "teddy_gone" },
        Inventory = new() { "photo", "dollar" },
        Ink = "{\"flows\":{}}",
        PlaytimeSeconds = 321.5,
    };

    [Fact]
    public void RoundTripPreservesEverything()
    {
        var back = SaveSerializer.TryDeserialize(SaveSerializer.Serialize(Sample()));

        Assert.NotNull(back);
        var s = Sample();
        Assert.Equal(s.Version, back!.Version);
        Assert.Equal(s.SavedAtUtc, back.SavedAtUtc);
        Assert.Equal(s.Room, back.Room);
        Assert.Equal(s.RoomTitle, back.RoomTitle);
        Assert.Equal(s.X, back.X);
        Assert.Equal(s.Y, back.Y);
        Assert.Equal(s.Facing, back.Facing);
        Assert.Equal(s.StoryAct, back.StoryAct);
        Assert.Equal(s.Flags, back.Flags);
        Assert.Equal(s.Inventory, back.Inventory);
        Assert.Equal(s.Ink, back.Ink);
        Assert.Equal(s.PlaytimeSeconds, back.PlaytimeSeconds);
    }

    [Fact]
    public void RecoveredRingAndAcceptedCrossPreserveOriginalChoice()
    {
        var data = Sample();
        data.Flags.AddRange(new[] { "ring_left_act2", "took_faith_ring", "cross_refused", "took_cross", "church_act3_return", "act2_office_done" });
        data.Inventory.AddRange(new[] { "faith_ring", "cross" });
        var back = SaveSerializer.TryDeserialize(SaveSerializer.Serialize(data));
        Assert.NotNull(back);
        Assert.Equal(data.Flags, back.Flags);
        Assert.Equal(data.Inventory, back.Inventory);
        Assert.Contains("ring_left_act2", back.Flags);
        Assert.DoesNotContain("ring_taken_act2", back.Flags);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("not json")]
    [InlineData("{\"Version\":1,")]
    [InlineData("[1,2,3]")]
    public void CorruptInputReturnsNull(string? json) => Assert.Null(SaveSerializer.TryDeserialize(json));

    [Fact]
    public void OtherVersionIsRejected()
    {
        var data = Sample();
        data.Version = SaveData.CurrentVersion + 1;
        Assert.Null(SaveSerializer.TryDeserialize(SaveSerializer.Serialize(data)));
    }

    [Fact]
    public void MissingRoomIsRejected() =>
        Assert.Null(SaveSerializer.TryDeserialize($"{{\"Version\":{SaveData.CurrentVersion}}}"));

    [Fact]
    public void NullCollectionsDefaultToEmpty()
    {
        var back = SaveSerializer.TryDeserialize(
            $"{{\"Version\":{SaveData.CurrentVersion},\"Room\":\"office\",\"Flags\":null,\"Inventory\":null,\"Ink\":null}}");

        Assert.NotNull(back);
        Assert.Empty(back!.Flags);
        Assert.Empty(back.Inventory);
        Assert.Equal("", back.Ink);
        Assert.Equal(1, back.StoryAct);
    }
}
