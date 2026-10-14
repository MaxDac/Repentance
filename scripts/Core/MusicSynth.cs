using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

public enum Track
{
    /// <summary>The Club: a bolero-like string ostinato climbing from double bass to violins and sinking back down.</summary>
    ClubStrings,
}

public enum StringInstrument { DoubleBass, Cello, Viola, Violin }

/// <summary>One bowed note: <see cref="Voice"/> is the player's part, times are in beats, pitch in MIDI.</summary>
public readonly record struct ScoreNote(StringInstrument Instrument, int Voice, double Beat, double Beats, int Midi, bool Strident);

/// <summary>
/// Synthesizes the background music: original pieces written as scores and played by bowed-string voices (band-limited
/// sawtooth bowing through a body resonance, delayed vibrato, bow noise) in a small reverberant hall. Each track renders
/// exactly one period of an endless loop, so it repeats without a seam. Output is interleaved stereo floats in [-1, 1]
/// at <see cref="SampleRate"/>. Godot-free, so it is unit tested directly.
/// </summary>
public static class MusicSynth
{
    public const int SampleRate = SoundSynth.SampleRate;
    private const double Peak = 0.9;

    private sealed record Part(StringInstrument Instrument, double Velocity, double Pan, string Notes);

    private sealed record Piece(double Bpm, Part[] Parts);

    // A bolero in 3/4 on the D diminished (octatonic) colours, D Eb F# G# A C: all tritones (D-G#, A-Eb, C-F#), no
    // minor third. The double bass bows one slow four-bar ostinato in long swelling strokes for all 24 bars;
    // every note is bowed, at least a beat long, one stroke flowing into the next.
    // A four-bar theme comes round again and again: the cello alone, then over a second cello droning the tritones
    // beneath it, the viola an octave up, and at the very end two strident violins a tritone apart, before everything
    // falls away down to the bass, which leads home.
    private const string ClubTheme = "D3:2 Eb3:1 G#3:3 A3:2 F#3:1 C3:1 D3:2 ";

    private static readonly Piece Club = new(72, new Part[]
    {
        new(StringInstrument.DoubleBass, 0.95, 0.1, Repeat("D2:2 Eb2:1 G#1:3 F#1:2 C2:1 A1:3 ", 6)),
        new(StringInstrument.Cello, 0.75, 0.35,
            "r:12 " + Repeat(ClubTheme, 4) + "Eb3:2 C3:1 A2:2 G#2:1"),
        new(StringInstrument.Cello, 0.5, -0.1,
            "r:24 " + Repeat("G#2:3 D3:3 C3:3 A2:3 ", 3)),
        new(StringInstrument.Viola, 0.6, -0.3,
            "r:45 A3:3 " + ClubTheme.Replace("3:", "4:") + "C4:2 A3:1"),
        new(StringInstrument.Violin, 0.5, -0.45,
            "r:48 D5:2! Eb5:1! G#5:3! A5:2! F#5:1! C6:2! G#5:1!"),
        new(StringInstrument.Violin, 0.4, 0.45,
            "r:48 G#4:3! D5:3! C5:3! A4:3!"),
    });

    private static string Repeat(string notes, int times) => string.Concat(Enumerable.Repeat(notes, times));

    private static Piece PieceFor(Track track) => track switch
    {
        Track.ClubStrings => Club,
        _ => throw new ArgumentOutOfRangeException(nameof(track)),
    };

    public static double SecondsPerBeat(Track track) => 60 / PieceFor(track).Bpm;

    public static double LengthBeats(Track track) => Score(track).Max(n => n.Beat + n.Beats);

    /// <summary>Samples per channel in one period of the loop.</summary>
    public static int LoopSamples(Track track) =>
        (int)Math.Round(LengthBeats(track) * SecondsPerBeat(track) * SampleRate);

    /// <summary>Playback level of each track relative to the Music bus, in dB.</summary>
    public static float BaseVolumeDb(Track track) => track switch
    {
        _ => -6f,
    };

