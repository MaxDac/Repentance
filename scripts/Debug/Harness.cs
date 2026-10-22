using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Shared base of every automated run (autoplay, settings, pause, walk, playthrough, film): the clock, checks and
/// the final pass/fail marker, synthetic mouse and keyboard input, isolated save directories and screenshots.
/// Every run prints exactly one "&lt;MARKER&gt; OK" or "&lt;MARKER&gt; FAILED:" line and quits with 0 or 1.
/// </summary>
public abstract class Harness
{
    /// <summary>Previous automated clock: 8× game time, display timing left alone.</summary>
    protected const double NormalTimeScale = 8;
    /// <summary>Uncapped clock: dialogue and <see cref="Game.Wait"/> do not take wall-clock story time.</summary>
    protected const double FastTimeScale = 60;

    protected Game _game = null!;
    protected readonly List<string> _failures = new();
    protected int _checks;
    /// <summary>Print every passing check (autoplay) or only the failures (walk test).</summary>
    protected bool VerbosePasses = true;
    protected string _dir = "";
    protected int _shot;

    /// <summary>"AUTOPLAY", "WALK TEST", ...: printed as "{Marker} OK" or "{Marker} FAILED:".</summary>
    protected abstract string Marker { get; }

    /// <summary>Common start: clock, scripted-sequence error capture, an emptied save directory for this suite.</summary>
    protected bool Begin(Game game, string saveSuite, bool applyClock = true)
    {
        _game = game;
        // keep "The End" up for the checks and the next seeded ending instead of leaving for the title
        game.EndReturnsToTitle = false;
        Game.SequenceFailed += OnSequenceFailed;
        if (applyClock && !ApplyClock(out var clockError))
        {
            _failures.Add(clockError);
            return false;
        }
        // never touch the player's own saves
        SaveSystem.Directory = $"user://autoplay_saves/{saveSuite}";
        foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
        return true;
    }

    /// <summary>Prints the marker line, restores the clock and quits with 0 (pass) or 1 (fail).</summary>
    protected void Finish(string? summary = null)
    {
        Game.SequenceFailed -= OnSequenceFailed;
        if (summary != null) GD.Print(summary);
        GD.Print(_failures.Count == 0 ? $"{Marker} OK" : $"{Marker} FAILED:\n  " + string.Join("\n  ", _failures));
        Engine.TimeScale = 1;
        Timers.ReleasePending();
        _game.Music.StopRendering();
        // At shutdown Godot disposes the wrappers C# still holds, but skips any the GC collected and has not yet
        // finalized: their objects leak, or their finalizers run while the engine is torn down. Finalize them now.
        GC.Collect();
        GC.WaitForPendingFinalizers();
        _game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    /// <summary><see cref="Game.Run"/> logs and swallows exceptions so the game survives; a test must not.</summary>
    private void OnSequenceFailed(Exception ex) => _failures.Add("scripted sequence threw: " + ex.Message);

    /// <summary>The current room draws its rain and plays its patter.</summary>
    protected bool RainsHere() =>
        _game.Room?.GetNodeOrNull<Rain>("Rain") is { Visible: true } && _game.Sfx.Ambient == Sound.Rain;

    /// <summary>No rain drawn in the current room, and no patter.</summary>
    protected bool DryHere() =>
        _game.Room?.GetNodeOrNull<Rain>("Rain") is not { Visible: true } && _game.Sfx.Ambient == null;

    /// <summary>
    /// <c>--clock=fast</c> (default) uncapped 60×, or <c>--clock=normal</c> for the previous 8× clock.
    /// Pause assertions still force 1×. Fast also disables vsync so an unfocused run is not stuck at the refresh rate.
    /// </summary>
    internal static bool ApplyClock(out string error)
    {
        error = "";
        string? value = null;
        foreach (var arg in OS.GetCmdlineUserArgs())
        {
            if (arg == "--clock")
            {
                error = "--clock requires =normal or =fast";
                return false;
            }
            if (!arg.StartsWith("--clock=")) continue;
            if (value != null)
            {
                error = "--clock given more than once";
                return false;
            }
            value = arg["--clock=".Length..];
        }
        if (value is null or "fast")
        {
            Engine.TimeScale = FastTimeScale;
            Uncap();
            GD.Print("[harness] clock fast (60x, vsync off)");
            return true;
        }
        if (value == "normal")
        {
            Engine.TimeScale = NormalTimeScale;
            GD.Print("[harness] clock normal (8x)");
            return true;
        }
        error = $"unknown --clock={value} (use normal or fast)";
        return false;
    }

    /// <summary>Lets a high <see cref="Engine.TimeScale"/> run as fast as the machine allows: no frame cap, no vsync.</summary>
    internal static void Uncap()
    {
        Engine.MaxPhysicsStepsPerFrame = 256;
        Engine.MaxFps = 0;
        OS.LowProcessorUsageMode = false;
        DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Disabled);
    }

