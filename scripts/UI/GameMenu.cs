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
    private bool _onSettings;
    private GameSettings? _settings;

    public bool IsOpen => Visible;

    /// <summary>The status line under the entries (used by the autoplay test).</summary>
    public string Status => _status.Text;

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

    /// <summary>True if the current page shows an entry starting with this label (used by the autoplay test).</summary>
    public bool HasEntry(string label) =>
        _list.GetChildren().OfType<Button>().Any(x => x.Text.StartsWith(label) && !x.IsQueuedForDeletion());

    // ------------------------------------------------------------------ pages

    private void TitlePage()
    {
        var latest = SaveSystem.Latest();
        bool any = latest != null;
        var rows = new List<(string, bool, Action)>
        {
            ("Continue", any, () => Finish(new MenuResult(MenuAction.Load, latest))),
            ("New game", true, () => Finish(new MenuResult(MenuAction.NewGame))),
            ("Load game", any, () => SlotsPage(saving: false)),
            ("Settings", true, SettingsPage),
        };
        AddRestartSound(rows);
        Page("", 142, null, rows.ToArray());
    }

    public const string RestartSoundLabel = "Restart sound";
    public const string SoundLostText = "No sound device was found, so the game is silent.";

    /// <summary>When Godot fell back to its silent driver at start, offers the relaunch that brings sound back and says
    /// why (unless the page already has something to report).</summary>
    private void AddRestartSound(List<(string, bool, Action)> rows)
    {
        if (!Game.Instance.SoundLost) return;
        rows.Add((RestartSoundLabel, true, Game.Instance.RestartSound));
        if (_status.Text == "") _status.Text = SoundLostText;
    }

    private void PausePage()
    {
        Page("Paused", -1, () => Finish(new MenuResult(MenuAction.Resume)),
            ("Resume", true, () => Finish(new MenuResult(MenuAction.Resume))),
            ("Save game", Game.Instance.CanSave, () => SlotsPage(saving: true)),
            ("Load game", true, () => SlotsPage(saving: false)),
            ("Settings", true, SettingsPage),
            ("Quit to title", true, () => Finish(new MenuResult(MenuAction.QuitToTitle))));
    }

    private void SettingsPage()
    {
        var settings = Game.Instance.Settings;
        Action back = _title ? TitlePage : PausePage;
        var rows = new List<(string, bool, Action)>
        {
            ($"Nudity: {(settings.NudityEnabled ? "On" : "Off")}", true, () =>
            {
                _status.Text = settings.SetNudity(!settings.NudityEnabled) ? "" : "Couldn't save settings.";
                SettingsPage();
            }),
        };
        // a phone is always full screen
        if (!OS.HasFeature("mobile"))
            rows.Add(($"Full screen: {(settings.Fullscreen ? "On" : "Off")}", true, () =>
            {
                _status.Text = settings.SetFullscreen(!settings.Fullscreen) ? "" : "Couldn't save settings.";
                SettingsPage();
            }));
        rows.Add(($"{EffectsLabel}: {settings.EffectsVolume}%", true, () => StepEffects(up: true)));
        rows.Add(($"{MusicLabel}: {settings.MusicVolume}%", true, () => StepMusic(up: true)));
        AddRestartSound(rows);
        rows.Add(("Back", true, () => { _status.Text = ""; back(); }));
        Page("Settings", -1, back, rows.ToArray());
        OnAltPress(EffectsLabel, () => StepEffects(up: false));
        OnAltPress(MusicLabel, () => StepMusic(up: false));
        _onSettings = true;
    }

    private const string EffectsLabel = "Effects volume";
    private const string MusicLabel = "Music volume";

    /// <summary>Like <see cref="StepEffects"/>; the music, if any is playing, keeps going under the menu as a preview.</summary>
    private void StepMusic(bool up)
    {
        var settings = Game.Instance.Settings;
        _status.Text = settings.SetMusicVolume(GameSettings.CycleVolume(settings.MusicVolume, up))
            ? "Left click: louder. Right click: quieter." : "Couldn't save settings.";
        SettingsPage();
    }

    /// <summary>Left click turns the effects up a step, right click down; both wrap around between 0% and 100%.</summary>
    private void StepEffects(bool up)
    {
        var settings = Game.Instance.Settings;
        _status.Text = settings.SetEffectsVolume(GameSettings.CycleVolume(settings.EffectsVolume, up))
            ? "Left click: louder. Right click: quieter." : "Couldn't save settings.";
        Game.Instance.Sfx.Preview();
        SettingsPage();
    }

    private readonly Dictionary<Button, Action> _altPress = new();

    /// <summary>Gives the row starting with <paramref name="label"/> a right-click action.</summary>
    private void OnAltPress(string label, Action action)
    {
        var b = _list.GetChildren().OfType<Button>().First(x => x.Text.StartsWith(label) && !x.IsQueuedForDeletion());
        _altPress[b] = action;
        b.GuiInput += e =>
        {
            if (e is not InputEventMouseButton { Pressed: true, ButtonIndex: MouseButton.Right } || b.Disabled) return;
            b.AcceptEvent();
            Callable.From(action).CallDeferred();
        };
        b.TreeExiting += () => _altPress.Remove(b);
    }

    /// <summary>Right-clicks a menu entry by its label (used by the autoplay test).</summary>
    public bool PressAlt(string label)
    {
        var b = _list.GetChildren().OfType<Button>().FirstOrDefault(x => x.Text.StartsWith(label) && !x.Disabled &&
            !x.IsQueuedForDeletion());
        if (b == null || !_altPress.TryGetValue(b, out var action)) return false;
        Callable.From(action).CallDeferred();
        return true;
    }

    /// <summary>Keeps the settings page in sync when a setting changes elsewhere (e.g. the F11 shortcut).</summary>
    public void BindSettings(GameSettings settings)
    {
        if (_settings != null) _settings.Changed -= OnSettingsChanged;
        _settings = settings;
        _settings.Changed += OnSettingsChanged;
    }

    public override void _ExitTree()
    {
        if (_settings != null) _settings.Changed -= OnSettingsChanged;
    }

    private void OnSettingsChanged()
    {
        if (Visible && _onSettings) Callable.From(() => { if (Visible && _onSettings) SettingsPage(); }).CallDeferred();
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
                    if (SaveSystem.Exists(slot)) OverwritePage(slot, data);
                    else SaveTo(slot);
                }));
            else
                rows.Add((label, data != null, () => Finish(new MenuResult(MenuAction.Load, data))));
        }
        rows.Add(("Back", true, back));
        Page(saving ? "Save game" : "Load game", -1, back, rows.ToArray());
    }

    /// <summary>Asks before replacing the save already in <paramref name="slot"/>; No or Esc returns to the slot list.</summary>
    private void OverwritePage(string slot, SaveData? data)
    {
        Action back = () => SlotsPage(saving: true);
        _status.Text = Describe(slot, data);
        Page($"Overwrite {SlotName(slot)}?", -1, back,
            ("Yes, overwrite", true, () => SaveTo(slot)),
            ("No", true, back));
    }

    private void SaveTo(string slot)
    {
        bool ok = Game.Instance.SaveToSlot(slot);
        _status.Text = ok ? $"Saved to {SlotName(slot)}." : "Couldn't save the game.";
        PausePage();
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
        _onSettings = false;
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
