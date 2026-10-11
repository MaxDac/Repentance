using Godot;
using System;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Awaited action strips with contact and speech points independent of the texture rectangle.</summary>
public sealed class PosePlayback
{
    public sealed class FrameData
    {
        [JsonPropertyName("anchor")] public required float[] Anchor { get; init; }
        [JsonPropertyName("head")] public required float[] Head { get; init; }
        [JsonPropertyName("bounds")] public required float[] Bounds { get; init; }
        [JsonPropertyName("seconds")] public double Seconds { get; init; }
    }

    public sealed class ClipData
    {
        [JsonPropertyName("width")] public int Width { get; init; }
        [JsonPropertyName("height")] public int Height { get; init; }
        [JsonPropertyName("frames")] public required FrameData[] Frames { get; init; }
    }

    /// <summary>Autoplay observes each displayed frame, holding it until its capture has finished.</summary>
    public static Func<PosePlayback, Task>? FrameObserver;

    private readonly Sprite2D _sprite;
    private ClipData? _clip;
    private TaskCompletionSource<bool>? _done;
    private Task? _observation;
    private double _elapsed;
    private bool _flipped;

    public PosePlayback(Sprite2D sprite) => _sprite = sprite;
    public string? Action { get; private set; }
    public int Frame { get; private set; }
    public int FrameCount => _clip?.Frames.Length ?? 0;
    public bool Active => _clip != null;
    public bool Playing => _done != null;
    private FrameData Current => _clip!.Frames[Frame];
    private Vector2 Mirror(float[] point) => new(_flipped ? _clip!.Width - point[0] : point[0], point[1]);
    public Vector2 HeadOffset => Mirror(Current.Head) - Mirror(Current.Anchor);
    public Rect2 Bounds
    {
        get
        {
            var b = Current.Bounds;
            var x = _flipped ? _clip!.Width - b[0] - b[2] : b[0];
            return new Rect2(new Vector2(x, b[1]) - Mirror(Current.Anchor), new Vector2(b[2], b[3]));
        }
    }

    public bool Flipped
    {
        set
        {
            _flipped = value;
            if (Active) Apply();
        }
    }

    private void Load(string name, bool flipped)
    {
        Clear();
        var path = $"res://assets/art/sprites/{name}";
        var json = Godot.FileAccess.GetFileAsString($"{path}.json");
        var clip = JsonSerializer.Deserialize<ClipData>(json)
            ?? throw new InvalidOperationException($"Invalid pose metadata: {name}");
        var texture = GD.Load<Texture2D>($"{path}.png")
            ?? throw new InvalidOperationException($"Missing pose texture: {name}");
        if (clip.Width <= 0 || clip.Height <= 0 || clip.Frames.Length == 0
            || texture.GetWidth() != clip.Width * clip.Frames.Length || texture.GetHeight() != clip.Height)
            throw new InvalidOperationException($"Pose dimensions do not match metadata: {name}");
        foreach (var frame in clip.Frames)
        {
            if (frame.Anchor.Length != 2 || frame.Head.Length != 2 || frame.Bounds.Length != 4
                || !double.IsFinite(frame.Seconds) || frame.Seconds <= 0)
                throw new InvalidOperationException($"Invalid frame metadata: {name}");
            foreach (var values in new[] { frame.Anchor, frame.Head, frame.Bounds })
                foreach (var number in values)
                    if (!float.IsFinite(number)) throw new InvalidOperationException($"Non-finite pose point: {name}");
        }
        _clip = clip;
        Action = name;
        _flipped = flipped;
        Frame = 0;
        _elapsed = 0;
        _sprite.Texture = texture;
        _sprite.Hframes = clip.Frames.Length;
        _sprite.Vframes = 1;
        Apply();
    }

    public void Hold(string name, bool flipped = false, bool last = false)
    {
        Load(name, flipped);
        if (last) { Frame = FrameCount - 1; Apply(); }
    }

    public Task<bool> Play(string name, bool flipped = false)
    {
        Load(name, flipped);
        _done = new TaskCompletionSource<bool>();
        Observe();
        return _done.Task;
    }

    private void Apply()
    {
        _sprite.Offset = -Mirror(Current.Anchor);
        _sprite.FlipH = _flipped;
        _sprite.Frame = Frame;
    }

    private void Observe() => _observation = FrameObserver?.Invoke(this);

    public void Process(double delta)
    {
        if (_done == null) return;
        if (_observation != null)
        {
            if (!_observation.IsCompleted) return;
            if (!_observation.IsCompletedSuccessfully)
            {
                var error = _observation.Exception?.GetBaseException()
                    ?? new InvalidOperationException("Pose frame observation was cancelled.");
                GD.PushError(error.ToString());
                _done.TrySetException(error);
                _done = null;
                return;
            }
            _observation = null;
        }
        _elapsed += delta;
        while (_done != null && _elapsed >= Current.Seconds)
        {
            _elapsed -= Current.Seconds;
            if (Frame == FrameCount - 1)
            {
                var done = _done;
                _done = null;
                done.TrySetResult(true);
                return;
            }
            Frame++;
            Apply();
            Observe();
            if (_observation != null) return;
        }
    }

    public void Clear()
    {
        var done = _done;
        _done = null;
        _clip = null;
        _observation = null;
        Action = null;
        done?.TrySetResult(false);
    }
}
