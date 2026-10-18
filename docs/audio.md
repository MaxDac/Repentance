# Audio

Sounds and music are synthesized at startup; the one exception is a real grand piano, recorded note by note
(see [Recorded piano](#recorded-piano)).

| Part | Godot-free | Role |
|---|---|---|
| `SoundSynth` (+ `SoundSynth.Effects.cs`) | yes | Renders `Sound` samples (mono, 22050 Hz, deterministic), parses `*cue*` lines |
| `Sfx` | no | Plays sounds on the **Effects** bus: 12 voices round-robin, footsteps, cues, room ambience |
| `MusicSynth` (+ `.Instruments.cs`, `.Scores.cs`) | yes | Renders scored tracks to seamless stereo loops |
| `PianoRecordings` | yes | Loads the recorded piano notes for `Instrument.RecordedPiano` |
| `Music` | no | Plays the room's track on the **Music** bus; keeps playing while paused |

Buses are created at runtime and routed to Master; their volume follows `GameSettings` (0% mutes).

For listening checks, `tools/run/game.sh` / `tools\run\game.ps1` uses real audio and player settings (unlike test
suites' dummy driver). Runtime errors are printed and logged to `logs/game.log` as warnings, so inspect the log
when diagnosing audio; a clean launcher exit alone does not prove sound played.

## Sound effects

`Sound`: `StepWood`, `StepStone`, `StepCarpet`, `Gunshot`, `Knock`, `Clang`, `Crash`, `Thunk`, `Crack`, `Rustle`,
`Click`, `Scrape`, `Whoosh`, `DoorSlam`, `Bell`, `Rain`, `Thunder`.

- **Footsteps**: the player and walking actors, by `Room.Floor` (`Wood`, `Stone`, `Carpet`).
- **Ambience**: `Room.Ambience`; by default rain where a `Rain` node exists, louder each act and silent once `Room.RainStopped` (see [Rooms](rooms-and-scenes.md)).
- **Cues**: only lines whose text starts with `*` (Ink or `Say`). Ordinary speech never plays sounds.

| Word in the `*...*` line | Sound |
|---|---|
| `knock` (each; `...` adds a pause) | `Knock` |
| `footsteps` | five `StepWood` |
| `slam` (`two` = twice) | `DoorSlam` |
| `bang` | `Gunshot` |
| `clang`, `crash`, `thunk`, `crack`, `rustle`, `click` | same name |
| `scrape` / `scraaape` | `Scrape` |
| `whoosh`, `fwoosh` (any length) | `Whoosh` |
| `ring` | `Bell` |
| `thunder` | `Thunder` |

From C#: `Game.Sfx.Play(Sound.X)`. Delayed cues use game-time timers, so they pause with the game.

**Add a sound**: enum -> `SoundSynth.Render` branch -> synthesis in `SoundSynth.Effects.cs` -> `BaseVolumeDb` ->
optional word in `CuesFor`. Validate with `SoundSynthTests` and the
[playthrough coverage gate](testing.md#suites).

## Music

| `Track` | Rooms | Piece |
|---|---|---|
| `ClubStrings` | Club vestibule, hall, lounge, stage, backstage; Agatha's night visit in the convent cell | Dark string bolero in 3/4 |
| `ChurchOrgan` | Church interior | Organist trying the pipes, then a chorale |
| `ConventPiano` | Convent corridor, cell | Hymn-like piano prelude in E-flat |
| `OfficeJazz` | Office; motel fire escape and room while Micah is with Eleanor (not the interludes) | Slow D-minor ballad, muted trumpet, piano, bass |
| `BlueLanternJazz` | Blue Lantern speakeasy (every visit, including the interlude) | A Chicago hot band rehearsing in the next room, muffled through the wall: cornet, low clarinet, trombone, banjo, tuba, recorded piano, drums; two choruses and a cornet break, then the clarinet noodles on under the false starts until a stick count-in. No accents, something on every beat |
| `BlueLanternAlley` | Alley behind the Blue Lantern in Act 1 (the back door is propped open) | The same rehearsal, far down the hall: almost muted, a dull mono thud and echo |
| `LobbyPiano` | Aurelian Hotel lobby only | House pianist's soft, low 1920s ballad in C on the recorded piano, pedalled broken chords under a plain tune in half notes |

A room returns its track from `Room.Music`; moving between rooms with the same track does not restart it, and
moving between two tracks that share a score (`MusicSynth.SharesScore`, e.g. the speakeasy and the alley) carries
on from the same moment. Tracks are
about a minute, rendered on worker threads in `Music._Ready`; rendering runs the loop twice and keeps the second
pass so filters and reverb have no seam.

A piece's optional `Distance` puts the band somewhere else: a band-pass, a narrower stereo image and a darkening
feedback echo, applied after the hall. Instruments: strings, organ stops, piano, muted trumpet, upright bass, drums
(`C2` kick, `C#2` sticks, `D2` snare, `E2` brush sweep, `F#2` hat, others a ride cymbal), cornet, clarinet,
trombone (`!` smears up into the note), banjo and tuba.

Score syntax (`MusicSynth.Scores.cs`): parts are space-separated tokens `name:beats` (e.g. `D4:1/2`), `r` rest,
`+` chord, `>` separates advance from held duration, `!` accent; `Bars` checks each `|`-separated 4/4 bar.

**Add a track**: `Track` -> score in `MusicSynth.Scores.cs` (parts, instruments, tempo, hall) -> `Room.Music` ->
`BaseVolumeDb` if needed. Validate with `MusicSynthTests` and playthrough.

### Recorded piano

`Instrument.RecordedPiano` plays real pianissimo grand piano notes from the University of Iowa Musical Instrument
Samples (free to use without restrictions, see [CREDITS.md](../CREDITS.md)) instead of synthesizing them. Each
pitch is a file in `assets/audio/piano/` (`C4.pcm`, `Db4.pcm`...): mono, 22050 Hz, raw 16-bit little-endian PCM
starting at the hammer's strike. They are not Godot resources, so the export presets list them in `include_filter`.
`Music._Ready` reads them on the main thread before rendering; a missing file fails the render.

The files hold only the pitches the scores use, each as long as its longest hold plus the damper's fall. After
changing a `RecordedPiano` part, regenerate them (downloads are cached in the temp folder; stale files are removed):

```sh
dotnet run --project tools/music -- piano
```

`MusicSynthTests.EveryRecordedPianoNoteHasARecordingLongEnough` fails until they match the scores.
Prefer `RecordedPiano` over the synthesized `Piano` for new piano parts.

### Music tool

`tools/music` is a small .NET console project (no Godot, Python or ffmpeg needed) that links the Godot-free
`SoundSynth*`, `MusicSynth*` and `PianoRecordings` sources:

| Command | Does |
|---|---|
| `dotnet run --project tools/music -- piano` | Downloads, trims and resamples the recorded piano notes the scores need; deletes unused ones |
| `dotnet run --project tools/music -- render <Track> [out.wav] [loops]` | Renders a track exactly as the game does to a 16-bit stereo WAV, twice round by default so the seam can be heard |

Use `render` to listen to a score change in seconds, without building or importing the game; write the WAV outside
the repository (or delete it) so it is not committed. The folder has a `.gdignore`, and `Repentance.csproj` excludes
`tools/**`.

Agents: `.claude/skills/music-change/SKILL.md`.
