using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>Room 507 at the Aurelian: where Eleanor slept the night she vanished, turned over by someone in a hurry.</summary>
public partial class EleanorRoom : Room
{
    /// <summary>The First Interlude: Eleanor, the Tuesday night she left (Story.Interlude).</summary>
    private bool Interlude => State.HasFlag("interlude1");

    public override async Task OnEnter(string entry)
    {
        if (Interlude)
        {
            if (entry == "interlude") await Game.Run(() => Talk("interlude_aurelian"));
            return;
        }
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
        if (Interlude) return await InterludeInteract(verb, target);
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
                await Think("Now ain't that a pip. A swell doll who runs with the Club crowd, and she locks her secrets up with the Good Book. Strange, a dame like her bringin' Christ into it.");
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

    private bool Packed => State.HasFlag("interlude_box_packed");
    private bool ReadyToLeave => State.HasFlag("interlude_safe_locked") && State.HasFlag("interlude_drawer_locked")
        && State.HasFlag("interlude_phoned");

    /// <summary>
    /// Eleanor's last hour in Room 507: the box packed at the vanity and locked in the closet safe, the riddle in the
    /// drawer, a call to Rizzo's from the bedside telephone, then the door, where Sal is waiting.
    /// </summary>
    private async Task<bool> InterludeInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("vanity", Verb.Look):
                await Say("Perfume, powder, and a face I don't much like tonight.");
                return true;
            case ("vanity", Verb.Hand) when !Packed:
                State.SetFlag("interlude_box_packed");
                await Say("The card. The matchbook. The bluing. The little paper flower that blooms in water.");
                await Say("Everything a clever man would need to follow me. Into the brass box with them.");
                return true;
            case ("vanity", Verb.Hand):
                await Say("The box is packed. Nothing else on there I'll miss.");
                return true;

            case ("closet", Verb.Look):
                await Say("Half my dresses on the floor. The safe's at the back, behind the rest.");
                return true;
            case ("closet", Verb.Hand) when !Packed:
                await Say("The safe can wait. The box isn't packed yet.");
                return true;
            case ("closet", Verb.Hand) when !State.HasFlag("interlude_safe_locked"):
                State.SetFlag("interlude_safe_locked");
                await Say("Into the safe, and spin the dial. The Twelve at His table. December. The day He rested.");
                await Say("Let Theodore's men scratch at it all night. They never could count past their fingers.");
                return true;
            case ("closet", Verb.Hand):
                await Say("Locked. Twice locked, like everything else I care about.");
                return true;

            case ("desk_drawer", Verb.Look or Verb.Hand) when !State.HasFlag("interlude_safe_locked"):
                await Say("The riddle goes in the drawer. But the box goes in the safe first.");
                return true;
            case ("desk_drawer", Verb.Hand) when !State.HasFlag("interlude_drawer_locked"):
                State.SetFlag("interlude_drawer_locked");
                await Say("Three lines of Sunday school on hotel paper. My grandmother would be proud.");
                await Say("Into the drawer, and turn the key. Whoever opens this one, I want him to have earned it.");
                return true;
            case ("desk_drawer", _):
                await Say("Locked, with the riddle inside.");
                return true;

            case ("bed", Verb.Look):
                await Say("I slit the mattress myself. Let them think somebody went looking for something.");
                return true;
            case ("bed", Verb.Hand or Verb.Talk) when !State.HasFlag("interlude_phoned"):
                State.SetFlag("interlude_phoned");
                await Say("The telephone on the night table. My hand's shaking. Good thing nobody can see it down a wire.");
                await Talk("interlude_rizzo");
                return true;
            case ("bed", Verb.Hand or Verb.Talk):
                await Say("I've made my call. Now I wait for the knock that isn't Theodore's.");
                return true;

            case ("exit", Verb.Walk or Verb.Hand) when !ReadyToLeave:
                await Say(!State.HasFlag("interlude_phoned") ? "Not yet. Nobody's coming for me unless I call."
                    : "Not yet. Nothing of mine stays out in the open for them.");
                return true;
            case ("exit", Verb.Walk or Verb.Hand):
                await Game.WalkTo(target.WalkTo);
                await Say("*Knock, knock*");
                await Talk("interlude_sal");
                await Game.Hud.Fade(1, 1.2);
                await Game.ChangeRoom("speakeasy", "interlude");
                return true;

            case ("clothes", Verb.Look or Verb.Hand):
                await Say("I threw them down myself. Some of them deserved it.");
                return true;
            case ("chair", Verb.Look or Verb.Hand):
                await Say("I kicked it over. It felt better than it should have.");
                return true;
            case ("window", Verb.Look or Verb.Hand):
                await Say("Five floors down to the alley. The rain doesn't care who's leaving.");
                return true;
            case ("desk", Verb.Look or Verb.Hand):
                await Say("Hotel stationery. I've written Theodore a hundred letters on it, and sent him none.");
                return true;
        }
        return false;
    }
}