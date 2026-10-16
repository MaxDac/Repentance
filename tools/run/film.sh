#!/usr/bin/env bash
# Film mode: watch the whole game play itself, title to "The End".
# Resets every generated file (imports, builds, logs, test saves) and rebuilds first. Your own saves are never touched.
# Input is ignored, except Space (pause), F11 (full screen) and Esc (stop).
#
# Usage: tools/run/film.sh [1|2|4] [--ending 1-10|1-oldman|1-steps] [--no-clean] [--godot PATH]
#   tools/run/film.sh            # 1x, ending 2
#   tools/run/film.sh 4 --ending 5
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

speed=1 ending=2 clean=1 godot_arg=""
while [ $# -gt 0 ]; do
  case "$1" in
    1|2|4) speed="$1" ;;
    --ending) ending="$2"; shift ;;
    --ending=*) ending="${1#*=}" ;;
    --no-clean) clean=0 ;;
    --godot) godot_arg="$2"; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "Unknown argument '$1' (speed is 1, 2 or 4)." >&2; exit 2 ;;
  esac
  shift
done
case "$ending" in 1|2|3|4|5|6|7|8|9|10|1-oldman|1-steps) ;; *) echo "--ending must be 1-10, 1-oldman or 1-steps." >&2; exit 2 ;; esac

godot="$(find_godot "$godot_arg")"
echo "Godot: $godot"
[ "$clean" -eq 1 ] && reset_generated
build_and_import "$godot"
# Logged errors are reported but don't stop the show (no audio device, for one, makes the engine log some).
if ERRORS_ARE_WARNINGS=1 godot_run "$godot" "film_${speed}x" "FILM OK|FILM STOPPED" -- "--film=$speed" "--ending=$ending"; then
  echo "Film finished."
else
  echo "Film failed; see the log above." >&2
  exit 1
fi
