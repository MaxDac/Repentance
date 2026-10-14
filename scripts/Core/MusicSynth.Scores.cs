using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace Repentance;

public static partial class MusicSynth
{
    private static Piece PieceFor(Track track) => track switch
    {
        Track.ClubStrings => Club,
        Track.ChurchOrgan => Church,
        Track.ConventPiano => Convent,
        Track.OfficeJazz => Office,
        _ => throw new ArgumentOutOfRangeException(nameof(track)),
    };

    private static string Repeat(string notes, int times) => string.Concat(Enumerable.Repeat(notes, times));

    // ------------------------------------------------------------------ the Club

    // A bolero in 3/4 on the D diminished (octatonic) colours, D Eb F# G# A C: all tritones (D-G#, A-Eb, C-F#), no
    // minor third. The double bass bows one slow four-bar ostinato in long swelling strokes for all 24 bars;
    // every note is bowed, at least a beat long, one stroke flowing into the next.
    // A four-bar theme comes round again and again: the cello alone, then over a second cello droning the tritones
    // beneath it, the viola an octave up, and at the very end two strident violins a tritone apart, before everything
    // falls away down to the bass, which leads home.
    private const string ClubTheme = "D3:2 Eb3:1 G#3:3 A3:2 F#3:1 C3:1 D3:2 ";

    private static readonly Piece Club = new(72, Concert, new Part[]
    {
        new(Instrument.DoubleBass, 0.95, 0.1, Repeat("D2:2 Eb2:1 G#1:3 F#1:2 C2:1 A1:3 ", 6)),
        new(Instrument.Cello, 0.75, 0.35,
            "r:12 " + Repeat(ClubTheme, 4) + "Eb3:2 C3:1 A2:2 G#2:1"),
        new(Instrument.Cello, 0.5, -0.1,
            "r:24 " + Repeat("G#2:3 D3:3 C3:3 A2:3 ", 3)),
        new(Instrument.Viola, 0.6, -0.3,
            "r:45 A3:3 " + ClubTheme.Replace("3:", "4:") + "C4:2 A3:1"),
        new(Instrument.Violin, 0.5, -0.45,
            "r:48 D5:2! Eb5:1! G#5:3! A5:2! F#5:1! C6:2! G#5:1!"),
        new(Instrument.Violin, 0.4, 0.45,
            "r:48 G#4:3! D5:3! C5:3! A4:3!"),
    });

    // ------------------------------------------------------------------ the church

    // Sixteen bars of 4/4 in a stone nave. The organist tries the instrument: a few pedal notes, a flute pipe and a
    // run up the D Dorian scale, a full-organ chord stabbed and let go. Then the mass: a plain, chant-like chorale,
    // its first phrase on the soft flutes and its second on the full chorus, closing bright on D major. Then back to
    // testing: one high pipe tapped again and again, a last low note, and the loop begins again with the pedals.
    private static readonly Piece Church = new(64, new Hall(1.6, 0.94, 0.25, 0.55), new Part[]
    {
        new(Instrument.OrganPedal, 0.9, 0.05,
            "D2:1 r:1 D2:1 r:1 A1:1 r:1 F2:1.5 r:0.5 r:8 D2:3 r:1 " +
            "D2:2 F2:2 G2:2 C2:2 A1:2 G1:2 F2:2 A1:2 " +
            "F2:2 G1:2 A1:2 C2:2 G2:2 E2:2 A1:2 D2:4 r:10"),
        new(Instrument.OrganFlute, 0.8, -0.3,
            "r:1 A4:0.5 r:1.5 A4:0.5 r:1.5 D5:2 r:1 " +
            "D4:0.25 E4:0.25 F4:0.25 G4:0.25 A4:0.25 B4:0.25 C5:0.25 D5:0.25 E5:0.25 F5:0.25 G5:0.25 A5:0.25 " +
            "B5:0.25 C6:0.25 D6:1.5 r:3 r:4 " +
            "D4+F4+A4:2 F4+A4+C5:2 G4+B4+D5:2 E4+G4+C5:2 C4+E4+A4:2 B3+D4+G4:2 D4+F4+A4:2 C#4+E4+A4:2 r:18 " +
            "D6:0.5 r:1 D6:0.5 r:1 D6:1.5 r:1 A4:3 r:1.5"),
        new(Instrument.OrganPlenum, 0.75, 0.25,
            "r:13 D4+F4+A4+D5:1.5 r:1.5 D4+A4+D5:2 r:2 r:16 " +
            "A3+C4+F4:2 B3+D4+G4:2 C4+E4+A4:2 E4+G4+C5:2 G4+B4+D5:2 E4+G4+C5:2 E4+A4+C#5:2 F#4+A4+D5:4 r:10"),
    });

