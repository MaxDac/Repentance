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

    public override async Task OnEnter(string entry)
    {
        if (entry == "thrown_out")
        {
            await Game.Run(ThrownOut);
            return;
        }
        if (State.HasFlag("thought_street")) return;
        State.SetFlag("thought_street");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("State Street. Wet pavement, headlamps hissing past, a newsboy selling tomorrow's trouble. Nobody out here has seen her either.");
        });
    }

    /// <summary>Act 2: Bruno dumps Micah on the pavement outside the Club. He thinks about Rose and Tommy, then chooses.</summary>
    private async Task ThrownOut()
    {
        Player.SetPose("micah_supine");
        await Wait(1.2);
        await Think("The pavement on Hubbard Street is cold under my back, and it doesn't ask questions. I like that in a pavement.");
        await Think("What am I doing, lying in the gutter for a woman I met four days ago?");
        await Think("I have a wife. On paper, anyway. And a boy who's eleven now, if I've counted right. Tommy.");
        await Think("I walked out on them because the bottle was easier to talk to. Now I walk into the night for a stranger.");
        await Think("At the library I thanked God Rose wasn't at her desk. She's been in my head every minute since.");
        await Think("Maybe that's the joke. Maybe it's easier to save somebody you don't owe anything to.");
        if (!await Player.PlayPose("micah_recover")) return;
        Player.SetPose(null);
        Player.Face(Facing.Down);
        await Wait(0.5);
        await Talk("street_choice");
        if (State.HasFlag("go_rose"))
            await Game.ChangeRoom("rose_house", "start");
        else
            await Game.ChangeRoom("chicago_map", "start");
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
            case "club_door" when State.HasFlag("masked") && !State.HasFlag("vestibule_passed"):
                // the rite night goes in by the vestibule, sealed summons and all; no slipping round the side
                await Say("Through the front tonight, with the procession.");
                return true;
            case "hotel_door" when !State.HasItem("key"):
                await Say("The doorman took one look at my coat and decided I was weather. I'd need a room key.");
                return true;
            case "road_out":
                await Say("Nothing out past the city limits but cornfields and men who went for a drive. Not yet.");
                return true;
        }
        return false;
    }
}
