using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Main scene controller: owns the current room, the player and the HUD, turns clicks into
/// "verb + object" commands and provides the scripting helpers rooms use (Say, WalkTo, ChangeRoom...).
/// </summary>
public partial class Game : Node
{
    public static Game Instance { get; private set; } = null!;

    [Export] public string StartRoom = "office";
    [Export] public string StartEntry = "start";

    public Player Player { get; private set; } = null!;
    public Hud Hud { get; private set; } = null!;
    public Room? Room { get; private set; }

    private Node2D _roomHost = null!;
    private Verb _verb = Verb.WalkTo;
    private string? _item;          // first object of "Use X with" / "Give X to"
    private string? _hoverItem;
    private int _busy;               // > 0 while a scripted sequence runs
    private int _actionId;
    private TaskCompletionSource? _skipSpeech;
    private bool _onTitle;
    private readonly Random _rng = new();

    public bool Busy => _busy > 0;

    public override void _EnterTree() => Instance = this;

    public override async void _Ready()
    {
        _roomHost = new Node2D { Name = "RoomHost" };
        AddChild(_roomHost);
        Player = new Player { Name = "Player" };
        Hud = new Hud { Name = "Hud" };
        AddChild(Hud);
        Hud.VerbClicked += OnVerbClicked;
        Hud.ItemClicked += OnItemClicked;
        Hud.ItemHovered += id => _hoverItem = id;
        Hud.TitleClicked += () => _onTitle = false;

        var args = OS.GetCmdlineUserArgs();
        foreach (var a in args)
        {
            if (a.StartsWith("--room=")) StartRoom = a[7..];
            if (a.StartsWith("--entry=")) StartEntry = a[8..];
        }
        if (Array.IndexOf(args, "--autoplay") >= 0)
        {
            await new AutoPlay().Run(this);
            return;
        }

        if (Array.IndexOf(args, "--skip-title") < 0)
        {
            _onTitle = true;
            Hud.ShowTitle(true);
            await Hud.Fade(0, 0.8);
            while (_onTitle) await Wait(0.05);
            await Hud.Fade(1, 0.5);
            Hud.ShowTitle(false);
        }
        await ChangeRoom(StartRoom, StartEntry);
    }

    // ------------------------------------------------------------------ input

