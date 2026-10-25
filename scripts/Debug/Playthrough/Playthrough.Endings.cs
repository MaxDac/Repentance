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
        int ending = EndingOf(_route);
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
        // the final stash records what Micah still carried: he throws Eleanor's cloth away at Rose's door, so giving up
        // on her drops it, and so does leaving her in the mansion (endings 8 and 9 go through his coffee with Rose,
        // except after killing Tony, when he never goes to Rose's)
        bool thrown = ending is 1 or 15 || (ending is 8 or 9 && !KillRoute);
        Check(Gs.HasFlag("stash_cloth") == !thrown,
            $"route {_route}: Eleanor's cloth {(thrown ? "thrown in the street" : "still in Micah's pocket")}");
        Check(!Story.Interlude.EleanorPlays(Gs.HasFlag), $"route {_route}: no Eleanor flag survives into the epilogue");
        // Choose() falls back to the first option, so a renamed or wrongly gated choice would otherwise pass silently.
        // Giving up on the steps ends the story before Act 3's office, where Caleb's visit and cross are answered.
        var required = StepsRoute ? Wants().Where(w => w is not ("Accept the cross" or "Visit Caleb")) : Wants();
        foreach (var want in required)
            Check(_matchedWants.Contains(want), $"route {_route}: the choice \"{want}\" was offered and taken");
    }

    /// <summary>The ending a route plays: its leading number (15-steps-caleb is ending 15).</summary>
    public static int EndingOf(string route) => int.Parse(route.Split('-')[0]);

    /// <summary>Routes that give up on the church steps after the Club, before Act 3 (ending 1, or 15 without Rose's call-back).</summary>
    private static bool IsSteps(string route) => route is "1-steps" or "1-steps-caleb" or "15-steps" or "15-steps-caleb";

    /// <summary>Routes where Micah walks away from Tony and goes home to Rose (ending 1, or 15 when she refuses him).</summary>
    private static bool IsWalkAway(string route) => route is "1" or "1-caleb" or "15" or "15-caleb";

    /// <summary>Routes where Micah goes back to Tony with the revolver and kills him.</summary>
    private static bool IsKill(string route) => route is "12" or "12-oldman" or "12-bed" or "8-kill" or "9-kill";

    /// <summary>Routes where Micah's shot misses Tony on purpose and the unseen alarm rings at the mansion (13 runs, 14 stays).</summary>
    private static bool IsAlarm(string route) => route is "13" or "14" or "13-caleb" or "14-caleb";

    /// <summary>Routes where Eleanor refuses the old man's gin too (both refusals), opening her endings and Caleb's escape.</summary>
    private bool EleanorRoute => _route is "8" or "9" or "10" or "11" or "1-caleb" or "15-caleb" or "1-steps-caleb"
        or "15-steps-caleb" or "1-bed" or "15-bed" or "12-bed" or "8-kill" or "9-kill" or "13-caleb" or "14-caleb";

    private bool StepsRoute => IsSteps(_route);

    private bool WalkAwayRoute => IsWalkAway(_route);

    /// <summary>Routes where Micah said good night to Rose at once in Act 2, so she refuses his coffee (ending 15).</summary>
    private bool RoseRefuses => EndingOf(_route) == 15;

    private bool KillRoute => IsKill(_route);

    private bool AlarmRoute => IsAlarm(_route);

    /// <summary>Routes where Micah prays the Our Father and spares the old man, then goes home to Rose.</summary>
    private bool OldManRoute => _route is "1-oldman" or "15-oldman";

    /// <summary>Routes where Micah prays and Eleanor, who held out, plays her coda in the mansion.</summary>
    private bool CodaRoute => _route is "8" or "9" or "1-bed" or "15-bed" or "12-bed" or "8-kill" or "9-kill";

    /// <summary>Coda routes where Eleanor goes back to bed instead of striking the old man.</summary>
    private bool BedRoute => _route.EndsWith("-bed", StringComparison.Ordinal);

    /// <summary>Coda routes where Eleanor sets the cellar alight on her way out.</summary>
    private bool Burns => EndingOf(_route) == 8;

    /// <summary>
    /// Eleanor held out and Micah never reached her (a give-up before the mansion, or the alarm): Caleb gets her out of
    /// the city, and her last scene is with him at the outskirts.
    /// </summary>
    private async Task CalebEscape()
    {
        int ending = EndingOf(_route);
        await Until(() => _game.Room?.Name == "Outskirts" && Gs.HasFlag("caleb_escape") &&
            _game.Player.Character == "eleanor_white_play", 600);
        Expect("Outskirts", "Eleanor and Caleb at the city's edge");
        Check(Gs.HasFlag("caleb_escape") && Gs.HasFlag($"ending_{ending}"), $"ending {ending}, with Eleanor's escape");
        Check(_game.Player.Character == "eleanor_white_play", "Eleanor in her white dress");
        Check(_game.Room?.FindActor("caleb")?.Visible == true, "Caleb beside her");
    }

    /// <summary>Micah at Rose's door after giving up: the coffee, or her refusal; then Eleanor's escape if she held out.</summary>
    private async Task RoseAndCaleb()
    {
        Check(Gs.HasFlag(Endings.RoseForgives) == !RoseRefuses, $"Rose {(RoseRefuses ? "refuses the coffee" : "takes the coffee")}");
        if (EleanorRoute) await CalebEscape();
    }

    /// <summary>
    /// Eleanor's coda in the mansion, after Micah's prayer: back to bed (the -bed routes), or the candlestick, then out
    /// through the study and the kitchen (ending 8 sets the cellar alight first), to Micah's coffee with Rose (unless he
    /// killed Tony) and her own last scene.
    /// </summary>
    private async Task EleanorCoda()
    {
        if (BedRoute)
        {
            await Beat("eleanor_coda_bed", async () =>
            {
                string next = KillRoute ? "Prison" : "RoseHouse";
                _ = Do(Verb.Hand, "bed");
                await Until(() => _game.Room?.Name == next, 300);
                Expect(next, KillRoute ? "Eleanor back to bed, Micah on to the station" : "Eleanor back to bed, Micah on to Rose");
                Check(!Gs.HasFlag(Endings.EleanorStruck) && !Gs.HasFlag("eleanor_coda"), "Eleanor goes back to bed without striking him");
                if (!KillRoute)
                    Check(Gs.HasFlag(Endings.RoseForgives) == !RoseRefuses, $"Rose {(RoseRefuses ? "refuses the coffee" : "takes the coffee")}");
                await TheEnd();
            }, roundTrip: false);
            return;
        }
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
        if (Burns)
            await Beat("eleanor_coda_fire", async () =>
            {
                await Do(Verb.Walk, "cellar_door");
                await WaitIdle();
                Expect("MansionCellar", "Eleanor down to the cellar");
                await Do(Verb.Hand, "hung_lantern");
                Check(Gs.HasItem("lantern_lit") && _game.Hud.SatchelVisible, "the lit lantern in Eleanor's own satchel");
                await Do(Verb.Hand, "barrel");
                Check(Gs.HasFlag("barrel_open") && !Gs.HasFlag(Endings.EleanorBurned), "she opens the spigot");
                await Do(Verb.UseItem, "barrel", "lantern_lit");
                await WaitIdle();
                Check(Gs.HasFlag(Endings.EleanorBurned) && Gs.HasFlag("cellar_fire") && !Gs.HasItem("lantern_lit"),
                    "Eleanor sets the whiskey alight with the lantern");
                Expect("MansionKitchen", "up out of the burning cellar");
            });
        await Beat("eleanor_coda_escape", async () =>
        {
            // after killing Tony, Micah promised Caleb the station steps: no coffee at Rose's door
            string last = Burns ? "Outskirts" : "Prison";
            bool blaze = false, atRose = false, sawRose = false;
            _ = Do(Verb.Walk, "back_door");
            await Until(() =>
            {
                blaze |= _game.Room?.Name == "MansionExterior" &&
                    _game.Room.GetNodeOrNull<CanvasItem>("EleanorFire")?.Visible == true;
                atRose |= _game.Room?.Name == "RoseHouse";
                sawRose |= _game.Room?.Name == "RoseHouse" && _game.Hud.CurrentCloseUp == CloseUps.Rose;
                return _game.Room?.Name == last;
            }, 900, 0.05);
            Check(blaze == Burns, $"the house {(Burns ? "burns" : "stays dark")} behind her outside");
            Check(!Gs.HasItem("lantern_lit") && !Gs.Flags.Any(f => f.StartsWith("coda_stash_")),
                "Micah's things back with him, and nothing of Eleanor's");
            Check(atRose == !KillRoute, KillRoute ? "Micah's at the station, not at Rose's door" : "Micah's coffee with Rose");
            Check(sawRose == !KillRoute, KillRoute ? "no Rose close-up after killing Tony" : "Rose's close-up frames Micah's coffee invitation");
            Expect(last, Burns ? "Eleanor alone at the city's edge" : "Eleanor confesses to Caleb");
            await TheEnd();
            Check(Gs.HasFlag(Endings.EleanorBurned) == Burns, "the house burns only in ending 8");
        }, roundTrip: false);
    }

    /// <summary>What each route answers. Unmatched choices take the first option, as the main story does.</summary>
    private IEnumerable<string> Wants()
    {
        yield return "(Tell her the truth.";
        yield return EleanorRoute ? "(Push it away.)" : "(Take the glass";
        // film mode plays Act 2 per route; the test's shared vestibule save forgets Rose's call-back instead
        if (RoseRefuses && _film) yield return "Good night, Rose.";
        yield return "Accept the cross";
        yield return "Visit Caleb";
        yield return StepsRoute ? "Give up" : "Keep going";
        switch (_route)
        {
            case "1":
            case "1-caleb":
            case "15":
            case "15-caleb":
                yield return "Lower the gun. It's not worth it";
                break;
            case "1-oldman":
            case "15-oldman":
            case "1-bed":
            case "15-bed":
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
            case "12-bed":
            case "8-kill":
            case "9-kill":
                yield return "Shoot him in the shoulder";
                yield return "Finish him";
                yield return "Not yet";
                yield return "Our Father";
                break;
            case "13":
            case "13-caleb":
                yield return "Fire into the wall";
                yield return "(Run.)";
                break;
            case "14":
            case "14-caleb":
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
            case "7-alone":
                // three clumsy lines lose her (4 + 0 + 0 + 0): the footsteps on the landing, and Micah leaves her to
                // them (5) or turns the gun on himself (7-alone)
                yield return "Shoot him";
                yield return "I didn't come all this way";
                yield return "Theodore's a coward";
                yield return "A singer";
                yield return "finishing the job";
                yield return _route == "5" ? "(Leave her to them.)" : "(Pull the trigger on myself.)";
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
