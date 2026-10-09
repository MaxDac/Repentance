using Godot;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Smoke test: plays the whole demo by itself, saving screenshots to screenshots/ and printing
/// AUTOPLAY OK / AUTOPLAY FAILED. Run with: godot -- --autoplay
/// </summary>
public class AutoPlay
{
    private Game _game = null!;
    private readonly HashSet<string> _shotKnots = new();
    private readonly List<string> _failures = new();
    private string _dir = "";
    private int _shot;

    public async Task Run(Game game)
    {
        _game = game;
        _dir = ProjectSettings.GlobalizePath("res://screenshots");
        DirAccess.MakeDirRecursiveAbsolute(_dir);
        // keep Godot from importing the screenshots
        using (FileAccess.Open($"{_dir}/.gdignore", FileAccess.ModeFlags.Write)) { }
        Engine.TimeScale = 3;
        DialogueManager.Instance.AutoChoose = async (knot, options) =>
        {
            GD.Print($"[autoplay] {knot}: {string.Join(" | ", options)}");
            if (_shotKnots.Add(knot))
            {
                _ = game.Hud.ShowChoices(options);
                await Shot($"choices_{knot.Replace('.', '_')}");
                game.Hud.HideChoices();
            }
            return 0;
        };

        try
        {
            await game.ChangeRoom("office", "start");
            Check(GameState.Instance.HasFlag("teddy_gone"), "Teddy left the office");
            Check(GameState.Instance.HasItem("photo"), "got the photo");
            await Shot("office");
            await game.Perform(Verb.Open, "drawer");
            await Shot("office_drawer");
            await game.Perform(Verb.PickUp, "dollar");
            Check(GameState.Instance.HasItem("dollar"), "got the dollar");
            await game.Perform(Verb.LookAt, "window");
            await MouseTest(game);
            await game.Perform(Verb.WalkTo, "door");
            Check(game.Room?.Name == "Lobby", "entered the lobby");

            await Shot("lobby");
            await game.Perform(Verb.TalkTo, "concierge");
            await game.Perform(Verb.WalkTo, "revolving_door");
            Check(game.Room?.Name == "Lobby", "revolving door is gated");
            await game.Perform(Verb.TalkTo, "bellboy");
            await game.Perform(Verb.Give, "bellboy", "dollar");
            Check(GameState.Instance.HasFlag("knows_lantern"), "bellboy tip");
            await game.Perform(Verb.PickUp, "urn");
            Check(GameState.Instance.HasItem("matchbook"), "got the matchbook");
            await game.Perform(Verb.WalkTo, "revolving_door");
            Check(game.Room?.Name == "Speakeasy", "entered the speakeasy");

            await Shot("speakeasy");
            await game.Perform(Verb.TalkTo, "bartender");
            Check(!GameState.Instance.HasFlag("photo_shown"), "Sal blocks the bar");
            await game.Perform(Verb.TalkTo, "sal");
            Check(GameState.Instance.HasFlag("sal_passed"), "password accepted");
            await Shot("speakeasy_inside");
            _ = game.Perform(Verb.TalkTo, "bartender");
            for (int i = 0; i < 600 && !GameState.Instance.HasFlag("ending"); i++) await game.Wait(0.1);
            Check(GameState.Instance.HasFlag("photo_shown"), "showed the photo");
            await game.Wait(1.5);
            await Shot("ending_sal");
            for (int i = 0; i < 600 && !game.Hud.CaptionVisible; i++) await game.Wait(0.1);
            Check(game.Hud.CaptionVisible, "reached 'To be continued'");
            await Shot("ending");
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }

        GD.Print(_failures.Count == 0 ? "AUTOPLAY OK" : "AUTOPLAY FAILED:\n  " + string.Join("\n  ", _failures));
        Engine.TimeScale = 1;
        game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    /// <summary>Drives the real input path: click the floor, then right-click the window (default verb Look at).</summary>
    private async Task MouseTest(Game game)
    {
        Click(new Vector2(420, 180), MouseButton.Left);
        for (int i = 0; i < 100 && game.Player.Position.DistanceTo(new Vector2(420, 180)) > 1; i++) await game.Wait(0.1);
        Check(game.Player.Position.DistanceTo(new Vector2(420, 180)) <= 1, "left click walks to the floor point");
        Click(new Vector2(400, 50), MouseButton.Right);
        for (int i = 0; i < 100 && !game.Busy; i++) await game.Wait(0.05);
        Check(game.Busy, "right click on the window starts 'Look at'");
        await Shot("office_look_window");
        for (int i = 0; i < 200 && game.Busy; i++) await game.Wait(0.1);
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

    private void Check(bool ok, string what)
    {
        GD.Print($"[autoplay] {(ok ? "PASS" : "FAIL")} {what}");
        if (!ok) _failures.Add(what);
    }

    private async Task Shot(string name)
    {
        await _game.Wait(0.4);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