    // ------------------------------------------------------------------ the convent

    // A prelude in Eb major, 3/4: the left hand rolls pedalled arpeggios bar after bar, the right hand sings a slow
    // hymn-like line above them. Twenty-two bars, ending on the dominant so the loop falls back home to Eb.
    private static readonly Piece Convent = new(66, new Hall(1.1, 0.86, 0.4, 0.28), new Part[]
    {
        new(Instrument.Piano, 0.45, -0.2, Arpeggios(
            "Eb2 Bb2 Eb3 G3|Eb2 Ab2 C3 Eb3|D2 Ab2 Bb2 F3|Eb2 Bb2 Eb3 G3|C2 G2 C3 Eb3|Ab1 Eb2 Ab2 C3|" +
            "F1 C2 Ab2 Eb3|Bb1 F2 Ab2 D3|G1 D2 G2 Bb2|C2 G2 C3 Eb3|Ab1 Eb2 Ab2 C3|Bb1 F2 Bb2 D3|" +
            "G1 Eb2 G2 Bb2|Ab1 Eb2 Ab2 C3|F1 C2 F2 Ab2|Bb1 F2 Bb2 Eb3|Bb1 F2 Ab2 D3|Eb2 Bb2 Eb3 G3|" +
            "Ab1 Eb2 Ab2 C3|Bb1 Eb2 G2 Bb2|F1 C2 Ab2 Eb3|Bb1 F2 Ab2 D3")),
        new(Instrument.Piano, 0.7, 0.2,
            "Bb4:2 G4:1 Ab4:2 C5:1 Bb4:1.5 Ab4:0.5 F4:1 G4:3 " +
            "G4:2 C5:1 Eb5:2 C5:1 Ab4:1.5 C5:0.5 Eb5:1 D5:3 " +
            "D5:2 Bb4:1 Eb5:2 C5:1 C5:1.5 Ab4:0.5 Eb5:1 F5:2 D5:1 " +
            "Eb5:2 Bb4:1 C5:2 Ab4:1 Ab4:1 G4:1 F4:1 Bb4:2 Eb5:1 " +
            "D5:2 Ab4:1 G4:3 C5:2 Eb5:1 Bb4:2 G4:1 Ab4:1 C5:1 Eb5:1 D5:2 r:1"),
    });

    /// <summary>
    /// Pedalled left-hand arpeggios, one 3/4 bar per four-note chord (low to high, separated by <c>|</c>): six eighth
    /// notes up and back down, each ringing until it is struck again or the bar is over.
    /// </summary>
    private static string Arpeggios(string chords)
    {
        int[] order = { 0, 1, 2, 3, 2, 1 };
        var sb = new StringBuilder();
        foreach (var chord in chords.Split('|'))
        {
            var notes = chord.Split(' ', StringSplitOptions.RemoveEmptyEntries);
            for (int i = 0; i < order.Length; i++)
            {
                int again = Array.IndexOf(order, order[i], i + 1);
                double held = again > 0 ? (again - i) * 0.5 : 3.5 - 0.5 * i;
                sb.Append(FormattableString.Invariant($"{notes[order[i]]}:0.5>{held} "));
            }
        }
        return sb.ToString();
    }

    // ------------------------------------------------------------------ the office

    // A 32-bar AABA chorus in F at a relaxed two-beat swing, as a small Chicago band might have cut it in 1927: the
    // clarinet sings the tune low and soft in swung eighths, the piano answers on two and four, the upright bass plucks
    // roots and fifths, and brushes sweep the snare under a quiet ride. All of it heard through a gramophone horn.
    private const string JazzTheme =
        "r:1 A4:2/3 C5:1/3 D5:1 C5:1 F#4:2/3 A4:1/3 C5:2/3 D5:1/3 Eb5:2 D5:1 B4:2/3 G4:1/3 F5:1 D5:1 E5:3 r:1 " +
        "F5:2/3 E5:1/3 D5:2/3 C5:1/3 A4:1 F#4:1 G4:1 Bb4:2/3 D5:1/3 E5:2/3 G5:1/3 Bb4:1 ";

