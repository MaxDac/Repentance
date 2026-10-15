using Godot;
using GodotInk;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>
/// Runs Ink conversations. All dialogue lives in res://dialogue/repentance.ink, one knot per
/// conversation. Lines are written "SPEAKER: text" (speaker = actor/voice Id; MICAH or DANIEL for the player).
/// "THOUGHT: text" is Micah's journal narration (top of the screen, nobody speaks it).
/// Choice text is spoken by the player; wrap it in parentheses, e.g. "(Leave)", to keep them quiet.
/// Ink can call give_item/take_item/has_item/set_flag/has_flag to touch the game state.
/// </summary>
public partial class DialogueManager : Node
{
    public const string StoryPath = "res://dialogue/repentance.ink";
    public static DialogueManager Instance { get; private set; } = null!;

    private InkStory? _story;

    /// <summary>Test hook: when set, picks dialogue choices instead of the player (knot, options) => index.</summary>
    public Func<string, IReadOnlyList<string>, Task<int>>? AutoChoose;
    /// <summary>Raised with the talk knot and every option shown, before one is picked (choice coverage).</summary>
    public event Action<string, IReadOnlyList<string>>? ChoicesOffered;

    public override void _EnterTree() => Instance = this;

    private InkStory Story
    {
        get
        {
            if (_story != null) return _story;
            _story = GD.Load<InkStory>(StoryPath);
            var gs = GameState.Instance;
            _story.BindExternalFunction("has_item", new Func<string, Variant>(id => gs.HasItem(id)));
            _story.BindExternalFunction("has_flag", new Func<string, Variant>(f => gs.HasFlag(f)));
        _story.BindExternalFunction("knows_note", new Func<string, Variant>(id => gs.HasItem(Notes.ItemId) && Notes.Known(id, gs.HasFlag)));
            _story.BindExternalFunction("cash_amount", new Func<Variant>(() => gs.HasItem("dollar") ? CashRules.Balance(gs.HasFlag) : 0));
            _story.BindExternalFunction("give_item", new Action<string>(gs.GiveItem));
            _story.BindExternalFunction("take_item", new Action<string>(gs.TakeItem));
            _story.BindExternalFunction("set_flag", new Action<string>(f => gs.SetFlag(f)));
            return _story;
        }
    }

    /// <summary>Plays the conversation starting at <paramref name="knot"/> until it runs out.</summary>
    public Task Talk(string knot) => Game.Instance.Run(() => TalkInner(knot));

    private async Task TalkInner(string knot)
    {
        var game = Game.Instance;
        var story = Story;
        story.ChoosePathString(knot);
        while (true)
        {
            while (story.CanContinue)
            {
                var line = story.Continue().Trim();
                if (line.Length == 0) continue;
                var (speaker, text) = Parse(line);
                // "none" fades out the inset; "none_now" removes it before the next line or choice.
                if (speaker == "INSET")
                {
                    if (text == "none") game.Hud.HideCloseUp();
                    else if (text == "none_now") game.Hud.HideCloseUp(0);
                    else game.Hud.ShowCloseUp(CloseUps.Get(text));
                    continue;
                }
                // "IMAGE: name" shows res://assets/art/ui/name.png full screen until clicked
                if (speaker == "IMAGE")
                {
                    await game.Hud.ShowImage(GD.Load<Texture2D>($"res://assets/art/ui/{text}.png"));
                    continue;
                }
                // "CUE: name" hands the stage to the room (Room.OnCue) and resumes when it is done
                if (speaker == "CUE")
                {
                    if (game.Room != null) await game.Room.OnCue(text);
                    continue;
                }
                // "THOUGHT: text" is Micah's journal narration, shown at the top of the screen
                if (speaker == "THOUGHT")
                {
                    await game.Think(text);
                    continue;
                }
                await game.Say(speaker, text);
            }
            var choices = story.CurrentChoices;
            if (choices.Count == 0) break;
            var labels = choices.Select(c => c.Text.Trim()).ToList();
            ChoicesOffered?.Invoke(knot, labels);
            int picked = AutoChoose != null ? await AutoChoose(knot, labels) : await game.Hud.ShowChoices(labels);
            var said = labels[picked];
            story.ChooseChoiceIndex(choices[picked].Index);
            if (!said.StartsWith('(')) await game.Say(game.Player, said);
        }
    }

    private static (string speaker, string text) Parse(string line)
    {
        int colon = line.IndexOf(':');
        if (colon > 0 && colon < 16 && line[..colon].All(ch => char.IsUpper(ch) || ch == '_'))
            return (line[..colon], line[(colon + 1)..].Trim());
        return ("MICAH", line);
    }

    /// <summary>Reads an Ink variable (handy for room scripts).</summary>
    public Variant Get(string variable) => Story.FetchVariable(variable);

    /// <summary>Ink runtime state (visit counts, variables) as JSON, or "" if no conversation has run yet.</summary>
    public string SaveInk() => _story?.SaveState() ?? "";

    public void LoadInk(string json)
    {
        if (string.IsNullOrEmpty(json)) ResetInk();
        else Story.LoadState(json);
    }

    public void ResetInk() => _story?.ResetState();
}
