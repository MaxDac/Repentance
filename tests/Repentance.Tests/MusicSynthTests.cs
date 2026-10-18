using Repentance;
using Xunit;

namespace Repentance.Tests;

public class MusicSynthTests
{
    private static readonly Dictionary<Track, Lazy<float[]>> Renders =
        Enum.GetValues<Track>().ToDictionary(t => t, t => new Lazy<float[]>(() => MusicSynth.Render(t)));

    public static TheoryData<Track> Tracks => new(Enum.GetValues<Track>());

    private static double Seconds(Track track) => MusicSynth.LoopSamples(track) / (double)MusicSynth.SampleRate;

    [Theory]
    [MemberData(nameof(Tracks))]
    public void LoopsWithoutASeam(Track track)
    {
        var s = Renders[track].Value;
        int frames = MusicSynth.LoopSamples(track);
        Assert.Equal(frames * 2, s.Length);
        Assert.InRange(Seconds(track), 55, 65);
        for (int c = 0; c < 2; c++)
        {
            var steps = new List<float>(frames);
            for (int i = 2 + c; i < s.Length; i += 2) steps.Add(Math.Abs(s[i] - s[i - 2]));
            steps.Sort();
            // a loop that opens on a note may jump at the seam as at any attack, but never further than the music does
            float ordinary = track == Track.ClubStrings ? steps.Average() : steps[(int)(steps.Count * 0.999)];
            Assert.True(Math.Abs(s[c] - s[s.Length - 2 + c]) <= ordinary, $"channel {c}: the wrap-around is no bigger than a normal sample step");
        }
    }

    [Theory]
    [MemberData(nameof(Tracks))]
    public void IsAudibleAndNeverClips(Track track)
    {
        var s = Renders[track].Value;
        Assert.All(s, v => Assert.True(float.IsFinite(v) && Math.Abs(v) <= 0.9001f));
        Assert.True(s.Max(Math.Abs) > 0.85f, "normalized");
        // never a dead stop: something always sounds, or rings on in the room
        int window = MusicSynth.SampleRate;
        for (int start = 0; start + window <= s.Length / 2; start += window)
        {
            double e = 0;
            for (int i = start; i < start + window; i++) e += s[2 * i] * s[2 * i];
            Assert.True(Math.Sqrt(e / window) > 0.005, $"second {start / window} is not silent");
        }
    }

    [Theory]
    [MemberData(nameof(Tracks))]
    public void RendersAreReproducible(Track track) =>
        Assert.Equal(Renders[track].Value, MusicSynth.Render(track));

    [Fact]
    public void ClubStringsClimbsFromTheBassToTheViolinsAndSinksBack()
    {
        var score = MusicSynth.Score(Track.ClubStrings);
        double Enters(Instrument i) => score.Where(n => n.Instrument == i).Min(n => n.Beat);
        double Leaves(Instrument i) => score.Where(n => n.Instrument == i).Max(n => n.Beat + n.Beats);
        Assert.Equal(0, Enters(Instrument.DoubleBass));
        Assert.True(Enters(Instrument.Cello) < Enters(Instrument.Viola));
        Assert.True(Enters(Instrument.Viola) < Enters(Instrument.Violin));
        Assert.True(Leaves(Instrument.Violin) < Leaves(Instrument.Viola));
        Assert.True(Leaves(Instrument.Viola) < Leaves(Instrument.Cello));
        Assert.True(Leaves(Instrument.Cello) < Leaves(Instrument.DoubleBass));
        Assert.Equal(MusicSynth.LengthBeats(Track.ClubStrings), Leaves(Instrument.DoubleBass));
        // the violins are the strident ones, and they are the highest notes in the piece
        Assert.All(score.Where(n => n.Strident), n => Assert.Equal(Instrument.Violin, n.Instrument));
        Assert.Equal(Instrument.Violin, score.MaxBy(n => n.Midi).Instrument);
        // every part fills the whole loop: the sections line up bar for bar
        foreach (var voice in score.GroupBy(n => n.Voice))
            Assert.All(voice.Zip(voice.Skip(1)), p => Assert.True(p.Second.Beat >= p.First.Beat + p.First.Beats - 1e-9));
    }

