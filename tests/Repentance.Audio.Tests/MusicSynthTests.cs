using Repentance;
using Xunit;

namespace Repentance.Tests;

public class MusicSynthTests
{
    private static readonly string ProjectFolder = FindProjectFolder();

    static MusicSynthTests() => Recordings.Use(path =>
    {
        var file = Folder(path);
        return File.Exists(file) ? File.ReadAllBytes(file) : null;
    });

    private static string Folder(string projectPath) =>
        Path.Combine(ProjectFolder, projectPath.Replace('/', Path.DirectorySeparatorChar));

    private static string FindProjectFolder()
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "project.godot")))
                return dir.FullName;
        throw new InvalidOperationException("project.godot not found above the test binaries");
    }
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
        // Rose's street is silent between its cars on purpose
        if (track == Track.RoseStreet) return;
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
        // background music: no accents, and even the violins' climax, the highest notes in the piece, stays low
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.Equal(Instrument.Violin, score.MaxBy(n => n.Midi).Instrument);
        Assert.All(score, n => Assert.True(n.Midi <= MusicSynth.Midi("C5"), $"{n}"));
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
        // background music: a pipe sounds on every beat, and none of them is shrill
        for (int beat = 0; beat < 64; beat++)
            Assert.Contains(score, n => n.Beat <= beat && beat < n.Beat + n.Beats);
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.All(score, n => Assert.True(n.Midi <= MusicSynth.Midi("D5"), $"{n}"));
        // the chorale closes on D major, not minor
        var plenum = score.Where(n => n.Instrument == Instrument.OrganPlenum).ToList();
        var last = plenum.Where(n => n.Beat == plenum.Max(p => p.Beat)).Select(n => n.Midi % 12).ToHashSet();
        Assert.Equal(new HashSet<int> { 2, 6, 9 }, last);
    }

    [Fact]
    public void ConventPianoIsAPreludeInEFlat()
    {
        var score = MusicSynth.Score(Track.ConventPiano);
        Assert.All(score, n => Assert.Equal(Instrument.RecordedPiano, n.Instrument));
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
    public void OfficeJazzIsAVerySlowSoftBlues()
    {
        var score = MusicSynth.Score(Track.OfficeJazz);
        // one twelve-bar chorus, very slow: rain on the window, a drink in the hand
        Assert.Equal(48, MusicSynth.LengthBeats(Track.OfficeJazz), 6);
        Assert.InRange(60 / MusicSynth.SecondsPerBeat(Track.OfficeJazz), 44, 52);
        // the band: recorded piano, real alto sax and real plucked bass, no drums
        Assert.Equal(
            new[] { Instrument.RecordedPiano, Instrument.RecordedSax, Instrument.RecordedBass }.ToHashSet(),
            score.Select(n => n.Instrument).ToHashSet());
        // background, not a performance: no accents, and the sax stays low and soft, never reaching for the top
        Assert.DoesNotContain(score, n => n.Strident);
        var sax = score.Where(n => n.Instrument == Instrument.RecordedSax).ToList();
        Assert.All(sax, n => Assert.True(n.Midi <= MusicSynth.Midi("D5"), $"{n}"));
        // strokes, not a solo: the sax plays less than half the time
        Assert.True(sax.Sum(n => n.Beats) < 24, $"the sax holds {sax.Sum(n => n.Beats)} of 48 beats");
        // D minor: the bass opens on D under a chord with F, not F#, and the sax leads home from the leading tone
        var bass = score.Where(n => n.Instrument == Instrument.RecordedBass).ToList();
        Assert.Equal(MusicSynth.Midi("D2"), bass[0].Midi);
        var opening = score.Where(n => n.Instrument == Instrument.RecordedPiano && n.Beat < 4).Select(n => n.Midi % 12).ToHashSet();
        Assert.Contains(5, opening);
        Assert.DoesNotContain(6, opening);
        Assert.Equal(MusicSynth.Midi("C#4"), sax.MaxBy(n => n.Beat)!.Midi);
        // a slow two-feel: the bass plucks only on the half notes
        Assert.All(bass, n => Assert.True(n.Beats >= 2 && n.Beat % 2 == 0, $"{n}"));
    }
    [Fact]
    public void BlueLanternIsAHotBandRehearsing()
    {
        var score = MusicSynth.Score(Track.BlueLanternJazz);
        const int together = 36 * 4; // two choruses and four bars of the third, before it falls apart
        Assert.Equal(192, MusicSynth.LengthBeats(Track.BlueLanternJazz));
        // a fast Chicago two-beat
        Assert.True(60 / MusicSynth.SecondsPerBeat(Track.BlueLanternJazz) >= 160);
        Assert.Equal(
            new[] { Instrument.Cornet, Instrument.Clarinet, Instrument.Trombone, Instrument.Banjo, Instrument.Tuba,
                    Instrument.RecordedPiano, Instrument.Drums }.ToHashSet(),
            score.Select(n => n.Instrument).ToHashSet());
        List<ScoreNote> Of(Instrument i, double from, double to) =>
            score.Where(n => n.Instrument == i && n.Beat >= from - 1e-6 && n.Beat < to - 1e-6).ToList();
        // while the band plays: the tuba only on one and three, the banjo on every beat but the stop-time breaks
        Assert.All(Of(Instrument.Tuba, 0, together), n => Assert.True(n.Beat % 2 == 0, $"{n}"));
        var banjoBeats = Of(Instrument.Banjo, 0, together).Select(n => n.Beat).ToHashSet();
        Assert.True(banjoBeats.Count >= together - 8, "the banjo chunks four to the bar");
        Assert.All(banjoBeats, b => Assert.Equal(0, b % 1));
        // the cornet takes its break over the stop-time hits in the second chorus
        Assert.DoesNotContain(Of(Instrument.Banjo, 89, 96).Concat(Of(Instrument.Tuba, 89, 96)), n => n.Beat % 4 != 0);
        Assert.True(Of(Instrument.Cornet, 88, 96).Count >= 8);
        // then it falls apart on a trombone clam, and the rehearsal is just noodling: no rhythm section
        Assert.Contains(score, n => n.Instrument == Instrument.Trombone && n.Beat == together);
        Assert.DoesNotContain(score, n => n.Beat > together + 4 && n.Instrument == Instrument.Drums && n.Midi != MusicSynth.Midi("C#2"));
        Assert.True(Of(Instrument.Banjo, together + 4, 184).Count < 8, "the banjo only checks a string or two");
        // background, not a performance: no accents, and something sounds on every beat, the clarinet noodling low
        // through the rehearsal
        Assert.DoesNotContain(score, n => n.Strident);
        for (int beat = 0; beat < 192; beat++)
            Assert.True(score.Any(n => n.Beat <= beat + 1e-6 && n.Beat + n.Beats > beat + 1e-6), $"silent beat {beat}");
        Assert.True(Of(Instrument.Clarinet, together, 184).Max(n => n.Midi) <= MusicSynth.Midi("Bb4"));
        // and the drummer counts it back in with his sticks, into the top of the loop
        var sticks = score.Where(n => n.Midi == MusicSynth.Midi("C#2")).Select(n => n.Beat).ToList();
        Assert.Equal(new double[] { 184, 186, 188, 189, 190, 191 }, sticks);
    }

    [Fact]
    public void BlueLanternAlleyIsTheSameRehearsalFurtherAway()
    {
        Assert.True(MusicSynth.SharesScore(Track.BlueLanternJazz, Track.BlueLanternAlley));
        Assert.False(MusicSynth.SharesScore(Track.BlueLanternJazz, Track.OfficeJazz));
        Assert.Equal(MusicSynth.LoopSamples(Track.BlueLanternJazz), MusicSynth.LoopSamples(Track.BlueLanternAlley));
        Assert.True(MusicSynth.BaseVolumeDb(Track.BlueLanternAlley) < MusicSynth.BaseVolumeDb(Track.BlueLanternJazz));
        // through a door and down a passage the highs go first, and the stereo picture shrinks
        static double Bright(float[] s)
        {
            double edge = 0, all = 0;
            for (int i = 2; i < s.Length; i += 2)
            {
                double d = s[i] - s[i - 2];
                edge += d * d;
                all += s[i] * s[i];
            }
            return edge / all;
        }
        static double Width(float[] s)
        {
            double side = 0, mid = 0;
            for (int i = 0; i < s.Length; i += 2)
            {
                side += Math.Pow(s[i] - s[i + 1], 2);
                mid += Math.Pow(s[i] + s[i + 1], 2);
            }
            return side / mid;
        }
        var room = Renders[Track.BlueLanternJazz].Value;
        var alley = Renders[Track.BlueLanternAlley].Value;
        Assert.True(Bright(alley) < Bright(room) * 2 / 3, $"alley {Bright(alley)} vs room {Bright(room)}");
        Assert.True(Width(alley) < Width(room), $"alley {Width(alley)} vs room {Width(room)}");
    }

    [Fact]
    public void StreetTrafficIsTrafficNotMusic()
    {
        var score = MusicSynth.Score(Track.StreetTraffic);
        Assert.Equal(60, MusicSynth.LengthBeats(Track.StreetTraffic));
        Assert.Equal(1, MusicSynth.SecondsPerBeat(Track.StreetTraffic));
        var traffic = new[] { Instrument.CityHum, Instrument.Motorcar, Instrument.Streetcar, Instrument.Horn }.ToHashSet();
        Assert.Equal(traffic, score.Select(n => n.Instrument).ToHashSet());
        // background, like the music: no accents, so no car passes close and no klaxon blares
        Assert.DoesNotContain(score, n => n.Strident);
        // the city roars under everything, all the way round the loop
        var hum = Assert.Single(score, n => n.Instrument == Instrument.CityHum);
        Assert.Equal((0.0, 60.0), (hum.Beat, hum.Beats));
        // cars go by both ways, and one crosses the seam so the loop has no quiet start
        var cars = score.Where(n => n.Instrument == Instrument.Motorcar).ToList();
        Assert.True(cars.Count >= 8, $"{cars.Count} cars");
        Assert.Equal(2, cars.Select(n => n.Voice).Distinct().Count());
        Assert.Contains(cars, n => n.Beat + n.Beats > 60);
        Assert.Single(score, n => n.Instrument == Instrument.Streetcar);
        // a bulb horn now and then, never a tune
        var horns = score.Where(n => n.Instrument == Instrument.Horn).ToList();
        Assert.InRange(horns.Count, 1, 3);
    }

    [Fact]
    public void LobbyPianoIsASoftLoungeBallad()
    {
        var score = MusicSynth.Score(Track.LobbyPiano);
        Assert.All(score, n => Assert.Equal(Instrument.RecordedPiano, n.Instrument));
        Assert.Equal(64, MusicSynth.LengthBeats(Track.LobbyPiano), 6);
        Assert.InRange(60 / MusicSynth.SecondsPerBeat(Track.LobbyPiano), 60, 76);
        // background, not a performance: no accents, quieter than the other tracks, the tune low around middle C
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.True(MusicSynth.BaseVolumeDb(Track.LobbyPiano) < MusicSynth.BaseVolumeDb(Track.ConventPiano));
        var tune = score.Where(n => n.Voice == 2).ToList();
        Assert.All(tune, n => Assert.InRange(n.Midi, MusicSynth.Midi("G3"), MusicSynth.Midi("A4")));
        Assert.All(score, n => Assert.True(n.Midi <= MusicSynth.Midi("A4"), $"{n}"));
        // a pedalled left hand: a bass on the first beat of each chord, its voicing broken over the rest, so a note
        // starts on every beat (no gaps) and none off it (no syncopation)
        var bass = score.Where(n => n.Voice == 0).ToList();
        var chords = score.Where(n => n.Voice == 1).GroupBy(n => n.Beat).ToList();
        Assert.Equal(16, bass.Count(n => n.Beat % 4 == 0));
        Assert.All(bass, n => Assert.Equal(0, n.Beat % 2));
        Assert.Empty(chords.Select(c => c.Key).Intersect(bass.Select(n => n.Beat)));
        Assert.All(score, n => Assert.Equal(0, n.Beat % 1));
        Assert.Equal(Enumerable.Range(0, 64).Select(b => (double)b), score.Select(n => n.Beat).Distinct().Order());
        Assert.All(tune, n => Assert.True(n.Beats >= 1, $"{n}"));
        // AABA: the three A sections open with the same three bars
        IEnumerable<(double, int)> Bars(double from) =>
            tune.Where(n => n.Beat >= from - 1e-6 && n.Beat < from + 12 - 1e-6).Select(n => (Math.Round(n.Beat - from, 6), n.Midi));
        Assert.Equal(Bars(0), Bars(16));
        Assert.Equal(Bars(0), Bars(48));
        Assert.NotEqual(Bars(0), Bars(32));
        // C major: the loop opens on C in the bass, and the last chord is the G dominant leading home
        Assert.Equal(MusicSynth.Midi("C2"), bass[0].Midi);
        var last = chords.MaxBy(c => c.Key)!.Select(n => n.Midi % 12).ToHashSet();
        Assert.Contains(11, last);
        Assert.Contains(5, last);
        Assert.Equal(MusicSynth.Midi("B3"), tune.MaxBy(n => n.Beat)!.Midi);
    }

    [Fact]
    public void PrisonParlourIsTheRoomNotMusic()
    {
        var score = MusicSynth.Score(Track.PrisonParlour);
        Assert.All(score, n => Assert.Equal(Instrument.Foley, n.Instrument));
        Assert.Equal(60, MusicSynth.LengthBeats(Track.PrisonParlour), 6);
        Assert.DoesNotContain(score, n => n.Strident);
        // near silence: a faint room tone under the whole loop, and only a handful of sounds over it
        Assert.Contains(score, n => n.Midi == MusicSynth.Midi("C2") && n.Beat == 0 && n.Beats == 60);
        Assert.InRange(score.Count(n => n.Midi != MusicSynth.Midi("C2")), 4, 16);
        // a couple of short walks, each step close behind the last, and a chair moved
        var steps = score.Where(n => n.Midi == MusicSynth.Midi("D2")).OrderBy(n => n.Beat).ToList();
        Assert.InRange(steps.Count, 4, 12);
        Assert.All(steps, s => Assert.Contains(steps, o => o != s && Math.Abs(o.Beat - s.Beat) <= 0.75 + 1e-9));
        Assert.Contains(score, n => n.Midi == MusicSynth.Midi("E2"));
        Assert.Contains(score, n => n.Midi == MusicSynth.Midi("F2"));
        Assert.True(MusicSynth.BaseVolumeDb(Track.PrisonParlour) < MusicSynth.BaseVolumeDb(Track.ConventPiano));
    }

    [Fact]
    public void InvestigationIsAQuietReflectivePiano()
    {
        var score = MusicSynth.Score(Track.Investigation);
        Assert.All(score, n => Assert.Equal(Instrument.RecordedPiano, n.Instrument));
        Assert.Equal(64, MusicSynth.LengthBeats(Track.Investigation), 6);
        Assert.InRange(60 / MusicSynth.SecondsPerBeat(Track.Investigation), 50, 66);
        // barely there: quieter than every track but the band heard through the alley wall, nothing accented, every
        // note on the beat and a note starting on every beat
        Assert.All(Enum.GetValues<Track>().Where(t => t is not (Track.Investigation or Track.BlueLanternAlley)),
            t => Assert.True(MusicSynth.BaseVolumeDb(Track.Investigation) < MusicSynth.BaseVolumeDb(t), $"{t}"));
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.All(score, n => Assert.Equal(0, n.Beat % 1));
        Assert.Equal(Enumerable.Range(0, 64).Select(b => (double)b), score.Select(n => n.Beat).Distinct().Order());
        // low and dark: nothing above A4; the bass a whole bar to a note, opening on D
        Assert.All(score, n => Assert.True(n.Midi <= MusicSynth.Midi("A4"), $"{n}"));
        var bass = score.Where(n => n.Voice == 0).ToList();
        Assert.Equal(Enumerable.Range(0, 16).Select(b => 4.0 * b), bass.Select(n => n.Beat));
        Assert.Equal(MusicSynth.Midi("D2"), bass[0].Midi);
        // the right hand thinks rather than sings: few, long notes, the first phrase left to the left hand alone,
        // and the last note the leading tone, C-sharp, falling home to D
        var tune = score.Where(n => n.Voice == 2).ToList();
        Assert.All(tune, n => Assert.True(n.Beats >= 2, $"{n}"));
        Assert.True(tune.Count <= 16);
        Assert.True(tune[0].Beat >= 16);
        Assert.Equal(MusicSynth.Midi("C#4"), tune[^1].Midi);
    }

    [Fact]
    public void MansionDreadIsADissonantThrillerLoop()
    {
        var score = MusicSynth.Score(Track.MansionDread);
        double length = MusicSynth.LengthBeats(Track.MansionDread);
        Assert.Equal(56, length);
        // slow and heavy
        Assert.InRange(60 / MusicSynth.SecondsPerBeat(Track.MansionDread), 50, 60);
        Assert.Equal(
            new[] { Instrument.DoubleBass, Instrument.Pizzicato, Instrument.Cello, Instrument.OpenTrumpet }.ToHashSet(),
            score.Select(n => n.Instrument).ToHashSet());
        // background, not a performance: no accents, every note on the beat
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.All(score, n => Assert.Equal(0, n.Beat % 1));
        static bool Dissonant(IEnumerable<int> midis) =>
            midis.SelectMany(a => midis, (a, b) => Math.Abs(a - b) % 12).Any(i => i is 1 or 6 or 11);
        // the bass bows without a break all the way round, grinding by semitones and tritones
        var bass = score.Where(n => n.Instrument == Instrument.DoubleBass).OrderBy(n => n.Beat).ToList();
        Assert.Equal(0, bass[0].Beat);
        Assert.Equal(length, bass[^1].Beat + bass[^1].Beats);
        Assert.All(bass.Zip(bass.Skip(1)), p => Assert.Equal(p.First.Beat + p.First.Beats, p.Second.Beat, 6));
        Assert.All(bass.Zip(bass.Skip(1)), p => Assert.Contains(Math.Abs(p.Second.Midi - p.First.Midi), new[] { 1, 5, 6, 7 }));
        Assert.All(bass, n => Assert.True(n.Beats >= 2, $"{n}"));
        // every pizzicato chord clashes, and they fall at uneven gaps
        var chords = score.Where(n => n.Instrument == Instrument.Pizzicato).GroupBy(n => n.Beat).OrderBy(g => g.Key).ToList();
        Assert.All(chords, c => Assert.True(c.Count() >= 3 && Dissonant(c.Select(n => n.Midi)), $"chord at {c.Key}"));
        Assert.True(chords.Zip(chords.Skip(1), (a, b) => b.Key - a.Key).Distinct().Count() >= 4, "an irregular pulse");
        // the cello bows long, low arcs above the plucked chords; apart from the trumpet everything stays low
        var cello = score.Where(n => n.Instrument == Instrument.Cello).ToList();
        Assert.All(cello, n => Assert.True(n.Beats >= 2, $"{n}"));
        Assert.True(cello.Average(n => n.Midi) > chords.SelectMany(c => c).Average(n => n.Midi));
        Assert.All(score.Where(n => n.Instrument != Instrument.OpenTrumpet), n => Assert.True(n.Midi <= MusicSynth.Midi("Bb3"), $"{n}"));
        // the trumpet stabs once: one brief, dissonant cluster, the highest sound in the piece
        var trumpet = score.Where(n => n.Instrument == Instrument.OpenTrumpet).ToList();
        Assert.Single(trumpet.Select(n => n.Beat).Distinct());
        Assert.All(trumpet, n => Assert.True(n.Beats <= 0.5, $"{n}"));
        Assert.True(Dissonant(trumpet.Select(n => n.Midi)));
        Assert.Equal(Instrument.OpenTrumpet, score.MaxBy(n => n.Midi).Instrument);
        Assert.True(trumpet.Min(n => n.Midi) >= MusicSynth.Midi("F5"), "high-pitched");
    }

    [Fact]
    public void RoseStreetIsSilentButForTheOddCar()
    {
        var score = MusicSynth.Score(Track.RoseStreet);
        double length = MusicSynth.LengthBeats(Track.RoseStreet);
        Assert.Equal(60, length);
        // not music: only cars, nothing accented, a quieter street than the city's traffic
        Assert.All(score, n => Assert.Equal(Instrument.Car, n.Instrument));
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.True(MusicSynth.BaseVolumeDb(Track.RoseStreet) < MusicSynth.BaseVolumeDb(Track.StreetTraffic));
        // the odd car, never two at once, none still passing as the loop wraps, and silence between them
        var cars = score.OrderBy(n => n.Beat).ToList();
        Assert.InRange(cars.Count, 2, 3);
        Assert.All(cars, n => Assert.True(n.Beat > 0 && n.Beat + n.Beats < length, $"{n}"));
        Assert.All(cars.Zip(cars.Skip(1)), p => Assert.True(p.Second.Beat >= p.First.Beat + p.First.Beats + 10, $"{p}"));
        var s = Renders[Track.RoseStreet].Value;
        int frames = MusicSynth.LoopSamples(Track.RoseStreet);
        double spb = MusicSynth.SecondsPerBeat(Track.RoseStreet);
        int quietFrom = (int)((cars[0].Beat + cars[0].Beats + 1) * spb * MusicSynth.SampleRate);
        int quietTo = (int)((cars[1].Beat - 1) * spb * MusicSynth.SampleRate);
        for (int i = 2 * quietFrom; i < 2 * quietTo; i++) Assert.True(Math.Abs(s[i]) < 0.001f, $"sample {i / 2} is silent");
        Assert.True(Math.Abs(s[0]) < 0.001f && Math.Abs(s[2 * frames - 1]) < 0.001f, "silent at the seam");
    }

    [Fact]
    public void AtticHouseIsTheHouseBelowNotMusic()
    {
        var score = MusicSynth.Score(Track.AtticHouse);
        double length = MusicSynth.LengthBeats(Track.AtticHouse);
        Assert.Equal(60, length);
        // not music: the house's hum, steps downstairs and cars outside, nothing accented, quieter than the music
        Assert.All(score, n => Assert.Contains(n.Instrument, new[] { Instrument.Foley, Instrument.Car }));
        Assert.DoesNotContain(score, n => n.Strident);
        Assert.True(MusicSynth.BaseVolumeDb(Track.AtticHouse) < MusicSynth.BaseVolumeDb(Track.ConventPiano));
        // the hum under the whole loop
        Assert.Contains(score, n => n.Instrument == Instrument.Foley && n.Midi == MusicSynth.Midi("C2") && n.Beat == 0 && n.Beats == length);
        // someone walking about below: steps close behind each other, a few walks
        var steps = score.Where(n => n.Instrument == Instrument.Foley && n.Midi == MusicSynth.Midi("D2")).OrderBy(n => n.Beat).ToList();
        Assert.InRange(steps.Count, 6, 20);
        Assert.All(steps, s => Assert.Contains(steps, o => o != s && Math.Abs(o.Beat - s.Beat) <= 0.75 + 1e-9));
        // a car or two going by, never two at once, none still passing as the loop wraps
        var cars = score.Where(n => n.Instrument == Instrument.Car).OrderBy(n => n.Beat).ToList();
        Assert.InRange(cars.Count, 1, 3);
        Assert.All(cars, n => Assert.True(n.Beat > 0 && n.Beat + n.Beats < length, $"{n}"));
        Assert.All(cars.Zip(cars.Skip(1)), p => Assert.True(p.Second.Beat >= p.First.Beat + p.First.Beats, $"{p}"));
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
            [Instrument.Foley] = ("C2", "F2"),
            [Instrument.Cornet] = ("E3", "C6"), [Instrument.Clarinet] = ("D3", "Bb6"), [Instrument.Trombone] = ("E2", "F5"),
            [Instrument.Banjo] = ("C3", "A5"), [Instrument.Tuba] = ("D1", "F4"),
            [Instrument.CityHum] = ("C1", "C3"), [Instrument.Motorcar] = ("C1", "C3"), [Instrument.Streetcar] = ("C2", "C5"),
            [Instrument.Horn] = ("C3", "C6"),
            [Instrument.RecordedSax] = ("Db3", "Ab5"), [Instrument.RecordedBass] = ("E1", "B2"),
            [Instrument.Pizzicato] = ("C2", "C5"), [Instrument.OpenTrumpet] = ("F#3", "D6"),
            [Instrument.RecordedPiano] = ("A0", "C8"), [Instrument.Car] = ("C1", "C3"),
        };
        Assert.All(MusicSynth.Score(track), n =>
            Assert.InRange(n.Midi, MusicSynth.Midi(range[n.Instrument].Low), MusicSynth.Midi(range[n.Instrument].High)));
    }

    public static TheoryData<Instrument> RecordedInstruments => new(Recordings.Instruments);

    [Theory]
    [MemberData(nameof(RecordedInstruments))]
    public void EveryRecordedNoteHasARecordingLongEnough(Instrument instrument)
    {
        var needed = Recordings.Needed(instrument);
        Assert.NotEmpty(needed);
        Assert.All(needed, n =>
        {
            var path = Folder(Recordings.PathOf(instrument, n.Key));
            Assert.True(File.Exists(path), $"{path} is missing: run dotnet run --project tools/music -- recordings");
            double seconds = new FileInfo(path).Length / 2.0 / MusicSynth.SampleRate;
            Assert.True(seconds >= n.Value + Recordings.TailSeconds(instrument),
                $"{path} is {seconds:0.00} s: run dotnet run --project tools/music -- recordings");
        });
        var extra = Directory.GetFiles(Folder(Recordings.Folder(instrument)), "*.pcm").Select(Path.GetFileName)
            .Except(needed.Keys.Select(Recordings.FileName));
        Assert.Empty(extra);
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