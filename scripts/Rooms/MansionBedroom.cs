using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The old man's bedroom: Eleanor under the sheet in the walnut bed, Harrington in his dressing gown. Micah listens from
/// behind the folding screen, steps out with the revolver, and the act's last choice is his.
/// </summary>
public partial class MansionBedroom : Room
{
    private static readonly Texture2D Shot = GD.Load<Texture2D>("res://assets/art/sprites/harrington_shot.png");

    private static readonly Vector2 BehindScreen = new(107, 214);
    private static readonly Vector2 PastScreenLeft = new(52, 214);
    private static readonly Vector2 PastScreenRight = new(162, 216);
    private static readonly Vector2 MicahAims = new(160, 236);
    private static readonly Vector2 EleanorUp = new(396, 240);
    private const float EleanorHurry = 120;

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("bed", Verb.Hand):
                await Say("Not my bed, not my business. I've slept on worse, and with a cleaner conscience.");
                return true;
        }
        return false;
    }

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
        // Round the end of the screen and in behind it: low enough that his hat and shoulders show over the top.
        await Game.WalkTo(PastScreenLeft);
        await Game.WalkTo(BehindScreen);
        Player.Face(Facing.Right);
        await Wait(0.8);
        await Think("Behind a folding screen, breathing through my mouth. A walnut bed the size of my office. She's in it.");
        await Talk("harrington_eleanor");

        // He steps out round the other end, then forward into the room with the revolver up.
        await Game.WalkTo(PastScreenRight);
        await Game.WalkTo(MicahAims);
        Player.Face(Facing.Right);
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
            await Think("I put the gun away. He's still talking when I reach the door. Let him. I know where I'm going.");
            await Wait(0.5);
            await Game.WalkTo(new Vector2(30, 236));
            await Act3.End();
            return;
        }

        await Say("*BANG*");
        if (harrington != null)
        {
            await harrington.PlayPose("harrington_fall");
            harrington.SetTexture(Shot);
        }
        await Wait(1.0);
        Player.SetPose(null);
        await Think("The old man folds onto his own carpet. Cordite and lilies. My hands are steady. That's the worst of it.");
        await Talk("eleanor_persuade");

        if (State.HasFlag(Endings.EleanorConvinced))
        {
            if (eleanor != null) await eleanor.MoveTo(MicahAims + new Vector2(36, 2), EleanorHurry);
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
