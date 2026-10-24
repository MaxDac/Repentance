#!/usr/bin/env bash
# Film mode: watch the game play itself to "The End", at 1x to 60x ("hyper") speed, from any chapter.
# Resets every generated file (imports, builds, logs, test saves) and rebuilds first. Your own saves are never touched.
# Input is ignored, except Space (pause), F11 (full screen) and Esc (stop).
# --from starts at a chapter: the earlier story still plays, unseen and muted, at 60x behind a black screen.
#
# Usage: tools/run/film.sh [--speed|-s 1|2|4|8|16|60|hyper] [--ending NUMBER|TITLE]
#                          [--from act1|interlude1|act2|interlude2|act3|ending] [--no-clean] [--godot PATH]
#   tools/run/film.sh            # 1x, ending 2
#   tools/run/film.sh --speed 4 --ending 5
#   tools/run/film.sh --speed 4 --ending prison-caleb-visits   # the same as --ending 5
#   tools/run/film.sh -s hyper --from ending --ending 8
#
# Endings: pass the number or the title (case-insensitive). The numbers are the ones used in docs/story-overview.md
# ("Branches and endings") and by the playthrough routes; 1-oldman, 1-steps and 1-caleb are other routes to ending 1,
# 12-oldman another route to ending 12.
#   Number    Title                    Ending
#   1         walk-away                Micah lowers the gun on Tony; coffee with Rose
#   1-oldman  spare-the-old-man        He prays the Our Father and spares the old man; coffee with Rose
#   1-steps   give-up                  He gives up on the cathedral steps; coffee with Rose
#   1-caleb   eleanor-escapes          Eleanor held out, he lowers the gun on Tony; Rose, then Eleanor and Caleb
#   2         escape-together          Evidence or fire, Eleanor convinced; out of town with her
#   3         escape-alone             Evidence or fire, Eleanor not convinced; out of town alone
#   4         prison-eleanor-visits    Neither, Eleanor convinced; prison, Eleanor visits
#   5         prison-caleb-visits      Neither, Eleanor not convinced; prison, Caleb visits
#   6         turn-himself-in          He turns himself in; prison, Rose visits
#   7         last-entry               He shoots Eleanor and/or himself; Caleb writes the last entry
#   8         eleanor-burns-the-house  Eleanor strikes the old man and burns the cellar; Rose, then Eleanor alone
#   9         eleanor-confesses        Eleanor strikes the old man; Rose, then she confesses to Caleb in prison
#   10        she-leaves-by-the-car    Eleanor follows after the shot, evidence or fire; she leaves him by the car
#   11        she-visits-once          Eleanor follows after the shot, nothing taken; prison, she visits once
#   12        kill-tony-surrender      He kills Tony, confesses to Caleb and turns himself in; prison, Caleb visits
#   12-oldman kill-tony-pray           He kills Tony, confesses, spares the old man, then gives himself up
#   13        alarm-run                A warning shot; the unseen alarm rings and he runs; out of Chicago, alone
#   14        alarm-ambush             A warning shot; the unseen alarm rings and he goes in; shot in the kitchen
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# Keep in step with the table above and with film.ps1.
ending_number() {
  case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
    1|walk-away) echo 1 ;;
    1-oldman|spare-the-old-man) echo 1-oldman ;;
    1-steps|give-up) echo 1-steps ;;
    1-caleb|eleanor-escapes) echo 1-caleb ;;
    2|escape-together) echo 2 ;;
    3|escape-alone) echo 3 ;;
    4|prison-eleanor-visits) echo 4 ;;
    5|prison-caleb-visits) echo 5 ;;
    6|turn-himself-in) echo 6 ;;
    7|last-entry) echo 7 ;;
    8|eleanor-burns-the-house) echo 8 ;;
    9|eleanor-confesses) echo 9 ;;
    10|she-leaves-by-the-car) echo 10 ;;
    11|she-visits-once) echo 11 ;;
    12|kill-tony-surrender) echo 12 ;;
    12-oldman|kill-tony-pray) echo 12-oldman ;;
    13|alarm-run) echo 13 ;;
    14|alarm-ambush) echo 14 ;;
    *) return 1 ;;
  esac
}

speed=1 ending=2 from=act1 clean=1 godot_arg=""
while [ $# -gt 0 ]; do
  case "$1" in
    --speed|-s|--ending|--from|--godot)
      if [ $# -lt 2 ] || [ -z "$2" ] || [[ "$2" == --* ]]; then
        echo "$1 requires a value." >&2; exit 2
      fi
      case "$1" in
        --speed|-s) speed="$2" ;;
        --ending) ending="$2" ;;
        --from) from="$2" ;;
        --godot) godot_arg="$2" ;;
      esac
      shift ;;
    --speed=*) speed="${1#*=}" ;;
    --ending=*) ending="${1#*=}" ;;
    --from=*) from="${1#*=}" ;;
    --no-clean) clean=0 ;;
    -h|--help) sed -n '2,35p' "$0"; exit 0 ;;
    *) echo "Unknown argument '$1'. Use --speed <value> or -s <value> (default: 1); see --help." >&2; exit 2 ;;
  esac
  shift
done
case "$speed" in 1|2|4|8|16|60|hyper) ;; *) echo "--speed / -s must be 1, 2, 4, 8, 16, 60 or hyper." >&2; exit 2 ;; esac
if ! ending="$(ending_number "$ending")"; then
  echo "--ending must be an ending number (1-14, 1-oldman, 1-steps, 1-caleb, 12-oldman) or its title; see --help." >&2; exit 2
fi
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
