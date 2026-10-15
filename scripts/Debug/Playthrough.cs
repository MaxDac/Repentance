using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// The canonical story, played from the attic to "The End" through the same actions a player would take, as ordered
/// named beats. Two modes share it:
/// <list type="bullet">
/// <item><c>--playthrough</c>: a test. Acts 1–2 once, then every ending route reloaded from a real save at the Club
/// vestibule. Every beat ends with a save → load round trip; coverage of sounds and Ink choices is checked at the end.
/// Prints "PLAYTHROUGH OK".</item>
/// <item><c>--film[=1|2|4]</c>: the same story to watch, at 1×, 2× or 4× speed, one ending (<c>--ending</c>, default 2).
/// The viewer's input is ignored (Space pauses, F11 toggles full screen, Esc stops). Prints "FILM OK".</item>
/// </list>
/// Routes: 2, 3, 4, 5 (by Eleanor's answer and whether the evidence/fire set Micah free), and the three ways to
/// ending 1: 1 (walk away from Tony), 1-oldman (spare Harrington), 1-steps (give up on the church steps).
/// </summary>
public sealed class Playthrough : Harness
{
    public static readonly string[] Routes = { "2", "3", "4", "5", "1", "1-oldman", "1-steps" };

    /// <summary>
    /// Sounds the canonical routes never play. Every other <see cref="Sound"/> must be heard at least once.
    /// Keep a reason with each entry.
    /// </summary>
    private static readonly Dictionary<Sound, string> UnheardSounds = new()
    {
    };

    private readonly bool _film;
    private string _route = "2";
    private string[] _routes = { "2" };
    private readonly List<string> _decisions = new();
    private readonly HashSet<string> _matchedWants = new();
    private readonly HashSet<string> _shownLabels = new();
    private int _roundTrips;
    private const string RoundTripSlot = "manual_3";

    public Playthrough(bool film)
    {
        _film = film;
        VerbosePasses = !film;
    }

    protected override string Marker => _film ? "FILM" : "PLAYTHROUGH";

    private string Tag => _film ? "film" : "playthrough";

    private static GameState Gs => GameState.Instance;

    public async Task Run(Game game)
    {
        string? summary = null;
        try
        {
            if (!Setup(game)) return;
            DialogueManager.Instance.AutoChoose = Choose;
            DialogueManager.Instance.ChoicesOffered += Record;
            if (_film) await Film();
            else await Test();
            summary = $"[{Tag}] {_checks} checks, {_roundTrips} save/load round trips, {_decisions.Count} decisions";
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            DialogueManager.Instance.AutoChoose = null;
            DialogueManager.Instance.ChoicesOffered -= Record;
            Finish(summary);
        }
    }

    private bool Setup(Game game)
    {
        _game = game;
        string ending = Arg("ending") ?? (_film ? "2" : "all");
        if (ending == "all" && !_film) _routes = Routes;
        else if (Routes.Contains(ending)) _routes = new[] { ending };
        else
        {
            _failures.Add($"unknown --ending={ending} (use {string.Join(", ", Routes)}{(_film ? "" : " or all")})");
            return false;
        }
        if (!_film) return Begin(game, "playthrough");

        string speed = Arg("film") ?? "1";
        if (speed is not ("1" or "2" or "4"))
        {
            _failures.Add($"unknown --film={speed} (use 1, 2 or 4)");
            return false;
        }
        if (!Begin(game, "film", applyClock: false)) return false;
        Engine.TimeScale = double.Parse(speed);
        game.GetTree().Root.CallDeferred(Node.MethodName.AddChild, new SpectatorFilter { Name = "SpectatorFilter" });
        GD.Print($"[film] {speed}x, ending {_routes[0]}. Space pauses, F11 toggles full screen, Esc stops.");
        return true;
    }

    // ------------------------------------------------------------------ modes

    private async Task Film()
    {
        _route = _routes[0];
        _game.Hud.ShowTitle(true);
        await _game.Hud.Fade(0, 0.8);
        await _game.Wait(3);
        await _game.Hud.Fade(1, 0.5);
        _game.Hud.ShowTitle(false);
        await _game.NewGame();
        await WaitIdle();
        await ActsOneAndTwo();
        await ActThree();
        await _game.Wait(4);
    }

    private async Task Test()
    {
        await _game.NewGame();
        await WaitIdle();
        await ActsOneAndTwo();
        string checkpoint = SaveSystem.ManualSlot(1);
        Check(_game.SaveToSlot(checkpoint), "saved the Club vestibule checkpoint");
        var save = SaveSystem.Read(checkpoint) ?? throw new InvalidOperationException("Missing the vestibule checkpoint");
        var wantsBeforeActThree = _matchedWants.ToList();
        for (int i = 0; i < _routes.Length; i++)
        {
            _route = _routes[i];
            GD.Print($"[playthrough] ---- route {_route}");
            if (i > 0)
            {
                await _game.LoadGame(save);
                await WaitIdle();
                _matchedWants.Clear();
                _matchedWants.UnionWith(wantsBeforeActThree);
                Check(_game.Room is Rooms.ClubVestibule && Gs.HasItem("sealed_invitation"), $"route {_route}: reloaded the vestibule checkpoint");
            }
            await ActThree();
        }
        if (_routes.Length == Routes.Length) CoverageGates();
    }

