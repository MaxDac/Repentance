using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Behind the Blue Lantern. In Act 1, after Sal's "word" with Micah: one street lamp that can't make up its mind, Micah
/// on his knees, and Tony the bartender telling him where Eleanor went. In Act 3 Micah comes back alone: he puts the
/// lamp out, lures Sal into the dark with the trash cans, knocks him cold and knocks Sal's knock for Tony.
/// </summary>
public partial class Alley : Room
{
    public override Track? Music => InAct3 ? Track.Investigation : Track.BlueLanternAlley;

    private static readonly Texture2D SalOut = GD.Load<Texture2D>("res://assets/art/sprites/sal_out.png");
    private static readonly Texture2D BartenderShot = GD.Load<Texture2D>("res://assets/art/sprites/bartender_shot.png");
    private static readonly Texture2D BartenderDead = GD.Load<Texture2D>("res://assets/art/sprites/bartender_dead.png");

    /// <summary>The far end of the passage on the left, where the alley opens onto the street.</summary>
    private static readonly Vector2 StreetMouth = new(50, 192);

    private static readonly Vector2 SalAtTrash = new(398, 224);
    private static readonly Vector2 BehindSal = new(352, 222);
    private static readonly Vector2 TonyOut = new(318, 208);
    private static readonly Vector2 MicahAims = new(258, 214);
    private static readonly Vector2 OverTony = new(428, 218);

    /// <summary>Act 1: Sal's place by Micah's head, and the spot he kicks from: behind Micah, half turned to the
    /// screen, so his right foot goes into Micah's belly out of sight behind Micah's body.</summary>
    private static readonly Vector2 SalStands = new(242, 224);
    private static readonly Vector2 SalKicks = new(250, 220);

    /// <summary>Seconds into sal_kick when his toe lands: the idle and wind-up frames.</summary>
    private const double KickLands = 0.45;

    private Sprite2D? _lamp;
    private double _flickerIn;
    private readonly RandomNumberGenerator _rng = new();

    private bool InAct3 => State.HasFlag("alley3");
    private bool Dark => State.HasFlag("alley3_dark");

    public override void _Ready()
    {
        base._Ready();
        _lamp = GetNodeOrNull<Sprite2D>("Lamp");
        // propped open in Act 1 until Sal and Tony go back in and shut it; shut in Act 3
        ShowDoorOpen(!InAct3 && !State.HasFlag("alley_done"));
        if (!InAct3) return;
        // a reload mid-puzzle puts Sal back where the story left him
        if (FindActor("sal") is { } sal && State.HasFlag("alley3_sal_out"))
        {
            sal.Position = SalAtTrash;
            sal.FaceLeft(false);
            sal.WalkTo = BehindSal;
            if (State.HasFlag("alley3_sal_down")) sal.SetTexture(SalOut);
        }
        if (State.HasFlag(Endings.WarnedTony) || State.HasFlag(Endings.WalkedAway))
            State.SetFlag("alley3_tony_inside", false);
        PlaceTony();
    }

    protected override void OnRefresh()
    {
        if (!InAct3)
        {
            if (FindActor("sal") is { } sal) sal.Visible = !State.HasFlag("alley_done");
            if (FindActor("bartender") is { } tony) tony.Visible = !State.HasFlag("alley_done");
        }
        // with the lamp out the alley goes blue-black, Micah included
        Modulate = Dark ? new Color(0.5f, 0.52f, 0.68f) : Colors.White;
    }

    public override void _Process(double delta)
    {
        if (_lamp == null) return;
        if (Dark)
        {
            _lamp.Visible = false;
            return;
        }
        _flickerIn -= delta;
        if (_flickerIn > 0) return;
        // mostly on, with short stuttering blackouts
        _lamp.Visible = !_lamp.Visible;
        _flickerIn = _lamp.Visible ? _rng.RandfRange(0.4f, 2.6f) : _rng.RandfRange(0.04f, 0.3f);
    }

    /// <summary>Act 1: Micah is already on his knees when the alley fades in.</summary>
    public override void OnArriving(string entry)
    {
        if (entry != "act3" && !InAct3 && !State.HasFlag("alley_done")) Player.SetPose("micah_kneel");
    }

