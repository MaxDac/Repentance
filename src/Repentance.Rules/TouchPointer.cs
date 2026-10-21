using System;
using System.Collections.Generic;

namespace Repentance;

public enum PointerKind { Move, LeftDown, LeftUp, RightDown, RightUp }

/// <summary>A mouse event the touch screen stands in for, in game pixels.</summary>
public readonly record struct PointerAction(PointerKind Kind, float X, float Y);

/// <summary>
/// Turns one finger into the mouse the game is played with. A tap is a left click where it touched; holding still
/// for <see cref="HoldSeconds"/> presses the right button there (the verb wheel), and the finger then drags and
/// releases it like a mouse; moving more than <see cref="Slop"/> first presses the left button where the touch began
/// and drags it (puzzle swipes, notepad pages).
/// </summary>
public sealed class TouchPointer
{
    public const double HoldSeconds = 0.45;
    public const float Slop = 6;

    private enum State { Idle, Pending, Dragging }

    private State _state;
    private bool _right;
    private float _x0, _y0;
    private double _t0;

    public bool Active => _state != State.Idle;

    public IReadOnlyList<PointerAction> Down(float x, float y, double time)
    {
        var actions = new List<PointerAction>();
        if (_state == State.Dragging) actions.Add(new(_right ? PointerKind.RightUp : PointerKind.LeftUp, _x0, _y0));
        (_state, _x0, _y0, _t0) = (State.Pending, x, y, time);
        actions.Add(new(PointerKind.Move, x, y));
        return actions;
    }

    public IReadOnlyList<PointerAction> Move(float x, float y, double time)
    {
        var actions = new List<PointerAction>();
        if (_state == State.Pending)
        {
            actions.AddRange(Tick(time));
            if (_state == State.Pending)
            {
                if (MathF.Abs(x - _x0) <= Slop && MathF.Abs(y - _y0) <= Slop) return actions;
                _state = State.Dragging;
                _right = false;
                actions.Add(new(PointerKind.LeftDown, _x0, _y0));
            }
        }
        if (_state == State.Dragging) actions.Add(new(PointerKind.Move, x, y));
        return actions;
    }

    public IReadOnlyList<PointerAction> Up(float x, float y, double time)
    {
        var actions = new List<PointerAction>();
        switch (_state)
        {
            case State.Pending:
                actions.AddRange(Tick(time));
                if (_state == State.Pending)
                {
                    actions.Add(new(PointerKind.LeftDown, _x0, _y0));
                    actions.Add(new(PointerKind.LeftUp, _x0, _y0));
                    break;
                }
                actions.Add(new(PointerKind.RightUp, _x0, _y0));
                break;
            case State.Dragging:
                actions.Add(new(PointerKind.Move, x, y));
                actions.Add(new(_right ? PointerKind.RightUp : PointerKind.LeftUp, x, y));
                break;
        }
        _state = State.Idle;
        return actions;
    }

    /// <summary>Call every frame: a finger held still long enough presses the right button.</summary>
    public IReadOnlyList<PointerAction> Tick(double time)
    {
        if (_state != State.Pending || time - _t0 < HoldSeconds) return Array.Empty<PointerAction>();
        _state = State.Dragging;
        _right = true;
        return new[] { new PointerAction(PointerKind.RightDown, _x0, _y0) };
    }
}
