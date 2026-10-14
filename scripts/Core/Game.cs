using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Main scene controller: owns the current room, the player and the HUD, turns clicks (left = walk /
/// default action, right = verb wheel, held inventory item = use it) into commands and provides the
/// scripting helpers rooms use (Say, WalkTo, ChangeRoom...).
/// </summary>
public partial class Game : Node
{
    public static Game Instance { get; private set; } = null!;

    [Export] public string StartRoom = "attic";
    [Export] public string StartEntry = "start";
    private readonly List<string> _startFlags = new();

    public Player Player { get; private set; } = null!;
    public Hud Hud { get; private set; } = null!;
    public Room? Room { get; private set; }
    public GameSettings Settings { get; private set; } = null!;
    public Sfx Sfx { get; private set; } = null!;

    private Node2D _roomHost = null!;
    private string? _carried;
    private string? _hoverItem;
    private int _busy;               // > 0 while a scripted sequence runs
    private int _actionId;
    private TaskCompletionSource? _skipSpeech;
    private bool _onTitle;
    private string _roomScene = "";
    private double _playtime;
    private bool _autosavePending;
    private TaskCompletionSource? _resume;
    private readonly Random _rng = new();

    public bool Busy => _busy > 0;

    public override void _EnterTree() => Instance = this;

    public override void _Process(double delta)
    {
        if (Room == null || _onTitle) return;
        _playtime += delta;
        if (Busy) { Hud.SetInterfaceVisible(false); return; }
        Hud.SetInterfaceVisible(true);

        if (_autosavePending)
        {
            _autosavePending = false;
            if (AutosaveEnabled) SaveToSlot(SaveSystem.AutosaveSlot);
        }

        var mouse = Hud.MousePos;
        if (Hud.Wheel.IsOpen) { Hud.SetHover(null, mouse); return; }
        string? obj = null;
        Hotspot? spot = null;
        if (_hoverItem != null) obj = Items.Get(_hoverItem).Name;
        else if (!Hud.InventoryOpen && (spot = Room.HotspotAt(mouse)) != null) obj = spot.Title;

        string? text = obj;
        if (_carried != null)
        {
            var name = Items.Get(_carried).Name;
            text = obj == null || obj == name ? null
                : spot is Actor ? $"Give {name} to {obj}" : $"Use {name} with {obj}";
        }
        Hud.SetHover(text, mouse);
    }
}