    public override async Task OnEnter(string entry)
    {
        if (entry == "act3" && State.HasFlag(Endings.KilledTony))
        {
            await Game.Run(() => Think("Back again. Like they say killers do. Tony hasn't moved, and Sal's still dreaming."));
            return;
        }
        if (entry == "act3" && (State.HasFlag("shot_bartender") || State.HasFlag(Endings.WarnedTony)
                                  || State.HasFlag(Endings.WalkedAway)))
        {
            await Game.Run(() => Think("Tony's still by the door. I've done enough here."));
            return;
        }
        if (entry == "act3")
        {
            await Game.Run(async () =>
            {
                await Wait(0.6);
                await Think("The Blue Lantern's back door. Last time I was here, I was on my knees.");
                await Think("Sal's inside, and Tony behind him. I need Tony out here. Alone. Without his gorilla.");
            });
            return;
        }
        if (State.HasFlag("alley_done")) return;
        await Game.Run(async () =>
        {
            Player.SetPose("micah_kneel");
            await Wait(0.8);
            if (FindActor("sal") is { } bouncer)
            {
                // so it's clear what happened out here: from behind Micah, two in the gut, then Sal steps back
                await bouncer.MoveTo(SalKicks, 50);
                bouncer.FaceLeft(true);
                for (int kick = 0; kick < 2; kick++)
                    if (!await Kick(bouncer)) return;
                await Wait(0.3);
                await bouncer.MoveTo(SalStands, 50);
                bouncer.FaceLeft(true);
            }
            await Wait(0.6);
            await Think("Gravel in my palms, copper in my mouth. Sal's fists did the talking, his shoes had the last word. Now Tony wants his turn.");
            await Talk("alley");
            // back inside through the club's back door
            if (FindActor("sal") is { } sal) _ = sal.MoveTo(new Vector2(322, 198), 50);
            if (FindActor("bartender") is { } tony) await tony.MoveTo(new Vector2(338, 196), 45);
            await Wait(0.3);
            // they go in, kick the brick away and pull the door shut behind them
            if (FindActor("sal") is { } salIn) salIn.Visible = false;
            if (FindActor("bartender") is { } tonyIn) tonyIn.Visible = false;
            Game.Sfx.Play(Sound.DoorClose);
            ShowDoorOpen(false);
            await Wait(0.4);
            if (!await Player.PlayPose("micah_kneel_rise")) return;
            await OnHisFeet();
        });
    }

    /// <summary>Act 1: Micah up off the gravel, alone in the alley. The street exit runs it too, in case the cutscene
    /// stopped short.</summary>
    private async Task OnHisFeet()
    {
        if (FindActor("sal") is { } sal) sal.Visible = false;
        if (FindActor("bartender") is { } tony) tony.Visible = false;
        ShowDoorOpen(false);
        Player.SetPose(null);
        Player.Face(Facing.Right);
        await Think("A convent. Of all the places to hide a woman like that.");
        State.SetFlag("alley_done");
    }

    /// <summary>Act 3, Tony told: out of the alley, to the office in the storm. The street exit runs it too.</summary>
    private async Task AfterTheShot()
    {
        Player.SetPose(null);
        await Game.WalkTo(StreetMouth);
        // first the office, in the storm, alone with the bottle; then the Gold Coast
        await Game.ChangeRoom("office_storm", "window");
    }

    /// <summary>Act 3, Tony dead: out of the alley onto the night's map, the church or the Gold Coast.</summary>
    private async Task AfterTheKill()
    {
        Player.SetPose(null);
        await Game.WalkTo(StreetMouth);
        await Game.ChangeRoom("chicago_map", "start");
    }