    /// <summary>The value of <c>--name=value</c> among the user arguments, or null.</summary>
    internal static string? Arg(string name)
    {
        foreach (var arg in OS.GetCmdlineUserArgs())
            if (arg.StartsWith($"--{name}=")) return arg[(name.Length + 3)..];
        return null;
    }

    // ------------------------------------------------------------------ checks

    protected void Check(bool ok, string what)
    {
        _checks++;
        if (ok)
        {
            if (VerbosePasses) GD.Print($"[{Tag}] PASS {what}");
            return;
        }
        Fail(what);
    }

    protected void Fail(string what)
    {
        GD.Print($"[{Tag}] FAIL {what}");
        _failures.Add(what);
    }

    private string Tag => Marker.ToLowerInvariant().Replace(' ', '-');

    // ------------------------------------------------------------------ time

    /// <summary>Waits in real time, ignoring the clock scale and pause.</summary>
    protected Task Observe(double seconds) => Timers.Wait(_game, seconds, processAlways: true, ignoreTimeScale: true);

    /// <summary>
    /// Waits until no scripted sequence runs, for at least <paramref name="timeout"/> game seconds. Long enough for the
    /// longest entry cutscene (the Act 3 office window, ~52 s of thoughts), whatever the frame rate.
    /// </summary>
    protected async Task WaitIdle(Game? game = null, double timeout = 120)
    {
        game ??= _game;
        await game.Wait(0.2);
        for (double t = 0; t < timeout && game.Busy; t += 0.1) await game.Wait(0.1);
        if (game.Busy) GD.Print($"[{Tag}] WaitIdle: still busy after {timeout} s");
    }

    /// <summary>When set, every <see cref="Until"/> step records the speech and thoughts on screen into it.</summary>
    protected List<string>? HeardLog;

    protected async Task Until(Func<bool> done, double timeout = 90, double step = 0.1)
    {
        for (double t = 0; t < timeout; t += step)
        {
            if (HeardLog != null) Heard(HeardLog);
            if (done()) break;
            await _game.Wait(step);
        }
    }

    /// <summary>Runs an action to the end and returns every speech line and thought shown while it ran, in order.</summary>
    protected async Task<List<string>> Spoken(Func<Task> action, double timeout = 90)
    {
        var lines = new List<string>();
        var running = action();
        await Until(() =>
        {
            Heard(lines);
            return running.IsCompleted;
        }, timeout, 0.02);
        await running;
        return lines;
    }

    /// <summary>Adds the speech line or thought on screen to <paramref name="lines"/>, once while it stays up.</summary>
    protected void Heard(List<string> lines)
    {
        foreach (var (visible, text) in new[] { (_game.Hud.SpeechVisible, _game.Hud.SpeechText), (_game.Hud.ThoughtVisible, _game.Hud.ThoughtText) })
            if (visible && text != "" && !lines.TakeLast(2).Contains(text))
                lines.Add(text);
    }

    // ------------------------------------------------------------------ synthetic input

    protected void Move(Vector2 pos)
    {
        Push(new InputEventMouseMotion { Position = pos, GlobalPosition = pos });
        _game.GetViewport().WarpMouse(pos);
    }

    protected void Click(Vector2 pos, MouseButton button = MouseButton.Left)
    {
        foreach (var pressed in new[] { true, false })
        {
            Push(new InputEventMouseButton
            {
                Position = pos, GlobalPosition = pos, ButtonIndex = button, Pressed = pressed,
            });
        }
    }

    protected void PressKey(Key key, bool alt = false)
    {
        foreach (var pressed in new[] { true, false })
            Push(new InputEventKey
            {
                Keycode = key, PhysicalKeycode = key, AltPressed = alt, Pressed = pressed,
            });
    }

    /// <summary>A finger on the touch screen (index 0): down, dragged or lifted at <paramref name="pos"/>.</summary>
    protected void Touch(Vector2 pos, bool pressed) => Push(new InputEventScreenTouch { Position = pos, Pressed = pressed });

    protected void TouchDrag(Vector2 pos) => Push(new InputEventScreenDrag { Position = pos });

    /// <summary>Pushes a synthetic event past film mode's <see cref="SpectatorFilter"/>.</summary>
    private void Push(InputEvent e)
    {
        SpectatorFilter.Injecting = true;
        try { _game.GetViewport().PushInput(e, true); }
        finally { SpectatorFilter.Injecting = false; }
    }

    // ------------------------------------------------------------------ story helpers

    /// <summary>Film mode waits here so a viewer can follow each click; tests don't wait.</summary>
    protected virtual Task Pace(double seconds) => Task.CompletedTask;

