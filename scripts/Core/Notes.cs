using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

/// <summary>One line of a notepad page; shown once <paramref name="Flag"/> is set (always when null).</summary>
public sealed record NoteLine(string Text, string? Flag = null);

/// <summary>A notepad page. It is written as soon as any of the <paramref name="Unlock"/> flags is set.</summary>
public sealed record NoteDef(string Id, string Title, string[] Unlock, NoteLine[] Lines, string? Sketch = null);

/// <summary>
/// Micah's notepad: what he has learned on the case, derived purely from story flags (so saves need no extra data).
/// Pages are in story order; <see cref="DebugStartFlags"/> fills in everything learned before a debug start room.
/// </summary>
public static class Notes
{
    public const string ItemId = "notepad";

    private static NoteDef N(string id, string title, string unlock, params NoteLine[] lines) =>
        new(id, title, unlock.Split(','), lines);

    private static NoteLine L(string text, string? flag = null) => new(text, flag);

    public static readonly IReadOnlyList<NoteDef> All = new[]
    {
        // ---------------------------------------------------------------- Act 1
        N("case", "The case", "teddy_briefed",
            L("Client: Theodore Harrington III."),
            L("Wife Eleanor gone since Tuesday, after dinner at the Aurelian Hotel. Her coat went with her."),
            L("No police. Twenty a day plus expenses.")),
        N("eleanor", "Eleanor Harrington", "teddy_briefed",
            L("From Teddy's photograph: pretty, poised, looking at the camera like it owed her money."),
            L("Sketched her here too - good enough to show around if the picture's not to hand.")),
        N("bellboy", "The bellboy", "knows_lantern",
            L("Tuesday, late: out through the hotel service door."),
            L("A big fella either side of her. Broken nose, cheap suit, expensive cigar."),
            L("Escorted, not dragged. Car with no lights, gone down the alley.")),
        N("service_lift", "The back way", "staff_elevator",
            L("Staff door by the potted palm, then the service lift."),
            L("Fifth-floor linen room, next door to 507."),
            L("501 is by the stairs, west. 509 by the fire escape, east."),
            L("Somebody turned her room over before me.", "seen_eleanor_room")),
        N("night_bolt", "Room 507", "seen_hotel_linen",
            L("Linen room door to 507: night bolt, shot from the corridor side."),
            L("The transom's open an inch. Something with a hook could reach that bolt.")),
        N("safe_riddle", "The safe", "took_combination",
            L("Slip of paper from her room:"),
            L("Those who sat at His table. The days of the month He was born. The day He rested."),
            L("No directions given."),
            L("Right 12, left 31, right 7. It opened.", "safe_open")),
        new NoteDef("brass_box", "The brass box", new[] { "opened_brass_box", "seen_blue_lantern_front", "club_lead" }, new[]
        {
            L("A perfumed card, blank but for two letters. Her perfume."),
            L("A matchbook: The Blue Lantern, State Street."),
            L("A vial of laundry bluing. She meant to wear a blue flower."),
            L("A Japanese water flower: \"Give me a drink and I'll tell you the word.\""),
        }),
        N("blue_lantern", "The Blue Lantern", "seen_blue_lantern_front",
            L("Rizzo's Flowers on State Street is the front."),
            L("Members get in with a blue carnation in the buttonhole. Nothing else."),
            L("Eleanor's water flower bloomed in Rizzo's bucket: MOONSHINE. The password.", "knows_password"),
            L("Sal on the door wanted a password. Ten dollars did instead.", "sal_bribed"),
            L("Sal on the door wanted a password. Moonshine did it.", "sal_password")),
        N("tony", "Tony", "alley_done",
            L("Tony the bartender sent her to the nuns."),
            L("The convent on the North Side.")),
        N("sister_agatha", "The convent", "nun_talked",
            L("The sister knew my prophet: \"I will shew thee, O man, what is good.\" Micah 6:8."),
            L("She called Eleanor a Jezebel, then bit her tongue."),
            L("Eleanor's cell: the last door at the end of the corridor.")),
        new NoteDef("triquetra", "Behind the mirror", new[] { "got_mirror" }, new[]
        {
            L("Scratched deep into the back of her hand mirror: three loops tied in one knot. No beginning, no end."),
            L("Copied it down. Somebody will know what it means."),
        }, "res://assets/art/ui/triquetra.png"),
        N("eleanor_found", "Eleanor", "eleanor_found",
            L("Found her outside the convent."),
            L("She can't go back. I promised I'd never tell where she went.")),

        // ---------------------------------------------------------------- Act 2
        N("librarian", "The library", "librarian_refused",
            L("The librarian knew the knot on sight and showed me the door."),
            L("Find the book another way. The card catalogue, maybe.")),
        N("rites", "The book", "catalogue_identified",
            L("A. R. Bell, Rites of the Old Isles."),
            L("Shelf C-17, behind locked glass.")),
        N("bell_book", "Rites of the Old Isles", "read_book",
            L("Concealed messages: gentle warmth brings up the ink; a mirror turns the writing back."),
            L("Ornament order: lily first, leaf second, feather last.")),
        N("club_address", "The card", "card_decoded",
            L("Warmed, read in the mirror, put in order, the perfumed card gives up an address:"),
            L("The Club, 18 W. Hubbard.")),
        N("moc", "The Club", "club_out",
            L("The Master of Ceremonies, in his robes: \"She is with us... thanks to your efforts.\""),
            L("Then his brute threw me out on the pavement.")),
        N("caleb_convent", "Caleb", "caleb_club",
            L("Eleanor hid at the convent once. The convent answers to the Church. Caleb might know."),
            L("Performers, he called the women. When the Club is done with them, the sisters take some in."),
            L("Ask at the convent.")),
        N("harrington_senior", "The sister again", "nun_threatened",
            L("I pulled a gun on a nun. My hand was shaking."),
            L("\"She's a performer.\" Go see Harrington senior."),
            L("The Tribune morgue will have where he keeps his office.")),
        N("harrington_building", "The clipping", "mended_clipping,harrington_located",
            L("Torn Tribune clipping, pieced together: \"HARRINGTON BUILDS... Building, LaS\""),
            L("Harrington Building, LaSalle Street, in the Loop.", "harrington_located")),
        N("harrington_road", "Harrington Building", "seen_harrington_road",
            L("Round the back: a watchman with a stick and a telephone inside."),
            L("The fire-escape ladder is up, held by a spring catch. The office window is lit.")),
        N("crests", "The procession", "drawer_right_open",
            L("In the old man's locked drawer, a black card: \"The Club. Saturday, at the turning of the night.\""),
            L("Procession crests, left to right: raven, lion, stag."),
            L("The portrait's key: raven = star, lion = sun, stag = moon.", "portrait_key_seen")),
        N("vestibule", "The vestibule", "seen_vestibule",
            L("\"Present your summons, sealed by the first of the procession.\""),
            L("The first is the raven.", "drawer_right_open")),

        // ---------------------------------------------------------------- Act 3
        N("stage", "The stage", "beaten",
            L("The leader on the stage: \"Are you satisfied, now, mister Jones?\""),
            L("Then Bruno, from behind.")),
        N("mansion", "The mansion", "shot_bartender",
            L("Tony, with a bullet in his shoulder: the old man's place on the Gold Coast."),
            L("Round the back to the kitchen. Booze comes in that way every Thursday."),
            L("Key on the lintel over the kitchen door.")),
        N("alarm", "The alarm", "alarm_noticed",
            L("A wire along the kitchen door frame, up the wall to a red box. A bell."),
            L("Open the door and it rings the house awake. Silence the bell first.")),
        N("cellar", "The kitchen", "seen_mansion_kitchen",
            L("The baize door is bolted from the house side."),
            L("Deliveries have another way up. There's a trapdoor to the cellar."),
            L("Bootleggers' stair: straight up to the bar in the study.", "cellar_lit")),
        N("audit", "The ledger", "audit_tracing_taken",
            L("The auditor's index: BANK above JUDGE, CAPTAIN left of BANK. Line it up on the study desk."),
            L("Signed payment sheets. Insurance, if I live long enough to use it.", "audit_identified")),
    };

