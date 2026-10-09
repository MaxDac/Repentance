using Xunit;

namespace Repentance.Tests;

public class ItemsTests
{
    [Fact]
    public void Catalogue_IsNotEmpty() => Assert.NotEmpty(Items.All);

    [Fact]
    public void EveryItem_KeyMatchesIdAndHasContent()
    {
        foreach (var (key, def) in Items.All)
        {
            Assert.Equal(key, def.Id);
            Assert.False(string.IsNullOrWhiteSpace(def.Name));
            Assert.False(string.IsNullOrWhiteSpace(def.Description));
            Assert.StartsWith("res://assets/art/items/", def.IconPath);
        }
    }

    [Fact]
    public void Get_UnknownItem_Throws() =>
        Assert.Throws<KeyNotFoundException>(() => Items.Get("nope"));
}
