using Godot;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Animated pixel rain drawn over a painted background: slanted 1px streaks in parallax layers, clipped to
/// <see cref="Areas"/> (window panes, the sky). Optional droplets running down the glass and splash ticks where
/// drops hit water. Seeded, so recorded frames are reproducible.
/// </summary>
[GlobalClass]
public partial class Rain : Node2D
{
    [Export] public Godot.Collections.Array<Rect2> Areas = new();
    /// <summary>Streaks per 1000 square pixels of area.</summary>
    [Export] public float Density = 3f;
    /// <summary>Fall speed of the nearest layer, pixels per second.</summary>
    [Export] public float Speed = 280f;
    /// <summary>Horizontal pixels per pixel of fall (negative leans the rain left).</summary>
    [Export] public float Slant = -0.25f;
    [Export] public int Length = 5;
    [Export] public int Layers = 2;
    [Export] public Color Tint = new(0.62f, 0.7f, 0.88f, 0.55f);
    /// <summary>Droplets slowly running down the glass.</summary>
    [Export] public int Drips;
    [Export] public Color DripTint = new(0.78f, 0.84f, 0.96f, 0.8f);
    /// <summary>Areas where drops splash (a river, a puddle); splashes per second per 1000 square pixels.</summary>
    [Export] public Godot.Collections.Array<Rect2> SplashAreas = new();
    [Export] public float SplashRate = 6f;
    [Export] public int Seed = 1;
    /// <summary>
    /// Scales the authored (Act 1) density, speed and length to the story act's <see cref="RainWeather"/>, so it
    /// builds to a downpour by Act 3. Off for the title screen.
    /// </summary>
    [Export] public bool FollowsStory = true;

    private struct Drop { public int Area, Layer; public float X, Y; }
    private struct Drip { public int Area; public float X, Y, Speed, Pause; }
    private struct Splash { public Vector2I At; public float Age; }

    private readonly List<Drop> _drops = new();
    private readonly List<Drip> _drips = new();
    private readonly List<Splash> _splashes = new();
    private RandomNumberGenerator _rng = new();
    private float _splashDebt;

    private const float SplashLife = 0.16f;

    public override void _Ready()
    {
        _rng.Seed = (ulong)Seed;
        if (FollowsStory && GameState.Instance != null)
        {
            var weather = RainWeather.ForAct(GameState.Instance.StoryAct);
            Density *= weather.Density;
            Speed *= weather.Speed;
            Length += weather.ExtraLength;
            SplashRate *= weather.Density;
        }
        if (Areas.Count == 0)
            Areas.Add(new Rect2(0, 0, 480, 270));
        for (int a = 0; a < Areas.Count; a++)
        {
            var r = Areas[a];
            int n = Mathf.Max(1, Mathf.RoundToInt(r.Size.X * r.Size.Y * Density / 1000f));
            for (int i = 0; i < n; i++)
            {
                var d = new Drop { Area = a, Layer = i % Mathf.Max(1, Layers) };
                Respawn(ref d, r.Position.Y + _rng.RandfRange(0, r.Size.Y + Length));
                _drops.Add(d);
            }
        }
        for (int i = 0; i < Drips && Areas.Count > 0; i++)
        {
            var d = new Drip { Area = i % Areas.Count };
            var r = Areas[d.Area];
            ResetDrip(ref d, r.Position.Y + _rng.RandfRange(0, r.Size.Y));
            _drips.Add(d);
        }
    }

    /// <summary>Layer 0 is the farthest: dimmer, shorter and slower.</summary>
    private float Depth(int layer) => Layers <= 1 ? 1f : (layer + 1f) / Layers;

    private void Respawn(ref Drop d, float y)
    {
        var r = Areas[d.Area];
        // spawn across the width the slant will sweep through, so the edges stay covered
        float sweep = -Slant * r.Size.Y;
        d.X = _rng.RandfRange(r.Position.X + Mathf.Min(0, sweep), r.End.X + Mathf.Max(0, sweep));
        d.Y = y;
    }

