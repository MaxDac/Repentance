# CI and release

## Pull requests

The description lists the changes and the local suites run. Every PR that adds or changes an image (generated art,
sprites, UI, icons) also shows it:

- Before and after: the image from `main` (`git show main:<path>`) and from the branch; new images need only after.
- Scale small pixel art up 3-4x with nearest-neighbour so it stays crisp. For overlays and sprites, preview them as
  they appear in game: composited onto their room, or a recorded frame
  ([Testing](testing.md#seeing-what-the-game-draws)).
- Attach them with GitHub CLI 2.99 or later. Reference the local files in the body and pass the same paths, and `gh`
  uploads them and rewrites the references:
  `gh pr edit <pr> --body-file body.md --attach ./before.png --attach ./after.png`.
- Keep preview files out of the repository.

### Stacked pull requests

Before opening a PR, check the open ones (`gh pr list --state open`). A PR whose title starts with `[NoStack]` is
independent and ignored. If any other PR is open, the new one stacks on top of them: rebase the branch onto the top
of the stack (the newest open PR whose branch no other open PR targets), open the PR against that branch instead of
`main`, and say `Stacked on #N` in the description. With no such PR, target `main`. Prefix a PR's title with
`[NoStack]` to keep later work from stacking on it.

Register the chain as a native GitHub stack too, so it can be reviewed and squash-merged as one. Find the
stack of the PR below (`gh api repos/MaxDac/Repentance/stacks?pull_request=<below>`); if it has one, append the new
PR (`gh api --method POST repos/MaxDac/Repentance/stacks/<stack>/add -F 'pull_requests[]=<new>'`), otherwise
create one listing every PR of the chain, bottom first (`gh api --method POST repos/MaxDac/Repentance/stacks
-F 'pull_requests[]=<bottom>' -F 'pull_requests[]=<new>'`). Check the result lists every PR bottom to top
([Stacks REST API](https://github.github.com/gh-stack/reference/rest-api/)).

## CI (`.github/workflows/ci.yml`)

Runs on every pull request (a newer push cancels the older run) and every push to `main`. Godot 4.7.2 .NET and .NET
10 are installed by the shared `.github/actions/setup-godot` action (inputs: version, export templates; cached).

| Job | What it does |
|---|---|
| `unit-tests` | `tools/run/test.sh unit --no-clean` and the launcher tests (`tests/test_run_scripts.py`) |
| `art-tests` | `tools/run/test.sh art --no-clean` (Python 3.14, Pillow, NumPy) |
| `godot-tests (<suite>)` | `autoplay`, `settings`, `pause`, `walk`, `playthrough` under xvfb; uploads logs/screenshots on failure |
| `export (linux / windows)` | Exports both presets as the release does; checks the .NET data folder; builds the AppImage and the Windows installer (`tools/package/`); the Linux build runs `--walk-test` from the AppImage; checks the icon frames in the `.exe`; validates, installs and uninstalls the desktop entry |
| `windows-installer` | On Windows: silently installs the installer, checks files, Start Menu shortcut and uninstall entry, then uninstalls and checks nothing is left |
| `ci-ok` | Green only if every job above succeeded |

`ci-ok` is the only required check on `main` (ruleset "main protection"). New jobs go in `ci-ok`'s `needs`, not the
ruleset.

```powershell
gh pr checks --watch
gh run view <run-id> --log-failed
gh run download <run-id> -n godot-tests-<suite> -D ci-logs   # export jobs: export-<platform>
```

Artifacts are uploaded on failure. Fix, push and watch again until `ci-ok` succeeds.

Launcher changes are covered by the isolated Python regressions (Bash and PowerShell), including normal play's
cleanup and marker-free exit handling. `game.sh` / `game.ps1` runs interactive source-project builds, not a CI
suite or an exported release; normal runtime errors are warnings, not the stricter automated-suite pass rule.

## Release (`.github/workflows/release.yml`)

Manual. Inputs: `version` (blank = bump the patch of the latest `v*` tag; first is `0.1.0`; must be `X.Y.Z` and a
new tag) and `prerelease` (default `true`). It runs the unit tests as CI does (`tools/run/test.sh unit --no-clean`),
exports both presets, and publishes a GitHub Release with:

| Asset | Contents |
|---|---|
| `Repentance-vX.Y.Z-windows-x86_64-setup.exe` | Per-user installer (no admin): `%LOCALAPPDATA%\Programs\Repentance`, Start Menu and desktop shortcuts, uninstaller in Apps & features. Unsigned, so SmartScreen warns. |
| `Repentance-vX.Y.Z-linux-x86_64.AppImage` | Single-file Linux build with the desktop entry and icons inside |
| `Repentance-vX.Y.Z-windows-x86_64.zip`, `Repentance-vX.Y.Z-linux-x86_64.zip` | Portable builds |

Packaging scripts (also run by CI's `export` job): `tools/package/windows-installer.sh <export dir> <X.Y.Z> <out>`
(NSIS script `dist/windows/Repentance.nsi`; needs `makensis`) and `tools/package/appimage.sh <export dir> <out>`
(downloads a pinned `appimagetool`). The uninstaller deletes only the files it installed.

The release also attaches `SHA256SUMS` and creates a build-provenance attestation for every asset
(`actions/attest-build-provenance`); the release notes tell players how to verify:
`sha256sum -c SHA256SUMS --ignore-missing` or `gh attestation verify <file> --repo MaxDac/Repentance`.

```powershell
gh workflow run release.yml -f version=0.2.0 -f prerelease=false
```

Agents: skill `.claude/skills/release/SKILL.md`.

### Export

`export_presets.cfg`: `Linux` -> `build/linux/Repentance.x86_64`, `Windows Desktop` -> `build/windows/Repentance.exe`.
Exporting needs `Repentance.sln`: without it Godot exits 0 but leaves out the C# assemblies. Local export:

```powershell
New-Item -ItemType Directory -Force build\windows | Out-Null
godot_console --path . --headless --export-release "Windows Desktop" build\windows\Repentance.exe
```

### The game icon

A white pixel cross on black, generated by `tools/art/icon.py` (`gen_art.py icon`).

- **Window, taskbar, Alt-Tab**: `config/icon` (and `config/windows_native_icon`) in `project.godot`.
- **`Repentance.exe`**: the Windows preset embeds `assets/art/ui/icon.ico` (`application/modify_resources=true`).
- **Linux desktops**: the Linux zip ships `dist/linux/` (`Repentance.desktop` with `StartupWMClass=Repentance`,
  `icons/hicolor`, `install-desktop.sh`). Godot's app_id / `WM_CLASS` is `config/name` ("Repentance"). Players run
  `./install-desktop.sh` (or `--uninstall`); rerun after moving the folder. The AppImage carries the same entry and
  icons for AppImage integration tools.
- **Windows installer**: `assets/art/ui/icon.ico` is the installer and uninstaller icon.
