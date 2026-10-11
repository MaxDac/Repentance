using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Behind the Blue Lantern, after Sal's "word" with Micah. One street lamp that can't make up its mind. Micah is on
/// his knees; Tony the bartender tells him where Eleanor went, then the scene moves on to the convent.
/// </summary>
public partial class Alley : Room
{
    private Sprite2D? _lamp;
    private double _flickerIn;
    private readonly RandomNumberGenerator _rng = new();

    public override void _Ready()
    {
        base._Ready();
        _lamp = GetNodeOrNull<Sprite2D>("Lamp");
    }

    public override void _Process(double delta)
    {
        if (_lamp == null) return;
        _flickerIn -= delta;
        if (_flickerIn > 0) return;
        // mostly on, with short stuttering blackouts
        _lamp.Visible = !_lamp.Visible;
        _flickerIn = _lamp.Visible ? _rng.RandfRange(0.4f, 2.6f) : _rng.RandfRange(0.04f, 0.3f);
    }

    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("alley_done")) return;
        await Game.Run(async () =>
        {
            Player.SetPose("micah_kneel");
            await Wait(1.2);
            await Talk("alley");
            // back inside through the club's back door
            if (FindActor("sal") is { } sal) _ = sal.MoveTo(new Vector2(322, 198), 50);
            if (FindActor("bartender") is { } tony) await tony.MoveTo(new Vector2(338, 196), 45);
            await Wait(0.4);
            if (!await Player.PlayPose("micah_kneel_rise")) return;
            Player.SetPose(null);
            Player.Face(Facing.Right);
            await Say("A convent. Of all the places to hide a woman like that.");
            State.SetFlag("alley_done");
            await Game.ChangeRoom("convent_corridor", "start");
        });
    }
}
