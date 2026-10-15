using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The old man's bedroom: Eleanor under the sheet in the walnut bed, Harrington in his dressing gown. Micah listens from
/// crouched beside the folding screen (folded tight and edge-on to us, between him and the bed), rises, steps out with
/// the revolver, and the act's last choice is his.
/// </summary>
public partial class MansionBedroom : Room
{
    private static readonly Texture2D Shot = GD.Load<Texture2D>("res://assets/art/sprites/harrington_shot.png");
    private static readonly Texture2D EleanorShot = GD.Load<Texture2D>("res://assets/art/sprites/eleanor_shot.png");
    private const string AimLower = "micah_aim_lower";
    private const int PrayerSteps = 6;
    private int _prayerStep;

    private static readonly Vector2 BesideScreen = new(106, 222);
    private static readonly Vector2 PastScreenFront = new(118, 241);
    private static readonly Vector2 MicahAims = new(160, 236);
    private static readonly Vector2 PrayerStop = new(52, 236);
    private static readonly Vector2 Door = new(30, 236);
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
        // In beside the screen, crouched low: hidden from the bed by it, in full view from the door.
        await Game.WalkTo(BesideScreen);
        Player.Face(Facing.Right);
        if (!await Player.PlayPose("micah_crouch")) return;
        Player.SetPose("micah_crouched");
        await Wait(0.8);
        await Think("Behind a folding screen, breathing through my mouth. A walnut bed the size of my office. She's in it.");
        await Talk("harrington_eleanor");

        if (!await Player.PlayPose("micah_crouch_rise")) return;
        Player.SetPose(null);
        // He rises, steps out round its near end, then forward into the room with the revolver up.
        await Game.WalkTo(PastScreenFront);
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
        _prayerStep = 0;
        await Talk("oldman_taunt");

        if (State.HasFlag(Endings.SparedOldMan))
        {
            // oldman_taunt went on into oldman_prayer: the Our Father, backing towards the door (OnCue).
            Player.SetPose(null);
            await Game.WalkTo(Door);
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

        if (State.HasFlag(Endings.Repented))
        {
            // straight out of the house and to the nearest precinct: no kitchen, no escape
            await Wait(0.6);
            await Game.WalkTo(Door);
            await Act3.End();
            return;
        }
        if (State.HasFlag(Endings.ShotEleanor))
        {
            await MurderSuicide(eleanor);
            return;
        }

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
        await Game.WalkTo(Door);
        await Game.ChangeRoom("mansion_kitchen", "escape");
    }

    /// <summary>
    /// The prayer retreat: each "CUE: step" in <c>oldman_prayer</c> takes Micah one step back towards the door, still
    /// facing the old man, with the revolver a little lower; "CUE: door" finishes lowering it.
    /// </summary>
    public override async Task OnCue(string cue)
    {
        switch (cue)
        {
            case "step":
                _prayerStep++;
                Player.SetPose(AimLower);
                Player.SetPoseFrame(_prayerStep);
                var x = Mathf.Lerp(MicahAims.X, PrayerStop.X, Mathf.Min(_prayerStep, PrayerSteps) / (float)PrayerSteps);
                await Player.BackstepTo(new Vector2(x, MicahAims.Y), 0.7);
                break;
            case "door":
                Player.SetPose(AimLower);
                Player.SetPoseFrame(int.MaxValue);
                await Wait(0.5);
                break;
        }
    }

    /// <summary>
    /// Ending 7: the gun comes up again and Eleanor goes down beside the old man. Then Micah turns it on himself; the
    /// screen cuts to black, the shot is heard over it, and the act ends there.
    /// </summary>
    private async Task MurderSuicide(Actor? eleanor)
    {
        Player.Face(Facing.Right);
        Player.SetPose("micah_aim");
        await Wait(0.6);
        await Say("*BANG*");
        if (eleanor != null)
        {
            await eleanor.PlayPose("eleanor_fall");
            eleanor.SetTexture(EleanorShot);
        }
        await Wait(1.2);
        await Think("She goes down on her knees, then onto her face, next to him. Like she's praying. She never prayed in her life.");
        await Think("Two of them on the carpet now. And the only one left in this room who deserves it is holding the gun.");
        Player.SetPose("micah_aim_self");
        await Wait(1.4);
        await Think("Our Father, who art in heaven, hallowed be Thy name...");
        await Wait(0.8);
        await Game.Hud.Fade(1, 0.08);
        await Wait(1.2);
        Game.Sfx.Play(Sound.Gunshot);
        await Wait(2.0);
        await Act3.End();
    }
}
