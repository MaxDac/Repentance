using Xunit;

namespace Repentance.Tests;

/// <summary>
/// It rains on 1927 Chicago, harder as the story goes on: every exterior and every room with a window draws a Rain
/// node (which also drives the rain ambience), except the rooms listed here with their reason.
/// </summary>
public class RainTests
{
    /// <summary>Rooms with no rain, and why.</summary>
    private static readonly Dictionary<string, string> Dry = new()
    {
        ["attic"] = "present day, in daylight",
        ["bedroom"] = "present day, a clear starry night in the window",
        ["chicago_map"] = "a paper map, not a place",
        ["club_backstage"] = "no window",
        ["club_hall"] = "no window",
        ["club_lounge"] = "no window",
        ["club_stage"] = "no window",
        ["club_vestibule"] = "no window",
        ["hotel_linen"] = "no window",
        ["library"] = "the one clear, sunny midday: sunlight through the window",
        ["mansion_cellar"] = "underground; the stair only opens into the house",
        ["mansion_kitchen"] = "no window",
        ["newspaper_morgue"] = "no window; the door's glass opens on the corridor",
        ["rose_house"] = "the rain stops on Rose's street; Micah remarks on it",
        ["speakeasy"] = "underground, no window",
    };

    private static readonly Lazy<string> Root = new(() =>
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "project.godot"))) return dir.FullName;
        throw new InvalidOperationException("project.godot not found above the test binaries");
    });

    private static IEnumerable<string> RoomScenes() =>
        Directory.GetFiles(Path.Combine(Root.Value, "scenes", "rooms"), "*.tscn");

    private static bool HasRain(string scene) => File.ReadAllText(scene).Contains("res://scripts/Core/Rain.cs");

    [Fact]
    public void EveryExteriorAndWindowRains()
    {
        var missing = RoomScenes().Where(s => !Dry.ContainsKey(Path.GetFileNameWithoutExtension(s)) && !HasRain(s))
            .Select(Path.GetFileNameWithoutExtension).ToList();
        Assert.True(missing.Count == 0, $"rooms without a Rain node: {string.Join(", ", missing)}");
    }

    [Fact]
    public void DryRoomsStayDryAndExist()
    {
        var scenes = RoomScenes().ToDictionary(s => Path.GetFileNameWithoutExtension(s)!);
        foreach (var (room, reason) in Dry)
        {
            Assert.False(string.IsNullOrWhiteSpace(reason), $"{room} needs a reason to stay dry");
            Assert.True(scenes.ContainsKey(room), $"{room} is listed as dry but has no scene");
            Assert.False(HasRain(scenes[room]), $"{room} is listed as dry but draws rain");
        }
    }

    [Fact]
    public void RainBuildsToADownpour()
    {
        var acts = Enumerable.Range(1, 3).Select(RainWeather.ForAct).ToList();
        Assert.Equal(new RainWeather(1f, 1f, 0, 0f), acts[0]);
        for (int i = 1; i < acts.Count; i++)
        {
            Assert.True(acts[i].Density > acts[i - 1].Density, $"act {i + 1} rains denser");
            Assert.True(acts[i].Speed > acts[i - 1].Speed, $"act {i + 1} rains faster");
            Assert.True(acts[i].ExtraLength >= acts[i - 1].ExtraLength, $"act {i + 1} streaks are no shorter");
            Assert.True(acts[i].VolumeDb > acts[i - 1].VolumeDb, $"act {i + 1} rains louder");
        }
        Assert.Equal(acts[2], RainWeather.ForAct(7));
        Assert.Equal(acts[0], RainWeather.ForAct(0));
    }
}
