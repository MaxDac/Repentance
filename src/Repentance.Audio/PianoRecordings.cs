using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>
/// Recordings of a real grand piano played pianissimo, one per pitch, for <see cref="Instrument.RecordedPiano"/>: the
/// University of Iowa Musical Instrument Samples (free to use without restrictions), cut to each note's onset,
/// downmixed to mono and stored at <see cref="MusicSynth.SampleRate"/> as raw 16-bit little-endian PCM in
/// <see cref="Folder"/>. <c>tools/music</c> (<c>piano</c>) regenerates them for every recorded note the scores use. Godot-free: the
/// game and the tests each say how to read a file with <see cref="Use"/>.
/// </summary>
public static class PianoRecordings
{
    public const string Folder = "assets/audio/piano";

    /// <summary>How long the felt damper takes to quiet a string once a key is let go, in seconds.</summary>
    public const double DamperSeconds = 0.12;

    /// <summary>How much of each recording is kept past the longest hold, so the damper can fall.</summary>
    public const double TailSeconds = 7 * DamperSeconds;

    private static readonly string[] Names = { "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" };
    private static readonly ConcurrentDictionary<int, float[]> Cache = new();
    private static Func<string, byte[]?>? _read;

    /// <summary>The note's name as the recordings spell it, with flats: "C4", "Db4", "Bb1".</summary>
    public static string Name(int midi) => $"{Names[midi % 12]}{midi / 12 - 1}";

    public static string FileName(int midi) => $"{Name(midi)}.pcm";

    /// <summary>Sets how a recording's file (named by <see cref="FileName"/>) is read, and forgets any loaded ones.</summary>
    public static void Use(Func<string, byte[]?> read)
    {
        _read = read;
        Cache.Clear();
    }

    /// <summary>The recording of one pitch, as samples in [-1, 1].</summary>
    public static float[] Get(int midi) => Cache.GetOrAdd(midi, m =>
    {
        var read = _read ?? throw new InvalidOperationException("PianoRecordings.Use was never called");
        var bytes = read(FileName(m));
        if (bytes is not { Length: > 0 })
            throw new InvalidOperationException($"No piano recording {FileName(m)} in {Folder}: run dotnet run --project tools/music -- piano");
        return Decode(bytes);
    });

    /// <summary>Every pitch the scores play on the recorded piano, with the longest it is held for, in seconds.</summary>
    public static IReadOnlyDictionary<int, double> Needed() =>
        Enum.GetValues<Track>()
            .SelectMany(t => MusicSynth.Score(t).Where(n => n.Instrument == Instrument.RecordedPiano)
                .Select(n => (n.Midi, Seconds: n.Beats * MusicSynth.SecondsPerBeat(t))))
            .GroupBy(n => n.Midi)
            .ToDictionary(g => g.Key, g => g.Max(n => n.Seconds));

    public static float[] Decode(byte[] pcm)
    {
        var samples = new float[pcm.Length / 2];
        for (int i = 0; i < samples.Length; i++) samples[i] = (short)(pcm[2 * i] | pcm[2 * i + 1] << 8) / 32768f;
        return samples;
    }

    public static byte[] Encode(IReadOnlyList<float> samples)
    {
        var pcm = new byte[samples.Count * 2];
        for (int i = 0; i < samples.Count; i++)
        {
            short v = (short)Math.Clamp(Math.Round(samples[i] * 32767), short.MinValue, short.MaxValue);
            pcm[2 * i] = (byte)(v & 0xff);
            pcm[2 * i + 1] = (byte)((v >> 8) & 0xff);
        }
        return pcm;
    }
}
