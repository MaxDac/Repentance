---
name: run-tests
description: Build, import, run and test Repentance (Godot 4.7 .NET) locally, pick the right test suites for a change, run film mode (any speed, ending or start chapter), or capture what the game draws. Use when asked to run, test, verify, debug a failing suite, play/watch the film, or look at the screen.
---

# Running and testing Repentance

Reference: `docs/testing.md` (suite selection, pass rule, harness, film and frame capture).
Pick only matching suites from its "Quick reference" table. Do not run all suites or film unless asked.

```powershell
tools\run\test.ps1 -Suite unit, playthrough     # first run: clean reset, build, import
tools\run\test.ps1 -Suite unit -NoClean         # later runs: skip generated-file deletion
```

Godot suites always build/import, even with `-NoClean`; `unit` runs xunit only.
Logs: `logs/<suite>.log`, `logs/import.log`. Failure = bad exit, missing marker or logged error.

## Read a failure

1. Open `logs/<suite>.log`; search for `FAIL`, `ERROR:`, `SCRIPT ERROR:`, `USER ERROR:`, `Unhandled exception`.
2. Playthrough and AutoPlay name the beat or check that failed; a timeout means a dead end (missing exit, item or
   choice). A run that logged an error fails even if it printed its marker.
3. xunit: rerun one class:
   `dotnet test tests/Repentance.Tests/Repentance.Tests.csproj --filter FullyQualifiedName~StoryIntegrityTests`.
4. Art: `py -3.14 -m unittest discover -s tests\art -v`.

## Delegate launcher runs to a cheap model

Launchers need no reasoning and print 100+ KB. Run each through a subagent on the least powerful model
(`claude-haiku-4.5` or the cheapest available), e.g. `task(agent_type: "task", model: "claude-haiku-4.5", ...)`.
Give it the worktree path, the exact command, a long wait (all suites ~10 min; a 1x film up to an hour, so prefer
`-Speed 16|60|hyper` unless the user wants to watch), and ask it to report only: exit code, the `== Summary` block
or `FILM OK` / `FILM STOPPED` / `FILM FAILED` lines, every `FAIL` / `ERROR:` line with context, and the log path.
It must not edit files, retry with other options or fix failures.

Never run two launchers in the same worktree at once (shared `logs/`, `.godot/`, test user data); run them in
sequence, all but the first with `-NoClean`.

Film: `tools\run\film.ps1 -Speed 1|2|4|8|16|60|hyper -Ending 1-11|1-oldman|1-steps -From act1|interlude1|act2|interlude2|act3|ending`
(bash: `tools/run/film.sh --speed hyper --from ending --ending 8 --no-clean`).
Bash speed is optional (default 1x); use `--speed <s>`, `-s <s>` or `--speed=<s>`, not a positional speed.

Normal interactive play: `tools/run/game.sh` / `tools\run\game.ps1`. These clean generated files (never player
saves/settings), build/import and open the title screen until the player quits. `--no-clean` / `-NoClean` skips
deletion, not build/import; `--godot PATH` / `-Godot PATH` selects the engine. `logs/game.log` needs no marker;
runtime errors are warnings, while nonzero exits and build/import failures fail. Do not use this as a suite pass.

For direct manual runs use `godot_console.exe`; bound diagnostic runs, not interactive play, with `--quit-after N`.
Never use `--headless` for `--autoplay` or `--settings-test`. Commands and options: `docs/getting-started.md`.
