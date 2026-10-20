---
name: pr-and-ci
description: Finish a Repentance change - commit, push, open the pull request, watch CI and fix failures until the ci-ok check is green. Use at the end of any implementation, or when asked to open a PR or fix CI.
---

# PR and CI

Reference: `docs/ci-and-release.md`.

1. Run matching local suites (`docs/testing.md`, "Quick reference"), not the full clean suite.
2. Commit on the session branch (no new branch).
3. Pick the base (see "Stacked pull requests" in `docs/ci-and-release.md`):
   `gh pr list --state open --json number,title,headRefName,baseRefName,createdAt`. Ignore PRs whose title starts
   with `[NoStack]`. If none remain, the base is `main`. Otherwise the base is the top of the stack: the newest
   remaining PR whose head branch is no other remaining PR's base. Rebase onto it:
   `git fetch origin <base> && git rebase --onto origin/<base> origin/main` (resolve conflicts, rebuild, rerun suites).
4. Push: `git push -u origin HEAD` (`--force-with-lease` after a rebase of pushed commits).
5. Open the PR with the app's create-PR tool when available, passing `base_branch: <base>` when stacked; otherwise
   `gh pr create --base <base>`. Description: changes, the PR it stacks on (`Stacked on #N`), and local suites
   were run. If any image changed, add before/after previews to the description (see "Pull requests" in
   `docs/ci-and-release.md`).
6. Watch: `gh pr checks --watch`. On failure read the failed log and artifacts (commands in
   `docs/ci-and-release.md`); fix, push, repeat.
7. Done only when every check, including `ci-ok`, is green. Never merge, or report success, while a check is red,
   pending or missing.

A new CI job goes into `ci-ok`'s `needs`, not the branch ruleset.
