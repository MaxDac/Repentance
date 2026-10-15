using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The other endings, seeded from Act 3, and the ending checks.</summary>
public partial class AutoPlay
{
    /// <summary>The other endings, each from a state seeded at the start of Act 3.</summary>
    private async Task PlayOtherEndings(Game game, GameState gs)
    {
        // ---- the other endings, each from a seeded state
        var act3Flags = _act3Flags;
        var act3Items = _act3Items;
        string[] alleyReady = act3Flags.Where(f => f != "alley3_sal_inside")
            .Concat(new[] { "alley3_dark", "alley3_sal_out", "alley3_sal_down" }).ToArray();

        // 5: no visits to Caleb, so no walking away; shoot, Eleanor stays, nothing to bargain with
        var noChurch = alleyReady.Where(f => f is not ("church_before_office" or "church_before_club" or "church_act3_return")).Append("rose_wait");
        Seed(noChurch, act3Items, "Shoot him", "You can't stay", "Nobody's coming");
        await game.ChangeRoom("alley", "act3");
        await game.Perform(Verb.Talk, "back_door");
        Check(!Offered("bartender_gun", "Lower the gun") && gs.HasFlag("shot_bartender"), "without Caleb, Micah can't walk away from Tony");
        await game.ChangeRoom("mansion_study", "start");
        await game.Perform(Verb.Hand, "drawer_right");
        await game.Perform(Verb.Hand, "drawer_left");
        await CancelPuzzle(() => game.Perform(Verb.UseItem, "documents", "audit_tracing"), PuzzleKind.Alignment, "audit_identified", "audit_room_use");
        Check(gs.HasItem("audit_folder") && gs.HasItem("audit_tracing") && !gs.HasFlag(Endings.TookDocuments),
            "cancelled room-use alignment retains clues but no evidence");
        await game.Perform(Verb.Walk, "door_right");
        Check(!Offered("oldman_taunt", "Lower the gun") && gs.HasFlag("shot_oldman"), "without Caleb, Micah can't spare the old man");
        Check(!gs.HasFlag("eleanor_convinced") && game.Room?.Name == "MansionKitchen", "Eleanor won't come");
        // Seeded endings follow the permanent epilogue lock; exercise the recipe without reopening its blocked HUD.
        await game.Run(() => Story.StoryPuzzles.TryReadAccounts(game));
        Check(!game.Hud.Puzzle.IsOpen && !gs.HasFlag(Endings.TookDocuments), "escape kitchen cannot decode skipped evidence after confrontation");
        await game.Perform(Verb.Walk, "baize_door");
        Check(game.Room?.Name == "MansionKitchen", "skipped study cannot be revisited during escape");
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionKitchen", "nor reached through the cellar");
        await Shot("mansion_kitchen_alone");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Prison");
        Check(gs.HasFlag("ending_5"), "ending 5: prison, Caleb visits");
        await game.Wait(4);
        await Shot("ending_prison_caleb");
        await TheEnd("ending_5");

        // 4: Eleanor comes, but no ledgers and no fire
        Seed(act3Flags, act3Items, "Shoot him", "I didn't come all this way");
        await game.ChangeRoom("mansion_bedroom", "start");
        Check(gs.HasFlag("eleanor_convinced"), "Eleanor convinced at the first try");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Prison");
        Check(gs.HasFlag("ending_4"), "ending 4: prison, Eleanor visits");
        await game.Wait(4);
        await Shot("ending_prison_eleanor");
        await TheEnd("ending_4");

        // 3: the house goes up, Eleanor stays behind
        Seed(act3Flags, act3Items, "Shoot him", "He had it coming", "I'll go to the police");
        await game.ChangeRoom("mansion_bedroom", "start");
        Check(!gs.HasFlag("eleanor_convinced"), "Eleanor stays");
        await game.Perform(Verb.Hand, "range");
        await game.Perform(Verb.Hand, "candle");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Outskirts");
        Check(gs.HasFlag("ending_3") && gs.HasFlag(Endings.MansionExploded), "ending 3: out of town, alone");
        await Until(() => game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning", 10);
        bool nextMorning = game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning";
        Check(nextMorning, "alone explosion escape opens with the next-morning caption");
        await game.Wait(3);
        await Shot("ending_alone");
        await TheEnd("ending_3", nextMorning);

        // Signed evidence alone preserves both outskirts outcomes without a fire.
        foreach (bool convinced in new[] { false, true })
        {
            Seed(act3Flags.Append(Endings.TookDocuments), act3Items.Append("documents"),
                "Shoot him", convinced ? "I didn't come all this way" : "He had it coming", "I'll go to the police");
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(gs.HasFlag(Endings.EleanorConvinced) == convinced, "documents-only route preserves Eleanor's decision");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Outskirts");
            string ending = convinced ? "ending_2" : "ending_3";
            Check(gs.HasFlag(ending) && !gs.HasFlag(Endings.MansionExploded) &&
                !gs.HasFlag("gas_on") && !gs.HasFlag("candle_lit"), $"{ending}: signed evidence without explosion");
            await TheEnd($"{ending} (documents only)");
        }

        // Verify the actual Ink choices for each missing commitment, not only the helper predicates.
        foreach (string missing in new[] { "faith_ring", "cross" })
        {
            Seed(act3Flags.Append("rose_wait"), act3Items.Where(i => i != missing), "Shoot him", "He had it coming", "I'll go to the police");
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(!Offered("oldman_taunt", "Lower the gun"), $"without {missing}, the final return is unavailable");
        }
        Seed(alleyReady, act3Items.Where(i => i != "faith_ring"), "Shoot him");
        await game.ChangeRoom("alley", "act3");
        await game.Perform(Verb.Talk, "back_door");
        Check(!Offered("bartender_gun", "Lower the gun"), "church return without ring doesn't allow walking away from Tony");

        // 1: walking away from Tony
        Seed(alleyReady, act3Items.Where(i => i != "cross"), "Lower the gun");
        await game.ChangeRoom("alley", "act3");
        _ = game.Perform(Verb.Talk, "back_door");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag("walked_away") && gs.HasFlag("ending_1"), "ending 1: walked away from Tony, coffee with Rose");
        await Until(() => gs.HasFlag("rose_door"));
        await game.Wait(1);
        await Until(() => game.Player.Facing == Facing.Up && game.Player.Position.DistanceTo(Rooms.RoseHouse.TalkSpot) < 2);
        Check(game.Player.Facing == Facing.Up, "Act 3: Micah stands by the bell, his back to the screen");
        await Shot("rose_coffee");
        await TheEnd("ending_1 (Tony)");

        // 1: sparing the old man, praying the Our Father verse by verse while backing to the door
        Seed(act3Flags.Append("rose_wait"), act3Items, "Lower the gun");
        float nearest = float.MaxValue;
        bool lowering = false;
        _ = game.ChangeRoom("mansion_bedroom", "start");
        var prayer = new List<string>();
        string? lastPrayerLine = null;
        await Until(() =>
        {
            if (game.Room is Rooms.MansionBedroom)
            {
                if (game.Player.PoseName == "micah_aim_lower") lowering = true;
                if (lowering) nearest = Mathf.Min(nearest, game.Player.Position.X);
            }
            if (game.Hud.SpeechVisible && game.Hud.SpeechText != lastPrayerLine) prayer.Add(lastPrayerLine = game.Hud.SpeechText);
            return game.Room?.Name == "RoseHouse";
        }, 180, 0.05);
        Check(gs.HasFlag("spared_oldman") && gs.HasFlag("ending_1"), "ending 1: spared the old man");
        Check(lowering && nearest < 70, "Micah backs to the door, lowering the revolver step by step");
        Check(prayer.Any(l => l.Contains("Thy kingdom come", StringComparison.OrdinalIgnoreCase)) &&
              prayer.Any(l => l.Contains("Amen")), "Micah says the whole Our Father on his way out");
        await TheEnd("ending_1 (old man)");

        // 6: shoots the old man, then repents and turns himself in; Rose visits him in jail
        Seed(act3Flags.Append(Endings.TookDocuments), act3Items.Append("documents"), "Shoot him", "turn yourself in");
        _ = game.ChangeRoom("mansion_bedroom", "start");
        await Until(() => game.Room?.Name == "Prison", 180);
        Check(gs.HasFlag(Endings.Repented) && gs.HasFlag("ending_6") && !gs.HasFlag("escaping"),
            "ending 6: straight to jail, even with the signed evidence");
        Check(game.Room?.GetNodeOrNull<CanvasItem>("Rose")?.Visible == true &&
              game.Room?.GetNodeOrNull<CanvasItem>("Caleb")?.Visible != true &&
              game.Room?.GetNodeOrNull<CanvasItem>("Eleanor")?.Visible != true, "ending 6: Rose sits across the table");
        await game.Wait(4);
        await Shot("ending_prison_rose");
        await TheEnd("ending_6");

        // 7: Eleanor won't come; Micah shoots her, then himself
        Seed(act3Flags, act3Items, "Shoot him", "He had it coming", "Shoot Eleanor");
        int shots = game.Sfx.Count(Sound.Gunshot);
        bool eleanorDown = false, aimSelf = false, morning = false;
        _ = game.ChangeRoom("mansion_bedroom", "start");
        await Until(() =>
        {
            if (game.Room is Rooms.MansionBedroom bedroom)
            {
                eleanorDown |= bedroom.FindActor("eleanor")?.Texture?.ResourcePath.EndsWith("eleanor_shot.png") == true;
                aimSelf |= game.Player.PoseName == "micah_aim_self";
            }
            morning |= game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning";
            return game.Hud.CaptionVisible && game.Hud.CaptionText == "End of Act Three";
        }, 180, 0.05);
        Check(gs.HasFlag(Endings.ShotEleanor) && gs.HasFlag("ending_7"), "ending 7: Micah shoots Eleanor");
        Check(eleanorDown, "ending 7: Eleanor falls like the old man, shot in the stomach");
        Check(aimSelf, "ending 7: Micah puts the revolver to his temple");
        Check(game.Sfx.Count(Sound.Gunshot) >= shots + 1, "ending 7: the last shot is heard over black");
        await TheEnd("ending_7");
        Check(!morning && !gs.HasFlag("escaping"), "ending 7: no escape and no \"The next morning\"");

        // 1: giving up on the church steps
        Seed(act3Flags.Where(f => f != "keep_going"), act3Items.Where(i => i is not ("faith_ring" or "cross")), "Give up");
        _ = game.ChangeRoom("church_exterior", "beaten");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag(Endings.GaveUpSteps) && gs.HasFlag("ending_1"), "ending 1: gave up on the steps");
        await TheEnd("ending_1 (steps)");
    }

    /// <summary>Starts a seeded Act 3 run from the alley: its flags (edited), inventory and Ink state, and the choices to prefer.</summary>
    private async Task RingAndCrossTest(Game game)
    {
        var gs = GameState.Instance;
        var originalFlags = gs.Flags.ToArray();
        var originalItems = gs.Inventory.ToArray();
        var originalInk = DialogueManager.Instance.SaveInk();
        var originalPrefer = _prefer;
        int offers = _crossOffers;
        var openingFlags = originalFlags.Where(f => f is not ("ring_taken_act2" or "took_faith_ring" or
            "act2_office_done" or "act2_whiskey_drunk" or "caleb_met" or "act2_church_thought"))
            .Append("act2_church");
        gs.Restore(openingFlags, originalItems.Where(i => i != "faith_ring"), 2);
        _prefer = new[] { "Leave the wedding ring" };
        await game.ChangeRoom("office", "act2");
        Check(gs.HasFlag("ring_left_act2") && !gs.HasFlag("ring_taken_act2") && !gs.HasItem("faith_ring"),
            "leaving the ring records the original choice without granting it");
        Check(_crossOffers == offers, "initial confession never offers the cross even when ring was left");
        gs.SetFlag("teddy_gone", false);
        await game.Perform(Verb.Walk, "office");
        Check(gs.HasFlag("teddy_gone") && game.Room?.FindHotspot("teddy")?.Visible != true,
            "Teddy doesn't come back to the office after Act 1");
        Check(game.Room?.GetNodeOrNull<Sprite2D>("WeddingRing/Glint") != null
            && game.Room?.FindHotspot("faith_ring")?.Bounds.Size is { X: <= 10, Y: <= 8 }, "the small ring glints on the desk");
        Check(game.Room?.FindHotspot("faith_ring")?.Visible == true, "left ring remains visible at the office");
        await Shot("office_ring_left");
        await game.Perform(Verb.Walk, "door");
        gs.SetFlag("club_out");
        gs.SetFlag("caleb_club");
        _prefer = new[] { "Refuse the cross" };
        await game.Perform(Verb.Walk, "church");
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 2 && !gs.HasItem("cross"), "Act 2 refusal repeats the offer on the next visit");
        await game.Perform(Verb.Walk, "office");
        await game.Perform(Verb.Hand, "faith_ring");
        Check(gs.HasItem("faith_ring") && gs.HasFlag("ring_left_act2") && !gs.HasFlag("ring_taken_act2") &&
            game.Room?.FindHotspot("faith_ring")?.Visible == false, "recovering the ring preserves the original leave decision");
        await game.Perform(Verb.Walk, "door");
        _prefer = new[] { "Accept the cross" };
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 3 && gs.HasItem("cross") && gs.HasFlag("took_cross"),
            "recovered ring doesn't postpone the Act 2 cross offer");
        await game.Perform(Verb.Walk, "church");
        Check(_crossOffers == offers + 3 && gs.Inventory.Count(i => i == "cross") == 1, "Act 2 acceptance stops duplicate offers");
        Rooms.Attic.StashMicahItems();
        Check(!gs.HasItem("faith_ring") && !gs.HasItem("cross") && gs.HasFlag("ring_left_act2") && !gs.HasItem(Notes.ItemId),
            "Daniel's interlude puts Micah's commitments aside without losing the original decision");
        Rooms.Attic.RestoreMicahItems(2);
        Check(gs.HasItem("faith_ring") && gs.HasItem("cross") && gs.HasFlag("took_cross"),
            "both commitments return with Micah's inventory");
        gs.TakeItem("faith_ring");
        gs.SetFlag("took_faith_ring", false);
        gs.SetFlag("micah_at_desk");
        gs.SetFlag("keep_going");
        gs.SetStoryAct(3);
        await game.ChangeRoom("office", "act3");
        Check(game.Room?.Name == "Office" && !game.Busy, "Act 3 office waits for player input");
        await game.Perform(Verb.Hand, "faith_ring");
        Check(gs.HasItem("faith_ring") && gs.HasFlag("ring_left_act2"), "left ring can be recovered at the Act 3 office");

        gs.Restore(originalFlags, originalItems, 2);
        DialogueManager.Instance.LoadInk(originalInk);
        _prefer = originalPrefer;
        await game.ChangeRoom("chicago_map", "start");
    }

    private async Task RoseWalkAwayTest(Game game)
    {
        var original = game.CaptureSave();
        var dialogue = DialogueManager.Instance;
        var choose = dialogue.AutoChoose!;
        try
        {
            foreach (var walkAway in new[] { false, true })
            {
                await game.LoadGame(original);
                dialogue.ResetInk();
                string[]? offered = null;
                dialogue.AutoChoose = (knot, options) =>
                {
                    if (knot != "rose_leave") return choose(knot, options);
                    offered = options.ToArray();
                    return Task.FromResult(walkAway ? 0 : 1);
                };
                await game.ChangeRoom("rose_house", "start");
                var heard = await Listen(game, game.Perform(Verb.Walk, "exit"));
                Check(offered is { Length: 2 } && offered[0].Contains("Walk away") && offered[1].Contains("Not yet"),
                    "leaving Rose's house before ringing is an active choice");
                Check(!GameState.Instance.HasFlag("rose_door") && !heard.Any(l => l.StartsWith("Good night") || l.Contains("Micah Jones")),
                    "Rose never opens the door nor answers when Micah doesn't ring");
                if (!walkAway)
                {
                    Check(game.Room?.Name == "RoseHouse" && !GameState.Instance.HasFlag("rose_avoided"), "\"Not yet\" keeps Micah at Rose's door");
                    continue;
                }
                Check(game.Room?.Name == "ChicagoMap" && GameState.Instance.HasFlag("rose_avoided") &&
                    !GameState.Instance.HasFlag("rose_wait") && !GameState.Instance.HasFlag("rose_done"),
                    "walking away without a word returns to the map, like leaving without insisting");
                Check(heard.Any(l => l.Contains("left the bell alone")), "Micah's closing thought as he walks away");
                await game.LoadGame(game.CaptureSave());
                Check(GameState.Instance.HasFlag("rose_avoided") && !GameState.Instance.HasFlag("rose_wait"),
                    "save/load preserves walking away from Rose's door");
            }
        }
        finally
        {
            dialogue.AutoChoose = choose;
            await game.LoadGame(original);
        }
    }

    private async Task RoseAppealsTest(Game game)
    {
        var original = game.CaptureSave();
        var dialogue = DialogueManager.Instance;
        var choose = dialogue.AutoChoose!;
        try
        {
            for (int appeals = 0; appeals <= 5; appeals++)
            {
                await game.LoadGame(original);
                dialogue.ResetInk();
                dialogue.AutoChoose = (knot, options) => knot == "rose_house"
                    ? Task.FromResult(dialogue.Get("pushes").AsInt32() < appeals ? 0 : options.Count - 1)
                    : choose(knot, options);
                await game.ChangeRoom("rose_house", "start");
                var heard = await Listen(game, game.Perform(Verb.Hand, "bell"));
                bool dismissed = heard.Any(l => l.Contains("Don't bother ringing this bell again, Micah Jones."));
                bool shutForGood = heard.Any(l => l.Contains("Just once, and for good."));
                Check(dismissed == (appeals < 3) && shutForGood == (appeals < 3),
                    $"Rose {(appeals < 3 ? "dismisses Micah and shuts the door" : "doesn't dismiss Micah")} after {appeals} appeals");
                Check(heard.Any(l => l.Contains("Wait!")) == (appeals >= 3), $"\"Wait!\" only after insisting ({appeals} appeals)");
                Check(dialogue.Get("pushes").AsInt32() == appeals, $"Rose visit records {appeals} appeals");
                Check(GameState.Instance.HasFlag("rose_wait") == (appeals >= 3),
                    $"Rose callback threshold after {appeals} appeals");
                Check(game.Room?.Name == "ChicagoMap" && !GameState.Instance.HasFlag("rose_door"),
                    "Rose closes the door and the visit returns to the map");
                await game.LoadGame(game.CaptureSave());
                Check(GameState.Instance.HasFlag("rose_wait") == (appeals >= 3) &&
                    dialogue.Get("pushes").AsInt32() == appeals, "save/load preserves the actual doorstep decision");
            }
        }
        finally
        {
            dialogue.AutoChoose = choose;
            await game.LoadGame(original);
        }
    }

    private void Seed(IEnumerable<string> flags, IEnumerable<string> items, params string[] prefer)
    {
        _game.Hud.ShowCaption(null);
        GameState.Instance.Restore(flags.ToArray(), items.ToArray(), 3);
        DialogueManager.Instance.LoadInk(_act3Ink);
        if (prefer.Length > 0) _prefer = prefer;
        _offered.Clear();
    }

    private bool Offered(string knot, string option) =>
        _offered.TryGetValue(knot, out var options) && options.Any(o => o.Contains(option));

    /// <summary>Waits for "End of Act Three", then for Daniel's epilogue to finish on "The End".</summary>
    private async Task TheEnd(string ending, bool sawNextMorning = false)
    {
        bool outskirts = _game.Room is Rooms.Outskirts;
        await Until(() =>
        {
            if (_game.Hud.CaptionVisible && _game.Hud.CaptionText == "The next morning")
                sawNextMorning = true;
            return _game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three";
        }, 120);
        Check(_game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three", $"{ending}: End of Act Three");
        var gs = GameState.Instance;
        if (outskirts)
            Check(sawNextMorning == (gs.HasFlag("ending_3") && gs.HasFlag(Endings.MansionExploded)),
                $"{ending}: next-morning transition only after alone escape with explosion");
        int endingNumber = Enumerable.Range(1, 7).FirstOrDefault(n => gs.HasFlag($"ending_{n}"));
        bool keepJournal = Endings.KeepsJournal(endingNumber);
        bool dismissed = endingNumber is >= 2 and <= 5;
        await Until(() => _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End", 120);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End",
            $"{ending}: final attic caption");
        Check(gs.HasItem("journal") == keepJournal,
            $"{ending}: Daniel {(keepJournal ? "keeps the journal for Leo" : "puts the journal back")}");
        var story = GD.Load<GodotInk.InkStory>(DialogueManager.StoryPath);
        string inkState = story.SaveState();
        try
        {
            story.ChoosePathString("epilogue");
            string[] lines = story.ContinueMaximally().Split('\n', StringSplitOptions.TrimEntries | StringSplitOptions.RemoveEmptyEntries);
            Check(lines.Contains("DANIEL: Maybe Leo would like to read it some day.") == keepJournal,
                $"{ending}: Leo's exact line only appears after reconciliation");
            Check(lines.Contains("DANIEL: That's enough of you for one lifetime, Micah Jones.") == dismissed,
                $"{ending}: dismissal only appears for the bleak endings 2-5");
        }
        finally
        {
            story.LoadState(inkState);
        }
        if (!_theEndShot) await Shot("the_end");
        _theEndShot = true;
    }
}
