using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Puzzle checks: cancelling, solving and recovering puzzles, and combining items.</summary>
public partial class AutoPlay
{
    private async Task ReloadCheckpoint(string label)
    {
        await WaitIdle(_game);
        Check(_game.SaveToSlot(SaveSystem.ManualSlot(2)), $"saved {label}");
        var saved = SaveSystem.Read(SaveSystem.ManualSlot(2));
        Check(saved != null, $"read {label}");
        if (saved == null) throw new InvalidOperationException($"Missing checkpoint {label}");
        await _game.LoadGame(saved);
        await WaitIdle(_game);
    }

    private async Task PuzzleRecoveryTest(Game game)
    {
        var legacy = new SaveData
        {
            Room = "chicago_map", RoomTitle = "Chicago", StoryAct = 2, X = 240, Y = 262, Facing = 1,
            Flags = new List<string>
            {
                "on_map", "map_seen", "teddy_gone", "teddy_briefed", "took_revolver", "took_dollar",
                "took_lockpick", "got_mirror", "took_mirror", "cell_drawer_open", "staff_elevator",
                "knows_lantern", "library_banned", "librarian_refused",
            },
            Inventory = new List<string> { "mirror", "lockpick", "revolver", "book" },
        };
        await game.LoadGame(legacy);
        var gs = GameState.Instance;
        Check(game.Room?.FindHotspot("hotel")?.Visible == true && !gs.HasItem("card"), "legacy missed-card save has a real recovery route, not a fabricated item");
        await Shot("legacy_hotel_recovery_map");
        await game.Perform(Verb.Walk, "hotel");
        await game.Perform(Verb.Walk, "service_door");
        Check(game.Room?.Name == "HotelLinen", "legacy hotel marker reaches the linen room through the lobby");
        await game.Perform(Verb.Hand, "rack");
        await game.Perform(Verb.Hand, "cart");
        await CombineAndWait("pliers", "hanger");
        await game.Perform(Verb.UseItem, "corridor_door", "wire_hook");
        Check(game.Room?.Name == "EleanorRoom", "legacy recovery bolts back the linen door into room 507");
        await game.Perform(Verb.UseItem, "desk_drawer", "lockpick");
        await game.Perform(Verb.Hand, "paper");
        await game.Perform(Verb.Hand, "closet");
        await SolvePuzzle(() => game.Perform(Verb.UseItem, "safe", "combination"), PuzzleKind.Safe,
            new[] { ("t0", 1), ("n0", 2), ("d1", 1), ("t1", 3), ("n1", 1), ("n2", 7) }, "legacy_safe");
        await game.Perform(Verb.Hand, "brass_box");
        await game.ItemVerb(Verb.Hand, "brass_box");
        await game.Perform(Verb.Walk, "exit");
        Check(game.Room?.Name == "HotelLinen" && gs.HasFlag("linen_door_open"), "room 507 exits to the linen room");
        await game.Perform(Verb.Walk, "lift");
        await game.Perform(Verb.Walk, "revolving_door");
        Check(game.Room?.Name == "ChicagoMap" && game.Room?.FindHotspot("hotel")?.Visible == false && gs.HasItem("card"),
            "recovered card returns to Act 2 map and removes temporary hotel marker");
        await game.Perform(Verb.Walk, "office");
        var warm = game.Perform(Verb.UseItem, "radiator", "card");
        await Until(() => game.Hud.ImageVisible);
        game.Hud.CloseImage();
        await warm;
        await Combine("card", "mirror");
        await WaitIdle(game);
        Check(gs.HasFlag("card_reflected") && !gs.HasFlag("read_book") && !gs.HasFlag("club_unlocked"),
            "heat and reflection before reading do not prematurely unlock Club");
        await ReloadCheckpoint("cipher_read_last");
        await SolvePuzzle(() => game.ItemVerb(Verb.Hand, "book"), PuzzleKind.Cipher,
            new[] { ("s0", 1), ("s1", 2) }, "cipher_read_last");
        Check(gs.HasFlag("club_unlocked") && gs.HasItem("address"), "reading last offers cipher without repeating heat or reflection");
    }

    private async Task ActThreePuzzleRecoveryTest(Game game)
    {
        var saved = new SaveData
        {
            Room = "mansion_study", RoomTitle = "Harrington's Study", StoryAct = 3, X = 242, Y = 222, Facing = 2,
            Ink = DialogueManager.Instance.SaveInk(),
            Flags = new List<string>
            {
                PuzzleMigration.SchemaFlag, "seen_mansion_study", "door_open",
                "drawer_right_open", "closet_open", Endings.TookDocuments,
            },
            Inventory = new List<string> { "documents", "revolver" },
        };
        await game.LoadGame(saved);
        var gs = GameState.Instance;
        Check(gs.HasFlag("bell_wedged") && gs.HasFlag("audit_identified") && gs.HasItem("documents"),
            "legacy Act 3 save keeps secured alarm and collected evidence despite original puzzle marker");
        Check(!gs.HasFlag("study_drawer_left_open") && !gs.HasFlag("study_drawer_right_open") && !gs.HasFlag("study_closet_open") &&
            game.Room?.FindHotspot("documents")?.Visible == false,
            "legacy shared drawer flags do not open unrelated study drawers or duplicate register");
        await ReloadCheckpoint("legacy_act3_completed");
        Check(gs.HasFlag(Endings.TookDocuments) && gs.HasItem("documents"), "legacy Act 3 completion survives another reload");
    }

