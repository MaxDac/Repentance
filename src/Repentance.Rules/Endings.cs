using System;

namespace Repentance;

/// <summary>
/// The rules that decide how Act 3 ends. Godot-free so they can be unit tested; callers pass GameState.HasFlag.
///   1  Rose        - Micah gives up: on the church steps, in front of the bartender or the old man, carrying the
///                    wedding ring and having insisted with Rose (rose_forgives). If Eleanor held out and he gave up
///                    before the mansion, Caleb gets her out of the city after the coffee.
///   2  Outskirts   - Eleanor convinced, and the mansion burned or Micah took the documents.
///   3  Outskirts   - Eleanor not convinced, and the mansion burned or Micah took the documents.
///   4  Prison      - Eleanor convinced, but nothing to bargain with: Eleanor visits.
///   5  Prison      - Eleanor not convinced, nothing to bargain with: Caleb visits.
///   6  Prison      - Micah shot the old man, then repented and walked out without Eleanor: Rose visits.
///   7  Mansion     - Micah shot the old man, then himself (after Eleanor, or with her left alive): Caleb finishes the journal.
///   8  Outskirts   - Eleanor (both refusals, Micah prayed) struck the old man and burned the house: she leaves alone.
///   9  Prison      - Eleanor struck the old man and left the house standing: she confesses to Caleb.
///  10  Outskirts   - Eleanor (both refusals), worn out, followed Micah after he shot; fire or documents: she leaves him for her peace.
///  11  Prison      - The same, but nothing to bargain with: Eleanor visits once, wishing him his peace.
///  12  Prison      - Micah killed Tony and turned himself in for it: from Caleb's church, or after the Our Father,
///                    which needs the confession on top of the usual gates. Caleb visits.
///  13  Outskirts   - After the warning shot (Tony never mentioned the alarm), Micah opened the kitchen door unnoticed,
///                    the bell rang and he ran: alone, out of Chicago, and the journal ends with his suicide.
///  14  Mansion     - The same bell, but he stayed and walked into the kitchen: two of the Club's men shot him.
///                    Caleb finishes the journal.
///                    In 13 and 14, if Eleanor held out, Caleb gets her out of the city afterwards.
///  15  Rose        - The same give-up without both the ring and the appeals: Rose refuses the coffee, but lets Micah
///                    see Tommy on Sundays. Caleb's escape with Eleanor plays as in ending 1.
/// Eleanor's own endings need both interlude refusals; the refusals alone change nothing (a give-up is still 1 or 15).
/// Repenting and the murder-suicide both end the night in the bedroom, so they decide before anything after it.
/// Once Tony is dead there is no going home to Rose: the prayer that would give ending 1 or 15 gives 12 instead.
/// The alarm stops the story at the kitchen door, so 13 and 14 decide before everything else.
/// </summary>
public static class Endings
{
    public const string GaveUpSteps = "gave_up_steps";
    public const string WalkedAway = "walked_away";
    public const string SparedOldMan = "spared_oldman";
    public const string EleanorConvinced = "eleanor_convinced";
    /// <summary>Set when the house burns after the cellar fire; the name predates the fire and is kept for saves.</summary>
    public const string MansionExploded = "mansion_exploded";
    public const string TookDocuments = "took_documents";
    public const string Repented = "repented";
    public const string ShotEleanor = "shot_eleanor";
    /// <summary>Micah turned the revolver on himself and left Eleanor alive.</summary>
    public const string ShotHimself = "shot_himself";
    /// <summary>First Interlude: Eleanor turned the Mother Superior away in the convent cell.</summary>
    public const string RefusedAbbess = "eleanor_refused_abbess";
    /// <summary>Second Interlude: Eleanor refused the old man's gin and powder backstage.</summary>
    public const string RefusedDrugs = "eleanor_refused_drugs";
    /// <summary>Eleanor's coda: she struck the old man with the candlestick.</summary>
    public const string EleanorStruck = "eleanor_struck";
    /// <summary>Eleanor's coda: she burned the house on her way out.</summary>
    public const string EleanorBurned = "eleanor_burned";
    /// <summary>Micah shot the old man and Eleanor (both refusals), too worn out to argue, followed him without persuasion.</summary>
    public const string EleanorWeary = "eleanor_weary";
    /// <summary>The alley: Micah shot Tony in the shoulder, and Tony knows who did it.</summary>
    public const string ShotBartender = "shot_bartender";
    /// <summary>The alley: Micah went back and finished Tony off, so he couldn't tell the mob.</summary>
    public const string KilledTony = "killed_tony";
    /// <summary>Micah confessed Tony to Caleb and went on to the mansion, promising to turn himself in after.</summary>
    public const string ConfessedTony = "confessed_tony";
    /// <summary>Micah confessed Tony to Caleb and walked with him to the police that night.</summary>
    public const string SurrenderedTony = "surrendered_tony";
    /// <summary>The alley: Micah fired into the brick by Tony's head instead. Tony talked, unhurt, but left out the alarm.</summary>
    public const string WarnedTony = "warned_tony";
    /// <summary>The kitchen door opened on an unnoticed alarm, and Micah ran from the footsteps.</summary>
    public const string AlarmRan = "alarm_ran";
    /// <summary>The kitchen door opened on an unnoticed alarm, and Micah walked in anyway.</summary>
    public const string AlarmStayed = "alarm_stayed";
    /// <summary>Derived before the peaceful choices: Micah carries the wedding ring and insisted with Rose.</summary>
    public const string RoseForgives = "rose_forgives";

