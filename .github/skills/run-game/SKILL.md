---
name: run-game
description: Run Repentance's test suites or film mode through the tools/run launchers (test.ps1/test.sh, film.ps1/film.sh), delegated to a cheap, fast model. Use when asked to run tests, a suite, the playthrough, or to play/watch the film (any speed, ending or start chapter).
---

# Running the launchers on a lightweight model

The launchers only build, run Godot and grep for a pass marker; no reasoning is needed while they run, and their
output is long (100+ KB). Don't run them in the main conversation. Delegate each run to a `task` subagent on the
least powerful model available (`claude-haiku-4.5`, or the cheapest listed one), and keep only its short report.

```text
task(agent_type: "task", model: "claude-haiku-4.5", description: "Run playthrough suite", prompt: <below>)
```

Give the subagent a complete prompt:

- the working directory (the session's worktree path) and the exact command, e.g.
  `tools\run\test.ps1 -Suite unit, playthrough -NoClean` or
  `tools\run\film.ps1 -Speed hyper -From ending -Ending 8 -NoClean` (bash: `tools/run/film.sh hyper --from ending --ending 8 --no-clean`);
- a long wait: every suite together takes about 10 minutes, and a film from the title at 1x can take up to an
  hour (prefer `-Speed 16|60|hyper` unless the user wants to watch);
- what to report back, and nothing else: the exit code, the `== Summary` block (tests) or the `FILM OK` /
  `FILM STOPPED` / `FILM FAILED` lines (film), every `FAIL` / `ERROR:` line with a few lines of context, and the
  `logs\<name>.log` path;
- that it must not edit files, retry with different options, or try to fix failures.

Then read the report yourself and decide what to fix. A suite passes only with exit code 0 and no logged `ERROR:`
lines (see the pass rules in `AGENTS.md`). Don't run two launchers in the same worktree at once: they share `logs/`,
`.godot/` and the test user data, and a clean run deletes what the other is using. Run them one after another, all
but the first with `-NoClean` / `--no-clean`.

Film mode options (see `docs/testing-and-film-mode.md`): `-Speed 1|2|4|8|16|60|hyper`,
`-Ending 1-10|1-oldman|1-steps`, `-From act1|interlude1|act2|interlude2|act3|ending`.
