using Xunit;

namespace Repentance.Tests;

public class NotesTests
{
    private static Func<string, bool> Has(IEnumerable<string> flags) => new HashSet<string>(flags).Contains;

    [Fact]
    public void Ids_AreUniqueAndEveryNoteHasContent()
    {
        Assert.Equal(Notes.All.Count, Notes.All.Select(n => n.Id).Distinct().Count());
        foreach (var n in Notes.All)
        {
            Assert.NotEmpty(n.Unlock);
            Assert.NotEmpty(n.Lines);
            Assert.False(string.IsNullOrWhiteSpace(n.Title));
            Assert.Contains(n.Lines, l => l.Flag == null);
        }
    }

    [Fact]
    public void Notepad_IsAnInventoryItem() => Assert.True(Items.All.ContainsKey(Notes.ItemId));

    [Fact]
    public void Triquetra_CarriesTheMirrorSketch() =>
        Assert.StartsWith("res://assets/art/", Notes.Get("triquetra")!.Sketch);

    [Fact]
    public void NothingIsKnown_WithoutFlags()
    {
        Assert.Empty(Notes.Visible(_ => false));
        Assert.False(Notes.Known("eleanor", _ => false));
        Assert.False(Notes.Known("nope", _ => true));
    }

    [Fact]
    public void ConditionalLines_AppearOnlyWithTheirFlag()
    {
        var safe = Notes.Get("safe_riddle")!;
        var before = Notes.Lines(safe, Has(new[] { "took_combination" })).ToList();
        var after = Notes.Lines(safe, Has(new[] { "took_combination", "safe_open" })).ToList();
        Assert.True(after.Count > before.Count);
        Assert.Contains(after, l => l.Contains("12"));
    }

    [Fact]
    public void BackWay_RoomNumbers_SpanTheLiftMaze()
    {
        var text = string.Join(" ", Notes.Get("service_lift")!.Lines.Select(l => l.Text));
        Assert.Contains("501 is by the stairs", text);
        Assert.Contains($"{500 + LiftMaze.Width} by the fire escape", text);
    }

    [Fact]
    public void HarringtonRoad_OfficeWindowIsDark()
    {
        var note = Notes.Get("harrington_road")!;
        var text = string.Join(" ", Notes.Lines(note, Has(new[] { "seen_harrington_road" })));
        Assert.Contains("The office window is dark.", text);
        Assert.DoesNotContain("is lit", text);
    }

    [Fact]
    public void ClubCard_IsForThursdayNight()
    {
        var text = string.Join(" ", Notes.Get("crests")!.Lines.Select(l => l.Text));
        Assert.Contains("The Club. Thursday, at the turning of the night.", text);
        Assert.DoesNotContain("Saturday", text);
        Assert.DoesNotContain("Sunday", text);
    }

    [Theory]
    [InlineData("bedroom")]
    [InlineData("office")]
    [InlineData("nowhere")]
    public void DebugStart_BeforeTheCase_HasNoNotes(string room) => Assert.Empty(Notes.DebugStartFlags(room));

    [Theory]
    [InlineData("lobby", "eleanor")]
    [InlineData("eleanor_room", "night_bolt")]
    [InlineData("library", "triquetra")]
    [InlineData("chicago_map", "taken")]
    [InlineData("harrington_office", "harrington_road")]
    [InlineData("mansion_cellar", "cellar")]
    public void DebugStart_KnowsWhatMicahWouldKnow(string room, string note) =>
        Assert.True(Notes.Known(note, Has(Notes.DebugStartFlags(room))));

    [Fact]
    public void DebugStart_DoesNotKnowTheFuture() =>
        Assert.False(Notes.Known("triquetra", Has(Notes.DebugStartFlags("convent_cell"))));

    [Fact]
    public void DebugStartFlags_Accumulate()
    {
        var seen = new HashSet<string>();
        foreach (var room in Notes.DebugRooms.Distinct())
        {
            var flags = Notes.DebugStartFlags(room);
            Assert.True(seen.IsSubsetOf(flags) || room == "office", $"{room} dropped earlier flags");
            seen.UnionWith(flags);
        }
        Assert.Contains("cellar_lit", seen);
    }
}
