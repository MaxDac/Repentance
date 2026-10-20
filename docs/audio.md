# Audio

Sounds are synthesized at startup and music when a room needs it; the exceptions are a real grand piano, alto sax and double bass, recorded note by note
(see [Recorded instruments](#recorded-instruments)).

| Part | Godot-free | Role |
|---|---|---|
| `SoundSynth` (+ `SoundSynth.Effects.cs`) | yes | Renders `Sound` samples (mono, 22050 Hz, deterministic), parses `*cue*` lines |
| `Sfx` | no | Plays sounds on the **Effects** bus: 12 voices round-robin, footsteps, cues, room ambience |
| `MusicSynth` (+ `.Instruments.cs`, `.Scores.cs`, `.Traffic.cs`, `.Foley.cs`, `.Street.cs`) | yes | Renders scored tracks to seamless stereo loops |
| `Recordings` | yes | Loads the recorded notes for `RecordedPiano`, `RecordedSax` and `RecordedBass` |
| `Music` | no | Plays the room's track on the **Music** bus; keeps playing while paused |

Buses are created at runtime and routed to Master; their volume follows `GameSettings` (0% mutes).

For listening checks, `tools/run/game.sh` / `tools\run\game.ps1` uses real audio and player settings (unlike test
suites' dummy driver). Runtime errors are printed and logged to `logs/game.log` as warnings, so inspect the log
when diagnosing audio; a clean launcher exit alone does not prove sound played.

## Sound effects

`Sound`: `StepWood`, `StepStone`, `StepCarpet`, `Gunshot`, `Knock`, `Clang`, `Crash`, `Thunk`, `Crack`, `Rustle`,
`Click`, `Scrape`, `Whoosh`, `DoorSlam`, `DoorOpen`, `DoorClose`, `Bell`, `Rain`, `Thunder`.

- **Footsteps**: the player and walking actors, by `Room.Floor` (`Wood`, `Stone`, `Carpet`).
- **Doors**: when the player's action on a hotspot marked `Door` changes room (an `ExitTo` exit or the room
  script's `ChangeRoom`), `DoorOpen` plays as the screen fades out and `DoorClose` once the new room has faded in.
  A door that opens on screen first (the office) calls `Game.OpenDoor()` with its animation; it sounds once per action.
  Refused doors, archways, map exits and cutscene room changes stay silent.
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
| `ClubStrings` | Club vestibule, hall, lounge, stage, backstage; Agatha's night visit in the convent cell | Dark string bolero in 3/4, kept soft: no accents, the violins' climax stays at or below C5 |
| `ChurchOrgan` | Church interior | Organist trying the pipes over held pedal notes, then a chorale; a pipe sounds on every beat, nothing above D5 |
| `ConventPiano` | Convent corridor, cell | Hymn-like prelude in E-flat on the recorded piano, pedalled arpeggios under a slow tune |
| `OfficeJazz` | Office; motel fire escape and room while Micah is with Eleanor (not the interludes) | Very slow, very soft D-minor blues (48 bpm): recorded piano, a few alto sax phrases, plucked double bass |
| `BlueLanternJazz` | Blue Lantern speakeasy (every visit, including the interlude) | A Chicago hot band rehearsing in the next room, muffled through the wall: cornet, low clarinet, trombone, banjo, tuba, recorded piano, drums; two choruses and a cornet break, then the clarinet noodles on under the false starts until a stick count-in. No accents, something on every beat |
| `BlueLanternAlley` | Alley behind the Blue Lantern in Act 1 (the back door is propped open) | The same rehearsal, far down the hall: almost muted, a dull mono thud and echo |
| `StreetTraffic` | Hubbard Street, Rizzo's Flowers on State Street, cathedral steps, convent road | Not music: 1920s traffic on a wet road, kept distant |
| `LobbyPiano` | Aurelian Hotel lobby only | House pianist's soft, low 1920s ballad in C on the recorded piano, pedalled broken chords under a plain tune in half notes |
| `PrisonParlour` | Joliet visiting room (prison endings) | Not music, near silence on `Foley`: a faint room hum, a guard's few steps twice, a chair dragged and sat on twice |
| `Investigation` | Hotel linen room, library, Tribune morgue, Harrington's office, the alley in Act 3 | Barely audible, reflective D-minor piece on the recorded piano: pedalled low broken chords, a note a beat, under a few long right-hand notes, with one shadowy turn to E-flat |
| `MansionDread` | Harrington mansion: exterior, kitchen, cellar, study, bedroom (including Eleanor's coda) | Dissonant thriller loop: bowed double bass grinding on E-F, on-beat pizzicato clusters at irregular gaps, low cello arcs, one brief unaccented high open-trumpet stab (the only high note) |
| `RoseStreet` | Rose's house (Act 2 visit, Act 3 coffee) | Not music: a quiet evening street, silent but for two 1920s cars driving past across the stereo field |

`RoseStreet` is scored like the others but played by the `Car` in `MusicSynth.Street.cs`: a note is one whole pass,
its pitch the engine's, and it moves across the stereo field (left to right when its part's pan is positive) with
distance, air absorption and Doppler. Between the cars the track is silent, so `MusicSynthTests` exempts it from the
never-silent check.

`StreetTraffic` is scored like the music, but its instruments (`MusicSynth.Traffic.cs`) are noise and engines: a
`CityHum` bed for the whole loop, `Motorcar` passes (Doppler, distance and stereo travel from the part's pan to the
other side), a `Streetcar` with bell and rail-joint clacks, and a bulb `Horn`. The instruments still support
accents (a car passing close, a klaxon), but like the music the score uses none, so the traffic stays in the
background. It plays on the Music bus, so it follows the music volume; rain ambience still plays on top.

A room returns its track from `Room.Music`; moving between rooms with the same track does not restart it, and
moving between two tracks that share a score (`MusicSynth.SharesScore`, e.g. the speakeasy and the alley) carries
on from the same moment. Tracks are
about a minute, rendered only when needed, one at a time on a single background worker; rendering runs the loop
twice and keeps the second pass so filters and reverb have no seam. `Music` keeps at most `CacheSize` (4) rendered
tracks as 16-bit PCM (about 5 MB each), evicting the least recently used but never the playing one; the policy is
the Godot-free `RenderCache`. A room asks for its track, which jumps ahead of everything else, then
`Game.LoadRoomScene` prefetches the tracks of the rooms its visible exits lead to, so the next room usually starts
with its music ready. A room whose track is not cached yet stays silent until the render finishes (about a second).
After each render the worker runs a compacting GC to hand the float buffers back to the system. `--no-music` skips
rendering and playback.

A piece's optional `Distance` puts the band somewhere else: a band-pass, a narrower stereo image and a darkening
feedback echo, applied after the hall. Instruments: strings, organ stops, piano, muted trumpet, upright bass, drums
(`C2` kick, `C#2` sticks, `D2` snare, `E2` brush sweep, `F#2` hat, others a ride cymbal), cornet, clarinet,
trombone (`!` smears up into the note), banjo and tuba.

Score syntax (`MusicSynth.Scores.cs`): parts are space-separated tokens `name:beats` (e.g. `D4:1/2`), `r` rest,
`+` chord, `>` separates advance from held duration, `!` accent; `Bars` checks each `|`-separated 4/4 bar.

`Instrument.Drums` and `Instrument.Foley` use the pitch to pick a sound rather than a note. `Foley`
(`MusicSynth.Foley.cs`) plays a room's noises: `C2` room tone, `D2` boot, `E2` chair dragged, `F2` chair set
down; room tone and chair drags last as long as their note.

**Add a track**: `Track` -> score in `MusicSynth.Scores.cs` (parts, instruments, tempo, hall) -> `Room.Music` ->
`BaseVolumeDb` if needed. Validate with `MusicSynthTests` and playthrough.

### Recorded instruments

`Instrument.RecordedPiano`, `RecordedSax` and `RecordedBass` play real pianissimo notes (grand piano, alto saxophone
with vibrato, double bass pizzicato) from the University of Iowa Musical Instrument Samples (free to use without
restrictions, see [CREDITS.md](../CREDITS.md)) instead of synthesizing them. Each pitch is a file in the instrument's
folder, `assets/audio/piano/`, `assets/audio/sax/` or `assets/audio/bass/` (`C4.pcm`, `Db4.pcm`...): mono, 22050 Hz,
raw 16-bit little-endian PCM starting at the note's onset. Piano notes come one per file; sax and bass notes are cut
from Iowa's chromatic scales, and the tool checks every cut's pitch. They are not Godot resources, so the export
presets list them in `include_filter`. `Music._Ready` reads them on the main thread before rendering; a missing file
fails the render.

The files hold only the pitches the scores use, each as long as its longest hold plus the release. After changing a
recorded part, regenerate them (downloads are cached in the temp folder; stale files are removed):

```sh
dotnet run --project tools/music -- recordings
```

`MusicSynthTests.EveryRecordedNoteHasARecordingLongEnough` fails until they match the scores.
Prefer the recorded instruments over the synthesized `Piano`, `Trumpet` and `UprightBass` for new parts.
### Music tool

`tools/music` is a small .NET console project (no Godot, Python or ffmpeg needed) that references the Godot-free
`src/Repentance.Audio` library (`SoundSynth*`, `MusicSynth*`, `Recordings`):

| Command | Does |
|---|---|
| `dotnet run --project tools/music -- recordings` | Downloads, cuts, pitch-checks, trims and resamples the recorded notes the scores need; deletes unused ones |
| `dotnet run --project tools/music -- render <Track> [out.wav] [loops]` | Renders a track exactly as the game does to a 16-bit stereo WAV, twice round by default so the seam can be heard |
| `dotnet run --project tools/music -- sound <Sound> [out.wav]` | Renders one sound effect exactly as the game does to a 16-bit mono WAV |

Use `render` to listen to a score change in seconds, without building or importing the game; write the WAV outside
the repository (or delete it) so it is not committed. The folder has a `.gdignore`, and `Repentance.csproj` excludes
`tools/**`.

Agents: `.claude/skills/music-change/SKILL.md`.
