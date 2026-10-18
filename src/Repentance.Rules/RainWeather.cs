namespace Repentance;

/// <summary>
/// How hard it rains in 1927 Chicago as the story goes on: a steady rain in Act 1, heavier in Act 2, a downpour in
/// Act 3. Scales the values a <c>Rain</c> node is authored with (its Act 1 look) and the rain ambience's level.
/// </summary>
public readonly record struct RainWeather(float Density, float Speed, int ExtraLength, float VolumeDb)
{
    public static RainWeather ForAct(int act) => act switch
    {
        <= 1 => new(1f, 1f, 0, 0f),
        2 => new(1.6f, 1.15f, 1, 2f),
        _ => new(2.6f, 1.35f, 3, 4.5f),
    };
}
