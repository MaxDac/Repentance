using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Room 507 at the Aurelian: where Eleanor slept the night she vanished, turned over by someone in a hurry.</summary>
public partial class EleanorRoom : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_eleanor_room")) return;
        State.SetFlag("seen_eleanor_room");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Room 507. Silk on the floor, feathers in the air. Somebody's been here before me, and they didn't knock either.");
            await Think("Her perfume still hangs in the air, under the cigar smoke. Whatever they were looking for, I'd bet they didn't find it.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("desk_drawer", Verb.Hand) when !State.HasFlag("eleanor_drawer_open"):
                await Say("The left drawer is locked. The only thing in this room nobody managed to open.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "lockpick" && !State.HasFlag("eleanor_drawer_open"):
                State.SetFlag("eleanor_drawer_open");
                await Say("A tension wrench, a rake, a little patience. The lock gave up before I did.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "lockpick":
            case ("desk_drawer", Verb.Hand):
                await Say(State.HasFlag("took_combination") ? "Empty now." : "There's a slip of paper inside.");
                return true;
            case ("desk_drawer", Verb.Kick):
                await Say("Kicking it open would bring the house detective. The quiet way, then.");
                return true;

            case ("paper", Verb.Hand):
                State.SetFlag("took_combination");
                State.GiveItem("combination");
                await Say("A slip of hotel paper in her hand. Three lines of Sunday school. Nobody writes that down unless it opens something.");
                return true;
            case ("paper", Verb.Look):
                await Say("Three riddles in Eleanor's handwriting. No numbers, no right or left. She didn't trust paper with anything plain.");
                return true;

            case ("closet", Verb.Hand) when !State.HasFlag("closet_open"):
                State.SetFlag("closet_open");
                await Say("Half her dresses were on the floor already. Behind the rest, set low in the back wall... a safe.");
                return true;
            case ("closet", Verb.Hand):
                await Say("Silk, cedar, and steel at the back.");
                return true;

            case ("safe", Verb.Hand) when !State.HasFlag("safe_open"):
            case ("safe", Verb.UseItem) when Shows(item, "combination", "safe_riddle") && !State.HasFlag("safe_open"):
                if (!await Game.Hud.Puzzle.Open(PuzzleKind.Safe)) return true;
                State.SetFlag("safe_open");
                await Say("Twelve apostles. Thirty-one days of December. The seventh day. The tumblers fell like dominoes.");
                await Say("Whoever tossed the room scratched the dial raw and never got the door open.");
                return true;
            case ("safe", Verb.Hand):
                await Say(State.HasFlag("took_brass_box") ? "Empty now." : "Something brass, catching the light.");
                return true;
            case ("safe", Verb.Kick):
                await Say("Steel. My foot would lose that argument.");
                return true;

            case ("brass_box", Verb.Hand):
                State.SetFlag("took_brass_box");
                State.GiveItem("brass_box");
                State.SetFlag("recover_hotel", false);
                await Say("A little brass box, engraved with lilies. The only thing in this room she bothered to lock away twice.");
                await Think("Her things trampled, her secrets locked away twice. Whoever Eleanor Harrington is, she was expecting company.");
                return true;

            case ("bed", Verb.Hand):
                await Say("Mattress slit, pillows gutted. Feathers and nothing else.");
                return true;
            case ("clothes", Verb.Hand):
                await Say("Her dresses, her stockings, her letters. All thrown down and trampled over.");
                return true;
            case ("chair", Verb.Hand):
                await Say("I left it on its back. Seemed only fair to the evidence.");
                return true;
            case ("window", Verb.Hand):
                await Say("Five floors down to the alley. She didn't leave this way.");
                return true;
            case ("vanity", Verb.Hand):
                await Say("Drawers pulled, perfume spilt. Smells like money and fear.");
                return true;
        }

        return false;
    }
}
