using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>The recipe for each <see cref="Sound"/>, built from the blocks in SoundSynth.cs.</summary>
public static partial class SoundSynth
{
    /// <summary>
    /// How a floor answers a shoe: its resonance, how bright the heel click stays, how much it booms, and how much
    /// of the step comes back off the walls of a hard hall.
    /// </summary>
    private readonly record struct FloorResponse(
        double BodyHz, double BodyQ, double BodyTau, double Click, double Thump, double Muffle, double Echo = 0);

    private static readonly FloorResponse Boards = new(BodyHz: 480, BodyQ: 2.2, BodyTau: 0.022, Click: 1.0, Thump: 0.35, Muffle: 0);
    private static readonly FloorResponse Cobbles = new(BodyHz: 1700, BodyQ: 0.7, BodyTau: 0.007, Click: 1.1, Thump: 0.1, Muffle: 0);
    private static readonly FloorResponse Rug = new(BodyHz: 280, BodyQ: 0.9, BodyTau: 0.016, Click: 0.7, Thump: 0.25, Muffle: 1400);
    private static readonly FloorResponse Marble = new(BodyHz: 1000, BodyQ: 0.8, BodyTau: 0.012, Click: 0.95, Thump: 0.15, Muffle: 0, Echo: 0.42);

    /// <summary>Delays (s) and levels of the reflections a marble hall sends back; irregular so they smear, not flutter.</summary>
    private static readonly (double Delay, double Level)[] HallTaps =
        { (0.047, 1.0), (0.071, 0.8), (0.103, 0.62), (0.131, 0.5), (0.173, 0.36), (0.229, 0.24), (0.29, 0.14) };

    /// <summary>
    /// A 1920s leather dress shoe: the hard stacked heel strikes with a sharp click, the floor answers, then the
    /// leather sole pats down a moment later. A rug muffles the whole step but leaves the heel distinct; a marble
    /// hall sends it back softly off the walls.
    /// </summary>
    private static float[] Step(Random rng, FloorResponse floor)
    {
        var buf = Buffer(0.2);
        double click = floor.Click, pitch = Vary(rng, 1, 0.06);

        // heel: a bright crack and the knock of the hard heel block - wide noise bands, never a pitched ring,
        // which would sound like metal
        Burst(buf, rng, 0, 0.0012, 0.9 * click, Biquad.HighPass(3000), attack: 0.0001);
        Burst(buf, rng, 0, Vary(rng, 0.005, 0.15), 0.7 * click, Biquad.BandPass(2600 * pitch, 0.6), attack: 0.0001);
        Burst(buf, rng, 0, Vary(rng, 0.008, 0.15), 0.8 * click, Biquad.BandPass(1100 * pitch, 0.7), attack: 0.0002);
        Burst(buf, rng, 0, Vary(rng, floor.BodyTau, 0.2), 0.6, Biquad.BandPass(Vary(rng, floor.BodyHz, 0.1), floor.BodyQ));
        Tone(buf, 0, Vary(rng, 150, 0.1), 95, 0.018, floor.Thump);

        // sole: the flat leather slapping down, softer and duller, no click
        double sole = Vary(rng, 0.075, 0.3), level = Vary(rng, 0.42, 0.15);
        Burst(buf, rng, sole, 0.006, level, Biquad.BandPass(Vary(rng, 1300, 0.15), 0.8), attack: 0.0004);
        Burst(buf, rng, sole, 0.002, level * 0.45 * click, Biquad.HighPass(2000), attack: 0.0003);
        Burst(buf, rng, sole, Vary(rng, floor.BodyTau, 0.2) * 0.7, level * 0.6,
            Biquad.BandPass(Vary(rng, floor.BodyHz, 0.1), floor.BodyQ));
        Tone(buf, sole, Vary(rng, 120, 0.1), 85, 0.012, floor.Thump * level);

        if (floor.Muffle > 0)
        {
            var lp = Biquad.LowPass(floor.Muffle);
            var lp2 = Biquad.LowPass(floor.Muffle * 1.6);
            for (int i = 0; i < buf.Length; i++) buf[i] = (float)lp2.Next(lp.Next(buf[i]));
        }
        FadeTail(buf, 0.03);
        return floor.Echo > 0 ? Hall(buf, floor.Echo) : buf;
    }

