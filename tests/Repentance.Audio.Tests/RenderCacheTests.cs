using Repentance;
using Xunit;

namespace Repentance.Tests;

public class RenderCacheTests
{
    private static RenderCache<Track, string> Cache(int capacity = 3) => new(capacity);

    private static void Render(RenderCache<Track, string> cache, Track track)
    {
        Assert.True(cache.TryStartNext(out var next));
        Assert.Equal(track, next);
        cache.Finish(next, next.ToString());
    }

    [Fact]
    public void RequestsJumpAheadOfPrefetches()
    {
        var cache = Cache();
        cache.Prefetch(new[] {         Track.StreetTraffic, Track.LobbyPiano });
        cache.Request(Track.OfficeJazz);
        cache.Request(Track.ChurchOrgan);
        Assert.Equal(new[] { Track.ChurchOrgan, Track.OfficeJazz, Track.StreetTraffic, Track.LobbyPiano }, cache.Queue);
    }

    [Fact]
    public void RendersOneAtATimeAndNeverQueuesWhatIsKeptOrRendering()
    {
        var cache = Cache();
        cache.Request(Track.OfficeJazz);
        Assert.True(cache.TryStartNext(out var first));
        cache.Request(Track.ChurchOrgan);
        Assert.False(cache.TryStartNext(out _));
        cache.Request(Track.OfficeJazz);
        cache.Prefetch(new[] { Track.OfficeJazz });
        Assert.Equal(new[] { Track.ChurchOrgan }, cache.Queue);
        cache.Finish(first, "jazz");
        cache.Request(Track.OfficeJazz);
        Assert.Equal(new[] { Track.ChurchOrgan }, cache.Queue);
        Assert.True(cache.TryGet(Track.OfficeJazz, out var value));
        Assert.Equal("jazz", value);
    }

    [Fact]
    public void EvictsTheLeastRecentlyUsedButNeverThePinned()
    {
        var cache = Cache(2);
        cache.Request(Track.OfficeJazz);
        Render(cache, Track.OfficeJazz);
        cache.Pinned = Track.OfficeJazz;
        cache.Request(Track.ChurchOrgan);
        Render(cache, Track.ChurchOrgan);
        cache.Request(Track.LobbyPiano);
        Assert.True(cache.TryStartNext(out var piano));
        Assert.Equal(new[] { Track.ChurchOrgan }, cache.Finish(piano, "piano"));
        Assert.Equal(new[] { Track.OfficeJazz, Track.LobbyPiano }, cache.Keys.Order());
    }

    [Fact]
    public void UsingAKeptRenderSavesItFromEviction()
    {
        var cache = Cache(2);
        foreach (var track in new[] { Track.OfficeJazz, Track.ChurchOrgan })
        {
            cache.Request(track);
            Render(cache, track);
        }
        Assert.True(cache.TryGet(Track.OfficeJazz, out _));
        cache.Request(Track.LobbyPiano);
        Render(cache, Track.LobbyPiano);
        Assert.Equal(new[] { Track.OfficeJazz, Track.LobbyPiano }, cache.Keys.Order());
    }

    [Fact]
    public void PrefetchReplacesEarlierGuessesAndLeavesRoomForThePinned()
    {
        var cache = Cache(3);
        cache.Pinned = Track.OfficeJazz;
        cache.Prefetch(new[] { Track.ChurchOrgan, Track.ChurchOrgan, Track.OfficeJazz, Track.LobbyPiano, Track.ConventPiano });
        Assert.Equal(new[] { Track.ChurchOrgan, Track.LobbyPiano }, cache.Queue);
        cache.Prefetch(new[] { Track.ConventPiano });
        Assert.Equal(new[] { Track.ConventPiano }, cache.Queue);
    }

    [Fact]
    public void AFailedRenderFreesTheWorker()
    {
        var cache = Cache();
        cache.Request(Track.OfficeJazz);
        cache.Request(Track.ChurchOrgan);
        Assert.True(cache.TryStartNext(out var first));
        cache.Fail(first);
        Assert.Null(cache.Rendering);
        Assert.True(cache.TryStartNext(out var second));
        Assert.Equal(Track.OfficeJazz, second);
        cache.ClearQueue();
        Assert.Empty(cache.Queue);
    }

    [Fact]
    public void Pcm16IsLittleEndianAndClamped()
    {
        var bytes = MusicSynth.ToPcm16(new[] { 0f, 1f, -1f, 2f, -2f, 0.5f });
        var values = Enumerable.Range(0, 6).Select(i => (short)(bytes[i * 2] | bytes[i * 2 + 1] << 8)).ToArray();
        Assert.Equal(new short[] { 0, short.MaxValue, -short.MaxValue, short.MaxValue, short.MinValue, 16384 }, values);
    }
}
