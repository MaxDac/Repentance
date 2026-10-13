using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The public library, where Rose Jones works and Eleanor hid Teddy's ledger.</summary>
public partial class Library : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("on_map"))
        {
            if (State.HasFlag("seen_library_night")) return;
            State.SetFlag("seen_library_night");
            await Game.Run(() => Say("The public library, in broad daylight. Leather, dust, and a room full of people pretending not to whisper."));
            return;
        }
        if (State.HasFlag("seen_library")) return;
        State.SetFlag("seen_library");
        await Game.Run(() => Say("The public library. Leather, dust and silence. Rose always said it was the only honest room in Chicago."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("exit", Verb.Walk or Verb.Hand) when State.HasFlag("on_map"):
                if (State.HasFlag("librarian_threatened")) State.SetFlag("library_banned");
                await Game.ChangeRoom("chicago_map", "start");
                return true;

            case ("librarian", Verb.Talk or Verb.UseItem) when State.HasFlag("librarian_threatened"):
                await Say("librarian", "Please. You have your book. Just go.");
                return true;
            case ("librarian", Verb.Talk):
            case ("librarian", Verb.UseItem) when Shows(item, "mirror", "triquetra"):
                await Talk("librarian");
                return true;
            case ("librarian", Verb.UseItem) when item == "revolver" && !State.HasFlag("librarian_refused"):
                await Say("Pulling a gun on a librarian before I've even asked nicely? Even I have manners.");
                return true;
            case ("librarian", Verb.UseItem) when item == "revolver":
                if (!State.HasFlag("catalogue_identified"))
                {
                    await Say("I need the precise title before I make him retrieve anything. That desk catalogue might help.");
                    return true;
                }
                Player.Face(Player.Position.X <= target.Position.X ? Facing.Right : Facing.Left);
                Player.SetPose("micah_aim");
                await Talk("librarian_threat");
                State.SetFlag("librarian_threatened");
                Player.SetPose(null);
                await Say("I'd just held up a library. Mother would have been so proud.");
                return true;
            case ("librarian", Verb.Hand):
                await Say("He looks like he'd break. I'm not that desperate. Not yet.");
                return true;
            case ("rose", Verb.Talk):
                await Talk("rose");
                return true;
            case ("rose", Verb.UseItem) when Shows(item, "photo", "eleanor"):
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
                if (State.HasFlag("on_map"))
                {
                    await Say("Restricted books behind locked glass. The librarian has the key; I need a title from his catalogue.");
                    return true;
                }
                await Say(State.HasFlag("found_ledger")
                    ? "I've got what I came for. The rest can stay alphabetized."
                    : "A hundred thousand books. I'd need to know which one before I started pulling.");
                return true;
            case ("globe", Verb.Hand):
                await Say("I spun it. It stopped on the Pacific. Story of my life: lots of water, no direction.");
                return true;
            case ("desk", Verb.Hand):
            case ("desk", Verb.Look) when State.HasFlag("on_map"):
                if (State.HasFlag("on_map"))
                {
                    if (!State.HasFlag("librarian_refused"))
                    {
                        await Say("I'd better ask the librarian about the mirror before digging through his catalogue.");
                        return true;
                    }
                    if (await Game.Hud.Puzzle.Open(PuzzleKind.Catalogue))
                    {
                        State.SetFlag("catalogue_identified");
                        await Say("Connected triquetra. Celtic traditions. A. R. Bell: Rites of the Old Isles, C-17. Now I know what to ask for.");
                    }
                    return true;
                }
                await Say("Rose's desk. A drawer with my picture in it, face down. I left it the way she wanted it.");
                return true;
            case ("ladder", Verb.Hand) when State.HasFlag("on_map"):
                await Say("The ladder won't unlock the restricted glass. The librarian has the key.");
                return true;
        }
        return false;
    }
}
