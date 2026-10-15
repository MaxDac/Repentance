using System;

namespace Repentance;

public static partial class MusicSynth
{
    private static void Sound(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        switch (note.Instrument)
        {
            case Instrument.DoubleBass or Instrument.Cello or Instrument.Viola or Instrument.Violin:
                Bow(buf, rng, note, spb, velocity, TimbreOf(note.Instrument));
                break;
            case Instrument.OrganFlute or Instrument.OrganPlenum or Instrument.OrganPedal:
                Pipe(buf, rng, note, spb, velocity);
                break;
            case Instrument.Piano:
                Hammer(buf, rng, note, spb, velocity);
                break;
            case Instrument.Clarinet:
                Reed(buf, rng, note, spb, velocity);
                break;
            case Instrument.UprightBass:
                Pluck(buf, rng, note, spb, velocity);
                break;
            case Instrument.Drums:
                Drum(buf, rng, note, spb, velocity);
                break;
        }
    }

    private static SoundSynth.Biquad[] BodyOf(Instrument instrument) => instrument switch
    {
        Instrument.DoubleBass or Instrument.Cello or Instrument.Viola or Instrument.Violin => TimbreOf(instrument).Body(),
        Instrument.OrganFlute => new[] { SoundSynth.Biquad.HighPass(30), SoundSynth.Biquad.LowPass(6000) },
        Instrument.OrganPlenum => new[] { SoundSynth.Biquad.HighPass(30), SoundSynth.Biquad.LowPass(9000) },
        Instrument.OrganPedal => new[] { SoundSynth.Biquad.HighPass(25), SoundSynth.Biquad.LowPass(4000) },
        Instrument.Piano => new[] { SoundSynth.Biquad.HighPass(30), SoundSynth.Biquad.LowPass(9000) },
        Instrument.Clarinet => new[]
        {
            SoundSynth.Biquad.HighPass(140), SoundSynth.Biquad.Peaking(1400, 3, 1), SoundSynth.Biquad.LowPass(4500),
            SoundSynth.Biquad.LowPass(6500),
        },
        Instrument.UprightBass => new[]
        {
            SoundSynth.Biquad.HighPass(35), SoundSynth.Biquad.Peaking(90, 4, 1), SoundSynth.Biquad.Peaking(700, -2, 1),
            SoundSynth.Biquad.LowPass(2500),
        },
        _ => new[] { SoundSynth.Biquad.HighPass(60) },
    };

    /// <summary>A sine oscillator by complex rotation: one multiply-add per sample instead of a sine.</summary>
    private sealed class Osc
    {
        private readonly double _c, _s;
        private double _re, _im;
        private int _n;

        public Osc(double hz, double phase)
        {
            _c = Math.Cos(2 * Math.PI * hz / SampleRate);
            _s = Math.Sin(2 * Math.PI * hz / SampleRate);
            _re = Math.Cos(phase);
            _im = Math.Sin(phase);
        }

        public double Next()
        {
            double v = _im;
            (_re, _im) = (_re * _c - _im * _s, _re * _s + _im * _c);
            if ((++_n & 1023) == 0)
            {
                double m = 1 / Math.Sqrt(_re * _re + _im * _im);
                _re *= m;
                _im *= m;
            }
            return v;
        }
    }

    // ------------------------------------------------------------------ bowed strings

    private sealed record Timbre(double Attack, double Release, double VibratoHz, double VibratoCents, double Noise,
        Func<SoundSynth.Biquad[]> Body);

