using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Scripting helpers rooms use: Run, WalkTo, Say and Wait.</summary>
public partial class Game
{
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

    /// <summary>Ends the current spoken line early, as a click would.</summary>
    public void SkipSpeech() => _skipSpeech?.TrySetResult();

    public async Task Say(ISpeaker who, string text)
    {
        _skipSpeech = new TaskCompletionSource();
        var skip = _skipSpeech;
        who.Talking = true;
        Hud.ShowSpeech(text, who);
        Sfx.PlayCues(text);
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
}
