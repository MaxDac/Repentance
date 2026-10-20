using System.Threading.Tasks;

namespace Repentance;

/// <summary>Micah showing Eleanor's photograph to someone and putting it away again.</summary>
public partial class Room
{
    private const string ShowPhotoPose = "micah_show_photo";
    private const string ShowPhotoBackPose = "micah_show_photo_back";

    /// <summary>
    /// Micah takes Eleanor's photograph out of his coat and holds it out to <paramref name="actorId"/>; the last frame
    /// stays held while they answer. With his back to the screen only his flexing arm shows. Without the photo (only
    /// the notepad's description) there's nothing to show.
    /// </summary>
    protected async Task ShowPhoto(string actorId)
    {
        if (!State.HasItem("photo")) return;
        if (FindActor(actorId) is { } actor) Player.FaceTowards(actor.GlobalPosition);
        await Player.PlayPose(Player.Facing == Facing.Up ? ShowPhotoBackPose : ShowPhotoPose);
    }

    /// <summary>The photograph goes back inside his coat and Micah is himself again.</summary>
    protected async Task PocketPhoto()
    {
        var pocket = Player.PoseName switch
        {
            ShowPhotoPose => "micah_pocket_photo",
            ShowPhotoBackPose => "micah_pocket_photo_back",
            _ => null,
        };
        if (pocket != null && await Player.PlayPose(pocket)) Player.SetPose(null);
    }
}
