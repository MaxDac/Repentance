using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Room 507 at the Aurelian: where Eleanor slept the night she vanished, turned over by someone in a hurry.
/// In the First Interlude it is still in order: the old man's men only search it after she has gone.
/// </summary>
public partial class EleanorRoom : Room
{
    private const string Tidy = "res://assets/art/rooms/eleanor_room_interlude.png";

    /// <summary>The First Interlude: Eleanor, the Tuesday night she left (Story.Interlude).</summary>
    private bool Interlude => State.HasFlag("interlude1");

    private Texture2D? _searched;

    /// <summary>While Eleanor holds the telephone, the one on the vanity is in her hands, not on it.</summary>
    private bool _onPhone;

    /// <summary>In the First Interlude the bench stands out in the room; she goes round to the front of it.</summary>
    public override Vector2 ClampWalkTarget(Vector2 target) =>
        Interlude && Walk is { } w && !w.Contains(target) && target.X is > 50 and < 136 && target.Y is > 218 and < 240
            ? new Vector2(target.X, 241) : target;

    /// <summary>Her kit is granted on load as well as on entering, so a save from before she carried it gets it too.</summary>
    public override void _Ready()
    {
        if (Interlude) PackEleanorsKit();
        base._Ready();
    }

    protected override void OnRefresh()
    {
        if (GetNodeOrNull<Sprite2D>("Background") is not { } bg) return;
        _searched ??= bg.Texture;
        bg.Texture = Interlude ? GD.Load<Texture2D>(Tidy) : _searched;
        if (GetNodeOrNull<FlagSprite>("InterludeTelephone") is { } phone) phone.Visible = Interlude && !_onPhone;
    }

    private void HoldPhone(bool held)
    {
        _onPhone = held;
        OnRefresh();
    }

    /// <summary>She lifts the candlestick off the vanity, puts the receiver to her ear, makes the call, hangs up.</summary>
    private async Task CallRizzo()
    {
        HoldPhone(true);
        try
        {
            await Player.PlayPose("eleanor_phone");
            await Talk("interlude_rizzo");
            await Player.PlayPose("eleanor_phone_down");
        }
        finally
        {
            Player.SetPose(null);
            HoldPhone(false);
        }
    }

