using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 1: the flophouse lobby. The night clerk is scared of the men who collect on Fridays and won't let Micah
/// upstairs; he'll hand over his umbrella just to see him gone (Puzzle 19).
/// Act 2: days later Micah asks him where Eleanor went. The clerk won't say, until Micah hauls him across the
/// counter by his tie: two men took her, the night Micah left.
/// </summary>
public partial class MotelLobby : Room
{
    /// <summary>Where Micah stands at the counter to reach the clerk's tie, facing him.</summary>
    public static readonly Vector2 TieSpot = new(245, 205);

    private bool Returning => State.HasFlag("motel_return") && !State.HasFlag("motel_return_done");

    public override async Task OnEnter(string entry)
    {
        if (Returning)
        {
            if (State.HasFlag("seen_motel_return_lobby")) return;
            State.SetFlag("seen_motel_return_lobby");
            await Game.Run(async () =>
            {
                await Wait(0.4);
                await Think("Same brown wallpaper, same dead palm. The clerk saw me come in and found something fascinating in his register.");
            });
            return;
        }
        if (State.HasFlag("seen_motel_lobby")) return;
        State.SetFlag("seen_motel_lobby");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("A long way down from the Aurelian. Brown wallpaper, a dead palm in a pot and a smell of boiled coffee and old cigars.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (State.HasFlag("motel_return") && await ReturnInteract(verb, target, item)) return true;
        switch (target.Id, verb)
        {
            case ("clerk" or "counter" or "bell", Verb.Talk):
            case ("clerk", Verb.Hand):
                await Talk("motel_clerk");
                if (State.HasFlag("clerk_talked") && !State.HasFlag("took_umbrella"))
                    await Think("Upstairs is out, the front way. But every flophouse in Chicago has a back way, and this one has a fire escape.");
                return true;
            case ("clerk", Verb.UseItem) when item == "dollar":
                await Say("clerk", "Put your money away, mister. There's no room for you here at any price.");
                return true;
            case ("clerk", Verb.UseItem) when item == "photo":
                await ShowPhoto("clerk");
                await Say("clerk", "I told you. I never saw nobody.");
                await PocketPhoto();
                await Think("He looked at the photograph for half a second, then he looked at the stairs. That was answer enough.");
                return true;
            case ("clerk", Verb.UseItem) when item == "revolver":
                await Say("Pull a gun in a joint that pays Moretti, and I'll be in the river by Friday. Him too.");
                return true;
            case ("clerk", Verb.Kick):
                await Say("He's a scared little man behind a counter. Kicking him won't make him braver.");
                return true;

            case ("bell", Verb.Hand):
                await Say("*ding*");
                await Say("clerk", "I'm standing right here, mister.");
                return true;

            case ("stairs", Verb.Walk or Verb.Hand):
                if (FindActor("clerk") != null)
                {
                    await Say("clerk", "Hey! Nobody goes up. Rules of the house.");
                    await Say("Not this way, then.");
                }
                return true;

            case ("umbrella" or "umbrella_stand", Verb.Hand):
                if (State.HasFlag("took_umbrella"))
                {
                    await Say("Empty now. The clerk's umbrella is mine for the night.");
                    return true;
                }
                if (!State.HasFlag("clerk_talked"))
                {
                    await Say("A black umbrella with a crook handle. The clerk's, I'd guess. Help yourself to a man's umbrella before you've said good evening and he gets testy.");
                    return true;
                }
                await Say("Mind if I borrow your umbrella? It's coming down out there.");
                await Say("clerk", "Take it. Take it and go.");
                State.GiveItem("umbrella");
                State.SetFlag("took_umbrella");
                await Say("A good stout crook on the end of it. It'll keep the rain off, or reach something higher than me.");
                return true;
        }
        return false;
    }

    /// <summary>Act 2: the second interrogation, and nothing else in the lobby that matters any more.</summary>
    private async Task<bool> ReturnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("clerk" or "counter" or "bell", Verb.Talk):
            case ("clerk", Verb.Hand):
            case ("clerk", Verb.UseItem) when item == "photo":
                await AskTheClerk();
                return true;
            case ("clerk", Verb.UseItem) when item == "dollar":
                await Say("clerk", "Keep it, mister. I don't want your money. I don't want nothing from you.");
                return true;
            case ("clerk", Verb.UseItem) when item == "revolver":
                await Say("A gun says too much in a Moretti joint. My hands will do the talking.");
                return true;
            case ("clerk", Verb.Kick):
                await Say("Not with my feet. I'll want him able to talk.");
                return true;
            case ("stairs", Verb.Walk or Verb.Hand) when Returning:
                await Say("clerk", "Hey! Nobody goes up. There's nothing up there for you anyhow.");
                await Think("Nothing up there. He said that a shade too fast.");
                return true;
            case ("stairs", Verb.Walk or Verb.Hand):
                await Say("Her room's empty. I don't need to see an empty room to know it.");
                return true;
            case ("umbrella_stand", Verb.Hand or Verb.Look):
                await Say("Still empty. His umbrella's hooked on a rung out back, and he hasn't been out to fetch it.");
                return true;
        }
        return false;
    }

    private async Task AskTheClerk()
    {
        if (State.HasFlag("motel_return_done"))
        {
            await Talk("motel_clerk_return");
            return;
        }
        await Talk("motel_clerk_return");
        if (!State.HasFlag("motel_return_done")) return;
        await Think("Two men, and the clerk swears he knows nothing else. For once I believe him.");
        await Think("Somebody wanted her back badly enough to come and get her. And I'd gone home to my bottle.");
        if (FindHotspot("door") is { } door) await Game.WalkTo(door.WalkTo);
        await Game.ChangeRoom("church_exterior", "start");
    }

    /// <summary>
    /// Act 1: "show_photo" / "pocket_photo": Micah holds Eleanor's photograph up across the counter, then puts it away.
    /// Act 2: "tie": Micah steps up to the counter, grabs the clerk's tie and hauls his face down onto the counter top.
    /// "release": he lets go, and the clerk straightens up behind the counter.
    /// </summary>
    public override async Task OnCue(string cue)
    {
        if (cue == "show_photo") { await ShowPhoto("clerk"); return; }
        if (cue == "pocket_photo") { await PocketPhoto(); return; }
        if (FindActor("clerk") is not { } clerk) return;
        switch (cue)
        {
            case "tie":
                await Game.WalkTo(TieSpot);
                Player.Face(Facing.Right);
                Player.ZIndex = 2;
                var micah = Player.PlayPose("micah_tie_pull");
                await Wait(0.2);
                // Only the counter-cut pose may draw over the desk; his standing sprite stays behind it.
                var pulled = clerk.PlayPose("clerk_tie_pulled");
                clerk.ZIndex = 1;
                await Task.WhenAll(micah, pulled);
                // Pinned face down on the desk, his lines would cover Micah's face: lift them clear of Micah's hat.
                clerk.SpeechLift = Mathf.Max(0, clerk.HeadPosition.Y - (Player.HeadPosition.Y - 4));
                break;
            case "release":
                Player.SetPose(null);
                Player.Face(Facing.Right);
                clerk.SetPose(null);
                clerk.SpeechLift = 0;
                clerk.ZIndex = 0;
                Player.ZIndex = 0;
                await Wait(0.4);
                break;
        }
    }
}