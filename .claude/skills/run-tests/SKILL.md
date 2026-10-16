---
name: run-tests
description: Build, import, run and test Repentance (Godot 4.7 .NET) locally, pick the right test suites for a change, run film mode, or capture what the game draws. Use when asked to run, test, verify, debug a failing suite, or look at the screen.
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

For manual runs use `godot_console.exe`; bound diagnostic runs with `--quit-after N`.
Never use `--headless` for `--autoplay` or `--settings-test`. Commands and options: `docs/getting-started.md`.
