using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Scripting helpers rooms use: Run, WalkTo, Say, Think and Wait.</summary>
public partial class Game
{
    /// <summary>Runs a scripted sequence, blocking player input and hiding the verbs while it runs.</summary>
    public async Task Run(Func<Task> sequence)
    {
        _busy++;
        try { await sequence(); }
        catch (Exception ex)
        {
            GD.PushError(ex.ToString());
            SequenceFailed?.Invoke(ex);
        }
        finally { _busy--; }
    }

    private TaskCompletionSource<bool>? _theEnd;

    /// <summary>How long "The End" stays up before the game returns to the title by itself (game seconds).</summary>
    public const double TheEndSeconds = 10;

    /// <summary>
    /// Whether a held "The End" leaves for the title on a click, a key or <see cref="TheEndSeconds"/>. Automated runs
    /// turn it off so the caption stays up for their checks and for the next seeded ending.
    /// </summary>
    public bool EndReturnsToTitle { get; set; } = true;

    public bool TheEndHeld => _theEnd != null;

    /// <summary>
    /// Keeps the final caption up (and the game busy). True when the player leaves it for the title (a click, a key or
    /// the timeout); false when a load, a new game or a test replaces the story first.
    /// </summary>
    public async Task<bool> HoldTheEnd()
    {
        ReleaseTheEnd();
        var hold = new TaskCompletionSource<bool>();
        _theEnd = hold;
        _ = TimeOutTheEnd(hold);
        bool toTitle = await hold.Task;
        if (_theEnd == hold) _theEnd = null;
        return toTitle;
    }

    private async Task TimeOutTheEnd(TaskCompletionSource<bool> hold)
    {
        const double step = 0.25;
        for (double t = 0; t < TheEndSeconds; t += step)
        {
            if (hold.Task.IsCompleted) return;
            if (!EndReturnsToTitle) t = -step;
            await Wait(step);
        }
        hold.TrySetResult(true);
    }

    /// <summary>The player leaves a held "The End" for the title (ignored while <see cref="EndReturnsToTitle"/> is off).</summary>
    public void DismissTheEnd()
    {
        if (EndReturnsToTitle) _theEnd?.TrySetResult(true);
    }

    /// <summary>Lets a held "The End" go (a load, a new game, or the autoplay test seeding its next ending).</summary>
    public void ReleaseTheEnd()
    {
        _theEnd?.TrySetResult(false);
        _theEnd = null;
    }

    /// <summary>
    /// After "The End": blocks input and autosave at once, then, once the epilogue's scripted chain has unwound,
    /// unloads the story and opens the title screen.
    /// </summary>
    public void LeaveStoryForTitle()
    {
        _onTitle = true;
        _ = ReturnToTitleWhenIdle();
    }

    private async Task ReturnToTitleWhenIdle()
    {
        while (Busy) await Wait(0.05);
        await ReturnToTitle();
    }

    /// <summary>Raised when <see cref="Run"/> swallows an exception, so automated runs can fail on it.</summary>
    public static event Action<Exception>? SequenceFailed;

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
        bool eleanor = Player.Character.StartsWith("eleanor");
        ISpeaker who = (eleanor ? id == "eleanor" : id == "micah" || id == "daniel" || id == Player.Character)
            ? Player
            : Room?.FindSpeaker(id) ?? Player;
        return Say(who, text);
    }

    /// <summary>Ends the current spoken line early, as a click would.</summary>
    public void SkipSpeech() => _skipSpeech?.TrySetResult();

    public Task Say(ISpeaker who, string text) => Speak(who, text, whisper: false);

    /// <summary>The player says a line under her breath: drawn faded and lowercase, with no voice cues.</summary>
    public Task Whisper(string text) => Speak(Player, text, whisper: true);

    private async Task Speak(ISpeaker who, string text, bool whisper)
    {
        _skipSpeech = new TaskCompletionSource();
        var skip = _skipSpeech;
        who.Talking = true;
        Hud.ShowSpeech(text, who, whisper);
        if (!whisper) Sfx.PlayCues(text);
        var seconds = Math.Clamp(0.9 + text.Length * 0.055, 1.5, 7.0);
        // ignore the click that triggered this line
        await Wait(0.15);
        await Task.WhenAny(Wait(seconds), skip.Task);
        who.Talking = false;
        Hud.HideSpeech();
        if (_skipSpeech == skip) _skipSpeech = null;
        await Wait(0.12);
    }

    /// <summary>
    /// Micah's journal narration: a thought shown along the top of the screen in faded ink. Blocks like speech
    /// (timed by length, a click skips it) but nobody's mouth moves.
    /// </summary>
    public async Task Think(string text)
    {
        _skipSpeech = new TaskCompletionSource();
        var skip = _skipSpeech;
        Hud.ShowThought(text);
        var seconds = Math.Clamp(1.2 + text.Length * 0.06, 2.0, 8.0);
        await Wait(0.15);
        await Task.WhenAny(Wait(seconds), skip.Task);
        Hud.HideThought();
        if (_skipSpeech == skip) _skipSpeech = null;
        await Wait(0.12);
    }

    public Task Wait(double seconds) => Timers.Wait(this, seconds);
}
