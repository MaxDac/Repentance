#!/bin/sh
# Packs an exported Linux build into a single-file AppImage with the desktop entry and icons from dist/linux.
#   tools/package/appimage.sh <export dir> <output .AppImage>
# Downloads appimagetool (pinned) into a temporary folder; needs curl.
set -eu

[ $# -eq 2 ] || { echo "usage: $0 <export dir> <output .AppImage>" >&2; exit 2; }
root="$(cd "$(dirname "$0")/../.." && pwd)"
src="$(cd "$1" && pwd)"
out="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"
tool_version=1.9.1
[ -x "$src/Repentance.x86_64" ] || { echo "Repentance.x86_64 not found in $src" >&2; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
appdir="$work/Repentance.AppDir"
mkdir -p "$appdir/usr/share"

# The game only: the zip's desktop helpers are replaced by the AppImage's own entry and icons.
cp -a "$src/." "$appdir/"
rm -rf "$appdir/icons" "$appdir/install-desktop.sh" "$appdir/Repentance.desktop"
cp "$root/dist/linux/Repentance.desktop" "$appdir/Repentance.desktop"
cp -r "$root/dist/linux/icons" "$appdir/usr/share/icons"
cp "$root/dist/linux/icons/hicolor/256x256/apps/repentance.png" "$appdir/repentance.png"
ln -s repentance.png "$appdir/.DirIcon"
cat > "$appdir/AppRun" <<'EOF'
#!/bin/sh
here="$(dirname "$(readlink -f "$0")")"
exec "$here/Repentance.x86_64" "$@"
EOF
chmod +x "$appdir/AppRun"

tool="$work/appimagetool"
curl -fsSL -o "$tool" \
    "https://github.com/AppImage/appimagetool/releases/download/$tool_version/appimagetool-x86_64.AppImage"
chmod +x "$tool"
# Extract-and-run: CI runners have no FUSE.
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 "$tool" --no-appstream "$appdir" "$out"
echo "Built $out"
