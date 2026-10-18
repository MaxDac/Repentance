#!/bin/sh
# Builds the per-user Windows installer (dist/windows/Repentance.nsi) from an exported Windows build.
#   tools/package/windows-installer.sh <export dir> <version X.Y.Z> <output setup.exe>
# Needs makensis (Debian/Ubuntu: apt install nsis).
set -eu

[ $# -eq 3 ] || { echo "usage: $0 <export dir> <version X.Y.Z> <output setup.exe>" >&2; exit 2; }
root="$(cd "$(dirname "$0")/../.." && pwd)"
src="$(cd "$1" && pwd)"
version="$2"
out="$(cd "$(dirname "$3")" && pwd)/$(basename "$3")"
command -v makensis >/dev/null 2>&1 || { echo "makensis not found (apt install nsis)" >&2; exit 1; }
[ -f "$src/Repentance.exe" ] || { echo "Repentance.exe not found in $src" >&2; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

# The uninstaller removes exactly these files, then the folders deepest first.
list="$work/uninstall.nsh"
(cd "$src" && find . -type f | sort) | sed -e 's|^\./||' -e 's|/|\\|g' -e 's|.*|  Delete "$INSTDIR\\&"|' > "$list"
(cd "$src" && find . -mindepth 1 -type d | sort -r) | sed -e 's|^\./||' -e 's|/|\\|g' -e 's|.*|  RMDir "$INSTDIR\\&"|' >> "$list"

makensis -V2 \
    "-DVERSION=$version" \
    "-DSOURCE=$src" \
    "-DOUTFILE=$out" \
    "-DICON=$root/assets/art/ui/icon.ico" \
    "-DUNINSTALL_LIST=$list" \
    "$root/dist/windows/Repentance.nsi"
echo "Built $out"
