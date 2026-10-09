using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

public partial class Street : Room
{
    private static readonly Texture2D DayBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_day.png");
    private static readonly Texture2D NightBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_night.png");

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is not { } background) return;
        background.Texture = State.HasFlag("is_night") || !State.HasFlag("is_day") ? NightBackground : DayBackground;
    }

    // The hub is open, but each door only matters once the case has pointed Micah at it.
    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (verb is not (Verb.Walk or Verb.Hand)) return false;
        switch (target.Id)
        {
            case "club_door" when !State.HasFlag("club_lead"):
                await Say("No sign, no knob on this side. A door for people who already know what's behind it.");
                return true;
            case "hotel_door" when !State.HasItem("key"):
                await Say("The doorman took one look at my coat and decided I was weather. I'd need a room key.");
                return true;
            case "road_out" when !State.HasItem("map") && !State.HasFlag("found_evidence"):
                await Say("Nothing out past the city limits but cornfields and men who went for a drive. Not yet.");
                return true;
        }
        return false;
    }
}