    /// <summary>The dry step plus its reflections off a hard hall, each duller than the one before.</summary>
    private static float[] Hall(float[] dry, double echo)
    {
        var wet = Buffer(0.55);
        Array.Copy(dry, wet, dry.Length);
        foreach (var (delay, level) in HallTaps)
        {
            var lp = Biquad.LowPass(3200 - 1600 * delay / HallTaps[^1].Delay);
            int s = At(delay), n = Math.Min(dry.Length, wet.Length - s);
            for (int i = 0; i < n; i++) wet[s + i] += (float)(echo * level * lp.Next(dry[i]));
        }
        FadeTail(wet, 0.05);
        return wet;
    }

    private static void FadeTail(float[] buf, double seconds)
    {
        int n = Math.Min(buf.Length, At(seconds));
        for (int i = 0; i < n; i++) buf[buf.Length - 1 - i] *= (float)i / n;
    }

    /// <summary>Walls, floor, ceiling and furniture of a bedroom-sized room: the first copies of a shot, 3-35 ms late.</summary>
    private static readonly (double Delay, double Level)[] RoomTaps =
        { (0.0031, 0.4), (0.0058, 0.34), (0.0087, 0.28), (0.0123, 0.23), (0.0161, 0.19), (0.0207, 0.15), (0.0266, 0.11), (0.0342, 0.08) };

