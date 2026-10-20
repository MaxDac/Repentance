// The music tool, for changing Repentance's music outside Godot:
//
//   dotnet run --project tools/music -- recordings
//     Downloads the University of Iowa Musical Instrument Samples ("freely available ... and may be downloaded and used
//     for any projects, without restrictions", https://theremin.music.uiowa.edu/MIS.html) that the scores play on the
//     recorded instruments: the pianissimo grand piano (one file a note), the pianissimo alto saxophone with vibrato
//     and the pianissimo double bass pizzicato (chromatic scales, one note after another, which are cut apart and
//     each note's pitch checked). Each note is written to its instrument's folder as Recordings expects: cut to the
//     onset, mono, MusicSynth.SampleRate, 16-bit, only as long as the longest hold plus the release. Recordings no
//     score needs any more are deleted. Downloads are cached in %TEMP%/repentance-recordings.
//
//   dotnet run --project tools/music -- render <Track> [out.wav] [loops]
//     Renders a track exactly as the game does, repeated `loops` times (default 2, so the seam can be heard), to a
//     16-bit stereo WAV (default <Track>.wav in the current folder), for listening to a change without the game.
//
//   dotnet run --project tools/music -- sound <Sound> [out.wav] [count]
//     Renders one sound effect exactly as the game does to a 16-bit mono WAV (default <Sound>.wav). A count above 1
//     plays it that many times in a row, cycling the variants with the game's pitch jitter, like a walk of footsteps.

using Repentance;

const string Mis = "https://theremin.music.uiowa.edu/sound%20files/MIS/";
const string Usage =
    "usage: dotnet run --project tools/music -- recordings | render <Track> [out.wav] [loops] | sound <Sound> [out.wav] [count]";

// the chromatic scales each recorded instrument (other than the piano) is cut from: file, first and last note
var scales = new Dictionary<Instrument, (string Url, string Low, string High)[]>
{
    [Instrument.RecordedSax] = new[]
    {
        (Mis + "Woodwinds/altosaxophone/AltoSax.Vib.pp.Db3B3.aiff", "Db3", "B3"),
        (Mis + "Woodwinds/altosaxophone/AltoSax.Vib.pp.C4B4.aiff", "C4", "B4"),
        (Mis + "Woodwinds/altosaxophone/AltoSax.Vib.pp.C5Ab5.aiff", "C5", "Ab5"),
    },
    [Instrument.RecordedBass] = new[]
    {
        (Mis + "Strings/doublebass/Bass.pizz.pp.sulE.E1B1.aiff", "E1", "B1"),
        (Mis + "Strings/doublebass/Bass.pizz.pp.sulA.C2B2.aiff", "C2", "B2"),
    },
};

string root = AppContext.BaseDirectory;
while (!File.Exists(Path.Combine(root, "project.godot")))
    root = Path.GetDirectoryName(root) ?? throw new InvalidOperationException("project.godot not found");
string Local(string path) => Path.Combine(root, path.Replace('/', Path.DirectorySeparatorChar));
string cache = Path.Combine(Path.GetTempPath(), "repentance-recordings");

switch (args.FirstOrDefault())
{
    case "recordings":
        await Generate();
        return 0;
    case "render" when args.Length >= 2 && Enum.TryParse<Track>(args[1], out var track):
        Render(track, args.Length >= 3 ? args[2] : $"{track}.wav", args.Length >= 4 ? int.Parse(args[3]) : 2);
        return 0;
    case "sound" when args.Length >= 2 && Enum.TryParse<Sound>(args[1], out var sound):
        RenderSound(sound, args.Length >= 3 ? args[2] : $"{sound}.wav", args.Length >= 4 ? int.Parse(args[3]) : 1);
        return 0;
    default:
        Console.Error.WriteLine(Usage);
        Console.Error.WriteLine($"tracks: {string.Join(", ", Enum.GetNames<Track>())}");
        Console.Error.WriteLine($"sounds: {string.Join(", ", Enum.GetNames<Sound>())}");
        return 1;
}

