using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// A motel room, that same night. Micah gets dressed while Eleanor lies under the sheet. They agree never to see each
/// other again. End of the first act of the journal: back to the attic.
/// </summary>
public partial class MotelNight : Room
{
    private PosePlayback _eleanor = null!;
    private Sprite2D _figure = null!;
    private Voice _voice = null!;

    public override void _Ready()
    {
        base._Ready();
        _figure = GetNode<Sprite2D>("EleanorFigure");
        _voice = GetNode<Voice>("Eleanor");
        _eleanor = new PosePlayback(_figure);
        _eleanor.Hold("eleanor_sheet_rise", last: State.HasFlag("motel_night_done"));
        UpdateVoice();
    }

    private void UpdateVoice()
    {
        // On the bed she is behind the near rail; once her feet reach the floor she stands in front of it.
        _figure.ZIndex = _eleanor.Frame >= 4 ? 2 : 0;
        _voice.GlobalPosition = _figure.ToGlobal(_eleanor.HeadOffset - new Vector2(0, 7));
    }

    public override void _Process(double delta)
    {
        _eleanor.Process(delta);
        UpdateVoice();
    }

    public override void _ExitTree()
    {
        _eleanor.Clear();
        base._ExitTree();
    }

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("motel_night_done")) return;
        await Game.Run(async () =>
        {
            await Wait(1.0);
            await Talk("motel_night");
            if (!await _eleanor.Play("eleanor_sheet_rise")) return;
            State.SetFlag("motel_night_done");
            await Wait(0.6);
            await Game.Hud.Fade(1, 1.5);
            State.SetFlag("attic_night");
            await Game.ChangeRoom("attic", "night");
        });
    }
}
