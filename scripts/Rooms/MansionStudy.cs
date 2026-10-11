using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// The old man's study, between the kitchen passage and his bedroom. A closet, a desk with two drawers, and in the right
/// one a folder of Harrington Steel papers that would interest a grand jury. Easy to walk past; no way back for it later.
/// </summary>
public partial class MansionStudy : Room
{
    public override async Task OnEnter(string entry)
    {
        if (State.HasFlag("seen_mansion_study")) return;
        State.SetFlag("seen_mansion_study");
        await Game.Run(() => Say("His study. Leather, cigars and old money. Voices behind the far door."));
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door_left", Verb.Hand or Verb.Walk):
                await Game.ChangeRoom("mansion_kitchen", "study");
                return true;
            case ("door_right", Verb.Hand or Verb.Walk):
                await Say("Voices. A man's. And hers.");
                await Game.ChangeRoom("mansion_bedroom", "start");
                return true;
            case ("door_right", Verb.Kick):
                await Say("And lose the only advantage I've got? No.");
                return true;

            case ("drawer_left", Verb.Hand):
                Toggle("drawer_left_open");
                if (State.HasFlag("drawer_left_open")) await Say("A box of Havanas. The old man smokes better than he sleeps, I bet.");
                return true;
            case ("drawer_right", Verb.Hand):
                Toggle("drawer_right_open");
                if (State.HasFlag("drawer_right_open") && !State.HasFlag(Endings.TookDocuments))
                    await Say("A folder, tied with red tape. \"Harrington Steel - Private\".");
                return true;
            case ("documents", Verb.Look):
                await Say("Ledgers. Payments to judges, an alderman, two police captains. Signed, initialled, dated.");
                return true;
            case ("documents", Verb.Hand):
                State.SetFlag(Endings.TookDocuments);
                State.GiveItem("documents");
                await Say("Payments to judges, an alderman, two police captains. Signed and dated. Harrington never threw anything away.");
                await Say("Into the coat. A man could buy his way out of a lot of trouble with this.");
                return true;

            case ("closet", Verb.Hand):
                Toggle("closet_open");
                if (State.HasFlag("closet_open")) await Say("Coats, a dinner jacket, a hatbox. No skeletons. He keeps those in the bank.");
                return true;
        }
        return false;
    }

    private void Toggle(string flag) => State.SetFlag(flag, !State.HasFlag(flag));
}
