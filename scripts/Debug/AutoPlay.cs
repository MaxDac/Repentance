using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Smoke test: plays the whole demo by itself, saving screenshots to screenshots/ and printing
/// AUTOPLAY OK / AUTOPLAY FAILED. Run with: godot -- --autoplay [--clock=fast|normal]
/// </summary>
public partial class AutoPlay
{
    /// <summary>Previous automated clock: 8× game time, display timing left alone.</summary>
    private const double NormalTimeScale = 8;
    /// <summary>Uncapped clock: dialogue and <see cref="Game.Wait"/> do not take wall-clock story time.</summary>
    private const double FastTimeScale = 60;
    private Game _game = null!;
    private readonly HashSet<string> _shotKnots = new();
    private readonly List<string> _failures = new();
    private string _dir = "";
    private int _shot;
    private readonly Dictionary<string, int> _poseCounts = new();
    private readonly Dictionary<PosePlayback, int> _lastPoseFrame = new();
    private string[] _prefer = Array.Empty<string>();
    private readonly Dictionary<string, string[]> _offered = new();
    private bool _theEndShot;
    private string _act3Ink = "";
    private int _crossOffers;
    private bool? _insetAtCaughtChoice;
    private bool? _insetAtBeatenChoice;
    private string[] _act3Flags = Array.Empty<string>();
    private string[] _act3Items = Array.Empty<string>();
    private CloseUp? _closeUpAtRoadChoice;

    public async Task Run(Game game)
    {
        _game = game;
        PosePlayback.FrameObserver = ObservePose;
        _dir = ProjectSettings.GlobalizePath("res://screenshots");
        DirAccess.MakeDirRecursiveAbsolute(_dir);
        // keep Godot from importing the screenshots
        using (FileAccess.Open($"{_dir}/.gdignore", FileAccess.ModeFlags.Write)) { }
        if (!ApplyClock(out var clockError))
        {
            GD.Print("AUTOPLAY FAILED:\n  " + clockError);
            game.GetTree().Quit(1);
            return;
        }
        // never touch the player's own saves
        SaveSystem.Directory = "user://autoplay_saves/ten_puzzles_act3";
        foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
        DialogueManager.Instance.AutoChoose = async (knot, options) =>
        {
            GD.Print($"[autoplay] {knot}: {string.Join(" | ", options)}");
            if (_shotKnots.Add(knot))
            {
                _ = game.Hud.ShowChoices(options);
                await Shot($"choices_{knot.Replace('.', '_')}");
                game.Hud.HideChoices();
            }
            _offered[knot] = options.ToArray();
            if (knot == "caleb_cross") _crossOffers++;
            if (knot == "club_caught") _insetAtCaughtChoice = game.Hud.InsetVisible;
            if (knot == "beaten_choice") _insetAtBeatenChoice = game.Hud.InsetVisible;
            if (knot == "eleanor_road")
            {
                _closeUpAtRoadChoice = game.Hud.CurrentCloseUp;
                Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn,
                    "the convent panel is completely removed before the compensation choice");
            }
            foreach (var want in _prefer)
            {
                for (int i = 0; i < options.Count; i++)
                    if (options[i].Contains(want)) return i;
            }
            return 0;
        };

        try
        {
            var gs = GameState.Instance;
            await ContentSettingsTest(game);
            if (OS.GetCmdlineUserArgs().Contains("--settings-test")) return;
            bool autosave = game.AutosaveEnabled;
            game.AutosaveEnabled = false;
            await StoryDialogueTest(game);
            await PuzzleRecoveryTest(game);
            await ActThreePuzzleRecoveryTest(game);
            foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
            gs.Reset();
            DialogueManager.Instance.ResetInk();

            await PlayPrologue(game, gs, autosave);
            await PlayActOne(game, gs);
            await PlayActTwo(game, gs);
            await PlayActThree(game, gs);
            await PlayOtherEndings(game, gs);
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            GD.Print(_failures.Count == 0 ? "AUTOPLAY OK" : "AUTOPLAY FAILED:\n  " + string.Join("\n  ", _failures));
            PosePlayback.FrameObserver = null;
            Engine.TimeScale = 1;
            game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
        }
    }

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
            Engine.MaxPhysicsStepsPerFrame = 256;
            Engine.MaxFps = 0;
            OS.LowProcessorUsageMode = false;
            DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Disabled);
            GD.Print("[autoplay] clock fast (60x, vsync off)");
            return true;
        }
        if (value == "normal")
        {
            Engine.TimeScale = NormalTimeScale;
            GD.Print("[autoplay] clock normal (8x)");
            return true;
        }
        error = $"unknown --clock={value} (use normal or fast)";
        return false;
    }

    private async Task Observe(double seconds)
    {
        var timer = _game.GetTree().CreateTimer(seconds, processAlways: true, ignoreTimeScale: true);
        await _game.ToSignal(timer, SceneTreeTimer.SignalName.Timeout);
    }

    private async Task AwaitTest(Task task, string description)
    {
        for (int i = 0; i < 100 && !task.IsCompleted; i++) await Observe(0.05);
        if (!task.IsCompleted) throw new TimeoutException(description);
        await task;
        Check(true, description);
    }

    private async Task WaitIdle(Game game)
    {
        await game.Wait(0.2);
        for (int i = 0; i < 300 && game.Busy; i++) await game.Wait(0.1);
    }

    private void Move(Vector2 pos)
    {
        _game.GetViewport().PushInput(new InputEventMouseMotion { Position = pos, GlobalPosition = pos }, true);
        _game.GetViewport().WarpMouse(pos);
    }

    private void Click(Vector2 pos, MouseButton button)
    {
        foreach (var pressed in new[] { true, false })
        {
            _game.GetViewport().PushInput(new InputEventMouseButton
            {
                Position = pos, GlobalPosition = pos, ButtonIndex = button, Pressed = pressed,
            }, true);
        }
    }

    private async Task Until(Func<bool> done, double timeout = 90)
    {
        for (double t = 0; t < timeout && !done(); t += 0.1) await _game.Wait(0.1);
    }

    private void Check(bool ok, string what)
    {
        GD.Print($"[autoplay] {(ok ? "PASS" : "FAIL")} {what}");
        if (!ok) _failures.Add(what);
    }

    private async Task Shot(string name)
    {
        await Observe(0.4 / Engine.TimeScale);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
