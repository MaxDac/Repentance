using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, that same night. Micah gets dressed. Eleanor stays against the pillows under the white sheet.
/// They agree never to see each other again. End of the first act of the journal.
/// In the interludes the room is Eleanor's: in the First she watches the convent from the window until Micah comes;
/// in the Second, after he has gone, two of the Order's men knock at the door, kick it in and walk her out.
/// </summary>
public partial class MotelNight : Room
{
    private const string EmptyBed = "res://assets/art/rooms/motel_empty.png";

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
        if (State.HasFlag("motel_night_done")) return;
        await Game.Run(async () =>
        {
            await Wait(1.0);
            await Think("Her room, up the fire escape. A buzzing sign, a cracked basin, her stockings over the chair.");
            await Think("I'm buttoning my shirt in the dark like a thief. Rose's face keeps turning up behind my eyes.");
            await Talk("motel_night");
            State.SetFlag("motel_night_done");
            await Think("I close the door on her softly. Rose, the boy, and now Eleanor. I'm getting good at doors.");
            await Wait(0.6);
            await Game.Hud.Fade(1, 1.5);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (First) return await FirstInteract(verb, target);
        if (Second) return await SecondInteract(verb, target);
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
    private static readonly Vector2 Doorway = new(28, 170);

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
        var bruteIn = brute.MoveTo(bruteSpot, 38);
        await Wait(0.9);
        await Task.WhenAll(bruteIn, goon.MoveTo(goonSpot, 38));
        brute.FaceLeft(false);
        goon.FaceLeft(false);
        Player.Face(Facing.Left);
        await Wait(0.4);
    }

    /// <summary>Bruno leads the way out, Eleanor follows him through the door, and the goon falls in behind her.</summary>
    private async Task TheyTakeHer()
    {
        if (FindActor("brute") is not { } brute || FindActor("goon") is not { } goon) return;
        var bruteOut = brute.MoveTo(Doorway, 40);
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
            case ("door", Verb.Look) when State.HasFlag("interlude_door_kicked"):
                await Say("Kicked in. The lock's hanging out of the jamb like a tooth.");
                return true;
            case ("door", Verb.Look):
                await Say("Somebody's knocking. Micah would have used his key. He'd have left it on the dresser, anyway.");
                return true;
            case ("bed", Verb.Look or Verb.Hand):
                await Say("Still warm on his side. I won't think about that.");
                return true;
            case ("chair", Verb.Look or Verb.Hand):
                await Say("His chair's empty. He took his coat and his hat, and he didn't look back.");
                return true;
            case ("window", Verb.Look or Verb.Hand):
                await Say("His car's gone from the lot. Another one's pulled in, lights off.");
                return true;
        }
        return false;
    }
}