void RenderSound(Sound sound, string path, int count)
{
    int rate = SoundSynth.SampleRate, gap = (int)(0.45 * rate);
    var s = count <= 1 ? SoundSynth.Render(sound) : new float[gap * (count - 1) + rate / 2];
    var jitter = new Random(1);
    for (int n = 0; n < count && count > 1; n++)
    {
        // as Sfx.Step: a random variant at a pitch between 0.94 and 1.06
        var one = SoundSynth.Render(sound, n % SoundSynth.StepVariants);
        double pitch = 0.94 + jitter.NextDouble() * 0.12;
        for (int i = 0; gap * n + i < s.Length && i * pitch < one.Length - 1; i++)
        {
            double x = i * pitch; int k = (int)x;
            s[gap * n + i] += (float)(one[k] + (one[k + 1] - one[k]) * (x - k));
        }
    }
    using (var w = new BinaryWriter(File.Create(path)))
    {
        w.Write("RIFF"u8); w.Write(36 + s.Length * 2); w.Write("WAVEfmt "u8); w.Write(16); w.Write((short)1);
        w.Write((short)1); w.Write(rate); w.Write(rate * 2); w.Write((short)2); w.Write((short)16);
        w.Write("data"u8); w.Write(s.Length * 2);
        foreach (var v in s) w.Write((short)Math.Clamp(Math.Round(v * short.MaxValue), short.MinValue, short.MaxValue));
    }
    Console.WriteLine($"{Path.GetFullPath(path)}: {sound}, {s.Length / (double)rate:0.00} s");
}

void Render(Track track, string path, int loops)
{
    Recordings.Use(name => File.Exists(Local(name)) ? File.ReadAllBytes(Local(name)) : null);
    var s = MusicSynth.Render(track);
    int rate = MusicSynth.SampleRate, frames = s.Length / 2 * loops;
    using (var w = new BinaryWriter(File.Create(path)))
    {
        w.Write("RIFF"u8); w.Write(36 + frames * 4); w.Write("WAVEfmt "u8); w.Write(16); w.Write((short)1);
        w.Write((short)2); w.Write(rate); w.Write(rate * 4); w.Write((short)4); w.Write((short)16);
        w.Write("data"u8); w.Write(frames * 4);
        for (int l = 0; l < loops; l++)
            foreach (var v in s) w.Write((short)Math.Clamp(Math.Round(v * short.MaxValue), short.MinValue, short.MaxValue));
    }
    Console.WriteLine($"{Path.GetFullPath(path)}: {track}, {loops} x {s.Length / 2.0 / rate:0.0} s");
}

async Task<byte[]> Download(HttpClient http, string url)
{
    string file = Path.Combine(cache, Uri.UnescapeDataString(url[Mis.Length..]).Replace('/', '_'));
    if (!File.Exists(file))
    {
        Console.WriteLine($"downloading {url}");
        File.WriteAllBytes(file, await http.GetByteArrayAsync(url));
    }
    return File.ReadAllBytes(file);
}

async Task Generate()
{
    Directory.CreateDirectory(cache);
    using var http = new HttpClient();
    foreach (var instrument in Recordings.Instruments)
    {
        string outDir = Local(Recordings.Folder(instrument));
        Directory.CreateDirectory(outDir);
        var needed = Recordings.Needed(instrument);
        double tail = Recordings.TailSeconds(instrument) + 0.05;
        if (instrument == Instrument.RecordedPiano)
        {
            foreach (var (midi, held) in needed.OrderBy(n => n.Key))
            {
                var aiff = await Download(http, $"{Mis}Piano_Other/piano/Piano.pp.{Recordings.Name(midi)}.aiff");
                var (mono, rate) = ReadAiff(aiff);
                Write(instrument, midi, Prepare(mono, rate, held + tail));
            }
        }
        else
        {
            foreach (var (url, low, high) in scales[instrument])
            {
                int first = MusicSynth.Midi(low), last = MusicSynth.Midi(high);
                if (!needed.Keys.Any(m => m >= first && m <= last)) continue;
                var (mono, rate) = ReadAiff(await Download(http, url));
                // a plucked string is cut at the pluck itself, past the hiss the recording opens with; a breath swells in slowly
                double attack = instrument == Instrument.RecordedBass ? 0.3 : 0.05;
                var notes = Split(mono, rate, last - first + 1, instrument == Instrument.RecordedBass ? 0.15 : 0.3, url);
                foreach (var (midi, held) in needed.Where(n => n.Key >= first && n.Key <= last).OrderBy(n => n.Key))
                {
                    var (from, to) = notes[midi - first];
                    string name = $"{instrument} {Recordings.Name(midi)}";
                    var note = mono[from..to];
                    CheckPitch(note, rate, Onset(note, rate, attack) + (int)(0.1 * rate), midi, name);
                    if ((to - from) / rate < held + tail - 0.05)
                        throw new InvalidOperationException($"{name} is held {held:0.00} s but the recording lasts {(to - from) / rate:0.00} s");
                    Write(instrument, midi, Prepare(note, rate, held + tail, attack));
                }
            }
        }
        foreach (var stale in Directory.GetFiles(outDir, "*.pcm")
                     .Where(f => !needed.Keys.Any(m => Path.GetFileName(f) == Recordings.FileName(m))))
        {
            Console.WriteLine($"removing {Path.GetFileName(stale)}");
            File.Delete(stale);
        }
    }
}

