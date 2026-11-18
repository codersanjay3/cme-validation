# CME project: instructions for every agent

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:1105d646 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/core-concepts/sync-concepts.md for details and anti-patterns.

## Agent Context Profiles

The managed Beads block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `bd` for task tracking. Do not run git commits, git pushes, or Dolt remote sync unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `bd prime`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close beads, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a Beads implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** - Create beads for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **Handle git/sync by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** - Summarize changes, validation, issue status, and any blocked sync/commit/push step

**Critical rules:**
- Explicit user or orchestrator instructions override this Beads block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required sync or push is blocked, stop and report the exact command and error.
<!-- END BEADS INTEGRATION -->

## What this project is

Chronotypic Market Ecology (CME): an agent-based model of investors with different trading horizons, plus an empirical test on SEC 13F holdings. Authors: Sanjay Subramanian and Sumedh Seetharaman. Target: Finance Research Letters or a complexity/finance journal. Read `DECISIONS.md` first; it is the project's memory. The long explanation is `CME_full_research_report.pdf`; reproduction steps are in `REPRODUCE.md`.

## Start of every session (do this before anything else)

1. `git pull --rebase` on your branch, then read the last 60 lines of `DECISIONS.md`.
2. `bd ready` and `bd list --status in_progress` to see open and claimed work.
3. `gh issue list --state open --limit 20` to see messages from other agents. Read any issue that mentions you or your task.

## During work

- **Claim before you start:** `bd update <id> --claim`. If someone else has claimed it, pick another task or ask on the linked GitHub issue.
- **One branch per agent per task**, in its own git worktree: `scripts/new_worktree.sh <agent-name> <task-slug>`. Never commit to `main`. Merge only through a pull request.
- **Never run two agents in the same checkout.**
- Create a bead for any follow-up work you discover (`bd create`), instead of keeping a private to-do list.

## Communication between agents (GitHub Issues)

Beads holds the task graph. GitHub Issues is the conversation channel. Use the issue templates:

- `handoff`: what you finished, what changed, what the next agent must check.
- `question`: a question for a specific agent or human. Label it `to:<agent>`.
- `result-change`: any change to a number reported in the paper (see below).
- `blocker`: you cannot proceed.

Label every issue with `from:<your-name>`. Comment on the issue instead of editing it, so history is kept. Close an issue only when the agent it is addressed to confirms.

## End of every session

1. Append an entry to `DECISIONS.md` (template at the top of that file): what changed, which numbers moved, what is open.
2. Update beads (`bd close`, or `bd update` with notes).
3. Commit to your branch and push it. Open or update a pull request. Do not merge your own pull request.
4. If you finished something another agent depends on, comment on the relevant issue.

## Hard rules (these came from real mistakes in this project)

- **Any change to a reported number needs a `result-change` issue and a `DECISIONS.md` entry** with the old value, the new value, the script and seed that produced it, and the reason.
- **No claim in the paper without a script and a stored output that produces it.** Earlier versions claimed a 17-lag correction that was never computed, a concentration result whose sweep never fed the simulation, and a significance level that was not true. All were corrected.
- **Use the share-based turnover**, not value-weighted turnover, for horizon diversity. Value weights mix in price drift.
- **State the model/data sign disagreement honestly.** The simulation says compressed horizons lower volatility; the stock data say similar-horizon owners go with higher volatility.
- **Fixed random seeds** for every simulation. Record them with the result.
- **No em dashes** in anything written for presentations or scripts.
- Do not commit data caches, `.env` files, or API keys. See `DATA.md` for where the data lives.

## Run and verify

```bash
pip install -r requirements.txt     # numpy, scipy, matplotlib, networkx, pandas (statsmodels, yfinance for the empirical scripts)
python verify_numbers.py            # 30-seed check of the simulation ratios
```

Other scripts and what they produce are listed in `REPRODUCE.md`.

## Where things live

- Model and simulation: `cme_canonical.py`, `verify_numbers.py`, `sim_concentration_check.py`
- Clustering score and inference: `kappa_empirical.py`, `kappa_hac_tests.py`
- Price-drift check: `price_adjusted_tdi.py`
- Stock-level test: `map_cusips.py`, `stock_prices.py`, `stock_level_test.py`
- Bond analysis: `bond_discover.py`, `bond_by_type.py`
- Paper: `cme_frl_submission.tex`; explanatory report: `report/`
