using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace Repentance;

public enum Track
{
    /// <summary>The Club: a bolero-like string ostinato climbing from double bass to violins and sinking back down.</summary>
    ClubStrings,
    /// <summary>The church: the organist trying the pipes, then a short mass chorale.</summary>
    ChurchOrgan,
    /// <summary>The convent: a quiet piano prelude, hymn-like over pedalled arpeggios.</summary>
    ConventPiano,
    /// <summary>Micah's office: a slow, depressed minor-key ballad for muted trumpet, piano, upright bass and brushes.</summary>
    OfficeJazz,
    /// <summary>The Blue Lantern: a Chicago hot-jazz band rehearsing across the room, behind the curtain.</summary>
    BlueLanternJazz,
    /// <summary>The same rehearsal heard from the alley, through the open back door and down a passage.</summary>
    BlueLanternAlley,
    /// <summary>The streets outside: no music at all, only 1920s Chicago traffic going by on a wet road.</summary>
    StreetTraffic,
    /// <summary>The Aurelian Hotel lobby: a house pianist's soft 1920s foxtrot over a hushed, pedalled stride.</summary>
    LobbyPiano,
    /// <summary>Investigation: a slow, reflective D-minor piano, pianissimo and barely audible, to think by.</summary>
    Investigation,
    /// <summary>The Harrington mansion: a dark, dissonant thriller loop for double bass, pizzicato chords, bowed cello
    /// and one brief, piercing trumpet stab.</summary>
    MansionDread,
}

public enum Instrument
{
    DoubleBass,
    Cello,
    Viola,
    Violin,
    /// <summary>Soft organ flute stops, 8' and 4'.</summary>
    OrganFlute,
    /// <summary>The organ's full principal chorus with its mixtures.</summary>
    OrganPlenum,
    /// <summary>Organ pedal, 16' and 8'.</summary>
    OrganPedal,
    Piano,
    /// <summary>A real grand piano, played pianissimo: recordings of each note (<see cref="PianoRecordings"/>).</summary>
    RecordedPiano,
    /// <summary>A trumpet played soft through a Harmon mute.</summary>
    Trumpet,
    /// <summary>A plucked upright bass.</summary>
    UprightBass,
    /// <summary>A brushed kit. The pitch picks the drum, General MIDI style: C2 kick, C#2 sticks clicked together,
    /// D2 brush tap, E2 brush sweep, F#2 hi-hat, Eb3 ride.</summary>
    Drums,
    /// <summary>An open cornet, played hot.</summary>
    Cornet,
    /// <summary>A Bb clarinet in the old Albert-system style: woody, with a wide vibrato.</summary>
    Clarinet,
    /// <summary>A tailgate trombone; a strident note is smeared up into from below.</summary>
    Trombone,
    /// <summary>A tenor banjo, chords strummed low string first.</summary>
    Banjo,
    /// <summary>A brass bass horn, the band's two-beat bottom.</summary>
    Tuba,
    /// <summary>The city's distant roar, a noise bed for the whole loop.</summary>
    CityHum,
    /// <summary>A motorcar driving past, from the part's side to the other; the pitch is the engine's firing note,
    /// and an accented car passes close.</summary>
    Motorcar,
    /// <summary>A streetcar rolling past with its bell, rail joints and motor whine at the note's pitch.</summary>
    Streetcar,
    /// <summary>A car horn at the note's pitch: a bulb horn's double honk, or, accented, an "ah-oo-gah" klaxon.</summary>
    Horn,
    /// <summary>Plucked string chords, pizzicato, on cello and viola strings.</summary>
    Pizzicato,
    /// <summary>An open trumpet, unmuted, hard-tongued and piercing.</summary>
    OpenTrumpet,
}

/// <summary>One note: <see cref="Voice"/> is the player's part, times are in beats, pitch in MIDI.</summary>
public readonly record struct ScoreNote(Instrument Instrument, int Voice, double Beat, double Beats, int Midi, bool Strident);

/// <summary>
/// Synthesizes the background music: original pieces written as scores and played by synthesized instruments (bowed
/// strings, pizzicato, pipe organ, piano, muted and open trumpet, plucked bass, brushed drums, a hot band's horns, banjo
/// and tuba) in a reverberant room, sometimes heard from a distance, plus the street's traffic, scored the same way
/// for engines, horns and a streetcar. Each track renders exactly
/// one period of an endless loop, so it repeats without a seam. Output is interleaved stereo floats in [-1, 1] at
/// <see cref="SampleRate"/>. Godot-free, so it is unit tested directly.
/// </summary>
/// <remarks>
/// A part's notes are space-separated tokens <c>name:beats</c>: <c>r</c> is a rest, <c>D3+F3+A3</c> a chord, the
/// length may be a fraction (<c>2/3</c> for a swung eighth), <c>0.5&gt;2</c> moves on half a beat but lets the note
/// ring for two (a pedalled piano), and a trailing <c>!</c> marks a strident or accented note.
/// </remarks>
public static partial class MusicSynth
{
    public const int SampleRate = SoundSynth.SampleRate;
    private const double Peak = 0.9;

