---
name: pr-and-ci
description: Finish a Repentance change - commit, push, open the pull request, watch CI and fix failures until the ci-ok check is green. Use at the end of any implementation, or when asked to open a PR or fix CI.
---

# PR and CI

Reference: `docs/ci-and-release.md`.

1. Run matching local suites (`docs/testing.md`, "Quick reference"), not the full clean suite.
2. Commit on the session branch (no new branch) and push: `git push -u origin HEAD`.
3. Open the PR with the app's create-PR tool when available; otherwise `gh pr create`. Description: changes and local suites
   were run.
4. Watch: `gh pr checks --watch`. On failure read the failed log and artifacts (commands in
   `docs/ci-and-release.md`); fix, push, repeat.
5. Done only when every check, including `ci-ok`, is green. Never merge, or report success, while a check is red,
   pending or missing.

A new CI job goes into `ci-ok`'s `needs`, not the branch ruleset.
