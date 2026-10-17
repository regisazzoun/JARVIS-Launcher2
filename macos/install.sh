#!/bin/bash
set -euo pipefail
if [ "$(uname -s)" != Darwin ]; then printf '%s\n' 'Installation uniquement sur macOS.' >&2; exit 1; fi
case "${1:-}" in macbook-pro|mac-mini) client_profile=$1 ;; *) printf '%s\n' 'Usage : bash macos/install.sh macbook-pro | mac-mini' >&2; exit 2 ;; esac
project_root=$(cd -- "$(dirname "$0")/.." && pwd)
application_dir="$HOME/Applications"
application_path="$application_dir/JARVIS Launcher.app"
configuration_dir="$HOME/Library/Application Support/JARVIS Launcher"
temporary_dir=$(mktemp -d "${TMPDIR:-/tmp}/jarvis-launcher-build.XXXXXX")
trap 'rm -rf -- "$temporary_dir"' EXIT
mkdir -p -- "$application_dir" "$configuration_dir"
chmod 700 "$configuration_dir"
/usr/bin/osascript -l JavaScript "$project_root/macos/setup.js" "$project_root" "$configuration_dir/config.json" "$client_profile"
chmod 600 "$configuration_dir/config.json"
/usr/bin/osacompile -o "$temporary_dir/JARVIS Launcher.app" "$project_root/macos/Launcher.applescript"
resources="$temporary_dir/JARVIS Launcher.app/Contents/Resources"
cp -- "$project_root/site/core.js" "$resources/core.js"
cp -- "$project_root/macos/launcher.js" "$resources/launcher.js"
cp -- "$project_root/macos/hardware.js" "$resources/hardware.js"
plist="$temporary_dir/JARVIS Launcher.app/Contents/Info.plist"
/usr/libexec/PlistBuddy -c 'Set :CFBundleIdentifier fr.jarvis.launcher' "$plist" 2>/dev/null || /usr/libexec/PlistBuddy -c 'Add :CFBundleIdentifier string fr.jarvis.launcher' "$plist"
/usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes array' "$plist"
/usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0 dict' "$plist"
/usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLName string JARVIS Launcher' "$plist"
/usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLSchemes array' "$plist"
/usr/libexec/PlistBuddy -c 'Add :CFBundleURLTypes:0:CFBundleURLSchemes:0 string jarvis-launcher' "$plist"
/usr/libexec/PlistBuddy -c 'Add :NSAppleEventsUsageDescription string Ouvrir vos terminaux JARVIS après confirmation locale.' "$plist" 2>/dev/null || /usr/libexec/PlistBuddy -c 'Set :NSAppleEventsUsageDescription Ouvrir vos terminaux JARVIS après confirmation locale.' "$plist"
/usr/bin/codesign --force --deep --sign - "$temporary_dir/JARVIS Launcher.app"
if [ -e "$application_path" ]; then
  backup_path="$application_path.backup-$(date +%Y%m%d-%H%M%S)-$$"
  mv -- "$application_path" "$backup_path"
  printf 'Ancienne application conservée : %s\n' "$backup_path"
fi
mv -- "$temporary_dir/JARVIS Launcher.app" "$application_path"
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$application_path"
printf 'Application : %s\nConfiguration locale : %s\n' "$application_path" "$configuration_dir/config.json"
printf 'Vérification locale : open "jarvis-launcher://launch/%s/check"\n' "$client_profile"
printf '%s\n' 'La clé SSH doit déjà être présente ; aucune clé ni configuration SSH existante n’a été remplacée.'
