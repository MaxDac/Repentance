using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
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
            await PauseTest(game);
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
            await bell;
            Check(gs.HasFlag("rose_wait") && game.Room?.Name == "ChicagoMap", "Rose called Micah back, then the map");
            Check(game.Room?.FindHotspot("club")?.Visible == true && game.Room?.FindHotspot("convent")?.Visible == false, "convent not on the map yet");
            await game.Perform(Verb.Walk, "club");
            Check(game.Room?.Name == "ChicagoMap", "no use going back to the Club");

            // ---- Caleb points to the convent; the sister, and the revolver
            await game.Perform(Verb.Walk, "church");
            Check(gs.HasFlag("caleb_club") && game.Room?.Name == "ChicagoMap", "Caleb talked about the Club, then back to the map");
            await game.Perform(Verb.Walk, "church");
            Check(game.Room?.Name == "ChicagoMap", "nothing new at the church yet");
            Check(game.Room?.FindHotspot("convent")?.Visible == true, "the convent is on the map");
            await game.Perform(Verb.Walk, "convent");
            Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_club_asked"), "asked the sister about the Club");
            await Shot("convent_act2");
            var threat = game.Perform(Verb.UseItem, "nun", "revolver");
            await game.Wait(1.5);
            await Shot("convent_gun");
            await threat;
            Check(gs.HasFlag("nun_threatened") && game.Room?.Name == "ChicagoMap", "the sister names Harrington");
            Check(game.Room?.FindHotspot("harrington")?.Visible == true && game.Room?.FindHotspot("club")?.Visible == false
                && game.Room?.FindHotspot("library")?.Visible == false, "only the church and Harrington are left on the map");
            await Shot("map_harrington");
            await game.Perform(Verb.Walk, "church");
            Check(gs.HasFlag("church_before_office") && game.Room?.Name == "ChicagoMap", "Caleb warns Micah before the office");

            // ---- the alley behind the Harrington Building
            await game.Perform(Verb.Walk, "harrington");
            Check(game.Room?.Name == "HarringtonRoad", "at the Harrington Building");
            await Shot("harrington_road");
            await game.Perform(Verb.Hand, "crates");
            Check(!gs.HasFlag("crates_stacked"), "the watchman sees Micah going for the crates");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonRoad", "can't climb while watched");
            await game.Perform(Verb.UseItem, "trash_can", "matchbook");
            Check(gs.HasFlag("watchman_distracted"), "the fire sends the watchman inside");
            await Shot("harrington_road_fire");
            await game.Perform(Verb.Hand, "fire_escape");
            Check(game.Room?.Name == "HarringtonRoad", "the ladder is too high without the crates");
            await game.Perform(Verb.Hand, "crates");
            Check(gs.HasFlag("crates_stacked"), "stacked the crates");
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
            await game.Perform(Verb.Hand, "panel");
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
            var rite = game.Perform(Verb.Walk, "club");
            await Until(() => game.Room?.Name == "ClubHall");
            await WaitIdle(game);
            Check(gs.HasFlag("masked") && game.Player.Character == "micah_masked", "Micah goes in masked");
            Check(game.Room?.FindHotspot("guest")?.Visible == true, "masked guests in the hall");
            await rite;
            await Shot("club_hall_masked");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "ClubLounge", "into the lounge");
            await Shot("club_lounge");
            var stage = game.Perform(Verb.Walk, "stage_exit");
            await Until(() => game.Room?.Name == "ClubStage");
            await game.Wait(4);
            await Shot("club_stage");
            await Until(() => game.Room?.Name == "Attic");
            await game.Wait(2);
            await Shot("attic_night2");
            await Until(() => game.Hud.CaptionVisible);
            Check(game.Player.Character == "daniel" && !gs.HasItem("revolver") && gs.HasItem("journal"), "back in the attic, Micah's things put away");
            await Shot("end_of_act_two");
            await Until(() => game.Room?.Name == "Bedroom");
            Check(gs.StoryAct == 3, "Act Three");
            await game.Wait(2);
            await Shot("bedroom");
            await Until(() => game.Room?.Name == "ClubStage");
            Check(gs.HasItem("revolver") && gs.HasFlag("masked"), "back on the stage with Micah's things");
            await game.Wait(3);
            await Shot("club_stage_act3");
            await Until(() => gs.HasFlag("brute_stage"));
            await game.Wait(1);
            await Shot("club_stage_brute");
            await Until(() => game.Room?.Name == "ChurchExterior");
            await game.Wait(1.5);
            await Shot("church_exterior_beaten");
            await Until(() => game.Room?.Name == "MotelRoom");
            await stage;
            await WaitIdle(game);
            Check(gs.HasFlag("keep_going") && !gs.HasFlag("masked"), "Micah keeps going, to the motel");

            // ---- the motel, and the road out of town
            await game.Perform(Verb.Hand, "bed");
            Check(gs.HasItem("map"), "found the map");
            await Shot("motel_room");
            await game.Perform(Verb.Walk, "exit");
            Check(game.Room?.Name == "Street", "back on the street");
            await game.Perform(Verb.Walk, "church_door");
            Check(game.Room?.Name == "Street", "only the road out is left");
            await Shot("street");
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

            // ---- the other Act 3 ending: giving up, and a coffee with Rose
            game.Hud.ShowCaption(null);
            _ = game.ChangeRoom("rose_house", "coffee");
            await Until(() => game.Room?.Name == "RoseHouse");
            await Until(() => gs.HasFlag("rose_door"));
            await game.Wait(1);
            await Shot("rose_coffee");
            for (int i = 0; i < 600 && !game.Hud.CaptionVisible; i++) await game.Wait(0.1);
            Check(game.Hud.CaptionVisible, "reached 'End of Act Three' with Rose");
            await Shot("ending_rose");
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }

        GD.Print(_failures.Count == 0 ? "AUTOPLAY OK" : "AUTOPLAY FAILED:\n  " + string.Join("\n  ", _failures));
        Engine.TimeScale = 1;
        game.GetTree().Quit(_failures.Count == 0 ? 0 : 1);
    }

    public async Task RunPauseTests(Game game)
    {
        _game = game;
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
        await Shot("attic_inventory");
        Click(slot, MouseButton.Left);
        await game.Wait(0.1);
        Check(game.Carried == "crowbar" && !game.Hud.InventoryOpen, "clicking an item holds it as the cursor");
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
        await Observe(0.4 / Engine.TimeScale);
        await _game.ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var img = _game.GetViewport().GetTexture().GetImage();
        img.SavePng($"{_dir}/{++_shot:00}_{name}.png");
    }
}
