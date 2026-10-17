#!/bin/bash
set -euo pipefail
project_root=$(cd -- "$(dirname "$0")/.." && pwd)
cd "$project_root"
[ "$(git remote get-url origin)" = https://github.com/regisazzoun/JARVIS-Launcher2.git ]
python3 scripts/build-pages.py
git push origin main
pages_work=$(mktemp -d)
trap 'rm -rf -- "$pages_work"' EXIT
cp -R dist/pages/. "$pages_work/"
git -C "$pages_work" init -q -b gh-pages
git -C "$pages_work" add .
git -C "$pages_work" -c user.name=Codex -c user.email=codex@localhost commit -qm 'Publish JL-02 frontend'
# Preserve Pages history when rerunning; never force-push an unrelated branch.
if git ls-remote --exit-code origin refs/heads/gh-pages > /dev/null 2>&1; then
 git -C "$pages_work" fetch -q "$project_root" gh-pages 2>/dev/null || git -C "$pages_work" fetch -q https://github.com/regisazzoun/JARVIS-Launcher2.git gh-pages
 git -C "$pages_work" reset --soft FETCH_HEAD
 git -C "$pages_work" -c user.name=Codex -c user.email=codex@localhost commit -qm 'Update JL-02 frontend' || true
fi
git -C "$pages_work" push https://github.com/regisazzoun/JARVIS-Launcher2.git HEAD:gh-pages
