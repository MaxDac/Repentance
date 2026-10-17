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
            await Do(Verb.UseItem, "closet", "eleanor_box_packed");
            Check(Gs.HasFlag("interlude_safe_locked") && !Gs.HasItem("eleanor_box_packed"), "the box locked in the closet safe");
            await Do(Verb.Hand, "desk_drawer");
            await Do(Verb.Hand, "bed");
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
            Check(Gs.HasFlag(Endings.RefusedAbbess), "Eleanor refuses Agatha (saved)");
            Check(dried, "the rain stops on the cell window when she refuses");
            Expect("MotelNight", "the next morning, the motel");
        });
        await Beat("act_two_opening", async () =>
        {
            var window = Do(Verb.Walk, "window");
            await Until(() => _game.Room?.Name == "MotelNight" && _game.Player.Character == "micah_dressing", 600);
            Check(!Gs.HasFlag("interlude1") && Gs.HasItem("revolver"),
                "after the interlude, the night in her motel room: Micah getting dressed, with his things");
            await window;
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
            await Do(Verb.UseItem, "librarian", "revolver");
            Check(Gs.HasItem("book"), "the book at gunpoint");
            await Do(Verb.Walk, "exit");
            Expect("ChicagoMap", "out of the library");
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
            await Do(Verb.UseItem, "nun", "revolver");
            await WaitIdle();
            Check(Gs.HasFlag("nun_threatened"), "the sister names Harrington");
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