    // ------------------------------------------------------------------ beats

    /// <summary>One named step of the story. Afterwards the playthrough saves, loads and compares the whole state.</summary>
    private async Task Beat(string id, Func<Task> body, bool roundTrip = true)
    {
        GD.Print($"[{Tag}] beat {id}" + (Gs.StoryAct == 3 ? $" (route {_route})" : ""));
        await body();
        if (roundTrip && !_film) await RoundTrip(id);
    }

    private async Task RoundTrip(string id)
    {
        await WaitIdle();
        if (!_game.CanSave)
        {
            Fail($"{id}: the game can't be saved after the beat");
            return;
        }
        var before = _game.CaptureSave();
        if (!_game.SaveToSlot(RoundTripSlot) || SaveSystem.Read(RoundTripSlot) is not { } saved)
        {
            Fail($"{id}: save written and read back");
            return;
        }
        await _game.LoadGame(saved);
        await WaitIdle();
        var after = _game.CaptureSave();
        _roundTrips++;
        var diffs = new List<string>();
        if (after.Room != before.Room) diffs.Add($"room {before.Room} -> {after.Room}");
        if (Math.Abs(after.X - before.X) > 0.5 || Math.Abs(after.Y - before.Y) > 0.5) diffs.Add("position");
        if (after.Facing != before.Facing) diffs.Add("facing");
        if (after.StoryAct != before.StoryAct) diffs.Add("act");
        if (!after.Flags.ToHashSet().SetEquals(before.Flags))
            diffs.Add("flags " + string.Join(",", after.Flags.Except(before.Flags).Concat(before.Flags.Except(after.Flags))));
        if (!after.Inventory.SequenceEqual(before.Inventory)) diffs.Add("inventory");
        if (after.Ink != before.Ink) diffs.Add("ink state");
        Check(diffs.Count == 0 && _game.CanSave, $"{id}: save/load round trip" + (diffs.Count > 0 ? $" ({string.Join("; ", diffs)})" : ""));
    }

