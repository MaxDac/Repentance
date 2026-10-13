using System.Linq;
using Xunit;

namespace Repentance.Tests;

public class PuzzleTests
{
    [Fact]
    public void LiftMazeConnectsEveryShaftAndTakesARealRoute()
    {
        foreach (var cell in LiftMaze.Cells())
            Assert.NotNull(LiftMaze.Route(LiftMaze.Start, cell));
        var route = LiftMaze.Route(LiftMaze.Start, LiftMaze.Target)!;
        Assert.True(route.Count >= 20, $"route is only {route.Count} moves");
        var p = LiftMaze.Start;
        foreach (var step in route)
        {
            var (dx, dy) = LiftMaze.Step(step);
            Assert.True(LiftMaze.CanMove(p, dx, dy));
            p = LiftMaze.Move(p, dx, dy);
        }
        Assert.True(LiftMaze.Solved(p));
        Assert.Equal("5th floor: linen room by 507", LiftMaze.Destination(p));
    }

    [Fact]
    public void LiftMazeHasWallsDecoysAndDeadEnds()
    {
        Assert.False(LiftMaze.CanMove(LiftMaze.Start, -1, 0));
        Assert.False(LiftMaze.CanMove(LiftMaze.Start, 0, 1));
        Assert.False(LiftMaze.CanMove(LiftMaze.Start, 1, 1));
        Assert.Equal(LiftMaze.Start, LiftMaze.Move(LiftMaze.Start, 0, 1));
        foreach (var decoy in LiftMaze.Decoys)
        {
            Assert.True(LiftMaze.IsLinen(decoy));
            Assert.False(LiftMaze.Solved(decoy));
            Assert.NotEqual(LiftMaze.Destination(LiftMaze.Target), LiftMaze.Destination(decoy));
        }
        int deadEnds = LiftMaze.Cells().Count(c =>
            new[] { (0, -1), (0, 1), (-1, 0), (1, 0) }.Count(d => LiftMaze.CanMove(c, d.Item1, d.Item2)) == 1);
        Assert.True(deadEnds >= 6, $"only {deadEnds} dead ends");
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
        Assert.Equal(3, PuzzleRules.SafeTumblers(directions, numbers));
        Assert.Equal(1, PuzzleRules.SafeTumblers(directions, new[] { 12, 30, 7 }));
        Assert.Equal(0, PuzzleRules.SafeTumblers(new[] { 1, 1, 0 }, numbers));
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
    public void AlarmHasOneSafePlanIncludingCutWireDecoys()
    {
        int solved = 0;
        for (int a = 0; a < 4; a++)
            for (int b = 0; b < 4; b++)
                for (int c = 0; c < 4; c++)
                    if (PuzzleRules.Bell(new[] { a, b, c })) solved++;
        Assert.Equal(1, solved);
        Assert.True(PuzzleRules.Bell(new[] { 0, 1, 2 }));
        Assert.False(PuzzleRules.Bell(new[] { 0, 1 }));
        Assert.False(PuzzleRules.Bell(new[] { 0, 1, 2, 3 }));
    }

    [Fact]
    public void RecipesAreSymmetricAndCipherRequiresAllPrerequisites()
    {
        Assert.True(PuzzleRules.Pair("cloth", "mirror_waxed", "cloth", "mirror_waxed"));
        Assert.True(PuzzleRules.Pair("mirror_waxed", "cloth", "cloth", "mirror_waxed"));
        Assert.False(PuzzleRules.Pair("cloth", "mirror", "cloth", "mirror_waxed"));
        Assert.True(PuzzleRules.Pair("audit_folder", "audit_tracing", "audit_folder", "audit_tracing"));
        Assert.True(PuzzleRules.Pair("audit_tracing", "audit_folder", "audit_folder", "audit_tracing"));
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
    public void LegacyHotelRemainsReachable()
    {
        var hotel = new SaveData { Room = "eleanor_room", Flags = new() { "safe_open" } };
        PuzzleMigration.Normalize(hotel);
        Assert.Contains("lift_routed", hotel.Flags);
        Assert.Contains("safe_open", hotel.Flags);
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

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void ActThreeMigrationRunsIndependentlyOfOriginalPuzzleMarker(bool originalStamped)
    {
        var save = new SaveData
        {
            Room = "mansion_study", StoryAct = 3,
            Flags = new() { "door_open", "drawer_right_open", "closet_open", Endings.TookDocuments },
            Inventory = new() { "documents" },
        };
        if (originalStamped) save.Flags.Add(PuzzleMigration.SchemaFlag);
        var originalVersion = save.Version;
        PuzzleMigration.Normalize(save);
        Assert.Contains(PuzzleMigration.Act3SchemaFlag, save.Flags);
        Assert.Contains("bell_wedged", save.Flags);
        Assert.Contains("audit_identified", save.Flags);
        Assert.Contains("audit_folder_taken", save.Flags);
        Assert.DoesNotContain("study_drawer_right_open", save.Flags);
        Assert.DoesNotContain("study_closet_open", save.Flags);
        Assert.Equal(originalVersion, save.Version);
        var serialized = SaveSerializer.Serialize(save);
        PuzzleMigration.Normalize(save);
        Assert.Equal(serialized, SaveSerializer.Serialize(save));
    }

    [Theory]
    [InlineData("documents")]
    [InlineData("stash_documents")]
    public void LegacyDocumentOwnershipStillCountsAsEvidence(string itemOrFlag)
    {
        var save = new SaveData { Room = "attic", StoryAct = 3 };
        if (itemOrFlag.StartsWith("stash_")) save.Flags.Add(itemOrFlag);
        else save.Inventory.Add(itemOrFlag);
        PuzzleMigration.Normalize(save);
        Assert.Contains(Endings.TookDocuments, save.Flags);
        Assert.Contains("audit_identified", save.Flags);
    }

    [Fact]
    public void MovingBinAndOpeningDrawerNeverGrandfatherActThreeSolutions()
    {
        var save = new SaveData
        {
            Room = "mansion_exterior", StoryAct = 3,
            Flags = new() { PuzzleMigration.SchemaFlag, "bin_moved", "alarm_noticed", "drawer_right_open", "closet_open" },
        };
        PuzzleMigration.Normalize(save);
        Assert.DoesNotContain("bell_wedged", save.Flags);
        Assert.DoesNotContain(Endings.TookDocuments, save.Flags);
        Assert.DoesNotContain("audit_identified", save.Flags);
        Assert.DoesNotContain("study_drawer_right_open", save.Flags);
        Assert.DoesNotContain("study_closet_open", save.Flags);
    }

    [Fact]
    public void StampedPartialActThreeSaveStaysUnsolvedAfterReload()
    {
        var save = new SaveData
        {
            Room = "mansion_study", StoryAct = 3,
            Flags = new() { PuzzleMigration.SchemaFlag, PuzzleMigration.Act3SchemaFlag, "study_drawer_right_open", "audit_folder_taken" },
            Inventory = new() { "audit_folder", "audit_tracing" },
        };
        var reloaded = SaveSerializer.TryDeserialize(SaveSerializer.Serialize(save))!;
        PuzzleMigration.Normalize(reloaded);
        Assert.DoesNotContain(Endings.TookDocuments, reloaded.Flags);
        Assert.DoesNotContain("audit_identified", reloaded.Flags);
        Assert.Equal(5, Endings.Resolve(reloaded.Flags.Contains));
        reloaded.Flags.Add(Endings.EleanorConvinced);
        Assert.Equal(4, Endings.Resolve(reloaded.Flags.Contains));
    }

    [Fact]
    public void RemovedTemporaryRouteSavesRemainIncompatibleWithMain()
    {
        var old = new SaveData
        {
            Version = 2, Room = "outskirts", StoryAct = 3,
            Flags = new() { PuzzleMigration.SchemaFlag, "burial_surveyed" },
            Inventory = new() { "map", "evidence", "map_base", "map_tracing" },
        };
        Assert.Null(SaveSerializer.TryDeserialize(SaveSerializer.Serialize(old)));
    }

    [Fact]
    public void LegacyStudyStartsClosedWithoutInheritingOfficeOrHotelDrawers()
    {
        var save = new SaveData
        {
            Room = "mansion_study", StoryAct = 3,
            Flags = new() { "seen_mansion_study", "drawer_left_open", "drawer_right_open", "closet_open" },
        };
        PuzzleMigration.Normalize(save);
        Assert.DoesNotContain("study_drawer_left_open", save.Flags);
        Assert.DoesNotContain("study_drawer_right_open", save.Flags);
        Assert.DoesNotContain("study_closet_open", save.Flags);
        Assert.DoesNotContain("audit_tracing_taken", save.Flags);
        Assert.DoesNotContain(Endings.TookDocuments, save.Flags);
    }
}
