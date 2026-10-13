using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Act 2: the map of Chicago. Micah picks where to look for Eleanor next. Which places are on the map
/// depends on how far the story has gone (see <see cref="OnRefresh"/>).
/// </summary>
public partial class ChicagoMap : Room
{
    private static readonly Rect2 CaptionRect = new(56, 234, 368, 24);
    private Control _captionBox = null!;
    private Label _caption = null!;

    /// <summary>The description in the bottom caption strip, or "" when it is hidden.</summary>
    public string CaptionText => _captionBox.Visible ? _caption.Text : "";

    public override void _Ready()
    {
        base._Ready();
        // a parchment strip at the foot of the map: hovering a place reads its description, no click needed
        _captionBox = new Panel
        {
            Position = CaptionRect.Position,
            Size = CaptionRect.Size,
            ZIndex = 20,
            Visible = false,
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _captionBox.AddThemeStyleboxOverride("panel", new StyleBoxFlat
        {
            BgColor = new Color("ece0bc"),
            BorderColor = new Color("4a3420"),
            BorderWidthLeft = 1, BorderWidthTop = 1, BorderWidthRight = 1, BorderWidthBottom = 1,
        });
        _caption = new Label
        {
            Position = new Vector2(4, 1),
            Size = CaptionRect.Size - new Vector2(8, 2),
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Center,
            VerticalAlignment = VerticalAlignment.Center,
            LabelSettings = new LabelSettings { Font = Hud.Font, FontSize = 8, FontColor = new Color("3a2a1c"), LineSpacing = 0 },
            MouseFilter = Control.MouseFilterEnum.Ignore,
        };
        _captionBox.AddChild(_caption);
        AddChild(_captionBox);
    }

    public override void _Process(double delta) => UpdateCaption(Game.Hud.MousePos);

    /// <summary>Shows the description of the place under <paramref name="mouse"/>, if any.</summary>
    public void UpdateCaption(Vector2 mouse)
    {
        var hud = Game.Hud;
        var spot = Game.Busy || hud.Wheel.IsOpen || hud.InventoryOpen ? null : HotspotAt(mouse);
        _captionBox.Visible = spot != null && spot.LookText != "";
        if (spot != null) _caption.Text = spot.LookText;
    }

    // on the map a left click goes there; looking is what hovering is for
    public override Verb? LeftClickVerb(Hotspot h) => Verb.Walk;

    public override async Task OnEnter(string entry)
    {
        State.SetFlag("on_map");
        if (State.HasFlag("map_seen")) return;
        State.SetFlag("map_seen");
        await Game.Run(() => Say("I have to find her again."));
    }

    // nobody walks on a map
    public override Vector2 ClampWalkTarget(Vector2 target) => Player.Position;

    private bool ClubOut => State.HasFlag("club_out");
    private bool NunThreatened => State.HasFlag("nun_threatened");
    private bool HarringtonDone => State.HasFlag("harrington_done");
    private bool HarringtonLocated => State.HasFlag("harrington_located");

    /// <summary>Investigation leads close as the hunt narrows; the office stays available for the ring.</summary>
    private bool Shows(string id) => id switch
    {
        "library" => !NunThreatened,
        "office" => true,
        "church" => true,
        "club" => State.HasFlag("club_unlocked") && (!NunThreatened || HarringtonDone),
        "convent" => State.HasFlag("caleb_club") && !NunThreatened,
        // after Agatha talks, the Tribune morgue has to give up the old man's address before his office is a place
        "tribune" => NunThreatened && !HarringtonLocated,
        "harrington" => NunThreatened && HarringtonLocated && !HarringtonDone,
        "hotel" => State.HasFlag("recover_hotel") && !State.HasItem("card") && !State.HasItem("brass_box") && !ClubOut,
        _ => false,
    };

    private static readonly (string id, string node)[] Places =
    {
        ("library", "Library"), ("church", "Church"), ("office", "Office"),
        ("club", "Club"), ("convent", "Convent"), ("tribune", "Tribune"), ("harrington", "Harrington"),
        ("hotel", "Hotel"),
    };

    protected override void OnRefresh()
    {
        foreach (var (id, node) in Places)
        {
            bool on = Shows(id);
            if (GetNodeOrNull<CanvasItem>($"Markers/{node}") is { } marker) marker.Visible = on;
            if (FindHotspot(id) is { } spot) spot.Visible = on;
        }
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (verb == Verb.UseItem)
        {
            await Say("I'd rather not leave anything on this map. It goes where I go.");
            return true;
        }
        if (verb is Verb.Kick or Verb.Talk)
        {
            await Say(verb == Verb.Kick ? "Kicking Chicago. Half the city would line up for a turn." : "Chicago never listened to me before.");
            return true;
        }
        if (verb == Verb.Look) return false;
        switch (target.Id)
        {
            case "library" when State.HasFlag("library_banned"):
                await Say("Better not show my face there for the time being.");
                return true;
            case "library":
                await Game.ChangeRoom("library", "start");
                return true;
            case "hotel":
                await Say("I left room 507 without its clues. The staff entrance is still there.");
                await Game.ChangeRoom("lobby", "eleanor_room");
                return true;

            case "church" when !ClubOut:
                await Say("Caleb's sermons can wait. Coming there was a mistake once already.");
                return true;
            case "church":
                await Game.ChangeRoom("church_interior", "map");
                return true;

            case "office":
                await Game.ChangeRoom("office", "door");
                return true;

            case "club" when ClubOut && !HarringtonDone:
                await Say("No use returning there now.");
                return true;
            case "club" when HarringtonDone:
                // the invitation, the mask and the cloak: tonight Micah goes in as one of them, through the vestibule
                State.SetFlag("masked");
                State.SetFlag("on_map", false);
                await Game.ChangeRoom("club_vestibule", "start");
                return true;
            case "club":
                State.SetFlag("on_map", false);
                await Game.ChangeRoom("club_hall", "from_street");
                return true;

            case "convent":
                await Game.ChangeRoom("convent_corridor", "start");
                return true;
            case "tribune":
                await Game.ChangeRoom("newspaper_morgue", "start");
                return true;
            case "harrington":
                await Game.ChangeRoom("harrington_road", "start");
                return true;
        }
        return false;
    }
}
