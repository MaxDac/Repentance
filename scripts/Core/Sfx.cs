using Godot;
using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Plays the synthesized sound effects (<see cref="SoundSynth"/>) on the "Effects" bus, whose level follows
/// <see cref="GameSettings.EffectsVolume"/>: one-shots from a small player pool, footsteps, and a looping room
/// ambience. Players pause with the game; the settings preview plays even while the menu has the tree paused.
/// </summary>
public partial class Sfx : Node
{
    public const string BusName = "Effects";
    private const int MaxVoices = 12;

    private readonly Dictionary<(Sound, int), AudioStreamWav> _streams = new();
    private readonly List<AudioStreamPlayer> _voices = new();
    private readonly Dictionary<Sound, int> _counts = new();
    private readonly System.Random _rng = new();
    private AudioStreamPlayer _ambient = null!;
    private AudioStreamPlayer _preview = null!;
    private GameSettings? _settings;
    private int _nextVoice;

    /// <summary>The looping ambience currently playing, if any.</summary>
    public Sound? Ambient { get; private set; }

    /// <summary>How many times a sound has started (used by the autoplay test; audio is silent when headless).</summary>
    public int Count(Sound sound) => _counts.GetValueOrDefault(sound);

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
        _ambient = new AudioStreamPlayer { Name = "Ambient", Bus = BusName };
        AddChild(_ambient);
        _preview = new AudioStreamPlayer { Name = "Preview", Bus = BusName, ProcessMode = ProcessModeEnum.Always };
        AddChild(_preview);
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
        int percent = _settings?.EffectsVolume ?? GameSettings.DefaultEffectsVolume;
        int bus = BusIndex;
        AudioServer.SetBusVolumeDb(bus, SoundSynth.PercentToDb(percent));
        AudioServer.SetBusMute(bus, percent <= 0);
    }

    public AudioStreamWav Stream(Sound sound, int variant = 0)
    {
        if (_streams.TryGetValue((sound, variant), out var cached)) return cached;
        var samples = SoundSynth.Render(sound, variant);
        var bytes = new byte[samples.Length * 2];
        for (int i = 0; i < samples.Length; i++)
        {
            short v = (short)Mathf.Clamp(Mathf.RoundToInt(samples[i] * short.MaxValue), short.MinValue, short.MaxValue);
            bytes[i * 2] = (byte)(v & 0xff);
            bytes[i * 2 + 1] = (byte)((v >> 8) & 0xff);
        }
        var stream = new AudioStreamWav
        {
            Format = AudioStreamWav.FormatEnum.Format16Bits,
            MixRate = SoundSynth.SampleRate,
            Stereo = false,
            Data = bytes,
        };
        if (sound == Sound.Rain)
        {
            stream.LoopMode = AudioStreamWav.LoopModeEnum.Forward;
            stream.LoopBegin = 0;
            stream.LoopEnd = samples.Length;
        }
        _streams[(sound, variant)] = stream;
        return stream;
    }

    /// <summary>Plays a one-shot. <paramref name="volumeDb"/> is added to the sound's own level.</summary>
    public void Play(Sound sound, float volumeDb = 0, float pitch = 1, int variant = 0)
    {
        var voice = NextVoice();
        voice.Stream = Stream(sound, variant);
        voice.VolumeDb = SoundSynth.BaseVolumeDb(sound) + volumeDb;
        voice.PitchScale = pitch;
        voice.Play();
        _counts[sound] = Count(sound) + 1;
    }

    /// <summary>One footstep on <paramref name="floor"/>; <paramref name="depthScale"/> softens far-away walkers.</summary>
    public void Step(FloorSurface floor, float depthScale = 1)
    {
        float distance = 1.5f * Mathf.LinearToDb(Mathf.Clamp(depthScale, 0.3f, 1.2f));
        Play(SoundSynth.StepFor(floor), distance, (float)(0.94 + _rng.NextDouble() * 0.12),
            _rng.Next(SoundSynth.StepVariants));
    }

    /// <summary>Plays the sounds a sound-effect line such as "*BANG*" stands for (see <see cref="SoundSynth.CuesFor"/>).</summary>
    public void PlayCues(string text)
    {
        foreach (var cue in SoundSynth.CuesFor(text))
        {
            if (cue.Delay <= 0) { Play(cue.Sound); continue; }
            var sound = cue.Sound;
            GetTree().CreateTimer(cue.Delay, processAlways: false).Timeout += () =>
            {
                if (IsInsideTree()) Play(sound, pitch: (float)(0.97 + _rng.NextDouble() * 0.06));
            };
        }
    }

    /// <summary>Starts (or, with null, stops) the room's looping ambience; the same loop keeps playing across rooms.</summary>
    public void SetAmbient(Sound? sound, float volumeDb = 0)
    {
        if (sound is { } s)
        {
            _ambient.VolumeDb = SoundSynth.BaseVolumeDb(s) + volumeDb;
            if (Ambient == s && _ambient.Playing) return;
            _ambient.Stream = Stream(s);
            _ambient.Play();
            _counts[s] = Count(s) + 1;
        }
        else _ambient.Stop();
        Ambient = sound;
    }

    /// <summary>A sample at the current effects volume, so the player can hear the setting while the menu is open.</summary>
    public void Preview()
    {
        _preview.Stream = Stream(Sound.Knock);
        _preview.VolumeDb = SoundSynth.BaseVolumeDb(Sound.Knock);
        _preview.Play();
    }

    private AudioStreamPlayer NextVoice()
    {
        foreach (var v in _voices)
            if (!v.Playing) return v;
        if (_voices.Count < MaxVoices)
        {
            var voice = new AudioStreamPlayer { Bus = BusName };
            AddChild(voice);
            _voices.Add(voice);
            return voice;
        }
        // all busy: take the voices over in turn
        _nextVoice = (_nextVoice + 1) % _voices.Count;
        return _voices[_nextVoice];
    }
}
