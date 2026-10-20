using Godot;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Loops the room's synthesized background music (<see cref="MusicSynth"/>) on the "Music" bus, whose level follows
/// <see cref="GameSettings.MusicVolume"/>. Tracks take a moment to render, so they are rendered only when needed, one
/// at a time on a background worker: the track a room asks for first, then the tracks of the rooms next door
/// (<see cref="Prefetch"/>). A track starts as soon as it is ready. Only <see cref="CacheSize"/> renders are kept,
/// as 16-bit PCM, and the least recently used one is dropped (never the one playing). The same track keeps playing
/// from room to room, and through the pause menu. With <see cref="Enabled"/> off (<c>--no-music</c>) nothing is
/// rendered or played, but the requested track is still tracked.
/// </summary>
public partial class Music : Node
{
    public const string BusName = "Music";

    /// <summary>Renders kept in memory: the track playing plus the guesses for the rooms next door.</summary>
    public const int CacheSize = 4;

    // main thread only: the worker just renders and hands its PCM back through _done
    private readonly RenderCache<Track, AudioStreamWav> _cache = new(CacheSize);
    // finished renders, handed from the worker to the main thread (Godot resources are made there)
    private readonly ConcurrentQueue<(Track Track, byte[]? Pcm)> _done = new();
    private readonly Dictionary<Track, int> _counts = new();
    private AudioStreamPlayer _player = null!;
    private GameSettings? _settings;
    private bool _exiting;
    // where a track still rendering should start once it is ready (a shared score picking up where it was)
    private float _startFrom;

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
        // finished renders are picked up even while the game is paused
        ProcessMode = ProcessModeEnum.Always;
        _player = new AudioStreamPlayer { Name = "Player", Bus = BusName, ProcessMode = ProcessModeEnum.Always };
        AddChild(_player);
        if (!Enabled) return;
        // the renders run on a worker thread, so the instrument recordings are read here, on the main thread
        Recordings.Use(path => FileAccess.GetFileAsBytes($"res://{path}"));
        foreach (var instrument in Recordings.Instruments)
            foreach (var midi in Recordings.Needed(instrument).Keys) Recordings.Get(instrument, midi);
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
        _exiting = true;
        _cache.ClearQueue();
    }

    private void Apply()
    {
        int percent = _settings?.MusicVolume ?? GameSettings.DefaultMusicVolume;
        int bus = BusIndex;
        AudioServer.SetBusVolumeDb(bus, SoundSynth.PercentToDb(percent));
        AudioServer.SetBusMute(bus, percent <= 0);
    }

    /// <summary>
    /// Renders these tracks in the background, after anything a room has asked for, so they are ready if the player
    /// goes there next. Replaces the previous guesses; only as many as the cache can hold beside the current track.
    /// </summary>
    public void Prefetch(IEnumerable<Track> tracks)
    {
        if (!Enabled) return;
        _cache.Prefetch(tracks);
        StartWorker();
    }

    // One render at a time, so music never keeps every core (and the GC) busy at once. The next one starts when the
    // main thread has kept this one.
    private void StartWorker()
    {
        if (_exiting || !_cache.TryStartNext(out var track)) return;
        Task.Run(() =>
        {
            byte[]? pcm = null;
            try { pcm = MusicSynth.ToPcm16(MusicSynth.Render(track)); }
            catch (System.Exception ex) { GD.PushError($"rendering {track}: {ex}"); }
            _done.Enqueue((track, pcm));
            // a render leaves a few hundred MB of float buffers behind; hand that memory back to the system now
            System.GC.Collect(System.GC.MaxGeneration, System.GCCollectionMode.Aggressive, blocking: true, compacting: true);
        });
    }

    public override void _Process(double delta)
    {
        while (_done.TryDequeue(out var done))
        {
            if (done.Pcm == null) _cache.Fail(done.Track);
            else
            {
                var stream = ToStream(done.Pcm);
                _cache.Finish(done.Track, stream);
                if (Current == done.Track && !_player.Playing) Start(done.Track, stream, _startFrom);
            }
            StartWorker();
        }
    }

    /// <summary>Starts (or, with null, stops) the background music; asking for the track already playing changes nothing.
    /// A track sharing the score of the one playing (the same band heard from elsewhere) picks up where it was.</summary>
    public void Play(Track? track)
    {
        if (track == Current) return;
        float from = Current is { } previous && track is { } next && _player.Playing && MusicSynth.SharesScore(previous, next)
            ? _player.GetPlaybackPosition() : 0;
        Current = track;
        _player.Stop();
        _cache.Pinned = track;
        if (track is not { } t) return;
        _counts[t] = Count(t) + 1;
        if (!Enabled) return;
        if (_cache.TryGet(t, out var stream)) Start(t, stream, from);
        else
        {
            _startFrom = from;
            _cache.Request(t);
            StartWorker();
        }
    }

    private void Start(Track track, AudioStreamWav stream, float from)
    {
        _player.Stream = stream;
        _player.VolumeDb = MusicSynth.BaseVolumeDb(track);
        _player.Play(from);
    }

    /// <summary>Whether a track has finished rendering and is actually sounding.</summary>
    public bool Playing => _player.Playing;

    private static AudioStreamWav ToStream(byte[] pcm) => new()
    {
        Format = AudioStreamWav.FormatEnum.Format16Bits,
        MixRate = MusicSynth.SampleRate,
        Stereo = true,
        Data = pcm,
        LoopMode = AudioStreamWav.LoopModeEnum.Forward,
        LoopBegin = 0,
        LoopEnd = pcm.Length / 4,
    };
}