    /// <summary>Act 3, the gun lowered: out of the alley and out of the story. The street exit runs it too.</summary>
    private async Task WalkAway()
    {
        Player.SetPose(null);
        await Game.WalkTo(StreetMouth);
        await Act3.End();
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (!InAct3)
        {
            if (target.Id == "back_door" && verb == Verb.Look)
            {
                await Say(State.HasFlag("alley_done")
                    ? "Shut. Through the steel, the band's still going over the same sixteen bars. Nobody's coming back out for me."
                    : "Propped open on a brick. Light, smoke and a band going over the same sixteen bars, a long way down the hall.");
                return true;
            }
            if (target.Id == "street" && (verb is Verb.Walk or Verb.Hand))
            {
                if (!State.HasFlag("alley_done")) await OnHisFeet();
                // Micah sleeps off the beating and goes up to the convent the evening after
                if (!State.HasFlag("seen_convent_exterior"))
                {
                    await Game.Hud.Fade(1, 1.2);
                    Game.Hud.ShowCaption("The next evening");
                    await Wait(2.2);
                    Game.Hud.ShowCaption(null);
                }
                await Game.ChangeRoom("convent_road", "street");
                return true;
            }
            return false;
        }
        bool salOut = State.HasFlag("alley3_sal_out"), salDown = State.HasFlag("alley3_sal_down");
        switch (target.Id, verb)
        {
            case ("street", Verb.Look):
                await Say("The street. Out there, the whole city's minding its own business.");
                return true;
            case ("street", Verb.Walk or Verb.Hand) when State.HasFlag(Endings.WalkedAway):
                await WalkAway();
                return true;
            case ("street", Verb.Walk or Verb.Hand) when State.HasFlag(Endings.KilledTony):
                await AfterTheKill();
                return true;
            case ("street", Verb.Walk or Verb.Hand) when State.HasFlag("shot_bartender") || State.HasFlag(Endings.WarnedTony):
                await AfterTheShot();
                return true;
            case ("street", Verb.Walk or Verb.Hand):
                await Say("Not without Tony telling me where she is. He knows. They always know.");
                return true;
            case ("street_lamp", Verb.Hand or Verb.Kick) when !Dark:
                await Say(verb == Verb.Kick ? "*CLANG*" : "I give the post a good shake. The bulb rattles in its cage...");
                State.SetFlag("alley3_dark");
                await Say("...and dies. Darkness. My oldest friend in this town.");
                return true;
            case ("street_lamp", Verb.Hand or Verb.Kick):
                await Say("It's dead. I'd like to keep it that way.");
                return true;

            case ("trash", Verb.Kick) when !Dark:
                await Say("Sal comes out to see who's making a racket, and finds me under that lamp, lit up like a Christmas tree. No.");
                return true;
            case ("trash", Verb.Kick) when !salOut:
                await LureSal();
                return true;
            case ("trash", Verb.Hand or Verb.Kick):
                await Say(salOut ? "I've made enough noise for one night." : "The cat hisses at me. Fair.");
                return true;

            case ("back_door", Verb.Hand or Verb.Talk) when State.HasFlag("shot_bartender"):
                await Say("Nobody's coming out that door now. Not after a shot. They'll be calling somebody instead.");
                return true;
            case ("back_door", Verb.Hand or Verb.Talk) when State.HasFlag(Endings.WarnedTony):
                await Say("Tony's right here. He's said all he's going to say, and he's said it to the wall.");
                return true;
            case ("back_door", Verb.Hand or Verb.Talk) when State.HasFlag(Endings.WalkedAway):
                await Say("I've lowered the gun. All that's left is to walk away.");
                return true;
            case ("back_door", Verb.Hand or Verb.Talk) when salDown:
                await KnockForTony();
                return true;
            case ("back_door", Verb.Hand or Verb.Talk) when salOut:
                await Say("Not with Sal out here, awake.");
                return true;
            case ("back_door", Verb.Hand or Verb.Talk):
                await Say("I knock, Sal opens, and I'm back on my knees in thirty seconds. I need him out here first. In the dark.");
                return true;
            case ("back_door", Verb.Kick):
                await Say("Steel. My foot would lose that argument.");
                return true;

            case ("sal", Verb.UseItem) when item == "revolver" && !salDown:
                await KnockOutSal();
                return true;
            case ("sal", Verb.Look) when salDown:
                await Say("Sal, out cold. He'll wake up with a headache and a story he'll never tell.");
                return true;
            case ("sal", Verb.Hand or Verb.Kick or Verb.Talk or Verb.UseItem) when salDown:
                await Say("He's out cold. Let him dream about his mother.");
                return true;
            case ("sal", Verb.Talk):
                await Say("And say what? \"Nice night\"? He'd fold me in half before I got to \"night\".");
                return true;
            case ("sal", Verb.Hand or Verb.Kick):
                await Say("With my bare hands? He'd fold me in half. I need something heavier than my fists.");
                return true;

            // a save from before the finish-or-leave choice moved into bartender_shot: Tony wounded, still undecided
            case ("bartender", Verb.UseItem) when item == "revolver" && State.HasFlag("shot_bartender")
                                                  && !State.HasFlag(Endings.KilledTony) && FindActor("bartender") is { } shot:
                State.SetFlag("finish_tony");
                await KillTony(shot);
                return true;
            case ("bartender", Verb.Look) when State.HasFlag(Endings.KilledTony):
                await Say("Tony, on his back in the rain, looking at nothing. He told me everything. Then I made sure he couldn't tell anyone else.");
                return true;
            case ("bartender", Verb.Look) when State.HasFlag("shot_bartender"):
                await Say("Tony, on his back by the door, a hand clamped on his shoulder. He's looking at me like he's memorising my face.");
                return true;
            case ("bartender", _) when State.HasFlag(Endings.KilledTony):
                await Say("There's nothing left to say to him. There never will be.");
                return true;
            case ("bartender", Verb.Talk) when State.HasFlag("shot_bartender"):
                await Talk("bartender_dismiss");
                return true;
            case ("bartender", Verb.Hand or Verb.Kick) when State.HasFlag("shot_bartender"):
                await Say("I've done enough to him for one night. Maybe.");
                return true;
            case ("bartender", Verb.Talk) when State.HasFlag(Endings.WarnedTony) || State.HasFlag(Endings.WalkedAway):
                await Talk("bartender_dismiss");
                return true;
            case ("bartender", Verb.Look) when State.HasFlag(Endings.WarnedTony) || State.HasFlag(Endings.WalkedAway):
                await Say("Tony, still by the door. Brick dust in his hair and no more answers in him.");
                return true;
            case ("bartender", Verb.Hand or Verb.Kick or Verb.UseItem) when State.HasFlag(Endings.WarnedTony) || State.HasFlag(Endings.WalkedAway):
                await Say("I've done enough. Time to leave him where he is.");
                return true;
        }
        return false;
    }

