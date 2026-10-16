#!/usr/bin/env bash
# Film mode: watch the game play itself to "The End", at 1x to 60x ("hyper") speed, from any chapter.
# Resets every generated file (imports, builds, logs, test saves) and rebuilds first. Your own saves are never touched.
# Input is ignored, except Space (pause), F11 (full screen) and Esc (stop).
# --from starts at a chapter: the earlier story still plays, unseen and muted, at 60x behind a black screen.
#
# Usage: tools/run/film.sh [1|2|4|8|16|60|hyper] [--ending 1-10|1-oldman|1-steps]
#                          [--from act1|interlude1|act2|interlude2|act3|ending] [--no-clean] [--godot PATH]
#   tools/run/film.sh            # 1x, ending 2
#   tools/run/film.sh 4 --ending 5
#   tools/run/film.sh hyper --from ending --ending 8
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

speed=1 ending=2 from=act1 clean=1 godot_arg=""
while [ $# -gt 0 ]; do
  case "$1" in
    1|2|4|8|16|60|hyper) speed="$1" ;;
    --ending) ending="$2"; shift ;;
    --ending=*) ending="${1#*=}" ;;
    --from) from="$2"; shift ;;
    --from=*) from="${1#*=}" ;;
    --no-clean) clean=0 ;;
    --godot) godot_arg="$2"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Unknown argument '$1' (speed is 1, 2, 4, 8, 16, 60 or hyper)." >&2; exit 2 ;;
  esac
  shift
done
case "$ending" in 1|2|3|4|5|6|7|8|9|10|1-oldman|1-steps) ;; *) echo "--ending must be 1-10, 1-oldman or 1-steps." >&2; exit 2 ;; esac
case "$from" in act1|interlude1|act2|interlude2|act3|ending) ;; *) echo "--from must be act1, interlude1, act2, interlude2, act3 or ending." >&2; exit 2 ;; esac
if [ "$from" = act3 ] && [ "$ending" = 1-steps ]; then
  echo "Ending 1-steps ends in the Second Interlude, before Act 3; pick another --from." >&2; exit 2
fi

godot="$(find_godot "$godot_arg")"
echo "Godot: $godot"
[ "$clean" -eq 1 ] && reset_generated
build_and_import "$godot"
name="film_${speed}x"
[ "$from" != act1 ] && name="${name}_from_$from"
# Logged errors are reported but don't stop the show (no audio device, for one, makes the engine log some).
if ERRORS_ARE_WARNINGS=1 godot_run "$godot" "$name" "FILM OK|FILM STOPPED" -- "--film=$speed" "--ending=$ending" "--from=$from"; then
  echo "Film finished."
else
  echo "Film failed; see the log above." >&2
  exit 1
fi
