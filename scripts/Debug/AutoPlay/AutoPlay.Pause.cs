using Godot;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>The --pause-test checks and the pause during the run.</summary>
public partial class AutoPlay
{
    public async Task RunPauseTests(Game game)
    {
        _marker = "PAUSE TEST";
        if (!Begin(game, "pause_test"))
        {
            Finish();
            return;
        }
        game.AutosaveEnabled = false;
        try
        {
            await game.ChangeRoom("attic", "start");
            await PauseTest(game);
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            if (game.IsPaused) game.TogglePause();
        }
        Finish();
    }

    private async Task PauseTest(Game game)
    {
        double timeScale = Engine.TimeScale;
        Engine.TimeScale = 1;
        try
        {
            var speech = game.Run(() => game.Say("Pause test."));
            await Observe(0.35);
            var frame = game.Player.GetChildren().OfType<Sprite2D>().Single().Frame;
            var playtime = game.CaptureSave().PlaytimeSeconds;
            PressKey(Key.Space);
            Check(game.IsPaused && game.GetTree().Paused && game.Hud.PauseVisible, "Space pauses mid-sentence");
            _game.GetViewport().PushInput(new InputEventKey
            {
                Keycode = Key.Space, PhysicalKeycode = Key.Space, Pressed = true, Echo = true,
            }, true);
            Click(new Vector2(240, 140), MouseButton.Left);
            Click(game.Hud.SatchelCenter, MouseButton.Left);
            PressKey(Key.Escape);
            await Observe(2);
            Check(game.IsPaused && !game.Hud.Menu.IsOpen, "repeat Space and Esc do not exit Space pause");
            Check(!speech.IsCompleted && game.Hud.SpeechVisible && game.Hud.SpeechText == "Pause test.",
                "paused speech survives its full duration and cannot be skipped");
            Check(game.Player.GetChildren().OfType<Sprite2D>().Single().Frame == frame, "talk animation freezes");
            Check(game.CaptureSave().PlaytimeSeconds == playtime && !game.Hud.InventoryOpen, "playtime and inventory input freeze");
            PressKey(Key.Space);
            await Observe(0.3);
            Check(!game.IsPaused && !game.Hud.PauseVisible && !speech.IsCompleted, "resume retains remaining sentence duration");
            await AwaitTest(speech, "speech finishes after resuming");
            var nextSpeech = game.Run(() => game.Say("Click to skip."));
            await Observe(0.3);
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(0.3);
            Check(nextSpeech.IsCompleted && !game.Hud.SpeechVisible, "click-to-skip still works after resuming");

            var thought = game.Run(() => game.Think("Pause thought."));
            await Observe(0.35);
            PressKey(Key.Space);
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(3);
            Check(game.IsPaused && !thought.IsCompleted && game.Hud.ThoughtVisible && game.Hud.ThoughtText == "Pause thought." &&
                !game.Hud.SpeechVisible && !game.Player.Talking, "a paused thought outlasts its duration and cannot be skipped");
            PressKey(Key.Space);
            await Observe(0.3);
            Check(!game.IsPaused && !thought.IsCompleted && game.Hud.ThoughtVisible, "the thought is still up after resuming");
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(0.3);
            Check(thought.IsCompleted && !game.Hud.ThoughtVisible, "click skips the thought after resuming");
            var skipped = game.Run(() => game.Think("Skip this thought."));
            await Observe(0.3);
            game.SkipSpeech();
            await Observe(0.3);
            Check(skipped.IsCompleted && !game.Hud.ThoughtVisible, "SkipSpeech ends a thought");

            var timer = game.Wait(0.8);
            await Observe(0.2);
            PressKey(Key.Space);
            await Observe(1);
            Check(!timer.IsCompleted, "gameplay timer does not expire while paused");
            PressKey(Key.Space);
            await Observe(0.2);
            Check(!timer.IsCompleted, "gameplay timer retains its remaining duration");
            await AwaitTest(timer, "gameplay timer completes after resuming");

            var walk = game.WalkTo(new Vector2(300, 205));
            await Observe(0.1);
            var position = game.Player.Position;
            PressKey(Key.Space);
            Click(new Vector2(420, 220), MouseButton.Left);
            await Observe(0.8);
            Check(!walk.IsCompleted && game.Player.IsWalking && game.Player.Position == position, "walking path freezes without cancellation");
            PressKey(Key.Space);
            await AwaitTest(walk, "walking completes after resuming");
            Check(await walk, "resume preserves the original walk");

            game.Hud.ShowInventory(true);
            PressKey(Key.Space);
            Click(new Vector2(10, 220), MouseButton.Left);
            await Observe(0.1);
            Check(game.Hud.InventoryOpen, "paused inventory remains open despite outside clicks");
            PressKey(Key.Space);
            Check(game.Hud.InventoryOpen, "resume preserves open inventory");
            game.Hud.ShowInventory(false);

            var choices = game.Hud.ShowChoices(new[] { "Pause regression choice" });
            var choiceButton = game.Hud.FindChildren("*", "Button", true, false).OfType<Button>()
                .Single(b => b.Text == "Pause regression choice");
            await Observe(0.1);
            PressKey(Key.Space);
            Click(choiceButton.GetGlobalRect().GetCenter(), MouseButton.Left);
            await Observe(0.1);
            Check(!choices.IsCompleted && game.Hud.ChoicesVisible, "dialogue choices cannot be selected while paused");
            PressKey(Key.Space);
            Click(choiceButton.GetGlobalRect().GetCenter(), MouseButton.Left);
            await AwaitTest(choices, "dialogue choices work after resuming");

            var image = game.Hud.ShowImage(GD.Load<Texture2D>("res://assets/art/ui/triquetra.png"));
            PressKey(Key.Space);
            Click(new Vector2(240, 140), MouseButton.Left);
            await Observe(0.1);
            Check(!image.IsCompleted && game.Hud.ImageVisible, "paused close-up cannot be dismissed");
            PressKey(Key.Space);
            Click(new Vector2(240, 140), MouseButton.Left);
            await AwaitTest(image, "close-up can be dismissed after resuming");

            var wheel = game.Hud.Wheel.Open(new Vector2(240, 140), "Pause regression");
            PressKey(Key.Space);
            Click(game.Hud.Wheel.SlotCenter(Verb.Look), MouseButton.Left);
            await Observe(0.1);
            Check(!wheel.IsCompleted && game.Hud.Wheel.IsOpen, "paused verb wheel cannot be selected");
            PressKey(Key.Space);
            Click(game.Hud.Wheel.SlotCenter(Verb.Look), MouseButton.Left);
            await AwaitTest(wheel, "verb wheel works after resuming");
            Check(await wheel == Verb.Look, "verb wheel retains its selection layout");

            var puzzle = game.Hud.Puzzle.Open(PuzzleKind.Lift);
            foreach (var (step, _) in LiftRoute()) PuzzleClick(step);
            PressKey(Key.Space);
            PuzzleClick("submit");
            PuzzleClick("reset");
            PuzzleClick("down");
            var open = new[] { "up", "down", "left", "right" }.First(s =>
            {
                var (dx, dy) = LiftMaze.Step(s);
                return LiftMaze.CanMove(LiftMaze.Target, dx, dy);
            });
            PuzzleKey(open);
            PuzzleDrag(LiftMazeScreen.Center(LiftMaze.Target), new[] { open });
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(game.IsPaused && game.Hud.Puzzle.IsOpen && !puzzle.IsCompleted,
                "Space pause blocks puzzle submission, reset, controls, arrow keys, swipes, and Esc");
            PressKey(Key.Space);
            PuzzleClick("submit");
            await AwaitTest(puzzle, "puzzle resumes with its settings preserved");
            Check(await puzzle, "paused puzzle controls did not change the correct solution");

            // long enough that a slow CI frame cannot finish the fade before the pause lands
            var fade = game.Hud.Fade(1, 2);
            await Observe(0.2);
            PressKey(Key.Space);
            var alpha = game.Hud.FadeAlpha;
            await Observe(1);
            Check(!fade.IsCompleted && game.Hud.FadeAlpha == alpha && game.Hud.PauseVisible,
                $"fade freezes with pause indicator above it (completed {fade.IsCompleted}, alpha {alpha} -> {game.Hud.FadeAlpha}, indicator {game.Hud.PauseVisible})");
            PressKey(Key.Space);
            await AwaitTest(fade, "fade completes after resuming");
            await game.Hud.Fade(0, 0.1);

            PressKey(Key.Escape);
            await Observe(0.1);
            Check(game.Hud.Menu.IsOpen && game.GetTree().Paused && !game.IsPaused, "Esc menu still pauses separately");
            PressKey(Key.Space);
            Check(game.Hud.Menu.IsOpen && game.GetTree().Paused && !game.IsPaused, "Space does not resume the Esc menu");
            PressKey(Key.Escape);
            await Observe(0.1);
            Check(!game.Hud.Menu.IsOpen && !game.GetTree().Paused, "Esc still resumes its own menu");

            game.Hud.ShowTitle(true);
            PressKey(Key.Space);
            Check(!game.IsPaused && !game.GetTree().Paused, "Space does nothing on the title screen");
            game.Hud.ShowTitle(false);
            for (int i = 0; i < 3; i++)
            {
                PressKey(Key.Space);
                Check(game.IsPaused, "repeated toggle pauses");
                PressKey(Key.Space);
                Check(!game.IsPaused && !game.GetTree().Paused, "repeated toggle resumes");
            }
        }
        finally
        {
            if (game.IsPaused) game.TogglePause();
            Engine.TimeScale = timeScale;
        }
    }
}
