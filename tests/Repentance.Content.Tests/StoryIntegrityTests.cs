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

    /// <summary>Game code: scripts/ and the src/ libraries, except the debug runners, which seed state on purpose.</summary>
    private static readonly Lazy<Dictionary<string, string>> Code = new(() =>
        SourceFiles.Game(Root.Value)
            .ToDictionary(f => Path.GetRelativePath(Root.Value, f).Replace('\\', '/'), File.ReadAllText));

    /// <summary>Knots that are one-time cutscenes: all their choices are <c>*</c> with no fallback, so the game must never run them twice.</summary>
    private static readonly Dictionary<string, string> OneShotKnots = new()
    {
        ["bartender_gun"] = "Alley: Tony at gunpoint, once; afterwards he is shot or Micah has left, and later talks use other lines",
        ["bartender_shot"] = "Alley: once, right after the shoulder shot; Micah then kills Tony or walks out, and never hears it again",
        ["beaten_choice"] = "ChurchExterior: the church steps cutscene, played once on the way out of the Club",
        ["caleb_club"] = "Church: Act 2 Club talk, guarded by caleb_club; later visits use other knots",
        ["caleb_tony"] = "Church: the confession after killing Tony, once; surrender ends Act 3 and confessed_tony skips it on return",
        ["club_caught"] = "ClubStage: the unmasking cutscene, once",
        ["eleanor_persuade"] = "MansionBedroom: the finale, once",
        ["eleanor_footsteps"] = "MansionBedroom: the last choice after the persuasion fails, once",
        ["eleanor_fire_escape"] = "MotelFireEscape: the rest of the fire-escape talk after the First Interlude, once",
        ["moc"] = "ClubHall: the first, unmasked visit, once; club_out is set when Micah is thrown out",
        ["motel_clerk"] = "redirects to motel_clerk.again once the first talk sets clerk_talked",
        ["motel_clerk_return"] = "redirects to motel_clerk_return.again once the clerk has talked and motel_return_done is set",
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
        foreach (var c in typeof(Endings).GetFields().Where(f => f.IsLiteral && f.FieldType == typeof(string))) read.Add((string)c.GetValue(null)!);
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
    public void EveryChoiceFitsTheChoiceBar()
    {
        var choices = Ink.Value.Choices.Where(c => !c.Fallback).ToList();
        Assert.NotEmpty(choices);
        // inline {...} content is counted by its literal text, so keep dynamic labels well under the limit
        var tooLong = choices
            .Select(c => (c, shown: Regex.Replace(c.Shown, @"\{[^{}]*\}", "")))
            .Where(x => x.shown.Length > InkScan.MaxChoiceChars)
            .Select(x => $"line {x.c.Line} ({x.shown.Length} chars): {x.c.Shown}").ToList();
        Assert.True(tooLong.Count == 0, $"choice labels longer than {InkScan.MaxChoiceChars} characters are cut off in the choice bar; " +
            "add a '#short: ...' tag (docs/story-and-dialogue.md): " + string.Join(" | ", tooLong));
        var badShort = choices.Where(c => c.Shown != c.Label && (c.Shown.Length == 0 || c.Shown.Length >= c.Label.Length))
            .Select(c => $"line {c.Line}: {c.Shown}").ToList();
        Assert.True(badShort.Count == 0, "#short: labels must be non-empty and shorter than the spoken text: " + string.Join(" | ", badShort));
        var needless = choices.Where(c => c.Shown != c.Label && c.Label.Length <= InkScan.MaxChoiceChars)
            .Select(c => $"line {c.Line}: {c.Label}").ToList();
        Assert.True(needless.Count == 0, "#short: tags on choices that already fit (remove them): " + string.Join(" | ", needless));
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
    private static bool Dynamic(string flag) => Regex.IsMatch(flag, @"^(ending_\d+|stash_\w*)$");

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
    [InlineData("docs/saves-and-settings.md")]
    [InlineData("Walkthrough.md")]
    public void DocsStateTheCurrentSaveVersion(string doc)
    {
        var text = File.ReadAllText(Path.Combine(Root.Value, doc));
        var versions = Regex.Matches(text, @"\bis version (\d+)").Select(m => int.Parse(m.Groups[1].Value)).ToList();
        Assert.NotEmpty(versions);
        Assert.All(versions, v => Assert.Equal(SaveData.CurrentVersion, v));
    }

    /// <summary>
    /// Timeline wording that drifted when the convent visit moved to the next evening (Saturday) and Micah started
    /// arriving at the motel on foot: Act Two is Thursday, days after the motel, Eleanor was met on the fire escape,
    /// and he has no car there.
    /// </summary>
    [Theory]
    [InlineData("Saturday, at the turning of the night", "the Club card is for Thursday, days after the motel")]
    [InlineData("Saturday is tonight", "Act Two is days later, on Thursday")]
    [InlineData("Sunday, at the turning of the night", "the Club card is for Thursday, days after the motel")]
    [InlineData("Sunday is tonight", "the motel night is Saturday and Act Two is days later, on Thursday")]
    [InlineData("The Harringtons liked their reading", "the library is the public library where Rose works")]
    [InlineData("or a daughter.", "the library desk is a public catalogue desk")]
    [InlineData("a woman I met four days ago", "Micah met Eleanor on the fire escape the night before")]
    [InlineData("Still warm on his side", "the Second Interlude is later the same night, after he left her")]
    [InlineData("The motel, the night after.", "the Order takes Eleanor the same night Micah leaves her")]
    [InlineData("Then why write it all down, Micah?", "Act One stops before Micah's promise in her room")]
    [InlineData("I called her a whore", "in the truth arm Agatha never says the word in the cell")]
    [InlineData("His car's gone from the lot", "Micah came to the motel on foot")]
    [InlineData("the motel on the road", "the motel is down the hill from the convent")]
    [InlineData("The Club took her back tonight", "the Order took Eleanor the motel night, before the daylight Club visit")]
    [InlineData("I don't have a car", "Micah owns the Ford Eleanor changes in (endings 2 and 10)")]
    [InlineData("Sit up, child", "Eleanor is already sitting up at the knock, and stands for Agatha's visit")]
    [InlineData("The only vanity allowed", "the comb is Eleanor's own, from her duffle, not the convent's")]
    [InlineData("Three floors of fire escape", "Harrington's office is one floor up the fire escape")]
    [InlineData("three floors of iron", "Harrington's office is one floor up the fire escape")]
    [InlineData("good Scotch and two books for show", "the library is the public library where Rose works")]
    [InlineData("Prohibition never made it past the front desk", "the library is the public library where Rose works")]
    [InlineData("nobody trusted the help to touch", "the library is the public library where Rose works")]
    [InlineData("One glass would steady my hands", "the library side table holds a glass of water, not liquor")]
    [InlineData("sat on the edge of the cot", "Agatha stops a step short of the bed and stays standing")]
    [InlineData("left them on Tuesday", "on Tuesday Eleanor dined at the Aurelian; the Club meets on Thursdays")]
    [InlineData("runs past a lit window", "on the motel return Eleanor's window is dark")]
    [InlineData("Serve your time, Micah Jones", "ending 8 also plays when Micah walked out of Joliet's reach unpunished; she wishes him peace")]
    [InlineData("the second one only to cover up the first", "in ending 6 after killing Tony, Tony died first, to keep him quiet")]
    [InlineData("glass between us", "Joliet's visiting room is a table with a NO TOUCHING sign, not a glass partition")]
    [InlineData("visiting-room glass", "Joliet's visiting room is a table with a NO TOUCHING sign, not a glass partition")]
    [InlineData("packed long ago", "Eleanor packed the duffle that afternoon")]
    [InlineData("Two dresses, my nightclothes", "the duffle holds the white dress, the black suit and the pearls she changes into")]
    [InlineData("In November.", "the story opens in October 1927")]
    [InlineData("est. 1923", "the Aurelian's sign has blinked at Micah for six years by 1927")]
    [InlineData("all through vespers", "Eleanor reaches the convent after Compline, after Vespers")]
    [InlineData("St. Brendan", "Caleb's church is Holy Name")]
    [InlineData("coal door", "the mansion has only a coal hatch, too small for anyone over nine")]
    [InlineData("Drake's", "the hotel with the service cage is the Aurelian")]
    [InlineData("renewed our vows", "there was no 1927 rite for renewing vows; Rose and Micah say their promises again, with Caleb's blessing")]
    public void TimelineWordingStaysConsistent(string stale, string reason)
    {
        var scenes = Directory.EnumerateFiles(Path.Combine(Root.Value, "scenes"), "*.tscn", SearchOption.AllDirectories)
            .Select(f => new KeyValuePair<string, string>(Path.GetRelativePath(Root.Value, f).Replace('\\', '/'), File.ReadAllText(f)));
        var sources = Code.Value.Append(new KeyValuePair<string, string>("dialogue/repentance.ink", InkText)).Concat(scenes);
        var hits = sources.Where(kv => kv.Value.Contains(stale)).Select(kv => kv.Key).ToList();
        Assert.True(hits.Count == 0, $"\"{stale}\" in {string.Join(", ", hits)}: {reason}");
    }

    [Fact]
    public void BranchDocsMatchTheLines()
    {
        string Flat(string doc) => Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, doc)), @"\s+", " ");
        var theology = Flat("docs/theology.md");
        Assert.Contains("Ending 1 ends it if Micah took the papers (Caleb carries them to the Tribune)", theology);
        Assert.Contains("ending 1 with the papers (the Tribune)", theology);
        Assert.Contains("\"the day it won't bury the girls we hid\"", theology);
        Assert.Contains("the day it won't bury the girls we hid", InkText);
        Assert.DoesNotContain("won't cost the girls", theology);
        var walkthrough = Flat("Walkthrough.md");
        Assert.DoesNotContain("police report", walkthrough);
        Assert.DoesNotContain("St. Brendan", walkthrough);
        Assert.DoesNotContain("renewing the vows", walkthrough);
        Assert.Contains("only that Tony was found behind the Blue Lantern", walkthrough);
        Assert.DoesNotContain("If Micah killed Tony, the \"Amen.\" is left off", walkthrough);
        Assert.DoesNotContain("two pasted halves aren't needed", walkthrough);
        Assert.Contains("Three nights after the Club, Caleb got her out", walkthrough);
        var overview = Flat("docs/story-overview.md");
        Assert.Contains("Micah's papers handed in with his confession to the grand jury in ending 12", overview);
        Assert.Contains("endings 8, 10, 11, and ending 1 with Caleb", overview);
        var persuasion = Flat("docs/eleanor-persuasion.md");
        Assert.Contains("it reads neither `eleanor_refused` nor the score", persuasion);
        Assert.DoesNotContain("only reads the flags `eleanor_convinced` / `eleanor_refused`", persuasion);
    }

    [Fact]
    public void FirstInterludeDocsHandBackToTheFireEscape()
    {
        var row = File.ReadAllLines(Path.Combine(Root.Value, "docs/story-and-dialogue.md"))
            .Single(l => l.StartsWith("| First interlude |"));
        Assert.Contains("`motel_fire_escape` entry `interlude1`", row);
        Assert.True(row.IndexOf("motel_fire_escape", StringComparison.Ordinal) < row.IndexOf("motel_night", StringComparison.Ordinal),
            "EndFirst resumes Micah on the fire escape before his night in motel_night");
    }

    [Fact]
    public void WalkthroughQuotesTeddysPaymentRemark()
    {
        var text = Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, "Walkthrough.md")), @"\s+", " ");
        Assert.DoesNotContain("walks around with more than a day's pay", text);
        Assert.Contains("Pocket lint to him. A day's pay to me, and then some.", text);
        Assert.Contains("Pocket lint to him. A day's pay to me, and then some.", Code.Value.Single(kv => kv.Key.EndsWith("Rooms/Office.cs")).Value);
    }

    [Theory]
    [InlineData("On second thought, I don't like you. Not one bit.")]
    [InlineData("You would do better to end the search here, and have nothing more to do with that Jezebel.")]
    [InlineData("Forgiving's the easy part, Micah. Forgetting is what you keep asking for.")]
    [InlineData("There isn't much left for me to do.")]
    [InlineData("You know that isn't true.")]
    [InlineData("Are you crazy?!")]
    [InlineData("Yeah. You can say that, sister. Where's Eleanor? What goes on at that club?")]
    [InlineData("Coat. Hat. The bag, too.")]
    public void WalkthroughQuotesThePerformedLine(string line)
    {
        var text = Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, "Walkthrough.md")), @"\s+", " ");
        Assert.Contains($"\"{line}", text);
        Assert.Contains(line, InkText);
    }

    [Fact]
    public void WalkthroughQuotesTheDressingRoomOrderHint()
    {
        var text = Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, "Walkthrough.md")), @"\s+", " ");
        Assert.DoesNotContain("(\"Powder first.", text);
        Assert.Contains("(\"Face powder first. Then the mouth. Then the hair.\")", text);
        Assert.Contains("\"Face powder first. Then the mouth. Then the hair.", Code.Value.Single(kv => kv.Key.EndsWith("Rooms/ClubBackstage.cs")).Value);
    }

    [Fact]
    public void EleanorTakesTheThursdayBookInTheStudy()
    {
        var strike = InkText[InkText.IndexOf("=== coda_strike ===", StringComparison.Ordinal)..];
        strike = strike[..strike.IndexOf("-> END", StringComparison.Ordinal)];
        Assert.DoesNotContain("Thursday book", strike);
        Assert.Contains("The Thursday book", Code.Value.Single(kv => kv.Key.EndsWith("MansionStudy.cs")).Value);
    }

    [Theory]
    [InlineData("Walkthrough.md")]
    [InlineData("docs/story-overview.md")]
    public void DocsCountSeventeenMicahPuzzles(string doc)
    {
        var text = File.ReadAllText(Path.Combine(Root.Value, doc));
        Assert.DoesNotContain("sixteen", text);
        Assert.Contains("seventeen", text);
    }

    [Fact]
    public void OverviewDiagramAndWalkthroughCountEveryEnding()
    {
        var overview = File.ReadAllText(Path.Combine(Root.Value, "docs/story-overview.md"));
        var nodes = Regex.Matches(overview, @"\bE(\d+)\[""\1:").Select(m => int.Parse(m.Groups[1].Value)).Order().ToList();
        Assert.Equal(Enumerable.Range(1, Endings.Count), nodes);
        var walkthrough = Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, "Walkthrough.md")), @"\s+", " ");
        Assert.Contains("fourteen ending outcomes", walkthrough);
        Assert.Equal(14, Endings.Count);
        Assert.Contains("Every ending but 7 and 14 has the \"The next morning\" caption.", walkthrough);
    }

    [Fact]
    public void OverviewQuotesAgathasJezebelLine()
    {
        var text = Regex.Replace(File.ReadAllText(Path.Combine(Root.Value, "docs/story-overview.md")), @"\s+", " ");
        Assert.DoesNotContain("another Jezebel from that hideous Club", text);
        Assert.Contains("A Jezebel from that hideous Club", InkText);
    }
}
