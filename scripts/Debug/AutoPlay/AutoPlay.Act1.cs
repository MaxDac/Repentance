using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The prologue and Act 1 of the autoplay run.</summary>
public partial class AutoPlay
{
    /// <summary>The present-day attic prologue, played through the real mouse input where it matters.</summary>
    private async Task PlayPrologue(Game game, GameState gs, bool autosave)
    {
        // ---- prologue: the attic, played through the real mouse input where it matters
        await TitleMenuTest(game, expectSaves: false);
        game.AutosaveEnabled = autosave;
        await game.ChangeRoom("attic", "start");
        await PauseTest(game);
        Check(game.Player.Character == "daniel" && !gs.HasItem(Notes.ItemId) && !gs.HasItem(MicahKit.LighterId), "prologue plays as Daniel, without Micah's notepad or lighter");
        await Shot("attic");
        Check(game.Sfx.Ambient == null, "no rain sounds in the dry attic");
        Check(game.Music.Current == null, "no music in the attic");
        int woodSteps = game.Sfx.Count(Sound.StepWood);
        await WheelTest(game);
        await PuzzleGestureTest(game);
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
    }

    /// <summary>Act 1 in 1927: the office, the hotel, the Blue Lantern and the convent.</summary>
    private async Task PlayActOne(Game game, GameState gs)
    {
        // ---- 1927
        Check(game.Room?.Name == "Office", "journal leads to the office");
        Check(game.Music.Current == Track.OfficeJazz, "soft jazz plays in the office");
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
        Check(!gs.HasFlag("drawer_open"), "Micah shuts the top drawer once it's empty");
        await game.Perform(Verb.Hand, "drawer");
        Check(!gs.HasFlag("drawer_open"), "the empty top drawer stays shut");
        await NotepadTest(game);
        await MouseTest(game);
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "Lobby", "entered the lobby");

        await Shot("lobby");
        await game.Perform(Verb.Talk, "concierge");
        await game.Perform(Verb.Walk, "revolving_door");
        Check(game.Room is Rooms.Lobby, "the revolving door holds Micah in the lobby before the bellboy's tip");
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
        Check(game.Sfx.Ambient == Sound.Rain, "rain patters on Eleanor's window");
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
        Check(!gs.HasItem("bluing") && gs.HasItem("brass_box") && !gs.HasFlag("opened_brass_box"),
            "the florist's shelf has no bluing: the carnation can't be dyed until the brass box is opened");
        await game.ItemVerb(Verb.Hand, "brass_box");
        Check(!gs.HasItem("brass_box") && gs.HasItem("card") && gs.HasItem("matchbook") && gs.HasItem("bluing") &&
            gs.HasItem("water_flower") && gs.HasFlag("opened_brass_box"),
            "the brass box holds a card, the matchbook, Eleanor's bluing and her water flower");
        await game.Perform(Verb.UseItem, "chalkboard", "water_flower");
        Check(gs.HasItem("water_flower") && !gs.HasFlag("knows_password"), "the water flower only talks in water");
        await Shot("blue_lantern_front_taken");
        await CombineAndWait("carnation", "bluing");
        Check(gs.HasItem("blue_carnation") && !gs.HasItem("carnation") && !gs.HasItem("bluing") && gs.HasFlag("made_blue_carnation"),
            "dyed the carnation blue with Eleanor's bluing");
        await game.Perform(Verb.UseItem, "grille", "blue_carnation");
        Check(game.Room?.Name == "Speakeasy", "the grille opens for a blue carnation");
        Check(gs.HasFlag("grille_opened") && !gs.HasItem("blue_carnation") && !gs.HasFlag("sal_passed"),
            "past the florist's grille, but Sal is still to come");

