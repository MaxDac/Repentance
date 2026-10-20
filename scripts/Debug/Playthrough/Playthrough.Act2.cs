using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The canonical story's Act 2 beats: from the map to the sealed invitation in the Club vestibule.</summary>
public sealed partial class Playthrough
{
    private async Task ActTwo()
    {
        await Beat("first_interlude_aurelian", async () =>
        {
            await Pace(0.6);
            await _game.ItemVerb(Verb.Hand, "journal");
            await WaitIdle();
            Expect("EleanorRoom", "the First Interlude opens in Room 507");
            Check(Gs.HasFlag("interlude1") && _game.Player.Character == "eleanor_play", "the player is Eleanor");
            Check(_game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("eleanor_room_interlude.png") == true,
                "Room 507 is still in order the night she leaves");
            Check(Gs.HasItem("eleanor_slip") && Gs.HasItem("eleanor_key"), "Eleanor brings a blank slip and her drawer key");
            // Puzzle 17: the brass box, the flower, the riddle and the thread, packed and locked in the closet safe
            await Do(Verb.Hand, "vanity");
            Check(Gs.HasItem("eleanor_box") && Gs.HasItem("pellet"), "the open brass box and the bare paper flower");
            await Do(Verb.Hand, "desk");
            await Do(Verb.Look, "clothes");
            await Do(Verb.Hand, "clothes");
            Check(Gs.HasItem("riddle_scrap") && Gs.HasItem("red_thread"), "the riddle on stationery and the red thread");
            await Pace(0.6);
            await CombineAndWait("riddle_scrap", "pellet");
            Check(Gs.HasItem("eleanor_flower") && !Gs.HasItem("red_thread"), "the riddle tied round the flower in red");
            await Pace(0.6);
            await CombineAndWait("eleanor_flower", "eleanor_box");
            Check(Gs.HasItem("eleanor_box_packed") && Gs.HasFlag("interlude_box_packed"), "the flower in the box, the lid down");
            await Do(Verb.Hand, "closet");
            Check(Gs.HasFlag("interlude_closet_open"), "the closet opens on the safe, standing half open");
            await Do(Verb.UseItem, "interlude_safe", "eleanor_box_packed");
            Check(Gs.HasFlag("interlude_box_in_safe") && !Gs.HasFlag("interlude_safe_locked") && !Gs.HasItem("eleanor_box_packed"),
                "the box put in the safe");
            await Do(Verb.Hand, "interlude_safe");
            Check(Gs.HasFlag("interlude_safe_locked"), "the safe shut on the box");
            await Do(Verb.Hand, "closet");
            Check(!Gs.HasFlag("interlude_closet_open"), "the closet shut again");
            await Do(Verb.UseItem, "desk", "eleanor_slip");
            Check(Gs.HasItem("eleanor_riddle") && !Gs.HasItem("eleanor_slip"), "the combination written as a riddle");
            await Do(Verb.UseItem, "desk_drawer", "eleanor_riddle");
            await Do(Verb.UseItem, "desk_drawer", "eleanor_key");
            Check(Gs.HasFlag("interlude_drawer_locked") && !Gs.HasItem("eleanor_riddle"), "the riddle locked in the drawer with her key");
            await Do(Verb.Hand, "telephone");
            Check(Gs.HasFlag("interlude_phoned"), "Eleanor telephones Rizzo's");
            await Do(Verb.Walk, "exit");
            await WaitIdle();
            Expect("Speakeasy", "Sal takes her to the Blue Lantern");
        });
        await Beat("first_interlude_convent", async () =>
        {
            await Do(Verb.Talk, "bartender");
            await WaitIdle();
            Expect("ConventCorridor", "Tony sends her to the convent");
            Check(Gs.HasFlag("interlude_agatha_met"), "Agatha meets her in the corridor");
            await Do(Verb.Walk, "cell_door");
            await WaitIdle();
            Expect("ConventCell", "to her cell");
        });
        await Beat("first_interlude_night", async () =>
        {
            Check(RainsHere(), "rain on Eleanor's cell window before Agatha's visit");
            bool dried = false;
            var night = Do(Verb.Hand, "bed");
            await Until(() =>
            {
                dried |= Gs.HasFlag(Endings.RefusedAbbess) && _game.Room is Rooms.ConventCell && DryHere();
                return night.IsCompleted;
            }, 600, 0.05);
            await night;
            await WaitIdle();
            Check(Gs.HasFlag(Endings.RefusedAbbess), "Eleanor tells Agatha the truth (saved)");
            Check(dried, "the rain stops on the cell window when she tells the truth");
            Expect("MotelNight", "the next morning, the motel");
        });
        await Beat("act_two_opening", async () =>
        {
            var window = Do(Verb.Walk, "window");
            bool onFireEscape = false;
            await Until(() =>
            {
                onFireEscape |= _game.Room is Rooms.MotelFireEscape && _game.Player.PoseName == "micah_kiss";
                return _game.Room?.Name == "MotelNight" && _game.Player.Character == "micah_dressing";
            }, 600, 0.05);
            Check(onFireEscape, "after the interlude, back on the fire escape for the rest of their talk and the kiss");
            Check(!Gs.HasFlag("interlude1") && Gs.HasItem("revolver"),
                "later that night, in her motel room: Micah getting dressed, with his things");
            bool daysLater = false;
            await Until(() =>
            {
                daysLater |= _game.Hud.CaptionVisible && _game.Hud.CaptionText == Rooms.MotelNight.DaysLater;
                return window.IsCompleted && _game.Room?.Name == "MotelAlley" && !_game.Busy;
            }, 600, 0.05);
            await WaitIdle();
            Check(daysLater, "\"Days later\" on black between the motel night and the office");
            Check(Gs.HasFlag("act2_whiskey_drunk") && Gs.HasFlag("motel_return"), "the office, then back to the motel");
            Check(!Gs.HasFlag("ladder_down"), "the drop ladder is pulled up again");
            await Do(Verb.Hand, "drop_ladder");
            Expect("MotelAlley", "Micah won't go up the fire escape again");
            await Do(Verb.Walk, "street");
            Expect("MotelAlley", "not away until he knows where she went");
            await Do(Verb.Walk, "motel_door");
            Expect("MotelLobby", "in at the front, to ask the clerk");
            bool tie = false, pulled = false;
            var ask = Do(Verb.Talk, "clerk");
            await Until(() =>
            {
                tie |= _game.Player.PoseName == "micah_tie_pull";
                pulled |= _game.Room?.FindActor("clerk")?.Poses?.Action == "clerk_tie_pulled";
                return ask.IsCompleted;
            }, 600, 0.05);
            await ask;
            Check(tie && pulled, "Micah hauls the clerk across the counter by his tie");
            Check(Gs.HasFlag("motel_return_done"), "the clerk spills: two men took her");
            await Until(() => _game.Room?.Name == "ChicagoMap", 600);
            await WaitIdle();
            Check(!Story.Interlude.EleanorPlays(Gs.HasFlag) && !_game.Player.Character.StartsWith("eleanor"), "Micah's journal again");
            Check(Gs.HasItem("faith_ring") && Gs.HasFlag("caleb_met"), "whiskey, the ring and Caleb");
            Expect("ChicagoMap", "Act 2 opens on the map");
        });
        await Beat("library", async () =>
        {
            await Do(Verb.Walk, "library");
            Expect("Library", "to the library");
            var ask = Do(Verb.UseItem, "librarian", "mirror");
            await DismissImage("the librarian sees the symbol");
            await ask;
            Check(Gs.HasFlag("librarian_refused"), "the librarian won't help");
            await SolvePuzzle(() => Do(Verb.Hand, "desk"), PuzzleKind.Catalogue,
                new[] { ("motif1", 1), ("entry2", 1) }, "catalogue", submit: false);
            await Do(Verb.Hand, "librarian");
            Check(Gs.HasItem("book"), "the book, by the collar");
            Expect("ChicagoMap", "Micah walks out of the library with it");
        });
        await Beat("office_cipher", async () =>
        {
            await Do(Verb.Walk, "office");
            Expect("Office", "back at the office");
            await Pace(0.6);
            await _game.ItemVerb(Verb.Hand, "book");
            var warm = Do(Verb.UseItem, "radiator", "card");
            await DismissImage("the warmed card");
            await warm;
            await SolvePuzzle(() => CombineAndWait("mirror", "card"), PuzzleKind.Cipher,
                new[] { ("s0", 1), ("s1", 2) }, "card_cipher");
            Check(Gs.HasFlag("club_unlocked"), "the card gives the Club's address");
            await Do(Verb.Walk, "door");
            Expect("ChicagoMap", "back to the map");
        });
        await Beat("club_first_visit", async () =>
        {
            var club = Do(Verb.Walk, "club");
            await Until(() => _game.Room?.Name == "RoseHouse", 600);
            await club;
            await WaitIdle();
            Expect("RoseHouse", "thrown out of the Club, to Rose's");
            await Do(Verb.Hand, "bell");
            await WaitIdle();
            Check(Gs.HasFlag("rose_wait"), "Rose calls Micah back");
            Expect("ChicagoMap", "from Rose's door to the map");
        });
        await Beat("church_and_convent", async () =>
        {
            await Do(Verb.Walk, "church");
            Check(Gs.HasFlag("caleb_club"), "Caleb on the Club");
            await Do(Verb.Walk, "convent");
            Check(Gs.HasFlag("nun_club_asked"), "the sister knows nothing");
            var confession = await Spoken(() => Do(Verb.UseItem, "nun", "revolver"));
            await WaitIdle();
            Check(Gs.HasFlag("nun_threatened"), "the sister names Harrington");
            Check(confession.Any(l => l.Contains("I failed her")) && !confession.Any(l => l.Contains("Jezebel")),
                "told the truth, Agatha confesses she failed her and never calls her a Jezebel");
            await Do(Verb.Walk, "church");
            Check(Gs.HasFlag("church_before_office"), "Caleb's warning");
            Expect("ChicagoMap", "back to the map");
        });
        await Beat("tribune_morgue", async () =>
        {
            await Do(Verb.Walk, "tribune");
            await WaitIdle();
            Expect("NewspaperMorgue", "down in the Tribune morgue");
            await Do(Verb.Hand, "drawer_h");
            await Do(Verb.Hand, "spike");
            await Do(Verb.Hand, "paste_pot");
            await CombineAndWait("clipping_top", "clipping_bottom");
            Check(Gs.HasFlag("harrington_located"), "the Harrington Building located");
            await Do(Verb.Walk, "door");
            Expect("ChicagoMap", "back to the map");
        });
        await Beat("harrington_road", async () =>
        {
            await Do(Verb.Walk, "harrington");
            Expect("HarringtonRoad", "at the Harrington Building");
            await Do(Verb.UseItem, "trash_can", MicahKit.LighterId);
            await Do(Verb.Hand, "crates");
            await Do(Verb.Hand, "packing_wedge");
            await Do(Verb.UseItem, "ladder_catch", "wedge");
            await Do(Verb.Hand, "fire_escape");
            await WaitIdle();
            Expect("HarringtonOffice", "up the fire escape");
        });
        await Beat("harrington_office", async () =>
        {
            await Do(Verb.Hand, "drawer_left");
            await Do(Verb.UseItem, "drawer_right", "lockpick");
            await Do(Verb.Hand, "closet");
            await Do(Verb.Look, "portrait");
            await WaitIdle();
            await SolvePuzzle(() => Do(Verb.Hand, "panel"), PuzzleKind.Crests,
                new[] { ("s0", 2), ("s2", 1) }, "crest_lock");
            await Do(Verb.Hand, "niche");
            Check(Gs.HasItem("mask") && Gs.HasItem("cloak") && Gs.HasItem("invitation"), "mask, cloak and invitation");
            await Do(Verb.Walk, "window");
            Expect("ChicagoMap", "out of the window");
            await Do(Verb.Walk, "church");
            Check(Gs.HasFlag("church_before_club"), "Caleb's last warning");
        });
        await Beat("club_vestibule", async () =>
        {
            await Do(Verb.Walk, "club");
            await WaitIdle();
            Expect("ClubVestibule", "masked, into the Club vestibule");
            await Do(Verb.Hand, "sealing_wax");
            await CombineAndWait(MicahKit.LighterId, "sealing_wax");
            await CombineAndWait("wax_soft", "invitation");
            await Do(Verb.Hand, "cloak_raven");
            await CombineAndWait("signet_raven", "invitation_waxed");
            Check(Gs.HasItem("sealed_invitation"), "the invitation sealed with the raven");
        });
    }
}
