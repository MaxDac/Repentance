using Repentance;
using Xunit;

namespace Repentance.Tests;

public class AudioFallbackTests
{
    [Theory]
    [InlineData("WASAPI")]
    [InlineData("PulseAudio")]
    public void RealDriverIsNeverAFallback(string driver) =>
        Assert.False(AudioFallback.IsUnintended(driver, ["--path", "."]));

    [Fact]
    public void DummyWithoutAskingIsAFallback() =>
        Assert.True(AudioFallback.IsUnintended("Dummy", ["--path", "."]));

    [Theory]
    [InlineData("--audio-driver", "Dummy")]
    [InlineData("--audio-driver", "dummy")]
    [InlineData("--audio-driver=Dummy", "--path")]
    [InlineData("--headless", "--path")]
    public void RequestedDummyIsNotAFallback(string a, string b) =>
        Assert.False(AudioFallback.IsUnintended("Dummy", ["--path", ".", a, b]));

    [Fact]
    public void UserArgsAfterTheSeparatorDontCount() =>
        Assert.True(AudioFallback.IsUnintended("Dummy", ["--path", ".", "--", "--headless"]));
}