    private static Timbre TimbreOf(Instrument instrument) => instrument switch
    {
        Instrument.DoubleBass => new(0.32, 0.7, 4.8, 9, 0.025, () => new[]
        {
            SoundSynth.Biquad.HighPass(32), SoundSynth.Biquad.Peaking(105, 5, 1.1), SoundSynth.Biquad.Peaking(420, -3, 1),
            SoundSynth.Biquad.Peaking(950, 3, 1.6), SoundSynth.Biquad.LowPass(1700), SoundSynth.Biquad.LowPass(2600),
        }),
        Instrument.Cello => new(0.24, 0.55, 5.3, 13, 0.03, () => new[]
        {
            SoundSynth.Biquad.HighPass(60), SoundSynth.Biquad.Peaking(220, 4, 1.2), SoundSynth.Biquad.Peaking(620, 2, 1.2),
            SoundSynth.Biquad.Peaking(1450, 3, 1.5), SoundSynth.Biquad.LowPass(3600), SoundSynth.Biquad.LowPass(5200),
        }),
        Instrument.Viola => new(0.2, 0.5, 5.6, 14, 0.035, () => new[]
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
            double dt = f0 * Cents(cents) / SampleRate;
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

    // ------------------------------------------------------------------ pipe organ

    // (footage as a multiple of the 8' pitch, level) for the stops drawn on each division
    private static readonly (double Ratio, double Level)[] FluteRanks = { (1, 1), (2, 0.28), (3, 0.06), (4, 0.22), (8, 0.04) };
    private static readonly (double Ratio, double Level)[] PedalRanks = { (0.5, 0.85), (1, 1), (2, 0.35), (3, 0.1), (4, 0.12), (6, 0.03) };
    private static readonly (double Ratio, double Level)[] PlenumRanks =
    {
        (0.5, 0.45), (1, 1), (2, 0.8), (3, 0.42), (4, 0.6), (5, 0.12), (6, 0.32), (8, 0.36), (10, 0.06), (12, 0.2),
        (16, 0.16),
    };

    /// <summary>
    /// One organ pipe set: steady additive partials from the drawn stops, each pipe a hair off true pitch, a breathy
    /// chiff as the wind speaks and a quick, clean cut-off when the key is let go.
    /// </summary>
    private static void Pipe(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        var (ranks, attack, chiffLevel) = note.Instrument switch
        {
            Instrument.OrganFlute => (FluteRanks, 0.06, 0.35),
            Instrument.OrganPedal => (PedalRanks, 0.09, 0.2),
            _ => (PlenumRanks, 0.045, 0.25),
        };
        const double release = 0.09;
        double f0 = Hz(note.Midi), held = note.Beats * spb;
        int start = (int)Math.Round(note.Beat * spb * SampleRate), n = (int)((held + release) * SampleRate);
        var oscs = new Osc[ranks.Length];
        var levels = new double[ranks.Length];
        double total = 0;
        for (int k = 0; k < ranks.Length; k++)
        {
            double hz = f0 * ranks[k].Ratio * Cents(3 * (rng.NextDouble() * 2 - 1));
            // the top of a mixture breaks back an octave rather than going out of hearing
            while (hz > 9000) hz /= 2;
            oscs[k] = new Osc(hz, rng.NextDouble() * 2 * Math.PI);
            levels[k] = ranks[k].Level;
            total += levels[k];
        }
        var chiff = SoundSynth.Biquad.BandPass(Math.Min(8000, f0 * 3), 2);
        double amp = velocity * 0.22 / Math.Sqrt(total);
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double env = Smooth(t / attack) * (t < held ? 1 : Math.Max(0, 1 - (t - held) / release));
            double s = 0;
            // higher pipes speak a little before the fundamental settles
            for (int k = 0; k < oscs.Length; k++) s += levels[k] * oscs[k].Next() * (k == 0 ? Smooth(t / (attack * 1.4)) : 1);
            s += chiffLevel * 4 * Math.Exp(-t / 0.04) * chiff.Next(rng.NextDouble() * 2 - 1);
            buf[(start + i) % buf.Length] += (float)(amp * env * s);
        }
    }

    // ------------------------------------------------------------------ piano

    /// <summary>
    /// A piano string: slightly stretched (inharmonic) partials weighted by where the hammer strikes, the upper ones
    /// dying away first, the lowest three doubled by a second string a hair out of tune so the tone beats and blooms.
    /// The damper falls when the note's hold is over.
    /// </summary>
    private static void Hammer(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        double f0 = Hz(note.Midi), held = note.Beats * spb;
        double b = 8e-5 * Math.Pow(2, (note.Midi - 48) / 18.0);
        double tau = 3.2 * Math.Pow(2, -(note.Midi - 48) / 20.0) + 0.4;
        double vel = velocity * (0.92 + 0.16 * rng.NextDouble());
        var oscs = new System.Collections.Generic.List<(Osc Osc, double Level, double Decay)>();
        for (int k = 1; k <= 30; k++)
        {
            double hz = k * f0 * Math.Sqrt(1 + b * k * k);
            if (hz > 9500) break;
            // a harder blow brings out the upper partials
            double level = Math.Abs(Math.Sin(Math.PI * k * 0.12)) / Math.Pow(k, 0.8) * Math.Exp(-(k - 1) * (0.9 - vel) * 0.25);
            double decay = tau / (1 + 0.18 * (k - 1));
            if (k <= 3)
            {
                oscs.Add((new Osc(hz * Cents(0.7), rng.NextDouble() * 2 * Math.PI), level * 0.5, decay));
                oscs.Add((new Osc(hz * Cents(-0.7), rng.NextDouble() * 2 * Math.PI), level * 0.5, decay));
            }
            else oscs.Add((new Osc(hz, rng.NextDouble() * 2 * Math.PI), level, decay));
        }
        var thump = SoundSynth.Biquad.LowPass(Math.Min(2000, f0 * 4));
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        int n = (int)(Math.Min(held + 0.6, tau * 7) * SampleRate);
        double amp = vel * 0.3;
        // each partial's decay as a per-sample factor
        var gains = new double[oscs.Count];
        var steps = new double[oscs.Count];
        for (int k = 0; k < oscs.Count; k++)
        {
            gains[k] = oscs[k].Level;
            steps[k] = Math.Exp(-1 / (oscs[k].Decay * SampleRate));
        }
        double damper = 1;
        double damperStep = Math.Exp(-1 / (0.09 * SampleRate));
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            if (t > held) damper *= damperStep;
            if (damper < 1e-4) break;
            double s = 0;
            for (int k = 0; k < oscs.Count; k++)
            {
                s += gains[k] * oscs[k].Osc.Next();
                gains[k] *= steps[k];
            }
            // a fast initial drop to the singing aftersound
            s *= 0.55 + 0.45 * Math.Exp(-t / 0.25);
            s *= Math.Min(1, t / 0.002);
            if (t < 0.03) s += 0.3 * Math.Exp(-t / 0.008) * thump.Next(rng.NextDouble() * 2 - 1);
            buf[(start + i) % buf.Length] += (float)(amp * damper * s);
        }
    }

