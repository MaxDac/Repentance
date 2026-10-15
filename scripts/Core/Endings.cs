using System;

namespace Repentance;

/// <summary>
/// The rules that decide how Act 3 ends. Godot-free so they can be unit tested; callers pass GameState.HasFlag.
///   1  Rose        - Micah gives up: on the church steps, in front of the bartender or the old man.
///   2  Outskirts   - Eleanor convinced, and the mansion blew up or Micah took the documents.
///   3  Outskirts   - Eleanor not convinced, and the mansion blew up or Micah took the documents.
///   4  Prison      - Eleanor convinced, but nothing to bargain with: Eleanor visits.
///   5  Prison      - Eleanor not convinced, nothing to bargain with: Caleb visits.
///   6  Prison      - Micah shot the old man, then repented and walked out without Eleanor: Rose visits.
///   7  Mansion     - Micah shot the old man, then Eleanor, then himself: Caleb finishes the journal.
/// Repenting and the murder-suicide both end the night in the bedroom, so they decide before anything after it.
/// </summary>
public static class Endings
{
    public const string GaveUpSteps = "gave_up_steps";
    public const string WalkedAway = "walked_away";
    public const string SparedOldMan = "spared_oldman";
    public const string EleanorConvinced = "eleanor_convinced";
    public const string MansionExploded = "mansion_exploded";
    public const string TookDocuments = "took_documents";
    public const string Repented = "repented";
    public const string ShotEleanor = "shot_eleanor";

    /// <summary>Endings in which Daniel keeps the journal for Leo.</summary>
    public static bool KeepsJournal(int ending) => ending is 1 or 6;

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

    /// <summary>Documents or the explosion give Micah something to bargain with, which keeps him out of jail.</summary>
    public static bool StaysFree(Func<string, bool> has) => has(MansionExploded) || has(TookDocuments);

    public static int Resolve(Func<string, bool> has)
    {
        if (has(GaveUpSteps) || has(WalkedAway) || has(SparedOldMan))
            return 1;
        if (has(Repented))
            return 6;
        if (has(ShotEleanor))
            return 7;
        var convinced = has(EleanorConvinced);
        if (StaysFree(has))
            return convinced ? 2 : 3;
        return convinced ? 4 : 5;
    }
}
