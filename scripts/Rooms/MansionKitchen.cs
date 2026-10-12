using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Harrington kitchen, in the dark. On the way in it's just a corridor with copper pans. On the way out, with the old
/// man on his bedroom carpet, there's a gas range and a candle on the table: everything a house needs to burn.
/// </summary>
public partial class MansionKitchen : Room
{
    private bool Escaping => State.HasFlag("escaping");

    public override async Task OnEnter(string entry)
    {
        if (entry == "escape")
        {
            await Game.Run(async () =>
            {
                await Wait(0.4);
                if (State.HasFlag(Endings.EleanorConvinced))
                    await Say("eleanor", "The back door, Micah. Please. Let's go.");
                else
                    await Say("Alone. She chose that house. Or the house chose her.");
                await Say("Gas range. A candle on the table. Matches. This house runs on the Club's gas, like everything else on the Gold Coast.");
            });
            return;
        }
        if (entry != "start" || State.HasFlag("seen_mansion_kitchen")) return;
        State.SetFlag("seen_mansion_kitchen");
        await Game.Run(() => Say("A kitchen bigger than my office, my flat and my marriage put together. Quiet as a church."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("back_door", Verb.Hand or Verb.Walk) when Escaping:
                await Game.ChangeRoom("mansion_exterior", "escape");
                return true;
            case ("back_door", Verb.Hand or Verb.Walk):
                await Say("Not without Eleanor.");
                return true;

            case ("baize_door", Verb.Hand or Verb.Walk) when Escaping:
            case ("cellar_door", Verb.Hand or Verb.Walk) when Escaping:
                await Say("Not back in there. Somebody's on the stairs by now.");
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
                await Say("Not why I'm here. Eleanor's somewhere upstairs.");
                return true;

            case ("range", Verb.Hand) when State.HasFlag("gas_on"):
                await Say("Every tap's open. The kitchen smells like a hospital waiting room.");
                return true;
            case ("range", Verb.Hand):
                await Say("One tap. Two. Three. All of them.");
                State.SetFlag("gas_on");
                await Say("*Hssssssss*");
                if (State.HasFlag(Endings.EleanorConvinced))
                {
                    await Say("eleanor", "Micah... what are you doing?");
                    await Say("Closing the Club's account.");
                }
                await LeaveHint();
                return true;

            case ("candle", Verb.Hand or Verb.UseItem) when State.HasFlag("candle_lit"):
                await Say("It burns, nice and steady. For now.");
                return true;
            case ("candle", Verb.Hand):
                await Say("A kitchen match off the box, and the candle catches.");
                State.SetFlag("candle_lit");
                await LeaveHint();
                return true;
        }
        return false;
    }

    private Task LeaveHint() =>
        State.HasFlag("gas_on") && State.HasFlag("candle_lit")
            ? Say("Gas, rising. A flame, waiting. Time to leave. Right now.")
            : Task.CompletedTask;
}
