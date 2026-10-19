using System;

namespace Repentance;

/// <summary>
/// The rules that decide how Act 3 ends. Godot-free so they can be unit tested; callers pass GameState.HasFlag.
///   1  Rose        - Micah gives up: on the church steps, in front of the bartender or the old man.
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
/// Eleanor's own endings need both interlude refusals; the refusals alone change nothing (a give-up is still 1).
/// Repenting and the murder-suicide both end the night in the bedroom, so they decide before anything after it.
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

    /// <summary>Endings in which Daniel keeps the journal for Leo.</summary>
    public static bool KeepsJournal(int ending) => ending is 1 or 6 or 8 or 9 or 10 or 11;

    /// <summary>Eleanor refused both the Mother Superior and the old man: her own endings open up.</summary>
    public static bool EleanorHeldOut(Func<string, bool> has) => has(RefusedAbbess) && has(RefusedDrugs);

    /// <summary>Eleanor came away with Micah: convinced, or worn out after the shot.</summary>
    public static bool EleanorFollows(Func<string, bool> has) => has(EleanorConvinced) || has(EleanorWeary);

    /// <summary>Micah went back to Caleb at least once while hunting for Eleanor.</summary>
    public static bool ChurchReturned(Func<string, bool> has) =>
        has("church_before_office") || has("church_before_club") || has("church_act3_return");

    /// <summary>Micah kept asking Rose for forgiveness on her doorstep.</summary>
    public static bool InsistedForgiveness(Func<string, bool> has) => has("rose_wait");

    public static bool CanWalkAwayFromBartender(Func<string, bool> has, Func<string, bool> hasItem) =>
        ChurchReturned(has) && hasItem("faith_ring");

    public static bool CanSpareOldMan(Func<string, bool> has, Func<string, bool> hasItem) =>
        CanWalkAwayFromBartender(has, hasItem) && InsistedForgiveness(has) && hasItem("cross");

    public static bool CanOfferCross(int act, Func<string, bool> has) =>
        has("caleb_met") && !has("took_cross") &&
        (act >= 3 || (act == 2 && has("ring_left_act2")));

    /// <summary>Documents or the fire give Micah something to bargain with, which keeps him out of jail.</summary>
    public static bool StaysFree(Func<string, bool> has) => has(MansionExploded) || has(TookDocuments);

    public static int Resolve(Func<string, bool> has)
    {
        if (has(EleanorStruck))
            return has(EleanorBurned) ? 8 : 9;
        if (has(EleanorWeary))
            return StaysFree(has) ? 10 : 11;
        if (has(GaveUpSteps) || has(WalkedAway) || has(SparedOldMan))
            return 1;
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
