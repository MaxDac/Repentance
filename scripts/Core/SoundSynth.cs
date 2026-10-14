using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace Repentance;

public enum Sound
{
    StepWood, StepStone, StepCarpet,
    Gunshot, Knock, Clang, Crash, Thunk, Crack, Rustle, Click, Scrape, Explosion, Hiss, DoorSlam, Bell,
    Rain,
}

/// <summary>What the floor of a room is made of; picks the footstep sound.</summary>
public enum FloorSurface { Wood, Stone, Carpet }

/// <summary>A sound to play <see cref="Delay"/> seconds after the line that asked for it.</summary>
public readonly record struct SoundCue(Sound Sound, double Delay);

/// <summary>
/// Synthesizes every sound effect from seeded noise and damped oscillators, so the game ships no audio files and
/// renders are reproducible. Samples are mono floats in [-1, 1] at <see cref="SampleRate"/>. Godot-free, so it is unit
/// tested directly.
/// </summary>
public static class SoundSynth
{
    public const int SampleRate = 22050;
    public const double RainLoopSeconds = 4;
    public const int StepVariants = 4;
    private const double Peak = 0.9;

    public static Sound StepFor(FloorSurface floor) => floor switch
    {
        FloorSurface.Stone => Sound.StepStone,
        FloorSurface.Carpet => Sound.StepCarpet,
        _ => Sound.StepWood,
    };

    /// <summary>Playback level of each sound relative to the Effects bus, in dB.</summary>
    public static float BaseVolumeDb(Sound sound) => sound switch
    {
        Sound.StepWood or Sound.StepStone => -13f,
        Sound.StepCarpet => -11f,
        Sound.Rustle or Sound.Click or Sound.Hiss => -6f,
        Sound.Rain => -14f,
        Sound.Gunshot or Sound.Explosion => 0f,
        _ => -3f,
    };

    /// <summary>A 0-100 volume setting as bus gain; 0 is effectively silent.</summary>
    public static float PercentToDb(int percent) =>
        percent <= 0 ? -80f : 20f * MathF.Log10(Math.Clamp(percent, 0, 100) / 100f);

    public static float[] Render(Sound sound, int variant = 0)
    {
        var rng = new Random(((int)sound + 1) * 7919 + variant * 104729);
        var buf = sound switch
        {
            Sound.StepWood => Step(rng, body: 520, q: 1.6, tau: 0.018, click: 0.55, thump: 0.45),
            Sound.StepStone => Step(rng, body: 1900, q: 0.9, tau: 0.009, click: 1.0, thump: 0.15),
            Sound.StepCarpet => Step(rng, body: 260, q: 0.8, tau: 0.03, click: 0.0, thump: 0.3),
            Sound.Gunshot => Gunshot(rng),
            Sound.Knock => Knock(rng),
            Sound.Clang => Clang(rng),
            Sound.Crash => Crash(rng),
            Sound.Thunk => Thunk(rng),
            Sound.Crack => Crack(rng),
            Sound.Rustle => Rustle(rng),
            Sound.Click => Click(rng),
            Sound.Scrape => Scrape(rng),
            Sound.Explosion => Explosion(rng),
            Sound.Hiss => Hiss(rng),
            Sound.DoorSlam => DoorSlam(rng),
            Sound.Bell => Bell(rng),
            Sound.Rain => Rain(rng),
            _ => throw new ArgumentOutOfRangeException(nameof(sound)),
        };
        Normalize(buf);
        return buf;
    }

    // ------------------------------------------------------------------ onomatopoeia

    private static readonly (Regex Pattern, Sound Sound)[] Words =
    {
        (new(@"\bbang\b"), Sound.Gunshot),
        (new(@"\bclang\b"), Sound.Clang),
        (new(@"\bcrash\b"), Sound.Crash),
        (new(@"\bthunk\b"), Sound.Thunk),
        (new(@"\bcrack\b"), Sound.Crack),
        (new(@"\brustle\b"), Sound.Rustle),
        (new(@"\bclick\b"), Sound.Click),
        (new(@"\bscra+pe\b"), Sound.Scrape),
        (new(@"\bbo{2,}m\b"), Sound.Explosion),
        (new(@"\bhs{3,}\b"), Sound.Hiss),
        (new(@"\bring\b"), Sound.Bell),
    };

