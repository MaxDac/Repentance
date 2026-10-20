using Repentance;
using Xunit;

namespace Repentance.Tests;

public class SoundSynthTests
{
    public static IEnumerable<object[]> AllSounds => Enum.GetValues<Sound>().Select(s => new object[] { s });

    [Theory]
    [MemberData(nameof(AllSounds))]
    public void EverySoundIsAudibleAndNeverClips(Sound sound)
    {
        var samples = SoundSynth.Render(sound);
        Assert.InRange(samples.Length, SoundSynth.SampleRate / 20, SoundSynth.SampleRate * 5);
        Assert.All(samples, v => Assert.True(float.IsFinite(v) && Math.Abs(v) <= 0.9001f));
        Assert.True(samples.Max(Math.Abs) > 0.85f, $"{sound} is normalized");
        // a one-shot dies away instead of stopping on a click
        if (sound != Sound.Rain) Assert.True(Math.Abs(samples[^1]) < 0.05f, $"{sound} ends quietly");
    }

    [Fact]
    public void RendersAreReproducibleAndStepsVary()
    {
        Assert.Equal(SoundSynth.Render(Sound.Gunshot), SoundSynth.Render(Sound.Gunshot));
        Assert.NotEqual(SoundSynth.Render(Sound.StepWood, 0), SoundSynth.Render(Sound.StepWood, 1));
    }

    [Fact]
    public void RainLoopsWithoutASeam()
    {
        var rain = SoundSynth.Render(Sound.Rain);
        Assert.Equal((int)(SoundSynth.RainLoopSeconds * SoundSynth.SampleRate), rain.Length);
        double typicalStep = Enumerable.Range(1, rain.Length - 1).Average(i => Math.Abs(rain[i] - rain[i - 1]));
        Assert.True(Math.Abs(rain[0] - rain[^1]) < typicalStep * 6, "the wrap-around is no bigger than a normal sample step");
    }

    [Fact]
    public void RoomDoorsAreQuieterThanASlamAndOverInASecond()
    {
        foreach (var door in new[] { Sound.DoorOpen, Sound.DoorClose })
        {
            Assert.True(SoundSynth.BaseVolumeDb(door) < SoundSynth.BaseVolumeDb(Sound.DoorSlam), $"{door} is softer than a slam");
            Assert.True(SoundSynth.Render(door).Length <= SoundSynth.SampleRate, $"{door} is over within a second");
        }
        Assert.DoesNotContain(SoundSynth.CuesFor("*A car door slams.*"), c => c.Sound is Sound.DoorOpen or Sound.DoorClose);
    }

    [Fact]
    public void GunshotIsLouderAndLongerThanAFootstep()
    {
        double Energy(float[] s) => s.Sum(v => (double)v * v);
        double ratio = Energy(SoundSynth.Render(Sound.Gunshot)) / Energy(SoundSynth.Render(Sound.StepWood));
        Assert.True(ratio > 4, $"energy ratio {ratio}");
        Assert.True(SoundSynth.BaseVolumeDb(Sound.Gunshot) > SoundSynth.BaseVolumeDb(Sound.StepStone));
    }

    [Theory]
    [InlineData("*BANG*", Sound.Gunshot)]
    [InlineData("*CLANG*", Sound.Clang)]
    [InlineData("*CRASH*", Sound.Crash)]
    [InlineData("*THUNK*", Sound.Thunk)]
    [InlineData("*CRACK*", Sound.Crack)]
    [InlineData("*rustle*", Sound.Rustle)]
    [InlineData("*click*", Sound.Click)]
    [InlineData("*scrape*", Sound.Scrape)]
    [InlineData("*SCRAAAPE*", Sound.Scrape)]
    [InlineData("*FWOOOSH*", Sound.Whoosh)]
    [InlineData("*Whoosh*", Sound.Whoosh)]
    [InlineData("*Ring*", Sound.Bell)]
    [InlineData("*THUNDER*", Sound.Thunder)]
    [InlineData("*A car door slams.*", Sound.DoorSlam)]
    public void SoundEffectLinesPlayTheirSound(string line, Sound expected) =>
        Assert.Equal(new[] { new SoundCue(expected, 0) }, SoundSynth.CuesFor(line));

    [Fact]
    public void SalsKnockIsTwoAPauseAndOne()
    {
        var cues = SoundSynth.CuesFor("*Knock knock*... *knock*");
        Assert.All(cues, c => Assert.Equal(Sound.Knock, c.Sound));
        var t = cues.Select(c => c.Delay).ToArray();
        Assert.Equal(3, t.Length);
        Assert.True(t[2] - t[1] > 1.5 * (t[1] - t[0]), "the third knock comes after a pause");
    }

    [Fact]
    public void MultipleAndSceneDescribingCues()
    {
        Assert.Equal(2, SoundSynth.CuesFor("*Two car doors slam in the dark.*").Count(c => c.Sound == Sound.DoorSlam));
        Assert.True(SoundSynth.CuesFor("*Footsteps on the landing, behind the other door. A man's voice. Then two.*")
            .Count(c => c.Sound == Sound.StepWood) >= 3);
    }

    [Fact]
    public void ThunderRumblesLongAfterItsCrack()
    {
        var thunder = SoundSynth.Render(Sound.Thunder);
        Assert.True(thunder.Length > SoundSynth.SampleRate * 3, "a long roll");
        double Rms(int from, int to) => Math.Sqrt(Enumerable.Range(from, to - from).Average(i => (double)thunder[i] * thunder[i]));
        int sr = SoundSynth.SampleRate;
        Assert.True(Rms(sr, sr * 2) > 0.02, "still rumbling a second in");
        Assert.True(Rms(0, sr / 2) > Rms(sr * 3, sr * 4), "dies away");
    }

    [Theory]
    [InlineData("Last time I carried it, I shot a mailbox. Bang.")]
    [InlineData("A ring. On the desk.")]
    [InlineData("*grunt*")]
    public void OrdinarySpeechIsSilent(string line) => Assert.Empty(SoundSynth.CuesFor(line));

    [Fact]
    public void VolumePercentMapsToBusGain()
    {
        Assert.Equal(0f, SoundSynth.PercentToDb(100), 3);
        Assert.Equal(-6.02f, SoundSynth.PercentToDb(50), 1);
        Assert.True(SoundSynth.PercentToDb(0) <= -60f);
        Assert.Equal(Sound.StepStone, SoundSynth.StepFor(FloorSurface.Stone));
        Assert.Equal(Sound.StepCarpet, SoundSynth.StepFor(FloorSurface.Carpet));
        Assert.Equal(Sound.StepWood, SoundSynth.StepFor(FloorSurface.Wood));
    }
}
