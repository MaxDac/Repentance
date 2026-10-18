using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Act 3 of the autoplay run, up to the main ending.</summary>
public partial class AutoPlay
{
    /// <summary>
    /// The Second Interlude: the Order's men at the motel door, then the Club's dressing room, where Eleanor takes the
    /// old man's gin this time (the playthrough's Eleanor routes refuse it). Micah's journal goes on at the stage.
    /// </summary>
    private async Task SecondInterlude(Game game, GameState gs)
    {
        await Until(() => game.Hud.CaptionVisible && game.Hud.CaptionText == "Chicago, 1927.", 30);
        Check(!game.Hud.CaptionSubVisible, "Act 3 opens on black with \"Chicago, 1927.\" alone");
        await Until(() => game.Hud.CaptionSubVisible && game.Hud.CaptionSubText == "Second Interlude", 10);
        Check(game.Hud.CaptionVisible && game.Hud.CaptionText == "Chicago, 1927.",
            "\"Second Interlude\" appears under \"Chicago, 1927.\" on the same black screen");
        await Until(() => game.Room?.Name == "MotelNight");
        await WaitIdle(game);
        Check(gs.HasFlag("interlude2") && game.Player.Character == "eleanor_play" && gs.Inventory.Count == 0 && !gs.HasItem("revolver"),
            "the player is Eleanor at the motel, with nothing of Micah's");
        Check(game.Music.Current == null, "no office jazz in the motel once Micah has gone");
        await Shot("interlude_motel_goons");
        var bedLines = await Spoken(() => game.Perform(Verb.Hand, "bed"));
        var windowLines = await Spoken(() => game.Perform(Verb.Look, "window"));
        Check(bedLines.Contains("Cold on his side now. I won't think about that.") && !bedLines.Any(l => l.Contains("Still warm")),
            "the night after, his side of the bed has gone cold");
        Check(windowLines.Contains("He's gone from the alley. A car's pulled in below, lights off.") && !windowLines.Any(l => l.Contains("His car")),
            "Micah came on foot: no car of his in the lot");
        Check(game.Room?.Name == "MotelNight" && !gs.HasFlag("interlude_goons_in"), "the bed and the window don't bring the knock forward");
        var taken = game.Perform(Verb.Hand, "door");
        await Until(() => game.Room?.FindActor("brute") is { Visible: true } b && b.Position.DistanceTo(new Vector2(84, 212)) < 1
            || game.Room?.Name != "MotelNight", 30);
        Check(game.Room?.GetNodeOrNull<Sprite2D>("DoorKicked")?.Visible == true && game.Sfx.Count(Sound.Crash) > 0,
            "the Order's men kick the motel door in");
        Check(game.Room?.FindActor("goon") is { Visible: true } && game.Player.Position.X >= 120,
            "Bruno and the goon walk in; Eleanor stopped halfway, well away from the door");
        await Shot("interlude_motel_kicked");
        await taken;
        await WaitIdle(game);
        Check(game.Room?.Name == "ClubBackstage" && game.Player.Character == "eleanor_gown_play",
            "the Order's men take her to the Club's dressing room, in the pink gown");
        Check(game.Music.Current == Track.ClubStrings, "the Club's strings behind the dressing room wall");
        Check(game.Room?.FindActor("harrington") is { Visible: false }, "she's alone; the old man isn't in yet");
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "ClubBackstage", "the only door leads to the stage, and Bruno's on it");
        await ReloadCheckpoint("second_interlude");
        Check(game.Player.Character == "eleanor_gown_play", "a save in the dressing room loads back in the gown");
        await game.Wait(0.5);
        await Shot("club_backstage");
        await TheFaceTheyPaidFor(game, gs);
        int drinks = _poseCounts.GetValueOrDefault("eleanor_drink");
        var prefer = _prefer;
        _prefer = new[] { "(Take the glass" };
        _ = game.Perform(Verb.Talk, "harrington");
        await Until(() => game.Room?.Name == "ClubStage");
        _prefer = prefer;
        Check(Offered("interlude_oldman", "(Push it away.)") && !gs.HasFlag(Endings.RefusedDrugs),
            "the old man's gin can be refused; taking it saves nothing");
        Check(_poseCounts.GetValueOrDefault("eleanor_drink") == drinks + 1, "Eleanor drinks: her drink strip plays");
        Check(!gs.HasFlag("interlude2") && !gs.HasFlag("interlude_goons_in") && !gs.HasFlag("interlude_door_kicked")
            && !gs.HasFlag("interlude_made_up"),
            "the interlude's flags are cleared for Micah's part");
        Check(gs.HasItem("revolver") && !new[] { "compact", "lipstick", "puff", "puff_powdered", "hairpin" }.Any(gs.HasItem),
            "Micah gets his kit back, and none of her makeup");
    }

    /// <summary>
    /// Puzzle 18: she puts her face on alone, in order (face powder with the puff, the lipstick, the hairpin), and a save
    /// halfway loads back halfway. Only then does the stage door open: she whispers, he walks in, the door shuts.
    /// </summary>
    private async Task TheFaceTheyPaidFor(Game game, GameState gs)
    {
        Check(game.Hud.SatchelVisible && gs.Inventory.Count == 0, "Eleanor's satchel in the dressing room, empty");
        Check(game.Room?.FindActor("harrington") is { Visible: false } && !gs.HasFlag("interlude_made_up"),
            "no old man to talk to before her face is on");
        await game.Perform(Verb.Hand, "table");
        Check(game.Room?.Name == "ClubBackstage" && gs.Inventory.Count == 0, "the gin table waits too, and gives nothing");
        await game.Perform(Verb.Hand, "mirror");
        Check(gs.HasItem("compact") && gs.HasItem("lipstick"), "her compact and lipstick from the ledge");
        await game.Perform(Verb.UseItem, "mirror", "lipstick");
        Check(gs.HasItem("lipstick") && !gs.HasFlag("interlude_lips"), "no lipstick on a bare face");
        await game.Perform(Verb.UseItem, "mirror", "compact");
        Check(gs.HasItem("compact") && !gs.HasFlag("interlude_powdered"), "no face powder without a puff");
        await CombineAndWait("compact", "lipstick");
        Check(gs.HasItem("compact") && gs.HasItem("lipstick"), "the compact and the lipstick don't go together");
        await game.Perform(Verb.Hand, "rack");
        await game.Perform(Verb.Hand, "screens");
        Check(gs.HasItem("puff") && gs.HasItem("hairpin"), "the puff from a gown pocket, the pin from a crane's wing");
        await game.Perform(Verb.Hand, "mirror");
        await game.Perform(Verb.Hand, "rack");
        await game.Perform(Verb.Hand, "screens");
        Check(gs.Inventory.Count == 4, "the ledge, the rail and the screen give nothing twice");
        await CombineAndWait("puff", "compact");
        Check(gs.HasItem("puff_powdered") && !gs.HasItem("puff") && !gs.HasItem("compact"), "the puff in the face powder");
        await game.Perform(Verb.UseItem, "mirror", "hairpin");
        Check(gs.HasItem("hairpin") && !gs.HasFlag("interlude_made_up"), "the hair waits for the face");
        await game.Perform(Verb.UseItem, "mirror", "puff_powdered");
        Check(gs.HasFlag("interlude_powdered") && !gs.HasItem("puff_powdered"), "face powder first");
        await ReloadCheckpoint("second_interlude_powdered");
        Check(gs.HasFlag("interlude_powdered") && gs.HasItem("lipstick") && gs.HasItem("hairpin") && game.Hud.SatchelVisible,
            "a save with the face half on loads back half on");
        var early = await Spoken(() => game.Perform(Verb.UseItem, "mirror", "hairpin"));
        Check(gs.HasItem("hairpin") && !gs.HasFlag("interlude_made_up") && early.Contains("Powder's on. The mouth next."),
            "the mouth before the hair, and she says so");
        await game.Perform(Verb.UseItem, "mirror", "lipstick");
        Check(game.Room?.FindActor("harrington") is { Visible: false }, "the mouth on, and still no old man");
        var hairpin = game.Perform(Verb.UseItem, "mirror", "hairpin");
        await Until(() => game.Room?.GetNodeOrNull<Sprite2D>("DoorOpen")?.Visible == true || hairpin.IsCompleted, 30);
        Check(game.Room?.GetNodeOrNull<Sprite2D>("DoorOpen")?.Visible == true && game.Room?.FindActor("harrington") is { Visible: false },
            "the face on, the stage door swings open before he shows");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechWhispered || hairpin.IsCompleted, 30);
        Check(game.Hud.SpeechWhispered && game.Hud.SpeechText == "a foul odour of death and ashes. he's here.",
            "Eleanor whispers that she smells him coming");
        await Until(() => game.Room?.FindActor("harrington") is { Visible: true } || hairpin.IsCompleted, 30);
        Check(game.Room?.FindActor("harrington") is { Visible: true } h && h.Position.X < 120, "the old man walks in by the door");
        await Shot("club_backstage_entrance");
        await hairpin;
        Check(game.Room?.FindActor("harrington") is { Visible: true } o && o.Position.DistanceTo(Rooms.ClubBackstage.OldManSpot) < 1,
            "he crosses to his place by the screens");
        Check(game.Room?.GetNodeOrNull<Sprite2D>("DoorOpen")?.Visible == false
            && game.Room?.GetNodeOrNull<Sprite2D>("DoorAjar")?.Visible == false && !gs.HasFlag("backstage_door_open"),
            "the stage door shut behind him");
        Check(gs.HasFlag("interlude_lips") && gs.HasFlag("interlude_made_up") && gs.Inventory.Count == 0, "the face they paid for, on");
    }

    /// <summary>The masked Club, Act 3 and the main ending.</summary>
    private async Task PlayActThree(Game game, GameState gs)
    {
        // ---- the Club, masked: end of Act Two, the bedroom, and the stage in Act 3
        await game.Perform(Verb.Walk, "club");
        await WaitIdle(game);
        Check(game.Room?.Name == "ClubVestibule" && gs.HasFlag("masked") && game.Player.Character == "micah_masked",
            "Micah goes in masked, by the vestibule");
        int clubStarts = game.Music.Count(Track.ClubStrings);
        Check(game.Music.Current == Track.ClubStrings, "the strings play in the vestibule");
        await Shot("club_vestibule");
        await game.Perform(Verb.Walk, "street_door");
        Check(game.Room?.Name == "ClubVestibule", "no way back out to the street");
        await game.Perform(Verb.UseItem, "slot", "invitation");
        Check(game.Room?.Name == "ClubVestibule" && !gs.HasFlag("vestibule_passed") && gs.HasItem("invitation"),
            "the slot refuses an unsealed invitation");
        await game.Perform(Verb.Look, "plaque");
        await game.Perform(Verb.Hand, "sealing_wax");
        Check(gs.HasItem("sealing_wax") && gs.HasFlag("took_sealing_wax"), "took the sealing wax");
        await CombineAndWait("sealing_wax", "invitation");
        Check(gs.HasItem("sealing_wax") && gs.HasItem("invitation") && !gs.HasItem("invitation_waxed"), "cold wax won't take");
        await CombineAndWait(MicahKit.LighterId, "sealing_wax");
        Check(gs.HasItem("wax_soft") && !gs.HasItem("sealing_wax") && gs.HasItem(MicahKit.LighterId) && gs.HasFlag("wax_softened"),
            "the lighter softens the wax and is kept");
        await CombineAndWait("wax_soft", "invitation");
        Check(gs.HasItem("invitation_waxed") && !gs.HasItem("invitation") && !gs.HasItem("wax_soft"), "wax dripped on the invitation");
        await game.Perform(Verb.UseItem, "slot", "invitation_waxed");
        Check(!gs.HasFlag("vestibule_passed") && gs.HasItem("invitation_waxed"), "the slot refuses wax with no seal in it");
        await game.Perform(Verb.Hand, "cloak_lion");
        Check(gs.HasItem("signet_lion"), "borrowed the lion signet");
        await CombineAndWait("signet_lion", "invitation_waxed");
        Check(gs.HasItem("invitation_waxed") && !gs.HasItem("sealed_invitation") && gs.HasItem("signet_lion"),
            "the lion is second in the procession, not first");
        await game.Perform(Verb.Hand, "cloak_raven");
        Check(gs.HasItem("signet_raven") && !gs.HasItem("signet_lion"), "taking the raven hangs the lion back up");
        await ReloadCheckpoint("vestibule_raven");
        await CombineAndWait("signet_raven", "invitation_waxed");
        Check(gs.HasItem("sealed_invitation") && !gs.HasItem("invitation_waxed") && !gs.HasItem("signet_raven")
            && gs.HasFlag("invitation_sealed"), "sealed with the raven, first of the procession; ring hung back up");
        await Shot("club_vestibule_sealed");
        var rite = game.Perform(Verb.UseItem, "slot", "sealed_invitation");
        await Until(() => gs.HasFlag("vestibule_passed"));
        await Shot("club_vestibule_open");
        await Until(() => game.Room?.Name == "ClubHall");
        await WaitIdle(game);
        Check(gs.HasFlag("masked") && game.Player.Character == "micah_masked", "Micah goes in masked");
        Check(gs.HasItem(MicahKit.LighterId) && gs.HasItem("sealed_invitation"), "lighter still held; the sealed card came back out of the slot");
        Check(game.Room?.FindHotspot("guest")?.Visible == true, "masked guests in the hall");
        await rite;
        await Shot("club_hall_masked");
        await game.Perform(Verb.Walk, "exit");
        Check(game.Room?.Name == "ClubLounge", "into the lounge");
        Check(game.Music.Current == Track.ClubStrings && game.Music.Count(Track.ClubStrings) == clubStarts && game.Music.Playing,
            "the same strings carry on through the vestibule, hall and lounge without restarting");
        await Shot("club_lounge");
        var stage = game.Perform(Verb.Walk, "stage_exit");
        await Until(() => game.Room?.Name == "ClubStage");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Stage && game.Hud.InsetName.StartsWith("stage_closeup"), "Eleanor's close-up framed over the stage after Micah's first line");
        Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "the close-up fills most of the screen");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText.StartsWith("And in the light", StringComparison.Ordinal));
        Check(game.Hud.InsetVisible && !game.Hud.SpeechVisible && game.Hud.ThoughtRect.Position.Y < 20 &&
            game.Hud.ThoughtRect.End.Y < game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.3f,
            "Micah's thoughts on Eleanor sit along the top while the close-up is up");
        await game.Wait(4);
        await Shot("club_stage");
        await Until(() => game.Room?.Name == "Attic");
        Check(!game.Hud.InsetVisible, "the close-up is gone in the attic");
        Check(game.Music.Current == null, "the music stops when the journal closes");
        await game.Wait(2);
        await Shot("attic_night2");
        await Until(() => game.Hud.CaptionVisible);
        Check(game.Player.Character == "daniel" && !gs.HasItem("revolver") && gs.HasItem("journal") && !gs.HasItem(Notes.ItemId),
            "back in the attic, Micah's things put away");
        await Shot("end_of_act_two");
        await Until(() => game.Room?.Name == "Bedroom");
        Check(gs.StoryAct == 3, "Act Three");
        await game.Wait(2);
        await Shot("bedroom");
        await SecondInterlude(game, gs);
        await Until(() => game.Room?.Name == "ClubStage");
        Check(gs.HasItem("revolver") && gs.HasFlag("masked") && gs.Inventory.Take(2).SequenceEqual(MicahKit.Pinned),
            "back on the stage with Micah's things, notepad and lighter first");
        Check(gs.Inventory.Skip(2).All(i => MicahKit.KeptInAct(3, i)) && !gs.HasItem("mirror") && !gs.HasItem("card") &&
            !gs.HasItem("lockpick"), "Act 3 starts with only the revolver, the cloth and Micah's commitments");
        Check(gs.HasItem("cloth"), "Eleanor's cloth survives the Act 3 satchel reset");
        await game.Wait(3);
        Check(game.Hud.InsetVisible, "the close-up is back when Act 3 opens on the stage");
        await Shot("club_stage_act3");
        await Until(() => gs.HasFlag("harrington_unmasked"));
        var unmasked = game.Room?.FindActor("harrington");
        Check(!game.Hud.InsetVisible && unmasked != null && game.Room?.FindActor("leader") == null
              && unmasked.Texture?.ResourcePath == "res://assets/art/sprites/leader_unmasked.png",
            "the stag takes off his mask in front of everyone: Harrington senior, close-up gone");
        await game.Wait(1);
        await Shot("club_stage_unmasked");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Power that never shows itself"));
        Check(game.Hud.SpeechText.Contains("rumour"), "Harrington says the meeting is only the exercise of his power");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.StartsWith("I am where I belong", StringComparison.Ordinal));
        Check(game.Hud.SpeechText == "I am where I belong, Mr. Jones.", "Eleanor answers flatly, like a recording");
        await Until(() => gs.HasFlag("brute_stage"));
        Check(_insetAtCaughtChoice == false, "the close-up is removed before the revolver choice");
        await game.Wait(1);
        await Shot("club_stage_brute");
        await Until(() => game.Room?.Name == "ChurchExterior");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText.StartsWith("Cathedral steps.", StringComparison.Ordinal));
        Check(!game.Hud.InsetVisible, "Micah's first line on the steps comes before his close-up");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Beaten && game.Hud.InsetName == "beaten_closeup", "Micah's close-up framed over the cathedral steps while he lies there");
        await Until(() => game.Hud.ThoughtVisible);
        Check(game.Hud.InsetVisible && !game.Hud.SpeechVisible && game.Hud.ThoughtRect.Position.Y < 20 &&
            game.Hud.ThoughtRect.End.Y < game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.3f,
            "his thoughts sit along the top, clear of his face, while the close-up is up");
        await game.Wait(1.5);
        await Shot("church_exterior_beaten");
        await Until(() => game.Room?.Name == "Office");
        Check(_insetAtBeatenChoice == false, "Micah's close-up is removed before he gets up and chooses");
        await game.Wait(1.5);
        Check(game.Player.Visible && game.Player.Facing == Facing.Up && game.Player.Position.X > 380,
            "Act 3 office: Micah talks at the window, his back to the room");
        Check(gs.HasFlag("office_lamp_off") && game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("office_act3.png") == true,
            "Act 3 office is dim, the lamp off and the whiskey on the desk");
        await Shot("office_act3_window");
        await stage;
        await WaitIdle(game);
        Check(_poseCounts.GetValueOrDefault("micah_masked_collapse") == 1, "masked collapse ran on the revolver branch");
        Check(!game.Player.Poses.Active, "recovery restored the walking sprite before returning control");
        Check(game.Room?.Name == "Office" && !gs.HasFlag("micah_at_desk"), "Act 3 office returns player control");
        _prefer = new[] { "Visit Caleb", "Refuse the cross" };
        int offers = _crossOffers;
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "Office" && gs.HasFlag("church_act3_return") && !gs.HasItem("cross") && _crossOffers == offers + 1,
            "Act 3 Caleb visit offers cross, refusal returns to office");
        await game.Perform(Verb.Walk, "door");
        Check(_crossOffers == offers + 2 && !gs.HasItem("cross"), "Caleb offers again after refusal");
        _prefer = new[] { "Visit Caleb", "Accept the cross" };
        await game.Perform(Verb.Walk, "door");
        Check(gs.HasItem("cross") && gs.HasFlag("took_cross") && gs.Inventory.Count(i => i == "cross") == 1,
            "accepted pendant is recorded and given once");
        await game.Perform(Verb.Walk, "door");
        Check(_crossOffers == offers + 3 && game.Room?.Name == "Office" && !gs.HasFlag("micah_at_desk"),
            "accepted cross isn't offered again, desk scene isn't replayed");
        var savedCommitments = game.CaptureSave();
        Check(SaveSerializer.TryDeserialize(SaveSerializer.Serialize(savedCommitments))?.Inventory.Contains("cross") == true,
            "accepted pendant survives save serialization");
        gs.TakeItem("cross");
        await game.LoadGame(savedCommitments);
        Check(gs.HasItem("cross") && gs.HasItem("faith_ring") && gs.HasFlag("ring_taken_act2") && game.Room is Rooms.Office,
            "load restores ring, pendant and initial decision without replaying the desk");
        _prefer = new[] { "Go to the Blue Lantern" };
        await game.Perform(Verb.Walk, "door");
        Check(gs.HasFlag("keep_going") && !gs.HasFlag("masked") && gs.HasFlag("alley3"), "Micah keeps going: from his desk to the Blue Lantern");
        // the seeded endings add Eleanor's refusals themselves
        var act3Flags = _act3Flags = gs.Flags.Where(f => f is not (Endings.RefusedAbbess or Endings.RefusedDrugs)).ToArray();
        var act3Items = _act3Items = gs.Inventory.ToArray();
        _act3Ink = DialogueManager.Instance.SaveInk();

        // ---- the alley: break the lamp, lure Sal out, knock him down, and bring Tony out
        await Shot("alley_act3");
        int stoneSteps = game.Sfx.Count(Sound.StepStone), knocks = game.Sfx.Count(Sound.Knock);
        int gunshots = game.Sfx.Count(Sound.Gunshot);
        await game.Perform(Verb.Talk, "back_door");
        Check(!gs.HasFlag("shot_bartender"), "not knocking with Sal inside");
        await game.Perform(Verb.Kick, "trash");
        Check(!gs.HasFlag("alley3_sal_out"), "no luring Sal out under the lamp");
        await game.Perform(Verb.Hand, "street_lamp");
        Check(gs.HasFlag("alley3_dark"), "broke the street lamp");
        Check(game.Sfx.Count(Sound.StepStone) > stoneSteps, "Micah's shoes sound on the alley cobbles");
        await Shot("alley_dark");
        await game.Perform(Verb.Kick, "trash");
        Check(gs.HasFlag("alley3_sal_out") && !gs.HasFlag("alley3_sal_inside"), "the noise brings Sal out");
        Check(game.Sfx.Count(Sound.Crash) > 0, "the trash cans go over with a crash");
        await Shot("alley_sal_out");
        CheckActorWins(game, "sal", "trash", "Sal, out by the trash cans, wins the hover over them (#97)");
        await game.Perform(Verb.UseItem, "sal", "revolver");
        Check(gs.HasFlag("alley3_sal_down"), "pistol-whipped Sal");
        Check(game.Room?.FindActor("sal") is { } downSal && downSal.Texture?.ResourcePath.EndsWith("sal_out.png") == true &&
            !downSal.Poses!.Active, "Sal goes down on his knees and ends face-down");
        await Shot("alley_sal_down");
        _prefer = Convinces.Prepend("Shoot him").ToArray();
        var tonyTalk = game.Perform(Verb.Talk, "back_door");
        await Until(() => gs.HasFlag("shot_bartender") && game.Room?.FindActor("bartender") is { } t &&
            t.Texture?.ResourcePath.EndsWith("bartender_shot.png") == true);
        Check(game.Room?.FindActor("bartender")?.Texture?.ResourcePath.EndsWith("bartender_shot.png") == true,
            "Tony falls, shot in the shoulder, and stays down on his back");
        await Shot("alley_tony_shot");
        Check(game.Sfx.Count(Sound.Knock) >= knocks + 3, "Sal's knock is heard: two, a pause, and one");
        Check(game.Sfx.Count(Sound.Gunshot) == gunshots + 1, "the revolver goes off once");
        await tonyTalk;
        Check(Offered("bartender_gun", "Lower the gun"), "Caleb's counsel lets Micah walk away from Tony");
        Check(gs.HasFlag("shot_bartender") && game.Room?.Name == "OfficeStorm", "shot Tony in the shoulder, back to the office in the storm");

        // ---- the office in the storm: the confession, the demon in the window, the hat, and out to the mansion
        if (game.Room is Rooms.OfficeStorm storm)
        {
            Check(gs.HasFlag("storm_confessed") && storm.DemonFlashes == 2, "two flashes show the demon in the window");
            Check(game.Sfx.Count(Sound.Thunder) > 0, "thunder follows the lightning");
            Check(game.Player.Character == "micah_hatless_bottle", "hatless, the bottle in his hand");
            Check(!storm.GetNode<Godot.CanvasItem>("Lightning/Demon1").Visible &&
                !storm.GetNode<Godot.CanvasItem>("Lightning/Demon2").Visible, "the demon is gone once it's dark");
        }
        await Shot("office_storm");
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "OfficeStorm" && !gs.HasFlag("storm_door_open"), "not out of the door without the hat");
        await game.Perform(Verb.Hand, "hat");
        Check(gs.HasFlag("storm_bottle_down") && gs.HasFlag("storm_hat_on") && game.Player.Character == "micah",
            "the bottle stays on the desk, the hat goes on");
        await Shot("office_storm_hat_on");
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "MansionExterior", "out of the office, on to the Harrington mansion");
        Check(game.Music.Current == Track.MansionDread, "the mansion's dread starts outside the house");
        int dreadStarts = game.Music.Count(Track.MansionDread);

        // ---- the mansion: the alarm bell, the key, the study, the bedroom
        await Shot("mansion_exterior");
        await game.Perform(Verb.Hand, "bell");
        await game.Perform(Verb.Look, "door");
        Check(gs.HasFlag("alarm_noticed"), "spotted the alarm wire");
        await game.Perform(Verb.Hand, "lintel");
        Check(gs.HasItem("kitchen_key"), "the key on the lintel");
        await game.Perform(Verb.Hand, "door");
        await game.Perform(Verb.Hand, "bell");
        Check(game.Room?.Name == "MansionExterior" && !gs.HasFlag("bell_wedged"), "the bell is out of reach");
        await game.Perform(Verb.Hand, "bin");
        Check(gs.HasFlag("bin_moved"), "moved the coal bin under the bell");
        await ReloadCheckpoint("alarm_unrestrained");
        Check(!gs.HasFlag("bell_wedged"), "save/load does not restrain a new alarm");
        await CancelPuzzle(() => game.Perform(Verb.Hand, "bell"), PuzzleKind.Bell, "bell_wedged", "alarm_restraint");
        await SolvePuzzle(() => game.Perform(Verb.Hand, "bell"), PuzzleKind.Bell,
            new[] { ("s1", 1), ("s2", 2) }, "alarm_restraint");
        Check(gs.HasFlag("bell_wedged"), "gagged the bell with the tie");
        Check(game.Player.Character == "micah_no_tie", "Micah has left his tie on the bell");
        await Shot("mansion_exterior_wedged");
        await game.Perform(Verb.Hand, "door");
        Check(game.Room?.Name == "MansionKitchen" && !gs.HasItem("kitchen_key"), "in through the kitchen, quietly");
        Check(game.Player.Character == "micah_no_tie", "still without his tie in the next room");
        await Shot("mansion_kitchen");
        await game.Perform(Verb.Hand, "range");
        await game.Perform(Verb.Hand, "back_door");
        Check(game.Room?.Name == "MansionKitchen", "no leaving without Eleanor");
        await game.Perform(Verb.Walk, "baize_door");
        Check(game.Room?.Name == "MansionKitchen" && !gs.HasFlag("baize_unbolted"), "the baize door is bolted from the house side");
        // ---- the wine cellar: a lantern, kerosene and the lighter light the bootleggers' stair up to the study
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionCellar" && !gs.HasFlag("cellar_lit"), "down the trapdoor into the dark cellar");
        await Shot("mansion_cellar_dark");
        await game.Perform(Verb.Walk, "stair");
        Check(game.Room?.Name == "MansionCellar", "no climbing the cellar stair blind");
        await game.Perform(Verb.Hand, "lantern");
        await game.Perform(Verb.Hand, "crates");
        Check(gs.HasItem("lantern") && gs.HasItem("kerosene") && gs.HasItem(MicahKit.LighterId), "lantern off the hook, kerosene off the crates, lighter in pocket");
        await Shot("mansion_cellar_taken");
        await CombineAndWait("lantern", MicahKit.LighterId);
        Check(gs.HasItem("lantern") && !gs.HasItem("lantern_filled") && !gs.HasItem("lantern_lit") && gs.HasItem(MicahKit.LighterId),
            "a dry wick won't light");
        await CombineAndWait("lantern", "kerosene");
        Check(gs.HasItem("lantern_filled") && !gs.HasItem("lantern") && !gs.HasItem("kerosene"), "filled the lantern");
        await CombineAndWait("lantern_filled", MicahKit.LighterId);
        Check(gs.HasItem("lantern_lit") && gs.HasFlag("lantern_lit") && gs.HasItem(MicahKit.LighterId), "lit the lantern; the lighter is kept");
        await game.Perform(Verb.UseItem, "stair", "lantern_lit");
        Check(gs.HasFlag("cellar_lit") && !gs.HasItem("lantern_lit"), "the lantern hung at the stair foot lights the cellar");
        await Shot("mansion_cellar_lit");
        await game.Perform(Verb.Hand, "barrel");
        await game.Perform(Verb.Hand, "hung_lantern");
        Check(!gs.HasFlag("barrel_open") && !gs.HasFlag("took_hung_lantern") && !gs.HasItem("lantern_lit"),
            "the whiskey and the hung lantern wait for the escape");
        await game.Perform(Verb.Walk, "stair");
        Check(game.Room?.Name == "MansionStudy", "up the bootleggers' stair into the study");
        Check(game.Music.Current == Track.MansionDread && game.Music.Count(Track.MansionDread) == dreadStarts,
            "the dread plays on unbroken through the kitchen, the cellar and the study");
        await Shot("mansion_study_hatch");
        await game.Perform(Verb.Walk, "door_left");
        Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("baize_unbolted"), "unbolted the baize door from the study side");
        await game.Perform(Verb.Walk, "baize_door");
        Check(game.Room?.Name == "MansionStudy", "into the study");
        await Shot("mansion_study");
        await game.Perform(Verb.Hand, "drawer_right");
        await Shot("mansion_study_drawer");
        await game.Perform(Verb.Hand, "documents");
        Check(gs.HasItem("audit_folder") && !gs.HasItem("documents") && !gs.HasFlag(Endings.TookDocuments),
            "account register alone is not incriminating evidence");
        await game.Perform(Verb.Hand, "drawer_left");
        Check(gs.HasItem("audit_tracing"), "matching index found under the cigars");
        await ReloadCheckpoint("audit_unsolved");
        Check(!gs.HasFlag(Endings.TookDocuments) && gs.HasItem("audit_folder") && gs.HasItem("audit_tracing"),
            "both audit clues survive save/load without granting evidence");
        await CancelPuzzle(() => CombineAndWait("audit_tracing", "audit_folder"), PuzzleKind.Alignment, "audit_identified", "audit_alignment");
        await SolvePuzzle(() => CombineAndWait("audit_folder", "audit_tracing"), PuzzleKind.Alignment,
            new[] { ("rotate", 1), ("right", 6), ("down", 3) }, "audit_alignment");
        Check(gs.HasFlag(Endings.TookDocuments) && gs.HasItem("documents"), "index identifies signed payoff sheets");
        var confront = game.Perform(Verb.Walk, "door_right");
        await Until(() => game.Room?.Name == "MansionBedroom");
        await game.Wait(1.5);
        await Until(() => game.Hud.SpeechVisible && game.Room?.Name == "MansionBedroom");
        var mansionLine = game.Hud.SpeechText;
        Check(game.Hud.SpeechVisible && !confront.IsCompleted, "Act Three confrontation is speaking before pause");
        PressKey(Key.Space);
        // Longer than the longest unpaused line (7s) at the current scale, so a failed pause would have finished.
        await Observe(7.0 / Engine.TimeScale + 0.2);
        Check(game.IsPaused && game.Hud.SpeechVisible && game.Hud.SpeechText == mansionLine
            && !confront.IsCompleted && game.Room?.Name == "MansionBedroom",
            "Space freezes the Act Three confrontation mid-sentence");
        PressKey(Key.Space);
        Check(game.Player.Visible && game.Player.Position.DistanceTo(new Vector2(106, 222)) < 2,
            "Micah listens beside the folded, edge-on screen, in full view, the screen between him and the bed (#104)");
        Check(game.Player.PoseName == "micah_crouched" && _poseCounts.GetValueOrDefault("micah_crouch") == 1,
            "Micah crouches down behind the screen and holds the crouch while he listens");
        await Shot("mansion_bedroom");
        int draws = _poseCounts.GetValueOrDefault("micah_draw");
        await Until(() => gs.HasFlag("eleanor_up"));
        Check(game.Player.Visible && game.Player.Position.DistanceTo(new Vector2(160, 236)) < 2,
            "Micah walks out from behind the screen to take aim (#104)");
        Check(_poseCounts.GetValueOrDefault("micah_crouch_rise") == 1 && game.Player.PoseName == "micah_aim",
            "Micah stands back up before stepping out, so the crouch is released");
        Check(_poseCounts.GetValueOrDefault("micah_draw") == draws + 1, "Micah draws the revolver from under his coat");
        Check(game.Player.Poses.Source == "micah_no_tie_aim", "Micah aims without his tie");
        await game.Wait(0.5);
        await Shot("mansion_bedroom_gun");
        await confront;
        await WaitIdle(game);
        Check(Offered("oldman_taunt", "Our Father") == Endings.CanSpareOldMan(gs.HasFlag, gs.HasItem), "sparing the old man follows Caleb, Rose, ring and cross");
        Check(gs.HasFlag("shot_oldman") && gs.HasFlag("eleanor_convinced") && game.Room?.Name == "MansionKitchen", "shot the old man; Eleanor comes along after the four right lines");
        await Shot("mansion_kitchen_escape");
        await game.Perform(Verb.Walk, "baize_door");
        Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("escaping"), "no going back through the baize door during the escape");
        var rangeLines = await Listen(game, game.Perform(Verb.Hand, "range"));
        var candleLines = await Listen(game, game.Perform(Verb.Hand, "candle"));
        Check(game.Room?.Name == "MansionKitchen" && !gs.HasFlag(Endings.MansionExploded) &&
              rangeLines.Concat(candleLines).Count(l => l.Contains("all that alcohol in the cellar")) == 2,
            "the range and the candle stay selectable, and Micah steers himself to the cellar whiskey");
        // ---- the fire: down to the cellar while Eleanor waits, open the whiskey, the hung lantern onto it
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionCellar", "back down to the cellar during the escape");
        await game.Perform(Verb.Walk, "stair");
        Check(game.Room?.Name == "MansionCellar", "the bootleggers' stair stays shut during the escape");
        await game.Perform(Verb.Walk, "kitchen_steps");
        Check(game.Room?.Name == "MansionKitchen" && game.Room?.FindHotspot("eleanor")?.Visible == true && !gs.HasFlag("cellar_fire"),
            "back up the steps without lighting anything: Eleanor still waits by the door");
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionCellar", "and down again: the trapdoor stays open until the fire");
        await game.Perform(Verb.Hand, "hung_lantern");
        Check(gs.HasFlag("took_hung_lantern") && gs.HasItem("lantern_lit"), "the lit lantern off its nail");
        await ReloadCheckpoint("the cellar mid-escape, lantern in hand");
        Check(game.Room?.Name == "MansionCellar" && gs.HasFlag("escaping") && gs.HasItem("lantern_lit") &&
              game.Room?.FindHotspot("hung_lantern")?.Visible != true,
            "a save in the cellar mid-escape restores the lantern in hand, off its nail");
        await game.Perform(Verb.UseItem, "barrel", "lantern_lit");
        Check(!gs.HasFlag("cellar_fire") && gs.HasItem("lantern_lit"), "a closed barrel won't burn");
        await game.Perform(Verb.UseItem, "barrel", MicahKit.LighterId);
        await game.Perform(Verb.Hand, "barrel");
        Check(gs.HasFlag("barrel_open") && !gs.HasFlag("cellar_fire"), "the whiskey runs out over the floor");
        await ReloadCheckpoint("the cellar mid-escape, whiskey running");
        Check(game.Room?.Name == "MansionCellar" && gs.HasFlag("barrel_open") && gs.HasItem("lantern_lit") && !gs.HasFlag("cellar_fire"),
            "a save with the whiskey running restores the open barrel and the lantern in hand");
        await Shot("mansion_cellar_whiskey");
        var fire = game.Perform(Verb.UseItem, "barrel", "lantern_lit");
        await Until(() => gs.HasFlag("cellar_fire"));
        await game.Wait(1.0);
        await Shot("mansion_cellar_fire");
        await fire;
        await WaitIdle(game);
        Check(game.Room?.Name == "MansionKitchen" && !gs.HasItem("lantern_lit"), "up out of the burning cellar, the lantern left in the fire");
        await ReloadCheckpoint("the kitchen after the cellar fire");
        Check(game.Room?.Name == "MansionKitchen" && gs.HasFlag("cellar_fire") && gs.HasFlag("escaping") &&
              game.Room?.FindHotspot("eleanor")?.Visible == true,
            "a save in the kitchen after the fire restores the fire and Eleanor waiting by the door");
        await game.Perform(Verb.Walk, "cellar_door");
        Check(game.Room?.Name == "MansionKitchen", "no going back down into the fire");
        HeardLog = new List<string>();
        _ = game.Perform(Verb.Walk, "back_door");
        await Until(() => gs.HasFlag(Endings.MansionExploded));
        await game.Wait(1.5);
        await Shot("mansion_fire");
        await Until(() => game.Room?.Name == "Outskirts");
        Check(gs.HasFlag("ending_2"), "ending 2: out of town, together");
        Check(game.Music.Current != Track.MansionDread && game.Music.Count(Track.MansionDread) == dreadStarts,
            "the dread played through the whole mansion, bedroom included, and stops once out of it");
        Check(HeardLog.Any(l => l.Contains("Oh my God, Micah.")) && !HeardLog.Any(l => l.Contains("She watches the windows go.")),
            "ending 2: convinced Eleanor cries out when the house goes");
        await game.Wait(3);
        await Shot("ending_together");
        await TheEnd("ending_2");
        Check(HeardLog.Any(l => l.Contains("She told me the rest of it in the car that night")) &&
              !HeardLog.Any(l => l.Contains("motel on the road")) && !HeardLog.Any(l => l.Contains("changed in mine on the way")),
            "ending 2: Daniel's journal puts the telling in the car, not a motel on the road; no weary-road dress beat");
        HeardLog = null;
    }
}
