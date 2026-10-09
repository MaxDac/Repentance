using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The public library, where Rose Jones works and Eleanor hid Teddy's ledger.</summary>
public partial class Library : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_library")) return;
        State.SetFlag("seen_library");
        await Game.Run(() => Say("The public library. Leather, dust and silence. Rose always said it was the only honest room in Chicago."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("rose", Verb.Talk):
                await Talk("rose");
                return true;
            case ("rose", Verb.UseItem) when item == "photo":
                await Say("rose", "She's beautiful. Is that why you're here? Work? Of course it is.");
                return true;
            case ("rose", Verb.Hand):
                await Say("The last time I reached for her she was already gone. I kept my hands in my pockets.");
                return true;

            case ("shelves_right" or "ladder", Verb.Hand) when State.HasFlag("rose_tip") && !State.HasFlag("found_ledger"):
                State.SetFlag("found_ledger");
                State.GiveItem("ledger");
                await Say("Top shelf, behind the county land records... a green ledger with Harrington Steel's seal.");
                await Say("Tucked in the back cover: a receipt from the Lakeview Motor Court. Room 6. Paid in cash by T. Harrington.");
                return true;
            case ("shelves_right" or "shelves_left", Verb.Hand):
                await Say(State.HasFlag("found_ledger")
                    ? "I've got what I came for. The rest can stay alphabetized."
                    : "A hundred thousand books. I'd need to know which one before I started pulling.");
                return true;
            case ("globe", Verb.Hand):
                await Say("I spun it. It stopped on the Pacific. Story of my life: lots of water, no direction.");
                return true;
            case ("desk", Verb.Hand):
                await Say("Rose's desk. A drawer with my picture in it, face down. I left it the way she wanted it.");
                return true;
        }
        return false;
    }
}