    [Fact]
    public void ClubStringsIsABoleroOverOneOstinato()
    {
        var score = MusicSynth.Score(Track.ClubStrings);
        // nothing plucked or clipped short: every note is a bowed stroke of at least a beat
        Assert.All(score, n => Assert.True(n.Beats >= 1, $"{n}"));
        // the bass bows the same four bars all the way round
        var bass = score.Where(n => n.Instrument == Instrument.DoubleBass).ToList();
        var cycle = bass.Where(n => n.Beat < 12).ToList();
        Assert.All(bass, n => Assert.Contains(cycle, c => c.Midi == n.Midi && Math.Abs(c.Beat - n.Beat % 12) < 1e-9));
        // the cello plays one theme over and over: every repetition is note for note the first
        var cello = score.Where(n => n.Voice == 1).ToList();
        var theme = cello.Where(n => n.Beat < 24).Select(n => (n.Beat - 12, n.Beats, n.Midi)).ToList();
        for (double start = 24; start < 60; start += 12)
            Assert.Equal(theme, cello.Where(n => n.Beat >= start && n.Beat < start + 12).Select(n => (n.Beat - start, n.Beats, n.Midi)));
    }

    [Fact]
    public void ChurchOrganIsTriedBeforeTheMassAndEndsInAMajorChord()
    {
        var score = MusicSynth.Score(Track.ChurchOrgan);
        Assert.Equal(64, MusicSynth.LengthBeats(Track.ChurchOrgan));
        Assert.All(score, n => Assert.Contains(n.Instrument, new[] { Instrument.OrganFlute, Instrument.OrganPlenum, Instrument.OrganPedal }));
        // first single pipes, then the first chord
        var firstChord = score.GroupBy(n => n.Beat).Where(g => g.Count() >= 3).Min(g => g.Key);
        Assert.True(score.Count(n => n.Beat < firstChord) >= 8, "the organist tries pipes one at a time first");
        // the chorale closes on D major, not minor
        var plenum = score.Where(n => n.Instrument == Instrument.OrganPlenum).ToList();
        var last = plenum.Where(n => n.Beat == plenum.Max(p => p.Beat)).Select(n => n.Midi % 12).ToHashSet();
        Assert.Equal(new HashSet<int> { 2, 6, 9 }, last);
    }

    [Fact]
    public void ConventPianoIsAPreludeInEFlat()
    {
        var score = MusicSynth.Score(Track.ConventPiano);
        Assert.All(score, n => Assert.Equal(Instrument.Piano, n.Instrument));
        Assert.Equal(66, MusicSynth.LengthBeats(Track.ConventPiano));
        int[] eFlatMajor = { 3, 5, 7, 8, 10, 0, 2 };
        Assert.All(score, n => Assert.Contains(n.Midi % 12, eFlatMajor));
        // the left hand rolls an arpeggio on every eighth, rising from the bass of each bar
        var left = score.Where(n => n.Voice == 0).ToList();
        Assert.Equal(66 * 2, left.Count);
        Assert.All(left.Where(n => n.Beat % 3 == 0), n => Assert.Equal(left.Where(m => Math.Floor(m.Beat / 3) == n.Beat / 3).Min(m => m.Midi), n.Midi));
        // the loop opens on the tonic and the melody leads back into it from the leading tone
        Assert.Equal(MusicSynth.Midi("Eb2"), left[0].Midi);
        Assert.Equal(MusicSynth.Midi("D5"), score.Where(n => n.Voice == 1).MaxBy(n => n.Beat).Midi);
    }