    private static readonly Dictionary<string, NoteDef> ById = All.ToDictionary(n => n.Id);

    public static NoteDef? Get(string id) => ById.GetValueOrDefault(id);

    public static bool Unlocked(NoteDef note, Func<string, bool> hasFlag) => note.Unlock.Any(hasFlag);

    public static bool Known(string id, Func<string, bool> hasFlag) => Get(id) is { } n && Unlocked(n, hasFlag);

    /// <summary>The pages written so far, oldest first.</summary>
    public static IReadOnlyList<NoteDef> Visible(Func<string, bool> hasFlag) => All.Where(n => Unlocked(n, hasFlag)).ToList();

    public static IEnumerable<string> Lines(NoteDef note, Func<string, bool> hasFlag) =>
        note.Lines.Where(l => l.Flag == null || hasFlag(l.Flag)).Select(l => l.Text);

    // Story order of the rooms; each row adds the flags learned before its first visit.
    private static readonly (string[] Rooms, string[] Flags)[] DebugRows =
    {
        (new[] { "office" }, Array.Empty<string>()),
        (new[] { "lobby" }, new[] { "teddy_briefed" }),
        (new[] { "hotel_linen" }, new[] { "knows_lantern", "staff_elevator" }),
        (new[] { "eleanor_room" }, new[] { "seen_hotel_linen" }),
        (new[] { "blue_lantern_front" }, new[] { "seen_eleanor_room", "took_combination", "safe_open", "took_brass_box", "opened_brass_box" }),
        (new[] { "speakeasy" }, new[] { "seen_blue_lantern_front" }),
        (new[] { "alley" }, new[] { "sal_passed" }),
        (new[] { "convent_road", "convent_corridor" }, new[] { "alley_done" }),
        (new[] { "convent_cell" }, new[] { "nun_talked" }),
        (new[] { "motel_night", "church_exterior", "church_interior", "chicago_map", "library" }, new[] { "got_mirror", "eleanor_found" }),
        (new[] { "club_hall" }, new[] { "librarian_refused", "catalogue_identified", "read_book", "card_decoded" }),
        (new[] { "street", "rose_house" }, new[] { "club_out" }),
        (new[] { "newspaper_morgue" }, new[] { "caleb_club", "nun_threatened" }),
        (new[] { "harrington_road" }, new[] { "mended_clipping", "harrington_located" }),
        (new[] { "harrington_office" }, new[] { "seen_harrington_road" }),
        (new[] { "club_vestibule" }, new[] { "drawer_right_open", "portrait_key_seen" }),
        (new[] { "club_lounge", "club_stage" }, new[] { "seen_vestibule" }),
        (new[] { "mansion_exterior" }, new[] { "beaten", "shot_bartender" }),
        (new[] { "mansion_kitchen" }, new[] { "alarm_noticed" }),
        (new[] { "mansion_cellar" }, new[] { "seen_mansion_kitchen" }),
        (new[] { "mansion_study", "mansion_bedroom", "outskirts", "prison" }, new[] { "cellar_lit" }),
    };

    /// <summary>Rooms with a debug-start entry, in story order.</summary>
    public static IEnumerable<string> DebugRooms => DebugRows.SelectMany(r => r.Rooms);

    /// <summary>
    /// Flags Micah would have learned before first entering <paramref name="room"/>, so a debug start there has
    /// the matching notepad pages. Unknown rooms (and the present-day attic and bedroom) get none.
    /// </summary>
    public static IReadOnlyList<string> DebugStartFlags(string room)
    {
        var flags = new List<string>();
        foreach (var (rooms, add) in DebugRows)
        {
            flags.AddRange(add);
            if (rooms.Contains(room)) return flags;
        }
        return Array.Empty<string>();
    }
}
