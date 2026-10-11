using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The back of the Harrington mansion, on the Gold Coast. Tony's trick (the key on the lintel, walk in like the delivery
/// boys) would ring an alarm bell wired to the kitchen door: Micah spots the wire, shoves the coal bin under the bell,
/// gags it with his tie, and only then lets himself in. On the way out the house may go up behind him.
/// </summary>
public partial class MansionExterior : Room
{
    private bool Noticed => State.HasFlag("alarm_noticed");
    private bool Moved => State.HasFlag("bin_moved");
    private bool Wedged => State.HasFlag("bell_wedged");

    public override async Task OnEnter(string entry)
    {
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
            await Say("The Harrington place. From the front it's a bank. From the back, it's still a bank, with a kitchen.");
            await Say("The kitchen door, the lintel, the key. Walk in like the delivery boys. Easy.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Look) or ("lintel", Verb.Look) when !Noticed:
                await NoticeAlarm();
                return true;

            case ("lintel", Verb.Hand) when !State.HasFlag("took_kitchen_key"):
                if (!Noticed)
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

            case ("bell", Verb.Hand or Verb.UseItem) when !Noticed:
                await Say("A burglar alarm, up on the wall. Out of my reach, and none of my business. Yet.");
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
        await Say("Open the door and the bell rings the house awake. \"Walk in like the delivery boys.\" Thanks, Tony.");
        await Say("The delivery boys come by day. With the cook expecting them.");
    }

    private async Task TryDoor()
    {
        if (!State.HasItem("kitchen_key"))
        {
            await Say(Noticed ? "Locked. And wired." : "Locked. The key's supposed to be on the lintel.");
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

    private async Task WedgeBell()
    {
        if (!await Game.Hud.Puzzle.Open(PuzzleKind.Bell)) return;
        await Say("Hold the hammer back, tie it clear of the gong, then let go. The wire stays intact.");
        await Say("My tie. Rose gave it to me, a lifetime ago. Knotted around the hammer and its bracket, holding it clear of the gong.");
        State.SetFlag("bell_wedged");
        await Say("Let it ring now. Nobody will hear a thing.");
    }

    /// <summary>Back out through the kitchen door, with or without Eleanor, and maybe with the house going up behind.</summary>
    private async Task Escape()
    {
        var eleanor = FindActor("eleanor");
        _ = Game.WalkTo(new Vector2(150, 238));
        if (eleanor != null && eleanor.Visible) await eleanor.MoveTo(new Vector2(190, 236), 46);
        await Wait(1.6);
        Player.Face(Facing.Right);
        eleanor?.FaceLeft(false);
        if (State.HasFlag("gas_on") && State.HasFlag("candle_lit"))
        {
            await Wait(1.0);
            await Game.Hud.Fade(1, 0.08);
            State.SetFlag(Endings.MansionExploded);
            await Wait(0.25);
            await Game.Hud.Fade(0, 1.4);
            await Say("*BOOOOOM*");
            await Say("The kitchen goes first. Then the study. Then everything Harrington ever wrote down in it.");
            if (eleanor != null && eleanor.Visible) await Say("eleanor", "Oh my God. Oh my God, Micah.");
            await Say("Time to go. Before the whole Gold Coast comes out in its pajamas.");
        }
        else
        {
            await Say("The house sleeps on, with the old man on the carpet. Somebody will find him by breakfast.");
        }
        await Game.WalkTo(new Vector2(30, 236));
        await Act3.End();
    }
}
