#!/usr/bin/env bash
# Play the game normally after cleaning generated files, building and importing.
# Player saves and settings are never touched. Quit the game normally to finish.
# Runtime errors are reported as warnings; build/import errors and nonzero exits fail.
#
# Usage: tools/run/game.sh [--no-clean] [--godot PATH]
#   tools/run/game.sh
#   tools/run/game.sh --no-clean
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

clean=1 godot_arg=""
while [ $# -gt 0 ]; do
  case "$1" in
    --no-clean) clean=0 ;;
    --godot)
      if [ $# -lt 2 ] || [ -z "$2" ] || [[ "$2" == --* ]]; then
        echo "--godot requires a path." >&2; exit 2
      fi
      godot_arg="$2"; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "Unknown argument '$1'; see --help." >&2; exit 2 ;;
  esac
  shift
done

godot="$(find_godot "$godot_arg")"
echo "Godot: $godot"
[ "$clean" -eq 1 ] && reset_generated
build_and_import "$godot"
if REQUIRE_MARKER=0 ERRORS_ARE_WARNINGS=1 godot_run "$godot" game "" --; then
  echo "Game closed."
else
  echo "Game failed; see the log above." >&2
  exit 1
fi
