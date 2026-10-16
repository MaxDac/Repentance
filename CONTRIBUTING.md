# Contributing to Repentance

Contributions are welcome: bug fixes, new rooms, dialogue, art, tests and docs.

## How to contribute

1. Fork the repository and create a branch.
2. Make your change. See `docs/testing.md` for the test launchers (`tools/run/test.ps1` / `test.sh`);
   locally, running the suites that match your change is enough.
3. Open a pull request describing what you changed and why. CI runs every suite and exports the game; the pull
   request can be merged once its `ci-ok` check is green.

## Licensing of contributions

Repentance is source-available and **non-commercial**:

- Code is licensed under [PolyForm Noncommercial 1.0.0](LICENSE).
- Art, audio, story and docs are licensed under [CC BY-NC-SA 4.0](LICENSE-ASSETS.md).

By submitting a contribution, you agree that it is licensed under the same terms as the part
of the project it changes (code under PolyForm Noncommercial 1.0.0, creative content under
CC BY-NC-SA 4.0), and you confirm you have the right to submit it. Do not submit third-party
material unless its licence permits inclusion, and add it to `CREDITS.md`.

You may fork, modify and share the project for non-commercial purposes. Selling the game, or a
game built from its code or content, is not permitted.
