using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Smoke test: plays the whole demo by itself, saving screenshots to screenshots/ and printing
/// AUTOPLAY OK / AUTOPLAY FAILED. Run with: godot -- --autoplay [--clock=fast|normal]
/// </summary>
public class AutoPlay
{
    /// <summary>Previous automated clock: 8× game time, display timing left alone.</summary>
    private const double NormalTimeScale = 8;
    /// <summary>Uncapped clock: dialogue and <see cref="Game.Wait"/> do not take wall-clock story time.</summary>
    private const double FastTimeScale = 60;
    private Game _game = null!;
    private readonly HashSet<string> _shotKnots = new();
    private readonly List<string> _failures = new();
    private string _dir = "";
    private int _shot;
    private readonly Dictionary<string, int> _poseCounts = new();
    private readonly Dictionary<PosePlayback, int> _lastPoseFrame = new();
    private string[] _prefer = Array.Empty<string>();
    private readonly Dictionary<string, string[]> _offered = new();
    private bool _theEndShot;
    private string _act3Ink = "";
    private int _crossOffers;
    private bool? _insetAtCaughtChoice;
    private bool? _insetAtBeatenChoice;
    private CloseUp? _closeUpAtRoadChoice;

    public async Task Run(Game game)
    {
        _game = game;
        PosePlayback.FrameObserver = ObservePose;
        _dir = ProjectSettings.GlobalizePath("res://screenshots");
        DirAccess.MakeDirRecursiveAbsolute(_dir);
        // keep Godot from importing the screenshots
        using (FileAccess.Open($"{_dir}/.gdignore", FileAccess.ModeFlags.Write)) { }
        if (!ApplyClock(out var clockError))
        {
            GD.Print("AUTOPLAY FAILED:\n  " + clockError);
            game.GetTree().Quit(1);
            return;
        }
        // never touch the player's own saves
        SaveSystem.Directory = "user://autoplay_saves/ten_puzzles_act3";
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
            _offered[knot] = options.ToArray();
            if (knot == "caleb_cross") _crossOffers++;
            if (knot == "club_caught") _insetAtCaughtChoice = game.Hud.InsetVisible;
            if (knot == "beaten_choice") _insetAtBeatenChoice = game.Hud.InsetVisible;
            if (knot == "eleanor_road")
            {
                _closeUpAtRoadChoice = game.Hud.CurrentCloseUp;
                Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn,
                    "the convent panel is completely removed before the compensation choice");
            }
            foreach (var want in _prefer)
            {
                for (int i = 0; i < options.Count; i++)
                    if (options[i].Contains(want)) return i;
            }
            return 0;
        };

        try
        {
            var gs = GameState.Instance;
            await ContentSettingsTest(game);
            if (OS.GetCmdlineUserArgs().Contains("--settings-test")) return;
            bool autosave = game.AutosaveEnabled;
            game.AutosaveEnabled = false;
            await StoryDialogueTest(game);
            await PuzzleRecoveryTest(game);
            await ActThreePuzzleRecoveryTest(game);
            foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
            gs.Reset();
            DialogueManager.Instance.ResetInk();

            // ---- prologue: the attic, played through the real mouse input where it matters
            await TitleMenuTest(game, expectSaves: false);
            game.AutosaveEnabled = autosave;
            await game.ChangeRoom("attic", "start");
            await PauseTest(game);
            Check(game.Player.Character == "daniel" && !gs.HasItem(Notes.ItemId) && !gs.HasItem(MicahKit.LighterId), "prologue plays as Daniel, without Micah's notepad or lighter");
            await Shot("attic");
            Check(game.Sfx.Ambient == null, "no rain sounds in the dry attic");
            int woodSteps = game.Sfx.Count(Sound.StepWood);
            await WheelTest(game);
            await PosePlaybackTest(game);
            await game.Perform(Verb.Talk, "hatch");
            await game.Perform(Verb.Hand, "sheet");
            Check(gs.HasFlag("sheet_lifted"), "lifted the dust sheet");
            Check(game.Sfx.Count(Sound.StepWood) > woodSteps, "Daniel's shoes sound on the attic boards");
            await game.Perform(Verb.Hand, "boxes");
            Check(gs.HasFlag("boxes_spilled"), "spilled the boxes");
            await game.Perform(Verb.Hand, "suitcase");
            Check(gs.HasItem("suitcase_key"), "found the key in the suitcase");
            await game.Perform(Verb.UseItem, "trunk", "suitcase_key");
            Check(!gs.HasFlag("trunk_open"), "the suitcase key doesn't fit the trunk");
            await game.Perform(Verb.Hand, "papers");
            Check(!gs.HasFlag("tool_tin_found"), "nothing heavy hides under the papers");
            await game.Perform(Verb.Hand, "boxes");
            Check(gs.HasFlag("tool_tin_found") && !gs.HasItem("crowbar"), "searching the boxes again opens one on a locked tin");
            await game.Perform(Verb.Hand, "tool_tin");
            Check(!gs.HasItem("crowbar"), "tin cannot be opened by hand");
            await game.Perform(Verb.UseItem, "tool_tin", "suitcase_key");
            Check(gs.HasItem("crowbar"), "small key opens the tool tin for the crowbar");
            await Shot("attic_mess");
            await InventoryTest(game);
            await ReadJournal(game);

            // ---- 1927
            Check(game.Room?.Name == "Office", "journal leads to the office");
            Check(game.Player.Character == "micah", "story continues as Micah");
            Check(gs.HasFlag("teddy_gone"), "Teddy left the office");
            Check(gs.HasItem("photo"), "got the photo");
            await Shot("office");
            Check(game.Sfx.Ambient == Sound.Rain, "rain patters on the office window");
            await game.Perform(Verb.Hand, "drawer");
            await Shot("office_drawer");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "Office", "can't leave without the drawer things");
            await game.Perform(Verb.Hand, "revolver");
            await game.Perform(Verb.Hand, "dollar");
            await game.Perform(Verb.Hand, "lockpick");
            Check(gs.HasItem("revolver") && gs.HasItem("dollar") && gs.HasItem("lockpick"), "took the revolver, the dollar and the lockpick");
            Check(CashRules.Balance(gs.HasFlag) == 22, "case cash covers every bribe");
            await Shot("office_drawer_empty");
            await NotepadTest(game);
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
            Check(gs.HasItem("dollar") && CashRules.Balance(gs.HasFlag) == 21 && gs.HasFlag("knows_lantern") &&
                !gs.HasFlag("staff_elevator"), "the first dollar buys the bellboy's memory, not the back way");
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room is Rooms.Lobby, "Eleanor's room comes before the Blue Lantern");
            await game.Perform(Verb.Talk, "bellboy");
            Check(CashRules.Balance(gs.HasFlag) == 21 && !gs.HasFlag("staff_elevator"), "talking doesn't buy the back way");
            await game.Perform(Verb.UseItem, "bellboy", "dollar");
            Check(CashRules.Balance(gs.HasFlag) == 20 && gs.HasFlag("staff_elevator"), "another dollar buys the way to Eleanor's room");
            await game.Perform(Verb.UseItem, "bellboy", "dollar");
            Check(CashRules.Balance(gs.HasFlag) == 20, "repeat bellboy visit does not charge again");
            await ReloadCheckpoint("cash_after_bellboy");
            Check(CashRules.Balance(gs.HasFlag) == 20 && gs.HasItem("dollar"), "save/load preserves remaining cash");
            Check(gs.HasFlag("knows_lantern") && gs.HasFlag("staff_elevator"), "bribed the bellboy for the staff elevator");
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room is Rooms.Lobby, "cannot abandon newly required hotel clues before Blue Lantern departure");
            await CancelPuzzle(() => game.Perform(Verb.Walk, "service_door"), PuzzleKind.Lift, "lift_routed", "lift_route");
            await SolvePuzzle(() => game.Perform(Verb.Walk, "service_door"), PuzzleKind.Lift, LiftRoute(), "lift_route");
            Check(game.Room?.Name == "HotelLinen", "staff elevator up to the fifth-floor linen room");

            // ---- the linen room: a hanger and the cart's pliers make a hook for the night bolt
            await Shot("hotel_linen");
            await game.Perform(Verb.Walk, "corridor_door");
            Check(game.Room?.Name == "HotelLinen" && !gs.HasFlag("linen_door_open"), "the corridor door is bolted from the far side");
            await game.Perform(Verb.UseItem, "corridor_door", "lockpick");
            Check(!gs.HasFlag("linen_door_open") && gs.HasItem("lockpick"), "no keyhole for the lockpick on the linen side");
            await game.Perform(Verb.Hand, "rack");
            Check(gs.HasItem("hanger") && gs.HasFlag("took_hanger"), "took a wire hanger from the laundry rack");
            await game.Perform(Verb.UseItem, "corridor_door", "hanger");
            Check(!gs.HasFlag("linen_door_open") && gs.HasItem("hanger"), "a straight hanger alone can't work the bolt");
            await game.Perform(Verb.Hand, "cart");
            Check(gs.HasItem("pliers") && gs.HasFlag("took_pliers"), "took the pliers from the housekeeping cart");
            await Shot("hotel_linen_taken");
            await CombineAndWait("hanger", "pliers");
            Check(gs.HasItem("wire_hook") && !gs.HasItem("hanger") && !gs.HasItem("pliers") && gs.HasFlag("made_wire_hook"),
                "bent the hanger into a wire hook; the pliers go back on the cart");
            await game.Perform(Verb.Hand, "cart");
            Check(!gs.HasItem("pliers"), "the cart doesn't hand the pliers out twice");
            await game.Perform(Verb.UseItem, "corridor_door", "wire_hook");
            Check(gs.HasFlag("linen_door_open") && !gs.HasItem("wire_hook"), "hooked the night bolt through the transom");
            Check(game.Room?.Name == "EleanorRoom", "across the corridor into Eleanor's room");

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
            await CancelPuzzle(() => game.Perform(Verb.UseItem, "safe", "combination"), PuzzleKind.Safe, "safe_open", "safe_dial");
            await SolvePuzzle(() => game.Perform(Verb.UseItem, "safe", "combination"), PuzzleKind.Safe,
                new[] { ("t0", 1), ("n0", 2), ("d1", 1), ("t1", 3), ("n1", 1), ("n2", 7) }, "safe_dial");
            Check(gs.HasFlag("safe_open"), "opened the safe");
            await Shot("eleanor_safe");
            await game.Perform(Verb.Hand, "brass_box");
            Check(gs.HasItem("brass_box"), "took the brass box");
            await Shot("eleanor_safe_empty");
            await game.ItemVerb(Verb.Hand, "brass_box");
            Check(!gs.HasItem("brass_box") && gs.HasItem("card") && gs.HasItem("matchbook"), "the brass box holds a card and the matchbook");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "HotelLinen", "back across the corridor to the linen room");
            await game.Perform(Verb.Walk, "lift");
            Check(game.Room?.Name == "Lobby", "back down in the lobby");
            await SaveLoadTest(game);
            await game.Perform(Verb.Walk, "revolving_door");
            Check(game.Room?.Name == "BlueLanternFront", "the Blue Lantern lead goes to Rizzo's Flowers");

            // ---- Rizzo's Flowers: dye a white carnation blue for the cold-room grille
            await Shot("blue_lantern_front");
            Check(game.Sfx.Ambient == Sound.Rain, "rain falls on State Street");
            await game.Perform(Verb.Look, "chalkboard");
            await game.Perform(Verb.Hand, "grille");
            Check(game.Room?.Name == "BlueLanternFront" && !gs.HasFlag("grille_opened"), "the grille won't open for a bare lapel");
            await game.Perform(Verb.Hand, "bucket");
            Check(gs.HasItem("carnation"), "bought a white carnation");
            await game.Perform(Verb.Hand, "bucket");
            Check(gs.Inventory.Count(i => i == "carnation") == 1, "one buttonhole, one flower");
            await game.Perform(Verb.UseItem, "grille", "carnation");
            Check(game.Room?.Name == "BlueLanternFront" && !gs.HasFlag("grille_opened") && gs.HasItem("carnation"),
                "a white carnation gets a shut slot");
            await game.Perform(Verb.Hand, "shelf");
            Check(gs.HasItem("bluing") && gs.HasFlag("took_bluing"), "took the bottle of bluing");
            await Shot("blue_lantern_front_taken");
            await CombineAndWait("carnation", "bluing");
            Check(gs.HasItem("blue_carnation") && !gs.HasItem("carnation") && !gs.HasItem("bluing") && gs.HasFlag("made_blue_carnation"),
                "dyed the carnation blue; the bluing goes back on the shelf");
            await game.Perform(Verb.UseItem, "grille", "blue_carnation");
            Check(game.Room?.Name == "Speakeasy", "the grille opens for a blue carnation");
            Check(gs.HasFlag("grille_opened") && !gs.HasItem("blue_carnation") && !gs.HasFlag("sal_passed"),
                "past the florist's grille, but Sal is still to come");

            await Shot("speakeasy");
            await game.Perform(Verb.Talk, "bartender");
            await Until(() => !game.Busy);
            Check(game.Room?.Name == "Speakeasy" && _offered.Keys.Any(k => k.StartsWith("sal")),
                "walking past Sal makes him step in and start the talk");
            Check(gs.HasFlag("sal_passed") && !gs.HasFlag("thrown_out") && !gs.HasFlag("photo_shown"),
                "no password, but Sal takes the bribe before Micah reaches the bar");
            await game.Perform(Verb.Talk, "sal");
            Check(game.Room?.Name == "Speakeasy" && gs.HasFlag("sal_passed"), "talking to Sal directly still works once inside");
            Check(CashRules.Balance(gs.HasFlag) == 10 && gs.HasItem("dollar"), "Sal costs ten dollars and leaves ten");
            await Shot("speakeasy_inside");
            var bar = game.Perform(Verb.Talk, "bartender");
            await Until(() => game.Room?.Name == "Alley");
            Check(game.Room?.Name == "Alley", "the bartender has Sal throw Micah out back");
            await game.Wait(2.5);
            await Shot("alley");
            await bar;

            // ---- the convent
            Check(game.Room is Rooms.Alley && gs.HasFlag("alley_done") && !game.Busy,
                "the beating ends with player control in the alley");
            Check(!game.Player.Poses.Active, "Micah stands before the player leaves the alley");
            Check(game.Room?.FindActor("sal")?.Visible == false && game.Room?.FindActor("bartender")?.Visible == false,
                "Sal and Tony have gone back inside");
            Check(game.Room?.FindHotspot("street")?.Visible == true, "the alley street exit is available");
            Check(game.Room?.FindHotspot("street")?.Bounds is { } exit && exit.Position.X < 10 && exit.End.X <= 100 &&
                exit.End.Y <= 192 && exit.Size.Y > 120, "the alley street exit covers the painted passage on the left");
            await ReloadCheckpoint("alley_standing");
            Check(game.Room is Rooms.Alley && game.Room.FindHotspot("street")?.Visible == true &&
                game.Room.FindActor("sal")?.Visible == false && game.Room.FindActor("bartender")?.Visible == false,
                "loading the alley retains the exit and does not restore the departed men");
            Click(game.Room!.FindHotspot("street")!.Bounds.GetCenter(), MouseButton.Left);
            await Until(() => game.Room is Rooms.ConventRoad && game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText.StartsWith("Gothic arches", StringComparison.Ordinal),
                "Micah comments on the architecture outside the convent");
            Check(game.Room?.FindActor("eleanor")?.Visible == false && !game.Hud.InsetVisible,
                "Eleanor and the close-up are absent on arrival");
            await Until(() => !game.Busy && gs.HasFlag("seen_convent_exterior"));
            Check(game.Room is Rooms.ConventRoad && !gs.HasFlag("nun_talked") && !gs.HasFlag("eleanor_found"),
                "arrival waits outside for the player to open the convent door");
            await Shot("convent_arrival");
            await ReloadCheckpoint("convent_arrival");
            Check(gs.HasFlag("seen_convent_exterior") && game.Room?.FindActor("eleanor")?.Visible == false &&
                !game.Hud.SpeechVisible && !gs.HasFlag("convent_departed"),
                "loading the exterior retains the arrival phase without repeating the remark");
            Click(game.Room!.FindHotspot("door")!.Bounds.GetCenter(), MouseButton.Left);
            await Until(() => game.Room is Rooms.ConventCorridor && gs.HasFlag("nun_talked") && !game.Busy);
            Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_talked"), "the nun questions Micah in the corridor");
            await game.Perform(Verb.Walk, "entrance");
            Check(game.Room is Rooms.ConventCorridor && !gs.HasFlag("convent_departed"),
                "Micah must search the cell before leaving the convent");
            await Shot("convent_corridor");
            await game.Perform(Verb.Walk, "cell_door");
            Check(game.Room?.Name == "ConventCell", "entered Eleanor's cell");
            await Shot("convent_cell");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "ConventCell", "can't leave the cell without the mirror");
            await game.Perform(Verb.Hand, "nightstand");
            Check(gs.HasFlag("cell_drawer_open"), "opened the nightstand drawer");
            await Shot("convent_cell_drawer");
            await game.Perform(Verb.Hand, "mirror");
            Check(gs.HasItem("mirror_waxed") && !gs.HasFlag("got_mirror") && !game.Hud.ImageVisible,
                "taking waxed mirror does not reveal the symbol");
            Check(game.Room?.FindHotspot("mirror")?.Visible == false, "taken mirror disappears from drawer");
            var searchBed = game.Perform(Verb.Hand, "bed");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "I ought to leave her bed alone. Somehow, I can't quite make myself turn away.");
            Check(!searchBed.IsCompleted && game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "I ought to leave her bed alone. Somehow, I can't quite make myself turn away.",
                "first bed search voices Micah's reluctance before taking the cloth");
            Check(!gs.HasItem("cloth"), "Micah hesitates before borrowing the cloth");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.");
            Check(!searchBed.IsCompleted && game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.",
                "first bed search retains the cloth's mirror-cleaning hint");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "Her perfume. I've lifted the cloth to my nose before I even know I'm doing it.");
            Check(!searchBed.IsCompleted && game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "Her perfume. I've lifted the cloth to my nose before I even know I'm doing it.",
                "Micah notices instinctively smelling her perfume after finding the cloth");
            await searchBed;
            Check(gs.HasItem("cloth") && !gs.HasFlag("got_mirror"), "bed search supplies cloth without revealing the symbol");
            var searchBedAgain = game.Perform(Verb.Hand, "bed");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.",
                "repeat bed search skips the first-pickup reluctance");
            await searchBedAgain;
            Check(game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.",
                "repeat bed search skips the first-pickup perfume line");
            await ReloadCheckpoint("convent_cloth");
            Check(gs.HasItem("cloth") && !gs.HasFlag("got_mirror"), "save/load retains borrowed cloth and unfinished mirror");
            var searchBedReloaded = game.Perform(Verb.Hand, "bed");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.",
                "bed search after loading skips the first-pickup reluctance");
            await searchBedReloaded;
            Check(game.Hud.SpeechText ==
                "A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.",
                "bed search after loading skips the first-pickup perfume line");
            await Combine("mirror_waxed", "cloth");
            await WaitIdle(game);
            Check(gs.HasItem("cloth") && !gs.HasFlag("got_mirror"), "cold wax refuses cleaning without losing cloth");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room is Rooms.ConventCell, "waxed mirror possession does not bypass symbol gate");
            await game.Perform(Verb.UseItem, "lampstand", "mirror_waxed");
            // real time, so Micah's line over the symbol is still running when the first click lands
            double mirrorScale = Engine.TimeScale;
            Engine.TimeScale = 1;
            try
            {
                await Combine("cloth", "mirror_waxed");
                await Until(() => game.Hud.ImageVisible && game.Hud.SpeechVisible);
                Check(game.Hud.ImageVisible && game.Hud.ImageHeld && game.Hud.SpeechText.StartsWith("Three loops", StringComparison.Ordinal),
                    "Micah's line is spoken over the symbol behind the mirror");
                await Shot("triquetra");
                Check(game.Hud.ImageHeld, "the line is still showing after the screenshot");
                Click(new Vector2(240, 140), MouseButton.Left);
                await Until(() => !game.Hud.SpeechVisible);
                await Observe(0.2);
                Check(game.Hud.ImageVisible && !game.Hud.ImageHeld, "the first click ends the line but keeps the mirror on screen");
                Click(new Vector2(240, 140), MouseButton.Left);
                await Until(() => !game.Hud.ImageVisible);
                Check(!game.Hud.ImageVisible, "the next click returns to the cell");
            }
            finally
            {
                Engine.TimeScale = mirrorScale;
            }
            await WaitIdle(game);
            await game.Perform(Verb.Hand, "comb");
            Check(gs.HasItem("mirror") && !gs.HasItem("comb") && !gs.HasItem("cloth"), "revealed mirror retained; comb and cloth left in cell");
            var searchBedAfterCleaning = game.Perform(Verb.Hand, "bed");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText == "Thin mattress, and the borrowed cloth back where it belongs.",
                "bed search after cleaning keeps the returned-cloth response");
            await searchBedAfterCleaning;
            Check(!gs.HasItem("cloth"), "bed search after cleaning does not borrow the cloth again");
            await Shot("convent_cell_after");

            await game.Perform(Verb.Walk, "exit");
            Check(game.Room is Rooms.ConventCorridor && game.Player.Position.DistanceTo(new Vector2(410, 200)) < 2,
                "the cell door returns Micah to the cell end of the corridor");
            Check(!gs.HasFlag("nun_farewell_done") && !gs.HasFlag("convent_departed") && !game.Busy,
                "returning from the cell leaves the farewell and departure under player control");
            await Shot("convent_corridor_return");
            await ReloadCheckpoint("convent_corridor_return");
            Check(game.Room is Rooms.ConventCorridor && !gs.HasFlag("nun_farewell_done") &&
                !game.Hud.SpeechVisible, "loading the corridor does not replay the initial interrogation");
            await ConventFarewellTalkTest(game);

            var leave = game.Perform(Verb.Walk, "entrance");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Detective, before you go...");
            Check(game.Room is Rooms.ConventCorridor && !gs.HasFlag("convent_departed") &&
                game.Hud.SpeechText == "Detective, before you go...",
                "the nun calls Micah back if he tries to leave without talking");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "What do you hope to find in all this, Detective?");
            Check(game.Hud.SpeechText == "What do you hope to find in all this, Detective?",
                "intercepted departure starts the shared farewell");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "I don't know, sister, but I can't stop at this point.");
            Check(game.Hud.SpeechText == "I don't know, sister, but I can't stop at this point.",
                "Micah gives the same reply when the nun calls him back");
            await Until(() => game.Room?.Name == "ConventRoad");
            Check(game.Room?.Name == "ConventRoad" && gs.HasFlag("nun_farewell_done") && gs.HasFlag("convent_departed"),
                "the intercepted exit continues outside after the farewell");
            Check(game.Room?.FindActor("eleanor")?.Visible == true, "Eleanor is waiting on departure");
            Check(!game.Hud.InsetVisible, "no close-up while Micah walks up to her");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "Not many people enter a convent this late, mister. Were you looking for someone?");
            Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn && game.Hud.SpeechText ==
                "Not many people enter a convent this late, mister. Were you looking for someone?",
                "Eleanor's new opening is spoken on the road before the close-up");
            await Until(() => game.Hud.InsetVisible);
            Check(game.Hud.CurrentCloseUp == CloseUps.Convent && game.Hud.InsetName == "convent_closeup",
                "the two-portrait close-up appears immediately after Eleanor's opening");
            Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "the two-portrait close-up fills most of the screen");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Eleanor Harrington. You wouldn't happen to know her?");
            CheckPortraitSpeech(game, right: false);
            await Shot("convent_portrait_micah");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Sister Agatha"));
            CheckPortraitSpeech(game, right: true);
            await Shot("convent_portrait_eleanor");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Twenty a day. I used to spend that on gloves.");
            Check(game.Hud.SpeechText == "Twenty a day. I used to spend that on gloves." && !game.Hud.InsetDrawn,
                "the compensation answer rejoins the existing conversation on the road");
            Check(_closeUpAtRoadChoice == null, "Micah answers the compensation choice without a portrait panel");
            await Shot("convent_road");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("can't go back"));
            Check(game.Hud.CurrentCloseUp == null && !game.Hud.InsetDrawn && game.Room is Rooms.ConventRoad,
                "the rest of Eleanor's conversation stays on the road without the panel");
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

            // ---- Act 2, 1927: whiskey and the ring, then the cathedral
            await Until(() => game.Room?.Name == "Office" && gs.HasFlag("office_cup_held"));
            await game.Wait(0.65);
            await Shot("office_whiskey_drinking");
            await Until(() => gs.HasFlag("act2_office_done"));
            Check(gs.HasFlag("act2_whiskey_drunk") && gs.HasFlag("ring_taken_act2") && gs.HasItem("faith_ring"),
                "Act 2 opens with whiskey and the recorded take-ring choice");
            Check(game.Room?.FindHotspot("faith_ring")?.Visible != true, "taken ring is no longer on the desk");
            await Until(() => game.Room?.Name == "ChurchExterior");
            Check(gs.HasItem("mirror"), "reading again leads back to 1927 with Micah's things");
            Check(gs.Inventory.Take(2).SequenceEqual(MicahKit.Pinned) &&
                gs.Inventory.Skip(2).All(i => MicahKit.KeptInAct(2, i)) &&
                !gs.HasItem("matchbook") && !gs.HasItem("photo") && !gs.HasItem("dollar"),
                "Act 2 starts with notepad, lighter and the case kit; Act 1 clues stay behind");
            await game.Wait(1.5);
            await Shot("church_exterior_act2");
            await Until(() => game.Room?.Name == "ChurchInterior");
            Check(gs.HasFlag("act2_church_thought"), "Micah thinks about Eleanor outside the cathedral, then goes in");
            await game.Wait(2);
            await Shot("church_act2");
            await Until(() => game.Room?.Name == "ChicagoMap");
            Check(gs.HasFlag("caleb_met") && !gs.HasFlag("act2_church"), "Micah talks with Caleb and walks out");
            Check(_crossOffers == 0, "no pendant offer on the initial confession");
            Check(!game.Player.Visible, "the player isn't drawn on the map");
            await read;
            await WaitIdle(game);
            await RingAndCrossTest(game);
            await RoseAppealsTest(game);
            await RoseWalkAwayTest(game);
            await Shot("map");
            Check(game.Room?.FindHotspot("club")?.Visible == false, "the club isn't on the map yet");
            if (game.Room is Rooms.ChicagoMap map && map.FindHotspot("library") is { } libSpot)
            {
                map.UpdateCaption(libSpot.Bounds.GetCenter());
                Check(map.CaptionText == libSpot.LookText && !map.CaptionText.Contains("Rose"),
                    "hovering a place reads its description in the map caption");
                map.UpdateCaption(new Vector2(20, 250));
                Check(map.CaptionText == "", "the map caption hides away from the places");
                Check(game.LeftClickVerb(libSpot) == Verb.Walk, "a left click on the map travels instead of looking");
            }
            else Check(false, "map caption test reached the map");
            await game.Perform(Verb.Walk, "church");
            Check(game.Room?.Name == "ChicagoMap", "Micah won't go back to the church");

            var libraryLines = await Listen(game, game.Perform(Verb.Walk, "library"));
            Check(game.Room?.Name == "Library" && game.Player.Visible, "went to the library");
            Check(libraryLines.Any(l => l.Contains("Not her shift. Thank God")) && libraryLines.Any(l => l.Contains("back in my head")),
                "Micah is relieved Rose isn't on duty, but she's back on his mind");
            Check(game.Room?.FindHotspot("librarian")?.Visible == true && game.Room?.FindHotspot("rose") == null, "the daytime librarian is there, and Rose isn't in the library at all");
            CheckActorWins(game, "librarian", "ladder", "the librarian wins over the ladder behind him");
            await Shot("library_day");
            await game.Perform(Verb.UseItem, "librarian", "revolver");
            Check(!gs.HasFlag("library_banned"), "no gun before asking");
            gs.TakeItem("mirror");
            var ask = game.Perform(Verb.UseItem, "librarian", Notes.ItemId);
            await Until(() => game.Hud.ImageVisible);
            Check(game.Hud.ImageVisible, "the notepad sketch of the symbol stands in for the mirror");
            await Shot("librarian_symbol");
            game.Hud.CloseImage();
            await ask;
            gs.GiveItem("mirror");
            var notes = game.ItemVerb(Verb.Hand, Notes.ItemId);
            await game.Wait(0.1);
            for (int i = 0; i < 40 && game.Hud.Notepad.PageId is not (null or "triquetra"); i++) game.Hud.Notepad.Turn(-1);
            Check(game.Hud.Notepad.PageId == "triquetra" && game.Hud.Notepad.SketchVisible, "the notepad keeps the sketch from behind the mirror");
            await Shot("notepad_triquetra");
            game.Hud.Notepad.Close();
            await notes;
            Check(gs.HasFlag("librarian_refused"), "the librarian won't talk");
            await game.Perform(Verb.UseItem, "librarian", "revolver");
            Check(!gs.HasItem("book"), "cannot retrieve book before identifying title");
            await game.Perform(Verb.Hand, "shelves_right");
            Check(!gs.HasItem("book"), "locked restricted shelves prevent a catalogue bypass");
            await CancelPuzzle(() => game.Perform(Verb.Hand, "desk"), PuzzleKind.Catalogue, "catalogue_identified", "catalogue");
            await SolvePuzzle(() => game.Perform(Verb.Hand, "desk"), PuzzleKind.Catalogue,
                new[] { ("motif1", 1), ("entry2", 1) }, "catalogue", submit: false);
            var threaten = game.Perform(Verb.UseItem, "librarian", "revolver");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.StartsWith("Good Lord", StringComparison.Ordinal));
            Check(game.Player.PoseName == "micah_aim", "Micah aims the revolver at the librarian");
            await Shot("library_threat");
            await threaten;
            Check(gs.HasItem("book") && gs.HasFlag("librarian_threatened") && !gs.HasFlag("library_banned") &&
                game.Room?.Name == "Library" && game.Player.PoseName == null,
                "threatened the librarian into giving up the book; Micah stays until he leaves");
            await game.Perform(Verb.Talk, "librarian");
            Check(game.Room?.Name == "Library", "the cowed librarian won't talk any more");
            await game.Perform(Verb.Walk, "exit");
            Check(gs.HasFlag("library_banned") && game.Room?.Name == "ChicagoMap", "leaving after the hold-up bans the library");
            await game.Perform(Verb.Walk, "library");
            Check(game.Room?.Name == "ChicagoMap", "the library is off limits now");

            await game.ItemVerb(Verb.Hand, "book");
            Check(!gs.HasItem("address"), "the book is only read at the office");
            await game.Perform(Verb.Walk, "office");
            Check(game.Room?.Name == "Office", "back at the office");
            await game.ItemVerb(Verb.Hand, "book");
            Check(!gs.HasItem("address") && !gs.HasFlag("club_unlocked"), "book gives cipher instructions, not a free address");
            await ReloadCheckpoint("cipher_book_only");
            Check(gs.HasFlag("read_book") && !gs.HasItem("address") && !gs.HasFlag("club_unlocked"), "new save/load does not grandfather unfinished cipher");
            await Combine("card", "mirror");
            await WaitIdle(game);
            Check(!gs.HasFlag("card_reflected"), "cold blank card does not yield an address");
            var warming = game.Perform(Verb.UseItem, "radiator", "card");
            await Until(() => game.Hud.ImageVisible);
            await Shot("card_reversed");
            game.Hud.CloseImage();
            await warming;
            await CancelPuzzle(() => CombineAndWait("card", "mirror"), PuzzleKind.Cipher, "card_decoded", "card_cipher");
            await SolvePuzzle(() => CombineAndWait("mirror", "card"), PuzzleKind.Cipher,
                new[] { ("s0", 1), ("s1", 2) }, "card_cipher");
            Check(gs.HasItem("address") && gs.HasFlag("club_unlocked"), "heat, reflection and ornament order reveal Club address");
            await Shot("office_book");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "ChicagoMap" && game.Room?.FindHotspot("club")?.Visible == true, "the club is on the map now");
            await Shot("map_club");
            // ---- the Club, the first time: thrown out onto Hubbard Street
            var club = game.Perform(Verb.Walk, "club");
            await Until(() => game.Room?.Name == "ClubHall");
            Check(!gs.HasFlag("on_map") && game.Room?.FindHotspot("guest")?.Visible == false, "entered the Club, no masks around yet");
            await game.Wait(1);
            await Shot("club_hall");
            await Until(() => gs.HasFlag("brute_called"));
            await game.Wait(1);
            await Shot("club_hall_brute");
            await Until(() => game.Room?.Name == "Street");
            await game.Wait(1.5);
            await Shot("street_thrown_out");
            await Until(() => game.Room?.Name == "RoseHouse");
            await club;
            await WaitIdle(game);
            Check(gs.HasFlag("go_rose") && gs.HasFlag("club_out"), "chose to go to Rose's house");
            await Shot("rose_house");
            var bell = game.Perform(Verb.Hand, "bell");
            await Until(() => gs.HasFlag("rose_door"));
            await game.Wait(1.5);
            await Shot("rose_house_door");
            await Until(() => game.Player.Facing == Facing.Up && game.Player.Position.DistanceTo(Rooms.RoseHouse.TalkSpot) < 2);
            Check(game.Room!.FindActor("rose")!.Texture!.ResourcePath.EndsWith("/rose_front.png"),
                "Micah stands by the bell with his back to the screen, Rose faces the camera");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Wait!"));
            Check(!game.Hud.InsetVisible, "no close-up yet while Rose calls \"Wait!\"");
            await Until(() => game.Hud.InsetVisible);
            Check(game.Hud.CurrentCloseUp == CloseUps.Rose && game.Room?.Name == "RoseHouse", "Rose's close-up framed over the door after she calls Micah back");
            Check(!game.Hud.SpeechVisible, "the close-up opens on a silent look");
            Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "Rose's close-up fills most of the screen");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText.Contains("trouble"), "after the pause, Rose's last line over the close-up");
            Check(game.Hud.SpeechRect.Position.Y > game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.7f, "speech sits below Rose's face while the close-up is up");
            await game.Wait(1);
            await Shot("rose_house_wait");
            await Until(() => !game.Hud.InsetVisible);
            Check(game.Room?.Name == "RoseHouse", "Rose's close-up is gone before the door closes");
            await bell;
            Check(gs.HasFlag("rose_wait") && game.Room?.Name == "ChicagoMap", "Rose called Micah back, then the map");
            Check(game.Room?.FindHotspot("club")?.Visible == true && game.Room?.FindHotspot("convent")?.Visible == false, "convent not on the map yet");
            await game.Perform(Verb.Walk, "club");
            Check(game.Room?.Name == "ChicagoMap", "no use going back to the Club");

            // ---- Caleb points to the convent; the sister, and the revolver
            await game.Perform(Verb.Walk, "church");
            Check(gs.HasFlag("caleb_club") && game.Room?.Name == "ChicagoMap", "Caleb talked about the Club, then back to the map");
            await game.Perform(Verb.Walk, "church");
            Check(game.Room?.Name == "ChicagoMap" && !gs.HasFlag("church_before_office"), "repeat church visit doesn't anticipate the sister's threat");
            Check(!gs.HasItem("cross"), "taking the ring initially postpones the cross until Act 3");
            Check(game.Room?.FindHotspot("convent")?.Visible == true, "the convent is on the map");
            await game.Perform(Verb.Walk, "convent");
            Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_club_asked"), "asked the sister about the Club");
            await Shot("convent_act2");
            var threat = game.Perform(Verb.UseItem, "nun", "revolver");
            await game.Wait(1.5);
            await Shot("convent_gun");
            await threat;
            Check(gs.HasFlag("nun_threatened") && game.Room?.Name == "ChicagoMap", "the sister names Harrington");
            Check(game.Room?.FindHotspot("tribune")?.Visible == true && game.Room?.FindHotspot("harrington")?.Visible == false
                && game.Room?.FindHotspot("club")?.Visible == false
                && game.Room?.FindHotspot("library")?.Visible == false
                && game.Room?.FindHotspot("office")?.Visible == true, "the Tribune before Harrington; office remains available for ring recovery");
            await Shot("map_tribune");
            await game.Perform(Verb.Walk, "church");
            Check(gs.HasFlag("church_before_office") && game.Room?.Name == "ChicagoMap", "Caleb warns Micah before the office");

            // ---- the Tribune morgue: a clipping torn through the address, paste, and a pin in the Loop
            await game.Perform(Verb.Walk, "tribune");
            Check(game.Room?.Name == "NewspaperMorgue", "down in the Tribune morgue");
            await WaitIdle(game);
            await Shot("newspaper_morgue");
            await game.Perform(Verb.Hand, "drawer_h");
            Check(gs.HasItem("clipping_top") && gs.HasFlag("took_clipping_top"), "drawer H: the top half of the clipping");
            await game.Perform(Verb.Hand, "spike");
            Check(gs.HasItem("clipping_bottom") && gs.HasFlag("took_clipping_bottom"), "the copy spike: the bottom half");
            await game.Perform(Verb.UseItem, "wall_map", "clipping_top");
            Check(!gs.HasFlag("harrington_located"), "half a clipping is no address");
            await CombineAndWait("clipping_top", "clipping_bottom");
            Check(!gs.HasItem("clipping") && gs.HasItem("clipping_top") && gs.HasItem("clipping_bottom"), "the halves won't hold without paste");
            await game.Perform(Verb.Hand, "paste_pot");
            Check(gs.HasItem("paste") && gs.HasFlag("paste_out"), "borrowed the paste pot");
            await Shot("newspaper_morgue_taken");
            await CombineAndWait("clipping_top", "clipping_bottom");
            Check(gs.HasItem("clipping") && gs.HasItem("paste") && !gs.HasItem("clipping_top") && !gs.HasItem("clipping_bottom"),
                "pasted the halves together; the paste pot is kept");
            await ReloadCheckpoint("morgue_clipping");
            await game.Perform(Verb.UseItem, "wall_map", "clipping");
            Check(gs.HasFlag("harrington_located") && !gs.HasItem("clipping"), "the clipping pins the Harrington Building on LaSalle");
            await Shot("newspaper_morgue_pin");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "ChicagoMap" && !gs.HasItem("paste") && !gs.HasFlag("paste_out"), "the paste pot goes back on the way out");
            Check(game.Room?.FindHotspot("harrington")?.Visible == true && game.Room?.FindHotspot("tribune")?.Visible == false,
                "Harrington's office on the map, the Tribune off it");
            await Shot("map_harrington");

            // ---- the alley behind the Harrington Building
            await game.Perform(Verb.Walk, "harrington");
            Check(game.Room?.Name == "HarringtonRoad", "at the Harrington Building");
            await Shot("harrington_road");
            await game.Perform(Verb.Hand, "crates");
            Check(!gs.HasFlag("crates_stacked"), "the watchman sees Micah going for the crates");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonRoad", "can't climb while watched");
            await game.Perform(Verb.UseItem, "trash_can", MicahKit.LighterId);
            Check(gs.HasFlag("watchman_distracted"), "the fire sends the watchman inside");
            var flames = game.Room?.GetNodeOrNull<LoopStrip>("Flames");
            var flameFrame = flames?.Frame ?? -1;
            await game.Wait(0.35);
            Check(flames != null && flames.Visible && flames.Hframes > 1 && flames.Frame != flameFrame,
                "the trash-can fire's flames and smoke loop while it burns");
            await Shot("harrington_road_fire");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonRoad", "the ladder is too high without the crates");
            await game.Perform(Verb.Hand, "packing_wedge");
            await game.Perform(Verb.UseItem, "ladder_catch", "wedge");
            Check(!gs.HasFlag("ladder_freed") && gs.HasItem("wedge"), "catch cannot be reached before stacking crates; wedge retained");
            await game.Perform(Verb.Hand, "crates");
            Check(gs.HasFlag("crates_stacked"), "stacked the crates");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonRoad", "stacked crates alone do not bypass the jammed catch");
            await game.Perform(Verb.Hand, "packing_wedge");
            Check(gs.HasItem("wedge"), "collected packing wedge from distinct hotspot");
            await ReloadCheckpoint("ladder_wedge");
            await game.Perform(Verb.UseItem, "ladder_catch", "wedge");
            Check(gs.HasFlag("ladder_freed") && !gs.HasItem("wedge"), "wedge remains installed holding catch clear");
            await Shot("harrington_road_crates");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonOffice", "climbed into Harrington's office");
            await WaitIdle(game);
            await Shot("harrington_office");
            await game.Perform(Verb.Walk, "window");
            Check(game.Room?.Name == "HarringtonOffice", "can't leave empty-handed");
            await game.Perform(Verb.Hand, "drawer_left");
            await game.Perform(Verb.Hand, "drawer_right");
            Check(!gs.HasItem("invitation"), "the right drawer is locked");
            await game.Perform(Verb.UseItem, "drawer_right", "lockpick");
            Check(gs.HasItem("invitation"), "picked the drawer: the invitation");
            await game.Perform(Verb.Hand, "closet");
            Check(gs.HasFlag("harrington_closet_open"), "Harrington closet uses independent flag");
            var lookPortrait = game.Perform(Verb.Look, "portrait");
            await Until(() => game.Hud.InsetVisible);
            Check(game.Hud.CurrentCloseUp == CloseUps.Heraldry && game.Hud.InsetName == "heraldry_closeup",
                "looking at the portrait frames the band of heraldry at its foot");
            await Until(() => game.Hud.SpeechVisible);
            await Shot("harrington_portrait_heraldry");
            await lookPortrait;
            await Until(() => !game.Hud.InsetVisible);
            Check(gs.HasFlag("portrait_key_seen") && !game.Hud.InsetVisible, "the heraldry close-up closes after Micah's look");
            Check(new CrestsScreen().Clue == "Three dials. Three symbols.",
                "the false-back lock's clue box gives nothing away");
            await CancelPuzzle(() => game.Perform(Verb.UseItem, "panel", "lockpick"), PuzzleKind.Crests, "secret_open", "crest_lock");
            await SolvePuzzle(() => game.Perform(Verb.Hand, "panel"), PuzzleKind.Crests,
                new[] { ("s0", 2), ("s2", 1) }, "crest_lock");
            await Shot("harrington_office_niche");
            await game.Perform(Verb.Hand, "niche");
            Check(gs.HasItem("mask") && gs.HasItem("cloak"), "took the mask and the cloak");
            await Shot("harrington_office_after");
            await game.Perform(Verb.Walk, "window");
            Check(gs.HasFlag("harrington_done") && game.Room?.Name == "ChicagoMap", "out the window, back to the map");
            Check(game.Room?.FindHotspot("club")?.Visible == true && game.Room?.FindHotspot("harrington")?.Visible == false, "the Club is back on the map");
            await game.Perform(Verb.Walk, "church");
            Check(gs.HasFlag("church_before_club"), "Caleb's last warning before the Club");

            // ---- the Club, masked: end of Act Two, the bedroom, and the stage in Act 3
            await game.Perform(Verb.Walk, "club");
            await WaitIdle(game);
            Check(game.Room?.Name == "ClubVestibule" && gs.HasFlag("masked") && game.Player.Character == "micah_masked",
                "Micah goes in masked, by the vestibule");
            await Shot("club_vestibule");
            await game.Perform(Verb.Walk, "street_door");
            Check(game.Room?.Name == "ClubVestibule", "no way back out to the street");
            await game.Perform(Verb.UseItem, "slot", "invitation");
            Check(game.Room?.Name == "ClubVestibule" && !gs.HasFlag("vestibule_passed") && gs.HasItem("invitation"),
                "the slot refuses an unsealed invitation");
            await game.Perform(Verb.Look, "plaque");
            await game.Perform(Verb.Hand, "sealing_wax");
            Check(gs.HasItem("sealing_wax") && gs.HasFlag("took_sealing_wax"), "took the sealing wax");
            await CombineAndWait("sealing_wax", "invitation");
            Check(gs.HasItem("sealing_wax") && gs.HasItem("invitation") && !gs.HasItem("invitation_waxed"), "cold wax won't take");
            await CombineAndWait(MicahKit.LighterId, "sealing_wax");
            Check(gs.HasItem("wax_soft") && !gs.HasItem("sealing_wax") && gs.HasItem(MicahKit.LighterId) && gs.HasFlag("wax_softened"),
                "the lighter softens the wax and is kept");
            await CombineAndWait("wax_soft", "invitation");
            Check(gs.HasItem("invitation_waxed") && !gs.HasItem("invitation") && !gs.HasItem("wax_soft"), "wax dripped on the invitation");
            await game.Perform(Verb.UseItem, "slot", "invitation_waxed");
            Check(!gs.HasFlag("vestibule_passed") && gs.HasItem("invitation_waxed"), "the slot refuses wax with no seal in it");
            await game.Perform(Verb.Hand, "cloak_lion");
            Check(gs.HasItem("signet_lion"), "borrowed the lion signet");
            await CombineAndWait("signet_lion", "invitation_waxed");
            Check(gs.HasItem("invitation_waxed") && !gs.HasItem("sealed_invitation") && gs.HasItem("signet_lion"),
                "the lion is second in the procession, not first");
            await game.Perform(Verb.Hand, "cloak_raven");
            Check(gs.HasItem("signet_raven") && !gs.HasItem("signet_lion"), "taking the raven hangs the lion back up");
            await ReloadCheckpoint("vestibule_raven");
            await CombineAndWait("signet_raven", "invitation_waxed");
            Check(gs.HasItem("sealed_invitation") && !gs.HasItem("invitation_waxed") && !gs.HasItem("signet_raven")
                && gs.HasFlag("invitation_sealed"), "sealed with the raven, first of the procession; ring hung back up");
            await Shot("club_vestibule_sealed");
            var rite = game.Perform(Verb.UseItem, "slot", "sealed_invitation");
            await Until(() => gs.HasFlag("vestibule_passed"));
            await Shot("club_vestibule_open");
            await Until(() => game.Room?.Name == "ClubHall");
            await WaitIdle(game);
            Check(gs.HasFlag("masked") && game.Player.Character == "micah_masked", "Micah goes in masked");
            Check(gs.HasItem(MicahKit.LighterId) && gs.HasItem("sealed_invitation"), "lighter still held; the sealed card came back out of the slot");
            Check(game.Room?.FindHotspot("guest")?.Visible == true, "masked guests in the hall");
            await rite;
            await Shot("club_hall_masked");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "ClubLounge", "into the lounge");
            await Shot("club_lounge");
            var stage = game.Perform(Verb.Walk, "stage_exit");
            await Until(() => game.Room?.Name == "ClubStage");
            await Until(() => game.Hud.InsetVisible);
            Check(game.Hud.CurrentCloseUp == CloseUps.Stage && game.Hud.InsetName.StartsWith("stage_closeup"), "Eleanor's close-up framed over the stage after Micah's first line");
            Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "the close-up fills most of the screen");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechRect.Position.Y > game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.7f, "speech sits below her face while the close-up is up");
            await game.Wait(4);
            await Shot("club_stage");
            await Until(() => game.Room?.Name == "Attic");
            Check(!game.Hud.InsetVisible, "the close-up is gone in the attic");
            await game.Wait(2);
            await Shot("attic_night2");
            await Until(() => game.Hud.CaptionVisible);
            Check(game.Player.Character == "daniel" && !gs.HasItem("revolver") && gs.HasItem("journal") && !gs.HasItem(Notes.ItemId),
                "back in the attic, Micah's things put away");
            await Shot("end_of_act_two");
            await Until(() => game.Room?.Name == "Bedroom");
            Check(gs.StoryAct == 3, "Act Three");
            await game.Wait(2);
            await Shot("bedroom");
            await Until(() => game.Room?.Name == "ClubStage");
            Check(gs.HasItem("revolver") && gs.HasFlag("masked") && gs.Inventory.Take(2).SequenceEqual(MicahKit.Pinned),
                "back on the stage with Micah's things, notepad and lighter first");
            Check(gs.Inventory.Skip(2).All(i => MicahKit.KeptInAct(3, i)) && !gs.HasItem("mirror") && !gs.HasItem("card") &&
                !gs.HasItem("lockpick"), "Act 3 starts with only the revolver and Micah's commitments");
            await game.Wait(3);
            Check(game.Hud.InsetVisible, "the close-up is back when Act 3 opens on the stage");
            await Shot("club_stage_act3");
            await Until(() => gs.HasFlag("harrington_unmasked"));
            var unmasked = game.Room?.FindActor("harrington");
            Check(!game.Hud.InsetVisible && unmasked != null && game.Room?.FindActor("leader") == null
                  && unmasked.Texture?.ResourcePath == "res://assets/art/sprites/leader_unmasked.png",
                "the stag takes off his mask in front of everyone: Harrington senior, close-up gone");
            await game.Wait(1);
            await Shot("club_stage_unmasked");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Power that never shows itself"));
            Check(game.Hud.SpeechText.Contains("rumour"), "Harrington says the meeting is only the exercise of his power");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.StartsWith("I am where I belong", StringComparison.Ordinal));
            Check(game.Hud.SpeechText == "I am where I belong, Mr. Jones.", "Eleanor answers flatly, like a recording");
            await Until(() => gs.HasFlag("brute_stage"));
            Check(_insetAtCaughtChoice == false, "the close-up is removed before the revolver choice");
            await game.Wait(1);
            await Shot("club_stage_brute");
            await Until(() => game.Room?.Name == "ChurchExterior");
            await Until(() => game.Hud.InsetVisible);
            Check(game.Hud.CurrentCloseUp == CloseUps.Beaten && game.Hud.InsetName == "beaten_closeup", "Micah's close-up framed over the cathedral steps while he lies there");
            await game.Wait(1.5);
            Check(game.Hud.SpeechRect.Position.Y > game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.7f,
                "his thoughts sit below his face while the close-up is up");
            await Shot("church_exterior_beaten");
            await Until(() => game.Room?.Name == "Office");
            Check(_insetAtBeatenChoice == false, "Micah's close-up is removed before he gets up and chooses");
            await game.Wait(1.5);
            Check(game.Player.Visible && game.Player.Facing == Facing.Up && game.Player.Position.X > 380,
                "Act 3 office: Micah talks at the window, his back to the room");
            Check(gs.HasFlag("office_lamp_off") && game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("office_act3.png") == true,
                "Act 3 office is dim, the lamp off and the whiskey on the desk");
            await Shot("office_act3_window");
            await stage;
            await WaitIdle(game);
            Check(_poseCounts.GetValueOrDefault("micah_masked_collapse") == 1, "masked collapse ran on the revolver branch");
            Check(!game.Player.Poses.Active, "recovery restored the walking sprite before returning control");
            Check(game.Room?.Name == "Office" && !gs.HasFlag("micah_at_desk"), "Act 3 office returns player control");
            _prefer = new[] { "Visit Caleb", "Refuse the cross" };
            int offers = _crossOffers;
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "Office" && gs.HasFlag("church_act3_return") && !gs.HasItem("cross") && _crossOffers == offers + 1,
                "Act 3 Caleb visit offers cross, refusal returns to office");
            await game.Perform(Verb.Walk, "door");
            Check(_crossOffers == offers + 2 && !gs.HasItem("cross"), "Caleb offers again after refusal");
            _prefer = new[] { "Visit Caleb", "Accept the cross" };
            await game.Perform(Verb.Walk, "door");
            Check(gs.HasItem("cross") && gs.HasFlag("took_cross") && gs.Inventory.Count(i => i == "cross") == 1,
                "accepted pendant is recorded and given once");
            await game.Perform(Verb.Walk, "door");
            Check(_crossOffers == offers + 3 && game.Room?.Name == "Office" && !gs.HasFlag("micah_at_desk"),
                "accepted cross isn't offered again, desk scene isn't replayed");
            var savedCommitments = game.CaptureSave();
            Check(SaveSerializer.TryDeserialize(SaveSerializer.Serialize(savedCommitments))?.Inventory.Contains("cross") == true,
                "accepted pendant survives save serialization");
            gs.TakeItem("cross");
            await game.LoadGame(savedCommitments);
            Check(gs.HasItem("cross") && gs.HasItem("faith_ring") && gs.HasFlag("ring_taken_act2") && game.Room is Rooms.Office,
                "load restores ring, pendant and initial decision without replaying the desk");
            _prefer = new[] { "Go to the Blue Lantern" };
            await game.Perform(Verb.Walk, "door");
            Check(gs.HasFlag("keep_going") && !gs.HasFlag("masked") && gs.HasFlag("alley3"), "Micah keeps going: from his desk to the Blue Lantern");
            var act3Flags = gs.Flags.ToArray();
            var act3Items = gs.Inventory.ToArray();
            _act3Ink = DialogueManager.Instance.SaveInk();

            // ---- the alley: break the lamp, lure Sal out, knock him down, and bring Tony out
            await Shot("alley_act3");
            int stoneSteps = game.Sfx.Count(Sound.StepStone), knocks = game.Sfx.Count(Sound.Knock);
            int gunshots = game.Sfx.Count(Sound.Gunshot);
            await game.Perform(Verb.Talk, "back_door");
            Check(!gs.HasFlag("shot_bartender"), "not knocking with Sal inside");
            await game.Perform(Verb.Kick, "trash");
            Check(!gs.HasFlag("alley3_sal_out"), "no luring Sal out under the lamp");
            await game.Perform(Verb.Hand, "street_lamp");
            Check(gs.HasFlag("alley3_dark"), "broke the street lamp");
            Check(game.Sfx.Count(Sound.StepStone) > stoneSteps, "Micah's shoes sound on the alley cobbles");
            await Shot("alley_dark");
            await game.Perform(Verb.Kick, "trash");
            Check(gs.HasFlag("alley3_sal_out") && !gs.HasFlag("alley3_sal_inside"), "the noise brings Sal out");
            Check(game.Sfx.Count(Sound.Crash) > 0, "the trash cans go over with a crash");
            await Shot("alley_sal_out");
            CheckActorWins(game, "sal", "trash", "Sal, out by the trash cans, wins the hover over them (#97)");
            await game.Perform(Verb.UseItem, "sal", "revolver");
            Check(gs.HasFlag("alley3_sal_down"), "pistol-whipped Sal");
            Check(game.Room?.FindActor("sal") is { } downSal && downSal.Texture?.ResourcePath.EndsWith("sal_out.png") == true &&
                !downSal.Poses!.Active, "Sal goes down on his knees and ends face-down");
            await Shot("alley_sal_down");
            _prefer = new[] { "Shoot him", "You can't stay", "Every time" };
            var tonyTalk = game.Perform(Verb.Talk, "back_door");
            await Until(() => gs.HasFlag("shot_bartender") && game.Room?.FindActor("bartender") is { } t &&
                t.Texture?.ResourcePath.EndsWith("bartender_shot.png") == true);
            Check(game.Room?.FindActor("bartender")?.Texture?.ResourcePath.EndsWith("bartender_shot.png") == true,
                "Tony falls, shot in the shoulder, and stays down on his back");
            await Shot("alley_tony_shot");
            Check(game.Sfx.Count(Sound.Knock) >= knocks + 3, "Sal's knock is heard: two, a pause, and one");
            Check(game.Sfx.Count(Sound.Gunshot) == gunshots + 1, "the revolver goes off once");
            await tonyTalk;
            Check(Offered("bartender_gun", "Lower the gun"), "Caleb's counsel lets Micah walk away from Tony");
            Check(gs.HasFlag("shot_bartender") && game.Room?.Name == "MansionExterior", "shot Tony in the shoulder, on to the Harrington mansion");

            // ---- the mansion: the alarm bell, the key, the study, the bedroom
            await Shot("mansion_exterior");
            await game.Perform(Verb.Hand, "bell");
            await game.Perform(Verb.Look, "door");
            Check(gs.HasFlag("alarm_noticed"), "spotted the alarm wire");
            await game.Perform(Verb.Hand, "lintel");
            Check(gs.HasItem("kitchen_key"), "the key on the lintel");
            await game.Perform(Verb.Hand, "door");
            await game.Perform(Verb.Hand, "bell");
            Check(game.Room?.Name == "MansionExterior" && !gs.HasFlag("bell_wedged"), "the bell is out of reach");
            await game.Perform(Verb.Hand, "bin");
            Check(gs.HasFlag("bin_moved"), "moved the coal bin under the bell");
            await ReloadCheckpoint("alarm_unrestrained");
            Check(!gs.HasFlag("bell_wedged"), "save/load does not restrain a new alarm");
            await CancelPuzzle(() => game.Perform(Verb.Hand, "bell"), PuzzleKind.Bell, "bell_wedged", "alarm_restraint");
            await SolvePuzzle(() => game.Perform(Verb.Hand, "bell"), PuzzleKind.Bell,
                new[] { ("s1", 1), ("s2", 2) }, "alarm_restraint");
            Check(gs.HasFlag("bell_wedged"), "gagged the bell with the tie");
            await Shot("mansion_exterior_wedged");
            await game.Perform(Verb.Hand, "door");
            Check(game.Room?.Name == "MansionKitchen" && !gs.HasItem("kitchen_key"), "in through the kitchen, quietly");
            await Shot("mansion_kitchen");
            await game.Perform(Verb.Hand, "range");
            await game.Perform(Verb.Hand, "back_door");
            Check(!gs.HasFlag("gas_on") && game.Room?.Name == "MansionKitchen", "no gas, no leaving yet");
            await game.Perform(Verb.Walk, "baize_door");
            Check(game.Room?.Name == "MansionKitchen" && !gs.HasFlag("baize_unbolted"), "the baize door is bolted from the house side");
            // ---- the wine cellar: a lantern, kerosene and the lighter light the bootleggers' stair up to the study
            await game.Perform(Verb.Walk, "cellar_door");
            Check(game.Room?.Name == "MansionCellar" && !gs.HasFlag("cellar_lit"), "down the trapdoor into the dark cellar");
            await Shot("mansion_cellar_dark");
            await game.Perform(Verb.Walk, "stair");
            Check(game.Room?.Name == "MansionCellar", "no climbing the cellar stair blind");
            await game.Perform(Verb.Hand, "lantern");
            await game.Perform(Verb.Hand, "crates");
            Check(gs.HasItem("lantern") && gs.HasItem("kerosene") && gs.HasItem(MicahKit.LighterId), "lantern off the hook, kerosene off the crates, lighter in pocket");
            await Shot("mansion_cellar_taken");
            await CombineAndWait("lantern", MicahKit.LighterId);
            Check(gs.HasItem("lantern") && !gs.HasItem("lantern_filled") && !gs.HasItem("lantern_lit") && gs.HasItem(MicahKit.LighterId),
                "a dry wick won't light");
            await CombineAndWait("lantern", "kerosene");
            Check(gs.HasItem("lantern_filled") && !gs.HasItem("lantern") && !gs.HasItem("kerosene"), "filled the lantern");
            await CombineAndWait("lantern_filled", MicahKit.LighterId);
            Check(gs.HasItem("lantern_lit") && gs.HasFlag("lantern_lit") && gs.HasItem(MicahKit.LighterId), "lit the lantern; the lighter is kept");
            await game.Perform(Verb.UseItem, "stair", "lantern_lit");
            Check(gs.HasFlag("cellar_lit") && !gs.HasItem("lantern_lit"), "the lantern hung at the stair foot lights the cellar");
            await Shot("mansion_cellar_lit");
            await game.Perform(Verb.Walk, "stair");
            Check(game.Room?.Name == "MansionStudy", "up the bootleggers' stair into the study");
            await Shot("mansion_study_hatch");
            await game.Perform(Verb.Walk, "door_left");
            Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("baize_unbolted"), "unbolted the baize door from the study side");
            await game.Perform(Verb.Walk, "baize_door");
            Check(game.Room?.Name == "MansionStudy", "into the study");
            await Shot("mansion_study");
            await game.Perform(Verb.Hand, "drawer_right");
            await Shot("mansion_study_drawer");
            await game.Perform(Verb.Hand, "documents");
            Check(gs.HasItem("audit_folder") && !gs.HasItem("documents") && !gs.HasFlag(Endings.TookDocuments),
                "account register alone is not incriminating evidence");
            await game.Perform(Verb.Hand, "drawer_left");
            Check(gs.HasItem("audit_tracing"), "matching index found under the cigars");
            await ReloadCheckpoint("audit_unsolved");
            Check(!gs.HasFlag(Endings.TookDocuments) && gs.HasItem("audit_folder") && gs.HasItem("audit_tracing"),
                "both audit clues survive save/load without granting evidence");
            await CancelPuzzle(() => CombineAndWait("audit_tracing", "audit_folder"), PuzzleKind.Alignment, "audit_identified", "audit_alignment");
            await SolvePuzzle(() => CombineAndWait("audit_folder", "audit_tracing"), PuzzleKind.Alignment,
                new[] { ("rotate", 1), ("right", 6), ("down", 3) }, "audit_alignment");
            Check(gs.HasFlag(Endings.TookDocuments) && gs.HasItem("documents"), "index identifies signed payoff sheets");
            var confront = game.Perform(Verb.Walk, "door_right");
            await Until(() => game.Room?.Name == "MansionBedroom");
            await game.Wait(1.5);
            await Until(() => game.Hud.SpeechVisible && game.Room?.Name == "MansionBedroom");
            var mansionLine = game.Hud.SpeechText;
            Check(game.Hud.SpeechVisible && !confront.IsCompleted, "Act Three confrontation is speaking before pause");
            PressKey(Key.Space);
            // Longer than the longest unpaused line (7s) at the current scale, so a failed pause would have finished.
            await Observe(7.0 / Engine.TimeScale + 0.2);
            Check(game.IsPaused && game.Hud.SpeechVisible && game.Hud.SpeechText == mansionLine
                && !confront.IsCompleted && game.Room?.Name == "MansionBedroom",
                "Space freezes the Act Three confrontation mid-sentence");
            PressKey(Key.Space);
            Check(game.Player.Visible && game.Player.Position.Y < 218 && game.Player.Position.X is > 68 and < 148,
                "Micah listens in view behind the lowered folding screen (#104)");
            await Shot("mansion_bedroom");
            await Until(() => gs.HasFlag("eleanor_up"));
            Check(game.Player.Visible && game.Player.Position.DistanceTo(new Vector2(160, 236)) < 2,
                "Micah walks out from behind the screen to take aim (#104)");
            await game.Wait(0.5);
            await Shot("mansion_bedroom_gun");
            await confront;
            await WaitIdle(game);
            Check(Offered("oldman_taunt", "Lower the gun") == Endings.CanSpareOldMan(gs.HasFlag, gs.HasItem), "sparing the old man follows Caleb, Rose, ring and cross");
            Check(gs.HasFlag("shot_oldman") && gs.HasFlag("eleanor_convinced") && game.Room?.Name == "MansionKitchen", "shot the old man; Eleanor comes along at the second try");
            await Shot("mansion_kitchen_escape");
            await game.Perform(Verb.Walk, "baize_door");
            await game.Perform(Verb.Walk, "cellar_door");
            Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("escaping"), "no going back through the baize door or the cellar during the escape");
            await game.Perform(Verb.Hand, "range");
            await game.Perform(Verb.Hand, "candle");
            Check(gs.HasFlag("gas_on") && gs.HasFlag("candle_lit"), "gas on, candle lit");
            await Shot("mansion_kitchen_gas");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => gs.HasFlag(Endings.MansionExploded));
            await game.Wait(1.5);
            await Shot("mansion_explosion");
            await Until(() => game.Room?.Name == "Outskirts");
            Check(gs.HasFlag("ending_2"), "ending 2: out of town, together");
            await game.Wait(3);
            await Shot("ending_together");
            await TheEnd("ending_2");

            // ---- the other endings, each from a seeded state
            string[] alleyReady = act3Flags.Where(f => f != "alley3_sal_inside")
                .Concat(new[] { "alley3_dark", "alley3_sal_out", "alley3_sal_down" }).ToArray();

            // 5: no visits to Caleb, so no walking away; shoot, Eleanor stays, nothing to bargain with
            var noChurch = alleyReady.Where(f => f is not ("church_before_office" or "church_before_club" or "church_act3_return")).Append("rose_wait");
            Seed(noChurch, act3Items, "Shoot him", "You can't stay", "Nobody's coming");
            await game.ChangeRoom("alley", "act3");
            await game.Perform(Verb.Talk, "back_door");
            Check(!Offered("bartender_gun", "Lower the gun") && gs.HasFlag("shot_bartender"), "without Caleb, Micah can't walk away from Tony");
            await game.ChangeRoom("mansion_study", "start");
            await game.Perform(Verb.Hand, "drawer_right");
            await game.Perform(Verb.Hand, "drawer_left");
            await CancelPuzzle(() => game.Perform(Verb.UseItem, "documents", "audit_tracing"), PuzzleKind.Alignment, "audit_identified", "audit_room_use");
            Check(gs.HasItem("audit_folder") && gs.HasItem("audit_tracing") && !gs.HasFlag(Endings.TookDocuments),
                "cancelled room-use alignment retains clues but no evidence");
            await game.Perform(Verb.Walk, "door_right");
            Check(!Offered("oldman_taunt", "Lower the gun") && gs.HasFlag("shot_oldman"), "without Caleb, Micah can't spare the old man");
            Check(!gs.HasFlag("eleanor_convinced") && game.Room?.Name == "MansionKitchen", "Eleanor won't come");
            // Seeded endings follow the permanent epilogue lock; exercise the recipe without reopening its blocked HUD.
            await game.Run(game.TryReadAccounts);
            Check(!game.Hud.Puzzle.IsOpen && !gs.HasFlag(Endings.TookDocuments), "escape kitchen cannot decode skipped evidence after confrontation");
            await game.Perform(Verb.Walk, "baize_door");
            Check(game.Room?.Name == "MansionKitchen", "skipped study cannot be revisited during escape");
            await game.Perform(Verb.Walk, "cellar_door");
            Check(game.Room?.Name == "MansionKitchen", "nor reached through the cellar");
            await Shot("mansion_kitchen_alone");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Prison");
            Check(gs.HasFlag("ending_5"), "ending 5: prison, Caleb visits");
            await game.Wait(4);
            await Shot("ending_prison_caleb");
            await TheEnd("ending_5");

            // 4: Eleanor comes, but no ledgers and no fire
            Seed(act3Flags, act3Items, "Shoot him", "I didn't come all this way");
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(gs.HasFlag("eleanor_convinced"), "Eleanor convinced at the first try");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Prison");
            Check(gs.HasFlag("ending_4"), "ending 4: prison, Eleanor visits");
            await game.Wait(4);
            await Shot("ending_prison_eleanor");
            await TheEnd("ending_4");

            // 3: the house goes up, Eleanor stays behind
            Seed(act3Flags, act3Items, "Shoot him", "He had it coming", "I'll go to the police");
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(!gs.HasFlag("eleanor_convinced"), "Eleanor stays");
            await game.Perform(Verb.Hand, "range");
            await game.Perform(Verb.Hand, "candle");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Outskirts");
            Check(gs.HasFlag("ending_3") && gs.HasFlag(Endings.MansionExploded), "ending 3: out of town, alone");
            await Until(() => game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning", 10);
            bool nextMorning = game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning";
            Check(nextMorning, "alone explosion escape opens with the next-morning caption");
            await game.Wait(3);
            await Shot("ending_alone");
            await TheEnd("ending_3", nextMorning);

            // Signed evidence alone preserves both outskirts outcomes without a fire.
            foreach (bool convinced in new[] { false, true })
            {
                Seed(act3Flags.Append(Endings.TookDocuments), act3Items.Append("documents"),
                    "Shoot him", convinced ? "I didn't come all this way" : "He had it coming", "I'll go to the police");
                await game.ChangeRoom("mansion_bedroom", "start");
                Check(gs.HasFlag(Endings.EleanorConvinced) == convinced, "documents-only route preserves Eleanor's decision");
                _ = game.Perform(Verb.Walk, "back_door");
                await Until(() => game.Room?.Name == "Outskirts");
                string ending = convinced ? "ending_2" : "ending_3";
                Check(gs.HasFlag(ending) && !gs.HasFlag(Endings.MansionExploded) &&
                    !gs.HasFlag("gas_on") && !gs.HasFlag("candle_lit"), $"{ending}: signed evidence without explosion");
                await TheEnd($"{ending} (documents only)");
            }

            // Verify the actual Ink choices for each missing commitment, not only the helper predicates.
            foreach (string missing in new[] { "faith_ring", "cross" })
            {
                Seed(act3Flags.Append("rose_wait"), act3Items.Where(i => i != missing), "Shoot him", "He had it coming", "I'll go to the police");
                await game.ChangeRoom("mansion_bedroom", "start");
                Check(!Offered("oldman_taunt", "Lower the gun"), $"without {missing}, the final return is unavailable");
            }
            Seed(alleyReady, act3Items.Where(i => i != "faith_ring"), "Shoot him");
            await game.ChangeRoom("alley", "act3");
            await game.Perform(Verb.Talk, "back_door");
            Check(!Offered("bartender_gun", "Lower the gun"), "church return without ring doesn't allow walking away from Tony");

            // 1: walking away from Tony
            Seed(alleyReady, act3Items.Where(i => i != "cross"), "Lower the gun");
            await game.ChangeRoom("alley", "act3");
            _ = game.Perform(Verb.Talk, "back_door");
            await Until(() => game.Room?.Name == "RoseHouse");
            Check(gs.HasFlag("walked_away") && gs.HasFlag("ending_1"), "ending 1: walked away from Tony, coffee with Rose");
            await Until(() => gs.HasFlag("rose_door"));
            await game.Wait(1);
            await Until(() => game.Player.Facing == Facing.Up && game.Player.Position.DistanceTo(Rooms.RoseHouse.TalkSpot) < 2);
            Check(game.Player.Facing == Facing.Up, "Act 3: Micah stands by the bell, his back to the screen");
            await Shot("rose_coffee");
            await TheEnd("ending_1 (Tony)");

            // 1: sparing the old man
            Seed(act3Flags.Append("rose_wait"), act3Items, "Lower the gun");
            _ = game.ChangeRoom("mansion_bedroom", "start");
            await Until(() => game.Room?.Name == "RoseHouse");
            Check(gs.HasFlag("spared_oldman") && gs.HasFlag("ending_1"), "ending 1: spared the old man");
            await TheEnd("ending_1 (old man)");

            // 1: giving up on the church steps
            Seed(act3Flags.Where(f => f != "keep_going"), act3Items.Where(i => i is not ("faith_ring" or "cross")), "Give up");
            _ = game.ChangeRoom("church_exterior", "beaten");
            await Until(() => game.Room?.Name == "RoseHouse");
            Check(gs.HasFlag(Endings.GaveUpSteps) && gs.HasFlag("ending_1"), "ending 1: gave up on the steps");
            await TheEnd("ending_1 (steps)");
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            GD.Print(_failures.Count == 0 ? "AUTOPLAY OK" : "AUTOPLAY FAILED:\n  " + string.Join("\n  ", _failures));
            PosePlayback.FrameObserver = null;
            Engine.TimeScale = 1;
            game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
        }
    }

    private async Task ContentSettingsTest(Game game)
    {
        const string path = "user://autoplay_settings.cfg";
        if (FileAccess.FileExists(path))
            Check(DirAccess.RemoveAbsolute(path) == Error.Ok, "removed only the isolated test settings");
        Check(game.Settings.Load() && !game.Settings.NudityEnabled, "nudity defaults to off");
        game.Hud.ShowTitle(true);
        var title = game.Hud.Menu.OpenTitle();
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

    public async Task RunPauseTests(Game game)
    {
        _game = game;
        if (!ApplyClock(out var clockError))
        {
            GD.Print("PAUSE TEST FAILED:\n  " + clockError);
            game.GetTree().Quit(1);
            return;
        }
        game.AutosaveEnabled = false;
        try
        {
            await game.ChangeRoom("attic", "start");
            await PauseTest(game);
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            if (game.IsPaused) game.TogglePause();
        }
        GD.Print(_failures.Count == 0 ? "PAUSE TEST OK" : "PAUSE TEST FAILED:\n  " + string.Join("\n  ", _failures));
        game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    private async Task PauseTest(Game game)
    {
        double timeScale = Engine.TimeScale;
        Engine.TimeScale = 1;
        try
        {
            var speech = game.Run(() => game.Say("Pause test."));
            await Observe(0.35);
            var frame = game.Player.GetChildren().OfType<Sprite2D>().Single().Frame;
            var playtime = game.CaptureSave().PlaytimeSeconds;
            PressKey(Key.Space);
            Check(game.IsPaused && game.GetTree().Paused && game.Hud.PauseVisible, "Space pauses mid-sentence");
            _game.GetViewport().PushInput(new InputEventKey
            {
                Keycode = Key.Space, PhysicalKeycode = Key.Space, Pressed = true, Echo = true,
            }, true);
            Click(new Vector2(240, 140), MouseButton.Left);
            Click(game.Hud.SatchelCenter, MouseButton.Left);
            PressKey(Key.Escape);
            await Observe(2);
            Check(game.IsPaused && !game.Hud.Menu.IsOpen, "repeat Space and Esc do not exit Space pause");
            Check(!speech.IsCompleted && game.Hud.SpeechVisible && game.Hud.SpeechText == "Pause test.",
                "paused speech survives its full duration and cannot be skipped");
            Check(game.Player.GetChildren().OfType<Sprite2D>().Single().Frame == frame, "talk animation freezes");
            Check(game.CaptureSave().PlaytimeSeconds == playtime && !game.Hud.InventoryOpen, "playtime and inventory input freeze");
            PressKey(Key.Space);
            await Observe(0.3);
            Check(!game.IsPaused && !game.Hud.PauseVisible && !speech.IsCompleted, "resume retains remaining sentence duration");
            await AwaitTest(speech, "speech finishes after resuming");
            var nextSpeech = game.Run(() => game.Say("Click to skip."));
            await Observe(0.3);
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(0.3);
            Check(nextSpeech.IsCompleted && !game.Hud.SpeechVisible, "click-to-skip still works after resuming");

            var timer = game.Wait(0.8);
            await Observe(0.2);
            PressKey(Key.Space);
            await Observe(1);
            Check(!timer.IsCompleted, "gameplay timer does not expire while paused");
            PressKey(Key.Space);
            await Observe(0.2);
            Check(!timer.IsCompleted, "gameplay timer retains its remaining duration");
            await AwaitTest(timer, "gameplay timer completes after resuming");

            var walk = game.WalkTo(new Vector2(300, 205));
            await Observe(0.1);
            var position = game.Player.Position;
            PressKey(Key.Space);
            Click(new Vector2(420, 220), MouseButton.Left);
            await Observe(0.8);
            Check(!walk.IsCompleted && game.Player.IsWalking && game.Player.Position == position, "walking path freezes without cancellation");
            PressKey(Key.Space);
            await AwaitTest(walk, "walking completes after resuming");
            Check(await walk, "resume preserves the original walk");

            game.Hud.ShowInventory(true);
            PressKey(Key.Space);
            Click(new Vector2(10, 220), MouseButton.Left);
            await Observe(0.1);
            Check(game.Hud.InventoryOpen, "paused inventory remains open despite outside clicks");
            PressKey(Key.Space);
            Check(game.Hud.InventoryOpen, "resume preserves open inventory");
            game.Hud.ShowInventory(false);

            var choices = game.Hud.ShowChoices(new[] { "Pause regression choice" });
            var choiceButton = game.Hud.FindChildren("*", "Button", true, false).OfType<Button>()
                .Single(b => b.Text == "Pause regression choice");
            await Observe(0.1);
            PressKey(Key.Space);
            Click(choiceButton.GetGlobalRect().GetCenter(), MouseButton.Left);
            await Observe(0.1);
            Check(!choices.IsCompleted && game.Hud.ChoicesVisible, "dialogue choices cannot be selected while paused");
            PressKey(Key.Space);
            Click(choiceButton.GetGlobalRect().GetCenter(), MouseButton.Left);
            await AwaitTest(choices, "dialogue choices work after resuming");

            var image = game.Hud.ShowImage(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"));
            PressKey(Key.Space);
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(0.1);
            Check(!image.IsCompleted && game.Hud.ImageVisible, "paused close-up cannot be dismissed");
            PressKey(Key.Space);
            Click(new Vector2(240, 140), MouseButton.Left);
            await AwaitTest(image, "close-up can be dismissed after resuming");

            var wheel = game.Hud.Wheel.Open(new Vector2(240, 140), "Pause regression");
            PressKey(Key.Space);
            Click(game.Hud.Wheel.SlotCenter(Verb.Look), MouseButton.Left);
            await Observe(0.1);
            Check(!wheel.IsCompleted && game.Hud.Wheel.IsOpen, "paused verb wheel cannot be selected");
            PressKey(Key.Space);
            Click(game.Hud.Wheel.SlotCenter(Verb.Look), MouseButton.Left);
            await AwaitTest(wheel, "verb wheel works after resuming");
            Check(await wheel == Verb.Look, "verb wheel retains its selection layout");

            var puzzle = game.Hud.Puzzle.Open(PuzzleKind.Lift);
            foreach (var (step, _) in LiftRoute()) PuzzleClick(step);
            PressKey(Key.Space);
            PuzzleClick("submit");
            PuzzleClick("reset");
            PuzzleClick("down");
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(game.IsPaused && game.Hud.Puzzle.IsOpen && !puzzle.IsCompleted,
                "Space pause blocks puzzle submission, reset, controls, and Esc");
            PressKey(Key.Space);
            PuzzleClick("submit");
            await AwaitTest(puzzle, "puzzle resumes with its settings preserved");
            Check(await puzzle, "paused puzzle controls did not change the correct solution");

            var fade = game.Hud.Fade(1, 0.8);
            await Observe(0.2);
            var alpha = game.Hud.FadeAlpha;
            PressKey(Key.Space);
            await Observe(1);
            Check(!fade.IsCompleted && game.Hud.FadeAlpha == alpha && game.Hud.PauseVisible, "fade freezes with pause indicator above it");
            PressKey(Key.Space);
            await AwaitTest(fade, "fade completes after resuming");
            await game.Hud.Fade(0, 0.1);

            PressKey(Key.Escape);
            await Observe(0.1);
            Check(game.Hud.Menu.IsOpen && game.GetTree().Paused && !game.IsPaused, "Esc menu still pauses separately");
            PressKey(Key.Space);
            Check(game.Hud.Menu.IsOpen && game.GetTree().Paused && !game.IsPaused, "Space does not resume the Esc menu");
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(!game.Hud.Menu.IsOpen && !game.GetTree().Paused, "Esc still resumes its own menu");

            game.Hud.ShowTitle(true);
            PressKey(Key.Space);
            Check(!game.IsPaused && !game.GetTree().Paused, "Space does nothing on the title screen");
            game.Hud.ShowTitle(false);
            for (int i = 0; i < 3; i++)
            {
                PressKey(Key.Space);
                Check(game.IsPaused, "repeated toggle pauses");
                PressKey(Key.Space);
                Check(!game.IsPaused && !game.GetTree().Paused, "repeated toggle resumes");
            }
        }
        finally
        {
            if (game.IsPaused) game.TogglePause();
            Engine.TimeScale = timeScale;
        }
    }

    /// <summary>
    /// <c>--clock=fast</c> (default) uncapped 60×, or <c>--clock=normal</c> for the previous 8× clock.
    /// Pause assertions still force 1×. Fast also disables vsync so an unfocused run is not stuck at the refresh rate.
    /// </summary>
    internal static bool ApplyClock(out string error)
    {
        error = "";
        string? value = null;
        foreach (var arg in OS.GetCmdlineUserArgs())
        {
            if (arg == "--clock")
            {
                error = "--clock requires =normal or =fast";
                return false;
            }
            if (!arg.StartsWith("--clock=")) continue;
            if (value != null)
            {
                error = "--clock given more than once";
                return false;
            }
            value = arg["--clock=".Length..];
        }
        if (value is null or "fast")
        {
            Engine.TimeScale = FastTimeScale;
            Engine.MaxPhysicsStepsPerFrame = 256;
            Engine.MaxFps = 0;
            OS.LowProcessorUsageMode = false;
            DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Disabled);
            GD.Print("[autoplay] clock fast (60x, vsync off)");
            return true;
        }
        if (value == "normal")
        {
            Engine.TimeScale = NormalTimeScale;
            GD.Print("[autoplay] clock normal (8x)");
            return true;
        }
        error = $"unknown --clock={value} (use normal or fast)";
        return false;
    }

    private async Task Observe(double seconds)
    {
        var timer = _game.GetTree().CreateTimer(seconds, processAlways: true, ignoreTimeScale: true);
        await _game.ToSignal(timer, SceneTreeTimer.SignalName.Timeout);
    }

    private async Task AwaitTest(Task task, string description)
    {
        for (int i = 0; i < 100 && !task.IsCompleted; i++) await Observe(0.05);
        if (!task.IsCompleted) throw new TimeoutException(description);
        await task;
        Check(true, description);
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
        Check(game.Carried == "crowbar" && !game.Hud.InventoryOpen, "clicking an item holds it as the cursor");
        Check(game.Hud.CursorItemVisible && game.Hud.CursorSize == crosshair,
            "a held item shows as a badge while the crosshair keeps its size");
        PressKey(Key.Space);
        Click(slot, MouseButton.Left);
        await Observe(0.1);
        Check(game.IsPaused && game.Carried == "crowbar", "Space pause preserves the carried inventory item");
        PressKey(Key.Space);
        var trunk = new Vector2(432, 205);
        Move(trunk);
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
        throw new InvalidOperationException($"Inventory does not contain '{item}'.");
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
        Check(game.Hud.Menu.Press("Slot 1"), "save menu lists slot 1");
        await Observe(0.1);
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

    private void PressKey(Key key, bool alt = false)
    {
        foreach (var pressed in new[] { true, false })
            _game.GetViewport().PushInput(
                new InputEventKey { Keycode = key, PhysicalKeycode = key, AltPressed = alt, Pressed = pressed }, true);
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
        Check(game.Hud.CurrentCloseUp == CloseUps.Convent && game.Hud.SpeechVisible &&
            speech.Position.X >= (right ? divider : panel.Position.X) &&
            speech.End.X <= (right ? panel.End.X : divider),
            right ? "Eleanor's subtitle stays beneath the right portrait" : "Micah's subtitle stays beneath the left portrait");
        Check(speech.Position.Y > panel.Position.Y + panel.Size.Y * 0.7f && speech.End.Y < panel.End.Y,
            "portrait speech wraps below the face and inside the frame");
    }

    private async Task ConventFarewellTalkTest(Game game)
    {
        var original = game.CaptureSave();
        var originalPrefer = _prefer;
        try
        {
            var talk = game.Perform(Verb.Talk, "nun");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText == "What do you hope to find in all this, Detective?",
                "talking to the nun starts the farewell without the exit-only call-back");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "I don't know, sister, but I can't stop at this point.");
            Check(game.Hud.SpeechText == "I don't know, sister, but I can't stop at this point.",
                "Micah's direct farewell reply matches the approved line");
            await Shot("convent_farewell");
            await talk;
            Check(game.Room is Rooms.ConventCorridor && GameState.Instance.HasFlag("nun_farewell_done") &&
                !GameState.Instance.HasFlag("convent_departed") && !game.Busy,
                "talking first clears Micah to leave but does not leave for him");
            await ReloadCheckpoint("convent_farewell");
            Check(GameState.Instance.HasFlag("nun_farewell_done") && !game.Hud.SpeechVisible,
                "loading after the farewell preserves permission without replaying it");
            var again = game.Perform(Verb.Talk, "nun");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText == "Go with God, Detective.", "the completed farewell does not repeat on another talk");
            await again;
            _prefer = new[] { "Right now, I'm not so sure." };
            Click(game.Room!.FindHotspot("entrance")!.Bounds.GetCenter(), MouseButton.Left);
            await Until(() => game.Room is Rooms.ConventRoad || game.Hud.SpeechVisible);
            Check(game.Room is Rooms.ConventRoad && GameState.Instance.HasFlag("convent_departed"),
                "opening the entrance after talking leaves directly without a second farewell");
            await Until(() => game.Hud.SpeechVisible &&
                game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month.");
            Check(game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month." &&
                !game.Hud.InsetVisible && !game.Hud.InsetDrawn,
                "the alternate compensation answer also continues on the road");
            await Until(() => game.Room is Rooms.Attic && !game.Busy, timeout: 300);
            if (game.Room is not Rooms.Attic || game.Busy)
                throw new InvalidOperationException($"Convent departure did not finish: room={game.Room?.Name}, busy={game.Busy}.");
            Check(game.Room is Rooms.Attic && !game.Busy, "the direct-talk exit completes the motel sequence");
        }
        finally
        {
            _prefer = originalPrefer;
            await game.LoadGame(original);
        }
    }

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

    /// <summary>Starts a seeded Act 3 run from the alley: its flags (edited), inventory and Ink state, and the choices to prefer.</summary>
    private async Task RingAndCrossTest(Game game)
    {
        var gs = GameState.Instance;
        var originalFlags = gs.Flags.ToArray();
        var originalItems = gs.Inventory.ToArray();
        var originalInk = DialogueManager.Instance.SaveInk();
        var originalPrefer = _prefer;
        int offers = _crossOffers;
        var openingFlags = originalFlags.Where(f => f is not ("ring_taken_act2" or "took_faith_ring" or
            "act2_office_done" or "act2_whiskey_drunk" or "caleb_met" or "act2_church_thought"))
            .Append("act2_church");
        gs.Restore(openingFlags, originalItems.Where(i => i != "faith_ring"), 2);
        _prefer = new[] { "Leave the wedding ring" };
        await game.ChangeRoom("office", "act2");
        Check(gs.HasFlag("ring_left_act2") && !gs.HasFlag("ring_taken_act2") && !gs.HasItem("faith_ring"),
            "leaving the ring records the original choice without granting it");
        Check(_crossOffers == offers, "initial confession never offers the cross even when ring was left");
        gs.SetFlag("teddy_gone", false);
        await game.Perform(Verb.Walk, "office");
        Check(gs.HasFlag("teddy_gone") && game.Room?.FindHotspot("teddy")?.Visible != true,
            "Teddy doesn't come back to the office after Act 1");
        Check(game.Room?.GetNodeOrNull<Sprite2D>("WeddingRing/Glint") != null
            && game.Room?.FindHotspot("faith_ring")?.Bounds.Size is { X: <= 10, Y: <= 8 }, "the small ring glints on the desk");
        Check(game.Room?.FindHotspot("faith_ring")?.Visible == true, "left ring remains visible at the office");
        await Shot("office_ring_left");
        await game.Perform(Verb.Walk, "door");
        gs.SetFlag("club_out");
        gs.SetFlag("caleb_club");
        _prefer = new[] { "Refuse the cross" };
        await game.Perform(Verb.Walk, "church");
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 2 && !gs.HasItem("cross"), "Act 2 refusal repeats the offer on the next visit");
        await game.Perform(Verb.Walk, "office");
        await game.Perform(Verb.Hand, "faith_ring");
        Check(gs.HasItem("faith_ring") && gs.HasFlag("ring_left_act2") && !gs.HasFlag("ring_taken_act2") &&
            game.Room?.FindHotspot("faith_ring")?.Visible == false, "recovering the ring preserves the original leave decision");
        await game.Perform(Verb.Walk, "door");
        _prefer = new[] { "Accept the cross" };
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 3 && gs.HasItem("cross") && gs.HasFlag("took_cross"),
            "recovered ring doesn't postpone the Act 2 cross offer");
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 3 && gs.Inventory.Count(i => i == "cross") == 1, "Act 2 acceptance stops duplicate offers");
        Rooms.Attic.StashMicahItems();
        Check(!gs.HasItem("faith_ring") && !gs.HasItem("cross") && gs.HasFlag("ring_left_act2") && !gs.HasItem(Notes.ItemId),
            "Daniel's interlude puts Micah's commitments aside without losing the original decision");
        Rooms.Attic.RestoreMicahItems(2);
        Check(gs.HasItem("faith_ring") && gs.HasItem("cross") && gs.HasFlag("took_cross"),
            "both commitments return with Micah's inventory");
        gs.TakeItem("faith_ring");
        gs.SetFlag("took_faith_ring", false);
        gs.SetFlag("micah_at_desk");
        gs.SetFlag("keep_going");
        gs.SetStoryAct(3);
        await game.ChangeRoom("office", "act3");
        Check(game.Room?.Name == "Office" && !game.Busy, "Act 3 office waits for player input");
        await game.Perform(Verb.Hand, "faith_ring");
        Check(gs.HasItem("faith_ring") && gs.HasFlag("ring_left_act2"), "left ring can be recovered at the Act 3 office");

        gs.Restore(originalFlags, originalItems, 2);
        DialogueManager.Instance.LoadInk(originalInk);
        _prefer = originalPrefer;
        await game.ChangeRoom("chicago_map", "start");
    }

    private async Task StoryDialogueTest(Game game)
    {
        var dialogue = DialogueManager.Instance;
        _ = dialogue.Get("pushes");
        var original = game.CaptureSave();
        double scale = Engine.TimeScale;
        var story = GD.Load<GodotInk.InkStory>(DialogueManager.StoryPath);
        try
        {
            foreach (var (knot, excerpt) in new[]
            {
                ("nun", "\"I will shew thee, O man, what is good.\""),
                ("caleb_act2", "Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace."),
                ("caleb_warn", "There's still a way back. There always is. But not where you're going."),
                ("caleb_last", "God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him."),
            })
            {
                await game.LoadGame(original);
                story.ChoosePathString(knot);
                string lines = "";
                for (int turn = 0; turn < 32; turn++)
                {
                    lines += story.ContinueMaximally();
                    if (story.CurrentChoices.Count == 0) break;
                    story.ChooseChoiceIndex(0);
                }
                Check(lines.Contains(excerpt, StringComparison.Ordinal), $"{knot}: approved compiled dialogue");
            }
            foreach (bool together in new[] { false, true })
            foreach (bool exploded in new[] { false, true })
            foreach (bool documents in new[] { false, true })
            {
                await game.LoadGame(original);
                GameState.Instance.SetFlag(Endings.MansionExploded, exploded);
                GameState.Instance.SetFlag(Endings.TookDocuments, documents);
                story.ChoosePathString(together ? "ending_together" : "ending_alone");
                string lines = story.ContinueMaximally();
                bool deathReport = !together && exploded;
                Check(lines.Contains("The morning paper lists the dead. Eleanor Harrington.", StringComparison.Ordinal) == deathReport,
                    $"newspaper death report: together={together}, exploded={exploded}, documents={documents}");
                Check(lines.Contains("I left her there and lit the fuse.", StringComparison.Ordinal) == deathReport &&
                    lines.Contains("They know who died. They don't know what I did.", StringComparison.Ordinal) == deathReport,
                    "responsibility and secret lines accompany only the death report");
                Check(!lines.Contains("The sky over the Gold Coast is still orange.", StringComparison.Ordinal),
                    "next-morning dialogue does not retain the same-night sky");
            }
            await game.LoadGame(original);
            Engine.TimeScale = 1;
            var timer = System.Diagnostics.Stopwatch.StartNew();
            await game.ChangeRoom("office", "start");
            timer.Stop();
            Check(GameState.Instance.HasFlag("teddy_gone"), "unaccelerated office sample completes its real dialogue");
            GD.Print($"[story timing] Office introduction at normal speed, automatic choices, no speech skipping: {timer.Elapsed.TotalSeconds:F1}s. Not a full-game or human playtime.");
        }
        finally
        {
            Engine.TimeScale = scale;
            await game.LoadGame(original);
        }
    }

    /// <summary>Awaits <paramref name="task"/>, collecting every speech line shown meanwhile.</summary>
    private static async Task<System.Collections.Generic.List<string>> Listen(Game game, Task task)
    {
        var heard = new System.Collections.Generic.List<string>();
        while (!task.IsCompleted)
        {
            if (game.Hud.SpeechVisible && (heard.Count == 0 || heard[^1] != game.Hud.SpeechText))
                heard.Add(game.Hud.SpeechText);
            await game.Wait(0.05);
        }
        await task;
        return heard;
    }

    private async Task RoseWalkAwayTest(Game game)
    {
        var original = game.CaptureSave();
        var dialogue = DialogueManager.Instance;
        var choose = dialogue.AutoChoose!;
        try
        {
            foreach (var walkAway in new[] { false, true })
            {
                await game.LoadGame(original);
                dialogue.ResetInk();
                string[]? offered = null;
                dialogue.AutoChoose = (knot, options) =>
                {
                    if (knot != "rose_leave") return choose(knot, options);
                    offered = options.ToArray();
                    return Task.FromResult(walkAway ? 0 : 1);
                };
                await game.ChangeRoom("rose_house", "start");
                var heard = await Listen(game, game.Perform(Verb.Walk, "exit"));
                Check(offered is { Length: 2 } && offered[0].Contains("Walk away") && offered[1].Contains("Not yet"),
                    "leaving Rose's house before ringing is an active choice");
                Check(!GameState.Instance.HasFlag("rose_door") && !heard.Any(l => l.StartsWith("Good night") || l.Contains("Micah Jones")),
                    "Rose never opens the door nor answers when Micah doesn't ring");
                if (!walkAway)
                {
                    Check(game.Room?.Name == "RoseHouse" && !GameState.Instance.HasFlag("rose_avoided"), "\"Not yet\" keeps Micah at Rose's door");
                    continue;
                }
                Check(game.Room?.Name == "ChicagoMap" && GameState.Instance.HasFlag("rose_avoided") &&
                    !GameState.Instance.HasFlag("rose_wait") && !GameState.Instance.HasFlag("rose_done"),
                    "walking away without a word returns to the map, like leaving without insisting");
                Check(heard.Any(l => l.Contains("left the bell alone")), "Micah's closing thought as he walks away");
                await game.LoadGame(game.CaptureSave());
                Check(GameState.Instance.HasFlag("rose_avoided") && !GameState.Instance.HasFlag("rose_wait"),
                    "save/load preserves walking away from Rose's door");
            }
        }
        finally
        {
            dialogue.AutoChoose = choose;
            await game.LoadGame(original);
        }
    }

    private async Task RoseAppealsTest(Game game)
    {
        var original = game.CaptureSave();
        var dialogue = DialogueManager.Instance;
        var choose = dialogue.AutoChoose!;
        try
        {
            for (int appeals = 0; appeals <= 5; appeals++)
            {
                await game.LoadGame(original);
                dialogue.ResetInk();
                dialogue.AutoChoose = (knot, options) => knot == "rose_house"
                    ? Task.FromResult(dialogue.Get("pushes").AsInt32() < appeals ? 0 : options.Count - 1)
                    : choose(knot, options);
                await game.ChangeRoom("rose_house", "start");
                var heard = new System.Collections.Generic.List<string>();
                var visit = game.Perform(Verb.Hand, "bell");
                while (!visit.IsCompleted)
                {
                    if (game.Hud.SpeechVisible && (heard.Count == 0 || heard[^1] != game.Hud.SpeechText))
                        heard.Add(game.Hud.SpeechText);
                    await game.Wait(0.05);
                }
                await visit;
                bool dismissed = heard.Any(l => l.Contains("Don't bother ringing this bell again, Micah Jones."));
                bool shutForGood = heard.Any(l => l.Contains("Just once, and for good."));
                Check(dismissed == (appeals < 3) && shutForGood == (appeals < 3),
                    $"Rose {(appeals < 3 ? "dismisses Micah and shuts the door" : "doesn't dismiss Micah")} after {appeals} appeals");
                Check(heard.Any(l => l.Contains("Wait!")) == (appeals >= 3), $"\"Wait!\" only after insisting ({appeals} appeals)");
                Check(dialogue.Get("pushes").AsInt32() == appeals, $"Rose visit records {appeals} appeals");
                Check(GameState.Instance.HasFlag("rose_wait") == (appeals >= 3),
                    $"Rose callback threshold after {appeals} appeals");
                Check(game.Room?.Name == "ChicagoMap" && !GameState.Instance.HasFlag("rose_door"),
                    "Rose closes the door and the visit returns to the map");
                await game.LoadGame(game.CaptureSave());
                Check(GameState.Instance.HasFlag("rose_wait") == (appeals >= 3) &&
                    dialogue.Get("pushes").AsInt32() == appeals, "save/load preserves the actual doorstep decision");
            }
        }
        finally
        {
            dialogue.AutoChoose = choose;
            await game.LoadGame(original);
        }
    }

    private void Seed(IEnumerable<string> flags, IEnumerable<string> items, params string[] prefer)
    {
        _game.Hud.ShowCaption(null);
        GameState.Instance.Restore(flags.ToArray(), items.ToArray(), 3);
        DialogueManager.Instance.LoadInk(_act3Ink);
        if (prefer.Length > 0) _prefer = prefer;
        _offered.Clear();
    }

    private bool Offered(string knot, string option) =>
        _offered.TryGetValue(knot, out var options) && options.Any(o => o.Contains(option));

    /// <summary>Waits for "End of Act Three", then for Daniel's epilogue to finish on "The End".</summary>
    private async Task TheEnd(string ending, bool sawNextMorning = false)
    {
        bool outskirts = _game.Room is Rooms.Outskirts;
        await Until(() =>
        {
            if (_game.Hud.CaptionVisible && _game.Hud.CaptionText == "The next morning")
                sawNextMorning = true;
            return _game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three";
        }, 120);
        Check(_game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three", $"{ending}: End of Act Three");
        var gs = GameState.Instance;
        if (outskirts)
            Check(sawNextMorning == (gs.HasFlag("ending_3") && gs.HasFlag(Endings.MansionExploded)),
                $"{ending}: next-morning transition only after alone escape with explosion");
        bool keepJournal = gs.HasFlag("ending_1");
        await Until(() => _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End", 120);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End",
            $"{ending}: final attic caption");
        Check(gs.HasItem("journal") == keepJournal,
            $"{ending}: Daniel {(keepJournal ? "keeps the journal for Leo" : "puts the journal back")}");
        var story = GD.Load<GodotInk.InkStory>(DialogueManager.StoryPath);
        string inkState = story.SaveState();
        try
        {
            story.ChoosePathString("epilogue");
            string[] lines = story.ContinueMaximally().Split('\n', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
            Check(lines.Contains("DANIEL: Maybe Leo would like to read it some day.") == keepJournal,
                $"{ending}: Leo's exact line only appears after reconciliation");
            Check(lines.Contains("DANIEL: That's enough of you for one lifetime, Micah Jones.") == !keepJournal,
                $"{ending}: dismissal only appears without reconciliation");
        }
        finally
        {
            story.LoadState(inkState);
        }
        if (!_theEndShot) await Shot("the_end");
        _theEndShot = true;
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
        await Observe(0.4 / Engine.TimeScale);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
