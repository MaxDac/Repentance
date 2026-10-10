using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

public enum MenuAction { Resume, NewGame, Load, QuitToTitle }

public readonly record struct MenuResult(MenuAction Action, SaveData? Save = null);

/// <summary>
/// Title menu (Continue / New game / Load) and Esc pause menu (Resume / Save / Load / Quit to title),
/// including the save-slot list. Runs while the tree is paused.
/// </summary>
public partial class GameMenu : Control
{
    private const int RowH = 13, PanelW = 300;
    private static readonly Color DisabledColor = new("5a4a30");

    private ColorRect _dim = null!;
    private Panel _panel = null!;
    private Label _heading = null!;
    private VBoxContainer _list = null!;
    private Label _status = null!;
    private TaskCompletionSource<MenuResult>? _tcs;
    private Action? _back;
    private bool _title;

    public bool IsOpen => Visible;

    public override void _Ready()
    {
        SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        MouseFilter = MouseFilterEnum.Stop;
        ProcessMode = ProcessModeEnum.Always;
        Visible = false;

        _dim = new ColorRect { Color = new Color(0, 0, 0, 0.55f), MouseFilter = MouseFilterEnum.Ignore };
        _dim.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        AddChild(_dim);

        var box = new StyleBoxFlat { BgColor = new Color(0.04f, 0.03f, 0.06f, 0.9f), BorderColor = new Color("3a2814") };
        box.SetBorderWidthAll(1);
        _panel = new Panel { MouseFilter = MouseFilterEnum.Ignore };
        _panel.AddThemeStyleboxOverride("panel", box);
        AddChild(_panel);

        _heading = Hud.MakeOutlinedLabel(Hud.VerbHover);
        _heading.HorizontalAlignment = HorizontalAlignment.Center;
        AddChild(_heading);

        _list = new VBoxContainer();
        _list.AddThemeConstantOverride("separation", 1);
        AddChild(_list);

        _status = Hud.MakeOutlinedLabel(Hud.ChoiceColor);
        _status.HorizontalAlignment = HorizontalAlignment.Center;
        AddChild(_status);
    }

    public Task<MenuResult> OpenTitle()
    {
        _title = true;
        _dim.Visible = false;
        _status.Text = "";
        TitlePage();
        return Open();
    }

    public Task<MenuResult> OpenPause()
    {
        _title = false;
        _dim.Visible = true;
        _status.Text = "";
        PausePage();
        return Open();
    }

    private Task<MenuResult> Open()
    {
        Visible = true;
        _tcs = new TaskCompletionSource<MenuResult>();
        return _tcs.Task;
    }

    private void Finish(MenuResult result)
    {
        Visible = false;
        _tcs?.TrySetResult(result);
    }

    public override void _Input(InputEvent e)
    {
        if (!Visible || !e.IsActionPressed("ui_cancel")) return;
        GetViewport().SetInputAsHandled();
        _back?.Invoke();
    }

    /// <summary>Clicks a menu entry by its label (used by the autoplay test).</summary>
    public bool Press(string label)
    {
        var b = _list.GetChildren().OfType<Button>().FirstOrDefault(x => x.Text.StartsWith(label) && !x.Disabled);
        b?.EmitSignal(BaseButton.SignalName.Pressed);
        return b != null;
    }

    // ------------------------------------------------------------------ pages

    private void TitlePage()
    {
        var latest = SaveSystem.Latest();
        bool any = latest != null;
        Page("", 142, null,
            ("Continue", any, () => Finish(new MenuResult(MenuAction.Load, latest))),
            ("New game", true, () => Finish(new MenuResult(MenuAction.NewGame))),
            ("Load game", any, () => SlotsPage(saving: false)));
    }

    private void PausePage()
    {
        Page("Paused", -1, () => Finish(new MenuResult(MenuAction.Resume)),
            ("Resume", true, () => Finish(new MenuResult(MenuAction.Resume))),
            ("Save game", Game.Instance.CanSave, () => SlotsPage(saving: true)),
            ("Load game", true, () => SlotsPage(saving: false)),
            ("Quit to title", true, () => Finish(new MenuResult(MenuAction.QuitToTitle))));
    }