    public override async Task OnEnter(string entry)
    {
        if (Interlude)
        {
            if (entry == "interlude") await Game.Run(() => Talk("interlude_aurelian"));
            return;
        }
        if (State.HasFlag("seen_eleanor_room")) return;
        State.SetFlag("seen_eleanor_room");
        await Game.Run(async () =>
        {
            await Wait(0.4);
            await Think("Room 507. Silk on the floor, feathers in the air. Somebody's been here before me, and they didn't knock either.");
            await Think("Her perfume still hangs in the air, under the cigar smoke. Whatever they were looking for, I'd bet they didn't find it.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (Interlude) return await InterludeInteract(verb, target, item);
        switch (target.Id, verb)
        {
            case ("desk_drawer", Verb.Hand) when !State.HasFlag("eleanor_drawer_open"):
                await Say("The left drawer is locked. The only thing in this room nobody managed to open.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "lockpick" && !State.HasFlag("eleanor_drawer_open"):
                State.SetFlag("eleanor_drawer_open");
                await Say("No hotel lock, this. Somebody paid a locksmith for it. It took the tension wrench, two rakes and the better part of my patience.");
                await Say("Damn hard. It snapped one of my picks off in the keyway before it gave.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "lockpick":
            case ("desk_drawer", Verb.Hand):
                await Say(State.HasFlag("took_combination") ? "Empty now." : "There's a slip of paper inside.");
                return true;
            case ("desk_drawer", Verb.Kick):
                await Say("Kicking it open would bring the house detective. The quiet way, then.");
                return true;

            case ("paper", Verb.Hand):
                State.SetFlag("took_combination");
                State.GiveItem("combination");
                await Say("A slip of hotel paper in her hand. Three lines of Sunday school. Nobody writes that down unless it opens something.");
                return true;
            case ("paper", Verb.Look):
                await Say("Three riddles in Eleanor's handwriting. No numbers, no right or left. She didn't trust paper with anything plain.");
                return true;

            case ("closet", Verb.Hand) when !State.HasFlag("closet_open"):
                State.SetFlag("closet_open");
                await Say("Half her dresses were on the floor already. Behind the rest, set low in the back wall... a safe.");
                return true;
            case ("closet", Verb.Hand):
                await Say("Silk, cedar, and steel at the back.");
                return true;

            case ("safe", Verb.Hand) when !State.HasFlag("safe_open"):
            case ("safe", Verb.UseItem) when Shows(item, "combination", "safe_riddle") && !State.HasFlag("safe_open"):
                if (!await Game.Hud.Puzzle.Open(PuzzleKind.Safe)) return true;
                Game.Sfx.Play(Sound.SafeOpen);
                State.SetFlag("safe_open");
                await Say("Twelve apostles. Thirty-one days of December. The seventh day. The tumblers fell like dominoes.");
                await Think("Now ain't that a pip. A swell doll who runs with the Club crowd, and she locks her secrets up with the Good Book. Strange, a dame like her bringin' Christ into it.");
                await Say("Somebody's been at the dial since. Scratched it raw and never got the door open.");
                return true;
            case ("safe", Verb.Hand):
                await Say(State.HasFlag("took_brass_box") ? "Empty now." : "Something brass, catching the light.");
                return true;
            case ("safe", Verb.Kick):
                await Say("Steel. My foot would lose that argument.");
                return true;

            case ("brass_box", Verb.Hand):
                State.SetFlag("took_brass_box");
                State.GiveItem("brass_box");
                State.SetFlag("recover_hotel", false);
                await Say("A little brass box, engraved with lilies. The only thing in this room she bothered to lock away twice.");
                await Think("Her things trampled, her secrets locked away twice. Whoever Eleanor Harrington is, she was expecting company.");
                return true;

            case ("bed", Verb.Hand):
                await Say("Mattress slit, pillows gutted. Feathers and nothing else.");
                return true;
            case ("fallen_telephone", Verb.Hand or Verb.Talk):
                await Say("Dead air. Somebody yanked it off the vanity by the cord and nobody's called down since. I'll leave it where it fell.");
                return true;
            case ("clothes", Verb.Hand):
                await Say("Her dresses, her stockings, her letters. All thrown down and trampled over.");
                return true;
            case ("chair", Verb.Hand):
                await Say("I left it on its back. Seemed only fair to the evidence.");
                return true;
            case ("window", Verb.Hand):
                await Say("Five floors down to the alley. She didn't leave this way.");
                return true;
            case ("vanity", Verb.Hand):
                await Say("Drawers pulled, perfume spilt. Smells like money and fear.");
                return true;
        }

        return false;
    }

    private bool Packed => State.HasFlag("interlude_box_packed");
    private bool ClosetOpen => State.HasFlag("interlude_closet_open");
    private bool BoxInSafe => State.HasFlag("interlude_box_in_safe");
    private bool SafeLocked => State.HasFlag("interlude_safe_locked");

    /// <summary>
    /// What Eleanor brings to Room 507: a blank slip for the safe's riddle and the key to the lock she had fitted to the
    /// desk drawer. Derived from her progress, so a save from before she carried them loads with them too.
    /// </summary>
    private void PackEleanorsKit()
    {
        if (!State.HasFlag("interlude_riddle_written") && !State.HasItem("eleanor_slip")) State.GiveItem("eleanor_slip");
        if (State.HasFlag("interlude_riddle_written") && !State.HasFlag("interlude_riddle_in_drawer") && !State.HasItem("eleanor_riddle"))
            State.GiveItem("eleanor_riddle");
        if (!State.HasFlag("interlude_drawer_locked") && !State.HasItem("eleanor_key")) State.GiveItem("eleanor_key");
    }

    private async Task LockSafe()
    {
        State.SetFlag("interlude_box_in_safe");
        State.SetFlag("interlude_safe_locked");
        Game.Sfx.Play(Sound.SafeClose);
        await Say("Swing the door to, and spin the dial. The Twelve at His table. December. The day He rested.");
        await Say("Let Theodore's men scratch at it all night. They never could count past their fingers.");
    }

    private async Task PutBoxInSafe()
    {
        State.TakeItem("eleanor_box_packed");
        State.SetFlag("interlude_box_in_safe");
        await Say("In it goes, right at the back, where the light doesn't reach.");
    }

    private bool ReadyToLeave => SafeLocked && State.HasFlag("interlude_drawer_locked") && State.HasFlag("interlude_phoned");

    /// <summary>The safe in her open closet: the packed box goes in, then her hand swings the door shut and spins the dial.</summary>
    private async Task<bool> InterludeSafe(Verb verb, string? item)
    {
        switch (verb)
        {
            case Verb.Look:
                await Say(SafeLocked ? "Shut and spun. Only the riddle knows the way in now."
                    : BoxInSafe ? "My brass box inside. Now the door, and the dial."
                    : "Standing half open, the way I left it. Empty, waiting for the box.");
                return true;
            case Verb.UseItem when SafeLocked:
                await Say("Locked. Twice locked, like everything else I care about.");
                return true;
            case Verb.UseItem when item == "eleanor_box_packed" && !BoxInSafe:
                await PutBoxInSafe();
                return true;
            case Verb.UseItem:
                await Say(BoxInSafe ? "The box is all that goes in there."
                    : item is "eleanor_box" or "eleanor_flower" or "pellet" or "riddle_scrap" or "red_thread"
                        ? "Not yet. Everything goes in the box first, and then the box goes in the safe."
                        : "That doesn't go in the safe. Only the box.");
                return true;
            case Verb.Hand when SafeLocked:
                await Say("Locked. Twice locked, like everything else I care about.");
                return true;
            // a save from before the box went in by hand: packed, with no box left in the satchel
            case Verb.Hand when BoxInSafe || (Packed && !State.HasItem("eleanor_box_packed")):
                await LockSafe();
                return true;
            case Verb.Hand:
                await Say(Packed ? "Not yet. The box goes in first." : "The safe can wait. The box isn't packed yet.");
                return true;
            case Verb.Kick:
                await Say("Steel. My foot would lose that argument.");
                return true;
        }
        return false;
    }

    /// <summary>
    /// Eleanor's last hour in Room 507 (Puzzle 17): the brass box and a bare paper flower from the vanity, a riddle
    /// written on desk stationery, red thread from a torn hem. The riddle tied round the flower, the flower into the
    /// box. The closet opened on the safe she left standing half open, the box put in it, the safe shut. Then the
    /// safe's combination written as a riddle on her blank slip at the desk, put in the drawer and locked with her own
    /// key, a call to Rizzo's on the candlestick telephone on the vanity, and the door, where Sal is waiting.
    /// </summary>
    private async Task<bool> InterludeInteract(Verb verb, Hotspot target, string? item)
    {
        switch (target.Id, verb)
        {
            case ("vanity", Verb.Look):
                await Say("Perfume, powder, and a face I don't much like tonight.");
                if (!State.HasFlag("interlude_took_box") && !Packed) await Say("And my brass box, open, waiting for the last of it.");
                return true;
            case ("vanity", Verb.Hand) when !State.HasFlag("interlude_took_box") && !Packed:
                State.SetFlag("interlude_took_box");
                State.GiveItem("eleanor_box");
                State.GiveItem("pellet");
                await Say("The brass box. The card, the matchbook, the bluing already inside. And the little paper flower that blooms in water.");
                await Say("The word's inked inside it. But a bare pellet's just a sweet. It needs a riddle round it, so whoever the paper sends knows to drown it.");
                return true;
            case ("vanity", Verb.Hand):
                await Say("Nothing else on there I'll miss.");
                return true;

            case ("closet", Verb.Look) when !ClosetOpen:
                await Say("My dresses in a row behind those doors, waiting like I'll be back to wear them. The safe's at the back, behind them.");
                return true;
            case ("closet", Verb.Look):
                await Say(SafeLocked ? "My dresses, and the safe behind them, shut and spun."
                    : "My dresses in a row, waiting like I'll be back to wear them. And the safe at the back, standing half open.");
                return true;
            case ("closet", Verb.Hand) when !ClosetOpen:
                State.SetFlag("interlude_closet_open");
                await Say("My dresses in a row, waiting like I'll be back to wear them.");
                await Say(SafeLocked ? "And the safe behind them, shut and spun."
                    : "And at the back, the safe, standing half open the way I left it this afternoon.");
                return true;
            case ("closet", Verb.Hand) when BoxInSafe && !SafeLocked:
                await Say("Not with the safe standing open. The safe door first.");
                return true;
            case ("closet", Verb.Hand):
                State.SetFlag("interlude_closet_open", false);
                await Say("I shut the doors on them. Let the dresses keep it company.");
                return true;
            case ("closet", Verb.UseItem) when !ClosetOpen:
                await Say(item is "eleanor_box_packed" or "eleanor_box" or "eleanor_flower"
                    ? "The safe's behind the closet doors. Open them first."
                    : "That doesn't go in the closet.");
                return true;
            case ("closet", Verb.UseItem):
                return await InterludeSafe(Verb.UseItem, item);
            case ("interlude_safe", _):
                return await InterludeSafe(verb, item);
            case ("desk_drawer", _) when !SafeLocked:
                await Say("The riddle goes in the drawer. But the box goes in the safe first.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "eleanor_riddle" && !State.HasFlag("interlude_riddle_in_drawer"):
                State.TakeItem("eleanor_riddle");
                State.SetFlag("interlude_riddle_in_drawer");
                await Say("Three lines of Sunday school on hotel paper, into the drawer. My grandmother would be proud.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "eleanor_slip":
                await Say("A blank slip won't open anything. The combination goes on it first, at the desk.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "eleanor_key" && !State.HasFlag("interlude_riddle_in_drawer"):
                await Say("Lock an empty drawer? The riddle goes in first.");
                return true;
            case ("desk_drawer", Verb.UseItem) when item == "eleanor_key" && !State.HasFlag("interlude_drawer_locked"):
                State.SetFlag("interlude_drawer_locked");
                await Say("I had a locksmith on Wabash fit this drawer with a lock of his own, and paid him to forget it. This is the only key.");
                await Say("Turn it, and keep it. Theodore's men will kick it and give up. A reporter with a whole night won't.");
                return true;
            case ("desk_drawer", Verb.Hand) when !State.HasFlag("interlude_riddle_in_drawer"):
                await Say(State.HasItem("eleanor_riddle") ? "The riddle goes in here, and then my key turns on it."
                    : "The riddle goes in here. I haven't written it yet.");
                return true;
            case ("desk_drawer", Verb.Hand or Verb.UseItem) when !State.HasFlag("interlude_drawer_locked"):
                await Say("The riddle's in. Now my key.");
                return true;
            case ("desk_drawer", _) when !State.HasFlag("interlude_riddle_in_drawer"):
                await Say("The safe's locked. Now the riddle goes in this drawer, and I turn the key.");
                return true;
            case ("desk_drawer", _) when !State.HasFlag("interlude_drawer_locked"):
                await Say("The riddle's inside. It wants my key.");
                return true;
            case ("desk_drawer", _):
                await Say("Locked, with the riddle inside.");
                return true;

            case ("bed", Verb.Look):
                await Say("Turned down by the maid, and I won't sleep in it. By morning Theodore's men will have it in ribbons.");
                return true;
            case ("bed", Verb.Hand):
                await Say("Lie down now and I'd never get up. Not tonight.");
                return true;

            case ("telephone", Verb.Look):
                await Say("The hotel extension, black and nickel. No dial: lift the receiver and the girl at the switchboard downstairs asks who I want.");
                await Say("She'll remember who I asked for, too. Let her. Rizzo's sells flowers.");
                return true;
            case ("telephone", Verb.Hand or Verb.Talk) when !State.HasFlag("interlude_drawer_locked"):
                await Say(!State.HasFlag("interlude_safe_locked") ? "Not yet. The box goes in the safe first."
                    : !State.HasFlag("interlude_riddle_written") ? "Not yet. The combination goes on paper first, at the desk."
                    : !State.HasFlag("interlude_riddle_in_drawer") ? "Not yet. The riddle goes in the drawer."
                    : "Not yet. My key turns on that drawer first. Then I call.");
                return true;
            case ("telephone", Verb.Hand or Verb.Talk) when !State.HasFlag("interlude_phoned"):
                State.SetFlag("interlude_phoned");
                await Say("My hand's shaking. Good thing nobody can see it down a wire.");
                await CallRizzo();
                return true;
            case ("telephone", Verb.Hand or Verb.Talk):
                await Say("I've made my call. Now I wait for the knock that isn't Theodore's.");
                return true;

            case ("exit", Verb.Walk or Verb.Hand) when !ReadyToLeave:
                await Say(!State.HasFlag("interlude_safe_locked") ? "Not yet. The box goes in the safe first."
                    : !State.HasFlag("interlude_riddle_written") ? "Not yet. The combination goes on paper first, at the desk."
                    : !State.HasFlag("interlude_riddle_in_drawer") ? "Not yet. The riddle goes in the drawer."
                    : !State.HasFlag("interlude_drawer_locked") ? "Not yet. The drawer wants my key."
                    : "Not yet. Nobody's coming for me unless I call.");
                return true;
            case ("exit", Verb.Walk or Verb.Hand):
                await Game.WalkTo(target.WalkTo);
                await Say("*Knock, knock*");
                await Talk("interlude_sal");
                await Game.Hud.Fade(1, 1.2);
                await Game.ChangeRoom("speakeasy", "interlude");
                return true;

            case ("clothes", Verb.Look):
                await Say("My red dress, laid out on the bench. Theodore's favourite.");
                if (!State.HasFlag("interlude_took_thread")) await Say("It's torn at the hem. Silk thread, hanging loose.");
                return true;
            case ("clothes", Verb.Hand) when !State.HasFlag("interlude_took_thread"):
                State.SetFlag("interlude_took_thread");
                State.GiveItem("red_thread");
                await Say("A length of red thread from the torn hem. Theodore bought me that dress. It can tie up one last thing for me.");
                return true;
            case ("clothes", Verb.Hand):
                await Say("Let it lie there. When his men come looking, they can trample it.");
                return true;
            case ("chair", Verb.Look or Verb.Hand):
                await Say("Pulled up to the desk, the way I leave it every night. Tonight's the last.");
                return true;
            case ("window", Verb.Look or Verb.Hand):
                await Say("Five floors down to the alley. The rain doesn't care who's leaving.");
                return true;
            case ("desk", Verb.UseItem) when item == "eleanor_slip":
                State.TakeItem("eleanor_slip");
                State.SetFlag("interlude_riddle_written");
                State.GiveItem("eleanor_riddle");
                await Say("Pencil, my best Sunday hand. The Twelve at His table. The days of December. The day He rested.");
                await Say("No numbers, no right or left. Anybody who doesn't know his Bible can stare at it all night.");
                return true;
            case ("desk", Verb.UseItem) when item == "eleanor_riddle":
                await Say("Written. It goes in the drawer, under lock and key.");
                return true;
            case ("desk", Verb.Hand) when !State.HasFlag("interlude_took_scrap"):
                State.SetFlag("interlude_took_scrap");
                State.GiveItem("riddle_scrap");
                await Say("A scrap of stationery, torn small. In a hurry, in pencil: \"Give me a drink and I'll tell you the word.\"");
                await Say("Wrapped round the flower, it tells a newspaperman what to do with it. Theodore's men would toss it with the rest.");
                return true;
            case ("desk", Verb.Look or Verb.Hand):
                await Say("Hotel stationery. I've written Theodore a hundred letters on it, and sent him none.");
                return true;
        }
        return false;
    }
}