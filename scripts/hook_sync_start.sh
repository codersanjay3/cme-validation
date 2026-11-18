#!/usr/bin/env bash
# SessionStart hook: refresh shared state. Never fails the session.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
git fetch origin --quiet 2>/dev/null || true
behind="$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)"
bd dolt pull >/dev/null 2>&1 && echo "beads: pulled latest tasks" || echo "beads: pull skipped (offline or no remote)"
[ "$behind" != "0" ] && echo "git: your branch is $behind commit(s) behind origin/main; consider git pull --rebase"
exit 0
