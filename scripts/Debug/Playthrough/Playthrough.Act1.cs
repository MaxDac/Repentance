using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The canonical story's Act 1 beats: from the attic to the end of Act One.</summary>
public sealed partial class Playthrough
{
    private async Task ActOne()
    {
        await Beat("attic", async () =>
        {
            Expect("Attic", "the story opens in the attic");
            await Do(Verb.Talk, "hatch");
            await Do(Verb.Hand, "sheet");
            await Do(Verb.Hand, "boxes");
            await Do(Verb.Hand, "suitcase");
            await Do(Verb.Hand, "boxes");
            await Do(Verb.UseItem, "tool_tin", "suitcase_key");
            Check(Gs.HasItem("crowbar"), "the attic: the crowbar from the tool tin");
            await Do(Verb.UseItem, "trunk", "crowbar");
            Check(Gs.HasFlag("trunk_open") && Gs.HasItem("journal"), "the crowbar opens the trunk on Micah's journal");
            await Pace(0.6);
            _ = _game.ItemVerb(Verb.Hand, "journal");
            await Until(() => _game.Room?.Name == "Office" && Gs.HasFlag("teddy_gone") && !_game.Busy, 600);
            Expect("Office", "the journal leads to 1927");
        });
        await Beat("office", async () =>
        {
            await Do(Verb.Hand, "drawer");
            await Do(Verb.Hand, "revolver");
            await Do(Verb.Hand, "dollar");
            await Do(Verb.Hand, "lockpick");
            await Do(Verb.Walk, "door");
            Expect("Lobby", "out of the office");
        });
        await Beat("lobby", async () =>
        {
            await Do(Verb.Talk, "concierge");
            await Do(Verb.Talk, "bellboy");
            await Do(Verb.UseItem, "bellboy", "dollar");
            await Do(Verb.UseItem, "bellboy", "dollar");
            Check(Gs.HasFlag("knows_lantern") && Gs.HasFlag("staff_elevator"), "the bellboy: the Blue Lantern and the staff lift");
            await SolvePuzzle(() => Do(Verb.Walk, "service_door"), PuzzleKind.Lift, LiftRoute(), "lift_route");
            Expect("HotelLinen", "up the service lift");
        });
        await Beat("linen_room", async () =>
        {
            await Do(Verb.Hand, "rack");
            await Do(Verb.Hand, "cart");
            await CombineAndWait("hanger", "pliers");
            await Do(Verb.UseItem, "corridor_door", "wire_hook");
            Expect("EleanorRoom", "the wire hook opens the corridor door");
        });
        await Beat("eleanor_room", async () =>
        {
            await Do(Verb.UseItem, "desk_drawer", "lockpick");
            await Do(Verb.Hand, "paper");
            await Do(Verb.Hand, "closet");
            await SolvePuzzle(() => Do(Verb.UseItem, "safe", "combination"), PuzzleKind.Safe,
                new[] { ("t0", 1), ("n0", 2), ("d1", 1), ("t1", 3), ("n1", 1), ("n2", 7) }, "safe_dial");
            await Do(Verb.Hand, "brass_box");
            Check(Gs.HasItem("brass_box"), "the brass box from the safe");
            await Do(Verb.Walk, "exit");
            await Do(Verb.Walk, "lift");
            Expect("Lobby", "back down to the lobby");
        });
        await Beat("blue_lantern_front", async () =>
        {
            await Do(Verb.Walk, "revolving_door");
            Expect("BlueLanternFront", "the revolving door leads to Rizzo's Flowers");
            await Do(Verb.Hand, "bucket");
            await Pace(0.6);
            await _game.ItemVerb(Verb.Hand, "brass_box");
            await CombineAndWait("carnation", "bluing");
            await Do(Verb.UseItem, "bucket", "water_flower");
            Check(Gs.HasFlag("knows_password") && !Gs.HasItem("water_flower"), "Eleanor's water flower blooms with the password");
            await Do(Verb.UseItem, "grille", "blue_carnation");
            Expect("Speakeasy", "the blue carnation opens the grille");
        });
        await Beat("speakeasy", async () =>
        {
            await Do(Verb.Talk, "sal");
            Check(Gs.HasFlag("sal_passed") && Gs.HasFlag("sal_password") && CashRules.Balance(Gs.HasFlag) == 20,
                "Moonshine gets Micah past Sal without paying");
            await Do(Verb.Talk, "bartender");
            await WaitIdle();
            Check(Gs.HasFlag("lantern_gin") && CashRules.Balance(Gs.HasFlag) == 19,
                "Micah knocks back a buck's worth of bathtub gin");
            Expect("Alley", "thrown out into the alley");
        });
        await Beat("convent_road", async () =>
        {
            await Do(Verb.Walk, "street");
            await Until(() => _game.Room is Rooms.ConventRoad && !_game.Busy && Gs.HasFlag("seen_convent_exterior"));
            Expect("ConventRoad", "from the alley to the convent");
        });
        await Beat("convent", async () =>
        {
            _ = Do(Verb.Walk, "door");
            await Until(() => _game.Room is Rooms.ConventCorridor && Gs.HasFlag("nun_talked") && !_game.Busy);
            await Do(Verb.Walk, "cell_door");
            Expect("ConventCell", "into Eleanor's cell");
            await Do(Verb.Hand, "nightstand");
            await Do(Verb.Hand, "mirror");
            await Do(Verb.Hand, "bed");
            await Do(Verb.UseItem, "lampstand", "mirror_waxed");
            await Combine("cloth", "mirror_waxed");
            await DismissImage("the symbol behind the mirror");
            await WaitIdle();
            await Do(Verb.Hand, "comb");
            Check(Gs.HasItem("mirror") && Gs.HasItem("cloth"), "the cleaned mirror, and Micah keeps her cloth");
            await Do(Verb.Walk, "exit");
            Expect("ConventCorridor", "back to the corridor");
        });
        await Beat("convent_dead_end", async () =>
        {
            await Do(Verb.Walk, "entrance");
            await Until(() => _game.Room is Rooms.MotelAlley && !_game.Busy && Gs.HasFlag("seen_motel_alley"));
            Check(Gs.HasFlag("convent_dead_end_done") && !Gs.HasFlag("eleanor_found"),
                "the farewell, an empty road, a dead end, and the motel sign down the hill");
            Expect("MotelAlley", "down the hill to the motel's back alley");
        });
        await Beat("motel", async () =>
        {
            await Do(Verb.Hand, "drop_ladder");
            await Do(Verb.Walk, "motel_door");
            Expect("MotelLobby", "in at the motel's front door");
            await Do(Verb.Talk, "clerk");
            Check(Gs.HasFlag("clerk_talked"), "the clerk won't let Micah upstairs");
            await Do(Verb.Hand, "umbrella");
            Check(Gs.HasItem("umbrella"), "the clerk hands over his umbrella to see Micah gone");
            await Do(Verb.Walk, "door");
            Expect("MotelAlley", "back out to the alley");
            await Do(Verb.Hand, "crate");
            await Do(Verb.UseItem, "drop_ladder", "umbrella");
            Check(Gs.HasFlag("ladder_down") && !Gs.HasItem("umbrella"), "the umbrella hooks the drop ladder down");
        });
        await Beat("end_of_act_one", async () =>
        {
            await Do(Verb.Hand, "ladder");
            await WaitIdle();
            Check(Gs.StoryAct == 2 && _game.Room?.Name == "Attic", "up the fire escape to Eleanor, the motel, and back to the attic in Act 2");
        });
    }
}
