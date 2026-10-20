using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The public library, where Rose Jones works.</summary>
public partial class Library : Room
{
    public override Track? Music => Track.Investigation;

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_library_night")) return;
        State.SetFlag("seen_library_night");
        await Game.Run(async () =>
        {
            await Think("The public library, in broad daylight. Leather, dust, and a room full of people pretending not to whisper.");
            await Think("A man I don't know behind Rose's desk. Not her shift. Thank God. I couldn't have stood that look today.");
            await Think("...Still. Her empty chair, her pencils lined up like soldiers. She's back in my head, and she isn't leaving.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("exit", Verb.Walk or Verb.Hand) when State.HasFlag("on_map"):
                if (State.HasFlag("librarian_threatened")) State.SetFlag("library_banned");
                await Game.ChangeRoom("chicago_map", "start");
                return true;

            case ("librarian", Verb.Talk or Verb.UseItem or Verb.Hand) when State.HasFlag("librarian_threatened"):
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
                await Player.PlayPose("micah_draw");
                Player.SetPose("micah_aim");
                await Talk("librarian_threat");
                State.SetFlag("librarian_threatened");
                Player.SetPose(null);
                await Think("I've just held up a library. Mother would be so proud.");
                await LeaveWithBook();
                return true;
            case ("librarian", Verb.Hand) when !State.HasFlag("librarian_refused"):
                await Say("He looks like he'd break. And I haven't even asked him nicely yet.");
                return true;
            case ("librarian", Verb.Hand):
                if (!State.HasFlag("catalogue_identified"))
                {
                    await Say("Shaking him won't shake a title loose. I need the precise one first; that desk catalogue might help.");
                    return true;
                }
                await GrabCollar(target);
                await LeaveWithBook();
                return true;

            case ("shelves_right" or "shelves_left", Verb.Hand):
                await Say("Restricted books behind locked glass. The librarian has the key; I need a title from his catalogue.");
                return true;
            case ("globe", Verb.Hand):
                await Say("I spun it. It stopped on the Pacific. Story of my life: lots of water, no direction.");
                return true;
            case ("side_table", Verb.Hand):
                await Say("One glass would steady my hands. Then it'd be two, and I'd forget why I came.");
                return true;
            case ("desk", Verb.Hand or Verb.Look):
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
            case ("ladder", Verb.Hand):
                await Say("The ladder won't unlock the restricted glass. The librarian has the key.");
                return true;
        }
        return false;
    }

    /// <summary>
    /// Where Micah stands to grab the librarian: COLLAR_GAP pixels short of him, COLLAR_RISE nearer the shelves, as the
    /// micah_collar strips (tools/art/sprites.py) draw them both.
    /// </summary>
    public static readonly Vector2 CollarSpot = new(-46, 2);

    /// <summary>With the book in hand after the hold-up, Micah walks straight out through the hall door to the map.</summary>
    private async Task LeaveWithBook()
    {
        State.SetFlag("library_banned");
        if (FindHotspot("exit") is { } door) await Game.WalkTo(door.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    }

    /// <summary>Micah drags him in by the collar, holds him through the request, then lets him go.</summary>
    private async Task GrabCollar(Hotspot target)
    {
        var librarian = FindActor("librarian");
        Player.Teleport(target.Position + CollarSpot, Facing.Right);
        if (librarian != null) librarian.Visible = false;
        try
        {
            await Player.PlayPose("micah_collar");
            await Talk("librarian_collar");
            State.SetFlag("librarian_threatened");
            await Player.PlayPose("micah_collar_release");
        }
        finally
        {
            Player.SetPose(null);
            if (librarian != null) librarian.Visible = true;
        }
        await Think("Roughing up a librarian in broad daylight. Mother would be so proud.");
    }
}
