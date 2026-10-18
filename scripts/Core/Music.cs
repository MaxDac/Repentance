using Godot;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Loops the room's synthesized background music (<see cref="MusicSynth"/>) on the "Music" bus, whose level follows
/// <see cref="GameSettings.MusicVolume"/>. Tracks take a moment to render, so they are rendered off the main thread
/// and start as soon as they are ready; the same track keeps playing from room to room, and through the pause menu.
/// </summary>
public partial class Music : Node
{
    public const string BusName = "Music";

    private readonly Dictionary<Track, Task<float[]>> _renders = new();
    private readonly Dictionary<Track, AudioStreamWav> _streams = new();
    private readonly Dictionary<Track, int> _counts = new();
    private AudioStreamPlayer _player = null!;
    private GameSettings? _settings;

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
        foreach (var track in System.Enum.GetValues<Track>()) RenderAsync(track);
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
    }

    private void Apply()
    {
        int percent = _settings?.MusicVolume ?? GameSettings.DefaultMusicVolume;
        int bus = BusIndex;
        AudioServer.SetBusVolumeDb(bus, SoundSynth.PercentToDb(percent));
        AudioServer.SetBusMute(bus, percent <= 0);
    }

    private Task<float[]> RenderAsync(Track track)
    {
        if (!_renders.TryGetValue(track, out var task))
            _renders[track] = task = Task.Run(() => MusicSynth.Render(track));
        return task;
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
