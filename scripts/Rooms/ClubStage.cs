using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Club's stage. Eleanor stands in the spotlight with three masked men around her, the members watching from the
/// seats. In Act 2 Micah only gets to see it before the journal stops; in Act 3 the leader recognises him.
/// </summary>
public partial class ClubStage : Room
{
    public override Track? Music => Track.ClubStrings;

    public override void _Ready()
    {
        base._Ready();
        Game.Settings.Changed += ApplyNuditySetting;
        ApplyNuditySetting();
    }

    public override void _ExitTree()
    {
        Game.Settings.Changed -= ApplyNuditySetting;
        base._ExitTree();
    }

    private void ApplyNuditySetting()
    {
        string sprite = Game.Settings.NudityEnabled ? "eleanor_stage" : "eleanor_stage_clothed";
        if (FindActor("eleanor") is { } eleanor)
            eleanor.SetTexture(GD.Load<Texture2D>($"res://assets/art/sprites/{sprite}.png"), 11);
    }

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
        await Think("The seats were full, and nobody was sitting. Everybody stood, facing the light.");
        Game.Hud.ShowCloseUp(CloseUps.Stage);
        await Game.WalkTo(new Vector2(212, 208));
        Player.Face(Facing.Up);
        await Wait(0.8);
        await Think(Game.Settings.NudityEnabled
            ? "And in the light, Eleanor. No mask. Not a stitch on her, and nothing in her face. Not fear, not shame. Nothing."
            : "And in the light, Eleanor. No mask, and nothing in her face. Not fear, not shame. Nothing.");
        await Think("Three of them around her, like pall-bearers: a stag, a boar and a wolf.");
        await Think("She looked like a doll somebody had wound up and set down. Whoever lived behind those eyes had gone out and left the lights on.");
        await Wait(1.0);
        await LightsOut();
    }

    /// <summary>Act 2's last page: the fade, and Daniel in the dark attic. The lounge archway runs it too.</summary>
    private async Task LightsOut()
    {
        await Game.Hud.Fade(1, 2.0);
        Game.Hud.HideCloseUp(0);
        await Wait(1.0);
        await Game.ChangeRoom("attic", "night2");
    }

    /// <summary>
    /// Act 3: the leader turns to Micah, then takes off the stag's face in front of everyone. He is Harrington senior,
    /// and the whole Club is a show of his power. Whatever Micah does, Bruno knocks him out from behind.
    /// </summary>
    private async Task Caught()
    {
        Game.Hud.ShowCloseUp(CloseUps.Stage);
        await Wait(1.0);
        await Say("leader", "Are you satisfied, now, mister Jones?");
        await Wait(0.4);
        // the whole room turns to look at him
        foreach (var child in World.GetChildren())
            if (child is Actor a && a.Id != "brute" && a.Visible)
                a.FaceLeft(a.Position.X > Player.Position.X);
        await Wait(1.6);
        await Think("Every mask in the room turns my way. White porcelain and carved bone, antlers, tusks and beaks, and all of them smiling.");
        Game.Hud.HideCloseUp();
        await Wait(0.8);
        await Unmask();
        await Talk("harrington_unmask");
        await Talk("club_caught");
        await KnockedOut();
    }

    /// <summary>
    /// Bruno puts Micah down from behind and dumps him on the cathedral steps. The lounge archway runs it too, so
    /// there is no walking out of the Club past him.
    /// </summary>
    private async Task KnockedOut()
    {
        Game.Hud.HideCloseUp();
        State.SetFlag("brute_stage");
        var brute = FindActor("brute") ?? throw new System.InvalidOperationException("The Club knockout requires Bruno.");
        await brute.MoveTo(new Vector2(Player.Position.X - 24, Player.Position.Y + 4), 70);
        brute.FaceLeft(false);
        await Say("brute", "Night night, pal.");
        Player.Face(Facing.Right);
        var strike = brute.PlayPose("brute_strike");
        while (!strike.IsCompleted && brute.Poses?.Frame < 2) await Wait(0.01);
        if (strike.IsCompleted && !await strike) return;
        Game.Sfx.Play(Sound.Thunk);
        bool collapsed = await Player.PlayPose("micah_masked_collapse");
        bool struck = await strike;
        brute.SetPose(null);
        if (!collapsed || !struck) return;
        await Wait(0.35);
        await Game.Hud.Fade(1, 0.08);
        await Wait(1.6);
        State.SetFlag("masked", false);
        State.SetFlag("beaten");
        await Game.ChangeRoom("church_exterior", "beaten");
    }

    /// <summary>The stag lowers his cowl and lifts the mask away: from here on the leader speaks as HARRINGTON.</summary>
    private async Task Unmask()
    {
        if (FindActor("leader") is not { } leader) return;
        await Think("All but one. The stag puts a hand to his jaw, lifts the face away, and pushes the cowl back off his head.");
        await leader.PlayPose("leader_unmask");
        leader.SetTexture(GD.Load<Texture2D>("res://assets/art/sprites/leader_unmasked.png"), leader.Frames);
        leader.Id = "harrington";
        leader.DisplayName = "Mr. Harrington";
        leader.LookText = "Harrington senior. Bald as an egg, white at the temples, the stag's face held against his chest like a hat at a funeral.";
        await Wait(1.2);
        await Think("I know the face. I've seen it in oils, over a desk on LaSalle Street. The old man himself.");
        await Think("Nobody else in the room even blinks. They've always known. That's the point.");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("eleanor", Verb.Talk):
                await Say("Not from down here. Not with them around her.");
                return true;
            case ("leader" or "harrington" or "ritual1" or "ritual2" or "audience", Verb.Talk):
                await Say("Silence. The only sound in the room is the spotlight humming.");
                return true;
            case ("lounge_exit", Verb.Walk or Verb.Hand) when State.StoryAct >= 3:
                await KnockedOut();
                return true;
            case ("lounge_exit", Verb.Walk or Verb.Hand):
                await LightsOut();
                return true;
        }
        return false;
    }
}
