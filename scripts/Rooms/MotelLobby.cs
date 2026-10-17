using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 1: the flophouse lobby. The night clerk is scared of the men who collect on Fridays and won't let Micah
/// upstairs; he'll hand over his umbrella just to see him gone (Puzzle 19).
/// </summary>
public partial class MotelLobby : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_motel_lobby")) return;
        State.SetFlag("seen_motel_lobby");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("A long way down from the Aurelian. Brown wallpaper, a dead palm in a pot and a smell of boiled coffee and old cigars.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("clerk" or "counter" or "bell", Verb.Talk):
            case ("clerk", Verb.Hand):
                await Talk("motel_clerk");
                if (State.HasFlag("clerk_talked") && !State.HasFlag("took_umbrella"))
                    await Think("Upstairs is out, the front way. But every flophouse in Chicago has a back way, and this one has a fire escape.");
                return true;
            case ("clerk", Verb.UseItem) when item == "dollar":
                await Say("clerk", "Put your money away, mister. There's no room for you here at any price.");
                return true;
            case ("clerk", Verb.UseItem) when item == "photo":
                await Say("clerk", "I told you. I never saw nobody.");
                await Think("He looked at the photograph for half a second, then he looked at the stairs. That was answer enough.");
                return true;
            case ("clerk", Verb.UseItem) when item == "revolver":
                await Say("Pull a gun in a joint that pays Moretti, and I'll be in the river by Friday. Him too.");
                return true;
            case ("clerk", Verb.Kick):
                await Say("He's a scared little man behind a counter. Kicking him won't make him braver.");
                return true;

            case ("bell", Verb.Hand):
                await Say("*ding*");
                await Say("clerk", "I'm standing right here, mister.");
                return true;

            case ("stairs", Verb.Walk or Verb.Hand):
                if (FindActor("clerk") != null)
                {
                    await Say("clerk", "Hey! Nobody goes up. Rules of the house.");
                    await Say("Not this way, then.");
                }
                return true;

            case ("umbrella" or "umbrella_stand", Verb.Hand):
                if (State.HasFlag("took_umbrella"))
                {
                    await Say("Empty now. The clerk's umbrella is mine for the night.");
                    return true;
                }
                if (!State.HasFlag("clerk_talked"))
                {
                    await Say("A black umbrella with a crook handle. The clerk's, I'd guess. Help yourself to a man's umbrella before you've said good evening and he gets testy.");
                    return true;
                }
                await Say("Mind if I borrow your umbrella? It's coming down out there.");
                await Say("clerk", "Take it. Take it and go.");
                State.GiveItem("umbrella");
                State.SetFlag("took_umbrella");
                await Say("A good stout crook on the end of it. It'll keep the rain off, or reach something higher than me.");
                return true;
        }
        return false;
    }
}