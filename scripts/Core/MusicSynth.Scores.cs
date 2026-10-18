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
        Track.BlueLanternJazz => Lantern,
        Track.BlueLanternAlley => LanternAlley,
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

    // A slow, depressed ballad in D minor at an adagio drag, in the late-night vein of Chet Baker or Kind of Blue: the
    // record a washed-up, half-drunk private eye leaves on after the bottle is empty. Sixteen bars, AABA, four to a
    // section. A Harmon-muted trumpet plays few notes and leaves a lot of air between them: long aching tones, a
    // lazy swung eighth here and there, every phrase falling. The piano rolls one soft chord a bar (two when the
    // harmony moves), and the upright bass walks nothing, just roots and fifths on half notes. No drums: nobody is
    // keeping time any more. The last A ends on the leading tone over A7, falling home to D.
    private const string BalladOpening =
        "r:1 E4:3 r:2/3 F4:1/3 E4:2/3 D4:1/3 B3:2 r:1 Bb4:2 A4:2/3 G4:1/3 ";

    private const string BalladBridge =
        "Bb4:3 A4:2/3 G4:1/3 E4:2 r:2/3 D4:1/3 E4:1 r:2/3 G4:1/3 A4:3 Bb4:2/3 G4:1/3 E4:1 C#4:2 ";

    private const string BalladBassA = "D2:2 A1:2 D2:2 B1:2 E2:2 A1:2 ";

    // declared before Office: static fields initialize in order
    private static readonly Dictionary<string, string> BalladChords = new()
    {
        ["Dm9"] = "F3+A3+C4+E4", ["Dm6"] = "F3+A3+B3+D4", ["Dm7"] = "C3+F3+A3+D4", ["Em7b5"] = "E3+G3+Bb3+D4",
        ["A7b9"] = "G3+Bb3+C#4+E4", ["D7b9"] = "F#3+C4+Eb4+A4", ["Gm9"] = "Bb3+D4+F4+A4", ["C9"] = "Bb3+D4+E4+G4",
        ["Fmaj9"] = "A3+C4+E4+G4",
    };

    private static readonly Piece Office = new(66, new Hall(0.8, 0.82, 0.6, 0.2), new Part[]
    {
        new(Instrument.Trumpet, 0.45, -0.15,
            BalladOpening + "F4:2/3 E4:1/3 D4:1 C#4:1 r:1 " +
            BalladOpening + "D4:2 r:2/3 F#4:1/3 A4:1 " +
            BalladBridge +
            BalladOpening + "F4:2/3 E4:1/3 C#4:2 r:1"),
        new(Instrument.Piano, 0.3, 0.25, Rolled(
            "Dm9|Dm6|Em7b5 A7b9|Dm9 A7b9|Dm9|Dm6|Em7b5 A7b9|Dm7 D7b9|" +
            "Gm9|C9|Fmaj9|Em7b5 A7b9|Dm9|Dm6|Em7b5 A7b9|Dm9 A7b9")),
        new(Instrument.UprightBass, 0.8, 0.05,
            BalladBassA + "D2:2 A1:2 " + BalladBassA + "D2:2 F#2:2 " +
            "G1:2 D2:2 C2:2 G1:2 F1:2 C2:2 E2:2 A1:2 " +
            BalladBassA + "D2:2 A1:2"),

    });

    /// <summary>
    /// Soft piano chords rolled from the bottom up, one 4/4 bar per <c>|</c>; a bar with two chords changes on beat
    /// three. Each note of a chord follows the one below it by an eighth of a beat and rings until the chord changes.
    /// </summary>
    private static string Rolled(string bars)
    {
        var sb = new StringBuilder();
        foreach (var bar in bars.Split('|'))
        {
            var chords = bar.Split(' ');
            int eighths = 32 / chords.Length;
            foreach (var chord in chords)
            {
                var notes = BalladChords[chord].Split('+');
                for (int i = 0; i < notes.Length; i++)
                {
                    int advance = i < notes.Length - 1 ? 1 : eighths - i;
                    sb.Append($"{notes[i]}:{advance}/8>{eighths - i}/8 ");
                }
            }
        }
        return sb.ToString();
    }

    // ------------------------------------------------------------------ the Blue Lantern

    // A Chicago hot band rehearsing behind the curtain, Hot Five fashion, in an original sixteen-bar strain in Bb at a
    // fast two-beat: the cornet leads, the clarinet weaves above it, the trombone smears tailgate lines below, the
    // banjo chunks four to the bar, the tuba blows on one and three, the piano comps on two and four over kick and
    // snare. One chorus; the second has a stop-time break for the cornet; the third falls apart in its fifth bar on a
    // trombone clam. Then the rehearsal: the clarinet noodles on alone, the piano runs up the scale, the cornet tries
    // the break, fluffs it, the tuba and banjo check a note, the cornet gets the break right, the trombone warms up,
    // and the drummer clicks his sticks, "one... two... one, two, three, four", into the top of the loop.
    private static readonly string[] LanternStrain =
        { "Bb", "Bb", "F7", "F7", "Bb", "Bb7", "Eb", "Eb", "Bb", "G7", "C7", "F7", "Bb", "G7", "C7 F7", "Bb" };

    /// <summary>Choruses one and two, the second with its stop-time break (bars 7-8, marked <c>*</c>), and the first
    /// four bars of the third: the bars the whole band plays together.</summary>
    private static readonly string[] LanternChart = LanternStrain
        .Concat(LanternStrain.Select((c, i) => i is 6 or 7 ? c + "*" : c))
        .Concat(LanternStrain.Take(4)).ToArray();

    /// <summary>Per chord: the tuba's root and fifth, the banjo's voicing and the piano's.</summary>
    private static readonly Dictionary<string, (string Root, string Fifth, string Banjo, string Piano)> LanternChords = new()
    {
        ["Bb"] = ("Bb1", "F2", "D4+F4+Bb4", "F3+Bb3+D4"),
        ["F7"] = ("F1", "C2", "C4+Eb4+F4+A4", "Eb3+A3+C4"),
        ["Bb7"] = ("Bb1", "F2", "D4+F4+Ab4", "Ab3+D4+F4"),
        ["Eb"] = ("Eb2", "Bb1", "Eb4+G4+Bb4", "G3+Bb3+Eb4"),
        ["G7"] = ("G1", "D2", "D4+F4+G4+B4", "F3+B3+D4"),
        ["C7"] = ("C2", "G1", "C4+E4+G4+Bb4", "E3+Bb3+C4"),
    };

    private const string CornetBreak = "G4:2/3 Bb4:1/3 Eb5:2/3 G5:1/3 F5:2/3 Eb5:1/3 D5:2/3 Db5:1/3|C5:2/3 Bb4:1/3 G4:2/3 Bb4:1/3 Eb5:2";

    private static readonly string[] CornetLead =
    {
        "r:2/3 F4:1/3 Bb4:1 D5:1 Bb4:2/3 C5:1/3", "D5:2 r:1 Bb4:2/3 C5:1/3", "C5:1 A4:2/3 C5:1/3 Eb5:1.5 r:0.5",
        "D5:2/3 C5:1/3 A4:1 F4:2", "r:1 F4:2/3 Bb4:1/3 D5:1 F5:1", "F5:2/3 Eb5:1/3 D5:1 Ab4:2",
        "G4:1 Bb4:1 Eb5:1 r:2/3 G4:1/3", "Bb4:3 r:1", "D5:1 D5:2/3 Eb5:1/3 D5:1 Bb4:1", "B4:1 D5:1 F5:1.5 r:0.5",
        "E5:2/3 D5:1/3 C5:1 Bb4:1 G4:1", "A4:1 C5:1 Eb5:1 r:2/3 C5:1/3", "D5:2 Bb4:1 r:1",
        "B4:2/3 D5:1/3 F5:1 D5:1 B4:1", "C5:1 E5:1 Eb5:1 A4:1", "Bb4:2 r:1 F4:2/3 A4:1/3",
    };

    private static readonly string[] ClarinetObbligato =
    {
        "F5:2 D5:2/3 F5:1/3 Bb5:1", "A5:2/3 Bb5:1/3 F5:1 D5:1 Bb4:1", "A4:2/3 C5:1/3 Eb5:2/3 F5:1/3 A5:2",
        "G5:2/3 F5:1/3 Eb5:2/3 C5:1/3 A4:1 C5:1", "D5:2/3 F5:1/3 Bb5:3", "Ab5:2/3 F5:1/3 D5:2/3 F5:1/3 Ab5:2",
        "G5:2 Eb5:2/3 G5:1/3 Bb5:1", "G5:2/3 Eb5:1/3 Bb4:2/3 G4:1/3 Bb4:2", "F5:2/3 D5:1/3 F5:2/3 D5:1/3 Bb5:2",
        "B5:2 G5:2/3 F5:1/3 D5:1", "E5:2/3 G5:1/3 Bb5:2 G5:1", "A5:2/3 F5:1/3 Eb5:2/3 C5:1/3 A4:2",
        "Bb4:2/3 D5:1/3 F5:2/3 Bb5:1/3 D6:2", "B5:2/3 G5:1/3 F5:2/3 D5:1/3 B4:2",
        "Bb4:2/3 C5:1/3 E5:1 Eb5:2/3 F5:1/3 A5:1", "Bb5:3 r:1",
    };

    private static readonly string[] TromboneTailgate =
    {
        "Bb2:2! F2:1 D3:1", "r:1 Bb2:1! D3:2", "A2:2! C3:1 Eb3:1", "F2:3! r:1", "D3:2! F3:1 D3:1", "Ab2:2! F2:2",
        "G2:2! Bb2:2", "Eb3:3! r:1", "F3:2! D3:2", "B2:2! G2:2", "Bb2:2! G2:1 E2:1", "A2:2! Eb3:2", "D3:2! Bb2:2",
        "F3:2! D3:1 B2:1", "E3:2! Eb3:2!", "D3:2! r:2",
    };

    /// <summary>A horn's part: its sixteen bars twice, the second time with <paramref name="stopTime"/> in bars 7-8
    /// (the break), then the third chorus's first four bars and the rest of the loop.</summary>
    private static string HornPart(string[] chorus, string stopTime, string rest) =>
        Bars(string.Join("|", chorus)) + Bars(string.Join("|", chorus.Take(6))) + Bars(stopTime)
        + Bars(string.Join("|", chorus.Skip(8))) + Bars(string.Join("|", chorus.Take(4))) + Bars(rest);

    /// <summary>The rhythm section through <see cref="LanternChart"/>, one bar at a time: <paramref name="play"/>
    /// gives a chord's notes for its beats (4 or 2), or its stop-time hit and rests.</summary>
    private static string Comp(Func<(string Root, string Fifth, string Banjo, string Piano), int, bool, string> play) =>
        Bars(string.Join("|", LanternChart.Select(bar =>
        {
            var chords = bar.Split(' ');
            return string.Concat(chords.Select(c =>
                play(LanternChords[c.TrimEnd('*')], 4 / chords.Length, c.EndsWith('*'))));
        })));

    /// <summary>Checks that every 4/4 bar (separated by <c>|</c>) adds up to four beats, and joins them.</summary>
    private static string Bars(string bars)
    {
        var sb = new StringBuilder();
        foreach (var bar in bars.Split('|'))
        {
            double beats = bar.Split(' ', StringSplitOptions.RemoveEmptyEntries)
                .Sum(token => Beats(token[(token.LastIndexOf(':') + 1)..].TrimEnd('!').Split('>')[0]));
            if (Math.Abs(beats - 4) > 1e-9) throw new FormatException($"Bar \"{bar}\" lasts {beats} beats, not 4");
            sb.Append(bar.Trim()).Append(' ');
        }
        return sb.ToString();
    }

    private static string Rests(int bars) => string.Join("|", Enumerable.Repeat("r:4", bars));

    private static readonly Piece Lantern = new(192, new Hall(1.1, 0.85, 0.45, 0.4), new Part[]
    {
        new(Instrument.Cornet, 0.8, 0,
            HornPart(CornetLead, CornetBreak,
                "r:2/3 F4:1/3 Bb4:1 r:2|" + Rests(2) + "|" + CornetBreak.Split('|')[0] +
                "|r:1 G4:2/3 Bb4:1/3 Eb5:2/3 G5:1/3 F5:1|" + Rests(2) + "|" + CornetBreak)),
        new(Instrument.Clarinet, 0.6, -0.35,
            HornPart(ClarinetObbligato, "Bb5:1 r:3|G5:1 r:3",
                "D5:2/3 F5:1/3 Bb5:1 F5:2/3 D5:1/3 C5:1|D5:2/3 F5:1/3 G5:1 r:2")),
        new(Instrument.Trombone, 0.7, 0.35,
            HornPart(TromboneTailgate, "G2:1 r:3|Eb3:1 r:3", "E3:2! r:2|" + Rests(8) + "|F2:1! Bb2:1! D3:2>4")),
        new(Instrument.Banjo, 0.55, -0.2,
            Comp((c, beats, stop) => stop ? $"{c.Banjo}:1>0.5 r:3 " : Repeat($"{c.Banjo}:1>0.6 ", beats)) +
            Bars("D4+F4+Bb4:1>0.6 D4+F4+Bb4:1>0.4 r:2|" + Rests(5) + "|G3:1 r:1 G3:1 G3:1")),
        new(Instrument.Tuba, 0.8, 0.15,
            Comp((c, beats, stop) => stop ? $"{c.Root}:1 r:3 " : beats == 4 ? $"{c.Root}:2 {c.Fifth}:2 " : $"{c.Root}:2 ") +
            Bars("Bb1:1 r:3|" + Rests(4) + "|Bb1:1 F1:1 Bb1:2")),
        new(Instrument.Piano, 0.45, 0.3,
            Comp((c, beats, stop) => stop ? $"{c.Piano}:1>0.6 r:3 " : Repeat($"r:1 {c.Piano}:1>0.7 ", beats / 2)) +
            Bars("r:1 F3+Bb3+D4:1>0.7 r:2|r:4|Bb3:1/3 C4:1/3 D4:1/3 F4:1/3 G4:1/3 A4:1/3 Bb4:1 D5+F5:1>2|" +
                 Rests(2) + "|F4:2/3 D4:1/3 Bb3:1>2 r:2|r:2 Bb3+D4+F4:2")),
        // kick on one and three; a crash on the stop-time hits
        new(Instrument.Drums, 0.6, 0,
            Comp((_, beats, stop) => stop ? "C2+Eb3:1 r:3 " : Repeat("C2:1 r:1 ", beats / 2)) + Bars("C2:1 r:3")),
        // snare and hi-hat on two and four
        new(Instrument.Drums, 0.5, -0.1,
            Comp((_, beats, stop) => stop ? "r:4 " : Repeat("r:1 D2+F#2:1 ", beats / 2)) + Bars("r:1 D2+F#2:1 r:2")),
        // the count-in
        new(Instrument.Drums, 0.8, 0.05, Bars(Rests(46) + "|C#2:2 C#2:2|C#2:1 C#2:1 C#2:1 C#2:1")),
    }, Distance: new Distance(180, 4200, 0.6, 0.27, 0.3, 0.3));

    /// <summary>The same rehearsal from the alley: through the open back door and down a brick passage, far, dark,
    /// almost mono and full of echoes.</summary>
    private static readonly Piece LanternAlley = Lantern with
    {
        Hall = new Hall(1.5, 0.9, 0.5, 0.7),
        Distance = new Distance(250, 1100, 0.15, 0.39, 0.4, 0.5),
    };
}