    public override void _UnhandledInput(InputEvent e)
    {
        if (e is not InputEventMouseButton { Pressed: true } mb) return;
        if (mb.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        GetViewport().SetInputAsHandled();

        if (_skipSpeech != null)
        {
            _skipSpeech.TrySetResult();
            return;
        }
        if (Busy || Room == null || _onTitle) return;
        var pos = mb.Position;
        if (pos.Y >= Hud.Top) return;

        var target = Room.HotspotAt(pos);
        if (mb.ButtonIndex == MouseButton.Right)
        {
            _item = null;
            if (target == null) return;
            _ = Execute(DefaultVerb(target), target, null, pos);
        }
        else
        {
            var verb = target == null ? Verb.WalkTo : _verb;
            var item = _item;
            if (verb == Verb.Give && item == null)
            {
                ResetVerb();
                _ = Run(() => Say(Pick("Give what? I should pick something from my pockets first.", "Give what?")));
                return;
            }
            _ = Execute(verb, target, item, pos);
        }
        ResetVerb();
    }

    private static Verb DefaultVerb(Hotspot h) => h switch
    {
        { IsExit: true } => Verb.WalkTo,
        Actor => Verb.TalkTo,
        _ => Verb.LookAt,
    };

    private void OnVerbClicked(Verb v)
    {
        if (Busy) return;
        _verb = v;
        _item = null;
        Hud.HighlightVerb(v);
    }

    private void OnItemClicked(string item, bool right)
    {
        if (_skipSpeech != null) { _skipSpeech.TrySetResult(); return; }
        if (Busy) return;
        if (right || _verb == Verb.LookAt)
        {
            ResetVerb();
            _ = Run(() => Say(Items.Get(item).Description));
            return;
        }
        if (_item != null && Verbs.IsTwoObject(_verb))
        {
            var first = _item;
            ResetVerb();
            if (first == item) return;
            _ = Run(async () =>
            {
                if (Room == null || !await Room.OnCombine(first, item))
                    await Say(Pick("That doesn't work.", "I can't see how those go together."));
            });
            return;
        }
        if (_verb is Verb.WalkTo or Verb.Use or Verb.Give)
        {
            if (_verb == Verb.WalkTo) _verb = Verb.Use;
            _item = item;
            Hud.HighlightVerb(_verb);
            return;
        }
        var verb = _verb;
        ResetVerb();
        _ = Run(() => Say(verb switch
        {
            Verb.PickUp => "I've already got it.",
            Verb.Open => "It doesn't open.",
            Verb.TalkTo => "I'm not that lonely. Yet.",
            _ => "That won't help.",
        }));
    }

    private void ResetVerb()
    {
        _verb = Verb.WalkTo;
        _item = null;
        Hud.HighlightVerb(null);
    }

    public override void _Process(double delta)
    {
        if (Room == null || _onTitle) return;
        if (Busy) { Hud.SetInterfaceVisible(false); return; }
        Hud.SetInterfaceVisible(true);

        var mouse = GetViewport().GetMousePosition();
        string? obj = null;
        if (_hoverItem != null) obj = Items.Get(_hoverItem).Name;
        else if (mouse.Y < Hud.Top) obj = Room.HotspotAt(mouse)?.Title;

        var s = Verbs.Label(_verb);
        if (_item != null)
        {
            s += " " + Items.Get(_item).Name + " " + Verbs.Preposition(_verb);
            if (obj != null && obj != Items.Get(_item).Name) s += " " + obj;
        }
        else if (obj != null) s += " " + obj;
        Hud.SetSentence(s);
    }

    // ------------------------------------------------------------------ command execution

    /// <summary>Performs "verb [item] hotspot" as if the player clicked it (used by the autoplay test).</summary>
    public async Task Perform(Verb verb, string hotspotId, string? item = null)
    {
        var h = Room?.FindHotspot(hotspotId) ?? throw new InvalidOperationException($"No hotspot '{hotspotId}' in {Room?.Name}");
        await Execute(verb, h, item, h.Bounds.GetCenter());
    }

    private async Task Execute(Verb verb, Hotspot? target, string? item, Vector2 point)
    {
        int id = ++_actionId;
        if (target == null)
        {
            await WalkTo(point);
            return;
        }

        var dest = target.WalkTo != Vector2.Zero
            ? target.WalkTo
            : new Vector2(target.Bounds.GetCenter().X, target.Bounds.End.Y + 4);
        bool arrived = await WalkTo(dest);
        if (!arrived || id != _actionId) return;

        if (target.Face != Facing.Auto) Player.Face(target.Face);
        else Player.FaceTowards(target.Bounds.GetCenter());

        await Run(async () =>
        {
            if (Room != null && await Room.OnInteract(verb, target, item)) return;
            if (verb == Verb.WalkTo)
            {
                if (target.IsExit) await ChangeRoom(target.ExitTo, target.ExitEntry);
                return;
            }
            await DefaultResponse(verb, target, item);
        });
    }

    private async Task DefaultResponse(Verb verb, Hotspot target, string? item)
    {
        switch (verb)
        {
            case Verb.LookAt:
                await Say(target.LookText != "" ? target.LookText : $"It's {Article(target.Title)}.");
                break;
            case Verb.Open when target.IsExit:
                await ChangeRoom(target.ExitTo, target.ExitEntry);
                break;
            case Verb.Open:
                await Say(Pick("It doesn't open.", "There's nothing to open."));
                break;
            case Verb.Close:
                await Say(Pick("It doesn't close.", "It's as closed as it gets."));
                break;
            case Verb.PickUp:
                await Say(target is Actor
                    ? "Let's keep our relationship professional."
                    : Pick("I don't need that.", "I'll leave it where it is.", "It's fine where it is."));
                break;
            case Verb.TalkTo:
                await Say(target is Actor ? "They don't seem to want to talk." : Pick("It's not much of a talker.", "I've had better conversations with a lamppost. But not with this."));
                break;
            case Verb.Push:
            case Verb.Pull:
                await Say(Pick("It won't budge.", "Nothing happens.", "I'd only hurt my back."));
                break;
            case Verb.Give when item != null:
                await Say(target is Actor ? "I don't think they'd want that." : "I can't give things to inanimate objects. Not anymore.");
                break;
            case Verb.Use when item != null:
                await Say(Pick("That doesn't work.", "I don't think so."));
                break;
            case Verb.Use:
                await Say(Pick("I can't use that.", "What would I use that for?"));
                break;
            default:
                await Say("Hmm.");
                break;
        }
    }

    private static string Article(string name) =>
        "aeiou".Contains(char.ToLowerInvariant(name[0])) ? "an " + name : "a " + name;

    public string Pick(params string[] options) => options[_rng.Next(options.Length)];

    // ------------------------------------------------------------------ scripting helpers

    /// <summary>Runs a scripted sequence, blocking player input and hiding the verbs while it runs.</summary>
    public async Task Run(Func<Task> sequence)
    {
        _busy++;
        try { await sequence(); }
        catch (Exception ex) { GD.PushError(ex.ToString()); }
        finally { _busy--; }
    }

    public async Task<bool> WalkTo(Vector2 point)
    {
        if (Room == null) return false;
        point = Room.ClampWalkTarget(point);
        var path = Room.Walk?.FindPath(Player.Position, point) ?? new List<Vector2> { point };
        return await Player.WalkPath(path);
    }

    public Task Say(string text) => Say(Player, text);

    public Task Say(string actorId, string text)
    {
        ISpeaker who = actorId.Equals("micah", StringComparison.OrdinalIgnoreCase)
            ? Player
            : (ISpeaker?)Room?.FindActor(actorId.ToLowerInvariant()) ?? Player;
        return Say(who, text);
    }

    public async Task Say(ISpeaker who, string text)
    {
        _skipSpeech = new TaskCompletionSource();
        var skip = _skipSpeech;
        who.Talking = true;
        Hud.ShowSpeech(text, who.HeadPosition, who.SpeechColor);
        var seconds = Math.Clamp(0.9 + text.Length * 0.055, 1.5, 7.0);
        // ignore the click that triggered this line
        await Wait(0.15);
        await Task.WhenAny(Wait(seconds), skip.Task);
        who.Talking = false;
        Hud.HideSpeech();
        if (_skipSpeech == skip) _skipSpeech = null;
        await Wait(0.12);
    }

    public async Task Wait(double seconds)
    {
        var timer = GetTree().CreateTimer(seconds);
        await ToSignal(timer, SceneTreeTimer.SignalName.Timeout);
    }

    public async Task ChangeRoom(string name, string entry)
    {
        _busy++;
        try
        {
            await Hud.Fade(1, 0.35);
            Player.Stop();
            if (Room != null)
            {
                Room.World.RemoveChild(Player);
                Room.QueueFree();
            }
            var scene = GD.Load<PackedScene>($"res://scenes/rooms/{name}.tscn");
            Room = scene.Instantiate<Room>();
            _roomHost.AddChild(Room);
            Room.World.AddChild(Player);
            var marker = Room.GetNodeOrNull<Node2D>($"Entries/{entry}");
            var facing = marker != null && marker.HasMeta("facing") ? (Facing)marker.GetMeta("facing").AsInt32() : Facing.Down;
            Player.Teleport(Room.EntryPoint(entry), facing);
            ResetVerb();
            await Hud.Fade(0, 0.35);
        }
        finally { _busy--; }
        await Room.OnEnter(entry);
    }
}
