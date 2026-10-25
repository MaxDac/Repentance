using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// The canonical story, played from the attic to "The End" through the same actions a player would take, as ordered
/// named beats. Two modes share it:
/// <list type="bullet">
/// <item><c>--playthrough</c>: a test. Acts 1–2 once, then every ending route reloaded from a real save at the Club
/// vestibule. Every beat ends with a save → load round trip; coverage of sounds and Ink choices is checked at the end.
/// Prints "PLAYTHROUGH OK".</item>
/// <item><c>--film[=1|2|4|8|16|60|hyper]</c>: the same story to watch, at 1× to 60× speed (hyper is 60×, uncapped),
/// one ending (<c>--ending</c>, default 2), from a chapter (<c>--from</c>, see <see cref="Chapters"/>; the earlier
/// beats play unseen and muted at 60×). The viewer's input is ignored (Space pauses, F11 toggles full screen, Esc
/// stops). Prints "FILM OK".</item>
/// <item><c>--playthrough --resume=act2|act3</c>: a fresh launch. Loads a checkpoint the full playthrough kept (end of
/// Act One, or the Club vestibule) and plays one route to "The End" (<c>--ending</c>, default 2 from Act One and 8 from
/// the vestibule), so state a save forgets cannot hide in memory. Prints "RESUME OK".</item>
/// </list>
/// Routes: 2, 3, 4, 5 (by Eleanor's answer and whether the evidence/fire set Micah free), 6 (prays on the stage,
/// then turns himself in after the shot), 7 (shoots Eleanor, then himself), 7-alone (loses her, and at the footsteps
/// shoots himself alone), and the ways to ending 1:
/// 1 (walk away from Tony), 1-oldman (spare Harrington, praying back to the door), 1-steps (give up on the church steps),
/// 1-caleb and 1-steps-caleb (walk away from Tony, or give up on the steps, after Eleanor refused the gin too: Rose, then
/// Eleanor and Caleb at the outskirts) and 1-bed (spare Harrington, and Eleanor, who held out, goes back to bed).
/// Ending 15 is route 1 (15), 1-caleb (15-caleb), 1-steps (15-steps), 1-steps-caleb (15-steps-caleb), 1-oldman
/// (15-oldman) or 1-bed (15-bed) after Micah said good night to Rose at once in Act 2, so she refuses the coffee.
/// Act 2's First Interlude always refuses the Mother Superior; Act 3's Second Interlude takes the old man's gin except on
/// Eleanor's routes: 8 (after the prayer she strikes him and burns the house), 9 (strikes him only), 10 (Micah shoots,
/// she follows him worn out, and the fire and documents take them out of town) and 11 (the same, but nothing taken: prison).
/// Ending 12 kills Tony in the alley: 12 (confesses to Caleb and turns himself in at the church) and 12-oldman (confesses,
/// goes on to the mansion for the papers and prays his way out past the old man); after Eleanor held out, the same prayer
/// leads to her coda: 12-bed (back to bed), 9-kill (strikes him) and 8-kill (strikes him and burns the house).
/// Endings 13 and 14 fire the warning shot by Tony's head: Tony leaves the alarm out, the kitchen door rings it, and
/// Micah runs out of Chicago (13) or goes in to the Club's two men (14); 13-caleb and 14-caleb add Eleanor's escape with
/// Caleb after she held out.
/// </summary>
public sealed partial class Playthrough : Harness
{
    public static readonly string[] Routes =
    {
        "2", "3", "4", "5", "6", "7", "7-alone", "1", "1-oldman", "1-steps", "1-steps-caleb", "1-caleb", "1-bed",
        "15", "15-caleb", "15-steps", "15-steps-caleb", "15-oldman", "15-bed", "8", "8-kill", "9", "9-kill", "10", "11",
        "12", "12-oldman", "12-bed", "13", "13-caleb", "14", "14-caleb",
    };

    /// <summary>
    /// Sounds the canonical routes never play. Every other <see cref="Sound"/> must be heard at least once.
    /// Keep a reason with each entry.
    /// </summary>
    private static readonly Dictionary<Sound, string> UnheardSounds = new()
    {
    };

    /// <summary>Film speeds; "hyper" is 60.</summary>
    public static readonly string[] Speeds = { "1", "2", "4", "8", "16", "60", "hyper" };

    /// <summary>Where <c>--from</c> may start the film, in story order.</summary>
    public static readonly string[] Chapters = { "act1", "interlude1", "act2", "interlude2", "act3", "ending" };

