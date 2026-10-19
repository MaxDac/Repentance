using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Loops the room's synthesized background music (<see cref="MusicSynth"/>) on the "Music" bus, whose level follows
/// <see cref="GameSettings.MusicVolume"/>. Tracks take a moment to render, so they are rendered one at a time on a
/// background worker (a requested track jumps the queue) and start as soon as they are ready; the same track keeps
/// playing from room to room, and through the pause menu. With <see cref="Enabled"/> off (<c>--no-music</c>) nothing
/// is rendered or played, but the requested track is still tracked.
/// </summary>
public partial class Music : Node
{
    public const string BusName = "Music";

    private readonly Dictionary<Track, TaskCompletionSource<float[]>> _renders = new();
    // tracks still to render, in order; shared with the worker, so only touched under its lock
    private readonly List<Track> _queue = new();
    private readonly Dictionary<Track, AudioStreamWav> _streams = new();
    private readonly Dictionary<Track, int> _counts = new();
    private AudioStreamPlayer _player = null!;
    private GameSettings? _settings;

    /// <summary>Whether music is rendered and played at all (off with <c>--no-music</c>, for suites that never check it).</summary>
    public bool Enabled { get; set; } = true;

    /// <summary>The track the current room asked for, if any (it may still be rendering).</summary>
    public Track? Current { get; private set; }

    /// <summary>How many times a track has been started (used by the autoplay test; audio is silent when headless).</summary>
    public int Count(Track track) => _counts.GetValueOrDefault(track);

    public static int BusIndex
    {
        get
        {
            int index = AudioServer.GetBusIndex(BusName);
            if (index >= 0) return index;
            AudioServer.AddBus();
            index = AudioServer.BusCount - 1;
            AudioServer.SetBusName(index, BusName);
            AudioServer.SetBusSend(index, "Master");
            return index;
        }
    }

    public override void _Ready()
    {
        _player = new AudioStreamPlayer { Name = "Player", Bus = BusName, ProcessMode = ProcessModeEnum.Always };
        AddChild(_player);
        if (!Enabled) return;
        // the renders run on worker threads, so the instrument recordings are read here, on the main thread
        Recordings.Use(path => FileAccess.GetFileAsBytes($"res://{path}"));
        foreach (var instrument in Recordings.Instruments)
            foreach (var midi in Recordings.Needed(instrument).Keys) Recordings.Get(instrument, midi);
        foreach (var track in System.Enum.GetValues<Track>())
            _renders[track] = new TaskCompletionSource<float[]>(TaskCreationOptions.RunContinuationsAsynchronously);
        _queue.AddRange(_renders.Keys);
        Task.Run(RenderQueue);
    }

    // One worker, so the boot doesn't keep every core (and the GC) busy rendering all the tracks at once.
    private void RenderQueue()
    {
        while (true)
        {
            Track track;
            lock (_queue)
            {
                if (_queue.Count == 0) return;
                track = _queue[0];
                _queue.RemoveAt(0);
            }
            var done = _renders[track];
            try { done.SetResult(MusicSynth.Render(track)); }
            catch (System.Exception ex) { done.SetException(ex); }
        }
    }

    public void Bind(GameSettings settings)
    {
        if (_settings != null) _settings.Changed -= Apply;
        _settings = settings;
        _settings.Changed += Apply;
        Apply();
    }

    public override void _ExitTree()
    {
        if (_settings != null) _settings.Changed -= Apply;
        lock (_queue) _queue.Clear();
    }

    private void Apply()
    {
        int percent = _settings?.MusicVolume ?? GameSettings.DefaultMusicVolume;
        int bus = BusIndex;
        AudioServer.SetBusVolumeDb(bus, SoundSynth.PercentToDb(percent));
        AudioServer.SetBusMute(bus, percent <= 0);
    }

    /// <summary>The track's render, moved to the front of the queue if it hasn't started yet.</summary>
    private Task<float[]> RenderAsync(Track track)
    {
        lock (_queue)
            if (_queue.Remove(track)) _queue.Insert(0, track);
        return _renders[track].Task;
    }

    /// <summary>Starts (or, with null, stops) the background music; asking for the track already playing changes nothing.
    /// A track sharing the score of the one playing (the same band heard from elsewhere) picks up where it was.</summary>
    public async void Play(Track? track)
    {
        if (track == Current) return;
        float from = Current is { } previous && track is { } next && _player.Playing && MusicSynth.SharesScore(previous, next)
            ? _player.GetPlaybackPosition() : 0;
        Current = track;
        _player.Stop();
        if (track is not { } t) return;
        _counts[t] = Count(t) + 1;
        if (!Enabled) return;
        if (!_streams.TryGetValue(t, out var stream))
        {
            var samples = await RenderAsync(t);
            if (!IsInsideTree()) return;
            stream = _streams.GetValueOrDefault(t) ?? (_streams[t] = ToStream(samples));
        }
        if (Current != t || _player.Playing) return;
        _player.Stream = stream;
        _player.VolumeDb = MusicSynth.BaseVolumeDb(t);
        _player.Play(from);
    }

    /// <summary>Whether a track has finished rendering and is actually sounding.</summary>
    public bool Playing => _player.Playing;

    private static AudioStreamWav ToStream(float[] stereo)
    {
        var bytes = new byte[stereo.Length * 2];
        for (int i = 0; i < stereo.Length; i++)
        {
            short v = (short)Mathf.Clamp(Mathf.RoundToInt(stereo[i] * short.MaxValue), short.MinValue, short.MaxValue);
            bytes[i * 2] = (byte)(v & 0xff);
            bytes[i * 2 + 1] = (byte)((v >> 8) & 0xff);
        }
        return new AudioStreamWav
        {
            Format = AudioStreamWav.FormatEnum.Format16Bits,
            MixRate = MusicSynth.SampleRate,
            Stereo = true,
            Data = bytes,
            LoopMode = AudioStreamWav.LoopModeEnum.Forward,
            LoopBegin = 0,
            LoopEnd = stereo.Length / 2,
        };
    }
}