        await Shot("speakeasy");
        Vector2? salWhenPassed = null;
        void OnSalPassed()
        {
            if (salWhenPassed == null && gs.HasFlag("sal_passed")) salWhenPassed = game.Room?.FindActor("sal")?.Position;
        }
        gs.Changed += OnSalPassed;
        await game.Perform(Verb.Talk, "bartender");
        await Until(() => !game.Busy);
        gs.Changed -= OnSalPassed;
        Check(salWhenPassed is { } p && p.DistanceTo(Rooms.Speakeasy.SalAside) > 4 &&
            game.Room?.FindActor("sal")?.Position.DistanceTo(Rooms.Speakeasy.SalAside) < 0.5f,
            $"Sal walks aside after the bribe instead of jumping there (at {salWhenPassed} when paid)");
        Check(game.Room?.Name == "Speakeasy" && _offered.Keys.Any(k => k.StartsWith("sal")),
            "walking past Sal makes him step in and start the talk");
        Check(gs.HasFlag("sal_passed") && gs.HasFlag("sal_bribed") && !gs.HasFlag("sal_password") &&
              !gs.HasFlag("thrown_out") && !gs.HasFlag("photo_shown"),
            "no password, but Sal takes the bribe before Micah reaches the bar");
        await game.Perform(Verb.Talk, "sal");
        Check(game.Room?.Name == "Speakeasy" && gs.HasFlag("sal_passed"), "talking to Sal directly still works once inside");
        Check(CashRules.Balance(gs.HasFlag) == 10 && gs.HasItem("dollar"), "Sal costs ten dollars and leaves ten");
        await Shot("speakeasy_inside");
        int barOffers = _offerLog.Count;
        var bar = game.Perform(Verb.Talk, "bartender");
        await Until(() => gs.HasFlag("lantern_gin_held"));
        Check(gs.HasFlag("lantern_gin_paid") && gs.HasFlag("lantern_gin_poured") && !gs.HasFlag("lantern_gin") &&
            CashRules.Balance(gs.HasFlag) == 9, "Tony pours the bathtub gin for a buck, leaving nine");
        Check(game.Room?.FindChild("Gin", true, false) is CanvasItem { Visible: false } &&
            game.Room?.FindChild("GinEmpty", true, false) is CanvasItem { Visible: false },
            "the glass leaves the counter while Micah holds it");
        await Until(() => game.Player.PoseName == "micah_gin");
        await game.Wait(0.7);
        await Shot("speakeasy_gin");
        await Until(() => gs.HasFlag("lantern_gin"));
        Check(_poseCounts.GetValueOrDefault("micah_gin") == 1 && game.Player.PoseName == null &&
            !gs.HasFlag("lantern_gin_held"), "Micah knocks the gin back and stands normally again");
        Check(game.Room?.FindChild("GinEmpty", true, false) is CanvasItem { Visible: true } &&
            game.Room?.FindChild("Gin", true, false) is CanvasItem { Visible: false },
            "the empty glass goes back on the counter");
        var barLog = _offerLog.Skip(barOffers).Where(o => o.Knot == "bartender").ToList();
        int ginAt = barLog.FindIndex(o => o.Options.Any(l => l.StartsWith("Bathtub?")));
        Check(barLog.Count > 0 && ginAt > 0 && barLog[ginAt - 1].Options[0] == "What've you got?" &&
            !barLog[0].Options.Any(l => l.StartsWith("Bathtub?")),
            "the gin is offered only after Tony names the bathtub gin");
        await Until(() => game.Room?.Name == "Alley");
        Check(_offerLog.Skip(barOffers).Where(o => o.Knot == "bartender").Count(o => o.Options.Any(l => l.StartsWith("Bathtub?"))) == 1 &&
            CashRules.Balance(gs.HasFlag) == 9, "one gin, charged once");
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
        Check(game.Room?.FindActor("eleanor") == null && !game.Hud.InsetVisible,
            "Eleanor and the close-up are absent on arrival");
        await Until(() => !game.Busy && gs.HasFlag("seen_convent_exterior"));
        Check(game.Room is Rooms.ConventRoad && !gs.HasFlag("nun_talked") && !gs.HasFlag("eleanor_found"),
            "arrival waits outside for the player to open the convent door");
        Check(game.Music.Current == null, "no piano outside the convent");
        await Shot("convent_arrival");
        await ReloadCheckpoint("convent_arrival");
        Check(gs.HasFlag("seen_convent_exterior") && game.Room?.FindActor("eleanor") == null &&
            !game.Hud.SpeechVisible && !gs.HasFlag("convent_departed"),
            "loading the exterior retains the arrival phase without repeating the remark");
        Click(game.Room!.FindHotspot("door")!.Bounds.GetCenter(), MouseButton.Left);
        await Until(() => game.Room is Rooms.ConventCorridor && gs.HasFlag("nun_talked") && !game.Busy);
        Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_talked"), "the nun questions Micah in the corridor");
        Check(game.Music.Current == Track.ConventPiano, "the piano plays in the convent corridor");
        int pianoStarts = game.Music.Count(Track.ConventPiano);
        await game.Perform(Verb.Walk, "entrance");
        Check(game.Room is Rooms.ConventCorridor && !gs.HasFlag("convent_departed"),
            "Micah must search the cell before leaving the convent");
        await Shot("convent_corridor");
        await game.Perform(Verb.Walk, "cell_door");
        Check(game.Room?.Name == "ConventCell", "entered Eleanor's cell");
        Check(game.Room?.FindActor("nun") is { Visible: false }, "nobody but Micah in Eleanor's cell");
        Check(game.Music.Current == Track.ConventPiano && game.Music.Count(Track.ConventPiano) == pianoStarts,
            "the piano carries on into the cell without restarting");
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
        Check(gs.HasItem("mirror") && !gs.HasItem("comb") && gs.HasItem("cloth"), "revealed mirror retained; comb left in cell; Micah keeps her cloth");
        var searchBedAfterCleaning = game.Perform(Verb.Hand, "bed");
        await Until(() => game.Hud.SpeechVisible);
        Check(game.Hud.SpeechText == "Thin mattress. Her rag oughta be lying here. It's in my pocket instead.",
            "bed search after cleaning admits the cloth wasn't returned");
        await searchBedAfterCleaning;
        Check(gs.Inventory.Count(i => i == "cloth") == 1, "bed search after cleaning does not borrow another cloth");
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
        Check(game.Room?.FindActor("eleanor") == null, "nobody is waiting on the road");
        await Until(() => game.Player.PoseName == "micah_smoke" || game.Room is not Rooms.ConventRoad);
        Check(game.Room is Rooms.ConventRoad && game.Player.PoseName == "micah_smoke", "Micah lights a cigarette in the road");
        await Until(() => game.Hud.InsetVisible || game.Room is not Rooms.ConventRoad);
        Check(game.Hud.CurrentCloseUp == CloseUps.Motel && game.Hud.InsetName == "motel_closeup",
            "the motel sign close-up appears when Micah spots it");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("long shot"));
        Check(game.Hud.InsetVisible && game.Hud.CurrentCloseUp == CloseUps.Motel,
            "the close-up stays up while Micah talks himself into the long shot");
        await Shot("motel_closeup");
        Check(_offered.TryGetValue("convent_dead_end", out var deadEnd) && deadEnd.Length == 1 && deadEnd[0].Contains("office"),
            "the mob, Harrington and the cops are refused before the office");
        await Until(() => game.Room is Rooms.MotelAlley && !game.Busy);
        Check(gs.HasFlag("convent_dead_end_done") && gs.HasFlag("seen_motel_alley") && !gs.HasFlag("eleanor_found") &&
            !game.Hud.InsetVisible && game.Player.PoseName == null, "down the hill to the motel's back alley");
        await Shot("motel_alley");
        await ReloadCheckpoint("motel_alley");
        Check(game.Room is Rooms.MotelAlley && !game.Hud.SpeechVisible, "loading the alley does not replay the dead end");

        await game.Perform(Verb.UseItem, "drop_ladder", "dollar");
        await game.Perform(Verb.Hand, "drop_ladder");
        Check(!gs.HasFlag("ladder_down"), "the drop ladder is out of reach from the ground");
        await game.Perform(Verb.Walk, "motel_door");
        await Until(() => game.Room is Rooms.MotelLobby && !game.Busy);
        Check(game.Room?.FindActor("clerk")?.Visible == true, "the night clerk behind the counter");
        await Shot("motel_lobby");
        await game.Perform(Verb.Hand, "umbrella");
        Check(!gs.HasItem("umbrella"), "Micah won't take the clerk's umbrella before talking to him");
        await game.Perform(Verb.Walk, "stairs");
        Check(game.Room is Rooms.MotelLobby, "the clerk keeps Micah off the stairs");
        await game.Perform(Verb.Talk, "clerk");
        Check(gs.HasFlag("clerk_talked") && game.Room is Rooms.MotelLobby, "the clerk refuses to let Micah upstairs");
        await game.Perform(Verb.Hand, "umbrella");
        Check(gs.HasItem("umbrella") && gs.HasFlag("took_umbrella") && game.Room?.FindHotspot("umbrella")?.Active != true,
            "the clerk lets Micah take his umbrella");
        await game.Perform(Verb.Walk, "door");
        await Until(() => game.Room is Rooms.MotelAlley && !game.Busy);
        await game.Perform(Verb.UseItem, "drop_ladder", "umbrella");
        Check(!gs.HasFlag("ladder_down") && gs.HasItem("umbrella"), "even the umbrella can't reach the ladder from the ground");
        await game.Perform(Verb.Hand, "crate");
        Check(gs.HasFlag("crate_moved") && game.Room?.FindHotspot("crate_under")?.Active == true &&
            game.Room?.FindHotspot("crate")?.Active != true, "the crate is pushed under the fire escape");
        await game.Perform(Verb.UseItem, "drop_ladder", "umbrella");
        Check(gs.HasFlag("ladder_down") && !gs.HasItem("umbrella") && game.Room?.FindHotspot("ladder")?.Active == true,
            "the umbrella hooks the drop ladder down");
        await Shot("motel_alley_ladder");
        var climb = game.Perform(Verb.Hand, "ladder");
        await Until(() => game.Room is Rooms.MotelFireEscape);
        Check(game.Room?.FindActor("eleanor")?.Visible == true, "Eleanor is waiting on the fire escape");
        Check(!game.Hud.InsetVisible, "no close-up while Micah walks up to her");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
            "Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?");
        Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn && game.Hud.SpeechText ==
            "Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?",
            "Eleanor's opening is spoken on the fire escape before the close-up");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Convent && game.Hud.InsetName == "convent_closeup",
            "the two-portrait close-up appears immediately after Eleanor's opening");
        Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "the two-portrait close-up fills most of the screen");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Eleanor Harrington. You wouldn't happen to know her?");
        CheckPortraitSpeech(game, right: false);
        await Shot("convent_portrait_micah");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Tony's boys"));
        CheckPortraitSpeech(game, right: true);
        await Shot("convent_portrait_eleanor");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Twenty a day. I used to spend that on gloves.");
        Check(game.Hud.SpeechText == "Twenty a day. I used to spend that on gloves." && !game.Hud.InsetDrawn,
            "the compensation answer rejoins the existing conversation on the fire escape");
        Check(_closeUpAtRoadChoice == null, "Micah answers the compensation choice without a portrait panel");
        await Shot("motel_fire_escape");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("can't go back"));
        Check(game.Hud.CurrentCloseUp == null && !game.Hud.InsetDrawn && game.Room is Rooms.MotelFireEscape,
            "the rest of Eleanor's conversation stays on the fire escape without the panel");
        await Until(() => game.Room?.Name == "MotelNight");
        Check(game.Player.Character == "micah_dressing", "Micah getting dressed in the motel");
        await game.Wait(2);
        await Shot("motel_night");
        await Until(() => game.Room?.Name == "Attic");
        await game.Wait(2.5);
        await Shot("attic_night");
        await leave;
        await climb;
    }
}
