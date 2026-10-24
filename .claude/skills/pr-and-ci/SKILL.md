---
name: pr-and-ci
description: Finish a Repentance change - commit, push, open the pull request, watch CI and fix failures until the ci-ok check is green. Use at the end of any implementation, or when asked to open a PR or fix CI.
---

# PR and CI

Reference: `docs/ci-and-release.md`. CI is the test run (`docs/testing.md`, "Local test policy").

1. Compile: `dotnet build -v q -clp:ErrorsOnly` for C# or Ink changes (nothing for docs/config). Then run only the
   test level or groups the user chose while planning (`docs/testing.md`, "Test levels"; `run-tests` skill), level 0 if none.
   Do not run other suites, `dotnet test`, the harness or film unless the user asked.
2. Commit on the session branch (no new branch).
3. Pick the base (see "Stacked pull requests" in `docs/ci-and-release.md`):
   `gh pr list --state open --json number,title,headRefName,baseRefName,createdAt`. Ignore PRs whose title starts
   with `[NoStack]`. If none remain, the base is `main`. Otherwise the base is the top of the stack: the newest
   remaining PR whose head branch is no other remaining PR's base. Rebase onto it:
   `git fetch origin <base> && git rebase --onto origin/<base> origin/main` (resolve conflicts, rebuild).
4. Push: `git push -u origin HEAD` (`--force-with-lease` after a rebase of pushed commits).
5. Open the PR with the app's create-PR tool when available, passing `base_branch: <base>` when stacked; otherwise
   `gh pr create --base <base>`. Description: changes, the PR it stacks on (`Stacked on #N`), and what ran locally
   (normally "Local: `dotnet build` only; tests run in CI"). If any image changed, add before/after previews to the
   description (see "Pull requests" in
   `docs/ci-and-release.md`).
6. When stacked, register the PR in the native GitHub stack (REST via `gh api`, not the `gh stack` extension):
   `gh api repos/MaxDac/Repentance/stacks?pull_request=<base-pr>`. If the base PR is in a stack, append only the new
   PR: `gh api --method POST repos/MaxDac/Repentance/stacks/<stack>/add -F 'pull_requests[]=<new-pr>'`. Otherwise
   create it bottom to top with every PR of the chain:
   `gh api --method POST repos/MaxDac/Repentance/stacks -F 'pull_requests[]=<bottom-pr>' -F 'pull_requests[]=<new-pr>'`.
   Check that the returned `pull_requests` list the whole chain in order.
7. Watch: `gh pr checks --watch`. On failure read only the failing lines of the failed log and artifacts
   ("Reading a CI failure" in `docs/ci-and-release.md`: filtered `gh run view <id> --log-failed`,
   `gh run download`); hand a long log to a cheapest-model subagent that reports only failures. Never reproduce the
   failure with a local suite unless the user asks; fix, push (the new CI run is the retest), repeat.
8. Done only when every check, including `ci-ok`, is green. Never merge, or report success, while a check is red,
   pending or missing.

A new CI job goes into `ci-ok`'s `needs` and into the ruleset's required checks (`docs/ci-and-release.md`).
