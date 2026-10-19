using System;

namespace Repentance;

public static partial class MusicSynth
{
    private const double SpeedOfSound = 343;

    /// <summary>Instruments that travel across the stereo field while they sound, so they render their own panning.</summary>
    private static bool Moves(Instrument instrument) => instrument is Instrument.Motorcar or Instrument.Streetcar or Instrument.Car;

    /// <summary>
    /// The city's roar for the length of the note: white noise swelling gently, with the colour left to the body
    /// filters. Its swells repeat a whole number of times over the note, so a note as long as the loop has no seam.
    /// </summary>
    private static void Hum(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        int n = (int)Math.Round(note.Beats * spb * SampleRate);
        for (int i = 0; i < n; i++)
        {
            double phase = 2 * Math.PI * i / n;
            double swell = 1 + 0.22 * Math.Sin(3 * phase) + 0.12 * Math.Sin(7 * phase + 1) + 0.06 * Math.Sin(17 * phase + 2);
            buf[(start + i) % buf.Length] += (float)(velocity * 0.5 * swell * (rng.NextDouble() * 2 - 1));
        }
    }

    /// <summary>
    /// Something driving along the street past the listener, from the side <paramref name="pan"/> points at to the
    /// other, closest half way through the note. <paramref name="source"/> makes the sound at the vehicle, given the
    /// time and the Doppler factor on its pitch; it comes out fainter and duller with distance.
    /// </summary>
    private static void Pass(float[] left, float[] right, ScoreNote note, double spb, double velocity, double pan,
        double speed, double near, Func<double, double, double> source)
    {
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        double seconds = note.Beats * spb;
        int n = (int)(seconds * SampleRate);
        double air = 0, fade = Math.Min(1.5, seconds / 4);
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double x = speed * (t - seconds / 2), d = Math.Sqrt(x * x + near * near);
            double doppler = SpeedOfSound / (SpeedOfSound + speed * x / d);
            double edge = Smooth(Math.Min(t, seconds - t) / fade);
            double s = source(t, doppler) * velocity * edge * near / d;
            // the air and the buildings take the top off a far car
            double cutoff = 700 + 7000 * near / d;
            air += (s - air) * (1 - Math.Exp(-2 * Math.PI * cutoff / SampleRate));
            double p = (-pan * x / d * 0.9 + 1) * Math.PI / 4;
            int j = (start + i) % left.Length;
            left[j] += (float)(air * Math.Cos(p));
            right[j] += (float)(air * Math.Sin(p));
        }
    }

    /// <summary>
    /// A motorcar going by on a wet road: the engine's lumpy firing note with its harmonics, the tyres hissing on the
    /// water, a rattle of loose body panels. Accented, it passes close and a little faster.
    /// </summary>
    private static void Motorcar(float[] left, float[] right, Random rng, ScoreNote note, double spb, double velocity, double pan)
    {
        double firing = Hz(note.Midi);
        var harmonics = new double[8];
        for (int k = 0; k < harmonics.Length; k++) harmonics[k] = (0.4 + 0.6 * rng.NextDouble()) / (k + 1);
        var tyres = SoundSynth.Biquad.BandPass(2800, 0.6);
        var rattle = SoundSynth.Biquad.BandPass(950, 2);
        var lumps = SoundSynth.Biquad.LowPass(18);
        var noise = new Random(rng.Next());
        double phase = 0, wobble = rng.NextDouble() * 6.28;
        double speed = note.Strident ? 15 : 11, near = note.Strident ? 5 : 12;
        Pass(left, right, note, spb, velocity, pan, speed, near, (t, doppler) =>
        {
            double rough = 1 + 6 * lumps.Next(noise.NextDouble() * 2 - 1);
            phase += 2 * Math.PI * firing * doppler * (1 + 0.02 * Math.Sin(2 * Math.PI * 0.7 * t + wobble)) / SampleRate;
            double engine = 0;
            for (int k = 0; k < harmonics.Length; k++) engine += harmonics[k] * Math.Sin((k + 1) * phase);
            double knock = Math.Pow(Math.Abs(Math.Sin(phase / 2)), 8);
            return 0.35 * engine * rough
                + 0.25 * tyres.Next(noise.NextDouble() * 2 - 1)
                + 0.12 * knock * rattle.Next(noise.NextDouble() * 2 - 1);
        });
    }

    /// <summary>
    /// A streetcar rolling slowly by across the road: the motor's whine at the note's pitch, a low rumble, the double
    /// clack of its trucks over each rail joint, and the motorman's bell clanged twice as it comes.
    /// </summary>
    private static void Streetcar(float[] left, float[] right, Random rng, ScoreNote note, double spb, double velocity, double pan)
    {
        double whine = Hz(note.Midi);
        var rumble = SoundSynth.Biquad.LowPass(240);
        var clack = SoundSynth.Biquad.BandPass(1700, 1.5);
        var noise = new Random(rng.Next());
        double[] bellModes = { 1180, 1975, 2860, 3790 };
        const double speed = 7, near = 18, joint = 12 / speed, truck = 8 / speed;
        double phase = 0;
        Pass(left, right, note, spb, velocity, pan, speed, near, (t, doppler) =>
        {
            phase += 2 * Math.PI * whine * doppler / SampleRate;
            double clacks = 0;
            foreach (double axle in new[] { 0, 0.1, truck, truck + 0.1 })
                clacks += Math.Exp(-(((t - axle) % joint + joint) % joint) / 0.012);
            double bell = 0;
            foreach (double ring in new[] { 1.2, 1.55 })
            {
                double b = t - ring;
                if (b < 0) continue;
                double e = Math.Exp(-b / 0.7);
                for (int k = 0; k < bellModes.Length; k++) bell += e * Math.Sin(2 * Math.PI * bellModes[k] * doppler * b) / (k + 1.5);
            }
            return 0.12 * Math.Sin(phase) + 0.05 * Math.Sin(2 * phase)
                + 0.6 * rumble.Next(noise.NextDouble() * 2 - 1)
                + 0.5 * clacks * clack.Next(noise.NextDouble() * 2 - 1)
                + 0.3 * bell;
        });
    }

    /// <summary>
    /// A horn somewhere down the street: a rubber bulb horn's two honks at the note's pitch or, accented, a klaxon's
    /// "ah-oo-gah", its buzzing diaphragm swooping up to the pitch and sagging off.
    /// </summary>
    private static void Horn(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        double pitch = Hz(note.Midi);
        var horn = SoundSynth.Biquad.BandPass(note.Strident ? 1100 : 750, 0.8);
        var bite = SoundSynth.Biquad.Peaking(2600, 5, 1.2);
        (double At, double Length)[] blasts = note.Strident ? new[] { (0.0, 0.95) } : new[] { (0.0, 0.17), (0.3, 0.22) };
        double phase = 0;
        foreach (var (at, length) in blasts)
        {
            int from = start + (int)(at * SampleRate), n = (int)((length + 0.05) * SampleRate);
            for (int i = 0; i < n; i++)
            {
                double t = (double)i / SampleRate;
                double hz = note.Strident
                    ? pitch * (t < 0.35 ? 0.55 + 0.45 * Smooth(t / 0.35) : 1 - 0.22 * Smooth((t - 0.6) / 0.35))
                    : pitch * (1 - 0.04 * t / length);
                phase += 2 * Math.PI * hz / SampleRate;
                double s = Math.Sin(phase);
                double buzz = Math.Sign(s) * Math.Pow(Math.Abs(s), 0.25) + 0.02 * (rng.NextDouble() * 2 - 1);
                double env = Math.Min(1, t / 0.015) * Smooth((length + 0.05 - t) / 0.05);
                buf[(from + i) % buf.Length] += (float)(velocity * env * bite.Next(horn.Next(buzz)));
            }
        }
    }
}
