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
            _ = Do(Verb.Walk, "stage_exit");
            await Until(() => _game.Room?.Name == "MotelNight", 900);
            await WaitIdle();
            Expect("MotelNight", "the Second Interlude opens in the motel");
            Check(Gs.StoryAct == 3 && Gs.HasFlag("interlude2") && _game.Player.Character == "eleanor_play", "Act 3: the player is Eleanor");
        });
        await Beat("second_interlude_taken", async () =>
        {
            await Do(Verb.Hand, "door");
            await WaitIdle();
            Expect("ClubBackstage", "the Order's men take her to the Club's dressing room");
            Check(_game.Player.Character == "eleanor_gown_play", "Eleanor in the pink gown");
            // Puzzle 18: the face they paid for, before the old man will talk
            await Do(Verb.Hand, "mirror");
            Check(Gs.HasItem("compact") && Gs.HasItem("lipstick"), "her compact and lipstick from the ledge");
            await Do(Verb.Look, "rack");
            await Do(Verb.Hand, "rack");
            await Do(Verb.Hand, "screens");
            Check(Gs.HasItem("puff") && Gs.HasItem("hairpin"), "a puff from a gown pocket, a pin from the screen");
            await Pace(0.6);
            await CombineAndWait("puff", "compact");
            Check(Gs.HasItem("puff_powdered"), "the puff in the face powder");
            await Do(Verb.UseItem, "mirror", "puff_powdered");
            await Do(Verb.UseItem, "mirror", "lipstick");
            await Do(Verb.UseItem, "mirror", "hairpin");
            Check(Gs.HasFlag("interlude_made_up") && !new[] { "compact", "lipstick", "hairpin", "puff_powdered" }.Any(Gs.HasItem),
                "powder, mouth and hair: the face is on");
        });
        await Beat("second_interlude_oldman", async () =>
        {
            var oldman = Do(Verb.Talk, "harrington");
            if (_route == "1-steps")
            {
                await Until(() => _game.Room?.Name == "RoseHouse", 900);
                Check(Gs.HasFlag(Endings.GaveUpSteps), "gave up on the church steps");
                await TheEnd();
                over = true;
                return;
            }
            await oldman;
            await WaitIdle();
            Check(Gs.HasFlag(Endings.RefusedDrugs) == EleanorRoute, "Eleanor's answer to the old man follows the route");
            Check(Gs.HasFlag("keep_going") && !Gs.HasFlag("interlude2"), "Micah keeps going");
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
            Expect("OfficeStorm", "back to the office, in the storm");
        }, roundTrip: _route != "1");
        if (over) return;
        await Beat("office_storm", async () =>
        {
            Check(Gs.HasFlag("storm_confessed"), "the journal's confession at the window");
            await Do(Verb.Walk, "door");
            Expect("OfficeStorm", "not out without the hat");
            await Do(Verb.Hand, "hat");
            Check(Gs.HasFlag("storm_bottle_down") && Gs.HasFlag("storm_hat_on"), "bottle down, hat on");
            await Do(Verb.Walk, "door");
            Expect("MansionExterior", "Tony gives up the mansion");
        });
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
        bool free = _route is "2" or "3" or "10";
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
                string flag = _route == "6" ? Endings.Repented : Endings.ShotEleanor;
                Check(Gs.HasFlag(flag), $"route {_route}: {flag}");
                over = true;
                return;
            }
            if (_route is "8" or "9")
            {
                await confront;
                await WaitIdle();
                Expect("MansionBedroom", "after the prayer, the player is Eleanor");
                Check(Gs.HasFlag("eleanor_coda") && _game.Player.Character == "eleanor_sheet_play", "Eleanor in the sheet");
                return;
            }
            await confront;
            await WaitIdle();
            Check(Gs.HasFlag("shot_oldman"), "Harrington shot");
            Check(Gs.HasFlag(Endings.EleanorConvinced) == (_route is "2" or "4"), "Eleanor's answer follows the route");
            Check(Gs.HasFlag(Endings.EleanorWeary) == (_route is "10" or "11"), "worn out, Eleanor follows without persuasion only on her routes");
            Check(Endings.EleanorFollows(Gs.HasFlag) == (_route is "2" or "4" or "10" or "11"), "Eleanor comes to the kitchen only when she follows");
            Expect("MansionKitchen", "the escape through the kitchen");
        }, roundTrip: _route is "2" or "3" or "4" or "5" or "8" or "9" or "10" or "11");
        if (over) return;
        if (_route is "8" or "9")
        {
            await EleanorCoda();
            return;
        }
        if (free)
        {
            await Beat("mansion_escape_cellar", async () =>
            {
                await Do(Verb.Walk, "cellar_door");
                Expect("MansionCellar", "back down to the cellar, Eleanor waiting in the kitchen");
                await Do(Verb.Hand, "barrel");
                await Do(Verb.Hand, "hung_lantern");
                Check(Gs.HasFlag("barrel_open") && Gs.HasItem("lantern_lit"), "the whiskey running, the lantern off its nail");
            });
            await Beat("mansion_escape_fire", async () =>
            {
                await Do(Verb.UseItem, "barrel", "lantern_lit");
                Expect("MansionKitchen", "up out of the burning cellar");
                Check(Gs.HasFlag("cellar_fire"), "the whiskey is alight");
            });
        }
        await Beat("mansion_escape", async () =>
        {
            _ = Do(Verb.Walk, "back_door");
            string room = free ? "Outskirts" : "Prison";
            await Until(() => _game.Room?.Name == "Outskirts" || _game.Room?.Name == "Prison", 300);
            Expect(room, free ? "out of town" : "prison");
            Check(Gs.HasFlag(Endings.MansionExploded) == free, "the house burns only after the cellar fire");
            await TheEnd();
        }, roundTrip: false);
    }
}
