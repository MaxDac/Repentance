using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>
/// Recordings of real instruments played pianissimo, one file per pitch, for the recorded instruments
/// (<see cref="Instrument.RecordedPiano"/>, <see cref="Instrument.RecordedSax"/>, <see cref="Instrument.RecordedBass"/>):
/// the University of Iowa Musical Instrument Samples (free to use without restrictions), cut to each note's onset,
/// downmixed to mono and stored at <see cref="MusicSynth.SampleRate"/> as raw 16-bit little-endian PCM in the
/// instrument's <see cref="Folder"/>. <c>tools/music</c> (<c>recordings</c>) regenerates them for every recorded note the
/// scores use. Godot-free: the game and the tests each say how to read a file with <see cref="Use"/>.
/// </summary>
public static class Recordings
{
    public static readonly Instrument[] Instruments =
        { Instrument.RecordedPiano, Instrument.RecordedSax, Instrument.RecordedBass };

    public static bool IsRecorded(Instrument instrument) => Array.IndexOf(Instruments, instrument) >= 0;

    /// <summary>Where an instrument's recordings live, relative to the project.</summary>
    public static string Folder(Instrument instrument) => instrument switch
    {
        Instrument.RecordedPiano => "assets/audio/piano",
        Instrument.RecordedSax => "assets/audio/sax",
        Instrument.RecordedBass => "assets/audio/bass",
        _ => throw new ArgumentOutOfRangeException(nameof(instrument)),
    };

    /// <summary>
    /// How long a note takes to die away once it is let go, in seconds: the piano's felt damper falling on the string,
    /// the saxophonist's breath stopping, the bassist's hand on the string.
    /// </summary>
    public static double ReleaseSeconds(Instrument instrument) => instrument switch
    {
        Instrument.RecordedSax => 0.07,
        Instrument.RecordedBass => 0.1,
        _ => 0.12,
    };

    /// <summary>How much of each recording is kept past the longest hold, so the release can fade.</summary>
    public static double TailSeconds(Instrument instrument) => 7 * ReleaseSeconds(instrument);

    private static readonly string[] Names = { "C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B" };
    private static readonly ConcurrentDictionary<(Instrument, int), float[]> Cache = new();
    private static Func<string, byte[]?>? _read;

    /// <summary>The note's name as the recordings spell it, with flats: "C4", "Db4", "Bb1".</summary>
    public static string Name(int midi) => $"{Names[midi % 12]}{midi / 12 - 1}";

    public static string FileName(int midi) => $"{Name(midi)}.pcm";

    /// <summary>The file's path relative to the project, as <see cref="Use"/>'s reader receives it.</summary>
    public static string PathOf(Instrument instrument, int midi) => $"{Folder(instrument)}/{FileName(midi)}";

    /// <summary>Sets how a recording's file (by <see cref="PathOf"/>) is read, and forgets any loaded ones.</summary>
    public static void Use(Func<string, byte[]?> read)
    {
        _read = read;
        Cache.Clear();
    }

    /// <summary>The recording of one pitch, as samples in [-1, 1].</summary>
    public static float[] Get(Instrument instrument, int midi) => Cache.GetOrAdd((instrument, midi), key =>
    {
        var read = _read ?? throw new InvalidOperationException("Recordings.Use was never called");
        var bytes = read(PathOf(key.Item1, key.Item2));
        if (bytes is not { Length: > 0 })
            throw new InvalidOperationException($"No recording {PathOf(key.Item1, key.Item2)}: run dotnet run --project tools/music -- recordings");
        return Decode(bytes);
    });

    /// <summary>Every pitch the scores play on an instrument, with the longest it is held for, in seconds.</summary>
    public static IReadOnlyDictionary<int, double> Needed(Instrument instrument) =>
        Enum.GetValues<Track>()
            .SelectMany(t => MusicSynth.Score(t).Where(n => n.Instrument == instrument)
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
