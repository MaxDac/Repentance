namespace Repentance;

/// <summary>
/// Look / Hand / Talk / Kick are the four icons on the right-click verb wheel (Curse of Monkey Island style).
/// Hand covers pick up, open, close and use; Kick covers push and pull. Walk is a plain left click on the
/// floor or an exit, and UseItem is a left click with an inventory item held as the cursor (use or give).
/// </summary>
public enum Verb { Walk, Look, Hand, Talk, Kick, UseItem }

public enum Facing { Auto, Down, Up, Left, Right }

public static class Verbs
{
    /// <summary>Wheel order, clockwise from the top.</summary>
    public static readonly Verb[] Wheel = { Verb.Look, Verb.Hand, Verb.Talk, Verb.Kick };

    public static string Label(Verb v) => v switch
    {
        Verb.Walk => "Walk to",
        Verb.Look => "Look at",
        Verb.Hand => "Use",
        Verb.Talk => "Talk to",
        Verb.Kick => "Kick",
        Verb.UseItem => "Use",
        _ => v.ToString(),
    };

    public static string Icon(Verb v) => v switch
    {
        Verb.Look => "res://assets/art/ui/verb_look.png",
        Verb.Hand => "res://assets/art/ui/verb_hand.png",
        Verb.Talk => "res://assets/art/ui/verb_talk.png",
        _ => "res://assets/art/ui/verb_kick.png",
    };
}
