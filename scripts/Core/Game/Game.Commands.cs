using Godot;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Repentance;

/// <summary>Executing "verb [item] hotspot" commands and the default responses.</summary>
public partial class Game
{
    /// <summary>Performs "verb [item] hotspot" as if the player clicked it (used by the autoplay test).</summary>
    public async Task Perform(Verb verb, string hotspotId, string? item = null)
    {
        var h = Room?.FindHotspot(hotspotId) ?? throw new InvalidOperationException($"No hotspot '{hotspotId}' in {Room?.Name}");
        await Execute(verb, h, item, h.Bounds.GetCenter());
    }

    private async Task Execute(Verb verb, Hotspot? target, string? item, Vector2 point)
    {
        int id = ++_actionId;
        if (target == null)
        {
            await WalkTo(point);
            return;
        }

        bool arrived = await WalkTo(ApproachPoint(target));
        if (!arrived || id != _actionId) return;

        if (target.Face != Facing.Auto) Player.Face(target.Face);
        else Player.FaceTowards(target.Bounds.GetCenter());

        await Run(async () =>
        {
            if (Room != null && await Room.OnInteract(verb, target, item)) return;
            if (verb is Verb.Walk or Verb.Hand && target.IsExit)
            {
                await ChangeRoom(target.ExitTo, target.ExitEntry);
                return;
            }
            if (verb == Verb.Walk) return;
            await DefaultResponse(verb, target, item);
        });
    }

    /// <summary>Where the player walks before acting on a hotspot: its WalkTo, or just below the middle of its shape.</summary>
    public static Vector2 ApproachPoint(Hotspot target) => target.WalkTo != Vector2.Zero
        ? target.WalkTo
        : new Vector2(target.Bounds.GetCenter().X, target.Bounds.End.Y + 4);

    private async Task DefaultResponse(Verb verb, Hotspot target, string? item)
    {
        bool person = target is Actor;
        switch (verb)
        {
            case Verb.Look:
                await Say(target.LookText != "" ? target.LookText : $"It's {Article(target.Title)}.");
                break;
            case Verb.Hand:
                await Say(person
                    ? "Let's keep our relationship professional."
                    : Pick("I don't need that.", "I'll leave it where it is.", "It's fine where it is.", "Nothing happens."));
                break;
            case Verb.Talk:
                await Say(person ? "They don't seem to want to talk." : Pick("It's not much of a talker.", "I've had better conversations with a lamppost."));
                break;
            case Verb.Kick:
                await Say(person ? "Tempting. But no." : Pick("It won't budge.", "Ow.", "Kicking things never solved anything. Mostly."));
                break;
            case Verb.UseItem when item != null:
                await Say(person ? "I don't think they'd want that." : Pick("That doesn't work.", "I don't think so."));
                break;
            default:
                await Say("Hmm.");
                break;
        }
    }
    private static string Article(string name) =>
        "aeiou".Contains(char.ToLowerInvariant(name[0])) ? "an " + name : "a " + name;

    public string Pick(params string[] options) => options[_rng.Next(options.Length)];
}
