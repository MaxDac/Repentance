using Godot;
using System;
using System.Collections.Generic;
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
    public bool IsPaused => _resume != null;

    public void TogglePause()
    {
        if (Room == null || _onTitle || Hud.TitleVisible || Hud.Menu.IsOpen) return;
        if (!IsPaused && GetTree().Paused) return;
        var resume = _resume;
        _resume = resume == null ? new TaskCompletionSource() : null;
        Hud.ShowPause(IsPaused);
        GetTree().Paused = IsPaused;
        resume?.TrySetResult();
    }

    public Task WaitUntilResumed() => _resume?.Task ?? Task.CompletedTask;

    /// <summary>Writes the autosave slot after every room change (turned off by tests that don't want it).</summary>
    public bool AutosaveEnabled { get; set; } = true;

    /// <summary>Saving is only allowed between actions, when no script, dialogue or fade is running.</summary>
    public bool CanSave => Room != null && !Busy && !_onTitle;

    public static string RoomScenePath(string room) => $"res://scenes/rooms/{room}.tscn";

    public override void _EnterTree() => Instance = this;

    public override async void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        bool settingsTest = Array.IndexOf(args, "--settings-test") >= 0;
        bool pauseTest = Array.IndexOf(args, "--pause-test") >= 0;
        Settings = new GameSettings(settingsTest || pauseTest || Array.IndexOf(args, "--autoplay") >= 0
            ? "user://autoplay_settings.cfg" : "user://settings.cfg");
        Settings.Load();
        _roomHost = new Node2D { Name = "RoomHost" };
        AddChild(_roomHost);
        Player = new Player { Name = "Player" };
        Hud = new Hud { Name = "Hud" };
        AddChild(Hud);
        Hud.BindSettings(Settings);
        Hud.ItemClicked += OnItemClicked;
        Hud.ItemHovered += id => _hoverItem = id;

        foreach (var a in args)
        {
            if (a.StartsWith("--room=")) StartRoom = a[7..];
            if (a.StartsWith("--entry=")) StartEntry = a[8..];
            if (a.StartsWith("--flag=")) _startFlags.AddRange(a[7..].Split(',', StringSplitOptions.RemoveEmptyEntries));
        }
        if (pauseTest)
        {
            await new AutoPlay().RunPauseTests(this);
            return;
        }
        if (settingsTest || Array.IndexOf(args, "--autoplay") >= 0)
        {
            await new AutoPlay().Run(this);
            return;
        }

        if (Array.IndexOf(args, "--skip-title") < 0) await TitleScreen();
        else await NewGame();
    }

    private async Task TitleScreen()
    {
        _onTitle = true;
        Hud.ShowTitle(true);
        await Hud.Fade(0, 0.8);
        var choice = await Hud.Menu.OpenTitle();
        await Hud.Fade(1, 0.5);
        Hud.ShowTitle(false);
        _onTitle = false;
        if (choice is { Action: MenuAction.Load, Save: { } save }) await LoadGame(save);
        else await NewGame();
    }

    // ------------------------------------------------------------------ input

    /// <summary>Inventory item currently held as the mouse cursor (left click a hotspot to use it there).</summary>
    public string? Carried => _carried;

    public override void _UnhandledInput(InputEvent e)
    {
        if (IsPaused) return;
        if (e.IsActionPressed("ui_cancel"))
        {
            GetViewport().SetInputAsHandled();
            if (Hud.Wheel.IsOpen) Hud.Wheel.Close();
            else if (CanSave && !Hud.Menu.IsOpen) _ = PauseMenu();
            return;
        }
        if (e.IsActionPressed("toggle_inventory") && e is not InputEventKey { Echo: true })
        {
            GetViewport().SetInputAsHandled();
            if (Room != null && !_onTitle && !Hud.Menu.IsOpen && !Hud.Puzzle.IsOpen && !Hud.Wheel.IsOpen &&
                Hud.InterfaceVisible)
                Hud.ShowInventory(!Hud.InventoryOpen);
            return;
        }
        if (e is not InputEventMouseButton { Pressed: true } mb) return;
        if (mb.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        GetViewport().SetInputAsHandled();

        if (_skipSpeech != null)
        {
            _skipSpeech.TrySetResult();
            return;
        }
        if (Busy || Room == null || _onTitle || Hud.Wheel.IsOpen) return;
        var pos = mb.Position;
        var target = Room.HotspotAt(pos);

        if (mb.ButtonIndex == MouseButton.Right)
        {
            if (_carried != null) { SetCarried(null); return; }
            if (target != null) _ = OpenWheel(target, pos);
            return;
        }
        if (_carried != null && target != null)
        {
            var item = _carried;
            SetCarried(null);
            _ = Execute(Verb.UseItem, target, item, pos);
            return;
        }
        _ = Execute(target == null ? Verb.Walk : DefaultVerb(target), target, null, pos);
    }

    /// <summary>Left click on a hotspot: exits are walked through, people are talked to, the rest is looked at.</summary>
    private static Verb DefaultVerb(Hotspot h) => h switch
    {
        { IsExit: true } => Verb.Walk,
        Actor => Verb.Talk,
        _ => Verb.Look,
    };

    private async Task OpenWheel(Hotspot target, Vector2 pos)
    {
        var verb = await Hud.Wheel.Open(pos, target.Title);
        if (verb is { } v && !Busy && Room != null && target.Visible) await Execute(v, target, null, pos);
    }

    private void SetCarried(string? item)
    {
        _carried = item;
        Hud.SetCursorItem(item);
    }

    private async void OnItemClicked(string item, bool right, Vector2 pos)
    {
        if (IsPaused) return;
        if (_skipSpeech != null) { _skipSpeech.TrySetResult(); return; }
        if (Busy || Hud.Wheel.IsOpen) return;
        if (right)
        {
            SetCarried(null);
            if (await Hud.Wheel.Open(pos, Items.Get(item).Name) is { } verb) await ItemVerb(verb, item);
            return;
        }
        if (_carried == null)
        {
            SetCarried(item);
            Hud.ShowInventory(false);
            return;
        }
        var first = _carried;
        SetCarried(null);
        if (first == item) return;
        await Run(async () =>
        {
            if (!await CombineItems(first, item) && (Room == null || !await Room.OnCombine(first, item)))
                await Say(Pick("That doesn't work.", "I can't see how those go together."));
        });
    }

    private async Task<bool> CombineItems(string first, string second)
    {
        var state = GameState.Instance;
        if (Room?.PlayerCharacter != "micah" || !state.HasItem(first) || !state.HasItem(second)) return false;
        if (PuzzleRules.Pair(first, second, "cloth", "mirror_waxed"))
        {
            if (!state.HasFlag("mirror_warmed"))
            {
                await Say("The cloth won't shift cold wax. Gentle warmth first.");
                return true;
            }
            state.TakeItem("mirror_waxed");
            state.TakeItem("cloth");
            state.GiveItem("mirror");
            state.SetFlag("got_mirror");
            await Say("The wax lifts cleanly. I put the borrowed cloth back on the bed.");
            await Hud.ShowImage(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"));
            await Say("Three loops tied in one knot. No beginning, no end. Scratched deep, on purpose.");
            return true;
        }
        if (PuzzleRules.Pair(first, second, "card", "mirror"))
        {
            if (!state.HasFlag("card_warmed"))
            {
                await Say("Blank paper in a mirror is still blank paper.");
                return true;
            }
            state.SetFlag("card_reflected");
            if (!state.HasFlag("read_book"))
                await Say("Words among the ornaments, in no sensible order. I need a guide to those markings.");
            await TryDecodeCard();
            return true;
        }
        if (PuzzleRules.Pair(first, second, "audit_folder", "audit_tracing"))
        {
            await TryReadAccounts();
            return true;
        }
        var outcome = Recipes.Evaluate(first, second, state.HasItem);
        if (outcome == null) return false;
        Recipes.Apply(outcome, id => state.TakeItem(id), id => state.GiveItem(id), id => state.SetFlag(id));
        await Say(outcome.Line);
        return true;
    }

    public async Task TryReadAccounts()
    {
        var state = GameState.Instance;
        if (Room is not Rooms.MansionStudy || state.HasFlag("entered_bedroom"))
        {
            await Say("I need the study desk to lay these out. Once I go through that bedroom door, I won't get another chance.");
            return;
        }
        if (!state.HasItem("audit_folder") || !state.HasItem("audit_tracing"))
        {
            await Say("The numbered accounts need the auditor's index. The other desk drawer might have it.");
            return;
        }
        if (!await Hud.Puzzle.Open(PuzzleKind.Alignment)) return;
        state.TakeItem("audit_folder");
        state.TakeItem("audit_tracing");
        state.GiveItem("documents");
        state.SetFlag("audit_identified");
        state.SetFlag(Endings.TookDocuments);
        await Say("Bank, judge, captain. The index identifies the numbered pocket in the drawer. Inside: signed payment sheets. Names, dates, signatures. Into the coat. Insurance.");
    }

    public async Task TryDecodeCard()
    {
        var state = GameState.Instance;
        if (state.HasFlag("card_decoded") || !state.HasItem("card") || !state.HasItem("mirror") ||
            !PuzzleRules.CipherReady(state.HasFlag("read_book"), state.HasFlag("card_warmed"), state.HasFlag("card_reflected")))
            return;
        if (!await Hud.Puzzle.Open(PuzzleKind.Cipher)) return;
        state.SetFlag("card_decoded");
        state.GiveItem("address");
        state.SetFlag("club_unlocked");
        await Say("Lily, leaf, feather. The Club, 18 W. Hubbard. I copy it onto a slip. A place that doesn't need a name.");
    }

    /// <summary>Applies a wheel verb to an inventory item (also used by the autoplay test).</summary>
    public Task ItemVerb(Verb verb, string item) => Run(async () =>
    {
        if (Room != null && await Room.OnItemVerb(verb, item)) return;
        if (verb == Verb.Hand && item == "brass_box")
        {
            var state = GameState.Instance;
            state.TakeItem("brass_box");
            state.GiveItem("card");
            state.GiveItem("matchbook");
            await Say("The clasp gave with a click. Inside: a calling card, and a matchbook.");
            await Say("A business card, only two letters in it; the same perfume that permeates the whole room, only stronger... hypnotic, even.");
            await Say("I hold it under my nose longer than a man on a job should. Get a grip, Micah.");
            await Say("The matchbook: a blue lantern on the cover. The Blue Lantern, State Street.");
            await Say("Two big fellas walked her out the back door without a soul seeing. Fellas like that drink somewhere. That's where her trail goes next.");
            return;
        }
        if (verb == Verb.Hand && item == "mirror")
        {
            await Hud.ShowImage(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"));
            await Say("Three loops tied in one knot. No beginning, no end. It looks old. Older than the convent.");
            return;
        }
        if (verb == Verb.Hand && item == "book")
        {
            await Say("Not here. A book like that wants a locked door and a desk lamp. My office has both.");
            return;
        }
        if (item == "card" && GameState.Instance.HasFlag("card_warmed") && verb is Verb.Hand or Verb.Look)
        {
            await Say(GameState.Instance.HasFlag("card_reflected")
                ? "Feather: Hubbard. Lily: The Club. Leaf: 18 W. The book's ornament legend should put them in order."
                : "The ink came up in the warmth, but every letter is backward. A reflection might help.");
            await TryDecodeCard();
            return;
        }
        switch (verb)
        {
            case Verb.Look:
                await Say(item == "dollar"
                    ? $"${CashRules.Balance(GameState.Instance.HasFlag)} in cash. Two dollars for the bellboy; ten for Sal. What's left stays in my pocket."
                    : Items.Get(item).Description);
                break;
            case Verb.Hand:
                Hud.ShowInventory(false);
                SetCarried(item);
                break;
            case Verb.Talk:
                await Say(Pick("I'm not that lonely. Yet.", "It doesn't answer. Thankfully."));
                break;
            default:
                await Say("I'd rather not break my own things.");
                break;
        }
    });

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
            if (verb is Verb.Walk or Verb.Hand && target.IsExit)
            {
                await ChangeRoom(target.ExitTo, target.ExitEntry);
                return;
            }
            if (verb == Verb.Walk) return;
            await DefaultResponse(verb, target, item);
        });
    }

    private async Task DefaultResponse(Verb verb, Hotspot target, string? item)
    {
        bool person = target is Actor;
        switch (verb)
        {
            case Verb.Look:
                await Say(target.LookText != "" ? target.LookText : $"It's {Article(target.Title)}.");
                break;
            case Verb.Hand:
                await Say(person
                    ? "Let's keep our relationship professional."
                    : Pick("I don't need that.", "I'll leave it where it is.", "It's fine where it is.", "Nothing happens."));
                break;
            case Verb.Talk:
                await Say(person ? "They don't seem to want to talk." : Pick("It's not much of a talker.", "I've had better conversations with a lamppost."));
                break;
            case Verb.Kick:
                await Say(person ? "Tempting. But no." : Pick("It won't budge.", "Ow.", "Kicking things never solved anything. Mostly."));
                break;
            case Verb.UseItem when item != null:
                await Say(person ? "I don't think they'd want that." : Pick("That doesn't work.", "I don't think so."));
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
        var id = actorId.ToLowerInvariant();
        ISpeaker who = id == "micah" || id == "daniel" || id == Player.Character
            ? Player
            : Room?.FindSpeaker(id) ?? Player;
        return Say(who, text);
    }

    public async Task Say(ISpeaker who, string text)
    {
        _skipSpeech = new TaskCompletionSource();
        var skip = _skipSpeech;
        who.Talking = true;
        Hud.ShowSpeech(text, who);
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
        var timer = GetTree().CreateTimer(seconds, processAlways: false);
        await ToSignal(timer, SceneTreeTimer.SignalName.Timeout);
    }

    public async Task ChangeRoom(string name, string entry)
    {
        _busy++;
        try
        {
            await Hud.Fade(1, 0.35);
            LoadRoomScene(name);
            var marker = Room!.GetNodeOrNull<Node2D>($"Entries/{entry}");
            var facing = marker != null && marker.HasMeta("facing") ? (Facing)marker.GetMeta("facing").AsInt32() : Facing.Down;
            Player.Teleport(Room.EntryPoint(entry), facing);
            await Hud.Fade(0, 0.35);
        }
        finally { _busy--; }
        await Room!.OnEnter(entry);
        // written once the player is back in control, so entry cutscenes have already set their flags
        _autosavePending = true;
    }

    private void LoadRoomScene(string name)
    {
        UnloadRoom();
        Hud.HideCloseUp(0);
        Room = GD.Load<PackedScene>(RoomScenePath(name)).Instantiate<Room>();
        _roomScene = name;
        _roomHost.AddChild(Room);
        Room.World.AddChild(Player);
        Player.SetCharacter(Room.ResolvePlayerCharacter());
        Player.Visible = Room.PlayerVisibleOnLoad;
    }

    private void UnloadRoom()
    {
        _actionId++;
        Player.Stop();
        SetCarried(null);
        Hud.ShowInventory(false);
        Hud.Wheel.Close();
        Hud.SetHover(null, Hud.MousePos);
        if (Room == null) return;
        Room.World.RemoveChild(Player);
        Room.QueueFree();
        Room = null;
        _roomScene = "";
    }

    // ------------------------------------------------------------------ save / load

    public SaveData CaptureSave()
    {
        var data = new SaveData
        {
            SavedAtUtc = DateTime.UtcNow,
            Room = _roomScene,
            RoomTitle = Room?.RoomName ?? "",
            X = Player.Position.X,
            Y = Player.Position.Y,
            Facing = (int)Player.Facing,
            Ink = DialogueManager.Instance.SaveInk(),
            PlaytimeSeconds = _playtime,
        };
        GameState.Instance.CaptureInto(data);
        return data;
    }

    public bool SaveToSlot(string slot) => CanSave && SaveSystem.Write(slot, CaptureSave());

    /// <summary>Restores a save: game state, Ink state, room and the player's exact spot. Entry cutscenes don't replay.</summary>
    public async Task LoadGame(SaveData data)
    {
        _busy++;
        try
        {
            await Hud.Fade(1, 0.35);
            PuzzleMigration.Normalize(data);
            GameState.Instance.Restore(data.Flags, data.Inventory, data.StoryAct);
            DialogueManager.Instance.LoadInk(data.Ink);
            _playtime = data.PlaytimeSeconds;
            _autosavePending = false;
            LoadRoomScene(data.Room);
            Player.Teleport(new Vector2(data.X, data.Y), (Facing)data.Facing);
            await Hud.Fade(0, 0.35);
        }
        finally { _busy--; }
    }

    public async Task NewGame()
    {
        GameState.Instance.Reset();
        DialogueManager.Instance.ResetInk();
        _playtime = 0;
        foreach (var flag in _startFlags) GameState.Instance.SetFlag(flag);
        await ChangeRoom(StartRoom, StartEntry);
    }

    private async Task PauseMenu()
    {
        _actionId++;
        Player.Stop();
        SetCarried(null);
        Hud.ShowInventory(false);
        Hud.SetHover(null, Hud.MousePos);
        GetTree().Paused = true;
        var choice = await Hud.Menu.OpenPause();
        GetTree().Paused = false;
        switch (choice)
        {
            case { Action: MenuAction.Load, Save: { } save }:
                await LoadGame(save);
                break;
            case { Action: MenuAction.QuitToTitle }:
                _busy++;
                try { await Hud.Fade(1, 0.5); }
                finally { _busy--; }
                UnloadRoom();
                await TitleScreen();
                break;
        }
    }
}
