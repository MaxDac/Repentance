---
name: story-change
description: Change Repentance's story - dialogue in dialogue/repentance.ink, room puzzles in scripts/Rooms, items, flags, acts or endings - and keep the canonical playthrough, regressions and story-integrity tests green. Use for any story, dialogue, puzzle, item or ending change.
---

# Changing the story

Follow `docs/story-and-dialogue.md`, especially "Ink conventions" and "Checklist for a story change".
Spec: `Walkthrough.md`. Test contracts and allowlists: `docs/testing.md`.

For requested hands-on review use `tools/run/game.sh` / `tools\run\game.ps1`. Watch-only Bash film speed is
optional (default 1x): `tools/run/film.sh --speed 4` or `-s 4`, never positional. Neither replaces story tests.

## Steps

1. Update the spec before implementation.
2. Edit Ink and room logic; shared inventory behavior goes in `scripts/Story/`, not `Game`.
   Use the guide's file map for items, notes, kits, puzzle rules and endings.
3. Update `scripts/Debug/Playthrough/Playthrough.ActN.cs`; branch Act 3 on `_route`, with route choices in
   `Playthrough.Endings.cs`. Every route must reach "The End".
4. Add relevant regressions in `scripts/Debug/AutoPlay/`; shared helpers belong in `Harness.cs`.
5. For incompatible saved meaning, follow `docs/saves-and-settings.md`, "Changing the format".
6. Run `dotnet build -v q -clp:ErrorsOnly`. CI runs `unit` and `playthrough` (`autoplay` for AutoPlay/Harness,
   `walk` for scenes); run them locally only if the user asks (`docs/testing.md`, "Local test policy").

## When story tests fail in CI

Read the failing lines from the CI log (`docs/ci-and-release.md`, "Reading a CI failure"); do not rerun locally.
Fix content before adding an allowlist entry; every exemption needs a reason.
Repeatable conversations need a sticky exit or fallback, not only exhausted `*` choices.
