using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2, puzzle 13: the Tribune's newspaper morgue. Harrington senior keeps his name off doors, but the paper once ran
/// "HARRINGTON BUILDS..." - torn in two straight through the address. The top half is filed in drawer H, the bottom
/// half is on the copy spike; the layout desk's paste pot mends them (see <see cref="Recipes"/>), and Micah pins the
/// mended clipping on the Loop wall map at once (<see cref="OnCombined"/>), locating the Harrington Building on LaSalle Street (<c>harrington_located</c>),
/// which swaps the Tribune for Harrington's office on the Chicago map. The paste pot is only borrowed.
/// </summary>
public partial class NewspaperMorgue : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_morgue")) return;
        State.SetFlag("seen_morgue");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("The Tribune morgue. Yesterday's news lies down here in steel drawers and smells of glue.");
            await Think("The night man upstairs owes me for a story I never told. He gives me ten minutes and the lights.");
        });
    }

    private bool PasteOut => State.HasFlag("paste_out");
    private bool Located => State.HasFlag("harrington_located");

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door", Verb.Walk or Verb.Hand):
                await Leave();
                return true;

            case ("drawer_h", Verb.Look) when !State.HasFlag("took_clipping_top"):
                await Say("Drawer H. Hansen, Harper, Harrington. If the old man ever made the paper, he's in there.");
                return true;
            case ("drawer_h", Verb.Look):
                await Say("Harrington's folder: society pages, steel prices, and the clipping somebody tore in half.");
                return true;
            case ("drawer_h", Verb.Hand) when !State.HasFlag("took_clipping_top"):
                State.SetFlag("took_clipping_top");
                State.GiveItem("clipping_top");
                await Say("\"HARRINGTON BUILDS...\" Here's the headline. Somebody tore it straight through the address.");
                await Say("I've got the top half. The rest of the story went somewhere else.");
                return true;
            case ("drawer_h", Verb.Hand):
                await Say("Nothing else under Harrington but steel prices and charity balls.");
                return true;
            case ("cabinets", Verb.Hand):
                await Say("A thousand drawers of other people's bad news. I only need H.");
                return true;

            case ("spike", Verb.Look) when !State.HasFlag("took_clipping_bottom"):
                await Say("The copy spike, where dead stories go. The top sheet is half a clipping - the bottom of \"HARRINGTON BUILDS...\", torn through the address.");
                return true;
            case ("spike", Verb.Look):
                await Say("Spiked copy. Rejected stories, rejected lives. Nothing else with his name on it.");
                return true;
            case ("spike", Verb.Hand) when !State.HasFlag("took_clipping_bottom"):
                State.SetFlag("took_clipping_bottom");
                State.GiveItem("clipping_bottom");
                await Say("The bottom half. \"...Building, LaS\" and a photo caption. It ends where the top half begins.");
                return true;
            case ("spike", Verb.Hand):
                await Say("Careful. That spike has gone through better reporters than me.");
                return true;

            case ("paste_pot", Verb.Look):
                await Say(PasteOut
                    ? "A ring of dried paste where the pot stood. The layout boys will want it back."
                    : "A pot of library paste, the brush standing up in it. The whole front page gets glued together right here.");
                return true;
            case ("paste_pot", Verb.Hand) when !PasteOut:
                State.SetFlag("paste_out");
                State.GiveItem("paste");
                await Say("Library paste and a brush. Nobody's pasting up pages at this hour; I'll bring it back.");
                return true;
            case ("paste_pot" or "layout_desk", Verb.Hand or Verb.UseItem) when PasteOut && (verb == Verb.Hand || item == "paste"):
                await ReturnPaste();
                return true;

            case ("wall_map", Verb.Look):
                await Say("Map of the Loop, pins for every address the paper ever printed.");
                if (Located) await Say("And one with my clipping under it: the Harrington Building, LaSalle Street.");
                return true;
            case ("wall_map", Verb.UseItem) when item == "clipping" || (!Located && Shows(item, "", "harrington_building")):
                if (item == "clipping") State.TakeItem("clipping");
                await PinClipping();
                return true;
            case ("wall_map", Verb.UseItem) when item is "clipping_top" or "clipping_bottom":
                await Say("Half an address is no address. I need both halves stuck together first.");
                return true;
            case ("wall_map", Verb.Hand):
                await Say(Located ? "The pin stays. The address stays with me." : "A pincushion without a name to go with it.");
                return true;
        }
        return false;
    }

    /// <summary>The mended clipping goes straight onto the wall map: Micah doesn't need telling where it belongs.</summary>
    public override async Task OnCombined(string result)
    {
        if (result != "clipping" || Located || !State.HasItem("clipping")) return;
        if (FindHotspot("wall_map") is { } map) await Game.WalkTo(map.WalkTo);
        State.TakeItem("clipping");
        await PinClipping();
    }

    private async Task PinClipping()
    {
        State.SetFlag("harrington_located");
        await Say("\"Harrington senior keeps his offices at the Harrington Building, LaSalle Street.\"");
        await Say("I pin it where it belongs. The Harrington Building, LaSalle Street - right in the middle of the Loop, where the money sleeps.");
        await Think("One pin in a city of pins. Somewhere under it, an old man who knows where Eleanor is.");
        if (PasteOut) await Say("I'll put the paste back on my way out.");
    }

    private async Task ReturnPaste()
    {
        State.TakeItem("paste");
        State.SetFlag("paste_out", false);
        await Say("Back where the layout boys left it.");
    }

    private async Task Leave()
    {
        if (State.HasItem("paste"))
        {
            if (FindHotspot("paste_pot") is { } pot) await Game.WalkTo(pot.WalkTo);
            State.TakeItem("paste");
            State.SetFlag("paste_out", false);
            await Think("I put the paste pot back on the layout desk. Borrowed is borrowed.");
        }
        if (FindHotspot("door") is { } door) await Game.WalkTo(door.WalkTo);
        await Game.ChangeRoom("chicago_map", "start");
    }
}
