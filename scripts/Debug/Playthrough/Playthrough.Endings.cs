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
        int ending = _route.StartsWith('1') ? 1 : int.Parse(_route);
        await Until(() => _game.Hud.CaptionVisible && _game.Hud.CaptionText == "End of Act Three", 300);
        Check(_game.Hud.CaptionText == "End of Act Three", $"route {_route}: End of Act Three");
        await Until(() => _game.Room?.Name == "Attic" && _game.Hud.CaptionVisible && _game.Hud.CaptionText == "The End", 300);
        Check(_game.Room?.Name == "Attic" && _game.Hud.CaptionText == "The End", $"route {_route}: the epilogue ends on \"The End\"");
        for (int n = 1; n <= 7; n++)
            Check(Gs.HasFlag($"ending_{n}") == (n == ending), $"route {_route}: ending_{n} {(n == ending ? "set" : "not set")}");
        bool keeps = Endings.KeepsJournal(ending);
        Check(Gs.HasItem("journal") == keeps, $"route {_route}: Daniel {(keeps ? "keeps the journal for Leo" : "puts the journal back")}");
        // Choose() falls back to the first option, so a renamed or wrongly gated choice would otherwise pass silently.
        // By now the cross is taken, so Wants() names the Blue Lantern; Caleb was asked for on the first visit. Giving up
        // on the steps ends the story before Act 3's office, so that route only answers the stage.
        var required = _route == "1-steps" ? new[] { "Give up" } : Wants().Append("Visit Caleb").Distinct();
        foreach (var want in required)
            Check(_matchedWants.Contains(want), $"route {_route}: the choice \"{want}\" was offered and taken");
    }

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
            case "6":
                yield return "Our Father";
                yield return "Shoot him";
                yield return "turn yourself in";
                break;
            case "7":
                yield return "Shoot him";
                yield return "He had it coming";
                yield return "Shoot Eleanor";
                break;
        }
    }
}
