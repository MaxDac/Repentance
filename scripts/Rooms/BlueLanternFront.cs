using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Rizzo's Flowers on State Street: the florist front of the Blue Lantern. The cold-room door has a speaking grille,
/// and the man behind it only opens for a blue carnation in the buttonhole. White carnations from the bucket,
/// dyed with the bluing on the sidewalk shelf, do the job. Sal's password and bribe inside are unchanged.
/// </summary>
public partial class BlueLanternFront : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_blue_lantern_front")) return;
        State.SetFlag("seen_blue_lantern_front");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("State Street again, and the rain hasn't let up. The matchbook says Blue Lantern. The sign says Rizzo's Flowers.");
            await Think("Closed at this hour, but somebody's still taking deliveries round the cold room.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("grille" or "cold_door", Verb.Walk or Verb.Hand) when State.HasFlag("grille_opened"):
                await Say("The hatch knows my lapel now. The door swings open before I knock.");
                await Game.ChangeRoom("speakeasy", "door");
                return true;
            case ("grille" or "cold_door", Verb.Hand or Verb.Talk):
                await Say("I rap on the grille. The slot opens, an eye drops to my lapel, and the slot shuts again.");
                await Say("No blue in my buttonhole, no hatch.");
                return true;
            case ("grille" or "cold_door", Verb.UseItem) when item == "blue_carnation" && !State.HasFlag("grille_opened"):
                await Say("Blue carnation in the buttonhole. I rap on the grille and stand where the eye can see it.");
                State.TakeItem("blue_carnation");
                State.SetFlag("grille_opened");
                await Say("The slot looks. The slot considers. Then a bolt slides back and the cold-room door sighs open.");
                await Game.ChangeRoom("speakeasy", "door");
                return true;
            case ("grille" or "cold_door", Verb.UseItem) when item == "carnation":
                await Say("A white one gets a long look and a shut slot. The chalkboard said blue. There's a bottle of bluing on the shelf.");
                return true;
            case ("grille" or "cold_door", Verb.UseItem) when item == "lockpick":
                await Say("No keyhole. Whoever's behind that grille is the lock.");
                return true;
            case ("grille" or "cold_door", Verb.UseItem):
                await Say("No blue in my buttonhole, no hatch.");
                return true;
            case ("grille" or "cold_door", Verb.Kick):
                await Say("Kick a speakeasy door and you meet the fellow whose job it is to kick back.");
                return true;

            case ("bucket", Verb.Hand) when State.HasFlag("grille_opened"):
                await Say("I've had all the flowers I need tonight.");
                return true;
            case ("bucket", Verb.Hand) when State.HasItem("carnation") || State.HasItem("blue_carnation"):
                await Say("One buttonhole, one flower.");
                return true;
            case ("bucket", Verb.Hand):
                State.GiveItem("carnation");
                await Say("I leave a nickel in the tin and take a white carnation. Honest money for an honest flower.");
                return true;

            case ("shelf", Verb.Hand) when !State.HasFlag("took_bluing") && !State.HasFlag("made_blue_carnation"):
                State.SetFlag("took_bluing");
                State.GiveItem("bluing");
                await Say("Mrs. Stewart's Bluing. Every laundress in Chicago has a bottle. So does every florist with a blue flower to sell.");
                return true;
            case ("shelf", Verb.Hand) when State.HasFlag("made_blue_carnation"):
                await Say("The bluing's back on the shelf, a few drops lighter.");
                return true;
            case ("shelf", Verb.Hand):
                await Say("Pots and a watering can. Nothing else worth borrowing.");
                return true;

            case ("chalkboard", Verb.Hand):
                await Say("Wipe it off and every member in Chicago turns up in the wrong flower. Tempting.");
                return true;
            case ("regular", Verb.Talk):
                await Say("Evening.");
                await Say("The brim tips up an inch. He takes in my bare lapel, then goes back to studying the pavement. Conversation over.");
                return true;
            case ("regular", Verb.Hand):
                await Say("Lift a flower off a man's coat on State Street and I'll be wearing it in the river.");
                return true;
            case ("regular", Verb.UseItem):
                await Say("He's not buying, and he's not selling. Not to me.");
                return true;
            case ("shop_door", Verb.Walk or Verb.Hand):
                await Say("Locked. The flowers sleep in the window; the business is done round the side.");
                return true;
            case ("window", Verb.Hand):
                await Say("Plate glass. Rizzo didn't pay for that with carnations.");
                return true;
            case ("lantern", Verb.Hand):
                await Say("Out of reach, and unlit. Lighting it would be advertising.");
                return true;
            case ("window" or "shop_door" or "shelf" or "bucket", Verb.Kick):
                await Say("Wreck a florist's on State Street. The Outfit would send flowers. To my funeral.");
                return true;
        }
        return false;
    }
}
