using System;
using System.Collections.Generic;
using System.Linq;

namespace Repentance;

public sealed record ItemDef(string Id, string Name, string IconPath, string Description);

/// <summary>
/// Inventory item catalogue. Items are listed per act in scripts/Core/Items/: add new ones to the act that
/// introduces them and drop a 32x24 icon in assets/art/items.
/// </summary>
public static partial class Items
{
    public static readonly IReadOnlyDictionary<string, ItemDef> All = Build(MicahItems(), Act1Items(), Act2Items(), Act3Items());

    private static Dictionary<string, ItemDef> Build(params ItemDef[][] lists)
    {
        var all = new Dictionary<string, ItemDef>();
        foreach (var item in lists.SelectMany(l => l))
            if (!all.TryAdd(item.Id, item))
                throw new InvalidOperationException($"Item '{item.Id}' is defined twice.");
        return all;
    }

    public static ItemDef Get(string id) => All[id];
}

public static class CashRules
{
    /// <summary>The bellboy's first dollar buys his memory, the second the staff door to Eleanor's room.</summary>
    public const int BellboyBribe = 1;
    public const int BellboyRoomBribe = 1;
    public const int SalBribe = 10;
    /// <summary>Tony's bathtub gin at the Blue Lantern.</summary>
    public const int GinPrice = 1;
    public const int StartingCash = 22;

    public static int Balance(System.Func<string, bool> hasFlag) =>
        !hasFlag("took_dollar") ? 0 : StartingCash
            - (hasFlag("knows_lantern") ? BellboyBribe : 0)
            - (hasFlag("bellboy_room_paid") ? BellboyRoomBribe : 0)
            - (hasFlag("sal_passed") ? SalBribe : 0)
            - (hasFlag("lantern_gin_paid") ? GinPrice : 0);
}