    private async Task CancelPuzzle(Func<Task> start, PuzzleKind kind, string flag, string name)
    {
        var action = start();
        await Until(() => _game.Hud.Puzzle.IsOpen);
        Check(_game.Hud.Puzzle.IsOpen && _game.Hud.Puzzle.Kind == kind, $"opened {name}");
        Check(_game.Busy && !_game.CanSave && !_game.SaveToSlot(SaveSystem.ManualSlot(1)), $"{name} blocks saves");
        var beforeAuto = SaveSystem.Read(SaveSystem.AutosaveSlot)?.SavedAtUtc;
        if (kind == PuzzleKind.Catalogue)
        {
            PuzzleClick("motif0");
            PuzzleClick("entry2");
        }
        else PuzzleClick("submit");
        if (kind == PuzzleKind.Bell)
        {
            for (int i = 0; i < 3; i++) PuzzleClick("s0");
            PuzzleClick("submit");
            Check(_game.Hud.Puzzle.IsOpen && !GameState.Instance.HasFlag(flag), "cut-wire plan rejected before triggering alarm");
        }
        Check(_game.Hud.Puzzle.IsOpen && !GameState.Instance.HasFlag(flag), $"{name} rejects wrong answer");
        Click(new Vector2(478, 268), MouseButton.Left);
        _game.Hud.ShowInventory(true);
        await _game.Wait(0.2);
        Check(!_game.Hud.InventoryOpen && _game.Hud.Puzzle.IsOpen, $"{name} blocks underlying interface");
        Check(SaveSystem.Read(SaveSystem.AutosaveSlot)?.SavedAtUtc == beforeAuto, $"{name} defers queued autosave");
        await Shot(name + "_wrong");
        PuzzleClick("reset");
        PressKey(Key.Escape);
        await action;
        await WaitIdle(_game);
        Check(!_game.Hud.Puzzle.IsOpen && !GameState.Instance.HasFlag(flag), $"{name} cancellation preserves unsolved state");
    }

    private async Task SolvePuzzle(Func<Task> start, PuzzleKind kind, (string Id, int Count)[] controls, string name, bool submit = true)
    {
        var action = start();
        await Until(() => _game.Hud.Puzzle.IsOpen);
        Check(_game.Hud.Puzzle.IsOpen && _game.Hud.Puzzle.Kind == kind, $"reopened {name}");
        foreach (var (id, count) in controls)
        {
            for (int i = 0; i < count; i++) PuzzleClick(id);
            await _game.Wait(0.1);
        }
        if (submit)
        {
            await Shot(name + "_solution");
            PuzzleClick("submit");
        }
        await action;
        await WaitIdle(_game);
        Check(!_game.Hud.Puzzle.IsOpen, $"solved {name} through real controls");
    }

    /// <summary>The cage's shortest way through the service shafts, as arrow-button clicks.</summary>
    private static (string Id, int Count)[] LiftRoute() =>
        LiftMaze.Route(LiftMaze.Start, LiftMaze.Target)!.Select(step => (step, 1)).ToArray();

    private void PuzzleClick(string id)
    {
        var point = _game.Hud.Puzzle.ButtonCenter(id);
        Move(point);
        Click(point, MouseButton.Left);
    }

    private async Task SelectInventoryItem(string item)
    {
        await WaitIdle(_game);
        if (!_game.Hud.InventoryOpen) Click(_game.Hud.SatchelCenter, MouseButton.Left);
        await _game.Wait(0.1);
        Check(_game.Hud.InventoryOpen, $"satchel open to select {item}");
        if (!_game.Hud.InventoryOpen) throw new InvalidOperationException($"Satchel did not open for {item}");
        int index = IndexOf(item);
        int page = index / 12;
        while (_game.Hud.InventoryPage != page)
        {
            Click(_game.Hud.InventoryPageCenter(_game.Hud.InventoryPage < page), MouseButton.Left);
            await _game.Wait(0.1);
        }
        Click(_game.Hud.SlotCenter(index), MouseButton.Left);
        await _game.Wait(0.1);
    }

    private async Task Combine(string first, string second)
    {
        await SelectInventoryItem(first);
        Check(_game.Carried == first, $"picked {first} from paged inventory");
        await SelectInventoryItem(second);
    }

    private async Task CombineAndWait(string first, string second)
    {
        await Combine(first, second);
        while (_game.Busy) await _game.Wait(0.1);
    }
}
