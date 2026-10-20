using Xunit;

namespace Repentance.Tests;

/// <summary>One finger standing in for the mouse: tap, long press and drag.</summary>
public class TouchPointerTests
{
    private static PointerAction A(PointerKind kind, float x, float y) => new(kind, x, y);

    [Fact]
    public void TapIsALeftClickWhereTheFingerTouched()
    {
        var t = new TouchPointer();
        Assert.Equal(new[] { A(PointerKind.Move, 100, 50) }, t.Down(100, 50, 0));
        Assert.Empty(t.Move(103, 52, 0.05));
        Assert.Empty(t.Tick(0.1));
        Assert.Equal(new[] { A(PointerKind.LeftDown, 100, 50), A(PointerKind.LeftUp, 100, 50) }, t.Up(103, 52, 0.15));
        Assert.False(t.Active);
    }

    [Fact]
    public void HoldingStillPressesTheRightButtonThenDragsAndReleasesIt()
    {
        var t = new TouchPointer();
        t.Down(100, 50, 0);
        Assert.Empty(t.Tick(TouchPointer.HoldSeconds - 0.01));
        Assert.Equal(new[] { A(PointerKind.RightDown, 100, 50) }, t.Tick(TouchPointer.HoldSeconds));
        Assert.Equal(new[] { A(PointerKind.Move, 120, 50) }, t.Move(120, 50, 0.6));
        Assert.Equal(new[] { A(PointerKind.Move, 125, 50), A(PointerKind.RightUp, 125, 50) }, t.Up(125, 50, 0.7));
        Assert.False(t.Active);
    }

    [Fact]
    public void ALongPressReleasedBeforeAFrameTicksStillCountsAsHeld()
    {
        var t = new TouchPointer();
        t.Down(10, 10, 0);
        Assert.Equal(new[] { A(PointerKind.RightDown, 10, 10), A(PointerKind.RightUp, 10, 10) }, t.Up(10, 10, 1));
    }

    [Fact]
    public void MovingPastTheSlopDragsTheLeftButtonFromWhereTheTouchBegan()
    {
        var t = new TouchPointer();
        t.Down(100, 50, 0);
        Assert.Equal(new[] { A(PointerKind.LeftDown, 100, 50), A(PointerKind.Move, 100 + TouchPointer.Slop + 1, 50) },
            t.Move(100 + TouchPointer.Slop + 1, 50, 0.1));
        Assert.Empty(t.Tick(2));
        Assert.Equal(new[] { A(PointerKind.Move, 140, 50) }, t.Move(140, 50, 2));
        Assert.Equal(new[] { A(PointerKind.Move, 150, 50), A(PointerKind.LeftUp, 150, 50) }, t.Up(150, 50, 2.1));
    }
}