    public static IReadOnlyList<ScoreNote> Score(Track track)
    {
        var notes = new List<ScoreNote>();
        var parts = PieceFor(track).Parts;
        for (int voice = 0; voice < parts.Length; voice++)
        {
            double beat = 0;
            foreach (var token in parts[voice].Notes.Split(' ', StringSplitOptions.RemoveEmptyEntries))
            {
                var (name, length) = (token.Split(':')[0], token.Split(':')[1]);
                bool strident = length.EndsWith('!');
                double beats = double.Parse(length.TrimEnd('!'), System.Globalization.CultureInfo.InvariantCulture);
                if (name != "r") notes.Add(new ScoreNote(parts[voice].Instrument, voice, beat, beats, Midi(name), strident));
                beat += beats;
            }
        }
        return notes;
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

    // ------------------------------------------------------------------ rendering

    private sealed record Timbre(double Attack, double Release, double VibratoHz, double VibratoCents, double Noise,
        Func<SoundSynth.Biquad[]> Body);

    private static Timbre TimbreOf(StringInstrument instrument) => instrument switch
    {
        StringInstrument.DoubleBass => new(0.32, 0.7, 4.8, 9, 0.025, () => new[]
        {
            SoundSynth.Biquad.HighPass(32), SoundSynth.Biquad.Peaking(105, 5, 1.1), SoundSynth.Biquad.Peaking(420, -3, 1),
            SoundSynth.Biquad.Peaking(950, 3, 1.6), SoundSynth.Biquad.LowPass(1700), SoundSynth.Biquad.LowPass(2600),
        }),
        StringInstrument.Cello => new(0.24, 0.55, 5.3, 13, 0.03, () => new[]
        {
            SoundSynth.Biquad.HighPass(60), SoundSynth.Biquad.Peaking(220, 4, 1.2), SoundSynth.Biquad.Peaking(620, 2, 1.2),
            SoundSynth.Biquad.Peaking(1450, 3, 1.5), SoundSynth.Biquad.LowPass(3600), SoundSynth.Biquad.LowPass(5200),
        }),
        StringInstrument.Viola => new(0.2, 0.5, 5.6, 14, 0.035, () => new[]
        {
            SoundSynth.Biquad.HighPass(115), SoundSynth.Biquad.Peaking(360, 4, 1.2), SoundSynth.Biquad.Peaking(900, 2, 1.3),
            SoundSynth.Biquad.Peaking(2300, 3, 1.5), SoundSynth.Biquad.LowPass(4600), SoundSynth.Biquad.LowPass(6400),
        }),
        _ => new(0.12, 0.45, 6.0, 18, 0.04, () => new[]
        {
            SoundSynth.Biquad.HighPass(190), SoundSynth.Biquad.Peaking(490, 4, 1.3), SoundSynth.Biquad.Peaking(1250, 1, 1.4),
            SoundSynth.Biquad.Peaking(3100, 6, 1.2), SoundSynth.Biquad.LowPass(7800),
        }),
    };

    public static float[] Render(Track track)
    {
        var piece = PieceFor(track);
        var score = Score(track);
        int length = LoopSamples(track);
        double spb = SecondsPerBeat(track);
        var rng = new Random(((int)track + 1) * 15485863);
        var left = new float[length];
        var right = new float[length];

        for (int voice = 0; voice < piece.Parts.Length; voice++)
        {
            var part = piece.Parts[voice];
            var timbre = TimbreOf(part.Instrument);
            // one period of the part, wrapped: a note held over the end of the loop sounds again at its start
            var raw = new float[length];
            foreach (var note in score.Where(n => n.Voice == voice))
                Bow(raw, rng, note, spb, part.Velocity, timbre);

            // run the body twice round the loop and keep the second lap, so the filters start in their looping state
            var body = timbre.Body();
            double pan = (part.Pan + 1) * Math.PI / 4;
            float gl = (float)Math.Cos(pan), gr = (float)Math.Sin(pan);
            for (int i = 0; i < 2 * length; i++)
            {
                double x = raw[i % length] + Dither(i);
                for (int k = 0; k < body.Length; k++) x = body[k].Next(x);
                if (i < length) continue;
                left[i - length] += (float)(x * gl);
                right[i - length] += (float)(x * gr);
            }
        }

        Reverb(left, right);
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

    /// <summary>
    /// One bow stroke: a band-limited sawtooth (the string's stick-slip motion) swelling in and out like an arc,
    /// vibrato that blooms after the attack, a little bow hiss. Strident notes are played near the bridge with a wide,
    /// fast vibrato: brighter and harsher, but still one continuous stroke.
    /// </summary>
    private static void Bow(float[] buf, Random rng, ScoreNote note, double spb, double velocity, Timbre timbre)
    {
        double held = note.Beats * spb, attack = note.Strident ? 0.15 : timbre.Attack, release = timbre.Release;
        double vibHz = (note.Strident ? 6.8 : timbre.VibratoHz) * (1 + 0.04 * (rng.NextDouble() * 2 - 1));
        double vibCents = note.Strident ? 24 : timbre.VibratoCents, noise = note.Strident ? timbre.Noise * 3 : timbre.Noise;
        double f0 = Hz(note.Midi), amp = velocity * (note.Strident ? 1.15 : 1);
        int start = (int)Math.Round(note.Beat * spb * SampleRate), n = (int)((held + release) * SampleRate);
        var drift = SoundSynth.Biquad.LowPass(3);
        var pressure = SoundSynth.Biquad.LowPass(4);
        var hiss = SoundSynth.Biquad.BandPass(Math.Min(6000, f0 * 6), 0.8);
        double phase = rng.NextDouble(), phase2 = rng.NextDouble(), vibPhase = rng.NextDouble() * 2 * Math.PI;
        // a bowed stroke never starts in tune with the last: alternate down- and up-bow weight
        double bowWeight = 0.9 + 0.2 * rng.NextDouble();
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double env = Smooth(t / attack) * (t < held ? 1 : Math.Cos(Math.PI / 2 * Math.Min(1, (t - held) / release)));
            double arc = 0.72 + 0.28 * Math.Sin(Math.PI * Math.Min(1, t / Math.Max(held, 0.2)));
            env *= arc * bowWeight * (1 + 0.6 * pressure.Next(rng.NextDouble() * 2 - 1));

            double vib = vibCents * Smooth((t - 0.3) / 0.6) * Math.Sin(vibPhase + 2 * Math.PI * vibHz * t);
            double cents = vib + 40 * drift.Next(rng.NextDouble() * 2 - 1);
            double dt = f0 * Math.Exp(cents * (Math.Log(2) / 1200)) / SampleRate;
            phase += dt; if (phase >= 1) phase -= 1;
            double s = 2 * phase - 1 - PolyBlep(phase, dt);
            if (note.Strident)
            {
                // near the bridge the upper partials take over
                phase2 += 2 * dt; if (phase2 >= 1) phase2 -= 1;
                s = 0.75 * s + 0.45 * (2 * phase2 - 1 - PolyBlep(phase2, 2 * dt));
            }
            s += noise * 6 * hiss.Next(rng.NextDouble() * 2 - 1);
            buf[(start + i) % buf.Length] += (float)(amp * env * 0.25 * s);
        }
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
    /// A Schroeder/Freeverb-style hall, run twice round the loop so its tail from the end of the period rings on into
    /// the start exactly as it will when the track repeats.
    /// </summary>
    private static void Reverb(float[] left, float[] right)
    {
        int length = left.Length;
        int[] combs = { 558, 594, 638, 678, 711, 745, 778, 808 }, allpasses = { 278, 220, 170, 112 };
        const int spread = 12;
        const double feedback = 0.88, damp = 0.35, wet = 0.32, input = 0.06;
        var chans = new[] { left, right };
        var wetOut = new[] { new float[length], new float[length] };
        for (int c = 0; c < 2; c++)
        {
            var combBuf = combs.Select(d => new double[d + c * spread]).ToArray();
            var combStore = new double[combs.Length];
            var combIdx = new int[combs.Length];
            var apBuf = allpasses.Select(d => new double[d + c * spread]).ToArray();
            var apIdx = new int[allpasses.Length];
            var pre = SoundSynth.Biquad.HighPass(140);
            for (int i = 0; i < 2 * length; i++)
            {
                double x = pre.Next((left[i % length] + right[i % length]) * input + Dither(i)), y = 0;
                for (int k = 0; k < combBuf.Length; k++)
                {
                    var b = combBuf[k];
                    double o = b[combIdx[k]];
                    combStore[k] = o * (1 - damp) + combStore[k] * damp;
                    b[combIdx[k]] = x + combStore[k] * feedback;
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
                if (i >= length) wetOut[c][i - length] = (float)(y * wet);
            }
        }
        for (int c = 0; c < 2; c++)
            for (int i = 0; i < length; i++) chans[c][i] += wetOut[c][i];
    }
}