void Write(Instrument instrument, int midi, float[] samples)
{
    File.WriteAllBytes(Local(Recordings.PathOf(instrument, midi)), Recordings.Encode(samples));
    Console.WriteLine($"{Recordings.PathOf(instrument, midi)}: {samples.Length / (double)MusicSynth.SampleRate:0.00} s");
}

// A chromatic scale cut into its notes by a 10 ms loudness envelope: a note starts when it rises over 3% of the loudest
// (and well over the noise floor) and ends when it falls under half that. Key clicks and breaths shorter than `shortest` seconds are dropped, and a
// note that dips and swells again straight away is one note. Each note runs from its start to the next one's.
static (int From, int To)[] Split(float[] x, double rate, int count, double shortest, string what)
{
    int hop = (int)(rate / 100);
    var env = new double[x.Length / hop];
    for (int w = 0; w < env.Length; w++)
    {
        double s = 0;
        for (int k = 0; k < hop; k++) s += x[w * hop + k] * x[w * hop + k];
        env[w] = Math.Sqrt(s / hop);
    }
    // over the room's hiss: the quietest fifth of the file is the noise floor
    double floor = env.Order().ElementAt(env.Length / 5);
    double on = Math.Max(env.Max() * 0.03, floor * 4);
    var found = new List<(int Start, int End)>();
    for (int w = 0, start = -1; w < env.Length; w++)
    {
        if (start < 0 && env[w] > on) start = w;
        else if (start >= 0 && (env[w] < on / 2 || w == env.Length - 1))
        {
            if (found.Count > 0 && start - found[^1].End < 50) found[^1] = (found[^1].Start, w);
            else if (w - start >= shortest * 100) found.Add((start, w));
            start = -1;
        }
    }
    if (found.Count != count)
        throw new InvalidDataException($"{what}: found {found.Count} notes, expected {count}: " +
            string.Join(" ", found.Select(f => $"{f.Start / 100.0:0.0}s+{(f.End - f.Start) / 100.0:0.00}")));
    return found.Select((f, i) => (Math.Max(0, f.Start * hop - (int)(0.05 * rate)),
        i + 1 < found.Count ? found[i + 1].Start * hop - (int)(0.05 * rate) : x.Length)).ToArray();
}

