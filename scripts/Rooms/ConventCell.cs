using Godot;
using System.Threading.Tasks;

namespace Repentance.Rooms;

/// <summary>
/// Eleanor's cell at the convent: a bed, a lampstand, a book and a nightstand. In the drawer, a comb and a little
/// waxed mirror. Warming and cleaning its back reveals the symbol; Micah won't leave until he has found it.
/// In the First Interlude Eleanor sets her duffle down in front of the nightstand, combs her hair from it, and leaves
/// the comb and mirror in the drawer: Agatha finds her sitting up on the bed in her pyjamas.
/// </summary>
public partial class ConventCell : Room
{
    public override Track? Music => Track.ConventPiano;

    /// <summary>The First Interlude: Eleanor's first night in the cell, and Mother Agatha's visit.</summary>
    private bool Interlude => State.HasFlag("interlude1");

    /// <summary>The rain stops the moment Eleanor refuses Agatha.</summary>
    protected override bool RainStopped => Interlude && State.HasFlag(Endings.RefusedAbbess);

    private static readonly Color Night = new(0.5f, 0.56f, 0.78f);

    /// <summary>Agatha's night visit: she comes in at the door and stops a step short of Eleanor at the bed.</summary>
    private static readonly Vector2 AgathaDoor = new(92, 228), AgathaByTheBed = new(238, 222);

    /// <summary>Where Eleanor stands to set her duffle down in front of the nightstand, facing left (the CellBag node).</summary>
    private static readonly Vector2 BagSpot = new(312, 215);

    /// <summary>Where she sits up on the edge of the bed by the pillow when Agatha knocks (tools/art/convent.py CELL_SIT_AT).</summary>
    private static readonly Vector2 SitAt = new(364, 236);

    /// <summary>While she combs her hair the open bag is drawn into her strip, so the one on the floor steps aside.</summary>
    private bool _combing;

    protected override void OnRefresh()
    {
        Modulate = Interlude ? Night : Colors.White;
        // Room.Refresh shows every hotspot without flag rules; Agatha is only here during her night visit
        if (FindActor("nun") is { } agatha) agatha.Visible = _agathaIn;
        if (GetNodeOrNull<FlagSprite>("World/CellBag") is { } bag) bag.Visible &= !_combing;
    }

    /// <summary>Agatha is in the cell: set for her night visit only, never saved.</summary>
    private bool _agathaIn;

    private void AgathaIn(bool inside)
    {
        _agathaIn = inside;
        Refresh();
    }

    public override async Task OnEnter(string entry)
    {
        if (Interlude)
        {
            await Game.Run(async () =>
            {
                await Think("Narrow enough to touch both walls. After Room 507, it feels like a coffin with a window.");
                if (!State.HasFlag("interlude_bag_left")) await SetBagDown();
            });
            return;
        }
        if (State.HasFlag("cell_seen")) return;
        State.SetFlag("cell_seen");
        await Game.Run(async () =>
        {
            await Wait(0.5);
            await Think("A bed, a lamp and a book. A woman who wore pearls to dinner slept here.");
            await Think("Narrow enough to touch both walls. I feel like I ought to knock, and I'm already inside.");
        });
    }

    public override async Task<bool> OnInteract(Verb verb, Hotspot target, string? item)
    {
        if (Interlude) return await InterludeInteract(verb, target);
        switch (target.Id, verb)
        {
            case ("exit", Verb.Walk or Verb.Hand) when !State.HasFlag("got_mirror"):
                await Say("There is still something to be found in this room.");
                return true;

            case ("nightstand" or "drawer", Verb.Hand) when !State.HasFlag("cell_drawer_open"):
                State.SetFlag("cell_drawer_open");
                await Say("The drawer sticks, then gives.");
                await Say("A comb and a little mirror. Not much to leave behind.");
                return true;
            case ("nightstand" or "drawer", Verb.Hand):
                await Say(State.HasFlag("got_mirror") ? "Just the comb left. It can stay." : "A comb and a little mirror.");
                return true;
            case ("nightstand" or "drawer", Verb.UseItem) when item == "lockpick":
                await Say("It isn't even locked. Nuns trust people. Must be nice.");
                return true;

            case ("mirror", Verb.Hand) when !State.HasFlag("took_mirror"):
                await Say("A little hand mirror. Cheap glass, but somebody loved the frame.");
                State.SetFlag("took_mirror");
                State.GiveItem("mirror_waxed");
                await Say("The wooden back is hidden under old wax. Gentle warmth, then a clean cloth. Not a flame.");
                return true;

            case ("comb", Verb.Hand):
                await Say("Tortoiseshell. A few dark hairs still caught in the teeth.");
                await Say("I'll leave the comb. A girl ought to have something to come back for.");
                return true;

            case ("lampstand", Verb.Hand):
            case ("lampstand", Verb.Look):
                await Say("A little warmth above the lamp, away from the flame. Enough to soften old wax without harming the wood.");
                return true;
            case ("lampstand", Verb.UseItem) when item == "mirror_waxed":
                State.SetFlag("mirror_warmed");
                await Say("I hold the wooden back in the gentle warmth. The wax softens. A clean cloth should lift it now.");
                return true;
            case ("book", Verb.Hand):
                await Say("A breviary. Dog-eared at the Psalms. Somebody was looking for something.");
                return true;
            case ("bed", Verb.Hand):
                if (!State.HasFlag("got_mirror"))
                {
                    bool firstPickup = !State.HasItem("cloth");
                    if (firstPickup)
                        await Say("I ought to leave her bed alone. Somehow, I can't quite make myself turn away.");
                    State.GiveItem("cloth");
                    await Say("A clean cloth folded by the pillow. I'll borrow it to wipe that mirror, then put it back.");
                    if (firstPickup)
                        await Say("Her perfume. I've lifted the cloth to my nose before I even know I'm doing it.");
                }
                else await Say("Thin mattress. Her rag oughta be lying here. It's in my pocket instead.");
                return true;
            case ("bed" or "nightstand" or "lampstand", Verb.Kick):
                await Say("Kick a nun's furniture. Nice, Micah. Very nice.");
                return true;
        }
        return false;
    }

