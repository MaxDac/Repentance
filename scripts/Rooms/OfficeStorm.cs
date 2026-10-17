using System.Threading.Tasks;
using Godot;

namespace Repentance.Rooms;

/// <summary>
/// Act 3, after Tony: Micah's office in a thunderstorm, the power out on the whole block. Hatless, the bottle in his
/// hand, he stands at the window while the journal confesses his descent; at its climax two flashes show a demon in
/// the window's reflection, swallowing him. Then the player has him put his hat on (the bottle stays on the desk) and
/// walk out through the door, to the Harrington mansion. Only the narrating voice speaks here.
/// </summary>
public partial class OfficeStorm : Room
{
    public override Track? Music => null;

    private Lightning _lightning = null!;

    /// <summary>How many flashes have shown the demon in the window (two, once the confession is over).</summary>
    public int DemonFlashes { get; private set; }

    public override void _Ready()
    {
        // the door is shut whenever he comes back in
        State.SetFlag("storm_door_ajar", false);
        State.SetFlag("storm_door_open", false);
        base._Ready();
        _lightning = GetNode<Lightning>("Lightning");
    }

    /// <summary>Hatless with the bottle until the hat goes back on.</summary>
    public override string ResolvePlayerCharacter() =>
        State.HasFlag("storm_hat_on") ? base.ResolvePlayerCharacter() : "micah_hatless_bottle";

    public override async Task OnEnter(string entry)
    {
        Player.Face(Facing.Up);
        if (State.HasFlag("storm_confessed")) return;
        await Game.Run(Confession);
    }

    private async Task Drink()
    {
        await Player.PlayPose("micah_hatless_bottle_drink");
        Player.SetPose(null);
    }

    private async Task Confession()
    {
        await Wait(1.2);
        await Think("The power's out on the whole block. The HOTEL sign is dead for the first time in six years. Only the sky lights the room now.");
        await Think("Hat on the desk. Bottle in my hand. I don't remember taking either off. I remember the shot.");
        await Drink();
        await Think("It starts small. A drink you don't need. A lie you didn't have to tell. A woman who isn't your wife.");
        await Think("Every step is a little lower than the last, and every one makes the next one easier. You don't fall. You walk down.");
        await Think("I know how this ends. I've arrested the men it ended for. I've read about them in the Tribune, the next morning.");
        await Drink();
        await Think("And knowing doesn't stop a thing. Knowing just means you get to watch.");

        // the climax: the sky holds its breath, then shows him what's wearing him
        await _lightning.Hush();
        await Think("Sin is a beast. It doesn't wait outside the door.");
        await Think("It climbs inside a man and wears him, until you can't tell where one stops and the other starts.");
        await Think("And it walks him down the road, all the way to the bottom.");
        await Wait(0.7);
        await Reflection();
        await Wait(2.2);

        await Think("Too late to turn round now. Eleanor's in that house. Whatever I am by morning, I'm going.");
        State.SetFlag("storm_confessed");
        _lightning.Ambient = true;
    }

    /// <summary>
    /// Light, dark, light: the first flash shows a demon at his reflection's shoulder, the second shows it
    /// swallowing him. Micah himself never moves.
    /// </summary>
    private async Task Reflection()
    {
        var first = GetNode<CanvasItem>("Lightning/Demon1");
        var second = GetNode<CanvasItem>("Lightning/Demon2");
        await _lightning.Strike(() =>
        {
            first.Visible = true;
            DemonFlashes++;
        }, () =>
        {
            first.Visible = false;
            second.Visible = true;
            DemonFlashes++;
        });
        second.Visible = false;
    }

    /// <summary>He sets the bottle down on the desk and puts his hat on.</summary>
    private async Task HatOn()
    {
        Player.Face(Facing.Up);
        var setDown = Player.PlayPose("micah_hatless_bottle_set");
        // the bottle leaves his hand on the third frame of the strip
        await Wait(0.81);
        State.SetFlag("storm_bottle_down");
        await setDown;
        State.SetFlag("storm_hat_on");
        await Player.PlayPose("micah_hatless_hat_on");
        Player.SetCharacter(ResolvePlayerCharacter());
        Player.SetPose(null);
        Player.Face(Facing.Up);
        await Think("The hat goes on. The bottle stays. One of us has to wait for me here.");
    }

    private async Task OpenTheDoor()
    {
        State.SetFlag("storm_door_ajar");
        await Wait(0.12);
        Player.Face(Facing.Right);
        await Player.PlayPose("micah_open_door");
        State.SetFlag("storm_door_ajar", false);
        State.SetFlag("storm_door_open");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Walk or Verb.Hand) when State.HasFlag("storm_hat_on"):
                await OpenTheDoor();
                await Game.ChangeRoom("mansion_exterior", "start");
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await Think("Not bareheaded, and not with a bottle in my fist. The hat's on the desk, by the cup.");
                return true;
            case ("hat", Verb.Hand):
                await HatOn();
                return true;
            case (_, Verb.Walk):
                return true;
            case (_, Verb.Look):
                await Think(target.LookText);
                return true;
            case ("bottle", Verb.Hand):
                await Think("Leave it. I've had enough to get me there, and not enough to stop me.");
                return true;
            case ("cup", Verb.Hand):
                await Think("The cup can stay empty. The bottle's doing the work tonight.");
                return true;
            case ("window", Verb.Hand):
                await Think("The glass is cold. Out there the rain's washing the street, and none of it's coming in here.");
                return true;
            case ("lamp", Verb.Hand):
                await Think("I pull the chain. Nothing. The whole block's dark, and I'm part of it.");
                return true;
            case (_, Verb.Talk):
                await Think("Nobody here to talk to. Just me, and this voice writing it all down.");
                return true;
            case (_, Verb.Kick):
                await Think("Kicking the furniture won't make the walk down any shorter.");
                return true;
            case (_, Verb.UseItem):
                await Think("Not now. Whatever I'm carrying, it's for the mansion.");
                return true;
            default:
                await Think(Game.Pick("Leave it.", "It's fine where it is.", "Not tonight."));
                return true;
        }
    }
}
