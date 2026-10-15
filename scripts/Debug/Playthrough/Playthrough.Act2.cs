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
        await Beat("act_two_opening", async () =>
        {
            await Pace(0.6);
            await _game.ItemVerb(Verb.Hand, "journal");
            await WaitIdle();
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
            await Do(Verb.UseItem, "wall_map", "clipping");
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
