using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The back of the Harrington mansion, on the Gold Coast. Tony's trick (the key on the lintel, walk in like the delivery
/// boys) would ring an alarm bell wired to the kitchen door: Micah spots the wire, shoves the coal bin under the bell,
/// gags it with his tie, and only then lets himself in. On the way out the house may go up behind him. Shot, Tony told
/// him about the bell; after the warning shot he left it out, and opening the door unseen rings it (endings 13 and 14).
/// </summary>
public partial class MansionExterior : Room
{
    public override Track? Music => Track.MansionDread;

    private bool Noticed => State.HasFlag("alarm_noticed");
    private bool Moved => State.HasFlag("bin_moved");
    private bool Wedged => State.HasFlag("bell_wedged");
    /// <summary>Tony only ever had a warning shot, so he never mentioned the bell.</summary>
    private bool Warned => State.HasFlag(Endings.WarnedTony);

    /// <summary>Eleanor waits out here on the escape only if she came: convinced, or worn out after the shot.</summary>
    protected override void OnRefresh()
    {
        if (FindActor("eleanor") is { } eleanor && !Endings.EleanorFollows(State.HasFlag)) eleanor.Visible = false;
    }

    public override async Task OnEnter(string entry)
    {
        if (entry == "eleanor_coda")
        {
            await Game.Run(EleanorLeaves);
            return;
        }
        if (entry == "escape")
        {
            await Game.Run(Escape);
            return;
        }
        if (State.HasFlag("seen_mansion")) return;
        State.SetFlag("seen_mansion");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("Gold Coast, past midnight. Wind off the lake, and hedges clipped as neat as a banker's moustache.");
            await Think("The Harrington place. From the front it's a bank. From the back, it's still a bank, with a kitchen.");
            await Think(Warned
                ? "Tony's directions: the kitchen door, the lintel, the key. Walk in like the delivery boys. Easy."
                : "Tony's directions: the kitchen door, the lintel, the key. And a bell on the door, he says. Walk in like the delivery boys. Sure.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door" or "lintel", Verb.Look) when !Noticed && !Warned:
            case ("wire" or "bell", Verb.Look or Verb.Hand or Verb.UseItem) when !Noticed:
                await NoticeAlarm();
                return true;

            case ("lintel", Verb.Hand) when !State.HasFlag("took_kitchen_key"):
                if (!Noticed && !Warned)
                {
                    await Say("I reach up for the key, and my eye goes along the door frame...");
                    await NoticeAlarm();
                }
                State.SetFlag("took_kitchen_key");
                State.GiveItem("kitchen_key");
                await Say("An iron key on the lintel, right where Tony said. Under a nice coat of dust.");
                return true;
            case ("lintel", Verb.Hand):
                await Say("Nothing else up there but dust and pigeon business.");
                return true;

            case ("door", Verb.Hand or Verb.UseItem) when item is null or "kitchen_key":
                await TryDoor();
                return true;
            case ("door", Verb.Kick):
                await Say("And wake the whole Gold Coast? Very subtle, Micah.");
                return true;

            case ("wire", Verb.Hand):
                await Say("Cut it and the bell's spring lets go: it rings anyway. Somebody thought about this.");
                return true;

            case ("bell", Verb.Hand or Verb.UseItem) when Wedged:
                await Say("My tie holds the hammer off the gong. Best use that tie ever had.");
                return true;
            case ("bell", Verb.Hand or Verb.UseItem) when !Moved:
                await Say("If I could reach the hammer, I could stop it. But it's a good two feet out of reach.");
                return true;
            case ("bell", Verb.Hand or Verb.UseItem):
                await WedgeBell();
                return true;

            case ("bin", Verb.Hand or Verb.Kick) when !Noticed:
                await Say("A coal bin. Heavy, and none of my business.");
                return true;
            case ("bin", Verb.Hand or Verb.Kick):
                await Say("Heavy as sin. I put my shoulder into it...");
                await Say("*SCRAAAPE*");
                State.SetFlag("bin_moved");
                await Say("...right under the bell. A step up in the world.");
                return true;
            case ("bin_moved", Verb.Hand or Verb.Kick):
                await Say("It's right where I want it.");
                return true;

            case ("coal_hole", Verb.Hand):
                await Say("The coal hatch. I'd fit, if I were nine years old and stupid. I'm only one of those.");
                return true;

            case ("gate", Verb.Hand or Verb.Walk) when State.HasFlag("eleanor_coda"):
                await DownTheRoad();
                return true;
            case ("gate", Verb.Hand or Verb.Walk) when State.HasFlag("escaping"):
                await Getaway();
                return true;
            case ("gate", Verb.Hand or Verb.Walk):
                await Say("Not without Eleanor. Not after all this.");
                return true;
        }
        return false;
    }

    private async Task NoticeAlarm()
    {
        State.SetFlag("alarm_noticed");
        await Say("Wait. A wire, along the door frame, up the wall... to that red box. A bell.");
        await Say(Warned
            ? "Open the door and the bell rings the house awake. \"Walk in like the delivery boys.\" Thanks, Tony. You left that part out."
            : "There it is, Tony's bell. Open the door cold and it rings the house awake. \"Walk in like the delivery boys.\"");
        await Say("The delivery boys come by day. With the cook expecting them.");
    }

    private async Task TryDoor()
    {
        if (!State.HasItem("kitchen_key"))
        {
            await Say(Noticed ? "Locked. And wired." : "Locked. The key's supposed to be on the lintel.");
            return;
        }
        if (!Noticed && Warned)
        {
            await RingAlarm();
            return;
        }
        if (!Noticed)
        {
            await Say("Key in the lock, and...");
            await NoticeAlarm();
            return;
        }
        if (!Wedged)
        {
            await Say("Not while that bell's listening.");
            return;
        }
        await Say("Key in, a quarter turn, and the wire goes taut... The hammer strains against my tie. Not a sound.");
        State.TakeItem("kitchen_key");
        State.SetFlag("door_open");
        await Wait(0.4);
        await Game.ChangeRoom("mansion_kitchen", "start");
    }

    /// <summary>
    /// The warning-shot route, the alarm unseen: the door rings the bell, feet come down the back stairs, and Micah
    /// runs (ending 13) or goes in to them (ending 14, <see cref="MansionKitchen"/>).
    /// </summary>
    private async Task RingAlarm()
    {
        await Say("Key in, a quarter turn, and...");
        Game.Sfx.Play(Sound.AlarmBell);
        await Think("A bell. Right over my head, loud enough to wake the whole Gold Coast. A wire along the door frame, up to a red box.");
        State.SetFlag("alarm_noticed");
        await Wait(0.8);
        for (int i = 0; i < 6; i++)
        {
            Game.Sfx.Step(FloorSurface.Wood, 0.7f);
            await Wait(0.32);
        }
        await Talk("alarm_footsteps");
        if (State.HasFlag(Endings.AlarmRan))
        {
            await Game.WalkTo(new Vector2(30, 236));
            await Act3.End();
            return;
        }
        State.TakeItem("kitchen_key");
        State.SetFlag("door_open");
        await Game.ChangeRoom("mansion_kitchen", "ambush");
    }

    private async Task WedgeBell()
    {
        if (!await Game.Hud.Puzzle.Open(PuzzleKind.Bell)) return;
        State.SetFlag("bell_wedged");
        Player.SetCharacter(ResolvePlayerCharacter());
        await Say("Hold the hammer back, tie it clear of the gong, then let go. The wire stays intact.");
        await Think("My tie. Rose gave it to me, a lifetime ago. Now it's all that keeps this house asleep.");
        await Say("Let it ring now. Nobody will hear a thing.");
    }

    /// <summary>
    /// The coda's last beat: Eleanor out of the kitchen door in the sheet, alone, and off down the road. Micah's journal
    /// takes the night back at Rose's door, where <see cref="RoseHouse"/> resolves ending 8 or 9 (straight to Eleanor's
    /// last scene on the kill route).
    /// </summary>
    private async Task EleanorLeaves()
    {
        await Game.WalkTo(new Vector2(150, 238));
        Player.Face(Facing.Right);
        await Wait(0.6);
        if (State.HasFlag(Endings.EleanorBurned))
        {
            Player.Face(Facing.Up);
            await Wait(0.8);
            State.SetFlag(EleanorBlaze);
            await Say("*CRASH*");
            await Wait(1.0);
            Player.Face(Facing.Right);
        }
        await Talk("coda_outside");
        await DownTheRoad();
    }

    /// <summary>Eleanor's fire reaches the house once she is out of it (ending 8 never sets <see cref="Endings.MansionExploded"/>).</summary>
    public const string EleanorBlaze = "eleanor_blaze";

    /// <summary>Eleanor off down the road, and the night back at Rose's door, or straight on after a killing. The gate runs it too, in case the coda stopped short.</summary>
    private async Task DownTheRoad()
    {
        await Game.WalkTo(new Vector2(30, 236));
        await Game.Hud.Fade(1, 1.5);
        Story.Interlude.EndCoda();
        // Micah killed Tony and promised Caleb the station steps: no coffee at Rose's door that morning.
        if (State.HasFlag(Endings.KilledTony)) await Act3.EleanorAfterRose();
        else await Game.ChangeRoom("rose_house", "coffee");
    }

    /// <summary>Back out through the kitchen door, with or without Eleanor, and maybe with the house burning behind.</summary>
    private async Task Escape()
    {
        var eleanor = FindActor("eleanor");
        _ = Game.WalkTo(new Vector2(150, 238));
        if (eleanor != null && eleanor.Visible) await eleanor.MoveTo(new Vector2(190, 236), 46);
        await Wait(1.6);
        Player.Face(Facing.Right);
        eleanor?.FaceLeft(false);
        if (State.HasFlag("cellar_fire"))
        {
            await Wait(1.0);
            State.SetFlag(Endings.MansionExploded);
            await Say("*CRASH*");
            await Think("The cellar goes first. Then the kitchen, then the study, and everything Harrington ever wrote down in it.");
            if (eleanor != null && eleanor.Visible)
            {
                if (State.HasFlag(Endings.EleanorWeary))
                    await Think("She watches the windows go. She doesn't make a sound.");
                else
                    await Say("eleanor", "Oh my God. Oh my God, Micah.");
                await Say("Time to go. Before the whole Gold Coast comes out in its pajamas.");
            }
            else await Think("Time to go. Before the whole Gold Coast comes out in its pajamas.");
        }
        else
        {
            await Think("The house sleeps on, with the old man on the carpet. Somebody will find him by breakfast.");
        }
        await Getaway();
    }

    /// <summary>Out through the gate, and the end of the night. The gate runs it too, in case the escape stopped short.</summary>
    private async Task Getaway()
    {
        if (State.HasFlag("cellar_fire")) State.SetFlag(Endings.MansionExploded);
        await Game.WalkTo(new Vector2(30, 236));
        await Act3.End();
    }
}
