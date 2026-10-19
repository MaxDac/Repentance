using System;

namespace Repentance;

public static partial class MusicSynth
{
    // ------------------------------------------------------------------ foley

    /// <summary>
    /// The noises of a room rather than an instrument, one per pitch (see <see cref="Instrument.Foley"/>). Each is
    /// rendered on its own and added into the loop, wrapping over its end.
    /// </summary>
    private static void Foley(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        double held = note.Beats * spb;
        double amp = velocity * (0.85 + 0.3 * rng.NextDouble());
        float[] sound = note.Midi switch
        {
            36 => RoomTone(rng, held),
            38 => Boot(rng),
            40 => ChairDrag(rng, held),
            41 => ChairDown(rng),
            _ => throw new ArgumentOutOfRangeException(nameof(note), $"no foley sound on {note.Midi}"),
        };
        for (int i = 0; i < sound.Length; i++) buf[(start + i) % buf.Length] += (float)(amp * sound[i]);
    }

    /// <summary>How long a held sound overlaps its own start when it wraps round the whole loop.</summary>
    private const double FoleyFade = 1.0;

    /// <summary>Equal-power fades in and out, so a held noise wrapped onto itself crossfades without a dip or a seam.</summary>
    private static double Crossfade(double t, double total) =>
        Math.Sqrt(Math.Min(1, t / FoleyFade) * Math.Clamp((total - t) / FoleyFade, 0, 1));

    private static double Rand(Random rng) => rng.NextDouble() * 2 - 1;

    private static float[] Seconds(double seconds) => new float[(int)(seconds * SampleRate)];

    /// <summary>Filtered noise decaying with time constant <paramref name="tau"/>, from <paramref name="at"/> seconds.</summary>
    private static void Hit(float[] buf, Random rng, double at, double tau, double amp, SoundSynth.Biquad filter,
        double attack = 0.0005)
    {
        int s = (int)(at * SampleRate), n = Math.Min(buf.Length - s, (int)(tau * 7 * SampleRate));
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            buf[s + i] += (float)(amp * Math.Min(1, t / attack) * Math.Exp(-t / tau) * filter.Next(Rand(rng)));
        }
    }

    /// <summary>A damped sine gliding from <paramref name="hz"/> to <paramref name="endHz"/>.</summary>
    private static void Ring(float[] buf, double at, double hz, double endHz, double tau, double amp, double attack = 0.001)
    {
        int s = (int)(at * SampleRate), n = Math.Min(buf.Length - s, (int)(tau * 7 * SampleRate));
        double phase = 0;
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            phase += 2 * Math.PI * (endHz + (hz - endHz) * Math.Exp(-t / (tau * 0.6))) / SampleRate;
            buf[s + i] += (float)(amp * Math.Min(1, t / attack) * Math.Exp(-t / tau) * Math.Sin(phase));
        }
    }


    /// <summary>The room itself: a low rumble of ventilation and the building, and a breath of air in the ducts.</summary>
    private static float[] RoomTone(Random rng, double held)
    {
        var buf = Seconds(held + FoleyFade);
        var rumble = SoundSynth.Biquad.LowPass(160);
        var rumble2 = SoundSynth.Biquad.LowPass(160);
        var air = SoundSynth.Biquad.BandPass(700, 0.6);
        var drift = SoundSynth.Biquad.LowPass(0.3);
        double brown = 0, hum = 0;
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / SampleRate;
            brown = Math.Clamp(brown * 0.997 + 0.06 * Rand(rng), -1, 1);
            hum += 2 * Math.PI * 120 / SampleRate;
            double swell = 1 + 4 * drift.Next(Rand(rng));
            double x = 0.1 * rumble2.Next(rumble.Next(brown)) + 0.05 * swell * air.Next(Rand(rng)) + 0.012 * Math.Sin(hum);
            buf[i] = (float)(x * Crossfade(t, buf.Length / (double)SampleRate));
        }
        return buf;
    }

    /// <summary>A guard's boot on concrete: a hard heel strike, then the sole coming down.</summary>
    private static float[] Boot(Random rng)
    {
        var buf = Seconds(0.35);
        double toe = 0.07 + 0.03 * rng.NextDouble();
        foreach (var (at, a) in new[] { (0.0, 1.0), (toe, 0.4) })
        {
            Hit(buf, rng, at, 0.003, 0.5 * a, SoundSynth.Biquad.HighPass(2500));
            Hit(buf, rng, at, 0.014, a, SoundSynth.Biquad.BandPass(800 + 200 * Rand(rng), 1.2));
            Ring(buf, at, 125, 80, 0.025, 0.5 * a);
        }
        return buf;
    }


    /// <summary>A wooden chair dragged across concrete: its legs judder, sticking and slipping, over a gritty scrape.</summary>
    private static float[] ChairDrag(Random rng, double held)
    {
        double length = Math.Max(0.3, held);
        var buf = Seconds(length + 0.1);
        for (double t = 0.01; t < length; t += 1 / (20 + 14 * rng.NextDouble()))
        {
            double env = Math.Sqrt(Math.Sin(Math.PI * t / length)) * (0.6 + 0.4 * rng.NextDouble());
            Hit(buf, rng, t, 0.01, 0.7 * env, SoundSynth.Biquad.BandPass(380 + 120 * Rand(rng), 3));
            Hit(buf, rng, t, 0.003, 0.25 * env, SoundSynth.Biquad.HighPass(2000));
        }
        var grit = SoundSynth.Biquad.BandPass(1800, 0.8);
        int n = (int)(length * SampleRate);
        for (int i = 0; i < n; i++) buf[i] += (float)(0.18 * Math.Sin(Math.PI * i / n) * grit.Next(Rand(rng)));
        return buf;
    }

    /// <summary>A chair set down, or someone sitting: two legs knocking the floor a moment apart, then the creak of the seat.</summary>
    private static float[] ChairDown(Random rng)
    {
        var buf = Seconds(0.6);
        double second = 0.025 + 0.03 * rng.NextDouble();
        foreach (var (at, a) in new[] { (0.0, 1.0), (second, 0.75) })
        {
            Ring(buf, at, 175, 115, 0.04, 0.8 * a);
            Hit(buf, rng, at, 0.02, 0.6 * a, SoundSynth.Biquad.BandPass(520, 2));
            Hit(buf, rng, at, 0.002, 0.3 * a, SoundSynth.Biquad.HighPass(3000));
        }
        Hit(buf, rng, 0.22, 0.05, 0.12, SoundSynth.Biquad.BandPass(950, 6), attack: 0.02);
        return buf;
    }





}
