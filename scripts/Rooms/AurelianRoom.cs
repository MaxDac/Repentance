using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>A luxury hotel room at the Aurelian, preserved badly by money and worse by memory.</summary>
public partial class AurelianRoom : Room
{
    // Set when Micah searches the bed; swaps the full-room background to the unmade variant.
    private const string BedDisturbedFlag = "aurelian_bed_disturbed";

    private static readonly Texture2D MadeBackground =
        GD.Load<Texture2D>("res://assets/art/rooms/hotel_room_made.png");

    private static readonly Texture2D UnmadeBackground =
        GD.Load<Texture2D>("res://assets/art/rooms/hotel_room_unmade.png");

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is not { } background) return;
        background.Texture = State.HasFlag(BedDisturbedFlag) ? UnmadeBackground : MadeBackground;
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("bed", Verb.Hand):
                if (State.HasFlag(BedDisturbedFlag))
                {
                    await Say("I'd already torn through the sheets. No ransom note. No miracle.");
                    return true;
                }

                State.SetFlag(BedDisturbedFlag);
                await Say("I checked under the bed. Dust, one stocking, and the feeling I'd arrived a day too late.");
                return true;

            case ("desk", Verb.Hand):
                await Say("Hotel stationery. Heavy stock, light conscience.");
                return true;

            case ("wardrobe", Verb.Hand):
                await Say("Empty hangers and cedar. Eleanor hadn't left much behind.");
                return true;

            case ("window", Verb.Hand):
                await Say("It opened a crack. Enough for smoke. Not enough for escape.");
                return true;

            case ("vanity", Verb.Hand):
                await Say("Powder on the tray. No lady at the mirror.");
                return true;

            case ("telephone", Verb.Hand or Verb.Talk):
                await Say("The line was quiet. In this town, silence usually costs extra.");
                return true;

            case ("sconce", Verb.Hand or Verb.Kick):
                await Say("Crystal and brass. I left it hanging.");
                return true;
        }

        return false;
    }
}
