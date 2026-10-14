using System.Text.RegularExpressions;
using Repentance;
using Xunit;

namespace Repentance.Tests;

/// <summary>
/// Static checks of the story across dialogue/repentance.ink and the C# rooms: every knot the game calls exists,
/// every flag read can be set and every flag set is read, every item exists and can be obtained, and an exhaustive
/// walk of the real Ink story (compiled with the same ink version as the game) finds no dead ends and reaches every
/// choice. The runtime side (playing every ending) is <c>--playthrough</c>.
/// </summary>
public class StoryIntegrityTests
{
    private static readonly Lazy<string> Root = new(() =>
    {
        for (var dir = new DirectoryInfo(AppContext.BaseDirectory); dir != null; dir = dir.Parent)
            if (File.Exists(Path.Combine(dir.FullName, "project.godot"))) return dir.FullName;
        throw new InvalidOperationException("project.godot not found above the test binaries");
    });

    private static string InkText => File.ReadAllText(Path.Combine(Root.Value, "dialogue", "repentance.ink"));
    private static readonly Lazy<InkScan> Ink = new(() => InkScan.Parse(InkText));

    /// <summary>Game code: everything under scripts/ except the debug runners, which seed state on purpose.</summary>
    private static readonly Lazy<Dictionary<string, string>> Code = new(() =>
        Directory.GetFiles(Path.Combine(Root.Value, "scripts"), "*.cs", SearchOption.AllDirectories)
            .Where(f => !f.Replace('\\', '/').Contains("/scripts/Debug/"))
            .ToDictionary(f => Path.GetRelativePath(Root.Value, f).Replace('\\', '/'), File.ReadAllText));

    /// <summary>Knots that are one-time cutscenes: all their choices are <c>*</c> with no fallback, so the game must never run them twice.</summary>
    private static readonly Dictionary<string, string> OneShotKnots = new()
    {
        ["bartender_gun"] = "Alley: Tony at gunpoint, once; the scene ends Act 3's alley either way",
        ["beaten_choice"] = "ChurchExterior: the church steps cutscene, played once on the way out of the Club",
        ["caleb_club"] = "Church: Act 2 Club talk, guarded by caleb_club; later visits use other knots",
        ["club_caught"] = "ClubStage: the unmasking cutscene, once",
        ["eleanor_persuade"] = "MansionBedroom: the finale, once",
        ["eleanor_road"] = "ConventRoad: the Act 1 farewell cutscene, once",
        ["moc"] = "ClubHall: the first, unmasked visit, once; club_out is set when Micah is thrown out",
        ["nun"] = "redirects to nun.again once the first talk sets nun_talked",
        ["nun_club"] = "ConventCorridor: once nun_club_asked is set the sister answers in C# and the knot is skipped (B1)",
        ["office_ring"] = "Office: Act 2 ring choice, once on the way out",
        ["oldman_taunt"] = "MansionBedroom: the confrontation, once",
        ["sal.bribe"] = "reached only through Sal's one-time \"I don't know the password\" choice",
        ["street_choice"] = "Street: the thrown-out cutscene, once",
        ["teddy"] = "redirects to teddy.again once the briefing sets teddy_briefed",
    };

    /// <summary>Flags written but never read by the story, kept because the tests assert on them.</summary>
    private static readonly Dictionary<string, string> UnreadFlags = new()
    {
        ["harrington_unmasked"] = "AutoPlay asserts the unmasking happened",
        ["ring_taken_act2"] = "the counterpart of ring_left_act2; SaveDataTests and EndingsTests assert on it",
        ["shot_oldman"] = "the playthrough asserts Harrington was shot",
        ["trunk_kicked"] = "AutoPlay asserts the kick on the trunk",
        ["brute_called"] = "AutoPlay asserts the brute was called",
        ["made_blue_carnation"] = "recipe bookkeeping; AutoPlay asserts the carnation was dyed",
        ["invitation_sealed"] = "recipe bookkeeping; AutoPlay asserts the invitation was sealed",
        ["wax_softened"] = "recipe bookkeeping; AutoPlay asserts the wax was softened",
        ["lantern_lit"] = "recipe bookkeeping; AutoPlay asserts the lantern was lit",
    };

    /// <summary>Items given through a variable, which the GiveItem("...") search can't see.</summary>
    private static readonly Dictionary<string, string> IndirectItems = new()
    {
        ["signet_raven"] = "ClubVestibule.Cloak gives the signet of the cloak searched",
        ["signet_lion"] = "ClubVestibule.Cloak gives the signet of the cloak searched",
        ["signet_stag"] = "ClubVestibule.Cloak gives the signet of the cloak searched",
    };

    /// <summary>Flags read by the story but set only by code these regexes can't follow.</summary>
    private static readonly Dictionary<string, string> UnsetFlags = new()
    {
    };