    /// <summary>
    /// The sounds a spoken line stands for. Only sound-effect lines, which start with an asterisk ("*BANG*",
    /// "*Knock knock*... *knock*", "*A car door slams.*"), make noise; ordinary speech never does.
    /// </summary>
    public static IReadOnlyList<SoundCue> CuesFor(string text)
    {
        var cues = new List<SoundCue>();
        var line = text.Trim();
        if (!line.StartsWith('*')) return cues;
        line = line.ToLowerInvariant();

        if (line.Contains("knock"))
        {
            double t = 0;
            foreach (Match m in Regex.Matches(line, @"knock|\.\.\."))
            {
                if (m.Value == "...") { t += 0.35; continue; }
                cues.Add(new SoundCue(Sound.Knock, t));
                t += 0.24;
            }
        }
        if (line.Contains("footsteps"))
            for (int i = 0; i < 5; i++) cues.Add(new SoundCue(Sound.StepWood, i * 0.42));
        if (Regex.IsMatch(line, @"\bslam"))
        {
            cues.Add(new SoundCue(Sound.DoorSlam, 0));
            if (Regex.IsMatch(line, @"\btwo\b")) cues.Add(new SoundCue(Sound.DoorSlam, 0.32));
        }
        foreach (var (pattern, sound) in Words)
            if (pattern.IsMatch(line)) cues.Add(new SoundCue(sound, 0));
        return cues;
    }

    // ------------------------------------------------------------------ building blocks

    private static float[] Buffer(double seconds) => new float[(int)(seconds * SampleRate)];

    private static double Noise(Random rng) => rng.NextDouble() * 2 - 1;

    private static int At(double seconds) => (int)(seconds * SampleRate);

    /// <summary>RBJ biquad: band-pass (constant peak gain) or low/high-pass.</summary>
    private struct Biquad
    {
        private double _b0, _b1, _b2, _a1, _a2, _x1, _x2, _y1, _y2;

        public static Biquad BandPass(double hz, double q)
        {
            double w = 2 * Math.PI * hz / SampleRate, alpha = Math.Sin(w) / (2 * q), a0 = 1 + alpha;
            return new Biquad { _b0 = alpha / a0, _b1 = 0, _b2 = -alpha / a0, _a1 = -2 * Math.Cos(w) / a0, _a2 = (1 - alpha) / a0 };
        }

        public static Biquad LowPass(double hz, double q = 0.707)
        {
            double w = 2 * Math.PI * hz / SampleRate, alpha = Math.Sin(w) / (2 * q), c = Math.Cos(w), a0 = 1 + alpha;
            return new Biquad { _b0 = (1 - c) / 2 / a0, _b1 = (1 - c) / a0, _b2 = (1 - c) / 2 / a0, _a1 = -2 * c / a0, _a2 = (1 - alpha) / a0 };
        }

        public static Biquad HighPass(double hz, double q = 0.707)
        {
            double w = 2 * Math.PI * hz / SampleRate, alpha = Math.Sin(w) / (2 * q), c = Math.Cos(w), a0 = 1 + alpha;
            return new Biquad { _b0 = (1 + c) / 2 / a0, _b1 = -(1 + c) / a0, _b2 = (1 + c) / 2 / a0, _a1 = -2 * c / a0, _a2 = (1 - alpha) / a0 };
        }

        public double Next(double x)
        {
            double y = _b0 * x + _b1 * _x1 + _b2 * _x2 - _a1 * _y1 - _a2 * _y2;
            _x2 = _x1; _x1 = x; _y2 = _y1; _y1 = y;
            return y;
        }
    }