    /// <summary>The propped back door has one overlay under the lamp and one on it, so it reads whichever way the lamp
    /// flickers.</summary>
    private void ShowDoorOpen(bool open)
    {
        foreach (var door in new[] { "DoorOpen", "Lamp/DoorOpenLit" })
            if (GetNodeOrNull<Sprite2D>(door) is { } overlay) overlay.Visible = open;
    }

    private async Task OpenBackDoor()
    {
        Game.Sfx.Play(Sound.DoorOpen);
        ShowDoorOpen(true);
        await Wait(0.25);
    }

    private void CloseBackDoor()
    {
        Game.Sfx.Play(Sound.DoorClose);
        ShowDoorOpen(false);
    }

    /// <summary>One kick: from behind Micah, facing the screen, Sal drives his foot into Micah's belly, and Micah
    /// doubles up and sags back onto his forearms.</summary>
    private async Task<bool> Kick(Actor sal)
    {
        var swing = sal.PlayPose("sal_kick");
        await Wait(KickLands);
        Game.Sfx.Play(Sound.Thunk);
        bool hit = await Player.PlayPose("micah_kicked");
        bool kicked = await swing;
        Player.SetPose("micah_kneel");
        sal.SetPose(null);
        return hit && kicked;
    }

    /// <summary>A kick at the cans in the dark: Micah ducks behind the lamp post and Sal comes out to look.</summary>
    private async Task LureSal()
    {
        await Say("*CRASH*");
        await Say("The cat goes one way, the lid goes the other.");
        await Game.WalkTo(new Vector2(165, 205));
        Player.Face(Facing.Right);
        await Wait(0.8);
        if (FindActor("sal") is not { } sal) return;
        sal.Position = new Vector2(331, 198);
        await OpenBackDoor();
        State.SetFlag("alley3_sal_inside", false);
        State.SetFlag("alley3_sal_out");
        await sal.MoveTo(SalAtTrash, 40);
        CloseBackDoor();
        sal.FaceLeft(false);
        sal.WalkTo = BehindSal;
        await Say("sal", "Damn cats. And who turned off the light? Tony! The light's out again!");
        await Say("sal", "...Tony? Ah, forget it.");
        await Think("His back's to me. Big back. It would be a shame to waste it.");
    }

