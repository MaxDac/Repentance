using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Harrington kitchen, in the dark. On the way in it's just a corridor with copper pans. On the way out, with the old
/// man on his bedroom carpet, the back door is open and the cellar trapdoor leads down to the Club's whiskey: everything
/// a house needs to burn. Eleanor, if she came, waits here by the door.
/// </summary>
public partial class MansionKitchen : Room
{
    private bool Escaping => State.HasFlag("escaping");
    private bool Coda => State.HasFlag("eleanor_coda");

    public override async Task OnEnter(string entry)
    {
        if (Coda)
        {
            if (entry == "eleanor_coda")
                await Game.Run(() => Think("The kitchen, in the dark. Copper pans, and the back door, and past it the whole of the night."));
            else if (entry == "cellar" && State.HasFlag(Endings.EleanorBurned))
                await Game.Run(() => Think("Smoke came up the cellar steps behind her, sweet with rye."));
            return;
        }
        if (entry == "escape")
        {
            await Game.Run(async () =>
            {
                await Wait(0.4);
                if (State.HasFlag(Endings.EleanorConvinced))
                    await Say("eleanor", "The back door, Micah. Please. Let's go.");
                else
                    await Think("Alone. She chose that house. Or the house chose her.");
                await Think("There's a barrel of the Club's whiskey down in that cellar. This house runs on bootleg liquor, like everything else on the Gold Coast.");
            });
            return;
        }
        if (entry == "cellar" && State.HasFlag("cellar_fire"))
        {
            await Game.Run(async () =>
            {
                await Wait(0.3);
                if (State.HasFlag(Endings.EleanorConvinced))
                {
                    await Say("eleanor", "Micah... there's smoke coming up through the floor. What did you do?");
                    await Say("Closed the Club's account. Out. Now.");
                }
                else await Think("Smoke at my heels, and the floor getting warm. Time to leave. Right now.");
            });
            return;
        }
        if (entry != "start" || State.HasFlag("seen_mansion_kitchen")) return;
        State.SetFlag("seen_mansion_kitchen");
        await Game.Run(async () =>
        {
            await Think("Copper pans glint in the dark. Somewhere upstairs a clock is counting the old man's money.");
            await Think("A kitchen bigger than my office, my flat and my marriage put together. Quiet as a church.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (Coda) return await CodaInteract(verb, target);
        switch (target.Id, verb)
        {
            case ("back_door", Verb.Hand or Verb.Walk) when Escaping:
                await Game.ChangeRoom("mansion_exterior", "escape");
                return true;
            case ("back_door", Verb.Hand or Verb.Walk):
                await Say("Not without Eleanor.");
                return true;

            case ("baize_door", Verb.Hand or Verb.Walk) when Escaping:
                await Say("Not back in there. Somebody's on the stairs by now.");
                return true;
            case ("cellar_door", Verb.Hand or Verb.Walk) when State.HasFlag("cellar_fire"):
                await Say("Not back down there. It's all fire under that trapdoor.");
                return true;
            case ("cellar_door", Verb.Hand or Verb.Walk) when Escaping:
                if (State.HasFlag(Endings.EleanorConvinced))
                {
                    await Say("eleanor", "Micah? The door's that way.");
                    await Say("Wait for me by the door. One minute.");
                }
                await Game.ChangeRoom("mansion_cellar", "kitchen");
                return true;
            case ("baize_door", Verb.Hand or Verb.Walk) when !State.HasFlag("baize_unbolted"):
                await Say("Bolted from the house side. There'll be another way up - houses like this always kept one for the deliveries.");
                return true;
            case ("baize_door", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_study", "start");
                return true;
            case ("baize_door", Verb.Kick):
                await Say("And bring the whole house down the back stairs? No.");
                return true;

            case ("cellar_door", Verb.Hand or Verb.Walk):
                if (!State.HasFlag("seen_mansion_cellar"))
                    await Say("I haul on the ring. Cold air and the smell of old wine come up out of the black.");
                await Game.ChangeRoom("mansion_cellar", "kitchen");
                return true;

            case ("range", Verb.Hand) when !Escaping:
            case ("candle", Verb.Hand) when !Escaping:
            case ("candle", Verb.UseItem) when !Escaping && item == MicahKit.LighterId:
                await Say("Not why I'm here. Eleanor's somewhere upstairs.");
                return true;
            case ("range" or "candle", Verb.Hand or Verb.UseItem) when item is null or MicahKit.LighterId:
                if (State.HasFlag("cellar_fire"))
                    await Say("No need. The cellar's doing the job for me.");
                else
                    await Say("Gas and a candle? It would explode before we'd be far enough. But maybe if I use all that alcohol in the cellar...");
                return true;
        }
        return false;
    }

    /// <summary>Eleanor on her way out: the back door, or the cellar and the Club's whiskey first.</summary>
    private async Task<bool> CodaInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("back_door", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_exterior", "eleanor_coda");
                return true;
            case ("baize_door", Verb.Hand or Verb.Walk):
                await Say("eleanor", "Not back up there. Not back to him.");
                return true;
            case ("cellar_door", Verb.Hand or Verb.Walk) when State.HasFlag(Endings.EleanorBurned):
                await Say("eleanor", "There's nothing down there now but fire.");
                return true;
            case ("cellar_door", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_cellar", "kitchen");
                return true;
            case ("range" or "candle", Verb.Hand):
                await Say("eleanor", "Gas and a candle. I'd go up with the house, and he isn't worth that.");
                return true;
        }
        return false;
    }
}