    private void ResetDrip(ref Drip d, float y)
    {
        var r = Areas[d.Area];
        d.X = Mathf.Floor(_rng.RandfRange(r.Position.X + 1, r.End.X - 1));
        d.Y = y;
        d.Speed = _rng.RandfRange(4f, 14f);
        d.Pause = _rng.RandfRange(0f, 1.5f);
    }

    public override void _Process(double delta)
    {
        float dt = (float)delta;
        for (int i = 0; i < _drops.Count; i++)
        {
            var d = _drops[i];
            var r = Areas[d.Area];
            float dy = Speed * (0.55f + 0.45f * Depth(d.Layer)) * dt;
            d.Y += dy;
            d.X += Slant * dy;
            if (d.Y - Length > r.End.Y) Respawn(ref d, r.Position.Y - _rng.RandfRange(0, 12));
            _drops[i] = d;
        }
        for (int i = 0; i < _drips.Count; i++)
        {
            var d = _drips[i];
            if (d.Pause > 0) d.Pause -= dt;
            else
            {
                d.Y += d.Speed * dt;
                // water runs in stops and starts
                if (_rng.Randf() < dt * 0.8f) d.Pause = _rng.RandfRange(0.3f, 1.8f);
            }
            if (d.Y > Areas[d.Area].End.Y + 2) ResetDrip(ref d, Areas[d.Area].Position.Y);
            _drips[i] = d;
        }
        for (int i = _splashes.Count - 1; i >= 0; i--)
        {
            var s = _splashes[i];
            s.Age += dt;
            if (s.Age >= SplashLife) _splashes.RemoveAt(i);
            else _splashes[i] = s;
        }
        foreach (var r in SplashAreas)
        {
            _splashDebt += r.Size.X * r.Size.Y * SplashRate / 1000f * dt;
            while (_splashDebt >= 1f)
            {
                _splashDebt -= 1f;
                _splashes.Add(new Splash
                {
                    At = new Vector2I((int)_rng.RandfRange(r.Position.X + 1, r.End.X - 1),
                        (int)_rng.RandfRange(r.Position.Y + 1, r.End.Y)),
                });
            }
        }
        QueueRedraw();
    }

    private void Dot(Rect2 clip, float x, float y, Color c)
    {
        var p = new Vector2(Mathf.Floor(x), Mathf.Floor(y));
        if (p.X < clip.Position.X || p.Y < clip.Position.Y || p.X >= clip.End.X || p.Y >= clip.End.Y) return;
        DrawRect(new Rect2(p, Vector2.One), c);
    }

    public override void _Draw()
    {
        foreach (var d in _drops)
        {
            var r = Areas[d.Area];
            float depth = Depth(d.Layer);
            int len = Mathf.Max(1, Mathf.RoundToInt(Length * (0.5f + 0.5f * depth)));
            var c = Tint with { A = Tint.A * (0.45f + 0.55f * depth) };
            for (int k = 0; k < len; k++)
            {
                // the head is brightest, the tail fades out
                var ck = c with { A = c.A * (1f - 0.5f * k / len) };
                Dot(r, d.X - Slant * k, d.Y - k, ck);
            }
        }
        foreach (var d in _drips)
        {
            var r = Areas[d.Area];
            Dot(r, d.X, d.Y, DripTint);
            Dot(r, d.X, d.Y - 1, DripTint with { A = DripTint.A * 0.5f });
            Dot(r, d.X, d.Y - 2, DripTint with { A = DripTint.A * 0.25f });
        }
        foreach (var s in _splashes)
        {
            var c = Tint with { A = Tint.A * (1f - s.Age / SplashLife) };
            var p = (Vector2)s.At;
            if (s.Age < SplashLife * 0.5f) DrawRect(new Rect2(p, Vector2.One), c);
            else
            {
                DrawRect(new Rect2(p + new Vector2(-1, -1), Vector2.One), c);
                DrawRect(new Rect2(p + new Vector2(1, -1), Vector2.One), c);
            }
        }
    }
}
