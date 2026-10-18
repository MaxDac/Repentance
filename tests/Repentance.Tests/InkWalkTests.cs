using System.Text.RegularExpressions;
using Story = Ink.Runtime.Story;
using Repentance;
using Xunit;
using Xunit.Abstractions;

namespace Repentance.Tests;

/// <summary>
/// Walks the compiled Ink story exhaustively: every knot the game calls is run, every choice taken, and each
/// conversation started again a few times (as a player clicking Talk again would), under several worlds for the
/// game's external functions (flags/items learned only from the story itself, everything true, and seeded mixes).
/// Fails on any Ink runtime error (such as running out of content: the B1 dead end) and on any choice no world
/// ever offers.
/// </summary>
public class InkWalkTests
{
    private readonly ITestOutputHelper _out;
    public InkWalkTests(ITestOutputHelper output) => _out = output;

    private const int Repeats = 3;
    private const int MaxDepth = 30;
    private const int NodeBudget = 20000;
    private const int RandomWorlds = 24;

    /// <summary>
    /// Choices no world reaches, with the reason. Each is a real dead branch or needs a game state the walk can't
    /// build; keep the list short.
    /// </summary>
    private static readonly Dictionary<string, string> UnreachedChoices = new()
    {
    };

    private static readonly Lazy<string> Root = new(() =>
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "project.godot"))) return dir.FullName;
        throw new InvalidOperationException("project.godot not found above the test binaries");
    });

    private static string InkText => File.ReadAllText(Path.Combine(Root.Value, "dialogue", "repentance.ink"));

    private static readonly Lazy<string> Compiled = new(() =>
    {
        var errors = new List<string>();
        var compiler = new Ink.Compiler(InkText, new Ink.Compiler.Options
        {
            countAllVisits = true,
            errorHandler = (message, type) => { if (type == Ink.ErrorType.Error) errors.Add(message); },
        });
        var story = compiler.Compile();
        if (story == null || errors.Count > 0) throw new InvalidOperationException("ink compile errors:\n" + string.Join("\n", errors));
        return story.ToJson();
    });

    /// <summary>How the game's external functions answer: learned (only what the story itself set), all true, or seeded.</summary>
    private sealed class World
    {
        public required string Name;
        public required Func<string, bool> Flag;
        public required Func<string, bool> Item;
        public int Cash = CashRules.StartingCash;
        public HashSet<string> Flags = new();
        public HashSet<string> Items = new();
        public HashSet<string> Taken = new();

        public World Clone() => new()
        {
            Name = Name, Flag = Flag, Item = Item, Cash = Cash,
            Flags = new HashSet<string>(Flags), Items = new HashSet<string>(Items), Taken = new HashSet<string>(Taken),
        };
    }

    private static IEnumerable<World> Worlds()
    {
        yield return new World { Name = "learned", Flag = _ => false, Item = i => MicahKit.IsPinned(i) };
        yield return new World { Name = "cash in hand", Flag = _ => false, Item = i => MicahKit.IsPinned(i) || i == "dollar" };
        yield return new World { Name = "all-true", Flag = _ => true, Item = _ => true };
        for (int seed = 1; seed <= RandomWorlds; seed++)
        {
            int s = seed;
            yield return new World
            {
                Name = $"seed {s}",
                Flag = f => Bit(f, s),
                Item = i => MicahKit.IsPinned(i) || Bit(i, s + 1000),
                Cash = Bit("cash", s) ? CashRules.StartingCash : 0,
            };
        }
    }

    private static bool Bit(string name, int seed)
    {
        unchecked
        {
            int h = seed * 486187739;
            foreach (char c in name) h = h * 31 + c;
            h ^= h >> 13;
            return (h & 1) == 0;
        }
    }

    private sealed class Walk
    {
        public readonly Story Story = new(Compiled.Value);
        public World World = null!;
        public readonly List<string> Errors = new();
        public readonly HashSet<string> Offered = new();
        public readonly HashSet<string> Shown = new();
        public int Nodes;

        public Walk()
        {
            Story.onError += (message, type) => { if (type == Ink.ErrorType.Error) Errors.Add(message); };
            bool HasFlag(string f) => World.Flags.Contains(f) || World.Flag(f);
            bool HasItem(string i) => World.Items.Contains(i) || (!World.Taken.Contains(i) && World.Item(i));
            Story.BindExternalFunction("has_item", (string id) => HasItem(id), lookaheadSafe: true);
            Story.BindExternalFunction("has_flag", (string f) => HasFlag(f), lookaheadSafe: true);
            Story.BindExternalFunction("knows_note", (string id) => HasItem(Notes.ItemId) && Notes.Known(id, HasFlag), lookaheadSafe: true);
            Story.BindExternalFunction("cash_amount", () => HasItem("dollar") ? World.Cash : 0, lookaheadSafe: true);
            Story.BindExternalFunction("give_item", (string id) => { World.Items.Add(id); World.Taken.Remove(id); });
            Story.BindExternalFunction("take_item", (string id) => { World.Items.Remove(id); World.Taken.Add(id); });
            Story.BindExternalFunction("set_flag", (string f) => { World.Flags.Add(f); });
        }
    }

    private static readonly Lazy<(HashSet<string> Offered, HashSet<string> Shown, List<string> Problems)> Result = new(Explore);

    private static (HashSet<string>, HashSet<string>, List<string>) Explore()
    {
        var scan = InkScan.Parse(InkText);
        var oneShot = OneShotKnotsOf();
        var entries = TalkTargets(scan);
        var offered = new HashSet<string>();
        var shown = new HashSet<string>();
        var problems = new List<string>();
        foreach (var knot in entries)
            foreach (var world in Worlds())
            {
                var walk = new Walk();
                walk.World = world;
                walk.Story.ChoosePathString(knot);
                var seen = new HashSet<string>();
                Visit(walk, knot, oneShot.Contains(knot) ? 0 : Repeats, new List<string>(), seen, problems);
                offered.UnionWith(walk.Offered);
                shown.UnionWith(walk.Shown);
            }
        return (offered, shown, problems);
    }

    private static void Visit(Walk walk, string knot, int repeats, List<string> path, HashSet<string> seen, List<string> problems)
    {
        if (++walk.Nodes > NodeBudget || path.Count > MaxDepth) return;
        var story = walk.Story;
        try
        {
            while (story.canContinue) story.Continue();
        }
        catch (Exception ex)
        {
            walk.Errors.Add(ex.Message);
        }
        if (walk.Errors.Count > 0)
        {
            problems.Add($"{knot} [{walk.World.Name}] after {Describe(path)}: {string.Join("; ", walk.Errors.Distinct())}");
            walk.Errors.Clear();
            return;
        }
        var choices = story.currentChoices.Select(c => c.text).ToList();
        if (choices.Count == 0)
        {
            if (repeats <= 0) return;
            story.ChoosePathString(knot);
            path.Add("(talk again)");
            Visit(walk, knot, repeats - 1, path, seen, problems);
            path.RemoveAt(path.Count - 1);
            return;
        }
        walk.Offered.UnionWith(choices);
        walk.Shown.UnionWith(story.currentChoices.Select(c => InkScan.ShownLabel(c.text, c.tags ?? new List<string>())));
        string key = $"{repeats}|{story.state.currentPathString}|{string.Join("|", choices)}|{string.Join(",", walk.World.Flags.Order())}|{string.Join(",", walk.World.Items.Order())}|{story.variablesState["pushes"]}|{story.variablesState["persuade_ok"]}";
        if (!seen.Add(key)) return;
        string state = story.state.ToJson();
        var world = walk.World;
        for (int i = 0; i < choices.Count; i++)
        {
            story.state.LoadJson(state);
            walk.World = world.Clone();
            story.ChooseChoiceIndex(i);
            path.Add(choices[i]);
            Visit(walk, knot, repeats, path, seen, problems);
            path.RemoveAt(path.Count - 1);
        }
        story.state.LoadJson(state);
        walk.World = world;
    }

    private static string Describe(List<string> path) => path.Count == 0 ? "starting" : string.Join(" > ", path.TakeLast(6));

    private static HashSet<string> TalkTargets(InkScan scan)
    {
        var talk = new Regex(@"\bTalk\(([^;]*?)\)\s*;");
        var literal = new Regex(@"""([a-z_][\w.]*)""");
        var knots = new HashSet<string>();
        foreach (var file in SourceFiles.Game(Root.Value))
        {
            foreach (Match call in talk.Matches(File.ReadAllText(file)))
                foreach (Match lit in literal.Matches(Regex.Replace(call.Groups[1].Value, @"\w+\(""[^""]*""\)", "")))
                    if (scan.Knots.Contains(lit.Groups[1].Value)) knots.Add(lit.Groups[1].Value);
        }
        return knots;
    }

    private static HashSet<string> OneShotKnotsOf() =>
        typeof(StoryIntegrityTests).GetField("OneShotKnots", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static)!
            .GetValue(null) is Dictionary<string, string> d ? d.Keys.ToHashSet() : new();

    [Fact]
    public void NoConversationHitsAnInkError()
    {
        var problems = Result.Value.Problems.Distinct().ToList();
        foreach (var p in problems.Take(40)) _out.WriteLine(p);
        Assert.True(problems.Count == 0, $"{problems.Count} Ink runtime errors; first: {problems.FirstOrDefault()}");
    }

    [Fact]
    public void EveryChoiceIsOffered()
    {
        var scan = InkScan.Parse(InkText);
        var offered = Result.Value.Offered;
        var missing = scan.Choices
            .Where(c => !c.Fallback && !offered.Any(o => InkScan.Matches(c, o)))
            .Select(c => $"{c.Knot}: {c.Label}")
            .Where(c => !UnreachedChoices.ContainsKey(c))
            .Distinct().ToList();
        foreach (var m in missing) _out.WriteLine(m);
        Assert.True(missing.Count == 0, "choices no conversation offers: " + string.Join(" | ", missing));
        var stale = UnreachedChoices.Keys.Where(k => scan.Choices.Any(c => $"{c.Knot}: {c.Label}" == k && offered.Any(o => InkScan.Matches(c, o)))).ToList();
        Assert.True(stale.Count == 0, "UnreachedChoices entries that are offered now: " + string.Join(" | ", stale));
    }

    [Fact]
    public void EveryOfferedChoiceFitsTheChoiceBar()
    {
        var shown = Result.Value.Shown;
        Assert.NotEmpty(shown);
        var tooLong = shown.Where(s => s.Length > InkScan.MaxChoiceChars).Order().ToList();
        Assert.True(tooLong.Count == 0, $"choice bar labels over {InkScan.MaxChoiceChars} characters (add a '#short: ...' tag): " +
            string.Join(" | ", tooLong));
        Assert.Contains("Bathtub? Swell. Set 'em up, pal.", shown);
        Assert.DoesNotContain(shown, s => s.Contains('#'));
    }
}