    /// <summary>
    /// A revolver fired indoors: the hammer falls, the muzzle blast arrives as a shock wave (N-wave plus a crack of
    /// broadband noise) over a low thump, all too loud for the microphone, then the room's walls answer at once and
    /// ring on in a dark, diffuse tail.
    /// </summary>
    private static float[] Gunshot(Random rng)
    {
        const double shot = 0.01;
        var blast = Buffer(0.25);
        NWave(blast, shot, 0.0016, 1.0);
        Burst(blast, rng, shot, 0.0025, 0.9, Biquad.HighPass(2000));
        Burst(blast, rng, shot, 0.012, 1.1, Biquad.BandPass(800, 0.6));
        // the blast's low body, noise rather than a pitched glide
        var body = Buffer(0.25);
        Burst(body, rng, shot, 0.02, 1, Biquad.LowPass(180, 0.9), attack: 0.0006);
        Burst(body, rng, shot, 0.04, 0.5, Biquad.LowPass(90), attack: 0.002);
        Normalize(body);
        for (int i = 0; i < blast.Length; i++) blast[i] += 0.9f * body[i];
        Saturate(blast, 2.5);
        // the hammer, before the powder: too quiet to be squashed
        var hammer = Buffer(0.25);
        Burst(hammer, rng, 0, 0.0008, 0.09, Biquad.BandPass(3600, 2.5));
        Burst(hammer, rng, 0.0004, 0.002, 0.05, Biquad.BandPass(1900, 3));
        for (int i = 0; i < blast.Length; i++) blast[i] += hammer[i];

        var room = Reflections(blast, RoomTaps, 0.04);
        var buf = Reverb(room, rt60: 0.85, size: 0.9, damping: 0.5, mix: 0.22, tail: 1.3);
        FadeTail(buf, 0.2);
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

    /// <summary>
    /// A wall safe cracked: the dial ratcheting round, a tumbler dropping at each number, the handle drawing the bolts
    /// back, then the heavy door groaning open on its hinge.
    /// </summary>
    private static float[] SafeOpen(Random rng)
    {
        var buf = Buffer(1.8);
        double t = 0;
        foreach (int ticks in new[] { 7, 5, 4 })
        {
            for (int i = 0; i < ticks; i++)
            {
                DialTick(buf, rng, t, 0.3);
                t += Vary(rng, 0.032, 0.15);
            }
            Tumbler(buf, rng, t, 0.6);
            t += 0.09;
        }
        // the handle: the bolts sliding back in their keepers, ending on a clack
        Slide(buf, rng, t, 0.16, 0.35);
        t += 0.16;
        Tone(buf, t, 240, 200, 0.03, 0.5);
        Burst(buf, rng, t, 0.003, 0.45, Biquad.HighPass(2400));
        // the hinge: a low steel groan swelling and dying as the weight swings out
        Groan(buf, rng, t + 0.1, 0.75, 150, 0.32);
        return buf;
    }

    /// <summary>
    /// A wall safe locked: the heavy door shutting with a dull ring, the handle throwing the bolts, then the dial
    /// spun hard so its ticks run fast and slow to a stop.
    /// </summary>
    private static float[] SafeClose(Random rng)
    {
        var buf = Buffer(1.6);
        Groan(buf, rng, 0, 0.3, 175, 0.18);
        double t = 0.26;
        Tone(buf, t, 80, 48, 0.09, 1.0, attack: 0.002);
        Burst(buf, rng, t, 0.04, 0.6, Biquad.LowPass(600));
        Tone(buf, t, 640, 632, 0.12, 0.16);
        Tone(buf, t, 1470, 1462, 0.07, 0.09);
        Burst(buf, rng, t, 0.002, 0.35, Biquad.HighPass(2600));
        t += 0.28;
        Slide(buf, rng, t, 0.13, 0.3);
        t += 0.13;
        Tone(buf, t, 260, 210, 0.03, 0.55);
        Burst(buf, rng, t, 0.003, 0.5, Biquad.HighPass(2400));
        t += 0.14;
        for (double gap = 0.016; t < 1.5; gap *= 1.13)
        {
            DialTick(buf, rng, t, 0.28 * Math.Clamp((1.5 - t) / 0.5, 0.2, 1));
            t += gap;
        }
        return buf;
    }

    /// <summary>One click of a combination dial's ratchet.</summary>
    private static void DialTick(float[] buf, Random rng, double start, double amp)
    {
        Burst(buf, rng, start, 0.0012, amp, Biquad.HighPass(3000), attack: 0.0002);
        Tone(buf, start, Vary(rng, 2700, 0.05), 2650, 0.004, amp * 0.5, attack: 0.0002);
    }

    /// <summary>A tumbler wheel falling into place behind the dial: a small, deeper clunk.</summary>
    private static void Tumbler(float[] buf, Random rng, double start, double amp)
    {
        Tone(buf, start, 420, 360, 0.018, amp);
        Burst(buf, rng, start, 0.006, amp * 0.6, Biquad.BandPass(1200, 2));
    }

    /// <summary>Steel bolts sliding in their keepers.</summary>
    private static void Slide(float[] buf, Random rng, double start, double seconds, double amp)
    {
        int s = At(start), n = At(seconds);
        var tone = Biquad.BandPass(2100, 3);
        for (int i = 0; i < n && s + i < buf.Length; i++)
        {
            double env = Math.Sin(Math.PI * i / n);
            buf[s + i] += (float)(amp * env * tone.Next(Noise(rng)));
        }
    }

    /// <summary>A heavy hinge turning: a low rubbing groan whose pitch wanders, swelling and fading to nothing.</summary>
    private static void Groan(float[] buf, Random rng, double start, double seconds, double hz, double amp)
    {
        int s = At(start), n = At(seconds);
        var wobble = Biquad.LowPass(12);
        var body = Biquad.BandPass(hz * 3, 2);
        double phase = 0;
        for (int i = 0; i < n && s + i < buf.Length; i++)
        {
            double t = (double)i / n;
            double env = Math.Sin(Math.PI * t) * Math.Sin(Math.PI * t);
            phase += 2 * Math.PI * (hz * (1 + 0.15 * t) + 8 * Math.Sin(2 * Math.PI * 3 * t)) / SampleRate;
            double grain = Math.Clamp(0.6 + 8 * wobble.Next(Noise(rng)), 0.1, 1.3);
            double rub = Math.Sin(phase) + 0.5 * Math.Sin(2 * phase) + 0.3 * Math.Sin(3 * phase);
            buf[s + i] += (float)(amp * env * (grain * rub + 0.5 * body.Next(Noise(rng))));
        }
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
    /// A strike a few hundred metres away, heard through a window. The lightning channel is a tortuous path from the
    /// ground up into the cloud and across it; every few metres of it bangs at once, and each bang (an N-wave) reaches
    /// the ear later, quieter, longer and duller the further away it is. The near channel arrives as a ripping crack,
    /// stretches of the path at the same distance swell into rolls, and the far cloud is a low rumble that dies away.
    /// </summary>
    private static float[] Thunder(Random rng)
    {
        const double seconds = 4.5, speedOfSound = 343, step = 2.5;
        var channel = new List<(double X, double Y, double Z)>();
        (double X, double Y, double Z) p = (140, 30, 0), drift = (0, 0, 0);
        (double, double, double)[] waypoints = { (170, -40, 650), (520, 260, 760), (980, 120, 820) };
        foreach (var (wx, wy, wz) in waypoints)
            while (channel.Count < 5000)
            {
                double dx = wx - p.X, dy = wy - p.Y, dz = wz - p.Z, left = Math.Sqrt(dx * dx + dy * dy + dz * dz);
                if (left < step * 2) break;
                // smoothed jitter keeps the kinks a few tens of metres long, like a real channel
                drift = (0.9 * drift.X + 0.45 * Noise(rng), 0.9 * drift.Y + 0.45 * Noise(rng), 0.9 * drift.Z + 0.45 * Noise(rng));
                double ux = dx / left + drift.X, uy = dy / left + drift.Y, uz = dz / left + drift.Z;
                double norm = Math.Sqrt(ux * ux + uy * uy + uz * uz);
                p = (p.X + step * ux / norm, p.Y + step * uy / norm, p.Z + step * uz / norm);
                channel.Add(p);
            }

        double nearest = double.MaxValue;
        foreach (var (x, y, z) in channel) nearest = Math.Min(nearest, Math.Sqrt(x * x + y * y + z * z));
        // the further the bang, the more of its highs the air has eaten: one band per distance
        double[] bandEdges = { 260, 450, 750, double.MaxValue };
        double[] bandCutoffs = { 6000, 2400, 1000, 420 };
        var bands = new float[bandEdges.Length][];
        for (int b = 0; b < bands.Length; b++) bands[b] = Buffer(seconds);
        var density = new double[At(seconds)];
        const double start = 0.015;
        for (int k = 0; k < channel.Count; k++)
        {
            var (x, y, z) = channel[k];
            double d = Math.Sqrt(x * x + y * y + z * z), t = start + (d - nearest) / speedOfSound;
            if (t >= seconds - 0.05) continue;
            // spreading and the air both take their share; the channel thins out into branches at the far end
            double fade = Math.Min(1, 4.0 * (channel.Count - k) / channel.Count);
            double amp = Math.Pow(nearest / d, 1.6) * fade * Vary(rng, 1, 0.5);
            double length = Vary(rng, 0.0015 + 0.02 * (d - nearest) / 800, 0.35);
            int band = Array.FindIndex(bandEdges, edge => d < edge);
            NWave(bands[band], t, length, amp);
            density[At(t)] += amp;
        }

        var buf = Buffer(seconds);
        for (int b = 0; b < bands.Length; b++)
        {
            var lp = Biquad.LowPass(bandCutoffs[b]);
            for (int i = 0; i < buf.Length; i++) buf[i] += (float)lp.Next(bands[b][i]);
        }
        Saturate(buf, 1.8);

        // the air itself shaking: deep rumble that swells and fades with how much of the channel is arriving
        var swell = Biquad.LowPass(3);
        var deep = Biquad.LowPass(110);
        var deeper = Biquad.LowPass(110);
        double brown = 0, peakEnv = 0;
        var env = new double[buf.Length];
        for (int i = 0; i < buf.Length; i++) peakEnv = Math.Max(peakEnv, env[i] = Math.Max(0, swell.Next(density[i])));
        var rumble = Buffer(seconds);
        for (int i = 0; i < buf.Length; i++)
        {
            brown = Math.Clamp(brown * 0.997 + 0.06 * Noise(rng), -1, 1);
            rumble[i] = (float)(Math.Sqrt(env[i] / peakEnv) * deeper.Next(deep.Next(brown)));
        }
        Normalize(rumble);
        // through the glass and into the room
        var window = Biquad.LowPass(3800);
        var glass = Biquad.Peaking(140, 3, 0.8);
        for (int i = 0; i < buf.Length; i++) buf[i] = (float)glass.Next(window.Next(0.75 * buf[i] + 0.5 * rumble[i]));

        var room = Reverb(buf, rt60: 0.6, size: 1.1, damping: 0.6, mix: 0.25, tail: 0.3);
        FadeTail(room, 0.8);
        return room;
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
