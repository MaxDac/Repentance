using Godot;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Player input: clicks, keys, the verb wheel and the held inventory item.</summary>
public partial class Game
{
    /// <summary>Inventory item currently held as the mouse cursor (left click a hotspot to use it there).</summary>
    public string? Carried => _carried;

    public override void _UnhandledInput(InputEvent e)
    {
        if (IsPaused) return;
        if (e.IsActionPressed("ui_cancel"))
        {
            GetViewport().SetInputAsHandled();
            if (Hud.Wheel.IsOpen) Hud.Wheel.Close();
            else if (CanSave && !Hud.Menu.IsOpen) _ = PauseMenu();
            return;
        }
        if (e.IsActionPressed("toggle_inventory") && e is not InputEventKey { Echo: true })
        {
            GetViewport().SetInputAsHandled();
            if (Room != null && !_onTitle && !Hud.Menu.IsOpen && !Hud.Puzzle.IsOpen && !Hud.Wheel.IsOpen &&
                Hud.InterfaceVisible)
                Hud.ShowInventory(!Hud.InventoryOpen);
            return;
        }
        if (e.IsActionPressed("toggle_notepad") && e is not InputEventKey { Echo: true })
        {
            GetViewport().SetInputAsHandled();
            if (Room != null && !_onTitle && !Busy && !Hud.Menu.IsOpen && !Hud.Puzzle.IsOpen && !Hud.Wheel.IsOpen &&
                Hud.InterfaceVisible && GameState.Instance.HasItem(Notes.ItemId) && !Story.Interlude.EleanorPlays(GameState.Instance.HasFlag))
                _ = ItemVerb(Verb.Look, Notes.ItemId);
            return;
        }
        if (e is not InputEventMouseButton { Pressed: true } mb) return;
        if (mb.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        GetViewport().SetInputAsHandled();

        if (_skipSpeech != null)
        {
            _skipSpeech.TrySetResult();
            return;
        }
        if (Busy || Room == null || _onTitle || Hud.Wheel.IsOpen) return;
        var pos = mb.Position;
        var target = Room.HotspotAt(pos);

        if (mb.ButtonIndex == MouseButton.Right)
        {
            if (_carried != null) { SetCarried(null); return; }
            if (target != null) _ = OpenWheel(target, pos);
            return;
        }
        if (_carried != null && target != null)
        {
            var item = _carried;
            SetCarried(null);
            _ = Execute(Verb.UseItem, target, item, pos);
            return;
        }
        _ = Execute(target == null ? Verb.Walk : LeftClickVerb(target), target, null, pos);
    }

    /// <summary>The verb a left click on this hotspot performs; the room may override the usual default.</summary>
    public Verb LeftClickVerb(Hotspot h) => Room?.LeftClickVerb(h) ?? DefaultVerb(h);

    /// <summary>Left click on a hotspot: exits are walked through, people are talked to, the rest is looked at.</summary>
    private static Verb DefaultVerb(Hotspot h) => h switch
    {
        { IsExit: true } => Verb.Walk,
        Actor => Verb.Talk,
        _ => Verb.Look,
    };

    private async Task OpenWheel(Hotspot target, Vector2 pos)
    {
        var verb = await Hud.Wheel.Open(pos, target.Title);
        if (verb is { } v && !Busy && Room != null && target.Visible) await Execute(v, target, null, pos);
    }

    private void SetCarried(string? item)
    {
        _carried = item;
        Hud.SetCursorItem(item);
    }

    private async void OnItemClicked(string item, bool right, Vector2 pos)
    {
        if (IsPaused) return;
        if (_skipSpeech != null) { _skipSpeech.TrySetResult(); return; }
        if (Busy || Hud.Wheel.IsOpen) return;
        if (right)
        {
            SetCarried(null);
            if (await Hud.Wheel.Open(pos, Items.Get(item).Name) is { } verb) await ItemVerb(verb, item);
            return;
        }
        if (_carried == null)
        {
            SetCarried(item);
            Hud.ShowInventory(false);
            return;
        }
        var first = _carried;
        SetCarried(null);
        if (first == item) return;
        await Run(async () =>
        {
            if (!await CombineItems(first, item) && (Room == null || !await Room.OnCombine(first, item)))
                await Say(Pick("That doesn't work.", "I can't see how those go together."));
        });
    }
}