    private async Task KnockOutSal()
    {
        if (FindActor("sal") is not { } sal) return;
        Player.FaceTowards(sal.Position);
        await Say("Revolver by the barrel. The butt's the only part of it I ever hit anything with.");
        var swing = Player.PlayPose("micah_pistol_whip");
        while (!swing.IsCompleted && Player.Poses.Frame < 2) await Wait(0.01);
        if (swing.IsCompleted && !await swing) return;
        Game.Sfx.Play(Sound.Thunk);
        bool fell = await sal.PlayPose("sal_knockout");
        bool struck = await swing;
        Player.SetPose(null);
        if (!fell || !struck) return;
        sal.SetTexture(SalOut);
        State.SetFlag("alley3_sal_down");
        await Wait(0.6);
        await Say("Down like a sack of coal. Nighty night, Sal.");
        await Say("Now, how did he knock? Two, a pause, and one more.");
    }

    private async Task KnockForTony()
    {
        await Say("*Knock knock*... *knock*");
        await Game.WalkTo(MicahAims);
        Player.Face(Facing.Right);
        await Wait(1.0);
        if (FindActor("bartender") is not { } tony) return;
        tony.Position = new Vector2(331, 198);
        await OpenBackDoor();
        State.SetFlag("alley3_tony_inside", false);
        await tony.MoveTo(TonyOut, 40);
        CloseBackDoor();
        tony.FaceLeft(true);
        tony.WalkTo = MicahAims;
        await Player.PlayPose("micah_draw");
        Player.SetPose("micah_aim");
        Act3.UpdateGates();
        await Talk("bartender_gun");
        if (State.HasFlag(Endings.WalkedAway))
        {
            await Player.Holster();
            await Wait(0.6);
            await Think("I walk away. Down the alley, past the dead lamp, out into the street. Nobody follows.");
            await WalkAway();
            return;
        }
        if (State.HasFlag(Endings.WarnedTony))
        {
            await WarnTony();
            return;
        }
        await Say("*BANG*");
        // the bullet takes him in the shoulder: he folds straight down and goes over on his back
        await tony.PlayPose("bartender_fall");
        tony.SetTexture(BartenderShot);
        await Wait(0.8);
        await Talk("bartender_shot");
        await Player.Holster();
        tony.WalkTo = MicahAims;
        if (State.HasFlag("finish_tony"))
        {
            await KillTony(tony);
            return;
        }
        await AfterTheShot();
    }

    /// <summary>
    /// Act 3, the warning shot: into the bricks by Tony's ear. He talks, all but the alarm, and stays outside while
    /// Micah leaves. No blood, so no debt with the mob.
    /// </summary>
    private async Task WarnTony()
    {
        await Say("*BANG*");
        await Think("Brick dust in his hair. The bullet's in the wall, an inch from his ear. That's where I meant it to go.");
        await Talk("bartender_miss");
        await Player.Holster();
        await Think("The Gold Coast. The kitchen door. The delivery boys' key.");
        await Think("Nobody bleeding, for once. Tony'll pour drinks tomorrow and swear he never saw me. He'd rather that than explain.");
        await AfterTheShot();
    }

    /// <summary>
    /// Act 3, Tony on his back after the first shot, and Micah chose to finish him: a second bullet, so he can't tell the
    /// mob who shot him. The street then opens onto the Act 3 map, where the church and the mansion are both the last choice.
    /// </summary>
    private async Task KillTony(Actor tony)
    {
        // up close, standing past his head, the revolver pointed down at it
        await Game.WalkTo(OverTony);
        Player.Face(Facing.Left);
        await Player.PlayPose("micah_draw");
        await Player.PlayPose("micah_aim_down");
        Player.SetPose("micah_aim_down_held");
        await Talk("bartender_kill");
        // the wound shows with the shot, not after it
        tony.SetTexture(BartenderDead);
        await Say("*BANG*");
        await Wait(1.0);
        await Player.Holster("micah_holster_down");
        await Talk("bartender_dead");
    }

    /// <summary>Tony back where the story left him on a reload, standing or on his back by the door.</summary>
    private void PlaceTony()
    {
        bool shot = State.HasFlag("shot_bartender");
        if ((!shot && !State.HasFlag(Endings.WarnedTony) && !State.HasFlag(Endings.WalkedAway))
            || FindActor("bartender") is not { } tony) return;
        tony.Position = TonyOut;
        tony.FaceLeft(true);
        tony.WalkTo = MicahAims;
        if (shot) tony.SetTexture(State.HasFlag(Endings.KilledTony) ? BartenderDead : BartenderShot);
    }
}