    private sealed record Part(Instrument Instrument, double Velocity, double Pan, string Notes);

    /// <summary>The space a piece is played in: comb delays scale with <see cref="Size"/>.</summary>
    private sealed record Hall(double Size, double Feedback, double Damp, double Wet);

    /// <summary>
    /// A band heard from somewhere else: the sound band-limited between <see cref="HighPass"/> and
    /// <see cref="LowPass"/>, its stereo narrowed to <see cref="Width"/> (0 mono, 1 as played), and a soft echo off a
    /// far wall every <see cref="EchoSeconds"/>.
    /// </summary>
    private sealed record Distance(double HighPass, double LowPass, double Width, double EchoSeconds, double EchoFeedback,
        double EchoMix);

    private sealed record Piece(double Bpm, Hall Hall, Part[] Parts, bool Gramophone = false, Distance? Distance = null);

    private static Hall Concert => new(1, 0.88, 0.35, 0.32);

    public static double SecondsPerBeat(Track track) => 60 / PieceFor(track).Bpm;

    /// <summary>The loop's length: the longest part, counting its rests.</summary>
    public static double LengthBeats(Track track) => Parse(PieceFor(track)).Length;

    /// <summary>Samples per channel in one period of the loop.</summary>
    public static int LoopSamples(Track track) =>
        (int)Math.Round(LengthBeats(track) * SecondsPerBeat(track) * SampleRate);

    /// <summary>Playback level of each track relative to the Music bus, in dB, evening out how loud they feel.</summary>
    public static float BaseVolumeDb(Track track) => track switch
    {
        Track.ChurchOrgan => -7.5f,
        Track.ConventPiano => -7.5f,
        Track.OfficeJazz => -15f,
        Track.BlueLanternJazz => -13f,
        Track.BlueLanternAlley => -27f,
        Track.StreetTraffic => -13f,
        Track.LobbyPiano => -12f,
        Track.Investigation => -20f,
        Track.MansionDread => -8.5f,
        _ => -6f,
    };

    public static IReadOnlyList<ScoreNote> Score(Track track) => Parse(PieceFor(track)).Notes;

    /// <summary>Two tracks playing the same score (one band heard from two places), so one can take over from the
    /// other at the same moment of the loop.</summary>
    public static bool SharesScore(Track a, Track b) => ReferenceEquals(PieceFor(a).Parts, PieceFor(b).Parts);

    private static (List<ScoreNote> Notes, double Length) Parse(Piece piece)
    {
        var notes = new List<ScoreNote>();
        double length = 0;
        for (int voice = 0; voice < piece.Parts.Length; voice++)
        {
            var part = piece.Parts[voice];
            double beat = 0;
            foreach (var token in part.Notes.Split(' ', StringSplitOptions.RemoveEmptyEntries))
            {
                int colon = token.LastIndexOf(':');
                string names = token[..colon], timing = token[(colon + 1)..];
                bool strident = timing.EndsWith('!');
                var times = timing.TrimEnd('!').Split('>');
                double advance = Beats(times[0]), held = times.Length > 1 ? Beats(times[1]) : advance;
                if (names != "r")
                    foreach (var name in names.Split('+'))
                        notes.Add(new ScoreNote(part.Instrument, voice, beat, held, Midi(name), strident));
                beat += advance;
            }
            length = Math.Max(length, beat);
        }
        return (notes, length);
    }

    private static double Beats(string text)
    {
        var f = text.Split('/');
        double v = double.Parse(f[0], CultureInfo.InvariantCulture);
        return f.Length > 1 ? v / double.Parse(f[1], CultureInfo.InvariantCulture) : v;
    }

    /// <summary>"C#3", "Bb1", "A5" as a MIDI note number (C4 = 60).</summary>
    public static int Midi(string name)
    {
        int pc = "C D EF G A B".IndexOf(name[0]);
        if (pc < 0) throw new FormatException($"Bad note name {name}");
        int i = 1;
        for (; i < name.Length && (name[i] == '#' || name[i] == 'b'); i++) pc += name[i] == '#' ? 1 : -1;
        return 12 * (int.Parse(name[i..]) + 1) + pc;
    }

