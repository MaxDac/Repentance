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
    public override Track? Music => Track.MansionDread;

    private static readonly Texture2D Shot = GD.Load<Texture2D>("res://assets/art/sprites/harrington_shot.png");
    private static readonly Texture2D EleanorShot = GD.Load<Texture2D>("res://assets/art/sprites/eleanor_shot.png");
    private static readonly Texture2D StruckDown = GD.Load<Texture2D>("res://assets/art/sprites/harrington_struck_down.png");
    private const string AimLower = "micah_aim_lower";
    private const string AimBack = "micah_aim_back";
    private const int PrayerSteps = 6;
    private int _prayerStep;

    private static readonly Vector2 BesideScreen = new(106, 222);
    private static readonly Vector2 PastScreenFront = new(118, 241);
    private static readonly Vector2 MicahAims = new(160, 236);
    private static readonly Vector2 PrayerStop = new(52, 236);
    private static readonly Vector2 Door = new(30, 236);
    private static readonly Vector2 EleanorUp = new(396, 240);
    // where her feet are while she gets out of bed (tools/art/mansion.py ELEANOR_RISE_AT)
    private static readonly Vector2 EleanorRise = new(382, 226);
    private const float EleanorHurry = 120;
    // The coda: the old man at the foot of the bed with his back to her, listening at the door for Micah's car; the
    // nightstand a step from where she stands, and the spot just behind him from where the candlestick reaches him
    // (eleanor_strike reaches about 35px ahead of her feet).
    public static readonly Vector2 HarringtonCoda = new(330, 238);
    public static readonly Vector2 Nightstand = new(402, 216);
    public static readonly Vector2 BehindHim = new(358, 238);
    private bool _striking;

    private bool Coda => State.HasFlag("eleanor_coda");
    private bool Struck => State.HasFlag(Endings.EleanorStruck);

    // Until she strikes, the old man stands between her and the door: she stays on the bed side of him.
    public override Vector2 ClampWalkTarget(Vector2 target) =>
        Coda && !Struck && target.X < BehindHim.X ? new Vector2(BehindHim.X, target.Y) : target;

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (Coda) return await CodaInteract(verb, target);
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
        if (entry == "eleanor_coda")
        {
            await Game.Run(async () =>
            {
                await Wait(0.6);
                await Talk("coda_wake");
            });
            return;
        }
        if (entry != "start") return;
        await Game.Run(Confrontation);
    }

    /// <summary>
    /// The coda's state comes from flags, since textures and poses aren't saved: the old man faces the door Micah left
    /// by, and lies face-down on the carpet once she has struck him (the candlestick FlagSprite hides on the same flag).
    /// </summary>
    protected override void OnRefresh()
    {
        if (!Coda || FindActor("harrington") is not { } harrington) return;
        harrington.Position = HarringtonCoda;
        harrington.WalkTo = BehindHim;
        harrington.FaceLeft(true);
        if (Struck && !_striking && harrington.Texture != StruckDown) harrington.SetTexture(StruckDown);
    }

    private async Task<bool> CodaInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("bed", Verb.Hand or Verb.Walk) when !Struck:
                await ReturnToBed();
                return true;
            case ("bed", Verb.Hand or Verb.Walk):
                await Say("eleanor", "Not that bed. Not ever again.");
                return true;
            case ("bed", Verb.Look):
                await Say("eleanor", "Walnut and rose satin. I know every inch of that canopy. I've had a lot of time to look at it.");
                return true;

            case ("candlestick", Verb.Hand) when !Struck:
                await Strike();
                return true;
            case ("candlestick", Verb.Look):
                await Say("eleanor", "A brass candlestick. Heavy. He bought it in Venice, he said. He tells everyone what everything cost.");
                return true;

            case ("harrington", Verb.Look) when Struck:
                await Say("eleanor", "Face down on his own carpet. He's breathing, or he isn't. I'm not going to bend down and find out.");
                return true;
            case ("harrington", Verb.Look):
                await Say("eleanor", "His back. All these years, and I've never once seen him turn it on me.");
                return true;
            case ("harrington", Verb.Talk) when Struck:
                await Say("eleanor", "Nothing to say, Mr. Harrington? That's a first.");
                return true;
            case ("harrington", Verb.Talk):
                await Say("eleanor", "Yes, Mr. Harrington.");
                await Say("harrington", "Bed, my dear. I said I'd be a moment.");
                return true;
            case ("harrington", Verb.Hand or Verb.Kick) when !Struck:
                await Say("eleanor", "With my bare hands? He'd laugh. He'd laugh, and then he'd ring for Bruno.");
                return true;

            case ("door", Verb.Hand or Verb.Walk) when !Struck:
                await Say("eleanor", "Past him, in a sheet? He'd have me by the hair before I reached the stairs.");
                return true;
            case ("door", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_study", "eleanor_coda");
                return true;
            case ("landing", Verb.Hand or Verb.Walk):
                await Say("eleanor", "Not that way. His men sleep across the landing.");
                return true;
        }
        return false;
    }

    /// <summary>Ending 1 for her: back under the sheet, the way she got out of it, and Micah's story goes on to Rose's.</summary>
    private async Task ReturnToBed()
    {
        await Game.WalkTo(EleanorRise);
        Player.Face(Facing.Left);
        await Player.PlayPose("eleanor_mansion_return");
        Player.Visible = false;
        State.SetFlag("eleanor_up", false);
        await Talk("coda_bed");
        await Game.Hud.Fade(1, 1.5);
        Story.Interlude.EndCoda();
        await Act3.End();
    }

    /// <summary>
    /// Endings 8 and 9: the candlestick off the nightstand, and down on the back of his head while he watches the door.
    /// </summary>
    private async Task Strike()
    {
        var harrington = FindActor("harrington");
        harrington?.FaceLeft(true);
        await Game.WalkTo(Nightstand);
        Player.Face(Facing.Up);
        // he doesn't turn round: he's listening at the door for the car
        await Say("harrington", "There. A Ford. Of course it's a Ford.");
        _striking = true;
        State.SetFlag(Endings.EleanorStruck);
        await Wait(0.3);
        await Game.WalkTo(BehindHim);
        Player.Face(Facing.Left);
        await Player.PlayPose("eleanor_strike");
        if (harrington != null)
        {
            await harrington.PlayPose("harrington_struck");
            harrington.SetTexture(StruckDown);
        }
        _striking = false;
        await Wait(0.8);
        Player.SetPose(null);
        Player.Face(Facing.Left);
        await Talk("coda_strike");
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
        if (!await Player.PlayPose("micah_draw")) return;
        Player.SetPose("micah_aim");
        await Wait(0.4);
        harrington?.FaceLeft(true);
        if (eleanor != null)
        {
            // She gets out of bed clutching the sheet; the strip starts exactly where the occupied bed sprite leaves off.
            eleanor.Position = EleanorRise;
            eleanor.FaceLeft(true);
            var rising = eleanor.PlayPose("eleanor_mansion_rise");
            State.SetFlag("eleanor_up");
            await rising;
            eleanor.SetPose(null);
            await eleanor.MoveTo(EleanorUp, EleanorHurry * 0.5f);
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
            await PrayerEnding();
            if (Endings.EleanorHeldOut(State.HasFlag))
            {
                // She never gave in: the story stays in the room after he's gone, and the player is Eleanor.
                Story.Interlude.BeginCoda();
                await Game.ChangeRoom("mansion_bedroom", "eleanor_coda");
                return;
            }
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
        if (Endings.EleanorHeldOut(State.HasFlag))
        {
            // Worn out, she only wants to leave: no persuasion. She follows him to the kitchen (endings 10 and 11).
            await Talk("eleanor_weary");
        }
        else
            await Talk("eleanor_persuade");

        if (State.HasFlag(Endings.Repented))
        {
            // straight out of the house and to the nearest precinct: no kitchen, no escape
            await Wait(0.6);
            await Game.WalkTo(Door);
            await Act3.End();
            return;
        }
        if (State.HasFlag("eleanor_refused") && !State.HasFlag(Endings.ShotEleanor))
        {
            // four turns and she still won't come: the Club's men on the stairs, and the last choice
            await Say("*Footsteps on the landing, behind the other door. A man's voice. Then two.*");
            await Talk("eleanor_footsteps");
        }
        if (State.HasFlag(Endings.ShotEleanor))
        {
            await MurderSuicide(eleanor);
            return;
        }
        if (State.HasFlag(Endings.ShotHimself))
        {
            await Suicide();
            return;
        }

        if (Endings.EleanorFollows(State.HasFlag) && eleanor != null)
            await eleanor.MoveTo(MicahAims + new Vector2(36, 2), EleanorHurry);
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
                var x = Mathf.Lerp(MicahAims.X, PrayerStop.X, Mathf.Min(_prayerStep, PrayerSteps) / (float)PrayerSteps);
                // Each verse he steps back and lowers the gun one level along the way, then holds it there.
                await Player.BackstepTo(new Vector2(x, MicahAims.Y), 0.9, AimBack, Mathf.Min(_prayerStep, PrayerSteps));
                Player.SetPose(AimLower);
                Player.SetPoseFrame(_prayerStep);
                break;
            case "door":
                Player.SetPose(AimLower);
                Player.SetPoseFrame(int.MaxValue);
                await Wait(0.5);
                break;
        }
    }

    /// <summary>
    /// The end of the prayer Micah left the room on, over black, a line at a time; after Tony's murder the Amen waits for
    /// the station steps (ending 12).
    /// </summary>
    public static readonly string[] Doxology =
        { "For Thine is the Kingdom, the Power and the Glory.", "Forever and ever.", "Amen." };
    public const double DoxologyFade = 3.5;

    private async Task PrayerEnding()
    {
        await Game.Hud.Fade(1, 1.0);
        await Wait(0.6);
        var verses = State.HasFlag(Endings.KilledTony) ? Doxology[..^1] : Doxology;
        await Game.Hud.ShowVerses(verses, DoxologyFade, 1.5);
        await Wait(0.5);
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
        await LastShot();
    }

    /// <summary>Ending 7 with Eleanor left alive: the men on the stairs, and Micah turns the gun on himself.</summary>
    private async Task Suicide()
    {
        Player.Face(Facing.Right);
        Player.SetPose("micah_aim");
        await Wait(0.6);
        await LastShot();
    }

    public const string LastWords = "Forgive me... all of you...";

    /// <summary>
    /// Micah lowers the gun and looks away from the bed, at an empty corner of the room, and asks it to forgive him.
    /// Then the revolver comes up to his temple; the screen cuts to black and the shot is heard over it.
    /// </summary>
    private async Task LastShot()
    {
        Player.SetPose(null);
        Player.Face(Facing.Left);
        await Wait(1.0);
        await Say(LastWords);
        Player.SetPose("micah_aim_self");
        await Wait(1.4);
        await Game.Hud.Fade(1, 0.08);
        await Wait(1.2);
        Game.Sfx.Play(Sound.Gunshot);
        await Wait(2.0);
        await Act3.End();
    }
}
