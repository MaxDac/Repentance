---
name: run-tests
description: Build, import, run and test Repentance (Godot 4.7 .NET) locally ONLY when the user explicitly asks - run a suite, film mode (any speed, ending or start chapter), or capture what the game draws - and pick which suites cover a change. Never run tests on your own before a PR; CI runs them all (see pr-and-ci). Use when the user asks to run, test, play/watch the film, or look at the screen.
---

# Running and testing Repentance

**Policy (`docs/testing.md`, "Local test policy"):** CI runs every suite on every PR. Run a suite, `dotnet test`,
the harness, film or frame capture only when the user explicitly asks for it. Before a PR the only local check is
`dotnet build -v q -clp:ErrorsOnly`. A failing CI check is read from its log (`pr-and-ci`), not rerun here.
A test level the user picked while planning ("Test levels" in `docs/testing.md`, levels 0 to 5), or a list of
groups or suites they typed instead (e.g. `Basic, Story`), counts as that request: after implementation, run
exactly that selection, once, as a single `test.ps1 -Suite ...` command.

Reference: `docs/testing.md` (test levels, suite selection, pass rule, harness, film and frame capture).
When asked for specific suites rather than a level, pick only the matching ones from its "Quick reference" table.
Do not run all suites or film unless asked.

```powershell
tools\run\test.ps1 -Suite unit, playthrough     # first run: clean reset, build, import
tools\run\test.ps1 -Suite unit -NoClean         # later runs: skip generated-file deletion
```

`test.ps1` / `test.sh` is the single entry point; no suite means `all` (unit, art, launcher and every Godot suite).
Launcher changes: `-Suite launcher` or `tools\run\harness.ps1` / `tools/run/harness.sh` (extra args go to unittest,
e.g. `-k film`); they test Bash (Git Bash on Windows) and pwsh, no Godot needed.
Godot suites always build/import, even with `-NoClean`; `unit` runs xunit only. Exports, packaging and Android run
only in CI (`docs/testing.md`, "What only CI runs").
Logs: `logs/<suite>.log`, `logs/import.log`. Failure = bad exit, missing marker or logged error.

## Read a failure

CI failures: `docs/ci-and-release.md`, "Reading a CI failure" (filtered `gh run view --log-failed`, artifacts).
For a run the user asked for:

1. Open `logs/<suite>.log`; search for `FAIL`, `ERROR:`, `SCRIPT ERROR:`, `USER ERROR:`, `Unhandled exception`.
2. Playthrough and AutoPlay name the beat or check that failed; a timeout means a dead end (missing exit, item or
   choice). A run that logged an error fails even if it printed its marker.
3. xunit, if the user wants a rerun: one class,
   `dotnet test tests/Repentance.Content.Tests --filter FullyQualifiedName~StoryIntegrityTests`.
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

Film: `tools\run\film.ps1 -Speed 1|2|4|8|16|60|hyper -Ending 1-15|1-oldman|1-steps|1-caleb|12-oldman|15-caleb|<title> -From act1|interlude1|act2|interlude2|act3|ending`
(bash: `tools/run/film.sh --speed hyper --from ending --ending 8 --no-clean`). Ending titles (e.g. `give-up`,
`she-visits-once`) are listed by `film.sh --help` / `Get-Help tools\run\film.ps1 -Parameter Ending`.
Bash speed is optional (default 1x); use `--speed <s>`, `-s <s>` or `--speed=<s>`, not a positional speed.

Normal interactive play: `tools/run/game.sh` / `tools\run\game.ps1`. These clean generated files (never player
saves/settings), build/import and open the title screen until the player quits. `--no-clean` / `-NoClean` skips
deletion, not build/import; `--godot PATH` / `-Godot PATH` selects the engine. `logs/game.log` needs no marker;
runtime errors are warnings, while nonzero exits and build/import failures fail. Do not use this as a suite pass.

For direct manual runs use `godot_console.exe`; bound diagnostic runs, not interactive play, with `--quit-after N`.
Never use `--headless` for `--autoplay` or `--settings-test`. Commands and options: `docs/getting-started.md`.
