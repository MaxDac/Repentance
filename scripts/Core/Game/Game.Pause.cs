using Godot;
using System;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Space pause/resume and the Escape pause menu.</summary>
public partial class Game
{
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

    /// <summary>Test hook: called instead of closing the game when a menu quits.</summary>
    public Action? QuitOverride { get; set; }

    /// <summary>Closes the game from the title's Quit game or the pause menu's Quit to desktop.</summary>
    public void QuitGame()
    {
        if (QuitOverride != null)
        {
            QuitOverride();
            return;
        }
        Timers.ReleasePending();
        GetTree().Quit();
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
                await ReturnToTitle();
                break;
        }
    }

    /// <summary>Fades out, unloads the story's room and its sound, and opens the title screen.</summary>
    private async Task ReturnToTitle()
    {
        _busy++;
        try { await Hud.Fade(1, 0.5); }
        finally { _busy--; }
        UnloadRoom();
        Sfx.SetAmbient(null);
        Music.Play(null);
        await TitleScreen();
    }
}
