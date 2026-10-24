#!/usr/bin/env bash
# Shared helpers for game.sh, film.sh and test.sh. Source it; don't run it directly.

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="$ROOT/logs"
# Extra engine flags for every Godot run, e.g. GODOT_FLAGS="--rendering-driver opengl3" under xvfb in CI.
GODOT_FLAGS="${GODOT_FLAGS:-}"

# The same rule as CI: Game.Run catches script exceptions with GD.PushError, so a run can print its marker after one.
ERROR_PATTERN='^(ERROR|SCRIPT ERROR|USER ERROR):|Unhandled exception'
# Godot 4.7 bug, not ours: on Linux the Android export plugin reads an editor setting after a headless --import has
# freed EditorSettings. Ignored in the import log only (docs/ci-and-release.md#android).
IMPORT_NOISE='EditorSettings not instantiated yet when getting setting "export/android/'

check_godot() {
  local godot="$1" probe output status=0
  probe="$(mktemp -d)" || return 1
  # An empty project directory keeps the probe independent of this project's C# autoloads and import cache.
  output="$("$godot" --headless --path "$probe" --script "$ROOT/tools/run/check-godot.gd" 2>&1)" || status=$?
  rmdir "$probe"
  if [ "$status" -eq 0 ] && grep -qF 'REPENTANCE GODOT OK' <<< "$output"; then return 0; fi
  printf "Cannot use Godot '%s':\n%s\n" "$godot" "$output" >&2
  echo "Install Godot 4 .NET/Mono (not the standard edition), then pass --godot <path> or set GODOT." >&2
  return 1
}

find_godot() {
  local explicit="${1:-}"
  if [ -n "$explicit" ]; then check_godot "$explicit" || return 1; echo "$explicit"; return; fi
  if [ -n "${GODOT:-}" ]; then check_godot "$GODOT" || return 1; echo "$GODOT"; return; fi
  local name found
  for name in godot_console godot-mono godot4-mono godot4 godot; do
    if found="$(command -v "$name")" && check_godot "$found"; then echo "$found"; return; fi
  done
  while IFS= read -r found; do
    if check_godot "$found"; then echo "$found"; return; fi
  done < <(find "$HOME/godot" "$HOME/Applications" /Applications "${LOCALAPPDATA:-/nonexistent}/Godot" \
    \( -name 'Godot_v*_mono_linux.x86_64' -o -name 'Godot_v*_mono_*console.exe' -o -path '*Godot_mono.app/Contents/MacOS/Godot' \) \
    -type f 2>/dev/null | sort -r || true)
  echo "Godot 4 .NET not found. Pass --godot <path>, or set GODOT." >&2
  return 1
}

user_data_dir() {
  if [ -n "${APPDATA:-}" ]; then echo "$APPDATA/Godot/app_userdata/Repentance"
  elif [ "$(uname)" = "Darwin" ]; then echo "$HOME/Library/Application Support/Godot/app_userdata/Repentance"
  else echo "${XDG_DATA_HOME:-$HOME/.local/share}/godot/app_userdata/Repentance"
  fi
}

# Deletes everything generated (imports, builds, screenshots, frames, logs, the test-only saves and settings).
# Player saves (user://saves) and settings (user://settings.cfg) are never touched.
reset_generated() {
  echo "== Clean reset"
  local data t
  data="$(user_data_dir)"
  local targets=("$ROOT/.godot" "$ROOT/.mono" "$ROOT/bin" "$ROOT/obj" "$ROOT/screenshots" "$ROOT/frames" "$ROOT/logs"
    "$data/autoplay_saves" "$data/autoplay_settings.cfg")
  while IFS= read -r t; do targets+=("$t"); done < <(find "$ROOT/tests" -type d \( -name bin -o -name obj \) -prune 2>/dev/null)
  for t in "${targets[@]}"; do
    if [ -e "$t" ]; then rm -rf "$t"; echo "  removed $t"; fi
  done
}

# The Ink importer is C#, so the build must come before the import.
build_and_import() {
  local godot="$1"
  (cd "$ROOT"
    echo "== dotnet build"
    dotnet build Repentance.csproj --nologo -v quiet
    echo "== Godot import"
    mkdir -p "$LOG_DIR"
    local log="$LOG_DIR/import.log" status=0
    # shellcheck disable=SC2086
    "$godot" --headless $GODOT_FLAGS --path . --import 2>&1 | tee "$log" || status=$?
    if [ "$status" -ne 0 ]; then echo "Godot import failed (exit code $status); see $log." >&2; return 1; fi
    if grep -nE "$ERROR_PATTERN" "$log" | grep -vF "$IMPORT_NOISE" >&2; then
      echo "Godot import logged errors; see $log. Launch cancelled." >&2
      return 1
    fi)
}

# godot_run <godot> <name> <markers, |-separated> [engine args...] -- <user args...>
# Tees the output to logs/<name>.log; succeeds when the run exited cleanly, printed a marker and logged no errors.
# With ERRORS_ARE_WARNINGS=1 (film/normal play), logged errors are reported but don't fail the run.
# REQUIRE_MARKER=0 explicitly disables marker checks for normal interactive play.
godot_run() {
  local godot="$1" name="$2" markers="$3"; shift 3
  local engine=() user=()
  while [ $# -gt 0 ] && [ "$1" != "--" ]; do engine+=("$1"); shift; done
  [ $# -gt 0 ] && shift
  user=("$@")
  mkdir -p "$LOG_DIR"
  local log="$LOG_DIR/$name.log" status=0 ok=0
  echo "== $name (${user[*]})"
  # shellcheck disable=SC2086
  (cd "$ROOT" && "$godot" --path . $GODOT_FLAGS ${engine[@]+"${engine[@]}"} -- ${user[@]+"${user[@]}"} 2>&1 | tee "$log"
    exit "${PIPESTATUS[0]}") || status=$?
  if [ "$status" -ne 0 ]; then echo "Godot exited with status $status" >&2; ok=1; fi
  if [ "${REQUIRE_MARKER:-1}" != 0 ]; then
    local found=0 m
    local ms=()
    IFS='|' read -r -a ms <<< "$markers"
    for m in "${ms[@]}"; do grep -qF "$m" "$log" && found=1; done
    if [ "$found" -eq 0 ]; then echo "None of '$markers' found in $log" >&2; ok=1; fi
  fi
  if grep -nE "$ERROR_PATTERN" "$log" >&2; then
    echo "Godot logged errors (see above)" >&2
    [ "${ERRORS_ARE_WARNINGS:-0}" = 1 ] || ok=1
  fi
  return $ok
}

find_python() {
  local c
  # Run each candidate: on Windows, python/python3 can be Microsoft Store stubs that only print an install hint.
  local candidates=(${PYTHON:+"$PYTHON"} python3 python py)
  if [ -n "${LOCALAPPDATA:-}" ] && command -v cygpath >/dev/null 2>&1; then
    while IFS= read -r c; do candidates+=("$c"); done < <(ls -d "$(cygpath -u "$LOCALAPPDATA")"/Programs/Python/Python3*/python.exe 2>/dev/null | sort -rV)
  fi
  for c in "${candidates[@]}"; do
    if "$c" -c 'import sys; sys.exit(sys.version_info[0] != 3)' >/dev/null 2>&1; then echo "$c"; return; fi
  done
  echo "Python 3 not found (needed for the art tests, with pillow and numpy). Set PYTHON to its path." >&2
  return 1
}
