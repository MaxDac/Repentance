using Xunit;

namespace Repentance.Tests;

public class PuzzleTests
{
    [Fact]
    public void LiftHasExactlyOneRouteTo507()
    {
        int solved = 0;
        for (int a = 0; a < 2; a++)
            for (int b = 0; b < 2; b++)
                for (int c = 0; c < 2; c++)
                {
                    var route = new[] { a, b, c };
                    if (PuzzleRules.Lift(route)) solved++;
                    Assert.Equal(PuzzleRules.Lift(route), PuzzleRules.LiftDestination(route) == "Room 507");
                }
        Assert.Equal(1, solved);
        Assert.False(PuzzleRules.Lift(new[] { 1, 0 }));
    }

    [Fact]
    public void SafeRequiresEveryDirectionAndNumber()
    {
        var directions = new[] { 0, 1, 0 };
        var numbers = new[] { 12, 31, 7 };
        Assert.True(PuzzleRules.Safe(directions, numbers));
        for (int row = 0; row < 3; row++)
        {
            for (int value = 0; value < 40; value++)
            {
                var attempt = (int[])numbers.Clone();
                attempt[row] = value;
                Assert.Equal(value == numbers[row], PuzzleRules.Safe(directions, attempt));
            }
            var wrongDirection = (int[])directions.Clone();
            wrongDirection[row] = 1 - wrongDirection[row];
            Assert.False(PuzzleRules.Safe(wrongDirection, numbers));
        }
        Assert.False(PuzzleRules.Safe(new[] { 0, 1 }, numbers));
        Assert.False(PuzzleRules.Safe(directions, new[] { 12, 31, 7, 0 }));
    }

    [Fact]
    public void CrestsAndCipherEachHaveOneOrderedSolution()
    {
        int crests = 0, cipher = 0;
        for (int a = 0; a < 3; a++)
            for (int b = 0; b < 3; b++)
                for (int c = 0; c < 3; c++)
                {
                    if (PuzzleRules.Crests(new[] { a, b, c })) crests++;
                    if (PuzzleRules.Cipher(new[] { a, b, c })) cipher++;
                }
        Assert.Equal(1, crests);
        Assert.Equal(1, cipher);
        Assert.True(PuzzleRules.Crests(new[] { 2, 0, 1 }));
        Assert.True(PuzzleRules.Cipher(new[] { 1, 2, 0 }));
    }

    [Fact]
    public void CatalogueRequiresBothMotifAndTitle()
    {
        for (int motif = -1; motif < 3; motif++)
            for (int entry = 0; entry < 3; entry++)
                Assert.Equal(motif == 1 && entry == 2, PuzzleRules.Catalogue(motif, entry));
    }

    [Fact]
    public void AlignmentHasExactlyOneTransformMatchingAllThreeMarks()
    {
        var solutions = new List<(int Rotation, int X, int Y)>();
        for (int turn = 0; turn < 4; turn++)
            for (int x = 0; x <= 10; x++)
                for (int y = 0; y <= 10; y++)
                    if (PuzzleRules.Alignment(turn, x, y)) solutions.Add((turn, x, y));
        Assert.Equal((1, 6, 3), Assert.Single(solutions));
        Assert.False(PuzzleRules.Alignment(0, 6, 3));
        Assert.False(PuzzleRules.Alignment(1, -1, 3));
        Assert.False(PuzzleRules.Alignment(4, 6, 3));
        Assert.Throws<ArgumentOutOfRangeException>(() => PuzzleRules.Transform(new GridPoint(), 4, 0, 0));
    }

    [Fact]
    public void SurveyHasOneTileMeetingBothMeasuredConstraints()
    {
        var solutions = new List<GridPoint>();
        for (int x = 0; x <= 10; x++)
            for (int y = 0; y <= 10; y++)
                if (PuzzleRules.Survey(x, y)) solutions.Add(new GridPoint(x, y));
        Assert.Equal(new GridPoint(8, 8), Assert.Single(solutions));
        Assert.False(PuzzleRules.Survey(8, 9));
        Assert.False(PuzzleRules.Survey(7, 8));
        Assert.False(PuzzleRules.Survey(11, 8));
    }

