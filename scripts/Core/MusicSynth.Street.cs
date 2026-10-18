using System;

namespace Repentance;

/// <summary>The street soundscape: the odd motor car driving past, and nothing else.</summary>
public static partial class MusicSynth
{
    private static double White(Random rng) => rng.NextDouble() * 2 - 1;

    private static int Samples(ScoreNote note, double spb) => (int)(note.Beats * spb * SampleRate);

    /// <summary>
    /// A motor car driving past along the street: it comes out of the distance on one side, is loudest and brightest
    /// half way through the note, and fades out on the other side. The engine putters at the note's pitch and drops a
    /// little as the car passes (Doppler), with the tyres hissing on the road under it. <paramref name="direction"/>
    /// is +1 for left to right, -1 for right to left.
    /// </summary>
    private static void Car(float[] left, float[] right, Random rng, ScoreNote note, double spb, double velocity, int direction)
    {
        const double speed = 11, kerb = 7, sound = 343, edge = 2;
        int start = (int)(note.Beat * spb * SampleRate), n = Samples(note, spb);
        double seconds = (double)n / SampleRate, middle = seconds / 2, hz = Hz(note.Midi);
        double phase = 0, firing = 1, tyre = 0, air = 0;
        if (direction == 0) direction = 1;
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double along = speed * (t - middle), distance = Math.Sqrt(along * along + kerb * kerb);
            double near = kerb / distance;
            // moving away lowers the pitch, coming closer raises it
            double receding = speed * along / distance;
            phase += 2 * Math.PI * hz * sound / (sound + receding) / SampleRate;
            if (phase >= 2 * Math.PI)
            {
                phase -= 2 * Math.PI;
                firing = 0.65 + rng.NextDouble() * 0.7;
            }
            double engine = 0;
            for (int k = 1; k <= 10; k++) engine += Math.Sin(k * phase) / Math.Pow(k, 1.1);
            engine += 0.35 * Math.Sin(phase / 2);
            tyre += (White(rng) - tyre) * 0.22;
            double x = 0.45 * firing * engine + 1.4 * tyre;
            // the air takes the top off a car far away
            double cutoff = 350 + 3200 * near * near;
            air += (x - air) * (1 - Math.Exp(-2 * Math.PI * cutoff / SampleRate));
            double fade = Smooth(t / edge) * Smooth((seconds - t) / edge);
            double amp = velocity * near * fade * air;
            double pan = (direction * along / distance * 0.85 + 1) * Math.PI / 4;
            int j = (start + i) % left.Length;
            left[j] += (float)(amp * Math.Cos(pan));
            right[j] += (float)(amp * Math.Sin(pan));
        }
    }
}
