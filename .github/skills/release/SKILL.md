---
name: release
description: Launch and monitor the Repentance Release workflow that exports Linux and Windows builds with Godot and publishes a GitHub Release. Use when asked to release, publish, cut a version, or ship a build.
---

# Releasing Repentance

The `Release` workflow (`.github/workflows/release.yml`) is manual-only. It computes the version, runs the unit
tests, exports the `Linux` and `Windows Desktop` presets with Godot 4.7.2 .NET, and creates a GitHub Release tagged
`vX.Y.Z` with `Repentance-vX.Y.Z-linux-x86_64.zip` and `Repentance-vX.Y.Z-windows-x86_64.zip`.

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `version` | blank | `X.Y.Z` without `v`. Blank bumps the patch of the latest `v*` tag; the first release is `0.1.0`. |
| `prerelease` | `true` | Publish as a preview (pre-release). Use `false` only when the user explicitly asks for a full/stable release. |

## Steps

1. Resolve the version. If the user gave none, show what blank will produce:
   ```powershell
   git fetch --tags --quiet; git tag -l 'v*' --sort=-v:refname | Select-Object -First 1
   ```
   Refuse a version whose tag already exists (the workflow fails on it anyway).
2. The workflow releases the **default branch** (`main`) head. Warn the user if the changes they expect are not
   pushed/merged to `main`. Only pass `--ref <branch>` when the user explicitly asks to release another branch.
3. Trigger it (omit `-f version=...` to auto-bump):
   ```powershell
   gh workflow run release.yml -f version=0.1.0 -f prerelease=true
   ```
4. Find the run and watch it until it finishes (exports take several minutes):
   ```powershell
   Start-Sleep -Seconds 5
   $run = gh run list --workflow release.yml --event workflow_dispatch --limit 1 --json databaseId,url | ConvertFrom-Json
   gh run watch $run[0].databaseId --exit-status
   ```
5. On success, report the release URL and assets:
   ```powershell
   gh release view v0.1.0 --json url,isPrerelease,assets --jq '{url, isPrerelease, assets: [.assets[].name]}'
   ```
6. On failure, show the failing step: `gh run view <id> --log-failed`. Common causes: tag already exists, unit test
   failure, or the export check `data_Repentance_*` missing (C# assemblies not exported; `Repentance.sln` must exist).
   Do not delete tags or releases unless the user asks.