    private static readonly Regex TalkCall = new(@"\bTalk\(([^;]*?)\)\s*;");
    private static readonly Regex Literal = new(@"""([a-z_][\w.]*)""");
    private static readonly Regex Const = new(@"public const string (\w+) = ""(\w+)"";");
    private static readonly Regex IndirectRead = new(@"\b(?:has|hasFlag|[Ff]lags\.Contains|Toggle)\(\s*""(\w+)""");
    private static readonly Regex IndirectSet = new(@"\b(?:[Ff]lags\.Add|Toggle)\(\s*""(\w+)""");
    private static readonly Regex SceneFlags = new(@"^(?:Show|Hide)IfFlags = ""([^""]*)""", RegexOptions.Multiline);
    private static readonly Regex FlagCall = new(@"\b(SetFlag|HasFlag)\(\s*(?:""(\w+)""|(\w+\.\w+)|(\w+))\s*(,\s*(\w+))?");

    private static Dictionary<string, string> Constants()
    {
        var map = new Dictionary<string, string>();
        foreach (var (file, text) in Code.Value)
        {
            string cls = Path.GetFileNameWithoutExtension(file);
            foreach (Match m in Const.Matches(text))
            {
                map[$"{cls}.{m.Groups[1].Value}"] = m.Groups[2].Value;
                map.TryAdd(m.Groups[1].Value, m.Groups[2].Value);
            }
        }
        return map;
    }

    /// <summary>(flags set, flags read) in C#; a <c>SetFlag(x, false)</c> clears a flag and counts as neither.</summary>
    private static (HashSet<string> Set, HashSet<string> Read) CodeFlags()
    {
        var consts = Constants();
        var set = new HashSet<string>();
        var read = new HashSet<string>();
        foreach (var text in Code.Value.Values)
            foreach (Match m in FlagCall.Matches(text))
            {
                string? flag = m.Groups[2].Success ? m.Groups[2].Value
                    : m.Groups[3].Success ? consts.GetValueOrDefault(m.Groups[3].Value)
                    : consts.GetValueOrDefault(m.Groups[4].Value);
                if (flag == null) continue;
                if (m.Groups[1].Value == "HasFlag") read.Add(flag);
                else if (m.Groups[6].Value != "false") set.Add(flag);
            }
        // Endings, puzzle migrations and saves read flags through a Func<string, bool> or the save's flag list.
        foreach (var text in Code.Value.Values)
        {
            foreach (Match m in IndirectRead.Matches(text)) read.Add(m.Groups[1].Value);
            foreach (Match m in IndirectSet.Matches(text)) set.Add(m.Groups[1].Value);
        }
        foreach (var c in typeof(Endings).GetFields().Where(f => f.IsLiteral)) read.Add((string)c.GetValue(null)!);
        foreach (var note in Notes.All)
            read.UnionWith(note.Unlock.Concat(note.Lines.Select(l => l.Flag).OfType<string>()));
        // Hotspots show and hide on flags set in the room scenes.
        foreach (var scene in Directory.GetFiles(Path.Combine(Root.Value, "scenes"), "*.tscn", SearchOption.AllDirectories))
            foreach (Match m in SceneFlags.Matches(File.ReadAllText(scene)))
                read.UnionWith(m.Groups[1].Value.Split(',').Select(f => f.Trim().TrimStart('!')).Where(f => f.Length > 0));
        foreach (var r in Recipes.All.Where(r => r.Flag != null)) set.Add(r.Flag!);
        return (set, read);
    }

    private static HashSet<string> TalkTargets()
    {
        var knots = new HashSet<string>();
        foreach (var text in Code.Value.Values)
            foreach (Match call in TalkCall.Matches(text))
                foreach (Match lit in Literal.Matches(Regex.Replace(call.Groups[1].Value, @"\w+\(""[^""]*""\)", "")))
                    knots.Add(lit.Groups[1].Value);
        return knots;
    }

    [Fact]
    public void EveryKnotTheGameCallsExists()
    {
        var targets = TalkTargets();
        Assert.NotEmpty(targets);
        var missing = targets.Where(k => !Ink.Value.Knots.Contains(k)).OrderBy(k => k).ToList();
        Assert.True(missing.Count == 0, "Talk() calls knots missing from repentance.ink: " + string.Join(", ", missing));
    }

    [Fact]
    public void EveryKnotIsCalledOrDivertedTo()
    {
        var talked = TalkTargets();
        string ink = InkText;
        var unused = Ink.Value.Knots.Where(k =>
        {
            if (talked.Contains(k)) return false;
            string name = k.Contains('.') ? k[(k.IndexOf('.') + 1)..] : k;
            return !Regex.IsMatch(ink, $@"->\s*({Regex.Escape(k)}|{Regex.Escape(name)})\b");
        }).OrderBy(k => k).ToList();
        Assert.True(unused.Count == 0, "knots nothing calls or diverts to: " + string.Join(", ", unused));
    }