    [Fact]
    public void OfficeJazzIsASlowSadBallad()
    {
        var score = MusicSynth.Score(Track.OfficeJazz);
        Assert.Equal(64, MusicSynth.LengthBeats(Track.OfficeJazz));
        // adagio: slow, but not a lento crawl
        Assert.InRange(60 / MusicSynth.SecondsPerBeat(Track.OfficeJazz), 60, 72);
        var trumpet = score.Where(n => n.Instrument == Instrument.Trumpet).ToList();
        // swung eighths: an offbeat always falls two thirds of the way through the beat, never half way
        Assert.DoesNotContain(trumpet, n => Math.Abs(n.Beat % 1 - 0.5) < 1e-6);
        Assert.Contains(trumpet, n => Math.Abs(n.Beat % 1 - 2.0 / 3) < 1e-6);
        // low key: the muted trumpet stays in its soft middle register, never reaching for the top
        Assert.All(trumpet, n => Assert.True(n.Midi <= MusicSynth.Midi("D5"), $"{n}"));
        // AABA: the three A sections open with the same three bars
        IEnumerable<(double, int)> Bars(double from) =>
            trumpet.Where(n => n.Beat >= from - 1e-6 && n.Beat < from + 12 - 1e-6).Select(n => (Math.Round(n.Beat - from, 6), n.Midi));
        Assert.Equal(Bars(0), Bars(16));
        Assert.Equal(Bars(0), Bars(48));
        Assert.NotEqual(Bars(0), Bars(32));
        // D minor: the bass opens on D under a chord with F, not F#, and the tune leads home from the leading tone
        var bass = score.Where(n => n.Instrument == Instrument.UprightBass).ToList();
        Assert.Equal(MusicSynth.Midi("D2"), bass[0].Midi);
        var opening = score.Where(n => n.Instrument == Instrument.Piano && n.Beat < 1).Select(n => n.Midi % 12).ToHashSet();
        Assert.Contains(5, opening);
        Assert.DoesNotContain(6, opening);
        Assert.Equal(MusicSynth.Midi("C#4"), trumpet.MaxBy(n => n.Beat).Midi);
        // a slow two-feel: the bass plucks only on the half notes
        Assert.All(bass, n => Assert.True(n.Beats >= 2 && n.Beat % 2 == 0, $"{n}"));
        // the band: muted trumpet, piano and plucked bass, no drums
        Assert.Equal(
            new[] { Instrument.Trumpet, Instrument.Piano, Instrument.UprightBass }.ToHashSet(),
            score.Select(n => n.Instrument).ToHashSet());
    }

    [Fact]
    public void StreetTrafficIsTrafficNotMusic()
    {
        var score = MusicSynth.Score(Track.StreetTraffic);
        Assert.Equal(60, MusicSynth.LengthBeats(Track.StreetTraffic));
        Assert.Equal(1, MusicSynth.SecondsPerBeat(Track.StreetTraffic));
        var traffic = new[] { Instrument.CityHum, Instrument.Motorcar, Instrument.Streetcar, Instrument.Horn }.ToHashSet();
        Assert.Equal(traffic, score.Select(n => n.Instrument).ToHashSet());
        // the city roars under everything, all the way round the loop
        var hum = Assert.Single(score, n => n.Instrument == Instrument.CityHum);
        Assert.Equal((0.0, 60.0), (hum.Beat, hum.Beats));
        // cars go by both ways, some of them close, and one crosses the seam so the loop has no quiet start
        var cars = score.Where(n => n.Instrument == Instrument.Motorcar).ToList();
        Assert.True(cars.Count >= 8, $"{cars.Count} cars");
        Assert.Equal(2, cars.Select(n => n.Voice).Distinct().Count());
        Assert.Contains(cars, n => n.Strident);
        Assert.Contains(cars, n => n.Beat + n.Beats > 60);
        Assert.Single(score, n => n.Instrument == Instrument.Streetcar);
        // a klaxon and a bulb horn, now and then, never a tune
        var horns = score.Where(n => n.Instrument == Instrument.Horn).ToList();
        Assert.Contains(horns, n => n.Strident);
        Assert.Contains(horns, n => !n.Strident);
        Assert.True(horns.Count <= 4);
    }

    [Theory]
    [MemberData(nameof(Tracks))]
    public void EveryNoteIsInItsInstrumentsRange(Track track)
    {
        var range = new Dictionary<Instrument, (string Low, string High)>
        {
            [Instrument.DoubleBass] = ("E1", "G4"), [Instrument.Cello] = ("C2", "A5"), [Instrument.Viola] = ("C3", "E6"),
            [Instrument.Violin] = ("G3", "E7"), [Instrument.OrganFlute] = ("C2", "C7"), [Instrument.OrganPlenum] = ("C2", "C7"),
            [Instrument.OrganPedal] = ("C1", "G3"), [Instrument.Piano] = ("A0", "C8"), [Instrument.Trumpet] = ("F#3", "D6"),
            [Instrument.UprightBass] = ("E1", "G4"), [Instrument.Drums] = ("C2", "B3"),
            [Instrument.CityHum] = ("C1", "C3"), [Instrument.Motorcar] = ("C1", "C3"), [Instrument.Streetcar] = ("C2", "C5"),
            [Instrument.Horn] = ("C3", "C6"),
        };
        Assert.All(MusicSynth.Score(track), n =>
            Assert.InRange(n.Midi, MusicSynth.Midi(range[n.Instrument].Low), MusicSynth.Midi(range[n.Instrument].High)));
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