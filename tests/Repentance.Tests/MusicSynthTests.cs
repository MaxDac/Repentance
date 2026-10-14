using Repentance;
using Xunit;

namespace Repentance.Tests;

public class MusicSynthTests
{
    private static readonly Lazy<float[]> Club = new(() => MusicSynth.Render(Track.ClubStrings));

    [Fact]
    public void ClubStringsLoopsWithoutASeam()
    {
        var s = Club.Value;
        int frames = MusicSynth.LoopSamples(Track.ClubStrings);
        Assert.Equal(frames * 2, s.Length);
        Assert.InRange(frames / (double)MusicSynth.SampleRate, 45, 90);
        for (int c = 0; c < 2; c++)
        {
            double typical = 0;
            for (int i = 2 + c; i < s.Length; i += 2) typical += Math.Abs(s[i] - s[i - 2]);
            typical /= frames - 1;
            Assert.True(Math.Abs(s[c] - s[s.Length - 2 + c]) < typical, $"channel {c}: the wrap-around is no bigger than a normal sample step");
        }
    }

    [Fact]
    public void ClubStringsIsAudibleAndNeverClips()
    {
        var s = Club.Value;
        Assert.All(s, v => Assert.True(float.IsFinite(v) && Math.Abs(v) <= 0.9001f));
        Assert.True(s.Max(Math.Abs) > 0.85f, "normalized");
        // never a dead stop: the bass is always sounding somewhere in the hall
        int window = MusicSynth.SampleRate;
        for (int start = 0; start + window <= s.Length / 2; start += window)
        {
            double e = 0;
            for (int i = start; i < start + window; i++) e += s[2 * i] * s[2 * i];
            Assert.True(Math.Sqrt(e / window) > 0.01, $"second {start / window} is not silent");
        }
    }

    [Fact]
    public void RendersAreReproducible() =>
        Assert.Equal(Club.Value, MusicSynth.Render(Track.ClubStrings));

    [Fact]
    public void ClubStringsClimbsFromTheBassToTheViolinsAndSinksBack()
    {
        var score = MusicSynth.Score(Track.ClubStrings);
        double Enters(StringInstrument i) => score.Where(n => n.Instrument == i).Min(n => n.Beat);
        double Leaves(StringInstrument i) => score.Where(n => n.Instrument == i).Max(n => n.Beat + n.Beats);
        Assert.Equal(0, Enters(StringInstrument.DoubleBass));
        Assert.True(Enters(StringInstrument.Cello) < Enters(StringInstrument.Viola));
        Assert.True(Enters(StringInstrument.Viola) < Enters(StringInstrument.Violin));
        Assert.True(Leaves(StringInstrument.Violin) < Leaves(StringInstrument.Viola));
        Assert.True(Leaves(StringInstrument.Viola) < Leaves(StringInstrument.Cello));
        Assert.True(Leaves(StringInstrument.Cello) < Leaves(StringInstrument.DoubleBass));
        Assert.Equal(MusicSynth.LengthBeats(Track.ClubStrings), Leaves(StringInstrument.DoubleBass));
        // the violins are the strident ones, and they are the highest notes in the piece
        Assert.All(score.Where(n => n.Strident), n => Assert.Equal(StringInstrument.Violin, n.Instrument));
        Assert.Equal(StringInstrument.Violin, score.MaxBy(n => n.Midi).Instrument);
        // every part fills the whole loop: the sections line up bar for bar
        foreach (var voice in score.GroupBy(n => n.Voice))
            Assert.All(voice.Zip(voice.Skip(1)), p => Assert.True(p.Second.Beat >= p.First.Beat + p.First.Beats - 1e-9));
    }

    [Fact]
    public void ClubStringsIsABoleroOverOneOstinato()
    {
        var score = MusicSynth.Score(Track.ClubStrings);
        Assert.InRange(MusicSynth.LoopSamples(Track.ClubStrings) / (double)MusicSynth.SampleRate, 55, 65);
        // nothing plucked or clipped short: every note is a bowed stroke of at least a beat
        Assert.All(score, n => Assert.True(n.Beats >= 1, $"{n}"));
        // the bass bows the same four bars all the way round
        var bass = score.Where(n => n.Instrument == StringInstrument.DoubleBass).ToList();
        var cycle = bass.Where(n => n.Beat < 12).ToList();
        Assert.All(bass, n => Assert.Contains(cycle, c => c.Midi == n.Midi && Math.Abs(c.Beat - n.Beat % 12) < 1e-9));
        // the cello plays one theme over and over: every repetition is note for note the first
        var cello = score.Where(n => n.Voice == 1).ToList();
        var theme = cello.Where(n => n.Beat < 24).Select(n => (n.Beat - 12, n.Beats, n.Midi)).ToList();
        for (double start = 24; start < 60; start += 12)
            Assert.Equal(theme, cello.Where(n => n.Beat >= start && n.Beat < start + 12).Select(n => (n.Beat - start, n.Beats, n.Midi)));
    }

    [Fact]
    public void EveryNoteIsInItsInstrumentsRange()
    {
        var lowest = new Dictionary<StringInstrument, int>
        {
            [StringInstrument.DoubleBass] = MusicSynth.Midi("E1"), [StringInstrument.Cello] = MusicSynth.Midi("C2"),
            [StringInstrument.Viola] = MusicSynth.Midi("C3"), [StringInstrument.Violin] = MusicSynth.Midi("G3"),
        };
        Assert.All(MusicSynth.Score(Track.ClubStrings), n => Assert.True(n.Midi >= lowest[n.Instrument], $"{n}"));
    }

    [Theory]
    [InlineData("C4", 60)]
    [InlineData("A4", 69)]
    [InlineData("C#3", 49)]
    [InlineData("Bb1", 34)]
    [InlineData("Ab1", 32)]
    [InlineData("E1", 28)]
    public void NoteNames(string name, int midi) => Assert.Equal(midi, MusicSynth.Midi(name));
}