    private const string JazzBridge =
        "E5:2/3 C#5:1/3 A4:1 E5:2 G5:2/3 F5:1/3 E5:2/3 C#5:1/3 A4:2 D5:3 F5:1 A5:2 F5:2/3 D5:1/3 A4:1 " +
        "B4:2/3 D5:1/3 G5:1 F5:2/3 D5:1/3 B4:1 G4:3 r:1 E5:2/3 G5:1/3 Bb5:1 A5:2/3 G5:1/3 E5:1 Bb4:2 G4:1 C5:1 ";

    private const string JazzBassA = "F2:2 C2:2 D2:2 A1:2 G1:2 D2:2 C2:2 G1:2 F2:2 D2:2 G1:2 C2:2 F2:2 C2:2 ";

    // declared before Office: static fields initialize in order
    private static readonly Dictionary<string, string> JazzChords = new()
    {
        ["F6"] = "A3+C4+D4+F4", ["D7"] = "A3+C4+F#4", ["G7"] = "B3+D4+F4", ["C7"] = "Bb3+E4+G4",
        ["Gm7"] = "Bb3+D4+F4", ["A7"] = "C#4+E4+G4", ["Dm"] = "A3+D4+F4", ["E7"] = "G#3+D4+E4",
    };

    private static readonly Piece Office = new(128, new Hall(0.6, 0.75, 0.5, 0.15), new Part[]
    {
        new(Instrument.Clarinet, 0.55, -0.15,
            JazzTheme + "A4:4 r:1 G4:2/3 A4:1/3 Bb4:2/3 C5:1/3 Db5:1 " +
            JazzTheme + "F4:3 r:1 r:1 E4:2/3 F4:1/3 G4:2/3 A4:1/3 C#5:1 " +
            JazzBridge +
            JazzTheme + "F5:2 D5:2/3 C5:1/3 A4:1 G4:2/3 A4:1/3 Bb4:2/3 C5:1/3 r:2"),
        new(Instrument.Piano, 0.42, 0.25, Comping(
            "F6|D7|G7|C7|F6 D7|Gm7 C7|F6|C7|F6|D7|G7|C7|F6 D7|Gm7 C7|F6|F6 E7|" +
            "A7|A7|Dm|Dm|G7|G7|C7|C7|F6|D7|G7|C7|F6 D7|Gm7 C7|F6|C7")),
        new(Instrument.UprightBass, 0.85, 0.05,
            JazzBassA + "C2:2 E2:2 " + JazzBassA + "F2:2 E2:2 " +
            "A1:2 E2:2 A1:2 C#2:2 D2:2 A1:2 D2:2 F2:2 G1:2 D2:2 G1:2 B1:2 C2:2 G1:2 C2:2 E2:2 " +
            JazzBassA + "C2:2 E2:2"),
        new(Instrument.Drums, 0.5, 0.1, Repeat("E2:4 ", 32)),
        new(Instrument.Drums, 0.35, 0.3, Repeat("r:1 F#2:1 r:1 F#2:1 ", 32)),
        new(Instrument.Drums, 0.3, -0.3, Repeat("Eb3:1 Eb3:2/3 Eb3:1/3 Eb3:1 Eb3:2/3 Eb3:1/3 ", 32)),
        new(Instrument.Drums, 0.3, 0, Repeat("C2:1 ", 128)),
    });

    /// <summary>Short piano chords on two and four, one 4/4 bar per <c>|</c>; a bar with two chords changes on beat three.</summary>
    private static string Comping(string bars)
    {
        var sb = new StringBuilder();
        foreach (var bar in bars.Split('|'))
        {
            var chords = bar.Split(' ');
            sb.Append($"r:1 {JazzChords[chords[0]]}:1>0.6 r:1 {JazzChords[chords[^1]]}:1>0.6 ");
        }
        return sb.ToString();
    }
}
