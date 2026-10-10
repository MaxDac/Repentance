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
        // never touch the player's own saves
        SaveSystem.Directory = "user://autoplay_saves";
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
            return 0;
        };

        try
        {
            var gs = GameState.Instance;

            // ---- prologue: the attic, played through the real mouse input where it matters
            await TitleMenuTest(game, expectSaves: false);
            await game.ChangeRoom("attic", "start");
            Check(game.Player.Character == "daniel", "prologue plays as Daniel");
            await Shot("attic");
            await WheelTest(game);
            await game.Perform(Verb.Talk, "hatch");
            await game.Perform(Verb.Hand, "sheet");
            Check(gs.HasFlag("sheet_lifted"), "lifted the dust sheet");
            await game.Perform(Verb.Hand, "boxes");
            Check(gs.HasFlag("boxes_spilled"), "spilled the boxes");
            await game.Perform(Verb.Hand, "suitcase");
            Check(gs.HasItem("suitcase_key"), "found the key in the suitcase");
            await game.Perform(Verb.UseItem, "trunk", "suitcase_key");
            Check(!gs.HasFlag("trunk_open"), "the suitcase key doesn't fit the trunk");
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
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "Office", "can't leave without the drawer things");
            await game.Perform(Verb.Hand, "revolver");
            await game.Perform(Verb.Hand, "dollar");
            await game.Perform(Verb.Hand, "lockpick");
            Check(gs.HasItem("revolver") && gs.HasItem("dollar") && gs.HasItem("lockpick"), "took the revolver, the dollar and the lockpick");
            await Shot("office_drawer_empty");
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
            Check(gs.HasFlag("knows_lantern") && gs.HasFlag("staff_elevator"), "bribed the bellboy for the staff elevator");
            await game.Perform(Verb.Walk, "service_door");
            Check(game.Room?.Name == "EleanorRoom", "staff elevator up to Eleanor's room");

            await Shot("eleanor_room");
            await game.Perform(Verb.Hand, "desk_drawer");
            Check(!gs.HasFlag("eleanor_drawer_open"), "the drawer is locked");
            await game.Perform(Verb.UseItem, "desk_drawer", "lockpick");
            Check(gs.HasFlag("eleanor_drawer_open"), "lockpicked the drawer");
            await Shot("eleanor_drawer");
            await game.Perform(Verb.Hand, "paper");
            Check(gs.HasItem("combination"), "got the combination");
            await game.Perform(Verb.Hand, "closet");
            Check(gs.HasFlag("closet_open"), "opened the closet");
            await game.Perform(Verb.UseItem, "safe", "combination");
            Check(gs.HasFlag("safe_open"), "opened the safe");
            await Shot("eleanor_safe");
            await game.Perform(Verb.Hand, "brass_box");
            Check(gs.HasItem("brass_box"), "took the brass box");
            await Shot("eleanor_safe_empty");
            await game.ItemVerb(Verb.Hand, "brass_box");
            Check(!gs.HasItem("brass_box") && gs.HasItem("card") && gs.HasItem("matchbook"), "the brass box holds a card and the matchbook");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "Lobby", "back down in the lobby");
            await SaveLoadTest(game);
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room?.Name == "Speakeasy", "entered the speakeasy");

            await Shot("speakeasy");
            await game.Perform(Verb.Talk, "bartender");
            Check(game.Room?.Name == "Speakeasy", "Sal blocks the bar");
            await game.Perform(Verb.Talk, "sal");
            Check(gs.HasFlag("sal_passed") && !gs.HasFlag("thrown_out"), "no password, but Sal takes the bribe");
            await Shot("speakeasy_inside");
            var bar = game.Perform(Verb.Talk, "bartender");
            await Until(() => game.Room?.Name == "Alley");
            Check(game.Room?.Name == "Alley", "the bartender has Sal throw Micah out back");
            await game.Wait(2.5);
            await Shot("alley");
            await bar;

            // ---- the convent
            Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_talked"), "the nun questions Micah in the corridor");
            await Shot("convent_corridor");
            await game.Perform(Verb.Walk, "cell_door");
            Check(game.Room?.Name == "ConventCell", "entered Eleanor's cell");
            await Shot("convent_cell");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "ConventCell", "can't leave the cell without the mirror");
            await game.Perform(Verb.Hand, "nightstand");
            Check(gs.HasFlag("cell_drawer_open"), "opened the nightstand drawer");
            await Shot("convent_cell_drawer");
            var take = game.Perform(Verb.Hand, "mirror");
            await Until(() => game.Hud.ImageVisible);
            Check(game.Hud.ImageVisible, "the symbol behind the mirror is shown full screen");
            await Shot("triquetra");
            game.Hud.CloseImage();
            await take;
            await game.Perform(Verb.Hand, "comb");
            Check(gs.HasItem("mirror") && !gs.HasItem("comb"), "took only the mirror");
            await Shot("convent_cell_after");

            var leave = game.Perform(Verb.Walk, "exit");
            await Until(() => game.Room?.Name == "ConventRoad");
            Check(game.Room?.Name == "ConventRoad", "Eleanor is waiting outside the convent");
            await game.Wait(3);
            await Shot("convent_road");
            await Until(() => game.Room?.Name == "MotelNight");
            Check(game.Player.Character == "micah_dressing", "Micah getting dressed in the motel");
            await game.Wait(2);
            await Shot("motel_night");
            await Until(() => game.Room?.Name == "Attic");
            await game.Wait(2.5);
            await Shot("attic_night");
            await leave;

            // ---- end of Act 1, then Act 2 the next day
            Check(gs.StoryAct == 2 && gs.HasItem("journal") && game.Player.Character == "daniel", "Act 2: Daniel is back with the journal");
            await Shot("attic_act2");
            var read = game.ItemVerb(Verb.Hand, "journal");

            // ---- Act 2, 1927: the cathedral, then the map of Chicago
            await Until(() => game.Room?.Name == "ChurchExterior");
            Check(gs.HasItem("mirror"), "reading again leads back to 1927 with Micah's things");
            await game.Wait(1.5);
            await Shot("church_exterior_act2");
            await Until(() => game.Room?.Name == "ChurchInterior");
            Check(gs.HasFlag("act2_church_thought"), "Micah thinks about Eleanor outside the cathedral, then goes in");
            await game.Wait(2);
            await Shot("church_act2");
            await Until(() => game.Room?.Name == "ChicagoMap");
            Check(gs.HasFlag("caleb_met") && !gs.HasFlag("act2_church"), "Micah talks with Caleb and walks out");
            Check(!game.Player.Visible, "the player isn't drawn on the map");
            await read;
            await WaitIdle(game);
            await Shot("map");
            Check(game.Room?.FindHotspot("club")?.Visible == false, "the club isn't on the map yet");
            await game.Perform(Verb.Walk, "church");
            Check(game.Room?.Name == "ChicagoMap", "Micah won't go back to the church");

            await game.Perform(Verb.Walk, "library");
            Check(game.Room?.Name == "Library" && game.Player.Visible, "went to the library");
            Check(game.Room?.FindHotspot("librarian")?.Visible == true && game.Room?.FindHotspot("rose")?.Visible == false, "the night librarian is there, not Rose");
            await Shot("library_night");
            await game.Perform(Verb.UseItem, "librarian", "revolver");
            Check(!gs.HasFlag("library_banned"), "no gun before asking");
            var ask = game.Perform(Verb.Talk, "librarian");
            await Until(() => game.Hud.ImageVisible);
            Check(game.Hud.ImageVisible, "the symbol is shown full screen during the talk");
            await Shot("librarian_symbol");
            game.Hud.CloseImage();
            await ask;
            Check(gs.HasFlag("librarian_refused"), "the librarian won't talk");
            await game.Perform(Verb.UseItem, "librarian", "revolver");
            Check(gs.HasItem("book") && gs.HasFlag("library_banned") && game.Room?.Name == "ChicagoMap", "threatened the librarian into giving up the book");
            await game.Perform(Verb.Walk, "library");
            Check(game.Room?.Name == "ChicagoMap", "the library is off limits now");

            await game.ItemVerb(Verb.Hand, "book");
            Check(!gs.HasItem("address"), "the book is only read at the office");
            await game.Perform(Verb.Walk, "office");
            Check(game.Room?.Name == "Office", "back at the office");
            await game.ItemVerb(Verb.Hand, "book");
            Check(gs.HasItem("address") && gs.HasFlag("club_unlocked"), "an address slipped out of the book");
            await Shot("office_book");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "ChicagoMap" && game.Room?.FindHotspot("club")?.Visible == true, "the club is on the map now");
            await Shot("map_club");
            await game.Perform(Verb.Walk, "club");

            // ---- the temporary story: every location in order
            Check(game.Room?.Name == "ClubHall" && !gs.HasFlag("on_map"), "entered the Starlight");
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
            await Shot("street");

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
        var slot = game.Hud.SlotCenter(IndexOf("crowbar"));
        Move(slot);
        await Shot("attic_inventory");
        Click(slot, MouseButton.Left);
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
        var slot = game.Hud.SlotCenter(IndexOf("journal"));
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

    private static int IndexOf(string item)
    {
        var inv = GameState.Instance.Inventory;
        for (int i = 0; i < inv.Count; i++)
            if (inv[i] == item) return i;
        return 0;
    }

    /// <summary>
    /// Autosave on room change, Esc pause menu, saving to slot 1 through the menu, wiping progress and
    /// loading the slot back.
    /// </summary>
    private async Task SaveLoadTest(Game game)
    {
        var gs = GameState.Instance;
        await WaitIdle(game);
        await game.Wait(0.1);
        var auto = SaveSystem.Read(SaveSystem.AutosaveSlot);
        Check(auto is { Room: "lobby" } && auto.Flags.Contains("seen_lobby"), "autosave written after a room change");

        PressKey(Key.Escape);
        await game.Wait(0.1);
        Check(game.Hud.Menu.IsOpen && game.GetTree().Paused, "Esc opens the pause menu and pauses the game");
        await Shot("pause_menu");
        Check(game.Hud.Menu.Press("Save game"), "pause menu offers Save game");
        await game.Wait(0.1);
        await Shot("save_slots");
        Check(game.Hud.Menu.Press("Slot 1"), "save menu lists slot 1");
        await game.Wait(0.1);
        var saved = SaveSystem.Read(SaveSystem.ManualSlot(0));
        Check(saved is { Room: "lobby", RoomTitle: "Aurelian Hotel" } && saved.Inventory.Contains("matchbook"), "saved to slot 1 from the menu");
        PressKey(Key.Escape);
        await game.Wait(0.1);
        Check(!game.Hud.Menu.IsOpen && !game.GetTree().Paused, "Esc resumes the game");
        if (saved == null) return;

        var ink = DialogueManager.Instance.SaveInk();
        gs.Reset();
        DialogueManager.Instance.ResetInk();
        await game.ChangeRoom("street", "lobby");
        await WaitIdle(game);
        Check(!gs.HasItem("matchbook") && game.Room?.Name == "Street", "progress wiped before loading");

        await game.LoadGame(saved);
        Check(game.Room?.Name == "Lobby", "load returns to the saved room");
        Check(gs.HasItem("matchbook") && gs.HasItem("photo") && gs.HasFlag("knows_lantern") && gs.HasFlag("seen_lobby"),
            "load restores items and flags");
        Check(game.Player.Position.DistanceTo(new Vector2(saved.X, saved.Y)) < 0.5f, "load restores the player's position");
        Check(ink.Length > 0 && DialogueManager.Instance.SaveInk() == ink, "load restores the Ink state");
        await Shot("lobby_loaded");
        await TitleMenuTest(game, expectSaves: true);
    }

    /// <summary>Shows the title menu: Continue/Load are only offered once a save exists.</summary>
    private async Task TitleMenuTest(Game game, bool expectSaves)
    {
        game.Hud.ShowTitle(true);
        var menu = game.Hud.Menu.OpenTitle();
        await game.Hud.Fade(0, 0.1);
        await Shot(expectSaves ? "title_with_saves" : "title_new");
        bool canContinue = game.Hud.Menu.Press("Continue");
        Check(canContinue == expectSaves, expectSaves ? "title offers Continue once saved" : "title hides Continue without saves");
        if (!canContinue) game.Hud.Menu.Press("New game");
        var result = await menu;
        Check(result.Action == (expectSaves ? MenuAction.Load : MenuAction.NewGame) && (result.Save != null) == expectSaves,
            "title menu returns the chosen action");
        game.Hud.ShowTitle(false);
    }

    private void PressKey(Key key)
    {
        foreach (var pressed in new[] { true, false })
            _game.GetViewport().PushInput(new InputEventKey { Keycode = key, PhysicalKeycode = key, Pressed = pressed }, true);
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
        await _game.Wait(0.4);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
