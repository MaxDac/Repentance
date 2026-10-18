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
        Track.LobbyPiano => Lobby,
        Track.MansionDread => Mansion,
        Track.RoseStreet => Street,
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

    // ------------------------------------------------------------------ the Aurelian lobby

    // The house pianist in the Aurelian's marble lobby, playing for nobody in particular: a slow 1920s ballad in C
    // major, kept low and so soft it is nearly furniture. Sixteen bars, AABA, with no syncopation at all: the left hand
    // lays a low bass on each chord and breaks a hushed sixth or ninth chord upwards over it, a note a beat, as if the
    // sustain pedal never came up; the right hand sings a plain tune in half notes around middle C, never reaching up
    // into the bright treble. The bridge slides from F6 to Fm6 and down through a diminished chord, and the last bar
    // turns round on G9 so the loop falls straight back to C.
    private const string LoungeOpening = "E4:2 G4:2 A4:2 E4:2 F4:2 D4:2 ";

    // declared before Lobby: static fields initialize in order. Each chord: its bass, and the voicing above it
    private static readonly Dictionary<string, (string Root, string Voicing)> LoungeChords = new()
    {
        ["C6"] = ("C2", "E3+G3+A3"), ["A9"] = ("A1", "C#3+G3+B3"), ["Dm7"] = ("D2", "C3+F3+A3"),
        ["G9"] = ("G1", "B2+F3+A3"), ["C7"] = ("C2", "Bb2+E3+G3"), ["F6"] = ("F2", "C3+D3+A3"),
        ["Fm6"] = ("F2", "C3+D3+Ab3"), ["C6/E"] = ("E2", "E3+G3+A3"), ["Ebdim7"] = ("Eb2", "C3+F#3+A3"),
    };

    private const string LoungeForm =
        "C6|A9|Dm7 G9|C6 G9|C6|A9|Dm7 G9|C6 C7|F6|Fm6|C6/E Ebdim7|Dm7 G9|C6|A9|Dm7 G9|C6 G9";

    // a real grand piano, recorded pianissimo, in a well-damped marble room
    private static readonly Piece Lobby = new(64, new Hall(1.3, 0.86, 0.65, 0.25), new Part[]
    {
        new(Instrument.RecordedPiano, 0.32, -0.15, Pedalled(LoungeForm, bass: true)),
        new(Instrument.RecordedPiano, 0.2, -0.05, Pedalled(LoungeForm, bass: false)),
        new(Instrument.RecordedPiano, 0.38, 0.2,
            LoungeOpening + "C4:2 D4:2 " +
            LoungeOpening + "C4:2 Bb3:2 " +
            "A4:2 F4:2 Ab4:2 F4:2 G4:2 F#4:2 F4:2 D4:2 " +
            LoungeOpening + "C4:3 B3:1"),
    });

    /// <summary>
    /// A soft, pedalled left hand, one 4/4 bar per <c>|</c>, each chord lasting the whole bar or, if the bar has two,
    /// half of it: with <paramref name="bass"/> the low note on the chord's first beat, ringing through it; otherwise
    /// the voicing broken upwards, one note a beat, each ringing to the chord's end (a two-beat chord sounds whole on
    /// its second beat), so a new note starts on every beat and the sound never thins out.
    /// </summary>
    private static string Pedalled(string bars, bool bass)
    {
        var sb = new StringBuilder();
        foreach (var bar in bars.Split('|'))
        {
            var chords = bar.Split(' ');
            int beats = 4 / chords.Length;
            foreach (var chord in chords)
            {
                var (root, voicing) = LoungeChords[chord];
                if (bass) sb.Append($"{root}:{beats} ");
                else if (beats == 2) sb.Append($"r:1 {voicing}:1 ");
                else
                {
                    sb.Append("r:1 ");
                    var notes = voicing.Split('+');
                    for (int i = 0; i < notes.Length; i++) sb.Append($"{notes[i]}:1>{notes.Length - i} ");
                }
            }
        }
        return sb.ToString();
    }

    // ------------------------------------------------------------------ the mansion

    // A dark, dissonant thriller loop for the Harrington house at night, fourteen slow bars of 4/4 with no key to stand
    // on, kept low and in the background. The double bass bows a grinding semitone, E against F, with tritone lurches
    // to Bb and B, never letting go, so something sounds on every beat; it quickens in bars 9 and 10 like a pulse.
    // Over it, pizzicato chords made of minor seconds and tritones fall on the beat but at uneven gaps, an irregular
    // heartbeat that stutters into every beat before the hush. The cello bows long low arcs above them, creeping by
    // semitones. Then, once and only once, as the hush begins, an open trumpet stabs a high cluster, F5 B5 C6, gone in
    // a quarter of a beat.
    private const string ToneRow = "E2+Bb2+F3";
    private const string Fist = "F2+B2+E3";
    private const string Claw = "G2+C#3+Ab3";
    private const string Needle = "D#3+E3+A3";

    private static readonly Piece Mansion = new(56, new Hall(1.5, 0.93, 0.5, 0.42), new Part[]
    {
        new(Instrument.DoubleBass, 0.95, 0.1,
            "E1:4 F1:4 E1:4 F1:2 E1:2 Bb1:6 A1:2 E1:4 F1:4 E1:2 F1:2 E1:2 F1:2 Bb1:4 B1:4 E1:4 F1:4"),
        new(Instrument.Pizzicato, 0.7, -0.35,
            $"r:1 {ToneRow}:2 {Fist}:1 r:2 {ToneRow}:2 " +
            $"{ToneRow}:1 {Claw}:3 r:1 {ToneRow}:1 {ToneRow}:2 " +
            $"{Fist}:2 r:1 {ToneRow}:1 {Needle}:3 r:1 " +
            $"r:2 {ToneRow}:1 {Fist}:1 {ToneRow}:3 r:1 " +
            $"{Claw}:2 {ToneRow}:1 {ToneRow}:1 {ToneRow}:2 r:2 " +
            $"{ToneRow}:1 {Fist}:1 {ToneRow}:1 {Fist}:1 {ToneRow}:1 {Fist}:1 r:2 " +
            $"r:3 {Needle}:2 r:3"),
        new(Instrument.Cello, 0.65, 0.3,
            "r:4 Bb2:6 A2:4 r:2 C3:4 B2:4 F3:6 E3:4 r:2 F3:4 Bb3:6 A3:4 r:2 E3:4"),
        new(Instrument.OpenTrumpet, 0.6, -0.1, "r:50 F5+B5+C6:1/4 r:5.75"),
    });

    // ------------------------------------------------------------------ Rose's street

    // Not music: an evening on a quiet terrace street a long way from the Loop, a minute long and silent but for two
    // cars, one coming by from the left and, later, another from the right. No reverb to speak of: it is out in the
    // open.
    private static readonly Piece Street = new(60, new Hall(0.5, 0.5, 0.6, 0.05), new Part[]
    {
        new(Instrument.Car, 1, 1, "r:7 A1:12 r:41"),
        new(Instrument.Car, 0.85, -1, "r:38 G1:11 r:11"),
    });
}