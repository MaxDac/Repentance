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
        Seed(noChurch, act3Items, Refuses.Append("(Leave her to them.)").Prepend("Shoot him").ToArray());
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
        Check(!Offered("oldman_taunt", "Our Father") && gs.HasFlag("shot_oldman"), "without Caleb, Micah can't spare the old man");
        Check(!gs.HasFlag("eleanor_convinced") && game.Room?.Name == "MansionKitchen", "Eleanor won't come");
        CheckPersuasionTurns();
        // Seeded endings follow the permanent epilogue lock; exercise the recipe without reopening its blocked HUD.
        await game.Run(() => Story.StoryPuzzles.TryReadAccounts(game));
        Check(!game.Hud.Puzzle.IsOpen && !gs.HasFlag(Endings.TookDocuments), "escape kitchen cannot decode skipped evidence after confrontation");
        await game.Perform(Verb.Walk, "baize_door");
        Check(game.Room?.Name == "MansionKitchen", "skipped study cannot be revisited during escape");
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionCellar", "the cellar is open during the escape");
        await game.Perform(Verb.Walk, "stair");
        Check(game.Room?.Name == "MansionCellar", "nor reached through the cellar stair");
        await game.Perform(Verb.Walk, "kitchen_steps");
        Check(game.Room?.Name == "MansionKitchen", "back up to the kitchen");
        await Shot("mansion_kitchen_alone");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Prison");
        Check(gs.HasFlag("ending_5"), "ending 5: prison, Caleb visits");
        Check(RainsHere(), "ending 5: it still rains past the prison window");
        Check(game.Music.Current == Track.PrisonParlour, "ending 5: the visiting room's own noises, no music");
        Check(gs.HasItem("cloth"), "ending 5: Eleanor's cloth is still in Micah's pocket");
        await game.Wait(4);
        await Shot("ending_prison_caleb");
        await TheEnd("ending_5");

        // 4: Eleanor comes, but no ledgers and no fire
        Seed(act3Flags, act3Items, Convinces.Prepend("Shoot him").ToArray());
        await game.ChangeRoom("mansion_bedroom", "start");
        Check(gs.HasFlag("eleanor_convinced") && !Offered("eleanor_footsteps", "Leave her to them"),
            "Eleanor convinced by the four right lines, before any footsteps");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Prison");
        Check(gs.HasFlag("ending_4"), "ending 4: prison, Eleanor visits");
        await game.Wait(4);
        await Shot("ending_prison_eleanor");
        await TheEnd("ending_4");

        // 3: the house burns, Eleanor stays behind
        Seed(act3Flags.Append("cellar_lit"), act3Items,
            Convinces.Take(3).Prepend("Shoot him").Append("I love you").Append("(Leave her to them.)").ToArray());
        await game.ChangeRoom("mansion_bedroom", "start");
        Check(!gs.HasFlag("eleanor_convinced") && Offered("eleanor_footsteps", "Leave her to them"),
            "three right lines and a wrong fourth aren't enough: Eleanor stays, and the footsteps come");
        await game.Perform(Verb.Walk, "cellar_door");
        await game.Perform(Verb.Hand, "barrel");
        await game.Perform(Verb.Hand, "hung_lantern");
        await game.Perform(Verb.UseItem, "barrel", "lantern_lit");
        await WaitIdle(game);
        Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("cellar_fire"), "alone, the cellar set alight");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Outskirts");
        Check(gs.HasFlag("ending_3") && gs.HasFlag(Endings.MansionExploded), "ending 3: out of town, alone");
        Check(RainsHere(), "ending 3: rain on the road out of town");
        await Until(() => game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning", 10);
        bool nextMorning = game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning";
        Check(nextMorning, "alone fire escape opens with the next-morning caption");
        await game.Wait(3);
        await Shot("ending_alone");
        await TheEnd("ending_3", nextMorning);

        // Signed evidence alone preserves both outskirts outcomes without a fire.
        foreach (bool convinced in new[] { false, true })
        {
            // not convinced: one wrong first line, then the right ones; the chain stays broken
            var lines = convinced ? Convinces : Convinces.Skip(1).Prepend("They'll pin it on you");
            Seed(act3Flags.Append(Endings.TookDocuments), act3Items.Append("documents"),
                lines.Prepend("Shoot him").Append("(Leave her to them.)").ToArray());
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(gs.HasFlag(Endings.EleanorConvinced) == convinced,
                convinced ? "documents-only route preserves Eleanor's decision" : "one wrong line breaks the chain for good");
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Outskirts");
            string ending = convinced ? "ending_2" : "ending_3";
            Check(gs.HasFlag(ending) && !gs.HasFlag(Endings.MansionExploded) && !gs.HasFlag("cellar_fire"),
                $"{ending}: signed evidence without fire");
            await TheEnd($"{ending} (documents only)");
        }

        // Verify the actual Ink choices for each missing commitment, not only the helper predicates.
        foreach (string missing in new[] { "faith_ring", "cross" })
        {
            Seed(act3Flags.Append("rose_wait"), act3Items.Where(i => i != missing), "Shoot him", "(Leave her.)");
            await game.ChangeRoom("mansion_bedroom", "start");
            Check(!Offered("oldman_taunt", "Our Father"), $"without {missing}, the final return is unavailable");
        }
        Seed(alleyReady, act3Items.Where(i => i != "faith_ring"), "Shoot him");
        await game.ChangeRoom("alley", "act3");
        await game.Perform(Verb.Talk, "back_door");
        Check(!Offered("bartender_gun", "Lower the gun"), "church return without ring doesn't allow walking away from Tony");

        // 1: walking away from Tony
        Check(act3Items.Contains("cloth"), "Act 3 seeds carry Eleanor's cloth");
        Seed(alleyReady, act3Items.Where(i => i != "cross"), "Lower the gun");
        await game.ChangeRoom("alley", "act3");
        _ = game.Perform(Verb.Talk, "back_door");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag("walked_away") && gs.HasFlag("ending_1"), "ending 1: walked away from Tony, coffee with Rose");
        await Until(() => gs.HasFlag("rose_door"));
        Check(!gs.HasItem("cloth"), "ending 1: Micah throws Eleanor's cloth in the street before ringing");
        await game.Wait(1);
        await Until(() => game.Player.Facing == Facing.Up && game.Player.Position.DistanceTo(Rooms.RoseHouse.TalkSpot) < 2);
        Check(game.Player.Facing == Facing.Up, "Act 3: Micah stands by the bell, his back to the screen");
        await Shot("rose_coffee");
        await TheEnd("ending_1 (Tony)");

        // 1: sparing the old man, praying the Our Father verse by verse while backing to the door
        Seed(act3Flags.Append("rose_wait"), act3Items, "Our Father");
        float nearest = float.MaxValue;
        bool lowering = false, steppedBack = false, versesFaded = false;
        _ = game.ChangeRoom("mansion_bedroom", "start");
        var prayer = new List<string>();
        var coda = new List<string>();
        string? lastPrayerLine = null;
        await Until(() =>
        {
            if (game.Room is Rooms.MansionBedroom)
            {
                if (game.Player.PoseName == "micah_aim_lower") lowering = true;
                if (game.Player.PoseName == "micah_aim_back") steppedBack = true;
                if (lowering) nearest = Mathf.Min(nearest, game.Player.Position.X);
                if (game.Hud.VersesVisible && game.Hud.VersesText != "" && (coda.Count == 0 || coda[^1] != game.Hud.VersesText))
                    coda.Add(game.Hud.VersesText);
                if (game.Hud.VersesVisible && game.Hud.VersesFading) versesFaded = true;
            }
            if (game.Hud.SpeechVisible && game.Hud.SpeechText != lastPrayerLine) prayer.Add(lastPrayerLine = game.Hud.SpeechText);
            return game.Room?.Name == "RoseHouse";
        }, 180, 0.05);
        Check(gs.HasFlag("spared_oldman") && gs.HasFlag("ending_1"), "ending 1: spared the old man");
        Check(lowering && nearest < 70, "Micah backs to the door, lowering the revolver step by step");
        Check(steppedBack, "Micah's legs step back with each verse");
        Check(prayer.Any(l => l.Contains("Thy kingdom come", StringComparison.OrdinalIgnoreCase)) &&
              prayer.Any(l => l.Contains("deliver us from evil")) && !prayer.Any(l => l.Contains("Amen")),
            "Micah prays up to \"deliver us from evil\" on his way out, without the Amen");
        var doxology = Rooms.MansionBedroom.Doxology;
        Check(coda.SequenceEqual(Enumerable.Range(1, doxology.Length).Select(n => string.Join("\n", doxology.Take(n)))),
            "the prayer ends over black, a line at a time, down to \"Amen.\"");
        Check(versesFaded, "the closing verses fade in and out");
        Check(prayer.Count(l => l.Contains("Our Father")) == 1, "Micah says \"Our Father...\" once, then goes on with the prayer");
        await TheEnd("ending_1 (old man)");

        // 6: shoots the old man, then repents and turns himself in; Rose visits him in jail
        Seed(act3Flags.Append(Endings.TookDocuments), act3Items.Append("documents"), "Shoot him", "turn yourself in");
        _ = game.ChangeRoom("mansion_bedroom", "start");
        await Until(() => game.Room?.Name == "Prison", 180);
        Check(gs.HasFlag(Endings.Repented) && gs.HasFlag("ending_6") && !gs.HasFlag("escaping"),
            "ending 6: straight to jail, even with the signed evidence");
        Check(DryHere(), "ending 6: Micah repented, and the rain has stopped outside the prison window");
        Check(game.Room?.GetNodeOrNull<CanvasItem>("Rose")?.Visible == true &&
              game.Room?.GetNodeOrNull<CanvasItem>("Caleb")?.Visible != true &&
              game.Room?.GetNodeOrNull<CanvasItem>("Eleanor")?.Visible != true, "ending 6: Rose sits across the table");
        await game.Wait(4);
        await Shot("ending_prison_rose");
        await TheEnd("ending_6");

        // 7: Eleanor won't come; on the fourth turn Micah shoots her, then himself. Then the other ending 7: four
        // turns without her, the footsteps, and he turns the gun on himself alone.
        foreach (bool murder in new[] { true, false })
        {
            string label = murder ? "ending_7 (murder)" : "ending_7 (alone)";
            var prefer = murder
                ? Refuses.Take(3).Prepend("Shoot him").Append("(Shoot Eleanor.)")
                : Refuses.Prepend("Shoot him").Append("(Pull the trigger on myself.)");
            Seed(act3Flags, act3Items, prefer.ToArray());
            HeardLog = new List<string>();
            int shots = game.Sfx.Count(Sound.Gunshot);
            bool eleanorDown = false, aimSelf = false, morning = false, lastWords = false, facedAway = false;
            _ = game.ChangeRoom("mansion_bedroom", "start");
            await Until(() =>
            {
                if (game.Room is Rooms.MansionBedroom bedroom)
                {
                    eleanorDown |= bedroom.FindActor("eleanor")?.Texture?.ResourcePath.EndsWith("eleanor_shot.png") == true;
                    aimSelf |= game.Player.PoseName == "micah_aim_self";
                    if (game.Hud.SpeechVisible && game.Hud.SpeechText == Rooms.MansionBedroom.LastWords)
                    {
                        lastWords = true;
                        facedAway |= game.Player.Facing == Facing.Left;
                    }
                }
                morning |= game.Hud.CaptionVisible && game.Hud.CaptionText == "The next morning";
                return game.Hud.CaptionVisible && game.Hud.CaptionText == "End of Act Three";
            }, 180, 0.05);
            Check(gs.HasFlag("ending_7") && gs.HasFlag(Endings.ShotEleanor) == murder && gs.HasFlag(Endings.ShotHimself) == !murder,
                murder ? "ending 7: Micah shoots Eleanor" : "ending 7: Micah shoots himself and leaves Eleanor alive");
            Check(Offered("eleanor_footsteps", "Pull the trigger") == !murder,
                murder ? $"{label}: shot on the fourth turn, before the footsteps" : $"{label}: the footsteps come after four turns");
            if (!murder) CheckPersuasionTurns();
            Check(eleanorDown == murder, murder ? "ending 7: Eleanor falls like the old man, shot in the stomach" : $"{label}: Eleanor stays standing");
            Check(lastWords && facedAway, $"{label}: \"{Rooms.MansionBedroom.LastWords}\", looking away at an empty corner");
            Check(aimSelf, $"{label}: Micah puts the revolver to his temple");
            Check(game.Sfx.Count(Sound.Gunshot) >= shots + 1, $"{label}: the last shot is heard over black");
            await TheEnd(label);
            Check(HeardLog.Count(l => l.Contains("He shot Mr. Harrington on his own carpet.")) == 1 && !HeardLog.Any(l => l.Contains("in his bed.")),
                $"{label}: Daniel's epilogue has the old man shot on his own carpet, not in his bed");
            HeardLog = null;
            Check(!morning && !gs.HasFlag("escaping"), $"{label}: no escape and no \"The next morning\"");
        }

        await EleanorEndings(game, gs, act3Flags, act3Items);

        // One refusal isn't enough to wear Eleanor out: with only the gin refused, the persuasion still runs.
        Seed(act3Flags.Append(Endings.RefusedDrugs), act3Items, Convinces.Prepend("Shoot him").ToArray());
        await game.ChangeRoom("mansion_bedroom", "start");
        Check(_offered.ContainsKey("eleanor_persuade") && gs.HasFlag(Endings.EleanorConvinced) &&
              !gs.HasFlag(Endings.EleanorWeary),
            "one refusal (the gin only): Micah gets his four turns, and Eleanor isn't worn out");
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => game.Room?.Name == "Prison");
        Check(gs.HasFlag("ending_4") && !gs.HasFlag("ending_11") && !gs.HasFlag(Endings.EleanorWeary),
            "one refusal (the gin only): the ordinary prison ending 4, not ending 11");
        await TheEnd("ending_4 (gin refused only)");

        // 1: giving up on the church steps
        Seed(act3Flags.Where(f => f != "keep_going"), act3Items.Where(i => i is not ("faith_ring" or "cross")), "Give up");
        _ = game.ChangeRoom("church_exterior", "beaten");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag(Endings.GaveUpSteps) && gs.HasFlag("ending_1"), "ending 1: gave up on the steps");
        await TheEnd("ending_1 (steps)");

        // Eleanor's refusals only matter once Micah shoots the old man: both of them still give way to the give-ups.
        var bothRefused = new[] { Endings.RefusedAbbess, Endings.RefusedDrugs };
        Seed(act3Flags.Where(f => f != "keep_going").Concat(bothRefused), act3Items.Where(i => i is not ("faith_ring" or "cross")), "Give up");
        _ = game.ChangeRoom("church_exterior", "beaten");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag(Endings.GaveUpSteps) && gs.HasFlag("ending_1") && !gs.HasFlag("eleanor_coda") &&
              !gs.HasFlag("eleanor_epilogue") && !gs.HasFlag(Endings.EleanorStruck),
            "ending 1: giving up on the steps wins over both of Eleanor's refusals");
        await TheEnd("ending_1 (steps, Eleanor held out)");

        Seed(alleyReady.Concat(bothRefused), act3Items.Where(i => i != "cross"), "Lower the gun");
        await game.ChangeRoom("alley", "act3");
        _ = game.Perform(Verb.Talk, "back_door");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(gs.HasFlag("walked_away") && gs.HasFlag("ending_1") && !gs.HasFlag("eleanor_coda") &&
              !gs.HasFlag("eleanor_epilogue") && !gs.HasFlag(Endings.EleanorWeary),
            "ending 1: walking away from Tony wins over both of Eleanor's refusals");
        await TheEnd("ending_1 (Tony, Eleanor held out)");
    }

    /// <summary>
    /// Endings 8 to 11, and ending 1 from Eleanor's coda: seeded with both of her refusals (Agatha and the old man's
    /// gin), which the main run's interludes didn't make.
    /// </summary>
    private async Task EleanorEndings(Game game, GameState gs, string[] act3Flags, string[] act3Items)
    {
        var heldOut = act3Flags.Append(Endings.RefusedAbbess).Append(Endings.RefusedDrugs).ToArray();

        // 10 and 11: Micah shoots the old man; Eleanor, worn out, skips the persuasion and follows him out in silence.
        // With the documents taken or the house burnt she leaves him at the edge of the city (10); with neither, she
        // visits him in prison (11).
        foreach (string way in new[] { "documents", "fire", "none" })
        {
            bool documents = way == "documents", fire = way == "fire", free = way != "none";
            string label = free ? $"ending_10 ({way})" : "ending_11";
            string ending = free ? "ending_10" : "ending_11";
            var flags = documents ? heldOut.Append(Endings.TookDocuments) : fire ? heldOut.Append("cellar_lit") : heldOut;
            Seed(flags.ToArray(), act3Items, "Shoot him");
            HeardLog = new List<string>();
            _ = game.ChangeRoom("mansion_bedroom", "start");
            await Until(() => game.Room?.Name == "MansionKitchen", 120);
            await game.Wait(0.2);
            await Until(() => !game.Busy, 30);
            Check(gs.HasFlag(Endings.EleanorWeary) && !gs.HasFlag(Endings.EleanorConvinced) && gs.HasItem("revolver"),
                $"{label}: Eleanor follows, worn out, and Micah keeps the revolver");
            Check(!_offered.ContainsKey("eleanor_persuade"), $"{label}: no persuasion turns");
            Check(HeardLog.Any(l => l.Contains("Let's get out of here, quick.")), $"{label}: \"Let's get out of here, quick.\"");
            Check(game.Room?.FindActor("eleanor")?.Visible == true, $"{label}: Eleanor waits in the kitchen");
            if (fire)
            {
                HeardLog.AddRange(await Spoken(() => game.Perform(Verb.Walk, "cellar_door")));
                await game.Perform(Verb.Hand, "barrel");
                await game.Perform(Verb.Hand, "hung_lantern");
                HeardLog.AddRange(await Spoken(() => game.Perform(Verb.UseItem, "barrel", "lantern_lit")));
                await game.Wait(0.2);
                await Until(() => game.Room?.Name == "MansionKitchen" && !game.Busy, 60);
                Check(gs.HasFlag("cellar_fire") && game.Room?.FindActor("eleanor")?.Visible == true,
                    $"{label}: the cellar set alight, Eleanor still by the door");
                Check(HeardLog.Any(l => l.Contains("She smells the smoke. She doesn't ask.")), $"{label}: she smells the smoke and doesn't ask");
            }
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() => game.Room?.Name == "Outskirts" || game.Room?.Name == "Prison", 120);
            Check(gs.HasFlag(ending) && game.Room?.Name == (free ? "Outskirts" : "Prison") && game.Player.Character != "eleanor_play",
                free ? $"{label}: Micah and Eleanor out of town" : "ending 11: Micah in prison");
            Check(gs.HasFlag(Endings.MansionExploded) == fire, $"{label}: the house goes up only when the cellar burns");
            Check(game.Room?.FindActor("eleanor")?.Visible == true || game.Room?.GetNodeOrNull<CanvasItem>("Eleanor")?.Visible == true,
                $"{label}: Eleanor is there");
            string line = free ? "I can't go on like this, Micah, I can't be with you. I need ... peace."
                : "I hope you find your peace, Micah. I'm going to try to find mine, with the help of the Lord...";
            await Until(() => HeardLog.Any(l => l.Contains(line)), 60);
            if (documents) await Shot("ending_weary_road");
            await TheEnd(label);
            Check(HeardLog.Any(l => l.Contains(line)), $"{label}: Eleanor's last words to Micah");
            Check(!HeardLog.Any(l => l.Contains("That's enough of you")), $"{label}: Micah writes the last entries himself");
            Check(HeardLog.Any(l => l.Contains("Not one more word in this house.")) &&
                  HeardLog.Any(l => l.Contains("She doesn't say a word. She said she wouldn't, not in this house.")),
                $"{label}: she swears off words in the house, and keeps to it");
            foreach (var spoken in new[] { "The back door, Micah", "The door's that way.", "What did you do?", "Oh my God, Micah." })
                Check(!HeardLog.Any(l => l.Contains(spoken)), $"{label}: weary Eleanor doesn't say \"{spoken}\"");
            Check(HeardLog.Any(l => l.Contains("She watches the windows go. She doesn't make a sound.")) == fire,
                $"{label}: she watches the house go without a sound only when it burns");
            Check(HeardLog.Any(l => l.Contains("changed in mine on the way")) == free,
                $"{label}: the black dress from the Club's car explained only on the road out");
            HeardLog = null;
        }
        // 9 and 8: the Our Father, then the player is Eleanor; the candlestick, the study, the kitchen and the back door.
        // Ending 8 sets the cellar alight on the way.
        foreach (bool fire in new[] { false, true })
        {
            string label = fire ? "ending_8" : "ending_9";
            Seed(fire ? heldOut.Append("rose_wait").Append("cellar_lit") : heldOut.Append("rose_wait"), act3Items, "Our Father");
            _ = game.ChangeRoom("mansion_bedroom", "start");
            await Until(() => game.Room is Rooms.MansionBedroom && game.Player.Character == "eleanor_sheet_play", 180);
            await WaitIdle(game);
            Check(gs.HasFlag(Endings.SparedOldMan) && gs.HasFlag("eleanor_coda"), $"{label}: after the prayer, the player is Eleanor");
            Check(!game.Hud.SatchelVisible, $"{label}: no satchel for Eleanor");
            var harrington = game.Room?.FindActor("harrington");
            Check(harrington?.Visible == true && harrington.Texture?.ResourcePath.EndsWith("harrington_struck_down.png") != true,
                $"{label}: the old man stands watching the door");
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "MansionBedroom" && !gs.HasFlag(Endings.EleanorStruck), $"{label}: she can't get past him");
            Check(game.Player.Position.X >= Rooms.MansionBedroom.BehindHim.X - 2,
                $"{label}: the door refusal leaves her on the bed side of him (x {game.Player.Position.X:0})");
            await game.WalkTo(new Vector2(40, 238));
            Check(game.Room?.Name == "MansionBedroom" && game.Player.Position.X >= Rooms.MansionBedroom.BehindHim.X - 2,
                $"{label}: a click on the floor by the door doesn't walk her through him (x {game.Player.Position.X:0})");
            if (!fire) await Shot("eleanor_coda");
            Check(harrington?.Position == Rooms.MansionBedroom.HarringtonCoda && harrington.FlipH,
                $"{label}: he stands at the foot of the bed, his back to her");
            int strikes = _poseCounts.GetValueOrDefault("eleanor_strike");
            float left = float.MaxValue;
            bool candleHidden = false, mutter = false, reached = false;
            var striking = game.Perform(Verb.Hand, "candlestick");
            await Until(() =>
            {
                reached |= game.Player.Position.DistanceTo(Rooms.MansionBedroom.Nightstand) < 3;
                if (reached) left = Mathf.Min(left, game.Player.Position.X);
                mutter |= game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("A Ford");
                candleHidden |= game.Player.PoseName == "eleanor_strike" &&
                    game.Room?.GetNodeOrNull<CanvasItem>("CandlestickSprite")?.Visible == false;
                return striking.IsCompleted;
            }, 60, 0.02);
            await WaitIdle(game);
            Check(mutter, $"{label}: he mutters at the door, back turned, while she takes it");
            Check(left >= Rooms.MansionBedroom.BehindHim.X - 2 && candleHidden,
                $"{label}: candlestick off the nightstand, a step to him, no walk across the room (leftmost x {left:0})");
            var down = game.Room?.FindActor("harrington");
            Check(down?.Position == Rooms.MansionBedroom.HarringtonCoda, $"{label}: he falls where he stood");
            Check(gs.HasFlag(Endings.EleanorStruck) && _poseCounts.GetValueOrDefault("eleanor_strike") == strikes + 1,
                $"{label}: the candlestick, from behind");
            Check(game.Room?.FindActor("harrington")?.Texture?.ResourcePath.EndsWith("harrington_struck_down.png") == true,
                $"{label}: the old man lies face down");
            if (!fire)
            {
                await ReloadCheckpoint("eleanor_coda");
                Check(game.Player.Character == "eleanor_sheet_play" && gs.HasFlag("eleanor_coda") &&
                      game.Room?.FindActor("harrington")?.Texture?.ResourcePath.EndsWith("harrington_struck_down.png") == true,
                    "a save in the coda loads back as Eleanor, with the old man down");
                await Shot("eleanor_struck");
            }
            await game.Perform(Verb.Walk, "door");
            Check(game.Room?.Name == "MansionStudy", $"{label}: through his study");
            if (fire)
            {
                // the other way down: the panel behind his bar, open since Micah came up the bootleggers' stair
                await game.Perform(Verb.Walk, "bar_panel");
                Check(game.Room?.Name == "MansionCellar", "ending 8: down the bootleggers' stair from the study");
                await game.Perform(Verb.Walk, "stair");
                Check(game.Room?.Name == "MansionCellar", "ending 8: not back up to him");
                await game.Perform(Verb.Hand, "barrel");
                Check(!gs.HasFlag(Endings.EleanorBurned), "ending 8: the barrel wants a flame first");
                await game.Perform(Verb.Hand, "hung_lantern");
                await game.Perform(Verb.Hand, "barrel");
                await WaitIdle(game);
                Check(gs.HasFlag(Endings.EleanorBurned) && gs.HasFlag("cellar_fire") && game.Room?.Name == "MansionKitchen",
                    "ending 8: the Club's rye alight, and up to the kitchen");
            }
            else
            {
                await game.Perform(Verb.Walk, "door_left");
                Check(game.Room?.Name == "MansionKitchen", $"{label}: down to the kitchen");
            }
            bool eleanorInmate = false, sawRose = false;
            HeardLog = new List<string>();
            _ = game.Perform(Verb.Walk, "back_door");
            await Until(() =>
            {
                sawRose |= game.Room?.Name == "RoseHouse";
                eleanorInmate |= game.Room?.Name == "Prison" && game.Room.GetNodeOrNull<CanvasItem>("EleanorInmate")?.Visible == true &&
                    game.Room.GetNodeOrNull<CanvasItem>("Micah")?.Visible != true;
                return game.Room?.Name == (fire ? "Outskirts" : "Prison") && !game.Busy || game.Hud.CaptionText == "End of Act Three";
            }, 240, 0.05);
            Check(sawRose && !gs.HasItem("cloth"), $"{label}: Micah's journal goes on to Rose's door, without the cloth");
            Check(gs.HasFlag(label) && !gs.HasFlag("eleanor_coda"), $"{label}: recorded once the coda is over");
            Check(DryHere(), $"{label}: no rain where Eleanor ends up");
            if (fire)
                Check(game.Player.Character == "eleanor_play" && !gs.HasFlag(Endings.MansionExploded), "ending 8: Eleanor alone, out of the city");
            else
                Check(eleanorInmate && gs.HasFlag("caleb_visits"), "ending 9: Eleanor in prison grey, confessing to Caleb");
            await TheEnd(label);
            Check(HeardLog.Any(l => l.Contains("her black dress still on the back seat")) == fire,
                fire ? "ending 8: out of the sheet and into her own black dress, from the Club's car" : $"{label}: no car at the gate");
            HeardLog = null;
        }

        // 1: back under the sheet, the way she got out of it; Micah's story goes on to Rose's
        Seed(heldOut.Append("rose_wait"), act3Items, "Our Father");
        _ = game.ChangeRoom("mansion_bedroom", "start");
        await Until(() => game.Room is Rooms.MansionBedroom && game.Player.Character == "eleanor_sheet_play", 180);
        await WaitIdle(game);
        int returns = _poseCounts.GetValueOrDefault("eleanor_mansion_return");
        _ = game.Perform(Verb.Hand, "bed");
        await Until(() => game.Room?.Name == "RoseHouse", 120);
        Check(gs.HasFlag("ending_1") && !gs.HasFlag(Endings.EleanorStruck) && !gs.HasFlag("eleanor_coda"),
            "ending 1: Eleanor goes back to bed, and Micah to Rose");
        Check(_poseCounts.GetValueOrDefault("eleanor_mansion_return") == returns + 1, "ending 1: her climb back into bed plays");
        await TheEnd("ending_1 (Eleanor's bed)");
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
        gs.Restore(openingFlags.Append("office_door_open"), originalItems.Where(i => i != "faith_ring"), 2);
        _prefer = new[] { "Leave the wedding ring" };
        await game.ChangeRoom("office", "act2");
        Check(gs.HasFlag("office_door_open"), "Micah opens the office door himself on his way out at the start of Act 2");
        Check(gs.HasFlag("ring_left_act2") && !gs.HasFlag("ring_taken_act2") && !gs.HasItem("faith_ring"),
            "leaving the ring records the original choice without granting it");
        Check(_crossOffers == offers, "initial confession never offers the cross even when ring was left");
        gs.SetFlag("teddy_gone", false);
        await game.Perform(Verb.Walk, "office");
        Check(!gs.HasFlag("office_door_open") && !gs.HasFlag("office_door_ajar")
            && game.Room?.GetNodeOrNull<Sprite2D>("DoorOpen")?.Visible == false,
            "the office door is shut again when Micah comes back");
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
        Check(!gs.HasFlag("office_door_open") && game.Room?.GetNodeOrNull<Sprite2D>("DoorOpen")?.Visible == false,
            "the Act 3 office starts with the door shut");
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

    /// <summary>The only way to convince Eleanor: these four lines, one per turn, in a row.</summary>
    private static readonly string[] Convinces =
        { "we don't stay in this city", "lend you out again", "walk through that door", "decide it yourself" };

    /// <summary>A wrong line on each of Eleanor's four turns.</summary>
    private static readonly string[] Refuses =
        { "I didn't come all this way", "Theodore's a coward", "A singer", "I love you" };

    private int _seedLog;

    /// <summary>
    /// Eleanor's four turns as offered since the last <see cref="Seed"/>: turning himself in only on the first,
    /// leaving her from the third, shooting her only on the fourth; then the footsteps' three ways out.
    /// </summary>
    private void CheckPersuasionTurns()
    {
        var turns = _offerLog.Skip(_seedLog).Where(o => o.Knot == "eleanor_persuade").Select(o => o.Options).ToList();
        Check(turns.Count == 4, $"Eleanor gets four turns ({turns.Count})");
        bool Has(int turn, string option) => turn < turns.Count && turns[turn].Any(o => o.Contains(option));
        bool On(string option, params int[] at) => Enumerable.Range(0, 4).All(i => Has(i, option) == at.Contains(i));
        Check(On("turn yourself in", 0), "turning himself in is offered on the first turn only");
        Check(On("(Leave her.)", 2, 3), "leaving her is offered after two turns");
        Check(On("(Shoot Eleanor.)", 3), "shooting her is offered only after three turns");
        var footsteps = _offerLog.Skip(_seedLog).LastOrDefault(o => o.Knot == "eleanor_footsteps").Options ?? Array.Empty<string>();
        Check(footsteps.Length == 3 && footsteps.Any(o => o.Contains("Pull the trigger on myself")) &&
              footsteps.Any(o => o.Contains("Shoot Eleanor")) && footsteps.Any(o => o.Contains("Leave her to them")),
            "after four turns, the footsteps: himself, Eleanor, or leave");
    }

    private void Seed(IEnumerable<string> flags, IEnumerable<string> items, params string[] prefer)
    {
        _seedLog = _offerLog.Count;
        // the previous ending holds "The End", and the game busy, until something replaces the story
        _game.ReleaseTheEnd();
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
                $"{ending}: next-morning transition only after alone escape with fire");
        int endingNumber = Enumerable.Range(1, 11).FirstOrDefault(n => gs.HasFlag($"ending_{n}"));
        bool keepJournal = Endings.KeepsJournal(endingNumber);
        bool dismissed = endingNumber is >= 2 and <= 5;
        bool sawVows = false, vowsBesideSpeech = false;
        bool TheEndOrVows()
        {
            if (_game.Hud.CurrentCloseUp == CloseUps.Vows && _game.Hud.InsetName == "vows_photo" && _game.Hud.InsetDrawn)
            {
                sawVows = true;
                var photo = _game.Hud.InsetRect;
                if (_game.Hud.SpeechVisible && photo.End.X < 480 / 2 && !photo.Intersects(_game.Hud.SpeechRect)
                    && _game.Hud.SpeechRect.Position.X > photo.End.X)
                    vowsBesideSpeech = true;
            }
            return _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End";
        }
        await Until(() => TheEndOrVows() || vowsBesideSpeech, 120);
        if (vowsBesideSpeech && !_vowsShot)
        {
            _vowsShot = true;
            await Shot("vows_photo");
        }
        await Until(TheEndOrVows, 120);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End",
            $"{ending}: final attic caption");
        Check(sawVows == (endingNumber == 1), $"{ending}: the vow-renewal photo only pops up in ending 1's epilogue");
        if (endingNumber == 1)
            Check(vowsBesideSpeech, $"{ending}: the photo sits on the left with Daniel's lines beside it");
        Check(!_game.Hud.InsetVisible, $"{ending}: no close-up left over on \"The End\"");
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
