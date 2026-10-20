#!/usr/bin/env bash
# Exports the Android preset to a signed APK and checks it:
#   tools/package/android-export.sh debug   <out.apk>
#   tools/package/android-export.sh release <out.apk> <X.Y.Z>
# Needs $GODOT, an imported project, tools/package/android-sdk.sh run first and $APKSIGNER. Debug exports sign with
# a throwaway key made here; release exports sign with GODOT_ANDROID_KEYSTORE_RELEASE_PATH/USER/PASSWORD.
set -euo pipefail

mode="$1" out="$2" version="${3:-0.0.0}"
[[ "$version" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]] || { echo "::error::version '$version' is not X.Y.Z"; exit 1; }
# Android needs a growing integer per upload: 1.2.3 -> 10203
code=$(( BASH_REMATCH[1] * 10000 + BASH_REMATCH[2] * 100 + BASH_REMATCH[3] ))
code=$(( code > 0 ? code : 1 ))
cp export_presets.cfg "${RUNNER_TEMP:-/tmp}/export_presets.cfg.bak"
trap 'mv -f "${RUNNER_TEMP:-/tmp}/export_presets.cfg.bak" export_presets.cfg' EXIT
sed -i -E "s/^version\/code=.*/version\/code=$code/; s/^version\/name=.*/version\/name=\"$version\"/" export_presets.cfg

case "$mode" in
  debug)
    if [ -z "${GODOT_ANDROID_KEYSTORE_DEBUG_PATH:-}" ]; then
      key="${RUNNER_TEMP:-/tmp}/repentance-debug.keystore"
      rm -f "$key"
      keytool -genkeypair -keystore "$key" -storetype PKCS12 -alias androiddebugkey -storepass android \
        -keypass android -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Android Debug,O=Android,C=US" > /dev/null 2>&1
      export GODOT_ANDROID_KEYSTORE_DEBUG_PATH="$key" GODOT_ANDROID_KEYSTORE_DEBUG_USER=androiddebugkey \
        GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD=android
    fi
    flag=--export-debug ;;
  release)
    for v in GODOT_ANDROID_KEYSTORE_RELEASE_PATH GODOT_ANDROID_KEYSTORE_RELEASE_USER GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD; do
      [ -n "${!v:-}" ] || { echo "::error::$v is not set (release signing secrets missing?)"; exit 1; }
    done
    flag=--export-release ;;
  *) echo "usage: $0 debug|release <out.apk> [X.Y.Z]"; exit 2 ;;
esac

mkdir -p "$(dirname "$out")"
rm -f "$out"
"$GODOT" --headless --path . "$flag" Android "$out"
git checkout -- export_presets.cfg 2>/dev/null || true

test -f "$out" || { echo "::error::Godot did not write $out"; exit 1; }
# Godot exits 0 even when the C# export step fails; the game's assembly inside the APK proves it ran.
unzip -l "$out" | grep -q 'Repentance\.dll' || { echo "::error::$out has no Repentance.dll (C# export failed)"; exit 1; }
"${APKSIGNER:-apksigner}" verify --print-certs "$out" | grep -E 'Signer #1 certificate (DN|SHA-256)'
ls -la "$out"
