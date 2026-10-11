using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2: the alley behind the Harrington Building. A watchman guards the service door and spots anybody who goes for
/// the fire escape. Burning the trash can sends him inside; stacking crates and wedging the ladder's jammed catch
/// gets Micah up to Harrington's office window.
/// </summary>
public partial class HarringtonRoad : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_harrington_road")) return;
        State.SetFlag("seen_harrington_road");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Say("The back of the Harrington Building. The front has a doorman, a brass plate and a bank's worth of marble.");
            await Say("The back has a trash can and a watchman. Back doors are more my class.");
        });
    }

    private bool Watched => !State.HasFlag("watchman_distracted");

    private async Task Spotted()
    {
        await Say("watchman", "Hey! You there! Get away from there!");
        await Game.WalkTo(new Vector2(250, 236));
        Player.Face(Facing.Left);
        await Say("Just admiring the architecture, officer.");
        await Say("watchman", "Admire it from LaSalle Street. Go on.");
        await Say("He isn't going to look anywhere but the alley while he's standing in it. I need to give him a reason to go inside.");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("watchman", Verb.Talk):
                if (State.HasFlag("seen_watchman_talk"))
                {
                    await Say("watchman", "Still here, mister? This ain't a public park.");
                    return true;
                }
                State.SetFlag("seen_watchman_talk");
                await Say("Evening. Quiet night?");
                await Say("watchman", "Was. Who's asking?");
                await Say("Nobody. Does Mr. Harrington work late?");
                await Say("watchman", "Mr. Harrington does what he likes, and I stand here while he does it. Building's closed.");
                await Say("watchman", "Anything happens in this alley, I'm on that telephone inside before you can spit. So don't spit.");
                return true;
            case ("watchman", Verb.Kick):
                await Say("He has a stick and a telephone. I'd lose the fight and then I'd lose the night.");
                return true;
            case ("watchman", Verb.UseItem) when item == "revolver":
                await Say("Pull a gun on a watchman in the Loop, and I'll be explaining myself to the Chicago police by midnight.");
                return true;
            case ("watchman", Verb.UseItem) when item == "matchbook":
                await Say("He doesn't smoke. Or he doesn't smoke on duty. Either way, he isn't taking a light from me.");
                return true;

            case ("trash_can", Verb.UseItem) when item == "matchbook":
                if (State.HasFlag("fire_lit"))
                {
                    await Say("It's burning well enough already. Any more and I'll take the building down with it.");
                    return true;
                }
                await LightFire();
                return true;
            case ("trash_can", Verb.Hand):
                await Say(State.HasFlag("fire_lit")
                    ? "It's on fire. I'm not touching it."
                    : "Newspapers, straw, and somebody's lunch. One match and it would go up like a Fourth of July.");
                return true;
            case ("trash_can", Verb.Kick):
                await Say(Watched ? "And have the watchman come over to see who's kicking his trash? Subtle." : "It's burning. Kicking it would just set my trousers on fire too.");
                return true;

            case ("crates", Verb.Hand):
                if (Watched)
                {
                    await Spotted();
                    return true;
                }
                await StackCrates();
                return true;
            case ("crates", Verb.Kick):
                await Say("They're more useful in one piece.");
                return true;
            case ("packing_wedge", Verb.Hand):
                if (Watched)
                {
                    await Spotted();
                    return true;
                }
                if (!State.HasFlag("ladder_freed"))
                {
                    State.GiveItem("wedge");
                    State.SetFlag("wedge_taken");
                    await Say("A tapered packing wedge. Just the thing to hold a spring catch clear.");
                }
                return true;
            case ("ladder_catch", Verb.Look or Verb.Hand):
                await Say("A spring catch jammed against the ladder. The little diagram says to hold it back while lowering. A wooden wedge would do.");
                return true;
            case ("ladder_catch", Verb.UseItem) when item == "wedge":
                if (Watched)
                {
                    await Spotted();
                    return true;
                }
                if (!State.HasFlag("crates_stacked"))
                {
                    await Say("The catch is up by the bottom rung. I need those crates stacked to reach it.");
                    return true;
                }
                State.SetFlag("ladder_freed");
                State.TakeItem("wedge");
                await Say("The wedge holds the spring catch clear. It stays there; the ladder can come down now.");
                return true;

            case ("fire_escape" or "window", Verb.Hand or Verb.Walk):
                if (Watched)
                {
                    await Spotted();
                    return true;
                }
                if (!State.HasFlag("crates_stacked"))
                {
                    await Say("I jumped. I'm fifty-one. The ladder's still up there. I need something to stand on.");
                    return true;
                }
                if (!State.HasFlag("ladder_freed"))
                {
                    await Say("I can reach it now, but the spring catch is jammed. That packing wedge could hold it clear.");
                    return true;
                }
                await Climb();
                return true;
            case ("back_door", Verb.Hand):
                await Say(Watched ? "Past the watchman? He'd have me by the collar before I touched the handle." : "Locked behind him. Watchmen trust their own doors.");
                return true;
            case ("back_door", Verb.Kick):
                await Say("That's a steel door. I'd break my foot and the watchman would break the rest.");
                return true;
        }
        return false;
    }

    private async Task LightFire()
    {
        await Say("Old newspapers and straw. Nobody's going to miss them.");
        await Say("*scrape*");
        State.SetFlag("fire_lit");
        await Wait(0.6);
        await Game.WalkTo(new Vector2(110, 248));
        Player.Face(Facing.Left);
        await Wait(0.8);
        await Say("watchman", "Hey! What the -- fire! FIRE!");
        await Say("watchman", "Stay away from that, mister! I'm calling the fire department!");
        if (FindActor("watchman") is { } w)
        {
            w.FaceLeft(true);
            await w.MoveTo(new Vector2(176, 196));
        }
        State.SetFlag("watchman_distracted");
        await Say("He'll stay inside explaining a trash can to the fire department. Time to sort out that ladder.");
    }

    private async Task StackCrates()
    {
        if (State.HasFlag("crates_stacked")) return;
        await Game.WalkTo(new Vector2(440, 222));
        Player.Face(Facing.Up);
        await Say("*grunt*");
        await Game.WalkTo(new Vector2(334, 222));
        Player.Face(Facing.Up);
        await Say("*grunt*");
        State.SetFlag("crates_stacked");
        await Say("Two crates under the ladder. It isn't a staircase, but it'll do.");
    }

    private async Task Climb()
    {
        await Game.WalkTo(new Vector2(334, 218));
        Player.Face(Facing.Up);
        await Say("Up the crates, down comes the ladder. One floor up to the office window, and trying not to look down.");
        await Game.ChangeRoom("harrington_office", "window");
    }
}