    /// <summary>The number of endings.</summary>
    public const int Count = 15;

    /// <summary>Endings in which Daniel keeps the journal for Leo.</summary>
    public static bool KeepsJournal(int ending) => ending is 1 or 6 or 8 or 9 or 10 or 11 or 12 or 15;

    /// <summary>Tony is alive and knows Micah shot him: the mob will want its revenge.</summary>
    public static bool TonyWantsRevenge(Func<string, bool> has) => has(ShotBartender) && !has(KilledTony);

    /// <summary>Eleanor refused both the Mother Superior and the old man: her own endings open up.</summary>
    public static bool EleanorHeldOut(Func<string, bool> has) => has(RefusedAbbess) && has(RefusedDrugs);

    /// <summary>
    /// When Eleanor held out and Micah never reached her, Caleb gets her out of the city, and she plays one last scene
    /// with him at the outskirts: in ending 1 or 15 from a give-up before the mansion (the church steps, or walking away
    /// from Tony), after Rose's door; and after the alarm, whether Micah ran (13) or was shot in the kitchen (14).
    /// </summary>
    public static bool EleanorEscapesWithCaleb(Func<string, bool> has)
    {
        if (!EleanorHeldOut(has)) return false;
        int ending = Resolve(has);
        return ending is 13 or 14 || (ending is 1 or 15 && (has(GaveUpSteps) || has(WalkedAway)));
    }

    /// <summary>
    /// Eleanor's clothes once she is out of the mansion and free (endings 2, 4, 8, 10, 11), from the duffle she packed for
    /// running: "eleanor_white" (her own dress in white, with pearls) if she held out, otherwise "eleanor_suit" (a black
    /// skirt suit cut above the knee). The sprite names of her NPC strip; seated and player variants add a suffix.
    /// </summary>
    public static string EleanorFreeOutfit(Func<string, bool> has) => EleanorHeldOut(has) ? "eleanor_white" : "eleanor_suit";

    /// <summary>Eleanor came away with Micah: convinced, or worn out after the shot.</summary>
    public static bool EleanorFollows(Func<string, bool> has) => has(EleanorConvinced) || has(EleanorWeary);

    /// <summary>Micah kept asking Rose for forgiveness on her doorstep.</summary>
    public static bool InsistedForgiveness(Func<string, bool> has) => has("rose_wait");

    /// <summary>Micah still holds on to his marriage: he carries the wedding ring, or he insisted with Rose.</summary>
    public static bool Faithful(Func<string, bool> has, Func<string, bool> hasItem) =>
        hasItem("faith_ring") || InsistedForgiveness(has);

    /// <summary>Rose takes the coffee (ending 1) only if Micah carries the ring and insisted with her; otherwise 15.</summary>
    public static bool RoseTakesHimBack(Func<string, bool> has, Func<string, bool> hasItem) =>
        hasItem("faith_ring") && InsistedForgiveness(has);

    /// <summary>Giving up on the church steps after the Club.</summary>
    public static bool CanGiveUp(Func<string, bool> has, Func<string, bool> hasItem) => Faithful(has, hasItem);

    /// <summary>Lowering the gun on Tony: the ring, the appeals or Caleb's cross, any one of them.</summary>
    public static bool CanWalkAwayFromBartender(Func<string, bool> has, Func<string, bool> hasItem) =>
        Faithful(has, hasItem) || hasItem("cross");

    /// <summary>The Our Father: the cross and the ring or the appeals, and, once Tony is dead, his confession to Caleb.</summary>
    public static bool CanSpareOldMan(Func<string, bool> has, Func<string, bool> hasItem) =>
        hasItem("cross") && Faithful(has, hasItem) && (!has(KilledTony) || has(ConfessedTony));

    public static bool CanOfferCross(int act, Func<string, bool> has) =>
        has("caleb_met") && !has("took_cross") &&
        (act >= 3 || (act == 2 && has("ring_left_act2")));

    /// <summary>Documents or the fire give Micah something to bargain with, which keeps him out of jail.</summary>
    public static bool StaysFree(Func<string, bool> has) => has(MansionExploded) || has(TookDocuments);

    public static int Resolve(Func<string, bool> has)
    {
        if (has(AlarmStayed))
            return 14;
        if (has(AlarmRan))
            return 13;
        if (has(EleanorStruck))
            return has(EleanorBurned) ? 8 : 9;
        if (has(EleanorWeary))
            return StaysFree(has) ? 10 : 11;
        if (has(SurrenderedTony) || (has(KilledTony) && has(SparedOldMan)))
            return 12;
        if (has(GaveUpSteps) || has(WalkedAway) || has(SparedOldMan))
            return has(RoseForgives) ? 1 : 15;
        if (has(Repented))
            return 6;
        if (has(ShotEleanor) || has(ShotHimself))
            return 7;
        var convinced = has(EleanorConvinced);
        if (StaysFree(has))
            return convinced ? 2 : 3;
        return convinced ? 4 : 5;
    }
}
