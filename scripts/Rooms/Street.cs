using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

public partial class Street : Room
{
    private static readonly Texture2D DayBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_day.png");
    private static readonly Texture2D NightBackground = GD.Load<Texture2D>("res://assets/art/rooms/street_night.png");
    private static readonly Texture2D DayFront = GD.Load<Texture2D>("res://assets/art/rooms/street_day_fg.png");
    private static readonly Texture2D NightFront = GD.Load<Texture2D>("res://assets/art/rooms/street_night_fg.png");

    protected override void OnRefresh()
    {
        var night = State.HasFlag("is_night") || !State.HasFlag("is_day");
        if (GetNodeOrNull<Sprite2D>("Background") is { } background) background.Texture = night ? NightBackground : DayBackground;
        // Lamp posts, hydrant and the parked car stand at the kerb, in front of anyone on the sidewalk.
        if (GetNodeOrNull<Sprite2D>("World/StreetFront") is { } front) front.Texture = night ? NightFront : DayFront;
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
