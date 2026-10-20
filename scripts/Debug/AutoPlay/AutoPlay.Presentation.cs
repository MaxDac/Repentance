using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Content settings and character pose playback checks.</summary>
public partial class AutoPlay
{
    private async Task ContentSettingsTest(Game game)
    {
        const string path = "user://autoplay_settings.cfg";
        if (FileAccess.FileExists(path))
            Check(DirAccess.RemoveAbsolute(path) == Error.Ok, "removed only the isolated test settings");
        Check(game.Settings.Load() && !game.Settings.NudityEnabled, "nudity defaults to off");
        game.Hud.ShowTitle(true);
        Check(!game.SoundLost && !game.Hud.Menu.HasEntry(GameMenu.RestartSoundLabel),
            "a requested Dummy driver (--audio-driver Dummy) isn't mistaken for a lost sound device");
        game.SoundLostOverride = true;
        var title = game.Hud.Menu.OpenTitle();
        Check(game.Hud.Menu.HasEntry(GameMenu.RestartSoundLabel) && game.Hud.Menu.Status == GameMenu.SoundLostText,
            "with the sound device lost at start, the title explains and offers Restart sound");
        await Shot("title_sound_lost");
        Check(game.Hud.Menu.Press("Settings"), "title offers Settings without sound");
        await Observe(0.1);
        Check(game.Hud.Menu.HasEntry(GameMenu.RestartSoundLabel), "settings offer Restart sound too");
        game.SoundLostOverride = null;
        game.Hud.Menu.Press("Back");
        await Observe(0.1);
        Check(!game.Hud.Menu.HasEntry(GameMenu.RestartSoundLabel) && game.Hud.Menu.Status == "",
            "with sound, the title has no Restart sound");
        Check(game.Hud.Menu.Press("Settings"), "title offers Settings");
        await Observe(0.1);
        Check(game.Hud.Menu.Press("Nudity: Off"), "settings offers explicit nudity opt-in");
        await Observe(0.1);
        Check(game.Settings.NudityEnabled, "nudity enabled through title settings");
        var reloaded = new GameSettings(path);
        Check(reloaded.Load() && reloaded.NudityEnabled, "nudity persists across settings instances");
        await Shot("settings_nudity_on");

        var windowMode = DisplayServer.WindowGetMode();
        Check(!game.Settings.Fullscreen && game.Hud.Menu.HasEntry("Full screen: Off"), "full screen defaults to off");
        Check(game.Hud.Menu.Press("Full screen: Off"), "settings offers a full-screen toggle");
        await Observe(0.1);
        Check(game.Settings.Fullscreen && game.Hud.Menu.HasEntry("Full screen: On"), "full screen enabled through settings");
        Check(reloaded.Load() && reloaded.Fullscreen && reloaded.NudityEnabled,
            "full screen persists without clobbering the nudity preference");
        PressKey(Key.F11);
        await Observe(0.1);
        Check(!game.Settings.Fullscreen && game.Hud.Menu.HasEntry("Full screen: Off"),
            "F11 toggles full screen and refreshes the open settings page");
        PressKey(Key.Enter, alt: true);
        await Observe(0.1);
        Check(game.Settings.Fullscreen && game.Hud.Menu.HasEntry("Full screen: On"), "Alt+Enter toggles full screen");
        Check(game.Settings.SetNudity(true) && reloaded.Load() && reloaded.Fullscreen,
            "saving nudity keeps the full-screen preference");
        PressKey(Key.F11);
        await Observe(0.1);
        Check(!game.Settings.Fullscreen && reloaded.Load() && !reloaded.Fullscreen && reloaded.NudityEnabled,
            "full screen turned back off and persisted");
        Check(DisplayServer.WindowGetMode() == windowMode, "automated runs never change the real window mode");

        Check(game.Settings.EffectsVolume == GameSettings.DefaultEffectsVolume && game.Hud.Menu.HasEntry("Effects volume: 80%"),
            "effects volume defaults to 80%");
        Check(game.Hud.Menu.Press("Effects volume"), "settings offers an effects volume");
        await Observe(0.1);
        Check(game.Settings.EffectsVolume == 90 && game.Hud.Menu.HasEntry("Effects volume: 90%") &&
            reloaded.Load() && reloaded.EffectsVolume == 90 && reloaded.NudityEnabled,
            "left click raises the effects volume and persists it alongside the other settings");
        Check(Mathf.IsEqualApprox(AudioServer.GetBusVolumeDb(Sfx.BusIndex), SoundSynth.PercentToDb(90)),
            "the Effects bus follows the setting");
        Check(game.Hud.Menu.PressAlt("Effects volume"), "right click lowers the effects volume");
        await Observe(0.1);
        Check(game.Settings.EffectsVolume == 80 && game.Hud.Menu.HasEntry("Effects volume: 80%"), "back down to 80%");
        Check(game.Settings.SetEffectsVolume(0) && AudioServer.IsBusMute(Sfx.BusIndex), "0% mutes the effects");
        await Observe(0.1);
        Check(game.Hud.Menu.HasEntry("Effects volume: 0%"), "the settings page shows 0%");
        Check(GameSettings.CycleVolume(100, up: true) == 0 && GameSettings.CycleVolume(0, up: false) == 100,
            "the volume wraps around");
        Check(game.Settings.SetEffectsVolume(GameSettings.DefaultEffectsVolume) && !AudioServer.IsBusMute(Sfx.BusIndex),
            "effects volume restored");
        await Observe(0.1);

        Check(game.Settings.MusicVolume == GameSettings.DefaultMusicVolume && game.Hud.Menu.HasEntry("Music volume: 70%"),
            "music volume defaults to 70%");
        Check(game.Hud.Menu.Press("Music volume"), "settings offers a music volume");
        await Observe(0.1);
        Check(game.Settings.MusicVolume == 80 && game.Hud.Menu.HasEntry("Music volume: 80%") &&
            reloaded.Load() && reloaded.MusicVolume == 80 && reloaded.EffectsVolume == GameSettings.DefaultEffectsVolume,
            "left click raises the music volume and persists it beside the effects volume");
        Check(Mathf.IsEqualApprox(AudioServer.GetBusVolumeDb(Music.BusIndex), SoundSynth.PercentToDb(80)) &&
            Mathf.IsEqualApprox(AudioServer.GetBusVolumeDb(Sfx.BusIndex), SoundSynth.PercentToDb(GameSettings.DefaultEffectsVolume)),
            "the Music bus follows its own setting, the Effects bus is untouched");
        Check(game.Hud.Menu.PressAlt("Music volume"), "right click lowers the music volume");
        await Observe(0.1);
        Check(game.Settings.MusicVolume == 70 && game.Hud.Menu.HasEntry("Music volume: 70%"), "music back down to 70%");
        Check(game.Settings.SetMusicVolume(0) && AudioServer.IsBusMute(Music.BusIndex) && !AudioServer.IsBusMute(Sfx.BusIndex),
            "0% mutes only the music");
        Check(game.Settings.SetMusicVolume(GameSettings.DefaultMusicVolume) && !AudioServer.IsBusMute(Music.BusIndex),
            "music volume restored");
        await Observe(0.1);

        PressKey(Key.Escape);
        await Observe(0.1);
        Check(game.Hud.Menu.IsOpen && game.Hud.Menu.Press("New game"), "Esc returns from settings to the title");
        await title;
        game.Hud.ShowTitle(false);

        foreach (int act in new[] { 2, 3 })
        {
            var save = new SaveData { Room = "club_stage", StoryAct = act, X = 86, Y = 208 };
            await game.LoadGame(save);
            var eleanor = game.Room!.FindActor("eleanor")!;
            var position = eleanor.Position;
            Check(eleanor.Texture!.ResourcePath.EndsWith("/eleanor_stage.png"), $"Act {act}: opted-in sprite on load");
            await Shot($"eleanor_act{act}_nudity_on");
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(game.GetTree().Paused && game.Hud.Menu.Press("Settings"), $"Act {act}: pause offers Settings");
            await Observe(0.1);
            PressKey(Key.F11);
            await Observe(0.1);
            Check(game.GetTree().Paused && game.Settings.Fullscreen && game.Hud.Menu.HasEntry("Full screen: On"),
                $"Act {act}: F11 works while paused");
            PressKey(Key.F11);
            await Observe(0.1);
            Check(!game.Settings.Fullscreen, $"Act {act}: F11 toggles back while paused");
            Check(game.Hud.Menu.Press("Nudity: On"), $"Act {act}: nudity can be disabled");
            await Observe(0.1);
            Check(!game.Settings.NudityEnabled &&
                eleanor.Texture!.ResourcePath.EndsWith("/eleanor_stage_clothed.png") &&
                eleanor.Position == position && eleanor.Frames == 11,
                $"Act {act}: disabling immediately restores dressed Eleanor without moving her");
            Check(reloaded.Load() && !reloaded.NudityEnabled, $"Act {act}: opt-out persists");
            await Shot($"eleanor_act{act}_nudity_off");
            PressKey(Key.Escape);
            await Observe(0.1);
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(!game.GetTree().Paused && !game.Hud.Menu.IsOpen, $"Act {act}: back from settings resumes correctly");
            await game.LoadGame(save);
            Check(game.Room!.FindActor("eleanor")!.Texture!.ResourcePath.EndsWith("/eleanor_stage_clothed.png"),
                $"Act {act}: loading a save respects the current opt-out");
            Check(game.Settings.SetNudity(true), $"Act {act}: re-enabled nudity");
            Check(game.Room.FindActor("eleanor")!.Texture!.ResourcePath.EndsWith("/eleanor_stage.png"),
                $"Act {act}: enabling immediately restores the opted-in variant");
        }
        game.Hud.ShowCloseUp(CloseUps.Stage, 0);
        Check(game.Hud.InsetName == "stage_closeup", "stage close-up uses the opted-in variant");
        Check(game.Settings.SetNudity(false), "reset isolated preference");
        Check(game.Hud.CurrentCloseUp == CloseUps.Stage && game.Hud.InsetName == "stage_closeup_clothed",
            "a close-up's variant swaps in place when the setting changes");
        game.Hud.HideCloseUp(0);
        Check(!game.Hud.InsetVisible && game.Hud.CurrentCloseUp == null, "close-up hidden");
        await game.ChangeRoom("attic", "start");
        await WaitIdle(game);
        GameState.Instance.Reset();
        DialogueManager.Instance.ResetInk();
        foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
    }

