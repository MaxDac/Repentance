#if TOOLS
using Godot;
using GodotInk;
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Runtime.CompilerServices;

namespace Repentance;

public partial class AutoPlay
{
    private void InheritanceContractTest()
    {
        const BindingFlags declared = BindingFlags.DeclaredOnly | BindingFlags.Instance |
            BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic;
        var assembly = typeof(Game).Assembly;
        using var symbols = File.OpenRead(ProjectSettings.GlobalizePath(
            $"res://.godot/mono/temp/bin/Debug/{assembly.GetName().Name}.pdb"));
        using var provider = MetadataReaderProvider.FromPortablePdbStream(symbols);
        var metadata = provider.GetMetadataReader();
        int checkedMethods = 0;
        foreach (var type in assembly.GetTypes().Where(t => t.IsClass && !t.IsDefined(typeof(CompilerGeneratedAttribute))))
        foreach (var method in type.GetMethods(declared))
        {
            if ((method.IsDefined(typeof(CompilerGeneratedAttribute)) && !method.IsSpecialName) ||
                method.GetBaseDefinition() != method) continue;
            var debug = metadata.GetMethodDebugInformation(MetadataTokens.MethodDefinitionHandle(method.MetadataToken & 0xFFFFFF));
            var documents = debug.GetSequencePoints().Select(p => p.Document).Where(d => !d.IsNil).Distinct().ToArray();
            // Godot generates hidden static registration methods; exclude their origin, not their names.
            if (documents.Length == 0 || documents.All(d =>
                metadata.GetString(metadata.GetDocument(d).Name).Replace('\\', '/').Contains("/Godot.SourceGenerators/")))
                continue;
            checkedMethods++;
            for (var parent = type.BaseType; parent != null; parent = parent.BaseType)
            foreach (var inherited in parent.GetMethods(declared).Where(m =>
                !m.IsPrivate && (m.IsPublic || m.IsFamily || m.IsFamilyOrAssembly || m.DeclaringType!.Assembly == assembly)))
            {
                if (method.Name != inherited.Name || method.GetGenericArguments().Length != inherited.GetGenericArguments().Length ||
                    !method.GetParameters().Select(p => ParameterSignature(p.ParameterType))
                        .SequenceEqual(inherited.GetParameters().Select(p => ParameterSignature(p.ParameterType))))
                    continue;
                Check(false, $"{type.FullName}.{method.Name} hides {parent.FullName}.{inherited.Name}; use its extension hook or a distinct name");
            }
        }
        Check(checkedMethods > 0, $"inheritance contracts checked across {checkedMethods} declared methods");
    }

    private static string ParameterSignature(Type type)
    {
        if (type.IsGenericParameter)
            return $"{(type.DeclaringMethod == null ? "type" : "method")}:{type.GenericParameterPosition}";
        if (type.HasElementType)
            return $"{(type.IsArray ? $"array:{type.GetArrayRank()}" : type.IsByRef ? "ref" : "pointer")}<{ParameterSignature(type.GetElementType()!)}>";
        if (type.IsGenericType)
            return $"{type.GetGenericTypeDefinition()}<{string.Join(",", type.GetGenericArguments().Select(ParameterSignature))}>";
        return type.AssemblyQualifiedName!;
    }

    private void InkResetTest()
    {
        string json = new Ink.Compiler("""
            EXTERNAL record()
            VAR counter = 0
            -> start
            === start ===
            Ready.
            + [Increment]
                ~ counter = counter + 1
                ~ record()
                Changed.
                -> start
            """, new Ink.Compiler.Options { countAllVisits = true }).Compile().ToJson();

        using var empty = new InkStory();
        using var stub = new StubInkStory();
        using var story = InkStory.Create(json);
        foreach (Resource resource in new Resource[] { empty, stub, story })
        {
            resource.ResetState();
            resource.Call(Resource.MethodName.ResetState);
        }
        Check(true, "empty, stub, and importer-created Ink resources can reset before initialization");

        // Loading assigns this serialized property through Godot's generated setter.
        story.Set("RawStory", json);
        int externalCalls = 0, variableChanges = 0, continued = 0, choicesMade = 0;
        story.BindExternalFunction("record", new Action(() => externalCalls++));
        story.ObserveVariable("counter", Callable.From<string, Variant>((_, _) => variableChanges++));
        story.Continued += () => continued++;
        story.MadeChoice += _ => choicesMade++;

        Action[] resets =
        {
            () => story.ResetState(),
            () => ((Resource)story).ResetState(),
            () => story.Call(Resource.MethodName.ResetState),
        };
        foreach (var reset in resets.Concat(resets))
        {
            Check(story.FetchVariable<int>("counter") == 0 && story.VisitCountAtPathString("start") == 0 &&
                story.CanContinue && story.CurrentChoices.Count == 0, "reset restores initial variables, visits, choices, and continuation");
            int previousContinued = continued, previousChoices = choicesMade, previousExternal = externalCalls;
            Check(story.ContinueMaximally().Trim() == "Ready." && story.CurrentChoices.Count == 1,
                "compiled story content remains playable after reset");
            int previousChanges = variableChanges;
            story.ChooseChoiceIndex(0);
            story.ContinueMaximally();
            Check(story.FetchVariable<int>("counter") == 1 && story.VisitCountAtPathString("start") > 0 &&
                story.CurrentChoices.Count == 1, "fixture progresses and changes state before reset");
            Check(variableChanges == previousChanges + 1 && externalCalls == previousExternal + 1 &&
                choicesMade == previousChoices + 1 && continued == previousContinued + 3,
                "reset retains observers, external bindings, and signals without duplicate callbacks");
            reset();
        }
        Check(story.FetchVariable<int>("counter") == 0 && story.VisitCountAtPathString("start") == 0,
            "C#, base-typed, and native resets all reach the Ink reset hook");
        Check(typeof(InkStory).GetMethod(nameof(Resource.ResetState))!.DeclaringType == typeof(Resource),
            "InkStory inherits the public resource reset entry point");

        using var imported = ResourceLoader.Load<InkStory>(DialogueManager.StoryPath, cacheMode: ResourceLoader.CacheMode.Ignore);
        imported.StoreVariable("pushes", 3);
        ((Resource)imported).ResetState();
        Check(imported.FetchVariable<int>("pushes") == 0, "normally imported story resets through Godot's resource lifecycle");
    }
}
#endif
