---
name: release
description: Launch and monitor the Repentance Release workflow that exports Linux, Windows and Android builds with Godot and publishes a GitHub Release. Use when asked to release, publish, cut a version, or ship a build.
---

# Releasing Repentance

Workflow, exports and asset names: `docs/ci-and-release.md`. Dispatch `.github/workflows/release.yml`; do not
build or publish releases by hand.

## Inputs

| Input | Default | Meaning |
|---|---|---|
| `version` | blank | `X.Y.Z` without `v`. Blank bumps the patch of the latest `v*` tag; the first release is `0.1.0`. |
| `prerelease` | `true` | Publish as a preview (pre-release). Use `false` only when the user explicitly asks for a full/stable release. |

## Steps

1. Resolve the version. If the user gave none, show what blank will produce:
   ```powershell
   git fetch --tags --quiet
   git tag -l 'v*' --sort=-v:refname | Where-Object { $_ -match '^v\d+\.\d+\.\d+$' } | Select-Object -First 1
   ```
   Refuse a version whose tag already exists (the workflow fails on it anyway).
2. Without `--ref`, dispatch uses the **default branch** (`main`). Warn if expected changes are not
   pushed/merged to `main`. Only pass `--ref <branch>` when the user explicitly asks to release another branch.
3. Trigger it (omit `-f version=...` to auto-bump):
   ```powershell
   gh workflow run release.yml -f version=0.1.0 -f prerelease=true
   ```
4. Find the dispatch matching the chosen ref/time and watch it. Do not assume the newest run is yours if another
   release was dispatched:
   ```powershell
   Start-Sleep -Seconds 5
   gh run list --workflow release.yml --event workflow_dispatch --limit 5 --json databaseId,headBranch,createdAt,url
   gh run watch <run-id> --exit-status
   ```
5. On success, report the release URL and assets:
   ```powershell
   gh release view v0.1.0 --json url,isPrerelease,assets --jq '{url, isPrerelease, assets: [.assets[].name]}'
   ```
6. On failure, show the failing step: `gh run view <id> --log-failed`. Common causes: tag already exists, unit test
   failure, or the export check `data_Repentance_*` missing (C# assemblies not exported; `Repentance.sln` must exist). Android job: `RELEASE_KEYSTORE_*` / `RELEASE_KEY_ALIAS` secrets missing, or no `Repentance.dll` in the APK.
   Do not delete tags or releases unless the user asks.