    [Fact]
    public void EveryFlagReadCanBeSet()
    {
        var (codeSet, codeRead) = CodeFlags();
        var set = codeSet.Concat(Ink.Value.Args("set_flag")).ToHashSet();
        var read = codeRead.Concat(Ink.Value.Args("has_flag")).ToHashSet();
        var never = read.Where(f => !set.Contains(f) && !UnsetFlags.ContainsKey(f) && !Dynamic(f)).OrderBy(f => f).ToList();
        Assert.True(never.Count == 0, "flags read but never set: " + string.Join(", ", never));
        var stale = UnsetFlags.Keys.Where(set.Contains).ToList();
        Assert.True(stale.Count == 0, "UnsetFlags entries that are set now: " + string.Join(", ", stale));
    }

    [Fact]
    public void EveryFlagSetIsRead()
    {
        var (codeSet, codeRead) = CodeFlags();
        var set = codeSet.Concat(Ink.Value.Args("set_flag")).ToHashSet();
        var read = codeRead.Concat(Ink.Value.Args("has_flag")).ToHashSet();
        var unread = set.Where(f => !read.Contains(f) && !UnreadFlags.ContainsKey(f) && !Dynamic(f)).OrderBy(f => f).ToList();
        Assert.True(unread.Count == 0, "flags set but never read (delete them, or allowlist with a reason): " + string.Join(", ", unread));
        var stale = UnreadFlags.Keys.Where(f => read.Contains(f) || !set.Contains(f)).ToList();
        Assert.True(stale.Count == 0, "UnreadFlags entries that are read now, or no longer set: " + string.Join(", ", stale));
    }

    /// <summary>Flags built at runtime: ending_N from <see cref="Endings.Resolve"/>, stash_* for Micah's stashed items.</summary>
    private static bool Dynamic(string flag) => Regex.IsMatch(flag, @"^(ending_\d|stash_\w*)$");

    [Fact]
    public void EveryItemExistsAndCanBeObtained()
    {
        var code = string.Join("\n", Code.Value.Values);
        var given = Regex.Matches(code, @"\bGiveItem\(\s*""(\w+)""").Select(m => m.Groups[1].Value)
            .Concat(Ink.Value.Args("give_item"))
            .Concat(Recipes.All.Select(r => r.Result))
            .ToHashSet();
        var referenced = Regex.Matches(code, @"\b(GiveItem|TakeItem|HasItem)\(\s*""(\w+)""").Select(m => m.Groups[2].Value)
            .Concat(Ink.Value.Args("give_item")).Concat(Ink.Value.Args("take_item")).Concat(Ink.Value.Args("has_item"))
            .Concat(Recipes.All.SelectMany(r => r.Inputs.Append(r.Result)))
            .ToHashSet();
        var unknown = referenced.Where(i => !Items.All.ContainsKey(i)).OrderBy(i => i).ToList();
        Assert.True(unknown.Count == 0, "item ids not in Items.All: " + string.Join(", ", unknown));
        var unobtainable = Items.All.Keys.Where(i => !given.Contains(i) && !MicahKit.Pinned.Contains(i) && !IndirectItems.ContainsKey(i))
            .OrderBy(i => i).ToList();
        Assert.True(unobtainable.Count == 0, "items nothing gives: " + string.Join(", ", unobtainable));
        var stale = IndirectItems.Keys.Where(i => given.Contains(i) || !Items.All.ContainsKey(i)).ToList();
        Assert.True(stale.Count == 0, "IndirectItems entries given directly now, or gone: " + string.Join(", ", stale));
    }

    [Fact]
    public void OneShotKnotsAreAllowlisted()
    {
        var oneShot = Ink.Value.OneShotKnots().ToHashSet();
        var missing = oneShot.Where(k => !OneShotKnots.ContainsKey(k)).OrderBy(k => k).ToList();
        Assert.True(missing.Count == 0,
            "knots with only one-time choices (a dead end if the game runs them again): " + string.Join(", ", missing) +
            ". Add a sticky choice or fallback, or list the knot in OneShotKnots with the reason the game plays it only once.");
        var stale = OneShotKnots.Keys.Where(k => !oneShot.Contains(k)).ToList();
        Assert.True(stale.Count == 0, "OneShotKnots entries that are no longer one-shot: " + string.Join(", ", stale));
    }

    [Theory]
    [InlineData("README.md")]
    [InlineData("Walkthrough.md")]
    public void DocsStateTheCurrentSaveVersion(string doc)
    {
        var text = File.ReadAllText(Path.Combine(Root.Value, doc));
        var versions = Regex.Matches(text, @"\bis version (\d+)").Select(m => int.Parse(m.Groups[1].Value)).ToList();
        Assert.NotEmpty(versions);
        Assert.All(versions, v => Assert.Equal(SaveData.CurrentVersion, v));
    }
}
