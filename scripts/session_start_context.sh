#!/usr/bin/env bash
# SessionStart hook: print the project memory so a fresh session is never blank.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
echo "=== CME shared memory: last entries of DECISIONS.md ==="
tail -n 40 DECISIONS.md
echo "=== Open GitHub issues (if gh is available) ==="
gh issue list --state open --limit 10 2>/dev/null || echo "(gh not available or no remote yet)"
echo "=== Rule: read DECISIONS.md, claim a bead, log your changes at the end. See CLAUDE.md ==="
