using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

public partial class MotelRoom : Room
{
    private const string BedSearchedFlag = "motel_bed_searched";

    private static readonly Texture2D MadeBackground = GD.Load<Texture2D>("res://assets/art/rooms/motel_room_made.png");
    private static readonly Texture2D UnmadeBackground = GD.Load<Texture2D>("res://assets/art/rooms/motel_room_unmade.png");

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is not { } background) return;
        background.Texture = State.HasFlag(BedSearchedFlag) ? UnmadeBackground : MadeBackground;
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("bed", Verb.Hand) when !State.HasFlag("map_base_taken") && !State.HasFlag("found_map"):
                State.SetFlag(BedSearchedFlag);
                State.SetFlag("map_base_taken");
                State.GiveItem("map_base");
                Refresh();
                await Say("Under the mattress: part of a county map. Windmill, creek bend, fence gate. Three registration marks for another sheet.");
                return true;
            case ("bed", Verb.Hand) when !State.HasFlag(BedSearchedFlag):
                State.SetFlag(BedSearchedFlag);
                await Say("I turned the bed over. Nothing but motel lint, old smoke, and fresh disappointment.");
                return true;
            case ("bed", Verb.Hand):
                await Say("I've already tossed the bed. It still looks guilty.");
                return true;

            case ("chair", Verb.Hand):
                await Say("Sit in that and I'd be wearing it home.");
                return true;
            case ("chair", Verb.Kick):
                await Say("One good kick and the chair'd retire before I do.");
                return true;

            case ("wall", Verb.Hand or Verb.Kick):
                await Say("The wall's already falling apart. It doesn't need my help.");
                return true;

            case ("window", Verb.Hand):
                await Say("It sticks halfway. Just enough to let in rain and regret.");
                return true;

            case ("nightstand", Verb.Hand):
                await Say("Empty drawer. Even the bedbugs checked out.");
                return true;

            case ("dresser", Verb.Hand):
                if (!State.HasFlag("map_tracing_taken") && !State.HasFlag("found_map"))
                {
                    State.SetFlag("map_tracing_taken");
                    State.GiveItem("map_tracing");
                    await Say("Transparent tracing paper behind the drawer. Three registration marks and an X. It needs the rest of the map.");
                }
                else await Say("Nothing more behind the drawer. I've got the tracing.");
                return true;

            case ("bottle", Verb.Hand):
                await Say("Rotgut. The kind that strips paint and memories.");
                return true;
        }

        return false;
    }
}
