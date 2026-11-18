# Onboarding a new machine or agent

1. Install tools: `brew install gh beads` (Mac), then `gh auth login`.
2. Accept the GitHub invite to `codersanjay3/cme-validation`, then:
   ```bash
   git clone https://github.com/codersanjay3/cme-validation.git
   cd cme-validation
   chmod 700 .beads
   bd bootstrap          # pulls the shared task database from GitHub
   bd list               # should show the same tasks as everyone else
   ```
3. Get the data: see `DATA.md`.
4. Pick a distinct agent name (for example `friend-agent`) and use it everywhere: branch prefix, `from:` label, `DECISIONS.md` entries.
5. Start Claude Code in the repo folder. The hooks load the shared memory automatically. Then follow `CLAUDE.md`.

Sync cheat sheet:
```bash
bd dolt pull    # get others' task updates     (run at session start)
bd dolt push    # share your task updates      (run at session end)
git pull --rebase && git push origin <your-branch>
```
Task data travels on `refs/dolt/data` in the same GitHub repo; code travels on normal branches.
