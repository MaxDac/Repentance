using Godot;

namespace Repentance;

/// <summary>Touch buttons for what the keyboard does on a desktop: the pause menu (Esc) and the notepad (N).</summary>
public partial class Hud
{
    private Control _touchButtons = null!;
    private Button _touchNotes = null!;

    public bool TouchButtonsVisible => _touchButtons.IsVisibleInTree();
    public Vector2 TouchMenuCenter => _touchButtons.GetChild<Button>(0).GetGlobalRect().GetCenter();
    public Vector2 TouchNotesCenter => _touchNotes.GetGlobalRect().GetCenter();

    private void BuildTouchButtons()
    {
        _touchButtons = new Control { MouseFilter = Control.MouseFilterEnum.Ignore, Visible = false };
        _interface.AddChild(_touchButtons);
        TouchButton("MENU", new Vector2(4, 250), Key.Escape);
        _touchNotes = TouchButton("NOTES", new Vector2(42, 250), Key.N);
    }

    private Button TouchButton(string text, Vector2 pos, Key key)
    {
        var b = new Button { Text = text, Position = pos, Size = new Vector2(36, 16), FocusMode = Control.FocusModeEnum.None };
        b.Pressed += () => Game.Instance.Touch.PressKey(key);
        _touchButtons.AddChild(b);
        return b;
    }

    private void UpdateTouchButtons()
    {
        _touchButtons.Visible = TouchInput.UsingTouch;
        _touchNotes.Visible = GameState.Instance.HasItem(Notes.ItemId);
        _cursor.Visible = !TouchInput.UsingTouch;
    }
}
