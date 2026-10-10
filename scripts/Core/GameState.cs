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
    private int _storyAct = 1;

    public IReadOnlyList<string> Inventory => _inventory;
    public IReadOnlyCollection<string> Flags => _flags;
    public int StoryAct => _storyAct;

    public override void _EnterTree() => Instance = this;

    public bool HasFlag(string flag) => _flags.Contains(flag);

    public void SetFlag(string flag, bool value = true)
    {
        if (value ? _flags.Add(flag) : _flags.Remove(flag))
            EmitSignal(SignalName.Changed);
    }

    public void SetStoryAct(int act)
    {
        act = Mathf.Clamp(act, 1, 3);
        if (_storyAct == act) return;
        _storyAct = act;
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

    public void Reset() => Restore(new[] { PuzzleMigration.SchemaFlag }, System.Array.Empty<string>(), 1);

    /// <summary>Copies flags, inventory and act into a save.</summary>
    public void CaptureInto(SaveData data)
    {
        data.Flags = new List<string>(_flags);
        data.Flags.Sort(System.StringComparer.Ordinal);
        data.Inventory = new List<string>(_inventory);
        data.StoryAct = _storyAct;
    }

    /// <summary>Replaces the whole state at once, emitting <see cref="Changed"/> a single time.</summary>
    public void Restore(IEnumerable<string> flags, IEnumerable<string> inventory, int storyAct)
    {
        _flags.Clear();
        _flags.UnionWith(flags);
        _inventory.Clear();
        foreach (var id in inventory)
            if (!_inventory.Contains(id)) _inventory.Add(id);
        _storyAct = Mathf.Clamp(storyAct, 1, 3);
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
