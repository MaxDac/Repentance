using System;

namespace Repentance;

/// <summary>The recipe for each <see cref="Sound"/>, built from the blocks in SoundSynth.cs.</summary>
public static partial class SoundSynth
{
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

    /// <summary>A small tool tin opened: the padlock's shackle snaps free, a hinge squeaks, the thin enamelled lid
    /// clanks back, and the crowbar inside shifts with a dull rattle.</summary>
    private static float[] TinOpen(Random rng)
    {
        var buf = Buffer(1.1);
        // the padlock: a bright snap and a tiny brass ping
        Burst(buf, rng, 0, 0.0015, 0.7, Biquad.HighPass(3000));
        Tone(buf, 0, 2950, 2900, 0.02, 0.35, attack: 0.0002);
        Tone(buf, 0.035, 4100, 4050, 0.012, 0.2, attack: 0.0002);
        // the hinge, a short dry squeak rising in pitch
        int h0 = At(0.12), hn = At(0.16);
        double phase = 0;
        var grit = Biquad.BandPass(1800, 3);
        for (int i = 0; i < hn; i++)
        {
            double t = (double)i / hn;
            phase += 2 * Math.PI * (850 + 600 * t + 40 * Math.Sin(t * 60)) / SampleRate;
            double env = Math.Sin(Math.PI * t);
            buf[h0 + i] += (float)(env * (0.1 * Math.Sin(phase) + 0.08 * grit.Next(Noise(rng))));
        }
        // the lid clanking back: thin sheet steel, inharmonic and quick to die
        double lid = 0.3;
        Burst(buf, rng, lid, 0.003, 0.6, Biquad.HighPass(1800));
        double[] hz = { 610, 1490, 2560, 3870 }, amp = { 0.7, 0.55, 0.4, 0.25 }, tau = { 0.16, 0.1, 0.07, 0.05 };
        for (int k = 0; k < hz.Length; k++)
        {
            Tone(buf, lid, hz[k], hz[k], tau[k], amp[k], attack: 0.0004);
            Tone(buf, lid, hz[k] * 1.013, hz[k] * 1.013, tau[k], amp[k] * 0.4, attack: 0.0004);
        }
        // a smaller bounce, and the crowbar shifting against the tin
        Tone(buf, lid + 0.07, 1490, 1490, 0.04, 0.2, attack: 0.0004);
        foreach (var (at, a) in new[] { (0.46, 0.45), (0.53, 0.25) })
        {
            Tone(buf, at, 340, 320, 0.05, a, attack: 0.0006);
            Tone(buf, at, 1150, 1150, 0.03, a * 0.4, attack: 0.0004);
            Burst(buf, rng, at, 0.006, a * 0.4, Biquad.BandPass(900, 1.5));
        }
        return buf;
    }

