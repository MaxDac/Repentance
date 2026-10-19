using System;
using System.Threading.Tasks;
using Godot;

namespace Repentance;

/// <summary>
/// A thunderstorm seen through a window in a blacked-out room. This node holds the room painted under the flash (a lit
/// background and its overlays as children) and stays hidden while it's dark; a strike shows it for a blink, hides the
/// dark painting (<see cref="DarkPath"/>) meanwhile, washes the characters (<see cref="TintPath"/>) from a near
/// silhouette to cold white, and the thunder follows a moment later. While <see cref="Ambient"/> it strikes by itself
/// every few seconds; scripted strikes (<see cref="Strike"/>) can flash more than once and show something on each.
/// </summary>
[GlobalClass]
public partial class Lightning : Node2D
{
    [Export] public NodePath DarkPath = "../Dark";
    [Export] public NodePath TintPath = "../World";
    [Export] public Color DarkTint = new(0.3f, 0.32f, 0.46f);
    [Export] public Color LitTint = new(0.84f, 0.88f, 1f);
    [Export] public float MinGap = 7f;
    [Export] public float MaxGap = 14f;
    [Export] public float FlashTime = 0.1f;
    [Export] public float ThunderDelay = 0.7f;
    [Export] public int Seed = 5;

    /// <summary>Whether it strikes on its own, at random gaps of <see cref="MinGap"/> to <see cref="MaxGap"/> seconds.</summary>
    public bool Ambient = true;

    /// <summary>Whether the room is lit by a flash right now.</summary>
    public bool Lit => Visible;

    /// <summary>How many times the thunder has rolled since the room loaded.</summary>
    public int Thunders { get; private set; }

    /// <summary>Whether a strike is flashing right now.</summary>
    public bool Striking => _striking;

    /// <summary>Stops the ambient strikes and waits for one already flashing to go dark.</summary>
    public async Task Hush()
    {
        Ambient = false;
        while (_striking && IsInsideTree()) await Pause(0.05);
    }

    private readonly RandomNumberGenerator _rng = new();
    private double _next;
    private bool _striking;

    public override void _Ready()
    {
        _rng.Seed = (ulong)Seed;
        _next = _rng.RandfRange(MinGap * 0.4f, MinGap);
        SetLit(false);
    }

    public override void _Process(double delta)
    {
        if (!Ambient || _striking) return;
        _next -= delta;
        if (_next > 0) return;
        _next = _rng.RandfRange(MinGap, MaxGap);
        // now and then the sky stutters: two flashes close together
        _ = _rng.Randf() < 0.35f ? Strike(null, null) : Strike();
    }

    /// <summary>
    /// One flash, or one per entry of <paramref name="onFlash"/> with a blink of dark between them; each action runs
    /// as its flash lights the room (and may show something only that flash reveals). Returns once it's dark again;
    /// the thunder rolls in after <see cref="ThunderDelay"/> without being waited for.
    /// </summary>
    public async Task Strike(params Action?[] onFlash)
    {
        if (onFlash.Length == 0) onFlash = new Action?[] { null };
        _striking = true;
        for (int i = 0; i < onFlash.Length; i++)
        {
            if (i > 0) await Pause(FlashTime * 1.4f);
            onFlash[i]?.Invoke();
            SetLit(true);
            await Pause(FlashTime * (i == onFlash.Length - 1 ? 1.6f : 1f));
            SetLit(false);
        }
        _striking = false;
        _ = Thunder();
    }

    private async Task Thunder()
    {
        await Pause(ThunderDelay);
        if (!IsInsideTree()) return;
        Thunders++;
        Game.Instance.Sfx.Play(Sound.Thunder);
    }

    private async Task Pause(double seconds)
    {
        if (!IsInsideTree()) return;
        await Timers.Wait(this, seconds);
    }

    private void SetLit(bool lit)
    {
        if (!IsInsideTree()) return;
        Visible = lit;
        if (GetNodeOrNull<CanvasItem>(DarkPath) is { } dark) dark.Visible = !lit;
        if (GetNodeOrNull<CanvasItem>(TintPath) is { } tint) tint.Modulate = lit ? LitTint : DarkTint;
    }
}
