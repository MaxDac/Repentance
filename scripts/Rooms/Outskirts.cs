using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Past the city limits: the field where the bookkeeper's drive ended. The demo ends here.</summary>
public partial class Outskirts : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_outskirts")) return;
        State.SetFlag("seen_outskirts");
        await Game.Run(() => Say("The last fence post, the last streetlight, the last place a man would go to bury something."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("disturbed_earth", Verb.Hand) or ("disturbed_earth", Verb.UseItem) when item is null or "map":
                if (!State.HasItem("map"))
                {
                    await Say("Somebody dug here. I'm not about to dig up the whole county on a hunch.");
                    return true;
                }
                if (State.HasFlag("found_evidence")) return false;
                State.SetFlag("found_evidence");
                await Say("Thirty paces from the last fence post, like the map says. The earth is soft. Too soft.");
                await Say("A rusted tin box. Moretti's IOUs, every one signed by Teddy. And a gold cufflink. T.H.");
                State.GiveItem("evidence");
                await Ending();
                return true;
        }
        return false;
    }

    private async Task Ending()
    {
        if (FindActor("sal") is not { } sal) return;
        State.SetFlag("ending");
        Refresh();
        await Wait(0.6);
        Player.FaceTowards(sal.Position);
        await sal.MoveTo(Player.Position + new Vector2(40, 2), 50);
        await DialogueManager.Instance.Talk("ending");
        await Game.Hud.Fade(1, 1.2);
        Game.Hud.ShowCaption("To be continued...");
        // The demo ends here; keep the game locked on the caption.
        await new TaskCompletionSource().Task;
    }
}
