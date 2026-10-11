using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2: Theodore Harrington's office, reached through the window from the fire escape. The locked right drawer
/// (lockpick) holds the invitation to the Club; the invitation and portrait decode the closet's disguise lock.
/// Leaving through the window with all three takes Micah back to the map, with the Club open again.
/// </summary>
public partial class HarringtonOffice : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_harrington_office")) return;
        State.SetFlag("seen_harrington_office");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Say("Theodore Harrington's office. The light's on and the chair's empty. Old money keeps its lamps burning even when it goes home.");
            await Say("The sister said Harrington senior. Let's see what senior keeps in his desk.");
        });
    }

    private bool HasEverything => State.HasItem("invitation") && State.HasItem("mask") && State.HasItem("cloak");

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("drawer_left", Verb.Hand) when !State.HasFlag("drawer_left_open"):
                State.SetFlag("drawer_left_open");
                await Say("Cigars, a silver letter opener, and a bottle of bonded rye. Prohibition is for the help.");
                return true;
            case ("drawer_left", Verb.Hand):
                await Say("I'll leave the rye. It's the only time I've ever said that.");
                return true;

            case ("drawer_right", Verb.Hand) when !State.HasFlag("drawer_right_open"):
                await Say("Locked. Of course it is. You don't lock the drawer with the cigars in it.");
                return true;
            case ("drawer_right", Verb.UseItem) when item == "lockpick" && !State.HasFlag("drawer_right_open"):
                await Say("A cheap lock in an expensive desk. Rich men always think the wood is enough.");
                await Say("*click*");
                State.SetFlag("drawer_right_open");
                State.GiveItem("invitation");
                await Say("Under a stack of bank drafts: a black card with gold edges. The same knot as the mirror.");
                await Say("\"The Club. Saturday, at the turning of the night.\" Saturday is tonight.");
                return true;
            case ("drawer_right", Verb.Hand):
                await Say("Bank drafts. Thousands of dollars, paid to nobody in particular. Not my business tonight.");
                return true;
            case ("drawer_left" or "drawer_right", Verb.Kick):
                await Say("And bring the night watchman up here? He'll be done with the fire department any minute.");
                return true;

            case ("closet", Verb.Hand) when !State.HasFlag("harrington_closet_open"):
                State.SetFlag("harrington_closet_open");
                await Say("Overcoats. Three of them, all the same cut. Cedar blocks for the moths.");
                await Say("And the closet is deeper outside than it is inside. A good foot deeper.");
                return true;
            case ("closet", Verb.Hand):
                await Say("Overcoats, cedar, and a back panel that doesn't belong.");
                return true;
            case ("panel", Verb.Hand):
            case ("panel", Verb.UseItem) when item == "lockpick":
                if (State.HasFlag("secret_open"))
                {
                    await Say("The little doors are already open.");
                    return true;
                }
                if (!await Game.Hud.Puzzle.Open(PuzzleKind.Crests)) return true;
                State.SetFlag("secret_open");
                await Say("Star, sun, moon. The back of the closet swings open like a pair of little doors.");
                await Say("A white mask, and a black cloak. Folded like vestments.");
                return true;
            case ("panel", Verb.Kick):
                await Say("Kick the wall in a dead quiet building. Brilliant.");
                return true;
            case ("niche", Verb.Hand):
                State.SetFlag("took_mask");
                State.GiveItem("mask");
                State.GiveItem("cloak");
                await Say("The mask is cold. It weighs nothing at all. I'm not sure I want to know what that means.");
                await Say("An invitation, a mask, a cloak. Everything a gentleman needs for a night at the Club.");
                return true;

            case ("filing", Verb.Hand):
                await Say("Locked, and not worth picking. Whatever's in there, he'd never put the interesting part on paper.");
                return true;
            case ("portrait", Verb.Hand or Verb.Look):
                State.SetFlag("portrait_key_seen");
                await Say("A heraldic key painted beneath the portrait: raven and star, lion and sun, stag and moon. Old money labels its secrets.");
                return true;
            case ("portrait", Verb.Talk):
                await Say("Evening, Mr. Harrington. I'm just going through your drawers. Don't get up.");
                return true;
            case ("desk", Verb.Hand):
                await Say("The blotter's clean. He writes nothing down at this desk. Other desks, other hands.");
                return true;

            case ("window", Verb.Walk or Verb.Hand) when !HasEverything:
                await Say("Not yet. I didn't climb three floors of iron to go home with a cigar.");
                return true;
            case ("window", Verb.Walk or Verb.Hand):
                State.SetFlag("harrington_done");
                await Say("Back out the window, down the fire escape, and away before the fire trucks come.");
                await Game.ChangeRoom("chicago_map", "start");
                return true;
        }
        return false;
    }
}
