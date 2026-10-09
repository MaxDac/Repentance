using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>The cathedral interior: a little peace, and a lot of guilt.</summary>
public partial class Church : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_church_interior")) return;
        State.SetFlag("seen_church_interior");
        await Game.Run(() => Say("The nave swallowed the street noise whole. Even my footsteps sounded guilty in here."));
    }
}
