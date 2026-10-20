#!/usr/bin/env bash
# Prepares a Linux machine (CI runner) to export the Android preset with Godot:
#   tools/package/android-sdk.sh
# Installs the SDK packages Godot needs into $ANDROID_HOME (the runners ship the SDK and JDK 17) and points
# Godot's editor settings at the SDK and JDK. Signing comes from GODOT_ANDROID_KEYSTORE_* environment variables
# at export time (see docs/ci-and-release.md).
set -euo pipefail

sdk="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
java="${JAVA_HOME_17_X64:-${JAVA_HOME:-}}"
[ -n "$sdk" ] && [ -d "$sdk" ] || { echo "::error::ANDROID_HOME is not set to an Android SDK"; exit 1; }
[ -n "$java" ] && [ -x "$java/bin/java" ] || { echo "::error::JDK 17 not found (JAVA_HOME_17_X64 / JAVA_HOME)"; exit 1; }

sdkmanager="$(ls "$sdk"/cmdline-tools/*/bin/sdkmanager 2>/dev/null | head -n1)"
[ -n "$sdkmanager" ] || { echo "::error::sdkmanager not found under $sdk/cmdline-tools"; exit 1; }
yes | JAVA_HOME="$java" "$sdkmanager" --sdk_root="$sdk" --licenses > /dev/null || true
JAVA_HOME="$java" "$sdkmanager" --sdk_root="$sdk" "platform-tools" "build-tools;35.0.1" "platforms;android-35" > /dev/null

# Godot reads these from its editor settings; one file per version scheme it has used.
config="${XDG_CONFIG_HOME:-$HOME/.config}/godot"
mkdir -p "$config"
version="$("$GODOT" --headless --version | grep -oE '^[0-9]+\.[0-9]+')"
for name in "editor_settings-${version}.tres" "editor_settings-${version%%.*}.tres"; do
  cat > "$config/$name" <<EOF
[gd_resource type="EditorSettings" format=3]

[resource]
export/android/android_sdk_path = "$sdk"
export/android/java_sdk_path = "$java"
EOF
done

if [ -n "${GITHUB_ENV:-}" ]; then
  echo "JAVA_HOME=$java" >> "$GITHUB_ENV"
  echo "APKSIGNER=$sdk/build-tools/35.0.1/apksigner" >> "$GITHUB_ENV"
fi
echo "Android SDK $sdk, JDK $java"
