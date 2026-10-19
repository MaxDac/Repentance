namespace Repentance.Tests;

/// <summary>C# sources scanned as text: the Godot game (scripts/) and its Godot-free libraries (src/).</summary>
internal static class SourceFiles
{
    private static readonly string[] Folders = { "scripts", "src" };

    /// <summary>Every source file, build output excluded.</summary>
    public static IEnumerable<string> All(string root) =>
        Folders.SelectMany(folder => Directory.GetFiles(Path.Combine(root, folder), "*.cs", SearchOption.AllDirectories))
            .Where(f => !Normalized(f).Contains("/bin/") && !Normalized(f).Contains("/obj/"));

    /// <summary>Story code: <see cref="All"/> without the debug runners, which seed state on purpose.</summary>
    public static IEnumerable<string> Game(string root) =>
        All(root).Where(f => !Normalized(f).Contains("/scripts/Debug/"));

    private static string Normalized(string path) => path.Replace('\\', '/');
}