    /// <summary>The first beat shown for a chapter on a route; null starts at the title.</summary>
    public static string? StartBeat(string chapter, string route) => chapter switch
    {
        "act1" => null,
        "interlude1" => "first_interlude_aurelian",
        "act2" => "act_two_opening",
        "interlude2" => "second_interlude_taken",
        "act3" => IsSteps(route) ? throw new ArgumentException($"ending {route} ends in the Second Interlude, before Act 3") : "act_three_office",
        "ending" => route switch
        {
            _ when IsWalkAway(route) || IsKill(route) || IsAlarm(route) => "alley_act_three",
            _ when IsSteps(route) => "second_interlude_oldman",
            _ => "mansion_study",
        },
        _ => throw new ArgumentException($"unknown chapter {chapter} (use {string.Join(", ", Chapters)})"),
    };

    /// <summary>Where <c>--resume</c> may start a fresh launch: after Act One, or at the Club vestibule before Act 3.</summary>
    public static readonly string[] ResumePoints = { "act2", "act3" };

    /// <summary>Real saves the full playthrough keeps for <c>--resume</c>; never cleared by a suite's <see cref="Harness.Begin"/>.</summary>
    private const string CheckpointDirectory = "user://autoplay_saves/checkpoints";
    private const string AfterActOne = "after_act_one";
    private const string Vestibule = "vestibule";

    private readonly bool _film;
    private string? _resume;
    private double _speed = 1;
    private string _chapter = "act1";
    private string? _startBeat;
    private bool _skipping;
    private FilmCover? _cover;
    private (int PhysicsSteps, int MaxFps, bool LowProcessor, DisplayServer.VSyncMode Vsync) _capped;
    private string _route = "2";
    private string[] _routes = { "2" };
    private readonly List<string> _decisions = new();
    private readonly HashSet<string> _matchedWants = new();
    private readonly HashSet<string> _shownLabels = new();
    private int _roundTrips;
    private const string RoundTripSlot = "manual_3";

    public Playthrough(bool film)
    {
        _film = film;
        VerbosePasses = !film;
    }

    protected override string Marker => _film ? "FILM" : _resume != null ? "RESUME" : "PLAYTHROUGH";

    private string Tag => _film ? "film" : _resume != null ? "resume" : "playthrough";

    private static GameState Gs => GameState.Instance;

    public async Task Run(Game game)
    {
        string? summary = null;
        try
        {
            if (!Setup(game)) return;
            DialogueManager.Instance.AutoChoose = Choose;
            DialogueManager.Instance.ChoicesOffered += Record;
            if (_film) await Film();
            else if (_resume != null) await Resume();
            else await Test();
            summary = $"[{Tag}] {_checks} checks, {_roundTrips} save/load round trips, {_decisions.Count} decisions";
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            DialogueManager.Instance.AutoChoose = null;
            DialogueManager.Instance.ChoicesOffered -= Record;
            Finish(summary);
        }
    }

    private bool Setup(Game game)
    {
        _game = game;
        string? resume = Arg("resume");
        if (resume != null)
        {
            if (_film)
            {
                _failures.Add("--resume is for --playthrough only");
                return false;
            }
            if (!ResumePoints.Contains(resume))
            {
                _failures.Add($"unknown --resume={resume} (use {string.Join(", ", ResumePoints)})");
                return false;
            }
            _resume = resume;
        }
        bool allowAll = !_film && _resume == null;
        string ending = Arg("ending") ?? (_film ? "2" : _resume switch { "act2" => "2", "act3" => "8", _ => "all" });
        if (ending == "all" && allowAll) _routes = Routes;
        else if (Routes.Contains(ending)) _routes = new[] { ending };
        else
        {
            _failures.Add($"unknown --ending={ending} (use {string.Join(", ", Routes)}{(allowAll ? " or all" : "")})");
            return false;
        }
        if (!_film)
        {
            if (Arg("from") != null)
            {
                _failures.Add("--from is for film mode only");
                return false;
            }
            return Begin(game, _resume != null ? "resume" : "playthrough");
        }

        string speed = Arg("film") ?? "1";
        if (!Speeds.Contains(speed))
        {
            _failures.Add($"unknown --film={speed} (use {string.Join(", ", Speeds)})");
            return false;
        }
        _speed = speed == "hyper" ? 60 : double.Parse(speed);
        _chapter = Arg("from") ?? "act1";
        try { _startBeat = StartBeat(_chapter, _routes[0]); }
        catch (ArgumentException ex)
        {
            _failures.Add($"--from={_chapter}: {ex.Message}");
            return false;
        }
        if (!Begin(game, "film", applyClock: false)) return false;
        _capped = (Engine.MaxPhysicsStepsPerFrame, Engine.MaxFps, OS.LowProcessorUsageMode, DisplayServer.WindowGetVsyncMode());
        // above 4x the frame rate and physics steps would hold the clock back
        if (_speed > 4 || _startBeat != null) Uncap();
        Engine.TimeScale = _speed;
        game.GetTree().Root.CallDeferred(Node.MethodName.AddChild, new SpectatorFilter { Name = "SpectatorFilter" });
        GD.Print($"[film] {_speed}x, ending {_routes[0]}, from {_chapter}. Space pauses, F11 toggles full screen, Esc stops.");
        return true;
    }

