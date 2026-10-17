#!/bin/bash
set -euo pipefail
if [ "$(uname -s)" != Darwin ]; then printf '%s\n' 'Désinstallation uniquement sur macOS.' >&2; exit 1; fi
application_path="$HOME/Applications/JARVIS Launcher.app"
if [ ! -d "$application_path" ]; then printf '%s\n' 'Application absente. Configuration et clés conservées.'; exit 0; fi
printf '%s\n' 'Déplacer JARVIS Launcher.app dans la Corbeille ? La configuration, les clés SSH et les sauvegardes seront conservées. [oui/non]'
read -r response
if [ "$response" != oui ]; then exit 0; fi
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "$application_path"
mkdir -p "$HOME/.Trash"
mv -- "$application_path" "$HOME/.Trash/JARVIS Launcher.app-$(date +%Y%m%d-%H%M%S)-$$"
printf '%s\n' 'Application déplacée dans la Corbeille. Aucun service à arrêter.'
