using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Dialogue checks: conversations and the speech lines they show.</summary>
public partial class AutoPlay
{
    private async Task ConventFarewellTalkTest(Game game)
    {
        var original = game.CaptureSave();
        var originalPrefer = _prefer;
        try
        {
            var talk = game.Perform(Verb.Talk, "nun");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText == "What do you hope to find in all this, Detective?",
                "talking to the nun starts the farewell without the exit-only call-back");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText ==
                "I don't know, sister, but I can't stop at this point.");
            Check(game.Hud.SpeechText == "I don't know, sister, but I can't stop at this point.",
                "Micah's direct farewell reply matches the approved line");
            await Shot("convent_farewell");
            await talk;
            Check(game.Room is Rooms.ConventCorridor && GameState.Instance.HasFlag("nun_farewell_done") &&
                !GameState.Instance.HasFlag("convent_departed") && !game.Busy,
                "talking first clears Micah to leave but does not leave for him");
            await ReloadCheckpoint("convent_farewell");
            Check(GameState.Instance.HasFlag("nun_farewell_done") && !game.Hud.SpeechVisible,
                "loading after the farewell preserves permission without replaying it");
            var again = game.Perform(Verb.Talk, "nun");
            await Until(() => game.Hud.SpeechVisible);
            Check(game.Hud.SpeechText == "Go with God, Detective.", "the completed farewell does not repeat on another talk");
            await again;
            _prefer = new[] { "Right now, I'm not so sure." };
            Click(game.Room!.FindHotspot("entrance")!.Bounds.GetCenter(), MouseButton.Left);
            await Until(() => game.Room is Rooms.ConventRoad || game.Hud.SpeechVisible);
            Check(game.Room is Rooms.ConventRoad && GameState.Instance.HasFlag("convent_departed"),
                "opening the entrance after talking leaves directly without a second farewell");
            await Until(() => game.Room is Rooms.MotelAlley && !game.Busy, timeout: 300);
            Check(game.Room is Rooms.MotelAlley && GameState.Instance.HasFlag("convent_dead_end_done"),
                "the direct-talk exit plays the dead end and goes down to the motel");
            GameState.Instance.SetFlag("crate_moved");
            GameState.Instance.SetFlag("ladder_down");
            var climb = game.Perform(Verb.Hand, "ladder");
            await Until(() => game.Room is Rooms.Attic && !game.Busy, timeout: 300);
            await climb;
            if (game.Room is not Rooms.Attic || game.Busy)
                throw new InvalidOperationException($"Convent departure did not finish: room={game.Room?.Name}, busy={game.Busy}.");
            Check(game.Room is Rooms.Attic && !game.Busy, "the direct-talk exit completes the motel sequence");
            Check(!_offered.ContainsKey("eleanor_fire_escape"), "Act 1 stops on Eleanor's question, before the compensation choice");
            var back = game.ChangeRoom("motel_fire_escape", "interlude1");
            await Until(() => game.Hud.SpeechVisible &&
                game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month.");
            Check(game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month." &&
                !game.Hud.InsetVisible && !game.Hud.InsetDrawn && game.Room is Rooms.MotelFireEscape,
                "the alternate compensation answer also continues on the fire escape");
            await Until(() => game.Room is Rooms.Office && !game.Busy, timeout: 300);
            await back;
        }
        finally
        {
            _prefer = originalPrefer;
            await game.LoadGame(original);
        }
    }

    private readonly HashSet<string> _choiceBarProblems = new();

    /// <summary>
    /// Every offer: the bar shows one label per choice, each fits on one row in the dialogue font, and a shortened
    /// label is the choice's #short: tag (the spoken text, <paramref name="options"/>, stays full).
    /// </summary>
    private void CheckChoiceBar(Game game, string knot, IReadOnlyList<string> options, bool drawn = true)
    {
        var shown = DialogueManager.Instance.ShownChoices;
        void Problem(string what)
        {
            if (_choiceBarProblems.Add(what)) Check(false, what);
        }
        if (shown.Count != options.Count)
        {
            Problem($"{knot}: choice bar has {shown.Count} labels for {options.Count} choices");
            return;
        }
        if (drawn && !game.Hud.ChoiceTexts.SequenceEqual(shown))
            Problem($"{knot}: choice bar buttons show [{string.Join(" | ", game.Hud.ChoiceTexts)}]");
        for (int i = 0; i < shown.Count; i++)
        {
            float width = Hud.DialogueFont.GetStringSize(shown[i], HorizontalAlignment.Left, -1, Hud.DialogueFontSize).X;
            if (width > Hud.ChoiceTextWidth) Problem($"{knot}: choice label is cut off ({width:F0}px > {Hud.ChoiceTextWidth}px): {shown[i]}");
            if (shown[i] != options[i] && shown[i].Length >= options[i].Length)
                Problem($"{knot}: short label is not shorter than the spoken line: {shown[i]}");
        }
    }

    /// <summary>InkScan.MaxChoiceChars (checked by the unit tests) must match the font and the bar it stands for.</summary>
    private void ChoiceBarLimitTest()
    {
        float Width(int chars) => Hud.DialogueFont.GetStringSize(new string('W', chars), HorizontalAlignment.Left, -1, Hud.DialogueFontSize).X;
        Check(Width(InkScan.MaxChoiceChars) <= Hud.ChoiceTextWidth && Width(InkScan.MaxChoiceChars + 1) > Hud.ChoiceTextWidth,
            $"InkScan.MaxChoiceChars ({InkScan.MaxChoiceChars}) is the most characters that fit the choice bar " +
            $"({Width(InkScan.MaxChoiceChars):F0}px of {Hud.ChoiceTextWidth}px)");
    }

    private async Task StoryDialogueTest(Game game)
    {
        ChoiceBarLimitTest();
        var dialogue = DialogueManager.Instance;
        _ = dialogue.Get("pushes");
        var original = game.CaptureSave();
        double scale = Engine.TimeScale;
        var story = GD.Load<GodotInk.InkStory>(DialogueManager.StoryPath);
        try
        {
            foreach (var (knot, excerpt) in new[]
            {
                ("nun", "\"I will shew thee, O man, what is good.\""),
                ("caleb_act2", "Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace."),
                ("caleb_act2", "Our Father, who art in heaven, hallowed be Thy name... and then nothing. I can't get past it."),
                ("caleb_warn", "There's still a way back. There always is. But not where you're going."),
                ("caleb_last", "God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him."),
                ("caleb_club", "We hide them. A new name, a ticket, a parish in Milwaukee or a farm in Iowa that doesn't ask."),
                ("caleb_club", "You're a hypocrite, Caleb."),
                ("harrington_unmask", "A new face on that stage every Thursday"),
                ("bartender_gun", "They bring girls in off the trains like crates of oranges"),
            })
            {
                await game.LoadGame(original);
                story.ChoosePathString(knot);
                string lines = "";
                for (int turn = 0; turn < 32; turn++)
                {
                    lines += story.ContinueMaximally();
                    if (story.CurrentChoices.Count == 0) break;
                    story.ChooseChoiceIndex(0);
                }
                Check(lines.Contains(excerpt, StringComparison.Ordinal), $"{knot}: approved compiled dialogue");
            }
            foreach (bool together in new[] { false, true })
            foreach (bool exploded in new[] { false, true })
            foreach (bool documents in new[] { false, true })
            {
                await game.LoadGame(original);
                GameState.Instance.SetFlag(Endings.MansionExploded, exploded);
                GameState.Instance.SetFlag(Endings.TookDocuments, documents);
                story.ChoosePathString(together ? "ending_together" : "ending_alone");
                string lines = story.ContinueMaximally();
                bool deathReport = !together && exploded;
                Check(lines.Contains("The morning paper lists the dead. Eleanor Harrington.", StringComparison.Ordinal) == deathReport,
                    $"newspaper death report: together={together}, exploded={exploded}, documents={documents}");
                Check(lines.Contains("I left her there and lit the fuse.", StringComparison.Ordinal) == deathReport &&
                    lines.Contains("They know who died. They don't know what I did.", StringComparison.Ordinal) == deathReport,
                    "responsibility and secret lines accompany only the death report");
                Check(!lines.Contains("The sky over the Gold Coast is still orange.", StringComparison.Ordinal),
                    "next-morning dialogue does not retain the same-night sky");
            }
            // The Club's traffic ends only where somebody exposes it: Micah's papers (1, 6, 10), Eleanor's Thursday
            // book (8) or her testimony (9). Endings 2 and 3 keep the papers private.
            foreach (bool documents in new[] { false, true })
            for (int ending = 1; ending <= 11; ending++)
            {
                await game.LoadGame(original);
                for (int other = 1; other <= 11; other++) GameState.Instance.SetFlag($"ending_{other}", other == ending);
                GameState.Instance.SetFlag(Endings.TookDocuments, documents);
                story.ChoosePathString("epilogue");
                string lines = story.ContinueMaximally();
                bool exposed = ending is 8 or 9 || (documents && ending is 1 or 6 or 10);
                Check(lines.Contains("Thursday", StringComparison.Ordinal) == exposed,
                    $"epilogue {ending}: the end of the Club's traffic is told only where it is exposed (documents={documents})");
            }
            foreach (bool documents in new[] { false, true })
            {
                await game.LoadGame(original);
                GameState.Instance.SetFlag(Endings.TookDocuments, documents);
                story.ChoosePathString("ending_weary_road");
                Check(story.ContinueMaximally().Contains("Give them to the newspapers.", StringComparison.Ordinal) == documents,
                    $"ending 10: Eleanor asks Micah to give the papers to the press only when he has them (documents={documents})");
            }
            await game.LoadGame(original);
            story.ChoosePathString("prison_eleanor_caleb");
            Check(story.ContinueMaximally().Contains("I told the court the rest, Father.", StringComparison.Ordinal),
                "ending 9: Eleanor testified about the Club in open court");
            await game.LoadGame(original);
            Engine.TimeScale = 1;
            var timer = System.Diagnostics.Stopwatch.StartNew();
            await game.ChangeRoom("office", "start");
            timer.Stop();
            Check(GameState.Instance.HasFlag("teddy_gone"), "unaccelerated office sample completes its real dialogue");
            GD.Print($"[story timing] Office introduction at normal speed, automatic choices, no speech skipping: {timer.Elapsed.TotalSeconds:F1}s. Not a full-game or human playtime.");
            Engine.TimeScale = scale;
            await ShortChoiceLabelTest(game);
        }
        finally
        {
            Engine.TimeScale = scale;
            await game.LoadGame(original);
        }
    }

    /// <summary>A #short: choice shows its short label in the bar, and Micah still says the whole line.</summary>
    private async Task ShortChoiceLabelTest(Game game)
    {
        const string spoken = "The convent answers to the Church. And you're the Church on this side of town.";
        const string label = "The convent answers to the Church. And you're the Church.";
        var dialogue = DialogueManager.Instance;
        var originalPrefer = _prefer;
        IReadOnlyList<string> offered = Array.Empty<string>(), shown = Array.Empty<string>();
        void Offered(string knot, IReadOnlyList<string> options)
        {
            if (knot != "caleb_club" || offered.Count > 0) return;
            offered = options.ToArray();
            shown = dialogue.ShownChoices.ToArray();
        }
        dialogue.ChoicesOffered += Offered;
        try
        {
            _prefer = new[] { spoken };
            var talk = dialogue.Talk("caleb_club");
            await Until(() => game.Hud.SpeechVisible && game.Hud.SpeechText == spoken);
            int i = offered.ToList().IndexOf(spoken);
            Check(i >= 0 && i < shown.Count && shown[i] == label,
                "a choice with a #short: tag shows the short label in the choice bar");
            Check(game.Hud.SpeechText == spoken, "picking a shortened choice still speaks the full line");
            await talk;
        }
        finally
        {
            dialogue.ChoicesOffered -= Offered;
            _prefer = originalPrefer;
        }
    }

    /// <summary>Awaits <paramref name="task"/>, collecting every speech and thought line shown meanwhile.</summary>
    private static async Task<System.Collections.Generic.List<string>> Listen(Game game, Task task)
    {
        var heard = new System.Collections.Generic.List<string>();
        string? lastSpeech = null, lastThought = null;
        while (!task.IsCompleted)
        {
            if (game.Hud.SpeechVisible && lastSpeech != game.Hud.SpeechText)
                heard.Add(lastSpeech = game.Hud.SpeechText);
            if (game.Hud.ThoughtVisible && lastThought != game.Hud.ThoughtText)
                heard.Add(lastThought = game.Hud.ThoughtText);
            await game.Wait(0.05);
        }
        await task;
        return heard;
    }
}
