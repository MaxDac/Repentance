using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2: Rose's terrace house. Micah can ring the bell and push her for forgiveness, or walk away. In Act 3, if he
/// gives up on Eleanor, he comes back here beaten to ask her out for a coffee.
/// </summary>
public partial class RoseHouse : Room
{
    public override Track? Music => Track.RoseStreet;

    public override async Task OnEnter(string entry)
    {
        if (entry == "coffee")
        {
            await Coffee();
            return;
        }
        if (State.HasFlag("seen_rose_house")) return;
        State.SetFlag("seen_rose_house");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("Number 14. I used to come home to this door. Mostly at three in the morning, mostly drunk.");
            await Think("Rose kept the house. Rose kept Tommy. I kept the bottle. It seemed fair at the time.");
            await Think("Funny. It's rained on me all week, and it stops at Rose's street.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("bell" or "door", Verb.Hand) when State.HasFlag("rose_done") || State.HasFlag("rose_avoided"):
                await Say("She said what she had to say. Ringing again would just be me not listening. Again.");
                return true;
            case ("bell", Verb.Hand):
            case ("door", Verb.Hand):
                await RingTheBell();
                return true;
            case ("door", Verb.Kick):
                await Say("I already broke enough in that house without starting on the furniture.");
                return true;
            case ("door", Verb.Talk):
                await Say("Talking to a door. It's how most of our conversations went, toward the end.");
                return true;

            case ("exit", Verb.Walk or Verb.Hand) when !State.HasFlag("rose_done") && !State.HasFlag("rose_avoided"):
                await LeaveWithoutRinging();
                return true;
            case ("exit", Verb.Walk or Verb.Hand):
                await Game.ChangeRoom("chicago_map", "start");
                return true;
        }
        return false;
    }

    /// <summary>
    /// Walking off before ringing has to be chosen: Micah never sees Rose, she never answers, and it counts as not
    /// insisting (no callback, the bell is closed to him).
    /// </summary>
    private async Task LeaveWithoutRinging()
    {
        await Talk("rose_leave");
        if (!State.HasFlag("rose_avoided")) return;
        await Think("Not tonight. I left the bell alone, the way I left everything else in that house.");
        await Game.WalkTo(new Vector2(8, 236));
        await Game.ChangeRoom("chicago_map", "start");
    }

    private async Task RoseOpens()
    {
        State.SetFlag("rose_door");
        if (FindActor("rose") is { } rose)
        {
            rose.FaceLeft(false);
            await rose.PlayPose("rose_open_door");
            rose.SetPose(null);
        }
        await Wait(0.3);
        await Game.WalkTo(TalkSpot);
        Player.Face(Facing.Up);
    }

    /// <summary>The bell, just right of the doorway: Micah talks to Rose from here so he never stands in front of her.</summary>
    public static readonly Vector2 TalkSpot = new(258, 220);

    private async Task RingTheBell()
    {
        await Game.WalkTo(TalkSpot);
        Player.Face(Facing.Up);
        await Say("*Ring*");
        await Wait(1.2);
        await RoseOpens();
        await Talk("rose_house");
        State.SetFlag("rose_done");
        await WalkAway();
    }

    /// <summary>
    /// Micah leaves the stoop. If he pushed her hard enough, Rose calls him back once before she closes the door;
    /// otherwise she shuts it on him right away.
    /// </summary>
    private async Task WalkAway()
    {
        if (!State.HasFlag("rose_wait"))
        {
            State.SetFlag("rose_door", false);
            await Think("The door shut. Not hard. Just once, and for good.");
            await Game.WalkTo(new Vector2(8, 236));
            await Game.ChangeRoom("chicago_map", "start");
            return;
        }
        await Game.WalkTo(new Vector2(110, 236));
        await Say("rose", "Wait!");
        if (FindActor("rose") is { } rose) Player.FaceTowards(rose.Position);
        // he turns, and there she is: a long look, and nobody says anything
        Game.Hud.ShowCloseUp(CloseUps.Rose);
        await Wait(2.0);
        await Say("rose", "Don't get into trouble again.");
        await Wait(0.6);
        await Say("...");
        await Wait(1.0);
        Game.Hud.HideCloseUp();
        await Wait(0.8);
        State.SetFlag("rose_door", false);
        await Think("The door closes. Softly. She always closed doors softly. It was worse than slamming.");
        await Game.WalkTo(new Vector2(8, 236));
        await Game.ChangeRoom("chicago_map", "start");
    }

    /// <summary>
    /// Ending 1, giving up on Eleanor: Micah asks Rose out for a coffee, and that's the end of Act Three. In endings 8
    /// and 9 (Eleanor struck the old man after Micah left) the same scene leads on to hers.
    /// </summary>
    private Task Coffee() => Game.Run(async () =>
    {
        await Wait(0.6);
        await Think("Same door. Same bell. A different man pressing it, I hope.");
        if (State.HasItem("cloth"))
        {
            State.TakeItem("cloth");
            await Think("Her rag. Still in my pocket, still smellin' of her.");
            await Think("Into the gutter with it. No more chasin' that dame.");
        }
        await Game.WalkTo(TalkSpot);
        Player.Face(Facing.Up);
        await Say("*Ring*");
        await Wait(1.2);
        await RoseOpens();
        await Talk("rose_coffee");
        await Think("Why not. Two small words. I'll walk home on them like they're solid ground.");
        if (State.HasFlag(Endings.EleanorStruck))
        {
            // endings 8 and 9: Micah's last entry ends here, and the story goes on with Eleanor's last scene
            await Wait(1.0);
            await Game.Hud.Fade(1, 1.5);
            await Act3.EleanorAfterRose();
            return;
        }
        await Act3.Finish();
    });
}
