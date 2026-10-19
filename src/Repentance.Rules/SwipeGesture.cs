using System;

namespace Repentance;

/// <summary>
/// Turns a pointer drag into unit grid steps for the arrow-pad puzzles. Each time the drag has travelled
/// <see cref="StepDistance"/> along its dominant axis since the last step, one step is emitted in that direction:
/// a short flick moves once, a long drag along a corridor moves several times.
/// </summary>
public sealed class SwipeGesture
{
    public float StepDistance { get; }
    private float _x, _y;

    public SwipeGesture(float x, float y, float stepDistance)
    {
        if (stepDistance <= 0) throw new ArgumentOutOfRangeException(nameof(stepDistance));
        StepDistance = stepDistance;
        _x = x;
        _y = y;
    }

    /// <summary>
    /// The next step for a pointer now at (x, y), or null while the drag hasn't covered a full step. Call again
    /// until null: one fast motion can cover several steps.
    /// </summary>
    public GridPoint? Next(float x, float y)
    {
        float dx = x - _x, dy = y - _y;
        bool horizontal = Math.Abs(dx) >= Math.Abs(dy);
        float along = horizontal ? dx : dy;
        if (Math.Abs(along) < StepDistance) return null;
        var step = horizontal ? new GridPoint(Math.Sign(dx), 0) : new GridPoint(0, Math.Sign(dy));
        // advance the anchor one step along the axis; the cross axis restarts at the pointer so diagonals pick a side each step
        if (horizontal) { _x += step.X * StepDistance; _y = y; }
        else { _y += step.Y * StepDistance; _x = x; }
        return step;
    }
}