    protected async Task SolvePuzzle(Func<Task> start, PuzzleKind kind, (string Id, int Count)[] controls, string name, bool submit = true)
    {
        var action = start();
        await Until(() => _game.Hud.Puzzle.IsOpen);
        Check(_game.Hud.Puzzle.IsOpen && _game.Hud.Puzzle.Kind == kind, $"reopened {name}");
        foreach (var (id, count) in controls)
        {
            for (int i = 0; i < count; i++)
            {
                await Pace(0.3);
                PuzzleClick(id);
            }
            await _game.Wait(0.1);
        }
        if (submit)
        {
            await Pace(0.8);
            await Shot(name + "_solution");
            PuzzleClick("submit");
        }
        await action;
        await WaitIdle(_game);
        Check(!_game.Hud.Puzzle.IsOpen, $"solved {name} through real controls");
    }

    /// <summary>The cage's shortest way through the service shafts, as arrow-button clicks.</summary>
    protected static (string Id, int Count)[] LiftRoute() =>
        LiftMaze.Route(LiftMaze.Start, LiftMaze.Target)!.Select(step => (step, 1)).ToArray();

    protected void PuzzleClick(string id)
    {
        var point = _game.Hud.Puzzle.ButtonCenter(id);
        Move(point);
        Click(point, MouseButton.Left);
    }

    /// <summary>One direction-pad step through the arrow keys.</summary>
    protected void PuzzleKey(string step) => PressKey(step switch
    {
        "up" => Key.Up, "down" => Key.Down, "left" => Key.Left, "right" => Key.Right,
        _ => throw new ArgumentException($"No arrow for '{step}'.", nameof(step)),
    });

    /// <summary>A left-button drag from <paramref name="from"/> along the steps, one cell each, in half-cell motions.</summary>
    protected void PuzzleDrag(Vector2 from, IEnumerable<string> steps, float cell = 14)
    {
        Move(from);
        Push(new InputEventMouseButton { Position = from, GlobalPosition = from, ButtonIndex = MouseButton.Left, Pressed = true, ButtonMask = MouseButtonMask.Left });
        var at = from;
        foreach (var step in steps)
        {
            var (dx, dy) = LiftMaze.Step(step);
            for (int half = 0; half < 2; half++)
            {
                var delta = new Vector2(dx, dy) * cell / 2;
                at += delta;
                Push(new InputEventMouseMotion { Position = at, GlobalPosition = at, Relative = delta, ButtonMask = MouseButtonMask.Left });
            }
        }
        Push(new InputEventMouseButton { Position = at, GlobalPosition = at, ButtonIndex = MouseButton.Left, Pressed = false });
    }

    protected async Task SelectInventoryItem(string item)
    {
        await WaitIdle(_game);
        if (!_game.Hud.InventoryOpen) Click(_game.Hud.SatchelCenter, MouseButton.Left);
        await _game.Wait(0.1);
        Check(_game.Hud.InventoryOpen, $"satchel open to select {item}");
        if (!_game.Hud.InventoryOpen) throw new InvalidOperationException($"Satchel did not open for {item}");
        await Pace(0.5);
        int index = IndexOf(item);
        int page = index / 12;
        while (_game.Hud.InventoryPage != page)
        {
            Click(_game.Hud.InventoryPageCenter(_game.Hud.InventoryPage < page), MouseButton.Left);
            await _game.Wait(0.1);
        }
        Click(_game.Hud.SlotCenter(index), MouseButton.Left);
        await _game.Wait(0.1);
    }

    protected async Task Combine(string first, string second)
    {
        await SelectInventoryItem(first);
        Check(_game.Carried == first, $"picked {first} from paged inventory");
        Check(_game.Hud.InventoryOpen, $"the case stays open after picking {first}");
        await SelectInventoryItem(second);
    }

    protected async Task CombineAndWait(string first, string second)
    {
        await Combine(first, second);
        while (_game.Busy) await _game.Wait(0.1);
    }

    protected static int IndexOf(string item)
    {
        var inv = GameState.Instance.Inventory;
        for (int i = 0; i < inv.Count; i++)
            if (inv[i] == item) return i;
        throw new InvalidOperationException($"Inventory does not contain '{item}'.");
    }

    // ------------------------------------------------------------------ screenshots

    /// <summary>Screenshots go to res://screenshots/ (gitignored, and hidden from the importer).</summary>
    protected void PrepareScreenshots()
    {
        _dir = ProjectSettings.GlobalizePath("res://screenshots");
        DirAccess.MakeDirRecursiveAbsolute(_dir);
        using (FileAccess.Open($"{_dir}/.gdignore", FileAccess.ModeFlags.Write)) { }
    }

    protected async Task Shot(string name)
    {
        // Headless runs never draw a frame, so FramePostDraw would never fire.
        if (_dir == "" || DisplayServer.GetName() == "headless") return;
        await Observe(0.4 / Engine.TimeScale);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
