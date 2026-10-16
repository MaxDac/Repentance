using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, that same night. Micah gets dressed. Eleanor stays against the pillows under the white sheet.
/// They agree never to see each other again. End of the first act of the journal.
/// In the interludes the room is Eleanor's: in the First she watches the convent from the window until Micah comes;
/// in the Second, after he has gone, two of the Order's men knock at the door.
/// </summary>
public partial class MotelNight : Room
{
    private const string EmptyBed = "res://assets/art/rooms/motel_empty.png";

    private bool First => State.HasFlag("interlude1");
    private bool Second => State.HasFlag("interlude2");

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
                    await Think("A motel on the road below the convent. From the window I can see the gate, and anyone who rings at it.");
                    await Think("Agatha would say I'm waiting for a sign. I'm waiting for a man. It's usually the same thing.");
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
            await Think("A motel at the edge of town. A buzzing sign, a cracked basin, her stockings over the chair.");
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
                await Say("My coat, over the back of the chair. Ready to go, the way I like it.");
                return true;
            case ("door", Verb.Walk or Verb.Hand):
                await Say("Not yet. First I want to see who comes up that road.");
                return true;
        }
        return false;
    }

    private async Task<bool> SecondInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Walk or Verb.Hand) when !State.HasFlag("interlude_goons_in"):
                await Game.WalkTo(target.WalkTo);
                await Say("Micah? Did you forget your...");
                State.SetFlag("interlude_goons_in");
                await Talk("interlude_goons");
                await Story.Interlude.Taken();
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
