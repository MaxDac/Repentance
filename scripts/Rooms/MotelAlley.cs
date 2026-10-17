using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 1: the rainy back alley behind the flophouse down the hill from the convent. The front door leads to the
/// lobby; the fire escape's drop ladder is pulled up out of reach (Puzzle 19: push the crate under it, stand on it,
/// and hook the ladder down with the clerk's umbrella).
/// </summary>
public partial class MotelAlley : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_motel_alley")) return;
        State.SetFlag("seen_motel_alley");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("Off the main drag, down an alley that smelled of wet ash and cabbage. The sign buzzed over a door nobody had painted since the war.");
            await Think("A fire escape zigzagged up the brickwork. One window on the first floor was lit.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("street", Verb.Walk or Verb.Hand):
                await Say("Back up the hill to nothing? She's in there, or she's nowhere.");
                return true;

            case ("crate", Verb.Hand):
                await PushCrate();
                return true;
            case ("crate", Verb.Kick):
                await Say("It's more use to me standing than in splinters.");
                return true;
            case ("crate_under", Verb.Hand):
                await Say("Solid enough to stand on. Just about.");
                return true;

            case ("drop_ladder" or "fire_escape", Verb.UseItem) when item == "umbrella":
                await HookLadder();
                return true;
            case ("drop_ladder" or "fire_escape", Verb.UseItem) when item == "revolver":
                await Say("Shoot a fire escape in a mob joint at midnight. That'd make me real popular.");
                return true;
            case ("drop_ladder", Verb.Hand or Verb.Walk):
            case ("fire_escape", Verb.Hand or Verb.Walk):
                if (State.HasFlag("ladder_down")) await Climb();
                else await LadderOutOfReach();
                return true;
            case ("drop_ladder" or "fire_escape", Verb.Kick):
                await Say("I can't reach it with my hands. I'm not reaching it with my feet.");
                return true;
            case ("ladder", Verb.Hand or Verb.Walk):
                await Climb();
                return true;

            case ("trash_cans", Verb.Hand):
                await Say("Wet newspapers and fish heads. Nothing worth the smell.");
                return true;
            case ("trash_cans", Verb.Kick):
                await Say("And have the clerk come out to see who's rattling his cans? He's scared enough already.");
                return true;
            case ("window", Verb.Hand or Verb.Walk):
                await Say("A first floor window. From down here it may as well be the moon.");
                return true;
        }
        return false;
    }

    private async Task LadderOutOfReach()
    {
        if (!State.HasFlag("crate_moved"))
        {
            await Say("The drop ladder's pulled up a good eight feet off the ground. I jumped. My ribs filed a complaint.");
            await Say("I need something to stand on.");
        }
        else if (!State.HasFlag("took_umbrella"))
            await Say("On the crate I'm still a foot short of the bottom rung. Something with a hook would do it.");
        else
            await Say("On the crate I'm still a foot short. That umbrella's crook handle would reach it.");
    }

    private async Task PushCrate()
    {
        if (State.HasFlag("crate_moved")) return;
        await Say("*grunt*");
        if (FindHotspot("crate_under") is { } under) await Game.WalkTo(under.WalkTo);
        Player.Face(Facing.Up);
        await Say("*grunt*");
        State.SetFlag("crate_moved");
        await Say("A fruit crate under the fire escape. Somebody's been using it for that already, by the look of the rungs.");
    }

    private async Task HookLadder()
    {
        if (State.HasFlag("ladder_down"))
        {
            await Say("The ladder's down. The umbrella's done its bit.");
            return;
        }
        if (!State.HasFlag("crate_moved"))
        {
            await Say("Even with the crook on the end, I'm a foot short from the ground. I need to stand on something.");
            return;
        }
        if (FindHotspot("crate_under") is { } under) await Game.WalkTo(under.WalkTo);
        Player.Face(Facing.Up);
        await Say("Up on the crate, crook over the bottom rung, and pull.");
        await Say("*clank*");
        State.TakeItem("umbrella");
        State.SetFlag("ladder_down");
        await Say("Down she comes. The umbrella stays up there, hooked on the rung. The clerk can come and get it.");
    }

    private async Task Climb()
    {
        if (FindHotspot("crate_under") is { } under) await Game.WalkTo(under.WalkTo);
        Player.Face(Facing.Up);
        await Think("Up the crate, up the ladder, one wet rung at a time. One floor up, and I didn't look down.");
        await Game.ChangeRoom("motel_fire_escape", "start");
    }
}