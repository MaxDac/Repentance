using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2, puzzle 14: the Club's vestibule on the rite night. Micah comes in masked from the map and can't go back out.
/// The plaque wants the summons "sealed by the first of the procession": the coat-check's sealing wax, softened with the
/// Micah's lighter (never used up), dripped on the invitation and pressed with the raven signet from the cloak rack (the
/// invitation lists the procession raven, lion, stag). The sealed invitation goes through the inner door's slot and comes
/// back out (the door has already vouched for Micah; the Master of Ceremonies doesn't ask for it again), sets <c>vestibule_passed</c> and opens the club hall.
/// Only one signet is borrowed at a time; any still held is hung back up on the way in.
/// </summary>
public partial class ClubVestibule : Room
{
    public override Track? Music => Track.ClubStrings;

    private static readonly string[] Signets = { "signet_raven", "signet_lion", "signet_stag" };

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_vestibule")) return;
        State.SetFlag("seen_vestibule");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("A vestibule in wine and gold, a cloakroom nobody minds, and an inner door with a slot in it instead of a doorman.");
            await Think("Their mask on my face, their cloak on my back. Somewhere past that door, Eleanor.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("street_door", Verb.Walk or Verb.Hand):
                await Say("Not back out. Not tonight. Eleanor is somewhere past that inner door.");
                return true;

            case ("sealing_wax", Verb.Hand):
                State.SetFlag("took_sealing_wax");
                State.GiveItem("sealing_wax");
                await Say("A stick of the house wax. Cold as the marble it's lying on.");
                return true;
            case ("coat_check", Verb.Hand):
                await Say("Nothing on the hooks but other men's coats. I'm not here to steal a coat.");
                return true;

            case ("cloak_raven", _):
                return await Cloak(verb, item, "signet_raven", "raven");
            case ("cloak_lion", _):
                return await Cloak(verb, item, "signet_lion", "lion");
            case ("cloak_stag", _):
                return await Cloak(verb, item, "signet_stag", "stag");

            case ("slot" or "inner_door", Verb.UseItem) when item == "sealed_invitation":
                await Pass();
                return true;
            case ("slot" or "inner_door", Verb.UseItem) when item == "invitation":
                await Say("The slot won't take a bare card. \"Sealed by the first of the procession,\" says the plaque.");
                return true;
            case ("slot" or "inner_door", Verb.UseItem) when item == "invitation_waxed":
                await Say("A blob of wax with nothing pressed into it. It needs the seal of the first of the procession.");
                return true;
            case ("slot" or "inner_door", Verb.UseItem) when item is "signet_raven" or "signet_lion" or "signet_stag":
                await Say("The slot wants a card, not a ring. The ring belongs on the card - in the wax.");
                return true;
            case ("slot" or "inner_door", Verb.UseItem):
                await Say("The slot is for summonses, not my pocket litter.");
                return true;
            case ("slot" or "inner_door", Verb.Walk or Verb.Hand) when State.HasFlag("vestibule_passed"):
                await GoThrough();
                return true;
            case ("slot" or "inner_door", Verb.Walk or Verb.Hand):
                await Say("Locked. It doesn't open for a hand - only for a card through the slot.");
                return true;
            case ("slot" or "inner_door", Verb.Kick):
                await Say("Kick the door of a room full of them? I'd rather keep my mask on and my teeth in.");
                return true;
        }
        return false;
    }

    /// <summary>Each cloak lends its signet; taking one hangs any other back on its own clasp.</summary>
    private async Task<bool> Cloak(Verb verb, string? item, string signet, string crest)
    {
        if (verb == Verb.UseItem && item == signet)
        {
            State.TakeItem(signet);
            await Say($"The {crest} ring goes back on its clasp.");
            return true;
        }
        if (verb != Verb.Hand) return false;
        if (State.HasItem(signet))
        {
            await Say($"I already have the {crest} ring.");
            return true;
        }
        bool swapped = false;
        foreach (var other in Signets)
        {
            if (other == signet || !State.HasItem(other)) continue;
            State.TakeItem(other);
            swapped = true;
        }
        State.GiveItem(signet);
        await Say(swapped
            ? $"I hang the other ring back where I found it and slip the {crest} off its clasp."
            : $"I slip the {crest} signet off the clasp. Nobody's watching the cloaks.");
        return true;
    }

    private async Task Pass()
    {
        foreach (var signet in Signets)
            if (State.HasItem(signet)) State.TakeItem(signet);
        await Say("The card goes into the slot. Something behind the door reads the raven, and approves.");
        State.SetFlag("vestibule_passed");
        await Wait(0.6);
        await Think("The card slides back out of the slot, like change. The door swings in.");
        await GoThrough();
    }

    /// <summary>Through the open inner door to the hall; the door runs it too once the card has passed.</summary>
    private async Task GoThrough()
    {
        if (FindHotspot("inner_door") is { } door) await Game.WalkTo(door.WalkTo + new Vector2(0, -4));
        await Game.ChangeRoom("club_hall", "from_street");
    }
}
