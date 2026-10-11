using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Club's stage. Eleanor stands in the spotlight with three masked men around her, the members watching from the
/// seats. In Act 2 Micah only gets to see it before the journal stops; in Act 3 the leader recognises him.
/// </summary>
public partial class ClubStage : Room
{
    public override async Task OnEnter(string entry)
    {
        if (entry == "act3")
        {
            await Game.Run(Caught);
            return;
        }
        if (State.StoryAct >= 3) return;
        await Game.Run(EndOfActTwo);
    }

    /// <summary>Micah walks up to the stage and sees her. Then the journal's page ends, and it's dark in the attic.</summary>
    private async Task EndOfActTwo()
    {
        await Wait(0.5);
        await Say("The seats were full, and nobody was sitting. Everybody stood, facing the light.");
        await Game.WalkTo(new Vector2(212, 208));
        Player.Face(Facing.Up);
        await Wait(0.8);
        await Say("And in the light, Eleanor. No mask. No fear in her face either. Three of them around her, like pall-bearers.");
        await Say("She wasn't a prisoner. Or she was, and she'd stopped minding. I couldn't tell which was worse.");
        await Wait(1.0);
        await Game.Hud.Fade(1, 2.0);
        await Wait(1.0);
        await Game.ChangeRoom("attic", "night2");
    }

    /// <summary>Act 3: the leader turns to Micah. Whatever he does, Bruno knocks him out from behind.</summary>
    private async Task Caught()
    {
        await Wait(1.0);
        await Say("leader", "Are you satisfied, now, mister Jones?");
        await Wait(0.4);
        // the whole room turns to look at him
        foreach (var child in World.GetChildren())
            if (child is Actor a && a.Id != "brute" && a.Visible)
                a.FaceLeft(a.Position.X > Player.Position.X);
        await Wait(1.6);
        await Say("Every mask in the room, turned my way. White, blank, and all of them smiling.");
        await Talk("club_caught");
        State.SetFlag("brute_stage");
        if (FindActor("brute") is { } brute)
            await brute.MoveTo(new Vector2(Player.Position.X - 24, Player.Position.Y + 4), 70);
        await Say("brute", "Night night, pal.");
        if (!await Player.PlayPose("micah_masked_collapse")) return;
        await Game.Hud.Fade(1, 0.08);
        await Wait(1.6);
        State.SetFlag("masked", false);
        State.SetFlag("beaten");
        await Game.ChangeRoom("church_exterior", "beaten");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("eleanor", Verb.Talk):
                await Say("Not from down here. Not with them around her.");
                return true;
            case ("leader" or "ritual1" or "ritual2" or "audience", Verb.Talk):
                await Say("Silence. The only sound in the room is the spotlight humming.");
                return true;
        }
        return false;
    }
}