// the strongest period within three semitones of the expected pitch, by autocorrelation, must be the expected note
static void CheckPitch(float[] x, double rate, int at, int midi, string name)
{
    double hz = MusicSynth.Hz(midi);
    int window = (int)(0.25 * rate);
    int minLag = (int)(rate / (hz * Math.Pow(2, 3 / 12.0))), maxLag = (int)Math.Ceiling(rate / (hz * Math.Pow(2, -3 / 12.0)));
    double best = double.MinValue;
    int bestLag = 0;
    for (int lag = minLag; lag <= maxLag; lag++)
    {
        double sum = 0, energy = 0;
        for (int i = at; i < at + window && i + lag < x.Length; i++)
        {
            sum += x[i] * x[i + lag];
            energy += x[i + lag] * x[i + lag];
        }
        double r = sum / Math.Sqrt(energy + 1e-12);
        if (r > best) (best, bestLag) = (r, lag);
    }
    double cents = 1200 * Math.Log2(rate / bestLag / hz);
    if (Math.Abs(cents) > 70) throw new InvalidDataException($"{name} sounds {cents:+0;-0} cents off: the scale was cut wrong");
}
// AIFF: big-endian chunks; COMM gives channels, bits and an 80-bit float sample rate; SSND holds the frames
static (float[] Mono, double Rate) ReadAiff(byte[] b)
{
    int Int(int at) => b[at] << 24 | b[at + 1] << 16 | b[at + 2] << 8 | b[at + 3];
    int channels = 0, bits = 0;
    double rate = 0;
    for (int at = 12; at + 8 <= b.Length;)
    {
        string id = System.Text.Encoding.ASCII.GetString(b, at, 4);
        int len = Int(at + 4), body = at + 8;
        if (id == "COMM")
        {
            channels = b[body] << 8 | b[body + 1];
            bits = b[body + 6] << 8 | b[body + 7];
            int exp = ((b[body + 8] & 0x7f) << 8 | b[body + 9]) - 16383;
            ulong mantissa = 0;
            for (int k = 0; k < 8; k++) mantissa = mantissa << 8 | b[body + 10 + k];
            rate = mantissa * Math.Pow(2, exp - 63);
        }
        else if (id == "SSND")
        {
            if (bits != 16) throw new InvalidDataException($"{bits}-bit AIFF");
            int data = body + 8 + Int(body), frames = (len - 8 - Int(body)) / (2 * channels);
            var mono = new float[frames];
            for (int i = 0; i < frames; i++)
            {
                double sum = 0;
                for (int c = 0; c < channels; c++)
                {
                    int p = data + 2 * (i * channels + c);
                    sum += (short)(b[p] << 8 | b[p + 1]) / 32768.0;
                }
                mono[i] = (float)(sum / channels);
            }
            return (mono, rate);
        }
        at = body + len + (len & 1);
    }
    throw new InvalidDataException("no sound data in AIFF");
}

// where the note starts: a hair before it first reaches `attack` of its peak
static int Onset(float[] x, double rate, double attack)
{
    float peak = x.Max(Math.Abs);
    return Math.Max(0, Array.FindIndex(x, v => Math.Abs(v) > peak * attack) - (int)(0.003 * rate));
}

// cut to the onset (a hair before, faded in), resample with a windowed-sinc low-pass, keep `seconds`, fade the end,
// and bring the peak to a common level so the score's velocities alone set the balance
static float[] Prepare(float[] x, double rate, double seconds, double attack = 0.05)
{
    int onset = Onset(x, rate, attack);
    double ratio = rate / MusicSynth.SampleRate, cutoff = 0.45 / ratio, width = 32 * ratio;
    int length = (int)Math.Round(seconds * MusicSynth.SampleRate);
    var y = new float[length];
    for (int i = 0; i < length; i++)
    {
        double centre = onset + i * ratio, sum = 0;
        for (int k = (int)Math.Ceiling(centre - width); k <= (int)Math.Floor(centre + width); k++)
        {
            if (k < 0 || k >= x.Length) continue;
            double t = k - centre;
            double sinc = t == 0 ? 2 * cutoff : Math.Sin(2 * Math.PI * cutoff * t) / (Math.PI * t);
            sum += x[k] * sinc * (0.5 + 0.5 * Math.Cos(Math.PI * t / width));
        }
        y[i] = (float)sum;
    }
    int fadeIn = (int)(0.002 * MusicSynth.SampleRate), fadeOut = (int)(0.05 * MusicSynth.SampleRate);
    for (int i = 0; i < fadeIn; i++) y[i] *= i / (float)fadeIn;
    for (int i = 0; i < fadeOut; i++) y[length - 1 - i] *= i / (float)fadeOut;
    float top = y.Max(Math.Abs);
    for (int i = 0; i < length; i++) y[i] *= 0.9f / top;
    return y;
}