    private void SlotsPage(bool saving)
    {
        Action back = _title ? TitlePage : PausePage;
        _status.Text = "";
        var slots = saving
            ? Enumerable.Range(0, SaveSystem.ManualSlots).Select(SaveSystem.ManualSlot)
            : SaveSystem.AllSlots;
        var rows = new List<(string, bool, Action)>();
        foreach (var slot in slots)
        {
            var data = SaveSystem.Read(slot);
            var label = $"{SlotName(slot)}: {Describe(slot, data)}";
            if (saving)
                rows.Add((label, true, () =>
                {
                    bool ok = Game.Instance.SaveToSlot(slot);
                    _status.Text = ok ? $"Saved to {SlotName(slot)}." : "Couldn't save the game.";
                    PausePage();
                }));
            else
                rows.Add((label, data != null, () => Finish(new MenuResult(MenuAction.Load, data))));
        }
        rows.Add(("Back", true, back));
        Page(saving ? "Save game" : "Load game", -1, back, rows.ToArray());
    }

    private static string SlotName(string slot) =>
        slot == SaveSystem.AutosaveSlot ? "Autosave" : "Slot " + slot[4..];

    private static string Describe(string slot, SaveData? data)
    {
        if (data == null) return SaveSystem.Exists(slot) ? "Incompatible" : "Empty";
        var title = data.RoomTitle != "" ? data.RoomTitle : data.Room;
        return $"{title}, {data.SavedAtUtc.ToLocalTime():d MMM HH:mm}";
    }

    /// <summary>Lays out a page. <paramref name="top"/> &lt; 0 centres it vertically.</summary>
    private void Page(string heading, float top, Action? back, params (string text, bool enabled, Action onPress)[] rows)
    {
        _back = back;
        foreach (var c in _list.GetChildren())
        {
            _list.RemoveChild(c);
            c.QueueFree();
        }
        foreach (var (text, enabled, onPress) in rows)
            _list.AddChild(MakeButton(text, enabled, onPress));

        bool hasHeading = heading != "";
        float headH = hasHeading ? RowH + 4 : 0;
        float statusH = _status.Text != "" ? RowH : 0;
        float h = headH + rows.Length * (RowH + 1) + statusH + 8;
        float y = top >= 0 ? top : Mathf.Round((Hud.ScreenH - h) / 2);
        float x = (Hud.ScreenW - PanelW) / 2f;

        _panel.Position = new Vector2(x, y);
        _panel.Size = new Vector2(PanelW, h);
        _heading.Visible = hasHeading;
        _heading.Text = heading;
        _heading.Position = new Vector2(x, y + 4);
        _heading.Size = new Vector2(PanelW, RowH);
        _list.Position = new Vector2(x + 4, y + 4 + headH);
        _list.Size = new Vector2(PanelW - 8, rows.Length * (RowH + 1));
        _status.Visible = statusH > 0;
        _status.Position = new Vector2(x, y + h - RowH - 3);
        _status.Size = new Vector2(PanelW, RowH);
    }

    private static Button MakeButton(string text, bool enabled, Action onPress)
    {
        var b = new Button
        {
            Text = text,
            Flat = true,
            Disabled = !enabled,
            FocusMode = FocusModeEnum.None,
            CustomMinimumSize = new Vector2(PanelW - 8, RowH),
            ClipText = true,
        };
        b.AddThemeColorOverride("font_color", Hud.VerbColor);
        b.AddThemeColorOverride("font_hover_color", Hud.VerbHover);
        b.AddThemeColorOverride("font_pressed_color", Colors.White);
        b.AddThemeColorOverride("font_hover_pressed_color", Colors.White);
        b.AddThemeColorOverride("font_disabled_color", DisabledColor);
        var empty = new StyleBoxEmpty();
        foreach (var s in new[] { "normal", "hover", "pressed", "hover_pressed", "focus", "disabled" })
            b.AddThemeStyleboxOverride(s, empty);
        // deferred: pressing a row rebuilds the page, which frees this very button
        b.Pressed += () => Callable.From(onPress).CallDeferred();
        return b;
    }
}
