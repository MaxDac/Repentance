using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Smoke test: plays the whole demo by itself, saving screenshots to screenshots/ and printing
/// AUTOPLAY OK / AUTOPLAY FAILED. Run with: godot -- --autoplay [--clock=fast|normal]
/// </summary>
public partial class AutoPlay : Harness
{
    private string _marker = "AUTOPLAY";
    protected override string Marker => _marker;
    private readonly HashSet<string> _shotKnots = new();
    private readonly Dictionary<string, int> _poseCounts = new();
    private readonly Dictionary<PosePlayback, int> _lastPoseFrame = new();
    private string[] _prefer = Array.Empty<string>();
    private readonly Dictionary<string, string[]> _offered = new();
    private readonly List<(string Knot, string[] Options)> _offerLog = new();
    private bool _theEndShot;
    private bool _vowsShot;
    private string _act3Ink = "";
    private int _crossOffers;
    private bool? _insetAtCaughtChoice;
    private bool? _insetAtBeatenChoice;
    private bool? _insetAtStreetChoice;
    private string[] _act3Flags = Array.Empty<string>();
    private string[] _act3Items = Array.Empty<string>();
    private CloseUp? _closeUpAtRoadChoice;

    public async Task Run(Game game)
    {
        if (OS.GetCmdlineUserArgs().Contains("--settings-test")) _marker = "SETTINGS TEST";
        PosePlayback.FrameObserver = ObservePose;
        PrepareScreenshots();
        if (!Begin(game, "autoplay"))
        {
            Finish();
            return;
        }
        DialogueManager.Instance.AutoChoose = async (knot, options) =>
        {
            GD.Print($"[autoplay] {knot}: {string.Join(" | ", options)}");
            if (_shotKnots.Add(knot))
            {
                _ = game.Hud.ShowChoices(DialogueManager.Instance.ShownChoices);
                CheckChoiceBar(game, knot, options);
                await Shot($"choices_{knot.Replace('.', '_')}");
                game.Hud.HideChoices();
            }
            else CheckChoiceBar(game, knot, options, drawn: false);
            _offered[knot] = options.ToArray();
            _offerLog.Add((knot, options.ToArray()));
            if (knot == "caleb_cross") _crossOffers++;
            if (knot == "club_caught") _insetAtCaughtChoice = game.Hud.InsetVisible;
            if (knot == "beaten_choice") _insetAtBeatenChoice = game.Hud.InsetVisible;
            if (knot == "street_choice") _insetAtStreetChoice = game.Hud.InsetVisible;
            if (knot == "eleanor_fire_escape")
            {
                _closeUpAtRoadChoice = game.Hud.CurrentCloseUp;
                Check(!game.Hud.InsetVisible && !game.Hud.InsetDrawn,
                    "the convent panel is completely removed before the compensation choice");
            }
            foreach (var want in _prefer)
            {
                for (int i = 0; i < options.Count; i++)
                    if (options[i].Contains(want)) return i;
            }
            return 0;
        };

        try
        {
#if TOOLS
            InheritanceContractTest();
            InkResetTest();
            if (_failures.Count != 0) return;
#endif
            var gs = GameState.Instance;
            await ContentSettingsTest(game);
            if (OS.GetCmdlineUserArgs().Contains("--settings-test")) return;
            bool autosave = game.AutosaveEnabled;
            game.AutosaveEnabled = false;
            await StoryDialogueTest(game);
            await PuzzleRecoveryTest(game);
            await ActThreePuzzleRecoveryTest(game);
            await TheEndHoldTest(game);
            foreach (var slot in SaveSystem.AllSlots) SaveSystem.Delete(slot);
            gs.Reset();
            DialogueManager.Instance.ResetInk();

            await PlayPrologue(game, gs, autosave);
            await PlayActOne(game, gs);
            await PlayActTwo(game, gs);
            await PlayActThree(game, gs);
            await PlayOtherEndings(game, gs);
        }
        catch (Exception ex)
        {
            _failures.Add(ex.ToString());
        }
        finally
        {
            PosePlayback.FrameObserver = null;
            Finish();
        }
    }

    private async Task AwaitTest(Task task, string description)
    {
        for (int i = 0; i < 100 && !task.IsCompleted; i++) await Observe(0.05);
        if (!task.IsCompleted) throw new TimeoutException(description);
        await task;
        Check(true, description);
    }
}