    /// <summary>Spirits catching all at once: a soft thump of air, a roar that swells and settles, crackling.</summary>
    private static float[] Whoosh(Random rng)
    {
        var buf = Buffer(2.6);
        Tone(buf, 0, 55, 35, 0.3, 0.5, attack: 0.03);
        var lp = Biquad.LowPass(900);
        var bp = Biquad.BandPass(1600, 0.8);
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / SampleRate;
            double swell = Math.Min(1, t / 0.22);
            double env = swell * swell * (0.35 + 0.65 * Math.Exp(-Math.Max(0, t - 0.22) * 1.6)) * Math.Clamp((2.6 - t) / 0.8, 0, 1);
            double n = Noise(rng);
            buf[i] += (float)(env * (lp.Next(n) + 0.35 * swell * bp.Next(n)));
        }
        for (int i = 0; i < 40; i++)
        {
            double start = 0.15 + rng.NextDouble() * 2.0;
            Burst(buf, rng, start, 0.002 + rng.NextDouble() * 0.004, 0.1 + 0.2 * rng.NextDouble() * (1 - start / 2.4),
                Biquad.BandPass(1500 + rng.NextDouble() * 2500, 1.5));
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

    /// <summary>A room door opening: the knob turns, the latch clicks free, the hinges creak as it swings.</summary>
    private static float[] DoorOpen(Random rng)
    {
        var buf = Buffer(0.9);
        Burst(buf, rng, 0, 0.012, 0.25, Biquad.BandPass(1400, 2));
        Burst(buf, rng, 0.07, 0.0015, 0.7, Biquad.HighPass(2500));
        Tone(buf, 0.07, 2300, 2250, 0.008, 0.35, attack: 0.0002);
        Tone(buf, 0.07, 160, 130, 0.02, 0.3);
        // the hinge: a rubbing squeak whose pitch wanders, swelling and fading
        int s = At(0.14), n = At(0.65);
        var wobble = Biquad.LowPass(18);
        var body = Biquad.BandPass(900, 3);
        double phase = 0;
        for (int i = 0; i < n && s + i < buf.Length; i++)
        {
            double t = (double)i / n;
            double env = Math.Sin(Math.PI * t) * Math.Sin(Math.PI * t);
            double hz = 520 + 140 * t + 25 * Math.Sin(2 * Math.PI * 5 * t);
            phase += 2 * Math.PI * hz / SampleRate;
            double grain = Math.Clamp(0.6 + 8 * wobble.Next(Noise(rng)), 0.1, 1.3);
            double squeak = Math.Sin(phase) + 0.4 * Math.Sin(2 * phase) + 0.2 * Math.Sin(3 * phase);
            buf[s + i] += (float)(0.22 * env * grain * squeak + 0.12 * env * body.Next(Noise(rng)));
        }
        return buf;
    }

    /// <summary>A room door shutting: the wooden thud against the frame, then the latch catching.</summary>
    private static float[] DoorClose(Random rng)
    {
        var buf = Buffer(0.5);
        Burst(buf, rng, 0, 0.015, 0.2, Biquad.BandPass(700, 1), attack: 0.004);
        Tone(buf, 0.02, 120, 75, 0.06, 1.0, attack: 0.002);
        Burst(buf, rng, 0.02, 0.035, 0.7, Biquad.BandPass(260, 2));
        Tone(buf, 0.02, 340, 320, 0.03, 0.25);
        Burst(buf, rng, 0.045, 0.0015, 0.45, Biquad.HighPass(2800));
        Tone(buf, 0.045, 2100, 2060, 0.008, 0.25, attack: 0.0002);
        return buf;
    }

    /// <summary>A two-tone door chime: a hammer strikes a high bar ("ding"), then a lower one a major third down ("dong").</summary>
    private static float[] Bell(Random rng)
    {
        var buf = Buffer(2.6);
        Chime(buf, rng, 0, 659.3, 1.0);
        Chime(buf, rng, 0.55, 523.3, 1.1);
        return buf;
    }

    /// <summary>One struck tone bar: a ringing fundamental, a few fading partials and the soft tap of the felt hammer.</summary>
    private static void Chime(float[] buf, Random rng, double start, double hz, double amp)
    {
        double[] ratio = { 1, 2.0, 3.0, 4.16 }, level = { 1, 0.3, 0.12, 0.06 }, tau = { 0.38, 0.2, 0.1, 0.05 };
        for (int k = 0; k < ratio.Length; k++)
            Tone(buf, start, hz * ratio[k], hz * ratio[k], tau[k], amp * level[k] * 0.5, attack: 0.003);
        Burst(buf, rng, start, 0.006, amp * 0.05, Biquad.BandPass(hz * 2, 2));
    }

    /// <summary>
    /// A storm overhead: the sharp crack of the strike, then a long low rumble that rolls in waves and dies away.
    /// </summary>
    private static float[] Thunder(Random rng)
    {
        const double seconds = 4.2;
        var buf = Buffer(seconds);
        Burst(buf, rng, 0, 0.012, 0.7, Biquad.HighPass(900));
        Burst(buf, rng, 0.004, 0.09, 0.8, Biquad.LowPass(1600));
        Tone(buf, 0, 70, 38, 0.6, 0.6, attack: 0.01);
        var lp = Biquad.LowPass(220);
        var lp2 = Biquad.LowPass(220);
        var rolls = Biquad.LowPass(2.2);
        double brown = 0;
        for (int i = 0; i < buf.Length; i++)
        {
            double t = (double)i / SampleRate;
            brown = Math.Clamp(brown * 0.995 + 0.08 * Noise(rng), -1, 1);
            double roll = Math.Clamp(0.55 + 9 * rolls.Next(Noise(rng)), 0.15, 1.4);
            double env = Math.Min(1, t / 0.08) * Math.Exp(-t / 1.3) * Math.Clamp((seconds - t) / 0.6, 0, 1);
            buf[i] += (float)(1.6 * env * roll * lp2.Next(lp.Next(brown)));
        }
        for (int i = 0; i < 6; i++)
        {
            double start = 0.15 + rng.NextDouble() * 1.6;
            Burst(buf, rng, start, 0.05 + rng.NextDouble() * 0.12, 0.25 * (1 - start / 2.2), Biquad.LowPass(500));
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
