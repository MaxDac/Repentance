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
            var gs = GameState.Instance;

            // ---- prologue: the attic, played through the real mouse input where it matters
            await game.ChangeRoom("attic", "start");
            Check(game.Player.Character == "daniel", "prologue plays as Daniel");
            await Shot("attic");
            await WheelTest(game);
            await game.Perform(Verb.Talk, "hatch");
            await game.Perform(Verb.Hand, "sheet");
            Check(gs.HasFlag("sheet_lifted"), "lifted the dust sheet");
            await game.Perform(Verb.Hand, "boxes");
            Check(gs.HasFlag("boxes_spilled"), "spilled the boxes");
            await game.Perform(Verb.Hand, "papers");
            Check(gs.HasItem("crowbar"), "found the crowbar");
            await Shot("attic_mess");
            await InventoryTest(game);
            await ReadJournal(game);

            // ---- 1927
            Check(game.Room?.Name == "Office", "journal leads to the office");
            Check(game.Player.Character == "micah", "story continues as Micah");
            Check(gs.HasFlag("teddy_gone"), "Teddy left the office");
            Check(gs.HasItem("photo"), "got the photo");
            await Shot("office");
            await game.Perform(Verb.Hand, "drawer");
            await Shot("office_drawer");
            await game.Perform(Verb.Hand, "dollar");
            Check(gs.HasItem("dollar"), "got the dollar");
            await MouseTest(game);
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "Lobby", "entered the lobby");

            await Shot("lobby");
            await game.Perform(Verb.Talk, "concierge");
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room?.Name == "Street", "revolving door leads to the street before the tip");
            await game.Perform(Verb.Walk, "lobby_door");
            Check(game.Room?.Name == "Lobby", "back in the lobby");
            await game.Perform(Verb.Talk, "bellboy");
            await game.Perform(Verb.UseItem, "bellboy", "dollar");
            Check(gs.HasFlag("knows_lantern"), "bellboy tip");
            await game.Perform(Verb.Hand, "urn");
            Check(gs.HasItem("matchbook"), "got the matchbook");
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room?.Name == "Speakeasy", "entered the speakeasy");

            await Shot("speakeasy");
            await game.Perform(Verb.Talk, "bartender");
            Check(!gs.HasFlag("photo_shown"), "Sal blocks the bar");
            await game.Perform(Verb.Talk, "sal");
            Check(gs.HasFlag("sal_passed"), "password accepted");
            await Shot("speakeasy_inside");
            await game.Perform(Verb.Talk, "bartender");
            Check(gs.HasFlag("photo_shown") && gs.HasFlag("club_lead"), "bartender points to the Starlight");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "Street", "speakeasy door leads to the street");

            // ---- the temporary story: every location in order
            await Shot("street");
            await game.Perform(Verb.Walk, "club_door");
            Check(game.Room?.Name == "ClubHall", "entered the Starlight");
            await Shot("club_hall");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "ClubLounge", "entered the lounge");
            await Shot("club_lounge");
            await game.Perform(Verb.Talk, "harrington");
            Check(gs.HasFlag("harrington_met"), "met Teddy's father in the lounge");
            await game.Perform(Verb.Walk, "stage_exit");
            Check(game.Room?.Name == "ClubStage", "entered the stage room");
            await Shot("club_stage");
            await game.Perform(Verb.Talk, "eleanor");
            Check(gs.HasItem("key"), "Eleanor gives Micah her key");
            await Shot("club_stage_after");
            await game.Perform(Verb.Walk, "lounge_exit");
            await game.Perform(Verb.Walk, "hall_exit");
            await game.Perform(Verb.Walk, "street_door");
            Check(game.Room?.Name == "Street", "back on the street");

            await game.Perform(Verb.Walk, "hotel_door");
            Check(game.Room?.Name == "AurelianRoom", "entered Eleanor's suite");
            await game.Perform(Verb.Hand, "vanity");
            Check(gs.HasItem("diary"), "found the diary");
            await Shot("aurelian_room");
            await game.Perform(Verb.Walk, "exit");

            await game.Perform(Verb.Walk, "church_door");
            Check(game.Room?.Name == "ChurchExterior", "at the cathedral steps");
            await Shot("church_exterior");
            await game.Perform(Verb.Walk, "doors");
            Check(game.Room?.Name == "ChurchInterior", "inside the cathedral");
            await game.Perform(Verb.Talk, "caleb");
            Check(gs.HasFlag("library_lead") && !gs.HasItem("diary"), "Caleb reads the diary");
            await Shot("church_interior");
            await game.Perform(Verb.Walk, "doors");
            await game.Perform(Verb.Walk, "exit");

            await game.Perform(Verb.Walk, "library_door");
            Check(game.Room?.Name == "Library", "entered the library");
            await game.Perform(Verb.Talk, "rose");
            Check(gs.HasFlag("rose_tip"), "Rose remembers Eleanor");
            await Shot("library");
            await game.Perform(Verb.Hand, "shelves_right");
            Check(gs.HasItem("ledger"), "found the ledger");
            await game.Perform(Verb.Walk, "exit");

            await game.Perform(Verb.Walk, "motel_door");
            Check(game.Room?.Name == "MotelRoom", "entered the motel room");
            await game.Perform(Verb.Hand, "bed");
            Check(gs.HasItem("map"), "found the map");
            await Shot("motel_room");
            await game.Perform(Verb.Walk, "exit");

            await game.Perform(Verb.Walk, "road_out");
            Check(game.Room?.Name == "Outskirts", "drove out of town");
            await Shot("outskirts");
            _ = game.Perform(Verb.Hand, "disturbed_earth");
            for (int i = 0; i < 600 && !gs.HasFlag("ending"); i++) await game.Wait(0.1);
            Check(gs.HasItem("evidence"), "dug up the evidence");
            await game.Wait(2.5);
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

    /// <summary>Right-click the trunk to open the verb wheel, then click the boot.</summary>
    private async Task WheelTest(Game game)
    {
        var trunk = new Vector2(432, 205);
        Move(trunk);
        Click(trunk, MouseButton.Right);
        await game.Wait(0.1);
        Check(game.Hud.Wheel.IsOpen, "right click opens the verb wheel");
        Move(game.Hud.Wheel.SlotCenter(Verb.Kick));
        await game.Wait(0.1);
        GD.Print($"[probe] wheel rect {game.Hud.Wheel.GetGlobalRect()} vis {game.Hud.Wheel.IsVisibleInTree()} hovered {game.GetViewport().GuiGetHoveredControl()?.GetPath()} mouse {game.GetViewport().GetMousePosition()} slot {game.Hud.Wheel.SlotCenter(Verb.Kick)}");
        await Shot("attic_wheel");
        Click(game.Hud.Wheel.SlotCenter(Verb.Kick), MouseButton.Left);
        for (int i = 0; i < 200 && !GameState.Instance.HasFlag("trunk_kicked"); i++) await game.Wait(0.05);
        await WaitIdle(game);
        Check(!game.Hud.Wheel.IsOpen && GameState.Instance.HasFlag("trunk_kicked"), "wheel 'Kick' on the trunk");
    }

    /// <summary>Open the satchel, pick up the crowbar as the cursor and click it on the trunk.</summary>
    private async Task InventoryTest(Game game)
    {
        Click(game.Hud.SatchelCenter, MouseButton.Left);
        await game.Wait(0.1);
        Check(game.Hud.InventoryOpen, "satchel opens the inventory");
        Move(game.Hud.SlotCenter(0));
        await Shot("attic_inventory");
        Click(game.Hud.SlotCenter(0), MouseButton.Left);
        await game.Wait(0.1);
        Check(game.Carried == "crowbar" && !game.Hud.InventoryOpen, "clicking an item holds it as the cursor");
        var trunk = new Vector2(432, 205);
        Move(trunk);
        await Shot("attic_carry_crowbar");
        Click(trunk, MouseButton.Left);
        for (int i = 0; i < 100 && !game.Busy; i++) await game.Wait(0.05);
        await game.Wait(1.2);
        await Shot("attic_trunk_open");
        await WaitIdle(game);
        Check(GameState.Instance.HasFlag("trunk_open") && GameState.Instance.HasItem("journal"), "crowbar opens the trunk");
    }

    /// <summary>Right-click the journal in the satchel and choose the hand: reading it starts 1927.</summary>
    private async Task ReadJournal(Game game)
    {
        await WaitIdle(game);
        Click(game.Hud.SatchelCenter, MouseButton.Left);
        for (int i = 0; i < 40 && !game.Hud.InventoryOpen; i++) await game.Wait(0.05);
        await game.Wait(0.1);
        var slot = game.Hud.SlotCenter(0);
        Move(slot);
        Click(slot, MouseButton.Right);
        await game.Wait(0.1);
        Check(game.Hud.Wheel.IsOpen, "right click on an item opens the wheel");
        Move(game.Hud.Wheel.SlotCenter(Verb.Hand));
        await Shot("journal_wheel");
        Click(game.Hud.Wheel.SlotCenter(Verb.Hand), MouseButton.Left);
        for (int i = 0; i < 400 && !game.Hud.CaptionVisible; i++) await game.Wait(0.05);
        await Shot("chicago_1927");
        for (int i = 0; i < 1200 && (game.Room?.Name != "Office" || !GameState.Instance.HasFlag("teddy_gone") || game.Busy); i++)
            await game.Wait(0.1);
    }

    /// <summary>Drives the real input path in 1927: left click the floor walks, left click the window looks at it.</summary>
    private async Task MouseTest(Game game)
    {
        var floor = new Vector2(420, 220);
        Click(floor, MouseButton.Left);
        for (int i = 0; i < 100 && game.Player.Position.DistanceTo(floor) > 1; i++) await game.Wait(0.1);
        Check(game.Player.Position.DistanceTo(floor) <= 1, "left click walks to the floor point");
        Move(new Vector2(400, 80));
        Click(new Vector2(400, 80), MouseButton.Left);
        for (int i = 0; i < 100 && !game.Busy; i++) await game.Wait(0.05);
        Check(game.Busy, "left click on the window looks at it");
        await Shot("office_look_window");
        await WaitIdle(game);
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
