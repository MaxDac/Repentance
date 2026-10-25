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
# ("Branches and endings") and by the playthrough routes; a suffixed number (1-oldman, 15-steps-caleb, 8-kill...) is
# another route to the same ending, each a different final scene.
#   Number         Title                           Ending
#   1              walk-away                       Micah lowers the gun on Tony; coffee with Rose
#   1-oldman       spare-the-old-man               He prays the Our Father and spares the old man; coffee with Rose
#   1-steps        give-up                         He gives up on the cathedral steps; coffee with Rose
#   1-steps-caleb  give-up-eleanor-escapes         As 1-steps, and Eleanor held out; Rose, then Eleanor and Caleb
#   1-caleb        eleanor-escapes                 Eleanor held out, he lowers the gun on Tony; Rose, then Eleanor and Caleb
#   1-bed          eleanor-back-to-bed             Eleanor held out, he prays; she goes back to bed, he goes to Rose
#   2              escape-together                 Evidence or fire, Eleanor convinced; out of town with her
#   3              escape-alone                    Evidence or fire, Eleanor not convinced; out of town alone
#   4              prison-eleanor-visits           Neither, Eleanor convinced; prison, Eleanor visits
#   5              prison-caleb-visits             Neither, Eleanor not convinced; prison, Caleb visits
#   6              turn-himself-in                 He turns himself in; prison, Rose visits
#   7              last-entry                      He shoots Eleanor, then himself; Caleb writes the last entry
#   7-alone        last-entry-alone                Four turns without her, the footsteps; he shoots himself alone
#   8              eleanor-burns-the-house         Eleanor strikes the old man and burns the cellar; Rose, then Eleanor alone
#   8-kill         kill-tony-eleanor-burns         As 12-oldman, Eleanor held out; she strikes him and burns the cellar
#   9              eleanor-confesses               Eleanor strikes the old man; Rose, then she confesses to Caleb in prison
#   9-kill         kill-tony-eleanor-confesses     As 12-oldman, Eleanor held out; she strikes him and confesses to Caleb
#   10             she-leaves-by-the-car           Eleanor follows after the shot, evidence or fire; she leaves him by the car
#   11             she-visits-once                 Eleanor follows after the shot, nothing taken; prison, she visits once
#   12             kill-tony-surrender             He kills Tony, confesses to Caleb and turns himself in; prison, Caleb visits
#   12-oldman      kill-tony-pray                  He kills Tony, confesses, spares the old man, then gives himself up
#   12-bed         kill-tony-eleanor-back-to-bed   As 12-oldman, Eleanor held out; she goes back to bed, he to the station
#   13             alarm-run                       A warning shot; the unseen alarm rings and he runs; out of Chicago, alone
#   13-caleb       alarm-run-eleanor-escapes       As 13, and Eleanor held out; then Eleanor and Caleb at the city's edge
#   14             alarm-ambush                    A warning shot; the unseen alarm rings and he goes in; shot in the kitchen
#   14-caleb       alarm-ambush-eleanor-escapes    As 14, and Eleanor held out; then Eleanor and Caleb at the city's edge
#   15             sunday-visits                   He walks away from Tony without having pressed Rose; she refuses the coffee
#   15-caleb       sundays-eleanor-escapes         As 15, and Eleanor held out; Rose's door, then Eleanor and Caleb
#   15-steps       sundays-give-up                 As 1-steps without having pressed Rose; she refuses the coffee
#   15-steps-caleb sundays-give-up-eleanor-escapes As 15-steps, and Eleanor held out; Rose's door, then Eleanor and Caleb
#   15-oldman      sundays-spare-the-old-man       As 1-oldman without having pressed Rose; she refuses the coffee
#   15-bed         sundays-eleanor-back-to-bed     As 1-bed without having pressed Rose; she refuses the coffee
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

# Keep in step with the table above and with film.ps1.
ending_number() {
  case "$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')" in
    1|walk-away) echo 1 ;;
    1-oldman|spare-the-old-man) echo 1-oldman ;;
    1-steps|give-up) echo 1-steps ;;
    1-steps-caleb|give-up-eleanor-escapes) echo 1-steps-caleb ;;
    1-caleb|eleanor-escapes) echo 1-caleb ;;
    1-bed|eleanor-back-to-bed) echo 1-bed ;;
    2|escape-together) echo 2 ;;
    3|escape-alone) echo 3 ;;
    4|prison-eleanor-visits) echo 4 ;;
    5|prison-caleb-visits) echo 5 ;;
    6|turn-himself-in) echo 6 ;;
    7|last-entry) echo 7 ;;
    7-alone|last-entry-alone) echo 7-alone ;;
    8|eleanor-burns-the-house) echo 8 ;;
    8-kill|kill-tony-eleanor-burns) echo 8-kill ;;
    9|eleanor-confesses) echo 9 ;;
    9-kill|kill-tony-eleanor-confesses) echo 9-kill ;;
    10|she-leaves-by-the-car) echo 10 ;;
    11|she-visits-once) echo 11 ;;
    12|kill-tony-surrender) echo 12 ;;
    12-oldman|kill-tony-pray) echo 12-oldman ;;
    12-bed|kill-tony-eleanor-back-to-bed) echo 12-bed ;;
    13|alarm-run) echo 13 ;;
    13-caleb|alarm-run-eleanor-escapes) echo 13-caleb ;;
    14|alarm-ambush) echo 14 ;;
    14-caleb|alarm-ambush-eleanor-escapes) echo 14-caleb ;;
    15|sunday-visits) echo 15 ;;
    15-caleb|sundays-eleanor-escapes) echo 15-caleb ;;
    15-steps|sundays-give-up) echo 15-steps ;;
    15-steps-caleb|sundays-give-up-eleanor-escapes) echo 15-steps-caleb ;;
    15-oldman|sundays-spare-the-old-man) echo 15-oldman ;;
    15-bed|sundays-eleanor-back-to-bed) echo 15-bed ;;
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
    -h|--help) sed -n '2,49p' "$0"; exit 0 ;;
    *) echo "Unknown argument '$1'. Use --speed <value> or -s <value> (default: 1); see --help." >&2; exit 2 ;;
  esac
  shift
done
case "$speed" in 1|2|4|8|16|60|hyper) ;; *) echo "--speed / -s must be 1, 2, 4, 8, 16, 60 or hyper." >&2; exit 2 ;; esac
if ! ending="$(ending_number "$ending")"; then
  echo "--ending must be an ending number (1-15, or a route such as 1-oldman or 15-steps-caleb) or its title; see --help." >&2; exit 2
fi
case "$from" in act1|interlude1|act2|interlude2|act3|ending) ;; *) echo "--from must be act1, interlude1, act2, interlude2, act3 or ending." >&2; exit 2 ;; esac
if [ "$from" = act3 ] && [[ "$ending" == *-steps* ]]; then
  echo "Ending $ending ends in the Second Interlude, before Act 3; pick another --from." >&2; exit 2
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
