using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Interface checks driven through real input: the verb wheel, inventory, mouse, saves, title menu and notepad.</summary>
public partial class AutoPlay
{
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
        var trunk = new Vector2(432, 205);
        Move(trunk);
        await game.Wait(0.05);
        Check(game.Hud.InventoryOpen, "moving away before ever reaching the case keeps the inventory open");
        var slot = game.Hud.SlotCenter(IndexOf("crowbar"));
        Move(slot);
        await game.Wait(0.1);
        Check(game.Hud.HoverRect.HasArea() && game.Hud.HoverDrawsOverInventory, "item name draws above the inventory case");
        await Shot("attic_inventory");
        PressKey(Key.I);
        await game.Wait(0.1);
        Check(!game.Hud.InventoryOpen, "I closes the inventory");
        PressKey(Key.I);
        await game.Wait(0.1);
        Check(game.Hud.InventoryOpen, "I opens the inventory");
        Move(slot);
        await game.Wait(0.05);
        var crosshair = game.Hud.CursorSize;
        Click(slot, MouseButton.Left);
        await game.Wait(0.1);
        Check(game.Carried == "crowbar" && game.Hud.InventoryOpen, "clicking an item holds it and keeps the case open");
        Check(game.Hud.CursorItemVisible && game.Hud.CursorSize == crosshair,
            "a held item shows as a badge while the crosshair keeps its size");
        PressKey(Key.Space);
        Click(slot, MouseButton.Left);
        await Observe(0.1);
        Check(game.IsPaused && game.Carried == "crowbar", "Space pause preserves the carried inventory item");
        PressKey(Key.Space);
        Move(trunk);
        await game.Wait(0.05);
        Check(!game.Hud.InventoryOpen && game.Carried == "crowbar", "leaving the case closes the inventory, still holding the item");
        await Shot("attic_carry_crowbar");
        Click(trunk, MouseButton.Left);
        for (int i = 0; i < 100 && !game.Busy; i++) await game.Wait(0.05);
        await game.Wait(1.2);
        await Shot("attic_trunk_open");
        await WaitIdle(game);
        Check(GameState.Instance.HasFlag("trunk_open") && GameState.Instance.HasItem("journal"), "crowbar opens the trunk");
        Check(!game.Hud.CursorItemVisible, "using the item clears the cursor badge");
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
        bool thoughtChecked = false;
        for (int i = 0; i < 1200 && (game.Room?.Name != "Office" || !GameState.Instance.HasFlag("teddy_gone") || game.Busy); i++)
        {
            if (!thoughtChecked && game.Room?.Name == "Office" && game.Hud.ThoughtVisible)
            {
                thoughtChecked = true;
                Check(game.Hud.ThoughtText.StartsWith("Rain ticks on the window", StringComparison.Ordinal),
                    "the office opens on Micah's thought");
                Check(game.Hud.ThoughtFontColor == Hud.ThoughtColor && game.Hud.ThoughtRect.Position.Y < 20,
                    "the thought is in faded ink along the top of the screen");
                Check(!game.Hud.SpeechVisible && !game.Player.Talking, "a thought is not spoken: no speech, no moving mouth");
                await Shot("office_thought");
            }
            await game.Wait(0.1);
        }
        Check(thoughtChecked, "saw Micah's opening thought in the office");
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
        await Observe(0.1);
        Check(game.Hud.Menu.IsOpen && game.GetTree().Paused, "Esc opens the pause menu and pauses the game");
        await Shot("pause_menu");
        Check(game.Hud.Menu.Press("Save game"), "pause menu offers Save game");
        await Observe(0.1);
        await Shot("save_slots");
        Check(game.Hud.Menu.HasEntry($"Slot {SaveSystem.ManualSlots}") && SaveSystem.ManualSlots == 5, "save menu lists five manual slots");
        Check(game.Hud.Menu.Press("Slot 1"), "save menu lists slot 1");
        await Observe(0.1);
        Check(!game.Hud.Menu.HasEntry("Yes, overwrite"), "saving to an empty slot asks no confirmation");
        var saved = SaveSystem.Read(SaveSystem.ManualSlot(0));
        Check(saved is { Room: "lobby", RoomTitle: "Aurelian Hotel" } && saved.Inventory.Contains("brass_box"), "saved to slot 1 from the menu");
        await OverwriteTest(game);
        PressKey(Key.Escape);
        await game.Wait(0.1);
        Check(!game.Hud.Menu.IsOpen && !game.GetTree().Paused, "Esc resumes the game");
        if (saved == null) return;

        var ink = DialogueManager.Instance.SaveInk();
        gs.Reset();
        DialogueManager.Instance.ResetInk();
        await game.ChangeRoom("office", "start");
        await WaitIdle(game);
        Check(!gs.HasItem("brass_box") && game.Room?.Name == "Office", "progress wiped before loading");

