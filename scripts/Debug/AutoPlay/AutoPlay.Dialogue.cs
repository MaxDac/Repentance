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
            await Until(() => game.Hud.SpeechVisible &&
                game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month.");
            Check(game.Hud.SpeechText == "That's the first honest thing a man has said to me in a month." &&
                !game.Hud.InsetVisible && !game.Hud.InsetDrawn,
                "the alternate compensation answer also continues on the road");
            await Until(() => game.Room is Rooms.Attic && !game.Busy, timeout: 300);
            if (game.Room is not Rooms.Attic || game.Busy)
                throw new InvalidOperationException($"Convent departure did not finish: room={game.Room?.Name}, busy={game.Busy}.");
            Check(game.Room is Rooms.Attic && !game.Busy, "the direct-talk exit completes the motel sequence");
        }
        finally
        {
            _prefer = originalPrefer;
            await game.LoadGame(original);
        }
    }

    private async Task StoryDialogueTest(Game game)
    {
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
                ("caleb_warn", "There's still a way back. There always is. But not where you're going."),
                ("caleb_last", "God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him."),
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
            await game.LoadGame(original);
            Engine.TimeScale = 1;
            var timer = System.Diagnostics.Stopwatch.StartNew();
            await game.ChangeRoom("office", "start");
            timer.Stop();
            Check(GameState.Instance.HasFlag("teddy_gone"), "unaccelerated office sample completes its real dialogue");
            GD.Print($"[story timing] Office introduction at normal speed, automatic choices, no speech skipping: {timer.Elapsed.TotalSeconds:F1}s. Not a full-game or human playtime.");
        }
        finally
        {
            Engine.TimeScale = scale;
            await game.LoadGame(original);
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
