using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The convent on the North Side. A nun bars the corridor and asks Micah what he wants with Eleanor.</summary>
public partial class ConventCorridor : Room
{
    /// <summary>Act 2: Micah comes back from the map to ask about the Club.</summary>
    private bool ClubVisit => State.HasFlag("caleb_club");

    public override async Task OnEnter(string entry)
    {
        if (ClubVisit)
        {
            if (State.HasFlag("nun_club_asked")) return;
            await Game.Run(async () =>
            {
                await Wait(0.6);
                await Think("Same corridor, same wax, same sister. She saw me coming from the other end of it.");
                if (FindActor("nun") is { } nun) await Game.WalkTo(nun.WalkTo);
                await Talk("nun_club");
            });
            return;
        }
        if (State.HasFlag("nun_talked")) return;
        await Game.Run(async () =>
        {
            await Wait(0.6);
            await Think("Incense, floor wax and cold stone. Every convent smells like my mother's disappointment.");
            await Talk("nun");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (ClubVisit && await ClubInteract(verb, target, item)) return true;
        switch (target.Id, verb)
        {
            case ("nun", Verb.Talk):
                if (State.HasFlag("got_mirror"))
                {
                    if (!State.HasFlag("nun_farewell_done")) await Talk("nun_farewell");
                    else await Say("nun", "Go with God, Detective.");
                }
                else await Talk("nun");
                return true;
            case ("nun", Verb.UseItem) when Shows(item, "photo", "eleanor"):
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
                if (!State.HasFlag("got_mirror"))
                {
                    await Say("I didn't take a beating to come all this way for the architecture.");
                    return true;
                }
                if (!State.HasFlag("nun_farewell_done"))
                {
                    await Say("nun", "Detective, before you go...");
                    if (FindActor("nun") is { } sister)
                    {
                        await Game.WalkTo(sister.WalkTo);
                        Player.FaceTowards(sister.Position);
                    }
                    await Talk("nun_farewell");
                    await Game.WalkTo(target.WalkTo);
                }
                State.SetFlag("convent_departed");
                await Game.ChangeRoom("convent_road", "start");
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

    private async Task<bool> ClubInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("nun", Verb.Talk) when State.HasFlag("nun_club_asked"):
                await Say("nun", "I told you. I know nothing. Good night.");
                return true;
            case ("nun", Verb.Talk):
                await Talk("nun_club");
                return true;
            case ("nun", Verb.UseItem) when item == "revolver" && !State.HasFlag("nun_club_asked"):
                await Say("Not before I've asked nicely. Even I have a running order.");
                return true;
            case ("nun", Verb.UseItem) when item == "revolver":
                Player.Face(Facing.Right);
                Player.SetPose("micah_aim");
                await Say("I'm sorry, sister. I'm not asking anymore.");
                await Talk("nun_threat2");
                State.SetFlag("nun_threatened");
                await Wait(1.0);
                Player.SetPose(null);
                await Say("...");
                await Think("I put the revolver away. My hand is shaking. It never used to.");
                await Think("Harrington senior keeps his name off doors. The Tribune morgue keeps everybody's name - I'd start there.");
                await LeaveToMap();
                return true;
            case ("cell_door", Verb.Walk or Verb.Hand):
                await Say("Eleanor's cell. It'll be empty. She's not hiding anymore.");
                return true;
            case ("entrance", Verb.Walk or Verb.Hand):
                await LeaveToMap();
                return true;
        }
        return false;
    }

    private async Task LeaveToMap()
    {
        if (FindHotspot("entrance") is { } door) await Game.WalkTo(door.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    }
}