    public static double Hz(int midi) => 440 * Math.Pow(2, (midi - 69) / 12.0);

    private static double Cents(double cents) => Math.Exp(cents * (Math.Log(2) / 1200));

    // ------------------------------------------------------------------ rendering

    public static float[] Render(Track track)
    {
        var piece = PieceFor(track);
        var score = Parse(piece).Notes;
        int length = LoopSamples(track);
        double spb = SecondsPerBeat(track);
        var rng = new Random(((int)track + 1) * 15485863);
        var left = new float[length];
        var right = new float[length];

        for (int voice = 0; voice < piece.Parts.Length; voice++)
        {
            var part = piece.Parts[voice];
            // one period of the part, wrapped: a note held over the end of the loop sounds again at its start
            var raw = new float[length];
            // a moving source pans itself, note by note, so it is rendered in stereo from the start
            var rawRight = Moves(part.Instrument) ? new float[length] : null;
            foreach (var note in score.Where(n => n.Voice == voice))
                Sound(raw, rawRight, rng, note, spb, part.Velocity, part.Pan);

            // run the body twice round the loop and keep the second lap, so the filters start in their looping state
            double pan = (part.Pan + 1) * Math.PI / 4;
            var channels = rawRight == null
                ? new[] { (raw, (float)Math.Cos(pan), (float)Math.Sin(pan)) }
                : new[] { (raw, 1f, 0f), (rawRight, 0f, 1f) };
            foreach (var (source, gl, gr) in channels)
            {
                var body = BodyOf(part.Instrument);
                for (int i = 0; i < 2 * length; i++)
                {
                    double x = source[i % length] + Dither(i);
                    for (int k = 0; k < body.Length; k++) x = body[k].Next(x);
                    if (i < length) continue;
                    left[i - length] += (float)(x * gl);
                    right[i - length] += (float)(x * gr);
                }
            }
        }

        Reverb(left, right, piece.Hall);
        if (piece.Gramophone) Gramophone(left, right, rng);
        if (piece.Distance is { } distance) Distant(left, right, distance);
        var stereo = new float[length * 2];
        float peak = 1e-6f;
        for (int i = 0; i < length; i++) peak = Math.Max(peak, Math.Max(Math.Abs(left[i]), Math.Abs(right[i])));
        float gain = (float)(Peak / peak);
        for (int i = 0; i < length; i++)
        {
            stereo[2 * i] = left[i] * gain;
            stereo[2 * i + 1] = right[i] * gain;
        }
        return stereo;
    }

    /// <summary>Inaudible noise that keeps filters ringing down through silence out of slow denormal arithmetic.</summary>
    private static double Dither(int i) => ((uint)i * 2654435761u >> 20) / 4096.0 * 2e-10 - 1e-10;

    private static double Smooth(double x)
    {
        x = Math.Clamp(x, 0, 1);
        return x * x * (3 - 2 * x);
    }

    private static double PolyBlep(double t, double dt)
    {
        if (t < dt) { t /= dt; return t + t - t * t - 1; }
        if (t > 1 - dt) { t = (t - 1) / dt; return t * t + t + t + 1; }
        return 0;
    }

    /// <summary>
    /// A Schroeder/Freeverb-style room, run twice round the loop so its tail from the end of the period rings on into
    /// the start exactly as it will when the track repeats.
    /// </summary>
    private static void Reverb(float[] left, float[] right, Hall hall)
    {
        int length = left.Length;
        int[] combs = { 558, 594, 638, 678, 711, 745, 778, 808 }, allpasses = { 278, 220, 170, 112 };
        const int spread = 12;
        const double input = 0.06;
        var chans = new[] { left, right };
        var wetOut = new[] { new float[length], new float[length] };
        for (int c = 0; c < 2; c++)
        {
            var combBuf = combs.Select(d => new double[(int)(d * hall.Size) + c * spread]).ToArray();
            var combStore = new double[combs.Length];
            var combIdx = new int[combs.Length];
            var apBuf = allpasses.Select(d => new double[(int)(d * hall.Size) + c * spread]).ToArray();
            var apIdx = new int[allpasses.Length];
            var pre = SoundSynth.Biquad.HighPass(140);
            for (int i = 0; i < 2 * length; i++)
            {
                double x = pre.Next((left[i % length] + right[i % length]) * input + Dither(i)), y = 0;
                for (int k = 0; k < combBuf.Length; k++)
                {
                    var b = combBuf[k];
                    double o = b[combIdx[k]];
                    combStore[k] = o * (1 - hall.Damp) + combStore[k] * hall.Damp;
                    b[combIdx[k]] = x + combStore[k] * hall.Feedback;
                    if (++combIdx[k] == b.Length) combIdx[k] = 0;
                    y += o;
                }
                for (int k = 0; k < apBuf.Length; k++)
                {
                    var b = apBuf[k];
                    double o = b[apIdx[k]];
                    b[apIdx[k]] = y + o * 0.5;
                    y = o - y;
                    if (++apIdx[k] == b.Length) apIdx[k] = 0;
                }
                if (i >= length) wetOut[c][i - length] = (float)(y * hall.Wet);
            }
        }
        for (int c = 0; c < 2; c++)
            for (int i = 0; i < length; i++) chans[c][i] += wetOut[c][i];
    }

