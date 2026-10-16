---
name: story-change
description: Change Repentance's story - dialogue in dialogue/repentance.ink, room puzzles in scripts/Rooms, items, flags, acts or endings - and keep the canonical playthrough, regressions and story-integrity tests green. Use for any story, dialogue, puzzle, item or ending change.
---

# Changing the story

Follow `docs/story-and-dialogue.md`, especially "Ink conventions" and "Checklist for a story change".
Spec: `Walkthrough.md`. Test contracts and allowlists: `docs/testing.md`.

## Steps

1. Update the spec before implementation.
2. Edit Ink and room logic; shared inventory behavior goes in `scripts/Story/`, not `Game`.
   Use the guide's file map for items, notes, kits, puzzle rules and endings.
3. Update `scripts/Debug/Playthrough/Playthrough.ActN.cs`; branch Act 3 on `_route`, with route choices in
   `Playthrough.Endings.cs`. Every route must reach "The End".
4. Add relevant regressions in `scripts/Debug/AutoPlay/`; shared helpers belong in `Harness.cs`.
5. For incompatible saved meaning, follow `docs/saves-and-settings.md`, "Changing the format".
6. Run `dotnet build`, then `tools\run\test.ps1 -Suite unit, playthrough`; add `autoplay` for AutoPlay/Harness
   changes and `walk` for scene changes.

## When story tests fail

Fix content before adding an allowlist entry; every exemption needs a reason.
Repeatable conversations need a sticky exit or fallback, not only exhausted `*` choices.