    private async Task ObservePose(PosePlayback pose)
    {
        string name = pose.Action!;
        int frame = pose.Frame;
        if (frame == 0)
        {
            _poseCounts[name] = _poseCounts.GetValueOrDefault(name) + 1;
            _lastPoseFrame[pose] = -1;
        }
        Check(frame == _lastPoseFrame.GetValueOrDefault(pose, -1) + 1, $"{name}: ordered frame {frame}");
        _lastPoseFrame[pose] = frame;
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        Check(pose.Action == name && pose.Frame == frame, $"{name}: frame {frame} held for rendering");
        if (name == "eleanor_sheet_rise")
            Check(_game.Room!.GetNode<Sprite2D>("EleanorFigure").ZIndex == (frame >= 4 ? 2 : 0),
                $"{name}: frame {frame} is on the correct side of the bed rail");
        if (name == "eleanor_bed_turn")
            Check(_game.Room!.GetNode<Sprite2D>("EleanorFigure").ZIndex == 0,
                $"{name}: frame {frame} stays behind the bed rail");
        var image = _game.GetViewport().GetTexture().GetImage();
        Check(image.SavePng($"{_dir}/{++_shot:00}_pose_{name}_{frame}.png") == Error.Ok, $"{name}: saved frame {frame}");
    }

