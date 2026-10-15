#!/usr/bin/env bash
# Runs the test suites from a clean slate and prints a summary. Exits non-zero if any suite fails.
# Suites: unit, art, autoplay, settings, pause, walk, playthrough, or all (the default).
# Unless --no-clean is given, every generated file is deleted first and the project is rebuilt and reimported.
# Godot logs go to logs/<suite>.log; a Godot suite passes only with its marker and no ERROR lines.
#
# Usage: tools/run/test.sh [suite...] [--no-clean] [--godot PATH]
#   tools/run/test.sh
#   tools/run/test.sh unit playthrough --no-clean
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"
set +e

ORDER=(unit art autoplay settings pause walk playthrough)
# Godot suites: user arg and pass marker (case statements, since macOS ships bash 3.2 without associative arrays).
suite_arg() {
  case "$1" in
    autoplay) echo --autoplay ;; settings) echo --settings-test ;; pause) echo --pause-test ;;
    walk) echo --walk-test ;; playthrough) echo --playthrough ;;
  esac
}
suite_marker() {
  case "$1" in
    autoplay) echo "AUTOPLAY OK" ;; settings) echo "SETTINGS TEST OK" ;; pause) echo "PAUSE TEST OK" ;;
    walk) echo "WALK TEST OK" ;; playthrough) echo "PLAYTHROUGH OK" ;;
  esac
}

wanted=() clean=1 godot_arg=""
while [ $# -gt 0 ]; do
  case "$1" in
    --no-clean) clean=0 ;;
    --godot) godot_arg="$2"; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    all|unit|art|autoplay|settings|pause|walk|playthrough) wanted+=("$1") ;;
    *) echo "Unknown suite or option '$1'." >&2; exit 2 ;;
  esac
  shift
done
[ ${#wanted[@]} -eq 0 ] && wanted=(all)

selected=() needs_godot=0
for s in "${ORDER[@]}"; do
  for w in "${wanted[@]}"; do
    if [ "$w" = all ] || [ "$w" = "$s" ]; then
      selected+=("$s"); [ -n "$(suite_arg "$s")" ] && needs_godot=1; break
    fi
  done
done

set -e
if [ "$needs_godot" -eq 1 ]; then
  godot="$(find_godot "$godot_arg")"
  echo "Godot: $godot"
fi
[ "$clean" -eq 1 ] && reset_generated
if [ "$needs_godot" -eq 1 ]; then
  build_and_import "$godot"
fi
set +e

results=() failed=0
for s in "${selected[@]}"; do
  start=$SECONDS
  case "$s" in
    unit)
      echo "== unit"
      (cd "$ROOT" && dotnet test tests/Repentance.Tests/Repentance.Tests.csproj --nologo) ;;
    art)
      echo "== art"
      py="$(find_python)" &&
        (cd "$ROOT" && "$py" -m unittest discover -s tests/art -v &&
          "$py" -m unittest discover -s tests -p test_character_art.py -v) ;;
    *)
      # Not --headless: AutoPlay captures viewport screenshots, which need a real renderer (use xvfb-run in CI).
      godot_run "$godot" "$s" "$(suite_marker "$s")" --audio-driver Dummy -- "$(suite_arg "$s")" ;;
  esac
  if [ $? -eq 0 ]; then state=PASS; else state=FAIL; failed=$((failed + 1)); fi
  results+=("$(printf '  %-12s %s  %5ss' "$s" "$state" "$((SECONDS - start))")")
done

echo
echo "== Summary"
printf '%s\n' "${results[@]}"
if [ "$failed" -gt 0 ]; then echo "$failed suite(s) failed. Godot logs: logs/" >&2; exit 1; fi
echo "All suites passed."
