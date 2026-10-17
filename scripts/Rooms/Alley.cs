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
    private static readonly Texture2D SalOut = GD.Load<Texture2D>("res://assets/art/sprites/sal_out.png");
    private static readonly Texture2D BartenderShot = GD.Load<Texture2D>("res://assets/art/sprites/bartender_shot.png");

    /// <summary>The far end of the passage on the left, where the alley opens onto the street.</summary>
    private static readonly Vector2 StreetMouth = new(50, 192);

    private static readonly Vector2 SalAtTrash = new(398, 224);
    private static readonly Vector2 BehindSal = new(352, 222);
    private static readonly Vector2 TonyOut = new(318, 208);
    private static readonly Vector2 MicahAims = new(258, 214);

    private Sprite2D? _lamp;
    private double _flickerIn;
    private readonly RandomNumberGenerator _rng = new();

    private bool InAct3 => State.HasFlag("alley3");
    private bool Dark => State.HasFlag("alley3_dark");

    public override void _Ready()
    {
        base._Ready();
        _lamp = GetNodeOrNull<Sprite2D>("Lamp");
        if (!InAct3) return;
        // a reload mid-puzzle puts Sal back where the story left him
        if (FindActor("sal") is { } sal && State.HasFlag("alley3_sal_out"))
        {
            sal.Position = SalAtTrash;
            sal.FaceLeft(false);
            sal.WalkTo = BehindSal;
            if (State.HasFlag("alley3_sal_down")) sal.SetTexture(SalOut);
        }
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

    public override async Task OnEnter(string entry)
    {
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
            await Wait(1.2);
            await Think("Gravel in my palms, copper in my mouth. Sal's fists did the talking. Now Tony wants his turn.");
            await Talk("alley");
            // back inside through the club's back door
            if (FindActor("sal") is { } sal) _ = sal.MoveTo(new Vector2(322, 198), 50);
            if (FindActor("bartender") is { } tony) await tony.MoveTo(new Vector2(338, 196), 45);
            await Wait(0.4);
            if (!await Player.PlayPose("micah_kneel_rise")) return;
            Player.SetPose(null);
            Player.Face(Facing.Right);
            await Think("A convent. Of all the places to hide a woman like that.");
            State.SetFlag("alley_done");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (!InAct3)
        {
            if (target.Id == "street" && (verb is Verb.Walk or Verb.Hand) && State.HasFlag("alley_done"))
            {
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
        }
        return false;
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
        State.SetFlag("alley3_sal_inside", false);
        State.SetFlag("alley3_sal_out");
        await sal.MoveTo(SalAtTrash, 40);
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
        await Say("*THUNK*");
        // hit from behind: down on his knees, then flat on his face
        await sal.PlayPose("sal_knockout");
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
        State.SetFlag("alley3_tony_inside", false);
        await tony.MoveTo(TonyOut, 40);
        tony.FaceLeft(true);
        await Player.PlayPose("micah_draw");
        Player.SetPose("micah_aim");
        Act3.UpdateGates();
        await Talk("bartender_gun");
        if (State.HasFlag(Endings.WalkedAway))
        {
            Player.SetPose(null);
            await Wait(0.6);
            await Think("I walk away. Down the alley, past the dead lamp, out into the street. Nobody follows.");
            await Game.WalkTo(StreetMouth);
            await Act3.End();
            return;
        }
        await Say("*BANG*");
        // the bullet takes him in the shoulder: he folds straight down and goes over on his back
        await tony.PlayPose("bartender_fall");
        tony.SetTexture(BartenderShot);
        await Wait(0.8);
        await Talk("bartender_shot");
        Player.SetPose(null);
        await Think("The Gold Coast. The kitchen door. The delivery boys' key.");
        await Think("I shot a man tonight. My hand doesn't shake. That's what scares me.");
        await Game.WalkTo(StreetMouth);
        // first the office, in the storm, alone with the bottle; then the Gold Coast
        await Game.ChangeRoom("office_storm", "window");
    }
}
