using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace Repentance;

public enum Sound
{
    StepWood, StepStone, StepCarpet,
    Gunshot, Knock, Clang, Crash, Thunk, Crack, Rustle, Click, Scrape, Whoosh, DoorSlam, DoorOpen, DoorClose, Bell,
    Rain, Thunder,
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
public static partial class SoundSynth
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
        Sound.Rustle or Sound.Click => -6f,
        Sound.DoorOpen or Sound.DoorClose => -8f,
        Sound.Rain => -14f,
        Sound.Gunshot or Sound.Whoosh or Sound.Thunder => 0f,
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
            Sound.Whoosh => Whoosh(rng),
            Sound.DoorSlam => DoorSlam(rng),
            Sound.DoorOpen => DoorOpen(rng),
            Sound.DoorClose => DoorClose(rng),
            Sound.Bell => Bell(rng),
            Sound.Rain => Rain(rng),
            Sound.Thunder => Thunder(rng),
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
        (new(@"\b(?:fw|wh|fwh)o{2,}sh\b"), Sound.Whoosh),
        (new(@"\bring\b"), Sound.Bell),
        (new(@"\bthunder\b"), Sound.Thunder),
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

    /// <summary>RBJ biquad: band-pass (constant peak gain), low/high-pass or peaking EQ.</summary>
    internal struct Biquad
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

        public static Biquad Peaking(double hz, double gainDb, double q)
        {
            double w = 2 * Math.PI * hz / SampleRate, alpha = Math.Sin(w) / (2 * q), c = Math.Cos(w), a = Math.Pow(10, gainDb / 40);
            double a0 = 1 + alpha / a;
            return new Biquad { _b0 = (1 + alpha * a) / a0, _b1 = -2 * c / a0, _b2 = (1 - alpha * a) / a0, _a1 = -2 * c / a0, _a2 = (1 - alpha / a) / a0 };
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
}