    private async Task PosePlaybackTest(Game game)
    {
        var player = game.Player;
        var character = player.Character;
        var observer = PosePlayback.FrameObserver;
        PosePlayback.FrameObserver = null;
        double timeScale = Engine.TimeScale;
        try
        {
            // Same turn as PlayPose: a scaled wait can outlive the clip when the autoplay clock hitches.
            var action = player.PlayPose("micah_recover");
            player.Poses.Process(0.05);
            Check(player.Poses.Playing && !action.IsCompleted, "pose is still playing before the character swap");
            player.SetCharacter(character);
            Check(!await action && !player.Poses.Active, "character swap cancels awaited playback and restores animation");

            Engine.TimeScale = 1;
            var normal = player.PlayPose("micah_recover");
            await game.Wait(0.2);
            Check(player.Poses.Playing && !normal.IsCompleted, "normal-speed check: pose is still playing before the character swap");
            player.SetCharacter(character);
            Check(!await normal && !player.Poses.Active, "normal-speed check: character swap cancels awaited playback and restores animation");

            player.SetPose("micah_supine");
            player.Face(Facing.Right);
            var right = player.HeadPosition - player.GlobalPosition;
            player.Face(Facing.Left);
            var left = player.HeadPosition - player.GlobalPosition;
            Check(Mathf.IsEqualApprox(right.X, -left.X) && Mathf.IsEqualApprox(right.Y, left.Y), "wide-pose speech mirrors around the contact anchor");
            var first = player.PlayPose("micah_recover");
            var second = player.PlayPose("micah_kneel_rise");
            Check(!await first, "a new pose cancels the previous await");
            player.Stop();
            Check(!await second && !player.Poses.Active, "stopping restores the sheet and cancels playback");
            var actor = new Actor { Id = "pose_test", Texture = GD.Load<Texture2D>("res://assets/art/sprites/sal.png"), DepthScale = false };
            game.Room!.World.AddChild(actor);
            actor.SetPose("micah_supine");
            actor.FaceLeft(false);
            var rightBounds = actor.Bounds;
            actor.FaceLeft(true);
            Check(Mathf.IsEqualApprox(actor.Bounds.Size.X, rightBounds.Size.X), "actor wide-pose hit bounds survive mirroring");
            Check(actor.Contains(actor.GlobalPosition + actor.Poses!.Bounds.GetCenter()), "actor hit testing uses the displayed pose");
            var leaving = actor.PlayPose("micah_recover");
            game.Room.World.RemoveChild(actor);
            Check(!await leaving, "actor removal cancels playback");
            actor.QueueFree();
        }
        finally
        {
            Engine.TimeScale = timeScale;
            player.SetCharacter(character);
            PosePlayback.FrameObserver = observer;
        }
    }
}
