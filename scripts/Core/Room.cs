using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Base class for a room. Expected scene layout:
/// <code>
/// Room (this script or a subclass)
///   Background   Sprite2D (480x200, Centered off)
///   WalkArea     Polygon2D - walkable floor (hidden at runtime)
///   Entries      Node2D with Marker2D children (entry names)
///   Hotspots     Node2D with Hotspot children (each with CollisionShape2D/Polygon2D)
///   World        Node2D, y-sorted: Actors, foreground props, and the player get placed here
/// </code>
/// Override <see cref="OnEnter"/> and <see cref="OnInteract"/> to script the room.
/// </summary>
[GlobalClass]
public partial class Room : Node2D
{
    /// <summary>Character scale at <see cref="FarY"/> (top of the floor) and at <see cref="NearY"/>.</summary>
    [Export] public float FarScale = 0.86f;
    [Export] public float NearScale = 1.0f;
    [Export] public float FarY = 130;
    [Export] public float NearY = 198;
    [Export] public string RoomName = "";

    public WalkArea? Walk { get; private set; }
    public Node2D World { get; private set; } = null!;

    protected Game Game => Game.Instance;
    protected GameState State => GameState.Instance;
    protected Player Player => Game.Player;

    protected Task Say(string text) => Game.Say(text);
    protected Task Say(string actorId, string text) => Game.Say(actorId, text);
    protected Task Talk(string knot) => DialogueManager.Instance.Talk(knot);
    protected Task Wait(double seconds) => Game.Wait(seconds);

    public override void _Ready()
    {
        if (GetNodeOrNull<Polygon2D>("WalkArea") is { } wa)
        {
            var pts = wa.Polygon.Select(p => wa.Transform * p).ToArray();
            Walk = new WalkArea(pts);
            wa.Visible = false;
        }
        World = GetNodeOrNull<Node2D>("World") ?? this;
        World.YSortEnabled = true;
        GameState.Instance.Changed += Refresh;
        Refresh();
    }

    public override void _ExitTree()
    {
        if (GameState.Instance != null) GameState.Instance.Changed -= Refresh;
    }

    public float ScaleAt(float y) =>
        Mathf.Lerp(FarScale, NearScale, Mathf.Clamp((y - FarY) / (NearY - FarY), 0, 1));

    public Vector2 EntryPoint(string name)
    {
        var m = GetNodeOrNull<Node2D>($"Entries/{name}") ?? GetNodeOrNull<Node2D>("Entries")?.GetChildOrNull<Node2D>(0);
        return m?.Position ?? new Vector2(240, 180);
    }

    public IEnumerable<Hotspot> Hotspots => FindAll<Hotspot>(this);

    public Actor? FindActor(string id) => FindAll<Actor>(this).FirstOrDefault(a => a.Id == id);

    public Hotspot? FindHotspot(string id) => Hotspots.FirstOrDefault(h => h.Id == id);

    /// <summary>The topmost active hotspot under a point.</summary>
    public Hotspot? HotspotAt(Vector2 p) => Hotspots
        .Where(h => h.Visible && h.Contains(p))
        .OrderByDescending(h => h.ClickPriority)
        .ThenBy(h => h.Bounds.Area)
        .FirstOrDefault();

    /// <summary>Re-evaluates flag-driven visibility. Called automatically when the game state changes.</summary>
    public void Refresh()
    {
        foreach (var h in Hotspots) h.Visible = FlagRules.Evaluate(h.ShowIfFlags, h.HideIfFlags);
        foreach (var s in FindAll<FlagSprite>(this)) s.Refresh();
        OnRefresh();
    }

    /// <summary>Lets a room restrict where the player may walk (e.g. a doorman blocking the way).</summary>
    public virtual Vector2 ClampWalkTarget(Vector2 target) => target;

    protected virtual void OnRefresh() { }

    /// <summary>Called after the room fades in. <paramref name="entry"/> is the entry marker used.</summary>
    public virtual Task OnEnter(string entry) => Task.CompletedTask;

    /// <summary>
    /// Handle a verb on a hotspot. <paramref name="item"/> is the inventory item for "Use X with"/"Give X to".
    /// Return false to fall back to the default responses.
    /// </summary>
    public virtual Task<bool> OnInteract(Verb verb, Hotspot target, string? item) => Task.FromResult(false);

    /// <summary>Handle "Use item with other item" inside the inventory.</summary>
    public virtual Task<bool> OnCombine(string item, string other) => Task.FromResult(false);

    private static IEnumerable<T> FindAll<T>(Node root) where T : Node
    {
        foreach (var child in root.GetChildren())
        {
            if (child is T t) yield return t;
            foreach (var d in FindAll<T>(child)) yield return d;
        }
    }
}