    // ------------------------------------------------------------------ modes

    private async Task Film()
    {
        _route = _routes[0];
        if (_startBeat != null)
        {
            _skipping = true;
            Engine.TimeScale = FastTimeScale;
            AudioServer.SetBusMute(0, true);
            _cover = new FilmCover($"Fast-forwarding to {ChapterTitle(_chapter)}...");
            _game.GetTree().Root.CallDeferred(Node.MethodName.AddChild, _cover);
            GD.Print($"[film] fast-forwarding to {_chapter} (beat {_startBeat})");
        }
        else
        {
            _game.ShowTitle(true);
            await _game.Hud.Fade(0, 0.8);
            await _game.Wait(3);
            await _game.Hud.Fade(1, 0.5);
            _game.ShowTitle(false);
        }
        await _game.NewGame();
        await WaitIdle();
        await ActOne();
        await ActTwo();
        await ActThree();
        if (_skipping) Fail($"--from={_chapter}: never reached beat {_startBeat} on route {_route}");
        await _game.Wait(4);
    }

    private static string ChapterTitle(string chapter) => chapter switch
    {
        "interlude1" => "the First Interlude",
        "act2" => "Act 2",
        "interlude2" => "the Second Interlude",
        "act3" => "Act 3",
        "ending" => "the ending",
        _ => "Act 1",
    };

    /// <summary>Reached the <c>--from</c> chapter: back to the chosen speed, with sound, and lift the curtain.</summary>
    private async Task EndSkip()
    {
        _skipping = false;
        await WaitIdle();
        Engine.TimeScale = _speed;
        if (_speed <= 4)
        {
            Engine.MaxPhysicsStepsPerFrame = _capped.PhysicsSteps;
            Engine.MaxFps = _capped.MaxFps;
            OS.LowProcessorUsageMode = _capped.LowProcessor;
            DisplayServer.WindowSetVsyncMode(_capped.Vsync);
        }
        AudioServer.SetBusMute(0, false);
        _cover?.Lift();
        _cover = null;
        GD.Print($"[film] {_chapter} starts");
        await Pace(1.0);
    }

    private async Task Test()
    {
        ClearCheckpoints();
        await _game.NewGame();
        await WaitIdle();
        await ActOne();
        KeepCheckpoint(AfterActOne);
        await ActTwo();
        string checkpoint = SaveSystem.ManualSlot(1);
        Check(_game.SaveToSlot(checkpoint), "saved the Club vestibule checkpoint");
        var save = SaveSystem.Read(checkpoint) ?? throw new InvalidOperationException("Missing the vestibule checkpoint");
        KeepCheckpoint(Vestibule);
        var wantsBeforeActThree = _matchedWants.ToList();
        for (int i = 0; i < _routes.Length; i++)
        {
            _route = _routes[i];
            GD.Print($"[playthrough] ---- route {_route}");
            if (i > 0)
            {
                await _game.LoadGame(save);
                await WaitIdle();
                _matchedWants.Clear();
                _matchedWants.UnionWith(wantsBeforeActThree);
                Check(_game.Room is Rooms.ClubVestibule && Gs.HasItem("sealed_invitation"), $"route {_route}: reloaded the vestibule checkpoint");
            }
            await ActThree();
        }
        if (_routes.Length == Routes.Length) CoverageGates();
    }

    // ------------------------------------------------------------------ fresh-launch checkpoints

    private static string WantsPath(string checkpoint) => $"{CheckpointDirectory}/{checkpoint}.wants";

