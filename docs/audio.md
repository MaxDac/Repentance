# Audio

No audio files; sounds and music are synthesized at startup.

| Part | Godot-free | Role |
|---|---|---|
| `SoundSynth` (+ `SoundSynth.Effects.cs`) | yes | Renders `Sound` samples (mono, 22050 Hz, deterministic), parses `*cue*` lines |
| `Sfx` | no | Plays sounds on the **Effects** bus: 12 voices round-robin, footsteps, cues, room ambience |
| `MusicSynth` (+ `.Instruments.cs`, `.Scores.cs`) | yes | Renders scored tracks to seamless stereo loops |
| `Music` | no | Plays the room's track on the **Music** bus; keeps playing while paused |

Buses are created at runtime and routed to Master; their volume follows `GameSettings` (0% mutes).

For listening checks, `tools/run/game.sh` / `tools\run\game.ps1` uses real audio and player settings (unlike test
suites' dummy driver). Runtime errors are printed and logged to `logs/game.log` as warnings, so inspect the log
when diagnosing audio; a clean launcher exit alone does not prove sound played.

## Sound effects

`Sound`: `StepWood`, `StepStone`, `StepCarpet`, `Gunshot`, `Knock`, `Clang`, `Crash`, `Thunk`, `Crack`, `Rustle`,
`Click`, `Scrape`, `Whoosh`, `DoorSlam`, `Bell`, `Rain`.

- **Footsteps**: the player and walking actors, by `Room.Floor` (`Wood`, `Stone`, `Carpet`).
- **Ambience**: `Room.Ambience`; by default rain where a `Rain` node exists (see [Rooms](rooms-and-scenes.md)).
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

A room returns its track from `Room.Music`; moving between rooms with the same track does not restart it. Tracks are
about a minute, rendered on worker threads in `Music._Ready`; rendering runs the loop twice and keeps the second
pass so filters and reverb have no seam.

Score syntax (`MusicSynth.Scores.cs`): parts are space-separated tokens `name:beats` (e.g. `D4:1/2`), `r` rest,
`+` chord, `>` separates advance from held duration, `!` accent.

**Add a track**: `Track` -> score in `MusicSynth.Scores.cs` (parts, instruments, tempo, hall) -> `Room.Music` ->
`BaseVolumeDb` if needed. Validate with `MusicSynthTests` and playthrough.
