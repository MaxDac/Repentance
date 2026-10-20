using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>A pane of glass (or a patch of sky) that rain is drawn through, in scene pixels.</summary>
public readonly record struct RainPane(float X, float Y, float Width, float Height)
{
    public float Right => X + Width;
    public float Bottom => Y + Height;

    /// <summary>Pixels of wall or frame between this pane and <paramref name="o"/>; 0 when they touch or overlap.</summary>
    public float GapTo(RainPane o) =>
        MathF.Max(MathF.Max(o.X - Right, X - o.Right), MathF.Max(MathF.Max(o.Y - Bottom, Y - o.Bottom), 0f));
}

/// <summary>
/// Groups the panes of one window, so the rain falls through the whole window as one field and only the muntins
/// between its panes hide it, instead of every pane raining on its own.
/// </summary>
public static class RainPanes
{
    /// <summary>Widest muntin or glazing bar between two panes of the same window.</summary>
    public const float MaxMuntin = 6f;

    /// <summary>Indices of <paramref name="panes"/> grouped into windows, transitively, in first-pane order.</summary>
    public static List<List<int>> Windows(IReadOnlyList<RainPane> panes, float maxGap = MaxMuntin)
    {
        var window = new int[panes.Count];
        for (int i = 0; i < window.Length; i++) window[i] = i;
        int Find(int i) { while (window[i] != i) i = window[i] = window[window[i]]; return i; }
        for (int i = 0; i < panes.Count; i++)
            for (int j = i + 1; j < panes.Count; j++)
                if (panes[i].GapTo(panes[j]) <= maxGap)
                {
                    int a = Find(i), b = Find(j);
                    if (a != b) window[Math.Max(a, b)] = Math.Min(a, b);
                }
        var groups = new List<List<int>>();
        var byRoot = new Dictionary<int, List<int>>();
        for (int i = 0; i < panes.Count; i++)
        {
            int r = Find(i);
            if (!byRoot.TryGetValue(r, out var g)) { byRoot[r] = g = new List<int>(); groups.Add(g); }
            g.Add(i);
        }
        return groups;
    }

    /// <summary>The smallest rectangle around the given panes.</summary>
    public static RainPane Bounds(IReadOnlyList<RainPane> panes, IEnumerable<int> indices)
    {
        float x0 = float.MaxValue, y0 = float.MaxValue, x1 = float.MinValue, y1 = float.MinValue;
        foreach (int i in indices)
        {
            x0 = MathF.Min(x0, panes[i].X); y0 = MathF.Min(y0, panes[i].Y);
            x1 = MathF.Max(x1, panes[i].Right); y1 = MathF.Max(y1, panes[i].Bottom);
        }
        return new RainPane(x0, y0, x1 - x0, y1 - y0);
    }
}