    /// <summary>Runs <paramref name="body"/> with the save system pointed at the checkpoint folder.</summary>
    private static T InCheckpoints<T>(Func<T> body)
    {
        string suite = SaveSystem.Directory;
        SaveSystem.Directory = CheckpointDirectory;
        try { return body(); }
        finally { SaveSystem.Directory = suite; }
    }

    private static void ClearCheckpoints()
    {
        foreach (var name in new[] { AfterActOne, Vestibule })
        {
            InCheckpoints(() => { SaveSystem.Delete(name); return true; });
            if (FileAccess.FileExists(WantsPath(name))) DirAccess.RemoveAbsolute(WantsPath(name));
        }
    }

    /// <summary>
    /// Writes a real save (through <see cref="Game.SaveToSlot"/>) for a later <c>--resume</c> run, with the choices
    /// matched so far, which the route checks at "The End" still expect.
    /// </summary>
    private void KeepCheckpoint(string name)
    {
        Check(InCheckpoints(() => _game.SaveToSlot(name)), $"kept the {name} checkpoint for a fresh launch");
        using var file = FileAccess.Open(WantsPath(name), FileAccess.ModeFlags.Write);
        if (file == null) Fail($"cannot write {WantsPath(name)}: {FileAccess.GetOpenError()}");
        else file.StoreString(string.Join("\n", _matchedWants.Order(StringComparer.Ordinal)));
    }

    /// <summary>A fresh process: load a kept checkpoint, as the title screen's Load does, and play one route to the end.</summary>
    private async Task Resume()
    {
        _route = _routes[0];
        string name = _resume == "act2" ? AfterActOne : Vestibule;
        var save = InCheckpoints(() => SaveSystem.Read(name));
        if (save == null || !FileAccess.FileExists(WantsPath(name)))
        {
            Fail($"--resume={_resume}: no readable {name} checkpoint in {CheckpointDirectory} (run --playthrough first)");
            return;
        }
        using (var file = FileAccess.Open(WantsPath(name), FileAccess.ModeFlags.Read))
            _matchedWants.UnionWith(file.GetAsText().Split('\n', StringSplitOptions.RemoveEmptyEntries));
        GD.Print($"[resume] fresh launch from the {name} checkpoint ({save.Room}), route {_route}");

        await _game.LoadGame(save);
        await WaitIdle();
        var loaded = _game.CaptureSave();
        Check(loaded.Room == save.Room && loaded.StoryAct == save.StoryAct
              && loaded.Flags.ToHashSet().SetEquals(save.Flags) && loaded.Inventory.SequenceEqual(save.Inventory)
              && loaded.Ink == save.Ink && _game.CanSave,
            $"the {name} checkpoint loads in a fresh process");
        if (_resume == "act2")
        {
            Check(Gs.StoryAct == 2 && _game.Room is Rooms.Attic, "resumed in the attic after Act One, in Act 2");
            await ActTwo();
        }
        else Check(_game.Room is Rooms.ClubVestibule && Gs.HasItem("sealed_invitation"), "resumed at the Club vestibule");
        await ActThree();
    }

    // ------------------------------------------------------------------ beats

    /// <summary>One named step of the story. Afterwards the playthrough saves, loads and compares the whole state.</summary>
    private async Task Beat(string id, Func<Task> body, bool roundTrip = true)
    {
        if (_skipping && id == _startBeat) await EndSkip();
        GD.Print($"[{Tag}] beat {id}" + (Gs.StoryAct == 3 ? $" (route {_route})" : ""));
        await body();
        if (roundTrip && !_film) await RoundTrip(id);
    }

    private async Task RoundTrip(string id)
    {
        await WaitIdle();
        if (!_game.CanSave)
        {
            Fail($"{id}: the game can't be saved after the beat");
            return;
        }
        var before = _game.CaptureSave();
        if (!_game.SaveToSlot(RoundTripSlot) || SaveSystem.Read(RoundTripSlot) is not { } saved)
        {
            Fail($"{id}: save written and read back");
            return;
        }
        await _game.LoadGame(saved);
        await WaitIdle();
        var after = _game.CaptureSave();
        _roundTrips++;
        var diffs = new List<string>();
        if (after.Room != before.Room) diffs.Add($"room {before.Room} -> {after.Room}");
        if (Math.Abs(after.X - before.X) > 0.5 || Math.Abs(after.Y - before.Y) > 0.5) diffs.Add("position");
        if (after.Facing != before.Facing) diffs.Add("facing");
        if (after.StoryAct != before.StoryAct) diffs.Add("act");
        if (!after.Flags.ToHashSet().SetEquals(before.Flags))
            diffs.Add("flags " + string.Join(",", after.Flags.Except(before.Flags).Concat(before.Flags.Except(after.Flags))));
        if (!after.Inventory.SequenceEqual(before.Inventory)) diffs.Add("inventory");
        if (after.Ink != before.Ink) diffs.Add("ink state");
        Check(diffs.Count == 0 && _game.CanSave, $"{id}: save/load round trip" + (diffs.Count > 0 ? $" ({string.Join("; ", diffs)})" : ""));
    }

