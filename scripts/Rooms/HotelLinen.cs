using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The Aurelian's fifth-floor linen room, where the routed staff lift lets out. The corridor door to 507 is
/// night-bolted from the far side; a hanger from the laundry rack, bent into a hook with the cart's pliers,
/// reaches the bolt through the cracked transom.
/// </summary>
public partial class HotelLinen : Room
{
    public override async Task OnEnter(string entry)
    {
        // Coming back from the corridor side the bolt is within reach, which also covers saves made before this room existed.
        if (entry == "corridor") State.SetFlag("linen_door_open");
        if (State.HasFlag("seen_hotel_linen")) return;
        State.SetFlag("seen_hotel_linen");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Fifth floor, linen room. Starch and hot pipes. 507's on the other side of that door. So is a night bolt.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("corridor_door", Verb.Walk or Verb.Hand) when State.HasFlag("linen_door_open"):
                await Game.ChangeRoom("eleanor_room", "corridor");
                return true;
            case ("corridor_door", Verb.Walk or Verb.Hand):
                await Say("Bolted from the corridor side. The maids must lock up at night and come round the long way.");
                return true;
            case ("corridor_door", Verb.UseItem) when item == "wire_hook" && !State.HasFlag("linen_door_open"):
                await Say("Up through the transom, feel for the knob of the bolt... hook it... and draw.");
                State.TakeItem("wire_hook");
                State.SetFlag("linen_door_open");
                await Say("Clack. Open. A hotel bolt is only as good as the inch of glass above it.");
                await Game.ChangeRoom("eleanor_room", "corridor");
                return true;
            case ("corridor_door", Verb.UseItem) when item == "lockpick":
                await Say("No keyhole on this side. The bolt's the only lock.");
                return true;
            case ("corridor_door", Verb.UseItem) when item == "hanger":
                await Say("A straight hanger just slides off the bolt. It needs a proper hook on the end, bent tight.");
                return true;
            case ("corridor_door", Verb.UseItem) when item == "pliers":
                await Say("Pliers won't reach through an inch of transom. Something long and thin would, with a bend in it.");
                return true;
            case ("corridor_door", Verb.Kick):
                await Say("Kick in a door on the fifth floor at this hour and the house detective is up here in two minutes.");
                return true;

            case ("rack", Verb.Hand) when !State.HasFlag("took_hanger"):
                State.SetFlag("took_hanger");
                State.GiveItem("hanger");
                await Say("A spare wire hanger. The Aurelian won't miss one. It's barely missed a murder.");
                return true;
            case ("rack", Verb.Hand):
                await Say("Uniforms for the morning shift. I'll leave the girls their hangers.");
                return true;

            case ("cart", Verb.Hand) when !State.HasFlag("took_pliers") && !State.HasFlag("made_wire_hook"):
                State.SetFlag("took_pliers");
                State.GiveItem("pliers");
                await Say("A pair of radiator pliers. Somebody on the night staff is going to blame somebody else.");
                return true;
            case ("cart", Verb.Hand) when State.HasFlag("made_wire_hook"):
                await Say("The pliers are back on the tray where I found them. No harm done.");
                return true;
            case ("cart", Verb.Hand):
                await Say("Soap, towels and a stack of little envelopes marked GRATUITIES. All of them empty.");
                return true;

            case ("shelves", Verb.Hand):
                await Say("Linen enough for a hundred beds. Not a single secret folded into any of it.");
                return true;
            case ("chute", Verb.Hand):
                await Say("Down to the laundry. I'd rather not leave the building in a bundle of sheets.");
                return true;
            case ("bulb", Verb.Hand):
                await Say("Hot. And it's the only light up here. I'll leave it be.");
                return true;
            case ("shelves" or "cart" or "rack", Verb.Kick):
                await Say("Make a racket up here and I'll be explaining myself to the house detective.");
                return true;
        }
        return false;
    }
}
