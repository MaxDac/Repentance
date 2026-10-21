---
name: add-room
description: Add or change a Repentance room - a new scene, entry marker, exit, hotspot or walk area - keeping the scene graph, walk test and canonical playthrough green. Use for any change to scenes/*.tscn or a new scripts/Rooms class.
---

# Adding or changing a room

Follow `docs/rooms-and-scenes.md`, "Adding a room" and "Invariants (checked by tests)".
Art contracts: `docs/art-pipeline.md`.

For requested interactive review, use `tools/run/game.sh` / `tools\run\game.ps1` (clean, build/import, normal
title screen). Use direct Godot room arguments for bounded diagnostics; normal-play launchers do not forward them.

## Steps

1. Edit the painter, regenerate art, and align overlay crop origins with scene positions; never hand-edit PNGs.
2. Create/change `scenes/rooms/<room>.tscn` and `scripts/Rooms/<Name>.cs : Room`; keep the documented node layout,
   floor polygon, entry facing metadata and exports.
3. Handle specific gated cases before generic ones; return `false` for unhandled actions.
4. Connect exits with `ExitTo`/`ExitEntry` or literal `Game.ChangeRoom("room", "entry")`. Keep every room reachable.
   A cutscene that leaves on its own ends in a method an exit hotspot also calls in that state (a manual failsafe);
   list scripted exit hotspots in `SceneGraphTests.ScriptedExits`.
5. Use `story-change` for dialogue/flags/items and playthrough beats; update debug kits/notes if needed.
6. For incompatible saved room/entry changes follow `docs/saves-and-settings.md`, "Changing the format".
7. Run `dotnet build`, then `tools\run\test.ps1 -Suite unit, walk`; add `playthrough` for story and `art` for art.

## When tests fail

`SceneGraphTests` reports invalid targets, off-floor points, unreachable rooms or rooms with no way out.
`logs/walk.log` names runtime movement failures; fix the polygon, target or marker, not the test.
