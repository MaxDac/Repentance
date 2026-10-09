namespace Repentance;

public enum Verb { WalkTo, Give, PickUp, Use, Open, LookAt, Push, Close, TalkTo, Pull }

public enum Facing { Auto, Down, Up, Left, Right }

public static class Verbs
{
    /// <summary>SCUMM-style 3x3 grid, row by row.</summary>
    public static readonly Verb[] Grid =
    {
        Verb.Give, Verb.PickUp, Verb.Use,
        Verb.Open, Verb.LookAt, Verb.Push,
        Verb.Close, Verb.TalkTo, Verb.Pull,
    };

    public static string Label(Verb v) => v switch
    {
        Verb.WalkTo => "Walk to",
        Verb.Give => "Give",
        Verb.PickUp => "Pick up",
        Verb.Use => "Use",
        Verb.Open => "Open",
        Verb.LookAt => "Look at",
        Verb.Push => "Push",
        Verb.Close => "Close",
        Verb.TalkTo => "Talk to",
        Verb.Pull => "Pull",
        _ => v.ToString(),
    };

    /// <summary>Verbs that take a second object ("Use X with Y", "Give X to Y").</summary>
    public static bool IsTwoObject(Verb v) => v is Verb.Use or Verb.Give;

    public static string Preposition(Verb v) => v == Verb.Give ? "to" : "with";
}