    [Fact]
    public void RecipesAreSymmetricAndCipherRequiresAllPrerequisites()
    {
        Assert.True(PuzzleRules.Pair("cloth", "mirror_waxed", "cloth", "mirror_waxed"));
        Assert.True(PuzzleRules.Pair("mirror_waxed", "cloth", "cloth", "mirror_waxed"));
        Assert.False(PuzzleRules.Pair("cloth", "mirror", "cloth", "mirror_waxed"));
        for (int mask = 0; mask < 8; mask++)
            Assert.Equal(mask == 7, PuzzleRules.CipherReady((mask & 1) != 0, (mask & 2) != 0, (mask & 4) != 0));
    }

    [Fact]
    public void StampedNewSaveDoesNotGrandfatherUnsolvedCipher()
    {
        var save = new SaveData { Room = "office", Flags = new() { PuzzleMigration.SchemaFlag, "read_book" }, Inventory = new() { "book", "card", "mirror" } };
        PuzzleMigration.Normalize(save);
        var reloaded = SaveSerializer.TryDeserialize(SaveSerializer.Serialize(save))!;
        PuzzleMigration.Normalize(reloaded);
        Assert.DoesNotContain("club_unlocked", reloaded.Flags);
        Assert.DoesNotContain("address", reloaded.Inventory);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void LegacyBookDiscoveryAndMirrorAreGrandfatheredIdempotently(bool stashed)
    {
        var save = new SaveData { Room = stashed ? "attic" : "office", StoryAct = 2, Flags = new() { "read_book", "secret_open" } };
        if (stashed)
        {
            save.Inventory.Add("journal");
            save.Flags.AddRange(new[] { "stash_book", "stash_mirror" });
        }
        else save.Inventory.AddRange(new[] { "book", "mirror" });
        PuzzleMigration.Normalize(save);
        Assert.Contains(PuzzleMigration.SchemaFlag, save.Flags);
        Assert.Contains("club_unlocked", save.Flags);
        Assert.Contains("got_mirror", save.Flags);
        Assert.Contains("took_mirror", save.Flags);
        Assert.Contains("harrington_closet_open", save.Flags);
        if (stashed) Assert.Contains("stash_address", save.Flags);
        else Assert.Contains("address", save.Inventory);
        string normalized = SaveSerializer.Serialize(save);
        PuzzleMigration.Normalize(save);
        Assert.Equal(normalized, SaveSerializer.Serialize(save));
    }

    [Fact]
    public void LegacyBribeAndHotelClosetAloneDoNotSolveNewPuzzles()
    {
        var save = new SaveData { Room = "lobby", Flags = new() { "staff_elevator", "knows_lantern", "closet_open" } };
        PuzzleMigration.Normalize(save);
        Assert.DoesNotContain("lift_routed", save.Flags);
        Assert.DoesNotContain("harrington_closet_open", save.Flags);
        Assert.DoesNotContain("ladder_freed", save.Flags);
    }

    [Fact]
    public void LegacyHotelAndCompletedEndingRemainReachable()
    {
        var hotel = new SaveData { Room = "eleanor_room", Flags = new() { "safe_open" } };
        PuzzleMigration.Normalize(hotel);
        Assert.Contains("lift_routed", hotel.Flags);
        Assert.Contains("safe_open", hotel.Flags);
        var ending = new SaveData { Room = "outskirts", Inventory = new() { "map", "evidence" } };
        PuzzleMigration.Normalize(ending);
        Assert.Contains("found_map", ending.Flags);
        Assert.Contains("burial_surveyed", ending.Flags);
    }

    [Fact]
    public void LegacyActTwoWithoutCardGetsReachableHotelRecovery()
    {
        var save = new SaveData
        {
            Room = "chicago_map", StoryAct = 2,
            Flags = new() { "on_map", "got_mirror", "staff_elevator" },
            Inventory = new() { "mirror", "lockpick" },
        };
        PuzzleMigration.Normalize(save);
        Assert.Contains("recover_hotel", save.Flags);
        Assert.Contains("staff_elevator", save.Flags);
        Assert.DoesNotContain("club_unlocked", save.Flags);
        Assert.DoesNotContain("card", save.Inventory);
        Assert.DoesNotContain("brass_box", save.Inventory);
    }

    [Theory]
    [InlineData("speakeasy")]
    [InlineData("convent_cell")]
    [InlineData("motel_night")]
    public void LegacyActOneAlreadyPastHotelCarriesRecoveryIntoActTwo(string room)
    {
        var save = new SaveData { Room = room, StoryAct = 1, Inventory = new() { "lockpick" } };
        PuzzleMigration.Normalize(save);
        Assert.Contains("recover_hotel", save.Flags);
        Assert.Contains("staff_elevator", save.Flags);
    }
}
