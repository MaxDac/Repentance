#!/usr/bin/env bash
# Runs the launcher regression tests (tests/test_run_scripts.py) on Linux, macOS or Windows (Git Bash).
# The tests run game, film and test launchers in throwaway projects against fake Godot and dotnet executables,
# through both Bash and PowerShell (pwsh). They need Python 3; the shell a machine lacks is skipped.
# No Godot, build or cleanup is involved. Extra arguments go to unittest, e.g. -k film.
# tools/run/test.sh launcher runs the same tests as part of the suite summary.
#
# Usage: tools/run/harness.sh [unittest args...]
#   tools/run/harness.sh
#   tools/run/harness.sh -k film
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

case "${1:-}" in -h|--help) sed -n '2,10p' "$0"; exit 0 ;; esac
py="$(find_python)"
# Under Git Bash, hand Python this bash: "bash" on the Windows PATH may be the WSL launcher.
if [ -z "${LAUNCHER_TEST_BASH:-}" ] && command -v cygpath >/dev/null 2>&1; then
  LAUNCHER_TEST_BASH="$(cygpath -w "$BASH")"
  export LAUNCHER_TEST_BASH
fi
cd "$ROOT"
exec "$py" -m unittest discover -s tests -p test_run_scripts.py -v "$@"
