---
name: music-change
description: Add or change Repentance music or sound - a Track, a score, an instrument, a room's music, or the recorded piano, sax or bass notes in assets/audio - render it for the user to hear, and keep the loops seamless and MusicSynthTests green. Use for any change to MusicSynth*, SoundSynth*, Recordings, Music, Sfx or Room.Music, or when asked to compose, regenerate, play or let the user listen to music.
---

# Changing music or sound

Follow `docs/audio.md` ("Music", "Recorded instruments", "Music tool"). Always use the repository's C# music tool,
`tools/music`; do not install Python or ffmpeg, write throwaway renderers, or download samples by hand.

## Instruments

- Piano music uses `Instrument.RecordedPiano`: real pianissimo grand piano notes (University of Iowa Musical
  Instrument Samples, free without restrictions, credited in `CREDITS.md`). Prefer it over the synthesized
  `Instrument.Piano` for any new piano part.
- Sax and bass parts use `Instrument.RecordedSax` (pp alto sax with vibrato) and `Instrument.RecordedBass`
  (double bass pizzicato), recorded the same way.
- Other instruments are synthesized in `MusicSynth.Instruments.cs`. Do not add other audio files without asking;
  any new recording source must be free to use, credited in `CREDITS.md` and excluded in `LICENSE-ASSETS.md`.
- Background music must stay unobtrusive: notes on the beat, something sounding on every beat (soft piano notes
  fade, so long gaps sound like pauses), a low register, no accents.

## Steps

1. Edit the score in `src/Repentance.Audio/MusicSynth.Scores.cs` (tempo, `Hall`, parts) and, for a new track, the `Track`
   enum, `BaseVolumeDb` and the room's `Music` override.
2. If any recorded note or hold changed, regenerate the recordings and commit the changed
   `assets/audio/{piano,sax,bass}/*.pcm` files (never hand-edit them):

   ```sh
   dotnet run --project tools/music -- recordings
   ```

3. Let the user listen: render to the session folder (not the repository) and open the file
   (`Invoke-Item` on Windows):

   ```sh
   dotnet run --project tools/music -- render LobbyPiano <session folder>/lobby_piano.wav
   ```

   Iterate on the score with the user before pushing. For in-game listening, when the user asks, use
   `tools\run\game.ps1`.
4. Update the track's row in `docs/audio.md` and its `MusicSynthTests` fact (range, form, rhythm).
5. Run `dotnet build -v q -clp:ErrorsOnly`. CI runs `MusicSynthTests` (seams, loudness, ranges, recordings) in
   `unit`, plus `playthrough` (every track must play) and `autoplay` (room music); run them locally only if the
   user asks (`docs/testing.md`, "Local test policy").