    /// <summary>The first thing she does in the cell: her duffle down in front of the nightstand, for good.</summary>
    private async Task SetBagDown()
    {
        await Game.WalkTo(BagSpot);
        Player.Face(Facing.Left);
        if (Player.Character == Story.EleanorBag.Sheet) await Player.PlayPose("eleanor_bag_down");
        State.SetFlag("interlude_bag_left");
        Player.SetCharacter(Story.EleanorBag.Plain);
    }

    /// <summary>
    /// Her first night (hand on the nightstand or the bed): she opens the duffle, takes out her comb and little mirror
    /// and combs her hair out. Over black the comb and mirror go in the drawer; when Agatha knocks she is sitting up on
    /// the edge of the bed in her pyjamas, awake.
    /// </summary>
    private async Task FirstNight()
    {
        if (!State.HasFlag("interlude_bag_left")) await SetBagDown();
        await Game.WalkTo(BagSpot);
        Player.Face(Facing.Left);
        _combing = true;
        State.SetFlag("interlude_combed");
        Refresh();
        await Player.PlayPose("eleanor_comb");
        await Say("A hundred strokes, the way my mother taught me. I lose count at forty, every night.");
        await Game.Hud.Fade(1, 1.2);
        _combing = false;
        await Think("She put the comb and the little mirror away in the nightstand drawer, and lay down in her nightclothes. She left them there when she went.");
        State.SetFlag("interlude_pyjamas");
        Player.SetCharacter("eleanor_pyjama_play");
        Player.Teleport(SitAt, Facing.Left);
        Player.SetPose("eleanor_cell_sit");
        await Wait(0.6);
        await Say("nun", "*Knock, knock*");
        // the Club follows her to the convent: its strings play for Agatha's visit only
        Game.Music.Play(Track.ClubStrings);
        await Game.Hud.Fade(0, 0.6);
        var agatha = FindActor("nun");
        if (agatha != null)
        {
            agatha.Position = AgathaDoor;
            AgathaIn(true);
            await agatha.MoveTo(AgathaByTheBed, 32);
            agatha.FaceLeft(false);
        }
        await Talk("interlude_agatha_night");
        if (agatha != null)
        {
            await agatha.MoveTo(AgathaDoor, 44);
            AgathaIn(false);
        }
        Game.Music.Play(Music);
        await Game.Hud.Fade(1, 1.2);
        Game.Hud.ShowCaption("The next morning");
        await Wait(1.6);
        Game.Hud.ShowCaption(null);
        await Game.ChangeRoom("motel_night", "interlude1");
    }

    private async Task<bool> InterludeInteract(Verb verb, Hotspot target)
    {
        switch (target.Id, verb)
        {
            case ("bed", Verb.Hand or Verb.Walk):
            case ("nightstand" or "drawer", Verb.Hand):
                await FirstNight();
                return true;
            case ("exit", Verb.Walk or Verb.Hand):
                await Say("The corridor's dark, and somebody in it is still awake. I can feel it.");
                return true;
            case ("window", Verb.Look or Verb.Hand):
                await Say("Bars, and a moon behind them. Even the moon's in a cell tonight.");
                return true;
            case ("book", Verb.Look or Verb.Hand):
                await Say("A breviary. I open it at the Psalms and can't read a line of it.");
                return true;
            case ("lampstand", Verb.Look or Verb.Hand):
                await Say("A lamp turned low. Somebody wanted me to have just enough light to be sorry by.");
                return true;
            case ("nightstand" or "drawer", Verb.Look):
                await Say("An empty drawer, and my bag in front of it. My comb and my little mirror will do for a welcome.");
                return true;
            case ("bed" or "nightstand", Verb.Kick):
                await Say("Kick the furniture in a convent. They'd hear it in Rome.");
                return true;
        }
        return false;
    }
}