    private async Task ActsOneAndTwo()
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
            await Do(Verb.UseItem, "grille", "blue_carnation");
            Expect("Speakeasy", "the blue carnation opens the grille");
        });
        await Beat("speakeasy", async () =>
        {
            await Do(Verb.Talk, "bartender");
            await Until(() => !_game.Busy);
            Check(Gs.HasFlag("sal_passed"), "Sal takes the bribe");
            await Do(Verb.Talk, "bartender");
            await WaitIdle();
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
            Check(Gs.HasItem("mirror"), "the cleaned mirror");
            await Do(Verb.Walk, "exit");
            Expect("ConventCorridor", "back to the corridor");
        });
        await Beat("end_of_act_one", async () =>
        {
            await Do(Verb.Walk, "entrance");
            await WaitIdle();
            Check(Gs.StoryAct == 2 && _game.Room?.Name == "Attic", "the farewell, Eleanor on the road, the motel, and back to the attic in Act 2");
        });
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

    /// <summary>Waits for "End of Act Three", then Daniel's epilogue in the attic and "The End".</summary>
    private async Task TheEnd()
    {
        int ending = _route.StartsWith('1') ? 1 : int.Parse(_route);
        await Until(() => _game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three", 300);
        Check(_game.Hud.CaptionText == "End of Act Three", $"route {_route}: End of Act Three");
        await Until(() => _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End", 300);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionText == "The End", $"route {_route}: the epilogue ends on \"The End\"");
        for (int n = 1; n <= 5; n++)
            Check(Gs.HasFlag($"ending_{n}") == (n == ending), $"route {_route}: ending_{n} {(n == ending ? "set" : "not set")}");
        Check(Gs.HasItem("journal") == (ending == 1), $"route {_route}: Daniel {(ending == 1 ? "keeps the journal for Leo" : "puts the journal back")}");
        // Choose() falls back to the first option, so a renamed or wrongly gated choice would otherwise pass silently.
        // By now the cross is taken, so Wants() names the Blue Lantern; Caleb was asked for on the first visit. Giving up
        // on the steps ends the story before Act 3's office, so that route only answers the stage.
        var required = _route == "1-steps" ? new[] { "Give up" } : Wants().Append("Visit Caleb").Distinct();
        foreach (var want in required)
            Check(_matchedWants.Contains(want), $"route {_route}: the choice \"{want}\" was offered and taken");
    }

    // ------------------------------------------------------------------ decisions

    /// <summary>What each route answers. Unmatched choices take the first option, as the main story does.</summary>
    private IEnumerable<string> Wants()
    {
        yield return "Accept the cross";
        yield return Gs.HasFlag("took_cross") ? "Go to the Blue Lantern" : "Visit Caleb";
        yield return _route == "1-steps" ? "Give up" : "Keep going";
        switch (_route)
        {
            case "1":
                yield return "Lower the gun. It's not worth it";
                break;
            case "1-oldman":
                yield return "Shoot him in the shoulder";
                yield return "Lower the gun";
                break;
            case "2":
                yield return "Shoot him";
                yield return "You can't stay";
                yield return "Every time";
                break;
            case "3":
                yield return "Shoot him";
                yield return "He had it coming";
                yield return "Nobody's coming";
                break;
            case "4":
                yield return "Shoot him";
                yield return "I didn't come all this way";
                break;
            case "5":
                yield return "Shoot him";
                yield return "You can't stay";
                yield return "I'll go to the police";
                break;
        }
    }

    private async Task<int> Choose(string knot, IReadOnlyList<string> options)
    {
        int pick = 0;
        foreach (var want in Wants())
        {
            int i = options.ToList().FindIndex(o => o.Contains(want, StringComparison.Ordinal));
            if (i < 0) continue;
            pick = i;
            _matchedWants.Add(want);
            break;
        }
        _decisions.Add($"{knot}: {options[pick]}");
        GD.Print($"[{Tag}] choice {knot}: {string.Join(" | ", options)} -> {options[pick]}");
        if (_film)
        {
            _ = _game.Hud.ShowChoices(options);
            await _game.Wait(1.5);
            _game.Hud.HighlightChoice(pick);
            await _game.Wait(1.0);
            _game.Hud.HideChoices();
        }
        return pick;
    }

    private void Record(string knot, IReadOnlyList<string> labels)
    {
        foreach (var label in labels) _shownLabels.Add(label);
    }

    // ------------------------------------------------------------------ coverage

    private void CoverageGates()
    {
        var all = Enum.GetValues<Sound>();
        var unheard = all.Where(s => _game.Sfx.Count(s) == 0).ToList();
        foreach (var s in unheard.Where(s => !UnheardSounds.ContainsKey(s)))
            Fail($"sound {s} is never played in the story (or add it to UnheardSounds with a reason)");
        foreach (var s in UnheardSounds.Keys.Where(s => !unheard.Contains(s)))
            Fail($"sound {s} is played now: remove it from UnheardSounds");
        Check(unheard.All(UnheardSounds.ContainsKey), $"every sound is heard ({all.Length - unheard.Count}/{all.Length})");
        var tracks = Enum.GetValues<Track>();
        var silent = tracks.Where(t => _game.Music.Count(t) == 0).ToList();
        foreach (var t in silent) Fail($"music track {t} never plays in the story");
        Check(silent.Count == 0, $"every music track plays ({tracks.Length - silent.Count}/{tracks.Length})");

        using var file = FileAccess.Open(DialogueManager.StoryPath, FileAccess.ModeFlags.Read);
        var scan = InkScan.Parse(file.GetAsText());
        var choices = scan.Choices.Where(c => !c.Fallback).ToList();
        int shown = choices.Count(c => _shownLabels.Any(l => InkScan.Matches(c, l)));
        GD.Print($"[playthrough] Ink choices offered on the canonical routes: {shown}/{choices.Count}; " +
                 "every choice is reached by InkWalkTests' exhaustive Ink walk.");
        Check(shown > 0, "the playthrough records the Ink choices it is offered");
    }

    // ------------------------------------------------------------------ helpers

    protected override Task Pace(double seconds) => _film ? _game.Wait(seconds) : Task.CompletedTask;

    private async Task Do(Verb verb, string hotspot, string? item = null)
    {
        await Pace(0.6);
        await _game.Perform(verb, hotspot, item);
    }

    private Task WaitIdle() => WaitIdle(_game);

    private void Expect(string room, string what) =>
        Check(_game.Room?.Name == room, $"{what} (in {_game.Room?.Name ?? "no room"}, expected {room})");

    /// <summary>Waits for a full-screen image, then lets any line over it finish (or clicks through it) and closes it.</summary>
    private async Task DismissImage(string what)
    {
        await Until(() => _game.Hud.ImageVisible, 60);
        Check(_game.Hud.ImageVisible, $"{what}: shown full screen");
        for (int i = 0; i < 600 && _game.Hud.ImageVisible; i++)
        {
            // a line over the picture: the test clicks through it, the film lets it be read
            if (_game.Hud.ImageHeld)
            {
                if (!_film) Click(new Vector2(240, 140));
            }
            else
            {
                await Pace(2);
                _game.Hud.CloseImage();
            }
            await _game.Wait(0.2);
        }
        Check(!_game.Hud.ImageVisible, $"{what}: closed");
    }
}
