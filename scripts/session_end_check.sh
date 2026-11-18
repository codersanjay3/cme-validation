#!/usr/bin/env bash
# Stop hook: non-blocking reminder if results changed but DECISIONS.md did not.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
changed="$(git status --porcelain | grep -E '\.(py|json|csv|tex)$' | grep -v DECISIONS | head -1)"
logged="$(git status --porcelain DECISIONS.md)"
if [ -n "$changed" ] && [ -z "$logged" ]; then
  echo '{"systemMessage":"Reminder: files changed but DECISIONS.md has no new entry. Before ending, log what changed and any moved numbers, and file a result-change issue if a reported number changed."}'
fi
exit 0
