#!/bin/bash
# Exports Xcode's agent skills into a temp folder and prints the path of Apple's
# resizability skill. Never copy the output into a repository (Xcode license).
# Runs under bash or zsh.
set -euo pipefail
OUT=$(mktemp -d "${TMPDIR:-/tmp}/dhwg-apple-skills.XXXXXX")
if ! xcrun agent skills export --output-dir "$OUT" >/dev/null 2>&1; then
  echo "export failed: needs Xcode 27.1+ (xcrun agent skills export)" >&2
  exit 3
fi
# Match by description, not folder name: Apple renamed this skill before.
for f in "$OUT"/*/SKILL.md; do
  if head -5 "$f" | grep -qi -E "resiz|iPhone Duo"; then
    dirname "$f"
    exit 0
  fi
done
echo "no resizability skill in this Xcode's export ($OUT)" >&2
exit 4
