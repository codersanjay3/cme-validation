#!/usr/bin/env bash
# Usage: scripts/new_worktree.sh <agent-name> <task-slug>
# Creates an isolated worktree on branch <agent>/<task> next to the main checkout.
set -euo pipefail
if [ $# -ne 2 ]; then echo "usage: $0 <agent-name> <task-slug>" >&2; exit 1; fi
agent="$1"; task="$2"
root="$(git rev-parse --show-toplevel)"
branch="${agent}/${task}"
dir="$(dirname "$root")/$(basename "$root")-wt-${agent}-${task}"
git -C "$root" fetch origin --quiet 2>/dev/null || true
base="main"; git -C "$root" rev-parse --verify origin/main >/dev/null 2>&1 && base="origin/main"
git -C "$root" worktree add -b "$branch" "$dir" "$base"
for d in edgar_cache bond_cache; do
  [ -e "$root/$d" ] && ln -s "$root/$d" "$dir/$d"
done
[ -e "$root/stock_prices.pkl" ] && ln -s "$root/stock_prices.pkl" "$dir/stock_prices.pkl"
echo "Worktree ready: $dir (branch $branch)"
echo "cd there, then: bd update <task-id> --claim"
