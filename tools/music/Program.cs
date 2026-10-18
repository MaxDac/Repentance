// The music tool, for changing Repentance's music outside Godot:
//
//   dotnet run --project tools/music -- piano
//     Downloads the University of Iowa Musical Instrument Samples' pianissimo grand piano notes that the scores play
//     on Instrument.RecordedPiano ("freely available ... and may be downloaded and used for any projects, without
//     restrictions", https://theremin.music.uiowa.edu/MIS.html), and writes each one to assets/audio/piano as
//     PianoRecordings expects: cut to the hammer's strike, mono, MusicSynth.SampleRate, 16-bit, only as long as the
//     longest hold plus the damper's fall. Recordings no score needs any more are deleted. Downloads are cached in
//     %TEMP%/repentance-piano.
//
//   dotnet run --project tools/music -- render <Track> [out.wav] [loops]
//     Renders a track exactly as the game does, repeated `loops` times (default 2, so the seam can be heard), to a
//     16-bit stereo WAV (default <Track>.wav in the current folder), for listening to a change without the game.

using Repentance;

const string Source = "https://theremin.music.uiowa.edu/sound%20files/MIS/Piano_Other/piano/Piano.pp.{0}.aiff";
const string Usage = "usage: dotnet run --project tools/music -- piano | render <Track> [out.wav] [loops]";

string root = AppContext.BaseDirectory;
while (!File.Exists(Path.Combine(root, "project.godot")))
    root = Path.GetDirectoryName(root) ?? throw new InvalidOperationException("project.godot not found");
string outDir = Path.Combine(root, PianoRecordings.Folder.Replace('/', Path.DirectorySeparatorChar));

switch (args.FirstOrDefault())
{
    case "piano":
        await Piano();
        return 0;
    case "render" when args.Length >= 2 && Enum.TryParse<Track>(args[1], out var track):
        Render(track, args.Length >= 3 ? args[2] : $"{track}.wav", args.Length >= 4 ? int.Parse(args[3]) : 2);
        return 0;
    default:
        Console.Error.WriteLine(Usage);
        Console.Error.WriteLine($"tracks: {string.Join(", ", Enum.GetNames<Track>())}");
        return 1;
}

void Render(Track track, string path, int loops)
{
    PianoRecordings.Use(name =>
    {
        var file = Path.Combine(outDir, name);
        return File.Exists(file) ? File.ReadAllBytes(file) : null;
    });
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

async Task Piano()
{
    string cache = Path.Combine(Path.GetTempPath(), "repentance-piano");
    Directory.CreateDirectory(outDir);
    Directory.CreateDirectory(cache);
    using var http = new HttpClient();
    var needed = PianoRecordings.Needed();
    foreach (var (midi, held) in needed.OrderBy(n => n.Key))
    {
        string name = PianoRecordings.Name(midi);
        string aiff = Path.Combine(cache, $"{name}.aiff");
        if (!File.Exists(aiff))
        {
            Console.WriteLine($"downloading {name}");
            File.WriteAllBytes(aiff, await http.GetByteArrayAsync(string.Format(Source, name)));
        }
        var (mono, rate) = ReadAiff(File.ReadAllBytes(aiff));
        var cut = Prepare(mono, rate, held + PianoRecordings.TailSeconds + 0.05);
        File.WriteAllBytes(Path.Combine(outDir, PianoRecordings.FileName(midi)), PianoRecordings.Encode(cut));
        Console.WriteLine($"{name}: {cut.Length / (double)MusicSynth.SampleRate:0.00} s");
    }
    foreach (var stale in Directory.GetFiles(outDir, "*.pcm")
                 .Where(f => !needed.Keys.Any(m => Path.GetFileName(f) == PianoRecordings.FileName(m))))
    {
        Console.WriteLine($"removing {Path.GetFileName(stale)}");
        File.Delete(stale);
    }
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

// cut to the strike (a hair before, faded in), resample with a windowed-sinc low-pass, keep `seconds`, fade the end,
// and bring the peak to a common level so the score's velocities alone set the balance
static float[] Prepare(float[] x, double rate, double seconds)
{
    float peak = x.Max(Math.Abs);
    int onset = Array.FindIndex(x, v => Math.Abs(v) > peak * 0.05);
    onset = Math.Max(0, onset - (int)(0.003 * rate));
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