    // ------------------------------------------------------------------ clarinet

    /// <summary>
    /// A clarinet: a hollow square wave (odd harmonics) with a touch of sawtooth, each note scooped up into pitch, a
    /// slow vibrato that only starts on longer notes, and the breath behind the reed.
    /// </summary>
    private static void Reed(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        const double attack = 0.035, release = 0.09;
        double f0 = Hz(note.Midi), held = note.Beats * spb * 0.95;
        int start = (int)Math.Round(note.Beat * spb * SampleRate), n = (int)((held + release) * SampleRate);
        var tone = SoundSynth.Biquad.LowPass(Math.Min(5000, f0 * 5));
        var breath = SoundSynth.Biquad.BandPass(Math.Min(5000, f0 * 4), 1.2);
        var drift = SoundSynth.Biquad.LowPass(3);
        double phase = rng.NextDouble(), vibPhase = rng.NextDouble() * 2 * Math.PI;
        double amp = velocity * (0.9 + 0.2 * rng.NextDouble()) * 0.22;
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double env = Smooth(t / attack) * (t < held ? 1 : Math.Cos(Math.PI / 2 * Math.Min(1, (t - held) / release)));
            double cents = -35 * Math.Exp(-t / 0.05) + 12 * Smooth((t - 0.25) / 0.4) * Math.Sin(vibPhase + 2 * Math.PI * 5.2 * t)
                + 25 * drift.Next(rng.NextDouble() * 2 - 1);
            double dt = f0 * Cents(cents) / SampleRate;
            phase += dt; if (phase >= 1) phase -= 1;
            double p2 = phase + 0.5 >= 1 ? phase - 0.5 : phase + 0.5;
            double square = (phase < 0.5 ? 1 : -1) + PolyBlep(phase, dt) - PolyBlep(p2, dt);
            double saw = 2 * phase - 1 - PolyBlep(phase, dt);
            double s = tone.Next(0.85 * square + 0.15 * saw) + 0.12 * breath.Next(rng.NextDouble() * 2 - 1);
            buf[(start + i) % buf.Length] += (float)(amp * env * s);
        }
    }

    // ------------------------------------------------------------------ upright bass

    /// <summary>
    /// A plucked gut string (Karplus-Strong): a burst of dark noise circulating in a tuned delay line, losing a little
    /// on each pass, and choked off by the left hand when the note ends.
    /// </summary>
    private static void Pluck(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        double f0 = Hz(note.Midi), held = note.Beats * spb * 0.9;
        double period = (double)SampleRate / f0 - 0.5;
        int len = (int)Math.Floor(period - 0.1);
        double frac = period - len, ap = (1 - frac) / (1 + frac);
        var line = new double[len];
        var dark = SoundSynth.Biquad.LowPass(Math.Min(1200, f0 * 8));
        for (int k = 0; k < len; k++) line[k] = dark.Next(rng.NextDouble() * 2 - 1) + 0.6 * Math.Sin(Math.PI * k / len);
        double mean = 0;
        foreach (var v in line) mean += v;
        mean /= len;
        for (int k = 0; k < len; k++) line[k] -= mean;
        int start = (int)Math.Round(note.Beat * spb * SampleRate), n = (int)((held + 0.2) * SampleRate);
        double amp = velocity * (0.9 + 0.2 * rng.NextDouble()) * 0.5, prev = 0, apX = 0, apY = 0;
        int idx = 0;
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            double loss = t < held ? 0.9975 : 0.95;
            double x = line[idx];
            double avg = loss * 0.5 * (x + prev);
            prev = x;
            double y = ap * avg + apX - ap * apY;
            apX = avg;
            apY = y;
            line[idx] = y;
            if (++idx == len) idx = 0;
            double env = Math.Min(1, t / 0.003) * (t < held ? 1 : Math.Max(0, 1 - (t - held) / 0.2));
            buf[(start + i) % buf.Length] += (float)(amp * env * x);
        }
    }

    // ------------------------------------------------------------------ brushed drums

    /// <summary>A brushed kit, one General MIDI drum per pitch (see <see cref="Instrument.Drums"/>).</summary>
    private static void Drum(float[] buf, Random rng, ScoreNote note, double spb, double velocity)
    {
        int start = (int)Math.Round(note.Beat * spb * SampleRate);
        double amp = velocity * (0.85 + 0.3 * rng.NextDouble());
        double held = note.Beats * spb;
        switch (note.Midi)
        {
            case 36: // kick, feathered
            {
                int n = (int)(0.4 * SampleRate);
                double phase = 0;
                for (int i = 0; i < n; i++)
                {
                    double t = (double)i / SampleRate;
                    phase += 2 * Math.PI * (48 + 22 * Math.Exp(-t / 0.05)) / SampleRate;
                    buf[(start + i) % buf.Length] += (float)(amp * 0.6 * Math.Min(1, t / 0.004) * Math.Exp(-t / 0.12) * Math.Sin(phase));
                }
                break;
            }
            case 38: // brush tap on the snare
                Noise(buf, rng, start, 0.25, amp * 0.5, SoundSynth.Biquad.BandPass(2500, 0.8), t => Math.Exp(-t / 0.05));
                break;
            case 40: // brush swept round the snare head, swelling once a beat
                Noise(buf, rng, start, held, amp * 0.18, SoundSynth.Biquad.BandPass(3200, 0.5), t =>
                {
                    double beat = t / spb, f = beat - Math.Floor(beat);
                    return (0.35 + 0.65 * Math.Pow(Math.Sin(Math.PI * f), 2)) * (Math.Floor(beat) % 2 == 1 ? 1.15 : 1);
                });
                break;
            case 42: // hi-hat closed with the foot
                Noise(buf, rng, start, 0.12, amp * 0.3, SoundSynth.Biquad.HighPass(7000), t => Math.Exp(-t / 0.025));
                break;
            default: // ride cymbal
            {
                int n = (int)(1.2 * SampleRate);
                var hp = SoundSynth.Biquad.HighPass(5000);
                double[] modes = { 517, 811, 1243, 1789, 2457, 3203, 4211 };
                var oscs = Array.ConvertAll(modes, hz => new Osc(hz * (0.99 + 0.02 * rng.NextDouble()), rng.NextDouble() * 6.28));
                for (int i = 0; i < n; i++)
                {
                    double t = (double)i / SampleRate;
                    double ping = 0;
                    foreach (var o in oscs) ping += o.Next();
                    double s = 0.5 * hp.Next(rng.NextDouble() * 2 - 1) * Math.Exp(-t / 0.3)
                        + 0.04 * ping * Math.Exp(-t / 0.6);
                    buf[(start + i) % buf.Length] += (float)(amp * 0.4 * Math.Min(1, t / 0.001) * s);
                }
                break;
            }
        }
    }

    private static void Noise(float[] buf, Random rng, int start, double seconds, double amp, SoundSynth.Biquad filter,
        Func<double, double> env)
    {
        int n = (int)(seconds * SampleRate);
        for (int i = 0; i < n; i++)
        {
            double t = (double)i / SampleRate;
            buf[(start + i) % buf.Length] += (float)(amp * Math.Min(1, t / 0.002) * env(t) * filter.Next(rng.NextDouble() * 2 - 1));
        }
    }
}
