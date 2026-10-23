using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, the night Micah found Eleanor on the fire escape. Micah gets dressed. Eleanor stays against the
/// pillows under the white sheet. They agree never to see each other again. It plays after the First Interlude and
/// the rest of their talk on the fire escape (<see cref="MotelFireEscape"/>), then, days later, Micah's journal goes on
/// at his office.
/// In the interludes the room is Eleanor's: in the First she watches the convent from the window until Micah comes;
/// in the Second, after he has gone, two of the Order's men knock at the door, kick it in and walk her out.
/// </summary>
public partial class MotelNight : Room
{
    private const string EmptyBed = "res://assets/art/rooms/motel_empty.png";
    /// <summary>The black card between the motel night and the office: Micah's journal skips the days in between.</summary>
    public const string DaysLater = "Days later";
    /// <summary>Seconds for <see cref="DaysLater"/> to fade in on the black screen, and out again.</summary>
    public const double DaysLaterFade = 3.0;

    private bool First => State.HasFlag("interlude1");
    private bool Second => State.HasFlag("interlude2");

    /// <summary>The office jazz plays while Micah is here with Eleanor; in the interludes she is alone, in silence.</summary>
    public override Track? Music => First || Second ? null : Track.OfficeJazz;

    private Texture2D? _occupied;

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is { } bg)
        {
            _occupied ??= bg.Texture;
            bg.Texture = First || Second ? GD.Load<Texture2D>(EmptyBed) : _occupied;
        }
        if (FindHotspot("bed") is { } bed) bed.DisplayName = First || Second ? "bed" : "Eleanor";
    }

    public override async Task OnEnter(string entry)
    {
        if (First)
        {
            if (entry == "interlude1")
                await Game.Run(async () =>
                {
                    await Think("Her room in the flophouse down the hill from the convent. From the window she could see the gate, and anyone who rang at it.");
                    await Think("Agatha would have said she was waiting for a sign. She was waiting for a man. It was usually the same thing.");
                });
            return;
        }
        if (Second)
        {
            if (entry == "interlude2")
                await Game.Run(async () =>
                {
                    await Talk("interlude_motel");
                    await Wait(0.6);
                    await Think("A knock at the door. Two knocks, heavy. Not Micah's.");
                });
            return;
        }
        if (entry != "start") return;
        await Game.Run(async () =>
        {
            await Wait(1.0);
            await Think("Her room, up the fire escape. A buzzing sign, a cracked basin, her stockings over the chair.");
            await Think("I'm buttoning my shirt in the dark like a thief. Rose's face keeps turning up behind my eyes.");
            await Talk("motel_night");
            await OutTheDoor();
        });
    }

    /// <summary>Micah closes her door behind him; "Days later", his office. The door runs it too, in case the scene stopped short.</summary>
    private async Task OutTheDoor()
    {
        await Think("I close the door on her softly. Rose, the boy, and now Eleanor. I'm getting good at doors.");
        await Wait(0.6);
        await Game.Hud.Fade(1, MotelFireEscape.NightFade);
        await Game.Hud.FadeCaptionIn(DaysLater, DaysLaterFade);
        await Wait(MotelFireEscape.NightCaption);
        await Game.Hud.FadeCaptionOut(DaysLaterFade);
        await Game.ChangeRoom("office", "act2", fadeInSeconds: MotelFireEscape.NightFade);
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (First) return await FirstInteract(verb, target);
        if (Second) return await SecondInteract(verb, target);
        if (target.Id == "door" && verb is Verb.Walk or Verb.Hand)
        {
            await OutTheDoor();
            return true;
        }
        return false;
    }

    private async Task<bool> FirstInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("window", Verb.Look or Verb.Hand or Verb.Walk):
                await Game.WalkTo(target.WalkTo);
                Player.Face(Facing.Up);
                await Talk("interlude_motel_window");
                await Story.Interlude.EndFirst();
                return true;
            case ("bed", Verb.Look):
                await Say("I haven't slept in it. I haven't dared take my shoes off.");
                return true;
            case ("bed", Verb.Hand):
                await Say("If I lie down, I'll miss him. If he comes at all.");
                return true;
            case ("chair", Verb.Look or Verb.Hand):
                await Say("An empty chair. I'd sit, but from there I can't see the road.");
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await Say("Not yet. First I want to see who comes up that road.");
                return true;
        }
        return false;
    }

    /// <summary>Where the Order's men stand in the doorway: on the walkway outside, framed by the kicked-in door.</summary>
    public static readonly Vector2 Doorway = new(26, 170);

    /// <summary>
    /// The floor just inside the door, in front of the bed's foot post. The Order's men step down here from the
    /// doorway before crossing the room, so they never walk through the foot of the bed behind its post.
    /// </summary>
    public static readonly Vector2 DoorStep = new(26, 196);

    /// <summary>Y-sort baseline of the bed's foot posts (<c>World/BedRails</c>): anyone above it draws behind them.</summary>
    public const float BedRailsBaseline = 185;

    /// <summary>The bed's left foot post and its finial, in room pixels.</summary>
    public const float FootPostLeft = 40, FootPostRight = 52;

    private static async Task MoveVia(Actor actor, float speed, params Vector2[] points)
    {
        foreach (var point in points) await actor.MoveTo(point, speed);
    }

    /// <summary>
    /// Eleanor goes to the door but stops halfway, calling out; the second knock is a shoulder, the third a boot.
    /// Bruno comes in first and the goon a step behind; they stop between her and the door.
    /// </summary>
    private async Task TheDoorGoesIn()
    {
        await Game.WalkTo(new Vector2(150, 206));
        Player.Face(Facing.Left);
        await Say("Micah? Did you forget your...");
        await Wait(0.5);
        Game.Sfx.Play(Sound.Thunk);
        await Wait(0.7);
        await Say("...Micah?");
        await Wait(0.3);
        if (FindActor("brute") is not { } brute || FindActor("goon") is not { } goon) return;
        Vector2 bruteSpot = brute.Position, goonSpot = goon.Position;
        brute.Position = Doorway;
        goon.Position = Doorway + new Vector2(-4, -2);
        brute.FaceLeft(false);
        goon.FaceLeft(false);
        Game.Sfx.Play(Sound.Crash);
        Game.Sfx.Play(Sound.DoorSlam);
        State.SetFlag("interlude_door_kicked");
        State.SetFlag("interlude_goons_in");
        await Wait(0.8);
        var bruteIn = MoveVia(brute, 38, DoorStep, bruteSpot);
        await Wait(0.9);
        await Task.WhenAll(bruteIn, MoveVia(goon, 38, DoorStep + new Vector2(-4, -2), goonSpot));
        brute.FaceLeft(false);
        goon.FaceLeft(false);
        Player.Face(Facing.Left);
        await Wait(0.4);
    }

    /// <summary>Bruno leads the way out, Eleanor follows him through the door, and the goon falls in behind her.</summary>
    private async Task TheyTakeHer()
    {
        if (FindActor("brute") is not { } brute || FindActor("goon") is not { } goon) return;
        var bruteOut = MoveVia(brute, 40, DoorStep, Doorway);
        await Wait(0.6);
        var eleanorOut = Game.WalkTo(new Vector2(30, 190));
        await Wait(0.8);
        await Task.WhenAll(bruteOut, eleanorOut, goon.MoveTo(new Vector2(70, 210), 40));
        await Wait(0.3);
    }

    private async Task<bool> SecondInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Walk or Verb.Hand) when !State.HasFlag("interlude_goons_in"):
                await TheDoorGoesIn();
                await Talk("interlude_goons");
                await TheyTakeHer();
                await Story.Interlude.Taken();
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await TheyTakeHer();
                await Story.Interlude.Taken();
                return true;
            case ("door", Verb.Look) when State.HasFlag("interlude_door_kicked"):
                await Say("Kicked in. The lock's hanging out of the jamb like a tooth.");
                return true;
            case ("door", Verb.Look):
                await Say("Somebody's knocking. Micah would have used his key. He'd have left it on the dresser, anyway.");
                return true;
            case ("bed", Verb.Look or Verb.Hand):
                await Say("Cold on his side now. I won't think about that.");
                return true;
            case ("chair", Verb.Look or Verb.Hand):
                await Say("His chair's empty. He took his coat and his hat, and he didn't look back.");
                return true;
            case ("window", Verb.Look or Verb.Hand):
                await Say("He's gone from the alley. A car's pulled in below, lights off.");
                return true;
        }
        return false;
    }
}