    // ------------------------------------------------------------------ decisions

    private async Task<int> Choose(string knot, IReadOnlyList<string> options)
    {
        int pick = 0;
        foreach (var want in Wants())
        {
            int i = options.ToList().FindIndex(o => o.Contains(want, StringComparison.Ordinal));
            if (i < 0) continue;
            pick = i;
            _matchedWants.Add(want);
            break;
        }
        _decisions.Add($"{knot}: {options[pick]}");
        GD.Print($"[{Tag}] choice {knot}: {string.Join(" | ", options)} -> {options[pick]}");
        if (_film && !_skipping)
        {
            _ = _game.Hud.ShowChoices(DialogueManager.Instance.ShownChoices);
            await _game.Wait(1.5);
            _game.Hud.HighlightChoice(pick);
            await _game.Wait(1.0);
            _game.Hud.HideChoices();
        }
        return pick;
    }

    private void Record(string knot, IReadOnlyList<string> labels)
    {
        foreach (var label in labels) _shownLabels.Add(label);
    }

    // ------------------------------------------------------------------ coverage

    private void CoverageGates()
    {
        var all = Enum.GetValues<Sound>();
        var unheard = all.Where(s => _game.Sfx.Count(s) == 0).ToList();
        foreach (var s in unheard.Where(s => !UnheardSounds.ContainsKey(s)))
            Fail($"sound {s} is never played in the story (or add it to UnheardSounds with a reason)");
        foreach (var s in UnheardSounds.Keys.Where(s => !unheard.Contains(s)))
            Fail($"sound {s} is played now: remove it from UnheardSounds");
        Check(unheard.All(UnheardSounds.ContainsKey), $"every sound is heard ({all.Length - unheard.Count}/{all.Length})");
        var tracks = Enum.GetValues<Track>();
        var silent = tracks.Where(t => _game.Music.Count(t) == 0).ToList();
        foreach (var t in silent) Fail($"music track {t} never plays in the story");
        Check(silent.Count == 0, $"every music track plays ({tracks.Length - silent.Count}/{tracks.Length})");

        using var file = FileAccess.Open(DialogueManager.StoryPath, FileAccess.ModeFlags.Read);
        var scan = InkScan.Parse(file.GetAsText());
        var choices = scan.Choices.Where(c => !c.Fallback).ToList();
        int shown = choices.Count(c => _shownLabels.Any(l => InkScan.Matches(c, l)));
        GD.Print($"[playthrough] Ink choices offered on the canonical routes: {shown}/{choices.Count}; " +
                 "every choice is reached by InkWalkTests' exhaustive Ink walk.");
        Check(shown > 0, "the playthrough records the Ink choices it is offered");
    }

    // ------------------------------------------------------------------ helpers

    protected override Task Pace(double seconds) => _film && !_skipping ? _game.Wait(seconds) : Task.CompletedTask;

    private async Task Do(Verb verb, string hotspot, string? item = null)
    {
        await Pace(0.6);
        await _game.Perform(verb, hotspot, item);
    }

    private Task WaitIdle() => WaitIdle(_game);

    private void Expect(string room, string what) =>
        Check(_game.Room?.Name == room, $"{what} (in {_game.Room?.Name ?? "no room"}, expected {room})");

    /// <summary>Waits for a full-screen image, then lets any line over it finish (or clicks through it) and closes it.</summary>
    private async Task DismissImage(string what)
    {
        await Until(() => _game.Hud.ImageVisible, 60);
        Check(_game.Hud.ImageVisible, $"{what}: shown full screen");
        for (int i = 0; i < 600 && _game.Hud.ImageVisible; i++)
        {
            // a line over the picture: the test clicks through it, the film lets it be read
            if (_game.Hud.ImageHeld)
            {
                if (!_film) Click(new Vector2(240, 140));
            }
            else
            {
                await Pace(2);
                _game.Hud.CloseImage();
            }
            await _game.Wait(0.2);
        }
        Check(!_game.Hud.ImageVisible, $"{what}: closed");
    }
}
