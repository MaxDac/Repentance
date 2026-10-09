using Godot;
using System.Collections.Generic;

namespace Repentance;

/// <summary>Global game state: story flags and the player's inventory. Autoloaded as "GameState".</summary>
public partial class GameState : Node
{
    public static GameState Instance { get; private set; } = null!;

    [Signal] public delegate void ChangedEventHandler();

    private readonly HashSet<string> _flags = new();
    private readonly List<string> _inventory = new();

    public IReadOnlyList<string> Inventory => _inventory;

    public override void _EnterTree() => Instance = this;

    public bool HasFlag(string flag) => _flags.Contains(flag);

    public void SetFlag(string flag, bool value = true)
    {
        if (value ? _flags.Add(flag) : _flags.Remove(flag))
            EmitSignal(SignalName.Changed);
    }

    public bool HasItem(string id) => _inventory.Contains(id);

    public void GiveItem(string id)
    {
        if (_inventory.Contains(id)) return;
        _inventory.Add(id);
        EmitSignal(SignalName.Changed);
    }

    public void TakeItem(string id)
    {
        if (_inventory.Remove(id))
            EmitSignal(SignalName.Changed);
    }

    public void Reset()
    {
        _flags.Clear();
        _inventory.Clear();
        EmitSignal(SignalName.Changed);
    }
}

/// <summary>Evaluates comma-separated flag conditions used by hotspots and flag sprites.</summary>
public static class FlagRules
{
    public static bool Evaluate(string showIfFlags, string hideIfFlags)
    {
        var gs = GameState.Instance;
        foreach (var f in Split(showIfFlags))
            if (!gs.HasFlag(f)) return false;
        foreach (var f in Split(hideIfFlags))
            if (gs.HasFlag(f)) return false;
        return true;
    }

    private static IEnumerable<string> Split(string s)
    {
        if (string.IsNullOrWhiteSpace(s)) yield break;
        foreach (var part in s.Split(','))
        {
            var t = part.Trim();
            if (t.Length > 0) yield return t;
        }
    }
}
