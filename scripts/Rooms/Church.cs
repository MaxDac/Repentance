using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The cathedral interior: a little peace, and a lot of guilt.</summary>
public partial class Church : Room
{
    public override Track? Music => Track.ChurchOrgan;

    public override async Task OnEnter(string entry)
    {
        if (entry == "act3")
        {
            await Game.Run(Act3Return);
            return;
        }
        if (entry == "map" && State.HasFlag(Endings.KilledTony))
        {
            await Game.Run(TonyConfession);
            return;
        }
        if (entry == "map")
        {
            await Game.Run(FromMap);
            return;
        }
        if (State.HasFlag("act2_church"))
        {
            await Act2Visit();
            return;
        }
        if (State.HasFlag("seen_church_interior")) return;
        State.SetFlag("seen_church_interior");
        await Game.Run(() => Think("The nave swallows the street noise whole. Even my footsteps sound guilty in here."));
    }

    /// <summary>Act 2: Micah talks to his brother, then walks out on him and onto the streets of Chicago.</summary>
    private Task Act2Visit() => Game.Run(async () =>
    {
        State.SetFlag("seen_church_interior");
        await Wait(0.4);
        await Think("Candle smoke and cold stone. My brother is up by the altar rail, and I still don't know what I came to say.");
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        await Talk("caleb_act2");
        State.SetFlag("act2_church", false);
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        await Think("He calls after me. I keep walking. Walking out is the one thing I've always been good at.");
        await Game.ChangeRoom("chicago_map", "start");
    });

    /// <summary>
    /// Act 2, from the map: after the Club, Micah presses Caleb about it; later visits only get warnings, and whether
    /// Micah came back before Harrington's office and before the Club is remembered.
    /// </summary>
    private async Task FromMap()
    {
        await Wait(0.4);
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        if (!State.HasFlag("caleb_club"))
        {
            await Talk("caleb_club");
            // Micah doesn't answer that one. He just leaves.
            await Wait(1.2);
            await Think("No answer for that. None I could say out loud, not in his church.");
        }
        else if (State.HasFlag("harrington_done"))
        {
            State.SetFlag("church_before_club");
            await Talk("caleb_last");
        }
        else if (State.HasFlag("nun_threatened"))
        {
            State.SetFlag("church_before_office");
            await Talk("caleb_warn");
        }
        else
        {
            await Talk("caleb_repeat");
        }
        await OfferCross();
        await LeaveToMap();
    }

    private async Task OfferCross()
    {
        if (Endings.CanOfferCross(State.StoryAct, State.HasFlag))
            await Talk("caleb_cross");
    }

    /// <summary>
    /// Act 3, after Micah killed Tony: his confession to Caleb, past midnight. Turning himself in ends the story there
    /// (ending 12); "not yet" is a promise to meet Caleb at the station at sunrise, and on to the Gold Coast through the
    /// office in the storm. Either way there's no going back to the map.
    /// </summary>
    private async Task TonyConfession()
    {
        await Wait(0.4);
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        if (!State.HasFlag(Endings.ConfessedTony)) await Talk("caleb_tony");
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        if (State.HasFlag(Endings.SurrenderedTony))
        {
            await Game.Hud.Fade(1, 1.5);
            await Act3.End();
            return;
        }
        await Game.ChangeRoom("office_storm", "window");
    }

    private async Task Act3Return()
    {
        if (FindActor("caleb") is { } caleb)
        {
            await Game.WalkTo(caleb.WalkTo);
            Player.Face(Facing.Right);
        }
        State.SetFlag("church_act3_return");
        await Talk("caleb_act3_return");
        if (!State.HasFlag("thought_church_act3"))
        {
            State.SetFlag("thought_church_act3");
            await Think("Rose and Tommy. He says their names like a door I could still knock on. Then I think of her, and I'm gone again.");
        }
        await OfferCross();
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        await Game.ChangeRoom("office", "from_caleb");
    }

    private async Task LeaveToMap()
    {
        if (FindHotspot("doors") is { } doors) await Game.WalkTo(doors.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("doors", Verb.Walk or Verb.Hand) when State.HasFlag(Endings.KilledTony):
                await TonyConfession();
                return true;
            case ("doors", Verb.Walk or Verb.Hand) when State.StoryAct == 3:
                await Game.ChangeRoom("office", "from_caleb");
                return true;
            case ("doors", Verb.Walk or Verb.Hand) when State.HasFlag("club_out"):
                await Game.ChangeRoom("chicago_map", "start");
                return true;
            case ("caleb", Verb.Talk):
                await Talk("caleb");
                return true;
            case ("caleb", Verb.UseItem) when Shows(item, "photo", "eleanor"):
                await Say("caleb", "Eleanor. She sat in that pew for two nights before she said a word. Is she safe?");
                return true;
            case ("caleb", Verb.Hand):
                await Say("The last time I touched my brother it was with a fist. Not tonight.");
                return true;
            case ("confessional", Verb.Walk or Verb.Hand):
                await Say("Not tonight. It'd take more than one Saturday to get through my list.");
                return true;
        }
        return false;
    }
}
