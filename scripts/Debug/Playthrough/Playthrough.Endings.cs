using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The ending routes: what each one answers, and the checks on "The End".</summary>
public sealed partial class Playthrough
{
    /// <summary>Waits for "End of Act Three", then Daniel's epilogue in the attic and "The End".</summary>
    private async Task TheEnd()
    {
        int ending = _route is "1" or "1-oldman" or "1-steps" ? 1 : KillRoute ? 12 : int.Parse(_route);
        await Until(() => _game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three", 300);
        Check(_game.Hud.CaptionText == "End of Act Three", $"route {_route}: End of Act Three");
        bool sawVows = false;
        await Until(() =>
        {
            sawVows |= _game.Hud.CurrentCloseUp == CloseUps.Vows && _game.Hud.InsetName == "vows_photo";
            return _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End";
        }, 300);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionText == "The End", $"route {_route}: the epilogue ends on \"The End\"");
        Check(sawVows == (ending == 1), $"route {_route}: the vow-renewal photo {(ending == 1 ? "shown" : "not shown")} in the epilogue");
        for (int n = 1; n <= Endings.Count; n++)
            Check(Gs.HasFlag($"ending_{n}") == (n == ending), $"route {_route}: ending_{n} {(n == ending ? "set" : "not set")}");
        bool keeps = Endings.KeepsJournal(ending);
        Check(Gs.HasItem("journal") == keeps, $"route {_route}: Daniel {(keeps ? "keeps the journal for Leo" : "puts the journal back")}");
        // the final stash records what Micah still carried: giving up on Eleanor throws her cloth away, and so does
        // leaving her in the mansion (endings 8 and 9 go through his coffee with Rose)
        bool thrown = ending is 1 or 8 or 9;
        Check(Gs.HasFlag("stash_cloth") == !thrown,
            $"route {_route}: Eleanor's cloth {(thrown ? "thrown in the street" : "still in Micah's pocket")}");
        Check(!Story.Interlude.EleanorPlays(Gs.HasFlag), $"route {_route}: no Eleanor flag survives into the epilogue");
        // Choose() falls back to the first option, so a renamed or wrongly gated choice would otherwise pass silently.
        // By now the cross is taken, so Wants() names the Blue Lantern; Caleb was asked for on the first visit. Giving up
        // on the steps ends the story before Act 3's office, so that route only answers the stage.
        var required = _route == "1-steps" ? new[] { "Give up" } : Wants().Append("Visit Caleb").Distinct();
        foreach (var want in required)
            Check(_matchedWants.Contains(want), $"route {_route}: the choice \"{want}\" was offered and taken");
    }

    /// <summary>Routes where Eleanor refuses the old man's gin too, opening her endings 8-11.</summary>
    private bool EleanorRoute => _route is "8" or "9" or "10" or "11";

    /// <summary>Routes where Micah goes back to Tony with the revolver and kills him, ending in prison (ending 12).</summary>
    private bool KillRoute => _route is "12" or "12-oldman";

    /// <summary>Routes where Micah's shot misses Tony on purpose and the unseen alarm rings at the mansion (13 runs, 14 stays).</summary>
    private bool AlarmRoute => _route is "13" or "14";

    /// <summary>
    /// Eleanor's coda in the mansion, after Micah's prayer: the candlestick, then out through the study and the kitchen
    /// (route 8 sets the cellar alight first), to Micah's coffee with Rose and her own last scene.
    /// </summary>
    private async Task EleanorCoda()
    {
        await Beat("eleanor_coda_strike", async () =>
        {
            var harrington = _game.Room?.FindActor("harrington");
            Check(harrington?.Position == Rooms.MansionBedroom.HarringtonCoda && harrington.FlipH,
                "the old man stands at the foot of the bed, his back to her");
            float left = float.MaxValue;
            var strike = Do(Verb.Hand, "candlestick");
            await Until(() =>
            {
                left = Mathf.Min(left, _game.Player.Position.X);
                return strike.IsCompleted;
            }, 60, 0.02);
            await WaitIdle();
            Check(Gs.HasFlag(Endings.EleanorStruck), "Eleanor strikes the old man");
            Check(left >= Rooms.MansionBedroom.BehindHim.X - 2,
                $"she takes the candlestick and steps up behind him without crossing the room (leftmost x {left:0})");
            await Do(Verb.Walk, "door");
            await WaitIdle();
            Expect("MansionStudy", "Eleanor out through the study");
            await Do(Verb.Walk, "door_left");
            await WaitIdle();
            Expect("MansionKitchen", "down to the kitchen");
        });
        if (_route == "8")
            await Beat("eleanor_coda_fire", async () =>
            {
                await Do(Verb.Walk, "cellar_door");
                await WaitIdle();
                Expect("MansionCellar", "Eleanor down to the cellar");
                await Do(Verb.Hand, "hung_lantern");
                await Do(Verb.Hand, "barrel");
                await WaitIdle();
                Check(Gs.HasFlag(Endings.EleanorBurned) && Gs.HasFlag("cellar_fire"), "Eleanor sets the whiskey alight");
                Expect("MansionKitchen", "up out of the burning cellar");
            });
        await Beat("eleanor_coda_escape", async () =>
        {
            _ = Do(Verb.Walk, "back_door");
            await Until(() => _game.Room?.Name == "RoseHouse", 300);
            Check(_game.Room?.Name == "RoseHouse", "Micah's coffee with Rose");
            string last = _route == "8" ? "Outskirts" : "Prison";
            await Until(() => _game.Room?.Name == last, 600);
            Expect(last, _route == "8" ? "Eleanor alone at the city's edge" : "Eleanor confesses to Caleb");
            await TheEnd();
            Check(Gs.HasFlag(Endings.EleanorBurned) == (_route == "8"), "the house burns only in ending 8");
        }, roundTrip: false);
    }

    /// <summary>What each route answers. Unmatched choices take the first option, as the main story does.</summary>
    private IEnumerable<string> Wants()
    {
        yield return "(Tell her the truth.";
        yield return EleanorRoute ? "(Push it away.)" : "(Take the glass";
        yield return "Accept the cross";
        yield return Gs.HasFlag("took_cross") ? "Go to the Blue Lantern" : "Visit Caleb";
        yield return _route == "1-steps" ? "Give up" : "Keep going";
        switch (_route)
        {
            case "1":
                yield return "Lower the gun. It's not worth it";
                break;
            case "1-oldman":
            case "8":
            case "9":
                yield return "Shoot him in the shoulder";
                yield return "Our Father";
                break;
            case "10":
            case "11":
                yield return "Shoot him";
                break;
            case "12":
                yield return "Shoot him in the shoulder";
                yield return "Finish him";
                yield return "(Turn yourself in.)";
                break;
            case "12-oldman":
                yield return "Shoot him in the shoulder";
                yield return "Finish him";
                yield return "Not yet";
                yield return "Our Father";
                break;
            case "13":
                yield return "Fire into the wall";
                yield return "(Run.)";
                break;
            case "14":
                yield return "Fire into the wall";
                yield return "(Stay.";
                break;
            // Eleanor's four turns: the lines' points must reach the threshold (see docs/eleanor-persuasion.md);
            // possessive 4 + rational 2 + possessive 4 + positive 1 = 11
            case "2":
            case "4":
                yield return "Shoot him";
                yield return "I didn't come all this way";
                yield return "lend you out again";
                yield return "Then be mine instead";
                yield return "decide it yourself";
                break;
            case "3":
                // she's left on the third turn, as soon as Micah may
                yield return "Shoot him";
                yield return "They'll pin it on you";
                yield return "Forget Theodore";
                yield return "(Leave her.)";
                break;
            case "5":
                // three clumsy lines lose her (4 + 0 + 0 + 0): the footsteps on the landing, and Micah leaves her to them
                yield return "Shoot him";
                yield return "I didn't come all this way";
                yield return "Theodore's a coward";
                yield return "A singer";
                yield return "finishing the job";
                yield return "(Leave her to them.)";
                break;
            case "6":
                // "Shoot him" first: the old man's taunt offers both, the club only the prayer
                yield return "Shoot him";
                yield return "Our Father";
                yield return "turn yourself in";
                break;
            case "7":
                // the shot is offered only on the fourth turn
                yield return "Shoot him";
                yield return "I didn't come all this way";
                yield return "Forget Theodore";
                yield return "Then be mine instead";
                yield return "(Shoot Eleanor.)";
                break;
        }
    }
}
