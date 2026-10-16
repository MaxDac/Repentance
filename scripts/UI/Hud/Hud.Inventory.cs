using Godot;
using System;

namespace Repentance;

/// <summary>The satchel button and the paged inventory case.</summary>
public partial class Hud
{
    private void BuildSatchel()
    {
        _satchel = new TextureButton
        {
            TextureNormal = GD.Load<Texture2D>("res://assets/art/ui/satchel.png"),
            Position = SatchelPos,
            FocusMode = Control.FocusModeEnum.None,
            TooltipText = "",
        };
        _satchel.Pressed += () => ShowInventory(!_inventory.Visible);
        _satchel.MouseEntered += () => _satchel.Modulate = new Color(1.3f, 1.2f, 1f);
        _satchel.MouseExited += () => _satchel.Modulate = Colors.White;
        _interface.AddChild(_satchel);
    }

    private void BuildInventory(Control root)
    {
        // full-screen catcher: clicking outside the case closes it
        _inventory = new Control { Visible = false, MouseFilter = Control.MouseFilterEnum.Stop };
        _inventory.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _inventory.GuiInput += e =>
        {
            if (e is InputEventMouseButton { Pressed: true }) ShowInventory(false);
        };
        root.AddChild(_inventory);
        _inventory.AddChild(new TextureRect
        {
            Texture = GD.Load<Texture2D>("res://assets/art/ui/inventory.png"),
            Position = InvPos,
            MouseFilter = Control.MouseFilterEnum.Stop,
        });

        var normal = new StyleBoxFlat { BgColor = new Color("140c08"), BorderColor = new Color("3a2814") };
        normal.SetBorderWidthAll(1);
        var hover = new StyleBoxFlat { BgColor = new Color("2a1c10"), BorderColor = new Color("d8b050") };
        hover.SetBorderWidthAll(1);
        for (int r = 0; r < InvRows; r++)
        for (int c = 0; c < InvCols; c++)
        {
            var b = new Button
            {
                Position = InvPos + new Vector2(10 + c * SlotW, 7 + r * SlotH),
                Size = new Vector2(SlotW - 2, SlotH - 2),
                FocusMode = Control.FocusModeEnum.None,
                IconAlignment = HorizontalAlignment.Center,
                ButtonMask = MouseButtonMask.Left | MouseButtonMask.Right,
            };
            b.AddThemeStyleboxOverride("normal", normal);
            b.AddThemeStyleboxOverride("hover", hover);
            b.AddThemeStyleboxOverride("pressed", hover);
            b.AddThemeStyleboxOverride("disabled", normal);
            b.AddThemeStyleboxOverride("focus", new StyleBoxEmpty());
            var slot = _slots.Count;
            b.GuiInput += e => OnSlotInput(slot, e);
            b.MouseEntered += () => ItemHovered?.Invoke(ItemInSlot(slot));
            b.MouseExited += () => ItemHovered?.Invoke(null);
            _inventory.AddChild(b);
            _slots.Add(b);
        }
        _previousPage = new Button { Text = "<", Position = new Vector2(110, 249), Size = new Vector2(30, 18), FocusMode = Control.FocusModeEnum.None };
        _nextPage = new Button { Text = ">", Position = new Vector2(340, 249), Size = new Vector2(30, 18), FocusMode = Control.FocusModeEnum.None };
        _pageLabel = MakeOutlinedLabel(VerbHover);
        _pageLabel.Position = new Vector2(197, 253);
        _previousPage.Pressed += () => { _inventoryPage--; ItemHovered?.Invoke(null); RefreshInventory(); };
        _nextPage.Pressed += () => { _inventoryPage++; ItemHovered?.Invoke(null); RefreshInventory(); };
        _inventory.AddChild(_previousPage);
        _inventory.AddChild(_nextPage);
        _inventory.AddChild(_pageLabel);
    }

    private string? ItemInSlot(int slot)
    {
        var inv = GameState.Instance.Inventory;
        slot += _inventoryPage * InvCols * InvRows;
        return slot < inv.Count ? inv[slot] : null;
    }

    /// <summary>Screen position of an inventory slot (used by the autoplay test).</summary>
    public Vector2 SlotCenter(int slot) => _slots[slot % _slots.Count].Position + _slots[slot % _slots.Count].Size / 2;
    public Vector2 InventoryPageCenter(bool next) => (next ? _nextPage : _previousPage).GetGlobalRect().GetCenter();

    public Vector2 SatchelCenter => SatchelPos + _satchel.Size / 2;
    public bool SatchelVisible => _satchel.Visible;

    private void OnSlotInput(int slot, InputEvent e)
    {
        if (e is not InputEventMouseButton { Pressed: true } mb) return;
        _slots[slot].AcceptEvent();
        if (ItemInSlot(slot) is not { } item || mb.ButtonIndex is not (MouseButton.Left or MouseButton.Right)) return;
        ItemClicked?.Invoke(item, mb.ButtonIndex == MouseButton.Right, mb.GlobalPosition);
    }

    public void RefreshInventory()
    {
        int pages = Math.Max(1, (GameState.Instance.Inventory.Count + _slots.Count - 1) / _slots.Count);
        _inventoryPage = Math.Clamp(_inventoryPage, 0, pages - 1);
        _previousPage.Disabled = _inventoryPage == 0;
        _nextPage.Disabled = _inventoryPage == pages - 1;
        _pageLabel.Text = $"Page {_inventoryPage + 1}/{pages}";
        for (int s = 0; s < _slots.Count; s++)
        {
            var id = ItemInSlot(s);
            _slots[s].Icon = id == null ? null : GD.Load<Texture2D>(Items.Get(id).IconPath);
        }
        _satchel.Disabled = false;
        _satchel.Visible = SatchelAllowed;
    }

    // Eleanor carries nothing of Micah's: in the interludes the satchel holds only what she finds there, and in her
    // coda and epilogue she has none.
    private static bool SatchelAllowed
    {
        get
        {
            var has = (Func<string, bool>)GameState.Instance.HasFlag;
            return !Story.Interlude.EleanorPlays(has) || Story.Interlude.SatchelOpen(has);
        }
    }

    public void ShowInventory(bool show)
    {
        if (show && (Game.Instance.Busy || !SatchelAllowed)) return;
        _inventory.Visible = show;
        if (!show) ItemHovered?.Invoke(null);
    }
}
