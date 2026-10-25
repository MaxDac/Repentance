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
        // film mode said good night to Rose at once in Act 2; the test and --resume share one vestibule save with her
        // call-back, so the ending 15 routes forget it here
        if (RoseRefuses && !_film) Gs.SetFlag("rose_wait", false);
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
            await Do(Verb.Hand, "compact");
            await Do(Verb.Hand, "lipstick");
            Check(Gs.HasItem("compact") && Gs.HasItem("lipstick"), "her compact and lipstick from the dressing table");
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
            Check(Gs.HasItem("faith_ring") && Gs.HasFlag("rose_wait") == !RoseRefuses,
                $"route {_route}: the ring in Micah's pocket, and Rose's call-back {(RoseRefuses ? "forgotten" : "remembered")}");
            var spoken = await Spoken(() => Do(Verb.Walk, "door"));
            await WaitIdle();
            Check(Gs.HasItem("cross") && spoken.Any(l => l.Contains("Rose and Tommy are still there")), "Caleb's counsel and his cross");
            Expect("Alley", "from the church straight on to the Blue Lantern's alley");
            Check(Gs.HasFlag("alley3_sal_inside") && Gs.HasFlag("alley3_tony_inside"), "the alley set for tonight");
        });
        await Beat("alley_act_three", async () =>
        {
            await Do(Verb.Kick, "street_lamp");
            await Do(Verb.Kick, "trash");
            await Do(Verb.UseItem, "sal", "revolver");
            Check(Gs.HasFlag("alley3_sal_down"), "Sal knocked down");
            Check(_game.Room?.FindActor("sal") is { } sal &&
                sal.Position.X - _game.Player.Position.X is >= 24 and <= 32,
                "Micah steps close behind Sal for the short downward revolver-butt blow");
            var tony = Do(Verb.Talk, "back_door");
            if (WalkAwayRoute)
            {
                await Until(() => _game.Room?.Name == "RoseHouse", 300);
                Check(Gs.HasFlag(Endings.WalkedAway), "walked away from Tony");
                Check(Gs.HasFlag(Endings.RoseForgives) == !RoseRefuses,
                    $"Rose {(RoseRefuses ? "refuses the coffee" : "takes the coffee")}");
                if (EleanorRoute)
                {
                    int ending = RoseRefuses ? 15 : 1;
                    await Until(() => _game.Room?.Name == "Outskirts", 600);
                    Expect("Outskirts", "Eleanor and Caleb at the city's edge");
                    Check(Gs.HasFlag("caleb_escape") && Gs.HasFlag($"ending_{ending}"), $"ending {ending}, with Eleanor's escape");
                    Check(_game.Player.Character == "eleanor_white_play", "Eleanor in her white dress");
                    Check(_game.Room?.FindActor("caleb")?.Visible == true, "Caleb beside her");
                }
                await TheEnd();
                over = true;
                return;
            }
            await tony;
            await WaitIdle();
            if (AlarmRoute)
            {
                Check(Gs.HasFlag(Endings.WarnedTony) && !Gs.HasFlag(Endings.ShotBartender) && !Gs.HasFlag("alley3_tony_inside"),
                    "the warning shot: Tony stays outside unhurt while Micah leaves");
                Expect("OfficeStorm", "back to the office, in the storm");
                return;
            }
            Check(Gs.HasFlag("shot_bartender"), "Tony shot in the shoulder");
            if (KillRoute)
            {
                Expect("Alley", "Micah finishes Tony, and stays in the alley");
                Check(Gs.HasFlag(Endings.KilledTony), "the second shot: Tony can't tell anyone now");
                await Do(Verb.Walk, "street");
                await WaitIdle();
                Expect("ChicagoMap", "the map, one last time");
                Check(new[] { "blue_lantern", "church", "mansion" }.All(id => _game.Room?.FindHotspot(id)?.Visible == true) &&
                      new[] { "office", "library", "club" }.All(id => _game.Room?.FindHotspot(id)?.Visible != true),
                    "only the Blue Lantern, the church and the mansion are left on the map");
                var church = Do(Verb.Walk, "church");
                bool closeUp = false;
                bool Watching(bool done)
                {
                    closeUp |= _game.Hud.CurrentCloseUp == CloseUps.Church && _game.Hud.SpeechVisible &&
                        _game.Hud.SpeechText.StartsWith("Bless me, Father");
                    return done;
                }
                if (_route == "12")
                {
                    await Until(() => Watching(_game.Room?.Name == "Prison"), 300, 0.05);
                    Check(closeUp, "the brothers' close-up for Micah's confession");
                    Expect("Prison", "Micah turns himself in at Caleb's side");
                    Check(Gs.HasFlag(Endings.SurrenderedTony), "surrendered at the church");
                    await TheEnd();
                    over = true;
                    return;
                }
                await Until(() => Watching(church.IsCompleted), 600, 0.05);
                await church;
                await WaitIdle();
                Check(closeUp && !_game.Hud.InsetVisible, "the brothers' close-up for Micah's confession, gone as he leaves");
                Check(Gs.HasFlag(Endings.ConfessedTony), "confessed to Caleb, and promised the station at sunrise");
                Expect("OfficeStorm", "on from the church to the office, in the storm");
                return;
            }
            Expect("OfficeStorm", "Tony left bleeding: Micah walks out, back to the office, in the storm");
        }, roundTrip: _route is not ("1" or "1-caleb" or "15" or "15-caleb" or "12"));
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
            if (AlarmRoute)
            {
                // Tony left the bell out: ordinary inspection of the door and lintel doesn't expose it.
                await Do(Verb.Look, "door");
                await Do(Verb.Look, "lintel");
                Check(!Gs.HasFlag("alarm_noticed"), "the door and lintel don't reveal Tony's omitted alarm");
                await Do(Verb.Hand, "lintel");
                Check(Gs.HasItem("kitchen_key") && !Gs.HasFlag("alarm_noticed"), "the key, and the bell still unseen");
                var door = _route == "14" ? Do(Verb.UseItem, "door", "kitchen_key") : Do(Verb.Hand, "door");
                if (_route == "13")
                {
                    await Until(() => _game.Room?.Name == "Outskirts", 300);
                    Expect("Outskirts", "Micah runs, and drives out of Chicago");
                    Check(Gs.HasFlag(Endings.AlarmRan) && Gs.HasFlag("alarm_noticed"), "the bell rang, and Micah ran");
                }
                else
                {
                    await Until(() => _game.Room?.Name == "MansionKitchen", 300);
                    Expect("MansionKitchen", "Micah goes in after the bell");
                    Check(Gs.HasFlag(Endings.AlarmStayed) && _game.Room?.FindActor("gunman")?.Visible == true
                        && _game.Room?.FindActor("gunman_b")?.Visible == true, "the Club's two men wait at the cook's table");
                }
                await TheEnd();
                over = true;
                return;
            }
            await Do(Verb.Look, "door");
            await Do(Verb.Hand, "lintel");
            await Do(Verb.Hand, "bin");
            await SolvePuzzle(() => Do(Verb.Hand, "bell"), PuzzleKind.Bell, new[] { ("s1", 1), ("s2", 2) }, "alarm_restraint");
            await Do(Verb.Hand, "door");
            Expect("MansionKitchen", "in through the kitchen");
        }, roundTrip: !AlarmRoute);
        if (over) return;
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
            if (free || _route == "12-oldman")
            {
                await Do(Verb.Hand, "drawer_right");
                await Do(Verb.Hand, "documents");
                await Do(Verb.Hand, "drawer_left");
                await SolvePuzzle(() => CombineAndWait("audit_folder", "audit_tracing"), PuzzleKind.Alignment,
                    new[] { ("flip", 1), ("rotate", 2), ("right", 6), ("down", 9) }, "audit_alignment");
                Check(Gs.HasFlag(Endings.TookDocuments), "the signed payoff sheets");
            }
            var confront = Do(Verb.Walk, "door_right");
            if (_route == "12-oldman")
            {
                await Until(() => _game.Room?.Name == "Prison", 300);
                Expect("Prison", "after the prayer, Caleb at the station steps");
                Check(Gs.HasFlag(Endings.SparedOldMan) && Gs.HasFlag("caleb_visits"), "spared the old man, and Caleb visits");
                await TheEnd();
                over = true;
                return;
            }
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
