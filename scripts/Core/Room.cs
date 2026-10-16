using Godot;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Base class for a room. Expected scene layout:
/// <code>
/// Room (this script or a subclass)
///   Background   Sprite2D (480x270, Centered off)
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
    /// <summary>Sprite sheet / speaker the player uses in this room ("micah" or "daniel").</summary>
    [Export] public string PlayerCharacter = "micah";
    /// <summary>False for screens like the city map, where the player character isn't drawn.</summary>
    [Export] public bool ShowPlayer = true;
    /// <summary>What footsteps sound like here.</summary>
    [Export] public FloorSurface Floor = FloorSurface.Wood;

    /// <summary>
    /// The looping ambience and its level in dB: rain wherever it is drawn, loud when the room is out in it, muffled
    /// when it only runs down a window.
    /// </summary>
    public virtual (Sound Sound, float VolumeDb)? Ambience
    {
        get
        {
            var rain = FindAll<Rain>(this).ToList();
            if (rain.Count == 0) return null;
            bool outside = rain.Any(r => r.Areas.Count == 0 || r.Areas.Sum(a => a.Area) > 480 * 270 * 0.3f);
            return (Sound.Rain, outside ? 0f : -9f);
        }
    }

    /// <summary>The background music that loops here; the same track carries on uninterrupted between rooms that share it.</summary>
    public virtual Track? Music => null;

    /// <summary>Whether the player is drawn when the room loads; rooms can hide him for an entry cutscene.</summary>
    public virtual bool PlayerVisibleOnLoad => ShowPlayer;

    /// <summary>
    /// The sheet the player actually wears here: Eleanor during the interludes and her coda (see
    /// <see cref="Story.Interlude.PlayerSheet"/>); otherwise Micah goes masked and cloaked while "masked" is set,
    /// and without his tie once he's left it on the Harrington mansion's alarm bell ("bell_wedged").
    /// </summary>
    public virtual string ResolvePlayerCharacter()
    {
        if (Story.Interlude.PlayerSheet(Game.RoomScene, GameState.Instance.HasFlag) is { } eleanor) return eleanor;
        return PlayerCharacter switch
        {
            "micah" when GameState.Instance.HasFlag("masked") => "micah_masked",
            "micah" when GameState.Instance.HasFlag("bell_wedged") => "micah_no_tie",
            _ => PlayerCharacter,
        };
    }

    public WalkArea? Walk { get; private set; }
    public Node2D World { get; private set; } = null!;

    protected Game Game => Game.Instance;
    protected GameState State => GameState.Instance;

    /// <summary>True when <paramref name="item"/> is the physical prop, or Micah's notepad once the matching note is written.</summary>
    protected bool Shows(string? item, string physical, string note) =>
        item == physical || (item == Notes.ItemId && Notes.Known(note, State.HasFlag));
    protected Player Player => Game.Player;

    protected Task Say(string text) => Game.Say(text);
    protected Task Say(string actorId, string text) => Game.Say(actorId, text);
    /// <summary>The player speaks under her breath (see <see cref="Game.Whisper"/>).</summary>
    protected Task Whisper(string text) => Game.Whisper(text);
    /// <summary>Micah's journal narration at the top of the screen (see <see cref="Game.Think"/>).</summary>
    protected Task Think(string text) => Game.Think(text);
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

    /// <summary>An actor or an off-screen <see cref="Voice"/> with this id.</summary>
    public ISpeaker? FindSpeaker(string id) =>
        (ISpeaker?)FindActor(id) ?? FindAll<Voice>(this).FirstOrDefault(v => v.Id == id);

    public Hotspot? FindHotspot(string id) => Hotspots.FirstOrDefault(h => h.Id == id);

    /// <summary>The verb a left click performs on a hotspot here, or null for the game-wide default.</summary>
    public virtual Verb? LeftClickVerb(Hotspot h) => null;

    /// <summary>
    /// The topmost active hotspot under a point. A character drawn over the point is in front of the scenery, so it
    /// wins (the frontmost, by feet position, if several overlap); otherwise click priority, then the smallest area.
    /// </summary>
    public Hotspot? HotspotAt(Vector2 p)
    {
        var drawn = Hotspots.OfType<Actor>().Where(a => a.DrawnAt(p)).OrderByDescending(a => a.GlobalPosition.Y).FirstOrDefault();
        return drawn ?? Hotspots.Where(h => h.Visible && h.Contains(p))
            .OrderByDescending(h => h.ClickPriority).ThenBy(h => h.Bounds.Area).FirstOrDefault();
    }

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

    /// <summary>Called after a <see cref="Recipes"/> combination made <paramref name="result"/> and its line was spoken.</summary>
    public virtual Task OnCombined(string result) => Task.CompletedTask;

    /// <summary>Handle a wheel verb on an inventory item (e.g. Hand on a journal = read it). Look falls back to the description.</summary>
    public virtual Task<bool> OnItemVerb(Verb verb, string item) => Task.FromResult(false);

    /// <summary>Runs a "CUE: name" line from Ink: stage business the room plays in the middle of a conversation.</summary>
    public virtual Task OnCue(string cue) => Task.CompletedTask;

    private static IEnumerable<T> FindAll<T>(Node root) where T : Node
    {
        foreach (var child in root.GetChildren())
        {
            if (child is T t) yield return t;
            foreach (var d in FindAll<T>(child)) yield return d;
        }
    }
}
