using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The canonical story's Act 3 beats, branching on the ending route.</summary>
public sealed partial class Playthrough
{
    private async Task ActThree()
    {
        bool over = false;
        await Beat("club_stage", async () =>
        {
            var rite = Do(Verb.UseItem, "slot", "sealed_invitation");
            await Until(() => _game.Room?.Name == "ClubHall", 300);
            await rite;
            await WaitIdle();
            await Do(Verb.Walk, "exit");
            Expect("ClubLounge", "into the lounge");
            var stage = Do(Verb.Walk, "stage_exit");
            if (_route == "1-steps")
            {
                await Until(() => _game.Room?.Name == "RoseHouse", 900);
                Check(Gs.HasFlag(Endings.GaveUpSteps), "gave up on the church steps");
                await TheEnd();
                over = true;
                return;
            }
            await stage;
            await WaitIdle();
            Check(Gs.StoryAct == 3 && Gs.HasFlag("keep_going"), "Act 3: Micah keeps going");
            Expect("Office", "Act 3 opens at Micah's desk");
        }, roundTrip: _route != "1-steps");
        if (over) return;
        await Beat("act_three_office", async () =>
        {
            await Do(Verb.Walk, "door");
            Check(Gs.HasItem("cross") && Gs.HasFlag("church_act3_return"), "Caleb's cross");
            Expect("Office", "back from the church");
            await Do(Verb.Walk, "door");
            Expect("Alley", "to the Blue Lantern's alley");
        });
        await Beat("alley_act_three", async () =>
        {
            await Do(Verb.Kick, "street_lamp");
            await Do(Verb.Kick, "trash");
            await Do(Verb.UseItem, "sal", "revolver");
            Check(Gs.HasFlag("alley3_sal_down"), "Sal knocked down");
            var tony = Do(Verb.Talk, "back_door");
            if (_route == "1")
            {
                await Until(() => _game.Room?.Name == "RoseHouse", 300);
                Check(Gs.HasFlag(Endings.WalkedAway), "walked away from Tony");
                await TheEnd();
                over = true;
                return;
            }
            await tony;
            await WaitIdle();
            Check(Gs.HasFlag("shot_bartender"), "Tony shot in the shoulder");
            Expect("MansionExterior", "Tony gives up the mansion");
        }, roundTrip: _route != "1");
        if (over) return;
        await Beat("mansion_exterior", async () =>
        {
            await Do(Verb.Look, "door");
            await Do(Verb.Hand, "lintel");
            await Do(Verb.Hand, "bin");
            await SolvePuzzle(() => Do(Verb.Hand, "bell"), PuzzleKind.Bell, new[] { ("s1", 1), ("s2", 2) }, "alarm_restraint");
            await Do(Verb.Hand, "door");
            Expect("MansionKitchen", "in through the kitchen");
        });
        await Beat("mansion_cellar", async () =>
        {
            await Do(Verb.Walk, "cellar_door");
            Expect("MansionCellar", "down to the cellar");
            await Do(Verb.Hand, "lantern");
            await Do(Verb.Hand, "crates");
            await CombineAndWait("lantern", "kerosene");
            await CombineAndWait("lantern_filled", MicahKit.LighterId);
            await Do(Verb.UseItem, "stair", "lantern_lit");
            await Do(Verb.Walk, "stair");
            Expect("MansionStudy", "up the bootleggers' stair");
        });
        bool free = _route is "2" or "3";
        await Beat("mansion_study", async () =>
        {
            if (free)
            {
                await Do(Verb.Hand, "drawer_right");
                await Do(Verb.Hand, "documents");
                await Do(Verb.Hand, "drawer_left");
                await SolvePuzzle(() => CombineAndWait("audit_folder", "audit_tracing"), PuzzleKind.Alignment,
                    new[] { ("rotate", 1), ("right", 6), ("down", 3) }, "audit_alignment");
                Check(Gs.HasFlag(Endings.TookDocuments), "the signed payoff sheets");
            }
            var confront = Do(Verb.Walk, "door_right");
            if (_route == "1-oldman")
            {
                await Until(() => _game.Room?.Name == "RoseHouse", 300);
                Check(Gs.HasFlag(Endings.SparedOldMan), "spared the old man");
                await TheEnd();
                over = true;
                return;
            }
            if (_route is "6" or "7")
            {
                if (_route == "6")
                {
                    await Until(() => _game.Room?.Name == "Prison", 300);
                    Expect("Prison", "Micah turns himself in");
                }
                await TheEnd();
                Check(Gs.HasFlag("shot_oldman"), "Harrington shot");
                Check(Gs.HasFlag(_route == "6" ? Endings.Repented : Endings.ShotEleanor),
                    _route == "6" ? "Micah repents" : "Micah shoots Eleanor");
                over = true;
                return;
            }
            await confront;
            await WaitIdle();
            Check(Gs.HasFlag("shot_oldman"), "Harrington shot");
            Check(Gs.HasFlag(Endings.EleanorConvinced) == (_route is "2" or "4"), "Eleanor's answer follows the route");
            Expect("MansionKitchen", "the escape through the kitchen");
        }, roundTrip: false);
        if (over) return;
        await Beat("mansion_escape", async () =>
        {
            if (free)
            {
                await Do(Verb.Walk, "cellar_door");
                Expect("MansionCellar", "back down to the cellar, Eleanor waiting in the kitchen");
                await Do(Verb.Hand, "barrel");
                await Do(Verb.Hand, "hung_lantern");
                await Do(Verb.UseItem, "barrel", "lantern_lit");
                Expect("MansionKitchen", "up out of the burning cellar");
                Check(Gs.HasFlag("cellar_fire"), "the whiskey is alight");
            }
            _ = Do(Verb.Walk, "back_door");
            string room = free ? "Outskirts" : "Prison";
            await Until(() => _game.Room?.Name == "Outskirts" || _game.Room?.Name == "Prison", 300);
            Expect(room, free ? "out of town" : "prison");
            Check(Gs.HasFlag(Endings.MansionExploded) == free, "the house burns only after the cellar fire");
            await TheEnd();
        }, roundTrip: false);
    }
}
