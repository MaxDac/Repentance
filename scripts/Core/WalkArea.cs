using Godot;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Walkable floor of a room, defined by a (possibly concave) polygon. Draw it in the editor as a
/// Polygon2D named "WalkArea" (it's hidden at runtime). Paths are found with a visibility graph
/// over the polygon's concave corners, which is plenty for adventure-game rooms.
/// </summary>
public sealed class WalkArea
{
    private readonly Vector2[] _poly;
    private readonly List<Vector2> _nodes = new();

    public WalkArea(Vector2[] polygon)
    {
        _poly = polygon;
        int n = _poly.Length;
        for (int i = 0; i < n; i++)
        {
            Vector2 prev = _poly[(i + n - 1) % n], cur = _poly[i], next = _poly[(i + 1) % n];
            var bis = (prev - cur).Normalized() + (next - cur).Normalized();
            if (bis.LengthSquared() < 0.0001f) continue;
            bis = bis.Normalized();
            // Reflex (inward-pointing) corners are the only places a shortest path bends around.
            if (!Contains(cur + bis * 1.5f))
            {
                var p = cur - bis * 1.5f;
                if (Contains(p)) _nodes.Add(p);
            }
        }
    }

    public bool Contains(Vector2 p) => Geometry2D.IsPointInPolygon(p, _poly);

    /// <summary>Closest walkable point to <paramref name="p"/>.</summary>
    public Vector2 Clamp(Vector2 p)
    {
        if (Contains(p)) return p;
        Vector2 best = _poly[0];
        float bestD = float.MaxValue;
        for (int i = 0; i < _poly.Length; i++)
        {
            var c = Geometry2D.GetClosestPointToSegment(p, _poly[i], _poly[(i + 1) % _poly.Length]);
            float d = c.DistanceSquaredTo(p);
            if (d < bestD) { bestD = d; best = c; }
        }
        // nudge inside
        foreach (var dir in new[] { Vector2.Up, Vector2.Down, Vector2.Left, Vector2.Right,
                     new Vector2(1, 1), new Vector2(-1, 1), new Vector2(1, -1), new Vector2(-1, -1) })
        {
            for (int k = 1; k <= 3; k++)
            {
                var q = best + dir * k;
                if (Contains(q)) return q;
            }
        }
        return best;
    }

    private bool Visible(Vector2 a, Vector2 b)
    {
        if (a.DistanceSquaredTo(b) < 0.01f) return true;
        for (int i = 0; i < _poly.Length; i++)
        {
            Vector2 c = _poly[i], d = _poly[(i + 1) % _poly.Length];
            var hit = Geometry2D.SegmentIntersectsSegment(a, b, c, d);
            if (hit.VariantType != Variant.Type.Nil)
            {
                var h = hit.AsVector2();
                if (h.DistanceSquaredTo(a) > 0.25f && h.DistanceSquaredTo(b) > 0.25f) return false;
            }
        }
        // sample along the segment to catch grazing a reflex corner
        for (int s = 1; s < 8; s++)
            if (!Contains(a.Lerp(b, s / 8f))) return false;
        return true;
    }

    /// <summary>Shortest path from <paramref name="from"/> to <paramref name="to"/> (both clamped inside).</summary>
    public List<Vector2> FindPath(Vector2 from, Vector2 to)
    {
        from = Clamp(from);
        to = Clamp(to);
        if (Visible(from, to)) return new List<Vector2> { to };

        var pts = new List<Vector2> { from };
        pts.AddRange(_nodes);
        pts.Add(to);
        int n = pts.Count, goal = n - 1;
        var dist = new float[n];
        var prev = new int[n];
        var done = new bool[n];
        for (int i = 0; i < n; i++) { dist[i] = float.MaxValue; prev[i] = -1; }
        dist[0] = 0;
        for (int iter = 0; iter < n; iter++)
        {
            int u = -1;
            for (int i = 0; i < n; i++)
                if (!done[i] && (u < 0 || dist[i] < dist[u])) u = i;
            if (u < 0 || dist[u] == float.MaxValue) break;
            if (u == goal) break;
            done[u] = true;
            for (int v = 0; v < n; v++)
            {
                if (done[v] || v == u) continue;
                float nd = dist[u] + pts[u].DistanceTo(pts[v]);
                if (nd < dist[v] && Visible(pts[u], pts[v])) { dist[v] = nd; prev[v] = u; }
            }
        }
        var path = new List<Vector2>();
        if (prev[goal] < 0) { path.Add(to); return path; }
        for (int at = goal; at != 0; at = prev[at]) path.Add(pts[at]);
        path.Reverse();
        return path;
    }
}
