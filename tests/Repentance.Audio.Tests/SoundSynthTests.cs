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
    public void FootstepsClickLikeLeatherHeelsThenTheSolePatsDown()
    {
        double Brightness(float[] s) =>
            Enumerable.Range(1, s.Length - 1).Sum(i => Math.Pow(s[i] - s[i - 1], 2)) / s.Sum(v => (double)v * v);
        int ms(double m) => (int)(m * SoundSynth.SampleRate / 1000);
        foreach (var step in new[] { Sound.StepWood, Sound.StepStone, Sound.StepCarpet, Sound.StepMarble })
            for (int v = 0; v < SoundSynth.StepVariants; v++)
            {
                var s = SoundSynth.Render(step, v);
                int peak = Array.IndexOf(s, s.MaxBy(Math.Abs));
                Assert.True(peak < ms(step == Sound.StepCarpet ? 8 : 4), $"{step}/{v}: the heel strikes at once (peak at {peak} samples)");
                double gapLevel = s[ms(30)..ms(40)].Max(Math.Abs), sole = s[ms(40)..ms(140)].Max(Math.Abs);
                Assert.True(sole > 0.15 && sole > gapLevel * 1.5, $"{step}/{v}: the sole lands after the heel ({sole} vs {gapLevel})");
            }
        double wood = Brightness(SoundSynth.Render(Sound.StepWood)), stone = Brightness(SoundSynth.Render(Sound.StepStone)),
            carpet = Brightness(SoundSynth.Render(Sound.StepCarpet)), marble = Brightness(SoundSynth.Render(Sound.StepMarble));
        Assert.True(stone > wood && wood > carpet * 2, $"brightness stone {stone}, wood {wood}, carpet {carpet}");
        Assert.True(stone > marble && marble > carpet, $"brightness stone {stone}, marble {marble}, carpet {carpet}");
    }

    [Fact]
    public void HeelsKnockWithoutAMetallicRing()
    {
        // a pitched ring shows as a narrow spike above the spectrum around it; a knock spreads across a wide band
        static double Peakiness(float[] s)
        {
            int n = 441;
            var mags = new List<double>();
            for (double hz = 800; hz <= 5200; hz += 10)
            {
                double re = 0, im = 0;
                for (int i = 0; i < n; i++)
                {
                    double w = 0.5 - 0.5 * Math.Cos(2 * Math.PI * i / (n - 1)), a = 2 * Math.PI * hz * i / SoundSynth.SampleRate;
                    re += s[i] * w * Math.Cos(a);
                    im -= s[i] * w * Math.Sin(a);
                }
                mags.Add(Math.Sqrt(re * re + im * im));
            }
            // 1000-5000 Hz, each against the mean of its +-200 Hz neighbourhood
            return Enumerable.Range(20, mags.Count - 40).Max(k => mags[k] / mags.Skip(k - 20).Take(41).Average());
        }
        foreach (var step in new[] { Sound.StepWood, Sound.StepStone, Sound.StepCarpet, Sound.StepMarble })
        {
            // the old sine-partial heel scored about 3.6; a noise knock about 2.2-2.4
            double p = Enumerable.Range(0, SoundSynth.StepVariants).Average(v => Peakiness(SoundSynth.Render(step, v)));
            Assert.True(p < 3.0, $"{step}: the heel rings like metal (spectral spike {p:F2} x its neighbourhood)");
        }
    }

    [Fact]
    public void MarbleHallsEchoTheStep()
    {
        static double Rms(float[] s, double from, double to) =>
            Math.Sqrt(s[(int)(from * SoundSynth.SampleRate)..(int)(to * SoundSynth.SampleRate)].Average(v => (double)v * v));
        for (int v = 0; v < SoundSynth.StepVariants; v++)
        {
            float[] marble = SoundSynth.Render(Sound.StepMarble, v), stone = SoundSynth.Render(Sound.StepStone, v);
            Assert.True(marble.Length > stone.Length, "the hall rings on after the step");
            double tail = Rms(marble, 0.2, 0.35), body = Rms(marble, 0, 0.15);
            Assert.True(tail > body * 0.04, $"marble/{v}: the reflections are audible ({tail} vs step {body})");
            Assert.True(tail < body * 0.5, $"marble/{v}: the echo stays below the step ({tail} vs step {body})");
        }
    }

    [Fact]
    public void SafeSoundsAreSofterThanASlamAndOverInTwoSeconds()
    {
        foreach (var safe in new[] { Sound.SafeOpen, Sound.SafeClose })
        {
            Assert.True(SoundSynth.BaseVolumeDb(safe) < SoundSynth.BaseVolumeDb(Sound.DoorSlam), $"{safe} is softer than a slam");
            Assert.True(SoundSynth.Render(safe).Length <= 2 * SoundSynth.SampleRate, $"{safe} is over within two seconds");
        }
        Assert.NotEqual(SoundSynth.Render(Sound.SafeOpen), SoundSynth.Render(Sound.SafeClose));
    }

    [Fact]
    public void GunshotIsLouderAndLongerThanAFootstep()
    {
        double Energy(float[] s) => s.Sum(v => (double)v * v);
        double ratio = Energy(SoundSynth.Render(Sound.Gunshot)) / Energy(SoundSynth.Render(Sound.StepWood));
        Assert.True(ratio > 4, $"energy ratio {ratio}");
        Assert.True(SoundSynth.BaseVolumeDb(Sound.Gunshot) > SoundSynth.BaseVolumeDb(Sound.StepStone));
    }

    private static double Rms(float[] s, double from, double to) =>
        Math.Sqrt(s[(int)(from * SoundSynth.SampleRate)..(int)(to * SoundSynth.SampleRate)].Average(v => (double)v * v));

    private static double Brightness(float[] s, double from, double to)
    {
        var part = s[(int)(from * SoundSynth.SampleRate)..(int)(to * SoundSynth.SampleRate)];
        return Enumerable.Range(1, part.Length - 1).Sum(i => Math.Pow(part[i] - part[i - 1], 2)) / part.Sum(v => (double)v * v);
    }

    [Fact]
    public void GunshotHitsAtOnceThenTheRoomRingsAway()
    {
        var shot = SoundSynth.Render(Sound.Gunshot);
        int peak = Array.IndexOf(shot, shot.MaxBy(Math.Abs));
        Assert.True(peak < SoundSynth.SampleRate / 50, $"the blast comes at once, after the hammer (peak at {peak} samples)");
        double blast = Rms(shot, 0, 0.03), room = Rms(shot, 0.15, 0.4);
        Assert.True(room > blast * 0.01, $"the room answers ({room} vs blast {blast})");
        Assert.True(room < blast * 0.2, $"the room stays well below the blast ({room} vs blast {blast})");
        // a diffuse tail only fades: no late burst like a discrete echo
        for (double t = 0.05; t < 0.8; t += 0.05)
            Assert.True(Rms(shot, t, t + 0.05) <= Rms(shot, t - 0.05, t) * 1.1, $"the tail swells again at {t:F2} s");
    }

    [Fact]
    public void ThunderCracksBrightThenRollsLow()
    {
        var thunder = SoundSynth.Render(Sound.Thunder);
        double crack = Brightness(thunder, 0, 0.3), rumble = Brightness(thunder, 1.5, 3);
        Assert.True(crack > rumble * 3, $"the near channel cracks brighter than the far rumble ({crack} vs {rumble})");
        Assert.True(Rms(thunder, 0, 0.4) > Rms(thunder, 1, 3), "the crack is the loudest part");
        // the channel's stretches at one distance arrive together and swell into rolls
        int rolls = 0;
        for (double t = 0.8; t < 3; t += 0.2)
            if (Rms(thunder, t, t + 0.2) > Rms(thunder, t - 0.2, t) * 1.15) rolls++;
        Assert.True(rolls >= 1, "the rumble rolls instead of fading evenly");
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
        Assert.Equal(Sound.StepMarble, SoundSynth.StepFor(FloorSurface.Marble));
        Assert.Equal(Sound.StepWood, SoundSynth.StepFor(FloorSurface.Wood));
    }
}
