#!/bin/sh
# Adds Repentance to the desktop menu (GNOME, KDE, Xfce...) with its icon, for the current user.
# Run it from the unpacked release folder; run it again after moving that folder.
#   ./install-desktop.sh              install
#   ./install-desktop.sh --uninstall  remove the menu entry and the icons
set -eu

here="$(cd "$(dirname "$0")" && pwd)"
data="${XDG_DATA_HOME:-$HOME/.local/share}"
apps="$data/applications"
icons="$data/icons/hicolor"
entry="$apps/Repentance.desktop"

refresh() {
    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
        gtk-update-icon-cache -q -t -f "$icons" || true
    fi
    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database -q "$apps" || true
    fi
}

if [ "${1:-}" = "--uninstall" ]; then
    rm -f "$entry"
    for dir in "$here"/icons/hicolor/*/apps; do
        size="$(basename "$(dirname "$dir")")"
        rm -f "$icons/$size/apps/repentance.png"
    done
    refresh
    echo "Removed Repentance from the desktop menu."
    exit 0
fi

binary="$here/Repentance.x86_64"
if [ ! -x "$binary" ]; then
    echo "Repentance.x86_64 not found next to this script ($here)." >&2
    exit 1
fi

for dir in "$here"/icons/hicolor/*/apps; do
    size="$(basename "$(dirname "$dir")")"
    mkdir -p "$icons/$size/apps"
    cp "$dir/repentance.png" "$icons/$size/apps/repentance.png"
done

# Exec takes a quoted path; escape the characters the Desktop Entry spec reserves inside quotes.
quoted="$(printf '%s' "$binary" | sed -e 's/[\\"`$]/\\&/g')"
mkdir -p "$apps"
sed -e "s|^Exec=.*|Exec=\"$(printf '%s' "$quoted" | sed -e 's/[\\&|]/\\&/g')\"|" \
    -e "/^Exec=/a Path=$(printf '%s' "$here" | sed -e 's/[\\&|]/\\&/g')" \
    "$here/Repentance.desktop" > "$entry"
chmod 644 "$entry"
refresh
echo "Installed $entry"