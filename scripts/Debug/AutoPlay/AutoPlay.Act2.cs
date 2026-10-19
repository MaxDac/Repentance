using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Act 2 of the autoplay run.</summary>
public partial class AutoPlay
{
    /// <summary>
    /// The First Interlude: Eleanor's last hour at the Aurelian, the Blue Lantern, the convent (indulging Agatha this time;
    /// the playthrough refuses her) and the motel window, then Micah's journal again on the fire escape and in her room.
    /// </summary>
    private async Task FirstInterlude(Game game, GameState gs)
    {
        await Until(() => game.Hud.CaptionVisible && game.Hud.CaptionText == "Chicago, 1927.", 20);
        Check(!game.Hud.CaptionSubVisible, "Act 2 opens on black with \"Chicago, 1927.\" alone");
        await Until(() => game.Hud.CaptionSubVisible && game.Hud.CaptionSubText == "First Interlude", 10);
        Check(game.Hud.CaptionVisible && game.Hud.CaptionText == "Chicago, 1927.",
            "\"First Interlude\" appears under \"Chicago, 1927.\" on the same black screen");
        await Until(() => game.Room?.Name == "EleanorRoom");
        await WaitIdle(game);
        Check(gs.HasFlag("interlude1") && game.Player.Character == "eleanor_play", "the player is Eleanor in Room 507");
        Check(game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("eleanor_room_interlude.png") == true,
            "Room 507 is still in order: Theodore's men search it only after she has gone");
        Check(game.Hud.SatchelVisible && gs.Inventory.Count == 0 && !gs.HasItem("revolver") && !gs.HasItem("journal"),
            "Micah's things (and Daniel's journal) are put away; Eleanor's satchel starts empty");
        await game.ItemVerb(Verb.Hand, Notes.ItemId);
        Check(!game.Hud.Notepad.Visible, "Micah's notepad doesn't open for Eleanor");
        await game.Wait(0.5);
        await Shot("interlude_aurelian");
        var leaving = await Spoken(() => game.Perform(Verb.Walk, "exit"));
        Check(game.Room?.Name == "EleanorRoom" && leaving.Contains("Not yet. The box goes in the safe first."),
            "Eleanor won't leave before the call and the locks; the safe comes first");
        await game.Perform(Verb.Hand, "closet");
        Check(!gs.HasFlag("interlude_safe_locked"), "the safe waits for the packed box");
        await LegacyPackedBox(game, gs);
        // Puzzle 17: wrong joins first, then the box packed and locked away
        await game.Perform(Verb.Hand, "vanity");
        Check(gs.HasItem("eleanor_box") && gs.HasItem("pellet"), "the open brass box and the bare paper flower from the vanity");
        await CombineAndWait("pellet", "eleanor_box");
        Check(gs.HasItem("pellet") && gs.HasItem("eleanor_box") && !gs.HasFlag("interlude_box_packed"), "a bare pellet won't go in the box");
        await game.Perform(Verb.Hand, "desk");
        await CombineAndWait("pellet", "riddle_scrap");
        Check(gs.HasItem("pellet") && gs.HasItem("riddle_scrap") && !gs.HasItem("eleanor_flower"), "the riddle won't stay on without thread");
        await game.Perform(Verb.Hand, "clothes");
        await CombineAndWait("red_thread", "pellet");
        Check(gs.HasItem("red_thread") && gs.HasItem("pellet"), "thread round a bare pellet is refused");
        await CombineAndWait("riddle_scrap", "pellet");
        Check(gs.HasItem("eleanor_flower") && !gs.HasItem("pellet") && !gs.HasItem("riddle_scrap") && !gs.HasItem("red_thread"),
            "the riddle tied round the flower uses up the thread");
        await game.Perform(Verb.Hand, "vanity");
        await game.Perform(Verb.Hand, "desk");
        await game.Perform(Verb.Hand, "clothes");
        Check(gs.Inventory.Count == 2 && !gs.HasItem("pellet") && !gs.HasItem("riddle_scrap") && !gs.HasItem("red_thread"),
            "the vanity, the desk and the dress give nothing twice");
        await game.Perform(Verb.UseItem, "closet", "eleanor_flower");
        Check(!gs.HasFlag("interlude_safe_locked") && gs.HasItem("eleanor_flower"), "the flower alone doesn't go in the safe");
        await ReloadCheckpoint("first_interlude_flower");
        Check(gs.HasItem("eleanor_flower") && gs.HasItem("eleanor_box") && game.Hud.SatchelVisible, "a save holding the wrapped flower loads back");
        await CombineAndWait("eleanor_flower", "eleanor_box");
        Check(gs.HasItem("eleanor_box_packed") && gs.HasFlag("interlude_box_packed") && gs.Inventory.Count == 1, "the flower packed in the box");
        await game.Perform(Verb.Hand, "closet");
        Check(!gs.HasFlag("interlude_safe_locked") && gs.HasItem("eleanor_box_packed"), "the box has to be put in the safe, not just the hand");
        await ReloadCheckpoint("first_interlude_packed");
        Check(gs.HasItem("eleanor_box_packed") && !gs.HasFlag("interlude_safe_locked"), "a save holding the packed box loads back");
        await game.Perform(Verb.UseItem, "closet", "eleanor_box_packed");
        Check(gs.HasFlag("interlude_safe_locked") && gs.Inventory.Count == 0, "the packed box locked in the closet safe");
        var early = await Spoken(() => game.Perform(Verb.Hand, "telephone"));
        Check(!gs.HasFlag("interlude_phoned") && early.Contains("Not yet. The box in the safe, the riddle in the drawer. Then I call."),
            "no call before the riddle is locked in the drawer");
        leaving = await Spoken(() => game.Perform(Verb.Walk, "exit"));
        Check(game.Room?.Name == "EleanorRoom" && leaving.Contains("Not yet. Nothing of mine stays out in the open for them."),
            "with the safe locked, the exit points to the drawer");
        var drawerLook = await Spoken(() => game.Perform(Verb.Look, "desk_drawer"));
        Check(!gs.HasFlag("interlude_drawer_locked") && !gs.HasFlag("interlude_phoned") &&
              drawerLook.Contains("The safe's locked. Now the riddle goes in this drawer, and I turn the key.") &&
              !drawerLook.Contains("Locked, with the riddle inside."),
            "looking at the empty drawer after the safe asks for the riddle, not claims it's inside");
        await game.Perform(Verb.Hand, "desk_drawer");
        drawerLook = await Spoken(() => game.Perform(Verb.Look, "desk_drawer"));
        Check(gs.HasFlag("interlude_drawer_locked") && drawerLook.Contains("Locked, with the riddle inside."),
            "once the riddle is in, the drawer says so");
        leaving = await Spoken(() => game.Perform(Verb.Walk, "exit"));
        Check(game.Room?.Name == "EleanorRoom" && leaving.Contains("Not yet. Nobody's coming for me unless I call."),
            "with the drawer locked, the exit points to the call");
        Check(game.Room?.FindHotspot("telephone")?.Visible == true && game.Room?.FindHotspot("fallen_telephone")?.Visible == false
              && game.Room?.GetNodeOrNull<Sprite2D>("InterludeTelephone")?.Visible == true,
            "the candlestick telephone stands on the vanity, not on the floor");
        int calls = _poseCounts.GetValueOrDefault("eleanor_phone"), hangups = _poseCounts.GetValueOrDefault("eleanor_phone_down");
        await game.Perform(Verb.Hand, "telephone");
        Check(gs.HasFlag("interlude_phoned") && gs.HasFlag("interlude_drawer_locked"), "the box in the safe, the riddle in the drawer, the call made");
        Check(_poseCounts.GetValueOrDefault("eleanor_phone") == calls + 1 && _poseCounts.GetValueOrDefault("eleanor_phone_down") == hangups + 1
              && game.Player.PoseName == null && game.Room?.GetNodeOrNull<Sprite2D>("InterludeTelephone")?.Visible == true,
            "Eleanor lifts the telephone for the call and hangs it back on the vanity");
        await ReloadCheckpoint("first_interlude");
        Check(game.Player.Character == "eleanor_play" && gs.HasFlag("interlude1"), "a save inside the interlude loads back as Eleanor");
        await game.Perform(Verb.Walk, "exit");
        await WaitIdle(game);
        Check(game.Room?.Name == "Speakeasy", "Sal takes her down to the Blue Lantern");
        await Shot("interlude_lantern");
        await game.Perform(Verb.Talk, "bartender");
        await WaitIdle(game);
        Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("interlude_agatha_met"), "Tony sends her to the convent; Agatha meets her");
        await Shot("interlude_corridor");
        await game.Perform(Verb.Walk, "cell_door");
        Check(game.Room?.Name == "ConventCell", "to her cell");
        Check(game.Room?.FindActor("nun") is { Visible: false }, "Eleanor is alone in the cell until the knock");
        Check(game.Music.Current == Track.ConventPiano, "the convent piano plays in the cell before the knock");
        int pianoBeforeVisit = game.Music.Count(Track.ConventPiano);
        var prefer = _prefer;
        _prefer = new[] { "(Seduce her." };
        var night = game.Perform(Verb.Hand, "bed");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("You're awake"));
        Check(game.Room?.FindActor("nun") is { Visible: true } agatha && agatha.Position.X > 200,
            "Agatha is in the cell, by the bed, while she talks");
        Check(game.Music.Current == Track.ClubStrings, "the Club's strings play for Agatha's night visit");
        await Shot("interlude_agatha_night");
        await night;
        await WaitIdle(game);
        Check(game.Music.Count(Track.ConventPiano) == pianoBeforeVisit + 1,
            "the convent piano comes back once Agatha has gone");
        _prefer = prefer;
        Check(Offered("interlude_agatha_night", "(Tell her the truth.") && !gs.HasFlag(Endings.RefusedAbbess),
            "the night visit offers the truth; seducing her saves nothing");
        Check(game.Room?.Name == "MotelNight" && game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("motel_empty.png") == true,
            "the next morning, the motel with an empty bed");
        await Shot("interlude_motel");
        _ = game.Perform(Verb.Hand, "window");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText.Contains("fishing for the fire-escape ladder"), 90);
        Check(game.Room?.Name == "MotelNight", "from the window Eleanor sees Micah climbing to the fire escape");
        bool captionOnWayBack = false;
        await Until(() =>
        {
            captionOnWayBack |= game.Hud.CaptionVisible;
            return game.Room is Rooms.MotelFireEscape;
        }, 90);
        Check(!captionOnWayBack && !gs.HasFlag("interlude1") && game.Player.Character.StartsWith("micah") && gs.HasItem("revolver"),
            "the First Interlude ends on black with no caption, and Micah's journal takes the story back on the fire escape");
        await FireEscapeNight(game, gs);
        await Until(() => game.Room?.Name == "MotelNight" && game.Player.Character == "micah_dressing");
        Check(!gs.HasFlag("interlude1") && gs.HasItem("revolver"),
            "later that night, the motel room, with Micah's things");
        Check(game.Room?.GetNode<Sprite2D>("Background").Texture.ResourcePath.EndsWith("motel_night.png") == true,
            "Eleanor is in the bed again");
        Check(game.Music.Current == Track.OfficeJazz, "the office jazz plays again in Eleanor's room");
        await game.Wait(2);
        await Shot("motel_night");
        await Until(() => game.Room?.Name == "Office");
        Check(!gs.HasFlag("interlude1") && game.Player.Character.StartsWith("micah") && gs.HasItem("revolver"),
            "Micah's journal takes the story back, with his things");
        Check(game.Hud.SatchelVisible, "the satchel is back for Micah");
        Check(!new[] { "eleanor_box", "pellet", "riddle_scrap", "red_thread", "eleanor_flower", "eleanor_box_packed" }.Any(gs.HasItem)
            && !gs.HasFlag("interlude_took_box") && !gs.HasFlag("interlude_took_thread"),
            "nothing of Eleanor's, and none of her puzzle flags, follow Micah out of the interlude");
    }

    /// <summary>
    /// After the First Interlude: Micah is already in front of Eleanor on the landing; she repeats her Act 1 question,
    /// the two-portrait close-up, the compensation choice, the slow approach and the kiss, then a 3-second fade.
    /// </summary>
    private async Task FireEscapeNight(Game game, GameState gs)
    {
        const string opening = "Not many fellas climb a fire escape in the rain, mister. Were you looking for someone?";
        var her = game.Room!.FindActor("eleanor")!.Position;
        Check(game.Player.Position.DistanceTo(her + new Vector2(-44, 4)) < 1f && game.Room.FindActor("eleanor")!.Visible,
            "Micah is already standing in front of Eleanor, where Act 1 left them");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == opening);
        Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn, "Eleanor repeats her opening, word for word, before the close-up");
        Check(game.Music.Current == Track.OfficeJazz, "the office jazz plays on the fire escape with Eleanor");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.FireEscape && game.Hud.InsetName == "fire_escape_closeup",
            "the two-portrait close-up appears immediately after Eleanor's opening");
        Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "the two-portrait close-up fills most of the screen");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Eleanor Harrington. You wouldn't happen to know her?");
        CheckPortraitSpeech(game, right: false);
        await Shot("convent_portrait_micah");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Tony's boys"));
        CheckPortraitSpeech(game, right: true);
        await Shot("convent_portrait_eleanor");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Twenty a day. I used to spend that on gloves.");
        Check(!game.Hud.InsetDrawn, "the compensation answer rejoins the existing conversation on the fire escape");
        Check(_closeUpAtRoadChoice == null, "Micah answers the compensation choice without a portrait panel");
        await Shot("motel_fire_escape");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("can't go back"));
        Check(game.Hud.CurrentCloseUp == null && !game.Hud.InsetDrawn && game.Room is Rooms.MotelFireEscape,
            "the rest of Eleanor's conversation stays on the fire escape without the panel");
        float talkingX = game.Player.Position.X;
        int kisses = _poseCounts.GetValueOrDefault("micah_kiss");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == "Then stay. Right here.");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.StartsWith("You're walking into the rain"));
        await game.Wait(0.5);
        Check(game.Player.IsWalking && game.Player.Position.X > talkingX && game.Player.PoseName == null &&
            !game.Hud.InsetVisible && !game.Hud.InsetDrawn,
            "Micah walks slowly towards Eleanor, with no portrait panel, as she answers him");
        await Shot("fire_escape_closer");
        const string attraction = "I'd have climbed a hundred fire escapes for that. Some things a man doesn't decide. They decide him.";
        const string guilt = "And somewhere across town Rose was waiting up for me, the way she always did. I kissed Eleanor anyway.";
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText == attraction);
        var eleanorActor = game.Room!.FindActor("eleanor")!;
        Check(game.Player.PoseName == "micah_kiss" && _poseCounts.GetValueOrDefault("micah_kiss") == kisses + 1 &&
            !eleanorActor.Visible, "Micah reaches Eleanor after her rain line and kisses her");
        Check(game.Player.Position.DistanceTo(her + Rooms.MotelFireEscape.KissSpot) < 1f,
            "he stands right in front of her for the kiss");
        Check(game.Hud.FadeAlpha == 0f, "the kiss is seen before any fade");
        await Shot("fire_escape_kiss");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText == guilt);
        Check(game.Player.PoseName == "micah_kiss" && game.Hud.FadeAlpha == 0f,
            "the kiss holds while Micah thinks of Rose, still before the fade");
        double scale = Engine.TimeScale;
        Engine.TimeScale = 1;
        try
        {
            await Until(() => !game.Hud.ThoughtVisible && game.Hud.FadeAlpha > 0f, step: 0.02);
            ulong fadeStart = Time.GetTicksMsec();
            await Until(() => game.Hud.FadeAlpha > 0.3f, step: 0.02);
            Check(game.Player.PoseName == "micah_kiss", "the fade to black takes them in the kiss");
            await Until(() => game.Hud.FadeAlpha >= 1f, step: 0.02);
            double fadeOut = (Time.GetTicksMsec() - fadeStart) / 1000.0;
            await Until(() => game.Hud.CaptionVisible, step: 0.02);
            Check(game.Hud.CaptionText == "Later that night" && game.Hud.FadeAlpha >= 0.99f && game.Room is Rooms.MotelFireEscape,
                "after the kiss, \"Later that night\" on black");
            ulong captionStart = Time.GetTicksMsec();
            await Shot("later_that_night");
            await Until(() => !game.Hud.CaptionVisible, step: 0.02);
            double caption = (Time.GetTicksMsec() - captionStart) / 1000.0;
            await Until(() => game.Room is Rooms.MotelNight && game.Hud.FadeAlpha < 1f, step: 0.02);
            ulong fadeInStart = Time.GetTicksMsec();
            await Until(() => game.Hud.FadeAlpha <= 0f, step: 0.02);
            double fadeIn = (Time.GetTicksMsec() - fadeInStart) / 1000.0;
            Check(fadeOut is > 2.5 and < 3.6 && caption is > 2.5 and < 3.6 && fadeIn is > 2.5 and < 3.6,
                $"3s fade to black, 3s \"Later that night\", 3s fade into her room (took {fadeOut:0.0}s, {caption:0.0}s, {fadeIn:0.0}s)");
        }
        finally { Engine.TimeScale = scale; }
    }

    /// <summary>
    /// A save from before Puzzle 17 holds "interlude_box_packed" with no box in the satchel: the closet hand still
    /// locks it, so the old save can finish. The run resumes from where it was.
    /// </summary>
    private async Task LegacyPackedBox(Game game, GameState gs)
    {
        await WaitIdle(game);
        Check(game.SaveToSlot(SaveSystem.ManualSlot(2)), "saved before the legacy box check");
        var resume = SaveSystem.Read(SaveSystem.ManualSlot(2));
        var legacy = new SaveData
        {
            Room = "eleanor_room", RoomTitle = "Aurelian Hotel", StoryAct = 2, X = 300, Y = 230, Facing = 3,
            Flags = resume!.Flags.Append("interlude_box_packed").ToList(),
            Inventory = new List<string>(), Ink = resume.Ink,
        };
        await game.LoadGame(legacy);
        await WaitIdle(game);
        Check(game.Player.Character == "eleanor_play" && game.Hud.SatchelVisible, "the legacy save loads as Eleanor");
        await game.Perform(Verb.Hand, "closet");
        Check(gs.HasFlag("interlude_safe_locked"), "a legacy packed box locks by hand, with no box in the satchel");
        await game.LoadGame(resume);
        await WaitIdle(game);
        Check(!gs.HasFlag("interlude_safe_locked") && !gs.HasFlag("interlude_box_packed"), "back to the run");
    }

    /// <summary>The end of Act 1 and Act 2: the cathedral, the library, the Club, the morgue and the Harrington office.</summary>
    private async Task PlayActTwo(Game game, GameState gs)
    {
        // ---- end of Act 1, then Act 2 the next day
        Check(gs.StoryAct == 2 && gs.HasItem("journal") && game.Player.Character == "daniel", "Act 2: Daniel is back with the journal");
        await Shot("attic_act2");
        var read = game.ItemVerb(Verb.Hand, "journal");
        await FirstInterlude(game, gs);

        // ---- Act 2, 1927: whiskey and the ring, then the cathedral
        await Until(() => game.Room?.Name == "Office" && gs.HasFlag("office_cup_held"));
        await game.Wait(0.65);
        await Shot("office_whiskey_drinking");
        await Until(() => gs.HasFlag("act2_office_done"));
        Check(gs.HasFlag("act2_whiskey_drunk") && gs.HasFlag("ring_taken_act2") && gs.HasItem("faith_ring"),
            "Act 2 opens with whiskey and the recorded take-ring choice");
        Check(game.Room?.FindHotspot("faith_ring")?.Visible != true, "taken ring is no longer on the desk");
        await Until(() => game.Room?.Name == "ChurchExterior");
        Check(game.Music.Current == Track.StreetTraffic, "traffic, not the organ, out on the cathedral steps");
        Check(gs.HasItem("mirror") && gs.HasItem("cloth"), "reading again leads back to 1927 with Micah's things, Eleanor's cloth too");
        Check(gs.Inventory.Take(2).SequenceEqual(MicahKit.Pinned) &&
            gs.Inventory.Skip(2).All(i => MicahKit.KeptInAct(2, i)) &&
            !gs.HasItem("matchbook") && !gs.HasItem("photo") && !gs.HasItem("dollar"),
            "Act 2 starts with notepad, lighter and the case kit; Act 1 clues stay behind");
        await game.Wait(1.5);
        await Shot("church_exterior_act2");
        await Until(() => game.Room?.Name == "ChurchInterior");
        Check(game.Music.Current == Track.ChurchOrgan, "the organ plays inside the cathedral");
        Check(gs.HasFlag("act2_church_thought"), "Micah thinks about Eleanor outside the cathedral, then goes in");
        await game.Wait(2);
        await Shot("church_act2");
        // the whole caleb_act2 conversation plays out here: about two minutes of game time
        await Until(() => game.Room?.Name == "ChicagoMap", timeout: 240);
        Check(game.Music.Current == null, "the organ stops on the map");
        Check(gs.HasFlag("caleb_met") && !gs.HasFlag("act2_church"), "Micah talks with Caleb and walks out");
        Check(_crossOffers == 0, "no pendant offer on the initial confession");
        Check(!game.Player.Visible, "the player isn't drawn on the map");
        await read;
        await WaitIdle(game);
        await RingAndCrossTest(game);
        await RoseAppealsTest(game);
        await RoseWalkAwayTest(game);
        await Shot("map");
        Check(game.Room?.FindHotspot("club")?.Visible == false, "the club isn't on the map yet");
        if (game.Room is Rooms.ChicagoMap map && map.FindHotspot("library") is { } libSpot)
        {
            map.UpdateCaption(libSpot.Bounds.GetCenter());
            Check(map.CaptionText == libSpot.LookText && !map.CaptionText.Contains("Rose"),
                "hovering a place reads its description in the map caption");
            map.UpdateCaption(new Vector2(20, 250));
            Check(map.CaptionText == "", "the map caption hides away from the places");
            Check(game.LeftClickVerb(libSpot) == Verb.Walk, "a left click on the map travels instead of looking");
        }
        else Check(false, "map caption test reached the map");
        await game.Perform(Verb.Walk, "church");
        Check(game.Room?.Name == "ChicagoMap", "Micah won't go back to the church");

        var libraryLines = await Listen(game, game.Perform(Verb.Walk, "library"));
        Check(game.Room?.Name == "Library" && game.Player.Visible, "went to the library");
        Check(game.Music.Current == Track.Investigation, "the investigation music plays in the library");
        Check(libraryLines.Any(l => l.Contains("Not her shift. Thank God")) && libraryLines.Any(l => l.Contains("back in my head")),
            "Micah is relieved Rose isn't on duty, but she's back on his mind");
        Check(game.Room?.FindHotspot("librarian")?.Visible == true && game.Room?.FindHotspot("rose") == null, "the daytime librarian is there, and Rose isn't in the library at all");
        CheckActorWins(game, "librarian", "ladder", "the librarian wins over the ladder behind him");
        await Shot("library_day");
        await game.Perform(Verb.UseItem, "librarian", "revolver");
        Check(!gs.HasFlag("library_banned"), "no gun before asking");
        gs.TakeItem("mirror");
        var ask = game.Perform(Verb.UseItem, "librarian", Notes.ItemId);
        await Until(() => game.Hud.ImageVisible);
        Check(game.Hud.ImageVisible, "the notepad sketch of the symbol stands in for the mirror");
        await Shot("librarian_symbol");
        game.Hud.CloseImage();
        await ask;
        gs.GiveItem("mirror");
        var notes = game.ItemVerb(Verb.Hand, Notes.ItemId);
        await game.Wait(0.1);
        for (int i = 0; i < 40 && game.Hud.Notepad.PageId is not (null or "triquetra"); i++) game.Hud.Notepad.Turn(-1);
        Check(game.Hud.Notepad.PageId == "triquetra" && game.Hud.Notepad.SketchVisible, "the notepad keeps the sketch from behind the mirror");
        await Shot("notepad_triquetra");
        game.Hud.Notepad.Close();
        await notes;
        Check(gs.HasFlag("librarian_refused"), "the librarian won't talk");
        await game.Perform(Verb.UseItem, "librarian", "revolver");
        Check(!gs.HasItem("book"), "cannot retrieve book before identifying title");
        await game.Perform(Verb.Hand, "shelves_right");
        Check(!gs.HasItem("book"), "locked restricted shelves prevent a catalogue bypass");
        await CancelPuzzle(() => game.Perform(Verb.Hand, "desk"), PuzzleKind.Catalogue, "catalogue_identified", "catalogue");
        await SolvePuzzle(() => game.Perform(Verb.Hand, "desk"), PuzzleKind.Catalogue,
            new[] { ("motif1", 1), ("entry2", 1) }, "catalogue", submit: false);
        int draws = _poseCounts.GetValueOrDefault("micah_draw");
        var threaten = game.Perform(Verb.UseItem, "librarian", "revolver");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.StartsWith("Good Lord", StringComparison.Ordinal));
        Check(game.Player.PoseName == "micah_aim" && _poseCounts.GetValueOrDefault("micah_draw") == draws + 1,
            "Micah draws the revolver and aims it at the librarian");
        await Shot("library_threat");
        await threaten;
        Check(gs.HasItem("book") && gs.HasFlag("librarian_threatened") && !gs.HasFlag("library_banned") &&
            game.Room?.Name == "Library" && game.Player.PoseName == null,
            "threatened the librarian into giving up the book; Micah stays until he leaves");
        await game.Perform(Verb.Talk, "librarian");
        Check(game.Room?.Name == "Library", "the cowed librarian won't talk any more");
        await game.Perform(Verb.Walk, "exit");
        Check(gs.HasFlag("library_banned") && game.Room?.Name == "ChicagoMap", "leaving after the hold-up bans the library");
        await game.Perform(Verb.Walk, "library");
        Check(game.Room?.Name == "ChicagoMap", "the library is off limits now");

        await game.ItemVerb(Verb.Hand, "book");
        Check(!gs.HasItem("address"), "the book is only read at the office");
        await game.Perform(Verb.Walk, "office");
        Check(game.Room?.Name == "Office", "back at the office");
        await game.ItemVerb(Verb.Hand, "book");
        Check(!gs.HasItem("address") && !gs.HasFlag("club_unlocked"), "book gives cipher instructions, not a free address");
        await ReloadCheckpoint("cipher_book_only");
        Check(gs.HasFlag("read_book") && !gs.HasItem("address") && !gs.HasFlag("club_unlocked"), "new save/load does not grandfather unfinished cipher");
        await Combine("card", "mirror");
        await WaitIdle(game);
        Check(!gs.HasFlag("card_reflected"), "cold blank card does not yield an address");
        var warming = game.Perform(Verb.UseItem, "radiator", "card");
        await Until(() => game.Hud.ImageVisible);
        await Shot("card_reversed");
        game.Hud.CloseImage();
        await warming;
        await CancelPuzzle(() => CombineAndWait("card", "mirror"), PuzzleKind.Cipher, "card_decoded", "card_cipher");
        await SolvePuzzle(() => CombineAndWait("mirror", "card"), PuzzleKind.Cipher,
            new[] { ("s0", 1), ("s1", 2) }, "card_cipher");
        Check(gs.HasItem("address") && gs.HasFlag("club_unlocked"), "heat, reflection and ornament order reveal Club address");
        await Shot("office_book");
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "ChicagoMap" && game.Room?.FindHotspot("club")?.Visible == true, "the club is on the map now");
        await Shot("map_club");
        // ---- the Club, the first time: thrown out onto Hubbard Street
        var club = game.Perform(Verb.Walk, "club");
        await Until(() => game.Room?.Name == "ClubHall");
        Check(!gs.HasFlag("on_map") && game.Room?.FindHotspot("guest")?.Visible == false, "entered the Club, no masks around yet");
        Check(game.Music.Current == Track.ClubStrings, "the Club's strings start in the hall");
        await game.Wait(1);
        await Shot("club_hall");
        await Until(() => gs.HasFlag("brute_called"));
        await game.Wait(1);
        await Shot("club_hall_brute");
        await Until(() => game.Room?.Name == "Street");
        Check(game.Music.Current == Track.StreetTraffic, "the strings give way to traffic out on the street");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText.StartsWith("The pavement on Hubbard Street", StringComparison.Ordinal));
        Check(!game.Hud.InsetVisible, "Micah's first line on the pavement comes before his close-up");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Beaten && game.Hud.InsetName == "beaten_closeup",
            "Micah's close-up framed over the pavement while he lies there");
        await game.Wait(1.5);
        await Shot("street_thrown_out");
        await Until(() => game.Room?.Name == "RoseHouse");
        Check(_insetAtStreetChoice == false, "Micah's close-up is removed before he gets up and chooses");
        Check(DryHere(), "the rain stops at Rose's street");
        Check(game.Music.Current == Track.RoseStreet, "the quiet evening street plays outside Rose's house");
        await Until(() => game.Hud.ThoughtVisible && game.Hud.ThoughtText.Contains("it stops at Rose's street"));
        Check(game.Hud.ThoughtText.Contains("it stops at Rose's street"), "Micah notices the rain stop at Rose's street");
        await club;
        await WaitIdle(game);
        Check(gs.HasFlag("go_rose") && gs.HasFlag("club_out"), "chose to go to Rose's house");
        await Shot("rose_house");
        var bell = game.Perform(Verb.Hand, "bell");
        await Until(() => gs.HasFlag("rose_door"));
        await game.Wait(1.5);
        await Shot("rose_house_door");
        await Until(() => game.Player.Facing == Facing.Up && game.Player.Position.DistanceTo(Rooms.RoseHouse.TalkSpot) < 2);
        Check(game.Room!.FindActor("rose")!.Texture!.ResourcePath.EndsWith("/rose_front.png"),
            "Micah stands by the bell with his back to the screen, Rose faces the camera");
        await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText.Contains("Wait!"));
        Check(!game.Hud.InsetVisible, "no close-up yet while Rose calls \"Wait!\"");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Rose && game.Room?.Name == "RoseHouse", "Rose's close-up framed over the door after she calls Micah back");
        Check(!game.Hud.SpeechVisible, "the close-up opens on a silent look");
        Check(game.Hud.InsetRect.Size.X >= 400 && game.Hud.InsetRect.Size.Y >= 200, "Rose's close-up fills most of the screen");
        await Until(() => game.Hud.SpeechVisible);
        Check(game.Hud.SpeechText.Contains("trouble"), "after the pause, Rose's last line over the close-up");
        Check(game.Hud.SpeechRect.Position.Y > game.Hud.InsetRect.Position.Y + game.Hud.InsetRect.Size.Y * 0.7f, "speech sits below Rose's face while the close-up is up");
        await game.Wait(1);
        await Shot("rose_house_wait");
        await Until(() => !game.Hud.SpeechVisible || !game.Hud.InsetVisible);
        Check(game.Hud.InsetVisible, "Rose's close-up holds after her last line");
        await Until(() => game.Hud.SpeechVisible || !game.Hud.InsetVisible);
        Check(game.Hud.InsetVisible && game.Hud.SpeechText == "...", "Micah answers Rose with \"...\" over the close-up");
        await Until(() => !game.Hud.InsetVisible);
        Check(game.Room?.Name == "RoseHouse", "Rose's close-up is gone before the door closes");
        await bell;
        Check(gs.HasFlag("rose_wait") && game.Room?.Name == "ChicagoMap", "Rose called Micah back, then the map");
        Check(game.Room?.FindHotspot("club")?.Visible == true && game.Room?.FindHotspot("convent")?.Visible == false, "convent not on the map yet");
        await game.Perform(Verb.Walk, "club");
        Check(game.Room?.Name == "ChicagoMap", "no use going back to the Club");

        // ---- Caleb points to the convent; the sister, and the revolver
        await game.Perform(Verb.Walk, "church");
        Check(gs.HasFlag("caleb_club") && game.Room?.Name == "ChicagoMap", "Caleb talked about the Club, then back to the map");
        Check(_offered.TryGetValue("caleb_club", out var calebLast) && calebLast.Length == 1 && calebLast[0].StartsWith("They have her, Caleb"),
            "Micah presses Caleb with both reasons before asking him outright");
        await game.Perform(Verb.Walk, "church");
        Check(game.Room?.Name == "ChicagoMap" && !gs.HasFlag("church_before_office"), "repeat church visit doesn't anticipate the sister's threat");
        Check(!gs.HasItem("cross"), "taking the ring initially postpones the cross until Act 3");
        Check(game.Room?.FindHotspot("convent")?.Visible == true, "the convent is on the map");
        await game.Perform(Verb.Walk, "convent");
        Check(game.Room?.Name == "ConventCorridor" && gs.HasFlag("nun_club_asked"), "asked the sister about the Club");
        await Shot("convent_act2");
        for (var i = 0; i < 3; i++)
        {
            var nunLines = await Listen(game, game.Perform(Verb.Talk, "nun"));
            Check(game.Room is Rooms.ConventCorridor && !gs.HasFlag("nun_threatened") &&
                nunLines.Any(l => l.Contains("I know nothing")), $"talking to the sister again is a short refusal ({i + 1})");
        }
        var threat = game.Perform(Verb.UseItem, "nun", "revolver");
        var threatHeard = Listen(game, threat);
        await game.Wait(1.5);
        await Shot("convent_gun");
        await threat;
        var threatLines = await threatHeard;
        Check(threatLines.Any(l => l.Contains("Jezebel")) && threatLines.Any(l => l.Contains("I failed her")),
            "seduced, Agatha still calls her a Jezebel, but confesses she failed her");
        Check(gs.HasFlag("nun_threatened") && game.Room?.Name == "ChicagoMap", "the sister names Harrington");
        Check(game.Room?.FindHotspot("tribune")?.Visible == true && game.Room?.FindHotspot("harrington")?.Visible == false
            && game.Room?.FindHotspot("club")?.Visible == false
            && game.Room?.FindHotspot("library")?.Visible == false
            && game.Room?.FindHotspot("office")?.Visible == true, "the Tribune before Harrington; office remains available for ring recovery");
        await Shot("map_tribune");
        await game.Perform(Verb.Walk, "church");
        Check(gs.HasFlag("church_before_office") && game.Room?.Name == "ChicagoMap", "Caleb warns Micah before the office");

        // ---- the Tribune morgue: a clipping torn through the address, paste, and a pin in the Loop
        await game.Perform(Verb.Walk, "tribune");
        Check(game.Room?.Name == "NewspaperMorgue", "down in the Tribune morgue");
        await WaitIdle(game);
        await Shot("newspaper_morgue");
        await game.Perform(Verb.Hand, "drawer_h");
        Check(gs.HasItem("clipping_top") && gs.HasFlag("took_clipping_top"), "drawer H: the top half of the clipping");
        await game.Perform(Verb.Hand, "spike");
        Check(gs.HasItem("clipping_bottom") && gs.HasFlag("took_clipping_bottom"), "the copy spike: the bottom half");
        await game.Perform(Verb.UseItem, "wall_map", "clipping_top");
        Check(!gs.HasFlag("harrington_located"), "half a clipping is no address");
        await CombineAndWait("clipping_top", "clipping_bottom");
        Check(!gs.HasItem("clipping") && gs.HasItem("clipping_top") && gs.HasItem("clipping_bottom"), "the halves won't hold without paste");
        await game.Perform(Verb.Hand, "paste_pot");
        Check(gs.HasItem("paste") && gs.HasFlag("paste_out"), "borrowed the paste pot");
        await Shot("newspaper_morgue_taken");
        await CombineAndWait("clipping_top", "clipping_bottom");
        Check(gs.HasFlag("mended_clipping") && gs.HasItem("paste") && !gs.HasItem("clipping_top") && !gs.HasItem("clipping_bottom"),
            "pasted the halves together; the paste pot is kept");
        Check(gs.HasFlag("harrington_located") && !gs.HasItem("clipping"),
            "the mended clipping is pinned on the wall map at once: the Harrington Building on LaSalle");
        await ReloadCheckpoint("morgue_clipping");
        Check(gs.HasFlag("harrington_located") && !gs.HasItem("clipping"), "the pin survives a reload");
        await Shot("newspaper_morgue_pin");
        await game.Perform(Verb.Walk, "door");
        Check(game.Room?.Name == "ChicagoMap" && !gs.HasItem("paste") && !gs.HasFlag("paste_out"), "the paste pot goes back on the way out");
        Check(game.Room?.FindHotspot("harrington")?.Visible == true && game.Room?.FindHotspot("tribune")?.Visible == false,
            "Harrington's office on the map, the Tribune off it");
        await Shot("map_harrington");

        // ---- the alley behind the Harrington Building
        await game.Perform(Verb.Walk, "harrington");
        Check(game.Room?.Name == "HarringtonRoad", "at the Harrington Building");
        await Shot("harrington_road");
        await game.Perform(Verb.Hand, "crates");
        Check(!gs.HasFlag("crates_stacked"), "the watchman sees Micah going for the crates");
        await game.Perform(Verb.Hand, "fire_escape");
        Check(game.Room?.Name == "HarringtonRoad", "can't climb while watched");
        await game.Perform(Verb.UseItem, "trash_can", MicahKit.LighterId);
        Check(gs.HasFlag("watchman_distracted"), "the fire sends the watchman inside");
        // count frame steps rather than compare two samples: at the fast clock one slow frame can step the strip a whole
        // loop and land back on the sampled frame
        var flames = game.Room?.GetNodeOrNull<LoopStrip>("Flames");
        int flameSteps = 0;
        void FlameStepped() => flameSteps++;
        if (flames != null) flames.FrameChanged += FlameStepped;
        await Until(() => flameSteps >= 2, timeout: 2);
        if (flames != null) flames.FrameChanged -= FlameStepped;
        Check(flames != null && flames.Visible && flames.Hframes > 1 && flameSteps >= 2,
            "the trash-can fire's flames and smoke loop while it burns");
        await Shot("harrington_road_fire");
        await game.Perform(Verb.Hand, "fire_escape");
        Check(game.Room?.Name == "HarringtonRoad", "the ladder is too high without the crates");
        await game.Perform(Verb.Hand, "packing_wedge");
        await game.Perform(Verb.UseItem, "ladder_catch", "wedge");
        Check(!gs.HasFlag("ladder_freed") && gs.HasItem("wedge"), "catch cannot be reached before stacking crates; wedge retained");
        await game.Perform(Verb.Hand, "crates");
        Check(gs.HasFlag("crates_stacked"), "stacked the crates");
        await game.Perform(Verb.Hand, "fire_escape");
        Check(game.Room?.Name == "HarringtonRoad", "stacked crates alone do not bypass the jammed catch");
        await game.Perform(Verb.Hand, "packing_wedge");
        Check(gs.HasItem("wedge"), "collected packing wedge from distinct hotspot");
        await ReloadCheckpoint("ladder_wedge");
        await game.Perform(Verb.UseItem, "ladder_catch", "wedge");
        Check(gs.HasFlag("ladder_freed") && !gs.HasItem("wedge"), "wedge remains installed holding catch clear");
        await Shot("harrington_road_crates");
        await game.Perform(Verb.Hand, "fire_escape");
        Check(game.Room?.Name == "HarringtonOffice", "climbed into Harrington's office");
        await WaitIdle(game);
        await Shot("harrington_office");
        await game.Perform(Verb.Walk, "window");
        Check(game.Room?.Name == "HarringtonOffice", "can't leave empty-handed");
        await game.Perform(Verb.Hand, "drawer_left");
        await game.Perform(Verb.Hand, "drawer_right");
        Check(!gs.HasItem("invitation"), "the right drawer is locked");
        await game.Perform(Verb.UseItem, "drawer_right", "lockpick");
        Check(gs.HasItem("invitation"), "picked the drawer: the invitation");
        await game.Perform(Verb.Hand, "closet");
        Check(gs.HasFlag("harrington_closet_open"), "Harrington closet uses independent flag");
        var lookPortrait = game.Perform(Verb.Look, "portrait");
        await Until(() => game.Hud.InsetVisible);
        Check(game.Hud.CurrentCloseUp == CloseUps.Heraldry && game.Hud.InsetName == "heraldry_closeup",
            "looking at the portrait frames the band of heraldry at its foot");
        await Until(() => game.Hud.SpeechVisible);
        await Shot("harrington_portrait_heraldry");
        await lookPortrait;
        await Until(() => !game.Hud.InsetVisible);
        Check(gs.HasFlag("portrait_key_seen") && !game.Hud.InsetVisible, "the heraldry close-up closes after Micah's look");
        Check(new CrestsScreen().Clue == "Three dials. Three symbols.",
            "the false-back lock's clue box gives nothing away");
        await CancelPuzzle(() => game.Perform(Verb.UseItem, "panel", "lockpick"), PuzzleKind.Crests, "secret_open", "crest_lock");
        await SolvePuzzle(() => game.Perform(Verb.Hand, "panel"), PuzzleKind.Crests,
            new[] { ("s0", 2), ("s2", 1) }, "crest_lock");
        await Shot("harrington_office_niche");
        await game.Perform(Verb.Hand, "niche");
        Check(gs.HasItem("mask") && gs.HasItem("cloak"), "took the mask and the cloak");
        await Shot("harrington_office_after");
        await game.Perform(Verb.Walk, "window");
        Check(gs.HasFlag("harrington_done") && game.Room?.Name == "ChicagoMap", "out the window, back to the map");
        Check(game.Room?.FindHotspot("club")?.Visible == true && game.Room?.FindHotspot("harrington")?.Visible == false, "the Club is back on the map");
        await game.Perform(Verb.Walk, "church");
        Check(gs.HasFlag("church_before_club"), "Caleb's last warning before the Club");
    }
}
