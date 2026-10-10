using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The old man's bedroom: Eleanor under the sheet in the four-poster, Harrington in his dressing gown. Micah listens from
/// behind the folding screen, steps out with the revolver, and the act's last choice is his.
/// </summary>
public partial class MansionBedroom : Room
{
    private static readonly Texture2D Falling = GD.Load<Texture2D>("res://assets/art/sprites/harrington_falling.png");
    private static readonly Texture2D Shot = GD.Load<Texture2D>("res://assets/art/sprites/harrington_shot.png");

    private static readonly Vector2 BehindScreen = new(107, 214);
    private static readonly Vector2 MicahAims = new(160, 236);
    private static readonly Vector2 EleanorUp = new(396, 240);

    public override async Task OnEnter(string entry)
    {
        if (entry != "start") return;
        await Game.Run(Confrontation);
    }

    private async Task Confrontation()
    {
        State.SetFlag("entered_bedroom");
        var harrington = FindActor("harrington");
        var eleanor = FindActor("eleanor");
        await Game.WalkTo(BehindScreen);
        Player.Visible = false;
        await Wait(0.8);
        await Talk("harrington_eleanor");

        Player.Teleport(MicahAims, Facing.Right);
        Player.Visible = true;
        Player.SetPose("micah_aim");
        await Wait(0.4);
        harrington?.FaceLeft(true);
        if (eleanor != null)
        {
            eleanor.Position = EleanorUp;
            eleanor.FaceLeft(true);
        }
        State.SetFlag("eleanor_up");
        await Wait(0.6);
        Act3.UpdateGates();
        await Talk("oldman_taunt");

        if (State.HasFlag(Endings.SparedOldMan))
        {
            Player.SetPose(null);
            await Wait(0.5);
            await Game.WalkTo(new Vector2(30, 236));
            await Act3.End();
            return;
        }

        await Say("*BANG*");
        harrington?.SetTexture(Falling);
        await Wait(0.45);
        harrington?.SetTexture(Shot);
        await Wait(1.0);
        Player.SetPose(null);
        await Talk("eleanor_persuade");

        if (State.HasFlag(Endings.EleanorConvinced))
        {
            if (eleanor != null) await eleanor.MoveTo(MicahAims + new Vector2(36, 2), 50);
        }
        else
        {
            await Say("*Footsteps on the landing, behind the other door. A man's voice. Then two.*");
            await Say("That's my cue. Goodbye, Eleanor.");
        }
        State.SetFlag("escaping");
        await Game.WalkTo(new Vector2(30, 236));
        await Game.ChangeRoom("mansion_kitchen", "escape");
    }
}