        await game.LoadGame(saved);
        Check(game.Room?.Name == "Lobby", "load returns to the saved room");
        Check(gs.HasItem("brass_box") && gs.HasItem("photo") && gs.HasFlag("knows_lantern") && gs.HasFlag("seen_lobby"),
            "load restores items and flags");
        Check(game.Player.Position.DistanceTo(new Vector2(saved.X, saved.Y)) < 0.5f, "load restores the player's position");
        Check(ink.Length > 0 && DialogueManager.Instance.SaveInk() == ink, "load restores the Ink state");
        await Shot("lobby_loaded");
        await TitleMenuTest(game, expectSaves: true);
    }

    /// <summary>Saving over an occupied slot asks first: No keeps the old save, Yes replaces it.</summary>
    private async Task OverwriteTest(Game game)
    {
        var menu = game.Hud.Menu;
        var path = $"{SaveSystem.Directory}/{SaveSystem.ManualSlot(0)}.json";
        // a trailing-space marker so a real rewrite is detectable even within the same second
        var stale = FileAccess.GetFileAsString(path) + " ";
        using (var f = FileAccess.Open(path, FileAccess.ModeFlags.Write)) f?.StoreString(stale);

        Check(menu.Press("Save game"), "pause menu offers Save game again");
        await Observe(0.1);
        Check(menu.Press("Slot 1"), "save menu lists the occupied slot 1");
        await Observe(0.1);
        Check(menu.HasEntry("Yes, overwrite") && menu.HasEntry("No"), "saving over an occupied slot asks for confirmation");
        await Shot("save_overwrite");
        Check(menu.Press("No"), "confirmation offers No");
        await Observe(0.1);
        Check(menu.HasEntry("Slot 1") && FileAccess.GetFileAsString(path) == stale, "No keeps the old save and returns to the slot list");
        Check(menu.Press("Slot 1"), "slot 1 can be chosen again");
        await Observe(0.1);
        Check(menu.Press("Yes, overwrite"), "confirmation offers Yes, overwrite");
        await Observe(0.1);
        Check(FileAccess.GetFileAsString(path) != stale && SaveSystem.Read(SaveSystem.ManualSlot(0)) != null,
            "Yes overwrites the slot");
        Check(menu.HasEntry("Resume"), "overwriting returns to the pause menu");
    }

    /// <summary>Shows the title menu: Continue/Load are only offered once a save exists.</summary>
    private async Task TitleMenuTest(Game game, bool expectSaves)
    {
        game.ShowTitle(true);
        Check(game.Sfx.Ambient == Sound.Rain, "rain patters on the title screen");
        var menu = game.Hud.Menu.OpenTitle();
        await game.Hud.Fade(0, 0.1);
        await Shot(expectSaves ? "title_with_saves" : "title_new");
        bool canContinue = game.Hud.Menu.Press("Continue");
        Check(canContinue == expectSaves, expectSaves ? "title offers Continue once saved" : "title hides Continue without saves");
        if (!canContinue) game.Hud.Menu.Press("New game");
        var result = await menu;
        Check(result.Action == (expectSaves ? MenuAction.Load : MenuAction.NewGame) && (result.Save != null) == expectSaves,
            "title menu returns the chosen action");
        game.ShowTitle(false);
        Check(game.Sfx.Ambient == game.Room?.Ambience?.Sound, "leaving the title hands the ambience back to the room");
    }

    /// <summary>Micah's notepad: always the first slot, read full screen from N or the satchel, paged back and forth.</summary>
    private async Task NotepadTest(Game game)
    {
        var gs = GameState.Instance;
        Check(gs.Inventory.FirstOrDefault() == Notes.ItemId && gs.Inventory.Count(i => i == Notes.ItemId) == 1,
            "Micah carries one notepad, in the first slot");
        Check(gs.Inventory.ElementAtOrDefault(1) == MicahKit.LighterId && gs.Inventory.Count(i => i == MicahKit.LighterId) == 1,
            "Micah carries one lighter, in the second slot");
        await WaitIdle(game);
        PressKey(Key.N);
        await game.Wait(0.1);
        var pad = game.Hud.Notepad;
        Check(pad.IsOpen && pad.PageCount >= 2 && pad.Page == pad.PageCount - 1 && pad.PageId == "eleanor",
            "N opens the notepad on the newest note");
        await Shot("notepad");
        PressKey(Key.Left);
        await game.Wait(0.05);
        Check(pad.Page == pad.PageCount - 2 && pad.PageId == "case", "left arrow turns back a page");
        Click(pad.PrevCenter, MouseButton.Left);
        await game.Wait(0.05);
        Check(pad.Page == 0, "cannot turn back past the first page");
        Click(pad.NextCenter, MouseButton.Left);
        await game.Wait(0.05);
        Check(pad.Page == 1, "the next button turns forward");
        PressKey(Key.N);
        await WaitIdle(game);
        Check(!pad.IsOpen && !game.Busy, "N puts the notepad away");

        var read = game.ItemVerb(Verb.Look, Notes.ItemId);
        await game.Wait(0.1);
        Check(pad.IsOpen, "looking at the notepad in the satchel opens it");
        Click(pad.CloseCenter, MouseButton.Left);
        await AwaitTest(read, "the close button puts the notepad away");
        gs.GiveItem("hanger");
        Check(gs.Inventory[0] == Notes.ItemId && gs.Inventory[1] == MicahKit.LighterId,
            "new items never push the notepad and lighter out of the first slots");
        gs.TakeItem("hanger");
    }

    /// <summary>
    /// Touch screen play: a long press opens the verb wheel and a tap picks its verb, the NOTES touch button opens the
    /// notepad, a swipe turns its page and a tap closes it; moving a real mouse hides the touch buttons again.
    /// </summary>
    private async Task TouchTest(Game game)
    {
        await WaitIdle(game);
        var window = new Vector2(400, 80);
        Touch(window, true);
        for (int i = 0; i < 100 && !game.Hud.Wheel.IsOpen; i++) await game.Wait(0.02);
        Check(game.Hud.Wheel.IsOpen && !game.Busy, "a long press opens the verb wheel without clicking first");
        Touch(window, false);
        await game.Wait(0.1);
        Check(game.Hud.Wheel.IsOpen, "lifting the finger off the wheel's centre leaves it open");
        Check(game.Hud.TouchButtonsVisible, "touch buttons show once the screen is touched");
        await Shot("touch_wheel");
        var look = game.Hud.Wheel.SlotCenter(Verb.Look);
        Touch(look, true);
        Touch(look, false);
        for (int i = 0; i < 100 && !game.Busy; i++) await game.Wait(0.02);
        Check(!game.Hud.Wheel.IsOpen && game.Busy, "a tap on the wheel's eye looks at the window");
        await WaitIdle(game);

        var notes = game.Hud.TouchNotesCenter;
        Touch(notes, true);
        Touch(notes, false);
        var pad = game.Hud.Notepad;
        for (int i = 0; i < 50 && !pad.IsOpen; i++) await game.Wait(0.02);
        Check(pad.IsOpen && pad.Page == pad.PageCount - 1, "the NOTES touch button opens the notepad");
        var at = new Vector2(240, 130);
        Touch(at, true);
        await game.Wait(0.05);
        for (int i = 1; i <= 6; i++)
        {
            TouchDrag(at + new Vector2(i * 10, 0));
            await game.Wait(0.02);
        }
        Touch(at + new Vector2(60, 0), false);
        await game.Wait(0.1);
        Check(pad.Page == pad.PageCount - 2, "swiping right turns back one page");
        var close = pad.CloseCenter;
        Touch(close, true);
        Touch(close, false);
        await WaitIdle(game);
        Check(!pad.IsOpen && !game.Busy, "a tap on the close button puts the notepad away");

        Move(new Vector2(240, 135));
        await game.Wait(0.05);
        Check(!game.Hud.TouchButtonsVisible, "moving the mouse hides the touch buttons");
    }

    /// <summary>Wherever a character is drawn over the scenery behind him, hovering or clicking there means him (#73, #97).</summary>
    private void CheckActorWins(Game game, string actorId, string sceneryId, string what)
    {
        if (game.Room?.FindHotspot(actorId) is not Actor actor || game.Room.FindHotspot(sceneryId) is not { } scenery)
        {
            Check(false, $"{what}: the room has {actorId} and {sceneryId}");
            return;
        }
        var b = actor.Bounds;
        int overlap = 0, wrong = 0;
        var winners = new HashSet<string>();
        for (float y = b.Position.Y; y < b.End.Y; y++)
            for (float x = b.Position.X; x < b.End.X; x++)
            {
                var p = new Vector2(x, y);
                if (!actor.DrawnAt(p)) continue;
                if (scenery.Bounds.HasPoint(p)) overlap++;
                if (game.Room.HotspotAt(p) is var h && h != actor) { wrong++; winners.Add($"{h?.Id ?? "none"}@{p}"); }
            }
        Check(overlap > 0 && wrong == 0, $"{what} ({overlap} overlapping pixels, {wrong} wrong: {string.Join(" ", winners.Take(6))})");
    }

    private void CheckPortraitSpeech(Game game, bool right)
    {
        var panel = game.Hud.InsetRect;
        var speech = game.Hud.SpeechRect;
        float divider = panel.Position.X + panel.Size.X / 2;
        Check(game.Hud.CurrentCloseUp == CloseUps.FireEscape && game.Hud.SpeechVisible &&
            speech.Position.X >= (right ? divider : panel.Position.X) &&
            speech.End.X <= (right ? panel.End.X : divider),
            right ? "Eleanor's subtitle stays beneath the right portrait" : "Micah's subtitle stays beneath the left portrait");
        Check(speech.Position.Y > panel.Position.Y + panel.Size.Y * 0.7f && speech.End.Y < panel.End.Y,
            "portrait speech wraps below the face and inside the frame");
    }
}
