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

    private TaskCompletionSource? _theEnd;

    /// <summary>Keeps the final caption up (and the game busy) until a load or a new game replaces the story.</summary>
    public Task HoldTheEnd()
    {
        _theEnd = new TaskCompletionSource();
        return _theEnd.Task;
    }

    /// <summary>Lets a held "The End" go (a load, a new game, or the autoplay test seeding its next ending).</summary>
    public void ReleaseTheEnd()
    {
        _theEnd?.TrySetResult();
        _theEnd = null;
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