    /// <summary>
    /// Moves the band further away (see <see cref="Distance"/>). Like the reverb it runs twice round the loop, so the
    /// filters and the echo from the end of the period carry on into its start.
    /// </summary>
    private static void Distant(float[] left, float[] right, Distance distance)
    {
        int length = left.Length;
        int delay = (int)Math.Round(distance.EchoSeconds * SampleRate);
        var outs = new[] { new float[length], new float[length] };
        for (int c = 0; c < 2; c++)
        {
            var filters = new[]
            {
                SoundSynth.Biquad.HighPass(distance.HighPass), SoundSynth.Biquad.HighPass(distance.HighPass),
                SoundSynth.Biquad.LowPass(distance.LowPass), SoundSynth.Biquad.LowPass(distance.LowPass),
            };
            // the echo comes back a little later on the right (less, the narrower the band), and darker each time round
            var echo = new double[delay + c * (int)Math.Round(323 * distance.Width)];
            var echoDark = SoundSynth.Biquad.LowPass(Math.Min(2000, distance.LowPass));
            int at = 0;
            for (int i = 0; i < 2 * length; i++)
            {
                int j = i % length;
                double mid = (left[j] + right[j]) * 0.5, side = (left[j] - right[j]) * 0.5 * distance.Width;
                double x = (c == 0 ? mid + side : mid - side) + Dither(i);
                for (int k = 0; k < filters.Length; k++) x = filters[k].Next(x);
                double back = echoDark.Next(echo[at]);
                echo[at] = x + back * distance.EchoFeedback;
                if (++at == echo.Length) at = 0;
                if (i >= length) outs[c][j] = (float)(x + back * distance.EchoMix);
            }
        }
        Array.Copy(outs[0], left, length);
        Array.Copy(outs[1], right, length);
    }

    /// <summary>
    /// An old 78 on a gramophone: nearly mono, the lows and highs cut away, a little surface hiss and crackle. Like the
    /// reverb it runs twice round the loop, and the crackle is part of the loop, so the seam stays clean.
    /// </summary>
    private static void Gramophone(float[] left, float[] right, Random rng)
    {
        int length = left.Length;
        float peak = 1e-6f;
        for (int i = 0; i < length; i++) peak = Math.Max(peak, Math.Max(Math.Abs(left[i]), Math.Abs(right[i])));
        var surface = new float[length];
        var hiss = SoundSynth.Biquad.HighPass(2500);
        for (int i = 0; i < length; i++) surface[i] = (float)(peak * 0.012 * hiss.Next(rng.NextDouble() * 2 - 1));
        for (int p = 0, pops = length / SampleRate * 6; p < pops; p++)
        {
            int at = rng.Next(length);
            double amp = peak * (0.01 + 0.09 * Math.Pow(rng.NextDouble(), 4)) * (rng.Next(2) * 2 - 1);
            for (int k = 0; k < 12; k++) surface[(at + k) % length] += (float)(amp * Math.Exp(-k / 2.5) * (k % 2 == 0 ? 1 : -0.5));
        }
        var outs = new[] { new float[length], new float[length] };
        for (int c = 0; c < 2; c++)
        {
            var horn = new[]
            {
                SoundSynth.Biquad.HighPass(170), SoundSynth.Biquad.HighPass(170), SoundSynth.Biquad.Peaking(1600, 3, 0.9),
                SoundSynth.Biquad.LowPass(4300), SoundSynth.Biquad.LowPass(4300),
            };
            for (int i = 0; i < 2 * length; i++)
            {
                int j = i % length;
                double mono = (left[j] + right[j]) * 0.5;
                double x = 0.8 * mono + 0.2 * (c == 0 ? left[j] : right[j]) + surface[j] + Dither(i);
                for (int k = 0; k < horn.Length; k++) x = horn[k].Next(x);
                if (i >= length) outs[c][j] = (float)x;
            }
        }
        Array.Copy(outs[0], left, length);
        Array.Copy(outs[1], right, length);
    }
}
