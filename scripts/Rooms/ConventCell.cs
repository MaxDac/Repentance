using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Eleanor's cell at the convent: a bed, a lampstand, a book and a nightstand. In the drawer, a comb and a little
/// mirror with a strange symbol on the back. Micah won't leave without the mirror.
/// </summary>
public partial class ConventCell : Room
{
    private static readonly Texture2D Symbol = GD.Load<Texture2D>("res://assets/art/ui/triquetra.png");

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("cell_seen")) return;
        State.SetFlag("cell_seen");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Say("A bed, a lamp and a book. A woman who wore pearls to dinner slept here.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("exit", Verb.Walk or Verb.Hand) when !State.HasFlag("got_mirror"):
                await Say("There is still something to be found in this room.");
                return true;

            case ("nightstand" or "drawer", Verb.Hand) when !State.HasFlag("cell_drawer_open"):
                State.SetFlag("cell_drawer_open");
                await Say("The drawer sticks, then gives.");
                await Say("A comb and a little mirror. Not much to leave behind.");
                return true;
            case ("nightstand" or "drawer", Verb.Hand):
                await Say(State.HasFlag("got_mirror") ? "Just the comb left. It can stay." : "A comb and a little mirror.");
                return true;
            case ("nightstand" or "drawer", Verb.UseItem) when item == "lockpick":
                await Say("It isn't even locked. Nuns trust people. Must be nice.");
                return true;

            case ("mirror", Verb.Hand):
                await Say("A little hand mirror. Cheap glass, but somebody loved the frame.");
                await Say("There's something on the back...");
                await Game.Hud.ShowImage(Symbol);
                await Say("Three loops tied in one knot. No beginning, no end. Scratched in deep, on purpose.");
                await Say("Not the kind of thing the sisters teach in catechism. I'm keeping this.");
                State.SetFlag("got_mirror");
                State.GiveItem("mirror");
                return true;

            case ("comb", Verb.Hand):
                await Say("Tortoiseshell. A few dark hairs still caught in the teeth.");
                await Say("I'll leave the comb. A girl ought to have something to come back for.");
                return true;

            case ("lampstand", Verb.Hand):
                await Say("If I turn it down, I won't be able to see. If I turn it up, I'll see too much.");
                return true;
            case ("book", Verb.Hand):
                await Say("A breviary. Dog-eared at the Psalms. Somebody was looking for something.");
                return true;
            case ("bed", Verb.Hand):
                await Say("Thin mattress, nothing under it. I checked. Professional habit.");
                return true;
            case ("bed" or "nightstand" or "lampstand", Verb.Kick):
                await Say("Kick a nun's furniture. Nice, Micah. Very nice.");
                return true;
        }
        return false;
    }
}