    /// <summary>Filtered noise with an exponential decay (time constant <paramref name="tau"/>), added at <paramref name="start"/>.</summary>
    private static void Burst(float[] buf, Random rng, double start, double tau, double amp, Biquad filter, double attack = 0.0005)
    {
        int s = At(start), n = Math.Min(buf.Length - s, At(tau * 7));
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double env = Math.Min(1, t / attack) * Math.Exp(-t / tau);
            buf[s + i] += (float)(amp * env * filter.Next(Noise(rng)));
        }
    }

    /// <summary>A damped sine whose pitch glides exponentially from <paramref name="hz"/> to <paramref name="endHz"/>.</summary>
    private static void Tone(float[] buf, double start, double hz, double endHz, double tau, double amp, double attack = 0.001)
    {
        int s = At(start), n = Math.Min(buf.Length - s, At(tau * 7));
        double phase = 0;
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double f = endHz + (hz - endHz) * Math.Exp(-t / (tau * 0.6));
            phase += 2 * Math.PI * f / SampleRate;
            double env = Math.Min(1, t / attack) * Math.Exp(-t / tau);
            buf[s + i] += (float)(amp * env * Math.Sin(phase));
        }
    }

    private static void Normalize(float[] buf)
    {
        float peak = 0;
        foreach (var v in buf) peak = Math.Max(peak, Math.Abs(v));
        if (peak < 1e-6f) return;
        float k = (float)(Peak / peak);
        for (int i = 0; i < buf.Length; i++) buf[i] *= k;
    }

    private static double Vary(Random rng, double value, double spread) => value * (1 + spread * Noise(rng));

    // ------------------------------------------------------------------ sounds

    /// <summary>A shoe on the floor: heel strike, then a softer toe roll-off.</summary>
    private static float[] Step(Random rng, double body, double q, double tau, double click, double thump)
    {
        var buf = Buffer(0.2);
        double toe = Vary(rng, 0.05, 0.25);
        foreach (var (start, amp) in new[] { (0.0, 1.0), (toe, 0.45) })
        {
            Burst(buf, rng, start, Vary(rng, tau, 0.2), amp, Biquad.BandPass(Vary(rng, body, 0.12), q));
            if (click > 0) Burst(buf, rng, start, 0.0018, click * amp, Biquad.HighPass(3500));
            Tone(buf, start, Vary(rng, 140, 0.1), 90, 0.02, thump * amp);
        }
        return buf;
    }

    private static float[] Gunshot(Random rng)
    {
        var buf = Buffer(1.6);
        Burst(buf, rng, 0, 0.004, 1.0, Biquad.HighPass(800));
        Burst(buf, rng, 0, 0.05, 0.9, Biquad.LowPass(2200));
        Tone(buf, 0, 110, 42, 0.16, 0.9);
        // the shot rolling off the walls
        Burst(buf, rng, 0.012, 0.4, 0.5, Biquad.LowPass(700), attack: 0.01);
        Burst(buf, rng, 0.17, 0.05, 0.28, Biquad.LowPass(1400));
        Burst(buf, rng, 0.31, 0.06, 0.14, Biquad.LowPass(900));
        return buf;
    }

    private static float[] Knock(Random rng)
    {
        var buf = Buffer(0.3);
        Burst(buf, rng, 0, 0.002, 0.5, Biquad.HighPass(2000));
        Burst(buf, rng, 0, 0.03, 1.0, Biquad.BandPass(230, 4));
        Tone(buf, 0, 190, 170, 0.045, 0.7);
        Tone(buf, 0, 430, 410, 0.025, 0.35);
        return buf;
    }

    private static float[] Clang(Random rng)
    {
        var buf = Buffer(1.4);
        Burst(buf, rng, 0, 0.003, 0.7, Biquad.HighPass(1500));
        double[] hz = { 430, 1102, 1876, 2690, 3520 }, amp = { 1, 0.6, 0.45, 0.3, 0.2 }, tau = { 0.5, 0.32, 0.22, 0.15, 0.1 };
        for (int k = 0; k < hz.Length; k++)
        {
            Tone(buf, 0, hz[k], hz[k], tau[k], amp[k]);
            Tone(buf, 0, hz[k] * 1.004, hz[k] * 1.004, tau[k], amp[k] * 0.5);
        }
        return buf;
    }

    /// <summary>Trash cans going over: a burst, a run of tinny metal hits, a lid rattling to rest.</summary>
    private static float[] Crash(Random rng)
    {
        var buf = Buffer(1.3);
        Burst(buf, rng, 0, 0.06, 0.8, Biquad.BandPass(1800, 0.7));
        Tone(buf, 0, 110, 70, 0.06, 0.5);
        double t = 0;
        for (int i = 0; i < 9; i++)
        {
            double amp = 0.9 * Math.Pow(0.8, i), basis = 380 + rng.NextDouble() * 500;
            foreach (var (ratio, part) in new[] { (1.0, 1.0), (2.37, 0.6), (3.91, 0.4), (5.6, 0.25) })
                Tone(buf, t, basis * ratio, basis * ratio, 0.08 / Math.Sqrt(ratio), amp * part * 0.5, attack: 0.0004);
            Burst(buf, rng, t, 0.004, amp * 0.5, Biquad.HighPass(2500));
            t += 0.03 + rng.NextDouble() * 0.09;
        }
        // the lid spinning down
        for (double gap = 0.09; t < 1.15 && gap > 0.012; gap *= 0.8)
        {
            Tone(buf, t, 1450, 1450, 0.025, 0.18, attack: 0.0004);
            Tone(buf, t, 3380, 3380, 0.015, 0.1, attack: 0.0004);
            t += gap;
        }
        return buf;
    }

    private static float[] Thunk(Random rng)
    {
        var buf = Buffer(0.45);
        Tone(buf, 0, 100, 52, 0.07, 1.0);
        Burst(buf, rng, 0, 0.03, 0.6, Biquad.LowPass(450));
        Burst(buf, rng, 0, 0.004, 0.25, Biquad.BandPass(1500, 1));
        return buf;
    }

    /// <summary>Splintering wood: one big snap, a run of smaller ones.</summary>
    private static float[] Crack(Random rng)
    {
        var buf = Buffer(0.6);
        Burst(buf, rng, 0, 0.004, 1.0, Biquad.HighPass(1200));
        Burst(buf, rng, 0, 0.02, 0.7, Biquad.BandPass(800, 1.5));
        Tone(buf, 0, 120, 70, 0.05, 0.4);
        double t = 0.02;
        for (int i = 0; i < 12; i++)
        {
            t += 0.005 + rng.NextDouble() * 0.02;
            double amp = 0.6 * (1 - i / 14.0);
            Burst(buf, rng, t, 0.003, amp, Biquad.HighPass(1500));
            Burst(buf, rng, t, 0.008, amp * 0.6, Biquad.BandPass(Vary(rng, 900, 0.3), 2));
        }
        return buf;
    }

    /// <summary>Sound shaped by a slowly wandering, always-positive amplitude (fabric, scraping).</summary>
    private static float[] Textured(Random rng, double seconds, Biquad tone, double wobbleHz, double grain, double amp)
    {
        var buf = Buffer(seconds);
        var wobble = Biquad.LowPass(wobbleHz);
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / buf.Length;
            double env = Math.Sin(Math.PI * t);
            double mod = Math.Clamp(0.4 + grain * wobble.Next(Noise(rng)), 0, 1.5);
            buf[i] = (float)(amp * env * mod * tone.Next(Noise(rng)));
        }
        return buf;
    }

    private static float[] Rustle(Random rng) => Textured(rng, 0.8, Biquad.BandPass(3200, 0.7), 14, 12, 1);

    private static float[] Scrape(Random rng)
    {
        var buf = Textured(rng, 1.1, Biquad.BandPass(1100, 2.5), 28, 16, 1);
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / SampleRate;
            buf[i] += (float)(0.06 * Math.Sin(Math.PI * i / buf.Length) * Math.Sin(2 * Math.PI * (650 + 40 * Math.Sin(t * 9)) * t));
        }
        return buf;
    }

    private static float[] Click(Random rng)
    {
        var buf = Buffer(0.15);
        foreach (var (start, amp) in new[] { (0.0, 1.0), (0.04, 0.7) })
        {
            Burst(buf, rng, start, 0.0015, amp, Biquad.HighPass(2500));
            Tone(buf, start, 3200, 3100, 0.005, amp * 0.6, attack: 0.0002);
        }
        return buf;
    }

    private static float[] Explosion(Random rng)
    {
        var buf = Buffer(3.2);
        Tone(buf, 0, 70, 28, 0.45, 1.0, attack: 0.004);
        Burst(buf, rng, 0, 0.75, 1.3, Biquad.LowPass(320), attack: 0.01);
        Burst(buf, rng, 0, 0.12, 0.8, Biquad.LowPass(2500), attack: 0.002);
        for (int i = 0; i < 70; i++)
        {
            double start = 0.05 + Math.Pow(rng.NextDouble(), 1.6) * 2.4;
            Burst(buf, rng, start, 0.003 + rng.NextDouble() * 0.006, 0.15 + 0.3 * rng.NextDouble() * (1 - start / 2.6),
                Biquad.BandPass(800 + rng.NextDouble() * 2500, 1.2));
        }
        return buf;
    }

    /// <summary>Gas escaping a cock.</summary>
    private static float[] Hiss(Random rng)
    {
        var buf = Buffer(1.7);
        var hp = Biquad.HighPass(3000);
        var lp = Biquad.LowPass(9000);
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / SampleRate;
            double env = Math.Min(1, t / 0.12) * Math.Min(1, (1.7 - t) / 0.45);
            buf[i] = (float)(env * (0.9 + 0.1 * Math.Sin(t * 23)) * lp.Next(hp.Next(Noise(rng))));
        }
        return buf;
    }

    /// <summary>A heavy car door: the panel's thump, the latch, a rattle of trim.</summary>
    private static float[] DoorSlam(Random rng)
    {
        var buf = Buffer(0.7);
        Tone(buf, 0, 85, 55, 0.09, 1.0, attack: 0.002);
        Burst(buf, rng, 0, 0.05, 0.8, Biquad.LowPass(800));
        Tone(buf, 0.015, 1800, 1780, 0.02, 0.25);
        Tone(buf, 0.015, 2650, 2620, 0.015, 0.2);
        Burst(buf, rng, 0.015, 0.002, 0.4, Biquad.HighPass(3000));
        Burst(buf, rng, 0.06, 0.04, 0.12, Biquad.BandPass(1300, 3));
        return buf;
    }

    /// <summary>An electric doorbell: a striker rattling against a gong for a second.</summary>
    private static float[] Bell(Random rng)
    {
        var buf = Buffer(1.8);
        double[] hz = { 1180, 2960, 4120 }, amp = { 1, 0.45, 0.25 };
        double t = 0;
        while (t < 0.9)
        {
            for (int k = 0; k < hz.Length; k++) Tone(buf, t, hz[k], hz[k], 0.3 / (k + 1), amp[k] * 0.35, attack: 0.0005);
            Burst(buf, rng, t, 0.002, 0.08, Biquad.HighPass(3000));
            t += 1 / Vary(rng, 19, 0.04);
        }
        return buf;
    }

    /// <summary>Steady rain with scattered drops, crossfaded onto itself so it loops without a seam.</summary>
    private static float[] Rain(Random rng)
    {
        int length = At(RainLoopSeconds), fade = At(0.5);
        var raw = new float[length + fade];
        var hp = Biquad.HighPass(350);
        var lp = Biquad.LowPass(2600);
        var wander = Biquad.LowPass(0.6);
        for (int i = 0; i < raw.Length; i++)
            raw[i] = (float)(0.3 * (0.85 + 0.6 * wander.Next(Noise(rng))) * lp.Next(hp.Next(Noise(rng))));
        int drops = (int)(raw.Length / (double)SampleRate * 70);
        for (int i = 0; i < drops; i++)
        {
            double start = rng.NextDouble() * (raw.Length - At(0.05)) / SampleRate;
            Burst(raw, rng, start, 0.002 + rng.NextDouble() * 0.004, 0.04 + rng.NextDouble() * 0.16,
                Biquad.BandPass(1800 + rng.NextDouble() * 3500, 1.5));
        }
        var buf = new float[length];
        Array.Copy(raw, buf, length);
        for (int i = 0; i < fade; i++)
        {
            double x = (double)i / fade;
            buf[i] = (float)(raw[i] * Math.Sqrt(x) + raw[length + i] * Math.Sqrt(1 - x));
        }
        return buf;
    }
}
