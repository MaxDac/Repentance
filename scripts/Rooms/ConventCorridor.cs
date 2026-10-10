using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The convent on the North Side. A nun bars the corridor and asks Micah what he wants with Eleanor.</summary>
public partial class ConventCorridor : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("nun_talked")) return;
        await Game.Run(async () =>
        {
            await Wait(0.6);
            await Say("Incense, floor wax and cold stone. Every convent smells like my mother's disappointment.");
            await Talk("nun");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("nun", Verb.Talk):
                await Talk("nun");
                return true;
            case ("nun", Verb.UseItem) when item == "photo":
                await Say("nun", "I know her face, young man. I have prayed for it.");
                return true;
            case ("nun", Verb.UseItem):
                await Say("nun", "We take a vow of poverty here. Keep your things.");
                return true;
            case ("nun", Verb.Hand or Verb.Kick):
                await Say("I'd sooner pick a fight with Sal again. At least Sal doesn't have God in his corner.");
                return true;

            case ("cell_door", Verb.Walk or Verb.Hand) when !State.HasFlag("nun_talked"):
                await Say("Not without the sister's say-so. I'm in enough trouble with the management upstairs.");
                return true;
            case ("cell_door", Verb.Kick):
                await Say("Kicking a door in a convent. Straight to the hot place, no stops.");
                return true;
            case ("entrance", Verb.Walk or Verb.Hand):
                await Say("I didn't take a beating to come all this way for the architecture.");
                return true;
            case ("statue" or "candles", Verb.Hand):
                await Say("I'd light one, but I'm not sure who I'd be lighting it for.");
                return true;
            case ("bench", Verb.Hand):
                await Say("My knees have done enough kneeling for one night.");
                return true;
        }
        return false;
    }
}
