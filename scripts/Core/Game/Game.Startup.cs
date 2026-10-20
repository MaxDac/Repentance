using Godot;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Startup: command-line options, test modes, the title screen and a new game.</summary>
public partial class Game
{
    public override async void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        bool settingsTest = Array.IndexOf(args, "--settings-test") >= 0;
        bool pauseTest = Array.IndexOf(args, "--pause-test") >= 0;
        bool walkTest = Array.IndexOf(args, "--walk-test") >= 0;
        bool film = args.Any(a => a == "--film" || a.StartsWith("--film="));
        bool playthrough = Array.IndexOf(args, "--playthrough") >= 0;
        bool anyTest = settingsTest || pauseTest || walkTest || film || playthrough || Array.IndexOf(args, "--autoplay") >= 0;
        Settings = new GameSettings(anyTest ? "user://autoplay_settings.cfg" : "user://settings.cfg");
        Settings.Load();
        ReportSoundLost();
        Sfx = new Sfx { Name = "Sfx" };
        AddChild(Sfx);
        Sfx.Bind(Settings);
        Music = new Music { Name = "Music", Enabled = Array.IndexOf(args, "--no-music") < 0 };
        AddChild(Music);
        Music.Bind(Settings);
        // film mode is watched, so it may go fullscreen with F11 (the setting is the autoplay copy, not the player's)
        AddChild(new WindowModeController(Settings, !anyTest || film) { Name = "WindowMode" });
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
        if (film || playthrough)
        {
            await new Playthrough(film).Run(this);
            return;
        }
        if (walkTest)
        {
            await new WalkTest().Run(this);
            return;
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
        ShowTitle(true);
        await Hud.Fade(0, 0.8);
        var choice = await Hud.Menu.OpenTitle();
        await Hud.Fade(1, 0.5);
        ShowTitle(false);
        _onTitle = false;
        if (choice is { Action: MenuAction.Load, Save: { } save }) await LoadGame(save);
        else await NewGame();
    }

    /// <summary>The title screen with the patter of its rain; hiding it hands the ambience back to the room, if any.</summary>
    public void ShowTitle(bool show)
    {
        Hud.ShowTitle(show);
        if (show) Sfx.SetAmbient(Sound.Rain);
        else if (Room?.Ambience is { } ambience) Sfx.SetAmbient(ambience.Sound, ambience.VolumeDb);
        else Sfx.SetAmbient(null);
    }

    public async Task NewGame()
    {
        ReleaseTheEnd();
        GameState.Instance.Reset();
        DialogueManager.Instance.ResetInk();
        _playtime = 0;
        // a debug start past the attic gets the notes Micah would have taken on the way there, and the act's kit
        if (StartRoom != "attic")
        {
            var gs = GameState.Instance;
            foreach (var flag in Notes.DebugStartFlags(StartRoom).Concat(MicahKit.DebugFlags(StartRoom))) gs.SetFlag(flag);
            foreach (var item in MicahKit.DebugItems(StartRoom)) gs.GiveItem(item);
            if (MicahKit.DebugAct(StartRoom) > 1) gs.SetStoryAct(MicahKit.DebugAct(StartRoom));
        }
        foreach (var flag in _startFlags) GameState.Instance.SetFlag(flag);
        // a debug start inside an interlude (--flag=interlude1/2): Eleanor's hands are empty, and the act's kit waits
        // in the stash for Micah when her journal hands back
        var state = GameState.Instance;
        int interludeAct = MicahKit.InterludeAct(state.HasFlag);
        if (interludeAct > 0)
        {
            foreach (var id in state.Inventory.ToList()) state.TakeItem(id);
            foreach (var id in MicahKit.InterludeKit(interludeAct)) state.GiveItem(id);
            Repentance.Rooms.Attic.StashMicahItems();
            state.SetStoryAct(interludeAct);
        }
        await ChangeRoom(StartRoom, StartEntry == "start" && RoomTargetError(StartRoom, StartEntry) != null ? FirstEntry : StartEntry);
    }
}
