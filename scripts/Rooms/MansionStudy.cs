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
        await Game.Run(async () =>
        {
            await Think("His study. Leather, cigars and old money. Voices behind the far door.");
            await Think("The whole room smells of a man who has never once had to say he was sorry.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("door_left", Verb.Hand or Verb.Walk):
                if (!State.HasFlag("baize_unbolted"))
                {
                    State.SetFlag("baize_unbolted");
                    await Say("The baize door's bolted on this side. I slide it back. Easier than the cellar.");
                }
                await Game.ChangeRoom("mansion_kitchen", "study");
                return true;

            case ("bar_panel", Verb.Hand or Verb.Walk) when State.HasFlag("cellar_lit"):
                await Game.ChangeRoom("mansion_cellar", "stair");
                return true;
            case ("bar_panel", Verb.Hand):
                await Say("Decanters and a soda siphon. The back panel's flush. Nothing to get a finger behind from this side.");
                return true;
            case ("bar_panel", Verb.Look) when State.HasFlag("cellar_lit"):
                await Say("The bootleggers' hatch, standing open. The lantern's still burning at the bottom of the stair.");
                return true;
            case ("door_right", Verb.Hand or Verb.Walk):
                await Think("Voices. A man's. And hers.");
                await Game.ChangeRoom("mansion_bedroom", "start");
                return true;
            case ("door_right", Verb.Kick):
                await Say("And lose the only advantage I've got? No.");
                return true;

            case ("drawer_left", Verb.Hand):
                Toggle("study_drawer_left_open");
                if (State.HasFlag("study_drawer_left_open"))
                {
                    if (!State.HasFlag("audit_tracing_taken") && !State.HasFlag(Endings.TookDocuments))
                    {
                        State.SetFlag("audit_tracing_taken");
                        State.GiveItem("audit_tracing");
                        await Say("Under the cigars: an auditor's index, stamped Harrington Steel - Private. Bank, judge, captain. Three marks to match against the register.");
                    }
                    else await Say("The cigars can stay. I've got what I need.");
                }
                return true;
            case ("drawer_right", Verb.Hand):
                Toggle("study_drawer_right_open");
                if (State.HasFlag("study_drawer_right_open") && !State.HasFlag("audit_folder_taken"))
                    await Say("A register of numbered accounts. \"Private. Use auditor's index to locate signed payment sheets.\" Might be something I could bargain with.");
                return true;
            case ("documents", Verb.Look):
                await Say("A register, not the evidence itself. BANK, JUDGE and CAPTAIN marks. The matching index should locate the signed sheets in this drawer.");
                return true;
            case ("documents", Verb.Hand):
                State.SetFlag("audit_folder_taken");
                State.GiveItem("audit_folder");
                await Say("A numbered register, not the signed sheets. The other drawer might have its index. I'd better sort it out before going into the bedroom; there'll be no coming back.");
                return true;
            case ("documents", Verb.UseItem) when item == "audit_tracing":
                State.SetFlag("audit_folder_taken");
                State.GiveItem("audit_folder");
                await Game.TryReadAccounts();
                return true;

            case ("closet", Verb.Hand):
                Toggle("study_closet_open");
                if (State.HasFlag("study_closet_open")) await Say("Coats, a dinner jacket, a hatbox. No skeletons. He keeps those in the bank.");
                return true;
        }
        return false;
    }

    private void Toggle(string flag) => State.SetFlag(flag, !State.HasFlag(flag));
}
