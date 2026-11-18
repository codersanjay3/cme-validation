#!/usr/bin/env bash
# Stop hook: share task updates. Code still goes through branches and PRs. Never fails the session.
cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
bd dolt push >/dev/null 2>&1 || true
exit 0
