using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Past the city limits: the field where the bookkeeper's drive ended. The demo ends here.</summary>
public partial class Outskirts : Room
{
    protected override void OnRefresh()
    {
        if (FindHotspot("disturbed_earth") is { } spot)
            spot.DisplayName = State.HasFlag("burial_surveyed") ? "marked burial spot" : "unverified disturbed earth";
    }

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
            case ("fence_post", Verb.UseItem) when item == "map":
                if (State.HasFlag("burial_surveyed"))
                {
                    await Say("Thirty paces east of this post, ten north of the creek. I've marked the place.");
                    return true;
                }
                if (await Game.Hud.Puzzle.Open(PuzzleKind.Survey))
                {
                    State.SetFlag("burial_surveyed");
                    await Say("Column eight, row eight. Both bearings agree. That's the patch to dig.");
                }
                return true;
            case ("fence_post", Verb.Hand):
                await Say("The map's bearing notes start at this fence post. I should use it here and count, not guess.");
                return true;
            case ("disturbed_earth", Verb.Hand) or ("disturbed_earth", Verb.UseItem) when item is null or "map":
                if (!State.HasItem("map") || !State.HasFlag("burial_surveyed"))
                {
                    await Say("Somebody dug here, but a hunch isn't enough. Use the completed map at the fence post and check both bearings.");
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
