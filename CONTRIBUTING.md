# Contributing to Repentance

Repentance is a collaborative, non-profit game. Contributions are welcome: bug fixes, new rooms, dialogue, art,
tests and docs.

## How to contribute

1. Fork the repository on GitHub (or create a branch, if you have write access).
2. Make your change. See `docs/testing.md` for the test launchers (`tools/run/test.ps1` / `test.sh`);
   locally, running the suites that match your change is enough.
3. Open a pull request against this repository describing what you changed and why. CI runs every suite and
   exports the game; the pull request can be merged once its `ci-ok` check is green.

## Licensing of contributions

Repentance is source-available, **non-commercial** and closed to derivatives:

- Code is licensed under [PolyForm Strict 1.0.0](LICENSE).
- Art, audio, story and docs are licensed under [CC BY-NC-ND 4.0](LICENSE-ASSETS.md).

Neither licence allows changing or redistributing the project. As a narrow exception, you may fork, clone and
modify the repository **only to prepare pull requests to this repository**. A fork must not be published,
distributed or used as the basis of another game, and must not be used commercially in any way. GitHub's
Terms of Service let users fork public repositories on GitHub; that does not grant any further rights.

By submitting a contribution, you confirm you have the right to submit it, and you grant Massimiliano D'Acunzo
a perpetual, worldwide, royalty-free, irrevocable licence to use, modify, distribute and sublicense it as part of
Repentance under the project's licences. Do not submit third-party material unless its licence permits
inclusion, and add it to `CREDITS.md`.

Nobody may sell the game, or profit from its code or content, in any form.
