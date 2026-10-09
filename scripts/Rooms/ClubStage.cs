using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The Starlight's stage, where Eleanor Harrington sings as "Nora".</summary>
public partial class ClubStage : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_club_stage")) return;
        State.SetFlag("seen_club_stage");
        await Game.Run(async () =>
        {
            await Say("One spotlight, one microphone, one brunette singing like the song owed her money.");
            await Say("Brown hair instead of the society blonde they print in the papers. But it was her.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("eleanor", Verb.Talk):
                await Talk("eleanor");
                return true;
            case ("eleanor", Verb.UseItem) when item == "photo":
                await Say("eleanor", "Teddy's favorite. He liked me blonde and quiet. I dyed my hair. Now I'm working on the quiet.");
                return true;
            case ("eleanor", Verb.UseItem) when item == "dollar":
                await Say("eleanor", "Keep it, mister. You look like you need it more than the band does.");
                return true;
            case ("eleanor", Verb.Hand or Verb.Kick):
                await Say("eleanor", "Hands off the talent, mister. The last man who tried is still picking up his teeth.");
                return true;
        }
        return false;
    }
}
