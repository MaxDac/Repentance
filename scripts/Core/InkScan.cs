using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace Repentance;

/// <summary>One choice line of the Ink script, as the player would see it.</summary>
/// <param name="Knot">"knot" or "knot.stitch" the choice belongs to.</param>
/// <param name="Label">Shown text; an inline <c>{...}</c> becomes a wildcard in <see cref="InkScan.Matches"/>.</param>
/// <param name="Sticky"><c>+</c> choices can be picked again; <c>*</c> choices are used up once picked.</param>
/// <param name="Fallback">A choice without text (<c>* -> knot</c>), taken automatically when nothing else is left.</param>
/// <param name="Conditional">Guarded by a <c>{condition}</c>, so it may not be offered.</param>
public sealed record InkChoice(string Knot, int Line, string Label, bool Sticky, bool Fallback, bool Conditional);

/// <summary>
/// A light static reader for dialogue/repentance.ink: knots, choices and calls to the game's external functions.
/// Godot-free, so the story checks run under xunit; the playthrough also uses it to measure choice coverage.
/// </summary>
public sealed class InkScan
{
    private static readonly Regex KnotHeader = new(@"^===\s*(function\s+)?(\w+)");
    private static readonly Regex StitchHeader = new(@"^=\s*(\w+)");
    private static readonly Regex Call = new(@"\b(set_flag|has_flag|give_item|take_item|has_item|knows_note)\(\s*""([^""]+)""");
    private static readonly Regex Condition = new(@"^\{[^{}]*\}\s*");
    private static readonly Regex LabelName = new(@"^\(\w+\)\s*");

    public List<string> Knots { get; } = new();
    public HashSet<string> Functions { get; } = new();
    public List<InkChoice> Choices { get; } = new();
    /// <summary>External call name ("set_flag", "has_item", ...) → literal arguments, in order of appearance.</summary>
    public Dictionary<string, List<string>> Calls { get; } = new();

    public static InkScan Parse(string text)
    {
        var scan = new InkScan();
        string knot = "", current = "";
        var lines = text.Split('\n');
        for (int i = 0; i < lines.Length; i++)
        {
            string line = StripComment(lines[i]).Trim();
            if (line.Length == 0) continue;
            if (KnotHeader.Match(line) is { Success: true } k)
            {
                knot = current = k.Groups[2].Value;
                if (k.Groups[1].Success) scan.Functions.Add(knot);
                else scan.Knots.Add(knot);
                continue;
            }
            if (StitchHeader.Match(line) is { Success: true } s && !line.StartsWith("=="))
            {
                current = $"{knot}.{s.Groups[1].Value}";
                scan.Knots.Add(current);
                continue;
            }
            foreach (Match m in Call.Matches(line))
            {
                if (!scan.Calls.TryGetValue(m.Groups[1].Value, out var list)) scan.Calls[m.Groups[1].Value] = list = new();
                list.Add(m.Groups[2].Value);
            }
            if (line[0] is '*' or '+') scan.Choices.Add(ParseChoice(current, i + 1, line));
        }
        return scan;
    }

    private static string StripComment(string line)
    {
        int c = line.IndexOf("//", StringComparison.Ordinal);
        return c >= 0 ? line[..c] : line;
    }

    private static InkChoice ParseChoice(string knot, int number, string line)
    {
        bool sticky = line[0] == '+';
        string rest = line.TrimStart('*', '+', ' ', '\t');
        rest = LabelName.Replace(rest, "");
        bool conditional = false;
        while (Condition.Match(rest) is { Success: true } c)
        {
            conditional = true;
            rest = rest[c.Length..];
        }
        string label;
        int open = rest.IndexOf('[');
        if (open >= 0)
        {
            int close = rest.IndexOf(']', open);
            label = rest[..open] + rest[(open + 1)..(close < 0 ? rest.Length : close)];
        }
        else
        {
            int divert = rest.IndexOf("->", StringComparison.Ordinal);
            label = divert >= 0 ? rest[..divert] : rest;
        }
        label = label.Trim();
        return new InkChoice(knot, number, label, sticky, label.Length == 0, conditional);
    }

    /// <summary>All literal arguments of an external call, e.g. every flag passed to <c>set_flag</c>.</summary>
    public IReadOnlyList<string> Args(string function) =>
        Calls.TryGetValue(function, out var list) ? list : Array.Empty<string>();

    /// <summary>
    /// Knots whose choices are all one-time <c>*</c> choices (a one-time fallback is used up too): a conversation there
    /// can only be run so many times before Ink has nothing left to offer. Each must be a cutscene the game plays once.
    /// </summary>
    public IEnumerable<string> OneShotKnots() => Choices
        .GroupBy(c => c.Knot)
        .Where(g => g.All(c => !c.Sticky))
        .Select(g => g.Key);

    /// <summary>Whether <paramref name="shown"/>, an option label the game displayed, is this choice.</summary>
    public static bool Matches(InkChoice choice, string shown)
    {
        if (!choice.Label.Contains('{')) return choice.Label == shown;
        var pattern = "^" + string.Join(".*", Regex.Split(choice.Label, @"\{[^{}]*\}").Select(Regex.Escape)) + "$";
        return Regex.IsMatch(shown, pattern);
    }
}
