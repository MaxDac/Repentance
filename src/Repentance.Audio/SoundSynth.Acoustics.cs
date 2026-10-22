using System;

namespace Repentance;

/// <summary>Physical building blocks for loud sounds: shock-wave pulses, overdriven microphones and rooms.</summary>
public static partial class SoundSynth
{
    // Freeverb's comb and all-pass lengths at 44.1 kHz; mutually prime-ish so the echoes smear instead of fluttering
    private static readonly int[] ReverbCombs = { 1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617 };
    private static readonly int[] ReverbAllPasses = { 556, 441, 341, 225 };

    /// <summary>
    /// A shock wave's N-shaped pressure pulse: an instant rise, a straight fall through zero, an instant return. Every
    /// supersonic bang, from a muzzle to a lightning channel, reaches the ear as one of these.
    /// </summary>
    private static void NWave(float[] buf, double start, double length, double amp)
    {
        int s = At(start), n = Math.Max(2, At(length));
        for (int i = 0; i < n && s + i < buf.Length; i++) buf[s + i] += (float)(amp * (1 - 2.0 * i / (n - 1)));
    }

    /// <summary>
    /// Scales to full level and drives through a tanh curve, the way a bang too loud for the microphone comes out
    /// dense and flat-topped. <paramref name="drive"/> 1 is nearly clean; 4 is heavily squashed.
    /// </summary>
    private static void Saturate(float[] buf, double drive)
    {
        float peak = 0;
        foreach (var v in buf) peak = Math.Max(peak, Math.Abs(v));
        if (peak < 1e-6f) return;
        double norm = Math.Tanh(drive);
        for (int i = 0; i < buf.Length; i++) buf[i] = (float)(Math.Tanh(drive * buf[i] / peak) / norm);
    }

    /// <summary>
    /// Copies of the sound off nearby walls, floor and ceiling, each later one quieter and duller; returns a buffer
    /// <paramref name="extra"/> seconds longer.
    /// </summary>
    private static float[] Reflections(float[] dry, (double Delay, double Level)[] taps, double extra)
    {
        var wet = new float[dry.Length + At(extra)];
        Array.Copy(dry, wet, dry.Length);
        double last = taps[^1].Delay;
        foreach (var (delay, level) in taps)
        {
            var lp = Biquad.LowPass(5000 - 3500 * delay / last);
            int s = At(delay), n = Math.Min(dry.Length, wet.Length - s);
            for (int i = 0; i < n; i++) wet[s + i] += (float)(level * lp.Next(dry[i]));
        }
        return wet;
    }

    /// <summary>
    /// A diffuse room tail (Schroeder/Freeverb: damped combs in parallel into all-passes in series) mixed under the dry
    /// sound. <paramref name="rt60"/> is how long it takes to die by 60 dB, <paramref name="size"/> scales the room,
    /// <paramref name="damping"/> (0-1) how fast the highs die before the lows. Returns a buffer
    /// <paramref name="tail"/> seconds longer.
    /// </summary>
    private static float[] Reverb(float[] dry, double rt60, double size, double damping, double mix, double tail)
    {
        var output = new float[dry.Length + At(tail)];
        var wet = new double[output.Length];
        foreach (int comb in ReverbCombs)
        {
            int len = Math.Max(1, (int)(comb * size * SampleRate / 44100.0));
            double feedback = Math.Pow(10, -3.0 * len / SampleRate / rt60), lp = 0;
            var line = new double[len];
            for (int i = 0, p = 0; i < output.Length; i++, p = (p + 1) % len)
            {
                double y = line[p];
                lp = y * (1 - damping) + lp * damping;
                line[p] = (i < dry.Length ? dry[i] : 0) + feedback * lp;
                wet[i] += y;
            }
        }
        foreach (int allPass in ReverbAllPasses)
        {
            int len = Math.Max(1, (int)(allPass * size * SampleRate / 44100.0));
            var line = new double[len];
            for (int i = 0, p = 0; i < output.Length; i++, p = (p + 1) % len)
            {
                double b = line[p], x = wet[i];
                line[p] = x + 0.5 * b;
                wet[i] = b - x;
            }
        }
        for (int i = 0; i < output.Length; i++)
            output[i] = (float)((i < dry.Length ? dry[i] : 0) + mix * wet[i] / ReverbCombs.Length);
        return output;
    }
}
